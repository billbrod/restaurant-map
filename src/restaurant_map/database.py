import tinydb
import hashlib
from datetime import datetime
import time
import json
import re
import geopy
from random import randint
from .config import Settings

# from https://cmap-docs.readthedocs.io/en/latest/catalog/qualitative/seaborn:tab10_new/
SEABORN_TAB10 = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14e",
    "#edc949",
    "#af7aa1",
    "#ff9da7",
    "#9c755f",
]

settings = Settings()
GEOLOCATOR = geopy.geocoders.Nominatim(user_agent='restaurant_map')

class DataBase:
    def __init__(self, path: str = settings.DATA_DIR / "data.json"):
        self.db = tinydb.TinyDB(path, sort_keys=True, indent=4, separators=(',', ": "))
        self.points = self.db.table("points")
        self.tags = self.db.table("tags")
        self.lists = self.db.table("lists")
        self.point_query = tinydb.Query().properties
        self.query = tinydb.Query()

    def get_random(self, table: str = "points"):
        table = self.db.table(table)
        num = randint(0, len(table))
        return table.get(doc_id=num)

    def find(self, key: str, value: str, table: str = "points",
             case_sensitive: bool = False):
        if table == "points":
            q = getattr(self.point_query, key)
        else:
            q = getattr(self.query, key)
        table = self.db.table(table)
        if not case_sensitive:
            flags = re.IGNORECASE
        else:
            flags = None
        return table.search(q.search(value, flags=flags))

    def find_tags(self, tags: str | list[str]) -> list[dict]:
        q = self.point_query.tags.any(tags)
        return self.points.search(q)

    def ingest_geojson(self, json_path: str):
        with open(json_path) as f:
            geojson = json.load(f)
        points = geojson["features"]
        last_geocode = 0
        for pt in points:
            pt["properties"]["date_added"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            coords = str(pt["geometry"]["coordinates"])
            pt_id = hashlib.sha256(coords.encode()).hexdigest()
            pt["properties"]["id"] = pt_id
            if not pt["properties"].get("address", None):
                print(f"getting address of {pt['properties']['name']}")
                # to respect api limit of 1/second
                while time.time() < last_geocode + 1:
                    time.sleep(.1)
                pt["properties"]["address"] = self.get_address(pt)
                last_geocode = time.time()
            try:
                tags = pt["properties"]["tags"].split(',')
            except AttributeError:
                # then this is already a list
                pass
            pt["properties"]["tags"] = tags
            for tag in tags:
                if not self.tags.contains(self.query.name == tag):
                    print(f"Adding new tag {tag}...")
                    self.tags.insert({"name": tag, "color": SEABORN_TAB10[len(self.tags.all()) % 9]})
        self.points.insert_multiple(points)

    def export(
            self,
            export_path: str | None = None,
            geojson: bool = True,
    ):
        data = self.points.all()
        if geojson:
            data = {"type": "FeatureCollection", "features": data}
        if export_path is None:
            return data
        else:
            with open(export_path, "w") as f:
                json.dump(data, f)

    def get_address(self, point: dict) -> str:
        coords = point["geometry"]["coordinates"]
        coords = f"{coords[1]},{coords[0]}"
        return GEOLOCATOR.reverse(coords).address

    def rename_tag(self, old_tag: str, new_tag: str):
        self.tags.update({"name": new_tag}, self.query.name == old_tag)
        def update_tag(old_tag, new_tag):
            def transform(doc):
                try:
                    doc["properties"]["tags"].remove(old_tag)
                    doc["properties"]["tags"].append(new_tag)
                except ValueError:
                    pass
            return transform
        self.points.update(update_tag(old_tag, new_tag))

    def update_point(self, pt_id: str, data: dict):
        def update_properties(new_properties):
            # this will overwrite specified fields, but leave those unincluded
            # or with None values untouched
            def transform(doc):
                new_props = {k: v for k, v in new_properties.items() if v is not None}
                doc["properties"].update(new_props)
            return transform
        self.points.update(update_properties(data),
                           self.point_query.id == pt_id)
