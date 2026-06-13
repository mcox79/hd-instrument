"""
exp_partition_stratified_smoke_gap_cpu_v1.py -- validate partition-stratified smoke closes the smoke-to-full P@30 gap -- CPU/local.

ROUTING: Research hand-off (exp_dev_handoff_research_smoke_to_full_corpus_degradation_partition_stratified_smoke). 3 self-extension
  iterations showed -0.17 to -0.44 smoke-to-full P@30 degradation; diagnosed as PARTITION-COMPOSITION MISMATCH (research_drill
  smoke is one homogeneous content-rich stratum; full corpus mixes 6 partitions, several jargon-heavy). Anchor 1: a 30-file
  partition-STRATIFIED smoke (5 per partition x 6, fixed seed) should predict full-corpus P@30 within +/-0.05. This cell measures
  the gap. MEASUREMENT-ONLY: runs the Phase-2-light pipeline (returns PROPOSALS; writes NO canonical atoms) on the stratified
  smoke and on the full corpus, computes a JARGON-PATTERN P@30 PROXY (true P@30 needs Research ACCEPT/REJECT review; the proxy
  scores a top-30 proposal as bona-fide iff its canonical_name is NOT substrate-meta-jargon -- the degradation cause). Reports
  proxy gap + per-partition proxy P@30 (disaggregated). NO LLM; Phase-2-light is numpy-only.

  HONEST: this reports the PROXY gap (auto-computable) AND saves both top-30 batches for Research to score the TRUE P@30 gap.
  The proxy is a directional stand-in for the meta-jargon mis-extraction that drives the degradation, not a substitute for review.

PRE-REGISTERED (research bands, on the PROXY): HARD-PASS |proxy gap| <= 0.05 (stratified smoke predicts full within 5pct).
  HARD-FAIL |proxy gap| > 0.15. MIDDLE [0.05, 0.15] (stratification helps; per-partition filters also needed). UNKNOWN if store/files absent.
ASCII-only. CPU/local (numpy-only; runs on laptop). --self-test + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "partition_stratified_smoke_gap_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SEED = 1028
NOTES = REPO / "notes"

# 6 partition strata defined by filename convention (the substrate's routing-note ecosystem)
PARTITIONS = {
    "research_drill": ["research_drill_*.md"],
    "research_history": ["research_to_*.md", "research_routing_*.md", "research_decisions_*.md"],
    "results_history": ["exp_dev_to_*.md", "exp_dev_handoff_*.md"],
    "findings_history": ["testbed_to_*.md"],
    "decision_history": ["strategy_decisions_*.md", "strategy_request_*.md", "visibility_decisions_*.md"],
    "meta_history": ["meta_audit_*.md", "orchestrator_*.md"],
}

# jargon-pattern P@30 PROXY: a top-30 proposal is NOT bona-fide (jargon artifact) if its canonical_name matches meta-jargon.
_JARGON_TOK = {"cycle", "macro", "axis", "verdict", "hard", "pass", "fail", "middle", "band", "route", "atom", "capability",
               "partition", "exp", "dev", "testbed", "research", "drill", "gpu", "cpu", "hrr", "bge", "tier", "phase",
               "anchor", "prereg", "smoke", "queue", "commit", "ship", "cap", "pp", "wave", "rung", "snr", "f1", "p30",
               "substrate", "methodology", "feedback", "scope", "orchestrator", "handoff", "rule", "meta"}


def _is_jargon(canonical_name: str) -> bool:
    cn = canonical_name.lower()
    if re.search(r"\d", cn):                       # cycle numbers, PP-###, versions -> jargon
        return True
    toks = re.split(r"[_\-/:]+", cn)
    if any(t in _JARGON_TOK for t in toks):        # meta tokens
        return True
    if len([t for t in toks if len(t) > 1]) < 2:   # single-token -> not a real multi-word primitive
        return True
    return False


def _proxy_p_at_30(proposals) -> float:
    top = proposals[:30]
    if not top:
        return 0.0
    bona = sum(1 for p in top if not _is_jargon(p.candidate.canonical_name))
    return bona / len(top)


def _selftest():
    assert _is_jargon("cycle_51_macro") and _is_jargon("pp376_math") and _is_jargon("verdict_hard_pass")
    assert not _is_jargon("circular_convolution") and not _is_jargon("marchenko_pastur_distribution")
    assert _is_jargon("singleton")  # single real token
    print("[selftest] PASS: partition_stratified_smoke_gap_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _files_for(globs: List[str]) -> List[Path]:
    seen = set(); out = []
    for g in globs:
        for f in NOTES.glob(g):
            if f.resolve() not in seen:
                seen.add(f.resolve()); out.append(f)
    return out


def run() -> Dict:
    import random
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    from backend.substrate_index.phase_2_light import run_phase_2_light_pipeline
    if not (REPO / "data" / "substrate_index").exists():
        return {"error": "no_substrate_index"}
    pstore = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=1024); ai.build(pstore)
    rng = random.Random(SEED)
    # build partition file lists
    part_files = {p: _files_for(globs) for p, globs in PARTITIONS.items()}
    for p, fs in part_files.items():
        print("  partition %-18s %d files" % (p, len(fs)), flush=True)
    # STRATIFIED smoke: 5 per partition (fixed seed); skip empty partitions
    per = 2 if SMOKE else 5
    strat = []
    strat_by_part = {}
    for p, fs in part_files.items():
        pick = rng.sample(fs, min(per, len(fs))) if fs else []
        strat_by_part[p] = pick; strat.extend(pick)
    print("  stratified smoke: %d files (%d per partition x %d partitions)" % (len(strat), per, len(PARTITIONS)), flush=True)
    # FULL corpus: union of all 6 partitions (cap for runtime if huge)
    full = []
    seen = set()
    for p, fs in part_files.items():
        for f in fs:
            if f.resolve() not in seen:
                seen.add(f.resolve()); full.append(f)
    FULL_CAP = 150 if SMOKE else 1200
    if len(full) > FULL_CAP:
        full = rng.sample(full, FULL_CAP)
        print("  full corpus sampled to %d files (cap for runtime)" % FULL_CAP, flush=True)
    else:
        print("  full corpus: %d files" % len(full), flush=True)
    # HOMOGENEOUS baseline: the OLD smoke (research_drill ONLY, same file count) -- to show stratification HELPS vs this
    homog_pool = part_files["research_drill"]
    homog = rng.sample(homog_pool, min(len(strat), len(homog_pool))) if homog_pool else []
    # run pipeline (MEASUREMENT-ONLY: returns proposals, writes nothing canonical)
    th = time.time()
    prop_homog = run_phase_2_light_pipeline(homog, pstore, ai, top_k=30)
    p_homog = _proxy_p_at_30(prop_homog)
    print("  [homogeneous smoke (research_drill only)] proxy P@30 = %.4f (%d proposals, %.1fs)" % (p_homog, len(prop_homog), time.time() - th), flush=True)
    t0 = time.time()
    prop_strat = run_phase_2_light_pipeline(strat, pstore, ai, top_k=30)
    p_strat = _proxy_p_at_30(prop_strat)
    print("  [stratified smoke] proxy P@30 = %.4f (%d proposals, %.1fs)" % (p_strat, len(prop_strat), time.time() - t0), flush=True)
    t1 = time.time()
    prop_full = run_phase_2_light_pipeline(full, pstore, ai, top_k=30)
    p_full = _proxy_p_at_30(prop_full)
    print("  [full corpus]      proxy P@30 = %.4f (%d proposals, %.1fs)" % (p_full, len(prop_full), time.time() - t1), flush=True)
    gap = abs(p_strat - p_full)
    gap_homog = abs(p_homog - p_full)
    print("  GAPS: homogeneous |homog - full| = %.4f  vs  stratified |strat - full| = %.4f  (stratification helps if strat-gap < homog-gap)" % (gap_homog, gap), flush=True)
    # per-partition proxy P@30 (disaggregated; run pipeline per single-partition stratum of `per` files)
    per_part = {}
    for p, pick in strat_by_part.items():
        if not pick:
            per_part[p] = None; continue
        pr = run_phase_2_light_pipeline(pick, pstore, ai, top_k=30)
        per_part[p] = round(_proxy_p_at_30(pr), 4)
    spread_vals = [v for v in per_part.values() if v is not None]
    spread = round(max(spread_vals) - min(spread_vals), 4) if spread_vals else None
    print("  proxy gap |strat - full| = %.4f | per-partition proxy P@30 = %s | spread = %s" % (gap, per_part, spread), flush=True)
    # save both batches for Research true-P@30 review
    out = {"stratified_top30": [{"rank": i + 1, "name": p.candidate.canonical_name, "route": p.route, "z": p.candidate.z_count,
                                  "proxy_bona": (not _is_jargon(p.candidate.canonical_name))} for i, p in enumerate(prop_strat)],
           "full_top30": [{"rank": i + 1, "name": p.candidate.canonical_name, "route": p.route, "z": p.candidate.z_count,
                            "proxy_bona": (not _is_jargon(p.candidate.canonical_name))} for i, p in enumerate(prop_full)]}
    bf = REPO / "data" / "substrate_index" / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "partition_stratified_smoke_batches.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return {"proxy_p_homog": round(p_homog, 4), "proxy_p_strat": round(p_strat, 4), "proxy_p_full": round(p_full, 4),
            "proxy_gap": round(gap, 4), "proxy_gap_homog": round(gap_homog, 4), "stratification_helps": bool(gap < gap_homog),
            "per_partition_proxy": per_part, "partition_spread": spread, "n_strat": len(strat), "n_homog": len(homog), "n_full": len(full),
            "note": "proxy = fraction of top-30 NOT meta-jargon; true P@30 needs Research review (batches saved)"}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    g = r["proxy_gap"]
    s = "proxy P@30 homog=%.4f strat=%.4f full=%.4f; gap homog=%.4f strat=%.4f (stratification_helps=%s); per-partition=%s spread=%s; n_strat=%d n_full=%d (PROXY: not-meta-jargon; true P@30 batches saved for Research)" % (
        r["proxy_p_homog"], r["proxy_p_strat"], r["proxy_p_full"], r["proxy_gap_homog"], g, r["stratification_helps"],
        r["per_partition_proxy"], r["partition_spread"], r["n_strat"], r["n_full"])
    if g <= 0.05:
        return ("HARD_PASS", "HARD_PASS (proxy): partition-stratified smoke predicts full-corpus P@30 within 5pct -- stratification closes the composition-mismatch gap. Validates the partition-stratified-smoke methodology rule (proxy evidence; Research confirms via true P@30 on the saved batches). " + s)
    if g <= 0.15:
        return ("MIDDLE_BAND", "MIDDLE_BAND (proxy): stratified smoke helps but residual gap [0.05,0.15] -- per-partition scope-aware filters (anchor 2) also needed. " + s)
    return ("HARD_FAIL", "HARD_FAIL (proxy): stratified smoke still mispredicts (gap > 0.15) -- degradation has a deeper root than composition (extractor partition-class-blind even after re-sampling; anchor 3 held-out decoupling). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
