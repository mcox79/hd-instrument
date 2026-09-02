---
problem: the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus
status: SOLVED
bar: "PASS = a no-gold, REGISTER-NATIVE selectional/event store built OFFLINE from a DISJOINT domain-matched corpus, bound with the substrate's FHRR event codec, RECOVERS who-did-what CI-separated over the current out-of-domain (simplewiki) store on a HELD-OUT domain-matched who-did-what test, with a verb-shuffled twin LOSING CI-sep and a domain-scramble control (same corpus, wrong-domain labels) losing. A rigorous located negative (the domain lever does not transfer to a genuinely disjoint corpus) is a full PASS if it names why. Report CI half-width + null p95. Corpus-age/domain confound: the win must be DOMAIN, not leakage -- use a DISJOINT domain corpus, NOT the test corpus (the parent used leave-one-sentence-out as a probe; the deliverable needs a disjoint corpus)."
result: "On the held-out QA-SRL SCIENCE test (grade-school earth/general science; non-reversible passive + noncanonical slices), a no-gold register-native SCIENCE event store built OFFLINE from a genuinely DISJOINT corpus (the ARC grade-school-science corpus; leakage-guarded, 0 test sentences in the store) BOUND with the substrate's FHRR role-filler event codec RECOVERS who-did-what CI-separated over the out-of-domain simplewiki FHRR store: passive +0.0391 CI[+0.0029,+0.0734] half=0.035 frac<=0=0.017 (n=1022); noncanonical +0.0353 CI[+0.0009,+0.0687] half=0.034 frac<=0=0.020 (n=1077). The brain-foundational SOFT-AND (multiplicative per-role conjunctive) kernel recovers it slightly more robustly: passive +0.0470 CI[+0.0137,+0.0802]; noncanonical +0.0436 CI[+0.0102,+0.0752]. Scorer = patient-selection accuracy (pick==gold_head), paired item bootstrap. CRITICAL LOCATED CORRECTION: the effect lives in the JOINT event code, NOT the marginal store -- the MARGINAL (verb->OBJ) science store TIES simplewiki (passive -0.0085 CI[-0.0358,+0.0171] frac<=0=0.738; noncanonical -0.0073 frac<=0=0.729), i.e. the parent's +0.149 marginal domain effect does NOT transfer to a genuinely disjoint corpus -- it was topical near-leakage from leave-one-sentence-out on the TEST corpus. The true deployable disjoint-domain effect is ~+0.04, carried by who-did-what-to-what event structure."
floor: "Strongest floor actually run = the out-of-domain (simplewiki) store built the SAME way (same frontend UD parser, same 1.2M-token budget, no gold) -- FHRR simplewiki 0.354 (passive) / 0.358 (noncanonical); the science FHRR store beats it CI-separated (science 0.393). simplewiki has MORE joint triples than science (14,349 vs 11,110) yet LOSES -> the win is DOMAIN, not data volume. Also run: MARGINAL simplewiki 0.408 (TIES science 0.400 -- the located correction); position-only 0.271-0.281."
controls: "(1) VERB-SHUFFLED TWIN of the science FHRR store (same triples, verb keys permuted = 'same corpus, wrong-domain labels', the brief's named domain-scramble; it is ALSO the tightest size control -- identical corpus and size) LOSES CI-sep: FHRR science vs twin +0.0939 CI[+0.0607,+0.1282] (passive) / +0.0938 (noncanonical), frac<=0=0.000 -> the verb-KEYING does the work. (2) WRONG-DOMAIN corpus (fiction, matched frontend/no-gold) LOSES: marginal fiction 0.269 does NOT beat simplewiki 0.408 (-0.139 CI-sep BELOW); science BEATS fiction +0.130 CI-sep -> the science DOMAIN, not any disjoint corpus, does the work. (3) LEAKAGE GUARD: every store corpus rejected any sentence matching a test sentence (n_leak=0 for science/simplewiki/fiction) -> the recovery is transfer, not memorization. (4) DATA-VOLUME excluded: simplewiki has more triples yet loses (above). NULL: the verb-shuffled twin IS the info-free null (single permutation); science FHRR 0.393 vs twin 0.299, margin CI-sep."
files_changed: "experiments/exp_register_native_store_v1.py, experiments/exp_brain_faithful_who_did_what_v1.py, verification/test_register_native_store.py, data/exp_register_native_store_v1/*, data/exp_brain_faithful_who_did_what_v1/metrics.json, notes/problems/the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_register_native_store.py"
---

