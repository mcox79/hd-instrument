# CELL: read_grow_foundation_conditioned_comprehension_v1
# QUESTION: Does a LEARNED, FOUNDATION-CONDITIONED comprehension step comprehend text BETTER
#   than cold reading -- i.e. does "knowledge guides comprehension" compound? This is the FIRST
#   piece of the compress-and-carry reading LOOP: comprehend a chunk USING the picture-so-far.
#   The BROKEN link in prior work = the FIRST step (comprehend the chunk) done with STATIC
#   hand-rules that CANNOT use the growing foundation. Here we replace hand-rule genus-selection
#   with a LEARNED, foundation-conditioned one and test the loop's CORE claim.
#
# GLASS-BOX (no runtime LLM): transparent LogisticRegression over INTERPRETABLE features
#   (term morphology + local syntactic-pattern counts + foundation counts/typecheck + global
#   frequency). NLTK POS/lemmatizer + WordNet (reused harness). NO spaCy-default / torch /
#   transformers. NOT next-word prediction -- trained on genus-grounding (comprehension) accuracy.
#
# ARCHITECTURE UNDER TEST (USER-converged 07-18): reading = a compress-and-carry LOOP. Read the
#   book IN ORDER, accumulate is-a/type knowledge. When comprehending a term defined in section N,
#   the reader may CONSULT the foundation built from sections <N -- to IMPORT a genus established
#   earlier AND to REJECT a local parse that contradicts the foundation's type-knowledge (the
#   coherence gate; the re-reading cell's polysaccharide->acid list-neighbor bug fix).
#
# ARMS (ONE variable = FOUNDATION-CONDITIONING; identical candidate set + classifier across a/b):
#   (a) FOUNDATION-CONDITIONED learned reader  [the loop]  -- full feature set incl foundation cols
#   (b) COLD learned reader (local context only) -- SAME classifier + SAME candidates, foundation cols ZEROED
#   (c) HAND-RULES baseline (reproduces v2-v4 / re-reading regime) -- local most-frequent genus, no learning
#   (d) FREQUENCY baseline -- global-majority genus for every term
#
# METRIC = comprehension accuracy (predicted genus vs gold, WordNet-lenient) reported OVERALL and
#   on CARRY-FORWARD terms (gold genus LOCALLY ABSENT but established in an EARLIER section -- the
#   terms where the foundation SHOULD help and cold reading structurally CANNOT).
#
# GUARDS (design-gate):
#   HELD-OUT      = gold TERMS split train/test; features carry NO term-identity, so generalization
#                   is genuine (not re-reading the same sentence / memorizing the definition).
#   CARRY-FORWARD = test terms with G* NOT in LOCAL candidate genera but G* IN FOUNDATION candidate
#                   genera (genuine CROSS-SECTION import, per the re-reading VET aa1212ba).
#   FREQUENCY GUARD = foundation win must beat the FREQUENCY baseline, not just cold (bootstrapping
#                   cell a9787ced found knowledge-guidance frequency-EQUIVALENT).
#   COHERENCE GATE = instrument that the foundation arm REJECTS/CORRECTS the class of wrong-genus
#                   errors the re-reading cell made (local list-neighbor false genus).
#   CAN-FAIL      = HARD_FAIL if no lift over cold/frequency OR carry-forward terms too rare.
#
# CELL-TEMPLATE MANDATORY:
# - start_marker + crash_diagnostic (Exception -> CELL_CRASHED metrics.json + traceback)
# - except SystemExit: raise BEFORE except Exception (no BaseException); no bare except
# - final_metrics_atomicity = tmp_replace (os.replace)
# - deterministic seeding only (FIXED int / sorted(); no built-in hash() / list(set()) ordering)
# - arms_differ_verified at smoke (foundation vs cold prediction vectors hash-differ)
# - all bands HYPOTHESIZED@ this file (pre-reg) -> confirmed MEASURED@ at smoke/full
#
# Compute architecture: (b) sequential-CPU. Justification: regex/POS/WordNet symbolic extraction +
#   a single small LogisticRegression fit (~thousands of interpretable-feature rows). No matmul on
#   substrate vectors. Diagnostic go/no-go on the loop's core claim (compute-proportionality:
#   cheapest decisive method). Wall < few min. Deterministic: OMP/OPENBLAS threads pinned to 1.

import os

