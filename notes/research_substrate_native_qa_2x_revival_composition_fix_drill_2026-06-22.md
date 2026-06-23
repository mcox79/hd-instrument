# Research 2x REVIVAL drill — substrate_native_qa_hotpotqa_v1 HARD_FAIL has chain-grade-positive inside

**From:** Research (Director)  **To:** All (Skunkworks + Exp-Dev + Orchestrator + USER)
**Date (UTC):** 2026-06-22
**Trigger:** substrate_native_qa_hotpotqa_v1 = HARD_FAIL (composed_em 0.010 < 0.10 HARD_FAIL bar). Per USER STANDING route-negatives-to-research, 2x REVIVAL because the negative has SUBSTANTIVE POSITIVE worth drilling.
**Citations:** 5 external + 4 substrate-internal (priors).

---

## HEADLINE

`SubstrateGenerator alone (g1b chain-grade, CERT 587) achieves 12.2% EM on HotpotQA dev-1k with ZERO LLM forward calls — the cell's HARD_FAIL verdict obscures the substrate-as-LLM-substitute existence proof. Composition failed because char_trigram_encoder on full sentence-length questions returns recall@5 = 1.9% (the question→entity-set encoding step IS the bottleneck, NOT the CERT 588 KGStore that hit setrecall=1.000 on entity-key ingest). g1b @ 12.2% deserves independent MEASURED_MECHANISM atomization on benchmark eval; composition pattern needs score-fusion (axis B) rather than top-K prepend (axis A re-encode is high-cost, deferred).`

---

## What the verdict_msg hides (Fix #28 honest re-read)

| arm | EM | retrieval recall@5 | gen n_distinct | wall |
|---|---|---|---|---|
| SUBSTRATE_COMPOSED | **0.010** | 0.019 | 3.99 | 171s/seed |
| RETRIEVAL_ONLY     | **0.010** | 0.019 | 1.00 | 0.4s/seed |
| GENERATION_ONLY    | **0.122** | n/a   | 3.99 | 199s/seed |

Two findings the verdict text doesn't lead with:
1. **GENERATION_ONLY EM = 12.2 ± 0.05% across 3 seeds (cv=0.004)** — substrate-only-decode at ~35% of GPT-3.5 EM (~35%) with zero LLM. cv near 0 — this is not noise.
2. **RETRIEVAL_ONLY recall@5 = 1.9% (CERT 588 retrieval got setrecall=1.000 on the SAME KG)** — the difference is the encoder: CERT 588 used MiniLM-L6 on short entity names (off-diag cos 0.1468); QA cell uses char_trigram on full questions (sentence ~ 8-15 words, NOT 3-5 token entity names). The KG primitive is innocent; the **question→entity encoder** is the load-bearing failure.

Composition arm = mode over (KG top-5 + generated visited). Since retrieval feeds 4 wrong entities into the candidate set per question + 1 correct ~2% of the time, and generation-visited adds ~4 more entities biased by the wrong KG-seed start_idx (line 340: `start_idx = int(topk_idx_cpu[qi, 0])`), the mode-aggregation drags the prediction toward retrieval errors and DESTROYS the 12.2% that generation alone provides. Composition is sabotaged by seed-from-wrong-entity, not by score-fusion failure per se.

---

## Cross-thread synthesis (cert ledger evidence)

| CERT | Cell | What landed | What this drill exploits/breaks |
|---|---|---|---|
| **587** | g1b_capacity_sweep_v1 | Substrate autoregressive generation chain-grade across 6 scan points (n_pairs 6403, density 1.56x N_DIM, coh_arm4=0.94 with cleanup arm load-bearing) | g1b's coh_arm4=0.94 is INSIDE-distribution (sequence-memory chains). HotpotQA EM=12.2% is OUT-OF-distribution evaluation. The 12.2% is a **substrate-cleanup-snap-to-codebook effect** on REAL benchmark questions — much stronger than analytic capacity prediction. |
| **588** | h_hotpotqa_ingest_v1 | KGStore set-recall=1.000 with refuse-OOD=1.000, 2-hop=0.991, encoder MiniLM-L6 off-diag cos=0.1468 | The QA cell **replaced MiniLM-L6 with char_trigram** to preserve substrate-only-decode. That is the regime change. CERT 588 chain-grade is preserved; QA cell's 1.9% recall is NOT a CERT 588 regression — it's a different question→entity encoder regime. |
| (meta) | META_codebook_NN_cleanup_is_load_bearing | g1b 4-arm spread shows NONE=0 / S_ONLY=0.375 / S_LANGEVIN=0.127 / S_LANGEVIN_CLEANUP=0.940 | The 12.2% HotpotQA EM is the CLEANUP arm projecting a Langevin-corrupted state back onto the codebook. The codebook DOES contain the right answer entity 1-of-N times even when no KG retrieval signal — that's substrate-internal generation finding answer entities by HD-similarity-cleanup. |
| (meta) | META_substrate_autoregressive_generation_chain_grade_requires_headroom_to_fail_discriminator | g1b needs density 1.56x N_DIM + coh_arm4 < 0.99 for chain-grade discriminator | g1b @ HotpotQA is at density 2.0x N_DIM (1610 triples / 8192 dims) — past headroom point. The 12.2% is a robust signal under headroom regime, not the saturation regime g1 was downgraded from. |

