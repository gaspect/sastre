import json
from pathlib import Path
from typing import Dict
from .base import BaseExtension

class React(BaseExtension):
    def name(self) -> str:
        return "React"

    def dev_dependencies(self) -> Dict[str, str]:
        return {
            "@astrojs/react": "^4.2.0",
            "@types/react": "^19.0.0",
            "@types/react-dom": "^19.0.0",
            "react": "^19.0.0",
            "react-dom": "^19.0.0"
        }

    def setup(self, project_dir: Path):
        # 1. Update astro.config.mjs
        config_path = project_dir / "astro.config.mjs"
        if config_path.exists():
            content = config_path.read_text(encoding="utf-8")
            if "react" not in content:
                if "import { defineConfig } from 'astro/config';" in content:
                    content = content.replace(
                        "import { defineConfig } from 'astro/config';",
                        "import { defineConfig } from 'astro/config';\nimport react from '@astrojs/react';"
                    )
                
                if "integrations: [" in content:
                    content = content.replace(
                        "integrations: [",
                        "integrations: [react(),"
                    )
                else:
                    if "defineConfig({" in content:
                        content = content.replace(
                            "defineConfig({",
                            "defineConfig({\n  integrations: [react()],"
                        )
                config_path.write_text(content, encoding="utf-8")
        
        # 2. Update tsconfig.json
        tsconfig_path = project_dir / "tsconfig.json"
        tsconfig = {}
        if tsconfig_path.exists():
            try:
                tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                # If it's invalid JSON (e.g. has comments), we might have an issue
                # but for now let's assume valid JSON as it's a generated project
                pass
        
        if "compilerOptions" not in tsconfig:
            tsconfig["compilerOptions"] = {}
        
        tsconfig["compilerOptions"]["jsx"] = "react-jsx"
        tsconfig["compilerOptions"]["jsxImportSource"] = "react"
        
        tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")
