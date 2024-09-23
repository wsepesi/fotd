from flask import Flask
from rich.console import Console
from rich.align import Align
from rich.columns import Columns

from api.get_culvers_locs import get_table_from_zip

app = Flask(__name__)

@app.route('/')
def home():
    table = get_table_from_zip()
    centered_table = Columns([table], align="center", expand=True)

    # Capture the console output
    console = Console(record=True, width=100)
    console.print(centered_table)
    
    # Get the captured output as a string
    output = console.export_text(clear=False, styles=True)
    
    # Return the output as plain text
    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}