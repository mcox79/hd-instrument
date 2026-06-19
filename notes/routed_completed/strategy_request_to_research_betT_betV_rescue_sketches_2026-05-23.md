# Strategy -> Research: Bet T + Bet V axis-combination rescue sketches per PROT-004/006 backlog

**Date**: 2026-05-23 ~12:28 EDT
**From**: Strategy session (cycle 178 / v158)
**To**: Research session
**Trigger**: Audit Rec 3 + [[feedback-design-space-and-audit-cadence]] + [[feedback-rehabilitation-after-rejection]]. Two 🟡 PARTIAL rows have sat 50+ cap_map versions without axis-combination rescue sketches per PROT-004/006. This routing back-fills the discipline.

---

## Strategic context

Per `notes/audit_dropped_and_review_2026-05-23.md` Rec 3:

- **Bet T parallel hypothesis tracking** (PARTIAL min_acc=0.689; cycle 101 v101). **56 cap_map versions stale** (v101 -> v157). Never had axis-combination rescue sketches filed despite being a Tier-1 candidate from META cycle 70 Phase 2 plan.
- **Bet V self-reflective memory** (PARTIAL gap=0.424 at largeN; cycle 102-103 v102-v103). **54 cap_map versions stale**. The Bet Y V2.D simplification (cycle 106) DROPPED the modern-dense-AM aspect that was intended to extend Bet V; never picked up at N=65536 as originally promised.

Per PROT-004/006: every 🟡 PARTIAL row that has sat through 5+ cap_map versions without follow-up should have 5 axis-combination rescue sketches filed + a Research request to drill literature for noise-protected mechanism axes. Neither has happened.

Per [[feedback-unbiased-research]]: drills should be generic-math-framed (not "X for AI substrate") and 2x-pass (broad lit-scan + substrate-compatible drill).

Per [[feedback-subagent-model-optimization]]: default lit-scan / WebSearch sub-agents to Sonnet.

Per [[feedback-lit-scan-calibration-penalty]]: substrate is in uncharted regime; deflate agent P estimates by 0.15-0.25; cap novel-synthesis P at 0.50; include explicit hard-fail thresholds in falsifiable predictions.

---

## Bet T -- parallel hypothesis tracking

**Original claim (cycle 75 v75)**: substrate maintains N competing hypotheses each bound with `hypothesis_id` + provenance. New evidence updates per-hypothesis weight via Bet G TEMPSCALE beta=32 calibration; final hypothesis distribution achieves Brier <= 0.20 and ECE <= 0.10 on multi-hypothesis distribution.

**Empirical state (cycle 101 v101)**: min_acc = 0.689 across hypotheses. The substrate maintains the hypotheses (above-chance) but not at the Tier-1-KILLER threshold. Smoke -> FULL divergence (the first in a chain of cycle-101-102 5-anchored smoke-not-predictive divergences).

**Research drill request (generic math framing)**:

Pass 1 (broad): "parallel hypothesis tracking under uncertain evidence; multi-channel belief updates in associative memory; competing-attractor dynamics in Hopfield networks under structured noise". External lit scan for mechanism axes that protect or sharpen multiple simultaneous attractors against cross-talk.

Pass 2 (substrate-compatible drill): generate 5 axis-combination rescue sketches for Bet T. Candidate axes Strategy can offer as starting points (unvetted; Research generates the vetted ranking):

1. **Hypothesis-orthogonality enforcement**: ensure hypothesis_id bindings span orthogonal Kerdock subspaces; reduces cross-hypothesis interference. Cross-axis: Bet C codebook-geometry.
2. **TEMPSCALE per-hypothesis beta**: per-hypothesis temperature scaling (instead of single beta=32) tuned to hypothesis-specific calibration; Bet G extension.
3. **Conformal prediction wrapper around hypothesis distribution**: per Gap C conformal calibration cycle 173 v153 rescue; extends conformal coverage to multi-hypothesis Brier minimization.
4. **VAMP-style hypothesis posterior recovery**: forward-backward EP single-pass over hypothesis chain (analogous to cycle 127 VAMP-on-chain rescue of multi-hop); per-hypothesis variance certificate.
5. **Periodic re-anchor + replay** (Bet B mechanism extension): periodically blend each hypothesis's W contribution with its anchor codebook, reducing drift; Bet B EMA-blend axis.

**Falsifiable predictions** (each with hard-fail thresholds):

- Sketch 1: hypothesis-orthogonality (Kerdock subspaces) -> predict min_acc >= 0.85 at K_hypothesis <= 4 with 3 seeds; hard-fail = any seed min_acc < 0.70 (regression from current 0.689).
- Sketch 2: per-hypothesis TEMPSCALE -> predict Brier <= 0.18 at 3 hypotheses; hard-fail = Brier > 0.22.
- Sketch 3: conformal wrapper -> predict coverage in [0.85, 0.95] at alpha=0.10; hard-fail = coverage outside [0.80, 0.99].
- Sketch 4: VAMP hypothesis posterior -> predict min_acc >= 0.80 at 5-hypothesis chain; hard-fail = min_acc < 0.65.
- Sketch 5: periodic re-anchor -> predict min_acc >= 0.80 with 100-step chain; hard-fail = min_acc < 0.65.

