# exp_dev hand-off — research: brain-fidelity goal-outcome architecture (top-down reframe)

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_brain_fidelity_goal_outcome_architecture_2026-08-09.md` — Director-
requested, load-bearing brain-fidelity audit answering whether goal-outcome fulfillment detection
("did the character get what they wanted") should be architected TOP-DOWN (maintained goal actively
biases interpretation of the outcome) or BOTTOM-UP (outcome extracted independently, then compared).
Finding: 4 independent lit-scans (RPE/OFC-vmPFC; PFC guided-activation/biased-competition/predictive
coding; situation-model/discourse comprehension; ACC/PRO-model + adversarial counter-search) converge
on TOP-DOWN. Our current `hdlab/goal_achievement.py::valence_channel` is bottom-up (uniform bag-of-
words valence vote over the whole outcome sentence, goal-blind) — a genuine fidelity divergence for
the sub-population where affect words ARE present but not bound to what the goal-owner cares about
(the standing project measurement: whole-passage affect acc ~0.615, below the trivial rule, on the
49% of DesireDB items with affect words present). This is the BINDING half of the wall specifically;
it is not a fix for the OOV/vocabulary half (already separately tracked).

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed
regardless of pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable
bands, context pointers) — exp_dev owns exact implementation (which similarity threshold, exact
dependency-arc weighting formula, exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_goal_cued_valence_channel_v1` (primary, do this first — cheapest, most precedented, reuses only owned organs)

**Anchor pointer:** research note section "Concrete brain-faithful architecture recommendation" +
"Cheap decisive test."

**Substrate-product reading:** if this HARD-PASSes, it directly replaces the goal-blind bag-of-words
`valence_channel` fallback in `hdlab/goal_achievement.py` with a goal-cued/biased-competition-style
weighted channel, closing (or substantially narrowing) the affect-binding half of the DesireDB
whole-passage-affect shortfall (~0.615 vs the trivial-rule baseline) without adding any new
primitive or external dependency — a drop-in channel replacement, not a new subsystem.

**Tier hint:** load-bearing if HARD-PASS — this is the number that decides whether the top-down
architectural reframe is the right next build for the goal-achievement comprehension program, or
whether the affect-binding residual needs a different mechanism. A HARD-FAIL here does NOT refute the
brain-fidelity literature (that convergence is independent of any one implementation), it would mean
this specific implementation's goal-cue signal is too weak/noisy on real DesireDB prose and needs a
richer cue (see HARD-FAIL triage in the research note).

**Why now:** cheapest possible test — reuses `hdlab.goal_typing.find_desired_state` (goal cue
extraction, same pattern as the file's own existing `_verb_synonyms`), `candidate_generator.py`'s
existing unlabeled UD-parse dependency arcs (proximity/attachment weighting — no new parser),
`hdlab.lexical_similarity`/`hdlab.verb_lexical_similarity` (shared-feature similarity, already
owned), and the existing `opinion_lexicon`/`wordnet_polarity_propagation` valence lookups already in
`valence_channel`. No new infra, no external calls, no gradient training.

**Design (from the research note, exp_dev owns implementation details):**
1. Build `goal_cued_valence_channel(desire, outcome)`: form a goal cue from
   `hdlab.goal_typing.find_desired_state(desire)` (desired-class + referent + key content lemma(s),
   WordNet-neighbor-expanded the same way `goal_achievement.py::_verb_synonyms` already does for the
   relation channel).
2. For each candidate valence-bearing token in `outcome` (same detection as current
   `valence_channel`: `opinion_lexicon` hit or `wordnet_polarity_propagation.dictionary_lookup` hit),
   compute a relevance WEIGHT to the goal cue — exp_dev picks the exact formula (e.g. dependency-arc
   distance/attachment to the goal referent's mention via `candidate_generator.py`'s arcs, or a
   shared-feature-similarity bucket via `lexical_similarity`/`verb_lexical_similarity`) and states it
   once in the pre-reg, not tuned/swept per-item.
3. Weighted-vote (not uniform-count) the polarity signals using that relevance weight; keep the
   existing negation-flip logic (`_verb_negated_before`) unchanged.
4. Compare THREE arms on the same held-out DesireDB split used to produce the 0.686/0.620
   macro-F1 numbers already cited in `goal_achievement.py`'s own docstring (exp_dev locates the exact
   eval harness — likely needs to be authored fresh since no existing `experiments/*.py` cell was
   found calling `goal_achievement_verdict` directly; the docstring's numbers imply one exists or was
   run inline — verify which, and if it must be authored, use DesireDB, Rahimtoroghi/Wu/Wang/Anand/
   Walker SIGDIAL 2017, same n=80 balanced seed 20260808 split for direct comparability):
   (i) CURRENT uniform `valence_channel` (reproduce exactly, as the baseline),
   (ii) `goal_cued_valence_channel` (the mechanism arm),
   (iii) SCRAMBLED-goal-cue control (same weighting mechanism, but the goal cue is drawn from a
   DIFFERENT random item's desire — falsifies whether goal-RELEVANCE is the active ingredient, vs.
   any per-token down-weighting improving things by variance-reduction alone; mirrors the
   scrambled-weight-table control pattern already used in
   `exp_coherence_role_compat_score_selector_v1`).
