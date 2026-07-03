# Prereg: substrate_concept_encoder_v2_A_ppmi_svd_sparse (2026-07-03)

**Cell:** `experiments/exp_substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026-07-03.py`
**Anchor:** `substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026_07_03`
**Module:** `hdlab/ppmi_sparse_encoder.py` (new)

## Strategic context

Per ML/AI drill 5x-5/5 rec 2026-07-02 (aa2f575d): tests PPMI/SVD-then-threshold
sparse encoder as PARALLEL rescue path #2 vs v1 concept_encoder HF on the
substrate-content HF task. Runs alongside v2 P1 VWFA+late-combine cell
(abe8e2ba) as independent rescue architectures.

**Prior v1 baseline (2026-07-02, MEASURED@`data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json:aggregate`):**
- ARM_CONCEPT_ENCODER (competitive-Hebbian) recall@5 = 0.160
- ARM_CHAR_POSITIONAL_ONLY recall@5 = 0.210
- ARM_CHAR_TRIGRAM_UNSUP recall@5 = 0.280 (target to beat)
- Verdict: HARD_FAIL (mechanism no advantage over bag baseline).

## FRAMING (LOAD-BEARING per USER 2026-07-02)

- Substrate has NOT ingested general knowledge. This tests PPMI/SVD mechanism
  on substrate's KNOWN SYMBOLIC KNOWLEDGE (WordNet definitions+synonyms).
- HP earned here does NOT grant "substrate knows things" broadly. HP grants
  "PPMI/SVD mechanism works on substrate's known symbolic content".
- Under brain-best-in-class discipline: PPMI-derived sparse codes are LESS
  brain-analog than competitive-Hebbian, but empirical text-literature
  support exists (SPOWV Faruqui 2015, SPINE Subramanian 2018, Random
  Indexing Sahlgren).
- Zero external LLM. Substrate-native forward-only closed-form.

## Prior-work check (USER-locked concept-query rule)

`bash tools/substrate_query.sh "PPMI SVD sparse encoder co-occurrence pointwise mutual information forward closed-form"`
returned top hit `Mutual information` at cosine=0.39 (generic math concept).
Legacy Wave14 series 2026-05-24 (`exp_wave14_sparse_coding_ppmi_v1`,
`exp_wave14b_m2_ppmi`, `exp_wave14d_sparse_vs_ppmi`) used PPMI on
BYTE-BIGRAM co-occurrence for VSA DICTIONARY ATOM generation (bpc / bigram
prediction task). DIFFERENT REGIME from WordNet held-out synonym retrieval.
**Genuinely novel synthesis for this task-regime.**

## Task

Same as prior baseline cell (`exp_substrate_concept_encoder_substrate_content_v1`):
- Corpus: WordNet 3.0 lexicon partition (`data/substrate_index/concept/atoms.jsonl`)
- Filter: kind=lexicon; pos in {n,v,a,r}; len(desc)>=20; len(synonyms)>=3;
  lemma_freq_semcor>=1
- Sort: freq desc; take top N atoms deterministic
- Per atom: fit(training=[definition, syn0, syn1, "related to hypernym"], label=atom_idx)
- Held-out query: LAST synonym (never in training)
- Metric: recall@{1,5,10} = fraction with correct atom_idx in top-k

## Arms (5, mirror + extend v1 baseline)

1. **ARM_V2A_PPMI_SVD** (LOAD-BEARING): `PPMISparseEncoder(n_dim=2048,
   k_sparsity=0.02, min_term_freq=2, smoothing=0.75)` on char-trigrams.
   Prototype table = mean-bundle of PPMI-encoded training sentences per
   concept.
2. **ARM_V1_CONCEPT_ENCODER**: `ConceptEncoder(...)` competitive-Hebbian
   baseline; positive control for prior 0.160 measurement.
3. **ARM_CHAR_TRIGRAM_UNSUP_REFERENCE**: `CharTrigramEncoder` bag-word
   baseline; TARGET TO BEAT.
4. **ARM_RANDOM_INDEXING** (Sahlgren bonus): deterministic sparse ternary
   per-trigram vectors, sum-bundle for text.
5. **ARM_RANDOM_BASELINE**: random bipolar per-concept prototypes; random
   HD per query. Chance-floor control.

## Compute architecture

- Class: **(b) sequential-CPU with justification**
- Justification: PPMI SVD is one-time per-seed operation over V x C matrix
  (V ~= 500 unique trigrams at N=100 atoms, C=100); numpy SVD dominates but
  wall <10s per seed. Bundle-encoding + cosine argmax over N=100 prototypes
  is trivially fast. No GPU batching benefit at smoke scale.
- Full-N wall estimate: ~5min per seed (dominated by SVD at V~2000, C=500);
  smoke wall ~30s-2min per seed.
- **Storage strategy:** `sharded_per_atom_prototype_hds` (per-concept
  prototype HDs, not bundled into a single vector; composition depth L=1,
  encoder eval not chain).

## HP / HF bands

**HARD_PASS** (all of HP1-HP5 required):
- **HP1 rescue over v1:** ARM_V2A_PPMI_SVD r@5 > ARM_V1_CONCEPT_ENCODER r@5 + 0.10
  (meaningful lift over failed competitive-Hebbian)
- **HP2 beats bag:** ARM_V2A_PPMI_SVD r@5 >= ARM_CHAR_TRIGRAM_UNSUP_REFERENCE + 0.05
  (v2-A architecture beats trivial bag baseline)
