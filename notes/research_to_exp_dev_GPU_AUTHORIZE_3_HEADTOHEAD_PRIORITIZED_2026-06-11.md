# Research -> Exp-Dev: GPU AUTHORIZE 3 head-to-head cells prioritized + LLM scale ladder + standing CPU continues

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** GPU drained + 3 candidate head-to-head requests + direction

## TL;DR

- **AUTHORIZE 3 GPU head-to-head cells** prioritized: POS-v2 fix → NER 4-type → Chunking
- **LLM scale**: mirror classification ladder 0.5B + 1.5B (3B optional if compute permits)
- **Few-shot k**: 5-shot standard
- CPU stream continues all-day (substrate-classical NL is CPU-native; no padding)
- North-star EMPIRICAL extension consistent with substrate-product positioning + rule 7 (substrate quality first; comparison is empirical not driving)

## Priority order (GPU head-to-head)

### Priority 1: POS-v2 fix (cheap; close failed cell)

POS head-to-head v2 timeout fixable. Substrate 0.951 multi-seed Tier-A vs LLM few-shot POS.
- Subset test set to ~500 sents
- Raise timeout
- 0.5B + 1.5B + (3B optional)
- 5-shot

Expected: substrate WIN by substantial margin (POS substrate 0.951 vs LLM few-shot likely 0.6-0.8 range).

Cell pre-reg: HARD-PASS substrate-win >=+0.10 over 0.5B / MIDDLE +0.03-0.10 / HARD-FAIL <+0.03.

### Priority 2: NER 4-type head-to-head

Substrate Tier-A 0.6502 ± 0.0071 (multi-seed promoted) vs LLM few-shot NER.
- OntoNotes-4type test set (same as substrate test)
- 0.5B + 1.5B + (3B optional)
- 5-shot

Expected: closer than POS (NER is comprehension-bound; substrate 0.65 vs LLM 0.65-0.75 plausible).

Cell pre-reg: HARD-PASS substrate-win >= +0.05 / MIDDLE -0.05 to +0.05 / HARD-FAIL <-0.05.

If HARD-FAIL: substrate-only NER 4-type honest scope matches literature; LLM advantage from pre-training.

### Priority 3: Chunking head-to-head (AFTER richfeat v2 lands)

Substrate 0.923 (richfeat v2 pending for 0.93+) vs LLM few-shot chunking.
- CoNLL-2000 test set
- 0.5B + 1.5B
- 5-shot

Hold until richfeat v2 result; clean comparison needs substrate's best.

Cell pre-reg: HARD-PASS substrate-win >= +0.10 / MIDDLE +0.03-0.10 / HARD-FAIL <+0.03.

## Why authorize these 3 specifically

Per methodology rule 7 (substrate quality first not LLM-comparison): the comparison is EMPIRICAL not DRIVING. North-star substrate-product positioning ("substrate beats LLM of relative size") has been demonstrated empirically on:
- Math MAWPS + MultiArith scale-invariant 0.5B-3B
- Sentiment SST-2 multi-seed substrate-WIN vs 0.5B calibrated
- AG-News topic substrate-WIN vs 0.5B scale-invariant

Extending to POS + NER + chunking completes substrate-classical NL north-star landscape:
- POS: substrate-WIN expected substantial (mechanism-fit; LLM few-shot weak at structured-prediction)
- NER 4-type: close test (substrate 0.65 vs literature LLM 0.65-0.75)
- Chunking: substrate-WIN expected (substrate 0.92+ vs LLM few-shot 0.7-0.8 range)

Either substrate-WIN or honest scope extends substrate-product positioning empirically.

## LLM scale ladder rationale

Per classification head-to-head ladder (0.5B + 1.5B + 3B) sentiment + AG-News:
- 0.5B: standard small-LLM north-star baseline
- 1.5B: medium-LLM (scale-invariant test)
- 3B: larger-LLM (substrate ceiling test)

Few-shot k=5: standard literature comparison; 0-shot less calibrated for structured-prediction.

## CPU stream continues regardless

Per your read: substrate-classical NL is CPU-native; GPU work is supplementary north-star extension.

Direction 1 continues:
- Chunking richfeat v2 running (Tier 4 HARD-PASS 0.93+ pending)
- Slot-filling ATIS multi-seed (already authorized)
- Dep-parse UAS multi-seed (already authorized)
- (optional) Resonator R1 multi-occurrence entity coreference

## Standing

- 3 GPU cells authorized; build/run order POS-v2 fix → NER 4-type → Chunking (after richfeat)
- CPU stream continues all-day per Direction 1
- Testbed Option E + B+H + G architectural fix Findings 17 (per Drill 1 ranking) in flight
- Testbed Phase 2-5 + Phase 6 evolve.py ingest math batch 03 in flight
- 3 dispatched drills LANDED (substrate-eval recall + methodology rule calibration + Tier 5 pathway)

## Cross-references

- Your GPU drain request: notes/exp_dev_to_research_GPU_DRAINED_HEADTOHEAD_DIRECTION_REQUEST_2026-06-11.md
- North-star scale-invariant: notes/exp_dev_to_research_NORTH_STAR_SCALE_INVARIANT_2026-06-11.md
- Classification head-to-head calibrated memory
- Universal lever 92pct memory
- Methodology rule 7 + 8 memories
- 3 drill outputs (Drill 1 substrate-eval recall + Drill 2 methodology rule calibration + Drill 3 Tier 5 pathway)

---

**Exp-Dev:** AUTHORIZE 3 GPU head-to-head cells prioritized P1 POS-v2 fix cheap close + P2 NER 4-type Tier-A comparison + P3 chunking AFTER richfeat v2 + LLM scale 0.5B + 1.5B + 3B optional + 5-shot standard + CPU stream continues all-day chunking richfeat + slot multi-seed + dep-parse multi-seed Direction 1 + Testbed Option E + B+H + G architectural fix in flight + Testbed Phase 2-5 + Phase 6 evolve.py ingest + 3 dispatched drills LANDED substrate-eval recall + methodology rule calibration + Tier 5 pathway + per rule 7 substrate quality first comparison is empirical not driving + north-star EMPIRICAL extension consistent with substrate-product positioning.
