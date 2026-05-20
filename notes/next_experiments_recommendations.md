# Next experiments — recommendations from capability synthesis

Written by capability-synthesis session. Updated against
`substrate_capability_map.md` v3 (2026-05-20 09:00).

The main session decides what to queue. This file is the ordered
shopping list with reasons; treat priority numbers as the synthesis
session's view, not a binding order.

## Priorities — top of queue

### Priority 1: ICL saturation curve (CLOSE A KILLER GAP)
**Question**: where does substrate ICL gain saturate as N grows?
v2 measured ALPHA=0.3 N=2048 (+1.63 bpc) and ALPHA=1.0 N=256 (+3.19 bpc).
The kNN-LM literature predicts log-linear gain through 10^9 entries;
our substrate's saturation point is unmeasured.

**Experiment**: `wave14d_icl_via_pool_v3_scaling`
- ALPHA=1.0 (pool-only), sweep N ∈ {64, 256, 1024, 4096, 16384}
- 3 seeds per N
- Pre-registered prediction: log-linear gain through N=4096, possible
  knee somewhere between N=4K-16K once P approaches d / log d ≈ 480
  (per Frady-Sommer overfill knee at our N=4096 substrate).

**Why now**: ICL just became a Tier-1 ✅ capability. We need its
scaling envelope before we can sell "substrate scales like kNN-LM"
as a product story. ~1-2h on GPU.

### Priority 2: RSB tree-walk algorithm (ACTIVATE A LATENT CAPABILITY)
**Question**: does the substrate's measured ultrametricity translate
to working O(log P) retrieval recall?

**Experiment**: `wave14f_rsb_tree_walk_v1`
- Build single-linkage MST on a P=4096 pool (cophenetic distance from
  bipolar overlap matrix, per wave14f_rsb_tree_walk_research.md)
- Implement priority-queue beam search with b ∈ {1, 2, 4}
- Compare against brute-force cosine and against random-leaf baseline
- Primary metric: recall@1 and recall@10 vs exact NN, query time
- Pre-registered prediction (from research synthesis): at our
  ultrametric-fraction 0.357 (partial-tree regime), recall@10 ≈
  0.7-0.85 at b=2, rising sharply with b.

**Why now**: structural finding is in hand; algorithm is unbuilt;
1-day build per the research synthesis. If it works, the substrate
ships with a free hierarchical index — a Tier-1 KILLER moves fully
to ✅. If it fails at the predicted recall, that's a real-axis
distinction from "RSB measured" to "RSB usable."

### Priority 3: Generation v2 at higher K with strict baseline
**Question**: does generation quality scale with K, or peak at K=16?

**Experiment**: `wave14d_generation_v2_K64` + `_K128` + `_K256`
- Same v2 protocol (B3 Markov-chain baseline, k4_validity threshold)
- 3 seeds each
- Pre-registered: monotone improvement through K=64, possible peak
  K=64-128 (matches R10 curve shape)

**Why now**: v1 showed generation works at K=4/8/16 but only against
random baseline. v2 strict-baseline confirmation lives only at K=16.
This is the obvious extension and uses existing infrastructure.

## Priorities — second tier (close UNSURE killers)

### Priority 4: Edit-then-query end-to-end pipeline
**Question**: given user uploads correction "X is actually Y," does
the next query reflect it?

**Experiment**: `wave14d_edit_then_query_v1`
- Multi-stage: decompose pool entry → swap target byte → rebundle →
  rerun query that originally returned old answer
- Measure: % of queries where update propagates correctly
- 3 seeds, 100 edit-query pairs

**Why now**: edit primitive ✅, query primitive ✅, but pipeline
integration untested. Tier-1 KILLER with the highest-product-leverage
gap — fact-correction is the LLM's biggest current weakness, and
substrate looks like it solves it natively. Worth ruling in or out.

**Research note exists**: `wave14d_edit_then_query_research.md` —
review for implementation details.

### Priority 5: Multi-task transfer beyond A→B
**Question**: continual learning confirmed for A→B distribution
shift on same corpus. What about A → genuinely different domain C?

**Experiment**: `wave14d_multi_task_cl_v1`
- A=current corpus, B=current shift, C=different domain (e.g. code,
  formal language, structured data) — `wave14d_multi_task_cl_research.md`
  has design candidates
- Sequential: Phase A → Phase B → Phase C
- Measure: retention of A, retention of B, learning of C
- Use confirmed random-replay mechanism throughout
- 3 seeds

