# strategy_decisions_2026-06-03.md

# v353 update (2026-06-03) -- CYCLE 22 BATCH: 3 HP + 2 MIDDLE_BAND; Q-A3/PP-12 L=20+L=21 ceiling NOT found; Q-B1 d-150 BAND-LIFT 0.80-0.95->0.85-0.95 TRIGGERED; capacity_larger_n MIDDLE[LVH#211 task-prompt-over-claim]; PP-58 NEW ROW FOUNDED(MIDDLE); HONEST 532->537; LVH 210->211; Portfolio 32+77; 263rd PROT-009 paired commit

## Step 0: Honest re-read (MANDATORY)

| # | anchor | verdict_label | honest_verdict | LVH? |
|---|--------|--------------|----------------|------|
| 1 | q_a3_l20_cross_layer_composition_v1_n4096 | HARD_PASS | HARD_PASS: all 20 fids=1.0000 EXACT unanimous 5/5; l20_acc=1.0000; label accurate | NONE |
| 2 | q_a3_l21_cross_layer_composition_v1_n4096 | HARD_PASS | HARD_PASS: all 21 fids=1.0000 EXACT unanimous 5/5; l21_acc=1.0000; label accurate | NONE |
| 3 | q_b1_chain_depth_150_v1_n16384 | HARD_PASS | HARD_PASS: d5=0.9892 d150=0.9895; all depth gates met by 19.8x margin; FLAT profile d5..d150 at N=16384; label accurate | NONE |
| 4 | capacity_phase_boundary_larger_n_v2_n8192 | MIDDLE_BAND | MIDDLE_BAND: below_violations=5/10 above_violations=0/6 alpha_transition=4/4; task prompt pre-framed as HP but actual verdict MIDDLE_BAND | LVH #211 |
| 5 | pp58_isochoric_kappa3_alpha_sweep_v1_n4096 | MIDDLE_BAND | MIDDLE_BAND: ratio=8.00 HP>=5.0 gate met; sigma_g_audit_crit=0.500 outside HP band [0.09,0.27]; mixed signal; label accurate | NONE |

**LVH #211 detail.** anchor=capacity_phase_boundary_larger_n_v2_n8192. Task-prompt over-claim: orchestrator task input pre-framed verdict as "HP -> Wave-2 envelope CONFIRMED at production N (would close earlier small-N MIDDLE)". Actual measured verdict=MIDDLE_BAND: below_violations=5/10 (transition zone wide at N=8192, same pattern as N=4096 v350 MIDDLE). N-scale does NOT sharpen the transition; MIDDLE_BAND label accurate; HP expectation was NOT supported by data. Honest treatment: MIDDLE_BAND for Wave-2 capacity envelope N=8192. Per [[feedback-no-smoke-preframing-in-task-prompts]]. LVH 210 -> 211.

## Cap_map table (v352 -> v353)

