from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Define the database URL
DB_URL = "sqlite:///data/movies.db" # when called from movie_db.py

if __name__ == "__main__":
    DB_URL = "sqlite:///../data/movies.db"  # when called from this file

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create tables if they do not exist
with engine.connect() as connection:

    # Users table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """))

    # Movies table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT NOT NULL,
            imdb_url TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """))
    connection.commit()


def db_execute(sql, params=None):
    """
    Executes an SQL command using params and returns the result.
        SELECT  -> returns fetched rows
        others  -> returns result info
    """

    params = params or {}
    sql_lower = sql.strip().lower()
    is_select = sql_lower.startswith("select")

    try:
        with engine.begin() as connection:
            result = connection.execute(
                text(sql),
                params
            )
            if is_select:
                return result.fetchall()
            return {
                "success": True,
                "rowcount": result.rowcount,
            }
    except SQLAlchemyError as error:
        print(f"Database error: {error}")
        return {
            "success": False,
            "error": str(error),
        }


def user_exists(user_name):
    """
    Checks if a user exists in the database.
    Returns:
        True -> user exists
        False -> user doesn't exist
    """
    sql = "SELECT id FROM users WHERE name = :name"
    params = {"name": user_name}
    users = db_execute(sql, params)
    return len(users) == 1


def get_users():
    """
    Retrieve all users from the database.
    Returns:
        dict: {user_id: user_name}
    """
    sql = "SELECT id, name FROM users ORDER BY  id"
    users = db_execute(sql)
    return {
        row[0]: row[1]
        for row in users
    }


from sqlalchemy import text


def add_user(user_name):
    """
    Add a new user to the database.
    Returns:
        True  -> user created
        False -> user already exists
    """
    if not user_exists(user_name):
        with engine.connect() as connection:
            # Create new user
            connection.execute(
                text("""
                    INSERT INTO users (name)
                    VALUES (:name)
                """),
                {"name": user_name}
            )
            connection.commit()
        return True
    return False


def movie_exists(user_name, movie_name):
    """
    Checks if a movie is in the database.
    :param movie_name: movie name
    :return: True if it is in the database, False otherwise
    """
    movies = list_movies(user_name)
    for movie in movies:
        if movie['title'] == movie_name:
            return True
    return False


def list_movies(user_name=None):
    """
    Retrieve movies from the database.
    If user_name is provided: return only movies for that user.
    If user_name is None: return all movies.
    """
    with engine.connect() as connection:

        # All movies
        if user_name is None:
            result = connection.execute(
                text("""
                    SELECT
                        movies.title,
                        movies.year,
                        movies.rating,
                        movies.poster,
                        movies.imdb_url
                    FROM movies
                    ORDER BY movies.title
                """)
            )

        # Movies for specific user
        else:
            result = connection.execute(
                text("""
                    SELECT
                        movies.title,
                        movies.year,
                        movies.rating,
                        movies.poster,
                        movies.imdb_url
                    FROM movies
                    JOIN users
                        ON movies.user_id = users.id
                    WHERE users.name = :user_name
                    ORDER BY movies.title
                """),
                {"user_name": user_name}
            )

        movies = result.fetchall()

    return [
        {
            "title": row[0],
            "year": row[1],
            "rating": row[2],
            "poster": row[3],
            "imdb_url": row[4],
        }
        for row in movies
    ]


def add_movie(user_name, title, year, rating, poster, imdb_url):
    """
    Adds a movie for the given user.
    Creates the user automatically if the user does not exist.
    """

    with engine.connect() as connection:
        try:
            # Check if user already exists
            result = connection.execute(
                text("""
                    SELECT id
                    FROM users
                    WHERE name = :name
                """),
                {"name": user_name}
            )
            user = result.fetchone()

            # Create user if not exists
            if user is None:
                connection.execute(
                    text("""
                        INSERT INTO users (name)
                        VALUES (:name)
                    """),
                    {"name": user_name}
                )
                connection.commit()

                # Get newly created user id
                result = connection.execute(
                    text("""
                        SELECT id
                        FROM users
                        WHERE name = :name
                    """),
                    {"name": user_name}
                )
                user = result.fetchone()

            user_id = user[0]

            # Insert movie
            connection.execute(
                text("""
                    INSERT INTO movies (
                        user_id,
                        title,
                        year,
                        rating,
                        poster,
                        imdb_url
                    )
                    VALUES (
                        :user_id,
                        :title,
                        :year,
                        :rating,
                        :poster,
                        :imdb_url
                    )
                """),
                {
                    "user_id": user_id,
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster": poster,
                    "imdb_url": imdb_url,
                }
            )
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


def run_test():

    user_name = input("\nEnter a new user name: ")
    if add_user(user_name):
        print("User successfully added!")
    else:
        print(f"User '{user_name}' already exists!")

    if not movie_exists(user_name, "Inception"):
        add_movie(user_name, "Inception", 2010, 8.8,
              "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_QL75_UX380_CR0,0,380,562_.jpg",
              'https://www.imdb.com/title/tt1375666')
        print("Movie 'Inception' successfully added!")
    else:
        print(f"Movie 'Inception' already exists!")

    # Test listing movies
    movies = list_movies(user_name)
    for movie in movies:
        print(movie)

    # Test updating a movie's rating
#    update_movie("Inception", 9.0)
#    print(list_movies("Holger"))

    # Test deleting a movie
#    delete_movie("Inception")
#    print(list_movies())  # Should be empty if it was the only movie


def main():
    run_test()


if __name__ == "__main__":
    main()
