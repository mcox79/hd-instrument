"""Run after pasting keys into .env.local to verify they work.

Usage on runner:
    cd C:\\dev\\hd-instrument
    .venv-demo\\Scripts\\python.exe scripts\\verify_api_keys.py
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Make project root importable so `from backend.llm.* import *` works
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load .env.local
env_path = ROOT / ".env.local"
if env_path.exists():
    print(f"loading {env_path}")
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()
else:
    print(f"WARNING: {env_path} not found; using shell env only")

# Test OpenAI
print("\n=== OpenAI gpt-4o-mini health check ===")
try:
    from backend.llm.openai_client import health_check as oai_health
    result = oai_health()
    if result.get("ok"):
        print(f"  PASS: responded {result['response_text']!r} in {result['latency_ms']:.0f} ms "
              f"(cost ${result['cost_usd']:.6f})")
    else:
        print(f"  FAIL: {result.get('error')}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")

# Test Anthropic
print("\n=== Anthropic Claude Haiku health check ===")
try:
    from backend.llm.anthropic_client import health_check as ant_health
    result = ant_health()
    if result.get("ok"):
        print(f"  PASS: responded {result['response_text']!r} in {result['latency_ms']:.0f} ms "
              f"(cost ${result['cost_usd']:.6f})")
    else:
        print(f"  FAIL: {result.get('error')}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {e}")
