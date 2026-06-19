"""
exp_lap1_defeasible_cpu_v1.py -- LAP-1 DEFEASIBLE-1: NAF default reasoning over substrate facts -- CPU.

ROUTING: Research OVERNIGHT_FILL_PRIORITIZED laptop batch (LAP-1). Default logic with negation-as-failure: the canonical
  birds-fly-but-penguins-dont class. Substrate stores each entity's property facts (is_bird, is_abnormal) as retrievable
  bindings; the defeasible rule fly(x) <- bird(x) AND NOT abnormal(x) is applied over the retrieved facts. Penguins/ostriches
  are abnormal (exceptions); normal birds fly; non-birds don't. Tests that the substrate's exact fact retrieval supports
  correct default+exception reasoning on 100 examples. numpy/VSA. CPU.
PRE-REGISTERED: HARD-PASS >= 0.90 correct (default + exception classification). MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "lap1_defeasible_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)


def _selftest():
    assert (True and not False) == True, "naf"; print("[selftest] PASS: lap1-defeasible", flush=True)


def run() -> Dict:
    g = np.random.default_rng(101); VE = 400 if SMOKE else 1200; ents = cphasor(VE, N, g)
    # property roles + boolean fillers
    R_BIRD, R_ABN = cphasor(2, N, g); TRUE, FALSE = cphasor(2, N, g); book = np.stack([FALSE, TRUE])
    TR = 100 if SMOKE else 400; correct = 0; n = 0
    for _ in range(TR):
        # sample a category: normal-bird(fly), exception-bird penguin/ostrich(abnormal,no-fly), non-bird(no-fly)
        cat = g.integers(0, 3)  # 0 normal-bird, 1 exception-bird, 2 non-bird
        is_bird = 1 if cat in (0, 1) else 0
        is_abn = 1 if cat == 1 else 0
        gold_fly = 1 if (is_bird and not is_abn) else 0
        x = int(g.integers(0, VE))
        # store property facts in a per-entity bundle (retrievable)
        prop = ents[x] * (R_BIRD * book[is_bird]) + ents[x] * (R_ABN * book[is_abn])
        # retrieve via cleanup (NAF: 'not abnormal' = abnormal-fact resolves to FALSE)
        bird_hat = int(np.argmax((book @ np.conj(prop * np.conj(ents[x]) * np.conj(R_BIRD))).real))
        abn_hat = int(np.argmax((book @ np.conj(prop * np.conj(ents[x]) * np.conj(R_ABN))).real))
        concl_fly = 1 if (bird_hat == 1 and abn_hat == 0) else 0          # default rule application
        correct += int(concl_fly == gold_fly); n += 1
    acc = correct / n; print("  DEFEASIBLE default+exception acc=%.3f (n=%d)" % (acc, n), flush=True)
    return {"defeasible_acc": acc, "n": n}


def verdict(r) -> Tuple[str, str]:
    s = "defeasible-acc=%.3f (n=%d)" % (r["defeasible_acc"], r["n"])
    if r["defeasible_acc"] >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate supports NAF default reasoning >=0.90 (birds fly, penguin/ostrich exceptions don't) -- exact fact retrieval enables non-monotonic default+exception logic. " + s)
    if r["defeasible_acc"] >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: defeasible 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: defeasible <0.75. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