- **HP3 v1 recovery:** ARM_V1_CONCEPT_ENCODER r@5 within +/-0.03 of prior 0.16
  (positive control; reproduces prior HF measurement AT TEST REGIME)
- **HP4 chance:** ARM_RANDOM_BASELINE r@5 <= 0.10 (chance floor sanity;
  theoretical chance = 5/100 = 0.05)
- **HP5 arms-differ:** all 5 arm prototype tables hash-distinct

**HARD_FAIL:**
- **HF1 no rescue:** ARM_V2A_PPMI_SVD < ARM_V1_CONCEPT_ENCODER
  (PPMI/SVD WORSE than failed baseline)
- **HF2 no bag beat:** ARM_V2A_PPMI_SVD < ARM_CHAR_TRIGRAM_UNSUP_REFERENCE
  (v2-A still loses to bag; MAJOR REFRAME)
- **HF_STRUCTURAL:** arms_differ_verified=False on any seed

**MIDDLE_BAND:** v2-A lifts v1 (HP1 pass) but ties/marginally below bag (HP2 miss);
OR passes HP1+HP2 but HP3 positive control fails (v1 doesn't reproduce).

## HP_SCOPE

- ARM_V2A_PPMI_SVD: [HP1, HP2, HP5]
- ARM_V1_CONCEPT_ENCODER: [HP3, HP5]
- ARM_CHAR_TRIGRAM_UNSUP_REFERENCE: [HP5]
- ARM_RANDOM_INDEXING: [HP5] (bonus arm; no HP gate applies; reported
  descriptively for extension analysis)
- ARM_RANDOM_BASELINE: [HP4, HP5]

## SCHEMA-VET checklist (§13-§16 disciplines)

- `arms_differ_verified: True` at smoke (5-way SHA256 hash-test)
- `final_metrics_atomicity: "tmp_replace"` (os.replace atomic)
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- `crlb_n/a: "supervised retrieval; chance floor = k/N = 0.05 at k=5 N=100"`
- `discriminator_reachability: True` (HP2 gap 0.05 above ct=0.28 -> target
  r5 >= 0.33 is on achievable side; PPMI on WordNet definitions has documented
  literature success rates > 0.30 on lexical similarity tasks)
- `baseline_in_band: True` expected (ct5=0.28 and v1_r5~=0.16 both within
  [0.05, 0.80])
- `cell_chunked: False` (single-cell 3-seed; SVD is fast; no runner-zombie
  risk documented for smoke wall <5min)
- `start_marker_written: True` (`_start_marker.json` at main() entry)
- `crash_diagnostic_present: True` (Exception -> `CELL_CRASHED` metrics.json
  + traceback)
- `heartbeat_present: True` (`CellHeartbeat` every 30s / every unit)
- `progress_logging: "print_flush_true"` (all print() calls use flush=True)
- `cardinality_ok: bool` (verdict logic checks landed_n_units == expected_n_units;
  expected = 5 arms x 3 seeds = 15 for smoke, 5 arms x 3 seeds = 15 for full)
- `calibration_check: "default_ok_for_this_regime"` (PPMI+SVD defaults
  Levy/Goldberg 2015; smoothing alpha=0.75 standard; min_term_freq=2
  standard for small corpora)
- All numbers tagged (MEASURED@prior baseline / HYPOTHESIZED@drill rec /
  THEORETICAL@chance floor / CITED@lit)

## Section 15 test-design gates

- **A) Effective-vs-nominal parameter audit:** No sweep axis in this cell
  (fixed hyperparameters); N/A.
- **B) Bracket includes discriminating band:** No sweep; single-point per
  regime. HP1/HP2 gaps placed in discriminating range around prior baselines.
- **C) Signal-shape compatibility audit:** ARM_V2A composes PPMI-encoded
  training sentences via mean-bundle -> prototype (float dense) + cosine
  argmax. SHAPE_MATCH at all edges (all float32 [n_dim]).
- **D) Positive-control reproduction at test regime:** HP3 is EXACTLY this
  gate: ARM_V1_CONCEPT_ENCODER must reproduce prior 0.16 r@5 within +/-0.03
  at SAME regime (N=100, seeds=[11,17,23], n_dim=2048, corpus config).
- **E) Functional-requirement decomposition:** Functional requirement =
  "encode text (definition/synonym) into HD that yields correct concept via
  cosine argmax". PPMI captures term-concept association via co-occurrence
  statistics (chain-grade primitive in NLP literature; novel for HD
  substrate). Random Indexing captures accumulated co-occurrence via
  hashed sparse vectors (Sahlgren classic). Both mapped.

## Flow

1. Author `hdlab/ppmi_sparse_encoder.py` + selftest PASS **[DONE]**
2. Author cell + prereg **[DONE]**
3. Local smoke on local_cpu (N=100 atoms same as prior)
4. Report smoke results + HP verdict
5. **HOLD before FULL dispatch** — Director + USER weigh outcome

## Novelty / prior-P

Novel synthesis (PPMI/SVD sparse encoder for HRR substrate on WordNet
retrieval). Lit-scan calibration penalty applied per USER-locked rule:
P_CG deflated to 0.30 (upper end of "cap novel-synthesis P at 0.50" with
downgrade for text-encoding regime where prior VSA-PPMI attempts on
different regime went MB/HF).
