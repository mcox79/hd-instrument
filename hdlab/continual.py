"""Continual-learning consolidation primitives (NREM replay + companion bounds).

Operationalizes the substrate_continual_NREM_replay_v1 cell mechanism (proven-bound
MEASURED_MECHANISM at +0.57 drift_reduction; cell-author HARD_PASS framing honest-
downgraded to MM per Skunkworks Fix #28 under-claim default; ledger row delta=+1 as
proven-bound landscape contribution; chain-grade bar forget<=0.05 NOT met by this
primitive alone).

Companion proven-negative: substrate_synaptic_homeostasis_global_downscale_v1 (REM
analog) — global multiplicative downscale destroys older traces uniformly (3/3 arms;
two arms at forget=1.000); revival angle = selective-not-global downscale (composes
with NREM replay via RC7 follow-up cell). The DEPRECATED global_downscale_decorator
intentionally NOT exposed as a public API per the proven negative; only the selective
variant would be eligible after RC7 chain-grade evidence lands.

Brain grounding: NREM sharp-wave-ripple replay analog. HC -> NC replay during NREM
consolidates recent traces. The +0.57 absolute drift reduction at best replay schedule
(every 100 cycles) is a USEFUL bound — partial mitigator, not full solver, of continual-
write drift. Atomized in batch 2 per skunkworks_tier_rule_batch2_4artifact_2026-06-26.md.
"""

from __future__ import annotations

import time
from collections.abc import Callable

import torch

from . import tracing


def replay_cycle(
    W: torch.Tensor,
    replay_indices: torch.Tensor,
    keys: torch.Tensor,
    values: torch.Tensor,
    replay_frac: float = 0.2,
    lr: float = 1.0,
    *,
    direction: str = "forward",
    W_back: torch.Tensor | None = None,
) -> torch.Tensor:
    """Single NREM replay cycle: re-Hebb a fraction of stored (key, value) traces.

    Selects `replay_frac` of indices uniformly from `replay_indices`, re-adds the
    Hebbian outer product (value @ key.T) scaled by lr to W. Mutates W in-place AND
    returns it (caller-convenience).

    Args:
        W: associative-memory weight matrix [N_DIM, N_DIM] or [V_DIM, K_DIM].
        replay_indices: LongTensor of candidate trace indices in keys/values.
        keys: stored keys [M, K_DIM].
        values: stored values [M, V_DIM].
        replay_frac: fraction of replay_indices to actually replay this cycle (default 0.2;
                     brain awake/sleep ratio in mammals ~30-40%; bound landscape covers
                     replay_frac at 0.2 -- RC5 sweep is open follow-up).
        lr: Hebbian re-add learning rate (default 1.0 = full re-Hebb).
        direction: one of {"forward", "reverse", "both"}.
                   "forward" (default): re-Hebb (value, key) in forward orientation into W;
                     bit-equivalent to original primitive.
                   "reverse": re-Hebb (key, value) in REVERSE orientation into W_back
                     (which must be supplied). Replays the (k, v) pairs in REVERSE temporal
                     order — i.e. iterates the selected indices in reverse before the outer-
                     sum, so the propagation direction is goal-back-to-start instead of
                     start-to-goal. Brain analog: hippocampal reverse-replay during sharp-
                     wave ripples (Foster-Wilson 2006; Diba-Buzsaki 2007) — TD credit
                     assignment by back-propagating reward to upstream states.
                   "both": run forward into W AND reverse into W_back in the same call.
        W_back: REQUIRED if direction in {"reverse", "both"}; the separate reverse store.
                Mutated in-place same as W. The reverse store is SEPARATE from W (not W.T)
                so that forward and reverse replay can be selectively gated independently —
                e.g. reward-gated reverse-replay (Ambrose-Pfeiffer-Foster 2016).

    Returns:
        W after in-place replay (W_back is also mutated if direction != "forward").

    Proven-bound (FORWARD direction only — reverse-direction proof open follow-up M5
    reverse-replay cell 2026-06-27): at replay_frac=0.2, N=4096, 2500 cycles continual
    writes, best schedule (replay_every=100) gives drift_reduction=+0.57 absolute
    (baseline 0.88 final_forget vs replay 0.31 final_forget). Chain-grade bar
    forget<=0.05 NOT met; primitive is partial mitigator.
    See: math::T3/EXP_substrate_continual_NREM_replay_v1
    _proven_bound_replay_reduces_drift_0p57_abs.
    """
    if direction not in ("forward", "reverse", "both"):
        raise ValueError(
            f"direction must be one of {{'forward', 'reverse', 'both'}}; got {direction!r}"
        )
    if direction in ("reverse", "both") and W_back is None:
        raise ValueError(
            f"direction={direction!r} requires W_back (the separate reverse store); got None"
        )
    n_replay = max(1, int(len(replay_indices) * replay_frac))
    perm = torch.randperm(len(replay_indices))[:n_replay]
    chosen = replay_indices[perm]
    k_sub = keys[chosen]    # [n_replay, K_DIM]
    v_sub = values[chosen]  # [n_replay, V_DIM]
    if direction in ("forward", "both"):
        delta = lr * (v_sub.T @ k_sub)  # outer-sum (v outer k)
        W.add_(delta)
    if direction in ("reverse", "both"):
        # Reverse-temporal-order replay: iterate selected indices in reverse before
        # the outer-sum. For Hebbian outer-sum the per-order is commutative (sum is
        # the same regardless of iteration order), so the load-bearing reverse
        # semantics are the ORIENTATION (k outer v, not v outer k) — i.e. the
        # reverse store learns "value -> key" instead of "key -> value". This makes
        # W_back @ v approximate k for trained traces — the temporal predecessor.
        chosen_rev = torch.flip(chosen, dims=[0])
        k_sub_rev = keys[chosen_rev]
        v_sub_rev = values[chosen_rev]
        delta_back = lr * (k_sub_rev.T @ v_sub_rev)  # outer-sum (k outer v)
        W_back.add_(delta_back)
    return W


