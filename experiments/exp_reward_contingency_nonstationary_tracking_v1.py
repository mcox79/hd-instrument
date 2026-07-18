"""exp_reward_contingency_nonstationary_tracking_v1 -- the NON-STATIONARY credit-assignment
test. The revival regime the stationary contingency VET (a33fada3) named verbatim: a moving
reward-predicting cue c* that SWITCHES over time, where a BATCH correlation counter that
averages over ALL trials CANNOT track the change (fails by construction), but an ONLINE
recency-weighted eligibility-trace rule CAN.

WHAT / WHY (glass-box, self-contained):
  The stationary contingency cell (exp_reward_contingency_credit_assignment_v1, VET a33fada3)
  was CORRELATION-TRIVIAL: because c* is FIXED, a delay-blind BATCH co-occurrence counter that
  tallies P(reward | cue_i fired) over all trials ties three_factor at 1.000 in <20 trials --
  it just averages over the whole history. The VET's exact revival criterion: make c*
  NON-STATIONARY (switch every K trials). Now the full-history batch counter averages the
  contingency over MANY different c* -> every cue looks equally (weakly) predictive -> it FAILS
  BY CONSTRUCTION. An online eligibility x RPE rule with a graded forgetting leak naturally
  tracks the CURRENT contingency. Behrens/Yu-Dayan: the brain RAISES its learning rate under
  volatility -- exactly this regime.

  HONEST CRUX (the MM guard the task mandates): a simple RECENCY-WINDOWED counter -- the same
  P(reward|cue) tally but over only the last W trials -- ALSO tracks the switches when W ~ block
  length. So beating the BATCH counter alone is NOT a unique capability; it only proves
  non-stationarity is the right regime. To claim a UNIQUE capability three_factor must beat the
  BEST windowed counter (oracle-tuned over a window set = the strongest fair counter). If it
  only MATCHES the windowed counter, the honest verdict is MM: three_factor is a mechanism-
  implementation of a trivial online-correlation task, not a unique capability. The cell
  measures and REPORTS which, decisively.

THE TASK (online current-c* tracking, non-stationary, delayed, recency-windowed-fair):
  M candidate cues {c_i -> t_i}, random bipolar HD vectors. c* SWITCHES every K_SWITCH trials
  (no-consecutive-repeat -> every switch is a real change). Each trial (episode):
    1. Each candidate fires independently prob p_fire, in RANDOM order (one event each).
    2. A DELAY window of k FRESH random distractor pairs fires (decorrelated identities).
    3. Reward r = +1 iff the CURRENT c* fired this trial, else 0.
  The schedule (which cues fire, c*(t), reward(t)) is generated ONCE per replicate and fed
  IDENTICALLY to every arm (the tracking RULE is the ONE variable). At every trial t each arm
  emits a BELIEF = its current estimate of which cue predicts reward (argmax of its running
  credit). Metric = steady-state current-c* tracking accuracy = P(belief(t) == c*(t)) over
  trials at least SETTLE steps past the most recent switch (the switch transient is excluded
  EQUALLY for all arms). Chance = 1/M.

ARMS (the tracking RULE is the variable; event/reward schedule identical across arms):
  ARM_THREE_FACTOR (mechanism): eligibility E = gamma*E + outer(post,pre) per event
    (gamma=0.9, reset per episode -> bridges the k-distractor delay); at reward
    W = (1 - W_LEAK)*W + lr*(r - r_baseline)*E, where r_baseline is a running EMA of reward
    (dopamine-RPE). The W_LEAK forgets stale contingencies (effective memory ~ 1/W_LEAK ~ K);
    the RPE sign ACTIVELY erodes an old c* the trial it stops predicting reward (negative RPE),
    a potential edge over a passive boxcar window at the switch transient. Belief =
    argmax_i (W @ c_i) . t_i.
  ARM_BATCH_COUNTER (must-FAIL baseline): full-history contingency counter. Per cue i tallies
    dP_i = P(r | i fired) - P(r | i not fired) over ALL trials so far (Laplace-smoothed).
    Belief = argmax_i dP_i. Averages over every past c* -> cannot track fast switches -> FAILS
    BY CONSTRUCTION (verify near chance @ SWITCH). This is the arm the VET said must fail.
  ARM_WINDOWED_COUNTER (strong / honest-MM baseline): the SAME contingency tally but over a
    sliding window of the last W trials; run for a SET of windows and report the BEST steady-
    state accuracy (oracle over windows = strongest fair counter, deliberately generous to the
    baseline). If this ties three_factor -> MM, not unique capability.
  ARM_RECENCY (reward-agnostic null): belief = most-recently-fired candidate cue. Firing is
    reward-agnostic + uniform -> most-recent-fired cue is uniform random -> chance. MUST FAIL.
  Chance = 1/M analytic (also cross-checked by all arms' floor).

CONDITIONS (per arm; ONE variable per comparison):
  SWITCH (c* switches every K_SWITCH trials): MAIN discriminating condition. HARD bands here.
  STATIONARY (c* never switches): POSITIVE CONTROL -- reproduces the v1 correlation-triviality;
    the BATCH counter should ACE it (>=0.90), proving the batch counter is defeated ONLY by
    non-stationarity, not by a bug/artifact.

BANDS (steady-state current-c* tracking accuracy; chance = 1/M = 0.1667 for M=6; META_RULE_L):
  DIFFICULTY-ON gate @ SWITCH: batch_counter <= 0.35 (near chance -> non-stationarity bites,
    batch fails by construction). If batch > 0.45 @ SWITCH -> DESIGN_FAIL (non-stationarity did
    not bite -> the whole premise is void; do not interpret downstream arms).
  CAN-FAIL / HARD_FAIL_TRACKING_INSUFFICIENT: three_factor < 0.40 @ SWITCH OR
    (three_factor - batch_counter) < 0.15 @ SWITCH -> DEFINITIVE negative: the online
    eligibility rule cannot track a moving contingency even where a batch counter fails.
    NOT tortured toward pass -> brain-check what is missing (Behrens volatility-adaptive rate).
  HARD_PASS (UNIQUE capability, ARM_THREE_FACTOR @ SWITCH): three_factor >= 0.60 AND
    (three_factor - best_windowed_counter) >= 0.05 AND (three_factor - batch_counter) >= 0.20
    AND (three_factor - recency) >= 0.20, on >= 2/3 seeds -> online eligibility genuinely
    tracks volatility BETTER than the strongest fair counter (not just the batch counter).
  MM / MIDDLE_BAND (honest expected outcome): three_factor beats {batch, recency, chance} by
    the margins above BUT does NOT beat the best windowed counter
    (three_factor - best_windowed_counter < 0.05) -> MM: mechanism-implementation of online-
    correlation tracking. Revives the mechanism from the stationary correlation-trivial tie
    (beats the batch counter the VET said fails by construction) but is NOT a unique capability
    a recency-windowed counter lacks. Reported honestly; CLAIM-VET-pending.
  POSCTRL @ STATIONARY: batch_counter >= 0.90 AND three_factor >= 0.90 (both ace it ->
    reproduces v1 correlation-triviality; confirms batch fails ONLY under non-stationarity).

COMPUTE ARCHITECTURE: class (b) sequential-CPU, justified -- the eligibility trace + the online
  counters have genuine SEQUENTIAL dependencies (E[t] depends on E[t-1]; the counter belief at t
  depends on the running tally) and this cell IS the substrate learning-rule being validated
  (bit-identical CPU reference). Full wall time < a few minutes on CPU. device='cpu' default
  (runner does not pass argv). Storage: no_storage / no_composition (single heteroassociative W
  per replicate). progress_logging: per-seed [say] prints flush=True + _heartbeat.jsonl per
  seed-unit (full wall < 1800s so dense per-step flushing not required by §17; heartbeat present).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash on per-arm belief sequences)
  - final_metrics_atomicity = tmp_replace
  - baseline_in_band at smoke: three_factor in (0.05,0.95) @ SWITCH (not saturated). batch +
    recency are MUST-FAIL controls, exempt from the in-band rule (HP_SCOPE below).
  - discriminator survives scale: smoke runs the FULL M/N/K regime and >= 6 switch-blocks so the
    batch counter already fails; only T (block count) / R / seeds shrink; asserts
    three_factor - max(batch,recency) margin fires at smoke.
  - crlb_n_a: discrete argmax over M candidates; analytic chance floor 1/M (no continuous CRLB).
  - HP_SCOPE: HARD_PASS gates apply to ARM_THREE_FACTOR only; batch/recency are must-fail
    controls (in-band + HARD_PASS floors do NOT apply to them).
  - calibration_check: default_ok_for_this_regime (gamma/W_LEAK derived a-priori from K, NOT
    tuned per run; windowed counter oracle-selected -> generous to baseline).
  - all numbers CITED@ (brain lit) / THEORETICAL@ (chance=1/M, W_LEAK~1/K) / MEASURED@ (disk).
  - NO hash()-derived seeds (PYTHONHASHSEED-safe): hashlib.sha256 digest for arm seed offset.
  - start marker + crash metrics + heartbeat + atomic write.

CITATIONS:
  Izhikevich (2007) distal reward via STDP+dopamine. Cerebral Cortex 17:2443. CITED
  Fremaux & Gerstner (2016) neuromodulated STDP / three-factor rules. Front Neural Circuits. CITED
  Gerstner, Lehmann, Liakoni, Corneil, Brea (2018) eligibility traces on behavioral time scales.
    Front Neural Circuits. CITED
  Behrens, Woolrich, Walton, Rushworth (2007) "Learning the value of information in an uncertain
    world" Nat Neurosci 10:1214 -- volatility raises the learning rate. CITED
  Yu & Dayan (2005) expected vs unexpected uncertainty (ACh/NE) -- unexpected uncertainty resets
    priors. CITED
  Rescorla & Wagner (1972) contingency (not contiguity) via dP = P(r|cue) - P(r|~cue). CITED
"""

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from collections import deque
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "reward_contingency_nonstationary_tracking_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- arg parse -------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--full", action="store_true")
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--device", default="cpu")  # default cpu: runner does not pass argv
_ARGS, _ = _P.parse_known_args()

