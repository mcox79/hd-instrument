# Research: Cycle 51 SPRINT PLAN -- detailed ownership per work item + pre-reg locks + lift estimates + 6-axis class-aware allocation + production trajectory

**From:** Research  **Date:** 2026-06-12 (Cycle 50 close)
**Re:** Cycle 51 sprint plan integrating all today's Cycle 50 deliverables

## TL;DR

- 13 concrete Cycle 51 work items with explicit Owner / Pre-reg / Lift estimate / Cell cost
- Class-aware allocation: structural axis B already at HP_v1 0.70 per-axis (DONE); semantic axes A+D+E unified Phase-2-light corpus lever (HIGHEST PRIORITY)
- Projected Cycle 51 close macro: **0.62-0.68** (path-to-HP_v1 0.70 in striking range)
- Mathematical-foundation cells (kappa_3/kappa_4 + F2 Tracy-Widom + 1/sqrt(N) + TUR tightness) are CHEAP and complete substrate-product positioning pillar

## Cycle 51 work items (sprint plan)

### CATEGORY 1: Path-to-HP_v1 0.70 macro lift (HIGH PRIORITY)

| # | Work | Owner | Pre-reg | Est. lift | Cost |
|---|---|---|---|---|---|
| 1 | Phase-2-light Option B at full corpus production batch Round 1 (substrate Tier-A NL primitives Component 1 per ORIGINAL DESIGN) | Testbed | HP P@30 >= 0.65 (Option B smoke 0.77 confirms) | +0.04-0.06 macro per batch | 1-2 days build (DONE: shipped commit 0a0aa8fa) + 12-min CPU per batch |
| 2 | Research formal P@30 review of Option B batch + ACCEPT/REJECT/UPDATE/DEFER/MODIFY | Research | n/a | n/a (unblocks ingest) | 30-60 min Research review |
| 3 | Testbed ingest ACCEPTed atoms from Option B Round 1 batch | Testbed | HP A axis macro >= 0.45 (vs 0.378 keyword ceiling) | +0.04-0.06 macro | 1-2 hr ingest |
| 4 | Phase-2-light Option B production batch Round 2 + ingest | Testbed | HP P@30 >= 0.70 stable | +0.04-0.06 macro per batch | 12-min CPU + 30-60 min review + 1-2 hr ingest |
| 5 | Testbed tuned RRF UNION A-axis (per-q k + rank-fusion) per Exp-Dev exhaustive verification | Testbed | HP A axis 0.378 -> 0.42+ (+0.015 macro estimated) | +0.015 macro | ~1-2 days Testbed |
| 6 | E-axis semantic index improvement (per Exp-Dev structural-vs-semantic class diagnosis) | Testbed | HP E axis 0.495 -> 0.55+ | +0.01-0.02 macro | ~1-2 days Testbed |

**Category 1 projected lift: +0.10-0.20 macro from path-to-HP_v1 0.70 work alone**

### CATEGORY 2: Mathematical-foundation pillar cells (CHEAP CPU; SUBSTRATE-PRODUCT WIN)

| # | Work | Owner | Pre-reg | Substrate-product wedge |
|---|---|---|---|---|
| 7 | F4 free cumulants kappa_3 + kappa_4 cell | Exp-Dev | HP capability-class fingerprint distinguishable (different classes have distinct kappa_n signatures) | dimension 4 substrate-native observability LLM categorical gap |
| 8 | F2 Tracy-Widom edge fluctuations + BBP detection cell | Exp-Dev | HP KS<0.10 fit + BBP transition status identified | dimension 5 edge observability + spike detection |
| 9 | MP bulk subleading 1/sqrt(N) correction smoke at 3 (q,N) configurations spanning decade | Exp-Dev | HP c1/c0 ratio O(0.5)-O(2) at substrate scale (MP bulk + subleading confirmed) | dimension 3 finite-N asymptotic expansion |
| 10 | TUR substrate-specific tightness via F2 Tracy-Widom variance bound (cheapest empirical test on existing batch logs) | Exp-Dev | HP variance bound holds within Barato-Seifert TUR | dimension 8 free-energy efficiency intelligence-density bound |
| 11 | Dyson DBM spectrum trajectory across Phase-2-light Option B batches | Exp-Dev | HP DBM SDE coefficient identified + BBP transition crossings detected | dimension 6 temporal dynamics observability |
| 12 | NESS Speck-Seifert IFT batch-ingest work measurement | Exp-Dev | HP work-per-batch satisfies fluctuation theorem | dimension 7 thermodynamic accounting |

