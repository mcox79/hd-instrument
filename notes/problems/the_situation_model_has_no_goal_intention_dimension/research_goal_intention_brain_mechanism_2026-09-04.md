# Brain-mechanism research drill: the GOAL/INTENTION dimension of the narrative situation model (2026-09-04)

5-lane literature scan grounding the goal/intention dimension in named brain mechanisms, so every
component of the build is labelled PINNED-BY-EVIDENCE (a named structure/computation, copied) or
OUR-INVENTION-UNDER-TEST (a defensible engineering choice, swept). Depth caveat: many findings are
abstract/secondary-source-verified (noted per lane); full-text where marked. This is the reference
cited by `SOLVED.md` §0. Prior drill reused: `notes/research_drill_biology_led_unstated_goal_inference_
inverse_planning_2026-08-03.md` (Baker/Saxe/Tenenbaum inverse planning at P=0.65).

## Lane 1 — Mentalizing substrate: is goal/intention DISTINCT from belief (TPJ)?
- **TPJ (esp. right) is belief-SELECTIVE, not goal-selective** (Saxe & Kanwisher 2003 *NeuroImage* 19:1835;
  Saxe & Powell 2006 *Psych Sci* 17:692 — RTPJ/LTPJ/PC respond to thoughts/beliefs, NOT to goals/
  perceptions/feelings; mPFC responds across all). 
- **dmPFC is the best-replicated single locus for INTENTION/MOTIVE content**, dissociated from manner:
  Spunt, Falk & Lieberman 2010 *Psych Sci* 21:1593; Spunt & Lieberman 2012 *J Neurosci* 32:3575; Spunt
  & Adolphs 2014 *NeuroImage* 99:301 — a "Why > How" double dissociation across 4 paradigms, supramodal
  (video AND text), and it does NOT scale with mirror-system activity (rejects the embodied-simulation
  account). This is the single strongest, most convergent finding in the scan.
- **No clean 3-way belief/desire/intention split** at the neural level (Liu/Meltzoff/Wellman 2009 *Child
  Dev* 80:1163 adult ERP = "shared core + belief-specific add-on"; Ciaramidaro 2007 *Neuropsychologia*
  45:3105 — intention itself fractionates by social/communicative context, overlapping belief regions;
  Abu-Akel & Shamay-Tsoory 2011 group belief+intention as "cognitive ToM" vs affective ToM). **DESIRE is
  the weakest-evidenced construct for its own register** — it piggybacks on shared mentalizing machinery.
- Dennett's intentional stance (1987, MIT): belief + desire are the two co-equal primitives; "intention"
  is the OUTPUT of practical reasoning over them (not an independent third primitive). Philosophy, 2ndary.

**VERDICT (PINNED):** goal/intention is a DISTINCT dmPFC-anchored mentalizing computation, sharing
infrastructure with belief (TPJ/precuneus) but not reducible to it. => keep GOALS a SEPARATE register
from the existing belief/ToM dimension, and **FOLD desire INTO the goal/intention register** (do not
build a third desire register — under-supported).

## Lane 2 — Narrative goal STRUCTURE (goal→plan→action→outcome)
- Zwaan & Radvansky 1998 *Psych Bull* 123:162 — intentionality is one of the FIVE event-indexing
  dimensions; goal-discontinuity raises reading time (a behavioral phenomenon, PINNED). The flat
  "continuity flag" representation is that literature's own simplification, not evidence against richer
  structure.
- Trabasso & van den Broek 1985 *JML* 24:612; **Trabasso & van den Broek 1986 *Discourse Processes* 9:1
  — when causal CONNECTIVITY is held constant, hierarchy LEVEL has NO independent effect on importance.**
  => compute salience from graph connectivity, NOT hierarchy depth alone.
- **Suh & Trabasso 1993 *JML* 32:279 — goal REINSTATEMENT = "most recent unsatisfied superordinate goal"
  stays active** (three methodologies: discourse-analytic, talk-aloud, recognition priming; replicated by
  Long/Golding/Graesser 1992 *JML* 31:634). PINNED.
- **Lutz & Radvansky 1997 *JML* 36:293 — goal STATUS needs ≥3 states with GRADED accessibility: failed >
  completed > neutral** (satisfaction down-weights but does not zero out). PINNED.
- Graesser, Singer & Trabasso 1994 *Psych Rev* 101:371 — superordinate-goal inferences are generated
  ONLINE; subordinate/consequence inferences are offline/on-demand. PINNED (moderate).

**VERDICT (PINNED):** the goal register carries an explicit STATUS field (active/satisfied/failed),
satisfaction = graded decay not deletion, reinstatement = last-unsatisfied-superordinate priority.

## Lane 3 — Unstated-goal INFERENCE: does it need world knowledge? (THE decisive lane)
Three tiers with DIFFERENT requirements:
- **Tier 0 "what did the action TARGET"** (Woodward 1998 *Cognition*: goal = a discrete agent→object
  binding, gated by agency cues) — maps onto argument-structure / thematic-role extraction. Structurally
  recoverable from text, zero world knowledge. **PINNED buildable.**