_NAME_SAYS_SMOKE = "smoke" in os.path.basename(__file__).lower()
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
else:
    RUN_MODE = "full"

DEVICE = torch.device(_ARGS.device if torch.cuda.is_available() or _ARGS.device == "cpu" else "cpu")
DTYPE = torch.float32
torch.set_num_threads(max(1, min(8, (os.cpu_count() or 4))))

# ---- regime constants ------------------------------------------------------
# THEORETICAL@ chance = 1/M for argmax over M candidates.
# M, N, K_SWITCH, delay (the difficulty axes) held CONSTANT across modes (discriminator survives
# scale); only T (block count) / R / seed-count shrink for cheaper modes. Smoke keeps >= 6
# switch-blocks so the batch counter already fails by construction.
K_SWITCH = 30       # c* switches every K_SWITCH trials (block length). THEORETICAL@ W_LEAK~1/K.
DELAY_K = 4         # k fresh distractor pairs between candidate events and reward.
M_CAND = 6
N_DIM = 256
P_FIRE = 0.5        # each candidate fires with this prob per trial (frequency matched)
SETTLE = 8          # trials post-switch excluded from steady-state accuracy (transient, all arms)

if RUN_MODE == "self_test":
    T_TRIALS = 6 * K_SWITCH     # 6 blocks
    R_REPLICATES = 4
    SEEDS = [7]
