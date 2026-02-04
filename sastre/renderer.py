from typing import TYPE_CHECKING
from pathlib import Path
import subprocess
import requests
import json
import os

from sastre.manager import ExtensionManager
from sastre.scaffold import Scaffold

if TYPE_CHECKING:
    from sastre.extensions.base import Extension


class Renderer:
    def __init__(self, _dir: str, port: int = 4321, host: str = "localhost"):
        self._dir = Path(_dir).resolve()
        self._port = port
        self._host = host
        self._server_process = None

        # Auto-scaffold if the directory doesn't exist or is missing package.json
        if not (self._dir / "package.json").exists():
            print(f"Directory {self._dir} does not seem to be an Astro project. Scaffolding...")
            Scaffold(str(self._dir)).project()

        self._manager = ExtensionManager(self._dir)

    def extension(self, *extensions: "Extension"):
        self._manager.apply(*extensions)

    def extensions(self, *extensions: "Extension"):
        # Keep for backward compatibility
        self.extension(*extensions)

    def start(self, build: bool = True):
        if self._server_process:
            return

        if build:
            print(f"Building Astro project in {self._dir}...")
            subprocess.run(["pnpm", "run", "build"], cwd=self._dir, check=True, shell=True)

        print(f"Starting Astro server on {self._host}:{self._port}...")
        env = dict(os.environ)
        env["PORT"] = str(self._port)
        env["HOST"] = self._host

        self._server_process = subprocess.Popen(
            ["pnpm", "run", "start"],
            cwd=self._dir,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )

        # Wait for the server to be ready
        import time
        max_retries = 30
        for i in range(max_retries):
            try:
                requests.get(f"http://{self._host}:{self._port}/render", timeout=1)
                print("Astro server is ready!")
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if self._server_process.poll() is not None:
                    stdout, stderr = self._server_process.communicate()
                    raise RuntimeError(
                        f"Astro server failed to start:\nSTDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}")
                time.sleep(1)
        else:
            self.stop()
            raise RuntimeError("Timed out waiting for Astro server to start")

    def stop(self):
        if self._server_process:
            print("Stopping renderer...")
            if os.name == 'nt':
                # On Windows, taskkill is more reliable for killing process trees
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(self._server_process.pid)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
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

    def render(self, view: str, model: dict, headers: dict = None) -> str:
        payload = {"view": view, "model": model}
        # noinspection HttpUrlsUsage
        url = f"http://{self._host}:{self._port}/render"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.text

    @property
    def assets(self):
        return self._dir / "public"

    @property
    def client(self):
        return self._dir / "dist/client"

    def __call__(self, view: str, model: dict) -> str:
        return self.render(view, model)
