from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class PostType(IntEnum):
    REEL = 0
    IMAGE = 1


@dataclass()
class InstagramPost:
    author_username: str
    author_display_name: str
    author_avatar_url: str
    author_profile_url: str
    post_url: str
    post_type: PostType
    post_description: str
    post_timestamp: datetime
    post_like_count: int
    post_comment_count: int
    post_image_urls: list[str] = None
    post_video_urls: list[str] = None
    post_video_files: list[str] = None
