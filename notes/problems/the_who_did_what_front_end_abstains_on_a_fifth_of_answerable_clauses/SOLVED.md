---
problem: the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses
status: SOLVED
bar: "PASS = a coverage recovery (attempt every finite verb + parser-robust candidate building, glass-box, NO LLM) that raises the LIVE reader's EFFECTIVE end-to-end who-did-what (abstention counted as wrong) CI-separated over the current 0.629, WITHOUT regressing the picked-clause NP-head precision (an explicit no-regression check on the accuracy the parent landed), with an info-free twin (recover random clauses) LOSING. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the dropped clauses are genuinely un-recoverable glass-box, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "Effective end-to-end who-did-what (abstention=wrong), 669 clean-19c direct-object clauses, scorer pick==gold_head: LIVE wired 0.6293 -> RECOVERED 0.9806, +0.3513 CI[+0.3154,+0.3886] half=0.0366 null_p95=0.0375 (the more brain-faithful STRUCTURAL-DO refinement 0.9851). Modern QA-SRL (n=1261) 0.5678 -> 0.9025, +0.3347 CI-sep. Present-accuracy 0.807 -> 0.981 (precision UP, not regressed)."
floor: "Strongest floor actually run = the reader's OWN better route, LIVE positional 0.7294 (RECOVERED beats it +0.2511 CI[+0.2167,+0.2840]). Also: LIVE wired 0.6293; best-available-parser wired floor (updated arc-eager, UD-EWT UAS 0.842) 0.6308 -- the abstention is parser-INDEPENDENT, not a strawman floor."
controls: "(1) info-free twin = full coverage + UNIFORM-RANDOM post-verbal pick 0.4185, LOSES CI-sep (REC-vs-twin +0.5620). (2) NO-REGRESSION: of 421 clauses the live reader already got right, RECOVERED keeps 416 (5 individual flips, all hard ditransitive/copula/distant-noun cases); present-accuracy 0.807->0.981. (3) INTRANSITIVE precision control (constructed, can-fail): the naive soft rule over-generates on 100% of intransitives; the brain-faithful STRUCTURAL-DO rule abstains correctly 0.975 AND recovers the 47 the hard gate loses AND does not regress the main gold (0.9851>=0.9806). (4) fair-floor: the UPDATED arc-eager parser recovers only 1/669 -> abstention is not parse-quality. (5) first-hand reader reproduces the stored wired_pick/pos_pick 100%. (6) per-cause ablation is exhaustive (recovered-correct sums exactly to 0.9806)."
files_changed: "experiments/exp_whodidwhat_coverage_diagnosis_v1.py, experiments/exp_whodidwhat_coverage_recover_v1.py, experiments/exp_whodidwhat_coverage_parser_floor_v1.py, experiments/exp_whodidwhat_coverage_transitivity_control_v1.py, experiments/exp_whodidwhat_verb_id_recoverable_v1.py, verification/test_whodidwhat_coverage.py, notes/problems/the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_whodidwhat_coverage.py"
---

# SOLVED — the who-did-what front end silently abstains on a fifth of answerable clauses

## What this problem asked, and the answer in one line
The live reader picks the patient right ~98% of the time WHEN it answers, but stays silent on 22% of answerable
clean-19c clauses, so its EFFECTIVE end-to-end who-did-what (silence counted as wrong) is only **0.629**. I diagnosed
the 22% first-hand into three exact causes, recovered them with a brain-faithful robust role path, and lifted the
effective end-to-end to **0.981** (+0.3513 CI-separated, info-free twin loses, no precision regression, generalizes
to modern text). The abstention was **never** a "the parser could not find the noun" problem — it is three
OUR-INVENTION precision gates mis-firing on 19c prose.

