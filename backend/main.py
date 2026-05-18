import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.api.orchestrate.intent import router as intent_router
from src.api.orchestrate.matching import router as matching_router
from src.api.orchestrate.pricing import router as pricing_router
from src.api.orchestrate.booking import router as booking_router
from src.api.orchestrate.unified import router as unified_router

app = FastAPI(
    title="AI Service Orchestrator API",
    description="Core backend for orchestrating AI intents and matching providers.",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "templates"))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register core orchestration routers
app.include_router(intent_router)
app.include_router(matching_router)
app.include_router(pricing_router)
app.include_router(booking_router)
app.include_router(unified_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the sleek UI dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})
