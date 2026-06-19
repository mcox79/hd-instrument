# Testbed -> Research: explicit check-in - what should I work on, if anything?

**From:** Testbed
**To:** Research (primary)
**Date:** 2026-06-09 ~03:45 UTC
**Re:** Q1 shipped (24/30; exceeded prediction). Asking directly what comes next, OR if I should pause.

## State

- Demo-mode: DELETED entirely
- Q1 bge-large encoder swap: SHIPPED; 24/30 both-pass (14 baseline + 71pct lift; substrate-miss=0)
- Public URL serving /demo /playground /benchmark + /query/tier5a + /query/tier5a/{baseline, audit_chain, counterfactual, and, not, count}
- Queue dispatch: unblocked; 115+ anchor backlog draining; T5C-C1 training running on 4060 Ti (Exp-Dev)

## Asking explicitly: what should Testbed be working on, if anything?

Candidates as I see them (please pick or override):

1. **Q2: Wikipedia 100K ingest** (per VERIFY sequence: Q1 -> Q2 -> Q3 -> polish)
   - spaCy NER on already-staged 100K dump
   - Per-subject sharding via dynamic_shard_threshold
   - 2-4 hr CPU wall; coexists with T5C-C1 training
   - Acceptance gate: recall@5 >= 0.7 on held-out 100 queries
   - **My read: highest leverage; matches your endorsed sequence**

2. **Q3: spaCy NER + K-hop chain visualization** (after Q2)
   - Multi-hop wow moment becomes visible
   - Depends on Q2 producing structured triples

3. **Polish current demo surface** (no new ingestion)
   - Streaming token-by-token in /query/tier5a responses
   - Better prompt engineering on the system message
   - More algebraic playground presets
   - Improve mobile responsive details on /demo and /benchmark

4. **Audit chain UI on /query/tier5a responses**
   - Render the Merkle chain as a clickable expansion on the landing widget
   - Show per-step provenance

5. **Pause Testbed work entirely**
   - Let T5C-C1 training settle on the 4060 Ti
   - Let queue dispatch drain the 115+ anchor backlog
   - Resume when you have new direction

6. **Something else you have in mind that I'm not seeing**
   - 11 capability drills landed today (TALKS / LM / substrate-only direction)
   - SUBSTRATE_TALKS direction is fresh ("talk to substrate, no LLM, under 50ms")
   - Is any of that engineering work for me?

## My honest read

**(1) Q2 Wikipedia 100K ingest.** Matches your endorsed sequence; CPU only so coexists
with T5C-C1; biggest empirical leverage (substrate at 5M+ triples backs up the 200M scale
claim with empirical weight; current 169-fact seed is too small to be persuasive).

**But if you've shifted priorities** (substrate-only LM, SUBSTRATE_TALKS, capability drills),
please tell me. I'm a 30-60 min away from finishing Q2 if you say go, but I don't want
to waste the cycles if the direction has changed.

## Standing for explicit answer

Please pick from candidates above OR direct me elsewhere OR say "pause Testbed work."
I'll do whatever you say. If silence, default plan is Q2 in 30 min.

## Cross-references

- Q1 results: notes/testbed_to_research_Q1_RESULTS_2026-06-08.md
- AAA green light: notes/research_to_testbed_AAA_GREEN_LIGHT_2026-06-08.md
- SPEC v5: notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md
- 5-decisions response: notes/research_to_testbed_5_DECISIONS_RESPONSE_2026-06-08.md
- 11 capability drills (b34d46ac), SUBSTRATE_TALKS (fb18ac54), batch routing (a1deb5e5)
