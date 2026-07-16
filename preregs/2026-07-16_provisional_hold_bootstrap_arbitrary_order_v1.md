# Pre-reg: provisional_hold_bootstrap_arbitrary_order_v1

**Date:** 2026-07-16. **Author:** exp_dev. **Cell:** `experiments/exp_provisional_hold_bootstrap_arbitrary_order_v1.py`.
**Compute:** local numpy, no queue/GPU/atoms/push. Sequential-CPU justified: wall < 15s; the cell IS the
bootstrapping/ingest mechanism being validated (bit-exact numpy reference). Runs to completion in foreground.

## Question

The curriculum cell (`exp_curriculum_order_ingest_schema_fit_v1`, HARD_PASS) showed ARBITRARY ingestion order craters
foundation quality (curriculum ~1.0 -> arbitrary ~0.039) under a single-pass STRICT schema-fit gate. But REAL data
arrives in ARBITRARY order -- a live edit/claim stream cannot be pre-sorted. So test the REALISTIC fix:
PROVISIONAL-HOLD / bootstrapping -- admit a premature (scaffold-less) fact to a HOLD buffer instead of REJECTING it,
and re-evaluate it once its prerequisites arrive. Carey/bootstrapping: a single-pass strict gate is definitionally
incompatible with bootstrapping (it drops the scaffold-less fact that must be retried). How much of the curriculum
advantage does provisional-hold RECOVER under arbitrary order, and at what COST?

## Construction (arena imported VERBATIM from the curriculum cell)

- Same forest, same prerequisite DAG, same noisy per-seed displacements, same fixed schema-fit gate `tau = 0.50`.
  The reject POLICY is the only thing that differs -> fairness is airtight. `_try_place` uses the identical admit
  criterion (sf >= tau and >=1 ref present) and identical degree-invariant mean placement; self-test asserts BIT-EXACT
  parity of the strict arms against `cur.run_regime`.
- Provisional-hold ingest: Phase 1 = arrival in the given order, a fact failing the tau gate goes to a hold buffer
  (NOT dropped). Phase 2 = drain: repeatedly sweep the hold buffer, admitting any held fact whose prerequisites are
  now present (SAME tau gate), until a full sweep admits nothing (fixpoint). Drain is swept in INSERTION (arrival)
  order, NOT id-sorted (forest ids are BFS/topological -> id-sort would leak curriculum order and understate cost),
  with SYNCHRONOUS within-pass updates (admit against the admitted-set frozen at pass start) -> `re_queue_passes` is
  an order-independent, CONSERVATIVE (upper-bound) cost = the dependency-cascade depth.

## Arms (hierarchical regime, mean over 8 seeds)

- (C) `cur_strict` = curriculum order + strict gate -> the ~1.0 CEILING reference.
- (A) `arb_strict` = arbitrary order + strict gate -> the ~0.04 FLOOR (baseline; premature facts permanently dropped).
- (B) `arb_hold`   = arbitrary order + PROVISIONAL-HOLD (bootstrapping).

## Metrics

- `foundation_quality` per arm (held-out sibling relational retrieval; same eval as the curriculum cell).
- `recovery_fraction = (hold_q - arb_strict_q) / (cur_strict_q - arb_strict_q)` = fraction of the curriculum
  advantage recovered under arbitrary order.
- `premature_recovered_fraction = (phase1_hold - final_hold) / phase1_hold` = fraction of strict-rejected facts the
  drain eventually admits.
- `re_queue_passes` (drain sweeps to fixpoint = the COST) and `retry_attempts` (total held-fact re-evaluations =
  wasted-work COST).
- `placement_error` per arm (recovery must be genuine placement, not garbage inflating quality).

## Null guard + graceful degradation

- NULL (flat regime): every fact grounds on always-present innate anchors -> nothing is ever premature -> hold buffer
  EMPTY, 0 drain passes, arbitrary_strict already == curriculum. Confirms the benefit is prerequisite-structure-driven.
