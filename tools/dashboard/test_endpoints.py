"""Phase 2 validation: exercise all endpoints in-process via FastAPI TestClient.

No port binding, no server process. Proves routing + lifespan + poller wiring.
"""

from __future__ import annotations

import json
import time

from fastapi.testclient import TestClient

from server import app


def main() -> None:
    with TestClient(app) as client:
        # Wait briefly for at least one poll cycle to complete.
        deadline = time.time() + 8.0
        while time.time() < deadline:
            h = client.get("/api/health").json()
            if h.get("last_poll_ok"):
                break
            time.sleep(0.5)

        for route in ("/api/health", "/api/system", "/api/runs", "/api/queue", "/api/history"):
            r = client.get(route)
            print(f"=== GET {route} -> {r.status_code} ===")
            body = r.json()
            text = json.dumps(body, indent=2)
            # truncate huge payloads for legibility
            print(text if len(text) <= 1200 else text[:1200] + f"\n... [{len(text)-1200} more chars]")
            print()


if __name__ == "__main__":
    main()
