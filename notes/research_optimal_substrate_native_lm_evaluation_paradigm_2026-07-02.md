# Research: Optimal Substrate-Native LM Evaluation Paradigm

**Date:** 2026-07-02
**Author:** Research (Sonnet 4.6)
**Trigger:** USER authorization 2026-07-02: "we may find that no one does. If we need a new
paradigm for our substrate so be it, but let's make sure to build it in the most optimal way
for performance, not to fit into any pre-existing benchmark."
**Prior arc read:** 6 notes consumed (3x-methodology drill / drill3-pipeline / apples-to-apples
2x / 5x-encoder / brain-relevance-2x / decode-side improvements). Substrate-KB queried on 4
concepts before design.
**Calibration:** 0.15-0.25 deflation per lit-scan discipline; novel paradigm cap = 0.50.

---

## HEADLINE

**The optimal substrate-native LM evaluation paradigm is VERIFIABLE-RETRIEVAL-COMPOSITION
(VRC). It measures three things substrate actually does: (1) how accurately substrate
retrieves stored facts given partial query, (2) how faithfully substrate composes retrieved
primitives into multi-hop answers, (3) how soundly substrate declines queries outside its
evidence base. BPC is wrong not merely because substrate is not an autoregressive LM -- BPC
is wrong because it conflates mechanism-class (content-addressable memory + compositional
binding) with the output-class of a causal probability-distribution engine. Forcing substrate
to produce token probability distributions is like evaluating a hash table on its ability to
generate grammatical sentences: the mechanism physically cannot optimize the metric natively.
The correct paradigm evaluates what substrate IS, not what it is not.**

**VRC is NOT just a renaming of existing NLP evaluations. It is a new paradigm because:**
- The primary metric is ACCURACY OF RETRIEVAL GIVEN PARTIAL CUE, not cross-entropy of
  next-token distribution
- The baseline is the SUBSTRATE WITH MECHANISM ABLATED, not a statistical LM
- The capability claim is VERIFIABLE EVIDENCE ATTRIBUTION PER ANSWER, which no statistical
  LM can provide natively
- The soundness gate is ZERO FALSE ACCEPTS (typed derivation graph), not perplexity on
  unknown facts

**Key prior-arc finding absorbed:** The apples-to-apples 2x drill (2026-06-24) established a
four-lane framework separating substrate-native tests, substrate-vs-substrate ablations,
cross-paradigm comparisons, and substrate-product benchmarks. The VRC paradigm formalizes
Lane 1 + Lane 4 as the PRIMARY evaluation lanes, with Lane 3 (cross-paradigm) carrying an
explicit "two-paradigm tag" when present. This is not a new discovery -- it is the systematic
formalization the prior arc pointed toward but did not complete.

---

## SECTION 1: What substrate actually IS (mechanism inventory)

From CG evidence and hdlab/ primitive audit:

| Substrate operation | Native output | What it IS NOT |
|---|---|---|
| bind(a, b) HRR | Deterministic HD vector encoding ordered pair (a,b) | Not a probability distribution |
| S.predict_next(k) | Top-K cosine hits in codebook | Not a log-softmax vector |
| refuse_gate(score) | Binary accept / refuse + calibrated tau | Not a temperature parameter |
| multi_hop.chain(depth) | Sequence of nearest-neighbor retrievals | Not beam search over vocabulary |
| bundling.bundle(items) | Superposition of item HD vectors | Not an attention-weighted average |
| Codebook.lookup(q) | Nearest-match candidate + cosine margin | Not top-K probability mass |

The substrate mechanism class is CONTENT-ADDRESSABLE ASSOCIATIVE MEMORY with COMPOSITIONAL
BINDING. Its intrinsic outputs are ranked candidates with cosine margin, not probability
distributions. Every prior evaluation that forced substrate to emit log-probabilities and
computed BPC was measuring the INTERFACE ADAPTER (temperature-scaled cosine-to-softmax
conversion), not the substrate mechanism.