# Determinism: pin BLAS threads BEFORE numpy/sklearn import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import re
import sys
import json
import time
import random
import argparse
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
from sklearn.linear_model import LogisticRegression

# Reuse the VET'd read->grow textbook harness (parse/extract/gold/genus/wn-match).
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from experiments.exp_read_grow_textbook_isa_growth_v1 import (
    parse_sections, ie_isa_extract, _split_sentences, genus_of_definition,
    _norm_term, _tokenize, _wn_related,
)
from nltk.corpus import wordnet as wn

ANCHOR_NAME = "read_grow_foundation_conditioned_comprehension_v1"
CORPUS = os.path.join(
    REPO, "data", "corpora", "textbook_concepts_biology", "cleaned",
    "concepts_biology.clean.txt",
)
SEED = 20260718

# ----------------------------- error-checking scaffolds -----------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "{}: {}".format(type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: {}".format(type(exc).__name__),
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ----------------------------- corpus -> per-section is-a edges -----------------------------

def extract_section_edges(prose):
    """Return list of (term_norm, genus_lemma, pattern) is-a edges for one section's prose.
       pattern in {COP, SUCHAS}. SUCHAS = coordinate-list / such-as context (list-neighbor prone)."""
    out = []
    for sent in _split_sentences(prose):
        for term, genus, pat in ie_isa_extract(sent):
            if term and genus:
                out.append((term, genus, pat))
    return out


def build_dataset(sections):
    """Read sections IN ORDER. Return:
       - gold: dict term_norm -> (home_section_idx, gold_genus)
       - sec_edges: list per-section [(term, genus, pattern), ...]
       - global_genus_counts: Counter over ALL read-pool genera (frequency baseline signal)
       Home section = the section whose glossary DEFINES the term (gold source)."""
    sec_edges = []
    for sec in sections:
        sec_edges.append(extract_section_edges(sec["prose"]))
    gold = {}
    for idx, sec in enumerate(sections):
        for term_surface, defn in sec["glossary"]:
            genus = genus_of_definition(defn)
            if genus is None:
                continue
            nt = _norm_term(_tokenize(term_surface))
            if not nt:
                continue
            if nt not in gold:  # first (defining) occurrence is home
                gold[nt] = (idx, genus)
    return gold, sec_edges


# ----------------------------- feature engineering -----------------------------

def _wn_is_noun(word):
    try:
        return len(wn.synsets(word, pos=wn.NOUN)) > 0
    except Exception:
        # single WordNet miss is non-fatal; treat as not-a-known-noun.
        return False


def _term_head(term_norm):
    parts = term_norm.split()
    return parts[-1] if parts else term_norm


def _suffix(head, k=4):
    return head[-k:] if len(head) >= k else head


def build_family_profiles(gold, sec_edges):
    """For each section boundary h, the foundation's morphological-family genus profile:
       maps 4-char term-suffix -> Counter(genus) accumulated from sections < h.
       Built incrementally so profile_at[h] uses ONLY sections strictly before h."""
    # per-section family contributions: from that section's own extracted edges
    per_sec_family = []
    for edges in sec_edges:
        fam = defaultdict(Counter)
        for term, genus, pat in edges:
            fam[_suffix(_term_head(term))][genus] += 1
        per_sec_family.append(fam)
    # prefix-accumulate: profile_at[h] = sum of per_sec_family[<h]
    profiles = []
    acc = defaultdict(Counter)
    for h in range(len(sec_edges)):
        # snapshot BEFORE adding section h (foundation = strictly earlier)
        snap = {k: Counter(v) for k, v in acc.items()}
        profiles.append(snap)
        for suf, cnt in per_sec_family[h].items():
            acc[suf].update(cnt)
    return profiles


def candidate_stats(term, home_idx, sec_edges):
    """Return (local, foundation): each a dict genus -> {cop, suchas} counts.
       local = home section only; foundation = all sections strictly before home."""
    local = defaultdict(lambda: {"cop": 0, "suchas": 0})
    found = defaultdict(lambda: {"cop": 0, "suchas": 0})
    for idx, edges in enumerate(sec_edges):
        if idx > home_idx:
            break
        for t, genus, pat in edges:
            if t != term:
                continue
            bucket = local if idx == home_idx else (found if idx < home_idx else None)
            if bucket is None:
                continue
            key = "cop" if pat == "COP" else "suchas"
            bucket[genus][key] += 1
    return local, found


