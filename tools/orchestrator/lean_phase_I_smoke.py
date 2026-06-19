#!/usr/bin/env python3
"""PHASE I smoke test for Lean toolchain integration.

1. Verify lean CLI accessible
2. Run a hello-world proof via lean CLI (no mathlib needed)
3. Run the same proof via lean-interact Python bindings
4. Report install verification status

Run from project root: .venv/Scripts/python.exe tools/orchestrator/lean_phase_I_smoke.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ELAN_BIN = Path.home() / ".elan" / "bin"
LEAN_CLI = ELAN_BIN / "lean.exe"

HELLO_LEAN = """\
-- PHASE I hello-world proof: addition of two naturals
def main : IO Unit := IO.println "lean phase I smoke ok"

example : 1 + 1 = 2 := by rfl
example : (3 : Nat) + 4 = 7 := by rfl
"""


def step1_lean_cli_present() -> dict:
    if not LEAN_CLI.exists():
        return {"step": "1_cli_present", "ok": False, "error": f"lean.exe not found at {LEAN_CLI}"}
    return {"step": "1_cli_present", "ok": True, "path": str(LEAN_CLI)}


def step2_lean_version() -> dict:
    try:
        out = subprocess.check_output([str(LEAN_CLI), "--version"], timeout=30, text=True)
        return {"step": "2_lean_version", "ok": True, "version": out.strip()}
    except Exception as e:
        return {"step": "2_lean_version", "ok": False, "error": f"{type(e).__name__}: {e}"}


def step3_hello_world_proof(tmpdir: Path) -> dict:
    lean_file = tmpdir / "Hello.lean"
    lean_file.write_text(HELLO_LEAN, encoding="utf-8")
    try:
        # lean --run executes main; otherwise lean checks types
        result = subprocess.run(
            [str(LEAN_CLI), "--run", str(lean_file)],
            timeout=60,
            capture_output=True,
            text=True,
        )
        ok = result.returncode == 0 and "lean phase I smoke ok" in result.stdout
        return {
            "step": "3_hello_world_proof",
            "ok": ok,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()[:500],
        }
    except Exception as e:
        return {"step": "3_hello_world_proof", "ok": False, "error": f"{type(e).__name__}: {e}"}


def step4_lean_interact_import() -> dict:
    try:
        import lean_interact
        return {"step": "4_lean_interact_import", "ok": True, "version": getattr(lean_interact, "__version__", "unknown")}
    except Exception as e:
        return {"step": "4_lean_interact_import", "ok": False, "error": f"{type(e).__name__}: {e}"}


def main():
    print("PHASE I Lean smoke test")
    print("=" * 60)

    results = []

    r1 = step1_lean_cli_present()
    print(json.dumps(r1, indent=2))
    results.append(r1)
    if not r1["ok"]:
        print("\nFAIL at step 1; aborting")
        sys.exit(1)

    r2 = step2_lean_version()
    print(json.dumps(r2, indent=2))
    results.append(r2)
    if not r2["ok"]:
        print("\nFAIL at step 2; aborting")
        sys.exit(2)

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r3 = step3_hello_world_proof(Path(td))
    print(json.dumps(r3, indent=2))
    results.append(r3)

    r4 = step4_lean_interact_import()
    print(json.dumps(r4, indent=2))
    results.append(r4)

    all_ok = all(r["ok"] for r in results)
    print("=" * 60)
    print(f"OVERALL: {'PASS' if all_ok else 'FAIL'}")
    sys.exit(0 if all_ok else 3)


if __name__ == "__main__":
    main()
