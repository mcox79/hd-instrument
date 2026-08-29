# Research drill: force-dynamic causation in the brain — is a verb-lexicon typer a wall for CAUSE-vs-ENABLE?

Drill run 2026-08-29 for the SOLVER on `causation_has_no_force_dynamic_typing`. Dispatched 3 parallel
lit-scans (Wolff tendency-source; neural/psycholinguistic CAUSE/ENABLE/PREVENT dissociation;
FrameNet/VerbNet force-dynamics mapping). Two scans returned near-empty (weekly API limit hit mid-run);
the neural/psycholinguistic scan returned in full and is the backbone below. **Sources marked PINNED
were verified at least at citation/abstract level; SPECULATIVE = inferential bridge, not a single
directly-evidenced finding.** Synthesized by the solver from the returned findings.

## The decision-relevant answer (drives what I CLAIM vs report as a bound)

**A verb-lexicon-only force-dynamic typer is a FAITHFUL PARTIAL model. It is faithful where the verb
LEXICALLY FIXES the patient-tendency + concordance; it is a PRINCIPLED WALL for tendency-ambiguous
verbs, where the brain supplies patient tendency from world-knowledge the verb does not carry.**

- **Wolff & Song (2003), "Models of causation and the semantics of causal verbs," Cognitive Psychology
  47:276-332 (PINNED).** Five animation experiments: choice among cause/help/allow/enable/prevent tracks
  the FORCE-VECTOR configuration (patient tendency, affector-patient concordance, resultant) better than
  counterfactual or covariational models. → the categories are psychologically real AND verbs genuinely
  carry force-vector information. This LICENSES a verb-force lexicon as a real signal (not an arbitrary
  mapping). PINNED.
