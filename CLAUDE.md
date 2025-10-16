# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FOTD (Flavor of the Day) is a Flask-based web service that displays Culver's Flavor of the Day information for locations near the user. The application:

- Detects user location via IP geolocation (using ipinfo)
- Queries Culver's API to find nearby locations
- Displays flavors in terminal-friendly format (via curl) or HTML in browser
- Deployed on Vercel as a serverless Python application

## Architecture

### Entry Point
- `api/index.py`: Main Flask application with single route `/`
  - Detects curl vs browser via User-Agent header
  - For curl: returns Rich table as plain text with ANSI colors
  - For browser: returns HTML table rendered from Jinja2 template
  - Uses IP-based geolocation as default, falls back to Eden Prairie coordinates on error

### Core Modules
- `api/get_culvers_locs.py`: Culver's API integration and data formatting
  - `get_json_from_lat_long()`: Queries Culver's API by coordinates
  - `get_json_from_zip()`: Queries Culver's API by location string
  - `parse_output()`: Extracts flavor, location, and coordinate data from API response
  - `create_table()`: Builds Rich table with distance calculations and grouping by city/state
  - Filters out "Coming Soon!" locations
  - Groups multiple locations in same city with subheadings

- `api/utils.py`: Helper utilities
  - `get_location_from_ip()`: IPInfo integration (requires IPINFO_TOKEN env var)
  - `get_html_template()`: Returns terminal-styled HTML template with black background

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (required for IP geolocation)
# Create .env file with:
IPINFO_TOKEN=your_token_here

# Run locally (note: Vercel handles Flask app in production)
python -m flask --app api/index run
```

### Testing the API
```bash
# Test via curl (terminal output)
curl 'http://localhost:5000'

# Test via browser (HTML output)
# Visit http://localhost:5000 in browser
```

## Key Technical Details

### Coordinate Handling
- Culver's API returns coordinates as `[longitude, latitude]`
- geopy expects `(latitude, longitude)` tuples
- `_flip_coords()` in `get_culvers_locs.py` handles this transformation

### Distance Calculation
- Uses geopy's `distance()` function with Vincenty formula
- Calculates from user location to each Culver's location
- Sorts results by city/state, then by distance within each city

### API Parameters
- Default radius: 600,000 meters (~373 miles) for lat/long queries
- Default radius: 1,000,000,000 meters for zip/location queries (effectively unlimited)
- Default limit: 10 locations

### Deployment
- Configured for Vercel via `vercel.json`
- All routes rewrite to `/api/index`
- Requires `IPINFO_TOKEN` environment variable in Vercel settings
