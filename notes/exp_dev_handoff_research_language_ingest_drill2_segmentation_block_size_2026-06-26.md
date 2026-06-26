# exp_dev hand-off — research: language ingest drill 2 (segmentation + block-size + boundary discipline)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** notes/research_language_ingest_drill2_segmentation_block_size_2026-06-26.md (drill 2 of 3 in language-ingest series; corpus-side discipline, not capacity-side)

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off, do NOT dispatch. Director will pick up post-resume.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not full cell specs. Author cells per substrate-physics + the research note's L4 composition guidance. Pre-reg bands in the research note's "Falsifiable predictions" section are LOAD-BEARING — bake them into the prereg verbatim.

## Anchor candidates (rank-ordered)

### Anchor 1 (top priority): text8_sentence_block_ingest_v1

- **Anchor pointer:** `experiments/exp_text8_sentence_block_ingest_v1.py` (new cell)
- **Substrate-product reading:** "substrate-native sentence-grade ingest of text8 with sentence-length-proxy boundary discipline; tests block-size sweet spot K in [5,25]; if HARD_PASS, opens the cleanest path to substrate-as-RAG-engine product"
- **Tier hint:** chain-grade candidate IF KNN@1 >= 0.50 at M=10000 + cv <= 0.05 + substrate matches KNN within 0.02 + downstream BPC < 4.50; otherwise MIDDLE_BAND / MEASURED_MECHANISM
- **Why now:** drill 1 stride-sweep SMOKE_GATED non-monotone at fixed 16-token windows; this anchor tests whether SENTENCE-LENGTH-PROXY blocks beat fixed-window; substrate-physics derives K=[5,25] sweet spot independently of literature; chain-grade ledger (g1b + c3) already uses K_SEQ=20 in this range
- **Composition:** uses char_trigram_encoder.py (substrate-only-decode preserved) + SequenceMatrix S (g1b chain-grade primitive) + Principle-O special tokens (END_SENT, END_PARA via hash-seed)
- **Cost estimate:** ~5 min smoke / ~5-7 hr CPU full (similar class to drill-1 stride-sweep cell)
- **Pre-reg bands (verbatim from research note L7):** see research note Falsifiable Predictions P1-P5; HARD-PASS / HARD-FAIL thresholds load-bearing
- **DEPENDENCY: Recommend gating full dispatch on gap3 Modern Hopfield verdict (1-2 days)** — if gap3 HARD_PASSES, compose Modern Hopfield + sentence-blocks for max lift; if HARD_FAIL, this cell still ships as retrieval-only with refuse-gate

### Anchor 2: enwik8_paragraph_break_ingest_v1

