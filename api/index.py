from flask import Flask, request, render_template_string
from rich.console import Console
from rich.columns import Columns

from api.get_culvers_locs import get_table_from_lat_long, get_data_from_lat_long, get_table_from_zip, get_data_from_zip
from api.utils import get_html_template, get_location_from_ip

app = Flask(__name__)

ASCII = """
 ______   ___   _______  ____  
|  ____| / _ \ |__   __||  _ \\
| |__   | | | |   | |   | | | |  
|  __|  | | | |   | |   | | | |
| |     | |_| |   | |   | |_| |   
|_|      \___/    |_|   |____/  
"""
LAT = 0
LONG = 1

@app.route('/', methods=['GET'])
def home():
    # Check if the request is coming from curl
    is_curl = 'curl' in request.headers.get('User-Agent', '').lower()
    user_ip = request.remote_addr

    # Check for manual location override via query params
    manual_zip = request.args.get('zip')
    manual_loc = request.args.get('loc')

    if manual_zip:
        # User provided zip code override
        location_string = f"ZIP {manual_zip}"
        use_zip_query = True
        query_location = manual_zip
    elif manual_loc:
        # User provided location string override
        location_string = manual_loc
        use_zip_query = True
        query_location = manual_loc
    else:
        # Auto-detect from IP
        try:
            location, coordinates, postal = get_location_from_ip(user_ip)

            # Prefer postal code for more precision
            if postal:
                location_string = f"{location} (ZIP {postal})"
                use_zip_query = True
                query_location = postal
            else:
                location_string = location
                use_zip_query = False
        except Exception as e:
            print(f"Error getting location: {e}")
            location = "Eden Prairie, MN"
            location_string = location
            coordinates = [44.8547, -93.4708]
            use_zip_query = False

    if is_curl:
        if use_zip_query:
            table = get_table_from_zip(zip=query_location, loc_string=location_string)
        else:
            table = get_table_from_lat_long(lat=coordinates[LAT], long=coordinates[LONG], loc_string=location_string)

        centered_table = Columns([table], align="center", expand=True)
        console = Console(record=True, width=100)

        console.print(centered_table)

        output = console.export_text(clear=False, styles=True)
        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        if use_zip_query:
            table_data = get_data_from_zip(zip=query_location, loc_string=location_string)
        else:
            table_data = get_data_from_lat_long(lat=coordinates[LAT], long=coordinates[LONG], loc_string=location_string)

        html_template = get_html_template()
        return render_template_string(html_template, table_data=table_data)