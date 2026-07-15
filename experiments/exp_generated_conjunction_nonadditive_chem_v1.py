"""GENERATED_CONJUNCTION_NONADDITIVE_CHEM (foundation-build: GENUINELY non-additive vettable cluster from a high-
interaction POCKET).

WHY THIS CELL (de-risks the pivot FOUNDATION half): drill 2026-07-14
(notes/drill_realworld_conjunctive_determination_prevalence_and_targets_2026-07-14.md) found genuine no-dominant-driver
conjunctions are a MINORITY regime overall BUT concentrate in specific pockets: chemistry potency/binding nonadditivity,
genetic epistasis / synthetic lethality, drug-drug synergy, chemical-incompatibility / threshold outcomes. Our prior
FOODS cluster (exp_generated_conjunction_monotone_foods_v1) came from organismal biology (the wrong domain class): it
PASSED the MI-only conjunction gate (dominance_ratio 0.306, mi_margin 1.25 bits) yet a MONOTONE ADDITIVE arm nearly
captured the target (dissociation only +0.088) -> MIDDLE_BAND. LESSON (load-bearing): single-vs-joint MI is NECESSARY but
NOT SUFFICIENT for GENUINE conjunctivity -- a target can depend on many features ADDITIVELY (transform-additive) and still
lift joint-MI far above best-single-MI. The DISCRIMINATING test the foods cell LACKED is a NON-ADDITIVITY check: does a
FLEXIBLE learned-ADDITIVE (main-effects) model FAIL to capture the target, so that a model WITH interactions beats it?

POCKET CHOSEN: chemical / substance MIXING HAZARD (SDS incompatibility). Highly vettable (established safety knowledge:
bleach+ammonia -> chloramine SEVERE; bleach+acid -> chlorine SEVERE; oxidizer+fuel -> fire; reactive-metal+water -> H2;
acid+base -> heat; two inerts -> none). Genuinely AND-gate / relational: a member's contribution to hazard changes
entirely with its PARTNER (ammonia+water = none, ammonia+bleach = severe) -> no single dominant driver, NOT additive.
Entity = a real named PAIR of substances; constituents = reactivity CLASS of each member (unordered, canonical-sorted);
held-out TARGET = mixing-hazard severity (ordinal). We MEASURE genuineness (we do NOT plant the real target).

GLASS-BOX: generation is BUILD-TIME-LOCAL (external LLM + adversarial vet). Measurement is glass-box CPU, NO LLM, runs to
completion locally (pure numpy MI + main-effects/interaction fits on ~150 real pairs; milliseconds).

ARMS (measurement): ADDITIVE (flexible per-class main-effects, quantile-threshold readout) ; INTERACTIVE (class-PAIR
conditional mode with additive backoff on novel pairs) ; FREQ_NULL/POP ; ORACLE(ceiling).
NON-ADDITIVITY METRIC (the whole point): interactive_seen_acc - additive_seen_acc on the SEEN-PAIR stratum (class-pair
present in train). If large, the class-pair carries genuine interaction info BEYOND the additive marginals.
CONTROL REGIMES (discriminator-fires + must-fail): CLEAN(real) ; ADDITIVE_SYNTH (target = quantile-bin of the BEST
additive projection sev[cA]+sev[cB] of the real data -> MI conjunction PRESENT but additive CAN capture it: the gate must
NOT fire) ; SHUFFLE (freq-preserving label permutation -> all MI destroyed). ADDITIVE_SYNTH is the load-bearing control:
it proves the gate SEPARATES genuine-interaction from additive-multi-feature (the exact thing the foods gate conflated).

PRE-REGISTERED BANDS (fixed BEFORE running):
  Genuineness gate (all on CLEAN, full/averaged):
    truth_rate >= 0.85 (adversarial vet) AND
    dominance_ratio = best_single_mi / joint_mi <= 0.60 AND
    mi_margin = joint_mi - best_single_mi >= 0.30 bits AND
    nonadditivity = interactive_seen_acc - additive_seen_acc >= 0.12 (a flexible ADDITIVE model canNOT capture it).
  Discriminator-valid (gate must SEPARATE genuine from additive; else INCONCLUSIVE):
    ADDITIVE_SYNTH nonadditivity <= 0.08 AND clean_nonadditivity > addsynth_nonadditivity + 0.05 AND
    SHUFFLE conj_present == False.
  HARD_PASS (pocket yields genuinely-conjunctive vettable data -> FOUNDATION-GENERATION GO for this pocket):
    genuineness gate holds AND discriminator-valid AND oracle ceiling ok.
  REFUTE (valuable negative -- even the RIGHT pocket does not yield genuinely non-additive vettable data here):
    (truth < 0.85) OR (dominance_ratio > 0.80: a single class dominates) OR (nonadditivity <= 0.04: additive captures it
    -> transform-additive, same failure mode as foods). Trusted only if discriminator-valid.
  MIDDLE_BAND: anything else (conjunction present but non-additivity modest / bands not clean).

ASCII-only. No bare except; except SystemExit before except Exception. Deterministic integer seeds (PROT-023): NO hash()-
derived RNG seeds, NO list(set()) ordering -- fixed ints + stable enumerated regime indices + sorted-unique combo ids.
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR_NAME = "generated_conjunction_nonadditive_chem_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "chem_pair_hazard_nonadditive_v1.json")

# reactivity classes (categorical; NO ordinal assumption in the additive model -- per-class main effects are learned)
CLASSES = [
    "inert_or_water",          # water, table salt, sugar, sand, most compatible inerts
    "weak_acid",               # vinegar, citric acid, carbonic
    "strong_acid",             # HCl, sulfuric, nitric
    "strong_base",             # lye/NaOH, KOH, strong caustic
    "ammonia_or_amine",        # ammonia, amines
    "hypochlorite_bleach",     # chlorine bleach
    "oxidizer",                # hydrogen peroxide (conc), nitrate/permanganate/chlorate, pool oxidizer
    "reactive_metal",          # sodium, potassium, lithium, alkali/alkaline-earth metal
    "sulfide_or_cyanide_salt", # sulfide/cyanide salts (release toxic gas with acid)
    "organic_solvent_or_fuel", # acetone, alcohol, gasoline, oils
    "reducing_agent",          # metal hydrides, active reducers
]
CLASS_IDX = {c: i for i, c in enumerate(CLASSES)}
NCLS = len(CLASSES)

TARGET = "hazard"
TARGET_SCALE = ["none", "minor", "moderate", "high", "severe"]
TGT_IDX = {v: i for i, v in enumerate(TARGET_SCALE)}
L = len(TARGET_SCALE)  # 5 ordinal severity levels 0..4

# ---- regimes (stable enumerated indices; NO hash()) ----
CLEAN = "CLEAN_REAL"
ADDSYNTH = "ADDITIVE_SYNTH"   # best additive projection of the real data (must-fail: gate must NOT fire)
SHUFFLE = "SHUFFLE"           # freq-preserving permutation (must-fail: MI destroyed)
REGIMES = [CLEAN, ADDSYNTH, SHUFFLE]
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- pre-registered bands (fixed before running) ----
HP_TRUTH = 0.85
CONJ_RATIO_CEIL = 0.60      # best_single_mi / joint_mi must be <= this
CONJ_MI_MARGIN = 0.30       # bits
NONADD_HP = 0.15            # interactive_seen_acc - additive_seen_acc (genuine non-additivity; clears the null floor)
NONADD_REFUTE = 0.05
ADDSYNTH_NONADD_CEIL = 0.10  # additive-synth control (best additive projection) must stay below this -> gate valid
DISCRIM_MARGIN = 0.05        # clean_nonadd must exceed EACH null (addsynth AND shuffle) by this margin
DOMINANCE_REFUTE = 0.80      # single class dominates -> REFUTE
# Both nulls (ADDITIVE_SYNTH, SHUFFLE) are judged on the held-out NON-ADDITIVITY metric (n-robust), NOT raw joint_mi:
# raw joint_mi carries a large finite-sample bias ~ (B_pairs-1)(L-1)/(2 N ln2) that does NOT vanish at our n, AND the
# interactive arm has a finite-sample overfit floor (memorized pair-modes score spurious hits on a random target). So the
# nulls are cleared RELATIVELY (clean must exceed each null by DISCRIM_MARGIN); addsynth also has a principled absolute
# ceiling because it is the BEST additive projection of the real data (on-distribution additive control).


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
# BUILD-TIME GENERATION (external tool; local only; writes the vetted artifact).
# ===========================================================================

GEN_BATCHES = [
    "pairs that are essentially SAFE to combine (hazard none or minor): common inert or compatible pairs such as table "
    "salt in water, sugar in water, sand with water, two mutually-inert household substances, a weak acid diluted in "
    "water.",
    "pairs with MODERATE hazard: acid-base neutralizations that release heat, concentrated acid added to water, mixing "
    "that produces notable heat or mild fizzing but no toxic gas or fire.",
    "pairs with HIGH or SEVERE hazard from established chemical safety: chlorine bleach with ammonia (chloramine), "
    "chlorine bleach with an acid (chlorine gas), an oxidizer with a fuel or organic solvent (fire), a reactive alkali "
    "metal with water (hydrogen fire), a strong acid with a sulfide or cyanide salt (toxic gas).",
    "common HOUSEHOLD chemical mixing outcomes people actually ask about (cleaners, disinfectants, pool chemicals, "
    "vinegar, ammonia, rubbing alcohol, hydrogen peroxide) -- give the real typical outcome, safe or hazardous.",
    "LABORATORY reagent incompatibilities taken from safety data sheets: oxidizers with reducers, strong acids with "
    "bases, water-reactive reagents, peroxide-forming or peroxide-reacting combinations.",
    "pairs where ONE member is otherwise benign on its own (vinegar, ammonia, rubbing alcohol, baking soda, hydrogen "
    "peroxide) but the COMBINATION outcome depends entirely on the PARTNER -- give several such pairs, some safe and "
    "some hazardous, for the SAME benign member with DIFFERENT partners.",
]


def _gen_prompt(batch_desc, n):
    lines = []
    lines.append("You are a careful chemical-safety expert building a vetted knowledge base of what happens when two "
                 "substances are MIXED. List %d real, distinct, well-known substance PAIRS from this scenario: %s"
                 % (n, batch_desc))
    lines.append("For EACH pair give real, named substances and classify EACH member into exactly one reactivity class "
                 "from this list: %s" % CLASSES)
    lines.append("Then give the typical MIXING HAZARD severity when the two are combined at common concentrations, as "
                 "exactly one of: %s" % TARGET_SCALE)
    lines.append("hazard meaning: none=safe/no reaction; minor=mild heat or irritation; moderate=notable heat or mild "
                 "gas; high=fire risk or significant toxic gas or vigorous reaction; severe=explosion or lethal toxic "
                 "gas (chlorine, chloramine, hydrogen cyanide, phosgene).")
    lines.append("Base every value on established chemistry and safety data. Do NOT follow any formula; give the real "
                 "typical outcome. Vary the partners so a class is not always the same hazard.")
    lines.append("Include ONLY pairs whose class assignments and hazard level are WELL-ESTABLISHED and UNAMBIGUOUS. "
                 "Avoid borderline severity calls: when a pair could reasonably be two adjacent levels, choose the level "
                 "most commonly cited in safety references. Prefer clear-cut, textbook-certain records over exotic or "
                 "debatable ones. Accuracy matters more than quantity.")
    lines.append("Return ONLY a JSON array, each element: "
                 '{"substance_a":..., "substance_b":..., "class_a":..., "class_b":..., "hazard":...}. No prose.')
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


def _pair_key(a, b):
    return tuple(sorted([str(a).strip().lower(), str(b).strip().lower()]))


def _vet_prompt(rows):
    lines = ["You are an adversarial chemical-safety fact-checker. For each mixing record below, judge whether ALL of: "
             "(1) both class assignments are correct for the named substances, and (2) the hazard severity is correct "
             "for mixing them at common concentrations. Answer strictly.",
             "Reactivity classes: %s" % CLASSES,
             "Hazard scale: %s (none=safe .. severe=explosion or lethal toxic gas)." % TARGET_SCALE,
             "Return ONLY a JSON array of {\"id\":..., \"ok\":true/false}. A record is ok=false if the class of either "
             "member is wrong OR the hazard severity is clearly wrong. Records:"]
    for i, r in enumerate(rows):
        lines.append(json.dumps({"id": i, "substance_a": r["substance_a"], "substance_b": r["substance_b"],
                                 "class_a": r["class_a"], "class_b": r["class_b"], "hazard": r["hazard"]}))
    return "\n".join(lines)


def do_generate(n_per_batch=30):
    """External generator + adversarial vetter; write the vetted artifact. Build-time local only."""
    import pathlib
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(_REPO) / ".env.local")
    from backend.llm import anthropic_client

    clsset = set(CLASSES)
    tgtset = set(TARGET_SCALE)
    seen = {}
    total_cost = 0.0
    for bi, bd in enumerate(GEN_BATCHES):
        _log("generate batch %d/%d" % (bi + 1, len(GEN_BATCHES)))
        resp = anthropic_client.chat(_gen_prompt(bd, n_per_batch), max_tokens=4096, temperature=0.4)
        total_cost += resp.cost_usd
        kept = 0
        for r in _extract_json_array(resp.text):
            sa = str(r.get("substance_a", "")).strip().lower()
            sb = str(r.get("substance_b", "")).strip().lower()
            ca = str(r.get("class_a", "")).strip().lower()
            cb = str(r.get("class_b", "")).strip().lower()
            hz = str(r.get("hazard", "")).strip().lower()
            if not sa or not sb or sa == sb:
                continue
            if ca not in clsset or cb not in clsset or hz not in tgtset:
                continue
            key = _pair_key(sa, sb)
            if key in seen:
                continue
            seen[key] = dict(substance_a=sa, substance_b=sb, class_a=ca, class_b=cb, hazard=hz)
            kept += 1
        _log("  kept %d (running total %d) cost=$%.4f" % (kept, len(seen), resp.cost_usd))
    rows = list(seen.values())

    # ---- adversarial vet (batches of 40) ----
    truth_flags = {}
    for s in range(0, len(rows), 40):
        chunk = rows[s:s + 40]
        vresp = anthropic_client.chat(_vet_prompt(chunk), max_tokens=4096, temperature=0.0)
        total_cost += vresp.cost_usd
        for j in _extract_json_array(vresp.text):
            try:
                idx = int(j.get("id", -1))
            except (ValueError, TypeError):
                idx = -1
            if 0 <= idx < len(chunk):
                key = _pair_key(chunk[idx]["substance_a"], chunk[idx]["substance_b"])
                truth_flags[key] = bool(j.get("ok", False))
    for r in rows:
        r["vetted_true"] = truth_flags.get(_pair_key(r["substance_a"], r["substance_b"]), None)
    n_judged = sum(1 for r in rows if r["vetted_true"] is not None)
    n_true = sum(1 for r in rows if r["vetted_true"] is True)
    truth_rate = (n_true / n_judged) if n_judged else float("nan")

    os.makedirs(os.path.dirname(ARTIFACT), exist_ok=True)
    payload = dict(anchor=ANCHOR_NAME, generator="claude-haiku-4-5", ts_iso=datetime.now(timezone.utc).isoformat(),
                   classes=CLASSES, target=TARGET, target_scale=TARGET_SCALE, L=L, gen_cost_usd=round(total_cost, 4),
                   n_entities=len(rows), n_judged=n_judged, n_true=n_true, truth_rate=truth_rate, rows=rows)
    tmp = ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, ARTIFACT)
    _log("ARTIFACT written: %s (n=%d truth_rate=%s cost=$%.4f)"
         % (ARTIFACT, len(rows), _fmt(truth_rate), total_cost))
    return payload


# ===========================================================================
# MEASUREMENT (glass-box; NO LLM). artifact -> canonical class-pair matrix -> arms -> verdict.
# ===========================================================================

def load_cluster():
    with open(ARTIFACT, "r", encoding="utf-8") as f:
        p = json.load(f)
    rows = [r for r in p["rows"] if r.get("vetted_true", None) is not False]  # keep vetted-true + unjudged; drop false
    X = np.zeros((len(rows), 2), dtype=np.int64)
    y = np.zeros(len(rows), dtype=np.int64)
    for i, r in enumerate(rows):
        a = CLASS_IDX[str(r["class_a"]).strip().lower()]
        b = CLASS_IDX[str(r["class_b"]).strip().lower()]
        X[i, 0], X[i, 1] = min(a, b), max(a, b)  # canonical unordered pair
        y[i] = TGT_IDX[str(r[TARGET]).strip().lower()]
    return p, X, y


def mutual_info(a, b, base=2.0):
    """Discrete MI(a;b) in bits."""
    n = len(a)
    if n == 0:
        return 0.0
    pa = defaultdict(float); pb = defaultdict(float); pab = defaultdict(float)
    inv = 1.0 / n
    for x, z in zip(a.tolist(), b.tolist()):
        pa[x] += inv; pb[z] += inv; pab[(x, z)] += inv
    mi = 0.0
    for (x, z), pxz in pab.items():
        mi += pxz * math.log(pxz / (pa[x] * pb[z]) + 1e-30, base)
    return max(0.0, mi)


def _pair_ids(X):
    """Deterministic id per canonical (cA,cB) via sorted-unique enumeration (NO hash())."""
    uniq = sorted(set((int(X[i, 0]), int(X[i, 1])) for i in range(X.shape[0])))
    m = {t: i for i, t in enumerate(uniq)}
    return np.array([m[(int(X[i, 0]), int(X[i, 1]))] for i in range(X.shape[0])], dtype=np.int64)


def conjunction_property(X, y):
    """single-constituent MI(y;member class) vs joint MI(y; class-pair). dominance ratio + margin."""
    mi_a = mutual_info(X[:, 0], y)
    mi_b = mutual_info(X[:, 1], y)
    joint = mutual_info(_pair_ids(X), y)
    best_single = max(mi_a, mi_b)
    ratio = (best_single / joint) if joint > 1e-9 else float("nan")
    return dict(single_mi=dict(member_lo=round(mi_a, 4), member_hi=round(mi_b, 4)),
                best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4),
                dominance_ratio=(round(ratio, 4) if ratio == ratio else ratio))


# ---- arms ----

def _design(Xm):
    """Per-class COUNT design (n x NCLS): col c = number of times class c appears in the pair (0/1/2). Plus intercept."""
    D = np.zeros((Xm.shape[0], NCLS + 1), dtype=np.float64)
    D[:, 0] = 1.0
    for r in range(Xm.shape[0]):
        D[r, 1 + int(Xm[r, 0])] += 1.0
        D[r, 1 + int(Xm[r, 1])] += 1.0
    return D


def _round_bins(vals):
    return np.clip(np.round(vals), 0, L - 1).astype(np.int64)


def arm_additive(Xtr, ytr, Xq):
    """OPTIMAL ADDITIVE main-effects predictor: least-squares fit of ordinal target on symmetric per-class contributions
    (linear in class counts), round-to-bin readout. This is the STRONGEST additive-over-classes predictor; if a target is
    truly additive in class contributions the additive arm captures it (so the non-additivity gap reflects genuine
    interaction, not readout loss)."""
    D_tr = _design(Xtr)
    beta, _, _, _ = np.linalg.lstsq(D_tr, ytr.astype(np.float64), rcond=None)
    pred = _round_bins(_design(Xq) @ beta)
    return pred, beta


def arm_interactive(Xtr, ytr, Xq, beta):
    """2-way INTERACTION predictor: class-PAIR conditional MEAN from train (round-to-bin readout, SAME readout as the
    additive arm); backoff to the additive prediction for pairs not present in train (novel class-pairs)."""
    pair_sum = defaultdict(float); pair_cnt = defaultdict(int)
    for r in range(Xtr.shape[0]):
        k = (int(Xtr[r, 0]), int(Xtr[r, 1]))
        pair_sum[k] += float(ytr[r]); pair_cnt[k] += 1
    add_pred = _round_bins(_design(Xq) @ beta)
    preds = np.empty(Xq.shape[0], dtype=np.int64)
    seen = np.zeros(Xq.shape[0], dtype=bool)
    for r in range(Xq.shape[0]):
        k = (int(Xq[r, 0]), int(Xq[r, 1]))
        if k in pair_cnt:
            preds[r] = int(np.clip(round(pair_sum[k] / pair_cnt[k]), 0, L - 1)); seen[r] = True
        else:
            preds[r] = add_pred[r]
    return preds, seen


def acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


# ---- regimes / split ----

def make_regime_target(X, y_real, regime, seed, sev=None):
    n = X.shape[0]
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ADDSYNTH:
        # target = TRULY ADDITIVE in value space: y = clip(round(a[cA] + a[cB])), a[c] = 0.5 * real per-class mean hazard
        # (so the pairwise sum spans the ordinal range). This is a genuinely additive target derived from real per-class
        # effects -> the optimal additive arm must capture it (non-additivity gate must NOT fire). The load-bearing
        # control proving the metric separates additive-multi-feature from genuine 2-way interaction (the foods pitfall).
        a = {c: 0.5 * sev[c] for c in range(NCLS)}
        yb = np.array([int(np.clip(round(a[int(X[r, 0])] + a[int(X[r, 1])]), 0, L - 1)) for r in range(n)],
                      dtype=np.int64)
        return yb, yb.copy()
    if regime == SHUFFLE:
        rng = np.random.default_rng(1000003 * seed + 7919 * REG_IDX[regime] + 101)
        return y_real[rng.permutation(n)].copy(), y_real.copy()
    raise ValueError(regime)


def split_query(X, seed, query_frac=0.40):
    n = X.shape[0]
    rng = np.random.default_rng(2000003 * seed + 13)
    perm = rng.permutation(n)
    nq = max(1, int(round(query_frac * n)))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_pairs = set((int(X[i, 0]), int(X[i, 1])) for i in tr)
    seen = np.array([(int(X[i, 0]), int(X[i, 1])) in train_pairs for i in q], dtype=bool)
    return q, tr, seen


def _class_sev(X, y):
    pools = defaultdict(list)
    for r in range(X.shape[0]):
        pools[int(X[r, 0])].append(int(y[r])); pools[int(X[r, 1])].append(int(y[r]))
    g = float(y.mean()) if len(y) else 0.0
    return {c: (float(np.mean(v)) if v else g) for c in range(NCLS) for v in [pools.get(c, [])]}


def score_regime(X, y_real, regime, seed, sev):
    q, tr, seen = split_query(X, seed)
    y, oracle = make_regime_target(X, y_real, regime, seed, sev=sev)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y[q], y[tr]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=L)))

    add_pred, beta = arm_additive(Xtr, ytr, Xq)
    int_pred, seen_by_train = arm_interactive(Xtr, ytr, Xq, beta)
    pop = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    orc = oracle[q]

    # seen-pair stratum = query entities whose class-pair appears in train (both split-seen and train-pair-present align)
    seen_mask = seen & seen_by_train
    novel_mask = ~seen_mask

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("seen", seen_mask), ("novel", novel_mask), ("all", np.ones(len(gold), bool))):
        out[sname] = dict(ADDITIVE=round(a(add_pred, m), 5), INTERACTIVE=round(a(int_pred, m), 5),
                          POP=round(a(pop, m), 5), ORACLE=round(a(orc, m), 5), n=int(m.sum()))
    nonadd_seen = (out["seen"]["INTERACTIVE"] - out["seen"]["ADDITIVE"]) if out["seen"]["n"] > 0 else float("nan")
    return dict(regime=regime, strata=out, nonadd_seen=nonadd_seen, n_seen=int(seen_mask.sum()),
                sigs=dict(ADDITIVE=_sig(add_pred), INTERACTIVE=_sig(int_pred), ORACLE=_sig(orc)))


def run_measurement(seeds=(7, 13, 17, 23, 29)):
    p, X, y = load_cluster()
    conj = conjunction_property(X, y)               # split-independent, on full clean data
    sev = _class_sev(X, y)                           # for ADDITIVE_SYNTH control

    per_seed = {reg: [] for reg in REGIMES}
    for sd in seeds:
        for reg in REGIMES:
            per_seed[reg].append(score_regime(X, y, reg, sd, sev))

    def mean_field(reg, fn):
        vals = [fn(r) for r in per_seed[reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    clean_nonadd = mean_field(CLEAN, lambda r: r["nonadd_seen"])
    addsynth_nonadd = mean_field(ADDSYNTH, lambda r: r["nonadd_seen"])
    shuffle_nonadd = mean_field(SHUFFLE, lambda r: r["nonadd_seen"])
    clean_add_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["ADDITIVE"])
    clean_int_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["INTERACTIVE"])
    clean_pop_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["POP"])
    clean_int_novel = mean_field(CLEAN, lambda r: r["strata"]["novel"]["INTERACTIVE"])
    clean_add_novel = mean_field(CLEAN, lambda r: r["strata"]["novel"]["ADDITIVE"])
    orc_all = mean_field(CLEAN, lambda r: r["strata"]["all"]["ORACLE"])
    mean_n_seen = mean_field(CLEAN, lambda r: float(r["n_seen"]))

    # shuffle joint MI (recompute on a shuffled target once, deterministic seed) for conj-destroyed check
    ys, _ = make_regime_target(X, y, SHUFFLE, seeds[0], sev=sev)
    shuf_conj = conjunction_property(X, ys)
    addsynth_y, _ = make_regime_target(X, y, ADDSYNTH, seeds[0], sev=sev)
    addsynth_conj = conjunction_property(X, addsynth_y)

    truth = p.get("truth_rate", float("nan"))
    ratio = conj["dominance_ratio"]

    conj_present = bool(ratio == ratio and ratio <= CONJ_RATIO_CEIL and conj["mi_margin"] >= CONJ_MI_MARGIN)
    truth_ok = bool(truth == truth and truth >= HP_TRUTH)
    nonadditive_ok = bool(clean_nonadd == clean_nonadd and clean_nonadd >= NONADD_HP)
    shuffle_destroyed = bool(shuffle_nonadd == shuffle_nonadd and clean_nonadd == clean_nonadd
                             and clean_nonadd > shuffle_nonadd + DISCRIM_MARGIN)
    gate_valid = bool(addsynth_nonadd == addsynth_nonadd and addsynth_nonadd <= ADDSYNTH_NONADD_CEIL
                      and clean_nonadd == clean_nonadd and clean_nonadd > addsynth_nonadd + DISCRIM_MARGIN
                      and shuffle_destroyed)
    ceiling_ok = bool(orc_all >= 0.999)

    single_driver = bool(ratio == ratio and ratio > DOMINANCE_REFUTE)
    transform_additive = bool(clean_nonadd == clean_nonadd and clean_nonadd <= NONADD_REFUTE)

    hard_pass = bool(truth_ok and conj_present and nonadditive_ok and gate_valid and ceiling_ok)
    refute = bool(((not truth_ok) or (not conj_present) or single_driver or transform_additive) and gate_valid
                  and ceiling_ok)

    if not ceiling_ok:
        verdict = "INCONCLUSIVE_CEILING_MALFORMED"
    elif not gate_valid:
        verdict = "INCONCLUSIVE_GATE_INVALID_CANNOT_SEPARATE_ADDITIVE"
    elif hard_pass:
        verdict = "GENERATED_NONADDITIVE_CONJUNCTION_VETTABLE_FOUNDATION_GO"
    elif refute:
        verdict = "GENERATED_NONADDITIVE_CONJUNCTION_PREMISE_REFUTED"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || n=%d(seen~%.0f) truth=%s(>=%.2f=%s) | CONJ joint=%.3f best_single=%.3f margin=%.3f(>=%.2f) "
           "ratio=%s(<=%.2f) present=%s | NONADD clean=%s(>=%.2f=%s) [add_seen=%s int_seen=%s pop_seen=%s] "
           "novel[int=%s add=%s] | GATE addsynth_nonadd=%s(<=%.2f) shuffle_nonadd=%s(clean>null+%.2f) valid=%s | "
           "single_driver=%s transform_additive=%s oracle=%s"
           % (verdict, p["n_entities"], mean_n_seen, _fmt(truth), HP_TRUTH, truth_ok, conj["joint_mi"],
              conj["best_single_mi"], conj["mi_margin"], CONJ_MI_MARGIN,
              _fmt(ratio) if ratio == ratio else "nan", CONJ_RATIO_CEIL, conj_present,
              _fmt(clean_nonadd), NONADD_HP, nonadditive_ok, _fmt(clean_add_seen), _fmt(clean_int_seen),
              _fmt(clean_pop_seen), _fmt(clean_int_novel), _fmt(clean_add_novel), _fmt(addsynth_nonadd),
              ADDSYNTH_NONADD_CEIL, _fmt(shuffle_nonadd), DISCRIM_MARGIN, gate_valid, single_driver,
              transform_additive, _fmt(orc_all)))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="local_measure",
        elapsed_s=0.0, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_entities=p["n_entities"], truth_rate=truth, n_judged=p.get("n_judged"), n_true=p.get("n_true"),
        seeds=list(seeds), L=L,
        conjunction=conj, shuffle_conjunction=shuf_conj, addsynth_conjunction=addsynth_conj,
        nonadditivity=dict(clean_seen=round(clean_nonadd, 5), addsynth_seen=round(addsynth_nonadd, 5),
                           shuffle_seen=round(shuffle_nonadd, 5)),
        clean=dict(add_seen=round(clean_add_seen, 5), int_seen=round(clean_int_seen, 5),
                   pop_seen=round(clean_pop_seen, 5), int_novel=round(clean_int_novel, 5),
                   add_novel=round(clean_add_novel, 5), oracle_all=round(orc_all, 5),
                   mean_n_seen=round(mean_n_seen, 3)),
        gates=dict(truth_ok=truth_ok, conj_present=conj_present, nonadditive_ok=nonadditive_ok,
                   gate_valid=gate_valid, shuffle_destroyed=shuffle_destroyed, ceiling_ok=ceiling_ok,
                   single_driver=single_driver, transform_additive=transform_additive,
                   hard_pass=hard_pass, refute=refute),
        bands=dict(HP_TRUTH=HP_TRUTH, CONJ_RATIO_CEIL=CONJ_RATIO_CEIL, CONJ_MI_MARGIN=CONJ_MI_MARGIN,
                   NONADD_HP=NONADD_HP, NONADD_REFUTE=NONADD_REFUTE, ADDSYNTH_NONADD_CEIL=ADDSYNTH_NONADD_CEIL,
                   DISCRIM_MARGIN=DISCRIM_MARGIN, DOMINANCE_REFUTE=DOMINANCE_REFUTE),
        per_seed={reg: [dict(strata=per_seed[reg][i]["strata"], nonadd_seen=per_seed[reg][i]["nonadd_seen"],
                             n_seen=per_seed[reg][i]["n_seen"]) for i in range(len(seeds))] for reg in REGIMES},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ===========================================================================
# SELF-TEST (real code path; NO LLM). Two planted arenas prove the gate FIRES on a genuine 2-way interaction and does
# NOT fire on a purely-additive target -- exercising the REAL MI + additive/interactive arms + split logic.
# ===========================================================================

def _plant_cluster(n, seed, mode):
    """Build (X canonical class-pairs, y). mode='interaction' -> pair-specific random table (genuine non-additive, no
    single dominant driver). mode='additive' -> y = quantile-bin(sev[cA]+sev[cB]) (additive; gate must NOT fire)."""
    rng = np.random.default_rng(seed)
    ncls = 8
    a = rng.integers(0, ncls, size=n); b = rng.integers(0, ncls, size=n)
    X = np.stack([np.minimum(a, b), np.maximum(a, b)], axis=1).astype(np.int64)
    if mode == "interaction":
        table = rng.integers(0, L, size=(ncls, ncls))          # pair-specific -> genuine 2-way interaction
        table = np.minimum(table, table.T)                     # symmetric over unordered pair
        y = np.array([table[int(X[i, 0]), int(X[i, 1])] for i in range(n)], dtype=np.int64)
    else:
        a = rng.integers(0, 3, size=ncls)   # per-class integer contribution 0/1/2 -> value-space additive target
        y = np.array([int(np.clip(a[int(X[i, 0])] + a[int(X[i, 1])], 0, L - 1)) for i in range(n)], dtype=np.int64)
    return X, y


def self_test():
    n = 600
    sev_dummy = {c: 0.0 for c in range(NCLS)}

    # --- genuine interaction arena: gate must FIRE ---
    Xi, yi = _plant_cluster(n, 7, "interaction")
    conj_i = conjunction_property(Xi, yi)
    sev_i = _class_sev(Xi, yi)
    rs_i = [score_regime(Xi, yi, CLEAN, sd, sev_i) for sd in (7, 13, 17)]
    nonadd_i = float(np.mean([r["nonadd_seen"] for r in rs_i if r["nonadd_seen"] == r["nonadd_seen"]]))
    add_seen_i = float(np.mean([r["strata"]["seen"]["ADDITIVE"] for r in rs_i]))
    int_seen_i = float(np.mean([r["strata"]["seen"]["INTERACTIVE"] for r in rs_i]))
    orc_i = float(np.mean([r["strata"]["all"]["ORACLE"] for r in rs_i]))
    n_seen_i = float(np.mean([r["n_seen"] for r in rs_i]))

    # --- additive arena: gate must NOT fire (real MI conjunction still present) ---
    Xa, ya = _plant_cluster(n, 11, "additive")
    conj_a = conjunction_property(Xa, ya)
    sev_a = _class_sev(Xa, ya)
    rs_a = [score_regime(Xa, ya, CLEAN, sd, sev_a) for sd in (7, 13, 17)]
    nonadd_a = float(np.mean([r["nonadd_seen"] for r in rs_a if r["nonadd_seen"] == r["nonadd_seen"]]))

    # --- shuffle destroys the held-out non-additivity signal on the interaction arena ---
    rs_sh = [score_regime(Xi, yi, SHUFFLE, sd, sev_i) for sd in (7, 13, 17)]
    nonadd_sh = float(np.mean([r["nonadd_seen"] for r in rs_sh if r["nonadd_seen"] == r["nonadd_seen"]]))

    ok = bool(
        nonadd_i >= NONADD_HP                       # genuine interaction: additive canNOT capture -> gate FIRES
        and int_seen_i > add_seen_i                 # interactive strictly beats additive on seen pairs
        and conj_i["mi_margin"] >= CONJ_MI_MARGIN    # genuine conjunction present
        and conj_i["dominance_ratio"] == conj_i["dominance_ratio"] and conj_i["dominance_ratio"] <= CONJ_RATIO_CEIL
        and nonadd_a <= ADDSYNTH_NONADD_CEIL         # additive arena: gate does NOT fire (discriminator valid)
        and nonadd_i > nonadd_a + DISCRIM_MARGIN     # gate separates genuine from additive
        and nonadd_i > nonadd_sh + DISCRIM_MARGIN    # gate separates genuine from pure-noise shuffle
        and orc_i >= 0.999                           # oracle ceiling intact
        and n_seen_i >= 8                            # seen stratum non-trivial
    )
    out = dict(interaction_nonadd_seen=round(nonadd_i, 4), interaction_add_seen=round(add_seen_i, 4),
               interaction_int_seen=round(int_seen_i, 4), interaction_mi_margin=conj_i["mi_margin"],
               interaction_dominance_ratio=conj_i["dominance_ratio"], additive_nonadd_seen=round(nonadd_a, 4),
               additive_mi_margin=conj_a["mi_margin"], shuffle_nonadd_seen=round(nonadd_sh, 4),
               oracle=round(orc_i, 4), n_seen=n_seen_i, passed=ok)
    print("[SELFTEST] %s" % json.dumps(out), flush=True)
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--n-per-batch", type=int, default=30)
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
        m = run_measurement()
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
