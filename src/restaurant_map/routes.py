from enum import Enum
import json
from typing import Annotated

from fastapi import APIRouter, Request, Form, Response
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


class Properties(BaseModel):
    name: str
    address: str
    description: str | None = None
    date_added: str | None = None
    id: str | None = None
    tags: list[str] | None = None


class Feature(BaseModel):
    geometry: Geometry
    properties: Properties
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


@router.get("/points.json")
def export_all_points(request: Request) -> GeoJSON:
    return db.export()


@router.get("/details/{pt_id}")
def detail_page(request: Request, pt_id: str) -> HTMLResponse:
    point = db.find("id", pt_id)[0]
    return templates.TemplateResponse(
        "details.html",
        {
            "request": request,
            "point": point,
            "tags": db.tags.all(),
            "type": "details",
        },
        block_name="content",
    )


@router.post("/details/{pt_id}")
def update_point(
        update_data: Annotated[Properties, Form()],
        pt_id: str
) -> HTMLResponse:
    db.update_point(pt_id, update_data.dict())
    point = db.find("id", pt_id)
    return templates.TemplateResponse(
        "main.html",
        {"request": [], "points": point},
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
            "tags": db.tags.all(),
            "type": "form",
        },
        block_name="content",
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
        })