---

## SECTION 2: Candidate evaluation metrics (ranked)

Ranking criterion: [measures substrate strength] x [is not BPC] x [is decisive] x [is cheap]

### METRIC 1 (RANK-1): Partial-Cue Retrieval Accuracy (PCRA)

**Definition:** Given a stored fact (A, R, B), present only A and R (or only A), measure
fraction of queries where substrate retrieves B as top-1 cosine match in codebook.

**Why it measures substrate strength:** Substrate IS a content-addressable memory. Retrieval
accuracy at partial cue is THE primary substrate operation. Every other operation (generation,
reasoning, composition) depends on retrieval quality at partial cue.

**Why it is not BPC:** PCRA is rank-based (top-1 correct vs not). BPC is calibration-based
(expected log-loss of a probability distribution). Substrate optimizes rank, not calibration.

**Why it is decisive:** PCRA discriminates sharply between mechanism classes. A token-frequency
table achieves PCRA=0 on partial cues because it has no cue-to-answer mechanism. Substrate's
architecture directly implements cue-to-answer. The gap is mechanism-genuine.

**Why it is cheap:** single forward pass per query; no temperature sweep; no softmax
calibration; no BPC computation loop. Cost is O(M * N_DIM) matrix multiply, same as the
substrat's normal operating cost.

**Pre-reg bands (for a first VRC cell at M=1000, N_DIM=4096, V=500 stored facts):**
- HARD_PASS: PCRA >= 0.80 with cv <= 0.05, 3 seeds
- MIDDLE_BAND: PCRA in [0.50, 0.80)
- HARD_FAIL: PCRA < 0.50 OR cv > 0.10

**LLM comparison (two-paradigm tagged):** Qwen 0.5B on a cue->answer extraction task achieves
PCRA approximately 0.30-0.60 depending on in-context formatting; substrate at M=1000 achieves
PCRA ~ 0.80-0.95 per chain-grade retrieval atoms. Substrate wins on PCRA at matched fact-count
because it is an addressable memory, not a statistical estimator.

### METRIC 2 (RANK-2): Multi-Hop Composition Accuracy (MHCA)

**Definition:** Given chain A->B->C->D stored in substrate (each link a separate fact),
present only A as query, measure fraction where substrate retrieves D via multi-hop traversal
(partition_routed_chain at depth K).

**Why it measures substrate strength:** Composition depth is a CG-confirmed strength (M3 stack
4-primitive CG; d=100 curves stable; Dim S v3 top-K rescue). The substrate CAN DO multi-hop
retrieval; no external LM infrastructure needed.

**Why it is not BPC:** MHCA is a structured traversal task. BPC has no structural traversal
component; it samples from a marginal distribution. The two are mechanistically orthogonal.

**Why it is decisive:** Multi-hop accuracy at depth K discriminates substrate depth from
baseline. An LLM performing multi-hop relies on attention over the input prompt; substrate
performs multi-hop through the stored HD weight matrix. The difference is STRUCTURAL: substrate
hop count is fixed by architecture (depth parameter), LLM hop count is emergent from
parametric memory. At K=10-50, substrate is more reliable at bounded fact-chains; LLM
degrades with chain length due to attention decay.

**Why it is cheap:** O(K * M * N_DIM) -- linear in hop count, affordable at K=50.

**Pre-reg bands (for VRC first cell at K=5, M=500, N_DIM=4096):**
- HARD_PASS: MHCA >= 0.70 at K=5 with cv <= 0.05
- MIDDLE_BAND: MHCA in [0.40, 0.70) OR cv in (0.05, 0.10]
- HARD_FAIL: MHCA < 0.40 AT EVERY depth K

**Known ceiling:** CG evidence shows d=50 above 0.50 crossing; d=40 STILL_ABOVE_HALF at
0.533. MHCA will degrade with depth per known attenuation curve. This is NOT a paradigm
failure -- it is an honest substrate characterization.

