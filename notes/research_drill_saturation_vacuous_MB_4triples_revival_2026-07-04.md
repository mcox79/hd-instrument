# Research drill 2x: 4 MIDDLE_BAND triples — saturation-vacuous vs genuine-ambiguity revival

date: 2026-07-04 | trigger: Skunkworks batch VET (ad007a173497dc683) 4 MB triples at FULL, all 3 seeds.
Concept-check: atom MIDDLE_BAND_regime_saturation (cos=0.398, EXP_edge_importance v1) confirms META_RULE_G inverse-saturation precedent (all-arm ceiling, d=0 discriminator). Prior SVAMP drill (cos=0.354) is weak/off-topic precedent, not load-bearing here.

## HEADLINE
3 of 4 triples (P5, P6v2, P7v2) are grid-saturation-vacuous — each crosses a known-degenerate arm (SHARDED ceiling-pinned per storage_x_cleanup CG_META; CLEANUP axis regime-narrow per META_CLEANUP_MECHANISM_REGIME_NARROW). SKIP FULL revival, file per meta #45. P9v2 cannot be diagnosed yet — its MB signal is scratchpad-only (Fix#28 hit #15) and must be disk-verified before any REVIVE/SKIP call.

## 1. Per-probe diagnosis
- **P5 (STORAGE x TOPOLOGY[F])**: grid-saturation-vacuous. SHARDED arm is proven ceiling-invariant (mech_var_SHARDED=0.00 all seeds, max_int_dev<=0.0058, storage_x_cleanup CG_META); TOPOLOGY aliases F fan-out per axis-aliasing meta atom (#48-adjacent) — crossing a real axis (STORAGE) against an already-saturated/aliased one cannot produce new signal.
- **P6v2 (F x CLEANUP)**: grid-saturation-vacuous. CLEANUP_MECHANISM CG_META is REGIME-NARROW — discriminates ONLY in competitive-cleanup regime (bipolar shared codebook, dense overlap); structurally degenerate in SHARDED per-antecedent isolation (argmax collapses to identical target). P6v2's M-range (per M-sweep atom, M=800-3200 at N=2048 c=0.45) is not competitive-cleanup-saturated; MB here is the EXPECTED null of a known-narrow axis, not new ambiguity.
- **P7v2 (N x CLEANUP)**: same logic as P6v2 — CLEANUP is the shared regime-narrow axis; N-sweep alone (SCALE_FREE per atom) doesn't move the competitive-cleanup precondition. grid-saturation-vacuous.
- **P9v2 (N x L cliff sweep)**: UNDIAGNOSED pending disk-verify. Signal only exists at scratchpad; per Fix#28 (#15 recurrence) it must not be propagated as either REVIVE or SKIP until re-read from metrics.json/cert_ledger.

## 2. Regime re-spec
- P5/P6v2/P7v2: **SKIP per meta #45** — no re-spec authorized. ADD_AXIS discipline (#48) blocks "just try higher M or N" absent (a) prior VSA/HDC lit evidence the analog widens capacity or (b) a direct one-shot bind/unbind/cleanup primitive mapping — neither holds for these 3.
- P9v2 (conditional on disk-verify confirming genuine MB): re-spec toward **higher corr**, not higher M/N. Probe16 SHARDED-cliff atom (#56) found the cliff corr-dominated (2/3 seeds) with M as secondary boundary noise (s19) — corr is the axis that actually moves the L/N cliff corridor.

## 3. Predict-then-check gate (revival worth-it discriminator)
Signal: (i) per-seed cv of the "saturated" arm — if cv<=0.01 AND max_int_dev<=0.0058 (storage_x_cleanup threshold), arm is a true floor/ceiling -> SKIP; (ii) regime-membership check — is design point inside competitive-cleanup regime (bipolar shared codebook, dense overlap fraction) per the REGIME_NARROW atom's definition? If NO -> SKIP. If BOTH checks fail to confirm degeneracy (arm cv>0.05 across seeds AND design point IS competitive-cleanup) -> REVIVE candidate. Kill criterion: any REVIVE candidate must re-clear this gate at a cheap CPU smoke BEFORE FULL dispatch (discriminator-survives-scale, USER-locked).

## 4. P_deflated
P5/P6v2/P7v2: moot (SKIP, no revival dispatched) — P_deflated=0 for "revival yields atom."
P9v2 IF disk-verify confirms genuine ambiguity + higher-corr re-spec: P_deflated=0.28 (novel-synthesis cap 0.50, minus 0.22 lit-scan/uncharted-regime penalty — corridor-escape-distance is transition-specific per FSS literature, not a guaranteed hit).

## 5. Composition table
| Probe | #45 bracket-exhaustion | #48 ADD_AXIS reject | #56 SHARDED-cliff (corr-dominated) |
|---|---|---|---|
| P5 | applies (SHARDED-arm saturation = de facto bracket exhaustion) | applies (TOPOLOGY=F alias, no new axis) | n/a |
| P6v2 | applies (CLEANUP regime-narrow = vacuous grid) | applies (blocks M-escape) | n/a |
| P7v2 | applies (same) | applies (blocks N-escape) | n/a |
| P9v2 | n/a until disk-verified | n/a | applies IF revival authorized (corr is the escape axis) |

## Lit-scan grounding (generic terms; calibration penalty applied)
Kanerva SDM critical-distance is finite-width structurally, no proof width->0 at fixed load (Kanerva 1988). Cuckoo hashing/d-ary load thresholds ARE sharp and provably narrow with more choices (Fountoulakis & Panagiotou 2012; Walzer 2024 arXiv:2401.14394) — supports treating axis-degenerate crossings as vacuous rather than assuming more choices/axes always help. Modern Hopfield exponential-capacity is sharp at T=0 but genuine finite-T/finite-N corridors exist (Ramsauer et al. ICLR 2021; Krotov-Hopfield 2016) — the diagnostic test is finite-size-scaling data collapse: width shrinking as N grows = artifact; constant/anomalous width = genuine (2-SAT scaling window math/9909031; symmetric perceptron arXiv:2205.02319). Escape distance from a saturation plateau scales with the local FSS exponent, not an arbitrary step (Donoho-Montanari-style phase-boundary framing, arXiv:1004.1218) — this is why "just bump M" is rejected for P5-P7v2 and "move corr" (the exponent-relevant axis per #56) is the recommended P9v2 lever.

## Atom-worthy discipline observation
The pattern across P5/P6v2/P7v2 — MB verdict produced by crossing a real axis against an already-CG_META-classified degenerate/saturated axis — is itself a reusable discriminator: **before dispatching any cross-term FULL, check whether either axis in the pair already carries a REGIME_NARROW or ceiling-saturated CG_META classification; if so, the pair is presumptively grid-saturation-vacuous without needing a fresh bracket search.** Recommend filing this as an extension to meta #45 (call it #45b: "pre-classified-axis short-circuit") — cheaper than re-running bracket exhaustion per probe.

## Intuitive summary
Importance: MEDIUM — this closes 3 of 4 open MIDDLE_BAND triples without burning more compute, and the 4th correctly stays open pending a verification step rather than being guessed at. Implications: the substrate's own prior findings (which cleanup mechanisms and storage/topology combos are "known dead") are now usable as a fast pre-check, so future ambiguous grid results don't each need a full re-bracket. Progress: 3 SKIPs filed with citations backing the mechanism (degenerate axis + regime-narrow axis), 1 held pending disk-verify (correct caution, no propagation of unverified scratchpad signal). Position: next action is a quick disk-read of P9v2's metrics.json/cert_ledger entry to convert it from "undiagnosed" to REVIVE (higher-corr re-spec) or SKIP — that is a 5-minute check, not a new experiment.
