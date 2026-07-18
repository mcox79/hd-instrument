"""exp_cls_distributed_protection_independent_content_v1.py

CLS CHAIN-GRADE test, DONE RIGHT (revival of exp_cls_distributed_protection_heldout_replay_v1 after the
VET a15e4d91 GENERALIZATION-CONFOUND diagnosis): does interleaved replay of a SMALL SUBSAMPLE of old
memories protect HELD-OUT NEVER-REPLAYED memories that carry INDEPENDENT WITHIN-CLASS CONTENT -- BEATING
the two confound baselines (1-NN proximity + fresh-net-trained-on-subsample) that the VET said killed the
prior attempt?

WHAT THE PRIOR CELL GOT WRONG (VET a15e4d91): its "320 never-replayed memories" were really 16 noisy
re-draws of 20 prototypes, and the held-out metric was CLASS classification. So the held-out items carried
NO INDEPENDENT INFORMATION -- their class was recoverable by GENERALIZATION. A zero-training 1-NN lookup
against the replayed subsample AND a fresh-net-trained-only-on-the-subsample both MATCH the replay arm,
because you only need to know the CLASS (which generalizes), not to have RETAINED the item's own trace.
=> subsample-replay's held-out "protection" was generalization, not distributed consolidation.

THE FIX (this cell) -- the VET's exact revival criterion:
  * Memories SHARE CLASS STRUCTURE (a shared class code in the cue) so distributed consolidation is
    mechanistically POSSIBLE (fully-random memories can't be distributedly protected -- that's not a fair
    failure). CITED@ McClelland-McNaughton-O'Reilly 1995; Kumaran-Hassabis-McClelland 2016.
  * BUT each held-out memory carries INDEPENDENT WITHIN-CLASS CONTENT: a UNIQUE per-item TARGET vector,
    assigned independently within a class, NOT recoverable from its class nor from its nearest replayed
    neighbour. Recovering a held-out item requires having RETAINED ITS OWN TRACE through interference --
    which generalization/proximity CANNOT provide, only genuine distributed consolidation can.
  * LOAD-BEARING metric = RETRIEVAL of the held-out item's OWN independent target (nearest target among
    the full old-target codebook; chance ~ 1/OLD_ITEMS), NOT class classification.

ARMS (ONE variable = how the old pool is used; held-out eval + cue/target construction FIXED across arms):
  * no_replay         : sequential, NO old replay = McCloskey-Cohen forgetting AND the no-replay FLOOR.
  * subsample_replay  : (MECHANISM) interleave replay of ONLY the eligible subsample; the held-out are
                        NEVER replayed. Does distributed consolidation protect their INDEPENDENT targets?
  * replay_all        : interleave replay of ALL old items (incl held-out) = protectable CEILING.
  * one_nn_proximity  : (MUST-BEAT CONFOUND, zero training) held-out target := target of the nearest
                        REPLAYED cue. FAILS iff held-out content is genuinely independent of class-proximity.
  * fresh_net_subsample: (MUST-BEAT CONFOUND) a FRESH net trained ONLY on the replayed subsample (never
                        sees held-out, zero interference). FAILS iff held-out content is not generalizable
                        from the subsample.

DESIGN-GATE (verified at smoke BEFORE full):
  (1) REAL baselines/arms = the 5 above (floor / mechanism / ceiling / 2 confounds).
  (2) LOAD-BEARING metric = held-out INDEPENDENT-target retrieval + margin of subsample OVER max(1-NN,
      fresh-net).
  (3) CAN-FAIL: HARD_FAIL if subsample does NOT beat BOTH confounds on held-out -> generalization again /
      per-item only, distributed protection REFUTED at scale (the honest bounded result; do NOT torture).
  (4) DIFFICULTY-ON: verify BOTH confounds actually FAIL to recover the independent held-out content (if
      they succeed, the content is NOT independent -- design broken). Plus net LEARNED held-out initially,
      no_replay FORGETS, replay_all PROTECTS.
  (5) ONE variable = replay-subsample vs the baselines (cue/target/init fixed).

HARD_PASS (=chain-grade ATTEMPT, VET-pending, NOT self-declared): subsample-replay protects the independent
  held-out content above BOTH the 1-NN and fresh-net baselines by a real margin, >=2/3 seeds -- genuine
  distributed consolidation, not generalization.

DEFLATE: if subsample ties EITHER confound -> "generalization again / per-item only, distributed protection
  refuted." Self-contained numpy; ASCII-only; local-runnable; glass-box.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH/H + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over per-arm predictions)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-metrics both tmp+os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retrieval accuracy over a codebook, chance=1/OLD_ITEMS; feasibility = replay_all ceiling>=0.55
# - baseline_in_band at smoke (META_RULE_AG): no_replay forgets, replay_all protects, BOTH confounds fail
# - discriminator survives scale: forgetting deepens with pool/interference; smoke runs FULL grid, 1 seed
# - HARD_PASS strictly above floor + confounds: subsample held-out >= max(confounds) + margin AND >= abs
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = len(SHARED_FRAC_GRID) * len(SEEDS); verdict counts
# - no PYTHONHASHSEED nondeterminism: all splits/seeds/targets are fixed ints or deterministic index math
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
from __future__ import annotations
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

ANCHOR_NAME = "cls_distributed_protection_independent_content_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- Config -------------------------------------------------------------------------------------------
N = 256                      # cue (hypervector) dimensionality
D_T = 64                     # target vector dimensionality (independent per-item content)
H = 160                      # shared hidden layer -- distributed/overlapping representation
OLD_CLASSES = 12             # old classes learned in the first block
OLD_EXEMPLARS = 12           # exemplars per old class -> 144 old items
ELIG_PER_CLASS = 3           # replay-eligible exemplars/class (25% of old = the subsample)
                             # -> held-out never-replayed = 9/class (75%); n_never_replayed = 108
K_INTERFERE = 8              # NEW-class interference blocks trained sequentially
NEW_CPB = 3                  # new classes per interference block
NEW_EXEMPLARS = 12           # exemplars per new class
E_OLD = 400                  # epochs on the old block (memorize independent targets)
E_NEW = 200                  # epochs per new interference block (overfit new -> real forgetting)
LR = 0.04                    # MEASURED@ smoke tuning: LR>=0.06 diverges (linear MSE readout); 0.04 stable
# Structure axis: SHARED_FRAC = fraction of the cue that is the SHARED CLASS code (rest = item probe).
# HIGH shared_frac = strong shared structure (distributed protection MOST plausible) = the "structured" end
# where the HP gate applies. LOW shared_frac = items more arbitrary/independent (per-item CONTROL end).
SHARED_FRAC_GRID = [0.75, 0.55, 0.35] if not SMOKE else [0.75, 0.35]
STRUCTURED_FRAC = 0.75
SEEDS = [7] if SMOKE else [7, 17, 23]

OLD_ITEMS = OLD_CLASSES * OLD_EXEMPLARS               # 144
HELDOUT_PER_CLASS = OLD_EXEMPLARS - ELIG_PER_CLASS    # 9
N_HELDOUT = OLD_CLASSES * HELDOUT_PER_CLASS           # 108 never-replayed
N_ELIG = OLD_CLASSES * ELIG_PER_CLASS                 # 36 replayed subsample
V_CLASSES = OLD_CLASSES + K_INTERFERE * NEW_CPB       # 12 + 24 = 36 total classes
EXPECTED_N_UNITS = len(SHARED_FRAC_GRID) * len(SEEDS)
CHANCE = 1.0 / OLD_ITEMS                              # THEORETICAL@ retrieval chance over old codebook

# HARD-PASS / HARD-FAIL bands (envelope-fail-bands, pre-registered)
CONFOUND_MARGIN_HP = 0.15    # subsample held-out must beat max(1-NN, fresh-net) by this (structured end)
FLOOR_MARGIN_HP = 0.15       # subsample held-out must also beat the no_replay floor by this
HELDOUT_ABS_HP = 0.40        # subsample held-out absolute floor for a PASS seed (structured end)
# DIFFICULTY-ON gates (per point, on aggregate):
DIFF_INITIAL_MIN = 0.70      # net LEARNED held-out independent targets in the first block (else vacuous)
DIFF_NOREPLAY_MAX = 0.30     # no_replay held-out retrieval collapses (forgetting real)
DIFF_CEILING_MIN = 0.55      # replay_all held-out retrieval high (independent content IS protectable)
DIFF_CONFOUND_MAX = 0.25     # BOTH confounds must FAIL to recover held-out (proves independence)
CANFAIL_EPS = 0.05           # subsample <= max(confound) + this at structured end -> generalization again


def _bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    x = np.sign(rng.standard_normal(shape))
    x[x == 0] = 1.0
    return x.astype(np.float64)


class RegNet:
    """cue(N) -> hidden(H) tanh -> target(D_T) linear. MSE regression, batch backprop.

    The shared hidden layer is the distributed/overlapping representation. Replaying a class sample can
    keep the shared feature basis aligned (McClelland); whether that protects the INDEPENDENT per-item
    target readout of NEVER-REPLAYED items is exactly the open question this cell tests.
    """

    def __init__(self, n: int, h: int, d_t: int, rng: np.random.Generator):
        self.W1 = (rng.standard_normal((h, n)) / np.sqrt(n)).astype(np.float64)
        self.W2 = (rng.standard_normal((d_t, h)) / np.sqrt(h)).astype(np.float64)

    def train(self, X: np.ndarray, T: np.ndarray, epochs: int, lr: float) -> None:
        if X.shape[0] == 0:
            return
        m = X.shape[0]
        for _ in range(epochs):
            A1 = np.tanh(X @ self.W1.T)          # (m,H)
            Y = A1 @ self.W2.T                    # (m,D_T) linear output
            dY = (Y - T) / m                      # MSE grad
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
    """Nearest-target retrieval accuracy over the full old-target codebook. Returns (acc, pred_tau)."""
    if pred.shape[0] == 0:
        return 0.0, np.array([], dtype=np.int64)
    # cosine similarity to every codebook target; argmax = retrieved item index
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-9)
    cn = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-9)
    sims = pn @ cn.T                              # (m, OLD_ITEMS)
    pred_tau = sims.argmax(axis=1)
    return float((pred_tau == tau_true).mean()), pred_tau


def _make_old_bank(rng: np.random.Generator, shared_frac: float
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Old bank: cue = [shared class code | item-specific probe]; target = UNIQUE per-item bipolar vector.

    Returns (X_cue[OLD_ITEMS,N], tau[OLD_ITEMS] item-index, y_class[OLD_ITEMS], codebook[OLD_ITEMS,D_T]).
    Independent within-class content: tau is a unique index per item; the target for item i is codebook[i],
    assigned independently of class -> class tells you NOTHING about which target.
    """
    s = int(round(shared_frac * N))
    proto = _bipolar(rng, (OLD_CLASSES, s))      # shared class code (first s dims)
    X = np.zeros((OLD_ITEMS, N), dtype=np.float64)
    y_class = np.zeros(OLD_ITEMS, dtype=np.int64)
    for c in range(OLD_CLASSES):
        for e in range(OLD_EXEMPLARS):
            i = c * OLD_EXEMPLARS + e
            X[i, :s] = proto[c]                                  # shared class structure
            X[i, s:] = _bipolar(rng, (N - s,))                   # item-specific probe (independent)
            y_class[i] = c
    tau = np.arange(OLD_ITEMS, dtype=np.int64)                   # unique per-item target index
    codebook = _bipolar(rng, (OLD_ITEMS, D_T))                   # independent target content
    return X, tau, y_class, codebook


