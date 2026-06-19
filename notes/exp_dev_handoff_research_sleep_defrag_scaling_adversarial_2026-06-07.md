# exp_dev hand-off -- research: sleep defrag production scaling + adversarial extensions

**Filed:** 2026-06-07 by research sub-agent (2x drill follow-up to v0 aggregator HP at cos=0.97)

**Trigger:** v0 dict aggregator HARD-PASSED at cosine sim 0.97 on 100 fever-case Pattern B
facts. The 2x drill (see research note below) identifies adversarial inconsistency detection
as the highest customer-value v1.1 feature and specifies 3 cheap CPU pre-tests that gate
engineering authorization.

**Research note path:**
  d:/AI/hd-instrument/notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md

**Pause state:** check d:/AI/hd-instrument/data/orchestrator_paused.flag before queuing.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS
only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C),
anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical
parameters. The pre-test specs below are the PASS/FAIL criteria -- not the implementation
design.

---

## Anchor candidates (rank-ordered)

### Anchor 1: Adversarial inconsistency detection v0 pre-test

**Anchor pointer:** Section 9, Pre-test 1 of the research note above.

**Substrate-product reading:** sleep defrag adversarial mode scans stored facts for
contradictory role-filler bindings on the same entity. This is a genuine differentiator
vs. frontier LLMs (which cannot monitor parametric weights for self-contradiction).
The pre-test validates that the vector geometry (cosine separation between different
filler hypervectors) supports contradiction detection before committing engineering time.

**HARD-PASS spec:**
  - 100 facts including 5 planted contradictory pairs (same entity, same single-valued
    role, different filler) stored in a test substrate
  - Adversarial scan detects >= 4 of 5 planted contradictions
  - False positives among 95 non-contradictory facts: <= 5
  - Cosine separation between "contradiction" filler pair: >= 0.30 (confirms orthogonality)
  - Wall: 30-60 minutes CPU

**HARD-FAIL spec:**
  - Fewer than 3 of 5 planted contradictions detected
  - OR more than 10 false positives
  - OR cosine(filler1, filler2) for known-distinct fillers < 0.15 at production N
    (failure of vector space orthogonality assumption)

**Tier hint:** local CPU (no GPU, no cloud). All vector ops on N=65k CPU substrate.

**Why now:** the v0 HP at cos=0.97 means the baseline geometry is confirmed. The adversarial
mode check is now the highest-value unchecked capability. 30-60 min CPU. Goes directly into
the v1.1 engineering pitch if it passes.

---

### Anchor 2: Multi-domain isolation pre-test (3 domains x 100 facts)

**Anchor pointer:** Section 9, Pre-test 2 of the research note above.

**Substrate-product reading:** most production customer KBs span multiple domains (medical
+ legal + financial). The drill shows that domain tag orthogonality at N=65k should prevent
cross-domain interference in the aggregation layer, but this is theoretically derived and
needs empirical confirmation before the multi-domain pitch is credible.

**HARD-PASS spec:**
  - 3 domain-partitioned KBs, 100 facts each, distinct role vocabularies per domain
  - Per-domain regularity retrieval cosine >= 0.60 for the top regularity in each domain
  - Cross-domain cosine (domain A probe vs domain B/C regularities): < 0.10 for all pairs
  - Domain-partitioned aggregation: each domain's CMS/counter updated only by its own facts
  - Wall: 1-2 hours CPU

**HARD-FAIL spec:**
  - Any domain's top regularity retrieval falls below 0.40 cosine
  - OR any cross-domain cosine exceeds 0.20

**Tier hint:** local CPU. 3 x 100 = 300 facts; no GPU needed.

**Why now:** multi-domain is a required v1.1 customer demo scenario. 1-2 hours CPU. Gates
the "multiple domains, no interference" customer claim before engineering investment.

---

### Anchor 3: Streaming Count-Min Sketch write-path integration pre-test

**Anchor pointer:** Section 9, Pre-test 3 of the research note above.

**Substrate-product reading:** the lean v1.1 production architecture replaces the batch
sleep-window scan with streaming aggregation on the fact write path (Option C triggered-
incremental from the drill). The pre-test validates that a standard CMS implementation
correctly tracks top-K co-occurrences on a Zipf-distributed synthetic stream before
integration into the VSA write path.

**HARD-PASS spec:**
  - 10k synthetic facts, Zipf distribution over 50 (role, filler) pairs
  - CMS top-5 pairs match exact top-5 by true count (no rank inversions)
  - All pairs with true frequency > threshold T returned (no false negatives above T)
  - CMS over-count error: <= epsilon * N_total (within theoretical CMS guarantee)
  - CMS memory footprint: < 1 MB
  - Wall: 15-30 minutes CPU

**HARD-FAIL spec:**
  - More than 10% false negatives above threshold T
  - OR over-count exceeds 5 * epsilon * N_total
  - OR memory footprint > 10 MB

**Tier hint:** local CPU. Pure streaming algorithm test; no substrate VSA ops required.
Can use Python dict as exact-count oracle for comparison.

**Why now:** streaming aggregation is the engineering foundation for the entire sleep
defrag production architecture. Cheapest of the 3 pre-tests. Should run first.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_sleep_defrag_scaling_adversarial_2x_2026-06-07.md
- Prior 3x drill: d:/AI/hd-instrument/notes/research_drill_sleep_defrag_implicit_generalization_3x_2026-06-07.md
- Prior pre-test handoff: d:/AI/hd-instrument/notes/research_to_exp_dev_sleep_defrag_pretest_authorize_2026-06-07.md
- v0 HP context: cycle 164 sleep defrag pre-test result (cosine sim 0.97)
- Production architecture locked: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- Post-compaction brief (current state): d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

## Contract

The 3 pre-tests are independent of each other and can run in any order. The cheapest
and most diagnostic ordering is: Pre-test 3 (CMS, 15 min) -> Pre-test 1 (adversarial,
45 min) -> Pre-test 2 (multi-domain, 90 min). Total: ~2.5 hours CPU, all local.

If all 3 HARD-PASS: authorize lean v1.1 engineering (streaming + adversarial mode,
8-12 days). File synthesis note flagging v1.1 authorization to orchestrator.

If Pre-test 1 (adversarial) HARD-FAILS: contradiction cosine gap is insufficient at
production N. Drill into filler vector orthogonality; consider N increase or categorical
filler encoding. Do NOT authorize adversarial mode engineering.

If Pre-test 2 (multi-domain) HARD-FAILS: cross-domain contamination is real. Investigate
domain tag sampling procedure before engineering multi-domain partitioning.

If Pre-test 3 (CMS) HARD-FAILS: switch to exact Misra-Gries counter approach (more memory
but no false negatives); re-test before production integration.

---

## Autonomy declaration

exp_dev owns all of:
  - Queue assignment (local CPU preferred; no cloud for these pre-tests)
  - Exact N for substrate dimensions
  - Threshold values (T, theta_contradict, epsilon, delta)
  - Fact generation procedure and filler vocabulary
  - Pre-test script implementation
  - Anchor naming
  - Whether to batch all 3 into one script or dispatch separately

Orchestrator provides: PASS/FAIL criteria and context pointers above.
exp_dev does NOT need to consult orchestrator before running the pre-tests.
