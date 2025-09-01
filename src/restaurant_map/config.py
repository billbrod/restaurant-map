from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings
from typing import Any

APP_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):

    APP_DIR: Path = APP_DIR

    STATIC_DIR: Path = APP_DIR / 'static'
    TEMPLATE_DIR: Path = APP_DIR / 'templates'
    DATA_DIR: Path = APP_DIR.parent.parent / 'data'

    FASTAPI_PROPERTIES: dict[str, Any] = {
        "title": "Restauranter",
        "description": "Simple site for viewing and editing restaurants",
        "version": "0.1.0",
    }

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        """Creates dictionary of values to pass to FastAPI app
        as **kwargs.

        Returns:
            dict: This can be unpacked as **kwargs to pass to FastAPI app.
        """
        fastapi_kwargs = self.FASTAPI_PROPERTIES
        return fastapi_kwargs
