"""the_register_write_path_has_a_hard_capacity_wall -- the SECOND-STORE half: a content/salience-gated
commit into the existing HDFactStore for the old events the leaky write decays out.

The leaky/recency write (exp_register_leaky_write_capacity_v1) keeps RECENT events recoverable at any load,
but by construction DECAYS OLD events out of the buffer (the fundamental single-store trade, W10). The brain
pairs the bounded recency buffer with CONSOLIDATION to a second permanent store -- and, decisively, that
consolidation is NOT organized by recency/eviction-order: it is gated by CONTENT SALIENCE (prediction-error +
schema-congruence), committing the EXTREMES of the SLIMM U-shape (very surprising OR very congruent) and dropping
the unsurprising middle (Tse 2007/2011; van Kesteren 2012 SLIMM; Lisman-Grace/Takeuchi PE; Redondo-Morris
synaptic tagging-and-capture). See research_consolidation_salience_gate_2026-08-29.md.

THE HARD ON-DISK CONSTRAINT (reproduced here as the negative control): a derived/self-referential salience gate
HARD_FAILED on this substrate (exp_attention_salience_reliability_gate_* -- a gate read from the same channel is
fooled by correlated error). The PE signal MUST come from an INDEPENDENT channel, never re-derived from the
register's own accumulated code -- which also matches the brain (VTA/LC compute PE in a separate circuit).

5-ARM DISCRIMINATOR (the research drill's design; the store is the real hdlab.HDFactStore, glass-box, never-forgets):
  A FIFO   : commit whatever the register evicts, in eviction order (oldest-first) -- the eviction-order floor
             the brain positively RULES OUT.
  B PE     : commit high prediction-error events (independent surprise channel) -- catches the surprise extreme.
  C CONG   : commit high schema-congruence events (MDL description-length-drop channel) -- catches the congruent extreme.
  D OR     : commit max(w_pe*PE, w_cong*CONG) -- the weighted-OR that reconstructs the U-shape from BOTH extremes.
  E SELF   : commit by the register's OWN readback confidence (self-derived) -- the on-disk HARD_FAIL negative control
             (readback margin tracks RECENCY, not importance -> wastes budget on events already safe in the buffer).
  TWIN     : commit a RANDOM subset (info-free) -> loses.

Under a fixed commit BUDGET, salient events are recovered from register(recent) UNION store(committed). A gate that
commits the SALIENT old events (D) recovers them where FIFO/self/twin waste the budget. Predicted: D > {B,C} > A ~ TWIN,
E reproduces the on-disk HARD_FAIL.

Run:
  .venv/Scripts/python.exe experiments/exp_register_salience_gated_handoff_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_register_salience_gated_handoff_v1.py --run
  .venv/Scripts/python.exe experiments/exp_register_salience_gated_handoff_v1.py --smoke
"""
from __future__ import annotations

import argparse
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import binding  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec, cleanup_argmax  # noqa: E402
from hdlab.hd_fact_store import HDFactStore  # noqa: E402

D = 256
V = 100
STORE_DIM = 4096          # HDFactStore bipolar dim (exact for unique (subject,relation); the durable store)
BASE_SEED = 20260829
RESULTS = os.path.join(REPO, "data", "exp_register_salience_gated_handoff_v1")

# SLIMM U-shape thresholds: an event is SALIENT (a downstream query target + consolidation-worthy) iff it is at
# an EXTREME on EITHER latent axis. ~ 1 - (P_extreme)^2 ~= 0.19 with a 0.9 quantile on each axis.
SAL_Q = 0.90
GATE_NOISE = 0.15         # the gate observes NOISY estimates of the true latent salience (imperfect channels)


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2 ** 31))


def _build_leaky(n, seed, leak):
    """Leaky register over n events; return per-event decode-correct flag and readback margin (recency proxy)."""
    g = _gen(seed)
    role_vecs = [unit_phase_vec(D, g) for _ in range(V)]
    keys = [unit_phase_vec(D, g) for _ in range(n)]
    rr = np.random.default_rng(seed + 1)
    truth = [int(rr.integers(0, V)) for _ in range(n)]
    S = torch.zeros(D, dtype=torch.complex64)
    for j in range(n):
        S = (1.0 - leak) * S + binding.bind(role_vecs[truth[j]], keys[j])
    vocab = {i: role_vecs[i] for i in range(V)}
    correct = []
    margin = []
    role_mat = torch.stack(role_vecs)
    for j in range(n):
        rb = binding.unbind(S, keys[j])
        scores = torch.real(torch.conj(role_mat) @ rb) / D
        top2 = torch.topk(scores, 2).values
        est = int(torch.argmax(scores))
        correct.append(est == truth[j])
        margin.append(float(top2[0] - top2[1]))
    return correct, margin, truth


