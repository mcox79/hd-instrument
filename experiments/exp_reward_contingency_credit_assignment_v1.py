"""exp_reward_contingency_credit_assignment_v1 -- the DECISIVE reward-contingency credit
assignment test. Kills the two artifacts the three-factor VET (acc6a02c) exposed in
exp_three_factor_eligibility_distal_credit_v1 (commit 4dc4ab4c6): (1) reward was
UNCONDITIONAL (nothing to discover -- c* hardcoded at index 0), and (2) c* was the
MOST-RECENT candidate (positional recency), so randomizing its position collapsed the
"credit" to chance. That cell was a CONSTRUCTION-PROOF, not credit discovery.

WHAT / WHY (glass-box, self-contained):
  Genuine reward-contingency credit assignment = discover, across many trials, WHICH cue
  predicts a (delayed) reward, when that cue is NOT identifiable by frequency, recency, or
  temporal-position. This is the Rescorla-Wagner / TD contingency problem solved by a
  three-factor eligibility-trace plasticity rule (eligibility x neuromodulator), the most
  experimentally-grounded no-backprop credit mechanism (Fremaux-Gerstner 2016; Izhikevich
  2007 distal reward; Gerstner et al 2018 behavioral-timescale traces; Lillicrap 2020 NGRAD).

  Two artifacts KILLED vs the prior cell:
    ARTIFACT 1 (unconditional reward -> nothing to learn): here reward is CONTINGENT on c*.
      r = +1 iff the specific cue c* fired earlier in the trial, else r = 0. c* fires on a
      RANDOM SUBSET of trials (prob p_fire), so the rule must DISCOVER c* by its cross-trial
      correlation with reward (present-when-rewarded / absent-when-not). No hardcoded index.
    ARTIFACT 2 (positional recency): each trial a RANDOM subset of candidates fires in
      RANDOM ORDER, then a DELAY window of k fresh distractors, then reward. So (a) c* is
      almost never the most-recent EVENT (a distractor is), and (b) among candidates c* is
      last only ~1/|fired| of the time -> a recency heuristic gets chance. Frequency is
      matched (every candidate fires with the same prob p_fire) so pure frequency also fails.

THE TASK (contingency-discovery, recency-killed, delayed):
  M candidate cues {c_i -> t_i}, random bipolar HD vectors; c* is the reward-predicting cue.
  Each trial (episode):
    1. Each candidate fires independently with prob p_fire, in RANDOM order (one event each).
    2. A DELAY window of k FRESH random distractor pairs fires (decorrelated identities).
    3. Global reward r delivered: CONTINGENCY-ON: r=+1 iff c* fired this trial, else 0.
                                  CONTINGENCY-OFF (sanity): r ~ Bernoulli(reward_rate),
                                  INDEPENDENT of c* (matched rate) -> nothing to discover.
  Metric = credit_accuracy = P( argmax_i [ (W @ c_i) . t_i ] == c* ) over R replicates.
  Chance = 1/M.

ARMS (the CREDIT RULE is the variable; event sequence identical across arms):
  ARM_THREE_FACTOR (mechanism): eligibility E = gamma*E + outer(post,pre) per event
    (gamma=0.9, reset per episode); at reward W += lr * (r - r_baseline) * E, where
    r_baseline is a running EMA of reward (dopamine-RPE modulator). The eligibility trace
    BRIDGES the delay (c*'s tag survives the k distractors) and the RPE gating integrates
    the cross-trial contingency (c* present-when-rewarded, never-when-not -> net positive;
    other cues fire independent of reward -> RPE cancels -> net ~0). delta_w = trace x neuromod.
  ARM_HEBBIAN_IMMEDIATE (baseline (c): rank-1 reward-modulated Hebbian, NO eligibility):
    gamma=0.0. Same RPE modulator, but eligibility holds only the CURRENT event -> at reward
    it credits whatever is active AT REWARD TIME = the LAST distractor (fresh random each
    trial). MUST FAIL the distal-credit problem (delay not bridged) -> chance.
  ARM_RECENCY (baseline (a): pure temporal-recency, reward-agnostic): each trial credits the
    MOST-RECENT candidate cue only (W += lr * outer(t_last, c_last)), ignoring reward. Under
    randomized position every candidate is "most-recent" equally often -> ties -> chance.
    MUST FAIL now that c* is not most-recent (proves the recency shortcut is killed). Kept
    reward-AGNOSTIC deliberately: a reward-gated most-recent-candidate rule would leak the
    presence-contingency signal, so the clean recency null ignores reward.
  Baseline (b) chance = 1/M is analytic (also cross-checked by all-arms under CONTINGENCY-OFF).

CONDITIONS (evaluated per arm; ONE variable per comparison):
  ON_k4  (contingency ON,  delay 4): MAIN discriminating condition. HARD_PASS bands here.
  ON_k0  (contingency ON,  delay 0): POSITIVE CONTROL -- with NO delay, the reward-gated
    immediate Hebbian CAN discover c* (candidates active at reward), proving the contingency
    signal IS present and discoverable; the DELAY is what makes eligibility necessary.
  OFF_k4 (contingency OFF, delay 4): SANITY -- reward decoupled from c* (matched rate) ->
    NO arm should discover c* (three_factor -> chance), proving discovery is driven by
    genuine contingency, not a leak/artifact.

BANDS (credit_accuracy; chance = 1/M = 0.1667 for M=6; strictly above floor per META_RULE_L):
  HARD_PASS (ARM_THREE_FACTOR @ ON_k4): credit_accuracy >= 0.70 AND
    (three_factor - recency) >= 0.40 AND (three_factor - hebbian_immediate) >= 0.40,
    on >= 2/3 seeds -> genuine reward-contingency credit assignment (not recency).
  MUST-FAIL controls fire @ ON_k4: recency <= 0.35 AND hebbian_immediate <= 0.35.
    If EITHER > 0.50 @ ON_k4 -> DESIGN_FAIL (recency/delay did not isolate credit assignment).
  SANITY @ OFF_k4: ALL arms <= 0.40; if three_factor > 0.50 -> SANITY_FAIL (leak/artifact).
  POSCTRL @ ON_k0: hebbian_immediate >= 0.50 (signal discoverable without delay) -- diagnostic.
  CAN-FAIL / HARD_FAIL_CONTINGENCY_CREDIT_INSUFFICIENT: three_factor < 0.45 @ ON_k4 ->
    DEFINITIVE, valuable negative: the substrate cannot do reward-contingency credit
    assignment under a fair test (trace too noisy / cannot integrate contingency across
    trials). NOT tortured toward pass -> brain-check what is missing.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, justified -- the eligibility trace has a
  genuine SEQUENTIAL dependency (E[t] depends on E[t-1], reward integrates across trials) and
  this cell IS the substrate learning-rule being validated (bit-identical CPU reference);
  full wall time < a few minutes on CPU. device='cpu' default (runner does not pass argv).
  Storage: no_storage / no_composition (single heteroassociative W per replicate).

CELL-TEMPLATE MANDATORY:
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash on W)
  - final_metrics_atomicity = tmp_replace
  - baseline_in_band at smoke (recency + hebbian_immediate near chance @ ON_k4; three_factor in band)
  - discriminator survives scale: smoke runs the FULL M/N/T regime (M and N unchanged across
    modes; only T/R/seeds shrink) and asserts three_factor - max(recency, immediate) margin fires
  - crlb_n_a: discrete argmax over M candidates; analytic chance floor 1/M (no continuous noise CRLB)
  - all numbers CITED@ (brain lit) / THEORETICAL@ (chance=1/M) / MEASURED@ (from disk)
  - NO hash()-derived seeds (PYTHONHASHSEED-safe): hashlib.sha256 digest for arm seed offset
  - start marker + crash metrics + heartbeat + atomic write
  - progress_logging: per-arm [say] prints flush=True + _heartbeat.jsonl per arm-unit (full < 1800s so
    dense per-step flushing not required by §17, but heartbeat present)

CITATIONS:
  Izhikevich (2007) "Solving the distal reward problem through linkage of STDP and dopamine
    signaling" Cerebral Cortex 17:2443. CITED
  Fremaux & Gerstner (2016) "Neuromodulated STDP and theory of three-factor learning rules"
    Frontiers in Neural Circuits. CITED
  Gerstner, Lehmann, Liakoni, Corneil, Brea (2018) "Eligibility traces and plasticity on
    behavioral time scales" Frontiers in Neural Circuits. CITED
  Rescorla & Wagner (1972) contingency (not contiguity) drives associative learning. CITED
"""

