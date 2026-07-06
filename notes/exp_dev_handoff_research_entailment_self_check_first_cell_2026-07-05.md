# exp_dev hand-off — research: entailment/self-check first cell (half-range comparator)

**STATUS 2026-07-06: COMPARATOR MERGED -- do NOT auto-dispatch as a separate cell.** The half-range comparator was folded into the already-in-flight compare cell (exp_dev af6b5bf, fired from the math-envelope drill); the director routed this handoff's three additions (native-signtest HARD_FAIL control, decode-then-compare baseline honesty gate, a>=threshold target) into that cell via SendMessage, and the research agent itself reconciled to the same half-range design (not a duplicate MRC cell). The Tier-2 real-cert-ledger self-check loop (anchor #3 below) REMAINS a genuine DEFERRED follow-up to build AFTER the comparator lands. Auto-refill scan: skip the comparator, keep the Tier-2 pointer.

**Filed:** 2026-07-05 by research (sub-agent context; main thread/orchestrator will dispatch
the exp_dev wrapper).

**Trigger:** `notes/research_entailment_self_check_first_cell_2026-07-05.md` — Director
scoping request for the smallest substrate-native entailment/self-check demonstration,
following directly from the landed exact-equality primitive
(`exp_math_rns_add_chain_v1`, commit `a4492b56c`, FULL, HARD_PASS,
`data/exp_math_rns_add_chain_v1/metrics.json`) and the SMOKE-HARD_PASS cert-ledger
self-query cell (`exp_cert_ledger_self_query_v1`, commit `61f84d107`,
`data/exp_cert_ledger_self_query_v1_smoke/metrics.json`). **Reconciled with a same-session
sibling hand-off**: `notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md`
independently scoped the SAME comparison gap and got there first with a cheaper mechanism
(half-range sign-detection, anchor `exp_math_rns_compare_halfrange_v1`, P_deflated=0.45) —
this hand-off adopts that anchor/mechanism rather than proposing a competing one, and adds
two refinements the sibling note's own research didn't have (see below). If a hand-off for
`exp_math_rns_compare_halfrange_v1` from the sibling note has already been picked up or
built by the time this is read, treat this file as SUPERSEDED — do not build a duplicate
cell; instead check whether the two control-arm additions below have been folded into
whatever landed, and file a small follow-up only if not.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent — verified this session).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS +
POINTERS + mechanism/bands only. exp_dev designs ALL of: N, moduli, seed count, exact
threshold bands, queue choice, anchor name, ETA, smoke profile, FULL profile.

---

## What the research found (one paragraph)

Two of three primitives self-checking needs are already free: subtraction is a same-
mechanism extension of the landed phase-linear-add homomorphism (conjugate-phasor bind,
near-zero new code); closed-set/categorical membership is already proven by
`exp_cert_ledger_self_query_v1` Task B (`HAS_STATUS` exact-match + tier-family compare).
The one genuine gap is a magnitude-comparison/ordering primitive — confirmed absent from
the VSA/HDC literature by TWO independent lit-scans (neither the modular nor the
continuous-FPE variant has ever been used as a discrete greater-than operator) and
confirmed classically hard in RNS for a precise, well-documented reason (no residue channel
carries order information). The cheapest correct fix (per the sibling note): **half-range
sign-detection** — subtract via the already-free conjugate-phasor bind, CRT-decode the
difference (already-proven reconstruction), threshold against `M/2`. This note's OWN
research separately found that the substrate's one prior comparator attempt
(`exp_comparator_resonator_primitive_smoke_v1`, FULL, HARD_FAIL — native vector-space
sign-test over CONTINUOUS scalar FPE added no lift over naive decode, comp_acc=0.8556 vs
raw_acc=0.8944) is a real, respected negative the sibling note never found — folded in below
as a recommended control-arm addition, not a competing mechanism.

---

## Anchor candidates (rank-ordered)

### 1. `exp_math_rns_compare_halfrange_v1` (PRIMARY — the cell this hand-off is for)

- **Anchor pointer:** `notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md`
  Q2/Q4 (original mechanism spec + bands) AND
  `notes/research_entailment_self_check_first_cell_2026-07-05.md` "THE CELL SPEC" section
  (adopts the sibling's mechanism verbatim, adds two control arms + the Tier-2 cert-ledger
  pointer). Read BOTH before authoring — they are complementary, not duplicates.
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
  remaining piece, cheap, and now doubly-scoped (two independent research threads converged
  on the same mechanism-gap diagnosis).
- **Construction summary** (exp_dev owns exact params): reuse `exp_math_rns_add_chain_v1`'s
  phase-linear residue codebook/regimes verbatim. Compute `d = bind(enc(a), conj(enc(b)))`
  (free conjugate-phasor subtraction). CRT-decode `d` (already-proven reconstruction).
  Threshold decoded `d` against `M/2` for the sign of `a-b`. Four arms:
  `halfrange_compare` [MECHANISM]; `dynamic_range_violation_control` [CONTROL, from the
  sibling note — deliberately generate `|a-b| >= M/2` trials; must be explicitly
  flagged/reported, not silently mis-signed — this is a named HARD-FAIL trigger, not
  optional]; `native_vector_signtest_control` [CONTROL, this hand-off's addition — literal
  repeat of the closed `exp_comparator_resonator_primitive_smoke_v1` sign-test design, now on
  the EXACT discrete representation instead of the continuous FPE it originally used; informs
  whether the historical HARD_FAIL was representation-specific or mechanism-general];
  `scrambled_residue_control` [CONTROL, expected collapse].
