from enum import Enum


class RecordType(Enum):
    """
    Enum class for storing TMDB prefixes
    """

    TMDB = "tmdb"
    MOVIE = "movie"
    SERIES = "tv"
    ARTIST = "person"
    NETWORK = "network"
