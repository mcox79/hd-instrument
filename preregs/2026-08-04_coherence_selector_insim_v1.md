# Pre-registration: coherence_selector_insim_v1 (2026-08-04)

## Problem
`cross_span_causal_binding_v1` (preregs/2026-08-04_cross_span_causal_binding_v1.md, landed
MIDDLE-BAND per its own predicted outcome) made the true blocker's causal link REACHABLE
(recall 0->3/4) but confirmed the SELECTION step is unsolved: the existing selector
(`_pick_strict_cb`, a recency operator) cannot discriminate a true causal antecedent from a
recent-but-non-causal distractor once both are reachable (recall_distr also lifts to 0.75).
Per `notes/research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md`
("Gap 1"), the missing organ is a genuinely-RETRAINED backward SR-transport map
(`train_sr_transport` on REVERSED transitions), not a transpose of the forward-certified M
and not the storage-only `CausalLinkRegister`.

## Hypothesis
A backward SR-transport map `M_backward`, trained via the SAME TD(0) delta-rule
(`train_sr_transport`, `experiments/exp_pfc_gate_cfrpe_trained_v2.py`) on REVERSED
(effect -> predecessor) rollout transitions collected only over a TRAIN partition of a
synthetic causal graph, will discriminate a graph-connected TRUE antecedent from a
graph-DISconnected but narratively-more-recent DISTRACTOR on HELD-OUT (EVAL-partition,
never seen during SR training) episodes -- beating recency, random, and raw-cosine
(no-replay-local) floors. This is the Foster-Wilson reverse-replay / Mattar-Daw
need-x-gain-shaped backward value computed BEFORE any link write, per the drill's
sharpened claim ("a LEARNED SCALAR, not a MEMORY LOOKUP").

## Mechanism (reuse, brain-structure-tagged; NO new organ)
- **SR-transport backward map**: `experiments.exp_pfc_gate_cfrpe_trained_v2.train_sr_transport`
  (TD(0) delta-rule over `(cur,nxt)` transitions), called AGAIN (not transposed) on
  `(effect_idx, predecessor_idx)` pairs collected by `collect_rollout_transitions` over a
  REVERSED adjacency built only from TRAIN-partition causal edges. Brain structure:
  hippocampal-striatal successor representation (Dayan 1993 / Stachenfeld 2017), scored by
  Foster & Wilson 2006 reverse replay / Mattar & Daw 2018 need x gain (value-shaped, not
  recency-shaped).