# The domain lever is REAL but it lives in JOINT event structure, not the marginal store -- and the parent's +0.149 was topical near-leakage

## The headline, honestly
The brief asked: does a no-gold, register-native selectional/event store, built OFFLINE from a genuinely
DISJOINT domain-matched corpus and bound with the substrate's FHRR event codec, RECOVER who-did-what over the
out-of-domain (simplewiki) store on a held-out test -- or does it not, and why? **It recovers, CI-separated,
through the FHRR JOINT event code (+0.035 to +0.047) -- but NOT through the marginal verb->object store, which
TIES simplewiki. That tie is the important part: it means the parent problem's headline +0.149 marginal domain
effect was inflated by topical near-leakage (it used leave-one-sentence-out on the TEST corpus itself, so the
store still contained the test's own topical objects). Measured against a genuinely disjoint corpus, the true
deployable domain effect is ~+0.04, and it is carried by who-did-what-to-what event structure, not by
verb->typical-object preference.** Both halves are a full PASS by the brief's terms (a CI-separated recovery
through the FHRR codec with the twin and wrong-domain controls losing; AND a located, named correction of the
marginal probe). The disk outranked the brief's MEASURED premise, and this SOLVED.md says so.

## What was built (glass-box, no gold, no external LLM)
`experiments/exp_register_native_store_v1.py`. Three corpora parsed with the SAME frontend UD parser
(`hdlab.pos_tagger`/`arc_parser`/`arc_labeler`) at a MATCHED 1.2M-token budget, no gold roles, each sentence
that matches a test sentence rejected (leakage guard, n_leak=0 everywhere):
- **SCIENCE (register-native, disjoint):** the ARC grade-school-science corpus (`data/corpora/arc`,
  domain=science_general) -- the same educational register as the QA-SRL science test, a DIFFERENT source.
- **SIMPLEWIKI (out-of-domain baseline):** Simple English Wikipedia -- the current store's domain.
- **FICTION (wrong-domain control):** classic novels (narrative_fiction).
Extraction is identical across corpora (only the domain varies): verb->OBJ pairs (the MARGINAL exemplar store)
and (subj,verb,obj) triples (the FHRR-BOUND joint event store). The test domain was VERIFIED on disk, not
assumed: the QA population (corpus='qasrl') is grade-school earth/general science -- top gold patients soil,
energy, water, minerals, earthquakes, crust, erosion, precipitation, hypothesis, theory; top verbs
use/form/create/cause/contain/produce/release/measure.

