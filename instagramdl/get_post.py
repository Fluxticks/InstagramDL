import os
from asyncio import Lock, sleep
from dataclasses import dataclass
from datetime import datetime
from time import time
from typing import Coroutine, Literal
from urllib.request import urlretrieve
from uuid import uuid4

from instagramdl.exceptions import PostUnavailableException
from instagramdl.post_data import InstagramPost, PostType
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright


@dataclass
class Request:
    url: str
    callback: Coroutine | None
    kwargs: dict


def __get_slideshow_content(post_info: dict) -> tuple[list[str], list[str]]:
    content = post_info.get("edge_sidecar_to_children").get("edges")
    image_urls = []
    video_urls = []
    for item in content:
        item_info = item.get("node")
        item_type = __get_post_type(item_info.get("__typename"))
        if item_type == PostType.IMAGE:
            image_urls += __get_image_content(item_info)
        elif item_type == PostType.REEL:
            video_urls += __get_video_content(item_info)

    return image_urls, video_urls


def __get_image_content(post_info: dict) -> list[str]:
    image_url = post_info.get("display_url")
    return [image_url]


def __get_video_content(post_info: dict) -> list[str]:
    video_url = post_info.get("video_url")
    return [video_url]


def __get_post_type(typename: str):
    match typename:
        case "GraphSidecar":
            return PostType.SLIDES
        case "GraphVideo":
            return PostType.REEL
        case "GraphImage":
            return PostType.IMAGE


def __parse_post_data(post_info: dict) -> InstagramPost:
    author_data = post_info.get("owner")

    author_username = author_data.get("username")
    author_display_name = author_data.get("full_name")
    author_avatar_url = author_data.get("profile_pic_url")
    author_profile_url = f"https://www.instagram.com/{author_username}/"
    author_is_verified = author_data.get("is_verified")

    post_url = f"https://www.instagram.com/p/{post_info.get('shortcode')}/"

    post_description = post_info.get("edge_media_to_caption").get("edges")[0].get("node").get("text")
    post_timestamp_string = post_info.get("taken_at_timestamp")
    post_timestamp = datetime.fromtimestamp(float(post_timestamp_string))

    post_like_count = post_info.get("edge_media_preview_like").get("count")
    post_comment_count = post_info.get("edge_media_preview_comment").get("count")

    post_type = __get_post_type(post_info.get("__typename"))
    match post_type:
        case PostType.SLIDES:
            post_image_urls, post_video_urls = __get_slideshow_content(post_info)
        case PostType.REEL:
            post_image_urls = []
            post_video_urls = __get_video_content(post_info)
        case PostType.IMAGE:
            post_image_urls = __get_image_content(post_info)
            post_video_urls = []

    post_info = InstagramPost(
        author_username=author_username,
        author_display_name=author_display_name,
        author_avatar_url=author_avatar_url,
        author_profile_url=author_profile_url,
        author_is_verified=author_is_verified,
        post_url=post_url,
        post_type=post_type,
        post_description=post_description,
        post_timestamp=post_timestamp,
        post_like_count=post_like_count,
        post_comment_count=post_comment_count,
        post_image_urls=post_image_urls,
        post_video_urls=post_video_urls
    )

    return post_info


def __download_video(video_url: str) -> str:
    filename = os.path.join(
        os.curdir,
        f"{uuid4()}.mp4",
    )
    path, _ = urlretrieve(video_url, filename=filename)
    return path


async def __get_info(
    url: str,
    download_videos: bool = True,
    browser: Literal["firefox",
                     "chromium",
                     "chrome",
                     "safari",
                     "webkit"] = "firefox",
    timeout: float | None = None,
    headless: bool | None = None,
    slow_mo: float | None = None
) -> dict:
    async with async_playwright() as playwright:
        match browser:
            case "firefox":
                browser_instance = playwright.firefox
            case "chrome":
                browser_instance = playwright.chromium
            case "chromium":
                browser_instance = playwright.chromium
            case "safari":
                browser_instance = playwright.webkit
            case "webkit":
                browser_instance = playwright.webkit
            case _:
                raise TypeError(f"Invalid browser given. Browser {browser} is not valid.")

        browser_instance = await playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
        browser_context = await browser_instance.new_context()
        await browser_context.clear_cookies()

        post_page = await browser_context.new_page()
        await post_page.goto(url)

        try:
            async with post_page.expect_response(lambda x: "/graphql/query/" in x.url, timeout=timeout) as response:
                response = await response.value
                data = await response.json()
                return data.get("data").get("shortcode_media")
        except PlaywrightTimeout:
            return None


async def get_info(
    url: str,
    download_videos: bool = True,
    browser: Literal["firefox",
                     "chromium",
                     "chrome",
                     "safari",
                     "webkit"] = "firefox",
    timeout: float | None = None,
    headless: bool | None = None,
    slow_mo: float | None = None
) -> InstagramPost:
    post_data = await __get_info(
        url=url,
        download_videos=download_videos,
        browser=browser,
        timeout=timeout,
        headless=headless,
        slow_mo=slow_mo
    )

    if not post_data:
        raise PostUnavailableException(url=url)

    post = __parse_post_data(post_data)

    video_paths = []
    if download_videos:
        for video in post.post_video_urls:
            video_paths.append(__download_video(video))

    post.post_video_files = video_paths

    return post


class RequestHandler:

    def __init__(self, minimum_request_interval: float = 5):
        self.last_request = time() - 2 * minimum_request_interval
        self.minimum_request_interval = minimum_request_interval
        self.request_list_mutex = Lock()
        self.active_request_mutex = Lock()
        self.request_queue = []

    async def make_next_request(self) -> InstagramPost:
        if not self.request_queue:
            return

        async with self.request_list_mutex:
            next_request = self.request_queue.pop(0)

        async with self.active_request_mutex:
            if self.last_request - time() < self.minimum_request_interval:
                await sleep(time() - (self.last_request + self.minimum_request_interval))

            post = await get_info(next_request.url)
            self.last_request = time()

        if next_request.callback is not None:
            await next_request.callback(post, **next_request.kwargs)
        return post

    async def add_request(self, url: str, callback: Coroutine | None = None, **kwargs):
        async with self.request_list_mutex:
            self.request_queue.append(Request(url, callback, kwargs))
