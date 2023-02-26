import time
import requests
import os
import jsonlines
import tempfile

from datetime import date
from typing import List, Dict, Any, Tuple

from db_connector.connector import ConnectorBase
from mf_representations.records import MovieRecord, SeriesRecord, ArtistRecord
from mf_representations.enums import RecordType


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
        if response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

    def _get_tmdb_config(self) -> None:
        url = f"{self.URL_BASE}/configuration?api_key={self.AUTH_TOKEN}"
        config_data = self._make_request(url)
        return config_data

    def _get_record_details(self, record_type: RecordType, tmdb_id: int):
        url = f"{self.base_url}/{record_type}/{tmdb_id}?api_key={self.api_key}"
        data = self._make_request(url)
        return data

    def _get_tmdb_daily_export(self, type: str) -> Dict[str, Any]:
        files_base_url = "http://files.tmdb.org/p/exports/"
        today_date = date.today().strftime("%d_%m_%Y")

        export_url = f"{files_base_url}{type}_ids_{today_date}.json.gz"
        req_json_file = requests.get(export_url)

        temp_json_file = tempfile.TemporaryFile()
        temp_json_file.write(req_json_file.content)
        temp_json_file.seek(0)
        with jsonlines.open(temp_json_file) as reader:
            for obj in reader:
                yield (obj["id"], obj["original_title"])

    def get_all_movie_id_titles(self, batch_size=10) -> Tuple[int, str]:
        pass

    def _generate_movie_record_from_response(
        self, movie_data: Dict[str, Any]
    ) -> MovieRecord:
        return MovieRecord(
            record_name=movie_data["title"],
            record_id=movie_data["id"],
            is_adult=movie_data["adult"],
            backdrop_path=movie_data["backdrop_path"],
            poster_path=movie_data["poster_path"],
            genre_ids=movie_data["genre_ids"],
            language=movie_data["original_language"],
            description=movie_data["overview"],
            release_date=movie_data["release_date"],
            vote_avg=movie_data["vote_average"],
            vote_count=movie_data["vote_count"],
        )

    def _generate_series_record_from_response(
        self, series_data: Dict[str, Any]
    ) -> SeriesRecord:
        pass

    def _generate_artist_record_from_response(
        self, artist_data: Dict[str, Any]
    ) -> ArtistRecord:
        pass

    def get_most_popular_movies(self) -> List[MovieRecord]:
        """
        Function that returns the movie records of top 20 popular movies
        Returns:
            List[MovieRecord]: List of MovieRecord objects
        """
        url = f"{self.URL_BASE}/movie/popular?api_key={self.AUTH_TOKEN}"
        data = self._make_request(url)
        movie_record_list = []
        for movie_data in data["results"]:
            movie_record = self._generate_movie_record_from_response(movie_data)
            movie_record_list.append(movie_record)
        return movie_record_list

    def get_popular_movies(self, num_records: int) -> List[MovieRecord]:
        url = f"{self.URL_BASE}/movie/popular?api_key={self.AUTH_TOKEN}&page="

        page = 1
        movies = []
        while len(movies < num_records):
            response = requests.get(url + str(page))
            data = response.json()
            movies.extend(
                [
                    self._generate_movie_record_from_response(movie_data)
                    for movie_data in data["results"]
                ]
            )
            if data["page"] == data["total_pages"]:
                break
            page += 1
            time.sleep(5)

        return movies

    def get_movie_details(self, tmdb_id: int):
        data = self._get_record_details(RecordType.MOVIE, tmdb_id)
        return {
            "name": data["title"],
            "id": data["id"],
            "overview": data["overview"],
            "release_date": data["release_date"],
            "popularity": data["popularity"],
        }

    def get_series_details(self, tmdb_id: int):
        data = self._get_record_details(RecordType.SERIES, tmdb_id)

    def get_popular_series(self):
        pass


if __name__ == "__main__":
    import ipdb

    connector = TmdbConnector()
    pop_movies = connector.get_most_popular_movies()
    ipdb.set_trace()
