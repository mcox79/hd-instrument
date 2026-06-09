# exp_dev hand-off — research: Path B architectural variations and failure-mode map

**Filed:** 2026-06-09 by research sub-agent (5x lit-scan, KBLaM failure mode + backup architecture mapping).

**Trigger:** User mandate: Path B de-risk is queued at 2000 facts (Pythia). If de-risk FAILS (held-out < 0.50): architectural backup variants identified and ranked. This hand-off pre-registers the backup anchor sequence so exp_dev can pick up immediately without re-doing the architecture search.

Research note path: `d:/AI/hd-instrument/notes/research_drill_path_b_variations_5x_2026-06-09.md`

**Pause state:** Check `data/orchestrator_paused.flag` before queue dispatch. Annotation bumps allowed while paused; queue-triggering commits require ACTIVE state.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters beyond the evidence-backed starting points in the research note.

---

## Trigger condition

This hand-off activates when Path B de-risk (C1-FACT-v2 or equivalent) returns held-out recall < 0.50 on the primary training recipe. Do NOT activate if de-risk PASSES (held-out >= 0.50) — proceed with full Path B scale-up instead.

---

## What the research found

Path B de-risk at 2000 facts has 5 identified failure modes:
1. KB too small for W_k/W_v adapter generalization (dominant at 2000 facts; W_k is massively underspecified)
2. Memorization bypass (Pythia-160M may parametrically memorize 2000 facts, bypassing KB adapter)
3. Gate collapse (sigmoid gate initialized at -4 may stay closed if gradient signal too sparse at 2000 facts)
4. Encoder manifold mismatch (Sentence-BERT and LLM hidden space have different geometry)
5. Every-layer injection overfitting (12-layer injection has too few examples per layer at 2000 facts)

Six architectural variations ranked by P_deflated x (1/cost) x differentiation. Five substrate-unique innovations. Four hybrid approaches. Full detail in research note.

---

## Anchor candidates (rank-ordered, cheapest-first per PROT-004)

### Anchor B-BACK-1 — K/V prefix injection smoke (CPU-local, zero training)
- **Pointer:** research note Level 2, Section 2.6 "Knowledge Capsules"; arXiv:2604.03270 (Knowledge Packs)
- **Substrate-product reading:** If Pythia-160M can answer held-out fact questions with substrate facts serialized as K/V prefix (no adapter training), the model's attention is compatible with substrate-formatted knowledge injection. This is the cheapest possible Path B backup: zero GPU, no training, tests the fundamental compatibility hypothesis. If this fails (accuracy no better than no-prefix baseline), all soft-attention paths are likely closed and pivot to substrate-as-tool is the correct call.
- **Tier hint:** CPU-local, ~30-60 min eval, no training
- **Why now:** This is the cheap decisive test (per [[feedback-drill-pretest-required]]) before any GPU spend on backup anchors. Run this before B-BACK-2 through B-BACK-5.

### Anchor B-BACK-2 — PP-107 algebraic gate substitution (CPU-local, delta on existing code)
- **Pointer:** research note Level 3, Section 3.2 "PP-107 algebraic gate substitution"; cap_map PP-107 validated (AUC=1.000)
- **Substrate-product reading:** Replace KBLaM's learned sigmoid gate with substrate's non-trainable PP-107 confidence threshold. Prevents gate collapse (failure mode 3). If held-out recall improves >= 1.20x vs learned gate, gate collapse is confirmed as a primary failure mode and the PP-107 gate is a substrate-native fix with no competitor equivalent. Product claim: "algebraic abstention gate eliminates learned-gate collapse at small KB scale."
- **Tier hint:** CPU-local (code delta only, re-run existing de-risk eval, ~2-3 eng-days + 1-2h eval)
- **Why now:** Minimal engineering, runs on same infrastructure as de-risk. Should run in parallel with B-BACK-1 if infrastructure allows.

### Anchor B-BACK-3 — kNN-LM inference ensemble (GPU or remote CPU)
- **Pointer:** research note Level 2, Section 2.3 "kNN-LM ensemble"; arXiv:1911.00172; cap_map pool retrieval validated
- **Substrate-product reading:** No-training-required backup. FHRR projection from Pythia hidden state -> substrate cosine retrieval -> interpolate p_LM with p_kNN. If lambda-optimal ensemble gives >= 3 pp accuracy improvement on held-out fact completions, substrate-FHRR space and Pythia hidden space are sufficiently aligned for inference-time KB retrieval without adapter training. This is the "Path B without training" version — weaker than full Path B but a real capability at zero training cost.
- **Tier hint:** GPU or remote CPU (FHRR projection + kNN eval, ~1 eng-week implementation + 1-2h eval on A100 or remote CPU)
- **Why now:** Run after B-BACK-1 and B-BACK-2 if both fail to fix the de-risk. Provides an inference-only fallback before committing to B-BACK-4's training costs.

