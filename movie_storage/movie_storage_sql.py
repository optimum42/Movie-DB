from sqlalchemy import create_engine, text
#from movie_storage_sql import add_movie, list_movies, delete_movie, update_movie

# Define the database URL
DB_URL = "sqlite:///data/movies.db" # when called from movie_db.py

if __name__ == "__main__":
    DB_URL = "sqlite:///../data/movies.db"  # when called from this file

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT NOT NULL
        )
    """))
    connection.commit()


def movie_exists(movie_name):
    """
    Checks if a movie is in the database.
    :param movie_name: movie name
    :return: True if it is in the database, False otherwise
    """
    movies = list_movies()
    for movie in movies:
        if movie['title'] == movie_name:
            return True
    return False


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, poster FROM movies"))
        movies = result.fetchall()

#    return {row[0]: {"year": row[1], "rating": row[2]} for row in movies}
    return [{'title': row[0], 'year': row[1], 'rating': row[2], 'poster': row[3]} for row in movies]


def add_movie(title, year, rating, poster):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO movies (title, year, rating, poster) VALUES (:title, :year, :rating, :poster)"),
                               {"title": title, "year": year, "rating": rating, "poster": poster})
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM movies WHERE title = :title"),
                               {"title": title})
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("UPDATE movies SET rating =  :rating WHERE title = :title"),
                               {"rating": rating, "title": title})
            connection.commit()
        except Exception as e:
            print(f"Error: {e}")


# Movie 'Inception' added successfully.
# ['Inception': {'year': 2010, 'rating': 8.8}]
# Movie 'Inception' updated successfully.
# ['Inception': {'year': 2010, 'rating': 9.0}]
# Movie 'Inception' deleted successfully.
# []
def run_test():
    # Test adding a movie
    add_movie("Inception", 2010, 8.8,
              "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_QL75_UX380_CR0,0,380,562_.jpg")

    # Test listing movies
    movies = list_movies()
    print(movies)

    # Test updating a movie's rating
    update_movie("Inception", 9.0)
    print(list_movies())

    # Test deleting a movie
    delete_movie("Inception")
    print(list_movies())  # Should be empty if it was the only movie


def main():
    run_test()


if __name__ == "__main__":
    main()
