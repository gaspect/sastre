from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path
from sastre.extensions.base import BaseExtension

if TYPE_CHECKING:
    from sastre.renderer import Renderer


class HtmxHelper:
    """
    A helper class for HTMX-related rendering.
    It provides a way to render views and handle HTMX-specific response headers.
    """
    def __init__(self, renderer: "Renderer"):
        self.renderer = renderer

    def render(self, view: str, model: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
        """
        Render a view using the Astro renderer.
        """
        return self.renderer.render(view, model, headers=headers)

    @staticmethod
    def trigger(response_headers: Dict[str, str], event_name: str, detail: Any = None):
        """
        Adds an HX-Trigger header to the response headers.
        """
        import json
        if detail:
            trigger_val = {event_name: detail}
            response_headers["HX-Trigger"] = json.dumps(trigger_val)
        else:
            response_headers["HX-Trigger"] = event_name
        return response_headers


class Htmx(BaseExtension):
    """
    HTMX extension for Sastre.
    Adds HTMX examples and dependencies to the Astro project.
    """
    # Extension methods
    def dirs(self) -> List[Path]:
        return [
            Path("src/views/example"),
            Path("src/views/fragments"),
        ]

    def dependencies(self) -> Dict[str, str]:
        return {}

    def dev_dependencies(self) -> Dict[str, str]:
        # We can add htmx as a dev dependency or dependency if we want to bundle it
        # But for now the example uses CDN. 
        # Let's add it to show it works.
        return {"htmx.org": "^2.0.4"}

    def files(self) -> Dict[Path, str]:
        from sastre.scaffold import _EXAMPLE_STYLE
        
        counter_fragment = """---
let { count = 0 } = Astro.props;
const nextCount = parseInt(count as string) + 1;
---
<div id="counter-fragment">
    <p>Current count: <strong>{nextCount}</strong></p>
    <button 
        hx-post="/render-fragment/counter" 
        hx-target="#counter-fragment" 
        hx-vals={`{"count": ${nextCount}}`}
        hx-swap="outerHTML"
    >
        Increment
    </button>
</div>
"""

        pagination_fragment = """---
const { items = [], page = 1, totalPages = 1 } = Astro.props;
const currentPage = parseInt(page as string) || 1;
---
<div id="pagination-container">
    <ul>
        {items.map((item: any) => <li>{item}</li>)}
    </ul>
    
    <div class="pagination-controls">
        {currentPage > 1 && (
            <button 
                hx-post="/render-fragment/pagination" 
                hx-target="#pagination-container" 
                hx-vals={`{"page": ${currentPage - 1}}`}
                hx-swap="outerHTML"
            >
                Anterior
            </button>
        )}
        
        <span>Página {currentPage} de {totalPages}</span>

        {currentPage < totalPages && (
            <button 
                hx-post="/render-fragment/pagination" 
                hx-target="#pagination-container" 
                hx-vals={`{"page": ${currentPage + 1}}`}
                hx-swap="outerHTML"
            >
                Siguiente
            </button>
        )}
    </div>
</div>
"""
        
        htmx_index = """---
const { title } = Astro.props;
import Layout from "./Layout.astro";
---
<Layout title={title}>
    <main>
        <h1>{title ?? "Sastre"}</h1>
        <p>Let's stitch this together</p>
        
        <div class="counter-container">
            <h2>Counter Fragment</h2>
            <button 
                hx-post="/render-fragment/counter" 
                hx-target="#counter-value" 
                hx-vals='{"count": 0}'
                hx-swap="innerHTML"
            >
                Initialize Counter
            </button>
            <div id="counter-value"></div>
        </div>

        <div class="pagination-example">
            <h2>Dynamic Pagination Fragment</h2>
            <div id="pagination-container">
                <button 
                    hx-post="/render-fragment/pagination" 
                    hx-target="#pagination-container" 
                    hx-vals='{"page": 1}'
                    hx-swap="outerHTML"
                >
                    Cargar Lista con Paginación
                </button>
            </div>
        </div>
    </main>
</Layout>
"""

        htmx_layout = """---
const { title } = Astro.props;
import "./style.css";
---
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title ?? "Sastre"}</title>
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head>
<body>
    <slot />
</body>
</html>
"""

        return {
            Path("src/views/example/index.astro"): htmx_index,
            Path("src/views/example/Layout.astro"): htmx_layout,
            Path("src/views/example/style.css"): _EXAMPLE_STYLE,
            Path("src/views/fragments/counter.astro"): counter_fragment,
            Path("src/views/fragments/pagination.astro"): pagination_fragment,
        }
