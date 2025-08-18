import tinydb
import json
import re
from random import randint
from .config import Settings

settings = Settings()

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
        self.points.insert_multiple(geojson["features"])

    def export(self, export_path: str | None = None):
        data = {"type": "FeatureCollection"}
        data["features"] = self.points.all()
        if export_path is None:
            return json.dumps(data)
        else:
            with open(export_path, "w") as f:
                json.dump(data, f)
