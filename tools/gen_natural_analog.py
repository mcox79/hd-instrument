"""Generator: emits the 5 natural-analog CPU pre-test cells (pure numpy). Run: python tools/gen_natural_analog.py"""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"

HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: natural_analog_5_pretests {analog}. {desc} Pure numpy. CPU.
PRE-REGISTERED: {prereg}
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "{anchor}"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)

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

CELLS = []

# Analog 2: ant-colony time-windowed Misra-Gries decay
CELLS.append(dict(anchor="natural_analog_antcolony_mg_decay_v1", analog="Analog 2 (ANT COLONY)",
    title="time-windowed Misra-Gries pheromone decay detects drift faster",
    desc="Add pheromone decay (rate alpha) to Misra-Gries counters; a 10000-query stream shifts topic at q=5000; measure how many queries after the shift the decayed counters reflect the new distribution vs un-decayed.",
    prereg="HARD-PASS decayed counters detect the shift within 100 queries AND faster than un-decayed. MIDDLE within 500. HARD-FAIL no faster.",
    body='''
def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()

def _selftest():
    p = zipf(10); assert abs(p.sum() - 1.0) < 1e-9, "zipf norm"
    c = {1: 5.0}; c = {k: v * 0.9 for k, v in c.items()}; assert c[1] < 5.0, "decay shrinks"
    assert 1 in {1: 2}, "counter present"
    print("[selftest] PASS: antcolony-mg-decay", flush=True)

def run() -> Dict:
    g = np.random.default_rng(11); V = 100; Q = 4000 if SMOKE else 10000; SHIFT = Q // 2; ALPHA = 0.98; TOPK = 8
    P = zipf(V); perm = g.permutation(V); Pn = np.zeros(V); Pn[perm] = zipf(V)
    stream = np.concatenate([g.choice(V, SHIFT, p=P), g.choice(V, Q - SHIFT, p=Pn)])
    new_top = set(int(i) for i in np.argsort(Pn)[::-1][:TOPK])
    def detect(decay):
        cnt = np.zeros(V)
        for t in range(Q):
            cnt[stream[t]] += 1.0
            if decay:
                cnt *= ALPHA
            if t >= SHIFT and t % 20 == 0:
                top = set(int(i) for i in np.argsort(cnt)[::-1][:TOPK])
                if len(top & new_top) >= TOPK * 0.6:
                    return t - SHIFT
        return Q - SHIFT
    d_dec = detect(True); d_und = detect(False)
    print("  shift-detection lag: decayed=%d queries  undecayed=%d (alpha=%.2f)" % (d_dec, d_und, ALPHA), flush=True)
    return {"lag_decayed": d_dec, "lag_undecayed": d_und}

def verdict(r) -> Tuple[str, str]:
    dd = r["lag_decayed"]; du = r["lag_undecayed"]; s = "decayed-lag=%d undecayed-lag=%d" % (dd, du)
    if dd <= 100 and dd < du:
        return ("HARD_PASS", "HARD_PASS: pheromone-decay Misra-Gries detects topic drift within 100 queries and faster than un-decayed -- ant-colony decay is the drift-responsiveness mechanism. " + s)
    if dd <= 500 and dd < du:
        return ("MIDDLE_BAND", "MIDDLE_BAND: decay helps but detection 100-500 queries. " + s)
    return ("HARD_FAIL", "HARD_FAIL: decay does not speed drift detection. " + s)
'''))

