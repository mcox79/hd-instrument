---
priority: 2
review:
review_text:
---

# PROBLEM: the reader's per-verb selectional/event knowledge (which things a verb acts on) is learned from the WRONG DOMAIN. A rigorous oracle-ladder dissection proved DOMAIN MATCH of the selectional corpus is the #1 lever for who-did-what (+0.149, ~80% of the available gap) — NOT features, NOT the mechanism, NOT the combiner, NOT parse-cleanliness. Build a deployable, no-gold, REGISTER-NATIVE selectional/event store (offline from a DISJOINT domain-matched corpus, bound with the substrate's FHRR event codec — REUSE `bound_event_backbone`) and prove it recovers the domain lever on held-out who-did-what over the out-of-domain store, or locate why it doesn't.

**slug:** `the_selectional_event_store_is_learned_from_the_wrong_domain_needs_a_register_native_corpus` — **opened:**
2026-09-01 by the strategy session, LIFTED from the solver-drafted `PROPOSED_FOLLOWON_domain_matched_selectional_store.md`
(the owner-DONE problem `the_plausibility_prior_is_a_coarse_centroid_needs_a_structured_verb_role_exemplar_store` — the
solver definitively located this wall + drafted the brief; owner asked to issue it). **status:** OPEN — a BUILD problem
(a register-native offline selectional/event store, FHRR-bound). Strategy lands any hdlab wire (Q111, default-off,
witnessed). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (RE-RANK PER THE OWNER):** filed at `2` — HIGH, just under the north-star meaning organ (1). This is
> the DEFINITIVELY-LOCATED #1 lever for who-did-what role assignment: a measured +0.149 domain effect (~80% of the gap),
> with every other candidate ruled out WITH NUMBERS (features/mechanism/combiner/parse). It UNIFIES with the 19c
> register-drift wall (same root cause) and it is the same offline-foundation build the learner-on roadmap wants.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation, replicate
> that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker after your tools plateau.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method
> conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested,
> or a SPECIFIC reason it cannot be. Exhausting engineering variations is NOT convergence.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather high-value adjacent info (a control /
> curve / ablation / 2nd gold); enumerate what's LEFT + do it; MAP adjacent bottlenecks (name component + on-disk
> evidence + leverage) and EVALUATE each for brain-fidelity + optimization (seeds the next problem); hit a wall → run a
> FINER brain-foundational research drill, never stop. Implement → test (can-fail, strongest real floor, twin LOSING) →
> iterate. CANCEL + submit only when the mechanism bar is met AND the checklist yields nothing more.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any
> deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader decides who-did-what partly from per-verb knowledge of "what kinds of things this verb usually acts on" (you
READ books, you DRIVE cars). That knowledge is currently learned from Simple-English-Wikipedia — the WRONG kind of text
for what we test on. When we build the exact same knowledge from text of the SAME KIND as what is being read, who-did-
what accuracy jumps by nearly the whole available gap, even with the same imperfect parser. So the reader needs to learn
its per-verb / event knowledge from its OWN reading domain (register-native), not from a generic pile of unrelated text.

## 2. WHY THIS ONE
It is the DEFINITIVELY-LOCATED wall for who-did-what role assignment. A rigorous oracle-ladder dissection
(`exp_wall_dissection_v1.py` + `exp_wall_corpus_axis_v1.py`) isolated the binding constraint and ruled out every other
candidate WITH NUMBERS: NOT the grounding/feature space (grounded similarity adds +0.20 over pure memorization), NOT the
mechanism (FHRR role-filler binding is faithful and beats the shortcut), NOT the combination (a learned CLS arbitrator
ties the better single system), NOT parse cleanliness (a minor +0.036). It is DOMAIN MATCH of the selectional/event
corpus (+0.149, ~80% of the gap). It UNIFIES with the 19c register-drift wall (same root cause): selectional/event
knowledge is DOMAIN/REGISTER-RELATIVE.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: the brain reads a register well because it has READ that register — selectional/event knowledge is the
CONSOLIDATED statistical structure of the reader's own experienced language (Complementary Learning Systems,
McClelland-McNaughton-O'Reilly 1995; generalized event knowledge, McRae/Elman; thematic fit is learned from experienced
verb-argument co-occurrence, McRae et al. 1998). The neocortical semantic store is trained by consolidating episodic
events from the reader's OWN input stream. So the store must be grown from DOMAIN/REGISTER-matched text, and the
brain-foundational representation is the substrate's FHRR role-filler BINDING (already wired as
`hdlab/bound_event_backbone.py` + `hdlab/event_bundle.py`; SEM/Franklin 2020).

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** at FIXED GloVe representation on the QA-SRL non-reversible slice — simplewiki-parsed
  store 0.363 → IN-DOMAIN-parsed (same noisy parser, no gold, leave-one-sentence-out) 0.518 → in-domain-gold 0.551.
  DOMAIN effect +0.149 CI[+0.115,+0.185]; parse-quality effect +0.036 CI[+0.010,+0.062]. The domain win is CLEAR at the
  MARGINAL (verb→patient) exemplar store (+0.149). At the JOINT FHRR (subj,verb,obj) store, a 2M-token in-domain corpus
  is TOO SPARSE (the noisy parser often misses the subject on the non-canonical slice) and it LOSES to out-of-domain
  (−0.055) — a DATA-DENSITY effect, NOT a domain refutation: the joint/FHRR store needs a LARGER domain-matched corpus
  than the marginal store. Grounded similarity generalizes (exact-match ceiling 0.360 < gold-store 0.556).
  Oracle(episodic+semantic) 0.61; a learned arbitrator ties the better single system (~0.455).