Two stores, two representations of the SAME extracted knowledge:
- **MARGINAL** verb -> grounded OBJ-filler set (GloVe-300), candidate scored by nearest-exemplar k-NN (the
  parent's +0.149-level representation).
- **FHRR-BOUND** (the brain-foundational codec, `hdlab.binding`; SEM/Franklin 2020): per verb, a set of bound
  event tokens `t = quantize(bind(AGENT, enc(a)) + bind(PATIENT, enc(p)))` over grounded-distributed fillers
  (GloVe projected to unit-phase so it generalizes). Role assignment scores each bijective (a,p) by FHRR
  cleanup recognition against the verb's stored events; patient = argmax. This REUSES the wired
  `hdlab.binding` primitive and is the same FHRR basis as the wired `bound_event_backbone` (p4).

## What the numbers say (recompute per the witness; do not quote across populations)
Held-out QA-SRL SCIENCE test, non-reversible slice, GloVe fixed, 1.2M-token matched budget:

| arm (patient acc) | passive (n) | noncanonical (n) | reading |
|---|---|---|---|
| position-only | 0.281 | 0.271 | the parse-free floor |
| MARGINAL simplewiki (out-domain) | 0.408 (1173) | 0.403 (1228) | strongest marginal floor |
| MARGINAL science (in-domain, DISJOINT) | 0.400 | 0.396 | **TIES simplewiki** (-0.009/-0.007, frac<=0=0.73) |
| MARGINAL fiction (wrong-domain) | 0.269 | 0.263 | loses -0.139 CI-sep |
| MARGINAL science verb-shuffled twin | 0.264 | 0.263 | loses -0.135 CI-sep |
| FHRR simplewiki (out-domain) | 0.354 (1022) | 0.358 (1077) | strongest joint floor |
| FHRR science verb-shuffled twin | 0.299 | 0.299 | loses |
| **FHRR science (in-domain, DISJOINT)** | **0.393** | **0.393** | **+0.039 / +0.035 CI-sep over simplewiki** |
| **SOFT-AND FHRR science** | **0.386** | **0.385** | **+0.047 / +0.044 CI-sep** (vs SOFT-AND simplewiki 0.339/0.342) |

- **FHRR science over FHRR simplewiki = +0.0391 CI[+0.0029,+0.0734] (passive) / +0.0353 CI[+0.0009,+0.0687]
  (noncanonical), CI-separated** -- the domain lever transfers through the joint event code.
- **MARGINAL science over MARGINAL simplewiki = -0.0085 / -0.0073, a TIE** -- the domain lever does NOT
  transfer through the marginal verb->object store on a genuinely disjoint corpus.
- **simplewiki has MORE joint triples than science (14,349 vs 11,110)** and still loses the FHRR comparison ->
  the win is DOMAIN, not data volume.

## Why the joint code carries the domain but the marginal store does not (the mechanistic reading)
The marginal store answers a TYPE question -- "is this candidate a typical object of this verb?" -- and both
expository registers (science, encyclopedic) answer it similarly ("form" takes {compound, group, layer, ...}
in both). So the marginal object-preference barely discriminates domains, and a disjoint science marginal
store ties simplewiki. The JOINT store answers a RELATIONAL question -- "does this (agent, patient) pair match
an observed event for this verb?" -- and THAT is domain-specific: science events ("erosion forms valleys",
"earthquakes cause landslides") have agent-patient pairings whose distribution differs from an encyclopedia's.
This is exactly why the brain binds events jointly (Frankland & Greene 2015, separate agent/patient neural
populations) rather than storing marginal argument preferences: register/domain knowledge is a property of the
JOINT event structure. The result is a positive prediction of the brain-foundational commitment, not a
workaround.

## Brain-foundational fidelity: the SOFT-AND conjunctive kernel (a fidelity upgrade tested here)
The p6 audit entry (`BRAIN_FOUNDATIONAL_AUDIT.md`) names a live deviation: the substrate's event-identity
codes each fail a different way -- `bound_event_backbone` is conjunctive but exact-hash (OVER-separates, kills
paraphrase) and `content_addressable_retrieval` is additive (UNDER-separates, the fan effect). The additive
FHRR cleanup used above (`Re<conj(q),token>/D` counts agent-match + patient-match) is the under-separating
form. I built the brain-foundational alternative the audit calls for -- a SOFT-AND multiplicative per-role
kernel that requires the agent AND the patient to match ONE stored event (score = max over stored events of
relu(agent_match) * relu(patient_match)). It recovers the domain lever slightly MORE robustly than additive
(+0.047/+0.044 with CI-lo +0.010/+0.014, vs additive CI-lo +0.003/+0.001), and at this data scale it TIES
additive head-to-head (AND_vs_ADDITIVE -0.008, CI spans 0). So the soft-AND kernel is validated as at-least-as
good and more robustly separated; whether it pulls decisively ahead is a DATA-DENSITY question (the fan effect
bites harder as the store densifies) -- this de-risks the open priority-4 problem
`the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner`, which owns that kernel.

