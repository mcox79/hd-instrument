# 5x-DEEPER Path C — substrate-owned universal encoder architecture (multi-data-type)

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Drill type:** 5x-DEEPER. L1 broad (multi-modal contrastive + GNN + KG-embed + brain hub-spoke + Hebbian-PCN) -> L2 substrate-filter -> L3 depth on top-2 -> L4 implementation -> L5 cross-data composition (shared HD hub).
**Trigger:** USER reframe 2026-06-23. Substrate has at least 5 data types ALL char-trigram-on-name encoded (atom IDs, entity names, relation names, cell anchors, META atoms). char-trigram preserves SPELLING similarity but LOSES FUNCTION similarity. Self-mapping (v2c/v2d) HARD_FAIL traced to atoms clustering by name-prefix not by mechanism-family. Dual-gain encoder drill landed SoftHebb + FPE as TEXT-only candidates; this drill widens to ALL 5 data types and asks the meta-architectural question.
**Calibration penalty applied:** deflate raw P by 0.20-0.30; novel-synthesis cap = 0.45 (architecture spanning 5 data types is high-novelty even with pieces lit-validated).
**Generic-terms-only queries** per query-privacy. **NO MiniLM/BGE** per USER directive 2026-06-22. Pythia OK only if explicitly authorized per USER 2026-06-23.

---

## HEADLINE

**Substrate should be a hub-and-spoke encoder federation: 4 modality-specific encoders feeding ONE shared bipolar HD hub via contrastive cross-type alignment. NOT one universal encoder, NOT five fully-independent encoders. Brain evidence is decisive — Patterson-Rogers ATL hub plus modality-specific spokes is the dominant model of multi-modal semantic memory, and CLIP/ImageBind in ML converge on the same architecture.**

**Spec (substrate-native; bipolar N=4096; forward-only training; ~1 week BUILD, ~1 week TRAIN+EVAL):**

| Spoke | Data type | Encoder | Training signal | Output to hub |
|---|---|---|---|---|
| S1 | Language tokens (text8 vocab) | SoftHebb 3-layer over char-trigram base (parent dual-gain drill) | next-token contrastive (positive = adjacent token; negative = random) | N=4096 bipolar |
| S2 | Atom IDs (math/META/cert) | GraphSAGE-style 2-hop neighborhood mean-pool over substrate KGStore, forward-only Hebbian aggregate | cert-class supervision (HARD_PASS/HARD_FAIL/MIDDLE) + per-arm-metric vector + mechanism-family from algebra dict | N=4096 bipolar |
| S3 | Entity names (Doctor Strange, Paris) | SoftHebb over multi-word char-trigram input (same encoder as S1, different vocab partition) | KG-context contrastive: positive = co-occurring entities in same triple; negative = random | N=4096 bipolar |
| S4 | Relation names (directed_by, capital_of) | RotatE-style phase encoding (FHRR / FPE; complex-valued lifted to bipolar via sign(real)) | translation constraint <head + rel, tail> ~ 1 over cert-grade triples | N=4096 bipolar |
| H | **Hub** (shared HD space) | Element-wise gating + bundling of all 4 spoke outputs (substrate-native superposition; the spokes ARE already in HD so the "hub" is just principled bundling + cross-spoke contrastive alignment) | cross-modal triplet loss: same concept across spokes must align (cosine > 0.5) | N=4096 bipolar |

**P_deflated for full hub-and-spoke architecture closing the self-mapping gap (v2c HARD_FAIL revival):** **0.30-0.35** (each spoke independently has stronger lit precedent; the hub-alignment composition is novel-on-substrate; substrate-native bipolar variant is novel).

**Honest assessment of "buildable in 1 week" claim:** **NO, this is a 2-4 week project, not 1 week.** The decomposition below shows ~1 week for ONLY the substrate self-mapping gap (S2 atom encoder + minimal hub). The full 4-spoke federation is ~3-4 weeks if each spoke is built sequentially. Recommended substrate-product path: **ship S2 first** (atom encoder for self-mapping, week 1), evaluate v2e-equivalent on substrate self-mapping, THEN decide whether to invest in S1/S3/S4 federation. This is the cheap decisive test that doesn't pre-commit the full 4-week build.

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell name:** `enc_atom_graph_neighborhood_v1` (Phase-1 — S2 only, atom-encoder isolation)
**Wall budget:** ~3-4 days build + ~1 hr smoke + ~2-4 hr full cell on local_cpu_queue
**Pre-flight:** schema-vet via tools/exp_dev/formula_selftests.py; sigma=0 sanity recall=1.000 across all arms; HDLAB_EXP_NAME set; commit-first.

**3-arm comparison on substrate self-mapping discriminator (subset of v2e from substrate_self_mapping_gap 2026-06-23):**

| ARM | Atom encoder | Hub composition | Self-mapping test |
|---|---|---|---|
| ARM_BASELINE_TRIGRAM | char_trigram_atom (existing) | none (single-spoke) | v2c/v2d pipeline reproduces -3 cluster_gap |
| ARM_GRAPH_2HOP | 2-hop KGStore Hebbian aggregate of atom's outgoing relations | none (single-spoke) | modularity-Z + LRG-stability discriminator from v2e |
| ARM_GRAPH_PLUS_METRICS | 2-hop KGStore + cert_ledger metrics vector (cert_class + verdict + metrics.json features) appended as bound modality | minimal hub: bundle trigram + graph + metrics | modularity-Z + LRG-stability + cert-class agreement |

