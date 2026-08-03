# Pre-reg: intent_valence_via_mentalizing_v1

**Date:** 2026-08-03
**Author:** hdi_exp_dev (spawned by hdi_research)
**Anchor:** `intent_valence_via_mentalizing_v1`
**Cell:** `experiments/exp_intent_valence_via_mentalizing_v1.py`

## Prior-work check (substrate_query.sh, MANDATORY before authoring)

Query: `"valence intent mentalizing theory of mind beneficiary irony"` -> top cosine=0.3037
(`beneficiary` concept node, WordNet/VerbNet -- not a prior CELL), next `pretense theory of
irony` (math atoms, cosine=0.2822, not a prior cell). **No prior ARC CELL at cosine>0.30** --
this is genuinely novel composition, not a rediscovery. The two cells it extends
(`exp_situated_goal_structure_valence_v1.py`, `exp_grounded_structure_phase0_probe_v1.py`) and
the ToM organ (`exp_theory_of_mind_sally_anne_nested_hrr_v1.py`) are read directly per the
Director's spawn pointers, not via KB search (they are named artifacts, not KB-discovered).

## Question

Both prior valence cells use SURFACE-WORD lexical valence (`HARM_WORDS`/`HELP_WORDS` token
match). This fails the intent-vs-surface cases:
- **011** (Dorothy slaps the Lion): surface action is lexically HARM (slap), but the true
  BENEFICIARY of the intent is Toto (the Lion is the instrumental patient, not who the act is
  *for*) -- a beneficiary-vs-patient confusion.
- **007** (Jo: "let her take care of herself"): surface words ("care") read HELP, but Jo's
  actual intent is spiteful retaliation (HARM) -- an irony case, only resolvable by knowing
  Jo's affective stance toward Amy, which itself derives from Amy having wronged Jo earlier in
  the same chapter (item 008, gold-verified).

USER's directive: the brain structure that does this is MENTALIZING (mPFC/TPJ) -- inferring an
agent's internal state (goal-object / affective stance) which can diverge from the surface
action -- and the substrate already has a HARD_PASS mentalizing organ
(`exp_theory_of_mind_sally_anne_nested_hrr_v1.py`, Q2_false_belief=0.806 vs baseline=0.138,
gap=0.668, `data/exp_theory_of_mind_sally_anne_nested_hrr_v1/metrics.json`). REUSE it rather
than reinventing a lexical patch.

## What is reused (not reinvented)

The ToM organ itself is a standalone experiment cell (not an importable `hdlab/` module) --
its validated MECHANISM CLASS is: **per-agent partitioned FHRR bank + bind/unbind + accumulate
(bundle) + cleanup-argmax decode**, where an agent's tracked internal state is read back from a
DEDICATED per-entity register rather than from ground truth. That exact architectural pattern
is already promoted into `hdlab/situation_model_accumulate.py`
(`AccumulateRegister`, validated HARD_PASS at atom 29609, same bind/bundle/unbind chain) and
already extended once before by `CausalLinkRegister` (reversed-role query: unbind by ROLE,
cleanup-argmax over the EVENT vocabulary -- a valid FHRR symmetry since elementwise complex
multiply commutes). This cell extends `AccumulateRegister` a SECOND time, the same way
`CausalLinkRegister` did, into `MentalStateAffectRegister`: per-agent bank of "valence I
RECEIVED from source X", queried by (owner, source) to predict the owner's own affective
stance toward that source (retaliation/reciprocity inference -- a canonical mentalizing
computation: inferring what someone else likely feels from a model of what happened to them,
not from their literal words). This IS reuse of the ToM organ's validated primitive (bind +
per-entity partition + accumulate + cleanup-argmax decode, imported directly from the promoted
`hdlab/situation_model_accumulate.py` module, not reimplemented from scratch), applied to a new
content domain (affect instead of belief-location) -- consistent with WIRE-DON'T-ISLAND.

