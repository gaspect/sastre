from pathlib import Path
from typing import List, Dict, Protocol, runtime_checkable


@runtime_checkable
class Extension(Protocol):
    def name(self) -> str: ...

    def dirs(self) -> List[Path]: ...

    def files(self) -> Dict[Path, str]: ...

    def dependencies(self) -> Dict[str, str]: ...

    def dev_dependencies(self) -> Dict[str, str]: ...

    def setup(self, project_dir: Path): ...

    def teardown(self, project_dir: Path): ...


class BaseExtension:
    def name(self) -> str:
        return self.__class__.__name__

    def dirs(self) -> List[Path]: return []

    def files(self) -> Dict[Path, str]: return {}

    def dependencies(self) -> Dict[str, str]: return {}

    def dev_dependencies(self) -> Dict[str, str]: return {}

    def setup(self, project_dir: Path):
        """Called after files are created and dependencies are updated, but before pnpm install."""
        pass

    def teardown(self, project_dir: Path):
        """Called if the extension needs to clean up something (rarely used)."""
        pass
