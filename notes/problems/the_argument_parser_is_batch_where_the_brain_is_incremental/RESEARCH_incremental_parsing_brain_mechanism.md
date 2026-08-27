# Research drill: the brain's incremental structure-builder (verbatim, 2026-08-27)

Read-only literature drill dispatched to the `research` agent. Findings that shape the build. Tags: [PINNED]=copy the operation, [UNPINNED]=sweep/invent.

## Q1 — Incremental parsing algorithm: LEFT-CORNER family [PINNED at family level]
- Abney & Johnson 1991: stack-space/local-ambiguity bounds — top-down mispredicts center-embedding cost.
- Resnik 1992: left-corner (recognize leftmost daughter bottom-up, then top-down project the rest of the rule) → stack depth grows ONLY for true center-embedding, matching "the rat the cat the dog chased bit died" being uniquely hard. Rules out pure top-down (over-predicts right-branching difficulty) and pure bottom-up.
- Left-corner RNNGs fit human RT + garden-path better than top-down, smaller beam (arXiv:2109.04939); left-corner parse steps correlate with LATL 350–500ms (Neurobiology of Language). Schuler et al. 2024 left-corner surprisal fits RT comparably to big LMs. Arc-eager dep parsing needs an explicit left-corner-flavored ordering to reproduce center-embedding difficulty.
- Multipath Parsing in the Brain (Franzluebbers/Hale ACL 2024): fMRI evidence for >1 simultaneously-maintained partial analysis (bilateral STG) → small competing BEAM, not strict single-stack.
- BUILD: eager, CONNECTED (no unattached fragments, Sturt & Lombardo 2005), left-corner-flavored, memory cost on center-embedding only, small (2–4) beam. [UNPINNED: beam width, graded vs discrete multipath.]

## Q2 — Verb-driven argument prediction = the left-corner top-down projection step [PINNED]
- Altmann & Kamide 1999: "the boy will eat the ___" → anticipatory saccade to edible BEFORE the noun. Selectional restrictions used predictively, pre-nominally.
- Kamide/Scheepers/Altmann 2003: verb + NP + case combined immediately (multi-cue constraint satisfaction).
- Subcat frame accessed at the verb, drives anticipatory gaze; valency = NUMBER and TYPE of args; obligatory args predicted MORE strongly than adjuncts (ranked slot-opening, PMC4702442).
- Demberg/Keller/Koller 2013 PLTAG: verb's elementary tree inserts substitution/foot nodes for its args IMMEDIATELY, before fillers arrive — SAME operation as the eye-tracking result, formalised. Q1 and Q2 are ONE mechanism.
- BUILD: on a verb, instantiate a typed, ranked argument-slot frame (obligatory>adjunct); open slots bias interpretation of following tokens. This is where `predictive_reader` (selectional-preference centroid) composes. [PINNED — 25+ yrs, multi-lingual, multi-paradigm.]

## Q3 — Revision: BOUNDED/LOCAL, gated by a TWO-ROUTE CONFLICT signal [PARTIALLY PINNED / CONTESTED]
- Frazier&Fodor Sausage Machine + Frazier&Rayner 1982: stage-1 heuristic structure (Minimal Attachment/Late Closure), stage-2 error-driven repair; garden-path = regressive eye-movements localized at the disambiguating word (a TARGETED repair event).
- Local/limited repair (Fodor&Inoue 2000): rebuild only the minimal subtree dominating the error, reuse existing structure, NO full backtrack/parallel history.
- Construal (Frazier&Clifton 1996): PRIMARY relations committed immediately (garden-path-able); NON-primary (many adjuncts/RCs) left UNDERSPECIFIED, resolved by plausibility later. "Leave underspecified" is first-class.
- Ferreira good-enough: recovery is a heuristic PATCH, often incomplete; capacity-graded (higher capacity commits more).
- Kim&Osterhout 2005 SEMANTIC P600 ("hearty meal was devouring the kids"): P600 on purely thematic role-reversal with well-formed syntax → DUAL-ROUTE: fast heuristic thematic-fit route vs slower compositional route, P600 = the CONFLICT/arbitration, not syntax-repair per se.
- Surprisal (Hale 2001; Levy 2008 noisy-channel; Michaelov 2024) explains much N400 + some P600 but is NOT sufficient (2025 critique) — needs semantic-relevance/discourse. Levy noisy-channel adds "infer the INPUT was corrupted" as a third repair mode → plausibility-driven non-literal reading instead of full reanalysis.
- BUILD: revision = BOUNDED LOCAL re-attach at the conflict site (never full re-parse), TRIGGERED by a two-route conflict (fast thematic-fit/plausibility vs current structural/valency parse), not by parse-failure. Make "underspecified/pending" a first-class output. [CONTESTED: exact P600 content, exact minimal-revision algorithm → sweep, hedge.]

