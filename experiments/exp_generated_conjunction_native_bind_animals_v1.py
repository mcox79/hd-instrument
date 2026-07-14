"""GENERATED_CONJUNCTION_NATIVE_BIND (foundation-build first batch de-risk).

De-risk question (per notes/foundation_build_first_batch_design_2026-07-14.md): the conjunction MECHANISM cell
(conjunction_native_bind_vs_homophily_cskg_v1, HARD-PASS) used PLANTED additive conjunctions. THIS batch tests whether
EXTERNALLY-GENERATED real-world conjunction structure is (a) PRESENT/generable, (b) constructable-encodable, (c) beats
frequency under the substrate's NATIVE additive FHRR bind -- with a genuine REFUTE path if generated targets are
single-relation/homophily-solvable OR not additively-factorizable.

Cluster (real, vettable, addresses the science/biology coverage gap): ANIMALS. Per entity the external generator
(claude-haiku-4-5, foundation-build tool) emits ordinal-graded values on FOUR constituent scales AND a held-out ordinal
target -- ALL real-world biology, NO rule revealed to the generator:
  body_size            [tiny,small,medium,large,huge]            -> 0..4
  habitat_temperature  [frigid,cold,temperate,warm,hot]          -> 0..4
  activity_level       [sedentary,low,moderate,active,very_active]-> 0..4
  diet_richness        [poor,lean,moderate,rich,very_rich]       -> 0..4
  TARGET metabolic_rate[very_low,low,moderate,high,very_high]    -> 0..4  (held out; plausibly a CONJUNCTION of the four)

Honest matched design: the substrate's VALIDATED mechanism is the NATIVE additive FHRR bind, which GENERALIZES only
additive/group-structured targets. So we encode the constituent ordinals with CONSTRUCTABLE FPE phasor codes (NO SGD)
and test whether the REAL metabolic-rate target is recovered by native bind (additive readout) on NOVEL constituent
COMBINATIONS, beating the strongest FREQUENCY/HOMOPHILY null and MEMORIZE. We do NOT plant the target = we MEASURE.

MEASURED de-risk gates:
  (a) CONJUNCTION PRESENT: joint MI(target ; all 4 constituents) >> best single-relation MI(target ; one constituent).
  (b) GENERALIZES: NATIVE_BIND novel-combo top1 - FREQ_NULL novel-combo top1 >= dissociation band.
  must-fails: ARBITRARY (random-table target) + SHUFFLE (freq-preserving label permutation) native-bind must NOT lift.

PRE-REGISTERED BANDS (NOVEL stratum, top-1 acc; chance=1/L=0.20; NOT tuned):
  HARD_PASS  (foundation build GO): conjunction_present (MI_joint - MI_single_best >= 0.15 bits) AND generation truth
             >= 0.85 AND NATIVE_BIND_novel - FREQ_NULL_novel >= 0.15 AND both must-fails fire (gap <= 0.05).
  REFUTE     (premise fails): generation truth < 0.85 OR NOT conjunction_present (target single-relation/homophily
             solvable: FREQ_NULL_novel >= NATIVE_BIND_novel - 0.05) -> generate-conjunctions premise fails / additive
             native bind does NOT transfer to real ordinal targets. THE most valuable negative.
  MIDDLE_BAND: anything else (conjunction present but native-bind modestly beats freq, or bands not clean).

This file is BOTH the build-time generator (--generate: calls the external tool, writes the vetted artifact) AND the
substrate measurement (reads the artifact, NO LLM at measurement time; --self-test / --run). Runtime measurement stays
glass-box (zero LLM). ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import math
import os
import platform
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

ANCHOR_NAME = "generated_conjunction_native_bind_animals_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "animals_ordinal_conjunction_v1.json")

SCALES = {
    "body_size": ["tiny", "small", "medium", "large", "huge"],
    "habitat_temperature": ["frigid", "cold", "temperate", "warm", "hot"],
    "activity_level": ["sedentary", "low", "moderate", "active", "very_active"],
    "diet_richness": ["poor", "lean", "moderate", "rich", "very_rich"],
}
CONSTITUENTS = list(SCALES.keys())
TARGET = "metabolic_rate"
TARGET_SCALE = ["very_low", "low", "moderate", "high", "very_high"]
L = 5  # ordinal levels per attribute (0..4)

# ---- regimes ----
CLEAN = "CLEAN_REAL"       # the real generated target
ARBITRARY = "ARBITRARY"    # target = fixed random table over the 4 constituents (must-fail)
SHUFFLE = "SHUFFLE"        # real target permuted across entities (freq-preserving; must-fail)
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]

NBIND = "NATIVE_BIND"
MEMO = "MEMORIZE"
HOM = "HOMOPHILY_COND"
POP = "POP"
ORC = "ORACLE"
FREQ_NULL_ARMS = [HOM, POP]

# ---- pre-registered bands ----
HP_MI_MARGIN = 0.15        # bits: MI_joint - MI_single_best
HP_TRUTH = 0.85
HP_DISSOCIATION = 0.15
MUSTFAIL_TOL = 0.05
REFUTE_TOL = 0.05


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


# ===========================================================================
# BUILD-TIME GENERATION (external tool; runs locally only, writes the vetted artifact).
# ===========================================================================

GEN_ANIMALS_BATCHES = [
    "mammals: carnivores, ungulates, rodents, bats, marine mammals, primates",
    "birds: raptors, songbirds, waterfowl, seabirds, flightless, wading birds",
    "reptiles and amphibians: snakes, lizards, turtles, crocodilians, frogs, salamanders",
    "fish: sharks, rays, bony fish (tropical and cold-water), deep-sea, freshwater",
    "invertebrates: insects, arachnids, crustaceans, cephalopods, mollusks, worms",
    "small mammals and misc: shrews, hedgehogs, marsupials, monotremes, mustelids",
]


def _gen_prompt(batch_desc, n):
    lines = []
    lines.append("You are a careful zoologist building a vetted knowledge base. List %d real, distinct, well-known "
                 "animal species from this group: %s." % (n, batch_desc))
    lines.append("For EACH animal, give its TYPICAL value on each of these ordinal scales (choose exactly one level):")
    for k, lv in SCALES.items():
        lines.append("  %s: one of %s" % (k, lv))
    lines.append("  %s: one of %s" % (TARGET, TARGET_SCALE))
    lines.append("Base every value on established biology. Do NOT follow any formula; give the real typical value.")
    lines.append("Return ONLY a JSON array, each element: "
                 '{"name":..., "body_size":..., "habitat_temperature":..., "activity_level":..., '
                 '"diet_richness":..., "metabolic_rate":...}. No prose.')
    return "\n".join(lines)


def _extract_json_array(text):
    s = text.find("[")
    e = text.rfind("]")
    if s < 0 or e < 0 or e <= s:
        return []
    try:
        return json.loads(text[s:e + 1])
    except Exception:
        return []


def _vet_prompt(rows):
    lines = ["You are an adversarial fact-checker. For each animal record below, judge whether ALL FIVE attribute "
             "values are biologically CORRECT for that species (typical adult). Answer strictly.",
             "Scales: body_size%s habitat_temperature%s activity_level%s diet_richness%s metabolic_rate%s"
             % (SCALES["body_size"], SCALES["habitat_temperature"], SCALES["activity_level"],
                SCALES["diet_richness"], TARGET_SCALE),
             "Return ONLY a JSON array of {\"name\":..., \"ok\":true/false}. A record is ok=false if ANY value is "
             "clearly wrong. Records:"]
    for r in rows:
        lines.append(json.dumps({k: r.get(k) for k in (["name"] + CONSTITUENTS + [TARGET])}))
    return "\n".join(lines)


def do_generate(n_per_batch=32, seed=7):
    """Call the external generator + adversarial vetter; write the vetted artifact. Local build-time only."""
    import pathlib
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(_REPO) / ".env.local")
    from backend.llm import anthropic_client

    valset = {k: set(v) for k, v in SCALES.items()}
    valset[TARGET] = set(TARGET_SCALE)
    seen = {}
    for bi, bd in enumerate(GEN_ANIMALS_BATCHES):
        _log("generate batch %d/%d: %s" % (bi + 1, len(GEN_ANIMALS_BATCHES), bd))
        resp = anthropic_client.chat(_gen_prompt(bd, n_per_batch), max_tokens=4096, temperature=0.4)
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

    # ---- adversarial vet (subset, in batches of 40) ----
    truth_flags = {}
    for s in range(0, len(rows), 40):
        chunk = rows[s:s + 40]
        vresp = anthropic_client.chat(_vet_prompt(chunk), max_tokens=4096, temperature=0.0)
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
                   scales=SCALES, target=TARGET, target_scale=TARGET_SCALE, L=L,
                   n_entities=len(rows), n_judged=n_judged, n_true=n_true, truth_rate=truth_rate, rows=rows)
    tmp = ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, ARTIFACT)
    _log("ARTIFACT written: %s (n=%d truth_rate=%s)" % (ARTIFACT, len(rows), _fmt(truth_rate)))
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
    """single-relation MI(y;X_i) vs joint MI(y; combo). Returns dict."""
    single = [mutual_info(X[:, i], y) for i in range(X.shape[1])]
    combo = np.array([hash(tuple(row)) & 0x7fffffff for row in X], dtype=np.int64)
    joint = mutual_info(combo, y)
    best_single = max(single) if single else 0.0
    return dict(single_mi={CONSTITUENTS[i]: round(single[i], 4) for i in range(len(single))},
                best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4))


def build_fpe_codebook(L_, n_dim, seed):
    g = np.random.default_rng(seed * 100003 + 17)
    m = g.integers(1, max(2, L_), size=n_dim).astype(np.float64)
    j = np.arange(L_, dtype=np.float64)[:, None]
    phase = (2.0 * np.pi / L_) * (j * m[None, :])
    return torch.from_numpy(np.exp(1j * phase).astype(np.complex64))  # (L_, n_dim)


def cleanup_scores(pred, Ycode):
    Yc = Ycode.conj().T.contiguous()
    return (pred @ Yc).real.to(torch.float32)


def arm_native_bind(Xq, Ycode):
    """Native additive FHRR bind of the 4 constituent FPE codes -> cleanup to nearest target code.
    Constructable (NO SGD): ONE shared FPE basis Ycode over 0..L-1 for all constituents AND the target. Because Ycode
    is a Z_L group homomorphism under FHRR bind, bind(Ycode[x0],...,Ycode[x3]) = Ycode[(x0+x1+x2+x3) mod L] EXACTLY, so
    the additive-combination class is predicted and GENERALIZES to novel constituent combinations."""
    acc = Ycode[torch.as_tensor(Xq[:, 0], dtype=torch.long)]
    for i in range(1, Xq.shape[1]):
        acc = hd_bind(acc, Ycode[torch.as_tensor(Xq[:, i], dtype=torch.long)])
    return cleanup_scores(acc, Ycode)  # (nq, L)


def arm_homophily_cond(Xq, Xtr, ytr, L_):
    """FREQUENCY/HOMOPHILY null: score(y) = sum_i count_train(X_i==xq_i, y). Subsumes factorized cond-freq P(y|X_i)."""
    per = [defaultdict(lambda: np.zeros(L_)) for _ in range(Xtr.shape[1])]
    for r in range(Xtr.shape[0]):
        for i in range(Xtr.shape[1]):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=L_).astype(np.float64)
    out = np.zeros((Xq.shape[0], L_), dtype=np.float32)
    for q in range(Xq.shape[0]):
        sc = np.zeros(L_)
        for i in range(Xq.shape[1]):
            sc = sc + per[i].get(int(Xq[q, i]), np.zeros(L_))
        if sc.sum() <= 0:
            sc = marg
        out[q] = sc
    return torch.from_numpy(out)


def arm_memorize(Xq, Xtr, ytr, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[tuple(Xtr[r].tolist())][int(ytr[r])] += 1
    preds = []
    for q in range(Xq.shape[0]):
        d = combo.get(tuple(Xq[q].tolist()))
        preds.append(max(d.items(), key=lambda kv: kv[1])[0] if d else pop_label)
    return np.asarray(preds, dtype=np.int64)


def acc_from_scores(scores, gold):
    if scores.shape[0] == 0:
        return float("nan")
    gt = torch.as_tensor(gold, dtype=torch.long)
    gs = scores.gather(1, gt.view(-1, 1)).squeeze(1)
    greater = (scores > gs.view(-1, 1)).sum(dim=1)
    equal = (scores == gs.view(-1, 1)).sum(dim=1)
    rank = greater.to(torch.float64) + (equal.to(torch.float64) + 1.0) / 2.0
    return float((rank <= 1.0).to(torch.float64).mean().item())


def acc_from_labels(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


def plant_regime_target(X, y_real, regime, seed):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100057 + (hash(regime) % 100000))
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ARBITRARY:
        table = rng.integers(0, L, size=(L, L, L, L))
        y = np.array([table[tuple(X[r])] for r in range(n)], dtype=np.int64)
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

    nb = arm_native_bind(Xq, Ycode)
    hom = arm_homophily_cond(Xq, Xtr, ytr, L)
    memo = arm_memorize(Xq, Xtr, ytr, pop_label)
    pop = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    orc = oracle[q]

    def strat(scores_or_lab, is_scores, msk):
        if msk.sum() == 0:
            return float("nan")
        if is_scores:
            return acc_from_scores(scores_or_lab[torch.as_tensor(msk)], gold[msk])
        return acc_from_labels(np.asarray(scores_or_lab)[msk], gold[msk])

    res = {}
    for sname, m in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        res[sname] = dict(
            NATIVE_BIND=round(strat(nb, True, m), 5), HOMOPHILY_COND=round(strat(hom, True, m), 5),
            MEMORIZE=round(strat(memo, False, m), 5), POP=round(strat(pop, False, m), 5),
            ORACLE=round(strat(orc, False, m), 5),
            FREQ_NULL=round(max(strat(hom, True, m), strat(pop, False, m)), 5), n=int(msk.sum() if False else m.sum()))
    sigs = dict(NATIVE_BIND=_sig(torch.argmax(nb, 1).numpy()), HOMOPHILY_COND=_sig(torch.argmax(hom, 1).numpy()),
                MEMORIZE=_sig(memo), POP=_sig(pop), ORACLE=_sig(orc))
    return dict(regime=regime, strata=res, sigs=sigs, n_query=int(len(gold)), n_novel=int(novel.sum()))


def run_measurement(seeds=(7, 13, 17), n_dim=1024):
    p, X, y = load_cluster()
    conj = conjunction_property(X, y)
    per_seed = []
    for sd in seeds:
        rr = {reg: score_regime(X, y, reg, sd, n_dim) for reg in REGIMES}
        per_seed.append(rr)

    def mean_novel(reg, arm):
        vals = [ps[reg]["strata"]["novel"][arm] for ps in per_seed]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    nb_clean = mean_novel(CLEAN, NBIND)
    fn_clean = mean_novel(CLEAN, "FREQ_NULL")
    memo_clean = mean_novel(CLEAN, MEMO)
    orc_clean = mean_novel(CLEAN, ORC)
    nb_arb = mean_novel(ARBITRARY, NBIND); fn_arb = mean_novel(ARBITRARY, "FREQ_NULL")
    nb_shuf = mean_novel(SHUFFLE, NBIND); pop_shuf = mean_novel(SHUFFLE, POP)

    diss = nb_clean - fn_clean
    arb_gap = nb_arb - fn_arb
    shuf_gap = nb_shuf - pop_shuf
    truth = p.get("truth_rate", float("nan"))

    conj_present = bool(conj["mi_margin"] >= HP_MI_MARGIN)
    truth_ok = bool(truth == truth and truth >= HP_TRUTH)
    generalizes = bool(diss == diss and diss >= HP_DISSOCIATION)
    mustfails_fire = bool(arb_gap <= MUSTFAIL_TOL and shuf_gap <= MUSTFAIL_TOL)
    ceiling_ok = bool(orc_clean >= nb_clean - 1e-6)

    hard_pass = bool(conj_present and truth_ok and generalizes and mustfails_fire and ceiling_ok)
    refute = bool((not truth_ok) or (not conj_present) or (diss <= REFUTE_TOL))

    if not ceiling_ok:
        verdict = "INCONCLUSIVE_CEILING_MALFORMED"
    elif hard_pass:
        verdict = "GENERATED_CONJUNCTION_NATIVE_BIND_BEATS_FREQUENCY_FOUNDATION_GO"
    elif refute:
        verdict = "GENERATED_CONJUNCTION_PREMISE_REFUTED_OR_NOT_ADDITIVE"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || n=%d truth=%s(>=%.2f=%s) | CONJ: joint_mi=%.3f best_single=%.3f margin=%.3f(>=%.2f=%s) singles=%s | "
           "CLEAN_REAL novel: NBIND=%s FREQ_NULL=%s diss=%s(>=%.2f=%s) MEMO=%s ORACLE=%s | ARBITRARY(mf): gap=%s(<=%.2f) "
           "SHUFFLE(mf): gap=%s(<=%.2f) mustfails_fire=%s ceiling_ok=%s"
           % (verdict, p["n_entities"], _fmt(truth), HP_TRUTH, truth_ok, conj["joint_mi"], conj["best_single_mi"],
              conj["mi_margin"], HP_MI_MARGIN, conj_present, conj["single_mi"], _fmt(nb_clean), _fmt(fn_clean),
              _fmt(diss), HP_DISSOCIATION, generalizes, _fmt(memo_clean), _fmt(orc_clean), _fmt(arb_gap),
              MUSTFAIL_TOL, _fmt(shuf_gap), MUSTFAIL_TOL, mustfails_fire, ceiling_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="local_measure",
        elapsed_s=0.0, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_entities=p["n_entities"], truth_rate=truth, n_judged=p.get("n_judged"), n_true=p.get("n_true"),
        seeds=list(seeds), n_dim=n_dim, L=L,
        conjunction=conj,
        gates=dict(conj_present=conj_present, truth_ok=truth_ok, generalizes=generalizes,
                   mustfails_fire=mustfails_fire, ceiling_ok=ceiling_ok, hard_pass=hard_pass, refute=refute),
        clean=dict(native_bind=round(nb_clean, 5), freq_null=round(fn_clean, 5), dissociation=round(diss, 5),
                   memorize=round(memo_clean, 5), oracle=round(orc_clean, 5)),
        arbitrary=dict(gap=round(arb_gap, 5), native_bind=round(nb_arb, 5), freq_null=round(fn_arb, 5)),
        shuffle=dict(gap=round(shuf_gap, 5), native_bind=round(nb_shuf, 5), pop=round(pop_shuf, 5)),
        bands=dict(HP_MI_MARGIN=HP_MI_MARGIN, HP_TRUTH=HP_TRUTH, HP_DISSOCIATION=HP_DISSOCIATION,
                   MUSTFAIL_TOL=MUSTFAIL_TOL, REFUTE_TOL=REFUTE_TOL),
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
    """Exercise the REAL bind path + arm machinery on a tiny PLANTED-additive arena (apparatus validity)."""
    n_dim = 256
    rng = np.random.default_rng(7)
    n = 200
    X = rng.integers(0, L, size=(n, 4)).astype(np.int64)
    y_add = (X.sum(1) % L).astype(np.int64)  # PLANTED additive -> native bind MUST solve + generalize
    r = score_regime(X, y_add, CLEAN, 7, n_dim)
    nb = r["strata"]["novel"][NBIND]
    fn = r["strata"]["novel"]["FREQ_NULL"]
    ra = score_regime(X, y_add, ARBITRARY, 7, n_dim)
    arb_gap = ra["strata"]["novel"][NBIND] - ra["strata"]["novel"]["FREQ_NULL"]
    # real bind homomorphism check
    cbs = [build_fpe_codebook(L, n_dim, 31 + i) for i in range(4)]
    Yt = cbs[0]
    a = cbs[0][torch.tensor([1, 2])]
    b = cbs[0][torch.tensor([2, 3])]
    bound = hd_bind(a, b)
    pred = torch.argmax(cleanup_scores(bound, Yt), 1).tolist()
    homo_ok = pred == [3 % L, 5 % L]
    conj = conjunction_property(X, y_add)
    ok = bool(nb >= 0.90 and (nb - fn) >= 0.30 and arb_gap <= 0.10 and homo_ok
              and conj["mi_margin"] >= 0.15 and r["n_novel"] >= 8)
    out = dict(native_bind_novel=round(nb, 4), freq_null_novel=round(fn, 4), dissociation=round(nb - fn, 4),
               arb_gap=round(arb_gap, 4), homomorphism_ok=homo_ok, mi_margin=conj["mi_margin"],
               n_novel=r["n_novel"], passed=ok)
    print("[SELFTEST] %s" % json.dumps(out), flush=True)
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-per-batch", type=int, default=32)
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
            _write_crash = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(e).__name__, str(e)[:400]),
                                summary="CELL_CRASHED", elapsed_s=0.0, anchor_name=ANCHOR_NAME,
                                traceback=traceback.format_exc()[:4000],
                                ts_iso=datetime.now(timezone.utc).isoformat())
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
                json.dump(_write_crash, f, indent=2)
        except Exception:
            pass
        raise