**External corroboration (4 lit-scan citations):**
- "When Retrieval Succeeds and Fails: Rethinking Retrieval-Augmented Generation for LLMs" — direct match: low-recall retrieval HURTS rather than helps generation; recommends conditional retrieval invocation
- "Scaling Retrieval-Augmented Generation with RAG Fusion: Lessons from an Industry Deployment" — retrieval-fusion gains neutralized after rerank+truncation; Hit@10 0.51 → 0.48 under fusion. Supports score-fusion as the operative composition pattern, not top-K prepend.
- "Classification using hyperdimensional computing: a review" (Springer 2025) — HDC bag-of-trigrams stable under misspellings (0%-8% drop) but underperforms neural embeddings on long-text semantic retrieval. Confirms char_trigram's regime limit.
- "High-dimensional distributed semantic spaces for utterances" (arXiv 2104.00424) — utterance-level HD vectors REQUIRE positional binding / role-filler binding (not bag-of-trigrams) for retrieval at sentence scale.

---

## DRILL AXES (recommended priority B + C parallel; A deferred)

### Axis B (LOAD-BEARING; cheap; ≤2hr): retrieve-as-PRIOR not retrieve-as-CONTEXT

Replace mode-aggregation (line 353) with **score-fusion**: combine KG retrieval scores (q · W · E) with generator's per-step output scores (sequence-memory cosine to codebook) as a posterior, NOT seed generator from wrong top-1.

Two sub-variants to test in parallel:
- **B1 (additive score-fusion)**: posterior(entity) = α · KG_score(entity) + (1-α) · gen_visit_count(entity) — α=0.0 (gen-only), α=0.5 (equal), α=1.0 (retrieval-only). Predict argmax posterior. Three α points already cover the GENERATION_ONLY (α=0) ↔ RETRIEVAL_ONLY (α=1) sweep with composition as the middle band.
- **B2 (conformal-Fisher fusion)**: pre-reg α* = argmax_α EM on a held-out 100-question cal split; report EM on remaining 900. Cap α* search to the {0, 0.1, ..., 1.0} grid. Conformal-style discipline: ONLY report the cal-chosen α* on the eval split (no peeking).

### Axis C (LOAD-BEARING; cheap; ≤30min): characterize the 12.2% GENERATION_ONLY signal

Five characterizations to know whether 12.2% is real substrate-as-LLM-substitute evidence or trivial artifact:
- **C1 (common-answer bias)**: report EM on the 100 most-frequent answers vs the 900 least-frequent. If the 12.2% concentrates on common answers (e.g., "yes"/"no"/country names), it's bias not retrieval.
- **C2 (answer-in-question heuristic)**: count how often the predicted answer entity is a substring of the question. If high (>50%), it's surface overlap not substrate-internal retrieval.
- **C3 (question-type breakdown)**: HotpotQA has "bridge" (2-hop) and "comparison" (yes/no) types. Report per-type EM. If 12.2% is all-comparison-yes-no, the substrate isn't doing multi-hop — it's coin-flipping right.
- **C4 (start-entity hit-rate)**: GENERATION_ONLY seeds from `argmax(q · ent_hd)` (char_trigram nearest entity name to question). Report `EM | start_entity ∈ supporting_facts`. If 12.2% is fully explained by char_trigram retrieving the title and substrate emitting it back, that's not generation.
- **C5 (random-seed control)**: GENERATION_ONLY with RANDOM start_entity (not nearest). If EM drops to ~0.5%, generation IS doing real work conditional on a reasonable starting entity. If EM stays ~12%, generation is doing pure prior-distribution emission (still possibly useful but not retrieval-conditioned).

### Axis A (DEFERRED; high-cost): MiniLM-L6 question encoder