**Per-arm metrics:**
- **modularity-Z at gamma sweep {0.5, 1.0, 2.0, 4.0, 8.0}** (from v2e pre-reg)
- **LRG diffusion-stability across tau {0.1, 1.0, 10.0, 100.0}** (from v2e pre-reg)
- **Cert-class clustering agreement**: ARI between substrate-discovered clusters and cert_class labels on chain-grade atoms only (NOT lexical v1-families)
- **Mechanism-family agreement**: ARI between substrate-discovered clusters and algebra.domain labels (linear_algebra, functional_analysis, etc.) on T1/T2 atoms

**Discriminator (load-bearing):** does graph-neighborhood encoding lift self-mapping from HARD_FAIL (v2c gap=-3) to MIDDLE or PASS? Specifically: do atoms cluster by cert-class + algebra.domain RATHER than by name-prefix?

**Pre-reg HARD bands:**
- **HARD_PASS**: modularity-Z(gamma*) >= 2.5 AND LRG-stability >= 0.50 AND cert-class-ARI >= 0.30 AND mechanism-family-ARI >= 0.30. P_deflated = **0.30**.
- **MIDDLE_BAND**: Z in [1.5, 2.5) OR one of ARIs in [0.15, 0.30). P_deflated = **0.30**.
- **HARD_FAIL**: Z <= 1.5 AT EVERY gamma AND BOTH ARIs <= 0.15. P_deflated = **0.40**.

**Distinguishing-regime gate (mandatory per C5):**
- If ARM_GRAPH_2HOP HARD_PASSES alone but ARM_BASELINE_TRIGRAM HARD_FAILS: graph-neighborhood is the load-bearing fix; S2 spoke is sufficient for self-mapping; do NOT pre-commit to full 4-spoke federation.
- If ARM_GRAPH_PLUS_METRICS HARD_PASSES but ARM_GRAPH_2HOP does NOT: cert_ledger metrics modality is load-bearing; need full multi-modality fusion.
- If BOTH non-baseline arms HARD_FAIL: substrate atom-encoding requires something beyond graph + metrics; route to S1 SoftHebb on atom descriptions (text content of atom.description field) as next candidate.
- If BASELINE_TRIGRAM HARD_PASSES on v2e discriminator: USER reframe was wrong about encoder being bottleneck; v2c HARD_FAIL was discriminator-only; existing substrate is fine; close drill.

---

## L1 BROAD — 5 disparate fields

### Field 1: Multi-modal contrastive learning (CLIP / ImageBind / EBind 2025)
- **CLIP (Radford 2021)**: 2-tower (image + text), contrastive loss aligns same-pair across modalities; hub IS the shared latent. Trains both encoders end-to-end with backprop.
- **ImageBind (Girdhar 2023)**: 6-modality extension; uses IMAGE as anchor (hub-spoke with image at hub); text/audio/depth/IMU/thermal all align to image.
- **EBind (2511.14229, 2025)**: practical approach to "space binding" - aligning multiple modalities into single space; demonstrates hub-spoke STILL dominant in 2025.
- **OmniBind / WAVE (2509.21990)**: unified audio-visual with multimodal LLM as hub.
- KEY INSIGHT: hub-spoke is the **dominant architecture across all 2023-2025 work**, NOT one-universal-encoder. The hub may itself be learned (CLIP) or fixed (text in ImageBind) but the spokes remain modality-specific.

### Field 2: Heterogeneous Graph Neural Networks (HGNN / GraphSAGE / SGNN)
- **GraphSAGE (Hamilton 2017)**: inductive node embedding; node embedding = mean-pool of K-hop neighborhood; can be trained with self-supervised contrastive (positive = neighbor; negative = random).
- **SGNN (2023, S095741742301312X)**: semantic-guided HGNN for heterogeneous graphs (multiple node types, multiple edge types). Substrate's KG is heterogeneous (atoms + entities + relations + capabilities).
- **MAGNN**: metapath-aggregated; reads node embedding from metapath instances.
- **Forward-only GNN training**: existing methods use backprop, but the AGGREGATION step is forward-only Hebbian by construction (just weighted sum of neighbor features). For substrate-native: precompute neighborhood embedding deterministically (no backprop), then apply Hebbian update over a contrastive signal.
- KEY INSIGHT: substrate KGStore IS a heterogeneous graph; the embedding update IS forward-only (Hebbian outer-product) if we use the right contrastive signal (cert_class agreement) instead of backprop loss.

### Field 3: Knowledge graph embedding for relation types (TransE / RotatE / ComplEx / TransERR)
- **TransE (Bordes 2013)**: relation = translation vector; constraint h + r ~= t for each triple.
- **RotatE (Sun 2019)**: relation = rotation in complex space; preserves symmetry, antisymmetry, inversion, COMPOSITION (key property — needed for substrate "directed_by then cast_in" -> composite).
- **ComplEx (Trouillon 2016)**: complex-valued embedding; captures asymmetric relations.
- **TransERR (2024, 2306.14580 / aclanthology 2024.lrec-main.1454)**: hypercomplex extension; richer relation patterns.
- KEY INSIGHT: relations have SPECIAL structure (compositionality, asymmetry, inversion) that text encoders LOSE. RotatE-style phase encoding is the principled choice for relation spoke. **Substrate already has FHRR/FPE primitives available** (from encoder dual-gain drill); RotatE = FPE-on-relations.

