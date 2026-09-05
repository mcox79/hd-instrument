# Research — why the SPACE dimension loses recall on modern narrative, and what the brain does instead of a motion-verb lexicon (2026-09-05)

**Trigger:** solver-reported diagnosis — the location register (`situation_model_has_no_spatial_location_dimension`,
closed SOLVED 2026-08-28) shows near-lossless register/readout (~0.79 ceiling given perfect extraction,
parse-quality-independent) but only ~44% motion-event **extraction recall** on modern narrative. The prior SOLVED
build and its two research drills (`research_motion_goal_vs_addressee_...2026-08-28.md`,
`research_deictic_center_and_hierarchical_spatial_frameworks_2026-08-28.md`) were measured almost entirely on
19th-century prose (LitBank / Tom Sawyer / Holmes) — per the standing corpus-age confound
([[project_mcguffey_corpus_is_200_years_old]]) this is a genuinely new regime, not a re-verification. 2x-research
discipline: this drill goes deeper into mechanism (what triggers a location update beyond a motion verb), not a
repeat lit-scan of ground already covered (Goal-vs-Recipient PP disambiguation, hierarchical containment,
deictic-shift-theory SKIP — all still stand, unchanged).

## (a) HEADLINE

**Neither pure (a) nor pure (b) — closer to (a), with one real complication.** The extraction detector's closed
motion-verb list is provably too narrow (Levin & Rappaport Hovav manner/result complementarity; Clark & Clark
1979 denominal location verbs) and the brain does not gate location-updating on a manner-of-motion lexicon. But
"obligatory continuous updating" is also an overclaim: Therriault, Rinck & Zwaan (2006) show spatial updating is
partly **strategic/attention-dependent** (unlike protagonist tracking, which is obligatory for all readers
regardless of instruction), and McKoon & Ratcliff's (1992) minimalist hypothesis predicts non-motion locative
inference is generated **on-demand for local coherence (bridging)**, not eagerly on every clause. The accurate
mechanism is: a **persistent, protagonist/goal-anchored WHERE-state** (deictic-center-like) that is updated by
**any predicate that lexically or contextually entails a location** — motion verbs, result/telic verbs
(board/enter/arrive), stative-locative assertions (sat/stood/waited + PP), and locative-PP-bearing non-motion
clauses — with the last category resolved lazily when something downstream needs it, not by an eager omniscient
scan. P_deflated for this composite claim = **0.50** (see calibration below).

## (b) Cheap decisive test

Build a ~150-200 token stratified gold set from the **same modern-narrative corpus that produced the 44% number**
(not LitBank — the corpus-age confound must not re-enter here), stratified into 5 buckets that map 1:1 onto the
diagnosed miss classes and the mechanism candidates below:

1. **Manner-motion** (go/come/walk/run + particle) — the existing gate's home turf; expected near-ceiling already.
2. **Result/telic motion verbs** (board, enter, exit, arrive, disembark, check into) — lexicon-coverage gap.
3. **Caused-motion** (wheeled, carried, pushed, dragged — theme moves, not agent) — existing argument-structure
   gate's coverage/routing gap.
4. **Stative-locative** (sat by / stood at / waited on / stayed there / was in) — a gate that does not exist yet.
5. **Locative-PP-bearing non-motion clause** (found a desk **on the third floor**; the location rides on the
   object's own modifier, not the verb) — a bridging-inference gap.

Score the *current* detector's recall per bucket first (diagnostic — confirms which buckets are driving the 44%
floor; hypothesis: bucket 1 near-ceiling, buckets 4–5 near zero, buckets 2–3 partial). Then add mechanisms A–D
(section (e) below) incrementally and re-score per bucket, holding bucket-1 precision (already measured 0.909 in
the SOLVED build) as a **must-not-regress** guardrail.

## (c) Falsifiable predictions

**HARD-PASS:** adding a stative-locative gate (A) + result-verb lexicon widening (B) alone lifts *overall* recall
from ~44% to **>=75%** on the modern-narrative gold set, CI-separated over the current detector, with bucket-4
(stative) recall **>=85%** and bucket-2 (result-verb) recall **>=85%**, while bucket-1 (manner-motion) precision
stays **>=0.85** (no more than a ~5-point regression from the existing 0.909).