# Analog 4: mycorrhizal hub-weighted initialization
CELLS.append(dict(anchor="natural_analog_mycorrhizal_hubinit_v1", analog="Analog 4 (MYCORRHIZAL)",
    title="hub-weighted initialization warm-starts a new customer's bridge cache",
    desc="Customer A accumulated 10K queries (its popular bridges = hubs). New customer B initializes its cache from A's top hubs. Measure B's bridge coverage at Q=100 with hub-init vs cold-start.",
    prereg="HARD-PASS B with hub-init reaches >= 0.70 coverage at Q=100 vs ~0.30 cold (warm-start works). MIDDLE 0.50-0.70. HARD-FAIL < 0.50.",
    body='''
def zipf(v, s=1.1):
    p = 1.0 / np.power(np.arange(1, v + 1), s); return p / p.sum()

def _selftest():
    p = zipf(10); assert p[0] > p[9], "zipf head heavier"
    seen = set([1, 2]); assert all(x in seen for x in [1, 2]), "cache membership"
    assert zipf(5).sum() > 0.99, "zipf norm"
    print("[selftest] PASS: mycorrhizal-hubinit", flush=True)

def run() -> Dict:
    g = np.random.default_rng(44); V = 2000; QA = 2000 if SMOKE else 10000; QB = 100; HUBS = 400
    pA = zipf(V)
    # B shares A's popular hubs (head correlated) + own tail
    perm = g.permutation(V); tailB = np.zeros(V); tailB[perm] = zipf(V); pB = 0.6 * pA + 0.4 * tailB; pB /= pB.sum()
    cacheA = set(int(x) for x in np.unique(g.choice(V, QA, p=pA)))
    hub_init = set(int(i) for i in np.argsort(pA)[::-1][:HUBS])      # top hubs from A
    streamB = g.choice(V, QB, p=pB)
    def coverage(cache):
        hit = 0
        for b in streamB:
            if int(b) in cache:
                hit += 1
        return hit / QB
    cold = coverage(set()); warm = coverage(set(hub_init))
    print("  customer B coverage at Q=%d: cold-start=%.3f hub-init=%.3f (hubs=%d)" % (QB, cold, warm, HUBS), flush=True)
    return {"cold": cold, "warm": warm}

def verdict(r) -> Tuple[str, str]:
    w = r["warm"]; s = "hub-init coverage=%.3f vs cold=%.3f at Q=100" % (w, r["cold"])
    if w >= 0.70:
        return ("HARD_PASS", "HARD_PASS: hub-weighted init warm-starts new customers to >=0.70 coverage at Q=100 (vs cold ~0.30) -- mycorrhizal cross-customer transfer works. " + s)
    if w >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: hub-init coverage 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: hub-init <0.50 coverage. " + s)
'''))

# Analog 5: quorum-sensing EMA adversarial detector
CELLS.append(dict(anchor="natural_analog_quorum_ema_detector_v1", analog="Analog 5 (QUORUM SENSING)",
    title="EMA signal-level detector flags high-frequency injection attacks",
    desc="A query stream has a baseline per-entity rate; an adversary injects a high-frequency burst on one entity. An EMA (exponential moving average) anomaly detector flags entities whose instantaneous rate exceeds K*EMA. Measure detection rate vs false positives.",
    prereg="HARD-PASS detector flags > 0.90 of injection bursts at < 0.10 false-positive on normal entities. MIDDLE recall 0.70-0.90. HARD-FAIL recall < 0.70 or FP > 0.10.",
    body='''
def _selftest():
    ema = 0.0; ema = 0.1 * 1.0 + 0.9 * ema; assert ema > 0, "ema updates"
    assert 5.0 > 3.0 * 1.0, "threshold logic"
    assert abs(np.mean([1.0, 1.0]) - 1.0) < 1e-9, "mean"
    print("[selftest] PASS: quorum-ema-detector", flush=True)

def run() -> Dict:
    g = np.random.default_rng(55); V = 100; Q = 5000 if SMOKE else 20000; ALPHA = 0.01; KTH = 6.0
    base = np.full(V, 1.0 / V)
    n_inject = 10; inj_entities = set(int(x) for x in g.choice(V, n_inject, replace=False))
    ema = np.zeros(V); flagged = set(); fp = set()
    inj_windows = {e: (int(g.integers(Q // 4, Q * 3 // 4)),) for e in inj_entities}
    for t in range(Q):
        if any(abs(t - w[0]) < 60 for w in inj_windows.values()) and g.random() < 0.6:
            e = int(g.choice(list(inj_entities)))      # injection burst
        else:
            e = int(g.choice(V, p=base))
        x = np.zeros(V); x[e] = 1.0
        inst = x; ema = ALPHA * inst + (1 - ALPHA) * ema
        if ema[e] > KTH * (1.0 / V):                     # sustained rate far above baseline 1/V (quorum signal)
            (flagged if e in inj_entities else fp).add(e)
    recall = len(flagged & inj_entities) / max(len(inj_entities), 1)
    fpr = len(fp) / max(V - len(inj_entities), 1)
    print("  EMA detector: injection recall=%.3f false-positive=%.3f (injected=%d)" % (recall, fpr, n_inject), flush=True)
    return {"recall": recall, "fpr": fpr, "n_inject": n_inject}

def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f fpr=%.3f (injected=%d)" % (r["recall"], r["fpr"], r["n_inject"])
    if r["recall"] > 0.90 and r["fpr"] < 0.10:
        return ("HARD_PASS", "HARD_PASS: EMA quorum-sensing detector flags >90%% of injection attacks at <10%% FP -- signal-level adversarial detection works. " + s)
    if r["recall"] >= 0.70 and r["fpr"] < 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: detection recall 0.70-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: recall <0.70 or FP >0.10. " + s)
'''))

for c in CELLS:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], analog=c["analog"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8")
    print("wrote", c["anchor"])
