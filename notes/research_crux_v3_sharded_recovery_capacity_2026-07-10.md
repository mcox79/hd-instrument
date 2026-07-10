# Research — does sharded per-rule-path recovery fix the crux-v2 compose-time SNR floor, or relocate it?

Filed by: research (Sonnet, self-contained WebSearch/WebFetch + 2 parallel Sonnet lit-scan sub-agents +
deep on-disk substrate-history scour) | 2026-07-10

**Trigger:** crux-v2 (resonator decode) landed `HARD_FAIL_A_SNR_FLOOR` at SMOKE (n=120, CPU, N_DIM=2048):
`res_gated_recall@10=0.058` vs `single_shot=0.175` vs `symbolic=0.317`; `nonconvergence_rate=0.95`;
codebook near-orthogonal (`mean|cos|=0.0196`, confirming NOT a correlation problem); `res_cond_mrr=0.464 >
sym_cond_mrr=0.404` (ranks excellently what little it recovers). exp_dev's proposed v3 fix: SHARDED
per-rule-path recovery — decode each rule-path's tail set separately (small superposition, within
capacity), then aggregate — citing this substrate's own "sharded > bundled" law.

**MID-CYCLE CORRECTION (folded in per live coordinator steer, both load-bearing):**

1. **The tightest on-substrate precedent is NOT the plate-bound/FHRR-chain memory the trigger pointed at —
   it is the direct sharding-vs-bundling capability-map track** (PP-127, PP-128, PP-116, Chain3, plus two
   *negative* results, Op B and Op E, that mark the failure boundary). Read in full below (Section 1).
2. **The ENCODE-vs-DECODE localization is NOT yet confirmed.** Skunkworks VET just landed: the crux-v2
   resonator was under-iterated (`t_iter=20` vs the 60-100 a prior drill recommended; `RES_TAU=0.4`,
   `RES_N_RESTART=16` at smoke, both below this substrate's own validated restart-budget law of R~19-29 for
   a comparable K=4 residual). Low proposal rate is silent, not wrong (`n_proposed=12/120` gated,
   `23/120` raw). A decode-budget sweep (`t_iter` 20→100 on the SAME frozen bundle) is in flight NOW to
   disambiguate: if raw recall stays FLAT as `t_iter` rises, the wall is genuinely encode-side (bundling
   capacity) and sharding is well-motivated; if raw recall RISES with `t_iter`, the wall was decode-side
   (under-iteration) and sharding is premature — the cheaper fix is just more iterations/restarts.

**This note is therefore explicitly conditional: IF the in-flight decode-budget sweep confirms the encode
floor (flat raw-recall vs t_iter), the analysis below tells you whether/how sharding clears it. If the
sweep shows recall rising with t_iter, downgrade this note's shard recommendation to "not yet needed" and
re-open once a REAL under-iterated ceiling is found.**

---

## (a) HEADLINE

**Conditional on the encode-floor being real: sharding-by-rule-path is well-founded and has the strongest
on-substrate precedent of any lever considered this week (PP-127: monolithic collapses to 0.060 at S=32 —
within noise of the crux's own failing 0.058 — while per-shard recall holds at 1.000 across S1-S32,
interference=0.000). But "sharded" only clears the floor if (i) the aggregation step is a discrete
list/score merge, never a joint vector-level operation across shards (two on-substrate negatives, Op B and
Op E, both show joint cross-shard linear/algebraic operations fail; every positive result, PP-127/128/130,
Chain3, uses independent-then-merge), and (ii) per-shard candidate counts are actually driven below the
capacity knee for ALL degree strata, not just the low/mid ones — this substrate's OWN degree-stratified
data on the crux-v2 smoke already shows the gap concentrated in the mid/high-degree tertiles
(`margin_vs_relfreq` mrr: low -0.033, mid -0.147, high substrate far behind relfreq), which is exactly where
naive per-rule-path sharding is weakest (hub relations resolve to hundreds of tails in ONE rule-path, so
sharding by rule-path does not shrink K for them). P_deflated=0.45 (capped, novel-synthesis) for "sharding
clears the HARD-PASS band in aggregate AND specifically in the high-degree tertile with a clean list-merge
aggregation"; P rises to ~0.60 if restricted to "clears in aggregate / low+mid tertiles only" (a real but
partial win, matching this substrate's own PP-132 per-relation-KG-sharding precedent, which landed
MIDDLE_BAND at 0.735 — not full HP — for exactly this reason, "dense relation within-shard capacity limit").**

