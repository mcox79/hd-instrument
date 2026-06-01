# Strategy -> Exp Dev: Bet A M_init capacity ceiling respec (cycle 174 v154)

**Filed**: 2026-05-23 ~10:32 EDT
**Trigger**: `wave14_betA_M_init_threshold_v1` FULL = BETA_M_INIT_UNIFORM_KILL
(all 6 M_init values in {1024, 2048, 4096, 8192, 16384, 32768} hit CUDA OOM
at N=65536; `oom: True` for every config; `mean_kept=0.0` artifact from
no-measurement not negative-measurement)
**Strategy decision (cycle 174)**: NOT a closure, NOT a substrate refutation.
21st smoke->FULL divergence anchor (2nd REFUTATION direction) is OOM-driven.
The M_init capacity ceiling question REMAINS OPEN.

## What needs to happen

Respec the M_init capacity sweep at N=65536 so that the experiment can
actually produce measurements at each M_init point. Three options ranked
by leverage / cost:

### Option A (recommended): per-M_init memory hygiene + narrower sweep

Modify `experiments/exp_wave14_betA_M_init_threshold_v1.py` to:

1. Move `torch.cuda.empty_cache()` BEFORE each M_init iteration (not only
   in the OOM branch). The current code calls empty_cache only after
   an OOM occurs; large allocations from prior M_init iterations may
   already have fragmented memory.
2. Narrow the FULL sweep to {1024, 2048, 4096, 8192} at N=65536. The
   v2 PASS at M_init=8192 N=65536 is the highest confirmed point;
   adding 4 more M_init points up to that value characterizes the
   regime BELOW the rescued operating point.
3. Optionally extend with a second-run "upper end" sweep at smaller N
   (e.g., {16384, 32768, 65536} at N=8192 or N=16384) to characterize
   the capacity ceiling vs N at a lower memory cost. Keep the two sweeps
   in separate experiment names for clean verdict harvesting.

Expected cost: ~30-45 GPU-min total for the N=65536 narrow sweep + the
smaller-N upper sweep. Memory budget at N=65536 should fit M_init <=8192
based on the v2 5-seed PASS evidence.

### Option B: gradient-checkpointing / chunked allocation

If the substrate's W matrix at N=65536 with large M_init exceeds VRAM
even after empty_cache hygiene, refactor `ba.run_one_seed` to allocate
W in chunks (e.g., per-row or per-block) rather than as a single large
tensor. This is the only path to actually exercise M_init >= 16384 at
N=65536 on 8GB VRAM. Substantially more engineering than Option A;
file a separate task if needed after Option A measures the practical
ceiling.

### Option C: defer the upper-end question

Accept that the substrate operating point at M_init=8192 N=65536 is
the validated regime for Bet A and that characterizing M_init in
{16384, 32768, 65536} at N=65536 is not on the current substrate-product
critical path. Mark the capacity ceiling at 🟡 OOM-deferred and revisit
when the hardware budget allows (e.g., on a 24GB GPU) or when a
substrate-product question specifically demands the larger-M_init regime.

## Strategy preference

Option A first (cheap, narrow sweep + smaller-N upper extension; ~30-45
GPU-min). If the narrow sweep at N=65536 confirms the substrate retains
across {1024, 2048, 4096, 8192} at FULL, that pins down the lower-half
of the M_init capacity envelope at the rescued N. The smaller-N upper
sweep then characterizes the M_init/N ratio for the upper-half.

Option B and C remain available depending on the Option A result.

## Verdict semantics for the respec

The current `compute_verdict` logic in
`experiments/exp_wave14_betA_M_init_threshold_v1.py` does not distinguish
between "OOM at all M_init" and "all M_init genuinely killed" — both
return BETA_M_INIT_UNIFORM_KILL with `mean_kept=0.0`. Recommend adding
a fourth branch:

```python
if all(v.get("oom", False) for v in per.values()):
    return ("BETA_M_INIT_OOM_INCONCLUSIVE", f"all M_init OOM: {per}.")
```

Insert before the UNIFORM_KILL branch (line 33 area). This avoids
mislabeling future OOM-only runs as substrate refutations.

## Acceptance criteria for the respec

- At least one M_init at N=65536 produces 5 seeds of data with
  `mean_kept >= 0.85 sd<0.05` (recovers cycle 172 v2 PASS evidence at
  the rescued operating point)
- At least three M_init points produce non-OOM measurements at the
  full N=65536 sweep, allowing the threshold logic to actually function
- Smaller-N extension covers M_init >= 16384 with non-OOM measurements
  so the upper end of the capacity ceiling is characterized at some N

## Substrate-product framing

Per [[feedback-no-papers-product-only]] this is a substrate-product
capacity-envelope measurement, NOT a paper-grade scaling study. The
question is "what M_init does the substrate retain at?" not "what is
the scaling law of M_init vs N?". Per Strategy v153 the substrate-product
portfolio already has Bet A axis ✅ at M_init=8192 N=65536; this respec
extends the envelope, it does not gate a substrate-product capability.

## File-routing only (per [[feedback-sessions-self-coordinate]])

No user-side prompt edit needed. Exp Dev reads this file on next cycle
via the `notes/exp_dev_request_from_strategy_*.md` convention; ACK with
a decision-log entry on pickup; ship the respec at Exp Dev's normal
pace. Strategy will harvest the next verdict via the orchestrator
dispatch mechanism.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
