from enum import Enum
from dataclasses import dataclass, asdict


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
