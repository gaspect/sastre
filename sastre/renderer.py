from pathlib import Path
import subprocess
import requests


class Renderer:
    def __init__(self, _dir: str, port: int = 4321):
        self._dir = Path(_dir).resolve()
        self._port = port
        self._server_process = None

    def start(self):
        if self._server_process:
            return

        subprocess.run(["pnpm", "run", "build"], cwd=self._dir, check=True, shell=True)

        self._server_process = subprocess.Popen(
            ["pnpm", "run", "start"],
            cwd=self._dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def stop(self):
        if self._server_process:
            print("Stopping renderer...")
            self._server_process.terminate()
            try:
                self._server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_process.kill()
            self._server_process = None

    def __aenter__(self):
        self.start()
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def render(self, view: str, model: dict) -> str:
        payload = {"view": view, "model": model}
        url = f"http://localhost:{self._port}/render"
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.content

    @property
    def assets(self):
        return self._dir / "public"

    @property
    def client(self):
        return self._dir / "dist/client"


    def __call__(self, view: str, model: dict) -> str:
        return self.render(view, model)