def _salience(n, seed):
    """Two INDEPENDENT latent salience channels (surprise, congruence) ~ U(0,1); an event is SALIENT iff it is
    at an EXTREME on either axis (the SLIMM U-shape). Returns (true_salient mask, noisy PE est, noisy CONG est)."""
    rr = np.random.default_rng(seed + 99)
    s = rr.random(n)                                    # prediction-error / surprise latent
    c = rr.random(n)                                    # schema-congruence latent
    ts, tc = np.quantile(s, SAL_Q), np.quantile(c, SAL_Q)
    salient = (s >= ts) | (c >= tc)                     # extremes on EITHER axis
    # gate observes noisy estimates on each INDEPENDENT channel
    pe_est = np.clip(s + rr.normal(0, GATE_NOISE, n), 0, None)
    cong_est = np.clip(c + rr.normal(0, GATE_NOISE, n), 0, None)
    return salient, pe_est, cong_est, s, c


def _commit_set(scores, budget, higher_is_better=True):
    """Top-`budget` events by gate score -> the committed set (indices)."""
    order = np.argsort(scores)
    if higher_is_better:
        order = order[::-1]
    return set(int(i) for i in order[:budget])


def _recall_with_store(n, seed, leak, budget, arm, w_pe=1.0, w_cong=1.0):
    """Full pipeline for one arm: leaky register (recent) + salience-gated HDFactStore commit (old). Returns
    fraction of SALIENT events recovered from register(recent) UNION store(committed), using the REAL HDFactStore."""
    correct, margin, truth = _build_leaky(n, seed, leak)
    salient, pe_est, cong_est, s_lat, c_lat = _salience(n, seed)
    correct = np.asarray(correct); margin = np.asarray(margin)

    if arm == "FIFO":
        scores = -np.arange(n)                          # oldest-first (eviction order)
    elif arm == "PE":
        scores = pe_est
    elif arm == "CONG":
        scores = cong_est
    elif arm == "OR":
        scores = np.maximum(w_pe * pe_est, w_cong * cong_est)
    elif arm == "SELF":
        scores = margin                                 # register's OWN readback confidence (recency proxy) -- neg control
    elif arm == "TWIN":
        rr = np.random.default_rng(seed + 7); scores = rr.random(n)
    else:
        raise ValueError(arm)
    committed = _commit_set(scores, budget)

    # durable commit into the REAL HDFactStore (glass-box, content-addressed, never-forgets)
    store = HDFactStore(n_dim=STORE_DIM, seed=int(seed) % 100000, use_index=True)
    for j in sorted(committed):
        store.store(subject=f"e{j}", relation="EV", obj=f"c{truth[j]}", source="register", trust="TRUST_MID")

    sal_idx = [j for j in range(n) if salient[j]]
    if not sal_idx:
        return None
    rec = 0
    for j in sal_idx:
        in_buffer = bool(correct[j])                    # recent salient events are still in the leaky buffer
        in_store = False
        if j in committed:
            q = store.query(f"e{j}", "EV")              # glass-box recovery from the durable store
            in_store = any(d["object"] == f"c{truth[j]}" for d in q)
        if in_buffer or in_store:
            rec += 1
    return rec / len(sal_idx)


def _leaky_only_recall(n, seed, leak):
    """Baseline: leaky register ALONE (no second store) -- recovers only the RECENT salient events."""
    correct, _, truth = _build_leaky(n, seed, leak)
    salient, *_ = _salience(n, seed)
    sal_idx = [j for j in range(n) if salient[j]]
    if not sal_idx:
        return None
    return sum(1 for j in sal_idx if correct[j]) / len(sal_idx)


