# Pre-reg: Component-5 GOLD-ROLE-ISOLATED goal-owner + outcome-binding selector eval

2026-08-04, exp_dev, spawned by Director. Design source:
`notes/research_component5_goal_owner_selection_binding_2026-08-04.md` (mechanism/reuse map) +
`notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md` (Instance C spec,
disk-verified prior-work check: cosine 0.39-0.40 hits, both READ in full before authoring; this
cell IS the "first buildable step" (Section 6.1) that spec recommends, not a rediscovery).

## Question
Given GOLD (hand-derivable, Component-3-shaped) role labels -- bypassing Component-3's
in-flight perceptron entirely -- does a role-content-aware candidate + the existing gold-free
`route_passage`/`decode_coherence_margins`/`decide_keep_or_revert` selector (hdlab/self_improving_
loop.py, promoted 2026-08-02) beat pure recency on goal-owner + outcome binding? This is the
make-or-break density-gating check flagged by both design docs: `decode_coherence_margins` is
proven WRONG for causal antecedent selection (write-then-read symmetric, CausalLinkRegister) --
unverified whether goal-outcome binding shares that same symmetric-write failure mode.

## Corpus (reused verbatim, no new items)
`experiments/exp_situation_model_goal_outcome_dimension_v1.py`: GOAL_BLOCK (6), CONTROLS (6),
RECENCY (3: 2 genuine pronoun-antecedent traps + 1 non-trap sanity item). RECENCY items already
satisfy "goal-owner is NOT the most-recently-mentioned entity" by construction for the 2 real
traps (build-spec Section 4's stated prerequisite for Instance C -- already met, verified by
reading the item texts: Amy/Tom are the gold antecedent, Jo/Sid are the more-recent foil).

## Mechanism under test
1. BASELINE candidate = `RecencyEntityResolver` (reused verbatim, unchanged) -- backward search,
   first gender-compatible entity by recency.
2. CONTENT candidate = new `ContentMatchResolver` (~30 lines, this cell): tracks which entities
   carry an OPEN GOAL (a GOAL-role event with no OUTCOME yet bound, GOLD-typed via the existing
   `type_sentence_events` lexicon reused bit-identical); when resolving an ambiguous pronoun,
   prefers a gender-compatible entity that currently holds an open goal over pure recency; falls
   back to recency if no open-goal entity is in the compatible pool (honest fallback, not a forced
   win).
3. SELECTOR: `hdlab.self_improving_loop.route_passage` (reused verbatim) scores both candidates'
   whole-passage resolutions via `decode_coherence_margins` (gold-free FHRR decode-margin over
   `role_vocab = GO_ROLES = [GOAL, ACTION_AGAINST, OUTCOME_UNMET, OUTCOME_MET]`, the richer
   role-content signal named as the missing wire in both design docs) and adopts the content
   candidate iff its aggregate coherence-margin delta over disagreement positions clears the
   abstain band (0.02, unchanged default).
4. `event_slots` = global position index (not per-entity slot count) -- a deliberate
   simplification vs `GoalOutcomeRegister`'s per-entity slot scheme, because candidate
   reassignment changes an entity's own next-slot number; global-position slotting keeps
   role_seq/event_slots identical across candidates (route_passage's documented contract) while
   cluster_ids (the entity assignment) is the only thing that varies per candidate.

## Controls (mandatory per task brief)
- **Anti-recency**: both real traps have goal-owner != most-recent entity by construction;
  `anti_recency_holds` = final selected owner matches gold on both traps (not just the recency
  answer).
- **Role-scramble**: for the 2 trap items, swap which entity's GOAL-role position carries the
  gold GOAL label (mislabel the foil as the goal-holder instead of the true owner) while leaving
  text and gold binding target UNCHANGED. If the selector is genuinely role-content-driven,
  binding accuracy on the scrambled version must COLLAPSE to <= the recency floor. If accuracy
  survives scrambling, the "coherence" signal is not actually using role content (the same
  positional-confound failure mode as `_pick_strict_cb`) -- HARD-FAIL discriminator.
- **Control false-fire**: `treatment_fires` (unchanged, reused bit-identical) on the 6 CONTROLS
  must stay 0/6 -- this eval's binding change only touches the RECENCY items' ambiguous-pronoun
  positions, controls are unaffected by construction; re-verified, not assumed.
- **Sign check**: `route_passage`'s own gold-free `agg_coherence_delta` for the content candidate
  must be POSITIVE on genuine traps (internal mechanism consistency, not just accuracy).

## Metrics
- `goal_owner_binding_accuracy` (GOAL_BLOCK, gold explicit-name attribution): same-clause binding,
  reported HONESTLY as GIVEN not EARNED (Component-3 already solves this; no cross-sentence search
  needed, per the design drill).
- `outcome_binding_accuracy` (RECENCY, 3 items): HARD target beat 0.333 (fb5b2a188 recency
  floor). N=3 -> only 4 discrete outcomes (0, 0.333, 0.667, 1.0).
- `control_false_fire_rate`: must be 0/6.
- `role_scramble_collapse`: scrambled-outcome_binding_accuracy on the 2 trap items <= 0.333 (i.e.
  content really drives the pick, not a positional artifact).
- `coherence_margin_delta_sign`: positive on genuine traps.
- `anti_recency_holds`: bool.
- 3 seeds (FHRR generator seed only; mechanism logic is deterministic given role/gender lexicons)
  for margin-noise robustness; report per-seed + majority.

## Bands (per task brief, VERBATIM)
- HARD-PASS: `outcome_binding_accuracy >= 0.67` AND `role_scramble_collapse` holds AND
  `control_false_fire_rate == 0` AND `goal_owner_binding_accuracy >= 5/6`.
- MIDDLE-BAND: `outcome_binding_accuracy` in [0.334, 0.66] OR scramble only partially collapses.
- HARD-FAIL: `outcome_binding_accuracy <= 0.333` OR `role_scramble_collapse` fails.
- **SMALL-N CAP (mandatory, VET-as-hard-as-negative discipline)**: N=3 recency items is not
  powered for a HARD-PASS claim. If the formal band computes HARD-PASS, the REPORTED verdict is
  capped at `MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS` (mechanism-class license, not a landed
  statistical result) -- negatives (HARD-FAIL) are NOT capped, a small-N clean failure is still
  informative evidence per the density-gating risk this eval exists to check.

## Compute architecture
Sequential-CPU, in-process, single Python process, wall time < 10s (3 items x 3 seeds x tiny FHRR
decode, D2=1024). No GPU batching candidate -- cell IS a diagnostic/gate question
(compute-proportionality rule), not a training fit.

## Guards
Glass-box; `RecencyEntityResolver` / `type_sentence_events` / `GO_ROLES` / `route_passage` /
`decode_coherence_margins` / `decide_keep_or_revert` reused bit-identical (imported, not
reimplemented); deterministic given seed; ASCII-only; atomic metrics write (tmp + os.replace);
`except SystemExit: raise` before `except Exception`; no bare `except:`. NOT dispatched to any
queue -- direct in-process foreground run per task brief, LOCAL-ONLY, no push.

## HYPOTHESIZED vs MEASURED
All numbers in this pre-reg are HYPOTHESIZED@this-file (bands, targets) or CITED@fb5b2a188
(the 0.333 recency floor, `data/exp_situation_model_goal_outcome_dimension_v1/metrics.json:
means.recency_binding_accuracy`). No MEASURED numbers exist until the cell runs.
