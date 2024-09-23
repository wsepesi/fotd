from flask import Flask, request, render_template_string
from rich.console import Console
from rich.columns import Columns

from api.get_culvers_locs import get_table_from_lat_long, get_data_from_lat_long
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

    try:
        location, coordinates = get_location_from_ip(user_ip)
    except Exception as e:
        print(f"Error getting location: {e}")
        location, coordinates = "Eden Prairie", [44.8547, -93.4708]

    if is_curl:
        table = get_table_from_lat_long(lat=coordinates[LAT], long=coordinates[LONG], loc_string=location)
        centered_table = Columns([table], align="center", expand=True)
        console = Console(record=True, width=100)

        console.print(centered_table)

        output = console.export_text(clear=False, styles=True)
        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        table_data = get_data_from_lat_long(lat=coordinates[LAT], long=coordinates[LONG], loc_string=location)
        html_template = get_html_template()
        return render_template_string(html_template, table_data=table_data)