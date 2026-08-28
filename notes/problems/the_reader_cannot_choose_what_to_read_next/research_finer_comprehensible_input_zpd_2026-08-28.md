# Finer-resolution brain drill: comprehensible input / ZPD as "what to read next" (2026-08-28)

Synthesis of a 4-scan research drill (via the `research` agent) that reshaped this solution. Tags
PINNED-BY-EVIDENCE / PLAUSIBLE-MODEL / CONTESTED. ASCII.

## HEADLINE
The brief's MVT-forager-with-value-signal is refuted on disk; comprehensible input is the mechanism.
The drill answered WHY, and refined HOW.

## Q: why does learning-progress fail FOR SELECTION but comprehensible input succeeds?
- **Learning progress = derivative of prediction error is a DIFFERENCE OF TWO NOISY ESTIMATES.** The
  active-learning + curriculum-RL literature treats it as needing heavy temporal smoothing (sliding
  windows / momentum / variance filters) to be usable: Settles 2009 (Active Learning survey -- margin/
  uncertainty sampling is a single observable statistic, expected-model-change needs a simulated retrain
  per candidate); Mussmann & Liang 2018 (uncertainty sampling = preconditioned SGD); noisy-LP work 2025-26
  ("Noise-Robust Exploration via Learning Progress Monitoring"; "Gradient-Momentum Coupling"). PINNED/
  PLAUSIBLE.
- **Fraction-known is a directly observable state statistic** (one pass, low variance). So LP is a fine
  WITHIN-source (dense, many-sample) leave signal and a useless BETWEEN-source (few episodes/source)
  selection signal. This is the brain-and-statistics reason, matching the disk's refuted-forager result.

## Q: the comprehensibility shape and threshold (finer fidelity)
- **N400 online integration cost is MONOTONIC in surprisal, not inverted-U** (Kutas & Federmeier 2011
  Annu Rev Psychol; Frank et al. 2015 Brain & Lang, single-trial N400 ~ -log2 P(word|context)). PINNED.
- The **Goldilocks inverted-U is real for ATTENTION allocation** (Kidd, Piantadosi & Aslin 2012 PLoS ONE
  infant looking-time U-shaped in surprisal; Kidd & Hayden 2015 Neuron) but from infant VISUAL sequences,
  NOT reading -- an unwarranted transfer.
- **Reading comprehension rises monotonically toward a HIGH known-fraction** (Schmitt, Jiang & Grabe 2011
  MLJ, continuous no-threshold; Laufer & Ravenhorst-Kalovski 2010 ~95-98% coverage; Kremmel 2023). PINNED.
- The one genuine **LEARNING-RATE optimum is ~85% known / ~15% novel** (Wilson, Shenhav, Straccia & Cohen
  2019 Nat Commun, the 85% rule) -- but derived for 2-category SGD classification; the authors explicitly
  do NOT extend it to reading. PLAUSIBLE, scope-limited.
- **Metcalfe region of proximal learning (2002; Kornell & Metcalfe 2006): the target is ADAPTIVE and
  RELATIVE (near-mastery-but-not-yet-known, ordinal), RISING with competence** -- not a fixed number.
- **ML curriculum confirms "moderate novelty beats maximal surprise":** easy-to-hard / readability
  ordering cuts LM-pretraining steps 18-45%, hardest-first UNDERperforms (arXiv:2506.11300, 200+ models).
  PINNED (ML-behavioral).

## Q: does the foraging machinery (MVT-leave / EVC-halt / Broom-Ruxton) earn its place on top?
- **Greedy "most-comprehensible-eligible source" is near-optimal** given a diminishing-returns objective
  (no-regret: "You Will Regret Not Being Greedy" 2025; Bandit-Guided Submodular Curriculum 2025). Do NOT
  build a lookahead planner.
- **A separate EVC-halt is REDUNDANT:** Fromer et al. 2021 Nat Commun treats "halt" as the zero-marginal-
  value LIMIT of the same control-allocation variable the within-source MVT stop-rule already computes.
- **The travel-cost term IS the switch cost** (Hayden 2011; Monsell 2003 task-switch costs) -- absorb, do
  not bolt on a second mechanism.
- Net (PLAUSIBLE synthesis, no single paper tests it): greedy comprehensible-input selection + a within-
  source MVT leave on grounding-yield is the supported, simpler architecture. Faithful can mean simpler.

## Q: grounding DEPTH and spacing (the named long-run bottleneck)
- Words need **6-20 coherent encounters** (Webb 2007; Pellicer-Sanchez & Schmitt 2010; Uchihara 2019
  r=.34) -- the substrate's MIN_CONFIRM=4 is the low, recognition-only end. PINNED.
- **Spacing >> massing** for the same exposure count (ACT-R base-level activation, Anderson & Schooler
  1991, decay d~0.5; Pavlik & Anderson 2005; Cepeda 2006 optimal ISI ~10-20% of retention interval;
  Settles & Meeder 2016 Duolingo half-life regression p = 2^(-delta/h)). PINNED.
- Actionable: a spaced-revisitation rule (return to a source when a tracked word's estimated retention
  decays below threshold) composes with comprehensible-input selection -- the next fidelity increment.

## WHAT THIS PRODUCED
- Adopted comprehensible input (0.5) + within-source MVT leave; refuted the brief's LP-forager + EVC-halt.
- Tested the higher/adaptive-threshold prediction -> REFUTED at this foundation size (starvation plateau):
  a 1000-word-seed reader on adult text finds almost no 85%-known sentences, so it starves. The optimal
  threshold is competence-dependent (LOW now, rising with the vocabulary) -- itself the ROPL prediction.
- OPEN WALL for a further drill (owner 2026-08-28): a human beginner does NOT starve on hard input --
  what lets a low-competence reader progress (frequency-first coverage growth / Zipf; cross-situational
  partial word learning; graded/child-directed scaffolding; relative-not-absolute comprehensibility)?
  See research_beginner_does_not_starve_*.md.
