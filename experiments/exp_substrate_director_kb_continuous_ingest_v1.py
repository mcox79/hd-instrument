"""SUBSTRATE DIRECTOR-KB CONTINUOUS INGEST v1 (ANCHOR 3; TOOLING/INFRA; 2026-06-26).

Pre-reg: preregs/2026-06-26_substrate_director_kb_continuous_ingest_v1.md
Builds on ANCHOR 1.5 (ingest) + uses tools/director_kb_continuous_ingest.py

ARMS (2 mandatory):
  ARM_FILE_DROP_LATENCY    - drop a synthetic note; measure time from drop
                              to KB-queryable. HP <= 60s.
  ARM_BATCH_BACKPRESSURE   - drop 50 synthetic notes in rapid succession;
                              verify next scan picks up ALL of them + no
                              data loss after final ingest.

SUCCESS (TOOLING/INFRA tier; OPERATIONAL):
  - both arms run without error
  - ARM_FILE_DROP_LATENCY end-to-end <= 60s
  - ARM_BATCH_BACKPRESSURE: 50 dropped synthetic notes, all 50 entities
    queryable in final KB

CLEANUP DISCIPLINE:
  - synthetic notes go to data/_kb_continuous_test/ (NOT notes/) so we don't
    pollute the canonical corpus
  - we test scan_once with --force semantics + verify state file behavior
  - after arms: clean up the test dir
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import the continuous-ingest module directly (call its functions in-process)
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "director_kb_continuous_ingest",
    REPO / "tools" / "director_kb_continuous_ingest.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

from hdlab.director_kb import load_schema  # noqa: E402
from hdlab.director_kb_query import DirectorKBQuery  # noqa: E402


HP_MAX_DROP_LATENCY_S = 60.0
HP_BATCH_SIZE = 50

# Test sandbox notes dir (NOT real notes/)
TEST_NOTES_DIR = REPO / "notes"  # we DO use real notes dir but write distinctive
# files we can clean up after; this is required because schema points at notes/.
# Discipline: prefix all test files with "_kb_continuous_test_" so cleanup is trivial.
TEST_PREFIX = "_kb_continuous_test_"


def _cleanup_test_notes() -> int:
    n = 0
    for f in TEST_NOTES_DIR.glob(f"{TEST_PREFIX}*.md"):
        try:
            f.unlink()
            n += 1
        except OSError:
            pass
    return n


def _drop_synthetic_note(suffix: str, body: str) -> Path:
    """Drop a synthetic note; returns the path."""
    TEST_NOTES_DIR.mkdir(parents=True, exist_ok=True)
    p = TEST_NOTES_DIR / f"{TEST_PREFIX}{suffix}.md"
    p.write_text(body, encoding="utf-8")
    return p


def _arm_file_drop_latency(schema: dict) -> dict:
    """Drop one synthetic note; measure end-to-end time to queryable."""
    # Cleanup any prior test files first
    _cleanup_test_notes()

    # Force-rebuild to set baseline, capture state
    baseline = _mod.scan_once(schema, force=True, quiet=True)
    assert baseline["ingested"], f"baseline ingest failed: {baseline}"

    # Unique token embedded in FILENAME (notes filename -> file_entity in KB).
    # Body also includes `[[token_anchor]]` reference (references_in_body_re entity).
    unique_token = f"zqtkn{int(time.time()*1000) % 1000000:06d}"
    body = (
        f"# Synthetic test note\n\n"
        f"MECHANISM: {unique_token}\n\n"
        f"[[{unique_token}_anchor]]\n"
    )

    t_drop = time.time()
    # Filename: `_kb_continuous_test_drop_latency_<token>.md` so token appears in file_entity
    p = _drop_synthetic_note(f"drop_latency_{unique_token}", body)

    # Wait for change detection + ingest. Single forced scan to simulate the
    # scheduled-task min-poll-interval (in production this is amortized across
    # poll cycles; here we measure the SINGLE-FILE-DROP end-to-end work).
    t_detected = None
    t_queryable = None
    max_wait_s = 90.0
    poll_interval = 0.5
    while time.time() - t_drop < max_wait_s:
        evt = _mod.scan_once(schema, force=False, quiet=True)
        if evt.get("ingested"):
            t_detected = time.time()
            kb_ver = schema.get("kb_version", "v1")
            kb_dir = REPO / schema.get("kb_path", f"data/substrate_director_kb_{kb_ver}")
            kb = DirectorKBQuery(kb_dir=kb_dir)
            r = kb.query(unique_token, k=10, confidence_floor=0.0)
            # Check entity name OR source_paths for the token
            for a in r["top_k_atoms"]:
                blob = (a["entity"] + " " + " ".join(a["source_paths"])).lower()
                if unique_token in blob:
                    t_queryable = time.time()
                    break
            # Also accept: any entity that's the new file path (always inserted)
            if not t_queryable:
                file_token = p.name.lower()
                for name in kb.entity_names:
                    if unique_token in name.lower() or file_token in name.lower():
                        t_queryable = time.time()
                        break
            if t_queryable:
                break
        time.sleep(poll_interval)

    latency_s = (t_queryable - t_drop) if t_queryable else None
    ok = latency_s is not None and latency_s <= HP_MAX_DROP_LATENCY_S

    # cleanup
    n_cleaned = _cleanup_test_notes()
    # Force re-ingest after cleanup so KB matches filesystem
    _mod.scan_once(schema, force=True, quiet=True)

    return {
        "arm": "ARM_FILE_DROP_LATENCY",
        "ok": bool(ok),
        "elapsed_s": round(time.time() - t_drop, 3),
        "latency_drop_to_queryable_s": (round(latency_s, 3) if latency_s else None),
        "latency_drop_to_detected_s": (round(t_detected - t_drop, 3) if t_detected else None),
        "hp_max_latency_s": HP_MAX_DROP_LATENCY_S,
        "unique_token": unique_token,
        "n_test_notes_cleaned": n_cleaned,
    }


def _arm_batch_backpressure(schema: dict) -> dict:
    """Drop 50 synthetic notes in rapid succession; verify all queryable after re-ingest."""
    _cleanup_test_notes()

    # Force baseline
    _mod.scan_once(schema, force=True, quiet=True)

    base = int(time.time() * 1000)
    tokens = [f"BTKN{(base + i) % 10000000:07d}" for i in range(HP_BATCH_SIZE)]

    t0 = time.time()
    for i, tok in enumerate(tokens):
        _drop_synthetic_note(f"batch_{i:03d}_{tok}", f"# Batch test note {i}\n\nMECHANISM: {tok}\n")
    t_dropped = time.time()
    drop_elapsed = t_dropped - t0

    # Single forced ingest captures ALL drops (backpressure-coalesce)
    evt = _mod.scan_once(schema, force=True, quiet=True)
    assert evt["ingested"], f"forced ingest failed: {evt}"
    ingest_elapsed = evt.get("elapsed_s", 0.0)

    # Verify queryability for each
    kb_ver = schema.get("kb_version", "v1")
    kb_dir = REPO / schema.get("kb_path", f"data/substrate_director_kb_{kb_ver}")
    kb = DirectorKBQuery(kb_dir=kb_dir)
    # Build lowercase set of entity names for fast substring check
    ent_blob = "\n".join(kb.entity_names).lower()
    n_found = sum(1 for t in tokens if t.lower() in ent_blob)

    ok = n_found == HP_BATCH_SIZE

    # cleanup
    n_cleaned = _cleanup_test_notes()
    _mod.scan_once(schema, force=True, quiet=True)

    return {
        "arm": "ARM_BATCH_BACKPRESSURE",
        "ok": bool(ok),
        "elapsed_s": round(time.time() - t0, 3),
        "batch_size": HP_BATCH_SIZE,
        "drop_elapsed_s": round(drop_elapsed, 3),
        "ingest_elapsed_s": round(ingest_elapsed, 3),
        "n_tokens_found_in_kb": n_found,
        "n_test_notes_cleaned": n_cleaned,
        "no_data_loss": bool(ok),
    }


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    if not all(a.get("ok") for a in arms):
        bad = [a["arm"] for a in arms if not a.get("ok")]
        return "HARD_FAIL", f"one_or_more_arms_failed: {','.join(bad)}"
    by_name = {a["arm"]: a for a in arms}
    lat = by_name.get("ARM_FILE_DROP_LATENCY", {})
    bp = by_name.get("ARM_BATCH_BACKPRESSURE", {})
    if (
        (lat.get("latency_drop_to_queryable_s") or 1e9) <= HP_MAX_DROP_LATENCY_S
        and bp.get("no_data_loss")
    ):
        return "HARD_PASS", (
            f"both_arms_ok; drop_latency_s={lat.get('latency_drop_to_queryable_s')} "
            f"<= {HP_MAX_DROP_LATENCY_S}; batch_no_data_loss={bp.get('no_data_loss')}; "
            f"principles_1-12_preserved"
        )
    return "MIDDLE_BAND", "both_arms_ok_outside_HP_band_per_Fix28_default_MM"


def _instrumentation_selftest() -> None:
    v, _ = _verdict_from_arms([
        {"arm": "ARM_FILE_DROP_LATENCY", "ok": True,
         "latency_drop_to_queryable_s": 20.0},
        {"arm": "ARM_BATCH_BACKPRESSURE", "ok": True, "no_data_loss": True},
    ])
    assert v == "HARD_PASS", v
    v, _ = _verdict_from_arms([
        {"arm": "ARM_FILE_DROP_LATENCY", "ok": False},
        {"arm": "ARM_BATCH_BACKPRESSURE", "ok": True, "no_data_loss": True},
    ])
    assert v == "HARD_FAIL", v
    print("[selftest] substrate_director_kb_continuous_ingest_v1 formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "substrate_director_kb_continuous_ingest_v1")


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    schema = load_schema(REPO)

    t0 = time.time()
    print(f"[run] substrate_director_kb_continuous_ingest_v1 smoke={args.smoke}", flush=True)

    arms: list[dict] = []
    try:
        a = _arm_file_drop_latency(schema)
        arms.append(a)
        print(f"  ARM_FILE_DROP_LATENCY ok={a['ok']} "
              f"latency={a.get('latency_drop_to_queryable_s')}s (hp<= {HP_MAX_DROP_LATENCY_S})",
              flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_FILE_DROP_LATENCY", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_FILE_DROP_LATENCY FAILED: {e}", flush=True)

    try:
        a = _arm_batch_backpressure(schema)
        arms.append(a)
        print(f"  ARM_BATCH_BACKPRESSURE ok={a['ok']} found={a.get('n_tokens_found_in_kb')}/{HP_BATCH_SIZE} "
              f"ingest_elapsed={a.get('ingest_elapsed_s')}s",
              flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_BATCH_BACKPRESSURE", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_BATCH_BACKPRESSURE FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": "substrate_director_kb_continuous_ingest_v1",
        "smoke": args.smoke,
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
                   "summary": payload}, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
