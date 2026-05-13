import json

MOVIES_JSON = "data/movies.json"


def create_movie_db():
    """
    this function creates a new movie database
    :return: list of movies
    """
    movies = [
        {
            "Title": "The Shawshank Redemption",
            "Rating": 9.5,
            "Year": 1995,
        },
        {
            "Title": "Pulp Fiction",
            "Rating": 8.8,
            "Year": 1995,
        },
        {
            "Title": "The Room",
            "Rating": 3.6,
            "Year": 2003,
        },
        {
            "Title": "The Godfather",
            "Rating": 9.2,
            "Year": 1982,
        },
        {
            "Title": "The Godfather: Part II",
            "Rating": 9.0,
            "Year": 1983,
        },
        {
            "Title": "The Dark Knight",
            "Rating": 9.0,
            "Year": 2008,
        },
        {
            "Title": "12 Angry Men",
            "Rating": 8.9,
            "Year": 1957,
        },
        {
            "Title": "Everything Everywhere All At Once",
            "Rating": 8.9,
            "Year": 2022,
        },
        {
            "Title": "Forrest Gump",
            "Rating": 8.8,
            "Year": 19934,
        },
        {
            "Title": "Star Wars: Episode V",
            "Rating": 8.7,
            "Year": 1980,
        },
    ]
    return movies


def movie_exists(movie_name):
    """
    Checks if a movie is in the database.
    :param movie_name: movie name
    :return: True if it is in the database, False otherwise
    """
    movies = get_movies()
    for movie in movies:
        if movie['Title'] == movie_name:
            return True
    return False


def get_movies():
    """
    Returns a list of dictionaries that
    contains the movies information in the database.
    The function loads the information from the JSON
    file and returns the data.
    """
    file_name = MOVIES_JSON
    try:
        with open(file_name, "r") as f:
            movie_db = json.loads(f.read())
            movies = movie_db['data']
    except FileNotFoundError:
        print(f"The JSON file '{file_name}' was not found.")
        movies = create_movie_db()
        save_movies(movies)
        print("New database created.")
    return movies


def save_movies(movies):
    """
    Gets all the movies as an argument and saves them to the JSON file.
    """
    movie_db = {
        'title': 'HM Movie Database',
        'author': 'Holger Massek',
        'data': movies,
    }
    json_str = json.dumps(movie_db)
    with open(MOVIES_JSON, "w") as f:
        f.write(json_str)


def add_movie(title, year, rating):
    """
    Adds a movie to the movies database.
    Loads the information from the JSON file, adds the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movie = {
        "Title": title,
        "Year": year,
        "Rating": rating,
    }
    movies = get_movies()
    movies.append(movie)
    save_movies(movies)


def delete_movie(title):
    """
    Deletes a movie from the movies database.
    Loads the information from the JSON file, deletes the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    for movie in movies:
        if movie['Title'] == title:
            movies.remove(movie)
            break
    save_movies(movies)


def update_movie(title, rating):
    """
    Updates a movie from the movies database.
    Loads the information from the JSON file, updates the movie,
    and saves it. The function doesn't need to validate the input.
    """
    movies = get_movies()
    for movie in movies:
        if movie['Title'] == title:
            movie['Rating'] = rating
            break
    save_movies(movies)

