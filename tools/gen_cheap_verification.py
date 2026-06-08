"""Generator: cheap verification/confidence cluster CHEAP-1..4 (contradiction / gap-score / PP-107 tiers / factual AUC). Write-tool authored."""
import pathlib
EXP = pathlib.Path(__file__).resolve().parent.parent / "experiments"
HEAD = '''"""
exp_{anchor}.py -- {title} -- CPU.

ROUTING: 8_DRILLS cheap-decisive batch ({tag}). {desc} Pure numpy FHRR. CPU.
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
def scores(v, book):
    return (book @ np.conj(v)).real / book.shape[1]
def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg); c = 0; t = 0
    for p in pos:
        c += (neg < p).sum() + 0.5 * (neg == p).sum(); t += len(neg)
    return c / max(1, t)
def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = math.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0
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
C.append(dict(anchor="cheap1_contradiction_detect_cpu_v1", tag="CHEAP-1 ACC-style contradiction detection",
  title="pre-output conflict detection: small top1-top2 gap flags contradictory facts",
  desc="ACC-style (Botvinick 2001) conflict monitor: a subject with two competing equally-bound objects for the same relation yields a SMALL top1-top2 cleanup gap (conflict); a clean single-object fact yields a LARGE gap. Flag contradiction when gap < threshold. Directly a hallucination/conflict pre-check.",
  prereg="HARD-PASS contradiction recall >= 0.90 AND false-positive rate < 0.02 on a 200-item KB. MIDDLE recall >= 0.80 / FP < 0.05. HARD-FAIL below.",
  body='''
def _selftest():
    g = np.random.default_rng(0); a = cphasor(3, 64, g); s = a[0] + a[1]; sc = scores(s, a); assert sc[2] < min(sc[0], sc[1]), "conflict"; print("[selftest] PASS: cheap1-contradiction-detect", flush=True)
def run() -> Dict:
    g = np.random.default_rng(611); N = 8192; VE = 200; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 80 if SMOKE else 200; THRESH = 0.25
    det = 0; ncon = 0; fp = 0; nclean = 0
    for _ in range(TR):
        s = int(g.integers(0, VE))
        if g.random() < 0.5:  # CONTRADICTION: two competing objects, same relation
            o1, o2 = g.choice(VE, 2, replace=False); shard = ents[int(o1)] * REL + ents[int(o2)] * REL
            ncon += 1; rec = shard * np.conj(REL); sc = np.sort(scores(rec, ents))[::-1]; gap = sc[0] - sc[1]
            det += int(gap < THRESH)
        else:                 # CLEAN: single object
            o = int(g.integers(0, VE)); shard = ents[o] * REL
            nclean += 1; rec = shard * np.conj(REL); sc = np.sort(scores(rec, ents))[::-1]; gap = sc[0] - sc[1]
            fp += int(gap < THRESH)
    rc = det / max(1, ncon); fpr = fp / max(1, nclean); print("  contradiction recall=%.3f FP-rate=%.3f (n_con=%d n_clean=%d)" % (rc, fpr, ncon, nclean), flush=True)
    return {"recall": rc, "fp": fpr}
def verdict(r) -> Tuple[str, str]:
    s = "recall=%.3f FP-rate=%.3f" % (r["recall"], r["fp"])
    if r["recall"] >= 0.90 and r["fp"] < 0.02: return ("HARD_PASS", "HARD_PASS: ACC-style contradiction detection >=0.90 recall, <0.02 FP -- pre-output conflict/hallucination pre-check works. " + s)
    if r["recall"] >= 0.80 and r["fp"] < 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: contradiction 0.80-0.90 / FP<0.05. " + s)
    return ("HARD_FAIL", "HARD_FAIL: contradiction detection weak. " + s)
