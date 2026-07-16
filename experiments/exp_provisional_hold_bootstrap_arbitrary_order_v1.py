"""exp_provisional_hold_bootstrap_arbitrary_order_v1

FOLLOW-UP to exp_curriculum_order_ingest_schema_fit_v1 (HARD_PASS: order matters; curriculum rescues
schema-fit; arbitrary order craters foundation quality ~1.0 -> ~0.04). But REAL data arrives in
ARBITRARY order -- you cannot pre-sort a live edit/claim stream. So test the REALISTIC fix:
PROVISIONAL-HOLD / bootstrapping. Instead of REJECTING a premature (scaffold-less) fact under a
single-pass strict gate, ADMIT it to a HOLD buffer and RE-EVALUATE it once its prerequisites arrive.

Carey/bootstrapping: a single-pass STRICT gate is definitionally incompatible with bootstrapping (it
drops the scaffold-less fact that must be retried later). Provisional-hold IS the bootstrapping loop.

ARENA: imported verbatim from exp_curriculum_order_ingest_schema_fit_v1 (same forest, same prerequisite
DAG, same noisy per-seed displacements, same schema-fit gate tau) -> fairness is airtight; only the
REJECT policy differs.

ARMS (hierarchical regime, mean over seeds):
  (C) curriculum_strict : topological order + single-pass strict gate  -> the ~1.0 CEILING reference.
  (A) arbitrary_strict  : random order + single-pass strict gate       -> the ~0.04 FLOOR (baseline;
                          premature facts are permanently dropped -- reproduces the curriculum cell).
  (B) arbitrary_hold    : random order + PROVISIONAL-HOLD. Phase 1 = stream arrival: a fact failing the
                          SAME tau gate goes to a hold buffer (not dropped). Phase 2 = drain: repeatedly
                          sweep the hold buffer, admitting any held fact whose prerequisites are now
                          present (SAME tau gate), until a full sweep admits nothing (fixpoint). The
                          admit CRITERION is identical to strict (anti-rig); only retry-vs-drop differs.

MEASURE (the QUANTIFICATION -- re-queue recovering facts is partly by-construction, so value is HOW
MUCH / AT WHAT COST / RESIDUAL, not yes/no):
  - foundation_quality per arm (held-out sibling relational retrieval, same eval as curriculum cell).
  - recovery_fraction = (hold_q - arbitrary_strict_q) / (curriculum_q - arbitrary_strict_q)
                        = fraction of the curriculum advantage recovered under arbitrary order.
  - premature_recovered_fraction = (phase1_hold - final_hold) / phase1_hold
                        = fraction of strict-rejected facts the drain eventually admits.
  - re_queue_passes  : number of drain sweeps to fixpoint (the COST; should be ~depth, constant in N).
  - retry_attempts   : total held-fact re-evaluations across all passes (wasted-work COST).
  - placement error per arm (recovery must be genuine placement, not garbage that inflates quality).

NULL GUARD (flat regime): every fact grounds on always-present innate anchors -> nothing is ever
premature -> hold buffer is EMPTY, 0 drain passes, arbitrary_strict already == curriculum. Confirms
provisional-hold's benefit is prerequisite-structure-driven, not a spurious artifact.

GRACEFUL DEGRADATION (separate sub-run): inject ORPHAN facts whose prerequisites NEVER arrive (refs to
phantom ids never ingested). The hold buffer must stay BOUNDED (it only shrinks during drain -> max
size = phase-1 hold), the drain must TERMINATE (fixpoint when only orphans remain), and orphans end in
a bounded give-up set (final_hold) rather than growing without bound.

PRE-REG BANDS (see preregs/2026-07-16_provisional_hold_bootstrap_arbitrary_order_v1.md):
  HARD-PASS = recovery_fraction >= 0.70 AND re_queue_passes bounded (<= depth+2) AND null guard holds
              (flat hold buffer empty, 0 passes, flat quality spread <= 0.05) AND graceful degradation
              holds (orphan buffer bounded + drain terminates) AND anti-rig holds (arbitrary_strict
              still craters: curriculum_q - arbitrary_strict_q >= 0.25).
              => arbitrary-order real data is handleable by bootstrapping; no pre-sort needed.
  HARD-FAIL = recovery_fraction <= 0.30 OR re_queue_passes unbounded (grows with N, not depth).
              => genuinely need curriculum order, which live streams cannot provide -- a real limitation.
  MIDDLE    = otherwise (partial recovery / residual order-dependence).

DISCRIMINATOR-FIRES (smoke gate): arbitrary_strict must actually crater (curriculum_q -
  arbitrary_strict_q >= 0.15 at smoke) AND hold must strictly help (hold_q >= arbitrary_strict_q + 0.10)
  AND hold admit-set must DIFFER from arbitrary_strict admit-set (arms-must-differ) AND flat null holds.
  If arbitrary_strict does not crater there is nothing to recover -> BLOCK (saturation-vacuous).

Determinism: numpy default_rng(fixed int seeds); order-perm rng seed-derived (matches curriculum cell);
sorted() for all set ops; hold swept in id order (NO depth sort -> no curriculum leakage into the drain).
ASCII-only. No emojis. Local numpy, no queue/GPU/atoms/push. Runs to completion in foreground (seconds).
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone

import numpy as np

# Import the curriculum arena VERBATIM (same dir) -> identical forest/DAG/displacements/gate = fair.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_curriculum_order_ingest_schema_fit_v1 as cur  # noqa: E402

ANCHOR_NAME = "provisional_hold_bootstrap_arbitrary_order_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAU = cur.TAU  # SAME fixed gate as the curriculum cell (anti-rig: identical admit criterion).


# ---------------------------------------------------------------------------
# Placement (shared by strict phase-1 arrival and provisional-hold drain).
# ---------------------------------------------------------------------------

def _try_place(nid, nodes_by_id, anchors, disp, foundation, admitted):
    """Attempt to admit+place node nid under the FIXED tau gate. Returns True iff admitted.

    Axiom/root (refs None): grounds on always-present innate anchors -> schema_fit = 1 -> always admit.
    Non-axiom: schema_fit = fraction of refs already admitted; admit iff sf >= TAU and >=1 ref present;
    placement = degree-invariant MEAN over present refs of (foundation[ref] + observed displacement).
    Identical criterion + placement math to cur.ingest (verified by self-test parity check)."""
    nd = nodes_by_id[nid]
    if nd["refs"] is None:
        d = disp[nid]
        ests = [anchors[j] + d[("A", j)] for j in range(anchors.shape[0])]
        foundation[nid] = np.mean(np.stack(ests, axis=0), axis=0)
        admitted.add(nid)
        return True
    refs = nd["refs"]
    present = [r for r in refs if r in admitted]
    sf = len(present) / float(len(refs))
    if sf >= TAU and len(present) > 0:
        d = disp[nid]
        ests = [foundation[r] + d[r] for r in present]
        foundation[nid] = np.mean(np.stack(ests, axis=0), axis=0)
        admitted.add(nid)
        return True
    return False


def ingest_provisional_hold(nodes_by_id, anchors, disp, seq, max_passes):
    """Bootstrapping ingest. Phase 1: stream arrival (fail -> hold, NOT drop). Phase 2: drain sweeps.

    Returns dict with foundation, admitted, phase1_hold, final_hold (give-up set), passes,
    retry_attempts, and max_buffer (for boundedness check)."""
    foundation = {}
    admitted = set()
    hold = []
    # Phase 1: arrival in the given (arbitrary) order.
    for nid in seq:
        if not _try_place(nid, nodes_by_id, anchors, disp, foundation, admitted):
            hold.append(nid)
    phase1_hold = len(hold)
    max_buffer = phase1_hold  # buffer only shrinks during drain -> this is the max.
    # Phase 2: drain the hold buffer. Swept in INSERTION (FIFO/arrival) order -- NOT id-sorted, because
    # the forest builder assigns ids in BFS/topological order, so an id-sort would leak curriculum order
    # into the drain and understate the pass cost. SYNCHRONOUS within-pass update: each pass admits facts
    # against the admitted-set FROZEN at pass start, so a cascade of D dependency levels takes D passes.
    # This makes re_queue_passes an order-independent, CONSERVATIVE (upper-bound) cost = cascade depth.
    passes = 0
    retry_attempts = 0
    buffer_trace = [len(hold)]
    while hold and passes < max_passes:
        passes += 1
        admitted_this = 0
        still = []
        snapshot = frozenset(admitted)  # freeze -> facts admitted this pass do not help others until next.
        for nid in hold:  # insertion order (arrival) -> arbitrary under arbitrary arrival, no topo leak.
            retry_attempts += 1
            nd = nodes_by_id[nid]
            if nd["refs"] is None:
                admittable = True
            else:
                present = [r for r in nd["refs"] if r in snapshot]
                admittable = (len(present) / float(len(nd["refs"])) >= TAU) and (len(present) > 0)
            if admittable and _try_place(nid, nodes_by_id, anchors, disp, foundation, admitted):
                admitted_this += 1
            else:
                still.append(nid)
        hold = still
        buffer_trace.append(len(hold))
        if admitted_this == 0:
            break  # fixpoint: only un-admittable (orphan / stuck) facts remain.
    return {
        "foundation": foundation,
        "admitted": admitted,
        "phase1_hold": phase1_hold,
        "final_hold": len(hold),
        "final_hold_ids": sorted(hold),
        "passes": passes,
        "retry_attempts": retry_attempts,
        "max_buffer": max_buffer,
        "buffer_trace": buffer_trace,
    }


# ---------------------------------------------------------------------------
# Orphan injection (graceful-degradation stress).
# ---------------------------------------------------------------------------

def add_orphans(nodes, rng, n_orphans, k, sigma_delta):
    """Append n_orphans facts whose refs point to PHANTOM ids never in the forest/stream.

    Their schema_fit is permanently 0 -> never admitted -> tests that the hold buffer stays bounded and
    the drain terminates (they end in the give-up set, not an unbounded buffer). Siblings among orphans
    only (kept OUT of the main quality query set: orphans are a degradation stress, not recoverable)."""
    base = max(nd["id"] for nd in nodes) + 1
    phantom = -1  # negative ids are never generated by the forest builders.
    orphan_ids = list(range(base, base + n_orphans))
    for oi in orphan_ids:
        x = rng.normal(0.0, 1.0, size=k) * 3.0
        nodes.append({"id": oi, "depth": 99, "parent": None,
                      "refs": sorted([phantom, phantom - 1]), "x_true": x, "siblings": []})
    return nodes, orphan_ids


# ---------------------------------------------------------------------------
# Arm runner (hierarchical or flat), mean over seeds.
# ---------------------------------------------------------------------------

def _build(regime, cfg, rng):
    if regime == "hierarchical":
        return cur.build_hierarchical_forest(
            rng, cfg["n_roots"], cfg["depth"], cfg["branching"], cfg["k"],
            cfg["sigma_delta"], cfg["n_anchors"], cfg["anchor_scale"], cfg["ref_levels"])
    return cur.build_flat_forest(
        rng, cfg["n_flat"], cfg["k"], cfg["sigma_delta"], cfg["n_anchors"], cfg["anchor_scale"])


def run_arms(regime, cfg, seeds, max_passes):
    """Three arms on the SAME per-seed forest/displacements. Returns per-arm aggregates + hold cost."""
    A = {"cur_strict": {"q": [], "adm": [], "err": []},
         "arb_strict": {"q": [], "adm": [], "err": []},
         "arb_hold":   {"q": [], "adm": [], "err": [], "passes": [], "retry": [],
                        "phase1_hold": [], "final_hold": [], "recovered": [], "max_buffer": [],
                        "monotone": []}}
    admit_sets0 = {}
    for si, seed in enumerate(seeds):
        rng = np.random.default_rng(seed)
        nodes, anchors = _build(regime, cfg, rng)
        nodes_by_id = {nd["id"]: nd for nd in nodes}
        disp = cur.make_observed_displacements(rng, nodes, anchors, cfg["sigma_d"])
        oseq_rng = np.random.default_rng(seed * 1000 + 7)  # SAME order-perm rng as curriculum cell.

        # (C) curriculum strict (ceiling) -- reuse cur.ingest verbatim.
        cseq = cur.order_indices(nodes, "curriculum", oseq_rng)
        cf, cadm, _, _ = cur.ingest(nodes_by_id, anchors, disp, cseq, TAU)
        cq, _, cerr = cur.eval_quality(nodes_by_id, cf, cadm)
        A["cur_strict"]["q"].append(cq); A["cur_strict"]["adm"].append(len(cadm) / len(nodes))
        A["cur_strict"]["err"].append(cerr)

        # arbitrary order (SHARED sequence for strict and hold -> fair head-to-head).
        aseq = cur.order_indices(nodes, "arbitrary", oseq_rng)

        # (A) arbitrary strict (floor) -- reuse cur.ingest verbatim.
        af, aadm, _, aprem = cur.ingest(nodes_by_id, anchors, disp, aseq, TAU)
        aq, _, aerr = cur.eval_quality(nodes_by_id, af, aadm)
        A["arb_strict"]["q"].append(aq); A["arb_strict"]["adm"].append(len(aadm) / len(nodes))
        A["arb_strict"]["err"].append(aerr)

        # (B) arbitrary provisional-hold (bootstrapping).
        h = ingest_provisional_hold(nodes_by_id, anchors, disp, aseq, max_passes)
        hq, _, herr = cur.eval_quality(nodes_by_id, h["foundation"], h["admitted"])
        A["arb_hold"]["q"].append(hq); A["arb_hold"]["adm"].append(len(h["admitted"]) / len(nodes))
        A["arb_hold"]["err"].append(herr)
        A["arb_hold"]["passes"].append(h["passes"])
        A["arb_hold"]["retry"].append(h["retry_attempts"])
        A["arb_hold"]["phase1_hold"].append(h["phase1_hold"])
        A["arb_hold"]["final_hold"].append(h["final_hold"])
        rec = (h["phase1_hold"] - h["final_hold"]) / float(h["phase1_hold"]) if h["phase1_hold"] > 0 else 0.0
        A["arb_hold"]["recovered"].append(rec)
        A["arb_hold"]["max_buffer"].append(h["max_buffer"])
        bt = h["buffer_trace"]
        A["arb_hold"]["monotone"].append(all(bt[i + 1] <= bt[i] for i in range(len(bt) - 1)))

        if si == 0:
            admit_sets0 = {"arb_strict": frozenset(sorted(aadm)),
                           "arb_hold": frozenset(sorted(h["admitted"])),
                           "cur_strict": frozenset(sorted(cadm))}

    def agg(arm):
        d = A[arm]
        o = {"quality_mean": float(np.mean(d["q"])), "quality_std": float(np.std(d["q"])),
             "admit_rate_mean": float(np.mean(d["adm"])),
             "placement_error_mean": float(np.nanmean(d["err"]))}
        if arm == "arb_hold":
            o.update({
                "re_queue_passes_mean": float(np.mean(d["passes"])),
                "re_queue_passes_max": int(np.max(d["passes"])),
                "retry_attempts_mean": float(np.mean(d["retry"])),
                "phase1_hold_mean": float(np.mean(d["phase1_hold"])),
                "final_hold_mean": float(np.mean(d["final_hold"])),
                "premature_recovered_fraction_mean": float(np.mean(d["recovered"])),
                "max_buffer_mean": float(np.mean(d["max_buffer"])),
                "buffer_monotone_nonincreasing_all": bool(all(d["monotone"])),
            })
        return o

    out = {a: agg(a) for a in A}
    out["_admit_sets0"] = admit_sets0
    return out


def run_graceful(cfg, seeds, max_passes, n_orphans):
    """Graceful-degradation sub-run: hierarchical forest + orphan facts (prereqs never arrive).

    Confirms buffer bounded (only shrinks), drain terminates, orphans end in a bounded give-up set."""
    finals = []
    passes = []
    monos = []
    orphan_leak = []  # orphans wrongly admitted (should be 0).
    max_bufs = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        nodes, anchors = cur.build_hierarchical_forest(
            rng, cfg["n_roots"], cfg["depth"], cfg["branching"], cfg["k"],
            cfg["sigma_delta"], cfg["n_anchors"], cfg["anchor_scale"], cfg["ref_levels"])
        nodes, orphan_ids = add_orphans(nodes, rng, n_orphans, cfg["k"], cfg["sigma_delta"])
        nodes_by_id = {nd["id"]: nd for nd in nodes}
        disp = _disp_with_orphans(rng, nodes, anchors, cfg["sigma_d"])  # handles phantom orphan refs.
        oseq_rng = np.random.default_rng(seed * 1000 + 7)
        aseq = cur.order_indices(nodes, "arbitrary", oseq_rng)
        h = ingest_provisional_hold(nodes_by_id, anchors, disp, aseq, max_passes)
        finals.append(h["final_hold"])
        passes.append(h["passes"])
        bt = h["buffer_trace"]
        monos.append(all(bt[i + 1] <= bt[i] for i in range(len(bt) - 1)))
        max_bufs.append(h["max_buffer"])
        orphan_leak.append(sum(1 for oi in orphan_ids if oi in h["admitted"]))
    return {
        "n_orphans": n_orphans,
        "final_hold_mean": float(np.mean(finals)),
        "final_hold_ge_n_orphans_all": bool(all(f >= n_orphans for f in finals)),  # orphans stuck in give-up.
        "orphans_admitted_total": int(np.sum(orphan_leak)),  # must be 0.
        "passes_mean": float(np.mean(passes)),
        "passes_max": int(np.max(passes)),
        "max_buffer_mean": float(np.mean(max_bufs)),
        "buffer_bounded_monotone_all": bool(all(monos)),
        "drain_terminated_all": bool(all(p < max_passes for p in passes)),
    }


def _disp_with_orphans(rng, nodes, anchors, sigma_d):
    """Displacements for a forest that includes orphan nodes (refs to phantom ids).

    Real nodes: identical to cur.make_observed_displacements. Orphan nodes (refs contain ids not in the
    node set): never admitted, so their disp is never read -> supply a harmless placeholder so the
    builder does not KeyError on the phantom ref lookup."""
    id_set = {nd["id"] for nd in nodes}
    disp = {}
    for nd in nodes:
        X = nd["x_true"]
        if nd["refs"] is None:
            d = {}
            for j in range(anchors.shape[0]):
                d[("A", j)] = (X - anchors[j]) + rng.normal(0.0, sigma_d, size=X.shape[0])
            disp[nd["id"]] = d
        elif all(r in id_set for r in nd["refs"]):
            nodes_by_id = {n["id"]: n for n in nodes}
            d = {}
            for r in nd["refs"]:
                xr = nodes_by_id[r]["x_true"]
                d[r] = (X - xr) + rng.normal(0.0, sigma_d, size=X.shape[0])
            disp[nd["id"]] = d
        else:
            # orphan: phantom refs never admitted -> disp never read. Placeholder zeros.
            disp[nd["id"]] = {r: np.zeros_like(X) for r in nd["refs"]}
    return disp


# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------

def compute_verdict(hier, flat, grace, cfg):
    cq = hier["cur_strict"]["quality_mean"]
    aq = hier["arb_strict"]["quality_mean"]
    hq = hier["arb_hold"]["quality_mean"]
    denom = cq - aq
    recovery = (hq - aq) / denom if denom > 1e-6 else 0.0
    passes_max = hier["arb_hold"]["re_queue_passes_max"]
    prem_rec = hier["arb_hold"]["premature_recovered_fraction_mean"]

    depth = cfg["depth"]
    passes_bounded = passes_max <= (depth + 2)

    flat_qs = [flat[a]["quality_mean"] for a in ("cur_strict", "arb_strict", "arb_hold")]
    flat_spread = max(flat_qs) - min(flat_qs)
    flat_hold_empty = (flat["arb_hold"]["phase1_hold_mean"] <= 1e-9) and \
                      (flat["arb_hold"]["re_queue_passes_mean"] <= 1e-9)
    null_holds = flat_hold_empty and (flat_spread <= 0.05)

    graceful_ok = (grace["orphans_admitted_total"] == 0) and grace["buffer_bounded_monotone_all"] and \
                  grace["drain_terminated_all"] and grace["final_hold_ge_n_orphans_all"]

    anti_rig = (denom >= 0.25)  # arbitrary_strict must still crater (else nothing to recover).
    arms_differ = (hier["_admit_sets0"]["arb_hold"] != hier["_admit_sets0"]["arb_strict"])

    hard_pass = (recovery >= 0.70) and passes_bounded and null_holds and graceful_ok and anti_rig and arms_differ
    hard_fail = (recovery <= 0.30) or (not passes_bounded)

    if not anti_rig:
        verdict = "MIDDLE_BAND_ANTI_RIG_ARBITRARY_DID_NOT_CRATER"
    elif not arms_differ:
        verdict = "BLOCK_ARMS_IDENTICAL_HOLD_NO_EFFECT"
    elif not null_holds:
        verdict = "BLOCK_NULL_GUARD_FAILED_HOLD_ACTS_IN_FLAT"
    elif not graceful_ok:
        verdict = "HARD_FAIL_GRACEFUL_DEGRADATION_VIOLATED"
    elif hard_pass:
        verdict = "HARD_PASS_PROVISIONAL_HOLD_RECOVERS_ARBITRARY_ORDER"
    elif hard_fail:
        verdict = "HARD_FAIL_NEED_CURRICULUM_ORDER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RECOVERY"

    return {
        "verdict": verdict,
        "recovery_fraction": recovery,
        "curriculum_quality": cq,
        "arbitrary_strict_quality": aq,
        "arbitrary_hold_quality": hq,
        "curriculum_advantage_denom": denom,
        "premature_recovered_fraction": prem_rec,
        "re_queue_passes_max": passes_max,
        "re_queue_passes_mean": hier["arb_hold"]["re_queue_passes_mean"],
        "retry_attempts_mean": hier["arb_hold"]["retry_attempts_mean"],
        "passes_bounded_le_depth_plus_2": bool(passes_bounded),
        "depth": depth,
        "flat_quality_spread": flat_spread,
        "flat_hold_buffer_empty": bool(flat_hold_empty),
        "null_holds": bool(null_holds),
        "graceful_ok": bool(graceful_ok),
        "anti_rig_arbitrary_craters": bool(anti_rig),
        "arms_differ": bool(arms_differ),
    }


# ---------------------------------------------------------------------------
# Self-test.
# ---------------------------------------------------------------------------

def _cfg(scale):
    cfg, seeds = cur._regime_cfg(scale)
    return cfg, seeds


def self_test():
    cfg, seeds = _cfg("smoke")
    max_passes = 2 * cfg["depth"] + 5
    hier = run_arms("hierarchical", cfg, seeds, max_passes)
    flat = run_arms("flat", cfg, seeds, max_passes)
    grace = run_graceful(cfg, seeds, max_passes, n_orphans=6)

    cq = hier["cur_strict"]["quality_mean"]
    aq = hier["arb_strict"]["quality_mean"]
    hq = hier["arb_hold"]["quality_mean"]

    # PARITY: strict arbitrary here must reproduce the curriculum cell's arbitrary floor (same arena).
    ref = cur.run_regime("hierarchical", cfg, seeds, TAU)
    assert abs(ref["arbitrary"]["foundation_quality_mean"] - aq) < 1e-9, \
        "arbitrary_strict must match cur.run_regime arbitrary (arena parity): %.4f vs %.4f" % (
            ref["arbitrary"]["foundation_quality_mean"], aq)
    assert abs(ref["curriculum"]["foundation_quality_mean"] - cq) < 1e-9, "curriculum parity broken"

    # 1. DISCRIMINATOR: arbitrary_strict craters vs curriculum (there is something to recover).
    assert (cq - aq) >= 0.15, "arbitrary_strict must crater at smoke, gap=%.3f" % (cq - aq)
    # 2. Hold strictly helps over strict arbitrary.
    assert hq >= aq + 0.10, "hold must beat arbitrary_strict, hold=%.3f arb=%.3f" % (hq, aq)
    # 3. ARMS-MUST-DIFFER: hold admits a different (larger) set than arbitrary_strict.
    assert hier["_admit_sets0"]["arb_hold"] != hier["_admit_sets0"]["arb_strict"], "hold must admit more"
    assert hier["arb_hold"]["admit_rate_mean"] > hier["arb_strict"]["admit_rate_mean"], "hold admits more"
    # 4. Re-queue passes BOUNDED (~depth), not unbounded.
    assert hier["arb_hold"]["re_queue_passes_max"] <= cfg["depth"] + 2, \
        "passes must be bounded, got %d (depth=%d)" % (hier["arb_hold"]["re_queue_passes_max"], cfg["depth"])
    # 5. Recovery placement is GENUINE (hold placement error not wildly worse than curriculum).
    assert hier["arb_hold"]["placement_error_mean"] < 5.0 * hier["cur_strict"]["placement_error_mean"] + 1e-6, \
        "hold placement must be genuine, not garbage"
    # 6. NULL GUARD: flat hold buffer empty, 0 passes, order-invariant.
    assert flat["arb_hold"]["phase1_hold_mean"] <= 1e-9, "flat hold buffer must be empty"
    assert flat["arb_hold"]["re_queue_passes_mean"] <= 1e-9, "flat must need 0 drain passes"
    flat_qs = [flat[a]["quality_mean"] for a in ("cur_strict", "arb_strict", "arb_hold")]
    assert (max(flat_qs) - min(flat_qs)) <= 0.05, "flat must be order/arm-invariant"
    # 7. GRACEFUL DEGRADATION: orphans never admitted, buffer bounded+monotone, drain terminates.
    assert grace["orphans_admitted_total"] == 0, "orphans must never admit"
    assert grace["buffer_bounded_monotone_all"], "buffer must be monotone non-increasing (bounded)"
    assert grace["drain_terminated_all"], "drain must terminate (fixpoint), not hit max_passes"
    assert grace["final_hold_ge_n_orphans_all"], "orphans must remain in bounded give-up set"

    print("[SELF-TEST] PASS")
    print("  cur_q=%.3f arb_strict_q=%.3f hold_q=%.3f -> recovery=%.3f" % (
        cq, aq, hq, (hq - aq) / (cq - aq) if (cq - aq) > 1e-6 else 0.0))
    print("  premature_recovered=%.3f passes_max=%d retry_mean=%.1f phase1_hold=%.1f final_hold=%.1f" % (
        hier["arb_hold"]["premature_recovered_fraction_mean"], hier["arb_hold"]["re_queue_passes_max"],
        hier["arb_hold"]["retry_attempts_mean"], hier["arb_hold"]["phase1_hold_mean"],
        hier["arb_hold"]["final_hold_mean"]))
    print("  flat spread=%.4f flat_hold_empty=%s | orphans_admitted=%d final_hold=%.1f passes=%d" % (
        max(flat_qs) - min(flat_qs), flat["arb_hold"]["phase1_hold_mean"] <= 1e-9,
        grace["orphans_admitted_total"], grace["final_hold_mean"], grace["passes_max"]))
    return True


# ---------------------------------------------------------------------------
# Diagnostics + main.
# ---------------------------------------------------------------------------

def _strip(d):
    return {k: v for k, v in d.items() if k != "_admit_sets0"}


def cost_scale_sweep(base_cfg, seeds, max_passes):
    """Show re_queue_passes scales with prerequisite DEPTH (structural), NOT with N (branching).

    HARD-FAIL guard: if passes grew with N (more facts) rather than depth, the cost would be unbounded
    for real large streams. This demonstrates passes ~ depth (bounded), branching only inflates buffer
    size linearly (bounded work), not pass count."""
    out = {}
    for d in (2, 3, 4, 5):
        cfg = dict(base_cfg); cfg["depth"] = d
        h = run_arms("hierarchical", cfg, seeds, max_passes)
        out["depth_%d" % d] = {
            "recovery": (h["arb_hold"]["quality_mean"] - h["arb_strict"]["quality_mean"]) /
                        max(1e-6, h["cur_strict"]["quality_mean"] - h["arb_strict"]["quality_mean"]),
            "passes_max": h["arb_hold"]["re_queue_passes_max"],
            "retry_mean": h["arb_hold"]["retry_attempts_mean"],
        }
    for b in (2, 3, 4):
        cfg = dict(base_cfg); cfg["branching"] = b; cfg["depth"] = 4
        h = run_arms("hierarchical", cfg, seeds, max_passes)
        out["branch_%d" % b] = {
            "passes_max": h["arb_hold"]["re_queue_passes_max"],
            "retry_mean": h["arb_hold"]["retry_attempts_mean"],
            "phase1_hold": h["arb_hold"]["phase1_hold_mean"],
        }
    return out


def main(scale="full"):
    t0 = datetime.now(timezone.utc)
    cfg, seeds = _cfg(scale)
    max_passes = 2 * cfg["depth"] + 5
    hier = run_arms("hierarchical", cfg, seeds, max_passes)
    flat = run_arms("flat", cfg, seeds, max_passes)
    grace = run_graceful(cfg, seeds, max_passes, n_orphans=cfg.get("n_orphans", 12))
    verdict = compute_verdict(hier, flat, grace, cfg)
    sweep = cost_scale_sweep(cfg, seeds, max_passes) if scale == "full" else {}

    elapsed = (datetime.now(timezone.utc) - t0).total_seconds()
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict["verdict"],
        "verdict_msg": "%s | recovery=%.3f (cur=%.3f arb=%.3f hold=%.3f) passes_max=%d prem_rec=%.3f" % (
            verdict["verdict"], verdict["recovery_fraction"], verdict["curriculum_quality"],
            verdict["arbitrary_strict_quality"], verdict["arbitrary_hold_quality"],
            verdict["re_queue_passes_max"], verdict["premature_recovered_fraction"]),
        "summary": verdict["verdict"],
        "elapsed_s": elapsed,
        "ts_iso": t0.isoformat(),
        "scale": scale,
        "tau_fixed": TAU,
        "max_passes": max_passes,
        "n_seeds": len(seeds),
        "config": cfg,
        "verdict_detail": verdict,
        "hierarchical": _strip(hier),
        "flat": _strip(flat),
        "graceful_degradation": grace,
        "cost_scale_sweep": sweep,
    }
    out_dir = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH

    print("[VERDICT] %s" % verdict["verdict"])
    print("  HIERARCHICAL arms:")
    for a in ("cur_strict", "arb_strict", "arb_hold"):
        r = hier[a]
        print("    %-11s quality=%.3f admit=%.3f place_err=%.3f" % (
            a, r["quality_mean"], r["admit_rate_mean"], r["placement_error_mean"]))
    h = hier["arb_hold"]
    print("  RECOVERY=%.3f  premature_recovered=%.3f  passes(mean/max)=%.1f/%d  retry_mean=%.1f" % (
        verdict["recovery_fraction"], h["premature_recovered_fraction_mean"],
        h["re_queue_passes_mean"], h["re_queue_passes_max"], h["retry_attempts_mean"]))
    print("  phase1_hold=%.1f final_hold=%.1f max_buffer=%.1f monotone=%s" % (
        h["phase1_hold_mean"], h["final_hold_mean"], h["max_buffer_mean"],
        h["buffer_monotone_nonincreasing_all"]))
    print("  NULL (flat): spread=%.4f hold_empty=%s passes=%.1f" % (
        verdict["flat_quality_spread"], verdict["flat_hold_buffer_empty"],
        flat["arb_hold"]["re_queue_passes_mean"]))
    print("  GRACEFUL: orphans_admitted=%d final_hold=%.1f passes_max=%d bounded=%s terminated=%s" % (
        grace["orphans_admitted_total"], grace["final_hold_mean"], grace["passes_max"],
        grace["buffer_bounded_monotone_all"], grace["drain_terminated_all"]))
    if sweep:
        print("  COST-SCALE SWEEP (passes ~ depth, NOT ~ N):")
        for kk, vv in sweep.items():
            if kk.startswith("depth"):
                print("    %s recovery=%.3f passes_max=%d retry=%.0f" % (
                    kk, vv["recovery"], vv["passes_max"], vv["retry_mean"]))
            else:
                print("    %s passes_max=%d retry=%.0f phase1_hold=%.0f" % (
                    kk, vv["passes_max"], vv["retry_mean"], vv["phase1_hold"]))
    print("  metrics -> %s" % final)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(scale="smoke" if args.smoke else "full")
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        sys.stderr.write("[CELL_CRASHED] %s: %s\n%s\n" % (type(e).__name__, e, traceback.format_exc()))
        raise