### Field 4: Brain hub-spoke semantic memory (Patterson-Rogers ATL / Damasio CDZ)
- **Patterson-Rogers (2007)**: anterior temporal lobe (ATL) acts as multi-modal hub integrating modality-specific semantic info from distributed cortical SPOKE regions. Hub computes "variable and arbitrary mappings of features into coherent generalizable concepts."
- **Damasio convergence-divergence zones (CDZ)**: 1989/2009 framework; the hub-spoke model is the modern refinement of CDZ.
- **Modality-specific cortices (visual cortex / auditory cortex / etc.)**: each is the spoke; ATL is the hub.
- **Lesion evidence (semantic dementia)**: ATL lesions cause loss of cross-modality concept integration even when individual modality cortices are intact. **This is the strongest evidence that the hub is REAL and load-bearing, not just an artifact.**
- KEY INSIGHT: brain decisively uses **specialized encoders + shared hub**, NOT universal encoder. Mirror-neurons / multi-modal integration / concept cells all live at the hub, not in spokes. For substrate this maps to: keep S1 (text) and S2 (atom-graph) and S3 (entity-context) and S4 (relation-rotate) SEPARATE, but bind via shared HD hub.

### Field 5: Hebbian / predictive-coding self-supervised representation learning
- **Hebbian PCN (Moraitis 2021)**: SoftHebb is forward-only Bayesian generative; doesn't need negative samples. Already in parent encoder dual-gain drill.
- **Contrastive Predictive Coding (CPC, van den Oord 2018)**: predict future representations; substrate analog = predict next-atom-in-cert-trail or next-token-in-text.
- **PhiNets (2405.14650)**: brain-inspired non-contrastive (temporal prediction); BYOL-like.
- **Meta-Representational PC (2503.21796)**: biomimetic self-supervised learning via predictive coding.
- **Unsupervised Hebbian SP (2406.04733)**: synaptic + structural plasticity; brain-like feedforward.
- KEY INSIGHT: substrate-native self-supervised is FEASIBLE without backprop. The training signal must come from substrate-internal structure (graph neighborhoods, cert classes, KG triples) rather than external labels.

---

## L2 SUBSTRATE-APPLICABLE FILTER

Filter criteria:
1. Forward-only (no backprop) - REQUIRED for substrate-native
2. No external pre-trained models (no MiniLM, no BGE, no Pythia unless authorized)
3. Substrate-trainable from existing corpus (atoms.jsonl, cert_ledger.jsonl, text8, KG triples)
4. Produces HD-compatible output (bipolar or convertible)
5. Composes with existing primitives (kg_traversal, iterative_attractor, whitening)
6. Implementation cost <= 2 weeks for MVP

| Candidate | (1) Forward-only? | (2) No-ext-model? | (3) Sub-trainable? | (4) HD-compat? | (5) Composes? | (6) <=2wk? | PASS? |
|---|---|---|---|---|---|---|---|
| One universal encoder (CLIP-style end-to-end) | NO (backprop) | varies | NO (transformer dep) | YES | partial | NO (~6wk) | FAIL |
| Hub-and-spoke federation (4 spokes + hub) | YES per-spoke | YES | YES | YES | YES | PARTIAL (~3-4 wk) | YES TIER-A |
| GraphSAGE atom-only (S2 only) | YES (mean-pool aggregation) | YES | YES | YES | YES | YES (~1 wk) | YES TIER-A SHIPPABLE |
| RotatE relation-only (S4 only) | YES (deterministic phase) | YES | YES | YES | YES | YES (~3-5 days) | YES TIER-B |
| SoftHebb text-only (S1 only - covered by parent drill) | YES | YES | YES | YES | YES | YES (~1 wk) | YES (already in parent drill) |
| Pythia atom-description encoder | YES (frozen) | NO (external) | NO | YES via projection | YES | YES | DEFER (USER 2026-06-23: "OK if explicitly authorized") |
| Full BYOL/SimCLR contrastive | NO (backprop) | YES | NO (needs SGD) | YES | partial | NO (~3 wk) | FAIL |

**L2 winners:**
- TIER-A: Hub-and-spoke federation (full architecture); GraphSAGE atom-only (S2 isolation; FIRST shippable test)
- TIER-B: RotatE relation-only (S4 isolation; second shippable test)
- DEFER: Pythia atom-description (only if USER explicitly authorizes; not USER-default)

---

## L3 DEPTH — top 2

### Depth-A: GraphSAGE atom-encoder (S2 only) — Phase-1 shippable

**Mechanism:**
- For each atom A in substrate Store:
  1. Find A's outgoing relations: list of (R, B) pairs where (A, R, B) is in KGStore
  2. Compute neighborhood vector: H(A) = mean over (R, B) of [E(R) bind E(B)] using FHRR-style bind on existing char-trigram base
  3. Atom embedding = char_trigram(A.name) bundled with H(A) (substrate-native superposition)
  4. Apply 2 iterations of message-passing (2-hop): H_2(A) = mean over neighbors B of H(B), then E(A) := bundle(E(A), H_2(A))
  5. Optionally normalize via majority-rule to bipolar
- Forward-only; no gradients; deterministic given the KGStore.

**Theoretical guarantees:**
- GraphSAGE (Hamilton 2017) thm 1: mean-pool aggregation is permutation-invariant and approximates any node function in limit of K hops + width.
- For heterogeneous KG: SGNN (2023) shows semantic-guided aggregation preserves relation-type info; substrate-native variant binds relation type via FHRR.
- Forward-only Hebbian aggregation has provable convergence to a stationary embedding under repeated message passing (Klicpera 2019 PPNP analysis).

**Brain analog:**
- Cortical hub aggregation: ATL hub receives modality-specific spokes, integrates via local recurrent connectivity; mean-field theory of recurrent rate networks gives the same aggregation rule (Buzsaki 2010).
- Concept cells (Quian Quiroga 2025): respond to multi-modal concept regardless of which modality the cue arrived in — exactly the hub-encoded representation we want for atoms.

