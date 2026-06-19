# exp_dev hand-off -- research: substrate compositional shard system (3x)

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Substrate has empirically validated 53+ capabilities in cycles 211-217. The architectural
next step formalizes FHRR's existing nested binding capability as a multi-level shard
hierarchy where shards are first-class typed units at 5 granularities (atomic, sentence,
paragraph/function, story/module, document/codebase). The 12 validated reasoning primitives
(Bayesian, causal, modal, defeasible, analogical, AGM, active-inference, multi-hop,
paraconsistent, drift-diffusion, Allen-interval, ToM) are lifted to operate at shard level,
not just atom level. This is a mechanism extension, not a new mechanism: every composition
operator maps to existing FHRR algebraic operations already implemented in the substrate.

The theoretical basis is fully established. The engineering execution is approximately
2 weeks. The cheapest decisive test (ATOMIC-COMPOSITION-SMOKE) runs in 30 minutes CPU
with no new training. The HARD-FAIL gate for ATOMIC-COMPOSITION-SMOKE is Hits@1 < 0.70;
if this fires, N must be upgraded to 4096+ before proceeding.

---

## Anchor Candidates (rank-ordered by P_actionable x prerequisite order)

### 1. PP-COMP-SMOKE (HIGHEST PRIORITY -- gates all other anchors)

Anchor pointer: PP-COMP-SMOKE (new; not yet queued)
Substrate-product reading: validates that FHRR nested binding at L2 (paragraph-shard level)
  works operationally. If Hits@1 >= 0.90, the entire v3.0 shard architecture is on a sound
  empirical footing and the engineering build is authorized. If Hits@1 < 0.70, the current
  N=1024 is insufficient for L2 composition and N must be upgraded before any other shard
  work proceeds. This is the cheapest possible gate.
Tier hint: CPU laptop; 30 min wall; uses existing FHRR engine with N as config parameter.
Why-now: gates 9 downstream anchors and the entire v3.0 engineering build.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: Hits@1 >= 0.90 over 100 random 10-item L2 bundles via DECOMPOSE
  HARD-FAIL: Hits@1 < 0.70 (N upgrade required; do NOT proceed to other anchors)
  MID-BAND: Hits@1 in [0.70, 0.90] -- proceed with N=4096 configuration, not N=1024

Implementation sketch (NOT design mandate):
  - Build 100 L2 shards: each is BUNDLE_MERGE of 10 random L1 shards
  - For each L2 shard, run top-10 cosine retrieval against the L1 vocabulary
  - Report Hits@1 (fraction of L2 shards where the correct L1 shard is rank-1)
  - Run at N=1024, N=4096, N=8192 if MID-BAND to find operational floor

### 2. PP-SENT-COMP (sentence-level composition)

Anchor pointer: PP-SENT-COMP (new; not yet queued)
Substrate-product reading: validates composition and retrieval at the sentence/fact level
  using real text data rather than random vectors. Prerequisite: PP-COMP-SMOKE PASS.
Tier hint: CPU laptop; 1-2 hour wall.
Why-now: first real-text validation of L2 shard composition; prerequisite for all
  higher-granularity tests.

Pre-reg bands:
  HARD-PASS: sentence retrieval Hits@1 >= 0.80 from 10-item paragraph-shard (100 trials)
  HARD-FAIL: Hits@1 < 0.60

### 3. PP-SUB-OP (SUBSTITUTE operator)

Anchor pointer: PP-SUB-OP (new; not yet queued)
Substrate-product reading: validates the SUBSTITUTE operator, which is the algebraic basis
  for code refactoring, story editing, counterfactual reasoning, and causal do() operations.
  If SUBSTITUTE works cleanly (new-scene Hits@1 >= 0.85, old-scene <= 0.15), the entire
  causal + hypothetical + refactoring capability class is operationally validated.
Tier hint: CPU laptop; 1-2 hour wall.
Why-now: high leverage; 4+ product capabilities depend on this operator.