import argparse
import hashlib
import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "reward_contingency_credit_assignment_v1"
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
# M and N (the difficulty axes) are held CONSTANT across modes (discriminator survives scale);
# only T / R / seed-count shrink for cheaper modes.
if RUN_MODE == "self_test":
    N_DIM = 96
    M_CAND = 5
    T_TRIALS = 120
    R_REPLICATES = 8
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 256
    M_CAND = 6
    T_TRIALS = 200
    R_REPLICATES = 12
    SEEDS = [7, 13]
else:  # full
    N_DIM = 256
    M_CAND = 6
    T_TRIALS = 350
    R_REPLICATES = 20
    SEEDS = [7, 13, 19]

GAMMA_THREE_FACTOR = 0.9    # eligibility decay; tau ~ 10 steps. CITED (Gerstner 2018 behavioral trace)
LR = 1.0
P_FIRE = 0.5               # each candidate fires with this prob per trial (frequency matched)
RPE_BASELINE_INIT = 0.5    # EMA reward-baseline init (reward rate = p_fire = 0.5 under both ON and OFF)
RPE_BASELINE_ALPHA = 0.05  # EMA update rate for the dopamine-RPE baseline
CHANCE = 1.0 / M_CAND

ARMS = ["three_factor", "hebbian_immediate", "recency"]
# conditions: (name, contingency_on, delay)
CONDITIONS = [("ON_k4", True, 4), ("ON_k0", True, 0), ("OFF_k4", False, 4)]
DISCRIM_COND = "ON_k4"
POSCTRL_COND = "ON_k0"
SANITY_COND = "OFF_k4"