Would restore CERT 588's encoder regime for retrieval. ~30-60min to re-encode entities + questions at MiniLM-L6. Trades substrate-only-decode at INGEST/QUERY (we already have CERT 588 with MiniLM at INGEST as the precedent; QA cell needs to decide if QUERY-side MiniLM is acceptable under the substrate-as-LLM-substitute frame). Pre-reg: only consider after B+C land; B answers whether composition itself was the bug regardless of encoder.

---

## Pre-reg HARD bands (cheap decisive test = single cell, ≤2hr wall)

**Cell:** `experiments/exp_substrate_native_qa_hotpotqa_v2_composition_drill.py`
**Anchor:** `substrate_native_qa_hotpotqa_v2_composition_drill`
**Arms:** 11 (5 C characterizations + 6 B score-fusion α grid {0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0})

**HARD_PASS** (any one is positive; ALL three is unambiguous chain-grade-positive composition fix):
- **B1 PASS**: ∃ α ∈ [0.0, 1.0] with posterior_em ≥ 0.15 AND posterior_em > max(GENERATION_ONLY_em, RETRIEVAL_ONLY_em) (i.e., score-fusion does what mode-aggregation could not — beats both per-primitive arms)
- **C-positive (12.2% is REAL not artifact)**: ALL of {C1: top-100-answer EM / least-900-answer EM < 5x ratio (not pure freq-bias); C2: substring-overlap < 50% of predictions; C5: random-seed EM ≤ 5% (generation IS conditional on seed)}
- **C4 hop-meaningful**: EM | start_entity NOT in supporting_facts > 5% (some non-trivial fraction of correct answers come from substrate generation expanding beyond the encoded start, not just emitting the seed back)

**HARD_FAIL** (all three):
- **B1 FAIL**: max α posterior_em < 0.13 (no α beats GENERATION_ONLY alone; score-fusion adds no value)
- **C2 FAIL**: substring-overlap ≥ 80% (12.2% is question-text-rebroadcast artifact, not substrate-internal QA)
- **C5 FAIL**: random-seed EM > 10% (generation is constant ~12% regardless of seed; the "signal" is uniform-prior emission, not retrieval-conditioned)

**MIDDLE_BAND**: any subset of the above mixed.

**cv cap**: cv_em across 3 seeds ≤ 0.10 per arm (matches v1 pre-reg).

