"""exp_cls_prioritized_replay_closed_loop_surprise_v1.py

CLOSED-LOOP SURPRISE-PRIORITIZED REPLAY vs UNIFORM replay, at MATCHED BUDGET. The UNTESTED variant after
R7 FALSIFIED a STATIC Hebbian-MIR replay tag: does allocating a FIXED replay budget by the substrate's OWN
CURRENT surprise (additive_map.score_all = 1 - reciprocal_rank, recomputed each block = closed-loop, Schaul
PER style) protect/consolidate old memories BETTER than allocating the same budget UNIFORMLY at random --
or can rank-1 Hebbian storage NOT exploit ANY priority signal?

THE ONE VARIABLE = the REPLAY SAMPLING DISTRIBUTION over a fixed eligible pool at MATCHED budget B/block.
Everything else identical (same store, same net init, same # replay steps, same held-out eval).

ARMS (single variable = which B eligible items get replayed each interference block):
  * no_replay             : sequential, no old replay = McCloskey-Cohen forgetting AND the no-replay FLOOR.
  * uniform_replay        : (REAL BASELINE) B eligible items sampled UNIFORMLY at random each block.
  * surprise_closed_loop  : (MECHANISM) B eligible items sampled ~ (current_surprise)^alpha, surprise
                            RECOMPUTED from the net's CURRENT prediction error EACH block = closed-loop.
                            surprise_i = 1 - reciprocal_rank_i (additive_map.score_all analog; glass-box).
  * surprise_static_snapshot: (CONTROL) B eligible items sampled ~ (surprise_snapshot)^alpha, surprise
                            computed ONCE after the old block and FROZEN (isolates the closed-loop-ness:
                            pre-interference surprise is nearly uninformative, so this is expected ~uniform
                            -- that degeneracy is itself the argument FOR closed-loop recomputation).
  * fresh_net_uniform     : (CONFOUND, equal-compute) fresh net trained ONLY on the union of items UNIFORM
                            replayed. Must NOT recover the independent held-out content (relearnability probe).
  * fresh_net_surprise    : (CONFOUND, equal-compute) fresh net trained ONLY on the union of items SURPRISE
                            replayed. Must NOT recover the independent held-out content.

WHY THIS TEST IS DECISIVE (the deep hypothesis it can falsify):
  Replaying item X does a gradient step toward X's target -- so it DOES protect X. But in a SHARED, rank-
  limited representation (shared tanh hidden + linear readout), protecting the at-risk items may DE-protect
  others (zero-sum). If retention capacity over the eligible pool is FIXED, priority merely RESHUFFLES which
  items survive without ADDING net protected capacity -> delta(surprise - uniform) ~ 0 on TOTAL eligible-pool
  retention. That HARD-FAIL is LOAD-BEARING (per the credit-assignment drill): to ADD protected capacity by
  allocation you need a plasticity rule that can DIFFERENTIALLY WEIGHT updates (three-factor eligibility-
  trace / neuromodulator-gated), which a rank-1 Hebbian outer-product LACKS. CITED@ Schaul 2016 PER (beat
  uniform on 41/49 Atari); Lillicrap 2020 NGRAD three-factor rules; McClelland-McNaughton-O'Reilly 1995 CLS.

DESIGN-GATE (verified at smoke BEFORE full):
  (1) REAL baseline = uniform_replay at MATCHED budget B (not no_replay, not abstain).
  (2) CAN-FAIL: HARD_FAIL if surprise ties/loses to uniform on eligible-pool retention -> rank-1 Hebbian
      can't exploit priority replay; fix = three-factor/eligibility-trace plasticity. VALID informative
      outcome; NOT tortured to avoid it.
  (3) DIFFICULTY-ON: interference forgets (no_replay collapses); replay helps at all (uniform > no_replay);
      INDEPENDENT per-item content so the fresh-net/1-NN generalization-confound is structurally defeated
      (both fresh-net confounds must FAIL on the independent held-out Q).
  (4) ONE variable = the replay sampling distribution (net init / budget / epochs / eval FIXED across arms).

METRICS (retrieval accuracy of each item's OWN independent target over the full old codebook; chance=1/P):
  * PRIMARY / LOAD-BEARING = E-pool retention (the eligible pool the budget is allocated over). This is
    where priority allocation DIRECTLY operates and has the STRONGEST chance; its failure is the cleanest
    "priority is not a lever for rank-1 Hebbian." delta_E = surprise_closed_loop_E - uniform_E.
  * SECONDARY / stricter distributed bonus = Q retention (a FIXED never-replayed held-out set, disjoint from
    the eligible pool, touched by NO arm) -- distributed consolidation via the shared basis.
  * closed_vs_static = surprise_closed_loop_E - surprise_static_snapshot_E (is closed-loop recomputation
    the lever, or does a frozen priority snapshot suffice?).

HARD_PASS (=chain-grade ATTEMPT, VET-pending, NOT self-declared): delta_E >= 0.08 on 2/3 seeds AND surprise
  does not hurt the never-replayed Q (delta_Q >= -0.03) AND difficulty gates on -> closed-loop surprise-
  prioritized replay is a REAL lever for the substrate's consolidation.
HARD_FAIL: delta_E <= 0.02 on 2/3 seeds (ties/loses) -> rank-1 Hebbian can't exploit priority replay; the
  fix is three-factor / eligibility-trace plasticity (NOT dressed as a win).

DEFLATE: self-contained numpy; ASCII-only; local-runnable foreground; glass-box; no external LLM.
"""
from __future__ import annotations
# OMP/OpenBLAS single-thread BEFORE numpy import (OpenBLAS DYNAMIC_ARCH non-determinism on MLP cells; bit-repro)
import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")
_os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH/H + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash over per-arm E-predictions + replay-index sets)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-metrics both tmp+os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retrieval accuracy over a codebook, chance=1/OLD_ITEMS; feasibility = uniform in-band at smoke
# - baseline_in_band at smoke (META_RULE_AG): uniform_E in (0.30,0.90); no_replay collapses; confounds fail Q
# - discriminator survives scale: allocation effect depends on pool/interference/budget, not seeds; smoke=FULL grid 1 seed
# - HARD_PASS strictly above floor: delta_E >= 0.08 (not >= 0); HARD_FAIL delta_E <= 0.02; MIDDLE between
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = len(SHARED_FRAC_GRID) * len(SEEDS); verdict counts
# - no PYTHONHASHSEED nondeterminism: all splits/seeds via fixed ints + deterministic index math + np.random.default_rng
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, json, time, hashlib, platform, traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics, record_gate