# feature column names (foundation columns flagged for cold-arm zeroing)
FEATURE_NAMES = [
    "local_count", "local_cop", "local_suchas",
    "found_count", "found_cop", "found_suchas", "found_typecheck",   # <- FOUNDATION cols
    "global_freq_norm", "is_list_only", "cand_is_wn_noun", "bias",
]
FOUNDATION_COLS = {"found_count", "found_cop", "found_suchas", "found_typecheck"}


def make_features(term, home_idx, cand, local, found, family_profile, global_genus_counts, gmax):
    head_suf = _suffix(_term_head(term))
    fam = family_profile.get(head_suf, {})
    fam_total = sum(fam.values()) if fam else 0
    l = local.get(cand, {"cop": 0, "suchas": 0})
    f = found.get(cand, {"cop": 0, "suchas": 0})
    l_count = l["cop"] + l["suchas"]
    f_count = f["cop"] + f["suchas"]
    typecheck = (fam.get(cand, 0) / fam_total) if fam_total else 0.0
    is_list_only = 1.0 if ((l["suchas"] + f["suchas"]) > 0 and (l["cop"] + f["cop"]) == 0) else 0.0
    feats = {
        "local_count": float(l_count),
        "local_cop": float(l["cop"]),
        "local_suchas": float(l["suchas"]),
        "found_count": float(f_count),
        "found_cop": float(f["cop"]),
        "found_suchas": float(f["suchas"]),
        "found_typecheck": float(typecheck),
        "global_freq_norm": float(global_genus_counts.get(cand, 0)) / float(gmax) if gmax else 0.0,
        "is_list_only": is_list_only,
        "cand_is_wn_noun": 1.0 if _wn_is_noun(cand) else 0.0,
        "bias": 1.0,
    }
    return feats


def candidate_set(term, gold_genus, local, found, top_freq_genera):
    """SAME candidate set for foundation + cold arms (one-variable). Union of:
       local genera, foundation genera, global-frequent distractors, and the gold genus."""
    cands = set(local.keys()) | set(found.keys()) | set(top_freq_genera)
    cands.add(gold_genus)
    return sorted(cands)  # deterministic ordering


# ----------------------------- dataset assembly -----------------------------

def assemble(gold, sec_edges, n_distractors=8):
    """Build per-term candidate rows + feature dicts + carry-forward flags.
       Returns terms_data: dict term -> {
         home_idx, gold_genus, cands, feats (list aligned to cands), labels (list),
         local_genera (set), found_genera (set), carry_forward (bool),
         handrule_pred (genus or None), handrule_from_list (bool),
       }, plus global_genus_counts + freq_majority_genus."""
    # global genus frequency over ALL sections' edges (frequency baseline + feature)
    global_genus_counts = Counter()
    for edges in sec_edges:
        for t, genus, pat in edges:
            global_genus_counts[genus] += 1
    gmax = max(global_genus_counts.values()) if global_genus_counts else 1
    top_freq_genera = [g for g, _ in global_genus_counts.most_common(n_distractors)]
    freq_majority_genus = global_genus_counts.most_common(1)[0][0] if global_genus_counts else None

    family_profiles = build_family_profiles(gold, sec_edges)

    terms_data = {}
    for term, (home_idx, gold_genus) in gold.items():
        local, found = candidate_stats(term, home_idx, sec_edges)
        local_genera = set(local.keys())
        found_genera = set(found.keys())
        # gold-match membership (WordNet-lenient) for local/foundation
        gold_in_local = any(c == gold_genus or _wn_related(c, gold_genus) for c in local_genera)
        gold_in_found = any(c == gold_genus or _wn_related(c, gold_genus) for c in found_genera)
        carry_forward = (not gold_in_local) and gold_in_found

        cands = candidate_set(term, gold_genus, local, found, top_freq_genera)
        fam_profile = family_profiles[home_idx]
        feats = []
        labels = []
        for c in cands:
            feats.append(make_features(term, home_idx, c, local, found, fam_profile,
                                       global_genus_counts, gmax))
            labels.append(1 if (c == gold_genus or _wn_related(c, gold_genus)) else 0)

        # hand-rules baseline (reproduces re-reading regime): most-frequent LOCAL genus,
        # ties broken toward higher total count then first; list-neighbor picks are spurious-prone.
        handrule_pred = None
        handrule_from_list = False
        if local:
            best_g, best_c, best_is_list = None, -1, False
            for g in sorted(local.keys()):
                c = local[g]["cop"] + local[g]["suchas"]
                is_list = (local[g]["suchas"] > 0 and local[g]["cop"] == 0)
                if c > best_c:
                    best_g, best_c, best_is_list = g, c, is_list
            handrule_pred = best_g
            handrule_from_list = best_is_list

        terms_data[term] = {
            "home_idx": home_idx,
            "gold_genus": gold_genus,
            "cands": cands,
            "feats": feats,
            "labels": labels,
            "local_genera": local_genera,
            "found_genera": found_genera,
            "carry_forward": carry_forward,
            "handrule_pred": handrule_pred,
            "handrule_from_list": handrule_from_list,
        }
    return terms_data, global_genus_counts, freq_majority_genus