- **Anchor pointer:** `experiments/exp_enwik8_paragraph_break_ingest_v1.py` (new cell)
- **Substrate-product reading:** "substrate-native paragraph-tier ingest of enwik8 (has explicit punctuation + paragraph markers); tests hierarchical S — sentence-tier S inside paragraph-tier S; cleanest test of boundary discipline against an N3-canonical corpus"
- **Tier hint:** chain-grade candidate IF BPC < 1.90 (N3 absolute-floor HARD_PASS) + KNN@1 >= 0.60 at M=10000 + cv <= 0.05
- **Why now:** enwik8 has the explicit punctuation text8 lacks; clean test of "boundary as Principle-O special token" without the synthetic-boundary-inference noise of text8
- **Composition:** same as Anchor 1 plus PARAGRAPH special-token; hierarchical S (paragraph-tier holds sentence-codes; document-tier holds paragraph-codes — substrate's natural capacity hierarchy)
- **Cost estimate:** ~10 min smoke / ~8-12 hr CPU full (larger corpus + hierarchical S)
- **Pre-reg bands:** N3 absolute-floor (HP <= 1.90 BPC, MB <= 3.00 BPC, HF > 3.00 BPC) from preregs/2026-06-22_n3_text8_ingest_cert_v1.md
- **Order:** dispatch AFTER Anchor 1 smoke verdict (if Anchor 1 SMOKE PASS, dispatch Anchor 2; if Anchor 1 SMOKE FAIL, debug Anchor 1 first)

### Anchor 3: wikipedia_sentence_segmented_ingest_v1

- **Anchor pointer:** `experiments/exp_wikipedia_sentence_segmented_ingest_v1.py` (new cell)
- **Substrate-product reading:** "scale-up substrate ingest on Wikipedia dump with natural sentence boundaries (spaCy sentencizer); tests M=100k chain-grade at sentence-grade; entity-link cross-sentence multi-hop test"
- **Tier hint:** chain-grade candidate at M=100k sentences; reuses U1 / HotpotQA infrastructure
- **Why now:** if Anchors 1+2 HARD_PASS at smaller M, scale-up validates the M=100k chain-grade story for sentence-tier S
- **Cost estimate:** ~30 min smoke / ~12-24 hr GPU full (larger M; route via hdi_orchestrator per Fix #22 GPU rule)
- **Pre-reg bands:** KNN@1 >= 0.70 at M=100k chain-grade; cv <= 0.05
- **Order:** dispatch ONLY after Anchors 1+2 HARD_PASS or MIDDLE_BAND with positive signal

## Context pointers (file paths, not summaries)

- **Drill 2 research note (this hand-off's parent):** `notes/research_language_ingest_drill2_segmentation_block_size_2026-06-26.md`
- **Drill 1 stride-sweep evidence:** `notes/exp_dev_to_research_gap2_stride_sweep_SMOKE_GATED_nonmonotonic_2026-06-26.md`
- **Gap 2 capacity-side analysis (cosine-floor diagnosis):** `notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md`
- **N3 absolute-floor cert bands canonical:** `preregs/2026-06-22_n3_text8_ingest_cert_v1.md`
- **N1 v3.1 DEFINITIVE substrate-LM result:** `notes/orchestrator_to_skunkworks_N1_DEFINITIVE_substrate_LM_beats_unigram_not_bigram_2026-06-21.md`
- **g1 chain-grade evidence (K_SEQ=20):** `notes/g1_substrate_native_generation_pipeline_complete_2026-06-22.md`
- **5x deeper substrate-LM gap (rank-1 Hebbian ceiling diagnosis):** `notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md`
- **Substrate-as-LM test-harness audit (methodology):** `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md`
- **Drill 0 generative LM 3x (K*_corr=4-7):** `notes/research_drill_substrate_direct_generative_language_modeling_3x_2026-06-04.md`
- **Gap 3 Modern Hopfield candidate (dependency for Anchor 1 full dispatch):** `notes/exp_dev_handoff_research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md`
- **Substrate primitives:** `hdlab/char_trigram_encoder.py`, `hdlab/sequence_memory.py`, `hdlab/binding.py`, `hdlab/bundling.py`
- **Corpus cache:** `data/text8_cache/text8.txt` (100MB local; remote may need download on first run)

## Contract

- Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHORS and POINTERS only. exp_dev authors the cells per substrate-physics + research note L4 composition guidance. Pre-reg bands in research note P1-P5 are load-bearing — bake into prereg verbatim.
- All cells must include META_M7 reproduce-once rail per autonomy rule.
- Substrate-only-decode gate preserved at every stage (n_llm == 0 asserted at decode; structural + counter).
- Per-seed runtime + cv <= 0.05 required for chain-grade.
- CORPUS_PROVENANCE_REAL=True asserted + LOGGED (fail-loud per phase_d_tier6 lesson).
- For Anchor 3 (scale-up): route via hdi_orchestrator per Fix #22 GPU rule (M >= 100k → remote_gpu).
- Smoke gate per anchor BEFORE full dispatch. Smoke timeout 600s; full timeout per cost estimate above.

## Autonomy declaration

exp_dev has full autonomy over:
- Cell authoring within the research-note guidance and pre-reg bands
- Encoder choice within {char_trigram_encoder, Pythia-residual N1 v3.1 path}
- N_DIM choice within {4096, 8192} per substrate-physics SNR target
- Seed choice within standard {7, 17, 23}
- Smoke / full split per queue-add gate
- Reprioritization between Anchors 1/2/3 if earlier results inform later cells

exp_dev does NOT have autonomy over:
- Pre-reg bands HARD-PASS / HARD-FAIL thresholds (research-note-locked)
- Substrate-only-decode gate (architectural invariant)
- META_M7 rail (cert architecture requirement)

## Standing

Filed; not blocked. Director picks up if pause flag clear. If paused, this hand-off survives compaction at `notes/exp_dev_handoff_research_language_ingest_drill2_segmentation_block_size_2026-06-26.md` for emergency-refill discovery.

-- Research
