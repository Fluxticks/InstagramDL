from dataclasses import dataclass
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