# ----------------------------- learned arms -----------------------------

def _matrix(feats_list, cols):
    return np.array([[fd[c] for c in cols] for fd in feats_list], dtype=np.float64)


def fit_and_predict(train_terms, test_terms, terms_data, cols):
    """Fit LogisticRegression on train-term (term,cand) rows using feature columns `cols`.
       Predict argmax candidate per test term. Returns dict term -> predicted_genus."""
    Xtr, ytr = [], []
    for t in train_terms:
        td = terms_data[t]
        for fd, lab in zip(td["feats"], td["labels"]):
            Xtr.append([fd[c] for c in cols])
            ytr.append(lab)
    Xtr = np.array(Xtr, dtype=np.float64)
    ytr = np.array(ytr, dtype=np.int64)
    # guard: need both classes present
    if len(set(ytr.tolist())) < 2:
        # degenerate; predict by raw local_count fallback
        clf = None
    else:
        clf = LogisticRegression(solver="lbfgs", C=1.0, max_iter=2000, random_state=0)
        clf.fit(Xtr, ytr)
    preds = {}
    coefs = None
    if clf is not None:
        coefs = {c: float(w) for c, w in zip(cols, clf.coef_[0])}
    for t in test_terms:
        td = terms_data[t]
        if not td["cands"]:
            preds[t] = None
            continue
        X = np.array([[fd[c] for c in cols] for fd in td["feats"]], dtype=np.float64)
        if clf is not None:
            scores = clf.decision_function(X)
        else:
            # fallback: local_count
            li = cols.index("local_count")
            scores = X[:, li]
        j = int(np.argmax(scores))
        preds[t] = td["cands"][j]
    return preds, coefs


def accuracy(preds, test_terms, terms_data, subset=None):
    """WordNet-lenient genus accuracy over test_terms (optionally restricted to `subset`)."""
    terms = [t for t in test_terms if (subset is None or t in subset)]
    if not terms:
        return 0.0, 0
    n_ok = 0
    for t in terms:
        gold = terms_data[t]["gold_genus"]
        p = preds.get(t)
        if p is not None and (p == gold or _wn_related(p, gold)):
            n_ok += 1
    return n_ok / len(terms), len(terms)


def handrule_accuracy(test_terms, terms_data, subset=None):
    terms = [t for t in test_terms if (subset is None or t in subset)]
    if not terms:
        return 0.0, 0
    n_ok = 0
    for t in terms:
        gold = terms_data[t]["gold_genus"]
        p = terms_data[t]["handrule_pred"]
        if p is not None and (p == gold or _wn_related(p, gold)):
            n_ok += 1
    return n_ok / len(terms), len(terms)


def freq_accuracy(test_terms, terms_data, freq_genus, subset=None):
    terms = [t for t in test_terms if (subset is None or t in subset)]
    if not terms:
        return 0.0, 0
    n_ok = 0
    for t in terms:
        gold = terms_data[t]["gold_genus"]
        if freq_genus is not None and (freq_genus == gold or _wn_related(freq_genus, gold)):
            n_ok += 1
    return n_ok / len(terms), len(terms)


# ----------------------------- coherence-gate evidence -----------------------------

