# 2026-07-03 substrate_rag_with_substrate_composition_smoke

## Architectural context (load-bearing)

This cell tests **substrate as REASONER over retrieved chunks** — NOT rerank/selection.

- bge retrieves top-K=5 candidate chunks
- Substrate does multi-hop bind/unbind composition over retrieved chunks
- Answer is COMPOSED from evidence in chunks; it may not be verbatim in any single retrieved chunk

**Distinct from:**
- Rerank arc (7 witnesses, verify_v1 at +0.027 F1, closed as tested-and-modest) — rerank SELECTS best chunk
- Rerank-v2 explicit-structure cell (separately firing) — still selection, not composition
- `substrate_multihop_pfc_chunked_2hop_decomposition_v1` (cosine=0.36 prior hit, HARD_FAIL) — substrate-alone chain, NO retrieval frontend. That cell HF'd at intrinsic per-hop information-theoretic floor. Load-bearing question here: **does retrieval frontend inject fresh evidence at each hop, breaking the floor?**

**Framing per USER-locked anchors:**
- SUBSTRATE KNOWS ALMOST NOTHING — this cell tests ARCHITECTURE (composition over retrieval), not knowledge
- Corpus is programmatically-generated synthetic facts (matches `feedback_smoke_clean_synthetic_data_not_substrate_state_USER_2026-06-23`)
- Codebook (entity/relation/value → HD) is deterministic-by-construction (fair test of composition primitive; substrate not required to LEARN concepts here)

## Task class
MULTI-HOP QA with retrieval frontend. Templated 2-hop compositional queries over a synthetic (entity, relation, value) fact corpus. Ground truth known by construction.

## Corpus + query construction (smoke)
- E=20 entities, R=5 relations, V=20 unique values; 40 facts total; per-entity r-coverage engineered to admit 2-hop chains
- Facts stored as text chunks: `"The <r> of <e> is <v>."`
- Queries: 20 templated 2-hop `"What is the <r1> of the <r2> of <e0>?"` with valid chain by construction
- N_DIM (smoke) = 4096; N_DIM (full sentinel) = 8192

## Compute architecture
Class: **(b) sequential-CPU with justification**. Per-query loop is inherently sequential (substrate unbind stage 1 depends on stage 0 output). N_DIM=4096 with 20 queries and 3 seeds keeps smoke wall < 180s. FULL will lift to N_DIM=8192 and 100 queries; still CPU. No GPU speedup available on the per-query multi-hop chain path.

Storage strategy: **sharded** — each fact stored as its own HD (bind of role-filler triple). Retrieved chunks each contribute one HD to the composition step. Not bundled. Complies with META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW.

## Arms (7 arms × 3 seeds = 21 units in smoke)
- `ARM_BGE_ALONE_SINGLE_CHUNK` — bge top-1 chunk's value as answer (naive baseline; expected fail on multi-hop)
- `ARM_BGE_ALONE_TOP_K_CONCAT` — pick value from top-K chunks by best-single-chunk-value-string match (naive multi-doc, no reasoning)
- `ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION` — **LOAD-BEARING**: bge top-K=5 → substrate 2-hop unbind chain → cleanup against value codebook
- `ARM_SUBSTRATE_ALONE_NO_RETRIEVAL` — substrate 2-hop chain over full corpus (no bge frontend)
- `ARM_TANDEM_RANDOM_CHUNKS_CONTROL` — substrate composition on 5 RANDOM chunks (isolates: does chunk-quality matter or is it substrate mechanism alone?)
- `ARM_RANDOM_BASELINE` — random value from codebook (chance floor)
- `ARM_TANDEM_SUBSTRATE_ORACLE` — substrate composition on the KNOWN GROUND-TRUTH chunks (upper bound)

## Metric
`answer_correct` = predicted value string == ground-truth value string (exact match; codebook is discrete).

## HPs
- HP1: `ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION` >= 0.40
- **HP2 (LOAD-BEARING):** `ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION` - `ARM_BGE_ALONE_TOP_K_CONCAT` >= +0.10
- HP3: `ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION` - `ARM_SUBSTRATE_ALONE_NO_RETRIEVAL` >= +0.10 (retrieval frontend adds value)
- HP4: `ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION` - `ARM_TANDEM_RANDOM_CHUNKS_CONTROL` >= +0.10 (chunk quality matters)
- **HF**: substrate composition fails all metrics (composition adds no value over rerank / concat / substrate-alone)
- **MB**: some HP fires but not all four

Verdict is `HARD_PASS` iff HP1 + HP2 + HP3 + HP4 all fire. `HARD_FAIL` iff none. `MIDDLE_BAND` iff partial.

## Discriminator-fires assertion (META_RULE_K)
Smoke must show ARM_TANDEM_SUBSTRATE_ORACLE >= 0.60. If oracle (perfect retrieval + substrate composition) can't clear 0.60 at N=4096 with 20 clean queries, the composition primitive itself is broken at this regime — do NOT dispatch full.

## Discriminator-survives-scale (pattern C: preview-arm)
Smoke includes N_DIM=4096 (smoke_dim); FULL uses N_DIM=8192. Per Plate 1995 FHRR literature, cleanup accuracy scales monotonically with N_DIM at fixed capacity M — the smoke gap should widen, not shrink, at full. Explicit CRLB check: at K=1 (single-key unbind) and M=40 facts, N=4096 gives noise floor ~ sqrt(K/N) ~ 0.016 — well below discriminator gap [0.10, 0.30]. Discriminator survives scale.

