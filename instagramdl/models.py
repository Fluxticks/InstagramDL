from dataclasses import dataclass
from enum import StrEnum
from typing import Any, List, Optional, Union

from instagramdl.api import download_file


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

    def download(self, download_path: str, max_chunk_size: int = 8192) -> Any:
        raise ValueError(
            "Method not implemented! Generic posts do not have media to download."
        )


@dataclass()
class VideoPost(Post):
    has_audio: bool
    video_url: str
    play_count: int
    view_count: int
    duration: float

    def download(self, download_path: str, max_chunk_size: int = 8192) -> str:
        return download_file(self.video_url, download_path, max_chunk_size)


@dataclass()
class ImagePost(Post):
    image_url: str
    alt_urls: List[str]
    accessibility_caption: str

    def download(self, download_path: str, max_chunk_size: int = 8192) -> str:
        return download_file(self.image_url, download_path, max_chunk_size)


@dataclass()
class MultiPost(Post):
    items: List[Union[ImagePost, VideoPost]]

    def download(self, download_path: str, max_chunk_size: int = 8192) -> List[str]:
        downloads = []
        for item in self.items:
            downloads.append(item.download(download_path, max_chunk_size))
        return downloads