ANCHOR_NAME = "cls_prioritized_replay_closed_loop_surprise_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- Config -------------------------------------------------------------------------------------------
N = 256                      # cue (hypervector) dimensionality
D_T = 64                     # target vector dimensionality (independent per-item content)
H = 160                      # shared hidden layer -- distributed/overlapping representation (rank-limited)
OLD_CLASSES = 12             # old classes learned in the first block
OLD_EXEMPLARS = 12           # exemplars per old class -> 144 old items
ELIG_PER_CLASS = 8           # replay-ELIGIBLE exemplars/class -> E = 96 (the pool the budget allocates over)
                             # -> held-out never-replayed Q = 4/class = 48 (touched by NO arm)
B_REPLAY = 12                # MATCHED replay BUDGET: distinct eligible items replayed PER block (12.5% of E).
                             # Scarce budget = most-decisive operating point (reshuffle-vs-add-capacity shows
                             # most when budget is tight) + centers uniform in the measurable band (META_RULE_AG)
ALPHA = 1.0                  # PER priority exponent (proportional). CITED@ Schaul 2016 (alpha=0.6-0.7 typical)
SURPRISE_EPS = 1e-3          # floor so zero-surprise items remain samplable (choice without replacement)
K_INTERFERE = 8              # NEW-class interference blocks trained sequentially
NEW_CPB = 3                  # new classes per interference block
NEW_EXEMPLARS = 12           # exemplars per new class
E_OLD = 400                  # epochs on the old block (memorize independent targets)
E_NEW = 200                  # epochs per new interference block (overfit new -> real forgetting)
LR = 0.04                    # MEASURED@ parent cell: LR>=0.06 diverges (linear MSE readout); 0.04 stable
SHARED_FRAC_GRID = [0.75, 0.55] if not SMOKE else [0.75]
STRUCTURED_FRAC = 0.75
SEEDS = [7] if SMOKE else [7, 17, 23]

OLD_ITEMS = OLD_CLASSES * OLD_EXEMPLARS               # 144
N_ELIG = OLD_CLASSES * ELIG_PER_CLASS                 # 96 replay-eligible
HELDOUT_PER_CLASS = OLD_EXEMPLARS - ELIG_PER_CLASS    # 4
N_HELDOUT = OLD_CLASSES * HELDOUT_PER_CLASS           # 48 never-replayed (Q)
V_CLASSES = OLD_CLASSES + K_INTERFERE * NEW_CPB       # 12 + 24 = 36 total classes
EXPECTED_N_UNITS = len(SHARED_FRAC_GRID) * len(SEEDS)
CHANCE = 1.0 / OLD_ITEMS                              # THEORETICAL@ retrieval chance over old codebook

