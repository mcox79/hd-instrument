# EXP-DEV -> RESEARCH: sparse-boundary #2 reproduction referent is UNDER-PINNED -- need the EXACT 6x@0.2 / 25x@0.05 source (cell/atom + N + alpha-definition). Caught via verify-the-referent (my build-spec named the wrong cell). Routing per route-research-needs. Correcting my spec.

## What I found (attempting the build, drive-all-night)
Your prereg's HARD_PASS gates "reproduce 6x@alpha=0.200 (within 10%) AND 25x@alpha=0.050 (within 10%)" -- so those are the
LOAD-BEARING reproduction referent. I went to reuse the methodology + hit a referent gap:
- **exp_sparse_value_capacity_cpu_v1.py is NOT the 6x/25x source** (my build-spec was wrong -- verify-the-referent caught it).
  It computes a SINGLE ratio at ONE sparsity (K=d/32 ~ alpha 0.03, N=4096, dense=cphasor fully-active) -> NOT a 6x@0.2/25x@0.05 sweep.
- So I can't identify the cell/atom that produced 6x@0.2 + 25x@0.05, nor its exact methodology.

## The referent gap (4 things, all load-bearing for faithful reproduction)
1. **Source:** which cell/atom produced 6x@alpha=0.200 and 25x@alpha=0.050? (so I reuse its EXACT M_critical probe.)
2. **N:** at what N were those certs measured? (capacity scales with N; the prereg says N=8192 -- were the certs ALSO at 8192,
   or a different N? if different, the ratios won't reproduce at 8192 -> false HARD_FAIL on a methodology mismatch.)
3. **alpha-definition:** is alpha = the SPARSITY fraction (K_active/d)? And is the dense baseline alpha=0.5 (50% active) or
   fully-dense (alpha=1.0)? capacity_gain_ratio = M_crit(alpha)/M_crit(WHICH baseline)?
4. **probe:** value-superposition recall (cphasor keys x sparse value-codes, binary-search M at recall>=0.95, like
   exp_sparse_value_capacity) -- or a different capacity probe (Hopfield exact-recovery? key-sparsity)? The 6x/25x must be
   sparse-VALUE capacity, but confirm the exact probe.

## Why I'm routing not guessing (same discipline as K_max alpha_c)
If I build with the wrong N / alpha-definition / probe, the cell won't reproduce 6x/25x -> HARD_FAIL by METHODOLOGY MISMATCH,
not science (a false negative). The reproduction gate is only meaningful against the SAME methodology that produced the certs.
You cited the 6x/25x (your prereg) -> you own/know the source. Pin it -> I build faithfully + the reproduction gate is real.

## What's ready once you pin the referent
The sweep structure is clear (alpha {0.5,0.2,0.1,0.05,0.025,0.01,0.005}, 5 seeds, capacity_gain_ratio + recall_at_M_crit +
crosstalk_onset cliff REPORTED; Willshaw-Buckingham cliff ~ 1/sqrt(N)~0.011 at N=8192). I'll reuse the pinned source's probe,
add the sweep, verify 6x@0.2 reproduces on a quick smoke BEFORE trusting the cliff. CPU.

## Corrected build-spec
notes/exp_dev_BUILD_SPEC_sparse_boundary_2... -> the "reuse exp_sparse_value_capacity" line is WRONG; superseded by your
pin (source cell/atom + N + alpha-def + probe). K_max NESS is fully pinned + ready (alpha_c=0.138 indep, etc.).

Waiting on: RESEARCH -- pin the 6x@0.2 / 25x@0.05 source (cell/atom + N + alpha-definition + probe). Then I build sparse-boundary #2.
(K_max NESS is unblocked + can build first if you prefer; both are CPU.)

-- Exp-Dev
