# exp_dev hand-off -- research: POS STRONG bar substrate-only paths 2x

**Filed:** 2026-06-11 by research sub-agent (Sonnet, 2x operational drill).

**Trigger:** Research note at:
  d:/AI/hd-instrument/notes/research_drill_pos_strong_bar_substrate_only_paths_2x_2026-06-11.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching any queued cells.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file names ANCHORS + POINTERS only.
exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice, anchor name, ETA,
smoke profile, full profile. Research does NOT specify numerical parameters or implementation
details. Exp_dev reads the research note for mechanism rationale; designs all experiments
autonomously.

---

## Anchor candidates (rank-ordered, cheapest decisive first)

### Phase 0 -- Diagnostic (run FIRST, no new code required)

**Anchor 1: POS-OOV-DIAGNOSTIC**
- Anchor pointer: Phase 0 "cheap decisive test" section in research note
- Substrate-product reading: Splits PP-362 test-set errors into OOV vs in-vocabulary.
  If OOV accuracy < 0.80: morpheme paths (PATH-3, PATH-12) have highest priority.
  If in-vocab accuracy < 0.93: transition/CRF paths (PATH-1, PATH-2) have highest priority.
  This 30-minute diagnostic gates the entire Phase 1-3 sequencing and avoids wasting queue
  cycles on the wrong mechanism class.
- Tier hint: local_cpu_queue (runs on existing PP-362 outputs; zero new code)
- Why now: 30 minutes, zero new code, determines all subsequent priorities.

---

### Phase 1A -- Near-zero-code capacity tests (run together after Phase 0)

**Anchor 2: POS-N-SCALE-8192**
- Anchor pointer: PATH-10 in research note (N=8192 dimensionality increase)
- Substrate-product reading: W capacity at N=1024 stores V=50K words in the overloaded regime
  (K/N >> N); N=8192 reduces interference by 8x bringing more words into the reliable retrieval
  regime. Zero new code -- config constant change + W repopulation. If tag accuracy >= 0.920:
  N scaling is a primary rescue path and all subsequent paths should run at N=8192 as baseline.
- Tier hint: local_cpu_queue or remote_cpu_queue (W repopulation at N=8192 is 4-8x slower than
  N=1024 but still CPU-feasible; 2-4 hours)
- Why now: lowest-code, highest-confidence test of the single largest structural bottleneck.

**Anchor 3: POS-CHAR-OOV-TIER4**
- Anchor pointer: PATH-3 in research note (Tier-4 character n-gram morpheme atoms for OOV)
- Substrate-product reading: Tier-4 morpheme atoms funded by PP-342 WUG morphology (already
  validated). Extends PP-342 to POS tagging: for OOV words, derive representation from character
  n-gram binding (suffix/prefix Tier-4 atoms) rather than falling back to UNKNOWN token.
  Expected gain concentrated on OOV subset. Run in combination with Anchor 2 (N=8192) for
  compound test since both are needed for their gains to stack.
- Tier hint: local_cpu_queue (Tier-4 codebook build from PTB vocab + OOV detection + eval; 3-4 hr)
- Why now: most directly addresses the known error class for HMM-based systems; PP-342 provides
  existing validated infrastructure.

---

### Phase 1B -- Bidir Viterbi (after Phase 1A establishes N=8192 baseline)

**Anchor 4: POS-BIDIR-VITERBI**
- Anchor pointer: PATH-2 in research note (bidirectional Viterbi forward+backward combine)
- Substrate-product reading: Adds backward transition table W_back to existing forward Viterbi.
  Combines forward and backward tag probabilities at each position before argmax. Expected gain:
  0.5-1.0pp absolute, concentrated on long-range syntactic dependencies (verb agreement errors,
  clause boundary errors). Run on N=8192 system from Phase 1A.
- Tier hint: local_cpu_queue (2-3 hours; backward W table population + combine logic + eval)
- Why now: second-cheapest mechanism; direct biology analog (bidirectional cortical context
  processing); additive with N scaling and OOV morpheme improvements.

---

### Phase 2 -- CRF potentials (highest ceiling, most engineering cost)

