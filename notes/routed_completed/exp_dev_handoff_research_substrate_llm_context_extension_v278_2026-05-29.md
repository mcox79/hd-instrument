# exp_dev hand-off -- research: substrate as INTRINSIC LLM context extension (v278, 2026-05-29)

Filed by: research sub-agent (Opus-escalated; DEEPER fresh-eyes drill)
Trigger: research delivery notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md
Pause state: HONOR pause flag; check data/orchestrator_paused.flag before any ship

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides ANCHOR CANDIDATES + CONTEXT POINTERS + CONTRACT + AUTONOMY DECLARATION. The exp_dev agent owns: anchor selection from the rank-ordered candidates, sweep grids, HF1/HF2/HF3 numerical bounds, queue choice + ETA, pre-committed cap_map decisions. This hand-off does NOT specify those.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Property 4 Johnson-Lindenstrauss sanity check (substrate-LLM-internal-rep compatibility)

- **Anchor pointer:** notes/seven_intrinsic_properties_validation_designs_v278_2026-05-29.md Property 4 Section D ("1-hour cheap sanity check")
- **Substrate-product reading:** GATING TEST. Decides whether substrate-as-deeper-layer-integration (L2-L4 in the context-extension landscape) is a viable product track or closes cleanly. PASS opens 6-12 week E2-E4 build path; FAIL focuses substrate on L1 extensions exclusively (E1 + E5).
- **Tier hint:** Tier-0 SANITY (cheapest possible probe; 1 hr CPU; ~$0)
- **Why-now:** This drill formalizes Property 4 as the L2-L4 gating prerequisite. Running it Week 1 of the 3-month roadmap (alongside E1 build) is structurally correct sequencing; results inform Month 2 commitment.
- **Substrate primitives needed:** N=4096 BSC substrate, codebook init, cosine-cleanup (all production-N HARD_PASS)
- **LLM dependency:** GPT-2-small (open-weight, HuggingFace; no API cost) OR Llama 3.1-8B if available locally
- **Verification scope:** HARD-PASS >=70% top-5 retrieval on 1K-item needle-in-haystack; HARD-FAIL <=30%; middle band 30-70% flagged for review

### Anchor 2: E1 substrate-LLM hybrid MVP (L1 CoT state offload)

- **Anchor pointer:** notes/substrate_llm_hybrid_multihop_architecture_v278_2026-05-29.md Section 6 (5-day MVP plan) + notes/pattern_b_integration_demo_executable_spec_v278_2026-05-29.md (Pattern B FastAPI scaffold)
- **Substrate-product reading:** Pattern B headline upgrade. Multi-hop agentic reasoning with audit chain. Closed-weight Claude/GPT-4 friendly; demos viable in Week 1 of pilot pitches.
- **Tier hint:** Tier-1 PRIORITY (3-5 day engineering; ~$20-50 API budget; P_deflated 0.55 HARD-PASS on HotpotQA 1000-q)
- **Why-now:** v278 hybrid spec is engineer-ready; HotpotQA benchmark is established; 5-day cycle fits Week 1 of 3-month roadmap. Status_log entries indicate this is queued from v278 hybrid delivery.
- **Substrate primitives needed:** hdlab_service Day-1 FastAPI scaffold (DONE per substrate-LLM hybrid spec); ingestion pipeline for HotpotQA passages; substrate.retrieve_fact + substrate.compose_query + audit_log + deletion_cert
- **LLM dependency:** Claude Sonnet via Anthropic Messages API (tool-use protocol)
- **Verification scope:** see notes/substrate_llm_hybrid_multihop_architecture_v278_2026-05-29.md Section "Falsifiable predictions" (HP1/HP2/HP3 + HF1/HF2/HF3)

### Anchor 3: E5 substrate-as-Letta-archival-backend (L1, partnership path)

- **Anchor pointer:** notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md Section 7 E5 + notes/anthropic_memory_competitive_and_agentic_ai_architecture_v278_2026-05-29.md Section 12.1 (Cognition Labs / Letta partnership pathway)
- **Substrate-product reading:** Structural partnership via product-engineering integration. Letta has existing customer base; substrate's deletion-cert + per-fact audit is differentiated. Closed-weight friendly.
- **Tier hint:** Tier-1 PRIORITY (1-2 week engineering; ~$0 marginal API budget; P_deflated 0.45 integration ships)
- **Why-now:** Letta agent framework is production; substrate-as-archival is a drop-in replacement; product-engineering channel matures the substrate-product positioning
- **Substrate primitives needed:** Letta API integration; REST wrapper around substrate.retrieve_fact + substrate.store_fact; audit_log surfaced through Letta interface
- **LLM dependency:** ANY (Letta-agnostic)
- **Verification scope:** drop-in replacement validation on Letta benchmark suite + custom agent multi-day session test

### Anchor 4: E3 substrate-as-KV-cache-extension (L3 deep integration, GATED on Anchor 1)