## CRLB / reachability
- `crlb_floor_computed: 0.016` (per-hop unbind noise at N=4096, M=40; formula sqrt(K/N) with K=1)
- `crlb_formula_reference: "sqrt(K/N) per Plate 1995 FHRR unbind noise floor"`
- `discriminator_reachability: true` — HP thresholds (0.40 abs, 0.10 relative) sit well above CRLB floor at both smoke and full regime

## Baseline-in-band (META_RULE_AG)
- `ARM_RANDOM_BASELINE` expected ~ 1/V = 0.05 (below 0.05 band-floor OK; this arm is the chance-floor)
- `ARM_BGE_ALONE_TOP_K_CONCAT` expected in [0.10, 0.40] on 2-hop (bge finds ONE relevant chunk but not chain-composed answer)
- `baseline_in_band: true` for TOP_K_CONCAT (0.10-0.40 sits in [0.05, 0.95])

## Effective-vs-nominal parameter audit (META_RULE §15.A)
No sweep axis in this cell (fixed arm × seed grid). N/A.

## Bracket-includes-discriminating-band (META_RULE §15.B)
No sweep axis. N/A.

## Signal-shape compatibility (META_RULE §15.C)
- bge top-K text-chunk output → substrate encoder input: SHAPE_MATCH via `chunk_HD = bind(entity_HD, bind(relation_HD, value_HD))` factory (lookup on codebook, no learned adapter)
- Substrate unbind chain output → value codebook cleanup: SHAPE_MATCH via cosine-argmax over V-value codebook

## Positive-control-reproducer-arm (META_RULE §15.D)
- `ARM_TANDEM_SUBSTRATE_ORACLE` serves as the positive control: substrate composition over the KNOWN ground-truth chunks. If oracle < 0.60, primitive doesn't extend to this regime; downstream arms cannot be trusted.

## Functional-requirements decomposition (META_RULE §15.E)
- FR1: encode fact text into HD → `chunk_HD = bind_triple(entity, relation, value)` (FHRR bind primitive; chain-grade)
- FR2: parse query template into role-filler chain → deterministic template regex (queries are constructed with known template)
- FR3: multi-hop unbind chain → 2 stages of `unbind + cleanup` (chain-grade primitive from Cell 3 tonight; ref `stage2_vsa_cell3_multi_hop_reasoning_smoke`)
- FR4: cleanup composed HD to answer text → cosine-argmax over value codebook

## Cell-template mandates (SCHEMA-VET checklist)
- `arms_differ_verified: true` — per-arm prediction arrays hashed at smoke gate
- `final_metrics_atomicity: "tmp_replace"` — atomic os.replace at end
- `except SystemExit: raise` before `except Exception:` — verified in cell outer try
- `crlb_floor_computed: 0.016`, `discriminator_reachability: true`
- `baseline_in_band: true`
- `cardinality_ok: true` — EXPECTED_N_UNITS = 7 arms × 3 seeds = 21; verdict counts len(per_unit)
- `calibration_check: "default_ok_for_this_regime"` — FHRR bind/unbind primitive defaults are chain-grade at N=4096
- `cell_chunked: false` — single cell handles 3 seeds (smoke; 3 seeds × 20 queries × 7 arms is bounded)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true` (per-seed heartbeat via `_cell_heartbeat`)
- `defensive_error_checking: "passed_all_4_patterns"`
- `progress_logging: "print_flush_true"` (smoke wall << 30min, but discipline)

## HP_SCOPE (per-arm HARD_PASS applicability)
- HP1 applies to: `ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION`
- HP2 applies to gap: TANDEM_RAG - TOP_K_CONCAT
- HP3 applies to gap: TANDEM_RAG - SUBSTRATE_ALONE
- HP4 applies to gap: TANDEM_RAG - RANDOM_CHUNKS

Baselines (`RANDOM_BASELINE`, `BGE_ALONE_SINGLE_CHUNK`) are NOT subject to HARD_PASS floors — they're diagnostic reference lines.

## Prediction / implication
- If HP2 fires (TANDEM > TOP_K_CONCAT by >=0.10): substrate composition adds real reasoning value → **substrate-as-RAG-reasoner is the target architecture for M3/M4 tandem**
- If HP2 HF: substrate multi-hop composition cannot leverage retrieval effectively; retrieval + selection (rerank) may be the only useful tandem
- If HP3 HF but HP2 fires: composition helps but retrieval doesn't — substrate-alone at scale is viable (unlikely given prior HF)

## Numbers tagged (META_RULE_AC)
- `crlb ~ 0.016 at N=4096 K=1` THEORETICAL@sqrt(K/N) per Plate 1995
- rerank verify_v1 `+0.027 F1` CITED@Director spawn prompt (rerank arc closure claim)
- pfc_chunked_2hop_decomposition prior HF MEASURED@`data/exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1/metrics.json` (VERDICT_OF->HARD_FAIL; concept-query cosine=0.3604)
- ALL HP thresholds are HYPOTHESIZED@this prereg (band selection based on architectural expectation; will be measured by smoke/full)

## Stage classification
Stage 3 (higher-function composition + retrieval tandem). NOT Stage 4 (no language-benchmark; synthetic corpus by construction).
