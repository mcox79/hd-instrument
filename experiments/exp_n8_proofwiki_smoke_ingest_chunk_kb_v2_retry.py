"""n8_proofwiki_smoke_ingest_chunk_kb_v2_retry -- v1 + retry + cache fallback.

USER 2026-06-27 NO LOCAL + GPU+CPU idle. exp_dev 2026-06-27 cell 2.

PROVENANCE: v1 (exp_n8_proofwiki_smoke_ingest_chunk_kb_v1) HARD_FAILed
because website returned 0 bytes (transient network failure). v2_retry:
  - uses fetch_and_materialize_proofwiki_v2_retry which adds 3-step
    exponential-backoff retry (1s, 5s, 25s) on each HTTP request
  - falls back to local cache at data/math_kb_cache/proofwiki/_export.xml
    if remote-fetch all-retries fail
  - the 10-page pre-populate step builds the local cache before relying
    on it as a fallback (so a subsequent full run can recover even if
    network fully down)

Otherwise mechanically identical to v1: same 4 arms, same pre-reg bands,
same META rules, same chunk-ingest pipeline, same probe titles.

Pre-reg: preregs/2026-06-27_n8_proofwiki_smoke_ingest_chunk_kb_v2_retry.md

ARMS (4 mandatory; verbatim v1):
  ARM_BASELINE_FILENAME_QUERY -- query existing v1 filename-metadata KB
  ARM_SMOKE_INGEST_500 -- fetch (RETRY+FALLBACK) + materialize + chunk-
    ingest + query probes
  ARM_FULL_N_PREVIEW_DISCRIMINATOR -- analytical scaling check
  ARM_CONTAMINATION_CONTROL -- non-math probes

PRE-REG BANDS (LOCKED; identical to v1):
  HP_TOP1_COSINE_MIN = 0.85
  HP_CONTAMINATION_MAX = 0.5
  HP_ANALYTICAL_SCALING_REQUIRED = True
  N_FULL_PROJECTION = 35000
  HARD_FAIL_CARDINALITY_BREACH if observed_chunks out of band

META_RULE_H cardinality_ok mandatory.
META_RULE_J no-silent-except: fetch errors recorded + halt OR re-raise.
META_RULE_K smoke fires discriminator: ARM_FULL_N_PREVIEW arm.
META_RULE_L band-floor strictly-above-floor.

PROT-020: numpy/no-torch -> remote_cpu_queue.

ASCII-only. Cell-author smoke uses MAX_PAGES=20.
Author: exp_dev 2026-06-27 (under Research lead).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_metrics,
)

from hdlab.director_kb import (
    load_schema,
    schema_hash,
)
from hdlab.director_kb_chunk_ingest import (
    build_chunk_plan,
    run_chunk_ingest,
)
from hdlab.director_kb_math_sources import (
    fetch_and_materialize_proofwiki_v2_retry,  # v2_retry function
    PROOFWIKI_PROBE_TITLES,
)
from hdlab.director_kb_query import DirectorKBQuery

ANCHOR_NAME = "n8_proofwiki_smoke_ingest_chunk_kb_v2_retry"
CORPUS_PROVENANCE = "proofwiki_featured_pages_cc_by_sa_3_0_chunk_ingest_v2_retry"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# ---------------- pre-reg bands (LOCKED; verbatim v1) ----------------
HP_TOP1_COSINE_MIN = 0.85
HP_CONTAMINATION_MAX = 0.5
HP_TOP1_MEAN_MIN_MB = 0.70
N_FULL_PROJECTION = 35000
HARD_FAIL_CHUNKS_MIN_SMOKE = 60
HARD_FAIL_CHUNKS_MIN_FULL = 1500
HARD_FAIL_CHUNKS_MAX_FULL = 4000

# ---------------- config ----------------
N_DIM = 2048
SEED = 17

THEOREM_PROBES = [
    "Cauchy-Schwarz Inequality",
    "Pythagoras Theorem",
    "Bayes Theorem",
    "Euler-Lagrange Equation",
    "Mean Value Theorem",
]
THEOREM_CONTENT_KEYWORDS = [
    ["cauchy", "schwarz", "inequality"],
    ["pythagoras", "right triangle", "hypotenuse"],
    ["bayes", "posterior", "prior"],
    ["euler", "lagrange", "stationary", "functional"],
    ["mean value", "derivative", "interval"],
]
CONTAMINATION_PROBES = [
    "Banana Republic",
    "Quarterly Earnings Report",
    "Soccer Tournament Schedule",
]

if SMOKE:
    MAX_PAGES = 20
    EXPECTED_N_CHUNKS_MIN = HARD_FAIL_CHUNKS_MIN_SMOKE
    EXPECTED_N_CHUNKS_MAX = 1000
else:
    MAX_PAGES = 500
    EXPECTED_N_CHUNKS_MIN = HARD_FAIL_CHUNKS_MIN_FULL
    EXPECTED_N_CHUNKS_MAX = HARD_FAIL_CHUNKS_MAX_FULL

# Pre-populate cache MAX_PAGES (used by v2 to seed local cache before
# relying on it as a fallback). Always small (10 pages) regardless of
# RUN_MODE so this step is cheap.
PREPOPULATE_CACHE_PAGES = 10

CONFIG_VERSION = (
    "proofwiki_v2_retry: N_DIM=%d SEED=%d MAX_PAGES=%d mode=%s "
    "HP_top1>=%.2f HP_contam<%.2f n_probes=%d n_contam=%d "
    "chunks_band=[%d,%d] N_FULL=%d retry=[1s,5s,25s] cache_seed=%d"
) % (
    N_DIM, SEED, MAX_PAGES, RUN_MODE,
    HP_TOP1_COSINE_MIN, HP_CONTAMINATION_MAX,
    len(THEOREM_PROBES), len(CONTAMINATION_PROBES),
    EXPECTED_N_CHUNKS_MIN, EXPECTED_N_CHUNKS_MAX,
    N_FULL_PROJECTION, PREPOPULATE_CACHE_PAGES,
)


# ---------------- helpers (verbatim v1) ----------------


def _content_match(chunk_body: str, keywords: list[str]) -> bool:
    body_lower = chunk_body.lower()
    return any(kw in body_lower for kw in keywords)


def _analytical_scaling(tau_smoke: float, n_chunks_observed: int,
                        n_full: int = N_FULL_PROJECTION) -> float:
    if n_chunks_observed <= 0:
        return float("inf")
    return tau_smoke * math.sqrt(n_full / n_chunks_observed)


# ---------------- arm implementations ----------------


def run_arm_baseline_filename_query() -> dict:
    t0 = time.perf_counter()
    kb_v1_dir = REPO / "data" / "substrate_director_kb_v1"
    arm_body: dict = {
        "arm": "ARM_BASELINE_FILENAME_QUERY",
        "kb_dir": str(kb_v1_dir),
        "kb_v1_present": kb_v1_dir.exists(),
        "per_probe": [],
        "wall_s": 0.0,
        "errors": [],
    }
    if not kb_v1_dir.exists():
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = True
        arm_body["note"] = "v1 KB not present; baseline informational"
        return arm_body
    try:
        kb = DirectorKBQuery(kb_v1_dir)
    except Exception as e:
        arm_body["errors"].append(f"load_kb: {type(e).__name__}: {e}")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body
    for probe in THEOREM_PROBES:
        try:
            res = kb.query(probe, schema_version=kb.schema_version,
                            k=3, filename_contains=probe.split()[0])
            top_k = res.get("top_k_atoms", []) or []
            if top_k:
                top1 = top_k[0]
                arm_body["per_probe"].append({
                    "probe": probe,
                    "top1_cosine": float(top1.get("confidence", 0.0) or 0.0),
                    "top1_entity": top1.get("entity") or top1.get("ent_name"),
                })
            else:
                arm_body["per_probe"].append({
                    "probe": probe, "top1_cosine": 0.0, "top1_entity": None,
                })
        except Exception as e:
            arm_body["errors"].append(f"{probe}: {type(e).__name__}: {e}")
            arm_body["per_probe"].append({
                "probe": probe, "top1_cosine": 0.0, "top1_entity": None,
            })
    arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
    arm_body["ok"] = len(arm_body["errors"]) == 0
    return arm_body


def run_arm_smoke_ingest_500(workdir: Path) -> dict:
    """v2_retry: uses retry-aware fetch + local-cache fallback."""
    t0 = time.perf_counter()
    arm_body: dict = {
        "arm": "ARM_SMOKE_INGEST_500",
        "max_pages": int(MAX_PAGES),
        "per_probe": [],
        "wall_s": 0.0,
        "errors": [],
        "fetch_errors": [],
        "fallback_used": False,
    }
    # v2 PRE-POPULATE local cache from small fetch (so if full fetch fails
    # all retries, fallback has SOMETHING). If pre-populate also fails,
    # record but continue -- main fetch may still work.
    prepop_t0 = time.perf_counter()
    try:
        prepop_result = fetch_and_materialize_proofwiki_v2_retry(
            REPO, max_pages=PREPOPULATE_CACHE_PAGES, force=False,
        )
        arm_body["prepopulate_result"] = prepop_result
        if not prepop_result.get("ok"):
            print(f"[arm] pre-populate failed (non-fatal): "
                  f"{prepop_result.get('errors')}", flush=True)
    except Exception as e:
        arm_body["errors"].append(f"prepopulate: {type(e).__name__}: {e}")
    arm_body["prepopulate_wall_s"] = round(time.perf_counter() - prepop_t0, 3)

    # Main fetch
    fetch_t0 = time.perf_counter()
    try:
        mat_result = fetch_and_materialize_proofwiki_v2_retry(
            REPO, max_pages=MAX_PAGES, force=False,
        )
        arm_body["fetch_result"] = mat_result
        arm_body["fallback_used"] = bool(mat_result.get("fallback_used", False))
        if mat_result.get("errors"):
            # Don't treat retry-recovery errors as fatal; only mark
            # fetch_errors if final result is NOT ok
            if not mat_result.get("ok"):
                arm_body["fetch_errors"] = mat_result["errors"]
        n_files = int(mat_result.get("n_files", 0))
    except Exception as e:
        arm_body["errors"].append(f"fetch_materialize: {type(e).__name__}: {e}")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body
    arm_body["n_files_materialized"] = n_files
    arm_body["fetch_wall_s"] = round(time.perf_counter() - fetch_t0, 3)

    if n_files == 0:
        # No files materialized; fetch + fallback both failed
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        arm_body["errors"].append("no_files_materialized_after_retry_and_fallback")
        return arm_body

    # Load schema + build chunk-ingest plan
    schema = load_schema(REPO)
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=("proofwiki",),
    )
    arm_body["plan_proofwiki_files"] = len(plan.get("proofwiki", {}).get("files", []))

    kb_dir = workdir / "kb"
    ingest_t0 = time.perf_counter()
    try:
        manifest = run_chunk_ingest(
            plan=plan,
            out_dir=kb_dir,
            schema=schema,
            n_dim=N_DIM,
            seed=SEED,
            wipe=True,
        )
        arm_body["manifest"] = {
            k: manifest.get(k) for k in (
                "n_entities", "n_relations", "n_atoms", "n_triples", "coverage_ratio",
            )
        }
    except Exception as e:
        arm_body["errors"].append(f"chunk_ingest: {type(e).__name__}: {e}")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body
    arm_body["ingest_wall_s"] = round(time.perf_counter() - ingest_t0, 3)
    n_atoms = int(manifest.get("n_atoms") or 0)
    n_chunks_observed = max(1, n_atoms // 3)
    arm_body["n_chunks_observed"] = int(n_chunks_observed)

    try:
        kb = DirectorKBQuery(kb_dir)
    except Exception as e:
        arm_body["errors"].append(f"load_kb_after_ingest: {type(e).__name__}: {e}")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body

    for probe, keywords in zip(THEOREM_PROBES, THEOREM_CONTENT_KEYWORDS):
        try:
            res = kb.query(probe, schema_version=kb.schema_version,
                            k=5, source_classes={"proofwiki"})
            top_k = res.get("top_k_atoms", []) or []
            if not top_k:
                arm_body["per_probe"].append({
                    "probe": probe, "top1_cosine": 0.0, "top1_entity": None,
                    "content_match": False, "top1_body_preview": None,
                })
                continue
            top1 = top_k[0]
            cos = float(top1.get("confidence", 0.0) or 0.0)
            ent_name = top1.get("entity") or top1.get("ent_name") or ""
            body_preview = ""
            try:
                ent_idx = kb.entity_names.index(ent_name)
                content_rel_idx = None
                try:
                    content_rel_idx = kb.relation_names.index("CHUNK_CONTENT")
                except ValueError:
                    content_rel_idx = None
                for a in kb._atoms_by_s.get(ent_idx, []):
                    if content_rel_idx is not None and a.get("p") == content_rel_idx:
                        body_preview = kb.entity_names[a["o"]] if isinstance(a.get("o"), int) else str(a.get("o"))
                        break
            except (ValueError, IndexError):
                pass
            content_match = _content_match(body_preview, keywords)
            arm_body["per_probe"].append({
                "probe": probe,
                "top1_cosine": cos,
                "top1_entity": ent_name,
                "content_match": bool(content_match),
                "top1_body_preview": body_preview[:200] if body_preview else None,
            })
        except Exception as e:
            arm_body["errors"].append(f"query {probe}: {type(e).__name__}: {e}")
            arm_body["per_probe"].append({
                "probe": probe, "top1_cosine": 0.0, "top1_entity": None,
                "content_match": False, "top1_body_preview": None,
            })

    arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
    arm_body["ok"] = len(arm_body["errors"]) == 0
    return arm_body


def run_arm_full_n_preview_discriminator(smoke_arm: dict) -> dict:
    t0 = time.perf_counter()
    arm_body = {
        "arm": "ARM_FULL_N_PREVIEW_DISCRIMINATOR",
        "n_full_projection": int(N_FULL_PROJECTION),
        "per_probe": [],
        "analytical_scaling_passes": True,
        "wall_s": 0.0,
        "errors": [],
    }
    n_chunks_observed = int(smoke_arm.get("n_chunks_observed", 0))
    arm_body["n_chunks_observed"] = n_chunks_observed
    if n_chunks_observed <= 0:
        arm_body["analytical_scaling_passes"] = False
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        arm_body["errors"].append("n_chunks_observed=0; cannot project to full")
        return arm_body
    for probe_result in smoke_arm.get("per_probe", []):
        tau_smoke = float(probe_result.get("top1_cosine", 0.0))
        tau_full = _analytical_scaling(tau_smoke, n_chunks_observed, N_FULL_PROJECTION)
        passes = tau_full >= HP_TOP1_COSINE_MIN
        arm_body["per_probe"].append({
            "probe": probe_result["probe"],
            "tau_smoke": tau_smoke,
            "tau_full_projected": round(tau_full, 4),
            "passes_scaling": bool(passes),
        })
        if not passes:
            arm_body["analytical_scaling_passes"] = False
    arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
    arm_body["ok"] = True
    return arm_body


def run_arm_contamination_control(workdir: Path) -> dict:
    t0 = time.perf_counter()
    arm_body = {
        "arm": "ARM_CONTAMINATION_CONTROL",
        "per_probe": [],
        "contamination_max_cosine": 0.0,
        "wall_s": 0.0,
        "errors": [],
    }
    kb_dir = workdir / "kb"
    if not kb_dir.exists():
        arm_body["errors"].append("KB dir from smoke arm missing")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body
    try:
        kb = DirectorKBQuery(kb_dir)
    except Exception as e:
        arm_body["errors"].append(f"load_kb: {type(e).__name__}: {e}")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body
    max_cos = 0.0
    for probe in CONTAMINATION_PROBES:
        try:
            res = kb.query(probe, schema_version=kb.schema_version,
                            k=3, source_classes={"proofwiki"})
            top_k = res.get("top_k_atoms", []) or []
            cos = float(top_k[0].get("confidence", 0.0) or 0.0) if top_k else 0.0
            max_cos = max(max_cos, cos)
            arm_body["per_probe"].append({
                "probe": probe,
                "top1_cosine": cos,
                "top1_entity": (top_k[0].get("entity") or top_k[0].get("ent_name")) if top_k else None,
            })
        except Exception as e:
            arm_body["errors"].append(f"{probe}: {type(e).__name__}: {e}")
            arm_body["per_probe"].append({
                "probe": probe, "top1_cosine": 0.0, "top1_entity": None,
            })
    arm_body["contamination_max_cosine"] = round(max_cos, 4)
    arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
    arm_body["ok"] = len(arm_body["errors"]) == 0
    return arm_body


# ---------------- verdict logic (verbatim v1) ----------------


def compute_verdict(arms: list[dict], cardinality_ok: bool) -> Tuple[str, str, Dict]:
    by_name = {a["arm"]: a for a in arms}
    baseline = by_name.get("ARM_BASELINE_FILENAME_QUERY", {})
    smoke = by_name.get("ARM_SMOKE_INGEST_500", {})
    preview = by_name.get("ARM_FULL_N_PREVIEW_DISCRIMINATOR", {})
    contam = by_name.get("ARM_CONTAMINATION_CONTROL", {})

    smoke_per_probe = smoke.get("per_probe", []) or []
    smoke_top1_list = [float(p.get("top1_cosine", 0.0)) for p in smoke_per_probe]
    smoke_top1_min = min(smoke_top1_list) if smoke_top1_list else 0.0
    smoke_top1_mean = float(sum(smoke_top1_list) / len(smoke_top1_list)) if smoke_top1_list else 0.0
    smoke_content_all_match = all(bool(p.get("content_match", False)) for p in smoke_per_probe) if smoke_per_probe else False

    n_chunks = int(smoke.get("n_chunks_observed", 0))
    chunks_in_band = EXPECTED_N_CHUNKS_MIN <= n_chunks <= EXPECTED_N_CHUNKS_MAX

    scaling_passes = bool(preview.get("analytical_scaling_passes", False))
    contam_max = float(contam.get("contamination_max_cosine", 1.0))

    fetch_errors = smoke.get("fetch_errors") or []
    fallback_used = bool(smoke.get("fallback_used", False))

    suspect_1000_with_mismatch = any(
        abs(p.get("top1_cosine", 0.0) - 1.0) < 1e-6 and not p.get("content_match", False)
        for p in smoke_per_probe
    )

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_chunks_observed": n_chunks,
        "chunks_in_band": chunks_in_band,
        "chunks_band": [EXPECTED_N_CHUNKS_MIN, EXPECTED_N_CHUNKS_MAX],
        "smoke_top1_cosine_min": round(smoke_top1_min, 4),
        "smoke_top1_cosine_mean": round(smoke_top1_mean, 4),
        "smoke_content_all_match": smoke_content_all_match,
        "analytical_scaling_passes": scaling_passes,
        "contamination_max_cosine": round(contam_max, 4),
        "fetch_errors": fetch_errors,
        "fallback_used": fallback_used,
        "suspect_1000_with_content_mismatch": suspect_1000_with_mismatch,
        "config_version": CONFIG_VERSION,
        "HP_top1_cosine_min": HP_TOP1_COSINE_MIN,
        "HP_contamination_max": HP_CONTAMINATION_MAX,
        "per_arm_brief": {
            "baseline_ok": baseline.get("ok", False),
            "smoke_ok": smoke.get("ok", False),
            "preview_ok": preview.get("ok", False),
            "contam_ok": contam.get("ok", False),
        },
    }

    if not cardinality_ok:
        return ("HARD_FAIL",
                f"cardinality_breach: n_chunks={n_chunks} not in "
                f"[{EXPECTED_N_CHUNKS_MIN}, {EXPECTED_N_CHUNKS_MAX}] OR arms missing",
                detail)
    if fetch_errors:
        return ("HARD_FAIL",
                f"fetch_errors_non_empty_after_retry_and_fallback: {fetch_errors[:3]} "
                f"(META_RULE_J)", detail)
    if contam_max > HP_CONTAMINATION_MAX:
        return ("HARD_FAIL",
                f"contamination_leak: max_cosine={contam_max:.4f} > "
                f"{HP_CONTAMINATION_MAX} (BIAS-S regime failure)", detail)
    if suspect_1000_with_mismatch:
        return ("HARD_FAIL",
                f"BIAS_Q_suspect_1000_with_content_mismatch: identity-match leak",
                detail)
    if smoke_top1_mean < HP_TOP1_MEAN_MIN_MB:
        return ("HARD_FAIL",
                f"smoke_top1_mean_below_floor: {smoke_top1_mean:.4f} < {HP_TOP1_MEAN_MIN_MB}",
                detail)

    if (smoke_top1_min >= HP_TOP1_COSINE_MIN
            and smoke_content_all_match
            and scaling_passes
            and contam_max < HP_CONTAMINATION_MAX
            and chunks_in_band):
        fallback_note = " (used local cache fallback)" if fallback_used else ""
        return ("HARD_PASS",
                f"chain_grade_proofwiki_smoke_ingest_v2_retry{fallback_note}: "
                f"top1_min={smoke_top1_min:.4f} >= {HP_TOP1_COSINE_MIN}; "
                f"content_all_match=True; analytical_scaling_passes=True; "
                f"contam_max={contam_max:.4f} < {HP_CONTAMINATION_MAX}; "
                f"n_chunks={n_chunks} in band", detail)

    if smoke_top1_mean >= HP_TOP1_MEAN_MIN_MB and not scaling_passes:
        return ("MIDDLE_BAND",
                f"smoke_passes_but_scaling_fails: top1_mean={smoke_top1_mean:.4f} >= "
                f"{HP_TOP1_MEAN_MIN_MB}; analytical_scaling_passes=False; "
                f"needs full-N test cell", detail)
    return ("MIDDLE_BAND",
            f"partial: top1_mean={smoke_top1_mean:.4f}; top1_min={smoke_top1_min:.4f}; "
            f"content_match={smoke_content_all_match}; scaling={scaling_passes}",
            detail)


# ---------------- self-test ----------------


def _selftest():
    print("[selftest] n8_proofwiki_smoke_ingest_chunk_kb_v2_retry starting", flush=True)
    # T1: schema
    schema = load_schema(REPO)
    sc = schema.get("source_classes", {})
    assert "proofwiki" in sc, "T1 schema missing proofwiki source class"
    ents = set(schema.get("entity_types", []))
    for required in ("THEOREM", "DEFINITION", "AXIOM", "PROOF", "MATHEMATICAL_FIELD"):
        assert required in ents, f"T1 schema missing entity_type {required}"
    print(f"[selftest] T1 PASS: schema includes proofwiki + entity_types", flush=True)

    # T2: v2_retry functions importable
    from hdlab.director_kb_math_sources import (
        fetch_and_materialize_proofwiki_v2_retry,
        fetch_proofwiki_featured_v2_retry,
        _http_get_with_retry,
        _http_post_with_retry,
        _local_cache_fallback_proofwiki,
        DEFAULT_RETRY_DELAYS_S,
    )
    assert callable(fetch_and_materialize_proofwiki_v2_retry)
    assert callable(_http_get_with_retry)
    assert callable(_http_post_with_retry)
    assert callable(_local_cache_fallback_proofwiki)
    assert DEFAULT_RETRY_DELAYS_S == (1.0, 5.0, 25.0), \
        f"T2 retry delays wrong: {DEFAULT_RETRY_DELAYS_S}"
    print(f"[selftest] T2 PASS: v2_retry functions importable + retry delays correct", flush=True)

    # T3: retry helper smoke -- call with bogus URL, expect retry exhaustion
    bogus_url = "http://invalid.test.bogus.proofwiki.unreachable.example.invalid"
    t_retry_0 = time.perf_counter()
    data, errors = _http_get_with_retry(
        bogus_url, timeout_s=2,
        retry_delays_s=(0.1, 0.1, 0.1),  # fast retries for selftest
        min_bytes=1,
    )
    t_retry_1 = time.perf_counter() - t_retry_0
    assert data is None, f"T3 expected None on bogus URL, got {len(data) if data else 0} bytes"
    assert len(errors) == 4, f"T3 expected 4 errors (1+3 retries), got {len(errors)}: {errors}"
    assert t_retry_1 < 30, f"T3 retry took too long: {t_retry_1:.1f}s"
    print(f"[selftest] T3 PASS: retry exhaustion on bogus URL in {t_retry_1:.2f}s "
          f"({len(errors)} errors)", flush=True)

    # T4: local cache fallback detection
    fallback = _local_cache_fallback_proofwiki(REPO)
    # No assertion on result -- may or may not exist; just verify callable
    print(f"[selftest] T4 PASS: cache fallback callable (returned: {fallback})", flush=True)

    # T5: analytical scaling math (verbatim v1)
    tau_full = _analytical_scaling(0.85, 100, 35000)
    expected = 0.85 * math.sqrt(35000 / 100)
    assert abs(tau_full - expected) < 1e-6, f"T5 scaling math wrong"
    print(f"[selftest] T5 PASS: analytical scaling math", flush=True)

    # T6: content_match (verbatim v1)
    assert _content_match("This proves Cauchy-Schwarz inequality holds...", ["cauchy"])
    assert not _content_match("Completely unrelated text about cats", ["cauchy"])
    print(f"[selftest] T6 PASS: content_match", flush=True)

    # T7: verdict-machinery synthetic HARD_PASS
    _fake_n_chunks = (EXPECTED_N_CHUNKS_MIN + EXPECTED_N_CHUNKS_MAX) // 2
    fake_hp_arms = [
        {"arm": "ARM_BASELINE_FILENAME_QUERY", "ok": True, "per_probe": []},
        {"arm": "ARM_SMOKE_INGEST_500", "ok": True,
         "n_chunks_observed": _fake_n_chunks, "fetch_errors": [],
         "fallback_used": False,
         "per_probe": [
             {"probe": p, "top1_cosine": 0.90, "content_match": True}
             for p in THEOREM_PROBES
         ]},
        {"arm": "ARM_FULL_N_PREVIEW_DISCRIMINATOR", "ok": True,
         "analytical_scaling_passes": True, "per_probe": []},
        {"arm": "ARM_CONTAMINATION_CONTROL", "ok": True,
         "contamination_max_cosine": 0.30, "per_probe": []},
    ]
    v, msg, det = compute_verdict(fake_hp_arms, cardinality_ok=True)
    assert v == "HARD_PASS", f"T7 expected HARD_PASS, got {v}: {msg}"
    print(f"[selftest] T7 PASS: HARD_PASS synthetic path", flush=True)

    # T8: fallback_used should appear in HARD_PASS verdict message
    fake_fallback_arms = [dict(a) for a in fake_hp_arms]
    fake_fallback_arms[1] = dict(fake_fallback_arms[1])
    fake_fallback_arms[1]["fallback_used"] = True
    v, msg, det = compute_verdict(fake_fallback_arms, cardinality_ok=True)
    assert v == "HARD_PASS", f"T8 expected HARD_PASS with fallback, got {v}"
    assert "fallback" in msg, f"T8 expected fallback note in msg, got {msg}"
    print(f"[selftest] T8 PASS: fallback_used recorded in HARD_PASS verdict", flush=True)

    # T9: cardinality breach
    v, msg, det = compute_verdict(fake_hp_arms, cardinality_ok=False)
    assert v == "HARD_FAIL", f"T9 expected HARD_FAIL on cardinality breach, got {v}"
    print(f"[selftest] T9 PASS: cardinality_breach -> HARD_FAIL", flush=True)

    # T10: pre-reg locks
    assert HP_TOP1_COSINE_MIN == 0.85
    assert HP_CONTAMINATION_MAX == 0.5
    assert N_FULL_PROJECTION == 35000
    print(f"[selftest] T10 PASS: pre-reg envelope constants LOCKED", flush=True)

    print("[selftest] ALL PASS", flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------- main runner ----------------


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    workdir = out_dir / "_workdir"
    if workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True, exist_ok=True)

    print(f"[run] {ANCHOR_NAME} smoke={SMOKE} {CONFIG_VERSION}", flush=True)

    t0 = time.time()
    arms: List[dict] = []

    try:
        a = run_arm_baseline_filename_query()
        arms.append(a)
        print(f"  ARM_BASELINE_FILENAME_QUERY ok={a.get('ok')} "
              f"wall={a.get('wall_s')}s "
              f"n_probes={len(a.get('per_probe', []))}", flush=True)
    except Exception as e:
        arms.append({"arm": "ARM_BASELINE_FILENAME_QUERY", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_BASELINE_FILENAME_QUERY FAILED: {e}", flush=True)

    smoke_arm = None
    try:
        smoke_arm = run_arm_smoke_ingest_500(workdir)
        arms.append(smoke_arm)
        print(f"  ARM_SMOKE_INGEST_500 ok={smoke_arm.get('ok')} "
              f"wall={smoke_arm.get('wall_s')}s "
              f"n_chunks={smoke_arm.get('n_chunks_observed')} "
              f"fallback_used={smoke_arm.get('fallback_used')} "
              f"errors={smoke_arm.get('errors')}", flush=True)
    except Exception as e:
        arms.append({"arm": "ARM_SMOKE_INGEST_500", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_SMOKE_INGEST_500 FAILED: {e}", flush=True)
        raise

    if smoke_arm:
        try:
            a = run_arm_full_n_preview_discriminator(smoke_arm)
            arms.append(a)
            print(f"  ARM_FULL_N_PREVIEW_DISCRIMINATOR ok={a.get('ok')} "
                  f"scaling_passes={a.get('analytical_scaling_passes')}",
                  flush=True)
        except Exception as e:
            arms.append({"arm": "ARM_FULL_N_PREVIEW_DISCRIMINATOR", "ok": False,
                         "error": f"{type(e).__name__}: {e}"})

    try:
        a = run_arm_contamination_control(workdir)
        arms.append(a)
        print(f"  ARM_CONTAMINATION_CONTROL ok={a.get('ok')} "
              f"max_cosine={a.get('contamination_max_cosine')}", flush=True)
    except Exception as e:
        arms.append({"arm": "ARM_CONTAMINATION_CONTROL", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})

    n_arms = len(arms)
    n_chunks_obs = int(smoke_arm.get("n_chunks_observed", 0)) if smoke_arm else 0
    cardinality_ok = (
        n_arms == 4
        and all(a.get("ok") for a in arms)
        and EXPECTED_N_CHUNKS_MIN <= n_chunks_obs <= EXPECTED_N_CHUNKS_MAX
    )

    verdict, vm, detail = compute_verdict(arms, cardinality_ok=cardinality_ok)
    elapsed = round(time.time() - t0, 2)

    schema = load_schema(REPO)
    summary = {
        "anchor": ANCHOR_NAME,
        "smoke": SMOKE,
        "N_DIM": int(N_DIM),
        "seed": int(SEED),
        "config_version": CONFIG_VERSION,
        "schema_version": schema.get("schema_version"),
        "schema_hash": schema_hash(schema),
        "per_arm_metrics": {a["arm"]: a for a in arms},
        "detail": detail,
        "corpus_provenance": CORPUS_PROVENANCE,
        "license_tag": "CC-BY-SA-3.0",
        "attribution": "ProofWiki contributors",
        "zero_llm_calls_at_inference": True,
        "v2_retry_active": True,
    }
    payload = {
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    write_metrics(out_dir, payload)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
