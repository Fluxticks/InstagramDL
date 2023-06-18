class PostUnavailableException(Exception):

    def __init__(self, url: str, *args: any, **kwargs: dict[any]):
        super().__init__(*args, **kwargs)
        self.url = url


class InstagramInaccessibleException(Exception):

    def __init__(self, url: str, *args: any, **kwargs: dict[any]):
        super().__init__(*args, **kwargs)
        self.url = url
