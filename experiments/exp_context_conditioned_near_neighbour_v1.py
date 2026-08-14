"""exp_context_conditioned_near_neighbour_v1 -- does CONTEXT-CONDITIONING buy near-neighbour
discrimination that CONTEXT-FREE comparison provably cannot?

PRE-REG: preregs/2026-08-13_context_conditioned_near_neighbour.md, COMMITTED (42792834c) BEFORE
this file existed and BEFORE any arm was scored. Every band, arm, split and gate is frozen there.

WHY THIS CELL EXISTS
Four cells have tested CONTEXT-FREE word-pair similarity and all four failed:
    MEASURED@data/exp_differentia_feature_supply_v1/metrics.json:rho_primary
        A_DIFFERENTIA 0.0247 | B_GENUS_ONLY 0.0179 | C_GROUNDED_RAW 0.2759 | E_SCRAMBLE -0.0235
    MEASURED@data/exp_near_vs_far_diagnostic_v1/metrics.json:table.SPLIT1_TAXONOMIC
        C on FAR 0.3042 (CI excludes 0) vs C on NEAR 0.1245 (CI INCLUDES 0)
CITED@notes/brain_drill_encoder_lexical_semantics_2026-08-13.md element E4: the brain's semantic
control system applies GAIN conditioned on the CURRENT CONTEXT (Chiou & Lambon Ralph 2018 Cortex,
DCM, F(2,34)=3.86 p=.03); it never computes context-free word-word similarity. Our
`concept_similarity(a,b)` is a bare 2-arg function with NO CONTEXT PORT -- a POSITION gap.
MEASURED@data/exp_context_vector_signal_v1/metrics.json: our per-encounter context vector carries
real signal (D = +0.2155, CI [+0.1982,+0.2332]) and ALL of it lives in argmax IDENTITY, none in
the cosine magnitude. We compute genuine context and discard it at the comparison step.

SimLex-999 is deliberately NOT the primary: it is a CONTEXT-FREE benchmark and using it would
repeat the framing error this cell exists to correct (pre-reg sec 1).

NOTHING UNDER hdlab/ IS MODIFIED. The context encoder, the anchor accumulator, the read-out and the
context-free comparator are all hdlab's own code, imported and called.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; per-arm choice-vector sha256)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes SEPARATE output dirs
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_floor_computed: paired-binomial se(delta)=sqrt(p_disc/n); mde_95 at n=200 is 0.098 < the
#   +0.10 HARD_PASS delta -> discriminator_reachability True (pre-reg 4.1)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < arm2 < 0.95)
# - discriminator survives scale: multi-scale smoke (150 / 600 items) + FULL at MAX_ITEMS
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L; STRICT_MARGIN)
# - HP_SCOPE: the four HARD_PASS gates apply to ARM 1 ONLY; arms 2/3/4 inherit no gate
# - cardinality_ok: EXPECTED_N_UNITS = 4 scored arms x n_items
# - per-unit failure-class instrumentation (META_RULE_J); no bare except
# - calibration_check: default_ok_for_this_regime (thresh=-1.0 removes the only threshold)
# - positive controls: CTX_MASKED_MULTI byte-identical to hdlab; SELF_RETRIEVAL_SANITY >= 0.70
# - deterministic seeding: hashlib + fixed ints only; no builtin hash(), no list(set())
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import (numpy sizes its pools at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import inspect
import itertools
import json
import pickle
import platform
import re
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nltk.corpus import wordnet as wn                                        # noqa: E402

# ---- THE ORGANS BEING REUSED (pre-reg 3.1). Imported, never modified. ------------------------
from hdlab.reading_grounding_loop import (                                   # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, canonicalize_fast, content_lemmas,
    context_vector_masked, normalize_lemma,
)
from hdlab.grounding_acquisition_loop import content_words, context_vector   # noqa: E402
from hdlab.lexical_similarity import concept_similarity                      # noqa: E402
from hdlab.grounded_similarity import in_grounded_lexicon                    # noqa: E402

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

# ---------------------------------------------------------------------------------------------
# CONFIG -- pre-registered. Nothing here is adjusted after seeing a result.
# ---------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_context_conditioned_near_neighbour_v1"
PREREG_PATH = "preregs/2026-08-13_context_conditioned_near_neighbour.md"
PREREG_COMMIT = "42792834c"

CORPUS_PATH = os.path.join(REPO_ROOT, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
CACHE_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_cache")

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")

MASTER_SEED = 20260813
BOOTSTRAP_SEED = 20260813
N_BOOTSTRAP = 5000

MIN_WORD_COUNT = 300        # corpus frequency floor for the candidate vocabulary
MIN_WORD_LEN = 4
MAX_GROUP = 40              # WordNet groups larger than this are skipped (pre-reg 2.1.3)
K_SENT = 100                # sentences collected per candidate word
N_PROFILE = 70              # of those, the first N_PROFILE build the ANCHOR (held-out from eval)
SENT_MIN_TOK, SENT_MAX_TOK = 8, 40
MIN_CONTEXT_WORDS = 4       # leak control L3
MAX_ITEMS_PER_WORD = 4
MAX_ITEMS = 4000            # FULL cap
MIN_ITEMS = 200             # HARD power gate (pre-reg 4.1); FULL only

SMOKE_ITEM_SCALES = (150, 600)      # multi-scale smoke; n_items is the statistic's load axis
STRICT_MARGIN_FRAC = 0.05           # META_RULE_L

ARMS = ("A1_CONTEXT_CONDITIONED", "A2_CONTEXT_FREE", "A3_CONTEXT_SCRAMBLED", "A4_FREQUENCY")
CHANCE = 0.50

HP_D12, HP_D13, HP_D14 = 0.10, 0.08, 0.05
MISSING_PIECE_D12 = 0.05
SELF_RETRIEVAL_FLOOR = 0.70

_TOK = re.compile(r"[a-z']+")


# ---------------------------------------------------------------------------------------------
# Durability plumbing
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
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
    os.replace(tmp, final)                                  # META_RULE_AH
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


def _seed_for(key: str) -> int:
    """Deterministic seed from a string. hashlib, NEVER builtin hash() (PROT-023 / gate F.5)."""
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 32)


# ---------------------------------------------------------------------------------------------
# THE ONE NEW FUNCTION -- context_vector_masked generalised to a SET of lemmas.
# Needed because the query must be SYMMETRIC in the two candidates: masking only the true target
# would leak the answer. Self-test S4 asserts byte-identity with hdlab's own single-lemma version.
# ---------------------------------------------------------------------------------------------
def _ctx_masked_multi(sentence: str, lemmas: Sequence[str], d: int = CTX_D, *,
                      graded: Optional[bool] = None) -> np.ndarray:
    """Exactly hdlab.reading_grounding_loop.context_vector_masked, with `!= target_lemma`
    generalised to `not in lemmas`. Same content_words filter, same context_vector bundling math,
    both called from hdlab -- nothing is re-implemented here.

    REPAIR 2026-08-14: `context_vector_masked` gained a `graded` kwarg defaulting to the module
    switch `GRADED_COMPARATOR` (ON) on the same day, and this function did not follow it. That
    silently FORKED the two, and self-test S4 -- whose entire job is to assert byte-identity --
    caught it and made this module unimportable at HEAD. Following the switch here restores S4.
    This changes what a FRESH run of this cell measures (the query is now graded, matching the
    live read-out); the LANDED metrics.json under data/exp_context_conditioned_near_neighbour_v1/
    is the pre-flip signed run and has NOT been overwritten."""
    if graded is None:
        graded = GRADED_COMPARATOR
    drop = set(lemmas)
    words = [w for w in content_words(sentence) if normalize_lemma(w) not in drop]
    return context_vector(" ".join(words), d=d, graded=graded)


def _is_variant(tok: str, word: str) -> bool:
    """Deliberately OVER-inclusive morphological-variant test (pre-reg 2.3). A leak control
    should over-remove."""
    if tok == word:
        return True
    if normalize_lemma(tok) == normalize_lemma(word):
        return True
    if tok.startswith(word) and 0 < len(tok) - len(word) <= 3:
        return True
    if word.startswith(tok) and 0 < len(word) - len(tok) <= 3 and len(tok) >= 4:
        return True
    return False


# ---------------------------------------------------------------------------------------------
# Corpus (two streaming passes; cached so smoke + full do not re-scan 251 MB three times)
# ---------------------------------------------------------------------------------------------
def _cache_key() -> str:
    cfg = json.dumps({"corpus": os.path.basename(CORPUS_PATH), "min_count": MIN_WORD_COUNT,
                      "min_len": MIN_WORD_LEN, "max_group": MAX_GROUP, "k_sent": K_SENT,
                      "tok_lo": SENT_MIN_TOK, "tok_hi": SENT_MAX_TOK,
                      "wn": wn.get_version()}, sort_keys=True)
    return hashlib.sha256(cfg.encode("utf-8")).hexdigest()[:16]


def build_corpus_assets() -> dict:
    """Pass 1 = token counts; WordNet STRICT near-neighbour pairs; Pass 2 = sentence buckets.
    Deterministic and config-keyed; the cache is a pure speed device, disclosed in metrics."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, "corpus_assets_%s.pkl" % _cache_key())
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            a = pickle.load(f)
        print("[corpus] cache hit %s (words=%d pairs=%d)"
              % (os.path.basename(cache_path), len(a["buckets"]), len(a["pairs_strict"])),
              flush=True)
        return a

    if not os.path.exists(CORPUS_PATH):
        raise FileNotFoundError("corpus missing: %s" % CORPUS_PATH)

    t0 = time.time()
    counts: Counter = Counter()
    n_lines = 0
    with open(CORPUS_PATH, encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            counts.update(_TOK.findall(line.lower()))
    print("[corpus] pass1 %.1fs lines=%d vocab=%d" % (time.time() - t0, n_lines, len(counts)),
          flush=True)

    vocab = sorted(w for w, n in counts.items()
                   if n >= MIN_WORD_COUNT and w.isalpha() and len(w) >= MIN_WORD_LEN
                   and wn.morphy(w, "n") == w and wn.synsets(w, "n"))

    # STRICT (pre-reg 2.1.3): groups built from the DOMINANT noun sense of BOTH words.
    grp_strict: Dict[str, set] = defaultdict(set)
    grp_loose: Dict[str, set] = defaultdict(set)
    for w in vocab:
        ss = wn.synsets(w, "n")
        s0 = ss[0]
        grp_strict[s0.name()].add(w)
        for h in s0.hypernyms():
            grp_strict[h.name()].add(w)
        for s in ss:                                        # LOOSE = the predecessor's literal S1
            grp_loose[s.name()].add(w)
            for h in s.hypernyms():
                grp_loose[h.name()].add(w)

    def _pairs_from(groups: Dict[str, set]) -> List[Tuple[str, str]]:
        out = set()
        for _g, ws in groups.items():
            ws_sorted = sorted(ws)                          # sorted(), never list(set()) (F.5)
            if not (2 <= len(ws_sorted) <= MAX_GROUP):
                continue
            for a, b in itertools.combinations(ws_sorted, 2):
                if normalize_lemma(a) == normalize_lemma(b):
                    continue
                if _is_variant(a, b) or _is_variant(b, a):
                    continue
                out.add((a, b))
        return sorted(out)

    pairs_strict = _pairs_from(grp_strict)
    pairs_loose = _pairs_from(grp_loose)
    words = sorted({w for p in pairs_strict for w in p} | {w for p in pairs_loose for w in p})
    wset = set(words)
    print("[corpus] vocab=%d strict_pairs=%d loose_pairs=%d words=%d"
          % (len(vocab), len(pairs_strict), len(pairs_loose), len(words)), flush=True)

    buckets: Dict[str, List[str]] = defaultdict(list)
    t1 = time.time()
    with open(CORPUS_PATH, encoding="utf-8") as f:
        for line in f:
            toks = _TOK.findall(line.lower())
            if not (SENT_MIN_TOK <= len(toks) <= SENT_MAX_TOK):
                continue
            hit = wset.intersection(toks)
            if not hit:
                continue
            s = line.strip()
            for w in hit:
                if len(buckets[w]) < K_SENT and toks.count(w) == 1:
                    buckets[w].append(s)
    print("[corpus] pass2 %.1fs" % (time.time() - t1), flush=True)

    assets = {"counts": {w: c for w, c in counts.items() if c >= 50},
              "n_lines": n_lines, "vocab_size": len(vocab),
              "pairs_strict": pairs_strict, "pairs_loose": pairs_loose,
              "buckets": {w: buckets[w] for w in words},
              "wordnet_version": wn.get_version(),
              "wordnet_asset": "nltk corpora/wordnet.zip (data/wordnet_cache/ is EMPTY on disk)"}
    tmp = cache_path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(assets, f, protocol=4)
    os.replace(tmp, cache_path)
    return assets


def split_pools(buckets: Dict[str, List[str]]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Per-word deterministic shuffle (hashlib-seeded), then PROFILE / EVAL split. Disjoint by
    construction: no sentence that builds an anchor is ever scored."""
    prof, ev = {}, {}
    for w in sorted(buckets):
        s = list(buckets[w])
        np.random.default_rng(_seed_for("split|" + w)).shuffle(s)
        prof[w] = s[:N_PROFILE]
        ev[w] = s[N_PROFILE:]
    return prof, ev


# ---------------------------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------------------------
def build_items(pairs: Sequence[Tuple[str, str]], eval_pool: Dict[str, List[str]],
                max_items: int) -> Tuple[List[dict], dict]:
    rm = Counter()
    used_sentences: set = set()
    per_word = Counter()
    items: List[dict] = []
    n_considered = 0
    for a, b in pairs:
        for target, distractor in ((a, b), (b, a)):
            if per_word[target] >= MAX_ITEMS_PER_WORD:
                rm["removed_word_cap"] += 1
                continue
            chosen = None
            for sent in eval_pool.get(target, ()):
                n_considered += 1
                key = (target, sent)
                if key in used_sentences:
                    rm["removed_sentence_reuse"] += 1
                    continue
                toks = _TOK.findall(sent.lower())
                # L1: target or a morphological variant anywhere OTHER than the single slot
                occ = [i for i, t in enumerate(toks) if t == target]
                if len(occ) != 1:
                    rm["removed_L1_target_multi_occurrence"] += 1
                    continue
                others = [t for i, t in enumerate(toks) if i != occ[0]]
                if any(_is_variant(t, target) for t in others):
                    rm["removed_L1_target_variant"] += 1
                    continue
                # L2: distractor or a morphological variant anywhere
                if any(_is_variant(t, distractor) for t in toks):
                    rm["removed_L2_distractor_present"] += 1
                    continue
                # L3: enough context left after masking BOTH candidates
                ctx = [w for w in content_lemmas(sent)
                       if w not in (normalize_lemma(target), normalize_lemma(distractor))]
                if len(ctx) < MIN_CONTEXT_WORDS:
                    rm["removed_L3_too_few_context_words"] += 1
                    continue
                chosen = sent
                used_sentences.add(key)
                break
            if chosen is None:
                rm["removed_no_eligible_sentence"] += 1
                continue
            per_word[target] += 1
            items.append({"item_id": "%s|%s|%d" % (target, distractor, per_word[target]),
                          "target": target, "distractor": distractor, "sentence": chosen})
    items.sort(key=lambda it: it["item_id"])
    n_before_cap = len(items)
    if max_items is not None and len(items) > max_items:
        items = items[:max_items]
    diag = {"n_eval_sentences_considered": n_considered,
            "n_items_before_cap": n_before_cap, "n_items": len(items),
            "removals": dict(sorted(rm.items())),
            "distinct_target_words": len(sorted({it["target"] for it in items})),
            "max_items_per_word": MAX_ITEMS_PER_WORD}
    return items, diag


def assign_donors(items: List[dict]) -> List[int]:
    """Deterministic derangement over sorted item ids for ARM 3: donor[i] != i and the donor's
    candidates are disjoint from item i's (pre-reg 3.3)."""
    n = len(items)
    off = n // 2 + 1
    donors = []
    for i in range(n):
        j = (i + off) % n
        tries = 0
        while tries < n and (j == i
                             or items[j]["target"] in (items[i]["target"], items[i]["distractor"])
                             or items[j]["distractor"] in (items[i]["target"],
                                                           items[i]["distractor"])):
            j = (j + 1) % n
            tries += 1
        donors.append(j)
    return donors


# ---------------------------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------------------------
def build_space(words: Sequence[str], profile_pool: Dict[str, List[str]]) -> ConceptSpace:
    """The substrate's OWN anchor construction: accumulate context_vector_masked over each word's
    HELD-OUT profile sentences into hdlab's ConceptSpace. No new mechanism."""
    sp = ConceptSpace(d=CTX_D)
    for w in sorted(words):
        for sent in profile_pool.get(w, ()):
            sp.observe(w, context_vector_masked(sent, w))
    return sp


def _mask_for(space: ConceptSpace, anchors: List[str], pos: Dict[str, int],
              a: str, b: str) -> np.ndarray:
    m = np.zeros(len(anchors), dtype=bool)
    m[pos[a]] = True
    m[pos[b]] = True
    return m


def arm_context(items: List[dict], space: ConceptSpace, queries: List[np.ndarray],
                out_dir: str, tag: str, t0: float) -> Tuple[np.ndarray, dict]:
    """ARM 1 / ARM 3 -- identical mechanism, different query. Read-out is hdlab's own
    canonicalize_fast restricted to the two candidates via its PRE-EXISTING eligible_mask, with
    thresh=-1.0 so it is a pure argmax (the channel measured to carry all lemma-specific signal)."""
    anchors, _mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    correct = np.zeros(len(items), dtype=bool)
    n_tie, n_zero_query = 0, 0
    cosines = []
    for i, it in enumerate(items):
        q = queries[i]
        if float(np.linalg.norm(q)) < 1e-9:
            n_zero_query += 1
        mask = _mask_for(space, anchors, pos, it["target"], it["distractor"])
        pick, cos = canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=mask)
        # tie diagnostic: recompute both cosines explicitly (cheap, 2 rows).
        # REPAIR 2026-08-14: must follow the same graded switch canonicalize_fast follows, or this
        # diagnostic counts ties in a DIFFERENT space from the one that made the decision. Affects
        # the reported n_ties only; `correct[i]` comes from canonicalize_fast either way.
        nb = np.asarray(q, dtype=np.float64) if GRADED_COMPARATOR else np.sign(q)
        nn = float(np.linalg.norm(nb))
        if nn >= 1e-9:
            ct, cd = [], []
            for w, acc in ((it["target"], ct), (it["distractor"], cd)):
                ab = space.bundle(w)
                na = float(np.linalg.norm(ab))
                acc.append(0.0 if na < 1e-9 else float(np.dot(ab, nb) / (na * nn)))
            if abs(ct[0] - cd[0]) < 1e-12:
                n_tie += 1
        correct[i] = (pick == it["target"])
        cosines.append(round(float(cos), 6))
        if (i + 1) % 500 == 0:
            _heartbeat(out_dir, i + 1, len(items), time.time() - t0, {"arm": tag})
    return correct, {"n_ties": n_tie, "n_zero_query": n_zero_query,
                     "mean_winning_cos": round(float(np.mean(cosines)), 6) if cosines else None}


_CS_CACHE: Dict[Tuple[str, str], Optional[float]] = {}


def _csim(a: str, b: str) -> Optional[float]:
    k = (a, b) if a <= b else (b, a)
    if k not in _CS_CACHE:
        _CS_CACHE[k] = concept_similarity(k[0], k[1], use_grounded_fallback=True)
    return _CS_CACHE[k]


def arm_context_free(items: List[dict], rng: np.random.Generator) -> Tuple[np.ndarray, dict]:
    """ARM 2 -- the SAME sentence and the SAME candidates, but every comparison is CONTEXT-BLIND:
    the current live `concept_similarity` path, pooled over the sentence's content lemmas. This is
    the one-variable isolation (pre-reg 3.2)."""
    correct = np.zeros(len(items), dtype=bool)
    n_undef, n_tie, cov = 0, 0, []
    for i, it in enumerate(items):
        tl, dl = normalize_lemma(it["target"]), normalize_lemma(it["distractor"])
        ctx = [w for w in content_lemmas(it["sentence"]) if w not in (tl, dl)]
        sc = {}
        for cand in (it["target"], it["distractor"]):
            vals = [v for v in (_csim(cand, w) for w in ctx) if v is not None]
            sc[cand] = (float(np.mean(vals)) if vals else None, len(vals))
        cov.append(max(sc[it["target"]][1], sc[it["distractor"]][1]))
        st, sd = sc[it["target"]][0], sc[it["distractor"]][0]
        if st is None or sd is None:
            n_undef += 1
            correct[i] = bool(rng.integers(2) == 0)
        elif abs(st - sd) < 1e-12:
            n_tie += 1
            correct[i] = bool(rng.integers(2) == 0)
        else:
            correct[i] = st > sd
    return correct, {"n_undefined_fell_back_to_coin": n_undef, "n_ties_fell_back_to_coin": n_tie,
                     "mean_defined_context_words": round(float(np.mean(cov)), 3) if cov else None,
                     "frac_items_with_any_defined_similarity":
                         round(float(np.mean([c > 0 for c in cov])), 4) if cov else None}


def arm_frequency(items: List[dict], counts: Dict[str, int],
                  rng: np.random.Generator) -> Tuple[np.ndarray, dict]:
    correct = np.zeros(len(items), dtype=bool)
    n_tie = 0
    for i, it in enumerate(items):
        ct, cd = counts.get(it["target"], 0), counts.get(it["distractor"], 0)
        if ct == cd:
            n_tie += 1
            correct[i] = bool(rng.integers(2) == 0)
        else:
            correct[i] = ct > cd
    return correct, {"n_ties_fell_back_to_coin": n_tie}


# ---------------------------------------------------------------------------------------------
# Paired bootstrap on the DELTAS (all arms score the SAME items)
# ---------------------------------------------------------------------------------------------
def paired_bootstrap(correct: Dict[str, np.ndarray], n_boot: int, seed: int,
                     clusters: Optional[np.ndarray] = None) -> dict:
    keys = list(ARMS)
    mat = np.stack([correct[k].astype(np.float64) for k in keys], axis=0)   # (n_arms, n)
    n = mat.shape[1]
    rng = np.random.default_rng(seed)
    acc_boot = np.empty((n_boot, len(keys)), dtype=np.float64)
    if clusters is None:
        chunk = 500
        done = 0
        while done < n_boot:
            m = min(chunk, n_boot - done)
            idx = rng.integers(0, n, size=(m, n))
            acc_boot[done:done + m] = mat[:, idx].mean(axis=2).T
            done += m
    else:
        uniq = sorted(set(int(c) for c in clusters))
        members = [np.flatnonzero(clusters == c) for c in uniq]
        for r in range(n_boot):
            pick = rng.integers(0, len(members), size=len(members))
            idx = np.concatenate([members[p] for p in pick])
            acc_boot[r] = mat[:, idx].mean(axis=1)
    out = {"n_boot": n_boot, "seed": seed,
           "clustered": clusters is not None, "arm_acc_ci": {}, "deltas": {}}
    for j, k in enumerate(keys):
        lo, hi = np.percentile(acc_boot[:, j], [2.5, 97.5])
        out["arm_acc_ci"][k] = {"acc": round(float(mat[j].mean()), 6),
                                "ci_lo": round(float(lo), 6), "ci_hi": round(float(hi), 6),
                                "sd": round(float(acc_boot[:, j].std()), 6)}
    a1 = keys.index("A1_CONTEXT_CONDITIONED")
    defs = [("d_A1_minus_A2", a1, keys.index("A2_CONTEXT_FREE")),
            ("d_A1_minus_A3", a1, keys.index("A3_CONTEXT_SCRAMBLED")),
            ("d_A1_minus_A4", a1, keys.index("A4_FREQUENCY"))]
    for name, i, j in defs:
        d = acc_boot[:, i] - acc_boot[:, j]
        point = float(mat[i].mean() - mat[j].mean())
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["deltas"][name] = {"delta": round(point, 6), "ci_lo": round(float(lo), 6),
                               "ci_hi": round(float(hi), 6), "sd": round(float(d.std()), 6),
                               "mde_95": round(float(1.96 * d.std()), 6),
                               "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
                               "frac_boot_above_zero": round(float((d > 0).mean()), 6)}
    dc = acc_boot[:, a1] - CHANCE
    lo, hi = np.percentile(dc, [2.5, 97.5])
    out["deltas"]["d_A1_minus_CHANCE"] = {
        "delta": round(float(mat[a1].mean() - CHANCE), 6), "ci_lo": round(float(lo), 6),
        "ci_hi": round(float(hi), 6), "sd": round(float(dc.std()), 6),
        "mde_95": round(float(1.96 * dc.std()), 6),
        "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
        "frac_boot_above_zero": round(float((dc > 0).mean()), 6)}
    return out


def decide_verdict(bs: dict) -> Tuple[str, List[str]]:
    d12 = bs["deltas"]["d_A1_minus_A2"]
    d13 = bs["deltas"]["d_A1_minus_A3"]
    d14 = bs["deltas"]["d_A1_minus_A4"]
    dch = bs["deltas"]["d_A1_minus_CHANCE"]
    notes = []
    # HARD_FAIL is evaluated FIRST and dominates (pre-reg 4).
    if not d12["ci_excludes_zero"]:
        return "HARD_FAIL_CONTEXT_ADDS_NOTHING", [
            "d(A1-A2)=%.4f CI=[%.4f,%.4f] INCLUDES 0" % (d12["delta"], d12["ci_lo"], d12["ci_hi"])]
    if d13["delta"] <= 0.0:
        return "HARD_FAIL_ANY_CONTEXT_WORKS_ARTIFACT", [
            "A1 <= A3: d(A1-A3)=%.4f -- the gain is not from THIS context" % d13["delta"]]
    m12 = HP_D12 * (1.0 + STRICT_MARGIN_FRAC)
    m13 = HP_D13 * (1.0 + STRICT_MARGIN_FRAC)
    m14 = HP_D14 * (1.0 + STRICT_MARGIN_FRAC)
    hp = (d12["delta"] >= HP_D12 and d13["delta"] >= HP_D13 and d14["delta"] >= HP_D14
          and d12["ci_excludes_zero"] and d13["ci_excludes_zero"] and d14["ci_excludes_zero"]
          and dch["ci_excludes_zero"] and dch["delta"] > 0)
    if hp:
        floor_hug = (d12["delta"] < m12 or d13["delta"] < m13 or d14["delta"] < m14)
        if floor_hug:
            notes.append("META_RULE_L: a HARD_PASS gate is cleared by < 5%% of its floor "
                         "(d12=%.4f/%.4f d13=%.4f/%.4f d14=%.4f/%.4f) -> MIDDLE_BAND"
                         % (d12["delta"], m12, d13["delta"], m13, d14["delta"], m14))
            return "MIDDLE_BAND_FLOOR_HUGGING", notes
        return "HARD_PASS", ["all four HARD_PASS gates cleared strictly above floor"]
    if d12["delta"] >= MISSING_PIECE_D12 and d12["ci_excludes_zero"] and d13["delta"] > 0.0:
        return "CONTEXT_IS_THE_MISSING_PIECE", [
            "d(A1-A2)=%.4f CI=[%.4f,%.4f] excludes 0 and A1 > A3 (d=%.4f), but the full "
            "HARD_PASS conjunction is not met" % (d12["delta"], d12["ci_lo"], d12["ci_hi"],
                                                  d13["delta"])]
    return "MIDDLE_BAND", [
        "d12=%.4f CI=[%.4f,%.4f]; d13=%.4f; d14=%.4f; d_chance=%.4f -- neither the HARD_PASS "
        "conjunction nor the weaker band is met, and no HARD_FAIL trigger fired"
        % (d12["delta"], d12["ci_lo"], d12["ci_hi"], d13["delta"], d14["delta"], dch["delta"])]


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY -- module scope, before any measurement; must not touch the 251 MB corpus)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    t0 = time.time()
    res: dict = {}
    exercised = set()

    # S1 -- SIGNATURE BINDING against the LIVE hdlab objects (gate F.2/F.3; base/portable kwargs).
    for name, obj, kwargs in (
            ("context_vector_masked", context_vector_masked,
             {"sentence": "x", "target_lemma": "x"}),
            ("canonicalize_fast", canonicalize_fast,
             {"new_lemma": "x", "new_raw_sum": None, "space": None, "thresh": 0.0,
              "eligible_mask": None}),
            ("ConceptSpace.observe", ConceptSpace.observe, {"lemma": "x", "ctx_vec": None}),
            ("concept_similarity", concept_similarity,
             {"word_a": "x", "word_b": "y", "use_grounded_fallback": True})):
        sig = inspect.signature(obj)
        try:
            sig.bind_partial(**({"self": None, **kwargs} if name.startswith("ConceptSpace.")
                                else kwargs))
        except TypeError as e:
            raise AssertionError("substrate_signature drift on %s: %s" % (name, e))
    res["substrate_signature_checked"] = ["context_vector_masked", "canonicalize_fast",
                                          "ConceptSpace.observe", "concept_similarity"]

    # S2 -- WordNet live, and the STRICT near-neighbour criterion FIRES and DISCRIMINATES.
    res["wordnet_version"] = wn.get_version()
    def _strict_near(a: str, b: str) -> bool:
        sa, sb = wn.synsets(a, "n"), wn.synsets(b, "n")
        if not sa or not sb:
            return False
        ga = {sa[0].name()} | {h.name() for h in sa[0].hypernyms()}
        gb = {sb[0].name()} | {h.name() for h in sb[0].hypernyms()}
        return bool(ga & gb)
    assert _strict_near("novelist", "poet"), "STRICT criterion does not fire on novelist/poet"
    assert _strict_near("cathedral", "basilica"), "STRICT criterion does not fire on cathedral/basilica"
    assert not _strict_near("cathedral", "democracy"), "STRICT criterion fires on cathedral/democracy"
    res["selftest_strict_criterion"] = {"novelist_poet": True, "cathedral_basilica": True,
                                        "cathedral_democracy": False}

    # S3 -- leak controls REMOVE what they must and KEEP what they must.
    assert _is_variant("poets", "poet") and _is_variant("poet", "poets")
    assert _is_variant("novelists", "novelist")
    assert not _is_variant("river", "poet"), "variant test over-fires on unrelated words"
    res["leak_control_selftest"] = {"poets~poet": True, "river~poet": False}

    # S4 -- POSITIVE CONTROL: _ctx_masked_multi is BYTE-IDENTICAL to hdlab's own single-lemma
    #       context_vector_masked. This is what makes arm 1 a REUSE, not a fork.
    for sent in ("The poet wrote a long book about rivers and mountains in winter.",
                 "A cathedral stands beside the river near the old market square."):
        for lem in ("poet", "cathedral", "river"):
            mine = _ctx_masked_multi(sent, [lem])
            theirs = context_vector_masked(sent, lem)
            assert np.array_equal(mine, theirs), (
                "_ctx_masked_multi has FORKED context_vector_masked on (%r,%r)" % (sent, lem))
    exercised.add("context_vector_masked")
    res["ctx_masked_multi_matches_hdlab"] = True
    # and masking TWO lemmas must actually remove both
    s = "The poet met the novelist beside the river."
    v2 = _ctx_masked_multi(s, ["poet", "novelist"])
    assert np.array_equal(v2, context_vector(" ".join(
        [w for w in content_words(s)
         if normalize_lemma(w) not in {"poet", "novelist"}]),
        graded=GRADED_COMPARATOR)), "multi-mask math drifted"

    # S5 -- REAL CODE PATH (gate F.1): build the ACTUAL ConceptSpace + read-out at tiny scale and
    #       assert the read-out MOVES with the query (a read-out that cannot move is not a read-out).
    sp = ConceptSpace(d=CTX_D)
    prof = {"poet": ["The poet wrote verses and published a book of poems every winter.",
                     "A famous poet read verses aloud at the library and the school."],
            "novelist": ["The novelist wrote a long story about a family and a war.",
                         "A novelist published a story and later wrote another long book."],
            "river": ["The river flows through the valley and past the bridge each spring.",
                      "Boats travel along the river between the town and the sea."]}
    for w, sents in prof.items():
        for sent in sents:
            sp.observe(w, context_vector_masked(sent, w))
    exercised.update({"ConceptSpace", "ConceptSpace.observe"})
    anchors, mat = sp.anchor_matrix()
    assert anchors == ["novelist", "poet", "river"], "anchor order drifted: %r" % anchors
    assert mat.shape == (3, CTX_D), "anchor matrix shape %r" % (mat.shape,)
    assert np.linalg.norm(mat, axis=1).min() > 0, "an anchor is a zero vector"
    pos = {a: i for i, a in enumerate(anchors)}
    m = np.zeros(3, dtype=bool)
    m[pos["poet"]] = True
    m[pos["river"]] = True
    q_poet = _ctx_masked_multi("She read verses from a book of poems at the library.",
                               ["poet", "river"])
    q_river = _ctx_masked_multi("Boats travel through the valley past the bridge to the sea.",
                                ["poet", "river"])
    p1, c1 = canonicalize_fast("__slot__", q_poet, sp, thresh=-1.0, eligible_mask=m)
    p2, c2 = canonicalize_fast("__slot__", q_river, sp, thresh=-1.0, eligible_mask=m)
    exercised.add("canonicalize_fast")
    assert p1 in ("poet", "river") and p2 in ("poet", "river"), "read-out returned %r/%r" % (p1, p2)
    assert p1 != p2, ("READ-OUT CANNOT MOVE: two maximally different queries picked the same "
                      "anchor (%r) -- the mechanism is analytically pinned" % p1)
    assert np.isfinite(c1) and np.isfinite(c2), "read-out cosine is not finite"
    assert abs(c1) > 1e-9, "read-out cosine is a sentinel zero"
    res["readout_moves"] = {"query_poetlike_picked": p1, "query_riverlike_picked": p2,
                            "cos_poetlike": round(float(c1), 4), "cos_riverlike": round(float(c2), 4)}

    # S6 -- ARM 2 comparator is LIVE and non-sentinel (and its fallback path is reachable).
    v = concept_similarity("poet", "river", use_grounded_fallback=True)
    exercised.update({"concept_similarity", "grounded_similarity"})
    assert v is None or np.isfinite(v), "concept_similarity returned %r" % v
    n_cov = sum(1 for w in ("poet", "river", "book", "valley", "bridge", "story")
                if in_grounded_lexicon(w))
    assert n_cov >= 1, "grounded lexicon covers NONE of a plain-English probe set"
    res["arm2_comparator"] = {"concept_similarity_poet_river": None if v is None else round(v, 4),
                              "grounded_lexicon_probe_coverage": n_cov}

    # S7 -- the bootstrap MOVES and separates a real delta from a null one.
    rng = np.random.default_rng(3)
    n = 300
    base = rng.random(n) < 0.50
    better = base | (rng.random(n) < 0.30)
    fake = {"A1_CONTEXT_CONDITIONED": better, "A2_CONTEXT_FREE": base,
            "A3_CONTEXT_SCRAMBLED": base.copy(), "A4_FREQUENCY": base.copy()}
    bs = paired_bootstrap(fake, 400, 7)
    assert bs["deltas"]["d_A1_minus_A2"]["ci_excludes_zero"], "bootstrap missed a real delta"
    # CALIBRATION, not a single draw: two independent fair coins CAN differ by chance, so a single
    # null replicate excluding zero is expected ~5% of the time and would be a flaky assertion.
    # Assert the FALSE-POSITIVE RATE instead: at most 1 of 6 independent null replicates may
    # exclude zero. (This exact check caught a bad single-draw version of itself first time out.)
    n_null_fp, n_null_rep, nn = 0, 6, 800
    for s in range(n_null_rep):
        r2 = np.random.default_rng(1000 + s)
        null = {k: (r2.random(nn) < 0.50) for k in ARMS}
        if paired_bootstrap(null, 400, 7)["deltas"]["d_A1_minus_A2"]["ci_excludes_zero"]:
            n_null_fp += 1
    assert n_null_fp <= 1, (
        "bootstrap false-positive rate too high: %d/%d null replicates excluded zero"
        % (n_null_fp, n_null_rep))
    res["bootstrap_selftest"] = {
        "real_delta": bs["deltas"]["d_A1_minus_A2"]["delta"],
        "real_ci_excludes_zero": True,
        "null_false_positives": n_null_fp, "null_replicates": n_null_rep, "null_n_items": nn}

    # S8 -- every verdict branch is REACHABLE (no unreachable band).
    def _bs(d12, d13, d14, dch, ex12=True, ex13=True, ex14=True, exch=True):
        def c(d, ex):
            return {"delta": d, "ci_lo": d - 0.02 if ex else -abs(d) - 0.02,
                    "ci_hi": d + 0.02, "ci_excludes_zero": ex}
        return {"deltas": {"d_A1_minus_A2": c(d12, ex12), "d_A1_minus_A3": c(d13, ex13),
                           "d_A1_minus_A4": c(d14, ex14), "d_A1_minus_CHANCE": c(dch, exch)}}
    seen = sorted({
        decide_verdict(_bs(0.20, 0.15, 0.12, 0.20))[0],
        decide_verdict(_bs(0.105, 0.081, 0.051, 0.20))[0],
        decide_verdict(_bs(0.07, 0.03, 0.02, 0.10))[0],
        decide_verdict(_bs(0.01, 0.01, 0.01, 0.01, ex12=False))[0],
        decide_verdict(_bs(0.20, -0.05, 0.12, 0.20))[0],
        decide_verdict(_bs(0.04, 0.02, 0.01, 0.05))[0]})
    want = sorted(["HARD_PASS", "MIDDLE_BAND_FLOOR_HUGGING", "CONTEXT_IS_THE_MISSING_PIECE",
                   "HARD_FAIL_CONTEXT_ADDS_NOTHING", "HARD_FAIL_ANY_CONTEXT_WORKS_ARTIFACT",
                   "MIDDLE_BAND"])
    assert seen == want, "verdict branches not all reachable: got %r want %r" % (seen, want)
    res["verdict_branches_reachable"] = seen

    # S9 -- gate F.1 declaration check: every declared entrypoint was actually exercised HERE.
    declared = {"context_vector_masked", "ConceptSpace", "ConceptSpace.observe",
                "canonicalize_fast", "concept_similarity", "grounded_similarity"}
    missing = sorted(declared - exercised)
    assert not missing, "real_code_path: declared but NOT exercised in self-test: %r" % missing
    res["real_code_path_exercised"] = sorted(exercised)

    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, max_items: int) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode, len(ARMS) * max_items)
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000

    assets = build_corpus_assets()
    counts = assets["counts"]
    profile_pool, eval_pool = split_pools(assets["buckets"])

    items, item_diag = build_items(assets["pairs_strict"], eval_pool, max_items)
    n = len(items)
    print("[items] n=%d %s" % (n, json.dumps(item_diag["removals"])), flush=True)

    if run_mode == "full" and n < MIN_ITEMS:
        metrics = {"verdict": "INSUFFICIENT_ITEMS_NO_READ",
                   "verdict_msg": "only %d clean items could be built (pre-registered floor %d); "
                                  "STOPPED rather than running underpowered" % (n, MIN_ITEMS),
                   "summary": "context-conditioned near-neighbour -- item gate stopped the run",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
                   "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "n_items": n, "min_items": MIN_ITEMS, "item_construction": item_diag,
                   "n_units": 0, "expected_n_units": len(ARMS) * MIN_ITEMS,
                   "cardinality_ok": False}
        _atomic_write_metrics(output_dir, metrics)
        print("[verdict] INSUFFICIENT_ITEMS_NO_READ", flush=True)
        return metrics
    if n < 2:
        raise AssertionError("VACUOUS RUN: %d items built" % n)

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    space = build_space(words_used, profile_pool)
    anchors, _ = space.anchor_matrix()
    print("[space] anchors=%d (each from <=%d HELD-OUT profile sentences)"
          % (len(anchors), N_PROFILE), flush=True)

    # ---- queries -------------------------------------------------------------------------------
    q_real = [_ctx_masked_multi(it["sentence"], [normalize_lemma(it["target"]),
                                                 normalize_lemma(it["distractor"]),
                                                 it["target"], it["distractor"]])
              for it in items]
    donors = assign_donors(items)
    q_scram = []
    for i, it in enumerate(items):
        d = items[donors[i]]
        q_scram.append(_ctx_masked_multi(
            d["sentence"], [normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                            it["target"], it["distractor"],
                            normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                            d["target"], d["distractor"]]))

    # ---- arms ----------------------------------------------------------------------------------
    correct: Dict[str, np.ndarray] = {}
    arm_diag: Dict[str, dict] = {}
    correct["A1_CONTEXT_CONDITIONED"], arm_diag["A1_CONTEXT_CONDITIONED"] = arm_context(
        items, space, q_real, output_dir, "A1", t0)
    correct["A3_CONTEXT_SCRAMBLED"], arm_diag["A3_CONTEXT_SCRAMBLED"] = arm_context(
        items, space, q_scram, output_dir, "A3", t0)
    correct["A2_CONTEXT_FREE"], arm_diag["A2_CONTEXT_FREE"] = arm_context_free(
        items, np.random.default_rng(MASTER_SEED + 2))
    correct["A4_FREQUENCY"], arm_diag["A4_FREQUENCY"] = arm_frequency(
        items, counts, np.random.default_rng(MASTER_SEED + 4))

    # ---- META_RULE_AF: arms must not be bit-identical ------------------------------------------
    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in correct.items()}
    seen_d: Dict[str, str] = {}
    for k in sorted(digests):
        if digests[k] in seen_d:
            raise AssertionError("META_RULE_AF VIOLATION: arms %r and %r bit-identical"
                                 % (seen_d[digests[k]], k))
        seen_d[digests[k]] = k

    # ---- POSITIVE CONTROL: SELF_RETRIEVAL_SANITY (pre-reg 6) -----------------------------------
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    pos_map = {a: i for i, a in enumerate(anchors)}
    n_sr = min(300, len(words_used))
    sr_words = [words_used[i] for i in
                np.sort(rng_sr.choice(len(words_used), size=n_sr, replace=False))]
    sr_hits = 0
    for w in sr_words:
        sents = profile_pool.get(w, [])
        if not sents:
            continue
        other = words_used[int(rng_sr.integers(len(words_used)))]
        while other == w:
            other = words_used[int(rng_sr.integers(len(words_used)))]
        q = _ctx_masked_multi(sents[0], [w, other, normalize_lemma(w), normalize_lemma(other)])
        m = np.zeros(len(anchors), dtype=bool)
        m[pos_map[w]] = True
        m[pos_map[other]] = True
        pick, _ = canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=m)
        sr_hits += int(pick == w)
    self_retrieval = round(sr_hits / max(1, len(sr_words)), 4)
    print("[positive-control] SELF_RETRIEVAL (held-IN profile sentence vs random other anchor) "
          "= %.4f (floor %.2f, n=%d)" % (self_retrieval, SELF_RETRIEVAL_FLOOR, len(sr_words)),
          flush=True)

    # ---- SECONDARY DIAGNOSTIC (added post-prereg; NO verdict weight) ---------------------------
    # arm 1's mechanism on HELD-OUT eval sentences against a RANDOM (non-sibling) distractor.
    # Parallels the predecessor's NEAR/FAR split: does the mechanism work at all when the
    # distractor is FAR, while failing when it is NEAR?
    rng_far = np.random.default_rng(MASTER_SEED + 11)
    far_hits, far_n = 0, 0
    sib = defaultdict(set)
    for a, b in assets["pairs_loose"]:
        sib[a].add(b)
        sib[b].add(a)
    for it in items:
        cand = words_used[int(rng_far.integers(len(words_used)))]
        tries = 0
        while tries < 20 and (cand == it["target"] or cand in sib[it["target"]]
                              or _is_variant(cand, it["target"])):
            cand = words_used[int(rng_far.integers(len(words_used)))]
            tries += 1
        if cand == it["target"] or cand in sib[it["target"]]:
            continue
        q = _ctx_masked_multi(it["sentence"], [it["target"], cand, normalize_lemma(it["target"]),
                                              normalize_lemma(cand)])
        m = np.zeros(len(anchors), dtype=bool)
        m[pos_map[it["target"]]] = True
        m[pos_map[cand]] = True
        pick, _ = canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=m)
        far_hits += int(pick == it["target"])
        far_n += 1
    far_acc = round(far_hits / max(1, far_n), 4)
    print("[secondary] A1 mechanism vs a RANDOM FAR distractor on the SAME held-out sentences "
          "= %.4f (n=%d)" % (far_acc, far_n), flush=True)

    # ---- META_RULE_AG: baseline in band --------------------------------------------------------
    a2 = float(correct["A2_CONTEXT_FREE"].mean())
    baseline_in_band = bool(0.05 < a2 < 0.95)

    # ---- bootstrap -----------------------------------------------------------------------------
    bs = paired_bootstrap(correct, n_boot, BOOTSTRAP_SEED)
    tw = sorted({it["target"] for it in items})
    twi = {w: i for i, w in enumerate(tw)}
    clusters = np.array([twi[it["target"]] for it in items], dtype=np.int64)
    bs_cluster = paired_bootstrap(correct, min(n_boot, 2000), BOOTSTRAP_SEED + 1, clusters)

    # ---- per-unit checkpoint (4 arms x n items) -------------------------------------------------
    done = completed_units(output_dir)
    for k in ARMS:
        key = unit_key(ANCHOR_NAME, run_mode, str(n), k)
        if key not in done:
            record_unit(output_dir, key, {"arm": k, "acc": float(correct[k].mean()),
                                          "n": n, "digest": digests[k]})
    units = load_units(output_dir)
    expected_units = len(ARMS)
    cardinality_ok = len(units) >= expected_units

    verdict, notes = decide_verdict(bs)
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    if self_retrieval < SELF_RETRIEVAL_FLOOR:
        verdict = "INSTRUMENTATION_SUSPECT_SELF_RETRIEVAL_BELOW_FLOOR"
        notes = ["SELF_RETRIEVAL=%.4f < floor %.2f: the anchor space cannot retrieve its own "
                 "held-in sentences, so no read on the hypothesis is licensed"
                 % (self_retrieval, SELF_RETRIEVAL_FLOOR)] + notes
    if not baseline_in_band:
        verdict = "MIDDLE_BAND_BASELINE_OUT_OF_BAND_META_RULE_AG"
        notes = ["A2 baseline = %.4f is outside (0.05, 0.95)" % a2] + notes

    accs = {k: round(float(correct[k].mean()), 6) for k in ARMS}
    msg = ("n=%d | A1=%.4f A2=%.4f A3=%.4f A4=%.4f CHANCE=0.50 | d12=%.4f CI=[%.4f,%.4f] "
           "d13=%.4f CI=[%.4f,%.4f] d14=%.4f CI=[%.4f,%.4f] | self_retrieval=%.4f | %s"
           % (n, accs["A1_CONTEXT_CONDITIONED"], accs["A2_CONTEXT_FREE"],
              accs["A3_CONTEXT_SCRAMBLED"], accs["A4_FREQUENCY"],
              bs["deltas"]["d_A1_minus_A2"]["delta"], bs["deltas"]["d_A1_minus_A2"]["ci_lo"],
              bs["deltas"]["d_A1_minus_A2"]["ci_hi"],
              bs["deltas"]["d_A1_minus_A3"]["delta"], bs["deltas"]["d_A1_minus_A3"]["ci_lo"],
              bs["deltas"]["d_A1_minus_A3"]["ci_hi"],
              bs["deltas"]["d_A1_minus_A4"]["delta"], bs["deltas"]["d_A1_minus_A4"]["ci_lo"],
              bs["deltas"]["d_A1_minus_A4"]["ci_hi"], self_retrieval, "; ".join(notes)))

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "near-neighbour disambiguation in context: does context-conditioning beat the "
                   "context-free comparator on WordNet dominant-sense siblings/synonyms?",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "prereg_commit": PREREG_COMMIT,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "hdlab_modified": False,
        "n_items": n, "min_items": MIN_ITEMS, "chance": CHANCE,
        "arm_accuracy": accs, "arm_labels": {
            "A1_CONTEXT_CONDITIONED": "query = THIS sentence's masked context; read-out = "
                                      "canonicalize_fast argmax over the 2 candidate anchors",
            "A2_CONTEXT_FREE": "SAME sentence, SAME candidates, but every comparison is "
                               "context-blind concept_similarity, pooled over content lemmas",
            "A3_CONTEXT_SCRAMBLED": "identical to A1 with a DIFFERENT item's real sentence as "
                                    "the query (deterministic derangement)",
            "A4_FREQUENCY": "pick the corpus-more-frequent candidate",
            "CHANCE": "0.50 by construction (2 candidates)"},
        "bootstrap_item": bs, "bootstrap_cluster_by_target_word": bs_cluster,
        "verdict_notes": notes,
        "bands": {"HARD_PASS": {"d12": HP_D12, "d13": HP_D13, "d14": HP_D14,
                                "and_A1_above_chance": True},
                  "CONTEXT_IS_THE_MISSING_PIECE": {"d12": MISSING_PIECE_D12, "and_A1_gt_A3": True},
                  "HARD_FAIL": {"d12_ci_includes_zero": True, "or_A1_le_A3": True},
                  "strict_margin_frac": STRICT_MARGIN_FRAC,
                  "declared_in": PREREG_PATH, "declared_at_commit": PREREG_COMMIT},
        "HP_SCOPE": {"A1_CONTEXT_CONDITIONED": ["d12", "d13", "d14", "above_chance"],
                     "A2_CONTEXT_FREE": [], "A3_CONTEXT_SCRAMBLED": [], "A4_FREQUENCY": []},
        "positive_control_self_retrieval": {
            "value": self_retrieval, "floor": SELF_RETRIEVAL_FLOOR, "n": len(sr_words),
            "definition": "a word's HELD-IN profile sentence scored against {own anchor, one "
                          "random other anchor}; if the space cannot retrieve itself the harness "
                          "is broken, not the hypothesis"},
        "secondary_far_distractor_diagnostic": {
            "prereg_status": "ADDED POST-PREREG, NO VERDICT WEIGHT -- disclosed",
            "acc": far_acc, "n": far_n,
            "definition": "A1's mechanism on the SAME held-out sentences against a RANDOM "
                          "non-sibling distractor; parallels the predecessor's NEAR/FAR split"},
        "arm_diagnostics": arm_diag,
        "arms_differ_verified": True, "arm_digests": digests,
        "baseline_in_band": baseline_in_band, "baseline_arm": "A2_CONTEXT_FREE",
        "item_construction": item_diag,
        "leak_controls": {
            "definition": {
                "L1": "target absent (and no morphological variant) anywhere but the masked slot",
                "L2": "distractor and every morphological variant absent from the sentence",
                "L3": ">= %d distinct content lemmas remain after masking both candidates"
                      % MIN_CONTEXT_WORDS,
                "variant_rule": "t==w, or normalize_lemma equal, or one is a <=3-character "
                                "extension of the other (deliberately over-inclusive)"},
            "removals": item_diag["removals"],
            "n_eval_sentences_considered": item_diag["n_eval_sentences_considered"]},
        "held_out": {"k_sentences_per_word": K_SENT, "n_profile": N_PROFILE,
                     "n_eval_pool": K_SENT - N_PROFILE,
                     "disjoint": "profile and eval pools are disjoint by construction; no "
                                 "sentence that builds an anchor is ever scored",
                     "split_seed": "hashlib.sha256('split|'+word) (never builtin hash())"},
        "corpus": {"path": "data/corpora/simplewiki/simplewiki_clean_v1.txt",
                   "n_lines": assets["n_lines"], "vocab_size": assets["vocab_size"],
                   "min_word_count": MIN_WORD_COUNT,
                   "n_pairs_strict": len(assets["pairs_strict"]),
                   "n_pairs_loose_predecessor_criterion": len(assets["pairs_loose"]),
                   "cache_note": "corpus assets are cached under %s keyed by a config hash; the "
                                 "cache is a pure speed device (both passes are deterministic)"
                                 % os.path.relpath(CACHE_DIR, REPO_ROOT)},
        "wordnet_version": assets["wordnet_version"], "wordnet_asset": assets["wordnet_asset"],
        "organs_reused": {
            "context_encoder": "hdlab.reading_grounding_loop.context_vector_masked",
            "anchor_accumulator": "hdlab.reading_grounding_loop.ConceptSpace(.observe)",
            "read_out": "hdlab.reading_grounding_loop.canonicalize_fast(eligible_mask=...)",
            "context_free_comparator": "hdlab.lexical_similarity.concept_similarity",
            "only_new_function": "_ctx_masked_multi (context_vector_masked generalised to a SET "
                                 "of lemmas; self-test S4 asserts byte-identity with hdlab's own "
                                 "single-lemma version)"},
        "n_anchors": len(anchors), "n_distinct_target_words": len(tw),
        "n_units": len(units), "expected_n_units": expected_units,
        "cardinality_ok": cardinality_ok,
        "crlb": {"crlb_formula_reference": "paired-binomial se(delta) = sqrt(p_disc/n)",
                 "crlb_floor_computed": round(float(1.96 * np.sqrt(0.5 / max(n, 1))), 6),
                 "discriminator_reachability": bool(1.96 * np.sqrt(0.5 / max(n, 1)) < HP_D12),
                 "note": "reported mde_95 per delta is 1.96 * bootstrap sd (see bootstrap_item)"},
        "compute_architecture": "sequential-CPU (pre-reg 5); thread pins set before numpy import",
        "storage_strategy": "sharded (one anchor vector per candidate word; nothing bundled "
                            "across concepts); no_composition (single-hop read-out)",
        "selftest": _SELFTEST_RESULT,
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (verdict, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--max-items", type=int, default=MAX_ITEMS)
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        for k in SMOKE_ITEM_SCALES:                 # multi-scale; n_items is the load-bearing axis
            out = OUT_SMOKE + "_n%d" % k
            print("=== SMOKE at max_items=%d -> %s ===" % (k, out), flush=True)
            m = run("smoke", out, k)
            if m["n_items"] < 10:
                raise AssertionError("VACUOUS SMOKE at %d: %d items" % (k, m["n_items"]))
            accs = m["arm_accuracy"]
            if len(sorted(set(round(v, 6) for v in accs.values()))) == 1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: all arms identical at %d: %r"
                                     % (k, accs))
            for a, v in accs.items():
                if v in (0.0, 1.0):
                    raise AssertionError("INSTRUMENTATION_SUSPECT: arm %s pinned at %r" % (a, v))
            if not m["baseline_in_band"]:
                raise AssertionError("META_RULE_AG: baseline out of band at %d: %r"
                                     % (k, accs["A2_CONTEXT_FREE"]))
            if m["positive_control_self_retrieval"]["value"] < SELF_RETRIEVAL_FLOOR:
                raise AssertionError("BLOCK_DISPATCH: SELF_RETRIEVAL %.4f < %.2f"
                                     % (m["positive_control_self_retrieval"]["value"],
                                        SELF_RETRIEVAL_FLOOR))
            if not m["arms_differ_verified"]:
                raise AssertionError("META_RULE_AF failed at %d" % k)
            if m["elapsed_s"] < 0.1:
                raise AssertionError("INSTRUMENTATION_SUSPECT: <100ms exit at %d" % k)
            print("[smoke] n%d OK: %s" % (k, json.dumps(accs)), flush=True)
        print("SMOKE=PASS (all scales)", flush=True)
        return
    run("full", OUT_FULL, args.max_items)


_SELFTEST_RESULT = _instrumentation_selftest()      # module scope, before any measurement

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