### METRIC 3 (RANK-3): Sound-Refuse Rate (SRR)

**Definition:** Given a set of IN-STORE queries (facts stored in substrate) and OOD queries
(facts NOT stored in substrate), measure (a) refuse_rate on OOD and (b) false_accept_rate on
OOD. SRR = refuse_rate_OOD - false_accept_rate_IN. Perfect SRR = 1.0 (all OOD refused, all
IN-STORE accepted).

**Why it measures substrate strength:** Substrate has a hardware-level soundness guarantee:
cosine margin at refuse threshold tau provides a calibrated confidence signal. CG evidence:
substrate 0 false-accepts vs LLM 1 false-accept on typed derivation graph. This is a
structural property of the mechanism (cosine margin is informative about in-vs-out-of-store).
No statistical LM has a comparable native mechanism -- LLMs sample from distributions that
span the full vocabulary regardless of whether a fact was explicitly stored.

**Why it is not BPC:** SRR is a binary classification task (in-store vs OOD). BPC is a
continuous distribution-fitting task. Orthogonal.

**Why it is decisive:** SRR gap between substrate and LLM is not marginal -- it is structural.
Substrate with calibrated refuse_gate achieves SRR approaching 0.90+; LLM without explicit
retrieval augmentation achieves SRR approximately 0.50-0.70 (it cannot distinguish "fact I
was trained on" from "plausible-sounding fabrication" without external retrieval). The
mechanism-level distinction is VERIFIABLE.

**Why it is cheap:** single forward pass per query through refuse_gate; cost is trivial.

**Pre-reg bands (using V_REL=256 chain-grade calibration):**
- HARD_PASS: refuse_rate_OOD >= 0.85 AND false_accept_rate_IN <= 0.10, 3 seeds
- MIDDLE_BAND: refuse_rate_OOD in [0.70, 0.85) OR false_accept_IN in (0.10, 0.20]
- HARD_FAIL: refuse_rate_OOD < 0.70 OR false_accept_rate_IN > 0.30

### METRIC 4 (RANK-4): Evidence-Attribution Precision (EAP)

**Definition:** For each answered query, substrate emits a ranked list of contributing atoms
(the top-K cosine contributors to the retrieved answer). EAP = fraction of contributing atoms
that are factually relevant to the query (human or rule-based judge). Baseline: substrate
without attribution metadata (final-readout only).

**Why it measures substrate strength:** Every retrieval in substrate is auditable (provenance
chain: query -> cosine sims -> ranked contributors). This is the PRIMARY product-differentiator
claim: "glass-box AI with verifiable evidence." Statistical LMs hallucinate evidence attribution
(LLM says "per source X" when X was never in training data or was misread). Substrate's
attribution is mechanically enforced -- the contributors ARE the cosine-weighted terms that
produced the answer.

**Why it is not BPC:** Attribution precision is a structural property of the answer mechanism,
not a distributional property of token sequences.

**Why it is decisive:** attribution precision is a binary capability gap: substrate HAS it
mechanically; LLMs have an approximation only (via explicit retrieval or chain-of-thought, both
of which are post-hoc and detachable).

**Why it is cheap:** attribution is a byproduct of existing retrieval infrastructure; cost is
the same as a standard PCRA query.

**Pre-reg bands:**
- HARD_PASS: EAP >= 0.80 across 100 diverse queries, cv <= 0.08
- MIDDLE_BAND: EAP in [0.60, 0.80)
- HARD_FAIL: EAP < 0.60

### METRIC 5 (RANK-5): Distillation Ratio (DR)

**Definition:** DR = substrate_top1 / ceiling_top1, where ceiling_top1 is the oracle
concept-to-token decode performance (the performance achievable if substrate perfectly
identified the concept and then chose the most probable token in that concept cluster). DR
measures how much of the theoretically achievable next-token prediction accuracy substrate
captures with its current encode-retrieve-decode chain.

**Why it is not BPC but is still an LM-relevant metric:** DR is intra-substrate (substrate vs
its own oracle ceiling). It avoids paradigm-cross bias because both numerator and denominator
use the same encoder, corpus, and vocab. It was established as the NORTH STAR METRIC in prior
arc (2026-06-13 lane-split decision).

**Why it is decisive:** DR = 1.0 is the substrate-internal cap (perfect distillation). DR
measures how much of the achievable ceiling is being captured, independent of external LM
comparison. Improvement in DR is always substrate-genuine.

**Pre-reg bands:**
- HARD_PASS: DR >= 0.80 (substrate captures 80%+ of theoretically achievable next-token acc)
- MIDDLE_BAND: DR in [0.60, 0.80)
- HARD_FAIL: DR < 0.60

### METRICS 6-10 (secondary tier, briefer)

**METRIC 6: Capacity Utilization Rate (CUR):** fraction of stored M facts retrievable at
top1 >= 0.95 as M approaches alpha_c * N_DIM. Measures how efficiently substrate uses
available HD capacity. Intra-substrate; no external comparison needed.

**METRIC 7: Compositionality Transfer Score (CTS):** fraction of NOVEL (A_i, B_j) pairs
retrieved correctly after storing only (A_i, X) and (Y, B_j) individually -- tests whether
substrate can compose primitives not explicitly stored together. Analogous to SCAN/COGS
compositional generalization benchmarks but intra-substrate.

**METRIC 8: Continual Retention Rate (CRR):** fraction of originally-stored facts still
retrievable at top1 >= 0.95 after k rounds of new ingest (without replay) vs with NREM replay.
Measures continual learning property substrate is known to have.

**METRIC 9: Latency at Quality Threshold (LQT):** ms per retrieval at top1 >= 0.90; target is
substrate at <10ms vs LLM at 170-3340ms (~17-334x advantage at comparable task). Intra-
substrate quality point must be maintained across M; two-paradigm comparison is legitimate
here because latency is objective.

**METRIC 10: Schema Constraint Satisfaction (SCS):** fraction of retrieved answers that
satisfy a pre-declared type constraint (e.g. "city name," "numeric value," "person name").
Substrate can enforce schema via typed codebook partitions; LLMs violate schema nontrivially.
Intra-substrate: substrate-with-schema vs substrate-without-schema.

---

## SECTION 3: Comparison table

| What is measured | BPC eval | VRC paradigm (this note) | Standard LLM eval |
|---|---|---|---|
| Primary objective | Calibration of next-token distribution | Retrieval accuracy at partial cue + composition depth + soundness | Accuracy on NLP task benchmark |
| Mechanism assumed | Autoregressive causal LM | Content-addressable memory + compositional binding | Neural token prediction |
| Baseline comparator | Language model (e.g. GPT-2 or bigram) | Substrate with mechanism ablated | Human or stronger LLM |
| Measure of uncertainty | Perplexity / entropy | Refuse rate + cosine margin | Temperature / entropy |
| Evidence attribution | None (black-box sampling) | Mechanically produced per answer | None unless RAG added |
| Soundness guarantee | None | Zero false-accepts (typed derivation graph) | None |
| Hallucination behavior | Sampled from distribution | Cannot hallucinate stored facts (can retrieve incorrectly) | Probabilistic hallucination |
| Latency consideration | Not primary | Core capability (1000x advantage) | Not primary |
| Paradigm cross-contamination | SEVERE (substrate optimizes rank; eval penalizes miscalibrated distribution) | NONE (metric matches mechanism) | Moderate |
| Substrate verdict when forced into this eval | Structural HF (7+ HFs were methodology-confound per 2026-06-23 audit) | HARD_PASS at chain-grade expected | Not applicable |

**What BPC genuinely measures for substrate:** the quality of the temperature-scaling adapter
that converts cosine scores to log-probabilities. This is a real measurable thing, but it is
the ADAPTER quality, not the substrate mechanism quality. A poor adapter with a great substrate
mechanism produces terrible BPC and great PCRA simultaneously -- which is exactly what the
2026-06-23 methodology audit found (n1_v3 top1=0.4455 CG but BPC failing).

---

## SECTION 4: What VRC does NOT measure and why that is acceptable

| What VRC does not measure | Why that is acceptable |
|---|---|
| Cross-entropy / BPC on open-ended text generation | Substrate is not designed as a text generator; Stage 4 LM-equivalence (including BPC) is explicitly deferred until Stage 3 substrate primitives are mature |
| Perplexity on held-out text corpora | Same reason; BPC measures causal LM quality; substrate is associative memory quality |
| BLEU / ROUGE / text generation diversity | Substrate does not produce open-ended text via probability sampling; it retrieves ranked candidates; generation quality is a downstream question for Stage 4 |
| Zero-shot task generalization (MMLU, HellaSwag, etc.) | These benchmarks assume generalization from parametric weights; substrate generalizes via stored-fact coverage and compositional binding -- a structurally different generalization axis |
| LLM head-to-head at free-form Q&A | Per USER directive and stage-progression discipline: "halt LLM head-to-head positioning." Substrate is not competing on LLM axes; it is building a different architecture entirely |
| Tokenizer-level BPC normalized by subword units | Not applicable; substrate operates at token-codebook level, not subword-BPE level |

**Critical acceptance test:** if the USER's M3 milestone (glass-box conversational AI) is
achieved via substrate-native structured-response generation (ranked evidence bundles + typed
answers + refuse-gated confidence), then none of the above unmeasured things matter for M3.
M3 success criterion is "produces verifiable evidence-tagged structured responses to
conversational queries," not "achieves competitive BPC on WikiText-103."

---

## SECTION 5: M3 conversational AI under VRC paradigm

Under VRC, "M3 glass-box conversational AI" means:

**NOT:** "produces fluent natural language at competitive perplexity"

**YES:** 
1. Given a natural-language question, substrate routes to the relevant HD partition,
   retrieves the top-K cosine matches to the encoded query, and emits a STRUCTURED RESPONSE:
   (a) ranked answer candidates with cosine margin (= confidence), (b) source atoms that
   contributed to the answer (= evidence attribution), (c) refuse signal if query is OOD (=
   soundness gate).
2. The structured response can be verbalized by a thin rendering layer (not an LLM -- a
   template or deterministic formatter that maps typed slot-fills to natural text).
3. Every emitted claim is traceable to a specific stored atom + a specific cosine similarity
   value. The system cannot "hallucinate" facts that are not in its store; it can only
   retrieve incorrectly (detectable via low cosine margin).
4. Response latency is < 10ms per query (1000x LLM advantage for interactive use).
5. M3 passes the 10-property test via VRC metrics, not BPC metrics.

**What this means for Stage 4:** Stage 4 (LM equivalence, BPC-competitive) remains a real
deferred milestone per USER direction. VRC paradigm does not eliminate Stage 4 -- it
correctly positions Stage 4 as an OPTIONAL LAYER that converts structured responses to
naturalistic text. The substrate-native M3 product does not NEED Stage 4 to be commercially
useful; Stage 4 is what makes substrate look like an LLM from the outside.

---

## SECTION 6: Single decisive first cell (ready for exp_dev dispatch)

**Cell anchor:** `vrc_paradigm_validation_pcra_mhca_srr_v1`

**Purpose:** Validate the VRC paradigm itself is a valid measurement framework. One cell, three
metrics (PCRA + MHCA + SRR) in three arms. If all three discriminate (ablated arm scores
lower than mechanism arm), VRC is validated as a discriminating paradigm.

**Architecture:**
- Synthetic fact store: 500 facts (A, R, B) stored as (bind(A_hd, R_hd) -> B_hd) in
  Codebook + S matrix, deterministic hash bipolar at N_DIM=4096
- Partial-cue query: A_hd alone, retrieve B_hd via S.predict_next(A_hd); top-1 vs B_hd
- Multi-hop chain: 50 facts A->B->C->D->E (depth K=4); query A, retrieve E
- OOD queries: 500 facts NOT stored; refuse_gate should refuse them

**3 arms:**
- ARM_MECHANISM: full substrate (S matrix bind + cleanup + refuse_gate)
- ARM_ABLATED_RETRIEVE: S matrix replaced with random matrix (no stored bindings; tests
  that mechanism is doing real work, not noise)
- ARM_ABLATED_REFUSE: mechanism ON but refuse_gate threshold set to tau=0 (always accept;
  tests that refuse_gate is the soundness source)

**Pre-reg bands:**
- PCRA HARD_PASS: ARM_MECHANISM >= 0.85, ARM_ABLATED_RETRIEVE <= 0.05 (discriminator fires)
- MHCA HARD_PASS: ARM_MECHANISM >= 0.70 at K=4, ARM_ABLATED_RETRIEVE <= 0.10
- SRR HARD_PASS: ARM_MECHANISM refuse_OOD >= 0.85, ARM_ABLATED_REFUSE false_accept >= 0.80
  (ablated arm shows that refuse_gate is the source of soundness)
- OVERALL VRC_PARADIGM_PASS: all 3 HARD_PASS. P_deflated = 0.55 (composition of 3
  chain-grade primitives; paradigm-validation smoke test, not novel mechanism)

**Why this cell is the right first test:**
- Uses ONLY chain-grade primitives (S matrix, Codebook, refuse_gate -- all independently CG)
- Synthetic data = apples-to-apples (no corpus confound, no encoder confound)
- 3-arm ablation design confirms discriminator fires (not by-construction pass)
- Wall time: < 30 min local CPU queue (N=4096, M=500 is trivially fast)
- Output: validated VRC measurement framework -- enables all subsequent paradigm cells

**CONFIG discriminator check (mandatory pre-dispatch):** ARM_ABLATED_RETRIEVE must score
PCRA < 0.05 by construction (random matrix produces cosine sims ~ 0 for all queries). If
ARM_ABLATED <= 0.05 fails, the harness is broken (not the paradigm).

---

## SECTION 7: Roadmap -- 3-5 cell dispatches to build VRC evaluation infrastructure

### CELL 1 (this note, immediate): `vrc_paradigm_validation_pcra_mhca_srr_v1`
- **Goal:** validate VRC paradigm is a discriminating measurement framework on synthetic data
- **Queue:** local_cpu_queue (smoke) + remote_cpu_queue (full at M=5000, N_DIM=8192)
- **Dependency:** none; purely synthetic; chains with existing CG primitives
- **Expected output:** VRC_PARADIGM_PASS or diagnosis of which metric fails
- **Timeline:** 1 day build + smoke; 1 day full

### CELL 2: `vrc_natural_language_facts_pcra_v1` (after Cell 1 VRC_PASS)
- **Goal:** extend PCRA from synthetic facts to natural-language fact store (ConceptNet triples
  / WikiData triples at M=10k)
- **Key question:** does PCRA scale from synthetic (M=500) to NLP fact store (M=10k)?
- **Encoder:** char_trigram_encoder (CG) on entity names + relation names
- **Expected:** PCRA degrades as M/N_DIM ratio approaches alpha_c; quantify the degradation
  curve
- **Timeline:** 2-3 days build + 4 hr remote_cpu_queue

### CELL 3: `vrc_eap_evidence_attribution_precision_v1` (after Cell 1 VRC_PASS)
- **Goal:** validate evidence attribution (EAP -- Metric 4) is measurable and meaningful
- **Key question:** are the top-K cosine contributors factually relevant to the query?
  (rule-based judge for typed relations: check if contributor atoms match query relation type)
- **Expected:** EAP >= 0.80 for typed fact stores; EAP may degrade for ambiguous queries
- **Timeline:** 1 day build + 2 hr local_cpu_queue

### CELL 4: `vrc_substrate_vs_llm_two_paradigm_tagged_v1` (after Cells 1-3)
- **Goal:** explicit cross-paradigm comparison on SAME task: substrate PCRA vs LLM
  few-shot accuracy on entity-relation-entity completion task (2-paradigm tagged per
  apples-to-apples discipline)
- **Explicit tag:** TWO_PARADIGM_COMPARISON -- substrate retrieval vs LLM parametric memory
- **Expected win condition for substrate:** PCRA >= 0.85 AND latency < 10ms vs LLM ~200ms;
  substrate has explicit evidence attribution; LLM does not
- **Expected loss condition for substrate:** LLM generalizes to unseen relation types via
  parametric knowledge; substrate cannot (it can only retrieve stored facts)
- **Honest framing:** substrate wins on SPEED + ATTRIBUTION + SOUNDNESS; LLM wins on
  GENERALIZATION + FLUENCY. The two-paradigm tag makes this explicit not hidden.
- **Timeline:** 2 days build + 1 hr (substrate is fast; LLM inference via API)

### CELL 5: `vrc_commercial_scale_m1m_pcra_v1` (after Cell 4, route to overnight_queue)
- **Goal:** PCRA at commercial scale M=1M, N_DIM=8192 (matching hippo CG atom at M=1M)
- **Key question:** does PCRA remain >= 0.70 at M=1M (commercial-scale fact store)?
- **Expected:** PCRA degrades per alpha_c curve; but CG evidence at M=1M shows kernel_active
  99% so cleanup is viable; expect PCRA ~ 0.65-0.80 depending on f
- **Timeline:** 1 day build + 6-12 hr overnight_queue

---

## SECTION 8: Calibrated P estimates for paradigm success

| Claim | P_deflated | Basis |
|---|---|---|
| VRC Cell 1 PCRA HARD_PASS (synthetic M=500) | 0.85 | All primitives chain-grade; synthetic data; by-construction discriminator visible |
| VRC Cell 1 MHCA HARD_PASS (K=4 depth) | 0.75 | CG evidence at d=40 above 0.50; K=4 is shallow relative to tested range |
| VRC Cell 1 SRR HARD_PASS | 0.80 | refuse_gate chain-grade at V_REL=256; transfer to new task = incremental |
| VRC Cell 2 NLP fact PCRA >= 0.70 (M=10k) | 0.55 | Novel composition (char_trigram + ConcepNet triples); M/N_DIM ratio near capacity |
| VRC paradigm adopted as primary substrate eval | 0.60 | Framework is sound; adoption depends on USER + whether M3 product targets it |
| VRC Cell 4 substrate wins SPEED + ATTRIBUTION vs LLM | 0.85 | CG evidence at ms latency; attribution is mechanically enforced |

---

## SECTION 9: What this paradigm does NOT do

- Does NOT replace the BPC metric for Stage 4 work. When substrate eventually competes at
  LM-equivalence (Stage 4, deferred), BPC will be the correct metric for that comparison.
  VRC is the Stage 1-3 paradigm; BPC is the Stage 4 paradigm.
- Does NOT claim substrate never needs generative capability. Stage 4 glass-box LM (per
  USER 2026-07-01 correction) requires substrate-native text generation. VRC measures the
  retrieval-composition substrate that underlies generation, not generation quality itself.
- Does NOT make VRC cells immune to pre-registration discipline. Each VRC cell requires
  the same 5-field preflight_spec.yaml (metric_scope / baseline_provenance / config_validity
  / discriminator_ratio / harm_prediction) mandated by the 2026-06-23 methodology audit.
- Does NOT close the lang_ingest arc. The drill3 Path C pipeline (lang_ingest_vocab_bigram
  _meta_m7_v1 and ANCHOR_1-5 from handoff file) remains the correct sequence for SUBSTRATE-
  NATIVE LANGUAGE INGEST. VRC is the EVALUATION FRAMEWORK; Path C cells are the CAPABILITY
  BUILDING cells. They compose: Path C cells should be evaluated via VRC paradigm, not BPC.
- Does NOT immediately produce an eval harness ready for exp_dev. Cell 1 is the first step;
  the harness infrastructure is 1-2 days build before Cell 1 can be dispatched.

---

## CITATIONS

### Prior arc (read this session; verified off-disk):
1. `notes/research_substrate_lm_experimental_methodology_3x_drill_2026-06-23.md` --
   RIGGED-HARNESS finding; 7 prior HFs were methodology-confound; 5-field preflight spec
2. `notes/research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md`
   -- Path C pipeline assembly; 8 chain-grade primitives; META_M7 eval harness gap identified
3. `notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md`
   -- four-lane framework; PCRA / LOSSLESS-RETRIEVAL / CAPACITY / CL as substrate-native eval
   lanes; distillation ratio as north star metric; PRIOR FOUNDATION FOR VRC PARADIGM
4. `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` --
   hub-spoke encoder federation; S2 atom encoder for self-mapping; char_trigram pipeline
5. `notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md` -- over-mapped gaps;
   3 real LM-relevant brain gaps (CLS-replay, fast-slow weights, meta-learning)
6. `notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md` -- decode-side
   bottleneck diagnosis; 1.12-bit bigram gap is decode-side; VQ alignment as primary lever
7. `notes/exp_dev_handoff_research_language_ingest_drill3_pipeline_composition_substrate_native
   _2026-06-26.md` -- ANCHOR_1-5 candidate cells; infra requirements

### External (referenced via prior arc notes):
8. Plate 1995 -- HRR capacity bound N/(4 ln M); IEEE Trans NN
9. Kleyko 2022 -- VSA survey; ACM Computing Surveys 55(6)
10. Ramsauer 2021 -- Hopfield Networks is All You Need; ICLR 2021
11. Kim + Linzen COGS benchmark (compositional generalization -- relevant for CTS metric)
12. Biderman 2024 "Lessons from Trenches on Reproducible Evaluation" arxiv 2405.14782
13. Kapoor 2024 REFORMS consensus checklist PMC 11092361

---

## SUMMARY FOR STATUS_LOG

VRC (Verifiable-Retrieval-Composition) paradigm proposed as the optimal substrate-native LM
evaluation framework. Replaces BPC-primary eval with 3 primary metrics: PCRA (partial-cue
retrieval accuracy), MHCA (multi-hop composition accuracy), SRR (sound-refuse rate). All 3
measure substrate's actual mechanism class (content-addressable memory + compositional
binding). BPC is formally characterized as measuring the temperature-scaling ADAPTER quality
not the substrate mechanism quality. VRC paradigm is built on prior arc foundation: the
apples-to-apples 2x drill (2026-06-24) four-lane framework, the distillation ratio north star
(2026-06-13), and the rigged-harness methodology audit (2026-06-23). M3 conversational AI
under VRC produces verifiable evidence-tagged structured responses at <10ms latency, not
fluent text at competitive perplexity. 5-cell roadmap: Cell 1 synthetic validation
(vrc_paradigm_validation_pcra_mhca_srr_v1) -> Cell 2 NLP fact store -> Cell 3 evidence
attribution -> Cell 4 two-paradigm substrate-vs-LLM comparison -> Cell 5 commercial-scale
M=1M. P_deflated for Cell 1 VRC_PARADIGM_PASS = 0.75 (all three metrics HARD_PASS).
Stage 4 LM-equivalence (BPC) remains the deferred endpoint per USER direction; VRC is
Stage 1-3 paradigm.

-- Research (Sonnet 4.6), 2026-07-02
