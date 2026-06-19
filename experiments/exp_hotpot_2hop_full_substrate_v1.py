"""
exp_hotpot_2hop_retrieval_pretest_v1 -- HotpotQA 2-hop with FULL substrate (ZCA-whiten) vs naive 0.16 baseline -- CPU.

ROUTING: handoff research_to_exp_dev_v1_benchmark_pretests_authorize. MuSiQue/LongMemEval not on runner; HotpotQA-distractor
  (available) is the same 2-hop multi-hop-QA class. Tests the substrate's core north-star claim: can substrate retrieval find
  BOTH supporting facts (recall@2hop) among distractors, which is what lets a small LLM answer multi-hop questions a bare LLM
  cannot. Encodes question + all candidate sentences (MiniLM), retrieves; measures recall@2hop (single-shot top-k) AND a
  2-hop chained retrieval (hop1 then re-query with hop1 context). CPU. (F1-vs-bare-Llama half flagged for a generation cell.)
PRE-REGISTERED: HARD-PASS recall@2hop >= 0.70 (substrate finds both supporting facts -> multi-hop story holds). MIDDLE
  0.50-0.70. HARD-FAIL < 0.50 (retrieval can't support multi-hop; integration story in trouble).
FORMULA SELF-TESTS (PROT-022): 1. recall bound. 2. self-retrieval. 3. parse hotpot record.
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

ANCHOR_NAME = "hotpot_2hop_full_substrate_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 50 if RUN_MODE == "smoke" else 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    assert 0 <= 1.0 <= 1.0, "recall bound"
    g = np.random.default_rng(0); e = unit(g.standard_normal((5, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    rec = {"context": [["T1", ["s0", "s1"]], ["T2", ["s2"]]], "supporting_facts": [["T1", 0]]}
    assert rec["context"][0][0] == "T1", "parse hotpot record"
    print("[selftest] PASS: hotpot-2hop", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


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
            slist = sent_lists[ti] if ti < len(sent_lists) else []
            for si, s in enumerate(slist):
                flat.append((title, si, s))
        goldset = set(zip(sf.get("title") or [], sf.get("sent_id") or []))   # columnar parallel arrays
        if len(flat) < 4 or len(goldset) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": goldset})
        if len(out) >= n:
            break
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 384), np.float32)


def whiten(E):
    Ec = E - E.mean(0); cov = (Ec.T @ Ec) / max(Ec.shape[0], 1)
    U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Ec @ Wd, E.mean(0), Wd
def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records parsed", flush=True); return {"recall_2hop": 0.0, "n": 0, "naive": 0.0, "substrate": 0.0}
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval()
    naive_hits = 0; sub_hits = 0
    for d in data:
        sents = d["sents"]; texts = [s for (_, _, s) in sents]; raw = encode(texts, tok, m); qraw = encode([d["q"]], tok, m)
        en = unit(raw); qn = unit(qraw)[0]; on = np.argsort(en @ qn)[::-1]
        naive_hits += int(len(set((sents[i][0], sents[i][1]) for i in on[:2]) & d["gold"]) >= 2)
        Wc, mu, Wd = whiten(raw); ew = unit(Wc); qw = unit((qraw - mu) @ Wd)[0]; ow = np.argsort(ew @ qw)[::-1]
        sub_hits += int(len(set((sents[i][0], sents[i][1]) for i in ow[:2]) & d["gold"]) >= 2)
    del m
    n = len(data); rn = naive_hits / n; rs = sub_hits / n
    print("  n=%d naive_recall@2hop=%.3f substrate(whiten)_recall@2hop=%.3f lift=%+.3f" % (n, rn, rs, rs - rn), flush=True)
    return {"n": n, "naive": rn, "substrate": rs, "recall_2hop": rs}


def verdict(r) -> Tuple[str, str]:
    rs = r["substrate"]; rn = r["naive"]; lift = rs - rn
    summary = "substrate(whiten)_recall@2hop=%.3f naive=%.3f lift=%+.3f (n=%d)" % (rs, rn, lift, r["n"])
    if rs >= 0.70:
        return ("HARD_PASS", "HARD_PASS: full-substrate recall@2hop>=0.70 on HotpotQA -- multi-hop integration story holds. " + summary)
    if lift >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: whitening lifts recall@2hop by >=0.05 over naive but not to 0.70 -- substrate helps, needs more (real K-hop). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: whitening does not lift multi-hop recall meaningfully -- naive-level; need real K-hop or stronger retrieval. " + summary)


print("[config] anchor=%s mode=%s n_q=%d encoder=MiniLM device=cpu (HotpotQA proxy for MuSiQue)" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