def coherence_gate_evidence(test_terms, terms_data, found_preds, cold_preds):
    """Among test terms where HAND-RULES predicts a WRONG list-neighbor genus (the class of error
       the re-reading cell made: SUCHAS/list-context false genus != gold), how often does the
       FOUNDATION arm predict correctly, vs the COLD arm? Shows the coherence gate rejecting the
       list-neighbor false-genus error class."""
    targets = []
    for t in test_terms:
        td = terms_data[t]
        hp = td["handrule_pred"]
        gold = td["gold_genus"]
        if hp is None:
            continue
        wrong = not (hp == gold or _wn_related(hp, gold))
        if wrong and td["handrule_from_list"]:
            targets.append(t)
    n = len(targets)
    if n == 0:
        return {"n_handrule_listneighbor_errors": 0,
                "foundation_corrects_frac": None, "cold_corrects_frac": None,
                "foundation_avoids_wrong_frac": None}
    def corrects(preds):
        c = 0
        for t in targets:
            gold = terms_data[t]["gold_genus"]
            p = preds.get(t)
            if p is not None and (p == gold or _wn_related(p, gold)):
                c += 1
        return c / n
    def avoids_wrong(preds):
        # avoids repeating the hand-rule's wrong list-neighbor genus
        c = 0
        for t in targets:
            if preds.get(t) != terms_data[t]["handrule_pred"]:
                c += 1
        return c / n
    return {"n_handrule_listneighbor_errors": n,
            "foundation_corrects_frac": round(corrects(found_preds), 5),
            "cold_corrects_frac": round(corrects(cold_preds), 5),
            "foundation_avoids_wrong_frac": round(avoids_wrong(found_preds), 5)}


# ----------------------------- split -----------------------------

def split_terms(terms, test_frac, seed):
    """Deterministic train/test split over sorted term list (NO hash()-based ordering)."""
    ts = sorted(terms)
    rng = random.Random(seed)
    rng.shuffle(ts)
    n_test = max(1, int(round(len(ts) * test_frac)))
    test = set(ts[:n_test])
    train = [t for t in ts if t not in test]
    return train, sorted(test)


# ----------------------------- pre-registered bands -----------------------------

BANDS = {
    # HARD_PASS: foundation MEANINGFULLY lifts comprehension on carry-forward terms above BOTH
    #   cold-learned AND frequency, with a real overall gain and enough carry-forward mass.
    "hp_carryfwd_lift_over_cold": 0.10,     # HYPOTHESIZED@ this file
    "hp_carryfwd_lift_over_freq": 0.10,     # HYPOTHESIZED@ this file
    "hp_overall_lift_over_cold": 0.03,      # HYPOTHESIZED@ this file
    "hp_min_carryforward_test": 15,         # HYPOTHESIZED@ this file (need mass to be meaningful)
    # HARD_FAIL: no meaningful lift OR carry-forward too rare (localize honestly).
    "hf_carryfwd_lift_max": 0.02,           # HYPOTHESIZED@ this file (<=2pp over max(cold,freq) = no lift)
    "hf_min_carryforward_test": 15,         # HYPOTHESIZED@ this file (< this = HARD_FAIL_CARRYFWD_RARE)
}


def compute_verdict(diag, bands):
    ncf = diag["n_carryforward_test"]
    if ncf < bands["hf_min_carryforward_test"]:
        return ("HARD_FAIL_CARRYFWD_RARE",
                "carry-forward test terms too rare (n={} < {}); loop untestable at this scale".format(
                    ncf, bands["hf_min_carryforward_test"]))
    fnd = diag["foundation_carryfwd_acc"]
    cold = diag["cold_carryfwd_acc"]
    freq = diag["freq_carryfwd_acc"]
    lift_vs_best = fnd - max(cold, freq)
    overall_lift = diag["foundation_overall_acc"] - diag["cold_overall_acc"]
    if lift_vs_best <= bands["hf_carryfwd_lift_max"]:
        return ("HARD_FAIL_NO_LIFT",
                "foundation gives no carry-forward lift over max(cold={:.3f},freq={:.3f}): {:+.3f} <= {:.3f}".format(
                    cold, freq, lift_vs_best, bands["hf_carryfwd_lift_max"]))
    if ((fnd - cold) >= bands["hp_carryfwd_lift_over_cold"]
            and (fnd - freq) >= bands["hp_carryfwd_lift_over_freq"]
            and overall_lift >= bands["hp_overall_lift_over_cold"]
            and ncf >= bands["hp_min_carryforward_test"]):
        return ("HARD_PASS",
                "foundation-conditioning compounds: carryfwd acc={:.3f} vs cold={:.3f} freq={:.3f}; overall +{:.3f}".format(
                    fnd, cold, freq, overall_lift))
    return ("MIDDLE_BAND",
            "some lift but below HARD_PASS: carryfwd fnd={:.3f} cold={:.3f} freq={:.3f} overall+{:.3f}".format(
                fnd, cold, freq, overall_lift))


