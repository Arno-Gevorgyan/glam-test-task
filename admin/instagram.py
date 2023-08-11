from admin.base import AuthModelView
from db.models import InstagramModel


class InstagramAdmin(AuthModelView, model=InstagramModel):
    name = "Instagram"
    name_plural = "Instagrams"
    icon = "fa-solid fa-instagram"

    column_list = [
        InstagramModel.id,
        InstagramModel.account_username,
        InstagramModel.created_at,
    ]

    column_details_list = [
        InstagramModel.user,
        InstagramModel.account_username,
        InstagramModel.photo_urls,
        InstagramModel.created_at,
    ]

    column_searchable_list = [
        InstagramModel.account_username,
    ]

    column_sortable_list = [
        InstagramModel.account_username,
        InstagramModel.created_at,
    ]
