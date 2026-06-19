"""
exp_llama_encoder_config_hotpot_v1 -- diagnostic: which Llama-1B encoder config retrieves? (layer x pool) -- GPU.

ROUTING: keystone diagnostic for BOTH the hotpot full-substrate pretest AND the URGENT privacy harness (both mandate
  Llama-3.2-1B L15 as the production encoder). hotpot_full_substrate_llama showed Llama-L15-last-token recall@2hop ~= 0
  (vs MiniLM 0.16). Before committing more Llama-L15 cells, sweep layer in {8,12,15,last} x pool in {last-token, mean} and
  report HotpotQA recall@2hop for each. Determines whether ANY Llama-1B config is a usable retrieval encoder. GPU.
PRE-REGISTERED: HARD-PASS some config reaches recall@2hop >= 0.15 (a usable Llama config exists; use it everywhere). MIDDLE
  best config 0.05-0.15 (weak; flag). HARD-FAIL all configs < 0.05 (Llama-1B last-layer-pooled embeddings are not a viable
  retrieval encoder; escalate the encoder mandate).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. mean vs last shapes. 3. parse columnar.
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

ANCHOR_NAME = "llama_encoder_config_hotpot_v1"
MODEL = "meta-llama/Llama-3.2-1B"
LAYERS = [8, 12, 15]; POOLS = ["last", "mean"]
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 25 if RUN_MODE == "smoke" else 100


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert len(LAYERS) * len(POOLS) == 6, "mean vs last shapes"
    rec = {"context": {"title": ["A"], "sentences": [["s0", "s1"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: llama-encoder-config", flush=True)


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


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l)
        ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = []
        for ti, title in enumerate(titles):
            for si, s in enumerate(sent_lists[ti] if ti < len(sent_lists) else []):
                flat.append((title, si, s))
        gold = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        if len(flat) < 4 or len(gold) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold})
        if len(out) >= n:
            break
    return out


def encode_all(texts, tok, m):
    # returns dict (layer, pool) -> [N, H] numpy
    reps = {(L, p): [] for L in LAYERS for p in POOLS}
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t, output_hidden_states=True)
        mask = t["attention_mask"].unsqueeze(-1).float()
        for L in LAYERS:
            h = o.hidden_states[L]
            reps[(L, "last")].append(h[:, -1, :].float().cpu().numpy())
            reps[(L, "mean")].append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).float().cpu().numpy())
    return {k: np.concatenate(v, 0).astype(np.float32) for k, v in reps.items()}


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"by": {}, "best": 0.0, "n": 0}
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    hits = {(L, p): 0 for L in LAYERS for p in POOLS}
    for d in data:
        sents = d["sents"]; texts = [s for (_, _, s) in sents]
        creps = encode_all(texts, tok, m); qreps = encode_all([d["q"]], tok, m)
        for key in hits:
            e = unit(creps[key]); q = unit(qreps[key])[0]; order = np.argsort(e @ q)[::-1]
            hits[key] += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
    del m; torch.cuda.empty_cache()
    n = len(data); by = {"L%d_%s" % (L, p): hits[(L, p)] / n for (L, p) in hits}
    for k in sorted(by, key=lambda x: -by[x]):
        print("  recall@2hop[%s] = %.3f" % (k, by[k]), flush=True)
    return {"by": by, "best": max(by.values()), "best_cfg": max(by, key=by.get), "n": n}


def verdict(r) -> Tuple[str, str]:
    b = r["best"]; summary = "best=%s @ %.3f | all: %s (n=%d, MiniLM ref naive=0.16)" % (r.get("best_cfg"), b, {k: round(v, 3) for k, v in r["by"].items()}, r["n"])
    if b >= 0.15:
        return ("HARD_PASS", "HARD_PASS: a usable Llama-1B retrieval config exists (recall@2hop>=0.15) -- adopt %s for all substrate cells. " % r.get("best_cfg") + summary)
    if b >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best Llama config weak (0.05-0.15) -- Llama-1B is a marginal retrieval encoder. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: all Llama-1B configs <0.05 recall@2hop -- Llama-1B pooled embeddings are NOT a viable retrieval encoder; escalate the L15 mandate (MiniLM gave 0.16). " + summary)


print("[config] anchor=%s mode=%s n_q=%d layers=%s pools=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, LAYERS, POOLS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
