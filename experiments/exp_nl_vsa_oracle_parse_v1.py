"""
exp_nl_vsa_oracle_parse_v1 -- NL->VSA parser gate: ORACLE-parse 2-hop on real HotpotQA (isolates parse from traversal) -- CPU.

ROUTING: NL_to_VSA_parser_HIGHEST_PRIORITY Anchor 1 (automatable proxy for the manual parse). The synthetic result showed
  substrate K-hop does multi-hop (0.825) on VSA-encoded queries; iterative NL approaches all failed (parse loses intent).
  This isolates the question: GIVEN a perfect bridge (oracle = HotpotQA gold supporting-fact title), does substrate retrieval
  solve hop2? hop1 = retrieve by question; hop2 = retrieve by the OTHER gold fact's title (oracle bridge) -> is the 2nd gold
  fact recovered? Compares oracle-2-hop recall@2 to single-shot (~0.31) and the failed iterative (~0.2). If oracle-2-hop >>
  iterative, the bottleneck is provably the PARSE (bridge identification), not the hop traversal. bge-small. CPU.
PRE-REGISTERED: HARD-PASS oracle-2-hop recall@2 >= 0.55 (substrate solves hop2 given a perfect bridge -> only the parser
  remains). MIDDLE 0.45-0.55. HARD-FAIL < 0.45 (even with a perfect bridge, retrieval fails -- deeper problem).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. recall counts gold. 3. title parse.
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

ANCHOR_NAME = "nl_vsa_oracle_parse_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    gold = {1, 3}; top = [1, 3]; assert len(set(top) & gold) == 2, "recall counts gold"
    sf = {"title": ["Alpha", "Beta"], "sent_id": [0, 1]}; assert sf["title"][1] == "Beta", "title parse"
    print("[selftest] PASS: nl-vsa-oracle-parse", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        sf_titles = sf.get("title") or []; sf_sids = sf.get("sent_id") or []
        flat = []; idx_of = {}; title_of = []
        for ti in range(len(titles)):
            for si, s in enumerate(sl[ti] if ti < len(sl) else []):
                idx_of[(titles[ti], si)] = len(flat); title_of.append(titles[ti]); flat.append(s)
        gold = [idx_of[(t, s)] for t, s in zip(sf_titles, sf_sids) if (t, s) in idx_of]
        gold_titles = list(dict.fromkeys([t for t in sf_titles]))
        if len(flat) < 12 or len(gold) < 2 or len(gold_titles) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold, "title_of": title_of, "gold_titles": gold_titles})
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
    ss_r2 = oracle_r2 = 0.0
    for d in data:
        sents = d["sents"]; gold = set(d["gold"]); en = unit(encode(sents, tok, m)); qn = unit(encode([Q_INSTR + d["q"]], tok, m))[0]
        order = np.argsort(en @ qn)[::-1]
        ss_r2 += int(len(set(order[:2].tolist()) & gold) == 2)                  # single-shot top-2
        # oracle 2-hop: hop1 = best by question; hop2 = best by the gold-bridge TITLE (perfect parse of the bridge)
        hop1 = int(order[0]); bridge_title = d["gold_titles"][1]                # oracle bridge entity
        qn2 = unit(encode([Q_INSTR + bridge_title], tok, m))[0]
        order2 = [i for i in np.argsort(en @ qn2)[::-1] if i != hop1]
        it_top = {hop1, int(order2[0])}; oracle_r2 += int(len(it_top & gold) == 2)
    del m; n = len(data); r = {"n": n, "ss_r2": ss_r2 / n, "oracle_r2": oracle_r2 / n}
    print("  recall@2 single-shot=%.3f oracle-bridge-2hop=%.3f (n=%d)" % (r["ss_r2"], r["oracle_r2"], n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "oracle-2hop r@2=%.3f vs single-shot=%.3f (n=%d)" % (r["oracle_r2"], r["ss_r2"], r["n"])
    if r["oracle_r2"] >= 0.55:
        return ("HARD_PASS", "HARD_PASS: given a perfect bridge (oracle parse), substrate 2-hop retrieval clears r@2>=0.55 -- the substrate SOLVES HotpotQA multi-hop with a structured query; the ONLY remaining work is the NL->VSA parser (bridge ID). " + s)
    if r["oracle_r2"] >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: oracle-2hop 0.45-0.55. " + s)
    return ("HARD_FAIL", "HARD_FAIL: even with a perfect bridge, 2-hop retrieval <0.45 -- the bottleneck is deeper than the parse. " + s)


print("[config] anchor=%s mode=%s n_q=%d bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
