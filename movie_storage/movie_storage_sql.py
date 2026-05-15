from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Define the database URL
DB_URL = "sqlite:///data/movies.db"  # when called from movie_db.py

if __name__ == "__main__":
    DB_URL = "sqlite:///../data/movies.db"  # when called from this file

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create tables if they do not exist
with engine.connect() as connection:
    # Users table
    connection.execute(text("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE NOT NULL
                            )
                            """))

    # Create the movies table if it does not exist
    connection.execute(text("""
                            CREATE TABLE IF NOT EXISTS movies
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                title TEXT NOT NULL,
                                year INTEGER NOT NULL,
                                rating REAL NOT NULL,
                                poster TEXT NOT NULL,
                                imdb_url TEXT NOT NULL,
                                notes TEXT
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
    :return: True if it is in the database, False otherwise:
    """
    sql = """
          SELECT id
          FROM users
          WHERE name = :name
          """
    params = {"name": user_name}
    users = db_execute(sql, params)
    return len(users) == 1


def movie_exists(movie_name, user_name):
    """
    Checks if a movie for a specified user is in the database.
    :return: True if it is in the database, False otherwise
    """
    sql = """ SELECT movies.id
              FROM movies
              JOIN users
                ON movies.user_id = users.id
              WHERE users.name = :user_name
              AND movies.title = :title
          """
    params = {"title": movie_name, "user_name": user_name}
    rows = db_execute(sql, params)
    return len(rows) >= 1


def get_users():
    """
    Retrieve all users from the database.
    :return: dict {user_id: user_name}
    """
    sql = "SELECT id, name FROM users ORDER BY  id"
    users = db_execute(sql)
    return {user[0]: user[1] for user in users}


def get_user_id(user_name):
    """
    Retrieves the user_id from the database by user_name.
    """
    sql = "SELECT id FROM users WHERE name = :name"
    params = {"name": user_name}
    rows = db_execute(sql, params)
    return rows[0][0]


def add_user(user_name):
    """
    Adds a new user to the database.
    :return:
        True  -> user created
        False -> user already exists
    """
    if not user_exists(user_name):
        sql = """
              INSERT INTO users (name)
              VALUES (:name)
              """
        params = {"name": user_name}
        db_execute(sql, params)
        return True
    return False


def delete_user(user_name):
    """
    Deletes a user and its movies from the database.
    """
    delete_user_movies(user_name)
    sql = """
          DELETE FROM users 
          WHERE name = :user_name
          """
    params = {"user_name": user_name}
    res = db_execute(sql, params)
    return res['rowcount'] > 0


def delete_user_movies(user_name):
    """
    Deletes a movies from the database for the given user.
    """
    sql = """
            DELETE FROM movies
            WHERE user_id = (
                SELECT id
                FROM users
                WHERE name = :user_name
            )
          """
    params = {"user_name": user_name}
    res = db_execute(sql, params)
    return res['rowcount'] > 0


def list_movies(user_name=None):
    """
    Returns movies from the database as list of dicts
    If user_name is provided: return only movies for that user.
    If user_name is None: return all movies.
    """
    # All movies
    if user_name is None:
        sql = """
                SELECT
                    users.name,
                    movies.title,
                    movies.year,
                    movies.rating,
                    movies.poster,
                    movies.imdb_url,
                    movies.notes
                FROM movies
                JOIN users
                  ON movies.user_id = users.id
                ORDER BY movies.title 
                """
        params = None
    # Movies for specific user
    else:
        sql = """
              SELECT users.name,
                     movies.title,
                     movies.year,
                     movies.rating,
                     movies.poster,
                     movies.imdb_url,
                     movies.notes
              FROM movies
              JOIN users
                ON movies.user_id = users.id
              WHERE users.name = :user_name
              ORDER BY movies.title
              """
        params = {"user_name": user_name}

    movies = db_execute(sql, params)
    return [
        {
            "user": row[0],
            "title": row[1],
            "year": row[2],
            "rating": row[3],
            "poster": row[4],
            "imdb_url": row[5],
            "notes": row[6],
        }
        for row in movies
    ]


def add_movie(user_name, title, year, rating, poster, imdb_url):
    """
    Adds a movie for the given user.
    Creates the user automatically if the user does not exist.
    """
    user_id = get_user_id(user_name)
    sql = """
          INSERT INTO movies (user_id,
                              title,
                              year,
                              rating,
                              poster,
                              imdb_url)
          VALUES (:user_id,
                  :title,
                  :year,
                  :rating,
                  :poster,
                  :imdb_url)
          """
    params = {
        "user_id": user_id,
        "title": title,
        "year": year,
        "rating": rating,
        "poster": poster,
        "imdb_url": imdb_url,
    }
    ret = db_execute(sql, params)
    assert ret['success']


def delete_movie(user_name, title):
    """ Deletes a movie from the database for the given user. """
    sql = """
          DELETE
          FROM movies              
          WHERE title = :title
          AND user_id = (
            SELECT id
            FROM users
            WHERE name = :user_name
          )
          """
    params = {"title": title, "user_name": user_name}
    db_execute(sql, params)


def update_movie(title, notes):
    """Update a movie's rating in the database."""
    sql = """
          UPDATE movies
          SET notes = :notes
          WHERE title = :title
          """

    params = {"notes": notes, "title": title}
    db_execute(sql, params)


def run_test():
    print(get_users())
    user_name = input("\nEnter a user name: ")
    if add_user(user_name):
        print("User successfully added!")
    else:
        print(f"User '{user_name}' already exists!")

    if not movie_exists("Inception", user_name):
        add_movie(user_name, "Inception", 2010, 8.8,
                  "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_QL75_UX380_CR0,0,380,562_.jpg",
                  'https://www.imdb.com/title/tt1375666')
        print("Movie 'Inception' successfully added!")
    else:
        print(f"Movie 'Inception' already exists!")

    # Test listing movies
    print(f"Movies of {user_name}")
    movies = list_movies(user_name)
    for movie in movies:
        print(movie)

    # List all movies
    print("All Movies")
    movies = list_movies()
    for movie in movies:
        print(movie)


def main():
    run_test()

    list_movies()
    if delete_user(input("\nUser to delete: ")):
        print("User successfully deleted!")
    else:
        print("User does not exist!")


if __name__ == "__main__":
    main()
