from enum import Enum
import time
import json
from typing import Annotated

from fastapi import APIRouter, Request, Form, Response, Query
from fastapi.responses import HTMLResponse
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import BaseModel

from .config import Settings
from .database import DataBase

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)
router = APIRouter()
db = DataBase()


class Geometry(BaseModel):
    coordinates: list[float]
    type: str


class DisplayProps(BaseModel):
    color: str


class BaseProperties(BaseModel):
    name: str
    address: str
    description: str | None = None
    date_added: str | None = None
    id: str | None = None
    tags: list[str] | None = None


class DisplayProperties(BaseProperties):
    display: DisplayProps | None = None


class FormProperties(BaseProperties):
    add_tag: str | None = None


class ShowProperties(BaseProperties):
    filter_text: list[str] | None = []

class Feature(BaseModel):
    geometry: Geometry
    properties: DisplayProperties
    type: str


class GeoJSON(BaseModel):
    type: str
    features: list[Feature]


class BasePages(str, Enum):
    index_pg = "index"
    map_pg = "map"
    list_pg = "list"


@router.get("/point/{pt_id}")
def export_single_point(request: Request, pt_id: str) -> Feature:
    p = db.find("id", pt_id)[0]
    return p


@router.delete("/tags/{pt_id}")
def delete_tag(
        request: Request,
        pt_id: str,
) -> HTMLResponse:
    tag = request.headers.get("HX-Trigger")
    point = db.find("id", pt_id)[0]
    point["properties"]["tags"].remove(tag)
    db.update_point(pt_id, point["properties"])
    if not db.find_tags(tag):
        db.remove_tags(tag)
    # return empty body so we remove element
    return Response()

@router.post("/tags/{pt_id}")
def update_tags(
        request: Request,
        update_data: Annotated[FormProperties, Form()],
        pt_id: str,
) -> HTMLResponse:
    new_tag = update_data.add_tag
    point = db.find("id", pt_id)[0]
    if new_tag not in point["properties"]["tags"]:
        point["properties"]["tags"].append(new_tag)
        db.update_point(pt_id, point["properties"])
        point = db.find("id", pt_id)[0]
    return templates.TemplateResponse(
        "details.html",
        {
            "request": request,
            "point": point,
            "type": "form",
        },
        block_name="tags"
    )


@router.get("/tags.css")
def get_tag_css(
        request: Request,
) -> HTMLResponse:
    # sleep so that update tags can happen first
    time.sleep(.1)
    return templates.TemplateResponse(
        "shared/_base.html",
        {
            "request": request,
            "tags": db.tags.all(),
        },
        block_name="tag_css"
    )


@router.get("/add_tags")
def get_add_tags(
        request: Request,
) -> HTMLResponse:
    time.sleep(.1)
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "tags": db.tags.all(),
            "show_add_tags": True,
        },
        block_name="add_tags"
    )


@router.get("/tags")
def get_tags_list(
        request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        "tags_select.html",
        {
            "request": request,
            "tags": db.tags.all(),
        }
    )


@router.get("/points.json")
def export_points(
        request: Request,
        add_tags: str = "",
        filter_tags_include: Annotated[list[str], Query()] = [],
        filter_tags_exclude: Annotated[list[str], Query()] = [],
) -> GeoJSON:
    points = db.find_tags(filter_tags_include, filter_tags_exclude, geojson=True)
    tags = db.export(geojson=False, table="tags")
    tags = {"color": {t["name"]: t["color"] for t in tags}}
    add_tags = add_tags.split(",")
    if add_tags == [""]:
        add_tags = []
    for tag in add_tags:
        for pt in points["features"]:
            pt_tag = tags[tag][pt["properties"]["tags"][-1]]
            try:
                pt["properties"]["display"][tag] = pt_tag
            except KeyError:
                pt["properties"]["display"] = {tag: pt_tag}
    return points

