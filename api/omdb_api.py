import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

OMDB_MOVIE_URL = f"https://www.omdbapi.com/?apikey={API_KEY}&t="


def fetch_movie(movie_name):
    """
    fetches a movie via OMDB API and returns it as a dictionary
    if exists else None
    """
    try:
        res = requests.get(OMDB_MOVIE_URL + movie_name)
        if res.status_code == 200:
            data = res.json()
            if data.get("Response") == 'True':
                return data
        else:
            return None
    except Exception as e:
        print(e)
        return None


def main():
    movie = get_movie("Titanic")
    for key, value in movie.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()