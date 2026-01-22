from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sastre import Renderer

renderer = Renderer(_dir=str(Path("./ui").resolve()))


@asynccontextmanager
async def lifespan(_: FastAPI):
    renderer.start()
    yield
    renderer.stop()


app = FastAPI(title="Astro Renderer API", lifespan=lifespan)


@app.get("/render/{view}", response_class=HTMLResponse)
def api(view: str):
    try:
        return HTMLResponse(content=renderer(view, {'title': 'Test Page'}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/assets", StaticFiles(directory=renderer.assets), name="assets")
app.mount("/", StaticFiles(directory=renderer.client), name="client")
