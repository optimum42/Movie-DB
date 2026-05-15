import statistics # for median calculation
from datetime import datetime # for current year
import random # for random movie pick
import matplotlib.pyplot # for histogram
import Levenshtein # for Fuzzy Matching
from movie_storage import movie_storage_sql
from api import omdb_api
from helpers import display_formats
import website
from movie_storage.movie_storage_sql import add_user
from data import blockbusters

EXPORT_DIR = 'data/exports/'


def get_movie_name():
    """
    this function prompts the user to enter a movie name
    and validates it against the min amount of characters
    :return: movie name
    """
    min_chars = 3
    while True:
        movie_name = input('\nEnter movie name: ')
        if len(movie_name.strip()) < min_chars :
            display_formats.cprint(f"Please enter at least {min_chars} characters", "red")
        else:
            return movie_name


def get_movie_year():
    """
    this function prompts the user to enter a movie year
    """
    min_year = 1888
    current_year = datetime.now().year
    year = 0
    while not min_year <= year <= current_year:
        try:
            year = int(input(f"Enter Movie Year ({min_year}-{current_year}): "))
        except ValueError:
            display_formats.cprint("Invalid input!", "red")
    return year


def show_movies(movies):
    """
    this function prints the movie details
    :param movies: list of movie details
    """
    display_formats.cprint(f"\n{len(movies)} movies found:", "cyan")
    for movie in movies:
        print(f"{movie['title']}", end="")
        display_formats.cprint(f" ({movie['year']})", "blue", end="")
        print(": ", end="")
        display_formats.cprint(f"{round(movie['rating'], 1)}", "cyan")
        display_formats.cprint(f"  Poster: {movie['poster']}", "blue")
        display_formats.cprint(f"  IMDb: {movie['imdb_url']}", "blue")
        notes = movie['notes']
        if notes is not None:
            display_formats.cprint(f"  Notes: {notes}", "magenta")
        print()


def list_movies(user_name):
    """
    this function shows all the movies in the database ordered by title
    """
    movies = movie_storage_sql.list_movies(user_name)
    if len(movies) > 0:
        movies.sort(key=lambda movie: movie['title'])
        show_movies(movies)
    else:
        display_formats.cprint("No movies found!", "red")


def add_movie(user_name):
    """
    this function fetches the movie details from the omdb api and
    adds the new movie to the database
    """
    movie_name = get_movie_name()
    if movie_storage_sql.movie_exists(movie_name, user_name):
        display_formats.cprint(f"Movie '{movie_name}' already exists!", "red")
    else:
        movie = omdb_api.fetch_movie(movie_name)
        if movie is None:
            display_formats.cprint('No movie information found!', 'red')
            return

        title = movie['Title']
        year = movie.get('Year')
        rating = movie.get('imdbRating')
        poster = movie.get('Poster')
        imdb_url = omdb_api.get_imdb_url(title)

        movie_storage_sql.add_movie(user_name, title, year, rating, poster, imdb_url)
        display_formats.cprint(f"Movie '{title}' added successfully.", "green")


def delete_movie(user_name):
    """
    this function deletes a movie from the database
    """
    movie_name = get_movie_name()
    if movie_storage_sql.movie_exists(movie_name, user_name):
        movie_storage_sql.delete_movie(user_name, movie_name)
        display_formats.cprint(f"Movie '{movie_name}' deleted successfully.", "green")
    else:
        display_formats.cprint(f"Movie '{movie_name}' doesn't exist!", "red")


def update_movie(user_name):
    """
    this function updates a movie rating in the database
    """
    movie_name = get_movie_name()
    if movie_storage_sql.movie_exists(movie_name, user_name):
        notes = input('Enter your notes: ')
        movie_storage_sql.update_movie(movie_name, notes)
        display_formats.cprint(f"Movie '{movie_name}' updated successfully.", "green")
    else:
        display_formats.cprint(f"Movie '{movie_name}' doesn't exist!", "red")


