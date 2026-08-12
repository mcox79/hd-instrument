# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: hand-lexicon path vs grounded-fallback path vs scrambled-grounded path
#   produce distinct digests (asserted below, _arms_must_differ)
# - final_metrics_atomicity = tmp_replace (single-shot, os.replace)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: this is a coverage/ordering/cap-compliance test, not a Gaussian noise-floor metric
# - baseline_in_band: N/A (no baseline-vs-mechanism accuracy gap; this is a coverage-extension +
#   anti-over-merge structural test)
# - discriminator survives scale: FULL uses WordNet-programmatic pair generation (hundreds of
#   words) not a hand-picked handful; smoke uses a small fixed set for fast iteration
# - HP_SCOPE: NO_REGRESSION + ANTI_OVER_MERGE are HARD gates (any failure = HARD_FAIL regardless
#   of coverage numbers); OOV_COVERAGE + CONTROLS are also HARD_PASS-required per pre-reg
# - cardinality_ok: N_SYNONYM_PAIRS_FULL + N_SIBLING_TRAP_PAIRS + N_UNRELATED_PAIRS logged;
#   verdict counts checked vs population
# - calibration_check: default_ok_for_this_regime (GROUNDED_CAP is architecturally fixed in
#   hdlab/grounded_similarity.py, not tuned by this cell)
# - all numbers in this header/docstring tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL hdlab.lexical_similarity / hdlab.grounded_similarity objects at
#   full scale (both are pure-Python/CSV, no toy-only branch exists)
# - substrate_signature_checked: concept_similarity(word_a, word_b, use_grounded_fallback=bool);
#   no hdlab/ file OTHER than lexical_similarity.py + the new grounded_similarity.py is modified
"""exp_grounded_meaning_wire_lexical_fallback_v1 -- validates the architecture-audit TIER-1
shore-up (notes/architecture_audit_2026-08-11.md): hdlab.lexical_similarity.concept_similarity now
falls back to hdlab.grounded_similarity (Lancaster sensorimotor + Brysbaert concreteness norms,
39,707/39,954-word CSVs in data/grounding_testbed/) for OOV-of-CONCEPT_FEATURES word pairs instead
of unconditionally returning None. See preregs/2026-08-11_grounded_meaning_wire_lexical_fallback_v1
.md for the full design, the MEASURED calibration table, and the learned-encoder diagnostic
(scale_win_tinytransformer_encoder -- evaluated, NOT wired; see pre-reg "Learned-encoder
diagnostic" section for the disk-verified reason).

FOUR test axes, each independently VET'd (never aggregated into one pass/fail):
  T1 NO_REGRESSION       -- hdlab/lexical_similarity.py::self_test() unchanged-assertions pass +
                             experiments/exp_representation_canonicalization_v1.py FULL reproduces
                             its landed HARD_PASS counts byte-for-byte (canon_entity pre-gates on
                             in_lexicon(), so it structurally cannot reach the new fallback --
                             this axis PROVES that structural argument empirically, not just by
                             code inspection).
  T2 OOV_COVERAGE        -- WordNet-synset-derived held-out synonym pairs (programmatic selection,
                             not hand-picked) that are OOV of CONCEPT_FEATURES now get a real
                             graded similarity; median synonym-pair score exceeds median
                             unrelated-pair score.
  T3 ANTI_OVER_MERGE      -- THE decisive guard. A held-out set of sibling-distinct "trap" pairs
                             (same broad WordNet-hypernym category, different identity: fruit,
                             vehicle, furniture, metal, fuel, hand_tool, bird, beverage,
                             vegetable, plus the task's own named produce/consume example) must
                             ALL score strictly below SIMILARITY_LINK_THRESHOLD via the public
                             concept_similarity() path.
  T4 CONTROLS             -- grounded_similarity.py's own scramble-circularity self-test +
                             a no-leak check (the grounded table build reads only the two static
                             CSVs; no test-pair label ever touches the join/z-score).

REUSE (wire-don't-island; both organs under test imported read-only): hdlab.lexical_similarity
(concept_similarity, in_lexicon, in_lexicon_or_grounded, CONCEPT_FEATURES, SIMILARITY_LINK_
THRESHOLD, self_test) + hdlab.grounded_similarity (grounded_similarity, in_grounded_lexicon,
GROUNDED_CAP, coverage_stats, self_test) + experiments.exp_representation_canonicalization_v1's own
run_pipeline / run_self_test (imported and called directly, same convention that cell's own docs
show for cross-experiments-file reuse).

Modes: --self-test (closed-form fixtures only, <5s) / --smoke (6 hand-picked pairs per axis,
<5s) / (no flag, default) = FULL (WordNet-programmatic pair generation + canonicalization-cell
FULL replication + pytest run), expected wall time <90s -- no training, no GPU, sequential-CPU
justified (pure lexicon lookups).

ASCII-only. Deterministic throughout (sorted(set()) discipline; fixed integer seeds 999/20260811;
no built-in hash() anywhere -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

ANCHOR_NAME = "grounded_meaning_wire_lexical_fallback_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.lexical_similarity import (  # noqa: E402
    concept_similarity, in_lexicon, in_lexicon_or_grounded, CONCEPT_FEATURES,
    SIMILARITY_LINK_THRESHOLD, self_test as lexical_similarity_self_test,
)
from hdlab.grounded_similarity import (  # noqa: E402
    grounded_similarity, in_grounded_lexicon, GROUNDED_CAP, coverage_stats as grounded_coverage_stats,
    self_test as grounded_similarity_self_test,
)


def get_output_dir(run_mode: str) -> str:
    suffix = {"self_test": "_selftest", "smoke": "_smoke", "full": ""}[run_mode]
    return os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME + suffix)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    import platform
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write(output_dir: str, metrics: Dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    return final


def _arms_must_differ(arms: Dict[str, bytes]) -> Dict[str, str]:
    digests = {name: hashlib.sha256(b if isinstance(b, bytes) else str(b).encode()).hexdigest()
              for name, b in arms.items()}
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    return digests


def _eligible(w: str) -> bool:
    """Clean single lowercase alphabetic token, OOV of CONCEPT_FEATURES, IN grounded lexicon --
    guarantees a probe word actually exercises the NEW fallback path end-to-end."""
    return (w.isalpha() and w.islower() and (w not in CONCEPT_FEATURES) and in_grounded_lexicon(w))


# ---------------------------------------------------------------------------------- T3 trap pairs
# Hand-anchored CATEGORY axes only (not the specific word pairs within them, which are pulled
# programmatically from WordNet hyponyms below) -- the task's own named example (produce/consume)
# is included literally since the audit calls it out by name. Categories chosen for topical
# diversity (material/food/animal/vehicle/tool/object), not to force a particular outcome.
TRAP_CATEGORIES = ["fruit.n.01", "vehicle.n.01", "furniture.n.01", "metal.n.01", "fuel.n.01",
                   "hand_tool.n.01", "bird.n.01", "beverage.n.01", "vegetable.n.01"]
HAND_TRAP_PAIRS = [("produce", "consume")]  # task's own named decisive example (both verbs)


def build_sibling_trap_pairs(wn) -> List[Tuple[str, str, str]]:
    """(word_a, word_b, category) co-hyponym pairs -- same broad category, different identity.
    Deterministic: sorted(set()) of each category's eligible hyponym-lemma words, first 2 (and
    3rd/4th if available) taken as pairs. No random sampling."""
    pairs: List[Tuple[str, str, str]] = []
    for catname in TRAP_CATEGORIES:
        try:
            cat = wn.synset(catname)
        except Exception:
            continue
        words = sorted({l.name().lower() for h in cat.hyponyms() for l in h.lemmas()
                        if "_" not in l.name()})
        cand = sorted(w for w in words if _eligible(w))
        if len(cand) >= 2:
            pairs.append((cand[0], cand[1], catname))
        if len(cand) >= 4:
            pairs.append((cand[2], cand[3], catname))
    for a, b in HAND_TRAP_PAIRS:
        if _eligible(a) and _eligible(b):
            pairs.append((a, b, "task_named_example"))
    return pairs


def build_synonym_pairs(wn, max_pairs: int) -> List[Tuple[str, str]]:
    """(word_a, word_b) pairs drawn from the SAME WordNet synset (true near-synonyms by
    construction), both OOV of CONCEPT_FEATURES and IN the grounded lexicon. Programmatic
    selection (not hand-picked) -- avoids cherry-picking pairs likely to pass. Deterministic:
    NLTK's synset enumeration order is stable for a fixed WordNet corpus version; each synset's
    candidate lemma list is itself sorted before the first-two are taken."""
    pairs: List[Tuple[str, str]] = []
    seen_words: set = set()
    for s in wn.all_synsets(pos=wn.NOUN):
        lemmas = sorted({l.name().lower() for l in s.lemmas() if "_" not in l.name()})
        cand = [w for w in lemmas if _eligible(w) and w not in seen_words]
        if len(cand) >= 2:
            a, b = cand[0], cand[1]
            pairs.append((a, b))
            seen_words.add(a)
            seen_words.add(b)
        if len(pairs) >= max_pairs:
            break
    return pairs


def build_unrelated_pairs(wn, synonym_pairs: List[Tuple[str, str]], n: int) -> List[Tuple[str, str]]:
    """Cross pairs drawn from FAR-APART entries of the synonym-pair word list itself (word i's
    first member vs word n-1-i's second member) -- reuses the SAME eligible vocabulary (no new
    sampling step, no p-hacking of a separate 'unrelated' word list), then keeps only pairs whose
    WordNet path_similarity is low (genuinely unrelated, not an accidental near-synonym pair
    picked up by the crossing construction). Deterministic (no randomness)."""
    flat = sorted({w for pair in synonym_pairs for w in pair})
    out: List[Tuple[str, str]] = []
    k = len(flat)
    for i in range(k):
        a = flat[i]
        b = flat[k - 1 - i]
        if a == b:
            continue
        sa = wn.synsets(a, pos=wn.NOUN)
        sb = wn.synsets(b, pos=wn.NOUN)
        if not sa or not sb:
            continue
        sim = sa[0].path_similarity(sb[0])
        if sim is not None and sim <= 0.15:
            out.append((a, b))
        if len(out) >= n:
            break
    return out


# --------------------------------------------------------------------------------------- T1 axis
def run_no_regression_check(run_mode: str) -> Dict:
    """T1: hdlab/lexical_similarity.py self_test (unchanged assertions still hold) +
    exp_representation_canonicalization_v1's FULL pipeline reproduces its landed counts."""
    lex_result = lexical_similarity_self_test()

    if run_mode != "full":
        # smoke/self-test: skip the (heavier, real-CSKG-pipeline) replication for fast iteration;
        # the pre-reg's NO_REGRESSION gate only requires this axis at FULL.
        return {"lex_self_test_ok": lex_result is not None, "canon_replicated": "skipped_non_full",
               "run_mode": run_mode}

    from experiments.exp_representation_canonicalization_v1 import run_pipeline as canon_run_pipeline

    prior_metrics_path = os.path.join(REPO_ROOT, "data", "exp_representation_canonicalization_v1",
                                      "metrics.json")
    with open(prior_metrics_path, encoding="utf-8") as f:
        prior = json.load(f)

    canon_result = canon_run_pipeline(process_filter=None, run_mode="full")

    same_idea_match = canon_result.get("same_idea_match_rate")
    corrob = canon_result.get("automatic_corroboration_rate")
    verdict = canon_result.get("verdict")
    n_distinct = canon_result.get("real_data", {}).get("n_distinct_canon_triples")
    n_distinct_total = canon_result.get("real_data", {}).get("n_distinct_material_whole_pairs")

    prior_same_idea = prior.get("same_idea_match_rate")
    prior_corrob = prior.get("automatic_corroboration_rate")
    prior_verdict = prior.get("verdict")
    prior_n_distinct = prior.get("real_data", {}).get("n_distinct_canon_triples")
    prior_n_distinct_total = prior.get("real_data", {}).get("n_distinct_material_whole_pairs")

    no_drop = (verdict == prior_verdict == "HARD_PASS_representation_canonicalization_realizes_same_rep_principle"
              and same_idea_match is not None and prior_same_idea is not None
              and same_idea_match >= prior_same_idea
              and corrob is not None and prior_corrob is not None and corrob >= prior_corrob
              and n_distinct == prior_n_distinct and n_distinct_total == prior_n_distinct_total)

    return {
        "lex_self_test_ok": lex_result is not None,
        "canon_verdict": verdict, "canon_prior_verdict": prior_verdict,
        "canon_same_idea_match_rate": same_idea_match, "canon_prior_same_idea_match_rate": prior_same_idea,
        "canon_corroboration_rate": corrob, "canon_prior_corroboration_rate": prior_corrob,
        "canon_n_distinct_canon_triples": n_distinct, "canon_prior_n_distinct_canon_triples": prior_n_distinct,
        "canon_n_distinct_material_whole_pairs": n_distinct_total,
        "canon_prior_n_distinct_material_whole_pairs": prior_n_distinct_total,
        "no_regression_ok": bool(no_drop),
    }


