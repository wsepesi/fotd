import requests

from rich.table import Table
from geopy.distance import distance

def get_json_from_lat_long(lat, long, radius=600000, limit=10):
    url = 'https://www.culvers.com/api/locator/getLocations'
    params = {
        'lat': lat,
        'long': long,
        'radius': radius,
        'limit': limit,
        'layer': ''
    }
    headers = {
        'authority': 'www.culvers.com',
        'accept': '*/*',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def get_json_from_zip(location, radius=1000000000, limit=10):
    url = 'https://www.culvers.com/api/locator/getLocations'
    params = {
        'location': location,
        'radius': radius,
        'limit': limit,
        'layer': ''
    }
    headers = {
        'authority': 'www.culvers.com',
        'accept': '*/*',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def parse_output(res, include_hrs=False):
    locations = res['data']['geofences']

    parsed = []

    for location in locations:
        description = location['description']
        flavor = location['metadata'].get('flavorOfDayName', 'Not specified')
        city = location['metadata']['city']
        state = location['metadata']['state']
        fotdSlug = location['metadata']['flavorOfDaySlug']
        coordinates = location['geometryCenter']['coordinates']
        hrs = location['metadata']['dineInHours']
        driveThruHrs = location['metadata']['driveThruHours']

        parsed.append({
            'description': description,
            'flavor': flavor,
            'city': city,
            'state': state,
            'fotdSlug': fotdSlug,
            'coordinates': coordinates,
            'hrs': hrs,
            'driveThruHrs': driveThruHrs
        })
        
    return parsed

def _handle_coords(coords):
    def _format_coord(coord):
        return f"{coord:.5f}"
    return f"{_format_coord(coords[1])}, {_format_coord(coords[0])}"

def _handle_flavor(flavor):
    return flavor if flavor else "Not specified"

def _flip_coords(coords):
    return (coords[1], coords[0])

def _handle_dist(dist):
    return f"{dist:.2f} mi"

def get_table_data(data, location="Eden Prairie"):
    table_data = []
    for item in data:
        table_data.append({
            'location': item['city'] + ', ' + item['state'],
            'flavor of the day': _handle_flavor(item['flavor']),
            'coordinates': _handle_coords(item['coordinates'])
        })
    return table_data

def create_table(data, location="Eden Prairie", coords=(45.676998, -111.042931)):
    # Create a table
    table = Table(title="Culvers Flavors of the Day Close to " + location)

    # Add columns (excluding 'hrs' and 'driveThruHrs')
    columns = ['location', 'flavor of the day', 'coordinates', 'distance']
    for column in columns:
        table.add_column(column.capitalize(), no_wrap=True)

    # Add rows
    for item in data:
        table.add_row(
            item['city'] + ', ' + item['state'],
            _handle_flavor(item['flavor']),
            _handle_coords(item['coordinates']),
            _handle_dist(distance(coords, _flip_coords(item['coordinates'])).miles)
        )

    return table

def get_table_from_zip(zip='55347'):
    json_data = get_json_from_zip(zip)
    return create_table(parse_output(json_data))

def get_data_from_zip(zip='55347'):
    json_data = get_json_from_zip(zip)
    return get_table_data(parse_output(json_data))

def get_table_from_lat_long(lat=44.8547, long=-93.4708, loc_string="Eden Prairie"):
    json_data = get_json_from_lat_long(lat, long)
    return create_table(parse_output(json_data), location=loc_string, coords=(lat, long))

def get_data_from_lat_long(lat=44.8547, long=-93.4708, loc_string="Eden Prairie"):
    json_data = get_json_from_lat_long(lat, long)
    return get_table_data(parse_output(json_data))
