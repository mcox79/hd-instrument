# 5x drill 1/5: empirical mechanism config sweep — brain-analog concept_encoder HF2 on substrate WordNet content

**Date:** 2026-07-02 late evening
**Drill role:** empirical rescue-path enumeration on the critical negative
**Drill trigger:** USER 2026-07-02 late evening "important negatives 5x drill"
**Companion drills:** math+info theory / neuroscience / physics+stat mech / ML lit (parallel)
**Anchor under review:** `substrate_concept_encoder_substrate_content_v1_2026_07_02`
**Verdict-as-landed:** HARD_FAIL_HF2 mechanism_r5=0.160 < max(baseline)=0.280 (ct=0.280 winner; cp=0.210 middle)
**Cell / prereg / metrics off-disk confirmed** (per verify-the-referent).

---

## 1. Prior-work check (substrate-KB concept-query MANDATORY)

Ran the required three queries via `bash tools/substrate_query.sh` with v2 schema flags.

| Query | Top hit | Cosine | Relevance |
|---|---|---|---|
| "sparse coding sparsification WordNet real corpus transfer" | `notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md::8.1 Sparse coding` | 0.3643 | Prior arc `wave14d_self_supervised_concepts` (0.360) framed sparse coding as domain-transfer story (Wikitext→code) with predicted transfer gap 50% (PPMI) vs 20% (sparse). Directly relevant. |
| "competitive Hebbian synonym retrieval bag of words baseline" | `wave14d_edit_then_query_research::Tier C Retrieval baselines` | 0.3262 | `research_drill_2x_hopfield_consolidation_revival_2026-06-27` (0.286) has section "B.2 Is BASELINE_HEBBIAN a valid baseline at all?". |
| "k sparsity threshold information transfer capacity" | `research_drill_rmt_beyond_free_probability_2x_2026-06-11::Capacity threshold detection (DBM)` | 0.3867 | **`research_drill_sparse_value_coding_within_shards_5x_2026-06-08.md::chunk090`** (0.341) — LOAD-BEARING prior arc that already grounds today's diagnosis: *"Recall capacity improves at K << N/2 only through matched filtering. Information capacity always decreases with K (fewer bits per fact). The right framing depends on whether KB facts are information-dense or information-sparse."* |

**Prior-work overlap check:** the KEY prior finding was already in the substrate. Sparse-value-coding drill 2026-06-08 stated the exact mechanism-diagnosis principle that predicts today's HF2: when facts are information-DENSE (WordNet definitions have distributed char-trigram signal across many dims), K << N/2 sparsification DESTROYS recall. When facts are information-SPARSE (25-cluster synthetic corpus, low-entropy templates), sparse coding wins. Cat/kitten CG at k=0.02 lived in the information-sparse regime; substrate-WordNet content is information-dense.

**Meta-observation:** the substrate ALREADY had the theory that predicts HF2 six weeks before this dispatch. Director should have concept-queried "k sparsity information density" pre-dispatch — the HF was foreseeable. Filing as recurrence of Fix-#28-adjacent (concept-query-before-dispatch violation despite substrate-KB v2 flags being available). No new directive needed; existing `feedback_substrate_kb_query_needs_v2_schema_flags_2026-07-01.md` covers.

---

## 2. Mechanistic diagnosis (before designing rescue sweeps)

Off-disk read of `hdlab/concept_encoder.py`:

- Surface: `CharPositionalEncoder` produces N_DIM=2048 float HD per sentence.
- Fit: per-concept Hebbian outer-product accumulator (dense N_dim float).
- Readout: top-K WTA + sign → `concept_hds[c, :]` stored as **int8** {-1, 0, +1}. At k_sparsity=0.02, k_effective = round(0.02 × 2048) = **41 non-zero dims out of 2048** per concept.
- Query: encode(held-out synonym) via `CharPositionalEncoder` (DENSE float HD) → cosine argmax against concept_hds table.

