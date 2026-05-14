"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .config import settings
from .routers.api import router as api_router

app = FastAPI(title=settings.APP_TITLE, docs_url="/docs")
app.include_router(api_router)

_BASE = Path(__file__).parent
templates = Jinja2Templates(directory=str(_BASE / "templates"))


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "app_title": settings.APP_TITLE,
        "refresh_interval": settings.REFRESH_INTERVAL_SECONDS,
        "demo_mode": settings.DEMO_MODE or not settings.azure_configured,
    })
