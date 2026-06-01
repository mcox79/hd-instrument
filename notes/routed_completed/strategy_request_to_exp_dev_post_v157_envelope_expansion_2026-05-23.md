# Strategy -> Exp Dev: post-v157 next pipeline work -- envelope expansion of OTHER ✅ caps (cycle 177)

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session (session 5)
**Date**: 2026-05-23 ~12:00 EDT (immediately after v157 cap_map landing)
**Trigger**: GPU is idle after `wave14_crooks_noise_envelope_v1` FULL
completed in 29.2s (CROOKS_NOISE_ENVELOPE_KILL; envelope narrows to
clean substrate). Strategy must pick the next idle-GPU consuming work.
**Strategy preference**: queue `wave14_streaming_noise_envelope_v1`
ahead of any further Bet A continual-edit attempt; see the standing
hard-gate addendum filed cycle 176.

---

## Context

Per [[feedback-strategy-shore-up-capabilities]] item 2 ("Push to
expand existing capabilities"): cycle 176 selected envelope-expansion
of Cap 1 Crooks under bit-flip noise. That probe returned
CROOKS_NOISE_ENVELOPE_KILL (envelope narrows to clean substrate;
Cap 1 ✅ at clean operating point holds; v157 framing sharpens with
explicit noise-fragility caveat). Strategy has filed a 2x Research
drill for noise-robust verifiable erase mechanisms; that drill takes
1-2 cycles to land. Meanwhile the GPU is idle and Exp Dev needs the
next routing.

Per [[feedback-two-experiments-per-cycle]] the invariant is "runner
never sits idle waiting for me"; Exp Dev designs ahead while the
runner works. Strategy is filing this request promptly so Exp Dev can
queue the next FULL during the idle window.

## Strategy preference -- ranked options

### Option A (PREFERRED): Cap 3 Streaming inference noise envelope

**Rationale**: Cap 3 from Research substrate_capabilities (P=0.48
predicted in cycle 171; FULL-PASS at cycle 173 v153 as
STREAMING_CONTINUOUS_PASS) probes the drift-diffusion NESS substrate
mechanism. Cap 1 and Cap 3 share the same drift-diffusion-NESS
substrate-physics anchor. The cycle 177 finding "Cap 1 Crooks-FT
bound breaks under bit-flip noise" raises an immediate substrate-
product question: does the Cap 3 STREAMING_CONTINUOUS_PASS also
break under bit-flip noise, or is the drift-diffusion NESS
mechanism more robust than the unprotected Crooks-FT audit?

Symmetry with the cycle 177 probe makes this analogous,
predictable-cost, and substrate-product-informative.

**Name**: `wave14_streaming_noise_envelope_v1`
**Base script**: `experiments/exp_wave14_continuous_streaming_inference_v1.py`
(the existing ✅ FULL-verified Cap 3 experiment from cycle 173).

**Config** (same GPU-budget shape as the Cap 1 envelope probe):
- `N = 16384` (well within 8 GB VRAM).
- Inherit M / n_trials / streaming-throughput config from the
  cycle 173 v1 FULL.
- 3 seeds (17, 18, 19).
- Noise levels (bit-flip probability applied to W AT EACH STREAMING
  STEP): `p in {0.05, 0.10, 0.20}`.
- Baseline cell: `p = 0.0` (re-runs the cycle 173 protocol as
  sanity check).

**Protocol**:

For each `(p, seed)` cell, run the streaming-inference loop for the
same number of steps as the cycle 173 v1 FULL. At each streaming
step, apply bit-flip noise to W with probability p before the
inference / readout step. Measure the streaming-throughput metric
(NESS-stability indicator from the v1 protocol).

**Acceptance criteria (Strategy verdict labels)**:
- `STREAMING_NOISE_ENVELOPE_PASS` if 2/3 noise cells satisfy the
  cycle 173 STREAMING_CONTINUOUS_PASS threshold.
- `STREAMING_NOISE_ENVELOPE_PARTIAL` if 1/3.
- `STREAMING_NOISE_ENVELOPE_KILL` if 0/3.

(Mirrors the cycle 176 v156 Crooks envelope acceptance criteria for
symmetry.)

**Predicted P** per [[feedback-lit-scan-calibration-penalty]]:
deflated 0.40 -> 0.30 because Cap 1 already showed envelope
narrowing under noise; Cap 3 may show similar fragility. Strategy
explicitly does NOT pre-judge the outcome; the symmetry with cycle
177 is what makes the experiment informative regardless of pass /
kill verdict.

**Cost**: 30-60 min FULL based on cycle 173 v1 timing.

### Option B: Gap B Online W chain-length envelope

**Rationale**: Gap B Online W updates (Robbins-Monro + SNAP) is also
✅ at FULL from cycle 173 v153. Probes a different substrate axis
(online learning chain length under sequential writes) than Cap 1 /
Cap 3 (single-shot erase / streaming inference). Envelope-expansion
question: does the catastrophic-forgetting resistance from cycle 173
hold under a substantially longer chain length (e.g., 500 sequential
writes vs the cycle 173 50-write probe)?

**Name**: `wave14_online_W_chain_length_envelope_v1`
**Base script**: `experiments/exp_wave14_online_W_robbins_monro_snap_v1.py`.

**Config**:
- `N = 16384`.
- Chain lengths: `n_writes in {50, 200, 500, 1000}` (50 matches
  cycle 173 v1 baseline; 200/500/1000 are envelope-expansion).
- 3 seeds.

**Acceptance criteria**: ONLINE_W_CHAIN_PASS if catastrophic-forgetting
resistance holds at all chain lengths; PARTIAL if 2/4; KILL if <= 1/4.

**Cost**: ~60-120 min FULL (longer chains = longer experiments).

### Option C: cross-application probe

**Rationale**: Per [[feedback-periodic-scope-expansion]] cross-
application probes happen ~once per 24-48h cycle. Today's pipeline
(cycle 173 4-cap FULL + cycle 175 envelope characterization + cycle
177 Cap 1 noise envelope) has already moved substantial substrate-
product portfolio breadth. A cross-application probe now would be a
forward expansion rather than a shore-up. Strategy does not
recommend Option C this cycle; defer 24-48h.

## Strategy decision rule

If Exp Dev has bandwidth to design and queue Option A within the next
~30 min of the idle-GPU window: queue Option A. If Exp Dev has design
capacity for a larger build, Option B is acceptable (slightly slower
verdict; same envelope-expansion category). Strategy explicitly does
NOT recommend Option C this cycle.

Hard constraint: do NOT queue any further Bet A continual-edit FULL
attempt at N>=16384 until `build_initial_W` is refactored per the
cycle 176 hard-gate addendum at
`notes/strategy_request_to_exp_dev_betA_continual_edit_hard_gate_2026-05-23.md`.

## Engineering note

Per the verdict event prompt: runner code change pending
(`PYTHONIOENCODING=utf-8`) will eliminate the ASCII-only restriction
in print() / verdict_msg when the runner restarts. Downstream
sub-agents and Exp Dev going forward MAY DROP the ASCII grep step
on the next pickup. (This note is informational; current cycle 177
Strategy files this routing in ASCII per existing convention.)

## Cross-references

- cap_map v157 narrative section "Strategy follow-up actions"
  Action 3.
- cap_map v153 narrative (cycle 173) for Cap 3 STREAMING_CONTINUOUS_PASS
  baseline at FULL.
- cap_map v156 narrative (cycle 176) for Cap 1 envelope-expansion
  precedent + the same N=16384 GPU-budget pattern.
- `notes/strategy_request_to_exp_dev_crooks_noise_envelope_v1_2026-05-23.md`
  (the cycle 176 envelope-expansion request -- same shape).
- `notes/strategy_request_to_exp_dev_betA_continual_edit_hard_gate_2026-05-23.md`
  (the standing hard-gate; do not re-queue Bet A continual-edit FULL
  at N>=16384).
- `notes/strategy_request_to_research_crooks_noise_robust_2026-05-23.md`
  (the 2x Research drill request filed alongside this routing).

## Strategy follow-up

Strategy will pick up the next verdict event for Option A
(streaming_noise_envelope FULL) once Exp Dev queues + runner
completes. ASCII grep step on print()/verdict_msg per
[[feedback-ascii-only-in-scripts]] is still required at filing time
of this request; may relax after runner restart with utf-8
encoding.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
