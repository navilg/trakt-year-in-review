import requests
from datetime import datetime
from time import sleep
from collections import Counter
import json
from dotenv import load_dotenv
import os
import sys

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align

if len(sys.argv) != 3:
    load_dotenv()
else:
    os.environ['TRAKT_USER'] = sys.argv[1]
    os.environ['YEAR'] = sys.argv[2]
    os.environ['TRAKT_CLIENT_ID'] = sys.argv[3]

# Trakt API configuration
TRAKT_CLIENT_ID = os.getenv('TRAKT_CLIENT_ID')
TRAKT_API_BASE_URL = 'https://api.trakt.tv'
TRAKT_HEADERS = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': TRAKT_CLIENT_ID
}

username = os.getenv('TRAKT_USER')

year=os.getenv('YEAR')

def fetch_trakt_history(username, start_date, end_date):
    url = f"{TRAKT_API_BASE_URL}/users/{username}/history"
    params = {
        'start_at': start_date.isoformat(),
        'end_at': end_date.isoformat(),
        'limit': 10000  # Adjust as needed
    }
    response = requests.get(url, headers=TRAKT_HEADERS, params=params)
    
    if response.status_code == 401:
        print("Status Code 401: Unauthorized - OAuth must be provided or profile must be public")
        exit(401)
    if response.status_code == 403:
        print("Status Code 403: Forbidden - invalid API key or unapproved app")
        exit(403)
    if response.status_code == 420:
        print("Status Code 420: Account Limit Exceeded")
        exit(420)
    if response.status_code == 426:
        print("Status Code 426: VIP Only - user must upgrade to VIP")
        exit(426)
    if response.status_code == 429:
        print("Status Code 429: Rate Limit Exceeded")
        exit(426)
    if 500 <= response.status_code < 600:
        print("Status Code", response.status_code+": Service Unavailable")
        exit(response.status_code)
    if response.status_code == 200:
        return response.json()

def get_movie_details(id):
    url = f"{TRAKT_API_BASE_URL}/movies/{id}"
    params = {'extended': 'full'}
    response = requests.get(url, headers=TRAKT_HEADERS, params=params)
    if response.status_code == 401:
        print("Status Code 401: Unauthorized - OAuth must be provided or profile must be public")
        exit(401)
    if response.status_code == 403:
        print("Status Code 403: Forbidden - invalid API key or unapproved app")
        exit(403)
    if response.status_code == 420:
        print("Status Code 420: Account Limit Exceeded")
        exit(420)
    if response.status_code == 426:
        print("Status Code 426: VIP Only - user must upgrade to VIP")
        exit(426)
    if response.status_code == 429:
        print("Status Code 429: Rate Limit Exceeded")
        exit(426)
    if 500 <= response.status_code < 600:
        print("Status Code", response.status_code+": Service Unavailable")
        exit(response.status_code)
    if response.status_code == 200:
        data = response.json()

    return data.get('runtime', 0), data.get('genres', []), data.get('rating', 0)

def get_episode_details(show_id, season_number, episode_number):
    url = f"{TRAKT_API_BASE_URL}/shows/{show_id}/seasons/{season_number}/episodes/{episode_number}"
    params = {'extended': 'full'}
    response = requests.get(url, headers=TRAKT_HEADERS, params=params)

    if response.status_code == 401:
        print("Status Code 401: Unauthorized - OAuth must be provided or profile must be public")
        exit(401)
    if response.status_code == 403:
        print("Status Code 403: Forbidden - invalid API key or unapproved app")
        exit(403)
    if response.status_code == 420:
        print("Status Code 420: Account Limit Exceeded")
        exit(420)
    if response.status_code == 426:
        print("Status Code 426: VIP Only - user must upgrade to VIP")
        exit(426)
    if response.status_code == 429:
        print("Status Code 429: Rate Limit Exceeded")
        exit(426)
    if 500 <= response.status_code < 600:
        print("Status Code", response.status_code+": Service Unavailable")
        exit(response.status_code)
    if response.status_code == 200:
        data = response.json()

    show_details_url = f"{TRAKT_API_BASE_URL}/shows/{show_id}"
    params = {'extended': 'full'}
    show_detail_response = requests.get(show_details_url, headers=TRAKT_HEADERS, params=params)

    if show_detail_response.status_code == 401:
        print("Status Code 401: Unauthorized - OAuth must be provided or profile must be public")
        exit(401)
    if show_detail_response.status_code == 403:
        print("Status Code 403: Forbidden - invalid API key or unapproved app")
        exit(403)
    if show_detail_response.status_code == 420:
        print("Status Code 420: Account Limit Exceeded")
        exit(420)
    if show_detail_response.status_code == 426:
        print("Status Code 426: VIP Only - user must upgrade to VIP")
        exit(426)
    if show_detail_response.status_code == 429:
        print("Status Code 429: Rate Limit Exceeded")
        exit(426)
    if 500 <= show_detail_response.status_code < 600:
        print("Status Code", response.status_code+": Service Unavailable")
        exit(response.status_code)
    if show_detail_response.status_code == 200:
        show_detail_data = show_detail_response.json()

    return data.get('runtime', 0), show_detail_data.get('genres', []), data.get('rating', 0)

