"""CHEM_BIND_READOUT_INTEGRATION (v1): THE synthetic->real integration proof. Does the substrate's LEARNED
SYMMETRIC BIND -- the frontier's symmetric-discovery arm LEARN_SYM (shared per-symbol code + ELEMENTWISE-PRODUCT
composition = swap-symmetric; proven on synthetic PARITY at 0.98 vs additive 0.38, commit 59056b6d4) -- READ OUT the
REAL generated chem-pair mixing-hazard NON-ADDITIVE conjunction on HELD-OUT pairs, BEATING (a) a matched-capacity
ADDITIVE model and (b) a fair FREQUENCY floor? First connection of the reasoning MECHANISM x the real FOUNDATION data.
Glass-box CPU, NO LLM at measurement time.

WHY (inlined; no re-hunt): the foundation generated a real, adversarially-vetted, genuinely-non-additive SYMMETRIC
conjunction -- chemical MIXING hazard (hazard(A,B)=hazard(B,A); SDS incompatibility). The generator cell
(exp_generated_conjunction_nonadditive_chem_v1, commit a6d93fbae) MEASURED (on disk, data/exp_.../metrics.json):
  non-additivity(SEEN class-pair) = int_seen 0.71121 - add_seen 0.44845 = 0.26275   MEASURED (CONFIRMED strong)
  additive-synth control non-additivity = 0.02793                                    MEASURED (gate valid)
  shuffle control non-additivity = 0.09065 ; joint_mi 1.718 best_single 1.002 ratio 0.583 ; oracle 1.0 ; truth 0.833
The generator's REFUTE was PURELY a truth-rate technicality (0.833 < its 0.85 threshold = ~16% adversarial-vet label
noise); the conjunction itself is strongly non-additive. That 16% noise makes THIS a REAL-DATA ROBUSTNESS test -- we do
NOT treat noise as failure; the question is whether the symmetric-bind mechanism reads the conjunction THROUGH the noise.

THE MECHANISM x DATA question (frontier-analog): the frontier's LEARN_SYM discovered SYMMETRIC non-additive PARITY on
NOVEL combos because a SHARED per-symbol code + PRODUCT composition GENERALIZES (a lookup table cannot). Chem hazard is
symmetric + non-additive -> LEARN_SYM is the PREDICTED-CORRECT inductive bias; an ADDITIVE (sum) model provably loses
the interaction. A lookup/MEMORIZE arm captures the SEEN class-pair by rote but collapses to additive on a NOVEL
class-pair (the generator MEASURED int_novel == add_novel == 0.29238 -- identical -- confirming a table cannot
generalize the conjunction). So the load-bearing claim is: LEARN_SYM (learned per-CLASS code + product) beats the
ADDITIVE arm at MATCHED code capacity => the multiplicative BIND, not memorization, reads the conjunction.

TWO STRATA on HELD-OUT (never-in-train) pairs (entity-level split; both are genuinely novel pairs):
  SEEN class-pair stratum (class-combination present in train; the generator's non-additivity regime): PRIMARY. Here
    LEARN_SYM (shared code, product, ~NCLS*D params) vs LEARN_ADD (shared code, SUM, SAME params) isolates
    interaction-vs-additive at matched capacity. Beating ADDITIVE here = the mechanism reads the real conjunction.
  NOVEL class-pair stratum (class-combination NEVER in train): STRETCH. Does the learned product-code EXTRAPOLATE the
    conjunction to an unseen class-pair where a lookup provably cannot? Thin stratum (~7-10 entities/seed) -> reported
    with variance; a non-generalization here is HONEST (MIDDLE), not a refute of the primary.

ARMS: LEARN_SYM (shared code + elementwise PRODUCT = the substrate symmetric bind op; WINNER hypothesis) ; LEARN_ADD
  (shared code + SUM; matched-capacity additive contrast, should LOSE the interaction) ; ADD_LSTSQ (optimal closed-form
  per-class main-effects; STRONGEST classical additive baseline -- SYM must beat BOTH additive arms) ; LEARN_ROLE
  (role-keyed / asymmetric product; ALGEBRA-DISCRIMINATION contrast -- on a SYMMETRIC target role-keying only
  over-parameterizes and must NOT beat LEARN_SYM) ; HOMOPHILY (per-class marginal vote) ; MEMORIZE (class-pair
  conditional mode, additive backoff) ; POP ; ORACLE(ceiling) ; FREQ_NULL = max(HOMOPHILY, POP).
REGIMES: CLEAN(real) ; ARBITRARY (random hazard per unique class-pair -> memorizable on SEEN, unpredictable on NOVEL:
  must-fail on the NOVEL stratum) ; SHUFFLE (label permutation across entities -> all structure destroyed: must-fail on
  ALL held-out). LEAK guard: query indices disjoint from train + novel-marked class-pairs genuinely absent from train.

PRE-REGISTERED BANDS (fixed BEFORE running; anchors HYPOTHESIZED from the generator's measured seen/novel arm proxies):
  PRIMARY (SEEN stratum, CLEAN, multi-seed mean):
    LEARN_SYM_seen - max(LEARN_ADD_seen, ADD_LSTSQ_seen) >= 0.10   (product beats additive at matched capacity)
    AND LEARN_SYM_seen - FREQ_seen >= 0.10  AND  LEARN_SYM_seen - chance >= 0.15
  ALGEBRA DISCRIMINATION: LEARN_SYM_seen >= LEARN_ROLE_seen - 0.05 (symmetric not beaten by role-keyed on symm target)
  MUST-FAILS: SHUFFLE (LEARN_SYM_all - FREQ_all) <= 0.12  AND  ARBITRARY (LEARN_SYM_novel - FREQ_novel) <= 0.12 ; oracle=1.0 ; leak_ok
  STRETCH (NOVEL stratum): LEARN_SYM_novel - max(additive_novel) >= 0.08  -> suffix _NOVEL_GENERALIZES if it holds.
  HARD_PASS_TRANSFER: PRIMARY holds AND algebra AND must-fails AND oracle AND leak. (mechanism transfers synth->real:
    the learned symmetric bind reads the real non-additive conjunction on held-out pairs.)
  MIDDLE: primary partial (beats freq XOR additive; or margins short) OR (seen holds but novel does not -> that is the
    _NOVEL suffix logic, still HARD_PASS on primary; MIDDLE reserved for a short primary).
  REFUTE_NO_TRANSFER: LEARN_SYM_seen - max(additive_seen) <= 0.03 (the mechanism does NOT read the real conjunction even
    in-distribution -> the synthetic->real transfer FAILS -> drill-worthy honest negative). Trusted only if must-fails
    fire + oracle=1.0 (discriminator valid).

Compute architecture: (b) sequential-CPU with justification -- arena is 135 real pairs x NCLS=11 classes; per-seed work
is a handful of tiny (<=135 x 32) Adam fits (milliseconds); total wall < 60s over 10 seeds. GPU batching yields no
speedup on sub-millisecond matmuls. Storage strategy: no_storage / no_composition-chaining (single-hop readout).
Determinism: ALL RNG from FIXED integer seeds + stable sorted-unique class-pair ids; NO Python hash(), NO list(set())
ordering (PROT-023; queue_add static scan enforces). ASCII-only. No bare except; except SystemExit before except
Exception. Atomic tmp+os.replace metrics write. Default invocation (no flag) = FULL run to completion.
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.binding import bind as hd_bind  # noqa: E402  # REAL substrate bind. complex64 -> FHRR elementwise multiply
# (a.is_complex() -> a*b): THIS is the elementwise-product operation LEARN_SYM's Hadamard composition mirrors. The
# self-test exercises hd_bind on complex64 unit phasors (homomorphism) to prove the product-bind IS the substrate op.
# (Do NOT route the learned real-valued codes through hd_bind: real float32 -> HRR circular convolution, a DIFFERENT
# op; LEARN_SYM uses the elementwise product = the real analog of the FHRR bind, bit-identical to the frontier arm.)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "chem_bind_readout_integration_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "chem_pair_hazard_nonadditive_v1.json")

# ---- reactivity classes / hazard scale (from the vetted artifact schema) ----
CLASSES = [
    "inert_or_water", "weak_acid", "strong_acid", "strong_base", "ammonia_or_amine", "hypochlorite_bleach",
    "oxidizer", "reactive_metal", "sulfide_or_cyanide_salt", "organic_solvent_or_fuel", "reducing_agent",
]
CLASS_IDX = {c: i for i, c in enumerate(CLASSES)}
NCLS = len(CLASSES)
TARGET = "hazard"
TARGET_SCALE = ["none", "minor", "moderate", "high", "severe"]
TGT_IDX = {v: i for i, v in enumerate(TARGET_SCALE)}
L = len(TARGET_SCALE)  # 5 ordinal severity levels 0..4

# ---- arms ----
SYM = "LEARN_SYM"; ADD = "LEARN_ADD"; ROLE = "LEARN_ROLE"; ADDLS = "ADD_LSTSQ"
HOM = "HOMOPHILY"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [SYM, ADD, ROLE, ADDLS, HOM, MEMO, POP, ORC, FREQ]
ADDITIVE_ARMS = [ADD, ADDLS]

# ---- regimes (stable enumerated indices; NO hash()) ----
CLEAN = "CLEAN_REAL"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- learned-arm hyperparams (fixed) ----
EMB_D = 32
EPOCHS = 500
LR = 0.05
QUERY_FRAC = 0.40

# ---- pre-registered bands (fixed before running) ----
HP_SEEN_SYM_ADD = 0.10       # LEARN_SYM_seen - max(additive_seen)  (product beats additive at matched capacity)
HP_SEEN_SYM_FREQ = 0.10      # LEARN_SYM_seen - FREQ_seen
HP_SEEN_SYM_CHANCE = 0.15    # LEARN_SYM_seen - chance
HP_ALGEBRA_EPS = 0.05        # LEARN_SYM_seen >= LEARN_ROLE_seen - eps (role-keying does not beat symmetric)
HP_NOVEL_SYM_ADD = 0.08      # STRETCH: LEARN_SYM_novel - max(additive_novel)
MUSTFAIL_TOL = 0.12          # SHUFFLE (all) + ARBITRARY (novel) LEARN_SYM - FREQ gap ceiling
REFUTE_GAP = 0.03            # LEARN_SYM_seen - max(additive_seen) <= this => NO transfer (honest negative)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


# ===========================================================================
# LOAD (real vetted-true class-pairs; strict vetted_true == True)
# ===========================================================================

def load_cluster():
    with open(ARTIFACT, "r", encoding="utf-8") as f:
        p = json.load(f)
    rows = [r for r in p["rows"] if r.get("vetted_true", None) is True]  # STRICT: only adversarially-vetted-true
    X = np.zeros((len(rows), 2), dtype=np.int64)
    y = np.zeros(len(rows), dtype=np.int64)
    for i, r in enumerate(rows):
        a = CLASS_IDX[str(r["class_a"]).strip().lower()]
        b = CLASS_IDX[str(r["class_b"]).strip().lower()]
        X[i, 0], X[i, 1] = min(a, b), max(a, b)  # canonical unordered class-pair
        y[i] = TGT_IDX[str(r[TARGET]).strip().lower()]
    return p, X, y


def chance_of(y):
    c = np.bincount(y, minlength=L).astype(np.float64)
    return float(c.max() / max(1.0, c.sum()))


# ===========================================================================
# non-additivity diagnostic (reported, not gated; reproduces the generator's conjunction property)
# ===========================================================================

def mutual_info(a, b, base=2.0):
    n = len(a)
    if n == 0:
        return 0.0
    pa = defaultdict(float); pb = defaultdict(float); pab = defaultdict(float)
    inv = 1.0 / n
    for x, z in zip(np.asarray(a).tolist(), np.asarray(b).tolist()):
        pa[x] += inv; pb[z] += inv; pab[(x, z)] += inv
    mi = 0.0
    for (x, z), pxz in pab.items():
        mi += pxz * math.log(pxz / (pa[x] * pb[z]) + 1e-30, base)
    return max(0.0, mi)


def _pair_ids(X):
    uniq = sorted(set((int(X[i, 0]), int(X[i, 1])) for i in range(X.shape[0])))  # sorted-unique (NO hash())
    m = {t: i for i, t in enumerate(uniq)}
    return np.array([m[(int(X[i, 0]), int(X[i, 1]))] for i in range(X.shape[0])], dtype=np.int64)


def conjunction_property(X, y):
    mi_a = mutual_info(X[:, 0], y); mi_b = mutual_info(X[:, 1], y)
    joint = mutual_info(_pair_ids(X), y)
    best_single = max(mi_a, mi_b)
    ratio = (best_single / joint) if joint > 1e-9 else float("nan")
    return dict(best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4),
                dominance_ratio=(round(ratio, 4) if ratio == ratio else ratio))


# ===========================================================================
# LEARNED ARMS (plain SGD). shared-product = symmetric bind ; shared-sum = additive ; role-product = asymmetric.
# ===========================================================================

def _train_learned(Xtr, ytr, Xq, mode, seed):
    """mode: 'sym' (SHARED code + elementwise PRODUCT = swap-symmetric bind) | 'add' (SHARED code + SUM = additive) |
    'role' (ROLE-KEYED code + PRODUCT = asymmetric). K=2 constituents (canonical class-pair), CrossEntropy over L."""
    g = torch.Generator().manual_seed(seed * 7919 + {"sym": 3, "add": 2, "role": 1}[mode])
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    k = Xtr.shape[1]  # == 2
    product = (mode in ("sym", "role"))
    if mode == "role":
        center = 1.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(k, NCLS, EMB_D, generator=g))   # role-keyed table
    else:
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(NCLS, EMB_D, generator=g))       # SHARED table (no role)
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, L, generator=g))
    b = torch.nn.Parameter(torch.zeros(L))
    params = [emb, W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        if mode == "role":
            e = emb[torch.arange(k).unsqueeze(0), Xi]     # (n,k,D) role-keyed
        else:
            e = emb[Xi]                                   # (n,k,D) shared
        return e.prod(dim=1) if product else e.sum(dim=1)

    for _ in range(EPOCHS):
        opt.zero_grad()
        h = compose(Xt)
        mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        logits = ((h - mu) / sd) @ W + b
        loss = lossf(logits, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = compose(Xt); mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        logits_q = ((compose(Xu) - mu) / sd) @ W + b
        return torch.argmax(logits_q, 1).numpy().astype(np.int64)


# ===========================================================================
# CLASSICAL ARMS
# ===========================================================================

def _design(Xm):
    """Per-class COUNT design (n x NCLS+1): col 1+c = count of class c in the pair (0/1/2); col0 intercept."""
    D = np.zeros((Xm.shape[0], NCLS + 1), dtype=np.float64)
    D[:, 0] = 1.0
    for r in range(Xm.shape[0]):
        D[r, 1 + int(Xm[r, 0])] += 1.0
        D[r, 1 + int(Xm[r, 1])] += 1.0
    return D


def arm_add_lstsq(Xtr, ytr, Xq):
    """STRONGEST closed-form additive: least-squares of ordinal target on symmetric per-class contributions."""
    beta, _, _, _ = np.linalg.lstsq(_design(Xtr), ytr.astype(np.float64), rcond=None)
    return np.clip(np.round(_design(Xq) @ beta), 0, L - 1).astype(np.int64)


def arm_homophily(Xtr, ytr, Xq):
    per = [defaultdict(lambda: np.zeros(L)) for _ in range(2)]
    for r in range(Xtr.shape[0]):
        for i in range(2):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=L).astype(np.float64)
    preds = []
    for q in range(Xq.shape[0]):
        sc = np.zeros(L)
        for i in range(2):
            sc = sc + per[i].get(int(Xq[q, i]), np.zeros(L))
        preds.append(int(np.argmax(sc if sc.sum() > 0 else marg)))
    return np.array(preds, dtype=np.int64)


def arm_memorize(Xtr, ytr, Xq, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[(int(Xtr[r, 0]), int(Xtr[r, 1]))][int(ytr[r])] += 1
    preds = []
    for q in range(Xq.shape[0]):
        dd = combo.get((int(Xq[q, 0]), int(Xq[q, 1])))
        preds.append(max(dd.items(), key=lambda kv: kv[1])[0] if dd else pop_label)
    return np.array(preds, dtype=np.int64)


def acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


# ===========================================================================
# regimes + split
# ===========================================================================

def make_regime_target(X, y_real, regime, seed):
    n = X.shape[0]
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ARBITRARY:
        # random hazard per UNIQUE canonical class-pair (deterministic; stable sorted-unique ids -> NO hash()).
        rng = np.random.default_rng(seed * 100057 + REG_IDX[regime] * 131 + 17)
        uniq = sorted(set((int(X[i, 0]), int(X[i, 1])) for i in range(n)))
        lab = {t: int(rng.integers(0, L)) for t in uniq}
        y = np.array([lab[(int(X[i, 0]), int(X[i, 1]))] for i in range(n)], dtype=np.int64)
        return y, y.copy()
    if regime == SHUFFLE:
        rng = np.random.default_rng(seed * 100057 + REG_IDX[regime] * 131 + 17)
        return y_real[rng.permutation(n)].copy(), y_real.copy()
    raise ValueError(regime)


def split_query(X, seed):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100081 + 13)
    perm = rng.permutation(n)
    nq = max(1, int(round(QUERY_FRAC * n)))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_pairs = set((int(X[i, 0]), int(X[i, 1])) for i in tr)
    seen = np.array([(int(X[i, 0]), int(X[i, 1])) in train_pairs for i in q], dtype=bool)
    return q, tr, seen, train_pairs


def score(X, y_real, regime, seed):
    q, tr, seen, train_pairs = split_query(X, seed)
    y_used, y_oracle = make_regime_target(X, y_real, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=L)))

    preds = {
        SYM: _train_learned(Xtr, ytr, Xq, "sym", seed),
        ADD: _train_learned(Xtr, ytr, Xq, "add", seed),
        ROLE: _train_learned(Xtr, ytr, Xq, "role", seed),
        ADDLS: arm_add_lstsq(Xtr, ytr, Xq),
        HOM: arm_homophily(Xtr, ytr, Xq),
        MEMO: arm_memorize(Xtr, ytr, Xq, pop_label),
        POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
        ORC: y_oracle[q],
    }
    # LEAK guard: query rows disjoint from train rows + novel-marked pairs genuinely absent from train pair set.
    leak_ok = (len(set(q.tolist()) & set(tr.tolist())) == 0
               and all(((int(Xq[i, 0]), int(Xq[i, 1])) not in train_pairs) for i in range(len(q)) if not seen[i]))

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("seen", seen), ("novel", ~seen), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds[arm], m), 5) for arm in preds}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["n"] = int(m.sum())
        out[sname] = d
    # ARMS-MUST-DIFFER (META_RULE_AF): the learned + classical predictor arms must be mutually distinct.
    sigs = {arm: _sig(preds[arm]) for arm in (SYM, ADD, ROLE, ADDLS, HOM, MEMO)}
    return dict(strata=out, sigs=sigs, leak_ok=bool(leak_ok),
                n_seen=int(seen.sum()), n_novel=int((~seen).sum()))


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29, 31, 37, 41, 43, 47)):
    p, X, y = load_cluster()
    conj = conjunction_property(X, y)
    chance = chance_of(y)
    _log("FULL: n=%d classes=%d L=%d seeds=%d chance=%.4f conj_margin=%.3f ratio=%s"
         % (X.shape[0], NCLS, L, len(seeds), chance, conj["mi_margin"], _fmt(conj["dominance_ratio"])))

    per = {reg: [] for reg in REGIMES}
    t0 = time.perf_counter()
    for si, sd in enumerate(seeds):
        for reg in REGIMES:
            per[reg].append(score(X, y, reg, sd))
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def mean_stratum(reg, stratum, arm):
        vals = [ps["strata"][stratum][arm] for ps in per[reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    # ---- CLEAN aggregates ----
    def cl(stratum, arm):
        return mean_stratum(CLEAN, stratum, arm)

    sym_seen = cl("seen", SYM); add_seen = max(cl("seen", ADD), cl("seen", ADDLS)); freq_seen = cl("seen", FREQ)
    role_seen = cl("seen", ROLE); chance_seen = chance
    sym_novel = cl("novel", SYM); add_novel = max(cl("novel", ADD), cl("novel", ADDLS)); freq_novel = cl("novel", FREQ)
    sym_all = cl("all", SYM); freq_all = cl("all", FREQ)
    orc_all = cl("all", ORC)

    # ---- must-fail gaps ----
    shuf_gap = mean_stratum(SHUFFLE, "all", SYM) - mean_stratum(SHUFFLE, "all", FREQ)         # all stratum
    arb_gap = mean_stratum(ARBITRARY, "novel", SYM) - mean_stratum(ARBITRARY, "novel", FREQ)  # novel stratum
    leak_ok = all(ps["leak_ok"] for reg in REGIMES for ps in per[reg])

    # ---- gates ----
    seen_sym_add = sym_seen - add_seen
    seen_sym_freq = sym_seen - freq_seen
    seen_sym_chance = sym_seen - chance_seen
    novel_sym_add = sym_novel - add_novel

    primary = bool(seen_sym_add >= HP_SEEN_SYM_ADD and seen_sym_freq >= HP_SEEN_SYM_FREQ
                   and seen_sym_chance >= HP_SEEN_SYM_CHANCE)
    algebra_ok = bool(sym_seen >= role_seen - HP_ALGEBRA_EPS)
    mustfails_ok = bool(shuf_gap <= MUSTFAIL_TOL and arb_gap <= MUSTFAIL_TOL)
    oracle_ok = bool(orc_all >= 0.999)
    novel_generalizes = bool(novel_sym_add >= HP_NOVEL_SYM_ADD)
    refute = bool(seen_sym_add <= REFUTE_GAP and mustfails_ok and oracle_ok)

    if not oracle_ok:
        verdict = "INCONCLUSIVE_CEILING_MALFORMED"
    elif not mustfails_ok:
        verdict = "INCONCLUSIVE_MUSTFAIL_LEAK"
    elif refute:
        verdict = "REFUTE_NO_TRANSFER_SYNTH_TO_REAL"
    elif primary and algebra_ok:
        verdict = "HARD_PASS_TRANSFER_SYMMETRIC_BIND_READS_REAL_CONJUNCTION"
        if novel_generalizes:
            verdict += "_NOVEL_GENERALIZES"
    else:
        verdict = "MIDDLE_BAND"
        if not algebra_ok:
            verdict += "_ROLE_BEATS_SYM"

    msg = ("%s || n=%d chance=%.3f | SEEN(primary): SYM=%s ADD=%s(LADD=%s LS=%s) FREQ=%s ROLE=%s "
           "(SYM-ADD=%s>=%.2f SYM-FREQ=%s>=%.2f SYM-chance=%s>=%.2f algebra_ok=%s) | "
           "NOVEL(stretch): SYM=%s ADD=%s (SYM-ADD=%s>=%.2f gen=%s) [n_novel~%.1f] | "
           "CONJ margin=%.3f ratio=%s joint=%.3f | MUSTFAIL shuf_all=%s arb_novel=%s(<=%.2f) leak_ok=%s oracle=%s"
           % (verdict, X.shape[0], chance, _fmt(sym_seen), _fmt(add_seen), _fmt(cl("seen", ADD)), _fmt(cl("seen", ADDLS)),
              _fmt(freq_seen), _fmt(role_seen), _fmt(seen_sym_add), HP_SEEN_SYM_ADD, _fmt(seen_sym_freq),
              HP_SEEN_SYM_FREQ, _fmt(seen_sym_chance), HP_SEEN_SYM_CHANCE, algebra_ok,
              _fmt(sym_novel), _fmt(add_novel), _fmt(novel_sym_add), HP_NOVEL_SYM_ADD, novel_generalizes,
              float(np.mean([ps["n_novel"] for ps in per[CLEAN]])),
              conj["mi_margin"], _fmt(conj["dominance_ratio"]), conj["joint_mi"],
              _fmt(shuf_gap), _fmt(arb_gap), MUSTFAIL_TOL, leak_ok, _fmt(orc_all)))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="full",
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        n_entities=int(X.shape[0]), truth_rate=p.get("truth_rate"), chance=round(chance, 5),
        seeds=list(seeds), emb_d=EMB_D, epochs=EPOCHS, lr=LR, query_frac=QUERY_FRAC,
        conjunction=conj,
        clean=dict(sym_seen=round(sym_seen, 5), add_seen=round(add_seen, 5), ladd_seen=round(cl("seen", ADD), 5),
                   ls_seen=round(cl("seen", ADDLS), 5), freq_seen=round(freq_seen, 5), role_seen=round(role_seen, 5),
                   memo_seen=round(cl("seen", MEMO), 5), pop_seen=round(cl("seen", POP), 5),
                   sym_novel=round(sym_novel, 5), add_novel=round(add_novel, 5), freq_novel=round(freq_novel, 5),
                   role_novel=round(cl("novel", ROLE), 5), sym_all=round(sym_all, 5), freq_all=round(freq_all, 5),
                   oracle_all=round(orc_all, 5)),
        gaps=dict(seen_sym_add=round(seen_sym_add, 5), seen_sym_freq=round(seen_sym_freq, 5),
                  seen_sym_chance=round(seen_sym_chance, 5), novel_sym_add=round(novel_sym_add, 5),
                  seen_sym_role=round(sym_seen - role_seen, 5), shuf_gap=round(shuf_gap, 5), arb_gap=round(arb_gap, 5)),
        gates=dict(primary=primary, algebra_ok=algebra_ok, mustfails_ok=mustfails_ok, oracle_ok=oracle_ok,
                   novel_generalizes=novel_generalizes, refute=refute, leak_ok=leak_ok),
        bands=dict(HP_SEEN_SYM_ADD=HP_SEEN_SYM_ADD, HP_SEEN_SYM_FREQ=HP_SEEN_SYM_FREQ,
                   HP_SEEN_SYM_CHANCE=HP_SEEN_SYM_CHANCE, HP_ALGEBRA_EPS=HP_ALGEBRA_EPS,
                   HP_NOVEL_SYM_ADD=HP_NOVEL_SYM_ADD, MUSTFAIL_TOL=MUSTFAIL_TOL, REFUTE_GAP=REFUTE_GAP),
        per_seed_regime={reg: [dict(strata=per[reg][i]["strata"], leak_ok=per[reg][i]["leak_ok"],
                                    n_seen=per[reg][i]["n_seen"], n_novel=per[reg][i]["n_novel"])
                               for i in range(len(seeds))] for reg in REGIMES},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (real bind path + guard-vs-arena-floor + planted product-beats-sum arena + arms-differ)
# ===========================================================================

def _plant(n, seed, mode):
    """Planted class-pair arena. mode='interaction' -> symmetric pair-table (product should beat sum). mode='additive'
    -> y = clip(a[cA]+a[cB]) (sum should match/beat product). Both symmetric over the unordered pair."""
    rng = np.random.default_rng(seed)
    ncls = 8
    a = rng.integers(0, ncls, size=n); b = rng.integers(0, ncls, size=n)
    X = np.stack([np.minimum(a, b), np.maximum(a, b)], axis=1).astype(np.int64)
    if mode == "interaction":
        tab = rng.integers(0, L, size=(ncls, ncls)); tab = np.minimum(tab, tab.T)  # symmetric 2-way interaction
        y = np.array([tab[int(X[i, 0]), int(X[i, 1])] for i in range(n)], dtype=np.int64)
    else:
        w = rng.integers(0, 3, size=ncls)
        y = np.array([int(np.clip(w[int(X[i, 0])] + w[int(X[i, 1])], 0, L - 1)) for i in range(n)], dtype=np.int64)
    return X, y


def self_test():
    ok_all = True
    details = {}

    # (1) REAL substrate bind (complex64 FHRR = elementwise multiply): bind of FPE phasors reads out (i+j) mod m.
    # This proves the elementwise-PRODUCT operation LEARN_SYM composes with IS the substrate bind (the frontier arm).
    g = np.random.default_rng(31)
    m = g.integers(1, 9, size=64).astype(np.float64)
    jj = np.arange(9, dtype=np.float64)[:, None]
    Yc = torch.from_numpy(np.exp(1j * (2.0 * np.pi / 9.0) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Yc[torch.tensor([1, 2])], Yc[torch.tensor([2, 3])])  # REAL substrate bind
    homo_pred = torch.argmax((bound @ Yc.conj().T.contiguous()).real, 1).tolist()
    homo_ok = homo_pred == [3 % 9, 5 % 9]
    details["fhrr_bind_homomorphism_ok"] = homo_ok

    # (2) elementwise product (LEARN_SYM composition) == real part of hd_bind on aligned complex phasors.
    va = torch.tensor([[2.0, -1.0, 0.5, 3.0]]); vb = torch.tensor([[-1.0, 2.0, 4.0, -0.5]])
    prod = (va * vb)
    cbind = hd_bind(va.to(torch.complex64), vb.to(torch.complex64)).real
    prod_is_bind = bool(torch.allclose(prod, cbind, atol=1e-5))
    details["hadamard_equals_complex_bind_real"] = prod_is_bind

    # (3) INTERACTION arena: SHARED-PRODUCT (sym) beats SHARED-SUM (add) on a genuine 2-way symmetric interaction,
    #     on the SEEN class-pair stratum. This is the discriminator the real cell tests -- it must FIRE at plant scale.
    Xi, yi = _plant(600, 7, "interaction")
    ri = [score(Xi, yi, CLEAN, sd) for sd in (7, 13, 17)]
    sym_seen_i = float(np.mean([r["strata"]["seen"][SYM] for r in ri]))
    add_seen_i = float(np.mean([max(r["strata"]["seen"][ADD], r["strata"]["seen"][ADDLS]) for r in ri]))
    role_seen_i = float(np.mean([r["strata"]["seen"][ROLE] for r in ri]))
    freq_seen_i = float(np.mean([r["strata"]["seen"][FREQ] for r in ri]))
    pop_seen_i = float(np.mean([r["strata"]["seen"][POP] for r in ri]))
    orc_i = float(np.mean([r["strata"]["all"][ORC] for r in ri]))
    n_seen_i = float(np.mean([r["n_seen"] for r in ri]))
    conj_i = conjunction_property(Xi, yi)
    details.update(dict(int_sym_seen=round(sym_seen_i, 4), int_add_seen=round(add_seen_i, 4),
                        int_role_seen=round(role_seen_i, 4), int_freq_seen=round(freq_seen_i, 4),
                        int_pop_seen=round(pop_seen_i, 4), int_oracle=round(orc_i, 4), int_n_seen=n_seen_i,
                        int_mi_margin=conj_i["mi_margin"]))

    # (4) ADDITIVE arena: SHARED-SUM (add) is the correct bias; the product arm must NOT massively beat it (guards
    #     against a spurious 'product always wins' artifact). Reported; the seen gap should be small/neg.
    Xa, ya = _plant(600, 11, "additive")
    ra = [score(Xa, ya, CLEAN, sd) for sd in (7, 13, 17)]
    add_gap_a = float(np.mean([r["strata"]["seen"][SYM] - max(r["strata"]["seen"][ADD], r["strata"]["seen"][ADDLS])
                               for r in ra]))
    details["additive_arena_sym_minus_add_seen"] = round(add_gap_a, 4)

    # (5) SHUFFLE must-fail on the interaction arena: product cannot beat freq when structure is destroyed.
    rsh = [score(Xi, yi, SHUFFLE, sd) for sd in (7, 13, 17)]
    shuf_gap_i = float(np.mean([r["strata"]["all"][SYM] - r["strata"]["all"][FREQ] for r in rsh]))
    details["shuffle_sym_minus_freq_all"] = round(shuf_gap_i, 4)

    # (6) ARMS-MUST-DIFFER (META_RULE_AF): witness on the REAL non-saturated data (also EXERCISES THE REAL CODE PATH:
    #     load_cluster + full score() over the actual artifact) -- on the solved plant, SYM=ROLE=MEMO legitimately
    #     coincide at gold (saturation), so the plant is the wrong witness. Real chem data (16% noise) spreads all 6.
    #     + guard-vs-arena-floor (FREQ/POP is a REAL floor, not degenerate 0).
    arms_differ = False; real_arms_sig_count = -1; real_path_ok = False
    try:
        _p, Xr, yr = load_cluster()
        scr = score(Xr, yr, CLEAN, 7)
        digs = scr["sigs"]
        real_arms_sig_count = len(set(digs.values()))
        arms_differ = real_arms_sig_count == len(digs)
        real_path_ok = (Xr.shape[0] >= 100 and Xr.shape[1] == 2)
    except (FileNotFoundError, OSError, KeyError) as e:
        details["real_arms_differ_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    guard_floor_valid = bool(freq_seen_i >= pop_seen_i - 1e-9 and pop_seen_i > 0.05)  # freq >= pop > degenerate
    details["real_arms_differ_sig_count"] = real_arms_sig_count
    details["real_code_path_exercised"] = real_path_ok
    details["guard_floor_valid"] = guard_floor_valid

    # (7) determinism: same seed -> identical predictions (no PYTHONHASHSEED leakage in the real code path).
    d1 = score(Xi, yi, CLEAN, 5)["sigs"][SYM]; d2 = score(Xi, yi, CLEAN, 5)["sigs"][SYM]
    determinism_ok = (d1 == d2)
    details["determinism_ok"] = determinism_ok

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hadamard_equals_complex_bind": prod_is_bind,
        # discriminator FIRES at plant scale: shared-product beats shared/closed-form additive on the interaction arena
        "SYM_beats_ADD_on_interaction_seen": (sym_seen_i - add_seen_i) >= 0.12,
        "SYM_beats_FREQ_on_interaction_seen": (sym_seen_i - freq_seen_i) >= 0.10,
        "algebra_role_not_beating_sym": sym_seen_i >= role_seen_i - 0.05,
        # additive arena: product does NOT spuriously dominate the additive bias (small/neg seen gap)
        "product_not_spurious_on_additive": add_gap_a <= 0.10,
        # must-fail fires
        "shuffle_mustfail_fires": shuf_gap_i <= 0.12,
        # fairness / integrity
        "oracle_ceiling": orc_i >= 0.999,
        "guard_floor_valid": guard_floor_valid,
        "arms_differ_on_real_data": arms_differ,
        "real_code_path_exercised": real_path_ok,
        "determinism_ok": determinism_ok,
        "enough_seen": n_seen_i >= 8,
    }
    for kk, vv in checks.items():
        if not vv:
            ok_all = False
    out = dict(passed=ok_all, checks=checks, details=details)
    print("[SELFTEST] %s" % json.dumps(out, default=float), flush=True)
    return ok_all, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true", help="explicit full run (default when no flag given)")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        ok, _ = self_test()
        sys.exit(0 if ok else 1)
    if not os.path.exists(ARTIFACT):
        _log("ARTIFACT missing (%s)." % ARTIFACT)
        sys.exit(2)
    if args.smoke:
        m = run_measurement(seeds=(7, 13, 17))
        m["run_mode"] = "smoke"
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    # DEFAULT (no flag) = FULL run to completion (runner invokes `python -u <script>` with no args).
    m = run_measurement()
    _write_metrics(m)
    _log(m["verdict_msg"])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            crash = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(e).__name__, str(e)[:400]),
                         summary="CELL_CRASHED", elapsed_s=0.0, anchor_name=ANCHOR_NAME,
                         traceback=traceback.format_exc()[:4000], ts_iso=datetime.now(timezone.utc).isoformat())
            os.makedirs(OUT_DIR, exist_ok=True)
            tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(crash, f, indent=2)
            os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
        except Exception:
            pass
        raise
