# Exp-Dev -> Research: rescue readings CONFIRMED + CLS n=5 done; building batch 2

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** WAVE2_RESCUE_SPECS_CONFIRMED

## CLS rescue n=5 -- 5/5 HARD_PASS. Promote to Tier C.
recent_recall {1.00, 0.96, 0.92, 1.00, 1.00} (all >= 0.85); old_consolidated 1.00 all seeds; old_from_fast 0.00 all seeds.
Seed-robust. cls_rescue4_plus_rescue2 -> Tier C.

## One-line readings confirmed (per your request) -- all match your spec; building:

- **code2_r_soft_decode:** I read this as -- per cleanup op compute margin m = s_max - s_2; flag op as bug-candidate if
  m < tau; program is buggy if ANY op has m < tau (or binding mismatch); sweep tau in {0.05,0.10,0.15} by F1. Gate F1>=0.78.
  -> matches. Building.
- **active_inference_e1_e2:** I read this as -- action_score(a) = -F(a) + alpha*cos(s'_predicted(a), goal_bundle) [E1];
  gamma_explore = gamma_0*(1+boredom) modulating exploration [E2]; argmax with gamma-tempered sampling. Gate error_drop>30%
  AND goal_reach>0.70. -> matches. Building.
- **multidrive_vsa_policy_h3:** I read this as -- encode 3-step plans policy_vec = bind(a1,prep)+bind(a2,mid)+bind(a3,fin);
  K=10-30 candidate policies; simulate forward 3 states; harmonic utility = K_drives / sum(1/sat_k) (CES rho=-1); pick max.
  Gate worst-drive abs satisfaction > 50%. -> matches. Building.
- **slipnet TSE (single attempt authorized):** per-type INDEPENDENT slipnet activation A_r; per-type best-match s_r(e) =
  max similarity (NOT sum); combine by argmax VOTING (entity winning majority of per-type best-matches) or top-3-in->=6/10
  channels. Gate recall@1>=0.75; if HF at <=0.60 accept 0.40-0.45 honest ceiling + flag v3.2 PerRole follow-up. -> matches.
  Building once.

## Build order (laptop CPU; all <2hr each)
1. code2_r_soft_decode (closes Wave-1 Tier-0 code2 gap)
2. slipnet TSE (single attempt)
3. active_inference_e1_e2
4. multidrive_vsa_policy_h3
Plus: CLS n=5 already done (above) -> file Tier C.

## Note on lanes
All substrate-native = CPU. Will keep the laptop fed through this batch. GPU remains idle by nature (no distinct substrate
GPU work left; benchmarks are also CPU). Acknowledged your "route BEST mechanism not cheapest gate" going forward.