# ----------------------------- driver -----------------------------

def corpus_structure_audit(gold, sec_edges):
    """MEASURED extraction-coverage / carry-forward-population audit (the load-bearing localization).
       For each gold term: is its gold genus extractable LOCAL at home, in an EARLIER section
       (causal carry-forward), a LATER section only (needs 2nd pass), or NEVER anywhere?"""
    term_sec_genera = defaultdict(dict)
    for idx, edges in enumerate(sec_edges):
        for t, g, p in edges:
            term_sec_genera[t].setdefault(idx, set()).add(g)

    def gmatch(cand, gg):
        return cand == gg or _wn_related(cand, gg)

    local_has = earlier_cf = later_only = never = any_avail = 0
    for t, (home, gg) in gold.items():
        sm = term_sec_genera.get(t, {})
        local_g = sm.get(home, set())
        earlier_g, later_g, all_g = set(), set(), set()
        for s, gs in sm.items():
            all_g |= gs
            if s < home:
                earlier_g |= gs
            elif s > home:
                later_g |= gs
        gl = any(gmatch(c, gg) for c in local_g)
        ge = any(gmatch(c, gg) for c in earlier_g)
        gL = any(gmatch(c, gg) for c in later_g)
        if gl:
            local_has += 1
        elif ge:
            earlier_cf += 1
        elif gL:
            later_only += 1
        else:
            never += 1
        if any(gmatch(c, gg) for c in all_g):
            any_avail += 1
    return {
        "n_gold_terms": len(gold),
        "gold_extractable_anywhere": any_avail,
        "extraction_coverage_frac": round(any_avail / max(1, len(gold)), 5),
        "gold_local_at_home": local_has,
        "gold_causal_carryforward_earlier": earlier_cf,
        "gold_later_section_only": later_only,
        "gold_never_extracted": never,
    }


def run(sections, test_frac=0.4, n_distractors=8, seed=SEED):
    gold, sec_edges = build_dataset(sections)
    terms_data, global_genus_counts, freq_genus = assemble(gold, sec_edges, n_distractors=n_distractors)

    all_terms = sorted(terms_data.keys())
    train, test = split_terms(all_terms, test_frac, seed)

    cold_cols = [c for c in FEATURE_NAMES if c not in FOUNDATION_COLS]
    found_cols = list(FEATURE_NAMES)

    found_preds, found_coefs = fit_and_predict(train, test, terms_data, found_cols)
    cold_preds, cold_coefs = fit_and_predict(train, test, terms_data, cold_cols)

    carry_set = {t for t in test if terms_data[t]["carry_forward"]}

    fnd_overall, n_test = accuracy(found_preds, test, terms_data)
    cold_overall, _ = accuracy(cold_preds, test, terms_data)
    hand_overall, _ = handrule_accuracy(test, terms_data)
    freq_overall, _ = freq_accuracy(test, terms_data, freq_genus)

    fnd_cf, n_cf = accuracy(found_preds, test, terms_data, subset=carry_set)
    cold_cf, _ = accuracy(cold_preds, test, terms_data, subset=carry_set)
    hand_cf, _ = handrule_accuracy(test, terms_data, subset=carry_set)
    freq_cf, _ = freq_accuracy(test, terms_data, freq_genus, subset=carry_set)

    coherence = coherence_gate_evidence(test, terms_data, found_preds, cold_preds)

    # arms-must-differ: foundation vs cold prediction vectors
    fv = tuple(found_preds.get(t) for t in test)
    cv = tuple(cold_preds.get(t) for t in test)
    arms_differ = (fv != cv)

    diag = {
        "n_gold_terms": len(gold),
        "n_train_terms": len(train),
        "n_test_terms": n_test,
        "n_carryforward_test": n_cf,
        "carryforward_frac_of_test": round(n_cf / max(1, n_test), 5),
        "foundation_overall_acc": round(fnd_overall, 5),
        "cold_overall_acc": round(cold_overall, 5),
        "handrules_overall_acc": round(hand_overall, 5),
        "freq_overall_acc": round(freq_overall, 5),
        "foundation_carryfwd_acc": round(fnd_cf, 5),
        "cold_carryfwd_acc": round(cold_cf, 5),
        "handrules_carryfwd_acc": round(hand_cf, 5),
        "freq_carryfwd_acc": round(freq_cf, 5),
        "freq_majority_genus": freq_genus,
        "arms_differ": bool(arms_differ),
        "foundation_coefs": found_coefs,
        "cold_coefs": cold_coefs,
        "coherence_gate": coherence,
        "corpus_structure_audit": corpus_structure_audit(gold, sec_edges),
        "overall_metric_caveat": (
            "overall_acc is INFLATED by candidate-set construction: gold genus is always injected as a "
            "candidate and distractors are the top-frequency genera, so the learned arm's high "
            "negative global_freq_norm weight recovers gold by 'avoid the frequent candidate' rather "
            "than by genuine comprehension. Treat overall_acc as NON-EVIDENTIAL for comprehension; "
            "the load-bearing signal is carry-forward mass (n_carryforward_test) + extraction_coverage_frac."
        ),
    }
    return diag


