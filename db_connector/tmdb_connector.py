import json
import gzip
import ipdb
import time
import requests
import os
import jsonlines
import tempfile
import pandas as pd

from pathlib import Path
from datetime import date
from typing import List, Dict, Any, Union

from db_connector.connector import ConnectorBase
from mf_representations.records import MovieRecord, SeriesRecord, ArtistRecord
from mf_representations.enums import RecordType
from mf_representations.configs import TmdbImageConfig


class TmdbExporter:
    def _get_tmdb_daily_export(self, type: str) -> Path:
        files_base_url = "http://files.tmdb.org/p/exports/"
        today_date = date.today().strftime("%d_%m_%Y")
        export_url = f"{files_base_url}{type}_ids_{today_date}.json.gz"
        req_json_file = requests.get(export_url)
        req_json_file.raise_for_status()

        written_file_name = Path(__file__).parent.resolve() / f"{type}_title_id_list.jsonl"
        with open(written_file_name, "w") as f:
            f.write(req_json_file.content)
        return written_file_name

    def export_all_movie_id_titles(self) -> pd.DataFrame:
        data = []
        with open(self._get_tmdb_daily_export("movie"), "r") as f:
            for line in f.readlines():
                try:
                    obj = json.loads(line)
                    data.append(
                        {
                            "tmdb_id": obj["id"],
                            "title": obj["original_title"],
                            "popularity": obj["popularity"],
                            "type": RecordType.MOVIE.name,
                        }
                    )
                except:
                    continue
        return pd.DataFrame(data)

    def export_all_series_id_titles(self) -> pd.DataFrame:
        data = []
        with open(self._get_tmdb_daily_export("tv_series"), "r") as f:
            for line in f.readlines():
                try:
                    obj = json.loads(line)
                    data.append(
                        {
                            "tmdb_id": obj["id"],
                            "title": obj["original_name"],
                            "popularity": obj["popularity"],
                            "type": RecordType.SERIES.name,
                        }
                    )
                except:
                    continue
        return pd.DataFrame(data)

    def export_all_artist_id_titles(self) -> pd.DataFrame:
        data = []
        with open(self._get_tmdb_daily_export("person"), "r") as f:
            for line in f.readlines():
                try:
                    obj = json.loads(line)
                    data.append(
                        {
                            "tmdb_id": obj["id"],
                            "title": obj["name"],
                            "popularity": obj["popularity"],
                            "type": RecordType.ARTIST.name,
                        }
                    )
                except:
                    continue
        return pd.DataFrame(data)

    def export_all_id_titles(self) -> None:
        df = pd.concat(
            [
                self.export_all_movie_id_titles(),
                self.export_all_series_id_titles(),
                self.export_all_artist_id_titles(),
            ]
        )
        df.drop(index=df[df.title.apply(len) == 0].index, inplace=True)
        df.reset_index(inplace=True)
        df.drop(columns=["index"], inplace=True)
        all_export_file_name = Path(__file__).parent.resolve() / "all_id_titles.csv"
        df.to_csv(all_export_file_name, sep="|", index_label="id", float_format="%g")


