"""TIER-2 P1 (Research: 2Wiki FIRST): 2WikiMultihopQA gold-path substrate traversal (clean evidence triples). Runs on HOME (HF works there). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
CELL = r'''"""
exp_2wiki_goldpath_traversal_cpu_v1.py -- TIER-2 P1: 2WikiMultihopQA gold-path substrate traversal -- CPU (home).

ROUTING: Research FB15K_ACK_NLQA_DECISION -- 2Wiki FIRST (clean evidence triples, no decomposition parsing). Path-1 gold-path:
  per question, encode the gold evidence triples into an FHRR substrate (per-(head,rel) sharded), traverse from the chain-start
  entity, and check the gold ANSWER is reached within the chain depth. METRIC = answer-reach rate (substrate faithfully traverses
  the clean evidence chain) + by-type. Tests categorical traversal completeness vs probabilistic sampling. Dispatch to HOME
  (cpu_runner_0 / overnight_queue) where HF downloads work; laptop HF downloads hang. numpy/VSA + datasets. CPU.
PRE-REGISTERED: HARD-PASS answer-reach >= 0.90 (substrate traverses clean gold chains faithfully). MIDDLE >= 0.75. HARD-FAIL < 0.75.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "8")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "60")
import argparse, time, math, re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, deque
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "2wiki_goldpath_traversal_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096; KHOP = 4; TOPK = 5
DS_NAMES = ["xanhho/2WikiMultihopQA", "voidful/2WikiMultihopQA", "scholarly-shadows-syndicate/2wikimultihopqa_with_q_gpt35"]
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()


def _selftest():
    assert norm("The Eiffel-Tower!") == "the eiffel tower", "norm"; print("[selftest] PASS: 2wiki-goldpath-traversal", flush=True)


def load_ds():
    from datasets import load_dataset
    for nm in DS_NAMES:
        for sp in ("validation", "dev", "test", "train"):
            try:
                ds = load_dataset(nm, split=sp)
                if "evidences" in ds.column_names or "evidence" in ds.column_names or "supporting_facts" in ds.column_names:
                    print("[data] %s[%s]: %d rows, cols=%s" % (nm, sp, len(ds), ds.column_names[:8]), flush=True); return ds, nm
            except Exception as e:
                print("[data] %s[%s] fail: %s" % (nm, sp, str(e)[:60]), flush=True)
    return None, None


def get_evidences(ex):
    ev = ex.get("evidences") or ex.get("evidence") or []
    out = []
    for e in ev:
        if isinstance(e, (list, tuple)) and len(e) == 3:
            out.append((str(e[0]), str(e[1]), str(e[2])))
    return out


def reach(graph, seeds, g):
    ents = sorted({h for h, _, _ in graph} | {t for _, _, t in graph}); rels = sorted({r for _, r, _ in graph})
    if not ents:
        return set()
    ei = {e: i for i, e in enumerate(ents)}; ri = {r: i for i, r in enumerate(rels)}
    E = cphasor(len(ents), N, g); R = cphasor(len(rels), N, g); Ec = np.conj(E)
    hr = defaultdict(list)
    for h, r, t in graph:
        hr[(ei[h], ri[r])].append(ei[t])
    shard = {}
    for (h, r), ts in hr.items():
        v = np.zeros(N, dtype=np.complex64)
        for t in ts:
            v = v + E[h] * (R[r] * E[t])
        shard[(h, r)] = v
    frontier = {ei[s] for s in seeds if s in ei}; seen = set(frontier)
    for _h in range(KHOP):
        nxt = set()
        for e in frontier:
            for (hh, r) in hr:
                if hh != e:
                    continue
                s2 = shard[(e, r)] * Ec[e] * np.conj(R[r]); order = np.argsort((E @ np.conj(s2)).real)[::-1][:TOPK]
                for o in order:
                    if int(o) not in seen:
                        nxt.add(int(o)); seen.add(int(o))
        frontier = nxt
        if not frontier:
            break
    inv = {i: e for e, i in ei.items()}
    return {norm(inv[i]) for i in seen}


def run() -> Dict:
    g = np.random.default_rng(2222); ds, nm = load_ds()
    if ds is None:
        return {"error": "download_failed", "answer_reach": 0.0, "n": 0}
    idx = list(range(len(ds))); g.shuffle(idx); want = 30 if SMOKE else 300
    hit = 0; n = 0; bytype = defaultdict(lambda: [0, 0])
    for i in idx:
        if n >= want:
            break
        ex = ds[i]; graph = get_evidences(ex)
        ans = ex.get("answer") or ""
        if not graph or not ans:
            continue
        tails = {t for _, _, t in graph}; heads = {h for h, _, _ in graph}
        seeds = list(heads - tails) or list(heads)                        # chain start = heads that are not tails
        reached = reach(graph, seeds, g); ok = int(norm(ans) in reached)
        hit += ok; n += 1; ty = ex.get("type", "?"); bytype[ty][0] += ok; bytype[ty][1] += 1
    ar = hit / n if n else 0.0
    bt = {k: round(v[0] / v[1], 3) for k, v in bytype.items() if v[1] >= 3}
    print("  2Wiki gold-path answer-reach=%.3f (n=%d, src=%s) by-type=%s" % (ar, n, nm, bt), flush=True)
    return {"answer_reach": ar, "n": n, "source": nm, "by_type": bt}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: 2Wiki download failed on runner; cell ok, retry / try other DS name. " + r["error"])
    s = "answer-reach=%.3f (n=%d) by-type=%s" % (r["answer_reach"], r["n"], r["by_type"])
    if r["answer_reach"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate traverses 2WikiMultihopQA gold evidence chains to the answer >=90pct -- categorical multi-hop traversal completeness on a real NL-QA benchmark (Path-1). " + s)
    if r["answer_reach"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: answer-reach 0.75-0.90 (cleanup top-K prunes some branches; raise TOPK). " + s)
    return ("HARD_FAIL", "HARD_FAIL: answer-reach <0.75. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s khop=%d" % (ANCHOR_NAME, RUN_MODE, KHOP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
(EXP / "exp_2wiki_goldpath_traversal_cpu_v1.py").write_text(CELL, encoding="utf-8"); print("wrote 2wiki_goldpath_traversal")
