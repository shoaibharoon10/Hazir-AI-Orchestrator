from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.orchestrate.intent import router as intent_router
from src.api.orchestrate.matching import router as matching_router
from src.api.orchestrate.pricing import router as pricing_router

app = FastAPI(
    title="AI Service Orchestrator API",
    description="Core backend for orchestrating AI intents and matching providers.",
    version="1.0.0"
)

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

@app.get("/health")
def health_check():
    return {"status": "healthy"}
