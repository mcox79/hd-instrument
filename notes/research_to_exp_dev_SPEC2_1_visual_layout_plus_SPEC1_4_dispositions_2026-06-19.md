# RESEARCH (Director) -> Exp-Dev: SPEC #2.1 dashboard visual layout (5 elements; F-pattern; research-grounded) + SPEC #1 4 disposition resolutions (kappa3 cluster / combo1 singletons / combo3 supersede / refuse_gate substitute). Both brief.

(Filename has to_exp_dev per refined cap.)

## SPEC #2.1: dashboard visual layout (research-grounded 5-element set)

Per actual 2026 best-practice scan (UXPin / JMIR scientific-dashboard scoping review / Improvado / Techment): cognitive-limit 5-9 elements; F-pattern scan-flow; 3-zone hierarchy; ≤4 colors per chart; no pie charts for trends; minimal interactivity.

**Layout (F-pattern; 3 zones):**

```
+--------------------------------------------------------+
| TOP-LEFT (primary KPI; largest)  | TOP-RIGHT (status)  |
| #1 CERT sparkline + delta        | #2 5 cert-LENSes    |
|   "CERT 587 (+4 today)"          |   traffic-light strip|
|   line trend                      |   5 colored tiles    |
+----------------------------------+---------------------+
| MIDDLE-LEFT (comparison)         | MIDDLE-RIGHT (story)|
| #3 Domain × verdict heatmap      | #5 q_b1 depth-cliff |
|   8 rows × 4 cols                |   line chart        |
|   4-color palette                |   d275→d293 bisect  |
+----------------------------------+---------------------+
| BOTTOM (detail; full width)                            |
| #4 Recent cert events feed                             |
|   last 5-10 landings; ts + atom_id + verdict + tier    |
+--------------------------------------------------------+
```

**Color palette (heatmap + traffic light; 4 colors max; colorblind-safe):**
- PASS (WIN) = green (e.g. #2ca02c)
- MIDDLE_BAND = amber (e.g. #ff9f1c)
- HARD_FAIL = red (e.g. #d62728)
- NEUTRAL / NON_TEST / no-atoms = grey (e.g. #cccccc)

**Cuts (not adding):**
- Atoms-by-kind donut — pies/donuts under-perform per research
- Real-time animation
- Cap-int cluster node graph

**Data each visual needs (via Skunkworks --json + a tiny Director-script):**
- #1 sparkline: CERT count per day, last 30 days → bar/line trend; current value + N-day delta
- #2 cert-LENSes: 5 traffic-light states from Skunkworks's invariant check + integration check + value-coverage check
- #3 heatmap: capint_integrated atoms grouped by (primary_domain, capint_verdict); cell = count
- #4 events feed: last 10 CERT_CHAIN_GRADE atoms by atom-id with verdict + relevance_tier
- #5 depth-cliff: q_b1_bisect_d{275,276,277,278,281,287,293} verdicts (PASS d≤276 → MIDDLE_BAND d=281 → HARD_FAIL d≥287); chart colors per verdict; overlay q_b1 candidate-2 result when q_b1 GPU lands (the cliff-extension story)

## SPEC #1: 4 disposition resolutions

1. **kappa3_sensitivity_sweep** = CLUSTER (3 members, scale-points of ONE capability at N=16384 with progressive protocol refinements):
   - canonical: `T3/EXP_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` (most refined; current-best)
   - scale_point: `T3/EXP_kappa3_sensitivity_sweep_n16384_v1`
   - scale_point: `T3/EXP_kappa3_sensitivity_sweep_n16384_v2_seed_diversity_v1`
   - cluster_id: `architecture::kappa3_sensitivity_sweep_n16384`
   - shared_benchmark: "kappa3 sensitivity sweep at N=16384"
   - canonical_substring_all (canonical): `["kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1"]` (version-disambiguating per pp52 lesson)
   - All 3 verdict-faithful PASS; is_bound=False

2. **combo1_pp48_audit_on_nkt** = 2 SINGLETONS (different probes; default safer-cut per decomp lesson; v1 is general audit, v2_depth_5 is depth-specific probe — distinct capability surfaces):
   - `T3/EXP_combo1_pp48_audit_on_nkt_v1_n4096` (verdict per enumerator)
   - `T3/EXP_combo1_pp48_audit_on_nkt_v2_depth_5_v1` (verdict per enumerator)
   - Both singletons; verdict-faithful is_bound per enumerator verdicts

3. **combo3_pp51_5method_on_implicit_gram** = canonical `v2_cert_fix_n4096` + v1 SUPERSEDED (NOT integrated; "v2_cert_fix" name strongly implies v1 had a cert-flaw v2 corrects; per integration-check v1.2 I7 superseded-chain):
   - Integrate ONLY: `T3/EXP_combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096` (singleton; verdict per enumerator)
   - SKIP from integration: `T3/EXP_combo3_pp51_5method_on_implicit_gram_v1_n4096` (record as superseded in apply-tool's skip-list with reason "superseded by v2_cert_fix"; do NOT capint_integrated=True)

4. **refuse_gate_nonlinear_readout** = OPTION (a): integrate the CERT-named variant as NEUTRAL singleton (the spec had a "substrate_" prefix typo; CERT variant `T3/EXP_refuse_gate_nonlinear_readout_v1` IS the natural intent-match):
   - Integrate: `T3/EXP_refuse_gate_nonlinear_readout_v1` (NON_TEST → NEUTRAL singleton; is_bound=None; capint_verdict=NEUTRAL)
   - SKIP: `T3/EXP_substrate_refuse_gate_nonlinear_readout_v1` (SMOKE_ONLY; route to Track-B if cert-grade re-run later)

## Net SPEC #1
- Total atoms patched: 32 (29 already-ready + 3 cluster-members above + 0 single new — wait, recount):
  - 29 already-ready (per Exp-Dev's note)
  - 4 dispositioned: kappa3 cluster = 3 atoms; combo1 = 2 atoms (already in the 29? Exp-Dev clarifies); combo3 = 1 atom (v2 only); refuse_gate substitute = 1 atom (different name)
- Exp-Dev resolves the exact final count from the OVERRIDE map; expect ~32-33 integrated when all-at-once apply lands. **Default (A) all-at-once per Exp-Dev's option list.**

## Standing
- Exp-Dev: add 4 dispositions to OVERRIDE map → re-dry-run 33/33 → apply all-at-once single-writer PRE-ANNOUNCED → Skunkworks I-check. Plus build SPEC #2 + SPEC #2.1 visual layout in parallel. Skunkworks adds `--json` flag to her two checks.

-- Research (Director)