**Mechanistic failure mode (self-consistent with prior-work overlap #3):**
- Query HD is DENSE (all 2048 dims contribute char-trigram info).
- Concept HD is SPARSE (only 41 dims non-zero).
- Cosine(dense_query, sparse_concept) = sum_{i in top-41} (query[i] × sign[i]) / normalizations.
- The dot-product effectively **projects the query onto a 41-dim subspace** chosen by WTA at fit-time.
- Those 41 dims were selected to maximize per-concept accumulator magnitude — which favors HIGH-FREQUENCY DEFINITION dims, not necessarily dims that overlap with SYNONYM char structure.
- The bag-word char_trigram baseline retains ALL 2048 dims of the mean-bundle prototype (dense float), so it uses the full char signal at cosine argmax time.
- Result: mechanism r5=0.160 < baseline r5=0.280 because ~1980 dims of query information are DISCARDED by the sparse readout on the concept-side.

**Cell-author's original diagnosis** ("definition text shares char roots with synonyms; aggressive sparsification loses cheap signal") is directionally correct. This drill sharpens it: the failure is not "sparsification loses signal" in general; it is "K=41/2048 dims of the concept-side vs. K=2048/2048 dims of the query-side is an asymmetric projection that discards ~98% of query-relevant char-trigram overlap."

---

## 3. Config sweep design (which sweeps to run at smoke scale)

Six rescue-path candidates enumerated. Two are diagnostic; three are direct config sweeps; one is architectural.

### Sweep A — k_sparsity dose-response (HIGHEST-VALUE)
- k_sparsity ∈ {0.02 (baseline), 0.05, 0.10, 0.20, 0.50}
- k_effective at N=2048: {41, 102, 205, 410, 1024}
- Fixed N=100 atoms, 3 seeds, same corpus, same query-pattern.
- **One cell, 5 sub-conditions × 3 seeds × 3 arms (mechanism only sweeps k; baselines are k-invariant).**

### Sweep B — WTA-OFF ablation (DIAGNOSTIC)
- ARM_HEBBIAN_NO_WTA: same Hebbian accumulator, skip top-K WTA, sign-quantize the DENSE accumulator directly. concept_hds becomes {-1, +1} in ALL 2048 dims.
- If ARM_HEBBIAN_NO_WTA ≥ char_trigram baseline → WTA sparsification is the whole failure, Hebbian accumulator is fine.
- If ARM_HEBBIAN_NO_WTA ≈ mechanism r5=0.16 → Hebbian per-concept accumulator itself is discriminatively wrong for this task.

### Sweep C — N_DIM scaling (LOW-VALUE)
- N ∈ {2048, 4096, 8192, 16384} at k_sparsity=0.02 fixed.
- k_effective scales linearly: {41, 82, 164, 328}. Query-side scales too.
- **Prediction:** mild improvement; not decisive alone. Recommend ONLY if Sweep A shows k plateau below baseline (would test whether more dims restore SNR at fixed sparsity fraction).

### Sweep D — training-text augmentation (LOW-VALUE)
- Base: 3-4 sentences per atom (definition + 2 syns + hypernym-hint).
- Augmented: add paraphrases via hypernym→definition text; morphological variants (plural, past-tense); dictionary examples if present in atoms.jsonl metadata.
- **Prediction:** 0.02-0.05 gain, not decisive. More definition-text adds more char noise before it adds semantic anchoring; the encoder has no lexical understanding.

### Sweep E — query pattern (DIAGNOSTIC-ONLY, NOT substrate-content claim)
- (a) held-out synonym (current). (b) definition→synonym (trivial; definition text often contains synonyms). (c) synonym→definition. (d) hypernym-cluster retrieval (mechanism was CG'd on designer clusters; regime-match).
- **CAVEAT:** hypernym-cluster retrieval is REGIME-DRIFT back to the synthetic-cluster CG regime. HP earned here does NOT grant "mechanism works on substrate content"; grants only "mechanism reproduces CG when substrate provides designer-analog cluster structure." File as clarification of scope, not rescue of the claim.

### Sweep F — HRR-bind with substrate relations (ARCHITECTURAL REFRAME)
- Not a "rescue" of concept_encoder — a SUBSTITUTE mechanism.
- WordNet has hypernym/hyponym/meronym relations already ingested. Use HRR primitives (`bind(atom_hd, relation_hd)`) to construct a relational concept encoding. Retrieve by unbinding the query synonym's inferred relation-role.
- This LEVERAGES substrate's algebraic primitives instead of using competitive-Hebbian sparse coding.
- Score: if this works, it validates "substrate has algebraic-structural knowledge" — a DIFFERENT strategic claim than "brain-analog competitive-Hebbian works on substrate content."

---

## 4. Predictions per sweep dimension (calibrated P-estimates)

Calibration: lit-scan penalty applied (deflate 0.15-0.25); novel-synthesis cap at 0.50 per USER-locked discipline. All values MEASURED@target = recall@5_mean at N=100 3 seeds, EXPECTED — not measured.

| Sweep | Condition | Predicted r5 | P(exceeds max baseline=0.28) |
|---|---|---:|---:|
| A | k=0.02 (baseline replication) | 0.16 | (measured) |
| A | k=0.05 | 0.20 | 0.20 |
| A | k=0.10 | 0.25 | 0.35 |
| A | k=0.20 | 0.29 | 0.45 |
| A | k=0.50 | 0.28 | 0.40 |
| B | WTA-off, dense sign | 0.27 | 0.45 |
| C | N=8192, k=0.02 | 0.18 | 0.15 |
| D | +50% training text | 0.20 | 0.20 |
| E-d | hypernym-cluster query | 0.35 (regime-drift; different claim) | 0.60 (BUT different claim) |
| F | HRR-bind substrate relations | 0.40 (architectural substitute) | 0.50 (capped) |

**Highest rescue probability on the original claim ("mechanism has advantage on substrate WordNet content"):** Sweep A at k=0.20 with P=0.45, Sweep B (WTA-off) with P=0.45. These test the DIAGNOSED root cause (asymmetric dense-vs-sparse dot product) directly. Composite P(at least one of A-k=0.20 OR B rescues) using rough independence ≈ 1 - (1-0.45)(1-0.45) = **0.70** — but discount for shared failure mode (both tests target the same knob) → **0.55 composite**, still capped at 0.50 per discipline.

---

## 5a. v2 CELL PROPOSAL if any config rescues

**Anchor:** `substrate_concept_encoder_substrate_content_v2_k_sparsity_sweep_2026-07-03`

**Design:**
- Corpus: SAME 100 WordNet atoms (top-freq semcor, ≥3 synonyms, ≥20-char definition).
- Seeds: [11, 17, 23].
- 5 k_sparsity conditions × 3 arms per seed:
  - ARM_CONCEPT_ENCODER_k002 (baseline replication)
  - ARM_CONCEPT_ENCODER_k005
  - ARM_CONCEPT_ENCODER_k010
  - ARM_CONCEPT_ENCODER_k020
  - ARM_CONCEPT_ENCODER_k050
  - ARM_HEBBIAN_NO_WTA (dense sign; ablation)
  - ARM_CHAR_POSITIONAL_ONLY (baseline holdover)
  - ARM_CHAR_TRIGRAM_UNSUP (baseline holdover; the current winner)
- N_DIM=2048 (matched to fail case).
- Metric: recall@{1,5,10}, seed-mean + arm-differ hashes.

**HP bands (v2):**
- HP1 (rescue detected): at least one k in {0.05, 0.10, 0.20, 0.50} shows recall@5 ≥ 0.30 (strictly above char_trigram=0.28 + 5% band).
- HP2 (WTA-off diagnostic): ARM_HEBBIAN_NO_WTA recall@5 ≥ 0.28 → WTA is the sole culprit.
- HP3 (monotonicity): recall@5 non-decreasing in k up to k=0.20 (mechanism-consistency check).
- HF1 (no k rescues): all k in {0.05...0.50} recall@5 < 0.25 AND WTA-off < 0.25 → mechanism CANNOT rescue on substrate content; commit to Sweep F architectural substitute.

**Cell arch:** sequential CPU numpy (one cell, one loop over conditions inside the seed loop; concept_hds re-fit per k). Estimated wall: 5 conditions × 3 arms × ~1s = 15s per seed → 45s total smoke. Well under timeout.

**Pre-reg fields:** cardinality_ok=(8 arms × 3 seeds = 24 units expected). All standard META rules touched. baseline_in_band on ct baseline (should replicate 0.28).

## 5b. REFRAME if NO config rescues

If Sweeps A (all k) and B (WTA-off) all land < 0.25, the mechanism is fundamentally unable to compete with dense bag-of-trigrams on substrate WordNet content at N=100.

**Stage-2 arc implications:**

1. **concept_encoder EARNS ONLY the synthetic-cluster CG claim.** No transfer to substrate content demonstrated. Update `hdlab/concept_encoder.py` module docstring VALIDATION SCOPE section: add "Substrate-content transfer: TESTED 2026-07-02, HF2. Substrate content is information-dense (WordNet); competitive-Hebbian sparse coding at any tested k does not exceed dense bag-word baseline."

2. **Stage 4 language ingest cannot use concept_encoder as-designed.** The Stage 3→4 progression assumes Stage 2/3 primitives transfer to real content. This HF2 says: they do not for information-dense corpora. Options:
   - (a) Reframe Stage 4 to REQUIRE information-sparse designer-cluster preprocessing (which is not what "language ingest" typically means; would be a substantial scope-narrowing).
   - (b) Substitute Stage 4 concept representation with substrate-native HRR-bind of atom + relation (Sweep F).
   - (c) Restrict Stage 2 primitive claim to explicitly designer-controlled cluster regimes (test-tube capability, not general).

3. **substrate-content evaluation methodology:** Any future test of a Stage 2/3 primitive on substrate content MUST include a dense-bag-of-features baseline (char_trigram or PPMI). Silent HP2/HP3-style "mechanism vs. baseline" gates catch this. File as verification-discipline reinforcement (already covered by `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` and `feedback_three_smoke_disciplines_...`).

4. **Cross-arc coherence with prior work.** The 2026-06-08 sparse-value-coding drill already stated this principle. Filed atomization suggestion: promote `META_information_density_vs_sparsity_regime_predicts_sparse_coding_transfer` to a chain-grade META atom in `data/substrate_index/meta/atoms.jsonl` (bumps discipline-catalog with the calibrated prediction rule).

**Which reframe is most productive:** (b) HRR-bind substrate-relations. It plays to the substrate's actual algebraic primitives (bind, unbind, cleanup memory), leverages the already-ingested WordNet relational structure, and gives Stage 4 a substrate-native path forward. Recommend queueing this as v3 architectural probe independent of v2 rescue outcome.

---

## 6. Recommended follow-up dispatch order

**Immediate (Director may spawn hdi_exp_dev on approval):**
1. **v2 k_sparsity sweep + WTA-off ablation cell** (Sweep A + B combined; ~45s smoke; addresses highest rescue P + diagnostic in one dispatch).

**Contingent on v2 HP1 hit (any k rescues):**
2. Full FULL v2 at N=500 atoms 3 seeds; commit rescue as v3 config.
3. Skunkworks landed-VET on rescue landing; atomize k-dependent claim as capability atom.

**Contingent on v2 HF1 (no k rescues):**
2b. **v3 architectural probe: HRR-bind substrate-relation concept representation** (Sweep F). Cell design: for each WordNet atom, construct concept_hd via `sum_i bind(hypernym_i_hd, HAS_HYPERNYM) + bind(synonym_i_hd, HAS_SYNONYM)` where atom HDs are seeded from atom_id string hash. Query: encode(synonym) via same atom_hd hash → cosine argmax on concept table. Test whether substrate's relational primitives beat 0.28 char_trigram baseline.
3b. If v3 also fails: substrate WordNet content is fundamentally not the right test-bench for either brain-analog or algebraic-relational Stage 2 primitives at this N=100 regime. Escalate to N=500 with better-curated atoms (require rich hypernym chains + multiple sense entries).

**Parallel with 1-3 (independent of outcome):**
- Companion 5x-drill outputs (math, neuro, physics, ML) should be synthesized into a cross-drill decision at USER cadence.
- Document THIS drill's substrate-KB prior-work overlap finding as evidence that concept-query BEFORE-dispatch discipline is under-followed even after being locked (Fix #28 lineage).

---

## 7. P-estimate summary + top-line verdict

| Rescue path | P(rescue > 0.28 max baseline) | Cost (smoke wall) | Decision-value |
|---|---:|---:|---|
| Sweep A: k_sparsity ∈ {0.05...0.50} | 0.45 (best at k=0.20) | ~30s | HIGH |
| Sweep B: WTA-off ablation | 0.45 | ~15s | HIGH (diagnostic) |
| Sweep A ∪ B composite | 0.50 (capped) | (combined cell ~45s) | HIGHEST |
| Sweep C: N_DIM scaling alone | 0.15 | ~60s | LOW |
| Sweep D: augment training text | 0.20 | ~90s | LOW |
| Sweep E: hypernym-cluster query | 0.60 for regime-drift claim; 0.10 for original claim | ~30s | LOW for the failing claim |
| Sweep F: HRR-bind substrate-relations | 0.50 (capped; architectural substitute, DIFFERENT claim) | ~120s | MEDIUM-HIGH strategically |

**Top-line verdict:** the highest-rescue-probability sweep dimension is **k_sparsity relaxation (Sweep A) combined with WTA-off ablation (Sweep B) in one v2 cell.** Composite calibrated P(exceeds char_trigram=0.28 baseline) = 0.50 (at cap). Both sweeps directly test the diagnosed root cause (asymmetric dense-vs-sparse cosine argmax discards ~98% of query char-trigram information).

**Concrete v2 config recommendation:**
- Cell anchor: `substrate_concept_encoder_substrate_content_v2_k_sparsity_sweep_2026-07-03`
- 5 k_sparsity conditions × 3 seeds + WTA-off ablation arm + 2 baseline arms = 24 units at smoke N=100 (~45s total).
- HP1 rescue floor: recall@5 ≥ 0.30 at some k (strict; char_trigram + 5% band-width).
- HP2 diagnostic: WTA-off ≥ 0.28 → sparsification is the whole failure mode.
- HF1 no-rescue: all k < 0.25 AND WTA-off < 0.25 → commit to Sweep F architectural substitute (HRR-bind substrate-relation encoder).

**Strategic framing regardless of v2 outcome:** the substrate-KB already contained the theory (sparse-value-coding-within-shards drill 2026-06-08) that predicted this HF. The failure is not "we didn't know"; it is "we didn't concept-query before dispatch despite the discipline being USER-locked 2026-06-27." This drill's most durable output may be the v3 architectural substitute proposal (HRR-bind substrate relations) rather than the k-sweep rescue itself.

---

**Deliverable path:** `d:/AI/hd-instrument/notes/research_5x_drill_1_empirical_mechanism_config_sweep_substrate_content_HF_2026-07-02.md`

**Substrate-KB queries executed:** 3 (mandatory pre-dispatch protocol satisfied).
**Prior-work overlap findings:** 3 relevant prior arcs; sparse-value-coding drill 2026-06-08 chunk090 is the LOAD-BEARING prior arc that predicted this HF6+ weeks before dispatch.
**Companion drills expected:** 4 (math, neuro, physics, ML) — this drill is 1/5 (empirical angle).

END drill 1/5.
