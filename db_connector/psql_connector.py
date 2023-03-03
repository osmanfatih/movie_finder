import ipdb
import abc
import os
import supabase

from typing import Dict, Any, List

from mf_representations.enums import RecordType, SupaMainData
from db_connector.connector import ConnectorBase
from db_connector.tmdb_connector import TmdbConnector
from mf_utils import logger_setup
import logging

logger = logger_setup.get_logger("supa_main_logger", "main_data_update_logs.txt")


class SupaConnector(ConnectorBase):
    @abc.abstractproperty
    def TABLE_NAME(cls) -> str:
        pass

    @property
    def AUTH_TOKEN(cls) -> str:
        return os.environ.get("SUPA_AUTH_TOKEN")

    @property
    def URL_BASE(cls) -> str:
        return os.environ.get("SUPA_BASE_URL")

    @property
    def PROJECT_PASSWORD(cls) -> str:
        return os.environ.get("SUPA_DB_KEY")

    @abc.abstractmethod
    def generate_supa_client(self) -> bool:
        pass

    def __init__(self) -> None:
        self.generate_supa_client()


class SupaTmdbConnector(SupaConnector):
    @property
    def TABLE_NAME(cls) -> str:
        return "mf_main"

    @property
    def COLUMN_NAMES(cls) -> List[str]:
        column_list = ["tmdb_id", "title", "type", "popularity"]
        return column_list

    def __init__(self) -> None:
        super().__init__()
        self.generate_tmdb_client()

    @classmethod
    def generate_tmdb_client(cls) -> bool:
        cls.tmdb_connector = TmdbConnector()
        return True

    def generate_supa_client(self) -> bool:
        self.client = supabase.create_client(self.URL_BASE, self.AUTH_TOKEN)
        self.client.table(self.TABLE_NAME).select("*").limit(1).execute()
        return True

    def _insert_tmdb_data(self, data_record: SupaMainData) -> bool:
        response = self.client.table(self.TABLE_NAME).insert(data_record._to_dict()).execute()
        return len(response.data) > 0

    def _update_tmdb_data(self, unique_id: int, data_record: SupaMainData) -> bool:
        ipdb.set_trace()
        response = (
            self.client.table(self.TABLE_NAME)
            .update(data_record._to_dict())
            .eq("unique_id", unique_id)
            .execute()
        )
        return len(response.data) > 0

    def _update_existing_tmdb_data(self, data_record: SupaMainData) -> bool:
        pass

    def _check_data_exists(self, data_record: SupaMainData) -> bool:
        # check if data exists
        type_response = (
            self.client.table(self.TABLE_NAME)
            .select("*")
            .eq("tmdb_id", data_record.tmdb_id)
            .eq("type", data_record.type.name)
        ).execute()
        if len(type_response.data) > 0:
            logger.log(
                level=logging.INFO, msg=f"Tried to insert existing data: {data_record._to_dict()}."
            )
            return True
        return False

    def _supa_main_to_data_record(self, data_dict: Dict[str, Any]):
        return SupaMainData(
            tmdb_id=data_dict["tmdb_id"],
            type=RecordType(data_dict["type"]),
            title=data_dict["title"],
            popularity=data_dict["popularity"],
        )

    def insert_tmdb_daily_export_movies(self) -> bool:
        logger.log(level=logging.INFO, msg="Inserting all TMDB movie data...")
        for item in self.tmdb_connector.get_all_movie_id_titles():
            supa_main_data_record = SupaMainData(
                tmdb_id=int(item["tmdb_id"]),
                type=RecordType.MOVIE,
                title=item["title"],
                popularity=item["popularity"],
            )
            if not self._check_data_exists(supa_main_data_record):
                assert self._insert_tmdb_data(
                    supa_main_data_record
                ), f"Failed to insert the MOVIE data: {supa_main_data_record._to_dict()}"
        logger.log(level=logging.INFO, msg="All TMDB movie data inserted!")

    def insert_tmdb_daily_export_series(self) -> bool:
        for item in next(self.tmdb_connector.get_all_series_id_titles()):
            supa_main_data_record = SupaMainData(
                tmdb_id=int(item["tmdb_id"]),
                type=RecordType.SERIES,
                title=item["title"],
                popularity=item["popularity"],
            )
            if not self._check_data_exists(supa_main_data_record):
                assert self._insert_tmdb_data(
                    supa_main_data_record
                ), f"Failed to insert the SERIES data: {supa_main_data_record._to_dict()}"

    def insert_tmdb_daily_export_artist(self) -> bool:
        for item in next(self.tmdb_connector.get_all_artist_id_titles()):
            supa_main_data_record = SupaMainData(
                tmdb_id=int(item["tmdb_id"]),
                type=RecordType.ARTIST,
                title=item["title"],
                popularity=item["popularity"],
            )
            if not self._check_data_exists(supa_main_data_record):
                assert self._insert_tmdb_data(
                    supa_main_data_record
                ), f"Failed to insert the ARTIST data: {supa_main_data_record._to_dict()}"

    def insert_all_tmdb_data(self) -> bool:
        assert self.insert_tmdb_daily_export_movies(), "Daily export movie insert error"
        assert self.insert_tmdb_daily_export_artist(), "Daily export series insert error"
        assert self.insert_tmdb_daily_export_artist(), "Daily export artists insert error"

    def update_tmdb_record(self, data_dict: Dict[str, Any]) -> bool:
        pass


if __name__ == "__main__":
    connector = SupaTmdbConnector()
    connector.insert_tmdb_daily_export_movies()
    ipdb.set_trace()