# HARD_PASS / control bands (credit_accuracy)
HP_ACC_THREE_FACTOR = 0.70
HP_MARGIN_VS_BASELINE = 0.40    # vs BOTH recency and hebbian_immediate
CONTROL_FAIL_MAX = 0.35         # controls must be at/below this @ ON_k4
DESIGN_FAIL_BASELINE = 0.50     # a control above this @ ON_k4 => difficulty not isolated
SANITY_OFF_MAX = 0.40           # all arms at/below this @ OFF_k4
SANITY_OFF_TF_FAIL = 0.50       # three_factor above this @ OFF_k4 => leak/artifact
POSCTRL_IMM_MIN = 0.50          # immediate discovers c* @ ON_k0 (signal present) -- diagnostic
CANFAIL_MIN = 0.45              # three_factor below this @ ON_k4 => HARD_FAIL (definitive negative)


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


def run_replicate(gen, arm, contingency_on, delay, n, m, t_trials, recency_probe=None):
    """One independent contingency-credit problem. Returns (correct: bool, W: tensor).

    Real substrate learning-rule code path (rank-1 outer-product delta-rule + eligibility trace
    + dopamine-RPE modulator). c* index is chosen at random per replicate (no hardcoded index).
    recency_probe (optional dict): accumulates recency-kill diagnostics.
    """
    gamma = GAMMA_THREE_FACTOR if arm == "three_factor" else 0.0

    # M candidate pairs (cue -> target), random bipolar. c* index random per replicate.
    cues = torch.stack([_bipolar(gen, n) for _ in range(m)])      # (m, n)
    tgts = torch.stack([_bipolar(gen, n) for _ in range(m)])      # (m, n)
    star = int(torch.randint(0, m, (1,), generator=gen).item())

    W = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    E = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    reward_rate = float(P_FIRE)   # matched reward rate for CONTINGENCY-OFF
    r_baseline = float(RPE_BASELINE_INIT)

    for _ in range(t_trials):
        E.zero_()  # eligibility resets per episode (standard)

        # 1. which candidates fire this trial (each prob P_FIRE), in RANDOM order.
        fires = (torch.rand(m, generator=gen, device=DEVICE) < P_FIRE)
        fired = [i for i in range(m) if bool(fires[i].item())]
        if len(fired) > 1:
            perm = torch.randperm(len(fired), generator=gen).tolist()
            fired = [fired[p] for p in perm]
        c_star_fired = star in fired
        last_cand = fired[-1] if fired else None

        # process candidate events (pre=cue, post=tgt)
        for ci in fired:
            if arm == "recency":
                pass  # recency handled at trial end (most-recent candidate only)
            else:
                E.mul_(gamma)
                E.addr_(tgts[ci], cues[ci])            # E = gamma*E + outer(post, pre)

        # 2. delay window: k fresh distractor pairs (decorrelated identities)
        for _d in range(delay):
            pre = _bipolar(gen, n)
            post = _bipolar(gen, n)
            if arm != "recency":
                E.mul_(gamma)
                E.addr_(post, pre)

        # recency-kill diagnostics (arm-agnostic; only need a probe once)
        if recency_probe is not None:
            recency_probe["n_trials"] += 1
            if c_star_fired:
                recency_probe["n_cstar_fired"] += 1
                if last_cand == star:
                    recency_probe["n_cstar_last_cand"] += 1
                if delay == 0 and last_cand == star:
                    recency_probe["n_cstar_last_event"] += 1
            # most-recent EVENT is a distractor whenever delay>0 -> never c*

        # 3. reward.
        if contingency_on:
            r = 1.0 if c_star_fired else 0.0
        else:
            r = 1.0 if (float(torch.rand(1, generator=gen, device=DEVICE).item()) < reward_rate) else 0.0

        # 4. plasticity update (the ARM variable).
        if arm == "recency":
            # pure temporal-recency, reward-AGNOSTIC: credit most-recent candidate only.
            if last_cand is not None:
                W.addr_(tgts[last_cand], cues[last_cand], alpha=LR)
        else:
            modulator = r - r_baseline                 # dopamine-RPE modulator
            W.add_(E, alpha=LR * modulator)            # three-factor: delta_w = trace x neuromod
            r_baseline += RPE_BASELINE_ALPHA * (r - r_baseline)  # EMA baseline update

    # readout: credit_score(c_i) = (W @ c_i) . t_i ; argmax should be c*
    resp = cues @ W.t()                # (m, n): row i = W @ c_i
    scores = (resp * tgts).sum(dim=1)  # (m,)
    pred = int(torch.argmax(scores).item())
    return pred == star, W