Pre-reg bands:
  HARD-PASS: new-scene Hits@1 >= 0.85 AND old-scene Hits@1 <= 0.15 (20-item story-shard, 50 trials)
  HARD-FAIL: new-scene < 0.70 OR old-scene > 0.30

### 4. PP-MHOP-SHARD (multi-hop through L2 shards)

Anchor pointer: PP-MHOP-SHARD (new; not yet queued)
Substrate-product reading: validates multi-hop traversal through composite shards. Extends
  the validated PP-258 (K-hop depth 10) to the shard level. Critical for the narrative
  analysis, argument traversal, and plan generation product surfaces.
Tier hint: CPU laptop; 2-4 hour wall.
Why-now: directly extends a validated empirical result; expected to pass given PP-258 success.

Pre-reg bands:
  HARD-PASS: F1 >= 0.65 on 3-hop chains through L2 paragraph-shards (50 examples)
  HARD-FAIL: F1 < 0.45

### 5. PP-SCHEMA-L2 (schema extraction at L2 level)

Anchor pointer: PP-SCHEMA-L2 (new; not yet queued)
Substrate-product reading: validates SCHEMA_EXTRACT operator at L2. Extends PP-282/284
  (schema extraction at 1000 categories validated) to paragraph-shard level. Critical for
  KB auto-evolution and curriculum learning product surfaces.
Tier hint: CPU laptop; 2-3 hour wall.
Why-now: extends a validated empirical result; expected to pass.

Pre-reg bands:
  HARD-PASS: schema cosine match to top-5 most common role-fillers >= 0.85 (50 paragraph-shards)
  HARD-FAIL: schema cosine < 0.60

### 6. PP-ANALOGY-L2 (cross-domain analogy at paragraph-shard level)

Anchor pointer: PP-ANALOGY-L2 (new; not yet queued)
Substrate-product reading: validates analogical transfer at paragraph-shard granularity.
  Extends PP-275 (RotatE Hits@1=0.899 at atom level). If top-3 >= 0.60, cross-domain
  hypothesis transfer and narrative structural analogy are both operationally viable.
Tier hint: CPU laptop; 3-4 hour wall.
Why-now: extends validated PP-275; highest-value new capability for scientific research surface.

Pre-reg bands:
  HARD-PASS: top-3 accuracy >= 0.60 on 30 cross-domain paragraph-shard analogies
  HARD-FAIL: top-3 < 0.40 (would indicate RotatE does not transfer to shard level)

### 7. PP-BAYES-SHARD (Bayesian inference at shard level)

Anchor pointer: PP-BAYES-SHARD (new; not yet queued)
Substrate-product reading: validates Bayesian reasoning lifted to story-shard level. 50
  binary narrative inference examples. If accuracy >= 0.75, the legal argument analysis
  product surface is empirically grounded.
Tier hint: CPU laptop; 2 hour wall.

Pre-reg bands:
  HARD-PASS: accuracy >= 0.75 on 50 binary narrative inference examples
  HARD-FAIL: accuracy < 0.55

### 8. PP-CAUSAL-MOD (causal do() on program module-shards)

Anchor pointer: PP-CAUSAL-MOD (new; not yet queued)
Substrate-product reading: validates causal intervention at module-shard level. 30 program
  module examples where do(input=X) is encoded as SUBSTITUTE and output-shard is predicted.
  Critical for code refactoring and program synthesis product surfaces.
Tier hint: CPU laptop; 3-4 hour wall.
Why-now: high product value; prerequisite for code-refactoring backend demo.

Pre-reg bands:
  HARD-PASS: top-1 accuracy >= 0.65 on 30 program module examples
  HARD-FAIL: < 0.50

### 9. PP-STORY-RES (story-shard resonator factorization)

Anchor pointer: PP-STORY-RES (new; not yet queued)
Substrate-product reading: validates resonator network factorization at L3 story level.
  This is the technically heaviest test; it uses iterative oscillator dynamics (Frady 2021)
  rather than direct cosine retrieval. Prerequisite: PP-SENT-COMP PASS.
