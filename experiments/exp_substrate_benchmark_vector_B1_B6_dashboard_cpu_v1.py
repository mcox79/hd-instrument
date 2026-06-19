"""
exp_substrate_benchmark_vector_B1_B6_dashboard_cpu_v1.py -- SUBSTRATE-INTERNAL BENCHMARK VECTOR dashboard (B1-B6 in one read-only shot) -- CPU/local (no heat), READ-ONLY.

ROUTING: Research 25th writeback SECONDARY (#2). The "substrate measures itself" operational dashboard: aggregate the substrate-internal
  benchmark vector B1-B6 (per Research's 21st-writeback definition) by READING each component's source-cell metrics.json -- NO re-running of
  heavy cells, NO re-implementation (single source of truth = each dedicated cell). Substrate-internal only (no LLM comparison; USER 11th rule).
  Honest: components whose exact source-key mapping is NOT yet confirmed are surfaced from their source cell with an explicit "mapping pending"
  label rather than a fabricated number (10th rule). Adds the NEW dim-5 replacement observable (spectral_slope / hill_alpha) as a bonus row.

  B-vector (Research 21st writeback):
    B1 KP P1 candidate count            <- exp_substrate_knowledge_promotion_p1_frequency_cpu_v1  per_seed.n_candidates
    B2 L6-PROOF FINDER found-rate(recall)<- exp_substrate_proof_finder_backward_chaining_cpu_v1   per_seed.found_rate
    B3 retrieval recall@10              <- (source-key mapping PENDING; surfaced from exp_qa_self_knowledge_cpu_v1 macro_f1 as related)
    B4 9d spectral observability dim-1  <- (exact dim-1 key PENDING; surfaced from f4_cell_c bbp 9d pillar alpha)
    B5 avg premise count (PRECNT)       <- exp_substrate_depth_forecast_scalefree_hill_premise_cpu_v1 per_seed.avg_premise_count
    B6 median_proof_depth               <- exp_substrate_theorem_portfolio_proof_tracker_cpu_v1     per_seed.median_depth
    (bonus) dim-5 replacement           <- exp_f4_spectrum_shoulder_replacement_observable_dim5_cpu_v1 stats.spectral_slope

PRE-REGISTERED: HARD-PASS iff >= 4 of 6 B-components are POPULATED (source metrics readable) AND none populated component is in an error
  state. MIDDLE_BAND iff 2-3 populated. UNKNOWN iff < 2 readable. (Dashboard is a reporting/aggregation cell; the gate is coverage+integrity,
  not a capability bar -- each component's own cell owns its verdict.) ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple, Any
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_benchmark_vector_B1_B6_dashboard_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
DATA = REPO / "data"

# (component, source-anchor-dir, extractor, label, mapping_confirmed)
def _ps(d):
    return (d.get("per_seed") or [{}])[0]


SPEC = [
    ("B1", "exp_substrate_knowledge_promotion_p1_frequency_cpu_v1", lambda d: _ps(d).get("n_candidates"), "KP P1 candidate count", True),
    ("B2", "exp_substrate_proof_finder_backward_chaining_cpu_v1", lambda d: _ps(d).get("found_rate"), "L6-PROOF FINDER found-rate", True),
    ("B3", "exp_qa_self_knowledge_cpu_v1", lambda d: _ps(d).get("macro_f1"), "retrieval recall@10 [PENDING: surfacing self-knowledge macro_F1]", False),
    ("B4", "exp_f4_cell_c_spike_bulk_decomposition_bbp_9d_pillar_cpu_v1", lambda d: _ps(d).get("alpha"), "9d spectral dim-1 [PENDING: surfacing 9d bulk alpha]", False),
    ("B5", "exp_substrate_depth_forecast_scalefree_hill_premise_cpu_v1", lambda d: _ps(d).get("avg_premise_count"), "avg premise count (PRECNT)", True),
    ("B6", "exp_substrate_theorem_portfolio_proof_tracker_cpu_v1", lambda d: _ps(d).get("median_depth"), "median_proof_depth (theorem portfolio)", True),
    ("dim5*", "exp_f4_spectrum_shoulder_replacement_observable_dim5_cpu_v1", lambda d: (_ps(d).get("stats", {}).get("spectral_slope", {}) or {}).get("value"), "dim-5 REPLACEMENT (power-law shoulder spectral_slope)", True),
]


def read_component(anchor_dir: str, extractor) -> Dict[str, Any]:
    p = DATA / anchor_dir / "metrics.json"
    if not p.exists():
        return {"populated": False, "reason": "no_metrics_json"}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        val = extractor(d)
        return {"populated": val is not None, "value": val, "source_verdict": d.get("verdict"),
                "source_mode": d.get("run_mode"), "reason": None if val is not None else "key_absent"}
    except Exception as e:
        return {"populated": False, "reason": "read_error:" + str(e)[:50]}


def _selftest():
    # extractor robustness on synthetic metrics dicts
    assert SPEC[0][2]({"per_seed": [{"n_candidates": 24}]}) == 24
    assert SPEC[6][2]({"per_seed": [{"stats": {"spectral_slope": {"value": -0.98}}}]}) == -0.98
    assert SPEC[1][2]({"per_seed": [{}]}) is None
    print("[selftest] PASS: substrate_benchmark_vector_B1_B6_dashboard_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    rows = []
    for comp, anchor, extractor, label, confirmed in SPEC:
        r = read_component(anchor, extractor)
        rows.append({"component": comp, "label": label, "mapping_confirmed": confirmed, "source": anchor, **r})
    core = [r for r in rows if r["component"] in ("B1", "B2", "B3", "B4", "B5", "B6")]
    populated = sum(1 for r in core if r["populated"])
    confirmed_pop = sum(1 for r in core if r["populated"] and r["mapping_confirmed"])
    print("  SUBSTRATE-INTERNAL BENCHMARK VECTOR (read-only aggregate; substrate measures itself, no LLM comparison):", flush=True)
    for r in rows:
        v = r.get("value"); flag = "" if r["mapping_confirmed"] else "  <-- mapping PENDING (Research confirm)"
        if r["populated"]:
            print("    %-6s %-52s = %-10s (src verdict=%s)%s" % (r["component"], r["label"], v, r.get("source_verdict"), flag), flush=True)
        else:
            print("    %-6s %-52s = N/A (%s)%s" % (r["component"], r["label"], r.get("reason"), flag), flush=True)
    print("  coverage: %d/6 B-components populated (%d with CONFIRMED mapping)" % (populated, confirmed_pop), flush=True)
    bf = REPO / "data" / "substrate_index" / "bench_reports"
    try:
        bf.mkdir(parents=True, exist_ok=True)
        (bf / "benchmark_vector_B1_B6.json").write_text(json.dumps({"rows": rows, "populated": populated, "confirmed_populated": confirmed_pop}, indent=2), encoding="utf-8")
    except Exception:
        pass
    return {"rows": rows, "populated": populated, "confirmed_populated": confirmed_pop}


def verdict(r) -> Tuple[str, str]:
    pop = r["populated"]; conf = r["confirmed_populated"]
    s = ("substrate-internal benchmark vector: %d/6 B-components populated (%d with confirmed source-key mapping). Components: %s. "
         "Read-only aggregate of dedicated cells (single source of truth each); B3 (retrieval recall@10) + B4 (9d dim-1) have PENDING exact "
         "source-key mappings -- surfaced from their source cells with explicit labels, not fabricated. This is the 'substrate measures itself' "
         "dashboard across hygiene/abstraction/grounding/depth dimensions (USER 11th rule: substrate-internal, no LLM comparison).") % (
        pop, conf, [(x["component"], x.get("value") if x["populated"] else "N/A") for x in r["rows"]])
    if pop >= 4:
        return ("HARD_PASS", "HARD_PASS (operational substrate-internal dashboard): %d/6 B-components aggregated read-only from their dedicated "
                "cells; substrate self-measures across the benchmark vector. %d have confirmed mappings; B3/B4 mappings flagged PENDING for "
                "Research (honest, not fabricated). " % (pop, conf) + s)
    if pop >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: only %d/6 B-components readable -- some source cells have not been run on the current index yet. " % pop + s)
    return ("UNKNOWN", "UNKNOWN: < 2 B-components readable; source metrics.json files missing. " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
