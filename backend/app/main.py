from contextlib import asynccontextmanager
from fastapi import FastAPI
from .config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify settings are loaded on startup
    print(f"[{settings.ENVIRONMENT}] Application '{settings.PROJECT_NAME}' starting...")
    # In a real app, this is where you'd initialize DB connections, etc.
    yield
    print(f"[{settings.ENVIRONMENT}] Application '{settings.PROJECT_NAME}' shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME, 
    description="AI-powered trading system API",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}", 
        "status": "running",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
