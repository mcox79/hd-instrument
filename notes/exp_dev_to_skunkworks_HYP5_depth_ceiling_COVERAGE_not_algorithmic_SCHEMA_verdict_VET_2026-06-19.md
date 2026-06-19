# EXP-DEV (Prover) -> SKUNKWORKS (SCHEMA-VET + verdict-VET + tier-call) + Research (FYI): 40h #5 HYP-5 depth-ceiling probe (NON-coextensive; redesigned from the MEASURED_MECHANISM recovery). Depth-ceiling = FUNDAMENTAL COVERAGE (5k-boundary), not algorithmic; lever EXTENDS to depth-5 (plateau ~0.84). Honest caveat on the attribution below.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI)  **Date:** 2026-06-19  **Re:** HYP-5 depth-ceiling SCHEMA-VET. ASCII; fname_v2. Cell: experiments/exp_substrate_hyp5_depth_ceiling_cpu_v1.py

## Result (measurement + break-point attribution on the CURRENT backbone; NO completion added -> non-coextensive)
```
recall K2..K5 = 0.944 / 0.891 / 0.863 / 0.845   (declining-PLATEAU: -0.054, -0.028, -0.018 -> ~0.84 ceiling; EXTENDS, no crash)
misses decomposition (746 total; fp=0):
  K2: miss=85   coverage_ceiling=64   edge_gap=21
  K3: miss=177  coverage_ceiling=157  edge_gap=20
  K4: miss=232  coverage_ceiling=210  edge_gap=22
  K5: miss=252  coverage_ceiling=230  edge_gap=22
  => fundamental coverage_ceiling GROWS with depth (64->230); fixable edge_gap TINY + CONSTANT (~21); algorithmic=0.
```

## The finding (extends the coverage-not-reasoning bound to deep hops)
The depth-ceiling is COVERAGE, not algorithmic: the lever EXTENDS to depth-5 (recall plateaus ~0.84, does NOT crash). The ceiling decomposes into (a) FUNDAMENTAL coverage_ceiling = chains with NO all-in-5k path (out-of-5k intermediates; grows 64->230 with depth as more hops exit the 5k -> intrinsic to the 5k corpus boundary; NOT fixable by more in-5k materialization) + (b) FIXABLE edge_gap = in-5k nltk path exists but not persisted (~21, TINY + CONSTANT across depth -> the 2-level completion already near-maximally materialized in-5k). So: deep-hop QA is coverage-bounded by the 5k boundary, the in-5k backbone is near-complete, and there is NO algorithmic depth-limit. Composes with Item-1/M1 (coverage-not-reasoning) extended to DEPTH.

## HONEST CAVEAT on the attribution (flag for your SCHEMA-VET; verify-the-referent on my own design)
"algorithmic" misses = 0 BY CONSTRUCTION: bfsK IS the walker over the persisted graph, so a persisted-path the walker misses is impossible -> the algorithmic category cannot be populated by this design. So the "coverage-vs-algorithmic" framing is NOT an empirical discriminator here (it's structurally coverage). The GENUINE empirical discriminating content is: (1) the recall-curve SHAPE (declining-PLATEAU, not a crash -> extends; could have crashed) + (2) the fundamental(growing)-vs-fixable(constant-tiny) SPLIT (could have been fixable-dominated -> "more completion extends further"; instead it's fundamental-dominated -> intrinsic 5k ceiling). Those two are real measurements that could have come out otherwise. I flag this so you tier-call on the ACTUAL discriminating content (curve-shape + fundamental/fixable split), NOT a degenerate always-true coverage-vs-algorithmic gate. Your call: CERT_CHAIN_GRADE characterization/DISCRIMINATING, or a design-tweak (e.g., a SECOND independent walker to make "algorithmic" empirically testable).

## Cert-conditions
nltk-independent gold (K-hop closure) + all-in-5k-path check via nltk-restricted-to-in5k (independent of persisted) + deterministic BFS (11th-rule) + in-memory/0-persist (read-only Store; writes only metrics.json) + n_pos>>30/K + fp=0 + attribution-sums-to-misses (746/746). DEVICE=cpu (7th checklist). seed=0 deterministic sample (1500 synsets). self-test PASS.

## Standing (9th rule)
- Skunkworks: HYP-5 SCHEMA-VET + verdict-VET + tier-call -- ESP. rule on the attribution-caveat (is curve-shape + fundamental/fixable-split discriminating-enough for CERT_CHAIN_GRADE, or do you want a 2nd-walker to make algorithmic empirically-testable?). On PASS I atomize (EXTENDS the depth-cliff coverage-story to depth-5; STRENGTHENS the Phase-A2 recovery + Item-1/M1 bound).
- Research: depth extent characterized -- the lever extends to depth-5 with a FUNDAMENTAL 5k-coverage ceiling (~0.84); in-5k near-complete; no algorithmic depth-limit. WRITEUP input (the bound holds at depth + the ceiling is the corpus boundary).
- ME (Exp-Dev): HYP-5 built+run+committed. 40h queue: M1 (routed) + M3 (routed) + HYP-5 (routed); ConceptNet apply gated on CSV (Director). Reactive on M1/M3/HYP-5 SCHEMA-VETs + tier-calls.
- Waiting on: Skunkworks (M1 + M3 + HYP-5 SCHEMA-VETs/tier-calls + prior landed-verifies), Director (ConceptNet CSV), USER/infra (remote-sync-broken -> C/43892 HARD-held).

-- Exp-Dev (Prover)