- GRACEFUL DEGRADATION (separate sub-run): inject ORPHAN facts whose prerequisites NEVER arrive (refs to phantom ids
  never ingested). Buffer must stay BOUNDED (only shrinks during drain -> max size = phase-1 hold, `buffer_trace`
  monotone non-increasing), drain must TERMINATE (fixpoint when only orphans remain), orphans end in a bounded
  give-up set (`final_hold >= n_orphans`), and NO orphan is ever admitted.

## PRE-REG BANDS

- **HARD-PASS** = `recovery_fraction >= 0.70` AND `re_queue_passes_max <= depth + 2` (bounded) AND null guard holds
  (flat hold buffer empty, 0 passes, flat quality spread `<= 0.05`) AND graceful degradation holds (orphans never
  admitted, buffer bounded+monotone, drain terminates, orphans in give-up set) AND anti-rig holds
  (`cur_strict_q - arb_strict_q >= 0.25`, i.e., arbitrary_strict still craters). => arbitrary-order real data is
  handleable by bootstrapping; no pre-sort needed.
- **HARD-FAIL** = `recovery_fraction <= 0.30` OR `re_queue_passes` unbounded (grows with N not depth). => genuinely
  need curriculum order, which live streams cannot provide -- a real limitation. Also HARD_FAIL if graceful
  degradation is violated (orphan buffer grows unbounded / admits garbage).
- **MIDDLE** = otherwise (partial recovery / residual order-dependence).

## Discriminator-fires gate (smoke)

- `arb_strict` must crater: `cur_strict_q - arb_strict_q >= 0.15` at smoke (else nothing to recover -> saturation-
  vacuous -> BLOCK).
- Hold must strictly help: `hold_q >= arb_strict_q + 0.10`.
- ARMS-MUST-DIFFER: hold admit-set != arbitrary_strict admit-set (hold admits strictly more).
- Passes bounded: `re_queue_passes_max <= depth + 2`.
- Placement genuine: hold placement_error < 5x curriculum placement_error.
- Null holds (flat hold buffer empty, 0 passes, spread <= 0.05); graceful (orphans never admit, buffer monotone,
  terminates).

## Anti-rig / feasibility

- `tau` fixed at 0.50, IDENTICAL to strict arms (bootstrapping only changes retry-vs-drop, not the admit criterion).
- Strict arms asserted BIT-EXACT vs `cur.run_regime` (arena parity -> no divergent re-implementation).
- Cost-scale sweep (depth {2..5} x branching {2..4}) reports `re_queue_passes` scales with DEPTH (structural cascade
  length), NOT with N/branching -> cost bounded for large streams; branching only inflates buffer/work linearly.
- Determinism: numpy `default_rng` fixed int seeds; order-perm rng seed-derived to MATCH the curriculum cell; NO
  `hash()`-derived seeds; `sorted()` for all set ops. Atomic tmp+os.replace metrics write (META_RULE_AH).
  `except Exception` only, SystemExit re-raised.

## Honest scope note

FULL recovery (recovery_fraction ~ 1.0) is PARTLY BY-CONSTRUCTION: in this synthetic arena every non-orphan fact's
full scaffold eventually arrives, so re-queuing it after the cascade necessarily restores coverage AND (because the
drain admits on the settled full scaffold) placement. The load-bearing, LESS-by-construction scientific content is
(1) the QUANTIFIED COST -- `re_queue_passes ~ depth` (constant in N; cost bounded for large arbitrary streams),
`retry_attempts`/`buffer` ~ linear in N (bounded work), buffer STRICTLY bounded (only shrinks); (2) GRACEFUL
DEGRADATION under permanent orphans (bounded give-up set, no unbounded growth, drain terminates); (3) the NULL guard
proving the benefit is prerequisite-structure-specific. The value is the how-much / at-what-cost / residual-failure
quantification, not a yes/no.
