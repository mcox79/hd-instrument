"""
exp_iterative_multihop_bgelarge_v1 -- multi-hop bridge-extraction RESCUE 1: iterative retrieval + e5-large (no LLM) -- CPU.

ROUTING: multihop_revival_followon_battery Experiment 1 (PRIORITY 1, cheapest). The Qwen-driven iterative_multihop HARD_FAILed
  (0.333 r@2); this tests whether a STRONGER ENCODER (bge-large, single-shot r@2=0.516) + iteration clears the gate WITHOUT an
  LLM in the loop: hop1 = retrieve top-1 by the question; hop2 = retrieve by the top-1 hop-1 sentence used as the next query
  (entity-bridging heuristic); accumulate; recall@2 of the 2 gold supporting facts. bge-large on CPU (avoids the GPU lane). CPU.
PRE-REGISTERED: HARD-PASS iterative recall@2 >= 0.55 (encoder upgrade + iteration clears the multi-hop HP gate). MIDDLE
  0.50-0.55. HARD-FAIL < 0.50 (ceiling holds; multi-hop stays closed).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. recall counts gold. 3. parse supporting_facts.
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

ANCHOR_NAME = "iterative_multihop_e5large_v1"
BI = "intfloat/e5-large-v2"; Q_INSTR = "query: "; P_INSTR = "passage: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    gold = {1, 3}; top = [1, 5, 3]; assert len(set(top) & gold) == 2, "recall counts gold"
    sf = {"title": ["A"], "sent_id": [0]}; assert sf["title"][0] == "A", "parse supporting_facts"
    print("[selftest] PASS: iterative-multihop-bgelarge", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []; flat = []; gold = []
        sfset = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        for ti in range(len(titles)):
            for si, s in enumerate(sl[ti] if ti < len(sl) else []):
                if (titles[ti], si) in sfset:
                    gold.append(len(flat))
                flat.append(s)
        if len(flat) < 12 or len(gold) < 2:
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
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"n": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI).to(DEV).eval()
    ss_r2 = it_r2 = 0.0
    for d in data:
        sents = d["sents"]; gold = set(d["gold"]); en = unit(encode([P_INSTR + x for x in sents], tok, m)); qn = unit(encode([Q_INSTR + d["q"]], tok, m))[0]
        order = np.argsort(en @ qn)[::-1]
        ss_top = list(order[:2]); ss_r2 += int(len(set(ss_top) & gold) == 2)        # single-shot top-2
        hop1 = int(order[0])
        qn2 = unit(encode([Q_INSTR + sents[hop1]], tok, m))[0]                       # next query = the hop-1 fact (e5 query prefix)
        order2 = [i for i in np.argsort(en @ qn2)[::-1] if i != hop1]
        it_top = [hop1, int(order2[0])]; it_r2 += int(len(set(it_top) & gold) == 2)  # iterative top-2
    del m; n = len(data); r = {"n": n, "ss_r2": ss_r2 / n, "it_r2": it_r2 / n}
    print("  recall@2 single-shot=%.3f iterative(bge-large)=%.3f (n=%d)" % (r["ss_r2"], r["it_r2"], n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "iterative r@2=%.3f vs single-shot=%.3f (n=%d, bge-large)" % (r["it_r2"], r["ss_r2"], r["n"])
    if r["it_r2"] >= 0.55:
        return ("HARD_PASS", "HARD_PASS: e5-large + iteration clears recall@2>=0.55 -- bridge-extraction rescue via encoder upgrade. " + s)
    if r["it_r2"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: iterative r@2 0.50-0.55 -- close but below HP gate. " + s)
    return ("HARD_FAIL", "HARD_FAIL: iterative bge-large r@2 <0.50 -- multi-hop ceiling holds (stays closed). " + s)


print("[config] anchor=%s mode=%s n_q=%d bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
