import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from sastre.extensions.base import Extension


class ExtensionManager:
    def __init__(self, project_dir: Path):
        self._dir = project_dir
        self._state_file = self._dir / ".sastre.json"

    def _get_state(self) -> dict:
        if not self._state_file.exists():
            return {"extensions": []}
        try:
            return json.loads(self._state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"extensions": []}

    def _save_state(self, state: dict):
        self._state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def is_installed(self, name: str) -> bool:
        state = self._get_state()
        return name in state.get("extensions", [])

    def record_extension(self, name: str):
        state = self._get_state()
        if "extensions" not in state:
            state["extensions"] = []
        if name not in state["extensions"]:
            state["extensions"].append(name)
            self._save_state(state)

    def apply(self, *extensions: "Extension"):
        for extension in extensions:
            if self.is_installed(extension.name()):
                continue

            print(f"Applying extension: {extension.name()} to {self._dir}")

            # Create directories
            for d in extension.dirs():
                target_dir = self._dir / d if not d.is_absolute() else d
                target_dir.mkdir(parents=True, exist_ok=True)

            # Create files
            for f, content in extension.files().items():
                target_file = self._dir / f if not f.is_absolute() else f
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(content, encoding="utf-8")

            # Update package.json
            package_json_path = self._dir / "package.json"
            needs_install = False
            if package_json_path.exists():
                package_json = json.loads(package_json_path.read_text(encoding="utf-8"))

                deps = extension.dependencies()
                if deps:
                    if "dependencies" not in package_json:
                        package_json["dependencies"] = {}
                    for k, v in deps.items():
                        if package_json["dependencies"].get(k) != v:
                            package_json["dependencies"][k] = v
                            needs_install = True

                dev_deps = extension.dev_dependencies()
                if dev_deps:
                    if "devDependencies" not in package_json:
                        package_json["devDependencies"] = {}
                    for k, v in dev_deps.items():
                        if package_json["devDependencies"].get(k) != v:
                            package_json["devDependencies"][k] = v
                            needs_install = True

                if needs_install:
                    package_json_path.write_text(json.dumps(package_json, indent=2), encoding="utf-8")

            # Call setup hook
            extension.setup(self._dir)

            if needs_install:
                print(f"Dependencies changed for {extension.name()}. Installing...")
                try:
                    subprocess.run(["pnpm", "install"], cwd=self._dir, check=True, shell=True)
                except subprocess.CalledProcessError:
                    print(f"Warning: 'pnpm install' failed for {extension.name()}. Please run it manually.")

            self.record_extension(extension.name())