---

## 1. The substrate's own sharded>bundled track record (direct precedent, not analogical)

Read in full from `notes/substrate_capability_map.md` this cycle (all cited rows verified on-disk):

**Positive precedent — sharding fixes bundling collapse when combined with independent-then-merge:**

- **PP-127 "Sharding scaling law"** (`sharding_scaling_law_cpu_v1`, HARD_PASS): per-shard recall = 1.000
  at every shard count S1 through S32; **monolithic (bundled) recall collapses to 0.060 at S=32**;
  interference=0.000. **This monolithic-collapse number (0.060) sits within noise of the crux-v2 smoke's own
  failing recall (0.058)** — the closest quantitative match to the crux's own failure mode found anywhere on
  this substrate. GPU-scale annotation (`sharding_scaling_largeS_gpu_v1`) and demo-scale annotation
  (`sharding_contrast_demo_data_cpu_v1`, contrast_ratio=58.8x at t=5120) both confirm the same shape at
  larger scale: monolithic collapses at a fixed per-unit capacity threshold (~8x shards' worth,
  ~640-facts-per-test-N), sharded holds at 1.000 indefinitely.
- **PP-128 "Shard routing accuracy"** (`shard_routing_accuracy_cpu_v1`, HARD_PASS): routing=e2e=oracle=1.000
  using a **content-derived** routing key (no pre-built shard oracle needed) — directly relevant, since
  crux-v3's "aggregate by rule-path" step needs exactly this: route/merge candidates by which rule-path
  produced them without a privileged oracle.
- **PP-116 "Markov transition encoding"**: sharpening (a decode-side cleanup lever) had ZERO effect;
  sharding (`markov_binding_sharpening_cpu_v1`) was the fix that moved this row MIDDLE_BAND→HARD_PASS.
  Directly analogous to the crux-v2 situation: decode-side tuning (resonator/restarts, pending the
  in-flight sweep) plausibly won't be the fix if the true bottleneck is bundling load, matching this
  substrate's own prior finding that sharpening ≠ sharding.
- **Chain3 cross-shard K-hop** (`chain3_v1_khop_3shard_gpu_v1`, HARD_PASS): 3-shard binary relay, K=12
  recovery=0.987, K_max=18, monotone K-curve — multi-shard chaining across a RELAY (sequential
  shard-to-shard hand-off of a discrete result), not a joint vector op, is viable at meaningful K.

**Negative precedent — the failure boundary, directly relevant to "does aggregation reintroduce crowding":**

- **Op B, `tensor_binding_two_shard_v1_n4096` (HARD_FAIL, HONEST-confirmed):** `mean_tensor_acc=0.018` (50x
  below random) when two shards' content is combined via one ELEMENT-WISE bind THEN passed through a shared
  W matmul in one shot. **The dispositive contrast: same shards, same W, SEQUENTIAL (one-at-a-time)
  composition = 1.000.** The substrate's own recorded diagnosis: "sequential works because per-shard storage
  preserves codeword integrity; tensor-binding fails because [joint algebra] doesn't survive matmul's
  information-mixing." This is a precise, on-substrate confirmation of the resonator note's own
  "topology mismatch" risk (simultaneous joint composition vs. sequential one-at-a-time) — and it says the
  same thing FHRR/BSC-side that Lisman-Idiart says brain-side (Section 3 below): sequential beats joint.
