# exp_dev REFUSAL — substrate_bidirectional_meet_in_middle_phase_diagram_v1

**Authored:** 2026-06-28T21:48Z (exp_dev sub-agent)
**Decision:** REFUSE TO DISPATCH (Fix #26 pre-dispatch verify-the-referent + NO BUSY WORK)
**Refusal class:** mechanism-was-disproven-within-24h; phase-diagram-of-nonexistent-effect

---

## Spawn request summary

Task asked for an 84-grid sweep across (depth × n_branch × N) on a 3-arm bracket
(BIDIRECTIONAL meet-in-middle vs GREEDY forward vs RANDOM) with HARD_PASS at
"ARM_BIDI > ARM_GREEDY by >=0.20 at >=25 of 84 grid points", to promote
"Bidirectional meet-in-middle" phase coverage PARTIAL -> HIGH per the
characteristics table.

## Verify-the-referent finding (Fix #26)

Pulled `data/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu/metrics.json`
(landed 2026-06-27 07:12 — 38 hours ago). Verdict: **HARD_FAIL_NO_MEETING_PREMIUM**.

The v3 cell was the rigorous, controlled successor to v1/v2. It added two controls
that v1/v2 lacked:
- `ARM_FORWARD_HALF_DEPTH` — forward-only at floor(d/2)
- `ARM_RANDOM_MEET_BASELINE` — meet at random midpoint

Per-depth results (verdict_msg, copied verbatim):

| depth | fwd_full | bidir_meet_mid | fwd_HALF_DEPTH | random_meet |
|---|---|---|---|---|
| 3 | 0.320 | 0.443 | **0.684** | 0.402 |
| 5 | 0.131 | 0.329 | **0.460** | 0.319 |
| 7 | 0.071 | 0.258 | **0.320** | 0.254 |
| 9 | 0.032 | 0.179 | **0.216** | 0.180 |

**Two findings disprove the meet-in-middle mechanism:**

1. **No meeting premium:** ARM_BIDIR < ARM_FORWARD_HALF_DEPTH at every depth.
   The "lift" v1/v2 attributed to bidirectional was just the shorter-chain effect
   (compounding error halved). When you control for chain length, forward-half
   STRICTLY DOMINATES bidirectional. The "meeting" provides no value.

2. **True midpoint indistinguishable from random midpoint:** ARM_BIDIR ~ ARM_RANDOM_MEET
   at every depth (gaps 0.04 / 0.01 / 0.004 / -0.001). The "true midpoint" is not
   load-bearing; cosine-meeting at any midpoint produces equivalent retrieval. This
   is exactly the signature of the meeting operation being noise.

## Why the spawn prompt's characteristics-table classification is stale

The "CHAIN-GRADE ✓ / 60% completeness / PARTIAL coverage" table entry was authored
BEFORE v3's controls landed. v3 superseded v2's framing: what v2 called a +0.297
"meet-in-middle lift" was a shorter-chain artifact that v2 didn't control for.

The honest update to the characteristics table is:
- Stage 2 "Bidirectional meet-in-middle" -> **HARD_FAIL_v3** / 0% completeness / N/A coverage
- Mechanism does not survive its own forward-half-depth control in current substrate.
- Brain analog (Pfeiffer-Foster bidirectional sweep) is not currently realized in
  substrate primitives; further substrate work needed BEFORE phase-diagram sweep.

## Why I refuse rather than dispatch

Dispatching this cell would:

1. **Violate Fix #26 (pre-dispatch verify-the-referent gate):** identical mechanism
   was tested 38h ago with a stricter discriminator and HARD_FAILED.

2. **Violate NO BUSY WORK (USER 2026-06-17):** sweeping phase-diagram of a mechanism
   that doesn't fire is padding compute. 84 grid points × 3 seeds × 3 arms ~ 12-18
   CPU-hours of confirmed-null-result.

3. **Violate DISCRIMINATOR_MUST_SURVIVE_SCALE (USER 2026-06-26):** the proposed
   smoke discriminator "ARM_BIDI > ARM_GREEDY by 0.20 at mid-depth" already failed
   at depth=5, N=8192 with a STRICTER discriminator (v3 measured BIDIR=0.329 vs
   GREEDY forward-full=0.131; gap=0.198, just barely above the proposed bar, BUT
   FORWARD-HALF was 0.460, dominating BIDIR). The proposed smoke bracket would
   PASS while hiding that the cell is a non-result — the prompt's bracket lacks
   v3's controls.

4. **Violate STRATEGIC_INTERPRETATION_OVER_CLAIM (META checklist):** the
   "phase boundary where meet-in-middle outperforms greedy" framing assumes such
   a boundary exists. v3 evidence: it doesn't. A phase-diagram of a nonexistent
   effect measures noise sweep parameters.

## What I'm doing instead (substantive, in-lane)

Filing this refusal note as the substantive artifact for this cycle. The honest
output of this work-unit is the diagnosis that v3 superseded the characteristics
table entry. Filing as cert-trail (not mailbox).

Recommended next-cycle work for whoever picks up the bidirectional thread:

- **If the goal is "do better at multi-hop retrieval"**: skip bidirectional;
  forward-only at half depth strictly dominates. Look at `forward_half_depth` as
  its own mechanism — it might be the actual lever (with proper controls for
  what "half depth" task means in user-facing usage).

- **If the goal is "make the meeting mechanism actually work"**: substrate-side
  fix needed first. v3 showed cosine-meeting at the true midpoint is
  indistinguishable from cosine-meeting at a random midpoint, which means the
  intermediate representation is not discriminative enough for `meet()` to
  identify a TRUE intersection. Candidate fixes: stronger intermediate vectors
  (e.g., context-tagged), threshold-based filtering, multi-scale matching.
  These are substrate primitive design work, NOT phase-diagram sweeps.

- **If the goal is "phase-diagram fill for SOME Stage 2 PARTIAL-coverage primitive"**:
  pick a different primitive whose mechanism IS confirmed to fire. The
  characteristics table needs a re-read to find a genuinely-PARTIAL chain-grade
  primitive (not a stale one).

## File paths for parent agent

- v3 metrics (proof of disproof): `d:/AI/hd-instrument/data/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu/metrics.json`
- v3 prereg: `d:/AI/hd-instrument/preregs/2026-06-27_multihop_bidirectional_meet_in_middle_depth_scaling_v3.md`
- v3 cell (read for design lessons): `d:/AI/hd-instrument/experiments/exp_multihop_bidirectional_meet_in_middle_depth_scaling_v3_gpu.py`
- This refusal note: `d:/AI/hd-instrument/notes/exp_dev_REFUSAL_bidirectional_meet_in_middle_phase_diagram_v1_2026-06-28.md`

---

## Return values (per spawn-prompt contract)

- **Commit hash:** NONE (refused; no cell written)
- **Smoke verdict:** NOT_RUN (refused at pre-dispatch verify-the-referent gate)
- **3 seed dispatches:** NOT_DISPATCHED

**Disposition:** characteristics-table entry for "Bidirectional meet-in-middle"
needs refresh per v3 HARD_FAIL_NO_MEETING_PREMIUM. Phase-diagram fill is not the
correct next step; substrate-side mechanism work is the prerequisite.
