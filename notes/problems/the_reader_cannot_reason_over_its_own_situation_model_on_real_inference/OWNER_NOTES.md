---
owner_verdict: DONE
---

════════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_reader_cannot_reason_over_its_own_situation_model_on_real_inference   STATUS: PARTIAL
(a rigorous, brain-grounded NEGATIVE that a NEAR-POSITIVE emerges from; the compound wall is fully decomposed,
mostly built-across, and the remaining fix is empirically de-risked. hdlab/ UNTOUCHED — proposed diffs only, Q111.)
REVERIFY:  .venv/Scripts/python.exe verification/test_reasoning_over_situation_model.py        -> 15/15 PASS
           .venv/Scripts/python.exe tools/problem_ledger.py --check                            -> malformed/incomplete: 0
════════════════════════════════════════════════════════════════════════════════════════════════════
ASKED: drive multi-hop/inference QA over the reader's OWN assembled situation model (who/what/when/where/why)
  through SituationReader.read() on a real inference benchmark, beating a SIMILARITY-only floor AND a NO-model
  floor CI-separated with the info-free (shuffled-model) twin LOSING + a graded multi-hop signature — OR, if the
  live model is too sparse/noisy, enumerate WHY (RECALL/parser vs reasoning-STEP). Glass-box, NO external LLM.
  A rigorous NEGATIVE is a full PASS. Instrument: MCScript2 before/after temporal-order QA (modern, 2-choice).

RESULT (n=1128 symmetric before/after via live read(); n=301 dev+test for the learned-schema/oracle arms):
  * REASONING MECHANISM WORKS (not the bottleneck): the episodic-timeline reasoner beats its shuffled-timeline
    twin CI-sep (0.548 vs 0.511, +0.036 [0.004,0.067]); on narration!=chronology it recovers true order 0.737
    vs text-order 0.263 (n=19); high-confidence retrieval 0.577 > chance.
  * DOES NOT BEAT FLOORS: vs SIMILARITY +0.021 (n.s.), vs NO-MODEL text-position +0.009 (n.s.).
  * RULED OUT, in order, each by a controlled experiment: (a) IN-PASSAGE RETRIEVAL (coverage 0.55->0.69, accuracy
    FLAT); (b) ABSTRACTION (precision-weighted/SR aggregator ablation PLATEAUS at chance: 0.505/0.514/0.523);
    (c) "commonsense-not-in-text" KNOWLEDGE gap — REFUTED (the events are NARRATED in the passage for 90-98% of
    questions); (d) EXTRACTION — REFUTED by the loop-closer (a clean spaCy supplied-grammar parse raised coverage
    0.36->0.74 but accuracy stayed at chance 0.446, ties twin).
  * THE FORK RESOLVED — the dominant residual is cross-narrative EVENT-ALIGNMENT, and it must be SEMANTIC:
    composing content_addressable_retrieval's additive partial-cue principle with GROUNDED meaning codes lifts the
    learned canonical script-order to 0.593 [0.531,0.654] and it BEATS its shuffled-order twin CI-sep (+0.111
    [0.019,0.200]) — a NEAR-POSITIVE (symbol/lexical codes only TIE the twin at 0.48). Not a clean full-bar pass:
    +0.074 over similarity (n.s.) and the twin-margin doesn't replicate on test alone.
  * WALL LOCALIZED TO EVENT-ALIGNMENT PRECISION: a coarse 12-d grounded cosine cannot pin WHICH of several
    SIMILAR script events a paraphrased cue means, so the order is read off the wrong pair ~40% of the time.
  * THE FIX IS EMPIRICALLY DE-RISKED (headroom drill): 98% of coarse-confusable event pairs are SEPARABLE by
    particle/argument/prep (only 2% irreducible); 51% of before/after questions hinge on a PARTICLE (in/out/up)
    the current verb+object code ignores.

BRAIN-FOUNDATIONAL ARC (6 drills; the opening move each step). PINNED: comprehension = inference over a situation
  model (Kintsch); online-bridging (who/what/when) is bound in, offline-commonsense is not. REUSED-verdict: building
  a canonical-order "map" is the brain's ONE general cognitive-map / relational-integration function (Behrens 2018;
  Constantinescu 2016; Whittington TEM 2020; transitive inference = Dusek & Eichenbaum) -> REUSE hdlab.transitive_
  ordering (validated to generalize to temporal script-order), do NOT reinvent. The residual wall = DG/CA3 PATTERN
  SEPARATION: event identity is a role-filler CONJUNCTION individuated by ARGUMENTS + PARTICLES, and our coarse
  holistic cosine has no separation stage. FIX (glass-box, no LLM): grounded CONJUNCTIVE event code + soft-AND
  (multiplicative) per-role kernel (add path/particle + 2nd arg; grounded fillers so paraphrase matches WITHIN a
  slot; PRODUCT across slots so a particle mismatch suppresses the wrong candidate). PROJECTED 0.59 -> 0.70-0.80
  (clean CI-sep positive); IRREDUCIBLE ceiling ~10-20% (truly-unordered pairs + state defaults + annotation noise);
  NOT human ~0.97. INDEPENDENT CORROBORATION: the Aug-2026 script_grain_acquisition_loop HARD_FAILED MCScript2 with
  the same signature (oracle beats baseline, learned no-better).

