---
owner_verdict: DONE
---

SOLVED (REFUTED — the brief's sanctioned located negative = FULL PASS): construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set (opus 4.8 solver)

Write-up: notes/problems/construction_aware_selector_for_multi_do_who_did_what_over_the_referent_set/
  {SOLVED.md, OWNER_NOTES.md, brain_comparison_and_signal_loss_2026-09-03.md, research_construction_vs_competition_brain_foundational_2026-09-03.md}
Reverify (re-runs no landed cell): .venv/Scripts/python.exe verification/test_construction_aware_selector.py   # 11/11

RESULT: a Goldberg construction-aware selector adds EXACTLY 0.000 to who-did-what over the LIVE feature-competition
theme selector (hdlab.graded_role_assigner.hybrid_role_patient), proven three ways: selector-level over the
referent-per-NP set (19c n=669: -0.0030 n.s.; multi-DO n=162: -0.0123 n.s.), END-TO-END through the real
SituationReader().read() (n=1354: +0.0000 CI[0,0]), and register-invariant (modern QA-SRL n=1261: -0.0008 n.s.).
The construction cue is REDUNDANT with word-order on canonical English; the brain binds roles by feature-competition
(eADM / Frankland-Greene / Competition Model), NOT construction-template retrieval — so the deployed selector already
IS the brain's mechanism and is statistically TIED with a competent reader (0.928 vs spaCy 0.922).

DISK-OUTRANKS-THE-BRIEF corrections (verified): the prototype's "+0.146 / 84%-multi-DO" premise was an artifact of the
experimental ideal_pick baseline's ANIMACY-OVERRIDE bug; over the deployed selector it is 0.000. ideal_pick is itself
NET-NEGATIVE vs the deployed hybrid_role_patient (0.898 vs 0.928). => AUDIT UPDATE (SOLVED.md): STRIKE the parent
open_a_discourse_referent...'s NEXT-STEP #1 ("land construction-aware selector 0.873->0.913"); do NOT adopt ideal_pick.

IDEAL COMPOSITION, prototyped + PROVEN (exp_construction_whole_composition_v1): the selector is held fixed (at ceiling);
the one buildable, brain-foundational upstream win is INDEFINITE-PRONOUN source coverage (DRT introduction) —
0.9283 -> 0.9387, +0.0105 CI[+0.0015,+0.0209] CI-sep, info-free twin loses, no single-DO regression, robust (risky
quantifiers add +0.0000). 19c-specific. A structural Right-hand-Head-Rule fix is a DOCUMENTED NULL (fixes 2 adjective
mis-tags, breaks 2 verb mis-tags — both register POS-tagger noise), PROVING the parse-recoverable lever is the
register-native POS tagger, not a selector patch. Composition ceiling 0.969; genuine irreducible residual ~3.1%
(ill-posed naming/object-complement + gold noise — the competent reader also misses it).

WHERE SIGNAL IS LOST (waterfall, ours vs brain): deployed reader's dominant loss is the SOURCE (coref covers the gold
patient only 0.818; referent-per-NP -> 0.971, gated on the coref linker). On the ideal chain the loss is S3-parse
(56% of residual = filed parser + register-native POS) + the ~3% gated/ill-posed tail. The SELECTOR is never the
bottleneck.

LAND (strategy, Q111): nothing on the selector. (1) Extend referent-per-NP source to indefinite-pronoun heads
(+0.0105, promote from exp_construction_ideal_composition_v1.INDEF_PRON) — land with the source wire. (2) Fold the
AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md §2b (selector = at ceiling, feature-competition PINNED; two parent
corrections). NEXT PROBLEMS (not this one, ranked): referent-per-NP SOURCE wire (gated on coref linker) > register-native
POS > filler-gap clefts > meaning-fit for the gated tail.

files: experiments/exp_construction_{aware_selector_diagnosis,aware_selector_residual,aware_selector_brain_comparison,
aware_selector_generalization,aware_selector_live_reader,ideal_composition,whole_composition,brain_waterfall}_v1.py +
verification/test_construction_aware_selector.py (11/11). NO hdlab written. Ledger: malformed/incomplete 0.
owner_verdict is set in OWNER_NOTES.md (this prompt = the DONE signal).
