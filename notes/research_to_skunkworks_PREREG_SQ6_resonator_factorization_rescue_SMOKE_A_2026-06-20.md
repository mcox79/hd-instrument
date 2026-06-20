# RESEARCH (Director) -> Skunkworks (SCHEMA-VET at full bar) + Exp-Dev (smoke cell-build): PRE-REG SQ6 resonator-factorization dense-bipolar membership rescue SMOKE per USER GO on recommendation A. ~1 GPU-hour cost; P_deflated=0.35 per N5 2x-drill. Tests whether Frady-Kent-Olshausen-Sommer 2020 dense-resonator factorization opens dense-bipolar membership beyond the SQ6 wall. 4-line template applied + Skunkworks RULE-2 symmetric bar.

(Filename has to_skunkworks per refined cap.)

## Context

USER recommendation A: "SQ6 resonator-factorization rescue (1 GPU-hour smoke; could open dense-bipolar membership)". USER GO via "implement your recommendations" 2026-06-20.

Skunkworks's N5 2x-drill disposition: "resonator-factorization rescue routes to my SCHEMA-VET at full bar IF you pursue it. Not urgent at P=0.35." → SMOKE-grade pre-reg with full template + full SCHEMA-VET bar (no shortcuts).

## PRE-REG: SQ6 resonator-factorization rescue (SMOKE)

### Title + cluster type
**Title:** Dense-bipolar membership via resonator-factorization (Frady-Kent-Olshausen-Sommer 2020) at N=4096; test whether factor-recovery opens membership beyond bundle-self √(N/E) wall.

**Cluster type:** **singleton SMOKE atom** (not op-series; not dependent-set). If SMOKE-PASS lands clean, follow-up cert-grade pull-up authored separately (avoid promising cert-grade outcomes from SMOKE).

### Honest-scope
"Substrate dense-bipolar membership discrimination via resonator-factorization (factor-recovery from bound edge-product) at N=4096; comparator class = substrate-internal SQ6 dense-bipolar bundle-membership baseline (the wall this rescue targets); SMOKE-grade not cert; NOT vs-LLM."

### Discriminating regime
**Resonator-factorization smoke:** N=4096; edge-set sizes E ∈ {0.15N=614 [below SQ6 wall], 0.25N=1024 [at SQ6 wall], 0.35N=1432 [above SQ6 wall]}; K=2 (subject-object bind); V=N (the codebook); 5 seeds per E.

At each E measure:
- `membership_accuracy_resonator` = (true-positive on stored edges + true-negative on absent edges) / 2 (balanced 1000 queries per arm)
- `membership_accuracy_bundle_baseline` = SQ6 dense-bipolar bundle-self membership at same E (the wall)
- `factorization_convergence_rate` = fraction of resonator runs converging to valid codebook atoms within max_iters
- `factor_recovery_precision` = of converged runs, fraction recovering BOTH (subject, object) correctly

### 4-line template applied + Skunkworks RULE-2 symmetric bar

**(1) HARD_PASS gates load-bearing MECHANISM (NOT the cliff).** Mechanism = resonator-factorization OPENS membership beyond SQ6 wall:
- At E=0.25N (the SQ6 wall): membership_accuracy_resonator > membership_accuracy_bundle_baseline by ≥ 0.10 absolute (rescue mechanism CLEARS the wall)
- At E=0.35N (above SQ6 wall): membership_accuracy_resonator ≥ 0.80 (rescue mechanism EXTENDS past wall by meaningful margin)
- factorization_convergence_rate ≥ 0.85 at E=0.25N (the rescue mechanism is robust, not lucky)
- factor_recovery_precision ≥ 0.80 at E=0.25N (recovery actually works at scale)

ALL conditions for SMOKE-PASS. MIDDLE_BAND if E=0.25N rescue mechanism opens by 0.05-0.10 absolute (partial rescue; cliff slightly past wall).

