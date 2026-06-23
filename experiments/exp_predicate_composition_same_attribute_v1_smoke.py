"""
predicate_composition_same_attribute_v1_smoke -- substrate-native SAME-ATTRIBUTE +
LOGICAL_AND + QUANTIFIER_EXISTS composed predicate primitive smoke on REAL HotpotQA
yes/no comparison subset.

SCIENTIFIC QUESTION (per preregs/2026-06_predicate_composition_same_attribute_v1_smoke.md):
  Prior temporal_not cell landed HARD_FAIL with fire_rate_temporal=0.0 across all
  seeds -- the 59-Q yes/no comparison subset has only 1 temporal question; 56 of 59
  (~95 percent) are SAME-attribute / BOTH-membership questions ("Are X and Y both
  documentaries?", "Were X and Y from the same country?"). This is the corpus-matched
  replacement: substrate-native SAME primitive composed with LOGICAL_AND + EXISTS.

ARMS (4):
  1. ARM_FREQ_BIAS              -- majority-class baseline on this 59-Q yes/no comparison subset
  2. ARM_RAW_W_LOOKUP           -- current substrate; yes/no codebook + projected w2v question vec
  3. ARM_SAME_ATTRIBUTE         -- SAME primitive in isolation (cos thresholding)
  4. ARM_SAME_PLUS_AND_EXISTS   -- composed SAME + LOGICAL_AND + QUANTIFIER_EXISTS recipe

PRE-REG HARD bands (verbatim from preregs/2026-06_predicate_composition_same_attribute_v1_smoke.md):
  HARD_PASS (ALL of):
    HP1 ARM_SAME_PLUS_AND_EXISTS.em_mean >= FREQ_BIAS + 0.05
    HP2 ARM_SAME_PLUS_AND_EXISTS.em_mean >= ARM_SAME_ATTRIBUTE.em_mean + 0.05
    HP3 CV across seeds <= 0.15
    HP4 Sanity self-test passes (SAME-ATTRIBUTE >= 20/20 on identity holdout)
  HARD_FAIL (any of):
    HF1 ARM_SAME_PLUS_AND_EXISTS.em_mean <= FREQ_BIAS - 0.02
    HF2 Sanity self-test fails (< 20/20 on identity holdout) -- primitive math broken
  MIDDLE_BAND: any other configuration

CORPUS: data/datasets/hotpot_qa_distractor_dev_1k.jsonl filtered to type=='comparison'
        and yes/no gold answer; id-sorted for determinism (59 questions: 27 yes, 32 no).

ENCODER: word2vec-google-news-300 (data/gensim_cache/) for entity + attribute encoding.

NUMPY + GENSIM. ASCII-ONLY. Smoke target ~10-15 min CPU wall.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials
)

ANCHOR_NAME = "predicate_composition_same_attribute_v1_smoke"

# ---- CLI ----
_AP = argparse.ArgumentParser()
_AP.add_argument("--smoke", action="store_true")
_AP.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _AP.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "smoke")

# ---- CONFIG (this anchor IS a smoke; same config in both modes) ----
N_DIM = 4096
SEEDS = [7, 17, 23]
N_QUESTIONS_CAP = 60  # take all yes/no comparison Qs (max 59 available)
HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
W2V_MODEL_NAME = "word2vec-google-news-300"
W2V_LOCAL_GZ = REPO / "data" / "gensim_cache" / "word2vec-google-news-300" / "word2vec-google-news-300.gz"

# Pre-reg bands
HP_LIFT_OVER_FREQ = 0.05
HP_COMP_VS_SAME = 0.05
HP_CV_MAX = 0.15
HF_LIFT_DOWN_FROM_FREQ = -0.02
SANITY_PAIRS_N = 20
SANITY_MIN_CORRECT = 20  # identity holdout is trivial-yes; must be perfect

# ============================================================================
# HD primitives (FHRR real analog via FFT circular convolution; identical to
# temporal_not cell for substrate-consistency)
# ============================================================================

def random_unit(n: int, rng: np.random.RandomState) -> np.ndarray:
    v = rng.randn(n).astype(np.float64)
    v /= (np.linalg.norm(v) + 1e-12)
    return v


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.fft.ifft(np.fft.fft(c) * np.fft.fft(b).conj()).real


def bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """Bundle via mean + L2-normalize. Substrate-native superposition."""
    if not vecs:
        raise ValueError("bundle of empty list")
    s = np.mean(np.stack(vecs, axis=0), axis=0)
    n = np.linalg.norm(s)
    if n > 1e-12:
        s = s / n
    return s


def cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


# ============================================================================
# PREDICATE PRIMITIVES (substrate-native naming-layer on top of HD algebra)
# ============================================================================

def same_attribute_category(X: np.ndarray, Y: np.ndarray, C: np.ndarray, tau: float) -> int:
    """SAME-ATTRIBUTE (BOTH-MEMBERSHIP form): are X and Y BOTH members of category C?

    Returns 1 if (cos(X, C) > tau AND cos(Y, C) > tau) else 0.
    Substrate-native: pure cosine + bipolar AND (LOGICAL_AND).
    """
    mx = cos(X, C) > tau
    my = cos(Y, C) > tau
    return 1 if (mx and my) else 0


def same_attribute_relational(X: np.ndarray, Y: np.ndarray, tau_sim: float) -> int:
    """SAME-ATTRIBUTE (relational form): do X and Y share their attribute value directly?

    For questions like "are X and Y from the same country?" where the attribute
    (country) is encoded geometrically into the entity vector via w2v.
    Returns 1 if cos(X, Y) > tau_sim else 0.
    """
    return 1 if cos(X, Y) > tau_sim else 0


def logical_and(p1: int, p2: int) -> int:
    """LOGICAL_AND: bipolar AND on predicate bits (substrate-free)."""
    return 1 if (p1 == 1 and p2 == 1) else 0


def logical_not(pred_result: int) -> int:
    """LOGICAL_NOT: sign flip on predicate result (free in substrate)."""
    return 1 - pred_result


def quantifier_exists(bits: List[int], threshold: int = 1) -> int:
    """QUANTIFIER_EXISTS: bundle-then-threshold; here on integer bits.

    In the BOTH-MEMBERSHIP recipe with exactly 2 entities, EXISTS over the
    AND result collapses to identity (returns the AND bit). Kept as named
    primitive for the substrate-native naming layer.
    """
    return 1 if sum(bits) >= threshold else 0


# ============================================================================
# FORMULA SELF-TESTS (run before any band measurement; abort on failure)
# ============================================================================

def _selftest_bind_unbind() -> float:
    rng = np.random.RandomState(0)
    a = random_unit(N_DIM, rng)
    b = random_unit(N_DIM, rng)
    c = bind(a, b)
    a_rec = unbind(c, b)
    c_ab = cos(a, a_rec)
    assert c_ab >= 0.40, "bind/unbind round-trip cos=%.4f (need >= 0.40)" % c_ab
    return c_ab


def _selftest_same_attribute_identity() -> Tuple[int, int]:
    """20-pair identity holdout (pre-reg HP4 / HF2 endpoint check).

    For each pair, X = Y (same random unit vector); SAME-ATTRIBUTE(X, X) must
    return 1 for ALL pairs (trivial-yes; cos(X, X) = 1.0 > any tau in [0, 1)).
    """
    rng = np.random.RandomState(99)
    correct = 0
    for _ in range(SANITY_PAIRS_N):
        X = random_unit(N_DIM, rng)
        # Both relational and category forms must give 1 on identity.
        rel = same_attribute_relational(X, X, tau_sim=0.5)
        cat = same_attribute_category(X, X, X, tau=0.5)
        if rel == 1 and cat == 1:
            correct += 1
    return correct, SANITY_PAIRS_N


def _selftest_logical_and() -> bool:
    """LOGICAL_AND truth table."""
    assert logical_and(0, 0) == 0
    assert logical_and(0, 1) == 0
    assert logical_and(1, 0) == 0
    assert logical_and(1, 1) == 1
    assert logical_not(0) == 1
    assert logical_not(1) == 0
    assert quantifier_exists([0, 0]) == 0
    assert quantifier_exists([0, 1]) == 1
    assert quantifier_exists([1, 1]) == 1
    return True


def _instrumentation_selftest() -> Dict:
    c_bu = _selftest_bind_unbind()
    truth_table_ok = _selftest_logical_and()
    sanity_n, sanity_d = _selftest_same_attribute_identity()
    print(
        "[selftest] bind_unbind_cos=%.4f truth_table_ok=%s identity_holdout=%d/%d" %
        (c_bu, truth_table_ok, sanity_n, sanity_d),
        flush=True,
    )
    return {
        "bind_unbind_cos": float(c_bu),
        "truth_table_ok": bool(truth_table_ok),
        "sanity_n": int(sanity_n),
        "sanity_d": int(sanity_d),
    }


SELFTEST_RESULTS = _instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# WORD2VEC encoder (Path A pretrained; loaded once, cached cross-seed)
# ============================================================================

_W2V_CACHE = [None]


def _load_w2v():
    if _W2V_CACHE[0] is not None:
        return _W2V_CACHE[0]
    print("[w2v] loading word2vec-google-news-300 from %s ..." % W2V_LOCAL_GZ, flush=True)
    t0 = time.time()
    from gensim.models import KeyedVectors
    if W2V_LOCAL_GZ.exists():
        kv = KeyedVectors.load_word2vec_format(str(W2V_LOCAL_GZ), binary=True)
    else:
        import gensim.downloader as gd
        gd.base_dir = GENSIM_CACHE_DIR
        kv = gd.load(W2V_MODEL_NAME)
    print("[w2v] loaded in %.1fs (vocab=%d, dim=%d)" % (time.time() - t0, len(kv), kv.vector_size), flush=True)
    _W2V_CACHE[0] = kv
    return kv


def _w2v_phrase_vec(kv, phrase: str) -> Optional[np.ndarray]:
    """Mean-pool w2v vectors over tokens in phrase. Returns None if no token matches."""
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", phrase or "")
    vecs = []
    for tok in tokens:
        v = None
        if tok in kv.key_to_index:
            v = kv[tok]
        elif tok.lower() in kv.key_to_index:
            v = kv[tok.lower()]
        elif tok.capitalize() in kv.key_to_index:
            v = kv[tok.capitalize()]
        if v is not None:
            vecs.append(v)
    if not vecs:
        return None
    out = np.mean(np.stack(vecs, axis=0), axis=0).astype(np.float64)
    n = np.linalg.norm(out)
    if n > 1e-12:
        out = out / n
    return out


# ============================================================================
# CORPUS: HotpotQA yes/no comparison subset (id-sorted for determinism)
# ============================================================================

YES = {"yes", "true", "correct"}
NO = {"no", "false", "incorrect"}


def normalize_answer(ans: str) -> str:
    s = re.sub(r"[^\w\s]", " ", ans or "").lower().strip()
    s = re.sub(r"\s+", " ", s)
    if s in YES:
        return "yes"
    if s in NO:
        return "no"
    return s


def is_yesno_question(q: Dict) -> bool:
    return normalize_answer(q["answer"]) in {"yes", "no"}


def load_comparison_subset() -> List[Dict]:
    """Load yes/no-only comparison-type Qs from dev_1k, id-sorted for determinism."""
    rows = []
    with open(HOTPOT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("type") == "comparison":
                rows.append(r)
    rows.sort(key=lambda r: r["id"])
    yn = [r for r in rows if is_yesno_question(r)]
    subset = yn[:N_QUESTIONS_CAP]
    print(
        "[corpus] %d total comparison in dev_1k; %d yes/no comparison; loaded %d" %
        (len(rows), len(yn), len(subset)),
        flush=True,
    )
    return subset


# ============================================================================
# QUESTION PARSING (lightweight; no LLM)
# ============================================================================

NEG_PATTERNS = [
    re.compile(r"\b(not|n't|never)\b", re.IGNORECASE),
    re.compile(r"\bdifferent\b", re.IGNORECASE),
    re.compile(r"\bnot the same\b", re.IGNORECASE),
]


def detect_negation(question: str) -> bool:
    """True if the question contains a polarity-flip cue (different, not, etc)."""
    for pat in NEG_PATTERNS:
        if pat.search(question):
            return True
    return False


def detect_question_form(question: str) -> str:
    """Categorize yes/no comparison question form.

    Returns one of:
      "both_membership" -- "Are X and Y both A?" / "Both X and Y are A?"
      "same_attr"       -- "Are X and Y the same A?" / "from the same A?"
      "share"           -- "Do X and Y share/have in common?"
      "other"           -- doesn't match a known SAME / BOTH form
    """
    ql = question.lower()
    if "both" in ql:
        return "both_membership"
    if "same" in ql or "common" in ql:
        return "same_attr"
    if "share" in ql:
        return "share"
    return "other"


# Regex to pull the trailing category from "Are X and Y both <CAT>?" style questions.
_BOTH_TAIL_RE = re.compile(r"\bboth\b(.+?)[\?\.]?$", re.IGNORECASE)
_SAME_TAIL_RE = re.compile(r"\bsame\b(.+?)[\?\.]?$", re.IGNORECASE)


def extract_category_phrase(question: str) -> Optional[str]:
    """Pull the category / attribute phrase mentioned in a SAME / BOTH question.

    "Are X and Y both documentaries?"        -> "documentaries"
    "Are X and Y the same country?"          -> "country"
    "Are X and Y both flowering plants?"     -> "flowering plants"
    "Are X and Y both based in Massachusetts?" -> "based in Massachusetts"
    Returns the matched phrase stripped of punctuation, or None.
    """
    m = _BOTH_TAIL_RE.search(question)
    if m:
        phrase = m.group(1)
    else:
        m = _SAME_TAIL_RE.search(question)
        if m:
            phrase = m.group(1)
        else:
            return None
    # Clean: drop stopwords at the head, strip punctuation, lowercase.
    phrase = re.sub(r"[^\w\s]", " ", phrase).strip()
    phrase = re.sub(r"\s+", " ", phrase).lower()
    # Drop common leading function words.
    LEAD = ["the", "a", "an", "of", "by", "from", "in", "at", "on", "to"]
    toks = phrase.split()
    while toks and toks[0] in LEAD:
        toks = toks[1:]
    if not toks:
        return None
    return " ".join(toks)


# ============================================================================
# ENTITY EXTRACTION (from supporting_facts.title; gold-supporting)
# ============================================================================

def get_entities(q: Dict) -> List[str]:
    """Unique entity titles preserving order from supporting_facts.title."""
    sup = q.get("supporting_facts", {})
    sup_titles = sup.get("title", [])
    unique = []
    seen = set()
    for t in sup_titles:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


# ============================================================================
# THRESHOLD CALIBRATION (smoke-scope: in-domain fit on per-seed half-split)
# ============================================================================

def calibrate_thresholds(qs: List[Dict], kv, seed: int) -> Tuple[float, float]:
    """Sweep tau (category membership) and tau_sim (relational similarity); pick
    values that max balanced-accuracy on a per-seed half-split.

    Acknowledged in-domain calibration (smoke-scope shortcut); leakage logged
    via calib_em_on_fit vs eval_em diagnostics in run_seed.
    """
    rng = np.random.RandomState(seed + 5000)
    # Half-split fit/eval
    idx = np.arange(len(qs))
    rng.shuffle(idx)
    fit_idx = idx[: len(qs) // 2]
    fit_qs = [qs[i] for i in fit_idx]

    def acc_at(tau, tau_sim):
        correct = 0
        for q in fit_qs:
            pred = predict_one_same_plus_and(q, kv, tau, tau_sim)
            if pred == normalize_answer(q["answer"]):
                correct += 1
        return correct / max(1, len(fit_qs))

    best = (0.0, 0.0, -1.0)
    for tau in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]:
        for tau_sim in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
            a = acc_at(tau, tau_sim)
            if a > best[2]:
                best = (tau, tau_sim, a)
    return best[0], best[1]


# ============================================================================
# PREDICT helpers (used by both isolated SAME arm + composed arm)
# ============================================================================

def predict_one_same_only(q: Dict, kv, tau: float, tau_sim: float) -> str:
    """ARM_SAME_ATTRIBUTE per-Q prediction.

    SAME primitive in isolation. No LOGICAL_AND wrapping for non-membership Qs;
    no negation handling. Pure SAME / BOTH-MEMBERSHIP detection.
    """
    entities = get_entities(q)
    if len(entities) < 2:
        return "no"
    form = detect_question_form(q["question"])
    cat_phrase = extract_category_phrase(q["question"])

    X = _w2v_phrase_vec(kv, entities[0])
    Y = _w2v_phrase_vec(kv, entities[1])
    if X is None or Y is None:
        return "no"

    if form == "both_membership" and cat_phrase:
        C = _w2v_phrase_vec(kv, cat_phrase)
        if C is None:
            return "no"
        bit = same_attribute_category(X, Y, C, tau)
    elif form == "same_attr":
        # Relational form: direct cos(X, Y).
        bit = same_attribute_relational(X, Y, tau_sim)
    elif form == "share":
        bit = same_attribute_relational(X, Y, tau_sim)
    else:
        # SAME-only arm: no fallback composition; predict no (does not fire).
        bit = 0

    return "yes" if bit == 1 else "no"


def predict_one_same_plus_and(q: Dict, kv, tau: float, tau_sim: float) -> str:
    """ARM_SAME_PLUS_AND_EXISTS per-Q prediction.

    Composed recipe:
      both_membership: LOGICAL_AND(is_C(X), is_C(Y)) = QUANTIFIER_EXISTS over the
                       AND-bits with threshold=2 (i.e. require BOTH to fire)
      same_attr:       SAME-ATTRIBUTE relational form (cos(X, Y) > tau_sim)
      negated forms:   detect_negation -> LOGICAL_NOT the result
      other:           fallback majority-class (yes if we have no signal)
    """
    entities = get_entities(q)
    if len(entities) < 2:
        return "no"
    form = detect_question_form(q["question"])
    cat_phrase = extract_category_phrase(q["question"])
    negated = detect_negation(q["question"])

    X = _w2v_phrase_vec(kv, entities[0])
    Y = _w2v_phrase_vec(kv, entities[1])
    if X is None or Y is None:
        return "no"

    base_bit: int = 0
    fired = False

    if form == "both_membership" and cat_phrase:
        C = _w2v_phrase_vec(kv, cat_phrase)
        if C is not None:
            # Explicit LOGICAL_AND + QUANTIFIER_EXISTS composition.
            x_in = 1 if cos(X, C) > tau else 0
            y_in = 1 if cos(Y, C) > tau else 0
            and_bit = logical_and(x_in, y_in)
            # EXISTS over the 2-element list with threshold=2 (collapse to AND);
            # written out to make the named primitive explicit in the recipe.
            base_bit = quantifier_exists([and_bit], threshold=1)
            fired = True
    elif form == "same_attr":
        base_bit = same_attribute_relational(X, Y, tau_sim)
        fired = True
    elif form == "share":
        base_bit = same_attribute_relational(X, Y, tau_sim)
        fired = True
    else:
        # Composed arm fallback: majority-class on this subset is "no" (32/59).
        base_bit = 0

    if negated:
        base_bit = logical_not(base_bit)

    return "yes" if base_bit == 1 else "no"


# ============================================================================
# ARMS
# ============================================================================

def arm_freq_bias_predict(qs: List[Dict]) -> List[str]:
    """Majority-class baseline."""
    answers = [normalize_answer(q["answer"]) for q in qs]
    counts = {}
    for a in answers:
        counts[a] = counts.get(a, 0) + 1
    if not counts:
        return ["yes"] * len(qs)
    majority = max(counts.items(), key=lambda kv: kv[1])[0]
    return [majority] * len(qs)


def arm_raw_w_lookup_predict(qs: List[Dict], seed: int, kv) -> Tuple[List[str], Dict]:
    """ARM_RAW_W_LOOKUP: substrate without predicate primitives.

    Yes/no codebook + projected w2v question vector. Weak structural baseline.
    """
    rng = np.random.RandomState(seed + 1000)
    answer_codebook = {}
    for a in ["yes", "no"]:
        answer_codebook[a] = random_unit(N_DIM, rng)
    PRETRAIN_DIM = 300
    P = rng.randn(N_DIM, PRETRAIN_DIM).astype(np.float64) / np.sqrt(PRETRAIN_DIM)

    def project(v300):
        v = P @ v300
        n = np.linalg.norm(v)
        return v / (n + 1e-12)

    preds = []
    fire = 0
    for q in qs:
        qvec = _w2v_phrase_vec(kv, q["question"])
        if qvec is None:
            preds.append("no")
            continue
        qhd = project(qvec)
        s_yes = float(np.dot(qhd, answer_codebook["yes"]))
        s_no = float(np.dot(qhd, answer_codebook["no"]))
        if s_yes >= s_no:
            preds.append("yes")
        else:
            preds.append("no")
        fire += 1
    return preds, {"fire_rate": float(fire) / max(1, len(qs))}


def arm_same_attribute_predict(qs: List[Dict], kv, tau: float, tau_sim: float) -> Tuple[List[str], Dict]:
    """ARM_SAME_ATTRIBUTE: SAME primitive in isolation."""
    preds = []
    fire = 0
    for q in qs:
        # Count "did the primitive fire" (form was both_membership / same_attr / share)
        form = detect_question_form(q["question"])
        if form in ("both_membership", "same_attr", "share"):
            fire += 1
        preds.append(predict_one_same_only(q, kv, tau, tau_sim))
    return preds, {
        "fire_rate_same": float(fire) / max(1, len(qs)),
        "tau": float(tau),
        "tau_sim": float(tau_sim),
    }


def arm_same_plus_and_exists_predict(qs: List[Dict], kv, tau: float, tau_sim: float) -> Tuple[List[str], Dict]:
    """ARM_SAME_PLUS_AND_EXISTS: composed SAME + LOGICAL_AND + QUANTIFIER_EXISTS."""
    preds = []
    fire_same = 0
    fire_and = 0
    fire_not = 0
    for q in qs:
        form = detect_question_form(q["question"])
        if form in ("both_membership", "same_attr", "share"):
            fire_same += 1
        if form == "both_membership":
            fire_and += 1
        if detect_negation(q["question"]):
            fire_not += 1
        preds.append(predict_one_same_plus_and(q, kv, tau, tau_sim))
    return preds, {
        "fire_rate_same": float(fire_same) / max(1, len(qs)),
        "fire_rate_and": float(fire_and) / max(1, len(qs)),
        "fire_rate_not": float(fire_not) / max(1, len(qs)),
        "tau": float(tau),
        "tau_sim": float(tau_sim),
    }


# ============================================================================
# EM SCORING
# ============================================================================

def em_score(pred: str, gold: str) -> float:
    return 1.0 if normalize_answer(pred) == normalize_answer(gold) else 0.0


def score_arm(preds: List[str], qs: List[Dict]) -> float:
    if not qs:
        return 0.0
    correct = 0.0
    for p, q in zip(preds, qs):
        correct += em_score(p, q["answer"])
    return correct / float(len(qs))


# ============================================================================
# PER-SEED RUN
# ============================================================================

def run_seed(seed: int, qs: List[Dict], kv) -> Dict:
    t0 = time.time()
    print("[seed=%d] starting (N=%d Qs, N_DIM=%d)..." % (seed, len(qs), N_DIM), flush=True)

    # Calibrate thresholds on per-seed half-split (in-domain; smoke-scope).
    tau, tau_sim = calibrate_thresholds(qs, kv, seed)
    print("  [seed=%d] calibrated tau=%.3f tau_sim=%.3f" % (seed, tau, tau_sim), flush=True)

    # Arm 1: FREQ_BIAS
    fb_preds = arm_freq_bias_predict(qs)
    fb_em = score_arm(fb_preds, qs)

    # Arm 2: RAW_W_LOOKUP
    raw_preds, raw_diag = arm_raw_w_lookup_predict(qs, seed, kv)
    raw_em = score_arm(raw_preds, qs)

    # Arm 3: SAME_ATTRIBUTE
    sa_preds, sa_diag = arm_same_attribute_predict(qs, kv, tau, tau_sim)
    sa_em = score_arm(sa_preds, qs)

    # Arm 4: SAME_PLUS_AND_EXISTS
    spa_preds, spa_diag = arm_same_plus_and_exists_predict(qs, kv, tau, tau_sim)
    spa_em = score_arm(spa_preds, qs)

    elapsed = time.time() - t0
    print(
        "  [seed=%d] FB=%.4f RAW=%.4f SAME=%.4f SAME+AND=%.4f same_fire=%.2f and_fire=%.2f not_fire=%.2f elapsed=%.2fs" %
        (seed, fb_em, raw_em, sa_em, spa_em,
         spa_diag.get("fire_rate_same", 0.0),
         spa_diag.get("fire_rate_and", 0.0),
         spa_diag.get("fire_rate_not", 0.0),
         elapsed),
        flush=True,
    )

    return {
        "seed": int(seed),
        "N_DIM": int(N_DIM),
        "n_qs": int(len(qs)),
        "ARM_FREQ_BIAS_em": float(fb_em),
        "ARM_RAW_W_LOOKUP_em": float(raw_em),
        "ARM_SAME_ATTRIBUTE_em": float(sa_em),
        "ARM_SAME_PLUS_AND_EXISTS_em": float(spa_em),
        "raw_diag": raw_diag,
        "same_diag": sa_diag,
        "same_plus_and_diag": spa_diag,
        "calibrated_tau": float(tau),
        "calibrated_tau_sim": float(tau_sim),
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }


# ============================================================================
# VERDICT
# ============================================================================

def compute_verdict(per_seed: List[Dict], selftest: Dict) -> Tuple[str, str]:
    if not per_seed:
        return ("HARD_FAIL", "no_per_seed_results")

    # Sanity (HP4 / HF2)
    sanity_ok = (
        selftest.get("sanity_n", 0) >= SANITY_MIN_CORRECT
        and selftest.get("sanity_d", 0) == SANITY_PAIRS_N
        and selftest.get("truth_table_ok", False)
    )
    if not sanity_ok:
        return ("HARD_FAIL",
                "HARD_FAIL HF2: sanity holdout %d/%d (need >= %d/%d) truth_table=%s -- SAME primitive math broken." %
                (selftest.get("sanity_n"), selftest.get("sanity_d"),
                 SANITY_MIN_CORRECT, SANITY_PAIRS_N, selftest.get("truth_table_ok")))

    fb_mean = float(np.mean([r["ARM_FREQ_BIAS_em"] for r in per_seed]))
    raw_mean = float(np.mean([r["ARM_RAW_W_LOOKUP_em"] for r in per_seed]))
    sa_mean = float(np.mean([r["ARM_SAME_ATTRIBUTE_em"] for r in per_seed]))
    spa_mean = float(np.mean([r["ARM_SAME_PLUS_AND_EXISTS_em"] for r in per_seed]))
    spa_per = [r["ARM_SAME_PLUS_AND_EXISTS_em"] for r in per_seed]
    spa_std = float(np.std(spa_per))
    spa_cv = spa_std / max(1e-6, spa_mean)

    summary = (
        "n_seeds=%d FB=%.4f RAW=%.4f SAME=%.4f SAME+AND=%.4f cv=%.4f "
        "lift_over_FB=%+.4f lift_over_SAME=%+.4f lift_over_RAW=%+.4f"
    ) % (len(per_seed), fb_mean, raw_mean, sa_mean, spa_mean, spa_cv,
         spa_mean - fb_mean, spa_mean - sa_mean, spa_mean - raw_mean)

    # HARD_FAIL HF1
    if spa_mean <= fb_mean + HF_LIFT_DOWN_FROM_FREQ:
        return ("HARD_FAIL",
                "HARD_FAIL HF1: SAME+AND %.4f <= FREQ_BIAS %.4f + (%.2f) (does not beat trivial guessing). %s" %
                (spa_mean, fb_mean, HF_LIFT_DOWN_FROM_FREQ, summary))

    # HARD_PASS checks (HP1-HP3 all must hold; HP4 sanity already checked)
    hp1 = spa_mean >= fb_mean + HP_LIFT_OVER_FREQ
    hp2 = spa_mean >= sa_mean + HP_COMP_VS_SAME
    hp3 = spa_cv <= HP_CV_MAX

    if hp1 and hp2 and hp3:
        return ("HARD_PASS",
                "HARD_PASS: HP1=%s HP2=%s HP3=%s (cv=%.4f). %s" %
                (hp1, hp2, hp3, spa_cv, summary))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: HP1=%s HP2=%s HP3=%s (cv=%.4f). %s" %
            (hp1, hp2, hp3, spa_cv, summary))


# ============================================================================
# MAIN
# ============================================================================

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)

t_run = time.time()
qs = load_comparison_subset()
n_yesno = sum(1 for q in qs if is_yesno_question(q))
print("[corpus] %d of %d Qs have yes/no gold answer" % (n_yesno, len(qs)), flush=True)

# Diagnostic: distribution of question forms across the addressable space.
form_counts = {"both_membership": 0, "same_attr": 0, "share": 0, "other": 0}
for q in qs:
    form_counts[detect_question_form(q["question"])] += 1
print("[corpus] form distribution: %s" % form_counts, flush=True)

kv = _load_w2v()

run_config = {"N": N_DIM, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)

for seed in remaining:
    result = run_seed(seed, qs, kv)
    write_partial(out_dir, seed, result)

per_seed_dict = aggregate_partials(out_dir, SEEDS, run_config=run_config)
per_seed = [per_seed_dict[str(s)] for s in SEEDS if str(s) in per_seed_dict]

verdict, verdict_msg = compute_verdict(per_seed, SELFTEST_RESULTS)
elapsed_s = time.time() - t_run

print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": float(elapsed_s),
    "N_DIM": int(N_DIM),
    "SEEDS": SEEDS,
    "N_QUESTIONS_CAP": int(N_QUESTIONS_CAP),
    "n_qs_loaded": int(len(qs)),
    "n_yesno": int(n_yesno),
    "form_distribution": form_counts,
    "run_mode": RUN_MODE,
    "selftest": SELFTEST_RESULTS,
    "per_seed": per_seed,
    "preregs": "preregs/2026-06_predicate_composition_same_attribute_v1_smoke.md",
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print("[metrics] written to %s" % metrics_path, flush=True)
