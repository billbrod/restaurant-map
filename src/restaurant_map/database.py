import tinydb
import time
import json
import re
import geopy
from random import randint
from .config import Settings

settings = Settings()
GEOLOCATOR = geopy.geocoders.Nominatim(user_agent='restaurant_map')

class DataBase:
    def __init__(self, path: str = settings.DATA_DIR / "data.json"):
        self.db = tinydb.TinyDB(path, sort_keys=True, indent=4, separators=(',', ": "))
        self.points = self.db.table("points")
        self.tags = self.db.table("tags")
        self.lists = self.db.table("lists")
        self.query = tinydb.Query()

    def get_random(self, table: str = "points"):
        table = self.db.table(table)
        num = randint(0, len(table))
        return table.get(doc_id=num)

    def find(self, key: str, value: str, table: str = "points"):
        table = self.db.table(table)
        q = getattr(self.query, key)
        return table.search(q == value)

    def search(self, key: str, value: str, table: str = "points"):
        table = self.db.table(table)
        q = getattr(self,query, key)
        return table.search(q.search(value, flags=re.IGNORECASE))

    def ingest_geojson(self, json_path: str):
        with open(json_path) as f:
            geojson = json.load(f)
        points = geojson["features"]
        last_geocode = 0
        for pt in points:
            if not pt["properties"].get("address", None):
                print(f"getting address of {pt['properties']['name']}")
                # to respect api limit of 1/second
                while time.time() < last_geocode + 1:
                    time.sleep(.1)
                pt["properties"]["address"] = self.get_address(pt)
                last_geocode = time.time()
            pt["properties"]["tags"] = pt["properties"]["tags"].split(',')
        self.points.insert_multiple(points)

    def export(self, export_path: str | None = None):
        data = {"type": "FeatureCollection"}
        data["features"] = self.points.all()
        for pt in data["features"]:
            pt["properties"]["tags"] = ",".join(pt["properties"]["tags"])
        if export_path is None:
            return json.dumps(data)
        else:
            with open(export_path, "w") as f:
                json.dump(data, f)

    def get_address(self, point):
        coords = point["geometry"]["coordinates"]
        coords = f"{coords[1]},{coords[0]}"
        return GEOLOCATOR.reverse(coords).address