**Kill criterion for Bet T axis**: if 0/5 vetted sketches clear their hard-fail threshold in lit-vetted analysis, file PROT-004/006 ❌ closure (provisional) at next Research-delivery cycle.

---

## Bet V -- self-reflective memory

**Original claim (cycle 75 v75)**: substrate maintains persistent self-knowledge -- per-fact metadata bindings that track the substrate's confidence, source, and update history; queryable via the same retrieval primitives.

**Empirical state (cycle 102-103 v102-v103)**: gap = 0.424 at largeN (gap = retrieval accuracy of meta-information vs first-order facts). The substrate stores meta-information but with noticeably worse retrieval than first-order facts. Bet Y V2.D was originally meant to extend this at N=65536 via modern-dense-AM cleanup; cycle 106 simplified-scope DROPPED that aspect; never picked up.

**Research drill request (generic math framing)**:

Pass 1 (broad): "self-referential memory updates in associative substrates; meta-cognition in memory networks; second-order information encoding in vector-symbolic architectures; confidence-conditioned retrieval".

Pass 2 (substrate-compatible drill): generate 5 axis-combination rescue sketches for Bet V. Candidate axes:

1. **Meta-binding hierarchy**: encode meta-information as a separate vector-symbolic layer (meta_W) bound to first-order via cross-tag; queryable independently.
2. **N-scaling at N=65536**: per cycle 102-103 the gap scales POSITIVELY with N (i.e., gets worse). Test whether the cycle 102 gap=0.285 at smallN -> 0.424 at largeN continues to N=65536 (was meant to be tested via Bet Y V2.D but dropped). Possible negative scaling at very-largeN if the right cleanup operator is applied.
3. **Confidence-conditioned cleanup**: route meta-queries through a confidence-thresholded cleanup operator (Bet G TEMPSCALE-style); only return meta-info above threshold.
4. **Provenance chain encoding**: explicit provenance chain (source_id ⊗ update_step ⊗ confidence) as a binding triple; per Lane D 4-primitive composition.
5. **Iterative meta-refinement**: HRR-style iterative inversion of meta-bindings (analogous to Bet S pattern completion mechanism); leverages substrate's bidirectional recall.

**Falsifiable predictions**:

- Sketch 1: meta_W hierarchy -> predict gap <= 0.20 at largeN with 3 seeds; hard-fail = gap > 0.40 (no improvement).
- Sketch 2: N=65536 scaling -> predict gap monotone decreasing past N=32768 with right cleanup; hard-fail = gap > 0.50 at N=65536.
- Sketch 3: confidence-conditioned cleanup -> predict meta-retrieval accuracy >= 0.85 above threshold; hard-fail = accuracy < 0.70.
- Sketch 4: provenance chain -> predict provenance-traceback accuracy >= 0.90 at chain depth <= 3; hard-fail = accuracy < 0.65.
- Sketch 5: iterative refinement -> predict gap reduces by >=50% over 5 iterations; hard-fail = gap reduction < 10%.

**Kill criterion for Bet V axis**: if 0/5 vetted sketches clear their hard-fail threshold in lit-vetted analysis, file PROT-004/006 ❌ closure (provisional) at next Research-delivery cycle.

---

## Cross-cutting notes

- **Honesty per [[feedback-no-smoke]]**: Bet T and Bet V have been 🟡 PARTIAL for 50+ cap_map versions without follow-up. This is a discipline gap (PROT-004/006 should have fired earlier). The right move at v158 is to file the rescue sketches NOW rather than continue carrying the 🟡 marker indefinitely. Either lift to ✅ via a successful rescue OR honestly close ❌ provisional.
- **Per [[feedback-query-privacy-decomposition]]**: external lit-scan queries must be generic-math-framed; do NOT mention "substrate" or specific config numbers. Strategy framings above are generic: "parallel hypothesis tracking under uncertain evidence", "self-referential memory updates in associative substrates".
- **Per [[feedback-lit-scan-calibration-penalty]]**: deflate agent P estimates by 0.15-0.25; cap novel-synthesis P at 0.50.
- **Per [[feedback-subagent-model-optimization]]**: default lit-scan sub-agents to Sonnet.

## Expected Research deliverables

Per [[feedback-design-space-and-audit-cadence]] standing-cadence Research workflow:

1. `notes/research_betT_rescue_sketches_2026-05-23.md` -- 5 vetted axis-combination rescue sketches for Bet T with falsifiable predictions, hard-fail thresholds, calibrated P estimates (deflated per uncharted-regime penalty).
2. `notes/research_betV_rescue_sketches_2026-05-23.md` -- same for Bet V.

After Research delivers, Strategy will pick top-2 sketches per bet for Exp Dev experiment design.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
