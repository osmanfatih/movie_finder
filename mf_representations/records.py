from copy import deepcopy
import dateutil
import datetime
import dataclasses
import abc

from typing import List

from mf_representations.enums import RecordType


class RecordBase(abc.ABC):
    """
    Base class for all type of movie, actor, genre, tmdb records
    """

    @abc.abstractproperty
    @classmethod
    def RECORD_TYPE(cls) -> str:
        """
        Indicates for which type of record this class has
        been created

        Returns:
            str: type of the record
        """
        pass

    def __init__(self, record_name: str, record_id: str) -> None:
        self.record_name = record_name
        self.record_id = record_id
        self.unique_id = self.RECORD_TYPE + self.record_id


class TmdbRecord(RecordBase):
    """
    Class for generating TMDB record objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.TMDB

    def __init__(self, record_name: str, record_id: str) -> None:
        super().__init__(record_name, record_id)


class MovieRecord(RecordBase):
    """
    Class for generating Movie record objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.MOVIE

    def __init__(self, **kwargs) -> None:
        self.title: str = kwargs["title"]
        self.tmdb_id: int = kwargs["id"]
        self.popularity: float = kwargs.get("popularity")
        self.vote_avg: float = kwargs.get("vote_count")
        self.vote_count: int = kwargs.get("vote_average")
        self.backdrop_path: str = kwargs.get("backdrop_path")
        self.poster_path: str = kwargs.get("poster_path")
        self.description: str = kwargs.get("description")
        self.overview: str = kwargs.get("overview")
        self.tagline: str = kwargs.get("tagline")
        self.runtime: int = kwargs.get("runtime")
        self.release_date: datetime = (
            dateutil.parser.parse(kwargs.get("release_date"))
            if kwargs.get("release_date")
            else None
        )
        self.release_status: str = kwargs.get("release_status")
        self.genres: List[dict] = kwargs.get("genres")
        self.video: bool = kwargs.get("video")
        self.meta_data: dict = {
            "adult": kwargs.get("adult"),
            "belongs_to_collection": kwargs.get("belongs_to_collection"),
            "budget": kwargs.get("budget"),
            "homepage": kwargs.get("homepage"),
            "imdb_ib": kwargs.get("imdb_id"),
            "original_language": kwargs.get("original_language"),
            "original_title": kwargs.get("original_title"),
            "production_companies": kwargs.get("production_companies"),
            "production_countries": kwargs.get("production_countries"),
            "revenue": kwargs.get("revenue"),
            "spoken_languages": kwargs.get("spoken_languages"),
        }

        # Create DB dictionary here so that we can push it later
        self._data_dict = deepcopy(self.__dict__)


class SeriesRecord(RecordBase):
    """
    Class for generating Series record objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.SERIES

    def __init__(self, **kwargs) -> None:
        self.title: str = kwargs["name"]
        self.tmdb_id: int = kwargs["id"]
        self.popularity: float = kwargs.get("popularity")
        self.vote_avg: float = kwargs.get("vote_average")
        self.vote_count: int = kwargs.get("vote_count")
        self.backdrop_path: str = kwargs.get("backdrop_path")
        self.poster_path: str = kwargs.get("poster_path")
        self.overview: str = kwargs.get("overview")
        self.tagline: str = kwargs.get("tagline")
        self.episode_run_time: int = kwargs.get("episode_run_time")
        self.first_air_date: datetime = (
            dateutil.parser.parse(kwargs.get("first_air_date"))
            if kwargs.get("first_air_date")
            else None
        )
        self.genres: dict = kwargs.get("genres")
        self.networks: dict = kwargs.get("networks")
        self.release_status: str = kwargs.get("status")
        self.meta_data = {
            "adult": kwargs.get("adult"),
            "created_by": kwargs.get("created_by"),
            "homepage": kwargs.get("homepage"),
            "in_production": kwargs.get("in_production"),
            "languages": kwargs.get("languages"),
            "last_air_date": dateutil.parser.parse(kwargs.get("last_air_date"))
            if kwargs.get("last_air_date")
            else None,
            "last_episode_to_air": kwargs.get("last_episode_to_air"),
            "next_episode_to_air": kwargs.get("next_episode_to_air"),
            "number_of_episodes": kwargs.get("number_of_episodes"),
            "number_of_seasons": kwargs.get("number_of_seasons"),
            "origin_country": kwargs.get("origin_country"),
            "original_language": kwargs.get("original_language"),
            "original_name": kwargs.get("original_name"),
            "production_companies": kwargs.get("production_companies"),
            "production_countries": kwargs.get("production_countries"),
            "seasons": kwargs.get("seasons"),
            "spoken_language": kwargs.get("spoken_language"),
            "type": kwargs.get("type"),
        }

        # Create DB dictionary here so that we can push it later
        self._data_dict = deepcopy(self.__dict__)


class ArtistRecord(RecordBase):
    """
    Class for generating people/actor/actress/director objects
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.ARTIST

    def __init__(self, **kwargs) -> None:
        self.tmdb_id = kwargs.get("id")
        self.title = kwargs.get("name")
        self.popularity = kwargs.get("popularity")
        self.imdb_id = kwargs.get("imdb_id")
        self.biography = kwargs.get("biography")
        self.meta_data = {
            "also_known_as": kwargs.get("also_known_as"),
            "birthday": kwargs.get("birthday"),
            "deathday": kwargs.get("deathday"),
            "gender": kwargs.get("gender"),
            "homepage": kwargs.get("homepage"),
            "known_for_department": kwargs.get("known_for_department"),
            "place_of_birth": kwargs.get("place_of_birth"),
        }

        # Create DB dictionary here so that we can push it later
        self._data_dict = deepcopy(self.__dict__)


class NetworkRecord(RecordBase):
    """
    Class for generating Network record objects
    such as a record for Universal/Paramount etc. network
    This class probably will not be used for now
    """

    @property
    def RECORD_TYPE(cls) -> str:
        return RecordType.NETWORK

    def __init__(self, record_name: str, record_id: str) -> None:
        super().__init__(record_name, record_id)
