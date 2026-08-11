# Pre-registration: three_tier_loop_independence_weighted_confirm_v1

## Context / motivation

`exp_three_tier_loop_genuine_cross_source_corroboration_v1` (commit 9d8926bce) HARD_FAILED for a
precise, non-mechanism reason: our current real sources (CSKG, CauseNet-precision, a ProPara-
derived process-physics KB; go.obo measured to contribute zero) give at most 3 distinct sources
per gap, but the retain-into-middle-tier confirmation gate
(`hdlab.prelim_tier.update_prelim_and_generalize`, `MIN_CONFIRM=4`, imported from
`hdlab.grounding_acquisition_loop`) is a raw TRACE-COUNT floor requiring 4 corroborations
regardless of source diversity. MEASURED@data/exp_three_tier_loop_genuine_cross_source_
corroboration_v1/metrics.json: 36/62 eligible gaps (58.1%) have >=2 real distinct sources; 8/62
have 3; max observed anywhere = 3. That cell's own positive control (R_reference, byte-identical
reproduction of the prior landed A_full arm) reproduced the prior result exactly
(n_foundation=40, cited=40), proving the mechanism sound and the zero a genuine real-source-
thinness finding, not a cell bug.

This cell tests the brain-foundational fix USER specified: make the confirmation gate
INDEPENDENCE/TRUST-WEIGHTED so N genuinely-independent-source corroborations count as stronger
evidence than N repeats of one (possibly correlated) source, per hippocampal multimodal-
convergence framing and the basic evidence-independence principle ("2-3 independent
confirmations is strong").

## Design: independence-weighted confirmation score

Defined in the CELL (not the reused organs, which stay generic and know nothing about "sources"):

```
SOURCE_INDEPENDENCE_CLASS = {
    "cskg": "independent", "causenet": "independent", "kb_role_schema": "independent",
    "reading_leg_synthetic": "correlated_with_cskg",   # negative-control-only tag
}
W_INDEPENDENT = 1.5       # weight for the FIRST trace from a genuinely-independent source
REPEAT_DECAY = 0.2        # geometric decay for the k-th (k=1,2,...) repeat of an ALREADY-seen tag
CORRELATED_WEIGHT = 0.15  # base weight for a correlated-tagged OR unmeasured/unknown source tag
                          # (deny-by-default: never assume independence)
INDEPENDENCE_MIN_CONFIRM = 2.5   # new threshold, replaces raw MIN_CONFIRM=4 for weighted arms
```

`score(traces) = sum over traces, sorted by (pass_idx, episode_id), of:
base_weight(first occurrence of this source tag) or base_weight * REPEAT_DECAY^k (k-th repeat)`,
where `base_weight = W_INDEPENDENT` iff `SOURCE_INDEPENDENCE_CLASS[tag] == "independent"`, else
`CORRELATED_WEIGHT` (covers both explicitly-correlated tags and any unrecognized tag).

**Closed-form guarantees (proven in self-test, not just hand-computed):**
- 2 independent sources: 2 * 1.5 = 3.0 >= 2.5 (crosses).
- 3 independent sources: 4.5 (crosses with more margin).
- 1 independent source, however repeated: asymptote = 1.5 / (1 - 0.2) = 1.875 < 2.5 for ANY N
  (never crosses via repetition of a single source).
- A correlated-tagged source, however repeated: asymptote = 0.15 / (1 - 0.2) = 0.1875 < 2.5 for
  ANY N (never crosses).
- A correlated pair (1 independent + 1 correlated): 1.5 + 0.15 = 1.65 < 2.5 (does not cross).
- Score is order-independent (deterministic sort by (pass_idx, episode_id) before scoring).

## SECOND FLOOR, HONESTLY DISCLOSED (found during authoring)

The retain gate is a CONJUNCTION: (1) the confirm/count check now made independence-weighted,
AND (2) a separate schema-coherence check (`schema_consistency_split_half`), which has its own
hardcoded `n>=4` structural floor (the module docstring discloses this floor was DELIBERATELY made
numerically coincident with the original raw MIN_CONFIRM=4: "keeps 'reached min_confirm' and
'schema-scoreable' coincident"). Lowering only the count gate to 2.5 without also lowering this
floor would make the fix a no-op (schema_score stays None forever at n=2-3).

Fix: `schema_consistency_split_half` gets an additive `min_half_size: int = 2` parameter (default
preserves `n<4 -> None` byte-for-byte); weighted arms pass `min_half_size=1` (permits scoring at
n=2..3). `schema_thresh` is LEFT AT THE CODEBASE DEFAULT (0.10, unchanged) -- not tuned down to
force a pass (that would be exactly the p-hacking SCHEMA-VET's calibration_check gate forbids).

Empirical spot-check during authoring (real text templates, D=256 context vectors):
- cos(CSKG, CauseNet) = 0.273 MEASURED (ad hoc script, not part of the cell) -- clears 0.10 easily.
- cos(CSKG, CauseNet, KB 3-way split) = 0.213 MEASURED -- clears 0.10.
- cos(CSKG, KB-role-schema ALONE, no CauseNet) = 0.039 MEASURED -- BELOW 0.10. Root cause: the KB
  source text never mentions the gap's `whole` (it only asserts a process-material role, a
  genuinely coarser-grained fact than the material-whole bridge CSKG asserts), so the two texts
  share few surface anchor words despite corroborating the same underlying gap.

This means a real possibility exists that the count gate will discriminate correctly (fixing the
ORIGINAL problem) while a large fraction of CSKG+KB-only pairs (no CauseNet) still fail to retain
end-to-end because of this SEPARATE, previously-uninvestigated floor. This is reported as a
distinct MIDDLE_BAND tier if it occurs, not folded into either PASS or FAIL.

## Organ changes (additive only, byte-for-byte backward compatible)

1. `hdlab/grounding_acquisition_loop.py::consolidation_pass` -- new kwonly params
   `trace_weight_fn: Optional[Callable[[List[Trace]], float]] = None` (default -> `float(len(traces))`,
   identical to prior behavior) and `schema_min_half_size: int = 2` (default identical to prior
   `n<4` floor).
2. `hdlab/grounding_acquisition_loop.py::schema_consistency_split_half` -- new param
   `min_half_size: int = 2` (default identical to prior `n<4` floor).
3. `hdlab/prelim_tier.py::update_prelim_and_generalize` -- new kwonly params `trace_weight_fn`
   and `schema_min_half_size`, same semantics/defaults as above.

Verified: both organs' own `self_test()` / `__main__` fixtures pass UNCHANGED after the edit
(MEASURED, run before authoring the new cell). The genuine-cross-source-corroboration cell's own
`--self-test` also passes unchanged (no regression).

## Arms

- **W_full**: full `ThreeTierLoop` wiring, real genuine encounter waves (CSKG always, CauseNet if
  measured, KB-role-schema if measured -- reused verbatim from the landed cell's
  `build_genuine_waves`), weighted gate (`min_confirm=2.5`, `trace_weight_fn=independence_
  weighted_trace_score`, `schema_min_half_size=1`) threaded through both the strict/foundation
  Library gate and the middle-tier retain gate via `ThreeTierLoop.consolidate`'s existing
  `gate_kwargs`/`middle_kwargs` passthrough (no `ThreeTierLoop` edit needed).
- **W_scramble**: same wiring + weighted gate, but eligibility recomputed under scrambled hop2
  bridge edges (reuses the EXACT scramble mechanism the parent cell's own `G_scramble` arm
  established) -- population collapses to a handful of items; must show near-zero retain.
- **R_reference**: byte-identical reproduction of the landed `A_full` arm (`run_arm`, imported
  verbatim from `exp_three_tier_loop_real_corpus_gap_stream_v1`), UNWEIGHTED default gate,
  `VISITS_PER_GAP=6` templated repeats -- proves the organ extensions are additive/non-destructive
  and this cell's plumbing is correct (core-preserved check).

## Additional checks (not full arms, cheap and deterministic)

- **closed_form_confirm_audit**: scores every real eligible gap's genuine-wave traces directly
  (no pipeline) via `independence_weighted_trace_score`, broken down by measured source-count
  bucket (1/2/3). The fastest, most direct answer to "does the weighted gate itself discriminate
  by source-count."
- **run_control_checks**: three synthetic can-fail probes via the REAL WIRED gate
  (`update_prelim_and_generalize` on a fresh `TierState`, not just the raw weight function):
  (A) 1 independent source repeated 10x -- must NOT retain; (B) a correlated-source pair -- must
  NOT retain; (C) a genuine 2-independent-source pair (differently-worded text) -- MUST retain.

## Pre-registered bands (before running)

- `confirm_gate_discriminates` = (0 of the real 1-source-eligible gaps cross the weighted score in
  the closed-form audit) AND (>=30% of the real 2+-source-eligible gaps cross it). This isolates
  "does the weighting scheme itself work" from the schema-coherence second floor.
- `controls_ok` = control_check_ok (A/B/C above) AND no_leak_ok (all arms) AND
  reference_reproduces_prior (R_reference n_foundation within abs 15 of cited 40) AND
  scramble_collapses (W_scramble eligible population <=1 OR its final n_middle == 0) AND
  positive_control_ok (Gate-D arm3 reproduction within 0.10 of cited 0.3802).
- `end_to_end_retain_ok` = W_full's real, end-to-end `n_middle` (checkpoints' final value) is
  >= 30% of the real 2+-source-eligible population.

**Verdict tree:**
- `controls_ok == False` -> `HARD_FAIL_controls_broken` (the weighted gate cannot be trusted).
- `confirm_gate_discriminates == False` -> `HARD_FAIL_weighting_scheme_does_not_discriminate` (the
  scheme itself needs redesign, not a threshold nudge).
- `confirm_gate_discriminates AND end_to_end_retain_ok` -> `HARD_PASS_independence_weighted_
  corroboration_crosses_gate` (the headline win: genuine cross-source corroboration now crosses
  the retain gate end-to-end on real data, controls hold, core preserved).
- `confirm_gate_discriminates AND NOT end_to_end_retain_ok` ->
  `MIDDLE_BAND_confirm_gate_fixed_schema_coherence_now_binding_floor` (the independence-weighting
  fix itself works and is proven by the closed-form audit + controls, but the SEPARATE
  schema-coherence floor, disclosed above, blocks a large fraction of end-to-end retains -- a
  genuine, newly-surfaced second-order finding, not a mechanism failure of this drill's own fix).

## Compute architecture

Class: (b) sequential-CPU with justification. Single deterministic pass per arm (3 arms, no
sweep), same regime as the landed parent cells (CSKG scan ~1.2M rows, CauseNet scan ~197K rows at
FULL only, both single streaming passes -- not matmul-heavy, not a batching candidate). Storage:
sharded (each gap its own item key via `pk_of_genuine`), no bundled storage. Wall time budget:
smoke ~20-40s, FULL ~90-150s (dominated by the CauseNet decompression scan, matching the parent
cell's own measured 50.4s FULL elapsed plus this cell's extra W_full/W_scramble/R_reference/
control-check overhead, all sub-second in-memory operations).

## Dispatch

RUN LOCAL, inline, foreground (per Autonomy Declaration: origin stale+irrelevant, no queue_add,
no remote, no push). Smoke first, then self-test gate re-confirmed, then FULL. LOCAL commit,
targeted `git add` (never `git add -A`).

## Schema-vet declarations

- `arms_differ_verified`: W_full vs R_reference asserted (digest inequality); W_full vs
  W_scramble asserted or exempted-by-construction if scrambled population collapses to the same
  size class.
- `final_metrics_atomicity`: tmp_replace (single-shot).
- `except SystemExit / KeyboardInterrupt` re-raised before `except Exception` (no BaseException).
- `crlb_n/a`: discrete weighted-evidence-score gate, not a Gaussian noise-floor metric;
  `discriminator_reachability=TRUE` proven closed-form (2 independent sources = 3.0 >= 2.5) in
  self-test, not just hand-computed.
- `cardinality_ok`: EXPECTED checkpoints = n_waves (2 smoke / 3 full) for W_full/W_scramble,
  VISITS_PER_GAP(6 full / 11 smoke) for R_reference.
- `calibration_check`: default_ok_for_this_regime (novelty_thresh imported verbatim from the
  landed cell's own calibration; schema_thresh left at codebase default, NOT adaptively tuned).
- `progress_logging`: print_flush_true (all `print(..., flush=True)`); N/A strictly since
  declared `--timeout` (300s) is below the 1800s (30min) MANDATORY threshold, but included anyway
  for audit parity with the parent cells' own convention.
