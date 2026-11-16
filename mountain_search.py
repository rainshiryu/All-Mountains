#Search and filtering 

import re
from flask import Blueprint, request, session, redirect, url_for, render_template_string
import requests
from mountain_information import API_URL, normalize, pick

search_and_filter = Blueprint('search_and_filter', __name__)


def number(value):
    #Read a numeric value or a simple dollar amount, not a price range."""
    if isinstance(value, bool):
        return None
    match = re.fullmatch(r'\s*\$?(\d+(?:\.\d+)?)\s*', str(value).replace(',', ''))
    return float(match.group(1)) if match else None


def filter_mountains(mountains, query='', location='', difficulty='',
                     min_trails=None, max_price=None):
    results = []
    for raw in mountains:
        if not isinstance(raw, dict):
            continue
        mountain = normalize(raw)
        searchable = (mountain['name'] + ' ' + mountain['location']).casefold()
        if not all(word in searchable for word in query.casefold().split()):
            continue
        if location.casefold() not in mountain['location'].casefold():
            continue
        if difficulty and not re.search(r'\b' + re.escape(difficulty) + r'\b', mountain['difficulty'], re.I):
            continue
        trails = number(mountain['trails'])
        if min_trails is not None and (trails is None or trails < min_trails):
            continue
        price = pick(raw, 'lift_ticket_price', 'liftTicketPrice', 'ticketPrice',
                     'lift_ticket_prices', 'liftTicketPrices', 'ticket_prices', 'prices')
        if isinstance(price, dict):
            price = pick(price, 'adult', 'Adult', 'adult_price', 'adultPrice')
        price = number(price)
        if max_price is not None and (price is None or price > max_price):
            continue
        results.append(mountain)
    return sorted(results, key=lambda m: m['name'].casefold())


PAGE = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Mountains | Search and Filter</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef4f8;color:#183549;font:16px system-ui,sans-serif}header{background:#183549;color:white;padding:22px}main{max-width:1000px;margin:30px auto;padding:0 18px}form,article{background:white;padding:20px;border:1px solid #d5e0e8;border-radius:12px}form{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px}label{display:grid;gap:6px}input,select,button{font:inherit;padding:10px;border:1px solid #a9bac6;border-radius:6px;width:100%}button{background:#18628a;color:white;cursor:pointer}.results{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}a{color:#18628a}h2{font-size:20px}.error{color:#9b2525}
</style></head><body><header><strong>All Mountains</strong></header><main>
<h1>Search and filter ski mountains</h1>
<form method="get">
<label>Mountain name<input name="q" value="{{ q }}" placeholder="Search mountains"></label>
<label>Location<input name="location" value="{{ location }}" placeholder="State or city"></label>
<label>Difficulty<select name="difficulty"><option value="">All levels</option>{% for level in levels %}<option {% if difficulty == level %}selected{% endif %}>{{ level }}</option>{% endfor %}</select></label>
<label>Minimum number of trails<input type="number" min="0" step="1" name="min_trails" value="{{ min_trails }}"></label>
<label>Maximum lift ticket price ($)<input type="number" min="0" step="0.01" name="max_price" value="{{ max_price }}"></label>
<div><button type="submit">Search and filter</button><p><a href="{{ url_for('search_and_filter.search') }}">Clear filters</a></p></div>
</form><p>Price filter uses a single listed ticket price or adult price. Resorts without comparable prices are excluded when the filter is active.</p>
{% if error %}<p class="error" role="alert">{{ error }}</p>{% else %}<p>{{ mountains|length }} mountain(s) found</p><div class="results">
{% for mountain in mountains %}<article><h2>{{ mountain.name }}</h2><p>{{ mountain.location }}</p><p><strong>Trails:</strong> {{ mountain.trails }}</p><p><strong>Difficulty:</strong> {{ mountain.difficulty }}</p><p><strong>Lift tickets:</strong> {{ mountain.prices }}</p><p><strong>Lessons:</strong> {{ mountain.lessons }}</p>{% if mountain.map_url %}<a href="{{ mountain.map_url }}" target="_blank" rel="noopener noreferrer">View trail map</a>{% else %}<p>Trail map not available</p>{% endif %}</article>{% else %}<p>No mountains match your filters.</p>{% endfor %}</div>{% endif %}</main></body></html>'''


@search_and_filter.get('/search-filter/')
def search():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    fields = {key: request.args.get(key, '').strip() for key in
              ('q', 'location', 'difficulty', 'min_trails', 'max_price')}
    levels = ('Beginner', 'Intermediate', 'Advanced', 'Expert')
    def page(mountains=(), error=None, status=200):
        return render_template_string(PAGE, mountains=mountains, error=error,
                                      levels=levels, **fields), status
    minimum = number(fields['min_trails'])
    maximum = number(fields['max_price'])
    if ((fields['min_trails'] and (minimum is None or not minimum.is_integer()))
        or (fields['max_price'] and maximum is None)
        or (fields['difficulty'] and fields['difficulty'] not in levels)):
        return page(error='Please enter valid filter values.', status=400)
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            data = data.get('mountains', data.get('data'))
        if not isinstance(data, list):
            raise ValueError('Unexpected mountain data')
        return page(filter_mountains(data, fields['q'], fields['location'],
                                     fields['difficulty'], minimum, maximum))
    except (requests.RequestException, ValueError):
        return page(error='Mountain data is currently unavailable.', status=503)