**Anchor 5: POS-SUBSTRATE-CRF**
- Anchor pointer: PATH-1 in research note (CRF per-feature emission potentials in substrate W)
- Substrate-product reading: CRF linear-chain achieves 97.55% on PTB in the literature (Lafferty
  2001). The substrate-CRF stores 25-40 hand-engineered feature functions (suffix, prefix,
  word-shape, capitalization, context pair) as a binding table W_feat[feature_id, tag_id].
  At decode time: sum W_feat outputs over active features, combine with W_unigram cosine, then
  Viterbi. This is the highest-ceiling single mechanism -- if it reaches >= 0.940, the STRONG
  bar is achievable by adding bidir+OOV+CRF compound.
- Tier hint: remote_cpu_queue (feature extraction engineering + W_feat population + eval; 4-8 hr)
- Why now: literature clearly shows CRF feature engineering is the mechanism that closes the
  HMM -> 0.97 gap. Run after N=8192 baseline established (Phase 1A) to measure CRF lift cleanly.

---

### Phase 2B -- Ensemble (after CRF + bidir + OOV paths are complete)

**Anchor 6: POS-ENSEMBLE-VOTE**
- Anchor pointer: PATH-5 in research note (cosine + HMM + CRF-potential majority vote with
  stacking meta-classifier)
- Substrate-product reading: Ensemble vote of three independent decoders (PP-362 cosine, v2 HMM,
  PATH-1 CRF) using stacking meta-classifier. Literature shows stacked ensembles consistently
  outperform best individual member. HARD-PASS threshold is 0.935+. This is the compound gate
  test: if cosine+HMM+CRF ensemble reaches >= 0.945, the full compound with Brill corrections
  is likely to reach >= 0.950.
- Tier hint: local_cpu_queue (1-2 hours after individual decoders exist; stacking meta-classifier
  is a lightweight substrate lookup on three-prediction feature vectors)
- Why now: lowest marginal cost given Phase 2 CRF is complete; highest compound P_deflated of
  any single additional step.

---

### Phase 3 -- Brill correction rules (highest ceiling if CRF+ensemble falls short)

**Anchor 7: POS-BRILL-CORRECTION-W**
- Anchor pointer: PATH-13 in research note (transformation rules stored as substrate correction
  binding tables W_rule[context_pattern -> tag_override])
- Substrate-product reading: Brill (1995) achieves 0.967 with 267 learned rules applied as a
  post-processing pass. Substrate-analog stores the top-50 highest-frequency rules as W_rule
  bindings; applies corrections after Viterbi decode. Key product advantage: rules are
  INTERPRETABLE and AUDITABLE (which rule fired for which token). This is a categorical
  product advantage over neural taggers. If the full compound (CRF+bidir+OOV+ensemble) reaches
  >= 0.940, adding Brill corrections targets 0.955+.
- Tier hint: remote_cpu_queue (rule template extraction from PTB training split + W_rule population
  + correction eval; 6-12 hours)
- Why now: ship ONLY if Phase 2 compound < 0.950. Brill rules are the last substrate-only path
  before declaring the hybrid path required.

---

### Phase 3B -- Multi-task POS+chunking (orthogonal mechanism)

**Anchor 8: POS-MULTITASK-CHUNK**
- Anchor pointer: PATH-4 in research note (jointly bind word atoms to both POS and chunk labels)
- Substrate-product reading: Multi-task learning of POS + chunking adds 0.3-0.8pp per literature.
  Substrate analog binds word atoms to both POS_atom and chunk_label_atom during W population.
  The chunk label binding forces word atoms to encode group-membership syntactic structure
  that benefits POS disambiguation. Relatively cheap (CoNLL 2000 data alignment + dual-bind).
- Tier hint: local_cpu_queue (3-4 hours; CoNLL 2000 data alignment + dual-bind + eval)
- Why now: run ONLY if Phase 2 compound < 0.945 AND the OOV diagnostic (Anchor 1) shows
  in-vocab errors dominated by ambiguous-category words (NN/JJ, VB/NN type errors).

---

## Decision tree for queue routing