## 1. The diagnosis — first-hand, exhaustive (cell: exp_whodidwhat_coverage_diagnosis_v1)
I re-ran the actual `hdlab.situation_reader.SituationReader` (the "strong" reader the gold was built with:
`role_route=wired`, `tense_agnostic_events=True`, `verb_subcat_gate=True`) first-hand on the 669 clean-19c
direct-object clauses. It reproduces the gold's stored `wired_pick`/`wired_no_event` fields **100%**. Every content
noun is handed to the reader as a candidate mention, so abstention is NOT a missing-candidate problem. The 147/669
(22%) abstentions decompose **exactly** (0 residual "other"):

| cause | n | what it is | brain verdict |
|---|---|---|---|
| **speech-verb quotative over-fire** | **80** | `role_route=wired` treats EVERY speech verb (call/tell/ask/show/reply/warn/…) as a quotative inversion ("said John") and FORCES patient=`?`, discarding the real direct object ("call **me**", "tell my **wife**"). The `positional` route recovers **all 80** (strict subset). | OUR-INVENTION over-fire |
| **verb_subcat hard-threshold suppression** | **47** | `verb_subcat_gate` deletes the patient when a modern-corpus transitivity propensity < 0.35, vetoing genuinely-transitive 19c verbs. Hits both routes. | OUR-INVENTION hard veto |
| **no-event (POS mis-tag)** | **20** | the in-substrate UD tagger mis-tags the 19c verb as ADJ/ADP/ADV/NOUN ("the lake **presents**…", "**obey**", "**spoil**", "**round**"), so the (Davidsonian, every-UPOS==VERB) tense-agnostic detector never fires. | upstream tagger recall |

The decisive number: **the wired parse-routing is NET-NEGATIVE for patient coverage** — effective 0.629 (wired) vs
0.729 (positional), a −0.100 cost, entirely the 80 speech-verb quotative vetoes. All 80 are speech verbs; 0 are
non-speech parse-attachment failures. So a "better parser" is the wrong lever.

## 2. Fair floor — I opted into the updated parser (cell: exp_whodidwhat_coverage_parser_floor_v1)
Per the standing instruction to test against the best available parser, I re-ran the wired reader with the promoted
**arc-eager parser** (`parser_arceager=True`, UD-EWT UAS 0.775 → 0.842). It recovers **1 of 669** clauses (effective
0.6293 → 0.6308; event-no-patient stays 127, no-event stays 20). The abstention is **parser-independent** — it lives
in the three gates ABOVE the parser, so the floor I beat is not a strawman weak parser.

## 3. The recovery — brain-faithful robust role path (cell: exp_whodidwhat_coverage_recover_v1)
The RECOVERED path is the Competition-Model robust role assignment (word-order-primary competition over parser-free
NP-head candidates, attempting EVERY finite verb, transitivity a SOFT cue, no quotative veto) — exactly the parent's
validated `role_patient_full_fix`, REUSED. Effective end-to-end on the 669:

| arm | effective | note |
|---|---|---|
| A0 LIVE wired | **0.6293** | the deployed floor |
| A1 LIVE positional | 0.7294 | the reader's OWN better route (recovers the 80 speech) |
| **RECOVERED** | **0.9806** | attempt-every-verb + parser-free NP-head competition + soft cues |
| info-free twin (random post-verbal pick) | 0.4185 | LOSES |

