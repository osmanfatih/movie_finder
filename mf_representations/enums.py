import ipdb
import datetime

from enum import Enum
from dataclasses import dataclass, asdict

from typing import List, Dict, Any


class RecordType(Enum):
    """
    Enum class for storing TMDB prefixes
    """

    TMDB = "tmdb"
    MOVIE = "movie"
    SERIES = "tv"
    ARTIST = "person"
    NETWORK = "network"


@dataclass
class SupaMainData:
    tmdb_id: int
    type: RecordType
    title: str = None
    popularity: float = None

    def _to_dict(self):
        dict_to_return = {key: value for key, value in asdict(self).items() if value is not None}
        dict_to_return["type"] = dict_to_return["type"].name
        return dict_to_return


class PlatformType(Enum):
    """
    List of available platforms on RapidAPI
    """

    NETFLIX = "netflix"
    PRIME = "prime"
    DISNEY = "disney"
    HBO = "hbo"
    HULU = "hulu"
    PEACOCK = "peacock"
    PARAMOUNT = "paramount"
    STARZ = "starz"
    SHOWTIME = "showtime"
    APPLE = "apple"
    MUBI = "mubi"

    def get_all_platform_list(self) -> List[str]:
        return [item.value.lower() for item in self]


@dataclass
class StreamingInfoCountry:
    tmdb_id: int
    record_type: RecordType
    platform: PlatformType
    country: str
    link: str
    added: datetime
    leaving: datetime


@dataclass
class RapidPlatformInfoCountry:
    imdb_id: str = None
    imdb_rating: int = None
    imdb_vote_count: int = None
    tmdb_id: int = None
    tmdb_rating: int = None
    title: str = None
    genre_ids: List[int] = None
    country: str = None
    year: int = None
    runtime: int = None
    cast: List[str] = None
    related_artist: List[str] = None
    overview: str = None
    tagline: str = None
    viewer_age: int = None
    streaming_info: List[StreamingInfoCountry] = None

    def generate_streaming_info_from_rapid(
        self, data_dict: Dict[str, Any], country: str
    ) -> StreamingInfoCountry:
        if data_dict.get("streamingInfo") is None:
            return None
        streaming_info_list = []
        for platform in data_dict["streamingInfo"].keys():
            platform_type = PlatformType(platform)
            link = data_dict["streamingInfo"][platform][country]["link"]
            added_time = datetime.datetime.fromtimestamp(
                data_dict["streamingInfo"][platform][country]["added"]
            )
            leaving_time = data_dict["streamingInfo"][platform][country]["leaving"]
            leaving_time = (
                datetime.datetime.fromtimestamp(leaving_time) if leaving_time > 0 else None
            )
            streaming_info_list.append(
                StreamingInfoCountry(
                    platform=platform_type,
                    country=country,
                    link=link,
                    added=added_time,
                    leaving=leaving_time,
                )
            )
        return streaming_info_list

    def generate_data_from_rapid(self, data_dict: Dict[str, Any]) -> None:
        self.imdb_id = data_dict["imdbID"]
        self.imdb_rating = data_dict["imdbRating"]
        self.imdb_vote_count = data_dict["imdbVoteCount"]
        self.tmdb_id = data_dict["tmdbID"]
        self.tmdb_rating = data_dict["tmdbRating"]
        self.title = data_dict["title"]
        self.genre_ids = data_dict["genres"]
        self.country = data_dict["countries"][0]
        self.year = data_dict["year"]
        self.runtime = data_dict["runtime"]
        self.cast = data_dict["cast"]
        self.related_artist = data_dict["significants"]
        self.overview = data_dict["overview"]
        self.tagline = data_dict["tagline"]
        self.viewer_age = data_dict["age"]
        self.streaming_info = self.generate_streaming_info_from_rapid(
            data_dict, country=self.country.lower()
        )
