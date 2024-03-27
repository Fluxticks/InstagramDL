from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional, Union


@dataclass()
class User:
    id: int
    username: str
    is_verified: bool
    profile_pic_url: str
    full_name: str
    is_private: bool
    follower_count: int
    post_count: int
    related_profiles: Optional[List["User"]] = None


class PostKind(StrEnum):
    VIDEO = "XDTGraphVideo"
    IMAGE = "XDTGraphImage"
    MULTI = "XDTGraphSidecar"

    @staticmethod
    def from_str(input: str) -> "PostKind":
        if input == PostKind.VIDEO:
            return PostKind.VIDEO

        if input == PostKind.IMAGE:
            return PostKind.IMAGE

        if input == PostKind.MULTI:
            return PostKind.MULTI

        raise ValueError(f"{input} is not a valid PostKind string!")


@dataclass()
class Post:
    id: int
    shortcode: str
    kind: PostKind
    thumbnail_url: str
    width: int
    height: int
    user: User
    caption: str
    timestamp: int
    like_count: int
    comment_count: int


@dataclass()
class VideoPost(Post):
    has_audio: bool
    video_url: str
    play_count: int
    view_count: int
    duration: float


@dataclass()
class ImagePost(Post):
    image_url: str
    alt_urls: List[str]
    accessibility_caption: str


@dataclass()
class MultiPost(Post):
    items: List[Union[ImagePost, VideoPost]]
