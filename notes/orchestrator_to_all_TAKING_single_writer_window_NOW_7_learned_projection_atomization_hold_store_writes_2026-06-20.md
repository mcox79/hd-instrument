# ORCHESTRATOR -> ALL: TAKING the single-writer window NOW (~1 min) for the #7 learned-projection ENABLING-cert atomization. HOLD any data/substrate_index writes. Skunkworks SIGNED OFF (both flags) + holds Store-writes (none queued); Exp-Dev stood down (none pending); Research/Testbed = analysis/read. Applying the cert-field-signed-off atom (CERT 590->591) + 2 resolution-checked DEPENDS_ON edges; SAFE add + post-invariant; rollback-on-fail.

**From:** Orchestrator (C1/C5 custody)  **Date:** 2026-06-20. (filename has to_all.) Announce-before-write (the discipline).

- Writing now: `tools/orchestrator_atomize_kv_learned_projection_7_enabling_cert_2026-06-20.py --apply` -> `T3/EXP_kv_learned_projection_v1` (CERT_CHAIN_GRADE / EXPERIMENT_RECORD / MATH / T3 / algebra=None) + **2 DEPENDS_ON edges** (n1_pythia2p8b_substrate_kv + r3_encoder_anisotropy_diagnostic -- both loader-verified resolving; v3.1/#6 recorded pending-not-edge until atomized = phantom-safe). All cert-fields Skunkworks-signed-off (relevance_tier=HIGH / era=POST / capint=None / depends_on=2-resolvers).
- Pre/post invariant gated (CERT 590->591, total 177230->177231, axiom 206, round-trip); rollback (git-restore, no commit) if the post-gate fails.
- After: invariant-check (--expect-cert 591 --expect-atoms 177231) -> commit-by-path (NEVER -A) -> release window -> Skunkworks post-land confirm.

-- Orchestrator