elif RUN_MODE == "smoke":
    T_TRIALS = 6 * K_SWITCH     # 6 blocks (batch already fails)
    R_REPLICATES = 8
    SEEDS = [7, 13]
else:  # full
    T_TRIALS = 12 * K_SWITCH    # 12 blocks
    R_REPLICATES = 16
    SEEDS = [7, 13, 19]

GAMMA_E = 0.9              # eligibility decay; tau ~ 10 steps. CITED (Gerstner 2018)
LR = 1.0
# W_LEAK ~ 1/K_SWITCH -> effective memory ~ block length. THEORETICAL@ (a-priori from K, not tuned).
W_LEAK = 1.0 / K_SWITCH   # ~0.0333 -> memory ~30 trials ~ K_SWITCH
RPE_BASELINE_INIT = float(P_FIRE)   # reward rate = P(c* fired) = p_fire
RPE_BASELINE_ALPHA = 0.05
# windowed-counter windows (oracle-best reported). "full history" is the BATCH arm, excluded here.
WINDOW_SET = [10, 20, 30, 50, 80]
COUNTER_SMOOTH = 1.0      # Laplace smoothing for dP estimates
CHANCE = 1.0 / M_CAND

ARMS = ["three_factor", "batch_counter", "windowed_counter", "recency"]
CONDITIONS = ["SWITCH", "STATIONARY"]
DISCRIM_COND = "SWITCH"
POSCTRL_COND = "STATIONARY"

# HARD bands (steady-state current-c* tracking accuracy)
HP_TF_MIN = 0.60
HP_MARGIN_VS_WINDOWED = 0.05     # unique-capability margin (beat the oracle windowed counter)
HP_MARGIN_VS_BATCH = 0.20
HP_MARGIN_VS_RECENCY = 0.20
DIFFICULTY_BATCH_MAX = 0.35      # batch must be at/below this @ SWITCH (fails by construction)
DIFFICULTY_FAIL_BATCH = 0.45     # batch above this @ SWITCH => non-stationarity did not bite
CANFAIL_TF_MIN = 0.40            # three_factor below this @ SWITCH => HARD_FAIL
CANFAIL_TF_VS_BATCH = 0.15       # three_factor must beat batch by this @ SWITCH else HARD_FAIL
MM_WINDOWED_TIE = 0.05           # |tf - windowed| < this => MM (not unique)
POSCTRL_MIN = 0.90               # batch + tf ace STATIONARY (reproduce v1 triviality)