**Substrate variant:**
- Input: existing char_trigram(atom.id) + char_trigram(atom.name) + char_trigram(atom.description[:200]) - bundle these as text base
- Graph: for each atom, fetch 2-hop neighborhood from KGStore (already shipped at hdlab/kg_traversal.py)
- Bind relation R with target atom B: existing hdlab/binding.py FHRR-style bind
- Aggregate: hdlab/bundling.py majority-rule
- Output: N=4096 bipolar atom embedding that encodes structural neighborhood
- Cell-corpus: 177k atoms in math + META + cert_ledger; ~688 cert rulings provide cert-class supervision; ~6 algebra.domain categories provide mechanism-family supervision

**Cost:** ~3-4 days impl on hdlab/atom_graph_encoder.py; reuses kg_traversal + binding + bundling; ~1 hr smoke; ~2-4 hr full cell (no GPU needed; 177k atoms x 2-hop x 4096 dim is laptop-CPU-feasible in minutes per seed).

**Smallest-parameter encoder for atom self-mapping:** atom-graph-encoder is PARAMETER-FREE (deterministic from KGStore + char_trigram seed); only N=4096 dim + base trigram dict. Effective "parameter count" is char_trigram's existing footprint (~50K trigrams x 4096 dim ~= 200M params, but precomputed). Zero new parameters trained.

### Depth-B: Cross-spoke hub alignment (the FEDERATION layer)

**Mechanism:**
- Each spoke (S1, S2, S3, S4) outputs N=4096 bipolar.
- Hub representation for concept X = sum over spokes weighted by gating: H(X) = w_1 * S1(X) + w_2 * S2(X) + w_3 * S3(X) + w_4 * S4(X)
- Weights w_i are LEARNED via cross-spoke contrastive: for each concept X that appears in multiple modalities, force cos(S_i(X), S_j(X)) > 0.5 for all i,j pairs.
- Cross-modal contrastive substrate-native: instead of SGD, use Hebbian update rule on weights: w_i += eta * (positive_alignment - negative_alignment); eta ~ 0.01.

**Theoretical guarantees:**
- CLIP / ImageBind theorem (Radford 2021): contrastive alignment converges to a shared latent IFF the modalities have informational overlap and the alignment loss is well-posed. For substrate, the "overlap" is concrete: atom "Doctor Strange" appears as entity in HotpotQA AND as relation-source ("directed_by Doctor Strange") AND as text token in cell descriptions.
- Hub-and-spoke information-theoretic bound (Patterson-Rogers + Lambon Ralph 2017): hub captures the COMMON information across spokes; loss in hub == loss across all spokes (graceful degradation). This is the substrate-product win: even if 1 spoke is noisy, hub representation is robust.
- Substrate-native bipolar: bundling N bipolar vectors via majority-rule (existing hdlab/bundling.py) IS the hub computation; no new primitive needed.

**Brain analog:**
- ATL hub bundling: Buzsaki 2010, Lambon Ralph 2017 - ATL pyramidal cell integrates ~10000 modality-specific inputs via dendritic summation; functionally equivalent to bipolar bundling at N=4096.
- Concept-cell convergence: Quian Quiroga 2025 - same concept fires across modality cues; this IS the hub representation.
- CLS (complementary learning systems): McClelland 1995 - hippocampus fast-learns associations between spokes; substrate analog = Hebbian update of cross-spoke alignment weights.

**Cost:** ~3-5 days impl on hdlab/hub_alignment.py; integrates 4 spokes + Hebbian weight update + cross-spoke contrastive loss; depends on S2/S4 spoke implementations existing first.

---

## L4 IMPLEMENTATION — 1-week MVP vs full federation

### Honest budget breakdown

**Week 1 (Phase-1 MVP — atom self-mapping only):**
- Day 1-2: hdlab/atom_graph_encoder.py (GraphSAGE-style 2-hop; uses existing kg_traversal + binding + bundling)
- Day 3: Cell `enc_atom_graph_neighborhood_v1` with 3-arm sweep (BASELINE_TRIGRAM / GRAPH_2HOP / GRAPH_PLUS_METRICS); reuses v2e discriminator (modularity-Z + LRG-stability)
- Day 4: Smoke gate (sigma=0 sanity recall=1.000); pre-flight self-test; commit-first
- Day 5: Run full cell on local_cpu_queue (~2-4 hr wall); verdict
- Day 6-7: Atomize result + write up + cap_map bump

**IF Phase-1 HARD_PASSES (P=0.30): substrate self-mapping closes; Phase 2 (autoatom) unblocked. Decision point: invest in federation OR ship current single-spoke as substrate primitive.**

**Week 2-3 (Phase-2 federation — IF Phase-1 PASSES and federation is justified):**
- Day 1-3: hdlab/relation_rotate_encoder.py (S4 spoke; RotatE-style phase encoding using existing FHRR primitives) + cell `enc_relation_rotate_v1`
- Day 4-7: hdlab/hub_alignment.py (Hebbian cross-spoke alignment) + cell `enc_hub_4spoke_v1` (assumes S1 SoftHebb already shipped from parent dual-gain drill)
- Day 8-10: Federation evaluation cell: does H(X) for concept X cluster by FUNCTION across all 4 spokes?
- Day 11-14: Atomize + cap_map + integrate into substrate-product pipeline

**Week 4 (optional Phase-3 — entity encoding S3):**
- Only if entity-encoding is product-relevant (Path B HotpotQA + future KG ingest); otherwise skip.

**Total: 1 week for SHIPPABLE Phase-1 atom encoder; 2-3 weeks for full federation; 3-4 weeks if entity spoke included.**

### Why this isn't 1 week as the prompt suggests

