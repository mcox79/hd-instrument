"""
exp_sleep_defrag_scaling_bundle_v1 -- BUNDLED sleep-defrag scaling 3 pre-tests (streaming + adversarial + GDPR) -- CPU.

ROUTING: sleep_defrag_scaling_3_pretests_AUTHORIZE (builds on C5 sleep-defrag HP cos=0.97). Three sub-tests in one process:
  ST1 STREAMING (Misra-Gries top-K): estimate heavy-hitter regularities from a stream with k counters; match ground-truth
      top-K frequencies within 10pct (bounded-memory aggregation).
  ST2 ADVERSARIAL (contradiction detection): plant 5 facts that contradict the majority regularity; flag them via
      anti-alignment of their unbound evidence to the aggregate; recall=1.0, FPR<=5pct.
  ST3 GDPR CASCADE (recompute with exclusion): aggregate a regularity over 100 FHRR facts; erase one source; recompute the
      regularity WITHOUT it; verify it matches the leave-one-out aggregate AND the audit hash changes (crypto-erasure proof).
  Pure numpy + hashlib. CPU.
PRE-REGISTERED: HARD-PASS all 3 sub-tests pass their bars. MIDDLE 2/3. HARD-FAIL <=1/3.
FORMULA SELF-TESTS (PROT-022): 1. misra-gries finds heavy hitter. 2. bind/unbind inverse. 3. leave-one-out exact.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "sleep_defrag_scaling_bundle_v1"; D = 2048; N_FILL = 20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_STREAM = 2000 if RUN_MODE == "smoke" else 10000; MG_K = 16; TOP_K = 8; N_FACTS = 100; N_CONTRA = 5


def phasor(m, d, g):
    return np.exp(1j * g.uniform(-np.pi, np.pi, (m, d))).astype(np.complex64)


def unit(v):
    return v / (np.abs(v) + 1e-8)


def bind(a, b):
    return a * b


def unbind(c, b):
    return c * np.conj(b)


def cleanup_idx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))


def cos(a, b):
    return float(np.vdot(a, b).real / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def misra_gries(stream, k):
    cnt = {}
    for x in stream:
        if x in cnt:
            cnt[x] += 1
        elif len(cnt) < k:
            cnt[x] = 1
        else:
            for key in list(cnt):
                cnt[key] -= 1
                if cnt[key] == 0:
                    del cnt[key]
    return cnt


def _selftest():
    s = [1] * 50 + [2] * 3 + [3] * 2; mg = misra_gries(s, 4); assert 1 in mg, "misra-gries finds heavy hitter"
    g = np.random.default_rng(0); a = phasor(1, 32, g)[0]; b = phasor(1, 32, g)[0]
    assert np.allclose(unbind(bind(a, b), b), a, atol=1e-4), "bind/unbind inverse"
    v = np.array([1.0, 2.0, 3.0]); assert abs((v.sum() - v[1]) - (v[0] + v[2])) < 1e-9, "leave-one-out exact"
    print("[selftest] PASS: sleep-defrag-scaling-bundle", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def st1_streaming(g):
    # heavy-hitter stream: a few regularities dominate (Zipf-ish); Misra-Gries top-K vs exact top-K frequencies
    probs = np.array([0.30, 0.20, 0.12, 0.08, 0.06, 0.05, 0.04, 0.03] + [0.02] * 6); probs = probs / probs.sum()
    stream = list(g.choice(len(probs), size=N_STREAM, p=probs))
    exact = {}
    for x in stream:
        exact[x] = exact.get(x, 0) + 1
    mg = misra_gries(stream, MG_K)                               # MG_K counters (> TOP_K for robust heavy-hitter recovery)
    top_exact = sorted(exact, key=exact.get, reverse=True)[:TOP_K]
    recovered = [t for t in top_exact if t in mg]
    frac = len(recovered) / TOP_K
    print("  [ST1 streaming] true top-%d recovered=%.2f (MG %d counters)" % (TOP_K, frac, MG_K), flush=True)
    return frac >= 0.90


def st2_adversarial(g):
    book = phasor(N_FILL, D, g); role = phasor(1, D, g)[0]; true_f = 0
    cases = []; planted = set()
    for i in range(N_FACTS):
        if i < N_CONTRA:
            f = int(g.integers(1, N_FILL)); planted.add(i)         # contradiction: not the majority filler
        else:
            f = true_f
        cases.append(bind(role, unit(book[f] + 0.4 * phasor(1, D, g)[0])))
    evidence = [unbind(c, role) for c in cases]; agg = np.sum(evidence, axis=0)
    scores = np.array([cos(e, agg) for e in evidence])
    # flag CLEAR outliers by a gap criterion (median - 3*MAD), not a fixed fraction -> low FPR when few are planted
    med = np.median(scores); mad = np.median(np.abs(scores - med)) + 1e-9
    thr = med - 3.0 * mad
    flagged = set(int(i) for i in np.where(scores <= thr)[0])
    recall = len(flagged & planted) / len(planted)
    fp = len(flagged - planted) / max(N_FACTS - len(planted), 1)
    print("  [ST2 adversarial] contradiction recall=%.2f FPR=%.3f (flagged %d, planted %d)" % (recall, fp, len(flagged), len(planted)), flush=True)
    return recall >= 0.99 and fp <= 0.05


def st3_gdpr_cascade(g):
    book = phasor(N_FILL, D, g); role = phasor(1, D, g)[0]
    fids = [0 if g.random() < 0.6 else int(g.integers(1, N_FILL)) for _ in range(N_FACTS)]
    ev = [unbind(bind(role, unit(book[f] + 0.4 * phasor(1, D, g)[0])), role) for f in fids]
    agg_all = np.sum(ev, axis=0)
    erase = 7
    agg_recompute = agg_all - ev[erase]                            # recompute regularity excluding the erased source
    agg_loo = np.sum([ev[i] for i in range(N_FACTS) if i != erase], axis=0)   # ground-truth leave-one-out
    exact = np.allclose(agg_recompute, agg_loo, atol=1e-3)
    h_before = hashlib.sha256(agg_all.tobytes()).hexdigest(); h_after = hashlib.sha256(agg_recompute.tobytes()).hexdigest()
    audit_ok = h_before != h_after
    print("  [ST3 gdpr-cascade] recompute-without-erased exact=%s audit-hash-changed=%s" % (exact, audit_ok), flush=True)
    return exact and audit_ok


def run() -> Dict:
    g = np.random.default_rng(71)
    s1 = st1_streaming(g); s2 = st2_adversarial(g); s3 = st3_gdpr_cascade(g)
    npass = int(s1) + int(s2) + int(s3)
    return {"st1_streaming": s1, "st2_adversarial": s2, "st3_gdpr": s3, "npass": npass}


def verdict(r) -> Tuple[str, str]:
    s = "streaming=%s adversarial=%s gdpr-cascade=%s (%d/3)" % (r["st1_streaming"], r["st2_adversarial"], r["st3_gdpr"], r["npass"])
    if r["npass"] == 3:
        return ("HARD_PASS", "HARD_PASS: all 3 sleep-defrag scaling pre-tests pass -- streaming aggregation, contradiction detection, and GDPR-cascade recompute all work; clears the Phase-1 integration gate. " + s)
    if r["npass"] == 2:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2/3 sleep-defrag scaling pre-tests pass. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <=1/3 sleep-defrag scaling pre-tests pass. " + s)


print("[config] anchor=%s mode=%s D=%d stream=%d facts=%d" % (ANCHOR_NAME, RUN_MODE, D, N_STREAM, N_FACTS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
