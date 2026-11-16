#Provide users with important mountain information, including trail maps, difficulty levels, number of trails, lift ticket prices, and available lessons.
import os
from urllib.parse import urlsplit
from flask import Blueprint, request, session, redirect, url_for, render_template_string
import requests

mountain_search = Blueprint('mountain_search', __name__)
API_URL = os.getenv('MOUNTAIN_API_URL', 'https://mountainmanaged.azurewebsites.net/mountains/')

PAGE = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>All Mountains | Search</title>
<style>
*{box-sizing:border-box} body{margin:0;background:#eef4f8;color:#183549;font:16px system-ui,sans-serif} header{background:#183549;color:white;padding:22px} main{max-width:960px;margin:36px auto;padding:0 18px} form{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0} input,button{font:inherit;padding:12px;border-radius:8px;border:1px solid #a9bac6} input{flex:1;min-width:200px} button{background:#18628a;color:white;cursor:pointer} .results{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px} article{background:white;padding:20px;border-radius:12px;border:1px solid #d5e0e8} h2{margin-top:0;font-size:20px} .error{color:#9b2525} a{color:inherit}
</style></head><body><header><strong>All Mountains</strong></header><main>
<h1>Find your next ski mountain</h1><p>Search by mountain name, state, or location.</p>
<form method="get"><input name="q" aria-label="Mountain name or location" placeholder="Search mountains (e.g. New Hampshire)" value="{{ query }}"><button type="submit">Search</button><a href="{{ url_for('mountain_search.search') }}">Clear</a></form>
{% if error %}<p class="error" role="alert">{{ error }}</p>{% else %}<p>{{ mountains|length }} mountain(s) found</p>
<div class="results">{% for mountain in mountains %}<article><h2>{{ mountain.name }}</h2><p>{{ mountain.location }}</p><p><strong>Number of trails:</strong> {{ mountain.trails }}</p><p><strong>Difficulty levels:</strong> {{ mountain.difficulty }}</p><p><strong>Lift ticket prices:</strong> {{ mountain.prices }}</p><p><strong>Available lessons:</strong> {{ mountain.lessons }}</p><p><strong>Trail map:</strong> {% if mountain.map_url %}<a href="{{ mountain.map_url }}" target="_blank" rel="noopener noreferrer">View trail map</a>{% else %}Not available{% endif %}</p></article>{% else %}<p>No mountains match your search.</p>{% endfor %}</div>{% endif %}
</main></body></html>'''

def pick(item, *keys):
    for key in keys:
        value = item.get(key)
        if value is not None and value != '':
            return value
    return None


def display(value):
    if value is None:
        return 'Not available'
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, dict):
        return '; '.join(f'{key}: {display(val)}' for key, val in value.items()) or 'Not available'
    if isinstance(value, list):
        return '; '.join(display(val) for val in value) or 'None listed'
    return str(value)


def safe_url(value):
    if isinstance(value, dict):
        value = value.get('url')
    if isinstance(value, str):
        try:
            parsed = urlsplit(value)
            if parsed.scheme in ('https', 'http') and parsed.hostname:
                return value
        except ValueError:
            pass
    return None


def normalize(item):
    location = ', '.join(dict.fromkeys(str(item[k]) for k in ('location', 'city', 'state', 'country') if item.get(k)))
    trails = pick(item, 'num_trails', 'trail_count', 'number_of_trails', 'numberOfTrails', 'trailCount', 'trails')
    if isinstance(trails, list):
        trails = len(trails)
    return {
        'name': str(pick(item, 'name', 'mountain_name', 'mountainName') or 'Unnamed mountain'),
        'location': location,
        'trails': display(trails),
        'difficulty': display(pick(item, 'difficulty_levels', 'difficultyLevels', 'difficulty', 'trail_difficulty')),
        'prices': display(pick(item, 'lift_ticket_prices', 'liftTicketPrices', 'lift_ticket_price', 'liftTicketPrice', 'ticket_prices', 'ticketPrice', 'prices')),
        'lessons': display(pick(item, 'available_lessons', 'availableLessons', 'lessons', 'ski_lessons', 'lessonAvailability')),
        'map_url': safe_url(pick(item, 'trail_map_url', 'trailMapUrl', 'trail_map', 'trailMap', 'map_url')),
    }


@mountain_search.get('/search/')
def search():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            data = data.get('mountains', data.get('data'))
        if not isinstance(data, list):
            raise ValueError('Unexpected mountain API response')
        mountains = [normalize(item) for item in data if isinstance(item, dict)]
        words = query.casefold().split()
        mountains = [m for m in mountains if all(word in (m['name'] + ' ' + m['location']).casefold() for word in words)]
        mountains.sort(key=lambda m: m['name'].casefold())
        return render_template_string(PAGE, mountains=mountains, query=query, error=None)
    except (requests.RequestException, ValueError):
        return render_template_string(PAGE, mountains=[], query=query, error='Mountain data is currently unavailable. Please try again later.'), 503
