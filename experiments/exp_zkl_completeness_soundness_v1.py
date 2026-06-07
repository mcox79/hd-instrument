"""
exp_zkl_completeness_soundness_v1 -- ZKL Certificate battery cells 1+2 (combined; shared KB encode) -- CPU.

ROUTING: Research handoff exp_dev_handoff_research_ZKL_Certificate_10h_battery. Cells 1 (completeness) and 2 (soundness)
  share the KB encode, so combined into one cell (verdict HARD_PASS only if BOTH pass). Production recipe = ZCA-whiten on
  real MiniLM keys. COMPLETENESS: store N facts, query each fact's exact text, measure top-1 self-retrieval. SOUNDNESS: N
  queries with content NEVER stored, measure false-positive rate at cosine > 0.90. CPU (MiniLM forward on CPU).
PRE-REGISTERED (research bands, may tighten not loosen):
  COMPLETENESS HARD-PASS >= 99.0% top-1; MID 95-99%; HF < 95%.
  SOUNDNESS HARD-PASS <= 0.5% FP@cos0.90; MID 0.5-2.0%; HF > 2.0%.
  Combined HARD-PASS = both HP; HARD-FAIL = either HF.
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. self-retrieval trivially top-1 on identity. 3. cosine bound.
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

ANCHOR_NAME = "zkl_completeness_soundness_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
COS_FP = 0.90
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_KB = 80 if RUN_MODE == "smoke" else 500
N_NEG = 80 if RUN_MODE == "smoke" else 500


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K.mean(0), Wd


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); W, mu, Wd = whiten_fit(g.standard_normal((40, 16))); assert W.shape == (40, 16), "whiten preserves dim"
    e = unit(g.standard_normal((5, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval top-1 identity"
    assert abs(float(unit(np.ones((1, 4)))[0] @ unit(np.ones((1, 4)))[0]) - 1.0) < 1e-5, "cosine bound"
    print("[selftest] PASS: zkl-comp-sound", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")                                            # handoff specifies CPU


def load_texts(n, skip=0):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for i, l in enumerate(open(f, encoding="utf-8")):
                r = json.loads(l); t = (r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300]
                out.append(t)
                if len(out) >= n + skip:
                    return out[skip:skip + n]
    return out[skip:skip + n]


def encode(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    kb_txt = load_texts(N_KB, 0); neg_txt = load_texts(N_NEG, N_KB + 2000)
    kb_raw = encode(kb_txt); Wkb, mu, Wd = whiten_fit(kb_raw)
    kb = unit(Wkb)                                                   # stored, whitened, unit
    # COMPLETENESS: query each stored fact's exact text, top-1 over KB
    q = unit((encode(kb_txt) - mu) @ Wd); sims = q @ kb.T; top1 = (np.argmax(sims, axis=1) == np.arange(N_KB)).mean()
    # SOUNDNESS: never-stored queries; FP = max cosine to KB > COS_FP
    neg = unit((encode(neg_txt) - mu) @ Wd); maxcos = (neg @ kb.T).max(axis=1); fp = float((maxcos > COS_FP).mean())
    print("  completeness_top1=%.4f  soundness_FP@%.2f=%.4f (n_kb=%d n_neg=%d)" % (top1, COS_FP, fp, N_KB, N_NEG), flush=True)
    return {"completeness_top1": float(top1), "soundness_fp": fp, "n_kb": N_KB, "n_neg": N_NEG}


def verdict(r) -> Tuple[str, str]:
    c = r["completeness_top1"]; f = r["soundness_fp"]
    summary = "completeness_top1=%.4f soundness_FP@0.90=%.4f (n_kb=%d n_neg=%d)" % (c, f, r["n_kb"], r["n_neg"])
    comp_hp = c >= 0.99; comp_hf = c < 0.95; snd_hp = f <= 0.005; snd_hf = f > 0.02
    if comp_hp and snd_hp:
        return ("HARD_PASS", "HARD_PASS: completeness >=99%% top-1 AND soundness <=0.5%% false-positive -- retrieval + no-false-assertion gates met. " + summary)
    if comp_hf or snd_hf:
        return ("HARD_FAIL", "HARD_FAIL: completeness <95%% OR soundness >2%% FP -- customer claim void. " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: one or both gates in qualify band (completeness 95-99%% or soundness 0.5-2%%). " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_neg=%d device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_NEG), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
