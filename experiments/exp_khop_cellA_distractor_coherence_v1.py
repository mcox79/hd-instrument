"""
exp_khop_cellA_distractor_coherence_v1 -- Authorization 5 / khop-noise-fork resolver (Cell A) -- CPU.

ROUTING: handoffs exp_dev_handoff_research_khop_noise_model_2x + 8-authorizations #5. Resolves the averaging-vs-distractor
  K-hop noise fork by MEASURING the empirical distractor coherence c_d on a real-encoder KB: when a cross-shard fan-out
  returns B candidates, how coherent (mutually similar) are the non-target distractors? Low c_d => distractors behave random
  => averaging + a confidence threshold suffices (cheap v1 50-LOC fix). High c_d => coherent distractors => semantic sharding
  required (v2, 3-4 weeks). Real MiniLM keys (production geometry). CPU.
PRE-REGISTERED (research bands): HARD-PASS c_d < 0.20 (random distractor regime; averaging+confidence path). MIDDLE 0.20-0.40.
  HARD-FAIL c_d > 0.40 (coherent distractors; semantic sharding required before v1 distributed reasoning).
FORMULA SELF-TESTS (PROT-022): 1. cosine bound. 2. random vectors low coherence. 3. clustered high coherence.
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

ANCHOR_NAME = "khop_cellA_distractor_coherence_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
B = 10
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 400; N_Q = 60
else:
    N_KB = 3000; N_Q = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); r = unit(g.standard_normal((50, 128)))
    iu = np.triu_indices(50, 1); assert float(np.mean((r @ r.T)[iu])) < 0.2, "random vectors low coherence"
    c = unit(0.9 * r[0][None, :] + 0.1 * unit(g.standard_normal((50, 128)))); assert float(np.mean((c @ c.T)[np.triu_indices(50, 1)])) > 0.4, "clustered high coherence"
    assert abs(float(unit(np.ones((1, 4)))[0] @ unit(np.ones((1, 4)))[0]) - 1.0) < 1e-5, "cosine bound"
    print("[selftest] PASS: cellA-distractor-coherence", flush=True)


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


def run() -> Dict:
    kb = unit(encode(load_texts(N_KB))); g = np.random.default_rng(7)
    qs = kb[g.choice(N_KB, N_Q, replace=False)]                     # queries drawn from KB (realistic fan-out targets)
    cds = []
    for q in qs:
        sims = kb @ q; top = np.argsort(sims)[-B:]                  # B-candidate fan-out
        cand = kb[top[:-1]]                                         # distractors = top B excluding the #1 (target)
        if len(cand) < 2:
            continue
        G = cand @ cand.T; iu = np.triu_indices(len(cand), 1); cds.append(float(np.mean(G[iu])))   # mutual coherence
    c_d = float(np.mean(cds))
    print("  c_d_empirical=%.4f (B=%d fan-out, real MiniLM KB n=%d)" % (c_d, B, N_KB), flush=True)
    return {"c_d_empirical": c_d, "B": B, "n_kb": N_KB}


def verdict(r) -> Tuple[str, str]:
    c = r["c_d_empirical"]
    summary = "c_d_empirical=%.4f (distractor mutual coherence in B=%d fan-out, real MiniLM)" % (c, r["B"])
    if c < 0.20:
        return ("HARD_PASS", "HARD_PASS: distractors are effectively RANDOM (c_d<0.20) -- averaging + a confidence threshold (cheap v1 50-LOC fix) handles cross-shard K-hop; no semantic sharding needed. " + summary)
    if c <= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: c_d 0.20-0.40 -- partial distractor coherence; confidence threshold helps but margins tight. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: distractors are COHERENT (c_d>0.40) -- semantic sharding required before v1 distributed reasoning (v2, 3-4 weeks). " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_q=%d B=%d device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_Q, B), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
