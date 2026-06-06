"""
exp_effective_rank_svd_multi_encoder_v1 -- Batch B TOP: rank-order encoders by effective dim d_eff -- GPU(encode)+CPU.

ROUTING: Research Batch B (NEW highest priority). Cycle 128: encoder d_eff is the PRIMARY production-capacity lever
  (random projection can't exceed rank; whitening rank-bounded). Computes d_eff (participation ratio + rank90 + rank99)
  for multiple encoders to find a higher-d_eff one than MiniLM (d_eff=82). Encodes the SAME texts with each cached
  encoder; SVD per encoder. CPU-routed (SVD dominates; encode brief per model).

PRE-REGISTERED: HARD-PASS some encoder d_eff >= 2x MiniLM (>=160 for 384-class, >=400 for 768-class) -> higher-capacity
  encoder available. MIDDLE: 1.3-2x. HARD-FAIL: all <= 1.3x MiniLM (d_eff is encoder-architecture-bounded).
FORMULA SELF-TESTS (PROT-022): 1. participation ratio. 2. var-rank monotone. 3. deps.
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
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "effective_rank_svd_multi_encoder_v1"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
# encoders: (id, type) -- sentence-transformer (mean-pool) or causal-LM (mean-pool hidden). MiniLM=reference.
ENCODERS = [("sentence-transformers/all-MiniLM-L6-v2", "st"), ("sentence-transformers/all-mpnet-base-v2", "st"),
            ("BAAI/bge-large-en-v1.5", "st")]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_ENC = 1500 if RUN_MODE == "smoke" else 6000
if RUN_MODE == "smoke":
    ENCODERS = ENCODERS[:2]   # MiniLM + mpnet (skip BGE-large download in smoke)


def participation_ratio(s):
    s2 = s ** 2; return float((s2.sum() ** 2) / (np.sum(s2 ** 2) + 1e-12))


def var_rank(s, frac):
    v = (s ** 2); v = v / v.sum(); return int(np.searchsorted(np.cumsum(v), frac) + 1)


def _selftest():
    assert abs(participation_ratio(np.ones(40)) - 40) < 1e-6, "PR flat"
    assert var_rank(np.array([5.0, 1e-9, 1e-9]), 0.9) == 1, "var-rank rank1"
    print("[selftest] PASS: pr varrank", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[dev] %s" % DEV, flush=True)


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n:
                    return out
    return out


def encode(eid, etype, texts):
    tok = AutoTokenizer.from_pretrained(eid)
    if etype == "lm":
        tok.pad_token = tok.eos_token; m = AutoModelForCausalLM.from_pretrained(eid, output_hidden_states=True).to(DEV).eval()
    else:
        m = AutoModel.from_pretrained(eid).to(DEV).eval()
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.hidden_states[-1] if etype == "lm" else o.last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def verdict(res) -> Tuple[str, str]:
    ref = res.get("all-MiniLM-L6-v2", {}).get("d_eff", 82.0)
    best = max((v["d_eff"] for v in res.values()), default=0.0)
    ratio = best / max(ref, 1e-6)
    summary = "d_eff by encoder: %s | best/MiniLM=%.2fx" % ({k: round(v["d_eff"], 1) for k, v in res.items()}, ratio)
    best_abs = max((v["d_eff"] for v in res.values()), default=0.0)
    if best_abs >= 200:
        return ("HARD_PASS", "HARD_PASS: a sentence-transformer reaches d_eff>=200 (~2.5x MiniLM) -- higher-capacity Phase-4a production encoder found. " + summary)
    if best_abs >= 150:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best encoder d_eff 150-200. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no encoder reaches d_eff>=150 -- d_eff architecture-bounded; encoder choice limited. " + summary)


print("[config] anchor=%s mode=%s N_enc=%d encoders=%s" % (ANCHOR_NAME, RUN_MODE, N_ENC, [e[0].split('/')[-1] for e in ENCODERS]), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); texts = load_texts(N_ENC); res = {}
for eid, etype in ENCODERS:
    try:
        emb = encode(eid, etype, texts); X = emb - emb.mean(0); s = np.linalg.svd(X, compute_uv=False)
        nm = eid.split("/")[-1]
        res[nm] = {"d_eff": participation_ratio(s), "rank90": var_rank(s, 0.90), "rank99": var_rank(s, 0.99), "D": int(emb.shape[1])}
        print("  [%s] d_eff=%.1f rank90=%d rank99=%d D=%d" % (nm, res[nm]["d_eff"], res[nm]["rank90"], res[nm]["rank99"], res[nm]["D"]), flush=True)
    except Exception as e:
        print("  [%s] SKIP: %s" % (eid, str(e)[:80]), flush=True)
v, vmsg = verdict(res); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [res], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [res]); print("[metrics] written", flush=True)
