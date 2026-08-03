# Pre-registration: grounded_appraisal_sim_earned_v1

Date: 2026-08-03. Author: exp_dev (cell author). Branch: local, NO push.
Design source: `notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` (2b sim spec, 2c
three-floor can-fail) + `notes/audit_grounded_foundation_program_VET_2026-08-03.md` (the 6 holes this
build fixes: esp #2 retaliate-primitive, #4 construction-determination). Director task 2026-08-03.

## One-line question
Does the substrate EARN the appraisal -> action-tendency dynamics from SIMULATED experience (no
text, no borrow, glass-box FHRR), such that REVENGE (harm directed at the true causal blocker)
EMERGES from primitive actions, generalizing to HELD-OUT agent identities?

## What is genuinely new (per design 1.5 "what's genuinely new")
The DYNAMIC temporal-causal mapping (goal-blocked-BY-agent -> appraisal -> targeted harm-toward-the-
causal-agent), earned by error-driven update over simulated consequence. No lexicon/rating table
contains this. KB-check (substrate_query.sh 2026-08-03): no prior grounding-SIMULATION cell; top hits
cosine 0.35 ("retaliation" WordNet, generic GO/action ontology terms) = NOT this mechanism. NOVEL.

## GUARDS held (entirely-brain-foundational bar; non-negotiable)
- **NO `retaliate` action label** (fixes VET #2). Primitive action set = {pursue, withdraw,
  harm(target), help(target)}, target = ANY candidate agent. "Revenge" = the LEARNED policy of
  harm(the-attributed-blocker). Targeting is EARNED from reward, never supplied.
- **Earn causal-COHERENCE not recency** (fixes tonight's recency falsification). Multi-candidate
  blocks: >=2 candidate agents act near the block; the TRUE blocker is the coherent one (its action
  explains A's goal-flip). Recency is DECORRELATED (true blocker is most-recent only ~1/n_cand of
  the time), so a recency shortcut cannot solve targeting.
- **Supply ONLY innate + appraisal schema.** Supplied: Spelke agent/object slot (identity + goal
  slot), Scherer CPM appraisal DIMENSIONS as a fixed check-sequence (goal-relevance, congruence,
  causal-attribution-slot, coping-potential). EARNED: (a) which candidate is the causal agent
  (coherence weighting), (b) the appraisal-vector -> action-tendency mapping.
- **NO borrow / LLM / text.** Discrete synthetic world; FHRR hypervectors (hdlab.binding /
  hdlab.bundling REUSED, project-native, NOT borrowed); glass-box linear reward-modulated readout
  (delta rule = three-factor Hebbian; theta inspectable).
- **Named sim-substitute limit.** The simulation is a NAMED SUBSTITUTE for embodied pre-literate
  experience; this cell does NOT claim full understanding, and SIM-TO-TEXT transfer is NOT claimed
  (a later stage; VET holes #5/#8 are explicitly out of scope for THIS cell).

## World / episodes (discrete, no text)
- Agents: TRAIN pool (24 ids) + disjoint EVAL pool (24 ids), each an integer + a random FHRR
  identity vector. Held-out eval = identities NEVER seen in training (no identity memorization).
- Each episode: focal agent A with a goal; n_cand=3 candidate agents act near a goal-relevant event.
- 4 episode types, each with a UNIQUE (congruence, coping) appraisal signature; correct action:
  - BLOCK_HIGH  (congruence=HURT, coping=HIGH) -> harm(true_blocker=coherent candidate)  [revenge]
  - BLOCK_LOW   (congruence=HURT, coping=LOW)  -> withdraw                                [helpless]
  - RECIPROCITY (congruence=HELP, coping=HIGH) -> help(true_helper=coherent candidate)    [gratitude]
  - NEUTRAL     (congruence=NEUTRAL)           -> pursue                                  [progress]
- Coherence marks the causally-relevant candidate (coh=1); recency assigned independently.

## Actions (8; primitive; no retaliate label)
pursue, withdraw, harm(c0), harm(c1), harm(c2), help(c0), help(c1), help(c2). Chance acc = 1/8 = 0.125.

## Reward (world dynamics the substrate must DISCOVER from consequence)
- BLOCK_HIGH: harm(true_blocker)=+1; harm(bystander)=-0.5; else 0.
- BLOCK_LOW:  withdraw=+1; harm(anyone)=-0.5; else 0.
- RECIPROCITY: help(true_helper)=+1; harm(anyone)=-0.5; else 0.
- NEUTRAL: pursue=+1; harm(anyone)=-0.5; else 0.

## Arms (each isolates one thing)
- FULL: action-type + coherence/recency-of-target + congruence + coping. IDENTITY-FREE (so held-out
  generalization is structural + empirically verified). Trained.
- RANDOM: FULL encoder, theta random, UNtrained. Isolates "solvable without learning" (must be ~chance).
- MEMORIZED: identity features only (candidate + focal identity) + action-type. NO coherence, NO
  appraisal. Trained on train ids, eval on HELD-OUT ids. Isolates identity-shortcut generalization.
- NO_APPRAISAL: action-type + coherence/recency-of-target, but NO congruence/coping. Trained.
  Isolates whether the appraisal DIMENSIONS add value (if it matches FULL, appraisal is vacuous).
- RECENCY: derived at eval; targeting forced to most-recent candidate. Isolates coherence-vs-recency.

## Metrics
- correct_action_acc (held-out): argmax action == reward-maximizing action. Primary.
- revenge_emergence_rate: P(policy picks harm(true_blocker) | held-out BLOCK_HIGH).
- targeting_specificity: among held-out BLOCK_HIGH where a harm action chosen, frac targeting true blocker.
- bystander_harm_rate: P(harm(bystander) | held-out BLOCK_HIGH).
- earned_restoration vs recency_restoration on held-out BLOCK_HIGH (goal restored = harm true blocker).
- FULL_train vs FULL_heldout acc (generalization gap).
- glass-box: Q(harm coherent-candidate) - Q(harm recent-candidate) on a canonical BLOCK_HIGH state
  (earned coherence-over-recency witness).

## Envelope-fail bands (PRE-REGISTERED; ALL floors MUST FAIL for a real PASS)
- random_failed: RANDOM_acc < 0.25 (near chance 0.125). If RANDOM >= 0.25 -> CONSTRUCTION_DETERMINED.
- memorized_failed: MEMORIZED_heldout < 0.30 AND (FULL_heldout - MEMORIZED_heldout) >= 0.20.
- appraisal_nonvacuous: (FULL_heldout - NO_APPRAISAL_heldout) >= 0.05.
- beats_recency: (earned_restoration - recency_restoration) >= 0.25.
- generalizes: |FULL_train - FULL_heldout| <= 0.10 AND FULL_heldout >= 0.70 (strictly above chance +
  above MEMORIZED by >=0.20; META_RULE_L strict band).
- revenge_emerged: revenge_emergence_rate >= 0.70 AND targeting_specificity >= 0.80.

## Verdict logic
- CONSTRUCTION_DETERMINED if RANDOM_acc >= 0.25 OR (NO_APPRAISAL >= 0.90 AND (FULL-NO_APPRAISAL)<0.05)
  -> the sim is too easy / trivially solvable without the earned appraisal (redesign, per design 2c).
- MECHANISM_EARNS if random_failed AND memorized_failed AND generalizes AND revenge_emerged AND
  beats_recency AND appraisal_nonvacuous.
- MECHANISM_EARNS_APPRAISAL_VACUOUS (PARTIAL) if all the above EXCEPT appraisal_nonvacuous (earns,
  but raw features suffice; informative negative -> shrink the supply list).
- MECHANISM_CANNOT_EARN if FULL_heldout < 0.40 OR (not revenge_emerged AND FULL_heldout < 0.55).
- PARTIAL_MIXED otherwise.

## Compute architecture
sequential-CPU, justified: contextual-bandit online update has a genuine sequential dependency
(theta at step N depends on step N-1); tiny (N_DIM=256, 6000 train + 1500 eval episodes x 4 arms x
5 seeds); wall < 10 min foreground. No GPU batching benefit (online RL). storage: no_storage /
no_composition-of-stored-items (this cell learns a readout; not a retrieval/chain cell).

## SCHEMA-VET fields
- cell_chunked: true (per-seed unit via tools/exp_checkpoint.py; 5 seeds).
- start_marker_written: true. crash_diagnostic_present: true. heartbeat_present: true (per-seed tick).
- final_metrics_atomicity: tmp_replace.
- arms_differ_verified: true (theta hash across FULL/RANDOM/MEMORIZED/NO_APPRAISAL at smoke).
- baseline_in_band: RANDOM ~0.125 (below 0.05? no -- RANDOM is the must-FAIL floor, expected near
  chance; the "in-band" mechanism arm is FULL, expected 0.70-0.98). discriminator-fires: FULL must
  exceed RANDOM by a margin at smoke.
- cardinality_ok: EXPECTED_N_UNITS = 5 seeds (per-seed each runs all 4 arms + derived). Verdict
  counts len(per_seed); < 5 -> HARD_FAIL_CARDINALITY.
- crlb_n/a: no quantitative noise-floor capacity claim (FHRR decode of ~5 bound pairs at N=256 is far
  below any capacity ceiling; self-test asserts decode fidelity as a sanity gate, not a swept metric).
- calibration_check: default_ok_for_this_regime (bands set from chance 1/8 and structural recency
  1/n_cand BEFORE running; not tuned).
- deterministic_seeding: true (torch.Generator per seed; sorted(set()) id pools; OMP/OPENBLAS=1; no
  hash()-seeded RNG, no list(set()) ordering).
- progress_logging: print_flush_true + line_buffered_stdout (though wall < 30 min).
- discriminator survives scale: smoke at reduced episodes with FULL-vs-RANDOM gap check; FULL run at
  full episode counts. Gap is not capacity-limited (analytical: separable linear problem).

## HYPOTHESIZED expectations (NOT measured; tagged per META_RULE_AC)
- FULL_heldout ~ 0.90-0.98  HYPOTHESIZED (separable linear mapping, identity-free -> generalizes).
- RANDOM ~ 0.125  HYPOTHESIZED (chance over 8 actions).
- MEMORIZED_heldout ~ 0.125-0.20  HYPOTHESIZED (novel identities uninformative).
- NO_APPRAISAL ~ 0.30-0.40  HYPOTHESIZED (best-constant over 4 indistinguishable types ~ plurality).
- recency_restoration ~ 0.33  THEORETICAL (1/n_cand, n_cand=3).
All are predictions; the cell reports MEASURED. If floors do NOT fail as predicted, that is the
CONSTRUCTION_DETERMINED result and is reported honestly (design 2c).
