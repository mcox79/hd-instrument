"""NEW-4 random-control can-fail re-run -- SIBLING of exp_substrate_per_cluster_stratified_extraction_v1 + a matched-budget
RANDOM-control arm (the discriminator Skunkworks's landed-VET held NEW-4 for: the original coverage=1.0-everywhere is
by-construction-saturated -- stratified keeps >=1 token per cluster so coverage is trivially ~1.0; only a random control at
the SAME budget shows whether that is stratification-VALUE or by-construction).

Arm 1 (stratified, baseline) = the sibling's per-cluster top-norm extraction, VERBATIM (true sibling, not a redesign).
Arm 2 (random-control, discriminator) = sample the SAME TOTAL n_extract as Arm 1 yields-in-total (sum across ALL clusters),
   uniformly random across-all-clusters (NOT per-cluster) -- Skunkworks matched-budget clarification (fair on total-extract;
   per-cluster random would be disadvantaged by construction).
Discrimination = Arm1.coverage - Arm2.coverage per sp. Uses the already-shipped Llama-1B residual npz (no model load). CPU.

PRE-REG bands (Research 2026-06-21): Arm1 coverage >= 0.95; Arm2 coverage <= 0.50 at sp1000; discrimination > 0.40 at sp1000;
   3 seeds cv per arm <= 0.05; symmetric guard. HARD_FAIL if Arm1 < 0.95 OR Arm2 > 0.80 at sp1000 (random competitive ->
   stratified value vanishes -> Skunkworks reclassifies stratified as MM). ASCII; no em-dashes. write_metrics; per-seed ckpt.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_per_cluster_stratified_extraction_with_random_control_v1"
# REFERENT (Exp-Dev 2026-06-21, git-CONVERGED): the sibling's hardcoded exp_phase05 npz was CLOBBERED by an anomalous Instruct-509
# SMOKE run; the cert's CANONICAL output is the POOL data/llama_1b_results/residuals_per_token.npz (106427x2048). git-definitive
# (Orchestrator, commit e5c4ddec): the extractor MODEL_ID = meta-llama/Llama-3.2-1B (BASE) since inception, NEVER changed -> the
# cert was ALWAYS base; the POOL IS that base canonical (the "106k" in the HARD_PASS commit). So pointing here IS apples-to-apples
# with the original stratified cert (same base model, 40k sampled from the 106k canonical pool). No re-extract needed; repoint is the fix.
# (Earlier "POOL=Instruct-different-model" was Orchestrator's mis-read of the clobber artifact, retracted via git.) HDLAB_NEW4_NPZ overrides.
_NPZ_POOL = REPO / "data" / "llama_1b_results" / "residuals_per_token.npz"          # CANONICAL base extraction (git-proven), 106427x2048
_NPZ_SIBLING = REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"   # clobbered to a 509 smoke -- NOT canonical
NPZ = Path(os.environ["HDLAB_NEW4_NPZ"]) if os.environ.get("HDLAB_NEW4_NPZ") else (_NPZ_POOL if _NPZ_POOL.exists() else _NPZ_SIBLING)
SPEEDUPS = [10, 100, 1000]
SOURCE_SIBLING = "substrate_per_cluster_stratified_extraction_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":                                            # MATCH the sibling's smoke/full configs exactly (true sibling)
    SEEDS = [1]; N_TOK = 5000; VC_GRID = [64, 256]
else:
    SEEDS = [7, 17, 23]; N_TOK = 40000; VC_GRID = [256, 1024, 4096]


def coverage(codes, keep_mask, vc):                               # VERBATIM sibling: fraction of used VQ codes still represented in the kept subset
    used = set(np.unique(codes).tolist())
    kept = set(np.unique(codes[keep_mask]).tolist())
    return len(kept) / max(len(used), 1)


def _selftest():
    norms = np.array([0.1, 0.9, 0.5, 0.8, 0.2], np.float32)
    thr = np.quantile(norms, 1 - 0.4); mask = norms >= thr
    assert mask.sum() == 2 and mask[1] and mask[3], "norm gate selects top-g"
    codes = np.array([0, 1, 2, 0, 1]); assert abs(coverage(codes, np.array([True, True, False, False, False]), 3) - 2 / 3) < 1e-6, "coverage computation"
    # random-control discriminator sanity: stratified (>=1 per cluster) covers ALL codes; a random same-budget sample misses some
    cg = np.random.default_rng(0); cd = cg.integers(0, 50, 2000)   # 50 clusters, 2000 tokens
    nrm = cg.random(2000); strat = np.zeros(2000, bool)
    for c in range(50):
        ci = np.where(cd == c)[0]
        if len(ci): strat[ci[np.argsort(-nrm[ci])[:1]]] = True     # top-1 per cluster
    tb = int(strat.sum()); rnd = np.zeros(2000, bool); rnd[cg.choice(2000, tb, replace=False)] = True
    cov_s = coverage(cd, strat, 50); cov_r = coverage(cd, rnd, 50)
    assert cov_s == 1.0 and cov_r < cov_s, "random-control discriminates (strat=%.3f > random=%.3f at matched budget)" % (cov_s, cov_r)
    print("[selftest] PASS: gate + coverage + random-control discriminates (strat=1.0 > random=%.3f @matched-budget)" % cov_r, flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not NPZ.exists():
    print("[FATAL] Llama-1B residual npz not found at %s" % NPZ, flush=True); sys.exit(1)
try:
    from sklearn.cluster import MiniBatchKMeans
except Exception as e:
    print("[FATAL] sklearn missing: %s" % e, flush=True); sys.exit(1)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    d = np.load(NPZ); R = d["residuals"]
    idx = g.choice(R.shape[0], size=min(N_TOK, R.shape[0]), replace=False)
    X = R[idx].astype(np.float32); norms = np.linalg.norm(X, axis=1)
    Xn = X / (norms[:, None] + 1e-8)
    vc = max(VC_GRID); k = min(vc, X.shape[0] // 4)
    codes = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=3, batch_size=512).fit(Xn).labels_
    rg = np.random.default_rng(seed * 101 + 7)                    # independent rng for the random-control arm (reproducible)
    res = {"seed": seed, "n_tok": len(idx), "by_speedup": {}}
    for sp in SPEEDUPS:
        budget = max(k, len(idx) // sp)                           # VERBATIM sibling: stratified keep ~budget tokens across clusters
        per = max(1, budget // k); keep = np.zeros(len(idx), bool)
        for c in range(k):
            ci = np.where(codes == c)[0]
            if len(ci):
                top = ci[np.argsort(-norms[ci])[:per]]; keep[top] = True   # Arm 1: top-norm WITHIN cluster (stratified)
        total_budget = int(keep.sum())                           # Arm 2 matched-budget = Arm 1's TOTAL kept (sum across clusters)
        rkeep = np.zeros(len(idx), bool); rkeep[rg.choice(len(idx), total_budget, replace=False)] = True   # uniform across-all-clusters
        c1 = coverage(codes, keep, vc); c2 = coverage(codes, rkeep, vc)
        res["by_speedup"]["sp%d" % sp] = {
            "arm1_stratified_coverage": c1, "arm1_actual_speedup": len(idx) / max(keep.sum(), 1),
            "arm2_random_coverage": c2, "arm2_actual_speedup": len(idx) / max(rkeep.sum(), 1),
            "discrimination": c1 - c2, "total_budget": total_budget}
    res["min_arm1_coverage"] = float(min(v["arm1_stratified_coverage"] for v in res["by_speedup"].values()))
    return res


def _agg(ps, sp, field):
    return float(np.mean([p["by_speedup"]["sp%d" % sp][field] for p in ps]))


def _cv(ps, sp, field):
    xs = [p["by_speedup"]["sp%d" % sp][field] for p in ps]
    return float(np.std(xs) / (abs(np.mean(xs)) + 1e-9))


def verdict(ps) -> Tuple[str, str, Dict]:
    if not ps:
        return ("HARD_FAIL", "no results", {})
    a1_min = float(min(_agg(ps, sp, "arm1_stratified_coverage") for sp in SPEEDUPS))
    a2_1000 = _agg(ps, 1000, "arm2_random_coverage"); a1_1000 = _agg(ps, 1000, "arm1_stratified_coverage")
    discrim_1000 = _agg(ps, 1000, "discrimination")
    worst_cv = max(max(_cv(ps, sp, "arm1_stratified_coverage"), _cv(ps, sp, "arm2_random_coverage")) for sp in SPEEDUPS)
    detail = {"by_sp": {("sp%d" % sp): {"arm1_cov": round(_agg(ps, sp, "arm1_stratified_coverage"), 4),
                                        "arm2_cov": round(_agg(ps, sp, "arm2_random_coverage"), 4),
                                        "arm1_speedup": round(_agg(ps, sp, "arm1_actual_speedup"), 1),
                                        "arm2_speedup": round(_agg(ps, sp, "arm2_actual_speedup"), 1),
                                        "discrimination": round(_agg(ps, sp, "discrimination"), 4)} for sp in SPEEDUPS},
              "arm1_min_coverage": round(a1_min, 4), "arm2_coverage_sp1000": round(a2_1000, 4),
              "discrimination_sp1000": round(discrim_1000, 4), "worst_cv": round(worst_cv, 4),
              "source_sibling": SOURCE_SIBLING, "pre_reg": "arm1>=0.95 & arm2<=0.50@sp1000 & discrim>0.40@sp1000 & cv<=0.05"}
    summary = "arm1_min_cov=%.3f arm2_cov@sp1000=%.3f discrim@sp1000=%.3f worst_cv=%.3f | %s" % (
        a1_min, a2_1000, discrim_1000, worst_cv, {k: (v["arm1_cov"], v["arm2_cov"]) for k, v in detail["by_sp"].items()})
    if a1_min < 0.95:
        return ("HARD_FAIL", "HARD_FAIL: stratified arm1 coverage < 0.95 (loses its own PASS regime). " + summary, detail)
    if a2_1000 > 0.80:
        return ("HARD_FAIL", "HARD_FAIL: random control competitive (arm2 coverage > 0.80 at sp1000) -> stratified adds no value over random-at-budget -> reclassify stratified MM. " + summary, detail)
    if worst_cv > 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: seed-unstable (cv > 0.05). " + summary, detail)
    if a2_1000 <= 0.50 and discrim_1000 > 0.40:
        return ("HARD_PASS", "HARD_PASS (can-fail-witnessed): random control FAILS (arm2 <= 0.50 at sp1000) while stratified holds; discrimination > 0.40 -> stratification has genuine value over random-at-budget. CHAIN-GRADE-CANDIDATE -> Skunkworks. " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: arm1 holds but random control partly competitive (arm2 in 0.50-0.80 OR discrim <= 0.40 at sp1000) -> stratified value is partial/honest-bounded -> Skunkworks reclassify MM-strong. " + summary, detail)


print("[config] anchor=%s mode=%s seeds=%s N_tok=%d vc=%s (sibling=%s)" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_TOK, VC_GRID, SOURCE_SIBLING), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    r = run_seed(seed)
    print("  [seed=%d] %s" % (seed, {k: ("a1=%.3f" % v["arm1_stratified_coverage"], "a2=%.3f" % v["arm2_random_coverage"], "d=%.3f" % v["discrimination"]) for k, v in r["by_speedup"].items()}), flush=True)
    write_partial_key(out_dir, key, r)
ps = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
v, vmsg, detail = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
           "detail": detail, "metrics_source": "measured_cpu_stratified_vs_random_control_matched_budget", "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