**MIDDLE_BAND:** overall recall improves but plateaus at **55-70%** — buckets 2/3/4 improve but bucket-5
(non-motion bridging inference) stays low (<40%). Correct read: the on-demand bridging extractor (D) is a real,
separate, additional mechanism to build — not a sign the approach is wrong, and not something to scope out
(unlike the SOLVED build's genuinely-rare conveyance gap at 0.01% of text, buckets 4-5 are not measured-rare here
— the user's own diagnosed misses are drawn from ordinary modern prose).

**HARD-FAIL:** overall recall stays **<55%** after A+B, OR bucket-1 precision drops **>10 points** (the new gates
fire promiscuously and break the existing precision win — would indicate the stative/result gates need the
ATL place-typing reuse tightened, not that the mechanism claim itself is wrong), OR the per-bucket diagnostic
in step 1 shows bucket-1 (manner-motion) itself recalling **<80%** on modern prose (would mean the more basic
problem is coordination/clause-segmentation dropping motion events wholesale — report before touching buckets
2-5, this exactly matches diagnosed miss #2, "two changes in one sentence, only one caught").

## (d) Cross-thread synthesis (4 parallel Sonnet lit-scans, this cycle)

**Thread 1 — event-indexing / continuous updating.** Zwaan & Radvansky (1998, *Psych Bull* 123:162-185) frame
SPACE as one of 5 monitored dimensions; exact wording on trigger-conditions unverifiable from source PDF
(confidence 0.4). Zwaan, Langston & Graesser (1995, *Psych Science* 6:292-297) found a weak/unreliable
spatial-discontinuity reading-time effect — historically read as "space is the weakest dimension." **Rinck &
Weber (2003, *Mem Cogn* 31:1284-1292)** is the load-bearing disambiguation: Exp 1 replicates the weak effect,
but Exp 2 — readers who first memorized a map of the story layout — get a *reliable* spatial-discontinuity
effect. This reframes "space is weak" from *readers don't update location* to *readers under-update only when
they lack a rich-enough spatial-layout representation to notice the violation* — a measurement artifact of the
reading-time paradigm, not evidence against broad updating. Zwaan, Radvansky, Hilliard & Curiel (1998) replicate
the same map-dependency. Countervailing: **Therriault, Rinck & Zwaan (2006, *Mem Cogn* 34:78-89)** found spatial
updating occurred only in readers *instructed* to attend to the spatial dimension, while protagonist-tracking
occurred in all readers regardless of instruction — real evidence spatial updating is **more strategic/
attention-gated** than protagonist tracking, a genuine asymmetry, not a uniform "obligatory continuous" story.
Rapp, Klug & Taylor (2006) found readers' *expectations* about movement (predictive, not just verb-triggered)
shape spatial accessibility — supports an inferential component. (Confidences 0.4-0.65 per source; none above 0.7.)

**Thread 2 — inference from non-motion events + world knowledge.** The strongest converging finding: **Levin &
Rappaport Hovav (manner/result complementarity) + Clark & Clark (1979, *Language* 55:767-811)** show, as a
linguistic-theoretic fact (confidence 0.8), that RESULT/telic verbs (arrive, enter, board) and denominal location
verbs (bottle, shelve, kennel) lexicalize a location-change/location-assertion result state with **zero
manner-of-motion morphology** — i.e., "board" not being in a manner-verb list is not a world-knowledge inference
gap at all, it's a **lexicon-coverage gap** against an independently well-defined, closed VerbNet-style class.
No direct online reading-time study was found timing this specific update (confidence drops to 0.2 for the
*online-processing* claim specifically — flagged, not invented). Bower, Black & Turner (1979, *Cog Psych*
11:177-220) confirms scripts supply unstated sub-events generally, but was not tested for location specifically
(0.35). **McKoon & Ratcliff (1992, *Psych Rev* 99:440-466)** minimalist hypothesis is the key calibration: only
(i) trivially-available and (ii) locally-needed bridging inferences are automatic; a locative inference from
"found a desk on the third floor" should be generated **when the next clause needs it**, not unconditionally —
this argues for a **lazy/on-demand** extraction design, not an eager one, and matches this substrate's own prior
design principle (SPACE as a lazily-populated dimension, Zwaan Langston Graesser 1995). Morrow/Greenspan/Bower
(1987, 1989) + Curiel & Radvansky (2014) cluster: goal/final-location sentences *without* an explicit motion verb
reproduce the same accessibility-by-distance gradient as sentences with one — the closest direct empirical
support found for "endpoint/result-state alone updates location" (confidence 0.55, flagged for primary-source
re-check on which exact paper carries this specific comparison).

**Thread 3 — deictic center / stative location / protagonist-anchoring.** Duchan, Bruder & Hewitt (eds. 1995,
*Deixis in Narrative*) — correction: Duchan/Bruder/Hewitt are the editors, Segal is a contributing chapter author,
not co-editor as originally framed — propose the Deictic Center (WHO/WHEN/WHERE) as a general locus the reader
projects into; **primary text could not be retrieved** (WebFetch failures both times), so the specific claim
about stative-vs-motion licensing conditions is **unverified, confidence 0.4, theoretically plausible only**.
Rapaport et al.'s SNePS/Cassie computational DC model (SUNY Buffalo TR 89-01) — same caveat. **A genuinely useful
negative result:** no study was found that directly pits a stative-locative sentence ("he sat by the window")
against a motion sentence ("he walked to the window") as competing location-update triggers — this exact
comparison appears to be an open gap in the literature, not a settled "no". Morrow, Bower & Greenspan (1989)
"one-place-one-perspective" rule and Wilson, Rinck, Hess, Bower & Morrow (*JML* 32:141-154) both independently
confirm spatial situation models are organized around **the protagonist specifically** (protagonist-probes
needed; object-only probes insufficient) — location tracking is not uniform-per-character, it is
protagonist/goal-anchored, consistent with the SOLVED build's existing design (no separate deictic-shift
apparatus needed, already correctly SKIPPED).

**Thread 4 — neural basis.** Honest calibration: **suggestive, not decisive.** Hassabis & Maguire (2007)
hippocampal scene-construction theory is a general framework never tested on reading itself (0.3). Zacks &
Tversky (2001) Event Segmentation Theory treats location change as **one of several co-equal** boundary features
(goal change, new person, causal break) — not uniquely dominant (0.35). The one directly relevant data point:
**Speer, Reynolds, Swallow & Zacks (2009, *Psych Science* 20:989-999)** coded narratives for 6 situational
dimensions and found spatial changes specifically drove increased BOLD in **parahippocampal cortex** (a
place-processing region) and FEF during silent story reading — a real bridge from narrative-space-tracking to
physical-navigation-adjacent cortex (confidence 0.70, the strongest single neural citation) — but their spatial
events were narratively confounded with motion/travel language, so it does **not** cleanly separate "any
location-entailing event" from "motion verb" as the trigger. Constantinescu, O'Reilly & Behrens (2016, *Science*)
grid-code-for-conceptual-space is real domain-generality evidence for the hippocampal-entorhinal machinery, but
several inferential steps removed from narrative reading. Robin, Buchsbaum & Moscovitch (2018) location-primacy
finding is actively contested (a competing "stimulus reliability, not spatial content" account exists in the
same literature). **Net: the neural thread corroborates the behavioral picture but adds no independent decisive
weight — treat as supporting color, not load-bearing evidence.**

## (e) Substrate-product implications (mechanism widening, ranked by the diagnosed misses)

1. **[NEW gate, highest expected recall gain] Stative-locative gate** — {sit/stand/lie/wait/remain/stay/be} +
   locative PP asserts a location with zero motion morphology. Directly fixes diagnosed misses "he sat by the
   window" and "waited on the platform." Grounded in Thread 3 (deictic-center WHERE as a general locus) +
   Thread 1 (protagonist-anchored persistent state) — reuse the existing ATL place-typing gate (already built,
   0.219->0.909 precision lift on Goal PPs) so the new gate inherits the same false-positive protection rather
   than being a fresh, untyped rule.
2. **[Lexicon widening, cheap] Extend the manner-verb list to RESULT/telic verbs** (board, enter, exit, arrive,
   disembark, check into, settle into) per Levin & Rappaport Hovav's independently-defined, closed verb class —
   this is not open-ended world-knowledge inference, it's adding a second enumerable VerbNet-style class to an
   existing gate. Fixes "board the plane" directly, including the embedded-clause case ("watched him board the
   plane" — flag separately as a parsing-scope issue: embedded-clause subjects need the same motion-frame check
   as matrix-clause subjects, independent of the lexicon fix).
3. **[Audit existing gate, likely bug not new mechanism] Caused-motion routing** — "wheeled him down to
   radiology" should already be handled by the SOLVED build's argument-structure gate (goal PP + competing
   moved-theme direct object -> object's path, not agent's). The reported suppression is more likely a verb-
   lexicon coverage gap (wheel/carry/push/pull/convey classes not in the caused-motion list feeding that gate)
   than a missing mechanism — check the gate's verb-class enumeration before building anything new.
