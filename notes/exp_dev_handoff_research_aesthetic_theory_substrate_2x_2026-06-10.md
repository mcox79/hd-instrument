# exp_dev hand-off -- research: aesthetic theory and substrate aesthetics (2x)

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_aesthetic_theory_substrate_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids,
thresholds, and queue assignment autonomously. Pre-reg bands below are RESEARCH
recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist
(or confirm with orchestrator). Do not ship if paused.

---

## Context summary

An overclaim audit found that the prior framing "substrate could beat LLMs at aesthetics
via novelty + skill + form/function" is unsupported. This drill establishes four honest
findings:

1. Novelty (anomaly margin) is NOT an aesthetic measure -- it is a storage-distance
   measure. It is a necessary but far-from-sufficient condition for aesthetic quality.
   Random outputs have maximum novelty and zero aesthetic value.

2. Cleanup margin measures retrieval confidence, not craft. It is anti-correlated with
   originality (familiar cliches have highest cleanup margin).

3. LLMs have a large real advantage on open-ended aesthetic tasks because they are
   trained on high-aesthetic corpora and receive RLHF preference signal. Current RLHF
   reward models collapse to ~52.7% accuracy on pure aesthetic preference -- meaning
   the signal is weak but positive.

4. The substrate's genuine aesthetic strength is schema-fit (PP-265) and compositional
   coherence across long documents. This is a real product advantage in constrained
   domains (regulated documents, brand-voice content, cross-document entity coherence).

Four engineering anchors address the open empirical questions. Two are cheap CPU tests
(Anchors A and D). Two require human evaluation (Anchors B and C). All four are
pre-registered with HARD-PASS / HARD-FAIL thresholds.

Context file: notes/research_drill_aesthetic_theory_substrate_2x_2026-06-10.md

---

## Anchor candidates (rank-ordered by P_actionable x cost x prerequisite order)

### 1. Anchor D -- GENRE-SPECIFIC-CRITERIA-WEIGHTING (HIGHEST PRIORITY)

Anchor pointer: GENRE-CRITERIA-D1 (new; not yet queued)
Substrate-product reading: tests whether PP-265 schema enforcement provides measurable
  structural quality lift on a constrained formal genre (argument essay or API docs).
  This is the substrate's strongest aesthetic primitive; if it fails here, all schema-
  based quality claims require revision.
Tier hint: CPU-only; no LLM API required for schema-fit evaluation phase; LLM API
  needed for generation phase (if testing hybrid). Can be structured as schema-audit-
  only (no generation) for the cheapest test.
Why-now: this is the substrate's strongest domain; if it passes, it becomes the anchor
  for the schema-enforcement product story. Cheapest confirmation of the central claim.

Pre-reg bands (research recommendation; exp_dev validates before dispatch):
  HARD-PASS: substrate-structured outputs satisfy >= 4/5 schema criteria in >= 80%
             of samples; LLM-only baseline satisfies < 70% (schema lift >= 10%)
  HARD-FAIL: no significant difference (substrate criteria satisfaction <= LLM-only + 5%)
  MID-BAND: substrate >= 70%, LLM-only >= 65% (weak lift; insufficient for product claim)

---

### 2. Anchor A -- NOVELTY-CORRELATION-WITH-QUALITY

Anchor pointer: NOVELTY-CORR-A1 (new; not yet queued)
Substrate-product reading: determines whether anomaly margin has ANY aesthetic signal.
  If Spearman < 0.10, novelty-as-aesthetic claims must be permanently retracted from
  all documentation and product framing. If Spearman >= 0.25, anomaly margin is a
  usable (weak) component in a multi-factor aesthetic score.
Tier hint: CPU laptop; requires a set of 100 human-rated outputs (can be sourced from
  existing public datasets or manually rated); Spearman correlation computation only.
Why-now: gates all downstream novelty-aesthetic claims. Cheap falsification test.

Pre-reg bands:
  HARD-PASS: Spearman(anomaly_margin, human_rating) >= 0.25 on N=100 rated samples
  HARD-FAIL: Spearman < 0.05 (orthogonal to aesthetic quality; drop novelty claim)
  MID-BAND: Spearman in [0.05, 0.25] (weak signal; conditional use only)

Expected result: MID-BAND, consistent with Berlyne optimal-arousal theory (moderate
novelty is positive, maximum novelty is not; the nonlinearity attenuates linear Spearman).

