"""hdlab/n400_coherence_monitor.py -- ORGAN F5, THE N400 COHERENCE MONITOR (event segmentation).

THE ORGAN THE AUDIT SAID WAS MISSING, NOW BUILT. `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (Tier 3, F5):
"N400 coherence monitor -- MISSING. No module computes ||Delta situation-model||." This is that
module, promoted from the validated cell `exp_prediction_error_event_segmentation_v1` (problem
`the_substrate_does_not_learn_or_update_by_prediction_error`, integrated EXCELLENT 2026-08-26).

WHAT IT COMPUTES. The brain constantly predicts the next input against the situation it is currently
tracking; when a word does not fit, that surprise (the N400) says "the situation just changed -- start
a new event." This organ is that signal as an ONLINE event-boundary detector:

  - a RUNNING gist `m` of the CURRENT event's content (the mean of the content vectors since the last
    boundary), RESET at every boundary -- this reset is the whole trick (see the "why it works" note);
  - a GRADED forward prediction error `e = 1 - cos(content_i, m)` -- graded, NOT sign-quantised, and
    computed in the CONTENT (semantic-similar) space, NOT the near-orthogonal binding space;
  - an EST relative threshold: a boundary is posted when `e` spikes relative to the model's OWN recent
    baseline (`running_avg_update`), i.e. `e >= tau * baseline`, not against a fixed constant.

WHY IT WORKS, AND WHY THE TWO PRIOR ATTEMPTS FAILED (measured, do not re-litigate):
  - The RESET is load-bearing. Surprise vs a whole-stream anchor that never resets (FORM_NOVELTY)
    catches early boundaries then blurs into every topic and misses late ones (caps ~0.74). Running
    reset to the CURRENT-event gist is what makes this the N400 rather than global novelty.
  - The SPACE is load-bearing. The naive ||Delta binding-register|| ties no-segmentation: in a
    near-orthogonal code every bound pair changes the register by ~the same amount, so its magnitude
    is uninformative. The error must be a CONTENT prediction error. (This is the p1 `sign_quantiser`
    coupling made concrete: graded AND content-similar, not sign'd / near-orthogonal.)
  On the validated instrument the downstream within-event recovery was 0.988 vs 0.52/0.44 baselines
  and a 0.74 form-novelty floor; boundary F1 0.987; the win is boundary POSITION, not rate.

BRAIN FRAME -- PINNED vs OUR-INVENTION.
  PINNED    Event Segmentation Theory: a perceived boundary fires when prediction error rises sharply
            against the model's own running baseline (Reynolds, Zacks & Braver 2007). The N400 is a
            graded coherence/integration signal (Kutas & Federmeier 2011). The reference the error is
            taken against is the RUNNING situation model (Zwaan & Radvansky).
  OUR-INVENTION-UNDER-TEST  the exact predictor (a running MEAN of the current event is a sufficient
            minimal predictor -- last-item and an online learned transition map behave the same, tested
            in the cell); the threshold `tau` and baseline `decay` (SWEEP per deployment, do NOT adopt
            the cell's synthetic-tuned defaults blindly); the minimum event duration.

STATUS: OFF-PATH / WIRE_CANDIDATE. Importing this changes NO existing behaviour. Wiring it live (post a
boundary -> advance `situation_model_accumulate`'s event slot) is a separate step and must be measured
on the LIVE reader before any capability claim -- the cell's win is a synthetic construction proof.

USAGE
  python -m hdlab.n400_coherence_monitor      # self-test
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .predictive_coding import running_avg_update

# Ported from the validated cell. SWEEP these per deployment; they are tuned to a synthetic stream and
# a constraint (short streams) the live reader does not share -- do not adopt them as truth.
DEFAULT_TAU = 1.5          # EST relative threshold: fire when e >= tau * running-baseline
DEFAULT_DECAY = 0.30       # running-average baseline low-pass decay
DEFAULT_MIN_SEG_LEN = 2    # a boundary cannot fire until the current event has this many items
_EPS = 1e-9


@dataclass(frozen=True)
class N400Event:
    """One observation's outcome from the monitor."""
    is_boundary: bool
    error: float             # the graded content prediction error e = 1 - cos(content, running gist)
    baseline: float          # the running-average baseline BEFORE this observation (the denominator)
    ratio: float             # e / baseline (inf-safe); the EST comparison quantity
    segment: int             # 0-based index of the event this observation was assigned to


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    return float(np.dot(a, b) / ((na + _EPS) * (nb + _EPS)))