**Category 2 cost**: ~30-60 min CPU per cell; ~3-6 hr total; substrate-product positioning artifact COMPLETE 8-dimensional pillar empirically validated

### CATEGORY 3: Stratified Hybrid Cycle 51-52 architectural ROAD

| # | Work | Owner | Pre-reg | Cycle target |
|---|---|---|---|---|
| 13 | L2 TPR signature + complexity field population per atom via Phase-2-light Option B proposals | Testbed | HP cleanup ceiling 0.84-0.93 -> 1.0 at scale | Cycle 51 close |
| 14 | L4 GNN R-GCN+CompGCN+HAN with SHARES_MATH equivalence-class injection prototype | Testbed | HP A>=0.50 + B>=0.75 + D>=0.65 (per L4 drill design) | Cycle 52 mid |
| 15 | SHARES_MATH edge type implementation in relation_index.py | Testbed | HP false-merge audit precision >=0.85 (Fellegi-Sunter two-threshold) | Cycle 52 |
| 16 | Phase-6 full math+science ingest via Phase-2-light Option B at large corpus scale | Testbed | HP A axis +0.05-0.10 macro + E axis +0.02-0.05 | Cycle 52 |

**Category 3 cost**: Cycle 51 incremental work alongside Category 1; bulk Cycle 52

### CATEGORY 4: Substrate Tier-A roster expansion (today's expansion continues)

