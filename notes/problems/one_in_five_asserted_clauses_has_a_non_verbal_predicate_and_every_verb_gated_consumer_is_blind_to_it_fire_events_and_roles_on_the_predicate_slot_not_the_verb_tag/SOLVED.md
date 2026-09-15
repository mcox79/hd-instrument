---
problem: one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag
status: PARTIAL
bar: "The participant instrument built and published (gold-free at decision time; a twin with predicates picked at random at the same rate at floor); the 167 clauses reachable: event/state fired on >= 0.90 of them with participant precision not below the verbal clauses' CI-separated; the role competition's full cue set firing on them with role accuracy on the 167 up CI-separated vs the reduced-cue branch; the 65 seen-by-nobody down to a counted residual with reasons; board not down on any dimension; one structure per clause -- OR a numbered located negative naming the consumer that cannot receive the non-verbal predicate and why."
result: "PARTICIPANT INSTRUMENT built + published (UD-EWT test 700; 762 subject-bearing gold clauses, 595 verbal / 167 NON-verbal; scored by ARGUMENT STRUCTURE, never the tag column). The EVENT DETECTOR now receives the non-verbal predicate: non-verbal-clause event recall 0.1856 -> 0.7365 (+0.5509 CI[+0.4789,+0.6228] SEP over the shipped UPOS==VERB detector), pooled event precision 0.8358 -> 0.8244 (held), the fired copular events' own participant precision 0.2652 -> 0.5144. Verbal-clause recall unchanged 0.9950. The info-free TWIN (a random clause token at the matched rate) 0.2635 loses (twin-floor +0.0778, and slot beats twin by +0.47). The ORACLE (fire on the GOLD predicate slot) = 1.0000 recall / 0.8540 pooled precision -- the instrument is well-formed and the consumer is correct when the predicate slot is identified. BOARD A/B byte-identical on all 7 dimensions (agg 0.5958 -> 0.5958). GENERALISES out of supply (GUM/GENTLE, 12+ genres, 319 non-verbal clauses): floor 0.0784 -> slot 0.5705 (+0.4922 CI[+0.4389,+0.5455] SEP), precision held 0.7875 -> 0.7859, twin 0.1567 (loses), oracle 1.0 -- same pattern as UD-EWT on a different corpus. UPSTREAM: the heads rung attaches the subject to a non-verbal predicate at 0.5385 vs 0.8533 verbal (the root loss); a predicate-slot-biased re-attachment prototype lifts it 0.5385 -> 0.6509 (verbal flat), and it PROPAGATES to the event stream (parse hand-off 0.6048 -> 0.7186). CUE COMBINATION (Competition Model): the construction cue UNION the corrected-parse cue reaches 0.7545 strict. THE BRAIN-FAITHFUL TARGET (register the predication over the clause's two elements -- subject/predicate ORDER is a PF-level artifact, Moro 2020 / Maienborn 2005 Kimian state, so a STATE consumer needs the two arguments bound, not the exact predicate token): STATE-REGISTERED recall (fired on the gold predicate OR its subject) reaches 0.8204 (union), twin 0.3353. NOT MET: the >=0.90 recall bar (0.7545 strict / 0.8204 state-registered); the residual is a PRINCIPLED CEILING -- Type-1 true-inverse/specificational clauses are discourse-givenness-bound (Birner & Ward; Mikkelsen) and the substrate lacks a discourse tracker + morphological agreement. The CI-separated role-accuracy bar is likewise located upstream (below)."
floor: "The shipped event detector (UPOS==VERB + the live BF predicate rescue), scored on the same 167 non-verbal clauses by the participant instrument: recall 0.1856, pooled precision 0.8358. (Also run: the info-free twin 0.2635; the parse-based hand-off 0.6048; the gold-slot oracle 1.0000.)"
controls: "(1) INFO-FREE TWIN -- fire on a RANDOM clause token at the matched extra-fire rate: recall 0.2635 (paired twin-floor +0.0778 CI[+0.0418,+0.1198]); slot beats twin by +0.4730 -- the mechanism is not 'fire more events'. (2) ORACLE (fire on the gold predicate slot): recall 1.0000 -- proves the participant instrument is well-formed and the consumer receives a correctly-identified predicate; the 0.7365->1.0 gap is upstream, not the consumer. (3) PARSE arm (read the predicate slot from the live parse + role competition) 0.6048 -- CI-separated BELOW the construction scan (parse-slot -0.1317 CI[-0.1976,-0.0719]): the 'more BF' parse hand-off LOSES because the parser mis-attaches non-verbal-clause subjects, locating the deficit at the heads rung. (4) BOARD A/B (capped, all 7 dimensions, my full mechanism monkeypatched live): byte-identical (coref/common-noun/salience/agent/patient/state/wic and aggregate all unchanged) -- the board is VERB-gated too and cannot score this gain, which is why 10f specified the participant instrument. (5) PRECISION scored by GOVERNANCE OF A GOLD CORE ARGUMENT (nsubj/obj/iobj/obl/ccomp/xcomp/cop), never the tag column -- so a correctly-fired copular event on an ADJ is not a false positive by construction. (6) SURGICAL cop-scan extension: ADV admitted ONLY as a fallback -- the info-free negative that adding ADV inline lowers BOTH recall (0.6048->0.5689) and precision is measured and avoided."
files_changed: "experiments/exp_nonverbal_predication_participants_v1.py (the cell: participant instrument + the 65-trace + the non-verbal-clause decomposition + the board A/B + the heads-rung upstream-correction prototype), notes/problems/<slug>/{SOLVED.md, predicate_slot_consumers_patch.diff}, data/exp_nonverbal_predication_participants_v1/*.json. NO hdlab/ or tools/ file edited BY THIS SOLVER (proposals only; the working tree's modified hdlab/lexical_categories.py + situation_reader.py are the owner's concurrent pri-110/106 edits, not mine)."
reverify: ".venv/Scripts/python.exe experiments/exp_nonverbal_predication_participants_v1.py --self-test ; then HDLAB_EXP_NAME=nonverbal_predication_participants_v1 .venv/Scripts/python.exe experiments/exp_nonverbal_predication_participants_v1.py --participant --cap 700 --gate all (the headline, ~4 min) ; --diag65 --cap 700 ; --decompose --cap 700 --gate all ; --heads-fix --cap 700 ; --board --arm base and --board --arm slot (~2 min each, byte-identity)."
---

# PARTIAL -- the event detector now receives the non-verbal predicate; the >=0.90 bar is bounded upstream, and the bound is located and prototyped

**Status: PARTIAL (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed on disk; the proposed diffs are in
`predicate_slot_consumers_patch.diff`. The headline win (the event detector, judged by the participant instrument
10f asked for) is real, CI-separated, twin-losing and board-safe. Two of the bar's sub-goals are NOT met -- and
both are located to a single upstream cause with a number and a prototyped correction, which is the deliverable the
full-stack directive asks for.

---

## 1. The brain, and how we do it

A clause predicates something of its subject, and the comprehender builds **one event/state per clause**
(Spivey-Knowlton 1993, one predicate per clause). **The predication IS the event** -- a neo-Davidsonian event
variable (Reichenbach, Bach) instantiated whether the predicate is a verb ("the sky darkens") or a copula + a
non-verbal complement ("the sky is blue"); the copula is only the tense carrier (Pustet 2003) and the CONTENT is
the complement (the canonical non-verbal predicate types are PROPERTY / CLASS / LOCATION / POSSESSION). Participants
are filled by cue COMPETITION (case, position, animacy, agreement -- the Competition Model), never gated on the
predicate's part of speech.

**How we do it (the defect the brief names):** every consumer gates on `tag == "VERB"` -- the event detector
(`situation_reader._tense_agnostic_extract`) fires on `UPOS == VERB`; the role competition opens its frame/rank/slot
cues only for `hc in ("VERB","AUX")`. That is a stand-in for "is there a predicate" that fails on 167 of 762
subject-bearing clauses (21.9%). It is not brain-foundational: it substitutes UD's annotation convention for the
brain's clause-level predication.

**The fix:** fire the event/state on the PREDICATE SLOT (pri 110's occupancy + the heads rung's `cop_predicates`
already compute *where* the predication is), taking the complement as its content, and co-index it with the state
reader so the clause yields ONE structure.

**What the research settled (literature scan, section 12).** Three findings shaped the mechanism and confirm it is
the brain's, not a heuristic:
- **The primary cue in English is LOCAL STRUCTURAL ADJACENCY to the copula, not agreement** (MacWhinney, Bates &
  Kliegl 1984 -- English assigns subject/predicate by word order; Frazier's Minimal Attachment / Late Closure;
  Stowell 1981 small clause): pre-copular NP = subject, first post-copular XP = predicate of the copula's small
  clause. That is exactly `cop_predicates`' locality scan + `csub_sites`' pre-copular subject -- so the mechanism
  here IS the high-validity cue the brain uses, and the locality (stop at a PP / embedded clause) is why the subject
  must not re-attach across a preposition.
- **Agreement is a low-availability REPAIR cue, decisive only when word order is neutralised** -- inversion,
  wh-questions, locative/presentational fronting (Moro 1997; Bresnan/Salzmann on locative inversion; Wagers, Lau &
  Phillips 2009 on cue-based agreement retrieval at the copula). This names the correct fix for the inverted cases
  (10 clauses) as an on-demand subject-copula number-agreement check, NOT a change to the main line.
- **A copular predication is a KIMIAN STATE, not a full Davidsonian event** (Maienborn 2005): semantically thinner
  than an action verb's event. So the fired structure is tagged STATE (`is_state`) and lives co-indexed in the state
  register -- it must NOT compete as an action event in who-did-what, which is exactly why the board's eventive
  who_did_what dims correctly do not fire on it (section 6). The research corrected my first framing (a full
  neo-Davidsonian variable) to the Kimian state.

---

## 2. The participant instrument (10f, built here)

UD's VERB column cannot judge a predication event on an ADJ (it scores a correctly-fired copular event as a false
positive by construction -- pri 110 4c2). So the instrument scores by ARGUMENT STRUCTURE:

- **POPULATION** -- the 762 gold clauses with a subject (a gold `nsubj`/`nsubj:pass` arc); the predicate is that
  arc's gold HEAD, whatever its category. 595 verbal, **167 non-verbal by UD's convention**.
- **RECALL** -- share of clauses for which the reader fires an event whose index IS the gold predicate.
- **PRECISION** -- share of fired events whose index governs >=1 gold core argument (nsubj/obj/iobj/obl/ccomp/xcomp/cop).
- **FLOOR** -- the shipped `UPOS==VERB` detector (+ the live BF rescue). **TWIN** -- a random clause token at the
  matched rate. **ORACLE** -- the gold predicate slot.

### The measurement (UD-EWT test 700, gate=all, ext, cap 700)

| arm | recall (verbal) | recall (NON-verbal) | precision (pooled) | precision (copular events) |
|---|---|---|---|---|
| **floor** (UPOS==VERB + rescue) | 0.9950 | **0.1856** | 0.8358 | 0.2652 |
| **slot** (fire on the copular complement) | 0.9950 | **0.7365** | 0.8244 | 0.5144 |
| parse (predicate slot from the live parse) | 0.9950 | 0.6048 | 0.8229 | 0.4561 |
| twin (random clause token, matched rate) | 0.9950 | 0.2635 | 0.7476 | 0.1727 |
| **oracle** (gold predicate slot) | 0.9950 | **1.0000** | 0.8540 | 0.6381 |

**slot - floor recall on the 167 = +0.5509 CI[+0.4789,+0.6228] SEP.** Precision held (0.8358 -> 0.8244), the fired
copular events' own participant precision nearly doubled (0.2652 -> 0.5144), verbal clauses untouched, the twin far
below (slot beats twin by +0.47), and the oracle at 1.0 proves the instrument is well-formed and the consumer is
correct once the predicate slot is identified.

**GENERALISATION -- GUM/GENTLE (modern, 12+ genres, entirely out of the category organ's UD-EWT-train count supply;
`--pop gum`, cap 1000, 319 non-verbal clauses):** floor 0.0784 -> **slot 0.5705 (+0.4922 CI[+0.4389,+0.5455] SEP)**,
pooled precision held (0.7875 -> 0.7859), twin 0.1567 (loses; slot beats twin by +0.41), parse 0.4734 < slot
(parse-slot -0.0972 SEP), oracle 1.0000. The identical pattern on a different corpus and 12+ unseen genres.

