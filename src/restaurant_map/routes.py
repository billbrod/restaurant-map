from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from .config import Settings
from .database import DataBase

settings = Settings()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
router = APIRouter()

@router.get("/")
def index(request: Request):
    db = DataBase()
    return templates.TemplateResponse("main.html", {"request": request, "points": db.points.all()})


@router.get("/about")
def about(request: Request):
    """About page - some background information about this app."""
    return templates.TemplateResponse("about.html", {"request": request})
