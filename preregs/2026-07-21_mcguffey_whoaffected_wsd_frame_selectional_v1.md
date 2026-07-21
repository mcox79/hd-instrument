# Pre-reg: WSD frame+selectional disambiguator for the verb-affectedness gate

anchor: `mcguffey_whoaffected_wsd_frame_selectional_v1`
cell: `experiments/exp_mcguffey_whoaffected_wsd_frame_selectional_v1.py`
date: 2026-07-21
author: exp_dev (hdi)
route: LOCAL foreground (deterministic, N=38 held-out + UD subset; seconds). NO queue, NO push, NO remote-persist, NO store mutation.

## Question
The lemma-level verb-affectedness gate (v2, atom 29414/29415) collapses each verb to its MODAL VerbNet
sense, so it mis-grades polysemy. Held-out eval (VET a38fa920): 2/5 sense cases pass, 3/5 failures
RESCUABLE-BY-PER-SENSE. Does matching the reader's PARSE-FRAME to the VerbNet sense whose syntactic
frame matches (+ an object-animacy selectional refinement) pick the RIGHT sense -- WITHOUT breaking the
non-polysemous sentences the lemma gate already gets right (a Pareto move)?

## Design (glass-box; extends v2, does NOT fork the pipeline)
Three deciders, one variable each = the sense-selection step, negation + hand copula/stative/phrasal
overrides identical across all three:
- BASELINE = v2 COMBINED lemma-modal gate (`combined_forces_none`), reproduced in-cell = positive control.
- FRAME = frame-matcher: coarse parse-frame signature {INTRANS/TRANS/NP_PP/PP/DATIVE} matched to each
  VerbNet sense's frame-signature set (from nltk `vn.frames`); select frame-compatible senses; if they
  AGREE on force-none -> use it; else ABSTAIN to modal (Pareto-safe overlay: only changes a decision
  when frame-compatible senses agree AND that agreement differs from the modal).
- FRAME_SEL = FRAME + object-animacy selectional tie-break: when frame-compatible senses DISAGREE and the
  parsed direct object is ANIMATE (pronoun closed-class OR local WordNet person/animal hypernym), prefer
  senses whose VerbNet class carries a +animate selrestr on a non-subject role; if that subset has a
  unique decision -> use it; else abstain. Fires ONLY on animate objects (the safe, informative case:
  animate objects of contact/social/perception verbs are targets-not-affected, per the McGuffey
  annotation guidance). Selectional naturally pulls in ENTITY/NOUN SEMANTICS (the next meaning-module
  gap after word-sense) -- included here MINIMALLY (animacy only) via LOCAL nltk WordNet; deeper noun
  semantics DEFERRED and flagged.

Brain-faithful: frame + selectional MUTUAL constraint settling to the coherent sense (Paczynski-Kuperberg
2012; N400 pre-activation). Runtime = parser-frame + nltk VerbNet/WordNet lookups ONLY. NO external LLM.

## Measurements
1. WORD-SENSE rescue: on the 5 cases {h08 leave-deposit(HARD), h14 hunt-pursuit, h15 lose, h17/h20
   meet-encounter(clean-rescue target)}, per-case decision vs gold for BASELINE/FRAME/FRAME_SEL + which
   sense was chosen + rescue classification.
2. NO-REGRESSION: on the 33 non-sense held-out sentences, per-sentence delta FRAME_SEL vs BASELINE
   (broken = baseline-correct & mechanism-wrong). PLUS UD-EWT who-affected (structural gold -> gate can
   only cost) delta >= -0.05.

## Bands (HARD-PASS / HARD-FAIL declared BEFORE full)
Let rescued_frame = frame_sense_correct - baseline_sense_correct (of 5); rescued_sel likewise for
FRAME_SEL; broken_sel = non-sense sentences baseline-correct but FRAME_SEL-wrong; ud_delta = FRAME_SEL
UD acc - baseline UD acc.