class N400CoherenceMonitor:
    """Online event-boundary detector. Feed it the CONTENT (semantic) vector of each proposition in
    order via `observe`; it returns an `N400Event` per item and posts a boundary when the running
    prediction error spikes. Stateful -- one monitor per stream; call `reset()` to reuse.

    Faithful to `exp_prediction_error_event_segmentation_v1.seg_relative_pe(mode='running')`: the
    running gist resets on a boundary, the baseline is updated only on non-boundary steps, and a
    boundary needs `min_seg_len` items in the current event first."""

    def __init__(self, tau: float = DEFAULT_TAU, *, decay: float = DEFAULT_DECAY,
                 min_seg_len: int = DEFAULT_MIN_SEG_LEN) -> None:
        if tau <= 0.0:
            raise ValueError(f"tau must be > 0; got {tau}")
        if not 0.0 < decay <= 1.0:
            raise ValueError(f"decay must be in (0, 1]; got {decay}")
        self.tau = float(tau)
        self.decay = float(decay)
        self.min_seg_len = int(min_seg_len)
        self.reset()

    def reset(self) -> None:
        self._gist_sum: Optional[np.ndarray] = None
        self._n = 0                       # items in the current event
        self._baseline: Optional[float] = None
        self._segment = 0

    def observe(self, content) -> N400Event:
        """Process the next proposition's content vector. Returns its N400Event."""
        v = np.asarray(content, dtype=float).reshape(-1)
        if self._gist_sum is None:        # first item: seed the event, no prediction error yet
            self._gist_sum = v.copy()
            self._n = 1
            return N400Event(False, 0.0, 0.0, 0.0, self._segment)
        m = self._gist_sum / self._n
        e = 1.0 - _cos(v, m)
        can_fire = self._n >= self.min_seg_len
        base = self._baseline
        fired = bool(can_fire and base is not None and base > _EPS and e >= self.tau * base)
        ratio = (e / base) if (base is not None and base > _EPS) else (float("inf") if e > _EPS else 0.0)
        base_before = float(base) if base is not None else 0.0
        if fired:
            # boundary: open a new event at this item; baseline is NOT updated on a boundary step
            # (matches the cell -- a boundary spike must not contaminate its own baseline)
            self._segment += 1
            self._gist_sum = v.copy()
            self._n = 1
        else:
            self._gist_sum = self._gist_sum + v
            self._n += 1
            self._baseline = running_avg_update(self._baseline, e, decay=self.decay)
        return N400Event(fired, float(e), base_before, float(ratio), self._segment)


def segment(contents: Sequence, tau: float = DEFAULT_TAU, *, decay: float = DEFAULT_DECAY,
            min_seg_len: int = DEFAULT_MIN_SEG_LEN) -> Tuple[List[int], List[int]]:
    """Batch convenience over a whole stream. Returns (segment_id_per_item, boundary_indices)."""
    mon = N400CoherenceMonitor(tau, decay=decay, min_seg_len=min_seg_len)
    seg_of: List[int] = []
    boundaries: List[int] = []
    for i, c in enumerate(contents):
        ev = mon.observe(c)
        if ev.is_boundary:
            boundaries.append(i)
        seg_of.append(ev.segment)
    return seg_of, boundaries


# -------------------------------------------------------------------------------------------
# SELF-TESTS. Each can fail.
# -------------------------------------------------------------------------------------------

def _synthetic_stream(n_events: int, dim: int, ev_len: int, noise: float, seed: int):
    """K near-orthogonal event topics; within an event each item is the UNIT topic plus a `noise`-scaled
    UNIT perturbation (so `noise` is the true relative spread: <1 => coherent within an event, a
    near-orthogonal jump at each boundary). Returns (contents, true_boundaries)."""
    g = np.random.default_rng(seed)
    topics = g.standard_normal((n_events, dim))
    topics /= np.linalg.norm(topics, axis=1, keepdims=True) + _EPS
    contents = []
    true_b = []
    for ev in range(n_events):
        for j in range(ev_len):
            if ev > 0 and j == 0:
                true_b.append(len(contents))
            nz = g.standard_normal(dim)
            nz /= np.linalg.norm(nz) + _EPS
            v = topics[ev] + noise * nz            # unit topic + noise*unit -> cos(v,topic)~1/sqrt(1+noise^2)
            contents.append(v / (np.linalg.norm(v) + _EPS))
    return contents, set(true_b)