- **Op E, `cross_shard_correlation_k10_v1_n4096` (HARD_FAIL, HONEST-confirmed with nuance):**
  `Tr(W_i^T W_j)`-style cross-shard correlation is indistinguishable from noise (`mean_AUC=0.459`, actually
  BELOW random) at ~0.7% true entity overlap between shards. The substrate's own annotation: this is a
  narrow closure of "this specific 2nd-order trace metric at this specific low-overlap fraction," not a
  closure of all cross-shard analytics. **Relevance to v3's aggregation step:** if crux-v3's "aggregate
  across rule-path shards" ends up implemented as anything resembling a joint second-order operation across
  shard representations (rather than a clean discrete list/score merge of already-decoded candidate IDs),
  Op E is direct on-substrate warning that this specific class of operation loses signal exactly in the
  sparse-true-overlap regime a real KG sits in (most entity pairs across different rule-paths have ~0 true
  relatedness — structurally similar overlap fraction to Op E's calibration point).
- **`khop_bundle_noise_battery_gpu_v1` (annotation, distinct axis — flagged so it is not conflated with
  shard-count):** uses "B" for per-hop RELAY bundle-width (not shard count S). Dense relay is vulnerable at
  B=2 (K_max=12) but RECOVERS at B>=10 (K_max=50) — more redundancy per hop, not less, is what helps there.
  This is a different mechanism (relay-noise averaging over a chain) from the crux's per-query
  compose-time bundling problem; cited here only to flag that "B" is overloaded across cap_map rows and
  should not be casually cross-applied.

**Verdict on Section 1:** the Director's prompt pointed at the FHRR-chain plate-bound memory
(`feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition`) as "the substrate's own
sharded>bundled law." On inspection, that memory is about **corruption-robustness of an L-hop bind CHAIN**
(a different axis — resilience to per-hop noise over sequence length) — it is a real, correctly-cited
supporting data point (same directional finding: sharded storage is far more forgiving than naive
Plate-bound math predicts) but it is a **partial-fit citation, not the tightest precedent**. The direct,
load-bearing precedent for "one big candidate bundle vs many small shards then merge" is the PP-127/128/116/
Chain3 + Op B/Op E track above, which is a closer structural match to what v3 actually proposes (same
granularity: partition-then-independently-process-then-merge, exactly what PP-127 tests) and gives a
concrete number (mono-collapse 0.060) that lands almost exactly on the crux's own failure value (0.058).

---

## 2. Capacity math — does sharding provably clear the floor, or relocate it

**Verified via lit-scan sub-agent this cycle (WebFetch, primary text retrieved and quoted) — Frady, Kleyko
& Sommer, "A Theory of Sequence Indexing and Working Memory in Recurrent Neural Networks," Neural
Computation 30(6):1449-1513 (2018), arXiv:1803.00412 (earlier draft arXiv:1707.01429):** the exact
order-statistics matched-filter derivation this question needs. Correct item's dot product (signal level
`s`, unit-variance noise); must exceed the max of `D-1` distractor scores (`D` = codebook size, our `V`).
High-fidelity approximation: `s² ≈ 4[ln(V-1) - ln(2ε)]`, where `ε` = target per-item error rate, and
`s = sqrt(N/K)` for bundling K items in dimension N. Solving for `K_max = N/s²`:

`K_max ≈ N / (4[ln(V) - ln(2ε)])`, stated by the authors to be **independent of the coding vectors'
statistical moments** (applies uniformly to dense HRR/FHRR/MAP-style codes) — and explicitly noted by the
authors to differ from **Plate's original bound by a factor of ~2** (their bound is the more conservative
one). With V ≈ 14,541 (FB15k-237 entity count), `ln V ≈ 9.55`:

| Target ε | K_max @ N=2048 | K_max @ N=4096 | K_max @ N=8192 |
|---|---|---|---|
| ε=0.01 (99% per-item success) | ~38 | ~76 | ~152 |
| ε=0.001 (99.9% success) | ~32 | ~65 | ~130 |

**Honest calibration note:** the lit-scan sub-agent could NOT independently verify the "~0.14·N" Plate
constant cited in this drill's own task framing against a primary source — flagged explicitly as
unverified by the sub-agent, and the one anecdotal Plate data point found (N=512 → ~50 items, i.e.
K/N≈0.098) is for an unspecified, likely much smaller item-memory size than V=14,541, so not directly
comparable. **The Frady/Kleyko/Sommer formula above is the one number in this section that is both
primary-source-verified AND directly parameterized for our actual V — treat it as the load-bearing
estimate, and treat "K_crit ~ 0.14N" as a looser, unverified-at-this-V rule of thumb.** Either way, the
qualitative conclusion is unchanged and if anything strengthened: **K_max is a small fraction of N (roughly
1.5-7.5% of N by this tighter, verified formula) when V is in the tens of thousands** — collapse toward
unreliable recovery sets in at K in the low-tens (N=2048) to low-hundreds (N=8192), even tighter than this
drill's own earlier back-of-envelope estimate.