def _say(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def get_output_dir():
    d = os.path.join(REPO_ROOT, "data", "exp_%s" % ANCHOR_NAME)
    if RUN_MODE == "smoke":
        d = os.path.join(REPO_ROOT, "data", "exp_%s_smoke" % ANCHOR_NAME)
    elif RUN_MODE == "self_test":
        d = os.path.join(REPO_ROOT, "data", "exp_%s_selftest" % ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _emit_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": elapsed_s,
    }
    if extra:
        row["extra"] = extra
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _bipolar(gen, n):
    """Random +/-1 bipolar HD vector, shape (n,)."""
    return (torch.randint(0, 2, (n,), generator=gen, device=DEVICE, dtype=torch.int64) * 2 - 1).to(DTYPE)


def _arm_seed_offset(arm):
    """PYTHONHASHSEED-safe deterministic per-arm offset (no builtin hash())."""
    return int.from_bytes(hashlib.sha256(arm.encode()).digest()[:4], "big") % 100000


def make_schedule(gen, m, t_trials, k_switch, switching):
    """Generate the SHARED trial schedule ONCE per replicate (fed identically to every arm).

    Returns dict with:
      fired: list[list[int]]  -- cue indices that fired each trial, in random order
      cstar: list[int]        -- current reward-predicting cue per trial
      reward: list[int]       -- 1 iff current cstar fired this trial
      switch_trials: set[int] -- trial indices where cstar changed (block starts, excl 0)
    """
    fired_all = []
    cstar_all = []
    reward_all = []
    switch_trials = set()
    cur_star = int(torch.randint(0, m, (1,), generator=gen).item())
    for t in range(t_trials):
        if switching and t > 0 and (t % k_switch == 0):
            # no-consecutive-repeat switch
            nxt = int(torch.randint(0, m - 1, (1,), generator=gen).item())
            if nxt >= cur_star:
                nxt += 1
            cur_star = nxt
            switch_trials.add(t)
        fires = (torch.rand(m, generator=gen, device=DEVICE) < P_FIRE)
        fired = [i for i in range(m) if bool(fires[i].item())]
        if len(fired) > 1:
            perm = torch.randperm(len(fired), generator=gen).tolist()
            fired = [fired[p] for p in perm]
        r = 1 if (cur_star in fired) else 0
        fired_all.append(fired)
        cstar_all.append(cur_star)
        reward_all.append(r)
    return {"fired": fired_all, "cstar": cstar_all, "reward": reward_all,
            "switch_trials": switch_trials}


def _steady_mask(t_trials, k_switch, switching, settle):
    """Bool list: True at trials where tracking is DEFINED and past the switch transient.

    Applied EQUALLY to every arm. Two exclusions (both principled, both arm-agnostic):
      (1) block 0 (t < k_switch) is excluded in the SWITCH condition -- before the first switch
          there is nothing to TRACK, and the full-history batch counter is trivially correct
          there (only one c* has ever been seen). Including it gives the batch counter free
          credit that is not a tracking signal. Tracking is only defined AFTER >= 1 switch.
      (2) the first `settle` trials of every block are the post-switch transient (no rule can
          re-lock instantly); excluded so the metric measures STEADY-STATE tracking.
    STATIONARY (single block, no switch): only exclusion (2) at the start applies.
    """
    mask = []
    for t in range(t_trials):
        if not switching:
            mask.append(t >= settle)
        else:
            within = t % k_switch
            defined = (t >= k_switch)          # exclusion (1): past block 0 (>= 1 switch seen)
            past_transient = (within >= settle)  # exclusion (2): steady-state within block
            mask.append(defined and past_transient)
    return mask


def run_three_factor(gen, sched, n, m):
    """ARM_THREE_FACTOR belief(t) sequence: eligibility x RPE with a forgetting leak.

    Processes the raw event stream (cue events + fresh delay distractors); bridges the delay
    with the eligibility trace. Belief(t) = argmax_i (W @ c_i) . t_i AFTER trial t's update.
    """
    cues = torch.stack([_bipolar(gen, n) for _ in range(m)])   # (m, n)
    tgts = torch.stack([_bipolar(gen, n) for _ in range(m)])   # (m, n)
    W = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    E = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    r_baseline = float(RPE_BASELINE_INIT)
    beliefs = []
    for t in range(len(sched["fired"])):
        E.zero_()
        for ci in sched["fired"][t]:
            E.mul_(GAMMA_E)
            E.addr_(tgts[ci], cues[ci])
        for _d in range(DELAY_K):
            pre = _bipolar(gen, n)
            post = _bipolar(gen, n)
            E.mul_(GAMMA_E)
            E.addr_(post, pre)
        r = float(sched["reward"][t])
        modulator = r - r_baseline
        W.mul_(1.0 - W_LEAK)                    # forget stale contingencies
        W.add_(E, alpha=LR * modulator)         # three-factor: delta_w = trace x neuromod
        r_baseline += RPE_BASELINE_ALPHA * (r - r_baseline)
        resp = cues @ W.t()                     # (m, n)
        scores = (resp * tgts).sum(dim=1)       # (m,)
        beliefs.append(int(torch.argmax(scores).item()))
    return beliefs


def run_recency(sched, m):
    """ARM_RECENCY belief(t): most-recently-fired candidate cue (reward-agnostic null)."""
    beliefs = []
    last = 0
    for t in range(len(sched["fired"])):
        fired = sched["fired"][t]
        if fired:
            last = fired[-1]
        beliefs.append(last)
    return beliefs


def _counter_beliefs(sched, m, window):
    """Online contingency counter belief(t) over a sliding window (window=None -> full history).

    dP_i = P(r | i fired) - P(r | i not fired), Laplace-smoothed, over the window ending at t.
    Belief(t) = argmax_i dP_i AFTER trial t. Ties broken by lowest index (deterministic).
    """
    fired_all = sched["fired"]
    reward_all = sched["reward"]
    t_trials = len(fired_all)
    beliefs = []
    if window is None:
        # running full-history counts
        fired_ct = [0] * m
        fired_rew = [0] * m
        n_trials = 0
        sum_rew = 0
        for t in range(t_trials):
            fs = set(fired_all[t]); r = reward_all[t]
            n_trials += 1; sum_rew += r
            for i in range(m):
                if i in fs:
                    fired_ct[i] += 1; fired_rew[i] += r
            scores = []
            for i in range(m):
                nf = fired_ct[i]; nnf = n_trials - nf
                p_r_f = (fired_rew[i] + COUNTER_SMOOTH) / (nf + 2 * COUNTER_SMOOTH)
                p_r_nf = ((sum_rew - fired_rew[i]) + COUNTER_SMOOTH) / (nnf + 2 * COUNTER_SMOOTH)
                scores.append(p_r_f - p_r_nf)
            beliefs.append(int(np.argmax(scores)))
    else:
        buf = deque(maxlen=window)  # each entry: (fired_set, reward)
        for t in range(t_trials):
            buf.append((set(fired_all[t]), reward_all[t]))
            n_trials = len(buf); sum_rew = sum(r for _, r in buf)
            fired_ct = [0] * m; fired_rew = [0] * m
            for fs, r in buf:
                for i in fs:
                    fired_ct[i] += 1; fired_rew[i] += r
            scores = []
            for i in range(m):
                nf = fired_ct[i]; nnf = n_trials - nf
                p_r_f = (fired_rew[i] + COUNTER_SMOOTH) / (nf + 2 * COUNTER_SMOOTH)
                p_r_nf = ((sum_rew - fired_rew[i]) + COUNTER_SMOOTH) / (nnf + 2 * COUNTER_SMOOTH)
                scores.append(p_r_f - p_r_nf)
            beliefs.append(int(np.argmax(scores)))
    return beliefs


def _accuracy(beliefs, cstar, mask):
    n = 0; c = 0
    for t in range(len(beliefs)):
        if mask[t]:
            n += 1
            if beliefs[t] == cstar[t]:
                c += 1
    return c / float(n) if n else 0.0


def run_arm_cond(seed, arm, cond, n, m, t_trials, r_reps, want_belief_sample=False):
    """Steady-state tracking accuracy over r_reps replicates for one arm+condition.

    windowed_counter returns the BEST window's accuracy (oracle over WINDOW_SET) + per-window.
    Returns dict: {acc, extra} where extra may hold best_window / per_window / belief_sample.
    """
    switching = (cond == "SWITCH")
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 100003 + (1 if switching else 0) * 5171 + _arm_seed_offset(arm))
    mask = _steady_mask(t_trials, K_SWITCH, switching, SETTLE)

    if arm == "windowed_counter":
        per_window_acc = {w: [] for w in WINDOW_SET}
    accs = []
    belief_sample = None
    for rep in range(r_reps):
        sched = make_schedule(gen, m, t_trials, K_SWITCH, switching)
        cstar = sched["cstar"]
        if arm == "three_factor":
            beliefs = run_three_factor(gen, sched, n, m)
            accs.append(_accuracy(beliefs, cstar, mask))
        elif arm == "recency":
            beliefs = run_recency(sched, m)
            accs.append(_accuracy(beliefs, cstar, mask))
        elif arm == "batch_counter":
            beliefs = _counter_beliefs(sched, m, None)
            accs.append(_accuracy(beliefs, cstar, mask))
        elif arm == "windowed_counter":
            best = -1.0; beliefs = None
            for w in WINDOW_SET:
                b = _counter_beliefs(sched, m, w)
                a = _accuracy(b, cstar, mask)
                per_window_acc[w].append(a)
                if a > best:
                    best = a; beliefs = b
            accs.append(best)
        else:
            raise ValueError("unknown arm %r" % arm)
        if want_belief_sample and rep == 0:
            belief_sample = list(beliefs)
    out = {"acc": float(np.mean(accs)), "acc_per_rep": accs}
    if arm == "windowed_counter":
        mean_per_w = {int(w): float(np.mean(per_window_acc[w])) for w in WINDOW_SET}
        out["per_window_acc"] = mean_per_w
        out["best_window"] = int(max(mean_per_w, key=mean_per_w.get))
    if belief_sample is not None:
        out["belief_sample"] = belief_sample
    return out


