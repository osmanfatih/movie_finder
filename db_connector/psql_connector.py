import ipdb
import abc
import os
import supabase

from typing import Dict, Any

from mf_representations.enums import RecordType
from db_connector.connector import ConnectorBase
from db_connector.tmdb_connector import TmdbConnector


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

    @classmethod
    def generate_supa_client(cls) -> bool:
        cls.client = supabase.create_client(cls.URL_BASE, cls.AUTH_TOKEN)
        cls.client.table("mf_main").select("*").limit(1).execute()
        return True

    @classmethod
    def generate_tmdb_client(cls) -> bool:
        cls.tmdb_connector = TmdbConnector()
        return True

    def __init__(self) -> None:
        pass


class SupaTmdbConnector(SupaConnector):
    @property
    def TABLE_NAME(cls) -> str:
        return "mf_main"

    def __init__(self) -> None:
        super().__init__()

    def _insert_tmdb_data(self, data_dict: Dict[str, Any]) -> bool:
        response = self.client.table(self.TABLE_NAME).insert(data_dict).execute()
        return len(response.data) > 0

    def _update_tmdb_data(self, data_dict: Dict[str, Any]) -> bool:
        if "unique_id" not in data_dict:
            raise ValueError("unique_id required for TMDB data update.")
        response = self.client.table(self.TABLE_NAME).update(data_dict).eq("unique_id", data_dict.pop("unique_id")).execute()
        return len(response.data) > 0

    def insert_tmdb_daily_export_movies(self) -> bool:
        for item in next(self.tmdb_connector.get_all_movie_id_titles()):
            data_dict = {"tmdb_id": int(item["tmdb_id"]), "title": item["title"], "type": RecordType.MOVIE}
            assert self._insert_tmdb_data(data_dict), f"Failed to insert the data: {data_dict}"

    def insert_tmdb_daily_export_series(self) -> bool:
        for item in next(self.tmdb_connector.get_all_series_id_titles()):
            data_dict = {"tmdb_id": int(item["tmdb_id"]), "title": item["title"], "type": RecordType.SERIES}
            assert self._insert_tmdb_data(data_dict)

    def insert_tmdb_daily_export_artist(self) -> bool:
        for item in next(self.tmdb_connector.get_all_artist_id_titles()):
            data_dict = {"tmdb_id": int(item["tmdb_id"]), "title": item["title"], "type": RecordType.ARTIST}
            assert self._insert_tmdb_data(data_dict)


if __name__ == "__main__":
    connector = SupaConnector()
    connector.insert_tmdb_movies()
