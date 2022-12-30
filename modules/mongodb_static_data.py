import json
from pathlib import Path
class StaticData:
    with open(Path(__file__).parent.absolute()/'credential.json') as data_file:
        data = json.load(data_file)
    # database connection
    MGDB_HOST = data["MGDB_HOST"]
    MGDB_PORT = data["MGDB_PORT"]
    MGDB_USERNAME = data["MGDB_USERNAME"]
    MGDB_PASSWORD = data["MGDB_PASSWORD"]
    MGDB_DATABASE = data["MGDB_DATABASE"]