"""
exp_pb_crt_real_encoder_atoms_v1 -- propose-back (does CRT multi-scale composition survive REAL-encoder atoms) -- GPU.

ROUTING: Exp-Dev propose-back. crt_multi_scale_grid_cell found multiplicative position capacity with RANDOM bipolar residue
  atoms. Open question: does the CRT composition survive when the residue atoms are REAL encoder-derived codes (correlated,
  anisotropic) instead of random? Builds residue codebooks from sign(ZCA-whiten(real MiniLM embeddings)) and re-runs the
  single-vs-3-scale distinguishability test; compares to a random-atom control. If real atoms still give multiplicative
  range, CRT positional addressing is deployable on real-encoder substrates. GPU (encoder forward).
PRE-REGISTERED: HARD-PASS real-atom 3-scale distinguishable >= 2x single-scale AND >= 0.8x the random-atom 3-scale
  (composition robust to real geometry). MID 1.3-2x. HARD-FAIL <1.3x (real-atom correlation breaks CRT).
FORMULA SELF-TESTS (PROT-022): 1. CRT uniqueness over coprime product. 2. coprime moduli. 3. whiten preserves dim.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pb_crt_real_encoder_atoms_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
MODULI = [7, 11, 13]; FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def encode_pos(pos, scales, codebooks):
    v = np.zeros(codebooks[0].shape[1], np.float32)
    for s, m in enumerate(scales):
        v += codebooks[s][pos % m]
    return np.sign(v)


def distinguishable(scales, codebooks, seed):
    P = int(np.prod(scales))
    codes = np.stack([encode_pos(p, scales, codebooks) for p in range(P)])
    ok = 0; g2 = np.random.default_rng(seed + 1); N = codes.shape[1]
    for p in range(P):
        cue = codes[p] * np.where(g2.random(N) < FLIP, -1.0, 1.0)
        if int(np.argmax(codes @ cue)) == p:
            ok += 1
    return ok


def _selftest():
    from math import gcd
    assert gcd(7, 11) == 1 and gcd(11, 13) == 1 and gcd(7, 13) == 1, "coprime moduli"
    assert len(set((p % 7, p % 11, p % 13) for p in range(7 * 11 * 13))) == 7 * 11 * 13, "CRT uniqueness"
    assert whiten_fit(np.random.default_rng(0).standard_normal((40, 16))).shape == (40, 16), "whiten preserves dim"
    print("[selftest] PASS: crt-real-atoms", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n:
                    return out
    return out


def encode(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def real_codebooks(atoms, scales, seed):
    # carve disjoint blocks of real sign-atoms, one block per scale
    g = np.random.default_rng(seed); perm = g.permutation(len(atoms)); off = 0; cbs = []
    for m in scales:
        cbs.append(atoms[perm[off:off + m]]); off += m
    return cbs


def rand_codebooks(N, scales, seed):
    g = np.random.default_rng(seed); return [(g.integers(0, 2, (m, N)) * 2 - 1).astype(np.float32) for m in scales]


def run_seed(atoms, seed) -> Dict:
    N = atoms.shape[1]
    real1 = distinguishable([MODULI[0]], real_codebooks(atoms, [MODULI[0]], seed), seed)
    real3 = distinguishable(MODULI, real_codebooks(atoms, MODULI, seed), seed)
    rnd3 = distinguishable(MODULI, rand_codebooks(N, MODULI, seed), seed)
    print("  [seed=%d] real 1-scale=%d real 3-scale=%d rand 3-scale=%d (product=%d)" % (seed, real1, real3, rnd3, int(np.prod(MODULI))), flush=True)
    return {"seed": seed, "real_single": real1, "real_three": real3, "rand_three": rnd3}


def verdict(ps) -> Tuple[str, str]:
    r1 = float(np.mean([p["real_single"] for p in ps])); r3 = float(np.mean([p["real_three"] for p in ps])); n3 = float(np.mean([p["rand_three"] for p in ps]))
    gain = r3 / max(r1, 1e-9); vs_rand = r3 / max(n3, 1e-9); prod = int(np.prod(MODULI))
    summary = "real 1-scale=%.0f real 3-scale=%.0f rand 3-scale=%.0f (CRT product=%d) | 3/1=%.2fx real/rand=%.2f" % (r1, r3, n3, prod, gain, vs_rand)
    if gain >= 2.0 and vs_rand >= 0.8:
        return ("HARD_PASS", "HARD_PASS: CRT multiplicative composition survives real-encoder atoms (>=2x single, >=0.8x random) -- positional addressing deployable on real substrates. " + summary)
    if gain >= 1.3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: real-atom CRT helps (1.3-2x) but degraded vs random. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: real-atom correlation breaks CRT composition (<1.3x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s moduli=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, MODULI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
emb = encode(load_texts(sum(MODULI) + 50)); atoms = np.sign(whiten_fit(emb)).astype(np.float32); atoms[atoms == 0] = 1.0
ps = [run_seed(atoms, s) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
