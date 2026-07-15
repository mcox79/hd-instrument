"""GENERATED_CONJUNCTION_MONOTONE_FOODS (foundation-build: monotone code on a GENUINELY-conjunctive real cluster).

Builds on two prior results (inlined here so the file is self-contained):
  (1) exp_generated_conjunction_native_bind_animals_v1.py: a real 191-animal ordinal cluster showed MODULAR FPE codes
      FAIL to read out the ordinal target (novel 0.159, below chance) because modular bind WRAPS the monotone biology.
  (2) An inline follow-up proved a MONOTONE code fixes the ENCODING (0.159 -> 0.573 on clean novel, must-fails fire) BUT
      beat the frequency null by only +0.062, because that animal target is WEAKLY conjunctive (activity_level carried
      1.11 of 1.88 joint-MI bits = a single dominant driver). A diagnostic confirmed this is DATA-limited, not code-limited
      (a balanced all-4-constituent monotone target on the same entities -> monotone beats freq by +0.387).

So: the ENCODING is solved (monotone constructable code + additive compose + train-fit quantile-threshold readout). The
OPEN question this cell answers: does EXTERNALLY-GENERATED, REAL, vettable knowledge contain STRONG multi-constituent
conjunctions with NO single dominant driver -- and does the monotone code then BEAT the frequency/homophily null on NOVEL
constituent combinations? Glass-box, NO LLM at measurement time.

Cluster (real, vettable, addresses food-science coverage; chosen for GENUINELY INDEPENDENT axes with a balance target):
FOODS. Per food the external generator emits TYPICAL ordinal values on FOUR natural constituent scales AND a held-out
ordinal target -- all real food science, NO rule revealed to the generator:
  water_content         [very_dry,dry,moderate,moist,very_moist]              -> 0..4
  acidity               [very_acidic,acidic,neutral,slightly_alkaline,alkaline]-> 0..4
  preservative_content  [none,low,moderate,high,very_high]                    -> 0..4  (salt/sugar/curing)
  unsaturated_fat_content[very_low,low,moderate,high,very_high]               -> 0..4  (oxidation liability)
  TARGET perishability  [very_stable,stable,moderate,perishable,very_perishable] -> 0..4 (held out)

Real-world causality: a food spoils fast if it is high-water AND low-preservative AND (near-neutral OR high-unsaturated-
fat); honey (dry, high-sugar) lasts forever, fresh fish (moist, unpreserved, high unsaturated fat) perishes fast. These
axes vary INDEPENDENTLY across foods, so the target should need a COMBINATION with no single dominant driver. We MEASURE
this (we do NOT plant it) via a generation-acceptance gate on single-vs-joint MI.

Monotone readout (the substrate contribution): each constituent is ORIENTED by its TRAIN-set Spearman sign (so it is
positively associated with the target -- no test leakage, orientation learned on train only), thermometer/ramp-encoded,
and additively composed (NO modular wrap). Readout = TRAIN-fit quantile thresholds mapping the composed score to the
target bin. Two monotone arms: MONO_THERM (equal weight) and MONO_WEIGHT (learned NON-NEGATIVE per-constituent weights).

ARMS: MONO_THERM + MONO_WEIGHT (monotone constructable) ; MODULAR native FHRR bind (the v1 contrast that should FAIL on a
non-modular target) ; FREQ_NULL = max(HOMOPHILY_COND, POP) ; MEMORIZE ; POP ; ORACLE.
MUST-FAILS: ARBITRARY (random non-monotone table over the 4 constituents) + SHUFFLE (freq-preserving label permutation) --
neither may lift the monotone arms above freq (gap <= tol).
HEADLINE METRIC (NOVEL stratum, top-1 acc; chance=1/L=0.20; NOT tuned): MONO_WEIGHT_novel - FREQ_NULL_novel.

PRE-REGISTERED BANDS (fixed BEFORE running):
  Generation-acceptance / conjunction-present gate:
    truth_rate >= 0.85 (adversarial vet) AND
    best_single_mi / joint_mi <= 0.55 (no single constituent carries most of the joint MI) AND
    (joint_mi - best_single_mi) >= 0.30 bits (real conjunction margin).
  HARD_PASS (foundation GO): conjunction-present gate holds AND MONO_WEIGHT_novel - FREQ_NULL_novel >= 0.10 AND
    MONO beats MODULAR (mono_gap > modular_gap) AND both must-fails fire (gap <= 0.05) AND oracle ceiling ok.
  REFUTE (the most valuable negative): truth < 0.85 OR NOT conjunction-present (target single-driver/homophily-solvable)
    OR MONO_WEIGHT_novel - FREQ_NULL_novel <= 0.03. -> real generated knowledge does not (here) yield strong
    non-dominated conjunctions readable by monotone codes beyond frequency.
  MIDDLE_BAND: anything else (conjunction present but monotone modestly beats freq, or bands not clean).

This file is BOTH the build-time generator (--generate: external tool + adversarial vet, writes the vetted artifact) AND
the substrate measurement (--run / --self-test; NO LLM at measurement time; glass-box CPU, run to completion locally).
ASCII-only. No bare except; except SystemExit before except Exception.
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

from hdlab.binding import bind as hd_bind  # noqa: E402  # REAL substrate FHRR bind (complex64 elementwise mul)

ANCHOR_NAME = "generated_conjunction_monotone_foods_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "foods_ordinal_conjunction_v1.json")

SCALES = {
    "water_content": ["very_dry", "dry", "moderate", "moist", "very_moist"],
    "acidity": ["very_acidic", "acidic", "neutral", "slightly_alkaline", "alkaline"],
    "preservative_content": ["none", "low", "moderate", "high", "very_high"],
    "unsaturated_fat_content": ["very_low", "low", "moderate", "high", "very_high"],
}
CONSTITUENTS = list(SCALES.keys())
TARGET = "perishability"
TARGET_SCALE = ["very_stable", "stable", "moderate", "perishable", "very_perishable"]
L = 5  # ordinal levels per attribute (0..4)

# ---- regimes ----
CLEAN = "CLEAN_REAL"       # the real generated target
ARBITRARY = "ARBITRARY"    # target = fixed random non-monotone table over the 4 constituents (must-fail)
SHUFFLE = "SHUFFLE"        # real target permuted across entities (freq-preserving; must-fail)
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]

MONO_T = "MONO_THERM"
MONO_W = "MONO_WEIGHT"
MODUL = "MODULAR_BIND"     # v1 modular FHRR native bind (the contrast that should FAIL on a non-modular target)
MEMO = "MEMORIZE"
HOM = "HOMOPHILY_COND"
POP = "POP"
ORC = "ORACLE"

# ---- pre-registered bands (fixed before running) ----
HP_TRUTH = 0.85
CONJ_RATIO_CEIL = 0.55     # best_single_mi / joint_mi must be <= this
CONJ_MI_MARGIN = 0.30      # bits: joint_mi - best_single_mi must be >= this
HP_DISSOCIATION = 0.10     # MONO_WEIGHT_novel - FREQ_NULL_novel
MUSTFAIL_TOL = 0.05
REFUTE_TOL = 0.03


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


# ===========================================================================
# BUILD-TIME GENERATION (external tool; runs locally only, writes the vetted artifact).
# ===========================================================================

GEN_FOOD_BATCHES = [
    "fresh produce: leafy greens, root vegetables, berries, citrus fruits, tropical fruits, gourds",
    "animal proteins fresh and cured: fresh fish, shellfish, poultry, red meat, cured meats, canned fish",
    "dairy and eggs: fresh milk, soft cheese, aged hard cheese, yogurt, butter, eggs",
    "grains legumes nuts and dried goods: rice, wheat flour, dried beans, tree nuts, seeds, crackers, pasta",
    "preserved and shelf-stable pantry: honey, fruit jam, pickles, dried fruit, table sugar, salt, cooking oils, vinegar",
    "prepared bakery and misc: fresh bread, pastries, cooked leftovers, tofu, sauces, soups, deli salads",
]


def _gen_prompt(batch_desc, n):
    lines = []
    lines.append("You are a careful food scientist building a vetted knowledge base. List %d real, distinct, well-known "
                 "foods from this group: %s." % (n, batch_desc))
    lines.append("For EACH food, give its TYPICAL value on each of these ordinal scales (choose exactly one level):")
    for k, lv in SCALES.items():
        lines.append("  %s: one of %s" % (k, lv))
    lines.append("  %s: one of %s" % (TARGET, TARGET_SCALE))
    lines.append("perishability = how quickly the food spoils at room temperature when fresh/opened (very_stable lasts "
                 "for years, very_perishable spoils within a day).")
    lines.append("Base every value on established food science. Do NOT follow any formula; give the real typical value.")
    lines.append("Return ONLY a JSON array, each element: "
                 '{"name":..., "water_content":..., "acidity":..., "preservative_content":..., '
                 '"unsaturated_fat_content":..., "perishability":...}. No prose.')
    return "\n".join(lines)


def _extract_json_array(text):
    s = text.find("[")
    e = text.rfind("]")
    if s < 0 or e < 0 or e <= s:
        return []
    try:
        return json.loads(text[s:e + 1])
    except (ValueError, TypeError):
        return []


def _vet_prompt(rows):
    lines = ["You are an adversarial fact-checker. For each food record below, judge whether ALL FIVE attribute values "
             "are correct for that food (typical, fresh/as-commonly-stored). Answer strictly.",
             "Scales: water_content%s acidity%s preservative_content%s unsaturated_fat_content%s perishability%s"
             % (SCALES["water_content"], SCALES["acidity"], SCALES["preservative_content"],
                SCALES["unsaturated_fat_content"], TARGET_SCALE),
             "Return ONLY a JSON array of {\"name\":..., \"ok\":true/false}. A record is ok=false if ANY value is "
             "clearly wrong. Records:"]
    for r in rows:
        lines.append(json.dumps({k: r.get(k) for k in (["name"] + CONSTITUENTS + [TARGET])}))
    return "\n".join(lines)


def do_generate(n_per_batch=34):
    """Call the external generator + adversarial vetter; write the vetted artifact. Local build-time only."""
    import pathlib
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(_REPO) / ".env.local")
    from backend.llm import anthropic_client

    valset = {k: set(v) for k, v in SCALES.items()}
    valset[TARGET] = set(TARGET_SCALE)
    seen = {}
    total_cost = 0.0
    for bi, bd in enumerate(GEN_FOOD_BATCHES):
        _log("generate batch %d/%d: %s" % (bi + 1, len(GEN_FOOD_BATCHES), bd))
        resp = anthropic_client.chat(_gen_prompt(bd, n_per_batch), max_tokens=4096, temperature=0.4)
        total_cost += resp.cost_usd
        arr = _extract_json_array(resp.text)
        kept = 0
        for r in arr:
            nm = str(r.get("name", "")).strip().lower()
            if not nm or nm in seen:
                continue
            ok = all(str(r.get(k, "")).strip().lower() in valset[k] for k in (CONSTITUENTS + [TARGET]))
            if not ok:
                continue
            seen[nm] = {k: str(r.get(k)).strip().lower() for k in (CONSTITUENTS + [TARGET])}
            kept += 1
        _log("  kept %d (running total %d) cost=$%.4f" % (kept, len(seen), resp.cost_usd))
    rows = [dict(name=nm, **v) for nm, v in seen.items()]

    # ---- adversarial vet (in batches of 40) ----
    truth_flags = {}
    for s in range(0, len(rows), 40):
        chunk = rows[s:s + 40]
        vresp = anthropic_client.chat(_vet_prompt(chunk), max_tokens=4096, temperature=0.0)
        total_cost += vresp.cost_usd
        for j in _extract_json_array(vresp.text):
            nm = str(j.get("name", "")).strip().lower()
            truth_flags[nm] = bool(j.get("ok", False))
    n_judged = sum(1 for r in rows if r["name"] in truth_flags)
    n_true = sum(1 for r in rows if truth_flags.get(r["name"], False))
    truth_rate = (n_true / n_judged) if n_judged else float("nan")
    for r in rows:
        r["vetted_true"] = truth_flags.get(r["name"], None)

    os.makedirs(os.path.dirname(ARTIFACT), exist_ok=True)
    payload = dict(anchor=ANCHOR_NAME, generator="claude-haiku-4-5", ts_iso=datetime.now(timezone.utc).isoformat(),
                   scales=SCALES, target=TARGET, target_scale=TARGET_SCALE, L=L, gen_cost_usd=round(total_cost, 4),
                   n_entities=len(rows), n_judged=n_judged, n_true=n_true, truth_rate=truth_rate, rows=rows)
    tmp = ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, ARTIFACT)
    _log("ARTIFACT written: %s (n=%d truth_rate=%s cost=$%.4f)"
         % (ARTIFACT, len(rows), _fmt(truth_rate), total_cost))
    return payload


# ===========================================================================
# MEASUREMENT (glass-box; NO LLM). Reads the artifact -> ordinal matrices -> arms -> verdict.
# ===========================================================================

def load_cluster():
    with open(ARTIFACT, "r", encoding="utf-8") as f:
        p = json.load(f)
    rows = p["rows"]
    idx = {k: {v: i for i, v in enumerate(SCALES[k])} for k in CONSTITUENTS}
    tidx = {v: i for i, v in enumerate(TARGET_SCALE)}
    X = np.array([[idx[k][r[k]] for k in CONSTITUENTS] for r in rows], dtype=np.int64)  # (n, 4)
    y = np.array([tidx[r[TARGET]] for r in rows], dtype=np.int64)                       # (n,)
    return p, X, y


def mutual_info(a, b, base=2.0):
    """Discrete MI(a;b) in bits. a,b int arrays."""
    n = len(a)
    if n == 0:
        return 0.0
    pa = defaultdict(float); pb = defaultdict(float); pab = defaultdict(float)
    for x, z in zip(a, b):
        pa[x] += 1.0 / n; pb[z] += 1.0 / n; pab[(x, z)] += 1.0 / n
    mi = 0.0
    for (x, z), pxz in pab.items():
        mi += pxz * math.log(pxz / (pa[x] * pb[z]) + 1e-30, base)
    return max(0.0, mi)


def conjunction_property(X, y):
    """single-relation MI(y;X_i) vs joint MI(y; full combo). Returns dict incl dominance ratio + margin."""
    single = [mutual_info(X[:, i], y) for i in range(X.shape[1])]
    combo = np.array([hash(tuple(int(v) for v in row)) & 0x7fffffff for row in X], dtype=np.int64)
    joint = mutual_info(combo, y)
    best_single = max(single) if single else 0.0
    ratio = (best_single / joint) if joint > 1e-9 else float("nan")
    return dict(single_mi={CONSTITUENTS[i]: round(single[i], 4) for i in range(len(single))},
                best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4), dominance_ratio=round(ratio, 4) if ratio == ratio else ratio)


# ---- monotone constructable code + train-fit quantile-threshold readout ----

def _spearman_sign(col, y):
    """Sign of the rank correlation between an ordinal feature column and y (train only). +1 or -1."""
    n = len(col)
    if n < 3:
        return 1.0
    rc = np.argsort(np.argsort(col)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rc = rc - rc.mean(); ry = ry - ry.mean()
    denom = math.sqrt(float((rc * rc).sum()) * float((ry * ry).sum()))
    if denom <= 1e-12:
        return 1.0
    r = float((rc * ry).sum()) / denom
    return 1.0 if r >= 0.0 else -1.0


def _orient(Xtr, ytr, Xq):
    """Orient each constituent by its TRAIN Spearman sign so higher -> higher target (no test leakage).
    Returns oriented train/query features in 0..L-1 and the per-feature |rank-corr| magnitudes (>=0 weights)."""
    d = Xtr.shape[1]
    Xt = np.empty_like(Xtr); Xu = np.empty_like(Xq)
    wmag = np.zeros(d, dtype=np.float64)
    for i in range(d):
        s = _spearman_sign(Xtr[:, i], ytr)
        Xt[:, i] = Xtr[:, i] if s >= 0 else (L - 1 - Xtr[:, i])
        Xu[:, i] = Xq[:, i] if s >= 0 else (L - 1 - Xq[:, i])
        # non-negative weight = |rank corr| on the oriented column
        rc = np.argsort(np.argsort(Xt[:, i])).astype(np.float64); rc -= rc.mean()
        ry = np.argsort(np.argsort(ytr)).astype(np.float64); ry -= ry.mean()
        den = math.sqrt(float((rc * rc).sum()) * float((ry * ry).sum()))
        wmag[i] = abs(float((rc * ry).sum()) / den) if den > 1e-12 else 0.0
    return Xt, Xu, wmag


def _fit_quantile_thresholds(scores_tr, ytr):
    """TRAIN-fit L-1 thresholds so predicted-bin marginal matches the train target histogram (monotone readout)."""
    counts = np.bincount(ytr, minlength=L).astype(np.float64)
    cum = np.cumsum(counts) / max(1.0, counts.sum())
    qs = cum[:L - 1]  # cumulative boundaries between bins
    thr = np.quantile(scores_tr, np.clip(qs, 0.0, 1.0))
    return np.sort(thr)


def _predict_bins(scores, thr):
    return np.array([int((s > thr).sum()) for s in scores], dtype=np.int64)


def arm_monotone(Xtr, ytr, Xq, weighted):
    """MONO_THERM (equal weight) or MONO_WEIGHT (learned non-negative per-constituent weights). Additive, NO wrap."""
    Xt, Xu, wmag = _orient(Xtr, ytr, Xq)
    if weighted:
        w = wmag.copy()
        if w.sum() <= 1e-9:
            w = np.ones_like(w)
    else:
        w = np.ones(Xt.shape[1], dtype=np.float64)
    s_tr = (Xt.astype(np.float64) * w[None, :]).sum(axis=1)
    s_q = (Xu.astype(np.float64) * w[None, :]).sum(axis=1)
    thr = _fit_quantile_thresholds(s_tr, ytr)
    return _predict_bins(s_q, thr)


# ---- modular native FHRR bind (the v1 contrast that should FAIL on a non-modular target) ----

def build_fpe_codebook(L_, n_dim, seed):
    g = np.random.default_rng(seed * 100003 + 17)
    m = g.integers(1, max(2, L_), size=n_dim).astype(np.float64)
    j = np.arange(L_, dtype=np.float64)[:, None]
    phase = (2.0 * np.pi / L_) * (j * m[None, :])
    return torch.from_numpy(np.exp(1j * phase).astype(np.complex64))  # (L_, n_dim)


def cleanup_scores(pred, Ycode):
    Yc = Ycode.conj().T.contiguous()
    return (pred @ Yc).real.to(torch.float32)


def arm_modular_bind(Xq, Ycode):
    """Native additive FHRR bind of the 4 constituent FPE codes -> cleanup to nearest target code. Predicts
    (x0+x1+x2+x3) mod L -- WRAPS. On a monotone (non-modular) target this is the contrast that should FAIL."""
    acc = Ycode[torch.as_tensor(Xq[:, 0], dtype=torch.long)]
    for i in range(1, Xq.shape[1]):
        acc = hd_bind(acc, Ycode[torch.as_tensor(Xq[:, i], dtype=torch.long)])
    return torch.argmax(cleanup_scores(acc, Ycode), 1).numpy()


# ---- frequency / homophily null + memorize + pop ----

def arm_homophily_cond(Xq, Xtr, ytr, L_):
    """FREQUENCY/HOMOPHILY null: score(y) = sum_i count_train(X_i==xq_i, y). Subsumes factorized cond-freq P(y|X_i)."""
    per = [defaultdict(lambda: np.zeros(L_)) for _ in range(Xtr.shape[1])]
    for r in range(Xtr.shape[0]):
        for i in range(Xtr.shape[1]):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=L_).astype(np.float64)
    out = np.zeros((Xq.shape[0], L_), dtype=np.float64)
    for q in range(Xq.shape[0]):
        sc = np.zeros(L_)
        for i in range(Xq.shape[1]):
            sc = sc + per[i].get(int(Xq[q, i]), np.zeros(L_))
        if sc.sum() <= 0:
            sc = marg
        out[q] = sc
    return np.argmax(out, axis=1).astype(np.int64)


def arm_memorize(Xq, Xtr, ytr, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[tuple(Xtr[r].tolist())][int(ytr[r])] += 1
    preds = []
    for q in range(Xq.shape[0]):
        d = combo.get(tuple(Xq[q].tolist()))
        preds.append(max(d.items(), key=lambda kv: kv[1])[0] if d else pop_label)
    return np.asarray(preds, dtype=np.int64)


def acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


# ---- regimes / splits ----

def plant_regime_target(X, y_real, regime, seed):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100057 + (hash(regime) % 100000))
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ARBITRARY:
        table = rng.integers(0, L, size=(L, L, L, L))
        y = np.array([table[tuple(int(v) for v in X[r])] for r in range(n)], dtype=np.int64)
        return y, y.copy()
    if regime == SHUFFLE:
        return y_real[rng.permutation(n)].copy(), y_real.copy()
    raise ValueError(regime)


def split_novel(X, seed, query_frac=0.45):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100081 + 9)
    perm = rng.permutation(n)
    nq = int(round(query_frac * n))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_combos = set(tuple(X[i].tolist()) for i in tr)
    novel = np.array([tuple(X[i].tolist()) not in train_combos for i in q], dtype=bool)
    return q, tr, novel


def score_regime(X, y_real, regime, seed, n_dim):
    q, tr, novel = split_novel(X, seed)
    y, oracle = plant_regime_target(X, y_real, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y[q], y[tr]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=L)))

    Ycode = build_fpe_codebook(L, n_dim, seed * 97 + 3)  # ONE shared FPE basis (the group homomorphism)

    mt = arm_monotone(Xtr, ytr, Xq, weighted=False)
    mw = arm_monotone(Xtr, ytr, Xq, weighted=True)
    mod = arm_modular_bind(Xq, Ycode)
    hom = arm_homophily_cond(Xq, Xtr, ytr, L)
    memo = arm_memorize(Xq, Xtr, ytr, pop_label)
    pop = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    orc = oracle[q]

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    res = {}
    for sname, m in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        freq_null = max(a(hom, m), a(pop, m))
        res[sname] = dict(
            MONO_THERM=round(a(mt, m), 5), MONO_WEIGHT=round(a(mw, m), 5), MODULAR_BIND=round(a(mod, m), 5),
            HOMOPHILY_COND=round(a(hom, m), 5), MEMORIZE=round(a(memo, m), 5), POP=round(a(pop, m), 5),
            ORACLE=round(a(orc, m), 5), FREQ_NULL=round(freq_null, 5), n=int(m.sum()))
    sigs = dict(MONO_WEIGHT=_sig(mw), MODULAR_BIND=_sig(mod), HOMOPHILY_COND=_sig(hom), ORACLE=_sig(orc))
    return dict(regime=regime, strata=res, sigs=sigs, n_query=int(len(gold)), n_novel=int(novel.sum()))


def run_measurement(seeds=(7, 13, 17, 23, 29), n_dim=1024):
    p, X, y = load_cluster()
    conj = conjunction_property(X, y)
    per_seed = []
    for sd in seeds:
        per_seed.append({reg: score_regime(X, y, reg, sd, n_dim) for reg in REGIMES})

    def mean_novel(reg, arm):
        vals = [ps[reg]["strata"]["novel"][arm] for ps in per_seed]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    mw_clean = mean_novel(CLEAN, MONO_W)
    mt_clean = mean_novel(CLEAN, MONO_T)
    mod_clean = mean_novel(CLEAN, MODUL)
    fn_clean = mean_novel(CLEAN, "FREQ_NULL")
    memo_clean = mean_novel(CLEAN, MEMO)
    orc_clean = mean_novel(CLEAN, ORC)
    mw_arb = mean_novel(ARBITRARY, MONO_W); fn_arb = mean_novel(ARBITRARY, "FREQ_NULL")
    mw_shuf = mean_novel(SHUFFLE, MONO_W); fn_shuf = mean_novel(SHUFFLE, "FREQ_NULL")

    diss = mw_clean - fn_clean               # HEADLINE: monotone learned-weight vs frequency null on NOVEL
    modular_gap = mod_clean - fn_clean       # modular contrast vs frequency null
    arb_gap = mw_arb - fn_arb
    shuf_gap = mw_shuf - fn_shuf
    truth = p.get("truth_rate", float("nan"))

    ratio = conj["dominance_ratio"]
    conj_present = bool(ratio == ratio and ratio <= CONJ_RATIO_CEIL and conj["mi_margin"] >= CONJ_MI_MARGIN)
    truth_ok = bool(truth == truth and truth >= HP_TRUTH)
    generalizes = bool(diss == diss and diss >= HP_DISSOCIATION)
    mono_beats_modular = bool(diss == diss and modular_gap == modular_gap and diss > modular_gap)
    mustfails_fire = bool(arb_gap <= MUSTFAIL_TOL and shuf_gap <= MUSTFAIL_TOL)
    ceiling_ok = bool(orc_clean >= mw_clean - 1e-6)

    hard_pass = bool(conj_present and truth_ok and generalizes and mono_beats_modular
                     and mustfails_fire and ceiling_ok)
    refute = bool((not truth_ok) or (not conj_present) or (diss <= REFUTE_TOL))

    if not ceiling_ok:
        verdict = "INCONCLUSIVE_CEILING_MALFORMED"
    elif hard_pass:
        verdict = "GENERATED_CONJUNCTION_MONOTONE_BEATS_FREQUENCY_FOUNDATION_GO"
    elif refute:
        verdict = "GENERATED_CONJUNCTION_MONOTONE_PREMISE_REFUTED"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || n=%d truth=%s(>=%.2f=%s) | CONJ: joint_mi=%.3f best_single=%.3f margin=%.3f(>=%.2f) ratio=%s(<=%.2f) "
           "present=%s singles=%s | CLEAN novel: MONO_W=%s MONO_T=%s FREQ_NULL=%s diss=%s(>=%.2f=%s) MODULAR=%s "
           "mod_gap=%s mono>mod=%s MEMO=%s ORACLE=%s | ARBITRARY(mf) gap=%s SHUFFLE(mf) gap=%s (<=%.2f) mustfails=%s "
           "ceiling_ok=%s"
           % (verdict, p["n_entities"], _fmt(truth), HP_TRUTH, truth_ok, conj["joint_mi"], conj["best_single_mi"],
              conj["mi_margin"], CONJ_MI_MARGIN, _fmt(ratio) if ratio == ratio else "nan", CONJ_RATIO_CEIL,
              conj_present, conj["single_mi"], _fmt(mw_clean), _fmt(mt_clean), _fmt(fn_clean), _fmt(diss),
              HP_DISSOCIATION, generalizes, _fmt(mod_clean), _fmt(modular_gap), mono_beats_modular, _fmt(memo_clean),
              _fmt(orc_clean), _fmt(arb_gap), _fmt(shuf_gap), MUSTFAIL_TOL, mustfails_fire, ceiling_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="local_measure",
        elapsed_s=0.0, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_entities=p["n_entities"], truth_rate=truth, n_judged=p.get("n_judged"), n_true=p.get("n_true"),
        seeds=list(seeds), n_dim=n_dim, L=L,
        conjunction=conj,
        gates=dict(conj_present=conj_present, truth_ok=truth_ok, generalizes=generalizes,
                   mono_beats_modular=mono_beats_modular, mustfails_fire=mustfails_fire, ceiling_ok=ceiling_ok,
                   hard_pass=hard_pass, refute=refute),
        clean=dict(mono_weight=round(mw_clean, 5), mono_therm=round(mt_clean, 5), modular_bind=round(mod_clean, 5),
                   freq_null=round(fn_clean, 5), dissociation=round(diss, 5), modular_gap=round(modular_gap, 5),
                   memorize=round(memo_clean, 5), oracle=round(orc_clean, 5)),
        arbitrary=dict(gap=round(arb_gap, 5), mono_weight=round(mw_arb, 5), freq_null=round(fn_arb, 5)),
        shuffle=dict(gap=round(shuf_gap, 5), mono_weight=round(mw_shuf, 5), freq_null=round(fn_shuf, 5)),
        bands=dict(HP_TRUTH=HP_TRUTH, CONJ_RATIO_CEIL=CONJ_RATIO_CEIL, CONJ_MI_MARGIN=CONJ_MI_MARGIN,
                   HP_DISSOCIATION=HP_DISSOCIATION, MUSTFAIL_TOL=MUSTFAIL_TOL, REFUTE_TOL=REFUTE_TOL),
        per_seed=[{reg: per_seed[i][reg]["strata"]["novel"] for reg in REGIMES} for i in range(len(seeds))],
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def self_test():
    """Exercise the REAL monotone arms + REAL hd_bind on a tiny PLANTED strongly-conjunctive MONOTONE arena.
    MONO must solve + generalize on NOVEL combos and clearly beat freq (no single dominant driver); ARBITRARY fires;
    modular bind must NOT win; guard-vs-arena-floor: freq_null must not be saturated."""
    n_dim = 256
    rng = np.random.default_rng(7)
    n = 320
    X = rng.integers(0, L, size=(n, 4)).astype(np.int64)
    # BALANCED monotone conjunction: all 4 contribute, no single dominant driver, non-modular (quantile-binned sum).
    w_true = np.array([0.9, 1.0, 1.1, 1.0])
    s = (X.astype(np.float64) * w_true[None, :]).sum(1)
    edges = np.quantile(s, [0.2, 0.4, 0.6, 0.8])
    y_add = np.array([int((v > edges).sum()) for v in s], dtype=np.int64)

    r = score_regime(X, y_add, CLEAN, 7, n_dim)
    nov = r["strata"]["novel"]
    mw = nov[MONO_W]; mt = nov[MONO_T]; fn = nov["FREQ_NULL"]; mod = nov[MODUL]
    ra = score_regime(X, y_add, ARBITRARY, 7, n_dim)
    arb_gap = ra["strata"]["novel"][MONO_W] - ra["strata"]["novel"]["FREQ_NULL"]
    mono_gap = mw - fn
    modular_gap = mod - fn

    # REAL bind homomorphism check: bind of FPE codes reads out (i+j) mod L.
    Yt = build_fpe_codebook(L, n_dim, 31)
    bound = hd_bind(Yt[torch.tensor([1, 2])], Yt[torch.tensor([2, 3])])
    homo_pred = torch.argmax(cleanup_scores(bound, Yt), 1).tolist()
    homo_ok = homo_pred == [3 % L, 5 % L]

    conj = conjunction_property(X, y_add)
    ratio = conj["dominance_ratio"]

    ok = bool(
        mw >= 0.50                                   # monotone solves + generalizes on novel
        and mono_gap >= 0.15                         # guard: clearly beats freq (real lift, not saturation)
        and fn <= 0.85                               # guard-vs-arena-floor: freq not saturated
        and mono_gap > modular_gap                   # monotone beats modular contrast
        and arb_gap <= 0.10                          # ARBITRARY must-fail fires
        and homo_ok                                  # real FHRR bind homomorphism intact
        and conj["mi_margin"] >= CONJ_MI_MARGIN      # planted arena is a genuine conjunction
        and ratio == ratio and ratio <= CONJ_RATIO_CEIL
        and r["n_novel"] >= 8
    )
    out = dict(mono_weight_novel=round(mw, 4), mono_therm_novel=round(mt, 4), freq_null_novel=round(fn, 4),
               mono_gap=round(mono_gap, 4), modular_novel=round(mod, 4), modular_gap=round(modular_gap, 4),
               arb_gap=round(arb_gap, 4), homomorphism_ok=homo_ok, mi_margin=conj["mi_margin"],
               dominance_ratio=ratio, n_novel=r["n_novel"], passed=ok)
    print("[SELFTEST] %s" % json.dumps(out), flush=True)
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-per-batch", type=int, default=34)
    ap.add_argument("--n-dim", type=int, default=1024)
    args = ap.parse_args()

    if args.self_test:
        ok, _ = self_test()
        sys.exit(0 if ok else 1)
    if args.generate:
        do_generate(n_per_batch=args.n_per_batch)
        return
    if args.run:
        if not os.path.exists(ARTIFACT):
            _log("ARTIFACT missing (%s); run --generate first (build-time)." % ARTIFACT)
            sys.exit(2)
        t0 = time.perf_counter()
        m = run_measurement(n_dim=args.n_dim)
        m["elapsed_s"] = time.perf_counter() - t0
        _write_metrics(m)
        _log(m["verdict_msg"])
        return
    ap.print_help()


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
            with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
                json.dump(crash, f, indent=2)
        except Exception:
            pass
        raise
