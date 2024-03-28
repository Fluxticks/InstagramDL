from typing import Dict

from instagramdl.models import (
    ImagePost,
    MultiPost,
    Post,
    PostKind,
    User,
    VideoPost,
)


__all__ = ["parse_user", "parse_post", "parse_api_response"]


def __parse_video_post(base_post: Post, api_response: Dict) -> VideoPost:
    """Parse the video post specifc parts of an API response. Requires the generic post to already be parsed.

    Args:
        base_post (Post): The generic post data already parsed.
        api_response (Dict): The rest of the API data to be parse.

    Returns:
        VideoPost: A VideoPost object containing the information regarding a video post.
    """
    has_audio = api_response.get("has_audio", False)
    video_url = api_response.get("video_url")
    play_count = api_response.get("video_play_count", 0)
    view_count = api_response.get("video_view_count", 0)
    duration = api_response.get("video_duration", 0.0)

    return VideoPost(
        **base_post.__dict__,
        has_audio=has_audio,
        video_url=video_url,
        play_count=play_count,
        view_count=view_count,
        duration=duration,
    )


def __parse_image_post(base_post: Post, api_response: Dict) -> ImagePost:
    """Parse the image post specific parts of an API response. Requires the generic post data to already be parsed.

    Args:
        base_post (Post): The generic post data already parsed.
        api_response (Dict): The rest of the API data to parse.

    Returns:
        ImagePost: An ImagePost object containing the information regarding an image post.
    """
    url = api_response.get("display_url")
    alt_urls = [x.get("src") for x in api_response.get("display_resources")]
    accessibility_caption = api_response.get("accessibility_caption")

    return ImagePost(
        **base_post.__dict__,
        image_url=url,
        alt_urls=alt_urls,
        accessibility_caption=accessibility_caption,
    )


def __parse_multi_post(base_post: Post, api_response: Dict) -> MultiPost:
    """Parse the multimedia post specific parts of an API response. Requires the generic post data to already be parsed.

    Args:
        base_post (Post): The generic post data already parsed.
        api_response (Dict): The rest of the API data to parse.

    Returns:
        MultiPost: A MultiPost object containing a list of ImagePost and VideoPost objects with information regarding the multimedia post.
    """
    items = api_response.get("edge_sidecar_to_children").get("edges")
    parsed_items = []
    for item in items:
        item_data = item.get("node")
        item_kind = item_data.get("__typename")
        if item_kind == PostKind.VIDEO:
            parsed_items.append(__parse_video_post(base_post, item_data))
        elif item_kind == PostKind.IMAGE:
            parsed_items.append(__parse_image_post(base_post, item_data))

    return MultiPost(**base_post.__dict__, items=parsed_items)


def parse_user(api_response: Dict, is_root_user: bool = True) -> User:
    """Parse the User/Owner information from an API response dictionary. Parses the user data as well as the related profiles data.

    Args:
        api_response (Dict): The API data to parse.
        is_root_user (bool, optional): If the data to parse is the post user. Set to false to parse related profile user data. Defaults to True.

    Returns:
        User: A User object containing the user data and the related profiles.
    """
    if is_root_user:
        user_info = api_response.get("owner")
    else:
        user_info = api_response.get("node")

    user_id = user_info.get("id")
    full_name = user_info.get("full_name")
    is_private = user_info.get("is_private")
    is_verified = user_info.get("is_verified")
    profile_pic_url = user_info.get("profile_pic_url")
    username = user_info.get("username")
    follower_count = user_info.get("edge_followed_by").get("count")
    post_count = user_info.get("edge_owner_to_timeline_media").get("count")

    user = User(
        id=user_id,
        username=username,
        is_verified=is_verified,
        profile_pic_url=profile_pic_url,
        full_name=full_name,
        is_private=is_private,
        follower_count=follower_count,
        post_count=post_count,
        related_profiles=[],
    )

    if is_root_user:
        related_profiles = []
        for edge in api_response.get("edge_related_profiles").get("edges"):
            related_profiles.append(parse_user(edge, False))

        user.related_profiles = related_profiles
        return user
    else:
        return user


def parse_post(api_response: Dict) -> Post:
    """Parse the generic post data from an API response. Does not get any media data/urls.

    Args:
        api_response (Dict): The API data to parse.

    Returns:
        Post: A Post object containing basic information about the parsed API data.
    """
    post_id = api_response.get("id")
    post_kind = PostKind.from_str(api_response.get("__typename"))
    shortcode = api_response.get("shortcode")
    thumbnail_url = api_response.get("thumbnail_src")

    # Get post dimensions
    dimensions = api_response.get("dimensions")
    width = dimensions.get("width")
    height = dimensions.get("height")

    # Get post interactions
    comment_count = api_response.get("edge_media_to_comment").get("count")
    like_count = api_response.get("edge_media_preview_like").get("count")

    post_caption = (
        api_response.get("edge_media_to_caption")
        .get("edges")[0]
        .get("node")
        .get("text")
    )

    timestamp = api_response.get("taken_at_timestamp")

    owner = parse_user(api_response)

    return Post(
        id=post_id,
        shortcode=shortcode,
        kind=post_kind,
        thumbnail_url=thumbnail_url,
        width=width,
        height=height,
        user=owner,
        caption=post_caption,
        timestamp=timestamp,
        like_count=like_count,
        comment_count=comment_count,
    )


def parse_api_response(api_response: Dict, ignore_media: bool = False) -> Post:
    """Parse an API response and get all related URLs for any media in the post. If media URLs are not needed, set the `ignore_media` flag to `True`.

    Args:
        api_response (Dict): The API data to parse.
        ignore_media (bool, optional): If the media URLs are not required, set to True. Defaults to False.

    Returns:
        Post: If `ignore_media` is set, returns a generic Post object. Else returns one of `VideoPost`, `ImagePost`, or `MultiPost` based on the API response content.
    """
    response_data = api_response.get("data").get("xdt_shortcode_media")
    post = parse_post(response_data)
    if ignore_media:
        return post

    if post.kind == PostKind.VIDEO:
        return __parse_video_post(post, response_data)

    if post.kind == PostKind.IMAGE:
        return __parse_image_post(post, response_data)

    if post.kind == PostKind.MULTI:
        return __parse_multi_post(post, response_data)

    return post
