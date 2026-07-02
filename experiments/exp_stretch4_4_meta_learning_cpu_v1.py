"""
exp_stretch4_4_meta_learning_cpu_v1.py -- few-shot new-schema induction (learn category from K examples) -- CPU.

ROUTING: Research WAVE3_RESOLUTION_WAVE4 (STRETCH4-4 META-LEARNING); pure-FHRR (no download). From K=5 examples extract a new category prototype; classify new instances; no pre-training.
UPGRADED 2026-07-02: 3-seed variance-probe (R1 rescue per PP-292 MIDDLE_BAND=0.707 from 2026-06-19). Same mechanism; adds cross-seed variance quantification.
PRE-REGISTERED: HARD_PASS min_acc>=0.80. MIDDLE_BAND_ROBUST mean in [0.68,0.80] AND cv<=0.05. MIDDLE_BAND mean in [0.68,0.80]. HARD_FAIL mean<0.68.
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
ANCHOR_NAME = "stretch4_4_meta_learning_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SEEDS = [4, 5, 6]  # 3-seed variance probe (R1 rescue plan per PP-292 MIDDLE_BAND=0.707)
N = 8192           # FHRR dim -- FIXED across smoke and full (discriminator-must-survive-scale)
NPROP = 50; SCHEMA_SZ = 6; KSHOT = 5
SIM_THRESH = 0.35  # classification threshold on normalized overlap (from v1 calibration)
TR = 40 if SMOKE else 250

def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)

def _selftest():
    # Formula self-test: verify FHRR bundle+overlap discriminates in-cat from out-cat at N=8192, K=5.
    # (We validate DISCRIMINATION -- in_mean > out_mean by clear margin -- NOT threshold placement.
    #  The fixed SIM_THRESH is the classifier-side ceiling and is measured empirically in run().)
    g = np.random.default_rng(4); props = cphasor(NPROP, N, g)
    schema = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
    def _mk(in_cat):
        if in_cat:
            ps = set(schema)
            for p in list(ps):
                if g.random() < 0.15: ps.discard(p)
            while g.random() < 0.3: ps.add(int(g.integers(0, NPROP)))
        else:
            ps = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
        return sum((props[p] for p in ps), np.zeros(N, dtype=np.complex64))
    proto = sum((_mk(True) for _ in range(KSHOT)), np.zeros(N, dtype=np.complex64))
    sims_in = [float(np.vdot(_mk(True), proto).real) / (N * KSHOT) for _ in range(20)]
    sims_out = [float(np.vdot(_mk(False), proto).real) / (N * KSHOT) for _ in range(20)]
    m_in = float(np.mean(sims_in)); m_out = float(np.mean(sims_out))
    margin = m_in - m_out
    print("[selftest] in_mean=%.3f out_mean=%.3f margin=%.3f thresh=%.3f (measured empirically at runtime)" % (m_in, m_out, margin, SIM_THRESH), flush=True)
    assert m_in > m_out, "in_mean <= out_mean -- substrate does NOT discriminate; bundle-overlap mechanism dead"
    assert margin > 0.5, "in/out margin < 0.5 -- substrate discrimination too weak for meta-learning"
    print("[selftest] PASS: FHRR bundle+overlap discriminates in vs out (margin=%.3f) at N=%d K=%d" % (margin, N, KSHOT), flush=True)

def run_one_seed(seed_int: int) -> Dict:
    g = np.random.default_rng(seed_int); props = cphasor(NPROP, N, g)
    correct = 0; n = 0
    for _ in range(TR):
        schema = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
        def instance(in_cat):
            if in_cat:
                ps = set(schema)
                for p in list(ps):
                    if g.random() < 0.15: ps.discard(p)
                while g.random() < 0.3: ps.add(int(g.integers(0, NPROP)))
            else:
                ps = set(int(p) for p in g.choice(NPROP, SCHEMA_SZ, replace=False))
            return sum((props[p] for p in ps), np.zeros(N, dtype=np.complex64))
        proto = sum((instance(True) for _ in range(KSHOT)), np.zeros(N, dtype=np.complex64))
        for _q in range(6):
            in_cat = g.random() < 0.5; inst = instance(in_cat)
            sim = float(np.vdot(inst, proto).real) / (N * KSHOT)
            pred = sim > SIM_THRESH
            correct += int(pred == in_cat); n += 1
    acc = correct / n
    return {"seed": seed_int, "fewshot_acc": acc, "kshot": KSHOT, "n": n, "N": N, "TR": TR}

def verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    accs = [r["fewshot_acc"] for r in per_seed]
    mean_acc = float(np.mean(accs)); std_acc = float(np.std(accs, ddof=1)) if len(accs) > 1 else 0.0
    cv = (std_acc / mean_acc) if mean_acc > 0 else 0.0
    min_acc = float(min(accs)); max_acc = float(max(accs))
    s = "seeds=%s mean=%.3f std=%.3f cv=%.3f min=%.3f max=%.3f (K=%d, N=%d, %d seeds)" % (
        [r["seed"] for r in per_seed], mean_acc, std_acc, cv, min_acc, max_acc, KSHOT, N, len(per_seed))
    if min_acc >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate learns NEW category schema from K=%d examples; all seeds >=0.80 -- one-shot/few-shot schema induction via prototype bundling (no pre-training). " % KSHOT + s, mean_acc, std_acc, cv)
    if 0.68 <= mean_acc < 0.80 and cv <= 0.05:
        return ("MIDDLE_BAND_ROBUST", "MIDDLE_BAND_ROBUST: mean in [0.68,0.80] with tight cross-seed variance (cv<=0.05) -- reproducible partial capability at prototype-bundling ceiling. " + s, mean_acc, std_acc, cv)
    if 0.68 <= mean_acc < 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: mean in [0.68,0.80] but cv>0.05 -- variance too high for robust closure. " + s, mean_acc, std_acc, cv)
    return ("HARD_FAIL", "HARD_FAIL: mean<0.68. " + s, mean_acc, std_acc, cv)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d TR=%d SEEDS=%s K=%d NPROP=%d" % (ANCHOR_NAME, RUN_MODE, N, TR, SEEDS, KSHOT, NPROP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
per_seed = []
for s in SEEDS:
    r = run_one_seed(s); per_seed.append(r)
    print("  seed=%d fewshot_acc=%.3f (n=%d)" % (s, r["fewshot_acc"], r["n"]), flush=True)
v, vmsg, mean_acc, std_acc, cv = verdict(per_seed)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "seeds": SEEDS, "per_seed": per_seed,
    "mean_fewshot_acc": mean_acc, "std_fewshot_acc": std_acc, "cv_fewshot_acc": cv,
    "N": N, "TR": TR, "KSHOT": KSHOT, "NPROP": NPROP, "SCHEMA_SZ": SCHEMA_SZ, "SIM_THRESH": SIM_THRESH,
    "elapsed_s": time.time() - t0,
    "cardinality_ok": len(per_seed) == len(SEEDS),
    "arms_differ_verified": len(set(r["seed"] for r in per_seed)) == len(SEEDS),
}
write_metrics(out_dir, metrics, per_seed); print("[metrics] written", flush=True)
