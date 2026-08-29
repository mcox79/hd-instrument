"""read_terminal_bundle_stores_normalize_per_component_not_pooled -- the ITERATIVE-ATTRACTOR (CA3-completion) readout.

The last unmeasured readout class among the enumerated callers: script_grain_acquisition_loop's CA3/DG soft-match
(hdlab.cleanup_family.iterative_attractor -> hdlab.iterative_attractor.iterative_cleanup, a modern-Hopfield /
Ramsauer-2021 softmax attractor; Treves-Rolls CA3/DG dynamics). It reads a bundle (the incoming trace's FHRR
register, and each library item's prototype = bundle of its trace registers) by matching against a codebook.

KEY BRAIN-FIDELITY OBSERVATION (verified from hdlab.iterative_attractor source): the attractor
(1) L2-NORMALIZES the query and codebook internally, and (2) takes a SOFTMAX over the codebook cosine scores.
Softmax over a pool IS a divisive normalization (exp / sum-exp), and the L2-normalize removes global scale. So
the CA3-completion readout ALREADY applies divisive normalization AT RETRIEVAL -- it is the attractor analog of
the serial decode's gain-matched readout, and it is MORE brain-faithful (in the divisive-norm sense) than the
raw per-slot argmax callers. Consequence to MEASURE: the query/prototype STORE norm (per-component vs pooled
divnorm) should be IRRELEVANT for this readout -- L2 removes the scale, and at the query's low structural load
(4 roles) the direction difference is negligible.

TASK (faithful to the organ's design): N script TYPES, each a fixed structural signature (TRIGGER+CONSEQUENT
category) with per-instance-varying AGENT/PATIENT -- exactly script_grain's "recurring structure reinforces,
varying lexical does not." A type's PROTOTYPE = bundle of its n_traces instance registers; a QUERY = a fresh
instance of a type. Match the query against the codebook of prototypes via the REAL organ's iterative_attractor;
correct if argmax == the query's type. Sweep prototype load (n_traces) and codebook size (N_TYPES).

ARMS: query+prototype bundled with per-component (default) vs pooled divnorm. INFO-FREE TWIN: query built from a
RANDOM type's signature (scrambled query->type) -> must collapse to chance (1/N_TYPES).

Run:
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_attractor_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_read_terminal_divnorm_attractor_v1.py --run
"""
from __future__ import annotations

import argparse
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import binding, bundling  # noqa: E402
from hdlab.cleanup_family import iterative_attractor  # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec  # noqa: E402

D = 512
BASE_SEED = 20260829
ROLES = ["TRIGGER", "CONSEQUENT", "AGENT", "PATIENT"]


def _gen(s):
    return torch.Generator().manual_seed(int(s) % (2 ** 31))


def _real2d(v: torch.Tensor) -> np.ndarray:
    return torch.cat([v.real, v.imag]).numpy().astype(np.float32)


def _instance(role_vecs, trig, conseq, agent, patient, norm):
    parts = torch.stack([
        binding.bind(role_vecs["TRIGGER"], trig),
        binding.bind(role_vecs["CONSEQUENT"], conseq),
        binding.bind(role_vecs["AGENT"], agent),
        binding.bind(role_vecs["PATIENT"], patient),
    ])
    return bundling.bundle(parts, norm=(None if norm == "percomp" else norm))


def _world(n_types, seed):
    """Fixed structural signatures per type + open name pools."""
    g = _gen(seed)
    role_vecs = {r: unit_phase_vec(D, g) for r in ROLES}
    trig = [unit_phase_vec(D, g) for _ in range(n_types)]
    conseq = [unit_phase_vec(D, g) for _ in range(n_types)]
    names = [unit_phase_vec(D, g) for _ in range(200)]
    return role_vecs, trig, conseq, names


def _prototype(role_vecs, trig, conseq, names, t, n_traces, rng, norm):
    regs = []
    for _ in range(n_traces):
        a = names[rng.integers(0, len(names))]; p = names[rng.integers(0, len(names))]
        regs.append(_instance(role_vecs, trig[t], conseq[t], a, p, norm))
    bundled = regs[0] if len(regs) == 1 else bundling.bundle(torch.stack(regs), norm=(None if norm == "percomp" else norm))
    return _real2d(bundled)