def _make_new_block(rng: np.random.Generator, shared_frac: float, block_classes: np.ndarray
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Interference block: same cue structure, fresh random targets (drives forgetting via shared W1/W2)."""
    s = int(round(shared_frac * N))
    nc = block_classes.shape[0]
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
    """Deterministic split: first ELIG_PER_CLASS exemplars/class -> eligible (replayed); rest -> held-out."""
    elig, held = [], []
    for c in range(OLD_CLASSES):
        base = c * OLD_EXEMPLARS
        elig.extend(range(base, base + ELIG_PER_CLASS))
        held.extend(range(base + ELIG_PER_CLASS, base + OLD_EXEMPLARS))
    return np.array(elig, dtype=np.int64), np.array(held, dtype=np.int64)


def _train_learned_arm(replay_mode: str, seed: int, old_X, old_tau, codebook,
                       elig_idx, held_idx, new_blocks) -> Dict:
    """replay_mode in {none, subsample, all}. SAME init across the 3 learned arms (one-variable)."""
    net = RegNet(N, H, D_T, np.random.default_rng(seed + 1))
    old_T = codebook[old_tau]
    net.train(old_X, old_T, E_OLD, LR)
    held_init, _ = _retrieval_acc(net.output(old_X[held_idx]), old_tau[held_idx], codebook)

    for b in range(K_INTERFERE):
        Xb, Tb = new_blocks[b]
        if replay_mode == "none":
            trX, trT = Xb, Tb
        elif replay_mode == "subsample":
            trX = np.concatenate([Xb, old_X[elig_idx]]); trT = np.concatenate([Tb, old_T[elig_idx]])
        elif replay_mode == "all":
            trX = np.concatenate([Xb, old_X]); trT = np.concatenate([Tb, old_T])
        else:
            raise ValueError("unknown replay_mode: %s" % replay_mode)
        net.train(trX, trT, E_NEW, LR)

    held_acc, held_tau = _retrieval_acc(net.output(old_X[held_idx]), old_tau[held_idx], codebook)
    elig_acc, _ = _retrieval_acc(net.output(old_X[elig_idx]), old_tau[elig_idx], codebook)
    digest = hashlib.sha256(held_tau.tobytes()).hexdigest()
    return {"heldout": round(held_acc, 3), "heldout_initial": round(held_init, 3),
            "replayed": round(elig_acc, 3), "digest": digest}


def _confound_one_nn(old_X, old_tau, elig_idx, held_idx) -> Dict:
    """Zero-training 1-NN: held-out target := target of nearest REPLAYED cue (cosine). MUST FAIL."""
    Xe = old_X[elig_idx]; Xh = old_X[held_idx]
    en = Xe / (np.linalg.norm(Xe, axis=1, keepdims=True) + 1e-9)
    hn = Xh / (np.linalg.norm(Xh, axis=1, keepdims=True) + 1e-9)
    sims = hn @ en.T                              # (n_held, n_elig)
    nn = sims.argmax(axis=1)
    pred_tau = old_tau[elig_idx][nn]              # nearest replayed cue's item-target index
    acc = float((pred_tau == old_tau[held_idx]).mean())
    return {"heldout": round(acc, 3), "digest": hashlib.sha256(pred_tau.tobytes()).hexdigest()}


def _confound_fresh_net(seed, old_X, old_tau, codebook, elig_idx, held_idx) -> Dict:
    """Fresh net trained ONLY on the replayed subsample (never sees held-out, zero interference). MUST FAIL."""
    net = RegNet(N, H, D_T, np.random.default_rng(seed + 99))
    net.train(old_X[elig_idx], codebook[old_tau[elig_idx]], E_OLD, LR)
    acc, pred_tau = _retrieval_acc(net.output(old_X[held_idx]), old_tau[held_idx], codebook)
    return {"heldout": round(acc, 3), "digest": hashlib.sha256(pred_tau.tobytes()).hexdigest()}


def _run_point(shared_frac: float, seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    old_X, old_tau, _yc, codebook = _make_old_bank(rng, shared_frac)
    new_blocks = []
    for b in range(K_INTERFERE):
        cls = np.arange(OLD_CLASSES + b * NEW_CPB, OLD_CLASSES + (b + 1) * NEW_CPB)
        new_blocks.append(_make_new_block(rng, shared_frac, cls))
    elig_idx, held_idx = _split_idx()

    learned = {m: _train_learned_arm(m, seed, old_X, old_tau, codebook, elig_idx, held_idx, new_blocks)
               for m in ("none", "subsample", "all")}
    one_nn = _confound_one_nn(old_X, old_tau, elig_idx, held_idx)
    fresh = _confound_fresh_net(seed, old_X, old_tau, codebook, elig_idx, held_idx)

    return {"shared_frac": shared_frac, "seed": seed,
            "no_replay": {"heldout": learned["none"]["heldout"], "heldout_initial": learned["none"]["heldout_initial"],
                          "replayed": learned["none"]["replayed"]},
            "subsample_replay": {"heldout": learned["subsample"]["heldout"],
                                 "heldout_initial": learned["subsample"]["heldout_initial"],
                                 "replayed": learned["subsample"]["replayed"]},
            "replay_all": {"heldout": learned["all"]["heldout"], "heldout_initial": learned["all"]["heldout_initial"],
                           "replayed": learned["all"]["replayed"]},
            "one_nn_proximity": {"heldout": one_nn["heldout"]},
            "fresh_net_subsample": {"heldout": fresh["heldout"]},
            "arm_digests": {"no_replay": learned["none"]["digest"], "subsample_replay": learned["subsample"]["digest"],
                            "replay_all": learned["all"]["digest"], "one_nn_proximity": one_nn["digest"],
                            "fresh_net_subsample": fresh["digest"]}}


ARMS5 = ("no_replay", "subsample_replay", "replay_all", "one_nn_proximity", "fresh_net_subsample")


def _difficulty_ok(agg: Dict) -> Tuple[bool, str]:
    base = agg["no_replay"]; ceil = agg["replay_all"]
    nn = agg["one_nn_proximity"]["heldout"]; fn = agg["fresh_net_subsample"]["heldout"]
    checks = [
        (base["heldout_initial"] >= DIFF_INITIAL_MIN, "net_learned_heldout_initial"),
        (base["heldout"] <= DIFF_NOREPLAY_MAX, "no_replay_forgets_heldout"),
        (ceil["heldout"] >= DIFF_CEILING_MIN, "replay_all_protects_ceiling"),
        (nn <= DIFF_CONFOUND_MAX, "one_nn_fails_proves_independence"),
        (fn <= DIFF_CONFOUND_MAX, "fresh_net_fails_proves_independence"),
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
        for arm in ARMS5:
            keys = ("heldout", "heldout_initial", "replayed") if arm in (
                "no_replay", "subsample_replay", "replay_all") else ("heldout",)
            agg[arm] = {k: round(_mean(arm, k), 3) for k in keys}

        hp = 0
        for u in units:
            sub = u["subsample_replay"]["heldout"]; base = u["no_replay"]["heldout"]
            cmax = max(u["one_nn_proximity"]["heldout"], u["fresh_net_subsample"]["heldout"])
            if (sub >= cmax + CONFOUND_MARGIN_HP and sub >= base + FLOOR_MARGIN_HP and sub >= HELDOUT_ABS_HP):
                hp += 1
        diff_ok, diff_msg = _difficulty_ok(agg)
        for u in units:
            d = u["arm_digests"]
            vals = list(d.values())
            if len(set(vals)) != len(vals):
                arms_differ = False
        points.append({"shared_frac": sf, "agg": agg, "hp_seeds": hp, "n_seeds": len(units),
                       "difficulty_ok": diff_ok, "difficulty_msg": diff_msg})

    return {"points": points, "per_unit": per_unit, "n_units": len(per_unit),
            "expected_n_units": EXPECTED_N_UNITS, "arms_differ": arms_differ,
            "n_never_replayed": N_HELDOUT, "n_replayed_subsample": N_ELIG, "chance": round(CHANCE, 5)}


def _fmt_curve(points: List[Dict]) -> str:
    segs = []
    for pt in points:
        a = pt["agg"]
        segs.append("SF=%.2f[no=%.3f sub=%.3f all=%.3f 1nn=%.3f fresh=%.3f hp=%d/%d diff=%s]"
                    % (pt["shared_frac"], a["no_replay"]["heldout"], a["subsample_replay"]["heldout"],
                       a["replay_all"]["heldout"], a["one_nn_proximity"]["heldout"],
                       a["fresh_net_subsample"]["heldout"], pt["hp_seeds"], pt["n_seeds"],
                       "Y" if pt["difficulty_ok"] else "N"))
    return " ".join(segs)


def verdict(r: Dict) -> Tuple[str, str]:
    points = r["points"]
    curve = _fmt_curve(points)
    struct = next(pt for pt in points if abs(pt["shared_frac"] - STRUCTURED_FRAC) < 1e-9)
    ns = struct["n_seeds"]; need = 2 if ns >= 3 else 1
    sa = struct["agg"]
    sub_h = sa["subsample_replay"]["heldout"]; base_h = sa["no_replay"]["heldout"]
    nn_h = sa["one_nn_proximity"]["heldout"]; fn_h = sa["fresh_net_subsample"]["heldout"]
    cmax = max(nn_h, fn_h)
    s = ("HELD-OUT independent-content retrieval (chance=%.4f) curve "
         "[no_replay/subsample/replay_all/1-NN/fresh-net]: %s | n_never_replayed=%d n_replayed=%d "
         "arms_differ=%s units=%d/%d"
         % (r["chance"], curve, r["n_never_replayed"], r["n_replayed_subsample"], r["arms_differ"],
            r["n_units"], r["expected_n_units"]))

    if r["n_units"] != r["expected_n_units"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d. %s" % (r["n_units"], r["expected_n_units"], s))
    if not r["arms_differ"]:
        return ("HARD_FAIL", "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: " + s)
    if not struct["difficulty_ok"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND_REGIME_INCONCLUSIVE: structured-end difficulty gate off (%s) -- "
                "cannot distinguish distributed consolidation from generalization until baselines in band "
                "AND both confounds proven to FAIL. " % struct["difficulty_msg"] + s)

    # CAN-FAIL (honest bounded result): subsample ties EITHER confound at the structured end.
    if sub_h <= cmax + CANFAIL_EPS:
        return ("HARD_FAIL",
                "HARD_FAIL_GENERALIZATION_NOT_CONSOLIDATION: at the structured end (SHARED_FRAC=%.2f) "
                "subsample-replay held-out retrieval (%.3f) does NOT beat the max confound baseline "
                "(1-NN=%.3f, fresh-net=%.3f) on the INDEPENDENT held-out content -- replay protects only "
                "the explicitly rehearsed items / whatever generalizes; the never-replayed independent "
                "traces are NOT distributedly consolidated. Distributed protection REFUTED at scale "
                "(per-item only; does NOT scale to textbook-after-textbook). " % (STRUCTURED_FRAC, sub_h, nn_h, fn_h) + s)
    if struct["hp_seeds"] >= need:
        return ("HARD_PASS",
                "HARD_PASS_DISTRIBUTED_CONSOLIDATION: at the structured end (SHARED_FRAC=%.2f) replaying a "
                "%d-item subsample (%d%% of old) protects the INDEPENDENT content of the %d NEVER-REPLAYED "
                "held-out memories (retrieval=%.3f) above BOTH confounds (1-NN=%.3f, fresh-net=%.3f; "
                "margin>=%.2f) AND the no_replay floor (%.3f; margin>=%.2f), abs>=%.2f, %d/%d seeds -- "
                "genuine distributed consolidation, NOT generalization. CLAIM-VET-pending, NOT self-declared "
                "chain-grade. " % (STRUCTURED_FRAC, r["n_replayed_subsample"], int(round(100 * N_ELIG / OLD_ITEMS)),
                                   r["n_never_replayed"], sub_h, nn_h, fn_h, CONFOUND_MARGIN_HP, base_h,
                                   FLOOR_MARGIN_HP, HELDOUT_ABS_HP, struct["hp_seeds"], ns) + s)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL: subsample beats the confounds/floor at the structured end but below the "
            ">=%.2f-margin / >=%.2f-abs bar on >=%d seeds -- partial distributed consolidation. "
            % (CONFOUND_MARGIN_HP, HELDOUT_ABS_HP, need) + s)


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
    """Exercise the REAL code path (RegNet + confounds + run()) at FULL grid, 1 seed.

    Forgetting deepens with pool/interference (not seeds), so difficulty is checked at the regime the FULL
    run uses (per DISCRIMINATOR-MUST-SURVIVE-SCALE); only the seed count is reduced.
    """
    global SEEDS
    _s = SEEDS
    SEEDS = [7]
    try:
        r = run()
        assert r["arms_differ"], "selftest: the 5 arms must produce differing held-out predictions"
        assert r["n_never_replayed"] == N_HELDOUT and r["n_never_replayed"] > 0, \
            "selftest: held-out never-replayed set must be non-empty (VET critique fix)"
        struct = next(pt for pt in r["points"] if abs(pt["shared_frac"] - STRUCTURED_FRAC) < 1e-9)
        a = struct["agg"]
        assert a["no_replay"]["heldout_initial"] >= 0.5, \
            "selftest: net did not learn independent held-out targets initially (init=%.3f)" % a["no_replay"]["heldout_initial"]
        print("[selftest] PASS real-code-path: curve %s | n_never_replayed=%d arms_differ=%s"
              % (_fmt_curve(r["points"]), r["n_never_replayed"], r["arms_differ"]), flush=True)
    finally:
        SEEDS = _s


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print("[config] anchor=%s mode=%s N=%d D_T=%d H=%d old_items=%d elig=%d heldout=%d blocks=%d "
          "E_OLD=%d E_NEW=%d SHARED_FRAC_GRID=%s seeds=%s chance=%.4f expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N, D_T, H, OLD_ITEMS, N_ELIG, N_HELDOUT, K_INTERFERE, E_OLD, E_NEW,
             SHARED_FRAC_GRID, SEEDS, CHANCE, EXPECTED_N_UNITS), flush=True)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)

    struct = next(pt for pt in r["points"] if abs(pt["shared_frac"] - STRUCTURED_FRAC) < 1e-9)
    sa = struct["agg"]
    sub = sa["subsample_replay"]; base = sa["no_replay"]; ceil = sa["replay_all"]
    nn = sa["one_nn_proximity"]["heldout"]; fn = sa["fresh_net_subsample"]["heldout"]
    cmax = max(nn, fn)
    gate_claims = [
        record_gate("struct_subsample_heldout", sub["heldout"], HELDOUT_ABS_HP, ">=",
                    "distributed consolidation of independent held-out content (LOAD-BEARING)"),
        record_gate("struct_subsample_over_confounds", sub["heldout"] - cmax, CONFOUND_MARGIN_HP, ">=",
                    "subsample beats max(1-NN, fresh-net) -- consolidation not generalization (LOAD-BEARING)"),
        record_gate("struct_subsample_over_floor", sub["heldout"] - base["heldout"], FLOOR_MARGIN_HP, ">=",
                    "subsample beats the no_replay floor (structured end)"),
        record_gate("struct_diff_no_replay", base["heldout"], DIFF_NOREPLAY_MAX, "<=",
                    "catastrophic forgetting of held-out content is real (difficulty ON)"),
        record_gate("struct_diff_ceiling", ceil["heldout"], DIFF_CEILING_MIN, ">=",
                    "independent content IS protectable if rehearsed (ceiling)"),
        record_gate("struct_diff_initial", base["heldout_initial"], DIFF_INITIAL_MIN, ">=",
                    "net learned independent held-out targets initially (forgetting not inability)"),
        record_gate("struct_diff_one_nn_fails", DIFF_CONFOUND_MAX, nn, ">=",
                    "1-NN proximity FAILS on held-out -> content is independent (difficulty ON)"),
        record_gate("struct_diff_fresh_net_fails", DIFF_CONFOUND_MAX, fn, ">=",
                    "fresh-net-on-subsample FAILS on held-out -> content is independent (difficulty ON)"),
        record_gate("struct_hp_seeds", struct["hp_seeds"], (2 if struct["n_seeds"] >= 3 else 1), ">=",
                    "seeds where subsample beats both confounds+floor above bar (structured end)"),
        record_gate("cardinality", r["n_units"], EXPECTED_N_UNITS, ">=",
                    "all sweep x seed units completed (META_RULE_H)"),
    ]
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_units": r["n_units"], "expected_n_units": EXPECTED_N_UNITS, "arms_differ": r["arms_differ"],
               "n_never_replayed": r["n_never_replayed"], "n_replayed_subsample": r["n_replayed_subsample"],
               "chance": r["chance"], "points": r["points"], "per_unit": r["per_unit"],
               "config": {"N": N, "D_T": D_T, "H": H, "OLD_CLASSES": OLD_CLASSES, "OLD_EXEMPLARS": OLD_EXEMPLARS,
                          "ELIG_PER_CLASS": ELIG_PER_CLASS, "K_INTERFERE": K_INTERFERE, "NEW_CPB": NEW_CPB,
                          "NEW_EXEMPLARS": NEW_EXEMPLARS, "E_OLD": E_OLD, "E_NEW": E_NEW, "LR": LR,
                          "SHARED_FRAC_GRID": SHARED_FRAC_GRID, "STRUCTURED_FRAC": STRUCTURED_FRAC, "seeds": SEEDS},
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
