"""
exp_hoc1_word_bigram_v1 -- Batch A Rank 1: WORD-bigram order-sensitive hallucination detection -- GPU(MiniLM)+CPU.

ROUTING: Research Batch A (cheapest decisive). G11 showed CHAR n-grams fail (survive word-shuffle). WORD bigrams DO
  capture word order. Augment MiniLM embedding with hashed WORD-bigram bag-of-features; test KF-1 grounding on the
  word-shuffle adversarial. Closes/routes the KF-1 negation/order production gate. AUC>=0.90 -> gate closes.
PRE-REGISTERED: HARD-PASS AUC_shuffle >= 0.90 (word bigrams rescue order sensitivity). MID 0.75-0.90. HF < 0.75.
FORMULA SELF-TESTS (PROT-022): 1. word-bigram vec changes under shuffle. 2. AUC monotonic. 3. encode.
ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "hoc1_word_bigram_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
WBG_DIM = 2048; WBG_W = 1.5; DROP = 0.3
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_KB = 800; N_Q = 200
else:
    SEEDS = [7, 17, 23]; N_KB = 4000; N_Q = 600


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); tot = len(pos) * len(neg)
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg]))); return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / max(tot, 1))


def wbg_vec(s, dim=WBG_DIM):
    w = s.lower().split(); v = np.zeros(dim, np.float32)
    for i in range(len(w) - 1):
        h = int(hashlib.md5((w[i] + " " + w[i + 1]).encode()).hexdigest(), 16) % dim; v[h] += 1.0
    nrm = np.linalg.norm(v); return v / nrm if nrm > 0 else v


def word_shuffle(s, g):
    w = s.split()
    if len(w) > 3:
        w = [w[i] for i in g.permutation(len(w))]
    return " ".join(w)


def word_drop(s, p, g):
    w = [x for x in s.split() if g.random() > p]; return " ".join(w) if w else s


def _selftest():
    g = np.random.default_rng(0); s = "alpha beta gamma delta epsilon zeta"
    assert np.linalg.norm(wbg_vec(s) - wbg_vec(word_shuffle(s, g))) > 0.1, "word-bigram changes under shuffle"
    assert abs(auc([3, 4], [0, 1]) - 1.0) < 1e-6, "AUC monotonic"
    print("[selftest] PASS: wbg auc", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[dev] %s" % DEV, flush=True)
_TOK = AutoTokenizer.from_pretrained(MINILM_ID); _M = AutoModel.from_pretrained(MINILM_ID).to(DEV).eval()


def enc_aug(texts):
    out = []
    for i in range(0, len(texts), 64):
        t = _TOK(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            h = _M(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float(); e = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        e = torch.nn.functional.normalize(e, dim=1).cpu().numpy()
        wb = np.stack([wbg_vec(s) for s in texts[i:i + 64]]) * WBG_W
        out.append(np.concatenate([e, wb], axis=1))
    A = np.concatenate(out, 0).astype(np.float32); return A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-8)


def load_lines(f, n):
    out = []
    if f.exists():
        for l in open(f, encoding="utf-8"):
            r = json.loads(l); txt = (r.get("question") or " ".join(r.get("context", {}).get("contexts", [""]))).strip()
            if len(txt.split()) >= 6:
                out.append(txt[:300])
            if len(out) >= n:
                break
    return out


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed); pub = load_lines(PUBMED, N_KB + N_Q)
    kb = pub[:N_KB]; Ekb = enc_aug(kb); src = [kb[i] for i in g.choice(len(kb), N_Q, replace=False)]
    sp = (enc_aug([word_drop(s, DROP, g) for s in src]) @ Ekb.T).max(1)
    na = (enc_aug([word_shuffle(s, g) for s in src]) @ Ekb.T).max(1)
    return {"seed": seed, "auc_shuffle": auc(sp, na)}


def verdict(ps) -> Tuple[str, str]:
    a = float(np.mean([p["auc_shuffle"] for p in ps]))
    summary = "AUC word-shuffle adversarial=%.3f (char-ngram G11 was 0.19; MiniLM-only 0.22)" % a
    if a >= 0.90:
        return ("HARD_PASS", "HARD_PASS: WORD bigrams rescue order-sensitive hallucination detection (AUC>=0.90) -- gate closes, no NLI needed. " + summary)
    if a >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: word bigrams partial (0.75-0.90); pair with NEG1. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: word bigrams insufficient (<0.75); NEG1/NLI mandatory. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_KB=%d N_Q=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r); print("  [seed=%d] auc_shuffle=%.3f" % (seed, r["auc_shuffle"]), flush=True)
del _M
if DEV.type == "cuda":
    torch.cuda.empty_cache()
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
