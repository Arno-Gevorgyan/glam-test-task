import anyio
import wtforms
from typing import Type, Any, Dict, Generator, Tuple

from sqladmin._queries import Query
from sqlalchemy.engine import Engine
from sqladmin import ModelView, Admin
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.exc import IntegrityError
from wtforms.fields.core import UnboundField
from starlette.exceptions import HTTPException
from sqladmin.authentication import login_required
from sqladmin.forms import ModelConverter, converts
from sqladmin.fields import QuerySelectField, TimeField
from sqlalchemy import inspect as sqlalchemy_inspect, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqladmin.helpers import get_primary_key, get_direction, get_column_python_type
from sqlalchemy.orm import Session, RelationshipProperty, ColumnProperty, joinedload

from gql.exceptions import ValidationError


class QuerySelectFixField(QuerySelectField):
    def iter_choices(self) -> Generator[Tuple[str, str, bool], None, None]:
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None)

        if self.data:
            primary_key = self.data if isinstance(self.data, str) else str(list(self.data)[0].id) if isinstance(
                self.data, (list, tuple)) else str(sqlalchemy_inspect(self.data).identity[0])
        else:
            primary_key = None

        for pk, label in self._select_data:
            yield (pk, self.get_label(label), str(pk) == primary_key)


class ModelConverterFix(ModelConverter):
    async def _prepare_select_options(self, prop, engine):
        target_model = prop.mapper.class_
        pk = get_primary_key(target_model)
        stmt = select(target_model)

        if isinstance(engine, Engine):
            with Session(engine) as session:
                objects = await anyio.to_thread.run_sync(session.execute, stmt)
                return [
                    (self._get_pk_value(obj, pk), str(obj))
                    for obj in objects.scalars().all()
                ]
        elif isinstance(engine, AsyncEngine):
            async with AsyncSession(engine) as session:
                objects = await session.execute(stmt)
                return [
                    (self._get_pk_value(obj, pk), str(obj))
                    for obj in objects.scalars().unique().all()
                ]

        return []  # pragma: nocover

    @converts("MANYTOONE")
    def conv_many_to_one(
        self, model: type, prop: RelationshipProperty, kwargs: Dict[str, Any]
    ) -> UnboundField:
        return QuerySelectFixField(**kwargs)

    @converts("Time")
    def conv_time(
            self, model: type, prop: ColumnProperty, kwargs: Dict[str, Any]
    ) -> UnboundField:
        return TimeField(format="%H:%M:%S", **kwargs)


async def get_model_form(
        model,
        engine,
        only=None,
        exclude=None,
        column_labels=None,
        form_args=None,
        form_widget_args=None,
        form_class=wtforms.Form,
        form_overrides=None,
        form_ajax_refs=None,
        form_include_pk=False,
):
    type_name = model.__name__ + "Form"
    converter = ModelConverterFix()
    mapper = sqlalchemy_inspect(model)
    form_args = form_args or {}
    form_widget_args = form_widget_args or {}
    column_labels = column_labels or {}
    form_overrides = form_overrides or {}
    form_ajax_refs = form_ajax_refs or {}

    attributes = []
    names = only or mapper.attrs.keys()
    for name in names:
        if exclude and name in exclude:
            continue
        attributes.append((name, mapper.attrs[name]))

    field_dict = {}
    for name, attr in attributes:
        field_args = form_args.get(name, {})
        field_widget_args = form_widget_args.get(name, {})
        label = column_labels.get(name, None)
        override = form_overrides.get(name, None)
        field = await converter.convert(
            model=model,
            prop=attr,
            engine=engine,
            field_args=field_args,
            field_widget_args=field_widget_args,
            label=label,
            override=override,
            form_include_pk=form_include_pk,
            form_ajax_refs=form_ajax_refs,
        )
        if field is not None:
            field_dict[name] = field

    return type(type_name, (form_class,), field_dict)


def filter_attrs(self, exclude_attr: list):
    exclude_attr.extend(['created_at', 'updated_at'])
    columns = list(self._mapper.columns)
    default = []
    for attr in self._attrs:
        if attr.key not in exclude_attr:
            if attr in self._relations:
                default.append(attr)
            if attr in columns:
                default.append(attr)
    return self._build_column_list(
        default=default,
    )


