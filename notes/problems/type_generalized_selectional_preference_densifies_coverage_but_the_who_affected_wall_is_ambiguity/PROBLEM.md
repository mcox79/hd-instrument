# PROBLEM — densify selectional knowledge (type generalization) to recover the who-was-affected residual

**slug:** `type_generalized_selectional_preference_densifies_coverage_but_the_who_affected_wall_is_ambiguity`
**opened:** 2026-09-10 (solver full-auto), transition to the knowledge-foundation north star from the who-was-affected
investigation. **status:** OPEN. Solver writes `experiments/`, `verification/`, this folder only. NO `hdlab/` (Q111 —
propose diffs). Glass-box; **NO external LLM at inference**; WordNet-read-live is an ADMISSIBLE static lexical asset
(manifest C5, owner 2026-08-16). THE DISK OUTRANKS THE BRIEF. Full report discipline (TLDR / QUESTIONS / NEXT STEPS).

## The measured bottleneck (why)
The who-was-affected extraction residual is dominated by attachment mis-picks on non-canonical prose, resolvable only
by MEANING (which candidate entity plausibly undergoes this verb). A prior meaning-reranker starved because the
selectional store is LEXICAL (verb → attested OBJ filler WORDS): on the hard mis-attachments **40% of verb-patient
pairs have ZERO record** ("stab"+"tourist" never co-attested), and even a PERFECT exact-match store recovered only
+6pp (oracle 0.53 vs syntax 0.47). The brain does not have this sparsity — it generalizes via TYPE (tourist IS-A
person; stab affects animate/body entities), so it never needed to see that exact pair.

## The bar
PASS = densify selectional knowledge brain-foundationally (TYPE generalization — selectional preference over semantic
CLASSES, not lexical items) so the 40%-no-signal gap closes, and show it **recovers who-was-affected mis-attachments
CI-separated over the syntax floor** on the hard set (clean-signal guard: no regression where signal already existed;
controls: scramble collapses, prior-lesion falls to syntax, attribution type-plausible) — **OR a rigorous LOCATED
NEGATIVE** that names + quantifies why densification cannot (with numbers; the brain-faithful stronger version tested;
residual routed). Grade on MODERN gold (UD-EWT). Report CI half-width; recompute floors on the item's own population.

## First steps (discipline)
- **PRIOR-WORK CHECK:** the manifest lists "syntactically-typed selectional preference (verb,role,arg)" as a MAPPED
  L2 LEARNER deliverable — NOT yet built; the lexical `selectional_slots_v1.pkl` is its seed. This milestone is that
  L2 build. The is-a backbone is LIVE: `hdlab/typed_spokes.py` (WordNet hypernym closure, 117k synsets, BF_SPIRIT),
  `hdlab/animacy_lexicon.py` (coarse type), `syn.lexname()` (26-way noun supersense).
- Understand the meaning organs: `verb_role_exemplar_selector` (lexical seed store), `typed_spokes`, `event_type`.

> **BRAIN-FOUNDATIONAL CHECKLIST (ordered):** 1) which structure computes typed selectional fit (McRae role-as-
> feature-bundle; Resnik class information-gain; Warren/Paczynski animacy-type N400)? 2) COPY the computation
> (class-based selectional association) EXACTLY, SWEEP the params (supersense-cut vs hypernym-cut; margin gate τ)? 3)
> is each organ BF/admissible (WordNet-at-inference is sanctioned; the store is reading-grown from simplewiki)? 4)
> measure vs the syntax floor on the item's own population, CI-separated; scramble must collapse. 5) FULL-STACK: if
> the residual is not sparsity, name + quantify the real wall and route it. **PHASE-DIAGRAM note:** class granularity
> + gate are free to sweep — a wall at one config = move the operating point, not a ceiling.


<!-- GUARD SECTIONS (appended by strategy 2026-09-11 for brief-cert conformance; the fleet brief above is the primary statement, SOLVED.md is authoritative). -->
## THE PROBLEM IN PLAIN LANGUAGE
The selectional-knowledge store is too sparse (40% of verb-patient pairs have zero record) to say which same-type entity a verb plausibly affects. The brain generalizes by TYPE (tourist IS-A person) rather than memorizing exact filler words. Densify by type generalization. See the fleet statement above and SOLVED.md.

## WHY THIS ONE
It densifies the meaning-reranker's starved knowledge for the who-was-affected residual, and tests whether the residual is a COVERAGE gap or genuine AMBIGUITY.

## MEASURED vs INFERRED
MEASURED: 40% of hard verb-patient pairs have zero record; a perfect exact-match store recovered only +6pp (oracle 0.53 vs syntax 0.47). INFERRED (now found): type generalization fixes coverage but the who-affected wall is AMBIGUITY, not coverage -> routes to the generative situation model. See SOLVED.md.

## ALREADY TRIED
Exact-match lexical store (too sparse). Do not re-run it as the reranker. See SOLVED.md located negatives.

## VERIFY BEFORE YOU START
WordNet read-live is an admissible static lexical asset (manifest C5). Reuse the existing selectional store + WordNet is-a; read SOLVED.md IN FULL. Modern gold only. Cap cores (OMP_NUM_THREADS=4 ...).

## THE BAR
See "## The bar" above: show type-generalized selectional preference densifies coverage and (dis)proves recovery of the who-affected residual with a number, or a rigorous located negative.

## FILES AND ENTRY POINTS
experiments/exp_typed_selectional_preference_v1.py + its verification witness; the selectional store; hdlab/situation_reader.py (the undergoer/patient meaning-reranker consumer).

## DO NOT QUOTE
Retired figures (notes/reference_retired_claims_never_requote.md); no spaCy / external LLM at inference; no 19c corpora.
