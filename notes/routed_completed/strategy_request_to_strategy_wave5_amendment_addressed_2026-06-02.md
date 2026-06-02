# Strategy request: Wave 5 amendment partially addressed (Cells 1-4 + 6 ready; Cells 2-refined + 7 deferred)

**From**: testbed
**To**: strategy (orchestrator) + research
**Date**: 2026-06-02
**Trigger**: `notes/research_wave5_cloud_bundle_amendment_2026-06-02.md` (ADD-1/2/3 + Cell 5 deferral)
**Related**: `notes/testbed_handoff_wave5_unified_n32768_2026-06-02.md` (original handoff)

## TL;DR

Amendment partially addressed:
- **Cell 5 (COMBO-1 implicit Gram-solve)** — DROPPED from batch JSON per amendment (deferred pending COMBO-1 v3). Script kept in repo at `experiments/exp_combo1_gram_kappa3_n32768_v1.py` but not referenced in batch.
- **Cell 6 (ADD-1: chain depth-extended)** — NEW SCRIPT BUILT (`exp_q_b1_depth_extended_n32768.py`). Smoke-validated at N=4096; mechanics + pre-reg bands working. Added to batch JSON.
- **Cell 2 ADD-2 refinement (delta-alpha sensitivity sweep)** — NOT YET extended. Current Cell 2 script only measures kappa_3 + kappa_4 + kappa_6 at a single alpha (no sensitivity perturbation sweep). Needs a follow-up edit to add the {0.0001, 0.001, 0.01, 0.04, 0.1} delta-alpha sweep with reused Hutchinson probes.
- **Cell 7 (ADD-3: PP-12 L=2 cross-layer composition)** — NOT YET BUILT. Amendment flags STORAGE BUDGET concern: full M_outer=1.24×10^6 needs 159GB (won't fit A100 80GB); recommend M_outer=5×10^5 (~64GB). Strategy + exp_dev resolve M_outer before testbed engineers the cell. If storage budget unresolvable on single instance, amendment says "DROP from bundle".

## Wave 5 batch JSON current state

`tools/cloud/batch_examples/wave5_unified_n32768.json` now contains 5 cells:
1. `qd1_spectral_primitives_n32768_v1` (Cell 1; built; ~30-60 min H100 wall)
2. `kappa46_fingerprint_n32768_v1` (Cell 2; built; ~30 min H100 wall — NOT YET refined per ADD-2)
3. `deletion_cert_zratio_n32768_v1` (Cell 3; built; ~30-60 min H100 wall)
4. `combo3_unified_api_n32768_v1` (Cell 4; built; ~30-60 min H100 wall)
5. `q_b1_depth_extended_n32768` (Cell 6 / ADD-1; built; ~30-60 min H100 wall)

Cell 5 (COMBO-1 N=32768) DROPPED per amendment. Cell 7 (PP-12 L=2) PENDING storage-budget resolution.

Estimated total bundle wall: ~3-5 hr H100 (per amendment's "~7-12hr" estimate for FULL bundle; my batch is leaner without Cell 5 + Cell 7).
Estimated cost: ~$6-12 at H100 ($4.29/hr) or ~$5-10 at A100 (~$1.50-2/hr per amendment).

## What testbed needs from strategy/exp_dev

### Decision 1: Cell 2 ADD-2 refinement scope

Should I extend `exp_kappa46_fingerprint_n32768_v1` to ALSO sweep delta-alpha at {0.0001, 0.001, 0.01, 0.04, 0.1} with the same Hutchinson probe set? The amendment says ~10-15 min added to bundle, which is cheap. ~30 min testbed engineering to add the inner-loop. Recommend YES if Cell 7 is also being built (avoids re-dispatch).

Alternative: ship the current Cell 2 (kappa_3/4/6 single alpha) in this batch; do delta-alpha sensitivity sweep as a separate follow-on dispatch later. Cleaner sequencing.

### Decision 2: Cell 7 PP-12 L=2 cross-layer storage budget

Per amendment, three options:
- (a) M_outer = 5×10^5 (FP32; ~64GB on A100 80GB; production-tractable; gives 2.5×10^11 addressable pairs)
- (b) M_outer = 1×10^6 with INT8 quantization (~64GB at INT8; tight; gives 5×10^11 addressable pairs)
- (c) DROP from bundle (amendment-sanctioned if storage doesn't resolve)

Testbed engineering effort for Cell 7: ~60-90 min if M_outer is fixed at one of (a) or (b). 

Need strategy/exp_dev call before I engineer.

### Decision 3: dispatch timing

Original handoff said "defer dispatch until Wave 5 trigger (user authorization OR auto-post-Wave-4-PASS)". The amendment doesn't change this. So all this engineering is preparatory; no Lambda spend yet.

Per [[feedback-short-cloud-runs-preferred]], cost estimate $6-12 is BELOW Round 6's $50-100 declined threshold but ABOVE the typical "short cloud" ~$1-2 size. Would still warrant explicit user case-by-case auth when dispatch trigger fires.

## What testbed will do, by default if no further direction lands

- Hold engineering on Cell 2 refinement + Cell 7 pending strategy decisions above
- Continue HOLDING on PP-8 (per v1b grid routing STOP directive)
- Standing by for Wave 5 dispatch trigger
- Could pick up other parallel work (Anthropic Phase 2 eval; dashboard Part B+D) if bandwidth permits

## Files referenced

- This routing
- `notes/research_wave5_cloud_bundle_amendment_2026-06-02.md` (amendment ADD-1/2/3)
- `notes/testbed_handoff_wave5_unified_n32768_2026-06-02.md` (original handoff)
- `experiments/exp_qd1_spectral_primitives_n32768_v1.py` (Cell 1)
- `experiments/exp_kappa46_fingerprint_n32768_v1.py` (Cell 2; needs ADD-2 refinement)
- `experiments/exp_deletion_cert_zratio_n32768_v1.py` (Cell 3)
- `experiments/exp_combo3_unified_api_n32768_v1.py` (Cell 4)
- `experiments/exp_q_b1_depth_extended_n32768.py` (Cell 6; NEW)
- `experiments/exp_combo1_gram_kappa3_n32768_v1.py` (Cell 5; dropped from batch; kept in repo for future)
- `tools/cloud/batch_examples/wave5_unified_n32768.json` (updated batch JSON)

Acted-on 2026-06-02: wave5 amendment review absorbed; testbed received amendment + ran cloud bundle delivering 3+1+1 HP/MIDDLE/HF; Cell 2 Part A theory refutation surfaced as wave5_theory_prereg_gap routing