def _boot_ci(per_trial, n_boot, seed, lo=2.5, hi=97.5):
    a = np.asarray([x for x in per_trial if x is not None], float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    b = a[idx].mean(axis=1)
    return float(a.mean()), float(np.percentile(b, lo)), float(np.percentile(b, hi))


def _boot_paired(a_t, b_t, n_boot, seed, lo=2.5, hi=97.5):
    a = np.asarray(a_t, float); b = np.asarray(b_t, float); d = a - b
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    boot = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(boot, lo)), float(np.percentile(boot, hi))


def handoff_sweep(n=200, leak=0.2, budget_frac=0.2, n_trials=24, n_boot=2000):
    budget = int(round(budget_frac * n))
    arms = ["FIFO", "PE", "CONG", "OR", "SELF", "TWIN"]
    per = {a: [] for a in arms}
    leaky_only = []
    for t in range(n_trials):
        seed = BASE_SEED + 137 * t
        leaky_only.append(_leaky_only_recall(n, seed, leak))
        for a in arms:
            per[a].append(_recall_with_store(n, seed, leak, budget, a))
    out = {"n": n, "leak": leak, "budget_frac": budget_frac, "budget": budget,
           "n_trials": n_trials, "n_boot": n_boot, "arms": {}}
    m, lo, hi = _boot_ci(leaky_only, n_boot, BASE_SEED)
    out["leaky_only"] = {"mean": round(m, 4), "ci": [round(lo, 4), round(hi, 4)]}
    for a in arms:
        m, lo, hi = _boot_ci(per[a], n_boot, BASE_SEED + hash(a) % 1000)
        out["arms"][a] = {"mean": round(m, 4), "ci": [round(lo, 4), round(hi, 4)]}
    # key contrasts (paired): OR vs FIFO floor; OR vs {PE,CONG}; OR vs TWIN; SELF vs FIFO (neg control)
    def contrast(a, b, tag):
        d, dlo, dhi = _boot_paired(per[a], per[b], n_boot, BASE_SEED + hash(tag) % 5000)
        return {"delta": round(d, 4), "ci": [round(dlo, 4), round(dhi, 4)], "sep": bool(dlo > 0)}
    out["contrasts"] = {
        "OR_minus_FIFO": contrast("OR", "FIFO", "orf"),
        "OR_minus_PE": contrast("OR", "PE", "orp"),
        "OR_minus_CONG": contrast("OR", "CONG", "orc"),
        "OR_minus_TWIN": contrast("OR", "TWIN", "ort"),
        "PE_minus_FIFO": contrast("PE", "FIFO", "pef"),
        "SELF_minus_FIFO": contrast("SELF", "FIFO", "self"),   # neg control: expect NOT above (self-derived fails)
    }
    return out


def positive_control(n=200, leak=0.2, budget_frac=0.2, n_trials=24):
    """The metric CAN move: the OR gate recovers salient OLD events that leaky-alone loses, CI-separated."""
    budget = int(round(budget_frac * n))
    orr, lo = [], []
    for t in range(n_trials):
        seed = BASE_SEED + 251 * t
        orr.append(_recall_with_store(n, seed, leak, budget, "OR"))
        lo.append(_leaky_only_recall(n, seed, leak))
    d, dlo, dhi = _boot_paired(orr, lo, 2000, BASE_SEED + 3)
    return {"OR_recall": round(float(np.mean(orr)), 3), "leaky_only_recall": round(float(np.mean(lo)), 3),
            "delta": round(d, 4), "ci": [round(dlo, 4), round(dhi, 4)], "moves": bool(dlo > 0)}