4. **[NEW, lazy/on-demand] Locative-PP bridging extractor, decoupled from verb class** — "found a desk on the
   third floor": the location rides on the object's own PP modifier, not the verb. Per McKoon & Ratcliff's
   minimalist hypothesis (Thread 2), implement this as a lazy, on-demand bridging pass — fire only when an
   entity's location is *queried downstream* and no explicit update exists in the current window — rather than
   an eager per-clause scan. This matches the already-adopted "SPACE is lazily-populated" design principle from
   the prior research drill and the brain's own inference economy; an eager version would over-generate false
   locations from every incidentally-mentioned locative NP.
5. **[Architecture, not new mechanism] Per-clause/per-conjunct looping for coordination** — "took the stairs to
   the subway and waited on the platform" is two separate location-updating events in one sentence; if the
   current detector fires once per sentence rather than once per predicate/conjunct, mechanisms 1-4 above will
   still only catch the first event. Verify this before crediting any per-bucket recall gain to a gate fix.
6. **[Do not build] A separate deictic-shift-theory apparatus** — already correctly SKIPPED in the prior drill
   (P=0.22; Zwaan/Magliano/Graesser 1995, Rinck & Weber 2003 — spatial-alone discontinuity doesn't reliably cost
   reading time on its own, and the protagonist-anchored absolute-tracking design already in place is the
   better engineering choice). Nothing in this drill overturns that call.
