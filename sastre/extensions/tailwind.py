from pathlib import Path
from typing import Dict
from .base import BaseExtension

class Tailwind(BaseExtension):
    def name(self) -> str:
        return "Tailwind"

    def dev_dependencies(self) -> Dict[str, str]:
        return {
            "tailwindcss": "^4.0.0",
            "@tailwindcss/vite": "^4.0.0"
        }

    def setup(self, project_dir: Path):
        config_path = project_dir / "astro.config.mjs"
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            if "tailwind" not in content:
                # Basic injection of tailwind vite plugin
                if "import { defineConfig } from 'astro/config';" in content:
                    content = content.replace(
                        "import { defineConfig } from 'astro/config';",
                        "import { defineConfig } from 'astro/config';\nimport tailwind from '@tailwindcss/vite';"
                    )
                
                if "adapter:" in content:
                    content = content.replace(
                        "adapter:",
                        "vite: { plugins: [tailwind()] },\n  adapter:"
                    )
                config_path.write_text(content, encoding="utf-8")
        
        # Create global.css with tailwind imports if it doesn't exist
        css_dir = project_dir / "src" / "styles"
        css_dir.mkdir(parents=True, exist_ok=True)
        global_css = css_dir / "global.css"
        if not global_css.exists():
            global_css.write_text("@import 'tailwindcss';", encoding="utf-8")
