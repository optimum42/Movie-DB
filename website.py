from pathlib import Path
from movie_storage import movie_storage_sql

WEBSITE_TITLE = "Movie Heroes Database"
HTML_TEMPLATE_FILE = "templates/index_template.html"
HTML_OUTPUT_FILE = "data/exports/index.html"


def load_html(file_path):
    """Loads an HTML file."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File does not exist: {file_path}")
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_html(html, file_path):
  """ Writes an HTML file """
  with open(file_path, "w") as handle:
      handle.write(html)


def serialize_movie(movie):
    """ serializes the movie data to a string and returns it """
    ret = ""
    ret += "<li>\n"
    ret += ("<div class='movie'>\n")
    ret += "<img class='movie-poster'\n"
    ret += f" src='{movie.get('poster')}'\n"
    ret += f" title=''/>\n"
    ret += f"<div class='movie-title'>{movie.get('title')}</div>\n"
    ret += f"<div class='movie-year'>{movie.get('year')}</div>\n"
    ret += f"</div>\n"
    ret += "</li>\n"
    return ret


def movies_to_html(movies):
    """ writes all the movies to a string and returns it """
    output = ""
    assert len(movies) > 0
    for movie in movies:
        output += serialize_movie(movie)
    return output


def export_movies_to_html():
    """ exports all the movies to a local website using a template"""
    html_template = load_html(HTML_TEMPLATE_FILE)
    if html_template is not None:
        html_output = html_template.replace("__TEMPLATE_TITLE__", WEBSITE_TITLE)
        movies = movie_storage_sql.list_movies()
        movies_html = movies_to_html(movies)
        html_output = html_output.replace("__TEMPLATE_MOVIE_GRID__", movies_html)
        write_html(html_output, HTML_OUTPUT_FILE)


if __name__ == "__main__":
    export_movies_to_html()