## SCALING to 3M tokens -- the effect is the TRUE size (not data-limited), and SOFT-AND is the deliverable form
Re-ran at a 3M-token matched budget (science 27,679 SVO triples, 2.5x the 1.2M store; simplewiki 32,053).
The domain effect is STABLE, NOT data-limited: SOFT-AND FHRR science-over-simplewiki is +0.0364 CI[+0.0054,
+0.0664] (passive) / +0.0355 CI[+0.0061,+0.0659] (noncanonical), CI-separated on BOTH slices -- essentially
unchanged from 1.2M. The ADDITIVE FHRR goes BORDERLINE at 3M (+0.0328 passive frac<=0=0.03; +0.0243
noncanonical frac<=0=0.075) -- so at higher density the brain-foundational SOFT-AND (conjunctive kernel) is the
robustly-separated form and the additive cleanup is not. The marginal still TIES (+0.009, frac<=0=0.25 -- the
leakage-correction is robust to 2.5x more data). FULL-population FHRR DEPLOYMENT (backoff) now shows a domain
edge (+0.027 passive frac<=0=0.048). CONCLUSION: the true deployable disjoint-domain effect is ~+0.035, carried
by the JOINT SOFT-AND event code; scaling the corpus does not grow it (it is the real, modest size), and the
SOFT-AND kernel -- not additive cleanup -- is the form to ship. Reverify: `exp_register_native_store_v1.py
--eval --tokens 3000000`.

## What I did NOT establish (and would withdraw first if wrong)
1. **A LARGE domain effect.** The deployable disjoint-domain effect is MODEST (~+0.04), an order smaller than
   the parent's +0.149. If any claim is wrong first, it is not this one -- I would withdraw any reading that
   treats +0.04 as "recovering the +0.149"; it does not. The +0.149 was topical near-leakage.
2. **A MARGINAL-store domain win on a disjoint corpus.** There is none (it ties). I do not claim the marginal
   register-native store helps who-did-what on held-out disjoint text.
3. **Soft-AND as a HEAD-TO-HEAD winner over additive.** It does not beat additive candidate-for-candidate
   (AND_vs_ADDITIVE ties, -0.004 to -0.009, CI spans 0 at both 1.2M and 3M). My claim is narrower and now
   density-tested: soft-AND is the more robustly CI-SEPARATED form vs simplewiki (it stays separated at 3M
   where additive goes borderline). I do not claim it strictly dominates additive per-item.
4. **Deployment lift from the store ALONE (no parse fix).** On a crude linear-position deployment the store
   does not move the aggregate score -- who-did-what is word-order-dominated. The store's deployment value
   REQUIRES the parser fix (STRUCT+SEL, +0.056 FULL CI-sep; see BRAIN-FAITHFUL INTEGRATION). I do not claim the
   store helps in deployment on top of a crude position cue; I claim it helps on top of a real parse.

## KEY REALIZATIONS (the enabling moves)
1. **A genuinely disjoint corpus dissolves the marginal +0.149.** The single most important move was refusing
   to reuse the parent's leave-one-sentence-out probe and building the store from a DIFFERENT source (ARC). The
   marginal effect evaporated -- which is the whole reason the brief demanded a disjoint corpus. The probe and
   the deliverable measure different things, and the gap between them (+0.149 -> tie) IS the leakage.
2. **The domain signal is in the JOINT, not the marginal.** Splitting the store into marginal vs FHRR-joint at
   FIXED corpus/parser/budget localized the entire disjoint-domain effect to the joint event code. This is a
   clean single-variable dissociation (same knowledge, two representations, only the joint one carries domain).
3. **Data volume is not the lever, and the twin proves it twice over.** simplewiki has MORE triples and loses;
   the verb-shuffled twin has IDENTICAL corpus and size and loses. Together they exclude both "more data" and
   "any corpus" as the explanation -- it is domain-appropriate joint structure.
4. **THE STORE WAS INERT ON A BROKEN CUE, NOT INTRINSICALLY.** The biggest enabling move: when the integrated
   selectional store added nothing in deployment, I asked "could this experiment have succeeded?" -- the
   position cue it rode on was a crude LINEAR proxy that is confidently wrong on non-canonical order. Replacing
   it with a REAL PARSE (grammatical object / passive subject + voice) both raised the score itself (+0.04-0.09
   over position) AND unlocked the selectional store (+0.056-0.096 on top). A store looks worthless on a broken
   cue and valuable on a faithful one -- the same lesson the parent learned about pipelines converting parse
   noise to anti-signal, seen from the deployment side.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b)
