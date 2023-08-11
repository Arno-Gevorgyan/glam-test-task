from admin.forms import UserForm
from admin.base import AuthModelView
from db.models import InstagramModel
from db.models._users import UserModel
from admin.validators import check_email


class UserAdmin(AuthModelView, model=UserModel):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    inline_models = [
        (InstagramModel, [InstagramModel.id, InstagramModel.account_username])
    ]
    form_columns = [
        UserModel.first_name,
        UserModel.last_name,
        UserModel.email,
        UserModel.is_active,
        UserModel.is_superuser,
    ]

    form_base_class = UserForm

    column_list = [
        UserModel.first_name,
        UserModel.last_name,
        UserModel.email,
        UserModel.is_active,
        UserModel.created_at,
    ]

    column_details_list = [
        UserModel.first_name,
        UserModel.last_name,
        UserModel.email,
        UserModel.verification_token,
        UserModel.is_active,
        UserModel.is_superuser,
        UserModel.created_at,
        UserModel.updated_at,
    ]

    column_searchable_list = [
        UserModel.first_name,
        UserModel.last_name,
        UserModel.email,
    ]

    column_sortable_list = [
        UserModel.first_name,
        UserModel.last_name,
        UserModel.email
    ]

    async def on_model_change(self, data: dict, model: UserModel, is_created: bool) -> None:
        if is_created:
            async with self.sessionmaker(expire_on_commit=False) as session:
                await check_email(session, data['email'])
        return await super().on_model_change(data, model, is_created)
