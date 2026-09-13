"""Build the SEMANTIC HUB's live asset: one unit vector per covered lemma = the ATL convergence code h = tanh(W.s + b) of the five
graded spokes (distributional phi, grounded-distinctive, valence, DINOv2 visual referent, per-lemma w2v aggregate), read with the
consolidated weights the owner-DONE pri-13 solver fitted (experiments/exp_semantic_hub_convergence_v1.py: consensus hub = denoising
reconstruction + precision-weighted cross-spoke consensus RSA; Rogers-McClelland convergence, Ma-Pouget precision, Cox 2024 RSL).
The weights file (hub.npz, numpy) is the BETWEEN-CONSOLIDATION snapshot; re-consolidation (batch or the online CLS path) lives in the
experiment class (torch) -- run it, then re-run this tool. Output: data/frontend_assets/semantic_hub_vectors_v1.npz (vocab, vectors).
Usage: python tools/build_semantic_hub_asset.py [--weights data/exp_semantic_hub_convergence_v1/hub.npz]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
os.chdir(REPO)   # the experiment uses repo-relative DATA_DIR

WEIGHTS = os.path.join(REPO, "data", "exp_semantic_hub_convergence_v1", "hub.npz")
OUT = os.path.join(REPO, "data", "frontend_assets", "semantic_hub_vectors_v1.npz")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default=WEIGHTS); ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    t0 = time.time()
    import experiments.exp_semantic_hub_convergence_v1 as E
    z = np.load(a.weights, allow_pickle=True)
    W = np.asarray(z["W"], dtype=np.float64); b = np.asarray(z["b"], dtype=np.float64)
    names = [str(x) for x in z["spoke_names"]]; dims = [int(x) for x in z["spoke_dimvals"]]
    spokes, backbone = E.load_real_spokes()
    # the hub's input order/dims must match the fitted weights: assemble in the weights' spoke order
    ordered = {nm: spokes[nm] for nm in names if nm in spokes}
    X, present, spoke_dims, index = E.assemble(ordered, backbone)
    got = [(nm, d) for nm, d in spoke_dims]
    if got != list(zip(names, dims)):
        raise SystemExit("spoke layout mismatch: weights %s vs assembled %s" % (list(zip(names, dims)), got))
    H = np.tanh(X @ W.T + b)                                  # (n, H): the convergence code
    H /= np.maximum(np.linalg.norm(H, axis=1, keepdims=True), 1e-12)
    covered = present.sum(axis=1) > 0
    vocab = np.array([w for w in backbone if covered[index[w]]], dtype=object)
    vecs = np.stack([H[index[w]] for w in vocab]).astype(np.float32)
    n_spokes = np.array([int(present[index[w]].sum()) for w in vocab], dtype=np.int8)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    np.savez_compressed(a.out, vocab=vocab, vectors=vecs, n_spokes=n_spokes, spoke_names=np.array(names, dtype=object),
                        hub_width=np.int64(W.shape[0]), weights_source=np.array(os.path.relpath(a.weights, REPO)))
    print("wrote %s: %d lemmas x %d-d hub codes (spokes %s) in %.0fs" % (os.path.relpath(a.out, REPO), len(vocab), W.shape[0], names, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