def _self_test():
    # 0. HDFactStore round-trip: a committed event recovers exactly (the durable second store works).
    st = HDFactStore(n_dim=STORE_DIM, seed=1, use_index=True)
    st.store(subject="e5", relation="EV", obj="c42", source="register", trust="TRUST_MID")
    assert any(d["object"] == "c42" for d in st.query("e5", "EV")), "store round-trip failed"
    # 1. the weighted-OR gate beats the FIFO/eviction-order floor (commit-most-salient, not oldest-evicted).
    res = handoff_sweep(n_trials=10, n_boot=500)
    arms = res["arms"]
    assert arms["OR"]["mean"] > arms["FIFO"]["mean"] + 0.05, \
        "OR must beat FIFO floor: %.3f vs %.3f" % (arms["OR"]["mean"], arms["FIFO"]["mean"])
    # 2. OR (both extremes) >= each single channel (each misses one extreme).
    assert arms["OR"]["mean"] >= arms["PE"]["mean"] - 1e-6 and arms["OR"]["mean"] >= arms["CONG"]["mean"] - 1e-6, \
        "OR must be >= single channels: OR=%.3f PE=%.3f CONG=%.3f" % (arms["OR"]["mean"], arms["PE"]["mean"], arms["CONG"]["mean"])
    # 3. the info-free TWIN loses to OR.
    assert arms["TWIN"]["mean"] < arms["OR"]["mean"] - 0.05, \
        "info-free twin must lose: TWIN=%.3f OR=%.3f" % (arms["TWIN"]["mean"], arms["OR"]["mean"])
    # 4. the SELF-derived gate (on-disk HARD_FAIL negative control) does NOT beat FIFO (it commits recent, not salient-old).
    assert not res["contrasts"]["SELF_minus_FIFO"]["sep"], \
        "self-derived gate must NOT CI-beat FIFO (neg control): %r" % res["contrasts"]["SELF_minus_FIFO"]
    # 5. positive control moves (OR rescues salient-old that leaky-alone loses).
    pc = positive_control(n_trials=10)
    assert pc["moves"], "positive control must move: %r" % pc
    print("[self-test] PASS  OR=%.3f > FIFO=%.3f; OR>=PE(%.3f),CONG(%.3f); TWIN=%.3f loses; "
          "SELF-FIFO sep=%s (neg ctrl); pos_ctrl moves (OR %.3f vs leaky-only %.3f)"
          % (arms["OR"]["mean"], arms["FIFO"]["mean"], arms["PE"]["mean"], arms["CONG"]["mean"],
             arms["TWIN"]["mean"], res["contrasts"]["SELF_minus_FIFO"]["sep"],
             pc["OR_recall"], pc["leaky_only_recall"]))


def _print(res):
    r = res["sweep"]
    print("=== SECOND-STORE: salience-gated HDFactStore handoff (commit-most-salient, NOT oldest-evicted) ===")
    print("  N=%d leak=%.2f budget=%d/%d (%.0f%%), %d trials; SLIMM U-shape salience; store=HDFactStore(%d)\n"
          % (r["n"], r["leak"], r["budget"], r["n"], 100 * r["budget_frac"], r["n_trials"], STORE_DIM))
    print("  Salient-event recall (register recent UNION store committed):")
    print("    leaky-only (no 2nd store): %.3f  %s" % (res["sweep"]["leaky_only"]["mean"], res["sweep"]["leaky_only"]["ci"]))
    order = ["FIFO", "SELF", "TWIN", "PE", "CONG", "OR"]
    for a in order:
        v = r["arms"][a]
        tag = {"FIFO": "eviction-order FLOOR", "SELF": "self-derived NEG-CTRL", "TWIN": "info-free twin",
               "PE": "prediction-error only", "CONG": "schema-congruence only", "OR": "weighted-OR (U-shape)"}[a]
        print("    %-5s %.3f  %-16s  %s" % (a, v["mean"], str(v["ci"]), tag))
    print("\n  Key contrasts (paired bootstrap):")
    for k, c in r["contrasts"].items():
        print("    %-16s %+.3f [%+.3f,%+.3f] %s" % (k, c["delta"], c["ci"][0], c["ci"][1], "SEP" if c["sep"] else "ns"))
    pc = res["positive_control"]
    print("\n  POSITIVE CONTROL: OR %.3f vs leaky-only %.3f  delta %+.3f %s"
          % (pc["OR_recall"], pc["leaky_only_recall"], pc["delta"], "MOVES" if pc["moves"] else "flat"))


def run(smoke=False):
    if smoke:
        sweep = handoff_sweep(n=120, n_trials=10, n_boot=500)
        pc = positive_control(n=120, n_trials=10)
    else:
        sweep = handoff_sweep(n_trials=30, n_boot=2000)
        pc = positive_control(n_trials=30)
    res = {"sweep": sweep, "positive_control": pc}
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "metrics.json"), "w") as f:
        json.dump(res, f, indent=2)
    _print(res)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    run(smoke=bool(args.smoke) or args.mode == "smoke")
