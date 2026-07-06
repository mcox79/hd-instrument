# exp_dev hand-off — research: entailment/self-check first cell (MRC comparator)

**Filed:** 2026-07-05 by research (sub-agent context; main thread/orchestrator will dispatch
the exp_dev wrapper).

**Trigger:** `notes/research_entailment_self_check_first_cell_2026-07-05.md` — Director
scoping request for the smallest substrate-native entailment/self-check demonstration,
following directly from the landed exact-equality primitive
(`exp_math_rns_add_chain_v1`, commit `a4492b56c`, FULL, HARD_PASS,
`data/exp_math_rns_add_chain_v1/metrics.json`) and the SMOKE-HARD_PASS cert-ledger
self-query cell (`exp_cert_ledger_self_query_v1`, commit `61f84d107`,
`data/exp_cert_ledger_self_query_v1_smoke/metrics.json`).

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent — verified this session).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS +
POINTERS + mechanism/bands only. exp_dev designs ALL of: N, moduli, seed count, exact
threshold bands, queue choice, anchor name, ETA, smoke profile, FULL profile.

---

## What the research note found (one paragraph)

Two of three primitives self-checking needs are already free: subtraction is a same-
mechanism extension of the landed phase-linear-add homomorphism (conjugate-phasor bind,
near-zero new code); closed-set/categorical membership is already proven by
`exp_cert_ledger_self_query_v1` Task B (`HAS_STATUS` exact-match + tier-family compare).
The one genuine gap is a magnitude-comparison/ordering primitive — confirmed absent from
the VSA/HDC literature (neither the modular nor the continuous-FPE variant has ever been
used as a discrete greater-than operator) and confirmed classically hard in RNS for a
precise, well-documented reason (no residue channel carries order information). The
substrate's one prior attempt at a comparator
(`exp_comparator_resonator_primitive_smoke_v1`, FULL, HARD_FAIL — native vector-space
sign-test over CONTINUOUS scalar FPE added no lift over naive decode, comp_acc=0.8556 vs
raw_acc=0.8944) is a real, respected negative that should NOT be re-run; the correctly-
scoped next attempt is a mechanistically different, classical technique — Mixed-Radix
Conversion (MRC) digit-serial comparison over the EXACT discrete residue representation,
reusing the substrate's already-CHAIN_GRADE exact-match + iterative-hop-with-early-exit
control flow for the compare step itself.

---

## Anchor candidates (rank-ordered)

### 1. `exp_math_rns_compare_mrc_v1` (PRIMARY — the cell this hand-off is for)

- **Anchor pointer:** `notes/research_entailment_self_check_first_cell_2026-07-05.md`,
  section "THE CELL SPEC" (full bands/arms/controls table there).
- **Substrate-product reading:** closes the one open primitive (comparison/ordering) needed
  for genuine numeric threshold entailment-checking over the substrate's own certification
  claims (e.g., does a recorded `spearman=0.886 >= 0.80 -> chain_grade` verdict actually
  follow from the cited number) — composes with the already-landed exact-equality primitive
  and the already-SMOKE-HARD_PASS cert-ledger retrieval cell into the full "substrate checks
  its own claims" loop the Director asked about.
