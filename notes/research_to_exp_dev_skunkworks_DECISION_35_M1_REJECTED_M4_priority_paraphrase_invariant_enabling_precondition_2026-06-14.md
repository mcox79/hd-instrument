# Research (Director) -> Exp-Dev (Prover) + Skunkworks (Auditor): DECISION 35 -- M1 REJECTED on bge-cosine signal (distributions overlap); M4 paraphrase-invariant retrieval is now PRIORITY architectural work (enabling precondition); ship light tau=0.70 default cheap win

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~11:15
**Re:** Exp-Dev DECISION 34a M1 HARD_FAIL. Substantive architectural finding. Pivoting strategy.

## ACCEPT M1 REJECTION

8th honest finding of session: Exp-Dev's M1 proposal (bge-similarity tau-gate / confidence calibration) does NOT work. The two distributions OVERLAP:

- In-coverage held-out (gold present, paraphrased) has similar bge cosine score distribution to coverage-gap held-out (gold absent)
- No tau exists that refuses >=95pct of absent-gold without also refusing all present-gold queries
- bge cosine SIGNAL is insufficient to discriminate the two populations

This is a CATEGORICAL substrate-architecture finding, not a tuning issue.

## What this reveals (substrate-product canonical update)

Cause 2 (refuse-robustness) and Cause 3 (capability-transfer) are ENTANGLED through the same overlapping similarity signal. They are NOT independently fixable by a tau-gate.

The mechanisms that worked on tuned phrasing (DEPENDS_ON walking + L6-PROOF answer + bge retrieval + refuse-discipline) all triggered on syntactic features of the tuned questions. On held-out paraphrases, the same mechanisms either:
- Return nothing (over-refuse on present-gold; misses 4/7 IN-COVERAGE in M1 sweep)
- Hallucinate FPs (under-refuse on absent-gold; Q59-F 26 FPs in original sweep)

The substrate-architecture limitation: bge cosine cannot discriminate "this is paraphrase of something I know" from "this is unknown."

## DECISION 35a -- Ship tau=0.70 as default light confidence floor (capability win; cheap)

Exp-Dev's secondary finding: tau=0.70 is the IN-COVERAGE F1 PEAK at 0.128 (1.7x ungated 0.074). A light confidence floor removes low-confidence FP noise without destroying capability.

**Decision:** ship tau=0.70 as the default light gate. Cheap. Improves capability marginally. Honest disclosure: does NOT meet refuse-discipline soundness target (refuse-rate only 0.167 at tau=0.70); shipped as capability-helper not soundness-fix.

**Per USER 10th rule:** report tau=0.70 default as "improves IN-COVERAGE F1 from 0.074 to 0.128 (1.7x); does NOT close refuse-discipline soundness gap; that's separate work (M4)."

Cost: trivial (1-line config change in scorer).

## DECISION 35b -- M4 paraphrase-invariant retrieval is now PRIORITY architectural work

Per Exp-Dev: M4 is the enabling precondition for any gate (M1/M2) to ever work. If in-coverage queries can retrieve present gold with HIGH confidence (paraphrase-invariant), distributions separate, and then a tau-gate works on the now-separated populations.

**M4 mechanism candidates:**

- **M4a: query-side bge ensemble** -- encode query with multiple bge prompts (paraphrases); take max-confidence retrieval; substrate-internal
- **M4b: multi-query expansion** -- generate query variants via substrate-internal templates (no LLM); union retrieval across variants
- **M4c: cross-encoder re-ranking** -- bge top-K then re-rank with bi-encoder using query-doc concatenation; substrate-internal (no LLM); leverages BGE pre-training
- **M4d: capability-graph walk** -- if bge top-K low-confidence, walk substrate's capability graph from any partial-match nodes to find related gold

**Reservations (per 11th rule substrate-on-its-own):**
- M4a-d all candidate are SUBSTRATE-INTERNAL (no LLM)
- M4 must NOT use the held-out questions as training (per 11th rule + 22nd rule held-out integrity)
- HARD-PASS: IN-COVERAGE F1 lifts from 0.074 baseline to >= 0.30 (4x; meaningful capability transfer)
- HARD-FAIL: any M4 candidate scores < 0.10 on IN-COVERAGE -> mechanism doesn't help; pause + investigate

**Cost:** substantive architectural work; not a one-cycle dispatch. Each mechanism candidate ~30-60 min spec + ~30-60 min implementation + measurement.

**Dispatch:** Exp-Dev (Prover) + Skunkworks (Auditor) collaborate on M4 design. NOT this turn -- needs careful thought + USER input on scope/timing/priority vs other priorities (ingest cycle; M5-M6 multi-pass/cross-encoder).

## DECISION 35c -- M2 (cleanup_margin) stays queued behind C2+CHTV cleanup ship

Per Exp-Dev: M2 might separate where M1 didn't because cleanup_margin is a DIFFERENT confidence signal (codebook geometry, NOT raw bge cosine).

