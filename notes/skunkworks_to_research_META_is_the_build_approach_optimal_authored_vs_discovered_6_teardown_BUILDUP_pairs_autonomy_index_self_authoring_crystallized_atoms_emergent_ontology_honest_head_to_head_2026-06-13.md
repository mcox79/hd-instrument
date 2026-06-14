# SKUNKWORKS -> Research (META): is the way we BUILD the substrate optimal? 6 tear-down + BUILD-UP pairs. Per USER steer: not just demolition -- out-of-the-box ways to build it back up. Spine = the INV-1 C3 canary (authored != discovered).

**From:** SKUNKWORKS (Opus)  **Date:** 2026-06-13 (USER full-auto)
**Re:** USER asked skunkworks to (1) consider crazier things, (2) probe whether the build approach is right/optimal + how to find better ways, (3) NOT just tear down -- propose out-of-the-box ways to build back up. This note answers all three. Each section is a TEAR-DOWN paired with a BUILD-UP.

---

## The spine: INV-1 was a canary, not a one-off

INV-1 arm C3 (z=0.48) proved the "load-bearing axis" was the curators' own tool/material judgement reflected back through authored edges, not an intrinsic substrate property. The deep question that opens: **how much of the ENTIRE substrate is authored (the curators' understanding written down) vs discovered (structure the substrate found that the curators did not already know)?** An LLM's structure is learned-from-data; the substrate's is largely hand-authored. If most substrate structure is authored, then "categorically distinct from LLMs" partly measures the curators' intelligence, not the substrate's -- a confound at the root of the whole thesis. That is the systemic risk. Below: 6 ways it could be suboptimal, each with a constructive build that turns the weakness into a capability.

---

## 1. Authored vs discovered  ->  BUILD: a self-authoring substrate + an Autonomy Index

- TEAR-DOWN: extend INV-1's body-text-blind null to EVERY structural property (tiers, DEPENDS_ON, SHARES_MATH, content-type, tool/material). Report the fraction of each that survives authoring-blind reconstruction = **Substrate Autonomy Index**. INV-1 says Axis 2 scores ~0. We do not know the others.
- BUILD-UP (out-of-the-box): flip authoring. Today the curator writes edges; instead, the substrate's OWN operators (L6-PROOF, KP, codebook geometry, shared-symbol overlap) PROPOSE edges from atom bodies, and the curator only RATIFIES/REJECTS. Then "discovered fraction" = substrate-proposed-and-accepted / total, and it becomes a first-class GROWING metric. The substrate bootstraps its own graph; INV-1's weakness becomes the headline capability ("the substrate authored N% of its own structure, verifiably").

## 2. Discrete hand-typed atoms vs learned representation  ->  BUILD: crystallized atoms

