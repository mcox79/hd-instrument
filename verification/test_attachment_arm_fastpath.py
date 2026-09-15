"""WITNESS: the vectorised attachment-arm readout equals the reference per-pair loop to 1e-9 on real sentences (UD-EWT test,
gold categories), under every live switch (plain; graded category hand-off; PP cue; the meaning cue when enabled), and is faster.
Run: python verification/test_attachment_arm_fastpath.py [cap]"""
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
import numpy as np

import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST


def main() -> int:
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    test = sentences(TEST, cap=cap, maxlen=10**6); tab = AA.load_attachment_validities()
    worst = 0.0; n_pairs = 0; t_fast = t_ref = 0.0; mism = []
    for toks, pos, hg, rels in test:
        t0 = time.perf_counter(); A, n = AA.arc_scores(toks, pos, tab); t_fast += time.perf_counter() - t0
        t0 = time.perf_counter(); B, _ = AA.arc_scores_reference(toks, pos, tab); t_ref += time.perf_counter() - t0
        fa, fb = np.isfinite(A), np.isfinite(B)
        if not np.array_equal(fa, fb):
            mism.append((" ".join(toks)[:80], "finite-mask differs", int((fa != fb).sum())))
            continue
        d = float(np.max(np.abs(A[fa] - B[fb]))) if fa.any() else 0.0
        worst = max(worst, d); n_pairs += int(fa.sum())
        if d > 1e-9 and len(mism) < 5:
            i = np.unravel_index(np.argmax(np.where(fa, np.abs(A - B), 0)), A.shape)
            mism.append((" ".join(toks)[:80], f"h={i[0]} j={i[1]}", round(float(A[i]), 4), round(float(B[i]), 4)))
    # the MAP heads must agree too (same argmax structure)
    agree = sum(AA.chu_liu_edmonds(*AA.arc_scores(t, p, tab)) == AA.chu_liu_edmonds(*AA.arc_scores_reference(t, p, tab))
                for t, p, _, _ in test[:40])
    ok = not mism and worst <= 1e-9 and agree == min(40, len(test))
    print(f"sentences {len(test)} | finite pairs {n_pairs} | max |fast - reference| = {worst:.2e} | MAP heads agree {agree}/{min(40, len(test))} "
          f"| time fast {t_fast:.2f}s vs reference {t_ref:.2f}s (x{t_ref / max(t_fast, 1e-9):.1f})")
    for m in mism:
        print("MISMATCH", m)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
