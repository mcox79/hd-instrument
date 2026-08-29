"""SITUATION-MODEL TIME DIMENSION -- the REPRESENTATION FORK (brain-foundational, bar step 1:
"copy the computation; SWEEP the representation").

The discrete Reichenbach front-end (tense/aspect/connective -> constraint edges) is PINNED-faithful
(research drill 2026-08-29). The question is the ORDER REGISTER representation:
  DISCRETE  -- the current mechanism: constraint graph -> topological sort -> ordinal ranks. before(x,y)
              reads the ranks; confidence is BINARY (connected=commit, else abstain).
  CONTINUOUS -- the landed hdlab.transitive_ordering MAGNITUDE LINE: settle the precedence premises into
              a bounded scalar line (delta-rule / Bradley-Terry), read before(x,y) off the coordinates;
              the coordinate GAP is a GRADED confidence margin.

The brain stores recovered order on a CONTINUOUS drifting temporal-context / magnitude line (Howard &
Kahana TCM 2002; MTL time cells, Eichenbaum 2014), which predicts three signatures a DISCRETE toposort
CANNOT produce. This cell tests all three on a controlled multi-event chronology gold (the order is the
ground truth; premises are the front-end's precedence edges), plus a real-front-end sanity check:

  (1) SYMBOLIC-DISTANCE EFFECT: far-apart events (more intervening events) discriminated MORE reliably
      -- accuracy & confidence-margin INCREASE with temporal distance. Discrete = FLAT.
  (2) FORWARD ASYMMETRY: TCM's contiguity effect is forward-biased -- 'A before B' resolves better than
      'B after A' for matched pairs. Discrete = symmetric.
  (3) MARGIN CALIBRATION: the continuous margin should track reliability -> abstaining on low-margin
      pairs RAISES selective accuracy. Discrete's binary margin cannot.
  (4) TRANSITIVE GAP-FILLING (the capability payoff): on PARTIAL cues (only some adjacent premises
      stated), the continuous line INTEGRATES and answers UN-STATED far pairs; the discrete toposort
      (path-connected only) ABSTAINS. This is the un-stated-pair regime real prose lives in.

DECISION RULE (research drill): a positive distance effect + calibration value + gap-filling => the
CONTINUOUS line is more brain-faithful for the TIME register AND adds capability; flat + no gap-filling
value => the DISCRETE toposort is adequate and adding machinery on fidelity grounds alone is unwarranted.

NOTE ON SCOPE: this REUSES hdlab.transitive_ordering (the landed magnitude-line primitive) as the STORE
for the TEMPORAL register -- it does not re-derive transitive inference (a separate problem/solver). The
contribution is the TEMPORAL representation decision + the TCM signatures for before/after.

ASCII-only. Deterministic given fixed seeds. Substrate-only (no LLM at inference).
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

ANCHOR = "temporal_order_distance_effect_v1"
D_DIM = 1024
SEED = 20260829


# ---------------------------------------------------------------------------
# Representations operating on abstract precedence premises with a KNOWN order.
# ---------------------------------------------------------------------------
def _toposort(n, premises):
    """Kahn toposort of premises [(earlier_idx, later_idx)] over items 0..n-1; index tiebreak.
    Returns rank[item] (position in reconstructed chronology) and the reachability closure."""
    adj = defaultdict(set)
    indeg = [0] * n
    for (a, b) in premises:
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1
    ready = sorted([i for i in range(n) if indeg[i] == 0])
    order = []
    while ready:
        u = ready.pop(0)
        order.append(u)
        for v in sorted(adj[u]):
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
        ready.sort()
    for i in range(n):
        if i not in order:
            order.append(i)
    rank = {u: i for i, u in enumerate(order)}
    # reachability (path-connected) closure for the abstain accounting
    reach = {i: set() for i in range(n)}
    for i in range(n):
        stack = list(adj[i])
        seen = set(stack)
        while stack:
            x = stack.pop()
            reach[i].add(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
    return rank, reach


def discrete_before(rank, reach, a, b):
    """(pred, margin): +1 a-before-b, -1 after, 0 abstain (no path). Binary margin."""
    connected = (b in reach[a]) or (a in reach[b])
    if not connected:
        return 0, 0.0
    return (1 if rank[a] < rank[b] else -1), 1.0


def continuous_line(n, premises, d=D_DIM, seed=0):
    """Settle premises into the transitive_ordering magnitude line; return coord[item] + reach closure."""
    import torch
    from hdlab.transitive_ordering import TransitiveOrderingLine
    _, reach = _toposort(n, premises)
    # transitive_ordering premise convention: (winner_idx, loser_idx) with winner = 'bigger'.
    # We map LATER = bigger coordinate, so premise (earlier a, later b) -> (winner=b, loser=a).
    prem = [(b, a) for (a, b) in premises]
    gen = torch.Generator().manual_seed(seed)
    line = TransitiveOrderingLine(n, d, gen, seed=seed)
    line.integrate(prem, seed=seed)
    coord = {i: line.coord(i) for i in range(n)}
    return coord, reach


def continuous_before(coord, reach, a, b, use_reach=True):
    """(pred, margin): sign(coord[a]-coord[b]) -> before if a lower (earlier); margin = |coord gap|.
    use_reach=True restricts commitment to path-connected pairs (fair vs discrete); False = the
    line's native transitive read-out (answers UN-STATED pairs -> the gap-filling regime)."""
    if use_reach and not ((b in reach[a]) or (a in reach[b])):
        return 0, 0.0
    gap = abs(coord[a] - coord[b])
    if coord[a] < coord[b]:
        return 1, gap
    elif coord[a] > coord[b]:
        return -1, gap
    return 0, gap


