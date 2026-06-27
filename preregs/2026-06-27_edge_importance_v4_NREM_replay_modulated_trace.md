# Prereg: edge_importance_v4_NREM_replay_modulated_trace

Date: 2026-06-27
Anchor: edge_importance_v4_NREM_replay_modulated_trace
Cell: experiments/exp_edge_importance_v4_NREM_replay_modulated_trace.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Wave: Path A per USER 2026-06-27 (v3 MIDDLE_BAND extension; replay-modulated trace)
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; 2026-06-26)
  - hdlab/ultrametric_clustering.py (chain-grade; 2026-06-26) [v3 lineage; coreness OFF in v4 base mechanism]
  - hdlab/ NREM replay primitive pattern (chain-grade; substrate_continual_NREM_replay_v1)
  - experiments/exp_substrate_continual_NREM_replay_v1.py (replay-cycle pattern referent)

## Motivation

v3 (retrieval-trace x ultrametric-coreness) landed MIDDLE_BAND:
COMPOSITION collapsed to TRACE at top-K because ULTRA contribution was
+0.008 above trace-only on sel_unretr; TRACE alone gave
sel_minus_rand=+0.083 (below the +0.15 PASS floor; well above the 0.0
noise floor).

Brain literature (STC / BTSP / engram reconsolidation) is explicit:
importance accumulates via MULTI-EVENT reconsolidation across
sharp-wave-ripple (SWR) replay during NREM sleep, not via single-pass
retrieval count. The 2024-2025 engram-reconsolidation literature
underlines that REPLAY during sleep is the importance-strengthening
mechanism; the retrieval count is the SEED for what gets replayed, not
the importance itself.

Substrate has a chain-grade NREM-replay primitive already (cell
substrate_continual_NREM_replay_v1, HARD_PASS continual-write horizon
extension via periodic re-write). v4 ports the multi-event replay
discipline into edge-importance scoring.

## v4 mechanism (replay-modulated trace; brain-grounded)

```
importance_score[atom] = base_retrieval_trace[atom]
                        + lambda_replay * replay_consolidation_count[atom]
```

- `base_retrieval_trace[atom]` = per-atom counter of cleanup-argmax hits
  during composite-query operation (same as v3's TRACE arm; seeds the
  replay).
- `replay_consolidation_count[atom]` = per-atom counter of NREM-replay
  reactivations (SWR analog: how many times this atom was selected for
  replay during interleaved retrieve+replay cycles).
- `lambda_replay` in {0.5, 1.0, 2.0} (REPLAY weight higher than v3's
  centrality lambda because replay IS importance-strengthening, not just
  a structural modulator).
- Apply NREM-style replay BETWEEN trace-collection passes (3 cycles of
  trace+replay; brain analog: wake-replay-wake alternation across short
  sleep epochs).

## Replay schedule (brain-grounded; load-bearing for v4)

- `N_TRACE_PASSES = 3` (wake-sleep cycles). Each pass:
  1. Composite-query the substrate; record cleanup-argmax winners into
     `base_retrieval_trace` (continues incrementing across passes).
  2. Sample top-K-traced atoms by current trace; perform NREM-replay
     write-back (Hebbian outer-product re-write) on these atoms;
     increment `replay_consolidation_count` for each replayed atom.
- `N_COMPOSITE_QUERIES_PER_PASS` chosen so total queries equal v3
  budget (N_COMPOSITE_QUERIES_FULL=3000 split into 3 passes of 1000).
- Top-K-traced selection: top `REPLAY_FRAC * N_USE = 0.20 * 240 ~ 48`
  atoms by current trace; replay each once per pass.
- Replay re-writes the (key, value) pair via outer-product onto W
  (matches substrate_continual_NREM_replay_v1.write_atom_to_W pattern).

## ARMS (4 mandatory; pre-reg discipline)

- ARM_BASELINE_RANDOM (importance = uniform random; sanity rail)
- ARM_TRACE_ONLY (single-pass trace; reproduces v3 TRACE arm; sel_unretr
  baseline ~ +0.083)
- ARM_TRACE_PLUS_REPLAY (the mechanism; sweeps lambda_replay in {0.5,
  1.0, 2.0})
