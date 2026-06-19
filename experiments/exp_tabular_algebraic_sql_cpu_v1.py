"""
exp_tabular_algebraic_sql_cpu_v1.py -- SELECT-WHERE over a substrate-encoded table via algebraic queries (SQL-equivalent) -- CPU.

ROUTING: strong-batch (CAP-7 tabular algebraic SQL). Encode a relational table (rows with column=value cells) into substrate; answer SELECT col WHERE other_col=val by binding the constraint and reading the projected column. Tests substrate as an algebraic SQL engine (HDDB precedent). Pure numpy. CPU.
PRE-REGISTERED: HARD-PASS SQL-equivalent SELECT-WHERE correctness >= 0.95 on a synthetic table. MIDDLE >= 0.85. HARD-FAIL < 0.85.
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
ANCHOR_NAME = "tabular_algebraic_sql_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))

def _selftest():
    g = np.random.default_rng(0); c = cphasor(1, 64, g)[0]; v = cphasor(1, 64, g)[0]; assert np.allclose(c*v*np.conj(c), v, atol=1e-3), "cell bind"; print("[selftest] PASS: tabular-algebraic-sql", flush=True)
def run() -> Dict:
    g = np.random.default_rng(903); N = 8192; NCOL = 5; VCARD = 20; NROW = 60 if SMOKE else 150; TR = 30 if SMOKE else 80
    cols = cphasor(NCOL, N, g); vals = cphasor(VCARD, N, g); rowid = None
    hit = 0; tot = 0
    for _ in range(TR):
        rows = g.integers(0, VCARD, (NROW, NCOL)); rowvecs = cphasor(NROW, N, g)
        # table memory: each row = bundle of col*value ; plus a row-keyed store for projection
        M = np.zeros(N, dtype=np.complex64); rowmem = np.zeros((NROW, N), dtype=np.complex64)
        for ri in range(NROW):
            rv = np.zeros(N, dtype=np.complex64)
            for ci in range(NCOL):
                rv = rv + cols[ci] * vals[int(rows[ri, ci])]
            rowmem[ri] = rv
        # query: SELECT proj_col WHERE where_col = where_val ; verify projected value matches the matching row(s)
        where_c = int(g.integers(0, NCOL)); where_v = int(g.integers(0, VCARD)); proj_c = int(g.integers(0, NCOL))
        matches = [ri for ri in range(NROW) if rows[ri, where_c] == where_v]
        if not matches:
            continue
        ri = matches[0]
        # find a row matching the WHERE by scoring rows on col*val, then project the SELECT column
        wq = cols[where_c] * vals[where_v]; scores = (rowmem @ np.conj(wq)).real / N; cand = int(np.argmax(scores))
        proj_val = cidx(rowmem[cand] * np.conj(cols[proj_c]), vals)
        hit += int(rows[cand, where_c] == where_v and proj_val == rows[cand, proj_c]); tot += 1
    acc = hit / max(1, tot); print("  algebraic SELECT-WHERE correctness=%.3f (NROW=%d, n=%d)" % (acc, NROW, tot), flush=True)
    return {"acc": acc, "nrow": NROW}
def verdict(r) -> Tuple[str, str]:
    s = "SELECT-WHERE correctness=%.3f (NROW=%d)" % (r["acc"], r["nrow"])
    if r["acc"] >= 0.95: return ("HARD_PASS", "HARD_PASS: substrate algebraic SELECT-WHERE >=0.95 -- substrate as a SQL-equivalent tabular query engine. " + s)
    if r["acc"] >= 0.85: return ("MIDDLE_BAND", "MIDDLE_BAND: tabular SQL 0.85-0.95. " + s)
    return ("HARD_FAIL", "HARD_FAIL: tabular SQL <0.85. " + s)

_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
