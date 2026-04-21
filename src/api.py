from fastapi import FastAPI

from .core.database import database_manager

app = FastAPI(title="Pipefy Manager API")


@app.on_event("startup")
def on_startup():
    database_manager.create_tables()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)