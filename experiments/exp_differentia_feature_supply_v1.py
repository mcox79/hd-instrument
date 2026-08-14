"""exp_differentia_feature_supply_v1 -- STEPS 2+3 of Stage 2: leak controls, then does an
EXTRACTOR-DERIVED DIFFERENTIA supply carry lexical-similarity signal that the genus alone does
not, and that ConceptNet-minus-lexical-relations does not?

PRE-REG: preregs/2026-08-13_differentia_feature_supply.md AMENDMENT A1, commit 64a4ea4c2, filed
BEFORE the extraction ran and BEFORE any correlation was computed. The COPULA+GLOSSARY_COLON
pattern restriction was frozen there, in advance, and is not revisited here.

SUPPLY: data/exp_differentia_simplewiki_extract_v1/ (169,982 COPULA+GLOSSARY_COLON facts over
119,720 terms) MEASURED@data/exp_differentia_simplewiki_extract_v1/metrics.json:n_treatment_facts

NO FILE UNDER hdlab/ IS MODIFIED. The comparator, the distinctiveness organ, the grounded control
and the scramble control are all IMPORTED FROM THE PREDECESSOR CELL
(exp_distinctiveness_weighted_composition_v1) so arm D is computed by the same code that produced
the 0.0804 reference, not by a re-implementation. That import also gives import-chain coverage:
the predecessor's own module-scope self-test runs before this cell does anything.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-arm score-vector sha256)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a declared (pre-reg A1.6); power statement is the PAIRED BOOTSTRAP, reported as an MDE
# - discriminator survives scale: multi-scale smoke (120 / 480 pairs), scramble must collapse
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - cardinality_ok: EXPECTED_N_UNITS = 11, gated in the verdict
# - per-unit failure-class instrumentation (META_RULE_J)
# - deterministic seeding: fixed ints + hashlib only; no builtin hash(), no list(set())
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy/torch import (they size their pools at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import glob
import hashlib
import json
import math
import platform
import re
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import torch
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.grounded_similarity import (                                  # noqa: E402
    _raw_cos as grounded_raw_cos, grounded_vector, in_grounded_lexicon,
)
from hdlab.lexical_similarity import _cos_complex                        # noqa: E402
from hdlab.thematic_role_labeler import lemma_word                       # noqa: E402
from experiments._validity_preflight import run_validity_preflight       # noqa: E402
# REUSE, not re-implementation: arm D and the scramble control are the PREDECESSOR's own code.
from experiments.exp_distinctiveness_weighted_composition_v1 import (    # noqa: E402
    CALIBRATION, FEATURE_SEED_BC, N_DIM_BC, SCRAMBLE_SEED, Supply, _build_phases,
    _scrambled_assignment, build_supply, get_cskg_cache, load_simlex, streamed_profile,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

# ---------------------------------------------------------------------------------------------
# CONFIG -- every value below is pre-registered (AMENDMENT A1). Nothing here is adjusted after
# seeing a result.
# ---------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_differentia_feature_supply_v1"
PREREG_PATH = "preregs/2026-08-13_differentia_feature_supply.md"
SUPPLY_DIR = os.path.join(REPO_ROOT, "data", "exp_differentia_simplewiki_extract_v1")
V6_ISA_PATH = os.path.join(REPO_ROOT, "data", "exp_definitional_predicate_v6",
                           "isa_facts_unchanged_v6.jsonl")

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")     # SEPARATE dir (mandatory)
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

TREATMENT_PATTERNS = ("COPULA", "GLOSSARY_COLON")          # frozen in A1.1, re-asserted here
FORBIDDEN_PATTERNS = ("CALLED", "REFERS_TO", "APPOSITIVE")
V6_STRICT_PATTERNS = ("COPULA", "GLOSSARY_COLON")          # for the B_STRICT sensitivity only

# L2 frozen phrase list (A1.2). First four are the dispatch brief's; last two are the same
# construction class and are included because a wider net is the stricter choice.
SYNONYM_PHRASES = ("another name for", "also known as", "same as", "another word for",
                   "another term for", "also called")
_SYN_RE = re.compile("|".join(re.escape(p) for p in SYNONYM_PHRASES), re.IGNORECASE)

FEATURE_ARMS = ("A_DIFFERENTIA", "B_GENUS_ONLY", "B_STRICT_GENUS", "D_CSKG_NOLEXREL", "E_SCRAMBLE")
COMPARATORS = ("UNIFORM", "WEIGHTED")      # PRIMARY = UNIFORM (A1.3); WEIGHTED is reported only
EXPECTED_N_UNITS = len(FEATURE_ARMS) * len(COMPARATORS) + 1     # +1 for C_GROUNDED_RAW == 11

# PRE-REGISTERED BANDS (A1.5). DO NOT EDIT AFTER A RUN.
HP_RHO_MIN = 0.35
HP_SCRAMBLE_MAX = 0.05
BAND_MARGIN_FRAC = 0.05          # META_RULE_L
MIN_SURVIVING_PAIRS = 50         # A1.2 power gate; armed on FULL only
THIN_COVERAGE = 0.30             # A1.5 SUPPLY_REAL_BUT_THIN threshold

N_BOOTSTRAP = 5000               # A1.4 (>= the 2000 the brief requires)
BOOTSTRAP_SEED = 20260813
SMOKE_PAIR_SCALES = (120, 480)   # multi-scale smoke; pair count is the statistic's load axis

# Positive control (SCHEMA-VET gate D): arm D must reproduce the predecessor AT ITS OWN REGIME.
# MEASURED@data/exp_distinctiveness_weighted_composition_v1/metrics.json:
#   per_supply.C_CSKG_NOLEXREL.rho.WEIGHTED = 0.0804  (n_eval_pairs = 639)
D_PRIOR_RHO_WEIGHTED = 0.0804
D_PRIOR_N = 639
D_REPRO_TOL = 0.01


# ---------------------------------------------------------------------------------------------
# Durability plumbing
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _heartbeat(output_dir: str, unit_idx: int, total_units: int, elapsed_s: float,
               extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 3)}
    if extra:
        row["extra"] = extra
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)          # META_RULE_AH
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    _atomic_write_metrics(output_dir, {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "run_mode": "crash", "failure_class": type(exc).__name__,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME})


# ---------------------------------------------------------------------------------------------
# Supply loading
# ---------------------------------------------------------------------------------------------
class WordRecord:
    """Everything one SimLex word's definitions supply: features, texts, source lines."""

    __slots__ = ("diff", "genus", "definiens_texts", "sentences", "line_nos", "definiens_lemmas")

    def __init__(self) -> None:
        self.diff: Set[str] = set()
        self.genus: Set[str] = set()
        self.definiens_texts: List[str] = []
        self.sentences: List[str] = []
        self.line_nos: Set[int] = set()
        self.definiens_lemmas: Set[str] = set()


