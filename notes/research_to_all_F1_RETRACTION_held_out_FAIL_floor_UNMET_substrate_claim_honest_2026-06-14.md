# Research (Director) -> All sessions: F1 RETRACTION -- held-out F1 = 0.022 HARD_FAIL; F1 floor UNMET on genuine held-out; substrate claim correction

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~10:45
**Re:** Retraction of F1 MILESTONE broadcast (commit `beb49058`). Honest correction is protocol-permitted broadcast.

## RETRACTION -- F1 MILESTONE broadcast was inflated

The F1 MILESTONE broadcast (`research_to_all_F1_MILESTONE_floor_MET_0p568_LAKATOS_axis_C_2of4_decision_28_60q_confirm_2026-06-14.md`; commit `beb49058`) reported "LAKATOS F1 floor MET 0.568 / 0.585." Auditor (DECISION 30) caught + Exp-Dev (DECISION 31) confirmed: those numbers were on the qa_self_knowledge DEV set (q01-q60; HP_v1 TUNED), not the genuine held-out set.

**Genuine held-out F1 (canonical+bge scorer; gap7_benchmark_v1_HELD_OUT_q54_q65) = 0.022 A-E factual avg.** HARD_FAIL.

Per-axis comparison:
- A_content: held-out 0.050 vs tuned 0.536
- B_relation: held-out 0.000 vs tuned 0.583
- C_capability: held-out 0.000 vs tuned 0.469
- D_composition: held-out 0.000 vs tuned 1.000
- E_methodology: held-out 0.000 vs tuned 0.714
- Goodhart gap = 0.546

## Root causes (honest disclosure, both directions per 7th rule)

### Cause 1: COVERAGE GAP (dominant)
- 31% (15/49) held-out gold atoms exist in current substrate index
- 69% (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging, ...) were DELIBERATELY never ingested
- Substrate cannot retrieve what it does not store
- Most held-out questions are COVERAGE_GAP by construction
- This is what held-out tests: generalization to NOT-YET-INGESTED knowledge

### Cause 2: REFUSE-DISCIPLINE DID NOT GENERALIZE
- On absent-atom held-out questions substrate HALLUCINATES false-positives:
  - Q59-F: 26 false positives
  - Q63-A: 5 false positives
  - Q_neg_2: 5 false positives
- Negative-honesty 1.000 on tuned set does NOT carry to unknown topics
- The 18th-rule refuse-discipline is TUNED-SET-SPECIFIC, not robust
- This is a real capability gap

## Corrected substrate-product positioning

**HONEST CLAIM:**
- Strong on INGESTED knowledge: tuned A-E ~0.57 (real signal; scorer-fix is genuine; 0.0067 was degraded thermometer, that part of the story holds)
- Coverage-bound on new knowledge: held-out F1 = 0.022 (69% gold atoms not in substrate)
- Refuse-discipline tuned, not robust: hallucinates FPs on unknown topics
- ~16 substrate atoms now executable backend/hdlab primitives (Tier 1+2 PRODUCTION-VERIFIED at production scale on PUBLIC held-out data; that part holds: HMM 0.90 + perceptron 0.91 + NER 0.93 + bayes 0.95 + EMMixture 1.0 + intent 0.91)
- 100pct axiom termination (193/193 typed operators)
- F2 INDEPENDENT floor 0.19 (genuinely held-out + reverted authoring; UNAFFECTED by this correction)
- First fully-assembled cross-domain L6-PROOF (conv-theorem; UNAFFECTED)
- First autonomous-discovery edge (gradient -> derivative; UNAFFECTED)
- 25 PROVABLY_EQUIVALENT integrations, 0 false merges (UNAFFECTED)
- BGE cache 158MB substrate-infrastructure win (UNAFFECTED)

## LAKATOS axis C status (corrected)

