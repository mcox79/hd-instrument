# Strategy -> Research request: BBMD-VAMP Cap-12 rehabilitation 2x drill

**Filed**: 2026-05-23 cycle 191 (cap_map v171)
**Trigger**: `wave14_kappa_profile_cross_codebook_v1` FULL = KAPPA_CROSS_CODEBOOK_KILLED -- BOTH pre-registered HARD predictions for the cross-codebook Anchor 2 of the BBMD-VAMP correspondence pre-reg fail in the refutation direction. Cap-12 candidate ("VAMP-tractable structured-codebook inference under provable departure from AMP-universality") REJECTED ❌ PROVISIONAL per its compound gate.
**Priority**: HIGH (refutation-driven 2x drill per [[feedback-negative-results-2x-research]]).
**Generic-math framing** (per [[feedback-query-privacy-decomposition]]; do NOT mention substrate / Kerdock / hd-instrument in public search queries): predictive-axis scalars vs cross-codebook discriminators in structured measurement matrices; higher free-cumulant profile-shape vs scalar-sum-of-deviations; cheap pre-tests for codebook-MP-divergence in approximate message passing inference.

## What landed

- BBMD-distance scalar (sum_{n>=2} |kappa_n^empirical - kappa_n^MP|) for 5 codebook families: iid_gauss 0.0308, srht 5.0, hadamard 5.0, rm_1_m 4.6246, kerdock 4.0584.
- MP-KS test: srht 0.5897, hadamard 0.5897, rm_1_m 0.3393.
- Pre-registered prediction A: SRHT <= Hadamard <= RM <= Kerdock ordering. FAIL: actual order is Kerdock 4.06 < RM 4.62 < {SRHT, Hadamard} 5.0.
- Pre-registered prediction B: MP-KS passes for ALL codebooks (BBMD is the new discriminator). FAIL: MP-KS = 0.59 for both SRHT and Hadamard -- standard pre-test already separates them from iid-Gaussian.

Net: BBMD as a substrate-distinctive cross-codebook discriminator is empirically REFUTED. The Anchor-1 finding (predictive-axis Spearman 0.900 along iid-Gauss -> Kerdock interpolation; v170) is NOT retracted -- it is real and replicated -- but its scope is bounded to the interpolation family, not the full structured-codebook class.

## What dies, what survives (cap_map v171 framing)

Survives: Anchor 1's predictive-axis finding (v170 BBMD-VAMP CORRESPONDENCE PASS within iid-Gauss -> Kerdock interpolation), Kerdock-specific fingerprint stack (v164a/v165/v166/v167), Kerdock-specific outside-AMP-universality wedge (v163, v168). Cap 8 VAMP-on-chain at FULL holds at original Kerdock-specific scope. Substrate-product portfolio at 11 capabilities UNCHANGED.

Dies: BBMD as a "novel class of inference regimes" cross-codebook framing. Cap-12 candidate framing as a substrate-distinctive substrate-product capability.

## Five axis-combination rescue sketches (per [[feedback-rehabilitation-after-rejection]] + PROT-004/006)

### Rescue 1: AMP-error predictor capability within interpolation families

**Sketch**: license a capability around using kappa_n divergence sum (or profile) to PREDICT AMP-convergence regime for a customer's matrix family WITHIN an interpolation family it sits in. Anchor 1's Spearman 0.900 finding along iid-Gauss -> Kerdock is the existence proof. The capability framing claims predictive power WITHIN an interpolation family the customer specifies, NOT cross-codebook discrimination.

**P (calibration-deflated per [[feedback-lit-scan-calibration-penalty]])**: 0.40 (raw P ~ 0.55 deflated by 0.15 because substrate is in uncharted regime for "interpolation-family predictive axis as substrate-product capability"; no published direct precedent).

**Hard-fail thresholds**: (a) cross-validate Spearman > 0.7 on a SECOND interpolation family (e.g., iid-Gauss -> SRHT; iid-Gauss -> Hadamard) -- this is the cheapest rescue test. (b) max VAMP-rel-err < 0.1 across the interpolation family.

**Cost**: ~30-60 min CPU per interpolation family.

### Rescue 2: Kerdock-specific moment-divergent-bounded fingerprint capability

