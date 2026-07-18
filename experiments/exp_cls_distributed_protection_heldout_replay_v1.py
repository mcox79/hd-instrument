"""exp_cls_distributed_protection_heldout_replay_v1.py

CLS CHAIN-GRADE test -- does interleaved replay of a SMALL SUBSAMPLE of old memories protect a
HELD-OUT, NEVER-REPLAYED subset of old memories from catastrophic interference (genuine DISTRIBUTED
protection, the scalable thing), or only the specific items it explicitly rehearses (per-item
rehearsal, which does NOT scale to "ingest textbook after textbook without forgetting")?

This is the exact revival criterion the CLS VET (a93a9b1e) localized for the pilot
(exp_cls_interleaved_replay_consolidation_pilot_v1, 7a682685f -- HARD_PASS deflated to
MEASURED_MECHANISM): its old pool was too small (every old item rehearsed ~3x, n_never_replayed=0),
so it could not tell distributed protection from per-item rehearsal. Excluding eval items from replay
collapsed old-recall to baseline -> the retention was per-item.

WHAT CHANGED vs the pilot:
  - Scale the OLD pool to 400 structured items (20 classes x 20 exemplars, prototype + bit-flip noise)
    so a FIXED SMALL replay budget is a genuine SUBSAMPLE.
  - Split old items into a REPLAY-ELIGIBLE pool (20%, 4 exemplars/class = 80 items) and a DISJOINT
    HELD-OUT NEVER-REPLAYED pool (80%, 16 exemplars/class = 320 items). The held-out items were TRAINED
    in the old block (legitimately learned) but are NEVER in any replay -> n_never_replayed = 320 (was 0).
  - LOAD-BEARING metric = old-recall on the HELD-OUT NEVER-REPLAYED subset (NOT the replayed subset,
    which was the prior artifact).
  - SWEEP the within-class structure axis P_FLIP (bit-flip noise). Distributed protection is only
    POSSIBLE when old memories share structure (McClelland: interleaved learning discovers/preserves
    shared STRUCTURE; fast ARBITRARY learning needs the hippocampus). The LOW-structure end of the sweep
    is a MEASURED per-item CONTROL: if replaying a sample of an arbitrary/unrelated old memory cannot
    protect un-replayed old memories, held-out collapses to the no_replay floor there BY CONSTRUCTION.
    The sweep therefore shows can-fail as data, not assertion. CITED@ McClelland-McNaughton-O'Reilly
    1995; Kumaran-Hassabis-McClelland 2016.

ARMS (ONE variable = replay COVERAGE of the old pool; held-out eval + init FIXED across arms):
  - no_replay      : single shared store, sequential, NO old replay = McCloskey-Cohen failure mode AND
                     the no-replay LOWER reference (floor for held-out old).
  - subsample_replay (MECHANISM): interleave replay of ONLY the 20% eligible old items; the 80% held-out
                     are NEVER replayed. Does held-out stay protected via the shared representation?
  - replay_all     : interleave replay of ALL 400 old items (incl. held-out) = UPPER reference / ceiling
                     (proves held-out IS protectable if rehearsed; metric not saturated-low).

SWEEP AXIS: P_FLIP in {0.20 ... 0.38} = within-class structure (low P_FLIP = related/structured memories
  like textbook topics; high P_FLIP = arbitrary/unrelated facts). At each point the held-out contrast
  {no_replay floor / subsample / replay_all ceiling} is reported.

PRIOR WORK (credited, NOT stolen): strategy_decisions_2026-05-26 REPLAY row found in a DIFFERENT
  substrate (additive bundle, N=8192) that replay is ZERO-SUM-WITH-NET-POSITIVE -- transfers retention
  from non-replayed to replayed items (cost 0.098 to non-replayed, benefit 0.122 to replayed) -> points
  toward per-item/zero-sum THERE. This cell tests the SHARED-NET (McClelland distributed-representation)
  regime, where distributed protection is mechanistically possible, and maps its structure-dependence.

DEFLATE: if held-out old-recall in subsample_replay sits at the no_replay floor even at the structured
  end -> "per-item rehearsal only, distributed protection refuted at this scale". Do NOT torture toward
  pass. CLAIM-VET-pending; NOT self-declared chain-grade. Self-contained numpy; ASCII-only.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH/H + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test over predictions)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-metrics both tmp+os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retention accuracy, no argmax-noise floor; feasibility = replay_all held-out ceiling >=0.70
# - baseline_in_band at smoke (META_RULE_AG; no_replay held-out forgotten, replay_all held-out high, per point)
# - discriminator survives scale: forgetting deepens with pool/interference; smoke runs FULL grid, 1 seed
# - HARD_PASS strictly above floor: subsample held-out >= no_replay + 0.20 AND >= 0.55 abs at structured end
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = len(P_FLIP_GRID) * len(SEEDS); verdict counts
# - no PYTHONHASHSEED nondeterminism: all splits/seeds are fixed ints or deterministic index arithmetic
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

ANCHOR_NAME = "cls_distributed_protection_heldout_replay_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- Config (difficulty knobs locked from a difficulty-only sweep; mechanism-independent) -----------
N = 128                      # key (hypervector) dimensionality
H = 24                       # shared hidden layer -- capacity PRESSURE drives catastrophic forgetting
OLD_CLASSES = 20             # old classes learned in the first block
OLD_EXEMPLARS = 20           # exemplars per old class -> 400 old items (the LARGE pool)
ELIG_PER_CLASS = 4           # replay-eligible exemplars/class (20% of old = 80 = the subsample)
                             # -> held-out never-replayed = 16/class = 320 (80%); n_never_replayed=320
K_INTERFERE = 10             # NEW-class blocks trained sequentially (interference source)
NEW_CPB = 4                  # new classes per interference block
NEW_EXEMPLARS = 20           # exemplars per new class
E_OLD = 150                  # backprop epochs on the old block
E_NEW = 120                  # backprop epochs per new interference block (overfit new -> real forgetting)
LR = 0.3
# Structure sweep: low P_FLIP = structured/related memories; high = arbitrary/unrelated.
P_FLIP_GRID = [0.20, 0.26, 0.30, 0.34, 0.38] if not SMOKE else [0.20, 0.30, 0.38]
STRUCTURED_PFLIP = 0.20      # the "related-concepts / textbook-topic" end where the HP gate applies
SEEDS = [7] if SMOKE else [7, 17, 23]

OLD_ITEMS = OLD_CLASSES * OLD_EXEMPLARS            # 400
HELDOUT_PER_CLASS = OLD_EXEMPLARS - ELIG_PER_CLASS  # 16
N_HELDOUT = OLD_CLASSES * HELDOUT_PER_CLASS         # 320 never-replayed
N_ELIG = OLD_CLASSES * ELIG_PER_CLASS               # 80 replayed subsample
V = OLD_CLASSES + K_INTERFERE * NEW_CPB             # total classes: 20 + 40 = 60
EXPECTED_N_UNITS = len(P_FLIP_GRID) * len(SEEDS)

# HARD-PASS / HARD-FAIL bands (envelope-fail-bands, pre-registered)
HELDOUT_MARGIN_HP = 0.20     # subsample held-out must beat no_replay floor by this (structured end)
HELDOUT_ABS_HP = 0.55        # subsample held-out absolute floor for a PASS seed (structured end)
RECENT_MIN = 0.55            # every arm must keep learning the recent block (not a frozen net)
DIFF_NOREPLAY_MAX = 0.45     # difficulty-on (per point): no_replay held-out <= this (forgetting real)
DIFF_INITIAL_MIN = 0.70      # difficulty-on: net LEARNED held-out old in the first block (else vacuous)
DIFF_CEILING_MIN = 0.70      # difficulty-on: replay_all held-out >= this (protectable ceiling)
CANFAIL_EPS = 0.05           # subsample held-out <= no_replay + this -> per-item rehearsal (that point)


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class SharedNet:
    """N->H->V shared-hidden-layer classifier (tanh + softmax), batch backprop.

    The shared hidden layer is the distributed/overlapping representation whose units participate in
    every class; sequential class-incremental training under capacity pressure catastrophically
    overwrites it (McCloskey-Cohen). Interleaved replay of a class sample maintains its region
    (McClelland distributed protection).
    """

    def __init__(self, n: int, h: int, v: int, rng: np.random.Generator):
        self.W1 = (rng.standard_normal((h, n)) / np.sqrt(n)).astype(np.float64)
        self.W2 = (rng.standard_normal((v, h)) / np.sqrt(h)).astype(np.float64)

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int, lr: float, v: int) -> None:
        if X.shape[0] == 0:
            return
        m = X.shape[0]
        oneh = np.zeros((m, v), dtype=np.float64)
        oneh[np.arange(m), y] = 1.0
        for _ in range(epochs):
            A1 = np.tanh(X @ self.W1.T)
            P = _softmax(A1 @ self.W2.T)
            dlog = (P - oneh) / m
            dW2 = dlog.T @ A1
            dA1 = dlog @ self.W2
            dZ1 = dA1 * (1.0 - A1 * A1)
            dW1 = dZ1.T @ X
            self.W2 -= lr * dW2
            self.W1 -= lr * dW1

    def predict(self, X: np.ndarray) -> np.ndarray:
        A1 = np.tanh(X @ self.W1.T)
        return (A1 @ self.W2.T).argmax(axis=1)


def _make_bank(rng: np.random.Generator, class_ids: np.ndarray, n_exemplars: int, p_flip: float
               ) -> Tuple[np.ndarray, np.ndarray]:
    """Structured exemplars: per class a bipolar prototype; exemplars flip each bit w.p. p_flip."""
    nc = class_ids.shape[0]
    protos = np.sign(rng.standard_normal((nc, N)))
    protos[protos == 0] = 1.0
    X = np.repeat(protos, n_exemplars, axis=0).astype(np.float64)
    flips = rng.random(X.shape) < p_flip
    X = X * np.where(flips, -1.0, 1.0)
    labels = np.repeat(class_ids, n_exemplars).astype(np.int64)
    return X, labels


def _recall(net: SharedNet, X: np.ndarray, y: np.ndarray) -> float:
    if X.shape[0] == 0:
        return 0.0
    return float((net.predict(X) == y).mean())


def _elig_heldout_idx() -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic split: first ELIG_PER_CLASS exemplars/class -> eligible; rest -> held-out."""
    elig, held = [], []
    for c in range(OLD_CLASSES):
        base = c * OLD_EXEMPLARS
        elig.extend(range(base, base + ELIG_PER_CLASS))
        held.extend(range(base + ELIG_PER_CLASS, base + OLD_EXEMPLARS))
    return np.array(elig, dtype=np.int64), np.array(held, dtype=np.int64)


