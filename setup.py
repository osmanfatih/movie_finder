from setuptools import setup

with open("requirements/requirements.txt", "r") as f:
    requirements = f.read().split("\n")

setup(
    name="movie-finder",
    version="0.0.1",
    description="Movie Finder Server and Utilities",
    packages=[
        "db_connector",
        "rem_engine",
        "mf_representations",
        "mf_utils",
        "mf_server",
    ],
    author="Osman Fatih Kilic",
    author_email="osmanfatihkilic@gmail.com",
    install_requires=requirements,
)