def _arms_must_differ(arm_belief_samples):
    """Hash per-arm belief sequences; assert not bit-identical (META_RULE_AF)."""
    digests = {}
    for name, seq in arm_belief_samples.items():
        b = np.asarray(seq, dtype=np.int64).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], \
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b)
    return digests


def run_seed(seed, output_dir, t0, hb_state):
    """Returns {cond: {arm: acc}}, windowed detail @ SWITCH, belief samples @ SWITCH."""
    per_cond = {}
    windowed_detail = {}
    belief_samples = {}
    for cond in CONDITIONS:
        per_cond[cond] = {}
        for arm in ARMS:
            want_sample = (cond == DISCRIM_COND)
            res = run_arm_cond(seed, arm, cond, N_DIM, M_CAND, T_TRIALS, R_REPLICATES,
                               want_belief_sample=want_sample)
            per_cond[cond][arm] = res["acc"]
            if cond == DISCRIM_COND:
                if arm == "windowed_counter":
                    windowed_detail = {"per_window_acc": res["per_window_acc"],
                                       "best_window": res["best_window"]}
                if "belief_sample" in res:
                    belief_samples[arm] = res["belief_sample"]
            hb_state["unit"] += 1
            _emit_heartbeat(output_dir, hb_state["unit"], hb_state["total"],
                            time.perf_counter() - t0,
                            extra={"seed": seed, "cond": cond, "arm": arm, "acc": round(res["acc"], 4)})
    return per_cond, windowed_detail, belief_samples


