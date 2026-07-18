"""exp_three_factor_eligibility_distal_credit_v1 -- three-factor eligibility-trace plasticity
solves DELAYED (distal) credit assignment that the rank-1 reward-modulated Hebbian rule
structurally cannot.

WHAT / WHY (glass-box, self-contained):
  The brain-learning drill (Lane A, credit-assignment) established: two-factor reward-modulated
  plasticity (delta_w = modulator * pre*post applied at the update moment) CANNOT solve the distal
  reward problem -- if the global reward/teaching signal arrives k steps AFTER the causal
  coincidence, with DISTRACTOR activity in between, the modulator credits whatever synapses are
  active AT REWARD TIME (the distractors), not the causal ones.
  The brain's fix (Fremaux-Gerstner 2016 three-factor review; Izhikevich 2007 "Solving the distal
  reward problem"; Gerstner-Lehmann-Liakoni 2018 behavioral-timescale eligibility traces): a
  DECAYING ELIGIBILITY TRACE at each synapse tags pre/post coincidence, and plasticity consolidates
  only when the delayed global neuromodulator arrives to gate it:
      delta_w = eligibility_trace x neuromodulator
  Because the causal pair fires at a FIXED lag before every reward, its trace is CONSISTENTLY
  present when reward arrives; distractors fire at decorrelated lags and average out over trials.

PRIOR WORK (credit + build-on, NOT rediscovery):
  exp_substrate_dual_trace_sequential_neuromod_LM_v1.py (cert atom
  dual_trace_sequential_neuromodulator_separated_eligibility_traces_break_single_scalar_modulator_floor,
  tier MEASURED_MECHANISM) already showed dual separated eligibility traces beat the rank-1 Hebbian
  single-scalar-modulator floor -- but on a LANGUAGE-MODELING BPC task (absolute bpc weak, NOT a
  language capability; the credit-assignment mechanism was confounded with the LM objective).
  THIS cell isolates the PURE delayed-credit-assignment capability: an explicit delay k with
  distractors, frequency-matched lures, and a delay-length curve. The rank-1 reward-modulated
  delta-rule form is reused directly from that cell's ARM_BASELINE (cf-RPE) and from R7
  (exp_wave14c_r7_surprise_closedloop_replay_v1.py, commit dc87d9a06): W += modulator * outer(post, pre).

THE DECISIVE TASK (distal credit, Izhikevich-2007-style, frequency-matched):
  M candidate pairs {(c_i -> t_i)}, all random bipolar HD vectors. Exactly one (c*) is the causal /
  rewarded pair (fixed across trials). Each trial (episode):
    1. Fire the M-1 LURES (frequency-matched, unrewarded) in random order, one per step.
    2. Fire the causal pair c* -> t*.
    3. Fire k FRESH random DISTRACTOR pairs (the delay window; decorrelated identities).
    4. Deliver global reward r = +1.
  All M candidates fire EXACTLY ONCE per trial (frequency-matched, so pure frequency cannot pick c*);
  c* fires at a FIXED lag k before reward (temporal contingency); lures fire at RANDOM larger lags.
  Metric = credit_accuracy = P( argmax_i [ (W @ c_i) . t_i ] == c* ) over R independent replicates.
  Chance = 1/M.

ARMS (ONE VARIABLE = eligibility persistence gamma; same code path otherwise):
  ARM_HEBBIAN_IMMEDIATE (baseline = the current substrate rule): gamma = 0.0. Eligibility holds only
    the current step's coincidence; at reward W += lr * r * E credits the LAST pair before reward
    (a fresh distractor at k>=1). This IS the substrate's reward-modulated rank-1 cf-RPE rule with
    no eligibility persistence. STRUCTURALLY FAILS distal credit (must-fail control).
  ARM_THREE_FACTOR (mechanism): gamma = 0.9 (tau ~ 10). Eligibility E = gamma*E + outer(post, pre)
    per step (reset per episode); at reward W += lr * r * E. c*'s trace survives the delay ->
    credited selectively. delta_w = eligibility_trace x neuromodulator.
  ARM_UNGATED_HEBBIAN (frequency control): W += lr * outer(post, pre) every pair event, ignores
    reward. All M candidates equally frequent -> ties -> chance. Proves the task is NOT
    frequency-solvable (difficulty-on control).

SANITY: at delay k=0 (reward immediately after c*, no distractors between) the immediate baseline
  credits c* correctly -> baseline ties three-factor. As k grows the baseline collapses to chance
  while three-factor bridges until gamma^k decays below the distractor noise floor (the bridging
  horizon = the delay-length curve).

BANDS (credit_accuracy; chance = 1/M = 0.125 for M=8; strictly above floor per META_RULE_L):
  HARD_PASS (ARM_THREE_FACTOR): credit_accuracy >= 0.70 at delay k=4, AND
    (three_factor - hebbian_immediate) >= 0.40 at k=4, on >= 2/3 seeds.
  MUST-FAIL control fires (ARM_HEBBIAN_IMMEDIATE): credit_accuracy <= 0.30 at k=4.
    If baseline > 0.50 at k>=4 -> DESIGN_FAIL (delay did not isolate credit assignment).
  SANITY (k=0): both immediate and three_factor >= 0.60 (within 0.20 of each other).
  CAN-FAIL / HARD_FAIL_TRACE_INSUFFICIENT: three_factor < 0.50 at k=4 -> real negative
    (trace too noisy / substrate cannot hold eligibility) -> brain-check what is missing.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, justified -- the eligibility trace has a genuine
  SEQUENTIAL dependency (E[t] depends on E[t-1]) and this cell IS the substrate learning-rule being
  validated (bit-identical CPU reference); full wall time < a few minutes on CPU. device='cpu'
  default (runner does not pass argv). Storage: no_storage / no_composition (single heteroassociative
  W per replicate; not multi-item sharded/bundled -> sharded-default rule N/A).

CELL-TEMPLATE MANDATORY:
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash)
  - final_metrics_atomicity = tmp_replace
  - baseline_in_band at smoke (immediate baseline near chance at k>=4; three_factor in band)
  - discriminator survives scale: smoke asserts three_factor - immediate margin fires at delay k>=2
  - crlb_n/a: discrete argmax over M candidates; analytic chance floor 1/M (no continuous noise CRLB)
  - all numbers CITED@ (brain lit) / THEORETICAL@ (chance=1/M) / MEASURED@ (from disk)
  - start marker + crash metrics + heartbeat + atomic write

CITATIONS:
  Izhikevich (2007) "Solving the distal reward problem through linkage of STDP and dopamine
    signaling" Cerebral Cortex 17:2443. CITED
  Fremaux & Gerstner (2016) "Neuromodulated STDP and theory of three-factor learning rules"
    Frontiers in Neural Circuits. CITED
  Gerstner, Lehmann, Liakoni, Corneil, Brea (2018) "Eligibility traces and plasticity on
    behavioral time scales" Frontiers in Neural Circuits. CITED
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "three_factor_eligibility_distal_credit_v1"
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
if RUN_MODE == "self_test":
    N_DIM = 64
    M_CAND = 4
    T_TRIALS = 20
    R_REPLICATES = 4
    DELAYS = [0, 4]
    SEEDS = [7]
elif RUN_MODE == "smoke":
    N_DIM = 128
    M_CAND = 8
    T_TRIALS = 80
    R_REPLICATES = 12
    DELAYS = [0, 2, 4]
    SEEDS = [7, 13]
else:  # full
    N_DIM = 256
    M_CAND = 8
    T_TRIALS = 150
    R_REPLICATES = 16
    DELAYS = [0, 1, 2, 4, 8]
    SEEDS = [7, 13, 19]

GAMMA_THREE_FACTOR = 0.9   # eligibility decay; tau ~ 10 steps. CITED (Gerstner 2018 behavioral trace)
LR = 1.0
CHANCE = 1.0 / M_CAND

ARMS = ["hebbian_immediate", "three_factor", "ungated_hebbian"]

# HARD_PASS / control bands
HP_ACC_THREE_FACTOR = 0.70
HP_MARGIN_VS_BASELINE = 0.40
CONTROL_FAIL_MAX = 0.30       # baseline must be at/below this at k>=4 (must-fail fires)
DESIGN_FAIL_BASELINE = 0.50   # baseline above this at k>=4 => delay did not isolate credit
SANITY_K0_MIN = 0.60          # both arms high at k=0
CANFAIL_MIN = 0.50            # three_factor below this at k=4 => HARD_FAIL_TRACE_INSUFFICIENT
DISCRIM_DELAY = 4             # the delay at which HARD_PASS bands are evaluated
SANITY_DELAY = 0


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


def run_replicate(gen, arm, delay, n, m, t_trials):
    """One independent distal-credit problem. Returns True if credit correctly assigned to c*.

    Real substrate learning-rule code path (rank-1 outer-product delta-rule + eligibility trace).
    """
    gamma = GAMMA_THREE_FACTOR if arm == "three_factor" else 0.0

    # M candidate pairs (cue -> target), random bipolar. Index 0 is the causal/rewarded pair c*.
    cues = torch.stack([_bipolar(gen, n) for _ in range(m)])      # (m, n)
    tgts = torch.stack([_bipolar(gen, n) for _ in range(m)])      # (m, n)
    star = 0

    W = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    E = torch.zeros((n, n), dtype=DTYPE, device=DEVICE)
    lure_idx = [i for i in range(m) if i != star]

    for _ in range(t_trials):
        E.zero_()  # eligibility resets per episode (standard)
        # 1. fire lures in random order (frequency-matched, unrewarded)
        perm = torch.randperm(len(lure_idx), generator=gen).tolist()
        events = [lure_idx[p] for p in perm]  # candidate-index events
        # 2. fire causal pair c*
        events.append(star)
        # process candidate events (pre=cue, post=tgt)
        for ci in events:
            if arm == "ungated_hebbian":
                W.addr_(tgts[ci], cues[ci], alpha=LR)  # W += lr * outer(post, pre)
            else:
                E.mul_(gamma)
                E.addr_(tgts[ci], cues[ci])            # E = gamma*E + outer(post, pre)
        # 3. fire k fresh distractor pairs (delay window, decorrelated identities)
        for _d in range(delay):
            pre = _bipolar(gen, n)
            post = _bipolar(gen, n)
            if arm == "ungated_hebbian":
                W.addr_(post, pre, alpha=LR)
            else:
                E.mul_(gamma)
                E.addr_(post, pre)
        # 4. delayed global reward r=+1 gates the trace (three-factor: delta_w = E x modulator)
        if arm != "ungated_hebbian":
            W.add_(E, alpha=LR)  # W += lr * r * E   (r = +1)

    # readout: credit_score(c_i) = (W @ c_i) . t_i ; argmax should be c*
    resp = cues @ W.t()               # (m, n) : row i = W @ c_i
    scores = (resp * tgts).sum(dim=1)  # (m,)
    pred = int(torch.argmax(scores).item())
    return pred == star, W


def run_arm_delay(seed, arm, delay, n, m, t_trials, r_reps):
    """credit_accuracy over r_reps independent replicates. Returns (acc, last_W)."""
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 100003 + delay * 9176 + hash_arm(arm))
    correct = 0
    last_W = None
    for _ in range(r_reps):
        ok, W = run_replicate(gen, arm, delay, n, m, t_trials)
        correct += 1 if ok else 0
        last_W = W
    return correct / float(r_reps), last_W


def hash_arm(arm):
    return int(hashlib.sha256(arm.encode()).hexdigest()[:8], 16) % 100000


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
    """Returns dict: {delay: {arm: acc}} plus a sample W per arm (at DISCRIM_DELAY) for hash check."""
    per_delay = {}
    sample_W = {}
    total_units = len(DELAYS) * len(ARMS)
    for d in DELAYS:
        per_delay[d] = {}
        for arm in ARMS:
            acc, W = run_arm_delay(seed, arm, d, N_DIM, M_CAND, T_TRIALS, R_REPLICATES)
            per_delay[d][arm] = acc
            if d == DISCRIM_DELAY:
                sample_W[arm] = W
            hb_state["unit"] += 1
            _emit_heartbeat(output_dir, hb_state["unit"], hb_state["total"],
                            time.perf_counter() - t0,
                            extra={"seed": seed, "delay": d, "arm": arm, "acc": round(acc, 4)})
    return per_delay, sample_W


def aggregate_and_verdict(per_seed, sample_W_last, elapsed_s):
    # mean accuracy per (delay, arm) across seeds
    mean_acc = {}
    for d in DELAYS:
        mean_acc[d] = {}
        for arm in ARMS:
            vals = [per_seed[s][d][arm] for s in SEEDS]
            mean_acc[d][arm] = float(np.mean(vals))

    # per-seed HARD_PASS check at DISCRIM_DELAY
    seed_pass = []
    for s in SEEDS:
        tf = per_seed[s][DISCRIM_DELAY]["three_factor"]
        hb = per_seed[s][DISCRIM_DELAY]["hebbian_immediate"]
        ok = (tf >= HP_ACC_THREE_FACTOR) and ((tf - hb) >= HP_MARGIN_VS_BASELINE)
        seed_pass.append(ok)
    n_seed_pass = sum(1 for b in seed_pass if b)

    tf_k = mean_acc[DISCRIM_DELAY]["three_factor"]
    hb_k = mean_acc[DISCRIM_DELAY]["hebbian_immediate"]
    ug_k = mean_acc[DISCRIM_DELAY]["ungated_hebbian"]

    # controls
    control_fires = hb_k <= CONTROL_FAIL_MAX
    design_fail = hb_k > DESIGN_FAIL_BASELINE
    sanity_ok = (SANITY_DELAY in mean_acc) and \
        (mean_acc[SANITY_DELAY]["hebbian_immediate"] >= SANITY_K0_MIN) and \
        (mean_acc[SANITY_DELAY]["three_factor"] >= SANITY_K0_MIN)
    canfail_trace_insufficient = tf_k < CANFAIL_MIN

    # bridging horizon: largest delay where three_factor mean acc >= CANFAIL_MIN
    horizon = None
    for d in sorted(DELAYS):
        if mean_acc[d]["three_factor"] >= CANFAIL_MIN:
            horizon = d

    if design_fail:
        verdict = "DESIGN_FAIL"
        vmsg = ("baseline hebbian_immediate acc=%.3f > %.2f at k=%d: the delay did not isolate "
                "credit assignment (must-fail control did not fire)." % (hb_k, DESIGN_FAIL_BASELINE, DISCRIM_DELAY))
    elif not sanity_ok:
        verdict = "SANITY_FAIL"
        vmsg = ("k=0 sanity failed: immediate=%.3f three_factor=%.3f (need both >= %.2f). "
                "reward-modulated update should work when reward is immediate." %
                (mean_acc[SANITY_DELAY]["hebbian_immediate"], mean_acc[SANITY_DELAY]["three_factor"], SANITY_K0_MIN))
    elif canfail_trace_insufficient:
        verdict = "HARD_FAIL_TRACE_INSUFFICIENT"
        vmsg = ("three_factor acc=%.3f < %.2f at k=%d: eligibility trace could not bridge the delay "
                "(trace too noisy / substrate cannot hold eligibility). Real negative -> brain-check." %
                (tf_k, CANFAIL_MIN, DISCRIM_DELAY))
    elif n_seed_pass >= 2 and control_fires:
        verdict = "HARD_PASS"
        vmsg = ("three_factor eligibility-trace SOLVES distal credit: acc=%.3f vs hebbian_immediate "
                "%.3f (margin=%.3f) at k=%d; %d/3 seeds pass; must-fail control fired (baseline<=%.2f); "
                "ungated-frequency control=%.3f (chance=%.3f); bridging horizon k=%s." %
                (tf_k, hb_k, tf_k - hb_k, DISCRIM_DELAY, n_seed_pass, CONTROL_FAIL_MAX, ug_k, CHANCE, str(horizon)))
    else:
        verdict = "MIDDLE_BAND"
        vmsg = ("three_factor acc=%.3f vs baseline %.3f (margin=%.3f) at k=%d; seed_pass=%d/3; "
                "control_fires=%s. Above chance but below HARD_PASS bands." %
                (tf_k, hb_k, tf_k - hb_k, DISCRIM_DELAY, n_seed_pass, control_fires))

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": "%s: three_factor=%.3f hebbian_immediate=%.3f margin=%.3f k=%d horizon=%s" %
                   (verdict, tf_k, hb_k, tf_k - hb_k, DISCRIM_DELAY, str(horizon)),
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "chance": CHANCE,
        "discrim_delay": DISCRIM_DELAY,
        "n_seed_pass": n_seed_pass,
        "seed_pass": seed_pass,
        "control_fires": bool(control_fires),
        "design_fail": bool(design_fail),
        "sanity_ok": bool(sanity_ok),
        "bridging_horizon_k": horizon,
        "mean_acc_by_delay": {str(d): mean_acc[d] for d in DELAYS},
        "per_seed": {str(s): {str(d): per_seed[s][d] for d in DELAYS} for s in SEEDS},
        "gamma_three_factor": GAMMA_THREE_FACTOR,
        "config": {"N_DIM": N_DIM, "M_CAND": M_CAND, "T_TRIALS": T_TRIALS,
                   "R_REPLICATES": R_REPLICATES, "DELAYS": DELAYS, "SEEDS": SEEDS},
        "final_metrics_atomicity": "tmp_replace",
        "compute_class": "b_sequential_cpu_justified_eligibility_trace_is_substrate_primitive",
        "crlb_n_a": "discrete argmax over M candidates; analytic chance floor 1/M; no continuous noise CRLB",
        "prior_work": ("builds on cert atom dual_trace_sequential_neuromodulator... (MEASURED_MECHANISM, "
                       "LM-BPC regime); this cell isolates pure delayed-credit-assignment (delay+distractors)."),
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
    total_units = len(SEEDS) * len(DELAYS) * len(ARMS)
    _write_start_marker(output_dir, total_units)
    t0 = time.perf_counter()
    hb_state = {"unit": 0, "total": total_units}
    per_seed = {}
    sample_W_last = None
    for s in SEEDS:
        _say("seed %d ..." % s)
        pd, sw = run_seed(s, output_dir, t0, hb_state)
        per_seed[s] = pd
        sample_W_last = sw
    elapsed = time.perf_counter() - t0
    metrics = aggregate_and_verdict(per_seed, sample_W_last, elapsed)
    _write_metrics_atomic(output_dir, metrics)
    return metrics, output_dir


def self_test():
    """Exercise the REAL learning-rule code path at tiny scale; assert mechanism direction."""
    _say("SELF-TEST start (real code path).")

    # 1. arms produce DIFFERENT W (bit-identical bug guard)
    def _W(arm):
        g = torch.Generator(device=DEVICE); g.manual_seed(42)
        _, W = run_replicate(g, arm, 4, 64, 4, 30)
        return W
    Ws = {a: _W(a) for a in ARMS}
    d = _arms_must_differ(Ws)
    assert len(set(d.values())) == len(ARMS), "arms not distinct"
    _say("arms_differ OK: %s" % {k: v[:8] for k, v in d.items()})

    # 2. gamma=0 immediate baseline must NOT hold current-step trace beyond one step:
    #    at delay=0 it should credit c* (freshest); at delay>=2 it should NOT (distractor freshest).
    def acc(arm, delay, seed=7, reps=24, n=96, m=6, t=120):
        a, _ = run_arm_delay(seed, arm, delay, n, m, t, reps)
        return a
    imm_k0 = acc("hebbian_immediate", 0)
    imm_k4 = acc("hebbian_immediate", 4)
    tf_k0 = acc("three_factor", 0)
    tf_k4 = acc("three_factor", 4)
    ug_k4 = acc("ungated_hebbian", 4)
    chance = 1.0 / 6
    _say("acc immediate k0=%.3f k4=%.3f | three_factor k0=%.3f k4=%.3f | ungated k4=%.3f (chance=%.3f)"
         % (imm_k0, imm_k4, tf_k0, tf_k4, ug_k4, chance))

    # 3. DIRECTIONAL assertions (the mechanism claim, verified in real code):
    assert imm_k0 >= 0.60, "immediate baseline should credit c* when reward is IMMEDIATE (k=0); got %.3f" % imm_k0
    assert imm_k4 <= 0.40, "immediate baseline must FAIL distal credit at k=4 (must-fail control); got %.3f" % imm_k4
    assert tf_k4 >= 0.60, "three_factor must bridge the delay at k=4; got %.3f" % tf_k4
    assert (tf_k4 - imm_k4) >= 0.30, "three_factor must beat immediate at k=4 by >=0.30; got %.3f" % (tf_k4 - imm_k4)
    assert ug_k4 <= 0.45, "ungated-frequency control should be near chance (task not frequency-solvable); got %.3f" % ug_k4
    _say("SELF-TEST PASS: mechanism direction confirmed on real code path.")
    return True


def smoke_gate():
    """Small-grid run + explicit discriminator-fires + baseline-in-band asserts."""
    metrics, output_dir = _run_all()
    ma = metrics["mean_acc_by_delay"]
    tf_k4 = ma[str(DISCRIM_DELAY)]["three_factor"]
    hb_k4 = ma[str(DISCRIM_DELAY)]["hebbian_immediate"]
    # smoke uses DELAYS with max 4; discriminator must fire at k=DISCRIM_DELAY
    _say("SMOKE mean_acc: %s" % json.dumps(ma))
    _say("SMOKE verdict=%s :: %s" % (metrics["verdict"], metrics["verdict_msg"]))
    assert metrics.get("arms_differ_verified", False), "arms_differ failed in smoke"
    assert not metrics["design_fail"], "SMOKE design_fail: baseline not isolated by delay"
    assert (tf_k4 - hb_k4) >= 0.30, "SMOKE discriminator did not fire: margin=%.3f" % (tf_k4 - hb_k4)
    assert hb_k4 <= 0.40, "SMOKE must-fail control did not fire: baseline=%.3f" % hb_k4
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