# HARD-PASS / HARD-FAIL bands (envelope-fail-bands, pre-registered) -- retrieval-accuracy metric in [0,1]
DELTA_E_HP = 0.08            # surprise_closed_loop_E - uniform_E must exceed this (structured end) = a real lever
DELTA_E_HF = 0.02            # <= this on 2/3 seeds -> ties/loses -> priority not a lever for rank-1 Hebbian
DELTA_Q_FLOOR = -0.03        # surprise must not HURT the never-replayed held-out Q (do-no-harm on distributed)
# DIFFICULTY-ON gates (aggregate at structured end):
DIFF_INITIAL_MIN = 0.70      # net LEARNED the independent targets in the first block (else vacuous)
DIFF_NOREPLAY_MAX = 0.35     # no_replay E-retention collapses (forgetting real)
DIFF_UNIFORM_MIN_OVER_FLOOR = 0.10  # uniform_E beats no_replay_E by this (replay budget matters at all)
DIFF_UNIFORM_BAND = (0.30, 0.90)    # uniform_E in measurable band (not saturated, not floored) META_RULE_AG
DIFF_CONFOUND_MAX_Q = 0.10   # BOTH fresh-net confounds FAIL to recover independent held-out Q (independence)


def _bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    x = np.sign(rng.standard_normal(shape))
    x[x == 0] = 1.0
    return x.astype(np.float64)


class RegNet:
    """cue(N) -> hidden(H) tanh -> target(D_T) linear. MSE regression, batch backprop.

    Shared hidden layer = distributed/overlapping (rank-limited) representation. Replaying an item does a
    gradient step toward its target; whether ALLOCATING a fixed replay budget by CURRENT surprise ADDS net
    protected capacity over the eligible pool (vs merely reshuffling which items survive) is the open question.
    """

    def __init__(self, n: int, h: int, d_t: int, rng: np.random.Generator):
        self.W1 = (rng.standard_normal((h, n)) / np.sqrt(n)).astype(np.float64)
        self.W2 = (rng.standard_normal((d_t, h)) / np.sqrt(h)).astype(np.float64)

    def train(self, X: np.ndarray, T: np.ndarray, epochs: int, lr: float) -> None:
        if X.shape[0] == 0:
            return
        m = X.shape[0]
        for _ in range(epochs):
            A1 = np.tanh(X @ self.W1.T)
            Y = A1 @ self.W2.T
            dY = (Y - T) / m
            dW2 = dY.T @ A1
            dA1 = dY @ self.W2
            dZ1 = dA1 * (1.0 - A1 * A1)
            dW1 = dZ1.T @ X
            self.W2 -= lr * dW2
            self.W1 -= lr * dW1

    def output(self, X: np.ndarray) -> np.ndarray:
        A1 = np.tanh(X @ self.W1.T)
        return A1 @ self.W2.T


def _retrieval_acc(pred: np.ndarray, tau_true: np.ndarray, codebook: np.ndarray) -> Tuple[float, np.ndarray]:
    """Nearest-target retrieval accuracy over the full old codebook. Returns (acc, pred_tau)."""
    if pred.shape[0] == 0:
        return 0.0, np.array([], dtype=np.int64)
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-9)
    cn = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-9)
    sims = pn @ cn.T
    pred_tau = sims.argmax(axis=1)
    return float((pred_tau == tau_true).mean()), pred_tau


