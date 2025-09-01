from fastapi import APIRouter, Request
from jinja2_fragments.fastapi import Jinja2Blocks

from .config import Settings
from .database import DataBase

settings = Settings()
templates = Jinja2Blocks(directory=settings.TEMPLATE_DIR)
router = APIRouter()
db = DataBase()

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "points": db.points.all(),
            "tags": db.tags.all(),
            "type": "both",
        })


@router.get("/map")
def map_only(request: Request):
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "points": db.points.all(),
            "tags": db.tags.all(),
            "type": "map",
        })


@router.get("/list")
def list_only(request: Request):
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "points": db.points.all(),
            "tags": db.tags.all(),
            "type": "list",
        })


@router.get("/points.json")
def export_points(request: Request):
    return db.export()


@router.get("/details")
def details(request: Request):
    try:
        pt_id = request.headers.get("HX-Trigger").replace("info-", "")
        point = db.find("id", pt_id)[0]
    except AttributeError:
        point = db.get_random()
    print(point)
    return templates.TemplateResponse(
        "details.html",
        {
            "request": request,
            "point": point,
            "tags": db.tags.all(),
        }
    )
