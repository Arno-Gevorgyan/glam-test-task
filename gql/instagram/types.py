import strawberry

from typing import Optional, List


@strawberry.input
class InstagramInput:
    username: str
    max_count: Optional[int] = 10


@strawberry.type
class InstagramType:
    urls: Optional[List[str]] = None