def show_stats(user_name):
    """
    this function prints statistics about the database for the given user
    """
    movies = movie_storage_sql.list_movies(user_name)
    ratings = [movie['rating'] for movie in movies]
    display_formats.cprint(f"\n{len(movies)} movies in total", "cyan")
    display_formats.cprint(f"Average rating: {round(sum(ratings)/len(ratings), 1)}")
    display_formats.cprint(f"Median rating: {round(statistics.median(ratings), 1)}")

    # show best and worst rated movies
    best_rating = round(max(ratings), 1)
    worst_rating = round(min(ratings), 1)
    for movie in movies:
        if movie['rating'] == best_rating:
            display_formats.cprint(f"Best movie: {movie['title']}: {best_rating}", "green")
    for movie in movies:
        if movie['rating'] == worst_rating:
            display_formats.cprint(f"Worst movie: {movie['title']}: {worst_rating}", "red")


def show_random_movie(user_name):
    """
    this function shows a random movie from the database for the given user
    """
    movies = movie_storage_sql.list_movies(user_name)
    movie = random.choice(movies)
    display_formats.cprint(f"\nYour movie for tonight: {movie['title']}, it's rated {movie['rating']}",
           "magenta")


def search_movie(user_name):
    """
    this function searches for a movie in the database
    if no movie name or search phrase is found move on with
    fuzzy search
    :return:
    """
    movies = movie_storage_sql.list_movies(user_name)
    search_phrase = get_movie_name().lower()
    movies_found = [movie for movie in movies if search_phrase in movie['title'].lower()]
    if len(movies_found) > 0:
        show_movies(movies_found)
    else:
        # else try fuzzy searching
        display_formats.cprint(f"No movie with '{search_phrase}' found.", "red")
        fuzzy_search_movie(movies, search_phrase)


def fuzzy_search_movie(movies, search_phrase):
    """
    this function searches for a movie with Levenshtein distance
    (fuzzy matching)
    It calculates the minimum number of insertions, deletions, and substitutions
    required to change the search phrase into the movie title
    """
    fuzzy_match = False
    fuzzy_matches = []
    for movie in movies:
        title = movie['title'].lower()
        # try with the entire title
        max_dist = 5 # maximum number of insertions/deletions/substitutions
        if Levenshtein.distance(search_phrase, title) <= max_dist:
            if movie not in fuzzy_matches:
                fuzzy_matches.append(movie)
                fuzzy_match = True
        # try with title split in parts
        title_parts = title.split()
        max_dist = 3 # narrow it down for single words
        for title_part in title_parts:
            if Levenshtein.distance(search_phrase, title_part) <= max_dist:
                if movie not in fuzzy_matches:
                    fuzzy_matches.append(movie)
                    fuzzy_match = True
    if fuzzy_match:
        display_formats.cprint("Did you mean:", "red", end="")
        show_movies(fuzzy_matches)
    else:
        display_formats.cprint("Please try another search phrase.", "red")


def show_movies_by_rating(user_name):
    """
    this function shows the movies ordered by their ratings
    """
    movies = movie_storage_sql.list_movies(user_name)
    sorted_movies = sorted(movies, key=lambda x: x['rating'], reverse=True)
    show_movies(sorted_movies)


def rating_histogram(user_name):
    """
    this function creates and stores a histogram of the ratings as png
    """
    movies = movie_storage_sql.list_movies(user_name)
    ratings = [movie['rating'] for movie in movies]
    matplotlib.pyplot.hist(ratings)
    filename = input('\nEnter file name: ')
    # remove file extension if present and add '.png'
    if filename == '':
        filename = 'movie_histogram.png'
    elif '.png' not in filename:
        filename += '.png'
    filename = EXPORT_DIR + filename
    matplotlib.pyplot.savefig(filename)
    display_formats.cprint(f"Histogram successfully saved in {filename}", "green")


def generate_website(user_name):
    """ exports movie database to a local website """
    website.export_movies_to_html(user_name)
    print("Website was generated successfully.")


