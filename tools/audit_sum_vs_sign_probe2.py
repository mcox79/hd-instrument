"""AUDIT probe 2 (read-only): scope the 6.93-of-7 bundling loss.

  (a) bundle size B sweep -- is the sum a CLIFF or a gradual cost?
  (b) collision-free store -- is the loss an artifact of the 33% lemma collisions
      (the same defect that ate 78% of the GOLD_ORTHO lift)?
  (c) sign-after-sum cost at each B (the site ORGAN_MAP names).
Nothing is modified.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))
import exp_encoding_quality_instrument_v2 as C  # noqa: E402

OUT = os.path.join(REPO, "data", "exp_encoding_quality_instrument_v2")
z = np.load(os.path.join(OUT, "concept_profiles_d256_V4096_B64000000.npz"), allow_pickle=True)
prof = C._l2n(z["profiles"].astype(np.float32))
cf = ~z["collide"]
words, counts = C.build_vocab(C.CORPUS, C.CORPUS_BYTES, C.V)

NG = C.N_GATE
res = {}
print("collision rate in the first %d store rows: %.3f"
      % (NG, 1.0 - cf[:NG].mean()))

arms = {
    "P_LIVE_CONCEPT": prof,
    "P_LIVE_CONCEPT_COLLISION_FREE": prof[cf][:NG],
    "P_LIVE_WORD": C.build_codes("P_LIVE_WORD", 256, 7, words, [], OUT)[0],
    "A_RANDOM_IID": C.build_codes("A_RANDOM_IID", 256, 7, words, [], OUT)[0],
    "A_PLANTED_STRUCTURE": C.build_codes("A_PLANTED_STRUCTURE", 256, 7, words, [], OUT)[0],
}
print("collision-free store rows available:", int(cf.sum()))

for name, codes in arms.items():
    n = min(NG, len(codes))
    row = {}
    print("\n---", name, "store n =", n)
    for b in [2, 4, 8, 16, 32]:
        a3 = C.bundle_survival(codes, n, b, False, 7)
        a4 = C.bundle_survival(codes, n, b, True, 7)
        ceil_bits = np.log2(n / b)
        b3 = C.fano_bits_list(a3, n, b)
        b4 = C.fano_bits_list(a4, n, b)
        row[str(b)] = {"S3_acc": a3, "S4_acc": a4, "S3_bits": b3, "S4_bits": b4,
                       "ceiling_bits": float(ceil_bits),
                       "frac_of_ceiling_retained_after_sum": b3 / ceil_bits,
                       "sign_after_sum_cost_bits": b3 - b4}
        print(f"  B={b:2d} ceil {ceil_bits:.2f}b | sum-> acc {a3:.4f} = {b3:.3f}b "
              f"({100*b3/ceil_bits:5.1f}% of ceiling) | +sign-> {a4:.4f} = {b4:.3f}b "
              f"(sign costs {b3-b4:+.3f}b)")
    res[name] = row

with open(os.path.join(REPO, "scratch", "audit_sum_vs_sign_probe2.json"), "w") as f:
    json.dump(res, f, indent=1)
print("\nwrote scratch/audit_sum_vs_sign_probe2.json")