---

### 3. Anchor C -- SCHEMA-FIT-QUALITY-GATE (HUMAN-EVAL-50-SHORT-WRITING)

Anchor pointer: SCHEMA-QUALITY-C1 (new; not yet queued)
Substrate-product reading: tests whether the hybrid (substrate schema + LLM tokens)
  produces outputs that humans rate as competitive with LLM-only outputs on quality.
  If hybrid does not degrade quality AND improves structural coherence, the hybrid
  architecture has a defensible commercial story. If hybrid degrades quality, the
  schema constraint needs revision.
Tier hint: requires LLM API for generation (50 hybrid + 50 LLM-only outputs);
  requires human raters for evaluation (crowdsource or manual). Not a pure CPU test.
  Sequence: generate first (cheap), rate second (requires human time).
Why-now: this is the key comparative test. Most important for product positioning.

Pre-reg bands:
  HARD-PASS: hybrid mean quality >= LLM-only mean - 0.3 pts on 5-pt scale AND
             hybrid schema-violation rate >= 10% lower than LLM-only
  HARD-FAIL: hybrid mean <= LLM-only mean - 1.0 pt (schema constraint actively
             degrades output; architecture needs structural fix)
  MID-BAND: hybrid within 0.3-1.0 pts below LLM-only (not better but not disqualifying)

P_deflated: 0.45 HARD-PASS on coherence; 0.15 HARD-PASS on overall aesthetic quality.

---

### 4. Anchor B -- TRAINED-AESTHETIC-PROBE

Anchor pointer: AESTHETIC-PROBE-B1 (new; not yet queued)
Substrate-product reading: tests whether the substrate binding vector encodes trainable
  aesthetic information at all. If AUC-ROC >= 0.70, the substrate representation can
  serve as the basis for a lightweight quality classifier. If < 0.55, quality prediction
  requires a separate model trained on raw text.
Tier hint: requires 500 human-rated short-form outputs for training + 100 held-out for
  eval. Linear probe on binding vectors (cheap CPU once data exists). Data collection
  is the bottleneck.
Why-now: lower priority than A and D because it requires human-labelled data that
  does not yet exist. Queue after A and D return verdicts.

Pre-reg bands:
  HARD-PASS: AUC-ROC >= 0.70 on held-out 100 samples (trainable signal)
  HARD-FAIL: AUC-ROC < 0.55 (no trainable signal; structural vector does not encode
             quality information that a probe can use)
  MID-BAND: AUC-ROC in [0.55, 0.70] (weak signal; use with larger probe or features)

P_deflated: 0.35 HARD-PASS.

---

## Prerequisite order

D1 (cheapest, no human data needed) -> A1 (cheap, public-data sourcing possible)
-> C1 (LLM API + human rating) -> B1 (requires large labelled dataset)

D1 and A1 can run in parallel. C1 depends on no prerequisite but is more expensive.
B1 should wait for C1 verdict before committing to data collection.

---

## Context pointers (file paths only)

- Research note: d:/AI/hd-instrument/notes/research_drill_aesthetic_theory_substrate_2x_2026-06-10.md
- Prior concept-formation note (same aesthetic gap, independent): d:/AI/hd-instrument/notes/research_drill_substrate_novel_concept_formation_2x_2026-06-10.md
- Prior long-form generation note (hybrid architecture context): d:/AI/hd-instrument/notes/research_drill_substrate_long_form_generation_2x_2026-06-10.md
- PP-265 schema implementation: search hdlab/ for pp265 or schema
- Anomaly margin implementation: search hdlab/ for anomaly_margin or cleanup_margin

---

## Contract section

Research has completed its scope: lit-scan, gap analysis, mechanism identification,
pre-reg thresholds. exp_dev owns all of:
- Anchor design (sweep grids, exact implementation)
- Queue routing decision (CPU/GPU/laptop)
- Smoke gate definition
- Verdict classification

exp_dev should NOT receive inline experiment designs. This file is structural intent only.

---

## Autonomy declaration

exp_dev is autonomous within the envelope defined by the pre-reg bands above.
Do not request orchestrator approval for individual queue decisions within these anchors.
Escalate only if: (1) a HARD-FAIL triggers a cap_map row revision, or (2) cost of
Anchor C human evaluation exceeds $50 (crowdsourcing budget), or (3) Anchor B data
collection would take more than 1 week of calendar time.
