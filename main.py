import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import engine
from models import link, member, skill
from routers import auth, members

# Create database tables
models = [member.Member, skill.Skill, link.Link]
for model in models:
    model.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="JARAM Member Service",
    description="Member management service for JARAM homepage",
    version="0.1.0",
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
