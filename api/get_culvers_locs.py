import requests

from rich.table import Table
from rich import box
from itertools import groupby
from geopy.distance import distance


def get_json_from_lat_long(lat, long, radius=600000, limit=10):
    # lat, long = (43.06105, -89.50676)
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
    # Calculate distances and sort data
    for item in data:
        item['distance'] = distance(coords, _flip_coords(item['coordinates'])).miles
    
    sorted_data = sorted(data, key=lambda x: (x['city'], x['state'], x['distance']))
    
    # Group the data by city and state
    grouped_data = groupby(sorted_data, key=lambda x: (x['city'], x['state']))
    
    # Create the main table
    main_table = Table(title=f"Culvers Flavors of the Day Close to {location}", box=box.SQUARE)
    main_table.add_column("Location", no_wrap=True)
    main_table.add_column("Flavor of the day")
    main_table.add_column("Coordinates")
    main_table.add_column("Distance", justify="right")
    
    # Sort cities by their closest location
    city_distances = []
    for (city, state), group in grouped_data:
        group_list = list(group)
        min_distance = min(item['distance'] for item in group_list)
        city_distances.append(((city, state), group_list, min_distance))
    
    city_distances.sort(key=lambda x: x[2])
    
    for (city, state), group_list, _ in city_distances:
        if len(group_list) == 1:
            # Single location in the city
            item = group_list[0]
            if "Coming Soon!" not in item['description']:
                main_table.add_row(
                    f"[bold]{city}, {state}[/bold]",
                    _handle_flavor(item['flavor']),
                    _handle_coords(item['coordinates']),
                    _handle_dist(item['distance'])
                )
        else:
            # Multiple locations in the city
            main_table.add_row(f"[bold]{city}, {state}[/bold]", "", "", "")
            for item in group_list:
                if "Coming Soon!" not in item['description']:
                    road = item['description'].split(' - ')[-1]
                    main_table.add_row(
                        f"  {road}",
                        _handle_flavor(item['flavor']),
                        _handle_coords(item['coordinates']),
                        _handle_dist(item['distance'])
                    )
    
    return main_table

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