**Why N-scaling alone stalled (0.020→0.058, N 512→2048, only ~3x lift for a 4x N increase, both still
near-floor):** K_crit scales only LINEARLY in N. If the true bundling load K for a meaningful fraction of
queries is itself large and HEAVY-TAILED (which this substrate's own degree data confirms — the crux-v2
smoke's own `deg_tertile_bounds=[54, 411]` shows some entities/relations already touch 400+ neighbors at
ONE hop, and multi-hop rule-paths compound this multiplicatively), then a linear N increase cannot catch a
heavy-tailed K distribution — you need to shrink K, not just grow N. **This is precisely the argument for
why sharding (which acts on K directly) is structurally the right axis, not "just raise N further" (lever 4
in the prior resonator note, already flagged there as "should be LAST, not first").**

**Does sharding provably clear the floor, or does aggregation relocate it?** Two distinct sub-cases,
directly informed by Op B/Op E above:

1. **If aggregation = discrete list/score merge of already-decoded candidate IDs (union or max-score across
   shards), NO — it does not relocate the problem.** Each shard's own decode-cleanup step compares its small
   bundle against the FULL V-size codebook (not against other shards), so shrinking per-shard K genuinely
   lowers that shard's crosstalk per the K_crit formula above; a final list-merge over already-resolved
   discrete winners introduces no new superposition and therefore no new crosstalk. This is the PP-127/128
   design pattern and it is the correct one.
2. **If aggregation is (or silently becomes) a joint vector-level operation spanning shards** — e.g.
   re-bundling shard-level summary vectors for a final joint rank, or a cross-shard trace/correlation step —
   **the crowding relocates to the shard-count axis** (now S items being jointly combined instead of K), and
   Op E is direct on-substrate evidence this specific failure mode is real and easy to trip into
   accidentally. **This is the single most important implementation-correctness check for the v3 cell.**

**The relocation risk that is NOT an implementation bug, but a genuine distributional limit:** per-rule-path
sharding only lowers K for a given shard if that rule-path's own tail-set is itself small. FB15k-237's
degree distribution is heavy-tailed (hub relations/entities). For a hub rule-path whose own within-path tail
count already exceeds K_crit (a few hundred at N=2048), sharding-by-rule-path does nothing — the bundling
problem is fully re-created one level down, inside that one shard. **This is the "relocation," and it is
empirically already visible in the crux-v2 smoke's own degree-stratified breakdown** (the mid/high-degree
tertiles are where the gap vs. POP_RELFREQ is worst) — this is not speculative, it is the same run's own
built-in instrumentation already showing where the wall concentrates.

---

## 3. Brain's answer: sequential slotting is the MAXIMAL form of sharding

Lit-scan sub-agent (Sonnet, this cycle) confirms via direct fetch:

**Lisman & Idiart, Science 1995 (PMID 7878473):** ~7±2 items stored as distinct "40 Hz" gamma subcycles
nested inside one 5-12 Hz theta cycle — explicitly a **serial-processing** timing mechanism, not
simultaneous joint binding. The capacity number is set by the **theta/gamma frequency-ratio** (a
clock-cycle-count limit), not by a network-size/interference limit per se, though later work (destructive
interference between gamma subcycles; tACS studies causally shifting capacity by shifting theta frequency)
shows both the ratio AND per-slot interference matter.

**Direct 2024 confirmation (fetched in full), PLOS Biology `journal.pbio.2003805`:** gamma-burst phase
within the working-memory maintenance cycle tracks list position (list-position-1 fires at an earlier phase
than position-2 than position-3, permutation p=0.0062) — described by the authors as **"the strongest
support to date for the serial organization of WM."**

