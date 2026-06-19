"""Atomic cap_map update: PP-12 band 0.90->0.91, append v376 history block."""
import pathlib, os

path = pathlib.Path('d:/AI/hd-instrument/notes/substrate_capability_map.md')
text = path.read_text(encoding='utf-8')

old_band = '**0.87-0.97** (v372 BAND-LIFT: L=63 N=16384 NEW DEEPEST project history; 44-rung series {L=20..L=63} EXACT-1.0000; L=38 N=8192 NEW N=8192 DEEPEST; 18-rung N=8192 series {L=19,L=22..L=38}; 8-rung batch [4 N=16384 + 4 N=8192]; ceiling NOT found either N; v371 +0.01 [4-rung L=58..L=59+L=33..L=34] + v372 +0.01 [8-rung L=60..L=63+L=35..L=38])'
new_band = '**0.91-0.97** (v376 BAND-LIFT: L=94 N=16384 NEW DEEPEST project history; 75-rung series {L=20..L=94} EXACT-1.0000; L=58 N=8192 NEW N=8192 DEEPEST; 38-rung N=8192 series {L=19,L=22..L=58}; 15-rung batch [7 N=16384 + 8 N=8192]; ceiling NOT found either N; lift trajectory v371+v372+v373+v374+v375+v376 = 0.85->0.91 six consecutive +0.01 lifts)'

count = text.count(old_band)
print(f'Found old_band {count} time(s)')
text2 = text.replace(old_band, new_band, 1)