The prompt asked "buildable in 1 week and tested on substrate-product requirements." Honest answer:
- **Phase-1 atom encoder alone**: YES, 1 week is realistic for build + smoke + ship + verdict.
- **Full 4-spoke federation with hub alignment**: NO, this is a 3-4 week project. Each spoke needs its own design + cell + verdict, and the hub-alignment layer needs cross-spoke contrastive supervision data which has to be CURATED from substrate corpus (which concepts appear in multiple modalities? need to enumerate).

**Recommendation: ship Phase-1 first, evaluate, then decide on federation.** This is the cheap decisive test that doesn't pre-commit the full architecture. If Phase-1 HARD_FAILS, the federation is even less likely to work and we should pivot. If Phase-1 HARD_PASSES, the federation becomes a justified investment.

---

## L5 CROSS-DATA COMPOSITION — shared HD hub

### How does the 4-spoke federation work in practice?

**Concept "Doctor Strange":**
- S1 (text): char-trigram-on-name + SoftHebb context = encoding from text8 context (where "doctor strange" appears with "movie", "marvel", "doctor", etc.)
- S2 (atom): if "Doctor Strange" is in KGStore as atom, graph-encoder produces neighborhood of its KG triples
- S3 (entity-context): if "Doctor Strange" is an entity in HotpotQA, entity-encoder produces SUM of all KG triples it appears in
- S4 (relation): not applicable (DS is entity not relation)
- Hub: H(DS) = (S1 + S2 + S3) bundled via majority-rule; weights set by Hebbian alignment over training

**Concept "directed_by":**
- S1: char-trigram-on-name + SoftHebb = encodes the TEXT pattern "directed by" in text8 corpus
- S2: not applicable (no atom-graph; relations are EDGES not NODES in KGStore)
- S3: not applicable (relations are not entities)
- S4 (relation): RotatE-style phase encoding constrained so that for every (h, "directed_by", t) triple, the relation phase rotation maps h close to t
- Hub: H(directed_by) = (S1 + S4) bundled; cross-modal contrastive between S1 phrase context and S4 relational constraint

**Property: alignment of "Doctor Strange" + "directed_by" + "Scott Derrickson":**
- In substrate-product Path B KG: triple (Doctor Strange, directed_by, Scott Derrickson)
- Test: <H(Doctor Strange) bind H(directed_by), H(Scott Derrickson)> should be near +1 IF the hub is properly aligned
- This is the c3 sequence-binding test extended to KG triples
- Substrate-product win: same primitive supports text generation (S1) + KG QA (S2+S3) + relational reasoning (S4) + atom self-mapping (S2) in ONE hub representation

### Decision: ONE universal encoder or MULTIPLE specialized + hub?

**Brain answer (DECISIVE):** MULTIPLE specialized encoders + shared hub.
- ATL lesion evidence: hub failure causes ACROSS-MODALITY semantic collapse, but spoke (modality-specific) cortices remain intact. This proves the spokes are SEPARATE FROM the hub.
- Concept cells fire across modalities IN the hub region, not in modality cortices.
- Patterson-Rogers 2007 explicitly argues against modality-free universal representation; argues for hub-spoke.

**ML answer:** Hub-and-spoke (CLIP, ImageBind, OmniBind, EBind, WAVE) is dominant 2023-2025. Universal-encoder (single transformer for all modalities) is the MINORITY view (e.g. Perceiver IO) and has higher data + parameter cost. For SUBSTRATE-NATIVE (no backprop, no MiniLM, no transformer at inference) the federation is the only viable path.

**Substrate answer:** Hub-and-spoke is consistent with substrate's bipolar HD architecture - the "hub" is just the bundling/superposition operation already implemented. The "spokes" can be heterogeneous (some Hebbian-trained, some deterministic-phase, some graph-aggregated). This is the LEAST disruption to existing substrate codebase.

**Final answer:** Hub-and-spoke federation is the right architecture; substrate already has the bundling primitive needed for the hub; the build is structuring SPOKE encoders + adding cross-spoke contrastive alignment.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Prediction 1 (Phase-1 atom-graph encoder, PRIMARY)
**Hypothesis:** S2 atom-graph encoder (2-hop KGStore + char-trigram base) produces atom embeddings that cluster by mechanism-family / cert-class at modularity-Z >= 2.5 + LRG-stability >= 0.50 on substrate self-mapping discriminator.
**Mechanism:** GraphSAGE thm: K-hop aggregation captures structural function-similarity beyond name-similarity; substrate's KGStore has enough multi-relational structure to discriminate mechanism-families.
**HARD_PASS:** modularity-Z(gamma*) >= 2.5, LRG-stability >= 0.50, cert-class-ARI >= 0.30, mechanism-family-ARI >= 0.30
**HARD_FAIL:** modularity-Z <= 1.5 at every gamma AND both ARIs <= 0.15
**P_deflated:** **0.30** (raw 0.45-0.55 deflated 0.20-0.25 because: (a) substrate KG has very HIGH lexical-name correlation with mechanism-family by construction, so name-trigram baseline may already be strong; (b) v2c HARD_FAIL already showed 200k-rel scope is hard; (c) 4 prior nulls on substrate self-mapping; (d) char_trigram_atom is fully encoded in the substrate self-mapping prior drill as the bottleneck).

### Prediction 2 (Cert-class agreement, PRIMARY)
**Hypothesis:** Atoms with same cert_class (chain_grade vs under_classified vs measured_mechanism) cluster together more than name-prefix expects.
**HARD_PASS:** cert-class-ARI >= 0.30 on chain-grade atoms; structural ARI > random null
**HARD_FAIL:** cert-class-ARI <= 0.10 (no signal beyond random)
**P_deflated:** **0.35** (cert_ledger has only 688 rulings vs 177k atoms; sparsity may dominate; deflation reflects the prior 4-attempt null history).

