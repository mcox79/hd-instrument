# Research: is training-free exemplar-based contextual re-representation the fix for the subordinate-sense WSD ceiling?

Filed by: research sub-agent, 2026-09-04. 3 parallel Sonnet lit-scan sub-agents dispatched (exemplar-theory
brain-fidelity; Erk&Pado/Reisinger-Mooney exact numbers; Zipf/class-imbalance kNN mathematics), synthesized
here against on-disk prior work for `break_the_contextual_input_encoding_ceiling_for_specific_sense_selection`
(SOLVED.md, PARTIAL/INTEGRATED 2026-09-03) and its 3 same-day companion research notes.

`research_field_advisor.py` run at cycle start: not applicable — its 22 fields are substrate-physics/
stat-mech, no adjacency to this cognitive-science question (same finding as the 3 prior notes on this thread).

**Prior-work check (two archives, both queried, counts quoted):** `experiment_index.py query "exemplar"`
50 cells/42 landed (none is instance-level kNN-over-raw-contexts for WSD; the one exemplar-kNN cell,
`exp_pragmatic_curriculum_dialogue_exemplar_knn_v1`, is a different task, n=15, PARTIAL — tied/lost to
role-sharded and attention arms 0.667 vs 0.733, scramble collapsed to 0.467 so it carries real but
non-dominant signal). `"MINERVA"`, `"Nosofsky"`, `"GCM"`, `"instance based"` all return **0 cells** — this
exact framing (individual-context storage + kernel retrieval for word sense) is untouched on disk. The
closest built thing is SOLVED.md section G's **sense-discriminative W** (PPMI: sense -> discriminating-
context-word association, one AGGREGATE profile per sense) — a **multi-prototype**, not exemplar, mechanism.

## HEADLINE

**Raw instance-level exemplar storage is NOT the fix, and the reason is decisively converged from three
independent directions: our own prior on-disk result, a head-to-head psycholinguistic-CL paper, and an
independent published WSD benchmark.** Reisinger & Mooney (2010) ran the exact 3-way test this project
needs (prototype K=1 vs. pure exemplar K=N vs. clustered multi-prototype K~20) on WordSim-353: prototype
0.53, **pure exemplar 0.60, multi-prototype 0.76** — clustering/aggregating into per-sense profiles beats
raw exemplars by a wide, significant margin, and the multi-prototype advantage is concentrated specifically
on **minority-sense** usages. That is exactly what this project already built and measured: the
sense-discriminative W (SOLVED.md G) is a multi-prototype (K=1-per-gold-sense, PPMI-aggregated), already
scores 0.367 on covered senses (+0.059 over topic, twin-separated), and its only failure is COVERAGE
(52%), not mechanism shape or Zipf-swamping. Raw exemplars would be reintroducing the worse-performing
variant of a mechanism family already tested here. Independently, Blevins & Zettlemoyer (2020) quantify
that naive nearest-neighbor WSD swamps the rare sense by **40-62 F1 points** versus the frequent sense —
direct, numeric confirmation that un-normalized instance retrieval Zipf-swamps exactly as everything else
on this problem has.

## Answers to the five questions