5. Report accuracy (or macro-F1, matched to whichever metric produced 0.686/0.620) for all three arms
   on: (a) the FULL held-out set, (b) the mixed-polarity/relation-abstain subset specifically (items
   where `relation_channel` returns `reason in {"abstain", "no_goal"}` AND the outcome sentence has
   >= 2 valence-bearing tokens with mixed polarity — the population the research note identifies as
   structurally most exposed to goal-blind bag-of-words confusion), (c) the single-clause/
   unambiguous subset (0-1 valence tokens — the regression-check population).

**Pre-registered bands:**
- HARD-PASS: (ii) beats (i) by >= 10 points accuracy/macro-F1 on subset (b) AND (ii) beats (iii) by a
  comparable margin on subset (b) (confirming goal-RELEVANCE, not just reweighting-per-se, is the
  active ingredient) AND (ii) does not regress subset (c) by more than 2 points relative to (i).
- HARD-FAIL: (ii) is within 3 points of (i) on subset (b) (goal-cue weighting isn't the lever even
  where affect words are present — triage per the research note: is the dependency-arc/similarity
  signal too noisy on real DesireDB prose, or is the goal-cue extraction itself (CLASS_REGISTRY-style)
  too narrow — richer goal-cue representation is the next thing to try, NOT abandonment of the
  top-down direction, since the brain-fidelity convergence in the research note is independent of
  this one implementation choice) OR (ii) regresses subset (c) by > 5 points (weighting is
  net-harmful / needs to be soft-graded rather than a hard gate, per predictive coding's own emphasis
  on precision-weighted combination, not override).
- INVALID: (i) does not reproduce the existing 0.686/0.620-adjacent baseline numbers on whatever
  split is used (harness/construction mismatch — fix before interpreting further); OR subset (b)/(c)
  are too small (n < ~15 each) on the existing n=80 DesireDB set to support the HARD-PASS/HARD-FAIL
  thresholds above — if so, exp_dev flags this and either sources additional DesireDB items or widens
  the thresholds with justification in the pre-reg, does not silently proceed on an underpowered
  split.

## Context pointers (files, not summaries)

- `notes/research_brain_fidelity_goal_outcome_architecture_2026-08-09.md` — full brain-fidelity
  synthesis, all 26 verified citations, per-mechanism SHAPE/POSITION/METRIC tables, the top-down
  verdict, and the honest scope limit (this fixes the affect-BINDING half of the wall, not the
  OOV/vocabulary half).
- `hdlab/goal_achievement.py` — the module to extend; `valence_channel` (line ~108) is the function
  being reframed; `relation_channel` (line ~80) is the existing goal-cued channel to model the new
  one's goal-cue-extraction pattern on (`_extend_goal`, `_verb_synonyms`).
- `hdlab/goal_typing.py` — `find_desired_state` (goal-side extraction), `CLASS_REGISTRY` (existing
  hand class taxonomy, reusable for the goal-cue if useful, not required).
- `hdlab/candidate_generator.py` — existing unlabeled UD-parse dependency-arc extraction, reusable
  for the relevance-weighting signal (documented as heuristic/over-generating; fine for a relevance
  proxy, not required to be precise).
- `hdlab/lexical_similarity.py`, `hdlab/verb_lexical_similarity.py` — owned shared-feature similarity,
  alternative/complementary relevance signal to dependency-arc proximity.
- `experiments/exp_coherence_role_compat_score_selector_v1.py` — the scrambled-weight-table control
  pattern to mirror for arm (iii) above.
- `notes/goal_owner_attribution_pipeline_brain_fidelity_audit.md` (2026-08-09, same day) — documents
  the SAME divergence pattern (bottom-up positional/bag-of-words heuristic where the brain runs
  competitive multi-cue integration) at the thematic-role-labeling pipeline stage; not this hand-off's
  target, but relevant background if a shared relevance-weighting primitive turns out to be useful at
  both stages.
- DesireDB source: Rahimtoroghi, Wu, Wang, Anand & Walker, SIGDIAL 2017 — exp_dev locates the actual
  data file/loader used to produce the 0.686/0.620 numbers cited in `goal_achievement.py`'s docstring
  (not found by this hand-off's author via `experiments/*.py` grep — may have been run inline/ad hoc;
  verify and, if genuinely absent, author the harness fresh using the same n=80 balanced seed 20260808
  convention named in the docstring).

## Contract section

- exp_dev owns: exact relevance-weighting formula (dependency-arc distance vs similarity-bucket vs a
  combination), exact weight-to-vote mapping, exact cell/file naming, exact seed handling, whether to
  locate or author the DesireDB eval harness.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/HARD-FAIL/INVALID bands,
  the mandatory scrambled-goal-cue control (arm iii — not optional, this is what makes the test a
  real falsification of "goal-relevance is the lever" rather than a vacuous "any reweighting helps"
  result), and the glass-box/no-external-embedding/no-LLM-at-inference invariant — every organ named
  above is already owned; nothing in this test may introduce a trained/opaque component.
- Per no-bolt-on-reader / no-borrowed-embeddings invariants: WordNet/opinion_lexicon are already-used
  structural lexical resources, not a pretrained embedding — consistent with the existing
  `goal_achievement.py` approach, no new external-model dependency introduced.

## Autonomy declaration

exp_dev decides the exact relevance-weighting formula, exact cell/file naming, exact seed count, and
whether to combine the harness-location/authoring step with the mechanism cell or split them. The
falsifiable bands and the mandatory scrambled-goal-cue control (arm iii) are NOT exp_dev's to loosen
or drop without flagging the change explicitly in the pre-reg.