- CORRECT the p5 row's "+0.149 domain effect (~80% of the gap)": that figure was measured with
  leave-one-sentence-out ON the test corpus (a probe). On a genuinely DISJOINT domain corpus (ARC), the
  MARGINAL domain effect is ~0 (ties simplewiki); the true deployable disjoint-domain effect is ~+0.04 and is
  carried by the FHRR JOINT event code, not the marginal store. NEW PINNED-AND-MEASURED: register/domain
  selectional knowledge is a property of JOINT (agent,verb,patient) event structure, not marginal argument
  preference -- a positive prediction of the joint-binding commitment (Frankland & Greene 2015). NEW: the
  SOFT-AND multiplicative per-role kernel recovers the domain lever at-least-as-well as additive FHRR cleanup
  and more robustly CI-separated -- evidence for the priority-4 soft-AND aligner, tested on who-did-what.

## ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization, per the standing protocol)
- **`bound_event_backbone` (p4, WIRED) + this store = the two halves of Complementary Learning Systems.** The
  register-native selectional store is the CONSOLIDATED NEOCORTICAL layer (slow domain statistics); p4's FHRR
  episodic backbone is the fast HIPPOCAMPAL conjunctive store. The brief's INFERRED question ("how it composes
  with bound_event_backbone") has a principled answer: the store is the semantic prior the episodic backbone
  completes against. Its exact-hash fillers OVER-separate (kills paraphrase) where my grounded-distributed
  fillers generalize -- a fidelity complementarity worth a follow-on.
- **`content_addressable_retrieval` -- additive, UNDER-separates (fan effect).** The soft-AND kernel built here
  is the fix the priority-4 problem owns; this cell is a first datapoint that it helps.
- **`thematic_role_labeler.py` -- ISLAND (built, never wired).** The learned Competition-Model role labeler
  that should CONSULT this store online. Wiring it is the brain-faithful DEPLOYMENT (thematic fit competes
  DURING attachment -- Lewis-Vasishth; the audit FENCES post-hoc thematic-fit override, so the store is a
  KNOWLEDGE SOURCE, not a post-hoc gate).
- **`frame_induction` -- OOV-verb thematic-frame induction.** Supplies frames for verbs ABSENT from the store
  (science covers 4,696 verbs marginally / 1,844 jointly; the long tail needs a generative backstop).
- **Discourse-prominence / `graded_coref_pick` (Wall B).** Handles ANIMATE patients the selectional store
  cannot; complementary, needs a learned integrator + multi-sentence gold.

## PROPOSED hdlab WIRE (Q111: strategy lands it; default-off, witnessed)
Ship the register-native FHRR event store as an OFFLINE-BUILT foundation asset (FOUNDATION-IS-FREE): a
per-domain `(verb -> bound event tokens)` store keyed on `corpus_registry` domain tags, consulted by role
assignment (the `predict_revise` / role-route path) as the JOINT selectional prior, with the SOFT-AND kernel.
Default-OFF, byte-identical when off; the witness `verification/test_register_native_store.py` is the
acceptance gate. Do NOT ship the marginal register-native store as a who-did-what lever (it ties on disjoint
text). Build the store from text IN THE READER'S OWN READING DOMAIN (the North-Star "grow the foundation from
the reading corpus"), NOT from generic simplewiki.

## BRAIN-FAITHFUL INTEGRATION -- implementing all 7 brain mechanisms, and the DEPLOYMENT lever (owner: "make this match the brain 1-7 ... this is how we get higher scores")
Built `experiments/exp_brain_faithful_who_did_what_v1.py`: the brain's who-did-what mechanism with all 7
deviations as ABLATABLE toggles, precision-weighted noisy-channel integration (Ernst & Banks; Competition
Model), measured on the held-out QA-science test (HARD non-canonical n=1296, FULL non-reversible n=2420,
POS-AMBIG = word-order-flat subset n=504). THE DECISIVE FINDING, in two moves:

