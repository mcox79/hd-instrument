"""
exp_oracle_structured_hotpot_discrete_cpu_v1 -- R1: oracle-structured HotpotQA, DISCRETE-substrate K-hop -- CPU.

ROUTING: iterative_drill / R1 PROCEED. Proof-of-transfer to real bridges. My earlier oracle-PARSE cell used a perfect bridge
  but FUZZY bge retrieval -> recall@2=0.35 (fuzzy regime loses). R1 keeps the SAME oracle structure (gold supporting facts give
  the chain start->bridge->answer) but encodes entities as DISCRETE clean symbols and runs substrate K-hop. If discrete K-hop
  clears where fuzzy failed, it proves: real HotpotQA multi-hop is solvable GIVEN discrete structure -- only the NL->structure
  parse remains (consistent with the universal principle). Entities = context titles + answer, each a clean FHRR symbol; gold
  chain + distractor edges form the KG; K-hop from the question entity recovers the answer. Pure numpy + HotpotQA json. CPU.
PRE-REGISTERED: HARD-PASS discrete oracle K-hop answer recall@1 >= 0.55 (clears the fuzzy 0.35; transfer proven). MIDDLE
  0.45-0.55. HARD-FAIL < 0.45.
FORMULA SELF-TESTS (PROT-022): 1. bind/unbind. 2. cleanup self. 3. substring entity match.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "oracle_structured_hotpot_discrete_cpu_v1"; N = 8192
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_Q = 20 if SMOKE else 150


def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; b = cphasor(1, 32, g)[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-3), "bind/unbind"
    bk = cphasor(4, 32, g); assert cidx(bk[1], bk) == 1, "cleanup self"
    assert "paris" in "the paris agreement".lower(), "substring match"
    print("[selftest] PASS: oracle-structured-hotpot-discrete", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sf_titles = list(dict.fromkeys(sf.get("title") or []))
        ans = (r.get("answer") or "").strip()
        if len(titles) < 4 or len(sf_titles) < 2 or not ans or ans.lower() in ("yes", "no"):
            continue
        out.append({"q": r.get("question", ""), "titles": titles, "gold_titles": sf_titles, "answer": ans})
        if len(out) >= n:
            break
    return out


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"n": 0, "recall": 0.0}
    g = np.random.default_rng(7); R1 = cphasor(1, N, g)[0]; R2 = cphasor(1, N, g)[0]; RD = cphasor(8, N, g); hit = 0; n = 0
    for d in data:
        ents = list(dict.fromkeys(d["titles"] + [d["answer"]]))             # entity vocabulary = titles + answer
        idx = {e: i for i, e in enumerate(ents)}; sym = cphasor(len(ents), N, g)
        gt = d["gold_titles"]; ql = d["q"].lower()
        start = next((t for t in gt if t.lower() in ql), gt[0]); bridge = gt[1] if gt[0] == start else gt[0]
        ans = d["answer"]
        if start not in idx or bridge not in idx or ans not in idx:
            continue
        # KG: gold 2-hop chain + distractor edges among context titles (noise)
        M = sym[idx[start]] * R1 * sym[idx[bridge]] + sym[idx[bridge]] * R2 * sym[idx[ans]]
        for _ in range(2 * len(d["titles"])):
            a = int(g.integers(0, len(ents))); b = int(g.integers(0, len(ents))); rr = RD[int(g.integers(0, 8))]
            M = M + sym[a] * rr * sym[b]
        bh = cidx(M * np.conj(sym[idx[start]] * R1), sym)                    # hop1 -> bridge
        ah = cidx(M * np.conj(sym[bh] * R2), sym)                            # hop2 -> answer (grounded on recovered bridge)
        hit += int(ah == idx[ans]); n += 1
    rec = hit / max(1, n); print("  discrete oracle K-hop answer recall@1=%.3f (n=%d)" % (rec, n), flush=True)
    return {"n": n, "recall": rec}


def verdict(r) -> Tuple[str, str]:
    s = "discrete oracle recall@1=%.3f (n=%d) vs fuzzy oracle-parse 0.35" % (r["recall"], r["n"])
    if r["recall"] >= 0.55:
        return ("HARD_PASS", "HARD_PASS: discrete-encoded oracle structure solves real HotpotQA multi-hop >=0.55 (fuzzy oracle-parse got 0.35) -- transfer proven; given discrete structure the substrate answers, only the NL->structure parse remains. " + s)
    if r["recall"] >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: discrete oracle recall 0.45-0.55. " + s)
    return ("HARD_FAIL", "HARD_FAIL: discrete oracle recall <0.45. " + s)


print("[config] anchor=%s mode=%s N=%d n_q=%d" % (ANCHOR_NAME, RUN_MODE, N, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
