# Prereg: kappa3_noise_convention_sign_distinguisher_v1_n4096

## Anchor
kappa3_noise_convention_sign_distinguisher_v1_n4096

## Priority
A (Research kappa3_sign_convention_2x handoff Anchor 1 -- CRITICAL/cheap; resolves the kappa3-NLO sign
saga + sets the correct noise convention for ALL downstream I-19 / sigma_g_crit kappa_3 anchors).

## Scientific question
Run kappa_3^free under two noise conventions back-to-back at matched sigma_g, alpha (N=4096):
(A) additive-on-W: W + sigma_g*G/sqrt(N), G symmetric Gaussian; (B) additive-on-patterns:
Xi + sigma_g*g per pattern. Measure SIGNED delta_kappa3 vs clean. sigma_g in {0.05,0.10,0.20} (small =
leading-order regime so 3*sg^2*alpha applies and heavy-tail blowup is avoided). 5 seeds.

## Pre-registered bands
HARD-PASS: additive-on-patterns (B) delta POSITIVE on >=2/3 cells AND matches 3*sg^2*alpha within 30%
on >=2/3 cells AND additive-on-W (A) negligible by contrast (mean|A| < mean|B|). Confirms
noise-convention determines sign.
MIDDLE: B positive but formula-match <2/3 or A-contrast weak.
HARD-FAIL: B delta NOT positive (<2/3 cells) -- convention model refuted.

## Formula self-tests (PROT-022)
1. pred(0.10,0.05)=3*0.01*0.05=0.0015. 2. free kappa_3 equal-diagonal=0. 3. additive-on-W per-entry std ~ sigma_g/sqrt(N). [PASS]

## N-suffix binding (PROT-018)
anchor _n4096; production N=4096. 5 seeds (PROT-021).

## Timeout
2 conditions x 3 sigma_g x 5 seeds x Hutchinson (3000 probes) at N=4096. timeout_s=14400.

## Smoke gate
Smoke PASSED (N=256, noise-limited): highest-SNR cell sg=0.20 shows B positive matching formula
(relB 0.08-0.28) both seeds; small-sg cells below the Hutchinson noise floor at N=256/400-probes.
Full N=4096/3000-probes (16x lower noise floor) resolves all cells.

## Queue
remote_cpu_queue (pure numpy; CPU).
