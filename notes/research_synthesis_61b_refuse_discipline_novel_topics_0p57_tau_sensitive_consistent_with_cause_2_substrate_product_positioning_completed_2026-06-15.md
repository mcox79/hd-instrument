# Research (Director) -- SYNTHESIS: 61b refuse-aware scorer complete; refuse-discipline on NOVEL topics = 0.57 (4/7 at tau=0.70); hallucinations are near-threshold + semantically-related (cos 0.70-0.74) not wild; consistent with in-distribution gap 0.667; tau=0.75 -> 7/7 but Goodhart risk; M2 cleanup_margin proposed fix; substrate-product positioning on 56d now COMPLETE; 36th honest finding

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~08:45
**Re:** Exp-Dev 61b complete (commit pending). 36th honest finding. Per USER overnight full-auto + auto mode.

## Result (one line)

Refuse-discipline on 7 novel-concept gap questions (Galois / Riemann / Navier-Stokes / Yoneda / Banach-Tarski / FLT / four-color): **4/7 correct refusals = 0.5714 at tau=0.70**.

## Hallucinations are NEAR-THRESHOLD + SEMANTICALLY RELATED

3 hallucinations at cos 0.70-0.74:
- Riemann hyp (0.732) -> "Floor of imaginary parts..." (zeta-related atom)
- Yoneda lemma (0.740) -> "Functor" (genuinely related concept)
- four-color thm (0.704) -> "Coloring a circuit with 4 colors" (graph-coloring-related)

bge correctly finds the NEAREST substrate atom; the tau=0.70 gate (from 35a) is slightly permissive for novel topics. At tau=0.75 -> 7/7 refuse, but Goodhart risk if tuned on gap set.

## Substrate-product positioning on 56d -- COMPLETE TRIPLET

The 56d held-out (concept-disjoint blind; n=59 = 52 in-cov + 7 gap; SHA-256 locked) now characterizes substrate-product positioning across three dimensions:

1. **Recall on NEW concepts (in-coverage):** F1 = 0.2218 (M4d +0.005 over bge; bge generalizes, M4d mechanism does not -- per DECISION 62)
2. **Refuse on NEW topics (gap):** 0.5714 at tau=0.70 (TAU-tunable; near-threshold hallucinations are semantically-related, not random)
3. **Precision-recall tension (M1/M1c corroborated):** the 0.70-0.75 bge cosine band is where "related-but-absent" and "present" overlap; no clean separating tau exists

Comparison to in-distribution (q54-q65) refuse: 0.667 (5/7 gap on the prior held-out). 0.57 vs 0.667 is comparable; refuse-discipline on novel topics is NOT categorically different from in-distribution; both are tau-sensitive partial gating.

## Strategic implication (no new mechanism dispatched; existing M2 + M7 cover it)

- **M2 cleanup_margin (gated on Testbed C2+CHTV ship)** is the proposed mechanism for the precision-recall tension. It uses a DIFFERENT signal than bge cosine; if it ships and lifts refuse-discipline, the substrate gains a cleanly-separating gate. Status: pending Testbed ratify queue.
- **M7 rule-driven question-conditional weighting** (dispatched per DECISION 62b) MAY also help: weight bge top-K by question-class -- a Riemann-hypothesis-class question should require explicit zeta-related typed-graph evidence, not just bge proximity; if no such evidence, refuse.
- No NEW mechanism needed; existing queue addresses it.

## Honest read (Exp-Dev's framing endorsed)

- 0.57 refuse on novel topics is consistent with the long-standing Cause-2 finding (refuse-discipline is partial + tau-specific)
- Hallucinations are not wild; they are nearest-related-atom returns -- substrate's bge retrieves semantically-coherent neighbors
- The tau=0.70-0.75 overlap band is the substrate's persistent refuse-discipline limitation
- M2 cleanup_margin (different signal) is the architectural fix; M7 (question-conditional) is the immediate near-term lever

## Session tally

62 cumulative decisions. 36 honest corrections (Auditor 10 + Prover 23 + Director 3). 56d characterization (recall + refuse + precision-recall tension) COMPLETE. Substrate-product positioning on the cleanest possible held-out (concept-disjoint + blind + SHA-locked) now stands as a coherent three-claim package.

## Substrate-product positioning -- FINAL three-claim package (for canonical positioning)

**Recall claim:** "M4d capability-graph walk lifts held-out in-distribution-concept F1 from 0.148 (bge baseline) to 0.272 (+84pct paired delta; n=7; rigorous de-Goodhart; 8 augmentation experiments all fail to exceed). On concept-disjoint blind held-out (n=52; SHA-256 locked; 0 gold overlap) the substrate achieves F1 0.222 but M4d adds only +0.005 over bge -- the substrate's distinctive mechanism is an IN-DISTRIBUTION-CONCEPT AMPLIFIER, not a general new-concept retriever."

**Refuse claim:** "On novel-concept gap questions (n=7; Galois / Riemann / Navier-Stokes / Yoneda / Banach-Tarski / FLT / four-color; SHA-256 locked) refuse-discipline is 0.57 at tau=0.70 -- comparable to in-distribution gap refuse 0.667; hallucinations are near-threshold (cos 0.70-0.74) semantically-related atoms, not random; tau=0.75 lifts refusal to 7/7 but Goodhart risk if tuned on gap set."

**Soundness invariant claim (unchanged):** "Substrate maintains 100pct axiom termination (213/213); capability_preservation=1.0; CHTV-verified PROVABLY_EQUIVALENT integrations zero false-merges; L6-PROOF FINDER sound backward-chaining prover; CH-P6 LLM soundness gap (substrate 0 false-accepts vs Qwen-0.5B 3/12); refuse-what-cannot-prove 18th rule operational."

## Cross-references

- 61a DECISIVE result: commit `c52e126a` (DECISION 62)
- 61b commit pending
- DECISION 35a (tau=0.70 floor)
- M1/M1c bge cosine overlap finding
- M2 cleanup_margin gated on Testbed

## Safety / invariants

- ASCII only
- 22nd rule: 56d gap questions remain DO-NOT-INGEST
- 18th rule: substrate refuses what it cannot prove (3 hallucinations are NOT proofs; they are nearest-neighbor returns; substrate's prover-class capability is separate and 100pct sound)

---

**No new mechanism dispatch.** 61b corroborates existing findings; M2 + M7 cover the refuse-discipline gap; substrate-product positioning is COMPLETE on the 56d held-out.

Tag: 61b_REFUSE_0p57_TAU_TUNABLE_CONSISTENT_WITH_IN_DIST_GAP_POSITIONING_COMPLETE -- Research (Director)
