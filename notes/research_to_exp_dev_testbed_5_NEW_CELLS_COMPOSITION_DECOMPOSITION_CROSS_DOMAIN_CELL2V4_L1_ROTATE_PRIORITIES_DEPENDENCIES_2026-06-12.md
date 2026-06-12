# Research -> Exp-Dev + Testbed: 5 new relational-analysis cells approved by USER (all of them) + priorities + dependencies + pre-regs + NO PP-### pre-allocation (verdict_handler allocates per discipline)

**From:** Research  **Date:** 2026-06-12 (Day 4 Cycle 49 close)
**Re:** USER approval "all of them" + research drills where they help

## TL;DR

- USER approved all 5 relational-analysis cells; immediate-launch 3 (standalone) + Phase-2-light-gated 2
- Composition benchmark + Decomposition benchmark + Cross-domain transfer: ship immediate parallel
- Cell 2 v4 cross-discipline analogy + L1 RotatE prototype: gate on Phase-2-light substrate-guided proposal tool surfacing relation gaps
- 2 research drills in flight: VSA composition + decomposition methodology + asymmetric retrieval leg degradation
- NO PP-### pre-allocation in this routing per meta::RULE_authoring_substrate_queries_first 4th-appearance discipline; verdict_handler allocates when verdicts land

## Cell priorities + dependencies + pre-regs

### Cell A -- Composition benchmark (standalone immediate)

- Given atoms A + B + role R from existing 280-atom algebra-encoded corpus
- Compute A_bound = A + R*B (HRR Hadamard binding)
- Validate via unbinding: A_bound * R_inverse should approx= B
- Measure cosine recovery + capacity vs N_bindings (1, 2, 5, 10, 20 simultaneous bindings)
- Demonstrates substrate > atom-set (atoms compose into structured representations)
- Pre-reg HARD-PASS: cosine recovery >= 0.8 at N_bindings=5 + capacity boundary identified
- Pre-reg MIDDLE: cosine recovery 0.5-0.8 at N_bindings=5
- Pre-reg HARD-FAIL: cosine recovery < 0.5 at N_bindings=5 = capacity collapsed at small N
- Cost: ~2-3 hr CPU + light-GPU
- Owner: Exp-Dev (standalone primitive cell)
- Awaits: VSA composition+decomposition methodology drill return (in flight) before final pre-reg locks

### Cell B -- Decomposition benchmark (standalone immediate)

- Given a bound state X = A + R1*B + R2*C + R3*D
- Extract A / B / C / D via Resonator decoder + cleanup codebook over 280-atom corpus
- Measure precision@k (k=1, 3, 5) as function of:
  - Cleanup codebook size (10, 50, 100, 280 atoms in codebook)
  - Number of bindings (2, 4, 8)
  - Additive noise level (0, 0.1, 0.3, 0.5)
- Demonstrates substrate decodes bound state -- substrate-product positioning
- Pre-reg HARD-PASS: precision@1 >= 0.8 at codebook=100 / N_bindings=4 / noise=0.1
- Pre-reg MIDDLE: precision@1 0.5-0.8 at same params
- Pre-reg HARD-FAIL: precision@1 < 0.5 = Resonator decoder doesn't generalize at scale
- Cost: ~3-4 hr CPU
- Owner: Exp-Dev (Resonator decoder validation cell)
- Awaits: VSA drill return for cleanup-codebook-size scaling laws

### Cell C -- Cross-domain transfer (standalone immediate)

- Train discriminative_perceptron primitive on math domain (substrate has 11+ caps already serving discriminative_perceptron per solution_history rule 1 universal lever)
- Transfer to bio domain (e.g. gene-name NER OR ProtBERT-style classification tasks)
- Measure transfer F1 vs train-from-scratch baseline at 1pct + 5pct + 10pct + 100pct of bio training data
- Substrate-product positioning: discriminative-weighting universal lever transfers across domains
- Pre-reg HARD-PASS: transfer F1 / scratch F1 >= 1.20 at 5pct (positive transfer)
- Pre-reg MIDDLE: ratio 0.95-1.20 (neutral/weak positive transfer)
- Pre-reg HARD-FAIL: ratio < 0.95 (negative transfer)
- Cost: ~3-5 hr CPU
- Owner: Exp-Dev (substrate-classical transfer cell)

### Cell D -- Cell 2 v4 cross-discipline analogy at scale (Phase-2-light gated)

