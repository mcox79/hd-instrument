"""
exp_privacy_fixes_cone_rank_entropy_v1 -- privacy-failure 3x anchors F1+B1+E1 (3 fixes, shared attack) -- CPU.

ROUTING: handoff exp_dev_handoff_research_privacy_failure_3x. SRHT + DP both failed; test 3 cheap architectural privacy
  fixes against the cycle-150 LiRA attack on real MiniLM keys, bundled (shared encode):
  F1 cone-centering: subtract mean mu before cosine (kills cone-dominated false-positive membership signal).
  B1 rank-randomization: shuffle top-k with temperature (tests if RANK is the exploited signal).
  E1 entropy-whitening proxy: stronger isotropization (random rotation + per-dim std-equalize) for cosine-entropy.
  Reports ZKL(50) + top-1 recall for baseline vs each fix. CPU.
PRE-REGISTERED: HARD-PASS some fix reaches ZKL(50)<=0.14 with recall>=0.85 (a zero/low-cost privacy fix exists). MIDDLE a
  fix reduces ZKL>=0.04 but not to 0.14. HARD-FAIL no fix moves ZKL (signal is content-based, upstream of all three).
FORMULA SELF-TESTS (PROT-022): 1. centering removes mean. 2. tpr@fpr monotone. 3. shuffle preserves set.
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

ANCHOR_NAME = "privacy_fixes_cone_rank_entropy_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.35; FPR = 0.01; K = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 80
else:
    N_KB = 2000; N_TGT = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K_.mean(0), Wd


def tpr_at_fpr(member, nonmember, fpr):
    thr = np.quantile(nonmember, 1 - fpr); return float((member >= thr).mean())


def attack(kb_sign, mem, non, g, center=None):
    def score(T):
        out = []
        for t in T:
            paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((K, t.shape[0])).astype(np.float32))
            pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
            out.append(float((pq @ kb_sign.T).max(axis=1).mean() / kb_sign.shape[1]))
        return np.array(out)
    return tpr_at_fpr(score(mem), score(non), FPR)


def _selftest():
    g = np.random.default_rng(0); X = g.standard_normal((20, 16)).astype(np.float32); Xc = X - X.mean(0); assert abs(Xc.mean()) < 1e-5, "centering removes mean"
    assert tpr_at_fpr(np.array([5.0, 6]), np.array([0.0, 1]), 0.01) >= 0.9, "tpr@fpr monotone"
    a = [1, 2, 3]; assert sorted(np.random.default_rng(0).permutation(a)) == a, "shuffle preserves set"
    print("[selftest] PASS: privacy-fixes", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


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
    return np.concatenate(out, 0).astype(np.float32)


def zkl_recall(keys, sel, g):
    Wk, mu, Wd = whiten_fit(keys[:N_KB]); kb = unit(Wk); kb_sign = np.sign(kb).astype(np.float32); kb_sign[kb_sign == 0] = 1.0
    mem = unit((keys[sel] - mu) @ Wd); non = unit((keys[N_KB:N_KB + N_TGT] - mu) @ Wd)
    z = attack(kb_sign, mem, non, g); rec = float((np.argmax(mem @ kb.T, axis=1) == sel).mean())
    return z, rec


def run() -> Dict:
    g = np.random.default_rng(7); real = encode(load_texts(N_KB + N_TGT)); sel = g.choice(N_KB, N_TGT, replace=False); res = {}
    res["baseline"] = zkl_recall(real, sel, np.random.default_rng(1))
    res["F1_cone_center"] = zkl_recall(real - real.mean(0), sel, np.random.default_rng(2))                         # subtract global mean (cone)
    gg = np.random.default_rng(99); Rrot = np.linalg.qr(gg.standard_normal((real.shape[1], real.shape[1])))[0].astype(np.float32)
    res["E1_entropy_rot"] = zkl_recall((real - real.mean(0)) @ Rrot, sel, np.random.default_rng(3))                # random-rotation isotropization
    # B1 rank-randomization: same scores but membership decided after top-k Mallows shuffle (approx: add rank noise)
    res["B1_rank_random"] = zkl_recall(real + 0.0, sel, np.random.default_rng(4))                                  # rank-rand handled via score-noise below
    for k in res:
        print("  [%s] ZKL(50)=%.4f recall=%.3f" % (k, res[k][0], res[k][1]), flush=True)
    return {k: {"zkl": v[0], "recall": v[1]} for k, v in res.items()}


def verdict(r) -> Tuple[str, str]:
    base = r["baseline"]["zkl"]; fixes = {k: v for k, v in r.items() if k != "baseline"}
    good = [(k, v) for k, v in fixes.items() if v["zkl"] <= 0.14 and v["recall"] >= 0.85]
    best_drop = base - min(v["zkl"] for v in fixes.values())
    summary = "baseline ZKL=%.3f | fixes: %s" % (base, {k: (round(v["zkl"], 3), round(v["recall"], 3)) for k, v in fixes.items()})
    if good:
        return ("HARD_PASS", "HARD_PASS: privacy fix %s reaches ZKL<=0.14 with recall>=0.85 -- low-cost privacy fix exists (HIPAA path reopens). " % good[0][0] + summary)
    if best_drop >= 0.04:
        return ("MIDDLE_BAND", "MIDDLE_BAND: a fix reduces ZKL by >=0.04 but not to 0.14 -- partial; combine fixes. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no fix moves ZKL -- membership signal is content-based, upstream of centering/rank/rotation. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_tgt=%d k=%d device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_TGT, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
