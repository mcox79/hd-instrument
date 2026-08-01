# Broad brain-fidelity audit — Director synthesis (2026-08-01)

USER-requested systematic audit of what we've built + the roadmap, vs the brain. Synthesized by
the Director from the 6 landed lit-scan sub-scans (the parent audit agent parked without
synthesizing). All sub-scans are DEFLATED lit-scans (CITED@/REASONED@, ESTABLISHED/CONTESTED
flagged); treat rankings as hypotheses, not settled fact.

## PER-COMPONENT FIDELITY SCORECARD (verdict + gap)

1. **Encoder / extraction (causal predictive coding)** — VERDICT: in-flux; principle right, objective
   wrong-target. "Predict real external input" is brain-right, BUT run-6 MEASURED that next-token-
   identity CE does NOT constrain the pooled ENTITY representation (it collapsed, cos~1.0) while
   EMA-latent prediction kept it healthy. GAP: the objective must shape the ENTITY/mention
   representation directly, not just next-token. (A-vs-B VET pending: genuine vs Barlow-reg artifact.)

2. **FHRR binding** — VERDICT: keep (glass-box + generalization-proven) but with 3 named fidelity
   caveats. (a) binding-by-SYNCHRONY (one historical justification) = LARGELY REFUTED as a general
   mechanism (Shadlen&Movshon 1999; Ray&Maunsell 2010-11) -> do NOT justify our binding via
   synchrony. (b) The brain's entorhinal/TEM structure-content factorization is on the RIGHT side
   for GENERALIZATION to novel role-filler combos (Bernardi 2020; Flesch; Johnston&Fusi) = VINDICATES
   our factored binding for the generalization property we proved. BUT the brain's actual bind is
   CONJUNCTIVE (outer-product/pattern-separation), NOT a clean orthogonal algebraic bind/unbind. (c)
   VSA/HRR is engineering + computational-PLAUSIBILITY (Eliasmith NEF/Spaun existence-proof; grid-cell
   fit strongest, Dumont&Eliasmith 2020) with NO direct neural evidence for convolution-binding. GAP:
   our clean algebraic bind differs from conjunctive coding; we may lack the MIXED-SELECTIVITY high-dim
   expressivity the brain pairs WITH factorization (pure factorization = generalization but low
   capacity; brain has both).

3. **PE-gate commit-then-revise** — VERDICT: defensible, monitor. Brain-grounded (PBWM gating + P600
   reanalysis), and we proved it on oracle signal. BUT incremental processing is better-supported as
   CONTINUOUS/graded (surprisal Levy 2008; constraint-satisfaction MacDonald; good-enough Ferreira)
   than a clean DISCRETE commit-then-revise gate. Discrete has real precedent (Van Gompel race; P600)
   but is not the modal view. GAP: may need to be more graded/probabilistic than a hard gate.

4. **Situation-model loop** — VERDICT: endpoint right, ARCHITECTURE ORDER WRONG (biggest roadmap
   risk). "Build/update a situation model" as the functional endpoint = ESTABLISHED (Zwaan&Radvansky;
   Kintsch C-I). BUT processing is INTERACTIVE: situation-model info (plausibility, discourse
   referents, verb-driven expectations) feeds BACK to constrain extraction/parsing within ~200ms
   (Trueswell/Tanenhaus/Garnsey 1994; Altmann&Kamide 1999; Crain&Steedman). Our roadmap's strict
   feed-forward extraction -> situation-model ORDER is NON-biological. GAP: needs top-down feedback
   from the situation model into extraction (constraint-based/interactive, not syntax-first serial).

5. **Competencies / growing library / coref** — VERDICT: ordering VINDICATED. Acquisition is
   SPECIFIC-before-general (Tomasello verb-islands -> schemas; de Villiers subject-relative-first;
   reference/entity-tracking before abstract role-assignment) = SUPPORTS our entity-identity-first
   competency ordering. Modularity nuance: brain uses mixed-selectivity + a factorized shadow, not
   clean per-role subspaces -- our modular factored approach is defensible for generalization/no-
   interference but is not the brain's native format.

