# PRE-REG: causal_attribution_bridging_v1 (2026-08-03)

## Question
Phase-0 (commit d76763195, `data/exp_grounded_structure_phase0_probe_v1/metrics.json`) found
the grounded appraisal structure needs an ORACLE prior-block (causal-attribution: "did agent
X thwart agent Y's earlier goal") to beat text-only (oracle_c4=0.75 vs strongest_text_only=
0.50); the fully-automatic AUTO_BLIND variant only TIES text-only (0.50) because its coarse
"any earlier same-chapter harm event" rule false-positives on `relinf_unstated_010` (Laurie
skating gets wrongly flagged REVENGE_PUNISH because Amy's unrelated harm-to-Jo event (008)
precedes it in the same chapter -- entity-linking-free). Can causal-attribution be derived
AUTOMATICALLY, via a BRAIN-FOUNDATIONAL mechanism (not a lexical/temporal/connective
pattern-extractor), and close (or move toward) the oracle's lift?

## BRAIN MECHANISM (not a new organ -- SAME circuit as coreference antecedent-retrieval)
Coreference resolution and causal-attribution bridging are both hippocampal/MTL RELATIONAL
ANTECEDENT-RETRIEVAL (pattern completion) over the accumulated situation model (Kintsch
construction-integration; Trabasso causal networks; Zwaan event-indexing). Resolving "she"
-> antecedent ENTITY is bridging-for-entities; resolving "her goal failed" -> antecedent
CAUSE is bridging-for-events. The brain has no separate causal-attribution module; it reuses
the same backward-looking-center / Centering-salience retrieval machinery.

**Mechanism = literal reuse of `hdlab/coreference_resolver.py`'s antecedent-pick primitive,
retargeted from entities to events:**
- `TrackedEntity` + `_pick_strict_cb` (strict-Cb: argmax over `most_recent_subject_clause`,
  i.e. the most recent clause < current where the entity held a grammatically-prominent
  AGENT role, tie-broken by recency) is imported UNCHANGED.
- Retarget: one `TrackedEntity` instance per candidate PRIOR AGENT in the same chapter. An
  entity gets a `clause_role[event_position] = "agent"` entry (the exact string
  `coreference_resolver.SUBJECT_LIKE_ROLES` checks for) IFF (a) that prior event's BLIND
  valence (reused verbatim, `resolve_valence_blind` from
  `experiments/exp_grounded_structure_phase0_probe_v1.py`) is HARM, AND (b) that event's
  PATIENT corefers with the CURRENT item's own protagonist -- the entity-linking gate,
  implemented via `coreference_resolver.normalize_tokens` token-overlap (the SAME name/
  nominal-branch machinery every resolver in the module shares).
- `_pick_strict_cb(compat, cur_clause=current_item_position)` (imported, unmodified) then
  performs the actual coherence-ranked backward search: `event_position` plays the role of
  Centering's `clause` index. This is the SAME antecedent-retrieval call coref makes for
  pronouns, called on a different candidate pool.
- Confidence: `coreference_resolver._pronoun_strict_cb_margin` (imported, unmodified) is
  reused verbatim to log a bridging-decision margin (0.0 on a criterion tie -- honest
  ambiguity signal, same semantics as the pronoun case).

**Situation-model storage (reuse, not re-invent):** once bridging identifies an antecedent
event, the link is written to `hdlab.situation_model_accumulate.CausalLinkRegister`
(`add_causal_link(cause_idx, effect_idx)`) and READ BACK via `query_cause_of(effect_idx)`
through genuine FHRR bind/unbind -- the discovered link is stored/retrieved by the validated
accumulate organ (atom 29609 lineage), not just held in a Python variable. Round-trip fidelity
(query_cause_of reproduces the write) is the storage-side correctness check.

**What is GIVEN vs INFERRED (measurement-first, isolates inference from extraction):**
GIVEN (declared, controlled, event-extraction stand-in -- explicitly NOT the mechanism under
test): per-event AGENT name, PATIENT name (or None), for the < 12 gold `unstated_goal` items
plus their same-chapter siblings, sourced from the novels' own established plot facts (public
domain, independently checkable), NEVER from the category label or a prior_block flag.
INFERRED (the mechanism under test): (1) which prior event's blind-valence is HARM,
(2) whether its patient corefers with the query item's agent, (3) WHICH prior event, if
multiple qualify, is the coherence-ranked (most-recent-agent-role) antecedent -- steps 2-3
are exactly coref's own job, retargeted.

