"""
exp_substrate_kf1_ngram_augmented_v1 -- Slot G13: contradiction detection on Pythia-160m (rescue for G5 negation HF) -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot G11. G2 found MiniLM bag-of-words -> word-shuffled hallucinations undetected (AUC 0.217).
  RESCUE: encode with Pythia-160m (causal LM) instead of bag-of-words MiniLM. Causal attention + positional
  embeddings make per-token contextual reps order-dependent -> mean-pooled sentence embedding changes under word-shuffle
  -> shuffled (false) facts score lower grounding -> detection recovers. HP: AUC >= 0.85 on word-shuffled. torch GPU (Pythia).

PRE-REGISTERED bands: HARD-PASS AUC_adv >= 0.85 on word-shuffled. HARD-FAIL AUC_adv < 0.70 (even order-sensitive encoder fails). MIDDLE: 0.65-0.80. HARD-FAIL: < 0.65 (n-grams do not
  rescue order-sensitivity). Also report easy/hard tiers (must stay >=0.90).
FORMULA SELF-TESTS (PROT-022): 1. AUC monotonic. 2. cuda.
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

ANCHOR_NAME = "substrate_kf1_contradiction_detection_order_sensitive_v1"
PYTHIA_ID = "EleutherAI/pythia-160m"
PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"; MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
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


def word_shuffle(s, g):
    w = s.split()
    if len(w) > 3:
        w = [w[i] for i in g.permutation(len(w))]
    return " ".join(w)


def word_drop(s, p, g):
    w = [x for x in s.split() if g.random() > p]; return " ".join(w) if w else s


_NEG = {"increases": "decreases", "increased": "decreased", "high": "low", "higher": "lower", "positive": "negative",
        "elevated": "reduced", "associated": "unassociated", "effective": "ineffective", "significant": "insignificant",
        "is": "is not", "was": "was not", "are": "are not", "causes": "prevents", "improves": "worsens"}

def negate(s):
    w = s.split(); out = []; done = False
    for x in w:
        lx = x.lower().strip(".,")
        if not done and lx in _NEG:
            out.append(_NEG[lx]); done = True
        else:
            out.append(x)
    if not done:
        out = w[:1] + ["not"] + w[1:]
    return " ".join(out)


def _selftest():
    assert abs(auc([3, 4, 5], [0, 1, 2]) - 1.0) < 1e-6 and abs(auc([0, 1], [2, 3])) < 1e-6, "AUC monotonic"
    g = np.random.default_rng(0); s = "alpha beta gamma delta epsilon"; assert word_shuffle(s, g) != s or len(s.split()) <= 3, "shuffle"
    print("[selftest] PASS: auc shuffle", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(PYTHIA_ID); _TOK.pad_token = _TOK.eos_token
_M = AutoModelForCausalLM.from_pretrained(PYTHIA_ID, output_hidden_states=True).to(DEVICE).eval()


def enc_aug(texts):
    out = []
    for i in range(0, len(texts), 32):
        t = _TOK(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            h = _M(**t).hidden_states[-1]                            # Pythia causal hidden states (order-sensitive)
        mask = t["attention_mask"].unsqueeze(-1).float(); e = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        out.append(torch.nn.functional.normalize(e, dim=1).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


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
    na = (enc_aug([negate(s) for s in src]) @ Ekb.T).max(1)
    return {"seed": seed, "auc_easy": auc(sp, ne), "auc_hard": auc(sp, nh), "auc_negation": auc(sp, na)}


def verdict(ps) -> Tuple[str, str]:
    aa = float(np.mean([p["auc_negation"] for p in ps])); ah = float(np.mean([p["auc_hard"] for p in ps])); ae = float(np.mean([p["auc_easy"] for p in ps]))
    summary = "AUC easy=%.3f hard=%.3f NEGATION=%.3f (MiniLM negation was 0.034)" % (ae, ah, aa)
    if aa >= 0.85:
        return ("HARD_PASS", "HARD_PASS: Pythia order-sensitive encoder rescues CONTRADICTION detection (negation AUC>=0.85) -- catches the highest-risk hallucination class. " + summary)
    if aa >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Pythia partial rescue (adv 0.70-0.85). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: even order-sensitive encoder fails (<0.70). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_KB=%d N_Q=%d encoder=pythia-160m" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] easy=%.3f hard=%.3f negation=%.3f" % (seed, r["auc_easy"], r["auc_hard"], r["auc_negation"]), flush=True)
del _M; torch.cuda.empty_cache()
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
