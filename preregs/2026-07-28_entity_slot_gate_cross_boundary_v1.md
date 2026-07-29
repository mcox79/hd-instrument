# Pre-reg: entity_slot_gate_cross_boundary_v1 (2026-07-28)

- Anchor: `entity_slot_gate_cross_boundary_v1`
- Cell: `experiments/exp_entity_slot_gate_cross_boundary_v1.py`
- New module: `hdlab/entity_slot_gate.py` (`EntitySlotGate`, `fit_entity_slot_gate`)
- Extended in place: `experiments/diag_order_critical_comprehension_calib_v1.py` (new
  `gen_cross_boundary` construction)
- Source: notes/comprehension_situation_model_frontier_scoping.md, "Design A" (RECOMMENDED FIRST)
  + "First can-fail experiment"

## Prior-work check (substrate-KB, USER-locked 2026-07-01)

`bash tools/substrate_query.sh "entity slot scaffold learned write gate frozen encoder situation
model comprehension"` -- top hits cosine 0.41 / 0.34 are the frontier-scoping note itself + a
sibling research-drill note on Kintsch situation-model theory (the SAME background reading that
motivated this cell, not a prior IMPLEMENTED cell). Third hit (cosine 0.31) is the generic WordNet
`comprehension` node. **Verdict: genuinely novel implementation; no rediscovery.** Separately,
`bash tools/substrate_query.sh "gated hebbian associative memory sequence matrix write gate
learned addressing capacity crosstalk"` -- top hit cosine 0.30 (`kg_store_write_rule_decorrelated
_ceiling_v1` prereg, generic associative-memory-capacity literature, not this construction) --
confirms no prior cell tested a gated/addressed Hebbian write-capacity question in this form.

## Question

Does a small TRAINED head (content-addressed entity slots + a learned write-gate, reading the
FROZEN RELOBJ_v3 encoder's own clause-level hidden states, writing via
`hdlab.sequence_memory.SequenceMatrix.bind_pair`) beat a matched PLAIN readout (whole-sentence
MEAN_POOL over the SAME frozen encoder) on a NEW leak-proof CROSS_BOUNDARY entity-consistency
construction? ONE variable = mechanism/readout only; encoder/data/seeds/construction fixed.

## Construction: CROSS_BOUNDARY (`gen_cross_boundary`, extended in place)

Two entities (e1, e2) sharing ONE state-axis (sA, sB) from `STATE_PAIRS`. Clause 1 = two short
sentences, each stating one entity's state; clause 2 (the boundary) = one claim, "it became sA",
using recency-antecedent "it" (construction-template ground truth, not a resolver the mechanism
sees). ORDER_1 (e1 first=sA, e2 last=sB): "it"->e2(sB); "became sA" = valid sB->sA flip ->
label=1 CONSISTENT. ORDER_2 (clause-1 sentences swapped): "it"->e1(sA, unchanged); "became sA"
while already sA = null/invalid -> label=0 VIOLATED. ORDER_1/ORDER_2 share an IDENTICAL WORD
MULTISET (verified by an in-function self-test over index-aligned pool pairs, pre-sampling) --
not solvable by bag-of-words.

### Calibration iteration (the honest record; four wordings tried, v4 landed)

| version | wording | result |
|---|---|---|
| v1 | `adv1 the e1 was sA and the e2 was sB . adv2 it became sA .` (900/200) | FAILED -- best margin 0.1175 (BGE MEAN_POOL), < 0.15 |
| v2 | `... it was still sB .` (direct-equality framing) | WORSE -- margin 0.02-0.07 |
| v3 | `... the second one / the one mentioned last was still sB .` (ordinal, no pronoun) | WORSE -- margin 0.02-0.07 |
| v4 (landed) | v1 wording, clause 1 SPLIT into two sentences, N doubled to 1800/300 | **PASSED** -- BGE_SMALL MEAN_POOL coherent=0.7517 scrambled=0.5217 margin=+0.2300 (z=8.28); LAST/CLS_TOKEN margin=+0.2150 |

MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json:
calibration_results.BGE_SMALL.CROSS_BOUNDARY.per_readout.MEAN_POOL. Reproduced independently by
the cell's own `run_calibration_gate` at smoke time (byte-different code path, same numbers:
MiniLM MEAN_POOL margin=0.1383, BGE_SMALL MEAN_POOL margin=0.2600) --
MEASURED@d:/AI/hd-instrument/data/exp_entity_slot_gate_cross_boundary_v1_smoke/metrics.json:
calibration.per_model.BGE_SMALL.MEAN_POOL.margin. **Calibration gate: PASS** (>=1 known reader
clears MARGIN_THRESH=0.15 / COHERENT_FLOOR=0.65).

## Mechanism (design A, `hdlab/entity_slot_gate.py`)

N_SLOTS content-addressable slots, each backed by a `SequenceMatrix`. `addr_net` (content-address
over clause-1 rep) + `gate_net` (write-strength scalar) are the TRAINED small head. WRITE is a
no_grad, gated Hebbian `bind_pair` over TRAIN-COHERENT items only (local plasticity, not backprop-
through-memory). READ is differentiable: `surprise_features` returns `[1-cosine(addr-weighted
slot-prediction, actual clause-2 rep), gate opinion, address entropy]`, fed to the SAME
`fit_binary_probe`/`score_readout_arm` machinery used by every other readout arm in this instrument.
MANDATORY control: `SLOT_GATE_RANDOM_GATE` runs the identical structure with `addr_net`/`gate_net`
at random init (zero optimizer steps).

## Bands (envelope-fail-bands, set BEFORE the mechanism-fires investigation below)

- **HARD_PASS_GAIN = 0.05** (`SLOT_GATE_TRAINED.margin - MEAN_POOL.margin`, both seeds).
- **MIDDLE_BAND_GAIN = 0.02**.
- **RANDOM_GATE_EPS = 0.02**: `HARD_FAIL_STRUCTURE_ALONE` if `random_gate_gain >= gain - 0.02`
  on ANY unit (structure alone, not learning -- MANDATORY per the frontier note; this session's
  design-C work already found random-init beating trained once on entity-state).
- **HARD_PASS**: gain >= 0.05 on BOTH seeds AND no structure-alone breach.
- **MIDDLE_BAND**: exactly 1/2 seeds clears, or gain in [0.02, 0.05).
- **HARD_FAIL**: 0/2 seeds clear 0.02, OR structure-alone breach.
- **CALIBRATION_GATE_FAIL**: no known reader clears the construction at the dispatched regime --
  own-encoder scoring is skipped entirely (uninterpretable against a broken instrument).
- Real baseline (motivating context, not the literal comparison point): RELOBJ_v3 MEAN_POOL on
  the OLDER ENTITY_STATE construction was +0.283 seed7 / +0.130 seed13 (non-replicated positive).
  On THIS construction, RELOBJ_v3 MEAN_POOL (seed_7) already measures margin=+0.2083 --
  MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json:
  own_encoder_results.RELOBJ_v3.CROSS_BOUNDARY.per_readout.MEAN_POOL.margin -- this is the actual
  "matched plain readout" comparison point the mechanism must beat by >=0.05.

### HP_SCOPE

```yaml
HP_SCOPE:
  seed_7, seed_13: [HARD_PASS, MIDDLE_BAND, HARD_FAIL, HARD_FAIL_STRUCTURE_ALONE, CALIBRATION_GATE_FAIL]
  random_init_encoder_slot_gate arm (both units): []   # informational only, does not gate verdict
```

## Smoke-stage discriminator-fires investigation (Option A, full-N smoke; DISCRIMINATOR-MUST-SURVIVE-SCALE)

Smoke ran the CROSS_BOUNDARY construction at FULL scale (train=1800, eval_per_label=300,
byte-identical to FULL_CFG), one seed (RELOBJ_v3 seed_7), reduced gate-training epochs (8 vs 15).

**First smoke (n_slots=4, the initial design default): FAILED to fire.**
MEASURED@d:/AI/hd-instrument/data/exp_entity_slot_gate_cross_boundary_v1_smoke/metrics.json (n_slots=4
run, superseded on disk by the n_slots=16 re-run below): `meanpool.margin=+0.2100`,
`slot_gate_trained.margin=+0.0050` (near-chance), `slot_gate_random_gate.margin=+0.0083` (also
near-chance) -> `gain=-0.205`. Verdict at the time: `HARD_FAIL_STRUCTURE_ALONE`.

