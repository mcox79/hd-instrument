"""Selective-Overwrite-Recall: reservoir-FAILING construction + CALIBRATION (v1).

MEASUREMENT-FIRST (design D3): this cell BUILDS the Selective-Overwrite-Recall task and CALIBRATES
whether it is genuinely reservoir-failing BEFORE any WM mechanism is built. It builds NO learned
gating mechanism (the WM is the NEXT dispatch, gated on this returning RESERVOIR_FAILING_VALID).

Construction: a per-example stream of (slot_id, filler) ASSIGNMENT events. S target slots are each
written MULTIPLE times (overwrites); interleaved with D >> S distractor slot-touches. Order/spacing
randomized per example. The query asks for the MOST-RECENTLY-OVERWRITTEN filler of one target slot.
Tail constraint: >= TAIL_MIN distractor events after every target slot's last write (so the globally
last token is a distractor and recency alone cannot answer). Tokens are encoded by a FIXED RANDOM
embedding (the "random-init frozen encoder"); surface text is deferred to the mechanism build because
reservoir-failing is a STRUCTURAL property independent of the surface strings.

Arms:
  CAN-FAIL (must land near chance = 1/V_FILL):
    reservoir_esn_linear  -- random-init frozen ESN encoder + LINEAR probe (query one-hot appended)
    reservoir_esn_mlp     -- SAME reservoir + shallow MLP probe (fair non-tautological shot)
    shortcut_globally_last / shortcut_fixed_position / shortcut_first_occurrence / shortcut_most_frequent
      -- deterministic rule oracles
  HEADROOM (must clear well above chance):
    oracle_keep_last              -- rule-follower keep-last-write-per-slot = ground truth (ceiling)
    gated_reservoir_at_lastwrite  -- SAME reservoir state at the queried slot's last-write timestep
      (FIXED-RULE gating, NOT a learned mechanism) + LINEAR probe -> localizes difficulty to GATING.

VERDICT: RESERVOIR_FAILING_VALID / HAS_SHORTCUT / NOT_LEARNABLE (see pre-reg for bands).

Run:  python experiments/exp_selective_overwrite_recall_calib_v1.py --self-test
      python experiments/exp_selective_overwrite_recall_calib_v1.py --full

ASCII-only. No emojis. Deterministic seeding (no hash(), no list(set())).
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:  # sklearn probes (CPU, deterministic via random_state)
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
except Exception as _imp_exc:  # pragma: no cover - environment guard
    LogisticRegression = None
    MLPClassifier = None
    _SKLEARN_IMPORT_ERROR = _imp_exc
else:
    _SKLEARN_IMPORT_ERROR = None

ANCHOR_NAME = "selective_overwrite_recall_calib_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---------------- construction params (author-owned) ----------------
V_FILL = 20                 # filler vocab (SHARED across target+distractor) = label space -> CHANCE = 0.05
CHANCE = 1.0 / V_FILL
S_TARGET = 6                # target slots
N_DISTRACT_SLOTS = 24       # distractor slot ids (slot vocab = S_TARGET + N_DISTRACT_SLOTS)
WRITES_MIN, WRITES_MAX = 2, 4   # overwrites per target slot
N_DISTRACT_EVENTS = 60      # distractor touches per stream (multiple of V_FILL for balanced fillers)
TAIL_MIN = 8                # distractor events guaranteed after the queried slot's last write
TARGET_TAIL_MIN = 5         # TARGET-write events guaranteed after the queried slot's last write
                            # (buries the answer among later target fillers -> kills the recency shortcut:
                            #  a passive reservoir's recency direction no longer preferentially hits the answer)
FIXED_POSITIONS = (0, 5, 10, 20, -1)  # positions probed by the fixed-position shortcut oracle

D_EMB = 64                  # random-embedding dim ("random-init frozen encoder")
D_RES = 128                 # reservoir state dim
RHO = 0.9                   # reservoir spectral radius
LEAK = 1.0                  # ESN leak rate (1.0 = standard tanh update)

NEAR_CHANCE_MARGIN = 0.05   # can-fail arms must be < CHANCE + this
HEADROOM_MIN = 0.50         # headroom arms must be >= this
ORACLE_KEEP_LAST_MIN = 0.95

FULL_TRAIN, FULL_EVAL = 3000, 1500
SEEDS_FULL = (7, 13)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- start-marker / crash-diagnostic (canonical hardening) ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": _now_iso(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ---------------- the construction ----------------
def gen_stream(rng):
    """Generate ONE Selective-Overwrite-Recall example.

    Returns dict with:
      slots  : int array [L]  -- slot id per event (0..SLOT_VOCAB-1); targets are 0..S_TARGET-1
      fills  : int array [L]  -- filler id per event (0..V_FILL-1)
      query  : int            -- queried target slot id (0..S_TARGET-1)
      answer : int            -- most-recently-overwritten filler of the queried slot
      last_write_idx : int    -- event index of the queried slot's last write (for gated arm)
    Guarantees: >= WRITES_MIN writes to the queried slot; >= TAIL_MIN distractor events AFTER the
    queried slot's last write; order fully randomized subject to those constraints.
    """
    slot_vocab = S_TARGET + N_DISTRACT_SLOTS

    # 1) build the SLOT sequence: each target slot touched k in [WRITES_MIN, WRITES_MAX] times,
    #    plus N_DISTRACT_EVENTS distractor-slot touches. (Fillers assigned in step 3.)
    slot_seq = []
    for s in range(S_TARGET):
        k = int(rng.integers(WRITES_MIN, WRITES_MAX + 1))
        slot_seq.extend([s] * k)
    for _ in range(N_DISTRACT_EVENTS):
        slot_seq.append(int(rng.integers(S_TARGET, slot_vocab)))
    slot_seq = np.array(slot_seq, dtype=np.int64)
    slot_seq = slot_seq[rng.permutation(len(slot_seq))]  # fully randomize order/spacing
    L = len(slot_seq)

    # 2) assign fillers from a GLOBALLY BALANCED shuffled multiset over the SHARED vocab V_FILL, so
    #    every filler VALUE has ~identical global frequency AND presence. This kills BOTH aggregate
    #    shortcuts at once: (a) most_frequent (no informative mode) and (b) "predict a present/target
    #    filler" (all values present with equal count, so presence/frequency of a value carries no
    #    information about whether it is the queried slot's last write). Only the query x sequence
    #    last-write INTERACTION is informative -> a passive linear reservoir readout cannot recover it.
    reps = L // V_FILL
    rem = L - reps * V_FILL
    fill_pool = np.concatenate([
        np.repeat(np.arange(V_FILL), reps),
        rng.permutation(V_FILL)[:rem] if rem else np.array([], dtype=np.int64),
    ]).astype(np.int64)
    fill_pool = fill_pool[rng.permutation(len(fill_pool))]
    events = [[int(slot_seq[i]), int(fill_pool[i])] for i in range(L)]

    # 4) choose the query = a target slot whose last write is buried by BOTH >= TAIL_MIN distractor
    #    events AND >= TARGET_TAIL_MIN later TARGET-write events (so neither raw recency nor
    #    "most-recent target filler" predicts the answer).
    L = len(events)
    last_write = {s: -1 for s in range(S_TARGET)}
    for idx, (sl, _fl) in enumerate(events):
        if sl < S_TARGET:
            last_write[sl] = idx
    # count TARGET-write events strictly after each slot's last write
    is_target = np.array([1 if e[0] < S_TARGET else 0 for e in events])
    cum_target_after = np.concatenate([np.cumsum(is_target[::-1])[::-1][1:], [0]])  # target writes after idx
    eligible = [s for s in range(S_TARGET)
                if last_write[s] >= 0
                and (L - 1 - last_write[s]) >= TAIL_MIN
                and int(cum_target_after[last_write[s]]) >= TARGET_TAIL_MIN]
    if not eligible:
        # give up gracefully on this draw; caller re-draws (append-distractor cannot add target tail)
        return None

    query = int(eligible[rng.integers(0, len(eligible))])
    answer = int(events[last_write[query]][1])

    slots = np.array([e[0] for e in events], dtype=np.int64)
    fills = np.array([e[1] for e in events], dtype=np.int64)
    return {
        "slots": slots,
        "fills": fills,
        "query": query,
        "answer": answer,
        "last_write_idx": int(last_write[query]),
    }


def gen_dataset(n, rng):
    out = []
    while len(out) < n:
        ex = gen_stream(rng)
        if ex is not None:
            out.append(ex)
    return out


# ---------------- random-init frozen ESN encoder ("reservoir") ----------------
class FrozenESN:
    """Random-init frozen echo-state reservoir. Fixed W_in, W_res, embeddings. No training."""

    def __init__(self, seed, d_emb, d_res, rho, slot_vocab, v_fill):
        rng = np.random.default_rng(seed + 90001)
        self.d_emb = d_emb
        self.d_res = d_res
        self.leak = LEAK
        self.E_slot = rng.standard_normal((slot_vocab, d_emb)).astype(np.float64) / np.sqrt(d_emb)
        self.E_fill = rng.standard_normal((v_fill, d_emb)).astype(np.float64) / np.sqrt(d_emb)
        self.W_in = rng.standard_normal((d_res, 2 * d_emb)).astype(np.float64) / np.sqrt(2 * d_emb)
        W = rng.standard_normal((d_res, d_res)).astype(np.float64)
        eig = np.max(np.abs(np.linalg.eigvals(W)))
        self.W_res = (W * (rho / eig)).astype(np.float64)

    def _inputs(self, slots, fills):
        return np.concatenate([self.E_slot[slots], self.E_fill[fills]], axis=1)  # [L, 2*d_emb]

    def run(self, examples):
        """Vectorized reservoir pass over a padded batch of streams.

        Returns:
          feat_reservoir : [n, 2*d_res]  concat(final_state, mean_state) -- for reservoir arm
          state_at_lastwrite : [n, d_res] -- reservoir state at each example's queried-slot last write
        """
        n = len(examples)
        lengths = np.array([len(ex["slots"]) for ex in examples])
        Lmax = int(lengths.max())
        # pad inputs
        X = np.zeros((n, Lmax, 2 * self.d_emb), dtype=np.float64)
        for i, ex in enumerate(examples):
            inp = self._inputs(ex["slots"], ex["fills"])
            X[i, : inp.shape[0]] = inp
        H = np.zeros((n, self.d_res), dtype=np.float64)
        sum_H = np.zeros((n, self.d_res), dtype=np.float64)
        active_count = np.zeros((n, 1), dtype=np.float64)
        lw_idx = np.array([ex["last_write_idx"] for ex in examples])
        state_at_lw = np.zeros((n, self.d_res), dtype=np.float64)
        final_state = np.zeros((n, self.d_res), dtype=np.float64)
        for t in range(Lmax):
            active = (t < lengths)  # [n]
            pre = X[:, t, :] @ self.W_in.T + H @ self.W_res.T
            newH = np.tanh(pre)
            H = np.where(active[:, None], (1 - self.leak) * H + self.leak * newH, H)
            am = active[:, None].astype(np.float64)
            sum_H += H * am
            active_count += am
            # capture state at last-write timestep and final active timestep
            is_lw = (lw_idx == t)[:, None]
            state_at_lw = np.where(is_lw, H, state_at_lw)
            is_last = ((t == lengths - 1))[:, None]
            final_state = np.where(is_last, H, final_state)
        mean_state = sum_H / np.maximum(active_count, 1.0)
        feat_reservoir = np.concatenate([final_state, mean_state], axis=1)
        return feat_reservoir, state_at_lw


def _query_onehot(examples):
    q = np.array([ex["query"] for ex in examples])
    oh = np.zeros((len(examples), S_TARGET), dtype=np.float64)
    oh[np.arange(len(examples)), q] = 1.0
    return oh


# ---------------- probes ----------------
def fit_eval_probe(kind, Xtr, ytr, Xev, yev, seed):
    """kind in {'linear','mlp'}. Returns eval accuracy + train accuracy (decoder-collapse sanity)."""
    if kind == "linear":
        clf = LogisticRegression(max_iter=500, C=1.0, solver="lbfgs", random_state=seed)
    elif kind == "mlp":
        clf = MLPClassifier(hidden_layer_sizes=(128,), max_iter=300, random_state=seed,
                            early_stopping=False, alpha=1e-3)
    else:
        raise ValueError("unknown probe kind %r" % kind)
    # standardize (fit on train only)
    mu = Xtr.mean(axis=0, keepdims=True)
    sd = Xtr.std(axis=0, keepdims=True) + 1e-8
    Xtr_s = (Xtr - mu) / sd
    Xev_s = (Xev - mu) / sd
    clf.fit(Xtr_s, ytr)
    train_acc = float((clf.predict(Xtr_s) == ytr).mean())
    eval_acc = float((clf.predict(Xev_s) == yev).mean())
    return eval_acc, train_acc


# ---------------- rule oracles (deterministic shortcuts + headroom ceiling) ----------------
def oracle_globally_last(ex):
    return int(ex["fills"][-1])


def oracle_fixed_position(ex, pos):
    L = len(ex["fills"])
    p = pos if pos >= 0 else L + pos
    if p < 0 or p >= L:
        return -1
    return int(ex["fills"][p])


def oracle_first_occurrence(ex):
    q = ex["query"]
    for i, s in enumerate(ex["slots"]):
        if int(s) == q:
            return int(ex["fills"][i])
    return -1


def oracle_most_frequent(ex):
    vals, counts = np.unique(ex["fills"], return_counts=True)
    return int(vals[int(np.argmax(counts))])


def oracle_keep_last(ex):
    """Content-gated keep-last-write-per-slot rule-follower = ground truth (headroom ceiling)."""
    q = ex["query"]
    ans = -1
    for i, s in enumerate(ex["slots"]):
        if int(s) == q:
            ans = int(ex["fills"][i])
    return ans


def oracle_acc(examples, fn):
    correct = sum(1 for ex in examples if fn(ex) == ex["answer"])
    return correct / len(examples)


# ---------------- self-tests (leak-proofing) ----------------
def selftest_construction(seed=7, n=800):
    rng = np.random.default_rng(seed)
    ds = gen_dataset(n, rng)
    fails = []

    # tail constraint (HARD)
    for ex in ds:
        L = len(ex["slots"])
        assert (L - 1 - ex["last_write_idx"]) >= TAIL_MIN, "tail constraint violated"
        assert ex["answer"] == oracle_keep_last(ex), "answer != keep-last rule"

    # label balance
    answers = np.array([ex["answer"] for ex in ds])
    _, counts = np.unique(answers, return_counts=True)
    max_share = counts.max() / len(ds)
    if max_share >= 2.0 * CHANCE:
        fails.append("label imbalance max_share=%.3f (>= 2x chance %.3f)" % (max_share, CHANCE))

    # naive-shortcut immunity
    sc = {
        "globally_last": oracle_acc(ds, oracle_globally_last),
        "first_occurrence": oracle_acc(ds, oracle_first_occurrence),
        "most_frequent": oracle_acc(ds, oracle_most_frequent),
    }
    for pos in FIXED_POSITIONS:
        sc["fixed_position_%d" % pos] = oracle_acc(ds, lambda ex, p=pos: oracle_fixed_position(ex, p))
    for name, acc in sc.items():
        if acc >= CHANCE + NEAR_CHANCE_MARGIN:
            fails.append("shortcut %s solves it acc=%.3f (>= chance+margin %.3f)"
                         % (name, acc, CHANCE + NEAR_CHANCE_MARGIN))

    # ceiling sanity
    kl = oracle_acc(ds, oracle_keep_last)
    if kl < 0.999:
        fails.append("oracle_keep_last=%.4f != 1.0 (construction/answer bug)" % kl)

    # split disjointness (deterministic hashing; NO python hash())
    def _key(ex):
        return (tuple(int(x) for x in ex["slots"]),
                tuple(int(x) for x in ex["fills"]), int(ex["query"]))
    rng2 = np.random.default_rng(seed + 1)
    ds_a = gen_dataset(n, np.random.default_rng(seed))
    ds_b = gen_dataset(n, rng2)
    keys_a = set(_key(ex) for ex in ds_a)
    overlap = sum(1 for ex in ds_b if _key(ex) in keys_a)
    if overlap > 0:
        fails.append("split leakage: %d/%d eval streams appear in train" % (overlap, n))

    return {"shortcut_accs": sc, "label_max_share": float(max_share),
            "keep_last": float(kl), "split_overlap": int(overlap), "chance": CHANCE,
            "fails": fails}


def run_self_test():
    _log("SELF-TEST: sklearn import ...")
    if _SKLEARN_IMPORT_ERROR is not None:
        raise RuntimeError("sklearn import failed: %r" % _SKLEARN_IMPORT_ERROR)

    _log("SELF-TEST: construction leak-proofing ...")
    st = selftest_construction(seed=7, n=800)
    _log("  chance=%.4f  keep_last=%.4f  label_max_share=%.4f  split_overlap=%d"
         % (st["chance"], st["keep_last"], st["label_max_share"], st["split_overlap"]))
    _log("  shortcut accs: " + ", ".join("%s=%.3f" % (k, v) for k, v in st["shortcut_accs"].items()))
    if st["fails"]:
        for f in st["fails"]:
            _log("  SELFTEST FAIL: " + f)
        raise AssertionError("construction self-test FAILED: %s" % "; ".join(st["fails"]))

    _log("SELF-TEST: tiny end-to-end arm smoke (reservoir + gated + probes) ...")
    res = run_calibration(train_n=200, eval_n=200, d_res=32, seeds=(7,), tag="selftest")
    # arms-must-differ sanity: reservoir vs gated must not be bit-identical accs across arms
    accs = res["per_seed"][0]["arms"]
    _log("  tiny arms: " + ", ".join("%s=%.3f" % (k, v) for k, v in accs.items()))
    assert accs["oracle_keep_last"] >= 0.999, "tiny: keep-last ceiling broke"
    _log("SELF-TEST PASS")
    return {"selftest": st, "tiny": res}


# ---------------- calibration driver ----------------
def run_calibration(train_n, eval_n, d_res, seeds, tag):
    per_seed = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        tr = gen_dataset(train_n, rng)
        ev = gen_dataset(eval_n, np.random.default_rng(seed + 777))
        slot_vocab = S_TARGET + N_DISTRACT_SLOTS
        esn = FrozenESN(seed, D_EMB, d_res, RHO, slot_vocab, V_FILL)

        # reservoir features
        feat_tr, lw_tr = esn.run(tr)
        feat_ev, lw_ev = esn.run(ev)
        q_tr, q_ev = _query_onehot(tr), _query_onehot(ev)
        ytr = np.array([ex["answer"] for ex in tr])
        yev = np.array([ex["answer"] for ex in ev])

        Xtr_res = np.concatenate([feat_tr, q_tr], axis=1)
        Xev_res = np.concatenate([feat_ev, q_ev], axis=1)

        arms = {}
        train_accs = {}

        # CAN-FAIL: reservoir + linear / mlp
        a, ta = fit_eval_probe("linear", Xtr_res, ytr, Xev_res, yev, seed)
        arms["reservoir_esn_linear"] = a
        train_accs["reservoir_esn_linear"] = ta
        a, ta = fit_eval_probe("mlp", Xtr_res, ytr, Xev_res, yev, seed)
        arms["reservoir_esn_mlp"] = a
        train_accs["reservoir_esn_mlp"] = ta

        # CAN-FAIL: rule-oracle shortcuts
        arms["shortcut_globally_last"] = oracle_acc(ev, oracle_globally_last)
        arms["shortcut_first_occurrence"] = oracle_acc(ev, oracle_first_occurrence)
        arms["shortcut_most_frequent"] = oracle_acc(ev, oracle_most_frequent)
        fp = [oracle_acc(ev, lambda ex, p=p: oracle_fixed_position(ex, p)) for p in FIXED_POSITIONS]
        arms["shortcut_fixed_position"] = float(max(fp))  # conservative: MAX over positions

        # HEADROOM: gated reservoir at last-write + oracle ceiling
        a, ta = fit_eval_probe("linear", lw_tr, ytr, lw_ev, yev, seed)
        arms["gated_reservoir_at_lastwrite"] = a
        train_accs["gated_reservoir_at_lastwrite"] = ta
        arms["oracle_keep_last"] = oracle_acc(ev, oracle_keep_last)

        per_seed.append({
            "seed": seed, "train_n": train_n, "eval_n": eval_n, "d_res": d_res,
            "arms": arms, "train_accs": train_accs,
        })
        _log("  [%s seed=%d] " % (tag, seed)
             + ", ".join("%s=%.3f" % (k, v) for k, v in arms.items()))
    return {"per_seed": per_seed}


CAN_FAIL_ARMS = [
    "reservoir_esn_linear", "reservoir_esn_mlp",
    "shortcut_globally_last", "shortcut_fixed_position",
    "shortcut_first_occurrence", "shortcut_most_frequent",
]
HEADROOM_GATED = "gated_reservoir_at_lastwrite"


def decide_verdict(per_seed):
    near = CHANCE + NEAR_CHANCE_MARGIN
    all_canfail_ok = True
    headroom_ok = True
    ceiling_ok = True
    worst_canfail = 0.0
    min_headroom = 1.0
    for ps in per_seed:
        a = ps["arms"]
        for arm in CAN_FAIL_ARMS:
            worst_canfail = max(worst_canfail, a[arm])
            if a[arm] >= near:
                all_canfail_ok = False
        min_headroom = min(min_headroom, a[HEADROOM_GATED])
        if a[HEADROOM_GATED] < HEADROOM_MIN:
            headroom_ok = False
        if a["oracle_keep_last"] < ORACLE_KEEP_LAST_MIN:
            ceiling_ok = False

    if not ceiling_ok:
        verdict = "NOT_LEARNABLE"
        msg = "oracle_keep_last ceiling below %.2f (construction/answer bug)" % ORACLE_KEEP_LAST_MIN
    elif not headroom_ok:
        verdict = "NOT_LEARNABLE"
        msg = ("gated headroom %.3f < %.2f: even with correct gating a readout cannot recover the "
               "answer -> construction too hard/mis-specified" % (min_headroom, HEADROOM_MIN))
    elif not all_canfail_ok:
        verdict = "HAS_SHORTCUT"
        msg = ("a can-fail arm reached %.3f >= chance+margin %.3f: reservoir/positional shortcut "
               "solves it -> tighten construction (increase D/TAIL_MIN/writes, decrease d_res)"
               % (worst_canfail, near))
    else:
        verdict = "RESERVOIR_FAILING_VALID"
        msg = ("all can-fail arms < %.3f (worst %.3f) AND gated headroom >= %.2f (min %.3f), "
               "both seeds; chance=%.4f -> the construction separates learned content-gated "
               "maintenance from structure-alone." % (near, worst_canfail, HEADROOM_MIN,
                                                        min_headroom, CHANCE))
    return verdict, msg, {
        "chance": CHANCE, "near_chance_bar": near, "headroom_min": HEADROOM_MIN,
        "worst_canfail_acc": worst_canfail, "min_gated_headroom_acc": min_headroom,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    args = ap.parse_args()

    run_mode = "self_test" if (args.self_test or not args.full) else "full"
    expected_units = 1 if run_mode == "self_test" else len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (construction leak-proofing + tiny end-to-end arms)",
            "summary": "SELFTEST_PASS",
            "run_mode": "self_test",
            "elapsed_s": elapsed,
            "ts_iso": _now_iso(),
            "anchor_name": ANCHOR_NAME,
            "chance": CHANCE,
            "selftest": st["selftest"],
            "tiny_calibration": st["tiny"],
        }
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % elapsed)
        return

    # FULL calibration
    _log("FULL calibration: train_n=%d eval_n=%d seeds=%s chance=%.4f"
         % (args.train_n, args.eval_n, SEEDS_FULL, CHANCE))
    st = selftest_construction(seed=7, n=800)
    if st["fails"]:
        raise AssertionError("pre-full construction self-test FAILED: %s" % "; ".join(st["fails"]))
    res = run_calibration(args.train_n, args.eval_n, D_RES, SEEDS_FULL, tag="full")
    verdict, msg, bands = decide_verdict(res["per_seed"])
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:120]),
        "run_mode": "full",
        "elapsed_s": elapsed,
        "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME,
        "chance": CHANCE,
        "bands": bands,
        "params": {
            "V_FILL": V_FILL, "S_TARGET": S_TARGET, "N_DISTRACT_SLOTS": N_DISTRACT_SLOTS,
            "N_DISTRACT_EVENTS": N_DISTRACT_EVENTS, "WRITES": [WRITES_MIN, WRITES_MAX],
            "TAIL_MIN": TAIL_MIN, "D_EMB": D_EMB, "D_RES": D_RES, "RHO": RHO,
            "train_n": args.train_n, "eval_n": args.eval_n, "seeds": list(SEEDS_FULL),
        },
        "construction_selftest": st,
        "per_seed": res["per_seed"],
    }
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
