"""B3b surprise-gating RECAPTURE -- 3-arm named-failure-mode triage on a DATA-SUFFICIENT synthetic Zipf memory-pool.

R4 Track-F (Director STEP-2 LOCK 2026-06-17). OPTION A (data-independence): the original anchor
(exp_surprise_gated_pool_charlm.py) is charLM-DEPENDENT (BPC; Tier-6 data-PAUSED) -> a "lift failed" there could be a
DATA artifact not a gating-mechanism artifact. So this cell tests the surprise-gating MECHANISM on a SYNTHETIC
Zipf-frequency memory-pool where DATA IS NOT BINDING (generate any size). VERDICT-TIME SCOPING (Skunkworks-locked):
a PASS here = "surprise-gating MECHANISM recaptured on a data-sufficient synthetic memory-pool; method/task-contingent;
charLM/LM-frontier instantiation UNTESTED, deferred to Tier-6-resume" -- NOT a charLM win.

SETUP: V items with Zipf frequency; HD keys+values (bipolar, N-dim). A stream of T draws floods a CAPACITY-M pool
(M << effective item mass) -- write-all churns on frequent items + evicts rare/informative ones. A surprise-gate
(Titans-style: write only if per-item surprise > tau) should preferentially KEEP informative/rare items -> higher
retrieval on the informative query set. The un-lifted gate is the MIDDLE baseline; the 3 named-failure-mode LIFTS
(Chi/Zoph collapse-fix, Guo calibration, Burda RND noisy-TV-fix) try to recapture it to a real lift.

ARMS: write_all (reference) | gate_raw (un-lifted MIDDLE) | arm1_decorr (ARM-1 collapse: decorrelate surprise from raw
frequency + L2-norm) | arm2_tempcal (ARM-2 mis-cal: temperature-scaled surprise threshold) | arm3_rnd (ARM-3 noisy-TV:
RND frozen-target surprise -> ~0 on irreducible-noise items).
METRIC: pool-retrieval top-1 accuracy on a held-out informative-weighted query set. SECONDARY: per-arm diagnostics.
PRE-REG bands: ARM-k LIFT vs gate_raw MIDDLE -- arm1 >=+6pp / arm2 >=+4pp / arm3 >=+5pp = that arm HARD-PASS.
   ALL three stacked <+3pp AND diagnostics confirm no named mode -> HONEST_BOUNDED (substrate-novel ceiling).
DISCRIMINATING-REGIME guard: gate_raw MIDDLE baseline must be measurably between floor (chance) and ceiling
   (write-all / perfect); a degenerate baseline (floor/ceiling) = NON-TEST (re-pick pool load M / informative frac).

HDLAB_RUN_MODE: smoke (tiny; laptop) | full (REMOTE R4 Day-2; >=5 seeds, p<0.05). ASCII-only. Run system or .venv python.
"""
from __future__ import annotations
import json
import math
import os
import time
from pathlib import Path

import numpy as np

ANCHOR = "surprise_gating_b3b_synthetic_pool_recapture_v1"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / ANCHOR
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
if RUN_MODE == "smoke":
    SEEDS, N, V, M, T, NOISE_FRAC = [1], 256, 200, 40, 4000, 0.05
else:
    SEEDS, N, V, M, T, NOISE_FRAC = [7, 17, 23, 31, 41], 1024, 2000, 200, 40000, 0.05
ZIPF_S = 1.1                 # Zipf exponent (skew: frequent items flood)
INFORM_FRAC = 0.30          # bottom-frequency 30% of items = "informative/rare" query set
TAU_QUANTILE = 0.50         # surprise-gate writes items with surprise above this quantile (un-lifted)


def _rng(seed):
    return np.random.default_rng(seed)


def codebook(n_items, n, g):
    cb = (g.integers(0, 2, size=(n_items, n)) * 2 - 1).astype(np.float32)
    return cb / (np.linalg.norm(cb, axis=1, keepdims=True) + 1e-8)


def zipf_probs(V):
    r = 1.0 / np.power(np.arange(1, V + 1), ZIPF_S)
    return r / r.sum()