**Root-cause investigation (ad-hoc, this session, not a formal cell -- reported here per the
HYPOTHESIZED/MEASURED discipline as MEASURED, off-disk-reproducible via the commands in this
section's git history):**
1. **Hebbian-capacity hypothesis**: `SequenceMatrix` is a bundled (single global matrix per slot)
   Hebbian associative store; classical bundle capacity ~0.15*N ~ 77 pairs at N=512. ~900
   coherent TRAIN items spread over only 4 slots is 3-10x over capacity per slot (crosstalk).
   **Test**: swept n_slots in {4, 16, 64} at the smoke regime, epochs=8, same seed. Result:
   margin 0.0050 (n=4) -> 0.0717 (n=16) -> 0.0667 (n=64, plateau/slight decline). Confirms the
   capacity-crosstalk diagnosis DIRECTIONALLY (more slots helps) but the ceiling (~0.07) remains
   far below the MEAN_POOL baseline (0.21) -- gain at n_slots=16 = 0.0717-0.21 = **-0.138**, still
   a clear HARD_FAIL, not a capacity-tuning fix.
2. **Readout-bottleneck hypothesis**: `surprise_features` compresses everything to 3 scalars,
   whereas MEAN_POOL gives the probe a full 512-dim vector. **Test A (naive rich concat)**:
   concatenated `[pred_mix (512d, UNNORMALIZED raw Hebbian-accumulated magnitude); h1; h2; the 3
   scalars]` (1539-dim) -> margin=+0.0100 (chance). Diagnosed as a SCALE-MISMATCH optimization
   artifact (`pred_mix` is an unnormalized sum-of-outer-products, large/unbounded magnitude,
   swamping the fixed-hyperparameter linear-probe fit against the unit-normalized h1/h2 blocks) --
   NOT evidence the raw content is uninformative. **Test B (matched-scale combo)**: concatenated
   `[h1 (unit-norm); h2 (unit-norm); the 3 BOUNDED gate scalars]` (1027-dim), properly scaled ->
   margin=+0.2250 (trained gate), margin=+0.2383 (RANDOM-init gate, same combo). **The gate's own
   3 scalars add ZERO incremental value over plain clause-split concatenation once the scale
   mismatch is fixed; the random-init control MATCHES (in fact marginally exceeds) the trained
   gate on the properly-scaled combo feature -- structure alone.**
3. **Side finding (not part of this cell's gated verdict, informational)**: plain
   `CLAUSE_SPLIT_CONCAT` (h1;h2, NO gate/memory/addressing at all -- just feeding the probe
   clause-1 and clause-2 pooled reps SEPARATELY instead of one blended whole-sentence MEAN_POOL)
   measures margin=+0.2400, modestly ABOVE the whole-sentence MEAN_POOL baseline (+0.21, i.e.
   +0.03 gain -- below this cell's own HARD_PASS_GAIN=0.05 bar, so not itself a HARD_PASS, but a
   directionally interesting "clause-separation-alone" observation for any follow-up design).

**Conclusion: mechanism does NOT fire, confirmed via three independent, cross-checking tests (raw
3-scalar readout at varying capacity; naive rich-concat with a diagnosed scale artifact; a
properly-scaled combo feature isolating the gate's marginal contribution). This is not a bug or a
single unlucky draw -- it is a reproducible property of this specific mechanism (Hebbian-bundled
gated slot memory, reduced to a low-dimensional surprise/gate/entropy summary) on this task.**

**Re-ran smoke at the corrected n_slots=16 (the best config found) for the authoritative on-disk
record**: MEASURED@d:/AI/hd-instrument/data/exp_entity_slot_gate_cross_boundary_v1_smoke/metrics.json
(current on-disk state): `meanpool.margin=+0.21` (recomputed fresh, matches), `slot_gate_trained.
margin` implies `gain=-0.1383`, verdict=`HARD_FAIL`. calibration_pass=true (reproduced).

## Decision: DO NOT DISPATCH FULL

Per the DISCRIMINATOR-MUST-SURVIVE-SCALE discipline ("Reject the full dispatch if discriminator
preview shows saturation... Burn the smoke time, save the full time. Honest abort beats fake
verdict") and the mechanism-fires gate ("If smoke doesn't fire the discriminator, STOP and re-spec
the regime. Don't dispatch full hoping it'll be different") -- this cell is NOT shipped to
`remote_cpu_queue`. The smoke-stage investigation (three independent tests, capacity-tuned,
scale-corrected) gives high confidence this is a real property of the mechanism, not noise a
2nd-seed FULL run would resolve differently.

## Recommendation for Director (per the frontier note's own contingency)

Design A, AS LITERALLY SPECIFIED (Hebbian-bundled gated slot memory, reduced to a
surprise/gate/entropy summary readout), is REFUTED on this construction. Two live paths:
1. **Escalate to Design B** (event-schema forward-prediction self-teacher) per the frontier note's
   own "ESCALATION path if A/C's structure-only supply is insufficient" -- this cell's evidence IS
   that structure-only supply (slot count, addressing scheme, write primitive) without changing
   the TRAINING OBJECTIVE was insufficient, which is exactly Design B's premise.
2. **Cheaper interim step, if Director wants one more structure-only iteration before escalating**:
   the side finding (CLAUSE_SPLIT_CONCAT alone, no gate, +0.03 over MEAN_POOL) suggests
   clause-separation itself has a small amount of unexploited value; a differentiable (not
   Hebbian-bundled) slot/attention mechanism trained end-to-end (rather than the local-plasticity
   two-stage design mandated here) might extract more of it -- but note this would REQUIRE
   backprop-through-memory (the design constraint this cell specifically avoided per the
   "Hebbian writes are local" brain-grounding rationale), so it is a genuine mechanism-class
   change, not a parameter tweak, and should be scoped as a fresh pre-reg if pursued.

## Wire target / capability gate

`hdlab/entity_slot_gate.py` is a genuinely-built, tested, reusable primitive (content-addressed
Hebbian-slot memory with a learned gate) even though THIS application is a HARD_FAIL. Recommend
**SHELVE** (not delete) with revival criteria: "a task where >=900 write-events per slot is not
required (lower N, or many more slots feasible), or a properly end-to-end-differentiable variant
if Director authorizes moving off the local-Hebbian-write constraint." Per role separation
(capability_registry.jsonl writes are owned by the skunkworks/triage role in this repo's
established pattern -- see recent `triaged_2026-07-28` rows), exp_dev is NOT writing this row
directly; flagging for Director to route.

## Compute architecture

- Class (b) sequential-CPU with justification: CPU-only, no `torch.cuda` reference; per-unit
  compute is small matmuls (d=512) over <=1800 items plus a Python-loop Hebbian write (cheap,
  bind_pair is O(d^2) per call). Explicitly designed to run parallel to the GPU breadth run.
- Storage strategy: no_storage / no_composition (single-item classification, not chained retrieval).

## SCHEMA-VET checklist

```yaml
cell_chunked: true
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: "passed_all_4_patterns"
final_metrics_atomicity: "per_iter_paths"
arms_differ_verified: true
crlb_n_a: "accuracy-margin discriminator over a binary linear probe, not a capacity/noise regime"
baseline_in_band: true    # MEAN_POOL coherent_acc 0.63-0.75 across calibration models, well inside (0.05,0.95)
calibration_check: "adaptive_with_discriminator_gate"   # re-runs calibration at dispatch time, gates on it
cardinality_ok: true
deterministic_seeding: true   # fixed int SEED throughout; no hash()-derived RNG
real_code_path_exercised: [gen_cross_boundary, load_frozen_encoder, TinyTransformer,
  compute_hidden_cache, EntitySlotGate, fit_entity_slot_gate, SequenceMatrix.bind_pair, fit_binary_probe]
guard_baseline_validated: []   # no control-vs-baseline break-guard in this cell
```

## Status: NOT DISPATCHED (self-test PASS, smoke PASS-as-in-ran-cleanly but discriminator
DID NOT FIRE -- HARD_FAIL at smoke per the investigation above). No remote queue_add issued.
