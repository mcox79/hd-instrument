---
slug: the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse
status: INTEGRATED
review:
review_text:
---

# PROBLEM: the reader's PARSE FRONT-END — POS tagging, arc parsing, arc-eager transitions, and dependency-relation labelling — is a set of FROZEN SUPERVISED averaged-perceptrons trained once on a treebank that HARD-DECODE a single best structure and DISCARD the posterior. That is **5 of the 8 live NOT-brain-foundational organs** (`pos_tagger`, `arc_parser`, `arceager_parser`, `arc_labeler`, `parse_confidence`) and it is the **dominant UPCHAIN component** — every downstream organ (coref, meaning, roles, events, causal, ToM) reads its output, so its errors and its false confidence propagate everywhere. The brain does not batch-train a perceptron on labelled trees and commit to one parse: it parses **INCREMENTALLY and PROBABILISTICALLY**, maintaining a GRADED, globally-normalized distribution over structures that downstream reads WITH its uncertainty. Make the parser brain-foundational: route the reader's parse consumers through the GRADED probabilistic parse (the globally-normalized Matrix-Tree marginals the substrate already computes in `graded_parser`/`incremental_parser`), replacing the hard-decode — and confront the deeper acquisition question (a treebank-supervised perceptron vs syntax LEARNED FROM READING). Glass-box, NO external LLM at inference.

**slug:** `the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse` — **opened:** 2026-09-10 by the strategy session, from the BF-certification of the live set (the parser cluster is 5 of the 8 live NOT_BF organs) + the owner directive "get the substrate to 100% BF UPCHAIN first" + the reasoning-shown-not-end-to-end finding (reasoners beat floors on GOLD but slump to floor on real prose because EXTRACTION — the parse — is the shared wall). **status:** OPEN. Strategy lands any hdlab change (Q111, witnessed); the solver builds the route-through + the acquisition analysis + the witness in `experiments/`, `verification/`, and this folder. Glass-box, NO external LLM at inference (the invariant); a vetted static offline FOUNDATION asset is admissible, an external tool AT INFERENCE or a fitted convenient stand-in is a DEFECT that blocks.

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
When the reader works out a sentence's structure — who did what to whom — it runs a fixed rulebook it memorized once from a big hand-labelled dataset, picks the single best structure, and throws away every alternative plus any sense of how sure it was. The brain does not do that. It reads left-to-right, keeps several possible structures alive at once each with a likelihood, and commits only as the evidence builds — and it passes that uncertainty downstream, so later steps know which parts of the structure to trust and which are shaky. Our frozen rulebook is the single biggest non-brain-like piece of the front-end, and *everything* the reader does sits on top of it, so when it is wrong or falsely confident the mistake spreads into meaning, reference, roles, events, and reasoning. The task is to make the reader read the brain's way: parse into a graded, running distribution over structures, and let the rest of the reader consume that distribution with its uncertainty instead of one committed guess.

## 2. WHY THIS ONE — the deep root, under the HARD 100%-BF gate + the owner's "100% BF upchain first"
The parser cluster is **5 of the 8 live NOT_BF organs** (`pos_tagger`, `arc_parser`, `arceager_parser`, `arc_labeler`, `parse_confidence` — see `notes/bf_status_registry.jsonl`) and the **#1 shared wall** in `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` (Target 1, ~16 solutions consume it). It is the deepest UPCHAIN component: making it brain-foundational is the single move that most raises the substrate's overall fidelity, because every downstream organ inherits the parse. It is ALSO the accuracy frontier the reasoning line hit: reasoners beat floors CI-sep on GOLD parses but **slump to floor on real prose because EXTRACTION — the parse — fails** (the reasoning-shown-not-end-to-end finding). The specific non-brain-faithfulness: a frozen averaged-perceptron trained on a treebank, greedy/Viterbi **hard-decode** that discards the globally-normalized posterior. The brain's parse is incremental + probabilistic (graded marginals), and downstream reads the uncertainty. Two levels to confront, in order: (a) **route-through** the graded probabilistic parse the substrate already computes; (b) the deeper **acquisition** question — the brain does not supervised-train on a labelled treebank; is a treebank-trained parser an admissible offline FOUNDATION, or must syntax be learned-from-reading (the pri-2 directional-channel / distributional-acquisition direction)?