- **Tier hint:** LOCAL-CPU-feasible (numpy-scale; same order of magnitude as the landed add
  cell's ~2-15s wall time). No GPU needed.
- **Why now:** the exact-equality primitive it depends on JUST landed FULL HARD_PASS this
  session; the cert-ledger retrieval half-loop is already SMOKE HARD_PASS; this is the one
  remaining piece, cheap, and the design is fully staged (arms/controls/bands pre-registered
  in the research note, including an honest "adds nothing over decode-then-compare" HARD-FAIL
  path that is itself a legitimate, reportable finding).
- **Construction summary** (exp_dev owns exact params): reuse `exp_math_rns_add_chain_v1`'s
  phase-linear residue codebook/regimes verbatim; add a Mixed-Radix-Conversion digit-
  derivation step (new, ~150-250 lines, direct port of the classical Szabo & Tanaka 1967
  algorithm or a parallel/table-lookup variant); compare MRC digits most-significant-first
  with early exit, using the substrate's existing exact-match primitive. Four arms:
  `mrc_digit_compare` [MECHANISM], `decode_then_compare_baseline` [CONTROL, expected
  strong/near-1.0 since it reuses the proven exact CRT decode], `native_vector_signtest_
  control` [CONTROL, expected to reproduce the closed HARD_FAIL — same failed mechanism,
  re-run on the exact representation as an honest recheck not a blind retry],
  `scrambled_digit_control` [CONTROL, expected collapse].

### 2. Same-session extension: subtraction arm on `exp_math_rns_add_chain_v1`

- **Anchor pointer:** research note, Q3 table row "Subtraction."
- **Substrate-product reading:** near-zero-cost (conjugate-phasor bind; same proven
  homomorphism). Not a new cell — a cheap addendum/revision to the already-landed add cell
  if/when exp_dev revisits it, or folds into the MRC comparator cell's own codebook module
  since both need the same conjugate-inverse helper.
- **Tier hint:** trivial, same wall-time class as the landed cell.
- **Why now:** essentially free; bundle opportunistically, not urgent on its own.

### 3. (Deferred, NOT this cell) Tier 2 wiring onto real cert_ledger metric/threshold pairs

- **Anchor pointer:** research note, Q1 "Tier 2" + Q2 staging recommendation.
- **Substrate-product reading:** once anchor #1 lands, wire the validated comparator onto a
  real, on-disk corpus of `(measured_metric, HARD-PASS threshold, recorded verdict)` triples
  pulled from `preregs/*.md` + `data/*/metrics.json` (hundreds exist) — oracle is the trivial
  `metric >= threshold` Python check. This is the FULL "substrate checks its own
  certification claims" loop.
- **Tier hint:** local/CPU, retrieval-scale (like `exp_cert_ledger_self_query_v1`).
- **Why now / why deferred:** explicitly sequenced AFTER anchor #1 passes in isolation
  (mirrors how both sibling cells staged synthetic-first, real-data-second). Not ready to
  dispatch yet — do not build until #1 has a verdict.

---

## Context pointers (pointers, not summaries)

- `notes/research_entailment_self_check_first_cell_2026-07-05.md` — this hand-off's source;
  full bands/arms/controls table, brain-grounding, external-lit citations.
- `notes/research_self_reasoning_capability_gap_2026-07-05.md` — designed
  `exp_cert_ledger_self_query_v1`; the sibling note this hand-off's cell was deferred from.
- `notes/research_math_capability_translation_first_cell_2026-07-05.md` — designed
  `exp_math_rns_add_chain_v1`; the sibling note whose landed primitive this hand-off builds
  on.
- `preregs/math_rns_add_chain_v1.md` — the codebook/regime construction to reuse verbatim.
- `preregs/cert_ledger_self_query_v1_2026-07-05.md` — the KGStore retrieval + exact-match
  pattern for Tier 2 wiring (deferred anchor #3).
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` — the closed HARD_FAIL
  this cell's controls respond to; read before authoring to avoid re-deriving the same
  failed sign-test design from scratch.
- `hdlab/kg_traversal.py`, `hdlab/multi_hop.py` — iterative-hop-with-early-exit control-flow
  pattern the MRC digit-compare step is structurally analogous to.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE
  smoke (bands already drafted in the research note; exp_dev finalizes exact numbers).
- Self-test per [[feedback-formula-selftests]] — include a homomorphism self-test for the
  conjugate/subtraction helper if bundled, and an MRC round-trip self-test
  (`mrc_decode(mrc_encode(x)) == x` for known integers) before any arm measurement.
- SMOKE local-only (USER-lock); FULL routes to `remote_cpu_queue` via Orchestrator (push
  harness-denied to exp_dev), matching both sibling cells' dispatch pattern.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code per [[feedback-ship-name-collision]].
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: anchor name (may rename from `exp_math_rns_compare_mrc_v1` if a
better name emerges), exact N/moduli/regimes (default: reuse the landed add cell's
small/mid/large regimes), MRC algorithm variant (sequential vs. parallel/table-lookup), seed
count, exact HARD-PASS/HARD-FAIL numeric bands, queue routing, ETA, smoke/FULL profiles. If
exp_dev judges the `decode_then_compare_baseline` control makes the `mrc_digit_compare`
mechanism arm redundant before even running it (i.e. decides decode-then-compare-in-plain-
scalar-space is obviously sufficient and the MRC increment isn't worth building), that is a
legitimate exp_dev call — report it as a design decision, not a failure to dispatch.

---

## Filed by

research (sub-agent context), 2026-07-05, following the landed `exp_math_rns_add_chain_v1`
FULL HARD_PASS and the SMOKE HARD_PASS `exp_cert_ledger_self_query_v1`. Hand-off ready for
exp_dev pickup (auto-discovered on next emergency-refill scan of
`notes/exp_dev_handoff_*.md` sorted by mtime, or explicit dispatch).