def show_menu_and_run_choice(user_name):
    """
    this function prints the menu on the screen,
    gets the user's choice and calls the related function accordingly
    if the choice is invalid, this functions calls itself again
    """
    # the menu dict also holds the function pointers for a good maintenance
    menu_dispatcher = {
        0: ('Exit', quit_program),
        1: ('List movies', list_movies),
        2: ('Add movie', add_movie),
        3: ('Delete movie', delete_movie),
        4: ('Update movie', update_movie),
        5: ('Stats', show_stats),
        6: ('Random movie', show_random_movie),
        7: ('Search movie', search_movie),
        8: ('Movies sorted by rating', show_movies_by_rating),
        9: ('Rating-Histogram', rating_histogram),
        10: ('Generate Website', generate_website),
        11: ('Fill with 100 Blockbusters', init_movie_db),
        12: ('Show movie details', movie_details),
    }

    while True:
        # print the menu...
        display_formats.cprint('\nMenu:', 'magenta')
        for num, menu_item in menu_dispatcher.items():
            print(f"{num}. {menu_item[0]}")

        # ... and call the function according to the user's choice
        display_formats.cprint("\nYour choice (0-10): ", "blue", end="")
        try:
            choice = int(input())
            if choice in menu_dispatcher:
                menu_dispatcher[choice][1](user_name) # run the function
                return
        except ValueError:
            pass # input is invalid, no extra handling necessary
        display_formats.cprint('Invalid choice', 'red')


def quit_program(user_name):
    """
    this function closes the program
    """
    print(f"Bye {user_name}!")
    quit()


def add_user():
    while True:
        user_name = input("\nEnter new user: ")
        if movie_storage_sql.add_user(user_name):
            return user_name
        display_formats.cprint('Invalid username', 'red')


def select_user():
    """
    selects a user from the users table of the movie database
    """
    users = list(movie_storage_sql.get_users().values())
    while True:
        user_count = 1
        display_formats.cprint('0: New user', 'magenta')
        for user in users:
            print(f"{user_count}. {user}")
            user_count += 1
        try:
            choice = int(input('\nSelect current user: '))
            if 1 <= choice <= len(users):
                return users[choice - 1]
            elif choice == 0:
                new_user = add_user()
                return new_user
        except ValueError:
            pass
        display_formats.cprint('Invalid choice', 'red')


def init_movie_db(user_name):
    """ fills the movie database with Blockbusters """
    for movie_name in blockbusters.TOP_MOVIES:
        if movie_storage_sql.movie_exists(movie_name, user_name):
            display_formats.cprint(f"Movie '{movie_name}' already exists!",
                                   "red")
        else:
            movie = omdb_api.fetch_movie(movie_name)
            if movie is None:
                display_formats.cprint('No movie information found!', 'red')
                return

            title = movie['Title']
            year = movie.get('Year')
            rating = movie.get('imdbRating')
            poster = movie.get('Poster')
            imdb_url = omdb_api.get_imdb_url(title)
            notes = movie.get('Awards')
            movie_storage_sql.add_movie(user_name, title, year, rating, poster,imdb_url)
            movie_storage_sql.update_movie(title, notes)
            display_formats.cprint(f"Movie '{title}' added successfully.","green")


def movie_details(user_name=None):
    """
    fetches movie details from the omdb api and displays it
    """
    title = get_movie_name()
    res = omdb_api.fetch_movie(title)
    for key, val in res.items():
        if type(val) == list:
            print(f"{key}:")
            for item in val:
                for k, v in item.items():
                    print(f"  {k}: {v}")
        else:
            print(f"{key}: {val}")


def main():
    """
    the main function loops through the user's choice
    until the user enters '0' to quit the program
    """
    welcome = "Welcome to your personal Movie Database"
    stars = '*' * len(welcome)
    display_formats.cprint(f"{stars}\n{welcome}\n{stars}", "cyan")
    user_name = select_user()

    stars = 10 * '*'
    display_formats.cprint(f"{stars} My Movies Database for {user_name} {stars}", "magenta")
    while True:
        show_menu_and_run_choice(user_name)
        display_formats.cprint("\nPress enter to continue ", "blue", end="")
        input()


if __name__ == "__main__":
    main()
