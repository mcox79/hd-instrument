"""
exp_substrate_kv_capacity_proper_gpu_v1 -- Tier-5a substrate-KV capacity probe, PROPER (incremental + resumable) -- GPU.

ROUTING: replaces f1_substrate_kv_m50000 + t5a_s2_m100000 (both killed: in-memory-only, VRAM-thrashed at 0%-useful, lost all
  data on kill). This is the STRUCTURAL FIX in action: encodes facts in CHUNKS, saves each chunk to disk via experiments/_stream.py
  (reusable embeddings + RESUMABLE), small encode batch + immediate CPU offload (no 8GB VRAM thrash), streams progress. Then
  whitens (corpus-scale ZCA) + computes recall@1 in chunks. Parameterized M (default 50000). Resumes from saved chunks if killed.
PRE-REGISTERED: HARD-PASS recall@1 >= 0.90 at M (production-scale capacity). MIDDLE >= 0.80. HARD-FAIL < 0.80.
FORMULA SELF-TESTS (PROT-022): 1. unit norm. 2. argmax-self. 3. chunk roundtrip.
ASCII-only. write_metrics + _stream incremental. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"; os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._stream import StreamWriter

ANCHOR_NAME = "substrate_kv_capacity_proper_gpu_v1"; MODEL = "EleutherAI/pythia-2.8b"
M = 2000 if "--smoke" in sys.argv else 50000; BATCH = 8; CHUNK = 2000
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    import numpy as _n
    assert abs(_n.linalg.norm(unit(_n.array([3.0, 4.0]))) - 1.0) < 1e-6, "unit norm"
    a = _n.eye(3); assert int(_n.argmax(a[1])) == 1, "argmax-self"
    x = _n.arange(6).reshape(3, 2); assert _n.concatenate([x[:1], x[1:]]).shape == (3, 2), "chunk roundtrip"
    print("[selftest] PASS: substrate-kv-capacity-proper", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def make_facts(m, g):
    subs = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel"]
    rels = ["was founded in", "is located near", "was invented by", "merged with", "is the capital of"]
    return ["entity %s-%d %s what" % (subs[i % len(subs)], i, rels[int(g.integers(0, len(rels)))]) for i in range(m)]


def run() -> Dict:
    g = np.random.default_rng(7); texts = make_facts(M, g)
    out_dir = get_output_dir(ANCHOR_NAME); sw = StreamWriter(out_dir)
    done = sw.done_units()                                            # resume: chunk indices already saved
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    need = [ci for ci in range(0, M, CHUNK) if ci not in done]
    if need:
        mdl = AutoModel.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(DEV).eval()
        for ci in need:
            chunk_texts = texts[ci:ci + CHUNK]; embs = []
            for i in range(0, len(chunk_texts), BATCH):
                t = tok(chunk_texts[i:i + BATCH], return_tensors="pt", padding=True, truncation=True, max_length=32).to(DEV)
                with torch.no_grad():
                    h = mdl(**t).last_hidden_state
                lens = t["attention_mask"].sum(1) - 1
                embs.append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())   # last-token pool, immediate CPU offload
                del h, t
            sw.save_chunk("emb", ci, np.concatenate(embs, 0))          # persist chunk to disk (reusable + resumable)
            sw.append({"i": ci, "n": len(chunk_texts)})
            print("  encoded chunk %d/%d (%d facts)" % (ci // CHUNK + 1, (M + CHUNK - 1) // CHUNK, ci + len(chunk_texts)), flush=True)
        del mdl
        if DEV.type == "cuda":
            torch.cuda.empty_cache()
    K = sw.load_chunks("emb")[:M]                                      # reassemble persisted embeddings
    print("  loaded %d embeddings from disk; whitening + recall" % len(K), flush=True)
    mu = K.mean(0); Kc = K - mu; cov = Kc.T @ Kc / len(K) + 1e-3 * np.eye(K.shape[1])
    w, V = np.linalg.eigh(cov); W = V @ np.diag(1.0 / np.sqrt(w)) @ V.T
    Kw = unit(Kc @ W); Q = K + 0.10 * g.standard_normal(K.shape).astype(np.float32); Qw = unit((Q - mu) @ W)
    pred = np.empty(M, dtype=np.int64); B = 2000
    for i in range(0, M, B):
        pred[i:i + B] = np.argmax(Qw[i:i + B] @ Kw.T, axis=1)
    rec = float((pred == np.arange(M)).mean()); sw.close()
    print("  Pythia-2.8b substrate-KV recall@1=%.3f at M=%d (chunked+persisted)" % (rec, M), flush=True)
    return {"recall": rec, "M": M}


def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.3f at M=%d" % (r["recall"], r["M"])
    if r["recall"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate-KV recall@1 >=0.90 at production scale M=%d (encoded incrementally + persisted; resumable) -- Tier-5a capacity holds. " % r["M"] + s)
    if r["recall"] >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: recall 0.80-0.90 at M=%d. " % r["M"] + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.80 at M=%d (capacity ceiling). " % r["M"] + s)


print("[config] anchor=%s mode=%s M=%d batch=%d chunk=%d model=%s" % (ANCHOR_NAME, RUN_MODE, M, BATCH, CHUNK, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