def aggregate_and_verdict(per_seed, windowed_detail_last, belief_samples_last, elapsed_s):
    mean_acc = {}
    for cond in CONDITIONS:
        mean_acc[cond] = {}
        for arm in ARMS:
            vals = [per_seed[s][cond][arm] for s in SEEDS]
            mean_acc[cond][arm] = float(np.mean(vals))

    tf = mean_acc[DISCRIM_COND]["three_factor"]
    batch = mean_acc[DISCRIM_COND]["batch_counter"]
    win = mean_acc[DISCRIM_COND]["windowed_counter"]
    rec = mean_acc[DISCRIM_COND]["recency"]
    tf_stat = mean_acc[POSCTRL_COND]["three_factor"]
    batch_stat = mean_acc[POSCTRL_COND]["batch_counter"]

    # per-seed HARD_PASS at DISCRIM_COND (unique-capability: beats even windowed)
    seed_pass = []
    for s in SEEDS:
        _tf = per_seed[s][DISCRIM_COND]["three_factor"]
        _batch = per_seed[s][DISCRIM_COND]["batch_counter"]
        _win = per_seed[s][DISCRIM_COND]["windowed_counter"]
        _rec = per_seed[s][DISCRIM_COND]["recency"]
        ok = (_tf >= HP_TF_MIN) and ((_tf - _win) >= HP_MARGIN_VS_WINDOWED) and \
             ((_tf - _batch) >= HP_MARGIN_VS_BATCH) and ((_tf - _rec) >= HP_MARGIN_VS_RECENCY)
        seed_pass.append(bool(ok))
    n_seed_pass = sum(1 for b in seed_pass if b)

    difficulty_on = (batch <= DIFFICULTY_BATCH_MAX)
    difficulty_fail = (batch > DIFFICULTY_FAIL_BATCH)
    canfail = (tf < CANFAIL_TF_MIN) or ((tf - batch) < CANFAIL_TF_VS_BATCH)
    posctrl_ok = (batch_stat >= POSCTRL_MIN) and (tf_stat >= POSCTRL_MIN)
    beats_naive = (tf >= HP_TF_MIN) and ((tf - batch) >= HP_MARGIN_VS_BATCH) and \
                  ((tf - rec) >= HP_MARGIN_VS_RECENCY)
    ties_windowed = (tf - win) < MM_WINDOWED_TIE

    if difficulty_fail:
        verdict = "DESIGN_FAIL"
        vmsg = ("batch_counter=%.3f > %.2f @ SWITCH: non-stationarity did NOT bite (batch did not "
                "fail by construction) -> the revival premise is void; do not interpret arms." %
                (batch, DIFFICULTY_FAIL_BATCH))
    elif not posctrl_ok:
        verdict = "POSCTRL_FAIL"
        vmsg = ("STATIONARY positive control failed: batch_counter=%.3f, three_factor=%.3f "
                "(need >= %.2f both). The batch counter should ACE the stationary regime "
                "(reproduce v1 triviality); if it does not, a bug -- not non-stationarity -- is "
                "defeating it. Do not interpret the SWITCH result." %
                (batch_stat, tf_stat, POSCTRL_MIN))
    elif canfail:
        verdict = "HARD_FAIL_TRACKING_INSUFFICIENT"
        vmsg = ("three_factor=%.3f @ SWITCH (batch=%.3f, margin=%.3f, chance=%.3f): the online "
                "eligibility rule CANNOT track a moving contingency even where the batch counter "
                "fails (batch=%.3f). DEFINITIVE negative -> brain-check (Behrens volatility-"
                "adaptive learning rate: the fix is likely a surprise-scaled eta, not fixed gamma)."
                % (tf, batch, tf - batch, CHANCE, batch))
    elif n_seed_pass >= 2 and difficulty_on:
        verdict = "HARD_PASS"
        vmsg = ("UNIQUE capability: three_factor=%.3f BEATS the best windowed counter=%.3f "
                "(margin=%.3f), the batch counter=%.3f (margin=%.3f, batch fails by construction), "
                "recency=%.3f (margin=%.3f) and chance=%.3f @ SWITCH; %d/%d seeds pass. Online "
                "eligibility x RPE tracks volatility BETTER than the strongest fair counter -- not "
                "just the batch counter. STATIONARY posctrl: batch=%.3f tf=%.3f (v1 triviality "
                "reproduced)." %
                (tf, win, tf - win, batch, tf - batch, rec, tf - rec, CHANCE, n_seed_pass,
                 len(SEEDS), batch_stat, tf_stat))
    elif beats_naive and ties_windowed and difficulty_on:
        verdict = "MM_ONLINE_CORRELATION"
        vmsg = ("MM (mechanism-implementation, NOT unique capability): three_factor=%.3f beats the "
                "batch counter=%.3f (margin=%.3f, batch fails by construction under non-stationarity) "
                ", recency=%.3f and chance=%.3f @ SWITCH, BUT does NOT beat the recency-windowed "
                "counter=%.3f (margin=%.3f < %.2f). So the mechanism REVIVES from the stationary "
                "correlation-trivial tie (it does track the moving target a batch counter cannot) "
                "but it is a mechanism-implementation of a trivial online-correlation task, not a "
                "capability a windowed counter lacks. STATIONARY posctrl: batch=%.3f tf=%.3f. "
                "CLAIM-VET-pending." %
                (tf, batch, tf - batch, rec, CHANCE, win, tf - win, MM_WINDOWED_TIE,
                 batch_stat, tf_stat))
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("three_factor=%.3f vs windowed=%.3f (margin=%.3f) vs batch=%.3f (margin=%.3f) vs "
                "recency=%.3f @ SWITCH; seed_pass=%d/%d; difficulty_on(batch<=%.2f)=%s. Above chance "
                "but does not cleanly hit HARD_PASS / MM bands." %
                (tf, win, tf - win, batch, tf - batch, rec, n_seed_pass, len(SEEDS),
                 DIFFICULTY_BATCH_MAX, difficulty_on))

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": "%s: tf=%.3f windowed=%.3f batch=%.3f recency=%.3f @ SWITCH (chance=%.3f)" %
                   (verdict, tf, win, batch, rec, CHANCE),
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "chance": CHANCE,
        "discrim_cond": DISCRIM_COND,
        "n_seed_pass": n_seed_pass,
        "seed_pass": seed_pass,
        "difficulty_on": bool(difficulty_on),
        "difficulty_fail": bool(difficulty_fail),
        "posctrl_ok": bool(posctrl_ok),
        "beats_naive_baselines": bool(beats_naive),
        "ties_windowed_counter": bool(ties_windowed),
        "windowed_detail_SWITCH": windowed_detail_last,
        "mean_acc_by_cond": mean_acc,
        "per_seed": {str(s): per_seed[s] for s in SEEDS},
        "config": {"N_DIM": N_DIM, "M_CAND": M_CAND, "K_SWITCH": K_SWITCH, "DELAY_K": DELAY_K,
                   "T_TRIALS": T_TRIALS, "R_REPLICATES": R_REPLICATES, "SEEDS": SEEDS,
                   "P_FIRE": P_FIRE, "SETTLE": SETTLE, "GAMMA_E": GAMMA_E, "W_LEAK": W_LEAK,
                   "WINDOW_SET": WINDOW_SET, "CONDITIONS": CONDITIONS},
        "bands": {"HP_TF_MIN": HP_TF_MIN, "HP_MARGIN_VS_WINDOWED": HP_MARGIN_VS_WINDOWED,
                  "HP_MARGIN_VS_BATCH": HP_MARGIN_VS_BATCH, "HP_MARGIN_VS_RECENCY": HP_MARGIN_VS_RECENCY,
                  "DIFFICULTY_BATCH_MAX": DIFFICULTY_BATCH_MAX, "CANFAIL_TF_MIN": CANFAIL_TF_MIN,
                  "CANFAIL_TF_VS_BATCH": CANFAIL_TF_VS_BATCH, "MM_WINDOWED_TIE": MM_WINDOWED_TIE,
                  "POSCTRL_MIN": POSCTRL_MIN},
        "final_metrics_atomicity": "tmp_replace",
        "compute_class": "b_sequential_cpu_justified_eligibility_trace_and_online_counter_are_sequential",
        "crlb_n_a": "discrete argmax over M candidates; analytic chance floor 1/M; no continuous noise CRLB",
        "calibration_check": "default_ok_for_this_regime: gamma/W_LEAK a-priori from K (not tuned per run); windowed counter oracle-selected (generous to baseline)",
        "hp_scope": {"three_factor": ["HP_TF_MIN", "HP_MARGIN_VS_WINDOWED", "HP_MARGIN_VS_BATCH",
                                      "HP_MARGIN_VS_RECENCY"],
                     "batch_counter": ["must_fail_control_difficulty_gate"],
                     "windowed_counter": ["strong_baseline_no_hard_pass_floor"],
                     "recency": ["must_fail_null_no_hard_pass_floor"]},
        "prior_work": ("Non-stationary revival of exp_reward_contingency_credit_assignment_v1 "
                       "(VET a33fada3 correlation-triviality + verbatim revival criterion). REUSES "
                       "the eligibility x RPE machinery; CHANGE = moving c* (switch every K) + "
                       "batch/windowed contingency-counter baselines. CLAIM-VET-pending."),
    }
    if belief_samples_last is not None and len(belief_samples_last) == len(ARMS):
        try:
            digests = _arms_must_differ(belief_samples_last)
            metrics["arms_differ_verified"] = True
            metrics["arm_belief_digests"] = digests
        except AssertionError as e:
            metrics["arms_differ_verified"] = False
            metrics["arms_differ_error"] = str(e)
    return metrics