- After Phase-2-light substrate-guided proposal tool surfaces structural-analogy relation gaps + Testbed authors more DUAL/SPECIALIZES/GENERALIZES/INSTANCE_OF relations (target >= 30 labeled pairs per relation type)
- Given (A,B,A') analogy probes, predict B' via HRR offset + cleanup
- Test cross-discipline (math primitive -> bio analog; physics -> CS; etc.)
- Pre-reg deferred until Phase-2-light + relation breadth ships
- Owner: Exp-Dev post Phase-2-light
- Dependency: Phase-2-light tool surfaces relation gaps + Testbed authors batch

### Cell E -- L1 RotatE prototype (Phase-2-light gated for relation breadth)

- Train RotatE on substrate's existing INSTANCE_OF / SPECIALIZES / DUAL / GENERALIZES relations
- Currently too thin (DUAL=4, SPECIALIZES=7, GEN=5, INSTANCE_OF=21, PRESERVES=2 per Exp-Dev's C-D4 audit)
- After Phase-2-light tool surfaces relation gaps + Testbed authors more, RotatE has enough train data
- Measure relation-completion F1; compare to algebra-HRR baseline; L1 production-tier relational layer
- Pre-reg HARD-PASS: RotatE relation-completion F1 >= +0.05 over algebra-HRR baseline
- Owner: Testbed (Stratified Hybrid L1 production layer)
- Dependency: Phase-2-light + relation breadth authoring batch

## Research drills informing cells

In flight:
- **VSA composition + decomposition benchmark methodology 2x DEEP** -- informs Cell A + Cell B pre-reg thresholds + cleanup-codebook scaling laws (commit deferred to drill subagent)
- **Asymmetric retrieval leg degradation methodology 2x DEEP** -- informs measurement protocol for testing rule 12's NOVEL prediction (asymmetric bge-vs-algebra degradation as corpus grows)

Skipped (literature mature, drill wouldn't change design):
- Cross-domain transfer methodology: domain adaptation literature mature; Cell C design adequate from existing literature
- L1 RotatE methodology: FB15k-237 / WN18RR / YAGO3-10 benchmarks standardized; Cell E design adequate from RotatE paper

## Substrate-product positioning for these 5 cells together

Cells A + B + C + D + E test the FULL relational analysis stack:
- **Composition (A)**: substrate builds structured representations from atoms
- **Decomposition (B)**: substrate decodes structured representations back to atoms
- **Cross-domain transfer (C)**: substrate primitives generalize across discipline
- **Cross-discipline analogy (D)**: substrate analogies cross domain via HRR offset
- **L1 RotatE relational layer (E)**: production-tier relational embedding layer

Together = empirical demonstration that substrate is the FIRST EMPIRICALLY-DEMONSTRATED REAL RELATIONAL ANALYSIS engine (per substrate-product positioning). LLMs have no analog (their "relations" are emergent attention patterns; substrate's are STRUCTURED primitives).

If all 5 land HARD-PASS or MIDDLE: substrate-product positioning artifact COMPLETE (Stratified Hybrid 6-layer architecture validated bottom-up).

If 1-2 HARD-FAIL: 9th methodology rule (refine-via-empirical-FAIL) refines our model; drill informs next iteration.

## Honest scope

- Cells A + B + C ship immediate parallel (CPU + light-GPU; no Phase-2-light dependency)
- Cells D + E gated on Phase-2-light substrate-guided proposal tool surfacing relation gaps
- Pre-regs locked AFTER VSA drill returns (Cells A + B) for honest empirical alignment
- No PP-### pre-allocation per meta::RULE_authoring_substrate_queries_first
- verdict_handler allocates cap_map entries when verdicts land

## Routing

**Exp-Dev**:
- Cell A composition benchmark IMMEDIATE (CPU + light-GPU, ~2-3 hr); lock pre-reg post VSA drill
- Cell B decomposition benchmark IMMEDIATE (CPU, ~3-4 hr); lock pre-reg post VSA drill
- Cell C cross-domain transfer IMMEDIATE (CPU, ~3-5 hr); lock pre-reg from existing literature
- Cell D + E queued post Phase-2-light + relation-breadth-authoring
- L-B remaining Ablations A+B under noise continue (transition + char n-gram noise robustness)
- Cell 2 PP-394 ASDiv-WK multi-seed CPU continues

**Testbed**:
- Phase-2-light substrate-guided proposal tool BUILD SHIP-PRIORITY (gates Cells D + E + future breadth-backfill)
- After Phase-2-light ships: tool surfaces relation gaps + authors batch to enable Cells D + E
- Cell E L1 RotatE prototype Testbed-owned when relation breadth ready
- Continue Cycle 49 close: revert batch 2 ingest + L1 categorical clustering + Q35 Lyapunov + Cell 2 v3 measurement

**Research**:
- This routing
- Standing for VSA composition+decomposition drill return + asymmetric leg degradation drill return + cell verdicts (verdict_handler discipline)
- Cell A + B pre-reg lock pending VSA drill return

## Cross-references

- USER directive: "all of them. also do research drills where it can help us"
- USER question: substrate's enormous body of knowledge state; relational analysis state; new and amazing things
- Research drill VSA composition+decomposition methodology 2x DEEP (in flight)
- Research drill asymmetric retrieval leg degradation 2x DEEP (in flight)
- NER architectural ceiling 2x DEEP RETURNED: corpus is the lever for 0.20 F1 gap above architectural ceiling; CONFIRMS math+science ingestion priority
- Substrate-rule-authoring-substrate-queries-first-2026-06-12 memory (no PP-### pre-allocation)

---

**Exp-Dev + Testbed:** 5 new relational-analysis cells USER-approved + 3 immediate (Cell A composition / B decomposition / C cross-domain transfer standalone CPU+GPU 2-5 hr each parallel) + 2 Phase-2-light-gated (Cell D cross-discipline analogy + Cell E L1 RotatE prototype post relation-breadth) + 2 research drills in flight informing Cell A+B pre-regs (VSA methodology + asymmetric leg degradation) + NER architectural ceiling 2x DEEP RETURNED only +0.030-0.083 F1 architecturally recoverable beyond substrate-classical baseline 0.6441 + 0.20 F1 gap to literature ceiling 0.91 is CORPUS NOT architecture = CONFIRMS USER math+science ingestion strategic priority + substrate-product positioning Cells A+B+C+D+E together = substrate FIRST EMPIRICALLY-DEMONSTRATED REAL RELATIONAL ANALYSIS engine + NO PP-### pre-allocation per meta::RULE_authoring_substrate_queries_first 4th-appearance discipline + verdict_handler allocates cap_map when verdicts land + USER full-auto continuing.
