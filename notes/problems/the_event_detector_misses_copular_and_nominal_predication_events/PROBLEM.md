---
priority:
review: EXCELLENT
review_text: Completes the event-detection front-end tense-agnostically — recovers the two non-verbal predication classes the keystone misses (COPULAR states via the `cop` dependency arc; DEVERBAL nominal events via event-denoting-ness + argument structure + boundedness), raising event RECALL CI-separated end-to-end through the LIVE SituationReader.read() while holding verbal-event precision BYTE-IDENTICAL (purely additive, W5/W12). Reverified 14/14 FIRST-HAND. Copular (the CLEAN class): UD-EWT recall 0.7951→0.9448 (+0.1497 [0.1344,0.1650] CI-sep over keystone AND +0.1330 over the info-free twin), cop-class precision 0.857, overall precision essentially neutral (−0.0089 [−0.0150,−0.0031]) — a clean structural win riding a HIGH-fidelity local relation even at UAS 0.79. Nominal: LitBank recall +0.0873 CI-sep + CROSS-CORPUS MAVEN modern-Wikipedia +0.1845 (the signal GENERALIZES and is LARGER on modern factual prose), nominal-class precision 10.2× the non-verb base rate, info-free twin LOSES on every corpus. The nominal precision wall (~0.20 absolute) was DRILLED to its brain mechanism (episodic event-token individuation; the event-vs-kind reading of a bare deverbal noun is discourse-model-bound) and PROVEN model-bound by CAN-FAIL-testing all three local proxies the literature offers (governing-predicate coercion, countability — which FAILED BACKWARDS on fiction — and event-anaphora) → the residual is irreducibly discourse-bound, not a lexicon gap (independently: the keystone's own verbal precision on LitBank is 0.27 = the gold ceiling, so 0.20 is within ~7pts). NON-CIRCULAR deflation (34.8% of nominal "misses" are lemmas gold-annotated as EVENT elsewhere in-corpus). ADJACENT-COMPONENT de-risking: built + validated the entity-state (HOLDER,PROPERTY) representation the copular states feed (0.677R/0.872P CI-sep over floor+twin; holder|property 0.939). Two tempting shortcuts (existential suppressor, countability) TESTED and REJECTED rather than shipped. Grade EXCELLENT: two classes with OPPOSITE structural profiles the brain predicts (copular clean+local, nominal context-bound), each measured on its PROPER gold, cross-corpus generalization, an honestly-drilled-and-proven-model-bound wall, and adjacent-component de-risking — the extraction-COMPLETENESS half of the front-end, cleanly.
---

> ## ✅ SOLVER REVIEW -- EXCELLENT (integrated by strategy 2026-08-31)
> **Why EXCELLENT, specifically:** event-hood is not tied to the verb slot in the brain (neo-Davidsonian; Bach 1986),
> and the solver recovered BOTH missing predication classes with the brain's actual distinction — a copular/predicative
> KIMIAN STATE (Maienborn 2005) read off the droppable-copula `cop` relation, binding HOLDER+PROPERTY; and a deverbal
> NOMINAL event routed through the verb machinery (Garbin 2012) via event-denoting-ness + argument structure + boundedness.
> The key structural insight is that the brain PREDICTS which class is clean: copular rides a LOCAL dependency relation
> (`cop`, high-fidelity even at UAS 0.79 → precision 0.857), while the bare-nominal event/kind reading is intrinsically
> discourse-model-bound (→ precision ~0.20, honestly context-bounded).
> **Reproduced under my check:** re-ran `verification/test_copular_nominal_event_detector_organ.py` — 14/14 PASS,
> scaffold-free, driving the LIVE `SituationReader(tense_agnostic_events=True).read()`. Copular UD 0.7951→0.9448
> (+0.1497 CI-sep, cop-class prec 0.857, overall-prec neutral −0.0089); nominal LitBank +0.0873 CI-sep + MAVEN
> cross-corpus +0.1845; class-prec 0.1994 vs twin 0.0195 (10.2×); deflation 0.348 (958/2751); verbal fires
> BYTE-IDENTICAL across modes AND == the landed keystone (219 preds, W5/W12); entity-state 0.677R/0.872P vs floor/twin
> CI-sep, holder|property 0.939 — all reproduce from source.
> **Adversarial audit (what could have faked it):** (1) Is the nominal recall gain just "fire more non-verb tokens"?
> No — the info-free count-matched twin LOSES on recall AND on class-precision on every corpus; the gain is event-hood
> alignment. (2) Is the low nominal precision hidden model error? No — the NON-CIRCULAR deflation test (lemma annotated
> as event elsewhere) + three local proxies tested-and-failed prove it discourse-bound, and it's within ~7pts of the
> gold's own verbal-precision ceiling. (3) Does it regress verbal precision? No — verbal-class fires are byte-identical
> (purely additive, checked structurally).
> **Honest bounds (solver-reported, so they cap nothing):** absolute nominal precision is ~0.20 (gold-deflated +
> discourse-bound); copular carries a 0.9-pt overall-precision cost (the new class is slightly less precise than verbs;
> the VERBAL precision itself is invariant); MAVEN/LitBank generalization is 19c-fiction + modern-Wikipedia (no
> hand-adjudicated modern narrative gold at scale).
> **Landing (QUEUED, Q111 — COUPLED with p5 into ONE extraction-front-end landing):** behind a default-off
> `copular_nominal_events` flag, extend `_tense_agnostic_extract` (byte-identical when off) to ALSO fire a `state`-sort
> node on each `cop` predicate (HOLDER=nsubj, PROPERTY=predicate) and an `event`-sort node on confident event-denoting
> nouns (bake the WordNet event lexicon to a static JSON asset → no nltk at runtime), plus a new
> `SituationModel.entity_states` field routed from the state nodes (NOT into the dynamic-event codec). Reference impl
> `experiments/_copular_nominal_events.py`. The faithful fix for the nominal residual is the incremental parser +
> situation model (p2, just owner-DONE) — one lever.

# PROBLEM: the just-landed tense-agnostic event detector (the p1 keystone) fires an event at every UPOS==VERB — which took verbal-event recall from ~0.33 to ~0.95, but by construction it MISSES events carried by NON-verbal predication: COPULAR/predicative states ("Sarah IS a doctor", "the room was cold", "he SEEMED nervous") and NOMINAL/deverbal events ("the DESTRUCTION of the city", "her ARRIVAL", "after the EXPLOSION"). The brain does not restrict event-hood to the verb slot: a state or a nominalised happening is an event node in the situation model. Build the missing detector: recover copular/predicative and nominal-event predications as events, tense-agnostically, WITHOUT regressing the verbal-event precision the keystone holds — so the reader's event set is COMPLETE, not just verb-complete.

**slug:** `the_event_detector_misses_copular_and_nominal_predication_events` — **opened:** 2026-08-31 by the strategy
session (the p1 keystone's own named boundary: "copular/nominal predications are NOT fixed — the UPOS==VERB target
class excludes them"). **status:** OPEN — a MECHANISM + BUILD problem. You build + validate in `experiments/`;
strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGH. Event RECALL caps every downstream
> dimension (the keystone proved it: fixing verbal-event recall lifted who-did-what, causation candidates, roles).
> Copular/nominal events are the named remaining recall gap after the keystone, and they carry a LOT of situation-
> model content (states = the entity-state dimension; nominal events = causation/temporal nodes). North-Star-central
> (a COMPLETE event set is the clean-foundation input). Ranked with the incremental-parser (p2, precision half) and
> above refinements. **Re-rank per the owner.** ⚠️ Compose with the landed `tense_agnostic_events` flag (turn it ON
> for the measurement — this is the recall population it extends); do not re-derive the verbal-event result.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
We just fixed the reader so it catches almost every event that's expressed with a verb. But plenty of what happens
in a story isn't a verb: "Sarah is a doctor" and "the room was cold" describe states; "the destruction of the city"
and "after the explosion" are events hiding inside nouns. The reader misses all of these, so its picture of "what is
true / what happened" has holes. Teach it to also catch these non-verb events and states — without breaking the
verb-event accuracy we just won — so its list of what's going on in the story is complete.

## 2. WHY THIS ONE
Event recall is the master lever — the keystone proved that fixing it cascades to who-did-what, causation, and roles.
Copular/nominal predications are the named remaining recall gap, and they carry high-value content: states feed the
entity-state dimension; nominal events feed the causal and temporal dimensions. A situation model built on a
verb-only event set is structurally incomplete. This is the completeness half of the clean-foundation input (the
keystone did the verbal-recall half; the incremental parser, p2, does the precision half).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate):** event-hood is NOT tied to the verb category. The neo-Davidsonian event variable attaches to
  predication in general — copular/predicative clauses assert a STATE (a stative eventuality; Bach 1986 eventuality
  types), and DEVERBAL NOMINALS denote events/processes (Grimshaw 1990 argument-structure nominals; nominalisation
  is a productive event-denoting device). Comprehension builds an event/state NODE for each (Zwaan & Radvansky
  situation-model states + events). Copular predication binds a SUBJECT to a PROPERTY/IDENTITY (the entity-state
  dimension); a nominal event binds its participants via of-/genitive/by arguments.
- **OUR-INVENTION (build + sweep):** the exact detectors — the copular/predicative trigger (BE/SEEM/BECOME +
  predicate nominal/adjective; the tagger's own POS) and the nominal-event trigger (deverbal/eventive-noun lexicon,
  e.g. WordNet event/act/process hypernyms + -tion/-ment/-al morphology + the argument-taking test). Glass-box, no LLM.

## 4. MEASURED vs INFERRED
- **MEASURED (the gap):** the landed `tense_agnostic_events` detector fires on UPOS==VERB only — copular predicate
  complements and deverbal nominal events are OUT of that class by construction (the p1 SOLVED names this explicitly).
- **INFERRED (you must measure):** whether a copular + nominal-event detector RECOVERS these events (recall on a gold
  that annotates copular/nominal events — e.g. UD copula `cop`/`nsubj` + a deverbal-nominal gold, or LitBank/MAVEN
  event triggers which INCLUDE nominal events) CI-separated over the verb-only detector, WITHOUT a CI-separated
  PRECISION regression on the verbal events, with the info-free twin (fire on random non-verb tokens matched in count)
  LOSING, measured END-TO-END through `SituationReader.read()` with `tense_agnostic_events=True`.

## 5. ALREADY TRIED / DO NOT RE-RUN
- The verbal-event tense-agnostic detector (p1, landed) — this EXTENDS it (copular + nominal on TOP of UPOS==VERB);
  do not re-derive the verbal result; compose with the flag ON.
- The force/causation typing + the foreground gate (p2/p3) — those TYPE/FILTER events; this DETECTS a new event
  class. Compose, don't collide (a nominal event may then be typed/gated downstream).

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/situation_reader.py::_tense_agnostic_extract` + `_extract_events` (the landed detector this extends) and
  the p1 SOLVED (`the_extraction_front_end…`) copular/nominal boundary note.
- Pick a gold that ACTUALLY annotates copular + nominal events (LitBank/MAVEN realis-event triggers include nominal
  events; UD gives `cop`/`nsubj` for copular) — MIND THE CORPUS-AGE CONFOUND (prefer modern/held-out).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On a REAL corpus whose gold includes copular + nominal events (LitBank/MAVEN event triggers + UD copula), through
`SituationReader.read()` with `tense_agnostic_events=True`:
- **PASS =** the copular+nominal detector raises EVENT RECALL CI-separated over the verb-only keystone detector,
  WITHOUT a CI-separated PRECISION regression on the verbal events, with the info-free twin (fire on random non-verb
  tokens, count-matched) LOSING CI-separated; report recall/precision operating point + CI half-width + null p95;
  report the copular vs nominal split honestly (one may be cleaner than the other).
- **A rigorous NEGATIVE is a full PASS:** if copular/nominal predications cannot be detected from structure without a
  precision cost (e.g. deverbal nominals are too ambiguous with entity nouns without deeper parsing), name why —
  enumerated — which points the completeness work at the incremental parser (p2) instead.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`; the detector composes in `_extract_events`/`_tense_agnostic_extract` (add copular + nominal
  triggers behind the same flag, or a coupled flag). Witness recomputes recall + precision from source through the live
  `read()`. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. This is the extraction-COMPLETENESS half
  of the clean-foundation input (the keystone did verbal recall; p2 does precision); it composes with the landed
  `tense_agnostic_events` keystone.


## DO NOT QUOTE / DO NOT REDO
- 🚫 **Nominal-class precision ~0.20** — gold-DEFLATED (34.8% of "misses" are events elsewhere in-corpus) AND intrinsically discourse-model-bound; do NOT quote it as detector error or re-attempt a static local cue to "fix" it (governing-predicate coercion / countability / event-anaphora all can-fail-TESTED and closed).
- 🚫 Copular vs nominal numbers are on DIFFERENT golds (UD `cop` vs LitBank realis-event); do not cross them. INTEGRATED (EXCELLENT) — build ON it; the faithful nominal fix is the incremental parser + situation model.