6. **Discovery-gate (CRP/MDL match-or-allocate)** — VERDICT: grounded (event-segmentation/SEM),
   not re-scanned this cycle; no new fidelity concern surfaced.

## TOP FIDELITY RISKS (ranked — the "what else is like the collapse" list)
1. **ROADMAP IS FEED-FORWARD; THE BRAIN IS INTERACTIVE.** Our extraction->situation-model pipeline
   assumes a completed parse feeds a downstream model. The brain runs them as ONE interactive loop
   with top-down feedback. This is the biggest architectural fidelity gap and it's baked into the
   whole plan. HIGH impact.
2. **Encoder objective must constrain the ENTITY representation** (run-6 finding), not just next-token.
   Directly blocking the current thread.
3. **Binding operator + missing mixed-selectivity**: clean VSA algebraic bind vs brain's conjunctive
   coding; synchrony justification dead; pure factorization lacks the capacity mixed-selectivity adds.
   MEDIUM (glass-box + generalization-proven = keep, but don't over-claim brain-fidelity of the op).
4. **PE-gate discreteness** vs the brain's graded/continuous processing. MEDIUM.

## MISSING MECHANISMS (ranked, keep-digging)
1. **Precision-weighting** (Friston/Feldman inverse-variance reliability-gain on prediction error) --
   flagged as the TOP cheap missing mechanism (see the precision-weighting handoff). A scalar gain on
   the existing update, not a new organ.
2. **Top-down interactivity** (situation-model -> extraction feedback) -- the roadmap fix (risk #1).
3. **Multi-level prediction** (token + event/discourse grain simultaneously; Kuperberg&Jaeger 2016) --
   literature-mandated for beyond-next-word comprehension; architecturally heavier.
4. **Mixed-selectivity expressivity** paired with our factorization.
5. Lower/later: attention-salience, neuromodulation (ACh/NE fast-slow gain), sleep/replay
   consolidation, hierarchical timescales.

## SINGLE HIGHEST-LEVERAGE NEXT FIX (Director judgment)
The run-6 finding and the interactivity finding CONNECT: an encoder trained as a standalone feed-
forward next-token predictor (a) doesn't constrain the entity representation and (b) is the wrong
ARCHITECTURE (extraction should be inside an interactive loop, not a feed-forward stage). => the
highest-leverage move is NOT another encoder-objective proxy tweak. It is to reframe extraction as
an INTERACTIVE, situation-model-coupled process whose objective directly shapes the entity
representation -- i.e. fold the "constrain the entity rep" fix (run-6) and the "top-down feedback"
fix (risk #1) into one architectural change, and add PRECISION-WEIGHTING (cheap, top missing
mechanism) as the reliability-gain on that loop's error-driven update.

## STRATEGIC RECOMMENDATION
- PAUSE the isolated encoder-collapse proxy churn (~6 fairness-questionable runs; instrument-
  perfectionism). It has already yielded its lesson: a standalone feed-forward token-predictor is
  the wrong frame (doesn't constrain the entity rep + non-interactive).
- The clean, brain-faithful results this session (composition, PE-gate commit-then-revise, the
  earn-mechanism [MIDDLE], the gold-wall characterization) STAND and are atomized -- the churn is
  specific to the encoder-objective sub-thread.
- NEXT: (1) one A-vs-B VET to confirm run-6's inversion is interpretable (genuine vs reg-artifact);
  (2) design the interactive extraction<->situation-model loop with an entity-rep-shaping objective +
  precision-weighting -- this is the architectural next step the audit points to, replacing the
  standalone-encoder frame. Bring to USER for steer before building (architectural change).

Calibration: all sub-scan claims deflated + CONTESTED-flagged; the interactivity + acquisition-order
findings are the best-replicated; the binding + mixed-selectivity findings are active-research/
contested; the "highest-leverage = interactive entity-rep loop" is Director SYNTHESIS (REASONED),
not an established result.
