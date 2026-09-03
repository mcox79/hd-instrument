---
problem: the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses
status: SOLVED
bar: "PASS = a coverage recovery (attempt every finite verb + parser-robust candidate building, glass-box, NO LLM) that raises the LIVE reader's EFFECTIVE end-to-end who-did-what (abstention counted as wrong) CI-separated over the current 0.629, WITHOUT regressing the picked-clause NP-head precision (an explicit no-regression check on the accuracy the parent landed), with an info-free twin (recover random clauses) LOSING. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the dropped clauses are genuinely un-recoverable glass-box, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "Effective end-to-end who-did-what (abstention=wrong), 669 clean-19c direct-object clauses, scorer pick==gold_head: LIVE wired 0.6293 -> RECOVERED 0.9806, +0.3513 CI[+0.3154,+0.3886] half=0.0366 null_p95=0.0375. Modern QA-SRL (n=1261) 0.5678 -> 0.9025, +0.3347 CI-sep. Present-accuracy 0.807 -> 0.981 (precision UP, not regressed)."
floor: "Strongest floor actually run = the reader's OWN better route, LIVE positional 0.7294 (RECOVERED beats it +0.2511 CI[+0.2167,+0.2840]). Also: LIVE wired 0.6293; best-available-parser wired floor (updated arc-eager, UD-EWT UAS 0.842) 0.6308 -- the abstention is parser-INDEPENDENT, not a strawman floor."
controls: "(1) info-free twin = full coverage + UNIFORM-RANDOM post-verbal pick 0.4185, LOSES CI-sep (REC-vs-twin +0.5620). (2) NO-REGRESSION: of 421 clauses the live reader already got right, RECOVERED keeps 416 (5 individual flips, all hard ditransitive/copula/distant-noun cases); present-accuracy 0.807->0.981. (3) fair-floor: the UPDATED arc-eager parser recovers only 1/669 -> abstention is not parse-quality. (4) first-hand reader reproduces the stored wired_pick/pos_pick 100%. (5) per-cause ablation is exhaustive (recovered-correct sums exactly to 0.9806)."
files_changed: "experiments/exp_whodidwhat_coverage_diagnosis_v1.py, experiments/exp_whodidwhat_coverage_recover_v1.py, experiments/exp_whodidwhat_coverage_parser_floor_v1.py, verification/test_whodidwhat_coverage.py, notes/problems/the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses/SOLVED.md"
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
3. **Soft transitivity (recovers 47):** replace the hard `verb_subcat_gate` veto with an override — do not suppress
   the patient when a plausible adjacent post-verbal candidate is present (Competition Model). Keep the transitivity
   signal as a down-weight for genuine intransitives.
4. **NP-head reduction** is already landed (`hdlab/np_head_reduce.py`) and should stay on this path (the accuracy half).
5. The **20 no-event** is a LOCATED sub-negative: it is upstream POS-tagger recall on 19c verbs, not a role-assignment
   defect — recovered here only because the who-did-what task supplies the verb index. It is filed as follow-on
   problem 1c below, not silently folded in.

Reference implementation of the full recovered path: `experiments/exp_whodidwhat_full_fix_v1.role_patient_full_fix`.

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
- The soft-transitivity recovery is validated on an ALL-transitive gold; I did not build a mixed-intransitive
  precision control here, so "soft transitivity does not over-generate on genuine intransitives" is argued from the
  mechanism (override only when a candidate is present) + the modern no-regression, not measured on a dedicated
  intransitive set. First thing to withdraw if a mixed-population check shows over-generation.
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
1. **Land the wire** (strategy, Q111, default-off, witnessed): quotative-on-evidence + positional fallback + soft
   transitivity in `_read_events_wired`; re-measure through the live reader; then re-validate the ~20 role-output
   organs (they inherit the fix — re-validate, don't re-code).
2. **Follow-on 1c — the 20 no-event = 19c POS-tagger verb recall** (adjacent component): the UD tagger mis-tags 19c
   verbs (ADJ/ADP/ADV/NOUN); a register-robust verb-identification cue (clausal position + agreement/tense morphology,
   per the brain literature) is the fix. Verdict-independent, high-value for free-text event detection.
3. **Follow-on 1d — ditransitive recipient-vs-theme** (the residual accuracy axis, 1 of the 5 regressions): the
   positional/NP-head rule does not model ARG2-GOL (recipient) vs ARG1-PPT (theme); the parse router or a PropBank
   frame cue is the lever. Small n here; its real home is the non-canonical-argument-structure problem already filed.
4. **Mixed-intransitive precision control** for soft transitivity (close the one un-measured no-regression gap).
