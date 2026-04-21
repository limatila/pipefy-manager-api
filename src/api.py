from contextlib import asynccontextmanager

from fastapi import FastAPI

from .core.database import database_manager
from .core.config import IS_CREATE_DEMO_API_STARTUP
from .routers import persons_router, pipefy_management_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    database_manager.create_tables()

    if IS_CREATE_DEMO_API_STARTUP:
        database_manager.create_demo_api_person()

    # API runtime
    yield


app = FastAPI(title="Pipefy Manager API", lifespan=lifespan)

#* Routers
app.include_router(persons_router)
app.include_router(pipefy_management_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)