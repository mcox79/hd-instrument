"""
exp_type_confusion_disambig_cpu_v1.py -- context-conditioned disambiguation of same-name-different-referent entities -- CPU.

ROUTING: NEW_EXPERIMENTS batch (N5 type-confusion stress (same name, different referent)). Build a KB with many same-NAME-different-referent entities (Apple-company vs apple-fruit). Each reference is name * context. Tests whether binding the disambiguating context resolves to the correct referent. Failure-mode-catalog input for named-entity ambiguity. Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS context-resolvable references disambiguated >= 0.90. MIDDLE >= 0.75. HARD-FAIL < 0.75.
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
ANCHOR_NAME = "type_confusion_disambig_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); name = cphasor(1, 32, g)[0]; ctx = cphasor(1, 32, g)[0]; ref = cphasor(1, 32, g)[0]
    assert np.allclose(name * ctx * ref * np.conj(name * ctx), ref, atol=1e-3), "name-ctx bind"; print("[selftest] PASS: type-confusion-disambig", flush=True)
def run() -> Dict:
    g = np.random.default_rng(224); N = 4096; NNAME = 50; SENSE = 3; NCTX = 40; TR = 60 if SMOKE else 200
    names = cphasor(NNAME, N, g); ctxs = cphasor(NCTX, N, g); VR = NNAME * SENSE; refs = cphasor(VR, N, g)
    # each (name, sense) referent has a characteristic context set; store name*ctx*referent
    M = np.zeros(N, dtype=np.complex64); sense_ctx = {}
    for nm in range(NNAME):
        for se in range(SENSE):
            ref_id = nm * SENSE + se; cset = g.choice(NCTX, 4, replace=False)
            sense_ctx[(nm, se)] = set(cset.tolist())
            for c in cset:
                M = M + names[nm] * ctxs[int(c)] * refs[ref_id]
    hit = 0; n = 0
    for _ in range(TR):
        nm = int(g.integers(0, NNAME)); se = int(g.integers(0, SENSE)); c = int(np.random.default_rng(g.integers(0, 1 << 30)).choice(list(sense_ctx[(nm, se)])))
        pred = cidx(M * np.conj(names[nm] * ctxs[c]), refs); hit += int(pred == nm * SENSE + se); n += 1
    rec = hit / n; print("  type-confusion disambiguation=%.3f (%d names x %d senses, n=%d)" % (rec, NNAME, SENSE, n), flush=True)
    return {"recall": rec}
def verdict(r) -> Tuple[str, str]:
    s = "context-disambiguation=%.3f" % r["recall"]
    if r["recall"] >= 0.90: return ("HARD_PASS", "HARD_PASS: same-name-different-referent disambiguated by context >=0.90 -- named-entity ambiguity handled via context binding. " + s)
    if r["recall"] >= 0.75: return ("MIDDLE_BAND", "MIDDLE_BAND: disambiguation 0.75-0.90. " + s)
    return ("HARD_FAIL", "HARD_FAIL: disambiguation <0.75. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
