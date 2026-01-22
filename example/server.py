from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sastre import Renderer

ASTRO_PROJECT_DIR = Path("../ui").resolve()

renderer = Renderer(_dir=str(ASTRO_PROJECT_DIR))


@asynccontextmanager
async def lifespan(_: FastAPI):
    renderer.start()
    yield
    renderer.stop()


app = FastAPI(title="Astro Renderer API", lifespan=lifespan)


# Instancia global del Renderer


def render(view, model):
    return HTMLResponse(content=renderer.render(view, model))


@app.get("/render/{view}", response_class=HTMLResponse)
def api(view: str):
    try:
        return render(view, {'name': 'Mónica' })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

# Monta assets estáticos (public/) en /assets
app.mount("/assets", StaticFiles(directory=ASTRO_PROJECT_DIR / "public"), name="assets")
app.mount("/", StaticFiles(directory=ASTRO_PROJECT_DIR / "dist/client"), name="client")
