# Skunkworks tier ruling -- pointer-chain v2 HARD_FAIL + META_M6 + smoke-floor META candidate (deferred)

Date: 2026-06-25
Auditor: skunkworks (audit-only; A5-gated atomization)
Method: independent recompute off `metrics.json` per_seed (NOT verdict_msg framing); smoke metrics
independently verified; existing META atom + Store state cross-checked off `data/substrate_index/`.

## Headline (read first)

1. **Pointer-chain hybrid v2 BASELINE_RAIL_FIXED -> HARD_FAIL ratified.** Verify off per-seed reproduces every
   cited number exactly. Mechanism HURTS by 22pp vs naive HRR baseline; depth-retention 0.0824 (FAIL >= 0.80);
   hybrid arm identical to pointer-only (zero compositional lift). Cert-owner tier: HARD_FAIL / honest_negative
   / delta=0 / counts as proven NEGATIVE bound. Atomized as `math::T3/EXP_substrate_multihop_pointer_chain_
   hybrid_v2_baseline_rail_fixed_HARD_FAIL`.

2. **META_M6 atomized as proposed.** Three observed instances in two weeks (consolidation v1 + consolidation
   v3 + pointer-chain v2) of NAIVE-baseline bands copied across cells without re-derivation from current-cell
   regime parameters. Composes with M2 (rail-must-match-referent-config) + M5 (chain-construction-match) to
   form the 3-rule "rail-discipline derivation-provenance-regime-match" set. Operational fix included.

3. **META smoke-floor candidate DEFERRED (NOT atomized).** Off-data verify caught that pointer-chain v2 smoke
   ran at THREE-DIMENSION reduced regime (N=2048 vs 8192 + pointer_n_chains=50 vs 200 + n_seeds=1 vs 3),
   making the smoke-vs-full sign-flip regime-confounded. The Director's "n_chains-floor" framing is single-
   cell evidence AND the single cell is multi-confound. Per Fix #28 default under-claim: documented as
   candidate in the exp_dev pickup section below; do NOT atomize until a second cell with a SINGLE-DIMENSION
   smoke regime mismatch confirms the rule.

