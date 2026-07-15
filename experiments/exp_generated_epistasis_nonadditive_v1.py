"""GENERATED_EPISTASIS_NONADDITIVE (v1): foundation-build of a GENUINELY non-additive vettable cluster from a TRUE
interaction pocket (genetic EPISTASIS / synthetic lethality), gated against a STRONG capacity-matched CATEGORICAL additive.

WHY (revival of the chem_bind_readout REFUTE per skunkworks VET a2f9a9e8): the mechanism is HEALTHY (on ARBITRARY-seen pure
non-additive labels SYM=1.000 vs ADD=0.830); the prior REFUTE was a DATA/foundation gate -- SDS mixing-hazard is ~98%
main-effects vs a STRONG categorical additive (non-additivity +0.022 vs strong categorical, though +0.42 vs the WEAK
ordinal-lstsq). Two foundation fixes, both here: (1) STRONG non-additivity gate = multinomial-logistic-on-counts CATEGORICAL
additive (NOT weak ordinal-lstsq); (2) genuine-interaction pocket = genetic epistasis / synthetic lethality (pure AND-gate:
single-KO viable, double-KO lethal), generated with a STRONGER model (claude-sonnet-4-5).

POCKET: gene PAIRS; constituent = functional pathway CLASS of each gene (canonical-sorted unordered); TARGET = negative
genetic-interaction SEVERITY of the double perturbation (none/mild/moderate/severe/lethal). With FINE-grained repair
sub-pathway classes, "count of DNA-repair genes" is NOT a usable additive feature: HR+NHEJ (redundant DSB repair) -> lethal
while HR+MMR (different lesions) -> none, both "2 DNA-repair genes". Outcome is set by the class-PAIR redundancy relationship,
not per-class main effects -> genuinely non-additive vs a strong categorical additive. Single-KO viable by construction ->
per-class marginal is weak. We MEASURE genuineness (do NOT plant the real target).

GLASS-BOX: generation is BUILD-TIME-LOCAL (external LLM + adversarial vet). Measurement is glass-box CPU, NO LLM.

STRONG additive (the load-bearing fix): arm_additive_cat = multinomial logistic (softmax) on the per-class COUNT design,
deterministic zero-init full-batch GD (no RNG). Non-additivity = interactive_seen - max(add_lstsq_seen, add_cat_seen).

CONTROL REGIMES: CLEAN(real) ; ADDITIVE_SYNTH (target = clip(round(a[cA]+a[cB])) from real per-class means -> additive CAN
capture it: gate must NOT fire) ; SHUFFLE (freq-preserving permutation -> MI destroyed). PRE-REGISTERED BANDS: see
preregs/2026-07-15_epistasis_bind_readout_transfer.md.

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

ANCHOR_NAME = "generated_epistasis_nonadditive_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "epistasis_pair_interaction_nonadditive_v1.json")
GEN_MODEL = "claude-sonnet-4-5"

# functional pathway classes (categorical; fine-grained repair sub-pathways so 'count of repair genes' is NOT additive)
CLASSES = [
    "dna_repair_hr",            # homologous recombination: BRCA1, BRCA2, RAD51, RAD54, PALB2
    "dna_repair_nhej",          # non-homologous end joining: KU70, KU80, LIG4, DNAPKcs, XRCC4
    "dna_repair_ber_parp",      # base excision / single-strand: PARP1, XRCC1, POLB, APE1
    "dna_repair_mmr",           # mismatch repair: MSH2, MLH1, MSH6, PMS2
    "dna_repair_ner",           # nucleotide excision: XPA, ERCC1, XPC, XPF
    "dna_damage_checkpoint",    # ATM, ATR, CHK1, CHK2, WEE1
    "cell_cycle_core",          # CDK1, cyclins, RB1, CDC20, APC
    "chromatin_remodeling",     # SWI/SNF (ARID1A, SMARCA4), histone modifiers, INO80
    "spindle_mitosis",          # kinetochore / spindle checkpoint: MAD2, BUB1, AURKB, kinesins
    "proteostasis_autophagy",   # proteasome subunits, autophagy (ATG), chaperones
    "metabolism_general",       # glycolysis, TCA, nucleotide/lipid metabolism
    "signaling_growth",         # RAS, PI3K, MAPK, MYC growth/proliferation signaling
]
CLASS_IDX = {c: i for i, c in enumerate(CLASSES)}
NCLS = len(CLASSES)

TARGET = "interaction"
TARGET_SCALE = ["none", "mild", "moderate", "severe", "lethal"]
TGT_IDX = {v: i for i, v in enumerate(TARGET_SCALE)}
L = len(TARGET_SCALE)  # 5 negative-interaction severity levels 0..4

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
STRONG_NONADD_HP = 0.12     # interactive_seen - max(add_lstsq_seen, add_cat_seen)  (STRONG bar; the load-bearing fix)
NONADD_REFUTE = 0.05
ADDSYNTH_NONADD_CEIL = 0.10  # additive-synth control (best additive projection) must stay below this -> gate valid
DISCRIM_MARGIN = 0.05        # clean_nonadd must exceed EACH null (addsynth AND shuffle) by this margin
DOMINANCE_REFUTE = 0.80      # single class dominates -> REFUTE
# Both nulls (ADDITIVE_SYNTH, SHUFFLE) judged on the held-out NON-ADDITIVITY metric (n-robust), cleared RELATIVELY
# (clean must exceed each null by DISCRIM_MARGIN); addsynth also has a principled absolute ceiling (best additive
# projection of the real data = on-distribution additive control).


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
    "gene pairs with NO genetic interaction (interaction=none): two genes in UNRELATED cellular processes whose double "
    "mutant is essentially as expected from the singles -- e.g. a DNA-repair gene paired with a general metabolism or "
    "growth-signaling gene, or two genes in the SAME linear pathway where one is epistatic to the other (no extra defect).",
    "gene pairs with a MILD or MODERATE negative genetic interaction: double mutants that are noticeably sicker or slower-"
    "growing than expected but still viable -- partially overlapping functions, a checkpoint gene with a repair gene, "
    "buffering relationships that are real but not lethal.",
    "SYNTHETIC LETHAL and SEVERE gene pairs from well-established genetics: BRCA1 or BRCA2 (homologous recombination) with "
    "PARP1 (base excision) -> synthetic lethal; two parallel/redundant DNA double-strand-break repair routes (HR with NHEJ); "
    "a DNA-damage checkpoint gene with a repair gene; redundant paralog pairs where losing both is lethal.",
    "gene pairs where ONE gene is otherwise tolerant to knockout on its own (viable single mutant) but the double mutant "
    "outcome depends ENTIRELY on the PARTNER -- give several pairs for the SAME gene or SAME pathway with DIFFERENT "
    "partners, some with no interaction and some synthetic lethal, so a class is not always the same interaction level.",
    "classic yeast and mammalian genetic-interaction / synthetic-lethality screen results across chromatin remodeling, "
    "spindle/mitosis checkpoint, proteostasis, and cell-cycle-core genes paired with DNA-repair or checkpoint genes.",
    "gene pairs within DNA repair that are NOT redundant and show little or no interaction (e.g. mismatch repair with "
    "homologous recombination, nucleotide-excision repair with non-homologous end joining), to contrast with the redundant "
    "pairs that are synthetic lethal -- give the real established outcome for each.",
]


def _gen_prompt(batch_desc, n):
    lines = []
    lines.append("You are a careful cancer-genetics and functional-genomics expert building a vetted knowledge base of "
                 "GENETIC INTERACTIONS between gene pairs (what happens to a cell's fitness when BOTH genes are lost / "
                 "knocked out, relative to losing each alone). List %d real, distinct, well-established gene PAIRS from this "
                 "scenario: %s" % (n, batch_desc))
    lines.append("For EACH pair give real, named human or model-organism genes and classify EACH gene into exactly one "
                 "functional pathway class from this list: %s" % CLASSES)
    lines.append("Then give the negative genetic-interaction SEVERITY of the DOUBLE loss-of-function (both genes knocked "
                 "out), as exactly one of: %s" % TARGET_SCALE)
    lines.append("severity meaning: none=genes act independently, double mutant fitness is as expected from the singles "
                 "(no genetic interaction); mild=slightly sicker than expected; moderate=clearly sick / strong growth "
                 "defect double mutant; severe=very sick / near-inviable double mutant; lethal=SYNTHETIC LETHAL, double "
                 "mutant is inviable/dead while each single mutant is viable.")
    lines.append("Only include pairs where each SINGLE knockout is viable (so the double outcome is a genuine genetic "
                 "interaction, not just one gene being essential). Base every value on established genetics / published "
                 "synthetic-lethality or genetic-interaction screens. Do NOT follow any formula; give the real established "
                 "outcome. Vary the partners so a pathway class is not always the same interaction level.")
    lines.append("Include ONLY pairs whose class assignments and interaction severity are WELL-ESTABLISHED and "
                 "UNAMBIGUOUS. Avoid borderline calls: when a pair could reasonably be two adjacent levels, choose the "
                 "level most commonly reported. Prefer clear-cut, textbook-certain records over exotic or debatable ones. "
                 "Accuracy matters more than quantity.")
    lines.append("Return ONLY a JSON array, each element: "
                 '{"gene_a":..., "gene_b":..., "class_a":..., "class_b":..., "interaction":...}. No prose.')
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
    lines = ["You are an adversarial functional-genomics fact-checker. For each genetic-interaction record below, judge "
             "whether ALL of: (1) both functional-class assignments are correct for the named genes, (2) each single "
             "knockout is genuinely viable (so a genetic interaction is meaningful), and (3) the negative genetic-"
             "interaction severity is correct for the DOUBLE loss-of-function. Answer strictly.",
             "Functional classes: %s" % CLASSES,
             "Severity scale: %s (none=independent .. lethal=synthetic lethal, double inviable while singles viable)."
             % TARGET_SCALE,
             "Return ONLY a JSON array of {\"id\":..., \"ok\":true/false}. A record is ok=false if either class is wrong, "
             "or a single knockout is actually lethal on its own, OR the interaction severity is clearly wrong. Records:"]
    for i, r in enumerate(rows):
        lines.append(json.dumps({"id": i, "gene_a": r["gene_a"], "gene_b": r["gene_b"],
                                 "class_a": r["class_a"], "class_b": r["class_b"], "interaction": r["interaction"]}))
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
        _log("generate batch %d/%d (model=%s)" % (bi + 1, len(GEN_BATCHES), GEN_MODEL))
        resp = anthropic_client.chat(_gen_prompt(bd, n_per_batch), model=GEN_MODEL, max_tokens=6000, temperature=0.4)
        total_cost += resp.cost_usd
        kept = 0
        for r in _extract_json_array(resp.text):
            ga = str(r.get("gene_a", "")).strip().lower()
            gb = str(r.get("gene_b", "")).strip().lower()
            ca = str(r.get("class_a", "")).strip().lower()
            cb = str(r.get("class_b", "")).strip().lower()
            it = str(r.get("interaction", "")).strip().lower()
            if not ga or not gb or ga == gb:
                continue
            if ca not in clsset or cb not in clsset or it not in tgtset:
                continue
            key = _pair_key(ga, gb)
            if key in seen:
                continue
            seen[key] = dict(gene_a=ga, gene_b=gb, class_a=ca, class_b=cb, interaction=it)
            kept += 1
        _log("  kept %d (running total %d) cost=$%.4f" % (kept, len(seen), resp.cost_usd))
    rows = list(seen.values())

    # ---- adversarial vet (batches of 40) ----
    truth_flags = {}
    for s in range(0, len(rows), 40):
        chunk = rows[s:s + 40]
        vresp = anthropic_client.chat(_vet_prompt(chunk), model=GEN_MODEL, max_tokens=4096, temperature=0.0)
        total_cost += vresp.cost_usd
        for j in _extract_json_array(vresp.text):
            try:
                idx = int(j.get("id", -1))
            except (ValueError, TypeError):
                idx = -1
            if 0 <= idx < len(chunk):
                key = _pair_key(chunk[idx]["gene_a"], chunk[idx]["gene_b"])
                truth_flags[key] = bool(j.get("ok", False))
    for r in rows:
        r["vetted_true"] = truth_flags.get(_pair_key(r["gene_a"], r["gene_b"]), None)
    n_judged = sum(1 for r in rows if r["vetted_true"] is not None)
    n_true = sum(1 for r in rows if r["vetted_true"] is True)
    truth_rate = (n_true / n_judged) if n_judged else float("nan")

    os.makedirs(os.path.dirname(ARTIFACT), exist_ok=True)
    payload = dict(anchor=ANCHOR_NAME, generator=GEN_MODEL, ts_iso=datetime.now(timezone.utc).isoformat(),
                   classes=CLASSES, target=TARGET, target_scale=TARGET_SCALE, L=L, gen_cost_usd=round(total_cost, 4),
                   n_entities=len(rows), n_judged=n_judged, n_true=n_true, truth_rate=truth_rate, rows=rows)
    tmp = ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, ARTIFACT)
    _log("ARTIFACT written: %s (n=%d n_true=%d truth_rate=%s cost=$%.4f)"
         % (ARTIFACT, len(rows), n_true, _fmt(truth_rate), total_cost))
    return payload


# ===========================================================================
# MEASUREMENT (glass-box; NO LLM).
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
    uniq = sorted(set((int(X[i, 0]), int(X[i, 1])) for i in range(X.shape[0])))
    m = {t: i for i, t in enumerate(uniq)}
    return np.array([m[(int(X[i, 0]), int(X[i, 1]))] for i in range(X.shape[0])], dtype=np.int64)


def conjunction_property(X, y):
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
    """Per-class COUNT design (n x NCLS+1): col 1+c = count of class c in the pair (0/1/2); col0 intercept."""
    D = np.zeros((Xm.shape[0], NCLS + 1), dtype=np.float64)
    D[:, 0] = 1.0
    for r in range(Xm.shape[0]):
        D[r, 1 + int(Xm[r, 0])] += 1.0
        D[r, 1 + int(Xm[r, 1])] += 1.0
    return D


def _round_bins(vals):
    return np.clip(np.round(vals), 0, L - 1).astype(np.int64)


def arm_additive_lstsq(Xtr, ytr, Xq):
    """WEAK additive baseline: ordinal least-squares on per-class contributions, round-to-bin (treats target as ordinal)."""
    beta, _, _, _ = np.linalg.lstsq(_design(Xtr), ytr.astype(np.float64), rcond=None)
    return _round_bins(_design(Xq) @ beta), beta


def arm_additive_cat(Xtr, ytr, Xq, iters=500, lr=0.5, l2=1e-3):
    """STRONG additive baseline (Fix 1): multinomial logistic (softmax) regression on the per-class COUNT design ->
    STRONGEST main-effects-only CATEGORICAL additive (no ordinal assumption, no round-to-bin loss). Deterministic
    zero-init full-batch GD (NO RNG -> PROT-023 clean)."""
    D = _design(Xtr); n, pdim = D.shape
    W = np.zeros((pdim, L), dtype=np.float64)
    Yoh = np.zeros((n, L), dtype=np.float64); Yoh[np.arange(n), ytr] = 1.0
    for _ in range(iters):
        Z = D @ W; Z -= Z.max(axis=1, keepdims=True)
        P = np.exp(Z); P /= P.sum(axis=1, keepdims=True)
        grad = D.T @ (P - Yoh) / n + l2 * W
        W -= lr * grad
    return np.argmax(_design(Xq) @ W, axis=1).astype(np.int64)


def arm_interactive(Xtr, ytr, Xq, beta):
    """2-way INTERACTION predictor: class-PAIR conditional MEAN from train (round-to-bin), backoff to the additive
    prediction for pairs not present in train (novel class-pairs)."""
    pair_sum = defaultdict(float); pair_cnt = defaultdict(int)
    for r in range(Xtr.shape[0]):
        k = (int(Xtr[r, 0]), int(Xtr[r, 1]))
        pair_sum[k] += float(ytr[r]); pair_cnt[k] += 1
    add_pred = _round_bins(_design(Xq) @ beta)
    preds = np.empty(Xq.shape[0], dtype=np.int64)
    for r in range(Xq.shape[0]):
        k = (int(Xq[r, 0]), int(Xq[r, 1]))
        if k in pair_cnt:
            preds[r] = int(np.clip(round(pair_sum[k] / pair_cnt[k]), 0, L - 1))
        else:
            preds[r] = add_pred[r]
    return preds


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
        # TRULY ADDITIVE target: y = clip(round(a[cA]+a[cB])), a[c] = 0.5*real per-class mean -> optimal additive captures
        # it (gate must NOT fire). Load-bearing control separating additive-multi-feature from genuine 2-way interaction.
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

    add_ls_pred, beta = arm_additive_lstsq(Xtr, ytr, Xq)
    add_cat_pred = arm_additive_cat(Xtr, ytr, Xq)
    int_pred = arm_interactive(Xtr, ytr, Xq, beta)
    pop = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    orc = oracle[q]

    train_pairs = set((int(Xtr[r, 0]), int(Xtr[r, 1])) for r in range(Xtr.shape[0]))
    seen_by_train = np.array([(int(Xq[r, 0]), int(Xq[r, 1])) in train_pairs for r in range(Xq.shape[0])], dtype=bool)
    seen_mask = seen & seen_by_train
    novel_mask = ~seen_mask

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("seen", seen_mask), ("novel", novel_mask), ("all", np.ones(len(gold), bool))):
        add_ls = a(add_ls_pred, m); add_cat = a(add_cat_pred, m)
        strong_add = max([v for v in (add_ls, add_cat) if v == v], default=float("nan"))
        out[sname] = dict(ADD_LSTSQ=round(add_ls, 5), ADD_CAT=round(add_cat, 5), STRONG_ADD=round(strong_add, 5),
                          INTERACTIVE=round(a(int_pred, m), 5), POP=round(a(pop, m), 5),
                          ORACLE=round(a(orc, m), 5), n=int(m.sum()))
    nonadd_seen = ((out["seen"]["INTERACTIVE"] - out["seen"]["STRONG_ADD"])
                   if out["seen"]["n"] > 0 else float("nan"))
    return dict(regime=regime, strata=out, nonadd_seen=nonadd_seen, n_seen=int(seen_mask.sum()),
                sigs=dict(ADD_LSTSQ=_sig(add_ls_pred), ADD_CAT=_sig(add_cat_pred),
                          INTERACTIVE=_sig(int_pred), ORACLE=_sig(orc)))


def run_measurement(seeds=(7, 13, 17, 23, 29, 31, 37, 41, 43, 47)):
    p, X, y = load_cluster()
    conj = conjunction_property(X, y)
    sev = _class_sev(X, y)

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
    clean_add_ls_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["ADD_LSTSQ"])
    clean_add_cat_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["ADD_CAT"])
    clean_strong_add_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["STRONG_ADD"])
    clean_int_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["INTERACTIVE"])
    clean_pop_seen = mean_field(CLEAN, lambda r: r["strata"]["seen"]["POP"])
    clean_int_novel = mean_field(CLEAN, lambda r: r["strata"]["novel"]["INTERACTIVE"])
    clean_strong_add_novel = mean_field(CLEAN, lambda r: r["strata"]["novel"]["STRONG_ADD"])
    orc_all = mean_field(CLEAN, lambda r: r["strata"]["all"]["ORACLE"])
    mean_n_seen = mean_field(CLEAN, lambda r: float(r["n_seen"]))
    # weak-baseline contrast (what the prior gate USED) -- reported to expose the WEAK vs STRONG gap
    clean_nonadd_weak = clean_int_seen - clean_add_ls_seen

    ys, _ = make_regime_target(X, y, SHUFFLE, seeds[0], sev=sev)
    shuf_conj = conjunction_property(X, ys)
    addsynth_y, _ = make_regime_target(X, y, ADDSYNTH, seeds[0], sev=sev)
    addsynth_conj = conjunction_property(X, addsynth_y)

    truth = p.get("truth_rate", float("nan"))
    ratio = conj["dominance_ratio"]

    conj_present = bool(ratio == ratio and ratio <= CONJ_RATIO_CEIL and conj["mi_margin"] >= CONJ_MI_MARGIN)
    truth_ok = bool(truth == truth and truth >= HP_TRUTH)
    nonadditive_ok = bool(clean_nonadd == clean_nonadd and clean_nonadd >= STRONG_NONADD_HP)
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
        verdict = "GENUINE_NONADDITIVE_EPISTASIS_VETTABLE_FOUNDATION_GO"
    elif refute:
        verdict = "EPISTASIS_POCKET_MAIN_EFFECTS_DOMINATED_OR_UNVETTABLE_REFUTE"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || n=%d(seen~%.0f) truth=%s(>=%.2f=%s) | CONJ joint=%.3f best_single=%.3f margin=%.3f(>=%.2f) "
           "ratio=%s(<=%.2f) present=%s | STRONG_NONADD clean=%s(>=%.2f=%s) [int_seen=%s strong_add=%s "
           "(cat=%s lstsq=%s) pop=%s] WEAK_nonadd=%s | novel[int=%s strong_add=%s] | GATE addsynth_nonadd=%s(<=%.2f) "
           "shuffle_nonadd=%s(clean>null+%.2f) valid=%s | single_driver=%s transform_additive=%s oracle=%s"
           % (verdict, p["n_entities"], mean_n_seen, _fmt(truth), HP_TRUTH, truth_ok, conj["joint_mi"],
              conj["best_single_mi"], conj["mi_margin"], CONJ_MI_MARGIN,
              _fmt(ratio) if ratio == ratio else "nan", CONJ_RATIO_CEIL, conj_present,
              _fmt(clean_nonadd), STRONG_NONADD_HP, nonadditive_ok, _fmt(clean_int_seen), _fmt(clean_strong_add_seen),
              _fmt(clean_add_cat_seen), _fmt(clean_add_ls_seen), _fmt(clean_pop_seen), _fmt(clean_nonadd_weak),
              _fmt(clean_int_novel), _fmt(clean_strong_add_novel), _fmt(addsynth_nonadd), ADDSYNTH_NONADD_CEIL,
              _fmt(shuffle_nonadd), DISCRIM_MARGIN, gate_valid, single_driver, transform_additive, _fmt(orc_all)))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="local_measure",
        elapsed_s=0.0, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        generator=p.get("generator"), n_entities=p["n_entities"], truth_rate=truth,
        n_judged=p.get("n_judged"), n_true=p.get("n_true"), seeds=list(seeds), L=L,
        conjunction=conj, shuffle_conjunction=shuf_conj, addsynth_conjunction=addsynth_conj,
        nonadditivity=dict(clean_strong=round(clean_nonadd, 5), clean_weak=round(clean_nonadd_weak, 5),
                           addsynth_strong=round(addsynth_nonadd, 5), shuffle_strong=round(shuffle_nonadd, 5)),
        clean=dict(int_seen=round(clean_int_seen, 5), strong_add_seen=round(clean_strong_add_seen, 5),
                   add_cat_seen=round(clean_add_cat_seen, 5), add_lstsq_seen=round(clean_add_ls_seen, 5),
                   pop_seen=round(clean_pop_seen, 5), int_novel=round(clean_int_novel, 5),
                   strong_add_novel=round(clean_strong_add_novel, 5), oracle_all=round(orc_all, 5),
                   mean_n_seen=round(mean_n_seen, 3)),
        gates=dict(truth_ok=truth_ok, conj_present=conj_present, nonadditive_ok=nonadditive_ok,
                   gate_valid=gate_valid, shuffle_destroyed=shuffle_destroyed, ceiling_ok=ceiling_ok,
                   single_driver=single_driver, transform_additive=transform_additive,
                   hard_pass=hard_pass, refute=refute),
        bands=dict(HP_TRUTH=HP_TRUTH, CONJ_RATIO_CEIL=CONJ_RATIO_CEIL, CONJ_MI_MARGIN=CONJ_MI_MARGIN,
                   STRONG_NONADD_HP=STRONG_NONADD_HP, NONADD_REFUTE=NONADD_REFUTE,
                   ADDSYNTH_NONADD_CEIL=ADDSYNTH_NONADD_CEIL, DISCRIM_MARGIN=DISCRIM_MARGIN,
                   DOMINANCE_REFUTE=DOMINANCE_REFUTE),
        per_seed={reg: [dict(strata=per_seed[reg][i]["strata"], nonadd_seen=per_seed[reg][i]["nonadd_seen"],
                             n_seen=per_seed[reg][i]["n_seen"]) for i in range(len(seeds))] for reg in REGIMES},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (real code path; NO LLM). Planted arenas prove the STRONG gate FIRES on a genuine 2-way interaction and does
# NOT fire on a purely-additive target, exercising the REAL MI + strong-categorical-additive + interactive arms + split.
# ===========================================================================

def _plant_cluster(n, seed, mode):
    rng = np.random.default_rng(seed)
    ncls = 8
    a = rng.integers(0, ncls, size=n); b = rng.integers(0, ncls, size=n)
    X = np.stack([np.minimum(a, b), np.maximum(a, b)], axis=1).astype(np.int64)
    if mode == "interaction":
        table = rng.integers(0, L, size=(ncls, ncls)); table = np.minimum(table, table.T)  # symmetric 2-way interaction
        y = np.array([table[int(X[i, 0]), int(X[i, 1])] for i in range(n)], dtype=np.int64)
    else:
        w = rng.integers(0, 3, size=ncls)
        y = np.array([int(np.clip(w[int(X[i, 0])] + w[int(X[i, 1])], 0, L - 1)) for i in range(n)], dtype=np.int64)
    return X, y


def self_test():
    n = 600

    Xi, yi = _plant_cluster(n, 7, "interaction")
    conj_i = conjunction_property(Xi, yi); sev_i = _class_sev(Xi, yi)
    rs_i = [score_regime(Xi, yi, CLEAN, sd, sev_i) for sd in (7, 13, 17)]
    nonadd_i = float(np.mean([r["nonadd_seen"] for r in rs_i if r["nonadd_seen"] == r["nonadd_seen"]]))
    strong_add_seen_i = float(np.mean([r["strata"]["seen"]["STRONG_ADD"] for r in rs_i]))
    int_seen_i = float(np.mean([r["strata"]["seen"]["INTERACTIVE"] for r in rs_i]))
    orc_i = float(np.mean([r["strata"]["all"]["ORACLE"] for r in rs_i]))
    n_seen_i = float(np.mean([r["n_seen"] for r in rs_i]))

    Xa, ya = _plant_cluster(n, 11, "additive")
    conj_a = conjunction_property(Xa, ya); sev_a = _class_sev(Xa, ya)
    rs_a = [score_regime(Xa, ya, CLEAN, sd, sev_a) for sd in (7, 13, 17)]
    nonadd_a = float(np.mean([r["nonadd_seen"] for r in rs_a if r["nonadd_seen"] == r["nonadd_seen"]]))

    rs_sh = [score_regime(Xi, yi, SHUFFLE, sd, sev_i) for sd in (7, 13, 17)]
    nonadd_sh = float(np.mean([r["nonadd_seen"] for r in rs_sh if r["nonadd_seen"] == r["nonadd_seen"]]))

    # real code path (if artifact exists): load + score once, arms-differ + n>=... ; unjudged-tolerant.
    real_ok = None; real_n = -1
    try:
        _p, Xr, yr = load_cluster()
        real_n = int(Xr.shape[0])
        sev_r = _class_sev(Xr, yr)
        scr = score_regime(Xr, yr, CLEAN, 7, sev_r)
        digs = scr["sigs"]
        # tolerate the two additive arms (ADD_LSTSQ / ADD_CAT) legitimately coinciding on simple real data; still catch
        # the bit-identical-collapse bug (would drop >=2 distinct values). META_RULE_AF arms_differ_exempted: (ADD_LSTSQ,ADD_CAT).
        real_ok = bool(len(set(digs.values())) >= len(digs) - 1 and Xr.shape[1] == 2)
    except (FileNotFoundError, OSError, KeyError) as e:
        real_ok = None
        print("[SELFTEST] real artifact not yet present (%s) -- plant checks still gate." % type(e).__name__, flush=True)

    ok = bool(
        nonadd_i >= STRONG_NONADD_HP                 # genuine interaction: strong additive canNOT capture -> gate FIRES
        and int_seen_i > strong_add_seen_i           # interactive strictly beats strong additive on seen pairs
        and conj_i["mi_margin"] >= CONJ_MI_MARGIN
        and conj_i["dominance_ratio"] == conj_i["dominance_ratio"] and conj_i["dominance_ratio"] <= CONJ_RATIO_CEIL
        and nonadd_a <= ADDSYNTH_NONADD_CEIL         # additive arena: gate does NOT fire (discriminator valid)
        and nonadd_i > nonadd_a + DISCRIM_MARGIN
        and nonadd_i > nonadd_sh + DISCRIM_MARGIN
        and orc_i >= 0.999
        and n_seen_i >= 8
        and (real_ok in (None, True))                # if artifact present, arms must differ + shape ok
    )
    out = dict(interaction_nonadd_strong=round(nonadd_i, 4), interaction_strong_add_seen=round(strong_add_seen_i, 4),
               interaction_int_seen=round(int_seen_i, 4), interaction_mi_margin=conj_i["mi_margin"],
               interaction_dominance_ratio=conj_i["dominance_ratio"], additive_nonadd_strong=round(nonadd_a, 4),
               additive_mi_margin=conj_a["mi_margin"], shuffle_nonadd_strong=round(nonadd_sh, 4),
               oracle=round(orc_i, 4), n_seen=n_seen_i, real_artifact_arms_differ=real_ok, real_n=real_n, passed=ok)
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
    # DEFAULT (no flag) OR --run = the STRONG non-additivity gate measurement (glass-box; runner invokes
    # `python -u <script>` with no args on remote -> this runs Step 2).
    if not os.path.exists(ARTIFACT):
        _log("ARTIFACT missing (%s); run --generate first (build-time)." % ARTIFACT)
        sys.exit(2)
    t0 = time.perf_counter()
    m = run_measurement()
    m["elapsed_s"] = round(time.perf_counter() - t0, 3)
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
