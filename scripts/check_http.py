"""Smoke-test the actual development proxy and API in one process environment.

Run from any directory using the repository's virtual-environment Python.
Requires frontend/node_modules and free loopback ports 8000 and 15173.
"""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    processes: list[subprocess.Popen] = []
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    base = "http://127.0.0.1:15173"
    try:
        processes.append(subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True,
        ))
        processes.append(subprocess.Popen(
            ["npm", "run", "dev", "--", "--port", "15173", "--strictPort"],
            cwd=root / "frontend", stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True,
        ))
        for _ in range(100):
            if any(process.poll() is not None for process in processes):
                raise RuntimeError("A development server exited; check installed dependencies and free ports.")
            try:
                with opener.open(base + "/api/health", timeout=1) as response:
                    health = json.load(response)
                break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.1)
        else:
            raise RuntimeError("Development servers did not become ready.")
        assert health["mode"] == "synthetic_demo" and health["orders_enabled"] is False
        with opener.open(base, timeout=2) as response:
            assert 'id="root"' in response.read().decode()
        for minute, qualified in (("30", 0), ("35", 1), ("40", 1)):
            as_of = f"2026-10-30T09:{minute}:00+05:30"
            query = urllib.parse.urlencode({"as_of": as_of})
            with opener.open(base + "/api/replay?" + query, timeout=2) as response:
                replay = json.load(response)
            assert replay["as_of"] == as_of
            assert replay["summary"]["qualified"] == qualified
            beta = next(card for card in replay["candidates"] if card["symbol"] == "DEMO_BETA")
            assert bool(beta["evidence"]) == (minute == "40")
            print(as_of, replay["summary"], "beta_fundamentals=" + beta["fundamentals_status"])
        print("HTTP frontend proxy / backend integration passed. No browser rendering was tested.")
    finally:
        for process in processes:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=3)
            if process.stderr:
                process.stderr.close()


if __name__ == "__main__":
    main()
