import requests
from datetime import datetime
from collections import Counter
import json
from dotenv import load_dotenv
import os

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align


load_dotenv()

# Trakt API configuration
TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
TRAKT_API_BASE_URL = 'https://api.trakt.tv'
TRAKT_HEADERS = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': TRAKT_CLIENT_ID
}

# TMDB API configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_BASE_URL = 'https://api.themoviedb.org/3'

year=os.getenv('YEAR')

def fetch_trakt_history(username, start_date, end_date):
    url = f"{TRAKT_API_BASE_URL}/users/{username}/history"
    params = {
        'start_at': start_date.isoformat(),
        'end_at': end_date.isoformat(),
        'limit': 10000  # Adjust as needed
    }
    response = requests.get(url, headers=TRAKT_HEADERS, params=params)
    return response.json()

def get_tmdb_movie_details(tmdb_id):
    url = f"{TMDB_API_BASE_URL}/movie/{tmdb_id}"
    params = {'api_key': TMDB_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    return data.get('runtime', 0), data.get('genres', [])

def get_tmdb_episode_details(show_tmdb_id, season_number, episode_number):
    url = f"{TMDB_API_BASE_URL}/tv/{show_tmdb_id}/season/{season_number}/episode/{episode_number}"
    params = {'api_key': TMDB_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    show_details_url = f"{TMDB_API_BASE_URL}/tv/{show_tmdb_id}"
    params = {'api_key': TMDB_API_KEY}
    show_detail_response = requests.get(show_details_url, params=params)
    show_detail_data = show_detail_response.json()

    return data.get('runtime', 0), show_detail_data.get('genres', [])

def analyze_history(history):
    tv_episodes = 0
    tv_minutes = 0
    tv_genres = Counter()
    movies = 0
    movie_minutes = 0
    movie_genres = Counter()

    for item in history:
        if item['type'] == 'episode':
            tv_episodes += 1
            show_tmdb_id = item['show'].get('ids', {}).get('tmdb')
            season_number = item['episode']['season']
            episode_number = item['episode']['number']
            if show_tmdb_id:
                runtime, genres = get_tmdb_episode_details(show_tmdb_id, season_number, episode_number)
                try:
                    tv_minutes += runtime
                except TypeError:
                     runtime = 30
            genre_list = [item['name'] for item in genres]
            tv_genres.update(genre_list)
        elif item['type'] == 'movie':
            movies += 1
            tmdb_id = item['movie'].get('ids', {}).get('tmdb')
            if tmdb_id:
                runtime, genres = get_tmdb_movie_details(tmdb_id)
                try:
                    movie_minutes += runtime
                except TypeError:
                     runtime = 90
            genre_list = [item['name'] for item in genres]
            movie_genres.update(genre_list)

    return {
        'tv_episodes': tv_episodes,
        'tv_hours': round(tv_minutes / 60, 2),
        'top_tv_genres': tv_genres.most_common(5),
        'movies': movies,
        'movie_hours': round(movie_minutes / 60, 2),
        'top_movie_genres': movie_genres.most_common(5)
    }

# Set the date range for 2024
start_date = datetime(int(year), 1, 1)
end_date = datetime(int(year), 12, 31)

# Fetch and analyze the history
username = 'navilg0409'
print('Generating Year in Review for', year+'...')
print("\n")
history = fetch_trakt_history(username, start_date, end_date)
with open("trakt-history-"+year+".json", "w") as file:
    file.write(json.dumps(history, indent=4))
stats = analyze_history(history)

# Print the results in a structured format
print({
    "username": username,
    "year": 2024,
    "statistics": {
        "tv_shows": {
            "episodes_watched": stats['tv_episodes'],
            "hours_watched": stats['tv_hours'],
            "top_genres": [genre for genre, count in stats['top_tv_genres']]
        },
        "movies": {
            "movies_watched": stats['movies'],
            "hours_watched": stats['movie_hours'],
            "top_genres": [genre for genre, count in stats['top_movie_genres']]
        }
    }
})

print(stats)

year_in_review_stats = {
    "username": username,
    "year": 2024,
    "statistics": {
        "tv_shows": {
            "episodes_watched": stats['tv_episodes'],
            "hours_watched": stats['tv_hours'],
            "top_genres": [genre for genre, count in stats['top_tv_genres']]
        },
        "movies": {
            "movies_watched": stats['movies'],
            "hours_watched": stats['movie_hours'],
            "top_genres": [genre for genre, count in stats['top_movie_genres']]
        }
    }
}

with open("year-in-review-"+str(year)+".json", "w") as file:
    file.write(json.dumps(year_in_review_stats, indent=4))

# Initialize Console
console = Console()

# Heading
heading = Align.center("[bold magenta]Year in Review "+year+"[/bold magenta]", vertical="middle")

# Four Cards
cards_table = Table.grid(expand=True)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)

cards_table.add_row(
    Panel("Movies Watched\n\n[bold cyan]"+str(stats['movies'])+"[/bold cyan]", border_style="cyan"),
    Panel("Movies Hours\n\n[bold green]"+str(stats['movie_hours'])+"[/bold green]", border_style="green"),
    Panel("TV Episodes Watched\n\n[bold cyan]"+str(stats['tv_episodes'])+"[/bold cyan]", border_style="cyan"),
    Panel("TV Episodes Hours\n\n[bold green]"+str(stats['tv_hours'])+"[/bold green]", border_style="green"),
)


# Function to create genre rows
def create_genre_row(genres, color):
    genre_row = Table.grid(expand=True)
    for genre in genres:
        genre_row.add_column(justify="center", ratio=1)
    genre_row.add_row(*[Panel(f"[bold {color}]{genre}[/bold {color}]", border_style=color, padding=(0, 2)) for genre in genres])
    return genre_row

# Top 5 Movie Genres Section
movie_genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller"]
movie_genres_row = create_genre_row([genre for genre, count in stats['top_movie_genres']], "bold cyan")

movie_genres_section = Panel(
    movie_genres_row,
    title="Top 5 Movie Genres",
    border_style="cyan",
    padding=1,
)

# Top 5 TV Show Genres Section
tv_genres = ["Drama", "Fantasy", "Reality", "Mystery", "Animation"]
tv_genres_row = create_genre_row([genre for genre, count in stats['top_tv_genres']], "bold green")

tv_genres_section = Panel(
    tv_genres_row,
    title="Top 5 TV Show Genres",
    border_style="green",
    padding=1,
)

# Layout
layout = Layout()
layout.split_column(
    Layout(heading, size=3),
    Layout(cards_table, size=5),
    Layout("\n\n", size=2),
    Layout(movie_genres_section, size=8),
    Layout("\n\n", size=2),
    Layout(tv_genres_section, size=8),
)

# Print Layout
console.print(layout)

