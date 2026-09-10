---
priority: 2
slug: scale_the_reading_learned_arc_scorer_the_brain_foundational_parser_acquisition
status: OPEN
review:
review_text:
---

# PROBLEM: the parser is a FROZEN SUPERVISED avg-perceptron trained on a treebank — the deepest NOT-brain-foundational cluster (5 of the 8 live NOT_BF organs) and the SHARED EXTRACTION WALL that multiple integrated solvers route their residuals to (force-dynamics harm/help's `from`-clause attach + rare-noun mistag; common-noun coref's span-head selection; the reasoning line slumps to floor on real prose because EXTRACTION fails). The in-flight parser solver (`the_parser_is_a_frozen_supervised_hard_decode...`, pri-3) settles the read-out (route through the graded probabilistic parse) and PROVED — but filed as a follow-on — the real brain-foundational fix for the ACQUISITION half: a **READING-LEARNED arc scorer** whose weights are self-taught from raw text (statistical/predictive syntax acquisition; Saffran; Klein-Manning DMV + EM locality prior; the substrate's own directional grow-by-reading channel + graded Matrix-Tree decode), NOT gradient-trained on labelled trees. The proven-viable prototype (`exp_predictive_selfsup_parser_v1`) was run UNDER-POWERED (~3,000 of the ~12.5k UD-EWT train sentences, ZERO EM iterations). SCALE + LEXICALIZE it: full-corpus, 2-3 EM re-estimation rounds soft-counting directional co-occurrence weighted by `graded_parser.single_root_marginals`, swept `prior_weight` (Naseem 2010 category-level structural prior) — and A/B the reading-learned scorer against the frozen supervised one on the reader's OWN metric. Show it matches-or-beats the supervised parser WITHOUT a treebank at inference — the brain-foundational replacement for the parser cluster's supervised ROOT — or a rigorous located negative. Glass-box, NO external LLM.

**slug:** `scale_the_reading_learned_arc_scorer_the_brain_foundational_parser_acquisition` — **opened:** 2026-09-10 by the strategy session, from the in-flight parser solver's filed follow-on ("the reading-learned arc scorer — mechanism now PROVEN, not just hypothesized; scale/lexicalize it; the biggest lever") + the folded BF-acquisition research (`RESEARCH_bf_acquisition.md`: category-induction-from-prediction is a verified in-substrate HARD_PASS; structure-induction hit an UNDER-POWERED located ceiling). **status:** OPEN. The SUCCESSOR to pri-3 (pri-3 settles the graded read-out; THIS builds the learned-from-reading acquisition it scoped). Strategy lands any hdlab wire (Q111, witnessed). Glass-box, NO external LLM; a treebank is admissible only as an OFFLINE analysis/eval asset, NOT as the inference-time scorer's supervised trainer.

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL, and spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model
> are NOT brain-foundational -- never reach for a convenient/easy tool without careful consideration (a vetted static
> offline FOUNDATION asset is admissible; an external tool AT INFERENCE or a fitted/convenient stand-in is a DEFECT
> that BLOCKS).**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader figures out sentence structure with a rulebook it memorized once from a big hand-labelled dataset. The brain never saw a labelled dataset — it learned to parse from raw exposure: which words predict which, what attaches to what, refined over everything it reads. A prototype that learns the parser's scoring from raw text (no labels) already works in principle, but it was only given a tiny slice of the training text and zero refinement passes, so it under-performed. This problem is to give it the full text and the refinement passes the brain-equivalent process needs (a few rounds of re-estimating what-attaches-to-what, weighted by how confident the current parse is), then check it against the memorized rulebook on the reader's own task. If a from-reading parser matches or beats the memorized one, we can retire the single deepest non-brain-like part of the front-end — the supervised training — because the parse would then be *acquired* the way the brain acquires it.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate
The parser cluster is 5 of the 8 live NOT_BF organs; pri-3 fixes the READ-OUT (hard-decode → graded posterior) but the deeper defect is the SUPERVISED ACQUISITION (gradient-trained on a treebank — the brain does not do this). It is the SHARED WALL: force-dynamics harm/help, common-noun coref, and the reasoning line all route their residuals to the parser (the reasoners beat floors on GOLD parses but slump to floor on real prose because EXTRACTION fails). The BF acquisition path is PROVEN-VIABLE but under-run: category-induction-from-prediction is a verified in-substrate HARD_PASS (`exp_srn_predict_category_v1`, delta-AMI +0.060, Elman 1990); structure-induction hit the field's documented right-branching trap (`exp_predictive_selfsup_parser_v1` UAS 0.2716 < adjacency 0.2979; Klein-Manning 2004 naive 33.6% → DMV+EM 43.2%) BUT on only ~3k/12.5k sentences with ZERO EM. The fix the literature prescribes (category-level structural prior + EM iteration, already coded as `prior_weight`) was never run at scale. Scaling it is the smallest, cheapest, highest-leverage move to make the parser brain-foundational at its root.