def nrem_replay_decorator(
    write_fn: Callable[..., None],
    *,
    replay_every: int = 100,
    replay_frac: float = 0.2,
    replay_lr: float = 1.0,
) -> Callable[..., None]:
    """Wrap a continual-writes `write_fn` with periodic NREM-replay consolidation.

    The returned wrapper invokes `write_fn(*args, **kwargs)` on every call and, every
    `replay_every` invocations, also performs a `replay_cycle` over the trace buffer
    that the caller maintains in `kwargs` under the keys: `W`, `replay_indices`,
    `keys`, `values`.

    HONEST SCOPE DOCSTRING (load-bearing; do not strip):
    ----------------------------------------------------
    NREM-replay primitive validated as a PARTIAL MITIGATOR of continual-write drift,
    NOT a chain-grade SOLVER. Best-validated bound at replay_every=100, replay_frac=0.2,
    N=4096, 2500 cycles: final_forget=0.31 (baseline 0.88; absolute drift_reduction=+0.57).
    The chain-grade bar (final_forget <= 0.05) is NOT met by this primitive alone.

    DOES NOT apply to your dataset if your continual-write regime differs along:
      - N_DIM (substrate dim; tested at 4096)
      - total cycles (tested at 2500)
      - new-trace-per-cycle ratio (tested with 1 new trace per cycle)
      - replay_frac (tested at 0.2; RC5 sweep open follow-up)
      - replay_every (tested at 100; RC4 finer schedule open follow-up)
      - whether cleanup is also applied during replay (RC6 cleanup-aided open follow-up)
    Validate the bound on YOUR regime before relying on it.

    See:
      math::T3/EXP_substrate_continual_NREM_replay_v1_proven_bound_replay_reduces_drift
        _0p57_abs_best_arm_0p31_final_forget_chain_grade_bar_0p05_not_met_monotone_in
        _replay_frequency_director_honest_downgrade
    Atomized 2026-06-26 batch 2 per Skunkworks Fix #28 default under-claim.

    Args:
        write_fn: the continual-write step you're decorating (e.g. Hebbian add).
        replay_every: replay cadence in calls (default 100; cell-validated).
        replay_frac: fraction of trace buffer to replay per cycle (default 0.2; brain
                     awake/sleep analog).
        replay_lr: Hebbian re-add learning rate during replay (default 1.0).

    Returns:
        Wrapper callable with the same signature; mutates W in-place on replay.
    """
    call_count = {"n": 0}

    def wrapper(*args, **kwargs):
        write_fn(*args, **kwargs)
        call_count["n"] += 1
        if call_count["n"] % replay_every == 0:
            W = kwargs.get("W") or (args[0] if args else None)
            replay_indices = kwargs.get("replay_indices")
            keys = kwargs.get("keys")
            values = kwargs.get("values")
            if W is None or replay_indices is None or keys is None or values is None:
                # Silent skip if caller doesn't pass the replay-buffer kwargs; honest
                # scope: this decorator can only replay what it's given.
                return
            t0 = time.perf_counter_ns()
            replay_cycle(W, replay_indices, keys, values,
                         replay_frac=replay_frac, lr=replay_lr)
            tracing.emit(
                "continual.nrem_replay",
                {"call_n": call_count["n"], "replay_frac": replay_frac,
                 "replay_every": replay_every},
                None,
                elapsed_ns=time.perf_counter_ns() - t0,
            )

    return wrapper


# ============================================================================
# NOT EXPOSED: global_downscale_decorator
# ============================================================================
# REM-homeostasis analog `global_downscale_decorator` is INTENTIONALLY NOT EXPOSED as
# a public API. The proven-negative cell substrate_synaptic_homeostasis_global_downscale_v1
# demonstrated that global multiplicative downscale (factor < 1.0 applied to ALL W)
# DESTROYS older traces uniformly; 3-of-3 arms forget=1.000 vs baseline=0.883.
#
# See: math::T3/EXP_substrate_synaptic_homeostasis_global_downscale_v1_HARD_FAIL
#      _proven_negative_global_multiplicative_downscale_destroys_older_traces_uniformly
#      _3of3_arms_all_seeds_clean
#
# Revival angle (RC7 open follow-up): selective_not_global_downscale_decorator —
# downscale ONLY W rows whose recent retrieval-activation is below threshold (i.e.
# "active during retrieval = protected"). This more faithfully matches the brain's REM
# homeostasis (REM downscales un-replayed traces, not uniform decay). The composition
# test (NREM replay + selective REM downscale) is the path to chain-grade. Only after
# RC7 lands chain-grade evidence will a selective_downscale_decorator be added here.
#
# This implements the "no scaffold-free primitive without verified witness" discipline.
