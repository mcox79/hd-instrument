"""Scaffold-free witness for hdlab/n400_coherence_monitor.py (ORGAN F5), landed 2026-08-26 from the
integrated problem `the_substrate_does_not_learn_or_update_by_prediction_error`.

Proves, first-hand and deterministically, the three load-bearing properties the integrated result rests
on -- so the ORGAN carries them, not just the experiment:
  (1) it posts boundaries at topic jumps (segments a discourse), boundary F1 high;
  (2) the RUNNING RESET is load-bearing -- it beats a never-resetting global anchor (why the two prior
      "surprise" negatives died);
  (3) the CONTENT SPACE is load-bearing -- the same detector on a near-orthogonal (binding-like) code
      cannot segment (the p1 `sign_quantiser` coupling: graded AND content-similar, not near-orthogonal).
Plus a GUARD that the organ reuses the pinned EST `running_avg_update`, and that a coherent stream stays
quiet. Writes nothing; own-process only.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from hdlab import n400_coherence_monitor as n4
from hdlab.predictive_coding import running_avg_update

_EPS = 1e-9


def _stream(n_events, dim, ev_len, noise, seed, *, orthogonal_items=False):
    """Coherent-within / jump-between content stream (orthogonal_items=False), OR a near-orthogonal
    per-item code (orthogonal_items=True) that mimics the binding register: every item near-orthogonal
    to every other, so there is no content gist to predict against."""
    g = np.random.default_rng(seed)
    topics = g.standard_normal((n_events, dim))
    topics /= np.linalg.norm(topics, axis=1, keepdims=True) + _EPS
    contents, gold = [], set()
    for ev in range(n_events):
        for j in range(ev_len):
            if ev > 0 and j == 0:
                gold.add(len(contents))
            if orthogonal_items:
                v = g.standard_normal(dim)                 # a fresh near-orthogonal code per item
            else:
                nz = g.standard_normal(dim); nz /= np.linalg.norm(nz) + _EPS
                v = topics[ev] + noise * nz                # unit topic + noise*unit -> coherent within event
            contents.append(v / (np.linalg.norm(v) + _EPS))
    return contents, gold


def _f1(pred, gold):
    pred, gold = set(pred), set(gold)
    if not pred and not gold:
        return 1.0
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    return (2 * p * r / (p + r)) if (p + r) > 0 else 0.0


def _global_anchor_boundaries(contents, tau, decay):
    """The FORM_NOVELTY control: same detector but the gist is the mean of ALL items so far (never reset)."""
    gsum, n, baseline, b = None, 0, None, []
    for i, c in enumerate(contents):
        v = np.asarray(c, float)
        if gsum is None:
            gsum, n = v.copy(), 1
            continue
        m = gsum / n
        e = 1.0 - n4._cos(v, m)
        if baseline is not None and baseline > _EPS and e >= tau * baseline:
            b.append(i)
        gsum, n = gsum + v, n + 1
        baseline = running_avg_update(baseline, e, decay=decay)
    return b


def test_guard_reuses_pinned_est_update():
    # the organ must sit on the literature-pinned running-average update, not a private reimplementation
    assert n4.running_avg_update is running_avg_update, "organ must reuse predictive_coding.running_avg_update"
    assert abs(running_avg_update(None, 0.5) - 0.5) < 1e-9, "seed with first value"
    assert abs(running_avg_update(1.0, 0.0, decay=0.3) - 0.7) < 1e-9, "EST low-pass math"
    print("PASS guard_reuses_pinned_est_update")


def test_posts_boundaries_at_topic_jumps():
    contents, gold = _stream(6, 128, 4, 0.4, seed=101)
    _, boundaries = n4.segment(contents, tau=n4.DEFAULT_TAU)
    f1 = _f1(boundaries, gold)
    assert f1 >= 0.8, f"boundary F1 too low: {f1:.3f} (pred={boundaries}, gold={sorted(gold)})"
    print(f"PASS posts_boundaries_at_topic_jumps: F1={f1:.3f}")


def test_running_reset_is_load_bearing():
    contents, gold = _stream(7, 128, 4, 0.4, seed=202)
    _, running_b = n4.segment(contents, tau=n4.DEFAULT_TAU)
    global_b = _global_anchor_boundaries(contents, n4.DEFAULT_TAU, n4.DEFAULT_DECAY)
    f1_run, f1_glob = _f1(running_b, gold), _f1(global_b, gold)
    assert f1_run >= 0.8, f"running-reset should segment well: {f1_run:.3f}"
    assert f1_run > f1_glob, f"running-reset ({f1_run:.3f}) must beat the never-reset anchor ({f1_glob:.3f})"
    print(f"PASS running_reset_is_load_bearing: running F1={f1_run:.3f} > global F1={f1_glob:.3f}")


def test_content_space_is_load_bearing():
    # the same detector on a near-orthogonal (binding-like) code cannot find the boundaries: there is no
    # content gist to predict against, so every item looks equally surprising (the ||Delta register|| trap).
    contents, gold = _stream(6, 128, 4, 0.0, seed=303, orthogonal_items=True)
    _, boundaries = n4.segment(contents, tau=n4.DEFAULT_TAU)
    f1 = _f1(boundaries, gold)
    assert f1 <= 0.4, f"a near-orthogonal code should NOT be segmentable, but F1={f1:.3f}"
    print(f"PASS content_space_is_load_bearing: near-orthogonal code F1={f1:.3f} (cannot segment)")


def test_coherent_stream_stays_quiet():
    contents, _ = _stream(1, 128, 20, 0.3, seed=404)
    _, boundaries = n4.segment(contents, tau=n4.DEFAULT_TAU)
    assert len(boundaries) <= 2, f"coherent stream should stay quiet, got boundaries {boundaries}"
    print(f"PASS coherent_stream_stays_quiet: {len(boundaries)} spurious boundaries on 20 items")


if __name__ == "__main__":
    test_guard_reuses_pinned_est_update()
    test_posts_boundaries_at_topic_jumps()
    test_running_reset_is_load_bearing()
    test_content_space_is_load_bearing()
    test_coherent_stream_stays_quiet()
    print("WITNESS PASS")