Tier hint: CPU laptop or remote CPU; 4-6 hour wall.
Why-now: validates the highest-granularity composition; prerequisite for document-level work.

Pre-reg bands:
  HARD-PASS: all 10 paragraphs recovered at cosine >= 0.90 (10 story-shards tested)
  HARD-FAIL: any paragraph at cosine < 0.70

### 10. PP-CAPACITY-LEVELS (empirical kstar per level)

Anchor pointer: PP-CAPACITY-LEVELS (new; not yet queued)
Substrate-product reading: measures empirical kstar at L1, L2, L3 to validate or refute
  the theoretical SNR prediction (kstar ~ N/9). Critical for production scaling decisions.
  If empirical kstar < 50% of theoretical, there is a structural problem beyond SNR theory.
Tier hint: CPU laptop; 4-8 hour wall (sweep over K values).
Why-now: required for N upgrade decision (N=1024 vs N=4096 vs N=8192).

Pre-reg bands:
  HARD-PASS: empirical kstar within 20% of theoretical N/9 at each level
  HARD-FAIL: empirical kstar < 50% of theoretical at any level

---

## Prerequisite ordering

1. PP-COMP-SMOKE -- no prerequisite; run first
2. PP-SENT-COMP, PP-SUB-OP -- prerequisite: PP-COMP-SMOKE PASS (can run in parallel)
3. PP-MHOP-SHARD, PP-SCHEMA-L2, PP-ANALOGY-L2 -- prerequisite: PP-SENT-COMP PASS
4. PP-BAYES-SHARD, PP-CAUSAL-MOD -- prerequisite: PP-SUB-OP and PP-MHOP-SHARD PASS
5. PP-STORY-RES -- prerequisite: PP-SENT-COMP PASS; runs independently of 3-4
6. PP-CAPACITY-LEVELS -- can run in parallel with any; needed before N upgrade decision

N upgrade trigger: if PP-COMP-SMOKE returns MID-BAND or HARD-FAIL, run PP-CAPACITY-LEVELS
immediately at N=4096 and N=8192 to determine the operational N floor before proceeding.

---

## Context pointers

- Research note: notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md
- Prior multi-hop validation: data/exp_PP258_*/metrics.json (K-hop depth 10 validated)
- Prior schema extraction: data/exp_PP282_*/metrics.json and data/exp_PP284_*/metrics.json
- Prior RotatE analogy: data/exp_PP275_*/metrics.json (Hits@1=0.899)
- Prior capacity: data/exp_PP244_*/metrics.json (kstar = 0.0488 * N)
- exp_dev brief 2026-06-09 evening: notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md
- Counterfactual validation (Wish 1): see exp_dev brief 2026-06-09 (20/20 counterfactual)
- FHRR engine: hdlab/ (existing implementation)

---

## Contract section

exp_dev may: design and queue any of the 10 anchors above in any order consistent with the
prerequisite ordering; refine pre-reg bands based on current empirical state; substitute
equivalent implementations that test the same algebraic properties; decide on N configuration
(1024 vs 4096 vs 8192) based on PP-COMP-SMOKE results.

exp_dev must NOT: queue an anchor that requires a prerequisite that has not yet passed;
ship cloud GPU experiments for any of these anchors (all are CPU-viable); modify the
substrate encoding of existing facts without explicit orchestrator authorization.

---

## Autonomy declaration

exp_dev is autonomous for anchor design, queue assignment, pre-reg refinement, and
N-configuration decisions based on PP-COMP-SMOKE results. No further authorization is
required to queue PP-COMP-SMOKE. All remaining anchors are authorized contingent on
prerequisite PASS. Escalate to orchestrator only if PP-COMP-SMOKE returns HARD-FAIL
AND N=8192 also returns HARD-FAIL (structural problem requiring research re-analysis).