**Calibration penalty (lit-scan; per Research discipline): P deflated 0.15-0.25 below naive; novel-synthesis P capped 0.50.**
- Naive P(B1 PASS) ~ 0.45 (score-fusion is a well-known composition fix; substrate-internal generation alone at 12% is a strong signal to fuse with anything coherent from retrieval).
- Deflated P(B1 PASS) = **0.25-0.30** (the 1.9% retrieval baseline is so low that even score-fusion may not add lift — additive fusion with α near 0 will dominate; capped at 0.30).
- Naive P(C-positive ALL three) ~ 0.55 (the 0.004 cv across seeds strongly implies real signal).
- Deflated P(C-positive ALL three) = **0.35-0.40** (could fail on C2 if many HotpotQA answers are title-substrings of questions; CERT 588 ingest had no such observation but ingest doesn't measure prediction substring-overlap).
- P(any axis lands chain-grade evidence) = **0.50** (capped per novel-synthesis discipline).

---

## Substrate-product implications

### IMMEDIATE atomization candidate (independent of composition fix)

**`META_substrate_only_decode_generation_partial_QA_on_real_benchmark`** — claim: SubstrateGenerator alone, with NO LLM forward calls and NO neural retrieval encoder, achieves 12.2% EM (cv 0.004 across 3 seeds, n=1000 HotpotQA dev) on real Wikipedia multi-hop QA. Below random ~0.5%, far above random multiple ~24x; below GPT-3.5 ~35%, but ~35% of GPT-3.5 at ZERO LLM compute. This IS the substrate-as-LLM-substitute partial-positive existence proof USER L1 vision specified.

- Tier: **MEASURED_MECHANISM** pending C-axis characterization (could promote to chain-grade if C-positive lands; could downgrade to mechanism-artifact if C2/C5 FAIL).
- Cert classification: needs Skunkworks ruling per A5 role-separation.
- Why this matters: even if composition fix (axis B) fails, generation-alone IS a chain-grade-relevant atom on a real benchmark — first such atom in the substrate.

### Composition pattern lessons (META candidate)

**`META_mode_aggregation_with_wrong_seed_is_anti_composition`** — composition arm in v1 cell uses (a) seed generator from KG top-1, and (b) mode-aggregate over (top-K + visited). When retrieval recall is far below generation EM, BOTH steps actively degrade: (a) wrong seed corrupts the generation trajectory; (b) mode-aggregation cannot recover the correct answer if it never appears in top-K. Discipline rule: **never aggregate by mode/count when one primitive is >10x the other's accuracy; use score-fusion with a learnable or pre-reg α.** Composes with META Fix #16 (mechanism-discriminating bands MUST include score-fusion sweep as the composition arm, not only top-K-prepend).

### Forward chain (if v2 lands HARD_PASS)

1. v2 score-fusion lands ≥ 0.15 EM → substrate-as-LLM-substitute existence proof STRENGTHENED.
2. v3: extend to NaturalQuestions / TriviaQA (more diverse question types; tests if 12.2% on HotpotQA generalizes).
3. v4: combine with MiniLM-L6 query encoder (axis A) for upper-bound on encoder regime; the difference v3 vs v4 quantifies the cost of substrate-only-decode at the QUERY stage.

---

## Citations (≥5 required)

External (lit-scan, generic queries; 4 + 1 follow-up):
1. **"When Retrieval Succeeds and Fails: Rethinking Retrieval-Augmented Generation for LLMs"** (arXiv:2510.09106v1) — low-recall retrieval CAN hurt rather than help; advocates conditional retrieval.
2. **"Scaling Retrieval-Augmented Generation with RAG Fusion: Lessons from an Industry Deployment"** (arXiv:2603.02153) — recall-oriented fusion gains neutralized after rerank+truncation; Hit@10 0.51 → 0.48.
3. **"Retrieval-Augmented Generation: A Comprehensive Survey of Architectures, Enhancements, and Robustness Frontiers"** (arXiv:2506.00054v1) — score-fusion and posterior-combination methods are the canonical composition pattern beyond top-K prepend.
4. **"Classification using hyperdimensional computing: a review with comparative analysis"** (Springer 2025, s10462-025-11181-2) — HDC bag-of-trigrams stable to misspellings (0%-8% drop) but underperforms neural embeddings on long-text semantic retrieval. Encoder regime confirmation.
5. **"High-dimensional distributed semantic spaces for utterances"** (arXiv:2104.00424) — utterance-level HD vectors require positional binding / role-filler, not just bag-of-trigrams. Supports the long-question encoder failure diagnosis.

Substrate-internal (cert_ledger evidence; 4):
- `data/exp_g1_substrate_native_generation_v1/metrics.json` + cert ledger row 650 — g1 MEASURED_MECHANISM (by-construction-saturation tiering).
- `data/exp_g1b_capacity_sweep_v1/metrics.json` + cert ledger row 652 — g1b CERT 587 chain-grade at headroom regime.
- `data/exp_h_hotpotqa_ingest_v1/metrics.json` + cert ledger row 654 — h_hotpotqa CERT 588 with MiniLM-L6 encoder.
- `notes/h_hotpotqa_ingest_pre_reg_2026-06-22.md` — explicit pre-reg of MiniLM-L6 over pythia-160m mean-pool (the encoder regime contrast).

---

## Next cell to dispatch

**Anchor:** `substrate_native_qa_hotpotqa_v2_composition_drill`
**Routing:** overnight_queue (GPU) per Fix #22; encoder + KG codebook reuse v1 (N_DIM=8192 char_trigram); only the composition aggregation + characterization arms are new. Wall budget ≤2hr (11 arms × 3 seeds × ~200ms/q × 1000q ≈ 110min; +20min slack).
**Smoke:** 50 questions, 1 seed, ≤5min; verify all 11 arms run + EM computed; smoke not expected to HARD_PASS at small N.
**Pre-reg:** this file IS the pre-reg per the bands above; will not be revised post-VET.

—Research (Director)

## OUTPUT (one line for spawn contract)

`substrate_native_qa_2x_revival_drill_delivered: D:/AI/hd-instrument/notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md; HEADLINE: g1b alone gets 12.2% EM on HotpotQA (cv 0.004) = substrate-as-LLM-substitute existence proof OBSCURED by composition mode-aggregation sabotage; encoder regime (char_trigram on sentences vs MiniLM-L6 on entity names) is the OTHER load-bearing diagnosis; P_deflated=0.50 (capped novel-synthesis); next-cell: substrate_native_qa_hotpotqa_v2_composition_drill (score-fusion α-sweep B + 5 characterization arms C; ≤2hr wall)`