- **Tier 1 "broad goal-ACT type"** (Schank & Abelson 1977 CD primitives; ~11 ACTs, ~6 goal types) — a
  small closed static lookup. Precedented (SAM/PAM), admissible as a free-to-build static asset, but not
  validated as sufficient. OUR-INVENTION-buildable.
- **Tier 2 "why THIS action over the alternatives"** (Baker, Saxe & Tenenbaum 2009/2017 Bayesian inverse
  planning; Jara-Ettinger 2016 *TiCS* 20:589 naive utility calculus; Csibra & Gergely teleological stance
  — geometric cost in VISION). **In TEXT there is no perceptual analog to path-length/jump-height; cost/
  value must come from world knowledge.** Graesser/Trabasso (constructionist), Sanford & Garrod (scenario
  mapping), Bower/Black/Turner 1979 (script intrusion) are UNANIMOUS that this needs world/script
  knowledge; no competing purely-structural account found despite explicit search.

**VERDICT (PINNED):** Tier-0/1 (what the action targeted, broad act-type) are glass-box-recoverable;
**Tier-2 (open-ended "why this over that") REQUIRES the world-knowledge/meaning channel — the located
negative.** Do NOT mislabel Tier-0/1 output as a full inferred goal (the narrow→general overclaim trap).

## Lane 4 — The LINGUISTIC anchor (non-circular gold)
- **PropBank tags ARGM-PRP (purpose) as a DISTINCT role from ARGM-CAU (cause)** — originally "PNC =
  purpose, not cause" (Babko-Malaya guidelines, LDC2007T21). Corpus-scale existence proof that the
  purpose/cause distinction is surface-recoverable with acceptable annotator reliability.
- **Rationale clauses (RC)** — subject-controlled, permit "in order to", preposable ("[in order] to
  impress John, Mary brought a pen") — vs **Purpose clauses (PC)** with a matrix-argument-bound gap
  (Faraci 1974; Jones 1991 *Purpose Clauses*, Kluwer; Williams 1974). 
- **The reliable disambiguation test = "in order to" substitutability** (the direct analog of "because"
  for cause): "went [in order] to buy bread" OK (purpose adjunct); "*began [in order] to rain",
  "*wants [in order] to leave", "*happened [in order] to see" REJECTED (raising/control complements).
  Plus optionality, preposing, why-answerability.
- **Levin 1993 desiderative/volition/try verb classes** (want/wish/desire/hope; intend/mean/plan/aim/
  resolve/decide; try/attempt/seek/strive) are reliable because the MATRIX VERB, not the infinitive, is
  the unambiguous marker.

**VERDICT (PINNED):** the reliable anchor is the "in order to"/"so as to" purpose class + the Levin
desiderative/intention verb classes. The ambiguous tail (bare "to VP", "for NP", "so that"-as-result)
needs a syntactic disambiguation filter; on real literary prose the purpose-vs-extraposition/complement
attachment and subject-attachment genuinely NEED a dependency parse (measured: bare-purpose precision
0.33 vs a spaCy oracle) — the parse-gated part of the located negative.

## Lane 5 — Goal vs physical CAUSE: separate?
**Decisively separate.** Malle 1999 *Pers Soc Psych Rev*; Malle 2004 *How the Mind Explains Behavior*
(MIT); Malle 2006 meta-reanalysis (n=173) — the GENERIC cause/effect attribution categories give NULL
effects (d≈0–0.1) while the reason/belief-marker categories give ROBUST effects (d=0.4–0.7) on the SAME
data; the "(in order) to / so (that)" construction family is reason-specific and was explicitly EXCLUDED
from Malle's cause-condition stimuli. Second pillar: teleological-vs-mechanical explanation dissociates
under load and lesion (Lombrozo & Carey 2006 *Cognition*). Davidson's "reasons are causes" (1963) is a
live but orthogonal metaphysical point.

**VERDICT (PINNED):** the goal (reason) dimension is DISJOINT from the physical-causation dimension; two
dimensions, not one "explanation" dimension with a sub-flag. => the goal-why vs physical-cause
COMPLEMENTARITY test (measured: goal-why register 0.98 / cause-dim 0.04; physical-cause dim 0.85 / goal
register 0.01) is the brain-faithful signature.

## Bottom line
1. The goal register is brain-mandated SEPARATE from belief (distinct dmPFC computation; desire folded in)
   and DECISIVELY separate from physical causation (Malle).
2. The reliable explicit-construction anchor = "in order to"/"so as to" + Levin desiderative/intention
   verbs (PropBank ARGM-PRP precedent) — buildable glass-box now.
3. Unstated/abductive Tier-2 "why this over that" REQUIRES the world-knowledge/meaning channel = the
   located negative; bare-purpose adjunct attachment on literary prose is parse-gated. Both are the
   explicit-vs-inferred split the brief predicted.
