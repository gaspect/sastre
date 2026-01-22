# 🧵 Sastre

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/sastre/)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Sastre** (Spanish for *Tailor*) is a lightweight tool designed to bridge the gap between Python backends and Astro's powerful frontend capabilities. It allows you to scaffold Astro projects and render Astro components directly from Python, making it perfect for SSR-heavy applications that want to leverage the best of both worlds.

## ✨ Features

- 🏗️ **Instant Scaffolding**: Create a pre-configured Astro project optimized for SSR with a single command.
- 🚀 **Seamless Rendering**: Render Astro views from Python using a simple API.
- 🔄 **Dynamic Data**: Pass Python dictionaries as models to your Astro components.
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

```python
from sastre import Renderer

# Point to your Astro project directory
renderer = Renderer(_dir="./my-ui-project")

# Start the Astro SSR server
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

```

## 🛠️ How it Works

Sastre sets up an Astro project with an adapter (Node.js) in standalone mode. It includes a special `render.astro` page that accepts `POST` requests. When you call `renderer.render()` in Python, it sends a JSON payload to this page, which dynamically imports the requested view and renders it with the provided model.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ for the Python and Astro communities.