def run_arm_cond(seed, arm, cond, n, m, t_trials, r_reps, probe=None):
    """credit_accuracy over r_reps independent replicates. Returns (acc, last_W)."""
    _cn, contingency_on, delay = cond
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 100003 + (1 if contingency_on else 0) * 5171 +
                    delay * 9176 + _arm_seed_offset(arm))
    correct = 0
    last_W = None
    for _ in range(r_reps):
        ok, W = run_replicate(gen, arm, contingency_on, delay, n, m, t_trials, recency_probe=probe)
        correct += 1 if ok else 0
        last_W = W
        probe = None  # accumulate diagnostics from first replicate only (cheap, representative)
    return correct / float(r_reps), last_W


def _arms_must_differ(arms_outputs):
    digests = {}
    for name, out in arms_outputs.items():
        b = out.detach().cpu().numpy().tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], \
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b)
    return digests


def run_seed(seed, output_dir, t0, hb_state):
    """Returns {cond_name: {arm: acc}}, sample_W at DISCRIM_COND, recency-kill probe."""
    per_cond = {}
    sample_W = {}
    probe = {"n_trials": 0, "n_cstar_fired": 0, "n_cstar_last_cand": 0, "n_cstar_last_event": 0}
    for cond in CONDITIONS:
        cn = cond[0]
        per_cond[cn] = {}
        for arm in ARMS:
            use_probe = probe if (cn == DISCRIM_COND and arm == "three_factor") else None
            acc, W = run_arm_cond(seed, arm, cond, N_DIM, M_CAND, T_TRIALS, R_REPLICATES, probe=use_probe)
            per_cond[cn][arm] = acc
            if cn == DISCRIM_COND:
                sample_W[arm] = W
            hb_state["unit"] += 1
            _emit_heartbeat(output_dir, hb_state["unit"], hb_state["total"],
                            time.perf_counter() - t0,
                            extra={"seed": seed, "cond": cn, "arm": arm, "acc": round(acc, 4)})
    return per_cond, sample_W, probe