'''))
C.append(dict(anchor="cheap2_gap_score_uncertainty_cpu_v1", tag="CHEAP-2 gap-score uncertainty signal",
  title="top1-top2 cleanup gap correlates with answer correctness (second-order uncertainty)",
  desc="The cleanup gap (top-1 minus top-2 similarity) is a usable uncertainty signal: when the substrate answer is correct the gap is large, when wrong/uncertain it is small. Vary distractor load so correctness varies; measure Spearman(gap, correct).",
  prereg="HARD-PASS AUC(gap separates correct vs incorrect) >= 0.75. MIDDLE >= 0.65. HARD-FAIL < 0.65.",
  body='''
def _selftest():
    assert abs(spearman([1,2,3,4],[1,2,3,4]) - 1.0) < 1e-9, "spearman"; print("[selftest] PASS: cheap2-gap-score-uncertainty", flush=True)
def run() -> Dict:
    g = np.random.default_rng(612); N = 4096; VE = 400; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 150 if SMOKE else 500
    gaps = []; correct = []
    for _ in range(TR):
        s = int(g.integers(0, VE)); o = int(g.integers(0, VE)); load = int(g.integers(5, 400))  # wide load -> correctness spans (needed for correlation)
        shard = ents[s] * REL * ents[o]
        for _d in range(load):
            shard = shard + ents[int(g.integers(0, VE))] * REL * ents[int(g.integers(0, VE))]
        rec = shard * np.conj(ents[s] * REL); allsc = scores(rec, ents); order = np.sort(allsc)[::-1]; gap = order[0] - order[1]
        pred = int(np.argmax(allsc)); gaps.append(gap); correct.append(int(pred == o))
    gaps = np.array(gaps); correct = np.array(correct)
    gc = gaps[correct == 1]; gw = gaps[correct == 0]
    a = auc(gc, gw) if (len(gc) and len(gw)) else 0.5; rho = spearman(gaps, correct); acc = float(correct.mean())
    print("  AUC(gap|correct-vs-wrong)=%.3f (point-biserial rho=%.3f, acc=%.3f, n=%d)" % (a, rho, acc, TR), flush=True)
    return {"auc": a, "spearman": rho, "acc": acc}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f (rho=%.3f, acc=%.3f)" % (r["auc"], r["spearman"], r["acc"])
    if r["auc"] >= 0.75: return ("HARD_PASS", "HARD_PASS: cleanup gap-score separates correct vs incorrect answers AUC>=0.75 -- usable second-order uncertainty/abstention signal. " + s)
    if r["auc"] >= 0.65: return ("MIDDLE_BAND", "MIDDLE_BAND: gap-AUC 0.65-0.75. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gap-AUC <0.65. " + s)
'''))
C.append(dict(anchor="cheap3_pp107_tiers_cpu_v1", tag="CHEAP-3 PP-107 confidence as graded population code",
  title="cleanup confidence tracks graded similarity tiers monotonically, with graceful noise degradation",
  desc="Store values at controlled cosine-similarity tiers to a probe (0.60-1.00); under query noise, the cleanup confidence should track the tier monotonically (Spearman high) and degrade gracefully -- the substrate confidence is a graded population-code-like signal, not binary.",
  prereg="HARD-PASS Spearman(confidence, tier) > 0.85 AND ranking preserved under noise. MIDDLE > 0.70. HARD-FAIL <= 0.70.",
  body='''
def _selftest():
    assert abs(spearman([1,2,3],[1,2,3]) - 1.0) < 1e-9, "spearman"; print("[selftest] PASS: cheap3-pp107-tiers", flush=True)
def run() -> Dict:
    g = np.random.default_rng(613); N = 8192; TIERS = [0.60,0.70,0.80,0.90,1.00]; TR = 60 if SMOKE else 200
    confs = []; tiervals = []
    for _ in range(TR):
        base = cphasor(1, N, g)[0]
        for t in TIERS:
            # mix base with a random vector to hit target real-cosine ~ t, then add query noise
            r = cphasor(1, N, g)[0]; mixed = t * base + math.sqrt(max(0.0,1-t*t)) * r; mixed = mixed / (np.abs(mixed)+1e-8)
            noisy = base * np.exp(1j * 0.15 * g.standard_normal(N)); noisy = noisy/(np.abs(noisy)+1e-8)
            conf = float((mixed @ np.conj(noisy)).real / N); confs.append(conf); tiervals.append(t)
    rho = spearman(confs, tiervals); print("  Spearman(confidence, tier)=%.3f (n=%d, noise=0.15)" % (rho, len(confs)), flush=True)
    return {"spearman": rho}
