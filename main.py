import requests
import os

url = "https://streaming-availability.p.rapidapi.com/countries"

headers = {
    "X-RapidAPI-Key": os.environ.get("RAPID_KEY"),
    "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com",
}

response = requests.request("GET", url, headers=headers)

print(response.text)
import ipdb

ipdb.set_trace()


import requests
import os
import time


def retrieve_movie_names_and_ids():
    api_key = os.environ["TMDB_API_KEY"]
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page="

    page = 1
    movies = []

    while True:
        response = requests.get(url + str(page))
        data = response.json()
        movies.extend(data["results"])
        if data["page"] == data["total_pages"]:
            break
        page += 1
        time.sleep(5)

    movie_names_and_ids = []

    for movie in movies:
        movie_names_and_ids.append({"name": movie["title"], "id": movie["id"]})

    return movie_names_and_ids