- **Bands (from the sibling note, sign-accuracy framing):** HARD-PASS sign-accuracy >= 0.95
  within the valid dynamic range (`|a-b| < M/2`) AND the range-violation control is honestly
  flagged/reported. HARD-FAIL sign-accuracy < 0.70 within valid range, OR the range-violation
  control silently mis-signs in > 50% of trials without being reported.

### 2. Same-session extension: subtraction arm on `exp_math_rns_add_chain_v1`

- **Anchor pointer:** `exp_math_rns_subtract_conjugate_v1` per the sibling note's Q4 table
  (rank 1, P_deflated=0.85, ~20-30 lines) — this hand-off defers naming/scoping detail to
  that note; not re-specified here to avoid a third redundant description.
- **Substrate-product reading:** near-zero-cost, essentially a free corollary; a literal
  prerequisite sub-step of anchor #1 (the difference `d` both cells need). Recommend
  building as a SHARED helper both the subtract cell and the compare cell import, per the
  sibling note's own recommendation, rather than duplicating the conjugate-bind logic.
- **Tier hint:** trivial, same wall-time class as the landed cell.
- **Why now:** essentially free; bundle opportunistically alongside #1 since #1 needs the
  same conjugate-subtract step anyway.

### 3. (Deferred, NOT this cell) Tier 2 wiring onto real cert_ledger metric/threshold pairs

- **Anchor pointer:** `notes/research_entailment_self_check_first_cell_2026-07-05.md`, Q1
  "Tier 2" + Q2 staging recommendation (this note's unique contribution — the sibling note
  does not cover this).
- **Substrate-product reading:** once anchor #1 lands, wire the validated comparator onto a
  real, on-disk corpus of `(measured_metric, HARD-PASS threshold, recorded verdict)` triples
  pulled from `preregs/*.md` + `data/*/metrics.json` (hundreds exist), retrieved via
  `exp_cert_ledger_self_query_v1`'s proven KG-retrieval mechanism — oracle is the trivial
  `metric >= threshold` Python check. This is the FULL "substrate checks its own
  certification claims" loop the Director's original question asked about.
- **Tier hint:** local/CPU, retrieval-scale (like `exp_cert_ledger_self_query_v1`).
- **Why now / why deferred:** explicitly sequenced AFTER anchor #1 passes in isolation
  (mirrors how all three sibling cells staged synthetic-first, real-data-second). Not ready
  to dispatch yet — do not build until #1 has a verdict.

---

## Context pointers (pointers, not summaries)

- `notes/research_math_arithmetic_basis_next_primitives_2026-07-05.md` — the PRIMARY source
  for `exp_math_rns_compare_halfrange_v1`'s mechanism, full bands, and the subtraction/
  multiplication build-order ranking. Read this FIRST.
- `notes/research_entailment_self_check_first_cell_2026-07-05.md` — this hand-off's other
  source; the reconciliation note at the top explains how it relates to the file above; the
  "THE CELL SPEC" section has the two added control arms + Tier-2 pointer.
- `notes/research_self_reasoning_capability_gap_2026-07-05.md` — designed
  `exp_cert_ledger_self_query_v1`; named the "numeric threshold logic" gap both math notes
  above are closing.
- `notes/research_math_capability_translation_first_cell_2026-07-05.md` — designed
  `exp_math_rns_add_chain_v1`; the landed primitive both this cell and its sibling build on.
- `preregs/math_rns_add_chain_v1.md` — the codebook/regime construction to reuse verbatim.
- `preregs/cert_ledger_self_query_v1_2026-07-05.md` — the KGStore retrieval + exact-match
  pattern for Tier 2 wiring (deferred anchor #3).
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` — the closed HARD_FAIL the
  `native_vector_signtest_control` arm responds to; read before authoring to avoid
  re-deriving the same failed sign-test design from scratch.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE
  smoke (bands already drafted across both research notes; exp_dev finalizes exact numbers).
- Self-test per [[feedback-formula-selftests]] — include a homomorphism self-test for the
  conjugate/subtraction helper (`bind(enc(a), conj(enc(a))) == enc(0)`, per the sibling note's
  own additive-inverse identity check) before any arm measurement.
- SMOKE local-only (USER-lock); FULL routes to `remote_cpu_queue` via Orchestrator (push
  harness-denied to exp_dev), matching both sibling cells' dispatch pattern.
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code per [[feedback-ship-name-collision]].
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: anchor name, exact N/moduli/regimes (default: reuse the landed add
cell's small/mid/large regimes, verifying `M > 2*max_operand_range` for the half-range
precondition), seed count, exact HARD-PASS/HARD-FAIL numeric bands, queue routing, ETA,
smoke/FULL profiles. exp_dev may drop the `native_vector_signtest_control` arm as optional
scope-trim if it judges the historical negative sufficiently well-established already — this
hand-off recommends including it (cheap, directly informative) but does not mandate it. If
exp_dev has already picked up the sibling note's version of this cell independently, treat
the two control-arm additions here as a lightweight follow-up patch, not a reason to re-author
from scratch.

---

## Filed by

research (sub-agent context), 2026-07-05, following the landed `exp_math_rns_add_chain_v1`
FULL HARD_PASS, the SMOKE HARD_PASS `exp_cert_ledger_self_query_v1`, and reconciled with the
same-session sibling scoping note on math primitives. Hand-off ready for exp_dev pickup
(auto-discovered on next emergency-refill scan of `notes/exp_dev_handoff_*.md` sorted by
mtime, or explicit dispatch).