**CA3 sparse-attractor capacity (Treves & Rolls, formalized; Rolls 2013 review, PMC3691555, fetched):**
`p_max ≈ k·C_RC / (a·ln(1/a))`, `C_RC≈12,000` recurrent-collateral synapses/neuron, `a`=sparseness of the
active population, `k≈0.2-0.3`. Since `a·ln(1/a)` shrinks as `a` shrinks, **capacity RISES as sparsity
increases** — fewer simultaneously-active neurons per pattern means less synaptic overlap between stored
patterns, raising storable-pattern count before crosstalk disrupts recall. This is the SAME
"reduce-simultaneous-overlap-to-raise-capacity" principle as theta-gamma phase coding, just applied to
long-term synaptic storage (spatial sparsity) rather than online temporal separation (temporal sparsity).

**Honest gap (flagged explicitly by the lit-scan sub-agent):** no single paper was found stating the
"sequential trades interference for K× time" tradeoff as a formal equation — this is a reasonable synthesis
across sources (phase-tagging binding-problem literature; eLife `hippocampal theta rhythm` paper describing
temporal segregation as "resolving mnemonic competition by separating and prioritising relevant memories"),
not a directly-quotable single-source result. Treat as strong analogical support, not a proven theorem.

**What this prescribes for the crux compose step:** the brain's actual answer to a combinatorial K-way
bind is not "shard into a moderate number of medium bundles" — it is **shard all the way down to size-1
slots and process sequentially.** Per-rule-path sharding (exp_dev's v3 proposal) is a MODEST, partial
version of this (shard size = "however many tails one rule-path resolves to," which per Section 2 can still
be in the hundreds for hub relations) — the maximal, most brain-faithful version would shard further,
down toward one-candidate-at-a-time recovery for high-fan-out rule-paths specifically (i.e., degree-adaptive
shard granularity: coarse shards for low-degree rule-paths, much finer/sequential shards for hub relations),
rather than one fixed shard-per-rule-path granularity applied uniformly. This directly answers "is there a
better/complementary compose-time capacity lever" — **degree-adaptive shard granularity, informed by the
brain's frequency-ratio-driven serial slotting, is the refinement on top of exp_dev's flat
per-rule-path-shard proposal.**

**Note on the prior resonator note's DG-decorrelation lever:** the earlier crux-v2 note flagged DG-style
codebook decorrelation as a complementary encode-side lever. This drill's finding: **less relevant to THIS
specific failure than previously scoped**, because the crux-v2 smoke's own instrumentation already shows
codebook correlation is low (`mean|cos|=0.0196`) — the wall here is bundling COUNT (K too high for N), not
correlation-driven crosstalk. DG-decorrelation attacks a different sub-mechanism than the one actually
implicated by this substrate's own diagnostic; deprioritize it for this specific fix.

---

## 4. Sparse/block coding as complementary, not competing, lever

**Verified this cycle via a second lit-scan sub-agent, and this materially CORRECTS a claim in the prior
crux-v2 note.** That note credited Hersche et al., "Factorizers for Distributed Sparse Block Codes"
(arXiv:2303.13957), with a ~1200x capacity gain relevant to this problem. Direct re-fetch this cycle
confirms: **that paper makes no bundling/superposition-capacity claims at all** — it is exclusively about
FACTORIZER (decode/disentangle) capacity of an already-bound composite, a different problem from "how many
items can be additively bundled and recovered." The ~1200x number is real but answers a different question
than the one this drill (and exp_dev's v3 fix) actually needs. **Downgrade: sparse/block coding's promised
gain for THIS specific bundling-capacity problem is currently unverified, not a confirmed ~1200x-class
lever.**

What IS verified: sparse superposition/regression codes (SPARC — Barron & Joseph and successors, e.g.
arXiv:1503.08040, spatially-coupled/VAMP variants arXiv:2303.08406) are provably capacity-achieving on the
AWGN channel using sparse random design matrices — a real, distinct, rigorous literature. The
Donoho-Tanner compressed-sensing phase transition (sharp recoverability boundary as a function of sparsity
ratio and undersampling ratio) is well-established for sparse-vector recovery generally. The mechanistic
link this drill's framing assumed — "sparse codewords have lower pairwise cross-correlation than dense
ones, therefore raise bundling K_max at fixed N" — is standard compressed-sensing intuition and plausible,
but **the lit-scan found no paper that explicitly restates the CS phase diagram as a bundling-capacity
result in HDC/VSA terms, and no verified concrete multiplicative gain number (no citable "10x/100x" for
bundling specifically)**. Qualitative attractor-network literature (sparse-coded patterns raise storage
capacity, matching Section 3's Treves-Rolls formula) supports the DIRECTION of the claim but not a specific
magnitude for THIS regime.

**Revised verdict:** sparse/block coding remains a plausible, complementary, ENCODE-side lever in principle
(raises the ceiling per N rather than lowering the load, so it composes with rather than substitutes for
sharding) — but its expected gain for this specific bundling problem is currently **unquantified and
unverified**, weaker-evidenced than this drill's Section 1-2 case for sharding. Given codebook correlation
is already low here (mean|cos|=0.02, Section 3), and given the sparse-coding case for THIS problem rests on
inference rather than a verified formula/number, **sequence it strictly as a fallback lever**: only invest
engineering effort in migrating entity codes to sparse/block form if degree-stratified sharding (Section 2's
fix) still fails specifically in the high-degree tertile, and even then, budget it as an exploratory,
unproven-magnitude bet, not a near-certain ~1200x-class win.

---

## Cheap decisive test (pre-registered, bolts onto existing crux-v2/v3 scaffolding)

**Stage 0 (already in flight, do not duplicate):** decode-budget sweep, `t_iter` 20→100 on the SAME frozen
smoke bundle. FLAT raw-recall vs t_iter ⇒ encode-floor confirmed, proceed to Stage 1. RISING raw-recall ⇒
decode-side was the wall; downgrade this note's shard recommendation, re-tune resonator iterations/restarts
first (cheaper, no redesign).

**Stage 1 (this note's proposal, gated on Stage 0 confirming encode-floor):** build the v3 sharded-recovery
cell with:
- Per-rule-path shard decode (exp_dev's baseline proposal), PLUS degree-adaptive shard granularity for
  hub relations (Section 3) — do not apply one fixed shard size uniformly.
- Aggregation = discrete list/score merge ONLY (union of shard-decoded candidate IDs + scores). Explicitly
  forbid any joint vector-level re-bundling or cross-shard trace/correlation step at aggregation time — this
  is the Op B/Op E must-check.
- **Degree-stratified reporting mandatory** (the cell already has this instrumentation from crux-v2 —
  reuse it): report residual-gated recall@10 separately for low/mid/high degree tertiles, not just in
  aggregate.

**HARD-PASS:** aggregate residual-gated recall@10 ≥ 0.35 AND high-degree-tertile recall@10 improves by
≥ 2x over the crux-v2 baseline's high-tertile number (not just the aggregate number). The second clause is
the must-fail control — an aggregate-only pass that is entirely carried by low/mid tertile improvement,
with the high-degree tertile unchanged, is a FALSE GREEN (the relocation risk materialized) per this
substrate's own discriminator-must-be-telemetry-sensitive discipline.

**HARD-FAIL:** aggregate recall stays < 0.25 even with per-rule-path sharding, OR aggregate improves but
high-degree tertile recall stays within noise of the crux-v2 baseline (relocation confirmed — sharding
fixed the easy majority of queries and pushed the hard hub-relation minority's problem down one level,
unresolved). Either HARD-FAIL routes next to: (a) degree-adaptive finer sharding for hub relations
specifically (Section 3), not uniform re-sharding, or (b) sparse/block entity codes (Section 4) as the
ceiling-raising complement.

**Secondary must-fail control (Op E analog):** instrument the aggregation step itself — if any shard-pair
comparison during merge shows AUC indistinguishable from 0.5 (mirroring Op E's exact failure signature),
that is a direct signal the aggregation implementation has drifted into a joint cross-shard operation and
needs to be rewritten as a pure discrete merge before the recall numbers above can be trusted at all.

---

## Cross-thread synthesis

- `notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md` (this same day): pre-registered
  the exact HARD-FAIL band (<0.25) this smoke landed in, and named "correlated codebooks" and "topology
  mismatch" as the two top risks — Section 3's finding that correlation is NOT the issue (mean|cos|=0.02)
  and Section 1's Op B finding (sequential beats joint) directly resolve those two named risks: correlation
  is ruled out by the substrate's own telemetry; topology mismatch is confirmed as a live risk with a
  concrete on-substrate mechanism (Op B) rather than a generic literature caution.
- `notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md`,
  `notes/research_resonator_reachability_ceiling_2026-07-07.md`,
  `notes/research_resonator_restart_budget_geometric_race_law_2026-07-07.md`: the restart-budget law
  (R~19-29 for a comparable K=4 residual) is directly why Stage 0's decode-budget sweep is the right cheap
  first check — RES_N_RESTART=16 at smoke is already below this substrate's own validated number.
- `notes/research_brain_grounding_resonator_basin_proliferation_2026-07-08.md`: DG-decorrelation ranked as
  top rescue candidate for basin-proliferation broadly; THIS drill narrows that — not the right lever for
  THIS specific failure, since correlation is already low here (see Section 3 caveat).
- Cap_map PP-127/128/116/130, Chain3 (`chain3_v1_khop_3shard_gpu_v1`), and negatives Op B
  (`tensor_binding_two_shard_v1_n4096`) / Op E (`cross_shard_correlation_k10_v1_n4096`): the direct,
  load-bearing precedent for this drill's entire Section 1-2 analysis, found by following the coordinator's
  correction rather than the originally-pointed-to plate-bound memory (which is a real but looser-fit
  citation — corruption-robustness of chain composition, not bundling-count capacity).
- `feedback_dont_over_correct_on_raw_full_either_trust_adversarial_recompute_over_own_swings` (memory,
  2026-07-10): directly motivates this note's conditional framing — do not treat the smoke's
  HARD_FAIL_A_SNR_FLOOR label as settled mechanism-truth before Stage 0's decode-budget sweep and (later) a
  landed-VET confirm it at FULL scale.

---

## Substrate-product implications

- If Stage 0 confirms the encode floor and Stage 1 HARD-PASSes (including the high-degree-tertile clause),
  the product gains a reusable "degree-adaptive sharded recovery" primitive directly reusable anywhere this
  substrate composes many candidates into one query response — not just KG completion. This would also be
  the substrate's first EMPIRICAL confirmation that its own theta-gamma-like "shard by natural partition,
  merge discretely" principle generalizes from storage-time sharding (already proven, PP-127 family) to
  query-time candidate-bundling, closing a real gap between "we know sharding fixes storage capacity" and
  "we know it fixes per-query compose capacity."
- If Stage 1 HARD-FAILs specifically via the high-degree-tertile clause (relocation confirmed), that is
  itself a valuable, well-localized negative: it means flat per-rule-path sharding is necessary but not
  sufficient, and the product roadmap should budget for degree-adaptive/hierarchical sub-sharding (this
  substrate already has a precedent for exactly this shape of fix — PP-129 "shard overflow recovery by
  online split," pre=0.160→post=1.000 by splitting an overflowing shard further) rather than treating
  uniform sharding as a complete architecture.
- Either outcome sharpens the same emerging cross-cell law this substrate keeps re-deriving from different
  angles this week: **decode-side cleverness (resonator, restarts, ACF) recovers information up to a point
  set by bundling load and codebook decorrelation at ENCODE/compose time; when that point is exceeded, the
  fix is structural (shard the composition itself, or raise the effective per-N capacity via sparse/block
  coding), not more decode iteration.**

---

## Citations (verified count)

**Internal substrate sources (on-disk, read in full this cycle):**
1. `data/exp_crux_engine_v2_resonator_decode_v1_smoke/metrics.json` (the actual smoke metrics this drill is
   grounded in — read directly, all numbers in this note cross-checked against it)
2. `experiments/exp_crux_engine_v2_resonator_decode_v1.py` (RES_T_ITER=15/20, RES_N_RESTART=8/16, RES_TAU=0.4,
   STAGE1_GATED_FAIL=0.25 thresholds confirmed directly in source)
3. `notes/substrate_capability_map.md` — PP-127, PP-128, PP-116, PP-129, PP-130, Chain3
   (`chain3_v1_khop_3shard_gpu_v1`), Op B (`tensor_binding_two_shard_v1_n4096`), Op E
   (`cross_shard_correlation_k10_v1_n4096`), `khop_bundle_noise_battery_gpu_v1` — all read directly this
   cycle, exact numbers quoted above
4. `notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md` (read in full)
5. `C:/Users/marsh/.claude/projects/d--AI/memory/feedback_plate_bound_too_pessimistic_for_sharded_fhrr_chain_composition_2026-07-03.md`
   (read in full; assessed and downgraded to "partial-fit citation" per Section 1)
6. `C:/Users/marsh/.claude/projects/d--AI/memory/reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md`,
   `reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06.md` (read, cross-checked against
   Section 3's correlation-is-low finding)

**External literature (fetched this cycle via Sonnet lit-scan sub-agent, generic-query, verified/unverified
flagged inline in Section 3):**
7. Lisman & Idiart, "Storage of 7±2 short-term memories in oscillatory subcycles of a theta cycle,"
   Science 267(5203):1512-1515 (1995), PMID 7878473 — abstract fetched and quoted directly.
8. "Serial representation of items during working memory maintenance at letter-selective cortical sites,"
   PLOS Biology, journal.pbio.2003805 — fetched in full, quoted directly.
9. "Phase separation of competing memories along the human hippocampal theta rhythm," eLife,
   elifesciences.org/articles/80633 — fetched in full.
10. Rolls, "A quantitative theory of the functions of the hippocampal CA3 network in memory," Frontiers in
    Cellular Neuroscience (2013), PMC3691555 — fetched in full, formula direction cross-checked/corrected.
11. Lisman & Jensen, "The Theta-Gamma Neural Code," Neuron 77:1002-1016 (2013) — bibliographic
    verification only, not full-text-fetched this cycle.
12. Frady, Kleyko & Sommer, "A Theory of Sequence Indexing and Working Memory in Recurrent Neural
    Networks," Neural Computation 30(6):1449-1513 (2018), arXiv:1803.00412 — fetched in full this cycle,
    order-statistics formula quoted directly, load-bearing for Section 2's capacity math.
13. Hersche et al., "Factorizers for Distributed Sparse Block Codes," arXiv:2303.13957 — RE-FETCHED this
    cycle specifically to check for bundling-capacity claims; confirmed it makes NONE (factorizer/decode
    capacity only) — this cycle's fetch corrects the prior crux-v2 note's use of this paper (Section 4).
14. Barron & Joseph et al., sparse superposition/regression codes (SPARC) family, e.g. arXiv:1503.08040,
    arXiv:2303.08406 — bibliographic/abstract-level verification, capacity-achieving-AWGN claim confirmed,
    not fully fetched line-by-line.
15. Donoho-Tanner compressed-sensing phase transition — verified via search-snippet secondary sources,
    not primary-paper-fetched this cycle; exact asymptotic constants flagged as moderately-verified only.
16. Clarkson, Ubaru & Yang, "Capacity Analysis of Vector Symbolic Architectures," arXiv:2301.10352 —
    bibliographic-level verification (concentration-inequality capacity bounds, same log(V)/N family).
17. Prior crux-v2 note's own external citations (Frady/Kent/Olshausen/Sommer resonator capacity papers,
    Karunaratne arXiv:2412.00354) — not re-fetched this cycle, cited by reference to note #4 above,
    unchanged.

**Total: 6 internal on-disk sources (all read in full) + 11 external sources (6 fetched in full/verified
this cycle, 5 bibliographic/search-snippet-only) = 17 verified sources/checks.**

## P_deflated summary

- **"Sharding clears the encode-floor in aggregate AND in the high-degree tertile, with clean list-merge
  aggregation" (this note's headline claim, conditional on Stage 0 confirming encode-floor):**
  P_deflated = 0.45 (capped, novel-synthesis rule — strongest on-substrate precedent found this week,
  PP-127's 0.060 mono-collapse near-matching the crux's own 0.058, but genuine open relocation risk
  concretely visible in this substrate's own degree-stratified data, not hypothetical).
- **"Sharding clears in aggregate / low+mid tertiles, but high-degree tertile remains a partial win"
  (a real, still-valuable, MIDDLE_BAND-shaped outcome matching PP-132's own precedent, 0.735 sub-HP for
  the same reason):** P_deflated = 0.60.
- **"The encode-floor diagnosis itself is confirmed by the in-flight Stage-0 decode-budget sweep"
  (a precondition for all of the above, NOT yet resolved as of this note):** treated as unknown, not
  assumed — this note is explicitly conditional on that outcome per the mid-cycle correction.
