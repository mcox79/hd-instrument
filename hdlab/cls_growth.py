"""hdlab/cls_growth.py -- the CLS keep-both-stores SAFE-GROWTH primitive (the reversibility heart of the
learner's safe-growth switch). PROMOTED 2026-08-31 (Q111) from the integrated North-Star capstone
`turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation` (EXCELLENT). NO external LLM.

WHAT THIS IS (and is NOT). The capstone PROVED that learning word-meaning by reading turns ON safe AND
beneficial when growth uses a Complementary Learning Systems (McClelland/O'Reilly 1995) KEEP-BOTH-STORES
ensemble -- the OLD store is NEVER overwritten; the new (grown) store is fused ALONGSIDE it -- gated by a
regression-checked ROLLBACK on a held-out known-correct probe. This module promotes exactly that
SAFETY PRIMITIVE (verbatim from the validated cells), so any growth loop is REVERSIBLE by construction:

  * `make_ensemble_sim` -- the keep-both fusion: z-score each channel (old-store sim, new-store sim) and
    combine, NEVER discarding a defined channel (that discard IS the naive-overwrite failure the switch
    exists to avoid). Turning growth "on" = read through the fused sim instead of the base sim; "off" =
    read through the base sim only (byte-identical). Reversible: the base channel is always retained.
  * `rollback_gate` -- accept a candidate grown update ONLY if it does not corrupt a frozen probe of
    known-correct items; else roll back to the prior store. A random-decision control fails to protect,
    which is how we know the gate's protection is real.

THE ANTI-DRIFT ANCHOR (added 2026-08-31, Q111, from the integrated live-canary problem
`run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite`, owner-DONE): `align_and_fuse`
is the SLOW-ANCHOR consolidation step -- keep-both-stores fused in ONE coordinate frame (Procrustes-rotate
the grown store onto the anchor's frame, L2-normalise, convex-combine per word `fused = (1-eta)*anchor +
eta*grown`). Iterated per reading round it IS the continual EMA slow anchor: eta=0 FROZEN (infinite inertia),
small eta = the brain-faithful slowly-consolidated neocortical store (Kumaran 2016 / mean-teacher; the
canary's primary safe+beneficial arm on held-out modern text), eta=0.5 DECAY (the can-fail control that
drifts). `alpha` here IS the consolidation rate eta. This is a COMPUTATIONAL-LEVEL SUBSTITUTE for synaptic
consolidation (Fusi 2005 cascade / EWC), reproducing anti-forgetting via an external slow store.

WHAT IS NOT HERE YET (deliberately, per WIRING_MAP "land faithfully, not improvise"): the reliability-
WEIGHTED fusion operating point (Ernst & Banks / Friston precision -- the capstone's BEST arm), the LOOP
ORCHESTRATION that builds each round's grown store from reading (experiment-side; store-write hazards), and
the reader-side `learner_growth` read-out flag -- the last is BLOCKED on `reader_meaning_channel` (the live
`read()` consults NO meaning store yet). The primitives here (fusion + rollback + anchor step) are the safe
substrate those stand on. NOTE (tracked, WIRING_MAP): `align_and_fuse`/`procrustes_rotation`/`_l2norm_rows`
are promoted byte-identical from `experiments/exp_learner_growth_aligned_continual_v1.py`; the experiment
keeps its own copy pending a re-export shim (a follow-up promote+shim; the organ witness asserts byte-equality
so there is no drift at landing).

DEFAULT-OFF / ISLAND: importing this changes NO existing behaviour (no live organ calls it yet -- a DEBT-1
promotion). ⚠️ The GROWTH loop writes a store; STORE-write hazards apply THERE (binary/newline='', git-
commit after every bank, NEVER `git add -A` the canonical store, remote-persist needs USER auth). This
module only FUSES read-side similarities and decides rollback -- it does not itself write a store.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

# The capstone's rollback bar 4: freeze a 40% probe of the OFF-correct (known-correct) items.
PROBE_FRAC = 0.4


def zscore_params(sim_fn: Callable, items: Sequence[Dict]) -> tuple:
    """Mean/std of sim_fn(query, cand) over every DEFINED (item, candidate) pair -- used to make two
    differently-scaled similarity channels (e.g. 5M-token cosines vs 15M-token cosines) commensurable
    before fusing them. std floored at 1.0 if degenerate (constant channel) to avoid a divide-by-~0.
    Ported verbatim from the validated exp_growth_cls_ensemble_v1.zscore_params."""
    vals = []
    for it in items:
        for c in it["cand"]:
            s = sim_fn(it["query"], c)
            if s is not None:
                vals.append(s)
    if not vals:
        return 0.0, 1.0
    arr = np.asarray(vals, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std())
    if std < 1e-12:
        std = 1.0
    return mean, std


def make_ensemble_sim(sim_a: Callable, mean_a: float, std_a: float,
                      sim_b: Callable, mean_b: float, std_b: float, mode: str = "mean") -> Callable:
    """CLS keep-both-stores fusion: z-score each channel, combine by mean or max of whichever channel(s)
    are defined. NEVER discards a channel that IS defined just because the other is not (that is exactly
    the naive-overwrite failure mode this arm is designed to avoid). sim_a = the BASE (old) store, sim_b =
    the GROWN (new) store. Ported verbatim from the validated exp_growth_cls_ensemble_v1.make_ensemble_sim."""
    def fused(q, c):
        sa = sim_a(q, c)
        sb = sim_b(q, c)
        za = (sa - mean_a) / std_a if sa is not None else None
        zb = (sb - mean_b) / std_b if sb is not None else None
        if za is None and zb is None:
            return None
        if za is None:
            return zb
        if zb is None:
            return za
        return (za + zb) / 2.0 if mode == "mean" else max(za, zb)
    return fused


def argmax_pred(sim_fn: Callable, query, cand: Sequence) -> Optional[object]:
    """The store's pick: argmax over candidates of sim_fn(query, cand). None if the store scores none of
    them (an abstain). Matches the validated exp_learner_safety_gate_v1.argmax_pred semantics."""
    best, best_s = None, None
    for c in cand:
        s = sim_fn(query, c)
        if s is None:
            continue
        if best_s is None or s > best_s:
            best_s, best = s, c
    return best


def rollback_gate(items: Sequence[Dict], base_correct_idx: Sequence[int], sim_prior: Callable,
                  updates: Dict[str, Callable], tolerance: float, seed: int,
                  probe_frac: float = PROBE_FRAC) -> Dict:
    """A real regression-checked rollback gate (ported from the validated capstone rollback_eval).
    base_correct_idx = the item indices the OFF/base store got RIGHT (the known-correct set). Freeze a
    PROBE (probe_frac random split) and its disjoint WORKING set. For each candidate update
    (name -> sim_fn of the UPDATED store): measure PROBE corruption = fraction of the frozen probe the
    update flips wrong; ACCEPT iff probe corruption < tolerance else ROLL BACK to sim_prior; then report
    the EFFECT on the DISJOINT WORKING set (the update's corruption if accepted; the prior's if rolled
    back) -- judged on data it did NOT decide on. A RANDOM-decision control (coin-flip accept) shows the
    gate's protection is real. items[i] = {"query","cand","target"}."""
    rng = np.random.default_rng(seed)
    idx = np.asarray(base_correct_idx, dtype=int)
    rng.shuffle(idx)
    n_probe = int(round(len(idx) * probe_frac))
    probe_idx = idx[:n_probe]
    work_idx = idx[n_probe:]

    def corruption_on(pool, sim_fn):
        wrong = 0
        n = 0
        for i in pool:
            it = items[i]
            pred = argmax_pred(sim_fn, it["query"], it["cand"])
            if pred is None:
                continue
            n += 1
            wrong += int(pred != it["target"])
        return (wrong / n) if n else None, n

    prior_work_corr, _ = corruption_on(work_idx, sim_prior)
    report = {"n_probe": int(len(probe_idx)), "n_work": int(len(work_idx)), "tolerance": tolerance,
              "prior_working_corruption": None if prior_work_corr is None else round(prior_work_corr, 4),
              "updates": {}, "random_control": {}}
    rng_ctl = np.random.default_rng(seed + 7)
    for name, sim_upd in updates.items():
        probe_corr, n_pr = corruption_on(probe_idx, sim_upd)
        accept = bool(probe_corr is not None and probe_corr < tolerance)
        if accept:
            work_corr, n_wk = corruption_on(work_idx, sim_upd)
        else:
            work_corr, n_wk = prior_work_corr, len(work_idx)
        rand_accept = bool(rng_ctl.random() < 0.5)
        rc_corr = corruption_on(work_idx, sim_upd)[0] if rand_accept else prior_work_corr
        report["updates"][name] = {
            "probe_corruption": None if probe_corr is None else round(probe_corr, 4),
            "n_probe_scored": n_pr, "decision": "ACCEPT" if accept else "ROLLBACK",
            "working_corruption_after_decision": None if work_corr is None else round(work_corr, 4),
            "n_work_scored": n_wk,
        }
        report["random_control"][name] = {"random_decision": "ACCEPT" if rand_accept else "ROLLBACK",
                                           "working_corruption": None if rc_corr is None else round(rc_corr, 4)}
    return report


