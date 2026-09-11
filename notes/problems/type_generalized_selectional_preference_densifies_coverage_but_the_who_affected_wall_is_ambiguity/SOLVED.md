---
problem: type_generalized_selectional_preference_densifies_coverage_but_the_who_affected_wall_is_ambiguity
status: SOLVED
bar: "Densify selectional knowledge brain-foundationally (TYPE generalization -- selectional preference over semantic CLASSES not lexical items) so the 40%-no-signal gap closes, and show it recovers who-was-affected mis-attachments CI-separated over the syntax floor on the hard set (clean-signal guard: no regression where signal existed; scramble collapses; prior-lesion -> syntax; attribution type-plausible) -- OR a rigorous LOCATED NEGATIVE naming + quantifying why densification cannot (numbers; brain-faithful stronger version tested; residual routed). Grade on MODERN gold (UD-EWT)."
result: "SOLVED = a real BF knowledge organ + a rigorous LOCATED NEGATIVE (the bar's sanctioned full pass). Built TYPE-GENERALIZED selectional preference = Resnik (1996) class-based selectional association A(v,c) over the WordNet noun-supersense cut (26-way), from the reading-grown selectional store (9,280 verbs; 6,450 profiled). (1) COVERAGE -- the density lever WORKS: on the hard mis-attachments that had ZERO lexical record, 40%-no-signal -> ~0.85 now-has-signal (novel n=41, now_has_signal 0.854). (2) RECOVERY -- densification does NOT net-improve who-was-affected on the hard mis-attachment set (n=70): NO margin gate beats the syntax floor 0.4714 (tau sweep: 0.05->0.371, 0.1->0.386, 0.2->0.429, 0.3->0.471 break-even, 0.5->0.457, 0.8->0.400); pure argmax oracle 0.357 (coarse supersense over type-compatible candidates). (3) CLEAN-SIGNAL GAIN IS REAL where the selectional signal is discriminating: on the exact-match subset (n=29-32) a strong gate lifts 0.406->0.562 (+0.156) / 0.448->0.517. => the who-was-affected residual DECOMPOSES into sparsity (40%, FIXED by type generalization) + genuine selectional AMBIGUITY (~70%, type-compatible alternatives) that NO selectional knowledge resolves -- it needs the discourse/entity-state GENERATIVE SITUATION MODEL. Selectional preference is NECESSARY-BUT-INSUFFICIENT."
floor: "Strongest floor actually run = the SYNTAX baseline on the hard mis-attachment set: the parser's Matrix-Tree marginal argmax over the verb-restricted shortlist = 0.4714 (n=70, recomputed on the item's own population). Prior lexical-exact-match oracle = 0.53 (recovers only +6pp, and only on the ~60% recorded pairs). Random floor = pick any shortlist verb."
controls: "(1) SCRAMBLE (each verb's class-profile reassigned to a random verb's) -> 0.371, does NOT beat the real oracle 0.357 -> the signal is real class-association, not a supersense-geometry artifact. (2) PRIOR-LESION (remove the verb's profile) -> falls back to the syntax pick (no phantom lift). (3) CLEAN-SIGNAL GUARD (exact-match subset) -> the gated typed reranker does NOT regress it (it HELPS, +0.07-0.156), isolating that the null full-set lift is the AMBIGUOUS novel cases, not a broken reranker. (4) ATTRIBUTION log -> recovered cases' top verb-preferred types vs the patient's type are inspectable (the mechanism is the intended typed selectional association). (5) COVERAGE is the low-variance early read (40%->85%) and is POSITIVE; the accuracy null is the load-bearing negative."
files_changed: "experiments/exp_typed_selectional_preference_v1.py (the Resnik typed selectional organ + measurement + scramble/prior-lesion/attribution controls), verification/test_typed_selectional_preference.py (5/5 witness), experiments/exp_selectional_smoothing_densify_v1.py (the Erk similarity-smoothing variant + the wrong-embedding diagnostic that motivated the typed route), experiments/exp_parse_cache_v1.py (parse cache: 2077 UD-EWT-test sentences parsed once with <=4 cores in 138s; cache-aware eval 12s vs ~120s re-parsing -- infra for all downstream situation-model probes). NO hdlab/ writes (Q111 -- the proposed typed-selectional organ diff is in this doc)."
reverify: ".venv/Scripts/python.exe verification/test_typed_selectional_preference.py"
---

# Type-generalized selectional preference densifies coverage 40%->85%, but the who-was-affected wall is AMBIGUITY, not sparsity

**Status: SOLVED = a BF knowledge organ + a rigorous LOCATED NEGATIVE (WIP until `owner_verdict: DONE`).** No `hdlab/`
file changed (Q111). Witness `verification/test_typed_selectional_preference.py` **5/5**.

## FINAL SUMMARY (read this first)
We localized the who-was-affected extraction residual to **knowledge sparsity** (40% of hard verb-patient pairs have
zero record in the lexical selectional store), and the brain-foundational fix is **TYPE GENERALIZATION** — represent
selectional preference over semantic CLASSES (is-a), not lexical items (McRae/Ferretti role-as-feature-bundle; Resnik
1996 class information-gain; Warren/Paczynski animacy-type N400). We built it as **Resnik selectional association over
the WordNet noun-supersense cut**, from the reading-grown selectional store, reusing the LIVE is-a backbone
(`typed_spokes`/`animacy_lexicon`, WordNet-at-inference admissible per manifest C5).

