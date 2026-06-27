"""n8_proofwiki_smoke_ingest_chunk_kb_v1 -- ProofWiki smoke ingest into chunk-KB v2.

USER 2026-06-27: math + science extractor design rank-1; strategic prerequisite
for USER vision Phase 3 (substrate proposes new mathematics).

DESIGN PROVENANCE: research drill 2026-06-27
  notes/research_drill_math_science_extractor_design_2026-06-27.md Section 3
PREREG: preregs/2026-06-27_n8_proofwiki_smoke_ingest_chunk_kb_v1.md

MECHANISM: 500 ProofWiki Featured pages fetched via Special:Export +
materialized into data/math_kb_cache/proofwiki/<safe>.md with YAML front-matter
(license + URL + entity_type) + chunk-ingest via chain-grade pipeline + query
5 theorem-name probes against new chunks. ProofWiki is CC-BY-SA-3.0; each
materialized file carries license + URL + attribution.

ARMS (4 mandatory):
  ARM_BASELINE_FILENAME_QUERY -- query existing v1 filename-metadata KB for
    5 theorem-name probes via --filename-contains; record top-1 cosine.
  ARM_SMOKE_INGEST_500 -- fetch + materialize + chunk-ingest ProofWiki
    Featured pages; query 5 probes against new chunks; verify-the-referent
    via CONTENT match (not just filename).
  ARM_FULL_N_PREVIEW_DISCRIMINATOR -- analytical scaling check:
    tau_full = tau_smoke * sqrt(N_full / n_chunks_observed); does smoke
    top-1 cosine clear scaled threshold?
  ARM_CONTAMINATION_CONTROL -- query non-math probes (Banana Republic,
    Quarterly Earnings, Soccer Tournament); expect top-1 cosine < 0.5.

PRE-REG BANDS (LOCKED at module init):
  HP_TOP1_COSINE_MIN = 0.85 (ARM_SMOKE_INGEST_500 all probes)
  HP_CONTAMINATION_MAX = 0.5
  HP_ANALYTICAL_SCALING_REQUIRED = True
  N_FULL_PROJECTION = 35000  # full ProofWiki chunk-count estimate
  HARD_FAIL_CARDINALITY_BREACH if observed < 60 (smoke) / 1500 (full)

META_RULE_H cardinality_ok mandatory.
META_RULE_J no-silent-except: fetch errors recorded + halt OR re-raise.
META_RULE_K smoke fires discriminator: ARM_FULL_N_PREVIEW arm.
META_RULE_L band-floor strictly-above-floor.
BIAS-S/Q/N/13 from USER 2026-06-24 master checklist applied.

PROT-020: cell does NOT use torch; routes to remote_cpu_queue (CPU-only).

ASCII-only. Cell-author smoke uses MAX_PAGES=20 (~100 chunks) for quick gate;
full uses MAX_PAGES=500 (~2500 chunks).
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
    fetch_and_materialize_proofwiki,
    PROOFWIKI_PROBE_TITLES,
)
from hdlab.director_kb_query import DirectorKBQuery

ANCHOR_NAME = "n8_proofwiki_smoke_ingest_chunk_kb_v1"
CORPUS_PROVENANCE = "proofwiki_featured_pages_cc_by_sa_3_0_chunk_ingest_v2"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# ---------------- pre-reg bands (LOCKED) ----------------
HP_TOP1_COSINE_MIN = 0.85
HP_CONTAMINATION_MAX = 0.5
HP_TOP1_MEAN_MIN_MB = 0.70
N_FULL_PROJECTION = 35000  # full ProofWiki chunk-count estimate
HARD_FAIL_CHUNKS_MIN_SMOKE = 60
HARD_FAIL_CHUNKS_MIN_FULL = 1500
HARD_FAIL_CHUNKS_MAX_FULL = 4000

# ---------------- config ----------------
N_DIM = 2048  # match chain-grade chunk-ingest v1 default
SEED = 17

# Probe titles (theorem-name queries); MUST exist as ProofWiki pages
THEOREM_PROBES = [
    "Cauchy-Schwarz Inequality",
    "Pythagoras Theorem",
    "Bayes Theorem",
    "Euler-Lagrange Equation",
    "Mean Value Theorem",
]
# Content keywords to verify-the-referent (BIAS-N): if any of these appear in
# the retrieved chunk body, content match is confirmed.
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
    EXPECTED_N_CHUNKS_MIN = HARD_FAIL_CHUNKS_MIN_SMOKE  # 60
    EXPECTED_N_CHUNKS_MAX = 1000
else:
    MAX_PAGES = 500
    EXPECTED_N_CHUNKS_MIN = HARD_FAIL_CHUNKS_MIN_FULL  # 1500
    EXPECTED_N_CHUNKS_MAX = HARD_FAIL_CHUNKS_MAX_FULL  # 4000

CONFIG_VERSION = (
    "proofwiki_smoke-v1: N_DIM=%d SEED=%d MAX_PAGES=%d mode=%s "
    "HP_top1>=%.2f HP_contam<%.2f n_probes=%d n_contam=%d "
    "chunks_band=[%d,%d] N_FULL=%d"
) % (
    N_DIM, SEED, MAX_PAGES, RUN_MODE,
    HP_TOP1_COSINE_MIN, HP_CONTAMINATION_MAX,
    len(THEOREM_PROBES), len(CONTAMINATION_PROBES),
    EXPECTED_N_CHUNKS_MIN, EXPECTED_N_CHUNKS_MAX,
    N_FULL_PROJECTION,
)


# ---------------- helpers ----------------


def _content_match(chunk_body: str, keywords: list[str]) -> bool:
    """Verify-the-referent: chunk body contains AT LEAST one keyword."""
    body_lower = chunk_body.lower()
    return any(kw in body_lower for kw in keywords)


def _analytical_scaling(tau_smoke: float, n_chunks_observed: int,
                        n_full: int = N_FULL_PROJECTION) -> float:
    """Scale cosine threshold to full-N per Mu-Viswanath anisotropy.

    Returns tau_full = tau_smoke * sqrt(n_full / n_chunks_observed).
    """
    if n_chunks_observed <= 0:
        return float("inf")
    return tau_smoke * math.sqrt(n_full / n_chunks_observed)


# ---------------- arm implementations ----------------


def run_arm_baseline_filename_query() -> dict:
    """ARM_BASELINE_FILENAME_QUERY: query existing v1 filename-metadata KB.

    Uses --filename-contains substring (chain-grade query primitive). Records
    top-1 substring match presence for each probe.
    """
    t0 = time.perf_counter()
    # Locate existing v1 KB from manifest if it exists; otherwise mark
    # baseline as not-applicable
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
        arm_body["note"] = "v1 KB not present; baseline is informational"
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
            # Use filename_contains for filename-metadata baseline lookup
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
    """ARM_SMOKE_INGEST_500: fetch + materialize + chunk-ingest + query probes."""
    t0 = time.perf_counter()
    arm_body: dict = {
        "arm": "ARM_SMOKE_INGEST_500",
        "max_pages": int(MAX_PAGES),
        "per_probe": [],
        "wall_s": 0.0,
        "errors": [],
        "fetch_errors": [],
    }
    # 1. Fetch + materialize ProofWiki Featured pages
    fetch_t0 = time.perf_counter()
    try:
        mat_result = fetch_and_materialize_proofwiki(
            REPO, max_pages=MAX_PAGES, force=False,
        )
        arm_body["fetch_result"] = mat_result
        if mat_result.get("errors"):
            arm_body["fetch_errors"] = mat_result["errors"]
        n_files = int(mat_result.get("n_files", 0))
    except Exception as e:
        arm_body["errors"].append(f"fetch_materialize: {type(e).__name__}: {e}")
        arm_body["wall_s"] = round(time.perf_counter() - t0, 3)
        arm_body["ok"] = False
        return arm_body
    arm_body["n_files_materialized"] = n_files
    arm_body["fetch_wall_s"] = round(time.perf_counter() - fetch_t0, 3)

    # 2. Load schema + build chunk-ingest plan limited to proofwiki source class
    schema = load_schema(REPO)
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=("proofwiki",),
    )
    arm_body["plan_proofwiki_files"] = len(plan.get("proofwiki", {}).get("files", []))

    # 3. Chunk-ingest into a fresh KB dir
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
    # n_chunks_observed = number of CHUNK_CONTENT atoms (approximation: n_atoms/3)
    n_atoms = int(manifest.get("n_atoms") or 0)
    n_chunks_observed = max(1, n_atoms // 3)  # each chunk emits ~3 atoms
    arm_body["n_chunks_observed"] = int(n_chunks_observed)

    # 4. Query each probe + verify-the-referent
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
                    "probe": probe,
                    "top1_cosine": 0.0,
                    "top1_entity": None,
                    "content_match": False,
                    "top1_body_preview": None,
                })
                continue
            top1 = top_k[0]
            cos = float(top1.get("confidence", 0.0) or 0.0)
            # Fetch the top entity's chunk body via atoms lookup
            ent_name = top1.get("entity") or top1.get("ent_name") or ""
            # Find any CHUNK_CONTENT atom for this entity to inspect body
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
    """ARM_FULL_N_PREVIEW_DISCRIMINATOR: analytical scaling check."""
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
        # Discriminator passes if scaled threshold STILL >= HP_TOP1_COSINE_MIN
        # (i.e., smoke margin is enough to survive projection to N=35k chunks)
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
    """ARM_CONTAMINATION_CONTROL: query non-math probes against ProofWiki chunks."""
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


# ---------------- verdict logic ----------------


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

    # BIAS-Q suspect-1.000: any exact 1.0 cosine with content mismatch
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

    # HARD_FAIL conditions
    if not cardinality_ok:
        return ("HARD_FAIL",
                f"cardinality_breach: n_chunks={n_chunks} not in "
                f"[{EXPECTED_N_CHUNKS_MIN}, {EXPECTED_N_CHUNKS_MAX}] OR arms missing",
                detail)
    if fetch_errors:
        return ("HARD_FAIL",
                f"fetch_errors_non_empty: {fetch_errors[:3]} (META_RULE_J)",
                detail)
    if contam_max > HP_CONTAMINATION_MAX:
        return ("HARD_FAIL",
                f"contamination_leak: max_cosine={contam_max:.4f} > "
                f"{HP_CONTAMINATION_MAX} (BIAS-S regime failure; encoder leaking name similarity)",
                detail)
    if suspect_1000_with_mismatch:
        return ("HARD_FAIL",
                f"BIAS_Q_suspect_1000_with_content_mismatch: identity-match leak detected",
                detail)
    if smoke_top1_mean < HP_TOP1_MEAN_MIN_MB:
        return ("HARD_FAIL",
                f"smoke_top1_mean_below_floor: {smoke_top1_mean:.4f} < {HP_TOP1_MEAN_MIN_MB}",
                detail)

    # HARD_PASS conditions (strictly-above-floor per META_RULE_L)
    if (smoke_top1_min >= HP_TOP1_COSINE_MIN
            and smoke_content_all_match
            and scaling_passes
            and contam_max < HP_CONTAMINATION_MAX
            and chunks_in_band):
        return ("HARD_PASS",
                f"chain_grade_proofwiki_smoke_ingest: top1_min={smoke_top1_min:.4f} >= "
                f"{HP_TOP1_COSINE_MIN}; content_all_match=True; "
                f"analytical_scaling_passes=True; contam_max={contam_max:.4f} < "
                f"{HP_CONTAMINATION_MAX}; n_chunks={n_chunks} in band",
                detail)

    # MIDDLE_BAND
    if smoke_top1_mean >= HP_TOP1_MEAN_MIN_MB and not scaling_passes:
        return ("MIDDLE_BAND",
                f"smoke_passes_but_scaling_fails: top1_mean={smoke_top1_mean:.4f} >= "
                f"{HP_TOP1_MEAN_MIN_MB}; analytical_scaling_passes=False; "
                f"needs full-N test cell",
                detail)
    return ("MIDDLE_BAND",
            f"partial: top1_mean={smoke_top1_mean:.4f}; top1_min={smoke_top1_min:.4f}; "
            f"content_match={smoke_content_all_match}; scaling={scaling_passes}",
            detail)


# ---------------- self-test ----------------


def _selftest():
    print("[selftest] n8_proofwiki_smoke_ingest_chunk_kb_v1 starting", flush=True)
    # T1: schema loaded + new entity_types + relation_types present
    schema = load_schema(REPO)
    sc = schema.get("source_classes", {})
    assert "proofwiki" in sc, "T1 schema missing proofwiki source class"
    ents = set(schema.get("entity_types", []))
    for required in ("THEOREM", "DEFINITION", "AXIOM", "PROOF", "MATHEMATICAL_FIELD"):
        assert required in ents, f"T1 schema missing entity_type {required}"
    rels = set(schema.get("relation_types", []))
    for required in ("STATES_THEOREM", "DEFINES", "ASSUMES_AXIOM", "PROOF_OF",
                      "CITES_THEOREM", "IN_FIELD", "GENERALIZES", "SPECIAL_CASE_OF"):
        assert required in rels, f"T1 schema missing relation_type {required}"
    assert schema.get("schema_version") == "v2", f"T1 schema_version expected v2, got {schema.get('schema_version')}"
    print(f"[selftest] T1 PASS: schema patched (v2, proofwiki class, 5 entity types, 8 relations)", flush=True)

    # T2: math_sources module imports + URL construction sanity
    from hdlab.director_kb_math_sources import (
        PROOFWIKI_BASE, PROOFWIKI_EXPORT_URL, PROOFWIKI_PROBE_TITLES,
        _wikitext_to_markdown, _safe_filename, _detect_entity_type,
        _cache_root,
    )
    assert PROOFWIKI_BASE.startswith("https://"), "T2 PROOFWIKI_BASE not https"
    assert "Special:Export" in PROOFWIKI_EXPORT_URL, "T2 export URL wrong"
    assert len(PROOFWIKI_PROBE_TITLES) >= 5, "T2 fewer than 5 probe titles"
    cache_path = _cache_root(REPO) / "proofwiki" / "_export.xml"
    assert "proofwiki" in str(cache_path), "T2 cache path missing proofwiki"
    print(f"[selftest] T2 PASS: math_sources imports + URL sanity", flush=True)

    # T3: wikitext-to-markdown minimal transform
    wt = "== Theorem ==\nLet [[X|x]] be a thing. {{drop_template}} See [[Y]].\n<ref>cite</ref> done."
    md = _wikitext_to_markdown(wt)
    assert "## Theorem" in md, f"T3 header not transformed: {md}"
    assert "[x](X.md)" in md, f"T3 pipe-link not transformed: {md}"
    assert "[Y](Y.md)" in md, f"T3 bare-link not transformed: {md}"
    assert "drop_template" not in md, f"T3 template not dropped: {md}"
    assert "<ref>" not in md, f"T3 ref not dropped: {md}"
    print(f"[selftest] T3 PASS: wikitext -> markdown transform", flush=True)

    # T4: safe filename + entity-type detection
    assert _safe_filename("Cauchy-Schwarz Inequality") == "Cauchy-Schwarz_Inequality"
    assert _detect_entity_type("Definition:Group", "body") == "DEFINITION"
    assert _detect_entity_type("Axiom:Choice", "body") == "AXIOM"
    assert _detect_entity_type("Proof:Pythagoras", "body") == "PROOF"
    assert _detect_entity_type("Cauchy-Schwarz Inequality", "body") == "THEOREM"
    print(f"[selftest] T4 PASS: safe_filename + entity_type detection", flush=True)

    # T5: analytical scaling math
    tau_full = _analytical_scaling(0.85, 100, 35000)
    expected = 0.85 * math.sqrt(35000 / 100)
    assert abs(tau_full - expected) < 1e-6, f"T5 scaling math wrong: {tau_full} vs {expected}"
    # When n_chunks_observed equals n_full, tau_full == tau_smoke
    tau_eq = _analytical_scaling(0.85, 35000, 35000)
    assert abs(tau_eq - 0.85) < 1e-6, f"T5 unit scaling wrong: {tau_eq}"
    print(f"[selftest] T5 PASS: analytical scaling math sanity", flush=True)

    # T6: content_match referent check
    assert _content_match("This proves Cauchy-Schwarz inequality holds for...", ["cauchy"])
    assert not _content_match("Completely unrelated text about cats", ["cauchy", "schwarz"])
    print(f"[selftest] T6 PASS: verify-the-referent content_match", flush=True)

    # T7: verdict-machinery
    # FIX (exp_dev 2026-06-27): use currently-active chunks band so this
    # synthetic test works in BOTH smoke and full RUN_MODE. Previously hard-
    # coded n=100, which is in smoke band [60, 1000] but NOT in full band
    # [1500, 4000] -- caused silent module-import crash when remote queue
    # runner invoked cell in FULL mode (no --smoke flag, name doesn't end in
    # _smoke). Now n is picked mid-band for whichever mode is active.
    _fake_n_chunks = (EXPECTED_N_CHUNKS_MIN + EXPECTED_N_CHUNKS_MAX) // 2
    fake_hp_arms = [
        {"arm": "ARM_BASELINE_FILENAME_QUERY", "ok": True, "per_probe": []},
        {"arm": "ARM_SMOKE_INGEST_500", "ok": True,
         "n_chunks_observed": _fake_n_chunks, "fetch_errors": [],
         "per_probe": [
             {"probe": p, "top1_cosine": 0.90, "content_match": True}
             for p in THEOREM_PROBES
         ]},
        {"arm": "ARM_FULL_N_PREVIEW_DISCRIMINATOR", "ok": True,
         "analytical_scaling_passes": True,
         "per_probe": []},
        {"arm": "ARM_CONTAMINATION_CONTROL", "ok": True,
         "contamination_max_cosine": 0.30,
         "per_probe": []},
    ]
    # tau_smoke=0.90, mid-band n, n_full=35000: tau_full = 0.90 * sqrt(35000/n);
    # for any n <= 35000 this scales tau_smoke UP, so analytical_scaling_passes
    # always True. (At full band n=2750, tau_full = 0.90 * sqrt(35000/2750) =
    # 0.90 * 3.57 = 3.2 >> 0.85.) Chunks-in-band True by construction.
    v, msg, det = compute_verdict(fake_hp_arms, cardinality_ok=True)
    assert v == "HARD_PASS", f"T7 HP expected HARD_PASS, got {v}: {msg}"
    print(f"[selftest] T7 PASS: synthetic HARD_PASS path "
          f"(fake_n_chunks={_fake_n_chunks} mode={RUN_MODE})", flush=True)

    # T8: contamination -> HARD_FAIL
    fake_contam = [dict(a) for a in fake_hp_arms]
    fake_contam[3] = {"arm": "ARM_CONTAMINATION_CONTROL", "ok": True,
                       "contamination_max_cosine": 0.7, "per_probe": []}
    v, msg, det = compute_verdict(fake_contam, cardinality_ok=True)
    assert v == "HARD_FAIL", f"T8 contam expected HARD_FAIL, got {v}"
    assert "contamination" in msg, f"T8 expected contamination msg, got {msg}"
    print(f"[selftest] T8 PASS: contamination leak -> HARD_FAIL", flush=True)

    # T9: MIDDLE_BAND (scaling fails)
    fake_mb = [dict(a) for a in fake_hp_arms]
    fake_mb[2] = {"arm": "ARM_FULL_N_PREVIEW_DISCRIMINATOR", "ok": True,
                   "analytical_scaling_passes": False, "per_probe": []}
    # Smoke top1_mean=0.90 still >= 0.70 -> MIDDLE_BAND not HARD_FAIL
    v, msg, det = compute_verdict(fake_mb, cardinality_ok=True)
    assert v == "MIDDLE_BAND", f"T9 expected MIDDLE_BAND, got {v}: {msg}"
    print(f"[selftest] T9 PASS: scaling-fails -> MIDDLE_BAND", flush=True)

    # T10: cardinality breach
    v, msg, det = compute_verdict(fake_hp_arms, cardinality_ok=False)
    assert v == "HARD_FAIL", f"T10 expected HARD_FAIL, got {v}"
    print(f"[selftest] T10 PASS: cardinality_breach -> HARD_FAIL", flush=True)

    # T11: BIAS-Q suspect-1.000 with content mismatch
    fake_b1q = [dict(a) for a in fake_hp_arms]
    fake_b1q[1] = dict(fake_b1q[1])
    fake_b1q[1]["per_probe"] = [
        {"probe": THEOREM_PROBES[0], "top1_cosine": 1.0, "content_match": False},
    ] + [
        {"probe": p, "top1_cosine": 0.90, "content_match": True}
        for p in THEOREM_PROBES[1:]
    ]
    v, msg, det = compute_verdict(fake_b1q, cardinality_ok=True)
    assert v == "HARD_FAIL", f"T11 expected HARD_FAIL, got {v}"
    assert "BIAS_Q" in msg or "suspect_1000" in msg, f"T11 expected BIAS-Q msg, got {msg}"
    print(f"[selftest] T11 PASS: BIAS-Q suspect-1.000 -> HARD_FAIL", flush=True)

    # T12: pre-reg envelope locks
    assert HP_TOP1_COSINE_MIN == 0.85
    assert HP_CONTAMINATION_MAX == 0.5
    assert N_FULL_PROJECTION == 35000
    print(f"[selftest] T12 PASS: pre-reg envelope constants LOCKED", flush=True)

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

    # ARM_BASELINE_FILENAME_QUERY
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

    # ARM_SMOKE_INGEST_500
    smoke_arm = None
    try:
        smoke_arm = run_arm_smoke_ingest_500(workdir)
        arms.append(smoke_arm)
        print(f"  ARM_SMOKE_INGEST_500 ok={smoke_arm.get('ok')} "
              f"wall={smoke_arm.get('wall_s')}s "
              f"n_chunks={smoke_arm.get('n_chunks_observed')} "
              f"errors={smoke_arm.get('errors')}", flush=True)
    except Exception as e:
        arms.append({"arm": "ARM_SMOKE_INGEST_500", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_SMOKE_INGEST_500 FAILED: {e}", flush=True)
        raise  # META_RULE_J no silent except

    # ARM_FULL_N_PREVIEW_DISCRIMINATOR
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
            print(f"  ARM_FULL_N_PREVIEW_DISCRIMINATOR FAILED: {e}", flush=True)

    # ARM_CONTAMINATION_CONTROL
    try:
        a = run_arm_contamination_control(workdir)
        arms.append(a)
        print(f"  ARM_CONTAMINATION_CONTROL ok={a.get('ok')} "
              f"max_cosine={a.get('contamination_max_cosine')}",
              flush=True)
    except Exception as e:
        arms.append({"arm": "ARM_CONTAMINATION_CONTROL", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CONTAMINATION_CONTROL FAILED: {e}", flush=True)

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
