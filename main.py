import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import Base, engine
from routers import auth, members


# Lifespan contxt manager for startup/shutdown events
@asynccontextmanager
async def lifespan():
    # Startup: Creates DB Tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown:


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="JARAM Member Service",
    description="Member management service for JARAM homepage",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(members.router)
app.include_router(auth.router)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "service": "JARAM Member Service",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