def analyze_history(history):
    tv_shows = {} # {tvshowid: countofplay}
    tv_minutes = 0
    tv_ratings = 0
    tv_genres = Counter()
    movies = {} # {movieid: countofplay}
    movie_minutes = 0
    movie_ratings = 0
    movie_genres = Counter()
    loop_count = 0

    for item in history:
        if item['type'] == 'episode':
            show_id = item['show'].get('ids', {}).get('trakt')
            if show_id in tv_shows:
                tv_shows[show_id] += 1
            else:
                tv_shows[show_id] = 1
            season_number = item['episode']['season']
            episode_number = item['episode']['number']
            if show_id:
                runtime, genres, rating = get_episode_details(show_id, season_number, episode_number)
                try:
                    tv_minutes += runtime
                except TypeError:
                    tv_minutes += 30
                tv_ratings += rating
            genre_list = genres
            tv_genres.update(genre_list)
        elif item['type'] == 'movie':
            id = item['movie'].get('ids', {}).get('trakt')
            if id in movies:
                movies[id] += 1
            else:
                movies[id] = 1
            if id:
                runtime, genres, rating = get_movie_details(id)
                try:
                    movie_minutes += runtime
                except TypeError:
                     movie_minutes += 90
                movie_ratings += rating
            genre_list = genres
            movie_genres.update(genre_list)
        loop_count += 1
        if loop_count >= 3:
            sleep(1) # To make sure API call rate for Trakt is not breached (1000 calls every 5 minutes). It waits for 1 seconds after ecery 3rd call (max 180 calls in a minute)
            loop_count = 0

    return {
        'tv_shows': len(tv_shows),
        'tv_hours': round(tv_minutes / 60, 2),
        'top_tv_genres': tv_genres.most_common(5),
        'tv_genres_total_count': sum(tv_genres.values()),
        'episodes_average_rating': round(tv_ratings/sum(tv_shows.values()), 1),
        'movies': len(movies),
        'movie_hours': round(movie_minutes / 60, 2),
        'top_movie_genres': movie_genres.most_common(5),
        'movie_genres_total_count': sum(movie_genres.values()),
        'movies_average_rating': round(movie_ratings/sum(movies.values()),1)
    }

def fetch_stats_from_local():
    with open("year-in-review-"+str(year)+".json", "r") as file:
        data = json.load(file)
    
    tv_shows = data["statistics"]["tv_shows"]
    movies = data["statistics"]["movies"]

    return {
        'tv_shows': tv_shows["shows_watched"],
        'tv_hours': tv_shows["hours_watched"],
        'top_tv_genres': tv_shows["top_genres"],
        'tv_genres_total_count': tv_shows["tv_genres_total_count"],
        'episodes_average_rating': tv_shows["episodes_average_rating"],
        'movies': movies["movies_watched"],
        'movie_hours': movies["hours_watched"],
        'top_movie_genres': movies["top_genres"],
        'movie_genres_total_count': movies["movie_genres_total_count"],
        'movies_average_rating': movies["movies_average_rating"]
    }