### Anchor B-BACK-4 — Single-layer injection + SR-KI attention supervision + 50K facts (GPU, training)
- **Pointer:** research note Level 1 Sections 1.2 + 1.3 + Level 2 Section 2.2; arXiv:2511.06446 (SR-KI); KBLaM arXiv:2410.10450 training recipe
- **Substrate-product reading:** Fix the training recipe: (a) reduce layer injection to last-N layers only (addresses failure mode 5), (b) add L_attn supervision (addresses failure mode 3 and 1.3 CE-only), (c) scale KB to 50K facts (addresses failure mode 1 and 2). This is the "fix the training recipe properly" path rather than the "try a different architecture" path. If held-out recall >= 0.50 at 50K facts with this recipe, the original de-risk failure was a recipe problem not a fundamental Path B problem, and scale-up can proceed with the fixed recipe.
- **Tier hint:** GPU (50K fact KB, 1K training steps, ~1-2h on A100; remote_gpu_queue)
- **Why now:** Run after B-BACK-1/2/3 establish the no-training baseline. This is the "full training fix" anchor; requires GPU authorization and ~2-3 eng-weeks for recipe implementation.

### Anchor B-BACK-5 — FHRR-native adapter + K-hop multi-step retrieval (GPU, longer, most differentiated)
- **Pointer:** research note Level 3 Sections 3.1 + 3.4; HD Probe arXiv:2509.25045; cap_map multi-hop validated (+0.983 vs kNN-LM)
- **Substrate-product reading:** Replace Sentence-BERT encoder with substrate FHRR encoding; add K-hop multi-step retrieval (K=2) for 2-hop questions. If 2-hop accuracy >= 0.45 on held-out examples, this is a categorical product claim KBLaM and all single-step RAG architectures cannot match: "substrate-attention with K-hop traversal answers multi-hop factual questions that require reasoning chains through the KB." Simultaneously closes the multi-hop revival question (project_multihop_revive_priority.md). Most differentiated anchor; highest engineering cost; run last but should not be skipped if B-BACK-4 reaches MID-BAND.
- **Tier hint:** GPU, longer run (Pythia-410M preferred, 50K facts, multi-hop training examples, K=2 traversal; ~2-4h on A100; remote_gpu_queue)
- **Why now:** Run after B-BACK-4 confirms base recipe works (held-out >= 0.30). Do not run if B-BACK-4 fails.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_path_b_variations_5x_2026-06-09.md`
- Prior generalizable retrieval handoff (C1-FACT-v2 context): `d:/AI/hd-instrument/notes/exp_dev_handoff_research_generalizable_retrieval_5x_2026-06-09.md`
- Cap_map (PP-107, multi-hop, pool retrieval, FHRR validated rows): `d:/AI/hd-instrument/notes/substrate_capability_map.md`
- Prior Tier 4 LLM architecture proposals: `d:/AI/hd-instrument/notes/research_drill_tier4_llm_architecture_proposals_3x_2026-06-07.md`
- Multi-hop revival priority: `d:/AI/hd-instrument/memory/project_multihop_revive_priority.md`
- Scaling law reference: arXiv:2604.00715 (memorize-vs-retrieve pretraining)
- Fact memorization ceiling: arXiv:2406.15720 (C = C* - alpha*exp(-beta*Epoch))

---

## Contract section

**Stopping criteria for this backup sequence:**
- STOP and pivot to substrate-as-tool if: (a) B-BACK-1 fails (< 0.20 zero-shot accuracy), AND (b) B-BACK-2 fails (< 1.05x recall improvement), AND (c) B-BACK-3 fails (< 3 pp accuracy improvement). This triple failure indicates fundamental manifold incompatibility.
- CONTINUE to B-BACK-4 if any of B-BACK-1/2/3 shows partial signal (>= threshold).
- CONTINUE to B-BACK-5 only after B-BACK-4 reaches MID-BAND (held-out >= 0.30).

**HARD-FAIL for full backup sequence:** all 5 backup anchors return below threshold (see research note Level 6). At that point, Path B is abandoned and product strategy pivots to Panel A + Path A + substrate-as-tool.

**HARD-PASS for full backup sequence:** any single anchor reaches its HARD-PASS threshold. Path B is viable; scale up with that architecture.

---

## Autonomy declaration

exp_dev owns ALL parameter choices: N, M, K, seed count, learning rate schedule, threshold bands, queue routing, anchor naming, smoke vs full profile, ETA. This hand-off provides architectural direction and evidence pointers only. The orchestrator does not specify implementation parameters.