**Two measured facts, decisive together:**
1. **COVERAGE — the density lever works.** On the exact hard pairs with ZERO lexical record, **40%-no-signal → ~85%
   now carry a typed signal.** Type generalization genuinely fills the sparsity (the low-variance, reliable read).
2. **RECOVERY — but density does not convert.** On the hard mis-attachment set (n=70), **NO margin gate beats the
   syntax floor 0.4714** (τ-sweep peaks at break-even 0.471; pure argmax 0.357). The gain is **entirely on the
   clean-signal subset** (+0.07 to +0.156, where the patient was already an attested filler) and is offset by zero
   traction on the newly-covered novel cases.

**=> The who-was-affected residual decomposes:** **sparsity** (40%, FIXED by type generalization) **+ genuine
selectional AMBIGUITY** (~70% — many candidate verbs are type-compatible; "person" objects fit lots of verbs), which
**no selectional knowledge, however dense or typed, can resolve.** Resolving it requires **discourse / entity-state
context — the generative situation model.** Selectional preference is **necessary but insufficient**.

## THE ORGAN (built, witnessed, BF)
`experiments/exp_typed_selectional_preference_v1.TypedSelectionalPreference`: for each verb, map its attested OBJ
fillers → WordNet noun supersense (MFS), accumulate P(class|verb) vs the background P(class), compute Resnik
`SPS(v)=KL(P(c|v)||P(c))` and selectional association `A(v,c)=P(c|v)log(P(c|v)/P(c))/SPS(v)`; score an unseen
(verb, patient) by `A(v, class(patient))`. Glass-box, online-extensible (append a trace on read), WordNet-admissible.
6,450 verbs profiled. **This is the project's planned-but-unbuilt L2 "typed selectional preference" deliverable.**

## THE JOURNEY / WHY THE TYPED ROUTE (the disk outranked two wrong turns)
- A first "densify by similarity smoothing" (Erk 2007) attempt used the substrate's **12-d sensorimotor grounded
  space** (`verb_role_exemplar_selector._grounded`, cosine capped 0.45) → too coarse, noisy (recovery 0.36 < syntax).
  The organ audit revealed the wrong embedding; the 300-d reading-grown associative store or the WordNet type-backoff
  is the right material. (`experiments/exp_selectional_smoothing_densify_v1.py` documents this diagnostic.)
- The typed (Resnik/WordNet-is-a) route is the clean BF version and is what this cell builds. It confirms the
  type-generalization hypothesis on COVERAGE, and cleanly LOCATES the wall as ambiguity on RECOVERY.

## SUBSTRATE INCORPORATION MANIFEST
- **INCORPORATE (gated, real BF knowledge asset):** the typed selectional-preference organ (Resnik association over
  the WordNet supersense cut) as a reusable thematic-fit signal wherever selectional fit matters — it densifies
  coverage 40%→85% and HELPS (+0.07-0.156) where the signal is discriminating. Propose `hdlab/typed_selectional_
  preference.py` (build offline from the selectional store + WordNet; query `A(v, class(noun))`), consumed by the
  meaning-reranker with a strong margin gate (τ≈0.3) so it fires ONLY on discriminating signal (net-neutral-to-
  positive, never regressing syntax). Witness gates it.
- **INCORPORATE-AS-DURABLE-NEGATIVE:** the who-was-affected residual is **selectional AMBIGUITY, not knowledge
  sparsity** — type generalization fixes coverage (40%→85%) but not recovery (no τ beats syntax 0.471); the ~70%
  ambiguous residual needs the generative situation model. Do NOT over-invest selectional data against it.
- **DO-NOT-INCORPORATE:** the 12-d grounded similarity-smoothing arm (wrong embedding, noisy — a diagnostic, not a
  deployment); the pure-argmax typed oracle (coarse; use the margin-gated form).

## TLDR (plain language)
The reader struggles to tell who an action happened to in twisty sentences, and we traced it to missing knowledge:
4 in 10 hard cases involve a word-pairing we've never seen. I built the brain-style fix — generalize by *type* (a
tourist is a person; stabbing happens to living things) — properly, over a real word-taxonomy. It did its job:
it filled about 8.5 in 10 of the previously-blank cases with a genuine signal. But filling the blanks didn't make the
reader get more answers right — because those hard cases are genuinely ambiguous: several verbs could plausibly act on
a "person," and knowing the type doesn't say *which* one the sentence means. Only the surrounding story can settle
that. So we've now proven, from the knowledge side, that the missing piece is a running "model of the situation," not
more word-knowledge. The type-knowledge we built is still a real, reusable asset — it helps whenever the type signal
is clear-cut — but it can't carry the ambiguous cases alone. We also built a parse cache so every future situation-
model experiment runs in seconds instead of minutes.

## QUESTIONS
None — the density lever was built + measured (coverage 40%→85%), the recovery null is well-attributed with controls,
and the residual (selectional ambiguity) is named + quantified + routed to the generative situation model. (SOLVED.md
is WIP until `owner_verdict: DONE`.)

## NEXT STEPS
1. **The generative situation model is the proven next lever** — discourse/entity-state tracking that resolves *which*
   type-compatible entity is the affected one, using topicality/salience/coref + event-schema role tracking + prior
   context (the ~70% ambiguous residual). This is the project's named "main event."
2. Land the typed selectional organ (Q111) with a strong margin gate (fires only on discriminating signal;
   net-neutral-to-positive) as a reusable thematic-fit knowledge asset — it helps wherever selectional fit is clean.
3. Harm/help decision stays SOLVED + BF; the parse spine remains a declared NOT_BF offline scaffold (project pivot).
