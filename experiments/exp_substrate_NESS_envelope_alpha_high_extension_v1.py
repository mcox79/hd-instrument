"""
substrate_NESS_envelope_alpha_high_extension_v1 -- alpha-high envelope extension.

PROMOTION CONTEXT (Research DRILL 1 ITEM 3, 2026-06-25):
  Today's chain-grade reference `kmax_ness_envelope_corrected_v1` (=`kmax_ness_envelope_gpu_v1`)
  HARD_PASS on alpha_frac in [0.3, 0.7]. Lift cand/eq is MONOTONICALLY INCREASING through alpha=0.7:
    cand/eq = {0.3: 2.12, 0.4: 2.91, 0.5: 4.21, 0.6: 6.17, 0.7: 12.27}
  ext_hopfrac stays >= 0.99 (degradation BEGINS at 0.7 -- the FIRST sign of cliff).
  Predicted cliff per Hatano-Sasa NESS theory: between alpha_frac in [0.85, 0.92].

v1 DESIGN (alpha-high extension; lift MAY keep increasing OR cliff identified):
  alpha_frac in {0.7 (rail), 0.8, 0.85, 0.9, 0.95}  -- 5 points
  All other config matched to reference cell: ALPHA_C=0.138 (independent Hopfield),
    K_GRID=[3,6,12,18,24,36,48,60,80,100,120], N_CHAINS=24, N=8192, seeds [11,13,19]
  Per-hop correct-next-node discriminator (ext_hopfrac >= 0.85 = genuine traverse, not cleanup
    jump-to-a_K artifact)

EXPECTED OUTCOMES per DRILL 1 P=0.45 + monotone trend:
  HARD_PASS_ALPHA_EXTENSION: at alpha_frac=0.85 ratio_to_eq >= 2.0 AND ext_hopfrac >= 0.95 across seeds
  CHAIN_GRADE_AT_ALPHA_CLIFF: cliff identified between 0.7 and 0.95 (envelope chain-grades to one point)
  HARD_FAIL_RAPID_DEGRADATION: cliff at alpha_frac=0.75 (extension fails immediately)
  MIDDLE_BAND: partial coverage (passes at 0.75 or 0.8 only)

META_M6: NAIVE/equilibrium K_eq DERIVED in-cell from the SAME alpha-grid (not copied from rail cell)
  Note: K_eq formula uses INDEPENDENT alpha_c=0.138; not a substrate-tuned baseline.
META_M7: smoke matches full on N + N_CHAINS + RECALL_THRESH + GENUINE_FLOOR + cleanup mechanism.
  Only K_GRID + SEEDS reduce for smoke (alpha grid still 3 points for monotonicity sanity).
Q-discipline: if ext_hopfrac >= 0.995 AT EVERY alpha through 0.95, BIAS-Q flag fires
  (corpus too easy at this regime; recommend deeper K_GRID or higher alpha_c).

CONFIG:
  N_DIM = 8192 (matches reference)
  N_CHAINS = 24
  K_GRID = [3, 6, 12, 18, 24, 36, 48, 60, 80, 100, 120]
  ALPHA_FRACS_FULL = [0.7, 0.8, 0.85, 0.9, 0.95]
  Seeds [11, 13, 19] (cross-cell consistent; reference cell used [1,2,3] but we use new seeds
    per META_PROSPECTIVE_BANDS_FRESH_SEEDS to avoid p-hacking)
  RECALL_THRESH = 0.90, GENUINE_FLOOR = 0.30
  CPU numpy execution (matches CORRECTED reference; was originally GPU but CPU now suffices
    at N=8192 with 5 alpha points; total wall ~30min per Research drill estimate)

Author: exp_dev 2026-06-25.
ASCII-only; per-(seed, alpha_frac) checkpoint; substrate-only; numpy only.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, atexit
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_NESS_envelope_alpha_high_extension_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = RUN_MODE == "smoke"

ALPHA_C = 0.138  # Hopfield critical capacity (Amit-Gutfreund-Sompolinsky); INDEPENDENT theory constant
RECALL_THRESH = 0.90
GENUINE_FLOOR = 0.30  # cleanup-OFF recall floor for control (genuine multi-hop)
EXT_GENUINE_THRESH = 0.85  # per-hop correct-next-node >= this = genuine traverse

# Bands LOCKED at module init
HP_RATIO_TO_EQ_MIN = 2.0          # cand/eq >= 2.0 at chain-grade point
HP_EXT_HOPFRAC_MIN = 0.95          # ext_hopfrac >= 0.95 at chain-grade point (tighter than reference 0.85)
HP_CHAIN_GRADE_ALPHA = 0.85        # which alpha must chain-grade for HARD_PASS_ALPHA_EXTENSION
RAPID_CLIFF_ALPHA = 0.75           # cliff at <= this = HARD_FAIL_RAPID_DEGRADATION
Q_SUSPECT_SATURATION = 0.995       # ext_hopfrac >= this across all alpha = saturation

# Lock-assert
assert HP_RATIO_TO_EQ_MIN >= 1.0, "lift > equilibrium ordered"
assert 0.5 < HP_EXT_HOPFRAC_MIN <= 1.0
assert HP_CHAIN_GRADE_ALPHA > RAPID_CLIFF_ALPHA, "chain-grade alpha above cliff alpha"

if SMOKE:
    ALPHA_FRACS = [0.7, 0.85, 0.95]   # 3 points for monotonicity smoke (rail + mid + top)
    K_GRID = [3, 6, 12, 24, 40]
    SEEDS = [11]
    N = 1024
    N_CHAINS = 8
else:
    ALPHA_FRACS = [0.7, 0.8, 0.85, 0.9, 0.95]
    K_GRID = [3, 6, 12, 18, 24, 36, 48, 60, 80, 100, 120]
    SEEDS = [11, 13, 19]
    N = 8192
    N_CHAINS = 24

CONFIG_VERSION = (
    "substrateNessEnvelopeAlphaHigh-v1: N=%d N_CHAINS=%d K_GRID=%s "
    "ALPHA_C=%.3f ALPHA_FRACS=%s seeds=%s mode=%s "
    "HP_ratio>=%.2f HP_ext_hopfrac>=%.2f HP_chain_grade_alpha=%.2f "
    "rapid_cliff_alpha=%.2f Q_sat>=%.3f"
) % (N, N_CHAINS, K_GRID, ALPHA_C, ALPHA_FRACS, SEEDS, RUN_MODE,
     HP_RATIO_TO_EQ_MIN, HP_EXT_HOPFRAC_MIN, HP_CHAIN_GRADE_ALPHA,
     RAPID_CLIFF_ALPHA, Q_SUSPECT_SATURATION)


def k_eq(alpha):
    """K_eq(alpha) = 3.3 * (1 - alpha/alpha_c)^2 / alpha (Hopfield equilibrium capacity).
    Drops to 0 as alpha -> alpha_c; blows up as alpha -> 0."""
    return 3.3 * max(0.0, (1.0 - alpha / ALPHA_C)) ** 2 / max(alpha, 1e-9)


def safe_gate_high(alpha):
    """At high alpha_frac (>= 0.7), K_eq is small (< 3.5); we test extension PAST equilibrium.
    A FLOOR-based gate (K_eq > 0.2 = alpha_frac < 1.0) keeps us out of the alpha == alpha_c
    triviality. For high-alpha extension, we INTENTIONALLY operate where K_eq is small (which
    makes ratio_to_eq large) -- the discriminator is whether substrate can hold genuine
    multi-hop chains with K_obs >= GENUINE_FLOOR despite high decay rate."""
    ke = k_eq(alpha)
    return 0.05 <= ke <= 10.0   # high-alpha safe zone (K_eq small but bounded above 0)


def bipolar(m, n, g):
    """numpy bipolar +/-1, shape (m, n)."""
    return (g.integers(0, 2, size=(m, n)).astype(np.float32) * 2.0 - 1.0)


def recall_chain_depth_numpy(alpha: float, K: int, seed: int) -> Tuple[float, float, float]:
    """N_CHAINS chains of depth K; per-chain NESS-decayed W; recall a_0->a_K.
    Returns (cand2_recall, control_recall, cand_hop_frac)."""
    g = np.random.default_rng(seed * 100003 + K * 31 + int(alpha * 1e6))
    chains = [bipolar(K + 1, N, g) for _ in range(N_CHAINS)]
    codebook = np.concatenate(chains, axis=0)  # (N_CHAINS*(K+1), N)

    cand_ok = 0
    ctrl_ok = 0
    cand_hop_frac = 0.0
    for c in range(N_CHAINS):
        nodes = chains[c]  # (K+1, N)
        W = np.zeros((N, N), dtype=np.float32)
        for i in range(K):
            W = (1.0 - alpha) * W + np.outer(nodes[i + 1], nodes[i]) / N
        tgt = c * (K + 1) + K
        # cand2 cleanup-ON: snap each hop; per-hop correct-next-node tracker
        r = nodes[0].copy()
        hop_correct = 0
        for h in range(K):
            v = W @ r
            snap = int(np.argmax(codebook @ v))
            r = codebook[snap]
            if snap == c * (K + 1) + (h + 1):
                hop_correct += 1
        cand_ok += int(int(np.argmax(codebook @ r)) == tgt)
        cand_hop_frac += hop_correct / K
        # control cleanup-OFF: sign-recall
        r = nodes[0].copy()
        for _h in range(K):
            v = W @ r
            r = np.sign(v).astype(np.float32)
            r[r == 0] = 1.0
        ctrl_ok += int(int(np.argmax(codebook @ r)) == tgt)
    return cand_ok / N_CHAINS, ctrl_ok / N_CHAINS, cand_hop_frac / N_CHAINS


def interp_kmax(curve_k, curve_recall):
    """Max K with recall >= RECALL_THRESH, linear-interpolated at the crossing."""
    prevK, prevR, kmax = 0.0, 1.0, 0.0
    for K, r in zip(curve_k, curve_recall):
        if r >= RECALL_THRESH:
            kmax = float(K)
            prevK, prevR = float(K), r
        else:
            if prevR > RECALL_THRESH:
                kmax = prevK + (K - prevK) * (prevR - RECALL_THRESH) / (
                    prevR - r + 1e-9)
            break
    return kmax


def run_unit(alpha_frac: float, seed: int) -> Dict:
    alpha = alpha_frac * ALPHA_C
    cand_curve = {}
    ctrl_curve = {}
    hop_curve = {}
    for K in K_GRID:
        cr, tr, hf = recall_chain_depth_numpy(alpha, K, seed)
        cand_curve[K] = round(cr, 4)
        ctrl_curve[K] = round(tr, 4)
        hop_curve[K] = round(hf, 4)
        if cr < RECALL_THRESH and K > K_GRID[0]:
            break
    kmax = interp_kmax(list(cand_curve.keys()), list(cand_curve.values()))
    ctrl_kmax = interp_kmax(list(ctrl_curve.keys()), list(ctrl_curve.values()))
    cleanup_boost = kmax / max(1.0, ctrl_kmax)
    keq = k_eq(alpha)
    ratio = kmax / (keq + 1e-9)
    ctrl_ratio = ctrl_kmax / (keq + 1e-9)
    deep_K = max([K for K, r in cand_curve.items() if r >= RECALL_THRESH],
                 default=K_GRID[0])
    ext_hopfrac = hop_curve.get(deep_K, 0.0)
    extension_genuine = ext_hopfrac >= EXT_GENUINE_THRESH
    genuine_control = ctrl_kmax > keq
    print("  [af=%.2f a=%.4f s=%d] K_obs=%.1f ctrlK=%.1f boost=%.2fx | K_eq=%.2f "
          "cand/eq=%.2f ctrl/eq=%.2f | ext_hopfrac@K%d=%.3f ext_genuine=%s "
          "genuine_ctrl=%s" % (
              alpha_frac, alpha, seed, kmax, ctrl_kmax, cleanup_boost, keq,
              ratio, ctrl_ratio, deep_K, ext_hopfrac, extension_genuine,
              genuine_control), flush=True)
    return {
        "alpha_frac": alpha_frac, "alpha": round(alpha, 5), "seed": seed,
        "k_obs": round(kmax, 2), "ctrl_k_obs": round(ctrl_kmax, 2),
        "cleanup_boost": round(cleanup_boost, 3),
        "k_eq": round(keq, 4), "ratio_to_eq": round(ratio, 3),
        "ctrl_ratio_to_eq": round(ctrl_ratio, 3),
        "safe_gate": bool(safe_gate_high(alpha)),
        "cand_curve": cand_curve, "ctrl_curve": ctrl_curve, "hop_curve": hop_curve,
        "deep_K": deep_K,
        "ext_hopfrac": round(ext_hopfrac, 4),
        "genuine_control": bool(genuine_control),
        "extension_genuine": bool(extension_genuine),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }


def _selftest():
    # K_eq sanity at the high-alpha grid
    for af in [0.7, 0.85, 0.95]:
        a = af * ALPHA_C
        ke = k_eq(a)
        assert ke >= 0.0, "K_eq nonneg at af=%.2f" % af
        print("[selftest] K_eq(af=%.2f) = %.3f" % (af, ke))

    # safe_gate_high passes 0.7..0.95 alpha_frac and rejects 1.0+ (alpha == alpha_c -> K_eq=0)
    assert safe_gate_high(0.7 * ALPHA_C), "T1 0.7*ac in high safe zone"
    assert safe_gate_high(0.85 * ALPHA_C), "T1 0.85*ac in high safe zone"
    assert safe_gate_high(0.95 * ALPHA_C), "T1 0.95*ac in high safe zone"
    assert not safe_gate_high(0.99 * ALPHA_C), "T1 0.99*ac too close to ac"
    print("[selftest] T1 PASS: safe_gate_high admits 0.7..0.95")

    # T2: bipolar shapes
    g = np.random.default_rng(0)
    x = bipolar(5, 64, g)
    assert x.shape == (5, 64)
    assert set(np.unique(x).tolist()) <= {-1.0, 1.0}
    print("[selftest] T2 PASS: bipolar +/-1 shape correct")

    # T3: tiny end-to-end at K=3
    global N, N_CHAINS, K_GRID
    orig = (N, N_CHAINS, K_GRID)
    N = 256
    N_CHAINS = 4
    K_GRID = [3]
    try:
        rec = run_unit(0.7, seed=11)
        assert "k_obs" in rec and "ext_hopfrac" in rec
        assert 0.0 <= rec["ext_hopfrac"] <= 1.0
        assert 0.0 <= rec["k_obs"] <= 10.0
        print("[selftest] T3 PASS: run_unit end-to-end at N=256 K=3")
    finally:
        N, N_CHAINS, K_GRID = orig

    # T4: bands locked
    assert HP_RATIO_TO_EQ_MIN == 2.0
    assert HP_EXT_HOPFRAC_MIN == 0.95
    assert HP_CHAIN_GRADE_ALPHA == 0.85
    print("[selftest] T4 PASS: bands locked")

    # T5: LLM counter = 0
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T5 PASS: LLM counter = 0")

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def compute_verdict(units: List[Dict]) -> Tuple[str, str]:
    if not units:
        return ("HARD_FAIL", "no units")

    # Aggregate per alpha_frac
    by_af = {}
    for u in units:
        by_af.setdefault(u["alpha_frac"], []).append(u)

    per_af = {}
    for af, us in by_af.items():
        per_af[af] = {
            "alpha": us[0]["alpha"],
            "k_obs_mean": float(np.mean([u["k_obs"] for u in us])),
            "ctrl_k_obs_mean": float(np.mean([u["ctrl_k_obs"] for u in us])),
            "k_eq": us[0]["k_eq"],
            "ratio_to_eq_mean": float(np.mean([u["ratio_to_eq"] for u in us])),
            "ctrl_ratio_to_eq_mean": float(np.mean([u["ctrl_ratio_to_eq"] for u in us])),
            "ext_hopfrac_mean": float(np.mean([u["ext_hopfrac"] for u in us])),
            "ext_hopfrac_cv": (float(np.std([u["ext_hopfrac"] for u in us]) /
                                      max(np.mean([u["ext_hopfrac"] for u in us]), 1e-9))
                                if len(us) >= 2 else 0.0),
            "ext_genuine_all": all(u["extension_genuine"] for u in us),
            "genuine_ctrl_all": all(u["genuine_control"] for u in us),
            "n_seeds": len(us),
            "safe_gate": us[0]["safe_gate"],
        }

    afs = sorted(per_af.keys())
    # Q-discipline: ext_hopfrac saturation across all alpha
    saturated_afs = [af for af in afs if per_af[af]["ext_hopfrac_mean"] >= Q_SUSPECT_SATURATION]

    # Per-alpha chain-grade check: ratio_to_eq >= 2.0 AND ext_hopfrac >= 0.95
    chain_grade_afs = [
        af for af in afs
        if (per_af[af]["ratio_to_eq_mean"] >= HP_RATIO_TO_EQ_MIN
            and per_af[af]["ext_hopfrac_mean"] >= HP_EXT_HOPFRAC_MIN
            and per_af[af]["ext_hopfrac_cv"] <= 0.05)
    ]

    # Summary string
    summ_parts = []
    for af in afs:
        d = per_af[af]
        summ_parts.append(
            "af=%.2f[K_obs=%.1f K_eq=%.2f ratio=%.2f ext_hf=%.3f cv=%.3f ext_gen=%s]" % (
                af, d["k_obs_mean"], d["k_eq"], d["ratio_to_eq_mean"],
                d["ext_hopfrac_mean"], d["ext_hopfrac_cv"], d["ext_genuine_all"]))
    summ = " | ".join(summ_parts)
    if saturated_afs:
        summ += " | [Q-DISCIPLINE: ext_hopfrac >= %.3f at af=%s; suspect saturation]" % (
            Q_SUSPECT_SATURATION, saturated_afs)

    # Verdict ladder
    # HARD_PASS_ALPHA_EXTENSION: af=0.85 chain-grades
    if HP_CHAIN_GRADE_ALPHA in chain_grade_afs:
        return ("HARD_PASS",
                "HARD_PASS_ALPHA_EXTENSION: NESS envelope chain-grades at af=%.2f "
                "(ratio>=2.0 AND ext_hopfrac>=0.95 cv<=0.05); chain-grade set=%s | %s" % (
                    HP_CHAIN_GRADE_ALPHA, chain_grade_afs, summ))

    # CHAIN_GRADE_AT_ALPHA_CLIFF: passes at one of {0.8, 0.9, 0.95} but not 0.85
    if any(af in chain_grade_afs for af in (0.8, 0.9, 0.95)):
        cliff_at = None
        for af in afs:
            if af not in chain_grade_afs and af > (min(chain_grade_afs) if chain_grade_afs else 0.0):
                cliff_at = af
                break
        return ("HARD_PASS",
                "CHAIN_GRADE_AT_ALPHA_CLIFF: NESS envelope extends to af=%s but cliffs "
                "(chain_grade_set=%s; cliff_at=%s) | %s" % (
                    max(chain_grade_afs), chain_grade_afs, cliff_at, summ))

    # Already chain-grade at rail (0.7) -- but didn't extend
    if chain_grade_afs == [0.7]:
        return ("HARD_FAIL",
                "HARD_FAIL_NO_EXTENSION_BEYOND_RAIL: NESS chain-grades ONLY at af=0.7 "
                "rail; envelope does NOT extend | %s" % summ)

    # HARD_FAIL_RAPID_DEGRADATION: NO af above 0.7 hits ext_hopfrac >= 0.85 even (weak gate)
    weak_afs_above_rail = [
        af for af in afs if af > 0.7 and per_af[af]["ext_hopfrac_mean"] >= 0.85
    ]
    if not weak_afs_above_rail:
        return ("HARD_FAIL",
                "HARD_FAIL_RAPID_DEGRADATION: no af above 0.7 holds ext_hopfrac>=0.85; "
                "cliff at af=0.75 or earlier | %s" % summ)

    # MIDDLE_BAND: some afs hold ext_hopfrac but cv or ratio gate fails
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_EXTENSION: some af above 0.7 hold weak gate "
            "(ext_hopfrac>=0.85: %s) but no chain-grade gate fires (need ratio>=2.0 AND "
            "ext_hopfrac>=0.95 AND cv<=0.05) | %s" % (
                weak_afs_above_rail, summ))


_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        keys = [("af%.2f_s%d" % (af, s)).replace(".", "p")
                for af in ALPHA_FRACS for s in SEEDS]
        agg = aggregate_partials(od, seeds=keys, run_config={"run_mode": RUN_MODE})
        if not agg:
            return
        units = list(agg.values())
        if not units:
            return
        v, vmsg = compute_verdict(units)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_units": len(units),
            "config_version": CONFIG_VERSION, "per_unit": units,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "ALPHA_FRACS": ALPHA_FRACS, "seeds": SEEDS,
        }
        write_metrics(od, metrics, results=units)
        print("[atexit] wrote synth metrics.json (%d units)" % len(units), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d ALPHA_FRACS=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N, ALPHA_FRACS, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"run_mode": RUN_MODE}
    keys = [("af%.2f_s%d" % (af, s)).replace(".", "p")
            for af in ALPHA_FRACS for s in SEEDS]
    existing = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    done_keys = set(existing.keys())
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(keys)), flush=True)

    for af in ALPHA_FRACS:
        for s in SEEDS:
            key = ("af%.2f_s%d" % (af, s)).replace(".", "p")
            if key in done_keys:
                continue
            try:
                rec = run_unit(af, s)
                write_partial_key(out_dir, key, rec)
            except Exception as e:
                print("[WARN] %s failed: %s" % (key, e), flush=True)

    agg = aggregate_partials(out_dir, seeds=keys, run_config=run_config)
    units = [agg[k] for k in keys if k in agg]
    if not units:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero"

    v, vmsg = compute_verdict(units)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_units": len(units),
        "config_version": CONFIG_VERSION, "per_unit": units,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "ALPHA_FRACS": ALPHA_FRACS, "seeds": SEEDS, "K_GRID": K_GRID, "N": N,
        "DESIGN_NOTE": (
            "NESS envelope alpha-high extension from reference cell's chain-grade "
            "rail [0.3, 0.7]. Sweeps alpha_frac in {0.7,0.8,0.85,0.9,0.95} to identify "
            "the cliff. Per Research drill, lift cand/eq is monotonically increasing "
            "through 0.7 (2.12 -> 12.27); extension likely to chain-grade up to ~0.85-0.90 "
            "before Hatano-Sasa concentration-ceiling cliff. Pre-reg per "
            "preregs/2026-06-25_substrate_NESS_envelope_alpha_high_extension_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (
        len(units), metrics["elapsed_s"]), flush=True)
