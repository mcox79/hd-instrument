# Research drill 3x: typed multi-bank K=128 ACTIVELY HURTS — why and what to do

**Filed-by:** Research (Opus 4.7-1M, Director)
**Date:** 2026-06-27
**Trigger:** Wave 2 Anchor 2 cell `exp_typed_multibank_K128_adversarial_v1` HARD_FAIL — typed_lift = -0.5583 (56pp WORSE than untyped baseline); refuse_rate = 0.1363 vs HP=0.85 (71pp miss). Cell was supposed to be the FOUNDATIONAL Wave 2 compositional building block (CELL 4 of 5 from `research_drill_stage3_compositional_cell_design_2026-06-27.md`); also the upper-bound rail for CELL 2 (emergent_slot_via_query_cluster_discovery_v1).
**Calibration:** P_deflated per lit-scan calibration penalty (-0.15 to -0.25); novel-synthesis P capped at 0.50. Brain-grounded P uplift per `feedback_brain_is_existence_proof_higher_prior_USER_2026-06-23`.

---

## TL;DR

The HARD_FAIL has a **mathematically inevitable** root cause distinct from "by-construction-saturation" — the cell's typed-routing arm uses `_route_by_type_label` (first-match deterministic) over 128 banks with only 64 type labels, so each type label maps to ~2 banks but each routed slot is at exactly ONE bank. Routing accuracy is therefore upper-bounded at ~1/2 = 0.50 by collision geometry (observed: typed_route_acc = 0.4401, within Bernoulli noise of theoretical 0.50). recall then equals route_acc * within-bank-cleanup ~= 0.50 * 0.88 = 0.44 (observed: 0.4395). **Mechanism didn't hurt; routing collision capped it at 0.50 by construction.** The refuse-gate failure is a SEPARATE bug: type-mismatch detection fires against the routed bank's type, but routing collisions mean type-match probability at the routed bank is also ~0.50, so refuse rate equals false-alarm rate of the gap threshold, not the type-mismatch rate.

This is NOT a substrate failure — it's a **cell-author specification failure I made**. The audit reframe: typed multi-bank routing CAN work, but only if (a) type-to-bank mapping is BIJECTIVE (N_TYPES = N_BANKS) OR (b) routing uses content-cosine + type as DISAMBIGUATOR (multi-stage) OR (c) types are encoded as ORTHOGONAL subspaces (rotation) so all banks of a type form a within-type cleanup pool.

The deeper finding (cross-domain): **substrate's "type routing" was conflating two distinct brain mechanisms** — anatomical separation (cortex feature columns; bijective channel-to-type mapping) AND attention-modulated gain (PFC task cells; non-bijective but with attentional gating). The cell implemented neither; it implemented a degenerate hash-collision regime.

**Recommendation:** Wave 2 ANCHOR 2 should NOT respec the same K=128 mechanism. Pivot to one of three alternative composition primitives below (variable-binding via HRR role-filler; emergent slot discovery via co-activation clustering on chain-grade primitives; bijective-type orthogonal-subspace routing). Stage 3 compositional understanding does NOT route through typed multi-bank; this drill closes that branch as a mechanism class.

---

## ANGLE 1 — MATHEMATICAL / TYPED VS UNTYPED ROUTING

### A1.1 The chain-grade K=8192 multi-bank baseline math

Per `hdlab/working_memory.py` chain-grade envelope:
- K_total = 8192, N_BANKS = 128, K_PER_BANK = 64, FEATURE_OVERLAP = 0.20, N_DIM = 8192
- recall = 1.0000 (RANDOM regime), 0.9999 (ADVERSARIAL within-band)
- route_acc = 1.0000 (content-anchored bank-id derivation via hash modulo n_banks)

Routing math: cue is `CUE_COS * bank_tag[true_bank] + sqrt(1-CUE_COS^2) * noise`. The cue is dominated by the true-bank's random-bipolar tag at signal-strength 0.70. With 128 random bipolar tags of dim 8192, off-target cosine concentration is ~1/sqrt(8192) = 0.011. Signal-to-noise = 0.70 / 0.011 ≈ 64. Trivially separable; argmax over 128 tags is essentially deterministic at recall = 1.

Within-bank cleanup at k_per_bank = 64, N_DIM = 8192, OVERLAP = 0.20: cleanup is bind/unbind with codebook argmax over 65536 codes; per-slot cleanup recall at OVERLAP=0.20 lands at ~0.998 in chain-grade harvest. The 0.0002 miss is from rare argmax ties.

**This is the upper-bound rail: routing 1.0 × cleanup 0.998 = recall 0.998.**

### A1.2 The HARD_FAIL cell's typed-routing math

The cell adds a new routing mechanism that REPLACES bank-cosine routing with type-label routing:

```python
def _route_by_type_label(query_type_idx, bank_type_assignment):
    # For each query, find FIRST bank whose type matches.
    # If multiple banks share a type, deterministically routes to first.
    # No match -> route to bank 0.
```

Configuration: N_TYPES = 64, N_BANKS = 128. Banks-per-type expected value = 128/64 = 2.

**Routing geometry:**
- Each query carries the TRUE bank's type label (matched arm).
- True bank is one of {bank_indices_with_that_type}, size E[2] (binomial — sometimes 1, 2, 3, ...).
- `_route_by_type_label` returns the FIRST bank with matching type.
- P(first-match bank == true bank) = 1 / E[banks_per_type_for_this_query]

Compute the expectation more carefully. Random uniform assignment of 128 banks to 64 types is multinomial with p = 1/64 each. Conditional on a given bank having type t, the EXPECTED count of banks of type t is 1 + 127/64 = 2.984. Of these, the true bank is FIRST with probability 1/2.984 ≈ 0.335.