4. **Two cert-trail integrity gaps flagged** (FOR DIRECTOR ROUTING; out of this spawn's scope):
   - consolidation_v3 HARD_FAIL: ruling note `notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-
     06-25.md` exists; NO atom in `data/substrate_index/math/atoms.jsonl`; NO row in `data/substrate_index/
     meta/cert_ledger.jsonl`. The Director's prompt this cycle assumed it was atomized; it is not. **The
     pointer-chain v2 HARD_FAIL atom in this spawn references it as a companion** and explicitly cites the
     gap in its `cites` field. Director should route a back-fill atomization (probably to me) next cycle.
   - META_M4 + META_M5: cert_ledger rows landed (by `skunkworks_tier_ruling_cell3_cell4_consolidation_2026-
     06-25` atomized_by tag) but NO atoms.jsonl entries (only M1, M2, M3 made it to atoms.jsonl; M4 + M5
     are LEDGER-OF-RECORD only). The atom-write step was incomplete in whatever tool wrote those ledger
     rows. **META_M6 atomized in this spawn references both M4 + M5** in its `composes_with` and flags M5
     as "LEDGER-ROW only, atom-write gap" in its `discipline_set_components` metadata.

## Artifact 1 -- pointer-chain hybrid v2 HARD_FAIL ratified

### Verify-off-data recompute (matches metrics.json verdict_msg exactly)

Per-seed (seeds [7, 17, 23], independently read from `per_seed[i].arm_<X>.top1`):

| arm | seed 7 | seed 17 | seed 23 | mean | pstdev | cv |
|---|---|---|---|---|---|---|
| arm_baseline_hrr_2hop | 0.605 | 0.670 | 0.675 | **0.6500** | 0.0319 | 0.0491 |
| arm_pointer_chain_2hop | 0.485 | 0.375 | 0.415 | **0.4250** | 0.0455 | **0.1070** |
| arm_pointer_chain_5hop | 0.145 | 0.110 | 0.110 | 0.1217 | 0.0165 | 0.1356 |
| arm_pointer_chain_10hop | 0.040 | 0.035 | 0.030 | 0.0350 | 0.0041 | 0.1166 |
| arm_pointer_hrr_hybrid | 0.485 | 0.375 | 0.415 | **0.4250** | 0.0455 | 0.1070 |

Pre-reg bands evaluated:
- HP_pointer_2hop >= 0.95: **FAIL** (0.425 vs 0.95; margin -0.525)
- HP_hybrid >= 0.85: **FAIL** (0.425 vs 0.85; margin -0.425)
- HP_cv <= 0.05: **FAIL** (0.1070 vs 0.05; 2.1x over cap)
- HP_depth_retention (top1_10hop / top1_2hop) >= 0.80: **FAIL** (0.0824 vs 0.80; margin -0.72)
- HF_top1 <= 0.75: **FIRED** (pointer 2hop 0.425 below floor; mechanism HURTS)
- baseline sanity [0.62, 0.68] majority of seeds: **1/3 BREACH** (seed 7 baseline 0.605 below 0.62)

Per-step accuracy (chain decay seed 7, depth 10):
`[0.69, 0.485, 0.31, 0.205, 0.145, 0.1, 0.07, 0.065, 0.04, 0.04]` -- per-hop survival ~0.70, compounding
to 0.70^10 ~ 0.028, matches observed 0.035. Geometric chain-cleanup attenuation; not an implementation bug.

Zero-LLM-calls-at-inference: verified per per_seed[i]._llm_forward_calls_at_inference = 0 across all 3 seeds
AND at cell-level. Substrate-only-decode gate PASSES.

### Smoke-vs-full divergence -- THREE-DIMENSION regime confound caught off-data

Director-flagged this as a Fix #28 violation: smoke POINTER=0.98 (+52% over baseline) flipped to
full POINTER=0.425 (-22% UNDER baseline). The framing attributed this to "chain-count-sensitive mechanism".

Off-data verify on `data/exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_smoke/metrics.json`:

| dim | smoke | full | ratio |
|---|---|---|---|
| N | 2048 | 8192 | 4x reduction |
| pointer_n_chains | 50 | 200 | 4x reduction |
| n_seeds | 1 | 3 | 3x reduction |
| verdict | HARD_PASS_BREAK_CEILING | HARD_FAIL | sign-flip |
| POINTER_2HOP top1 | 0.98 | 0.425 | -0.555 abs |

**The sign-flip is regime-confounded across three dimensions** (capacity-N + density-pointer-chains +
seed-pool). Cannot attribute to a single dimension from this single cell. The FULL-SCALE ruling is the
load-bearing measurement; the smoke result is a SUSPECT 1.000 artifact of toy-regime by-construction lift
(Q-discipline: SUSPECT 1.000 results).

### Tier ruling: HARD_FAIL / honest_negative / delta=0 (proven NEGATIVE bound)

**Reasoning:**
- Pre-reg bands were CONCRETE and PRE-SPECIFIED at config_version (not retrofitted).
- All HP bands failed with concrete margin (0.45-0.72 BPC magnitude); no near-miss.
- Sanity-breach is downward (seed 7 baseline 0.605 BELOW band) -- so baseline mean 0.650 is at midpoint
  of expected; even widening the band wouldn't put POINTER 0.425 in striking distance.
- HYBRID arm identical to pointer_2hop arm (per-seed exactly equal) shows the hybrid pathway adds zero
  discriminative information. This is mechanism-add-no-value, not instrument-bug-MM.
- Per-step accuracy is geometric decay consistent with FUNDAMENTAL chain-cleanup attenuation; the
  mechanism cleanly MEASURES its own failure.

**Sub-class: pre_reg_miss_proven_bound.** Counts as proven NEGATIVE result (per Skunkworks disposition
framework -- HARD_FAIL at pre-reg bar = proven bound).

**Barrier 1 double-negative context (preserved in atom description):** Together with consolidation v3
HARD_FAIL same day, the two substrate-native multi-hop closure mechanisms (compound-predicate
consolidation + pointer-chain hybrid) are both REFUTED at random-bipolar isotropic production regime
(V_C=200 V_P=2 N=8192 K_SET=20). This is the load-bearing negative for L2 encoder pivot per
`notes/research_barrier1_double_negative_substrate_product_definition_2026-06-25.md`. The substrate-product
definition is unchanged: 2-hop chain-grade memory + composition + retrieval + audit; multi-hop reasoning
requires external scaffold (PFC analog) OR semantic-consolidation under feature-share cortical analog
(different cell entirely).

### Concerns considered and rejected

**Concern 1: sanity-breach makes ruling unreliable.** No. The breach DIRECTION is downward (baseline weaker
than expected at seed 7); even with a widened band, POINTER 0.425 doesn't approach the 0.65 baseline
midpoint. The rail miss does not mask a direction-correct mechanism signal beneath.

**Concern 2: smoke-vs-full sign-flip suggests rescue at right regime.** No. Smoke is at 0.25x N + 0.25x
pointer_n_chains + 0.33x seed-pool; the smoke 0.98 is suspect-1.000 by-construction territory (likely
storing-the-answer at toy density), not evidence the mechanism scales. The cell would need to RE-DISPATCH
at e.g. N=4096 + pointer_n_chains=100 + n_seeds=3 to disentangle which dimension is load-bearing -- a
SEPARATE cell, not a rescue of this one.

**Concern 3: should this be MEASURED_MECHANISM not HARD_FAIL?** No. MM is for clean characterizations
without a pre-reg bar OR for by-construction-saturation by-construction wins. This cell has a CLEAR
pre-reg HP bar (>=0.95) and missed it by 0.525; it has a CLEAR HF floor (<=0.75) and the mechanism IS
BELOW the floor (0.425). Honest_negative / pre_reg_miss_proven_bound is the correct subclass.

## Artifact 2 -- META_M6 atomized

### Rule (final phrasing per atom)

> Pre-reg NAIVE-baseline sanity-band MUST be DERIVED from the cell's CURRENT regime parameters (V_C, V_P,
> n_chains, chain-class structure, K_SET, N), NOT copied from a prior cell's pre-reg without re-derivation.
> Provenance is NOT derivation.

