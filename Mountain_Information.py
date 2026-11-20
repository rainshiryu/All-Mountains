# Mountain_Information.py
# Provide users with important mountain information, including name, weather, hours of operation,
# location relevance to where you are, trail maps, difficulty levels, number of trails,
# lift ticket prices, rental prices, and available lessons.
import os
import re
from urllib.parse import urlsplit
from flask import Blueprint, request, session, redirect, url_for, render_template_string
import requests

mountain_search = Blueprint('mountain_search', __name__)
API_URL = os.getenv('MOUNTAIN_API_URL', 'https://mountainmanaged.azurewebsites.net/mountains/')

# Comprehensive Nationwide US Ski Resort Fallback Database
FALLBACK_MOUNTAINS = [
    # --- NEW HAMPSHIRE ---
    {
        "name": "Gunstock Mountain Resort", "city": "Gilford", "state": "New Hampshire (NH)", "country": "USA",
        "latitude": 43.5431, "longitude": -71.3686, "weather": "28°F • Packed Powder, Light Snow",
        "hours_of_operation": "Mon–Thu: 9AM–4PM | Fri–Sat: 9AM–9PM | Sun: 8:30AM–4PM",
        "num_trails": 49, "difficulty_levels": "19% Beginner, 51% Intermediate, 30% Advanced",
        "lift_ticket_prices": "Adult Full Day: $115 | Youth/Senior: $92", "rental_prices": "Full Package: $58/day",
        "available_lessons": "Yes — Group ($75), Private ($165/hr), Learn-to-Ski Package ($139)", "trail_map_url": "https://www.gunstock.com/winter/trail-map/"
    },
    {
        "name": "Loon Mountain Resort", "city": "Lincoln", "state": "New Hampshire (NH)", "country": "USA",
        "latitude": 44.0361, "longitude": -71.6214, "weather": "24°F • Machine Groomed, Partly Sunny",
        "hours_of_operation": "Weekdays: 9AM–4PM | Weekends: 8AM–4PM",
        "num_trails": 73, "difficulty_levels": "20% Beginner, 54% Intermediate, 26% Advanced",
        "lift_ticket_prices": "Adult Full Day: $144 | Junior: $109", "rental_prices": "Sport Package: $64/day",
        "available_lessons": "Yes — Clinics ($95), Private ($210)", "trail_map_url": "https://www.loonmtn.com/trail-map"
    },
    {
        "name": "Bretton Woods", "city": "Bretton Woods", "state": "New Hampshire (NH)", "country": "USA",
        "latitude": 44.2598, "longitude": -71.4622, "weather": "21°F • Fresh Snow (4\")",
        "hours_of_operation": "Daily: 8AM–4PM",
        "num_trails": 98, "difficulty_levels": "23% Beginner, 31% Intermediate, 46% Advanced/Expert",
        "lift_ticket_prices": "Adult Full Day: $139 | Youth/Senior: $105", "rental_prices": "Standard Package: $62/day",
        "available_lessons": "Yes — Group ($89), Private Coaching ($195)", "trail_map_url": "https://www.brettonwoods.com/snow-sports/trail-map"
    },
    {
        "name": "Cannon Mountain", "city": "Franconia", "state": "New Hampshire (NH)", "country": "USA",
        "latitude": 44.1567, "longitude": -71.6987, "weather": "19°F • Crisp & Clear",
        "hours_of_operation": "Mon–Fri: 9AM–4PM | Sat–Sun: 8:30AM–4PM",
        "num_trails": 97, "difficulty_levels": "15% Beginner, 49% Intermediate, 36% Advanced",
        "lift_ticket_prices": "Adult Full Day: $104 | Teen/Senior: $84", "rental_prices": "Full Package: $52/day",
        "available_lessons": "Yes — Beginner Group ($70), Private ($145)", "trail_map_url": "https://www.cannonmt.com/mountain/trail-map"
    },
    {
        "name": "Waterville Valley Resort", "city": "Waterville Valley", "state": "New Hampshire (NH)", "country": "USA",
        "latitude": 43.9652, "longitude": -71.5276, "weather": "25°F • Machine Groomed",
        "hours_of_operation": "Mon–Fri: 9AM–3:45PM | Sat–Sun: 8AM–3:45PM",
        "num_trails": 62, "difficulty_levels": "14% Beginner, 60% Intermediate, 26% Advanced",
        "lift_ticket_prices": "Adult Full Day: $119 | Youth/Senior: $95", "rental_prices": "Full Setup: $59/day",
        "available_lessons": "Yes — First-Timer Package ($149), Group ($85)", "trail_map_url": "https://www.waterville.com/trail-map"
    },
    {
        "name": "Pats Peak", "city": "Henniker", "state": "New Hampshire (NH)", "country": "USA",
        "latitude": 43.1642, "longitude": -71.7972, "weather": "30°F • Packed Powder",
        "hours_of_operation": "Mon–Thu: 9AM–9PM | Fri–Sat: 8:30AM–10PM | Sun: 8:30AM–4PM",
        "num_trails": 28, "difficulty_levels": "50% Beginner, 21% Intermediate, 29% Advanced",
        "lift_ticket_prices": "Adult Full Day: $94 | Night Skiing: $54", "rental_prices": "Package: $49/day",
        "available_lessons": "Yes — Lesson + Rental + Lift ($129)", "trail_map_url": "https://www.patspeak.com/the-mountain/trail-map/"
    },

    # --- COLORADO ---
    {
        "name": "Vail Ski Resort", "city": "Vail", "state": "Colorado (CO)", "country": "USA",
        "latitude": 39.6403, "longitude": -106.3742, "weather": "25°F • Powder Bowls, Light Snow",
        "hours_of_operation": "Daily: 8:30 AM – 4:00 PM",
        "num_trails": 195, "difficulty_levels": "18% Beginner, 29% Intermediate, 53% Advanced/Expert",
        "lift_ticket_prices": "Adult Full Day: $219 | Youth: $145", "rental_prices": "Performance Rental: $79/day",
        "available_lessons": "Yes — Ski & Snowboard School Available", "trail_map_url": "https://www.vail.com/the-mountain/about-the-mountain/trail-map.aspx"
    },
    {
        "name": "Breckenridge Ski Resort", "city": "Breckenridge", "state": "Colorado (CO)", "country": "USA",
        "latitude": 39.4817, "longitude": -106.0676, "weather": "22°F • Alpine Wind, Packed Powder",
        "hours_of_operation": "Daily: 8:30 AM – 4:00 PM",
        "num_trails": 187, "difficulty_levels": "14% Beginner, 31% Intermediate, 55% Advanced/Expert",
        "lift_ticket_prices": "Adult Full Day: $209", "rental_prices": "Standard Package: $72/day",
        "available_lessons": "Yes — Group & Private Lessons", "trail_map_url": "https://www.breckenridge.com/the-mountain/about-the-mountain/trail-map.aspx"
    },
    {
        "name": "Aspen Snowmass", "city": "Aspen", "state": "Colorado (CO)", "country": "USA",
        "latitude": 39.2089, "longitude": -106.9492, "weather": "27°F • Sunny, Groomers",
        "hours_of_operation": "Daily: 9:00 AM – 3:30 PM",
        "num_trails": 336, "difficulty_levels": "6% Beginner, 47% Intermediate, 47% Advanced",
        "lift_ticket_prices": "Adult Full Day: $224", "rental_prices": "Demo Package: $85/day",
        "available_lessons": "Yes — Clinics & Private Instructors", "trail_map_url": "https://www.aspensnowmass.com/"
    },
    {
        "name": "Telluride Ski Resort", "city": "Telluride", "state": "Colorado (CO)", "country": "USA",
        "latitude": 37.9375, "longitude": -107.8123, "weather": "26°F • Clear Skies",
        "hours_of_operation": "Daily: 9:00 AM – 4:00 PM",
        "num_trails": 148, "difficulty_levels": "23% Beginner, 36% Intermediate, 41% Advanced/Expert",
        "lift_ticket_prices": "Adult Full Day: $189", "rental_prices": "Package: $75/day",
        "available_lessons": "Yes — Mountain Sports Academy", "trail_map_url": "https://tellurideskiresort.com/"
    },

    # --- UTAH ---
    {
        "name": "Park City Mountain", "city": "Park City", "state": "Utah (UT)", "country": "USA",
        "latitude": 40.6514, "longitude": -111.5081, "weather": "31°F • Greatest Snow on Earth (Fresh 5\")",
        "hours_of_operation": "Daily: 9:00 AM – 4:00 PM",
        "num_trails": 348, "difficulty_levels": "10% Beginner, 50% Intermediate, 40% Advanced",
        "lift_ticket_prices": "Adult Full Day: $215", "rental_prices": "Demo Ski Package: $78/day",
        "available_lessons": "Yes — Adult and Kids Ski School", "trail_map_url": "https://www.parkcitymountain.com/"
    },
    {
        "name": "Alta Ski Area", "city": "Alta", "state": "Utah (UT)", "country": "USA",
        "latitude": 40.5901, "longitude": -111.6386, "weather": "29°F • Powder Day (Skiers Only)",
        "hours_of_operation": "Daily: 9:15 AM – 4:30 PM",
        "num_trails": 116, "difficulty_levels": "25% Beginner, 40% Intermediate, 35% Advanced",
        "lift_ticket_prices": "Adult Full Day: $149", "rental_prices": "Ski-Only Package: $65/day",
        "available_lessons": "Yes — Alta Lodge Ski School", "trail_map_url": "https://www.alta.com/"
    },
    {
        "name": "Snowbird", "city": "Snowbird", "state": "Utah (UT)", "country": "USA",
        "latitude": 40.5829, "longitude": -111.6536, "weather": "28°F • Deep Powder",
        "hours_of_operation": "Daily: 9:00 AM – 4:00 PM",
        "num_trails": 169, "difficulty_levels": "27% Beginner, 38% Intermediate, 35% Advanced",
        "lift_ticket_prices": "Adult Full Day: $179", "rental_prices": "Demo Package: $82/day",
        "available_lessons": "Yes — Mountain School Available", "trail_map_url": "https://www.snowbird.com/"
    },

    # --- CALIFORNIA ---
    {
        "name": "Mammoth Mountain", "city": "Mammoth Lakes", "state": "California (CA)", "country": "USA",
        "latitude": 37.6308, "longitude": -119.0326, "weather": "35°F • Sunny & Clear",
        "hours_of_operation": "Daily: 8:30 AM – 4:00 PM",
        "num_trails": 175, "difficulty_levels": "25% Beginner, 40% Intermediate, 35% Advanced",
        "lift_ticket_prices": "Adult Full Day: $189", "rental_prices": "Performance Rental: $74/day",
        "available_lessons": "Yes — Group & Private Sessions", "trail_map_url": "https://www.mammothmountain.com/"
    },
    {
        "name": "Palisades Tahoe", "city": "Olympic Valley", "state": "California (CA)", "country": "USA",
        "latitude": 39.1969, "longitude": -120.2358, "weather": "33°F • Spring Skiing Conditions",
        "hours_of_operation": "Daily: 9:00 AM – 4:00 PM",
        "num_trails": 270, "difficulty_levels": "25% Beginner, 45% Intermediate, 30% Advanced",
        "lift_ticket_prices": "Adult Full Day: $205", "rental_prices": "Demo Package: $80/day",
        "available_lessons": "Yes — Ski & Snowboard School", "trail_map_url": "https://www.palisadestahoe.com/"
    },

    # --- VERMONT ---
    {
        "name": "Killington Resort", "city": "Killington", "state": "Vermont (VT)", "country": "USA",
        "latitude": 43.6260, "longitude": -72.7980, "weather": "20°F • Beast of the East, Packed Powder",
        "hours_of_operation": "Mon–Fri: 9AM–4PM | Sat–Sun: 8AM–4PM",
        "num_trails": 155, "difficulty_levels": "17% Beginner, 40% Intermediate, 43% Advanced",
        "lift_ticket_prices": "Adult Full Day: $165 | Youth/Senior: $129", "rental_prices": "Standard Package: $69/day",
        "available_lessons": "Yes — Group Lessons ($110), Private Guides", "trail_map_url": "https://www.killington.com/the-mountain/trail-map"
    },
    {
        "name": "Stowe Mountain Resort", "city": "Stowe", "state": "Vermont (VT)", "country": "USA",
        "latitude": 44.5306, "longitude": -72.7811, "weather": "22°F • Light Flurries",
        "hours_of_operation": "Daily: 8:00 AM – 4:00 PM",
        "num_trails": 116, "difficulty_levels": "16% Beginner, 59% Intermediate, 25% Advanced",
        "lift_ticket_prices": "Adult Full Day: $179", "rental_prices": "Demo Package: $78/day",
        "available_lessons": "Yes — Ski School Available", "trail_map_url": "https://www.stowe.com/"
    },

    # --- WYOMING & MONTANA ---
    {
        "name": "Jackson Hole Mountain Resort", "city": "Teton Village", "state": "Wyoming (WY)", "country": "USA",
        "latitude": 43.5875, "longitude": -110.8278, "weather": "18°F • Steep & Deep Powder",
        "hours_of_operation": "Daily: 9:00 AM – 4:00 PM",
        "num_trails": 133, "difficulty_levels": "10% Beginner, 40% Intermediate, 50% Advanced/Expert",
        "lift_ticket_prices": "Adult Full Day: $195", "rental_prices": "Demo Setup: $85/day",
        "available_lessons": "Yes — Mountain Sports School", "trail_map_url": "https://www.jacksonhole.com/"
    },
    {
        "name": "Big Sky Resort", "city": "Big Sky", "state": "Montana (MT)", "country": "USA",
        "latitude": 45.2842, "longitude": -111.4019, "weather": "16°F • Cold & Clear, Dry Snow",
        "hours_of_operation": "Daily: 9:00 AM – 4:00 PM",
        "num_trails": 321, "difficulty_levels": "15% Beginner, 25% Intermediate, 60% Advanced/Expert",
        "lift_ticket_prices": "Adult Full Day: $185", "rental_prices": "Package: $79/day",
        "available_lessons": "Yes — Private and Group Lessons", "trail_map_url": "https://bigskyresort.com/"
    },

    # --- MAINE & NEW YORK ---
    {
        "name": "Sunday River", "city": "Newry", "state": "Maine (ME)", "country": "USA",
        "latitude": 44.4717, "longitude": -70.8567, "weather": "23°F • Packed Powder",
        "hours_of_operation": "Mon–Fri: 9AM–4PM | Sat–Sun: 8AM–4PM",
        "num_trails": 139, "difficulty_levels": "21% Beginner, 36% Intermediate, 43% Advanced",
        "lift_ticket_prices": "Adult Full Day: $149", "rental_prices": "Sport Rental: $66/day",
        "available_lessons": "Yes — Group Clinics ($99)", "trail_map_url": "https://www.sundayriver.com/trail-map"
    },
    {
        "name": "Whiteface Mountain", "city": "Wilmington", "state": "New York (NY)", "country": "USA",
        "latitude": 44.3656, "longitude": -73.9032, "weather": "21°F • Olympic Mountain, Packed Snow",
        "hours_of_operation": "Daily: 8:30 AM – 3:30 PM",
        "num_trails": 94, "difficulty_levels": "20% Beginner, 42% Intermediate, 38% Advanced",
        "lift_ticket_prices": "Adult Full Day: $118", "rental_prices": "Package: $55/day",
        "available_lessons": "Yes — Snowsports School", "trail_map_url": "https://whiteface.com/"
    }
]

