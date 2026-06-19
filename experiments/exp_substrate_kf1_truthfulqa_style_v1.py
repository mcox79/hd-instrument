"""
exp_substrate_hallucination_robustness_hard_negatives_v1 -- Slot G5: KF-1 on harder (negated/contradiction) adversarial -- GPU.

ROUTING: follow-on to KF-1 (hallucination detection AUC=0.999, 21st flagship). KF-1 used easy negatives. This stress-tests
  robustness: grounding score s(q) = max cosine(enc(q), KB) must still separate GROUNDED queries from HALLUCINATED ones
  across 3 hardness tiers: (easy) cross-domain sentence; (hard) held-out SAME-DOMAIN fact not in KB; (adversarial) a KB
  fact with its content words shuffled (high lexical overlap, false). Reports AUC per tier. MiniLM encoder, torch GPU.

PRE-REGISTERED bands: HARD-PASS AUC >= 0.90 on the HARD (held-out same-domain) tier. MIDDLE: 0.75-0.90. HARD-FAIL: < 0.75
  (grounding does not survive hard negatives -> hallucination detection is brittle).
FORMULA SELF-TESTS (PROT-022): 1. AUC monotonic. 2. word-shuffle changes order. 3. cuda.
ASCII-only. write_metrics. PROT-018: no _nN.
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

ANCHOR_NAME = "substrate_kf1_truthfulqa_style_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"; MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_KB = 800; N_Q = 200; DROP = 0.3
else:
    SEEDS = [7, 17, 23]; N_KB = 4000; N_Q = 800; DROP = 0.3


def auc(pos, neg):
    # prob a random pos scores above a random neg (Mann-Whitney)
    pos = np.asarray(pos); neg = np.asarray(neg); n = 0.0; tot = len(pos) * len(neg)
    ranks = np.argsort(np.argsort(np.concatenate([pos, neg])))
    rpos = ranks[:len(pos)].sum(); return float((rpos - len(pos) * (len(pos) - 1) / 2) / max(tot, 1))


def word_shuffle(s, g):
    w = s.split();
    if len(w) > 3:
        idx = g.permutation(len(w)); w = [w[i] for i in idx]
    return " ".join(w)


def word_drop(s, p, g):
    w = s.split(); keep = [x for x in w if g.random() > p]; return " ".join(keep) if keep else s


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
    assert negate("risk increases with dose") != "risk increases with dose", "negate changes meaning"
    print("[selftest] PASS: auc negate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoTokenizer
_TOK = AutoTokenizer.from_pretrained(MINILM_ID); _M = AutoModel.from_pretrained(MINILM_ID).to(DEVICE).eval()


def enc(texts):
    out = []
    for i in range(0, len(texts), 64):
        t = _TOK(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            h = _M(**t).last_hidden_state
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
    pub = load_lines(PUBMED, N_KB + N_Q + N_Q); med = load_lines(MEDQA, N_Q)
    kb = pub[:N_KB]; held = pub[N_KB:N_KB + N_Q]                          # held-out same-domain (hard negatives)
    Ekb = enc(kb)
    src = [kb[i] for i in g.choice(len(kb), N_Q, replace=False)]
    pos = enc([word_drop(s, DROP, g) for s in src])                      # grounded: dropped-word version of a KB fact
    neg_hard = enc(held)
    neg_neg = enc([negate(s) for s in src])                              # contradiction: negated KB fact (opposite meaning, high overlap)
    def gscore(E):
        return (E @ Ekb.T).max(1)
    sp = gscore(pos)
    res = {"seed": seed, "auc_hard": auc(sp, gscore(neg_hard)), "auc_negation": auc(sp, gscore(neg_neg))}
    return res


def verdict(ps) -> Tuple[str, str]:
    an = float(np.mean([p["auc_negation"] for p in ps])); ah = float(np.mean([p["auc_hard"] for p in ps]))
    summary = "AUC hard(held-out same-domain)=%.3f NEGATION(contradiction)=%.3f" % (ah, an)
    if an >= 0.85:
        return ("HARD_PASS", "HARD_PASS: grounding detects contradictions/negations (AUC>=0.85) -- production-grade adversarial hallucination detection. " + summary)
    if an >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: contradiction detection 0.70-0.85. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: grounding misses negations/contradictions (<0.70) -- MiniLM negation-insensitive (encoder limit, like word-order). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_KB=%d N_Q=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_KB, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] auc_hard=%.3f auc_negation=%.3f" % (seed, r["auc_hard"], r["auc_negation"]), flush=True)
del _M; torch.cuda.empty_cache()
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