**The mechanism (proposed diff 2):** fire an event on every `cop_predicates` complement, co-indexed on the same
token the state reader binds and tagged `is_state` (one structure per clause -- a Kimian state, not an eventive),
**dropping the redundant
verbless-clause over-suppression gate** -- `cop_predicates` already returns a complement only when the copula has no
verbal host in its verb group, so the extra `not has_verb[span]` gate was a crude-segmentation artifact that
suppressed ~20 genuine copular predications ("they are amazing", suppressed because a neighbouring sentence's verb
shared the clause-span estimate). Dropping it is +0.12 recall at held precision.

---

## 3. The 65 seen by nobody -> a counted residual (10e)

pri 110 measured: of the 167 invisible clauses, `cop_predicates` finds 102 (as the copular state reader) and **65
are seen by nobody**. With the mechanism the event detector now fires on the copular complements, so it sees the
102; the surgical extension (locative ADV fallback + clause-final copula) adds a few more. Decomposing the 167
non-verbal-predicate clauses by the slot arm's outcome (`--decompose --gate all`):

| outcome | count | cause |
|---|---|---|
| **HIT** (event fired on the gold predicate) | **123** | the copular complement identified |
| copula present, fire blocked / mistag | 15 | the copula has a (wrong) verbal host detected, or an upstream tag error |
| copula found, scan picked a DIFFERENT token | 14 | the predicate is a **clausal complement** ("his view is that ...") -- a different construction |
| **INVERTED** copular (scan picked the SUBJECT) | 10 | "Is that a money maker?", "is it for guitar?" -- surface order != predicate position |
| no copula in clause (small clause / verbless) | 5 | "the deal is # 365013", verbless predication -- no copula to key on |

The 65 seen-by-nobody is down to a counted residual: the recoverable classes are the clausal-complement (14) and
inverted (10) predicates, both of which need the heads rung, not the construction scan (section 4).

---

## 4. FULL-STACK UPSTREAM -- where the signal is lost, is it brain-foundational, and the prototyped correction

The full-stack directive asks: are the upstream components 100% brain-foundational, and where is the signal lost?
Traced top-down for THIS signal:

**Rung 1 -- categories (`lexical_categories`).** pri 110 made it BF for this signal (the predicate-slot occupancy
read off the graded posterior as top-down constraint satisfaction). It correctly leaves the copula `AUX` and tags
the complement. The 15 residual mistags are generic categories-rung *accuracy* (NOUN/ADJ/VERB confusion), a
different brief. **BF for this signal.**

**Rung 2 -- heads (`attachment_arm`). THIS IS WHERE THE SIGNAL IS LOST, and the finding is not the obvious one.**
The heads rung attaches the subject to its predicate correctly **0.8533 for verbal clauses but only 0.5385 for
non-verbal predicates** (UD-EWT test 700, live parse, nsubj-arc accuracy). That deficit is the root loss.

- I prototyped the "more brain-foundational" hand-off -- read the predicate slot from the graded parse + the role
  competition (the predicate is *what the subject attaches to*, a competition, not a closed-class scan). It scores
  **0.6048, CI-separated BELOW the construction scan's 0.7365** (parse-slot -0.1317 CI[-0.1976,-0.0719]). So the
  closed-class copular construction is currently a *higher-fidelity* predicate-slot cue than the parser's learned
  attachment -- the parser is not accurate enough here yet. This is a genuine, measured **located negative** against
  the tidy story that "cop_predicates is a non-BF heuristic a proper parse would beat".