def verdict(r) -> Tuple[str, str]:
    s = "Spearman(conf,tier)=%.3f" % r["spearman"]
    if r["spearman"] > 0.85: return ("HARD_PASS", "HARD_PASS: cleanup confidence tracks graded tiers >0.85 under noise -- graded population-code-like confidence (PP-107) confirmed. " + s)
    if r["spearman"] > 0.70: return ("MIDDLE_BAND", "MIDDLE_BAND: tier-tracking 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: tier-tracking <=0.70. " + s)
'''))
C.append(dict(anchor="cheap4_factual_confidence_auc_cpu_v1", tag="CHEAP-4 substrate confidence as factual predictor",
  title="cleanup confidence separates true from hallucinated claims (AUC)",
  desc="For a claim (subject, relation, claimed-object), the substrate cleanup confidence (score of the claimed object after unbinding subject*relation from the KB shard) is high for TRUE claims (object actually bound) and low for HALLUCINATED claims (wrong object). Measures AUC of confidence as a factual-vs-hallucinated classifier -- a customer-presentable hallucination-detection number.",
  prereg="HARD-PASS confidence AUC >= 0.90 (true vs hallucinated). MIDDLE >= 0.80. HARD-FAIL < 0.80.",
  body='''
def _selftest():
    assert auc([0.9,0.8],[0.1,0.2]) == 1.0, "auc"; print("[selftest] PASS: cheap4-factual-confidence-auc", flush=True)
def run() -> Dict:
    g = np.random.default_rng(614); N = 8192; VE = 300; REL = cphasor(1, N, g)[0]; ents = cphasor(VE, N, g); TR = 80 if SMOKE else 250
    pos = []; neg = []
    for _ in range(TR):
        s = int(g.integers(0, VE)); deg = int(g.integers(2, 6)); objs = g.choice(VE, deg, replace=False)
        shard = np.zeros(N, dtype=np.complex64)
        for o in objs:
            shard = shard + ents[int(o)] * REL
        rec = shard * np.conj(REL)
        true_o = int(objs[0]); pos.append(float(scores(rec, ents)[true_o]))   # true claim confidence
        wrong = int(g.integers(0, VE))
        while wrong in objs:
            wrong = int(g.integers(0, VE))
        neg.append(float(scores(rec, ents)[wrong]))                            # hallucinated claim confidence
    a = auc(pos, neg); print("  factual-confidence AUC=%.3f (true mean=%.3f, halluc mean=%.3f, n=%d)" % (a, float(np.mean(pos)), float(np.mean(neg)), len(pos)), flush=True)
    return {"auc": a}
def verdict(r) -> Tuple[str, str]:
    s = "AUC=%.3f" % r["auc"]
    if r["auc"] >= 0.90: return ("HARD_PASS", "HARD_PASS: substrate confidence separates true vs hallucinated claims AUC>=0.90 -- usable factual-accuracy/hallucination predictor (EU AI Act verification claim). " + s)
    if r["auc"] >= 0.80: return ("MIDDLE_BAND", "MIDDLE_BAND: factual AUC 0.80-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: factual AUC <0.80. " + s)
'''))
for c in C:
    txt = HEAD.format(anchor=c["anchor"], title=c["title"], tag=c["tag"], desc=c["desc"], prereg=c["prereg"], body=c["body"])
    (EXP / ("exp_" + c["anchor"] + ".py")).write_text(txt, encoding="utf-8"); print("wrote", c["anchor"])