def _band_check(diag):
    """Design-gate: real baselines, baseline-in-band, can-fail, one-variable, difficulty-on."""
    checks = {}
    # baseline-in-band (cold, freq, handrules must be measurable, not saturated/floored)
    for k in ("cold_overall_acc", "freq_overall_acc", "handrules_overall_acc"):
        v = diag[k]
        checks[k + "_in_band"] = bool(0.02 < v < 0.98)
    checks["arms_differ"] = diag["arms_differ"]
    checks["carryforward_present"] = diag["n_carryforward_test"] > 0
    checks["real_freq_baseline"] = diag["freq_majority_genus"] is not None
    # can-fail: the discriminator (carryfwd lift) is a MEASURED gap, not pinned to a constant.
    checks["one_variable_foundation_cols"] = sorted(FOUNDATION_COLS) == sorted(
        c for c in FEATURE_NAMES if c not in [x for x in FEATURE_NAMES if x not in FOUNDATION_COLS])
    return checks


# ----------------------------- self-test -----------------------------

def self_test():
    print("[self-test] exercising REAL code path (parse/extract/assemble/fit) on tiny corpus", flush=True)
    # Tiny in-order book. Section Alpha ESTABLISHES 'X is a carbohydrate' in prose; the term is
    # only DEFINED (glossary gold) later in Gamma, where the LOCAL prose gives a spurious list
    # neighbor -> carry-forward + coherence-gate exercised on the REAL code path.
    text = "\n".join([
        "# Tiny Book",
        "##### Section Alpha",
        "A monosaccharide is a carbohydrate that stores energy.",
        "A disaccharide is a carbohydrate found in food.",
        "A polysaccharide is a carbohydrate built from many sugars.",
        "###### Glossary",
        "monosaccharide: a carbohydrate that is a simple sugar",
        "##### Section Beta",
        "An enzyme is a protein that speeds reactions.",
        "A hormone is a molecule that carries signals.",
        "###### Glossary",
        "enzyme: a protein that catalyzes reactions",
        "##### Section Gamma",
        "Compounds such as polysaccharide, acid, and base appear in cells.",
        "###### Glossary",
        "polysaccharide: a carbohydrate made of many monosaccharides",
        "disaccharide: a carbohydrate of two sugars",
    ])
    secs = parse_sections(text)
    assert len(secs) == 3, "expected 3 sections, got {}".format(len(secs))
    gold, sec_edges = build_dataset(secs)
    assert "polysaccharide" in gold, gold
    # polysaccharide home = Gamma (idx 2); genus established as carbohydrate in Alpha (idx 0)
    assert gold["polysaccharide"][0] == 2, gold["polysaccharide"]
    terms_data, gcounts, fgen = assemble(gold, sec_edges, n_distractors=6)
    td = terms_data["polysaccharide"]
    # carry-forward: gold 'carbohydrate' NOT local (Gamma local = such-as list w/ acid/base),
    # but IS in foundation (Alpha COP). Verify the structural flag on the REAL code path.
    assert "carbohydrate" in td["found_genera"], ("foundation import missing", td["found_genera"])
    assert td["carry_forward"] is True, ("polysaccharide should be carry-forward", td)
    # candidate set is identical across arms (built once); foundation feature present for gold cand
    fd_gold = td["feats"][td["cands"].index("carbohydrate")]
    assert fd_gold["found_count"] > 0, ("foundation feature must fire for imported genus", fd_gold)
    # cold arm cannot see found_count (column dropped)
    cold_cols = [c for c in FEATURE_NAMES if c not in FOUNDATION_COLS]
    assert "found_count" not in cold_cols and "local_count" in cold_cols
    # end-to-end run on tiny corpus (all terms; just verify it produces a diag with arms)
    diag = run(secs, test_frac=0.5, n_distractors=6, seed=SEED)
    assert "foundation_carryfwd_acc" in diag and "cold_carryfwd_acc" in diag
    v, msg = compute_verdict(diag, BANDS)
    assert v in ("HARD_PASS", "HARD_FAIL_NO_LIFT", "HARD_FAIL_CARRYFWD_RARE", "MIDDLE_BAND")
    # coherence-gate structure present
    assert "n_handrule_listneighbor_errors" in diag["coherence_gate"]
    print("[self-test] PASS: sections={} gold={} carryfwd_flag(poly)={} verdict={}".format(
        len(secs), len(gold), td["carry_forward"], v), flush=True)
    return True


# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke-sections", type=int, default=200,
                    help="leading sections used in smoke mode (design-gate verification)")
    ap.add_argument("--test-frac", type=float, default=0.4)
    ap.add_argument("--n-distractors", type=int, default=8)
    args, _ = ap.parse_known_args()

    if args.self_test:
        ok = self_test()
        sys.exit(0 if ok else 1)

    run_mode = args.mode
    output_dir = os.path.join(REPO, "data", "exp_{}{}".format(
        ANCHOR_NAME, "_smoke" if run_mode == "smoke" else ""))
    _write_start_marker(output_dir, run_mode, expected_n_units=1)

    t0 = time.perf_counter()
    with open(CORPUS, "r", encoding="utf-8") as f:
        text = f.read()
    sections_all = parse_sections(text)
    sections = sections_all[:args.smoke_sections] if run_mode == "smoke" else sections_all
    print("[{}] sections={} (of {})".format(run_mode, len(sections), len(sections_all)), flush=True)

    diag = run(sections, test_frac=args.test_frac, n_distractors=args.n_distractors, seed=SEED)
    checks = _band_check(diag)
    verdict, verdict_msg = compute_verdict(diag, BANDS)
    elapsed = time.perf_counter() - t0

    gate = {
        "design_gate_checks": checks,
        "difficulty_on": "held-out test terms (features carry no term-identity); carry-forward = gold genus locally ABSENT, foundation-present",
        "one_variable": "foundation-conditioning cols {} zeroed in cold arm; identical candidate set + classifier".format(sorted(FOUNDATION_COLS)),
        "real_baselines": {
            "cold_learned": diag["cold_overall_acc"],
            "hand_rules": diag["handrules_overall_acc"],
            "frequency": diag["freq_overall_acc"],
            "freq_majority_genus": diag["freq_majority_genus"],
        },
        "frequency_guard": "foundation carryfwd {:.3f} vs freq carryfwd {:.3f}".format(
            diag["foundation_carryfwd_acc"], diag["freq_carryfwd_acc"]),
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": "{}: carryfwd fnd={:.3f} cold={:.3f} freq={:.3f} hand={:.3f} | overall fnd={:.3f} cold={:.3f} | n_cf={}".format(
            verdict, diag["foundation_carryfwd_acc"], diag["cold_carryfwd_acc"],
            diag["freq_carryfwd_acc"], diag["handrules_carryfwd_acc"],
            diag["foundation_overall_acc"], diag["cold_overall_acc"], diag["n_carryforward_test"]),
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "bands": BANDS,
        "diag": diag,
        "gate": gate,
        "seed": SEED,
    }
    _write_metrics_atomic(output_dir, metrics)
    print("[{}] VERDICT={} {}".format(run_mode, verdict, metrics["summary"]), flush=True)
    print("[{}] coherence_gate={}".format(run_mode, json.dumps(diag["coherence_gate"])), flush=True)
    print("[{}] design_gate_checks={}".format(run_mode, json.dumps(checks)), flush=True)
    print("[{}] metrics -> {}".format(run_mode, os.path.join(output_dir, "metrics.json")), flush=True)


if __name__ == "__main__":
    OUT_FOR_CRASH = os.path.join(REPO, "data", "exp_{}".format(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUT_FOR_CRASH, e)
        raise