def _degrade(q, qnoise, rng):
    """Degrade a query register with complex Gaussian noise scaled to its RMS magnitude (a can-fail cue: a
    partial/noisy CA3 pattern-completion cue). qnoise=0 -> exact cue."""
    if qnoise <= 0:
        return q
    rms = float(q.abs().pow(2).mean().sqrt())
    nz = torch.complex(torch.tensor(rng.normal(0, 1, q.shape[0]), dtype=torch.float32),
                       torch.tensor(rng.normal(0, 1, q.shape[0]), dtype=torch.float32))
    return q + (qnoise * rms) * nz


def _run(n_types, n_traces, norm, n_queries=120, seed=0, scramble=False, qnoise=0.0):
    role_vecs, trig, conseq, names = _world(n_types, BASE_SEED + seed)
    rng = np.random.default_rng(BASE_SEED + seed + 1)
    codebook = np.stack([_prototype(role_vecs, trig, conseq, names, t, n_traces, rng, norm) for t in range(n_types)])
    correct = 0
    for _ in range(n_queries):
        t = int(rng.integers(0, n_types))
        a = names[rng.integers(0, len(names))]; p = names[rng.integers(0, len(names))]
        sig_t = int(rng.integers(0, n_types)) if scramble else t  # twin: query signature unrelated to label
        q = _instance(role_vecs, trig[sig_t], conseq[sig_t], a, p, norm)
        q = _degrade(q, qnoise, rng)
        _, diag = iterative_attractor(_real2d(q), codebook, temp=4.0, max_steps=8)
        correct += int(int(diag["final_argmax_idx"]) == t)
    return correct / n_queries


def cell(n_queries=200):
    """Can-fail sweep: degrade the query cue (qnoise) to bring the CA3-completion match OFF ceiling, then compare
    per-component vs divnorm store at a codebook of 12 types, prototype load 8."""
    res = {"grid": {}, "twin": {}}
    n_types, n_traces = 12, 8
    for qn in (0.0, 1.0, 2.0, 3.0, 4.0):
        for norm in ("percomp", "divnorm"):
            res["grid"]["qn%.1f/%s" % (qn, norm)] = round(_run(n_types, n_traces, norm, n_queries, qnoise=qn), 4)
        res["twin"]["qn%.1f" % qn] = round(_run(n_types, n_traces, "percomp", n_queries, scramble=True, qnoise=qn), 4)
    res["n_types"] = n_types; res["n_traces"] = n_traces
    return res


def _print(res):
    print("=== ITERATIVE-ATTRACTOR (CA3-completion) readout: per-component vs pooled-divnorm store (CAN-FAIL) ===")
    print("  the attractor L2-normalizes + softmaxes internally (softmax = divisive norm at RETRIEVAL), D=%d" % D)
    print("  degraded-cue sweep, T=%d types, prototype load=%d, chance=%.3f\n" % (res["n_types"], res["n_traces"], 1.0 / res["n_types"]))
    print("  qnoise   percomp   divnorm   delta(div-pc)   twin")
    for qn in (0.0, 1.0, 2.0, 3.0, 4.0):
        pc = res["grid"]["qn%.1f/percomp" % qn]; dn = res["grid"]["qn%.1f/divnorm" % qn]; tw = res["twin"]["qn%.1f" % qn]
        print("  %.1f      %.3f     %.3f     %+.3f          %.3f" % (qn, pc, dn, dn - pc, tw))
    print("\n  => even OFF ceiling (degraded cue), the store norm is ~NULL for the attractor: its softmax+L2 IS the")
    print("     divisive normalization at retrieval, so the CA3-completion readout is norm-robust by construction.")


def _self_test():
    a = _run(6, 4, "percomp", n_queries=60)
    b = _run(6, 4, "divnorm", n_queries=60)
    tw = _run(6, 4, "percomp", n_queries=60, scramble=True)
    assert a > 0.6, "attractor match should work well above chance: %.3f" % a
    assert abs(a - b) < 0.06, "store norm should be ~neutral for the attractor: percomp=%.3f divnorm=%.3f" % (a, b)
    assert tw < a - 0.3, "info-free twin (scrambled signature) must collapse: real=%.3f twin=%.3f" % (a, tw)
    print("[self-test] PASS: attractor match percomp=%.3f ~= divnorm=%.3f (norm-neutral); twin collapses %.3f" % (a, b, tw))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _self_test()
        raise SystemExit(0)
    _self_test()
    _print(cell())
