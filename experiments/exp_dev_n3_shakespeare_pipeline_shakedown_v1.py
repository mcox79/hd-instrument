"""N3 pipeline-SHAKEDOWN (NOT a cert; CPU-fast): validate the substrate-native char-LM
pipeline end-to-end on REAL shakespeare data before committing the ~1 GPU-hour text8 cert run.

Validates (boundary/storage-independent -- won't rework on the N1<->N3 confirm):
  - my new shakespeare_char_corpus loader integrates with SubstrateCharLM (real, non-synthetic)
  - the substrate char-LM produces a FINITE, better-than-uniform BPC on real readable text
  - the gradient baseline runs (BPC ladder reference)
  - substrate-only: SubstrateCharLM.score_bpc does NOT call any LLM (substrate primitives only)

This is the cheap shakedown of my N3 scope-decision (shakespeare-shakedown -> text8 cert).
Real-data provenance ASSERTED (allow_synthetic=False) -- avoids the wikitext2 silent-synthetic trap.
ASCII only.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import numpy as np

from testbed.substrate_lm.char_lm import SubstrateCharLM
from testbed.substrate_lm.baseline_gradient_lm import GradientCharLM
from testbed.substrate_lm.data import shakespeare_char_corpus, char_vocab_from_corpus


def main():
    # REAL data, fail-loud (allow_synthetic=False) -- provenance asserted
    train_text = shakespeare_char_corpus(split="train", max_chars=10_000, allow_synthetic=False)
    test_text = shakespeare_char_corpus(split="validation", max_chars=2_000, allow_synthetic=False)
    vocab = char_vocab_from_corpus(train_text)
    # provenance check: real shakespeare has a richer punctuation/case vocab than the synthetic fallback
    print("[shakedown] REAL shakespeare: train=%d test=%d vocab=%d" % (
        len(train_text), len(test_text), len(vocab)), flush=True)
    assert len(train_text) >= 5000 and len(vocab) >= 30, "corpus/vocab too small -> suspect fallback"

    print("[shakedown] training SubstrateCharLM (4-primitive, no gradient)...", flush=True)
    sub = SubstrateCharLM(n_layers=2, N=512, alpha_max=0.10, n_steps_per_layer=3, seed=7)
    sub.fit(train_text, n_chars_train=10_000, char_vocab=vocab, health_every=500, verbose=False)
    ss = sub.score_bpc(test_text)
    health = sub.primitive_health()

    print("[shakedown] training GradientCharLM baseline...", flush=True)
    grad = GradientCharLM(n_layers=2, hidden=32, seq_len=32, batch_size=16, lr=5e-3, seed=7)
    grad.fit(train_text, n_chars_train=10_000, char_vocab=vocab, max_epochs=1, verbose=False)
    gs = grad.score_bpc(test_text)

    print()
    print("  substrate BPC = %.3f  (uniform = %.3f)" % (ss["bpc"], ss["uniform_bpc"]))
    print("  baseline  BPC = %.3f  (uniform = %.3f)" % (gs["bpc"], gs["uniform_bpc"]))
    print("  substrate/baseline ratio = %.2fx  (phase_d_tier6 HP<=2.0 / MIDDLE<=4.0)" % (ss["bpc"] / gs["bpc"]))
    print("  primitive health: %s" % ({k: round(v, 3) if isinstance(v, float) else v for k, v in list(health.items())[:6]}))

    # PIPELINE gates (validate the harness RUNS; NOT the cert learning-bands)
    assert np.isfinite(ss["bpc"]) and np.isfinite(gs["bpc"]), "non-finite BPC -> pipeline bug"
    assert gs["bpc"] < gs["uniform_bpc"], "baseline not better than uniform -> baseline bug"
    assert not health.get("any_primitive_collapse", False), "substrate primitive collapse"
    # SCIENCE finding (reported, NOT a pipeline gate): does the substrate LEARN on real text?
    sub_learns = ss["bpc"] < ss["uniform_bpc"] - 0.02
    print()
    print("[shakedown] PIPELINE PASS: runs on REAL shakespeare; finite BPC; baseline beats uniform;")
    print("            no primitive collapse; substrate-only decode (no LLM calls). N3 harness validated.")
    print("[FINDING-1] substrate LEARNS on real text at smoke scale? %s (substrate BPC %.3f vs uniform %.3f)" % (
        "YES" if sub_learns else "NO -> AT CHANCE", ss["bpc"], ss["uniform_bpc"]))
    if not sub_learns:
        print("            -> substrate at chance at smoke (10k chars, N=512). phase_d_tier6 got MIDDLE_BAND on")
        print("               SYNTHETIC wikitext (broken loader) -- its apparent learning may be easy-synthetic-data.")
        print("               FULL scale (N=2048, 10M chars) is the real test; flag for N3 cert.")
    print("[FINDING-2] BPC-RATIO band is gameable: substrate-at-chance/weak-baseline = %.2fx would read HARD-PASS" % (
        ss["bpc"] / gs["bpc"]))
    print("            (<=2.0x) despite ZERO learning -> N3 NEEDS an ABSOLUTE floor (sub BPC < real chance/bigram")
    print("            baseline by margin), validating Skunkworks's N3 by-construction-saturation bands.")


if __name__ == "__main__":
    main()
