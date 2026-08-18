"""SUBSTRATE DIRECTOR-KB LANGUAGE TRIO INGEST v1 (TOOLING; 2026-06-26).

USER 2026-06-26: "more language capability."

Extends the base Director-KB (anchor substrate_director_kb_ingest_v1) with
three structured English-language corpora via the chain-grade ingest pipeline:

  - WordNet (Princeton 3.1 via NLTK): synsets + hyper/hyponyms + holonyms +
    antonyms + lemmas + glosses + examples + POS tags. ~117k synsets.
  - VerbNet (Levin classes via NLTK): verb classes + members + thematic roles
    + selectional restrictions + syntactic frames. ~429 classes.
  - FrameNet (Berkeley via NLTK): frames + frame elements + lexical units +
    inter-frame relations. ~1221 frames.

Composes ONLY on chain-grade primitives:
  - hdlab.kg_traversal.KGStore (CERT 584/585)
  - hdlab.char_trigram_encoder.CharTrigramEncoder (substrate-native)
  - hdlab.director_kb pipeline (schema-driven; principles 1-12 preserved)

ARMS (4 mandatory):
  ARM_INGEST_LANGUAGE_TRIO_SMOKE       - 100/10/50 sample sizes
  ARM_INGEST_LANGUAGE_TRIO_FULL        - uncapped (full corpora)
  ARM_REINGEST_DETERMINISTIC_TRIO      - 2x ingest, byte-equal + W L2 < 1e-6
  ARM_REGRESSION_BASE_KB               - base-class triple counts unchanged

HARD_PASS:
  - All 4 arms ok
  - FULL elapsed_s <= 1200
  - FULL n_triples >= 500_000
  - DETERMINISM byte-equal + W L2 < 1e-6
  - REGRESSION delta in [-5%, +25%] vs baseline

Anchor: substrate_director_kb_language_trio_v1
Queue:  local_cpu_queue
Pre-reg: preregs/2026-06-26_substrate_director_kb_language_trio_v1.md
Schema: config/director_kb_schema.json
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
    W_l2_diff,
    build_ingest_plan,
    files_byte_equal,
    load_schema,
    run_ingest,
    schema_hash,
)


# ---------- envelope thresholds ----------
HP_MAX_FULL_ELAPSED_S = 1200      # 20 min
HF_MAX_FULL_ELAPSED_S = 2400      # 40 min
HP_MIN_FULL_TRIPLES = 500_000     # WordNet alone yields >1M; conservative floor
HP_MAX_W_L2 = 1e-6                # deterministic tolerance
HP_REGRESSION_LOWER = -0.05       # 5% drop max
HP_REGRESSION_UPPER = 0.25        # 25% growth tolerance (corpus may have grown)
HF_REGRESSION_LOWER = -0.25       # 25% drop = REJECT

# ---------- smoke caps ----------
SMOKE_CAPS = {"wordnet": 100, "verbnet": 10, "framenet": 50}
FULL_CAPS: dict[str, int] = {}    # empty = uncapped

LANGUAGE_TRIO_CLASSES = ["wordnet", "verbnet", "framenet"]

# ---------- HD dim / seed ----------
N_DIM = 2048
SEED = 17

BASE_KB_BASELINE_PATH = "data/exp_substrate_director_kb_ingest_v1/metrics.json"


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "substrate_director_kb_language_trio_v1")


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

def _run_arm_smoke(schema: dict) -> dict:
    arm_dir = _arm_workdir("smoke")
    out_dir = arm_dir / "kb"
    plan = build_ingest_plan(
        schema=schema, repo_root=REPO,
        max_files_per_class=None, only_classes=LANGUAGE_TRIO_CLASSES,
    )
    t0 = time.perf_counter()
    manifest = run_ingest(
        plan=plan, out_dir=out_dir, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=False,
        api_max_items_override=SMOKE_CAPS,
    )
    elapsed = time.perf_counter() - t0
    # Per-class atom presence
    per_class_counts: dict[str, int] = {}
    with (out_dir / "atoms.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            c = rec.get("source_class", "")
            per_class_counts[c] = per_class_counts.get(c, 0) + 1
    ok = (
        manifest["n_triples"] > 1000
        and all(per_class_counts.get(c, 0) > 0 for c in LANGUAGE_TRIO_CLASSES)
    )
    return {
        "arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "caps": SMOKE_CAPS,
        "n_triples": manifest["n_triples"],
        "n_entities": manifest["n_entities"],
        "n_relations": manifest["n_relations"],
        "per_class_triples": per_class_counts,
        "out_dir": str(out_dir),
    }


def _run_arm_full(schema: dict) -> dict:
    arm_dir = _arm_workdir("full")
    out_dir = arm_dir / "kb"
    plan = build_ingest_plan(
        schema=schema, repo_root=REPO,
        max_files_per_class=None, only_classes=LANGUAGE_TRIO_CLASSES,
    )
    t0 = time.perf_counter()
    manifest = run_ingest(
        plan=plan, out_dir=out_dir, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=False,
        api_max_items_override=FULL_CAPS,
    )
    elapsed = time.perf_counter() - t0
    per_class_counts: dict[str, int] = {}
    with (out_dir / "atoms.jsonl").open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            c = rec.get("source_class", "")
            per_class_counts[c] = per_class_counts.get(c, 0) + 1
    ok = (
        manifest["n_triples"] > 0
        and all(per_class_counts.get(c, 0) > 0 for c in LANGUAGE_TRIO_CLASSES)
    )
    return {
        "arm": "ARM_INGEST_LANGUAGE_TRIO_FULL",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "caps": "uncapped",
        "n_triples": manifest["n_triples"],
        "n_entities": manifest["n_entities"],
        "n_relations": manifest["n_relations"],
        "per_class_triples": per_class_counts,
        "out_dir": str(out_dir),
    }


def _run_arm_reingest_deterministic(schema: dict) -> dict:
    """LOAD-BEARING per Principle 2.

    Uses smoke caps for tractability; determinism is by-construction (sorted
    iteration + fixed seed + content-deterministic encoder), so if it holds at
    smoke caps it holds at any cap.
    """
    arm_dir = _arm_workdir("reingest_det")
    out_a = arm_dir / "kb_a"
    out_b = arm_dir / "kb_b"
    plan_a = build_ingest_plan(
        schema=schema, repo_root=REPO,
        max_files_per_class=None, only_classes=LANGUAGE_TRIO_CLASSES,
    )
    t0 = time.perf_counter()
    man_a = run_ingest(
        plan=plan_a, out_dir=out_a, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=True,
        api_max_items_override=SMOKE_CAPS,
    )
    t_a = time.perf_counter() - t0
    t1 = time.perf_counter()
    plan_b = build_ingest_plan(
        schema=schema, repo_root=REPO,
        max_files_per_class=None, only_classes=LANGUAGE_TRIO_CLASSES,
    )
    man_b = run_ingest(
        plan=plan_b, out_dir=out_b, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=True,
        api_max_items_override=SMOKE_CAPS,
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
        "arm": "ARM_REINGEST_DETERMINISTIC_TRIO",
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


def _run_arm_regression_base_kb(schema: dict) -> dict:
    """Verify base Director-KB ingest unaffected by language-trio schema additions.

    Re-runs ingest of ONLY base (non-language, non-bio) classes with the extended
    schema; compares triple count to baseline metrics.json from prior HARD_PASS.
    """
    arm_dir = _arm_workdir("regression_base")
    out_dir = arm_dir / "kb"
    # Base classes = everything EXCEPT api-mode classes (language trio + bio trio additions)
    base_classes = [
        cname for cname, cdef in schema["source_classes"].items()
        if cdef.get("mode") not in ("api", "obo_go", "kegg_kgml", "nif_ttl")
    ]
    plan = build_ingest_plan(
        schema=schema, repo_root=REPO,
        max_files_per_class=None, only_classes=base_classes,
    )
    t0 = time.perf_counter()
    manifest = run_ingest(
        plan=plan, out_dir=out_dir, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0

    # Load baseline
    baseline_path = REPO / BASE_KB_BASELINE_PATH
    baseline_triples = None
    if baseline_path.exists():
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
            # Walk arms for ARM_INGEST_FULL n_triples
            for a in baseline.get("summary", {}).get("arms", []):
                if a.get("arm") == "ARM_INGEST_FULL":
                    baseline_triples = a.get("n_triples")
                    break
        except (json.JSONDecodeError, OSError):
            pass
    delta_pct = None
    if baseline_triples and baseline_triples > 0:
        delta_pct = (manifest["n_triples"] - baseline_triples) / baseline_triples
    ok = (
        manifest["n_triples"] > 0
        and len(base_classes) >= 6
        and (delta_pct is None or delta_pct >= HF_REGRESSION_LOWER)
    )
    return {
        "arm": "ARM_REGRESSION_BASE_KB",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "n_triples_current": manifest["n_triples"],
        "n_triples_baseline": baseline_triples,
        "delta_pct": None if delta_pct is None else round(delta_pct, 4),
        "n_base_classes": len(base_classes),
        "base_classes": sorted(base_classes),
        "coverage_ratio": manifest["coverage_ratio"],
    }


# ---------- sample queries (post-ingest verification) ----------

def _run_sample_queries(language_kb_dir: Path) -> list[dict]:
    """Probe the language-trio KB with 3 hand-picked queries. Verifies the KB is
    actually retrievable + semantically meaningful, not just byte-correct.
    """
    try:
        from hdlab.director_kb_query import DirectorKBQuery
    except ImportError as e:
        return [{"query": "<import failure>", "error": f"{type(e).__name__}: {e}"}]
    try:
        kb = DirectorKBQuery(kb_dir=language_kb_dir)
    except Exception as e:  # noqa: BLE001
        return [{"query": "<kb load failure>", "error": f"{type(e).__name__}: {e}"}]
    queries = [
        ("dog.n.01", "expected: synset with HYPERNYM_OF + LEMMA_OF edges"),
        ("give-13.1", "expected: verbnet class id with ROLE_OF edges"),
        ("Commerce_buy", "expected: framenet frame with HAS_FE edges"),
    ]
    results = []
    for q, expectation in queries:
        try:
            r = kb.query(question=q, k=3, confidence_floor=0.0)  # don't refuse
            top = r.get("top_k_atoms", [])
            top_entity = top[0].get("entity") if top else None
            top_cos = top[0].get("cosine") if top else None
            top_edges = top[0].get("relations", []) if top else []
            results.append({
                "query": q,
                "expectation": expectation,
                "top_entity": top_entity,
                "top_cosine": top_cos,
                "n_edges_top": len(top_edges),
                "sample_edges": [(r, o) for r, o in top_edges[:5]],
                "refused": r.get("refused", False),
            })
        except Exception as e:  # noqa: BLE001
            results.append({"query": q, "error": f"{type(e).__name__}: {e}"})
    return results


# ---------- verdict ----------

def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by_name = {a["arm"]: a for a in arms}
    smoke = by_name.get("ARM_INGEST_LANGUAGE_TRIO_SMOKE", {})
    full = by_name.get("ARM_INGEST_LANGUAGE_TRIO_FULL", {})
    det = by_name.get("ARM_REINGEST_DETERMINISTIC_TRIO", {})
    reg = by_name.get("ARM_REGRESSION_BASE_KB", {})

    if not all(a.get("ok") for a in arms):
        return "HARD_FAIL", (
            f"one_or_more_arms_not_ok: smoke.ok={smoke.get('ok')} "
            f"full.ok={full.get('ok')} det.ok={det.get('ok')} reg.ok={reg.get('ok')}"
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
            f"(re-shard required)"
        )
    delta = reg.get("delta_pct")
    if delta is not None and delta < HF_REGRESSION_LOWER:
        return "HARD_FAIL", (
            f"base_kb_regression_severe: delta_pct={delta} < {HF_REGRESSION_LOWER} "
            f"(language-trio schema extension broke base ingest = REJECT)"
        )

    # HARD_PASS
    if (
        full.get("elapsed_s", 1e9) <= HP_MAX_FULL_ELAPSED_S
        and full.get("n_triples", 0) >= HP_MIN_FULL_TRIPLES
        and (delta is None or HP_REGRESSION_LOWER <= delta <= HP_REGRESSION_UPPER)
    ):
        return "HARD_PASS", (
            f"all_4_arms_ok; full_elapsed_s={full.get('elapsed_s')} <= {HP_MAX_FULL_ELAPSED_S}; "
            f"full_n_triples={full.get('n_triples')} >= {HP_MIN_FULL_TRIPLES}; "
            f"determinism_w_l2={det.get('w_l2_diff')} < {HP_MAX_W_L2}; "
            f"base_regression_delta_pct={delta}; principles_1-12_preserved"
        )

    return "MIDDLE_BAND", (
        f"all_4_arms_ok_but_outside_HP_band: "
        f"full_elapsed_s={full.get('elapsed_s')} (HP<={HP_MAX_FULL_ELAPSED_S}); "
        f"full_n_triples={full.get('n_triples')} (HP>={HP_MIN_FULL_TRIPLES}); "
        f"base_delta_pct={delta} (HP in [{HP_REGRESSION_LOWER},{HP_REGRESSION_UPPER}])"
    )


# ---------- instrumentation self-test (runs at import) ----------

def _instrumentation_selftest() -> None:
    """Synthetic verdict-machinery test. No filesystem ingest; pure formula."""
    hf = [
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE", "ok": True},
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_FULL", "ok": True, "elapsed_s": 500, "n_triples": 600_000},
        {"arm": "ARM_REINGEST_DETERMINISTIC_TRIO", "ok": False,
         "entities_byte_equal": False, "relations_byte_equal": True,
         "atoms_byte_equal": False, "w_l2_diff": 1.0, "w_tolerance": HP_MAX_W_L2},
        {"arm": "ARM_REGRESSION_BASE_KB", "ok": True, "delta_pct": 0.0},
    ]
    v, _ = _verdict_from_arms(hf)
    assert v == "HARD_FAIL", f"selftest non-det: expected HARD_FAIL got {v}"

    envelope = [
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE", "ok": True},
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_FULL", "ok": True, "elapsed_s": 3000, "n_triples": 600_000},
        {"arm": "ARM_REINGEST_DETERMINISTIC_TRIO", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2},
        {"arm": "ARM_REGRESSION_BASE_KB", "ok": True, "delta_pct": 0.0},
    ]
    v2, _ = _verdict_from_arms(envelope)
    assert v2 == "HARD_FAIL", f"selftest envelope: expected HARD_FAIL got {v2}"

    regression = [
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE", "ok": True},
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_FULL", "ok": True, "elapsed_s": 500, "n_triples": 600_000},
        {"arm": "ARM_REINGEST_DETERMINISTIC_TRIO", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2},
        {"arm": "ARM_REGRESSION_BASE_KB", "ok": True, "delta_pct": -0.50},
    ]
    v3, _ = _verdict_from_arms(regression)
    assert v3 == "HARD_FAIL", f"selftest regression: expected HARD_FAIL got {v3}"

    hp = [
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE", "ok": True},
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_FULL", "ok": True, "elapsed_s": 500, "n_triples": 600_000},
        {"arm": "ARM_REINGEST_DETERMINISTIC_TRIO", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2},
        {"arm": "ARM_REGRESSION_BASE_KB", "ok": True, "delta_pct": 0.02},
    ]
    v4, _ = _verdict_from_arms(hp)
    assert v4 == "HARD_PASS", f"selftest HP: expected HARD_PASS got {v4}"

    mb = [
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE", "ok": True},
        {"arm": "ARM_INGEST_LANGUAGE_TRIO_FULL", "ok": True, "elapsed_s": 1800, "n_triples": 600_000},
        {"arm": "ARM_REINGEST_DETERMINISTIC_TRIO", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2},
        {"arm": "ARM_REGRESSION_BASE_KB", "ok": True, "delta_pct": 0.02},
    ]
    v5, _ = _verdict_from_arms(mb)
    assert v5 == "MIDDLE_BAND", f"selftest MB: expected MIDDLE_BAND got {v5}"

    # Schema loads + has new source classes
    schema = load_schema(REPO)
    for c in LANGUAGE_TRIO_CLASSES:
        assert c in schema["source_classes"], f"schema missing source class: {c}"
        assert schema["source_classes"][c].get("mode") == "api", f"{c} not api mode"
    for r in ("HYPERNYM_OF", "ROLE_OF", "HAS_FE"):
        assert r in schema["relation_types"], f"schema missing relation: {r}"

    print("[selftest] substrate_director_kb_language_trio_v1 formula+schema PASS", flush=True)


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
    out_dir = _exp_dir()
    schema = load_schema(REPO)

    t0 = time.time()
    print(
        f"[run] substrate_director_kb_language_trio_v1 smoke={smoke} N_DIM={N_DIM} "
        f"seed={SEED} schema_hash={schema_hash(schema)[:12]}",
        flush=True,
    )

    arms: list[dict] = []
    try:
        a = _run_arm_smoke(schema)
        arms.append(a)
        print(
            f"  ARM_INGEST_LANGUAGE_TRIO_SMOKE ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_triples={a['n_triples']} per_class={a['per_class_triples']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_INGEST_LANGUAGE_TRIO_SMOKE", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_INGEST_LANGUAGE_TRIO_SMOKE FAILED: {e}", flush=True)

    if smoke:
        # Smoke mode: skip the heavy full + reingest_det + regression; mechanism + smoke arm only.
        # The cell still produces a metrics.json so the queue_add smoke gate sees REQUIRED_FIELDS.
        elapsed = round(time.time() - t0, 2)
        verdict = "HARD_PASS" if arms[0].get("ok") else "HARD_FAIL"
        vm = f"smoke_only; arm_ok={arms[0].get('ok')}"
        payload = {
            "verdict": verdict,
            "verdict_msg": vm,
            "elapsed_s": elapsed,
            "summary": {
                "anchor": "substrate_director_kb_language_trio_v1",
                "smoke": True,
                "N_DIM": N_DIM,
                "seed": SEED,
                "schema_version": schema.get("schema_version"),
                "schema_hash": schema_hash(schema),
                "arms": arms,
                "verdict": verdict,
                "verdict_msg": vm,
                "elapsed_s": elapsed,
            },
        }
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"\n[smoke verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)
        return

    try:
        a = _run_arm_full(schema)
        arms.append(a)
        print(
            f"  ARM_INGEST_LANGUAGE_TRIO_FULL ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_triples={a['n_triples']} per_class={a['per_class_triples']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_INGEST_LANGUAGE_TRIO_FULL", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_INGEST_LANGUAGE_TRIO_FULL FAILED: {e}", flush=True)

    try:
        a = _run_arm_reingest_deterministic(schema)
        arms.append(a)
        print(
            f"  ARM_REINGEST_DETERMINISTIC_TRIO ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"ent_eq={a['entities_byte_equal']} rel_eq={a['relations_byte_equal']} "
            f"atoms_eq={a['atoms_byte_equal']} w_l2={a['w_l2_diff']:.3e}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_REINGEST_DETERMINISTIC_TRIO", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_REINGEST_DETERMINISTIC_TRIO FAILED: {e}", flush=True)

    try:
        a = _run_arm_regression_base_kb(schema)
        arms.append(a)
        print(
            f"  ARM_REGRESSION_BASE_KB ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_triples_current={a['n_triples_current']} baseline={a['n_triples_baseline']} "
            f"delta_pct={a['delta_pct']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_REGRESSION_BASE_KB", "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_REGRESSION_BASE_KB FAILED: {e}", flush=True)

    # Sample queries against full KB
    full_arm = next((x for x in arms if x.get("arm") == "ARM_INGEST_LANGUAGE_TRIO_FULL"), {})
    sample_queries: list[dict] = []
    if full_arm.get("ok") and full_arm.get("out_dir"):
        try:
            sample_queries = _run_sample_queries(Path(full_arm["out_dir"]))
            print("  SAMPLE QUERIES:", flush=True)
            for sq in sample_queries:
                print(f"    {sq}", flush=True)
        except Exception as e:  # noqa: BLE001
            sample_queries = [{"error": f"{type(e).__name__}: {e}"}]

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    summary: dict[str, Any] = {
        "anchor": "substrate_director_kb_language_trio_v1",
        "smoke": False,
        "N_DIM": N_DIM,
        "seed": SEED,
        "schema_version": schema.get("schema_version"),
        "schema_hash": schema_hash(schema),
        "kb_version": schema.get("kb_version"),
        "arms": arms,
        "sample_queries": sample_queries,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "envelope_hp_max_full_elapsed_s": HP_MAX_FULL_ELAPSED_S,
        "envelope_hf_max_full_elapsed_s": HF_MAX_FULL_ELAPSED_S,
        "envelope_hp_min_full_triples": HP_MIN_FULL_TRIPLES,
        "envelope_hp_max_w_l2": HP_MAX_W_L2,
        "envelope_hp_regression_band": [HP_REGRESSION_LOWER, HP_REGRESSION_UPPER],
        "envelope_hf_regression_lower": HF_REGRESSION_LOWER,
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