v376_block = r"""
# v375 -> v376 (2026-06-04) -- CYCLE 44 LARGE BATCH: 15 HP + 2 MIDDLE_BAND + 1 HF; 0 LVH; Q-A3 L=88..94 N=16384 (rungs 69-75; L=94 NEW DEEPEST project history; {L=20..L=94} 75-rung series); Q-A3 L=51..58 N=8192 (rungs 32-39; L=58 NEW N=8192 DEEPEST; {L=19,L=22..L=58} 38 rungs); BAND-LIFT PP-12/Q-A3 0.90-0.97->0.91-0.97 (15-rung batch); PP-58 SCS extended_d MIDDLE_BAND (3/6 in-range; SCS valid low-load alpha<=0.06); PP-58 SCS d_sweep MIDDLE_BAND (monotone d confirmed; spike over-calibrated alpha>=0.07); spectral_monitor_overfitting HF (sub fires step=200 3/3; scale gate); HONEST 685->703; LVH 213; Portfolio 32+77 UNCHANGED; 287th PROT-009 paired commit

## v375 -> v376 (2026-06-04) Cycle 44 large batch; 15 HP + 2 MID + 1 HF; 0 LVH; Q-A3 L=88..94 N=16384 (rungs 69-75; L=94 NEW DEEPEST) + Q-A3 L=51..58 N=8192 (rungs 32-39; L=58 NEW N=8192 DEEPEST); BAND-LIFT PP-12/Q-A3 0.90-0.97->0.91-0.97; PP-58 SCS 2x MID; spectral_monitor_overfitting HF (scale gate); HONEST 685->703; LVH 213; Portfolio 32+77; 287th PROT-009 paired commit

**Cap_map row changes (v375 -> v376).**

| Capability | v375 status | v376 status | Triggering anchors |
|---|---|---|---|
| PP-12/Q-A3 cross-layer composition | 0.90-0.97 | **0.91-0.97** | q_a3_l88..l94 N=16384 + q_a3_l51..l58 N=8192 (15-rung batch; L=94 NEW DEEPEST project history) |

**Anchor table (v376):**

| # | Anchor | Runner | N | Seeds | Verdict | Key metric | Cap_map impact |
|---|---|---|---|---|---|---|---|
| 1 | q_a3_l88_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 88 levels EXACT-1.0000 5/5 | PP-12/Q-A3 L=88 rung 69 |
| 2 | q_a3_l89_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 89 levels EXACT-1.0000 5/5 | PP-12/Q-A3 L=89 rung 70 |
| 3 | q_a3_l90_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 90 levels EXACT-1.0000 5/5 | PP-12/Q-A3 L=90 rung 71 |
| 4 | q_a3_l91_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 91 levels EXACT-1.0000 5/5 | PP-12/Q-A3 L=91 rung 72 |
| 5 | q_a3_l92_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 92 levels EXACT-1.0000 5/5 | PP-12/Q-A3 L=92 rung 73 |
| 6 | q_a3_l93_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 93 levels EXACT-1.0000 5/5 | PP-12/Q-A3 L=93 rung 74 |
| 7 | q_a3_l94_cross_layer_composition_v1_n16384 | GPU | 16384 | 5 | HARD_PASS | All 94 levels EXACT-1.0000 5/5; NEW DEEPEST | PP-12/Q-A3 L=94 rung 75; BAND-LIFT 0.90->0.91 |
| 8 | q_a3_l51_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 51 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=51 rung 32 |
| 9 | q_a3_l52_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 52 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=52 rung 33 |
| 10 | q_a3_l53_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 53 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=53 rung 34 |
| 11 | q_a3_l54_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 54 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=54 rung 35 |
| 12 | q_a3_l55_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 55 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=55 rung 36 |
| 13 | q_a3_l56_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 56 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=56 rung 37 |
| 14 | q_a3_l57_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 57 levels EXACT-1.0 5/5 | PP-12/Q-A3 L=57 rung 38 |
| 15 | q_a3_l58_cross_layer_composition_v1_n8192 | GPU | 8192 | 5 | HARD_PASS | All 58 levels EXACT-1.0 5/5; NEW N=8192 DEEPEST | PP-12/Q-A3 L=58 rung 39; N=8192 DEEPEST |
| 16 | pp58_scs_extended_d_sweep_v1_n8192 | CPU | 8192 | 3 | MIDDLE_BAND | 3/6 alphas in-range; d_range=1.3-1.8; SCS valid alpha<=0.06 | PP-58 MID annotation |
| 17 | pp58_scs_d_sweep_v1_n8192 | CPU | 8192 | 3 | MIDDLE_BAND | d monotone=True; spike_alphas=[0.075..0.13] ratio outside [0.7,1.3] | PP-58 MID monotone sub-property |
| 18 | substrate_spectral_monitor_overfitting_v1_n4096 | CPU | 4096 | 3 | HARD_FAIL | val_overfit=None 0/3; sub_overfit_step=200 3/3; scale gate | Spectral monitor HF rescue R1 |

**(A) PP-12/Q-A3 BAND-LIFT: 0.90-0.97 -> 0.91-0.97 (rungs 69-75 N=16384 + 32-39 N=8192; 15-rung batch; L=94 NEW DEEPEST project history).**
All 7 N=16384 anchors (L=88..94): EXACT-1.0000 unanimous 5/5 seeds. N=16384 series: {L=20..L=94} = 75 contiguous rungs. L=94 NEW DEEPEST project history (prior L=87 v375; +7 rungs). Ceiling NOT found. All 8 N=8192 anchors (L=51..58): EXACT-1.0 unanimous 5/5 seeds. N=8192 series: {L=19,L=22..L=58} = 38 rungs. L=58 NEW N=8192 DEEPEST (prior L=50 v375; +8 rungs). 2-N cross-N confirmed at L=51..58. BAND-LIFT: 15-rung batch exceeds 4-rung threshold. +0.01 lower bound. Upper 0.97 ceiling unchanged. Lift trajectory: 6 consecutive +0.01 lifts (v371-v376 = 0.85->0.91). Product framing: substrate cross-layer composition holds EXACT-1.0000 fidelity through 94 levels at N=16384; 75-rung unbroken series; audit API algebraic moat structurally unbounded through L=94; no ceiling found at either N.

**(B) PP-58 SCS partial validity characterised (2x MIDDLE_BAND).**
extended_d_sweep: SCS formula valid at low-load alpha<=0.06 (3/6 alphas in-range; ratio 0.82-1.30); over-estimated at alpha>=0.08 (ratio 1.40-1.64). d_sweep R2: d monotone vs alpha confirmed (d=1.20 at alpha=0.01 to d=1.84 at alpha=0.13; 3 seeds); spike at alpha>=0.075 but ratio outside [0.7,1.3] (SCS over-calibrated at high load). PP-58 band 0.55-0.70 UNCHANGED. Sub-property annotation added: SCS valid alpha<=0.06 N=8192 (low-load regime); over-calibrated alpha>=0.07; d monotone confirmed.

**(C) substrate_spectral_monitor_overfitting_v1_n4096 HARD_FAIL scale gate.**
val_overfit_step=None 0/3 seeds (LM never reached overfitting at TRAIN_CHARS=30000). sub_overfit_step=200 all 3 seeds (substrate spectral signal fires consistently). HARD_FAIL per pre-reg. Rescue R1 (BEST-RESCUE): increase TRAIN_CHARS to 100000-200000 + N_STEPS to 5000-10000; substrate signal is present. R2: N_OBS=8192. R3: smaller LM_HIDDEN.

- PROT-004/006: No closures. 0 new rows. 1 BAND-LIFT (PP-12/Q-A3 0.90->0.91). PP-58 2x MID annotations. HF rescue R1-R3 cheapest-first.
- PROT-007/008: v376 block appended. Portfolio 32+77 UNCHANGED.
- PROT-009: 287th PROT-009 paired commit.
- PROT-018: 18 anchors verified. 0 PROT-018 violations.
- PROT-021: all 18 source=remote run_mode=full. No smoke artifacts.
- PROT-022: Q-A3 consistent {L=20..L=94} 75 rungs; {L=19,L=22..L=58} 38 rungs; pp58 alpha=0.06 mean_ratio=1.293; spectral_monitor sub_overfit_step=200 3/3 seeds consistent.

Cap map: v375 -> v376 CYCLE 44 LARGE BATCH (15 HP + 2 MID + 1 HF; 0 LVH; Q-A3 N=16384 75-rung series L=94 NEW DEEPEST; Q-A3 N=8192 38-rung series L=58 NEW N=8192 DEEPEST; BAND-LIFT PP-12/Q-A3 0.90-0.97->0.91-0.97 15-rung; PP-58 SCS 2x MID partial-validity characterised; spectral_monitor_overfitting HF scale-gate R1-R3; HONEST 685->703; LVH 213; Portfolio 32+77; 287th PROT-009 paired commit) (2026-06-04)
"""

text2 = text2 + v376_block

tmp = path.with_suffix('.tmp')
tmp.write_text(text2, encoding='utf-8')
os.replace(tmp, path)
print(f'Done. Band replaced: {count} time(s). Total lines: {len(text2.splitlines())}')