- ARM_REPLAY_ONLY (importance = replay_consolidation_count alone;
  control: does replay alone produce the signal? Discriminates whether
  trace seeds the replay vs replay independently selects)

ALL arms share the SAME workload, the SAME retrieved/unretrieved
partition; differ only in importance-scoring + which counters they
consume.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS)

HARD_PASS_REPLAY_EXTENDS_TRACE:
  - best (TRACE_PLUS_REPLAY) sel_unretr asymmetry >= 0.15
    (rec_UNRETR_random - rec_UNRETR_trace_plus_replay >= 0.15;
    ORIGINAL bar Path A targets; replay extension should clear what
    trace-only didn't)
  - AND cor(importance, |W|) < 0.30 (USER fairness gate)
  - AND mechanism fires (n_downscaled > 0 AND replay_events > 0)
  - AND COMP over TRACE_ONLY: best sel_unretr >= trace_sel_unretr + 0.05
    (replay must add value beyond trace-only; if not, replay is silent)
  - AND COMP over REPLAY_ONLY: best sel_unretr >= replay_only_sel_unretr
    + 0.05 (composition must add value over replay alone; if not, trace
    is silent and the mechanism is really just replay)

HARD_FAIL:
  - All four arms within 0.05 of each other on rec_RETRIEVED (saturation;
    regime too easy)
  - OR cor(importance, |W|) >= 0.30 (fairness regression)
  - OR n_downscaled == 0 OR replay_events == 0 (inert; either pruning or
    replay didn't actually run)
  - OR composition arm UNDERPERFORMS trace_only by > 0.02 on sel_unretr
    (composition actively hurts)
  - OR any caught exception (D3 no-silent-except)

MIDDLE_BAND: fairness held + mechanism fired + some sel_unretr signal
  but full PASS not cleared. Best to be expected if replay reliably
  strengthens but doesn't fully close the +0.15 gap from +0.083.

## Cardinality (D4 mandatory)

EXPECTED_N_UNITS = len(SEEDS) * (3 single arms + len(LAMBDA_REPLAY_LIST)
                                  composition arms)
                = 3 * (3 + 3) = 18 arm entries TOTAL across full run.
HARD_FAIL_CARDINALITY_BREACH = observed_n_arm_entries != 18.

Smoke EXPECTED_N_UNITS = 1 * 6 = 6.

## Discriminator-must-survive-scale (D1)

Smoke uses FULL-N parameters (N=512, M_OLD=600, M_RECENT=400) with
N_COMPOSITE_QUERIES = 1500 (half full; preserves 3-pass schedule at 500
queries/pass) + SEEDS=[7] + N_QUERIES=100. The composition discriminator
must show a sel_unretr advantage >= 0.03 over TRACE_ONLY at smoke (else
stop and route back). At full N=512 alpha=1.953 is held (matches v3).

## Substrate-only-decode gate (load-bearing)

n_llm_calls per seed = 0 (numpy-only mechanism; substrate primitives
only; no transformers / no encoders).

## Real data / synthetic provenance

The cell uses random bipolar key/value pairs (matches v3 base; the
mechanism is about importance scoring + pruning + replay, NOT corpus
semantics). allow_synthetic=True is appropriate here per scope; cell
asserts no real-corpus dependency.

## Honest scope

This cell tests whether MULTI-EVENT REPLAY consolidation lifts the
sel_unretr discriminator from +0.083 (TRACE_ONLY) past the +0.15 PASS
floor. It does NOT test:
  - Whether replay generalizes to real-corpus ingest (separate cell).
  - Whether replay frequency is biologically tuned (just 3 cycles).
  - Whether other replay variants (compressed shuffle, etc.) outperform
    top-K trace-seeded replay (separate sweep).

## Verdict logic (4-class)

HARD_PASS only if all 5 HARD_PASS conditions met.
HARD_FAIL if any HARD_FAIL trigger fires.
MIDDLE_BAND if mechanism fired + sel_unretr > 0 + fairness held but
  PASS gaps not cleared.
HARD_FAIL otherwise (default).