## 3. MEASURED vs INFERRED
- **MEASURED (on disk):** the graded parser's globally-normalized **Matrix-Tree MARGINAL beats the fitted logistic** `parse_confidence` on parse-arc reliability (obl_reliability_marginal AUC **0.782** > logistic — recorded in the registry note + the obl-spatial SOLVED). Prior piecemeal graded paths landed + verified (graded-POS posterior, arc-labeler fast path, arceager/arc double-parse consolidation, obl graded marginal). The hard-decode is the live default in the reader's parse consumers.
- **INFERRED (to prove or refute WITH A NUMBER):** that routing the reader's parse consumers through the graded probabilistic parse lifts a downstream extraction / board dimension **on REAL prose** (the extraction-wall hypothesis). That a treebank-supervised parser is / is not an admissible brain-foundational foundation. Do not assume either — measure.
- **🔬 RESEARCH (2026-09-10, vetted first-hand — full map in `RESEARCH_bf_acquisition.md`, READ IT):** the "frozen supervised hard-decode" hides **TWO orthogonal defects**, and the substrate has already run both halves of the answer: **(1) hard-decode vs graded-decode of a GIVEN scorer** — solvable NOW via the `graded_parser` route-through, NO acquisition dependency (do this Stage-0 regardless: globally-normalized posterior is more brain-faithful, Koo 2007 + Matrix-Tree marginals already in `graded_parser.single_root_marginals`/`matrix_tree_marginals`); **(2) supervised-trained vs self-taught scorer WEIGHTS** — the genuine acquisition question. Category induction from prediction is a **verified in-substrate HARD_PASS** (`experiments/exp_srn_predict_category_v1.py`, delta-AMI +0.060 over static counting, 3/3 seeds; Elman 1990). Structure/attachment induction from pure co-occurrence hit a **located ceiling that reproduces the field's documented right-branching trap** (`experiments/exp_predictive_selfsup_parser_v1.py` UAS 0.2716 < its own adjacency-right floor 0.2979; Klein&Manning 2004 naive right-attach 33.6% → DMV+EM-locality-prior 43.2%) — BUT the on-disk run used only ~3,000 of the ~12.5k UD-EWT train sentences with ZERO EM iterations, so it is UNDER-POWERED, not a proven failure. **RECOMMENDED CHEAP FIRST BUILD (no new organ, CPU-minutes):** re-run `exp_predictive_selfsup_parser_v1.py` at full UD-EWT scale with 2-3 EM re-estimation rounds (soft-count directional co-occurrence weighted by `graded_parser`'s own `single_root_marginals`) + a swept `prior_weight` (the Naseem 2010 category-level structural prior is already coded). This composes the just-landed **pri-2 directional grow-by-reading channel** (`reading_grounding_loop.track_directional_context_counts` — itself a Mintz/Redington-Chater-Finch frame-based acquisition channel) with the landed graded Matrix-Tree decode.

## 4. ALREADY TRIED / DO NOT REDO
- **Integrated already (do NOT re-add piecemeal):** `consume_the_graded_pos_posterior_uncertainty_aware…`, `add_the_arc_labeler_fast_scoring_path…`, `consolidate_the_arceager_and_arc_double_parse…`, `build_the_obl_spatial_defer_consumer_to_cash_the_graded_parser_marginal`. These added graded paths PIECEMEAL and proved the graded marginal is real, but the CORE reader still **hard-decodes** — the full route-through + the acquisition question are open. Do NOT re-derive a fast scoring path or re-benchmark the frozen perceptron against another frozen model.
- **Barred:** spaCy / any off-the-shelf parser / a neural treebank parser AT INFERENCE (NOT_BF, the invariant). The frozen avg-perceptron is the thing being REPLACED, not a floor to beat with a bigger supervised model.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/graded_parser.py` + `hdlab/incremental_parser.py` (the graded/incremental probabilistic parse — the REUSE target), `hdlab/parse_confidence.py` (the `obl_reliability_marginal` Matrix-Tree marginal), and the four frozen organs (`pos_tagger`, `arc_parser`, `arceager_parser`, `arc_labeler`). Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b parser entries + the four prior integrated parser SOLVEDs IN FULL. Read `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` Target 1 (every consumer that inherits the parse) + the reasoning-shown-not-end-to-end note. Enumerate the reader's parse call sites in `hdlab/situation_reader.py`. Run `python tools/substrate_map.py` / `tools/reader_capabilities.py` for the current wiring. Understand ALL the organs before proposing a change.

## 6. THE BAR (can-fail; a rigorous located-negative naming the exact ceiling WITH a number is a full pass)
Route the reader's parse consumers through the GRADED probabilistic parse (globally-normalized marginals) **replacing the hard-decode**, and SHOW a downstream extraction / board dimension lifts **CI-separated on REAL prose** (strongest real floor, info-free twin LOSING) — OR a rigorous LOCATED NEGATIVE naming exactly why the graded parse cannot beat the hard-decode on the reader's own metric (with a number, a fair test: the brain's actual mechanism faithfully built). EITHER outcome must also answer the ACQUISITION question with evidence: is a treebank-supervised parser an admissible offline FOUNDATION (justify computationally), or must the parse be learned-from-reading (name the brain-foundational acquisition mechanism + a first measured step)? Recall/downstream INVARIANT: any consumer not yet moved must be byte-identical; no external tool/LLM at inference.

## 7. FILES AND ENTRY POINTS
`hdlab/graded_parser.py`, `hdlab/incremental_parser.py`, `hdlab/parse_confidence.py`, `hdlab/pos_tagger.py`, `hdlab/arc_parser.py`, `hdlab/arceager_parser.py`, `hdlab/arc_labeler.py`; the parse call sites in `hdlab/situation_reader.py`; the board `experiments/exp_situation_model_qa_modern_v1.py` (the real-prose dims to move / not-regress); `notes/bf_status_registry.jsonl` (the 5 NOT_BF entries to retire/upgrade); prior work in `notes/problems/{consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection,add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost,consolidate_the_arceager_and_arc_double_parse_the_reader_now_parses_every_sentence_twice,build_the_obl_spatial_defer_consumer_to_cash_the_graded_parser_marginal}/`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT re-quote retired figures (`notes/reference_retired_claims_never_requote.md` — check before citing any number). Do NOT re-add a piecemeal fast scoring path (already integrated). Do NOT reach for spaCy or any external / neural treebank parser at inference (NOT_BF, blocks). Do NOT treat the frozen avg-perceptron as a baseline to beat with a bigger supervised model — it is the component being replaced. Do NOT claim "converged" on engineering variations; the bar is the brain's incremental probabilistic parse, faithfully built, with the acquisition question answered.
