from sqlalchemy import create_engine, text

# Define the database URL
DB_URL = "sqlite:///../data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=True)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL
        )
    """))
    connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating FROM movies"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2]} for row in movies}


def add_movie(title, year, rating):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(text("INSERT INTO movies (title, year, rating) VALUES (:title, :year, :rating)"),
                               {"title": title, "year": year, "rating": rating})
            connection.commit()
            print(f"Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    pass


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    pass


# Movie 'Inception' added successfully.
# ['Inception': {'year': 2010, 'rating': 8.8}]
# Movie 'Inception' updated successfully.
# ['Inception': {'year': 2010, 'rating': 9.0}]
# Movie 'Inception' deleted successfully.
# []
def run_test():
    """ Tests the storage functions """
    from movie_storage_sql import add_movie, list_movies, delete_movie, \
        update_movie

    # Test adding a movie
    add_movie("Inception", 2010, 8.8)

    # Test listing movies
    movies = list_movies()
    print(movies)

    # Test updating a movie's rating
    update_movie("Inception", 9.0)
    print(list_movies())

    # Test deleting a movie
    delete_movie("Inception")
    print(list_movies())  # Should be empty if it was the only movie