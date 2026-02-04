# 🧵 Sastre

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/sastre/)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Sastre** (Spanish for *Tailor*) is a lightweight tool designed to bridge the gap between Python backends and Astro's powerful frontend capabilities. It allows you to scaffold Astro projects and render Astro components directly from Python, making it perfect for SSR-heavy applications that want to leverage the best of both worlds.

## ✨ Features

- 🏗️ **Instant Scaffolding**: Create a pre-configured Astro project optimized for SSR with a single command.
- 🚀 **Seamless Rendering**: Render Astro views from Python using a simple API.
- 🔄 **Dynamic Data**: Pass Python dictionaries as models to your Astro components.
- ⚡ **HTMX Ready**: Easily render HTML fragments for dynamic server-side updates.
- 🛠️ **FastAPI Integration**: Easily integrate with FastAPI or any other Python web framework.

## 📦 Installation

Sastre requires **Python 3.13+** and **Node.js** (with `pnpm` installed).

```bash
pip install sastre
```

*Note: Sastre will attempt to install `pnpm` globally if it's not found during the scaffolding process.*

## 🚀 Quick Start

### 1. Scaffold a New Project

To create a new Astro project structure ready for rendering:

```bash
python -m sastre my-ui-project
```

This will create a directory named `my-ui-project` with the following structure:
- `src/views/`: Put your `.astro` components here.
- `src/pages/render.astro`: The SSR entry point for Sastre.
- `public/`: Static assets.

### 2. Render from Python

You can use the `Renderer` class to start the Astro server and render components.

**Note**: If the directory provided to `Renderer` doesn't exist or is empty, Sastre will automatically scaffold a base Astro project for you.

```python
from sastre import Renderer

# Point to your Astro project directory
renderer = Renderer(_dir="./my-ui-project")

# Start the Astro SSR server (performs 'pnpm run build' by default)
renderer.start()

# Render a view ('example' refers to src/views/example/index.astro)
html_content = renderer.render(
    view="example", 
    model={"title": "Hello from Python!"}
)

print(html_content)

# Don't forget to stop the server when done
renderer.stop()
```

The `Renderer` also supports context managers:

```python
with Renderer(_dir="./my-ui-project") as renderer:
    html = renderer("example", {"title": "Fast!"})
```

### 3. FastAPI Example

Integrating Sastre with FastAPI is straightforward using `lifespan` events:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sastre import Renderer

renderer = Renderer(_dir=str(Path("./ui").resolve()))

@asynccontextmanager
async def lifespan(_: FastAPI):
    # build=False skips the slow build step if you've already built the project
    renderer.start(build=False)
    yield
    renderer.stop()

app = FastAPI(title="Astro Renderer API", lifespan=lifespan)

@app.get("/render/{view}", response_class=HTMLResponse)
async def api(view: str):
    try:
        import asyncio
        loop = asyncio.get_running_loop()
        # renderer is sync, so we run it in an executor to avoid blocking the loop
        content = await loop.run_in_executor(None, renderer, view, {'title': 'Test Page'})
        return HTMLResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/assets", StaticFiles(directory=renderer.assets), name="assets")
app.mount("/", StaticFiles(directory=renderer.client), name="client")

```

## ⚡ HTMX Integration

Sastre makes it easy to build dynamic UIs with HTMX by rendering Astro components as HTML fragments.

```python
from sastre import Renderer, Htmx, HtmxHelper
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

renderer = Renderer(_dir="./ui")

# 1. Apply the HTMX extension to set up dependencies and examples
renderer.extension(Htmx())

# 2. Use the HtmxHelper for rendering and triggers
htmx = HtmxHelper(renderer)

app = FastAPI()


@app.post("/increment", response_class=HTMLResponse)
async def increment(request: Request):
    model = await request.json()
    # Render a specific fragment (e.g., src/views/fragments/counter.astro)
    content = htmx.render("fragments/counter.astro", model)

    # Optional: use HTMX triggers
    headers = htmx.trigger({}, "item-updated", {"id": 1})
    return HTMLResponse(content=content, headers=headers)
```

## 🧩 Pluggable Extensions

Sastre's architecture is built on a flexible extension system managed by `ExtensionManager` (automatically used by `Renderer`). You can create your own extensions or use the built-in ones.

### Built-in Extensions

- **HTMX**: `Htmx()` - Sets up HTMX dependencies and example fragments.
- **Tailwind**: `Tailwind()` - Integrates Tailwind CSS v4.
- **Alpine**: `Alpine()` - Adds Alpine.js integration.
- **React**: `React()` - Adds React integration.
- **Svelte**: `Svelte()` - Adds Svelte integration.
- **Vue**: `Vue()` - Adds Vue integration.
- **Lucide**: `Lucide()` - Adds `lucide-astro` for icons.

### Using Multiple Extensions

Sastre is designed to be elastic. You can apply multiple extensions to the same project.

```python
from sastre import Renderer, Tailwind, Vue, Htmx

renderer = Renderer(_dir="./ui")

# Apply multiple extensions
renderer.extension(Tailwind())
renderer.extension(Vue())
renderer.extension(Htmx())
```

### Creating a Custom Extension

```python
from sastre import BaseExtension
from pathlib import Path


class TailwindExtension(BaseExtension):
    def name(self):
        return "Tailwind"

    def dev_dependencies(self):
        return {
            "tailwindcss": "^3.4.1",
            "@astrojs/tailwind": "^5.1.0"
        }

    def setup(self, project_dir: Path):
        # Add tailwind config or modify astro.config.mjs here
        config_path = project_dir / "tailwind.config.mjs"
        config_path.write_text("export default { ... }")


# Apply it
renderer._apply_extension(TailwindExtension())
```

### 🔢 Dynamic Pagination Example

You can implement dynamic pagination by combining HTMX with Astro fragments.

**1. Create a fragment (`src/views/fragments/list.astro`):**
```astro
---
const { items, page, totalPages } = Astro.props;
---
<div id="list-container">
  <ul>
    {items.map(item => <li>{item}</li>)}
  </ul>
  <button hx-post="/list" hx-vals={`{"page": ${page + 1}}`} hx-target="#list-container" hx-swap="outerHTML">
    Next Page
  </button>
</div>
```

**2. Handle it in Python:**
```python
@app.post("/list")
async def get_list(request: Request):
    data = await request.json()
    page = data.get("page", 1)
    # ... logic to fetch your items for the page ...
    return HTMLResponse(htmx.render("fragments/list.astro", {
        "items": items,
        "page": page,
        "totalPages": 10
    }))
```

## 🛠️ How it Works

Sastre sets up an Astro project with an adapter (Node.js) in standalone mode. It includes a special `render.astro` page that accepts `POST` requests. When you call `renderer.render()` in Python, it sends a JSON payload to this page, which dynamically imports the requested view and renders it with the provided model.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ for the Python and Astro communities.
