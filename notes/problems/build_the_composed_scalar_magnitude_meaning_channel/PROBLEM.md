---
priority:
review: EXCELLENT
review_text: "Re-verified FIRST-HAND (verify_composed_magnitude_channel.py ALL CHECKS PASS). The composed magnitude channel (dimension-routed grounded ORIENTED place code + FPE-log Weber comparator) beats the strongest single sub-op (pooled 0.441 vs 0.359, +0.081 CI-sep) AND the incumbent cosine (0.071) CI-separated; the word-class operation-ROUTER beats a gloss-only reader (0.616 vs 0.424) AND a magnitude-only reader (0.339) with NO N/V regression; FPE-log preserves Weber on-substrate (LOG ratio-CV 0.000 vs LINEAR 0.686), comparator unbind decodes log-ratio corr 1.000. As a COMPARISON system it beats the incumbent CLEANLY: relative-comparison 0.758 vs 0.552 (+0.206 CI-sep), Moyer distance effect +0.340, semantic-congruity AUC 1.000 where the incumbent gloss cosine INVERTS to 0.215. The solver CORRECTED the brief to be MORE brain-faithful (pole+degree are ONE oriented place code, not three stacked ops -- opponent pools->peaked code->oriented axis). Honest deflations upheld (the sub-op win is concreteness-routing; gate is coarse; markedness/FPE-log's value is comparison+Weber not static recovery; frontier is DATA-blocked). ACCEPTED; the hdlab landing is a substantial multi-module port (queued, careful build)."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-28 (strategy session; grade EXCELLENT; owner-DONE + authorized in-session)
> **Re-verified FIRST-HAND** (`verification/verify_composed_magnitude_channel.py`, ALL CHECKS PASS — ran it myself).
> **Result:** the composed magnitude "ruler" (dimension-select → grounded ORIENTED place code → markedness fine-degree →
> FPE-log Weber comparator) beats every single sub-op (pooled 0.441 vs best sub-op 0.359, +0.081 CI-sep) AND the incumbent
> cosine (0.071) CI-separated; the word-class operation-ROUTER beats BOTH a gloss-only reader (0.616 vs 0.424, misses
> magnitude) AND a magnitude-only reader (0.339, destroys N/V similarity) with the N/V read-outs IDENTICAL under routing
> (exact no-regression). Substrate: FPE-log preserves Weber (LOG ratio-CV 0.000 vs LINEAR 0.686), the comparator `unbind`
> decodes the log-ratio at corr 1.000, a different-pole code decorrelates.
> **Argument audit (where the win is CLEAN):** as a COMPARISON system (the brain's actual use of magnitude), it beats the
> incumbent decisively — "which is more X" 0.758 vs 0.552 (+0.206 CI-sep), the Moyer distance effect +0.340, and it
> separates graded comparison from categorical opposition at AUC 1.000 where the incumbent gloss cosine INVERTS (0.215 —
> it ranks antonyms as MORE similar than same-pole pairs). Info-free twins lose (random-axis, shuffled-degree, structure-free
> FPE). **To the solver's credit:** a research drill on the composition CORRECTED the brief to be MORE brain-faithful — pole
> and degree are NOT two stacked operations; the brain fuses them into ONE oriented place code (opponent pools → peaked
> log-Gaussian code → oriented axis: Roitman/Nieder/Verguts&Fias/SNARC), and the disk confirms it (within-scale oriented
> ordering 0.72 ≈ markedness 0.77). An opponent-pool readout drill found the linear projection MONOTONE-EQUIVALENT (the
> place-code stage is load-bearing, the opponent-readout stage is not for recovery) — a rigorous honest negative.
> **Honest deflations upheld (why it's excellent-not-overclaimed):** the CI-win over the best single sub-op is driven by ONE
> dimension (concreteness routing to the perceptual axis; the 3 evaluative dims tie antonym-SemAxis by construction) — the
> decisive claims are the +0.40 over the incumbent and the comparison-system win; the gradability gate is coarse (sharper
> gate = has_antonym-or-satellite AND NOT pertainym-relational, built here); markedness/FPE-log do NOT improve static
> recovery (their value is fine ordering + the Weber comparison code); the deeper frontier (comparison-class re-anchoring,
> negativity bias, congruity RT) is DATA-blocked, not mechanism-blocked.
> **hdlab LANDING — ACCEPTED, QUEUED as a careful multi-module port (NOT rushed):** the `ScalarMagnitudeChannel` imports FOUR
> experiment modules (FPE fractional-power encoding, the antonym/perceptual axis machinery, Warriner/Lancaster/freq loaders)
> that must be relocated into `hdlab/` cleanly first (an hdlab organ cannot import `experiments/`). The landing = (1) port
> FPE + the semantic-axis machinery + the offline loaders to hdlab; (2) ADD `hdlab/scalar_adjective_operation.py`
> (`ScalarMagnitudeChannel`); (3) UPGRADE `hdlab/quality_relation.py` Ch.B LINEAR→FPE-log + pole/dim binding + the
> grounded-degree lexicon; (4) ROUTE the meaning read-out by word class (gradable adj → magnitude; else gloss) with the
> sharper gate; wire dimension-selection to `hdlab/semantic_control`. This is the immediate-next dedicated landing; the
> learner problem's substrate-validation half depends on it. AUDIT UPDATE folded (§2b). Priority cleared.

# PROBLEM: the scalar-adjective magnitude operation is PROVEN PIECE-BY-PIECE but not COMPOSED — build the ONE deployable magnitude meaning channel (dimension/pole + markedness degree + FPE-log Weber code + per-dimension grounding) with operation-routing by word class, validated composed, proposing the hdlab diff

**slug:** `build_the_composed_scalar_magnitude_meaning_channel` - **opened:** 2026-08-27 by the strategy session
(the earned build from the integrated `the_meaning_read_out_is_one_operation_where_the_brain_has_three` (SOLVED/EXCELLENT):
that solver PROVED each sub-operation IN ISOLATION — SemAxis dimension/pole (valence 0.724), markedness degree
(frequency/AoA orders intensity), the FPE-log Weber code (validated vs 240k human number-comparison trials), Lancaster
perceptual grounding (concreteness 0.26→0.53) — but did NOT COMPOSE them into one deployable magnitude channel, nor
build the operation-router, nor upgrade the substrate FPE code. This is that large multi-part BUILD).
**status:** OPEN - **a BUILD problem (owner 08-27: use problems for large projects). Compose the proven pieces into one
magnitude meaning channel + operation-routing; validate the COMPOSED thing; propose the exact hdlab diff. Strategy LANDS
the hdlab (Q111); you build + validate in `experiments/` and propose the diff.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. The pieces are proven; the composition +
> substrate FPE-log upgrade + live-reader validation are the remaining large build. Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The reader needs a "ruler" operation for describing-words that come in degrees (hot/cold, good/bad, big/small). We already
PROVED, separately, every part the brain uses for this: WHERE a word sits on the scale (a geometric axis), HOW INTENSE it
is (how rare/late-learned the word is — markedness, not geometry), the "stretched ruler" where big amounts blur together
(Weber's law, built as a log-encoding in our own maths and validated against 240,000 human trials), and that different
scales need different anchors (feelings from opposite-word pairs; physical scales from perceptual strength). But those are
SEPARATE proofs on separate benchmarks. Nobody has BUILT them into ONE working "ruler" the reader can call — nor the
switch that routes each word to the RIGHT tool (nouns/verbs to the definition channel, gradable adjectives to the ruler).
This builds that one composed channel and the router, and shows the composed thing works.

## 2. WHY THIS ONE

- **The pieces are proven; the COMPOSITION is the missing, load-bearing build.** A pile of isolated proofs is not an
  organ the reader can use. The magnitude channel must be ONE callable operation (dimension → pole → degree → Weber code)
  with a word-class router.
- **It is the meaning line's remaining fidelity win** (the one class the incumbent cosine cannot serve).
- **It composes existing landed machinery** (FPE=self-bind in `hdlab/binding`; `hdlab/quality_relation` Ch.B; the
  conceptual channel; the WordNet-antonym valence organ; the semantic-control router) — wire-don't-island.

## 3. HOW THE BRAIN DOES THIS (frame + discipline — all PINNED by the integrated p3 work; COMPOSE, don't re-derive)

The magnitude read-out is a PIPELINE, each stage PINNED + proven in isolation (read the p3 SOLVED for the evidence):
SELECT the scale (semantic control; LIFG/pMTG) → DIMENSION/POLARITY = a geometric bipolar axis ANCHORED by the explicit
antonym relation (Walsh ATOM signed magnitude; per-dimension, INDEPENDENT axes — one global ATOM axis is refuted) →
OPPOSITION from the explicit relation (NOT the projection — raw geometry inverts antonyms) → DEGREE/INTENSITY from
MARKEDNESS (frequency/AoA — Horn/Zipf/Greenberg; the projection is at its random floor for fine ordering) → encode the
degree as FPE(LOG(degree)) in FHRR (the tuned Weber number-neuron code; the log PINNED by Laughlin efficient coding; the
reference-point comparator = a native `unbind`). Anchor EVALUATIVE dims (valence/dominance) from WordNet antonym poles,
DENOTATIONAL dims (concreteness/size) from Lancaster PERCEPTUAL strength.

**OUR-INVENTION-UNDER-TEST (compose + sweep, don't re-adopt):** how the sub-ops COMPOSE into one channel (does the
composed magnitude channel beat each sub-op alone / the incumbent cosine on a per-class task?); the gradability GATE (the
router's can-fail trigger); the grounded-degree lexicon feeding FPE-log. Reuse `hdlab/binding` (FPE/unbind),
`hdlab/quality_relation` Ch.B (upgrade linear→log), `hdlab/conceptual_meaning` (nouns/verbs), `hdlab/wordnet_polarity_propagation`
(opposition), `hdlab/semantic_control` (scale selection). Do NOT: replace the verb gloss op with VerbNet (net-neutral,
tested); use one global ATOM axis (refuted); read fine degree from the projection (tested-negative — use markedness).

## 4. MEASURED vs INFERRED

**MEASURED (from `the_meaning_read_out_is_one_operation_where_the_brain_has_three`, integrated 2026-08-27, EXCELLENT):**
each sub-op IN ISOLATION — SemAxis dimension recovery (valence 0.724 vs incumbent 0.165, random 0.067, CI-sep; Moyer
distance effect); markedness orders intensity CI-above chance where SemAxis is at its random floor; FPE-log Weber code
scale-invariant + validated vs 240k human number-comparison trials (RT rho 0.96, beats a difference kernel CI-sep);
Lancaster grounding concreteness 0.26→0.53 CI-sep; per-class specificity (cosine wins nouns/verbs, loses adjectives);
dimension selection by context 0.661 vs MFS 0.529 CI-sep. All on disk in `experiments/exp_*` + `data/`.

**INFERRED / OPEN (this problem):**
- Does the COMPOSED magnitude channel (all sub-ops chained: select→axis→opposition→markedness-degree→FPE-log) beat (a) the
  incumbent single cosine AND (b) the best SINGLE sub-op alone, on a per-word-class comprehension/similarity task,
  CI-separated, with info-free twins (random axis / shuffled degree / structure-free FPE) LOSING?
- Does operation-ROUTING by word class (gradability gate; nouns/verbs/classificatory-adj → gloss; gradable/evaluative adj
  → the magnitude channel) beat a single-operation read-out end-to-end, without hurting the classes the cosine already wins?
- Does upgrading `quality_relation` Ch.B linear→FPE-log (with a grounded-degree lexicon) preserve the Weber properties on
  the substrate + feed the composed channel?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT re-prove the sub-ops in isolation (DONE, CI-sep). COMPOSE them + measure the composed channel + the router.
- Do NOT replace the verb gloss op with VerbNet (net-neutral, tested-negative); keep verbs/nouns/classificatory-adj on the gloss.
- Do NOT use one global ATOM axis (refuted); do NOT read fine degree from the geometric projection (markedness is the signal).
- Query `experiment_index.py query "magnitude"`, `query "adjective"`, `query "fpe"`; read the p3 SOLVED + its
  `experiments/exp_perclass_*`, `exp_fpe_log_*`, `exp_adjective_*` + `hdlab/quality_relation.py` + `hdlab/binding.py`
  BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Reproduce the sub-op numbers (`verification/verify_perclass_meaning_operations.py` PASS; the `exp_fpe_log_*` gates).
- Read `hdlab/quality_relation.py` Ch.B (the LINEAR FPE-axis machinery to upgrade) + `hdlab/binding.py` (FPE=self-bind,
  comparator=unbind) — confirm how the composed channel plugs in.
- Recompute every floor (incumbent cosine; each single sub-op; the info-free twins) on the composed task's OWN population.

## 7. THE BAR

Build the COMPOSED magnitude meaning channel + the word-class operation-router, and validate the COMPOSED thing:

- **The composed magnitude channel must beat BOTH the incumbent single cosine AND the strongest SINGLE sub-op alone on a
  per-word-class task CI-separated over its UPPER bound, with info-free twins (random axis / shuffled degree /
  structure-free FPE) LOSING CI-separated.** Report CI half-width + null p95. The FPE-log magnitude code must preserve its
  Weber property on-substrate (scale-invariant kernel) after the Ch.B linear→log upgrade.
- **Operation-ROUTING must beat a single-operation read-out end-to-end** (gradable adj → magnitude, else gloss) WITHOUT a
  CI-separated regression on the nouns/verbs/classificatory-adj the cosine already wins (a net-positive, canonical-clean
  route, like the front-end hybrid).
- **DECISIVE EITHER WAY:** the composed channel + router beats the pieces + the incumbent CI-separated → PROPOSE the exact
  hdlab diff (`scalar_adjective_operation` + the router + the Ch.B FPE-log upgrade); strategy lands it. It does NOT →
  a rigorous negative localising whether the composition loses to a sub-op (which one, why) or the router mis-gates.

## 8. FILES AND ENTRY POINTS

- The p3 `experiments/exp_perclass_meaning_operations_v1.py`, `exp_fpe_log_weber_magnitude_v1.py`, `exp_adjective_magnitude_deeper_v1.py`,
  `exp_adjective_dimension_selection_v1.py` + `hdlab/quality_relation.py` (Ch.B), `hdlab/binding.py`, `hdlab/conceptual_meaning.py`,
  `hdlab/wordnet_polarity_propagation.py`, `hdlab/semantic_control.py`. Warriner VAD + Brysbaert + Lancaster + the fetched
  intensity golds (`data/scalar_adj_intensity/`) on disk.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT
  write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT re-prove the isolated sub-ops (done); the deliverable is the COMPOSED channel + router + substrate upgrade.
- Do NOT replace the verb gloss with VerbNet; do NOT use one global ATOM axis; do NOT read fine degree from the projection.
- No number crosses populations/word-classes — recompute floors on the composed task's own population.