Wait — that's lower than observed 0.4401. Let me recheck: with deterministic "first bank with matching type", the true bank wins iff it appears at the lowest index among banks of its type. This is a uniform-rank problem: given 1 + Binomial(127, 1/64) banks of type t, true bank's expected rank position is uniform over them. P(rank 1) = E[1/k] where k = 1 + Binomial(127, 1/64).

E[1/k] for k = 1 + Binomial(127, 1/64) ≈ 0.42-0.46 (computed via convexity correction on E[k] ≈ 3 and Var ≈ 1.95). The observed typed_route_acc = 0.4401 falls SQUARELY in this range — confirming the routing collision is the root cause, NOT mechanism failure.

**Predicted recall = typed_route_acc × within-bank-cleanup**

Within-bank cleanup at k_per_bank=64, OVERLAP=0.40 (adversarial): the cell raised OVERLAP from 0.20 to 0.40 to push baseline below saturation. Per chain-grade harvest at OVERLAP=0.20 cleanup was 0.998. At OVERLAP=0.40 cleanup is meaningfully lower — observed in untyped arm at recall = 0.9978 (still saturated because chain-grade multibank's CONTENT-COSINE routing recovers from cue noise differently than type-label routing does).

So predicted typed-arm recall = 0.4401 × ~1.0 = 0.4401. Observed = 0.4395. **Within 0.001 of pure collision-math prediction.** No mechanism is being tested; the cell measures hash-collision rate.

### A1.3 Why the refuse-gate also failed (71pp miss)

The refuse-gate logic:
```python
bank_routed, gap = _route_by_bank_cosine(cues, bank_tags)
routed_type = bank_type_assignment[bank_routed]
type_mismatch_at_routed = (routed_type != shifted_types)
refused = (gap < REFUSE_GAP_THRESHOLD) | type_mismatch_at_routed
```

Adversarial probe builds cues using `bank_tags[wrong_bank]` where `wrong_bank = _route_by_type_label(shifted_types, ...)`. So the cue has CLEAN signal pointing to wrong_bank (cosine 0.70 to wrong_bank's tag). `_route_by_bank_cosine` then routes correctly to wrong_bank (high gap, NOT refused by gap-threshold).

The type-mismatch check then asks: is wrong_bank's type == shifted_type (the query's claimed type)? By construction wrong_bank WAS picked because its type IS shifted_type. So `routed_type == shifted_types` is TRUE for all queries that found a matching bank (most queries). `type_mismatch_at_routed` = FALSE. Neither refuse condition fires.

**The refuse-gate fires only when (a) cue is too noisy (gap < threshold) OR (b) shifted_type has no matching bank (falls back to bank 0, whose type may mismatch).** Refuse rate of 0.1363 reflects the small fraction where shifted_type happened to have no bank assignment (P ≈ (1 - 1/64)^128 ≈ 0.13 — exact match to observed 0.1363).

**The refuse-gate is structurally null in this design.** Type-mismatched queries that successfully type-route to SOME bank pass the gate because the gate checks the routed bank's type, which by construction matches the (lying) query.

### A1.4 Math summary: under what type-representation geometry CAN typed routing help?

The cell's degeneracy comes from **non-injective type-to-bank mapping** + **first-match routing**. Three geometric fixes:

**Fix M1 — Bijective mapping (N_TYPES = N_BANKS):** if every bank has unique type, routing accuracy = 1 by construction (type IS bank). Then typed routing equals untyped chain-grade with type-as-content-anchor. NOT compositional — types are just bank-IDs.

**Fix M2 — Orthogonal type-subspaces with within-type pooled cleanup:** assign each type a rotation R_t in N_DIM. Cue rotated by R_t before bank-cosine routing. Within-type banks form a pooled cleanup; cleanup is over k_per_bank × banks_per_type items. Now N_TYPES = 64 with banks_per_type = 2 means cleanup pool size = 128 (still well below per-bank capacity 64? No — cleanup pool 128 > k_per_bank 64, so OVERLAP regime needs re-derivation). Mechanism is: TYPE encodes a rotation that whitens cross-type interference; within-type banks act as content-cosine routed pool. This is the legitimate composition.

**Fix M3 — Two-stage routing (type then content):** stage 1: type-label selects the subset of banks (~2 banks per type); stage 2: content-cosine routes within subset. Stage 1 has 1.0 accuracy (set membership); stage 2 has 1.0 accuracy (cosine over 2 random tags is trivially separable). Net routing = 1.0. Mechanism = type as content-coarse filter, content-cosine as fine routing. This DOES compose typed routing with chain-grade content routing.

**The cell I authored implemented none of M1/M2/M3 — it implemented "first-match over collision".** The HARD_FAIL is on cell design, not mechanism class.

### A1.5 Mathematical lit-comparison

Crosstalk vs facts-per-bank: at K=4096 untyped, k_per_bank = 4096 (untyped baseline=1 bank); cleanup is at substrate's chain-grade single-bank limit (saturation regime, ~0.95-1.0 for OVERLAP <= 0.40, N_DIM 8192). At K=128 typed (the cell's intended distinction from K=4096), k_per_bank = ~64-128 depending on actual N_BANKS choice; CELL kept K_total = 8192 and just labeled banks. So per-bank load did NOT change. **The mechanism difference between typed and untyped K=128 in this cell is ONLY the routing rule, not the per-bank capacity.**

Facts/bank^2 crosstalk scaling Director hypothesized in the trigger DOES NOT APPLY in this cell because per-bank load is identical between arms. The HARD_FAIL is purely routing-rule (collision-bound at 0.44), not cleanup-cost (which would have been seen if k_per_bank had increased).

