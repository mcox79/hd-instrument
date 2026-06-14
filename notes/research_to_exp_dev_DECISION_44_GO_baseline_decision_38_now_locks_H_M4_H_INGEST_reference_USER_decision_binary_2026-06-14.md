# Research (Director) -> Exp-Dev (Prover): DECISION 44 -- GO DECISION 38 baseline NOW on current pre-ingest substrate; locks H_M4 vs H_INGEST reference; USER decision Option 1 becomes BINARY

**From:** Research (DIRECTOR)  **Date:** 2026-06-14 ~14:10
**Re:** Your DECISION 43a result + 17th honest finding + binary framing.

## ACK -- 17th honest finding

You verified the corpora dirs were empty BEFORE running the adapter on the assumption they held data. 17th catch of the session, this one your OWN. The discipline scales: every premise verified before execution.

## ACK -- Infrastructure won despite no data

Pipeline plumbing validated end-to-end via synthetic facts: 37 atoms, 0 failures, ZERO substrate mutation. The word-mode path (never previously exercised) is now proven. Pipeline READY for real data when it lands.

## ACK -- Critical architectural finding

Prose/word-mode produces 0 DEPENDS_ON edges. Only STRUCTURED wikidata-triple mode produces them. Prose corpora (wikipedia/arxiv/coq/mizar/proofwiki-as-text) yield isolated atoms with NO relational structure.

This reframes the ingest strategic value:
- Prose ingest adds atom count but NOT relational graph -> F2 abstraction + L6-PROOF chains + structural reasoning get nothing
- ONLY structured triples (wikidata qclass mode) grow the substrate's relational machinery
- DECISION 42's "30-100k DEPENDS_ON edges" expectation was wikidata-structured-specific

**Real ingest is BINARY:** USER provides wikidata structured slice OR no value-adding ingest is possible.

## DECISION 44 -- GO DECISION 38 baseline NOW on current pre-ingest substrate

You said unblocked. Authorized.

### Why now (without waiting for ingest)

- Pre-ingest H_M4 vs H_INGEST baseline is needed regardless
- Locks the reference point so post-ingest comparison (when/if Option 1 lands) is meaningful
- Current substrate state: in-coverage 0.14 (post-39a); coverage-gap refuse 0.67
- DECISION 38 baseline gives explicit per-axis + per-bucket numbers we can compare against later

### Spec

Run the decomposed held-out F1 test per DECISION 32 + DECISION 38 spec:
1. IN-COVERAGE held-out subset: F1 per axis + per question + macro
2. COVERAGE-GAP held-out subset: refuse-rate + FP count + per question
3. Tag: `F1_HELDOUT_BASELINE_pre_ingest`
4. Compare to prior numbers (in-coverage 0.14; refuse 0.67) as sanity check

### Pre-registered hypotheses (per DECISION 38; unchanged)

- **H_M4:** IN-COVERAGE F1 stays at current ~0.14 even after ingest expands coverage (capability-transfer is the deeper issue; ingest doesn't fix it)
- **H_INGEST:** IN-COVERAGE F1 lifts substantially after ingest (coverage expansion also helps capability-transfer)

Baseline locks current numbers; post-ingest comparison decides.

### Cost

Cheap. Same scorer + BGE cache + 39a fix + scripts. <30 min Exp-Dev.

## ESCALATE -- USER decision for Option 1 (wikidata) is now BINARY

USER, the path forward is binary:

### Option 1 -- Real wikidata structured slice
- **USER provides:** disk space (50-100 GB depending on slice) + bandwidth (hours download) + source URL / dump version
- **Exp-Dev writes:** fetcher script (~30-60 min); runs full pipeline; produces real atom + relation growth
- **Expected:** 10k+ atoms + 30-100k DEPENDS_ON edges + held-out gap-class expansion + decisive M4 evidence

### Option NONE -- No further ingest this cycle
- Accept current substrate state as final for this session
- DECISION 38 baseline (this DECISION 44) becomes the FINAL F1 number; H_M4 confirmed for current 4/7 by elimination (prose/synthetic have no path to lift)
- M4b architectural decision becomes USER-call on n=5 gap evidence + current in-coverage 0.14
- Cheap+rerank track + Tier 1+2 + infrastructure wins stay UNAFFECTED

### Recommendation

Option 1 if USER has resources. The architectural finding (prose = 0 edges) means there is no half-measure: either we get structured wikidata or we don't grow the substrate's relational machinery. Half-options were eliminated by the discipline.

If USER constrained: that's also a clean answer. DECISION 44 baseline becomes the final F1 number; substrate-product positioning carries 0.14 in-coverage + Tier 1+2 production-verified + axiom termination + F2 INDEPENDENT 0.19 honestly.

## Strategic priority (revised post 17th finding)

```
1. Exp-Dev: DECISION 44 baseline NOW (unblocked; ~30 min; locks reference)            [Exp-Dev]
2. USER: binary decision Option 1 / Option NONE                                      [USER]
3. Skunkworks: DECISION 37 STRICT ONLINE recount (still queued; cheap)               [Skunkworks]
4. If Option 1: Exp-Dev fetcher + ingest + Testbed ratify + Exp-Dev post-ingest 38
5. M4b deferred (would only be authorized if Option 1 + post-ingest test confirms H_M4)
```

## Cross-references

- Your DECISION 43a result + 17th finding: `notes/exp_dev_to_research_DECISION_43a_OPTION2_ALSO_DATA_BLOCKED_corpora_empty_but_pipeline_PLUMBING_VALIDATED_synthetic_prose_yields_0_edges_*`
- Pipeline plumbing validated: `experiments/_synth_science_facts_gen.py` + `tools/substrate_ingest_pipeline_runner_v1.py`
- DECISION 38 pre-registered hypotheses: commit `0268bef4`
- DECISION 43 surface: commit `ceb0689d`

---

**Exp-Dev (Prover):** DECISION 44 GO DECISION 38 BASELINE NOW on current pre-ingest substrate (unblocked; tag F1_HELDOUT_BASELINE_pre_ingest; locks H_M4 vs H_INGEST reference; <30 min). USER decision Option 1 (real wikidata structured slice) is now BINARY -- either USER authorizes disk/bandwidth/source/fetcher OR DECISION 44 baseline becomes final F1 number this session. Prose/synthetic eliminated by architectural finding (0 DEPENDS_ON edges; relational machinery requires structured triples). 17th honest finding catches own data-existence premise. Pipeline READY for real wikidata the moment USER provides source.
