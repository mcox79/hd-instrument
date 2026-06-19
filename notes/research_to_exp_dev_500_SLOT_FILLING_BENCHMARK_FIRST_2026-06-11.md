# Research -> Exp-Dev: 500-item NL slot-filling benchmark FIRST + revised sequence

**From:** Research  **Date:** 2026-06-11
**Re:** NL-understanding 3x DEEP drill landed; sequence revision

## NL-understanding drill key finding

**Frame-role binding is Priority-1 substrate-native NL primitive (unlocks 15 of 22 downstream tasks).** Substrate-only slot-filling at F1>=0.85 on 1-3 sentence specs: P=0.52.

Slot-filling may be MORE DIRECT than full dep-parsing for math/code use cases. Extracts entities + quantities + intent directly; doesn't require syntactic tree.

## Revised sequence (slot-filling FIRST)

Run 500-item slot-filling benchmark BEFORE the multi-day dep-parser build:

### 500-item NL slot-filling benchmark (3-4 hr CPU)

**Anchor:** `nl_slot_filling_500_cpu_v1`

**Setup:**
- 500 items: ~167 math word-problems + ~167 code docstrings + ~167 customer-support queries
- Each item: 1-3 sentence NL spec
- Ground truth slots: SUBJECT, OBJECT, QUANTITY, CONSTRAINT (entity slots) + INTENT (COMPUTE/RETRIEVE/TRANSFORM/FILTER) + solvability flag

**Substrate-only architecture:**
- PP-364 POS tagger (validated) for tokenization + atomic labeling
- Frame-role binding via substrate v3.1 context-binding (PP-346 mechanism extended)
- Tier-2 schemas for slot inventory (await Drill A return for inventory design)
- Substrate composition + cleanup for slot-filling

**Comparison baselines:**
- BASELINE-1: regex + keyword matcher (rule-based upper bound)
- BASELINE-2: GPT-4o 5-shot or small LLM equivalent (practical ceiling reference)

**HARD-PASS gates:**
- F1 (entity slots) >= 0.85
- F1 (intent) >= 0.80
- Solvability accuracy >= 0.90

**HARD-FAIL gates:**
- F1 (entity slots) < 0.50

**Per drill-defeatism rule:** NO pre-registered defeat thresholds. Report empirical results; we decide path forward.

## Decision tree per slot-filling outcome

| Slot-filling result | Path forward |
|---|---|
| **F1 >= 0.85 PASS** | Skip dep-parser build; slot-filling is the right primitive; proceed to Phase 2 (Tier-2 schemas) + Phase 3 (multi-step reasoning bridge) + Phase 4 (MATH+CODEGEN integration). 2-3 days instead of 4-6 days. |
| **F1 0.65-0.85 MIDDLE** | Hybrid: slot-filling base + dep-parser enrichment. Build smaller dep-parser focused on slot-completion. |
| **F1 < 0.65 HARD_FAIL** | Slot-filling alone insufficient; full dep-parser Phase 1 build justified per original Option 1 routing. |

## Two pre-build drills DISPATCHED

While the 500-item benchmark + dep-parser run on laptop CPU:

- **Drill A: Tier-2 problem-schema inventory** (math + code + customer support; ~10 min return)
- **Drill B: Multi-step reasoning composition routing** (PP-343 + PP-348 + PP-360 + PP-307 + DPEFE; ~10 min return)

Both inform Phase 2 + Phase 3 builds empirically before they start.

## Updated build sequence

1. Run 500-item slot-filling benchmark (3-4 hr)
2. While running: Drills A + B return; design Phase 2 + Phase 3 specifics
3. Branch per slot-filling result (above)
4. Phase 2 build (informed by Drill A)
5. Phase 3 build (informed by Drill B)
6. Phase 4 MATH + CODEGEN integration

Plus parallel cheap tests already routed:
- LANG-MATH-COEXIST (15 min)
- CREATIVE-DREAMING-SMOKE (30 min)
- SLIPNET-PHASE0-WN18RR (~2 hr)

## Cross-references
- NL-understanding 3x DEEP drill: notes/research_drill_nl_understanding_universal_unlock_3x_2026-06-11.md
- Option 1 routing: notes/research_to_exp_dev_OPTION_1_SUBSTRATE_ONLY_DEEPER_PATHS_2026-06-11.md
- Dep-parse build authorization: notes/research_to_exp_dev_DEPPARSE_BUILD_PLUS_3_CHEAP_SPECS_2026-06-11.md
- Drill-defeatism feedback: memory feedback_dont_parrot_drill_defeatism_2026-06-11

---

**Exp-Dev:** Sequence revision -- run 500-item NL slot-filling benchmark FIRST (3-4 hr CPU); slot-filling may skip dep-parser entirely if F1>=0.85. Pre-build drills A + B dispatched (Tier-2 schemas + reasoning routing). Phase 2-3 specifics informed empirically before build.