`hdlab.coreference_resolver`'s TrackedEntity/mention-stream machinery is NOT used directly (as
`exp_situated_goal_structure_valence_v1.py` already documented, it needs a multi-mention
passage this single-clause eval schema lacks); AGENT/TARGET entity identification is supplied
as declared factual metadata (character names visible in the text), exactly the same tier as
the already-accepted `novel`/`chapter`/`line_range` gold fields -- NOT a valence or category
flag, so not contaminating.

`hdlab.situation_model_multibank` / `CausalLinkRegister`'s existing GOAL/causal-chain machinery
is not directly invoked here (the discriminator scope is 12 hand-verified items, below the
multibank capacity threshold where it would matter) -- `AccumulateRegister` flat mode is the
correct-scope choice per its own documented capacity data (flat and multibank decode
identically at this pilot load).

## Mechanism (ONE variable: VALENCE SOURCE)

Both arms hold TARGET (`sgv.resolve_target`, reflexive-marker proxy, unchanged) and
CAUSAL-ATTRIBUTION / PRIOR_BLOCK (`gs.resolve_prior_block_oracle`, the phase-0 bridging oracle,
unchanged) FIXED. Only the VALENCE feature source varies:

- **SURFACE_VALENCE** (arm A, reproduces the known fails): `gs.resolve_valence_blind`, fixed
  lexicon, category-blind.
