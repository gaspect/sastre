import subprocess
import json
from pathlib import Path

_ASTRO_BASE_PACKAGE = {
    "name": "astro-renderer",
    "version": "0.1.0",
    "type": "module",
    "scripts": {
        "dev": "astro dev",
        "build": "astro build",
        "preview": "astro preview",
        "start": "node ./dist/server/entry.mjs"
    },
    "dependencies": {
        "astro": "^5.16.14"
    },
    "devDependencies": {
        "@astrojs/node": "^9.5.2"
    }
}

ASTRO_CONFIG = """import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  publicDir: 'public',
});
"""

_EXAMPLE_STYLE = """body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  margin: 0;
  padding: 20px;
}

main {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.counter-container, .pagination-example {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}

button {
  padding: 5px 15px;
  cursor: pointer;
}
"""

_RENDER_PAGE = """---
let payload = {};

if (Astro.request.method === 'POST') {
  const contentType = Astro.request.headers.get('content-type') ?? '';
  if (!contentType.includes('application/json')) {
    throw new Error('Content-Type debe ser application/json');
  }
  payload = await Astro.request.json();
}

const { view, model } = payload;

if (!view) {
  throw new Error('Missing "view" in the JSON body');
}

const viewModules = import.meta.glob('../views/**/*.astro');

const viewKey = view.includes('.') ? `../views/${view}` : `../views/${view}/index.astro`;
const loadView = viewModules[viewKey];

if (!loadView) {
  throw new Error(`View not found: ${view}`);
}

const Page = (await loadView()).default;

let props = {};
if (model && typeof model === 'object') props = model;
if (typeof model === 'string') {
  try {
    props = JSON.parse(model);
  } catch {
    throw new Error('The model field must be a valid JSON string or an object');
  }
}
---

<Page {...props} />
"""


class Scaffold:
    def __init__(self, _dir: str):
        self._path = Path(_dir).resolve()

    def dirs(self):
        dirs = [
            self._path / "src" / "views",
            self._path / "src" / "pages",
            self._path / "public" / "css",
            self._path / "public" / "js",
            self._path / "public" / "images"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def files(self):
        # Base files
        package_json = _ASTRO_BASE_PACKAGE.copy()
        
        files = {
            self._path / "package.json": json.dumps(package_json, indent=2),
            self._path / "astro.config.mjs": ASTRO_CONFIG,
            self._path / "src" / "pages" / "render.astro": _RENDER_PAGE
        }
        
        for file_path, content in files.items():
            file_path.write_text(content, encoding="utf-8")

    def install(self, skip_pnpm_install: bool = False):
        if not skip_pnpm_install:
            try:
                subprocess.run(["pnpm", "--version"], capture_output=True, check=True, shell=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("pnpm not found. Attempting to install it globally...")
                subprocess.run(["npm", "install", "-g", "pnpm"], cwd=self._path, check=True, shell=True)
        
        print("Installing base dependencies...")
        subprocess.run(["pnpm", "install"], cwd=self._path, check=True, shell=True)
        subprocess.run(["pnpm", "run", "build"], cwd=self._path, check=True, shell=True)

    def project(self, skip_pnpm_install: bool = False):
        self.dirs()
        self.files()
        print(f"🚀 Astro project created in {self._path}")
        self.install(skip_pnpm_install=skip_pnpm_install)
        # We don't build here, let the Renderer handle it or user handle it
        print("😎 Base project is ready!")
