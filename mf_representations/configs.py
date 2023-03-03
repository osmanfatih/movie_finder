class TmdbImageConfig:
    def __init__(self, config) -> None:
        self._image_config = {
            "base_url": config["images"]["base_url"],
            "secure_base_url": config["images"]["secure_base_url"],
            "backdrop_size_list": config["images"]["backdrop_sizes"],
            "poster_size_list": config["images"]["poster_sizes"],
            "profile_size_list": config["images"]["profile_sizes"],
        }
        self.base_url = self._image_config.get("base_url")
        self.secure_base_url = self._image_config.get("secure_base_url")
        self.backdrop_size_list = self._image_config.get("backdrop_size_list")
        self.poster_size_list = self._image_config.get("poster_size_list")
        self.profile_size_list = self._image_config.get("profile_size_list")

    def _get_image_url(
        self, url_path: str, image_size: str = "original", secure: bool = False
    ) -> str:
        if not secure:
            return self.base_url + image_size + url_path
        return self.secure_base_url + image_size + url_path
