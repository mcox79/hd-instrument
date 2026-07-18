"""exp_cls_distributed_protection_budget_envelope_v1.py

ENVELOPE characterization (NOT a new capability claim) of the VET-confirmed distributed-consolidation
effect from exp_cls_distributed_protection_independent_content_v1 (VET ad3947bd, MEASURED_MECHANISM):
replaying a SMALL SUBSAMPLE of old memories protects the INDEPENDENT within-class content of NEVER-REPLAYED
held-out memories -- REAL (both confounds at 0.000, 3/3 seeds) but PARTIAL (equal-compute-corrected genuine
effect ~0.11 at a 25% replay subsample).

LOAD-BEARING QUESTION (for continual textbook ingestion): does the equal-compute-corrected never-replayed
protection scale USEFULLY with replay BUDGET? Does a SMALL replay budget protect a LARGE never-replayed set
(sub-linear -> a usable foundation), or does protection track budget ~linearly (must-rehearse-most -> does
not scale), or stay FLAT-marginal (budget-independent, small)?

WHAT CHANGES vs the parent cell: the ONE swept variable is REPLAY BUDGET (ELIG_PER_CLASS = # old exemplars
per class made replay-eligible). Everything else -- cue/target construction, the shared class structure
(SHARED_FRAC fixed at the structured end 0.75), interference schedule, net, init, seeds -- is IDENTICAL to
the parent (so ELIG_PER_CLASS=3 REPRODUCES the parent's MEASURED subsample held-out 0.247 as a positive
control; deviation > tolerance = regime/invocation drift).

THE ESSENTIAL NEW ARM (per VET ad3947bd): EQUAL-COMPUTE random-filler control at EVERY budget point. Without
it the effect is INFLATED by generic-regularization (extra interleaved data slows over-fitting to the new
block regardless of what that data is). The GENUINE distributed-consolidation effect =
  subsample_replay_heldout  -  equal_compute_filler_heldout
where the filler is the SAME NUMBER of interleaved items as the eligible subsample, but FRESH RANDOM content
(random protos + random probes + random targets) carrying ZERO information about the old distribution. The
filler matches compute/batch/regularization but not old-item content; the residual is the part attributable
to replaying the actual OLD distribution = distributed consolidation. CITED@ McClelland-McNaughton-O'Reilly
1995; Kumaran-Hassabis-McClelland 2016. Prior-work: v211 REPLAY H-A found replay ZERO-SUM-WITH-NET-POSITIVE
in the N=8192 substrate-storage regime (transfers retention replayed<-non-replayed); this cell characterizes
the never-replayed FREE-protection component in the independent-content MLP regime across budget.

ARMS (per budget point; ONE variable = replay budget; eval/cue/target/init FIXED across arms and budgets):
  * no_replay          : sequential, NO old replay = forgetting FLOOR (budget-independent net, held-eval
                         sliced per budget).
  * subsample_replay   : (MECHANISM) interleave replay of ONLY the eligible subsample; held-out NEVER
                         replayed.
  * equal_compute_filler: (NEW ESSENTIAL CONTROL) interleave the SAME # of FRESH-RANDOM filler items;
                         isolates generic-regularization from old-content consolidation.
  * replay_all         : interleave replay of ALL old = protectable CEILING (budget-independent net, sliced).
  * one_nn_proximity   : (CONFOUND, zero training) held target := nearest replayed cue's target. MUST stay
                         ~0 across budgets (independence holds).
  * fresh_net_subsample: (CONFOUND) fresh net trained ONLY on the subsample. MUST stay ~0 across budgets.

DESIGN-GATE (verified at smoke BEFORE full):
  (1) REAL baselines at EACH budget = no_replay floor + equal_compute_filler + replay_all ceiling + 2
      confounds; genuine effect = subsample MINUS equal_compute_filler.
  (2) LOAD-BEARING metric = the EQUAL-COMPUTE-CORRECTED never-replayed protection vs budget curve.
  (3) CAN-FAIL / honest read (characterization, no HARD_PASS): report the SHAPE --
      SUB_LINEAR_EFFICIENT (small budget, large protection = useful) vs LINEAR_MUST_REHEARSE (tracks budget
      = does not scale) vs FLAT_MARGINAL (budget-independent, small). The honest curve IS the result.
  (4) ONE variable = replay budget (ELIG_PER_CLASS). Confounds must stay ~0 across budgets (independence).

DEFLATE: report the equal-compute-CORRECTED effect, never the raw subsample-over-floor. CLAIM-VET-pending;
NOT self-declared chain-grade. Self-contained numpy; ASCII-only; local-runnable; glass-box.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH/H + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test over per-arm held-out predictions per unit)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-metrics both tmp+os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retrieval accuracy over a codebook, chance=1/OLD_ITEMS; feasibility = replay_all ceiling >= 0.55
# - baseline_in_band at smoke (META_RULE_AG): no_replay forgets, replay_all protects, BOTH confounds fail
# - discriminator survives scale: forgetting deepens with pool/interference; smoke runs anchor+ends grid, 1 seed
# - characterization (NOT HARD_PASS): shape of the equal-compute-corrected genuine effect vs budget curve
# - positive control (Gate D): ELIG_PER_CLASS=3 subsample held-out reproduces parent MEASURED 0.247 (tol 0.10)
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = len(BUDGET_GRID) * len(SEEDS); verdict counts units
# - no PYTHONHASHSEED nondeterminism: all splits/seeds/targets/filler are fixed ints or deterministic index math
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

ANCHOR_NAME = "cls_distributed_protection_budget_envelope_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# --- Config (IDENTICAL to parent exp_cls_distributed_protection_independent_content_v1 except the budget) ---
N = 256                      # cue (hypervector) dimensionality
D_T = 64                     # target vector dimensionality (independent per-item content)
H = 160                      # shared hidden layer -- distributed/overlapping representation
OLD_CLASSES = 12             # old classes learned in the first block
OLD_EXEMPLARS = 12           # exemplars per old class -> 144 old items
K_INTERFERE = 8              # NEW-class interference blocks trained sequentially
NEW_CPB = 3                  # new classes per interference block
NEW_EXEMPLARS = 12           # exemplars per new class
E_OLD = 400                  # epochs on the old block (memorize independent targets)
E_NEW = 200                  # epochs per new interference block (overfit new -> real forgetting)
LR = 0.04                    # MEASURED@ parent smoke tuning: LR>=0.06 diverges (linear MSE readout); 0.04 stable
SHARED_FRAC = 0.75           # FIXED at the structured end (distributed protection most plausible; the parent
                             # STRUCTURED_FRAC where the VET-confirmed effect lives). ONE variable = budget.

# THE SWEPT VARIABLE = replay budget = # old exemplars/class made replay-eligible (the subsample).
# fraction of old replayed = ELIG_PER_CLASS / OLD_EXEMPLARS. Grid spans a small-budget -> large-budget range;
# ELIG_PER_CLASS=3 (25%) is the parent's anchor (positive-control reproduction of MEASURED 0.247).
BUDGET_GRID = [1, 2, 3, 4, 6, 9] if not SMOKE else [1, 3, 9]   # fractions 8.3/16.7/25/33.3/50/75 %
ANCHOR_ELIG = 3                                                 # parent regime (25%) positive control
SEEDS = [7] if SMOKE else [7, 17, 23]

OLD_ITEMS = OLD_CLASSES * OLD_EXEMPLARS               # 144
V_CLASSES = OLD_CLASSES + K_INTERFERE * NEW_CPB       # 12 + 24 = 36 total classes
EXPECTED_N_UNITS = len(BUDGET_GRID) * len(SEEDS)
CHANCE = 1.0 / OLD_ITEMS                              # THEORETICAL@ retrieval chance over old codebook

# Positive-control anchor (Gate D): parent MEASURED subsample held-out at ELIG=3 / SF=0.75.
PARENT_ANCHOR_SUBSAMPLE = 0.247   # MEASURED@d:/AI/hd-instrument/data/exp_cls_distributed_protection_independent_content_v1/metrics.json:points[SF=0.75].agg.subsample_replay.heldout
PARENT_ANCHOR_TOL = 0.10          # identical regime -> should reproduce within tol; > tol = drift (flag)

# DIFFICULTY-ON gates (per budget, on aggregate at the structured end) -- reused from parent:
DIFF_INITIAL_MIN = 0.70      # net LEARNED held-out independent targets in the first block (else vacuous)
DIFF_NOREPLAY_MAX = 0.30     # no_replay held-out retrieval collapses (forgetting real)
DIFF_CEILING_MIN = 0.55      # replay_all held-out retrieval high (independent content IS protectable)
DIFF_CONFOUND_MAX = 0.25     # BOTH confounds must FAIL to recover held-out (proves independence)

# Descriptor thresholds for the SHAPE classification (characterization, NOT pass/fail bands):
GENUINE_MARGINAL_MAX = 0.08  # if max genuine effect over budgets < this -> FLAT_MARGINAL (budget-independent, small)
SUBLINEAR_FACTOR = 1.8       # eff_ratio >= this * linear_ratio (and top budget effect real) -> SUB_LINEAR_EFFICIENT
LINEAR_FACTOR = 1.3          # eff_ratio <= this * linear_ratio -> LINEAR_MUST_REHEARSE (tracks budget)
GENUINE_TOP_MIN = 0.08       # top-budget genuine effect must exceed this to call SUB_LINEAR meaningful


def _bipolar(rng: np.random.Generator, shape) -> np.ndarray:
    x = np.sign(rng.standard_normal(shape))
    x[x == 0] = 1.0
    return x.astype(np.float64)


class RegNet:
    """cue(N) -> hidden(H) tanh -> target(D_T) linear. MSE regression, batch backprop.

    The shared hidden layer is the distributed/overlapping representation. Replaying a class sample can keep
    the shared feature basis aligned (McClelland); whether that protects the INDEPENDENT per-item target
    readout of NEVER-REPLAYED items, and how that scales with replay budget, is what this cell characterizes.
    """

    def __init__(self, n: int, h: int, d_t: int, rng: np.random.Generator):
        self.W1 = (rng.standard_normal((h, n)) / np.sqrt(n)).astype(np.float64)
        self.W2 = (rng.standard_normal((d_t, h)) / np.sqrt(h)).astype(np.float64)

    def clone(self) -> "RegNet":
        c = RegNet.__new__(RegNet)
        c.W1 = self.W1.copy()
        c.W2 = self.W2.copy()
        return c

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


def _pred_tau(net: RegNet, X: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Nearest-target retrieval over the full old codebook -> retrieved item index per row."""
    pred = net.output(X)
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-9)
    cn = codebook / (np.linalg.norm(codebook, axis=1, keepdims=True) + 1e-9)
    return (pn @ cn.T).argmax(axis=1)


