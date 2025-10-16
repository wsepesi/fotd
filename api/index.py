from flask import Flask, request, render_template_string
from rich.console import Console
from rich.columns import Columns

from api.get_culvers_locs import get_table_from_lat_long, get_data_from_lat_long, get_table_from_zip, get_data_from_zip
from api.utils import get_html_template, get_location_with_consensus

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
        is_confident = True  # User-provided location is always confident
    elif manual_loc:
        # User provided location string override
        location_string = manual_loc
        use_zip_query = True
        query_location = manual_loc
        is_confident = True  # User-provided location is always confident
    else:
        # Auto-detect from IP using lat/long with dual-provider consensus
        try:
            location_string, coordinates, is_confident = get_location_with_consensus(user_ip)
            use_zip_query = False
        except Exception as e:
            print(f"Error getting location: {e}")
            location_string = "Eden Prairie, MN"
            coordinates = [44.8547, -93.4708]
            is_confident = False
            use_zip_query = False

    if is_curl:
        if use_zip_query:
            table = get_table_from_zip(zip=query_location, loc_string=location_string)
        else:
            table = get_table_from_lat_long(lat=coordinates[LAT], long=coordinates[LONG], loc_string=location_string)

        centered_table = Columns([table], align="center", expand=True)
        console = Console(record=True, width=100)

        console.print(centered_table)

        # Add low-confidence warning if IP-based detection disagrees between providers
        if not is_confident and not use_zip_query:
            console.print("\n[dim]Location based on ISP routing. For accurate results, add ?zip=YOUR_ZIP[/dim]", justify="center")

        output = console.export_text(clear=False, styles=True)
        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        if use_zip_query:
            table_data = get_data_from_zip(zip=query_location, loc_string=location_string)
        else:
            table_data = get_data_from_lat_long(lat=coordinates[LAT], long=coordinates[LONG], loc_string=location_string)

        html_template = get_html_template()
        show_warning = not is_confident and not use_zip_query
        return render_template_string(html_template, table_data=table_data, show_warning=show_warning)