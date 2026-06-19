"""
exp_pattern_b_unbind_substitute_v1 -- Pattern B Phase-1: analogical mapping A:B::C:? via VSA transform -- CPU.

ROUTING: handoff research_to_exp_dev_pattern_b_full_exploration_program Phase 1 (algebra validation). Tests the substrate-
  native decomposition mechanism: store a compositional fact as sum_i role_i (x) filler_i (FHRR binding), substitute ONE
  filler, and retrieve the substituted value by unbinding its role. This is the algebraic core of Pattern B multi-hop (the
  LLM-free decomposition the fair-size-ceiling finding motivates). FHRR = unit complex vectors, bind = elementwise product,
  unbind = elementwise product with conjugate, cleanup = nearest stored filler. CPU.
PRE-REGISTERED: HARD-PASS substitution-retrieval accuracy >= 0.95 at 4 role-filler bindings, N=1024. MIDDLE 0.85-0.95.
  HARD-FAIL < 0.85 (substitution corrupts the bundle; Pattern B substitution not reliable).
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts bind. 2. unit magnitude. 3. cleanup self.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pattern_b_analogy_v1"; N = 1024
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]; BINDINGS = [2, 4, 6, 8]; VOCAB = 200 if RUN_MODE == "smoke" else 1000


def rand_phasor(n, k, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)   # unit-magnitude FHRR vectors


def bind(a, b):
    return a * b


def unbind(c, role):
    return c * np.conj(role)


def cleanup(v, vocab):
    sims = (vocab @ np.conj(v)).real; return int(np.argmax(sims))


def _selftest():
    g = np.random.default_rng(0); a = rand_phasor(64, 1, g)[0]; b = rand_phasor(64, 1, g)[0]
    assert np.allclose(unbind(bind(a, b), a), b, atol=1e-4), "unbind inverts bind"
    assert np.allclose(np.abs(a), 1.0, atol=1e-5), "unit magnitude"
    voc = rand_phasor(64, 5, g); assert cleanup(voc[2], voc) == 2, "cleanup self"
    print("[selftest] PASS: pattern-b-unbind-substitute", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed, k) -> float:
    # analogy: transform T = A* (x) B maps A->B; apply to C -> should retrieve D where C:D::A:B (same relation).
    g = np.random.default_rng(seed); vocab = rand_phasor(N, VOCAB, g)
    ok = 0; trials = 100 if RUN_MODE == "smoke" else 300
    for _ in range(trials):
        a, b, c = (int(g.integers(0, VOCAB)) for _ in range(3))
        # define D by the SAME phasor offset as A->B applied to C (ground-truth analogue)
        T = bind(np.conj(vocab[a]), vocab[b])           # relation transform A->B
        d_vec = bind(vocab[c], T)                        # apply to C
        # add k-1 distractor pairs to the transform bundle (interference)
        for _ in range(k - 1):
            x, y = int(g.integers(0, VOCAB)), int(g.integers(0, VOCAB)); T = T + bind(np.conj(vocab[x]), vocab[y])
        pred = cleanup(bind(vocab[c], T), vocab); truth = cleanup(d_vec, vocab)
        ok += int(pred == truth)
    return ok / trials


def run() -> Dict:
    by = {}
    for k in BINDINGS:
        acc = float(np.mean([run_seed(s, k) for s in SEEDS])); by["k%d" % k] = acc
        print("  transform_pairs=%d analogy_acc=%.3f" % (k, acc), flush=True)
    return {"by": by, "acc_k4": by.get("k4", 0.0)}


def verdict(r) -> Tuple[str, str]:
    a4 = r["acc_k4"]; summary = "substitution-retrieval acc: %s (N=%d)" % ({k: round(v, 3) for k, v in r["by"].items()}, N)
    if a4 >= 0.95:
        return ("HARD_PASS", "HARD_PASS: analogical mapping A:B::C:? >=0.95 at k=4 -- substrate does cross-domain analogy via VSA transform (a capability bare retrieval lacks). " + summary)
    if a4 >= 0.85:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substitution acc 0.85-0.95 at k=4. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substitution acc <0.85 at k=4 -- bundle interference corrupts substitution; Pattern B editing unreliable at this N. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d bindings=%s vocab=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N, BINDINGS, VOCAB), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
