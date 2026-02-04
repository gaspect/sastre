from pathlib import Path
from typing import Dict
from .base import BaseExtension

class Alpine(BaseExtension):
    def name(self) -> str:
        return "Alpine"

    def dev_dependencies(self) -> Dict[str, str]:
        return {
            "@astrojs/alpinejs": "^0.4.0",
            "alpinejs": "^3.14.0"
        }

    def setup(self, project_dir: Path):
        config_path = project_dir / "astro.config.mjs"
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            if "alpine" not in content:
                if "import { defineConfig } from 'astro/config';" in content:
                    content = content.replace(
                        "import { defineConfig } from 'astro/config';",
                        "import { defineConfig } from 'astro/config';\nimport alpine from '@astrojs/alpinejs';"
                    )
                
                if "integrations: [" in content:
                    content = content.replace(
                        "integrations: [",
                        "integrations: [alpine(),"
                    )
                else:
                    if "defineConfig({" in content:
                        content = content.replace(
                            "defineConfig({",
                            "defineConfig({\n  integrations: [alpine()],"
                        )
                config_path.write_text(content, encoding="utf-8")