PRIMARY (the literal task question -- does FRAME-matching pick the right sense?):
- HARD-PASS-FRAME: rescued_frame >= +1 AND broken_frame == 0 AND ud_delta_frame >= -0.05.
- HARD-FAIL-FRAME: rescued_frame <= 0 (frame alone rescues nothing -> the ambiguity is not syntactic).

OVERALL DELIVERABLE (best mechanism = FRAME_SEL):
- HARD-PASS-WSD: rescued_sel >= +2 AND broken_sel == 0 AND ud_delta >= -0.05 (genuine Pareto rescue of
  >= 2 of the 3 rescuable cases, zero collateral).
- MIDDLE_BAND-WSD: rescued_sel == +1 with no regression; OR rescued_sel >= +2 with exactly 1 collateral
  (broken_sel == 1) and ud_delta >= -0.05.
- HARD-FAIL-WSD: rescued_sel <= 0 OR broken_sel >= 2 OR ud_delta < -0.05.

## CAN-FAIL bounds (per drill; a can't-fail cell is worse than idle)
- Frame granularity is coarse; some senses share a frame -> frame CANNOT separate them (predicted: met is
  transitive under BOTH meet senses; leave-deposit shares NP-PP with keep-possession). Frame-alone
  rescuing 0 is a REAL, expected outcome (HARD-FAIL-FRAME), not a bug.
- Parser attach errors propagate (predicted: h08 "on the box" misattaches to the noun -> verb reads TRANS).
- h08 leave-deposit is NOT resolvable by frame OR object-animacy (inanimate object; deposit-vs-keep needs
  aspect/world-knowledge) -> predicted to stay failed under all arms = the acknowledged hard bound.
- FRAME_SEL can REGRESS if the animacy tie-break fires wrongly on a non-sense sentence -> measured; a
  regression triggers HARD-FAIL-WSD.

## HYPOTHESIZED (pre-run, tagged; NOT measured)
- rescued_frame = 0 HYPOTHESIZED (frame-compatible senses disagree or abstain on all 5; met transitive
  under both senses; leave-deposit misattached). -> FRAME alone predicted HARD-FAIL.
- rescued_sel = +2 HYPOTHESIZED (met h17+h20 rescued via object animacy = the encounter sense; h08
  unresolved). -> predicted HARD-PASS-WSD IFF no non-sense regression. Honest can-fail if it regresses.
- baseline_sense_correct = 2/5 CITED@atom 29415 (VET a38fa920).

## Schema-vet
- arms_differ_verified: baseline/frame/frame_sel decision vectors (smoke asserts not all identical).
- final_metrics_atomicity: tmp_replace.
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: accuracy on labeled gold, no quantitative noise floor.
- baseline_in_band: baseline held-out acc in (0.05, 0.95); baseline_sense=2/5=0.4 in band.
- discriminator survives scale: full IS the scale (N=38 fixed held-out).
- calibration_check: default_ok_for_this_regime (0.35 graded threshold = v2 builder spot-check 94.4%).
- cardinality_ok: n/a (no sweep axis; single deterministic pass).
- deterministic_seeding: fixed seed in the leak-clean permutation probe; no hash()-seeded RNG.
- leak_clean: gate = verb-lemma + parse-frame + argument-animacy, gold-independent; self-test permutes
  gold type/affected labels and asserts gate decisions byte-identical.
- selftest NON-tautological (v1 gate flag): the WSD probe DEGRADES the cue (obj_anim True->False) and
  asserts FRAME_SEL reverts from the encounter decision to the modal -> the mechanism RESPONDS to the
  animacy signal (must-fail control), not a constant.
- progress_logging: n/a (wall seconds; single-pass; not >= 1800s).

## Credit
VerbNet (Kipper-Schuler 2005); WordNet (Fellbaum 1998); Levin 1993; Dowty 1991; Beavers 2011;
Paczynski-Kuperberg 2012 (frame+selectional mutual constraint); v1 hand-lexicon + v2 held-out gate.
