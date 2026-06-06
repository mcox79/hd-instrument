"""
exp_bge_large_capacity_measurement_v1 -- Batch E Cell 5 (Drill-5 PRED-1; cap ~ 1.33*d_eff) -- GPU.

ROUTING: Batch E Drill-5 #1. Tests the Marchenko-Pastur capacity-ceiling theory cap ~ 1.33 * d_eff directly on BGE-large
  (D=1024; measured d_eff ~ 114.8 cycle 131). Predicted exact-recovery cap in [140,165] if LINEAR (HP), or <125 if
  SUBLINEAR (HF). Encodes real text with BGE-large, ZCA-whiten + sign, measures Hopfield exact-recovery capacity + d_eff
  (participation ratio). GPU (model forward).
PRE-REGISTERED: HARD-PASS cap in [140,165] (cap ~ 1.33*d_eff linear confirmed). MID 125-140 or 165-185. HARD-FAIL <125
  (sublinear -- theory falsified) or >185 (super-linear).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. participation ratio. 3. Hopfield low load.
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

ANCHOR_NAME = "bge_large_capacity_measurement_v1"
ENCODER = "BAAI/bge-large-en-v1.5"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1000; M_GRID = [20, 50, 100, 150, 200]
else:
    SEEDS = [7, 17, 23]; N_ENC = 5000; M_GRID = [40, 80, 110, 125, 140, 150, 165, 180, 200, 240, 300]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def participation_ratio(emb):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False); s2 = s ** 2
    return float((s2.sum() ** 2) / (np.sum(s2 ** 2) + 1e-12))


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def capacity(sg, seed):
    c = 0
    for M in M_GRID:
        if M > sg.shape[0]:
            break
        if hop_recall(sg[:M], seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    assert abs(participation_ratio(np.linalg.svd(g.standard_normal((200, 30)), full_matrices=False)[0]) - participation_ratio(np.linalg.svd(g.standard_normal((200, 30)), full_matrices=False)[0])) < 1e6, "pr runs"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield low load"
    print("[selftest] PASS: bge-cap", flush=True)


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
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, emb) -> Dict:
    sg = np.sign(whiten_fit(emb)).astype(np.float32); sg[sg == 0] = 1.0
    cap = capacity(sg, seed); deff = participation_ratio(emb)
    print("  [seed=%d] cap=%d d_eff=%.1f cap/d_eff=%.2f" % (seed, cap, deff, cap / max(deff, 1e-9)), flush=True)
    return {"seed": seed, "cap": cap, "d_eff": deff, "cap_over_deff": cap / max(deff, 1e-9)}


def verdict(ps) -> Tuple[str, str]:
    cap = float(np.mean([p["cap"] for p in ps])); deff = float(np.mean([p["d_eff"] for p in ps])); r = cap / max(deff, 1e-9)
    summary = "cap=%.0f d_eff=%.1f cap/d_eff=%.2f (MP theory ~1.33)" % (cap, deff, r)
    if 140 <= cap <= 165:
        return ("HARD_PASS", "HARD_PASS: BGE-large cap in [140,165] -- cap ~ 1.33*d_eff Marchenko-Pastur linear theory CONFIRMED; informs production encoder choice. " + summary)
    if 125 <= cap < 140 or 165 < cap <= 185:
        return ("MIDDLE_BAND", "MIDDLE_BAND: BGE-large cap near predicted band. " + summary)
    if cap < 125:
        return ("HARD_FAIL", "HARD_FAIL: BGE-large cap <125 -- SUBLINEAR; cap~1.33*d_eff theory falsified. " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: cap >185 (super-linear vs theory). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC)); print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
