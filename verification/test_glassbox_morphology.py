#!/usr/bin/env python3
"""Scaffold-free witness for the glass-box morphology organ.

Asserts, without touching any landed metrics.json (runs the cells in smoke = own bounded universes):
  A  RULE SNAPSHOT   the organ's hardcoded detachment rules still equal the vendored nltk snapshot in the asset.
  B  BYTE-IDENTITY   glass-box morphy == wn.morphy over the exhaustive-lemma / exception / inflection / real-prose
                     universes (smoke), 0 divergences, AND the full hdlab lemma path (lemma_word/lemma_verb/
                     is_known_word/concept_lemma/gek) is 0-divergence when the organ is swapped in -> the proposed
                     diff changes NO output (the brief's BAR).
  C  EXCEED          the brain-faithful dual-route organ beats morphy on modern gold lemma CI-separated, and the
                     info-free (wrong-pos) twin LOSES -> the lift is the obligatory-decomposition mechanism.

Run: .venv/Scripts/python.exe verification/test_glassbox_morphology.py
"""
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
# BYTE-IDENTITY is a property of the MORPHY ARM (the exact port of the dictionary tool). Since 2026-09-13 the live default arm is
# DUAL-ROUTE (words-and-rules; exceed cell 0.9826 vs 0.9594; board-neutral on every dimension), which diverges from the tool on
# ~0.6% of full-path lemmas BY DESIGN -- so this witness pins the arm it is about. HDLAB_MORPH_MODE=dualroute on the command line
# still runs the dual-route arm (and the byte-identity asserts are then expected to fail).
os.environ.setdefault("HDLAB_MORPH_MODE", "morphy")

from experiments.glassbox_morphology import default_morphology
import experiments.exp_glassbox_morphy_byte_identity_v1 as BI
import experiments.exp_dualroute_morphology_exceed_v1 as EX
import experiments.exp_glassbox_pos_bf_and_morphology_stack_v1 as ST


def main():
    m = default_morphology()

    # A -- rule snapshot
    assert m.self_test_rules(), "hardcoded morphy rules diverged from the vendored nltk snapshot"

    # B -- byte identity (smoke universes; the full 6.3M-comparison run is the landed metric)
    bi = BI.run(smoke=True)["result"]
    assert bi["raw_morphy"]["total_divergences"] == 0, ("raw morphy not byte-identical", bi["raw_morphy"])
    assert bi["full_lemma_path"]["total_divergences"] == 0, ("full lemma path not byte-identical",
                                                             bi["full_lemma_path"])
    assert bi["BYTE_IDENTICAL"], "BYTE_IDENTICAL flag false"

    # C -- exceed on modern gold, twin loses
    ex = EX.run(smoke=True)["result"]
    dm = ex["DUAL_minus_MORPHY"]; dt = ex["DUAL_minus_TWIN"]
    assert dm["sep"] and dm["delta"] > 0, ("dual-route must beat morphy CI-sep on gold lemma", dm)
    assert dt["sep"] and dt["delta"] > 0, ("info-free wrong-pos twin must LOSE", dt)

    # D -- the REQUIRED upstream upgrade: a BF (count-based, generative, graded) POS lifts the morphology, twin loses
    st = ST.run(smoke=True)["result"]
    q2 = st["Q2_morphology_stack_lemma_acc"]
    assert q2["DUAL_POS_bayes"] > q2["DUAL_GEN"], ("BF POS upstream must lift morphology over the no-POS floor", q2)
    assert st["twin_loses"], ("shuffled-POS twin must lose", q2)
    assert q2["DUAL_POS_gold"] > q2["DUAL_GEN"], ("perfect POS is the ceiling above no-POS", q2)

    print("WITNESS PASS")
    print("  A rules-snapshot: OK (hardcoded detachment rules == vendored nltk)")
    print("  B byte-identity (smoke): raw=%d div, full-path=%d div => BYTE_IDENTICAL=%s"
          % (bi["raw_morphy"]["total_divergences"], bi["full_lemma_path"]["total_divergences"], bi["BYTE_IDENTICAL"]))
    print("  C exceed: MORPHY=%.4f DUALROUTE=%.4f TWIN=%.4f | dual-morphy=%+.4f sep=%s | dual-twin=%+.4f sep=%s"
          % (ex["MORPHY_acc"], ex["DUALROUTE_acc"], ex["TWIN_acc"], dm["delta"], dm["sep"], dt["delta"], dt["sep"]))
    print("  D REQUIRED upstream POS upgrade: BF-POS lifts morphology DUAL_GEN=%.4f -> BF_POS=%.4f (gold ceiling %.4f, "
          "twin %.4f loses=%s)" % (q2["DUAL_GEN"], q2["DUAL_POS_bayes"], q2["DUAL_POS_gold"], q2["DUAL_POS_twin"],
                                   st["twin_loses"]))
    print("  => external tool removed byte-identically (the BAR); brain-faithful organ EXCEEDS it (the optimum); the "
          "morphology gain REQUIRED a BF POS upstream.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