def aggregate_and_verdict(per_seed, probe_last, sample_W_last, elapsed_s):
    mean_acc = {}
    for cond in CONDITIONS:
        cn = cond[0]
        mean_acc[cn] = {}
        for arm in ARMS:
            vals = [per_seed[s][cn][arm] for s in SEEDS]
            mean_acc[cn][arm] = float(np.mean(vals))

    # per-seed HARD_PASS at DISCRIM_COND
    seed_pass = []
    for s in SEEDS:
        tf = per_seed[s][DISCRIM_COND]["three_factor"]
        rec = per_seed[s][DISCRIM_COND]["recency"]
        imm = per_seed[s][DISCRIM_COND]["hebbian_immediate"]
        ok = (tf >= HP_ACC_THREE_FACTOR) and ((tf - rec) >= HP_MARGIN_VS_BASELINE) and \
             ((tf - imm) >= HP_MARGIN_VS_BASELINE)
        seed_pass.append(bool(ok))
    n_seed_pass = sum(1 for b in seed_pass if b)

    tf_k = mean_acc[DISCRIM_COND]["three_factor"]
    rec_k = mean_acc[DISCRIM_COND]["recency"]
    imm_k = mean_acc[DISCRIM_COND]["hebbian_immediate"]
    off_tf = mean_acc[SANITY_COND]["three_factor"]
    off_max = max(mean_acc[SANITY_COND][a] for a in ARMS)
    pos_imm = mean_acc[POSCTRL_COND]["hebbian_immediate"]

    controls_fire = (rec_k <= CONTROL_FAIL_MAX) and (imm_k <= CONTROL_FAIL_MAX)
    design_fail = (rec_k > DESIGN_FAIL_BASELINE) or (imm_k > DESIGN_FAIL_BASELINE)
    sanity_off_ok = (off_max <= SANITY_OFF_MAX) and (off_tf <= SANITY_OFF_TF_FAIL)
    canfail = tf_k < CANFAIL_MIN

    # recency-kill diagnostics (from three_factor probe @ DISCRIM_COND, last seed)
    rk = {}
    if probe_last and probe_last.get("n_cstar_fired", 0) > 0:
        rk["frac_cstar_most_recent_candidate"] = probe_last["n_cstar_last_cand"] / float(probe_last["n_cstar_fired"])
        rk["frac_cstar_most_recent_event"] = probe_last["n_cstar_last_event"] / float(probe_last["n_cstar_fired"])
        rk["n_cstar_fired"] = probe_last["n_cstar_fired"]
        rk["n_trials"] = probe_last["n_trials"]

    if design_fail:
        verdict = "DESIGN_FAIL"
        vmsg = ("a must-fail control cleared %.2f @ %s (recency=%.3f, immediate=%.3f): recency/delay "
                "did not isolate credit assignment." % (DESIGN_FAIL_BASELINE, DISCRIM_COND, rec_k, imm_k))
    elif not sanity_off_ok:
        verdict = "SANITY_FAIL"
        vmsg = ("CONTINGENCY-OFF sanity failed: three_factor=%.3f (max arm=%.3f) @ %s discovered c* "
                "with reward DECOUPLED from c* -> leak/artifact, not genuine contingency." %
                (off_tf, off_max, SANITY_COND))
    elif canfail:
        verdict = "HARD_FAIL_CONTINGENCY_CREDIT_INSUFFICIENT"
        vmsg = ("three_factor acc=%.3f < %.2f @ %s: the substrate CANNOT do reward-contingency credit "
                "assignment under a fair test (recency killed, reward contingent, delay=4). DEFINITIVE "
                "negative -> brain-check what is missing (trace noise / cross-trial integration)." %
                (tf_k, CANFAIL_MIN, DISCRIM_COND))
    elif n_seed_pass >= 2 and controls_fire:
        verdict = "HARD_PASS"
        vmsg = ("three_factor eligibility-trace does GENUINE reward-contingency credit assignment: "
                "acc=%.3f vs recency=%.3f (margin=%.3f) vs immediate=%.3f (margin=%.3f) @ %s "
                "(chance=%.3f); %d/%d seeds pass; both must-fail controls fired (<=%.2f); "
                "CONTINGENCY-OFF sanity: three_factor=%.3f (all arms<=%.3f); recency-kill: "
                "c* is most-recent candidate on %.1f%% of its trials (chance=1/mean_fired)." %
                (tf_k, rec_k, tf_k - rec_k, imm_k, tf_k - imm_k, DISCRIM_COND, CHANCE, n_seed_pass,
                 len(SEEDS), CONTROL_FAIL_MAX, off_tf, off_max,
                 100.0 * rk.get("frac_cstar_most_recent_candidate", float("nan"))))
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("three_factor acc=%.3f vs recency=%.3f (margin=%.3f) vs immediate=%.3f (margin=%.3f) "
                "@ %s; seed_pass=%d/%d; controls_fire=%s. Above chance but below HARD_PASS bands." %
                (tf_k, rec_k, tf_k - rec_k, imm_k, tf_k - imm_k, DISCRIM_COND, n_seed_pass,
                 len(SEEDS), controls_fire))

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": "%s: three_factor=%.3f recency=%.3f immediate=%.3f @ %s (chance=%.3f)" %
                   (verdict, tf_k, rec_k, imm_k, DISCRIM_COND, CHANCE),
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "chance": CHANCE,
        "discrim_cond": DISCRIM_COND,
        "n_seed_pass": n_seed_pass,
        "seed_pass": seed_pass,
        "controls_fire": bool(controls_fire),
        "design_fail": bool(design_fail),
        "sanity_off_ok": bool(sanity_off_ok),
        "posctrl_immediate_ON_k0": pos_imm,
        "posctrl_signal_discoverable": bool(pos_imm >= POSCTRL_IMM_MIN),
        "recency_kill": rk,
        "mean_acc_by_cond": mean_acc,
        "per_seed": {str(s): per_seed[s] for s in SEEDS},
        "gamma_three_factor": GAMMA_THREE_FACTOR,
        "config": {"N_DIM": N_DIM, "M_CAND": M_CAND, "T_TRIALS": T_TRIALS,
                   "R_REPLICATES": R_REPLICATES, "SEEDS": SEEDS, "P_FIRE": P_FIRE,
                   "CONDITIONS": [c[0] for c in CONDITIONS]},
        "final_metrics_atomicity": "tmp_replace",
        "compute_class": "b_sequential_cpu_justified_eligibility_trace_is_substrate_primitive",
        "crlb_n_a": "discrete argmax over M candidates; analytic chance floor 1/M; no continuous noise CRLB",
        "prior_work": ("KILLS the two artifacts of exp_three_factor_eligibility_distal_credit_v1 "
                       "(4dc4ab4c6, VET acc6a02c): unconditional reward (now contingent on c*) + "
                       "positional recency (now randomized position + reward-agnostic recency null)."),
    }
    if sample_W_last is not None:
        try:
            digests = _arms_must_differ(sample_W_last)
            metrics["arms_differ_verified"] = True
            metrics["arm_W_digests"] = digests
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
    sample_W_last = None
    probe_last = None
    for s in SEEDS:
        _say("seed %d ..." % s)
        pc, sw, probe = run_seed(s, output_dir, t0, hb_state)
        per_seed[s] = pc
        sample_W_last = sw
        probe_last = probe
    elapsed = time.perf_counter() - t0
    metrics = aggregate_and_verdict(per_seed, probe_last, sample_W_last, elapsed)
    _write_metrics_atomic(output_dir, metrics)
    return metrics, output_dir