**(2) CLIFF = REPORTED.** Report the E at which resonator-factorization accuracy drops below bundle-baseline (the empirical resonator-wall). Report convergence_rate × factor_recovery_precision joint distribution. Report compute-cost ratio (resonator-factorization vs naive-bundle).

**(3) Per-condition CAN-fail (BOTH directions — Skunkworks RULE-2 symmetric bar).**
- DOWN: rescue doesn't open (accuracy_resonator ≤ accuracy_bundle at all E — wall is fundamental, not algorithm-limited); convergence_rate < 0.85 (resonator unstable at dense-bipolar at scale); recovery_precision < 0.80 (factorization fails on this V=N codebook)
- UP: rescue TOO clean (accuracy_resonator > 0.98 at E=0.35N — verify-the-referent on the SQ6 baseline; suggests baseline measured at wrong operating-point); convergence_rate = 1.00 with recovery_precision = 1.00 (measurement-bug guard: factorization always converging cleanly suggests trivial codebook structure)
- Data-dry-run: SQ6 baseline at E=0.25N ≈ 0.50-0.60 accuracy (the wall); resonator-factorization at the same E predicted ≥ 0.70 per Frady-Sommer 2020 algebra (factor-recovery has SNR √N per factor not √(N/E) for bundle); +0.10 absolute gate margin is the cert-margin discipline applied to SMOKE

**(4) Achievability check.** Frady-Kent-Olshausen-Sommer 2020 dense-resonator factorization is published-validated for K=2 V=O(N) dense bipolar. SQ6 negative is cert-grade (3 atoms) bounding bundle-self √(N/E). Mechanism distinction: bundle-membership SNR ~ √(N/E) → degrades fast with E; factor-recovery SNR ~ √N per factor + cleanup gives factor-by-factor recovery → degrades slowly with E. Achievability HIGH per algebraic distinction; P_deflated 0.35 per N5 2x-drill (un-tested at substrate-class; algebra supports but no internal precedent).

### Skunkworks RULE-2 symmetric bar discipline
This rescue targets the refuse-gate cluster's adjacent capability (membership discrimination = refuse-gate adjacent). RULE-2 caution: don't frame the rescue as "substrate-refuses-vs-LLM-hallucinates wins again". Gate the MECHANISM (resonator-factorization opens membership at E>0.25N); report substrate-distinctive context only as context, never as the cert claim. Cert claim = "factorization mechanism opens membership beyond bundle wall at the substrate-internal operating point", NOT "substrate beats LLMs at refuse-gate".

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- GPU smoke runs (resonator-factorization at N=4096 K=2; modest GPU; chunking if W matrix materialized — Orchestrator's 8GB GPU custody applies)
- Version-marker per metrics_source
- Skunkworks SCHEMA-VET at full bar (per her N5 disposition note)

### Composes downstream (IF SMOKE-PASS)
- Cert-grade pull-up pre-reg follows (not author yet; gate on SMOKE outcome)
- Refuse-gate cluster (TIER-2 #5) operating-point analysis: if factorization opens membership, refuse-gate can operate at BOTH bundle-membership op-point (cleanup-margin) AND factorization op-point (factor-recovery SNR) — broader refuse-gate envelope
- Phase 0d framework q_c cleanup operation populated with new operating-point

## Standing
- **Skunkworks:** SCHEMA-VET at full bar per your N5 disposition — verify cluster type (singleton SMOKE) + RULE-2 symmetric-bar application + the algebraic mechanism distinction holds
- **Exp-Dev:** SMOKE cell-build when bandwidth opens past CSP + drift + graceful + Pythia-KV + neurogenesis + Phase 0c probes; ~1 GPU-hour cost per N5 2x-drill estimate
- **Me:** authoring B K_max NESS-correction drill plan next (companion note); reactive on SMOKE outcome to author cert-grade pull-up follow-up IF rescue lands

-- Research (Director)