def render_points_list(
        request: Request,
        filter_text: list[str] = [],
        filter_tags_include: list[str] = [],
        filter_tags_exclude: list[str] = [],
        selected: list[str] = [],
) -> HTMLResponse:
    points = db.find_tags(filter_tags_include, filter_tags_exclude)
    if request.headers.get("hx-current-url", "list").endswith("list"):
        subgrid = "col-span-4"
    else:
        subgrid = "col-span-1"
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "points": points,
            "show_tags": "tags" in filter_text,
            "show_date_added": "date_added" in filter_text,
            "show_id": "id" in filter_text,
            "show_address": "address" in filter_text,
            "show_description": "description" in filter_text,
            "subgrid": subgrid,
            "selected": selected,
        },
        block_name="point_list",
    )


@router.post("/points_list")
def update_points_list(
        request: Request,
        filter_text: Annotated[list[str] | None, Form()] = [],
        filter_tags_include: Annotated[list[str] | None, Form()] = [],
        filter_tags_exclude: Annotated[list[str] | None, Form()] = [],
        add_tag_input: Annotated[list[str] | None, Form()] = [],
        add_tags_include: Annotated[list[str] | None, Form()] = [],
        add_tags_exclude: Annotated[list[str] | None, Form()] = [],
        point_select_checkbox: Annotated[list[str] | None, Form()] = [],
) -> HTMLResponse:
    tags = [t for t in add_tags_include + add_tag_input if t]
    db.bulk_update_tags(point_select_checkbox, tags, add_tags_exclude)
    return render_points_list(request, filter_text,
                              filter_tags_include, filter_tags_exclude,
                              point_select_checkbox)

@router.get("/points_list")
def points_list(
        request: Request,
        filter_text: Annotated[list[str] | None, Query()] = [],
        filter_tags_include: Annotated[list[str] | None, Query()] = [],
        filter_tags_exclude: Annotated[list[str] | None, Query()] = [],
) -> HTMLResponse:
    return render_points_list(request, filter_text,
                              filter_tags_include,
                              filter_tags_exclude)


@router.get("/details/{pt_id}")
def detail_page(request: Request, pt_id: str) -> HTMLResponse:
    point = db.find("id", pt_id)[0]
    return templates.TemplateResponse(
        "details.html",
        {
            "request": request,
            "point": point,
            "type": "details",
        },
    )


@router.post("/details/{pt_id}")
def update_point(
        request: Request,
        update_data: Annotated[ShowProperties, Form()],
        pt_id: str,
) -> HTMLResponse:
    update_data = update_data.dict()
    filter_text = update_data.pop("filter_text", [])
    db.update_point(pt_id, update_data)
    point = db.find("id", pt_id)
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "points": point,
            "show_tags": "tags" in filter_text,
            "show_date_added": "date_added" in filter_text,
            "show_id": "id" in filter_text,
            "show_address": "address" in filter_text,
            "show_description": "description" in filter_text,
        },
        block_name="point_entry",
    )


@router.get("/details/{pt_id}/edit")
def edit_point(request: Request, pt_id: str) -> HTMLResponse:
    point = db.find("id", pt_id)[0]
    return templates.TemplateResponse(
        "details.html",
        {
            "request": request,
            "point": point,
            "type": "form",
        },
    )


# this needs to be last: it will grab everything else
@router.get("/{page_path}")
def full_pages(request: Request, page_path: BasePages) -> HTMLResponse:
    if page_path is BasePages.index_pg:
        pg_type = "both"
    elif page_path is BasePages.map_pg:
        pg_type = "map"
    elif page_path is BasePages.list_pg:
        pg_type = "list"
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "points": db.points.all(),
            "tags": db.tags.all(),
            "type": pg_type,
            "filter_targets": [k for k in BaseProperties.__fields__ if k not in ["name"]],
            "show_tags": True,
            "show_date_added": False,
            "show_id": False,
            "show_address": True,
            "show_description": True,
        })