class MyQuery(Query):

    async def _set_attributes_async(
        self, session: AsyncSession, obj: Any, data: dict
    ) -> Any:
        for key, value in data.items():
            column = self.model_view._mapper.columns.get(key)
            relation = self.model_view._mapper.relationships.get(key)

            if not value:
                # Set falsy values to None, if column is Nullable
                if not relation and column.nullable and value is not False:
                    value = None

                setattr(obj, key, value)
                continue

            if relation:
                direction = get_direction(relation)
                if direction in ["ONETOMANY", "MANYTOMANY"]:
                    related_stmt = self._get_to_many_stmt(relation, value)
                    result = await session.execute(related_stmt)
                    related_objs = result.scalars().unique().all()
                    setattr(obj, key, related_objs)
                elif direction == "ONETOONE":
                    related_stmt = self._get_to_one_stmt(relation, value)
                    result = await session.execute(related_stmt)
                    related_obj = result.scalars().first()
                    setattr(obj, key, related_obj)
                else:
                    obj = self._set_many_to_one(obj, relation, value)
            else:
                setattr(obj, key, value)
        return obj

    async def _insert_async(self, data: Dict[str, Any]) -> Any:
        obj = self.model_view.model()

        async with self.model_view.sessionmaker(expire_on_commit=False) as session:
            try:
                await self.model_view.on_model_change(data, obj, True)
                obj = await self._set_attributes_async(session, obj, data)
                session.add(obj)
                await session.commit()
                await self.model_view.after_model_change(data, obj, True)
                return obj
            except IntegrityError as e:
                error_msg = str(e.__cause__) if e.__cause__ else str(e)
                detail = error_msg.split('DETAIL: ')[-1]
                raise HTTPException(status_code=400, detail=detail) from e

            except ValidationError as e:
                error_message = e.extensions['explain']
                temp_dict = error_message.copy()
                key, value = temp_dict.popitem()
                await session.rollback()
                raise HTTPException(status_code=400, detail=f"{key} {value}") from e

            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=400, detail=str(e)) from e

    async def _update_async(self, pk: Any, data: Dict[str, Any]) -> None:
        pk = get_column_python_type(self.model_view.pk_column)(pk)
        stmt = select(self.model_view.model).where(self.model_view.pk_column == pk)

        for relation in self.model_view._relations:
            stmt = stmt.options(joinedload(relation.key))
        try:
            async with self.model_view.sessionmaker() as session:
                result = await session.execute(stmt)
                obj = result.scalars().first()
                await self.model_view.on_model_change(data, obj, False)
                obj = await self._set_attributes_async(session, obj, data)
                await session.commit()
                await self.model_view.after_model_change(data, obj, False)
        except IntegrityError as e:
            error_msg = str(e.__cause__) if e.__cause__ else str(e)
            detail = error_msg.split('DETAIL: ')[-1]
            raise HTTPException(status_code=400, detail=detail) from e

        except ValidationError as e:
            error_message = e.extensions['explain']
            temp_dict = error_message.copy()
            key, value = temp_dict.popitem()
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"{key} {value}") from e

        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def insert(self, data: dict) -> Any:
        if self.model_view.async_engine:
            return await self._insert_async(data)
        else:
            return await anyio.to_thread.run_sync(self._insert_sync, data)

    async def update(self, pk: Any, data: dict) -> None:
        if self.model_view.async_engine:
            await self._update_async(pk, data)
        else:
            await anyio.to_thread.run_sync(self._update_sync, pk, data)


class AuthModelView(ModelView):

    create_template = "admin/create.html"
    edit_template = "admin/edit.html"
    details_template = "admin/details.html"
    form_excluded_columns = ('created_at', 'updated_at')
    page_size = 20
    inline_models = []

    async def update_model(self, pk: Any, data: Dict[str, Any]) -> None:
        await MyQuery(self).update(pk, data)

    async def insert_model(self, data: dict) -> None:
        await MyQuery(self).insert(data)

    def is_accessible(self, request) -> bool:
        if user := request.session.get('user'):
            return user['is_active'] and user['is_superuser']
        return False

    def is_visible(self, request) -> bool:
        if user := request.session.get('user'):
            return user['is_active'] and user['is_superuser']
        return False

    async def scaffold_form(self) -> Type[wtforms.Form]:
        if self.form is not None:
            return self.form
        form = await get_model_form(
            model=self.model,
            engine=self.engine,
            only=[i[1].key or i[1].name for i in self._form_attrs],
            column_labels={k.key: v for k, v in self._column_labels.items()},
            form_args=self.form_args,
            form_widget_args=self.form_widget_args,
            form_class=self.form_base_class,
            form_overrides=self.form_overrides,
            form_ajax_refs=self._form_ajax_refs,
            form_include_pk=self.form_include_pk,
        )
        form.has_file_field = self.has_file_field if hasattr(self, 'has_file_field') else False
        return form


class CustomAdmin(Admin):

    def _calculate_mapping_key_pair(self, model, child_model):
        """
            Calculate mapping property key pair between `model` and inline model,
                including the forward one for `model` and the reverse one for inline model.
                Override the method to map your own inline models.
        """
        mapper = model._sa_class_manager.mapper

        # Find property from target model to current model
        # Use the base mapper to support inheritance
        target_mapper = child_model._sa_class_manager.mapper.base_mapper

        reverse_prop = None

        for prop in target_mapper.iterate_properties:
            if (hasattr(prop, 'direction') and prop.direction.name in ('MANYTOONE', 'MANYTOMANY') and
                    issubclass(model, prop.mapper.class_)):
                reverse_prop = prop
                break
        else:
            raise Exception('Cannot find reverse relation for model %s' % child_model)

        # Find forward property
        forward_prop = None

        candidate = 'ONETOMANY' if prop.direction.name == 'MANYTOONE' else 'MANYTOMANY'

        for prop in mapper.iterate_properties:
            if (hasattr(prop, 'direction') and prop.direction.name == candidate and
                    prop.mapper.class_ == target_mapper.class_):
                forward_prop = prop
                break
        else:
            raise Exception('Cannot find forward relation for model %s' % model)

        return forward_prop.key, reverse_prop.key

    def _find_model_view(self, identity: str) -> ModelView:
        for view in self.views:
            if isinstance(view, ModelView) and (view.identity == identity or view.model == identity):
                return view
        raise HTTPException(status_code=404)

    @login_required
    async def details(self, request: Request) -> Response:
        """Details route."""

        await self._details(request)

        model_view = self._find_model_view(request.path_params["identity"])

        model = await model_view.get_model_by_pk(request.path_params["pk"])
        if not model:
            raise HTTPException(status_code=404)

        inline_views = []
        for model_name, fields in model_view.inline_models:
            inline_model = self._find_model_view(model_name)
            model_relation, _ = self._calculate_mapping_key_pair(model.__class__, model_name)
            inline_objects = getattr(model, model_relation)
            inline_views.append({
                'model': inline_model,
                'objects': inline_objects,
                'fields': fields
            })

        context = {
            "request": request,
            "model_view": model_view,
            "model": model,
            "title": model_view.name,
            "inline_views": inline_views
        }

        return self.templates.TemplateResponse(model_view.details_template, context)
