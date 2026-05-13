import statistics # for median calculation
from datetime import datetime # for current year
import random # for random movie pick
import matplotlib.pyplot # for histogram
# note: in codio terminal we need to install the Levenshtein module first:
# "python3 -m pip install Levenshtein"
import Levenshtein # for Fuzzy Matching
from movie_storage import movie_storage_json
from movie_storage import movie_storage_sql
from api import omdb_api

EXPORT_DIR = 'data/exports/'


def cprint(text, color_str=None, end="\n"):
    """
    this function works like 'print' but with color
    """
    color_reset_code = '\033[0m'
    text_colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m'
    }
    color_code = text_colors.get(color_str, "")
    print(color_code + text + color_reset_code, end=end)


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
            cprint(f"Please enter at least {min_chars} characters", "red")
        else:
            return movie_name


def get_movie_rating():
    """
    this function prompts the user to enter a movie rating
    :return movie rating as float
    """
    try:
        rating = float(input('Enter new movie rating (0-10): '))
        if rating < 0 or rating > 10:
            raise ValueError
        return rating
    except ValueError:
        cprint("Invalid input!", "red")
        return get_movie_rating()


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
            cprint("Invalid input!", "red")
    return year


def show_movies(movies):
    """
    this function prints the movie details
    :param movies: list of movie details
    """
    cprint(f"\n{len(movies)} movies found:", "cyan")
    for movie in movies:
        print(f"{movie['title']}", end="")
        cprint(f" ({movie['year']})", "blue", end="")
        print(": ", end="")
        cprint(f"{round(movie['rating'], 1)}", "cyan", end="")
        cprint(f"  Poster: {movie['poster']}", "blue")


def show_all_movies():
    """
    this function shows all the movies in the database ordered by title
    """
    movies = movie_storage_sql.list_movies()
    if len(movies) > 0:
        movies.sort(key=lambda movie: movie['title'])
        show_movies(movies)
    else:
        cprint("No movies found!", "red")


def add_movie():
    """
    this function adds a new movie to the database
    """
    movie_name = get_movie_name()
    if movie_storage_sql.movie_exists(movie_name):
        cprint(f"Movie '{movie_name}' already exists!", "red")
    else:
        movie = omdb_api.get_movie(movie_name)
        title = movie['Title']
        year = movie.get('Year')
        rating = movie.get('imdbRating')
        poster = movie.get('Poster')

        movie_storage_sql.add_movie(title, year, rating, poster)
        cprint(f"Movie '{title}' added successfully.", "green")


def delete_movie():
    """
    this function deletes a movie from the database
    """
    movie_name = get_movie_name()
    if movie_storage_sql.movie_exists(movie_name):
        movie_storage_sql.delete_movie(movie_name)
        cprint(f"Movie '{movie_name}' deleted successfully.", "green")
    else:
        cprint(f"Movie '{movie_name}' doesn't exist!", "red")


def update_movie():
    """
    this function updates a movie rating in the database
    """
    movie_name = get_movie_name()
    if movie_storage_sql.movie_exists(movie_name):
        rating = get_movie_rating()
        movie_storage_sql.update_movie(movie_name, rating)
        cprint(f"Movie '{movie_name}' updated successfully.", "green")
    else:
        cprint(f"Movie '{movie_name}' doesn't exist!", "red")


def show_stats():
    """
    this function prints statistics about the database
    """
    movies = movie_storage_sql.list_movies()
    ratings = [movie['rating'] for movie in movies]
    cprint(f"\n{len(movies)} movies in total", "cyan")
    cprint(f"Average rating: {round(sum(ratings)/len(ratings), 1)}")
    cprint(f"Median rating: {round(statistics.median(ratings), 1)}")

    # show best and worst rated movies
    best_rating = round(max(ratings), 1)
    worst_rating = round(min(ratings), 1)
    for movie in movies:
        if movie['rating'] == best_rating:
            cprint(f"Best movie: {movie['title']}: {best_rating}", "green")
    for movie in movies:
        if movie['rating'] == worst_rating:
            cprint(f"Worst movie: {movie['title']}: {worst_rating}", "red")


def show_random_movie():
    """
    this function shows a random movie from the database
    """
    movies = movie_storage_sql.list_movies()
    movie = random.choice(movies)
    cprint(f"\nYour movie for tonight: {movie['title']}, it's rated {movie['rating']}",
           "magenta")


def search_movie():
    """
    this function searches for a movie in the database
    if no movie name or search phrase is found move on with
    fuzzy search
    :return:
    """
    movies = movie_storage_sql.list_movies()
    search_phrase = get_movie_name().lower()
    movies_found = [movie for movie in movies if search_phrase in movie['title'].lower()]
    if len(movies_found) > 0:
        show_movies(movies_found)
    else:
        # else try fuzzy searching
        cprint(f"No movie with '{search_phrase}' found.", "red")
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
        cprint("Did you mean:", "red", end="")
        show_movies(fuzzy_matches)
    else:
        cprint("Please try another search phrase.", "red")


def show_movies_by_rating():
    """
    this function shows the movies ordered by their ratings
    """
    movies = movie_storage_sql.list_movies()
    sorted_movies = sorted(movies, key=lambda x: x['rating'], reverse=True)
    show_movies(sorted_movies)


def rating_histogram():
    """
    this function creates and stores a histogram of the ratings as png
    """
    movies = movie_storage_sql.list_movies()
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
    cprint(f"Histogram successfully saved in {filename}", "green")


def show_menu_and_run_choice():
    """
    this function prints the menu on the screen,
    gets the user's choice and calls the related function accordingly
    if the choice is invalid, this functions calls itself again
    """
    # the menu dict also holds the function pointers for a good maintenance
    menu_dispatcher = {
        0: ('Exit', quit_program),
        1: ('List movies', show_all_movies),
        2: ('Add movie', add_movie),
        3: ('Delete movie', delete_movie),
        4: ('Update movie', update_movie),
        5: ('Stats', show_stats),
        6: ('Random movie', show_random_movie),
        7: ('Search movie', search_movie),
        8: ('Movies sorted by rating', show_movies_by_rating),
        9: ('Rating-Histogram', rating_histogram),
    }

    # print the menu...
    cprint('\nMenu:', 'magenta')
    for num, menu_item in menu_dispatcher.items():
        print(f"{num}. {menu_item[0]}")

    # ... and call the function according to the user's choice
    cprint("\nYour choice (0-9): ", "blue", end="")
    try:
        choice = int(input())
        if choice in menu_dispatcher:
            menu_dispatcher[choice][1]() # run the function
            return
    except ValueError:
        pass # input is invalid, no extra handling necessary
    cprint('Invalid choice', 'red')
    show_menu_and_run_choice()


def quit_program():
    """
    this function closes the program
    """
    print('Bye!')
    quit()


def main():
    """
    the main function loops through the user's choice
    until the user enters '0' to quit the program
    """
    stars = 10 * '*'
    cprint(f"{stars} My Movies Database {stars}", "magenta")
    while True:
        show_menu_and_run_choice()
        cprint("\nPress enter to continue ", "blue", end="")
        input()


if __name__ == "__main__":
    main()