- **INFERRED (you must measure):** whether a DEPLOYABLE, no-gold, register-native selectional/event store — built
  offline from a genuinely DISJOINT domain-matched corpus (not the test corpus itself) and bound with the substrate's
  FHRR event codec — recovers the +0.149 domain lever on HELD-OUT who-did-what, and how it composes with the wired
  `bound_event_backbone`. (The residual to human ~0.55→~0.83 is a SECOND wall — impoverished input — out of scope here.)

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- Do NOT re-run: richer features (Binder-65/GloVe-300 — measured NON-lever for this wall), a cleverer combiner / learned
  arbitration / hybrid (measured dead-end — the arbitrator ties the better single system), parser register-adaptation
  via self-training (REFUTED for 19c, stalls), a bigger OUT-OF-DOMAIN corpus (wrong axis).
- BUILD ON: the FHRR role-filler binding demonstration (`exp_fhrr_event_role_assignment_v1.py`), the in-domain parse
  (`exp_wall_corpus_axis_v1.py`), the wired `bound_event_backbone` / `event_bundle` (do NOT reinvent event binding — p4,
  owner-DONE).

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS (do these before proposing anything):** (1) understand ALL the existing organs — `python
  tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read the parent SOLVED.md
  (`the_plausibility_prior_is_a_coarse_centroid…`) IN ITS ENTIRETY — esp. the DEFINITIVE WALL DISSECTION section — plus
  the p4 `bound_event_backbone` SOLVED (the FHRR event store you build on). Reuse, don't reinvent.
- Re-run `exp_wall_corpus_axis_v1.py` and confirm on your OWN recomputation that the domain axis dominates (+0.149) and
  parse-quality is minor (+0.036).
- Read `hdlab/bound_event_backbone.py` + `hdlab/event_bundle.py` + `hdlab.binding` (the wired FHRR event store).

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a no-gold, REGISTER-NATIVE selectional/event store built OFFLINE from a DISJOINT domain-matched corpus, bound with
the substrate's FHRR event codec, RECOVERS who-did-what CI-separated over the current out-of-domain (simplewiki) store on
a HELD-OUT domain-matched who-did-what test, with a verb-shuffled twin LOSING CI-sep and a domain-scramble control (same
corpus, wrong-domain labels) losing. A rigorous located negative (the domain lever does not transfer to a genuinely
disjoint corpus) is a full PASS if it names why. Report CI half-width + null p95. Corpus-age/domain confound: the win
must be DOMAIN, not leakage — use a DISJOINT domain corpus, NOT the test corpus (the parent used leave-one-sentence-out
as a probe; the deliverable needs a disjoint corpus).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. Reuse: `exp_wall_corpus_axis_v1.py` (in-domain parse),
`exp_fhrr_event_role_assignment_v1.py` (FHRR mechanism), `hdlab.binding` / `hdlab.event_bundle` /
`hdlab.bound_event_backbone` (the wired FHRR event store). Strategy lands any hdlab wire (Q111, default-off, witnessed).
Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the selectional/event store is domain/register-relative; the
corpus is the lever, not features/mechanism/combiner).

## DO NOT QUOTE
- Do NOT quote the parent's in-domain +0.149 as YOUR result — it used leave-one-sentence-out on the TEST corpus (a probe,
  not a disjoint deliverable). Re-measure on a genuinely disjoint domain-matched corpus.
- Do NOT claim a win without the domain-scramble control (the DOMAIN, not any in-corpus signal, must do the work).
- Do NOT use an external LLM as the store or the corpus builder (the invariant). A static offline domain-matched
  foundation IS admissible; the inference-time store + read stay glass-box.
