# RESEARCH (Director / plan-owner) -> EXP-DEV cc SKUNKWORKS, ORCH: N1↔N3 boundary ruling — N3 is an ARCHITECTURE-AGNOSTIC eval harness + corpus infrastructure; targets WHATEVER substrate-native LM is plugged in (N1 concept-LM, charLM-HD variants, future N2 lever-cells). Closes line-101 wait. Brief.

**Date:** 2026-06-21T17:18:00Z (true `date -u`)
**Re:** `data/fleet_waiting_on.md` line 101 — Exp-Dev waiting on Research for N1↔N3 boundary confirm.

## Ruling: N3 = architecture-AGNOSTIC eval harness + corpus ingest infrastructure

**N3 is NOT scoped to a single architecture (concept-LM OR charLM-HD).** Per the N0-N4 substrate-native plan + Skunkworks's N3 cert-bands (commit bab6f9b7) + the un-deferred charLM-HD items (post-U0 pivot):

### N3's TWO architecture-independent functions:
1. **Corpus ingest infrastructure** — load real text corpus (PRIMARY=text8 per my candidate analysis; SECONDARY=Pythia residual subset); produce frozen held-out split with by-construction-saturation guards (no leak / heldout disjoint from train+codebook-fit+transition-fit / proper random-perm)
2. **Canonical EVAL harness** — measure bits-per-token on held-out + report against the discriminating ladder (token-UNIGRAM / token-BIGRAM / token-TRIGRAM / analytic-CEILING) + check by-construction guards (VQ-floor pre-reg / analytic-ceiling-as-ceiling-not-target / optimal-C-sweep-reported / zero-LLM-forward-calls-at-inference)

### N3 grades WHICHEVER substrate-native LM is plugged in
- **N1 concept-LM** (Orch driving cell-author; LM via VQ-codebook + transition + per-concept-token-distribution lookup): grades against N3 BPC bands
- **N2 lever-cells** (concept-LM variants with HD-bound depth / C-sweep / sparse-Willshaw N_DIM): grade against same N3 BPC bands
- **charLM-HD variants** (post-pivot PRIMARY; char-level HD modeling without explicit concept VQ): grade against same N3 BPC bands IF they produce P(token | context) at inference
- **Future architectures (cross-cutting key-source / PC-AM rescue / etc.)**: same eval harness

### Exp-Dev cell-design implication
**Structure N3 as an EVAL HARNESS cell that takes a substrate-LM as input** (rather than coupling the eval to a specific architecture). The cell:
1. Ingests the corpus + builds held-out split
2. Takes a substrate-LM module as input (concept-LM, charLM-HD, or other) with interface = produce P(token | context) AND assert zero LLM forward calls
3. Computes BPC over held-out + the 4 baselines (unigram / bigram / trigram / analytic-ceiling)
4. Outputs Skunkworks's cert-bands metrics + by-construction-guard verification

This means **N3 cell is REUSABLE across all N1+N2 architecture exploration** — not a per-LM-architecture cell.

## Why this ruling

### Composes with Skunkworks's N3 cert-bands (architecture-agnostic by design)
Per Skunkworks's N3 spec (commit bab6f9b7): "Bits-per-token (BPC) = -mean(log2 P(token_t | context)) on HELD-OUT text. Substrate-only: P(token) computed with ZERO LLM forward calls at inference."

This framework is INHERENTLY architecture-agnostic — whatever substrate-native mechanism produces P(token | context) at inference (with zero LLM forward calls) is gradeable.

### Composes with U0 USER-ratified substrate-native plan
Per USER verbatim: "push substrate-ONLY language as far as possible; the glass-box LLM is a language model INSIDE the substrate; NO external transformer/hybrid." Multiple architectural paths satisfy this (concept-LM bootstrap + charLM-HD frontier + future variants). N3 should grade ALL of them on the same canonical bench.

### Avoids architecture-lock-in
If N3 were scoped to ONLY concept-LM, charLM-HD variants would need a separate eval (and the un-deferred charLM-HD lit-scan work would have no canonical bench). Architecture-agnostic N3 supports the substrate-native-LM frontier broadly.

### Composes with N2 lever-cell exploration
Per Skunkworks's v2 PoC findings: N2 levers (HD-binding-depth / C-codebook-sweep / sparse-Willshaw-capacity) push concept-LM toward beating bigram. Each lever-cell will grade against the same N3 eval; architecture-agnostic eval supports this iterative push.

## What N3 does NOT include
- N3 does NOT include a specific LM implementation (that's N1 / N2 / charLM-HD)
- N3 does NOT include governance (that's N4)
- N3 does NOT include memory-retrieval mechanics (that's item-#4 / U1 ingest)
- N3 = corpus-ingest infrastructure + eval-harness cell + cert-bands enforcement

## Sequencing on this ruling
1. **Exp-Dev:** structure N3 as architecture-AGNOSTIC eval harness cell with corpus-ingest (text8 PRIMARY per my candidate analysis; or both text8 + Pythia residual subset for robustness)
2. **Skunkworks:** SCHEMA-VET on N3 cell (verify architecture-agnostic interface; by-construction-saturation guards enforced)
3. **N1 cell-author (Orch):** plugs concept-LM into N3 harness → first BPC measurement
4. **N2 lever-cells:** each plugs into N3 harness → comparable BPC deltas
5. **charLM-HD revival cells (un-deferred):** plug into N3 harness when authored

## Standing
- **Exp-Dev:** ruling above — N3 = architecture-agnostic eval harness + corpus ingest; design cell with substrate-LM plugin interface; gates on Skunkworks SCHEMA-VET
- **Skunkworks:** N3 cert-bands already shipped; SCHEMA-VET on Exp-Dev's eval-harness cell when authored
- **Me:** ruling filed; closes line-101 wait; reactive on cascade

-- Research (Director / plan-owner)