- **REC vs A0 (wired):** +0.3513 CI[+0.3154, +0.3886] half=0.0366 **null_p95=0.0375** → CI-separated AND over null.
- **REC vs A1 (positional, the strongest floor):** +0.2511 CI[+0.2167, +0.2840] → CI-separated.
- **REC vs info-free twin:** +0.5620 CI[+0.5247, +0.6009] → CI-separated (the recovery's accuracy is structural, not luck).

**Per-cause ablation (0.629 → 0.981 decomposed, sums exactly):** already-picked-correct 421→416 kept (+0.622),
already-picked-wrong 101→99 fixed (+0.148), speech-quotative 80→74 recovered (+0.111), verb_subcat 47→47 (+0.070),
no-event 20→20 (+0.030).

**NO-REGRESSION:** present-accuracy (on the clauses it answers) rises **0.807 → 0.981**; of the 421 clauses the live
reader already got right, RECOVERED keeps 416. The **5 individual flips** are genuinely hard multi-candidate cases:
one ditransitive ("gave [master] [errand]" — the parse router correctly gets the recipient, positional doesn't model
it), one copula/raising ("seemed … people"), three where grounded competition chose a distant noun. Net precision is
up, not down — the 5 are the residual value of the parse router, which the proposed wire deliberately keeps as an
ADDITIVE override (below).

**Generalization (modern QA-SRL, n=1261):** effective 0.5678 → 0.9025, +0.3347 CI-separated; present-accuracy 0.9025.
The same mechanism recovers coverage on modern text — the gates cost coverage in both registers, and the robust path
is register-independent.

## 4. Is the wall brain-faithful? (the opening move, and the user's standing question)
The three gates are each LESS brain-faithful than the recovery — confirmed by a literature drill converging across
five independent literatures:
- **Parse-dependence (the 80):** the brain does NOT require a complete syntactic parse to assign the patient; it
  assigns roles incrementally from robust cues (word order, animacy, morphology) that survive parse failure —
  Competition Model (Bates & MacWhinney 1989), good-enough/shallow processing (Ferreira 2002; Ferreira & Patson
  2007), Now-or-Never bottleneck (Christiansen & Chater 2016), constraint-satisfaction (MacDonald et al. 1994),
  noisy-channel (Gibson et al. 2013). Principled abstention-on-parse-failure has **no** empirical analog — garden
  paths yield a degraded/hybrid reading, never silence. → the parser-free positional recovery is MORE faithful.
- **Transitivity (the 47):** no literature has verb bias fully BLOCK bottom-up argument evidence; strong local
  plausibility OVERRIDES verb bias when they conflict (Garnsey et al. 1997; Trueswell et al. 1993; Altmann & Kamide
  1999). → a soft, overridable transitivity cue is MORE faithful than a hard threshold veto. (Honest caveat from the
  drill: the brain still DISCOUNTS an overridden reading rather than forgetting the prior — a graded confidence, not
  a binary flip; our recovery treats it as a present-object override, a small simplification worth noting.)
- **Verb identification (the 20):** the brain identifies the predicate from clausal position + agreement/tense
  morphology + closed-class scaffolding, not a static category lookup (MacDonald 1993; Mintz 2003 frequent-frames;
  Christophe/Morgan & Demuth function-word bootstrapping). → the 19c mis-tagging is an adjacent-component
  (tagger-recall) limitation, not a fundamental wall.
- **Register-independence (honest caveat):** consistent with the general adaptive-parser literature (Fine et al.
  2013), but **no direct archaic-register study was located** — I do not claim this as settled; the modern+19c
  generalization result is the evidence I actually have.

Not a single one of these is a fidelity wall we cannot cross — each fix moves the substrate TOWARD the brain's
mechanism, not toward a convenient tool.

## 5. PROPOSED hdlab WIRE (strategy lands it — Q111, default-off, witnessed; I do NOT edit hdlab)
A surgical, precision-preserving change to `hdlab/situation_reader.py::_read_events_wired`, not a wholesale
replacement — each step recovers one cause while keeping the router's genuine passive/ditransitive value:
1. **Quotative-on-evidence (recovers 80):** apply the speaker-inversion `patient='?'` branch (line ~1031) ONLY when
   the clause actually has quote structure, not on `is_speech_verb` lexical class alone; otherwise assign the patient
   normally. Equivalent minimal form: never let the quotative branch leave `patient='?'` when a post-verbal nominal
   candidate exists — fall back to the positional patient.
2. **Positional fallback in the router (backstop):** the wired path must never emit `patient='?'` when the positional
   `_assign_roles` found one; the router `theme` is an ADDITIVE override (keep it — it is what correctly handles the 5
   ditransitive/passive cases), never a delete.
3. **STRUCTURAL direct-object filter (recovers 47, replaces the verb_subcat veto — REFINED by the deepening below):**
   restrict the patient candidate set to BARE post-verbal nominals (no intervening preposition) before the pick — a
   patient is structurally a DIRECT object; a preposition-governed oblique is never the patient. This recovers the 47
   the hard gate false-suppressed AND correctly abstains on genuine intransitives (measured 0.975), AND slightly
   IMPROVES the main gold (0.9806 -> 0.9851). It subsumes the `verb_subcat_gate`'s protective purpose without its
   false-suppression, and needs no transitivity threshold at all.
4. **NP-head reduction** is already landed (`hdlab/np_head_reduce.py`) and should stay on this path (the accuracy half).
5. The **20 no-event** is a LOCATED sub-negative: it is upstream POS-tagger recall on 19c verbs, not a role-assignment
   defect — recovered here only because the who-did-what task supplies the verb index. It is filed as follow-on
   problem 1c below, not silently folded in.

Reference implementation of the full recovered path: `experiments/exp_whodidwhat_full_fix_v1.role_patient_full_fix`.

## 6. DEEPENING — two pushes that made the fix more brain-faithful and closed my own gaps
A second research drill (verb/noun category ambiguity, ditransitive linking, singleton referents) plus two new cells:

**(a) STRUCTURAL direct-object rule beats "soft transitivity" — a cleaner mechanism, discovered by pushing.**
(cell: `exp_whodidwhat_coverage_transitivity_control_v1`.) My first recovery softened the transitivity veto, and I had
flagged its no-regression as *argued, not measured*. I measured it on a constructed can-fail INTRANSITIVE control ("the
man arrived at noon", "she sat by the fire", …; correct answer = no patient): the naive soft rule OVER-GENERATES on
**100%** of them (assigns the oblique as patient) — a real regression. The brain-faithful fix is not a softer
transitivity threshold at all: **the patient is structurally a direct object, so restrict candidates to BARE
post-verbal nominals (no intervening preposition); a preposition-governed oblique is never the patient** (grounded in
the definition of the patient role + structural DO evidence — Goldberg construction linking; Bresnan 2007). This
STRUCTURAL-DO rule: recovers the 47 hard-suppressed clauses (1.00), abstains correctly on **0.975** of the
intransitive control (vs the hard gate's 1.00), and *improves* the main gold **0.9806 → 0.9851**. It subsumes the
`verb_subcat_gate` entirely — no transitivity number needed. This is the recommended form of wire-step 3.

**(b) The 20 no-event is SOLVABLE-in-principle, not a wall — but not trivially (honest located sub-result).**
(cell: `exp_whodidwhat_verb_id_recoverable_v1`.) The mis-tagged 19c verbs ARE lexically verbs (WordNet verb-reading on
**18/20**), confirming the research verdict that verbhood is recoverable from lexicon+structure, not a static tag. But
a cheap glass-box heuristic does NOT cleanly recover them: "verb-reading + any preceding subject" gets 75% at an
unusable 5.0 false-verbs/sentence; a Mintz frequent-frame cue (N-[verb]-N, no verb in the predicate slot) gets only
30% at 0.8 FP/sentence. So a clean recovery needs REAL clause-level predicate identification (the research's
parser-attachment-as-verbhood-override), which is the adjacent component — filed as follow-on 1c with this evidence,
NOT claimed as solved here. "If the brain can do it we can too" holds; the honest scope is that it needs a mechanism,
not a heuristic.

## 7. ADJACENT-COMPONENT MAP — brain-fidelity, capability, limitation, opportunity (to seed the next problems)
Evaluated while solving this, per the standing instruction to map adjacent components:

| component (hdlab) | brain status | capability now | limitation found | opportunity / next problem |
|---|---|---|---|---|
| **event detection** (`_extract_events` / `tense_agnostic`) | Davidsonian per-verb = PINNED ✓; verb-IDENTIFICATION by static UD tag = OUR-INVENTION deviation | fires at every UPOS==VERB (recall 0.97 through the reader) | capped by UD-tagger 19c verb recall — the 20 no-event; verb-ID should be position+morphology, not a tag | **1c: register-robust predicate identification** (parser-attachment/frame verbhood override; evidence in cell (b)) |
| **role routing** (`_read_events_wired`, parse route) | Competition-Model incremental role assignment = PINNED; full-parse-gated routing = deviation | richer passive/ditransitive roles when the parse succeeds | net-NEGATIVE for patient coverage on 19c (−0.10); quotative veto + no positional fallback | **this problem's wire** (demote router to additive override; positional/structural-DO primary) |
| **transitivity gate** (`verb_subcat`) | verb bias = graded overridable cue (PINNED); hard threshold = deviation | suppresses spurious intransitive patients | false-suppresses genuinely-transitive 19c verbs (47) | **subsumed** by the STRUCTURAL-DO rule (push (a)) — candidate for retirement on this path |
| **quotative inversion** (`is_speech_verb` branch) | speaker-inversion is real; lexical-class trigger = deviation | handles "'…,' said John" | over-fires on every speech verb with a real object (80) | fold into the wire: gate on actual quote structure |
| **mention / candidate builder** (`parse_litbank_conll`) | referent-per-NP incl. singletons = PINNED (Kamp/Heim) | eval marks every content noun a mention | DEPLOYED `read()` derives mentions from COREF chains — can drop singleton referents | **next problem: referent-per-NP first, coref as a downstream LINKING pass** (Q3 confirms our design premise) |
| **ditransitive linking** (positional/NP-head) | double-object construction obj1=recipient/obj2=theme = PINNED (Goldberg; VerbNet) | word-order patient works for mono-transitives | mis-assigns recipient vs theme (1 of the 5 regressions) | **1d / the filed non-canonical-argument problem**: VerbNet ditransitive frame + animacy backoff (research: cheapest win) |

## KEY REALIZATIONS
- **The abstention was disguised as a parser problem and was actually three lexical/threshold gates.** The enabling
  move was running the reader FIRST-HAND and splitting the 147 by CAUSE instead of trusting "the parse is weak on
  19c" — the moment I compared the wired and positional routes and saw positional recover all 80, the story flipped
  from "build a better parser" to "stop three gates from vetoing real patients".
- **A more accurate component made the whole system less accurate.** The `wired` parse route was added for
  richer/passive roles and it is net-NEGATIVE (−0.10) for patient coverage — a concrete instance of "the convenient
  fancy mechanism loses; the robust brain-faithful cue wins".
- **The updated parser recovering 1/669 is the proof, not a footnote.** Opting into the best parser and watching the
  gap NOT move is what licenses "parser-free is the right lever".
- **Coverage, not accuracy, was the larger loss** — and it hid behind a 0.98 present-accuracy number. Counting
  silence as wrong is the measurement that made the real bottleneck visible.
- **Pushing on "soft transitivity" replaced it with a better mechanism entirely.** Building the can-fail intransitive
  control showed the naive soft rule regresses (over-generates on 100% of intransitives); the fix was not a softer
  threshold but a structural principle — *the patient is a direct object, obliques never are* — which needs no
  transitivity number, recovers the 47, abstains 0.975 on intransitives, and even improves the main gold. The lesson:
  when a gate mis-fires, the brain-faithful move is often to delete the gate and use the structural definition of the
  role, not to re-tune the gate's threshold.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
`situation_reader` role assignment: the `role_route=wired` patient path carries two OUR-INVENTION precision gates
(speech-verb quotative veto; verb_subcat hard threshold) that are register-brittle and cost 127/669 patients on 19c
prose, plus 20 upstream POS-tagger no-events. The brain-faithful operation is word-order-primary Competition-Model
role assignment with transitivity/quotative as SOFT overridable cues (PINNED by Bates & MacWhinney / Ferreira /
Garnsey). Current fidelity: the robust positional+NP-head competition path is the faithful one and reaches 0.981
end-to-end; the parse router should be demoted to an additive passive/ditransitive override. The tense-agnostic
Davidsonian event detector is correct but capped by UD-tagger 19c verb recall (adjacent component).

## What I did NOT establish (would withdraw first if wrong)
- I did NOT edit hdlab or measure the wire landed in-place — I proved the mechanism in experiments/ and the strategy
  session lands it (Q111). The 0.981 is the reference-path measurement, first-hand-reproduced against the live reader.
- The intransitive precision control is a CONSTRUCTED (glass-box, hand-built) set of 40 clauses, not mined 19c
  intransitives; it can-fail and the STRUCTURAL-DO rule passes it (0.975), but a corpus-mined intransitive population
  would be a stronger control. First thing to withdraw if mined intransitives over-generate. (This SUPERSEDES the
  earlier "argued not measured" caveat — the gap is now measured.)
- The 20 no-event are recovered here only because the task supplies the verb index; in free-text deployment they
  depend on POS-tagger 19c recall (follow-on 1c). I do NOT claim end-to-end event DETECTION is solved.
- Register-independence is an extrapolation (no direct archaic-register study); the evidence is the modern+19c
  generalization, not a brain finding.

---

### TLDR (plain language)
The reader's "who did what to whom" is right about 98% of the time when it answers, but on old-fashioned prose it
stays completely silent on about one in five sentences that DO have an answer — so, counting silence as a miss, it is
really right only ~63% of the time. I ran the reader itself and found the silence has three exact causes, and none of
them is "the grammar tool couldn't find the noun": (1) it throws away the object of every "saying" verb — "call
**me**", "tell my **wife**" — because it assumes a speech verb must be someone speaking; (2) it deletes the object
whenever a word-frequency table thinks the verb is rarely transitive, which misfires on old verbs; (3) it never
starts because its part-of-speech tool mislabels old verbs like "the lake **presents**" as nouns. Fixing all three
with a robust, brain-style rule (nearest sensible noun after the verb, always try, treat those two vetoes as soft
hints not hard blocks) takes it from 63% to 98%, holds up on modern text too, and a scrambled version collapses to
42% — proving the fix is real, not luck. I also turned on the newest, most accurate grammar parser to be fair: it
fixed only 1 sentence out of 669, confirming the problem was never the parser.

### QUESTIONS
None blocking. One judgement call for the strategy session at landing: whether to keep the parse router as an
additive passive/ditransitive override (recommended — it correctly handles the 5 hard cases the pure positional rule
misses) or drop it entirely for simplicity.

### NEXT STEPS
1. **Land the wire** (strategy, Q111, default-off, witnessed): quotative-on-evidence + positional fallback +
   **STRUCTURAL-DO candidate filter** (patient = bare post-verbal nominal; the refined form that subsumes verb_subcat)
   in `_read_events_wired`; re-measure through the live reader; then re-validate the ~20 role-output organs (they
   inherit the fix — re-validate, don't re-code).
2. **Follow-on 1c — register-robust predicate identification** (the 20 no-event; adjacent component, SOLVABLE not a
   wall): the mis-tagged tokens ARE lexically verbs (18/20 WordNet), but a heuristic can't cleanly recover them (cell
   (b)) — the fix is the research-indicated parser-attachment / clause-structure verbhood override, not a better
   static tagger. High-value for free-text event detection; verdict-independent.
3. **Follow-on 1d — ditransitive recipient-vs-theme** (1 of the 5 regressions): the double-object construction assigns
   obj1=recipient/obj2=theme (Goldberg; VerbNet) with animacy backoff (Bresnan 2007) — the research calls this the
   cheapest win (a wiring fix against resources already held). Its home is the filed non-canonical-argument problem.
4. **Referent-per-NP mention sourcing** (adjacent, brain-fidelity): the deployed `read()` derives mentions from coref
   chains, which can drop singleton referents; the brain-faithful order is referent-per-NP first (Kamp/Heim), coref as
   a downstream LINKING pass. Verify the deployed mention source annotates singletons; if not, it is a coverage
   ceiling this recovery's eval harness hides. Candidate next problem.