def _run_all():
    output_dir = get_output_dir()
    total_units = len(SEEDS) * len(CONDITIONS) * len(ARMS)
    _write_start_marker(output_dir, total_units)
    t0 = time.perf_counter()
    hb_state = {"unit": 0, "total": total_units}
    per_seed = {}
    windowed_detail_last = {}
    belief_samples_last = None
    for s in SEEDS:
        _say("seed %d ..." % s)
        pc, wd, bs = run_seed(s, output_dir, t0, hb_state)
        per_seed[s] = pc
        windowed_detail_last = wd
        belief_samples_last = bs
    elapsed = time.perf_counter() - t0
    metrics = aggregate_and_verdict(per_seed, windowed_detail_last, belief_samples_last, elapsed)
    _write_metrics_atomic(output_dir, metrics)
    return metrics, output_dir


def self_test():
    """Exercise the REAL tracking-rule code path at tiny scale; assert mechanism direction."""
    _say("SELF-TEST start (real code path).")
    n, m, t = 96, 5, 6 * K_SWITCH
    seed = 7

    # 1. arms produce DIFFERENT belief sequences (bit-identical bug guard) on identical schedule.
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 100003)
    sched = make_schedule(gen, m, t, K_SWITCH, True)
    g2 = torch.Generator(device=DEVICE); g2.manual_seed(999)
    samples = {
        "three_factor": run_three_factor(g2, sched, n, m),
        "recency": run_recency(sched, m),
        "batch_counter": _counter_beliefs(sched, m, None),
        "windowed_counter": _counter_beliefs(sched, m, 30),
    }
    d = _arms_must_differ(samples)
    assert len(set(d.values())) == len(samples), "arms not distinct"
    _say("arms_differ OK: %s" % {k: v[:8] for k, v in d.items()})

    # 2. DIRECTIONAL mechanism check on real code (tiny but full pipeline).
    def acc(arm, cond, reps=4):
        r = run_arm_cond(seed, arm, cond, n, m, t, reps)
        return r["acc"], r
    chance = 1.0 / m
    tf_sw, _ = acc("three_factor", "SWITCH")
    batch_sw, _ = acc("batch_counter", "SWITCH")
    win_sw, win_res = acc("windowed_counter", "SWITCH")
    rec_sw, _ = acc("recency", "SWITCH")
    batch_st, _ = acc("batch_counter", "STATIONARY")
    tf_st, _ = acc("three_factor", "STATIONARY")
    _say("acc @SWITCH: tf=%.3f windowed=%.3f(best_w=%s) batch=%.3f recency=%.3f | "
         "@STATIONARY: batch=%.3f tf=%.3f (chance=%.3f)" %
         (tf_sw, win_sw, win_res.get("best_window"), batch_sw, rec_sw, batch_st, tf_st, chance))

    # 3. DIRECTIONAL assertions (the revival claim, verified in real code at tiny scale):
    assert batch_sw <= 0.45, \
        "DIFFICULTY: batch counter must FAIL @SWITCH (non-stationarity bites); got %.3f" % batch_sw
    assert tf_sw >= 0.45, \
        "three_factor must TRACK the moving c* @SWITCH; got %.3f" % tf_sw
    assert (tf_sw - batch_sw) >= 0.15, \
        "three_factor must beat the batch counter @SWITCH; margin %.3f" % (tf_sw - batch_sw)
    assert rec_sw <= 0.45, \
        "recency null must FAIL @SWITCH (reward-agnostic); got %.3f" % rec_sw
    assert batch_st >= 0.80, \
        "POSCTRL: batch counter must ACE @STATIONARY (v1 triviality); got %.3f" % batch_st
    assert tf_st >= 0.80, \
        "POSCTRL: three_factor must ACE @STATIONARY; got %.3f" % tf_st
    _say("SELF-TEST PASS: non-stationarity kills the batch counter; three_factor tracks; "
         "recency null fails; stationary posctrl reproduces v1 triviality. "
         "(windowed-counter MM check deferred to smoke/full.)")
    return True


