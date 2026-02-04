from pathlib import Path
from typing import Dict
from .base import BaseExtension

class Svelte(BaseExtension):
    def name(self) -> str:
        return "Svelte"

    def dev_dependencies(self) -> Dict[str, str]:
        return {
            "@astrojs/svelte": "^7.0.0",
            "svelte": "^5.0.0"
        }

    def setup(self, project_dir: Path):
        config_path = project_dir / "astro.config.mjs"
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            if "svelte" not in content:
                if "import { defineConfig } from 'astro/config';" in content:
                    content = content.replace(
                        "import { defineConfig } from 'astro/config';",
                        "import { defineConfig } from 'astro/config';\nimport svelte from '@astrojs/svelte';"
                    )
                
                if "integrations: [" in content:
                    content = content.replace(
                        "integrations: [",
                        "integrations: [svelte(),"
                    )
                else:
                    if "defineConfig({" in content:
                        content = content.replace(
                            "defineConfig({",
                            "defineConfig({\n  integrations: [svelte()],"
                        )
                config_path.write_text(content, encoding="utf-8")
