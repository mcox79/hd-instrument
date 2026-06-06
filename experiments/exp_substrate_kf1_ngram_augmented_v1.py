"""
exp_substrate_kf1_ngram_augmented_v1 -- Slot G11: n-gram-augmented MiniLM for order-sensitive hallucination detection -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot G11. G2 found MiniLM bag-of-words -> word-shuffled hallucinations undetected (AUC 0.217).
  RESCUE: concat character-level n-gram (n=2,3,4) bag-of-features to the MiniLM embedding. Char n-grams at word boundaries
  CHANGE under word-shuffle -> the augmented grounding score drops for shuffled (false) facts -> detection recovers.
  Lightweight (no encoder swap). HP: AUC >= 0.80 on word-shuffled adversarial (vs 0.217 MiniLM-only). torch GPU (MiniLM).

PRE-REGISTERED bands: HARD-PASS AUC_adv >= 0.80 on word-shuffled. MIDDLE: 0.65-0.80. HARD-FAIL: < 0.65 (n-grams do not
  rescue order-sensitivity). Also report easy/hard tiers (must stay >=0.90).
FORMULA SELF-TESTS (PROT-022): 1. char n-gram changes under shuffle. 2. AUC monotonic. 3. cuda.
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
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_kf1_ngram_augmented_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"; MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
NG_DIM = 2048; NG_WEIGHT = 1.0
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_KB = 800; N_Q = 200; DROP = 0.3
else:
    SEEDS = [7, 17, 23]; N_KB = 4000; N_Q = 600; DROP = 0.3


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); tot = len(pos) * len(neg)
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg]))); rpos = ranks[:len(pos)].sum()
    return float((rpos - len(pos) * (len(pos) - 1) / 2) / max(tot, 1))


def char_ngram_vec(s, dim=NG_DIM):
    v = np.zeros(dim, dtype=np.float32); s = s.lower()
    for n in (2, 3, 4):
        for i in range(len(s) - n + 1):
            h = int(hashlib.md5(s[i:i + n].encode()).hexdigest(), 16) % dim; v[h] += 1.0
    nrm = np.linalg.norm(v); return v / nrm if nrm > 0 else v


def word_shuffle(s, g):
    w = s.split()
    if len(w) > 3:
        w = [w[i] for i in g.permutation(len(w))]
    return " ".join(w)


def word_drop(s, p, g):
    w = [x for x in s.split() if g.random() > p]; return " ".join(w) if w else s


def _selftest():
    g = np.random.default_rng(0); s = "john gave mary the heavy book today please"
    assert np.linalg.norm(char_ngram_vec(s) - char_ngram_vec(word_shuffle(s, g))) > 0.1, "char n-gram changes under shuffle"
    assert abs(auc([3, 4, 5], [0, 1, 2]) - 1.0) < 1e-6, "AUC monotonic"
    print("[selftest] PASS: ngram shuffle auc", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MINILM_ID); _M = AutoModel.from_pretrained(MINILM_ID).to(DEVICE).eval()


def enc_aug(texts):
    out = []
    for i in range(0, len(texts), 64):
        t = _TOK(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            h = _M(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float(); e = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        e = torch.nn.functional.normalize(e, dim=1).cpu().numpy()
        ng = np.stack([char_ngram_vec(s) for s in texts[i:i + 64]]) * NG_WEIGHT
        out.append(np.concatenate([e, ng], axis=1))                  # MiniLM (semantic) + char-ngram (order-sensitive)
    A = np.concatenate(out, 0).astype(np.float32); return A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-8)


def load_lines(f, n):
    out = []
    if f.exists():
        for l in open(f, encoding="utf-8"):
            r = json.loads(l); txt = (r.get("question") or " ".join(r.get("context", {}).get("contexts", [""]))).strip()
            if len(txt.split()) >= 5:
                out.append(txt[:300])
            if len(out) >= n:
                break
    return out


def run_seed(seed) -> Dict:
    g = np.random.default_rng(seed)
    pub = load_lines(PUBMED, N_KB + 2 * N_Q); med = load_lines(MEDQA, N_Q)
    kb = pub[:N_KB]; held = pub[N_KB:N_KB + N_Q]; Ekb = enc_aug(kb)
    src = [kb[i] for i in g.choice(len(kb), N_Q, replace=False)]
    sp = (enc_aug([word_drop(s, DROP, g) for s in src]) @ Ekb.T).max(1)
    ne = (enc_aug(med[:N_Q] if len(med) >= N_Q else med + pub[:N_Q - len(med)]) @ Ekb.T).max(1)
    nh = (enc_aug(held) @ Ekb.T).max(1)
    na = (enc_aug([word_shuffle(s, g) for s in src]) @ Ekb.T).max(1)
    return {"seed": seed, "auc_easy": auc(sp, ne), "auc_hard": auc(sp, nh), "auc_adv": auc(sp, na)}


def verdict(ps) -> Tuple[str, str]:
    aa = float(np.mean([p["auc_adv"] for p in ps])); ah = float(np.mean([p["auc_hard"] for p in ps])); ae = float(np.mean([p["auc_easy"] for p in ps]))
    summary = "AUC easy=%.3f hard=%.3f ADV(shuffled)=%.3f (MiniLM-only adv was 0.217)" % (ae, ah, aa)
    if aa >= 0.80:
        return ("HARD_PASS", "HARD_PASS: n-gram augmentation rescues word-order sensitivity (adv AUC>=0.80) -- lightweight Phase-4 order-sensitive detection. " + summary)
    if aa >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: n-gram partial rescue (adv 0.65-0.80). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: n-gram augmentation does not rescue order sensitivity (<0.65). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_KB=%d N_Q=%d ng_dim=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB, N_Q, NG_DIM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] easy=%.3f hard=%.3f adv=%.3f" % (seed, r["auc_easy"], r["auc_hard"], r["auc_adv"]), flush=True)
del _M; torch.cuda.empty_cache()
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