def fetch_stats_from_trakt():
    # Fetch and analyze the history
    print(f"Preparing your Year in Review for {year}. This might take a few minutes, depending on the size of your watch history...")
    print("Note: Up to 180 movies/episodes are processed per minute to comply with Trakt API rate limits.")
    print("\n")

    history = fetch_trakt_history(username, start_date, end_date)
    with open("trakt-history-"+year+".json", "w") as file:
        file.write(json.dumps(history, indent=4))

    trakt_stat = analyze_history(history)

    # print(stats)

    year_in_review_stats = {
        "username": username,
        "year": year,
        "statistics": {
            "tv_shows": {
                "shows_watched": trakt_stat['tv_shows'],
                "hours_watched": trakt_stat['tv_hours'],
                "average_rating": trakt_stat['episodes_average_rating'],
                "top_genres": trakt_stat['top_tv_genres'],
                "tv_genres_total_count": trakt_stat["tv_genres_total_count"],
                "episodes_average_rating": trakt_stat["episodes_average_rating"]
            },
            "movies": {
                "movies_watched": trakt_stat['movies'],
                "hours_watched": trakt_stat['movie_hours'],
                "average_rating": trakt_stat['movies_average_rating'],
                "top_genres": trakt_stat['top_movie_genres'],
                "movie_genres_total_count": trakt_stat["movie_genres_total_count"],
                "movies_average_rating": trakt_stat["movies_average_rating"]

            }
        }
    }

    with open(f"year-in-review-"+str(year)+".json", "w") as file:
        file.write(json.dumps(year_in_review_stats, indent=4))

    return trakt_stat

start_date = datetime(int(year), 1, 1)
end_date = datetime(int(year), 12, 31)

if not os.path.exists("year-in-review-"+str(year)+".json"):
    fetch_stats_from_trakt()
else:
    use_local_stat = input(f"Local statistics for {year} are available. Would you like to use them? \nSelecting this will use locally stored data and skip importing the latest data from Trakt. (y/N): ")
    print("\n")
    if use_local_stat == "y" or use_local_stat == "Y":
        stats = fetch_stats_from_local()
    else:
        stats = fetch_stats_from_trakt()

# Initialize Console
console = Console()

# Heading
heading = Align.center(f"[bold magenta]Year in Review {year} | Trakt user: {username}[/bold magenta]", vertical="middle")

# Four Cards
cards_table = Table.grid(expand=True)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)
cards_table.add_column(justify="center", ratio=1)

cards_table.add_row(
    Panel(f"Movies Watched\n\n[bold cyan]{stats['movies']}[/bold cyan]", border_style="cyan"),
    Panel(f"Movie Hours\n\n[bold green]{stats['movie_hours']}[/bold green]", border_style="green"),
    Panel(f"Movies Avg Rating\n\n[bold blue]{stats['movies_average_rating']}[/bold blue]", border_style="blue"),
    Panel(f"TV Shows Watched\n\n[bold cyan]{stats['tv_shows']}[/bold cyan]", border_style="cyan"),
    Panel(f"Episode Hours\n\n[bold green]{stats['tv_hours']}[/bold green]", border_style="green"),
    Panel(f"Episodes Avg Rating\n\n[bold blue]{stats['episodes_average_rating']}[/bold blue]", border_style="blue")
)


# Function to create genre rows
def create_genre_row(top_movie_genres_stat, total_count, color):
    genre_row = Table.grid(expand=True)
    for genre, count in top_movie_genres_stat:
        genre_row.add_column(justify="center", ratio=1)

    genre_row.add_row(*[Panel(f"[bold {color}]{genre}\n\n{round(100*count/total_count, 2)}%[/bold {color}]", border_style=color, padding=(0, 2)) for genre, count in top_movie_genres_stat])
    return genre_row

# Top 5 Movie Genres Section
movie_genres_row = create_genre_row(stats['top_movie_genres'], stats['movie_genres_total_count'], "bold cyan")

movie_genres_section = Panel(
    movie_genres_row,
    title="Top 5 Movie Genres",
    border_style="cyan",
    padding=1,
)

# Top 5 TV Show Genres Section
tv_genres_row = create_genre_row(stats['top_tv_genres'], stats['tv_genres_total_count'], "bold green")

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
    Layout(movie_genres_section, size=9),
    Layout("\n\n", size=2),
    Layout(tv_genres_section, size=9),
)

# Print Layout
console.print(layout)