- **INTENT_VALENCE_MENTALIZING** (arm B, mechanism): for each item,
  1. If a declared BENEFICIARY fact exists AND differs from the item's surface grammatical
     target (patient) -- valence = HELP (the action is instrumental in service of a third
     party's protection, not harm toward the patient). Declared as an ORACLE-TIER fact for item
     011 ONLY (`BENEFICIARY_ORACLE = {"relinf_unstated_011": "Toto"}`), sourced from the real
     untruncated Baum text one clause before the citation boundary ("fearing Toto would be
     killed" -- excluded from the gold citation per its own `why_inferred` note) -- an
     independently-checkable textual fact, NOT the category label. Declared explicitly as an
     oracle ceiling, same tier/precedent as phase-0's `ORACLE_PRIOR_BLOCK`; AUTO_BLIND
     beneficiary resolution is reported separately and is honestly expected to NOT fire in this
     12-item excerpt (no earlier item establishes a Dorothy-Toto care-bond within the
     `unstated_goal` subset -- checked, absent).
  2. ELSE query `MentalStateAffectRegister.query_affect(owner=agent, source=target)` (fully
     AUTOMATIC, no oracle): built from all items strictly earlier in the same novel (matches
     `resolve_prior_block_auto_blind`'s existing strictly-earlier discipline), recording
     `add_affect(owner=<recipient>, source=<acting agent>, valence=<surface blind valence of
     that earlier action>)`. If the CURRENT item's agent was previously the RECIPIENT of a
     signal from the CURRENT item's target (with margin above the refuse-gate threshold, reused
     from the ToM organ's `cleanup_with_refuse` pattern), predict the SAME valence class as a
     retaliation/reciprocity inference.
  3. ELSE fall back to SURFACE_VALENCE (no override available).
- **INTENT_VALENCE_ABLATED_TOM** (arm C, negative control): identical composition, but the
  `MentalStateAffectRegister` is built from a SCRAMBLED (agent,target)->register-key mapping
  (fixed, seeded permutation of the entity-name vocabulary) BEFORE writing events -- corrupts
  WHAT the register holds while preserving its structure/noise level. Query keys for the
  CURRENT item stay real (unscrambled) so the ablation isolates "does the register need to be
  TRUE," not "does having any register help." The declared BENEFICIARY_ORACLE fact for 011 is
  NOT touched by this ablation (it is not part of the ToM mechanism under test).
- **TEXT_ONLY_LEXICAL** / **RANDOM**: reused verbatim from `ci.score_goal_item` (no structure at
  all), reference floor.

## Fairness / contamination gates

- Every per-item record logs `valence_source` in
  `{SURFACE_LEXICON, BENEFICIARY_ORACLE_DECLARED, TOM_RETALIATION_REGISTER,
  SURFACE_FALLBACK_NO_TOM_SIGNAL}` -- explicit, auditable, not hidden.
- NEGATIVE CONTROL: `INTENT_VALENCE_ABLATED_TOM`'s item-007-specific fix MUST collapse (item
  007 reverts to INCORRECT under ablation) -- if it stays correct under a scrambled register,
  the retaliation mechanism was never doing the work and the result is CONTAMINATED.
- The BENEFICIARY_ORACLE fact for item 011 is declared exactly ONCE, sourced from real text
  (not the gold category), and its entity value ("Toto") is never equal to any candidate
  category name -- can't be reverse-engineered from the label set.

## Brain-fidelity gate

Composition is a mentalizing computation in BOTH sub-mechanisms: beneficiary resolution =
perspective-taking about what the agent's goal-object is (who they act FOR); retaliation
inference = inferring an agent's affective stance from a model of what happened TO them (a
canonical reciprocity/ToM computation, not a lexical rule). Failures (if any) are classified via
`gs.brain_fidelity_class` (reused verbatim) as BRAIN_LIKE_MISS vs ARCHITECTURE_ARTIFACT.

## Verdict bands

- `INTENT_VALENCE_WORKS`: item 011 correct under INTENT (decisively, not tied) AND item 007
  correct under INTENT AND ablation ladder holds (007 flips wrong under
  `INTENT_VALENCE_ABLATED_TOM`) -- REUSE validated, residual is the honestly-scoped IRONY
  subclass (item-007-style cases where NO earlier-chapter wronging fact exists to retaliate
  from) + event-extraction.
- `INTENT_VALENCE_PARTIAL`: fixes 011 but not 007 (or vice versa) with ablation holding for
  whichever fired -- partial REUSE validated, report which half and why.
- `INSUFFICIENT`: ToM reuse does not beat SURFACE_VALENCE net of the ablation control, OR the
  ablation control fails to collapse (contamination) -- diagnose brain-faithfully, do not claim
  a fix that isn't structurally earned.

## Compute architecture

Class (b) sequential-CPU with justification: n=12 items, D=1024 FHRR vectors, single register
build (<=12 events) -- wall time is sub-second; not a batching candidate (rule exemption per
`10s wall-time` clause).

## Cell-template mandates

- `arms_differ_verified`: SHA-256 hash test over the 5 arms' concatenated prediction sequences.
- `final_metrics_atomicity: tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare/BaseException).
- `crlb_floor: n/a` (fixed 4/12-item discriminator, no capacity sweep; the one quantitative
  claim -- FHRR single-event bind/unbind decode fidelity in the affect register -- is
  self-tested directly at D=1024, single event per entity, far below any capacity ceiling).
- `calibration_check: default_ok_for_this_regime` (refuse-gate margin threshold declared
  before running: 0.02, well below the near-1.0 single-event decode margin measured in
  self-test, well above cross-entity interference noise floor).
- `cell_chunked: false` (single-shot, n=12, seconds); `heartbeat_present: false` (exempt,
  elapsed_s << 1800s threshold).
- All numbers in the completion report tagged MEASURED@ / HYPOTHESIZED@ / CITED@.

## Content-filter safety

Public-domain texts only (Little Women / Wizard of Oz / Alice in Wonderland / Tom Sawyer, all
pre-1928). Metrics + at most 2 short quoted snippets (the "fearing Toto would be killed" clause
citation, and one HARM_WORDS token example) -- no bulk text reproduction.

## Run mode

RUN FOREGROUND inline in `.venv` to completion; `--self-test` first; deterministic seeding
(`ci.FIXED_RANDOM_SEED`, no `hash()`/`list(set())`). Git local-only commit after landing,
`--no-verify`, no push. Do NOT dispatch to any queue -- this is a foreground diagnostic cell.
