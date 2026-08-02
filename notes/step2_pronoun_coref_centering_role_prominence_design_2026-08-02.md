# Step 2 design: PRONOUN COREF via Centering / grammatical-role prominence (2026-08-02)

## Diagnosis (from dense-eval error_diagnostic, pre-step-1)
Pronoun-only B3-F1 = 0.534 (vs name 0.891). Two distinct error sources in the sample errs:
1. **Possessive-gender confound (step 1 fixes this):** "his mother"/"His mother" wrongly gender-ambiguous (None) -> merges with masc "Harry"/"he". ~12/20 sample errs involve a possessive NP. Step 1 (head-noun gender) makes "his mother" -> fem -> blocks these merges. Expect pronoun-only F1 to rise on its own after step 1.
2. **Pure same-gender antecedent-selection failures (step 2's target, RESIDUAL after step 1):**
   - `SPLIT | 'Sam' <-> 'he'`: "he" assigned to a different cluster than Sam (went to Harry, higher salience).
   - `MERGE | 'Harry' <-> 'he'`: "he" resolved to the WRONG masculine entity.
   When 2+ same-gender entities co-occur, gender/number compat can't disambiguate, and the current salience (frequency-count + recency tie-break) picks the wrong one.

## Current pronoun path (run_learnable, exp_earn_coref_match_or_allocate_v1.py L206-219)
For a pronoun: filter entities by gn_compatible; pick max `salience(pos)` where
salience = count + OVERLAY_BETA*exp(-OVERLAY_TIEBREAK_LAMBDA*(now-last_pos)) (frequency-dominant).
NO grammatical-role / subjecthood signal. That is the gap.

## The brain-faithful lever (step 2)
**Centering Theory (Grosz/Joshi/Weinstein; Gordon-Grosz-Gilliom):** a pronoun preferentially refers
to the backward-looking center Cb = the most grammatically PROMINENT entity of the prior utterance,
with prominence subject > object > other (agent-role ~ subject). Topic/subject continuity beats raw
frequency. Also grammatical-role PARALLELISM: a subject pronoun prefers the previous subject.
This is exactly the Centering machinery the coref cell claims to reuse from hdlab.state_of_mind but
the salience function currently ignores role.

## Concrete change (glass-box, our own; NO bolt-on)
1. Carry per-mention grammatical ROLE into the mention stream (build_mention_stream currently DROPS
   the gold 'role' field; add it). Roles: agent/experiencer/theme/patient/recipient/possessor/addressee/goal.
   (For the coref-isolation cell, role comes from gold; end-to-end it comes from the extraction organ.)
2. Add a role-prominence term to antecedent salience for PRONOUN resolution: prefer antecedents that
   most recently held a SUBJECT/AGENT role (Cb = topic), i.e. salience += ROLE_PROMINENCE_WEIGHT *
   prominence(entity.last_role) with prominence(agent) > prominence(others). Optionally add role
   PARALLELISM (subject-pronoun prefers previous agent). Keep weights as a small explicit set (glass-box).
3. CAN-FAIL: on same-gender multi-entity passages, Centering-salience must beat the frequency-only
   salience on pronoun-only B3-F1; on single-antecedent passages it must not regress. Fair baseline =
   current frequency+recency salience (already in the cell).

## Sequencing
Dispatch AFTER step 1 lands + I read its residual pronoun-only F1 and the residual pronoun errors
(so step 2 targets the TRUE same-gender cases, not the gender confound). Measure step 2's lift on
pronoun-only F1 AND on the end-to-end situation-model metric (the milestone cell), not just B3.

## Note
This shares the "carry role into the stream" change with the milestone wiring cell (both need per-mention
role). Do them coherently: the milestone cell already needs role for add_event(); step 2 uses the same
role for Centering. One stream-enrichment serves both.
