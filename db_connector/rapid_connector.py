import ipdb
import datetime
import os
import dataclasses
import requests

from typing import Dict, Any, List, Union

from db_connector.connector import ConnectorBase
from mf_representations.records import RecordType
from mf_representations.enums import PlatformType, RapidPlatformInfoCountry


class RapidConnector(ConnectorBase):
    @property
    def AUTH_TOKEN(cls) -> str:
        return os.environ.get("RAPID_KEY")

    @property
    def HOST_BASE(cls) -> str:
        return "streaming-availability.p.rapidapi.com"

    @property
    def URL_BASE(cls) -> str:
        return "https://streaming-availability.p.rapidapi.com"

    @property
    def URL_GET_BASIC(cls) -> str:
        return f"{cls.URL_BASE}/get/basic"

    @property
    def URL_GET_COUNTRIES(cls) -> str:
        return f"{cls.URL_BASE}/countries"

    @property
    def URL_GET_TMDB_GENRE(cls) -> str:
        return f"{cls.URL_BASE}/genres"

    @property
    def HEADERS(cls) -> Dict[str, Any]:
        return {"X-RapidAPI-Key": cls.AUTH_TOKEN, "X-RapidAPI-Host": cls.HOST_BASE}

    def get_country_streaming_info(self, platform_type: PlatformType) -> List[str]:
        response = requests.request("GET", self.URL_GET_COUNTRIES, headers=self.HEADERS)
        response.raise_for_status()
        return response.json().get(platform_type.name.lower())

    def check_platform_available_in_country(
        self, platform_type: PlatformType, country: str
    ) -> List[str]:
        response = requests.request("GET", self.URL_GET_COUNTRIES, headers=self.HEADERS)
        response.raise_for_status()
        return country in response.json().get(platform_type.name.lower())

    def get_country_platform_info(self, country: str) -> List[PlatformType]:
        response = requests.request("GET", self.URL_GET_COUNTRIES, headers=self.HEADERS)
        response.raise_for_status()
        country_platform_list = []
        for platform in PlatformType:
            if country in response.json().get(platform.name.lower()):
                country_platform_list.append(platform)
        return country_platform_list

    def get_tmdb_genre_id_list(self) -> Dict[int, str]:
        response = requests.request("GET", self.URL_GET_TMDB_GENRE, headers=self.HEADERS)
        response.raise_for_status()
        return response.json()

    def get_platform_info(
        self, tmdb_id: int, type: RecordType, country: str = "us", output_language: str = "en"
    ) -> Dict[str, Any]:
        query = {
            "tmdb_id": f"{type.name.lower()}/{tmdb_id}",
            "output_language": output_language,
            "country": country,
        }
        response = requests.get(self.URL_GET_BASIC, headers=self.HEADERS, params=query)
        response.raise_for_status()
        movie_platform_info = RapidPlatformInfoCountry()
        movie_platform_info.generate_data_from_rapid(response.json())
        return movie_platform_info