# ---------------------------------------------------------------------------------------------------
# THE ANTI-DRIFT SLOW-ANCHOR consolidation step (the continual EMA anchor). Promoted VERBATIM 2026-08-31
# from experiments/exp_learner_growth_aligned_continual_v1.py (the validated live-canary mechanism).
# Pure numpy, self-contained. `alpha` is the consolidation rate eta.
# ---------------------------------------------------------------------------------------------------
def procrustes_rotation(src_shared, ref_shared):
    """Closed-form orthogonal Procrustes: R (d x d) minimizing ||src_shared @ R - ref_shared||_F over the
    SHARED rows. R = U @ Vt where U,S,Vt = svd(src_shared.T @ ref_shared). Orthogonal -> norm-preserving."""
    Mmat = src_shared.T @ ref_shared
    U, _s, Vt = np.linalg.svd(Mmat, full_matrices=False)
    return U @ Vt


def _l2norm_rows(V):
    n = np.linalg.norm(V, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return V / n


def align_and_fuse(ref_vecs, ref_idx, new_vecs, new_idx, alpha, do_align):
    """Keep-both-stores in a SHARED FRAME. Align new_vecs to ref_vecs's frame on the shared vocab (Procrustes
    rotation), L2-normalise both, convex-combine per word over the UNION vocab: fused = (1-a)*ref + a*new for
    shared words, ref-only or new(aligned)-only otherwise. Returns (fused_vecs, union_index). do_align=False
    is the control: average the two UNALIGNED frames (no rotation) -- expected to be meaningless."""
    shared = [w for w in ref_idx if w in new_idx]
    if do_align and len(shared) >= 10:
        A = np.asarray([new_vecs[new_idx[w]] for w in shared], dtype=np.float64)
        B = np.asarray([ref_vecs[ref_idx[w]] for w in shared], dtype=np.float64)
        R = procrustes_rotation(A, B)
        new_aligned = new_vecs @ R
    else:
        new_aligned = new_vecs
    ref_n = _l2norm_rows(np.asarray(ref_vecs, dtype=np.float64))
    new_n = _l2norm_rows(np.asarray(new_aligned, dtype=np.float64))
    union = sorted(set(ref_idx) | set(new_idx))
    uidx = {w: i for i, w in enumerate(union)}
    d = ref_n.shape[1]
    fused = np.zeros((len(union), d), dtype=np.float64)
    for w, i in uidx.items():
        inr = w in ref_idx; inn = w in new_idx
        if inr and inn:
            fused[i] = (1.0 - alpha) * ref_n[ref_idx[w]] + alpha * new_n[new_idx[w]]
        elif inr:
            fused[i] = ref_n[ref_idx[w]]
        else:
            fused[i] = new_n[new_idx[w]]
    return fused, uidx


__all__ = ["PROBE_FRAC", "zscore_params", "make_ensemble_sim", "argmax_pred", "rollback_gate",
           "procrustes_rotation", "align_and_fuse"]