**Why now**: continual-learning capability claim is currently
"single-shift only." Product claim "LLM that genuinely learns from
interactions" requires multi-domain. Higher-risk than priority 4 but
higher-leverage if positive.

## Priorities — third tier (mechanism / framework)

### Priority 6: 3-factor binding design-space mapping
**Question**: with B=3 cliff at K/N≈0.31, which previously-planned
capabilities survive the new constraint?

**Action item (not an experiment)**: re-audit experiments_backlog.md
+ design notes for any 3-factor binding designs (polarity-tagged,
temporal-tagged, mode-tagged). Mark which ones now have K-cap
≈1270 at N=4096 and adjust their feasibility.

**Why now**: B=3 cliff finding is fresh and capability-bounded.
Cheap audit; prevents queueing experiments that can't reach their
claimed K range.

### Priority 7: SSH-BSC topological winding (Tier-2 KILLER probe)
**Experiment**: `wave14e2_ssh_bsc_topological` — already queued in
v2 but not yet run. 30-min CPU test.

**Why now**: low-cost probe of a Tier-2 KILLER (integer
winding-protected memories). If positive, opens a categorical
noise-immunity story; if negative, closes one direction cleanly.
Bounded downside, structured upside.

### Priority 8: Multi-hop reasoning v2 (UNSURE → ?)
**Experiment**: `wave14e_multi_hop_v2` — queued, not yet run.
- Encode facts as e = subj * rel * obj, superpose into M
- Probe with per-hop cleanup
- Per research: 50+ hops viable with cleanup

**Why now**: cheap-ish (1-2h GPU), tests a Tier-2 KILLER cleanly.

## Gaps without queued experiments

These are capabilities I cannot yet propose a clean test for; flagging
so main session knows the unknown unknowns:

1. **Compositional generalization** — novel combinations of learned
   concepts. No clean held-out compositional eval designed.
2. **Calibration / uncertainty** — does the substrate's softmax temp
   match epistemic uncertainty? Tested implicitly by ICL gain but no
   direct calibration probe.
3. **Sleep-style memory consolidation** — offline replay-during-
   quiescence experiment ungated by the random-replay positive (which
   was online during Phase B, not quiescent).
4. **Self-supervised concept discovery** — without PPMI prior.
   Open since v1.

## Conflicts / things to watch

### Conflict: R3 status across notes
The map closes R3 at K≥16. STATE_2026_05_19.md and the overnight log
still carry "R3 +0.032" as a positive low-K finding. Both are right:
the substrate has a real K=4 R3-Laplace effect, but it's *literature-floor
small-effect, not substrate-unique*. Documentation drift risk if main
session pulls from older notes.

### Conflict: cpu_platform_timing inconclusive
v1 map had cpu_platform_timing 🟡 (cpu_platform_timing_redo timed out
at 3600s). Has it been re-run since the WMI runner repair? If yes and
positive, → ✅. If still hung, the consumer-CPU claim is unverified.
Recommend a clean re-run as a Priority 1.5 if not done.

### Conflict: K=2944 dip retraction
Earlier notes (overnight_log up to cycle 3) cite the 50%/61% dip as a
real cliff substructure. v3 retracts it. Old characterizations of
the K-cliff substructure should be searched and updated when relevant.

## Anti-recommendations (do not queue)

- **R3 rescue variants** — closed, mechanism understood, K-flat.
- **Compound interventions sharing W-drift correction** — closed by
  four-argument convergence.
- **MIR-style priority replay** — closed by rank-equivalence math.
- **Iterative Hopfield as label readout** — protocol mismatch closed.
- **C3 factored vs C1 classical** — retracted lambda artifact.
- **Pre-shift bpc improvements** — wrong goal per pre-shift research.
  The substrate is at hygiene-pass on pre-shift; product stories live
  at post-shift / BWT / decomposition / K-scaling.

---

## Summary for main session

Top three experiments to queue (in priority order):

1. **`wave14d_icl_via_pool_v3_scaling`** — N sweep at ALPHA=1.0 (1-2h GPU)
2. **`wave14f_rsb_tree_walk_v1`** — single-linkage MST + beam search (1-day build, CPU)
3. **`wave14d_generation_v2_K64`** through K=256 — strict-baseline generation curve (2-3h GPU)

These three close the highest-leverage gaps in the v3 map: ICL
saturation, RSB algorithm, generation-K curve. After they land, the
Tier-1 KILLER board would be 4-5 out of 6 ✅, which is a different
product than "memory backend."
