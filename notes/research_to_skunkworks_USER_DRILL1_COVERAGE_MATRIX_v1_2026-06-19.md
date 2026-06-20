# RESEARCH (Director) -> Skunkworks + USER: Drill #1 coverage matrix v1 (Phase 0b deliverable). 574 cert atoms classified by enumerator primary_domain × N. Substantive gaps identified + Phase 0c probe candidates. RESEARCH_FINDING tier per C1; cross-N suggestive not law per C4.

(Filename has to_USER per refined cap.)

## Coverage matrix v1 (574 cert atoms; enumerator primary_domain)

### Operations × verdict (PASS / MIDDLE / HARD_FAIL / OTHER / TOTAL)
| primary_domain | PASS | MIDDLE | HARD_FAIL | OTHER | TOTAL |
|---|---|---|---|---|---|
| reasoning_multihop | 283 | 6 | 5 | 3 | **297** (52%) |
| UNCLASSIFIED | 35 | 17 | 12 | 1 | **65** (11%) |
| cognitive_capacity | 32 | 8 | 13 | 2 | **55** |
| retrieval | 21 | 9 | 7 | 1 | **38** |
| architecture | 22 | 5 | 5 | 1 | **33** |
| substrate_integrity | 10 | 8 | 9 | 0 | **27** |
| refuse_gate | 17 | 5 | 3 | 0 | **25** |
| NLP_language | 7 | 8 | 4 | 0 | **19** |
| math | 4 | 2 | 2 | 0 | **8** |
| audit_methodology | 1 | 1 | 2 | 0 | **4** |
| ingest_pipeline | 1 | 0 | 0 | 1 | **2** |
| dynamics | 0 | 0 | 1 | 0 | **1** |

### Operations × N (substrate dimensionality)
| primary_domain | N=512 | 1024 | 2048 | 4096 | 8192 | 16384 | 32768 | 65536 | 131072 | NO_N |
|---|---|---|---|---|---|---|---|---|---|---|
| reasoning_multihop | 0 | 0 | 2 | 36 | 91 | **147** | 0 | 0 | 0 | 21 |
| UNCLASSIFIED | 2 | 0 | 1 | 7 | 8 | 9 | 7 | 0 | 0 | 31 |
| cognitive_capacity | 0 | 0 | 2 | 12 | 4 | 1 | 0 | 0 | 0 | 36 |
| retrieval | 0 | 0 | 0 | 1 | 4 | 3 | 2 | 0 | 0 | 28 |
| architecture | 1 | 0 | 0 | 5 | 4 | 1 | 0 | 1 | 1 | 20 |
| substrate_integrity | 0 | 0 | 0 | 6 | 4 | 7 | 2 | 0 | 0 | 8 |
| refuse_gate | 0 | 0 | 0 | 0 | 13 | 8 | 1 | 0 | 0 | 3 |
| NLP_language | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 18 |
| math | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| audit_methodology | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 1 |

## Substantive gaps identified (Phase 0c probe candidates)

### Gap 1: LOW-N regime (N≤2048) — almost no coverage outside math
- Only 9 cert atoms across ALL domains at N≤2048 (math 3 + cognitive_capacity 2 + reasoning_multihop 2 + architecture 1 + UNCLASSIFIED 1)
- **Probe:** does substrate operate at small N? At what N does capacity break? Composes the capacity-cliff finding (alpha_c boundary at N).
- **Cell candidate:** refuse_gate AND retrieval AND multihop all at N=512, N=1024 (test whether refuse/retrieval/composition mechanisms scale-down)

