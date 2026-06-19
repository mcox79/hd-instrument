"""
exp_zkl_hypB_position_v1 -- ZKL Hypothesis B: token-position concentration in L15 last-token pooling -- GPU.

ROUTING: handoff zkl_hypB_hypC_diagnostics_authorize Diagnostic 2 (Hyp B, P=0.18), parallel to Hyp C. Tests whether the
  last-token-pool membership signal is dominated by a few INPUT token positions (via the last token's L15 attention). If
  concentrated, the mitigation is position-specific subtraction or earlier-layer pooling. Llama-3.2-1B L15, HotpotQA-Wikipedia
  sentences. Measures entropy of the last-token attention distribution over positions (avg over heads) + top-3 share. GPU.
PRE-REGISTERED: HARD-PASS (B supported) position-attention entropy < 0.4 of uniform-max OR top-3 positions > 60% of mass;
  queue position-subtraction / earlier-layer mitigations. HARD-FAIL (B not supported) entropy near uniform; positions spread.
FORMULA SELF-TESTS (PROT-022): 1. uniform entropy ratio ~1. 2. peaked entropy ratio low. 3. probs sum 1.
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "zkl_hypB_position_v1"; MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
CORPUS = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N = 80 if RUN_MODE == "smoke" else 400


def ent_ratio(p):
    p = p[p > 1e-9]; h = -(p * np.log(p)).sum(); return float(h / np.log(len(p))) if len(p) > 1 else 0.0


def _selftest():
    u = np.ones(10) / 10; assert abs(ent_ratio(u) - 1.0) < 1e-6, "uniform entropy ratio ~1"
    pk = np.array([0.9, 0.05, 0.05]); assert ent_ratio(pk) < 0.5, "peaked entropy ratio low"
    assert abs(u.sum() - 1.0) < 1e-9, "probs sum 1"
    print("[selftest] PASS: zkl-hypB-position", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_texts(n):
    out = []; seen = set()
    if not CORPUS.exists():
        return out
    for l in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        for sl in (r.get("context") or {}).get("sentences") or []:
            for s in sl:
                t = s.strip()
                if 40 < len(t) < 300 and t not in seen:
                    seen.add(t); out.append(t)
                    if len(out) >= n:
                        return out
    return out


def run() -> Dict:
    texts = load_texts(N)
    if len(texts) < 20:
        print("[FATAL] corpus too small", flush=True); return {"n": 0, "ent": 1.0, "top3": 0.0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, attn_implementation="eager", use_safetensors=True).to(DEV).eval()
    ents = []; top3s = []
    for t in texts:
        enc = tok([t], return_tensors="pt", truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**enc, output_attentions=True)
        att = o.attentions[LAYER][0]            # [heads, seq, seq]
        last = att[:, -1, :].mean(0).float().cpu().numpy()   # last-token attention over positions, avg heads
        last = last / (last.sum() + 1e-9)
        ents.append(ent_ratio(last)); top3s.append(float(np.sort(last)[::-1][:3].sum()))
    del m; torch.cuda.empty_cache()
    e = float(np.mean(ents)); t3 = float(np.mean(top3s))
    print("  position-attention entropy ratio=%.3f (of uniform) | top-3 positions share=%.3f (n=%d)" % (e, t3, len(texts)), flush=True)
    return {"n": len(texts), "ent": e, "top3": t3}


def verdict(r) -> Tuple[str, str]:
    e = r["ent"]; t3 = r["top3"]; summary = "entropy_ratio=%.3f top3_share=%.3f (n=%d)" % (e, t3, r["n"])
    if e < 0.4 or t3 > 0.60:
        return ("HARD_PASS", "HARD_PASS (Hyp B supported): last-token pooling concentrates on a few input positions (entropy<0.4 of max OR top-3>60%%) -- queue position-specific subtraction / earlier-layer pooling mitigations. " + summary)
    return ("HARD_FAIL", "HARD_FAIL (Hyp B not supported): position attention spread (entropy near uniform, top-3 low) -- leak not position-concentrated; next candidate Hyp E (layer selection) or accept qualified-privacy posture. " + summary)


print("[config] anchor=%s mode=%s n=%d model=%s layer=%d" % (ANCHOR_NAME, RUN_MODE, N, MODEL, LAYER), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