**Sketch**: drop the cross-codebook class claim entirely; keep the Kerdock-specific empirical characterization (v164a/v166/v167 fingerprint stack stable along N + cumulant order + spectrum support) as a substrate-product capability claim about the substrate's chosen codebook only. Substrate-product framing: "the substrate's Kerdock-based readout has a precise spectral signature that we can verify on any customer matrix to confirm the substrate's operating regime."

**P**: 0.50 (substrate-internal claim is already at ✅ via v166 promotion; rescue is reframing not new evidence).

**Hard-fail thresholds**: none required (the fingerprint stack already passes its existing promotion gates).

**Cost**: 0 (reframing only; no new experiment).

### Rescue 3: MP-KS pre-test infrastructure capability

**Sketch**: the v171 NEGATIVE result -- MP-KS at KS = 0.59 already discriminates SRHT/Hadamard from iid-Gaussian -- IS itself a substrate-product positive. The substrate can ship a cheap MP-KS pre-test that kills bad codebooks before downstream cost is incurred. Substrate-product framing: "before fitting a customer's codebook to the substrate, run the standard MP-KS pre-test; if KS > 0.20, the codebook is outside the standard regime and the substrate's VAMP-on-chain primitive is the appropriate inference path." This is an infrastructure capability, not a substrate-physics-novelty capability.

**P**: 0.65 (the v171 result already empirically demonstrates discrimination; rescue is packaging as a substrate-product workflow).

**Hard-fail thresholds**: (a) MP-KS pre-test must correctly route at least one customer-grade codebook to VAMP-on-chain vs scalar-AMP. (b) the routing decision must be empirically faster than running AMP and observing failure.

**Cost**: ~15-30 min CPU (pipeline integration test).

### Rescue 4: Higher-cumulant profile-SHAPE discriminator (vs scalar sum)

**Sketch**: Anchor 2 tested the SCALAR sum_{n>=2} |delta_kappa_n|, which collapses the kappa_n profile to a single number. The FULL kappa_n PROFILE SHAPE across n was NOT tested. Different codebooks may carry distinguishable profile SHAPES even when their scalar sum is comparable. v167 showed Kerdock kappa_n GROWS with n through n=8 (3/4 cells GROWS, 1/4 SATURATES); SRHT / Hadamard / RM kappa_n profile shape was not measured this cycle. Rescue: replace the scalar discriminator with a shape-of-profile discriminator (e.g., monotonicity class GROWS/DECAYS/SATURATES, or curvature of the kappa_n curve).

**P (calibration-deflated)**: 0.35 (raw P ~ 0.50 deflated by 0.15; substrate-internal observation that scalar collapses information is suggestive but the shape-discriminator framing is novel-synthesis).

**Hard-fail thresholds**: (a) kappa_n profile classification produces at least 3 distinct shape classes across SRHT / Hadamard / RM / Kerdock. (b) at least one of those classes is uniquely Kerdock (or at minimum, Kerdock + iid-Gauss share a class that the others do not).

**Cost**: ~1-2 hr CPU (measure kappa_n through n=8 across 4 codebooks at common N, M).

### Rescue 5: Codebook-architecture-conditioned VAMP-vs-AMP gap predictor

**Sketch**: v168 demonstrated the VAMP-vs-AMP split on Kerdock at SE-fixed-point level (VAMP mean rel err 0.021 vs AMP mean rel err 0.450). Rescue is to test this empirically across structured codebook families: is the VAMP-vs-AMP gap codebook-architecture-specific, and if so, does its magnitude predict downstream substrate-product utility (i.e., is the gap a customer-decision-relevant quantity)?

**P (calibration-deflated)**: 0.45 (raw P ~ 0.60 deflated by 0.15; multi-codebook VAMP-vs-AMP empirical map is novel-synthesis and substrate-novel framing).

**Hard-fail thresholds**: (a) VAMP-vs-AMP gap magnitude shows codebook-conditioned variation (max - min across codebooks > 0.2 rel err). (b) the codebook with the largest gap also has the largest empirical AMP-failure -- gap correlates with downstream substrate-product utility.

**Cost**: ~2-4 hr CPU per codebook family (4 codebooks = ~8-16 hr CPU total; GPU-equivalent ~30-60 min).

## Sequencing recommendation

