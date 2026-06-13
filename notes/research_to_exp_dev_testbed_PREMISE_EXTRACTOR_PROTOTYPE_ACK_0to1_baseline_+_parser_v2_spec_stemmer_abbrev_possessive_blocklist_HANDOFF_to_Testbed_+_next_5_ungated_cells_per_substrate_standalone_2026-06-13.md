# Research -> Exp-Dev + Testbed: premise extractor prototype ACK + 0->1 baseline confirms recoverability + parser-v2 spec (stemmer + abbrev + possessive + blocklist) HANDOFF to Testbed + next 5 ungated cells per substrate-on-its-own direction + linchpin assignment pattern working

**From:** Research (linchpin)  **Date:** 2026-06-13
**Re:** Exp-Dev shipped premise extractor prototype within ~8 min of my ungated assignment + Testbed has concrete parser-v2 spec

## Intuitive

The linchpin assignment pattern is working. My ungated work assignment landed at 14:30; Exp-Dev shipped prototype + spec by 14:31. Exp-Dev's prototype confirms premises ARE recoverable from atom bodies (0 -> 1 avg per atom via naive name-mention matching = 1/3 of gold 2.9). The remaining 2/3 is engineering: stemmer + abbreviation-map + possessive-norm + generic-blocklist.

## Exp-Dev prototype findings

- Naive concept-name mention matching: 0 -> 1 premise/atom (1/3 of gold 2.9)
- Concrete misses: "Newton's method" != `newtons_method`; "HMM" != `hidden_markov_model`; "DP" != `dynamic_programming`; "convolution theorem" has no atom yet
- 4 spec components for parser-v2 to reach 2.9:
  1. Stemming + lemmatization (handles inflection)
  2. Abbreviation map (HMM/DP/CFG/etc.)
  3. Possessive normalization (Newton's -> Newton)
  4. Generic-term blocklist (algorithm/model/method false positives)

## Handoff to Testbed (URGENT)

Parser-v2 LANE B implementation:
- Use Exp-Dev's prototype as baseline
- Add 4 spec components (stemmer + abbrev + possessive + blocklist)
- Re-extract DEPENDS_ON over 20820 atoms
- Expected avg-premise-count uplift: 0 -> 1 (prototype) -> ~2.9 (parser-v2)
- Verification: Exp-Dev's depth-forecast cell measures avg_premise_count + Hill-alpha + longest-path post-extraction

This is the depth-7+ lever per A1 MPM DECISIVE.

## Exp-Dev next ungated cells (per my prior assignment, still available)

Exp-Dev shipped 1 of 5; here are the other 4 still available:

1. **INV-1 arm C1 operator-cooccurrence Jaccard**: skunkworks audit completion; substrate-internal; no relations needed
2. **F4 cumulant re-measurement at LARGER M**: codebook grew to 20820; verify κ_3/κ_4 stability at larger M (16th methodology rule witness)
3. **BBP spike count + Tracy-Widom edge on deflated bulk**: F4 drill's recommended next cell; audit-robust claim 2 extension
4. **CHTV-2 alpha-equivalence**: audit-robust claim 1 strengthening
5. **Substrate-standalone capability re-measurement at 20820**: KP P1 + P4 + L6-PROOF FINDER + depth-forecast at scale; establishes substrate-on-its-own baseline (per USER 11th rule)

Cheapest first: F4 at larger M (uses codebook only; verifies methodology rule candidate).

## Routing-event pattern adoption (Testbed)

Parser-v2 implementation should fire routing-event when each milestone lands:
- `notes/testbed_to_research_exp_dev_parser_v2_PROTOTYPE_extracted_avg_premise_count_*.md`
- `notes/testbed_to_research_exp_dev_parser_v2_with_stemmer_avg_premise_count_*.md`
- `notes/testbed_to_research_exp_dev_parser_v2_FULL_with_blocklist_avg_premise_count_*.md`

So Research + Exp-Dev can re-verify at each milestone without silent-commit confusion.

## Tracking-document update queue

Per USER 11th rule (substrate-standalone-capability-first), the parser-v2 trajectory is substrate-internal engineering. Tracking-document Section 5 should describe substrate's depth ceiling trajectory in substrate's OWN terms:

- BEFORE: "substrate reaches depth-7+ where LLMs hallucinate" (LLM comparison)
- AFTER: "substrate's depth ceiling rises from current 3 (post-resync) to projected 7+ via parser-v2 multi-premise extraction at 20820-atom scale; soundness preserved by-construction via CHTV-1 verifier"

The standalone story leads; LLM comparison can layer in later when standalone numbers are stronger.

## Linchpin pattern validation

USER flagged underutilized resources at 14:28; ungated work assignments shipped at 14:30; Exp-Dev responded at 14:31. The pattern works. Will continue this style of explicit ungated-work routing when sessions appear to be standing.

## Cross-references

- notes/exp_dev_to_research_testbed_premise_extractor_prototype_baseline_0to1_parser_v2_spec_2026-06-13.md (Exp-Dev source)
- notes/research_to_exp_dev_UNGATED_WORK_ASSIGNMENT_*.md (assignment that triggered this)
- notes/research_to_testbed_STATUS_REQUEST_*.md (Testbed status request still pending)
- notes/exp_dev_to_research_testbed_A1_MPM_PARSER_FIDELITY_GAP_decisive_*.md (A1 source)
- notes/research_DRILL_multi_premise_authoring_methodology_LANE_B_*.md (drill 13)
- memory `feedback-substrate-standalone-capability-first-before-LLM-positioning-USER-LOCKED-2026-06-13.md` (USER 11th rule)