7. **[Calibration note for the register itself]** Rinck & Weber (2003) / Zwaan-Radvansky-Hilliard-Curiel (1998)'s
   map-dependency finding is indirectly reassuring for the existing design: the register already uses a
   topological scene-node + region hierarchy (not raw text positions), which is exactly the kind of persistent
   spatial-layout representation those studies show is necessary for reliable spatial tracking to be *legible*
   at all — the tracking substrate is right; the gap is entirely in the extraction front-end (gates 1-5 above).

## (f) Citations (verified count = 24)

Thread 1: Zwaan & Radvansky 1998 (*Psych Bull* 123:162-185); Zwaan, Langston & Graesser 1995 (*Psych Sci*
6:292-297); Zwaan, Magliano & Graesser 1995 (*JEP:LMC* 21:386-397); Rinck & Weber 2003 (*Mem Cogn* 31:1284-1292);
Rinck & Bower 1995 (*JML* 34:110-131); Rinck & Bower 2000 (*Mem Cogn* 28:1310-1320); Rinck, Hähnel, Bower &
Glowalla 1997 (*JEP:LMC* 23:622-637); Therriault, Rinck & Zwaan 2006 (*Mem Cogn* 34:78-89); Levine & Klin 2001
(*Mem Cogn* 29:327-335); Rapp, Klug & Taylor 2006 (*Mem Cogn* 34).