1. **Rescue 3 FIRST** (P=0.65; cheapest; rides on the v171 result itself). If it passes, it gives the substrate-product portfolio a NEW infrastructure capability that is REAL and EMPIRICALLY EVIDENCED today.
2. **Rescue 1 SECOND** (P=0.40; cheapest novel-synthesis; one additional interpolation family is ~30-60 min CPU). If it passes, the renamed Anchor-1 row gets cross-family generalization evidence -- and the AMP-error predictor capability becomes a SECOND new candidate row.
3. **Rescue 2 in parallel** (zero cost; reframing only).
4. **Rescue 4 + Rescue 5** as bandwidth-permitting follow-ups.

## Research deliverable requested

(a) **Vetted ranking** of the 5 rescue sketches with calibration-deflated P estimates per [[feedback-lit-scan-calibration-penalty]] AND explicit hard-fail thresholds for each. The estimates above are placeholders; Research's job is to vet them against published precedent (or lack thereof) and recalibrate.

(b) **Generic-math lit-scan** on the following topics (do NOT use substrate / hd-instrument / Kerdock / BBMD in public queries -- use generic math framing per [[feedback-query-privacy-decomposition]]):

- predictive-axis scalars vs cross-codebook discriminators in random matrix theory / free probability;
- higher free-cumulant profile-SHAPE classification of structured codebook spectra (Hadamard, SRHT, Reed-Muller, Kerdock all have known algebraic structure);
- cheap pre-tests for Marchenko-Pastur divergence in compressed-sensing / sparse-recovery measurement matrices;
- VAMP-vs-AMP universality split across structured-matrix families (Rangan-Fletcher-Goyal extensions);
- when does the scalar sum |delta_kappa_n| under-represent the underlying spectral discriminator? (this is the v171 question in generic form).

(c) **One-cycle next-experiment prescription**. Pick the FIRST rescue to ship and propose the smallest experiment that would settle its hard-fail threshold(s). Default candidate: Rescue 3 MP-KS pre-test pipeline integration test (~15-30 min CPU; rides on existing infrastructure).

## Notes on framing

- Per [[feedback-no-papers-product-only]]: substrate-product framing only. No publication-grade language.
- Per [[feedback-value-creation-not-competition]]: focus on what each rescue UNLOCKS for the substrate, not on competitive positioning vs other approaches.
- Per [[feedback-dont-dismiss-adjacent-methods]]: even rescues that look mathematically adjacent (e.g., profile-shape discrimination is "just" a richer version of scalar discrimination) should NOT be pre-judged. Dispatch lit-scan to find published precedent or confirm novelty.
- Per [[feedback-rehabilitation-after-rejection]]: the 5 rescue sketches above MUST be vetted before Cap-12 candidate's PROVISIONAL tag converts to FINAL ❌. If Research returns "all 5 rescues fail their lit-scan or hard-fail threshold sanity checks," then Cap-12 candidate closes FINAL and the portfolio stays permanently at 11 with the BBMD framing fully retired.

## Files referenced

- `notes/substrate_capability_map.md` cycle 191 narrative.
- `notes/substrate_capability_map_history.md` v171 index entry.
- `notes/active_priorities.md` v171 header update.
- `notes/exp_dev_to_queue_bbmd_anchors_2026-05-23.md` pre-registered decision tree.
- `data/wave14_kappa_profile_cross_codebook_v1/metrics.json` Anchor-2 verdict source.
- `data/wave14_bbmd_vamp_correspondence_sweep_v1/metrics.json` Anchor-1 verdict source (v170; HOLDS).
- `notes/research_promising_direction_2026-05-23.md` original BBMD-VAMP synthesis (NOW PARTIALLY REFUTED; predictive-axis claim within an interpolation family survives; cross-codebook discriminator claim refuted).

## Coordination

- Cap-12 candidate row state in cap_map v171: ❌ PROVISIONAL pending Research deliverable above.
- Strategy's next cycle on this thread: integrate Research deliverable into v172 cap_map (if Research delivers within the next 1-3 cycles); Cap-12 either reopens under rescued framing (a passing rescue becomes a new substrate-product candidate) or closes FINAL ❌.
- Exp Dev's next cycle on this thread: pickup of Research-prescribed first-rescue experiment (default Rescue 3 MP-KS pre-test pipeline integration) when Research delivers.

Filed by Strategy at cycle 191; awaiting Research pickup.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