## FAIR CONTROLS (pre-registered, mandatory)
1. **No gold-flag leakage**: bridging never reads `correct_category`, `distractor_categories`,
   or the `CATEGORY_STRUCTURE`/`ORACLE_PRIOR_BLOCK` tables. Verified by construction (the
   bridging function's only inputs are event position, blind valence, and the GIVEN
   agent/patient table) + reported per-item ("used" field lists exactly which GIVEN facts and
   which computed signals fed the decision).
2. **Shuffled-event-content control** (must degrade): for K=20 fixed seeds, randomly permute
   WHICH (agent, patient, blind-valence) triple is bound to which event POSITION within a
   chapter (positions/ordering held fixed; content-to-slot binding scrambled -- breaks the
   coherent agent-patient-position relation the mechanism depends on without changing the
   BLIND-valence computation pathway). Report the fraction of shuffles where item 007 still
   recovers prior_block=True with attributed_agent="Amy" -- must be well below 1.0 (chance
   floor given 2 same-chapter candidate slots ~= 0.5) for the result to be non-degenerate
   (i.e. the mechanism is not vacuously always-True regardless of content).
3. **Beat temporal-recency baseline**: `recency_baseline(item)` = the agent of the nearest
   preceding same-chapter HARM-valence event, WITHOUT the coreference/entity-linking gate
   (mirrors the old AUTO_BLIND bug). Bridging must NOT match recency's false-positive on
   `relinf_unstated_010` (recency baseline is expected to wrongly flag Laurie via Amy's
   unrelated harm-to-Jo event; bridging's entity-linking gate must correctly reject it).
4. **Future-event distractor control** (temporal-order sanity): a synthetic decoy event
   (Meg harms Jo) is inserted AFTER item 007's own position with a matching coreference
   target; bridging must NOT attribute to it (the `< cur_clause` backward constraint,
   inherited unmodified from `_pick_strict_cb`, must still be enforced).

## GATES (pre-registered before running)
- `BRIDGING_MATCHES_ORACLE`: per-item, bridging-derived prior_block == oracle prior_block on
  confused_4 (007/010/011/012). Report exact matches, not aggregated.
- `GROUNDED_BRIDGING` arm (Phase-0's `classify_grounded`, reused verbatim, fed
  bridging-derived prior_block instead of oracle) confused_4 accuracy >= strongest_text_only
  (0.50) for HARD_PASS-adjacent signal; matching oracle (0.75) is the stronger bar.
- Fairness gate: shuffle-control fraction < 1.0 (see control 2).
- Brain-foundational gate: verified by construction (literal import + retarget of
  `coreference_resolver`'s functions, no lexical/connective/temporal-pattern extractor
  authored) + per-item BRAIN_LIKE_MISS vs ARCHITECTURE_ARTIFACT classification (reuse
  Phase-0's `brain_fidelity_class`).
- **VERDICT categories**: `BRIDGING_WORKS` (matches oracle on confused_4, beats recency on
  010, survives shuffle+future-distractor controls, brain-fidelity gate holds) vs
  `BRIDGING_PARTIAL` (beats recency + survives controls but doesn't fully match oracle) vs
  `BRIDGING_INSUFFICIENT` (fails to beat recency, or fails a control, or degenerate under
  shuffle).

## Compute architecture
(b) sequential-CPU with justification: n=4 confused items + <=3 events per chapter; FHRR ops
at D=256 (matches sgv/ci's declared dim); wall time expected < 5s total. No GPU batching
candidate.

## CELL-TEMPLATE fields
- `cell_chunked`: false (single-shot, seconds)
- `final_metrics_atomicity`: tmp_replace
- `crlb_floor`: n/a (fixed-item discriminator, no capacity sweep; the one quantitative claim
  -- CausalLinkRegister FHRR round-trip fidelity -- is self-tested directly at D=256, far
  below any capacity ceiling for a handful of links)
- `calibration_check`: default_ok_for_this_regime (GIVEN agent/patient table declared before
  running, not tuned post-hoc; blind-valence table reused verbatim from Phase-0/sgv)
- `arms_differ_verified`: true (smoke gate, hash-test over BRIDGING / RECENCY_BASELINE /
  ORACLE / TEXT_ONLY_LEXICAL / AUTO_BLIND_OLD prediction vectors)
- `deterministic_seeding`: true (fixed int seeds for the 20 shuffle draws, `random.Random`,
  never `hash()`/`list(set())`)
- `progress_logging`: n/a (elapsed_s << 1800s threshold)

## Content-filter safety
Public-domain (Little Women / Alice in Wonderland / Wizard of Oz / Tom Sawyer), metrics-only
report with <= 2 short snippets, no bulk text reproduction.