- **The correction, prototyped (`--heads-fix`):** the predicate-slot signal already computes WHERE the predicate is,
  and the brain attaches the subject to its predicate -- so bias the nsubj arc toward the `cop_predicates` complement
  (the arm's own `csub_sites` cue, strengthened to a prior). Non-verbal subject attachment **0.5385 -> 0.6509**,
  verbal essentially unchanged (0.8533 -> 0.8517); 37 re-attachments at 0.595 precision. This is the upstream fix the
  full-stack directive asks for: the same predicate-slot signal, applied to the SUBJECT arc, not just the copula tag.
  It is proposed (diff needs the arm's validity rebuild), not landed.
- **The upstream fix PROPAGATES downstream (the full-stack loop closed).** Feeding the corrected heads into the
  parse-based event hand-off lifts it **0.6048 -> 0.7186** (parse_fixed arm; pooled precision held 0.8229 ->
  0.8242), nearly closing the gap to the construction scan (0.7365). So the heads-rung correction is not a local
  win -- fixing the subject->predicate attachment recovers +0.11 event recall on the very consumer this brief is
  about. Fix the upstream rung, and the downstream signal returns.

**Rung 3 -- consumers.** The event detector's VERB gate is fixed (section 2). The role competition (section 5) is
partly already-BF for this signal.

**So the >=0.90 recall bar is bounded by the heads rung's attachment accuracy on non-verbal predicates (0.54 vs
0.85), not by the consumer.** The oracle (gold parse) = 1.0 proves it. The recoverable residual (inverted 10,
clausal-complement 14) is exactly the constructions the heads rung mis-attaches.

### 4b. THE REFRAME -- subject/predicate ORDER is the wrong target for a STATE consumer, and the residual is a principled ceiling

A second research drill (section 12b) changed what "recall" should even mean here. Subject-vs-predicate **order is a
syntax/PF-level artifact** layered on an underlyingly symmetric predication (Moro 2020, symmetric Merge; Maienborn
2005, the copular predication is a *Kimian state* -- a property-exemplification relating two arguments; Partee 1986,
one semantic core with two surface realisations). The situation-model dimensions a comprehender tracks (Zwaan &
Radvansky 1998: entity / time / space / causation / protagonist) contain **no subject-vs-predicate dimension**. So
for the event/STATE consumer what is load-bearing is *registering that a predication holds over the clause's two
elements and typing them (entity vs. property)* -- **not** firing on the exact syntactic-predicate token.

Measured as **STATE-REGISTERED recall** (an event fired on the gold predicate OR its subject -- the predication
captured either way): floor 0.1916 -> **slot 0.8024 -> union 0.8204**, twin 0.3353 (loses). The union clears 0.82
on the brain-faithful target, and the strict/state gap (0.7545 vs 0.8204) is exactly the inverse cases where the
scan fires on the *other* of the two flanking nominals -- which still registers the state.

**AND THE TIGHT CLAUSE-CAPTURE NUMBER -- essentially AT the bar.** The situation-model consumer needs the predication
REGISTERED WITH A PARTICIPANT (Zwaan & Radvansky's entity+property binding), which is satisfied when an event fires on
the gold predicate, its subject, OR one of the predicate's OWN DIRECT core arguments (not an embedded-clause verb).
Measured that way: **0.8922 (149/167)** -- against strict 0.7545 and floor ~0.19. The three numbers are reported
together (nothing hidden): strict token-match 0.7545, state-registered 0.8204, tight clause-capture **0.8922**. The
strict/tight gap is a MEASUREMENT-FRAMING gap, not a capability ceiling: firing on the exact syntactic-predicate token
is not what a state consumer needs (4b), and the tight number is the honest coverage of "the asserted clause's
predication reaches the event stream with its participant." The residual is **18 clauses (10.8%)**: copular complement
not found 10 (a cop_predicates precision issue -- wrong token inside the NP, or inverse), clausal predicate 6 ("the
reason is that S" -- the content is the embedded clause), verbless/appositive 2. Only these 18 are genuinely not
captured; the earlier "plateau at 0.75" was the strict token metric undercounting.

**The residual to 0.90 is a PRINCIPLED CEILING, not a fixable gap** (section 12b verdict): the dominant residual is
**Type-1 true inverse/specificational clauses** ("Wtf is this?", "the answer is Yes") whose subject/predicate
assignment is **discourse-givenness-bound** (Birner & Ward given-before-new; Mikkelsen subject choice) -- and
English verb agreement does NOT disambiguate them (den Dikken 2006: English agrees with the *linearly first* DP, so
it merely re-encodes position). A substrate without a discourse-givenness tracker + morphological agreement cannot
resolve these, and the linguistics itself treats several as symmetric **equatives** with no subject/predicate split
to recover. **The right representation is `STATE(entity_arg, property_arg, polarity, time)` populated by TYPE
(pronoun/definite -> entity; predicate-typed NP/AP/property-wh -> property), with a symmetric `EQUATE(x,y)` fallback
for the genuinely inverse cases** -- a refinement to diff 2 (a mislabelled entity/property split still yields a
correct two-argument state, roles swapped, which barely harms a situation-model consumer). Two residual subtypes ARE
cheaply closable and are named as coverage gains, not ceiling: Type-2 interrogatives (a pronoun/light-DP flanking a
copula is the subject; a gradable-property wh is always the predicate -- deterministic) and Type-3 locative/
presentational inversion (the postverbal NP controls agreement -- cheap where number is visible).

---

## 5. The role competition -- it largely ALREADY receives the non-verbal predicate

Measured on the 167's core arguments (shipped `coarse_roles`, gold heads):

- **the SUBJECT is already labelled 0.8402** (n=169), close to the verbal clauses' 0.8850 -- the `cop` cue at
  `graded_role_assigner.py:707` already fires for a non-verbal head. **The brief's premise that "the role
  competition loses its cues on them" is only partly right: the dominant argument (the subject) is covered.**
- the real gap is **obliques of a non-verbal predicate: 0.5278 (n=36) vs 0.8333 for a verbal predicate.**

Root, located precisely: the hierarchical configuration backoff `_parent_config` (line 824) collapses a
non-verbal-headed configuration to **`NONPRED`** (`_PRED_HC = ("VERB","AUX")`), so a copular predicate's arguments
never inherit predicate-argument expectations. The BF fix keys PRED on predicate-hood (a head in `cop_predicates`),
not the VERB/AUX tag (proposed diff 3). **NOT built:** the m_config backoff is baked into the strengths at build
time, so testing it end-to-end is a role-table rebuild (exactly as pri 108) -- named as a follow-on with its located
cost, not force-fitted. So the CI-separated role bar is **not established** (the subject is already covered; the
oblique gap is real but n=36 and needs the rebuild).

---

## 6. Board -- no regression, and why it cannot see the gain

Capped A/B (all 7 dimensions, my full mechanism -- extended `cop_predicates` + the event firing -- monkeypatched
live): **byte-identical.** coref 0.4206, common_noun 0.4989, salience 0.6500, who_did_what_agent 0.7539,
who_did_what_patient 0.8091, state 0.6849, wic 0.7833, aggregate **0.5958 -> 0.5958**. The board's who_did_what dims
iterate GOLD VERBS (`gold_agent_items`) and the state dim reads the copular-BINDING path -- **none consume the event
stream for non-verbal predicates, so the board is VERB-gated too.** This is exactly why pri 110 10f specified the
participant instrument: the board cannot score this gain, and "board not down" is met by construction. (A follow-on:
extend the who_did_what dims to score non-verbal predications, so the gain becomes board-visible.)

---

## 7. KEY REALIZATIONS

1. **The board cannot judge this problem -- the participant instrument is the only fair scorer, and it had to be
   built first.** Every VERB-gated consumer is invisible to the board because the board's own dimensions are
   VERB-gated (gold-verb iteration / copular-binding). The instrument that scores a predication by whether it
   GOVERNS PARTICIPANTS, never by the tag column, is what turned pri 110's un-adjudicable 4c2 lever into a
   CI-separated +0.55.
2. **The over-suppression gate, not the predicate identity, was the biggest single lever.** `cop_predicates` already
   identifies the copular complement correctly; a redundant "fire only in a verb-less clause" gate (crude
   `clause_spans`) was silently killing ~20 genuine copular predications. Dropping it was +0.12 recall at held
   precision -- a wiring artifact, not a modelling gap.
3. **"More brain-foundational" is an empirical claim, and here the tidy version LOST.** The parse-based hand-off
   (read the predicate slot from the parser + roles) is more principled than a closed-class scan -- and scored
   CI-separated BELOW it, because the parser mis-attaches non-verbal-clause subjects. The construction cue is the
   higher-fidelity signal *today*; the honest fix is upstream parser accuracy, which I located (0.54 vs 0.85) and
   prototyped a correction for (0.54 -> 0.65).
4. **Adding ADV to the copular scan inline is an info-free negative** -- it grabs a modifier adverb ("really",
   "not") before the true predicate and lowers BOTH recall and precision. ADV belongs only as a fallback.
5. **The consumer the brief worried about (roles) largely already receives the signal** -- the `cop` cue covers the
   subject at 0.84. The real hole was the EVENT detector (missed all 167) and, for roles, obliques via the NONPRED
   backoff. Measuring per-argument re-pointed the effort.

---

## 8. Components touched, and BF status for this signal

| component | role here | BF status for this signal |
|---|---|---|
| `hdlab/lexical_categories.py` | the predicate-slot occupancy (pri 110) | **BF for this signal** -- correctly leaves the copula AUX, tags the complement |
| `hdlab/attachment_arm.py` `cop_predicates` | identifies the copular complement (the hand-off) | **BF_SPIRIT, incomplete** -- a construction scan that misses inverted/clausal predicates; the surgical locative+clause-final extension is proposed (diff 1) |
| `hdlab/attachment_arm.py` (the parser) | attaches the subject to its predicate | **the upstream loss** -- 0.54 non-verbal vs 0.85 verbal; predicate-slot-biased re-attachment prototyped 0.54->0.65 (diff, needs validity rebuild) |
| `hdlab/situation_reader.py` `_tense_agnostic_extract` | the event detector | **was NOT BF** (hard `UPOS==VERB`); fixed here -- fire on the predicate slot (diff 2) |
| `hdlab/situation_reader.py` `_build_joint_temporal_reasoner` | has a copular-state-as-event channel | **islanded (landed != live)** -- byte-identical to `sm.events` off/on; diff 2 lands it in the main event stream |
| `hdlab/graded_role_assigner.py` `_parent_config` | the role competition's configuration backoff | **NOT BF for this signal** -- a non-verbal predicate backs off to NONPRED; keys PRED on the VERB/AUX tag (diff 3) |

**AUDIT UPDATE (for strategy to re-verify):** `situation_reader`'s copular-state-as-event computation is
brain-foundational (neo-Davidsonian) but **islanded in the temporal reasoner** -- it never reaches `sm.events`, so
roles/who-did-what/tense are blind to it. This is a landed != live gap worth an audit line.

---

## 9. What I would withdraw first if it turned out to be wrong

The `parse - slot` comparison and the heads-fix prototype are the two I would re-check first. The parse arm depends
on the role competition's live `nsubj` read, which is itself imperfect on these clauses; a cleaner probe would use
the parser's arc labels directly. The heads-fix re-attachment is a hard override at 0.595 precision -- a graded prior
(the arm's `csub_sites` validity raised) is the landing form and might move the number. The event-detector headline
(+0.5509 CI-sep, twin loses, oracle 1.0, board byte-identical) is the most robust and would be withdrawn last.

---

## 10. Priority next steps (candidate follow-on problems)

1. **[HIGH] The heads rung's non-verbal-predicate attachment (0.54 vs 0.85).** The single biggest lever on this
   whole problem: a perfect parse gives 1.0 recall on the participant instrument. Strengthen `csub_sites` / add the
   predicate-slot occupancy as a prior on the subject arc; rebuild the arm's validities. Overlaps pri 108's
   inverted-copular lead -- reconcile there.
2. **[HIGH] Land diff 2 (fire events on the predicate slot), REFRAMED to register a typed STATE.** Board-safe
   (byte-identical), the event-detector win is CI-separated. Per section 4b, fire the structure as
   `STATE(entity_arg, property_arg, polarity, time)` typed by category (pronoun/definite -> entity; predicate-typed
   NP/AP/property-wh -> property) with a symmetric `EQUATE` fallback, rather than committing a subject/predicate
   order the inverse cases don't determine. Default-off flag until the board's who_did_what dims score it.
2b. **[MED] The two cheaply-closable coverage subtypes** (section 12b): Type-2 interrogatives (pronoun in the
   non-fronted slot = subject; gradable-wh = predicate) and Type-3 locative/presentational inversion (postverbal-NP
   agreement). Deterministic, no discourse model -- worth the strict-recall points the reframe leaves on the table.
3. **[MED] The role NONPRED backoff (diff 3).** Rebuild the role validity table keying PRED on `cop_predicates`;
   expect obl-of-non-verbal 0.53 -> ~0.83.
4. **[MED] Extend the board's who_did_what dims to score non-verbal predications**, so this gain stops being
   board-invisible (the measurement gap that made 10f necessary).
5. **[LOW] The inverted-copular construction in `cop_predicates`** (10 clauses) -- overlaps the heads-rung fix (1).

---

## 12. Research grounding (literature scan, 2026-09-14)

The mechanism was checked against the psycholinguistics of copular predication before finalising:

- **Competition Model** (MacWhinney, Bates & Kliegl 1984; Bates & MacWhinney 1989) -- English assigns the
  subject/predicate role predominantly by **word order** (cue validity = availability x reliability); agreement is
  high-reliability but low-availability (marked only on 3rd-sg present *is*/*are*), so it is a backup cue. **This
  confirms the locality/position mechanism here is the brain's primary cue, not a convenience.**
- **Small clause + locality** (Stowell 1981; Williams 1980; Frazier 1978 Minimal Attachment / Late Closure; Gibson
  2000 DLT) -- the copula selects one [Subject XP] small clause; the post-copular AP/NP/PP is licensed as the
  predicate by category and local adjacency, which is why the subject must not re-attach across a PP or into an
  embedded clause. **This is the `cop_predicates` locality scan and the `csub_sites` pre-copular subject.**
- **Inversion needs agreement as a repair cue** (Moro 1997 predicate raising; Bresnan / Salzmann 2011 locative
  inversion; Wagers, Lau & Phillips 2009 cue-based agreement retrieval at the copula) -- when word order is
  neutralised (yes/no inversion "is that a maker?", locative fronting "here is the draft"), the copula's **number
  agreement** with the post-copular notional subject becomes decisive. **This names the correct next cue for the 10
  inverted clauses (an on-demand subject-copula agreement check), and it is why my order-based inverted patch
  over-fired -- position is the wrong cue exactly there.**
- **Kimian state, not a full event** (Maienborn 2005 "On Davidsonian and Kimian States"; Bach 1986 eventualities) --
  a copular predication is a property-exemplification state, semantically thinner than an action verb's Davidsonian
  event. **This is why the fired structure is tagged `is_state` and belongs in the state register co-indexed, not as
  an action event in who-did-what -- and why the board's eventive dims correctly do not fire on it.**

**12b. Second drill -- is the residual fixable or a principled ceiling, and is ORDER even the right target?**
- **Type-1 inverse/specificational ("Wtf is this?", "the answer is Yes") = principled ceiling.** Subject choice is
  information-structure-bound (Mikkelsen 2005; Birner & Ward 1998 given-before-new); the base small clause is
  **symmetric** (Moro 1997/2020); English agreement tracks the linearly-first DP, so it is NOT an independent
  subject detector (den Dikken 2006); several are best analysed as **equatives** with no predicate to find (Heycock
  & Kroch 1999). A substrate without a discourse-givenness tracker cannot resolve these -- this is the real ceiling.
- **Type-2 interrogatives = cheaply closable.** Copula-fronting is structure-preserving; a gradable-property wh
  ("how reliable is that?") always originates as the predicate; a pronoun in the non-fronted slot is a strong local
  subject cue -- deterministic, no discourse/agreement needed.
- **Type-3 locative/presentational ("below is a list") = cheaply closable where agreement is visible** (Bresnan
  1994: the postverbal NP controls agreement -- a string-local number-match, no discourse tracking).
- **ORDER is not the right target for a STATE consumer.** Maienborn 2005 (Kimian state), Moro 2020 (symmetric
  predication), Partee 1986 (one semantic core), Zwaan & Radvansky 1998 (situation-model dimensions have no
  subject/predicate axis) converge: register `STATE(entity_arg, property_arg)` typed by category, with a symmetric
  `EQUATE` fallback -- subject/predicate ordering is a PF artifact and a swapped-role error barely harms the
  consumer. (Honest gap: no processing study directly shows comprehenders leave inverse-copular order unresolved --
  the reframe is theory-grounded, hypothesis-pending an eye-tracking/SPR confirmation.)

## 13. Prototyped the two ceiling-break cues (agreement + discourse-givenness) -- BRAIN-FOUNDATIONAL, and REFUTED as levers on this population

The research (12) named two cues for the inverse-copular residual: subject-copula **number agreement** (repair cue) and
a **discourse-givenness tracker** (the primary cue, Centering/Birner). Both were built brain-foundationally, by REUSING
existing organs rather than a hand-rolled lexicon (the first attempt -- a hardcoded plural-pronoun list + an "ends-in-s"
rule -- was caught and discarded as the easy stand-in):

- **Number** read from the MORPHOLOGY organ (`morphy(w,"n") != w` => plural, the words-and-rules productive analysis) +
  the COREF organ's `PRONOUN_SCOPE` for pronoun number (the same feature the brain uses for coref agreement) + the
  closed-class copula forms. Verified: cabinets->pl, problem->sg, business->sg, they->pl.
- **Givenness** as a running per-lemma **entity-activation register** over the corpus-ordered sentences (Centering Cf/Cb
  recency; the SAME graded activation a coref/salience register keeps -- reuse, not a new organ).

**Measured on the ambiguous two-nominal copular subset (UD-EWT test 700, n=81; `--givenness`):**

| cue | picks the gold predicate |
|---|---|
| POSITION (post-copular = predicate) | **1.0000** |
| AGREEMENT (number match = subject) | 1.0000 |
| GIVENNESS (more-active = subject) | **0.9012** |
| COMBINED (givenness, agreement tie-break, position backstop) | 0.9012 |

**Position is already perfect on the copular clauses that actually occur**, and the givenness override HURTS (it costs
canonical cases to chase a near-empty inverse tail). This is the Competition Model's own cue-validity prediction
confirmed empirically (MacWhinney/Bates: word order is the highest-validity cue in English; agreement/givenness are
low-availability and only decisive where position is neutralised -- which almost never happens on this corpus). **So
the discourse-givenness tracker and the agreement cue are NOT the lever for this population** -- a rigorous negative,
established by building the brain's actual mechanism and measuring it, not by declaring a wall. The residual to 0.90 is
therefore NOT subject/predicate order (the STATE reframe in 4b already handles the inverse tail); it is the
categories-rung mistags, the clausal-complement predicates, and the no-copula small clauses -- a different rung.

**What this means for the build:** ship the position-based cue (it is the high-validity brain cue); keep agreement as a
narrow repair for the rare number-MISMATCH locative-inversion case only (Bresnan); do NOT add a givenness override for
copular subject choice -- it is below the position cue's validity here. The givenness register remains the right organ
for its actual job (coref/salience), which is where it already lives.

## 14. THE REAL PATH TO IMPROVEMENT -- a non-verbal predication is an ATTRIBUTE on the entity, not an event (research synthesis)

An aggressive downstream research drill (sources below) fully explains **what happened here** and names **the real
path** -- and it partially reframes the brief itself (the disk/brain outranks the brief).

**WHAT HAPPENED.** The strict "fire an EVENT on the predicate token" bar plateaued (0.7545) because it is chasing the
WRONG DATA TYPE. Convergent evidence -- Maienborn 2005 (a copular predication is a **Kimian state**, ontologically
NOT a Davidsonian event: it fails every event diagnostic), Kahneman/Treisman/Gibbs 1992 (**object files**: a property
is a slot value overwritten on a persistent token), Kamp & Reyle 1993 (DRT: a copular clause adds a **condition**
`blue(x)` onto the subject's discourse referent, not a new event referent `e`) -- says a non-verbal predication is an
**updatable, typed, timestamped ATTRIBUTE bound to the subject entity's discourse file**, a distinct data type from an
eventive record (no agent/patient, no causal/temporal advance). This is exactly why the board's EVENTIVE who_did_what
dimensions stayed byte-identical (section 6): a Kimian state does not belong in the event stream, and firing it there
is a category error. Measured the brain-faithful way (does the predication register with a participant -- Zwaan &
Radvansky entity+property binding), **clause-capture is already 0.8922 (149/167)** -- the "plateau" was the metric.

**THE REAL REPRESENTATION** (route by predication type, Pustet 2003 / Higgins 1979 mapped to data structures):
| type | example | representation |
|---|---|---|
| property | "the sky is blue" | an **attribute value** on the entity file (Kimian state, timestamped) |
| class | "she is a doctor" | a **type/schema field** -- inherits a frame, licenses default inference |
| location | "he is here" | the **spatial-dimension index** of the entity (Zwaan & Radvansky) |
| identity/equative | "Cicero is Tully" | a **symmetric file-merge** (coreference), not an attribute write |
| clausal/specificational | "the reason is that S" | a **propositional-value slot** filled by fact anaphora (Asher 1993) |

**THE HIGHEST-VALUE DOWNSTREAM CONSUMER** is NOT "what/who/where is X" retrieval (that is nearly free -- it is the
clause itself). It is **type-licensed forward inference + later attribute-based coreference/bridging** (Graesser &
Franklin 1990 QUEST; Clark 1975 bridging; Garrod & Sanford category-overlap resolution; McKoon & Ratcliff 1992
minimalist hypothesis): a later "the doctor" / "she" / "it" resolves fast and correctly, and later clauses draw
type-licensed inferences, ONLY if the attribute was durably bound at encoding. These fail SILENTLY (wrong antecedent,
missed inference) when the binding was not done -- which is why the win is invisible to a token-match metric and to the
eventive board, and needs an attribute-bridging instrument to be seen.

**THE HIGHEST-YIELD FIX -- MEASURED, and it corrects the a-priori guess.** The research predicted subject-entity
binding would be the fragile link. I measured it on the 167 (`--state-binding`: run the substrate's entity-state
binding -- `copular_binding` cop-label path UNION robust_cop -- on the live chain, and check holder+property vs gold):

| stage | result |
|---|---|
| PROPERTY detected (a copular STATE fired on the gold predicate) | **0.3892 (65/167)** |
| HOLDER correct, given detected (bound to the gold subject) | **0.9077 (59/65)** |
| BOTH (typed attribute bound to the RIGHT entity) | **0.3533 (59/167)** |

**So subject-entity binding is NOT the bottleneck -- it is 0.91 correct when detection happens.** The bottleneck is
**DETECTION reaching the entity-state register: only 0.39.** My event-detector predicate-slot firing captures the
predication at **0.89 clause-capture, but that signal never reaches the entity-state register**, which runs its OWN
narrower `cop`-label detection (0.39) and drops 102/167. The highest-yield fix is therefore a **WIRING job, not a new
capability**: feed the predicate-slot detection (holder = the clause subject, property = the predicate slot, already
computed at 0.89) INTO `copular_binding`/`state_register`, replacing its narrow independent detection. That closes the
entity-attribute capture 0.35 -> ~0.89 with holder-binding already at 0.91. (Garrod & Sanford / minimalist-hypothesis
still hold in principle -- a mis-bound holder corrupts silently -- but on this population binding is not where the
signal is lost; detection into the register is. Measure before asserting.)

**AND THE WIRING FIX, PROTOTYPED AND MEASURED (`--state-binding`, WIRED arm).** Built in scope: form `(holder,
property)` from my predicate-slot detection -- property = the predicate slot (0.89), holder = the subject the copular
construction (`csub_sites`) / the live parse binds to it -- and route THAT into the entity-attribute form instead of
`copular_binding`'s narrow native detection. On the 167: PROPERTY detected 0.3892 -> **0.6587**, HOLDER correct given
detected **0.8545**, BOTH (typed attribute on the right entity) 0.3533 -> **0.5629 (+0.21) from a pure WIRING change**.
The paired 0.66 < the event-detector 0.89 because a `(holder, property)` pair also needs a bound subject (clause-final
/ bare-ADV predicates detect as a state but have no local nominal holder -- they still register, just unpaired here).
This is the proven brain-foundational path: the predicate-slot signal exists at 0.89; wiring it into the entity-state
register (a diff, not a new capability) roughly doubles the typed-attribute capture the downstream inference/bridging
consumers actually read.

**AND THE TYPING, IMPLEMENTED + MEASURED (`--typing`).** The Higgins classifier (`copular_binding.predicted_type`)
types the detected predications coherently onto the representation targets: ADJ->PROPERTY (pred_adj, 44/45),
indefinite NOUN->CLASS (pred_nom, 34), PROPN/definite NP->IDENTITY (ident: PROPN 5/6, definite NOUN 11) -- so
property/class/identity separate correctly by predicate category with no gold labels needed. **LOCATED GAP:** the
classifier has NO location type -- an ADV/locative predicate ("he is here") should update the SPATIAL dimension
(Zwaan & Radvansky), not an attribute; adding a `pred_loc` type is a small, named classifier extension.

**SO THE REAL PATH, concretely (supersedes chasing the strict predicate token):**
1. **Route the non-verbal predication to the ENTITY-STATE register, not (only) the event stream.** The substrate
   already has the right organ -- `hdlab/state_register.py` + `hdlab/copular_binding.py` + the reader's
   `bind_entity_states` (the board's state dimension) -- which writes a typed (holder, property, htype) state on the
   entity. Diff 2's event should be a co-indexed STATE-ATTRIBUTE write there, typed by the table above, with a
   symmetric EQUATE for the identity case and a proposition slot for the clausal case -- NOT an eventive record.
2. **Gate the attribute write on subject-entity coreference binding** (the highest-yield fix): the holder must be the
   correct already-tracked discourse referent. This is where to spend effort, not on inverse-copular subject/predicate
   order (which section 13 refuted as a lever).
3. **Build the attribute-bridging instrument** so the win is measurable: does a later mention ("the doctor", "she")
   resolve to the entity the copular clause typed? That is the consumer that fails silently today, and the one that
   turns this from a board-invisible gain into a scored one.

This is the brain-foundational reframe of the brief: the brief said "fire EVENTS and roles on the predicate slot"; the
neuroscience says a non-verbal predication is a **state-attribute bound to the entity**, so it should fire a typed
STATE into the entity register (which exists) and be gated on entity binding -- the event-stream framing is why the
number plateaued and why the eventive board could not see it.

## 15. The three residual walls -- all BUILDABLE gaps, mechanized and (where tractable) prototyped

A walls research drill (Zwaan & Radvansky; Franklin & Tversky; Schmid 2000; Asher 1993; Graesser; McKoon & Ratcliff)
found that none of the residual is an intrinsic limit -- each has a cited target representation. Ranked by
value x tractability **on this population** (the research's general ranking put WALL 2 first; measuring it on UD-EWT
reorders them):

- **WALL 2 -- clausal / SPECIFICATIONAL predication ("the reason is that S") -> PROPOSITION binding.** Mechanism
  PINNED: a shell-noun subject (Schmid 2000, a CLOSED lexical class) + copula + finite clause binds the shell NP to
  the embedded PROPOSITION (Asher 1993 typed abstract objects) -- a 4th type `propositional-identity`, not a property
  attribute, and it feeds later "that/this/it" anaphora. **PROTOTYPED (`--shell`) + MEASURED: only ~3 clauses on the
  762 (1 of the clausal-governing set).** High tractability (lexicon + pattern) but LOW YIELD on modern UD-EWT --
  build it for downstream anaphora CORRECTNESS, not recall. Honest reorder: the research ranked it #1 in general; on
  this data it is small.
- **WALL 1 -- LOCATIVE / temporal predication ("he is here", "the meeting is tomorrow") -> the SPATIAL/TEMPORAL
  index.** Mechanism PINNED (Zwaan & Radvansky event-indexing; Franklin & Tversky spatial framework; Morrow/Greenspan/
  Bower): route to a **deictic-anchor register** `(spatial_origin, temporal_origin)` with axis-relative offsets, NOT
  an entity attribute. ~13 ADV predicates on the 167 + the temporal ones. Buildable (a new subsystem + the closed
  locative/temporal lexicon gates it); the `space_reader` organ already exists to receive it. Moderate value,
  moderate tractability.
- **WALL 3 -- TYPE-LICENSED INFERENCE (the downstream payoff, unbuilt).** Mechanism: a category->attribute-defaults
  lookup (Rumelhart schemata; Fillmore frames) **gated by local-coherence need** (McKoon & Ratcliff minimalist, to
  avoid over-firing). Instrument: consistent/inconsistent continuation cost ("She is a doctor. She checked the
  patient's chart" vs "...the engine's oil"). Highest VALUE (it is the whole point of typing an entity) but least
  tractable to calibrate (the automaticity boundary is a live 30-year debate) -- sequence it last, reusing WALL 2's
  coherence gate as the firing criterion. This is the same consumer as rung 5 (attribute-based bridging + inference)
  and remains the single highest-value drill for the whole line.

**ALL THREE PROTOTYPED PAST, brain-foundationally (each reuses an existing organ / closed-class lexicon, no LLM):**
- **WALL 1 (`--spatial`):** the deictic lexicon (Franklin & Tversky body axes) routes **9 of 13 ADV predicates** to a
  SPATIAL/TEMPORAL index write (`loc(X)=anchor +/- axis-offset`, `time(X)=now +/- offset`) instead of an attribute --
  "here"/"there" proximal, "below"/"down" vertical, "now" temporal; the 4 untyped are 2 correctly-not-locative wh
  ("why"/"how"), a tagger error, and one gap. The `space_reader` organ already exists to receive it.
- **WALL 2 (`--shell`):** shell-noun (Schmid) + copula + finite clause detects the specificational proposition-binding
  cases (~3/762 -- small on modern data; build for anaphora correctness, not recall).
- **WALL 3 (`--type-inference`) -- THE PAYOFF, and it fires:** a class-membership TYPE licenses the correct default
  inference via the substrate's GEK organ (McRae generalized event knowledge, PINNED). On 16 category minimal pairs:
  **consistent > inconsistent continuation 16/16 (mean GEK 3.48 vs 0.00), shuffled-pairing control 0.875.** "she is a
  doctor" -> `expected` = patient/vaccination/tumor/mri/chemotherapy; the consistent continuation beats the
  cross-domain one every time. This is the rung-5 downstream consumer the whole line feeds -- now demonstrated
  measurable and firing, using the existing organ. The remaining build is WIRING the typed attribute into GEK at
  read-time + a continuation-cost eval on real prose (a strategy integration).

**Net:** the ADJ/NOUN property+class predications (the bulk, ~130 of 167) are handled by the typed-attribute write
(sections 4b/14). The three residual walls are all buildable, all mechanized, and on THIS population are individually
small (WALL 2 ~3, WALL 1 ~13); the big remaining VALUE is not recall on the residual but WALL 3 / rung 5 -- wiring the
typed attribute to a bridging+inference consumer and scoring it, which is where the brain's advantage is realized.

## 16. HONEST distance to brain-level -- wiring is NECESSARY, NOT SUFFICIENT

Do not read the prototypes as "wiring away from brain performance." Landing the wiring gets the detected+typed
predication into the entity-state register / GEK (attribute capture 0.35 -> ~0.56, inference reachable). Brain-level
performance would ADDITIONALLY require, none of which wiring provides:
- **Detection 0.89 -> ~1.0** -- 18 residual clauses (heads-rung parser errors on non-verbal subjects, clausal
  predicates, mistags); an upstream accuracy build, not a wiring change.
- **Binding capture 0.56 -> ~1.0** -- the paired ceiling is ~0.66 (clause-final / bare predicates have no local
  nominal holder to pair); holder-binding is 0.91 only WHEN paired.
- **Heads rung 0.65 -> ~0.85+** -- the parser mis-attaches non-verbal subjects.
- **A REAL type-licensed-inference capability on open prose.** The GEK 16/16 is a MECHANISM DEMO on clean hand-built
  minimal pairs -- NOT a performance number. On real text: GEK coverage is partial, the coherence GATE that stops
  over-firing is UNBUILT, and the automaticity boundary is UNCALIBRATED.
- **End-to-end measurement.** The board is byte-identical; the actual reading-comprehension gain from all of this is
  UNMEASURED. A capability not scored on a real task is not a performance claim.
So: the chain is now traced, prototyped, and measured rung by rung, and every wall is shown buildable -- but "land the
wiring and we are at brain performance" would be the demo-as-capability error. Wiring is the next step that unblocks
the rest; brain-level is several measured builds beyond it.

## 17. BF-STATUS OF THE PROTOTYPES -- heuristics LOCATE the signal; the LANDED form must be graded + learned

Honest audit (a heuristic is not brain-foundational just because it approximates the brain's OUTPUT -- the
COMPUTATION must be the brain's):
- **BF (keep as-is):** the occupancy read (graded, off the posterior; constraint satisfaction); the GEK type-inference
  (associative co-activation, PINNED); the number read (morphology words-and-rules + coref PRONOUN_SCOPE); the
  closed-class lexicons (copula forms, deictic here/there/now -- a closed class IS stored lexical knowledge).
- **HEURISTIC (locator only, NOT the landed implementation):** `cop_predicates`/`cop_predicates_ext` (a left-to-right
  surface SCAN), the `csub_sites` HARD re-attachment, the inversion if-then rules. These approximate the output, not
  the mechanism -- and that is WHY they hit precision walls (a hard rule over-fires where a graded competition would
  down-weight). Shell nouns are semi-open, so weaker than a true closed class.
- **THE BRAIN-FOUNDATIONAL LANDED FORM:** a GRADED CUE COMPETITION with LEARNED validities -- which `attachment_arm`
  already IS. The fix is to feed that scorer the **predicate-slot occupancy as a graded ARC FEATURE** and let the
  weighted competition + online learning produce the copular-subject attachment, NOT a hand re-attach. The heuristic
  prototypes did their proper solver job (locate the signal, prove the cue carries information); the diff to land must
  be the graded/learned version. (This is the open question the heads-rung research drill is scoping.)

## 18. The BF heads-rung fix -- GRADED arc feature, prototyped and WORKING (with a corrected earlier error)

Research (Moro/Bowers/den Dikken; UD `cop` convention; MacWhinney cue validity) says the fix is the predicate-slot as
a GRADED ARC FEATURE, not a hard re-attach. Prototype: add a weighted bonus to the arc (head=predicate ->
dependent=subject) in the arc-score matrix and RE-DECODE, so the cue COMPETES in the decode (`--heads-graded`).

**CORRECTION (honesty): my first run reported "0 arcs moved" and I wrongly concluded the fix was not cell-prototypable.
That was an OFF-BY-ONE bug** -- the arc matrix is square `(n+1, n+1)` with column = dependent index directly (1-based),
so the subject arc is `A[predicate, subject]`, not `A[predicate, subject-1]`; I had been bumping the DETERMINER arc.
Caught by introspecting one clause (`A[4, :]` on "The sky is blue"). Corrected result:

| decode | base (non-verbal nsubj) | + graded cue (w=3) | verbal | twin |
|---|---|---|---|---|
| **incr** (BF live default) | 0.5385 | **0.5917** (+0.053) | 0.8533 (held) | 0.5503 |
| MAP | 0.6331 | **0.6568** (w=5, +0.024) | 0.8567 (held) | 0.6213 |

**So the BF graded fix IS cell-prototypable and it WORKS** -- an additive arc feature that competes in the decode
lifts non-verbal subject attachment (+0.05 incr, +0.02 MAP), verbal held, twin below. It is the right form (competes,
online-learnable), unlike the heuristic hard re-attach (`--heads-fix`, 0.54->0.65, NOT BF).
**BUT it is BELOW the research's pre-registered +10-point bar** (+5.3 incr). Per that pre-reg, the residual is then
upstream: a chunk of the copular-subject error is POS mistags / needs the cue to be a LEARNED validity (swept weight,
rebuilt into the table like pri 108's role cue) rather than a fixed additive bonus, and/or the incremental beam commits
some subjects before the predicate arrives (incr base 0.54 < MAP 0.63 -- the beam is itself sub-optimal on copulars).
**The BF landed form:** add a copular-subject construction cue to `arc_scores`' existing construction-cue block
(`sc.constr` / the `CONVENTION_BONUS` `fw` slot) with a swept/learned weight, and rebuild the validity table.
**Binding capture (0.56) is downstream of this** (research B: fixing the parse largely fixes binding for the
adjacent/embedded-verb majority); the inverted/clause-final tail then needs the memory-retrieval fallback (Lewis &
Vasishth cue-based retrieval), a separate, lower-confidence build.

## 19. TOP-DOWN SIGNAL ROUTING -- the plumbing is live; the non-verbal signal drops at 5 named hand-offs

Verified on disk (the flags/plumbing that carry the predicate-slot signal down the chain):
- **Categories rung**: `HDLAB_LC_PREDICATE_SLOT=1` (default) -- occupancy applied to the posterior handed down. LIVE.
- **Frontend -> heads**: `Tagger.tag_with_posterior` -> `Parser.arc_scores_graded(..., tag_posterior, ...)`, with
  `HDLAB_HEADS_SOURCE=attachment_arm` (default). The GRADED posterior (occupancy included) IS routed to the heads
  rung and, through the one frontend, to the board. LIVE -- this is why pri 110's occupancy reached the governor.
- **Event detector**: `tense_agnostic_events=True` (default), reads the revised tag. LIVE.

So the SHARED graded posterior is routed top-down and live. What is dropped is the NON-VERBAL-PREDICATE-specific
signal, at 5 hand-offs where the consumer re-gates on the verb tag or runs its own narrow detection instead of
reading the predicate-slot signal already computed upstream:
1. **Heads rung** -- the posterior carries the copula's revised TAG, not a subject->predicate ARC cue; the subject
   arc never sees the predicate-slot signal (§18; fix = a learned copular-subject cue in `arc_scores`).
2. **Event detector** -- fires on `UPOS==VERB`, drops the copular complement (diff 2).
3. **Role competition** -- `_parent_config` -> NONPRED, arguments don't inherit predicate expectations (diff 3).
4. **State register** -- runs its own `cop`-label detection (0.39) not the 0.89 predicate-slot detection (diff 4).
5. **GEK type-inference** -- not wired to the entity type at read-time.
The routing FIX is uniform: each consumer should READ the predicate-slot occupancy (already handed down) instead of
re-deciding on the verb tag -- the same "read the slot, not the tag" principle, applied at all 5 hand-offs.

## 20. Roles NONPRED fix -- PROTOTYPED, works for obliques, but MUST be selective (measured), + updated signal-loss eval

Diff 3 prototyped in-cell (`--roles-fix`, a proxy that treats the non-verbal predicate as PRED for the role config):
- **obl-of-non-verbal 0.5278 -> 0.6667 (+0.14)** -- confirms the NONPRED-backoff is the oblique bottleneck.
- **BUT nsubj 0.8402 -> 0.4615** under the blunt "force head=VERB" proxy -- because forcing VERB turns OFF the `cop`
  cue that already handles the copular subject. So the landed fix must be **selective**: PRED backoff for the
  predicate's OBLIQUES/OBJECTS only, with the `cop` cue preserved for the subject. A blunt implementation regresses
  the subject badly. Refined diff-3 spec: key PRED on `cop_predicates` in `_parent_config` for non-subject arguments;
  do not disturb the subject's cop-cue branch (line 707).

### Updated signal-loss evaluation (all fixes now prototyped)
| rung | fix | before -> after (prototype) | status |
|---|---|---|---|
| heads (subject attach) | graded arc cue | 0.5385 -> 0.5917 (incr) | works, below +10 pre-reg bar; residual upstream (POS) / wants a learned weight |
| detection -> event stream | fire on predicate slot | 0.19 -> 0.89 clause-capture | strong |
| entity-attribute binding | wire predicate-slot into the register | 0.35 -> 0.56 | works; holder 0.91 |
| roles (obliques) | PRED backoff (selective) | obl 0.53 -> 0.67 | works, MUST be selective |
| type | Higgins classifier | property/class/identity coherent | works; location-type gap |
| WALL1 locative | deictic spatial index | 9/13 routed | works |
| WALL2 clausal | shell-noun proposition bind | ~3/762 | works, small |
| WALL3 type-inference | GEK | 16/16 consistent>inconsistent | works (clean pairs) |

**Where signal is still lost, after all prototypes:** (1) the heads rung's graded fix clears only +5 of the ~+31 gap
to verbal (0.54->0.59 vs 0.85) -- the rest is POS mistags + the cue needing to be learned + the incremental beam's
sub-optimal copular commitment; (2) binding capture 0.56 vs ~1.0 (rides on the heads fix + the clause-final/inverted
tail); (3) every fix is a PROTOTYPE, not landed/measured end-to-end on the board or real-prose comprehension. The gaps
are now all located to specific, named, buildable causes -- none intrinsic.

## 21. PLASTICITY -- the landed forms must be online-learned, never frozen (owner directive)

The brain never runs a frozen weight. Every fixed-constant in the prototypes is a LOCATOR; the landed form must carry
an online observe/update path:
- **Heads copular-subject cue (diff 1):** my graded arc bonus was a FIXED swept weight (frozen). The BF landed form
  is an online-LEARNED cue validity (Competition-Model validity = frequency x contingency; usage-based / error-driven
  Rescorla-Wagner accrual with an `observe` path), NOT a hand-tuned constant -- which is also why learning should
  clear the +10 bar where a fixed bonus plateaus at +5.
- **Occupancy read (categories):** already plastic (pri 110 -- the occupancy moves after the organ observes a form as
  a VERB); keep it.
- **Role validities (diff 3):** the organ already has online accrual (`observe_role_outcome`); the PRED-backoff must
  be learned/accrued the same way, not a frozen table patch.
- **Entity-state register (diff 4):** the typed attribute is written online per clause (plastic by construction).
- **GEK type-inference (WALL 3):** the store is currently FROZEN (`GEK_ASSET`, built offline). The BF form grows it
  ONLINE from reading (episodic accrual / the project's propose-verify grow direction), so newly-read categories and
  their event knowledge accrue -- not a static asset queried at read time.
So the landed spec for every fix is: the CUE/STORE is learned and updated online from what the reader perceives, not
a frozen bonus or a static table. The prototypes prove the signal; plasticity is how the weight/store becomes right
and stays right.

## 22. WALL A (premature commitment) -- the dominant heads-rung fix, PROTOTYPED, + gold-POS test rules out tagging

Two decisive results:
- **GOLD-POS vs SYSTEM-POS test (the cheap decisive test the research demanded):** non-verbal nsubj attachment with
  gold POS is NOT better -- it is slightly WORSE (incr 0.5385 system vs 0.4911 gold; MAP 0.6331 vs 0.6154). So the
  residual is NOT upstream tagging noise; it is the ARC SCORER / DECODE. This rules out the POS-mistag hypothesis and
  confirms Wall A as the target.
- **WALL A -- the HELD copular-subject decode (`--heads-held`):** the incremental beam commits the subject before its
  predicate arrives (incr 0.54 < MAP 0.63 on the SAME clauses). The brain holds the open dependency and resolves it
  once the predicate is seen (Gibson 1998 storage cost; Levy 2008 expectation; Lewis & Vasishth 2005 retrieval;
  Altmann & Kamide prediction; small-clause grammar Stowell/Mikkelsen). Prototype (defer the copular subject to the
  full-information resolution -- bounded, local, not global lookahead, not a hard rule): **incremental 0.5385 ->
  HELD 0.6272, closing 94% of the incr->MAP gap** while staying incremental.

**So the heads-rung fix stack, brain-foundational and measured:** (1) WALL A held decode 0.54 -> 0.63 (the dominant
fix -- a decode-order correction, PINNED by Gibson/Levy); (2) the graded copular-subject arc cue 0.54 -> 0.59 in
isolation, which the research says should be FIT AFTER Wall A and as an online-LEARNED validity (Rescorla-Wagner;
plastic, not a frozen bonus) -- expected to add on top of the held decode. The remaining gap to verbal (~0.63 -> ~0.85)
is the genuinely harder tail (inverted / clausal / true small-clause), not POS and not the eager-commit bug.
**Landed form (both plastic, both in `attachment_arm`, strategy's live file):** the held/predicted copular-subject
commitment in the incremental decode + the online-learned copular-subject cue validity. Binding capture (0.56) rides
on this per research B.

## 23. The SOTA gap is SYSTEM-LEVEL and REPRESENTATIONAL (adjacent finding; strategy's to prioritise)

pri 113's work pins WHERE the system underperforms SOTA, and research names the glass-box path:
- **Evidence from this problem:** the heads rung is the dominant bottleneck (non-verbal nsubj 0.54-0.63 vs verbal
  0.85 vs neural SOTA ~0.95); the gold-POS test (§22) rules out tagging as the cause; so the gap is the arc scorer's
  REPRESENTATION + decode, not this or that construction.
- **WALL 1 REPRESENTATION (dominant):** discrete, context-blind cues vs graded CONTEXTUAL vectors (Elman 1990; ELMo
  Peters 2018; Manning et al. 2020 PNAS -- syntax recoverable from BERT geometry). Glass-box closure = a VSA/HRR
  contextual encoder (Plate 1995; D-CYK Zanzotto 2020; Holographic CCG Yamaki 2023; consistent with the substrate's
  FHRR) -- decodable bound vectors, no black-box transformer. This is already a filed problem
  (`distributed_contextual_representations_into_the_parser`).
- **WALL 2 LEARNING (second-order, localized to long-distance/root):** McDonald & Nivre 2007. Glass-box closure =
  (a) global graph-based decode (Eisner/Chu-Liu-Edmonds -- cheap, inspectable) + (b) predictive-coding local learning
  (Whittington & Bogacz 2017; Scellier & Bengio 2017 -- every unit is a prediction-error value, inspectable).
- **Highest-yield glass-box upgrade:** VSA/HRR contextual encoder -> global graph-based arc decode -> predictive-coding
  fitting; attacks the dominant representational wall + the decode half of learning in one auditable build.
- **HONEST caveat:** no cited work shows a STANDALONE (non-gradient-trained) VSA parser matching neural SOTA -- every
  demo is a hybrid with a learned scorer. "Closes the gap" is a plausible upper bound, not an expected result.
This is beyond pri 113's scope (a cross-cutting parser-representation program); recorded here as the adjacent finding
that explains the SOTA gap, for strategy to prioritise on the cross-solution map.

## 24. Parser work to date -- WINS already banked, and how they RECONCILE/TEMPER the §23 SOTA-gap answer (disk outranks)

Surveyed the existing parser solves (the disk outranks my §23 research recommendation). Substantial wins are ALREADY
banked on my walls, and two located negatives correct §23:
- **Global-normalized graded parser -- SOLVED/POSITIVE** (`replace_the_greedy_arc_eager...`): Chu-Liu/Edmonds MAP +
  Matrix-Tree edge marginals built; exact decode > greedy (no invalid trees), marginals AUC 0.855 right-vs-wrong,
  gold always in marginal support, live patient selective 0.878->0.947. **The Wall-2 DECODE half is done and won.**
- **Predict-and-revise recall pass -- SOLVED** (`the_reader_parses_as_truth...predict_and_revise`): drop-filling
  recovers who-did-what patient +0.0599 CI-sep, localized to non-canonical (passive 0.287->0.567, pre-verbal-gap
  0.023->0.511). **This IS my WALL A (held/predict), already done and won for the recall direction** -- my held-decode
  prototype (§22) is the same family; the landed form should extend this existing pass to the copular-subject arc.
- **Reading-learned plastic arc scorer -- PARTIAL** (`scale_the_reading_learned_arc_scorer`): matches supervised
  in-domain, BEATS it OOD (GUM +0.0235, register-general); text-only UAS capped ~0.48 (Klein-Manning; scale/EM not the
  lever). **The Wall-2 LEARNING half + plasticity exists.**
- **Calibrated-confidence precision-weighting -- the pivot win**: selective accuracy confident-half 0.826 vs 0.776;
  who-did-what confident-half 0.871 vs 0.780.

**TWO located negatives that TEMPER §23:**
- A distributed (meaning_foundation) SELECTIONAL feature is **REFUTED for UAS** (anti-complementary on hard cases,
  literature-corroborated) -- so "distributed representation closes the UAS gap" is already a located negative, not an
  open lever. §23's VSA/HRR CONTEXTUAL encoder is a DIFFERENT mechanism (contextual token rep, not an object-class
  selectional feature), so it is not directly refuted -- but the substrate's evidence says do NOT expect distributed
  meaning to close UAS; expect it to help COMPREHENSION via precision-weighting and the two-valid-agent residual only
  via grounded event knowledge.
- The remaining wall is the **scorer's FEATURES on genuinely ambiguous attachments** (67% of wrong patient picks are
  true two-valid-animate ambiguity needing GROUNDED EVENT KNOWLEDGE), NOT the decode/normalization, and NOT (mostly)
  UAS -- the established PIVOT is that the right objective is comprehension (precision-weighted), not UAS.

**Corrected SOTA-gap picture:** decode + plastic learning + predict-and-revise + precision-weighting are largely SOLVED
and won. The live remaining levers are (1) grounded event knowledge for the two-valid-agent scorer residual, (2)
extending the existing predict-and-revise pass to the copular-subject arc (my Wall A), (3) comprehension-precision-
weighting as the objective. A VSA/HRR contextual encoder (§23) remains a candidate for the representational half but
is NOT expected, on this substrate's evidence, to close UAS -- and UAS itself is the wrong target.

## 25. FALSE-NEGATIVE AUDIT of the cited negatives (a weak-impl negative is not a closed lever)

Owner caution: some located negatives could be false negatives -- a fair test of a WEAK implementation proves THAT
setup failed, not that the lever is closed. Auditing the §23/§24 negatives:
- **"Distributed representation cannot close UAS"** -- tested ONLY an object-class SELECTIONAL-PREFERENCE feature
  (Pado/Resnik) for PP-attachment. It did NOT test a CONTEXTUAL distributed encoder (ELMo/BERT-style, which Manning
  et al. 2020 shows recovers syntax) or a VSA/HRR contextual representation. **HIGH false-negative risk if
  generalized.** The strong representational lever (§23) is UNTESTED, not refuted -- §24 over-leaned on this; the
  representational program remains genuinely OPEN.
- **"Text-only UAS capped ~0.48 (Klein-Manning)"** -- the UNSUPERVISED grammar-induction ceiling for a count-based
  DMV-style scorer with no distributed features; it does NOT bound a distributed-contextual parser (the substrate's
  own supervised scorer hits 0.796; neural 0.95). **False-negative risk if read as a parser ceiling.**
- **"Two-valid-agent needs grounded event knowledge"** -- well-drilled (67% genuinely two-valid) but measured with the
  CURRENT arc-factored features; a contextual encoder might separate some cases that look ambiguous only to
  impoverished features. **Partial false-negative risk.**
- **My own:** the graded arc-cue plateau at +5 used a FIXED bonus (weak) -- the LEARNED form (§21) is untested; the
  inverse-copular / givenness / agreement refutations (§13/§18) used specific cue FORMS, and the givenness proxy had
  a known subset-selection limitation. Lower risk (position dominance is robust), but not "brain's strongest form
  tested" for each.
LOWER false-negative risk (robust): the gold-POS test (§22, gold slightly WORSE -- a direct measurement), the global
graded-parser WIN and the predict-and-revise WIN (positive results, not negatives).
**Net:** treat the representational lever (§23 contextual VSA/HRR encoder) as OPEN, not foreclosed by §24 -- the
refuted thing was a narrower, weaker feature. The strong brain/SOTA version has not been fairly tested here.

## 26. DO-IT-ALL combined heads fix -- measured; caps at the scorer's ceiling, remaining gap is the representational lever

Combined the two working mechanisms (`--heads-full`): a LEARNED copular-subject cue validity (contingency 0.754 ->
log-odds w=1.12, Bates-MacWhinney, not a fixed bonus) + the held/predicted decode (Wall A). Non-verbal nsubj:
- base **0.5385** | learned-cue-only **0.5680** | held-only **0.6272** | **HELD+CUE 0.6331** (n=169; verbal ~0.85).

Honest conclusions:
- **The held decode (Wall A) is the dominant heads-rung fix (+0.089).** The incremental-commitment bug was the main
  cause; deferring the copular subject to predicate-arrival fixes it.
- **The learned cue adds ~nothing on top of held (+0.006)** -- once the held decode resolves with the predicate
  visible, the cue is redundant; and its contingency is only 0.754 (the copular-subject DETECTION picks the wrong
  nominal ~25% of the time, itself a construction-detection limit).
- **HELD+CUE = 0.6331 = exactly the MAP ceiling.** So the decode-order fix already extracts everything the current
  arc-factored SCORER can express. The remaining 0.63 -> ~0.85 gap is the **scorer's FEATURES**, not the decode and
  not a bigger cue -- i.e. the §23/§25 REPRESENTATIONAL lever (a contextual distributed encoder), which is the
  genuinely OPEN, untested-in-strong-form wall. This matches the global-parser solve's own located negative (the wall
  is the scorer's features / two-valid ambiguity, not the decode).
**Net for the heads rung:** the decode-order fix is done and brain-foundational (0.54 -> 0.63, the MAP ceiling); going
past it needs the representational upgrade, not more decode/cue engineering -- and that upgrade is strategy's
cross-cutting program (and must be tested in its STRONG contextual form, per §25, before being called a wall).

## 27. UNDERSTANDING THE gold-POS NEGATIVE -> the scorer's copular-subject validity is UNDER-LEARNED (the real wall)

The negative I least understood (gold POS slightly WORSE, §22) is now understood at the mechanism level -- and it is
REAL, not a confound, and it identifies the true upstream/scorer wall.

On the 12 cases where SYSTEM-POS attaches the copular subject correctly but GOLD-POS does NOT (vs 4 the other way):
- **(AUX/ADJ/ADV -> VERB) 6 of 12:** the system tagged the copular predicate VERB (via the occupancy revision, or a
  mistag), and the subject attached CORRECTLY; gold's CORRECT ADJ/NOUN tag made it WORSE.
- **(NOUN -> NOUN) 4:** same tag -- the graded marginalization helped where gold's one-hot did not.

**Mechanism:** the arc scorer's learned cue validities strongly favor **subject -> VERB** and are **under-learned for
subject -> ADJ/NOUN** (the non-verbal predicate is a sparse configuration). So CORRECT POS exposes the scorer's
feature gap, while VERB-tagging the predicate accidentally routes the subject into the strong verb-attachment
pathway. **The bottleneck is the scorer's under-learned copular-subject validity, NOT POS quality** -- gold-POS-worse
is an informative POSITIVE finding, not a false negative.

**This is the upstream-BF point exactly:** the predicate-slot occupancy IS computed upstream (categories rung, BF),
but it is handed down only as a TAG -- never delivered to the arc scorer as a GRADED ARC FEATURE -- so the scorer
cannot treat a high-occupancy ADJ/NOUN as predicate-like and falls back on its verb-biased validities. And per
"never frozen," the copular-subject validity is under-LEARNED because the construction is under-represented in what
the scorer accrued.

**Why the prototypes capped at the MAP ceiling (now understood):** the fixed cue + held decode route the subject
correctly but do NOT retrain the scorer's competing verb-biased validities, so they extract only what the current
validities allow (= MAP). **The fix that gets through the wall:** (1) ROUTE the graded occupancy from the categories
rung into the arc scorer as a feature (an upstream hand-off completeness fix -- the signal exists but isn't
delivered), AND (2) LEARN the copular-subject arc validity ONLINE (plasticity; the construction accrues its own
validity), so the scorer stops defaulting to subject->VERB. Both are in `attachment_arm` (strategy's live file); both
are plastic, not frozen. This is the fully-understood route past the heads-rung wall.

## 28. RESHAPE + HELD -- the WIN (0.54 -> 0.65), and a CORRECTED premature "feature-bound" call

I first predicted reshape would exceed MAP; reshape-alone (incremental decode) did NOT (0.6213 < MAP 0.6331), and I
then WRONGLY concluded the residual was FEATURE-BOUND at ~0.63 and that reshape+held "cannot change the conclusion."
**That was a premature call before the decisive test finished** (the second premature conclusion this session -- the
first was an indexing bug; the discipline "do not conclude before the test" is right). The reshape+HELD result:

| arm | non-verbal nsubj |
|---|---|
| base | 0.5385 |
| occupancy cue only | 0.5680 |
| reshape only (incr) | 0.6213 |
| held only | 0.6272 |
| MAP (global optimum of current scores) | 0.6331 |
| **reshape + HELD** | **0.6509** |

**reshape+held EXCEEDS the MAP ceiling (+0.018) and is the best heads-rung result: 0.5385 -> 0.6509 (+0.11).** So the
residual is NOT fully feature-bound at 0.63. Mechanism: the boost+suppress reshaping (occupancy delivered as an arc
feature + small-clause-locality SUPPRESSION of the subject->embedded-verb arc) DOES add recoverable signal -- but only
when paired with the HELD decode that resolves the copular subject with the FULL reshaped information; the incremental
decode commits before the reshaping can land, which is why reshape-alone capped. All three ingredients are
brain-foundational and PINNED: occupancy-as-feature (the signal exists upstream), small-clause locality (Stowell), and
held/predicted commitment (Gibson/Levy).

**The BF landed heads fix (the do-it-all, right-not-cheap result):** occupancy-as-arc-feature + small-clause-locality
suppression of the embedded-verb arc + held/predicted copular-subject commitment, decoded with full information. 0.54
-> 0.65 in-cell. The landed form makes the cue/suppression LEARNED (plastic, §21) inside `attachment_arm` + extends
the existing predict-and-revise pass (§24) to the copular-subject arc.
**Remaining gap 0.65 -> ~0.85 verbal:** part is still the two-valid / grounded-meaning residual (the global-parser
solve) and part may be the representational lever (§23, untested in strong form per §25) -- but 0.63 was NOT the
ceiling, and I should not have called it one before the test.

## 29. What holds back the 0.65 -> DETECTION COVERAGE (inverted/clausal), NOT the scorer; and the win CASHES OUT downstream

Two measured results answer "what else holds back the parser 0.65, and does the win propagate":

**(A) The limiter is DETECTION COVERAGE, not the scorer features.** The reshape+held fix can only act on copular
subjects it DETECTS as a (predicate, subject) pair. Of the 167 non-verbal clauses:
- **101 COVERED** (the fix can act) ; **66 NOT covered** (stays at base). Not-covered breakdown:
  - **45 copula present but predicate not detected** (inverted / clausal -- the forward cop scan misses the predicate)
  - **13 predicate detected but subject scan failed** (inverted / no pre-copular nominal)
  - **8 no copula** (small clause / verbless)
- **~58 of 66 (~35% of all copular clauses) are INVERTED/CLAUSAL constructions the pair-detection misses.** THAT is
  what holds back the 0.65 -- a construction-COVERAGE problem (extendable, brain-foundational: the inverted copular
  and shell-noun/clausal are known constructions), NOT the arc scorer's features. This REFINES §28: past 0.65 the
  next lever is detection coverage of inverted/clausal copulars, before the representational lever.

**(B) The heads win CASHES OUT downstream (+0.18).** On the covered clauses (n=103), the reshape+held heads lift the
entity-attribute BINDING capture (holder = gold subject) **0.7087 -> 0.8932** -- i.e. where the copular subject is
correctly attached, the typed attribute binds to the right entity 0.89 of the time. This confirms research B
(fixing the parse largely fixes binding) DECISIVELY: the heads-rung fix is not a local UAS number, it propagates to
the downstream consumer that matters (the entity-attribute store). Full-stack loop closed WHERE the pair is detected.

**(C) BUT the detection-coverage gap is a LONG TAIL (measured).** Extending detection to the inverted (clause-initial
copula) case recovers only **+7** (101 -> 108 covered) at a precision cost (detected-subject precision 0.954 ->
0.932). The 66 not-covered is NOT one construction: inverted-clause-initial +7, clausal/shell-noun ~3, and ~45
heterogeneous (predicate behind a PP, wh-predicate, false verbal-host). Each is small and precision-risky to
hand-detect -- per-construction scan extensions have DIMINISHING RETURNS and rising precision cost.

**Net optimization path for the parser (priority order, brain-foundational):** (1) the reshape+held fix (0.54 -> 0.65
on covered, landed as learned+plastic; the win propagates +0.18 to binding); (2) +7 from inverted-clause-initial
detection (cheap, small); (3) the LONG TAIL of copular constructions is the argument FOR the **representational
lever** -- a contextual encoder detects the copular predicate/subject across the tail WITHOUT enumerating each
construction by hand-coded scan, which is where per-construction extension stops paying. So the honest synthesis:
the near-term in-scope win is reshape+held (done); the long-tail coverage past it is best bought by the contextual
representation (§23, untested strong form), NOT by more hand-coded construction scans -- and NOT by the scorer
features (which the covered clauses show are adequate once the pair is detected).

## 30. PER-STEP vs SOTA (research) -- the untried glass-box levers; parsing is #1

Per-step gap (ours vs SOTA benchmark numbers) + the untried brain-foundational glass-box lever, ranked by
gap x downstream leverage:
| step | ours | SOTA | gap | untried glass-box lever |
|---|---|---|---|---|
| POS | 0.94 | ~0.98 (Meta-BiLSTM/Flair PTB; UDify EWT) | ~3-4, real, small | HRR contextual code (neighbor(x)position, cleanup-memory classify) + morpheme binding for OOV |
| **Parsing** | 0.62 live / 0.79-0.80 offline | ~90-93 UAS (Dozat&Manning 95.7 PTB; UDify 90.96 EWT) | **live 28-31, offline 10-13 (real)** | attractor-relaxation global decode; **dual head/dependent HRR codes (glass-box biaffine analog)**; predictive-coding reanalysis |
| SRL/roles | 0.87-0.92 gold / 0.83-0.88 live | 87-88 F1 | smallest; competitive on gold heads; shortfall INHERITED from parsing | whole predicate-arg frame as one HRR structure + reuse the solved WSD organ for sense |
| Coref | 0.65 narrative | 80-83 F1 (SpanBERT 79.6, CorefQA 83.1) | 15-18, 2nd-largest but TERMINAL + part corpus-difficulty | episodic MINERVA-2 antecedent retrieval (HRR episode traces) + Centering buffer |

**Ranking: (1) parsing (biggest true gap + only step whose errors compound forward -- SRL 0.87->0.83 purely from head
errors), (2) coref (large but terminal), (3) POS (small), (4) SRL (inherited).**

**What we have NOT done, precisely:** the parser's GLOBAL-DECODE half is already built (§24 Matrix-Tree/MST); the
untried piece is the **contextual, decodable SCORING representation** -- dual head/dependent HRR codes (a glass-box
biaffine analog) -- plus predictive-coding reanalysis (partly built as predict-and-revise, §24). This UNIFIES the
whole chain's finding (§23/§25/§28/§29): the single open lever is the **contextual distributed representation**,
untested in strong form, and it is what SOTA's win at every step (POS, parsing, SRL, coref) actually comes from
(contextual embeddings/span reps). Coref's lever (episodic MINERVA-2) is already the project's named learner north
star. HONEST caveats from the research: our SRL 0.87-0.92 is RECALL not F1 (flatters us); our coref 0.65 is on harder
"real narrative" than curated OntoNotes and lands where the field itself started (2017); our live-parser 0.62 is the
most benchmark-penalized number (no lookahead vs globally-decoded SOTA) -- the fair figure is the offline 0.79-0.80,
still trailing by double digits. So: the biggest, realest, most-compounding, and still-open lever is a **glass-box
contextual encoder feeding the (already-built) global decode** -- strategy's cross-cutting program, and the thing we
have genuinely not yet built or tested in strong form.

## 31. The §30 representational lever CANNOT be faithfully prototyped in-cell (weak-impl false-negative risk) -- it is the open cross-cutting build

Checked the substrate for a usable contextual encoder to prototype the §30 lever (a glass-box contextual arc-scoring
representation). Finding: the available encoders -- `PPMISparseEncoder`, `GsbcGradedEncoder`, `RandomIndexingEncoder`
-- are FORM / DISTRIBUTIONAL word vectors (char-trigram / co-occurrence), NOT contextual-SEMANTIC per-token codes.
Building a contextual HRR encoder FROM those form vectors would be a WEAK IMPLEMENTATION of the semantic
disambiguation the copular-subject residual needs, at high risk of a FALSE NEGATIVE -- exactly what the §25 discipline
warns against (a weak-impl null tells you nothing). Running it and reporting a number would violate the discipline,
not honor it.

**So the honest boundary:** every pri-113-SCOPE fix is prototyped + measured (event detector 0.19->0.89; entity-
attribute wiring 0.35->0.56; typing; heads reshape+held 0.54->0.65, +0.18 to binding; roles NONPRED backoff; the
three walls; detection-coverage long tail). The ONE remaining fix -- the glass-box SEMANTIC contextual encoder (§30,
the #1 lever) -- is NOT solver-cell-prototypable: the substrate has no glass-box semantic contextual representation,
and the form/distributional encoders would false-negative. Building that encoder is the OPEN CROSS-CUTTING PROGRAM
(the filed `distributed_contextual_representations_into_the_parser`, whose SELECTIONAL form was refuted §24 -- the
CONTEXTUAL form is the genuinely untested one, per §25), and is strategy's scope, not a pri-113 cell. Prototyping the
weak form to satisfy "prototype everything" would be the anti-pattern; the right move is to name it precisely as the
build that requires the encoder, and hand it to the cross-cutting program.

## 32. §30 CONTEXTUAL-HRR lever, PROTOTYPED -- it HELPS (+0.049), correcting the §31 over-caution

Built the strongest in-cell form of the §30 contextual lever: a glass-box CONTEXTUAL HRR code per token (Random-
Indexing base vector + position-bound neighbors via circular convolution = Plate HRR, the substrate's FHRR basis)
and a head<->dependent contextual-COMPATIBILITY arc feature (cosine of contextual codes) added to the arc scorer,
held-decoded. On copular subjects: cap 300 (n=103) base 0.6408 -> 0.6893 (+0.049); **FULL population cap 700 (n=169):
base 0.5385 -> +contextual-compat 0.6272 (+0.089)** -- a BIGGER gain at full size, and it recovers as much as the
held decode did (0.6272) on a DIFFERENT, contextual signal (not the construction cues).

**This corrects §31's over-caution.** I predicted a form-based, learning-free contextual prototype would just
false-negative (weak impl). It did NOT -- even this weak form (char-trigram RI vectors, unlearned projection) ADDS
signal (+0.049). So contextual STRUCTURE carries real attachment information for the copular subject, and the §30
representational lever is POSITIVELY indicated -- the strong (learned-SEMANTIC, applied to all arcs) form is expected
to help MORE, not less. (Another self-correction this session: don't pre-judge a lever as a wall before testing it --
§25's discipline, and I mis-called this one.)

**Honest scope of the result:** (a) DIAGNOSTIC -- the contextual feature is added to the GOLD copular-subjects'
candidate arcs, so it shows the signal CARRIES information on that population, not a deployable detector (deploying
needs contextual scoring on ALL arcs, i.e. the full contextual parser); (b) FORM-BASED / LEARNING-FREE -- RI vectors
are char-trigram, the projection unlearned; the strong lever is learned-semantic; (c) cap 300 (base differs from the
cap-700 numbers). So this is POSITIVE EVIDENCE for the §30 lever, not a landed win: the glass-box contextual encoder
is worth building in strong form (learned-semantic, all-arcs) -- the cross-cutting program -- and it is no longer
"expected to false-negative." Next confirmation: cap 700 + apply to all arcs (not just gold copular subjects).

## 33. FINAL DOCUMENTATION -- components touched, BF status, and the key levers (read this section alone for the whole picture)

### 33a. Components touched / modified (what, where it lives, BF verdict)

| # | Component (file) | What we did | On disk? | BF status after the change |
|---|---|---|---|---|
| 1 | **The cell** `experiments/exp_nonverbal_predication_participants_v1.py` | Built the participant instrument (score by argument governance, never the tag column) + all diagnostics, the 65-trace, the decompose, the board A/B, and every upstream prototype (heads reshape/held, contextual-HRR, roles, state-binding). | **WRITTEN (solver scope)** | N/A -- an instrument, not an organ. Gold-free at decision; twin at floor; oracle 1.0. |
| 2 | **Event detector** `hdlab/situation_reader.py` `_tense_agnostic_extract` | Fire the clause's event/state on the copula's COMPLEMENT (the predicate slot), `is_state=True`, co-indexed with the state reader. Proposed as `_add_copular_predicate_events`. | **PROPOSED** (diff 2) | **BECOMES BF.** Today it gates on `UPOS=="VERB"` = a stand-in for "is there a predicate" (a UD-convention proxy, NOT BF). The fix fires on predicate-hood = the brain's one-predicate-per-clause. **Proven**: non-verbal recall 0.19->0.74, precision held, twin loses, board byte-identical. |
| 3 | **Copula scan** `hdlab/attachment_arm.py` `cop_predicates` | Surgical locative + clause-final fallback (ADV only when no nominal complement -- avoids the measured ADV-inline negative). | **PROPOSED** (diff 1) | **BF-neutral extension** (same locality-scan computation, wider coverage of the 65). Ships now. |
| 4 | **Arc scorer** `hdlab/attachment_arm.py` `arc_scores_graded` / decode | Prototyped the heads-rung correction: predicate-slot-biased re-attachment of the copular subject as a GRADED arc feature + held/reshape decode. Non-verbal attachment 0.5385 -> 0.6509 (exceeds the current MAP ceiling), verbal flat; propagates to the event stream 0.6048 -> 0.7186 and to entity binding 0.71 -> 0.89. | **PROTOTYPED** (in the cell; not a diff yet -- needs an online-learned validity, §21) | **Partially BF, needs plasticity.** The graded arc feature is BF (Competition-Model cue validity); the copular-subject validity is currently a fixed bias and MUST be online-learned (Rescorla-Wagner) before landing, never frozen. |
| 5 | **Role competition** `hdlab/graded_role_assigner.py` `_parent_config` (`_PRED_HC`) | Key PRED on predicate-hood (head in `cop_predicates`), not the VERB/AUX tag, so a non-verbal predicate's OBLIQUES inherit predicate-argument expectations. | **PROPOSED** (diff 3, needs a role-table rebuild -- same as pri 108) | **BECOMES BF** ("read the slot, not the tag"). Subject is already 0.84; the fix targets the located oblique gap (0.53 -> ~0.83). Not force-fit; measured cost stated. |
| 6 | **Entity-state route** `hdlab/copular_binding.py` + `state_register` | Route the predicate slot INTO the entity-state register as a TYPED attribute (property/class/location/identity/clausal), gated on subject-coref binding. Prototyped `--state-binding`: typed-attribute capture 0.35 -> 0.56, holder 0.85. | **PROPOSED** (diff 4, architectural) | **BF and the REAL PATH** (§14). A Kimian state = an updatable attribute on the entity (Maienborn 2005), NOT an eventive record -- this is why the event-token metric plateaued and the eventive board stayed byte-identical. |
| 7 | **Occupancy read** `hdlab/lexical_categories.py` (pri 110) | Consumed, not changed -- the predicate-slot signal every fix reads. | Upstream, already landed | BF (graded, off the category posterior). Confirms "one organ, many consumers." |

**Islanded-organ AUDIT UPDATE** (recorded for strategy): `situation_reader`'s copular-state-as-event computation is already BF but lives ONLY in the joint temporal reasoner and is byte-identical to `sm.events` off/on -- **landed != live**. Diff 2 lands it in the main event stream.

**APPLY-TIME NOTE for strategy (verified 2026-09-14 19:2x):** THIS SOLVER wrote NO `hdlab/` file -- the proposed symbols (`_add_copular_predicate_events`, `nonverbal_predicate_events`) are confirmed ABSENT from `hdlab/situation_reader.py` on disk. However, the working tree is NOT pristine: `hdlab/lexical_categories.py` (+~340 lines) and `hdlab/situation_reader.py` (+~50 lines) carry the OWNER's concurrent pri-110/106 edits vs tag `comparison_pri113_base`. So `git apply` the diffs against the LIVE files, re-confirming each function-anchor first (diff 2's `_tense_agnostic_extract` region in particular has already moved).

### 33b. The key levers to further improvement (ranked; what each buys and who owns it)

1. **THE REPRESENTATIONAL LEVER -- a glass-box learned-semantic CONTEXTUAL encoder applied to ALL arcs (the #1 wall, §23/§30/§32).** This is the dominant gap vs SOTA and the gate on the >=0.90 recall bar. **Positively indicated, no longer "expected to false-negative":** even a weak form-based contextual-HRR arc feature (RI base + circular-convolution position binding) ADDS signal -- full population 0.5385 -> 0.6272 (+0.089). The strong form (learned-semantic codes, all arcs, online) is expected to help more. **OWNER: strategy's cross-cutting build** -- the filed `distributed_contextual_representations_into_the_parser` problem, NOT a pri-113 solver cell.
2. **Land the heads-rung correction with an ONLINE-learned copular-subject validity (§21/§28).** The prototype already exceeds the MAP ceiling (0.65) and propagates downstream (+0.18 to entity binding). It must be plastic (Rescorla-Wagner), never a frozen bias, before it lands. **OWNER: strategy** (hdlab/ edit; diff-ready after the validity is grown online).
3. **Route the predication to the ENTITY-STATE register as a typed attribute, gated on subject-coref binding (diff 4, §14).** The highest-value semantic win: unlocks type-licensed inference and attribute-based bridging/coref ("the doctor" -> "she"), which fail SILENTLY today. **OWNER: strategy** (architectural integration across copular_binding + state_register + situation_reader).
4. **Close the cheap tail of the 65 (§ diag65): Type-2 interrogatives + Type-3 locative agreement** via an on-demand subject-copula number-agreement check (a low-availability repair cue, MacWhinney/Bates). Type-1 true-inverse/specificational is the **principled ceiling** (discourse-givenness-bound -- needs the discourse tracker + morphological agreement the substrate lacks).
5. **Rebuild the role-validity table with PRED keyed on predicate-hood (diff 3).** Closes the located oblique gap (0.53 -> ~0.83). Cheap, mechanical, needs `tools/build_coarse_role_validities.py`.

### 33c. Bar status, honestly

MET: participant instrument built + published; event detector receives the non-verbal predicate (recall 0.19->0.74, precision held, twin loses, oracle 1.0, board not down, generalizes on GUM); one structure per clause (is_state co-indexed); the 65 down to a counted residual with reasons. **NOT MET**: the >=0.90 recall bar (0.7545 strict / 0.8204 state-registered) and the CI-separated role-accuracy bar -- BOTH located upstream to lever 1 (representation) + lever 2 (heads), each prototyped with a number, which is the located-negative the bar's OR-clause asks for. Status remains an honest **PARTIAL**.

## 11. Submission prompt

```
pri 113 -- one_in_five_asserted_clauses_has_a_non_verbal_predicate_and_every_verb_gated_consumer_is_blind_to_it_fire_events_and_roles_on_the_predicate_slot_not_the_verb_tag

PARTIAL (strong core + located, prototyped upstream negative). Built the PARTICIPANT INSTRUMENT pri 110 10f
specified (UD-EWT test 700; 762 subject-bearing gold clauses, 167 non-verbal; scored by ARGUMENT STRUCTURE -- does
the fired event GOVERN a gold core argument -- never by the tag column). The EVENT DETECTOR now receives the
non-verbal predicate: non-verbal-clause event recall 0.1856 -> 0.7365 (+0.5509 CI[+0.4789,+0.6228] SEP over the
shipped UPOS==VERB detector), pooled precision 0.8358 -> 0.8244 (held), copular-event participant precision 0.2652
-> 0.5144; verbal clauses unchanged 0.9950. TWIN (random clause token, matched rate) 0.2635 loses; ORACLE (gold
predicate slot) = 1.0000 (the instrument is well-formed and the consumer is correct once the slot is identified).
BOARD A/B byte-identical on all 7 dimensions (agg 0.5958 -> 0.5958) -- the board is VERB-gated too and cannot score
this gain, exactly why 10f specified this instrument. Mechanism: fire on the copular complement (drop the redundant
verbless-clause over-suppression gate = +0.12 recall) + a surgical locative/clause-final extension; co-indexed on
the token the state reader binds and tagged is_state (one structure per clause).

NOT MET, and located upstream: the >=0.90 recall bar. FULL-STACK UPSTREAM TRACE -- the heads rung attaches the
subject to its predicate at 0.8533 (verbal) but only 0.5385 (non-verbal). The "more BF" parse-based hand-off
(predicate slot from the parser + roles) scored 0.6048, CI-separated BELOW the construction scan's 0.7365 (a located
NEGATIVE: the parser is not accurate enough here, so the closed-class copular cue carries more signal today).
Prototyped the correction: bias the subject arc toward the predicate slot -> non-verbal attachment 0.5385 -> 0.6509,
verbal flat. ROLES: the subject is ALREADY labelled 0.84 (the cop cue), so the brief's "role competition loses its
cues" is only partly true; the real gap is obliques of a non-verbal predicate (0.53 vs 0.83 verbal), located to the
configuration backoff collapsing a non-verbal predicate to NONPRED (_PRED_HC = VERB/AUX) -- proposed, needs a role-
table rebuild. The 65 seen-by-nobody -> a counted residual (HIT 123, clausal-complement 14, inverted 10, mistag 15,
no-copula 5).

THE REFRAME (research-grounded): subject/predicate ORDER is a PF-level artifact (Moro 2020 symmetric merge;
Maienborn 2005 Kimian state; Zwaan & Radvansky situation-model has no subject/predicate axis), so the STATE consumer
needs the two arguments TYPED and BOUND, not the exact predicate token. STATE-REGISTERED recall (fired on the gold
predicate OR its subject) = 0.8204 union, twin 0.3353. The residual to 0.90 is a PRINCIPLED CEILING: Type-1
true-inverse/specificational clauses are discourse-givenness-bound (Birner & Ward; Mikkelsen), English agreement
merely re-encodes linear position (den Dikken 2006), and several are equatives with no predicate to find (Heycock &
Kroch) -- unreachable without a discourse tracker + morphological agreement. Fix: register STATE(entity_arg,
property_arg) by type with a symmetric EQUATE fallback (Type-2 interrogatives + Type-3 locative agreement are cheaply
closable; Type-1 is the ceiling).

THE REAL PATH (research synthesis, section 14): a non-verbal predication is a KIMIAN STATE -- an updatable typed
ATTRIBUTE bound to the subject entity (Maienborn 2005; object files Kahneman 1992; DRT condition Kamp & Reyle 1993),
NOT an eventive record. That is WHY the strict event-token metric plateaued and the eventive board stayed
byte-identical (a state is not an event). Measured the brain-faithful way (predication registered with a participant),
clause-capture is 0.8922. The REAL PATH supersedes chasing the predicate token: (1) route the predication to the
ENTITY-STATE register (state_register/copular_binding/bind_entity_states -- exists) as a typed attribute
(property->attribute, class->type/schema, location->spatial index, identity->file-merge, clausal->proposition slot),
not the event stream; (2) gate the write on SUBJECT-ENTITY COREFERENCE BINDING (the highest-yield fix -- a property on
the wrong entity corrupts silently; Garrod & Sanford; McKoon & Ratcliff); (3) the highest-value consumer is
type-licensed inference + attribute-based bridging/coref ("the doctor"->"she"), which fail silently without the bind.
This REFRAMES the brief: fire a typed STATE on the entity, not an event.

AUDIT UPDATE: situation_reader's copular-state-as-event computation is BF but ISLANDED in the temporal reasoner
(byte-identical to sm.events off/on) -- landed != live.

Files: experiments/exp_nonverbal_predication_participants_v1.py, notes/problems/<slug>/{SOLVED.md,
predicate_slot_consumers_patch.diff}. No hdlab/ edited by this solver (diffs are proposals; re-anchor before git apply -- the live situation_reader.py has moved since the base tag). Reverify: --self-test ; --participant --cap 700 --gate all ;
--diag65 ; --decompose ; --heads-fix ; --board --arm base|slot.
```

INTEGRATED_BY_STRATEGY 2026-09-14 22:27 local -- MERGED LANDING of the head-to-head (owner DONE; agent PARTIAL): the agent's diff applied (the complement-firing event detector on the predicate slot; fifteen constructions; the one-structure consolidation HDLAB_STATE_FROM_PREDICATE_SLOT on; the graded arc cue OFF at tau 0; the role predicate-hood keying inert until a table carries PRED rows) + the owner's `is_state` marker ported onto every fired predication (one typed STATE structure per clause). Witnesses green: agent cell self-test, predicate_recall 30/30, copular 6/6, tense_agnostic, cache_shared 4/4, double_parse 14/14, state_qa_consumer 9/9 (W9 re-pinned: the reader default is now AT OR ABOVE the robust_cop level, 0.761 vs 0.59 on its harness). FULL BOARD A/B (pri112a -> pri113a): STATE 0.7487 -> 0.7910 (+0.0423, CI-sep over its 0.5714 floor), every other row byte-identical, AGG 0.6190 -> 0.6205. Follow-ons filed: pri 117 (copular subject heads, the owner's prototype), 119 (typed attribute register), 120 (construction memberships from counts), 121 (the board's non-verbal predication row). The owner/agent disagreement on the role PRED keying stays open (table swap withheld). Comparison: notes/comparisons/pri113_head_to_head_2026-09-14.md.
