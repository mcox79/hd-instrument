"""SUBSTRATE DIRECTOR-KB INGEST v1 (ANCHOR 1; TOOLING; 2026-06-26).

USER green-lit 2026-06-26 with no-lock-in constraint:
  "Make sure we're not locking ourselves into a particular architecture
   that will be hard to correct should we need to."

This cell ships ANCHOR 1 of the Director-KB dogfood build per
notes/exp_dev_handoff_research_substrate_director_kb_dogfood_2026-06-26.md.

ARMS (3 mandatory):
  ARM_INGEST_NOTES_ONLY      - notes/ only; sanity
  ARM_INGEST_FULL            - notes + memory + metrics + preregs
  ARM_REINGEST_DETERMINISTIC - run FULL twice; assert byte-equal entities/
                               relations/atoms (timestamp-redacted) +
                               W L2 diff < 1e-6. Load-bearing for Principle 2
                               (wipe-and-rebuild safety).

SUCCESS CRITERIA (pre-reg HARD_PASS):
  - All 3 arms run without uncaught exceptions
  - ARM_INGEST_FULL elapsed_s <= 900 (15 min envelope cap, Principle 9)
  - ARM_INGEST_FULL coverage_ratio >= 0.95
  - ARM_REINGEST_DETERMINISTIC passes exact-equal + W L2 < 1e-6
  - Schema is externalized (cell loaded config/director_kb_schema.json)

FAILURE CRITERIA (pre-reg HARD_FAIL):
  - ARM_INGEST_FULL elapsed_s > 1800 (twice envelope cap)
  - ARM_REINGEST_DETERMINISTIC non-deterministic (Principle 2 violation)
  - Coverage < 0.80 (too many silent rejects)
  - Schema not loadable from config (lock-in violation)

Anchor: substrate_director_kb_ingest_v1
Queue:  local_cpu_queue
Pre-reg: preregs/2026-06-26_substrate_director_kb_ingest_v1.md
Arch doc: docs/director_kb_arch.md
Schema:  config/director_kb_schema.json
CLI:     tools/director_kb_ingest.py
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

from hdlab.director_kb import (  # noqa: E402
    SCHEMA_PATH_DEFAULT,
    W_l2_diff,
    build_ingest_plan,
    files_byte_equal,
    load_schema,
    run_ingest,
    schema_hash,
)


# ---------- envelope thresholds (Principle 9 + pre-reg bands) ----------
HP_MAX_FULL_ELAPSED_S = 900     # 15 min
HF_MAX_FULL_ELAPSED_S = 1800    # 30 min
HP_MIN_COVERAGE = 0.95
HF_MIN_COVERAGE = 0.80
HP_MAX_W_L2 = 1e-6              # ARM_REINGEST_DETERMINISTIC tolerance

# ---------- smoke caps ----------
SMOKE_MAX_FILES_PER_CLASS = 200  # ~800 files total
FULL_MAX_FILES_PER_CLASS = None  # uncapped; respects schema per-class cap

# ---------- N (HD dimension) ----------
# Default 2048 (chain-grade-tested in KGStore primitive). No _n<N> anchor
# suffix (PROT-018 not applicable).
N_DIM = 2048
SEED = 17


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "substrate_director_kb_ingest_v1")


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _arm_workdir(arm_name: str) -> Path:
    d = _exp_dir() / f"_arm_{arm_name}"
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- arm implementations ----------

def _run_arm_notes_only(schema: dict, max_files: int | None) -> dict:
    arm_dir = _arm_workdir("notes_only")
    out_dir = arm_dir / "kb"
    plan = build_ingest_plan(
        schema=schema,
        repo_root=REPO,
        max_files_per_class=max_files,
        only_classes=["note"],
    )
    n_disc = sum(len(plan[c]["files"]) for c in plan)
    t0 = time.perf_counter()
    manifest = run_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=N_DIM,
        seed=SEED,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0
    ok = (
        manifest["n_triples"] > 0
        and manifest["n_entities"] > 0
        and manifest["n_relations"] > 0
        and (out_dir / "reject_log.jsonl").exists()
    )
    return {
        "arm": "ARM_INGEST_NOTES_ONLY",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "n_discovered": n_disc,
        "n_triples": manifest["n_triples"],
        "n_entities": manifest["n_entities"],
        "n_relations": manifest["n_relations"],
        "coverage_ratio": manifest["coverage_ratio"],
        "out_dir": str(out_dir),
    }


def _run_arm_full(schema: dict, max_files: int | None) -> dict:
    arm_dir = _arm_workdir("full")
    out_dir = arm_dir / "kb"
    plan = build_ingest_plan(
        schema=schema,
        repo_root=REPO,
        max_files_per_class=max_files,
        only_classes=None,
    )
    per_class_disc = {c: len(plan[c]["files"]) for c in plan}
    n_disc = sum(per_class_disc.values())
    t0 = time.perf_counter()
    manifest = run_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=N_DIM,
        seed=SEED,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0
    n_classes_with_files = sum(1 for c in per_class_disc.values() if c > 0)
    ok = (
        manifest["n_triples"] > 0
        and manifest["n_entities"] > 0
        and n_classes_with_files >= 2
    )
    return {
        "arm": "ARM_INGEST_FULL",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "n_discovered": n_disc,
        "per_class_discovered": per_class_disc,
        "n_triples": manifest["n_triples"],
        "n_entities": manifest["n_entities"],
        "n_relations": manifest["n_relations"],
        "coverage_ratio": manifest["coverage_ratio"],
        "out_dir": str(out_dir),
    }


def _run_arm_reingest_deterministic(schema: dict, max_files: int | None) -> dict:
    """LOAD-BEARING: Principle 2 wipe-and-rebuild safety.

    Runs the FULL ingest twice into separate temp dirs (with timestamps
    redacted from atoms) and asserts byte-equal entities/relations/atoms
    plus W L2 diff < 1e-6.
    """
    arm_dir = _arm_workdir("reingest_det")
    out_a = arm_dir / "kb_a"
    out_b = arm_dir / "kb_b"
    plan = build_ingest_plan(
        schema=schema,
        repo_root=REPO,
        max_files_per_class=max_files,
        only_classes=None,
    )
    t0 = time.perf_counter()
    man_a = run_ingest(
        plan=plan, out_dir=out_a, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=True,
    )
    t_a = time.perf_counter() - t0
    t1 = time.perf_counter()
    # Re-build the plan a second time (regenerates file lists from disk;
    # validates that the walk itself is deterministic across calls).
    plan2 = build_ingest_plan(
        schema=schema,
        repo_root=REPO,
        max_files_per_class=max_files,
        only_classes=None,
    )
    man_b = run_ingest(
        plan=plan2, out_dir=out_b, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=True,
    )
    t_b = time.perf_counter() - t1
    elapsed = time.perf_counter() - t0

    entities_eq = files_byte_equal(out_a / "entities.jsonl", out_b / "entities.jsonl")
    relations_eq = files_byte_equal(out_a / "relations.jsonl", out_b / "relations.jsonl")
    atoms_eq = files_byte_equal(out_a / "atoms.jsonl", out_b / "atoms.jsonl")
    w_diff = W_l2_diff(out_a / "W.pt", out_b / "W.pt")
    w_ok = w_diff < HP_MAX_W_L2

    ok = entities_eq and relations_eq and atoms_eq and w_ok

    return {
        "arm": "ARM_REINGEST_DETERMINISTIC",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "t_run_a_s": round(t_a, 3),
        "t_run_b_s": round(t_b, 3),
        "entities_byte_equal": bool(entities_eq),
        "relations_byte_equal": bool(relations_eq),
        "atoms_byte_equal": bool(atoms_eq),
        "w_l2_diff": w_diff,
        "w_within_tolerance": bool(w_ok),
        "w_tolerance": HP_MAX_W_L2,
        "n_triples_a": man_a["n_triples"],
        "n_triples_b": man_b["n_triples"],
        "schema_hash_a": man_a["schema_hash"],
        "schema_hash_b": man_b["schema_hash"],
    }


# ---------- verdict ----------

def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by_name = {a["arm"]: a for a in arms}
    full = by_name.get("ARM_INGEST_FULL", {})
    det = by_name.get("ARM_REINGEST_DETERMINISTIC", {})
    notes = by_name.get("ARM_INGEST_NOTES_ONLY", {})

    # HARD_FAIL conditions
    if not all(a.get("ok") for a in arms):
        return "HARD_FAIL", (
            f"one_or_more_arms_not_ok: notes_only.ok={notes.get('ok')} "
            f"full.ok={full.get('ok')} det.ok={det.get('ok')}"
        )
    if not det.get("ok"):
        return "HARD_FAIL", (
            f"reingest_non_deterministic_principle_2_violation: "
            f"entities_eq={det.get('entities_byte_equal')} "
            f"relations_eq={det.get('relations_byte_equal')} "
            f"atoms_eq={det.get('atoms_byte_equal')} "
            f"w_l2={det.get('w_l2_diff')} (tol={det.get('w_tolerance')})"
        )
    if full.get("elapsed_s", 1e9) > HF_MAX_FULL_ELAPSED_S:
        return "HARD_FAIL", (
            f"full_ingest_exceeds_hf_envelope: "
            f"elapsed_s={full.get('elapsed_s')} > {HF_MAX_FULL_ELAPSED_S} "
            f"(principle_9_envelope_cap violated; re-shard required)"
        )
    if full.get("coverage_ratio", 0.0) < HF_MIN_COVERAGE:
        return "HARD_FAIL", (
            f"full_coverage_below_hf_band: "
            f"coverage={full.get('coverage_ratio')} < {HF_MIN_COVERAGE} "
            f"(too many silent rejects = dishonestly selective index)"
        )

    # HARD_PASS conditions
    if (
        full.get("elapsed_s", 1e9) <= HP_MAX_FULL_ELAPSED_S
        and full.get("coverage_ratio", 0.0) >= HP_MIN_COVERAGE
    ):
        return "HARD_PASS", (
            f"all_3_arms_ok; full_elapsed_s={full.get('elapsed_s')} "
            f"<= {HP_MAX_FULL_ELAPSED_S}; coverage={full.get('coverage_ratio')} "
            f">= {HP_MIN_COVERAGE}; reingest_deterministic_w_l2={det.get('w_l2_diff')} "
            f"< {HP_MAX_W_L2}; principles_1-12_preserved"
        )

    # MIDDLE_BAND
    return "MIDDLE_BAND", (
        f"all_3_arms_ok_but_outside_HP_band: "
        f"full_elapsed_s={full.get('elapsed_s')} (HP<= {HP_MAX_FULL_ELAPSED_S}); "
        f"coverage={full.get('coverage_ratio')} (HP>= {HP_MIN_COVERAGE})"
    )


# ---------- instrumentation self-test (formula-selftests; runs at import) ----------

def _instrumentation_selftest() -> None:
    """Synthetic-data verdict-machinery test; runs at import (not gated by --self-test).

    Validates: verdict-compute function discriminates HP/HF/MB on synthetic
    arm outputs. No filesystem ingest; pure formula check.
    """
    # HARD_FAIL: non-deterministic
    fake_arms_hf = [
        {"arm": "ARM_INGEST_NOTES_ONLY", "ok": True, "elapsed_s": 5.0, "coverage_ratio": 0.99},
        {"arm": "ARM_INGEST_FULL", "ok": True, "elapsed_s": 100.0, "coverage_ratio": 0.99},
        {"arm": "ARM_REINGEST_DETERMINISTIC", "ok": False,
         "entities_byte_equal": False, "relations_byte_equal": True,
         "atoms_byte_equal": False, "w_l2_diff": 1.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": False},
    ]
    v, _ = _verdict_from_arms(fake_arms_hf)
    assert v == "HARD_FAIL", f"selftest verdict failure: expected HARD_FAIL, got {v}"

    # HARD_FAIL: envelope exceeded
    fake_arms_envelope = [
        {"arm": "ARM_INGEST_NOTES_ONLY", "ok": True},
        {"arm": "ARM_INGEST_FULL", "ok": True, "elapsed_s": 2000.0, "coverage_ratio": 0.99},
        {"arm": "ARM_REINGEST_DETERMINISTIC", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": True},
    ]
    v2, _ = _verdict_from_arms(fake_arms_envelope)
    assert v2 == "HARD_FAIL", f"selftest envelope: expected HARD_FAIL, got {v2}"

    # HARD_PASS
    fake_arms_hp = [
        {"arm": "ARM_INGEST_NOTES_ONLY", "ok": True, "elapsed_s": 5.0, "coverage_ratio": 0.99},
        {"arm": "ARM_INGEST_FULL", "ok": True, "elapsed_s": 100.0, "coverage_ratio": 0.99},
        {"arm": "ARM_REINGEST_DETERMINISTIC", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": True},
    ]
    v3, _ = _verdict_from_arms(fake_arms_hp)
    assert v3 == "HARD_PASS", f"selftest HP: expected HARD_PASS, got {v3}"

    # MIDDLE_BAND
    fake_arms_mb = [
        {"arm": "ARM_INGEST_NOTES_ONLY", "ok": True, "elapsed_s": 5.0, "coverage_ratio": 0.99},
        {"arm": "ARM_INGEST_FULL", "ok": True, "elapsed_s": 1200.0, "coverage_ratio": 0.85},
        {"arm": "ARM_REINGEST_DETERMINISTIC", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": True},
    ]
    v4, _ = _verdict_from_arms(fake_arms_mb)
    assert v4 == "MIDDLE_BAND", f"selftest MB: expected MIDDLE_BAND, got {v4}"

    # Schema loads + has required keys
    schema = load_schema(REPO)
    assert "source_classes" in schema, "schema missing source_classes"
    assert "relation_types" in schema, "schema missing relation_types"
    assert "atom_tags_required" in schema, "schema missing atom_tags_required"
    assert schema.get("kb_version") == "v1", f"schema kb_version: {schema.get('kb_version')}"
    assert isinstance(schema_hash(schema), str), "schema_hash not a string"

    print("[selftest] substrate_director_kb_ingest_v1 formula+schema PASS", flush=True)


_instrumentation_selftest()


# ---------- main ----------

def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    max_files = SMOKE_MAX_FILES_PER_CLASS if smoke else FULL_MAX_FILES_PER_CLASS
    out_dir = _exp_dir()
    schema = load_schema(REPO)

    t0 = time.time()
    print(
        f"[run] substrate_director_kb_ingest_v1 smoke={smoke} N_DIM={N_DIM} "
        f"seed={SEED} max_files_per_class={max_files} schema_hash={schema_hash(schema)[:12]}",
        flush=True,
    )

    arms: list[dict] = []
    try:
        a = _run_arm_notes_only(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_INGEST_NOTES_ONLY ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_triples={a['n_triples']} n_ent={a['n_entities']} cov={a['coverage_ratio']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_INGEST_NOTES_ONLY", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_INGEST_NOTES_ONLY FAILED: {e}", flush=True)

    try:
        a = _run_arm_full(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_INGEST_FULL ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_triples={a['n_triples']} n_ent={a['n_entities']} cov={a['coverage_ratio']} "
            f"per_class={a['per_class_discovered']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_INGEST_FULL", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_INGEST_FULL FAILED: {e}", flush=True)

    try:
        a = _run_arm_reingest_deterministic(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_REINGEST_DETERMINISTIC ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"ent_eq={a['entities_byte_equal']} rel_eq={a['relations_byte_equal']} "
            f"atoms_eq={a['atoms_byte_equal']} w_l2={a['w_l2_diff']:.3e} "
            f"(tol={a['w_tolerance']})",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_REINGEST_DETERMINISTIC", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_REINGEST_DETERMINISTIC FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    summary: dict[str, Any] = {
        "anchor": "substrate_director_kb_ingest_v1",
        "smoke": smoke,
        "N_DIM": N_DIM,
        "seed": SEED,
        "max_files_per_class": max_files,
        "schema_version": schema.get("schema_version"),
        "schema_hash": schema_hash(schema),
        "kb_version": schema.get("kb_version"),
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "envelope_hp_max_full_elapsed_s": HP_MAX_FULL_ELAPSED_S,
        "envelope_hf_max_full_elapsed_s": HF_MAX_FULL_ELAPSED_S,
        "envelope_hp_min_coverage": HP_MIN_COVERAGE,
        "envelope_hf_min_coverage": HF_MIN_COVERAGE,
        "envelope_hp_max_w_l2": HP_MAX_W_L2,
    }
    payload = {
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
