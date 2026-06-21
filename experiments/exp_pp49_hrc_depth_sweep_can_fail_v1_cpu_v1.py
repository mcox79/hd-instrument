"""D1 saturation-suspect CAN-FAIL re-run: pp49_hrc counterfactual-abduction DEPTH SWEEP (CPU port).

The original `pp49_hrc_counterfactual_depth_8_v1_n4096` HARD_PASSed at a SINGLE depth=8 -> D1 saturation-suspect (a single
depth data-point may be a lucky/saturated PASS, not a genuine envelope with a measured cliff). This re-run SWEEPS depth in
{6, 8 (control), 10, 12} with 3 seeds to (a) CONFIRM the depth=8 PASS re-tests, and (b) LOCATE the can-fail (deeper chains
accumulate more per-hop retrieval error -> the 4 HPs break = cliff onset).

CPU port (pre-reg name _cpu_v1): the original is GPU/torch but the mechanism (N=4096 Hopfield heteroassoc chain + counterfactual
substitution + 4 HP certs) is CPU-tractable. Reuses the mechanism VERBATIM in numpy: bsc bipolar codes, H=sum outer(c[d+1],c[d])/n
+ bg, deletion_cert=-(|xi|^2)^2/n^2, counterfactual H_cf swap at midpoint, HP1 cert~-1 / HP2 cf-retrieval cos>=0.95 / HP3 audit
cert~0 / HP4 downstream cos>=0.70. Same N=4096, same thresholds.

Pre-reg (Research 2026-06-21) + Skunkworks BUILD-GO, 3-way verdict (consistent with the RATIFIED planted_csp symmetric refinement):
  depth=8 PASS re-confirmed AND cliff LOCATED at depth <= 12  -> HARD_PASS (genuine envelope; saturation false alarm; original stands).
  depth=8 FAILS on re-test                                    -> HARD_FAIL (original was a lucky single-point -> honest demote to MM/RESEARCH_FINDING).
  depth=8 holds but NO cliff through depth=12                 -> MIDDLE_BAND (genuine but envelope wider than swept range -> LOWER-BOUND, a3f473dd precedent; Skunkworks rules KEEP-wide vs MM).
  3 seeds; cv <= 0.05. Scope-guard: same mechanism + same N=4096; CPU. ASCII; per-seed ckpt.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "pp49_hrc_depth_sweep_can_fail_v1_cpu_v1"
SOURCE_CELL = "pp49_hrc_counterfactual_depth_8_v1_n4096"
N = 4096; CERT_TOL = 1e-4                                            # VERBATIM original (N + cert tolerance)
HP_CERT = 0.85; HP_CF_COS = 0.95; HP_AUDIT = 0.85; HP_DOWNSTREAM = 0.70; HF_CF_COS = 0.40   # VERBATIM original thresholds
CONTROL_DEPTH = 8                                                    # the original's PASS depth (must re-confirm)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [7, 17]; DEPTHS = [8, 12]; N_ACTIVE = 512; N_CHAINS = 3; M_BG = 20
else:
    SEEDS = [7, 17, 23]; DEPTHS = [6, 8, 10, 12]; N_ACTIVE = N; N_CHAINS = 10; M_BG = 100   # 3 seeds (pre-reg), full N=4096


def deletion_cert(xi, n):                                            # VERBATIM original: bipolar xi -> -(n^2)/n^2 = -1.0
    norm_sq = float(xi.dot(xi)); return -(norm_sq ** 2) / (n * n)


def cosine(a, b):                                                    # VERBATIM original
    na = float(np.linalg.norm(a)); nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(a.dot(b)) / (na * nb)


def run_depth(depth, seed, n_dim, g):
    subst = depth // 2                                               # midpoint substitution (depth=8 -> 4, matching original)
    def bsc():
        return (g.integers(0, 2, n_dim).astype(np.float32) * 2 - 1)
    res = []
    for _ in range(N_CHAINS):
        chain = [bsc() for _ in range(depth + 1)]
        bg_keys = np.stack([bsc() for _ in range(M_BG)]); bg_vals = np.stack([bsc() for _ in range(M_BG)])
        H = np.zeros((n_dim, n_dim), np.float32)
        for d in range(depth):
            H += np.outer(chain[d + 1], chain[d]) / n_dim
        H += (bg_vals.T @ bg_keys) / n_dim
        hp1_ok = abs(deletion_cert(chain[subst], n_dim) + 1.0) < CERT_TOL          # HP1 deletion cert ~ -1
        xi_A = chain[subst]; xi_B = bsc()
        H_cf = H - np.outer(xi_A, chain[subst - 1]) / n_dim + np.outer(xi_B, chain[subst - 1]) / n_dim
        r = chain[0].copy()                                                         # HP2 counterfactual retrieval c0 -> subst hops
        for _ in range(subst):
            r = np.sign(H_cf @ r); r[r == 0] = 1.0
        cf_cos = cosine(r, xi_B)
        h_cf_xi_A = H_cf @ xi_A                                                     # HP3 audit cert for xi_A in H_cf ~ 0
        cert_A_cf = float(h_cf_xi_A.dot(xi_A)) / (n_dim * float(xi_A.dot(xi_A))); hp3_ok = abs(cert_A_cf) < 0.15
        r_ds = chain[subst + 1].copy()                                             # HP4 downstream: subst+1 -> +2 hops -> target subst+3
        for _ in range(2):
            r_ds = np.sign(H_cf @ r_ds); r_ds[r_ds == 0] = 1.0
        ds_cos = cosine(r_ds, chain[subst + 3])
        res.append((hp1_ok, cf_cos, hp3_ok, ds_cos))
    hp1r = float(np.mean([r[0] for r in res])); cf = float(np.mean([r[1] for r in res]))
    hp3r = float(np.mean([r[2] for r in res])); ds = float(np.mean([r[3] for r in res]))
    n_hp = int((hp1r >= HP_CERT) + (cf >= HP_CF_COS) + (hp3r >= HP_AUDIT) + (ds >= HP_DOWNSTREAM))
    passed = (hp1r >= HP_CERT and cf >= HP_CF_COS and hp3r >= HP_AUDIT and ds >= HP_DOWNSTREAM)
    return {"depth": depth, "hp1_cert_rate": round(hp1r, 4), "cf_cos": round(cf, 4), "hp3_audit_rate": round(hp3r, 4),
            "ds_cos": round(ds, 4), "n_hp": n_hp, "passed_4hp": bool(passed)}


def run_unit(seed):
    g = np.random.default_rng(seed)
    by_depth = {("d%d" % dp): run_depth(dp, seed, N_ACTIVE if RUN_MODE == "smoke" else N, g) for dp in DEPTHS}
    print("  [seed=%d] %s" % (seed, {k: (v["n_hp"], "PASS" if v["passed_4hp"] else "fail", "cf=%.2f" % v["cf_cos"]) for k, v in by_depth.items()}), flush=True)
    return {"seed": seed, "by_depth": by_depth}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    agg = {}
    for dp in DEPTHS:
        dk = "d%d" % dp
        cfs = [u["by_depth"][dk]["cf_cos"] for u in units]; dss = [u["by_depth"][dk]["ds_cos"] for u in units]
        pass_rate = float(np.mean([u["by_depth"][dk]["passed_4hp"] for u in units]))
        agg[dk] = {"depth": dp, "cf_cos_mean": round(float(np.mean(cfs)), 4), "ds_cos_mean": round(float(np.mean(dss)), 4),
                   "pass_rate": pass_rate, "cf_cv": round(float(np.std(cfs) / (abs(np.mean(cfs)) + 1e-9)), 4),
                   "all_pass": pass_rate >= 0.99}
    ctrl = agg["d%d" % CONTROL_DEPTH]
    # can-fail = shallowest depth (>control) where the 4-HP no longer all-pass (cliff onset)
    deeper = [dp for dp in DEPTHS if dp > CONTROL_DEPTH]
    canfail = next((dp for dp in deeper if not agg["d%d" % dp]["all_pass"]), None)
    worst_cv = max(v["cf_cv"] for v in agg.values())
    detail = {"by_depth": agg, "control_depth": CONTROL_DEPTH, "control_all_pass": ctrl["all_pass"], "canfail_depth": canfail,
              "worst_cv": worst_cv, "source_cell": SOURCE_CELL, "cites": [SOURCE_CELL, "pp48_nkt_depth_cliff_cluster"]}
    summ = "control(d=%d)all_pass=%s pass_rates=%s cf_cos=%s worst_cv=%.3f" % (
        CONTROL_DEPTH, ctrl["all_pass"], {k: v["pass_rate"] for k, v in agg.items()}, {k: v["cf_cos_mean"] for k, v in agg.items()}, worst_cv)
    if worst_cv > 0.05 and len(units) >= 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: seed-unstable (cv>0.05). " + summ, detail)
    if not ctrl["all_pass"]:
        return ("HARD_FAIL", "HARD_FAIL: depth=%d (the original's PASS depth) does NOT re-confirm all-4-HP on 3-seed re-test -> the original was a lucky single-point -> honest DEMOTE to MM/RESEARCH_FINDING. " % CONTROL_DEPTH + summ, detail)
    if canfail is not None:
        return ("HARD_PASS", "HARD_PASS: depth=%d PASS RE-CONFIRMED (3-seed) AND can-fail LOCATED at depth=%d (deeper chains break the 4-HP as per-hop error accumulates) -> genuine depth envelope with a measured cliff -> original NOT single-point-saturated -> saturation FALSE ALARM, original CHAIN-GRADE stands. " % (CONTROL_DEPTH, canfail) + summ, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: depth=%d PASS re-confirmed but NO cliff located through depth=%d (all swept depths all-pass) -> genuine but the envelope exceeds the swept range = LOWER-BOUND (a3f473dd precedent); Skunkworks rules KEEP-with-wide-envelope vs reframe-MM. " % (CONTROL_DEPTH, max(DEPTHS)) + summ, detail)


def _selftest():
    g = np.random.default_rng(0); n = 256
    xi = (g.integers(0, 2, n).astype(np.float32) * 2 - 1)
    assert abs(deletion_cert(xi, n) + 1.0) < 1e-6, "deletion_cert bipolar = -1.0 (VERBATIM original selftest)"
    a = np.array([1.0, 0, 0, 0], np.float32); b = np.array([0, 1.0, 0, 0], np.float32)
    assert abs(cosine(a, b)) < 1e-9 and abs(cosine(a, a) - 1.0) < 1e-9, "cosine orth=0 self=1"
    # depth-monotonicity sanity (the can-fail mechanism): a shallow chain retrieves the counterfactual better than a deep one.
    # (min valid depth = 6: HP4 needs subst+3 <= depth, subst=depth//2.)
    g2 = np.random.default_rng(1); cf_shallow = run_depth(6, 1, 512, g2)["cf_cos"]
    g3 = np.random.default_rng(1); cf_deep = run_depth(16, 1, 512, g3)["cf_cos"]
    assert cf_shallow >= cf_deep - 1e-6, "can-fail mechanism: deeper chain retrieval <= shallow (shallow=%.2f deep=%.2f)" % (cf_shallow, cf_deep)
    print("[selftest] PASS: VERBATIM cert/cosine + depth-monotonic can-fail mechanism (cf d6=%.2f >= d16=%.2f)" % (cf_shallow, cf_deep), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] %s mode=%s N=%d seeds=%s depths=%s n_chains=%d (CPU port of %s)" % (ANCHOR_NAME, RUN_MODE, N_ACTIVE if RUN_MODE == "smoke" else N, SEEDS, DEPTHS, N_CHAINS, SOURCE_CELL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE, "schema": "depth-sweep-canfail-cpu", "depths": str(DEPTHS), "n_chains": N_CHAINS}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    write_partial_key(out_dir, key, run_unit(seed))
units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "n_seeds": len(SEEDS),
           "detail": detail, "metrics_source": "measured_cpu_pp49_hrc_depth_sweep_canfail_port", "per_seed": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