def self_test():
    """Exercise the REAL learning-rule code path at tiny scale; assert mechanism direction."""
    _say("SELF-TEST start (real code path).")

    # 1. arms produce DIFFERENT W (bit-identical bug guard)
    def _W(arm):
        g = torch.Generator(device=DEVICE); g.manual_seed(42)
        _, W = run_replicate(g, arm, True, 4, 64, 5, 60)
        return W
    Ws = {a: _W(a) for a in ARMS}
    d = _arms_must_differ(Ws)
    assert len(set(d.values())) == len(ARMS), "arms not distinct"
    _say("arms_differ OK: %s" % {k: v[:8] for k, v in d.items()})

    # 2. DIRECTIONAL mechanism check on real code (tiny but full pipeline).
    def acc(arm, contingency_on, delay, seed=7, reps=16, n=96, m=5, t=140):
        cond = ("probe", contingency_on, delay)
        a, _ = run_arm_cond(seed, arm, cond, n, m, t, reps)
        return a
    chance = 1.0 / 5
    tf_on4 = acc("three_factor", True, 4)
    rec_on4 = acc("recency", True, 4)
    imm_on4 = acc("hebbian_immediate", True, 4)
    imm_on0 = acc("hebbian_immediate", True, 0)   # positive control: signal discoverable w/o delay
    tf_off4 = acc("three_factor", False, 4)        # sanity: no contingency -> chance
    _say("acc @ON_k4: three_factor=%.3f recency=%.3f immediate=%.3f | @ON_k0 immediate=%.3f | "
         "@OFF_k4 three_factor=%.3f (chance=%.3f)" %
         (tf_on4, rec_on4, imm_on4, imm_on0, tf_off4, chance))

    # 3. DIRECTIONAL assertions (the mechanism claim, verified in real code):
    assert tf_on4 >= 0.55, "three_factor must discover c* @ON_k4 (contingency+delay); got %.3f" % tf_on4
    assert rec_on4 <= 0.45, "recency must FAIL @ON_k4 (position randomized); got %.3f" % rec_on4
    assert imm_on4 <= 0.45, "immediate rank-1 must FAIL @ON_k4 (delay -> credits distractors); got %.3f" % imm_on4
    assert (tf_on4 - rec_on4) >= 0.20, "three_factor must beat recency @ON_k4; margin %.3f" % (tf_on4 - rec_on4)
    assert (tf_on4 - imm_on4) >= 0.20, "three_factor must beat immediate @ON_k4; margin %.3f" % (tf_on4 - imm_on4)
    assert imm_on0 >= 0.40, "POSCTRL: immediate should discover c* @ON_k0 (no delay); got %.3f" % imm_on0
    assert tf_off4 <= 0.45, "SANITY: three_factor must be ~chance @OFF_k4 (no contingency); got %.3f" % tf_off4
    _say("SELF-TEST PASS: contingency-credit-assignment mechanism confirmed; recency+immediate fail; "
         "posctrl+sanity hold.")
    return True