def _train_arm(replay_mode: str, seed: int, old_X: np.ndarray, old_y: np.ndarray,
               elig_idx: np.ndarray, held_idx: np.ndarray,
               new_blocks: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
    """replay_mode in {none, subsample, all}. Returns per-arm recalls + a prediction digest."""
    net = SharedNet(N, H, V, np.random.default_rng(seed + 1))   # SAME init across arms (one-variable)
    net.train(old_X, old_y, E_OLD, LR, V)
    heldout_initial = _recall(net, old_X[held_idx], old_y[held_idx])

    for b in range(K_INTERFERE):
        Xb, yb = new_blocks[b]
        if replay_mode == "none":
            trX, trY = Xb, yb
        elif replay_mode == "subsample":
            trX = np.concatenate([Xb, old_X[elig_idx]]); trY = np.concatenate([yb, old_y[elig_idx]])
        elif replay_mode == "all":
            trX = np.concatenate([Xb, old_X]); trY = np.concatenate([yb, old_y])
        else:
            raise ValueError("unknown replay_mode: %s" % replay_mode)
        net.train(trX, trY, E_NEW, LR, V)

    heldout = _recall(net, old_X[held_idx], old_y[held_idx])    # LOAD-BEARING (never-replayed old)
    replayed = _recall(net, old_X[elig_idx], old_y[elig_idx])   # reference (rehearsed subsample)
    recent = _recall(net, new_blocks[-1][0], new_blocks[-1][1]) # guard (net still learning new)
    dig_X = np.concatenate([old_X, new_blocks[-1][0]])
    digest = hashlib.sha256(net.predict(dig_X).tobytes()).hexdigest()
    return {"heldout": round(heldout, 3), "replayed": round(replayed, 3),
            "recent": round(recent, 3), "heldout_initial": round(heldout_initial, 3), "digest": digest}


def _run_point(p_flip: float, seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    old_X, old_y = _make_bank(rng, np.arange(OLD_CLASSES), OLD_EXEMPLARS, p_flip)
    new_blocks: List[Tuple[np.ndarray, np.ndarray]] = []
    for b in range(K_INTERFERE):
        cls = np.arange(OLD_CLASSES + b * NEW_CPB, OLD_CLASSES + (b + 1) * NEW_CPB)
        new_blocks.append(_make_bank(rng, cls, NEW_EXEMPLARS, p_flip))
    elig_idx, held_idx = _elig_heldout_idx()
    arms = {m: _train_arm(m, seed, old_X, old_y, elig_idx, held_idx, new_blocks)
            for m in ("none", "subsample", "all")}
    keys = ("heldout", "replayed", "recent", "heldout_initial")
    return {"p_flip": p_flip, "seed": seed,
            "no_replay": {k: arms["none"][k] for k in keys},
            "subsample_replay": {k: arms["subsample"][k] for k in keys},
            "replay_all": {k: arms["all"][k] for k in keys},
            "arm_digests": {"no_replay": arms["none"]["digest"],
                            "subsample_replay": arms["subsample"]["digest"],
                            "replay_all": arms["all"]["digest"]}}


def run() -> Dict:
    per_unit = [_run_point(p, s) for p in P_FLIP_GRID for s in SEEDS]

    points = []
    arms_differ = True
    for p in P_FLIP_GRID:
        units = [u for u in per_unit if u["p_flip"] == p]

        def _mean(arm, key):
            return float(np.mean([u[arm][key] for u in units]))

        agg = {arm: {k: round(_mean(arm, k), 3) for k in ("heldout", "replayed", "recent", "heldout_initial")}
               for arm in ("no_replay", "subsample_replay", "replay_all")}
        # per-seed HARD-PASS count at this point
        hp = 0
        for u in units:
            sub = u["subsample_replay"]; base = u["no_replay"]
            if (sub["heldout"] >= base["heldout"] + HELDOUT_MARGIN_HP
                    and sub["heldout"] >= HELDOUT_ABS_HP and sub["recent"] >= RECENT_MIN):
                hp += 1
        diff_ok, diff_msg = _difficulty_ok(agg)
        for u in units:
            d = u["arm_digests"]
            if d["no_replay"] == d["subsample_replay"] or d["subsample_replay"] == d["replay_all"] \
                    or d["no_replay"] == d["replay_all"]:
                arms_differ = False
        points.append({"p_flip": p, "agg": agg, "hp_seeds": hp, "n_seeds": len(units),
                       "difficulty_ok": diff_ok, "difficulty_msg": diff_msg})

    return {"points": points, "per_unit": per_unit, "n_units": len(per_unit),
            "expected_n_units": EXPECTED_N_UNITS, "arms_differ": arms_differ,
            "n_never_replayed": N_HELDOUT, "n_replayed_subsample": N_ELIG}


def _difficulty_ok(agg: Dict) -> Tuple[bool, str]:
    base = agg["no_replay"]; ceil = agg["replay_all"]; sub = agg["subsample_replay"]
    checks = [
        (base["heldout_initial"] >= DIFF_INITIAL_MIN, "net_learned_old_initial"),
        (base["heldout"] <= DIFF_NOREPLAY_MAX, "no_replay_forgets_heldout"),
        (ceil["heldout"] >= DIFF_CEILING_MIN, "replay_all_protects_ceiling"),
        (base["recent"] >= RECENT_MIN and sub["recent"] >= RECENT_MIN and ceil["recent"] >= RECENT_MIN,
         "all_arms_learn_recent"),
    ]
    fails = [name for ok, name in checks if not ok]
    return (len(fails) == 0), ("OK" if not fails else "FAILS:" + ",".join(fails))


def _fmt_curve(points: List[Dict]) -> str:
    segs = []
    for pt in points:
        a = pt["agg"]
        segs.append("P=%.2f[no=%.3f sub=%.3f all=%.3f hp=%d/%d diff=%s]"
                    % (pt["p_flip"], a["no_replay"]["heldout"], a["subsample_replay"]["heldout"],
                       a["replay_all"]["heldout"], pt["hp_seeds"], pt["n_seeds"],
                       "Y" if pt["difficulty_ok"] else "N"))
    return " ".join(segs)


def verdict(r: Dict) -> Tuple[str, str]:
    points = r["points"]
    curve = _fmt_curve(points)
    struct = next(pt for pt in points if abs(pt["p_flip"] - STRUCTURED_PFLIP) < 1e-9)
    arb = points[-1]  # highest P_FLIP = arbitrary/unrelated end (internal per-item control)
    ns = struct["n_seeds"]; need = 2 if ns >= 3 else 1
    sa = struct["agg"]; aa = arb["agg"]
    s = ("HELD-OUT never-replayed old-recall curve (no_replay floor / subsample / replay_all ceiling): "
         "%s | replayed-subset(structured)=%.3f n_never_replayed=%d n_replayed=%d | "
         "arms_differ=%s units=%d/%d" % (curve, sa["subsample_replay"]["replayed"], r["n_never_replayed"],
                                          r["n_replayed_subsample"], r["arms_differ"], r["n_units"], r["expected_n_units"]))

    if r["n_units"] != r["expected_n_units"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units. %s" % (r["n_units"], r["expected_n_units"], s))
    if not r["arms_differ"]:
        return ("HARD_FAIL", "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: " + s)
    if not struct["difficulty_ok"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND_REGIME_INCONCLUSIVE: structured-end difficulty gate off (%s) -- "
                "cannot distinguish distributed vs per-item until baselines in band. " % struct["difficulty_msg"] + s)

    sub_h = sa["subsample_replay"]["heldout"]; base_h = sa["no_replay"]["heldout"]
    # CAN-FAIL (honest bounded result): even at the STRUCTURED end, held-out collapses to the floor.
    if sub_h <= base_h + CANFAIL_EPS:
        return ("HARD_FAIL",
                "HARD_FAIL_PER_ITEM_REHEARSAL: even at the structured end (P_FLIP=%.2f), subsample-replay "
                "held-out old-recall sits at the no_replay floor -- replaying a subsample protects ONLY the "
                "explicitly rehearsed items, NOT the never-replayed old memories. Distributed protection "
                "REFUTED at this scale; per-item only (does NOT scale to textbook-after-textbook). " % STRUCTURED_PFLIP + s)
    if struct["hp_seeds"] >= need:
        # note whether the arbitrary end collapses (structure-dependence = mechanism confirmation)
        arb_collapse = (aa["subsample_replay"]["heldout"] <= aa["no_replay"]["heldout"] + 0.20)
        return ("HARD_PASS",
                "HARD_PASS_DISTRIBUTED_PROTECTION: at the structured/related-memory end (P_FLIP=%.2f) replaying "
                "a %d-item subsample (%d%% of old) protects the %d NEVER-REPLAYED old memories above the "
                "no_replay floor (margin>=%.2f abs>=%.2f, %d/%d seeds) -- distributed protection is REAL "
                "(the scalable thing). Structure-dependence confirms the mechanism: arbitrary-end collapse=%s "
                "(subsample->floor when memories lack shared structure). CLAIM-VET-pending, NOT self-declared "
                "chain-grade. " % (STRUCTURED_PFLIP, r["n_replayed_subsample"], int(100 * N_ELIG / OLD_ITEMS),
                                   r["n_never_replayed"], HELDOUT_MARGIN_HP, HELDOUT_ABS_HP, struct["hp_seeds"], ns,
                                   arb_collapse) + s)
    if sub_h > base_h + CANFAIL_EPS:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_PROTECTION: subsample held-out beats the no_replay floor at the structured "
                "end but below the >=%.2f margin / >=%.2f abs bar on >=%d seeds -- partial distributed protection. "
                % (HELDOUT_MARGIN_HP, HELDOUT_ABS_HP, need) + s)
    return ("HARD_FAIL", "HARD_FAIL_NO_PROTECTION: " + s)


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
    """Exercise the REAL code path (SharedNet + run()) at FULL grid, 1 seed.

    Forgetting deepens with pool size + interference (not seeds), so difficulty is checked at the regime
    the FULL run uses (per DISCRIMINATOR-MUST-SURVIVE-SCALE); only the seed count is reduced.
    """
    global SEEDS
    _s = SEEDS
    SEEDS = [7]
    try:
        r = run()
        assert r["arms_differ"], "selftest: the 3 replay-coverage arms must differ"
        assert r["n_never_replayed"] == N_HELDOUT and r["n_never_replayed"] > 0, \
            "selftest: held-out never-replayed set must be non-empty (VET critique fix)"
        struct = next(pt for pt in r["points"] if abs(pt["p_flip"] - STRUCTURED_PFLIP) < 1e-9)
        assert struct["agg"]["no_replay"]["heldout_initial"] >= 0.5, \
            "selftest: net did not learn old held-out at structured end (init=%.3f)" % struct["agg"]["no_replay"]["heldout_initial"]
        print("[selftest] PASS real-code-path: curve %s | n_never_replayed=%d arms_differ=%s"
              % (_fmt_curve(r["points"]), r["n_never_replayed"], r["arms_differ"]), flush=True)
    finally:
        SEEDS = _s


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print("[config] anchor=%s mode=%s N=%d H=%d V=%d old_items=%d elig=%d heldout=%d blocks=%d "
          "E_OLD=%d E_NEW=%d P_FLIP_GRID=%s seeds=%s expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N, H, V, OLD_ITEMS, N_ELIG, N_HELDOUT, K_INTERFERE, E_OLD, E_NEW,
             P_FLIP_GRID, SEEDS, EXPECTED_N_UNITS), flush=True)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)

    struct = next(pt for pt in r["points"] if abs(pt["p_flip"] - STRUCTURED_PFLIP) < 1e-9)
    sa = struct["agg"]
    sub = sa["subsample_replay"]; base = sa["no_replay"]; ceil = sa["replay_all"]
    gate_claims = [
        record_gate("struct_subsample_heldout_recall", sub["heldout"], HELDOUT_ABS_HP, ">=",
                    "distributed protection of never-replayed old at structured end (LOAD-BEARING)"),
        record_gate("struct_subsample_heldout_margin", sub["heldout"] - base["heldout"], HELDOUT_MARGIN_HP, ">=",
                    "subsample protects held-out above the no-replay floor (structured end)"),
        record_gate("struct_difficulty_no_replay", base["heldout"], DIFF_NOREPLAY_MAX, "<=",
                    "catastrophic forgetting of held-out old is real (difficulty ON)"),
        record_gate("struct_difficulty_replay_all_ceiling", ceil["heldout"], DIFF_CEILING_MIN, ">=",
                    "held-out IS protectable if rehearsed (ceiling / not saturated-low)"),
        record_gate("struct_difficulty_initial", base["heldout_initial"], DIFF_INITIAL_MIN, ">=",
                    "net learned held-out old initially (forgetting not inability)"),
        record_gate("struct_hp_seeds", struct["hp_seeds"], (2 if struct["n_seeds"] >= 3 else 1), ">=",
                    "seeds where subsample protects held-out above bar (structured end)"),
        record_gate("cardinality", r["n_units"], EXPECTED_N_UNITS, ">=",
                    "all sweep x seed units completed (META_RULE_H)"),
    ]
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_units": r["n_units"], "expected_n_units": EXPECTED_N_UNITS, "arms_differ": r["arms_differ"],
               "n_never_replayed": r["n_never_replayed"], "n_replayed_subsample": r["n_replayed_subsample"],
               "points": r["points"], "per_unit": r["per_unit"],
               "config": {"N": N, "H": H, "V": V, "OLD_CLASSES": OLD_CLASSES, "OLD_EXEMPLARS": OLD_EXEMPLARS,
                          "ELIG_PER_CLASS": ELIG_PER_CLASS, "K_INTERFERE": K_INTERFERE, "NEW_CPB": NEW_CPB,
                          "NEW_EXEMPLARS": NEW_EXEMPLARS, "E_OLD": E_OLD, "E_NEW": E_NEW, "LR": LR,
                          "P_FLIP_GRID": P_FLIP_GRID, "STRUCTURED_PFLIP": STRUCTURED_PFLIP, "seeds": SEEDS},
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
