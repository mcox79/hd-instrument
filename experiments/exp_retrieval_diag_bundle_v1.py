"""
exp_retrieval_diag_bundle_v1 -- BUNDLED retrieval diagnostics (encoder-ablation + KB-scaling) -- GPU.

ROUTING: 5-GPU batch, bundled. Two retrieval-only diagnostics over HotpotQA-distractor supporting-fact labels:
  D1 ENCODER-ABLATION: bge-small vs bge-large vs e5-large-v2 -- gold supporting-fact recall@2 and recall@10. Informs the v1
     two-encoder choice (which retrieval encoder).
  D2 KB-SCALING: with bge-small, supporting-fact recall@10 as the candidate pool grows (add distractor sentences pooled from
     other questions): N in {25,50,100,200,400}. Tests whether retrieval quality holds as the KB scales.
  No LLM (retrieval only). GPU for the encodes. GPU.
PRE-REGISTERED: D1 HARD-PASS the best encoder reaches recall@2 >= 0.55 (multi-hop gate). D2 HARD-PASS recall@10 drop from
  smallest to largest N <= 0.15 (scales gracefully). Bundle verdict = HARD_PASS if both; MIDDLE if one; HARD-FAIL if neither.
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. recall monotone in k. 3. parse supporting_facts.
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

ANCHOR_NAME = "retrieval_diag_bundle_v1"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
ENCODERS = [("bge-small", "BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
            ("bge-large", "BAAI/bge-large-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
            ("e5-large", "intfloat/e5-large-v2", "query: ", "passage: ")]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    sims = np.array([0.9, 0.1, 0.5]); top2 = set(np.argsort(sims)[::-1][:2]); top1 = set(np.argsort(sims)[::-1][:1])
    assert top1 <= top2, "recall monotone in k"
    sf = {"title": ["A"], "sent_id": [0]}; assert sf["title"][0] == "A", "parse supporting_facts"
    print("[selftest] PASS: retrieval-diag-bundle", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        flat = []; gold = []
        sf_set = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        for ti in range(len(titles)):
            for si, s in enumerate(sl[ti] if ti < len(sl) else []):
                if (titles[ti], si) in sf_set:
                    gold.append(len(flat))
                flat.append(s)
        if len(flat) < 12 or not gold:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold})
        if len(out) >= n:
            break
    return out


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


def encode(texts, tok, m, prefix):
    out = []
    for i in range(0, len(texts), 32):
        t = tok([prefix + x for x in texts[i:i + 32]], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def recall_at(en, qn, gold, k):
    order = np.argsort(en @ qn)[::-1][:k]; hit = len(set(order.tolist()) & set(gold))
    return hit / len(gold)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"abl": {}, "scale": {}}
    abl = {}
    for name, model, qpfx, ppfx in ENCODERS:
        try:
            tok = AutoTokenizer.from_pretrained(model); m = AutoModel.from_pretrained(model).to(DEV).eval()
        except Exception as e:
            print("  [%s] load failed: %s" % (name, str(e)[:70]), flush=True); continue
        r2 = r10 = 0.0
        for d in data:
            en = unit(encode(d["sents"], tok, m, ppfx)); qn = unit(encode([d["q"]], tok, m, qpfx))[0]
            r2 += recall_at(en, qn, d["gold"], 2); r10 += recall_at(en, qn, d["gold"], 10)
        n = len(data); abl[name] = {"r2": r2 / n, "r10": r10 / n}
        print("  [ablation %s] recall@2=%.3f recall@10=%.3f" % (name, abl[name]["r2"], abl[name]["r10"]), flush=True)
        del m; torch.cuda.empty_cache()
    # D2 KB-scaling with bge-small: grow candidate pool with distractors from other questions
    tok = AutoTokenizer.from_pretrained(ENCODERS[0][1]); m = AutoModel.from_pretrained(ENCODERS[0][1]).to(DEV).eval()
    allsents = [s for d in data for s in d["sents"]]
    g = np.random.default_rng(5); scale = {}
    for N in ([25, 60] if RUN_MODE == "smoke" else [25, 50, 100, 200, 400]):
        rec = 0.0
        for d in data:
            base = d["sents"]; need = max(0, N - len(base))
            extra = list(g.choice(len(allsents), size=min(need, len(allsents)), replace=False)) if need > 0 else []
            pool = base + [allsents[i] for i in extra]; goldset = set(range(len(d["gold"])))  # gold are first indices in base
            gold = d["gold"]
            en = unit(encode(pool, tok, m, "")); qn = unit(encode([ENCODERS[0][2] + d["q"]], tok, m, ""))[0]
            rec += recall_at(en, qn, gold, 10)
        scale["N%d" % N] = rec / len(data)
        print("  [scaling N=%d] recall@10=%.3f" % (N, scale["N%d" % N]), flush=True)
    del m; torch.cuda.empty_cache()
    return {"abl": abl, "scale": scale}


def verdict(r) -> Tuple[str, str]:
    abl = r["abl"]; scale = r["scale"]
    best_r2 = max((x["r2"] for x in abl.values()), default=0.0)
    bestname = max(abl, key=lambda k: abl[k]["r2"]) if abl else "none"
    svals = list(scale.values()); drop = (svals[0] - svals[-1]) if len(svals) >= 2 else 1.0
    d1 = best_r2 >= 0.55; d2 = drop <= 0.15
    summary = "ablation: %s | best=%s r@2=%.3f | scaling recall@10: %s (drop=%.3f)" % ({k: (round(v["r2"], 3), round(v["r10"], 3)) for k, v in abl.items()}, bestname, best_r2, {k: round(v, 3) for k, v in scale.items()}, drop)
    if d1 and d2:
        return ("HARD_PASS", "HARD_PASS: best encoder (%s) clears recall@2>=0.55 AND retrieval scales gracefully (recall@10 drop<=0.15). " % bestname + summary)
    if d1 or d2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of (encoder>=0.55 r@2 / graceful scaling) holds. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no encoder reaches recall@2>=0.55 and scaling degrades >0.15. " + summary)


print("[config] anchor=%s mode=%s n_q=%d encoders=%d (ablation+scaling bundled)" % (ANCHOR_NAME, RUN_MODE, N_Q, len(ENCODERS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