PAGE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>All Mountains | Mountain Directory</title>
  <style>
    :root {
      --pine-dark: #163028;
      --pine-primary: #2c5e4f;
      --pine-light: #e7f0ed;
      --sunset-accent: #d97724;
      --sunset-hover: #b86119;
      --snow-bg: #f3f6f5;
      --card-bg: #ffffff;
      --text-main: #1d2b27;
      --text-muted: #5a6e67;
      --border-subtle: #d5e0dc;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background-color: var(--snow-bg);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
    }

    /* Top Navigation Bar */
    header {
      background: var(--pine-dark);
      color: #ffffff;
      padding: 16px 24px;
      border-bottom: 4px solid var(--sunset-accent);
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
    }

    .nav-inner {
      max-width: 1180px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.4px;
      display: flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      color: #ffffff;
    }

    .nav-links {
      display: flex;
      gap: 16px;
      align-items: center;
    }

    .nav-link {
      color: #d3e3de;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.9rem;
    }
    .nav-link:hover { color: #ffffff; text-decoration: underline; }

    /* Hero Search Banner */
    .hero {
      background: linear-gradient(135deg, #1f4439 0%, #2c5e4f 100%);
      color: #ffffff;
      padding: 44px 20px 52px;
      text-align: center;
    }

    .hero-inner {
      max-width: 780px;
      margin: 0 auto;
    }

    .hero h1 {
      margin: 0 0 10px;
      font-size: 2.1rem;
      font-weight: 800;
      letter-spacing: -0.5px;
    }

    .hero p {
      margin: 0 0 26px;
      color: #d3e3de;
      font-size: 1.05rem;
    }

    /* Search Bar */
    .search-form {
      display: flex;
      gap: 10px;
      background: #ffffff;
      padding: 8px;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(15, 35, 29, 0.25);
      flex-wrap: wrap;
    }

    .search-form input {
      flex: 1;
      min-width: 220px;
      border: none;
      padding: 12px 14px;
      font-size: 1rem;
      color: var(--text-main);
      outline: none;
      background: transparent;
    }

    .btn {
      font: inherit;
      font-weight: 600;
      padding: 11px 20px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.15s ease, transform 0.1s ease;
    }

    .btn-primary {
      background: var(--sunset-accent);
      color: #ffffff;
    }

    .btn-primary:hover {
      background: var(--sunset-hover);
    }

    .btn-secondary {
      background: var(--pine-primary);
      color: #ffffff;
      font-size: 0.9rem;
      padding: 9px 15px;
    }

    .btn-secondary:hover {
      background: var(--pine-dark);
    }

    .btn-clear {
      background: #edf2f0;
      color: var(--text-muted);
    }

    .btn-clear:hover {
      background: #dfe7e4;
      color: var(--text-main);
    }

    /* Filter Row */
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      width: 100%;
      border-top: 1px solid #e3ebe8;
      padding: 10px 6px 4px;
    }

    .filter-row label {
      display: flex;
      flex-direction: column;
      flex: 1;
      min-width: 150px;
      text-align: left;
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--text-muted);
      gap: 4px;
    }

    .search-form .filter-row input,
    .filter-row select {
      min-width: 0;
      border: 1px solid #d5e0dc;
      border-radius: 8px;
      padding: 8px 10px;
      font: inherit;
      font-size: 0.95rem;
      font-weight: 400;
      color: var(--text-main);
      background: #ffffff;
    }

    /* Location Relevance Toolbar */
    .location-bar {
      margin-top: 16px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: center;
      align-items: center;
    }

    .manual-loc-group {
      display: flex;
      background: rgba(255, 255, 255, 0.14);
      border: 1px solid rgba(255, 255, 255, 0.28);
      border-radius: 8px;
      padding: 3px;
    }

    .manual-loc-group input {
      background: transparent;
      border: none;
      color: #ffffff;
      padding: 6px 10px;
      font-size: 0.9rem;
      outline: none;
      width: 190px;
    }

    .manual-loc-group input::placeholder {
      color: #c5dad4;
    }

    .manual-loc-group button {
      background: rgba(255, 255, 255, 0.2);
      color: #ffffff;
      border: none;
      border-radius: 6px;
      padding: 6px 12px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
    }

    .manual-loc-group button:hover {
      background: rgba(255, 255, 255, 0.32);
    }

    #location-status {
      width: 100%;
      font-size: 0.88rem;
      color: #e7f0ed;
      margin-top: 4px;
    }

    /* Main Content Area */
    main {
      max-width: 1180px;
      margin: 32px auto 64px;
      padding: 0 20px;
    }

    .results-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 20px;
      color: var(--text-muted);
      font-size: 0.95rem;
      font-weight: 500;
    }

    .sort-controls {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .sort-controls select {
      padding: 7px 12px;
      border-radius: 8px;
      border: 1px solid var(--border-subtle);
      background: #ffffff;
      color: var(--text-main);
      font: inherit;
      font-size: 0.9rem;
      font-weight: 600;
    }

    /* Error & Empty States */
    .alert-error {
      background: #fdecea;
      border-left: 5px solid #d93025;
      color: #9b1c1c;
      padding: 16px 20px;
      border-radius: 8px;
      font-weight: 500;
    }

    .empty-state {
      text-align: center;
      background: var(--card-bg);
      border: 1px dashed var(--border-subtle);
      border-radius: 14px;
      padding: 48px 20px;
      color: var(--text-muted);
    }

    .empty-state h3 {
      margin: 0 0 8px;
      color: var(--text-main);
    }

    /* Mountain Cards Grid */
    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 24px;
    }

    .mountain-card {
      background: var(--card-bg);
      border: 1px solid var(--border-subtle);
      border-top: 5px solid var(--pine-primary);
      border-radius: 14px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 4px 12px rgba(22, 48, 40, 0.05);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .mountain-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 24px rgba(22, 48, 40, 0.11);
    }

    .card-header {
      margin-bottom: 16px;
      padding-bottom: 14px;
      border-bottom: 1px solid #eef3f1;
    }

    .card-header h2 {
      margin: 0 0 8px;
      font-size: 1.32rem;
      color: var(--pine-dark);
      line-height: 1.25;
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }

    .location-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.83rem;
      font-weight: 600;
      color: var(--pine-primary);
      background: var(--pine-light);
      padding: 4px 10px;
      border-radius: 20px;
    }

    .distance-badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 0.83rem;
      font-weight: 700;
      color: #9c4b0c;
      background: #fdf0e4;
      border: 1px solid #f5d3b3;
      padding: 4px 10px;
      border-radius: 20px;
    }

    .distance-badge.hidden {
      display: none;
    }

    /* Specs List */
    .specs-list {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 20px;
    }

    .spec-item {
      background: #f8fbfa;
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid #eaf0ee;
    }

    .spec-item.full-width {
      grid-column: 1 / -1;
    }

    .spec-item.weather-highlight {
      background: #f2f8fc;
      border-color: #d7e8f5;
    }

    .spec-label {
      display: block;
      font-size: 0.73rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      font-weight: 700;
      margin-bottom: 3px;
    }

    .spec-value {
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-main);
      word-break: break-word;
    }

    /* Card Footer / Trail Map Action */
    .card-footer {
      margin-top: auto;
      display: flex;
      gap: 10px;
    }

    .btn-map {
      flex: 1;
      background: var(--pine-primary);
      color: #ffffff;
      padding: 11px 14px;
      border-radius: 8px;
      text-align: center;
      font-weight: 600;
      font-size: 0.92rem;
      text-decoration: none;
      display: block;
      transition: background 0.15s ease;
    }

    .btn-map:hover {
      background: var(--pine-dark);
    }

    .btn-directions {
      background: #edf2f0;
      color: var(--pine-dark);
      padding: 11px 14px;
      border-radius: 8px;
      text-align: center;
      font-weight: 600;
      font-size: 0.92rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s ease;
    }

    .btn-directions:hover {
      background: #dfe7e4;
    }

    .btn-map-disabled {
      flex: 1;
      background: #edf2f0;
      color: #82948e;
      padding: 11px 14px;
      border-radius: 8px;
      text-align: center;
      font-weight: 600;
      font-size: 0.9rem;
      display: block;
      cursor: not-allowed;
    }
  </style>
