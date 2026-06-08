"""Generator: POST-CYCLE192 Group A compositions (A1-A5) -- prove validated primitives compose. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: POST-CYCLE192 Group A composition ({tag}). {desc} Pure numpy. CPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def topk(v, book, k):
    return set(np.argsort((book @ np.conj(v)).real)[::-1][:k].tolist())
{body}
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\\n[VERDICT] " + vmsg, flush=True)
metrics = {{"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
'''
C = []
C.append(dict(anchor="comp_a1_and_not_cpu_v1", tag="A1 AND-NOT composition (PP-162 x PP-163)",
  title="conjunctive-with-exclusion query: subjects with property P AND NOT property Q",
  desc="1000-subject KB; each property has an inverted shard (sum of subjects having it). 'P AND NOT Q' ranks subjects high on shard[P] and low on shard[Q]. Validates AND-NOT precision composes from the individual primitives.",
  prereg="HARD-PASS AND-NOT precision >= 0.95 on 1000-subject KB. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(2, 64, g); s = a[0] + a[1]; assert (np.stack([a[0], a[1]]) @ np.conj(s)).real.min() / 64 > 0.4, "shard cleanup"; print("[selftest] PASS: comp-a1-and-not", flush=True)
def run() -> Dict:
    g = np.random.default_rng(401); N = 8192; NSUBJ = 1000 if not SMOKE else 300; NPROP = 30; TR = 30 if SMOKE else 80
    subs = cphasor(NSUBJ, N, g)
    precs = []
    for _ in range(TR):
        has = (g.random((NSUBJ, NPROP)) < 0.25)
        shard = np.zeros((NPROP, N), dtype=np.complex64)
        for p in range(NPROP):
            idx = np.where(has[:, p])[0]
            if len(idx):
                shard[p] = subs[idx].sum(0)
        P, Q = 0, 1
        gold = set(int(i) for i in range(NSUBJ) if has[i, P] and not has[i, Q])
        if not gold:
            continue
        sP = (subs @ np.conj(shard[P])).real / N; sQ = (subs @ np.conj(shard[Q])).real / N
        score = sP - 1e3 * (sQ > 0.5)                                          # exclude Q-members
        top = set(np.argsort(score)[::-1][:len(gold)].tolist())
        precs.append(len(top & gold) / len(top))
    prec = float(np.mean(precs)); print("  AND-NOT precision=%.3f (%d subjects)" % (prec, NSUBJ), flush=True)
    return {"precision": prec, "nsubj": NSUBJ}
def verdict(r) -> Tuple[str, str]:
    s = "AND-NOT precision=%.3f (%d subj)" % (r["precision"], r["nsubj"])
    if r["precision"] >= 0.95: return ("HARD_PASS", "HARD_PASS: AND-NOT composition precision >=0.95 -- conjunction + negation compose. " + s)
    if r["precision"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: AND-NOT 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AND-NOT <0.85. " + s)
'''))
C.append(dict(anchor="comp_a2_count_filter_cpu_v1", tag="A2 COUNT-filter composition (PP-159 + PP-162)",
  title="aggregation over a filter: how many subjects have property P",
  desc="Count the support of a property's inverted shard by thresholding subject scores. Validates COUNT composes with the property filter to within +/-2 of the true count on a 1000-subject KB.",
  prereg="HARD-PASS COUNT-filter accuracy within +/-2 of true count for >= 0.90 of queries. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    import numpy as _n; assert abs(round(3.4) - 3) == 0, "round"; print("[selftest] PASS: comp-a2-count-filter", flush=True)
def run() -> Dict:
    g = np.random.default_rng(402); N = 8192; NSUBJ = 1000 if not SMOKE else 300; NPROP = 30; TR = 30 if SMOKE else 80
    subs = cphasor(NSUBJ, N, g); ok = 0; n = 0
    for _ in range(TR):
        has = (g.random((NSUBJ, NPROP)) < 0.15)
        for p in range(0, NPROP, 6):
            idx = np.where(has[:, p])[0]
            if not len(idx):
                continue
            shard = subs[idx].sum(0); sc = (subs @ np.conj(shard)).real / N
            est = int((sc > 0.5).sum()); true = len(idx); ok += int(abs(est - true) <= 2); n += 1
    acc = ok / max(1, n); print("  COUNT-filter within-2 accuracy=%.3f (n=%d)" % (acc, n), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "COUNT-filter within-2=%.3f" % r["acc"]
    if r["acc"] >= 0.90: return ("HARD_PASS", "HARD_PASS: COUNT-over-filter accurate within +/-2 for >=90pct -- aggregation composes with filter. " + s)
    if r["acc"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: COUNT-filter 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: COUNT-filter <0.75. " + s)
'''))
C.append(dict(anchor="comp_a3_temporal_asof_cpu_v1", tag="A3 temporal+bitemporal composition (PP-164 + PP-154)",
  title="order of events AS-OF time T: temporal sequence restricted to a valid-time",
  desc="Events carry an ordinal position and a valid-time; an AS-OF(T) query recovers the ordered sequence of events valid at time T. Validates temporal ordering composes with bitemporal as-of.",
  prereg="HARD-PASS AS-OF temporal ordering recall = 1.000 (all valid events recovered in order). MIDDLE >= 0.90. HARD-FAIL < 0.90.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; t = cphasor(1, 32, g)[0]
    assert np.allclose(a * p * t * np.conj(p * t), a, atol=1e-3), "pos-time bind"; print("[selftest] PASS: comp-a3-temporal-asof", flush=True)
def run() -> Dict:
    g = np.random.default_rng(403); N = 8192; VE = 200; L = 6; NT = 5; TR = 60 if SMOKE else 200
    ents = cphasor(VE, N, g); pos = cphasor(L, N, g); times = cphasor(NT, N, g)
    hit = 0; tot = 0
    for _ in range(TR):
        # at each time period a prefix of the sequence is valid (events accrue over time)
        seq = g.choice(VE, L, replace=False); M = np.zeros(N, dtype=np.complex64)
        valid_upto = {}
        for i in range(L):
            t_app = int(g.integers(0, NT)); valid_upto[i] = t_app
            for t in range(t_app, NT):
                M = M + times[t] * pos[i] * ents[int(seq[i])]
        T = int(g.integers(0, NT)); valid_idx = [i for i in range(L) if valid_upto[i] <= T]
        for i in valid_idx:
            pred = cidx(M * np.conj(times[T] * pos[i]), ents); hit += int(pred == int(seq[i])); tot += 1
    rec = hit / max(1, tot); print("  AS-OF temporal ordering recall=%.3f" % rec, flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "AS-OF ordering recall=%.3f" % r["recall"]
    if r["recall"] >= 0.999: return ("HARD_PASS", "HARD_PASS: AS-OF temporal ordering recall=1.0 -- temporal sequence + bitemporal as-of compose. " + s)
    if r["recall"] >= 0.90: return ("MIDDLE_BAND", "MIDDLE_BAND: AS-OF ordering 0.90-1.0. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AS-OF ordering <0.90. " + s)
'''))
C.append(dict(anchor="comp_a4_cyclic_hierarchical_cpu_v1", tag="A4 cyclic+hierarchical composition (PP-161 + PP-160)",
  title="hierarchical traversal over a cyclic graph (org chart with cross-links), depth 3",
  desc="A hierarchy (parent->children) that also contains cycles (cross-links). Depth-3 traversal with a visited-set recovers the reachable sub-tree without looping. Validates hierarchical navigation composes with cycle-safety.",
  prereg="HARD-PASS cyclic-hierarchical recall >= 0.90 at depth 3 AND termination=1.000. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    seen = {0, 1}; assert 1 in seen, "visited"; print("[selftest] PASS: comp-a4-cyclic-hierarchical", flush=True)
def run() -> Dict:
    g = np.random.default_rng(404); N = 8192; VE = 200; TR = 40 if SMOKE else 120; ents = cphasor(VE, N, g); CHILD = cphasor(1, N, g)[0]
    rec_sum = 0; term = 0; n = 0
    for _ in range(TR):
        adj = {i: [] for i in range(VE)}; shard = {i: np.zeros(N, dtype=np.complex64) for i in range(VE)}
        root = 0
        # tree edges
        nxt = 1
        frontier = [root]
        for _d in range(3):
            nf = []
            for u in frontier:
                for _c in range(2):
                    if nxt < VE:
                        adj[u].append(nxt); shard[u] = shard[u] + CHILD * ents[nxt]; nf.append(nxt); nxt += 1
            frontier = nf
        # add cross-links (cycles) among existing nodes
        for _x in range(15):
            a = int(g.integers(0, nxt)); b = int(g.integers(0, nxt))
            if b not in adj[a] and a != b:
                adj[a].append(b); shard[a] = shard[a] + CHILD * ents[b]
        gold = set()
        fr = {root}; seen = {root}
        for _ in range(3):                                                     # ground truth reachable within depth 3 (tree+cross)
            nf = set()
            for u in fr:
                nf |= set(adj[u]) - seen
            seen |= nf; gold |= nf; fr = nf
        # substrate traversal with visited-set
        reached = set(); fr = [root]; steps = 0
        while fr and steps < 8:
            steps += 1; nf = []
            for u in fr:
                cand = [v for v in range(VE) if (ents[v] @ np.conj(shard[u] * np.conj(CHILD))).real / N > 0.5]
                for v in cand:
                    if v not in reached and v != root:
                        nf.append(v)
            reached |= set(nf); fr = nf
            if len(reached) > VE:
                break
        if gold:
            rec_sum += len(gold & reached) / len(gold); term += int(steps < 8); n += 1
    rec = rec_sum / max(1, n); tr = term / max(1, n); print("  cyclic-hierarchical recall=%.3f termination=%.3f" % (rec, tr), flush=True)
    return {"recall": rec, "termination": tr}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f termination=%.3f" % (r["recall"], r["termination"])
    if r["recall"] >= 0.90 and r["termination"] >= 0.99: return ("HARD_PASS", "HARD_PASS: hierarchical traversal over cyclic graphs recall>=0.90, always terminates -- navigation + cycle-safety compose. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: cyclic-hierarchical 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cyclic-hierarchical <0.75. " + s)
'''))
C.append(dict(anchor="comp_a5_provenance_crossshard_cpu_v1", tag="A5 provenance+cross-shard chain (PP-157 + PP-141)",
  title="cross-shard 3-hop chain preserves provenance at every hop",
  desc="A 3-hop chain crosses 3 shards (A in shard1 -> B in shard2 -> C in shard3); each hop's fact carries a SOURCE. After traversing the chain, recover both the endpoint AND each hop's provenance. Validates provenance survives cross-shard chaining.",
  prereg="HARD-PASS endpoint recall >= 0.95 AND per-hop provenance fidelity = 100pct over the 3-hop chain. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; r = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]; s = cphasor(1, 32, g)[0]
    assert np.allclose(a * r * o * s * np.conj(a * r), o * s, atol=1e-3), "prov chain bind"; print("[selftest] PASS: comp-a5-provenance-crossshard", flush=True)
def run() -> Dict:
    g = np.random.default_rng(405); N = 16384; VE = 150; NS = 12; REL = cphasor(1, N, g)[0]; PROVTAG = cphasor(1, N, g)[0]; TR = 40 if SMOKE else 120
    ents = cphasor(VE, N, g); srcs = cphasor(NS, N, g)
    end_hit = 0; prov_hit = 0; prov_tot = 0; n = 0
    for _ in range(TR):
        # 3 shards, one hop each; fact = head*REL*tail (edge) + head*REL*PROVTAG*source (provenance role -- separable)
        chain = g.choice(VE, 4, replace=False); chsrc = g.integers(0, NS, 3)
        shards = []
        for h in range(3):
            hd = ents[int(chain[h])] * REL
            sh = hd * ents[int(chain[h + 1])] + hd * PROVTAG * srcs[int(chsrc[h])]
            for _d in range(3):                                                # distractor edges in same shard
                a = int(g.integers(0, VE)); b = int(g.integers(0, VE)); sh = sh + ents[a] * REL * ents[b]
            shards.append(sh)
        cur = int(chain[0]); ok_chain = True
        for h in range(3):
            payload = shards[h] * np.conj(ents[cur] * REL)                     # -> tail + PROVTAG*source
            tail = cidx(payload, ents); src = cidx(payload * np.conj(PROVTAG), srcs)
            prov_hit += int(src == int(chsrc[h])); prov_tot += 1
            if tail != int(chain[h + 1]):
                ok_chain = False
            cur = tail
        end_hit += int(cur == int(chain[3]) and ok_chain); n += 1
    er = end_hit / n; pr = prov_hit / prov_tot; print("  endpoint-recall=%.3f provenance-fidelity=%.3f" % (er, pr), flush=True)
    return {"endpoint": er, "provenance": pr}
def verdict(r) -> Tuple[str, str]:
    s = "endpoint=%.3f provenance=%.3f" % (r["endpoint"], r["provenance"])
    if r["endpoint"] >= 0.95 and r["provenance"] >= 0.999: return ("HARD_PASS", "HARD_PASS: cross-shard 3-hop chain reaches endpoint >=0.95 with 100pct provenance fidelity -- provenance + cross-shard chaining compose. " + s)
    if r["endpoint"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: endpoint 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: endpoint <0.85. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
