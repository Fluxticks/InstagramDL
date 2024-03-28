from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional, Union

from instagramdl.api import download_file


@dataclass()
class User:
    """A class that represents an instagram user."""

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
    """A string enum to store the Instagram string representations of the different post types."""

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
    """A class that represent a generic post. Is the superclass of all other Post type classes."""

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

    def download(
        self, download_path: str, max_chunk_size: int = 8192
    ) -> Union[str, List[str]]:
        """Downloads any media related to a post. Cannot be used on the generic `Post` class as it has no associated media.

        Args:
            download_path (str): The path to download the files to.
            max_chunk_size (int, optional): The maximum chunk size to use while downloading. Defaults to 8192.

        Raises:
            ValueError: If called on the generic `Post` class.
            HTTPError: If an error occurs during file downloading.

        Returns:
            Union[str, List[str]]: If a single file, the download file path. Else a list of filepaths for all the associated files.
        """
        raise ValueError(
            "Method not implemented! Generic posts do not have media to download."
        )


@dataclass()
class VideoPost(Post):
    """A class to represent a post that contains a single video."""

    has_audio: bool
    video_url: str
    play_count: int
    view_count: int
    duration: float

    def download(self, download_path: str, max_chunk_size: int = 8192) -> str:
        return download_file(self.video_url, download_path, max_chunk_size)


@dataclass()
class ImagePost(Post):
    """A class to represent a post that contains a single image."""

    image_url: str
    alt_urls: List[str]
    accessibility_caption: str

    def download(self, download_path: str, max_chunk_size: int = 8192) -> str:
        return download_file(self.image_url, download_path, max_chunk_size)


@dataclass()
class MultiPost(Post):
    """A class to represent a post that has more than one image or video. Can contain a mix of both media types."""

    items: List[Union[ImagePost, VideoPost]]

    def download(self, download_path: str, max_chunk_size: int = 8192) -> List[str]:
        downloads = []
        for item in self.items:
            downloads.append(item.download(download_path, max_chunk_size))
        return downloads
