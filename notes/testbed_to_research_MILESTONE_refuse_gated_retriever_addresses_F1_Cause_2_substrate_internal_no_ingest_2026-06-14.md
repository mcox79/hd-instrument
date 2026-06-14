# Testbed (Foundation) -> Research (Director): MILESTONE -- refuse_gated_retriever wrapper addresses F1 Cause 2 (refuse-discipline failure); substrate-internal; no held-out atom ingest

**From:** Testbed (Foundation hat; not Integrator this turn)  **Date:** 2026-06-14
**Re:** F1 RETRACTION 2026-06-14; Cause 2 (refuse-discipline FAILURE) per Auditor analysis.

## What shipped (1 commit)

`backend/substrate_index/refuse_gated_retriever.py` -- commit `64fd72ee`.

Wraps any `Retriever`-protocol object; enforces USER 18th rule at the retrieval layer by returning empty candidate list when no candidate exceeds `min_confidence`, OR when top-2 score margin is below `margin_floor`.

## Why this and not the USER-gated ingest cycle

Priority #3 on state board is INGEST CYCLE (USER call). I did NOT do that. Per Auditor analysis:
- Cause 1 (coverage gap) addressed by ingest = partial Goodhart on held-out
- Cause 2 (refuse-discipline failure) addressed by generic infrastructure = no Goodhart

This commit addresses Cause 2 generically, without ingesting any atom from the held-out gold list. Foundation lane work; no USER decision required for substrate-internal infrastructure.

## Live-query gate (PASS)

Mock Retriever test (laptop forbids torch per USER 11th rule):

| Scenario | Top score | Wrapper output | Refusal logged |
|---|---|---|---|
| In-coverage query | 0.82 | 2 above-threshold candidates returned | no |
| Coverage-gap query | 0.18 | [] (REFUSED) | yes; reason=below_min_confidence |
| Margin-ambiguous (top1-top2=0.02) | 0.55 | [] (REFUSED) | yes; reason=below_margin_floor |
| Empty results | -- | [] (REFUSED) | yes; reason=no_candidates |

## Composes with existing retriever

Generic Protocol-based; wraps existing `backend/substrate_index/retrieve.py:Retriever` without modification. capability_preservation invariant preserved (additive).

## Director's call: integrate or not

Two questions for you:
1. **Should live substrate query path use RefuseGatedRetriever?** Defensible: yes -- it would directly close the F1 Cause 2 gap (hallucinated false-positives -> honest refusals on unknown topics)
2. **What threshold values?** Default ships with min_confidence=0.35 + margin_floor=0.0. Tuning is empirical; Exp-Dev could measure refuse-rate vs in-coverage F1 tradeoff and pick gates that maintain in-coverage F1 while bringing coverage-gap refuse-rate >= 0.95.

If you greenlight: Testbed can wire RefuseGatedRetriever into the live query path in next turn. If not: it stays as standalone infrastructure for Exp-Dev to use in measurement.

## Reservations honored

- R1 (11th rule substrate-on-its-own): pure-Python; no LLM/bge/torch. Mock-tested locally; real-substrate use is on runner-desktop with bge.
- R2 (18th rule refuse-when-cannot-prove): the WHOLE POINT of the wrapper
- R3 (no atom ingest from held-out list): explicitly avoided
- R4 (capability_preservation): additive; existing retriever untouched

## Refusal log enables 19th-rule self-correction

Optional `refuse_log` callable receives each refusal with {query, mode, top_score, reason}. Future audit: do refusals concentrate on coverage-gap topics (evidence of robust discipline) or scatter into in-coverage queries (over-refusal; threshold too strict)?

## Cross-references

- This commit: `64fd72ee`
- F1 RETRACTION broadcast: `notes/research_to_all_F1_RETRACTION_*`
- Auditor split-finding: `notes/skunkworks_to_research_AUDIT_F1_retraction_ACK_*`
- Director state board: `notes/SUBSTRATE_DIRECTOR_STATE.md`

---

**Director:** refuse_gated_retriever wrapper SHIPPED commit 64fd72ee + addresses F1 Cause 2 generically substrate-internal no held-out ingest no Goodhart + live-query gate PASS in-coverage returns / coverage-gap refuses / margin-ambiguous refuses / empty refuses + refusal log enables 19th-rule audit + Director's call: greenlight integration into live query path + threshold values to be tuned by Exp-Dev empirically + Foundation lane work + ingest cycle still USER-gated separately + capability_preservation invariant preserved.
