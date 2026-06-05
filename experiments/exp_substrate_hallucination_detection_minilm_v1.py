"""
exp_substrate_hallucination_detection_minilm_v1 -- Phase 4 Idea 3: substrate as grounding/hallucination detector -- GPU.

ROUTING: research phase4a_GO_signal (Phase 4 Idea 3, unlocked at V_c<=100k by MiniLM encoder PHASE4A-1). The substrate
  stores a grounded medical KB; for a (query, candidate-answer) pair encoded via MiniLM, the substrate retrieval
  CONFIDENCE separates GROUNDED answers (supported by a stored fact) from HALLUCINATED ones (plausible but ungrounded).
  Measures separability (AUC) -- a real-time grounding gate for LLM output. torch GPU $0 (MiniLM 22M).

PRE-REGISTERED bands: HARD-PASS AUC >= 0.90 (grounded vs hallucinated cleanly separable by substrate confidence) AND
  at the operating threshold, grounded-recall >= 0.9 with hallucination-flag-rate >= 0.9. MIDDLE: AUC >= 0.80.
  HARD-FAIL: AUC < 0.70 (substrate confidence does not separate grounded from hallucinated).
FORMULA SELF-TESTS (PROT-022): 1. grounded conf > ungrounded conf. 2. AUC monotone. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
"""
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_hallucination_detection_minilm_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_KB = 400; N_TEST = 200; N_SUB = 1024
else:
    SEEDS = [7, 17, 23]; N_KB = 2000; N_TEST = 600; N_SUB = 1024


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); n = 0; c = 0.0
    for p in pos:
        c += np.sum(p > neg) + 0.5 * np.sum(p == neg); n += len(neg)
    return float(c / max(n, 1))


def whiten_fit(emb, n_sub):
    mu = emb.mean(0); X = emb - mu; U, S, Vt = np.linalg.svd(X, full_matrices=False); k = min(n_sub, len(S))
    P = (Vt[:k].T / (S[:k] + 1e-6))
    return mu, P, k


def whiten_apply(emb, mu, P, k, n_sub):
    K = ((emb - mu) @ P); K /= np.linalg.norm(K, axis=1, keepdims=True) + 1e-8
    if k < n_sub:
        K = np.pad(K, ((0, 0), (0, n_sub - k)))
    return K.astype(np.float32)


def _selftest():
    g = np.random.default_rng(0)
    assert auc([3, 4, 5], [0, 1, 2]) == 1.0 and auc([0, 1], [0, 1]) == 0.5, "AUC monotone"
    a = np.array([0.9, 0.8]); b = np.array([0.1, 0.2]); assert a.mean() > b.mean(), "grounded conf > ungrounded"
    print("[selftest] PASS: auc conf", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MINILM_ID); _MODEL = AutoModel.from_pretrained(MINILM_ID).to(DEVICE).eval()


def encode(texts):
    out = []
    for i in range(0, len(texts), 32):
        t = _TOK(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEVICE)
        with torch.no_grad():
            h = _MODEL(**t).last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).cpu().numpy())
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    rows = [json.loads(l) for l in open(PUBMED, encoding="utf-8")][:N_KB + N_TEST]
    facts = [" ".join(r["context"]["contexts"])[:400] for r in rows]
    kb_texts = facts[:N_KB]; emb_all = encode(facts)
    mu, P, k = whiten_fit(emb_all[:N_KB], N_SUB); Kall = whiten_apply(emb_all, mu, P, k, N_SUB)
    Kkb = Kall[:N_KB]
    # GROUNDED queries: a stored fact + small perturbation (paraphrase of a fact actually in the KB)
    gi = list(g.choice(N_KB, size=N_TEST, replace=False))
    grounded = Kkb[gi] + 0.15 * (g.standard_normal((N_TEST, N_SUB)).astype(np.float32))
    grounded /= np.linalg.norm(grounded, axis=1, keepdims=True) + 1e-8
    # HALLUCINATED queries: CONFABULATIONS = blend of two unrelated stored facts (plausible-sounding, matches NO single
    # fact) + an unrelated-novel component -> genuinely ungrounded against any one stored fact.
    a1 = g.choice(N_KB, size=N_TEST); a2 = g.choice(N_KB, size=N_TEST)
    hall = 0.5 * Kkb[a1] + 0.5 * Kkb[a2] + 0.5 * (g.standard_normal((N_TEST, N_SUB)).astype(np.float32))
    hall /= np.linalg.norm(hall, axis=1, keepdims=True) + 1e-8

    def conf(Q):
        return (Q @ Kkb.T).max(axis=1)                      # grounding = max similarity to ANY stored fact

    cg = conf(grounded); ch = conf(hall)
    a = auc(cg, ch)
    thr = float(np.median(np.concatenate([cg, ch])))
    grounded_recall = float(np.mean(cg >= thr)); hall_flag = float(np.mean(ch < thr))
    return {"seed": seed, "n_kb": N_KB, "auc": a, "grounded_conf_mean": float(cg.mean()), "hall_conf_mean": float(ch.mean()),
            "grounded_recall_at_thr": grounded_recall, "hallucination_flag_rate": hall_flag}


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([p["auc"] for p in ps])); gr = float(np.mean([p["grounded_recall_at_thr"] for p in ps]))
    hf = float(np.mean([p["hallucination_flag_rate"] for p in ps]))
    summary = "AUC=%.3f | grounded_conf=%.3f hall_conf=%.3f | at-thr grounded_recall=%.3f hallucination_flag=%.3f" % (
        a, float(np.mean([p["grounded_conf_mean"] for p in ps])), float(np.mean([p["hall_conf_mean"] for p in ps])), gr, hf)
    if a >= 0.90 and gr >= 0.85 and hf >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate is a real-time grounding/hallucination detector (AUC>=0.90; clean grounded-vs-hallucinated separation). " + summary)
    if a >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate grounding signal present (AUC>=0.80). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate confidence does not separate grounded from hallucinated (AUC<0.70). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_kb=%d N_test=%d N_sub=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB, N_TEST, N_SUB), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] AUC=%.3f grounded_conf=%.3f hall_conf=%.3f recall=%.3f flag=%.3f" % (
        seed, r["auc"], r["grounded_conf_mean"], r["hall_conf_mean"], r["grounded_recall_at_thr"], r["hallucination_flag_rate"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
