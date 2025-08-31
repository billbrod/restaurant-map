from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from .config import Settings
from .database import DataBase

settings = Settings()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
router = APIRouter()
db = DataBase()

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("main.html",
                                      {
                                          "request": request,
                                          "points": db.points.all(),
                                          "tags": db.tags.all(),
                                          "type": "both",
                                       })


@router.get("/map")
def map_only(request: Request):
    return templates.TemplateResponse("main.html",
                                      {
                                          "request": request,
                                          "points": db.points.all(),
                                          "tags": db.tags.all(),
                                          "type": "map",
                                       })


@router.get("/list")
def list_only(request: Request):
    return templates.TemplateResponse("main.html",
                                      {
                                          "request": request,
                                          "points": db.points.all(),
                                          "tags": db.tags.all(),
                                          "type": "list",
                                       })

@router.get("/points.json")
def export_points(request: Request):
    return db.export()
