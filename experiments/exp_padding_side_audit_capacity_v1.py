"""
exp_padding_side_audit_capacity_v1 -- Batch E Cell 4 (TAX-2; may explain last-token=0 anomaly) -- CPU.

ROUTING: Batch E Drill-4 anchor C. HuggingFace tokenizers default to RIGHT padding; naive last-token pooling at position
  -1 then extracts a PAD embedding (~0) for any sequence shorter than the batch max -> may ENTIRELY explain cycle-138's
  "last-token raw cap=0" anomaly. Audits 3 extraction modes on Pythia-160m (cached causal LM): (a) right-pad + position[-1]
  (the buggy default), (b) right-pad + last-REAL-token via attention mask (correct), (c) left-pad + position[-1] (also
  correct). Capacity (Hopfield exact-recovery on sign keys). CPU $0.
PRE-REGISTERED: HARD-PASS (a) cap ~0 while (b),(c) cap >> 0 -- confirms right-pad+pos[-1] extracts PAD (the anomaly).
  MID partial. HARD-FAIL all three similar (padding side is NOT the anomaly cause).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. Hopfield low load. 3. deps.
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

ANCHOR_NAME = "padding_side_audit_capacity_v1"
ENCODER = "EleutherAI/pythia-160m"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 600; LOADS = [0.02, 0.05, 0.1, 0.2]
else:
    SEEDS = [7, 17, 23]; N_ENC = 3000; LOADS = [0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]
ARMS = ["rightpad_pos_neg1_BUG", "rightpad_lastreal_OK", "leftpad_pos_neg1_OK"]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(emb, seed):
    sg = np.sign(whiten_fit(emb)).astype(np.float32); sg[sg == 0] = 1.0; D = emb.shape[1]; c = 0
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
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield low load"
    print("[selftest] PASS: padding-audit", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
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


def encode(texts, side):
    tok = AutoTokenizer.from_pretrained(ENCODER); tok.pad_token = tok.eos_token; tok.padding_side = side
    m = AutoModelForCausalLM.from_pretrained(ENCODER, output_hidden_states=True).to(DEV).eval()
    pos_neg1, lastreal = [], []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            h = m(**t).hidden_states[-1]
        pos_neg1.append(h[:, -1, :].cpu().numpy())                   # naive last position
        lens = t["attention_mask"].sum(1) - 1; lastreal.append(h[torch.arange(h.shape[0]), lens].cpu().numpy())  # last real token
    del m
    return np.concatenate(pos_neg1, 0).astype(np.float32), np.concatenate(lastreal, 0).astype(np.float32)


def run_seed(seed, arms_emb) -> Dict:
    a = {arm: cap(arms_emb[arm], seed) for arm in ARMS}
    print("  [seed=%d] %s" % (seed, a), flush=True); return {"seed": seed, "cap": a}


def verdict(ps) -> Tuple[str, str]:
    agg = {arm: float(np.mean([p["cap"][arm] for p in ps])) for arm in ARMS}
    bug = agg["rightpad_pos_neg1_BUG"]; ok = max(agg["rightpad_lastreal_OK"], agg["leftpad_pos_neg1_OK"])
    summary = "cap %s" % {k: round(v, 1) for k, v in agg.items()}
    if ok >= 2.0 * max(bug, 1e-6) and ok > 0:
        return ("HARD_PASS", "HARD_PASS: right-pad + position[-1] extracts PAD (cap~0) while correct extraction works -- THIS explains the last-token=0 anomaly; fix = mask-aware last-token or left-pad. " + summary)
    if ok >= 1.3 * max(bug, 1e-6):
        return ("MIDDLE_BAND", "MIDDLE_BAND: padding side matters partially. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: padding side is NOT the anomaly cause (all similar). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); texts = load_texts(N_ENC)
rp_neg1, rp_real = encode(texts, "right"); lp_neg1, _ = encode(texts, "left")
arms_emb = {"rightpad_pos_neg1_BUG": rp_neg1, "rightpad_lastreal_OK": rp_real, "leftpad_pos_neg1_OK": lp_neg1}
print("[encoded] %s" % (rp_neg1.shape,), flush=True)
ps = [run_seed(s, arms_emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
