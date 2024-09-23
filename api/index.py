from flask import Flask, request, render_template_string
from rich.console import Console
from rich.columns import Columns

from api.get_culvers_locs import get_table_from_zip, get_data_from_zip

app = Flask(__name__)

ASCII = """
 ______   ___   _______  ____  
|  ____| / _ \ |__   __||  _ \\
| |__   | | | |   | |   | | | |  
|  __|  | | | |   | |   | | | |
| |     | |_| |   | |   | |_| |   
|_|      \___/    |_|   |____/  
"""

@app.route('/')
def home():
    # Check if the request is coming from curl
    user_agent = request.headers.get('User-Agent', '').lower()
    is_curl = 'curl' in user_agent

    if is_curl:
        table = get_table_from_zip()
        centered_table = Columns([table], align="center", expand=True)
        # For curl requests, return plain text
        console = Console(record=True, width=100)
        # console.print(ASCII)
        console.print(centered_table)
        output = console.export_text(clear=False, styles=True)
        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        table_data = get_data_from_zip()
        # For browser requests, return terminal-like HTML
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
        return render_template_string(html_template, table_data=table_data)