- **Anchor pointer:** notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md Section 7 E3 + Memorizing Transformers (Wu et al. 2022) baseline
- **Substrate-product reading:** HEADLINE DEEP INTEGRATION. Substrate becomes "compute-cheap audit-grade context extension". 50K-100K effective context on Llama 3.1-8B. Killer feature 1+2+5 deeper-layer instantiation.
- **Tier hint:** Tier-1 DEEP (2-3 week engineering; ~$100-200 budget; P_deflated 0.40 HARD-PASS on PG-19 perplexity matching MT baseline; HEAVILY GATED on Anchor 1 PASS)
- **Why-now:** if Property 4 sanity PASSes (Anchor 1), this is the Month 2 headline. If Property 4 FAILS, this anchor is closed cleanly without ship cost.
- **Substrate primitives needed:** substrate ingestion of KV pairs (new ingest path); attention-layer modification on Llama-3.1-8B (~200 LOC; reuse Memorizing Transformers reference architecture); benchmark harness for PG-19 / arXiv-math
- **LLM dependency:** Llama-3.1-8B local hosting (open-weight required); HuggingFace Transformers infrastructure
- **Verification scope:** see notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md Section "Falsifiable predictions" E3 (HP1/HP2/HP3 + HF1/HF2/HF3)

### Anchor 5: E2 substrate-as-compressed-prompt-store (L2, GATED on Anchor 1)

- **Anchor pointer:** notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md Section 7 E2 + gist tokens (Mu et al. 2023) baseline
- **Substrate-product reading:** "prompt-compression-with-audit" product category. Complementary to E3; deeper than L1 but shallower than L3.
- **Tier hint:** Tier-2 (1-2 week engineering; ~$50-100 budget; P_deflated 0.35 HARD-PASS on 10x compression at 80% quality)
- **Why-now:** if Anchor 1 PASSes, ship after E3 lands (Month 2-3); complementary L2 demo
- **Substrate primitives needed:** substrate ingestion of AutoCompressor-style gist embeddings; soft-prefix injection at Llama input embedding layer
- **LLM dependency:** Llama-3.1-8B
- **Verification scope:** see notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md Section "Falsifiable predictions" E2

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/substrate_llm_context_extension_intrinsic_v278_2026-05-29.md (THIS drill; landscape + 7-layer matrix + 5 ship candidates + customer demos)
- d:/AI/hd-instrument/notes/substrate_llm_hybrid_multihop_architecture_v278_2026-05-29.md (v278 hybrid spec; E1 ship-ready)
- d:/AI/hd-instrument/notes/pattern_b_integration_demo_executable_spec_v278_2026-05-29.md (Pattern B FastAPI scaffold + 8-week build plan)
- d:/AI/hd-instrument/notes/seven_intrinsic_properties_validation_designs_v278_2026-05-29.md (Property 4 sanity check details, Anchor 1)
- d:/AI/hd-instrument/notes/anthropic_memory_competitive_and_agentic_ai_architecture_v278_2026-05-29.md (Part II agentic memory hierarchy; Letta partnership pathway, Anchor 3)
- d:/AI/hd-instrument/notes/research_lagging_caps_v276_fresh_eyes_2026-05-29.md (substrate primitives inventory; production-N status per primitive)
- d:/AI/hd-instrument/notes/strategic_roadmap_llm_integration_3mo_v278_2026-05-29.md (3-month roadmap; this drill refines Item 3 Pattern C)
- d:/AI/hd-instrument/hdlab_service/ (FastAPI scaffold; Day-1 of E1)

---

## Contract

- exp_dev OWNS:
  - Anchor selection from the 5 ranked candidates (sequencing, dependencies)
  - Sweep grids (substrate N, M_frac, codebook init seeds for variance)
  - HF1/HF2/HF3 numerical bounds (use values in v278 hybrid + this drill's E1/E2/E3 predictions as starting point; tighten per substrate cap_map)
  - Queue choice (GPU vs CPU; Anchor 1 is CPU; Anchor 2-3 are mixed CPU+LLM-API; Anchor 4 is GPU for Llama hosting)
  - Pre-committed cap_map decisions (none; this drill does NOT pre-commit cap_map)
  - ETA bands per anchor
  - PROT-018 anchor name `_n<N>` suffix discipline
  - Per-experiment `--timeout` calculation per [[feedback-per-experiment-timeout-required]]
  - Ingestion dependency verification per [[feedback-ship-before-dependency-verified]]

- research (THIS hand-off) provides:
  - 5 anchor candidates with substrate-product reading, tier hint, why-now, primitives needed, LLM dependency, verification scope
  - Context pointer files (no inline summaries)
  - Strategic sequencing recommendation (Anchor 1 + Anchor 2 in parallel Week 1; Anchor 3 Week 2-3; Anchor 4 gated on Anchor 1 PASS; Anchor 5 gated on Anchor 4 PASS)

- research does NOT provide:
  - Anchor names
  - Sweep grids
  - HF1/HF2/HF3 numerical bounds (the predictions in the drill are starting point; exp_dev tightens)
  - Queue routing or ETA
  - Cap_map pre-commitments

## Autonomy declaration

exp_dev has full autonomy on the 5 anchor candidates above; this hand-off does not dictate any specific experiment design or ship sequencing beyond the strategic recommendation that Anchor 1 (1-hour CPU sanity) precedes commitment of E2-E4 build budget. exp_dev may choose to ship anchors in different order, alter the dependency gating, defer anchors based on queue health, or surface alternative anchors that this drill missed.

Pause flag honored: if data/orchestrator_paused.flag exists, no ship; this hand-off is read-only until resume.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