CONTROLS: shuffled-timeline twin (cell 1, loses CI-sep); MODEL_TEXTORDER ablation (isolates chrono reordering);
  retrieval rule-out (coverage up, accuracy flat); retrieval-confidence stratification; per-split + per-qtype;
  proper random-order schema twin; the precision/SR aggregator ablation (plateau); the oracle clean-extraction
  loop-closer; symbol-vs-semantic alignment contrast; both-decide twin comparison; split-half schema self-consistency
  (0.82); the 90-98%-in-passage partition; the 98%-separable headroom drill. Leakage: schema induced from TRAIN
  narratives only, over event TYPES (189/194 test + 162/162 dev scenarios seen in train).

KEY REALIZATIONS: (1) REUSE-not-reinvent; ask "reused or standalone?" FIRST (owner's steer) -> transitive_ordering
  was already the cognitive-map organ. (2) A controlled experiment must be allowed to REFUTE your own prior
  conclusion — the loop-closer killed my "just fix the parser," the fork-resolver flipped a tie-with-twin into a
  beats-twin near-positive. (3) The alignment had to be SEMANTIC, not symbolic (symbol codes over-separate/tie;
  grounded under a soft-AND separates). (4) DIAGNOSE a negative before labelling it: a too-weak twin (premise-flip,
  which transitive settling heals) once hid the real result. (5) PRIOR-WORK check is experiment_index, not just
  drills — I re-derived a known negative (script_grain HARD_FAIL); the convergence is now a strength.

AUDIT UPDATE (fold into BRAIN_FOUNDATIONAL_AUDIT.md sec 2b): situation_reader temporal reasoning driven+measured
  LIVE end-to-end on a real benchmark — the episodic WHEN dimension is a validated reasoning signal but not
  sufficient for MCScript2 inference. transitive_ordering generalizes to temporal script-order (PINNED cognitive
  map). NEW compound-wall verdict: the reasoning STEP is sound; the binding residual is SEMANTIC cross-narrative
  event alignment (DG pattern-separation), NOT extraction (loop-closer refuted that) and NOT a knowledge gap
  (90-98% in-passage). Correct any prior "extraction is THE binding wall" note.

ADJACENT COMPONENTS / FOLLOW-ONS: (1) build the soft-AND conjunctive event aligner (compose bound_event_backbone's
  role-filler structure + content_addressable_retrieval's graded match + a grounded soft-AND kernel; keep
  transitive_ordering as read-out) — the highest-leverage build, de-risked to ~0.70-0.80. (2) frame_induction
  recomputes a >90s program-induction search EVERY process (in-memory cache only) -> persist to disk. (3)
  timeline_register de-dupes events by verb lemma ("got in" vs "got out" collapse) -> key by (lemma, sent_idx).

FILES (glass-box, NO LLM; hdlab/ UNTOUCHED): experiments/_situation_inference_live.py (driver: passage->CoNLL->
  read() + MCScript2 loader + frame_induction perf pre-seed); experiments/exp_situation_model_inference_mcscript_v1
  .py (cell 1: temporal reasoner + floors + twins + retrieval rule-out + knowledge-gap decomposition); experiments/
  exp_learned_script_order_prior_mcscript_v1.py (cell 2: learned script-order via REUSED transitive_ordering + the
  aggregator ablation); experiments/exp_oracle_extraction_script_order_mcscript_v1.py (cell 3: loop-closer clean
  extraction + object AND grounded-semantic alignment arms); verification/test_reasoning_over_situation_model.py
  (15/15 scaffold-free witness); notes/problems/<slug>/{SOLVED.md + 5 research notes}; data/exp_*/metrics.json (3).

TLDR (plain): I made the reader answer real "did X happen before or after Y" questions by reasoning over the mental
  model it builds while reading. The reasoning itself works (scramble its sense of time and it fails; tell a story
  out of order and it still recovers the sequence), but it can't beat simple baselines — and through six drills I
  found exactly why, twice overturning my own guess. It is NOT that the answer isn't in the text (it is, 90%+ of the
  time) and NOT the parser (a clean professional parse didn't fix it). The real bottleneck is telling apart similar
  events — "get OUT of the shower" vs "get IN," "watch" vs "push" — which the brain does with a dedicated
  separation circuit and which our coarse meaning-vector can't. I reused our existing "ordered-map" machinery, added
  meaning-based event-matching, and it became a genuine signal that beats a scrambled-order control and reached ~59%
  (vs ~52% baselines) — a near miss, not a clean win. Then I proved the fix has room: 98% of the events it confuses
  are actually distinguishable by the word details (like in/out) it currently ignores, and half the questions turn
  on exactly those details. So the machine is built, brain-faithful, and one well-scoped upgrade (separate similar
  events by their arguments/particles) away from a clean win — with an honest ~10-20% ceiling of genuinely
  unanswerable questions.
QUESTIONS: none.
NEXT STEPS: (1) build the soft-AND conjunctive event aligner (de-risked, projected clean positive) — isolated
  precision probe first as the can-fail gate, then end-to-end; (2) the two low-cost substrate fixes above.
════════════════════════════════════════════════════════════════════════════════════════════════════