- **BUT the force vectors are inputs from perception/knowledge, not fully lexical.** In Wolff's theory the
  three dimensions are read off the affector/patient force vectors; for a *tending* patient ("the gate
  swings open once unlocked") vs a *non-tending* one ("the jammed gate"), the SAME verb (open) yields
  ENABLE vs CAUSE. The tendency bit is world-knowledge about the patient's disposition. → a verb→class
  lexicon must give ONE answer and is capped at chance on tendency-ambiguous verbs. This is the WALL,
  and it is principled, not an implementation bug. (Measured in `exp_causal_force_lexicon_coverage_v1`:
  verb-lexicon 0.500 vs tendency-oracle 1.000 on covered ambiguous verbs.)
- **Kuhnmuench & Beller (2005), "Distinguishing Between Causes and Enabling Conditions—Through Mental
  Models or Linguistic Cues?," Cognitive Science 29(6):1077-1090 (PINNED, abstract-level).** Directly
  tested the mental-model account of CAUSE-vs-ENABLE and found judgments track LINGUISTIC/TASK FRAMING
  cues, NOT a framing-independent mental model. → CAUSE-vs-ENABLE is **partly linguistically
  CONSTRUCTED**, not a hard-wired stable representation. This CONVERGES with our disk finding that the
  ENABLE (letting) class is barely lexicalised (FrameNet: 8 core ENABLE verbs; of 391 non-gold lexicon
  verbs only 1 is ENABLE). The distinction lives partly in framing/context, not the verb.

**Practical consequence for the build:** claim the typer only where tendency is lexically fixed —
PREVENT/Thwarting/Hindering verbs (always oppose a tending patient) and prototypical CAUSE verbs
(shatter/topple/ignite: patient does not tend). Report the tendency-ambiguous CAUSE-vs-ENABLE case as a
measured brain-faithful bound whose FIX is a patient-disposition/world-knowledge input (an adjacent
follow-on), NOT a bigger verb lexicon.

## PREVENT is special, and reading it via negation IS brain-faithful (PINNED at each end)

- **Wolff, Barbey & Hausknecht (2010), "For want of a nail: How absences cause events," JEP:General
  139:191-221 (PINNED, citation/abstract).** Comprehenders represent "virtual forces that were
  anticipated but never realized" as causally relevant — i.e. a prevented/never-happened endstate is
  actively REPRESENTED (a suppressed event node), not merely omitted. This is the exact mechanism our
  PREVENT-killer needs, and it grounds the "no outcome node to link" argument against the placeholder.
- **Kaup, Yaxley, Madden, Zwaan & Ludtke (2007), QJEP 60(7); Kaup & Ludtke (2010), QJEP 63(12)
  (PINNED).** Negation-as-simulation: negated content is first briefly simulated/activated then rejected
  in favour of the true state (two-step; an active one-step-vs-two-step debate). → reading a prevented
  endstate via a negation/polarity detector over the outcome clause is a defensible model of how a
  prevented outcome is represented. Our endstate detector (default reached; flipped by negation/failure
  cue) is a coarse computational stand-in for this.
- Costlier negation processing (RT + ERP) is a broad, well-replicated pattern (PINNED as a pattern), and
  counterfactual-reasoning fMRI implicates a simulation/memory network (hippocampus, mPFC, precuneus;
  De Brigard et al. 2013 and related, PINNED at title/venue). Whether PREVENT-type force-dynamic
  sentences measurably recruit MORE of this machinery than CAUSE/ENABLE was NOT found head-to-head →
  SPECULATIVE at the joint (PINNED at each end).

## Neural localisation — a CORRECTION for the audit (AUDIT UPDATE)

- **"Kang et al. 2021" (cited in the scoping doc, the probe, and PROBLEM.md §3) is a MISATTRIBUTION.**
  The real matching paper is **Feng, Wang, Liu, Wang, Tian & Fan (2021), "Neural Correlates of Causal
  Inferences in Discourse Understanding and Logical Problem-Solving: A Meta-Analysis Study," Frontiers
  in Human Neuroscience 15:666179 (PINNED, read as full text via PMC8261065).** ALE meta-analysis of 19
  discourse-causal-inference + 20 logical-problem-solving experiments. Discourse causal inference =
  left-lateralised frontotemporal system (left IFG BA45/44/47, left MTG BA21/37, bilateral mPFC BA10/9),
  tied to language + theory-of-mind; logical-problem causal inference = a NON-overlapping frontoparietal
  system (memory/executive). **Critically it studies discourse-BRIDGING causal inference and explicitly
  does NOT dissociate CAUSE/ENABLE/PREVENT** — so it is adjacent, not a direct localiser for force-
  dynamic typing. Correct the citation and soften any claim that the meta-analysis localises the typer.
- **No neuroimaging or ERP study was found that dissociates CAUSE vs ENABLE** (region, latency,
  development). State this as a GAP, not a settled "no". The distinction's reality rests on behavioural
  categorisation (Wolff & Song) + is partly constructed (Kuhnmuench & Beller).

## FrameNet -> force-class mapping (my synthesis; the dedicated scan hit the API limit)

Mapping used (frame membership, the one hand-split being the ENABLE vs PREVENT lexical units of
`Preventing_or_letting`/`Prevent_or_allow_possession`):
CAUSE <- Causation + Cause_* family; ENABLE <- {allow, enable, let, permit, leave, free, loosen, ...};
PREVENT <- Preventing (prevent-sense) + Thwarting + Hindering + Halt. This aligns with Wolff & Song's
verb groupings at the class level (help/allow/enable = ENABLE; prevent/block/hinder = PREVENT;
cause/force/make = CAUSE). Two measured resource gaps: (a) common prevention verbs deter/curb/stall are
absent from FrameNet's Causation family (small principled backoff); (b) broad Cause_* frames over-admit
light/polysemous verbs (do/give/take/see) → low precision on real text without verb-sense
disambiguation (adjacent problem `no_glass_box_verb_sense_disambiguation`).

## Bottom line for the solve
1. Build the typer; claim it where tendency is lexically fixed (PREVENT + prototypical CAUSE) — faithful.
2. Report CAUSE-vs-ENABLE for tendency-ambiguous verbs as a MEASURED wall (verb lexicon 0.50 cap) whose
   brain-faithful fix is a patient-disposition world-knowledge input (adjacent follow-on).
3. The PREVENT-killer (negation/never-happened endstate) is brain-faithful (Wolff/Barbey/Hausknecht;
   Kaup negation-as-simulation) — the sharpest single win over the link-the-nearest-outcome placeholder.
4. AUDIT UPDATE: correct "Kang et al. 2021" -> Feng et al. 2021; note it does not dissociate the subtypes.
