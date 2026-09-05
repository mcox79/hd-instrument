---
problem: a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround
status: REFUTED
bar: "PASS = a glass-box force-dynamic / situation-model plausibility causal scorer (Talmy/Wolff force dynamics; implicit-causality verb-class + a normality/compatibility scorer; participant-overlap DROPPED as falsified) that picks the connective cause CI-separated over BOTH the current adjacency/connective heuristic AND the scoped floor, with a shuffled-plausibility info-free twin LOSING and no-regress on the other dimensions — and the `predicate_recall` scoping workaround retired. A coarse VerbNet/FrameNet + argument-compatibility first cut is admissible (full fidelity via the meaning hub). Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — a glass-box force-dynamic causal scorer cannot beat the connective heuristic within the invariant (with the named cause + number) — is a FULL PASS. Strategy lands the Q111 wire; fold a §2b AUDIT UPDATE."
result: "LOCATED NEGATIVE (= the FULL PASS the bar names). A glass-box force-dynamic + agentivity plausibility SELECTOR does NOT beat the connective heuristic — it is CI-separated WORSE at base density: off_plaus 0.6931 vs off_pos 0.9010, d=-0.2079 CI[-0.2970,-0.1268] (n=101 causal QA, 16 LitBank docs). The scoped floor CANNOT be beaten because it IS the gold's own rule: build_causal_questions defines gold = post[0]/pre[-1] (the event ADJACENT to the connective), and agree(gold, positional-pick-on-OFF)=0.9010 == the OFF QA score EXACTLY (all 10 misses are ordering/multi-connective artifacts, 0 plausibility-recoverable). Named cause (3 independent, measured): (1) connective cause-selection is STRUCTURAL (the connective marks the cause clause), not plausibility — so a plausibility scorer moves off the gold and loses; (2) the QA instrument's gold is that same positional rule (circular — confirmed: perfect-parse oracle 0.7624 and oracle-participants 0.8218 both score WORSE than positional 0.8317, not better); (3) even where plausibility DOES belong (bridging), the force lexicon covers only 3/16 real narrative cause verbs — 11/16 are MENTAL/SOCIAL causation (ToM), which force dynamics structurally cannot represent. CONSTRUCTIVE POSITIVE (the landed causal-chain cell's named-but-unbuilt next lever): on NON-ADJACENT physical bridges a force-dynamic plausibility selector (FORCE_BRIDGE) beats MOST_RECENT (locality) AND CONNECTIVE_ONLY (abstains) by +1.000 CI[+1.000,+1.000] (n=8), stays density-robust (1.000 adjacent AND non-adjacent vs MOST_RECENT collapsing 0.750->0.000), and beats the shuffled-plausibility null (FORCE_BRIDGE 1.000 > twin p95 0.750, twin mean 0.459) — plausibility selection works exactly where the brain uses it (unstated links across dead-ends), not for connective selection."
floor: "The scoped floor (positional-on-sparse causal QA) = 0.8911 landed (reproduced 0.9010, within 1/101; the dense blanket regression reproduced EXACTLY at 0.8317), n=101 causal QA over 16 LitBank docs — and it is the CEILING: every non-positional selector scores AT or BELOW it (dense-positional 0.8317, force+agentivity plausibility 0.6931, perfect-parse oracle 0.7624, oracle-participants 0.8218, prior semantic _compat 40-doc 0.7972). For the constructive positive the floors are MOST_RECENT (locality) 0.000 and CONNECTIVE_ONLY 0.000 on non-adjacent physical bridges (n=8)."
controls: "(1) SHUFFLED-PLAUSIBILITY TWIN (the bar's info-free control): bridge FORCE_BRIDGE 1.000 > twin p95 0.750 (twin mean 0.459 over 1000 per-item force-label permutations) -> the win rides the force signal, not position; on the QA the twin is WORSE than plaus (off_twin 0.6436 < off_plaus 0.6931) -> plaus carries some signal but in the WRONG direction for connective selection. (2) ORACLE ISOLATION (excludes 'upstream parse/participants is the cause'): a PERFECT spaCy parse structural pick 0.7624 and oracle spaCy participants 0.8218 BOTH score worse than positional 0.8317 -> the failure is not our parse/roles, it is that the gold rewards adjacency (disk, exp_event_detection_causal_oracle_v1). (3) DENSITY CONTROL (excludes 'plausibility is a density-robust connective fix'): under predicate_recall positional drops 0.8911->0.8317 and plausibility drops FURTHER to 0.6535 (worse than the naive dense heuristic by -0.1782 CI-sep). (4) COVERAGE BOUND (excludes 'a bigger lexicon fixes it'): force lexicon covers 3/16 real cause verbs; 11/16 mental/social. (5) CIRCULARITY CONTROL: agree(gold, positional-on-OFF)=0.9010 == the OFF QA score exactly -> the gold IS the mechanism. (6) DENSITY-ROBUSTNESS / no-regression: FORCE_BRIDGE non-adjacent == adjacent (1.000) -> the mechanism does not regress when the true cause is displaced."
files_changed: "experiments/exp_causal_selection_instrument_diagnostic_v1.py (circularity + selectors at OFF/DENSE density, faithful reproduction of the landed scoped/blanket numbers), experiments/exp_causal_bridge_plausibility_beats_locality_v1.py (the non-adjacent physical-bridge dissociation — the constructive positive), verification/test_causal_selection_plausibility_and_scoping.py (scaffold-free witness, 7/7). NO hdlab/ changed — the recommendation is to KEEP scoping for the connective path and file a NEW bridging/ToM problem (see PROPOSED, below); strategy owns any hdlab change (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_causal_selection_plausibility_and_scoping.py"
---