**1. Brain-foundational?** MIXED. Hippocampal instance/episodic storage is a PINNED, well-established
neuroanatomical claim (McClelland, McNaughton & O'Reilly 1995, *Psychol Rev* 102:419-457; Complementary
Learning Systems — real pattern-separation/completion over individual episodes, not an ML metaphor). But
GCM-style exemplar theory as a model of *categorization* has **no established neural implementation** —
Ashby & Rosedahl (2017, *Psychol Rev*) state exemplar theory "has never had a detailed neurobiological
interpretation," and their own first implementation is cortico-striatal, explicitly NOT literal hippocampal
exemplar storage. Applying instance retrieval specifically to WORD MEANING is a thin, non-mainstream
position — essentially one paper found, Jamieson, Avery, Johns & Jones (2018, *Comput Brain Behav*, "An
Instance Theory of Semantic Memory," MINERVA-2-based; medium-confidence, detail unverified) — competing
against the mainstream, better-evidenced Kintsch Construction-Integration account this project already
built faithfully and which LOST to the wired diagnostic (0.22 vs 0.32) for a W-quality reason, not a
mechanism-shape reason. **PINNED: instance storage exists in the brain. OUR-INVENTION: applying it, raw
and unclustered, to lexical sense selection** — the literature's own preferred word-meaning mechanism
(Kintsch) and its own preferred exemplar-vs-alternatives comparison (Reisinger & Mooney) both point away
from raw exemplars.

**2. Invariant-admissible?** Yes, cleanly. A static, offline-built exemplar store (no gradient descent, no
transformer, no external LLM) is admissible under the project's own PIVOT rule ("a static offline-built
asset IS admissible"), exactly like the already-built PPMI sense-discriminative W. Kernel-weighted
retrieval (Nosofsky GCM: `s_ij = exp(-c*d_ij)`, Luce-choice-rule combination; or Hintzman MINERVA-2:
`activation = S_i^3`, echo = sum of activations) is fully glass-box and inspectable line by line.

**3. Does it de-superpose the rare sense, or Zipf-swamp?** It Zipf-swamps, quantified independently:
Blevins & Zettlemoyer (2020, arXiv:2005.02590) report nearest-neighbor-style WSD scores **~40-62 F1 points
lower** on rare-sense than frequent-sense examples; adding structure (gloss information) cuts the
rare-sense error by 31.1% — i.e. raw similarity retrieval alone does not fix it, extra structure does.
Mechanistically (He & Garcia 2009 survey; Zhang & Mani 2003; Gøttcke & Zimek 2021 kCNN): raw kNN sums
LOCAL COUNT, not class-normalized density — a numerous-but-slightly-farther dominant-sense cluster can
outvote a sparse-but-closer rare-sense cluster. Erk & Padó (2010) report only a qualitative *target-word*
frequency effect ("deteriorating performance for the highest-frequency targets") — a different axis
(word frequency, not within-word sense frequency) and not evidence against sense-level swamping. **Fix
that actually works, per the class-imbalance literature:** per-sense COUNT-NORMALIZATION (score by mean
similarity within a sense's exemplars, i.e. divide by n_exemplars-in-sense before comparing across
senses) or a Bayes-corrected posterior (Gøttcke & Zimek's kCNN; Saerens/Latinne/Decaestecker 2002 EM prior
correction) — **not** kernel-exponent sharpening alone. MINERVA-2's classic cubing (S^3) sharpens by
*distance*, not by *class count*, so it does not by itself fix majority-volume swamping.

**4. Erk & Padó (2010) exact numbers.** ACL Short Papers pp.92-97, Lexical Substitution (LexSub) dataset,
Generalized Average Precision (GAP): random 28.5, single-prototype baseline 34.6-35.7, best exemplar arm
(activation-by-percentage, actP 10%) **38.6** — exemplar beats prototype by ~3-4 GAP points project-wide,
no numeric subordinate/rare-sense breakdown given. Reisinger & Mooney's own head-to-head (above) is the
more decisive comparison and it FAVORS clustering over raw exemplars. Vs. a trained encoder: context2vec
(Melamud, Goldberger & Dagan 2016) essentially split with the best prior exemplar-based system (Melamud
et al. 2015a) — context2vec won LST-07 (56.1 vs 55.2) but LOST LST-14 (47.7 vs 50.0) — exemplar methods
were competitive with an early trained BiLSTM encoder as late as 2016, consistent with this project's own
finding that a small (41M-token) context2vec arm underperformed.

**5. Ranking (brain-fidelity x expected a_s x invariant-compliance):**
1. **Multi-prototype / sense-discriminative W (already built, SOLVED.md G).** Moderate brain-fidelity
   (Kintsch-compatible, PPMI-aggregated per-sense profile), MEASURED a_s=0.367 on covered senses, fully
   admissible. Not a new build — this IS the answer, blocked only by coverage (52%).
2. **Raw exemplars + mandatory per-sense count-normalization (genuinely untested here).** Low-moderate
   brain-fidelity (thin literature), expected a_s below #1's covered-sense ceiling per Reisinger & Mooney's
   own 0.60-vs-0.76 gap, same coverage wall (a rare sense's exemplar count IS its coverage), admissible.
3. **Kintsch predication / type-level neighbor-filtering (already built as C-I settling, 0.219-0.225).**
   Not exemplar-based (type-level, not token-level); already measured, loses to the diagnostic.
4. **MINERVA-2 raw echo (S^3, no per-sense normalization).** Lowest — fixed exponent sharpens by distance
   only, does not address the count-swamping mechanism that actually causes the failure (per Q3).

## Cheap decisive test

Not a new build. Re-read the existing `exp_sg_lite_sense_discriminative_W_headroom_v1` LEARNED-W arm
(already on disk) and check whether its PPMI aggregation is mathematically equivalent to a per-sense-
count-normalized exemplar score (mean-of-similarities-within-sense) — if so, the multi-prototype result
already IS the "exemplar + normalization" upper bound this drill was asked to evaluate, and no new cell
is needed. If a genuinely different (structured/dependency-filtered) exemplar variant is wanted anyway,
gate it against beating 0.367-on-covered before funding a full build.

## Falsifiable predictions

**HARD-PASS (would justify building raw/normalized exemplars as a NEW cell):** a per-sense-count-
normalized exemplar arm, built and run on the same document-disjoint SemCor population, beats the existing
learned sense-discriminative W's covered-sense a_s (0.367) by a CI-separated margin, with an un-normalized
(raw-sum) twin losing CI-separated (demonstrating the normalization, not exemplar storage per se, is
doing the work).

**HARD-FAIL:** the normalized-exemplar arm ties or loses to 0.367 covered-sense a_s, OR the un-normalized
raw-sum twin reproduces the 40-62 F1-point rare-sense collapse Blevins & Zettlemoyer report (would confirm
this substrate's own W-aggregate already IS the de-superposition fix, and raw exemplars add nothing new).

## Cross-thread synthesis

Converges with, and does not overturn, SOLVED.md's verdict: the ceiling is W-quality x coverage, not
mechanism shape. This drill closes off "try raw instance-level exemplars" as an unexplored promising
direction — it is very likely a known-worse variant (Reisinger & Mooney's own ablation) of a mechanism
family already tested and already identified as blocked on coverage alone. Reinforces the P1 redirect
(`build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner`) rather than opening a
parallel one. Also connects to `research_gold_blind_relevance_mechanism_2026-09-03.md`'s mechanism-4
finding (precision-weighting needs an ACCUMULATED PRIOR, not a per-instance computation) — exemplar
retrieval without per-sense normalization is exactly a per-instance computation lacking that accumulated
correction, the same failure shape.

## Substrate-product implications

In plain terms: we asked whether "just remember every sentence a word has appeared in, and blend the
ones that look like the new sentence" would fix the system's trouble with rare word meanings. The
science says no, for a very concrete reason — raw memory-of-every-instance gets outvoted by the sheer
number of common-meaning examples, the same way a search engine buries a rare result under a flood of
common ones, unless you first average each meaning's examples into one profile and compare profile-to-
profile rather than instance-to-instance. We already built and tested exactly that averaged-profile
approach, and it already works better than the plain reading system on the meanings it has seen enough
of; the only thing missing is having seen enough examples of each rare meaning in the first place. So
this research says: don't build a raw-memory system, keep pushing on giving the existing averaged-profile
approach more reading material. Risk of this recommendation: it depends on Reisinger & Mooney's 2010
result generalizing from their word-similarity task to this project's WSD task, which is a reasonable but
not certain extrapolation (P_deflated below).

## Citations (verified count)

**14 distinct sources touched this pass** (by 3 parallel sub-agents, cross-checked against 2+ independent
listings where full-text fetch failed; flagged where noted):
Nosofsky 1986 *JEP:General* (GCM formula, multi-source corroborated, primary PDF extraction failed);
Hintzman 1984 *BRMIC* / 1986 *Psychol Rev* (MINERVA-2, S^3 formula, multi-source corroborated, primary PDF
extraction failed); McClelland, McNaughton & O'Reilly 1995 *Psychol Rev* 102:419-457 (CLS, PMID 7624455,
confirmed); Ashby & Rosedahl 2017 *Psychol Rev* (fetched, confirmed: exemplar theory has no established
neural implementation); Jamieson, Avery, Johns & Jones 2018 *Comput Brain Behav* (found via automated
extraction, NOT hand-verified — flag before quoting further); Erk & Padó 2010, ACL Short Papers pp.92-97
(aclanthology.org/P10-2017, fetched, numbers confirmed); Reisinger & Mooney 2010, NAACL-HLT
(aclanthology.org/N10-1013, fetched, numbers confirmed — this is the single most load-bearing citation in
this note); Kintsch 2001 *Cognitive Science* 25(2):173-202 (primary paywalled, mechanism triangulated via
secondary Kintsch reviews); Melamud, Goldberger & Dagan 2016, CoNLL pp.51-61 (aclanthology.org/K16-1006,
fetched, Table 7 numbers confirmed); He & Garcia 2009 *IEEE TKDE* 21(9):1263-1284 (survey, confirmed);
Zhang & Mani 2003, ICML workshop (confirmed); Gøttcke & Zimek 2021, SISAP LNCS 13058 (confirmed); Blevins
& Zettlemoyer 2020, arXiv:2005.02590 (fetched, confirmed — the decisive quantified rare-sense-swamping
number); Saerens, Latinne & Decaestecker 2002 *Neural Computation* 14(1):21-41 (confirmed).

Per mandatory lit-scan calibration discipline: **P_deflated = 0.10** that raw/normalized instance-level
exemplars would beat the already-built multi-prototype W (raw estimate ~0.20-0.25, deflated for: thin
brain-fidelity literature per Q1, Reisinger & Mooney's own within-paper result running the opposite
direction, and the Blevins-Zettlemoyer quantified swamping precedent). **P_deflated = 0.48** (capped at
0.50, novel-synthesis) that the existing multi-prototype-W redirect, if given broader coverage, would
itself cross a_s 0.35 on the FULL population — this is a re-statement of SOLVED.md's already-measured
lever, not new novel synthesis, so confidence is higher than a fresh claim but still capped because
coverage-scaling behavior beyond 52% is inferred, not measured.

## TLDR

We checked whether "remember every example sentence a word has appeared in and blend the similar ones"
(exemplar memory) would fix the system's weak spot on rare word meanings. It would not, and we can say
why with real numbers from outside sources: raw memory-of-every-example gets swamped by the sheer count
of common-meaning examples (an independent study measured a 40-62 point accuracy drop from exactly this
kind of swamping), unless you first average each meaning's examples into one profile before comparing —
and we already built and tested that averaged-profile version. It already beats the current system on the
meanings it has enough examples for; the only gap is not having enough examples yet for the rarest
meanings. So the honest answer is: this specific idea would not have helped, and it does not open new
work — it confirms the direction already chosen (grow the library of reading examples) is still the
right one.

## QUESTIONS

None blocking.

## NEXT STEPS

1. No new experiment cell recommended from this drill — it is a located negative that reinforces the
   existing P1 redirect (knowledge-growth/consolidation-gate).
2. If a future session wants to test the one HARD-PASS-gated cell above (per-sense-normalized exemplars
   vs. the existing learned W), it is cheap (re-derivable from existing document-disjoint SemCor data) and
   should be pre-registered against beating 0.367 covered-sense a_s before any larger build.
3. Fold this note's mechanism-comparison (multi-prototype > pure exemplar, Reisinger & Mooney 2010) into
   `notes/BRAIN_FOUNDATIONAL_AUDIT.md` alongside the existing Kintsch C-I / sense-discriminative-W entry —
   it strengthens, with an independent citation, the existing "aggregate not raw-instance" verdict.