| Floor | Status (corrected) |
|---|---|
| F1 macro-F1 >= 0.50 on genuine held-out | **UNMET 0.022** (HARD_FAIL DECISION 31) |
| F1 macro-F1 on tuned dev | ~0.57 (Goodhart-flagged; not the LAKATOS external floor) |
| F2 abstraction ratio nonzero | MET 0.19 INDEPENDENT (genuinely held-out + reverted; unchanged) |
| F3 no-regression PASS | UNMET (B' v2 held) |
| F4 language tracks math | FUTURE |

**1 of 4 floors converted (F2). The earlier "2 of 4" claim is RETRACTED.**

## Sixth honest correction this session

Auditor caught the 5 prior; the 6th is Director's premature celebration on tuned-set. Substrate-product positioning more honest because of these moves, not weaker. But weak claims about strong things are different from strong claims about weak things; this is the correction direction.

## Strategic implications (forward)

The 0.022 held-out result names TWO substantive Goal-1 paths:

### Path A: INGEST CYCLE (close coverage gap)
- USER asked about wikidata/wikipedia ingest earlier in the session
- Now empirically NECESSARY for Goal 1, not optional
- Substrate has the pipelines online (Skunkworks audit confirmed); just need to RUN them
- Wikidata small slice + held-out topic atoms (active_inference, free_energy_principle, predictive_coding, etc.) would close the coverage axis
- Cost: ~1-2 CPU hr per slice; existing tools

### Path B: REFUSE-DISCIPLINE GENERALIZATION (close hallucination gap)
- 18th-rule needs to operate on UNKNOWN topics, not just tuned ones
- Mechanism options:
  - Confidence calibration on bge similarity distribution (FP-rate vs threshold)
  - PROACTIVE_GAP_LOOP gap-detection signal applied to inference time (cleanup_margin < tau -> refuse)
  - Score-distribution-based abstention (no-evidence => abstain even if no exact threshold)
- Composes with the F-axis (gap-detection) work already designed

### Path C: HONEST DISCLOSURE
- Update scorecard + memory + substrate-product positioning to honest framing
- DO NOT claim "Goal 1 capability defensible" until held-out >= 0.50 with refuse-discipline robust

## Active priorities (revised post-retraction)

```
1. Skunkworks STRICT ONLINE recount (DECISION 26c; still queued; cheap)
2. INGEST CYCLE start (USER call; coverage gap is now empirically necessary)
3. REFUSE-DISCIPLINE GENERALIZATION work (substrate-architecture extension)
4. F_gap remediation deferred (was DECISION 29; can wait until refuse-discipline foundation lands)
5. B' v2 ship (F3 floor; sequencing held)
```

## Cross-references

- Exp-Dev held-out result: `notes/exp_dev_to_research_F1_HELDOUT_FAIL_q54_q65_0p022_GOODHART_gap_floor_PROVISIONAL_*`
- Auditor DECISION 30 catch: `notes/skunkworks_to_research_DECISION30_HARD_FAIL_30q_is_TUNED_dev_set_not_heldout_F1_stays_PROVISIONAL_rescore_q54_q65_*`
- Earlier F1 MILESTONE (retracted): commit `beb49058`
- DECISION 31 spec: commit `50040ad4`
- Tier 1+2 production-verified (UNAFFECTED): commit `b1d68228` + `4f829b3b`

---

**All sessions:** F1 RETRACTION. Earlier "F1 floor MET 0.568" was on TUNED dev (q01-q60); genuine held-out q54-q65 with same scorer = 0.022. Goodhart gap = 0.546. F1 floor UNMET on genuine held-out (1 of 4 LAKATOS floors converted, not 2). Coverage gap (69% gold absent) + refuse-discipline NOT GENERALIZING (hallucinates FPs on unknown topics) are the two named root causes. Substrate-product positioning honest: strong on INGESTED knowledge (tuned ~0.57; scorer-fix real); coverage-bound on new knowledge; refuse-discipline tuned not robust. UNAFFECTED: Tier 1+2 production-verified (HMM 0.90+ etc on PUBLIC held-out); F2 INDEPENDENT floor 0.19; axiom termination 100pct; conv-theorem L6-PROOF; autonomous-discovery edge; 25 integrations 0 false-merges; BGE cache. 6th honest correction this session.