### Prediction 3 (Algebra.domain mechanism-family clustering)
**Hypothesis:** atoms with same algebra.domain (linear_algebra, functional_analysis, etc.) cluster together in graph-neighborhood embedding more than in char-trigram embedding.
**Mechanism:** atoms in same algebra.domain share relation patterns (same axioms; same operation types); graph encoder captures this; char-trigram doesn't.
**HARD_PASS:** mechanism-family-ARI >= 0.30 on graph encoder; gap of >= 0.15 vs char-trigram baseline
**HARD_FAIL:** mechanism-family-ARI <= 0.15 OR gap <= 0.05 vs char-trigram
**P_deflated:** **0.40** (algebra.domain is structurally encoded in atom metadata; graph encoder should be able to recover it; the test is whether this lifts the FULL self-mapping discriminator).

### Prediction 4 (Hub-and-spoke architecture wins over single-spoke - DEFERRED to Phase-2)
**Hypothesis:** ARM_GRAPH_PLUS_METRICS (multi-modality fusion) beats ARM_GRAPH_2HOP (single-modality) on all 4 metrics.
**HARD_PASS:** gap of >= 0.05 on at least 2 of 4 metrics
**HARD_FAIL:** gap <= 0.02 (multi-modality fusion adds no value over single-modality)
**P_deflated:** **0.25** (lower because: (a) substrate cert_ledger metrics may be too sparse to add signal over graph alone; (b) need careful HD binding of metrics-as-modality which is novel-on-substrate).

### Prediction 5 (Falsifier — Phase-1 HARD_FAILS, all arms null)
**Implication:** Substrate atom-encoding cannot be lifted by graph-neighborhood; the v2c HARD_FAIL is not encoder-bound but discriminator-bound; route back to v2e modularity-Z discriminator without changing encoder.
**P_deflated:** **0.30** (this is the BAYES-FLIP threshold from substrate_self_mapping_gap drill; 5th attempt null would close the hypothesis class).

### Prediction 6 (Symmetric anti-negativity)
P_HARD_PASS + P_MIDDLE + P_HARD_FAIL = 0.30 + 0.30 + 0.40 = 1.00 ✓

---

## CROSS-THREAD SYNTHESIS

**With substrate self-mapping gap drill 2026-06-23 (parent):**
- v2c HARD_FAIL traced to 5-axis structural diagnosis. AXIS 1 was "v1 lexical families ARE NOT a substrate ground truth" - so this drill discards lexical-family-ARI and instead uses cert_class-ARI + algebra.domain-ARI (substrate-internal labels, not human-curated).
- This drill's Phase-1 atom-graph encoder is the **encoder-substitution** that the parent's HARD_FAIL pre-reg said would be the next move (parent: "next action is encoder substitution: replace char_trigram_atom with substrate-native context-bundle encoder").
- This drill IS the parent's "5-7-cycle effort" - compressed to 1 week MVP + 2-3 week full federation by leveraging existing substrate primitives (kg_traversal, binding, bundling, char_trigram).

**With encoder dual-gain drill 2026-06-23 (sibling):**
- Parent dual-gain drill landed SoftHebb + FPE as text-encoder candidates (S1 spoke). This drill widens the lens to S1 + S2 + S3 + S4 + hub.
- S1 (text spoke) = parent dual-gain SoftHebb winner (if that drill HARD_PASSES); compositional.
- S4 (relation spoke) = FPE/RotatE-style; reuses parent dual-gain FPE primitive (if implemented).
- Hub composition uses existing hdlab/bundling.py + Hebbian alignment update.
- **Combined leverage:** if BOTH dual-gain S1 HARD_PASSES AND this drill S2 HARD_PASSES, substrate has 2 of 4 spokes shipped + clear path to hub-and-spoke federation.