def load_treatment_store(vocab: Set[str]) -> Tuple[Dict[str, WordRecord], Dict[str, int], dict]:
    """Index the simplewiki treatment store for the evaluated vocabulary, and compute feature
    document-frequency over the WHOLE term population (that is the population distinctiveness is
    measured against, per the predecessor's construction).

    Returns (records for evaluated words, df over the whole population, provenance)."""
    shards = sorted(glob.glob(os.path.join(SUPPLY_DIR, "facts_block_*.jsonl")))
    if not shards:
        raise FileNotFoundError("treatment store missing: %s" % SUPPLY_DIR)
    recs: Dict[str, WordRecord] = {}
    pop: Dict[str, Set[str]] = {}          # term -> feature set, over the WHOLE population
    seen_patterns: Set[str] = set()
    n_rows = 0
    t0 = time.time()
    for sh in shards:
        with open(sh, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                n_rows += 1
                seen_patterns.add(d["pattern"])
                head = d["head"]
                lem = [l for l in d["definiens_lemmas"] if l != head]
                feats = ["DIFF|" + l for l in lem]
                if head:
                    feats.append("GENUS|" + head)
                key_pop = (d["term"] or d["definiendum_lemma"] or "").strip().lower()
                if key_pop and feats:
                    pop.setdefault(key_pop, set()).update(feats)
                if not d["definiens"]:
                    continue
                for cand in (d["term"], d["definiendum"], d["definiendum_lemma"]):
                    if not cand:
                        continue
                    c = cand.strip().lower()
                    if c not in vocab:
                        continue
                    r = recs.setdefault(c, WordRecord())
                    r.diff.update("DIFF|" + l for l in lem)
                    if head:
                        r.genus.add("GENUS|" + head)
                    r.definiens_texts.append(d["definiens"])
                    r.sentences.append(d["sentence"])
                    r.line_nos.add(int(d["line_no"]))
                    r.definiens_lemmas.update(d["definiens_lemmas"])
    # ---- THE FROZEN RESTRICTION, RE-ASSERTED AT CONSUMPTION TIME (A1.1) ----------------------
    forbidden = sorted(seen_patterns & set(FORBIDDEN_PATTERNS))
    if forbidden:
        raise AssertionError("FORBIDDEN PATTERN IN TREATMENT SUPPLY: %r" % forbidden)
    if not seen_patterns <= set(TREATMENT_PATTERNS):
        raise AssertionError("unexpected pattern in treatment supply: %r" % sorted(seen_patterns))
    df: Dict[str, int] = {}
    for feats in pop.values():
        for ft in feats:
            df[ft] = df.get(ft, 0) + 1
    prov = {"n_shards": len(shards), "n_rows": n_rows, "n_population_terms": len(pop),
            "n_population_features": len(df),
            "patterns_present": sorted(seen_patterns),
            "forbidden_present": forbidden,
            "load_elapsed_s": round(time.time() - t0, 2)}
    print("[supply] %s" % json.dumps(prov), flush=True)
    return recs, df, prov


def load_v6_genus(vocab: Set[str]) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], dict]:
    """Genus half of the v6 ISA store. Returns (all-pattern, COPULA+GLOSSARY-only, provenance).
    The dispatch brief names this file explicitly and it carries all five patterns; the strict
    variant exists only for the reported B_STRICT sensitivity (A1.3)."""
    allp: Dict[str, Set[str]] = {}
    strict: Dict[str, Set[str]] = {}
    counts: Dict[str, int] = {}
    with open(V6_ISA_PATH, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            counts[d["pattern"]] = counts.get(d["pattern"], 0) + 1
            w = d["subject"].strip().lower()
            if w not in vocab or not d["object"]:
                continue
            allp.setdefault(w, set()).add("GENUS|" + d["object"])
            if d["pattern"] in V6_STRICT_PATTERNS:
                strict.setdefault(w, set()).add("GENUS|" + d["object"])
    prov = {"path": os.path.relpath(V6_ISA_PATH, REPO_ROOT), "pattern_counts": counts,
            "simlex_words_covered_allpat": len(allp),
            "simlex_words_covered_strict": len(strict)}
    print("[v6-isa] %s" % json.dumps(prov), flush=True)
    return allp, strict, prov


# ---------------------------------------------------------------------------------------------
# LEAK CONTROLS (STEP 2) -- run BEFORE the measurement; reported regardless of outcome
# ---------------------------------------------------------------------------------------------
def _whole_word_in(needles: Sequence[str], haystack: str) -> bool:
    low = haystack.lower()
    for n in needles:
        if not n:
            continue
        if re.search(r"\b" + re.escape(n.lower()) + r"\b", low):
            return True
    return False


def leak_controls(pairs: List[Tuple[str, str, float]], recs: Dict[str, WordRecord]
                  ) -> Tuple[List[Tuple[str, str, float]], dict]:
    """L1 direct leak, L2 synonym-statement leak, L3 source-sentence overlap.

    Each is computed on the pair set BEFORE any arm is scored. Every excluded set is reported
    with its count and a sample. A pair can trip more than one control; `n_excluded_union` is the
    count that matters for power."""
    l1: List[Tuple[str, str]] = []
    l2: List[Tuple[str, str]] = []
    l3: List[Tuple[str, str]] = []
    for a, b, _g in pairs:
        ra, rb = recs[a], recs[b]
        # L1 -- a's definiens names b (surface or lemma), or vice versa.
        nb = [b, lemma_word(b)]
        na = [a, lemma_word(a)]
        hit = (any(_whole_word_in(nb, t) for t in ra.definiens_texts)
               or any(_whole_word_in(na, t) for t in rb.definiens_texts)
               or lemma_word(b) in ra.definiens_lemmas or b in ra.definiens_lemmas
               or lemma_word(a) in rb.definiens_lemmas or a in rb.definiens_lemmas)
        if hit:
            l1.append((a, b))
        # L2 -- an explicit synonymy construction anywhere in either word's kept definitions.
        syn = any(_SYN_RE.search(t) for t in ra.definiens_texts + ra.sentences) or \
              any(_SYN_RE.search(t) for t in rb.definiens_texts + rb.sentences)
        if syn:
            l2.append((a, b))
        # L3 -- a and b defined from the SAME source line.
        if ra.line_nos & rb.line_nos:
            l3.append((a, b))
    excluded = set(l1) | set(l2) | set(l3)
    survivors = [p for p in pairs if (p[0], p[1]) not in excluded]
    report = {
        "n_pairs_before_controls": len(pairs),
        "L1_direct_leak": {"n": len(l1), "sample": sorted(l1)[:15],
                           "definition": "a's definiens names b (whole word, surface or lemma), "
                                         "or vice versa"},
        "L2_synonym_statement_leak": {
            "n": len(l2), "sample": sorted(l2)[:15], "phrases": list(SYNONYM_PHRASES),
            "definition": "an explicit synonymy construction in either word's definiens or its "
                          "source sentence"},
        "L3_source_sentence_overlap": {"n": len(l3), "sample": sorted(l3)[:15],
                                       "definition": "a and b defined from the SAME source line"},
        "n_excluded_union": len(excluded),
        "n_surviving": len(survivors),
        "all_three_excluded_from_primary": True,
    }
    print("[leak] L1=%d L2=%d L3=%d union=%d surviving=%d/%d"
          % (len(l1), len(l2), len(l3), len(excluded), len(survivors), len(pairs)), flush=True)
    return survivors, report


# ---------------------------------------------------------------------------------------------
# Supplies -> the PREDECESSOR's comparator
# ---------------------------------------------------------------------------------------------
def make_supply(name: str, word_feats: Dict[str, List[str]], df: Dict[str, int],
                n_docs: int) -> Supply:
    """Build a Supply for the predecessor's comparator. Distinctiveness comes from the same organ
    (hdlab.low_information_filter.InformationProfile via the predecessor's streamed_profile), so
    no parallel measure is introduced."""
    wf = {w: sorted(set(fs)) for w, fs in word_feats.items() if fs}
    needed = sorted({f for fs in wf.values() for f in fs})
    for f in needed:
        if f.startswith("/r/"):
            raise AssertionError("FORBIDDEN: ConceptNet edge %r reached treatment supply %r"
                                 % (f, name))
        if f not in df:
            raise AssertionError("feature %r has no population df in supply %r" % (f, name))
    prof = streamed_profile(n_docs, {f: df[f] for f in needed}, wf)
    # One representative concept per feature, built in a single pass. prof.pmi() reduces to
    # log2(n_docs/df_f) and so is independent of which concept is passed (that reduction is what
    # the predecessor's _assert_pmi_reduction proves); the representative only satisfies the
    # organ's (concept, feature) call signature. O(incidences), not O(features x words).
    rep: Dict[str, str] = {}
    for w, fs in wf.items():
        for f in fs:
            if f not in rep:
                rep[f] = w
    weights = {f: prof.pmi(rep[f], f) for f in needed}
    feat_index = {f: i for i, f in enumerate(needed)}
    phases = _build_phases(needed, N_DIM_BC, FEATURE_SEED_BC)
    return Supply(name, wf, weights, N_DIM_BC, FEATURE_SEED_BC, None, phases, feat_index)


def supply_scores(sup: Supply, pairs: List[Tuple[str, str, float]], weighted: bool) -> List[float]:
    cache: Dict[str, torch.Tensor] = {}
    w = sup.weights if weighted else None

    def cv(word: str) -> torch.Tensor:
        if word not in cache:
            cache[word] = sup.concept_vector(sup.word_feats[word], w)
        return cache[word]

    return [float(_cos_complex(cv(a), cv(b))) for a, b, _ in pairs]


def analytic_incidence_cosine(sup: Supply, pairs: List[Tuple[str, str, float]]) -> List[float]:
    """Zero-noise limit of the FHRR bundle: exact uniform cosine over feature-incidence space.
    Diagnostic only -- bounds how much of a null is embedding sampling noise vs mechanism."""
    out = []
    for a, b, _ in pairs:
        fa, fb = set(sup.word_feats[a]), set(sup.word_feats[b])
        num = float(len(fa & fb))
        na, nb = math.sqrt(len(fa)), math.sqrt(len(fb))
        out.append(num / (na * nb) if na > 0 and nb > 0 else 0.0)
    return out


def _rho(scores: Sequence[float], golds: Sequence[float]) -> float:
    arr = np.asarray(scores, dtype=np.float64)
    if float(arr.std()) == 0.0:
        return 0.0
    r = spearmanr(list(scores), list(golds)).statistic
    return 0.0 if (r is None or np.isnan(r)) else float(r)


# ---------------------------------------------------------------------------------------------
# PAIRED BOOTSTRAP (A1.4) -- the arms are DEPENDENT correlations; a naive independent SE is wrong
# ---------------------------------------------------------------------------------------------
def paired_bootstrap(arm_scores: Dict[str, List[float]], golds: List[float],
                     n_boot: int, seed: int) -> dict:
    """Resample PAIRS with replacement; recompute every arm on the SAME resampled index set.
    Percentile 95% CI for each arm rho and for each pre-registered delta."""
    n = len(golds)
    g = np.asarray(golds, dtype=np.float64)
    mat = {k: np.asarray(v, dtype=np.float64) for k, v in arm_scores.items()}
    rng = np.random.default_rng(seed)
    names = sorted(mat)
    boot: Dict[str, List[float]] = {k: [] for k in names}
    n_degenerate = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        gg = g[idx]
        if float(gg.std()) == 0.0:
            n_degenerate += 1
            continue
        for k in names:
            ss = mat[k][idx]
            if float(ss.std()) == 0.0:
                boot[k].append(0.0)
                continue
            r = spearmanr(ss, gg).statistic
            boot[k].append(0.0 if (r is None or np.isnan(r)) else float(r))
    out: dict = {"n_boot_requested": n_boot, "n_boot_used": n_boot - n_degenerate,
                 "n_degenerate_resamples": n_degenerate, "seed": seed, "arm_ci": {}, "delta_ci": {}}
    for k in names:
        arr = np.asarray(boot[k], dtype=np.float64)
        out["arm_ci"][k] = {"lo": float(np.percentile(arr, 2.5)),
                            "hi": float(np.percentile(arr, 97.5)),
                            "sd": float(arr.std(ddof=1))}
    return out, boot


def delta_ci(boot: Dict[str, List[float]], a: str, b: str,
             point_a: float, point_b: float) -> dict:
    d = np.asarray(boot[a], dtype=np.float64) - np.asarray(boot[b], dtype=np.float64)
    sd = float(d.std(ddof=1))
    return {"point": round(point_a - point_b, 4),
            "ci_low": round(float(np.percentile(d, 2.5)), 4),
            "ci_high": round(float(np.percentile(d, 97.5)), 4),
            "bootstrap_sd": round(sd, 4),
            "mde_95": round(1.96 * sd, 4),
            "includes_zero": bool(np.percentile(d, 2.5) <= 0.0 <= np.percentile(d, 97.5))}


# ---------------------------------------------------------------------------------------------
# Verdict (A1.5) -- frozen bands, evaluated in the pre-registered order
# ---------------------------------------------------------------------------------------------
def classify(rho_a: float, rho_b: float, rho_c: float, rho_d: float, rho_e: float,
             d_ab: dict, d_ac: dict, coverage999: float) -> Tuple[str, List[str]]:
    notes: List[str] = []
    # 1. HARD_FAIL
    if d_ab["includes_zero"]:
        return "HARD_FAIL", [
            "CI(A-B)=[%.4f,%.4f] includes 0: the DIFFERENTIA adds nothing over the GENUS."
            % (d_ab["ci_low"], d_ab["ci_high"])]
    if rho_a <= rho_d:
        return "HARD_FAIL", [
            "A=%.4f <= D=%.4f: the extracted supply does not beat CSKG-minus-lexical-relations."
            % (rho_a, rho_d)]
    # 2. HARD_PASS
    gates = {"A>=0.35": (rho_a, HP_RHO_MIN, True),
             "CI_low(A-C)>0": (d_ac["ci_low"], 0.0, True),
             "CI_low(A-B)>0": (d_ab["ci_low"], 0.0, True),
             "scramble<=0.05": (rho_e, HP_SCRAMBLE_MAX, False)}
    all_pass = all((v > t if t == 0.0 and hi else (v >= t if hi else v <= t))
                   for v, t, hi in gates.values())
    if all_pass:
        thin = [k for k, (v, t, hi) in gates.items()
                if t != 0.0 and abs(v - t) < BAND_MARGIN_FRAC * abs(t)]
        if thin:
            return "MIDDLE_BAND", ["META_RULE_L: cleared %s by <5%% of the threshold magnitude"
                                   % thin]
        if coverage999 < THIN_COVERAGE:
            notes.append("coverage of the full 999 is %.3f (<%.2f): supply-limited even though "
                         "every gate cleared" % (coverage999, THIN_COVERAGE))
        return "HARD_PASS", notes
    # 3. SUPPLY_REAL_BUT_THIN
    if d_ac["ci_low"] > 0.0 and coverage999 < THIN_COVERAGE:
        return "SUPPLY_REAL_BUT_THIN", [
            "CI_low(A-C)=%.4f>0 but coverage=%.3f<%.2f: the mechanism works where it reaches; the "
            "fix is more extraction, not a different mechanism."
            % (d_ac["ci_low"], coverage999, THIN_COVERAGE)]
    failed = [k for k, (v, t, hi) in gates.items()
              if not ((v > t if t == 0.0 and hi else (v >= t if hi else v <= t)))]
    return "MIDDLE_BAND", ["gates not met: %s" % failed]


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY -- module scope, before any sweep)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}
    assert os.path.isdir(SUPPLY_DIR), "treatment store missing: %s" % SUPPLY_DIR
    shards = sorted(glob.glob(os.path.join(SUPPLY_DIR, "facts_block_*.jsonl")))
    assert shards, "treatment store has no shards"
    res["n_shards"] = len(shards)
    assert os.path.exists(V6_ISA_PATH), "v6 ISA store missing"

    # (1) leak-control regexes actually FIRE (a control that can never fire is not a control).
    assert _SYN_RE.search("a movie, also known as a film"), "L2 regex does not fire"
    assert not _SYN_RE.search("a nephron is the functional unit of the kidney"), "L2 over-fires"
    assert _whole_word_in(["film"], "a movie is a film"), "L1 whole-word matcher does not fire"
    assert not _whole_word_in(["film"], "a movie is a filmy thing"), "L1 matcher matches substrings"
    res["leak_regex_fires"] = True

    # (2) the comparator is live at tiny scale and the ONE variable actually varies.
    df = {"DIFF|wheel": 2, "DIFF|road": 3, "DIFF|engine": 1, "GENUS|vehicle": 4, "GENUS|animal": 5}
    wf = {"car": ["DIFF|wheel", "DIFF|engine", "GENUS|vehicle"],
          "truck": ["DIFF|wheel", "DIFF|road", "GENUS|vehicle"],
          "dog": ["GENUS|animal"]}
    sup = make_supply("selftest", wf, df, 100)
    v_u = sup.concept_vector(sup.word_feats["car"], None)
    v_w = sup.concept_vector(sup.word_feats["car"], sup.weights)
    assert v_u.shape == (N_DIM_BC,) and torch.isfinite(v_u.real).all(), "degenerate concept vector"
    assert not torch.equal(v_u, v_w), (
        "META_RULE_AF: UNIFORM and WEIGHTED produced a bit-identical vector")
    c_self = _cos_complex(v_u, v_u)
    assert abs(c_self - 1.0) < 1e-4, "cos(v,v)=%r" % c_self
    c_ct = _cos_complex(v_u, sup.concept_vector(sup.word_feats["truck"], None))
    c_cd = _cos_complex(v_u, sup.concept_vector(sup.word_feats["dog"], None))
    assert c_ct > c_cd, ("comparator not ordered: cos(car,truck)=%r <= cos(car,dog)=%r"
                         % (c_ct, c_cd))
    res["selftest_cos"] = {"self": round(c_self, 6), "car_truck": round(c_ct, 4),
                           "car_dog": round(c_cd, 4)}

    # (3) distinctiveness MOVES and is ordered the brain's way (rarer feature weighs more).
    assert sup.weights["DIFF|engine"] > sup.weights["GENUS|animal"] > 0, (
        "distinctiveness not ordered: %r" % sup.weights)
    res["w_rare"], res["w_common"] = (round(sup.weights["DIFF|engine"], 4),
                                     round(sup.weights["GENUS|animal"], 4))

    # (4) FORBIDDEN assertion actually rejects a ConceptNet edge.
    rejected = False
    try:
        make_supply("selftest_forbidden", {"car": ["/r/Synonym|/c/en/auto"]},
                    {"/r/Synonym|/c/en/auto": 1}, 100)
    except AssertionError:
        rejected = True
    assert rejected, "FORBIDDEN assertion did NOT reject a ConceptNet lexical-relation edge"
    res["forbidden_assertion_fires"] = True

    # (5) grounded control is live and non-sentinel; benchmark loads; filters pass >= 1 item.
    graw = grounded_raw_cos(grounded_vector("sofa"), grounded_vector("couch"))
    assert graw is not None and not math.isnan(graw), "grounded raw control returned %r" % graw
    res["grounded_raw_sofa_couch"] = round(float(graw), 4)
    pairs = load_simlex()
    assert len(pairs) == 999, "SimLex loaded %d pairs" % len(pairs)
    n_gnd = sum(1 for a, b, _ in pairs if in_grounded_lexicon(a) and in_grounded_lexicon(b))
    assert n_gnd >= 1, "grounded-lexicon filter eliminated ALL SimLex pairs"
    res["simlex_pairs"], res["pairs_both_grounded"] = len(pairs), n_gnd

    # (6) the paired bootstrap is wired, moves, and separates a real delta from a null one.
    g = list(np.linspace(0.0, 10.0, 60))
    good = [x + 0.01 * ((i * 37) % 7) for i, x in enumerate(g)]
    noise = list(np.random.default_rng(3).normal(size=60))
    bs, boot = paired_bootstrap({"good": good, "noise": noise}, g, 200, 1)
    d = delta_ci(boot, "good", "noise", _rho(good, g), _rho(noise, g))
    assert d["ci_low"] > 0.0 and not d["includes_zero"], (
        "bootstrap failed to separate a perfect arm from noise: %r" % d)
    d0 = delta_ci(boot, "noise", "noise", 0.0, 0.0)
    assert d0["includes_zero"], "bootstrap claims a self-delta is non-zero: %r" % d0
    res["bootstrap_selftest"] = {"good_vs_noise_ci_low": d["ci_low"],
                                 "self_delta_includes_zero": d0["includes_zero"]}

    # (7) the verdict function can return every band (no unreachable branch).
    fake_pos = {"point": 0.2, "ci_low": 0.1, "ci_high": 0.3, "includes_zero": False}
    fake_null = {"point": 0.0, "ci_low": -0.1, "ci_high": 0.1, "includes_zero": True}
    seen = sorted({classify(0.50, 0.20, 0.30, 0.08, 0.01, fake_pos, fake_pos, 0.66)[0],
                   classify(0.50, 0.20, 0.30, 0.08, 0.01, fake_null, fake_pos, 0.66)[0],
                   classify(0.20, 0.10, 0.30, 0.08, 0.01, fake_pos, fake_pos, 0.10)[0],
                   classify(0.20, 0.10, 0.30, 0.08, 0.40, fake_pos, fake_pos, 0.66)[0]})
    assert seen == ["HARD_FAIL", "HARD_PASS", "MIDDLE_BAND", "SUPPLY_REAL_BUT_THIN"], (
        "verdict bands not all reachable: %r" % seen)
    res["verdict_bands_reachable"] = seen

    # (8) declared validity preflight (F.1 real code path / F.2 live-signature binding).
    exercised = {"streamed_profile", "Supply", "_build_phases", "bundle", "_cos_complex",
                 "grounded_raw_cos", "_scrambled_assignment"}
    _scrambled_assignment(sup)          # exercise the REAL predecessor control, not a copy
    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["streamed_profile", "Supply", "_build_phases", "bundle",
                                        "_cos_complex", "grounded_raw_cos",
                                        "_scrambled_assignment"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": build_supply,
         "callable_name": "build_supply",
         "kwargs": {"name": "C_CSKG_NOLEXREL", "eval_vocab": [], "cskg_cache": None}},
        {"kind": "substrate_signature", "callable_obj": get_cskg_cache,
         "callable_name": "get_cskg_cache", "kwargs": {"vocab": set()}},
        {"kind": "metric_moves", "metric_name": "comparator_cosine",
         "before": float(c_cd), "after": float(c_ct)},
    ], run_mode="selftest")
    res["validity_preflight_ok"] = bool(ok)
    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, n_pairs: Optional[int]) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode)
    pairs_all = load_simlex(limit=n_pairs)
    full_vocab = {w for p in load_simlex() for w in p[:2]}
    recs, df_pop, supply_prov = load_treatment_store(full_vocab)
    v6_all, v6_strict, v6_prov = load_v6_genus(full_vocab)

    # ---- Arm D is built FIRST, because EVERY ARM MUST BE ON THE SAME PAIRS -------------------
    # The predecessor measured arm D's own supply coverage at 0.639 of SimLex (words whose ONLY
    # ConceptNet edges were the deleted lexical relations end up with no features at all --
    # `apparent`, `big`, `narrow`, ... ). A pair arm D cannot score is a pair the paired bootstrap
    # cannot use, so D-coverage is an ELIGIBILITY criterion alongside differentia-coverage and the
    # grounded lexicon, applied BEFORE the leak controls. The count lost to it is reported.
    cskg = get_cskg_cache(full_vocab)
    sup_d = build_supply("C_CSKG_NOLEXREL", sorted(full_vocab), cskg)    # PREDECESSOR's own code

    # ---- Coverage BEFORE leak controls -------------------------------------------------------
    diff_words = sorted({w for w, r in recs.items() if r.diff})
    diff_set = set(diff_words)
    cov_diff = [p for p in pairs_all if p[0] in diff_set and p[1] in diff_set]
    # Arm C needs the grounded lexicon; it covers 1028/1028 SimLex words
    # MEASURED@this cell 2026-08-13, so it does not restrict the set.
    cov_gnd = [p for p in cov_diff if in_grounded_lexicon(p[0]) and in_grounded_lexicon(p[1])]
    covered = [p for p in cov_gnd if p[0] in sup_d.word_feats and p[1] in sup_d.word_feats]
    n_lost_to_d = len(cov_gnd) - len(covered)
    print("[coverage] words_with_differentia=%d diff_pairs=%d grounded_pairs=%d "
          "same-pairs_after_armD=%d/%d (lost_to_armD_coverage=%d)"
          % (len(diff_words), len(cov_diff), len(cov_gnd), len(covered), len(pairs_all),
             n_lost_to_d), flush=True)

    # ---- STEP 2: LEAK CONTROLS (before any arm is scored) ------------------------------------
    survivors, leak = leak_controls(covered, recs)
    leak["coverage_before_controls_of_evaluated"] = round(len(covered) / len(pairs_all), 4)
    leak["eligibility_before_leak_controls"] = {
        "n_pairs_differentia_covered": len(cov_diff),
        "n_pairs_also_in_grounded_lexicon": len(cov_gnd),
        "n_pairs_also_scorable_by_arm_D": len(covered),
        "n_lost_to_arm_D_coverage": n_lost_to_d,
        "why": "every arm must be scored on the SAME pairs for the paired bootstrap; arm D has no "
               "features for words whose only ConceptNet edges were the deleted lexical relations"}
    n_surv = len(survivors)
    coverage999 = n_surv / 999.0

    if run_mode == "full" and n_surv < MIN_SURVIVING_PAIRS:
        msg = ("POWER GATE FAILED: %d pairs survive all three leak controls (< %d). Refusing to "
               "run an underpowered correlation." % (n_surv, MIN_SURVIVING_PAIRS))
        metrics = {"verdict": "STOP_UNDERPOWERED", "verdict_msg": msg,
                   "summary": "differentia supply -- leak controls left too few pairs",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "leak_controls": leak, "supply_provenance": supply_prov,
                   "v6_provenance": v6_prov, "n_surviving_pairs": n_surv,
                   "coverage_of_full_999": round(coverage999, 4),
                   "n_units": 0, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": False}
        _atomic_write_metrics(output_dir, metrics)
        print("[verdict] STOP_UNDERPOWERED -- %s" % msg, flush=True)
        return metrics

    golds = [g for _, _, g in survivors]
    eval_words = sorted({w for p in survivors for w in p[:2]})

    # ---- Supplies ----------------------------------------------------------------------------
    n_docs_pop = supply_prov["n_population_terms"]
    wf_diff = {w: sorted(recs[w].diff) for w in diff_words}
    wf_genus = {w: sorted(recs[w].genus | v6_all.get(w, set())) for w in diff_words}
    wf_genus_strict = {w: sorted(recs[w].genus | v6_strict.get(w, set())) for w in diff_words}
    df_b = dict(df_pop)
    for w, fs in list(wf_genus.items()) + list(wf_genus_strict.items()):
        for f in fs:
            df_b.setdefault(f, 1)          # v6-only genus heads absent from the simplewiki pop
    sup_a = make_supply("A_DIFFERENTIA", wf_diff, df_pop, n_docs_pop)
    sup_b = make_supply("B_GENUS_ONLY", wf_genus, df_b, n_docs_pop)
    sup_bs = make_supply("B_STRICT_GENUS", wf_genus_strict, df_b, n_docs_pop)
    sup_e = make_supply("E_SCRAMBLE", _scrambled_assignment(sup_a), df_pop, n_docs_pop)

    missing_d = [w for w in eval_words if w not in sup_d.word_feats]
    if missing_d:
        raise AssertionError("arm D lacks features for %d surviving words (e.g. %r); the arms "
                             "would not be on the same pairs" % (len(missing_d), missing_d[:8]))

    supplies = {"A_DIFFERENTIA": sup_a, "B_GENUS_ONLY": sup_b, "B_STRICT_GENUS": sup_bs,
                "D_CSKG_NOLEXREL": sup_d, "E_SCRAMBLE": sup_e}

    # ---- STEP 3: arms (per-unit checkpoint/resume) -------------------------------------------
    done = completed_units(output_dir)
    prior = load_units(output_dir)
    scores: Dict[str, List[float]] = {}
    digests: Dict[str, str] = {}
    unit_idx = 0
    for arm in FEATURE_ARMS:
        for comp in COMPARATORS:
            key = unit_key(arm, comp, run_mode, n_surv)
            unit_idx += 1
            if key in done:
                r = prior[key]
            else:
                sv = supply_scores(supplies[arm], survivors, comp == "WEIGHTED")
                arr = np.asarray(sv, dtype=np.float64)
                r = {"scores": sv, "rho": _rho(sv, golds), "n": n_surv,
                     "digest": hashlib.sha256(arr.tobytes()).hexdigest(),
                     "score_std": float(arr.std()),
                     "failure_class": "CONSTANT_SCORE_VECTOR" if arr.std() == 0.0 else None}
                record_unit(output_dir, key, r)
                _heartbeat(output_dir, unit_idx, EXPECTED_N_UNITS, time.time() - t0,
                           {"arm": arm, "comparator": comp, "rho": r["rho"]})
            tag = arm + "|" + comp
            scores[tag] = r["scores"]
            digests[tag] = r["digest"]
            print("[%s] rho=%.4f n=%d" % (tag, r["rho"], r["n"]), flush=True)

    key_c = unit_key("C_GROUNDED_RAW", "RAW", run_mode, n_surv)
    unit_idx += 1
    if key_c in done:
        rc = prior[key_c]
    else:
        sv = [float(grounded_raw_cos(grounded_vector(a), grounded_vector(b)))
              for a, b, _ in survivors]
        arr = np.asarray(sv, dtype=np.float64)
        rc = {"scores": sv, "rho": _rho(sv, golds), "n": n_surv,
              "digest": hashlib.sha256(arr.tobytes()).hexdigest(),
              "score_std": float(arr.std()),
              "failure_class": "CONSTANT_SCORE_VECTOR" if arr.std() == 0.0 else None}
        record_unit(output_dir, key_c, rc)
    scores["C_GROUNDED_RAW|RAW"] = rc["scores"]
    digests["C_GROUNDED_RAW|RAW"] = rc["digest"]
    print("[C_GROUNDED_RAW|RAW] rho=%.4f n=%d" % (rc["rho"], rc["n"]), flush=True)

    # META_RULE_AF: no two arms may be bit-identical.
    seen: Dict[str, str] = {}
    for tag in sorted(digests):
        d = digests[tag]
        if d in seen:
            raise AssertionError("META_RULE_AF VIOLATION: arms %r and %r bit-identical (%s)"
                                 % (seen[d], tag, d))
        seen[d] = tag

    rho = {tag: _rho(sv, golds) for tag, sv in scores.items()}

    # ---- PRIMARY = UNIFORM comparator (A1.3) -------------------------------------------------
    P = {"A": "A_DIFFERENTIA|UNIFORM", "B": "B_GENUS_ONLY|UNIFORM",
         "B_STRICT": "B_STRICT_GENUS|UNIFORM", "C": "C_GROUNDED_RAW|RAW",
         "D": "D_CSKG_NOLEXREL|UNIFORM", "E": "E_SCRAMBLE|UNIFORM"}
    primary_scores = {k: scores[v] for k, v in P.items()}
    bs, boot = paired_bootstrap(primary_scores, golds, N_BOOTSTRAP, BOOTSTRAP_SEED)
    deltas = {
        "A_minus_B": delta_ci(boot, "A", "B", rho[P["A"]], rho[P["B"]]),
        "A_minus_C": delta_ci(boot, "A", "C", rho[P["A"]], rho[P["C"]]),
        "A_minus_D": delta_ci(boot, "A", "D", rho[P["A"]], rho[P["D"]]),
        "A_minus_B_STRICT": delta_ci(boot, "A", "B_STRICT", rho[P["A"]], rho[P["B_STRICT"]]),
        "A_minus_E": delta_ci(boot, "A", "E", rho[P["A"]], rho[P["E"]]),
    }
    # Same deltas under the reported-only WEIGHTED comparator.
    wP = {"A": "A_DIFFERENTIA|WEIGHTED", "B": "B_GENUS_ONLY|WEIGHTED",
          "C": "C_GROUNDED_RAW|RAW", "D": "D_CSKG_NOLEXREL|WEIGHTED",
          "E": "E_SCRAMBLE|WEIGHTED"}
    bs_w, boot_w = paired_bootstrap({k: scores[v] for k, v in wP.items()}, golds,
                                    N_BOOTSTRAP, BOOTSTRAP_SEED)
    deltas_w = {
        "A_minus_B": delta_ci(boot_w, "A", "B", rho[wP["A"]], rho[wP["B"]]),
        "A_minus_C": delta_ci(boot_w, "A", "C", rho[wP["A"]], rho[wP["C"]]),
        "A_minus_D": delta_ci(boot_w, "A", "D", rho[wP["A"]], rho[wP["D"]]),
    }

    verdict, notes = classify(rho[P["A"]], rho[P["B"]], rho[P["C"]], rho[P["D"]], rho[P["E"]],
                              deltas["A_minus_B"], deltas["A_minus_C"], coverage999)

    # ---- Positive control (SCHEMA-VET gate D): arm D reproduces the predecessor AT ITS REGIME --
    prior_pairs = [p for p in load_simlex()
                   if p[0] in sup_d.word_feats and p[1] in sup_d.word_feats
                   and in_grounded_lexicon(p[0]) and in_grounded_lexicon(p[1])]
    d_repro_rho = _rho(supply_scores(sup_d, prior_pairs, True), [g for _, _, g in prior_pairs])
    d_repro = {"n": len(prior_pairs), "prior_n": D_PRIOR_N,
               "rho_weighted": round(d_repro_rho, 4), "prior_rho_weighted": D_PRIOR_RHO_WEIGHTED,
               "abs_deviation": round(abs(d_repro_rho - D_PRIOR_RHO_WEIGHTED), 4),
               "tolerance": D_REPRO_TOL,
               "reproduced": bool(abs(d_repro_rho - D_PRIOR_RHO_WEIGHTED) <= D_REPRO_TOL
                                  and len(prior_pairs) == D_PRIOR_N)}
    if not d_repro["reproduced"]:
        notes.append("POSITIVE-CONTROL WARNING: arm D did not reproduce the predecessor at its own "
                     "regime (%r); arm D's value on the surviving pairs is suspect." % d_repro)

    diag = {
        "analytic_incidence_rho_A": round(_rho(analytic_incidence_cosine(sup_a, survivors),
                                               golds), 4),
        "analytic_incidence_rho_B": round(_rho(analytic_incidence_cosine(sup_b, survivors),
                                               golds), 4),
        "median_diff_features_per_word": int(np.median([len(sup_a.word_feats[w])
                                                        for w in eval_words])),
        "median_genus_features_per_word": int(np.median([len(sup_b.word_feats[w])
                                                         for w in eval_words])),
        "n_features_A": len(sup_a.weights), "n_features_B": len(sup_b.weights),
        "n_features_D": len(sup_d.weights),
        "baseline_in_band_B": bool(0.05 < abs(rho[P["B"]]) < 0.95),
        "se_rho_naive_independent_NOT_USED": round(1.0 / math.sqrt(max(n_surv - 1, 1)), 4),
    }

    units = load_units(output_dir)
    cardinality_ok = len(units) >= EXPECTED_N_UNITS
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    msg = ("n_surviving=%d (L1=%d L2=%d L3=%d union=%d of %d covered) | A=%.4f B=%.4f C=%.4f "
           "D=%.4f E=%.4f | A-B=%+.4f [%.4f,%.4f] A-C=%+.4f [%.4f,%.4f] A-D=%+.4f [%.4f,%.4f] | "
           "coverage999=%.3f"
           % (n_surv, leak["L1_direct_leak"]["n"], leak["L2_synonym_statement_leak"]["n"],
              leak["L3_source_sentence_overlap"]["n"], leak["n_excluded_union"], len(covered),
              rho[P["A"]], rho[P["B"]], rho[P["C"]], rho[P["D"]], rho[P["E"]],
              deltas["A_minus_B"]["point"], deltas["A_minus_B"]["ci_low"],
              deltas["A_minus_B"]["ci_high"],
              deltas["A_minus_C"]["point"], deltas["A_minus_C"]["ci_low"],
              deltas["A_minus_C"]["ci_high"],
              deltas["A_minus_D"]["point"], deltas["A_minus_D"]["ci_low"],
              deltas["A_minus_D"]["ci_high"], coverage999))

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "notes": notes,
        "summary": "extractor-derived DIFFERENTIA supply vs genus / grounded / CSKG on SimLex-999",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
        "prereg_amendment": "A1 (commit 64a4ea4c2), filed BEFORE extraction and BEFORE any arm",
        "pattern_restriction_frozen_in_advance": {
            "treatment": list(TREATMENT_PATTERNS), "forbidden": list(FORBIDDEN_PATTERNS),
            "patterns_present_in_supply": supply_prov["patterns_present"],
            "forbidden_present_in_supply": supply_prov["forbidden_present"],
            "assertion": "PASS"},
        "forbidden_conceptnet_edges_in_treatment_arms": {
            "asserted": "no feature token in A/B/E begins with '/r/'", "result": "PASS"},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_units": len(units), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok, "arms_differ_verified": True,
        "arm_digests": digests,
        "leak_controls": leak,
        "n_pairs_evaluated_before_controls": len(covered),
        "n_surviving_pairs": n_surv,
        "coverage_of_full_999": round(coverage999, 4),
        "primary_comparator": "UNIFORM",
        "rho_primary": {k: round(rho[v], 4) for k, v in P.items()},
        "rho_all_units": {k: round(v, 4) for k, v in rho.items()},
        "bootstrap": bs, "bootstrap_weighted_secondary": bs_w,
        "deltas_primary": deltas, "deltas_weighted_secondary": deltas_w,
        "bands": {"HP_RHO_MIN": HP_RHO_MIN, "HP_SCRAMBLE_MAX": HP_SCRAMBLE_MAX,
                  "MIN_SURVIVING_PAIRS": MIN_SURVIVING_PAIRS, "THIN_COVERAGE": THIN_COVERAGE,
                  "HARD_FAIL": "CI(A-B) includes 0 OR A <= D",
                  "HARD_PASS": "A>=0.35 AND CI_low(A-C)>0 AND CI_low(A-B)>0 AND E<=0.05"},
        "public_calibration_not_arms": CALIBRATION,
        "positive_control_D_reproduces_predecessor": d_repro,
        "diagnostics": diag,
        "supply_provenance": supply_prov, "v6_provenance": v6_prov,
        "hdlab_modified": False,
        "units": {k: {kk: vv for kk, vv in v.items() if kk != "scores"}
                  for k, v in units.items()},
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (verdict, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--pairs", type=int, default=None)
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        for n in SMOKE_PAIR_SCALES:              # multi-scale smoke
            out = OUT_SMOKE + "_p%d" % n
            print("=== SMOKE at %d pairs -> %s ===" % (n, out), flush=True)
            m = run("smoke", out, n)
            if m["n_surviving_pairs"] < 10:
                raise AssertionError("VACUOUS SMOKE at %d pairs: only %d pairs survive"
                                     % (n, m["n_surviving_pairs"]))
            r = m["rho_primary"]
            if r["A"] == r["B"]:
                raise AssertionError("VACUOUS SMOKE: A and B rho identical (%.4f)" % r["A"])
            # DISCRIMINATOR-FIRES: the scramble control MUST collapse where the treatment carries
            # signal. Where the treatment is itself at the floor there is nothing to falsify, and
            # asserting there would be mis-specified rather than informative (same scoping the
            # predecessor cell arrived at and DISCLOSED).
            if r["A"] >= 0.20:
                if not (r["E"] <= HP_SCRAMBLE_MAX or r["E"] < r["A"] - 0.10):
                    raise AssertionError(
                        "VACUOUS SMOKE at %d pairs: SCRAMBLE rho=%.4f did not collapse against "
                        "A rho=%.4f; the discriminator does not fire." % (n, r["E"], r["A"]))
                print("[smoke] discriminator fired (A=%.4f, scramble=%.4f)" % (r["A"], r["E"]),
                      flush=True)
            else:
                print("[smoke] A=%.4f at floor; scramble assertion not applicable at this scale"
                      % r["A"], flush=True)
            if abs(r["B"]) >= 0.95:
                raise AssertionError("META_RULE_AG: baseline B saturated at %.4f" % r["B"])
        print("SMOKE=PASS (all scales)", flush=True)
        return
    run("full", OUT_FULL, args.pairs)


_SELFTEST_RESULT = _instrumentation_selftest()      # module scope, before any sweep

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                          # NOT BaseException
        _write_crash_metrics(OUT_SMOKE if "smoke" in sys.argv else OUT_FULL, _e)
        raise
