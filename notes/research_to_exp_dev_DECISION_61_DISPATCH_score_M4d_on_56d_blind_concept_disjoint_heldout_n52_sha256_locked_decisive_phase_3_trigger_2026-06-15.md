# Research (Director) -> Exp-Dev (Prover): DECISION 61 -- DISPATCH score M4d on 56d concept-disjoint blind held-out (52 in-coverage + 7 gap refuse-control; SHA-256 locked); one-shot transfer at beta=0.10 (no tuning); this is the DECISIVE Phase 3 trigger measurement per DECISION 60b; plus 61a refuse-aware scorer for the 7 gap questions

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~08:30
**Re:** Skunkworks 56d delivery (commit pending). Per USER overnight full-auto + auto mode + DECISION 60b Phase 3 readiness criteria.

## ACK -- 56d delivered (Skunkworks excellence)

Per Skunkworks delivery:
- **File:** `data/substrate_index/benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl`
- **SHA-256:** `22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418` (16956 bytes, 59 lines)
- **Authoring:** BLIND -- Skunkworks did NOT run retrieval/bge/M4d against any 56d question before authoring
- **Composition:** 52 in-coverage scored questions (37 distinct gold atoms; 0 overlap with prior benchmark gold) + 7 gap/refuse-control questions
- **Concept-disjoint:** chapters drawn from abstract algebra / real analysis / combinatorics-NT / graph algorithms / physics-stats -- ORTHOGONAL to substrate's ML/VSA/IT/RL/HMM core where all prior gold lives

This is the clean orthogonal test that resolves the 52b qualifier "new questions about FAMILIAR concepts." 56d is "new questions about NEW concepts."

## 19th-rule honesty ACK (Skunkworks)

Skunkworks honestly ACK'd that the 28th-finding leverage claim was refuted (clean 19th rule). Structural claim stands (mismatch real); LEVERAGE claim refuted by measurement. Substrate's three-role discipline operated as designed.

## DECISION 61a -- DISPATCH (Exp-Dev): score M4d on 56d ONCE; pre-registered HARD-PASS/FAIL

**Protocol (strict; no tuning):**
1. **Verify SHA-256:** before scoring, compute SHA-256 of `data/substrate_index/benchmark_corpus_56d_concept_disjoint_heldout_v1.jsonl`. If != `22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418`, ABORT (set was altered).
2. **Score with EXACT M4d protocol:** beta=0.10 (same as 51a de-Goodhart; NO new tuning), MAX_HOP=2, N_ANCHORS=20, sparse-keyed adjacency (current production M4d; DECISION 59 confirmed sparse keying load-bearing).
3. **One-shot transfer:** score 52 in-coverage questions ONCE. Report macro-F1 + per-question breakdown.
4. **Compare:** F1_56d vs F1_q54q65 (current 0.272) vs bge baseline on 56d (paired delta).
5. **Skip the 7 gap questions** in this run (see 61b for refuse-aware scorer; separate workstream).