def _surprise_scores(net: RegNet, X: np.ndarray, tau: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Glass-box surprise = 1 - reciprocal_rank (additive_map.score_all analog).

    For each item: rank of its TRUE target among the full codebook by cosine of the net's CURRENT output;
    reciprocal_rank = 1/rank; surprise = 1 - reciprocal_rank in [0, 1-1/P]. High = model currently fails it.
    """
    pred = net.output(X)
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-9)
    cn = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-9)
    sims = pn @ cn.T                                       # (n, OLD_ITEMS)
    true_sim = sims[np.arange(sims.shape[0]), tau]
    ranks = 1 + (sims > true_sim[:, None]).sum(axis=1)     # strict-greater rank (1 = best)
    rr = 1.0 / ranks
    return 1.0 - rr


def _sample_replay(weights: np.ndarray, elig_idx: np.ndarray, b: int, rng: np.random.Generator) -> np.ndarray:
    """Sample b DISTINCT eligible items without replacement ~ weights (matched budget). weights None=uniform."""
    if b >= elig_idx.shape[0]:
        return elig_idx.copy()
    if weights is None:
        return rng.choice(elig_idx, size=b, replace=False)
    w = np.asarray(weights, dtype=np.float64)
    w = (w + SURPRISE_EPS) ** ALPHA
    w = w / w.sum()
    return rng.choice(elig_idx, size=b, replace=False, p=w)


def _make_old_bank(rng: np.random.Generator, shared_frac: float
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Old bank: cue=[shared class code | independent item probe]; target = UNIQUE per-item bipolar vector."""
    s = int(round(shared_frac * N))
    proto = _bipolar(rng, (OLD_CLASSES, s))
    X = np.zeros((OLD_ITEMS, N), dtype=np.float64)
    for c in range(OLD_CLASSES):
        for e in range(OLD_EXEMPLARS):
            i = c * OLD_EXEMPLARS + e
            X[i, :s] = proto[c]
            X[i, s:] = _bipolar(rng, (N - s,))
    tau = np.arange(OLD_ITEMS, dtype=np.int64)
    codebook = _bipolar(rng, (OLD_ITEMS, D_T))
    return X, tau, codebook


def _make_new_block(rng: np.random.Generator, shared_frac: float, nc: int
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Interference block: same cue structure, fresh random targets (drives forgetting via shared W1/W2)."""
    s = int(round(shared_frac * N))
    proto = _bipolar(rng, (nc, s))
    m = nc * NEW_EXEMPLARS
    X = np.zeros((m, N), dtype=np.float64)
    for j in range(nc):
        for e in range(NEW_EXEMPLARS):
            i = j * NEW_EXEMPLARS + e
            X[i, :s] = proto[j]
            X[i, s:] = _bipolar(rng, (N - s,))
    T = _bipolar(rng, (m, D_T))
    return X, T


def _split_idx() -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic: first ELIG_PER_CLASS exemplars/class -> eligible pool; rest -> never-replayed held-out Q."""
    elig, held = [], []
    for c in range(OLD_CLASSES):
        base = c * OLD_EXEMPLARS
        elig.extend(range(base, base + ELIG_PER_CLASS))
        held.extend(range(base + ELIG_PER_CLASS, base + OLD_EXEMPLARS))
    return np.array(elig, dtype=np.int64), np.array(held, dtype=np.int64)


def _train_replay_arm(mode: str, seed: int, old_X, old_tau, codebook, elig_idx, held_idx, new_blocks
                      ) -> Dict:
    """mode in {none, uniform, surprise_closed, surprise_static}. SAME init across arms (one-variable).

    Matched budget: uniform/surprise_closed/surprise_static each replay EXACTLY B_REPLAY distinct eligible
    items PER block (identical compute). 'none' replays 0 (floor). Returns retention on E-pool and held-out Q.
    """
    net = RegNet(N, H, D_T, np.random.default_rng(seed + 1))
    old_T = codebook[old_tau]
    net.train(old_X, old_T, E_OLD, LR)
    e_init, _ = _retrieval_acc(net.output(old_X[elig_idx]), old_tau[elig_idx], codebook)

    # sampling RNG per-arm (deterministic, distinct stream per mode so arms are not bit-identical)
    mode_salt = {"none": 0, "uniform": 100, "surprise_closed": 200, "surprise_static": 300}[mode]
    srng = np.random.default_rng(seed * 1000 + mode_salt)

    # static snapshot surprise (frozen), computed once after the old block
    snap = None
    if mode == "surprise_static":
        snap = _surprise_scores(net, old_X[elig_idx], old_tau[elig_idx], codebook)

    replayed_counts = np.zeros(elig_idx.shape[0], dtype=np.int64)  # per-eligible replay count over the run
    for b in range(K_INTERFERE):
        Xb, Tb = new_blocks[b]
        if mode == "none":
            trX, trT = Xb, Tb
        else:
            if mode == "uniform":
                sel = _sample_replay(None, elig_idx, B_REPLAY, srng)
            elif mode == "surprise_closed":
                sc = _surprise_scores(net, old_X[elig_idx], old_tau[elig_idx], codebook)  # CLOSED-LOOP recompute
                sel = _sample_replay(sc, elig_idx, B_REPLAY, srng)
            elif mode == "surprise_static":
                sel = _sample_replay(snap, elig_idx, B_REPLAY, srng)
            else:
                raise ValueError("unknown replay mode: %s" % mode)
            # map selected global indices -> position within elig_idx for count tracking
            pos = np.searchsorted(elig_idx, sel)
            replayed_counts[pos] += 1
            trX = np.concatenate([Xb, old_X[sel]])
            trT = np.concatenate([Tb, old_T[sel]])
        net.train(trX, trT, E_NEW, LR)

    e_acc, e_tau = _retrieval_acc(net.output(old_X[elig_idx]), old_tau[elig_idx], codebook)
    q_acc, _ = _retrieval_acc(net.output(old_X[held_idx]), old_tau[held_idx], codebook)
    replayed_union = elig_idx[replayed_counts > 0]
    digest = hashlib.sha256(e_tau.tobytes() + replayed_counts.tobytes()).hexdigest()
    return {"E_retention": round(e_acc, 3), "Q_retention": round(q_acc, 3),
            "E_initial": round(e_init, 3), "n_distinct_replayed": int(replayed_union.shape[0]),
            "total_replay_exposures": int(replayed_counts.sum()), "replayed_union": replayed_union,
            "digest": digest}


def _confound_fresh_net(seed, salt, old_X, old_tau, codebook, replayed_union, elig_idx, held_idx) -> Dict:
    """Fresh net trained ONLY on the union of items an arm replayed (never sees held-out, zero interference).

    Independent per-item content => it can recover only the items it was trained on; MUST FAIL on held-out Q.
    Equal-compute proxy: same LR + a total epoch budget comparable to the online arm's replay exposures.
    """
    net = RegNet(N, H, D_T, np.random.default_rng(seed + salt))
    if replayed_union.shape[0] > 0:
        net.train(old_X[replayed_union], codebook[old_tau[replayed_union]], E_OLD, LR)
    e_acc, _ = _retrieval_acc(net.output(old_X[elig_idx]), old_tau[elig_idx], codebook)
    q_acc, pred_tau = _retrieval_acc(net.output(old_X[held_idx]), old_tau[held_idx], codebook)
    return {"E_retention": round(e_acc, 3), "Q_retention": round(q_acc, 3),
            "digest": hashlib.sha256(pred_tau.tobytes()).hexdigest()}


ARMS = ("no_replay", "uniform_replay", "surprise_closed_loop", "surprise_static_snapshot",
        "fresh_net_uniform", "fresh_net_surprise")


def _run_point(shared_frac: float, seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    old_X, old_tau, codebook = _make_old_bank(rng, shared_frac)
    new_blocks = []
    for b in range(K_INTERFERE):
        new_blocks.append(_make_new_block(rng, shared_frac, NEW_CPB))
    elig_idx, held_idx = _split_idx()

    none = _train_replay_arm("none", seed, old_X, old_tau, codebook, elig_idx, held_idx, new_blocks)
    unif = _train_replay_arm("uniform", seed, old_X, old_tau, codebook, elig_idx, held_idx, new_blocks)
    clos = _train_replay_arm("surprise_closed", seed, old_X, old_tau, codebook, elig_idx, held_idx, new_blocks)
    stat = _train_replay_arm("surprise_static", seed, old_X, old_tau, codebook, elig_idx, held_idx, new_blocks)
    fn_u = _confound_fresh_net(seed, 501, old_X, old_tau, codebook, unif["replayed_union"], elig_idx, held_idx)
    fn_s = _confound_fresh_net(seed, 601, old_X, old_tau, codebook, clos["replayed_union"], elig_idx, held_idx)

    return {"shared_frac": shared_frac, "seed": seed,
            "no_replay": {k: none[k] for k in ("E_retention", "Q_retention", "E_initial")},
            "uniform_replay": {k: unif[k] for k in ("E_retention", "Q_retention", "E_initial",
                                                     "n_distinct_replayed", "total_replay_exposures")},
            "surprise_closed_loop": {k: clos[k] for k in ("E_retention", "Q_retention", "E_initial",
                                                          "n_distinct_replayed", "total_replay_exposures")},
            "surprise_static_snapshot": {k: stat[k] for k in ("E_retention", "Q_retention", "E_initial",
                                                             "n_distinct_replayed", "total_replay_exposures")},
            "fresh_net_uniform": {k: fn_u[k] for k in ("E_retention", "Q_retention")},
            "fresh_net_surprise": {k: fn_s[k] for k in ("E_retention", "Q_retention")},
            "arm_digests": {"no_replay": none["digest"], "uniform_replay": unif["digest"],
                            "surprise_closed_loop": clos["digest"], "surprise_static_snapshot": stat["digest"],
                            "fresh_net_uniform": fn_u["digest"], "fresh_net_surprise": fn_s["digest"]}}


def _difficulty_ok(agg: Dict) -> Tuple[bool, str]:
    base = agg["no_replay"]; unif = agg["uniform_replay"]
    fn_u = agg["fresh_net_uniform"]["Q_retention"]; fn_s = agg["fresh_net_surprise"]["Q_retention"]
    checks = [
        (unif["E_initial"] >= DIFF_INITIAL_MIN, "net_learned_E_initial"),
        (base["E_retention"] <= DIFF_NOREPLAY_MAX, "no_replay_forgets_E"),
        (unif["E_retention"] - base["E_retention"] >= DIFF_UNIFORM_MIN_OVER_FLOOR, "uniform_beats_floor"),
        (DIFF_UNIFORM_BAND[0] < unif["E_retention"] < DIFF_UNIFORM_BAND[1], "uniform_E_in_band"),
        (fn_u <= DIFF_CONFOUND_MAX_Q, "fresh_net_uniform_fails_Q_independence"),
        (fn_s <= DIFF_CONFOUND_MAX_Q, "fresh_net_surprise_fails_Q_independence"),
    ]
    fails = [name for ok, name in checks if not ok]
    return (len(fails) == 0), ("OK" if not fails else "FAILS:" + ",".join(fails))


def run() -> Dict:
    per_unit = [_run_point(sf, s) for sf in SHARED_FRAC_GRID for s in SEEDS]
    points = []
    arms_differ = True
    for sf in SHARED_FRAC_GRID:
        units = [u for u in per_unit if u["shared_frac"] == sf]

        def _mean(arm, key):
            return float(np.mean([u[arm][key] for u in units]))

        agg = {}
        for arm in ARMS:
            keys = [k for k in ("E_retention", "Q_retention", "E_initial",
                                "n_distinct_replayed", "total_replay_exposures") if k in units[0][arm]]
            agg[arm] = {k: round(_mean(arm, k), 3) for k in keys}

        # per-seed HARD_PASS: delta_E >= HP AND delta_Q >= floor
        hp = 0
        deltas_e = []
        for u in units:
            de = u["surprise_closed_loop"]["E_retention"] - u["uniform_replay"]["E_retention"]
            dq = u["surprise_closed_loop"]["Q_retention"] - u["uniform_replay"]["Q_retention"]
            deltas_e.append(de)
            if de >= DELTA_E_HP and dq >= DELTA_Q_FLOOR:
                hp += 1
        hf = sum(1 for de in deltas_e if de <= DELTA_E_HF)  # seeds where surprise ties/loses uniform

        diff_ok, diff_msg = _difficulty_ok(agg)
        for u in units:
            vals = list(u["arm_digests"].values())
            if len(set(vals)) != len(vals):
                arms_differ = False
        points.append({"shared_frac": sf, "agg": agg, "hp_seeds": hp, "hf_seeds": hf,
                       "n_seeds": len(units), "mean_delta_E": round(float(np.mean(deltas_e)), 3),
                       "difficulty_ok": diff_ok, "difficulty_msg": diff_msg})

    return {"points": points, "per_unit": [_strip(u) for u in per_unit], "n_units": len(per_unit),
            "expected_n_units": EXPECTED_N_UNITS, "arms_differ": arms_differ,
            "n_eligible": N_ELIG, "n_never_replayed": N_HELDOUT, "b_replay": B_REPLAY,
            "chance": round(CHANCE, 5)}


def _strip(u: Dict) -> Dict:
    """Drop non-JSON arrays (replayed_union) from per_unit before serialization."""
    out = {}
    for k, v in u.items():
        if isinstance(v, dict):
            out[k] = {kk: vv for kk, vv in v.items() if not isinstance(vv, np.ndarray)}
        else:
            out[k] = v
    return out


def _fmt_curve(points: List[Dict]) -> str:
    segs = []
    for pt in points:
        a = pt["agg"]
        segs.append("SF=%.2f[no=%.3f unif=%.3f clos=%.3f stat=%.3f |Q no=%.3f unif=%.3f clos=%.3f "
                    "|fnQ u=%.3f s=%.3f dE=%.3f hp=%d hf=%d/%d diff=%s]"
                    % (pt["shared_frac"], a["no_replay"]["E_retention"], a["uniform_replay"]["E_retention"],
                       a["surprise_closed_loop"]["E_retention"], a["surprise_static_snapshot"]["E_retention"],
                       a["no_replay"]["Q_retention"], a["uniform_replay"]["Q_retention"],
                       a["surprise_closed_loop"]["Q_retention"], a["fresh_net_uniform"]["Q_retention"],
                       a["fresh_net_surprise"]["Q_retention"], pt["mean_delta_E"], pt["hp_seeds"],
                       pt["hf_seeds"], pt["n_seeds"], "Y" if pt["difficulty_ok"] else "N"))
    return " ".join(segs)


def verdict(r: Dict) -> Tuple[str, str]:
    points = r["points"]
    curve = _fmt_curve(points)
    struct = next(pt for pt in points if abs(pt["shared_frac"] - STRUCTURED_FRAC) < 1e-9)
    ns = struct["n_seeds"]; need = 2 if ns >= 3 else 1
    a = struct["agg"]
    unif_e = a["uniform_replay"]["E_retention"]; clos_e = a["surprise_closed_loop"]["E_retention"]
    stat_e = a["surprise_static_snapshot"]["E_retention"]
    d_e = struct["mean_delta_E"]; d_cs = round(clos_e - stat_e, 3)
    s = ("E-pool retention (chance=%.4f) [no/unif/clos/stat] + held-out-Q + fresh-net-Q confounds: %s | "
         "B=%d matched budget over E=%d, never-replayed Q=%d | arms_differ=%s units=%d/%d"
         % (r["chance"], curve, r["b_replay"], r["n_eligible"], r["n_never_replayed"], r["arms_differ"],
            r["n_units"], r["expected_n_units"]))

    if r["n_units"] != r["expected_n_units"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d. %s" % (r["n_units"], r["expected_n_units"], s))
    if not r["arms_differ"]:
        return ("HARD_FAIL", "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: " + s)
    if not struct["difficulty_ok"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND_REGIME_INCONCLUSIVE: structured-end difficulty gate off (%s) -- "
                "cannot read priority-vs-uniform until interference forgets, uniform is in band, and the "
                "generalization confounds are proven to FAIL. " % struct["difficulty_msg"] + s)

    if struct["hp_seeds"] >= need:
        return ("HARD_PASS",
                "HARD_PASS_PRIORITY_REPLAY_IS_A_LEVER: at the structured end (SHARED_FRAC=%.2f) closed-loop "
                "surprise-prioritized replay (E-retention=%.3f) beats UNIFORM (%.3f) at MATCHED budget by "
                "delta_E=%.3f (>=%.2f) on %d/%d seeds without hurting the never-replayed held-out Q "
                "(closed_vs_static delta=%.3f). Prioritizing replay by the substrate's OWN current surprise "
                "(1-reciprocal_rank) is a REAL consolidation lever. CLAIM-VET-pending, NOT self-declared "
                "chain-grade. " % (STRUCTURED_FRAC, clos_e, unif_e, d_e, DELTA_E_HP, struct["hp_seeds"], ns, d_cs) + s)
    if struct["hf_seeds"] >= need:
        return ("HARD_FAIL",
                "HARD_FAIL_RANK1_HEBBIAN_CANNOT_EXPLOIT_PRIORITY: at the structured end (SHARED_FRAC=%.2f) "
                "closed-loop surprise-prioritized replay (E-retention=%.3f) TIES/LOSES to UNIFORM (%.3f) at "
                "matched budget -- delta_E=%.3f (<=%.2f) on %d/%d seeds. The substrate's rank-1 Hebbian "
                "storage CANNOT exploit priority replay: allocating the fixed budget by current surprise only "
                "RESHUFFLES which items survive in the shared rank-limited representation, it does NOT ADD net "
                "protected capacity. This is NOT a dead end -- it LOCALIZES the fix to the PLASTICITY RULE: "
                "priority replay needs a rule that can DIFFERENTIALLY WEIGHT updates (three-factor eligibility-"
                "trace / neuromodulator-gated), which a rank-1 outer-product lacks. NOT dressed as a win. " % (
                    STRUCTURED_FRAC, clos_e, unif_e, d_e, DELTA_E_HF, struct["hf_seeds"], ns) + s)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_WEAK_LEVER: closed-loop surprise beats uniform at the structured end but below the "
            ">=%.2f delta_E bar on >=%d seeds (delta_E=%.3f) -- weak/partial priority effect, not decisive. " % (
                DELTA_E_HP, need, d_e) + s)


# --- error-checking template (defensive) ------------------------------------
def _write_start_marker(output_dir: Path) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "expected_n_units": EXPECTED_N_UNITS,
              "host": platform.node()}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    fin = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, fin)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    fin = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, fin)


