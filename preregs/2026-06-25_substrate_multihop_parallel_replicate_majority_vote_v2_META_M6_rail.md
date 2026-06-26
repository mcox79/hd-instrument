# Pre-reg: substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail

**Authored:** 2026-06-25 (exp_dev under autonomous YOLO; USER explicit ask "dispatch cell x v2 for sure")
**Anchor:** `substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail`
**Cell:** `experiments/exp_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail.py`
**Routing:** `local_cpu_queue`
**Mode determination (from Stage-1 sanity check):** **MODE B** (Cell X v1 used the SAME cleanup primitive as
pointer-chain v2; the 0.78-vs-0.122 single-chain gap is a REGIME artifact, not a mechanism gain)

---

## Stage 1 sanity-check findings (authoritative)

### Identical pieces (verbatim across both cells)
| Component | Cell X v1 | pointer-chain v2 |
|---|---|---|
| `bipolar(M, n, g)` | L180-182 | L149-151 (verbatim) |
| `ingest_hebbian` | L185-195 | L154-164 (verbatim) |
| `make_two_hop_chains_betasweep` | L198-220 | L169-194 (verbatim) |
| `chain_naive_hard` | L223-230 | L197-207 (verbatim) |
| `make_deep_chains` | L246-276 | L230-267 (verbatim) |
| Substrate dims (FULL) | N=8192 V_C=200 n_predicates=10 K_SET=20 seeds=[7,17,23] | identical |

### Cleanup-primitive math (the load-bearing pair)

Cell X v1 `_one_chain_step` (L283-298, K=1 noise=0 branch):
```
key = (cur_state * R[p] * sq).astype(np.float32)
readout = W @ key             # noise=0 when K_replicate==1
next_idx = int((E @ readout).argmax())
new_state = E[next_idx].copy() # next-hop cur_state = cleaned codebook atom
```

pointer-chain v2 `_retrieve_1hop` (L270-274) chained via `arm_pointer_chain` (L277-300):
```
key = (E[s] * R[p] * sq).astype(np.float32)
scores = E @ (W @ key)
s_pred = int(scores.argmax()) # next-hop seed = cleaned codebook index; next iter does E[s_pred]
```

**These are algorithmically equivalent.** Same key formula; same W projection; same argmax over E; same
cleaned-atom seed propagation. Cell X v1 at K=1 noise=0 == pointer-chain v2 mechanism EXACTLY.

### So why did Cell X v1 K=1 5HOP=0.78 vs pointer-chain v2 5HOP=0.122 (seed=7: 0.145)?

**Cell X v1 was run in SMOKE MODE.** Per metrics.json L5: `"run_mode": "smoke"`, N=2048, n_chains=50,
max_depth=5, 1 seed. Pointer-chain v2 ran FULL: N=8192, n_chains=200, max_depth=10.

**W-binding crosstalk diff (the dominant driver):**
- Cell X v1 W = make_deep_chains(n_chains=50, V_P=10, max_depth=5) -> 50 x 5 = **250 (s,p,o) bindings**
- pointer-chain v2 W = make_deep_chains(n_chains=200, V_P=10, max_depth=10) -> 200 x 10 = **2000 bindings**