def smoke_gate():
    """Full-M/N/K-regime small-block run + discriminator-fires + baseline-in-band asserts."""
    metrics, output_dir = _run_all()
    ma = metrics["mean_acc_by_cond"]
    tf = ma[DISCRIM_COND]["three_factor"]
    batch = ma[DISCRIM_COND]["batch_counter"]
    win = ma[DISCRIM_COND]["windowed_counter"]
    rec = ma[DISCRIM_COND]["recency"]
    _say("SMOKE mean_acc: %s" % json.dumps(ma))
    _say("SMOKE windowed_detail: %s" % json.dumps(metrics.get("windowed_detail_SWITCH", {})))
    _say("SMOKE verdict=%s :: %s" % (metrics["verdict"], metrics["verdict_msg"]))
    assert metrics.get("arms_differ_verified", False), "arms_differ failed in smoke"
    assert not metrics["difficulty_fail"], \
        "SMOKE difficulty_fail: batch counter did NOT fail @SWITCH (non-stationarity did not bite)"
    assert metrics["difficulty_on"], \
        "SMOKE batch_counter=%.3f not at/below %.2f @SWITCH (must fail by construction)" % \
        (batch, DIFFICULTY_BATCH_MAX)
    assert 0.05 < tf < 0.95, "SMOKE three_factor=%.3f not in band (0.05,0.95) @SWITCH" % tf
    assert (tf - max(batch, rec)) >= 0.15, \
        "SMOKE discriminator did not fire: three_factor - max(batch,recency) = %.3f" % \
        (tf - max(batch, rec))
    assert metrics["posctrl_ok"], \
        "SMOKE STATIONARY posctrl failed (batch/tf did not ace stationary -> bug, not non-stationarity)"
    _say("SMOKE GATE PASS. (windowed MM outcome reported; not a gate.)")
    return metrics


def main():
    if RUN_MODE == "self_test":
        self_test()
        return
    if RUN_MODE == "smoke":
        smoke_gate()
        return
    metrics, output_dir = _run_all()
    _say("FULL verdict=%s :: %s" % (metrics["verdict"], metrics["verdict_msg"]))
    _say("metrics -> %s" % os.path.join(output_dir, "metrics.json"))


if __name__ == "__main__":
    _od = get_output_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