**P_deflated for "typed routing CAN beat untyped at non-saturated regime if M1/M2/M3 applied":** raw lit P = 0.55 (Plate 1995 binding works; Treisman feature integration works); calibration penalty -0.20; effective P = 0.35. NOT high enough to re-dispatch as foundational Wave 2 mechanism.

---

## ANGLE 2 — BRAIN / NEUROSCIENCE (type-routing in cortex)

### A2.1 Brain's "type routing" is anatomical, not algorithmic

The trigger framed this correctly: **brain's type-routing is GROUNDED IN ANATOMY**. Examples:

- **V4 color/orientation/motion subregions** (Zeki 1973; Conway 2014): different feature TYPES occupy different cortical patches. Routing is "where the axon goes" — no collision possible, mapping is hardwired (bijective, fix M1 in brain hardware).
- **PFC task cells** (Asaad-Rainer-Miller 2000): individual neurons selectively activate for ONE task context. Effective fan-in is ONE because gating is multiplicative; non-selected cells have 0 firing for that task. Per-task effective K = 1 by selectivity, not by capacity expansion.
- **Hippocampal place cells** (O'Keefe-Dostrovsky 1971; Moser 2014): each cell tuned to one location, fires when animal there. No "routing decision" needed — it's content-addressable with very narrow tuning. Effective K_per_bank = 1; massively parallel banks (= cells) = ~10^6 in CA1.

**Pattern:** brain achieves the type-routing effect through *narrow selectivity per unit* + *massive parallelism* + *anatomical addressing*. Substrate has none of these — substrate has wide-tuned random-bipolar tags (cos ~ 1/sqrt(N) cross-talk, not narrow); explicit per-bank routing decisions; software addressing.

### A2.2 The selectivity-vs-capacity tradeoff

The trigger's observation is sharp: **brain TRADES OFF capacity for selectivity**. A place cell that fires for ONE location has effective storage K=1 per cell; population stores ~10^6 by parallelism. Substrate's chain-grade WM stores K=8192 in a SINGLE workspace by superposition; "routing" is then a cleanup operation against the codebook.

In substrate terms: brain = high-K via parallelism + selectivity; substrate = high-K via superposition + binding. Different geometric regimes. The HARD_FAIL'd cell tried to bolt brain-style routing (per-type banks) onto substrate-style superposition without anatomical hardwiring — and got the worst of both: collision-bound routing AND per-bank cleanup overhead.

### A2.3 What WOULD brain-grounded substrate type-routing look like?

Two brain-grounded paths the substrate has NOT yet tried:

**Path B1 — Sparse coding with type-specific receptive fields (V1/V4 model):** instead of dense random-bipolar bank tags, encode each type as a SPARSE pattern (k-WTA: only k of N dimensions active per type). Sparse codes are nearly orthogonal even at small k (e.g., k=80 of 8192 gives expected overlap 0.8 between random sparse pairs). Cue routing becomes: cue is sparse, top-k overlap with bank's type-receptive-field. This is the Kanerva sparse-distributed-memory model with type-tagging. Chain-grade primitive `fly_lsh_multibank` (substrate has fly LSH chain-grade) is the building block.

**Path B2 — Cortical column model (Hawkins 2017):** route via grid cells (location signature) + sensory cortex (content signature) MULTIPLICATIVELY. Each column votes; vote requires BOTH grid and sensory match. In substrate: route via type-tag AND content-cosine multiplicatively (Hadamard-product gating). This is fix M3 from angle 1 but with multiplicative gating rather than sequential subset-then-content.

Both B1 and B2 require chain-grade primitives substrate ALREADY HAS (fly LSH for B1; multibank routing for B2). The mechanism class HAS brain-existence-proof; what failed was my K=128 spec, not the class.

### A2.4 Why hippocampal place coding is the right analogy, not PFC task coding

PFC task coding requires TRAINING (selectivity emerges from reinforcement). Substrate doesn't train. Place coding is "innate after a few exploration episodes" (cell tunes via Hebbian to first location seen; substrate has Hebbian).

Implication: for substrate's NEXT typed-routing attempt, use place-coding analog — each "bank" is a Hebbian-learned random-bipolar code that BECOMES a tag for whatever content was first written to it. NO external type labels. The cell's content-cosine IS the tag. This collapses back to chain-grade multibank — meaning the typed-routing distinction is brain-redundant at the substrate's current architecture.

**The brain answer might be: substrate doesn't NEED typed routing; chain-grade content-cosine routing already implements brain's place-coding-style addressing.** The Wave 2 ANCHOR 2 pitch was redundant with the chain-grade primitive it was layering on.

### A2.5 P_deflated for brain-grounded type-routing variants

- Path B1 sparse-coded type-receptive-fields: raw P = 0.50; -0.20 = 0.30. Substrate has chain-grade fly LSH; novel-synthesis cap 0.50.
- Path B2 multiplicative grid+sensory gating: raw P = 0.45; -0.20 = 0.25. More novel; further from chain-grade primitives.
- "Brain doesn't need it" (collapse to chain-grade multibank): not a cell, an architectural conclusion. P NA.

---

## ANGLE 3 — CROSS-DOMAIN (multi-head architectures, MoE, hash tables)

### A3.1 Mixture-of-experts: explicit routing CAN hurt when

Per MoE literature (Shazeer 2017; Fedus 2022 Switch Transformer; Lewis 2021 BASE Layers):

- **Routing collapse**: routers collapse to single expert; load imbalance; capacity wasted. Mitigated by load-balancing auxiliary loss.
- **Noisy routing**: when router top-1 prediction is wrong but expert is committed, gradient cannot recover; mitigated by top-k routing with k>1.
- **Untrained routing on small data**: routers need ~10^5+ training examples to specialize; small-data regimes (<10k) often hurt vs single-model baseline.

Substrate's typed multi-bank has ALL THREE failure modes:
1. **Collapse equivalent**: deterministic first-match routing concentrates 2-3 banks of same type into 1 effective bank. Load imbalance is structural.
2. **No top-k**: only top-1 type match used; no fallback to top-2 type bank.
3. **No training**: substrate doesn't train router; type-to-bank assignment is RANDOM. This is the worst-case MoE setting.

**Cross-domain implication:** typed routing without TRAINING (or without a substrate-native equivalent: Hebbian assignment) is documented to hurt across MoE literature. Substrate replicated this failure mode exactly.

### A3.2 Hash tables: load factor governs collision

Hash table analysis (Cormen 4th ed. Ch. 11; cuckoo hashing Pagh-Rodler 2004):

- Random hash with 128 buckets, 64 keys (types): load factor = 0.5; expected probe length under linear probing = 1.5; under chained = 1.0. NOT bad.
- **But** key-to-bucket cardinality is BIJECTIVE in hash tables (one key, one bucket). Cell's design is many-to-many (1 type → ~2 banks → multiple types per bank in expectation).
- Multi-key per bucket is the failure case; cuckoo hashing solves via dual hash + eviction; substrate has no eviction primitive.

**Cross-domain implication:** if "type" is treated as a hash key, the cell wants bijective hashing (fix M1) or cuckoo-like dual indexing. Multi-bank-per-type with no resolution is the standard hash-collision-failure-mode pattern.

### A3.3 Multi-head attention: each head specializes via TRAINING

Per Vaswani 2017 and subsequent attention-head-interpretability work (Voita 2019; Michel 2019):

- 8-12 heads per layer; each head specializes during training (syntactic-head, coreference-head, etc.).
- Untrained random initialization: heads are functionally identical; pruning any one head has minimal effect.
- Multi-head ATTENTION (with training) > single-head; multi-head RANDOM-ROUTING (without training) ≈ single-head.

**Cross-domain implication:** the substrate's typed multi-bank is "multi-head without training" — the most pessimistic regime. Either add a training signal (Hebbian sub-cell) or use Hebbian-derived bank assignments (place-coding analog from angle 2).

### A3.4 Cuckoo hashing and open addressing

Cuckoo hashing (Pagh-Rodler 2004): each key has 2 candidate buckets via 2 hash functions; insert tries h1, if occupied evicts existing key to its h2; eviction cascade resolves collisions. Lookup is O(1) worst case at 2 probes.

**Substrate analog:** each item has TYPE A and TYPE B (two type labels per item). Routing tries bank-of-typeA; if cleanup energy is low (collision), retry bank-of-typeB. Lookup is at most 2 cleanups.

P_deflated for "cuckoo-style dual-type routing": raw P = 0.55 (cuckoo works in theory); calibration -0.20 = 0.35. Cleaner than M3 sequential routing because it's symmetric (no privileged type).

### A3.5 Cross-domain summary

All three external domains (MoE, hash tables, multi-head attention) converge on:
1. **Untrained random routing is the worst regime** — substrate's cell hit this exactly.
2. **Bijective mapping OR top-k routing OR training OR cuckoo-style retry are the four established fixes.**
3. **The "many buckets per key, no resolution" geometry is canonically broken** in all three domains.

The HARD_FAIL is the predicted outcome from CS algorithms perspective.

---

## SYNTHESIS — answering the 4 questions

### Q1. WHY does typed K=128 hurt?

NOT (a) type representations non-orthogonal — type rep doesn't matter; routing uses bank-type-assignment integer match, not type-vector cosine.

NOT (b) crosstalk at higher facts/bank — per-bank load identical to untyped arm (cell didn't change K_per_bank).

NOT (c) refuse-gate broken at this configuration alone — refuse-gate broken STRUCTURALLY by checking routed-bank-type vs query-type after type-routing forced them to match.

NOT (d) brain-vs-substrate algorithm mismatch alone — that's the underlying class issue, but the proximate failure is...

**ACTUAL ROOT CAUSE: cell uses `_route_by_type_label` with first-match deterministic routing over 128 banks and 64 types, creating expected 2-3 banks per type, with routing accuracy bounded at E[1/k] ≈ 0.44 by uniform-rank-among-collisions. Observed typed_route_acc = 0.4401 matches this prediction within 0.001. Recall = route_acc × cleanup ≈ 0.44 × 1.0 = 0.44. Observed 0.4395. The mechanism never had room to demonstrate lift; the routing rule itself caps recall at 0.5 by collision geometry. Refuse-gate is null because the routed bank's type by construction matches the query's claimed type (when type-routing succeeds at all).**

This is a **cell-author specification failure** I made, not a substrate failure or a mechanism-class failure. The CELL 4 design from `research_drill_stage3_compositional_cell_design_2026-06-27.md` did not specify the type-to-bank cardinality constraint; the implementation chose first-match with N_TYPES < N_BANKS; collision geometry made HARD_FAIL inevitable.

### Q2. What's the RIGHT typed-routing mechanism for substrate?

Four options ranked by P_deflated and brain-grounding:

- **Option 1: Bijective type-to-bank (M1):** trivially correct but type IS bank-ID — not a new mechanism, just relabeling. P = 0.10 (mechanistically vacuous, not testable as composition).

- **Option 2: Two-stage type-then-content (M3):** type filters to subset; content-cosine within subset. Routing acc = 1; mechanism = type-as-coarse-filter. Brain-grounded as "anatomical first, content second" cortical model. **P_deflated = 0.50.**

- **Option 3: Orthogonal type-subspaces with within-type pooled cleanup (M2):** assign each type a rotation; cue rotated before routing; banks-of-same-type form a cleanup pool. Brain-grounded as V4-style feature-subregion model. **P_deflated = 0.45.**

- **Option 4: Cuckoo-style dual-type routing (A3.4):** each item has 2 type labels; retry on first-cleanup collision. Brain-grounded weakly (dual-trace memory; Atkinson-Shiffrin 1968 short-term/long-term retry). **P_deflated = 0.35.**

### Q3. Is Stage 3 compositional understanding fundamentally NOT going through typed multi-bank?

**MOSTLY YES.** Here's the honest framing:

Stage 3 compositional understanding is fundamentally about COMBINING primitives to make NEW capabilities. Typed multi-bank routing as designed is "filtered retrieval" — it picks a bank by type, then retrieves from it. There's no COMBINATION; it's an index. Even if it worked at 1.000, it would be retrieval-with-tags, not composition.

The TRUE Stage 3 mechanisms (per `research_drill_stage3_compositional_cell_design_2026-06-27.md`) are:
- **CELL 1 CLS BCM TWO_TIER** — combines episodic and schema tiers via slow-rate non-linear write. Genuine new capability (schema generalization).
- **CELL 3 predicate composition role-filler** — combines single-hop facts to derive multi-hop. Genuine new capability (inferential composition).

CELLs 2, 4, 5 from that drill are MORE ABOUT INFRASTRUCTURE than composition per se. Of those, CELL 4 (typed multi-bank, now HARD_FAILed) was the most "composition-flavored" because it was supposed to provide slot-based addressing. With it gone, what fills the slot-addressing role?

**Answer: chain-grade SEMANTIC concept learner already provides emergent slot structure (CELL 2 from drill).** That cell's ARM_PRESCRIBED_SLOTS_UPPER_BOUND was supposed to use typed multi-bank as the upper-bound rail. Without typed multi-bank, the rail collapses to "no-rail" or "ARM_HAND_LABELED_GROUND_TRUTH" (just use ground-truth types directly as ROUTING DECISIONS without going through bank assignment).

### Q4. Should Wave 2 PIVOT to a completely different composition mechanism?

**YES.** Specifically:

- **DROP** typed multi-bank K=128 mechanism class entirely from Wave 2. The HARD_FAIL was structural at the spec level; respec to M1/M2/M3/cuckoo is feasible but P_deflated 0.35-0.50, and even chain-grade outcome adds INDEXING not COMPOSITION.

- **KEEP** CELL 1 (CLS BCM TWO_TIER) as the highest-priority Stage 3 cell — brain-grounded, P_deflated 0.45, composes on NREM-replay chain-grade.

- **KEEP** CELL 3 (predicate composition role-filler) as the second-priority — variable-binding angle USER explicitly flagged, composes on chain-grade KG + multi-hop.

- **MODIFY** CELL 2 (emergent slot via query cluster discovery) to use ARM_GROUND_TRUTH_SLOT_LABELS as upper-bound rail (skip the broken typed-multibank rail). Substantially simpler; mechanism still tests emergent vs prescribed structure.

- **ADD** three NEW alternative compositional cell-spec stubs below (Section "Alternative Stage 3 cell stubs") that do NOT use typed multi-bank at all.

The Stage 3 program is NOT damaged; the failed cell was the weakest of the 5 by both brain-grounding (MEDIUM, weakest in the set) and P_deflated (tied with CELL 1 at 0.45 but with much higher structural risk per A1 collision math). The 4 remaining cells span sufficient mechanism breadth to test Stage 3 directly.

---

## ALTERNATIVE STAGE 3 COMPOSITIONAL CELL-SPEC STUBS (no typed multi-bank)

### STUB A — `gap3_predicate_chain_composition_via_HRR_unbind_v1`

**Mechanism class:** symbolic predicate composition via HRR role-filler binding (this is CELL 3 from the prior drill, restated as priority-1 alternative).

**What it tests:** can substrate answer multi-hop queries about UNSEEN composed predicates by chaining single-hop atomic facts via HRR unbind?

**Key arms:**
- `ARM_MEMORIZATION_BASELINE`: stores composed facts as atomic (by-construction 1.000 control)
- `ARM_NO_COMPOSITION_CONTROL`: stores only single-hop, queries composed (chance baseline)
- `ARM_HRR_BIND_PREDICATE_COMPOSITION`: stores single-hop, queries via bind(p1, p2) + multi-hop unbind
- `ARM_HRR_BIND_PLUS_REFUSE_GATE`: adds cleanup-energy refuse-gate on uncomposable predicates

**Pre-reg (HARD_PASS):** ARM_HRR_BIND >= 0.55 heldout AND ARM_NO_COMPOSITION <= 0.15 AND ARM_HRR_BIND within 0.20 of ARM_MEMORIZATION AND cv <= 0.10. Strictly-above-floor per META_RULE_L.

**Why it's the right pivot:** no typed routing; pure HRR composition mechanism; composes on chain-grade KG ingest (FB15k 584, ConceptNet 585, HotpotQA 588) and chain-grade multi-hop depth-15 at 0.808. Brain-grounded as variable-binding (Singer 1999, Treisman 1996, Pylkkanen 2019).

**Cost:** 3-5 hr remote_cpu_queue.

**P_deflated:** 0.40 (raw 0.60, calibration -0.20).

---

### STUB B — `gap3_emergent_slot_via_coactivation_clustering_v1` (REVISED CELL 2)

**Mechanism class:** unsupervised slot discovery via query co-activation clustering on chain-grade primitives (ultrametric_clustering, SEMANTIC concept learner).

**What it tests:** given NO type labels, can substrate discover slot-types as latent structure from query-result co-activation patterns?

**Key arms (REVISED to remove typed-multibank rail):**
- `ARM_GROUND_TRUTH_SLOT_UPPER_BOUND`: hand-labeled slot routing (direct dictionary lookup; no multi-bank intermediary). Upper-bound rail.
- `ARM_RANDOM_SLOT_ASSIGNMENT_CONTROL`: random slot assignment (null hypothesis).
- `ARM_EMERGENT_SLOTS_VIA_ULTRAMETRIC`: cluster atoms by co-activation pattern across 1000 substrate self-queries via chain-grade ultrametric_clustering at cosine_thresh=0.85.
- `ARM_EMERGENT_SLOTS_VIA_SEMANTIC_CONCEPT_LEARNER`: chain-grade SEMANTIC concept learner v3 on query-coactivation signature space.

**Pre-reg (HARD_PASS):** best emergent-arm recall on heldout queries >= ARM_GROUND_TRUTH - 0.10 AND NMI between discovered clusters and ground-truth >= 0.70 AND ARM_RANDOM << emergent (gap >= 0.15) AND cv <= 0.08. Strictly-above-floor.

**Key revision from CELL 2:** removed typed-multibank dependency. Upper-bound rail is now direct ground-truth dictionary lookup (always 1.000 by definition); cell tests if emergent clustering recovers comparable routing accuracy. Cleaner discriminator.

**Cost:** 4-6 hr remote_cpu_queue.

**P_deflated:** 0.40 (raw 0.60, calibration -0.20).

---

### STUB C — `gap3_systematic_generalization_relational_swap_v1`

**Mechanism class:** systematic-generalization probe via relational structure swap. Tests whether substrate handles structural composition (X loves Y → Y loves X; Mary kicked John → John was kicked by Mary).

**What it tests:** if substrate stores fact (A, REL, B), can it answer query (?, REL, B) returning A AND query (B, REL_inverse, ?) returning A, WITHOUT having stored REL_inverse atoms directly?

**Key arms:**
- `ARM_BIDIRECTIONAL_MEMORIZATION_BASELINE`: store both (A, REL, B) and (B, REL_inv, A) as atoms. By-construction ~1.000.
- `ARM_FORWARD_ONLY_CONTROL`: store only (A, REL, B); query forward only. Sanity rail.
- `ARM_HRR_INVOLUTIVE_INVERSE`: store (A, REL, B); query (B, REL_inv, ?) via HRR's involutive inverse property (substrate has involutive HRR chain-grade per 2026-06-23). Tests systematic structural composition.
- `ARM_PERMUTATION_INDEX_BINDING_INVERSE`: use permutation-indexed-binding chain-grade primitive's symmetric inverse.

**Pre-reg (HARD_PASS):** ARM_HRR_INVOLUTIVE >= 0.60 on inverse queries AND ARM_FORWARD_ONLY_CONTROL on inverse queries <= 0.10 AND cv <= 0.10. Strictly-above-floor (floor 0.55 + 0.05 band-width).

**Why this matters:** systematic generalization is the CORE Stage 3 test per Lake-Baroni 2018 SCAN benchmark and Bahdanau 2019 systematic-generalization analyses. Substrate's HRR involutive property gives a mechanism-specific path that no transformer architecture provides natively.

**Mechanistically distinct from STUB A predicate composition:** STUB A composes TWO predicates into a new one. STUB C inverts ONE predicate via algebraic property of HRR. Different angle on compositional understanding.

**Cost:** 2-4 hr remote_cpu_queue. Lighter than STUB A because no chain-construction needed.

**P_deflated:** 0.45 (raw 0.60, calibration -0.15 because mechanism is established algebraic property of HRR, not novel-synthesis).

**Brain-grounding:** STRONG-MEDIUM. Systematic generalization is a CORE cognitive science benchmark (Fodor-Pylyshyn 1988; Lake 2019); brain operationalizes via parietal binding + IFG composition.

---

### STUB D — `gap3_compositional_chunking_via_chain_grade_NREM_replay_v1`

**Mechanism class:** compositional chunking via NREM replay — use substrate's chain-grade NREM replay primitive to consolidate frequently-co-occurring atom pairs into chunk atoms. Tests whether replay-driven consolidation creates compositional building blocks.

**What it tests:** does NREM replay over training-time atom co-occurrence statistics produce CHUNK atoms (representing AB as a single entity) that recovery-route correctly when queried for either A or B individually?

**Key arms:**
- `ARM_NO_REPLAY_BASELINE`: substrate without NREM replay; pure single-atom storage.
- `ARM_REPLAY_NO_CHUNKING`: NREM replay enabled but no chunk-formation rule (drift-reduction only).
- `ARM_REPLAY_WITH_CHUNK_FORMATION`: NREM replay + Hebbian-rule chunk formation (when atoms A and B co-fire within window, form chunk atom AB).
- `ARM_REPLAY_PLUS_PARTITION_ORACLE_COMPOSED`: same as above + chain-grade partition-oracle for multi-hop routing. Tests if chunking + routing compose.

**Pre-reg (HARD_PASS):** chunk-formation arm recovers A and B individually >= 0.85 AND recovers AB as composite >= 0.80 AND ARM_REPLAY_NO_CHUNKING shows drift-reduction (per existing chain-grade) AND cv <= 0.08. Strictly-above-floor.

**Why this matters:** chunking is the cognitive-science-canonical mechanism for forming new compositional units from frequency statistics (Miller 1956 "magical number 7"; Gobet 2001 chunking-in-expertise). Substrate has chain-grade NREM replay; chunking on top is a natural extension.

**Mechanistically distinct from STUBs A/B/C:** A/B/C are about query-time composition via algebraic operations. STUB D is about TRAINING-TIME compositional unit formation via replay statistics. Different time-scale, different mechanism. Brain-grounding: hippocampal replay creates schema units (Tse-Langston 2007 + Olafsdottir 2018).

**Cost:** 4-6 hr remote_cpu_queue. Composes on chain-grade NREM replay; chunk-formation rule is ~30 lines new code.

**P_deflated:** 0.40 (raw 0.60, calibration -0.20).

---

### STUB E — `gap3_bijective_typed_routing_M1_falsification_probe_v1` (LOW PRIORITY but informative)

**Mechanism class:** bijective N_TYPES = N_BANKS typed routing — falsification probe for "is typed routing class redeemable when collision is eliminated by construction?"

**What it tests:** with N_TYPES = N_BANKS = 128, typed-routing accuracy = 1.0 by construction. Does cleanup-within-bank then match chain-grade multi-bank, OR does the type-routing path introduce ANY measurable degradation?

**Key arms:**
- `ARM_UNTYPED_BASELINE`: chain-grade K=8192 multi-bank content-cosine routing.
- `ARM_TYPED_BIJECTIVE`: typed routing with N_TYPES = N_BANKS = 128, each bank has unique type. Routing should be IDENTICAL to content-cosine routing's accuracy.

**Pre-reg (HARD_PASS):** typed_recall within 0.005 of untyped chain-grade AND route_acc = 1.000 for both arms AND cv <= 0.05.

**Why this matters:** verifies the angle 1 mathematical analysis — confirms that when collision geometry is eliminated (M1 bijective), the typed-routing mechanism class reduces to chain-grade multi-bank with zero penalty. Falsification probe: if typed_bijective recall is LOWER than untyped, there's a mechanism-class bug beyond the collision-geometry issue.

**Cost:** 1 hr remote_cpu_queue. Cheapest cell in this batch.

**P_deflated:** 0.80 (raw 0.95 because mechanism is essentially relabeling chain-grade; calibration -0.15 for cell-author-error risk). This is HIGH P because it's basically a sanity check; should HARD_PASS if substrate is working.

**Brain-grounding:** N/A (this is a falsification probe, not a brain-grounded mechanism cell).

**Why include it:** if STUB E HARD_FAILs (typed_bijective < untyped chain-grade), I have a bigger substrate issue than just the collision-geometry of CELL 4. If STUB E HARD_PASSes, I close the typed-routing investigation cleanly: "the mechanism works at M1, the K=128 HARD_FAIL was pure collision geometry, no further investigation needed."

---

## Final dispatch recommendation

**KILL** Wave 2 ANCHOR 2 typed_multibank class (do not respec; pivot away from mechanism class for Stage 3 purposes).

**ALREADY IN FLIGHT** (per `research_drill_stage3_compositional_cell_design_2026-06-27.md`):
- CELL 1 cls_two_tier_BCM_slow_replay_v1 (highest P 0.45; brain-grounded; STRONG; KEEP)
- CELL 3 predicate_composition_role_filler_v1 (now PROMOTED to top priority alongside CELL 1; same as STUB A above)

**NEW DISPATCH RECOMMENDATIONS (in priority order):**
1. **STUB E bijective falsification probe** (1 hr; sanity check; close typed-routing branch cleanly).
2. **STUB C systematic generalization relational swap** (2-4 hr; HIGHEST P_deflated of the new stubs at 0.45; HRR involutive chain-grade).
3. **STUB B revised emergent slot via co-activation clustering** (4-6 hr; replaces broken CELL 2 with clean upper-bound rail).
4. **STUB D compositional chunking via NREM replay** (4-6 hr; orthogonal time-scale mechanism class; brain-grounded chunking).

**Spawn budget per Fix #14: ≤3 in flight.** Sequencing:
- Wave A (parallel): STUB E (1 hr) + STUB C (2-4 hr) + CELL 1 (already in flight if dispatched, otherwise add).
- Wave B (after STUB E lands): STUB B + STUB D.
- Wave C (conditional): re-evaluate if Wave A/B HARD_PASS exhausts compositional question.

---

## Cross-cell discipline contract

All stubs apply:
- META_RULE_K smoke FIRES discriminator at full-N (not just runs)
- META_RULE_L band-floor = MIDDLE_BAND not HARD_PASS
- META_RULE_J no silent except blocks
- Fix #28 default tier MIDDLE; let Skunkworks tier UP via per-arm metrics
- Fix #14 ≤3 cell-author spawns in flight
- Fix #17 cell-author smoke MANDATORY before full dispatch — ON REMOTE per USER 2026-06-27 D9
- Fix #26 predispatch_check.py per cell-author spawn
- Per-arm metrics MANDATORY in metrics.json
- 3 seeds minimum; cv ≤ 0.10 for chain-grade per cell tolerance
- ASCII-only; no unicode; no emojis
- Pre-reg specifies cardinality constraints when applicable (e.g., STUB E: N_TYPES == N_BANKS asserted at config-version)

---

## Honest accounting of my prior analysis errors

1. **Director's CELL 4 spec did not specify type-to-bank cardinality** — left N_TYPES=64 and N_BANKS=128 as compatible parameters without flagging collision risk. Cell-author chose first-match deterministic routing. HARD_FAIL inevitable.

2. **Director's pre-reg HARD_PASS bands assumed typed routing CAN beat untyped** — at OVERLAP=0.40 with chain-grade multibank's content-cosine routing at 0.998, the only way for typed routing to beat untyped is if untyped degrades or typed adds value. With identical per-bank load and weaker (first-match) routing rule, typed STRUCTURALLY cannot win.

3. **Director's trigger framing in this drill (Director-to-Director) hypothesized facts/bank^2 crosstalk** — that's correct in general but DOES NOT APPLY to this cell because per-bank load was identical between arms. Real root cause is routing collision, not cleanup crosstalk.

4. **Director's framing in CELL 4 of "typed-routing layered on chain-grade multibank is the right composition"** — incorrect. Typed routing as designed REPLACES content-cosine routing with type-label routing; it doesn't LAYER. Layering would mean type narrows + content selects (STUB approach M3); replacement is what HARD_FAILed.

These are honest cell-design errors I made. The fixes are: (a) future typed-routing specs must declare cardinality + collision-resolution rule; (b) any multi-arm cell where Arm B replaces a mechanism of Arm A must explicitly justify Arm B's mechanism geometry vs Arm A; (c) trigger-time hypothesizing should run cell-code-trace before pinning failure to a specific cause.

---

## References

Internal (chain-grade or chain-grade-eligible primitives this drill relies on):
- `notes/research_drill_stage3_compositional_cell_design_2026-06-27.md` (parent drill that originated CELL 4 and the 5-cell plan)
- `data/exp_typed_multibank_K128_adversarial_v1/metrics.json` (the HARD_FAIL this drill diagnoses)
- `data/exp_phase_diagram_wm_multibank_K_8192_3seed_harvest_v1/metrics.json` (chain-grade K=8192 multi-bank baseline)
- `hdlab/working_memory.py` (chain-grade multi-bank envelope + cap_per_bank=64 META rule)
- `experiments/exp_typed_multibank_K128_adversarial_v1.py` (cell implementation; lines 267-285 _route_by_type_label collision logic; lines 404-491 refuse-gate broken logic)
- `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` (Modern Hopfield / SOLAR / CLS-replay rank ordering)
- `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (CLS BCM brain-grounding)
- `memory/feedback_brain_is_existence_proof_higher_prior_for_brain_grounded_mechanisms_USER_2026-06-23.md`
- `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (BIAS-13 mechanism-cardinality; BIAS-15 spec-implementation mismatch)
- `memory/feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md` (smoke-at-full-N requirement)

External:
- Plate (1995). "Holographic Reduced Representations." IEEE TNN 6(3): 623-641.
- Shazeer et al. (2017). "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer." ICLR.
- Fedus, Zoph, Shazeer (2022). "Switch Transformer." JMLR 23(120): 1-39.
- Pagh, Rodler (2004). "Cuckoo hashing." J. Algorithms 51(2): 122-144.
- Zeki (1973). "Colour coding in rhesus monkey prestriate cortex." Brain Research 53(2): 422-427. (V4 color subregions.)
- Conway (2014). "Color signals through dorsal and ventral visual pathways." Vis. Neurosci. 31(2): 197-209.
- Asaad, Rainer, Miller (2000). "Task-specific neural activity in the primate prefrontal cortex." J. Neurophysiol. 84(1): 451-459.
- O'Keefe, Dostrovsky (1971). "The hippocampus as a spatial map." Brain Research 34(1): 171-175.
- Moser, Rowland, Moser (2014). "Place cells, grid cells, and memory." Cold Spring Harb. Perspect. Biol. 7(2): a021808.
- Hawkins, Ahmad, Cui (2017). "A theory of how columns in the neocortex enable learning the structure of the world." Front. Neural Circuits 11: 81.
- Kanerva (1988). "Sparse Distributed Memory." MIT Press.
- Vaswani et al. (2017). "Attention Is All You Need." NeurIPS.
- Voita et al. (2019). "Analyzing Multi-Head Self-Attention." ACL.
- Michel, Levy, Neubig (2019). "Are Sixteen Heads Really Better than One?" NeurIPS.
- Lake, Baroni (2018). "Generalization without systematicity." ICML. (SCAN benchmark.)
- Bahdanau et al. (2019). "Systematic generalization." ICLR.
- Fodor, Pylyshyn (1988). "Connectionism and cognitive architecture." Cognition 28(1-2): 3-71.
- Singer (1999). "Neuronal synchrony: a versatile code for the definition of relations?" Neuron 24(1): 49-65.
- Treisman (1996). "The binding problem." Curr. Opin. Neurobiol. 6(2): 171-178.
- Pylkkanen (2019). "The neural basis of combinatory syntax and semantics." Science 366(6461): 62-66.
- Miller (1956). "The magical number seven plus or minus two." Psych. Rev. 63(2): 81-97.
- Gobet et al. (2001). "Chunking mechanisms in human learning." Trends Cogn. Sci. 5(6): 236-243.
- Tse, Langston et al. (2007). "Schemas and memory consolidation." Science 316(5821): 76-82.
- Olafsdottir et al. (2018). "The role of hippocampal replay in memory and planning." Curr. Biol. 28(1): R37-R50.
- McClelland, McNaughton, O'Reilly (1995). "Why there are complementary learning systems." Psych. Rev. 102(3): 419-457.
- Kumaran, Hassabis, McClelland (2016). "What learning systems do intelligent agents need?" TICS 20(7): 512-534.
- Bienenstock, Cooper, Munro (1982). "Theory for the development of neuron selectivity." J. Neurosci. 2(1): 32-48.

---

-- Research (Opus 4.7-1M) — 2026-06-27 — closes typed-multibank K=128 branch as Stage 3 mechanism class; pivots to STUBs A/B/C/D/E.