def _make_old_bank(rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Old bank: cue = [shared class code | item-specific probe]; target = UNIQUE per-item bipolar vector.

    Returns (X_cue[OLD_ITEMS,N], tau[OLD_ITEMS] item-index, codebook[OLD_ITEMS,D_T], proto[OLD_CLASSES,s]).
    Independent within-class content: tau is a unique index per item; class tells you NOTHING about which target.
    """
    s = int(round(SHARED_FRAC * N))
    proto = _bipolar(rng, (OLD_CLASSES, s))      # shared class code (first s dims)
    X = np.zeros((OLD_ITEMS, N), dtype=np.float64)
    for c in range(OLD_CLASSES):
        for e in range(OLD_EXEMPLARS):
            i = c * OLD_EXEMPLARS + e
            X[i, :s] = proto[c]                                  # shared class structure
            X[i, s:] = _bipolar(rng, (N - s,))                   # item-specific probe (independent)
    tau = np.arange(OLD_ITEMS, dtype=np.int64)                   # unique per-item target index
    codebook = _bipolar(rng, (OLD_ITEMS, D_T))                   # independent target content
    return X, tau, codebook, proto


def _make_new_block(rng: np.random.Generator, nc: int) -> Tuple[np.ndarray, np.ndarray]:
    """Interference block: same cue structure, fresh random targets (drives forgetting via shared W1/W2)."""
    s = int(round(SHARED_FRAC * N))
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


def _make_filler_random(rng: np.random.Generator, n_items: int) -> Tuple[np.ndarray, np.ndarray]:
    """EQUAL-COMPUTE control (RANDOM): n_items FRESH-RANDOM cues (random protos+probes) + FRESH-RANDOM targets.

    Same cue format + item count as the eligible subsample; matches extra compute/batch/generic-regularization
    but carries ZERO old-distribution information (fresh random protos, NOT old class codes). CAVEAT (surfaced
    at smoke): random protos are MORE DIVERSE than the correlated 12-class old items, so this filler can be a
    STRONGER regularizer than the old subsample -> it can OVER-correct. Reported as a bracket; the STRUCT
    filler below is the fairer diversity-matched primary control.
    """
    s = int(round(SHARED_FRAC * N))
    nfc = max(1, n_items // NEW_EXEMPLARS + 1)
    proto = _bipolar(rng, (nfc, s))
    X = np.zeros((n_items, N), dtype=np.float64)
    for i in range(n_items):
        X[i, :s] = proto[i % nfc]
        X[i, s:] = _bipolar(rng, (N - s,))
    T = _bipolar(rng, (n_items, D_T))
    return X, T


def _make_filler_struct(rng: np.random.Generator, n_items: int, old_proto: np.ndarray
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """EQUAL-COMPUTE control (STRUCT, PRIMARY): reuses the OLD class protos (same shared-structure subspace and
    same class-code DIVERSITY as the eligible subsample) + FRESH probes + FRESH-RANDOM targets.

    Holds constant EVERYTHING the eligible subsample provides EXCEPT the specific old cue->target CONTENT:
    same volume, same old class structure re-activation, same class-code diversity. The residual
    (subsample - struct_filler) isolates the protection attributable to the old items' OWN retained
    cue->target traces (distributed consolidation of never-replayed independent content) -- NOT generic
    regularization and NOT mere old-structure reactivation. This is the fairer equal-compute control.
    """
    s = int(round(SHARED_FRAC * N))
    nc = old_proto.shape[0]
    X = np.zeros((n_items, N), dtype=np.float64)
    for i in range(n_items):
        X[i, :s] = old_proto[i % nc]                             # reuse OLD class codes (diversity matched)
        X[i, s:] = _bipolar(rng, (N - s,))                       # fresh probe (not an old item)
    T = _bipolar(rng, (n_items, D_T))                            # random target (no old content)
    return X, T


def _split_idx(elig_per_class: int) -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic split: first elig_per_class exemplars/class -> eligible (replayed); rest -> held-out."""
    elig, held = [], []
    for c in range(OLD_CLASSES):
        base = c * OLD_EXEMPLARS
        elig.extend(range(base, base + elig_per_class))
        held.extend(range(base + elig_per_class, base + OLD_EXEMPLARS))
    return np.array(elig, dtype=np.int64), np.array(held, dtype=np.int64)


def _confound_one_nn(old_X, old_tau, elig_idx, held_idx) -> np.ndarray:
    """Zero-training 1-NN: held-out target := target of nearest REPLAYED cue (cosine). Returns pred_tau."""
    Xe = old_X[elig_idx]; Xh = old_X[held_idx]
    en = Xe / (np.linalg.norm(Xe, axis=1, keepdims=True) + 1e-9)
    hn = Xh / (np.linalg.norm(Xh, axis=1, keepdims=True) + 1e-9)
    nn = (hn @ en.T).argmax(axis=1)
    return old_tau[elig_idx][nn]


def _run_seed(seed: int) -> List[Dict]:
    """Train the budget-independent nets ONCE, then per budget train the budget-dependent arms + confounds."""
    rng = np.random.default_rng(seed)
    old_X, old_tau, codebook, old_proto = _make_old_bank(rng)
    old_T = codebook[old_tau]
    new_blocks = []
    for b in range(K_INTERFERE):
        nc = NEW_CPB
        new_blocks.append(_make_new_block(rng, nc))

    # Base net: memorize the old block ONCE (identical init+old-training across all learned arms/budgets).
    base = RegNet(N, H, D_T, np.random.default_rng(seed + 1))
    base.train(old_X, old_T, E_OLD, LR)
    init_pred = _pred_tau(base, old_X, codebook)                 # retrieval right after old-block memorization
    init_correct = (init_pred == old_tau).astype(np.float64)

    def _interfere(net: RegNet, replay_X, replay_T) -> RegNet:
        for b in range(K_INTERFERE):
            Xb, Tb = new_blocks[b]
            if replay_X is None:
                trX, trT = Xb, Tb
            else:
                trX = np.concatenate([Xb, replay_X]); trT = np.concatenate([Tb, replay_T])
            net.train(trX, trT, E_NEW, LR)
        return net

    # Budget-INDEPENDENT arms (train once; held-eval sliced per budget). Keep full pred over old for slicing.
    net_none = _interfere(base.clone(), None, None)
    none_pred_all = _pred_tau(net_none, old_X, codebook)
    none_correct = (none_pred_all == old_tau).astype(np.float64)
    net_all = _interfere(base.clone(), old_X, old_T)
    all_pred_all = _pred_tau(net_all, old_X, codebook)
    all_correct = (all_pred_all == old_tau).astype(np.float64)

    units = []
    for elig in BUDGET_GRID:
        elig_idx, held_idx = _split_idx(elig)
        n_elig = elig_idx.shape[0]; n_held = held_idx.shape[0]

        # MECHANISM: replay the eligible subsample.
        net_sub = _interfere(base.clone(), old_X[elig_idx], old_T[elig_idx])
        sub_pred = _pred_tau(net_sub, old_X[held_idx], codebook)
        sub_heldout = float((sub_pred == old_tau[held_idx]).mean())

        # EQUAL-COMPUTE control (STRUCT, PRIMARY): old protos + fresh probes/targets (diversity matched).
        sX, sT = _make_filler_struct(np.random.default_rng(seed + 7000 + elig), n_elig, old_proto)
        net_fs = _interfere(base.clone(), sX, sT)
        fs_pred = _pred_tau(net_fs, old_X[held_idx], codebook)
        fs_heldout = float((fs_pred == old_tau[held_idx]).mean())

        # EQUAL-COMPUTE control (RANDOM, bracket): fresh random content (deterministic per seed,budget).
        fX, fT = _make_filler_random(np.random.default_rng(seed + 5000 + elig), n_elig)
        net_fil = _interfere(base.clone(), fX, fT)
        fil_pred = _pred_tau(net_fil, old_X[held_idx], codebook)
        fil_heldout = float((fil_pred == old_tau[held_idx]).mean())

        # CONFOUND: fresh net trained ONLY on the subsample (never sees held-out; zero interference).
        net_fresh = RegNet(N, H, D_T, np.random.default_rng(seed + 99))
        net_fresh.train(old_X[elig_idx], old_T[elig_idx], E_OLD, LR)
        fresh_pred = _pred_tau(net_fresh, old_X[held_idx], codebook)
        fresh_heldout = float((fresh_pred == old_tau[held_idx]).mean())

        # CONFOUND: 1-NN proximity to replayed cues.
        nn_pred = _confound_one_nn(old_X, old_tau, elig_idx, held_idx)
        nn_heldout = float((nn_pred == old_tau[held_idx]).mean())

        no_heldout = float(none_correct[held_idx].mean())
        all_heldout = float(all_correct[held_idx].mean())
        init_heldout = float(init_correct[held_idx].mean())
        genuine_struct = sub_heldout - fs_heldout               # LOAD-BEARING (fairer, diversity-matched control)
        genuine_random = sub_heldout - fil_heldout              # bracket (random filler; may over-correct)
        raw = sub_heldout - no_heldout                          # inflated (subsample over floor)
        struct_contrib = fs_heldout - no_heldout                # structure-reactivation + generic reg component
        filler_contrib = fil_heldout - no_heldout               # generic-regularization component (random)

        digests = {
            "no_replay": hashlib.sha256(none_pred_all[held_idx].tobytes()).hexdigest(),
            "subsample_replay": hashlib.sha256(sub_pred.tobytes()).hexdigest(),
            "equal_compute_struct": hashlib.sha256(fs_pred.tobytes()).hexdigest(),
            "equal_compute_random": hashlib.sha256(fil_pred.tobytes()).hexdigest(),
            "replay_all": hashlib.sha256(all_pred_all[held_idx].tobytes()).hexdigest(),
            "one_nn_proximity": hashlib.sha256(nn_pred.tobytes()).hexdigest(),
            "fresh_net_subsample": hashlib.sha256(fresh_pred.tobytes()).hexdigest(),
        }
        units.append({
            "elig_per_class": elig, "budget_frac": round(elig / OLD_EXEMPLARS, 4), "seed": seed,
            "n_replayed": n_elig, "n_never_replayed": n_held,
            "no_replay": round(no_heldout, 4), "subsample_replay": round(sub_heldout, 4),
            "equal_compute_struct": round(fs_heldout, 4), "equal_compute_random": round(fil_heldout, 4),
            "replay_all": round(all_heldout, 4),
            "one_nn_proximity": round(nn_heldout, 4), "fresh_net_subsample": round(fresh_heldout, 4),
            "heldout_initial": round(init_heldout, 4),
            "genuine_effect": round(genuine_struct, 4), "genuine_effect_random": round(genuine_random, 4),
            "raw_effect": round(raw, 4),
            "struct_contribution": round(struct_contrib, 4), "filler_contribution": round(filler_contrib, 4),
            "arm_digests": digests,
        })
    return units


ARMS7 = ("no_replay", "subsample_replay", "equal_compute_struct", "equal_compute_random", "replay_all",
         "one_nn_proximity", "fresh_net_subsample")
# META_RULE_AF exemption: the two zero-training MUST-FAIL confounds legitimately produce identical
# degenerate predictions when BOTH fully fail (retrieval 0.000 at extreme-low budget) -- that coincidence is
# expected, NOT an arm-implementation bug (their code paths are entirely distinct). All OTHER arm pairs must
# differ. Rationale per feedback: confound-confound collision at the floor is not a bit-identical-arm defect.
ARMS_DIFFER_EXEMPT = frozenset([frozenset(("one_nn_proximity", "fresh_net_subsample"))])


def _arms_differ_ok(digests: Dict[str, str]) -> bool:
    """True iff every NON-exempt arm pair has a distinct held-out prediction digest (META_RULE_AF)."""
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if frozenset((a, b)) in ARMS_DIFFER_EXEMPT:
                continue
            if digests[a] == digests[b]:
                return False
    return True


def _difficulty_ok(agg: Dict) -> Tuple[bool, str]:
    checks = [
        (agg["heldout_initial"] >= DIFF_INITIAL_MIN, "net_learned_heldout_initial"),
        (agg["no_replay"] <= DIFF_NOREPLAY_MAX, "no_replay_forgets_heldout"),
        (agg["replay_all"] >= DIFF_CEILING_MIN, "replay_all_protects_ceiling"),
        (agg["one_nn_proximity"] <= DIFF_CONFOUND_MAX, "one_nn_fails_proves_independence"),
        (agg["fresh_net_subsample"] <= DIFF_CONFOUND_MAX, "fresh_net_fails_proves_independence"),
    ]
    fails = [name for ok, name in checks if not ok]
    return (len(fails) == 0), ("OK" if not fails else "FAILS:" + ",".join(fails))


def run() -> Dict:
    per_unit = []
    for s in SEEDS:
        per_unit.extend(_run_seed(s))

    points = []
    arms_differ = True
    for elig in BUDGET_GRID:
        units = [u for u in per_unit if u["elig_per_class"] == elig]

        def _mean(key):
            return float(np.mean([u[key] for u in units]))

        agg = {k: round(_mean(k), 4) for k in (
            "no_replay", "subsample_replay", "equal_compute_struct", "equal_compute_random", "replay_all",
            "one_nn_proximity", "fresh_net_subsample", "heldout_initial",
            "genuine_effect", "genuine_effect_random", "raw_effect", "struct_contribution", "filler_contribution")}
        diff_ok, diff_msg = _difficulty_ok(agg)
        for u in units:
            if not _arms_differ_ok(u["arm_digests"]):
                arms_differ = False
        points.append({
            "elig_per_class": elig, "budget_frac": round(elig / OLD_EXEMPLARS, 4),
            "n_replayed": units[0]["n_replayed"], "n_never_replayed": units[0]["n_never_replayed"],
            "n_seeds": len(units), "agg": agg, "difficulty_ok": diff_ok, "difficulty_msg": diff_msg})

    return {"points": points, "per_unit": per_unit, "n_units": len(per_unit),
            "expected_n_units": EXPECTED_N_UNITS, "arms_differ": arms_differ, "chance": round(CHANCE, 5)}


def _classify_shape(points: List[Dict]) -> Dict:
    """Classify the equal-compute-corrected genuine-effect vs budget curve. Descriptors are reported raw."""
    pts = sorted(points, key=lambda p: p["budget_frac"])
    g = [p["agg"]["genuine_effect"] for p in pts]
    bf = [p["budget_frac"] for p in pts]
    g_lo, g_hi = g[0], g[-1]
    b_lo, b_hi = bf[0], bf[-1]
    g_max = max(g)
    linear_ratio = (b_lo / b_hi) if b_hi > 0 else float("nan")
    eff_ratio = (g_lo / g_hi) if g_hi > 1e-6 else float("nan")
    if g_max < GENUINE_MARGINAL_MAX:
        label = "FLAT_MARGINAL"
    elif g_hi <= GENUINE_TOP_MIN:
        label = "FLAT_MARGINAL"
    elif (not np.isnan(eff_ratio)) and eff_ratio >= SUBLINEAR_FACTOR * linear_ratio:
        label = "SUB_LINEAR_EFFICIENT"
    elif (not np.isnan(eff_ratio)) and eff_ratio <= LINEAR_FACTOR * linear_ratio:
        label = "LINEAR_MUST_REHEARSE"
    else:
        label = "INTERMEDIATE"
    return {"label": label, "genuine_lo": round(g_lo, 4), "genuine_hi": round(g_hi, 4),
            "genuine_max": round(g_max, 4), "budget_lo": b_lo, "budget_hi": b_hi,
            "eff_ratio": (None if np.isnan(eff_ratio) else round(eff_ratio, 3)),
            "linear_ratio": (None if np.isnan(linear_ratio) else round(linear_ratio, 3))}


def _fmt_curve(points: List[Dict]) -> str:
    segs = []
    for pt in sorted(points, key=lambda p: p["budget_frac"]):
        a = pt["agg"]
        segs.append("b=%.3f(n_rep=%d,n_held=%d)[no=%.3f sub=%.3f fStr=%.3f fRnd=%.3f GEN=%.3f(rnd=%.3f) "
                    "all=%.3f 1nn=%.3f fresh=%.3f diff=%s]"
                    % (pt["budget_frac"], pt["n_replayed"], pt["n_never_replayed"], a["no_replay"],
                       a["subsample_replay"], a["equal_compute_struct"], a["equal_compute_random"],
                       a["genuine_effect"], a["genuine_effect_random"], a["replay_all"],
                       a["one_nn_proximity"], a["fresh_net_subsample"], "Y" if pt["difficulty_ok"] else "N"))
    return " ".join(segs)


def verdict(r: Dict) -> Tuple[str, str]:
    points = r["points"]
    curve = _fmt_curve(points)
    shape = _classify_shape(points)
    anchor = next((pt for pt in points if pt["elig_per_class"] == ANCHOR_ELIG), None)
    confounds_ok = all(pt["agg"]["one_nn_proximity"] <= DIFF_CONFOUND_MAX
                       and pt["agg"]["fresh_net_subsample"] <= DIFF_CONFOUND_MAX for pt in points)
    all_diff_ok = all(pt["difficulty_ok"] for pt in points)
    s = ("EQUAL-COMPUTE-CORRECTED never-replayed protection vs REPLAY BUDGET (chance=%.4f) | shape=%s "
         "genuine[lo=%.3f hi=%.3f max=%.3f] eff_ratio=%s linear_ratio=%s | curve: %s | confounds_ok=%s "
         "arms_differ=%s units=%d/%d"
         % (r["chance"], shape["label"], shape["genuine_lo"], shape["genuine_hi"], shape["genuine_max"],
            str(shape["eff_ratio"]), str(shape["linear_ratio"]), curve, confounds_ok, r["arms_differ"],
            r["n_units"], r["expected_n_units"]))

    if r["n_units"] != r["expected_n_units"]:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d. %s"
                % (r["n_units"], r["expected_n_units"], s))
    if not r["arms_differ"]:
        return ("HARD_FAIL", "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF: " + s)
    if not confounds_ok:
        return ("MIDDLE_BAND", "MIDDLE_BAND_INDEPENDENCE_BROKEN: a confound (1-NN / fresh-net) recovered "
                "held-out content above %.2f at some budget -- content NOT independent there; the curve is "
                "uninterpretable as distributed consolidation. " % DIFF_CONFOUND_MAX + s)
    if anchor is None or not anchor["difficulty_ok"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND_REGIME_INCONCLUSIVE: anchor-budget difficulty gate off (%s) -- "
                "cannot characterize until baselines in band. " % (anchor["difficulty_msg"] if anchor else "no-anchor") + s)
    if not all_diff_ok:
        off = [pt["budget_frac"] for pt in points if not pt["difficulty_ok"]]
        return ("MIDDLE_BAND", "MIDDLE_BAND_PARTIAL_REGIME: difficulty gate off at budgets %s (curve valid at "
                "anchor + others; partial coverage). " % off + s)

    read = {
        "SUB_LINEAR_EFFICIENT": ("BUDGET-EFFICIENT: a small replay budget protects a disproportionately large "
                                 "never-replayed set (sub-linear) -- distributed consolidation is USABLE as a "
                                 "continual-ingestion foundation (small rehearsal, large protection)."),
        "LINEAR_MUST_REHEARSE": ("NOT BUDGET-EFFICIENT: equal-compute-corrected protection tracks budget ~"
                                 "linearly -- you must rehearse most of the corpus to protect it; does NOT "
                                 "scale to textbook-after-textbook."),
        "FLAT_MARGINAL": ("MARGINAL: the equal-compute-corrected effect is small and roughly budget-"
                          "independent -- distributed consolidation gives a fixed modest protection, not a "
                          "budget-scalable foundation."),
        "INTERMEDIATE": ("INTERMEDIATE: neither cleanly sub-linear nor linear -- see the raw genuine-effect "
                         "curve; partial budget-efficiency."),
    }[shape["label"]]
    return ("CHARACTERIZATION", "CHARACTERIZATION_%s: %s CLAIM-VET-pending; NOT self-declared chain-grade. %s"
            % (shape["label"], read, s))


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
    """Exercise the REAL code path (RegNet + filler + confounds + run()) at the smoke grid, 1 seed.

    Positive control (Gate D): at ELIG=3 (parent regime) subsample held-out must reproduce the parent MEASURED
    0.247 within tolerance -- identical regime, so a large deviation = invocation/regime drift. Also asserts
    arms differ, net learned held-out initially, and the difficulty gate is ON at the anchor budget (so the
    smoke FIRES the discriminator, not just runs).
    """
    global SEEDS, BUDGET_GRID
    _s, _b = SEEDS, BUDGET_GRID
    SEEDS = [7]
    if ANCHOR_ELIG not in BUDGET_GRID:
        BUDGET_GRID = sorted(set(BUDGET_GRID + [ANCHOR_ELIG]))
    try:
        r = run()
        assert r["arms_differ"], "selftest: the 6 arms must produce differing held-out predictions per unit"
        anchor = next(pt for pt in r["points"] if pt["elig_per_class"] == ANCHOR_ELIG)
        a = anchor["agg"]
        assert a["heldout_initial"] >= 0.5, \
            "selftest: net did not learn independent held-out targets initially (init=%.3f)" % a["heldout_initial"]
        dev = abs(a["subsample_replay"] - PARENT_ANCHOR_SUBSAMPLE)
        assert dev <= PARENT_ANCHOR_TOL, \
            ("selftest POSITIVE-CONTROL (Gate D): ELIG=%d subsample held-out %.3f deviates from parent MEASURED "
             "%.3f by %.3f > tol %.3f -- regime/invocation drift" %
             (ANCHOR_ELIG, a["subsample_replay"], PARENT_ANCHOR_SUBSAMPLE, dev, PARENT_ANCHOR_TOL))
        # discriminator-fires: at the anchor budget the difficulty gate must be ON (baselines in band).
        assert anchor["difficulty_ok"], \
            "selftest: anchor-budget difficulty gate OFF (%s) -- smoke does not fire the discriminator" % anchor["difficulty_msg"]
        # confounds must fail (independence) at every smoke budget.
        for pt in r["points"]:
            assert pt["agg"]["one_nn_proximity"] <= DIFF_CONFOUND_MAX and pt["agg"]["fresh_net_subsample"] <= DIFF_CONFOUND_MAX, \
                "selftest: a confound recovered held-out at budget %.3f -- content not independent" % pt["budget_frac"]
        shape = _classify_shape(r["points"])
        print("[selftest] PASS real-code-path: anchor_sub=%.3f (parent %.3f, dev %.3f) shape=%s | curve %s"
              % (a["subsample_replay"], PARENT_ANCHOR_SUBSAMPLE, dev, shape["label"], _fmt_curve(r["points"])),
              flush=True)
    finally:
        SEEDS, BUDGET_GRID = _s, _b


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    print("[config] anchor=%s mode=%s N=%d D_T=%d H=%d old_items=%d SHARED_FRAC=%.2f blocks=%d E_OLD=%d "
          "E_NEW=%d BUDGET_GRID=%s seeds=%s chance=%.4f expected_units=%d"
          % (ANCHOR_NAME, RUN_MODE, N, D_T, H, OLD_ITEMS, SHARED_FRAC, K_INTERFERE, E_OLD, E_NEW,
             BUDGET_GRID, SEEDS, CHANCE, EXPECTED_N_UNITS), flush=True)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)

    shape = _classify_shape(r["points"])
    anchor = next((pt for pt in r["points"] if pt["elig_per_class"] == ANCHOR_ELIG), None)
    anchor_sub = anchor["agg"]["subsample_replay"] if anchor else float("nan")
    anchor_dev = abs(anchor_sub - PARENT_ANCHOR_SUBSAMPLE) if anchor else float("nan")
    confounds_max = max(max(pt["agg"]["one_nn_proximity"], pt["agg"]["fresh_net_subsample"]) for pt in r["points"])
    gate_claims = [
        record_gate("cardinality", r["n_units"], EXPECTED_N_UNITS, ">=",
                    "all budget x seed units completed (META_RULE_H)"),
        record_gate("arms_differ", 1 if r["arms_differ"] else 0, 1, ">=",
                    "the 6 arms produce differing held-out predictions (META_RULE_AF)"),
        record_gate("anchor_positive_control_dev", anchor_dev, PARENT_ANCHOR_TOL, "<=",
                    "ELIG=3 subsample held-out reproduces parent MEASURED 0.247 (Gate D positive control)"),
        record_gate("confounds_independence_max", confounds_max, DIFF_CONFOUND_MAX, "<=",
                    "both confounds fail across ALL budgets -> held-out content independent (difficulty ON)"),
        record_gate("genuine_effect_max", shape["genuine_max"], GENUINE_MARGINAL_MAX, ">=",
                    "peak equal-compute-corrected genuine effect over budget (descriptor, not pass/fail)"),
    ]
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE,
               "n_units": r["n_units"], "expected_n_units": EXPECTED_N_UNITS, "arms_differ": r["arms_differ"],
               "chance": r["chance"], "shape": shape, "points": r["points"], "per_unit": r["per_unit"],
               "anchor_positive_control": {"elig_per_class": ANCHOR_ELIG, "subsample_heldout": anchor_sub,
                                           "parent_measured": PARENT_ANCHOR_SUBSAMPLE, "deviation": anchor_dev,
                                           "tolerance": PARENT_ANCHOR_TOL},
               "config": {"N": N, "D_T": D_T, "H": H, "OLD_CLASSES": OLD_CLASSES, "OLD_EXEMPLARS": OLD_EXEMPLARS,
                          "K_INTERFERE": K_INTERFERE, "NEW_CPB": NEW_CPB, "NEW_EXEMPLARS": NEW_EXEMPLARS,
                          "E_OLD": E_OLD, "E_NEW": E_NEW, "LR": LR, "SHARED_FRAC": SHARED_FRAC,
                          "BUDGET_GRID": BUDGET_GRID, "ANCHOR_ELIG": ANCHOR_ELIG, "seeds": SEEDS},
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