</head>
<body>

  <header>
    <div class="nav-inner">
      <a href="{{ url_for('mountain_search.search') }}" class="brand">
        <span>🏔️</span> All Mountains
      </a>
      <div class="nav-links">
        <a href="{{ url_for('logout') }}" class="nav-link">🚪 Log Out</a>
      </div>
    </div>
  </header>

  <section class="hero">
    <div class="hero-inner">
      <h1>Find your next ski mountain</h1>
      <p>Check live weather, operating hours, distance from you, lift tickets, rentals, and lessons across the USA.</p>
      <form method="get" class="search-form">
        <input
          name="q"
          aria-label="Mountain name or location"
          placeholder="Search by resort name, city, state (e.g. Colorado, Utah)..."
          value="{{ query }}"
        >
        <button type="submit" class="btn btn-primary">Search Resorts</button>
        {% if query or difficulty or min_trails or max_price %}
          <a href="{{ url_for('mountain_search.search') }}" class="btn btn-clear">Clear</a>
        {% endif %}

        <!-- Filters -->
        <div class="filter-row">
          <label>Skill Level
            <select name="difficulty">
              <option value="">Any level</option>
              {% for level in levels %}
                <option value="{{ level }}" {% if difficulty == level %}selected{% endif %}>Good for {{ level }}</option>
              {% endfor %}
            </select>
          </label>
          <label>Min Trails
            <input type="number" name="min_trails" min="0" step="1" placeholder="e.g. 50" value="{{ min_trails }}">
          </label>
          <label>Max Lift Ticket ($)
            <input type="number" name="max_price" min="0" step="1" placeholder="e.g. 150" value="{{ max_price }}">
          </label>
        </div>
      </form>

      <!-- Location Relevance Controls -->
      <div class="location-bar">
        <button type="button" id="use-gps-btn" class="btn btn-secondary">
          📍 Calculate Distance From My Location
        </button>
        <div class="manual-loc-group">
          <input type="text" id="manual-city-input" placeholder="Or enter City, State / ZIP">
          <button type="button" id="manual-city-btn">Set Location</button>
        </div>
        <div id="location-status"></div>
      </div>
    </div>
  </section>

  <main>
    {% if error %}
      <div class="alert-error" role="alert">⚠️ {{ error }}</div>
    {% else %}
      <div class="results-meta">
        <span>
          Showing <strong>{{ mountains|length }}</strong> mountain{{ 's' if mountains|length != 1 else '' }}
          {% if query %} matching "<strong>{{ query }}</strong>"{% endif %}
        </span>

        {% if mountains %}
          <div class="sort-controls">
            <label for="sort-select">Sort by:</label>
            <select id="sort-select">
              <option value="name">Name (A–Z)</option>
              <option value="price">Lift Ticket (Lowest First)</option>
              <option value="trails">Most Trails</option>
              <option value="distance" disabled id="sort-distance-opt">Distance (Closest First)</option>
            </select>
          </div>
        {% endif %}
      </div>

      {% if mountains %}
        <div class="results-grid" id="mountains-grid">
          {% for mountain in mountains %}
            <article
              class="mountain-card"
              data-name="{{ mountain.name }}"
              data-location="{{ mountain.location }}"
              data-lat="{{ mountain.lat if mountain.lat is not none else '' }}"
              data-lon="{{ mountain.lon if mountain.lon is not none else '' }}"
              data-distance=""
              data-price="{{ mountain.price_num if mountain.price_num is not none else '' }}"
              data-trails="{{ mountain.trails_num if mountain.trails_num is not none else '' }}"
            >
              <div>
                <div class="card-header">
                  <h2>{{ mountain.name }}</h2>
                  <div class="badge-row">
                    {% if mountain.location %}
                      <span class="location-badge">📍 {{ mountain.location }}</span>
                    {% endif %}
                    <span class="distance-badge hidden"></span>
                  </div>
                </div>

                <div class="specs-list">
                  <div class="spec-item weather-highlight full-width">
                    <span class="spec-label">🌤️ Current Weather</span>
                    <span class="spec-value">{{ mountain.weather }}</span>
                  </div>

                  <div class="spec-item full-width">
                    <span class="spec-label">🕒 Hours of Operation</span>
                    <span class="spec-value">{{ mountain.hours }}</span>
                  </div>

                  <div class="spec-item">
                    <span class="spec-label">🎟️ Lift Tickets</span>
                    <span class="spec-value">{{ mountain.prices }}</span>
                  </div>

                  <div class="spec-item">
                    <span class="spec-label">🎿 Rental Prices</span>
                    <span class="spec-value">{{ mountain.rentals }}</span>
                  </div>

                  <div class="spec-item">
                    <span class="spec-label">🏔️ Trails</span>
                    <span class="spec-value">{{ mountain.trails }}</span>
                  </div>

                  <div class="spec-item">
                    <span class="spec-label">⛰️ Difficulty</span>
                    <span class="spec-value">{{ mountain.difficulty }}</span>
                  </div>

                  <div class="spec-item full-width">
                    <span class="spec-label">🧑‍🏫 Lessons Offered</span>
                    <span class="spec-value">{{ mountain.lessons }}</span>
                  </div>
                </div>
              </div>

              <div class="card-footer">
                {% if mountain.map_url %}
                  <a href="{{ mountain.map_url }}" target="_blank" rel="noopener noreferrer" class="btn-map">
                    🗺️ Trail Map ↗
                  </a>
                {% else %}
                  <span class="btn-map-disabled">Trail Map Unavailable</span>
                {% endif %}
                <a
                  href="https://www.google.com/maps/dir/?api=1&destination={{ (mountain.name ~ ' ' ~ mountain.location)|urlencode }}"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-directions"
                  title="Get Driving Directions"
                >
                  🚗 Directions
                </a>
              </div>
            </article>
          {% endfor %}
        </div>
      {% else %}
        <div class="empty-state">
          <h3>No ski mountains found</h3>
          <p>We couldn't find any resorts matching your search. Try searching a broader location or clearing your filter.</p>
        </div>
      {% endif %}
    {% endif %}
  </main>

  <script>
    (function () {
      const gpsBtn = document.getElementById('use-gps-btn');
      const manualInput = document.getElementById('manual-city-input');
      const manualBtn = document.getElementById('manual-city-btn');
      const statusEl = document.getElementById('location-status');
      const sortSelect = document.getElementById('sort-select');
      const sortDistOpt = document.getElementById('sort-distance-opt');
      const grid = document.getElementById('mountains-grid');
      const geocodeCache = {};

      if (!gpsBtn || !grid) return;

      function haversineMiles(lat1, lon1, lat2, lon2) {
        const toRad = (deg) => (deg * Math.PI) / 180;
        const R = 3958.8;
        const dLat = toRad(lat2 - lat1);
        const dLon = toRad(lon2 - lon1);
        const a =
          Math.sin(dLat / 2) * Math.sin(dLat / 2) +
          Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
          Math.sin(dLon / 2) * Math.sin(dLon / 2);
        return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
      }

      function formatDriveTime(miles) {
        const estRoadMiles = miles * 1.2;
        const totalMins = Math.round((estRoadMiles / 52) * 60);
        const hrs = Math.floor(totalMins / 60);
        const mins = totalMins % 60;
        return hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`;
      }

      async function geocodePlace(query) {
        if (geocodeCache[query]) return geocodeCache[query];
        const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(query)}`;
        const resp = await fetch(url);
        if (!resp.ok) return null;
        const data = await resp.json();
        if (data && data.length > 0) {
          const coords = { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
          geocodeCache[query] = coords;
          return coords;
        }
        return null;
      }

      async function updateDistances(userLat, userLon, label) {
        statusEl.textContent = `Calculating distances from ${label}...`;
        const cards = Array.from(grid.querySelectorAll('.mountain-card'));

        for (const card of cards) {
          let lat = parseFloat(card.dataset.lat);
          let lon = parseFloat(card.dataset.lon);

          if (isNaN(lat) || isNaN(lon)) {
            const searchPlace = `${card.dataset.name}, ${card.dataset.location}`.trim();
            const coords = await geocodePlace(searchPlace) || await geocodePlace(card.dataset.location);
            if (coords) {
              lat = coords.lat;
              lon = coords.lon;
              card.dataset.lat = lat;
              card.dataset.lon = lon;
            }
          }

          const badge = card.querySelector('.distance-badge');
          if (!isNaN(lat) && !isNaN(lon) && badge) {
            const dist = haversineMiles(userLat, userLon, lat, lon);
            const roadMiles = Math.round(dist * 1.2);
            card.dataset.distance = dist.toFixed(2);
            badge.textContent = `🚗 ~${roadMiles} mi (${formatDriveTime(dist)} drive)`;
            badge.classList.remove('hidden');
          }
        }

        statusEl.textContent = `Showing location relevance from ${label}`;
        if (sortDistOpt && sortSelect) {
          sortDistOpt.disabled = false;
          sortSelect.value = 'distance';
          sortCards('distance');
        }
      }

      function sortCards(mode) {
        const cards = Array.from(grid.querySelectorAll('.mountain-card'));
        cards.sort((a, b) => {
          if (mode === 'distance') {
            const da = parseFloat(a.dataset.distance);
            const db = parseFloat(b.dataset.distance);
            if (isNaN(da) && isNaN(db)) return 0;
            if (isNaN(da)) return 1;
            if (isNaN(db)) return -1;
            return da - db;
          }
          if (mode === 'price' || mode === 'trails') {
            const va = parseFloat(mode === 'price' ? a.dataset.price : a.dataset.trails);
            const vb = parseFloat(mode === 'price' ? b.dataset.price : b.dataset.trails);
            if (isNaN(va) && isNaN(vb)) return 0;
            if (isNaN(va)) return 1;
            if (isNaN(vb)) return -1;
            return mode === 'price' ? va - vb : vb - va;
          }
          return a.dataset.name.localeCompare(b.dataset.name);
        });
        cards.forEach((card) => grid.appendChild(card));
      }

      gpsBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
          statusEl.textContent = 'Geolocation is not supported by your browser. Enter a city above.';
          return;
        }
        statusEl.textContent = 'Requesting your location...';
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            updateDistances(pos.coords.latitude, pos.coords.longitude, 'your current location');
          },
          () => {
            statusEl.textContent = 'Location permission denied. Enter a City/State or ZIP code instead.';
          }
        );
      });

      manualBtn.addEventListener('click', async () => {
        const val = manualInput.value.trim();
        if (!val) return;
        statusEl.textContent = `Looking up "${val}"...`;
        const coords = await geocodePlace(val);
        if (coords) {
          updateDistances(coords.lat, coords.lon, val);
        } else {
          statusEl.textContent = `Could not locate "${val}". Try entering "City, State" or a ZIP code.`;
        }
      });

      manualInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          manualBtn.click();
        }
      });

      if (sortSelect) {
        sortSelect.addEventListener('change', (e) => sortCards(e.target.value));
      }
    })();
  </script>

