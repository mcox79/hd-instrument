"""exp_curriculum_order_ingest_schema_fit_v1

Does INGESTION ORDER matter for foundation-building? Ingest the SAME facts in 3 orders under a
FIXED schema-fit gate and measure (1) final foundation QUALITY (held-out relational retrieval) and
(2) schema-fit admit-accuracy / premature-rejection during ingestion.

USER insight: "learn quantum mechanics before addition -> very different experience." Abstraction is
SCAFFOLDED, not free. A deep fact's schema-fit is RELATIVE to what is already in the foundation, so
ORDER determines what schema-fit can see. The real-data Wikidata test ingested in temporal/arbitrary
order, handicapping schema-fit.

CONSTRUCTION (glass-box, numpy, no LLM):
  - Foundation = additive-map coordinate space (reuses hdlab/additive_map's core idea: entities are
    coordinates X in R^k, relations are displacements, readout = closed-form Euclidean distance,
    compose = degree-invariant arithmetic MEAN of per-edge tail estimates). Numpy re-implementation
    (additive_map itself is torch/CSKG-coupled; this is a directional-gate cell -> proportional method).
  - Facts have a GENUINE PREREQUISITE DEPENDENCY DAG: a concept forest where a deep node's true
    coordinate x_true = x_true(parent) + delta. A node is INGESTED as (refs -> up-to-R nearest
    ancestors, with noisy observed displacements). To PLACE the node you must anchor it on refs that
    are ALREADY in the foundation. Prerequisites are REAL: a deep fact ingested before its ancestors
    has genuinely no structure to anchor to -> schema-fit ~ 0 -> mis-rejected as premature.
  - schema_fit(X) = fraction of X's refs present in the foundation (reuses reachability_audit's
    prerequisite-reachability idea). Root/axiom nodes ground on an always-present INNATE anchor set
    (core-knowledge priors) -> schema_fit = 1.
  - FIXED gate: admit iff schema_fit >= tau. tau set ONCE, principled (majority-of-prerequisites
    present), applied identically to ALL orders and BOTH regimes (anti-rig). A rejected fact is NOT
    re-queued (single-pass) -> that is exactly why order can matter.
  - Placement on admit = degree-invariant MEAN over present refs of (foundation[ref] + observed
    displacement). More prereqs present -> average of more noisy estimates -> more ACCURATE placement
    (additive_map's mean-of-estimates benefit). Errors PROPAGATE: a ref placed under a thin scaffold
    is itself noisy, so its children inherit error -> arbitrary order compounds error.

THREE ORDERS (same facts, same noisy displacements per seed -> fair):
  (A) CURRICULUM  = topological (shallow/core first).
  (B) ARBITRARY   = random permutation.
  (C) REVERSE     = deep/advanced first.

TWO REGIMES:
  - HIERARCHICAL (positive control): deep prerequisite forest -> order PROVABLY matters -> gap fires.
  - FLAT (null guard): every fact grounds directly on the always-present innate anchors (no
    prerequisites) -> schema_fit = 1 for all facts in ALL orders -> order should NOT matter. Confirms
    the order effect is prerequisite-structure-driven, not a spurious gate artifact.

METRICS (per regime x order, mean over seeds):
  - admit_rate            : fraction of TRUE facts admitted (all facts are true).
  - premature_rejection   : fraction of non-axiom TRUE facts REJECTED (would admit under curriculum).
  - foundation_quality    : held-out relational retrieval accuracy (sibling-retrieval; edges NOT used
                            during ingestion) over the built foundation.
  - mean_placement_error  : mean ||x_foundation - x_true|| over admitted nodes.

PRE-REG BANDS (see preregs/2026-07-16_curriculum_order_ingest_schema_fit_v1.md):
  HARD-PASS = HIERARCHICAL: (curriculum_quality - reverse_quality) >= 0.25 AND curriculum rescues
              schema-fit vs arbitrary ((arbitrary_premature - curriculum_premature) >= 0.20);
              AND NULL guard holds: FLAT quality spread across orders <= 0.05 AND flat premature <= 0.02.
  HARD-FAIL = HIERARCHICAL quality spread across orders <= 0.05 (gate handles any order equally).
  MIDDLE    = otherwise.

DISCRIMINATOR-FIRES (smoke gate): HIERARCHICAL reverse premature_rejection >= 0.30 (reverse must
  actually mis-reject) AND FLAT spread <= 0.05 (null must hold). If flat shows an order effect the
  mechanism is spurious -> BLOCK.

Determinism: numpy default_rng(fixed int seeds); no hash()-derived seeds; sorted() for any set ops.
ASCII-only. No emojis. Local numpy, no queue/GPU/atoms/push. Runs to completion in foreground (seconds).
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "curriculum_order_ingest_schema_fit_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Forest / fact construction.
# ---------------------------------------------------------------------------

def build_hierarchical_forest(rng, n_roots, depth, branching, k, sigma_delta, n_anchors, anchor_scale, ref_levels):
    """Deep prerequisite forest. Returns (nodes, anchors).

    nodes: list of dicts {id, depth, parent, siblings, refs (ancestor ids up to ref_levels up),
                          x_true (k,)}. Root refs = None (grounded on innate anchors).
    anchors: (n_anchors, k) always-present innate priors.
    """
    anchors = rng.normal(0.0, 1.0, size=(n_anchors, k)) * anchor_scale
    nodes = []
    children_of = {}
    nid = 0
    for r in range(n_roots):
        # root grounded near a rotating innate anchor
        a = anchors[r % n_anchors]
        x_root = a + rng.normal(0.0, sigma_delta, size=k)
        root_id = nid
        nodes.append({"id": root_id, "depth": 0, "parent": None, "refs": None, "x_true": x_root})
        nid += 1
        frontier = [root_id]
        for d in range(1, depth + 1):
            new_frontier = []
            for pid in frontier:
                for _b in range(branching):
                    x_par = nodes[pid]["x_true"]
                    x_new = x_par + rng.normal(0.0, sigma_delta, size=k)
                    cid = nid
                    nodes.append({"id": cid, "depth": d, "parent": pid, "refs": None, "x_true": x_new})
                    children_of.setdefault(pid, []).append(cid)
                    new_frontier.append(cid)
                    nid += 1
            frontier = new_frontier
    # refs = up-to-ref_levels nearest ancestors (parent, grandparent, ...)
    for nd in nodes:
        if nd["depth"] == 0:
            nd["refs"] = None
            continue
        refs = []
        cur = nd["parent"]
        while cur is not None and len(refs) < ref_levels:
            refs.append(cur)
            cur = nodes[cur]["parent"]
        nd["refs"] = sorted(refs)
    # siblings (share parent) -> held-out relational eval set
    for nd in nodes:
        p = nd["parent"]
        sibs = [c for c in children_of.get(p, []) if c != nd["id"]] if p is not None else []
        nd["siblings"] = sorted(sibs)
    return nodes, anchors


def build_flat_forest(rng, n_nodes, k, sigma_delta, n_anchors, anchor_scale):
    """Null-guard regime: every node grounds directly on the always-present innate anchors (no prereqs).

    refs = None for ALL nodes (all anchor-grounded, schema_fit = 1 in every order). Siblings = a random
    partner so the held-out relational eval is structurally comparable to the hierarchical regime.
    """
    anchors = rng.normal(0.0, 1.0, size=(n_anchors, k)) * anchor_scale
    nodes = []
    for i in range(n_nodes):
        a = anchors[i % n_anchors]
        x = a + rng.normal(0.0, sigma_delta, size=k)
        nodes.append({"id": i, "depth": 0, "parent": None, "refs": None, "x_true": x})
    ids = list(range(n_nodes))
    for nd in nodes:
        others = [j for j in ids if j != nd["id"]]
        nd["siblings"] = sorted(rng.choice(others, size=min(2, len(others)), replace=False).tolist())
    return nodes, anchors


def make_observed_displacements(rng, nodes, anchors, sigma_d):
    """Fixed per-seed noisy observed displacements, REUSED across all 3 orders (fairness).

    Returns dict: for non-root node id -> {ref_id: d_obs (k,)}; for root id -> {("A", j): d_obs}.
    d_obs(ref->X) = (x_true_X - x_true_ref) + N(0, sigma_d).
    """
    disp = {}
    for nd in nodes:
        X = nd["x_true"]
        if nd["refs"] is None:
            # grounded on innate anchors
            d = {}
            for j in range(anchors.shape[0]):
                d[("A", j)] = (X - anchors[j]) + rng.normal(0.0, sigma_d, size=X.shape[0])
            disp[nd["id"]] = d
        else:
            d = {}
            for r in nd["refs"]:
                xr = nodes[r]["x_true"]
                d[r] = (X - xr) + rng.normal(0.0, sigma_d, size=X.shape[0])
            disp[nd["id"]] = d
    return disp


# ---------------------------------------------------------------------------
# Ingestion under a FIXED schema-fit gate, in a given order.
# ---------------------------------------------------------------------------

def order_indices(nodes, order, rng):
    """Deterministic order over node ids. Ties broken by id for determinism."""
    if order == "curriculum":
        return [nd["id"] for nd in sorted(nodes, key=lambda n: (n["depth"], n["id"]))]
    if order == "reverse":
        return [nd["id"] for nd in sorted(nodes, key=lambda n: (-n["depth"], n["id"]))]
    if order == "arbitrary":
        ids = np.array([nd["id"] for nd in sorted(nodes, key=lambda n: n["id"])], dtype=np.int64)
        perm = rng.permutation(ids.shape[0])
        return ids[perm].tolist()
    raise ValueError("unknown order: %r" % order)


def ingest(nodes_by_id, anchors, disp, seq, tau):
    """Simulate ingestion. Returns (foundation: dict id->coord, admitted: set, schema_fits: dict,
    premature_reject: set of non-axiom rejected ids)."""
    foundation = {}
    admitted = set()
    schema_fits = {}
    premature_reject = set()
    for nid in seq:
        nd = nodes_by_id[nid]
        if nd["refs"] is None:
            # axiom / anchor-grounded: innate anchors always present -> schema_fit = 1
            sf = 1.0
            schema_fits[nid] = sf
            ests = []
            d = disp[nid]
            for j in range(anchors.shape[0]):
                ests.append(anchors[j] + d[("A", j)])
            foundation[nid] = np.mean(np.stack(ests, axis=0), axis=0)
            admitted.add(nid)
            continue
        refs = nd["refs"]
        present = [r for r in refs if r in admitted]
        sf = len(present) / float(len(refs))
        schema_fits[nid] = sf
        if sf >= tau and len(present) > 0:
            d = disp[nid]
            ests = [foundation[r] + d[r] for r in present]
            foundation[nid] = np.mean(np.stack(ests, axis=0), axis=0)
            admitted.add(nid)
        else:
            premature_reject.add(nid)
    return foundation, admitted, schema_fits, premature_reject


def eval_quality(nodes_by_id, foundation, admitted):
    """Held-out relational retrieval: for each (source, sibling-target) query where BOTH are admitted,
    predict target = foundation[source] + true displacement (noiseless query oracle), retrieve nearest
    admitted node. Accuracy over ALL queries (queries with a rejected endpoint count as FAIL, because
    the foundation cannot answer). Returns (quality, n_queries, mean_placement_error)."""
    adm_ids = sorted(admitted)
    if len(adm_ids) == 0:
        return 0.0, 0, float("nan")
    coords = np.stack([foundation[i] for i in adm_ids], axis=0)  # (A,k)
    id_to_row = {i: r for r, i in enumerate(adm_ids)}
    # build query set: (source, target) sibling pairs across ALL nodes (order-independent)
    queries = []
    for nid in sorted(nodes_by_id.keys()):
        for sib in nodes_by_id[nid]["siblings"]:
            queries.append((nid, sib))
    if not queries:
        return 0.0, 0, float("nan")
    correct = 0
    for (s, t) in queries:
        if s not in admitted or t not in admitted:
            continue  # FAIL (counted in denominator below)
        pred = foundation[s] + (nodes_by_id[t]["x_true"] - nodes_by_id[s]["x_true"])
        d2 = np.sum((coords - pred[None, :]) ** 2, axis=1)
        nn = adm_ids[int(np.argmin(d2))]
        if nn == t:
            correct += 1
    quality = correct / float(len(queries))
    # placement error over admitted nodes
    errs = [float(np.linalg.norm(foundation[i] - nodes_by_id[i]["x_true"])) for i in adm_ids]
    return quality, len(queries), float(np.mean(errs))


# ---------------------------------------------------------------------------
# Regime runner.
# ---------------------------------------------------------------------------

def run_regime(regime, cfg, seeds, tau):
    orders = ["curriculum", "arbitrary", "reverse"]
    acc = {o: {"admit_rate": [], "premature": [], "quality": [], "place_err": []} for o in orders}
    admit_sets = {o: [] for o in orders}  # for arms-must-differ (seed 0)
    for si, seed in enumerate(seeds):
        rng = np.random.default_rng(seed)
        if regime == "hierarchical":
            nodes, anchors = build_hierarchical_forest(
                rng, cfg["n_roots"], cfg["depth"], cfg["branching"], cfg["k"],
                cfg["sigma_delta"], cfg["n_anchors"], cfg["anchor_scale"], cfg["ref_levels"])
        else:
            nodes, anchors = build_flat_forest(
                rng, cfg["n_flat"], cfg["k"], cfg["sigma_delta"], cfg["n_anchors"], cfg["anchor_scale"])
        nodes_by_id = {nd["id"]: nd for nd in nodes}
        disp = make_observed_displacements(rng, nodes, anchors, cfg["sigma_d"])
        n_nonaxiom = sum(1 for nd in nodes if nd["refs"] is not None)
        for o in orders:
            oseq_rng = np.random.default_rng(seed * 1000 + 7)  # order-perm rng, seed-derived (deterministic)
            seq = order_indices(nodes, o, oseq_rng)
            foundation, admitted, sfits, premature = ingest(nodes_by_id, anchors, disp, seq, tau)
            n_admitted_nonaxiom = sum(1 for nid in admitted if nodes_by_id[nid]["refs"] is not None)
            admit_rate = len(admitted) / float(len(nodes))
            premature_rate = (len(premature) / float(n_nonaxiom)) if n_nonaxiom > 0 else 0.0
            quality, nq, place_err = eval_quality(nodes_by_id, foundation, admitted)
            acc[o]["admit_rate"].append(admit_rate)
            acc[o]["premature"].append(premature_rate)
            acc[o]["quality"].append(quality)
            acc[o]["place_err"].append(place_err)
            if si == 0:
                admit_sets[o].append(frozenset(sorted(admitted)))
    out = {}
    for o in orders:
        out[o] = {
            "admit_rate_mean": float(np.mean(acc[o]["admit_rate"])),
            "admit_rate_std": float(np.std(acc[o]["admit_rate"])),
            "premature_rejection_mean": float(np.mean(acc[o]["premature"])),
            "premature_rejection_std": float(np.std(acc[o]["premature"])),
            "foundation_quality_mean": float(np.mean(acc[o]["quality"])),
            "foundation_quality_std": float(np.std(acc[o]["quality"])),
            "mean_placement_error_mean": float(np.nanmean(acc[o]["place_err"])),
        }
    out["_admit_sets_seed0"] = {o: admit_sets[o][0] for o in orders}
    return out


def _regime_cfg(scale):
    if scale == "smoke":
        return {"n_roots": 2, "depth": 3, "branching": 2, "k": 24, "sigma_delta": 1.0,
                "sigma_d": 0.18, "n_anchors": 4, "anchor_scale": 6.0, "ref_levels": 3,
                "n_flat": 30}, [11, 23]
    # full
    return {"n_roots": 3, "depth": 5, "branching": 2, "k": 32, "sigma_delta": 1.0,
            "sigma_d": 0.18, "n_anchors": 4, "anchor_scale": 6.0, "ref_levels": 3,
            "n_flat": 189}, [11, 23, 37, 41, 53, 67, 71, 83]
    # (n_flat 189 matches hierarchical node count: 3 roots x (1+2+4+8+16+32) = 189)


# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------

TAU = 0.5  # FIXED gate: admit iff >= half of prerequisites present. Set ONCE, principled, not tuned.


def compute_verdict(hier, flat):
    cur_q = hier["curriculum"]["foundation_quality_mean"]
    rev_q = hier["reverse"]["foundation_quality_mean"]
    arb_q = hier["arbitrary"]["foundation_quality_mean"]
    cur_pr = hier["curriculum"]["premature_rejection_mean"]
    arb_pr = hier["arbitrary"]["premature_rejection_mean"]
    rev_pr = hier["reverse"]["premature_rejection_mean"]

    quality_gap = cur_q - rev_q
    rescue = arb_pr - cur_pr  # curriculum admits what arbitrary mis-rejects

    hier_spread = max(cur_q, arb_q, rev_q) - min(cur_q, arb_q, rev_q)
    flat_qs = [flat[o]["foundation_quality_mean"] for o in ("curriculum", "arbitrary", "reverse")]
    flat_spread = max(flat_qs) - min(flat_qs)
    flat_pr_max = max(flat[o]["premature_rejection_mean"] for o in ("curriculum", "arbitrary", "reverse"))

    # discriminator-fires gate
    discriminator_fired = (rev_pr >= 0.30)
    null_holds = (flat_spread <= 0.05) and (flat_pr_max <= 0.02)

    hard_pass = (quality_gap >= 0.25) and (rescue >= 0.20) and null_holds
    hard_fail = (hier_spread <= 0.05)

    if not discriminator_fired:
        verdict = "MIDDLE_BAND_DISCRIMINATOR_DID_NOT_FIRE"
    elif not null_holds:
        verdict = "BLOCK_NULL_GUARD_FAILED_SPURIOUS_ORDER_EFFECT"
    elif hard_pass:
        verdict = "HARD_PASS_ORDER_MATTERS_CURRICULUM_RESCUES_SCHEMA_FIT"
    elif hard_fail:
        verdict = "HARD_FAIL_ORDER_INVARIANT"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict,
        "quality_gap_curriculum_minus_reverse": quality_gap,
        "rescue_arbitrary_premature_minus_curriculum_premature": rescue,
        "hierarchical_quality_spread": hier_spread,
        "flat_quality_spread": flat_spread,
        "flat_premature_max": flat_pr_max,
        "discriminator_fired_reverse_premature_ge_0.30": bool(discriminator_fired),
        "null_holds": bool(null_holds),
    }


# ---------------------------------------------------------------------------
# Self-test.
# ---------------------------------------------------------------------------

def self_test():
    """Assert core invariants on a tiny config BEFORE trusting the full run."""
    cfg, seeds = _regime_cfg("smoke")
    hier = run_regime("hierarchical", cfg, seeds, TAU)
    flat = run_regime("flat", cfg, seeds, TAU)

    # 1. curriculum admits ~everything in hierarchical (all prereqs present in topo order)
    assert hier["curriculum"]["admit_rate_mean"] >= 0.98, \
        "curriculum admit_rate should be ~1.0, got %.3f" % hier["curriculum"]["admit_rate_mean"]
    # 2. reverse mis-rejects many true facts (scaffold-less deep facts)
    assert hier["reverse"]["premature_rejection_mean"] >= 0.30, \
        "reverse premature_rejection should fire, got %.3f" % hier["reverse"]["premature_rejection_mean"]
    # 3. curriculum quality > reverse quality (order matters in hierarchical)
    assert hier["curriculum"]["foundation_quality_mean"] > hier["reverse"]["foundation_quality_mean"] + 0.15, \
        "curriculum should beat reverse on quality"
    # 4. NULL guard: flat regime order-invariant (same gate, no prereqs -> no order effect)
    flat_qs = [flat[o]["foundation_quality_mean"] for o in ("curriculum", "arbitrary", "reverse")]
    assert (max(flat_qs) - min(flat_qs)) <= 0.05, \
        "flat regime must be order-invariant, spread=%.3f" % (max(flat_qs) - min(flat_qs))
    assert max(flat[o]["premature_rejection_mean"] for o in ("curriculum", "arbitrary", "reverse")) <= 0.02, \
        "flat premature_rejection must be ~0"
    # 5. ARMS-MUST-DIFFER: curriculum vs reverse admit sets differ in hierarchical (discriminator real)
    assert hier["_admit_sets_seed0"]["curriculum"] != hier["_admit_sets_seed0"]["reverse"], \
        "curriculum and reverse admit sets must differ (arms-must-differ)"
    # 6. FLAT arms admit-identical (all admit) -> quality equal is a REAL null not a bug
    assert flat["_admit_sets_seed0"]["curriculum"] == flat["_admit_sets_seed0"]["reverse"], \
        "flat regime all-admit -> admit sets identical across orders"
    print("[SELF-TEST] PASS")
    print("  hier curriculum quality=%.3f reverse quality=%.3f gap=%.3f" % (
        hier["curriculum"]["foundation_quality_mean"], hier["reverse"]["foundation_quality_mean"],
        hier["curriculum"]["foundation_quality_mean"] - hier["reverse"]["foundation_quality_mean"]))
    print("  hier reverse premature=%.3f arbitrary premature=%.3f" % (
        hier["reverse"]["premature_rejection_mean"], hier["arbitrary"]["premature_rejection_mean"]))
    print("  flat quality spread=%.4f" % (max(flat_qs) - min(flat_qs)))
    return True


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def _strip_sets(regime_out):
    return {k: v for k, v in regime_out.items() if k != "_admit_sets_seed0"}


def depth_sweep(base_cfg, seeds, depths):
    """Diagnostic: how order-sensitivity scales with prerequisite DEPTH. Cheap. Not part of verdict logic.

    Shows arbitrary order transitions from intermediate (shallow) to collapsed (deep) -> the order effect
    is a smooth function of the structural depth knob, not a binary artifact of one regime."""
    out = {}
    for d in depths:
        cfg = dict(base_cfg)
        cfg["depth"] = d
        h = run_regime("hierarchical", cfg, seeds, TAU)
        out["depth_%d" % d] = {
            "curriculum_quality": h["curriculum"]["foundation_quality_mean"],
            "arbitrary_quality": h["arbitrary"]["foundation_quality_mean"],
            "reverse_quality": h["reverse"]["foundation_quality_mean"],
            "arbitrary_premature": h["arbitrary"]["premature_rejection_mean"],
            "reverse_premature": h["reverse"]["premature_rejection_mean"],
        }
    return out


def main(scale="full", tau_sweep=False):
    t0 = datetime.now(timezone.utc)
    cfg, seeds = _regime_cfg(scale)
    hier = run_regime("hierarchical", cfg, seeds, TAU)
    flat = run_regime("flat", cfg, seeds, TAU)
    verdict = compute_verdict(hier, flat)
    dsweep = depth_sweep(cfg, seeds, [2, 3, 4, 5]) if scale == "full" else {}

    tau_robustness = {}
    if tau_sweep:
        for tv in (0.34, 0.5, 0.67):
            h = run_regime("hierarchical", cfg, seeds, tv)
            f = run_regime("flat", cfg, seeds, tv)
            tau_robustness["tau_%.2f" % tv] = {
                "quality_gap": h["curriculum"]["foundation_quality_mean"] - h["reverse"]["foundation_quality_mean"],
                "reverse_premature": h["reverse"]["premature_rejection_mean"],
                "arbitrary_premature": h["arbitrary"]["premature_rejection_mean"],
                "flat_spread": max(f[o]["foundation_quality_mean"] for o in ("curriculum", "arbitrary", "reverse"))
                - min(f[o]["foundation_quality_mean"] for o in ("curriculum", "arbitrary", "reverse")),
            }

    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict["verdict"],
        "verdict_msg": "%s | gap(curr-rev)=%.3f rescue=%.3f hier_spread=%.3f flat_spread=%.4f" % (
            verdict["verdict"], verdict["quality_gap_curriculum_minus_reverse"],
            verdict["rescue_arbitrary_premature_minus_curriculum_premature"],
            verdict["hierarchical_quality_spread"], verdict["flat_quality_spread"]),
        "summary": verdict["verdict"],
        "elapsed_s": elapsed,
        "ts_iso": t0.isoformat(),
        "scale": scale,
        "tau_fixed": TAU,
        "n_seeds": len(seeds),
        "config": cfg,
        "verdict_detail": verdict,
        "hierarchical": _strip_sets(hier),
        "flat": _strip_sets(flat),
        "tau_robustness": tau_robustness,
        "depth_sweep": dsweep,
    }
    out_dir = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH

    print("[VERDICT] %s" % verdict["verdict"])
    print("  HIERARCHICAL (positive control):")
    for o in ("curriculum", "arbitrary", "reverse"):
        r = hier[o]
        print("    %-11s quality=%.3f admit=%.3f premature=%.3f place_err=%.3f" % (
            o, r["foundation_quality_mean"], r["admit_rate_mean"],
            r["premature_rejection_mean"], r["mean_placement_error_mean"]))
    print("  FLAT (null guard):")
    for o in ("curriculum", "arbitrary", "reverse"):
        r = flat[o]
        print("    %-11s quality=%.3f admit=%.3f premature=%.3f" % (
            o, r["foundation_quality_mean"], r["admit_rate_mean"], r["premature_rejection_mean"]))
    print("  gap(curr-rev)=%.3f rescue=%.3f hier_spread=%.3f flat_spread=%.4f" % (
        verdict["quality_gap_curriculum_minus_reverse"],
        verdict["rescue_arbitrary_premature_minus_curriculum_premature"],
        verdict["hierarchical_quality_spread"], verdict["flat_quality_spread"]))
    if tau_robustness:
        print("  TAU-ROBUSTNESS:")
        for kk, vv in tau_robustness.items():
            print("    %s gap=%.3f rev_prem=%.3f flat_spread=%.4f" % (
                kk, vv["quality_gap"], vv["reverse_premature"], vv["flat_spread"]))
    if dsweep:
        print("  DEPTH-SWEEP (order-sensitivity vs prerequisite depth):")
        for kk, vv in dsweep.items():
            print("    %s curr_q=%.3f arb_q=%.3f rev_q=%.3f | arb_prem=%.3f" % (
                kk, vv["curriculum_quality"], vv["arbitrary_quality"],
                vv["reverse_quality"], vv["arbitrary_premature"]))
    print("  metrics -> %s" % final)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--tau-sweep", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(scale="smoke" if args.smoke else "full", tau_sweep=args.tau_sweep)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        sys.stderr.write("[CELL_CRASHED] %s: %s\n%s\n" % (type(e).__name__, e, traceback.format_exc()))
        raise
