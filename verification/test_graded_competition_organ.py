"""Witness for hdlab.graded_competition (landed 2026-08-27, consolidation phase).

Self-contained construction proof of the graded cue-based competition MECHANISM (no corpus/front-end
dependency). On synthetic items where each candidate has a latent "true fit" (gold = argmax fit) and each cue
supplies a noisy reflection of that fit weighted by its reliability, the additive->softmax maintained
distribution's normalized ENTROPY is a valid GOLD-FREE difficulty signal: it is CI-separated higher on items
where the argmax pick is WRONG than where it is right (the argmax flips exactly when the true fits are close,
which is also when entropy is high). Can-fail: the info-free RANDOM-SETTLING twin (entropy of a softmax over
random activations, unrelated to the item) must NOT predict the error. Also proves the noise->0 collapse
(graded argmax == map_pick == argmax(net); high gain -> one-hot) and glass-box invariants (no gold in the
signature; normalized entropy is candidate-count-robust). The full-corpus validation is the solver's
verify_graded_competition_parsing_role.py.
"""
from __future__ import annotations

import inspect
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.graded_competition import (  # noqa: E402
    DEFAULT_GAIN, difficulty, graded_pick, map_pick, net_activation, softmax,
)


def _boot_diff(err_vals, cor_vals, rng, n_boot=2000):
    """Bootstrap the mean difference (error - correct) with a 95% CI."""
    err = np.asarray(err_vals, float); cor = np.asarray(cor_vals, float)
    point = err.mean() - cor.mean()
    boots = np.empty(n_boot)
    for b in range(n_boot):
        ei = rng.integers(0, len(err), len(err))
        ci = rng.integers(0, len(cor), len(cor))
        boots[b] = err[ei].mean() - cor[ci].mean()
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(point), float(lo), float(hi)


def main() -> int:
    rng = np.random.default_rng(20260827)
    N, K = 4000, 4
    CUE_SD = {"strong": 0.15, "mid": 0.30, "weak": 0.60}   # cue noise -> reliability
    WEIGHTS = {c: 1.0 / (sd * sd) for c, sd in CUE_SD.items()}  # precision-weighted (Competition-Model validity analog)

    real_err_ent, real_cor_ent = [], []
    twin_err_ent, twin_cor_ent = [], []
    n_err = 0
    for _ in range(N):
        fit = rng.uniform(0.0, 1.0, size=K)          # latent "true fit"; gold = its argmax
        gold = int(np.argmax(fit))
        supports = {c: fit + rng.normal(0.0, sd, size=K) for c, sd in CUE_SD.items()}
        g = graded_pick(supports, WEIGHTS, gain=DEFAULT_GAIN)
        is_err = int(g["win"] != gold)
        n_err += is_err
        # info-free RANDOM-SETTLING twin: entropy of a softmax over random activations for THIS item
        twin_ent = float(graded_pick({"r": rng.normal(0.0, 1.0, size=K)}, {"r": 1.0}, gain=DEFAULT_GAIN)["entropy"])
        if is_err:
            real_err_ent.append(g["entropy"]); twin_err_ent.append(twin_ent)
        else:
            real_cor_ent.append(g["entropy"]); twin_cor_ent.append(twin_ent)

    err_rate = n_err / N
    assert 0.03 < err_rate < 0.45, f"degenerate error rate {err_rate:.3f} (need a genuine can-fail regime)"

    # [1] the maintained-distribution ENTROPY predicts the argmax error, CI-separated
    r_pt, r_lo, r_hi = _boot_diff(real_err_ent, real_cor_ent, rng)
    print(f"[1] entropy(error)-entropy(correct) = {r_pt:+.3f} CI[{r_lo:+.3f},{r_hi:+.3f}] (err_rate={err_rate:.3f})")
    assert r_lo > 0.0, "[witness] entropy does not predict the argmax error CI-separated"

    # [2] info-free RANDOM-SETTLING twin LOSES (carries no item-specific difficulty)
    t_pt, t_lo, t_hi = _boot_diff(twin_err_ent, twin_cor_ent, rng)
    print(f"[2] info-free random-settling twin = {t_pt:+.3f} CI[{t_lo:+.3f},{t_hi:+.3f}] (must not predict error)")
    assert (t_lo <= 0.0 <= t_hi) or (abs(t_pt) < 0.5 * r_pt), \
        "[witness] the random-settling twin predicted the error -> the signal is not the real competition"

    # [3] noise->0 COLLAPSE: graded argmax == map_pick == argmax(net); high gain -> one-hot at the argmax
    sup = {"order": np.array([0.9, 0.2, 0.1, 0.4]), "struct": np.array([0.1, 0.8, 0.3, 0.2]),
           "recency": np.array([0.3, 0.3, 0.2, 0.7])}
    w = {"order": 1.0, "struct": 0.6, "recency": 0.2}
    net = net_activation(sup, w)
    g = graded_pick(sup, w)
    assert g["win"] == int(np.argmax(net)) == map_pick(sup, w), "graded argmax must equal the discrete resolver"
    hot = softmax(net, gain=1e6)
    assert int(np.argmax(hot)) == int(np.argmax(net)) and hot.max() > 0.999, "gain->inf must collapse to argmax"
    print(f"[3] noise->0 collapse PASS (win={g['win']} == argmax(net); high-gain one-hot={hot.max():.4f})")

    # [4] glass-box: no gold in the signature; normalized entropy is candidate-count-robust (uniform -> 1.0)
    params = list(inspect.signature(graded_pick).parameters)
    assert "gold" not in params and "labels" not in params, params
    h4 = difficulty({"u": np.zeros(4)}, {"u": 1.0}); h8 = difficulty({"u": np.zeros(8)}, {"u": 1.0})
    assert abs(h4 - 1.0) < 1e-6 and abs(h8 - 1.0) < 1e-6, (h4, h8)
    # a decisive (one cue dominant, no competition) item -> LOW entropy
    h_low = difficulty({"a": np.array([10.0, 0.0, 0.0, 0.0])}, {"a": 1.0})
    assert h_low < 0.2, f"a decisive item must have LOW entropy, got {h_low:.3f}"
    print(f"[4] glass-box PASS (no gold in signature; uniform4={h4:.4f} uniform8={h8:.4f} -> 1.0; decisive={h_low:.3f})")

    print("\nALL WITNESS ASSERTIONS PASSED -- the additive->softmax maintained-distribution entropy is a valid")
    print("gold-free difficulty signal (CI-separated on the argmax error; the info-free random-settling twin")
    print("loses), the discrete resolver is its noise->0 argmax collapse, and the readout is glass-box.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
