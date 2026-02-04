from pathlib import Path
from typing import Dict
from .base import BaseExtension

class Lucide(BaseExtension):
    def name(self) -> str:
        return "Lucide"

    def dependencies(self) -> Dict[str, str]:
        return {
            "lucide-astro": "^0.470.0"
        }

    def setup(self, project_dir: Path):
        # Lucide-astro doesn't need config, just import and use in components
        pass