### Three observed instances (validates rule)

1. **consolidation_v3 HELDOUT_FIX (2026-06-25):** NAIVE=0.850 vs pre-reg band [0.62, 0.68] copied from v2
   single-pair regime; v3 changed to V_P=6 multi-class with separate W. Research 2x drill decoded sanity-
   breach as rail mis-spec, not methodology bug. Consolidation HARD_FAIL on heldout remains load-bearing.
2. **consolidation_v1 (2026-06-24):** NAIVE=0.847 vs prior beta-sweep BASELINE_HARD=0.65 (V_P=10 uniform
   vs V_P=2 fixed-pair regime). Sanity rail expected [0.40, 0.75] BLOWN PAST at 0.847 but REPRODUCIBILITY_
   DIVERGENCE not flagged.
3. **pointer-chain hybrid v2 (2026-06-25, this spawn):** Baseline mean 0.650 in nominal band BUT seed 7
   = 0.605 (1/3 seeds breach downward) even with "rail fix" using beta-sweep's EXACT V_P=2 fixed-pair
   regime. Regime variance leaks through at n_seeds=3; n_seeds>=10 OR widened band needed.

### Three-rule rail-discipline set (composes with M2 + M5 + M6)

- **META_M2** (atomized 2026-06-25, in atoms.jsonl): rail tolerance must match referent config exactly OR
  widen by predicted capacity-scaling drift.
- **META_M5** (LEDGER-ROW only, atom-write gap flagged): cross-cell baseline comparisons require chain-
  construction match, not just V/N match.
- **META_M6** (atomized this spawn): NAIVE-baseline must be DERIVED from current-cell regime parameters,
  NOT copied. Provenance is not derivation.

The three rules together form the **rail-discipline derivation-provenance-regime-match set:**
- (a) Rails must have explicit derivation provenance (where the band came from).
- (b) Rails must match the regime they will be evaluated in (V_C, V_P, n_chains, chain-class structure,
  K_SET, N, encoder, device).
- (c) Rails must be DERIVED from the current cell's parameters at pre-reg time, not copied.

### Operational fix (built into the rule)

Every cell pre-reg with a NAIVE arm MUST include either:
- (a) A smoke-run NAIVE arm at n_seeds >= 5 at CURRENT regime, with the measured NAIVE value used to SET
  the sanity band as `smoke-mean +/- 0.03`; OR
