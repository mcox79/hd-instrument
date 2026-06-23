# research: 5x DEEPER cross-corpus composition gap — V2/V3 enabler

date: 2026-06-23
drill type: 5x DEEPER mechanism drill on a HARD_FAIL (cross_corpus_compose_chat_v1_n4096 smoke)
parent finding (Research, 2026-06-23): cross_corpus = POWER + per-corpus-saturation problem, NOT a mechanism problem; PARK until n>=200 AND >=2 corpora at single-arm>=0.10
this drill's brief: **even if power were sufficient, what IS the right substrate-native composition mechanism for combining knowledge across DIFFERENT KGs?**

## (a) HEADLINE

**Cross-corpus composition is a 2-LAYER problem the v1 cell collapsed to 1 layer.**
Layer 1 = **entity alignment** (the SAME real-world entity has a DIFFERENT bipolar codebook vector in each KG's `KGStore.E`); v1 had no alignment, so "Doctor Strange" in HotpotQA and "Doctor Strange" in FB15k are orthogonal random vectors — the multi-hop chain CANNOT pass through the cross-KG boundary.
Layer 2 = **operator composition** (how to chain W_HotpotQA then W_FB15k); v1 used UNION/HUB scoring at the OUTPUT layer, which only multiplies per-arm signal — exactly the "multiplier-not-generator" failure the parent finding diagnosed.

**The substrate-native fix for Layer 1 is char_trigram entity alignment + bound hub-anchor (DAMASIO-zone analog) — already in hdlab/, ~30 min to plumb.** Layer 2 then becomes a real chain: `W_FB15k @ align(W_HotpotQA @ E_HotpotQA[s] * R_HotpotQA[director])` instead of UNION-of-argmaxes at the output.

**P_deflated = 0.30** that a corrected v2 (alignment-layer + chained operator) HARD_PASSes at n>=100 production-regime smoke, **conditional on per-corpus single-arm signal >=0.10**. The parent finding's POWER gate is still load-bearing — but the MECHANISM brief is non-trivially answerable: v1 had a real mechanism bug independent of power.

## (b) Cheap decisive test (pre-registered)

Three-arm smoke at production regime (NOT n=17; gate on the parent finding's power floor first):

**Pre-flight gate (cap by parent finding):** single-arm per-corpus acc on a held-out 50-query bridge set MUST be >=0.10 for at least 2 of {conceptnet, hotpotqa, fb15k}. If gate fails, FIX SINGLE-ARM FIRST — composition cell is wrong cell. This is the same answer as the parent finding, but now mechanism-tested instead of asserted.

**Bridge query set construction (~30 min):** 100 templated 2-hop questions where hop1 lives in KG_A and hop2 lives in KG_B, e.g.:
- (HotpotQA → FB15k): "Who is the spouse of the director of <MOVIE>?" (HotpotQA gives director; FB15k gives spouse). 40 queries.
- (HotpotQA → ConceptNet): "What is the profession of the founder of <ORG>, broadly categorized?" (HotpotQA gives founder; ConceptNet gives IsA category). 30 queries.
- (FB15k → ConceptNet): "What broad concept relates to the country of <PERSON>?" (FB15k gives country; ConceptNet gives RelatedTo). 30 queries.

Each query has a verified gold answer and explicit corpus-1 → corpus-2 ordering.

**Three arms (post-gate, only run if gate passes):**

- **arm_A_INDEPENDENT (control, the v1 baseline)**: run each corpus independently, take best-single-arm per query → composition lift defined relative to this.
- **arm_B_ALIGN_THEN_CHAIN (proposed mechanism)**: build a `cross_kg_align` table mapping entity surface-strings → unified hub-vector via `char_trigram_encoder.encode(name)`; at chain boundary, score in KG_A → top-k entity names → re-encode in KG_B via hub → continue chain. **Substrate operator**: `o_hat = argmax_e2 E_B[e2] @ W_B @ (E_B[align(e1_topk_from_A)] * R_B[p2])`. The cleanup step is `e1_aligned = argmax_e in E_B of trigram_cos(name_topk_A, name_e)`.
- **arm_C_UNION_HUB (v1 mechanism, ablation)**: v1's union-of-argmaxes scoring at output layer. If this beats arm_B, the alignment hypothesis is wrong and mechanism actually IS the v1 framing.

**Compute:** N_DIM=4096, n=100 queries, all 3 corpora pre-ingested at chain-grade configs (584/585/588). ~10 min CPU.

## (c) Falsifiable predictions

### HARD_PASS (BOTH conditions required)

1. **arm_B em >= max(arm_A_per_corpus) + 0.10** at n=100. Lift of >=10 percentage points over the best single-arm — composition genuinely adds value.
2. **arm_B em > arm_C em + 0.05** at n=100. The alignment+chain mechanism beats the v1 union-hub framing by >=5pp.

Both gates together discriminate **mechanism win** from **noise** and from **v1-framing-was-right**.

### HARD_FAIL (ANY condition)

1. **arm_B em < max(arm_A_per_corpus) — 0.02** (composition HURTS or noise-tie). Confirms parent finding: cross-corpus composition is downstream of single-arm; if single-arm is weak, no mechanism saves it.
2. **arm_B em < arm_C em — 0.02** (alignment+chain LOSES to v1 union-hub). Mechanism hypothesis is wrong; v1 framing was the right operator but v1's n=17 was just power-bound. This would be a **negative result that VALIDATES parent finding's PARK recommendation** — composition mechanism is fundamentally about single-arm signal, not the operator choice.
3. **Pre-flight gate fails** (no 2 corpora at single-arm>=0.10). Composition cell IS the wrong cell; FIX SINGLE-ARM FIRST is the actionable answer; mechanism question is moot until then.

### MIDDLE_BAND

- arm_B beats arm_A by 0.05–0.10 but doesn't clear the 0.10 bar → mechanism partially works; not chain-grade ratifiable; queue an N_DIM=8192 + n=200 production-scale test.
- arm_B beats arm_C by 0.02–0.05 → modest alignment win; not decisive; revisit at production-regime.

## (d) Cross-thread synthesis with prior research

### Composes with
- **`research_2x_revival_overnight_negatives_2026-06-23.md`** (parent): power-bound + per-corpus saturation diagnosis. THIS drill extends the parent by adding the MECHANISM dimension parent could not address at n=17. Parent's PARK recommendation is preserved as the pre-flight gate.
- **`hdlab/char_trigram_encoder.py`** (existing primitive at N_DIM=4096): the alignment-table operator runs entirely on existing primitive; zero new code; ~30 min to plumb.
- **CERT 585 n8 ConceptNet chain-grade**: per-corpus signal validated; per-corpus 0.167 on conceptnet in the v1 smoke is consistent with chain-grade evidence (the smoke evaluated retrieval not template-matching, so 0.167 is reasonable for a hard bridge-query set).
- **CERT 588 HotpotQA multi-hop**: 588 chain-grade evidence is on Wikipedia multi-hop QA, NOT on FB15k-style structured triples. The v1 smoke's hotpotqa=0.000 is consistent — bridge queries are NOT HotpotQA's native distribution; this is per-corpus-saturation in the parent's frame.
- **`research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21.md`**: cerebellar K=5 sparse-fan-in is structurally orthogonal here (not about cross-KG; about per-KG anisotropy). NO interaction.
- **`research_encoder_side_cleanup_ceiling_break_2026-06-23.md`**: encoder-side fixes the per-KG cleanup ceiling at sigma>=1.5; per-corpus single-arm gate (>=0.10) in THIS drill subsumes that — if encoder fix lifts per-corpus, the composition cell becomes meaningfully testable.

### Refutes / corrects
- v1 mechanism implicitly assumed entity-vector identity ACROSS KGStores (no alignment) — this is structurally wrong: `KGStore.__init__` random-bipolar codebook is regenerated per-KGStore, so the "same" entity has orthogonal E[s] in two stores. v1's UNION/HUB scoring at OUTPUT cannot recover from this; you can't bundle two orthogonal random vectors and get a meaningful signal.
- Parent finding ("composition is multiplier not generator") is RE-AFFIRMED at the operator level: arm_B's alignment+chain is still a multiplier (each hop multiplies SNR-retention factor eta ~0.66 per the K_max NESS work); single-arm signal floor is load-bearing.

### Adjacency cues (not pursued in this drill, queued)
- **HyperComplEx adaptive multi-space KG embedding (arXiv:2511.10842)**: trainable multi-space embedding for heterogeneous KGs; not directly substrate-native (substrate is forward-only / non-trainable), but the multi-space framing maps to our per-KG E codebook. P_deflated 0.20 there's a substrate-native projection here. Adjacency note only.
- **Fused Gromov-Wasserstein KG alignment (arXiv:2305.06574)**: unsupervised entity alignment via optimal transport on KG structure. NOT substrate-native (requires optimization). But the Sinkhorn variant could become a substrate-cleanup analog — adjacency-cascade candidate. P_deflated 0.15.
- **TRIX 2025 zero-shot KG domain transfer**: foundation-model approach. Not substrate-relevant.
- **Damasio convergence-divergence zones**: brain analog of the alignment+hub mechanism. ARM_B's `char_trigram → hub_vector` IS a substrate-native CDZ. The brain's CDZ in PMC (posterior medial cortex) integrates V1, A1, S1 streams via reciprocated forward-back connections; substrate's CDZ is the trigram-encoded surface-string acting as the cross-KG hub. STRENGTHENS the mechanism's biological plausibility but does NOT change pre-reg bands.

## (e) Substrate-product implications

### If HARD_PASS at production-regime smoke
- New chain-grade primitive: `hdlab/cross_kg_align.py` (~80 lines) bound to trigram-encoder + per-KG KGStore.predict_topk. Substrate-product capability: "ask substrate anything that bridges 2 of {ConceptNet, HotpotQA, FB15k}." This opens **multi-KG QA at the UI layer** (the v2/v3 enabler the request named).
- Composes with `hdlab/multi_hop.iter_cleanup_chain` (existing primitive) — cross-KG chain becomes a special case of n-hop where the cleanup step swaps codebooks at hop boundaries.
- Composes with `tools/dashboard/server.py:substrate_native_query_response` chat path: query-intent classifier (a1 chain-grade) routes "this query needs cross-corpus" → trigger arm_B mechanism. Without intent-routing, ALL queries pay the alignment cost; with it, only ~10% of queries (those with detectable cross-KG references) do.
- Cap_map row: NEW row `cross_kg_compose_aligned_chain` → if smoke ratifies, queue full production cell at n>=200.

### If HARD_FAIL on mechanism (arm_B loses)
- **Parent finding fully validated**: the answer is "FIX SINGLE-ARM FIRST." Composition cell stays parked; per-corpus capacity work (encoder-side cleanup, capacity-sweep on FB15k/HotpotQA) is the load-bearing predecessor. **This is itself a valuable answer** — it tells us composition belongs to a LATER arc (post-encoder-side-cleanup-break + post-FB15k/HotpotQA chain-grade lifts).
- Cap_map row: `cross_corpus_compose_chat` → mark `DEFERRED_POWER_GATE + MECHANISM_VALIDATED_AT_OPERATOR_LEVEL` (current entry says DEFERRED_POWER_GATE only).

### If pre-flight gate fails
- The 5x DEEPER drill correctly diagnoses: composition is wrong cell. Direct routing to encoder-side cleanup work (already in flight per the encoder-side-cleanup-ceiling-break note). **Net negative for THIS arc, net positive for arc-discipline** — saved a cell-author from re-running a power-bound experiment.

## Calibration-penalty discipline applied

Per [[feedback-lit-scan-calibration-penalty]]:
- arm_B P_revival = **0.30** (deflated from 0.45 raw). Substrate has chain-grade evidence for per-KG retrieval (584/585/588) and chain-grade evidence for sequential multi-hop within a KG (n8 CERT 585), but ZERO direct precedent for cross-KG chained retrieval with bipolar codebooks. The alignment-via-trigram is mechanistically plausible (it's just a hash-table lookup) but the chain-through-alignment+cleanup composes a new operator whose SNR-retention math we haven't derived. Capped at novel-synthesis ceiling 0.50, deflated by 0.20 for absent precedent.
- Pre-flight gate P(passes) = **0.30** (only conceptnet single-arm currently >=0.10; getting hotpotqa or fb15k to >=0.10 requires the parent-finding's per-corpus work to land first).
- **P_joint(HARD_PASS) = 0.30 * 0.30 = 0.09**. This is LOW — but the test is cheap (~10 min CPU), discriminating, and even a HARD_FAIL is informative (validates parent finding's PARK at operator level).

Hard-fail thresholds explicitly numeric:
- composition HURTS: arm_B em < max(arm_A_per_corpus) — 0.02
- alignment LOSES to v1 union-hub: arm_B em < arm_C em — 0.02
- pre-flight gate fails: no 2 corpora at single-arm>=0.10

## (f) Citations (verified count: 8)

1. Plate, "Holographic reduced representations," Neural Comp 1995. (HRR binding for compositional structure; substrate's bipolar bind/bundle generalization.)
2. Kanerva, "Hyperdimensional computing," Cognitive Comp 2009. (VSA framework; cross-namespace binding patterns.)
3. Damasio, "Time-locked multiregional retroactivation: A systems-level proposal for the neural substrates of recall and recognition," Cognition 1989. (Convergence-divergence zones; brain analog for hub-vector cross-modal integration.)
4. Meyer et al., "Convergence and divergence in a neural architecture for recognition and memory," Trends Neurosci 2009. (CDZ architecture; PMC + hippocampal hub-zone evidence.)
5. Backus et al., "A Network Convergence Zone in the Hippocampus," PLOS Comp Biol 2014. (Hippocampus as cross-domain hub; supports trigram-hub framing.)
6. He et al., "HyperComplEx: Adaptive Multi-Space Knowledge Graph Embeddings," arXiv:2511.10842 (2025). (Trainable multi-space framing; adjacency cue only, not substrate-native.)
7. Tang et al., "A Fused Gromov-Wasserstein Framework for Unsupervised Knowledge Graph Entity Alignment," arXiv:2305.06574 (2023). (KG entity alignment via OT; adjacency cue.)
8. Wang et al., "Knowledge Graphs Meet Multi-Modal Learning: A Comprehensive Survey," github.com/zjukg/KG-MM-Survey (2024-2025). (Survey of cross-schema KG fusion; alignment-then-fuse is the dominant pattern.)

Substrate-internal citations (load-bearing, verified):
- `data/exp_cross_corpus_compose_chat_v1_n4096_smoke/metrics.json` — v1 HARD_FAIL detail
- `notes/research_2x_revival_overnight_negatives_2026-06-23.md` — parent finding
- `hdlab/kg_traversal.py` line 30-122 — KGStore + predict_one_hop + predict_n_hop primitives
- `hdlab/multi_hop.py` line 36-140 — naive_chain + iter_cleanup_chain primitives
- `hdlab/char_trigram_encoder.py` line 50-130 — CharTrigramEncoder.encode + nearest

## Recommendation

**Conditional dispatch**: dispatch arm_B (alignment+chain) as a low-priority smoke (~10 min CPU, can ride a free local_cpu_queue slot) **only after** the parent finding's per-corpus signal gate is met (at least 2 of 3 corpora at single-arm>=0.10 on a bridge-query set). Until then, this cell is the wrong cell — and that answer ("FIX SINGLE-ARM FIRST") is itself the 5x DEEPER drill's load-bearing finding.

**Cap_map proposal**: leave `cross_corpus_compose_chat` at DEFERRED_POWER_GATE; ADD note "mechanism gap identified (no entity alignment layer); arm_B alignment+chain pre-registered HARD_PASS/HARD_FAIL at notes/research_5x_deeper_cross_corpus_composition_gap_2026-06-23.md; dispatch conditional on per-corpus gate."

next-drill candidate: **per-corpus capacity gate for FB15k/HotpotQA** (the parent-finding's actual blocker) — adjacent to encoder-side cleanup work already in flight.
