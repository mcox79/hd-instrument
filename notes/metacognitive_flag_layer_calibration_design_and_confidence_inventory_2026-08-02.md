# Metacognitive FLAG layer: design + confidence-signal inventory (2026-08-02)

Prep for the north-star arc (the self-improving reader): the reader FLAGS what it doesn't know with
CALIBRATED error estimates -> tiered research -> learn. Per memory this arc's foundational prereq is
a CALIBRATED flag; noisy flags => the loop learns the wrong things. This note designs the flag layer
and inventories the confidence signals the pipeline ALREADY exposes (so we calibrate what exists
before inventing new machinery).

## What the reader should flag (by pipeline stage), and the signal it already has
1. COREF decision (match-or-allocate, exp_earn_coref_match_or_allocate_v1.py run_learnable):
   - NAME path: `best_overlap` (token Jaccard to the chosen entity). MARGIN = best_overlap - 2nd_best_overlap.
     Low margin / low absolute overlap = uncertain link.
   - PRONOUN path: chosen = argmax salience over gender-compatible entities. MARGIN = salience(top) -
     salience(2nd). Small gap with 2+ same-gender candidates = the KNOWN hard case (Harry/Sam) = should flag.
   - MATCH-vs-ALLOCATE-NEW: when best is None -> allocates a new entity. The "no compatible/overlapping
     antecedent" decision is itself a confidence event (could be a missed coref).
   - GROUND TRUTH available: the dense-eval error_diagnostic already labels each MERGE/SPLIT error ->
     we can directly measure whether margin predicts error (AUC).
2. ROLE extraction (the ~0.60 learned construction-conditional organ): construction-classifier posterior +
   the role-assignment confidence. Prior probe found self-detection best signal = the reader's own
   confidence AUC 0.76 (WHERE history) -- so an extraction-confidence signal ALREADY exists and is
   partially calibrated. Reuse it, don't reinvent.
3. WORD/lexical: dictionary MISS (animacy_lexicon / supplied lexicon returns unknown). Binary + graded
   surprise via the KnownBase.surprise() seam already in hdlab/state_of_mind.py (SetKnownBase /
   AdditiveMapKnownBase) -- the "recognize-KNOWN / surprise" seam is BUILT. This is the "look up the word"
   tier-1 research trigger (USER: "just give it a dictionary" + "flag when the dictionary doesn't have it").

## The calibration probe (FIRST concrete experiment of this arc -- CHEAP, dispatch after milestone commits)
Question: does the coref mechanism's OWN decision-margin predict its OWN errors? (metacognitive
confidence / uncertainty monitoring -- brain-faithful: the reader knows when it's guessing.)
- Instrument run_learnable to log, per mention decision: chosen margin (as above), is_pronoun,
  n_compatible_candidates, chose_new.
- Ground truth per decision = correct/incorrect coref (from the gold cluster vs predicted cluster;
  reuse diagnose_errors). 
- METRIC: AUC / calibration curve of margin -> P(error). CAN-FAIL: if margin has AUC ~0.5 (no better
  than chance at predicting its own errors), the confidence signal is UNCALIBRATED and the flag layer
  needs a different signal -- report honestly, do not spin. TARGET: AUC well above 0.5, and a threshold
  that flags the known-hard same-gender pronoun cases.
- FAIR: report AUC separately for name vs pronoun decisions (pronoun is where the hard cases live).
- Implement as a NEW standalone probe cell (instrument a local copy / wrapper of the decision loop; do
  NOT modify run_learnable in place -- step 2 also touches that path; keep one-variable clean).

## Why this is the hard blocking thing (not busywork)
The self-improving loop cannot start until the flag is calibrated (memory: "calibration is foundational;
noisy flags => learns the wrong things"). This probe answers whether the CHEAPEST possible flag signal
(the margin the mechanism already computes) is good enough, before we build anything heavier. If yes,
the flag layer's coref-tier is earned nearly for free. If no, we know to look elsewhere (e.g. an
ensemble/agreement signal) before scaling content.

## Sequencing
- Dispatch AFTER the milestone fair-metric commits (serialize git; avoid the commit race already hit once).
- Runs in parallel with step 2 ONLY if it does not modify run_learnable (standalone instrumented copy).
- After: if calibrated, wire flag -> tiered research (dictionary -> targeted lookup) + the "learn from
  flagged gaps" loop on RICHER/LONGER content (the convergent 5-probe finding: McGuffey too thin for the
  advanced competencies -> may need a denser public-domain corpus; decide with evidence).
[[project_autonomous_flag_driven_self_improving_read_loop_vision_2026-08-02]]
[[feedback_reader_must_flag_unknowns_with_error_estimates_and_do_tiered_research_2026-08-02]]