- (b) A closed-form derivation of expected NAIVE from regime parameters, with the band derived as
  `expected +/- max(0.03, expected * 0.05)`.

Closed-form rough approximation for K=2 random-bipolar isotropic:
`NAIVE_2hop ~ erf(N / (4 * n_chains * V_P_effective))` (underestimates at low density; over-estimates
when single-pair saturates a single codebook code; empirical smoke takes precedence when they disagree
by > 0.05).

### Tier ruling: meta_rule / delta=0 / CERT-neutral

Validated by three observed instances same week. NOT yet validated by a cell that DESIGNED its rail per
the rule prospectively and succeeded -- that cert-ladder DEFINITIVE upgrade is a future cell-author cycle
pickup. For now, the rule is M-tier (operational discipline; useful at pre-reg time and at landed-VET time).

## Artifact 3 -- META smoke-floor discriminator: DEFERRED (NOT atomized)

### Director's proposed rule (verbatim)

> Any mechanism whose lift depends on n_chains MUST smoke at n_chains >= 100. Smoke at toy n_chains
> (10-20) can flip sign vs full and pass smoke gate while failing full HARD.

### Why DEFERRED (Fix #28 default under-claim)

Off-data verify CAUGHT a confound in the single supporting cell (pointer-chain v2): the smoke run differs
from full along THREE dimensions, not just n_chains. The smoke-vs-full sign-flip cannot be cleanly
attributed to n_chains-sensitivity from this single cell.

**The cleaner rule candidate** (broader; covers the actual evidence):

> Smoke regime MUST match the full-run regime along EVERY capacity-sensitive dimension (N, density-
> parameters like n_chains, n_seeds at minimum). A smoke run that reduces multiple dimensions
> simultaneously is regime-confounded -- its sign cannot be used as a smoke gate for the full mechanism.

This broader rule has the same single-cell support and is more honest about what the evidence shows.
**Still single-cell.** Per Fix #28 + Q-discipline, single-cell evidence for a methodology rule is too
thin to atomize.

### For exp_dev pickup (recommended)

Add to `.claude/agents/exp_dev.md` RECENT-DISCIPLINE section as candidate (NOT a META atom yet):

> CANDIDATE smoke-vs-full regime-match: when authoring smoke + full versions of a cell, the smoke MUST
> match the full along EVERY capacity-sensitive dimension (N, density-parameters, n_seeds). Reducing
> multiple dimensions simultaneously creates a regime-confounded smoke whose sign cannot be used as a
> gate for the full mechanism. Pointer-chain v2 (2026-06-25) showed this: smoke at N=2048 + pointer_n_
> chains=50 + n_seeds=1 gave POINTER=0.98 (+52% over baseline); full at N=8192 + pointer_n_chains=200
> + n_seeds=3 gave POINTER=0.425 (-22% UNDER baseline). PENDING second-cell confirmation before
> atomization.

If a second cell within a few cycles shows the same regime-confounded smoke pattern, this should be
atomized as META_M7 (or whichever rule_id is next free in the cert-discipline series).

## Integrity gaps flagged (out of this spawn's scope; for Director routing)

### Gap 1: consolidation_v3 HARD_FAIL atom never landed

- Ruling note exists: `notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-06-25.md`
- Atom search: `data/substrate_index/math/atoms.jsonl` has NO entry for consolidation_v3 / multihop_
  consolidation_v3 / heldout_fix.
- Ledger search: `data/substrate_index/meta/cert_ledger.jsonl` has NO row referencing the v3 cell.
- The Director's prompt this cycle assumed it was atomized (referenced as companion HARD_FAIL); my pointer-
  chain v2 atom in this spawn references it as a companion but the referent isn't in the Store.

