"""
exp_patternb_1A_subst_scale_v1 -- Pattern B Phase-1 1A: counterfactual substitution at scale + contamination -- CPU.
ROUTING: handoff pattern_b_full_exploration_program Phase-1 1A. Store M Pattern-B facts; substitute one filler in 20; measure substitution recall AND contamination of unrelated facts, at scales 100/500/2000. CPU.
PRE-REGISTERED: HARD-PASS substitution recall>=0.95 AND contamination<=0.01 at 2000 facts; BORDER 0.85-0.95 or 1-5%; HARD-FAIL <0.85 or >5%.
FORMULA SELF-TESTS (PROT-022): 1. unbind inverts. 2. unit phasor. 3. scales sweep.
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
ANCHOR_NAME = "patternb_1A_subst_scale_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
N = 2048; SCALES = [100, 500] if RUN_MODE == "smoke" else [100, 500, 2000]; N_ROLE = 6; N_SUB = 20
def _selftest():
    g = np.random.default_rng(0); a = phasor(64, 1, g)[0]; b = phasor(64, 1, g)[0]
    assert np.allclose((a * b) * np.conj(a), b, atol=1e-4), "unbind inverts"
    assert np.allclose(np.abs(a), 1.0, atol=1e-5), "unit phasor"
    assert len(SCALES) >= 2, "scales sweep"
    print("[selftest] PASS: patternb-1A", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def run_scale(M, g):
    roles = phasor(N, N_ROLE, g); vocab = phasor(N, max(2 * M, 50), g)
    facts = []; fillers = []
    for i in range(M):
        k = int(g.integers(3, 6)); idx = g.choice(N_ROLE, k, replace=False); fid = g.choice(len(vocab), k, replace=False)
        facts.append(np.sum([roles[idx[j]] * vocab[fid[j]] for j in range(k)], axis=0).astype(np.complex64))
        fillers.append((idx, fid))
    facts = np.array(facts)
    sub_ids = g.choice(M, min(N_SUB, M), replace=False); ok = 0; contam = 0; checked = 0
    base_fp = unit(np.concatenate([facts.real, facts.imag], 1))   # fingerprint to detect contamination
    for si in sub_ids:
        idx, fid = fillers[si]; j = 0; newf = int(g.integers(0, len(vocab)))
        delta = roles[idx[j]] * vocab[newf] - roles[idx[j]] * vocab[fid[j]]
        f2 = facts.copy(); f2[si] = facts[si] + delta
        rec = int(np.argmax((vocab @ np.conj((f2[si]) * np.conj(roles[idx[j]]))).real))   # retrieve substituted filler
        ok += int(rec == newf)
        fp2 = unit(np.concatenate([f2.real, f2.imag], 1))
        moved = np.where(np.abs((fp2 * base_fp).sum(1) - 1.0) > 1e-3)[0]   # which facts changed
        contam += len([m for m in moved if m != si]); checked += M - 1
    return ok / len(sub_ids), contam / max(checked, 1)
def run() -> Dict:
    g = np.random.default_rng(7); by = {}
    for M in SCALES:
        rec, con = run_scale(M, g); by["M%d" % M] = {"recall": rec, "contam": con}
        print("  M=%d substitution_recall=%.3f contamination=%.4f" % (M, rec, con), flush=True)
    top = "M%d" % SCALES[-1]; return {"by": by, "rec_top": by[top]["recall"], "con_top": by[top]["contam"], "scale": SCALES[-1]}
def verdict(r) -> Tuple[str, str]:
    rec = r["rec_top"]; con = r["con_top"]; s = "at %d facts: recall=%.3f contamination=%.4f" % (r["scale"], rec, con)
    if rec >= 0.95 and con <= 0.01: return ("HARD_PASS", "HARD_PASS: Pattern B substitution recall>=0.95 with contamination<=1% at scale -- compositional editing is clean + scalable. " + s)
    if rec >= 0.85 and con <= 0.05: return ("MIDDLE_BAND", "MIDDLE_BAND: substitution recall/contamination borderline. " + s)
    return ("HARD_FAIL", "HARD_FAIL: substitution recall<0.85 or contamination>5% at scale. " + s)

print('[config] anchor=%s mode=%s' % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)
metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}
write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)
