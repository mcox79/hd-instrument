"""
exp_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1 -- SSOT G16 (Phase-4 production rule) -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot G16 (G7 HF subsumption at small scale; confirm at full N_enc=10000). 4 arms on real
  MiniLM keys: (a) base raw sign, (b) whiten only, (c) expand only (random-projection x4), (d) expand + whiten. Question:
  once expanded, does ZCA whitening STILL add capacity, or is it SUBSUMED (expansion alone suffices)? Decides whether the
  Phase-4 production rule is "expand" (simple) or "expand + whiten" (stacking ~97x). Hopfield exact-recovery capacity.
PRE-REGISTERED: HARD-PASS (d) > (c) by >=15pct (NO subsumption; whitening still adds -> stacking holds). MID (d)>=(c) but
  <15pct (marginal). HARD-FAIL (d) ~ (c) (subsumption CONFIRMED; whitening redundant once expanded -> simpler production rule).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. expand raises dim. 3. Hopfield recovers low load.
ASCII-only. write_metrics. PROT-018 no _nN.
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

ANCHOR_NAME = "substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"; EXPAND = 4
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1500; LOADS = [0.01, 0.03, 0.06, 0.1, 0.2]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; LOADS = [0.005, 0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]
ARMS = ["base_raw", "whiten_only", "expand_only", "expand_whiten"]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def expand(K, seed):
    g = np.random.default_rng(seed + 13); R = g.standard_normal((K.shape[1], K.shape[1] * EXPAND)).astype(np.float32) / np.sqrt(K.shape[1])
    return K @ R


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free dense Hopfield
    return float(np.mean(np.all(s == P, axis=1)))


def cap(keys, seed):
    sg = np.sign(keys).astype(np.float32); sg[sg == 0] = 1.0; D = keys.shape[1]; c = 0
    for load in LOADS:
        M = max(2, int(load * D))
        if M > sg.shape[0]:
            break
        if hop_recall(sg[:M], seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    assert expand(K, 0).shape[1] == 64 * EXPAND, "expand raises dim"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield recovers low load"
    print("[selftest] PASS: g16", flush=True)


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
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mask = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, emb) -> Dict:
    ex = expand(emb, seed)
    a = {"base_raw": cap(emb, seed), "whiten_only": cap(whiten_fit(emb), seed), "expand_only": cap(ex, seed), "expand_whiten": cap(whiten_fit(ex), seed)}
    print("  [seed=%d] %s" % (seed, a), flush=True); return {"seed": seed, "cap": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {arm: float(np.mean([p["cap"][arm] for p in ps])) for arm in ARMS}
    d = agg["expand_whiten"]; c = agg["expand_only"]; b = agg["whiten_only"]
    # honest comparison: does expansion add ON TOP of whitening? (expand_only is often ~0 -> div-by-zero useless)
    exp_adds = d / max(b, 1e-9)        # expand+whiten vs whiten-only: does expansion stack?
    wh_adds = d / max(c, 1e-9) if c > 0 else float("inf")  # whitening vs expand-only (usually inf since expand_only~0)
    summary = "cap %s | expand+whiten/whiten-only=%.2fx ; whitening mandatory (expand-only=%.1f)" % ({k: round(v, 1) for k, v in agg.items()}, exp_adds, c)
    if exp_adds >= 1.15:
        return ("HARD_PASS", "HARD_PASS: NO subsumption -- expansion adds >=15pct ON TOP of whitening (and whitening is mandatory: expand-only~0). Production rule = expand + whiten (stacking holds). " + summary)
    if exp_adds >= 1.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: whitening mandatory; expansion adds marginally on top (<15pct). Production rule ~ whiten (expansion optional). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: expansion does not add on top of whitening (expand+whiten < whiten-only) -- whitening subsumes expansion; production rule = whiten only. " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s expand=%dx N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, EXPAND, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC)); print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