## 3. MEASURED vs INFERRED
- **MEASURED (on disk):** `exp_srn_predict_category_v1` category induction from prediction = HARD_PASS (+0.060, 3/3 seeds); `exp_predictive_selfsup_parser_v1` reading-learned arc scorer UAS 0.2716 at ~3k sentences, 0 EM (< adjacency 0.2979 — the underpowered located ceiling); the graded Matrix-Tree decode + directional grow-by-reading channel are landed.
- **INFERRED (to prove or refute WITH A NUMBER):** that at FULL UD-EWT scale + 2-3 EM rounds (soft-counting weighted by `graded_parser.single_root_marginals`) + swept `prior_weight`, the reading-learned scorer matches-or-beats the frozen supervised scorer on the reader's OWN metric (a downstream extraction / dependency dim), info-free twin LOSING. Do not assume scale closes it; report the scale + EM curve.

## 4. ALREADY TRIED / DO NOT REDO
- Do NOT re-run at the under-powered ~3k/0-EM config (that IS the located ceiling). Do NOT re-derive the graded parser or the directional grow-by-reading store (landed — REUSE). Do NOT re-benchmark the frozen supervised scorer against another SUPERVISED model — the point is the LEARNED-FROM-READING replacement.
- Barred: spaCy / any off-the-shelf or neural treebank parser at inference. A treebank is admissible ONLY as an offline EVAL/analysis asset (to score UAS), never as the inference-time scorer's supervised trainer.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `experiments/exp_predictive_selfsup_parser_v1.py` (the reading-learned scorer prototype — the scale/EM/prior_weight knobs), `experiments/exp_srn_predict_category_v1.py` (the category-induction HARD_PASS), `hdlab/graded_parser.py` (`single_root_marginals`/`matrix_tree_marginals`) + `hdlab/incremental_parser.py`, `hdlab/reading_grounding_loop.py` (`directional_context_lemmas`). Read the in-flight `the_parser_is_a_frozen_supervised_hard_decode...` PROBLEM + its `RESEARCH_bf_acquisition.md` + `SCOUTING_blast_radius.md` IN FULL (this is its filed successor). Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` parser entries + `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` Target 1. Run `python tools/substrate_map.py`.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
Scale + lexicalize the reading-learned arc scorer (full UD-EWT, 2-3 EM rounds soft-counting directional co-occurrence weighted by `graded_parser`'s `single_root_marginals`, swept `prior_weight`), and SHOW it **matches-or-beats the frozen supervised scorer on the reader's OWN metric** (a downstream extraction / dependency board dim, info-free twin LOSING) WITHOUT a treebank at inference — OR a rigorous LOCATED NEGATIVE naming exactly where the reading-learned acquisition ceiling is and why (with a number, at FULL scale + EM — not the underpowered config; the brain's actual mechanism faithfully built). INVARIANT: recall path byte-identical; no external tool/LLM at inference.

## 7. FILES AND ENTRY POINTS
`experiments/exp_predictive_selfsup_parser_v1.py`, `experiments/exp_srn_predict_category_v1.py`; `hdlab/graded_parser.py`, `hdlab/incremental_parser.py`, `hdlab/reading_grounding_loop.py` (the directional store); the parse consumers in `hdlab/situation_reader.py`; the board `experiments/exp_situation_model_qa_modern_v1.py` (who_did_what / extraction dims); the in-flight parser problem folder (`notes/problems/the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse/` — `RESEARCH_bf_acquisition.md` + `SCOUTING_blast_radius.md`).

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use a treebank (or spaCy / a neural parser) as the inference-time scorer — labelled trees are an offline eval asset only. Do NOT re-run the underpowered ~3k/0-EM config + call it a ceiling. Do NOT overlap the in-flight pri-3's graded-read-out core — THIS problem is the ACQUISITION scale-up (the learned scorer), pri-3's filed successor. Do NOT claim "converged" on engineering variations; the bar is a reading-learned scorer matching-or-beating the supervised one at full scale — or a numbered located negative.