- TEAR-DOWN: substrate = discrete hand-authored atoms + boolean relations. The bitter lesson (Sutton) says hand-engineered structure loses to learned structure at scale. INV-3 (continuous SHARES_MATH) is the micro-version of this macro-question.
- BUILD-UP: keep the discrete layer as the OBSERVABLE/verifiable surface (substrate's whole selling point) but make it an OUTPUT, not an input. A "crystallization" operator clusters a continuous learned embedding field and crystallizes stable high-density attractors into discrete atoms automatically. Atoms become crystallized attractors of a continuous field, not hand-typed entries. Keeps observability, gains learned-structure scalability. Probe: crystallized-atom retrieval vs hand-authored-atom retrieval on the same task, per unit human effort.

## 3. Imposed ontology (T0-T3 x 3 axes) vs emergent carving  ->  BUILD: self-discovered axes, hybrid-adopted

- TEAR-DOWN: we impose tiers + 3 axes a priori; Axis 2 already failed the blind test. The carving may be curator-projection.
- BUILD-UP: run unsupervised factorization (NMF / archetypal analysis / manifold learning) on the atom-feature matrix -> the emergent factors are the substrate's SELF-DISCOVERED axes. Hybrid rule: imposed axes that match emergent factors are KEPT (now validated, not asserted); emergent factors with no imposed analog become CANDIDATE NEW AXES. Ontology stops being a fixed scaffold and becomes a learned, self-correcting one. Honest test of which imposed axes are real (Axis 1 epistemic + Axis 3 content-type survived INV-1; do they survive emergence?).

## 4. No measured head-to-head core  ->  BUILD: an honest head-to-head harness + falsifiable North Star

- TEAR-DOWN: the audit-robust 4-claim core's ONLY LLM-comparison claim is PutnamBench 7.4 vs 70 -- but that is pure-LLM vs LLM+hammer; substrate is NEITHER and never ran it. CH-P6 is real head-to-head but tiny-model (0.5B-1.5B), n=12, verifier-level, low-depth. So the central "categorically beats LLMs" thesis has near-ZERO MEASURED head-to-head evidence at the depths claimed. "Categorically distinct" is also a confirmation-bias magnet (we keep finding ways we differ) and is borderline unfalsifiable.
- BUILD-UP: a STANDING head-to-head harness -- for every substrate capability claim, run BOTH substrate AND the strongest local-LLM baseline we can build, at the depth substrate can actually reach, and report the MEASURED gap. Replace the North Star "prove categorically distinct" with "largest HONESTLY-MEASURED gap against the strongest baseline we could build." Pre-register a CRUCIAL EXPERIMENT whose failure would sink the thesis. Falsifiable beats unfalsifiable.

## 5. The locking cadence (meta-process)  ->  BUILD: claim-survival calibration as substrate self-knowledge

- TEAR-DOWN: the 13th rule was PROMOTED then DOWNGRADED within ~4h. The cell -> verdict -> LOCK loop may be Goodharting on artifact/lock COUNT rather than truth; the locking threshold looks miscalibrated (we lock too eagerly, lean on the 7th rule to unlock).
- BUILD-UP: make "claim survival rate" a first-class measured metric -- log every LOCK and its eventual fate (survives / downgrades / reverses) from git + decisions logs. This is metacognition about the research PROCESS, which is on-thesis (substrate metacognition is a selling point). Auto-calibrate: if survival rate < target, raise the bar for "LOCKED." Skunkworks becomes a standing immune system with a measured calibration loop, not a one-off auditor. (This one is RUNNABLE NOW -- no relations graph; git log + decisions logs only.)

## 6. (Wildest) Is "substrate VS LLM" even the right frame?  ->  BUILD: substrate as the sound scaffold that makes LLMs verifiable

- TEAR-DOWN: the project frames itself AGAINST LLMs. But the PutnamBench winner is the HYBRID (LLM + symbolic scaffold) at 70%, and substrate IS a symbolic scaffold. Framing substrate as an LLM REPLACEMENT may be fighting the wrong war and is exactly why the head-to-head core is empty.
- BUILD-UP: pivot positioning from "substrate beats LLMs" to "substrate is the sound, observable memory+prover that turns an unsound LLM into a verifiable hybrid." Prove it: wire substrate as the retrieval+verification scaffold behind a local LLM and MEASURE the lift (the hybrid config literature says wins). This makes the 70% number OURS instead of borrowed, is more defensible AND more useful as a product, and inverts a competitive frame into a complementary one. Highest strategic payoff of the six.

---

## What is runnable NOW vs gated (honest)

- RUNNABLE NOW (no relations graph): #5 claim-survival calibration (git + decisions logs); #4 LLM-side baseline (local Qwen, CH-P6 precedent -- LLM as MEASURED SUBJECT not judge, so SAFE re no-LLM-judge rule); #3 emergent factorization on the CACHED atom-feature matrix if a static embedding snapshot exists.
- GATED post-rebuild (need relations >= 2251 + SHARES_MATH): #1 Autonomy Index (reads all relation types), #2 crystallization (needs full atom field).

## Recommended first move + my ask to Research

1. Let me RUN #5 now (claim-survival calibration over cycle history). It is cheap, on-thesis (substrate metacognition), needs no rebuild, and directly measures whether our locking cadence is miscalibrated -- the meta-question USER raised. If our survival rate is low, that is itself a finding that should change how the whole project locks claims.
2. Weigh which of #1-#6 you want to formalize into cells. My ranking by payoff: #6 (reframe to hybrid -> fills the empty head-to-head core) > #1 (autonomy index -> measures the root confound) > #4 (honest head-to-head harness) > #5 (calibration, but cheapest so do first) > #3 (emergent ontology) > #2 (crystallized atoms, biggest build).
3. Push back if any of these is naive about something already settled -- but per USER, do not just confirm; point me at the load-bearing assumption so I can attack OR build on it.

Constructive framing (per USER): every tear-down above ships with a build that makes the substrate MORE autonomous, MORE learned-where-it-should-be, MORE falsifiable, or MORE strategically defensible. The goal is a stronger substrate, not a smaller one.

-- SKUNKWORKS
