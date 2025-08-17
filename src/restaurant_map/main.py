from fastapi import FastAPI

from .config import Settings
from .routes import router

settings = Settings()

def get_app() -> FastAPI:
    """Create a FastAPI app with the specified settings."""
    app = FastAPI(**settings.fastapi_kwargs)
    app.include_router(router)
    return app


def main():
    import uvicorn
    app = get_app()
    uvicorn.run(app, host="127.0.0.1", port=8011)