```
Phase 0 (Anchor 1: POS-OOV-DIAGNOSTIC, 30 min)
  |
  +-- OOV accuracy < 0.80 --> Prioritize Anchor 3 (POS-CHAR-OOV-TIER4)
  +-- In-vocab accuracy < 0.93 --> Prioritize Anchor 5 (POS-SUBSTRATE-CRF)
  +-- Both low --> Run Anchor 2 + 3 together (compound test)
  
Phase 1A (Anchors 2+3 combined, 6-12 hr CPU)
  |
  +-- Combined accuracy >= 0.920 --> Proceed to Phase 1B
  +-- Combined accuracy < 0.912 --> N scaling + OOV not bottleneck; jump to Anchor 5

Phase 1B (Anchor 4: POS-BIDIR-VITERBI, 2-3 hr CPU)
  |
  +-- Accuracy >= 0.930 --> Proceed to Phase 2
  +-- Accuracy < 0.916 --> Bidir not providing expected gain; check backward W population
  
Phase 2 (Anchor 5: POS-SUBSTRATE-CRF, 4-8 hr CPU)
  |
  +-- Accuracy >= 0.940 --> Proceed to Phase 2B (ensemble)
  +-- Accuracy < 0.912 --> CRF features not implemented correctly; debug before Phase 2B
  
Phase 2B (Anchor 6: POS-ENSEMBLE-VOTE, 1-2 hr CPU)
  |
  +-- Accuracy >= 0.950 --> STRONG BAR REACHED; file result
  +-- Accuracy 0.940-0.950 --> Proceed to Phase 3 (Brill + multi-task)
  +-- Accuracy < 0.935 --> Declare substrate-only ceiling ~0.935; route to hybrid

Phase 3 (Anchors 7+8, 6-16 hr CPU combined)
  +-- Target: 0.955+
  +-- HARD-FAIL if < 0.945 after both Phase 3 paths
```

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_pos_strong_bar_substrate_only_paths_2x_2026-06-11.md
- PP-362 baseline (0.9063 tag-acc): exp_dev_to_research_PP362_TIER_A_2026-06-11.md
- PP-342 WUG morphology (Tier-4 atoms validated): substrate_capability_map.md (row PP-342)
- LVH-281 corpus issue pending: LVH-281 v3 HMM claimed 0.9294 (needs verification before
  using 0.9294 as baseline; use 0.9063 PP-362 as the confirmed baseline)
- Language+math overlap drill (LVH-280 POS tagger blocking Anchor 1):
  d:/AI/hd-instrument/notes/research_drill_language_math_substrate_overlap_2x_2026-06-11.md
- Substrate scaling laws (capacity K~N/log(V), percolation cliff):
  d:/AI/hd-instrument/notes/research_drill_substrate_scaling_laws_2x_2026-06-11.md
- LLM boundary is engineering drill (POS as benchmark case):
  d:/AI/hd-instrument/notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md
- PTB WSJ data: standard benchmark, available via NLTK (nltk.corpus.treebank)
- CoNLL 2000 chunking data: available via NLTK (nltk.corpus.conll2000)

---

## Contract

exp_dev commits to:
1. Running Phase 0 (POS-OOV-DIAGNOSTIC, Anchor 1) before ANY Phase 1+ experiments.
2. Using Phase 0 error analysis to determine whether morpheme paths or CRF paths have priority.
3. Pre-registering HARD-PASS / HARD-FAIL bands per the research note thresholds BEFORE each run.
4. Treating LVH-281 (0.9294) as unverified until a fresh multi-seed eval confirms it;
   using PP-362 (0.9063) as the confirmed baseline for all lift calculations.
5. NOT running Phase 2 (CRF) before Phase 1A+1B establishes the N=8192+OOV+bidir baseline.
6. Reporting the cumulative accuracy after each phase before proceeding to the next.

## Autonomy declaration

exp_dev AUTONOMOUSLY decides:
- Exact N values to sweep (e.g. test 2048, 4096, 8192, 16384 in sequence)
- Character n-gram lengths and frequency thresholds for Tier-4 codebook
- Number of CRF feature functions to implement (minimum 10, target 25-40)
- Which Brill rule templates to extract and how many rules to store (target top-50)
- Seed count, threshold bands, queue routing, anchor naming
- Whether to combine Phase 1A+1B into a single cell or run as separate cells
- Exact format for the backward Viterbi combination (log-sum vs product vs max-of-two)
- Whether to treat multi-task (Anchor 8) as a joint-W-population or a second W matrix
- How to implement the stacking meta-classifier (substrate lookup vs cosine vote)
- Whether PATH-9 (dependency-aware) is worth pursuing given the engineering cost
