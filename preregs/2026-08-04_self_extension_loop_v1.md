# Prereg: exp_self_extension_loop_v1 (the first integrated self-extension loop)

**Date:** 2026-08-04. **Local-only:** no queue / remote / push. **Deterministic, multi-seed (8), resumable per-seed.**

## Question
Can the substrate MINT a new causal-role type ('goal-blocker') from READING, triggered by a
prediction-error residual against its current schema library and disposed by a STRUCTURALLY-
INDEPENDENT second view, WITHOUT drifting (no spurious mint on noise / no redundant mint on an
already-typed harm passage), AND does re-reading after minting improve goal-blocking attribution?

Cites: notes/brain_component_functional_map_2026-08-04.md; notes/research_self_extending_grounded_knowledge_prior_art_2026-08-04.md (parts a/e/h — NELL CPL independent-view coupling, Piaget disequilibrium, CLS fast-bind/slow-consolidate); exp_disequilibrium_novelty_signal_test_v1 (residual gap 0.27, p=3e-4 — the validated mint TRIGGER).

## The loop (minimal, on goal-directedness)
Seed the schema library W (Hebbian autoassociative, predictive_coding) with ONLY harm/physical
templates (physical_harm/help, theft, instrument, accident) — NO goal-blocking type. Read passages
(text). TYPE each passage's causal structure to a feature-atom bundle via a glass-box grounded
lexical typer (reuses coreference_resolver.normalize_tokens for tokenization). Then:
1. NOVELTY GATE = hdlab.predictive_coding.threshold_gate on residual_magnitude(obs, predict(W,obs)),
   threshold=0.25 (pre-registered; calibration probe: redundant-harm ~0.05, goal-block ~0.42,
   noise ~0.47 — 0.25 cleanly separates typed-harm from both novel classes).
2. SECOND INDEPENDENT VIEW = discourse/purpose-connective cue presence (so that / in order to /
   hoping to / wanted to / tried to / meant to / because / would / lest ... — a DISJOINT function-word
   class, never in the content-feature typer's lexicons). The residual PROPOSES; the second view
   DISPOSES. Brain: left IFG/pMTG connective processing — structurally distinct from the VTA-RPE /
   cortical predictive-coding novelty organ.
3. MINT operator: for a gate-passing passage, propose a new type whose signature = the passage's
   features NOT explained by its best-matching existing template (Carey placeholder; hippocampal
   fast pattern-separated binding of a novel schema trace, CLS McClelland 1995).
4. CONSOLIDATE (promote-gate = hdlab.self_improving_loop.decide_keep_or_revert abstain-band): a
   candidate type is written into W as a fixed point ONLY if >=2 passages independently confirm the
   same signature AND the aggregate residual-margin clears the abstain band (neocortical slow
   consolidation on repeated cross-view confirmation; NELL multi-cycle agreement).
5. RE-READ: residual on goal-block passages after minting; attribution (argmax template-cosine over
   the type inventory) before vs after.

Two loop MODES contrasted:
- FULL = residual gate AND second view (both must fire to enter minting).
- RESIDUAL_ONLY = residual gate alone (the anti-drift ablation; the key result).

## Passages
- SYNTHETIC controlled set (labeled synthetic, for statistical power): K=8 each of {goal_block,
  noise, redundant_harm}, templated text with word-bank fills.
- REAL ruler items (n small, DIRECTIONAL): grapp_mcca_004 (Amy blocked-goal, gold) as goal_block;
  a gold harm item as redundant. Loaded best-effort from data/eval_gold_mention_role_mcguffey_v1.

## Pre-registered bands (majority of 8 seeds)
Controls (MUST behave — the whole point):
- C1 NOISE-NO-MINT (FULL): FULL mode mints 0 spurious (non-goal) types.
- C2 REDUNDANT-NO-MINT (FULL): no new type minted from harm passages (residual gate blocks).
- C3 UTILITY-LIFT: goal-block attribution accuracy AFTER mint > BEFORE mint (strictly), and no
  regression on redundant-harm attribution.
- C4 ANTI-DRIFT ABLATION (key): RESIDUAL_ONLY mode mints >=1 spurious (noise) type; FULL mints 0
  spurious. Demonstrates the second view is load-bearing.
Target:
- MINTS goal_blocker: FULL mode mints exactly the goal_blocker type (signature = the goal
  sub-structure), confirmed by >=2 goal-block passages.

## Verdict logic
- SELF_EXTENSION_WORKS (milestone, VET hard) iff, majority of seeds: FULL mints goal_blocker AND
  C1 AND C2 AND C3 (utility lift>0, no regression) AND C4 (residual_only drifts, full does not).
- SECOND_VIEW_NOT_LOADBEARING iff FULL passes but RESIDUAL_ONLY does NOT drift (ablation vacuous).
- DRIFT_OR_INSUFFICIENT (honest negative, routes anti-drift redesign) iff FULL mints on noise or
  redundant, OR fails to mint goal_blocker, OR no utility lift.

## Guards
Glass-box; NO borrowed embedding/LLM/parser as mechanism; predictive_coding + self_improving_loop +
normalize_tokens reused bit-identical. Deterministic (OMP/OPENBLAS/MKL=1; RandomState(seed);
sorted()); multi-seed; resumable per-seed (tools/exp_checkpoint). No gold-answer leakage: the typer
reads only span/goal-description content words (never the gold type label or true-agent name); the
minted type NAME is arbitrary (placeholder); attribution "correct" judged vs a gold type label the
mechanism never reads. Construction caveat: feature typing is a supplied glass-box lexical map
(same accepted caveat as exp_disequilibrium_novelty_signal_test_v1); the two VIEWS are mechanically
independent (HD residual vs disjoint connective-cue presence). Store binary/newline=''; commit after
valid metrics.