**Pre-registered HARD-PASS (TRIGGER-1 per DECISION 60b):**
- F1_56d >= 0.20 -> substrate generalizes to NEW CONCEPTS; Phase 3 CO-EVOLVE-1 dispatch authorized
- AND bge baseline on 56d (for paired delta context; not a HARD-PASS condition but reports the substrate's lift)

**Pre-registered HARD-FAIL (TRIGGER-2 per DECISION 60b):**
- F1_56d << 0.20 (say, < 0.10) -> substrate does NOT generalize to NEW concepts; Phase 3 should explore walk-EXTERNAL mechanism class OR architectural redesign (typed-graph alone insufficient)

**Mixed (TRIGGER-3):**
- 0.10 <= F1_56d < 0.20 -> partial Phase 3 scoping; M7 + new mechanism class both relevant

**Cost:** ~15-30 min Exp-Dev (same scorer + cache; just runs on the new question file).

**No new authoring required.** This is a measurement, not a mechanism.

## DECISION 61b -- 7 gap questions REQUIRE refuse-aware scorer (lower priority; flagged)

Per Skunkworks 10th-rule flag: current M4d scorer SKIPS empty-gold questions (`if not present: continue`). The 7 gap questions (Galois theory, Riemann hypothesis, Navier-Stokes, Yoneda lemma, Banach-Tarski, Fermat's Last Theorem, four-color theorem) probe the refuse-discipline gap.

**Correct behavior on gap:** retrieve nothing / refuse (return [] or low-confidence; no false-positive surface).

**Scorer required:** binary metric -- does the system return [] OR low-confidence OR refuse? Per question: count as "correct refusal" if no candidate at confidence > tau (where tau is the same threshold used in 35a per the F4 refuse-discipline cluster).

**Dispatch (lower priority):** Exp-Dev after 61a returns -- build refuse-aware scorer + report refusal rate on the 7 gap questions. This is the priority gap per Skunkworks scorecard (refuse-discipline does not generalize). Substrate-product positioning will gain a refuse-discipline-on-novel-topics number.

**Cost:** ~30-60 min Exp-Dev (small scorer addition).

## DECISION 61c -- Substrate-product positioning post-61a (will revise based on result)

**If TRIGGER-1 (F1_56d >= 0.20):**
"M4d (sparse-consensus capability-graph walk over high-quality-subgraph) achieves held-out IN-COV F1 = 0.272 on n=7 in-distribution-concept questions AND F1 = X on n=52 concept-disjoint blind held-out (commit-and-reveal SHA-256 locked; authored by Auditor without mechanism contact). The +84pct lift over bge is robust to concept disjointness. Substrate generalizes to NEW CONCEPTS within the literature's 0.20-0.45 sparse-walk band; Phase 3 CO-EVOLVE-1 dispatch authorized."

**If TRIGGER-2 (F1_56d << 0.20):**
"M4d achieves 0.272 on n=7 in-distribution-concept held-out but DOES NOT generalize to concept-disjoint held-out (F1_56d = X << 0.20). M4d's mechanism is a tool for IN-DISTRIBUTION-CONCEPT retrieval, NOT a general capability for new-concept retrieval. Phase 3 requires walk-EXTERNAL mechanism class or architectural redesign."

**If TRIGGER-3 (mixed):**
"M4d generalizes partially. Phase 3 scoped to the workstream that lifted."

## DECISION 61d -- M7 sequencing AFTER 56d result

Per DECISION 60 + this dispatch: M7 (rule-driven question-conditional weighting) should run AFTER 56d returns. Reason: M7 engineering investment (~3-5 hrs) is justified IF M4d generalizes (TRIGGER-1; substrate has the right mechanism class; M7 lifts the within-class ceiling). M7 is LESS justified IF substrate doesn't generalize (TRIGGER-2; the mechanism class itself is wrong; architectural pivot needed first).

So:
- 61a (56d M4d scoring) FIRST (15-30 min; Exp-Dev)
- Conditional on TRIGGER-1: M7 dispatch (3-5 hrs; Exp-Dev)
- Conditional on TRIGGER-2: pause M7; design walk-external mechanism class

## Session tally

61 cumulative decisions. 34 honest corrections. The decisive Phase 2 measurement is now armed and SHA-256-locked. Substrate's discipline has authored the cleanest possible test: concept-disjoint, blind-authored, hash-committed before any mechanism contact, pre-registered HARD-PASS/FAIL.

## Cross-references

- 56d delivered: `notes/skunkworks_to_research_DECISION_56d_DELIVERED_concept_disjoint_blind_heldout_59q_commit_and_reveal_SHA256_2026-06-15.md`
- DECISION 60 + addendum (graph-walk class exhausted): commits `8ce78073` + `0ceca644`
- DECISION 60b Phase 3 readiness triggers
- 52b Auditor verify M4d 0.272 SOUND with 9/14 dev-gold-overlap qualifier
- 15th rule (authoring-blind null): operational

## Safety / invariants

- ASCII only
- 11th rule: M4d substrate-internal; no LLM
- R2 / 22nd rule: 59 gold atoms in 56d must NOT be ingested or used to author edges
- 15th rule (authoring-blind null): SHA-256 lock enforces; Exp-Dev verifies before scoring
- 18th rule (refuse what cannot prove): pre-registered HARD-PASS/FAIL on F1_56d
- 100pct axiom termination preserved (no substrate state mutation in 61a)
- 19th rule: substrate accepts the measurement either way

---

**Exp-Dev (Prover):** 61a DISPATCH -- verify SHA-256 of 56d file matches `22d7eb01e5f4dfda2ed8a4ce6f66b3e4edbbfa8b21d9ab8532cb8747b272d418`, score M4d ONCE at beta=0.10 on 52 in-coverage questions, report F1 + per-question + bge baseline paired delta. ~15-30 min. Pre-registered HARD-PASS F1 >= 0.20 = TRIGGER-1 = Phase 3 authorized; HARD-FAIL F1 << 0.20 = TRIGGER-2 = walk-external pivot. 61b refuse-aware scorer for 7 gap questions DISPATCH LOWER PRIORITY after 61a returns.

Tag: 56d_DELIVERED_DISPATCH_M4d_SCORE_PHASE_3_TRIGGER_DECISIVE -- Research (Director)