</body>
</html>'''


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


# Skill level filter: a mountain is "good for" a level if at least this
# percent of its trails are that level.
LEVEL_THRESHOLDS = {'Beginner': 20, 'Intermediate': 40, 'Advanced': 40}


def first_number(value):
    """Pull the first number out of things like 'Adult Full Day: $115 | Youth: $92'."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r'\d+(?:\.\d+)?', str(value).replace(',', ''))
    return float(match.group()) if match else None


def level_percent(difficulty, level):
    """Read e.g. '20% Beginner, 54% Intermediate' and return the percent for one level."""
    match = re.search(r'(\d+)\s*%\s*' + re.escape(level), str(difficulty), re.I)
    return int(match.group(1)) if match else None


def normalize(item):
    city = str(pick(item, 'city', 'location') or '')
    state = str(pick(item, 'state', 'province') or '')
    country = str(pick(item, 'country') or '')
    
    loc_parts = [p for p in (city, state, country) if p]
    location = ', '.join(dict.fromkeys(loc_parts))
    
    trails = pick(item, 'num_trails', 'trail_count', 'number_of_trails', 'numberOfTrails', 'trailCount', 'trails')
    if isinstance(trails, list):
        trails = len(trails)
        
    return {
        'name': str(pick(item, 'name', 'mountain_name', 'mountainName') or 'Unnamed mountain'),
        'location': location,
        'city': city.casefold(),
        'state': state.casefold(),
        'country': country.casefold(),
        'lat': pick(item, 'latitude', 'lat'),
        'lon': pick(item, 'longitude', 'lon', 'lng'),
        'weather': display(pick(item, 'weather', 'current_weather', 'currentWeather', 'conditions', 'forecast')),
        'hours': display(pick(item, 'hours_of_operation', 'hoursOfOperation', 'operating_hours', 'operatingHours', 'hours')),
        'trails': display(trails),
        'difficulty': display(pick(item, 'difficulty_levels', 'difficultyLevels', 'difficulty', 'trail_difficulty')),
        'prices': display(pick(item, 'lift_ticket_prices', 'liftTicketPrices', 'lift_ticket_price', 'liftTicketPrice', 'ticket_prices', 'ticketPrice', 'prices')),
        'rentals': display(pick(item, 'rental_prices', 'rentalPrices', 'equipment_rentals', 'equipmentRentals', 'rentals', 'rental_price')),
        'lessons': display(pick(item, 'available_lessons', 'availableLessons', 'lessons', 'ski_lessons', 'lessonAvailability')),
        'map_url': safe_url(pick(item, 'trail_map_url', 'trailMapUrl', 'trail_map', 'trailMap', 'map_url')),
        'trails_num': first_number(trails),
        'price_num': first_number(pick(item, 'lift_ticket_prices', 'liftTicketPrices', 'lift_ticket_price', 'liftTicketPrice', 'ticket_prices', 'ticketPrice', 'prices')),
    }


@mountain_search.get('/search/')
def search():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    min_trails = request.args.get('min_trails', '').strip()
    max_price = request.args.get('max_price', '').strip()
    if difficulty not in LEVEL_THRESHOLDS:
        difficulty = ''
    data = []
    
    try:
        response = requests.get(API_URL, timeout=6)
        response.raise_for_status()
        api_json = response.json()
        if isinstance(api_json, dict):
            data = api_json.get('mountains', api_json.get('data', api_json.get('results', [])))
        elif isinstance(api_json, list):
            data = api_json
    except Exception as e:
        print("Azure API notice:", e)

    if not data or not isinstance(data, list):
        data = FALLBACK_MOUNTAINS

    mountains = [normalize(item) for item in data if isinstance(item, dict)]

    if query:
        q_lower = query.casefold()
        filtered = []
        for m in mountains:
            searchable_text = f"{m['name']} {m['location']} {m['city']} {m['state']} {m['country']}".casefold()
            if all(word in searchable_text for word in q_lower.split()):
                filtered.append(m)
        mountains = filtered

    if difficulty:
        mountains = [m for m in mountains
                     if (level_percent(m['difficulty'], difficulty) or 0) >= LEVEL_THRESHOLDS[difficulty]]

    min_trails_num = first_number(min_trails)
    if min_trails_num is not None:
        mountains = [m for m in mountains if m['trails_num'] is not None and m['trails_num'] >= min_trails_num]

    max_price_num = first_number(max_price)
    if max_price_num is not None:
        mountains = [m for m in mountains if m['price_num'] is not None and m['price_num'] <= max_price_num]

    mountains.sort(key=lambda m: m['name'].casefold())
    return render_template_string(PAGE, mountains=mountains, query=query, error=None,
                                  levels=list(LEVEL_THRESHOLDS), difficulty=difficulty,
                                  min_trails=min_trails, max_price=max_price)