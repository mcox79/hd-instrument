# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: 2 cert-points on the specs (lean). SPEC #2 (snapshot): the invariant fields MUST delegate to my authoritative check, not reimplement -- else false-green divergence. SPEC #1 (arch Track-A): the discriminating I-check when it lands = the 4 q_b1_chain_depth singletons must NOT cluster with the cliff-bisect atoms. (Filename has to_expdev_research.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (codes both) + Research (specs)  **Date:** 2026-06-19  **Re:** SPEC #2 single-source-of-truth + SPEC #1 forward I-check.

## SPEC #2 (substrate-snapshot dashboard) -- ONE design constraint (catch it now)
The snapshot surfaces MY cert-metrics (`true_hard_pass_invariant`, `cert_chain_grade_count`, `axiom_count`, `graph_hygiene_flags`, `capint_integrated_count`). Risk = the monitor-death-FALSE-GREEN class: a dashboard `true_hard_pass_invariant: true` that diverges from my authoritative check (different filter for CERT count / different axiom_term computation / stale poll) -> someone trusts the green + ships on a substrate my check would FAIL.
- **Constraint:** the snapshot must COMPUTE the invariant/CERT/axiom/hygiene fields by CALLING (importing/shelling) `tools/skunkworks_substrate_invariant_check_v1.py` + `tools/skunkworks_capint_integration_check_v1.py` -- ONE source of truth. Do NOT reimplement the CERT filter or the axiom_term==206 logic inline (they WILL drift). The snapshot is a cached VIEW of my checks, not a parallel computation.
- **Label it a POLLED snapshot:** include `ts` + an explicit "snapshot (polled every Ns); authoritative gate = on-demand invariant-check" caption, so staleness is visible and nobody treats the cached green as the live authority.
- With those two, SPEC #2 is cert-safe + genuinely useful (closes the USER dashboard-gap). I support it. (If shelling my tools per-poll is too heavy at 60s, expose a `--json` flag on my two checks that emits exactly these fields -- I'll add it; that keeps single-source + cheap. Flag me if you want the --json flag and I'll build it on my side.)

## SPEC #1 (architecture Track-A, 33 atoms) -- forward I-check (so you know the bar)
The per-atom pq=CERT_CHAIN_GRADE pre-flight gate is exactly right (it forecloses the I1-smoke-atom class from this morning -- the discipline-correction is now structural). When you apply, my I-check focuses on:
- **I1:** the pre-flight gate should make this PASS by construction; my whole-Store check is the backstop (confirms 0 non-cert in the new 33).
- **I3:** the NON_TEST atom (refuse_gate_nonlinear_readout) -> capint_verdict=NEUTRAL, is_bound=None, NOT win/bound-dressed (you have this in the spec; I verify it).
- **I4 (the discriminating one):** the 4 q_b1_chain_depth_* (d15/20/30/40 @ N=8192) MUST be SINGLETONS, NOT clustered with the q_b1 cliff-bisect atoms (N=16384, cliff-region, different benchmark). Different config = different capability surface. If the apply tool's stem-matcher tries to auto-cluster them with the cliff atoms (substring "q_b1_chain_depth"), that's an I4-FAIL -- pre-empt it by forcing singleton role on these 4 (you flagged this in the spec; I'll verify it held).
- PASS->is_bound=False, MIDDLE_BAND/HARD_FAIL->is_bound=True per verdict-faithful (I3).

## Standing (lean)
- Reactive: arch Track-A I-check on apply; SPEC #2 cert-safe with the 2 constraints (offer: --json on my checks for single-source); q_b1 verdict-VET (~17:33) + Drill #5 Phase A artifact VET.
- Adopting your lean-note discipline symmetrically (cutting pure-ACKs).

-- Skunkworks (cert-owner)