def smoke_gate():
    """Full-M/N-regime small-T run + discriminator-fires + baseline-in-band asserts."""
    metrics, output_dir = _run_all()
    ma = metrics["mean_acc_by_cond"]
    tf = ma[DISCRIM_COND]["three_factor"]
    rec = ma[DISCRIM_COND]["recency"]
    imm = ma[DISCRIM_COND]["hebbian_immediate"]
    _say("SMOKE mean_acc: %s" % json.dumps(ma))
    _say("SMOKE recency_kill: %s" % json.dumps(metrics.get("recency_kill", {})))
    _say("SMOKE verdict=%s :: %s" % (metrics["verdict"], metrics["verdict_msg"]))
    assert metrics.get("arms_differ_verified", False), "arms_differ failed in smoke"
    assert not metrics["design_fail"], "SMOKE design_fail: a control not isolated @ %s" % DISCRIM_COND
    assert (tf - max(rec, imm)) >= 0.25, \
        "SMOKE discriminator did not fire: three_factor - max(control) = %.3f" % (tf - max(rec, imm))
    assert rec <= 0.45 and imm <= 0.45, \
        "SMOKE must-fail controls did not fire: recency=%.3f immediate=%.3f" % (rec, imm)
    assert metrics["sanity_off_ok"], "SMOKE contingency-off sanity failed (leak/artifact)"
    _say("SMOKE GATE PASS.")
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
