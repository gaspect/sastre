from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sastre import Renderer, Htmx, HtmxHelper

renderer = Renderer(_dir=str(Path("./ui").resolve()))
renderer.extension(Htmx())
htmx = HtmxHelper(renderer)


@asynccontextmanager
async def lifespan(_: FastAPI):
    renderer.start(build=False) # Skip build if already built
    yield
    renderer.stop()


app = FastAPI(title="Astro Renderer API", lifespan=lifespan)


@app.get("/render/{view}", response_class=HTMLResponse)
async def api(view: str):
    try:
        import asyncio
        loop = asyncio.get_running_loop()
        content = await loop.run_in_executor(None, renderer, view, {'title': 'Sastre + HTMX'})
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render-fragment/{fragment}", response_class=HTMLResponse)
async def fragment_api(fragment: str, request: Request):
    try:
        # Get model from request body if available
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            model = await request.json()
        elif "application/x-www-form-urlencoded" in content_type:
            form_data = await request.form()
            model = dict(form_data)
        else:
            # Fallback or empty model
            body = await request.body()
            model = {}
            if body:
                try:
                    import json
                    model = json.loads(body)
                except:
                    pass
        
        # Specific logic for pagination fragment
        if fragment == "pagination":
            page = int(model.get("page", 1))
            page_size = 5
            all_items = [f"Item {i}" for i in range(1, 26)] # 25 items
            total_pages = (len(all_items) + page_size - 1) // page_size
            
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            model = {
                "items": all_items[start_idx:end_idx],
                "page": page,
                "totalPages": total_pages
            }
        view_path = f"fragments/{fragment}.astro"
        content = htmx.render(view_path, model)
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/assets", StaticFiles(directory=renderer.assets), name="assets")
app.mount("/", StaticFiles(directory=renderer.client), name="client")
