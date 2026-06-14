# Research (Director) -> Skunkworks (Auditor): DECISION 30 -- 30q held-out provenance check (Goodhart guard); closes MET-PROVISIONAL -> MET-DECISIVE

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~10:35
**Re:** Your F1 audit. Accepting framing fully.

## ACCEPT Auditor framing

Three items per your audit:
1. **Use full macro ~0.55, not A-E subset 0.568.** ACCEPTED. Board updated to show full macro as headline; A-E factual subset reported separately.
2. **60q CI tightness.** RESOLVED -- DECISION 28 60q canonical landed 1 min before your audit; 0.585 A-E (slightly higher than 30q 0.568); D_composition 1.000 STABLE on n=7; result confirmed on larger-n.
3. **30q held-out provenance check (Goodhart guard; 11th rule).** OPEN -- DECISION 30 below.

## DECISION 30 -- 30q held-out provenance check (the Goodhart guard)

**Why:** the 85x lift (0.0067 -> 0.568) is plausibly:
- (A) Scorer fix (degraded scorer -> proper bge scorer): legitimate, just better measurement of the same substrate behavior
- (B) Scorer leniency / tuning (the 30q canonical set tuned BY the mechanisms it tests): Goodhart -- inflated claim

Auditor cannot adjudicate from broadcast. Need substrate-internal evidence.

## Spec

Auditor confirms 30q held-out provenance by checking:

1. **Authoring timestamps:** when were the 30q canonical questions authored vs when were the mechanisms (HMM, perceptron, NER, bayes, intent, L6-PROOF FINDER, CHTV-1) shipped/promoted?
   - Source: `data/substrate_index/benchmark_corpus_v1_30q.jsonl` (file mtime + content timestamps)
   - Source: git history for tool commits (HMM decoder file commits + L6-PROOF FINDER + CHTV-1 + KP P1 promotions)
   - If 30q authored AFTER mechanism shipment: GENUINELY held-out (no tuning possible)
   - If 30q authored BEFORE mechanism shipment: pre-existing test set; mechanisms could have been tuned to fit
   - If 30q authored CONCURRENTLY: requires manual review of overlap

2. **Mechanism reach check:** for each 30q question, did the substrate retrieve/answer it via a mechanism that was tuned on this specific question or similar questions?
   - Spot-check: 5 random 30q questions; trace substrate's answer path; check if the answer mechanism was authored/promoted with that question in scope

3. **HP_v1 reference:** the internal pre-reg HP_v1 = 0.70 bar. If 30q matches HP_v1 question set, then 30q is the PRE-REG set substrate was designed against; expected to score well; Goodhart-OK but caveat the headline
   - Source: search for any HP_v1 question authoring artifacts

## HARD-PASS / HARD-FAIL

- **HARD-PASS (GENUINELY HELD-OUT):** 30q questions authored after mechanism shipment OR before mechanism shipment but explicitly NOT used for mechanism tuning -> floor LOCKS to MET-DECISIVE
- **HARD-FAIL (TUNED):** any of the 30q questions can be traced to mechanism authoring/tuning -> floor stays MET-PROVISIONAL with Goodhart-caveat; report honestly
- **AMBIGUOUS:** mixed authoring; some genuinely held-out, some tuned -> partition 30q into TUNED + HELD-OUT subsets; report F1 separately on each

## Cost

~30-60 min Auditor scan + manual review. Cheap.

## Reservations

- **R1 (USER 10th rule):** report ACTUAL provenance evidence; do not advocate either direction
- **R2 (USER 11th rule):** substrate-on-its-own first; if mechanism + question authoring overlap is found, honest disclosure required
- **R3 (USER 7th rule reconsider):** Auditor may flag if the entire 30q benchmark needs replacement with a fresh held-out set; that's a substantive disclosure

## What this closes

- IF GENUINELY HELD-OUT: F1 floor = MET-DECISIVE; LAKATOS axis C 2/4 with both floors DECISIVE; Goal 1 capability claim defensible at strongest level
- IF NOT: F1 floor = MET-PROVISIONAL with honest disclosure; still substantive (60q confirmation; conservative macro >= 0.50 still holds with tuned baseline) but with Goodhart-caveat
- EITHER WAY: substrate-product positioning is more honest; Auditor's discipline serves the goal

## Tag

Tag verdict with `F1_PROVENANCE_PASS` or `F1_PROVENANCE_FAIL` so both monitors fire on the resolution.

## Cross-references

- Your F1 audit note: `notes/skunkworks_to_research_AUDIT_F1_floor_MET_confirmed_on_conservative_macro_0p55_two_items_before_DECISIVE_*`
- F1_FINAL canonical: `notes/exp_dev_to_research_F1_FINAL_canonical_union_0p568_*`
- F1 60q confirmation: `notes/exp_dev_to_research_DECISION_28_60q_CONFIRMS_*`
- Benchmark corpus: `data/substrate_index/benchmark_corpus_v1_30q.jsonl` + `benchmark_corpus_v3_60q.jsonl`

---

**Skunkworks (Auditor):** DECISION 30 30q held-out provenance check (Goodhart guard per 11th rule). 3-prong: authoring timestamps + per-question mechanism reach + HP_v1 reference check. HARD-PASS GENUINELY HELD-OUT -> floor MET-DECISIVE. HARD-FAIL TUNED -> MET-PROVISIONAL with honest disclosure. AMBIGUOUS -> partition 30q into TUNED + HELD-OUT and report separately. Cost ~30-60 min. Tag verdict with F1_PROVENANCE_PASS|F1_PROVENANCE_FAIL.
