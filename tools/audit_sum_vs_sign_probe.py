"""AUDIT probe (read-only): is 'sign destroys 0.000 bits' criterion-specific?

Recomputes, off the LANDED artifacts of exp_encoding_quality_instrument_v2:
  (1) the M4 S1/S2 pair (graded codes vs sign(codes)) at EVERY sigma in the cell's own
      SIGMAS list, not only SIGMA_GATE=1.0 which the cell's own FIX (b) declares saturated;
  (2) the same pair under the TOP-1 criterion (recoverability) as well as TOP-8;
  (3) near-neighbour discriminability (target vs 31 orthographic / frequency-matched
      distractors) for graded vs signed -- the instrument's own closest analogue to the
      2AFC near-neighbour scorer that ORGAN_MAP's +0.0602 lives on;
  (4) the S3/S4 pair (bundle-then-sign) for the arms where the sum leaves bits standing.

Nothing under hdlab/, experiments/, data/ is modified. Output to stdout + scratch json.
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
NPZ = os.path.join(OUT, "concept_profiles_d256_V4096_B64000000.npz")

z = np.load(NPZ, allow_pickle=True)
prof = z["profiles"].astype(np.float32)
print("profiles", prof.shape, "collision-free", int((~z["collide"]).sum()))

words, counts = C.build_vocab(C.CORPUS, C.CORPUS_BYTES, C.V)
ortho = C.build_ortho_neighbours(words, C.K_DISTRACT)
freq = C.build_freq_controls(counts, ortho, C.K_DISTRACT)
print("vocab rebuilt:", words[:8], "...")

NG = C.N_GATE
B = C.BUNDLE_B
SEEDS = C.SEEDS
SIGMAS = C.SIGMAS

res = {"note": "audit recompute, read-only", "N_GATE": NG, "B": B, "SEEDS": SEEDS,
       "SIGMAS": SIGMAS}


def arm_codes(arm, d, seed):
    if arm == "P_LIVE_CONCEPT":
        return C._l2n(prof)
    return C.build_codes(arm, d, seed, words, [], OUT)[0]


def sweep(arm, d):
    signed_note = {}
    for sig in SIGMAS:
        rows = {"top8_graded": [], "top8_signed": [],
                "top1_graded": [], "top1_signed": [],
                "disc_ortho_graded": [], "disc_ortho_signed": [],
                "disc_freq_graded": [], "disc_freq_signed": []}
        for seed in SEEDS:
            codes = arm_codes(arm, d, seed)
            sgn = C._l2n(np.sign(codes).astype(np.float32))
            rows["top8_graded"].append(C.recoverability_topb(codes, NG, sig, seed, B))
            rows["top8_signed"].append(C.recoverability_topb(sgn, NG, sig, seed, B))
            rows["top1_graded"].append(C.recoverability(codes, NG, sig, seed))
            rows["top1_signed"].append(C.recoverability(sgn, NG, sig, seed))
            rows["disc_ortho_graded"].append(C.discriminability(codes, ortho, sig, seed))
            rows["disc_ortho_signed"].append(C.discriminability(sgn, ortho, sig, seed))
            rows["disc_freq_graded"].append(C.discriminability(codes, freq, sig, seed))
            rows["disc_freq_signed"].append(C.discriminability(sgn, freq, sig, seed))
            if arm == "P_LIVE_CONCEPT":
                break  # profiles are seed-independent (built once, no seed)
        signed_note[f"{sig:g}"] = {k: float(np.mean(v)) for k, v in rows.items()}
        g8 = signed_note[f"{sig:g}"]["top8_graded"]
        s8 = signed_note[f"{sig:g}"]["top8_signed"]
        signed_note[f"{sig:g}"]["bits_top8_graded"] = C.fano_bits_list(g8, NG, B)
        signed_note[f"{sig:g}"]["bits_top8_signed"] = C.fano_bits_list(s8, NG, B)
        signed_note[f"{sig:g}"]["bits_destroyed_by_sign_top8"] = (
            C.fano_bits_list(g8, NG, B) - C.fano_bits_list(s8, NG, B))
    return signed_note


for arm, d in [("P_LIVE_CONCEPT", 256), ("A_RANDOM_IID", 256), ("P_LIVE_WORD", 256)]:
    print("\n===", arm, "d=", d)
    r = sweep(arm, d)
    res[f"{arm}_d{d}"] = r
    for sig, v in r.items():
        print(f" sigma={sig:>3}  top8 G {v['top8_graded']:.4f} / S {v['top8_signed']:.4f}"
              f" | bits destroyed by sign {v['bits_destroyed_by_sign_top8']:+.3f}"
              f" | top1 G {v['top1_graded']:.4f} / S {v['top1_signed']:.4f}"
              f" | discORTHO G {v['disc_ortho_graded']:.4f} / S {v['disc_ortho_signed']:.4f}"
              f" | discFREQ G {v['disc_freq_graded']:.4f} / S {v['disc_freq_signed']:.4f}")

# ---- S3 vs S4: the POST-SUM sign site (this is where ORGAN_MAP places the defect)
print("\n=== S3 (bundle) vs S4 (bundle then sign), d=256")
post = {}
for arm in ["A_RANDOM_IID", "P_LIVE_WORD", "A_PLANTED_SEMANTIC", "A_ORTHOGRAPHIC",
            "P_LIVE_CONCEPT"]:
    s3s, s4s = [], []
    for seed in SEEDS:
        if arm == "A_PLANTED_SEMANTIC":
            continue
        codes = arm_codes(arm, 256, seed)
        s3s.append(C.bundle_survival(codes, NG, B, False, seed))
        s4s.append(C.bundle_survival(codes, NG, B, True, seed))
        if arm == "P_LIVE_CONCEPT":
            break
    if not s3s:
        continue
    a3, a4 = float(np.mean(s3s)), float(np.mean(s4s))
    b3, b4 = C.fano_bits_list(a3, NG, B), C.fano_bits_list(a4, NG, B)
    post[arm] = {"S3_acc": a3, "S4_acc": a4, "S3_bits": b3, "S4_bits": b4,
                 "bits_destroyed_by_post_sum_sign": b3 - b4}
    print(f" {arm:20s} S3 {a3:.4f} ({b3:.3f} bits) -> S4 {a4:.4f} ({b4:.3f} bits)"
          f"  sign cost {b3 - b4:+.3f} bits")
res["post_sum_sign_S3_to_S4_d256"] = post

with open(os.path.join(REPO, "scratch", "audit_sum_vs_sign_probe.json"), "w") as f:
    json.dump(res, f, indent=1)
print("\nwrote scratch/audit_sum_vs_sign_probe.json")