- **Scoring**: `reach_value(outcome_E, candidate_E, M_backward)` = cos(outcome_E @
  M_backward, candidate_E), reused verbatim (same function, arguments read as "does the
  backward map, applied to the outcome, predict this candidate").
- **Anti-tautology control**: `reach_control_targetcos(outcome_E, candidate_E)` (M:=identity),
  reused verbatim -- doubles as the NO-REPLAY-LOCAL floor (raw cosine, no dynamics).
- **Situation-model buffer**: `hdlab.situation_model_accumulate.AccumulateRegister`, reused
  as the DMN/hippocampal event-index buffer that indexes which events belong to an episode's
  situation model (2-role vocab so `cleanup_argmax` must genuinely discriminate); NOT used as
  the scorer (per the drill's Finding 1a/1b correction: it is a buffer/storage organ only).
  Its decode fidelity on episode-membership is reported as a glass-box sanity check that the
  buffer is genuinely exercised, not imported unused.
- **Abstain-band architecture**: `hdlab.self_improving_loop.decide_keep_or_revert` +
  `ABSTAIN_BAND_DEFAULT`, reused verbatim as CONTROL-FLOW (per the drill's Finding 1d
  correction: architecture reuse, not a drop-in function call) over the NEW margin quantity
  `reach_value(true) - reach_value(distractor)`.
- **Recency floor**: literal position-comparison (structurally the same operator class as
  `hdlab.coreference_resolver._pick_strict_cb`, confirmed-falsified 0/4 on the real recency-trap
  items per the WHERE-banner, commit e34d54701) -- included as the floor that MUST fail here too.

## Data (the sim = a NAMED SUBSTITUTE for experienced causal episodes)
Synthetic causal graph over `V_TOTAL` bipolar-codebook nodes (`N_DIM`-dim, FHRR-free real
bipolar per `make_bipolar_E`, matching `exp_pfc_gate_cfrpe_trained_v2`'s substrate exactly --
no borrowed embedding). `V_TOTAL` split into disjoint TRAIN and EVAL node partitions (never
overlapping indices). Within each partition, directed CAUSES edges are drawn at a fixed
density (a node's true cause is a direct in-edge predecessor). Each episode = one outcome
node with >=1 in-edge: TRUE candidate = a real predecessor (edge exists); DISTRACTOR
candidate = a same-partition node with NO edge to the outcome, assigned a narrative position
LATER (closer to the outcome) than the true candidate's position -- the deliberate recency
trap (mirrors the real `grapp_mcca` items' DISTR_CAND-at-later-position construction). Because
embeddings are i.i.d. random bipolar vectors independent of graph structure, raw cosine
(no-replay-local floor) carries zero graph information by construction -- this is the built-in
guard against coherence and recency (or coherence and raw similarity) being accidentally
correlated (Guard 2 in the task brief).

## One variable
The SELECTOR applied to (outcome, true-candidate, distractor-candidate) triples. Graph, node
embeddings, episode construction, seed, N_DIM all held fixed across selector arms.

## Arms (floors that MUST fail + the organ under test)
1. `RECENCY` -- argmax(narrative_position) -- always picks the distractor by construction ->
   pre-registered to score 0% correct.
2. `RANDOM` -- seeded coin flip -> pre-registered ~50%.
3. `NO_REPLAY_LOCAL` -- `reach_control_targetcos(outcome_E, candidate_E)` (raw cosine, M:=identity)
   -> pre-registered ~50% (embeddings carry no graph signal by construction); this arm is
   simultaneously the anti-tautology guard for arm 4.
4. `COHERENCE_REVERSE_REPLAY` (the organ under test) -- `reach_value(outcome_E, candidate_E,
   M_backward)`, argmax over candidates, gated through `decide_keep_or_revert`'s abstain band
   (episodes where the margin does not strictly clear `ABSTAIN_BAND_DEFAULT` are scored as
   INCORRECT under the conservative primary metric, so abstention cannot inflate accuracy).
5. `ORACLE` (positive control) -- reads the TRUE graph edge directly (ground truth, not from
   M) -- must score 100% on both partitions or the episode-construction pipeline itself is
   broken and no other arm's verdict can be trusted.

## Generalization / anti-memorization
`M_backward` is trained ONLY on rollout transitions over TRAIN-partition edges. All four
non-oracle arms are evaluated on BOTH the TRAIN-partition episodes (in-distribution check) and
the EVAL-partition episodes (node identities and edges never seen during `train_sr_transport`
training) -- the EVAL-partition number is the primary, pre-registered metric. A result that
only holds on TRAIN partition episodes is memorization, not a learned function, and is reported
as such (not counted toward the verdict).

## Multi-seed
5 seeds (7, 17, 23, 31, 41); each seed redraws the full graph (embeddings + edges + episodes)
independently. Report per-seed and mean +/- std.

## Pre-registered PASS/FAIL bands (EVAL partition, mean over seeds)
- **HARD-PASS**: `COHERENCE_REVERSE_REPLAY` EVAL accuracy (conservative, abstain=incorrect)
  >= 0.75 AND strictly beats all three floors (RECENCY, RANDOM, NO_REPLAY_LOCAL) on EVAL by
  >= 0.15 absolute each AND the glass-box margin `mean(reach_value(true) -
  reach_value(distractor))` on EVAL is POSITIVE in every seed AND ORACLE == 1.0 on both
  partitions (positive-control gate).
- **MIDDLE-BAND**: beats all three floors on EVAL by a smaller margin (>0 but <0.15) or is
  positive in >=4/5 seeds but not all 5 -- read as "right mechanism-class, needs more
  rollout/SR-training budget (Gap 1 underpowered)," not a refutation.
- **HARD-FAIL**: does not beat RECENCY and RANDOM and NO_REPLAY_LOCAL on EVAL (no better than
  floors already known to fail) OR the glass-box margin is not consistently positive OR the
  TRAIN-vs-EVAL gap shows the win only holds in-distribution (memorization, not a learned
  function). Per brain-faithful-losing = presumed-impl-bug-first: a HARD-FAIL triggers
  inspection of `sr_diag.err_first` vs `err_last` (did TD actually converge?) before any
  structural conclusion.

## Secondary (reported, does NOT gate the verdict)
Transfer-probe: apply the SAME trained-per-seed `M_backward`-style selector logic, re-purposed
as `reach_value` scored directly over the 7 Director-verified real-text
`multi_candidate_causal_attribution` items already used by `cross_span_causal_binding_v1`
(`grapp_mcca_001/003/004/005/007/008/009`, excluding the REJECTED `grapp_mcca_006`) IF a
compatible embedding/candidate-event representation for those items is available on disk at
run time; if not available in the time-box, this is reported honestly as NOT RUN rather than
approximated, and the sim result stands alone as the primary (in-sim) finding. n~7 is a thin
directional probe only, per the task brief.

## Guards
`torch.Generator` seeding (per-seed, per-purpose sub-seeds derived deterministically from the
seed, no shared mutable RNG state across arms); `sorted(set())` iteration; no `hash()`-seed;
resumable per-seed via `experiments._seed_checkpoint` (`write_partial_key`/`resumable_seeds`/
`aggregate_partials`, the same helper `exp_pfc_gate_cfrpe_trained_v2` uses); store writes
binary/atomic (`os.replace`); glass-box (every scalar traceable to `reach_value`/
`reach_control_targetcos`/graph ground truth, no black-box head); no borrowed embedding/LLM/
parser as the mechanism -- `make_bipolar_E` (i.i.d. random bipolar codebook) is the same
embedding primitive already certified in `exp_pfc_gate_cfrpe_trained_v2`.

## Honest scope caveats (stated before running)
- The sim is a NAMED SUBSTITUTE for experienced causal episodes: single-hop CAUSES edges are
  a simplification of real narrative causal chains (which may be multi-hop / conjunctive); a
  win here licenses "the mechanism-class works when coherence and recency are genuinely
  decorrelated," not "narrative causal attribution is solved."
- Construction risk: episode generation explicitly makes the distractor's narrative position
  LATER than the true cause's (the recency trap) while embeddings carry zero graph signal.
  This is a controlled trap BY DESIGN (matching the real `grapp_mcca` items' own construction),
  not an accidental confound -- but it does mean RECENCY is expected to fail by construction,
  not discovered; the informative comparison is COHERENCE vs RANDOM and COHERENCE vs
  NO_REPLAY_LOCAL, which carry no such built-in advantage.
- n=5 seeds per arm is adequate for a within-cell multi-seed stability check, not a
  large-N statistical study; this is a pilot cell per the task brief's own framing.