Thread 2: Glenberg, Meyer & Lindem 1987 (*JML* 26:69-83); Bower, Black & Turner 1979 (*Cog Psych* 11:177-220);
McKoon & Ratcliff 1992 (*Psych Rev* 99:440-466); Levin & Rappaport Hovav (manner/result complementarity, in
*Lexical Semantics, Syntax, and Event Structure*, 2010); Clark & Clark 1979 (*Language* 55:767-811); Morrow,
Greenspan & Bower 1987 (*JML* 26:165-187); Morrow, Bower & Greenspan 1989 (*JML* 28:292-312); Curiel & Radvansky
2014 (*J Cognitive Psychology* 26:205-212).

Thread 3: Duchan, Bruder & Hewitt (eds.) 1995, *Deixis in Narrative* (primary text unverified — flagged);
Rapaport et al., SUNY Buffalo TR 89-01 (primary text unverified — flagged); Wilson, Rinck, Hess, Bower & Morrow
(*JML* 32:141-154); Zwaan, Radvansky, Hilliard & Curiel 1998 (*Mem Cogn*).

Thread 4: Hassabis & Maguire 2007 (*TICS* 11:299-306); Zacks & Tversky 2001 (*Psych Bull* 127:3-21); Zacks,
Speer, Swallow, Braver & Reynolds 2007 (*Psych Bull* 133:273-293); Speer, Zacks & Reynolds 2007 (*Psych Sci*);
Speer, Reynolds, Swallow & Zacks 2009 (*Psych Sci* 20:989-999); Baldassano, Chen, Zadbood, Pillow, Hasson &
Norman 2017 (*Neuron* 95:709-721); Robin, Buchsbaum & Moscovitch 2018 (*J Neurosci* 38:2755-2765);
Constantinescu, O'Reilly & Behrens 2016 (*Science* 352:1464-1468); Behrens et al. 2018 (*Neuron*) /
Whittington et al. 2020 (*Cell*, Tolman-Eichenbaum Machine — corrects a commonly-misdated "2018/Neuron" citation).

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):** raw synthesis estimate for the composite
bottom-line claim ("broad, entailment-driven, protagonist-anchored, lazily-resolved" over "motion-verb lexicon
lookup") ~0.70; deflated by 0.20 for uncharted-regime + two unverifiable primary sources (Thread 3) +
one direct behavioral complication (Therriault 2006) not fully reconciled -> **P_deflated = 0.50** (at the
novel-synthesis cap). Confidence is substantially higher (0.75-0.80) on the narrower, purely linguistic-theoretic
sub-claim that result/telic verbs and stative locatives are legitimately location-entailing independent of any
motion-verb lexicon — that sub-claim rests on closed-class linguistic theory (Levin & Rappaport Hovav, Clark &
Clark), not contested psycholinguistic timing data.

## TLDR

The story-reading brain does not keep a fixed list of "moving" words and only update someone's location when one
appears. It keeps a running, character-centered sense of "where they are," and updates it from anything that
plainly implies a place — arriving, boarding, sitting somewhere, or even just discovering something at a place —
not only walking/running/going. But it isn't purely automatic either: people are shown to track a location more
reliably once they have a decent mental map of the setting, and the "where" update for a side detail can wait
until the story actually needs it, rather than firing on every sentence. The fix for the current tool is mostly
cheap: recognize a few more well-defined verb types (arrive/board/enter), add a rule for "sitting/standing/
waiting somewhere" (currently missing entirely), and make sure a sentence with two events updates location twice,
not once. One case flagged by the diagnosis (the wheelchair example) is probably a plain bug in an existing rule,
not a missing brain mechanism.

## QUESTIONS

None.

## NEXT STEPS

1. Run the 5-bucket diagnostic (section b) on the same modern-narrative sample that produced the 44% number to
   confirm which bucket(s) are driving the miss before building anything.
2. Ship gates 1-2 (stative-locative + result-verb lexicon widening, section e) first — cheapest, most directly
   evidenced, and reuses the existing ATL place-typing/argument-structure machinery rather than adding new
   untyped rules.
3. Audit the caused-motion argument-routing gate's verb-class list (gate 3) before assuming a new mechanism is
   needed for "wheeled him down to radiology."
4. Only after 1-3, build the lazy locative-PP bridging extractor (gate 4) if bucket-5 recall is still low — this
   is the one genuinely new, more expensive mechanism, and per McKoon & Ratcliff should be implemented as
   on-demand, not eager.
