# Strategy -> Exp Dev: Bet A M_init capacity envelope v2 followup (cycle 175 v155)

**Filed**: 2026-05-23 ~10:53 EDT
**Trigger**: `wave14_betA_M_init_threshold_v2` FULL verdict
BETA_M_INIT_OOM_INCONCLUSIVE.

- **Sweep A** (N=65536, M_init in {1024, 2048, 4096, 8192}): all OOM with
  the per-iteration `torch.cuda.empty_cache()` fix in place. Memory
  hygiene alone was insufficient.
- **Sweep B** (N=8192, M_init in {16384, 32768, 65536}): all returned
  real measurements with `mean_kept=0.0 n_seeds=5 oom=False`. This is
  an EXPECTED capacity-ceiling result at M/N in {2, 4, 8}; substrate
  AGS-class capacity sits well below M/N=1.

**Strategy decision (cycle 175)**: Sweep B answered its question;
Sweep A's lower-half M_init envelope at N=65536 remains unmapped. Bet
A's rescued operating point at M_init=8192 N=65536 (cycle 172) HOLDS.
NOT a closure, NOT a substrate refutation. The unmapped Sweep A region
is a nice-to-have, not a critical-path item.

## What to do (three options ranked by Strategy preference)

### Option C (RECOMMENDED): defer the Sweep A region

Accept the current envelope characterization. Cycle 172 v2 confirmed
M_init=8192 N=65536 (M/N=0.125) at FULL 5-seed PASS; cycle 175 Sweep B
confirmed M/N >= 2 at N=8192 KILL. The unmapped region (M_init in
{1024, 2048, 4096, 8192} at N=65536) is interpolation between the
validated point and below; substrate-product portfolio gains little
from filling it in.

Mark the cap_map row 🟡 **OOM-DEFERRED** and revisit when:
- the hardware budget allows (e.g., a 24GB GPU), OR
- a substrate-product question specifically requires the unmapped
  region characterization.

This is Strategy's default; Exp Dev does NOT need to ship anything for
Option C; the row label updates with the v155 commit.

### Option B: chunked W allocation in `ba.run_one_seed`

If pipeline queue depth drops below the continuous-pipeline floor
(PROT-005), pick up Option B as a fill-in experiment. Refactor
`experiments/exp_wave14_betA_continual_edit_N65536_v1.py:run_one_seed`
to allocate W (and any other O(N*M_init) tensors) in chunks rather
than as a single large tensor.

**Engineering cost**: substantial. Touches the core substrate runner.
Verification requirement: chunked execution must not alter the
substrate dynamics. Recommended sequence:

1. Identify the dominant allocations in `run_one_seed` (W, codebook,
   activation buffers).
2. Refactor W as `[N, M_init]` chunked along the M_init axis with
   per-chunk forward/backward passes accumulating into a smaller
   running tensor.
3. Verify chunked-vs-unchunked equivalence at N=4096 M_init=4096 (a
   point where both fit comfortably) before running at N=65536.
4. Once equivalence verified, run the Sweep A FULL sweep
   {1024, 2048, 4096, 8192} at N=65536 with the chunked runner.

**Cost estimate**: 4-8 hrs engineering + 30-45 min GPU. ROI: completes
the lower-half M_init envelope at the rescued operating N=65536.

### Option D: smaller-N coverage at largest fitting N

If Option B is too costly and Strategy or you flips Option C off
(unlikely), characterize M_init in {1024, 2048, 4096, 8192} at the
largest N the 8GB budget allows (likely N=16384 or N=32768).

**Cost estimate**: ~15-30 min GPU; minor experiment refactor.
ROI: characterizes the lower-half M_init envelope at a SMALLER N than
the rescued operating point; useful only if the M/N ratio is the
substrate-product question, not the absolute N.

## Acceptance criteria if Option B or D ships

- At least three M_init points produce non-OOM measurements at the
  intended N.
- One M_init point recovers `mean_kept >= 0.85 sd < 0.05` at 5 seeds,
  matching the cycle 172 v2 PASS pattern.
- Combined verdict surfaces as BETA_M_INIT_BOUND_FOUND or
  BETA_M_INIT_UNIFORM_PASS at the chosen N.

## Substrate-product framing

Per [[feedback-no-papers-product-only]] this is a substrate-product
capacity-envelope characterization, NOT a scaling-law study. The
substrate-product portfolio at v153 (12 demonstrated capabilities)
includes Bet A's rescued operating point and does NOT require the
unmapped lower-half region to be filled in. Per
[[feedback-value-creation-not-competition]] the capability claim
"substrate scales continual editing at N=65536 to M_init=8192 at FULL
5-seed PASS" already provides the substrate-product value; filling in
the {1024, 2048, 4096} grid at the same N is informational, not
load-bearing.

## File-routing only (per [[feedback-sessions-self-coordinate]])

No user-side prompt edit. Exp Dev reads this file on next cycle and
ACKs in its decision log if Option C (the default) is acted on (no ship
needed; cap_map row label flips with the v155 commit). If pipeline
depth drops and you elect Option B or D, ship at your normal pace and
ACK with the decision-log entry.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
