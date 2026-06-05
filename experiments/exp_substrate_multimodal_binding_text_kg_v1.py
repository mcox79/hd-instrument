"""
substrate_multimodal_binding_text_kg_v1 -- HP-9: multi-modal substrate binding (text + KG) -- CPU.

ROUTING: research envelope HP-9 + HP-9 architectural update (cross-modal BayesRAG/Kalman). Tests substrate's VSA
  binding as MODALITY-AGNOSTIC: bind text-concept <-> KG-entity in one substrate; cross-modal query (text->KG and
  KG->text) recovers the paired item. Plus cross-modal evidence combination (retrieve from text substrate + KG
  substrate, Rule-8 combine by cosine). Validates substrate handles a NEW modality dimension. CPU numpy $0 (no faiss).

PRE-REGISTERED bands: HARD-PASS cross-modal recovery (text->KG and KG->text) >= 0.90 AND cross-modal-combine >= single-
  modality. MIDDLE: recovery >= 0.70. HARD-FAIL: < 0.70 (binding not modality-agnostic).
FORMULA SELF-TESTS (PROT-022): 1. VSA bind/unbind cross-modal. 2. cleanup. 3. N=4096.
ASCII-only. write_metrics. PROT-018 _n4096 -> N=4096.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_multimodal_binding_text_kg_v1"
_N_SUFFIX = 4096; N = 4096; assert N == _N_SUFFIX
LR = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1, 2]; N_DIM = 1024; M_PAIRS = 300
else:
    SEEDS = [7, 17, 23]; N_DIM = N; M_PAIRS = 2000


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def cfrpe(W, k, v, n):
    W += (LR / n) * np.outer(v - W @ k, k)


def _selftest():
    g = np.random.default_rng(0); n = 256; T = bp(3, n, g); KG = bp(3, n, g)   # text + KG modalities
    W = np.zeros((n, n), dtype=np.float32)
    for i in range(3):
        cfrpe(W, T[i], KG[i], n)                            # bind text_i -> kg_i (heteroassoc)
    pred = int(np.argmax(KG @ (W @ T[1]))); assert pred == 1, "VSA cross-modal text->KG"
    assert N == 4096; print("[selftest] PASS: cross-modal bind cleanup", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); n = N_DIM; M = M_PAIRS
    T = bp(M, n, g); KG = bp(M, n, g)                       # paired text-concepts <-> KG-entities
    # bidirectional cross-modal store
    Wtk = (KG.T @ T).astype(np.float32)                    # text -> KG (batched Hebbian)
    Wkt = (T.T @ KG).astype(np.float32)                    # KG -> text
    ev = list(g.choice(M, size=min(300, M), replace=False))
    # cross-modal recovery from NOISY cue (modality-agnostic)
    t2kg = np.mean([int(np.argmax(KG @ (Wtk @ (T[i] + 0.5 * bp(1, n, g)[0])))) == i for i in ev])
    kg2t = np.mean([int(np.argmax(T @ (Wkt @ (KG[i] + 0.5 * bp(1, n, g)[0])))) == i for i in ev])
    # cross-modal EVIDENCE COMBINE (text-cue + KG-cue both point to target i; combine beats single modality)
    single = combine = 0
    for i in ev:
        tc = T[i] + 1.5 * bp(1, n, g)[0]; kc = KG[i] + 1.5 * bp(1, n, g)[0]      # noisy cues in both modalities
        s_text = T @ tc; s_kg = T @ (Wkt @ kc)                                    # both score over text space
        single += int(int(np.argmax(s_text)) == i)
        cs = s_text / (np.linalg.norm(s_text) + 1e-8) + s_kg / (np.linalg.norm(s_kg) + 1e-8)   # cross-modal combine
        combine += int(int(np.argmax(cs)) == i)
    return {"seed": seed, "M_pairs": M, "text_to_kg": float(t2kg), "kg_to_text": float(kg2t),
            "single_modality": float(single / len(ev)), "cross_modal_combine": float(combine / len(ev))}


def verdict(ps) -> Tuple[str, str]:
    t2k = float(np.mean([p["text_to_kg"] for p in ps])); k2t = float(np.mean([p["kg_to_text"] for p in ps]))
    sm = float(np.mean([p["single_modality"] for p in ps])); cm = float(np.mean([p["cross_modal_combine"] for p in ps]))
    summary = "text->KG=%.3f KG->text=%.3f | cross-modal-combine=%.3f vs single-modality=%.3f (M=%d)" % (t2k, k2t, cm, sm, ps[0]["M_pairs"])
    if min(t2k, k2t) >= 0.90 and cm >= sm:
        return ("HARD_PASS", "HARD_PASS: substrate VSA binding is modality-agnostic (text<->KG cross-modal recovery + combine helps). " + summary)
    if min(t2k, k2t) >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial cross-modal binding. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: binding not modality-agnostic. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N=%d M_pairs=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_PAIRS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] text->KG=%.3f KG->text=%.3f | combine=%.3f single=%.3f" % (seed, r["text_to_kg"], r["kg_to_text"], r["cross_modal_combine"], r["single_modality"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "N": N_DIM, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
