from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel, Field
from .config import get_settings
from .orchestrator import portfolio_audit, run_project_task
from .projects import PROJECTS
from .store import recent_runs


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="ERP Super Agent", version="0.1.0", lifespan=lifespan,
              description="DeepSeek-powered coordinator for 11 ERP repositories.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class TaskRequest(BaseModel):
    project_key: str
    request: str = Field(min_length=5, max_length=8000)
    role: str = "router"


@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(Path(__file__).resolve().parent.parent / "dashboard" / "index.html")


@app.get("/health")
async def health():
    settings = get_settings()
    return {"status": "ok", "model_configured": bool(settings.llm_model), "model": settings.llm_model,
            "github_configured": bool(settings.github_token), "github_writes_enabled": settings.github_write_enabled}


@app.get("/api/projects")
async def projects():
    return [{"key": p.key, "name": p.name, "repository": p.repository, "mission": p.mission} for p in PROJECTS]


@app.post("/api/audit")
async def audit():
    try:
        return await portfolio_audit()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/tasks")
async def task(payload: TaskRequest):
    try:
        return await run_project_task(payload.project_key, payload.request, payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/runs")
async def runs(limit: int = 30):
    return recent_runs(max(1, min(limit, 100)))