def _selftest() -> None:
    """Exercise the REAL code path (RegNet + surprise + sampling + confounds + run()) at FULL grid, 1 seed."""
    global SEEDS
    _s = SEEDS
    SEEDS = [7]
    try:
        r = run()
        assert r["arms_differ"], "selftest: the 6 arms must produce differing outputs/replay-sets"
        assert r["n_never_replayed"] == N_HELDOUT and r["n_never_replayed"] > 0, \
            "selftest: never-replayed held-out Q must be non-empty"
        struct = next(pt for pt in r["points"] if abs(pt["shared_frac"] - STRUCTURED_FRAC) < 1e-9)
        a = struct["agg"]
        assert a["uniform_replay"]["E_initial"] >= 0.5, \
            "selftest: net did not learn independent targets initially (init=%.3f)" % a["uniform_replay"]["E_initial"]
        # closed-loop and uniform must replay DIFFERENT item distributions (surprise signal is live)
        assert a["surprise_closed_loop"]["total_replay_exposures"] == a["uniform_replay"]["total_replay_exposures"], \
            "selftest: matched budget violated (replay exposures differ)"
        print("[selftest] PASS real-code-path: %s | Q=%d arms_differ=%s"
              % (_fmt_curve(r["points"]), r["n_never_replayed"], r["arms_differ"]), flush=True)
    finally:
        SEEDS = _s


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print("[config] anchor=%s mode=%s N=%d D_T=%d H=%d old=%d E=%d Q=%d B=%d alpha=%.1f blocks=%d "
          "E_OLD=%d E_NEW=%d SF_GRID=%s seeds=%s chance=%.4f expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N, D_T, H, OLD_ITEMS, N_ELIG, N_HELDOUT, B_REPLAY, ALPHA, K_INTERFERE,
             E_OLD, E_NEW, SHARED_FRAC_GRID, SEEDS, CHANCE, EXPECTED_N_UNITS), flush=True)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)

    struct = next(pt for pt in r["points"] if abs(pt["shared_frac"] - STRUCTURED_FRAC) < 1e-9)
    a = struct["agg"]
    unif_e = a["uniform_replay"]["E_retention"]; clos_e = a["surprise_closed_loop"]["E_retention"]
    stat_e = a["surprise_static_snapshot"]["E_retention"]; base_e = a["no_replay"]["E_retention"]
    fn_u_q = a["fresh_net_uniform"]["Q_retention"]; fn_s_q = a["fresh_net_surprise"]["Q_retention"]
    gate_claims = [
        record_gate("struct_delta_E_closed_vs_uniform", clos_e - unif_e, DELTA_E_HP, ">=",
                    "closed-loop surprise replay beats uniform on E-pool retention (LOAD-BEARING lever)"),
        record_gate("struct_hp_seeds", struct["hp_seeds"], (2 if struct["n_seeds"] >= 3 else 1), ">=",
                    "seeds where delta_E >= HP and delta_Q >= floor (structured end)"),
        record_gate("struct_delta_E_static_vs_uniform", stat_e - unif_e, 0.0, ">=",
                    "static-snapshot priority vs uniform (expected ~0: pre-interference surprise uninformative)"),
        record_gate("struct_diff_no_replay", base_e, DIFF_NOREPLAY_MAX, "<=",
                    "catastrophic forgetting of E-pool is real (difficulty ON)"),
        record_gate("struct_diff_uniform_over_floor", unif_e - base_e, DIFF_UNIFORM_MIN_OVER_FLOOR, ">=",
                    "uniform replay budget helps at all (matched-budget sanity)"),
        record_gate("struct_diff_uniform_lower_band", unif_e, DIFF_UNIFORM_BAND[0], ">",
                    "uniform_E above floor band (not saturated-low) META_RULE_AG"),
        record_gate("struct_diff_uniform_upper_band", DIFF_UNIFORM_BAND[1], unif_e, ">",
                    "uniform_E below ceiling band (headroom for a lever) META_RULE_AG"),
        record_gate("struct_diff_initial", a["uniform_replay"]["E_initial"], DIFF_INITIAL_MIN, ">=",
                    "net learned independent targets initially (forgetting not inability)"),
        record_gate("struct_diff_fresh_net_uniform_fails_Q", DIFF_CONFOUND_MAX_Q, fn_u_q, ">=",
                    "fresh-net on uniform-replayed FAILS held-out Q -> content independent (difficulty ON)"),
        record_gate("struct_diff_fresh_net_surprise_fails_Q", DIFF_CONFOUND_MAX_Q, fn_s_q, ">=",
                    "fresh-net on surprise-replayed FAILS held-out Q -> content independent (difficulty ON)"),
        record_gate("cardinality", r["n_units"], EXPECTED_N_UNITS, ">=",
                    "all sweep x seed units completed (META_RULE_H)"),
    ]
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_units": r["n_units"], "expected_n_units": EXPECTED_N_UNITS, "arms_differ": r["arms_differ"],
               "n_eligible": r["n_eligible"], "n_never_replayed": r["n_never_replayed"], "b_replay": r["b_replay"],
               "chance": r["chance"], "points": r["points"], "per_unit": r["per_unit"],
               "config": {"N": N, "D_T": D_T, "H": H, "OLD_CLASSES": OLD_CLASSES, "OLD_EXEMPLARS": OLD_EXEMPLARS,
                          "ELIG_PER_CLASS": ELIG_PER_CLASS, "B_REPLAY": B_REPLAY, "ALPHA": ALPHA,
                          "K_INTERFERE": K_INTERFERE, "NEW_CPB": NEW_CPB, "NEW_EXEMPLARS": NEW_EXEMPLARS,
                          "E_OLD": E_OLD, "E_NEW": E_NEW, "LR": LR, "SHARED_FRAC_GRID": SHARED_FRAC_GRID,
                          "STRUCTURED_FRAC": STRUCTURED_FRAC, "seeds": SEEDS,
                          "bands": {"DELTA_E_HP": DELTA_E_HP, "DELTA_E_HF": DELTA_E_HF, "DELTA_Q_FLOOR": DELTA_Q_FLOOR}},
               "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, r["per_unit"], gate_claims=gate_claims)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
