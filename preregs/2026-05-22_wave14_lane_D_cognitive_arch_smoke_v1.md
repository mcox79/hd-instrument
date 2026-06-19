# Pre-reg: Wave 14 Lane D Cognitive Architecture Integration Smoke v1

**Filed:** 2026-05-22
**Bet:** Lane D (cognitive architecture, TAM $30-50B+) per cap_map v79 Phase 3
**Strategy slot:** Phase 3 priority — composes already-validated Lane D primitives

## Question

Can the validated Lane D primitives (Bet S Pattern Completion, Bet T Hypothesis Tracking, Bet U Working Memory + decay, Bet X Skill Composition) all co-exist on a single bipolar BSC substrate without destructive interference?

This is a substrate-product integration demo, not a new mechanism test. Each primitive has already been shipped individually with PASS/PARTIAL verdicts. The question is whether they compose.

## Hypothesis

H_compose: At N=4096, with shared codebooks but role-distinct atoms (entity / relation / hypothesis / position / skill), all 4 primitives clear their individual acceptance thresholds (>=0.70) on the same single substrate.

H_null: Primitives interfere. >=3 of 4 fall below 0.70 → LANE_D_INCOMPATIBLE.

## Pre-declared verdicts

- `LANE_D_COMPOSE` — all 4 metrics >= 0.70 on the shared substrate.
- `LANE_D_PARTIAL` — 1-2 primitives fall below 0.70 (which primitive matters).
- `LANE_D_INCOMPATIBLE` — >=3 of 4 fall below 0.70 (substrate cannot host all four roles simultaneously).
- `LANE_D_INCONCLUSIVE` — metric collection error.

## Metrics

- `S_acc`: Bet S triple recall on M_S (50 facts, 20 probes) — pattern completion.
- `T_acc`: Bet T per-hypothesis decode on M_T (3 hypotheses, 30 facts) — hypothesis tracking.
- `U_recent`: Bet U EMA decay accumulator recall on last-5 facts (40-fact stream, decay=0.95).
- `X_acc`: Bet X position-indexed skill program decode (10 programs of length 4, alphabet 5).

## Method

Single shared codebook design — all 4 primitives draw from the same BSC atom factories:
- 100 entity atoms
- 20 relation atoms
- 3 hypothesis atoms
- 8 position atoms
- 5 skill atoms

Each primitive constructs its own bundled memory (M_S, M_T, B for U, prog for X) using sign-quantized triple/role binding. No primitive shares its bundle with another — only the atoms.

## Acceptance thresholds

- Threshold 0.70 per primitive matches the lower bound used in each primitive's individual pre-reg.
- Random-baseline guard: oracle.assert_baseline_high("any_primitive_works", max(metrics), 0.30) — at minimum one primitive must work above chance.

## Config

- N=1024 (smoke), 4096 (full)
- seeds=[17] (smoke), [17, 23, 31] (full)

## Pre-declared interpretation

- `COMPOSE`: substrate hosts cognitive-architecture demo. Next: build orchestration layer (working memory feeds pattern completer feeds hypothesis tracker feeds skill executor).
- `PARTIAL`: identifies which primitive degrades under shared-substrate load. Build remediation for that one primitive (more orthogonal codebook? higher N? role isolation?).
- `INCOMPATIBLE`: substrate cannot host Lane D as a single-bundle system. Pivot to multi-bundle architecture (separate memory per primitive).

## Not in scope

- Cross-primitive routing (substrate-to-substrate flow). This is the substrate-only test.
- Comparing to LLM cognitive architectures. We are not benchmarking against transformers here.
- Capacity scaling. Fixed M for each primitive; capacity sweep is a follow-on if COMPOSE.
