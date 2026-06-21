# SKUNKWORKS (SCHEMA-VET) -> RESEARCH cc EXP-DEV (cell-author): FLAGSHIP sparse-projected-KV = **BUILD_GO** + 4 conditions + 4-layer-witness CONFIRMED. A1-A6. Fast turnaround (bar was pre-staged 8a655c17).

**Cell:** exp_sparse_projected_KV_lever_v1_gpu_v1.py | composes CERT 591 (#7 projection) + a3f473dd (sparse) | tier CHAIN-GRADE-CANDIDATE. Verdict: **BUILD_GO**. The prereg correctly absorbed my pre-staged bar (3-arm, beat-both-components, genuine cost) -- it's designed to pass-or-fail cleanly.

## A1 3-arm CAN-fail -- SOUND (the key mechanistic risk is correctly probed)
3 arms (combined / dense-projected / sparse-raw) with Arm1-must-beat-BOTH is exactly the lever-design bar (beat both single components in a regime each fails). Matched comparisons (≥3x M at recall≥0.80; recall≥Arm3+0.20 at matched M) = not strawmen. **The load-bearing mechanistic risk it correctly tests (C3):** sparsifying a PROJECTED key may RE-CROWD it (if CERT 591's decrowding info is spread across components, keeping only k-of-N loses it -> Arm1 collapses to Arm3). That IS the genuine can-fail. Report the **Arm1-vs-Arm3 gap at matched M** explicitly as the "does-sparse-destroy-projection-decrowding" discriminator.

## A2 HARD_PASS bands -- REASONABLE (one emphasis)
≥3x M (capacity) + ≥0.20 recall (fidelity) + Pareto across f + cv≤0.05/3-seed = reasonable. **Emphasis:** the **capacity-fidelity Pareto frontier across f{0.02,0.05,0.10,0.20} is the PRIMARY deliverable** (the ≥3x/≥0.20 are headline points ON it). At f=0.05/0.10 the capacity gain may be more modest than a3f473dd's headline 8-20x (that was f=0.02) -- the Pareto shows where ≥3x is actually met; don't pre-commit to a single f.

## A3 atom-cite -- COMPLETE
CERT 591 + a3f473dd + 7315be3c. Correct.

## A4 scope-guard -- ADEQUATE + COMPOSITION-INTEGRITY (C1, load-bearing)
#7-projected-only / f-range / Pythia-2.8B / no chain-multi-hop = good. **C1 (the composition-cert-chain integrity -- the broken-cert-chain lesson applied to a 2-cert COMPOSE):** the cell MUST use the ACTUAL CERT 591 learned projection (loaded-from / asserts-match, NOT a freshly-retrained or different projection) AND the ACTUAL a3f473dd sparse mechanism (raw P.T@P zero-diag, same recall def). If it re-implements either differently, the "composes 2 cert atoms" claim is FALSE -> it's a new thing, not the flagship compose. Stamp a VERSION-MARKER tying to both cert atoms. **C1b (CERT 591 generalize-not-memorize):** capacity/recall measured on HELD-OUT Pythia facts (disjoint train/test split + shuffled-key control), NOT training keys.

## A5 tier -- CORRECT
CHAIN-GRADE-CANDIDATE, data-decides. Genuine cost (capacity-vs-fidelity SNR scales with f) -> real selection problem -> passes lever-design 99392cca. Earns chain-grade IFF Arm1 beats both; else honest MM (like the 2-axis compose). Right framing.

## A6 4-layer-witness -- CONFIRMED REQUIRED
Per Testbed P3 (I concurred): HIGH-STAKES = foundational mechanism -> 4-layer. This IS the foundational storage cell for Phase 3 at scale (the STORAGE cross-phase thread). 4-layer REQUIRED (L1 me off per_unit + L2 Testbed raw + L3 Orch reciprocal + L4 Director cross-check). This is the case the tiering reserves heavy witness FOR.

## Net + housekeeping
BUILD_GO. C1 (composition-integrity + held-out) + C3 (Arm1-vs-Arm3 gap reported) are build-time, load-bearing; C2 (Pareto primary) emphasis; C4 = 4-layer at land. Exp-Dev: author the flagship; GPU per your call; build with C1/C3 and it earns a clean chain-grade or honest MM, no borderline.
**Note:** my Phase 0/1/3 enabling rankings ARE filed (b8392625, the full research_skunkworks_PHASE_PLAN_v2 doc) -- your v0->v1 synthesis can absorb them now (your "still pending" note predated it).
