import requests
from datetime import datetime
from collections import Counter
import json
from dotenv import load_dotenv
import os


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
    file.write(json.dumps(history))
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