# REFUTED — the scoping workaround is NOT interim debt to retire; it is the correct treatment for the connective path, and a force-dynamic plausibility SELECTOR is the wrong mechanism for connective cause-selection

**Status: REFUTED (WIP until `owner_verdict: DONE`).** This is the FULL PASS the bar explicitly names ("a rigorous
located NEGATIVE ... is a FULL PASS"). No `hdlab/` file changed — the mechanism is proven in `experiments/` +
`verification/`; the recommendation and the proposed follow-on problem are below; strategy lands anything (Q111).
Glass-box, NO external LLM. **THE DISK OUTRANKS THE BRIEF, and here it corrected the brief's premise in three
independent, measured ways — and then showed the one place the proposed mechanism genuinely works.**

## 0. The opening move — how does the BRAIN select the cause, and does our subtask even need plausibility?
The brief assumes ONE mechanism (force-dynamic plausibility) for cause-SELECTION. The reading-science literature it
cites is about a DIFFERENT thing than our failing subtask. Causal cause-selection is really **two subtasks with two
brain mechanisms**:
- **CONNECTIVE-MARKED selection** ("X because Y", "X so Y"): the connective is an explicit discourse-syntactic marker
  that BINDS the cause clause. The reader follows the connective to its clausal argument — a STRUCTURAL operation
  (discourse parsing), NOT a plausibility competition. Koornneef & Van Berkum / Sanders & Noordman show plausibility
  matters when the structure is AMBIGUOUS or ABSENT — they do not say plausibility overrides an explicit connective.
- **BRIDGING** (unstated links, no connective — "He dropped the glass. It shattered."): here there is no structural
  marker, so the reader MUST infer the cause by plausibility — Talmy/Wolff force dynamics for PHYSICAL causation, and
  mentalizing/ToM (mPFC/TPJ; Wolff & Barbey 2015) for MENTAL/INTENTIONAL/SOCIAL causation.

The density regression the brief wants to fix lives in the **connective** path. So the brief applies the **bridging**
mechanism (plausibility) to the **connective** subtask — a category error. The disk confirms it below.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a story says "B because A", the reader has to pick which earlier event A is the cause. The old worry was that
our reader just grabs the nearest event, and that this breaks when it notices more events. The brief asked me to
replace "grab the nearest" with a "does this cause plausibly produce this effect" scorer. I built that scorer (the
brain's force-dynamics), and it made connective questions **much worse**, not better — because for "because"/"so"
sentences the grammar word itself points at the cause clause, so "nearest to the connective" is essentially the
right answer, and picking the most physically-forceful verb instead pulls you off it. I also found the scoreboard
we grade on was *built* by the "nearest" rule, so nothing that departs from "nearest" can ever win on it. AND I
found the deeper reason a physical-force scorer can't carry narrative causation: most story causation is mental
("she frowned because she remembered"), which force dynamics can't touch at all. So the stop-gap is not a hack to
retire — it is the right call for these sentences. The genuinely useful place for the plausibility scorer is the
*other* case (no grammar word, an unstated cause an event or two back), and there I show it clearly beats "grab the
nearest."

## 2. WHAT I MEASURED — the located negative, three independent reasons (all reproduced first-hand)
`exp_causal_selection_instrument_diagnostic_v1` (16 LitBank docs, n=101 causal QA; a cached-events reimplementation
of `_read_causation` + `_answer_causal` that reproduces the landed numbers as a correctness gate):

| arm | acc | vs positional(OFF) |
|---|---|---|
| **off_pos** (positional/sparse = the scoped floor) | **0.9010** | 0.0 (landed scoped 0.8911; within 1/101) |
| off_plaus (force+agentivity plausibility) | 0.6931 | **-0.2079 CI[-0.2970,-0.1268] SEP** |
| off_twin (shuffled plausibility) | 0.6436 | -0.2574 SEP |
| **dense_pos** (positional/dense = current heuristic if unscoped) | **0.8317** | -0.0693 SEP (== landed blanket EXACTLY) |
| dense_plaus | 0.6535 | -0.2475 SEP |
| dense_twin | 0.5842 | -0.3168 SEP |

- **(1) Connective selection is STRUCTURAL, not plausibility.** A faithful force-dynamic + agentivity plausibility
  selector is **CI-separated WORSE** than the positional connective rule at BASE density (-0.2079). It is worse
  still on the dense set, and worse than even the naive dense heuristic (dense_plaus vs dense_pos = -0.1782 CI-sep).
  The prior force+participant scorer regressed the same way (disk: `exp_event_detection_semantic_causal_v1`, 40 docs,
  SEMANTIC 0.7972 vs blanket 0.8252 vs OFF 0.9441 — semantic is worse than blanket).
- **(2) The evaluation instrument's gold IS the positional rule (circular).** `build_causal_questions` sets
  gold = `post[0]`/`pre[-1]` (the event adjacent to the connective); `connective_cause` picks `after[0]`/`before[-1]`
  (also adjacent). Measured: agree(gold, positional-pick-on-OFF) = **0.9010 == the OFF QA score exactly**; all 10
  misses are ordering / multi-connective artifacts (0 plausibility-recoverable). So the scoped floor is unbeatable —
  it replays the gold's own rule on the gold's own events. The smoking gun is on disk already
  (`exp_event_detection_causal_oracle_v1`): a **PERFECT spaCy parse** structural pick scores 0.7624 and **oracle
  spaCy participants** score 0.8218 — BOTH *worse* than positional 0.8317. If the metric rewarded causal plausibility,
  a perfect parse and correct participants would help; they hurt, because the metric rewards connective-adjacency.
- **(3) Even in its proper home (bridging), force dynamics covers a minority of narrative causation.** Landed
  `exp_causal_network_realtext_v1`: on 16 verbatim LitBank cross-event causal edges the force lexicon classes only
  **3/16** cause verbs; **11/16 are MENTAL/SOCIAL** (remember/die/promise/say/know/feel) — a different brain system
  (mentalizing/ToM, Wolff & Barbey 2015). A bigger lexicon cannot fix a representational mismatch.

**The refutation is MECHANISM-AGNOSTIC — it covers the brief's un-built normality/implicit-causality variants too.**
I built force-class + agentivity (and the prior work built force-class + participant-overlap). I did NOT separately
build the brief's "normality/compatibility" or "implicit-causality verb-class" terms — because I do not need to: the
**perfect-parse spaCy oracle (0.7624) and the oracle-participant arm (0.8218) both score WORSE than positional
(0.8317)** on this instrument. Those oracles are an UPPER BOUND on any glass-box structural or participant/plausibility
signal (a normality or IC scorer is strictly weaker than perfect participants + perfect parse). Since even the perfect
signal loses, no plausibility scorer of any kind — force, normality, IC, or their combination — can beat positional on
the causal QA. The circularity (agree(gold, positional)=the QA score) is the reason, and it is independent of which
plausibility signal you pick.

**Scoping is therefore the CEILING, not interim debt.** `off_pos` 0.9010 is the maximum any arm reaches; scoping
(`exp_event_detection_causal_scope_v1`: scoped == OFF byte-identical) achieves it while keeping the dense who-did-what
events. The faithful structural alternative is a located negative (the OOD parse can't ID the clausal head:
`exp_event_detection_structural_causal_v1`, -0.079 to -0.317), and plausibility is worse still. **The brief's premise
— "scoping is an interim workaround to retire [with a plausibility selector]" — is refuted: retiring it via
plausibility makes causal WORSE.**

## 3. THE CONSTRUCTIVE POSITIVE — where plausibility selection DOES beat locality (the named next lever)
Refuting the brief is the halfway point. The landed `exp_read_causal_chain_on_chain_cause_v1` (HARD_PASS, real
non-circular gold) itself names the unbuilt lever: its BRIDGE items have the force-cause coinciding with the
most-recent event (MOST_RECENT=1.0 on bridge), so they do NOT dissociate plausibility from locality — "a NON-adjacent
implicit-cause bridge test is the named NEXT lever, not claimed solved." I built it
(`exp_causal_bridge_plausibility_beats_locality_v1`): 8 physical force->result bridges (no connective), with a
DEAD-END intransitive non-force event injected between cause and outcome (a controlled psycholinguistics-style
dissociation, labelled as such — not a naturalistic benchmark):

| condition | MOST_RECENT | CONNECTIVE_ONLY | **FORCE_BRIDGE** | twin (mean / p95) |
|---|---|---|---|---|
| ADJACENT (control) | 0.750 | 0.000 | **1.000** | 0.875 / — |
| NON-ADJACENT (+1 dead-end) | **0.000** | 0.000 | **1.000** | 0.459 / 0.750 |
| NON-ADJACENT (+2 dead-ends) | 0.000 | 0.000 | 0.875 | 0.311 / — |

- FORCE_BRIDGE beats MOST_RECENT and CONNECTIVE_ONLY by **+1.000 CI[+1.000,+1.000]** on the non-adjacent items.
- It is **density-robust** (1.000 adjacent AND non-adjacent) exactly where locality collapses (0.750 -> 0.000).
- It beats the **shuffled-plausibility null** (1.000 > twin p95 0.750; twin mean 0.459) — the win is the force
  signal, not position.
So plausibility selection is real and buildable — but its domain is **bridging** (unstated links across dead-ends),
not connective selection. This is the correct re-scoping of the brief's mechanism.

## 4. PERFORMANCE vs the brain + the exact mechanism-diff
A competent reader (a) follows an explicit connective to the cause clause (structural), (b) bridges unstated PHYSICAL
links by force dynamics, and (c) bridges unstated MENTAL/INTENTIONAL links by mentalizing (ToM). Our reader does (a)
via the connective/adjacency rule (correct for the subtask; scoping keeps it clean under density), can do (b) on the
physical slice (demonstrated here; the landed CAUSAL_NET already HARD_PASSes the bridge cases where cause==recent),
and does NOT do (c) at all — the 69% mental/social majority of narrative causation. **The signal we lose is not
"plausibility for connective causes" (that is not a real capability — the connective already carries it); it is
INTENTIONAL-causation bridging, which needs a ToM organ, a different brain system from force dynamics.**

## 5. PROPOSED (strategy owns hdlab, Q111) — and it is mostly "do NOT change, and file the right successor"
1. **KEEP the scoping in `situation_reader._read_causation`.** It is the connective-path optimum, not interim debt.
   Do NOT replace the connective selection with a force-dynamic plausibility scorer — measured -0.21 CI-sep at base
   density. (If anything is added, add a WELL-FORMEDNESS gate on recovered candidates — graded predicate belief, the
   joint-decoder theme — but on THIS instrument it can only tie scoping, so it is not worth landing until a
   non-circular instrument exists.)
2. **FILE A NEW PROBLEM: a mental/intentional-causation (ToM) bridging organ.** This is the real lever for narrative
   causal comprehension (69% of the edges), and it is a DIFFERENT brain system (mPFC/TPJ) from the SOLVED
   force-dynamic typer. The force-dynamic BRIDGING selector demonstrated here handles the physical slice and is a
   small additive win worth wiring IF a bridging readout is built (note: `_read_causation` currently fires ONLY on
   connective sentences, so bridging links are not built at all today; adding them is additive but feeds the goal
   graph — see §7 — so it needs a goal no-regress check at landing).
3. **AUDIT UPDATE (§2b) — correct the prior note.** The event-detection SOLVED §2b said the density-brittle connective
   selection's "faithful fix = force-dynamic attribution." That is WRONG for the connective subtask: force-dynamic
   attribution is the fix for BRIDGING, not connective selection (which is structural). Scoping is the correct
   connective-path treatment; force dynamics belongs to bridging and covers only the physical slice.

## 6. CONTROLS — what each EXCLUDED (a control that excludes nothing is not one)
- **Shuffled-plausibility twin** (the bar's info-free control): bridge FORCE_BRIDGE 1.000 > twin p95 0.750 -> the win
  is the force signal. On the QA, off_twin 0.6436 < off_plaus 0.6931 -> plausibility carries signal, but it points
  AWAY from the adjacency gold (confirms the mechanism-mismatch, not noise).
- **Oracle isolation** (excludes "our parse/participants are the cause"): perfect-parse structural 0.7624 and oracle
  participants 0.8218 BOTH < positional 0.8317 — the failure is the metric, not our upstream.
- **Density control** (excludes "plausibility is a density-robust connective fix"): plausibility drops FURTHER than
  positional under recall (dense_plaus 0.6535 vs dense_pos 0.8317).
- **Coverage bound** (excludes "a bigger lexicon fixes it"): 3/16 real cause verbs classed; 11/16 mental.
- **Circularity control** (excludes "there is plausibility headroom in the misses"): agree(gold, positional)=off QA
  score exactly; all misses are ordering artifacts.
- **Density-robustness / no-regression**: FORCE_BRIDGE non-adjacent == adjacent (1.000) — the mechanism holds when
  the true cause is displaced.

## 7. ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization potential — seeds the next problems)
- **`_read_causation` is connective-only.** It fires only on sentences containing `_CAUSAL_CONNECTIVES`, so UNSTATED
  (bridging) causal links — the majority of real causation — are never built. FIDELITY: partial (the connective path
  is faithful; the bridging path is absent). OPTIMIZATION: add a bridging readout (physical via force dynamics =
  demonstrated here; mental via a ToM organ = the big lever). This is the highest-yield causal follow-on.
- **The reader's causal event stream is ROLE-FREE.** `_read_causation`/`_extract_events` emit `T.Event`
  (lemma/idx/tense only) — no agent/patient; roles live in `sm.events` (EventRecord) and must be joined by
  (sent_idx, surface). This is WHY the prior semantic scorer's participant-overlap term never fired on the reader's
  own events (it silently degenerated). FIDELITY: a deviation (the brain queries one participant-bound eventuality
  inventory; ours splits roles from the causal stream). OPTIMIZATION: the filed unified sort-typed eventuality
  inventory would give the causal organ roles directly.
- **`sm.causal_links` feeds the GOAL graph** (`_build_goal_graph(..., causal_links=...)`). So ANY change to causal
  selection is NOT causal-only — it can move the goal dimension. LANDING NOTE: keeping scoping (recommended) keeps
  causal_links byte-identical to today, so goals are unaffected; adding bridging links would need a goal no-regress
  check.
- **The force-dynamic TYPER is SOLVED and landed** (CAUSE/ENABLE/PREVENT). It TYPES an edge; it does not SELECT
  which event is the cause. My work confirms these are cleanly separable (SELECTION = structural for connectives /
  plausibility for bridging; TYPING = force dynamics). No overlap/conflict with the concurrent typing work.

## KEY REALIZATIONS (the enabling moves)
- **The gold IS the mechanism.** Reading `build_causal_questions` line-by-line against `connective_cause` showed
  gold = post[0]/pre[-1] and the mechanism = after[0]/before[-1] — the same positional rule. Measuring
  agree(gold, positional)=0.9010 == the OFF QA score turned "the scorer regresses" into "the scorer CANNOT win — the
  instrument grades the rule I was told to replace." A metric built from a rule cannot reward departing from it.
- **The oracle rows on disk were the tell.** A PERFECT parse and CORRECT participants scoring WORSE than positional
  is only explicable if the metric rewards adjacency, not plausibility. That one fact reframed the whole problem
  before I wrote a line of scorer.
- **Two subtasks, two brain systems.** Splitting cause-SELECTION into connective (structural) vs bridging
  (plausibility), and bridging into physical (force dynamics) vs mental (ToM), dissolved the paradox: the brief's
  mechanism is right for a subtask that is NOT the one that's failing, and the failing subtask (connective under
  density) is correctly handled by scoping.
- **Build the dissociation the landed cell asked for.** The HARD_PASS causal-chain cell literally named the missing
  test (non-adjacent bridge). Injecting a dead-end between a force cause and its result — a one-variable manipulation
  — is what let plausibility beat locality CI-sep with the twin losing, instead of the coincidence-with-recency that
  hid the effect before.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- **CORRECT the causal-SELECTION verdict.** Cause-selection is TWO subtasks: (a) connective-marked = STRUCTURAL (the
  connective's clausal argument) — a force-dynamic plausibility scorer is CI-sep WORSE here (-0.2079, n=101), so the
  prior §2b note ("faithful fix = force-dynamic attribution") is WRONG for this subtask; scoping is the correct,
  optimal treatment. (b) bridging (unstated) = plausibility: force dynamics for PHYSICAL (demonstrated: +1.000 CI-sep
  over locality on non-adjacent bridges, twin losing), ToM for MENTAL/SOCIAL (the 11/16 majority — a DIFFERENT brain
  system, mPFC/TPJ, currently unbuilt).
- **The causal QA instrument is CIRCULAR for plausibility.** Its gold (build_causal_questions) is the positional
  connective-adjacency rule; the scoped floor replays it; perfect-parse and oracle-participants both score worse. Any
  future causal-plausibility claim MUST use a non-circular instrument (the bridging dissociation here, or a
  meaning-derived gold like RC.GOLD), not the connective QA.
- **NEW located adjacent-component negative:** `_read_causation` builds NO bridging (unstated) links (connective-gated),
  and the majority of narrative causation is mental/social — the biggest causal fidelity gap, needing a ToM organ.

## What I did NOT establish / would withdraw first if wrong
- The constructive positive is a CONTROLLED dissociation on **8 constructed physical items** (verbatim-style prose
  with injected dead-ends), not a naturalistic benchmark. It PROVES the mechanism (plausibility can beat locality
  when they are dissociated) with a clean twin, but it does not measure real-world bridging accuracy or n. I would
  withdraw any "X% of real bridges" reading — the real-corpus non-adjacent physical-bridge MINING (a foundation
  build) is the named next step. FORCE_BRIDGE=1.000 is a mechanism ceiling on clean single-force items, not a
  field accuracy.
- The QA reproduction is faithful (dense blanket EXACT at 0.8317) but off_pos reproduced at 0.9010 vs the landed
  0.8911 (a 1/101 first-match tie-break edge in my cached-events harness). The CONCLUSION (scoping is the ceiling; the
  gold is positional) is unaffected — 0.8911 and 0.9010 are both the positional-on-sparse rule and both the max.
- The twin mean on the bridge (0.459, not ~0) reflects that with few candidates a random force-label lands on the
  true cause ~half the time; the p95 (0.750) is the honest null and FORCE_BRIDGE (1.000) clears it.
- I did NOT land any hdlab change; I recommend KEEPING scoping and filing the ToM-bridging successor. If the strategy
  disagrees and wants a connective plausibility scorer landed, I would withdraw nothing — the -0.21 says do not.

---

### TLDR (plain language)
I was asked to replace "pick the nearest earlier event as the cause" with a smarter "does this cause plausibly
produce this effect" scorer, and to retire a stop-gap that currently hides the problem. I built the smarter scorer
(the brain's force-dynamics) and it made the cause questions **much worse** — because when a sentence says "because"
or "so", the grammar word itself points at the cause, so "nearest to that word" is basically the right answer, and
preferring the most forceful verb pulls you off it. I also found the scoreboard we grade on was literally built by
the "nearest" rule, so nothing else can win on it — and, deeper, that most story causation is *mental* ("she frowned
because she remembered"), which a physical-force scorer can't represent at all. So the stop-gap isn't debt to
retire — it's the right call. THEN I showed the smart scorer's real value: on the *other* kind of case (no grammar
word, an unstated cause an event or two back) it clearly beats "grab the nearest" and a scrambled version fails —
proving it reads real cause-and-effect, just for the case the brief pointed it at the wrong one. The real next win
is a *mental*-causation reader (a different brain system), which I've mapped as the follow-on problem.

### QUESTIONS
None blocking. One judgement call for strategy: I recommend NOT retiring the scoping and instead filing a
mental/intentional-causation (ToM) bridging organ as the real causal lever; if you'd prefer I instead grow the
physical-bridge positive into a real-corpus mined gold (a foundation build) before filing, say so.

### NEXT STEPS (PRIORITY-ORDERED)
1. **KEEP scoping** in `_read_causation` (it is the connective-path optimum; the brief's premise is refuted). No wire.
2. **FILE: a mental/intentional-causation (ToM) bridging organ** — the 69% majority of narrative causation force
   dynamics cannot touch (mPFC/TPJ; Wolff & Barbey 2015). The highest-yield causal follow-on.
3. **Optionally wire a force-dynamic BRIDGING selector** (physical slice, demonstrated here) once a bridging readout
   exists — additive, but check goal no-regress (causal_links feeds the goal graph). Grow the 8-item dissociation
   into a real-corpus mined non-adjacent physical-bridge gold first (foundation build) for a field number.
4. **Retire the causal QA instrument for plausibility claims** — it is circular (gold = positional). Future causal
   work uses a non-circular gold (RC.GOLD / the bridging dissociation).