def _f1(pred: set, gold: set) -> float:
    if not pred and not gold:
        return 1.0
    tp = len(pred & gold)
    prec = tp / len(pred) if pred else 0.0
    rec = tp / len(gold) if gold else 0.0
    return (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0


def _selftest_posts_boundaries_at_topic_jumps() -> dict:
    contents, gold = _synthetic_stream(n_events=6, dim=128, ev_len=4, noise=0.4, seed=7)
    _, boundaries = segment(contents, tau=DEFAULT_TAU)
    f1 = _f1(set(boundaries), gold)
    assert f1 >= 0.75, f"boundary F1 too low ({f1:.3f}); the monitor should find topic jumps"
    return {"f1": round(f1, 3), "n_pred": len(boundaries), "n_gold": len(gold)}


def _selftest_coherent_stream_stays_quiet() -> dict:
    # ONE topic throughout -> a within-event coherent run should not manufacture boundaries.
    contents, _ = _synthetic_stream(n_events=1, dim=128, ev_len=20, noise=0.4, seed=11)
    _, boundaries = segment(contents, tau=DEFAULT_TAU)
    # a handful of stray fires is tolerable noise; a segmenter that shreds a coherent stream is broken.
    assert len(boundaries) <= 2, f"too many spurious boundaries on a coherent stream: {boundaries}"
    return {"n_spurious": len(boundaries), "n_items": len(contents)}


def _selftest_min_seg_len_enforced() -> dict:
    contents, _ = _synthetic_stream(n_events=8, dim=64, ev_len=3, noise=0.5, seed=3)
    seg_of, boundaries = segment(contents, tau=1.2, min_seg_len=2)
    # no two boundaries closer than min_seg_len apart
    diffs = [b2 - b1 for b1, b2 in zip(boundaries, boundaries[1:])]
    assert all(d >= 2 for d in diffs), f"min_seg_len violated: boundary gaps {diffs}"
    return {"boundaries": boundaries[:8], "min_gap": (min(diffs) if diffs else None)}


def _selftest_running_reset_beats_global_anchor() -> dict:
    # The reset is the trick: a running-reset monitor should track late boundaries a global (never-
    # reset) anchor loses. Compare boundary F1 on a multi-event stream.
    contents, gold = _synthetic_stream(n_events=6, dim=128, ev_len=4, noise=0.4, seed=21)
    _, running_b = segment(contents, tau=DEFAULT_TAU)
    # global anchor: gist = mean of ALL items so far (never reset). Reproduce inline.
    gsum = None
    n = 0
    baseline = None
    glob_b = []
    for i, c in enumerate(contents):
        v = np.asarray(c, dtype=float)
        if gsum is None:
            gsum = v.copy(); n = 1; continue
        m = gsum / n
        e = 1.0 - _cos(v, m)
        if baseline is not None and baseline > _EPS and e >= DEFAULT_TAU * baseline:
            glob_b.append(i)
        gsum = gsum + v; n += 1
        baseline = running_avg_update(baseline, e, decay=DEFAULT_DECAY)
    f1_run = _f1(set(running_b), gold)
    f1_glob = _f1(set(glob_b), gold)
    assert f1_run >= f1_glob, f"running-reset ({f1_run:.3f}) should not lose to global anchor ({f1_glob:.3f})"
    return {"f1_running": round(f1_run, 3), "f1_global": round(f1_glob, 3)}


def run_selftests() -> dict:
    out = {
        "posts_boundaries_at_topic_jumps": _selftest_posts_boundaries_at_topic_jumps(),
        "coherent_stream_stays_quiet": _selftest_coherent_stream_stays_quiet(),
        "min_seg_len_enforced": _selftest_min_seg_len_enforced(),
        "running_reset_beats_global_anchor": _selftest_running_reset_beats_global_anchor(),
    }
    return out


if __name__ == "__main__":
    import json

    print(json.dumps(run_selftests(), indent=2))
    print("N400 COHERENCE MONITOR SELF-TEST PASS")