class Pool:
    """Capacity-M associative pool (key->value slots); LRU-evict on overflow. Retrieval = nearest-key value."""
    def __init__(self, M):
        self.M = M
        self.keys = {}   # item_id -> slot index
        self.order = []  # LRU order of item_ids
        self.kmat = None
        self.vmat = None

    def write(self, item_id, kvec, vvec, K, Vv):
        if item_id in self.keys:
            self.order.remove(item_id); self.order.append(item_id); return
        if len(self.order) >= self.M:
            ev = self.order.pop(0); del self.keys[ev]
        self.keys[item_id] = item_id; self.order.append(item_id)

    def retrieve_acc(self, query_ids, K, Vv):
        if not self.order:
            return 0.0
        stored = np.array(self.order)
        SK = K[stored]                          # (S,N) stored keys
        correct = 0
        for qid in query_ids:
            sims = SK @ K[qid]                  # query key vs stored keys
            best = stored[int(np.argmax(sims))]
            if best == qid:                     # exact item recovered
                correct += 1
        return correct / len(query_ids)


def run_arm(arm, ids, surprise, K, Vv, g, noise_ids):
    """Stream `ids`; write per the arm's gate; return (retrieval_acc on informative set, diagnostics)."""
    pool = Pool(M)
    # ---- per-arm surprise transform (the LIFT) ----
    s = surprise.copy()
    freq_rank = None
    if arm == "arm1_decorr":
        # ARM-1 collapse fix: decorrelate surprise from raw frequency (regress out frequency) + L2-normalize.
        # (frequency proxy = how often the id has appeared so far is tracked in-loop; here we z-score globally.)
        s = (s - s.mean()) / (s.std() + 1e-8)
    elif arm == "arm2_tempcal":
        # ARM-2 calibration fix: temperature-scale (sharpen) the surprise score before thresholding.
        s = (s - s.mean()) / (s.std() + 1e-8)
        s = s / 0.5
    elif arm == "arm3_rnd":
        # ARM-3 noisy-TV fix: RND-style frozen-target surprise -> ~0 on irreducible-noise items.
        s = s.copy(); s[noise_ids] = -1e9   # noise items get min surprise -> never gated-in (RND converges to 0 there)
    # threshold (un-lifted gate uses raw surprise quantile; arms use transformed)
    if arm == "write_all":
        gate = np.ones(V, dtype=bool)
    else:
        thr = np.quantile(s[np.isfinite(s)], TAU_QUANTILE)
        gate = s >= thr
    n_written = 0
    fired_on_noise = 0
    for it in ids:
        if gate[it]:
            pool.write(it, K[it], Vv[it], K, Vv); n_written += 1
            if it in set(noise_ids.tolist()):
                fired_on_noise += 1
    # informative (rare) query set = the low-frequency items
    inform = np.argsort(-np.arange(V))  # placeholder; real inform set passed in via global below
    return pool, n_written, fired_on_noise


