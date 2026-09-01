# PROPOSED FOLLOW-ON PROBLEM (draft brief for the strategy session to file as a new problem)

**Proposed slug:** `the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus`
**Proposed priority:** HIGH (it is the DEFINITIVELY-LOCATED #1 lever for who-did-what; measured, not inferred).
**Author:** solver of `the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store`
(owner asked to "make it its own problem for a solver"). Strategy session: lift this into `notes/problems/<slug>/PROBLEM.md`,
set the frontmatter (priority/review), and file.

---

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader decides who-did-what partly from per-verb knowledge of "what kinds of things this verb usually
acts on" (you READ books, you DRIVE cars). That knowledge is currently learned from Simple-English-Wikipedia
-- the WRONG kind of text for what we test on. When we build the exact same knowledge from text of the SAME
KIND as what is being read, who-did-what accuracy jumps by nearly the whole available gap, even with the same
imperfect parser. So the reader needs to learn its per-verb / event knowledge from its OWN reading domain
(register-native), not from a generic pile of unrelated text.

## 2. WHY THIS ONE
It is the DEFINITIVELY-LOCATED wall for who-did-what role assignment. A rigorous oracle-ladder dissection
(`experiments/exp_wall_dissection_v1.py` + `exp_wall_corpus_axis_v1.py`) isolated the binding constraint and
ruled out every other candidate WITH NUMBERS: it is NOT the grounding/feature space (grounded similarity adds
+0.20 over pure memorization), NOT the mechanism (FHRR role-filler binding is faithful and beats the shortcut),
NOT the combination (a learned CLS arbitrator ties the better single system), NOT parse cleanliness (a minor
+0.036). It is DOMAIN MATCH of the selectional/event corpus (+0.149, ~80% of the gap). It also UNIFIES with the
19c register-drift wall (same root cause): selectional/event knowledge is DOMAIN/REGISTER-RELATIVE.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: the brain reads a register well because it has READ that register -- selectional/event knowledge is the
CONSOLIDATED statistical structure of the reader's own experienced language (Complementary Learning Systems,
McClelland-McNaughton-O'Reilly 1995; generalized event knowledge, McRae/Elman; thematic fit is learned from
experienced verb-argument co-occurrence, McRae et al. 1998). The neocortical semantic store is trained by
consolidating episodic events from the reader's OWN input stream. So the store must be grown from
DOMAIN/REGISTER-matched text, and the brain-foundational representation is the substrate's FHRR role-filler
BINDING (already wired as `hdlab/bound_event_backbone.py` + `hdlab/event_bundle.py`; SEM/Franklin 2020).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** at FIXED GloVe representation on the QA-SRL non-reversible slice --
  simplewiki-parsed store 0.363 -> IN-DOMAIN-parsed (same noisy parser, no gold, leave-one-sentence-out) 0.518
  -> in-domain-gold 0.551. DOMAIN effect +0.149 CI[+0.115,+0.185]; parse-quality effect +0.036 CI[+0.010,+0.062].
  DEMONSTRATION (`exp_domain_matched_fhrr_demo_v1.py`): the domain-matched win is CLEAR at the MARGINAL
  (verb->patient) exemplar store (+0.149). At the JOINT FHRR (subj,verb,obj) store, a 2M-token in-domain
  corpus is TOO SPARSE (joint SVO needs both subj+obj; the noisy parser often misses the subject on the
  non-canonical slice) and it LOSES to out-of-domain (-0.055) -- a DATA-DENSITY effect, NOT a domain
  refutation. SO: the joint/FHRR store needs a LARGER domain-matched corpus than the marginal store. Grounded
  similarity generalizes (exact-match ceiling 0.360 < gold-store 0.556). Oracle(episodic+semantic) 0.61;
  learned arbitrator ties the better single system (~0.455).
- **INFERRED (you must measure):** whether a DEPLOYABLE, no-gold, register-native selectional/event store --
  built offline from a genuinely DISJOINT domain-matched corpus (not the test corpus itself) and bound with the
  substrate's FHRR event codec -- recovers the +0.149 domain lever on HELD-OUT who-did-what, and how it composes
  with the wired `bound_event_backbone`. Also: the residual to human (~0.55 -> ~0.83) is a SECOND wall
  (impoverished input: full parse + discourse) -- out of scope here, a separate problem.

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- Do NOT re-run: richer features (Binder-65/GloVe-300 -- measured NON-lever for this wall), a cleverer combiner
  / learned arbitration / hybrid (measured dead-end -- the arbitrator ties the better single system), parser
  register-adaptation via self-training (REFUTED for 19c, stalls), a bigger OUT-OF-DOMAIN corpus (wrong axis).
- BUILD ON: the FHRR role-filler binding demonstration (`exp_fhrr_event_role_assignment_v1.py`), the in-domain
  parse (`exp_wall_corpus_axis_v1.py`), the wired `bound_event_backbone` / `event_bundle` (do NOT reinvent
  event binding -- p4, owner-DONE).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- Read the DEFINITIVE WALL DISSECTION section of the parent SOLVED.md and re-run `exp_wall_corpus_axis_v1.py`.
- Confirm the domain axis dominates (+0.149) and parse-quality is minor (+0.036) on your own recomputation.
- Read `hdlab/bound_event_backbone.py` + `hdlab/event_bundle.py` (the wired FHRR event store you build on).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a no-gold, REGISTER-NATIVE selectional/event store built OFFLINE from a DISJOINT domain-matched corpus,
bound with the substrate's FHRR event codec, RECOVERS who-did-what CI-separated over the current out-of-domain
(simplewiki) store on a HELD-OUT domain-matched who-did-what test, with a verb-shuffled twin LOSING CI-sep, and
a domain-scramble control (same corpus, wrong-domain labels) losing. A rigorous located negative (the domain
lever does not transfer to a genuinely disjoint corpus) is a full PASS if it names why. Report CI half-width +
null p95. Corpus-age/domain confound: the win must be DOMAIN, not leakage -- use a DISJOINT domain corpus, not
the test corpus (the parent used leave-one-sentence-out as a probe; the deliverable needs a disjoint corpus).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. Reuse: `exp_wall_corpus_axis_v1.py` (in-domain parse),
`exp_fhrr_event_role_assignment_v1.py` (FHRR mechanism), `hdlab.binding` / `hdlab.event_bundle` /
`hdlab.bound_event_backbone` (the wired FHRR event store). Strategy lands any hdlab wire (Q111, default-off,
witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` (the selectional/event store is
domain/register-relative; the corpus is the lever, not features/mechanism/combiner).

## DO NOT QUOTE
- Do NOT quote the parent's in-domain +0.149 as YOUR result -- it used leave-one-sentence-out on the TEST
  corpus (a probe, not a disjoint deliverable). Re-measure on a genuinely disjoint domain-matched corpus.
- Do NOT claim a win without the domain-scramble control (the DOMAIN, not any in-corpus signal, must do the work).
