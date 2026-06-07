"""
exp_lsh_fanout_norm_cone_llama_v1 -- LSH fanout pre-tests (L2-norm + cone-correction) on real Llama embeddings -- GPU.

ROUTING: handoff research_to_exp_dev_lsh_fanout_pretests_authorize (combines pre-test 1 normalization + pre-test 2 cone).
  Real production Llama-3.2-1B embeddings of real text (avoids the vacuous-synthetic-harness trap flagged in the URGENT
  privacy note). Random-hyperplane LSH routes facts to S=100 shards; B_eff = mean distinct shards spanned by a query's top-K.
  Three arms: raw / L2-normalized / cone-corrected (subtract global mean then normalize). GPU.
PRE-REGISTERED: norm-arm HARD-PASS B_eff < 30 (normalization alone fixes it). cone-arm HARD-PASS B_eff < 20 (ship cone
  correction in v1 LSH). HARD-FAIL cone-arm B_eff >= 30 (anisotropy not the dominant cause). Reports all three arms.
FORMULA SELF-TESTS (PROT-022): 1. hash deterministic. 2. cone reduces mean-norm. 3. B_eff <= S.
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

ANCHOR_NAME = "lsh_fanout_norm_cone_llama_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
S = 100; N_BITS = 7; TOPK = 50    # 2^7=128 hash buckets -> mod S=100 shards
CORPUS = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_FACTS = 800 if RUN_MODE == "smoke" else 4000
N_Q = 100 if RUN_MODE == "smoke" else 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def lsh_shards(E, planes):
    bits = (E @ planes.T > 0).astype(np.int64)            # [N, N_BITS]
    code = (bits * (2 ** np.arange(N_BITS))).sum(1)
    return code % S


def b_eff(E, shard, qidx):
    beffs = []
    for qi in qidx:
        sims = E @ E[qi]; top = np.argsort(sims)[-TOPK:]
        beffs.append(len(np.unique(shard[top])))
    return float(np.mean(beffs))


def _selftest():
    g = np.random.default_rng(0); E = unit(g.standard_normal((20, 16))); pl = g.standard_normal((N_BITS, 16))
    assert np.array_equal(lsh_shards(E, pl), lsh_shards(E, pl)), "hash deterministic"
    aniso = g.standard_normal((50, 16)).astype(np.float32) + 5.0
    assert np.linalg.norm((aniso - aniso.mean(0)).mean(0)) < np.linalg.norm(aniso.mean(0)), "cone reduces mean-norm"
    assert b_eff(E, lsh_shards(E, pl), [0, 1]) <= S, "B_eff <= S"
    print("[selftest] PASS: lsh-fanout-norm-cone", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required (production Llama encoder).", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_texts(n):
    out = []
    if not CORPUS.exists():
        return out
    for l in open(CORPUS, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        t = r.get("long_answer") or r.get("text") or r.get("question") or ""
        if not isinstance(t, str):
            ctx = r.get("context")
            t = " ".join(ctx) if isinstance(ctx, list) else (ctx if isinstance(ctx, str) else "")
        if isinstance(t, str) and len(t) > 30:
            out.append(t[:400])
        if len(out) >= n:
            break
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t, output_hidden_states=True)
        out.append(o.hidden_states[LAYER][:, -1, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 1), np.float32)


def run() -> Dict:
    texts = load_texts(N_FACTS)
    if len(texts) < 50:
        print("[FATAL] corpus too small", flush=True); return {"raw": 0.0, "norm": 0.0, "cone": 0.0, "n": 0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    raw = encode(texts, tok, m); del m; torch.cuda.empty_cache()
    H = raw.shape[1]; g = np.random.default_rng(7); planes = g.standard_normal((N_BITS, H)).astype(np.float32)
    qidx = g.choice(len(raw), min(N_Q, len(raw)), replace=False)
    arms = {}
    arms["raw"] = b_eff(raw, lsh_shards(raw, planes), qidx)
    En = unit(raw); arms["norm"] = b_eff(En, lsh_shards(En, planes), qidx)
    Ec = unit(raw - raw.mean(0)); arms["cone"] = b_eff(Ec, lsh_shards(Ec, planes), qidx)
    for k in ("raw", "norm", "cone"):
        print("  B_eff[%s] = %.2f (baseline ~40)" % (k, arms[k]), flush=True)
    arms["n"] = len(raw); return arms


def verdict(r) -> Tuple[str, str]:
    summary = "B_eff raw=%.2f L2norm=%.2f cone=%.2f at S=%d (n=%d Llama embeddings; baseline ~40)" % (r["raw"], r["norm"], r["cone"], S, r["n"])
    if r["n"] < 50:
        return ("HARD_FAIL", "HARD_FAIL: corpus too small to measure B_eff (n=%d). " % r["n"] + summary)
    if r["cone"] < 20:
        return ("HARD_PASS", "HARD_PASS: cone-correction B_eff<20 -- anisotropy IS the dominant fanout cause; ship cone correction in v1 LSH. " + summary)
    if r["norm"] < 30 or r["cone"] < 30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: normalization/cone brings B_eff<30 but cone not <20 -- partial fix. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: cone-arm B_eff>=30 -- anisotropy is NOT the dominant fanout cause; LSH needs a different fix. " + summary)


print("[config] anchor=%s mode=%s n_facts=%d S=%d bits=%d model=%s" % (ANCHOR_NAME, RUN_MODE, N_FACTS, S, N_BITS, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