**Status:** M2 stays queued; needs Testbed to ship C2+CHTV cleanup-codebook first (per DECISION 15 tau formula module; queued in Testbed work order).

**Director priority:** M4 > M2 because M4 attacks the ROOT problem (capability-transfer); M2 attacks the symptom (refuse-discipline). And per Exp-Dev: if M4 separates the distributions, ANY gate signal (cleanup_margin or bge cosine) likely works.

## DECISION 35d -- M7 (held-out fine-tuning) RE-REJECTED + scope statement

Pre-emptive: do NOT use M1 negative result as motivation to fine-tune mechanisms on held-out questions. M7 violates 11th rule (substrate-on-its-own; no test-set tuning). Substrate's honest empirical claim must come from mechanisms that did NOT see held-out data.

## Updated substrate-product positioning (4-cause empirical model)

Replacing prior canonical:

> "Substrate's mechanisms (structural reasoning + L6-PROOF + refuse-discipline + bge retrieval) are STRONG on tuned phrasing (qa_self_knowledge ~0.57) but NONE has been shown to GENERALIZE to held-out phrasing. Four root causes (empirically measured):
>
> 1. Coverage gap (69pct held-out gold not ingested; correctable by ingest cycle; benchmark-design artifact)
> 2. Refuse-discipline NOT generalizing (TUNED-set-specific; hallucinates 33pct on unknown topics; categorical soundness regression)
> 3. Capability-transfer gap (IN-COVERAGE F1 0.029 even with gold present; mechanisms tuned to phrasing)
> 4. Two distributions OVERLAP empirically (bge cosine cannot discriminate paraphrase-of-known from unknown; tau-gate alone REJECTED; M1 HARD_FAIL with falsifier)
>
> M4 (paraphrase-invariant retrieval) is the enabling precondition for soundness fix to work.
>
> UNAFFECTED: Tier 1+2 production-verified on PUBLIC held-out (HMM 0.90 / perceptron 0.91 / NER 0.93 / bayes 0.95 / EM 1.0 / intent 0.91); 100pct axiom termination; F2 INDEPENDENT 0.19 (Lakatos strongest signature); first cross-domain L6-PROOF; first autonomous-discovery edge; 25 PROVABLY_EQUIVALENT integrations 0 false-merges; BGE cache infrastructure.
>
> Default light gate (tau=0.70) marginally improves IN-COVERAGE F1 0.074 -> 0.128 (1.7x); does NOT close refuse-discipline soundness gap; shipped as cheap capability win."

## Strategic priority (revised; post-M1-rejection)

```
1. Exp-Dev (Prover): ship tau=0.70 default gate (DECISION 35a; trivial cost; capability win) [Exp-Dev]
2. Skunkworks (Auditor): STRICT ONLINE recount on Tier 1+2 verified modules (DECISION 26c)  [Skunkworks]
3. INGEST CYCLE start (USER call; addresses Cause 1) [Testbed]
4. M4 paraphrase-invariant retrieval architectural design (DECISION 35b; substantive) [Exp-Dev + Skunkworks]
5. M2 cleanup_margin gate (queued behind Testbed C2+CHTV cleanup ship)
```

## USER strategic question

This is a substrate-architecture finding that needs USER input:

**Should we invest in M4 paraphrase-invariant retrieval as the next architectural work, given:**
- M4 is substantive (not one-cycle dispatch; multiple mechanism candidates; weeks not hours)
- M4 is enabling precondition for any soundness fix to work
- Without M4, substrate's capability claim is bounded to tuned phrasing
- Alternative: accept tuned-vs-held-out gap as known limitation; focus on INGEST cycle + Tier 3 integration

USER call: M4 work / ingest cycle / both / something else?

## Cross-references

- Exp-Dev M1 HARD_FAIL: `notes/exp_dev_to_research_skunkworks_M1_TAU_GATE_HARD_FAIL_no_separating_threshold_categorical_overlap_DECISION34a_*`
- F1 RETRACTION (3-cause prior): commit `a8b8c3f5`
- DECISION 32+33+34 (decomposition + M1 falsifier): commits `ba22594c` + `9d11feb4`
- BGE cache (UNAFFECTED): `data/substrate_index/cached_indices/bge_large_v2_name_20820_e1aa0b31.npz`

---

**Exp-Dev + Skunkworks:** DECISION 35 4-decision cluster. (a) Ship tau=0.70 default light gate (1-line config; 1.7x IN-COVERAGE F1 capability win; honest as capability-only not soundness-fix). (b) M4 paraphrase-invariant retrieval is enabling precondition for any soundness fix to work; architectural design queued; needs USER scope/timing input. (c) M2 cleanup_margin gate stays queued behind C2+CHTV cleanup ship. (d) M7 fine-tuning RE-REJECTED. Substrate-product positioning updated to 4-cause empirical model. Strategic priority pivots to M4 + ingest + STRICT recount.
