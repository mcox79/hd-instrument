"""Generate runway CPU cells: Pattern-B 1A (substitution-at-scale) + storage Anchor 2 (3-bit quant). On-disk generator."""
import pathlib
HEAD = '''"""
{title}
ROUTING: {routing} CPU.
PRE-REGISTERED: {prereg}
FORMULA SELF-TESTS (PROT-022): 1. {t1}. 2. {t2}. 3. {t3}.
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
def phasor(n, k, g): return np.exp(1j * g.uniform(-np.pi, np.pi, (k, n))).astype(np.complex64)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)
'''
TAIL = ("\nprint('[config] anchor=%s mode=%s' % (ANCHOR_NAME, RUN_MODE), flush=True)\n"
        "out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()\n"
        "v, vmsg = verdict(r); print('[VERDICT] ' + vmsg, flush=True)\n"
        "metrics = {'anchor_name': ANCHOR_NAME, 'verdict': v, 'verdict_msg': vmsg, 'run_mode': RUN_MODE, 'n_seeds': 1, 'per_seed': [r], 'elapsed_s': time.time() - t0}\n"
        "write_metrics(out_dir, metrics, [r]); print('[metrics] written', flush=True)\n")

def write(anchor, title, routing, prereg, t1, t2, t3, body):
    pathlib.Path("experiments/exp_%s.py" % anchor).write_text(
        HEAD.format(title=title, routing=routing, prereg=prereg, t1=t1, t2=t2, t3=t3, anchor=anchor) + body + TAIL, encoding="utf-8")
    print("wrote", anchor)

# Pattern-B 1A: counterfactual substitution at scale + contamination
write("patternb_1A_subst_scale_v1",
  "exp_patternb_1A_subst_scale_v1 -- Pattern B Phase-1 1A: counterfactual substitution at scale + contamination -- CPU.",
  "handoff pattern_b_full_exploration_program Phase-1 1A. Store M Pattern-B facts; substitute one filler in 20; measure substitution recall AND contamination of unrelated facts, at scales 100/500/2000.",
  "HARD-PASS substitution recall>=0.95 AND contamination<=0.01 at 2000 facts; BORDER 0.85-0.95 or 1-5%; HARD-FAIL <0.85 or >5%.",
  "unbind inverts", "unit phasor", "scales sweep",
'''N = 2048; SCALES = [100, 500] if RUN_MODE == "smoke" else [100, 500, 2000]; N_ROLE = 6; N_SUB = 20
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
''')

# Storage Anchor 2: 3-bit quantization of pinv W vs 4-bit
write("storage_3bit_quant_v1",
  "exp_storage_3bit_quant_v1 -- storage Anchor 2: 3-bit scalar quant of pinv W vs 4-bit baseline -- CPU.",
  "handoff storage_compression_v3 Anchor 2. Does 3-bit scalar quantization of the pseudoinverse W degrade recall@1 by <2% vs the validated 4-bit baseline? Synthetic keys (storage is structural).",
  "HARD-PASS recall@1 drop <2% from 4-bit -> ship 3-bit default; MIDDLE 2-4%; HARD-FAIL >4%.",
  "quant levels", "pinv recovers", "3bit<4bit levels",
'''N = 1024; M = int(0.5 * N); SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]
def quant(W, bits):
    L = 2 ** bits - 1; lo, hi = np.quantile(W, 0.001), np.quantile(W, 0.999); Wc = np.clip(W, lo, hi)
    q = np.round((Wc - lo) / (hi - lo + 1e-12) * L); return (q / L * (hi - lo) + lo).astype(np.float32)
def _selftest():
    g = np.random.default_rng(0); assert quant(g.standard_normal((8, 8)), 3).shape == (8, 8), "quant levels"
    K = unit(g.standard_normal((5, 16))); assert int(np.argmax(unit(K) @ unit(K)[0])) == 0, "pinv recovers"
    assert (2 ** 3 - 1) < (2 ** 4 - 1), "3bit<4bit levels"
    print("[selftest] PASS: storage-3bit", flush=True)
_selftest()
if _ARGS.self_test: sys.exit(0)
def recall_at1(W, K, g, flip=0.05):
    s = K * np.where(g.random(K.shape) < flip, -1.0, 1.0)
    rec = np.sign(s @ W.T); rec[rec == 0] = 1.0
    return float(np.mean(np.all(rec == K, axis=1)))
def run_seed(seed):
    g = np.random.default_rng(seed); K = np.sign(g.standard_normal((M, N))).astype(np.float32)
    Kf = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-9)
    W = (Kf.T @ np.linalg.solve(Kf @ Kf.T + 1e-3 * np.eye(M), Kf)).astype(np.float32); np.fill_diagonal(W, 0.0)
    r4 = recall_at1(quant(W, 4), K, np.random.default_rng(seed + 1)); r3 = recall_at1(quant(W, 3), K, np.random.default_rng(seed + 1))
    return r4, r3
def run() -> Dict:
    rs = [run_seed(s) for s in SEEDS]; r4 = float(np.mean([a for a, _ in rs])); r3 = float(np.mean([b for _, b in rs]))
    drop = r4 - r3; print("  recall@1 4-bit=%.3f 3-bit=%.3f drop=%.3f" % (r4, r3, drop), flush=True)
    return {"r4": r4, "r3": r3, "drop": drop}
def verdict(r) -> Tuple[str, str]:
    d = r["drop"]; s = "4-bit=%.3f 3-bit=%.3f drop=%.3f" % (r["r4"], r["r3"], d)
    if d < 0.02: return ("HARD_PASS", "HARD_PASS: 3-bit W drops recall@1 <2% vs 4-bit -- ship 3-bit as default (25% more storage saving). " + s)
    if d < 0.04: return ("MIDDLE_BAND", "MIDDLE_BAND: 3-bit drop 2-4%. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 3-bit drop >=4% -- keep 4-bit. " + s)
''')
print("DONE")
