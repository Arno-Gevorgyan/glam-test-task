import strawberry
from strawberry.types import Info

from gql.base.types import MessageType
from gql.permissions import IsAuthenticated
from services.instagram import InstagramScraper
from gql.instagram.types import InstagramInput, InstagramType


@strawberry.type
class InstagramQuery:
    @strawberry.field(
        description='Getting list of photos',
        permission_classes=[IsAuthenticated],
    )
    async def get_photos(self, info: Info, data: InstagramInput) -> InstagramType | MessageType:
        scraper = InstagramScraper()
        return await scraper.get_photos(info.context['session'], info.context['user'], data)
