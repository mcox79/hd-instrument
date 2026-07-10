# Pillar-2 Native-Router — Build Spec (ready-to-dispatch) — 2026-07-10 (Director)

**Purpose:** turn the Pillar-2 design (notes/pillar2_native_router_geometric_design_2026-07-10.md) into a concrete, fair, build-ready cell spec so the routing front is ready to dispatch to exp_dev without a design delay. Same fairness discipline as the grounding cell.

## The wall (from the scour)

Our proven multi-hop traversal (chain-grade to ~50 hops) RIDES ON A PARTITION-ORACLE that hands the router which bank the next hop lives in. Every oracle-free router failed: closed-form 0.000, learned routers stuck at naive-centroid ~0.66, typed routing HURTS (0.44 vs 0.998), routing-geometry crashes at ingest scale. Root cause: router SNR ~ sqrt(N/M) collapses under memory load M; only the oracle escapes.

## The honest target (NOT oracle-free)

The brain's router is not oracle-free either (grid drifts + needs landmark recalibration; PFC supplies top-down goal bias). So the target is a NATIVE-LOCAL router + periodic EXTERNAL-REFERENT recalibration, that BEATS the sqrt(N/M) collapse where the dense/learned routers died. The specific bet: a LOW-RANK SR / spectral-basis router (grid cells = leading eigenvectors of M=(I-gamma T)^-1) is not a dense associative lookup, so it may survive load. NOTE: "low-rank avoids capacity collapse" is an UNTESTED cross-literature inference (the SR track and Hopfield-capacity track never intersect) -- so the cell's PRIMARY job is to MEASURE it, not assume it.

## The core claim to test (pre-register both bands)

A native router built from the low-rank normalized-SR / spectral basis (personalized-PageRank / random-walk-normalized, degree-invariant + anti-collapse by the same construction as the consolidation loop) routes multi-hop lookups WITHOUT the partition-label oracle, and its accuracy-vs-load curve STAYS ABOVE the dense/learned router's collapse curve at the same M.

## Arms
- ORACLE (partition-label handed): the current ceiling.
- DENSE/LEARNED router: reproduce the known collapse curve vs M (the baseline to beat).
- LOW-RANK SR / SPECTRAL router (the candidate): normalized-SR eigenbasis, top-k.
- DEGREE-ONLY POPULARITY baseline: pick highest-degree next-partition, no geometry.
- RANDOM: floor.

## Fair-test controls (mandatory -- same lens as grounding)
1. **Load sweep is the whole point:** vary memory load M and plot each arm's routing accuracy vs M. The claim is a CURVE separation (SR stays up where dense collapses), NOT a single-M number. Compute the info-ceiling: what's the best-possible routing accuracy given branching (E[1/k] for same-relation siblings), and score achieved/ceiling, never an absolute bar above the ceiling (the reader-multihop lesson).
2. **ORACLE-LEAK check (the killer control):** ablate/shuffle the partition-label channel -> the SR router must STILL route (if routing dies under label-shuffle, it was leaking the oracle). This is the routing analog of codes_necessary. HARD_FAIL if it leaks.
3. **DEGREE control:** the router must beat the degree-only popularity baseline AND be degree-invariant (route rare-partition targets as well as popular ones -- reuse the retest's degree strata). A router that only finds popular banks is the popularity shortcut again.
4. **RECALIBRATION-necessity:** if the design includes external-referent recalibration (drift correction), show it is load-bearing -- without it the router drifts and degrades over hops; with it, holds. Distinguishes "native+recalibrated" from "secretly still oracle'd."
5. **Real ingested KG, not synthetic chains** (scour constraint -- synthetic partition-oracle chains are exactly what we're trying to escape).
6. **Collapse discriminator** (shared with consolidation): the spectral basis must not degenerate to the trivial constant mode (effective-rank floor).

## Bands (pre-register numerically before running)
- HARD_PASS(native-router-real): SR router's accuracy-vs-M curve stays materially above the dense-collapse curve at high M AND survives label-shuffle (oracle-free) AND beats the degree baseline AND is degree-invariant AND achieved/ceiling is high AND no collapse.
- HARD_FAIL: SR collapses at the same M as dense (low-rank bought nothing -- the key negative result, still valuable) OR dies under label-shuffle (was leaking) OR ties the degree baseline (popularity, not routing) OR degenerates.

## Unification note (why this shares the consolidation machinery)
The SR/spectral router and the consolidation loop use the SAME normalized-Laplacian-with-restart operator (personalized PageRank = SR). If the consolidation engine validates (degree-invariant geometry), the router is the same operator applied to ROUTING (address) rather than CONTENT (concept placement). So Pillar-1-engine and Pillar-2-router may be one mechanism doing two jobs -- but each needs its own fair test; do not assume one from the other.

## Sequencing
Dispatch after (or parallel to) the fair-grounding cell, once a runner slot is free. exp_dev designs N/M-sweep-grid/k/seeds/exact-bands/data-source per the usual autonomy; this spec fixes only the claim, the arms, the fair-test controls, and the bands' SHAPE.
