"""EXP 3 -- THE RECONCILIATION (the meat): the SAME "completion" helps RECALL but HURTS RANK; deliver a
gold-blind readout that ROUTES BY QUERY STRUCTURE and never regresses ranking.

PROBLEM: the_register_reads_by_argmax_not_recurrent_completion, bar item 4. Two measured facts appear to
conflict:
  (A) On an overloaded register (superposition of role-filler bindings, KNOWN keys), theta-gamma SERIAL
      decode-and-suppress RECOVERS ~4x the load over argmax (exp_register_completion_readout_v1). Completion
      HELPS.
  (B) On a ranked-retrieval over a consolidated cortical store (graded, CORRELATED concept codes), recurrent
      ATTRACTOR completion HURTS -- it settles toward high-degree HUB items (bigger basins) and re-promotes
      them, corrupting a ranking the graded scores already carried (the_consolidated_cortical_store... NEW
      deviation). Completion HURTS.

THE RECONCILIATION (from the 2026-08-28 brain drill, grounded in O'Reilly & McClelland 1994 + CLS):
these are TWO DIFFERENT operations for TWO DIFFERENT query types, on TWO DIFFERENT code geometries.
  * RECALL a specific bound item/set from a superposition with KNOWN KEYS on a pattern-SEPARATED code ->
    the right op is known-key SERIAL decode-and-suppress (crosstalk cancellation). Completion helps.
  * RANK many candidates by graded similarity on a CORRELATED code -> the right op is the direct graded read
    (familiarity/global-match). Recurrent settling here imports basin-size = HUB bias. Completion hurts.
The brain's fix is ARCHITECTURAL (route ranking to a non-settling circuit), not a within-attractor de-bias
(replay is even biased TOWARD hubs). So the deliverable is a GOLD-BLIND readout that routes by QUERY
STRUCTURE (is there a known key / is this recall-a-set vs order-by-similarity) + a margin gate, and thereby
tracks the UPPER ENVELOPE of both tasks -- where each blanket policy fails one.

THIS CELL:
  PART A (rank task, self-contained, CORRELATED hub-structured codes):
     - reproduce the hub bias: attractor-settle read < graded read on target-hit@1 (CI-separated).
     - FALSIFIABLE PREDICTION test: hub corruption SCALES with settling depth (more steps -> more hub
       promotion, lower target hit@1). Witness a hub's rank RISING and the target's rank FALLING with depth.
     - info-free control: random-scored ranking = chance (the metric can fail).
  PART B (recall task): reuse the LIVE register at a fixed overload (argmax cliffs; serial recovers).
  PART C (the GATED readout over a MIXED workload): three policies --
     ALWAYS_GRADED (never complete), ALWAYS_COMPLETE (serial on recall + attractor on rank), GATED (route by
     query structure + margin). GATED must beat BOTH blanket policies on the aggregate: ALWAYS_GRADED cliffs
     on recall, ALWAYS_COMPLETE regresses rank; GATED does neither.

D fixed. Real-valued correlated codes for the rank task (cortical concept-code geometry); FHRR for the
register recall task. ASCII only. Writes ONLY to data/exp_readout_recall_vs_rank_reconciliation_v1/. NO hdlab write.

Run:  .venv/Scripts/python.exe experiments/exp_readout_recall_vs_rank_reconciliation_v1.py [--self-test | --full]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
from experiments.exp_register_completion_readout_v1 import decode_argmax, decode_serial, _gen, _margin  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_readout_recall_vs_rank_reconciliation_v1")
SEED = 20260828

# Rank-task regime: STRONG graded baseline (a good cue reliably finds the target) so the attractor's
# hub-drift degradation is unambiguous. Hub bias is a MODERATE-beta, multi-step phenomenon (beta too high
# snaps to nearest = graded; beta too low collapses fully to the hub) -- the settling IS the pathology.
RANK_KW = dict(n_items=120, d=128, n_hubs=6, cluster_alpha=0.70, cue_gamma=0.80, beta=6.0, n_queries=300)


# ==================================================================================================
# PART A -- the RANK task over CORRELATED, hub-structured codes.
# ==================================================================================================
def _unit(x):
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.clip(n, 1e-12, None)


def make_hub_world(n_items, d, n_hubs, cluster_alpha, rng):
    """Correlated concept-code world with HUBS. n_hubs prototype directions; each non-hub item clusters
    around a prototype (alpha toward proto + (1-alpha) random) -> prototypes are CENTRAL/high-degree = hubs.
    Returns (codes (N,d) unit, hub_ids set, assign (N,) prototype id)."""
    protos = _unit(rng.standard_normal((n_hubs, d)))
    assign = rng.integers(0, n_hubs, size=n_items)
    codes = np.empty((n_items, d))
    hub_ids = []
    # first n_hubs items ARE the hubs (the prototype itself = maximally central)
    for i in range(n_items):
        if i < n_hubs:
            codes[i] = protos[i]
            assign[i] = i
            hub_ids.append(i)
        else:
            codes[i] = cluster_alpha * protos[assign[i]] + (1 - cluster_alpha) * rng.standard_normal(d)
    return _unit(codes), set(hub_ids), assign


def _attractor_settle(q, codes, steps, beta):
    """Modern-Hopfield / recurrent attractor settle of query q over the code matrix (Ramsauer 2020, real).
    state <- normalize(softmax(beta * codes @ state) @ codes). steps=0 returns q unchanged (= graded read)."""
    state = q.copy()
    for _ in range(steps):
        s = beta * (codes @ state)
        s -= s.max()
        w = np.exp(s); w /= (w.sum() + 1e-30)
        state = w @ codes
        state = state / max(np.linalg.norm(state), 1e-12)
    return state


def rank_task(n_items=120, d=128, n_hubs=6, cluster_alpha=0.70, cue_gamma=0.80, steps=4, beta=6.0,
              n_queries=300, seed=1):
    """For non-hub targets, build a partial cue and rank all items by score under GRADED vs ATTRACTOR read.
    Returns dict with target hit@1, mean target rank, mean hub rank, for graded and attractor, + chance."""
    rng = np.random.default_rng(seed)
    codes, hub_ids, assign = make_hub_world(n_items, d, n_hubs, cluster_alpha, rng)
    non_hub = [i for i in range(n_items) if i not in hub_ids]
    targets = rng.choice(non_hub, size=min(n_queries, len(non_hub)), replace=len(non_hub) < n_queries)

    def _ranks(scores, tgt):
        # rank of target (0 = best) and mean rank of hubs
        order = np.argsort(-scores)
        rankpos = np.empty(n_items, dtype=int)
        rankpos[order] = np.arange(n_items)
        return rankpos[tgt], float(np.mean([rankpos[h] for h in hub_ids]))

    g_hit = a_hit = 0
    g_tr, a_tr, g_hr, a_hr = [], [], [], []
    rand_hit = 0
    for t in targets:
        q = cue_gamma * codes[t] + (1 - cue_gamma) * rng.standard_normal(d)
        q = q / max(np.linalg.norm(q), 1e-12)
        gs = codes @ q                               # graded read (no settle)
        settled = _attractor_settle(q, codes, steps, beta)
        as_ = codes @ settled                        # attractor read
        g_hit += int(np.argmax(gs) == t)
        a_hit += int(np.argmax(as_) == t)
        rnd = rng.standard_normal(n_items)
        rand_hit += int(np.argmax(rnd) == t)
        gt, gh = _ranks(gs, t); at, ah = _ranks(as_, t)
        g_tr.append(gt); a_tr.append(at); g_hr.append(gh); a_hr.append(ah)
    n = len(targets)
    return {"n": n, "n_items": n_items, "n_hubs": n_hubs, "steps": steps,
            "graded_hit1": round(g_hit / n, 4), "attractor_hit1": round(a_hit / n, 4),
            "chance_hit1": round(rand_hit / n, 4),
            "graded_target_rank": round(float(np.mean(g_tr)), 2), "attractor_target_rank": round(float(np.mean(a_tr)), 2),
            "graded_hub_rank": round(float(np.mean(g_hr)), 2), "attractor_hub_rank": round(float(np.mean(a_hr)), 2)}


def rank_task_boot(steps=4, n_boot=1000, seed=1):
    """Bootstrap the paired graded-minus-attractor hit@1 gap over queries (same RANK_KW regime)."""
    kw = RANK_KW
    r = rank_task(steps=steps, seed=seed, **kw)
    rr = np.random.default_rng(seed)
    codes, hub_ids, _ = make_hub_world(kw["n_items"], kw["d"], kw["n_hubs"], kw["cluster_alpha"], rr)
    non_hub = [i for i in range(kw["n_items"]) if i not in hub_ids]
    nq = kw["n_queries"]
    targets = rr.choice(non_hub, size=min(nq, len(non_hub)), replace=len(non_hub) < nq)
    gh, ah = [], []
    for t in targets:
        q = kw["cue_gamma"] * codes[t] + (1 - kw["cue_gamma"]) * rr.standard_normal(kw["d"])
        q = q / max(np.linalg.norm(q), 1e-12)
        gh.append(int(np.argmax(codes @ q) == t))
        ah.append(int(np.argmax(codes @ _attractor_settle(q, codes, steps, kw["beta"])) == t))
    gh, ah = np.asarray(gh), np.asarray(ah)
    bt = np.random.default_rng(seed + 5)
    idx = bt.integers(0, len(gh), size=(n_boot, len(gh)))
    diff = (gh[idx].mean(1) - ah[idx].mean(1))
    lo, hi = np.percentile(diff, [2.5, 97.5])
    r["graded_minus_attractor_hit1"] = {"mean": round(float(diff.mean()), 4), "lo": round(float(lo), 4),
                                        "hi": round(float(hi), 4), "hw": round(float((hi - lo) / 2), 4)}
    return r


# ==================================================================================================
# PART B -- the RECALL task on the LIVE register (reuse exp1 machinery) + the CA1-COMPARATOR gate.
# ==================================================================================================
def _recon_residual(est, keys, role_mat, rawsum):
    """CA1-comparator (Vinogradova 2001) match/mismatch: reconstruct the superposition from the decoded
    estimates and measure how much of the stored trace it FAILS to explain. Gold-blind (no truth).
    residual = ||rawsum - sum_s bind(est_s, key_s)|| / ||rawsum||. Low = the readout explains the trace."""
    import hdlab.binding as _b
    recon = _b.bind(role_mat[est[0]], keys[0]).clone()
    for s in range(1, len(keys)):
        recon = recon + _b.bind(role_mat[est[s]], keys[s])
    return float(torch.linalg.vector_norm(rawsum - recon) / torch.linalg.vector_norm(rawsum).clamp_min(1e-12))


def decode_gated_recall(rawsum, keys, role_mat, n_iter=6, clean_eps=0.05, accept_eps=0.15):
    """The readout that KNOWS WHEN to complete -- CA1 comparator (Vinogradova 2001) as an EXACT-MATCH gate.
    (1) If argmax already reconstructs the trace (residual < clean_eps: full cue / low load) -> keep cheap
        argmax (completion inert; Nakazawa full-cue result).
    (2) Else run serial and ACCEPT it ONLY if it (near-)EXACTLY reconstructs the trace (residual <
        accept_eps). The TRUE joint solution reconstructs the stored sum exactly (residual ~0); a SPURIOUS
        diverged solution at extreme overload reconstructs only PARTIALLY (residual ~0.5) with wrong
        assignments -- a partial match IS the mismatch/novelty signal, so it is REJECTED in favour of argmax.
        (Merely 'lower residual than argmax' is NOT enough -- the spurious solution has lower residual yet
        worse accuracy; only near-exact match certifies the completion.) Returns (est, which)."""
    est_a = decode_argmax(rawsum, keys, role_mat)
    res_a = _recon_residual(est_a, keys, role_mat, rawsum)
    if res_a < clean_eps:
        return est_a, "argmax_inert"
    est_s = decode_serial(rawsum, keys, role_mat, n_iter=n_iter)
    res_s = _recon_residual(est_s, keys, role_mat, rawsum)
    return (est_s, "serial") if res_s < accept_eps else (est_a, "argmax_fallback")


def recall_task(d=256, m=64, v=100, n_reps=30, seed=1, n_iter=6):
    """Per-slot recall accuracy under ARGMAX, SERIAL, and the CA1-comparator GATED readout."""
    ARMS = ["argmax", "serial", "gated"]
    per_rep = {a: [] for a in ARMS}
    which = {}
    for rep in range(n_reps):
        g = _gen(seed + rep * 7919)
        role_vocab = [f"r{i}" for i in range(v)]
        reg = AccumulateRegister(role_vocab, d, g, max_event_slots=m)
        role_mat = torch.stack([reg.role_vecs[r] for r in role_vocab], dim=0)
        keys = [reg.idx_vecs[s] for s in range(m)]
        rr = np.random.default_rng(seed + rep * 7919 + 1)
        truth = [int(rr.integers(0, v)) for _ in range(m)]
        for s in range(m):
            reg.add_event("e", role_vocab[truth[s]], s)
        rawsum = torch.stack(reg._events["e"], dim=0).sum(dim=0)
        arg = decode_argmax(rawsum, keys, role_mat)
        ser = decode_serial(rawsum, keys, role_mat, n_iter=n_iter)
        gat, w = decode_gated_recall(rawsum, keys, role_mat, n_iter=n_iter)
        which[w] = which.get(w, 0) + 1
        per_rep["argmax"].append(float(np.mean([int(arg[s] == truth[s]) for s in range(m)])))
        per_rep["serial"].append(float(np.mean([int(ser[s] == truth[s]) for s in range(m)])))
        per_rep["gated"].append(float(np.mean([int(gat[s] == truth[s]) for s in range(m)])))
    out = {a: round(float(np.mean(per_rep[a])), 4) for a in ARMS}
    out["gate_choice"] = which
    return out


def gate_across_load(seed=1):
    """Diagnostic: the CA1-comparator gate must track the BETTER arm at every load -- pick SERIAL in the
    recovery window and fall back to ARGMAX at extreme overload where serial DIVERGES (the M>=96 own-cliff)."""
    rows = []
    for m in [8, 32, 48, 64, 96, 128]:
        r = recall_task(m=m, n_reps=20, seed=seed)
        best = max(r["argmax"], r["serial"])
        rows.append({"M": m, "argmax": r["argmax"], "serial": r["serial"], "gated": r["gated"],
                     "gate_tracks_best": bool(r["gated"] >= best - 0.03), "choice": r["gate_choice"]})
    return rows


# ==================================================================================================
# PART C -- the GATED readout over a MIXED workload. Three policies; GATED must beat both blankets.
# ==================================================================================================
def mixed_workload(seed=1):
    """Aggregate score of three readout POLICIES over a mixed workload {recall @ overload, rank}.
    ALWAYS_GRADED: argmax on recall, graded on rank. ALWAYS_COMPLETE: serial on recall, attractor on rank.
    GATED: route by query structure (recall->serial-if-crosstalk-high, rank->graded)."""
    rec = recall_task(m=64, n_reps=30, seed=seed)               # overloaded recall (argmax cliffs)
    rnk = rank_task(steps=4, seed=seed)                          # ranking (attractor hurts)
    # per-task score for each policy
    policies = {
        "always_graded":   {"recall": rec["argmax"], "rank": rnk["graded_hit1"]},
        "always_complete": {"recall": rec["serial"], "rank": rnk["attractor_hit1"]},
        "gated":           {"recall": rec["gated"],  "rank": rnk["graded_hit1"]},
    }
    for p in policies.values():
        p["aggregate"] = round(0.5 * (p["recall"] + p["rank"]), 4)
    return {"recall_detail": rec, "rank_detail": rnk, "policies": policies}


# ==================================================================================================
def cue_degradation_curve(seed=SEED):
    """Falsifiable prediction, part 2 (semantic-dementia signature): hub-corruption should get WORSE as the
    CUE DEGRADES (more reliance on attractor fill-in). Sweep cue completeness at FIXED settling depth; the
    graded-minus-attractor gap should GROW as the cue weakens."""
    out = []
    for cg in [0.9, 0.85, 0.8, 0.75, 0.7]:
        kw = dict(RANK_KW); kw["cue_gamma"] = cg
        r = rank_task(steps=4, seed=seed, **kw)
        out.append({"cue_gamma": cg, "graded_hit1": r["graded_hit1"], "attractor_hit1": r["attractor_hit1"],
                    "gap": round(r["graded_hit1"] - r["attractor_hit1"], 4)})
    return out


def run():
    depth_curve = [rank_task(steps=s, seed=SEED) for s in [0, 1, 2, 4, 8]]
    cue_curve = cue_degradation_curve(seed=SEED)
    rank_boot = rank_task_boot(steps=4, seed=SEED)
    gate_load = gate_across_load(seed=SEED)
    mixed = mixed_workload(seed=SEED)
    return {"anchor": "readout_recall_vs_rank_reconciliation_v1",
            "rank_depth_curve": depth_curve, "cue_degradation_curve": cue_curve, "rank_boot": rank_boot,
            "gate_across_load": gate_load, "mixed_workload": mixed}


def summarize(res):
    print("\n=== PART A: RANK task -- attractor completion HURTS by hub promotion; scales with settling depth ===")
    print("  steps  target_hit1  attractor_hit1  target_rank(g->a)  hub_rank(g->a)")
    for r in res["rank_depth_curve"]:
        print(f"   {r['steps']:>2d}     {r['graded_hit1']:.3f}        {r['attractor_hit1']:.3f}       "
              f"{r['graded_target_rank']:.1f}->{r['attractor_target_rank']:.1f}        "
              f"{r['graded_hub_rank']:.1f}->{r['attractor_hub_rank']:.1f}")
    rb = res["rank_boot"]["graded_minus_attractor_hit1"]
    print(f"  graded - attractor hit@1 (steps=4): {rb['mean']:+.3f} [{rb['lo']:+.3f},{rb['hi']:+.3f}] "
          f"(chance {res['rank_depth_curve'][0]['chance_hit1']:.3f})")
    print("\n  FALSIFIABLE PREDICTION pt2 (hub-corruption WORSENS as the cue degrades -- semantic-dementia signature):")
    print("    cue_gamma  graded  attractor  gap")
    for r in res.get("cue_degradation_curve", []):
        print(f"      {r['cue_gamma']:.2f}     {r['graded_hit1']:.3f}   {r['attractor_hit1']:.3f}    {r['gap']:+.3f}")
    print("\n=== PART B: CA1-comparator GATE tracks the better recall arm at EVERY load (incl. serial's own cliff) ===")
    print("    M   argmax  serial  gated   tracks_best  gate_choice")
    for r in res["gate_across_load"]:
        print(f"  {r['M']:>3d}   {r['argmax']:.3f}   {r['serial']:.3f}   {r['gated']:.3f}    {r['gate_tracks_best']}"
              f"      {r['choice']}")
    print("\n=== PART C: GATED readout over MIXED workload {recall@overload, rank} ===")
    print("  policy            recall  rank   aggregate")
    for name, p in res["mixed_workload"]["policies"].items():
        print(f"  {name:<16s}  {p['recall']:.3f}  {p['rank']:.3f}   {p['aggregate']:.3f}")
    pol = res["mixed_workload"]["policies"]
    gated_best = (pol["gated"]["aggregate"] > pol["always_graded"]["aggregate"] and
                  pol["gated"]["aggregate"] > pol["always_complete"]["aggregate"])
    print(f"\n  GATED beats BOTH blanket policies={gated_best} -- always_graded cliffs on recall, "
          f"always_complete regresses rank; the query-structure gate does neither.")


def self_test():
    # PART A: attractor HURTS ranking (hub bias), and it scales with depth.
    r0 = rank_task(steps=0, n_queries=200, seed=1)   # steps=0 == graded
    r4 = rank_task(steps=4, n_queries=200, seed=1)
    assert abs(r0["graded_hit1"] - r0["attractor_hit1"]) < 1e-9, "steps=0 must equal graded"
    assert r4["attractor_hit1"] < r4["graded_hit1"] - 0.05, \
        f"attractor must HURT ranking (hub bias); graded={r4['graded_hit1']} attractor={r4['attractor_hit1']}"
    assert r4["attractor_hub_rank"] < r4["graded_hub_rank"], \
        f"hubs must RISE in rank under settling (lower rank# = better); {r4['graded_hub_rank']}->{r4['attractor_hub_rank']}"
    # PART B: the CA1-comparator gate must track the better arm at overload AND at serial's own divergence.
    gl = gate_across_load(seed=1)
    for r in gl:
        assert r["gate_tracks_best"], f"gate must track the better arm at M={r['M']}: {r}"
    div = [r for r in gl if r["M"] == 128][0]
    assert div["gated"] >= div["argmax"] - 0.02, \
        f"at M=128 (serial DIVERGES) the gate must fall back to argmax, not follow serial down; {div}"
    # PART C: gated beats both blanket policies.
    mx = mixed_workload(seed=1)
    pol = mx["policies"]
    assert pol["gated"]["aggregate"] > pol["always_graded"]["aggregate"] + 0.02, \
        f"gated must beat always-graded (which cliffs on recall); {pol}"
    assert pol["gated"]["aggregate"] > pol["always_complete"]["aggregate"] + 0.02, \
        f"gated must beat always-complete (which regresses rank); {pol}"
    print(f"SELF-TEST PASS: rank graded={r4['graded_hit1']:.3f} attractor={r4['attractor_hit1']:.3f} "
          f"(hub rank {r4['graded_hub_rank']:.1f}->{r4['attractor_hub_rank']:.1f}); gate tracks best at all "
          f"loads incl M128 divergence (gated={div['gated']:.3f}>=argmax={div['argmax']:.3f}); mixed aggregate "
          f"graded={pol['always_graded']['aggregate']:.3f} complete={pol['always_complete']['aggregate']:.3f} "
          f"GATED={pol['gated']['aggregate']:.3f}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mode", default="full")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