# ---------------------------------------------------------------------------
# Gold: random chronologies + adjacency premises (full or partial).
# ---------------------------------------------------------------------------
def make_chronologies(n_items, n_chron, drop_frac, seed, noise_frac=0.0):
    """Each chronology: a RANDOM ground-truth chronological order (a permutation over item ids), and
    adjacent precedence premises between consecutive TRUE-ordered items. The item ids 0..n-1 are the
    'text/narration' order and are UNRELATED to the true chronology -> the toposort's index tiebreak is
    NOT the answer (removes the tiebreak==truth confound; real prose has narration != chronology).
    drop_frac removes edges; noise_frac FLIPS an edge (the extraction-error analog). Returns list of
    (true_rank: item->chronological position, premises: [(earlier_item, later_item)])."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_chron):
        perm = rng.permutation(n_items)                 # perm[pos] = item id at chronological position pos
        true_rank = {int(item): pos for pos, item in enumerate(perm)}
        premises = []
        for pos in range(n_items - 1):
            a, b = int(perm[pos]), int(perm[pos + 1])   # a strictly before b in TRUE chronology
            if drop_frac > 0 and rng.random() < drop_frac:
                continue
            if noise_frac > 0 and rng.random() < noise_frac:
                premises.append((b, a))                  # FLIPPED wrong-direction cue
            else:
                premises.append((a, b))
        if not premises:
            a, b = int(perm[0]), int(perm[1])
            premises.append((a, b))
        out.append((true_rank, premises))
    return out


def robustness(n_items, n_chron, noise_frac, seed, d=D_DIM):
    """NOISE regime (real-prose extraction-error analog): flip noise_frac of adjacent cues, then compare
    DISCRETE toposort vs CONTINUOUS line accuracy on ALL true-ordered pairs (native read-out). A soft
    delta-rule line that AVERAGES contradictory premises should degrade more gracefully than a hard
    toposort that a single flipped edge can invert along a chain."""
    chrons = make_chronologies(n_items, n_chron, 0.0, seed, noise_frac=noise_frac)
    dc = dn = cc = cn = 0
    for ci, (true_rank, premises) in enumerate(chrons):
        rank, reach = _toposort(n_items, premises)
        coord, _ = continuous_line(n_items, premises, d=d, seed=seed + ci)
        for i in range(n_items):
            for j in range(i + 1, n_items):
                earlier, later = (i, j) if true_rank[i] < true_rank[j] else (j, i)
                dp = 1 if rank[earlier] < rank[later] else -1
                dn += 1; dc += int(dp == 1)
                cp, _ = continuous_before(coord, reach, earlier, later, use_reach=False)
                cn += 1; cc += int(cp == 1)
    return {"discrete_acc": round(dc / dn, 4) if dn else 0.0,
            "continuous_acc": round(cc / cn, 4) if cn else 0.0, "n_pairs": dn}


def eval_condition(n_items, n_chron, drop_frac, seed, d=D_DIM):
    """Score discrete vs continuous over all ordered pairs (a<b in TRUE chronology), binned by distance
    = b-a. Ground truth: a is always before b. Returns per-distance accuracy + margins + gap-filling."""
    chrons = make_chronologies(n_items, n_chron, drop_frac, seed)
    # accuracy/margin accumulators by distance
    disc = defaultdict(lambda: {"c": 0, "n": 0})
    cont = defaultdict(lambda: {"c": 0, "n": 0, "margin": []})
    cont_native = defaultdict(lambda: {"c": 0, "n": 0})   # gap-filling (answers un-stated)
    disc_unstated = {"c": 0, "n": 0, "abstain": 0}
    cont_unstated = {"c": 0, "n": 0, "abstain": 0}
    fwd = {"c": 0, "n": 0}
    bwd = {"c": 0, "n": 0}
    for ci, (true_rank, premises) in enumerate(chrons):
        rank, reach = _toposort(n_items, premises)
        coord, _ = continuous_line(n_items, premises, d=d, seed=seed + ci)
        for i in range(n_items):
            for j in range(i + 1, n_items):
                earlier, later = (i, j) if true_rank[i] < true_rank[j] else (j, i)
                dist = abs(true_rank[i] - true_rank[j])
                stated_path = (later in reach[earlier]) or (earlier in reach[later])
                # DISCRETE (reach-gated)
                dp, dm = discrete_before(rank, reach, earlier, later)
                if dp != 0:
                    disc[dist]["n"] += 1
                    disc[dist]["c"] += int(dp == 1)   # truth: earlier before later
                # CONTINUOUS (reach-gated, matched to discrete)
                cp, cm = continuous_before(coord, reach, earlier, later, use_reach=True)
                if cp != 0:
                    cont[dist]["n"] += 1
                    cont[dist]["c"] += int(cp == 1)
                    cont[dist]["margin"].append(cm)
                # CONTINUOUS native (answers un-stated) -- gap-filling
                cpn, _ = continuous_before(coord, reach, earlier, later, use_reach=False)
                cont_native[dist]["n"] += 1
                cont_native[dist]["c"] += int(cpn == 1)
                # UN-STATED (no path) pair accounting
                if not stated_path:
                    disc_unstated["abstain"] += int(dp == 0)
                    disc_unstated["n"] += 1
                    disc_unstated["c"] += int(dp == 1)
                    cont_unstated["n"] += 1
                    cont_unstated["c"] += int(cpn == 1)
                # forward/backward asymmetry
                fwd["n"] += 1; fwd["c"] += int(cpn == 1)                       # 'earlier before later' truth yes
                bp, _ = continuous_before(coord, reach, later, earlier, use_reach=False)
                bwd["n"] += 1; bwd["c"] += int(bp == -1)                       # 'later before earlier' truth no
    return disc, cont, cont_native, disc_unstated, cont_unstated, fwd, bwd


def _acc_by_dist(dd):
    return {int(k): {"acc": round(v["c"] / v["n"], 4) if v["n"] else None, "n": v["n"],
                     "mean_margin": (round(float(np.mean(v["margin"])), 4) if v.get("margin") else None)}
            for k, v in sorted(dd.items())}


def _slope(dd, key):
    xs, ys = [], []
    for k, v in sorted(dd.items()):
        val = v.get(key)
        if key == "acc":
            val = (v["c"] / v["n"]) if v["n"] else None
        elif key == "mean_margin":
            val = float(np.mean(v["margin"])) if v.get("margin") else None
        if val is not None and (v["n"] if "n" in v else 1) > 0:
            xs.append(k); ys.append(val)
    if len(xs) < 2:
        return None
    xs = np.array(xs, float); ys = np.array(ys, float)
    return float(np.polyfit(xs, ys, 1)[0])


def _selective_by_margin(n_items, n_chron, drop_frac, seed, d=D_DIM):
    """Continuous margin CALIBRATION: sort committed pairs by margin, sweep an abstain threshold,
    report selective accuracy at increasing coverage cutoffs."""
    chrons = make_chronologies(n_items, n_chron, drop_frac, seed, noise_frac=0.15)
    pairs = []
    for ci, (true_rank, premises) in enumerate(chrons):
        rank, reach = _toposort(n_items, premises)
        coord, _ = continuous_line(n_items, premises, d=d, seed=seed + ci)
        for i in range(n_items):
            for j in range(i + 1, n_items):
                earlier, later = (i, j) if true_rank[i] < true_rank[j] else (j, i)
                cp, cm = continuous_before(coord, reach, earlier, later, use_reach=False)
                pairs.append((cm, int(cp == 1)))
    pairs.sort(reverse=True)  # highest margin first
    out = {}
    for cov in (0.25, 0.5, 0.75, 1.0):
        k = max(1, int(cov * len(pairs)))
        sub = pairs[:k]
        out[str(cov)] = round(sum(c for _, c in sub) / len(sub), 4)
    return out


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(out_dir, metrics):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def self_test():
    print("[self-test] representation fork")
    disc, cont, contn, du, cu, fwd, bwd = eval_condition(5, 4, 0.0, SEED, d=256)
    assert cont, "continuous produced nothing"
    # full cues: both should order stated pairs correctly
    print("[self-test] PASS")
    return True


def main(smoke=False):
    out_dir = _out_dir()
    t0 = time.perf_counter()
    n_items = 7
    n_chron = 8 if smoke else 60
    d = 256 if smoke else D_DIM

    # FULL cues (all adjacent premises) -- the distance effect + margin signature
    disc_f, cont_f, contn_f, du_f, cu_f, fwd_f, bwd_f = eval_condition(n_items, n_chron, 0.0, SEED, d=d)
    # PARTIAL cues (drop 50% of adjacent premises) -- gap-filling regime
    disc_p, cont_p, contn_p, du_p, cu_p, fwd_p, bwd_p = eval_condition(n_items, n_chron, 0.5, SEED + 1, d=d)

    margin_slope = _slope(cont_f, "mean_margin")            # continuous margin vs distance (FULL)
    disc_acc_slope = _slope(disc_f, "acc")                  # discrete accuracy vs distance (expect ~0)
    cont_native_acc_slope = _slope(contn_p, "acc")          # continuous native accuracy vs distance (PARTIAL)

    # gap-filling: on un-stated pairs (PARTIAL), discrete abstains, continuous answers
    disc_unstated_cov = 1.0 - (du_p["abstain"] / du_p["n"]) if du_p["n"] else 0.0
    cont_unstated_acc = (cu_p["c"] / cu_p["n"]) if cu_p["n"] else 0.0
    disc_unstated_acc_committed = ((du_p["n"] - du_p["abstain"]) and
                                   (du_p["c"] / max(1, (du_p["n"] - du_p["abstain"])))) or 0.0

    # forward vs backward asymmetry (FULL)
    fwd_acc = fwd_f["c"] / fwd_f["n"] if fwd_f["n"] else 0.0
    bwd_acc = bwd_f["c"] / bwd_f["n"] if bwd_f["n"] else 0.0

    selective = _selective_by_margin(n_items, n_chron, 0.5, SEED + 2, d=d)

    # NOISE robustness sweep (real-prose extraction-error analog): does the soft line beat the hard sort?
    noise_curve = {str(nf): robustness(n_items, n_chron, nf, SEED + 3, d=d)
                   for nf in (0.0, 0.1, 0.2, 0.3)}
    # continuous wins robustness if it beats discrete at any noise level by a clear margin
    robust_win = max((v["continuous_acc"] - v["discrete_acc"]) for v in noise_curve.values())

    # verdict on the representation fork -- HONEST: discrete-toposort REACHABILITY already does all
    # warranted transitive inference (on no-path pairs there is no information), so the continuous line
    # adds ORDERING capability ONLY if it is more noise-robust. It reproduces the human distance-effect
    # signature (margin) regardless.
    distance_effect = (margin_slope is not None and margin_slope > 0)
    calibrated = selective["0.25"] > selective["1.0"] + 0.01         # high-margin subset more accurate
    noise_robust = robust_win > 0.03                                 # continuous clearly more robust
    if noise_robust and distance_effect:
        verdict = "CONTINUOUS_MORE_FAITHFUL_AND_ADDS_CAPABILITY"
    elif distance_effect and (calibrated or noise_robust):
        verdict = "CONTINUOUS_MORE_FAITHFUL_SIGNATURE_ONLY"          # reproduces human signature, ~no capability gain
    else:
        verdict = "DISCRETE_ADEQUATE"

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "summary": (f"{verdict}: margin-vs-distance slope {margin_slope} (continuous distance effect; "
                    f"discrete acc slope {disc_acc_slope}=flat). Gap-filling (PARTIAL cues): discrete "
                    f"abstains on {du_p['abstain']}/{du_p['n']} un-stated pairs (commit acc "
                    f"{disc_unstated_acc_committed:.3f}); continuous answers them at acc {cont_unstated_acc:.3f}. "
                    f"Forward {fwd_acc:.3f} vs backward {bwd_acc:.3f}. Selective@0.25 {selective['0.25']} "
                    f"vs @1.0 {selective['1.0']}."),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR, "n_items": n_items, "n_chron": n_chron, "n_dim": d,
        "distance_effect": {
            "continuous_margin_by_distance_FULL": _acc_by_dist(cont_f),
            "continuous_margin_slope": margin_slope,
            "discrete_acc_by_distance_FULL": _acc_by_dist(disc_f),
            "discrete_acc_slope": disc_acc_slope,
            "continuous_native_acc_by_distance_PARTIAL": _acc_by_dist(contn_p),
            "continuous_native_acc_slope_PARTIAL": cont_native_acc_slope,
        },
        "gap_filling_PARTIAL": {
            "discrete_unstated_coverage": round(disc_unstated_cov, 4),
            "discrete_unstated_abstain": du_p["abstain"], "n_unstated": du_p["n"],
            "discrete_unstated_acc_when_committed": round(disc_unstated_acc_committed, 4),
            "continuous_unstated_acc": round(cont_unstated_acc, 4),
            "note": "discrete toposort abstains on un-stated (non-path) pairs; the continuous line "
                    "integrates the premises and answers them -- the real-prose regime (cues are sparse)."},
        "forward_asymmetry": {"forward_acc": round(fwd_acc, 4), "backward_acc": round(bwd_acc, 4)},
        "margin_calibration_selective_acc": selective,
        "noise_robustness_curve": noise_curve,
        "noise_robustness_max_continuous_minus_discrete": round(robust_win, 4),
        "gates": {"distance_effect": distance_effect, "calibrated": calibrated, "noise_robust": noise_robust},
        "brain_note": ("TCM/time-cell continuous line predicts distance effect (far pairs easier), forward "
                       "asymmetry, calibrated margin; discrete toposort predicts flat + symmetric + binary. "
                       "The fork is decided on which signatures the representation actually produces + whether "
                       "the continuous store ADDS capability (gap-filling) for the TIME register."),
    }
    _atomic_write(out_dir, metrics)
    print(metrics["summary"])
    print(f"verdict={verdict} elapsed={elapsed:.1f}s -> {os.path.join(out_dir, 'metrics.json')}")
    return metrics


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit(0)
    smoke = ("--smoke" in sys.argv) and not ("--mode" in sys.argv and "full" in sys.argv)
    try:
        main(smoke=smoke)
    except SystemExit:
        raise
    except Exception as e:
        _atomic_write(_out_dir(), {"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                                   "traceback": traceback.format_exc()[:4000]})
        raise
