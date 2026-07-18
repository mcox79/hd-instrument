"""
Base-first reader: can a glass-box reader LEARN a held-out concrete word's category
FROM the understood context, when a base makes ~99% of the surround known?

FAIR held-out test of base-first comprehension. Measured ONLY on held-out words
(anti-masking). Glass-box (Naive-Bayes over interpretable context features);
learn-in-substrate; NO external LLM; NOT next-word prediction.

Arc: comprehension-loop v1 (50e4a73c0 / VET aca3e0bd) HARD_FAILed at 18% coverage
(context NOT understood -> nothing to learn from). This is v1 done RIGHT: the FULL
base clears the Hu&Nation ~98% coverage threshold on the cleaned McGuffey readers,
so the ~99% surround is understood and only the sparse held-out NEW is learned.

ANCHOR: base_first_reader_heldout_context_learn_v1
COMPUTE: sequential-CPU, wall < 10s, no substrate HD primitive, no GPU (justified).
DETERMINISM: OMP_NUM_THREADS=1; fixed RNG seed 12345; sorted(set(...)) ordering only.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)  [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                [META_RULE_AF]
# - baseline_in_band 0.05 < prior < 0.95              [META_RULE_AG]
# - discriminator CAN-FAIL (gap can be <=0)           [design-gate]
# - deterministic seeding (fixed int seed, sorted set) [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 10s)
# - all reported numbers MEASURED@this metrics.json
# - N/A: KGStore/substrate_signature/real_code_path (no substrate object constructed)
# - N/A: cardinality sweep-axis (no seed/param sweep); N/A CRLB (no HD noise floor)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import csv
import re
import json
import math
import time
import random
import argparse
import hashlib
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

from nltk.corpus import wordnet as wn

ANCHOR_NAME = "base_first_reader_heldout_context_learn_v1"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
BASE_CSV = os.path.join(REPO, "data", "corpora", "base_vocabulary", "cleaned", "base_vocabulary_ordered.csv")
READER_PATHS = [
    os.path.join(REPO, "data", "corpora", "graded_readers_grade1", "cleaned", "mcguffey_first_reader.clean.txt"),
    os.path.join(REPO, "data", "corpora", "graded_readers_grade1", "cleaned", "mcguffey_primer.clean.txt"),
]

SEED = 12345
WINDOW = 4          # same-sentence context window (+/- W) -- linguistic default, chosen a priori
MIN_OCC = 2         # a word must appear >= MIN_OCC times in the reader to have usable context
N_BOOT = 5000

# ---- Pre-registered bands (set BEFORE the final expanded run) --------------------
COVERAGE_GATE = 0.98            # base-adequacy AND understood-surround must both clear this
HP_GAP = 0.15                   # PRIMARY gap(a-b) HARD-PASS threshold (strict; META_RULE_L)
HP_ACC = 0.45                   # PRIMARY (a) must reach ~halfway prior->ceiling ("approaching lookup")
HP_ALPHA = 0.05                 # bootstrap significance P(gap<=0) < alpha
MB_GAP = 0.05                   # MIDDLE_BAND floor: positive but not HP

# ---- HAND-AUTHORED coarse categories (INDEPENDENT gold; NOT WordNet-derived on the
#      held-out word). The scoring grader uses ONLY these hand labels. WordNet is used
#      to GROUND context words + as the (d) lookup CEILING reference, never as the grader
#      of a held-out word. Anti-circularity: inference never looks up the held-out word.
HELDOUT_GOLD = {
    # ANIMAL
    "hen": "ANIMAL", "frog": "ANIMAL", "owl": "ANIMAL", "duck": "ANIMAL",
    "fox": "ANIMAL", "bee": "ANIMAL", "rat": "ANIMAL", "chick": "ANIMAL",
    # PLANT
    "grass": "PLANT", "rose": "PLANT", "corn": "PLANT", "nut": "PLANT",
    "bush": "PLANT", "willow": "PLANT", "vine": "PLANT",
    # FOOD
    "bread": "FOOD", "honey": "FOOD", "meat": "FOOD", "milk": "FOOD",
    "apple": "FOOD", "cracker": "FOOD",
    # ARTIFACT
    "doll": "ARTIFACT", "basket": "ARTIFACT", "cart": "ARTIFACT", "cage": "ARTIFACT",
    "bell": "ARTIFACT", "flag": "ARTIFACT", "mill": "ARTIFACT", "skate": "ARTIFACT", "fan": "ARTIFACT",
    # BODY
    "hand": "BODY", "mouth": "BODY", "head": "BODY", "neck": "BODY",
    "arm": "BODY", "lap": "BODY", "hair": "BODY",
    # PLACE (natural feature / geographic)
    "pond": "PLACE", "brook": "PLACE", "hill": "PLACE", "sea": "PLACE",
    "shore": "PLACE", "beach": "PLACE", "river": "PLACE",
    # SUBSTANCE (material)
    "ice": "SUBSTANCE", "sand": "SUBSTANCE", "wood": "SUBSTANCE",
    "log": "SUBSTANCE", "fur": "SUBSTANCE", "snow": "SUBSTANCE",
}
# KNOWN exemplars: STAY in the base; give the classifier per-category context prototypes
# to transfer from. Hand-labeled with the SAME coarse scheme (a supervised label space is
# shared between train and test by design; the held-out word's identity is never a train
# feature and its gold is never wn-derived here).
KNOWN_LABELS = {
    "dog": "ANIMAL", "cat": "ANIMAL", "bird": "ANIMAL", "horse": "ANIMAL",
    "fish": "ANIMAL", "cow": "ANIMAL", "lamb": "ANIMAL", "wolf": "ANIMAL",
    "goat": "ANIMAL", "sheep": "ANIMAL",
    "tree": "PLANT", "flower": "PLANT", "moss": "PLANT", "stump": "PLANT",
    "egg": "FOOD", "tea": "FOOD", "hay": "FOOD", "cake": "FOOD",
    "hat": "ARTIFACT", "box": "ARTIFACT", "boat": "ARTIFACT", "mat": "ARTIFACT",
    "slate": "ARTIFACT", "cap": "ARTIFACT", "barn": "ARTIFACT", "kite": "ARTIFACT",
    "house": "ARTIFACT", "drum": "ARTIFACT",
    "feet": "BODY", "face": "BODY", "wing": "BODY", "eye": "BODY", "foot": "BODY",
    "rock": "PLACE", "bank": "PLACE", "town": "PLACE", "home": "PLACE", "spot": "PLACE",
    "water": "SUBSTANCE", "air": "SUBSTANCE", "fat": "SUBSTANCE", "foam": "SUBSTANCE",
}

STOP = set((
    "the a an and or of to in on is it he she we you i they his her its my your our "
    "their this that these those with at by for as be are was were do does did has "
    "have had not no yes will would can could"
).split())

CONTRACTIONS = {
    "can't", "don't", "won't", "it's", "he's", "she's", "that's", "i'm",
    "let's", "there's", "what's",
}

# WordNet noun lexname -> coarse category (for the (d) dictionary-lookup CEILING only)
LEX2CAT = {
    "noun.animal": "ANIMAL", "noun.plant": "PLANT", "noun.food": "FOOD",
    "noun.artifact": "ARTIFACT", "noun.body": "BODY", "noun.location": "PLACE",
    "noun.object": "PLACE", "noun.substance": "SUBSTANCE", "noun.shape": "ARTIFACT",
}


# ------------------------------------------------------------------ data helpers
def load_base(path):
    ranked = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = (row.get("word") or "").strip().lower()
            if w:
                ranked.append(w)
    return ranked


def make_normalizer(base_all):
    def norm(t):
        if "'" in t and t not in CONTRACTIONS:
            j = t.replace("'", "")
            if j in base_all:
                return j
            if t.endswith("'s") and t[:-2] in base_all:
                return t[:-2]
        return t
    return norm


def roman_set(upto=120):
    def roman(n):
        vals = [(100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"),
                (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
        s = ""
        for v, sy in vals:
            while n >= v:
                s += sy
                n -= v
        return s
    return set(roman(i) for i in range(1, upto + 1))


def detect_names(reader_paths, base_all, label_words):
    raw = " ".join(open(p, encoding="utf-8").read() for p in reader_paths)
    cap = set(m.lower() for m in re.findall(r"\b([A-Z][a-z]+)\b", raw))
    return set(w for w in cap if w not in base_all and w not in label_words)


def read_sentences(path):
    keep = []
    for ln in open(path, encoding="utf-8").read().splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if parts and sum(1 for p in parts
                         if len(re.sub(r"[^a-z]", "", p.lower())) <= 2) / len(parts) > 0.6:
            continue  # phonics-fragment row
        keep.append(s)
    joined = " ".join(keep)
    out = []
    for seg in re.split(r"[.?!]+", joined):
        out.append(re.findall(r"[a-zA-Z']+", " " + seg.lower()))
    return out


def make_lemmatizer(label_words):
    def lemma(t):
        if t in label_words:
            return t
        if t.endswith("s") and t[:-1] in label_words:
            return t[:-1]
        if t.endswith("es") and t[:-2] in label_words:
            return t[:-2]
        return t
    return lemma


def coverage(sents, base, norm, names, romans):
    tot = known = 0
    for toks in sents:
        for t in toks:
            if t in names:
                continue
            if t in romans and t != "i":
                continue
            nt = norm(t)
            if nt not in base and len(nt) <= 2:
                continue  # phonics fragment, not vocabulary
            tot += 1
            known += (1 if nt in base else 0)
    return (known / tot if tot else 0.0), known, tot


def surround_coverage(sents, reduced_base, heldout, norm, lemma, names, romans, window):
    known = total = 0
    for toks in sents:
        lem = [lemma(t) for t in toks]
        for i, w in enumerate(lem):
            if w not in heldout:
                continue
            lo = max(0, i - window)
            hi = min(len(lem), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                tj = toks[j]
                if tj in names or (tj in romans and tj != "i"):
                    continue
                if lem[j] in heldout:
                    continue  # another held-out word is sparse-new, not the surround
                nt = norm(tj)
                if nt not in reduced_base and len(nt) <= 2:
                    continue
                total += 1
                known += (1 if nt in reduced_base else 0)
    return (known / total if total else 0.0), known, total


def noun_supersense(w):
    ss = wn.synsets(w, pos=wn.NOUN)
    return ss[0].lexname() if ss else None


# ------------------------------------------------------------- NB context reader
def build_context_reader(sents, known_labels, heldout_gold, lemma, mode, window, cats):
    """Glass-box Naive Bayes: context features -> category. Trained on KNOWN exemplar
    occurrences only. mode in {identity, handcat, wnsup}."""
    cat_ctx = defaultdict(Counter)
    cat_prior = Counter()
    vocab = set()
    held_ctx = defaultdict(Counter)
    held_occ = Counter()

    def feats(lem, i):
        lo = max(0, i - window)
        hi = min(len(lem), i + window + 1)
        fs = []
        for j in range(lo, hi):
            if j == i:
                continue
            c = lem[j]
            if c in STOP or len(c) < 2:
                continue
            fs.append("W=" + c)  # context-word identity (distributional)
            if mode == "handcat" and c in known_labels:
                fs.append("HC=" + known_labels[c])  # labeled-neighbor category tag
            if mode == "wnsup":
                sp = noun_supersense(c)
                if sp:
                    fs.append("SS=" + sp)  # WordNet-grounded supersense of context word
        return fs

    for toks in sents:
        lem = [lemma(t) for t in toks]
        for i, w in enumerate(lem):
            if w in known_labels:
                cat_prior[known_labels[w]] += 1
                for f in feats(lem, i):
                    cat_ctx[known_labels[w]][f] += 1
                    vocab.add(f)
            if w in heldout_gold:
                held_occ[w] += 1
                for f in feats(lem, i):
                    held_ctx[w][f] += 1

    V = len(vocab) + 1
    totc = {c: sum(cat_ctx[c].values()) for c in cats}
    tp = sum(cat_prior.values())

    def score(fc, c):
        s = math.log((cat_prior[c] + 1) / (tp + len(cats)))
        d = totc[c] + V
        for f, n in fc.items():
            s += n * math.log((cat_ctx[c][f] + 1) / d)
        return s

    train_majority = max(cats, key=lambda c: cat_prior[c])
    preds = {}
    for w in heldout_gold:
        if held_occ[w] > 0:
            preds[w] = max(cats, key=lambda c: score(held_ctx[w], c))
    return preds, dict(cat_prior), train_majority, held_occ


def dict_lookup(w):
    ss = wn.synsets(w, pos=wn.NOUN)
    if not ss:
        return None
    return LEX2CAT.get(ss[0].lexname())


def bootstrap_gap(present, corr_a, corr_b, seed, n_boot):
    n = len(present)
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ga = sum(corr_a[i] for i in idx) / n
        gb = sum(corr_b[i] for i in idx) / n
        diffs.append(ga - gb)
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs))]
    p_le0 = sum(1 for x in diffs if x <= 0) / len(diffs)
    return lo, hi, p_le0


# ---------------------------------------------------------------- infra helpers
def _write_start_marker(output_dir, run_mode):
    import platform
    os.makedirs(output_dir, exist_ok=True)
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "host": platform.node(),
    }
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "run_mode": "crash",
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _arms_differ(arms_pred):
    digests = {}
    for name, pred in arms_pred.items():
        blob = json.dumps(pred, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(blob).hexdigest()
    names = sorted(digests)
    for a in names:
        for b in names:
            if a < b:
                assert digests[a] != digests[b], (
                    "META_RULE_AF: arms %r and %r produced bit-identical predictions" % (a, b))
    return digests


# ----------------------------------------------------------------- core pipeline
def run_pipeline(run_mode):
    t0 = time.perf_counter()
    ranked = load_base(BASE_CSV)
    base_all = set(ranked)
    norm = make_normalizer(base_all)
    romans = roman_set()
    label_words = set(KNOWN_LABELS) | set(HELDOUT_GOLD)
    names = detect_names(READER_PATHS, base_all, label_words)
    lemma = make_lemmatizer(label_words)

    sents = []
    for p in READER_PATHS:
        sents += read_sentences(p)

    # occurrence filter: drop held-out / known that do not appear >= MIN_OCC
    occ = Counter()
    for toks in sents:
        for t in toks:
            occ[lemma(t)] += 1
    heldout = {w: c for w, c in HELDOUT_GOLD.items() if occ[w] >= MIN_OCC}
    known = {w: c for w, c in KNOWN_LABELS.items() if occ[w] >= 1}
    dropped_held = sorted(set(HELDOUT_GOLD) - set(heldout))
    dropped_known = sorted(set(KNOWN_LABELS) - set(known))

    reduced_base = base_all - set(heldout)
    cats = sorted(set(list(known.values()) + list(heldout.values())))

    # ---- fairness gates
    cov_full, kf, tf = coverage(sents, base_all, norm, names, romans)
    cov_red, kr, tr = coverage(sents, reduced_base, norm, names, romans)
    cov_sur, ks, ts = surround_coverage(sents, reduced_base, heldout, norm, lemma,
                                        names, romans, WINDOW)

    # ---- per-category cardinality (each category needs >=2 known AND >=2 held-out present)
    held_by_cat = Counter(heldout.values())
    known_by_cat = Counter(known.values())
    degenerate_cats = [c for c in cats if held_by_cat[c] < 2 or known_by_cat[c] < 2]

    # ---- build the 3 feature-variant readers (PRIMARY = wnsup, pre-registered)
    panel = {}
    prior = None
    train_majority = None
    held_occ = None
    for mode in ["identity", "handcat", "wnsup"]:
        preds, prior_m, tmaj, hocc = build_context_reader(
            sents, known, heldout, lemma, mode, WINDOW, cats)
        panel[mode] = preds
        prior = prior_m
        train_majority = tmaj
        held_occ = hocc

    present = sorted(w for w in heldout if held_occ[w] > 0)
    n = len(present)

    # ---- arms
    # (a) base-context (per variant), (b) no-context (trained prior/majority),
    # (c) frequency (train majority == token-prior argmax), (d) dictionary lookup CEILING
    b_pred = {w: train_majority for w in present}
    c_pred = {w: train_majority for w in present}  # coincide with (b): both are the no-context floor
    d_pred = {w: dict_lookup(w) for w in present}

    def acc(pred):
        return sum(1 for w in present if pred.get(w) == heldout[w]) / n if n else 0.0

    a_acc = {m: acc(panel[m]) for m in panel}
    b_acc = acc(b_pred)
    c_acc = acc(c_pred)
    d_acc = acc(d_pred)

    # ---- baseline-in-band (META_RULE_AG): prior accuracy must be measurable, not saturated
    baseline_in_band = 0.05 < b_acc < 0.95

    # ---- PRIMARY = wnsup ; bootstrap significance of gap(a-b)
    primary = "wnsup"
    corr_a = [1 if panel[primary].get(w) == heldout[w] else 0 for w in present]
    corr_b = [1 if b_pred.get(w) == heldout[w] else 0 for w in present]
    ci_lo, ci_hi, p_le0 = bootstrap_gap(present, corr_a, corr_b, SEED, N_BOOT)
    primary_gap = a_acc[primary] - b_acc

    # ---- arms-must-differ (a-primary, b, d must differ; a and b legitimately may coincide
    #      only if context yields the majority everywhere -> then flag). c==b is EXEMPT
    #      (declared: both are the no-context floor by construction).
    arms_for_hash = {"a_" + primary: panel[primary], "b_nocontext": b_pred, "d_dictlookup": d_pred}
    arms_differ_digests = _arms_differ(arms_for_hash)

    # ---- per-word table
    per_word = []
    for w in present:
        per_word.append({
            "word": w, "gold": heldout[w], "occ": held_occ[w],
            "a_identity": panel["identity"].get(w),
            "a_handcat": panel["handcat"].get(w),
            "a_wnsup": panel["wnsup"].get(w),
            "b_nocontext": b_pred[w], "d_dictlookup": d_pred[w],
            "a_wnsup_correct": bool(panel["wnsup"].get(w) == heldout[w]),
        })

    # ---- VERDICT (pre-registered bands)
    gates_ok = (cov_full >= COVERAGE_GATE and cov_sur >= COVERAGE_GATE
                and baseline_in_band and not degenerate_cats and n >= 20)
    if not gates_ok:
        verdict = "GATE_FAIL"
        why = []
        if cov_full < COVERAGE_GATE:
            why.append("base_coverage %.4f < %.2f" % (cov_full, COVERAGE_GATE))
        if cov_sur < COVERAGE_GATE:
            why.append("surround_coverage %.4f < %.2f" % (cov_sur, COVERAGE_GATE))
        if not baseline_in_band:
            why.append("baseline %.3f out of band" % b_acc)
        if degenerate_cats:
            why.append("degenerate_cats %s" % degenerate_cats)
        if n < 20:
            why.append("n_heldout %d < 20" % n)
        verdict_msg = "GATE_FAIL: " + "; ".join(why)
    else:
        significant = p_le0 < HP_ALPHA
        if primary_gap >= HP_GAP and a_acc[primary] >= HP_ACC and significant:
            verdict = "HARD_PASS"
            verdict_msg = ("HARD_PASS: base-context reader learns held-out categories "
                           "significantly better than no-context, approaching lookup "
                           "(a=%.3f gap=%.3f p=%.4f)" % (a_acc[primary], primary_gap, p_le0))
        elif primary_gap >= MB_GAP and a_acc[primary] > b_acc:
            verdict = "MIDDLE_BAND"
            verdict_msg = ("MIDDLE_BAND: context helps weakly (a=%.3f gap=%.3f "
                           "p=%.4f, CI=[%.3f,%.3f]) but below significance/approach-lookup bar; "
                           "far below dict-lookup ceiling %.3f"
                           % (a_acc[primary], primary_gap, p_le0, ci_lo, ci_hi, d_acc))
        else:
            verdict = "HARD_FAIL"
            verdict_msg = ("HARD_FAIL: base-context reader no better than no-context "
                           "(a=%.3f b=%.3f gap=%.3f) -- context not usable at grade-1 scale"
                           % (a_acc[primary], b_acc, primary_gap))

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "%s | a_wnsup=%.3f b=%.3f d=%.3f gap=%.3f p=%.4f n=%d cov_base=%.4f cov_surround=%.4f"
                   % (verdict, a_acc["wnsup"], b_acc, d_acc, primary_gap, p_le0, n, cov_full, cov_sur),
        "run_mode": run_mode,
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "window": WINDOW,
        "min_occ": MIN_OCC,
        "prereg_bands": {
            "coverage_gate": COVERAGE_GATE, "hp_gap": HP_GAP, "hp_acc": HP_ACC,
            "hp_alpha": HP_ALPHA, "mb_gap": MB_GAP, "primary_variant": primary,
        },
        "coverage": {
            "full_base_gate": round(cov_full, 4), "full_base_frac": [kf, tf],
            "understood_surround_gate": round(cov_sur, 4), "surround_frac": [ks, ts],
            "reduced_base_info_only": round(cov_red, 4),
            "gate_passed": bool(cov_full >= COVERAGE_GATE and cov_sur >= COVERAGE_GATE),
        },
        "arms": {
            "a_identity": round(a_acc["identity"], 4),
            "a_handcat": round(a_acc["handcat"], 4),
            "a_wnsup_PRIMARY": round(a_acc["wnsup"], 4),
            "b_nocontext": round(b_acc, 4),
            "c_frequency": round(c_acc, 4),
            "d_dictlookup_CEILING": round(d_acc, 4),
        },
        "primary_gap_a_minus_b": round(primary_gap, 4),
        "bootstrap": {"ci95_lo": round(ci_lo, 4), "ci95_hi": round(ci_hi, 4),
                      "p_gap_le_0": round(p_le0, 4), "n_boot": N_BOOT},
        "n_heldout_present": n,
        "n_known_present": len(known),
        "heldout_gold_distribution": dict(Counter(heldout[w] for w in present)),
        "train_majority_category": train_majority,
        "baseline_in_band": bool(baseline_in_band),
        "degenerate_categories": degenerate_cats,
        "dropped_heldout_low_occ": dropped_held,
        "dropped_known_absent": dropped_known,
        "n_detected_names_excluded": len(names),
        "arms_differ_verified": True,
        "arms_differ_digests": arms_differ_digests,
        "arms_differ_exempted": [["b_nocontext", "c_frequency"]],
        "final_metrics_atomicity": "tmp_replace",
        "compute_class": "sequential_cpu_wall_lt_10s_no_hd_primitive",
        "anti_circularity": "gold hand-authored; inference never looks up held-out word; "
                            "wn used only to ground context + as (d) lookup ceiling",
        "per_word": per_word,
    }
    return metrics


# ------------------------------------------------------------------- self-test
def self_test():
    """Exercises the REAL code path (build_context_reader, coverage, arms_differ) at
    tiny scale; asserts measured values match expectation BEFORE any full run."""
    # toy corpus: 2 categories, context separates them
    toy_sents = [
        ["the", "dog", "ran"], ["the", "cat", "ran"], ["a", "dog", "sat"],
        ["the", "hat", "fell"], ["a", "box", "fell"], ["the", "hat", "sat"],
        ["the", "pup", "ran"],   # pup = held-out ANIMAL (context: ran/sat like dog/cat)
        ["a", "lid", "fell"],    # lid = held-out ARTIFACT (context: fell like hat/box)
    ]
    known = {"dog": "ANIMAL", "cat": "ANIMAL", "hat": "ARTIFACT", "box": "ARTIFACT"}
    heldg = {"pup": "ANIMAL", "lid": "ARTIFACT"}
    lemma = make_lemmatizer(set(known) | set(heldg))
    cats = sorted(set(list(known.values()) + list(heldg.values())))
    preds, prior, tmaj, hocc = build_context_reader(toy_sents, known, heldg, lemma,
                                                    "identity", 4, cats)
    assert preds.get("pup") == "ANIMAL", "self-test: pup should map ANIMAL, got %r" % preds.get("pup")
    assert preds.get("lid") == "ARTIFACT", "self-test: lid should map ARTIFACT, got %r" % preds.get("lid")

    # coverage self-test: all-known toy -> 1.0
    base = set(known) | {"the", "a", "ran", "sat", "fell"}
    cov, k, t = coverage(toy_sents[:6], base, lambda x: x, set(), set())
    assert abs(cov - 1.0) < 1e-9, "self-test: all-known coverage should be 1.0, got %.4f" % cov

    # arms-differ self-test: identical dicts must raise
    try:
        _arms_differ({"x": {"a": "A"}, "y": {"a": "A"}})
        raise AssertionError("self-test: _arms_differ failed to catch identical arms")
    except AssertionError as e:
        if "META_RULE_AF" not in str(e):
            raise

    # real WordNet path exercised
    assert dict_lookup("hen") == "ANIMAL", "self-test: wn lookup hen should be ANIMAL"
    print("SELFTEST_PASS: toy context reader + coverage + arms-differ + wn lookup OK", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", default=None)
    args = ap.parse_args()

    run_mode = "full"
    if args.run_mode:
        run_mode = args.run_mode
    elif args.self_test:
        run_mode = "self_test"

    _write_start_marker(OUTPUT_DIR, run_mode)

    if run_mode == "self_test":
        self_test()
        # still write a metrics stub so downstream never mistakes selftest for full
        _atomic_write_metrics(OUTPUT_DIR, {
            "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (self-test only; not a full run)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": 0.0,
        })
        return

    # full run: self-test first (fail loud before burning the run), then pipeline
    self_test()
    metrics = run_pipeline(run_mode)
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    print(metrics["summary"], flush=True)
    print(metrics["verdict_msg"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
