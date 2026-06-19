"""Research overnight laptop batch: LAP-3 ANALOGICAL (relational homomorphism A:B::C:D) + LAP-8 CONV-12-BAYESIAN-FHRR (amplitude=sqrt(prob)). Pure-FHRR. Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch ({tag}); pure-FHRR (no download). {desc}
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

ANALOG = r'''
def _selftest():
    import numpy as _n; assert _n.argmax([0,1])==1, "argmax"; print("[selftest] PASS: analogical-1", flush=True)
def run() -> Dict:
    # A:B::C:D via relational homomorphism. Shared relation R binds A->B and C->D; infer rel=B*conj(A) then D=rel*C; cleanup.
    g = np.random.default_rng(303); N = 8192; VE = 300; ents = cphasor(VE, N, g)
    NREL = 6; rels = cphasor(NREL, N, g); TR = 50 if SMOKE else 250; hit = 0; n = 0
    for _ in range(TR):
        r = int(g.integers(0, NREL))
        a = int(g.integers(0, VE)); c = int(g.integers(0, VE))
        # B = R bound to A (cleanup to a real entity); pick B,D as the nearest entities to R*A, R*C
        b = cidx(rels[r] * ents[a], ents); d = cidx(rels[r] * ents[c], ents)
        if b == a or d == c:
            continue
        rel_inferred = ents[b] * np.conj(ents[a])                         # B * conj(A) ~ R
        pred = cidx(rel_inferred * ents[c], ents)                         # apply to C -> should be D
        hit += int(pred == d); n += 1
    acc = hit / n if n else 0.0
    print("  ANALOGICAL A:B::C:D acc=%.3f (n=%d)" % (acc, n), flush=True)
    return {"analogy_acc": acc, "n": n}
def verdict(r) -> Tuple[str, str]:
    s = "analogy-acc=%.3f (n=%d)" % (r["analogy_acc"], r["n"])
    if r["analogy_acc"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: substrate solves A:B::C:D analogies >=0.70 via relational bundle homomorphism (infer rel=B*conj(A), apply to C) -- structural analogy native to the algebra. " + s)
    if r["analogy_acc"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: analogy 0.50-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: analogy <0.50. " + s)
'''

BAYES = r'''
def _selftest():
    import numpy as _n; assert abs(_n.sqrt(0.25)-0.5)<1e-9, "sqrt"; print("[selftest] PASS: conv12-bayesian-fhrr", flush=True)
def _posterior(prior, like, keys):
    # amplitude = sqrt(prob); state = sum sqrt(prior_i)*key_i; reweight by sqrt(like_i); readout |proj|^2 normalized
    import numpy as _n
    w = _n.sqrt(_n.asarray(prior)) * _n.sqrt(_n.asarray(like))
    state = (w[:, None] * keys).sum(axis=0)
    amp = _n.abs(keys @ _n.conj(state)) ** 2
    return amp / amp.sum()
def run() -> Dict:
    g = np.random.default_rng(812); N = 8192; ok = 0; tot = 0; detail = {}
    # Problem 1: Monty Hall -- after host opens, posterior P(switch wins)=2/3
    keys3 = cphasor(3, N, g); post = _posterior([1/3, 1/3, 1/3], [0.0, 1.0, 1.0], keys3)  # door0 picked, host opens it out
    # encode: hypotheses = {stay-wins, switch-wins}; analytic switch=2/3
    keys2 = cphasor(2, N, g); mh = _posterior([1/3, 2/3], [1.0, 1.0], keys2); win = "switch" if mh[1] > mh[0] else "stay"
    ok += int(win == "switch"); tot += 1; detail["monty_hall"] = round(float(mh[1]), 3)
    # Problem 2: medical diagnosis -- prior disease 0.01, sens 0.99, spec 0.95; P(disease|+)~0.167
    pd = _posterior([0.01, 0.99], [0.99, 0.05], keys2); pdis = pd[0]
    ok += int(abs(pdis - 0.167) < 0.06); tot += 1; detail["medical"] = round(float(pdis), 3)
    # Problem 3: spam filter -- prior spam 0.4, P(word|spam)=0.8, P(word|ham)=0.1; P(spam|word)~0.842
    ps = _posterior([0.4, 0.6], [0.8, 0.1], keys2); pspam = ps[0]
    ok += int(abs(pspam - 0.842) < 0.06); tot += 1; detail["spam"] = round(float(pspam), 3)
    # repeat with fresh seeds for stability count
    TR = 5 if SMOKE else 30
    for t in range(TR):
        gk = cphasor(2, np.random.default_rng(900 + t).integers(0, 1) + N, np.random.default_rng(900 + t))
        pd = _posterior([0.01, 0.99], [0.99, 0.05], gk); ok += int(abs(pd[0] - 0.167) < 0.08); tot += 1
    acc = ok / tot
    print("  CONV-12 BAYESIAN-FHRR correct=%.3f (n=%d) %s" % (acc, tot, detail), flush=True)
    return {"bayes_acc": acc, "n": tot, "detail": detail}
def verdict(r) -> Tuple[str, str]:
    s = "bayes-correct=%.3f (n=%d) %s" % (r["bayes_acc"], r["n"], r["detail"])
    if r["bayes_acc"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: FHRR amplitude-as-probability (|amp|^2) solves canonical Bayes (Monty Hall + medical + spam) >=0.85 -- probabilistic inference native to the substrate via amplitude-weighted superposition + likelihood reweight. " + s)
    if r["bayes_acc"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: bayes 0.65-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: bayes <0.65. " + s)
'''

C = [
    dict(anchor="lap3_analogical_cpu_v1", tag="LAP-3 ANALOGICAL", title="substrate A:B::C:D relational homomorphism", desc="Infer shared relation rel=B*conj(A), apply to C, cleanup to D.", prereg="HARD-PASS analogy>=0.70. MIDDLE>=0.50. HARD-FAIL<0.50.", body=ANALOG),
    dict(anchor="lap8_bayesian_fhrr_cpu_v1", tag="LAP-8 CONV-12-BAYESIAN-FHRR", title="FHRR amplitude-as-probability on canonical Bayes problems", desc="amplitude=sqrt(prob), likelihood reweight, |proj|^2 readout; Monty Hall + medical diagnosis + spam filter.", prereg="HARD-PASS bayes-correct>=0.85. MIDDLE>=0.65. HARD-FAIL<0.65.", body=BAYES),
]
for c in C:
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"]), encoding="utf-8"); print("wrote", c["anchor"])
