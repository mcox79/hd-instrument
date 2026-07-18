# Pre-reg: reward_contingency_nonstationary_tracking_v1

Non-stationary credit-assignment test. The revival regime the stationary contingency VET
(a33fada3) named verbatim: does an ONLINE eligibility-trace rule track a MOVING reward-
predicting cue better than a BATCH correlation counter that structurally cannot?

Cell: `experiments/exp_reward_contingency_nonstationary_tracking_v1.py`
Anchor: `reward_contingency_nonstationary_tracking_v1`
Metrics: `data/exp_reward_contingency_nonstationary_tracking_v1/metrics.json`

## Prior work / novelty
Non-stationary extension of `exp_reward_contingency_credit_assignment_v1` (VET a33fada3), which
was CORRELATION-TRIVIAL: with c* FIXED, a delay-blind batch co-occurrence counter ties
three_factor at 1.000 in <20 trials. The VET's revival criterion: make c* switch over time so a
full-history batch counter fails by construction. REUSES the eligibility x RPE machinery; the
CHANGE is a moving c* (switch every K trials) + batch/windowed contingency-counter baselines.
Substrate-KB concept-query prior-work check: top hits are the general track0.1c eligibility-trace
concept notes at cosine 0.32-0.35 (NOT a non-stationary tracking cell); genuinely novel regime,
builds on the stationary predecessor. CLAIM-VET-pending.

## Design (glass-box, local-runnable, sequential-CPU)
- M=6 candidate cues (random bipolar HD, N=256); c* SWITCHES every K_SWITCH=30 trials
  (no-consecutive-repeat). Each trial: candidates fire iid p_fire=0.5 in random order; DELAY of
  DELAY_K=4 fresh distractor pairs; reward r=+1 iff CURRENT c* fired.
- Schedule (fired cues, c*(t), reward(t)) generated ONCE per replicate, fed IDENTICALLY to every
  arm -> the tracking RULE is the ONE variable.
- Metric = steady-state current-c* tracking accuracy = P(belief(t)==c*(t)) over trials where
  tracking is DEFINED (past block 0, i.e. >=1 switch has occurred) AND past the SETTLE=8-trial
  post-switch transient. Both exclusions applied EQUALLY to all arms. chance=1/M=0.167.

## Arms (ONE variable = the tracking rule)
- ARM_THREE_FACTOR (mechanism): E=gamma*E+outer(post,pre) per event (gamma=0.9, reset/episode ->
  bridges the delay); at reward W=(1-W_LEAK)*W + lr*(r-r_baseline)*E, r_baseline = EMA reward
  (dopamine-RPE). W_LEAK=1/K_SWITCH (a-priori from K, NOT tuned) -> memory ~ block length; RPE
  sign actively erodes a stale c*. Belief = argmax_i (W@c_i).t_i.
- ARM_BATCH_COUNTER (must-FAIL baseline): full-history contingency dP_i = P(r|i fired) -
  P(r|~i fired), Laplace-smoothed. Averages over every past c* -> fails by construction.
- ARM_WINDOWED_COUNTER (strong / honest-MM baseline): same tally over a sliding window; run over
  WINDOW_SET={10,20,30,50,80}, report the BEST steady-state accuracy (oracle over windows =
  strongest fair counter, generous to baseline). Ties three_factor -> MM, not unique.
- ARM_RECENCY (reward-agnostic null): belief = most-recently-fired candidate. -> chance.

## Conditions
- SWITCH (main discriminating): c* switches every K_SWITCH.
- STATIONARY (positive control): c* fixed -> reproduces v1 triviality; batch must ACE (>=0.90).

## Bands (steady-state tracking accuracy; META_RULE_L strict-above-floor)
- DIFFICULTY-ON gate @ SWITCH: batch_counter <= 0.35 (fails by construction). > 0.45 -> DESIGN_FAIL.
- CAN-FAIL / HARD_FAIL_TRACKING_INSUFFICIENT: three_factor < 0.40 OR (three_factor-batch) < 0.15.
- HARD_PASS (UNIQUE capability): three_factor >= 0.60 AND (tf-best_windowed) >= 0.05 AND
  (tf-batch) >= 0.20 AND (tf-recency) >= 0.20, on >= 2/3 seeds.
- MM_ONLINE_CORRELATION (honest expected): tf beats {batch,recency,chance} by the margins but
  (tf-best_windowed) < 0.05 -> mechanism-implementation of online-correlation, not unique.
- POSCTRL @ STATIONARY: batch >= 0.90 AND tf >= 0.90.
- HP_SCOPE: HARD_PASS gates apply to ARM_THREE_FACTOR only; batch/recency are must-fail controls.

## Design-gate compliance (pre-verified at smoke)
1. REAL baselines: batch (full history) + oracle-windowed + recency + chance. Not strawman.
2. CAN-FAIL: HARD_FAIL branch reachable (tf could fail to beat batch); HARD_PASS reachable
   (tf could beat windowed). Verdict is NOT forced by construction.
3. DIFFICULTY-ON: batch counter fails by construction (verified near chance at smoke).
4. ONE variable: identical schedule fed to all arms; only the rule differs.

## Cell-template mandates
except SystemExit-before-Exception (no BaseException); arms_differ on belief seqs; tmp_replace
atomic write; baseline_in_band (tf in (0.05,0.95)); discriminator survives scale (smoke = full
M/N/K, >=6 blocks so batch already fails); crlb_n/a (discrete argmax, chance=1/M); PYTHONHASHSEED-
safe seeds (sha256); start marker + crash metrics + heartbeat.

## RESULT (MEASURED@data/exp_reward_contingency_nonstationary_tracking_v1/metrics.json)
FULL (N=256, M=6, K=30, 12 blocks, 16 reps, seeds 7/13/19), 24.3s local CPU:
- verdict = MM_ONLINE_CORRELATION (all 3 seeds consistent).
- @SWITCH mean: three_factor=0.739, batch_counter=0.258, windowed_counter=0.996 (best_w=10),
  recency=0.170, chance=0.167. tf beats batch (+0.481), recency (+0.569), chance; tf does NOT
  beat windowed (-0.257) -> MM.
- windowed per-window: {10:0.997, 20:0.902, 30:0.707, 50:0.268, 80:0.341}.
- @STATIONARY: batch=1.000, tf=1.000 (v1 triviality reproduced).
- difficulty_on=True, posctrl_ok=True, beats_naive=True, ties_windowed=True, arms_differ=True.

INTERPRETATION (hypothesis-pending-VET, deflated): the mechanism REVIVES from the stationary
correlation-trivial tie -- it genuinely tracks a moving target the batch counter cannot -- but a
recency-windowed counter (oracle window=10) tracks BETTER, so this is a mechanism-implementation
of online-correlation, not a unique capability. Honest brain-check direction: three_factor's
fixed-timescale forget (gamma/W_LEAK) is beaten by an oracle boxcar; the Behrens volatility-
adaptive learning-rate (surprise-scaled eta) is the candidate mechanism that could beat any fixed
window -- a follow-up cell, not claimed here.
