from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.database import database_manager
from .core.config import IS_CREATE_DEMO_API_STARTUP, PIPE_ID
from .routers import cards_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    database_manager.create_tables()

    if IS_CREATE_DEMO_API_STARTUP:
        database_manager.create_demo_api_person()

    # API runtime
    yield

app_description = (
    "API for managing cards in Pipefy, allowing you to create, update, and delete cards within a specific pipe."
    f"\n - Active Pipe Id: {PIPE_ID}"
)
app = FastAPI(title="Pipefy Manager API", lifespan=lifespan, description=app_description)

#* Routers
app.include_router(cards_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)