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

    def find_tags(
            self,
            include_tags: str | list[str] = [],
            exclude_tags: str | list[str] = [],
            geojson: bool = False,
    ) -> list[dict]:
        not_q = self.point_query.tags.any(exclude_tags)
        if include_tags:
            q = self.point_query.tags.all(include_tags)
            data = self.points.search(q & ~not_q)
        else:
            data = self.points.search(~not_q)
        if geojson:
            data = {"type": "FeatureCollection", "features": data}
        return data

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
            self.add_tags(tags)
        self.points.insert_multiple(points)

    def export(
            self,
            export_path: str | None = None,
            geojson: bool = True,
            table: str = "points",
    ):
        data = self.db.table(table).all()
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

    def bulk_update_tags(self, pt_ids: list[str], tags_add: list[str], tags_remove: list[str]):
        def update_tag():
            # this will overwrite specified fields, but leave those unincluded
            # or with None values untouched
            def transform(doc):
                for tag in tags_add:
                    if tag not in doc["properties"]["tags"]:
                        doc["properties"]["tags"].append(tag)
                for tag in tags_remove:
                    if tag in doc["properties"]["tags"]:
                        doc["properties"]["tags"].remove(tag)
            return transform
        self.points.update(update_tag(), self.point_query.id.one_of(pt_ids))
        self.add_tags(tags_add)

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
        if "tags" in data and data["tags"] is not None:
            self.add_tags(data["tags"])

    def add_tags(self, new_tags: str | list[str]):
        if isinstance(new_tags, str):
            new_tags = [new_tags]
        for tag in new_tags:
            if not self.tags.search(self.query.name == tag):
                self.tags.insert({"name": tag,
                                  "color": SEABORN_TAB10[len(self.tags.all()) % 9],
                                  "css_name": tag.replace(' ', '-').lower(),
                                  })

    def remove_tags(self, tags: str | list[str]):
        if isinstance(tags, str):
            tags = [tags]
        for tag in tags:
            self.tags.remove(self.query.name == tag)
            for pt in self.find_tags(tag):
                props = pt["properties"]
                props["tags"].remove(tag)
                self.update_point(props["id"], props)
