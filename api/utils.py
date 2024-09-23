import ipinfo
from dotenv import load_dotenv
import os

def _coords_string_to_list(coords):
    return [float(coord) for coord in coords.split(',')]

def get_location_from_ip(ip):
    load_dotenv()
    token = os.getenv('IPINFO_TOKEN')
    handler = ipinfo.getHandler(token)

    res = handler.getDetails(ip)

    return res.city + res.region, _coords_string_to_list(res.loc)

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
            </div>
        </body>
        </html>
        """
    return html_template