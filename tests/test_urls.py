import unittest
from instagramdl.api import get_post_data
from instagramdl.models import ImagePost, MultiPost, Post, PostKind, User, VideoPost
from instagramdl.parser import parse_api_response


class Test_TestInstagramURL(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url_1 = "https://www.instagram.com/nasa/reel/C401dSkpAH8/"
        self.url_2 = "https://www.instagram.com/nasa/p/C4-91DLO93K/"
        self.url_3 = "https://www.instagram.com/nasa/p/C23EYTXyNJM/"  # Multiple images.

    def assert_data(self, expected_data: Post, actual_data: Post):
        self.assertIsNotNone(actual_data)

        self.assertEqual(expected_data.id, actual_data.id)
        self.assertEqual(expected_data.shortcode, actual_data.shortcode)
        self.assertEqual(expected_data.timestamp, actual_data.timestamp)
        self.assertEqual(expected_data.user.id, actual_data.user.id)
        self.assertEqual(expected_data.kind, actual_data.kind)

    def test_url_1(self):
        expected_data = Post(
            id="3329521133805634044",
            shortcode="C401dSkpAH8",
            kind=PostKind.VIDEO,
            thumbnail_url="some-url",
            width=1080,
            height=1920,
            user=User(
                id="528817151",
                username="nasa",
                is_verified=True,
                profile_pic_url="some-url",
                full_name="NASA",
                is_private=False,
                follower_count=98032669,
                post_count=4140,
                related_profiles=[],
            ),
            caption="",
            timestamp=1711130017,
            like_count=541530,
            comment_count=2308,
        )

        raw_data = get_post_data(self.url_1)
        actual_data = parse_api_response(raw_data, ignore_media=True)
        self.assert_data(expected_data, actual_data)

    def test_url_2(self):
        expected_data = Post(
            id="3332372700679888330",
            shortcode="C4-91DLO93K",
            kind=PostKind.IMAGE,
            thumbnail_url="some-url",
            width=1080,
            height=843,
            user=User(
                id="528817151",
                username="nasa",
                is_verified=True,
                profile_pic_url="some-url",
                full_name="NASA",
                is_private=False,
                follower_count=98032675,
                post_count=4140,
                related_profiles=[],
            ),
            caption="",
            timestamp=1711469803,
            like_count=428222,
            comment_count=988,
        )

        raw_data = get_post_data(self.url_2)
        actual_data = parse_api_response(raw_data, ignore_media=True)
        self.assert_data(expected_data, actual_data)

    def test_url_3(self):
        expected_data = Post(
            id="3294120914698424908",
            shortcode="C23EYTXyNJM",
            kind=PostKind.MULTI,
            thumbnail_url="some-url",
            width=1080,
            height=1080,
            user=User(
                id="528817151",
                username="nasa",
                is_verified=True,
                profile_pic_url="some-url",
                full_name="NASA",
                is_private=False,
                follower_count=98032681,
                post_count=4140,
                related_profiles=[],
            ),
            caption="",
            timestamp=1706909835,
            like_count=1511268,
            comment_count=4383,
        )

        raw_data = get_post_data(self.url_3)
        actual_data = parse_api_response(raw_data, ignore_media=True)
        self.assert_data(expected_data, actual_data)
