"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from app.database import init_db
from app.api.routes_offers import router

# Initialize database on startup
init_db()

# Create FastAPI app
app = FastAPI(
    title="Job Offers Scraper API",
    description="Scraper for collecting job practice offers from Chilean job portals",
    version="0.1.0",
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on app startup.
    """
    init_db()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