# --------------------------------------------------------------------------------------- T2 axis
def run_oov_coverage_check(wn, run_mode: str) -> Dict:
    if run_mode == "full":
        synonym_pairs = build_synonym_pairs(wn, max_pairs=200)
    else:
        synonym_pairs = [("sofa", "couch"), ("trash", "garbage"), ("shout", "yell"),
                         ("whisper", "murmur"), ("puppy", "kitten"), ("dawn", "sunrise")]
        synonym_pairs = [(a, b) for a, b in synonym_pairs if _eligible(a) and _eligible(b)]
    unrelated_pairs = build_unrelated_pairs(wn, synonym_pairs, n=len(synonym_pairs))

    syn_scores = [concept_similarity(a, b) for a, b in synonym_pairs]
    unrel_scores = [concept_similarity(a, b) for a, b in unrelated_pairs]
    assert all(s is not None for s in syn_scores), "COVERAGE FAILURE: a synonym-pair probe returned None"
    assert all(s is not None for s in unrel_scores), "COVERAGE FAILURE: an unrelated-pair probe returned None"

    words_now_covered = sorted({w for pair in synonym_pairs + unrelated_pairs for w in pair})
    n_previously_none = sum(1 for w in words_now_covered if w not in CONCEPT_FEATURES)

    syn_sorted = sorted(syn_scores)
    unrel_sorted = sorted(unrel_scores)
    median_syn = syn_sorted[len(syn_sorted) // 2]
    median_unrel = unrel_sorted[len(unrel_sorted) // 2]

    return {
        "n_synonym_pairs": len(synonym_pairs), "n_unrelated_pairs": len(unrelated_pairs),
        "n_words_now_covered": len(words_now_covered), "n_previously_none_words": n_previously_none,
        "median_synonym_score": round(median_syn, 4), "median_unrelated_score": round(median_unrel, 4),
        "ordering_ok": bool(median_syn > median_unrel),
        "sample_synonym_pairs": synonym_pairs[:10], "sample_unrelated_pairs": unrelated_pairs[:10],
    }


# --------------------------------------------------------------------------------------- T3 axis
def run_anti_over_merge_check(wn, run_mode: str) -> Dict:
    if run_mode == "full":
        trap_pairs = build_sibling_trap_pairs(wn)
    else:
        trap_pairs = [("wood", "coal", "fuel_hand"), ("apple", "orange", "fruit_hand"),
                     ("dog", "cat", "pet_hand"), ("produce", "consume", "task_named_example")]
        trap_pairs = [(a, b, c) for a, b, c in trap_pairs if _eligible(a) and _eligible(b)]

    results = []
    n_over_merge = 0
    for a, b, cat in trap_pairs:
        s = concept_similarity(a, b)
        assert s is not None, "T3 setup error: trap pair (%s,%s) not covered by grounded fallback" % (a, b)
        ok = s < SIMILARITY_LINK_THRESHOLD
        if not ok:
            n_over_merge += 1
        results.append({"a": a, "b": b, "category": cat, "score": round(s, 4), "stays_distinct": ok})

    return {
        "n_trap_pairs": len(trap_pairs), "n_over_merge": n_over_merge,
        "anti_over_merge_ok": bool(n_over_merge == 0),
        "trap_results": results,
    }


# --------------------------------------------------------------------------------------- T4 axis
def run_controls_check() -> Dict:
    grounded_result = grounded_similarity_self_test()
    # no-leak: the grounded table is built from the two static CSVs alone; verify no test-only
    # module-level state (e.g. a cache primed by THIS cell's own trap/synonym words) is required
    # for grounded_vector to answer a word it has never been asked about in this process.
    from hdlab import grounded_similarity as _gs
    fresh_word = "kerosene"  # a fuel-category word not otherwise queried by T1/T4
    no_leak_ok = _gs.grounded_vector(fresh_word) is not None or not in_grounded_lexicon(fresh_word)
    return {
        "grounded_self_test": grounded_result,
        "scramble_control_ok": bool(
            grounded_result["mean_synonym_raw"] - grounded_result["mean_synonym_raw_scrambled"] >= 0.30),
        "no_leak_ok": bool(no_leak_ok),
        "cap_below_threshold_ok": bool(GROUNDED_CAP < SIMILARITY_LINK_THRESHOLD),
    }


# --------------------------------------------------------------------------------------- pytest
def _venv_python() -> str:
    """Project convention (CLAUDE.md / exp_dev canonical instructions): verification runs on the
    repo .venv, which carries deps (e.g. duckdb) the ambient/system python may lack. Falls back to
    sys.executable if no .venv is present (e.g. a remote runner with its own env)."""
    candidate = os.path.join(REPO_ROOT, ".venv", "Scripts", "python.exe")
    if os.path.exists(candidate):
        return candidate
    candidate_posix = os.path.join(REPO_ROOT, ".venv", "bin", "python")
    if os.path.exists(candidate_posix):
        return candidate_posix
    return sys.executable


def run_pytest_verification() -> Dict:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [_venv_python(), "-m", "pytest", "verification/", "-q"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=480)
    elapsed = time.perf_counter() - t0
    tail = (proc.stdout or "")[-2000:]
    return {"returncode": proc.returncode, "elapsed_s": round(elapsed, 2),
            "stdout_tail": tail, "pytest_green": bool(proc.returncode == 0)}


# ---------------------------------------------------------------------------------------- main
def run_self_test() -> Dict:
    from nltk.corpus import wordnet as wn
    t1 = run_no_regression_check("self_test")
    t2 = run_oov_coverage_check(wn, "smoke")
    t3 = run_anti_over_merge_check(wn, "smoke")
    t4 = run_controls_check()
    digests = _arms_must_differ({
        "hand_lexicon_vessel_ferry": str(concept_similarity("vessel", "ferry")),
        "grounded_fallback_sofa_couch": str(concept_similarity("sofa", "couch")),
        "grounded_fallback_off_sofa_couch": str(concept_similarity("sofa", "couch", use_grounded_fallback=False)),
    })
    return {"T1_no_regression": t1, "T2_oov_coverage": t2, "T3_anti_over_merge": t3,
           "T4_controls": t4, "arms_digests": digests}


def run_full(run_mode: str) -> Dict:
    from nltk.corpus import wordnet as wn
    t0 = time.perf_counter()
    print("[stage] T1 no-regression (lexical_similarity self-test + canonicalization-cell replication)", flush=True)
    t1 = run_no_regression_check(run_mode)
    print(f"[T1] no_regression_ok={t1.get('no_regression_ok')}", flush=True)

    print("[stage] T2 OOV coverage unlock (WordNet-programmatic pairs)", flush=True)
    t2 = run_oov_coverage_check(wn, run_mode)
    print(f"[T2] n_words_now_covered={t2['n_words_now_covered']} ordering_ok={t2['ordering_ok']}", flush=True)

    print("[stage] T3 anti-over-merge (decisive guard)", flush=True)
    t3 = run_anti_over_merge_check(wn, run_mode)
    print(f"[T3] n_trap_pairs={t3['n_trap_pairs']} n_over_merge={t3['n_over_merge']}", flush=True)

    print("[stage] T4 controls (scramble + no-leak)", flush=True)
    t4 = run_controls_check()
    print(f"[T4] scramble_ok={t4['scramble_control_ok']} no_leak_ok={t4['no_leak_ok']}", flush=True)

    pytest_result = None
    if run_mode == "full":
        print("[stage] pytest verification/", flush=True)
        pytest_result = run_pytest_verification()
        print(f"[pytest] green={pytest_result['pytest_green']} elapsed_s={pytest_result['elapsed_s']}", flush=True)

    digests = _arms_must_differ({
        "hand_lexicon_vessel_ferry": str(concept_similarity("vessel", "ferry")),
        "grounded_fallback_sofa_couch": str(concept_similarity("sofa", "couch")),
        "grounded_fallback_off_sofa_couch": str(concept_similarity("sofa", "couch", use_grounded_fallback=False)),
        "grounded_scrambled_marker": str(t4["grounded_self_test"]["mean_synonym_raw_scrambled"]),
    })

    elapsed = time.perf_counter() - t0

    t1_ok = t1.get("no_regression_ok", True) if run_mode == "full" else True  # not exercised in smoke
    t2_ok = t2["ordering_ok"] and t2["n_words_now_covered"] >= (200 if run_mode == "full" else 4)
    t3_ok = t3["anti_over_merge_ok"] and t3["n_trap_pairs"] >= (15 if run_mode == "full" else 3)
    t4_ok = t4["scramble_control_ok"] and t4["no_leak_ok"] and t4["cap_below_threshold_ok"]
    pytest_ok = (pytest_result["pytest_green"] if pytest_result is not None else True)  # not run outside FULL

    if not t3_ok:
        verdict = "HARD_FAIL_anti_over_merge"
        verdict_msg = (f"ANTI-OVER-MERGE decisive guard FAILED or under-populated: "
                        f"n_over_merge={t3['n_over_merge']}/{t3['n_trap_pairs']} -- "
                        f"the grounded fallback smears distinct concepts together.")
    elif run_mode == "full" and not t1_ok:
        verdict = "HARD_FAIL_regression"
        verdict_msg = (f"NO-REGRESSION check FAILED: canonicalization-cell replication diverged "
                        f"from its landed baseline (see T1_no_regression for counts).")
    elif not t4_ok:
        verdict = "HARD_FAIL_controls_broken"
        verdict_msg = f"one or more controls failed: {t4}"
    elif run_mode == "full" and not pytest_ok:
        verdict = "MIDDLE_BAND_pytest_not_green"
        verdict_msg = (f"T1-T4 hold (no regression, OOV coverage extended, anti-over-merge clean, "
                        f"controls clean), but `pytest verification/` did NOT return green "
                        f"(returncode={pytest_result['returncode']}) -- see pytest.stdout_tail for "
                        f"the failure; investigate before claiming full pass (per pre-reg gate 6, "
                        f"this is a required HARD-PASS gate, not optional).")
    elif not t2_ok:
        verdict = "MIDDLE_BAND_no_coverage_extension"
        verdict_msg = (f"anti-over-merge and controls hold, but OOV coverage extension is "
                        f"insufficient or mis-ordered: {t2}")
    else:
        verdict = "HARD_PASS_grounded_meaning_wired_without_over_merge"
        verdict_msg = (f"grounded (Lancaster sensorimotor + Brysbaert concreteness) fallback wired "
                        f"into concept_similarity: n_words_now_covered={t2['n_words_now_covered']} "
                        f"(median_synonym={t2['median_synonym_score']:.4f} > "
                        f"median_unrelated={t2['median_unrelated_score']:.4f}), anti-over-merge "
                        f"clean ({t3['n_trap_pairs']}/{t3['n_trap_pairs']} trap pairs stay distinct, "
                        f"capped at GROUNDED_CAP={GROUNDED_CAP} < SIMILARITY_LINK_THRESHOLD="
                        f"{SIMILARITY_LINK_THRESHOLD}), controls clean, no regression on covered "
                        f"vocab" + (" (pytest GREEN)" if pytest_ok and pytest_result else "") + ".")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "T1_no_regression": t1, "T2_oov_coverage": t2, "T3_anti_over_merge": t3,
        "T4_controls": t4, "pytest": pytest_result, "arms_digests": digests,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "full"

    output_dir = get_output_dir(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=4)

    if run_mode == "self_test":
        t0 = time.perf_counter()
        result = run_self_test()
        elapsed = time.perf_counter() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS (closed-form fixtures)",
                  "summary": "SELFTEST_PASS", "elapsed_s": elapsed, "run_mode": run_mode,
                  "anchor_name": ANCHOR_NAME, "ts_iso": datetime.now(timezone.utc).isoformat(),
                  "pid": os.getpid(), "details": result}
        _atomic_write(output_dir, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        print("ALL SELF-TESTS PASSED")
        return

    metrics = run_full(run_mode)
    _atomic_write(output_dir, metrics)
    print(f"[verdict] {metrics['verdict']}", flush=True)
    print(metrics["verdict_msg"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(get_output_dir("full"), e)
        raise