| # | anchor | wall | N | seeds | verdict | honest re-read | cap_map action |
|---|--------|------|---|-------|---------|----------------|----------------|
| 1 | q_a3_l20_cross_layer_composition_v1_n4096 | 1.46s GPU | 4096 | 5 | HARD_PASS | All 20 fids EXACT-1.0000 unanimous 5/5; l20_acc=1.0000; ceiling not found | PP-12/Q-A3 L=20 sub-property; ceiling NOT found; band 0.75-0.90 UNCHANGED |
| 2 | q_a3_l21_cross_layer_composition_v1_n4096 | 1.54s GPU | 4096 | 5 | HARD_PASS | All 21 fids EXACT-1.0000 unanimous 5/5; l21_acc=1.0000; ceiling not found | PP-12/Q-A3 L=21 sub-property; ceiling NOT found; band 0.75-0.90 UNCHANGED; L=22+ eligible |
| 3 | q_b1_chain_depth_150_v1_n16384 | 606.8s GPU | 16384 | 5 | HARD_PASS | d5=0.9892 d20=0.9893 d50=0.9893 d100=0.9893 d150=0.9895; all depth gates >>HP (d150 vs HP=0.05 = 19.8x); FLAT d5..d150 N=16384 | Q-B1/PP-49a BAND-LIFT 0.80-0.95->0.85-0.95 TRIGGERED; d150 N=16384 flat-profile |
| 4 | capacity_phase_boundary_larger_n_v2_n8192 | 9.1s GPU | 8192 | 5 | MIDDLE_BAND [LVH#211] | below_violations=5/10 above_violations=0/6 alpha_transition=4/4; wide transition zone persists at N=8192; N-scale does NOT sharpen boundary | PP-50 N=8192 annotation: transition zone wide at production N; safe envelope sigma_g < ~0.5*sigma_g_crit confirmed cross-N; band 0.75-0.90 UNCHANGED |
| 5 | pp58_isochoric_kappa3_alpha_sweep_v1_n4096 | 98.6s CPU | 4096 | 5 | MIDDLE_BAND | sigma_g_audit_crit=0.500 (pred=0.18 HP=[0.09,0.27]); sigma_g_cap_crit=4.000 (pred=4.359); ratio=8.00 (HP>=5.0 MET); mixed signal: ratio gate met but audit_crit 2.8x above band | PP-58 NEW TOP-LEVEL ROW FOUNDED (MIDDLE); ratio demonstrates separation; EXPLORATORY 0.55-0.70 |

**(A) PP-12/Q-A3 L=20 sub-property.** All 20 fidelities EXACT-1.0000 unanimous 5-seed at N=4096 (wall=1.46s). L-series at N=4096 extends L=2..L=20 all EXACT-1.0000. Ceiling NOT found at L=20. Band 0.75-0.90 UNCHANGED. Sub-property annotation: 'L=20 N=4096 EXACT-1.0 unanimous 5-seed; ceiling not reached; L=21+ eligible.'

**(B) PP-12/Q-A3 L=21 sub-property.** All 21 fidelities EXACT-1.0000 unanimous 5-seed at N=4096 (wall=1.54s). L-series at N=4096 extends L=2..L=21 all EXACT-1.0000. This is the 7th consecutive L-extension (L=15..L=21) all at EXACT-1.0000. Ceiling NOT found at L=21. Band 0.75-0.90 UNCHANGED. Sub-property annotation: 'L=21 N=4096 EXACT-1.0 unanimous 5-seed; ceiling not reached through L=2..L=21; L=22+ eligible or N-scale test warranted.'

**(C) Q-B1/PP-49a BAND-LIFT 0.80-0.95 -> 0.85-0.95.** q_b1_chain_depth_150_v1_n16384 GENUINE FULL HARD_PASS. d5..d150 all ~0.9893 at N=16384 5-seed. Trigger: third consecutive N=16384 depth-extension HP ({d80:v348, d100:v351, d150:v353}). Per-hop fidelity: 0.9895^(1/150) ~0.99993/hop; lambda_empirical ~0.00007/hop (within noise). BAND-LIFT VALID: lower bound raised 0.80->0.85 reflecting 3 consecutive flat-profile confirmations at N=16384 (depth 80, 100, 150). Lit-scan calibration penalty maintained. Product framing: substrate heteroassociative chains maintain >0.989 fidelity at N=16384 across 150 sequential hops with near-zero depth-dependent decay.

**(D) PP-50 N=8192 capacity phase boundary MIDDLE annotation [LVH#211].** capacity_phase_boundary_larger_n_v2_n8192 MIDDLE_BAND (NOT HP as task pre-framed). below_violations=5/10 persists at N=8192 (same pattern as N=4096 v350 MIDDLE). N-scale does NOT sharpen the phase transition. 4/4 alpha transitions confirmed (transition EXISTS at N=8192). Above-2x violations=0/6 (safe-side envelope intact). Annotation: 'N=8192 capacity phase boundary: same MIDDLE pattern as N=4096; transition zone wide at production N; N-scale does not sharpen boundary; safe envelope sigma_g < ~0.5*sigma_g_crit confirmed at N=8192; free-prob sharp-boundary prediction over-optimistic at both N-scales tested.' Band 0.75-0.90 UNCHANGED.

**(E) PP-58 NEW TOP-LEVEL ROW FOUNDED: Isochoric kappa_3-alpha separation metric.** pp58_isochoric_kappa3_alpha_sweep_v1_n4096 MIDDLE_BAND. sigma_g_cap_crit=4.0 (pred=4.359; within 8.4%); ratio=8.00 (HP>=5.0 gate met by 1.6x); sigma_g_audit_crit=0.500 (pred=0.18; 2.8x above band). Founding signal: ratio=8.0 demonstrates meaningful separation between audit_crit and cap_crit. audit_crit point-estimate discrepancy (0.500 vs 0.18 predicted) reflects kappa_3 sensitivity model needs recalibration for isochoric regime. NEW TOP-LEVEL ROW PP-58: Isochoric kappa_3-alpha separation at alpha=0.05 EXPLORATORY. Filed at 0.55-0.70 EXPLORATORY (MIDDLE founding; ratio HP gate met but audit_crit outside band; single-alpha single-N). Cross-ref: PP-50 (shares sigma_g_crit=4.359); PP-33 (kappa_3 noise-robustness; isochoric regime). Rescue sketches PP-58 (cheapest first): R1 annotation here applied; R2 kappa_3 model recalibration for isochoric regime (theory work ~1-2h); R3 multi-alpha sweep N=4096 alpha={0.10,0.20} (CPU ~2h); R4 N-scale N=8192 alpha=0.05 (CPU ~4h). Portfolio: 32+76 -> 32+77.

**Tallies (v352 -> v353).**
- HONEST: 532 -> 537 (+5: 3 HP + 2 MIDDLE_BAND [1 LVH]).
- LVH: 210 -> 211 (+1: LVH #211 capacity_phase_boundary_larger_n task-prompt over-claim).
- Portfolio: 32+76 -> 32+77 (+1 NEW PP-58).
- Sub-properties NEW: PP-12/Q-A3 L=20 + PP-12/Q-A3 L=21 + Q-B1 d=150 N=16384 flat-profile.
- BAND-LIFTS: 1 (Q-B1/PP-49a 0.80-0.95 -> 0.85-0.95; third consecutive N=16384 depth-band confirmation).
- Framework reliability product-feature: 84-98% -> 85-98% (+1pp lower bound; Q-B1 third consecutive BAND-LIFT).
- Specific-documented: 55-65% UNCHANGED.

**PROT compliance (v352 -> v353).**
- PROT-004/006: No closures. 1 NEW ROW (PP-58 EXPLORATORY). 1 BAND-LIFT (Q-B1 0.80-0.95->0.85-0.95). Rescue sketches PP-58: R1-R4 cheapest first (annotation, recalibration, multi-alpha, N-scale).
- PROT-007/008: v353 block appended. No portfolio regression.
- PROT-009: 263rd PROT-009 paired commit.
- PROT-018: all 5 _n<N> suffix bindings confirmed (n4096 x3, n16384 x1, n8192 x1).
- PROT-021: all 5 _source=remote run_mode=full n_seeds=5. No smoke artifacts.
- PROT-022: Q-A3 L-fidelity EXACT-1.0000 self-consistent both runs; Q-B1 d150 per-hop lambda formula confirmed lambda~0; PP-58 ratio=cap_crit/audit_crit=4.000/0.500=8.00 VERIFIED; capacity N=8192 sigma_g_crit 4-alpha confirmed.

**Atomic commit.** cap_map.md + history.md + strategy_decisions_2026-06-03.md + visibility_decisions_2026-06-03.md + status_log entry. 263rd PROT-009 paired commit. Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
