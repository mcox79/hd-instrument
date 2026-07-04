# 2x drill: SHARDED-storage saturation regime-map gap (2026-07-04)

Trigger: repeating negative pattern (P4 STORAGE x N, P5 STORAGE x F) where SHARDED
pins at 1.000 across both swept axes. 2x discipline: 1 broad lit-scan (2 parallel
Sonnet sub-agents, generic VSA/SDM/hashing terms only) focusing 1 operational drill.

## (a) Q1 lit-scan findings

- Chou 1989, *Capacity of the Kanerva Associative Memory*, IEEE Trans IT / NeurIPS 1987
  (https://ieeexplore.ieee.org/iel1/18/1394/00032123.pdf). Per-hard-location SDM achieves
  sphere-packing bound 1-h2(delta); capacity is address-space/radius geometry, an extensive
  scaling law distinct from bundle/superposition. P_deflated=0.50 (textbook, capped).
- Willshaw/Palm/Knoblauch review (redwood.berkeley.edu/.../knoblauch2010memory.pdf).
  Sparse local nets store ~ln2 bits/synapse near optimal sparsity k~log(n); per-slot
  schemes have a distinct extensive law, analogy not identity to hash-of-slots. P=0.40.
- Fountoulakis & Panagiotou 2012, *Sharp Load Thresholds for Cuckoo Hashing*
  (arXiv:0910.5147). k-choice hashing: sharp load-factor threshold (~0.92 for k=2) —
  succeeds w.h.p. below, fails w.h.p. above. Clean cliff-not-gradient model for
  per-slot/local schemes. P=0.48.
- Frady/Kent/Olshausen/Sommer 2020, *Resonator Networks 2* (arXiv:1906.11684). Capacity
  governed by number of simultaneously-bound factors (chain-depth analog), not dimension
  alone; more factors erodes local capacity even error-free. P=0.38.
- Donoho & Tanner (compressed-sensing phase-transition method). Standard cliff-finding
  design sweeps sparsity ratio vs undersampling ratio jointly — never samples only
  deep-interior points. P=0.42 (methodological analog, not domain-native).
- **Explicit gap**: no source found doing a joint fan-out x dimension regime map for
  per-slot/local associative memory. P4/P5's SHARDED-saturates-on-both-axes result is
  NOT contradicted by lit — it is filling an undocumented gap, not refuting known theory.

## (b) Q2 SMOKE candidates

1. **[TOP PICK] N=512 fixed, fine M/N interpolation, corr in {0.80,0.85,0.90}.**
   Mechanism: per-slot capacity is a load-factor (M/N) + noise (corr) threshold
   (Kanerva sphere-packing + cuckoo-hashing sharp cliff), not F or N in tested ranges.
   Reuses Probe 6 informal anchors directly: N=512,M=3200,corr=0.85 -> acc=0.867;
   N=512,M=6400,corr=0.85 F=1 -> acc=0.85/0.75/0.65 (mechanism-divergent, near cliff);
   N=512,M=6400,corr=0.90 -> acc~0-0.10 (past cliff). Cheapest: only fill M in
   {4000,4800,5600} at fixed N, corr. Minimum sweep: 1 N x 3 corr x 4 M = 12 cells.
2. **Formal M/N x N joint regime map** (generalizes #1). Tests whether cliff M/N ratio
   is roughly N-invariant, as Kanerva/cuckoo theory predicts a ratio threshold not an
   absolute-M threshold. Minimum sweep: N in {512,1024,2048} x M/N in {1,4,8,12.5,16}
   at corr=0.85 (already known cliff-adjacent). Composes directly with
   `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1` by mapping its own boundary.
3. **L (chain-depth) x M/N near cliff** — resonator-network lit predicts depth erodes
   per-slot slack independent of noise. NOT a new gap: Probes 13/14/15 already probe
   L x F / L x CLEANUP cross-terms near the SHARDED cliff per atom-48 addendum
   (unmapped L x N, L x F, L x M, L x corr). Recommend composing with those in-flight
   probes rather than re-authoring.

## (c) Composition with atoms 48/49/sharded_v1

- Atom 48 (regime matrix complete at 6 pairs, axis-aliasing: TOPOLOGY/ALGEBRA = F):
  M/N is NOT aliased with F — it is a genuinely distinct covariate (load factor vs
  fan-out), so candidate 1/2 does not reopen the axis-aliasing question.
- Atom 49 (BUNDLED first-order transition, no mid-band, theory-confirmed via
  AGS/Krotov-Hopfield/Ramsauer): SHARDED's cliff, by the Kanerva/cuckoo-hashing lit
  found here, is ALSO expected to be sharp (not gradual) — same "step function, not
  gradient" character as BUNDLED, just at a different, much higher M/N ratio.
- `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`: P4/P5 REGIME_EXTENSION
  results (SHARDED=1.000 on both N and F axes) are exactly what this atom + lit
  predicts when M/N stays far below the per-slot cliff. The atom's scope should be
  amended: "holds for M/N << cliff-ratio; cliff-ratio itself unmapped — candidate 1/2
  above is the mapping test."

## (d) Recommendation

**SHARDED-cliff regime probe: YES (candidate 1, cheap N=512 M/N-interpolation).**
BUNDLED-only cross-term work cannot answer the open question (what governs SHARDED's
OWN cliff) — Probe 6 already shows the cliff exists and is reachable at M/N~12.5,
corr>=0.85, so a 12-cell interpolation directly maps the transition width/sharpness
lit predicts should be sharp (cuckoo-hashing-like), at near-zero marginal cost since
it reuses already-bracketed anchor points rather than opening new N/F territory.