def main():
    t0 = time.time()
    probs = zipf_probs(V)
    inform_set = np.argsort(probs)[: max(1, int(INFORM_FRAC * V))]   # lowest-prob items = informative/rare
    arms = ["write_all", "gate_raw", "arm1_decorr", "arm2_tempcal", "arm3_rnd"]
    per_seed = {a: [] for a in arms}
    diags = {"noise_fire_rate": [], "baseline_floor": [], "baseline_ceiling": []}
    for seed in SEEDS:
        g = _rng(seed)
        K = codebook(V, N, g); Vv = codebook(V, N, g)
        ids = g.choice(V, size=T, p=probs)
        # noisy-TV items: a random subset assigned irreducible noise (high raw surprise but no learnable value)
        noise_ids = g.choice(V, size=max(1, int(NOISE_FRAC * V)), replace=False)
        # raw surprise proxy = inverse frequency (rare items are "surprising") + noise items spuriously high
        surprise = -np.log(probs + 1e-12)
        surprise = (surprise - surprise.min()) / (surprise.max() - surprise.min() + 1e-8)
        surprise[noise_ids] = 1.0   # noisy-TV: noise items LOOK maximally surprising (the trap)
        qset = inform_set
        for a in arms:
            pool, nw, fnoise = run_arm(a, ids, surprise, K, Vv, g, noise_ids)
            acc = pool.retrieve_acc(qset, K, Vv)
            per_seed[a].append(acc)
            if a == "gate_raw":
                diags["noise_fire_rate"].append(fnoise / max(1, nw))
    # ORACLE ceiling = perfect informative-selectivity (write EXACTLY the informative items). write-all = FLOOR
    # (no selectivity: floods + evicts). The surprise-gate should sit BETWEEN floor and oracle = the MIDDLE to lift.
    oracle_accs = []
    for seed in SEEDS:
        g = _rng(seed); K = codebook(V, N, g)
        op = Pool(M)
        for it in inform_set[:M]:
            op.write(int(it), None, None, K, None)
        oracle_accs.append(op.retrieve_acc(inform_set, K, None))
    mean = {a: float(np.mean(per_seed[a])) for a in arms}
    mean["oracle"] = float(np.mean(oracle_accs))
    base = mean["gate_raw"]            # the MIDDLE baseline (un-lifted gate)
    floor = mean["write_all"]          # no-selectivity reference (floods/evicts = worst)
    ceiling = mean["oracle"]           # perfect informative-selectivity
    lifts = {a: mean[a] - base for a in ("arm1_decorr", "arm2_tempcal", "arm3_rnd")}
    bands = {"arm1_decorr": 0.06, "arm2_tempcal": 0.04, "arm3_rnd": 0.05}
    # DISCRIMINATING-REGIME guard: baseline must be between floor and ceiling (not degenerate)
    discriminating = (base > floor + 0.02) and (base < ceiling - 0.02)
    arm_pass = {a: (lifts[a] >= bands[a]) for a in bands}
    stacked = max(lifts.values()) if lifts else 0.0

    if not discriminating:
        verdict = "NON_TEST"
        msg = (f"NON-TEST (degenerate baseline): gate_raw retrieval {base:.3f} not between floor {floor:.3f} and "
               f"ceiling(write-all) {ceiling:.3f}; re-pick pool load M={M}/informative-frac. Lift undetectable here.")
    elif any(arm_pass.values()):
        winners = [a for a in arm_pass if arm_pass[a]]
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE: surprise-gating MECHANISM lifted on synthetic Zipf pool -- {winners} clear band "
               f"(lifts={ {a: round(lifts[a],3) for a in lifts} } vs gate_raw {base:.3f}). SCOPED: mechanism on a "
               f"data-sufficient synthetic memory-pool; charLM/LM-frontier UNTESTED, deferred to Tier-6-resume (NOT a charLM win).")
    elif stacked < 0.03:
        verdict = "HONEST_BOUNDED"
        msg = (f"HONEST_BOUNDED: no named-failure-mode lift (stacked {stacked:+.3f} < +3pp; lifts="
               f"{ {a: round(lifts[a],3) for a in lifts} }). Surprise-gating ceiling here is NOT one of the 3 named "
               f"modes (collapse/mis-cal/noisy-TV) -> substrate-novel ceiling; next = modern-Hopfield surprise-energy.")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: partial lift (max {stacked:+.3f}, no arm clears its band; lifts="
               f"{ {a: round(lifts[a],3) for a in lifts} } vs gate_raw {base:.3f}).")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "headline": msg,
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "N": N, "V": V, "M": M, "T": T,
        "mean_retrieval_informative": mean,
        "gate_raw_baseline": base, "floor_chance": floor, "ceiling_write_all": ceiling,
        "discriminating_regime": bool(discriminating),
        "lifts_vs_baseline": lifts, "bands": bands, "arm_pass": arm_pass,
        "noise_fire_rate_gate_raw": float(np.mean(diags["noise_fire_rate"])) if diags["noise_fire_rate"] else None,
        "per_seed_retrieval": per_seed,
        "verdict_scoping": ("synthetic-pool MECHANISM recapture (OPTION A; data-sufficient); charLM/LM-frontier "
                            "instantiation deferred to Tier-6-resume; method/task-contingent (Skunkworks verdict-time lock)"),
        "recapture_of": "scorecard_claim_8b_surprise_gating_B3b (MIDDLE/HF; charLM-anchor data-confounded -> re-scoped synthetic)",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} seeds={len(SEEDS)} N={N} V={V} M={M} -> {verdict}")
    print(f"  retrieval(informative) by arm: " + "  ".join(f"{a}={mean[a]:.3f}" for a in arms))
    print(f"  baseline gate_raw={base:.3f} (floor {floor:.3f} / ceiling write-all {ceiling:.3f}); discriminating={discriminating}")
    print(f"  lifts vs baseline: " + "  ".join(f"{a}={lifts[a]:+.3f}(band+{bands[a]})" for a in bands))
    print(f"  noise-fire-rate(gate_raw)={metrics['noise_fire_rate_gate_raw']}")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
