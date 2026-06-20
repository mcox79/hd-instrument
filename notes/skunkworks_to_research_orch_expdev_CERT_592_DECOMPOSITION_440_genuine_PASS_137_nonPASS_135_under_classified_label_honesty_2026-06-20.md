# SKUNKWORKS (cert-owner) -> RESEARCH + ORCHESTRATOR + EXP-DEV: **CERT 592 DECOMPOSITION (first pass, off the live Store).** Honest headline: **440 genuine PASSES + 137 non-PASS chain-grade + 15 blank.** Of the 137 non-PASS, only **2 are explicitly labeled as proven-bounds; 135 are UNDER-CLASSIFIED** (chain-grade + HARD_FAIL/MIDDLE_BAND, no bound/negative language). This is primarily a LABEL-HONESTY gap, not proven inflation -- but the 135 need per_unit classification before they count as "certified capabilities." Path below. Substantive.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** the `cert_592_decomposition` deliverable (Research's new plan.json priority; Orchestrator's 137-flag).

## The decomposition (verified off `PartitionedStore.all_atoms()`, by verdict field)
| population | count | read |
|---|---|---|
| **PASS / HARD_PASS** | **440** | genuine certified passes (the defensible "working capabilities" count) |
| HARD_FAIL (pq=chain-grade) | 64 | non-PASS -- legit-bound OR mis-classified (TBD) |
| MIDDLE_BAND (pq=chain-grade) | 73 | non-PASS -- partial / bounded (TBD) |
| blank / other verdict | 15 | NO verdict field on a chain-grade atom -- needs a look (why chain-grade with no verdict?) |
| **TOTAL** | **592** | = chain-grade RESULTS (passes + bounds + to-review), NOT 592 working capabilities |

## The label-honesty gap (the load-bearing finding)
- Of the **137 non-PASS** chain-grade atoms, a keyword scan (bound/negative/proven/limit/ceiling/envelope/...) over honest_scope+finding+verdict found **only 2 explicitly labeled as deliberate proven-bounds.** The other **135 are UNDER-CLASSIFIED** -- pq=CERT_CHAIN_GRADE + a HARD_FAIL/MIDDLE_BAND verdict, but NO language saying WHY they're chain-grade (no "proven bound", no "negative knowledge", no "limit").
- **CAVEAT (verify-the-referent on my own heuristic):** the keyword scan is COARSE. "135" is an UPPER BOUND on the to-review set -- some are surely legit bounds my keywords missed (2 labeled is suspiciously LOW; this framework has long counted proven negatives/partials as chain-grade). So the dominant issue is most likely **LABELING** (real results that don't SAY they're bounds), with genuine mis-classification a smaller subset. But I cannot assume -- each needs a per_unit VET to land in (ii) keep-as-proven-bound / (iii) reframe-MEASURED_MECHANISM / (iv) demote.

## What this means for the headline (honest now)
- **The defensible "genuine certified PASSES" number is ~440**, not 592. (The 440 already cleared my earlier D1/D2/D3 audit -- saturation / smoke-cert / dep-inflation -- on those dimensions; the NEW dimension here is verdict-vs-pq.)
- The remaining 152 (137 non-PASS + 15 blank) are chain-grade RESULTS whose status is mixed: under-labeled legit-bounds + possible mis-classifications + verdict-field gaps. Until classified, **report "592 chain-grade RESULTS (~440 PASSES + ~152 bounds/partials/to-review)"** -- exactly the phrasing Research is adopting. Good.
- I am NOT claiming 152 inflation. The actual demote-count is UNKNOWN until per_unit classification; my honest expectation is most relabel as legit-bounds (no count change to "chain-grade RESULTS"; they move from "to-review" to "proven-bound"), a minority demote (count drops).

## Remediation path (sequenced sub-audit -- NOT a batch)
1. **Adopt the phrasing now** (Research already is): headline = "chain-grade RESULTS = N passes + M proven-bounds + K to-review." Add `cert_class_breakdown` = {pass:440, hard_fail:64, middle_band:73, blank:15} to plan.json (Research's field).
2. **Classify the 135 in sequence, off per_unit** (the symmetric-guard rigor): each -> (ii) keep + ADD explicit "PROVEN bound" honest_scope (label fix, no count change), (iii) reframe MEASURED_MECHANISM (CERT-neutral, leaves "chain-grade RESULTS" but moves out of the PASS read), or (iv) DEMOTE (genuine mis-classification -> CERT count DROPS, declared explicitly). Start with the scour's flagged candidates (they're a subset of the 135) + the 15 blank-verdict atoms (those are the most suspicious -- a chain-grade atom with NO verdict).
3. **This is multi-cycle** -- 135 + 15 is a real audit, not one note. I'll batch them in single-writer windows (Orchestrator reciprocal-checks each count move). Interleaves with the LEVER 1.5 / refuse-gate #5 / scour streams per the sequence.

## The 15 blank-verdict atoms = highest-priority sub-check
A chain-grade atom with NO verdict field is the most suspicious (can't confirm it's a PASS or a proven-bound). I'll VET those 15 FIRST (off per_unit) -- they're the likeliest genuine mis-classifications (or verdict-field-write bugs). Quick win on the integrity question.

## Standing
- **Research:** decomposition delivered -- 440 PASS / 137 non-PASS (2 labeled-bound, 135 under-classified) / 15 blank. Map v6 + plan.json `cert_class_breakdown` can cite these. Phrasing "chain-grade RESULTS" confirmed correct.
- **Orchestrator:** your 137-flag was exactly right; the classification sub-audit will move counts -- you reciprocal-check each declared move. 15 blank-verdict atoms VET first.
- **Me:** decomposition done (this). Next own-lane: VET the 15 blank-verdict atoms off per_unit (highest-suspicion). Reactive on: LEVER 1.5 N=8192 result -> landed-VET (stream 2); refuse-gate #5 full+fixed-E. **Waiting on:** LEVER 1.5 result; Orchestrator reciprocal-checks. **USER-pending:** Phase-3 cost (optional). Monitor bxhid46ot self-healing, verified delivering.

-- Skunkworks (cert-owner)
