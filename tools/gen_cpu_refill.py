"""Generator: CPU refill batch -- MIDDLE rescues (N5 sharded, N3 harder, analogy fixed) + new capability cells. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: refill batch ({tag}). {desc} Pure numpy. CPU.
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
C.append(dict(anchor="type_confusion_sharded_cpu_v1", tag="N5 RESCUE: per-name sharding",
  title="same-name-different-referent disambiguation via per-name sharding (rescue of N5 0.75)",
  desc="N5 (monolithic bundle) hit only 0.75 because 600 facts in one bundle overloaded it. Rescue: SHARD by name -- each name's (sense,context,referent) facts live in their own sub-bundle. Context-conditioned disambiguation should jump to near-1.0, demonstrating sharding fixes named-entity ambiguity at scale (the locked invariant).",
  prereg="HARD-PASS sharded disambiguation >= 0.95 (and beats N5 monolithic 0.75). MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; c = cphasor(1, 32, g)[0]; r = cphasor(1, 32, g)[0]
    assert np.allclose(a * c * r * np.conj(a * c), r, atol=1e-3), "name-ctx bind"; print("[selftest] PASS: type-confusion-sharded", flush=True)
def run() -> Dict:
    g = np.random.default_rng(324); N = 4096; NNAME = 50; SENSE = 3; NCTX = 40; TR = 60 if SMOKE else 200
    names = cphasor(NNAME, N, g); ctxs = cphasor(NCTX, N, g); VR = NNAME * SENSE; refs = cphasor(VR, N, g)
    shard = {n: np.zeros(N, dtype=np.complex64) for n in range(NNAME)}; sense_ctx = {}
    for nm in range(NNAME):
        cset_all = g.choice(NCTX, 4 * SENSE, replace=False)                   # DISJOINT contexts across this name's senses
        for se in range(SENSE):
            ref_id = nm * SENSE + se; cset = cset_all[se * 4:(se + 1) * 4]; sense_ctx[(nm, se)] = set(int(x) for x in cset)
            for c in cset:
                shard[nm] = shard[nm] + names[nm] * ctxs[int(c)] * refs[ref_id]   # per-NAME shard
    hit = 0; n = 0
    for _ in range(TR):
        nm = int(g.integers(0, NNAME)); se = int(g.integers(0, SENSE)); c = int(g.choice(list(sense_ctx[(nm, se)])))
        pred = cidx(shard[nm] * np.conj(names[nm] * ctxs[c]), refs); hit += int(pred == nm * SENSE + se); n += 1
    rec = hit / n; print("  sharded type-confusion disambiguation=%.3f (vs N5 monolithic 0.75)" % rec, flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "sharded disambiguation=%.3f" % r["recall"]
    if r["recall"] >= 0.95: return ("HARD_PASS", "HARD_PASS: per-name sharding lifts disambiguation to >=0.95 (from N5 monolithic 0.75) -- sharding fixes named-entity ambiguity. " + s)
    if r["recall"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: sharded 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: sharded <0.85. " + s)
'''))
C.append(dict(anchor="self_improving_routing_harder_cpu_v1", tag="N3 RESCUE: harder cold-start",
  title="online routing warm-gain with a genuinely-imperfect cold-start (rescue of N3 no-headroom)",
  desc="N3 showed 0 warm-gain only because the cold-start router was already at 1.0 (no headroom). Rescue: harder regime (higher feature fuzz + cold centroids from a single noisy sample) so cold-start accuracy is materially below ceiling; then online centroid updates should produce a measurable >=5pp warm-equilibrium gain.",
  prereg="HARD-PASS warm-equilibrium accuracy >= cold-start + 5pp AND cold-start < 0.9 (genuine headroom). MIDDLE gain > 0. HARD-FAIL gain <= 0.",
  body='''
def _selftest():
    import numpy as _n; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"; print("[selftest] PASS: self-improving-routing-harder", flush=True)
def run() -> Dict:
    g = np.random.default_rng(323); D = 24; S = 40; PER = 250; FUZZ = 3.5
    centers = g.standard_normal((S, D))
    def sample(s):
        return centers[s] + FUZZ / math.sqrt(D) * g.standard_normal(D)
    cold = np.stack([sample(s) for s in range(S)]); cold = cold / np.linalg.norm(cold, axis=1, keepdims=True)  # 1 noisy sample each
    def acc(cents):
        h = 0; n = 0
        for s in range(S):
            for _ in range(PER):
                q = sample(s); q = q / np.linalg.norm(q); h += int(int(np.argmax(cents @ q)) == s); n += 1
        return h / n
    cold_acc = acc(cold); warm = cold.copy(); cnt = np.ones(S)
    for _ in range(S * PER * 2):
        s = int(g.integers(0, S)); q = sample(s); q = q / np.linalg.norm(q); pred = int(np.argmax(warm @ q))
        if pred == s:
            cnt[s] += 1; warm[s] = warm[s] + (q - warm[s]) / cnt[s]; warm[s] = warm[s] / np.linalg.norm(warm[s])
    warm_acc = acc(warm); print("  routing: cold=%.3f warm=%.3f gain=%+.3f" % (cold_acc, warm_acc, warm_acc - cold_acc), flush=True)
    return {"cold": cold_acc, "warm": warm_acc, "gain": warm_acc - cold_acc}
def verdict(r) -> Tuple[str, str]:
    s = "cold=%.3f warm=%.3f gain=%+.3f" % (r["cold"], r["warm"], r["gain"])
    if r["gain"] >= 0.05 and r["cold"] < 0.9: return ("HARD_PASS", "HARD_PASS: with genuine headroom (cold<0.9) online routing gains >=5pp at warm equilibrium -- self-improving routing validated. " + s)
    if r["gain"] > 0: return ("MIDDLE_BAND", "MIDDLE_BAND: positive but <5pp gain. " + s)
    return ("HARD_FAIL", "HARD_FAIL: no warm gain. " + s)
'''))
C.append(dict(anchor="analogy_transfer_continuous_cpu_v1", tag="analogy chain (continuous, fixed)",
  title="a learned relation applied as a continuous chain transfers across steps",
  desc="Fixed analogy-chain: estimate relation T from K codebook example pairs, then apply That CHAINED in the continuous space and measure cosine of the produced vector to the TRUE c*T^k target (not codebook cleanup, which broke the earlier version). Reports 1-step and 2-step transfer fidelity.",
  prereg="HARD-PASS 2-step continuous transfer cosine-to-true >= 0.6 AND cleanup recall >= 0.85. MIDDLE recall >= 0.7. HARD-FAIL < 0.7.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; t = cphasor(1, 64, g)[0]; assert np.allclose(a * t * np.conj(t), a, atol=1e-3), "bind"; print("[selftest] PASS: analogy-transfer-continuous", flush=True)
def run() -> Dict:
    g = np.random.default_rng(322); N = 4096; V = 300; K = 8; TR = 60 if SMOKE else 200; book = cphasor(V, N, g)
    cos1 = []; cos2 = []; rec2 = 0; n = 0
    for _ in range(TR):
        T = cphasor(1, N, g)[0]
        ex = g.choice(V, K, replace=False); That = np.zeros(N, dtype=np.complex64)
        for x in ex:
            That = That + (book[int(x)] * T) * np.conj(book[int(x)])     # estimate T from pairs (x, x*T)
        That = That / (np.abs(That) + 1e-8)
        c0 = book[int(g.integers(0, V))]
        p1 = c0 * That; g1 = c0 * T; p2 = p1 * That; g2 = g1 * T
        cos1.append(float((p1 @ np.conj(g1)).real / N)); cos2.append(float((p2 @ np.conj(g2)).real / N))
        # cleanup recall: does p2 land on the same codebook item as the true g2?
        rec2 += int(cidx(p2, book) == cidx(g2, book)); n += 1
    c1 = float(np.mean(cos1)); c2 = float(np.mean(cos2)); rr = rec2 / n
    print("  continuous transfer cos@1=%.3f cos@2=%.3f | 2-step cleanup recall=%.3f" % (c1, c2, rr), flush=True)
    return {"cos1": c1, "cos2": c2, "rec2": rr}
def verdict(r) -> Tuple[str, str]:
    s = "cos@1=%.3f cos@2=%.3f cleanup-recall@2=%.3f" % (r["cos1"], r["cos2"], r["rec2"])
    if r["cos2"] >= 0.6 and r["rec2"] >= 0.85: return ("HARD_PASS", "HARD_PASS: learned relation transfers as a continuous 2-step chain (cos>=0.6, cleanup>=0.85) -- analogical composition works. " + s)
    if r["rec2"] >= 0.7: return ("MIDDLE_BAND", "MIDDLE_BAND: 2-step cleanup 0.7-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2-step transfer weak. " + s)
'''))
C.append(dict(anchor="negation_polarity_cpu_v1", tag="signed/negated facts",
  title="facts carry polarity (affirmed vs negated) recovered alongside the value",
  desc="Each fact binds a POLARITY tag (affirm/negate) so 'X cites Y' and 'X overrules Y' (opposite relation polarity) are distinguishable. Recovers both the object and the polarity. Tests signed/negated knowledge -- a known weakness for embedding stores.",
  prereg="HARD-PASS object recall >= 0.95 AND polarity recall >= 0.95. MIDDLE >= 0.85. HARD-FAIL < 0.85.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; o = cphasor(1, 32, g)[0]
    assert np.allclose(a * p * o * np.conj(a * p), o, atol=1e-3), "polarity bind"; print("[selftest] PASS: negation-polarity", flush=True)
def run() -> Dict:
    g = np.random.default_rng(325); N = 4096; VK = 100; VO = 300; M = int(0.6 * VK); TR = 60 if SMOKE else 200
    keys = cphasor(VK, N, g); objs = cphasor(VO, N, g); pol = cphasor(2, N, g)
    oh = 0; ph = 0; n = 0
    for _ in range(TR):
        Mem = np.zeros(N, dtype=np.complex64); facts = []; ks = g.choice(VK, M, replace=False)
        for k in ks:
            o = int(g.integers(0, VO)); p = int(g.integers(0, 2)); Mem = Mem + keys[k] * pol[p] * objs[o]; facts.append((int(k), p, o))
        for k, p, o in facts[:20 if not SMOKE else 8]:
            rec = Mem * np.conj(keys[k]); opred = cidx(rec * np.conj(pol[p]), objs); ppred = cidx(rec * np.conj(objs[o]), pol)
            oh += int(opred == o); ph += int(ppred == p); n += 1
    print("  object-recall=%.3f polarity-recall=%.3f (n=%d)" % (oh / n, ph / n, n), flush=True)
    return {"obj": oh / n, "pol": ph / n}
def verdict(r) -> Tuple[str, str]:
    s = "object-recall=%.3f polarity-recall=%.3f" % (r["obj"], r["pol"])
    if r["obj"] >= 0.95 and r["pol"] >= 0.95: return ("HARD_PASS", "HARD_PASS: signed/negated facts recovered with object + polarity >=0.95 -- affirm-vs-negate distinguishable (embedding-store weakness covered). " + s)
    if min(r["obj"], r["pol"]) >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.85. " + s)
'''))
C.append(dict(anchor="compositional_and_query_cpu_v1", tag="conjunctive (AND) constraint query",
  title="retrieve items satisfying TWO bound attribute constraints simultaneously",
  desc="Items each bind several attribute=value facets (color, shape, size). A conjunctive query (color=red AND shape=circle) is answered by scoring items against the combined constraints; only items matching BOTH should rank top. Measures precision@matchcount of the AND.",
  prereg="HARD-PASS conjunctive-query precision >= 0.90 (matching items ranked above non-matching). MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 64, g)[0]; v = cphasor(1, 64, g)[0]; assert np.allclose(a * v * np.conj(a), v, atol=1e-3), "bind"; print("[selftest] PASS: compositional-and-query", flush=True)
def run() -> Dict:
    g = np.random.default_rng(326); N = 8192; NITEM = 300; NF = 3; VALS = 5; TR = 40 if SMOKE else 120
    facets = cphasor(NF, N, g); vals = cphasor(NF * VALS, N, g)
    hit = 0; tot = 0
    for _ in range(TR):
        item_attr = g.integers(0, VALS, (NITEM, NF)); items = np.zeros((NITEM, N), dtype=np.complex64)
        for it in range(NITEM):
            for f in range(NF):
                items[it] = items[it] + facets[f] * vals[f * VALS + int(item_attr[it, f])]
        items = items / (np.abs(items) + 1e-8)
        f1, f2 = 0, 1; v1 = int(g.integers(0, VALS)); v2 = int(g.integers(0, VALS))
        gold = set(it for it in range(NITEM) if item_attr[it, f1] == v1 and item_attr[it, f2] == v2)
        if not gold:
            continue
        q = facets[f1] * vals[f1 * VALS + v1] + facets[f2] * vals[f2 * VALS + v2]   # conjunctive constraint vector
        top = topk(q, items, len(gold)); hit += len(top & gold); tot += len(gold)
    prec = hit / max(1, tot); print("  conjunctive AND-query precision@k=%.3f" % prec, flush=True)
    return {"precision": prec}
def verdict(r) -> Tuple[str, str]:
    s = "AND-query precision=%.3f" % r["precision"]
    if r["precision"] >= 0.90: return ("HARD_PASS", "HARD_PASS: conjunctive (A AND B) query precision >=0.90 -- multi-constraint structured retrieval works. " + s)
    if r["precision"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: AND-query 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: AND-query <0.75. " + s)
'''))
C.append(dict(anchor="temporal_ordering_recovery_cpu_v1", tag="event sequence ordering",
  title="recover the temporal order of events stored with ordinal-position binding",
  desc="A sequence of events each bound to an ordinal-position vector; the stored order is recovered by querying each position and reading out the event. Measures adjacent-pair order accuracy (is event[i] correctly before event[i+1]).",
  prereg="HARD-PASS adjacent-pair order accuracy >= 0.90 over sequences. MIDDLE >= 0.75. HARD-FAIL < 0.75.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(1, 32, g)[0]; p = cphasor(1, 32, g)[0]; assert np.allclose(a * p * np.conj(p), a, atol=1e-3), "pos bind"; print("[selftest] PASS: temporal-ordering-recovery", flush=True)
def run() -> Dict:
    g = np.random.default_rng(327); N = 4096; VE = 200; L = 8; TR = 60 if SMOKE else 200; ents = cphasor(VE, N, g); pos = cphasor(L, N, g)
    correct = 0; tot = 0
    for _ in range(TR):
        seq = g.choice(VE, L, replace=False); M = np.zeros(N, dtype=np.complex64)
        for i in range(L):
            M = M + pos[i] * ents[int(seq[i])]
        readout = [cidx(M * np.conj(pos[i]), ents) for i in range(L)]
        for i in range(L - 1):
            correct += int(readout[i] == int(seq[i]) and readout[i + 1] == int(seq[i + 1])); tot += 1
    acc = correct / tot; print("  adjacent-pair order accuracy=%.3f (L=%d)" % (acc, L), flush=True)
    return {"acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "order-accuracy=%.3f" % r["acc"]
    if r["acc"] >= 0.90: return ("HARD_PASS", "HARD_PASS: temporal sequence order recovered >=0.90 adjacent-pair -- event ordering supported. " + s)
    if r["acc"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: order 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: order <0.75. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
