import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from pipeline.pipeline import run
from ws.jobs import app

def start_pipeline():
    asyncio.run(run())

@asynccontextmanager
async def lifespan(app):
    loop = asyncio.get_running_loop()

    task = loop.run_in_executor(
        None,
        start_pipeline
    )

    yield


app.router.lifespan_context = lifespan


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )