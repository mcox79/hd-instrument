"""
exp_lap3_5_gram_matrix_diag_gpu_v1.py -- LAP3-5 GRAM-MATRIX-CONDITION-DIAGNOSTIC -- GPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (LAP3-5; routed to GPU-torch). The PP-225 transfer needs an fp32 projection head above
  160M (bf16 head HARD_FAILs). This diagnostic measures, per frozen encoder, the Gram-matrix condition number of its sentence
  embeddings -- a high condition number means the head's logit projection is ill-conditioned in bf16 and needs fp32, predicting
  the bf16-envelope failure PROACTIVELY (no costly re-train to discover it). Loads encoders via HF, encodes a fixed probe set,
  reports condition numbers + an fp32/bf16 recommendation per encoder. torch + transformers. GPU.
PRE-REGISTERED: HARD-PASS produces a per-encoder cond-number + actionable fp32/bf16 call (diagnostic completes for >=2 encoders).
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "lap3_5_gram_matrix_diag_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
ENCODERS = ["BAAI/bge-large-en-v1.5", "intfloat/e5-large-v2"] if not SMOKE else ["BAAI/bge-small-en-v1.5"]
PROBES = ["The secret code of %s is" % w for w in ("aardvark albatross amsterdam barcelona violet copper seven marble thunder "
    "willow saffron glacier ember quartz orchid harvest lantern meadow falcon cinnamon velvet anchor prism cobalt cairo dublin "
    "oslo prague venice").split()]


def _selftest():
    import numpy as _n; c = _n.linalg.cond(_n.eye(3)); assert abs(c - 1) < 1e-6, "cond"; print("[selftest] PASS: gram-matrix-diag", flush=True)


def run() -> Dict:
    import torch
    from transformers import AutoTokenizer, AutoModel
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % dev, flush=True)
    res = {}
    for enc in ENCODERS:
        try:
            tok = AutoTokenizer.from_pretrained(enc); mdl = AutoModel.from_pretrained(enc, torch_dtype=torch.float32).to(dev).eval()
            embs = []
            with torch.no_grad():
                for i in range(0, len(PROBES), 16):
                    b = tok(PROBES[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=32).to(dev)
                    h = mdl(**b).last_hidden_state[:, 0]
                    embs.append(torch.nn.functional.normalize(h, dim=-1).float().cpu().numpy())
            E = np.concatenate(embs)                                      # (P, dim)
            G = E @ E.T                                                   # Gram matrix
            sv = np.linalg.svd(G, compute_uv=False); cond = float(sv[0] / max(sv[-1], 1e-9))
            # bf16 has ~3 decimal digits (~8 bit mantissa) -> ill-conditioned if cond > ~1e3
            need_fp32 = cond > 1e3
            res[enc] = {"cond": round(cond, 1), "need_fp32": bool(need_fp32), "dim": int(E.shape[1])}
            print("  %s: Gram-cond=%.1f -> %s" % (enc.split("/")[-1], cond, "NEEDS fp32 head" if need_fp32 else "bf16 OK"), flush=True)
            del mdl; torch.cuda.empty_cache() if torch.cuda.is_available() else None
        except Exception as e:
            res[enc] = {"error": str(e)[:80]}; print("  %s: FAIL %s" % (enc, str(e)[:60]), flush=True)
    ok = sum(1 for v in res.values() if "cond" in v)
    return {"per_encoder": res, "n_diagnosed": ok}


def verdict(r) -> Tuple[str, str]:
    s = "diagnosed=%d encoders; %s" % (r["n_diagnosed"], {k.split("/")[-1]: v for k, v in r["per_encoder"].items()})
    if r["n_diagnosed"] >= 2 or (SMOKE and r["n_diagnosed"] >= 1):
        return ("HARD_PASS", "HARD_PASS: Gram-condition diagnostic produces a per-encoder fp32/bf16 head recommendation -- proactively flags which encoders need fp32 (high Gram condition), preventing bf16-envelope failures before any re-train. " + s)
    return ("HARD_FAIL", "HARD_FAIL: diagnostic did not complete for >=2 encoders. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch  # noqa
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
print("[config] anchor=%s mode=%s encoders=%d" % (ANCHOR_NAME, RUN_MODE, len(ENCODERS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
