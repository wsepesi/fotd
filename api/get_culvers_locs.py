import requests

from rich.console import Console
from rich.table import Table
from rich.align import Align

def get_json_from_lat_long(lat, long, radius=40233, limit=10):
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

def get_json_from_zip(location, radius=40233, limit=10):
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

def create_table(data, location="Eden Prairie"):
    # Create a table
    table = Table(title="Flavors of the Day close to " + location)

    # Add columns (excluding 'hrs' and 'driveThruHrs')
    columns = ['location', 'flavor of the day', 'coordinates'] #, 'fotdSlug', 'coordinates']
    for column in columns:
        table.add_column(column.capitalize(), style="black", no_wrap=True)

    # Add rows
    for item in data:
        table.add_row(
            # item['description'],
            item['city'] + ', ' + item['state'],
            _handle_flavor(item['flavor']),
            # item['fotdSlug'],
            _handle_coords(item['coordinates'])
        )

    return table

def get_table_from_zip(zip='55347'):
    json_data = get_json_from_zip(zip)
    return create_table(parse_output(json_data))

# if __name__ == '__main__':
#     location = '55347'
#     json_data = get_json_from_zip(location)
#     create_table(parse_output(json_data))
