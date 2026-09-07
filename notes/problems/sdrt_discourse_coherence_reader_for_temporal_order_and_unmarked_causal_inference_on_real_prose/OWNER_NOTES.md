---
owner_verdict: DONE
---

SOLVED (pending your verdict) -- sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose  (opus 4.8 solver)

Write-up: notes/problems/sdrt_discourse_coherence_reader_for_temporal_order_and_unmarked_causal_inference_on_real_prose/SOLVED.md
Reverify (scaffold-free witness; recomputes every headline from source; NO hdlab write, Q111):
  .venv/Scripts/python.exe verification/test_sdrt_coherence_reader.py     # 14/14 PASS (~20s incl. CSKG load)

THE PROBLEM: the temporal + causal reasoners are both starved because the coherence relations that carry
unmarked temporal order and causal links are almost never spelled out. Build a glass-box SDRT-lite reader that
INFERS the relation (Narration/Result/Explanation/Background/Elaboration) from causal-world-knowledge (NOT
connectives) and feeds both reasoners. NO external LLM at inference.

WHAT'S PROVEN (clean CI-sep positives):
1. THE MECHANISM. Constructed Lascarides-Asher minimal pairs (n=48, no connectives): relation-4way 0.8125 vs
   connective-only 0.25 (+0.5625) and vs the info-free shuffled-label TWIN 0.29 (+0.5208, twin LOSES CI-sep);
   order-edit (reverse/forward/overlap) 0.875 vs iconicity 0.5 (+0.375). The reader infers the DICE relation +
   its temporal/causal consequence from world knowledge, not markers. (Research correction folded in:
   Background/Elaboration are aspectual, NOT causal -- routed to the aspect signal.)
2. A REAL-PROSE WIN ON THE DOMINANT CAUSAL CATEGORY. Aggressive drilling (owner push) found the located
   negative was a MISSING brain-faithful ENGINE: GOAL/intentional causation is 36% of TellMeWhy non-adjacent
   causes (the largest type; Trabasso goal chains, Malle reason-vs-cause), and the physics+psych simulator was
   BLIND to it (0.293). The substrate already had the goal organs (goal_register) it never composed. With the
   goal engine, on the GOAL-typed subset (n=92, its proper domain): goal-engine 0.5326 CI-sep over base 0.293
   (+0.239), topical 0.239 (+0.294), AND the twin 0.272 (+0.261) -- twin LOSES, on modern narrative gold.
3. COUPLING + NO-REGRESS. The causal_reasoner's graded_necessity over the inferred coherence-typed edges
   reproduces the cause-ID; temporal_reasoner.before() is BYTE-IDENTICAL with the channel off (10/10), overrides
   only a confident Explanation; sm.causal_links untouched.

"DO IT ALL" -- 8 tractable no-LLM levers built or ranked (4 research drills + built + measured):
   * GENERATIVE goal-object-as-patient means-end (computed-from-text) -- union with the CSKG typed-edge is the
     best full-population arm (0.309 vs base 0.277, beats the twin CI-sep +0.113, doubles coverage). SHIP.
   * A referential-coherence CONTROL proved the goal-gated object-match is MORE than Centering coherence (it
     beats the UNGATED version CI-sep; ungated over-fires and HURTS).
   * Two of my own "upgrades" were caught as DEGENERATE and corrected honestly: the Kintsch settling under
     uniform inhibition is a PROVEN mathematical no-op (Amari/Grossberg; 3/68 changes = ties); the scalar-
     relatedness means-end measures the WRONG AXIS (topicality; fired on 97%).
   * result-state matching = the valid general means-end but coverage-bound (needs a broad verb->effect model);
     multi-hop Trabasso goal-chains are distance-decayed and won't beat the strong nearest-antecedent baseline
     full-population; aspect/telicity + surprise/PE are legitimate but tangential/corpus-gated; selectional
     dropped. Full table in SOLVED.md.

THE WALL, LOCATED FROM ~6-8 ANGLES: every retrieval/structural lever is coverage-bound (CSKG cause-pairs 17.3%,
goal->action edges 34%, newswire flip-precision) or a confound; the ONE thing that would deliver a
full-population win is a GENERATIVE world-model (simulate the action forward, check the goal-STATE) -- the causal
reasoner's own P1, a large build shared by three consumers, needing the meaning channel.

CONTROLS: info-free twin LOSES on the mechanism control + goal subset (ties only on the full population -- the
honest bound); base-engine + topical + connective-only + adjacency floors all beaten CI-sep where a positive is
claimed; TB-Dense flip-selectivity null (the located negative); no-regression byte-identical; c-axis ablation
(content-only 0.000 -> engines add the directed signal).

HONEST COMPLETENESS BOUND (asked + answered): this is an EXCELLENT mechanism + investigation, NOT yet a complete
capability. The clean win is on a principled SUBSET (36% goal-typed) + constructed pairs; the FULL-population
unmarked-causal win is NOT achieved (best arm ties base, +0.031 not CI-sep), the temporal-override on newswire
is a located negative, and the completing lever (the generative world-model) is unbuilt. Tie the label to a
full-population lift on both slices and it is a strong PARTIAL; I filed SOLVED on the subset-positive + the bar's
"rigorous negative is a full pass" clause + precedent. Your call via owner_verdict.

FILES: experiments/_sdrt_coherence.py (the reader: physics + psych + goal engines, means-end + Kintsch functions)
+ 8 experiment cells (mechanism, TB-Dense override, TellMeWhy unmarked-causal, causation-type diagnostic,
goal-causation subset, deepen/c-axis, no-regress, kintsch integration, inverse-planning simulator, generative
means-end) + verification/test_sdrt_coherence_reader.py (14/14) + 4 RESEARCH notes. NO hdlab written (Q111).

>>> PRIORITY NEXT STEPS:
    P1 (COMPLETING LEVER, build): the GENERATIVE result-state world-model -- simulate action->result-state, check
       goal-state (Schank-Abelson RESULT links / Baker-Saxe-Tenenbaum). The one lever that makes the subset win a
       full-population win; the causal reasoner's shared P1; ONE large build serving temporal + causal + coherence;
       needs the meaning channel.
    P2 (SHIP NOW, Q111 default-OFF, impact-measured): land hdlab/coherence_reader.py with the goal engine +
       typed-edge + generative object-as-patient means-end (the three that do real work); wire confidence-gated
       into temporal_reasoner (Explanation override) + causal_reasoner (new inferred-edge field); measure live.
    P3: acquire a NARRATIVE flashback temporal gold (TB-Dense newswire is the wrong genre).
    P4: acquire GUM-eRST / RST-DT to validate the inferred relation directly (only GUM's conllu layer is on disk).
    DO NOT re-file: Kintsch settling under uniform inhibition (proven no-op); ungated referential coherence
       (over-fires); scalar-relatedness means-end (wrong axis); a multi-hop chain expecting a full-pop win;
       scaling RETRIEVAL to cross the coverage wall.

QUESTIONS: one -- SOLVED vs strong PARTIAL (above); science identical either way.