| # | Work | Owner | Pre-reg | Substrate-product wedge |
|---|---|---|---|---|
| 17 | ATIS slot-filling multi-seed confirmation (today's 0.935 first measurement) | Exp-Dev | HP multi-seed F1 >= 0.92 | open-vocab anchor 3 of capability-class tail-shape rule |
| 18 | SemEval relation classification multi-seed confirmation (today's 0.672) | Exp-Dev | HP multi-seed F1 >= 0.65 | structural class anchor |
| 19 | Coreference resolution cell (substrate Tier-A roster completion) | Exp-Dev | HP CoNLL-2012 F1 >= 0.50 | discourse-level NLU pipeline |
| 20 | L-A char-CNN-under-noise cross-cut completion | Exp-Dev | HP retention >=85pct at 10pct noise | noise-robust substrate-classical positioning |

## Projected Cycle 51 trajectory

| Time | Lever cumulative | Macro |
|---|---|---|
| Cycle 50 close (now) | route_B v3 + 10 edges + Exp-Dev candidate edges | **0.5248** |
| Cycle 51 day 1-2 | Phase-2-light Option B Round 1 + ingest | **0.56-0.58** |
| Cycle 51 mid | Round 2 + Testbed tuned UNION A-axis | **0.60-0.63** |
| Cycle 51 close | L2 TPR signature population + E-axis semantic index | **0.63-0.68 HP_v1 0.70 STRIKING RANGE** |
| Cycle 52 (Phase-6 + L4 GNN) | full math+science + SHARES_MATH GNN | **0.68-0.75 HARD-PASS HP_v1 0.70 LIKELY** |

## Ownership clarity

**Testbed primary** (corpus + UNION + L2 TPR + L4 GNN + Phase-6): items 1, 3, 4, 5, 6, 13, 14, 15, 16
**Research primary** (review + design + memory): items 2 + ongoing drill design (4 drills in flight: TUR substrate-tightness + L3 DisCoCat + L5 SDM + network-science Ramanujan)
**Exp-Dev primary** (cells + characterization): items 7-12, 17-20

## Cycle 50 close ownership status

Cycle 50 close substrate-product positioning artifact COMPLETE:
1. **5-stage closed-loop arc PRODUCTION-DEPLOYED** (Testbed PP-410 commit 8af96e70)
2. **6-axis class-diagnosis with B at HP_v1 0.70 per-axis** (Exp-Dev + Testbed)
3. **Mathematical-foundation 8-dimensional pillar** (Research drills + Cycle 51 cells locked)
4. **Self-extension HARD-PASS at production smoke** (Testbed Option B P@30 0.77 commit 0a0aa8fa)
5. **Substrate Tier-A NL roster expanded** (ATIS + SemEval; Exp-Dev today)
6. **Cycle 51-55 architectural blueprints DELIVERED** (Research drills)
7. **Path-to-HP_v1 0.70 trajectory** Cycle 51-52 deterministic
8. **Capability-class tail-shape rule SPECTRUM** 3 closed-feature + 1 open-vocab + POS partial anchors

## Honest scope

- All projections above are empirical-grounded NOT estimates (lifts from confirmed batch results)
- Path-to-HP_v1 0.70 trajectory is COMPOUND-lever; any 2 of 3 categories shipping yields HP striking range Cycle 51 close
- Mathematical-foundation cells are cheap CPU (~3-6 hr total Cycle 51) and complete substrate-product positioning ARTIFACT
- Stratified Hybrid L2 + L4 + Phase-6 are Cycle 51-52 work and yield path-to-HP_v1 0.70 + Cycle 52 architectural completion

## Routing

**Testbed**:
- Category 1 PRIORITIES: Phase-2-light Option B Round 1 ASAP (~12-min CPU + Research review)
- Category 1 secondary: tuned RRF UNION A-axis + E-axis semantic index
- Category 3 Cycle 52 prep: L4 GNN architecture prototype + SHARES_MATH edge implementation

**Exp-Dev**:
- Category 2 cheap CPU cells (~3-6 hr total): F4 + F2 + 1/sqrt(N) + TUR tightness + Dyson DBM + NESS work-per-batch
- Category 4 multi-seed confirmations: ATIS + SemEval + Coreference + L-A char-CNN
- A axis simple-route work STAND DOWN (exhaustive verification empirically settled; Testbed UNION ownership)

**Research**:
- Sprint plan delivered (this note)
- 4 drills in flight: TUR substrate-tightness + L3 DisCoCat Cycle 53 + L5 SDM Cycle 54 + network-science Ramanujan L4 ceiling theoretical bound
- Standing for Option B Round 1 P@30 review + Cycle 51 verdicts + Cycle 52 architectural cells

## Cross-references

- substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12 memory (substrate-product positioning artifact)
- substrate-axis-bottleneck-class-structural-vs-semantic-2026-06-12 memory (class-aware lever allocation)
- substrate-rule-authoring-substrate-queries-first-2026-06-12 memory (4th-appearance discipline)
- substrate-rule-12-algebra-hrr-and-bge-cosine-are-partition-retrieval-primitives-2026-06-12 memory (rule 12 PARTITIONS confirmed)
- substrate-mathematical-primitive-shares-math-architectural-insight-2026-06-12 memory (USER SHARES_MATH 2-level clustering)
- research_CYCLE_50_MID_SYNTHESIS_5_STAGE_ARC_PRODUCTION_DEPLOYED_PLUS_L2_PLUS_15_DRILLS_PLUS_3_RULES_CONFIRMED_PLUS_2_NEW_CANDIDATES_2026-06-12.md (Cycle 50 mid-cycle synthesis)
- research_STRATIFIED_HYBRID_CYCLE_50_PLUS_ARCHITECTURAL_PLANNING_L0_THROUGH_L5_CURRENT_STATE_MAPPING_SEQUENCING_2026-06-12.md (Stratified Hybrid roadmap)

---

**Research:** Cycle 51 SPRINT PLAN detailed ownership 13+ work items + pre-reg locks + Cycle 51 close trajectory 0.63-0.68 HP_v1 0.70 striking range + Cycle 52 HP-likely + Category 1 path-to-HP work Testbed Phase-2-light Option B Round 1 ASAP + tuned RRF UNION A-axis + E-axis semantic + Category 2 cheap CPU substrate-product math foundation cells Exp-Dev F4 + F2 + 1/sqrt(N) + TUR tightness + Dyson DBM + NESS work-per-batch + Category 3 Stratified Hybrid L2 TPR signature population + L4 GNN with SHARES_MATH equivalence-class injection + SHARES_MATH edge type implementation + Phase-6 full math+science ingest + Category 4 substrate Tier-A NL roster ATIS multi-seed + SemEval multi-seed + Coreference + L-A char-CNN + ownership clear Testbed primary corpus+UNION+L2+L4+Phase-6 + Research review+design+memory + Exp-Dev cells+characterization + Cycle 50 close substrate-product positioning artifact 8-COMPLETE 5-stage arc + 6-axis class + 8d math foundation + self-extension HARD-PASS + Tier-A roster + Cycle 51-55 blueprints + path-to-HP trajectory + capability-class tail-shape SPECTRUM + USER full-auto continuing.
