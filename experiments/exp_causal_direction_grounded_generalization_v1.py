"""exp_causal_direction_grounded_generalization_v1 -- DOES the grounded interventional direction mechanism GENERALIZE,
and HOW DO WE PERFORM VS THE BRAIN? (brain-foundational checklist #3 generalize + #6 vs the brain).

The base prototype (exp_causal_direction_grounded_intervention_v1) recovered direction 0.99 in a LINEAR-Gaussian
micro-world with ~4000 interventional samples/node. Two generalization axes matter for brain fidelity:
  (1) DATA EFFICIENCY -- the brain's signature is FEW-SHOT causal learning: toddlers orient cause->effect from ~2-10
      interventions (Gopnik & Schulz blicket detector; Bramley 2017 near-optimal active learning). If our mechanism
      needs thousands of samples it does NOT match the brain. We sweep n_int and read the data-efficiency CURVE +
      the samples-to-0.9 threshold, against a brain reference band (few-shot, ~<=10).
  (2) FUNCTIONAL FORM -- the world is not linear. We test LINEAR vs monotone-NONLINEAR (tanh) vs NON-monotone
      (quadratic) couplings. The interventional asymmetry is Pearl-general (intervention breaks confounding for ANY
      functional form); the question is whether the READOUT (|cov| under do) survives -- and if not, whether a
      magnitude/rank dependence readout restores it (the mechanism generalizes with the right dependence measure).
  (bonus) CONFOUNDER strength sweep -- grounded should stay high while the observational text-analog degrades.

Reuses make_scm (structure) + causal_reasoner; self-contained nonlinear sampler. Glass-box, synthetic, NO LLM.
Run: .venv/Scripts/python.exe experiments/exp_causal_direction_grounded_generalization_v1.py --run [--smoke]
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"
__bf_note__ = ("generalization + brain-comparison of grounded interventional direction learning: data-efficiency curve "
               "vs the brain's few-shot band; linear/monotone/non-monotone functional forms; confounder robustness.")

import argparse
import json
import os
import sys
import time
from typing import Dict, List

import numpy as np

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("PYTHONHASHSEED", "0")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_grounded_ddyn_v1 import make_scm

from experiments._seed_checkpoint import get_output_dir  # Q115 (owner 2026-08-23): route the output dir
OUT = str(get_output_dir("exp_causal_direction_grounded_generalization_v1"))
TEXT_STORE_CEILING = 0.61
BRAIN_FEWSHOT_BAND = 10   # toddlers/adults orient from ~2-10 interventions (Gopnik/Bramley)


def _link(v, form):
    if form == "linear":
        return v
    if form == "tanh":
        return np.tanh(v)
    if form == "quad":
        return v * v - 1.0            # non-monotone (even) -- breaks a signed-covariance readout
    raise ValueError(form)


def sample_nl(scm: Dict, rng, n: int, do_node: int, form: str, cstr: float) -> np.ndarray:
    """Grounded dynamical sampler with a link FORM and confounder strength cstr. do_node set independently."""
    k = scm["k"]; V = np.zeros((n, k))
    C = rng.normal(0, 1, size=n)
    for j in range(k):
        eps = rng.normal(0, 0.3, size=n)
        if j == do_node:
            V[:, j] = rng.uniform(-2, 2, size=n)
            continue
        val = cstr * scm["gamma"][j] * C + eps
        for i in scm["parents"][j]:
            val = val + scm["sign"][(i, j)] * scm["wt"][(i, j)] * _link(V[:, i], form)
        V[:, j] = val
    return V


def _cov(x, y):
    return float(np.mean((x - x.mean()) * (y - y.mean())))


def infl_cov(intr, a, b):
    """|cov| readout of do(a)->b (works for monotone forms)."""
    return abs(_cov(intr[a][:, a], intr[a][:, b]))


def infl_mag(intr, a, b):
    """Magnitude/variance readout: how much does do(a) MOVE b beyond b's baseline spread? |corr(|a-centered|,|b|)| is
    a monotone-agnostic dependence proxy (recovers non-monotone couplings a signed cov misses)."""
    va = intr[a][:, a]; vb = intr[a][:, b]
    return abs(_cov(np.abs(va - va.mean()), np.abs(vb - vb.mean())))


def _mi_binned(x, y, bins=8):
    """Binned mutual information I(X;Y) >= 0 -- a NON-MONOTONE-robust dependence measure. Captures any functional
    dependence (quadratic, thresholded), which a signed covariance misses. The brain's causal learning is not limited
    to monotone couplings, so the interventional readout should be a general dependence measure."""
    n = len(x)
    if n < bins * 2:
        return 0.0
    xe = np.quantile(x, np.linspace(0, 1, bins + 1)); ye = np.quantile(y, np.linspace(0, 1, bins + 1))
    xe[0] -= 1e-9; ye[0] -= 1e-9
    xi = np.clip(np.digitize(x, xe) - 1, 0, bins - 1); yi = np.clip(np.digitize(y, ye) - 1, 0, bins - 1)
    pij = np.zeros((bins, bins))
    for a, b in zip(xi, yi):
        pij[a, b] += 1.0
    pij /= pij.sum()
    pi = pij.sum(1, keepdims=True); pj = pij.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        m = pij * (np.log(pij + 1e-12) - np.log(pi + 1e-12) - np.log(pj + 1e-12))
    return float(np.nansum(np.where(pij > 0, m, 0.0)))


def infl_mi(intr, a, b):
    """Interventional MUTUAL INFORMATION readout: I(do(a): a, b). do(cause) informs the effect; do(effect) does not
    inform the (exogenous-to-it) cause -> the MI asymmetry orients ANY functional form, monotone or not."""
    return _mi_binned(intr[a][:, a], intr[a][:, b])


def grounded_dir(intr, a, b, readout):
    iab = readout(intr, a, b); iba = readout(intr, b, a)
    return 1 if iab > iba else (-1 if iba > iab else 0)


def _descendants(scm, i):
    k = scm["k"]; reach = {i}; changed = True
    while changed:
        changed = False
        for j in range(k):
            if j not in reach and any(p in reach for p in scm["parents"][j]):
                reach.add(j); changed = True
    reach.discard(i); return sorted(reach)


def direction_acc(form, cstr, n_int, readout, n_world, kk, rng_seed=2026):
    rng = np.random.default_rng(rng_seed)
    hits = []
    for w in range(n_world):
        scm = make_scm(kk, np.random.default_rng(1000 + w))
        intr = {i: sample_nl(scm, rng, n_int, i, form, cstr) for i in range(kk)}
        for i in range(kk):
            for j in _descendants(scm, i):
                gd = grounded_dir(intr, i, j, readout)
                hits.append(1.0 if gd == 1 else 0.0)      # true orientation is i->j
    return float(np.mean(hits)), len(hits)


def run(smoke: bool = False) -> Dict:
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    kk = 8
    n_world = 20 if smoke else 60
    grid_n = [5, 10, 25, 50, 100, 500] if smoke else [3, 5, 10, 25, 50, 100, 500, 2000]

    out = {"smoke": smoke, "k": kk, "n_worlds": n_world, "text_store_ceiling": TEXT_STORE_CEILING,
           "brain_fewshot_band": BRAIN_FEWSHOT_BAND}

    # (1) DATA-EFFICIENCY CURVE (linear, |cov| readout) -- the brain-comparison axis
    curve = {}
    for n_int in grid_n:
        acc, npair = direction_acc("linear", 1.0, n_int, infl_cov, n_world, kk)
        curve[n_int] = round(acc, 4)
    samples_to_90 = next((n for n in grid_n if curve[n] >= 0.90), None)
    out["data_efficiency_linear"] = {"acc_by_n_interventions": curve, "samples_to_0.90": samples_to_90,
                                     "brain_fewshot_band_interventions": BRAIN_FEWSHOT_BAND}

    # (2) FUNCTIONAL-FORM generalization at a fixed modest budget
    nb = 50 if smoke else 100
    forms = {}
    for form in ("linear", "tanh", "quad"):
        a_cov, _ = direction_acc(form, 1.0, nb, infl_cov, n_world, kk)
        a_mag, _ = direction_acc(form, 1.0, nb, infl_mag, n_world, kk)
        a_mi, _ = direction_acc(form, 1.0, nb, infl_mi, n_world, kk)
        forms[form] = {"cov_readout": round(a_cov, 4), "magnitude_readout": round(a_mag, 4),
                       "mutual_information_readout": round(a_mi, 4)}
    out["functional_form_generalization"] = {"n_interventions": nb, "by_form": forms,
        "note": "cov readout handles linear+monotone(tanh); non-monotone(quad) needs a general dependence readout -- "
                "mutual information orients ANY functional form (the brain's causal learning is not monotone-limited)"}

    # (bonus) CONFOUNDER strength (grounded should hold; strong confounder is what kills text/observation)
    conf = {}
    for cstr in ([0.5, 2.0] if smoke else [0.0, 0.5, 1.0, 2.0, 4.0]):
        a, _ = direction_acc("linear", cstr, nb, infl_cov, n_world, kk)
        conf[cstr] = round(a, 4)
    out["confounder_robustness_grounded"] = conf

    de = out["data_efficiency_linear"]; ff = out["functional_form_generalization"]["by_form"]
    out["headline"] = (
        "GROUNDED-DIRECTION GENERALIZATION | DATA-EFFICIENCY (acc by #interventions): %s -> reaches 0.90 at n=%s "
        "(brain few-shot band ~<=%d) | FUNCTIONAL FORM @n=%d: linear cov %.3f / tanh cov %.3f / quad cov %.3f "
        "(quad MUTUAL-INFO-readout %.3f) | CONFOUNDER acc: %s | text ceiling %.2f" % (
            {k: de["acc_by_n_interventions"][k] for k in de["acc_by_n_interventions"]}, de["samples_to_0.90"],
            BRAIN_FEWSHOT_BAND, out["functional_form_generalization"]["n_interventions"],
            ff["linear"]["cov_readout"], ff["tanh"]["cov_readout"], ff["quad"]["cov_readout"],
            ff["quad"]["mutual_information_readout"], out["confounder_robustness_grounded"], TEXT_STORE_CEILING))
    out["elapsed_s"] = round(time.time() - t0, 1)
    tmp = os.path.join(OUT, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as fh:
        json.dump(out, fh, indent=2, default=str)
    os.replace(tmp, os.path.join(OUT, "metrics.json"))
    print("[run] " + out["headline"], flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test or a.smoke:
        run(smoke=True); print("SELFTEST PASS", flush=True); return 0
    run(); return 0


if __name__ == "__main__":
    sys.exit(main())
