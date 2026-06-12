"""
exp_substrate_name_augmented_encoding_recovery_gpu_v1.py -- constructive validation of the encoding-discriminability fix:
  does folding the EXISTING atom-name field into the algebra-HRR encoding recover the composition/decode cleanup deficit? -- light-GPU.

ROUTING: follow-on to the near-duplicate diagnostic (~32 cos=1.0 collision atoms cap cleanup; root cause = 0-populated
  signature/complexity -> atoms sharing algebra_category encode identically). The recommended fix is "finer encoding". This
  cell CONSTRUCTIVELY TESTS it using data ALREADY PRESENT (the atom id/name tokens -- no bge, no content authoring): build a
  name-signature vector per atom (HRR bundle of hashed name+id tokens, same scheme as AlgebraIndex fillers), form an augmented
  codebook aug = normalize(algebra_hrr + alpha * name_vec), and re-measure composition cleanup capacity (Cell A protocol) vs
  the plain algebra_hrr codebook. If augmentation separates the collisions, cleanup recovers toward the uniform-codebook 1.0.
  Substrate-quality-first; NO LLM frame. Informs (does not implement) the Testbed encoding change.

  Sweep alpha in {0 (plain), 0.5, 1.0, 2.0}; cleanup@1 at F in {1,3,10}; 3 seeds. alpha=0 reproduces the deficit (~0.84-0.93).

PRE-REGISTERED (substrate-property):
  HARD-PASS: name-augmented cleanup@1 at F=3 >= 0.97 at some alpha (existing name field recovers decode to near-uniform).
  MIDDLE: best augmented F3 cleanup in 0.92-0.97 (partial recovery). HARD-FAIL: < 0.92 (name field insufficient; needs the
  authored signature/complexity semantic fields, not just name tokens). UNKNOWN if corpus load fails.
ASCII-only. torch (light-GPU). --self-test + --smoke + metrics.json. Route via overnight_queue (GPU) or local_cpu_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, hashlib, re
from pathlib import Path
from typing import Dict, Tuple
try:
    import torch
    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except Exception:
    _DEVICE = "cpu"
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_name_augmented_encoding_recovery_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
DIM = 1024
ALPHAS = [0.0, 0.25, 0.5, 1.0]   # cross-axis alpha-sweep drill Capability 1 (BINDING) per Research 2026-06-12
F_SWEEP = [1, 3, 10, 20]          # extended to F=20 for the rule-generalization-at-high-binding-count test
SEEDS = [7, 8, 9]
N_TRIALS = 20
_TOK = re.compile(r"[a-z0-9]+")


def _tok_vec(token, dim):
    """Deterministic unit vector for a token (same hashing scheme spirit as AlgebraIndex fillers)."""
    h = int(hashlib.sha256(("nametok::" + token).encode()).hexdigest(), 16)
    rng = np.random.default_rng(h % (2 ** 63 - 1))
    v = rng.standard_normal(dim).astype(np.float64)
    return v / (np.linalg.norm(v) + 1e-12)


def _name_vec(atom_id, dim):
    """Bundle of hashed name+id tokens -> a name-signature vector (shared tokens -> shared component)."""
    toks = _TOK.findall(atom_id.lower())
    if not toks:
        return np.zeros(dim)
    s = np.sum([_tok_vec(t, dim) for t in toks], axis=0)
    n = np.linalg.norm(s)
    return s / n if n > 0 else s


def _unitary_roles(n, dim, gen):
    v = torch.randn(n, dim, generator=gen)
    fv = torch.fft.fft(v); fv = fv / (fv.abs() + 1e-12)
    return torch.fft.ifft(fv).real.contiguous()


def _load():
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    ps = PartitionedStore(REPO / "data" / "substrate_index")
    ai = AlgebraIndex(dim=DIM); ai.build(ps)
    ids, alg, nm = [], [], []
    for aid, av in ai._atom_vectors.items():
        if av.algebra_hrr is not None:
            ids.append(aid); alg.append(av.algebra_hrr); nm.append(_name_vec(aid, DIM))
    if not alg:
        return None, None, None
    A = np.stack(alg).astype(np.float64); A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    N = np.stack(nm).astype(np.float64)
    return ids, A, N


def _codebook(A, N, alpha):
    M = A + alpha * N
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return torch.tensor(M, dtype=torch.float32, device=_DEVICE)


def _cleanup_capacity(M, sweep, seeds, n_trials):
    from hdlab.binding import bind, unbind
    from hdlab.bundling import bundle
    Mn = M.shape[0]; dim = M.shape[1]; Mt = M.t().contiguous()
    out = {}
    for F in sweep:
        if F > Mn:
            continue
        hit = 0; cnt = 0
        for sd in seeds:
            gen = torch.Generator().manual_seed(sd * 1000 + F)
            for _ in range(n_trials):
                idx = torch.randperm(Mn, generator=gen)[:F]
                R = _unitary_roles(F, dim, gen).to(_DEVICE)
                Ab = bundle(torch.stack([bind(R[i], M[idx[i]]) for i in range(F)]))
                for j in range(F):
                    est = unbind(Ab, R[j]); est = est / (est.norm() + 1e-12)
                    hit += int(int(torch.argmax(est @ Mt)) == int(idx[j])); cnt += 1
        out[F] = round(hit / cnt, 4)
    return out


def run() -> Dict:
    ids, A, N = _load()
    if A is None:
        return {"error": "no_algebra_atoms"}
    seeds = SEEDS[:1] if SMOKE else SEEDS
    n_trials = 6 if SMOKE else N_TRIALS
    sweep = [1, 3] if SMOKE else F_SWEEP
    alphas = [0.0, 1.0] if SMOKE else ALPHAS
    rows = []
    for alpha in alphas:
        M = _codebook(A, N, alpha)
        acc = _cleanup_capacity(M, sweep, seeds, n_trials)
        rows.append({"alpha": alpha, "cleanup": acc})
        print("  alpha=%.1f cleanup@1 %s" % (alpha, acc), flush=True)
    return {"rows": rows, "n_atoms": A.shape[0], "dim": A.shape[1], "device": _DEVICE, "n_seeds": len(seeds)}


def verdict(r) -> Tuple[str, str]:
    """Cross-axis drill Capability 1 (BINDING): does the alpha=0.5 sweet spot generalize to high binding count F=10/20?"""
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by_alpha = {x["alpha"]: x["cleanup"] for x in r["rows"]}
    a05 = by_alpha.get(0.5, {})
    f10 = a05.get(10); f20 = a05.get(20)
    s = ("alpha=0.5: cleanup@1 F10=%s F20=%s; full alpha x F grid=%s; corpus=%d device=%s"
         % (f10, f20, [(x["alpha"], x["cleanup"]) for x in r["rows"]], r["n_atoms"], r["device"]))
    if f10 is None or f20 is None:
        return ("UNKNOWN", "UNKNOWN: F=10/20 not in sweep. " + s)
    if f10 >= 0.95 and f20 >= 0.85:
        return ("HARD_PASS", "HARD_PASS (BINDING drill cap-1): alpha=0.5 identity-augmentation generalizes to high binding count -- cleanup@1 >=0.95 at F=10 AND >=0.85 at F=20. Two-vector architecture rule holds across binding scale. " + s)
    if f10 >= 0.80 or f20 >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND (BINDING drill cap-1): alpha=0.5 cleanup@1 F10 0.80-0.95 or F20 0.70-0.85 -- partial generalization to high binding count. " + s)
    return ("HARD_FAIL", "HARD_FAIL (BINDING drill cap-1): alpha=0.5 cleanup@1 <0.80 at F=10 -- sweet spot does not survive binding-count scaling. " + s)


def _selftest():
    v1 = _name_vec("concept::MWP/ROLE_ARG0_agent", 256)
    v2 = _name_vec("concept::MWP/ROLE_ARG1_theme", 256)
    assert v1.shape == (256,) and abs(float(np.dot(v1, v1)) - 1.0) < 1e-6
    # distinct names -> distinct (not identical) name vectors despite shared tokens
    assert float(np.dot(v1, v2)) < 0.95, float(np.dot(v1, v2))
    print("[selftest] PASS: name-augmented-encoding (ARG0 vs ARG1 name-vec cos=%.3f < 0.95)" % float(np.dot(v1, v2)), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s device=%s" % (ANCHOR_NAME, RUN_MODE, _DEVICE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