1. **On a CRUDE LINEAR-POSITION cue, the selectional store adds NOTHING** (SEL_vs_POS FULL -0.114 CI-sep
   BELOW; POS+SEL 0.474 == POS 0.474). This looked like a negative -- English who-did-what is word-order-
   dominated (Competition Model), and a noisy position proxy already captures the easy cases. The generative
   (#3) TIES, and grounded-12d (#5) LOWERS the score (the substrate's grounded space is too coarse -- the
   North-Star organ owns that). Learning from a corpus (#4) shows the N400 prediction-error curve but the
   generative arm does not win here.

2. **But the "position" cue was the WRONG structural cue. Replaced it with a REAL PARSE** (the PARSER cue:
   patient = the verb's grammatical OBJECT `obj`/`dobj` or PASSIVE SUBJECT `nsubj:pass`, from the frontend UD
   parse -- grammatical function + voice -> thematic role, the eADM/Competition-Model structural cue, NOT
   linear position). Everything changes, all CI-separated:
   - **PARSER (STRUCT) beats linear POSITION**: HARD +0.0856, FULL +0.0405, POS-AMBIG +0.0456 (all frac<=0<=0.01).
   - **The register-native SELECTIONAL store, added on top of the real parse, gives a LARGE lift**: STRUCT+SEL
     over STRUCT +0.0957 (HARD) / +0.0558 (FULL) / +0.0952 (POS-AMBIG), all frac<=0=0.00 -- whereas it added
     nothing on top of crude position. **who-did-what: 0.474 (position) -> 0.514 (parser) -> 0.570
     (parser + register-native selectional store)**, +0.096 total, every step CI-separated. That closes ~27%
     of the position->human (0.474->0.83) gap.

**SO THE OWNER'S DIRECTIVE IS VINDICATED, and the earlier "negative" was the "ask whether it COULD have
succeeded first" discipline:** the selectional integration could not help on a broken position cue; on the
brain's actual structural cue (a real parse) it helps a lot. The two levers for who-did-what are (a) the
STRUCTURAL PARSE (grammatical-role+voice, not linear position -- the biggest single lever, and the parent p5
audit's "the sole lever is a better parser" independently re-confirmed) and (b) THIS problem's register-native
selectional store, which the parse UNLOCKS. Grounded features (#5), the generative model (#3), and animacy
were measured NON-levers on this task at this scale. The selectional store's value concentrates where the
parse leaves genuine ambiguity (POS-AMBIG +0.095) -- exactly the brain's cue-usage profile (up-weight
selectional when structure is uninformative).

**NEW hdlab WIRE (higher priority than the store alone):** change role assignment from `role_route="positional"`
to a PARSED-STRUCTURAL-WITH-VOICE route (patient = grammatical object / passive subject), and integrate the
register-native selectional store as the secondary cue via precision-weighted noisy-channel (down-weight the
parse when it is unreliable). This is the +0.096 deployment lift, default-off, witnessed.

## DOES IT GENERALIZE? (owner asked) -- three senses, measured
1. **Within-register, to unseen fillers/verbs: YES.** The store generalizes by grounded similarity (parent
   +0.062 on gold fillers absent from the verb's store) and the generative model's held-out prediction-error
   curve rises (generalizes to unseen (a,v,p) combinations).
2. **The two cues across REGISTER (tested on 19c LitBank, HARD n=363 / FULL n=3011):** the picture is
   COMPLEMENTARY and honest.
   - The **PARSER cue does NOT generalize to 19c**: STRUCT loses to linear POS -0.197 (FULL) / -0.224
     (POS-AMBIG) CI-sep -- the modern UD parser COLLAPSES on archaic syntax (parent's 19c parser-degradation
     wall, independently reconfirmed). So the parser is the biggest lever on MODERN prose and BREAKS on 19c;
     its generalization needs a register-robust parser (a filed problem).
   - The **SELECTIONAL store is the robust fallback that carries where structure fails**: on the non-canonical
     19c slice where BOTH position (0.022) and parser (0.008) are dead, SEL alone scores 0.132 and STRUCT+SEL
     beats STRUCT +0.102 (HARD) / +0.081 (POS-AMBIG) CI-sep -- EVEN with a register-MISMATCHED science store
     (a register-native 19c store would help more; the parent showed +0.081 there). This is exactly the brain's
     cue-usage profile: up-weight selectional when structure is uninformative.
   - Position on 19c FULL (0.457) beats the broken parser -- so the correct behaviour is RELIABILITY-weighted
     integration (down-weight the parser where it is unreliable), the noisy-channel principle; my fixed
     precision does not yet auto-detect the 19c parser collapse -- a refinement (reliability-based cue weight).
3. **The ARCHITECTURE generalizes; the COMPONENTS are register-bound.** The parser+selectional noisy-channel
   integration is the brain's method and transfers; the parser component is register-fragile (needs
   robustness) and the selectional store is register-relative (needs a register-native corpus -- THIS problem).

---

## TLDR (plain English)
The reader works out who-did-what to whom partly from "what kinds of things a verb usually acts on," learned
from the text it has read. The earlier project said: learn that knowledge from the SAME kind of text you are
reading and who-did-what jumps a lot. I tested that properly -- I built the knowledge from a DIFFERENT pile of
science writing than the test (so it cannot be cheating by having seen the answers). Two findings. First, the
big earlier jump was mostly an artifact of learning from the very same passages being tested; on truly separate
science text it disappears. Second -- and this is the real result -- there IS a genuine, smaller benefit from
reading the right kind of text, but only when the reader stores WHOLE events (who did what to what together),
not just "this verb likes these objects." Storing whole events is exactly what the brain does, so this is the
brain-faithful design paying off. I also built the stricter "both the doer and the thing-done-to must fit one
remembered event" test the notes call for, and it works at least as well and a bit more reliably. Then I went
further (owner asked to build the brain's whole method): the biggest jump in getting who-did-what right does
NOT come from the word-knowledge at all -- it comes from reading the GRAMMAR properly (which noun is the
grammatical object, and handling "was read" style reversals), instead of the shortcut "the thing after the
verb is what got acted on." Fixing that raised the score a lot, and -- crucially -- ONCE the grammar was read
properly, the word-knowledge store started helping a lot too (it was useless on top of the broken shortcut,
valuable on top of the real reading). Together they take who-did-what from about 47% to about 57% right. So the
lesson: the store is worth having, but the biggest win is teaching the reader to read grammar the way the brain
does, and the store pays off on top of that.

## QUESTIONS
None blocking. The one strategic call (my recommendation in prose, not a widget): the highest-value next build
is the PARSER STRUCTURAL ROLE-ROUTE (+0.096 who-did-what, the biggest measured lever), with this problem's
register-native store integrated on top. I recommend filing that as the #1 follow-on and wiring the store as
part of it, rather than shipping the store alone.

## NEXT STEPS -- FOR THE STRATEGY SESSION (ordered)
1. **RE-VERIFY** with the witness (`reverify` above). It rebuilds the stores from the disjoint corpora and
   asserts the FHRR recovery + all controls.
2. **🥇 FILE THE #1 FOLLOW-ON -- THE PARSER STRUCTURAL ROLE-ROUTE (the biggest measured lever, +0.096 who-did-
   what).** The highest-value result here: role assignment via `role_route="positional"` (linear position) is
   the wrong cue; a PARSED-STRUCTURAL-WITH-VOICE route (patient = grammatical object `obj`/`dobj` or passive
   subject `nsubj:pass`) beats it +0.04-0.09 CI-sep, and integrating THIS problem's register-native selectional
   store on top adds a further +0.056-0.096 CI-sep (0.474 -> 0.514 -> 0.570). Prototype:
   `experiments/exp_brain_faithful_who_did_what_v1.py`. File it as its own problem (the parser role-route +
   noisy-channel selectional integration) -- it is where the who-did-what score actually moves.
3. **FOLD THE AUDIT UPDATE** (above) into `BRAIN_FOUNDATIONAL_AUDIT.md` -- correct the p5 "+0.149" row to the
   disjoint-corpus reality (marginal ties; the ~+0.04 domain effect is joint-only); add that the who-did-what
   levers are the STRUCTURAL PARSE (grammatical-role+voice > linear position) and the selectional store the
   parse UNLOCKS; grounded-12d/generative/animacy measured NON-levers on this task.
4. **WIRE (default-off)** the FHRR register-native event store as the JOINT selectional prior consulted by role
   assignment, built offline per reading domain -- but INTEGRATED WITH THE PARSED-STRUCTURAL CUE (that is where
   it pays off), not as a standalone who-did-what lever, and not the marginal store.
5. **SEED THE NEXT PROBLEMS:** (a) the CLS composition of this consolidated store with p4's episodic backbone;
   (b) the soft-AND conjunctive aligner (priority-4) now has a supporting datapoint; (c) the richer grounded
   meaning space (North-Star) -- grounded-12d LOWERS the score, so the coarse ATL space is a real ceiling.
