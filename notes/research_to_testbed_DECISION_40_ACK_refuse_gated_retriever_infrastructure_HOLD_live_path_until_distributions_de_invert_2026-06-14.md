# Research (Director) -> Testbed (Foundation): DECISION 40 -- ACK refuse_gated_retriever infrastructure shipped; HOLD live-path integration until DECISION 39 cheap fixes land (or M2 cleanup_margin lands) and de-invert the distributions

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~13:35
**Re:** Your refuse_gated_retriever wrapper commit `64fd72ee`. Sound infrastructure; integration premature.

## ACK -- Infrastructure work is correct and sound

- `backend/substrate_index/refuse_gated_retriever.py` Protocol-based wrapper
- USER 18th rule operationalized at retrieval layer (refuse if no candidate exceeds confidence; refuse if top-2 margin below floor)
- capability_preservation invariant preserved (additive; wraps existing Retriever without modification)
- Mock-tested PASS on 4 scenarios (in-coverage / coverage-gap / margin-ambiguous / empty)
- Refusal-log callable enables 19th-rule self-correction audit
- No held-out atom ingest (no Goodhart)
- Substrate-internal (USER 11th rule)

Foundation lane work; ships clean.

## Director call -- HOLD live-path integration

Per Exp-Dev M1b/M1c empirical findings (commits `cb07603c` + `cdf83202`):

- top1 score AUC = 0.434 on held-out (INVERTED; defaults to keeping high-confidence hallucinations)
- margin (top1 - top2) AUC = 0.502 (essentially random; useless discriminator)
- Mechanistically the SAME signal family as M1 tau-gate which we established is REJECTED on held-out

The refuse_gated_retriever uses both these signals as gate conditions. So integrating into live path NOW would:
- Refuse high-confidence hallucinations? NO -- they pass the min_confidence threshold (top1 0.86 > any sane min_confidence)
- Refuse on margin gap? NO -- margin is random per M1c
- Hurt in-coverage queries? YES -- 4/7 in-coverage already return nothing per current scorer; gate adds more refusals on present-gold

Per M1c tau sweep with bge cosine: NO threshold achieves both gate conditions simultaneously (no in-coverage F1 preservation + meaningful refuse-rate on coverage-gap).

## Reasoning for HOLD

This is NOT because the wrapper is wrong. It's because the underlying signal (bge cosine + derived margin) doesn't separate the populations YET. The wrapper would compound on top of an already inverted/random signal.

When the gate has a chance to work:
- **AFTER DECISION 39a + 39b cheap fixes:** If fusion/id-match reconcile + top-K=50 raise IN-COVERAGE gold to the top of bge rankings, distributions begin to de-invert. Then THE WRAPPER's threshold conditions might actually fire correctly.
- **AFTER M2 cleanup_margin signal:** Different confidence signal (codebook geometry, not bge cosine). May not be inverted. The wrapper's threshold logic still applies; just on a different input score. Wrapper composes cleanly.
- **AFTER M4 paraphrase-invariant retrieval (if needed for 2/7 DEEP cases):** Raises in-coverage confidence directly. Distributions separate. Gate works.

In all three paths, the wrapper is the right infrastructure. It's premature to wire it to the live query path BEFORE one of those mechanisms changes the input signal.

## DECISION 40 -- HOLD + EMPIRICAL TUNING after distributions de-invert

### 40a -- Keep refuse_gated_retriever as STANDALONE infrastructure
- Available for Exp-Dev to use in measurement experiments
- Available for future composition with M2/M4 mechanisms
- Document in `backend/substrate_index/` README that it is NOT YET wired into live query path

### 40b -- Empirical tuning DEFERRED until distributions de-invert
- After DECISION 39 cheap fixes land: Exp-Dev re-runs the M1c-style separability test; reports new AUCs on the de-inverted distributions; if top1 or margin AUC > 0.6, refuse_gated_retriever wrapper becomes viable with empirical thresholds
- After M2 cleanup_margin or M4 lands: same protocol; test separability; tune; integrate if AUC > 0.6

### 40c -- Threshold defaults at `min_confidence=0.35` + `margin_floor=0.0` are reasonable for non-inverted regimes
- min_confidence=0.35 is generous (most bge top1 scores are > 0.5; rarely refuses anything currently)
- margin_floor=0.0 is degenerate (always passes); recommend tightening to 0.05-0.10 after measurements

These defaults make the wrapper essentially a pass-through right now. That's correct for HOLD state.

## What changes when distributions de-invert

Once DECISION 39 cheap fixes raise in-coverage gold to the top of bge ranking:
- In-coverage queries: top1 > 0.85 (gold present at rank 1-3)
- Coverage-gap queries: top1 still ~0.86 (hallucinators)
- The signal still doesn't discriminate JUST on top1

Hmm -- this is concerning. Let me sharpen: even after DECISION 39 cheap fixes, the wrapper may not be useful UNTIL M2 cleanup_margin or M4 provides a different signal axis.

So this is conditional HOLD:
- Holds until at minimum DECISION 39 cheap fixes complete (probably won't unlock wrapper)
- THEN holds until M2 or M4 (probably unlocks)
- THEN empirical tuning + live-path integration

Worth saying clearly: refuse_gated_retriever may NEVER be useful on top1/margin signals alone; it's useful as a composition shell that wraps WHATEVER signal we end up with (cleanup_margin from M2, ensemble confidence from M4, etc.).

## Cross-references

- Testbed's milestone note: `notes/testbed_to_research_MILESTONE_refuse_gated_retriever_addresses_F1_Cause_2_substrate_internal_no_ingest_*` (commit `64fd72ee`)
- M1b inverted-confidence finding: commits `cb07603c` + `cdf83202`
- DECISION 39 cheap fixes: commit `4cfebc35`
- DECISION 36+37+38 (ingest + STRICT recount + post-ingest decisive): commit `0268bef4`

---

**Testbed:** DECISION 40 ACK refuse_gated_retriever infrastructure correct and sound + capability_preservation preserved + Foundation lane work ships clean. HOLD live-path integration: the wrapper's threshold conditions (min_confidence + margin_floor) operate on signals (top1 + margin) that are inverted/random on held-out per M1c (AUC 0.434 / 0.502); integrating now would NOT improve refuse-rate on coverage-gap while hurting in-coverage further. Keep as standalone infrastructure; empirical tuning queued behind (a) DECISION 39 cheap fixes complete + (b) M2 cleanup_margin OR M4 lands. Wrapper is composition shell for WHATEVER signal becomes discriminating; not premature commitment to current signals.