**8x more bindings in the same (V_C=200, V_P=10) key space.** This is exactly the documented pointer-chain v1
->v2 BUG PATTERN (cell v2 DESIGN_NOTE quote: "v1 ingested ~7.5x more triples spread across the same
per-predicate key space -> drastically more per-(s,p) crosstalk -> lower 1-hop accuracy -> chain compounds").
Cell X v1 inadvertently re-created the LOW-CROSSTALK regime by running smoke (50 chains) at smaller max_depth
(5 instead of 10).

**N dimension (secondary):** N=2048 (smoke) vs N=8192 (full). Smaller N usually HURTS, not helps; this is
not the dominant factor.

### Verdict on Cell X v1: META_M6 violation, regime artifact

Cell X v1 v1's 0.78 single-chain 5HOP comes from:
1. Running in SMOKE MODE (verdict reported as if full)
2. n_chains=50 max_depth=5 -> 250 W bindings vs pointer-chain v2's 2000 bindings
3. Pointer-chain v2 cleanup (verbatim) WOULD produce ~0.78 in that low-crosstalk regime too

The 0.78 is NOT a parallel-voting win and NOT a better-cleanup win. It is the **smoke-vs-full sign-flip
pattern** repeated. The K=5/K=15 voting arms (0.80, 0.86, 0.82) showed only marginal lift over 0.78 and were
NON-monotonic (K5 > K15) which itself is a tell that voting wasn't the load-bearing mechanism.

## Mode B (selected): Cell X v2 must reproduce pointer-chain v2 at IDENTICAL regime

If Cell X v2 ARM_REPRODUCE_POINTER_CHAIN_V2 at IDENTICAL regime (N=8192, n_chains=200, max_depth=10,
W from deep-chains-of-depth-10) returns 0.78 -> META_M6 says regime is the same and v1 was NOT a regime
artifact (would contradict my stage-1 finding; mode would flip to Mode A). If it returns 0.10-0.20 -> v1's
0.78 was indeed the regime artifact; Cell X v2's parallel-voting arms (also at the matched regime) tell us
whether parallel voting actually helps in pointer-chain v2's hard regime.

## Cell X v2 design

### Five arms

| Arm | Config | Target |
|---|---|---|
| ARM_BASELINE_HRR_2HOP | beta-sweep regime; chain_naive_hard mechanism | top1 in [0.62, 0.68] (sanity rail) |
| ARM_REPRODUCE_POINTER_CHAIN_V2 | K=1 noise=0; W = make_deep_chains(n=200, V_P=10, max_depth=10); test depth=5 | top1 in [0.08, 0.20] (META_M6 rail) |
| ARM_CELLX_V1_AS_DOC | K=1 noise=0; W = make_deep_chains(n=50, V_P=10, max_depth=5); test depth=5 | top1 in [0.65, 0.85] (replicates v1's 0.78 within smaller-W regime) |
| ARM_PARALLEL_K5_PERHOP_5HOP | K=5 noise=0.05; per-hop vote; W = pointer-chain v2 regime (n=200, depth=10) | discriminator at matched-regime |
| ARM_PARALLEL_K15_PERHOP_5HOP | K=15 noise=0.05; per-hop vote; W = pointer-chain v2 regime (n=200, depth=10) | primary discriminator at matched-regime |

**Two-W discipline:** ARM_REPRODUCE_POINTER_CHAIN_V2 + ARM_PARALLEL_* all SHARE one W matrix
(`W_pointer_v2_regime`) built from deep-chains(n=200, max_depth=10). ARM_CELLX_V1_AS_DOC has its OWN W
(`W_v1_regime`) built from deep-chains(n=50, max_depth=5). The 200 test queries in ARM_REPRODUCE +
ARM_PARALLEL_* come from the n=200 chain set (truncated to depth=5). The 50 test queries in
ARM_CELLX_V1_AS_DOC come from the n=50 chain set (truncated to depth=5). Same E, R, seed across all.

### Pre-reg bands (LOCKED via module-init asserts; cv across seeds [7, 17, 23])

**SACRED SANITY rails (verdict pre-empted by rail breach):**
- RAIL_BASELINE: ARM_BASELINE_HRR_2HOP NOT in [0.62, 0.68] on majority of seeds -> `RAIL_BASELINE_BREACH`
- RAIL_META_M6: ARM_REPRODUCE_POINTER_CHAIN_V2 NOT in [0.08, 0.25] on majority of seeds ->
  `META_M6_RAIL_VIOLATION` (regime DIFFERENT than pointer-chain v2; v1 + v2 results uninterpretable for
  Barrier 1 revival claim)
- RAIL_V1_DOCUMENTED: ARM_CELLX_V1_AS_DOC NOT in [0.60, 0.90] on majority of seeds ->
  `RAIL_V1_DOC_BREACH` (couldn't reproduce v1's 0.78 in v1's regime; stage-1 analysis wrong)

(Wider META_M6 rail of [0.08, 0.25] vs prereg ask of [0.08, 0.20]: pointer-chain v2's seed=7 was 0.145,
seed=17 was 0.11, seed=23 was 0.11; mean 0.122; +/-0.05 from the ask brings upper to 0.25 to absorb noise.)

**Mode B verdict ladder (applies only if all three rails PASS):**

- `HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE`:
  - ARM_PARALLEL_K15_PERHOP_5HOP >= 0.70 AND
  - ARM_PARALLEL_K5_PERHOP_5HOP >= 0.50 AND
  - monotonic K1 < K5 < K15 (K1 = ARM_REPRODUCE_POINTER_CHAIN_V2) AND
  - cv_K15 <= 0.07
  - Headline: parallel voting at MATCHED REGIME revives Barrier 1

- `HARD_PASS_PARTIAL_BARRIER_1_LIFT`:
  - ARM_PARALLEL_K15_PERHOP_5HOP >= 0.50 AND
  - monotonic K1 < K5 < K15

- `MIDDLE_BAND_VOTING_MARGINAL`:
  - ARM_PARALLEL_K15_PERHOP_5HOP in [0.30, 0.50)

- `HARD_FAIL_PARALLEL_DOESNT_HELP`:
  - ARM_PARALLEL_K15_PERHOP_5HOP < 0.30
  - At MATCHED regime, K=15 voting doesn't beat single-chain pointer-chain v2 baseline ->
    errors correlate through W; voting can't recover

**Fallback (Mode A scenario; only triggers if Stage-1 was wrong and ARM_CELLX_V1_AS_DOC >> ARM_REPRODUCE
+ math shows Cell X v1 had a better cleanup):**

- `HARD_PASS_BARRIER_1_REVIVAL_VIA_BETTER_CLEANUP`:
  - ARM_CELLX_V1_AS_DOC >= 0.70 AND
  - ARM_REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
  - ARM_PARALLEL_K15 at v1 regime (would need separate arm; not included v2 because Stage-1 ruled this out)

If ARM_CELLX_V1_AS_DOC > 0.70 AND ARM_REPRODUCE is INSIDE [0.08, 0.25] -> the lift is regime not cleanup
(matches Stage-1; Mode B confirmed). The verdict will land in the Mode B ladder; the v1-doc arm just
documents that Cell X v1's number reproduces.

### Config (FULL mode)

- N=8192 (matches pointer-chain v2 + Cell X v1 full intention)
- V_C=200, V_P=10, K_SET=20
- Seeds [7, 17, 23] (apples-to-apples with pointer-chain v2 + Cell X v1 + WM-scaffold + CSP-gated)
- Pointer-v2-regime W: n_chains=200, max_depth=10, ingests 2000 bindings
- V1-regime W: n_chains=50, max_depth=5, ingests 250 bindings
- Test depth=5 in all multi-hop arms (apples-to-apples comparison point)
- REPLICATE_NOISE_FRAC=0.05 (verbatim from v1; per-chain independent Gaussian noise on per-hop key)
- HOP_DEPTHS=[2] for baseline only; deep-chain arms all at depth=5

### Config (SMOKE)

- N=2048, V_C=200, V_P=10, K_SET=20
- Seeds [7] (1 seed)
- Pointer-v2-regime W: n_chains=50, max_depth=10 (kept at depth=10 so smoke W has crosstalk-relevant size)
- V1-regime W: n_chains=20, max_depth=5
- Per-arm test chains: 20 each
- Smoke target for ARM_REPRODUCE_POINTER_CHAIN_V2: in [0.08, 0.40] (wider absorption at smaller N + smaller n_chains;
  the floor stays low; the ceiling expands because smaller W has less crosstalk)
- **Smoke regression-guard:** if ARM_REPRODUCE_POINTER_CHAIN_V2 at smoke > 0.50 -> regime-confound risk;
  flag in smoke log (does NOT block dispatch but prints WARN; full run is the verdict)

### Self-test (runs at module init)

- T1: bipolar / ingest_hebbian / make_deep_chains construction self-consistency
- T2: K=1 noise=0 at v1 regime produces top1 > 5/V (beats chance at small scale)
- T3: K=1 noise=0 at pointer-chain v2 regime produces top1 LESS THAN T2 result (crosstalk hurts; mechanism
  is the same; the asymmetry validates regime is load-bearing) -- WARN-only at module init (test scale
  too small for the asymmetry to be reliable; full run is the verdict)
- T4: K=5 noise>0 produces nonzero mean_diversity (vote mechanism active)
- T5: vote_at_end != vote_per_hop math under noise (protocols are distinct)
- T6: NaN guard on N=4096 production-scale
- T7: bands locked (assert exact numeric values)
- T8: LLM call counter == 0 (substrate-only)

## Estimated runtime

Full mode 3 seeds: pointer-chain v2 ran 384s total (128s/seed for 5 arms). Cell X v2 adds 3 parallel arms
on top of pointer-chain v2's baseline+pointer arms; estimated **~600-700s for full run** (3 seeds, local
CPU, N=8192). Comfortable within local_cpu_queue.

## Routing

- Queue: `local_cpu_queue`
- Timeout: 1800s (3x safety on ~600s estimate)
- Per-experiment self-test BLOCKS dispatch if T1-T8 don't all PASS

## What this cell answers

If pre-reg lands `HARD_FAIL_PARALLEL_DOESNT_HELP` at the matched regime: parallel voting cannot revive
Barrier 1 even when the mechanism is the same as pointer-chain v2; errors through W are correlated. Time
to retire parallel voting as a Barrier 1 candidate.

If pre-reg lands `HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE`: USER-proposed mechanism is chain-grade-
eligible; route to Skunkworks for landed-VET tier classification.

If pre-reg lands `META_M6_RAIL_VIOLATION`: my stage-1 analysis is wrong; ARM_REPRODUCE doesn't reproduce
pointer-chain v2 at IDENTICAL regime. Cell X v2 itself needs re-design; the cleanup-primitive math diff
needs further investigation.

## Risk register

- BIAS-Q (suspect 1.000): if any per-step accuracy hits 1.00 at depth=5 with V_C=200, that's a tell of
  W-saturation / by-construction shortcut; would flag in verdict_msg even on PASS
- BIAS-Q non-monotonic K (K5 > K15): K=5 beating K=15 is a tell that voting isn't the mechanism (more
  votes should be > fewer votes if the math is sound); v1 already showed this pattern (0.86 > 0.82)
- Fix #28: read per-arm metrics not just verdict_msg; per-arm top1 + per-step-acc + diversity reported
  for every arm
- META_M6: this is THE rail; if it breaks, the entire stack of comparisons is uninterpretable