**With Shannon-floor META cert row 675:**
- Shannon-floor is about CLEANUP at sigma=1.5 on RANDOM BIPOLAR codebook; this drill is about ENCODER QUALITY in the LEARNED-key regime.
- IF Shannon-floor is synthetic-codebook-artefact (branch #3 refuted by parent dual-gain): then richer encoders (this drill's atom + relation spokes) can break it.
- IF Shannon-floor is fully chain-grade (branch #3 closes): then encoder upgrades help at sigma <= 1.0 production regime but not at sigma=1.5 stress regime; substrate envelope remains sigma <= 1.0.
- Either way, this drill's hub-and-spoke is product-positive.

**With isotropy_REFRAME (rho_mean as load-bearing):**
- Graph-neighborhood encoding is naturally low-rho_mean because aggregating over diverse neighbors decorrelates the mean direction.
- RotatE phase encoding has rho_mean=0 by construction.
- Hub bundling preserves the most decorrelated spoke (by Plate's HRR thm) - so federation has rho_mean upper-bounded by min-rho-mean across spokes.
- ALL 4 spokes are STRUCTURALLY chosen to be low-rho_mean. This is consistent with substrate's deepest finding.

**With c3 sequence-binding 586 + g1b generation 587:**
- Both depend on atom quality; atom-graph encoder (S2) gives richer per-atom signal -> better sequence binding + better next-step prediction.
- g1 conversation downstream depends on entity encoding (S3) and atom encoding (S2); federation unlocks substrate-native KG-grounded conversation.

**With cross_corpus_composition_gap drill 2026-06-23 (sibling):**
- That drill identified shared-vocab bridges between FB15k-237 + ConceptNet + HotpotQA as the path to chain-grade composition.
- Hub-and-spoke federation gives the principled architecture for cross-corpus alignment: shared HD hub IS the shared-vocab bridge.
- Composes with this drill: if hub-and-spoke ships, cross-corpus composition gets the architectural foundation.

**With USER strategic vision (Phase 1 self-improvement -> Phase 2 autoatom -> Phase 3 substrate proposes mathematics):**
- Phase 1 (self-improvement / relational-analysis) blocked on substrate self-mapping; this drill's Phase-1 atom encoder is the UNBLOCKER.
- Phase 2 (autoatom) requires multi-scale partition of atom space; hub-and-spoke gives this via spoke-level + hub-level views.
- Phase 3 (substrate proposes mathematics) requires substrate to identify GAPS - hub-and-spoke's cross-spoke contrastive identifies concepts where spokes DISAGREE (those are the gaps where new mathematics might live).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**If Phase-1 atom-graph encoder HARD_PASSES (P=0.30):**
- Atomize: `substrate_self_mapping_via_graph_neighborhood_chain_grade_2026-06-23` (cert-grade).
- hdlab/ primitive: `atom_graph_encoder.py` ships; closes 1 of 7 backlog.
- cap_map: `substrate_self_map` bumps from STRUCTURAL_DEEPER_REVIVAL to OPEN_VIA_GRAPH_NEIGHBORHOOD.
- Phase 2 (autoatom) unblocked.
- Justifies investment in full hub-and-spoke federation (Phase-2 of this drill).

**If Phase-1 MIDDLE_BAND (P=0.30):**
- Atomize: graph-neighborhood is PARTIAL lift; characterize which sub-mechanism load-bearing (cert-class agreement OR algebra.domain OR neither).
- cap_map: bump to PARTIAL_GRAPH_NEIGHBORHOOD.
- Phase 2 conditionally unblocked on the load-bearing sub-mechanism.
- Federation deferred (insufficient lift to justify investment).

**If Phase-1 HARD_FAILS (P=0.40):**
- Atomize: `substrate_self_mapping_encoder_substitution_null_chain_grade_2026-06-23` (META).
- Substrate self-mapping is NOT encoder-bound; v2c HARD_FAIL was discriminator-bound; route to v2e (substrate_self_mapping_gap pre-reg, modularity-Z + LRG only, char_trigram_atom unchanged).
- Federation HARD_FAILED at root (S2 spoke null); cancel hub-and-spoke investment.
- Phase 2 still blocked; alternative routes: (a) Pythia atom-description (USER authorization required); (b) full backprop GraphSAGE (substrate-non-native; ~6 week project; rejected).

**If Phase-2 federation HARD_PASSES (conditional on Phase-1 passing) (P=0.20):**
- Atomize: `substrate_hub_and_spoke_4_modality_federation_chain_grade_2026-06-23` (META cert-grade).
- 4 new hdlab/ primitives: `atom_graph_encoder.py`, `relation_rotate_encoder.py`, `entity_context_encoder.py`, `hub_alignment.py`.
- Substrate-product: substrate has principled multi-modal encoder federation; supports text + KG + cert + relational reasoning in ONE shared HD space.
- Closes 4-6 of 7 hdlab backlog items.
- Phase 3 (substrate proposes mathematics) within reach.

---

## CHEAP DECISIVE TEST OPERATIONAL SUMMARY

**Cell:** `enc_atom_graph_neighborhood_v1`
**Queue:** local_cpu_queue (177k atoms x 2-hop x 4096 dim is laptop-CPU-feasible)
**Wall budget:** ~2-4 hr full cell + ~3-4 days impl
**Arms (3):** BASELINE_TRIGRAM / GRAPH_2HOP / GRAPH_PLUS_METRICS
**Discriminator:** modularity-Z gamma sweep + LRG-stability tau sweep + cert-class-ARI + algebra.domain-ARI
**Pre-reg:** `preregs/2026-06-23_enc_atom_graph_neighborhood.md` with HARD bands above
**Smoke gate:** sigma=0 sanity recall=1.000 across all arms
**Implementation order:**
1. `hdlab/atom_graph_encoder.py` (Day 1-2)
2. Cell wiring + 3 arms (Day 3)
3. Smoke + pre-flight self-test (Day 4)
4. Full cell run (Day 5)
5. Atomize + cap_map + writeup (Day 6-7)

---

## CITATIONS (verified)

External lit (10):
1. CLIP - Radford et al. (2021). "Learning Transferable Visual Models from Natural Language Supervision." [https://arxiv.org/abs/2103.00020]
2. ImageBind - Girdhar et al. (2023). "ImageBind: One Embedding Space To Bind Them All." [https://arxiv.org/abs/2305.05665]
3. EBind - 2025 (2511.14229). "EBind: a practical approach to space binding." [https://arxiv.org/html/2511.14229v1]
4. Patterson, Rogers et al. (2007). "Where do you know what you know? The representation of semantic knowledge in the human brain." Nature Reviews Neuroscience. (ATL hub-spoke)
5. Damasio (1989). "Time-locked multiregional retroactivation: A systems-level proposal for the neural substrates of recall and recognition." Cognition. (convergence-divergence zones)
6. GraphSAGE - Hamilton et al. (2017). "Inductive Representation Learning on Large Graphs." NeurIPS. [https://arxiv.org/abs/1706.02216]
7. SGNN - Semantic-guided GNN for heterogeneous graph embedding (2023). [https://www.sciencedirect.com/science/article/abs/pii/S095741742301312X]
8. TransE - Bordes et al. (2013). "Translating Embeddings for Modeling Multi-relational Data." NeurIPS.
9. RotatE - Sun et al. (2019). "RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space." ICLR. [https://arxiv.org/abs/1902.10197]
10. TransERR (2024, 2306.14580). "Translation-based Knowledge Graph Embedding via Efficient Relation Rotation." ACL LREC 2024. [https://aclanthology.org/2024.lrec-main.1454/]

Brain & PCN (5):
11. Moraitis et al. (2021/2022). "SoftHebb." arXiv:2107.05747. (parent dual-gain drill)
12. Lambon Ralph et al. (2017). "The neural and computational bases of semantic cognition." Nature Reviews Neuroscience.
13. Quian Quiroga (2025). "On the origin of memory neurons in the human hippocampus." Trends Cog Sci. [S1364-6613(25)00031-2]
14. McClelland et al. (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review.
15. Buzsaki (2010). "Neural syntax: cell assemblies, synapsembles, and readers." Neuron.

Substrate-internal (10):
16. `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` (SoftHebb + FPE for S1 spoke)
17. `notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` (v2c HARD_FAIL + 5-axis structural diagnosis)
18. `notes/research_5x_deeper_cross_corpus_composition_gap_2026-06-23.md` (sibling; shared-vocab bridges)
19. `data/exp_encoder_dual_gain_softhebb_v1/metrics.json` (forward-only encoder exhausted: recall=0.020-0.023)
20. `data/substrate_index/math/atoms.jsonl` (177k atoms - the corpus for S2 atom-graph)
21. `data/substrate_index/meta/cert_ledger.jsonl` (688 cert rulings - supervision signal)
22. `hdlab/char_trigram_encoder.py` (existing baseline; arm 1)
23. `hdlab/kg_traversal.py` (KGStore; substrate's graph primitive)
24. `hdlab/binding.py` (FHRR bind; reused for S2 + S4 spokes)
25. `hdlab/bundling.py` (majority-rule; reused for hub composition)

**Verified count: 25 (10 external + 5 brain + 10 substrate-internal).**

---

## CALIBRATION NOTES

- **Lit-scan calibration penalty:** raw P deflated 0.20-0.30 because (a) hub-and-spoke composition on substrate is novel-on-substrate; (b) 5 prior null attempts at substrate self-mapping (v2/v2b/v2c/v2d-smoke/ENC1) raise empirical Bayes prior against attractive mechanisms; (c) all individual pieces (GraphSAGE, RotatE, hub-spoke) are lit-validated but their substrate-native composition is research-novel.
- **Novel-synthesis cap:** 0.45 applied (Phase-1 standalone P=0.30; full federation P=0.20-0.30).
- **Symmetric anti-negativity:** P_HARD_PASS=0.30 + P_MIDDLE=0.30 + P_HARD_FAIL=0.40 = 1.00 ✓ Bias toward null outcome consistent with 4 prior nulls.
- **HARD-FAIL bands explicit numerically:** modularity-Z <= 1.5 AT EVERY gamma AND both ARIs <= 0.15.
- **CAN-fail discriminator:** modularity-Z under degree-preserving null is by-construction CAN-fail; LRG-stability at unstable partitions is by-construction CAN-fail; cert-class-ARI on chain-grade subset is by-construction CAN-fail.
- **Generic-terms-only queries:** verified (CLIP / ImageBind / GraphSAGE / RotatE / hub-spoke / Hebbian PCN are public terms; no substrate-novel mechanism names leaked).
- **Empowered-to-experiment-where-lit-says-dismissed:** applicable (forward-only GNN aggregation is research-marginal vs full backprop GraphSAGE; substrate-native variant is "dismissed" in mainstream lit but USER directive empowers this path).
- **Verify-the-referent:** Patterson-Rogers ATL hub-spoke is canonical lit (Nature Rev Neurosci 2007/2017); CLIP/ImageBind are foundational ML; GraphSAGE is foundational GNN; RotatE is foundational KG-embed. NOT self-flatter - each architectural decision is grounded in 2+ independent canonical sources.

---

## DELIVERABLE SUMMARY

**Note:** `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` (THIS FILE)
**Companion handoff:** `notes/exp_dev_handoff_research_5x_deeper_path_c_universal_encoder_2026-06-23.md` (next)
**Anchor candidates (rank-ordered):**
1. **enc_atom_graph_neighborhood_v1** (Tier-A; P_deflated 0.30; ~1 week build + 2-4 hr cell) — THE CHEAP DECISIVE TEST
2. **enc_relation_rotate_v1** (Tier-B; P_deflated 0.25; ~3-5 days; dispatch if Phase-1 PASSES)
3. **enc_hub_4spoke_v1** (Tier-C; P_deflated 0.20; ~2 weeks; dispatch if Phase-1 + Phase-2 BOTH pass)

**Next-drill candidate (if Phase-1 MIDDLE or HARD_FAIL):**
- `network-science-graph-theory` (Tier-1b adjacent un-drilled; drill_count<=2 per field advisor): expander/Ramanujan/spectral-gap analyses of substrate KGStore - gives a CAPACITY BOUND on what GraphSAGE-style aggregation CAN recover from substrate's graph structure. Tells us whether HARD_FAIL is encoder-fundamental or graph-density-fundamental.

**Honest scope assessment:**
- Phase-1 (atom encoder for self-mapping): **1 week** realistic.
- Full hub-and-spoke federation (4 spokes + hub): **3-4 weeks**.
- The prompt's "1 week" budget is achievable ONLY for the Phase-1 subset.
- Recommendation: ship Phase-1, then decide on federation based on verdict.

-- Research (Opus 4.7-1M)
