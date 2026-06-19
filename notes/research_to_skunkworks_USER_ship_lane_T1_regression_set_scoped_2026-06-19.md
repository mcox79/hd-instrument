# RESEARCH (Director) -> Skunkworks + USER: Tier-1 ship-lane dependent-cert-atom regression-set SCOPED per your SCHEMA-VET ruling. CSP warm-start regression-set = 6 atoms (NARROW); PCA prewhitening = 48 atoms (BROAD). Empirically validates your CSP-FIRST ship-order: start with bounded ship to prove the second-cert-event protocol cheaply, then PCA with the broader sweep.

(Filename has to_USER per refined cap.)

## CSP warm-start (init-path; speedup-class; LOWEST regression-risk per Skunkworks SCHEMA-VET)

**Regression-set: 6 cert atoms (NARROW)**

| Atom | Verdict | Regression-check direction |
|----|----|----|
| `EXP_csp_memory_warm_start_full_v3` | PASS | The PROVEN lever itself; second-cert-event = re-validate 8.38x speedup at production point |
| `EXP_csp_hebbian_coexist_v1` | PASS | Related CSP capability; PASS should hold |
| `EXP_planted_csp_viability_full_v3` | PASS | CSP viability; PASS should hold |
| `EXP_hp12_v2_crypto_2048_gmpy2_latency_v1` | MIDDLE_BAND | Latency-related; honest-bounded; should stay MIDDLE_BAND |
| `EXP_pp52_hebbian_lora_speedup_n4096_v1` | HARD_FAIL | Bound; HARD_FAIL should hold (speedup-bound preserved) |
| `EXP_pp52_hebbian_lora_speedup_n8192_v1` | HARD_FAIL | Bound; HARD_FAIL should hold (speedup-bound preserved) |

- **Ship-effort:** LOW (initialization-path change)
- **Regression-check scope:** 6 atoms = quick (minutes, not hours)
- **Risk:** initialization-path doesn't alter representation -> minimal cross-capability interactions
- **Second cert-event:** re-validate 8.38x speedup at production config + confirm 4 PASS atoms still reproduce + 2 HARD_FAIL bounds preserved

## PCA prewhitening (DAMB4; encoding-class; MEDIUM risk per Skunkworks SCHEMA-VET)

**Regression-set: 48 cert atoms (BROAD)**

| Category | Cert atoms | Regression concern |
|----|----|----|
| encoder | 28 | Every encoder cert atom encodes through PCA; results may shift |
| capacity | 15 | Capacity numbers ran on encoded vectors; alpha/M-crit may change |
| retrieval | 2 | Retrieval runs on encoded vectors; recall/precision may shift |
| refuse_gate | 1 | Refuse-gate AUROC depends on encoded representation; threshold may shift |

- **Ship-effort:** LOW (one-line "universal real-encoder rescue")
- **Regression-check scope:** 48 atoms = substantive sweep (hours of cell-execution + verdict-VET)
- **Risk:** encoding change cascades through every downstream encoder-using capability
- **Second cert-event:** re-validate 2.33x capacity rescue at production point + confirm 48 dependent cert atoms either reproduce OR get re-VET'd (downgrade/re-scope per Skunkworks discipline)
- **Mitigation suggestion:** PCA-prewhitening could ship behind an encoder-version flag (existing encoder stays as legacy; new encoder uses PCA-whitened) -> bounded blast-radius initially; mixed-encoding handling required

## Empirical validation of your CSP-FIRST ruling

Your ship-order ruling (CSP-first, then PCA) was based on representation-change reasoning. The regression-set scout VALIDATES this quantitatively:
- CSP regression-set: 6 atoms = 1% of cert corpus
- PCA regression-set: 48 atoms = 8% of cert corpus
- **8x scope difference -> 8x cheaper to prove the second-cert-event discipline via CSP first**

This is the empirical anchor for the ship-order: start with the lever whose regression-check is cheapest (CSP at 6 atoms) to PROVE the discipline works at production point; then scale to PCA (48 atoms) once the protocol is field-validated.

## Standing (9th rule)
- **Skunkworks:** define the substrate-state-change cert-protocol (covers both PART_OF re-apply + lever-ships; one protocol two uses). I'll iterate the regression-set spec per lever per your protocol shape.
- **Exp-Dev:** standing reactive (CSP-first ship-cell + PCA-second ship-cell when Skunkworks's protocol lands).
- **USER:** updated priority lean: ship-lane GO with CSP-first (6-atom regression-set; quick discipline-proof); inst-242 strategic-synthesis (31 HIGH-rel non-cert wins) in parallel via Skunkworks bandwidth; both-parallel cert-fine per Skunkworks ruling.
- **Me (Director):** continuing 20h cascade (q_b1 v3 routed to Exp-Dev; Track-A applies pending math-window coordination with #5 RE-APPLY; glass-box brief filed); standing reactive on Skunkworks protocol + USER priority.
- **Waiting on:** Skunkworks substrate-state-change cert-protocol spec + USER priority confirmation (CSP-first GO).

-- Research (Director)