## Q4 — Now-or-Never bottleneck [PARTIALLY PINNED]
- Christiansen&Chater 2016 (BBS): raw sensory trace decays ~100ms auditory / ~60–70ms iconic → must chunk-and-pass immediately, raw form lost. CAUSES eagerness + lossy multi-level compression + reliance on learned predictions.
- Direct link to Q3: reanalysis CANNOT re-read raw words — it operates over the already-abstracted (lossy) chunk → principled reason repair is local/bounded/incomplete.
- [UNPINNED: buffer size / chunk granularity — explicitly criticized as underspecified even by sympathizers. The "4–5 word" figure is from an UNRELATED dependency-distance study — do NOT adopt it. Sweep buffer depth.]

## Q5 — Neural: STRUCTURE-BUILDING and ROLE-BINDING are SEPARATE ORGANS [PINNED — most load-bearing]
- eADM (Bornkessel-Schlesewsky): Phase1 category-general structure-building (IFG BA44 + pSTG) SEPARATE from Phase2 argument-role assignment (pSTS/TPJ) SEPARATE from Phase3 interpretive elaboration (ATL).
- Matchin&Hickok 2020: pIFG = morpho-syntactic SEQUENCING (mainly production); pMTG = hierarchical structure-building (comprehension+production). Demotes BA44 from "seat of movement".
- Beber et al. 2025 (Brain Communications, VLSM n=33, fetched): DOUBLE DISSOCIATION, asymmetric. Morphosyntax → IFG opercularis/triangularis + MFG (survives phon-STM control). Thematic role assignment → angular gyrus + pSTG + planum temporale. Posterior damage → SELECTIVE thematic errors with intact morphosyntax; frontal damage → both (structure failure cascades into role failure). Refines (not overturns) Matchin&Hickok. Reversible-role binding is POSTERIOR-TEMPORAL/inferior-parietal, NOT BA44 movement. Convergent causal TMS (l-IPS/posterior parietal disrupts reversible-sentence comprehension).
- BUILD: TWO separable operations over shared coarse-vector+UPOS input — (1) structure/hierarchy-builder (the left-corner attach/predict step) and (2) role-binder (agent/patient via small cue set: word-order/animacy/valency-fit). DO NOT fuse attachment-decision with role-assignment. This IS the brief's split: my incremental STRUCTURE-BUILDER feeds the SEPARATE converged role assigner.

## Cross-thread synthesis
1. Q1 == Q2: left-corner top-down projection IS verb-slot opening. One eager step, not parser+prediction bolted on.
2. Q3 caused by Q4: revision must be local/lossy because raw input is gone. Full re-parse/backtrack is UNFAITHFUL regardless of accuracy.
3. Q5: builder and binder are different organs. Biggest architectural constraint (lesion+TMS+fMRI). Keep attachment separate from role assignment.
Weakest links (sweep, don't hang falsifiability on): Q3 P600 mechanism (contested through 2025), Q4 buffer size (underspecified).
