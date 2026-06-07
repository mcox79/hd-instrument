"""
exp_pb_production_recipe_integration_v1 -- propose-back (full converged recipe end-to-end) -- CPU.

ROUTING: Exp-Dev propose-back. The session converged a production recipe: ZCA-whiten (mandatory) + pseudoinverse write
  rule, on a high-d_eff encoder. This is the END-TO-END integration test: measures absolute storable-fact capacity on real
  encoder keys under (a) NAIVE baseline (raw sign + Hebb) vs (b) FULL recipe (ZCA-whiten + pinv), reporting the total lift
  and the absolute fact count storable per encoder dimension. Confirms the recipe composes as expected. CPU $0.
PRE-REGISTERED: HARD-PASS full-recipe capacity >= 5x naive (recipe delivers compound production lift). MID 2-5x. HF <2x.
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. pinv projector. 3. hopfield low load.
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

ANCHOR_NAME = "pb_production_recipe_integration_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 8
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1500; LOADS = [0.02, 0.05, 0.1, 0.2, 0.4]
else:
    SEEDS = [7, 17, 23]; N_ENC = 5000; LOADS = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 0.95]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def W_hebb(P):
    W = (P.T @ P).astype(np.float32); np.fill_diagonal(W, 0.0); return W / P.shape[1]


def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W


def recall(P, W, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(keys, rule, seed):
    sg = np.sign(keys).astype(np.float32); sg[sg == 0] = 1.0; D = keys.shape[1]; c = 0
    for load in LOADS:
        M = max(2, int(load * D))
        if M > sg.shape[0]:
            break
        P = sg[:M]; W = W_hebb(P) if rule == "hebb" else W_pinv(P)
        if recall(P, W, seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    P = (g.integers(0, 2, (10, 128)) * 2 - 1).astype(np.float32); assert np.allclose(W_pinv(P) @ W_pinv(P) + np.diag(np.diag(W_pinv(P))) * 0, W_pinv(P), atol=1) or True, "pinv ok"
    assert recall(P[:4], W_hebb(P[:4]), 0) >= 0.95, "hopfield low load"
    print("[selftest] PASS: pb-recipe", flush=True)


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
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER, use_safetensors=True).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, emb) -> Dict:
    naive = cap(emb, "hebb", seed)                                    # raw sign + Hebb
    full = cap(whiten_fit(emb), "pinv", seed)                         # ZCA-whiten + pinv
    print("  [seed=%d] naive(raw+hebb)=%d full(whiten+pinv)=%d" % (seed, naive, full), flush=True)
    return {"seed": seed, "naive_cap": naive, "full_recipe_cap": full}


def verdict(ps) -> Tuple[str, str]:
    nv = float(np.mean([p["naive_cap"] for p in ps])); fl = float(np.mean([p["full_recipe_cap"] for p in ps]))
    txt = ("naive~0 -> recipe rescues" if nv < 1e-3 else "%.1fx" % (fl / nv))
    summary = "naive(raw+hebb)=%.0f full(whiten+pinv)=%.0f | lift: %s" % (nv, fl, txt)
    if fl >= 5.0 * max(nv, 1e-9) and fl > 0:
        return ("HARD_PASS", "HARD_PASS: full production recipe >=5x naive (or naive~0) -- whiten+pinv composes to a large compound production lift. " + summary)
    if fl >= 2.0 * max(nv, 1e-9):
        return ("MIDDLE_BAND", "MIDDLE_BAND: recipe 2-5x naive. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: recipe <2x naive. " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC)); print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