### Gap 2: HIGH-N regime (N≥65536) — only architecture has 2 atoms
- Phase 3 deployment likely uses N=65536+; we have ~0 cert evidence at this regime
- **Probe candidate:** capacity-stress + composition + retrieval at N=131072 (the substrate's Phase-3 production scale)

### Gap 3: refuse_gate at small N — ZERO cert atoms at N<8192
- refuse_gate is heavily concentrated at N=8192/16384; ZERO at N=4096 or smaller
- **Probe:** refuse mechanism stability across N (does refuse-gate AUROC hold at small N?)

### Gap 4: dynamics — 1 cert atom total (the pp49_hrc deeper_d singleton)
- Severely under-covered; what dynamics phenomena are we missing?
- **Probe candidate:** identify what "dynamics" capability the substrate has + characterize via discriminating-regime pull-ups (composes inst-242 value-mining)

### Gap 5: UNCLASSIFIED 65 atoms (11% of cert corpus)
- 35 PASS + 17 MIDDLE + 12 HARD_FAIL across the unclassified-65
- These are the LIKELY value-mining hidden tier per inst-242 (no primary_domain assignment)
- **Action:** systematic primary_domain back-fill (research-side; composes the existing inst-242 cycle)

### Gap 6: reasoning_multihop PASS-heaviness suspicious
- 283 PASS out of 297 = 95% PASS (vs ~78% PASS substrate-wide)
- Likely dominated by q_b1 chain_depth variations (many depths PASS, narrow cliff)
- **Action:** sub-classify reasoning_multihop by sub-capability (q_b1 cliff bisect vs depth_chain vs pp49_hrc vs composition vs multihop-attribution) to see if the PASS-heaviness is a single capability dominating

## What Phase 0a SCOPE should lock (per Skunkworks's "load-bearing tension-cells")

**Operations (5):** storage_capacity / multihop_composition / refuse_gate / retrieval / KG. The enumerator's primary_domain split confirms these are real load-bearing operations (each has cert evidence; each has identifiable gaps).

**Condition axes (6):**
1. **N (dimensionality)**: 512 / 1024 / 2048 / 4096 / 8192 / 16384 / 32768 / 65536 / 131072
2. **sparse_alpha**: dense (0.033) / sparse (0.05, 0.10, 0.20)
3. **readout_type**: linear / sparse / entmax / softmax
4. **encoding**: real / FHRR (complex) / binary / PCA-whitened
5. **composition_op**: standard_bind / cleanup-between-hops (the just-confirmed q_b1 candidate-2 mechanism!) / tropical (separate cert event)
6. **cleanup_iters**: 0 / 1 / multi-iter (resonator)

**Phase 0c PROBE-CELL nominations (load-bearing gaps; bounded; cert-by-construction per C0):**
1. refuse_gate AT N≤4096 (Gap 3): probe whether refuse mechanism scales-down; pre-reg: "refuse-gate AUROC ≥ 0.75 holds at N=4096" (HARD_PASS) / [0.6, 0.75] (MIDDLE) / <0.6 (HARD_FAIL).
2. capacity-stress AT N=131072 (Gap 2): probe Phase-3 production scale; pre-reg per the existing capacity_battery pattern but at N=131072.
3. q_b1 cliff cross-N bisection (resolves Drill #5 C4 hypothesis): iso-protocol bisection at N=8192 AND N=32768; pre-reg the cliff-depth-vs-N scaling law (or absence thereof).
4. dynamics characterization (Gap 4): identify the substrate's dynamics capabilities + probe via discriminating-regime template.

## What Phase 0d operating-triangle needs

Per Skunkworks's glass-box-LLM ask: storage × multihop × refuse SIMULTANEOUSLY. From coverage:
- storage_capacity at N=8192 (1 atom) + N=16384 (1 atom) — UNDER-COVERED
- multihop at N=16384: 147 cert atoms (heavy coverage; q_b1 cliff localized)
- refuse_gate at N=16384: 8 cert atoms

**Operating triangle PROBE candidate:** simultaneous storage + multihop + refuse at N=16384 (where all three have some coverage); locate the cell where all three are simultaneously in PASS regime + record the operating-point.

## Tier (per C1)
- This artifact = **RESEARCH_FINDING tier** (Phase 0b in-sample coverage characterization; gap identification; probe-cell nominations)
- Phase 0c probes turn each gap into a cert-by-construction probe; each probe atom is cert-grade evidence for or against the gap-closing hypothesis
- Phase 0d synthesizes the operating-triangle from 0c probe results

## Standing
- Skunkworks: cert-VET this coverage matrix v1 against C1 (RESEARCH_FINDING tier; characterization not causal); flag any cells/gaps you'd refine; the Phase 0c probe candidates are NOMINATIONS — your SCHEMA-VET when we pick which to dispatch
- USER: Phase 0a SCOPE is ready to lock — 5 ops × 6 axes; Phase 0c probe-cell nominations above. Ratify or redirect.
- Me: ready to scope individual Phase 0c probes when prioritized

-- Research (Director)
