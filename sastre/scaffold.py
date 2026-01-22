import subprocess
from pathlib import Path

_ASTRO_BASE_PACKAGE = """{
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
"""

ASTRO_CONFIG = """import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  publicDir: 'public',
});
"""

_EXAMPLE_TEMPLATE = """---
const { title } = Astro.props;
import "./style.css";
---
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <title>{title ?? "Ejemplo"}</title>
</head>
<body>
    <h1>{title ?? "Ejemplo"}</h1>
    <p>Este es un template vacío listo para agregar React, Vue o Tailwind.</p>
</body>
</html>
"""

_EXAMPLE_STYLE = """body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  margin: 0;
  padding: 0;
}

h1 {
  text-align: center;
  margin-top: 20px;
  color: #333;
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
  throw new Error('Falta "view" en el body JSON');
}

const viewModules = import.meta.glob('../views/*/index.astro');

const viewKey = `../views/${view}/index.astro`;
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
    throw new Error('El campo "model" debe ser un objeto JSON o un string JSON válido');
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
            self._path / "src" / "views" / "example",
            self._path / "src" / "pages",
            self._path / "public" / "css",
            self._path / "public" / "js",
            self._path / "public" / "images"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def files(self):
        files = {
            self._path / "package.json": _ASTRO_BASE_PACKAGE,
            self._path / "astro.config.mjs": ASTRO_CONFIG,
            self._path / "src" / "views" / "example" / "index.astro": _EXAMPLE_TEMPLATE,
            self._path / "src" / "views" / "example" / "style.css": _EXAMPLE_STYLE,
            self._path / "src" / "pages" / "render.astro": _RENDER_PAGE
        }
        for file_path, content in files.items():
            file_path.write_text(content, encoding="utf-8")

    def install(self):
        subprocess.run(["npm", "install", "-g", "pnpm"], cwd=self._path, check=True, shell=True)
        subprocess.run(["pnpm", "install"], cwd=self._path, check=True, shell=True)

    def project(self):
        self.dirs()
        self.files()
        print(f"🚀 Astro project created in {self._path}")
        self.install()
        print("😎 Dependencias instaladas")
