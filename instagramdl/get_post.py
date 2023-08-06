import os
from asyncio import Lock, sleep
from dataclasses import dataclass
from datetime import datetime
from json import loads
from time import time
from typing import Coroutine, Literal
from urllib.request import urlretrieve
from uuid import uuid4

from bs4 import BeautifulSoup
from instagramdl.exceptions import PostUnavailableException
from instagramdl.post_data import InstagramPost, PostType
from playwright.async_api import TimeoutError as PlaywrightTimeout
from playwright.async_api import async_playwright


@dataclass
class Request:
    url: str
    callback: Coroutine | None
    kwargs: dict


def __get_interaction_stat(
    interaction_statistics: list[dict],
    interaction_kind: Literal["likes",
                              "comments",
                              "views"]
) -> int | None:
    interaction_type_string = ""
    match interaction_kind:
        case "likes":
            interaction_type_string = "http://schema.org/LikeAction"
        case "comments":
            interaction_type_string = "https://schema.org/CommentAction"
        case "views":
            interaction_type_string = "http://schema.org/WatchAction"
        case _:
            return None

    statistic_found = [
        x.get("userInteractionCount") for x in interaction_statistics if x.get("interactionType") == interaction_type_string
    ]

    if not statistic_found:
        return None

    return int(statistic_found[0])


def __get_post_info_from_source(page_source: str) -> dict:
    soup = BeautifulSoup(page_source, "lxml")
    page_script = soup.find("script", attrs={"type": "application/ld+json"})
    script_dictionary = loads(page_script.text)
    if isinstance(script_dictionary, list):
        script_dictionary = script_dictionary[0]

    return script_dictionary


def __parse_post_data(post_info: dict) -> InstagramPost:
    author_data = post_info.get("author")

    author_username = author_data.get("alternateName")
    author_display_name = author_data.get("name")
    author_avatar_url = author_data.get("image")
    author_profile_url = author_data.get("url")

    post_url = post_info.get("mainEntityOfPage").get("@id")

    post_description = post_info.get("articleBody")
    post_timestamp_string = post_info.get("dateCreated")
    post_timestamp = datetime.strptime(post_timestamp_string, "%Y-%m-%dT%H:%M:%S%z")

    post_interactions = post_info.get("interactionStatistic")

    post_like_count = __get_interaction_stat(post_interactions, "likes")
    post_comment_count = __get_interaction_stat(post_interactions, "comments")

    post_image_urls = [x.get("url") for x in post_info.get("image")]
    post_video_urls = [{"url": x.get("contentUrl"), "thumbnail": x.get("thumbnailUrl")} for x in post_info.get("video")]

    post_type = PostType.REEL if len(post_video_urls) else PostType.IMAGE

    post_info = InstagramPost(
        author_username=author_username,
        author_display_name=author_display_name,
        author_avatar_url=author_avatar_url,
        author_profile_url=author_profile_url,
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


async def get_info(
    url: str,
    download_videos: bool = True,
    browser: Literal["firefox",
                     "chromium",
                     "chrome",
                     "safari",
                     "webkit"] = "firefox",
    headless: bool | None = None,
    slow_mo: float | None = None
) -> InstagramPost:
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
        await post_page.goto(url, wait_until="networkidle")

        try:
            decline_button = post_page.get_by_text("Decline optional cookies")
            await decline_button.click(button="left")
        except PlaywrightTimeout:
            pass

        post_unavailable = post_page.get_by_text("Sorry, this page isn't available")
        count = await post_unavailable.count()
        if count > 0:
            raise PostUnavailableException(url=url)

        page_content = await post_page.content()
        raw_post_info = __get_post_info_from_source(page_content)
        post_data = __parse_post_data(raw_post_info)

        video_paths = []
        if download_videos:
            for video in post_data.post_video_urls:
                video_paths.append(__download_video(video.get("url")))

        post_data.post_video_files = video_paths
        return post_data


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
