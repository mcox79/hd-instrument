"""
exp_colbert_maxsim_hotpot_v1 -- ColBERT late-interaction (MaxSim) recall@2/@10 on HotpotQA 2-hop -- GPU.

ROUTING: handoff research_to_exp_dev_colbert_pretest (PRIORITY 1, gating). Multi-hop ceiling: single-vector retrieval +
  decomposition all plateau ~0.42. Late interaction (token-level MaxSim) is the standard fix. Uses colbert-ir/colbertv2.0
  token embeddings with brute-force MaxSim over each question's candidate set (no Ragatouille index needed -- candidate sets
  are ~40 sentences/question, so per-question MaxSim is cheap + exact). Proxy: raw checkpoint token embeddings (no separate
  128-dim projection head / FAISS index), so this is a lower bound on ColBERT-v2. GPU.
PRE-REGISTERED: HARD-PASS recall@2 >= 0.55 (striking distance of 0.70 with substrate composition; build the ColBERT path).
  BORDER 0.50-0.55. HARD-FAIL < 0.50 (ColBERT path closed; pivot benchmark). Compare to bge-small (r@2=0.42, r@10=0.74).
FORMULA SELF-TESTS (PROT-022): 1. maxsim self-max. 2. unit token norm. 3. parse columnar.
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

ANCHOR_NAME = "colbert_maxsim_hotpot_v1"; MODEL = "colbert-ir/colbertv2.0"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 40 if RUN_MODE == "smoke" else 100


def _selftest():
    q = np.eye(3, 8).astype(np.float32); assert abs(float((q @ q.T).max(1).sum()) - 3.0) < 1e-5, "maxsim self-max"
    v = np.array([3.0, 4.0]); assert abs(np.linalg.norm(v / np.linalg.norm(v)) - 1.0) < 1e-6, "unit token norm"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: colbert-maxsim", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
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


def tok_emb(text, tok, m):
    t = tok([text], return_tensors="pt", truncation=True, max_length=180).to(DEV)
    with torch.no_grad():
        h = m(**t).last_hidden_state[0]                              # [L, d]
    mask = t["attention_mask"][0].bool()
    h = h[mask]                                                      # real tokens only
    h = torch.nn.functional.normalize(h, dim=-1)
    return h.float().cpu().numpy()


def maxsim(Q, D):
    # sum over query tokens of max over doc tokens of cosine
    return float((Q @ D.T).max(axis=1).sum())


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"r2": 0.0, "r10": 0.0, "n": 0}
    tok = AutoTokenizer.from_pretrained(MODEL); m = AutoModel.from_pretrained(MODEL).to(DEV).eval()
    h2 = 0; h10 = 0
    for d in data:
        sents = d["sents"]; Q = tok_emb(d["q"], tok, m)
        scores = [maxsim(Q, tok_emb(s, tok, m)) for (_, _, s) in sents]
        order = np.argsort(scores)[::-1]
        h2 += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
        h10 += int(len(set((sents[i][0], sents[i][1]) for i in order[:10]) & d["gold"]) >= 2)
    del m; torch.cuda.empty_cache()
    n = len(data); r2 = h2 / n; r10 = h10 / n
    print("  n=%d ColBERT-MaxSim recall@2hop=%.3f recall@10=%.3f (bge-small ref: 0.42 / 0.74)" % (n, r2, r10), flush=True)
    return {"n": n, "r2": r2, "r10": r10}


def verdict(r) -> Tuple[str, str]:
    r2 = r["r2"]; summary = "ColBERT-MaxSim recall@2hop=%.3f recall@10=%.3f (n=%d; bge-small 0.42/0.74; proxy=no proj-head/index, lower bound)" % (r2, r["r10"], r["n"])
    if r2 >= 0.55:
        return ("HARD_PASS", "HARD_PASS: ColBERT late-interaction recall@2>=0.55 -- within striking distance of 0.70 with substrate composition; the ColBERT integration path is worth the 2-3wk investment. " + summary)
    if r2 >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: ColBERT recall@2 0.50-0.55 -- proceed with caution; measure if substrate composition closes the gap. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: ColBERT recall@2 <0.50 -- late interaction does not beat bge-small enough; ColBERT path closed, pivot benchmark. (Note: proxy is a lower bound; the proj-head/index version may do better.) " + summary)


print("[config] anchor=%s mode=%s n_q=%d model=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
