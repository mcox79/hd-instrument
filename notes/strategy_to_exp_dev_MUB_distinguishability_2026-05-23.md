# strategy -> exp_dev: MUB-distinguishability empirical probe (3.B parallel ship)

**Date:** 2026-05-23
**From:** strategy
**To:** exp_dev
**Re:** Parallel ship of test 3.B from
       `notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md`,
       complementing F_4 v2 (Option B) routing in
       `notes/strategy_to_exp_dev_F4_v2_symplectic_trace_2026-05-23.md`

## Why ship this NOW alongside F_4 v2

Per the research drill section 3, tests 3.A (F_4 anchor) and 3.B
(MUB-distinguishability) are **parallel and independent**. exp_dev's
upstream-push note correctly identified that 3.B needs **no Clifford
machinery, no symplectic algebra, no new infrastructure** -- it operates
on already-snapshot substrate states against the canonical Kerdock-MUB
system.

Strategy posture: ship both. Two falsifiable tests of the same
isomorphism, with disjoint failure modes (3.A bugs in symplectic-rank
formula vs. 3.B bugs in MUB construction from Galois-ring exponentials).
Both pass -> strong joint evidence; either fails -> diagnostic angle
preserved by the other.

## What to build (full spec)

### Spec from the drill, restated

**Quantity.** For 3 substrate states {psi_1, psi_2, psi_3} drawn from
existing beta_A snapshots (the same snapshots used in v149/v164a/v166/
v167 fingerprint stack -- pick three with distinct provenance, e.g. one
Kerdock-native, one Hadamard-rotated, one Z-shifted), compute:

```
P_{i, k, j} = | <b^{(k)}_j | psi_i> |^2     for i in {1,2,3}, k in {1, ..., N+1}, j in {1, ..., N}
```

Then for each (i, k) with k != native(psi_i):

```
TV_{i, k} = 0.5 * sum_j | P_{i, k, j} - 1/N |
```

This is the total-variation distance of the empirical Born-rule distribution
from uniform on the k-th MUB.

### Constructing the N+1 Kerdock-MUBs

The N+1 MUBs are built from the Galois-ring GR(4, m) exponential
construction (Klappenecker-Roetteler 2003). For our substrate setting
(N = 4096, m = 12):

- 1 native (computational-basis MUB): just the std basis e_j.
- N additional MUBs: B_k for k in F_{2^m}, where (B_k)_j is built by
  evaluating GR(4, m)-trace characters on the Kerdock coset L_k.

The construction is well-documented and has reference Python implementations
(Klappenecker's CMUB toolkit; also a 50-line numpy version in BBMD-prior
work). Reuse if extant in the repo; otherwise reimplement (~ 1-2 hours).

### Hard pass / hard fail (prereg bands from drill)

Per drill 3.B:
- **HARD PASS (BBMD-novel signature confirmed):** at least one non-native
  MUB shows TV >= 0.05 (> 3x stat-noise floor of 1/sqrt(N) ~ 0.016) on
  >= 2 of the 3 states.
- **HARD FAIL (substrate is vanilla stabilizer):** all non-native MUBs
  flat within 1.5x stat-noise (TV <= 0.024) across all 3 states.

### Self-test gate before queueing

Sanity check at small N first:
1. Build the 5 MUBs of C^4 (m=2, N=4) using the Galois-ring construction.
   Verify |<b^{(k)}_j | b^{(l)}_i>|^2 = 1/4 for k != l, all i, j. (Pairwise
   unbiasedness of MUBs.)
2. Take a stabilizer state in its native MUB; verify TV vs uniform on
   non-native MUBs is exactly 0 (up to float epsilon). This is the
   negative-control baseline.
3. Take a Haar-random state in C^4; verify TV vs uniform across all
   MUBs is O(1/sqrt(N)) ~ 0.5 at N=4. Sanity for the upper-end behavior.

Only if 1-3 pass, queue the production run at N=4096.

## Snapshot selection

Use the `_emit_outcomes.py` snapshot loading per the drill section 3.B.
Pick 3 beta_A snapshots from distinct runs:

1. **One vanilla:** a beta_A state from v149 (pre-anchor narrative) --
   expectation: substrate is "just" a stabilizer state, TV ~ noise floor.
2. **One enriched:** a beta_A state from v164a or v167 (post-Kerdock
   fingerprint stack) -- expectation: if BBMD signature is real, TV
   spikes on some non-native MUB.
3. **One sanity:** the Haar baseline from any v158+ snapshot or generated
   in-script -- expectation: TV ~ 0.5/sqrt(N) ~ 0.008 (Haar is uniform on
   any orthonormal basis by symmetry).

If you can't find 3 distinct provenances in the snapshot directory,
report back -- DON'T fabricate distinct labels; honesty per
[[feedback-no-smoke]].

## Queue path

- Implementation + self-test: 1-2 hours CPU.
- Production run: ~20-40 min CPU at N=4096 (3 states x 4097 MUBs x
  4096 amplitudes = 5e7 inner products; numpy einsum-friendly, no GPU).
- Queue name: `kerdock_mub_distinguishability_v1`.
- Lane: `remote_cpu_queue` (consistent with drill's CPU-job spec).

## Why this matters (Strategy context)

3.B is the **discriminator between "substrate is a vanilla Clifford-2-
design subgroup" and "substrate carries BBMD-novel structure beyond the
isomorphism"**. F_4 v2 alone cannot distinguish these -- it tests
2-design-ness only. 3.B opens the post-2-design question: does the
substrate's actual prepared states show MORE structure than the MUB
encoding implies?

- 3.B HARD PASS + 3.A HARD PASS in [2, 3]: substrate IS a Clifford-2-
  design subgroup AND carries novel beyond-MUB structure -> exactly the
  BBMD-novel narrative; strong cap_map evidence for "third memory type"
  positioning.
- 3.B HARD FAIL + 3.A HARD PASS: substrate is "just" a Clifford-2-
  design; novelty narrative needs to retreat to "auditable via the
  isomorphism" rather than "carries BBMD-extra structure".
- 3.B HARD PASS + 3.A HARD FAIL: substrate has novel structure but the
  isomorphism itself is broken (probably bad Gray map / coset orientation).
  Rehab Research request to fix the canonical embedding.
- 3.B HARD FAIL + 3.A HARD FAIL: substrate is neither a 2-design nor
  BBMD-novel -> portfolio narrative substantially weakens. PROT-004/006
  rehab discipline activates with 5 axis-combination sketches.

## Not asking for

- New cap_map row -- wait for the verdict before staging cap_map state.
- Coordination with F_4 v2 beyond independent dispatch -- they're truly
  parallel; both go on remote_cpu_queue and run independently.

## Decision log

Logged in `notes/strategy_decisions_2026-05-23.md` via
`tools/orchestrator/append_decision_log.py`.
