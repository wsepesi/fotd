import ipinfo
from dotenv import load_dotenv
import os
import requests
from geopy.distance import distance

def _coords_string_to_list(coords):
    return [float(coord) for coord in coords.split(',')]

def get_location_from_ip(ip):
    load_dotenv()
    token = os.getenv('IPINFO_TOKEN')
    handler = ipinfo.getHandler(token)

    res = handler.getDetails(ip)

    return f'{res.city}, {res.region}', _coords_string_to_list(res.loc)

def get_location_from_ipdata(ip):
    """Query ipdata.co API for IP geolocation (free tier: 1500/day)"""
    load_dotenv()
    api_key = os.getenv('IPDATA_API_KEY', '')

    # ipdata.co free tier endpoint
    url = f'https://api.ipdata.co/{ip}'
    params = {'api-key': api_key} if api_key else {}

    try:
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()
        data = response.json()

        location = f"{data['city']}, {data['region']}"
        coordinates = [data['latitude'], data['longitude']]

        return location, coordinates
    except Exception as e:
        print(f"ipdata.co error: {e}")
        return None, None

def get_location_with_consensus(ip):
    """
    Query both ipinfo and ipdata.co, use consensus logic for better accuracy.
    Returns: (location_string, coordinates, is_confident)
    """
    # Query both providers
    ipinfo_loc, ipinfo_coords = get_location_from_ip(ip)
    ipdata_loc, ipdata_coords = get_location_from_ipdata(ip)

    # If ipdata failed, use ipinfo only
    if ipdata_loc is None or ipdata_coords is None:
        return ipinfo_loc, ipinfo_coords, True

    # Calculate distance between the two results
    # ipinfo returns [lat, long], ipdata returns [lat, long]
    dist_km = distance(
        (ipinfo_coords[0], ipinfo_coords[1]),
        (ipdata_coords[0], ipdata_coords[1])
    ).kilometers

    # If both providers agree within 10km, high confidence
    is_confident = dist_km < 10

    # Use ipinfo as primary (since we've been using it)
    return ipinfo_loc, ipinfo_coords, is_confident

def get_html_template():
    html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FOTD - Flavor of the Day</title>
            <style>
                body {
                    font-family: 'Courier New', Courier, monospace;
                    background-color: #000;
                    color: #ffffff;
                    padding: 20px;
                    line-height: 1.6;
                }
                .terminal {
                    border: 1px solid #ffffff;
                    padding: 20px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    text-align: left;
                    padding: 8px;
                    border-bottom: 1px solid #ffffff;
                }
                th {
                    color: #ffffff;
                }
            </style>
        </head>
        <body>
            <div class="terminal">
                <table>
                    <tr>
                        <th>Location</th>
                        <th>Flavor of the Day</th>
                        <th>Coordinates</th>
                    </tr>
                    {% for row in table_data %}
                    <tr>
                        <td>{{ row['location'] }}</td>
                        <td>{{ row['flavor of the day'] }}</td>
                        <td>{{ row['coordinates'] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% if show_warning %}
                <p style="margin-top: 20px; opacity: 0.6; text-align: center;">
                    Location based on ISP routing. For accurate results, add ?zip=YOUR_ZIP
                </p>
                {% endif %}
            </div>
        </body>
        </html>
        """
    return html_template