**Recommended Director routing:** queue a Skunkworks atomize task next cycle to land the consolidation_v3
HARD_FAIL atom with cross-reference to the pointer-chain v2 HARD_FAIL atom landed in this spawn. Use the
same `pre_reg_miss_proven_bound` cert_class. Or, if the ruling note's "atomization YES" claim was already
the intent and the write just failed silently, investigate the failure mode (whatever tool drafted the
ruling didn't ship the atomize step).

### Gap 2: META_M4 + META_M5 are ledger-only

- `data/substrate_index/meta/cert_ledger.jsonl` has rows for both M4 + M5 (atomized_by `skunkworks_tier_
  ruling_cell3_cell4_consolidation_2026-06-25`).
- `data/substrate_index/meta/atoms.jsonl` has M1, M2, M3 but NOT M4, M5.
- The `cell3_cell4_consolidation` ruling note proposed M4 + M5 as atomizations, but no `tools/skunkworks_
  atomize_*cell3*` script exists; the ledger rows seem to have been written directly without the
  corresponding atom-write step.

**Recommended Director routing:** queue a Skunkworks atomize task to back-fill the M4 + M5 atoms with
text matching the ledger row verdicts. Use the same convention as M1/M2/M3 (provenance_quality=`META_RULE_
CERT_NEUTRAL`, kind=`METHODOLOGY_RULE`, corpus=`META`, tier=`T3`). This is also a chance to investigate
the ledger-without-atom write path -- if direct ledger-row writes are happening outside the A5-gated
atomize tool flow, that's a discipline gap worth catching at the next phase 3 architecture review.

## Cert-N impact (per ledger-delta-sum headline convention)

Two atoms landed in this spawn; BOTH are CERT-neutral (delta=0):
- Pointer-chain v2 HARD_FAIL: honest_negative / delta=0 / counts as proven NEGATIVE bound (does NOT add
  to CERT N; the headline CERT N tracks chain-grade PASS rulings).
- META_M6: meta_rule / delta=0.

**Headline CERT N: unchanged at 591** (Director-prompt baseline; cert_ledger.jsonl sum-delta accounting).

Atom count delta: +2 (math: +1, meta: +1). Total atoms ~177341 (from pre 177339).

## Referent pointers (absolute paths)

- Metrics (full): `D:/AI/hd-instrument/data/exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed/metrics.json`
- Metrics (smoke): `D:/AI/hd-instrument/data/exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed_smoke/metrics.json`
- Atomize tool: `D:/AI/hd-instrument/tools/skunkworks_atomize_pointer_chain_v2_plus_META_M6_2026-06-25.py`
- Cell 2 v5 prior atomize (pattern reference): `D:/AI/hd-instrument/tools/skunkworks_atomize_cell_2_v5_DEFINITIVE_2026-06-25.py`
- Cell 3 cell 4 prior atomize (M1/M2/M3 reference): `D:/AI/hd-instrument/tools/skunkworks_atomize_tier_ruling_3cells_post_drill_2026-06-25.py`
- Consolidation v3 ruling note (INTEGRITY GAP): `D:/AI/hd-instrument/notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-06-25.md`
- Research 2x drill (load-bearing for META_M6 evidence): `D:/AI/hd-instrument/notes/research_consolidation_v3_HARD_FAIL_2x_drill_2026-06-25.md`
- Director strategic synthesis (Barrier 1 context): `D:/AI/hd-instrument/notes/research_barrier1_double_negative_substrate_product_definition_2026-06-25.md`
- Cert ledger writer helper: `D:/AI/hd-instrument/tools/cert_ledger_writer.py`

## Disciplines honored this spawn

- Verify-OFF-DATA (not verdict_msg): every cited metric recomputed from per_seed via .venv Python.
- Verify-the-referent: smoke metrics independently read; existing META atoms cross-checked off Store;
  consolidation v3 + M4/M5 atomization state checked off both atoms.jsonl + cert_ledger.jsonl.
- Q-discipline (SUSPECT 1.000): pointer-chain v2 smoke 0.98 flagged as by-construction-suspect.
- Fix #28 default under-claim: META smoke-floor candidate DEFERRED to second-cell confirmation.
- A5-gated atomize: PRE snapshot (math/meta counts, CERT_N, axiom=206, cap_pres 6/6) + atomic add_atom
  + verify-load round-trip + POST snapshot.
- Idempotency: atomize tool aborts if either atom_qid already present.
- Path-scoped commit (caller responsibility): atoms.jsonl + cert_ledger.jsonl + ruling note + atomize tool
  explicitly staged; never `git add -A`/`.`.
- Foreground execution (Fix #20); no subprocess pipes.
- ASCII only.

-- Skunkworks, 2026-06-25 (cert-owner / auditor; spawn-and-die teammate)