class TmdbConnector(ConnectorBase):
    """
    Interface for connecting to the TMDB API that inherits from the ConnectorBase
    """

    @property
    def AUTH_TOKEN(cls) -> str:
        return os.environ.get("TMDB_AUTH")

    @property
    def URL_BASE(cls) -> str:
        return "https://api.themoviedb.org/3"

    def __init__(self) -> None:
        self.tmdb_config = self._get_tmdb_config()
        self.image_config = TmdbImageConfig(self.tmdb_config)

    def _make_request(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def _get_tmdb_config(self) -> None:
        url = f"{self.URL_BASE}/configuration?api_key={self.AUTH_TOKEN}"
        config_data = self._make_request(url)
        return config_data

    def _get_record_details(self, record_type: RecordType, tmdb_id: int):
        url = f"{self.URL_BASE}/{record_type.value.lower()}/{tmdb_id}?api_key={self.AUTH_TOKEN}"
        data = self._make_request(url)
        return data

    def _generate_movie_record_from_response(self, movie_data: Dict[str, Any]) -> MovieRecord:
        return MovieRecord(**movie_data)

    def _generate_series_record_from_response(self, series_data: Dict[str, Any]) -> SeriesRecord:
        return SeriesRecord(**series_data)

    def _generate_artist_record_from_response(self, artist_data: Dict[str, Any]) -> ArtistRecord:
        return ArtistRecord(**artist_data)

    def _get_popular_n(self, num_records: int, record_type: RecordType):
        url = f"{self.URL_BASE}/{record_type.value.lower()}/popular?api_key={self.AUTH_TOKEN}&page="
        page = 1
        data = []
        while len(data < num_records):
            response = requests.get(url + str(page))
            data = response.json()
            for item_data in data["results"]:
                if record_type == RecordType.MOVIE:
                    item_data = self._generate_movie_record_from_response(item_data)
                elif record_type == RecordType.SERIES:
                    item_data = self._generate_artist_record_from_response(item_data)
                elif record_type == RecordType.ARTIST:
                    item_data = self._generate_artist_record_from_response(item_data)
                else:
                    raise ValueError(f"Unsupported record type: {record_type}")
                data.append(item_data)

            if data["page"] == data["total_pages"]:
                break
            page += 1
            time.sleep(2)

        return data

    def get_movie_details(self, tmdb_id: int):
        data = self._get_record_details(RecordType.MOVIE, tmdb_id)
        ipdb.set_trace()
        return self._generate_movie_record_from_response(data)

    def get_series_details(self, tmdb_id: int):
        data = self._get_record_details(RecordType.SERIES, tmdb_id)
        ipdb.set_trace()
        return self._generate_series_record_from_response(data)

    def get_artist_details(self, tmdb_id: int):
        data = self._get_record_details(RecordType.ARTIST, tmdb_id)
        ipdb.set_trace()
        return self._generate_artist_record_from_response(data)

    def get_popular_n_movies(self, num_records: int) -> List[MovieRecord]:
        return self._get_popular_n(num_records, record_type=RecordType.MOVIE)

    def get_popular_n_series(self, num_records: int) -> List[SeriesRecord]:
        return self._get_popular_n(num_records, record_type=RecordType.SERIES)

    def get_popular_n_artists(self, num_records: int) -> List[ArtistRecord]:
        return self._get_popular_n(num_records, record_type=RecordType.ARTIST)

    def get_most_popular_movies(self) -> List[MovieRecord]:
        """
        Function that returns the movie records of top 20 popular movies
        Returns:
            List[MovieRecord]: List of MovieRecord objects
        """
        url = f"{self.URL_BASE}/{RecordType.MOVIE.name.lower()}/popular?api_key={self.AUTH_TOKEN}"
        data = self._make_request(url)
        movie_record_list = []
        for movie_data in data["results"]:
            movie_record = self._generate_movie_record_from_response(movie_data)
            movie_record_list.append(movie_record)
        return movie_record_list

    def get_most_popular_series(self) -> List[SeriesRecord]:
        """
        Function that returns the series records of top 20 popular series
        Returns:
            List[SeriesRecord]: List of SeriesRecord objects
        """
        url = f"{self.URL_BASE}/{RecordType.SERIES.name.lower()}/popular?api_key={self.AUTH_TOKEN}"
        data = self._make_request(url)
        series_record_list = []
        for series_data in data["results"]:
            series_record = self._generate_series_record_from_response(series_data)
            series_record_list.append(series_record)
        return series_record_list

    def get_most_popular_artists(self) -> List[ArtistRecord]:
        """
        Function that returns the artist records of top 20 popular artists
        Returns:
            List[ArtistRecord]: List of SeriesRecord objects
        """
        url = f"{self.URL_BASE}/{RecordType.ARTIST.name.lower()}/popular?api_key={self.AUTH_TOKEN}"
        data = self._make_request(url)
        artist_record_list = []
        for artist_data in data["results"]:
            artist_record = self._generate_artist_record_from_response(artist_data)
            artist_record_list.append(artist_record)
        return artist_record_list


if __name__ == "__main__":
    import ipdb

    connector = TmdbConnector()
    connector.get_artist_details(tmdb_id=1253360)
    ipdb.set_trace()
