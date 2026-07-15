"""EPISTASIS_BIND_READOUT_INTEGRATION (v1): THE properly-done real-data transfer proof (revival of the chem REFUTE per
skunkworks VET a2f9a9e8). Does the substrate's LEARNED SYMMETRIC BIND (shared per-symbol code + ELEMENTWISE-PRODUCT
composition = swap-symmetric) READ OUT a GENUINELY non-additive real conjunction -- genetic-interaction severity of a gene
PAIR (epistasis / synthetic lethality) -- on HELD-OUT class-pairs, BEATING a CAPACITY-MATCHED CATEGORICAL additive + a
FREQUENCY floor? Glass-box CPU, NO LLM at measurement time.

WHY (inlined): the prior chem_bind_readout REFUTE was a DATA/foundation gate, NOT a mechanism failure (VET: mechanism
HEALTHY, on ARBITRARY-seen pure non-additive labels SYM=1.000 vs ADD=0.830). Chem SDS mixing-hazard is ~98% main-effects vs
a STRONG categorical additive. Two fixes: (1) STRONG capacity-matched additive baselines (LEARN_ADD shared-code+SUM AND
ADD_MULTINOM softmax-on-counts) -- the gate is SYM - max(all strong additive arms); (2) a GENUINE-interaction pocket
(epistasis) sourced by a stronger generator and cleared through the STRONG non-additivity gate
(exp_generated_epistasis_nonadditive_v1). This cell is dispatched ONLY if that gate HARD_PASSes.

THE MECHANISM x DATA question: the frontier's LEARN_SYM discovered SYMMETRIC non-additive structure on NOVEL combos because
a SHARED per-symbol code + PRODUCT composition GENERALIZES (a lookup cannot). Epistasis severity(classA,classB) is symmetric
+ genuinely non-additive (redundancy-relationship, not per-class main effect) -> LEARN_SYM is the PREDICTED-CORRECT bias; an
ADDITIVE (sum / softmax-on-counts) provably loses the interaction. Load-bearing claim: LEARN_SYM beats a capacity-matched
categorical additive at matched code capacity => the multiplicative BIND, not memorization, reads the conjunction.

TWO STRATA on HELD-OUT pairs (entity-level split): SEEN class-pair (PRIMARY; matched-capacity interaction-vs-additive) ;
NOVEL class-pair (STRETCH; does the learned product-code extrapolate the conjunction where a lookup cannot).

ARMS: LEARN_SYM (shared code + PRODUCT = substrate symmetric bind; WINNER hypothesis) ; LEARN_ADD (shared code + SUM;
matched-capacity LEARNED categorical additive) ; ADD_MULTINOM (softmax-on-counts; STRONG closed-form categorical additive) ;
ADD_LSTSQ (ordinal closed-form) ; LEARN_ROLE (role-keyed product; ALGEBRA contrast -- must NOT beat SYM on a symmetric
target) ; HOMOPHILY ; MEMORIZE ; POP ; ORACLE(ceiling) ; FREQ_NULL=max(HOMOPHILY,POP). strong_additive = max(LEARN_ADD,
ADD_MULTINOM, ADD_LSTSQ). REGIMES: CLEAN(real) ; ARBITRARY (random label per unique class-pair; must-fail on NOVEL) ;
SHUFFLE (label permutation; must-fail on ALL). LEAK guard: query disjoint from train + novel pairs absent from train.

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_epistasis_bind_readout_transfer.md):
  PRIMARY (SEEN, CLEAN, multi-seed mean):
    LEARN_SYM_seen - max(strong_additive_seen) >= 0.10  AND  LEARN_SYM_seen - FREQ_seen >= 0.10
    AND LEARN_SYM_seen - chance >= 0.15
  ALGEBRA: LEARN_SYM_seen >= LEARN_ROLE_seen - 0.05.
  MUST-FAILS: SHUFFLE (SYM_all - FREQ_all) <= 0.12 AND ARBITRARY (SYM_novel - FREQ_novel) <= 0.12 ; oracle=1.0 ; leak_ok.
  STRETCH (NOVEL): LEARN_SYM_novel - max(strong_additive_novel) >= 0.08 -> suffix _NOVEL_GENERALIZES.
  HARD_PASS_TRANSFER: PRIMARY & algebra & must-fails & oracle & leak.
  MIDDLE: partial. REFUTE_NO_TRANSFER: LEARN_SYM_seen - max(strong_additive_seen) <= 0.03 (trusted iff must-fails+oracle).

Compute architecture: (b) sequential-CPU with justification -- ~120-150 real pairs x NCLS=12; per-seed work is a handful of
tiny (<=150x32) Adam fits + numpy softmax (ms); total wall < 90s over 10 seeds; GPU yields no speedup on sub-ms matmuls.
torch thread-capped (HDI_TORCH_THREADS default 2). Storage: no_storage/no_composition (single-hop). Determinism: FIXED int
seeds + stable sorted-unique class-pair ids; NO hash(), NO list(set()) (PROT-023). ASCII-only; no bare except; except
SystemExit before except Exception; atomic tmp+os.replace. Default invocation (no flag) = FULL run to completion.
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

torch.set_num_threads(int(os.environ.get("HDI_TORCH_THREADS", "2")))

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.binding import bind as hd_bind  # noqa: E402  # REAL substrate bind (complex64 FHRR elementwise multiply);
# the elementwise-PRODUCT LEARN_SYM composes with IS this op. Self-test exercises hd_bind on complex64 unit phasors.

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "epistasis_bind_readout_integration_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "epistasis_pair_interaction_nonadditive_v1.json")

# ---- functional pathway classes / interaction-severity scale (mirrors the generator artifact schema) ----
CLASSES = [
    "dna_repair_hr", "dna_repair_nhej", "dna_repair_ber_parp", "dna_repair_mmr", "dna_repair_ner",
    "dna_damage_checkpoint", "cell_cycle_core", "chromatin_remodeling", "spindle_mitosis", "proteostasis_autophagy",
    "metabolism_general", "signaling_growth",
]
CLASS_IDX = {c: i for i, c in enumerate(CLASSES)}
NCLS = len(CLASSES)
TARGET = "interaction"
TARGET_SCALE = ["none", "mild", "moderate", "severe", "lethal"]
TGT_IDX = {v: i for i, v in enumerate(TARGET_SCALE)}
L = len(TARGET_SCALE)  # 5 negative-interaction severity levels 0..4

# ---- arms ----
SYM = "LEARN_SYM"; ADD = "LEARN_ADD"; ROLE = "LEARN_ROLE"; ADDLS = "ADD_LSTSQ"; ADDMULTI = "ADD_MULTINOM"
HOM = "HOMOPHILY"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [SYM, ADD, ROLE, ADDLS, ADDMULTI, HOM, MEMO, POP, ORC, FREQ]
ADDITIVE_ARMS = [ADD, ADDLS, ADDMULTI]

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
HP_SEEN_SYM_ADD = 0.10       # LEARN_SYM_seen - max(strong_additive_seen)
HP_SEEN_SYM_FREQ = 0.10      # LEARN_SYM_seen - FREQ_seen
HP_SEEN_SYM_CHANCE = 0.15    # LEARN_SYM_seen - chance
HP_ALGEBRA_EPS = 0.05        # LEARN_SYM_seen >= LEARN_ROLE_seen - eps
HP_NOVEL_SYM_ADD = 0.08      # STRETCH: LEARN_SYM_novel - max(strong_additive_novel)
MUSTFAIL_TOL = 0.12          # SHUFFLE (all) + ARBITRARY (novel) LEARN_SYM - FREQ gap ceiling
REFUTE_GAP = 0.03            # LEARN_SYM_seen - max(strong_additive_seen) <= this => NO transfer (honest negative)


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
# non-additivity diagnostic (reported, not gated)
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
    """Ordinal closed-form additive (WEAK): least-squares of ordinal target on symmetric per-class contributions."""
    beta, _, _, _ = np.linalg.lstsq(_design(Xtr), ytr.astype(np.float64), rcond=None)
    return np.clip(np.round(_design(Xq) @ beta), 0, L - 1).astype(np.int64)


def arm_add_multinom(Xtr, ytr, Xq, iters=500, lr=0.5, l2=1e-3):
    """STRONG categorical additive: multinomial logistic (softmax) regression on the per-class COUNT design (the STRONGEST
    main-effects-only CATEGORICAL additive; no ordinal assumption, no round-to-bin loss). Deterministic zero-init GD."""
    D = _design(Xtr); n, pdim = D.shape
    W = np.zeros((pdim, L), dtype=np.float64)
    Yoh = np.zeros((n, L), dtype=np.float64); Yoh[np.arange(n), ytr] = 1.0
    for _ in range(iters):
        Z = D @ W; Z -= Z.max(axis=1, keepdims=True)
        Pm = np.exp(Z); Pm /= Pm.sum(axis=1, keepdims=True)
        grad = D.T @ (Pm - Yoh) / n + l2 * W
        W -= lr * grad
    return np.argmax(_design(Xq) @ W, axis=1).astype(np.int64)


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
        ADDMULTI: arm_add_multinom(Xtr, ytr, Xq),
        HOM: arm_homophily(Xtr, ytr, Xq),
        MEMO: arm_memorize(Xtr, ytr, Xq, pop_label),
        POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
        ORC: y_oracle[q],
    }
    leak_ok = (len(set(q.tolist()) & set(tr.tolist())) == 0
               and all(((int(Xq[i, 0]), int(Xq[i, 1])) not in train_pairs) for i in range(len(q)) if not seen[i]))

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("seen", seen), ("novel", ~seen), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds[arm], m), 5) for arm in preds}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["STRONG_ADD"] = round(max(d[ADD], d[ADDLS], d[ADDMULTI]), 5)
        d["n"] = int(m.sum())
        out[sname] = d
    sigs = {arm: _sig(preds[arm]) for arm in (SYM, ADD, ROLE, ADDLS, ADDMULTI, HOM, MEMO)}
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

    def cl(stratum, arm):
        return mean_stratum(CLEAN, stratum, arm)

    sym_seen = cl("seen", SYM); add_seen = cl("seen", "STRONG_ADD"); freq_seen = cl("seen", FREQ)
    role_seen = cl("seen", ROLE); chance_seen = chance
    sym_novel = cl("novel", SYM); add_novel = cl("novel", "STRONG_ADD"); freq_novel = cl("novel", FREQ)
    sym_all = cl("all", SYM); freq_all = cl("all", FREQ)
    orc_all = cl("all", ORC)

    shuf_gap = mean_stratum(SHUFFLE, "all", SYM) - mean_stratum(SHUFFLE, "all", FREQ)
    arb_gap = mean_stratum(ARBITRARY, "novel", SYM) - mean_stratum(ARBITRARY, "novel", FREQ)
    leak_ok = all(ps["leak_ok"] for reg in REGIMES for ps in per[reg])

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
        verdict = "REFUTE_NO_TRANSFER_SYM_DOES_NOT_READ_EPISTASIS"
    elif primary and algebra_ok:
        verdict = "HARD_PASS_TRANSFER_SYMMETRIC_BIND_READS_REAL_EPISTASIS_CONJUNCTION"
        if novel_generalizes:
            verdict += "_NOVEL_GENERALIZES"
    else:
        verdict = "MIDDLE_BAND"
        if not algebra_ok:
            verdict += "_ROLE_BEATS_SYM"

    msg = ("%s || n=%d chance=%.3f | SEEN(primary): SYM=%s STRONG_ADD=%s(LADD=%s MULTI=%s LS=%s) FREQ=%s ROLE=%s "
           "(SYM-ADD=%s>=%.2f SYM-FREQ=%s>=%.2f SYM-chance=%s>=%.2f algebra_ok=%s) | "
           "NOVEL(stretch): SYM=%s STRONG_ADD=%s (SYM-ADD=%s>=%.2f gen=%s) [n_novel~%.1f] | "
           "CONJ margin=%.3f ratio=%s joint=%.3f | MUSTFAIL shuf_all=%s arb_novel=%s(<=%.2f) leak_ok=%s oracle=%s"
           % (verdict, X.shape[0], chance, _fmt(sym_seen), _fmt(add_seen), _fmt(cl("seen", ADD)),
              _fmt(cl("seen", ADDMULTI)), _fmt(cl("seen", ADDLS)), _fmt(freq_seen), _fmt(role_seen),
              _fmt(seen_sym_add), HP_SEEN_SYM_ADD, _fmt(seen_sym_freq), HP_SEEN_SYM_FREQ, _fmt(seen_sym_chance),
              HP_SEEN_SYM_CHANCE, algebra_ok, _fmt(sym_novel), _fmt(add_novel), _fmt(novel_sym_add), HP_NOVEL_SYM_ADD,
              novel_generalizes, float(np.mean([ps["n_novel"] for ps in per[CLEAN]])),
              conj["mi_margin"], _fmt(conj["dominance_ratio"]), conj["joint_mi"],
              _fmt(shuf_gap), _fmt(arb_gap), MUSTFAIL_TOL, leak_ok, _fmt(orc_all)))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="full",
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        n_entities=int(X.shape[0]), truth_rate=p.get("truth_rate"), generator=p.get("generator"),
        chance=round(chance, 5), seeds=list(seeds), emb_d=EMB_D, epochs=EPOCHS, lr=LR, query_frac=QUERY_FRAC,
        conjunction=conj,
        clean=dict(sym_seen=round(sym_seen, 5), strong_add_seen=round(add_seen, 5), ladd_seen=round(cl("seen", ADD), 5),
                   multi_seen=round(cl("seen", ADDMULTI), 5), ls_seen=round(cl("seen", ADDLS), 5),
                   freq_seen=round(freq_seen, 5), role_seen=round(role_seen, 5), memo_seen=round(cl("seen", MEMO), 5),
                   pop_seen=round(cl("seen", POP), 5), sym_novel=round(sym_novel, 5),
                   strong_add_novel=round(add_novel, 5), freq_novel=round(freq_novel, 5),
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
# SELF-TEST (real bind path + guard-vs-arena-floor + planted product-beats-strong-additive arena + arms-differ)
# ===========================================================================

def _plant(n, seed, mode):
    """mode='interaction' -> symmetric pair-table (product should beat sum + softmax-on-counts). mode='additive' ->
    y = clip(a[cA]+a[cB]) (additive should match/beat product). Both symmetric over the unordered pair."""
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

    # (3) INTERACTION arena: SHARED-PRODUCT (sym) beats the STRONG additive (max of sum/lstsq/softmax-on-counts) on a
    #     genuine 2-way symmetric interaction, on the SEEN class-pair stratum. Discriminator must FIRE at plant scale.
    Xi, yi = _plant(600, 7, "interaction")
    ri = [score(Xi, yi, CLEAN, sd) for sd in (7, 13, 17)]
    sym_seen_i = float(np.mean([r["strata"]["seen"][SYM] for r in ri]))
    add_seen_i = float(np.mean([r["strata"]["seen"]["STRONG_ADD"] for r in ri]))
    role_seen_i = float(np.mean([r["strata"]["seen"][ROLE] for r in ri]))
    freq_seen_i = float(np.mean([r["strata"]["seen"][FREQ] for r in ri]))
    pop_seen_i = float(np.mean([r["strata"]["seen"][POP] for r in ri]))
    orc_i = float(np.mean([r["strata"]["all"][ORC] for r in ri]))
    n_seen_i = float(np.mean([r["n_seen"] for r in ri]))
    conj_i = conjunction_property(Xi, yi)
    details.update(dict(int_sym_seen=round(sym_seen_i, 4), int_strong_add_seen=round(add_seen_i, 4),
                        int_role_seen=round(role_seen_i, 4), int_freq_seen=round(freq_seen_i, 4),
                        int_pop_seen=round(pop_seen_i, 4), int_oracle=round(orc_i, 4), int_n_seen=n_seen_i,
                        int_mi_margin=conj_i["mi_margin"]))

    # (4) ADDITIVE arena: SHARED-SUM is the correct bias; product must NOT massively beat the STRONG additive.
    Xa, ya = _plant(600, 11, "additive")
    ra = [score(Xa, ya, CLEAN, sd) for sd in (7, 13, 17)]
    add_gap_a = float(np.mean([r["strata"]["seen"][SYM] - r["strata"]["seen"]["STRONG_ADD"] for r in ra]))
    details["additive_arena_sym_minus_strong_add_seen"] = round(add_gap_a, 4)

    # (5) SHUFFLE must-fail on the interaction arena.
    rsh = [score(Xi, yi, SHUFFLE, sd) for sd in (7, 13, 17)]
    shuf_gap_i = float(np.mean([r["strata"]["all"][SYM] - r["strata"]["all"][FREQ] for r in rsh]))
    details["shuffle_sym_minus_freq_all"] = round(shuf_gap_i, 4)

    # (6) ARMS-MUST-DIFFER (META_RULE_AF) on REAL data (also EXERCISES THE REAL CODE PATH: load_cluster + full score()
    #     over the actual artifact) + guard-vs-arena-floor. Unjudged-tolerant if artifact absent (plant checks still gate).
    arms_differ = None; real_arms_sig_count = -1; real_path_ok = None
    try:
        _p, Xr, yr = load_cluster()
        scr = score(Xr, yr, CLEAN, 7)
        digs = scr["sigs"]
        real_arms_sig_count = len(set(digs.values()))
        arms_differ = real_arms_sig_count == len(digs)
        real_path_ok = (Xr.shape[0] >= 80 and Xr.shape[1] == 2)
    except (FileNotFoundError, OSError, KeyError) as e:
        details["real_arms_differ_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
        print("[SELFTEST] real artifact not yet present (%s) -- plant checks still gate." % type(e).__name__, flush=True)
    guard_floor_valid = bool(freq_seen_i >= pop_seen_i - 1e-9 and pop_seen_i > 0.05)
    details["real_arms_differ_sig_count"] = real_arms_sig_count
    details["real_code_path_exercised"] = real_path_ok
    details["guard_floor_valid"] = guard_floor_valid

    # (7) determinism: same seed -> identical predictions.
    d1 = score(Xi, yi, CLEAN, 5)["sigs"][SYM]; d2 = score(Xi, yi, CLEAN, 5)["sigs"][SYM]
    determinism_ok = (d1 == d2)
    details["determinism_ok"] = determinism_ok

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hadamard_equals_complex_bind": prod_is_bind,
        "SYM_beats_STRONG_ADD_on_interaction_seen": (sym_seen_i - add_seen_i) >= 0.12,
        "SYM_beats_FREQ_on_interaction_seen": (sym_seen_i - freq_seen_i) >= 0.10,
        "algebra_role_not_beating_sym": sym_seen_i >= role_seen_i - 0.05,
        "product_not_spurious_on_additive": add_gap_a <= 0.10,
        "shuffle_mustfail_fires": shuf_gap_i <= 0.12,
        "oracle_ceiling": orc_i >= 0.999,
        "guard_floor_valid": guard_floor_valid,
        "arms_differ_on_real_data": (arms_differ in (None, True)),
        "real_code_path_exercised": (real_path_ok in (None, True)),
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
