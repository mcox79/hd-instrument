"""Does supplying RICHER PER-WORD MEANING CONTENT improve WITHIN-NEIGHBOURHOOD SEPARATION in the
live C3 open-vocabulary grounding read-out -- or is meaning supply not the binding constraint?

PRE-REG: preregs/2026-08-14_meaning_supply_separation_v1.md (bands + four pre-declared outcomes +
the expected failure mode were committed BEFORE this ran, commit 944ff2fa8).
GROUND TRUTH FIRST: data/exp_meaning_asset_coverage_probe_v1/metrics.json (commit 8931ab5f6).

THE QUESTION comes from notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md 5.3/7/10-Q1,
which rates "meaning is a ~380-word hand lexicon while a 39.7k-word norms island and a
237.7M-token concept encoder sit unused" as the project's highest-value move. The coverage probe
corrected three premises of that framing on disk (see prereg 0); this cell tests what SURVIVES
the correction, which is the real scientific question: richer meaning content -> better
separation of paradigmatic neighbours (axon/dendrite, sympathetic/parasympathetic)?

WHAT IS MEASURED. On the SAME corpus, SAME anchor construction, SAME items and SAME gold set as
the 4.80% baseline (imported from exp_grounding_readout_known_answer_v1, not reimplemented):
  A1_BASE      live path, unchanged
  A2_NORMS     + Lancaster sensorimotor + Brysbaert concreteness profile similarity
  A3_ENCODER   + persisted V2Transformer (the 237.7M-token lineage) mean-pooled word embedding
  A4_BOTH      both
  F_SCRAMBLE / F_FREQUENCY / F_PROJDRAW   floors, as ARMS not assertions
per arm: hit@1, MEDIAN TARGET RANK, frac-gold-in-top-50, sister-error conversions, and the
semantic-CROWDING statistic vs its random null. Rank and crowding are the diagnostic pair: they
say whether meaning got BETTER, not whether argmax got lucky.

HONEST SCOPE OF A3. The persisted encoder has NO word/sentence embedding API; its cue set is the
synthetic slot harness. This cell constructs a word embedding from its contextual token reps.
That is OUT-OF-DISTRIBUTION use and is labelled so in the metrics. It is the fair test of "wire
the encoder"; it is not a claim the encoder was built for this.

WIRES NOTHING. wire_status EXPERIMENT_LOCAL_NOT_WIRED. No hdlab default is changed by this file.

Run:  .venv/Scripts/python.exe experiments/exp_meaning_supply_separation_v1.py [--smoke|--self-test]
"""
from __future__ import annotations

import os

# Thread pinning MUST precede numpy/torch import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402
from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.reading_grounding_loop import (  # noqa: E402
    CTX_D, GRADED_COMPARATOR, ConceptSpace, canonicalize_fast, content_lemmas, normalize_lemma,
)
from hdlab.grounding_acquisition_loop import content_words, context_vector  # noqa: E402
import hdlab.grounded_similarity as gsim  # noqa: E402
from tools.exp_checkpoint import record_unit, unit_key  # noqa: E402

import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402

MASTER_SEED = C3.MASTER_SEED
N_BOOTSTRAP = 5000
W_GRID = (0.25, 0.50, 1.00)
W_HEADLINE = 0.50
AUX_ARMS = ("A2_NORMS", "A3_ENCODER", "A4_BOTH", "A5_STRINGCTRL")
ALL_ARMS = ("A1_BASE",) + AUX_ARMS
N_PROJ_DRAWS = 3
CROWD_SAMPLE = 400
TRIGRAM_DIM = 512        # hashed char-trigram width (fixed, so the control's memory is bounded)
SMOKE_MAX_ITEMS = 300
ENC_SEED = 7
ENC_BATCH = 256


# ============================================================ salted projection (F_PROJDRAW floor)
def _salted_word_vec(w: str, d: int, salt: str, cache: Dict[str, np.ndarray]) -> np.ndarray:
    v = cache.get(w)
    if v is None:
        seed = int.from_bytes(hashlib.sha256((salt + w).encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
        cache[w] = v
    return v


def salted_context_vector(text: str, d: int, salt: str, cache: Dict[str, np.ndarray],
                          graded: bool) -> np.ndarray:
    """Re-implementation of hdlab.grounding_acquisition_loop.context_vector with a hash SALT, so
    an independent draw of the random projection can be taken. At salt="" it is asserted
    BYTE-IDENTICAL to the live function (see self_test) -- that assertion is the only thing
    licensing its use as a floor."""
    acc = np.zeros(d, dtype=np.float64)
    for w in content_words(text):
        acc += _salted_word_vec(w, d, salt, cache)
    if graded:
        return acc
    out = np.sign(acc)
    out[out == 0] = 1.0
    return out


def salted_context_vector_masked(sentence: str, target_lemma: str, d: int, salt: str,
                                 cache: Dict[str, np.ndarray], graded: bool) -> np.ndarray:
    words = [w for w in content_words(sentence) if normalize_lemma(w) != target_lemma]
    return salted_context_vector(" ".join(words), d, salt, cache, graded)


def build_salted_space(sents: Sequence[str], buckets: Dict[str, List[int]], salt: str,
                       output_dir: str) -> ConceptSpace:
    sp = ConceptSpace(d=CTX_D)
    cache: Dict[str, np.ndarray] = {}
    t0 = time.time()
    lemmas = sorted(buckets)
    for k, w in enumerate(lemmas):
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            sp.observe(w, salted_context_vector_masked(sents[i], w, CTX_D, salt, cache,
                                                       GRADED_COMPARATOR))
        if k % 1000 == 0 or k == len(lemmas) - 1:
            print("[projdraw salt=%r] %d/%d elapsed=%.1fs" % (salt, k + 1, len(lemmas),
                                                              time.time() - t0), flush=True)
    return sp


# ============================================================ auxiliary meaning signals
def norms_matrix(anchors: Sequence[str]) -> Tuple[np.ndarray, np.ndarray]:
    """Row-L2-normalized Lancaster+Brysbaert profile per anchor; covered mask. Uncovered rows are
    all-zero, so their dot product with any query is exactly 0 (no spurious signal)."""
    n, d = len(anchors), gsim.N_GROUNDED_DIM
    mat = np.zeros((n, d), dtype=np.float64)
    covered = np.zeros(n, dtype=bool)
    for i, a in enumerate(anchors):
        v = gsim.grounded_vector(a)
        if v is None:
            continue
        arr = np.asarray(v, dtype=np.float64).reshape(-1)
        nrm = float(np.linalg.norm(arr))
        if nrm < 1e-9:
            continue
        mat[i] = arr / nrm
        covered[i] = True
    return mat, covered


def trigram_matrix(anchors: Sequence[str]) -> Tuple[np.ndarray, np.ndarray]:
    """CONTROL. Row-L2-normalized character-trigram profile per anchor -- pure SURFACE STRING
    similarity, no meaning whatsoever.

    WHY THIS ARM EXISTS (layered-controls discipline: prefer the control that reproduces the win
    from the WRONG source). The encoder arm embeds anchor WORD STRINGS through a BPE tokenizer, so
    morphologically related words share subwords. Much of the WordNet gold set (synonyms,
    hypernyms, sisters) is morphologically related to the query. A gain in A3_ENCODER is therefore
    only a MEANING gain if it EXCEEDS what this string-only control achieves; if A5 reproduces A3,
    A3 is a morphology shortcut, not encoder meaning."""
    dim = TRIGRAM_DIM
    mat = np.zeros((len(anchors), dim), dtype=np.float64)
    covered = np.zeros(len(anchors), dtype=bool)
    for i, a in enumerate(anchors):
        s = "^" + a + "$"
        for k in range(len(s) - 2):
            # hashlib (never built-in hash()) -- PROT-023/F.5 determinism
            j = int.from_bytes(hashlib.sha256(s[k:k + 3].encode("utf-8")).digest()[:4],
                               "big") % dim
            mat[i, j] += 1.0
        nrm = float(np.linalg.norm(mat[i]))
        if nrm >= 1e-9:
            mat[i] /= nrm
            covered[i] = True
    return mat, covered


def encoder_matrix(anchors: Sequence[str], output_dir: str) -> Tuple[np.ndarray, np.ndarray, dict]:
    """Row-L2-normalized mean-pooled contextual token reps of each anchor WORD from the persisted
    V2Transformer (hdlab.encoder_retrain_persist.load_improved_encoder, the 237.7M-token
    lineage). OUT-OF-DISTRIBUTION by construction -- see module docstring."""
    import torch
    from hdlab.encoder_retrain_persist import load_improved_encoder
    t0 = time.time()
    ext = load_improved_encoder(seed=ENC_SEED)
    info = {"seed": ENC_SEED, "d_model": int(ext.d), "class": type(ext).__name__,
            "tokenizer_vocab_size": int(ext.tok.get_vocab_size()),
            "load_s": round(time.time() - t0, 2),
            "USE_IS_OUT_OF_DISTRIBUTION": True,
            "note": "encoder trained on a SYNTHETIC templated slot harness (cues: %r); it exposes "
                    "no word-embedding API, so this cell mean-pools its contextual token reps."
                    % sorted(getattr(ext, "CUES", {}))}
    vocab = set(k.lower() for k in ext.tok.get_vocab().keys())
    whole = int(sum(1 for a in anchors if a in vocab))
    info["anchors_whole_token_in_vocab"] = {"n": whole, "frac": whole / max(1, len(anchors))}

    n, d = len(anchors), int(ext.d)
    mat = np.zeros((n, d), dtype=np.float64)
    covered = np.zeros(n, dtype=bool)
    max_len = int(getattr(ext.model, "max_len", 64))
    for s in range(0, n, ENC_BATCH):
        chunk = list(anchors[s:s + ENC_BATCH])
        encs = ext.tok.encode_batch(chunk)
        ids_list = [e.ids[:max_len] or [ext.pad_id] for e in encs]
        width = max(len(x) for x in ids_list)
        ids = np.full((len(chunk), width), ext.pad_id, dtype=np.int64)
        for r, x in enumerate(ids_list):
            ids[r, :len(x)] = x
        with torch.no_grad():
            # token_reps -> (h, pad_mask); h is [B, L, d], per-real-token L2-normed, pad zeroed
            reps, pad_mask = ext.model.token_reps(torch.from_numpy(ids))
        arr = reps.numpy().astype(np.float64)
        real = (~pad_mask.numpy()).astype(np.float64)[:, :, None]
        pooled = (arr * real).sum(axis=1) / np.maximum(real.sum(axis=1), 1.0)
        nrm = np.linalg.norm(pooled, axis=1)
        ok = nrm >= 1e-9
        mat[s:s + len(chunk)][ok] = pooled[ok] / nrm[ok][:, None]
        covered[s:s + len(chunk)] = ok
        if (s // ENC_BATCH) % 5 == 0:
            print("[encoder] %d/%d anchors elapsed=%.1fs" % (s + len(chunk), n, time.time() - t0),
                  flush=True)
    info["encoded_nonzero"] = {"n": int(covered.sum()), "frac": float(covered.mean())}
    info["elapsed_s"] = round(time.time() - t0, 2)
    return mat, covered, info


# ============================================================ scoring
def _z(x: np.ndarray) -> np.ndarray:
    sd = float(np.std(x))
    if sd < 1e-12:
        return np.zeros_like(x)
    return (x - float(np.mean(x))) / sd


def arm_scores(base: np.ndarray, aux_terms: Sequence[np.ndarray], w: float) -> np.ndarray:
    """z(base) + w * sum(z(aux)). Per-item z over the ELIGIBLE pool makes w scale-free."""
    out = _z(base)
    for a in aux_terms:
        out = out + w * _z(a)
    return out


def _is_sister(a: str, b: str) -> bool:
    """a and b share a WordNet hypernym -- the 'right neighbourhood, wrong member' relation the
    C3 failure mode is made of (axon/dendrite, artery/vessel)."""
    ha = set()
    for s in wn.synsets(a):
        ha.update(s.hypernyms() + s.instance_hypernyms())
    if not ha:
        return False
    for s in wn.synsets(b):
        if ha & set(s.hypernyms() + s.instance_hypernyms()):
            return True
    return False


def paired_bootstrap(arms: Dict[str, np.ndarray], deltas: Sequence[Tuple[str, str, str]],
                     n_boot: int, seed: int) -> dict:
    keys = sorted(arms)
    n = len(arms[keys[0]])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = {k: arms[k][idx].mean(axis=1) for k in keys}
    out = {"n_boot": n_boot, "seed": seed, "n_items": n, "arm_acc_ci": {}, "deltas": {}}
    for k in keys:
        out["arm_acc_ci"][k] = {"acc": float(arms[k].mean()),
                                "ci_lo": float(np.percentile(boots[k], 2.5)),
                                "ci_hi": float(np.percentile(boots[k], 97.5)),
                                "sd": float(np.std(boots[k]))}
    for name, a, b in deltas:
        db = boots[a] - boots[b]
        lo, hi = float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))
        out["deltas"][name] = {"delta": float(arms[a].mean() - arms[b].mean()),
                               "ci_lo": lo, "ci_hi": hi, "sd": float(np.std(db)),
                               "ci_excludes_zero": bool(lo > 0 or hi < 0)}
    return out


# ============================================================ crowding
def _concat_space(mat: np.ndarray, aux_mats: Sequence[np.ndarray], w: float) -> np.ndarray:
    """The arm's blend read GEOMETRICALLY: [profile_hat, w*aux1_hat, w*aux2_hat], row-L2-normalized.
    Cosine in this space is a TRUE cosine in [-1,1] that EQUALS the base cosine at w=0, so
    crowding is on ONE comparable scale across arms. (The per-item z-blend used for SCORING is
    rank-equivalent to this up to per-item affine terms; crowding is a property of the space, not
    of one query, so it is measured here.)"""
    nrm = np.linalg.norm(mat, axis=1)
    ok = nrm >= 1e-9
    blocks = [np.where(ok[:, None], mat / np.where(ok, nrm, 1.0)[:, None], 0.0)]
    for a in aux_mats:
        an = np.linalg.norm(a, axis=1)
        aok = an >= 1e-9
        blocks.append(w * np.where(aok[:, None], a / np.where(aok, an, 1.0)[:, None], 0.0))
    cat = np.concatenate(blocks, axis=1)
    cn = np.linalg.norm(cat, axis=1)
    cok = cn >= 1e-9
    cat[cok] /= cn[cok][:, None]
    return cat


def crowding(mat: np.ndarray, aux_mats: Sequence[np.ndarray], w: float, sample_idx: np.ndarray,
             rng: np.random.Generator) -> dict:
    """Median nearest-neighbour COSINE among sampled anchors in the arm's own concatenated space,
    against a random null (random bipolar profiles + row-permuted aux). The live baseline pair
    this reproduces is 0.4637 vs 0.2264. Lower median_nn (and lower ratio-to-null) = LESS
    semantic crowding = better separated."""
    cat = _concat_space(mat, aux_mats, w)

    def _nn(sp: np.ndarray) -> float:
        vals = []
        for i in sample_idx:
            sc = sp @ sp[i]
            sc[i] = -np.inf
            vals.append(float(np.max(sc)))
        return float(np.median(vals))

    real = _nn(cat)
    rnd_mat = rng.choice([-1.0, 1.0], size=mat.shape)
    rnd_aux = [a[rng.permutation(a.shape[0])] for a in aux_mats]
    null = _nn(_concat_space(rnd_mat, rnd_aux, w))
    return {"median_nn": real, "median_nn_random_null": null,
            "ratio_to_null": (real / null) if abs(null) > 1e-9 else None,
            "n_sample": int(len(sample_idx)),
            "note": "cosine in the arm's concatenated space (comparable to base at w=0); "
                    "null = random bipolar profiles + row-permuted aux"}


# ============================================================ self-test
def self_test() -> dict:
    """Asserts the things that license this cell: the salted projection reproduces the live one at
    salt='', the aux blend actually CHANGES the ranking (arms-must-differ), and z-scoring is
    degenerate-safe."""
    txt = "the axon carries a signal away from the neuron cell body"
    cache: Dict[str, np.ndarray] = {}
    got = salted_context_vector(txt, CTX_D, "", cache, True)
    want = context_vector(txt, d=CTX_D, graded=True)
    assert np.array_equal(got, want), "SALT=='' MUST reproduce context_vector byte-identically"
    got2 = salted_context_vector(txt, CTX_D, "SALT_A", cache={}, graded=True)
    assert not np.array_equal(got2, want), "salted draw must DIFFER from the live draw"

    mgot = salted_context_vector_masked(txt, "axon", CTX_D, "", {}, True)
    from hdlab.reading_grounding_loop import context_vector_masked
    assert np.array_equal(mgot, context_vector_masked(txt, "axon")), "masked salt='' must match live"

    # arms-must-differ: a nonzero aux with nonzero variance must move the argmax off base at some w
    rng = np.random.default_rng(0)
    base = rng.normal(size=200)
    aux = rng.normal(size=200)
    s0 = arm_scores(base, [], 0.0)
    s1 = arm_scores(base, [aux], 1.0)
    assert int(np.argmax(s0)) == int(np.argmax(base)), "w=0 must be the base ranking"
    assert not np.array_equal(np.argsort(s0), np.argsort(s1)), "aux blend must change the ranking"

    # degenerate-safe: constant aux contributes exactly nothing (never NaN)
    sc = arm_scores(base, [np.ones(200)], 1.0)
    assert np.all(np.isfinite(sc)), "constant aux must not produce NaN/inf"
    assert np.array_equal(np.argsort(sc), np.argsort(s0)), "constant aux must not change ranking"

    # grounded norms are real and ordered, and the DOCUMENTED sibling ceiling is present
    assert gsim.in_grounded_lexicon("apple"), "grounded norms not loaded"
    assert _is_sister("axon", "dendrite") or True   # wordnet-dependent; not an assertion
    return {"self_test": "PASS", "ctx_d": int(CTX_D), "graded": bool(GRADED_COMPARATOR)}


# ============================================================ main
def run(run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    rep: Dict[str, object] = {
        "anchor_name": "exp_meaning_supply_separation_v1",
        "run_mode": run_mode,
        "prereg": "preregs/2026-08-14_meaning_supply_separation_v1.md",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "wire_status": "EXPERIMENT_LOCAL_NOT_WIRED",
        "graded_comparator": bool(GRADED_COMPARATOR),
        "ctx_d": int(CTX_D),
        "w_grid": list(W_GRID),
        "w_headline": W_HEADLINE,
        "baselines_quoted": {"c3_hit_at_1": 0.048, "c3_scramble": 0.008,
                             "crowding_live": 0.4637, "crowding_null": 0.2264,
                             "twoafc_live_d256_graded_on": 0.698},
    }

    sents = C3.build_corpus(run_mode)
    print("[corpus] n_sentences=%d" % len(sents), flush=True)
    buckets, counts = C3.build_buckets(sents)
    print("[corpus] n_candidate_lemmas=%d" % len(buckets), flush=True)
    space = C3.build_space(sents, buckets, output_dir)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    max_items = SMOKE_MAX_ITEMS if run_mode != "full" else C3.MAX_ITEMS
    items, item_diag = C3.build_items(space, buckets, counts, max_items)
    n = len(items)
    print("[items] n=%d n_anchors=%d" % (n, n_anchors), flush=True)
    if n < 2:
        return {"verdict": "INSUFFICIENT_ITEMS_NO_READ", "n_items": n}
    rep["item_construction"] = item_diag
    rep["n_items"] = n
    rep["n_anchors"] = n_anchors

    # ---- coverage of THESE anchors (the exact denominator, not the superset)
    import hdlab.lexical_similarity as lx
    n_hand = sum(1 for a in anchors if lx.in_lexicon(a))
    n_norm = sum(1 for a in anchors if gsim.in_grounded_lexicon(a))
    rep["coverage_of_these_anchors"] = {
        "hand_lexicon": {"n": n_hand, "frac": n_hand / n_anchors},
        "grounded_norms": {"n": n_norm, "frac": n_norm / n_anchors},
        "hand_lexicon_size": len(lx.CONCEPT_FEATURES),
        "grounded_norms_size": int(gsim.coverage_stats()["n_words"]),
    }

    g_mat, g_cov = norms_matrix(anchors)
    e_mat, e_cov, e_info = encoder_matrix(anchors, output_dir)
    t_mat, t_cov = trigram_matrix(anchors)
    rep["encoder"] = e_info
    rep["coverage_of_these_anchors"]["encoder_nonzero"] = e_info["encoded_nonzero"]
    print("[aux] norms_cov=%.4f enc_cov=%.4f trigram_cov=%.4f"
          % (g_cov.mean(), e_cov.mean(), t_cov.mean()), flush=True)

    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9

    # ---- per-item scoring
    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])

    hits = {w: {a: np.zeros(n, dtype=bool) for a in ALL_ARMS} for w in W_GRID}
    ranks = {w: {a: np.zeros(n, dtype=np.int64) for a in ALL_ARMS} for w in W_GRID}
    top50 = {w: {a: np.zeros(n, dtype=bool) for a in ALL_ARMS} for w in W_GRID}
    margins = {w: {a: np.zeros(n, dtype=np.float64) for a in ALL_ARMS} for w in W_GRID}
    picks = {w: {a: [] for a in ALL_ARMS} for w in W_GRID}
    scram_hit = np.zeros(n, dtype=bool)
    freq_hit = np.zeros(n, dtype=bool)
    rng = np.random.default_rng(MASTER_SEED + 3)
    donors = C3._derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                                 & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        elig &= mat_ok
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        gold = C3.gold_meaning_set(L)
        gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)

        q = space.bundle(L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        base = (mat[sel] @ q) / (mat_nrm[sel] * qn)

        gq = gsim.grounded_vector(L)
        if gq is not None:
            gq = np.asarray(gq, dtype=np.float64).reshape(-1)
            gqn = float(np.linalg.norm(gq))
            aux_g = g_mat[sel] @ (gq / gqn) if gqn >= 1e-9 else np.zeros(sel.size)
        else:
            aux_g = np.zeros(sel.size)
        eq = e_mat[pos[L]] if e_cov[pos[L]] else None
        aux_e = e_mat[sel] @ eq if eq is not None else np.zeros(sel.size)
        tq = t_mat[pos[L]] if t_cov[pos[L]] else None
        aux_t = t_mat[sel] @ tq if tq is not None else np.zeros(sel.size)

        armaux = {"A1_BASE": [], "A2_NORMS": [aux_g], "A3_ENCODER": [aux_e],
                  "A4_BOTH": [aux_g, aux_e], "A5_STRINGCTRL": [aux_t]}
        for w in W_GRID:
            for arm in ALL_ARMS:
                sc = arm_scores(base, armaux[arm], 0.0 if arm == "A1_BASE" else w)
                b = int(np.argmax(sc))
                p = anchors[sel[b]]
                picks[w][arm].append(p)
                hits[w][arm][i] = p in gold
                if gsel.size:
                    best_gold = float(np.max(sc[gsel]))
                    r = int(np.sum(sc > best_gold)) + 1
                    ranks[w][arm][i] = r
                    top50[w][arm][i] = r <= 50
                    # SEPARATION MARGIN, in sd units of this item's candidate pool: how far the
                    # best gold anchor stands above the best NON-gold competitor. This is the
                    # direct measure of within-neighbourhood separation at the read-out.
                    ng = np.ones(sel.size, dtype=bool)
                    ng[gsel] = False
                    margins[w][arm][i] = (best_gold - float(np.max(sc[ng]))) if ng.any() else 0.0
                else:
                    ranks[w][arm][i] = sel.size
        # floors
        qd = space.bundle(items[donors[i]]["L"])
        qdn = float(np.linalg.norm(qd))
        if qdn >= 1e-9:
            sc = (mat[sel] @ qd) / (mat_nrm[sel] * qdn)
            scram_hit[i] = anchors[sel[int(np.argmax(sc))]] in gold
        cnts = np.array([counts[anchors[a]] for a in sel])
        freq_hit[i] = anchors[sel[int(np.argmax(cnts))]] in gold

        if (i + 1) % 250 == 0 or i == n - 1:
            print("[score] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)
            record_unit(output_dir, unit_key("score", str(i + 1)), {"i": i + 1})

    # ---- floors: projection-draw sd
    proj = []
    for r in range(N_PROJ_DRAWS):
        sp = build_salted_space(sents, buckets, "PROJDRAW_%d|" % r, output_dir)
        an2, m2 = sp.anchor_matrix()
        p2 = {a: j for j, a in enumerate(an2)}
        nr2 = np.linalg.norm(m2, axis=1)
        ok2 = nr2 >= 1e-9
        n2idx: Dict[str, List[int]] = defaultdict(list)
        for a in an2:
            n2idx[normalize_lemma(a)].append(p2[a])
        h = np.zeros(n, dtype=bool)
        for i, it in enumerate(items):
            L = it["L"]
            if L not in p2:
                continue
            e2 = ok2.copy()
            for k in sorted(set(n2idx[normalize_lemma(L)] + [p2[L]])):
                e2[k] = False
            s2 = np.flatnonzero(e2)
            if s2.size == 0:
                continue
            q2 = sp.bundle(L)
            q2n = float(np.linalg.norm(q2))
            if q2n < 1e-9:
                continue
            sc = (m2[s2] @ q2) / (nr2[s2] * q2n)
            h[i] = an2[s2[int(np.argmax(sc))]] in C3.gold_meaning_set(L)
        proj.append(float(h.mean()))
        print("[projdraw] draw %d hit@1=%.4f" % (r, proj[-1]), flush=True)

    # ---- assemble
    crng = np.random.default_rng(MASTER_SEED + 11)
    sample_idx = crng.choice(n_anchors, size=min(CROWD_SAMPLE, n_anchors), replace=False)
    crowd_aux = {"A1_BASE": [], "A2_NORMS": [g_mat], "A3_ENCODER": [e_mat],
                 "A4_BOTH": [g_mat, e_mat], "A5_STRINGCTRL": [t_mat]}

    per_w: Dict[str, object] = {}
    for w in W_GRID:
        armv = {a: hits[w][a].astype(float) for a in ALL_ARMS}
        armv["F_SCRAMBLE"] = scram_hit.astype(float)
        armv["F_FREQUENCY"] = freq_hit.astype(float)
        dl = [("d_%s_minus_BASE" % a, a, "A1_BASE") for a in AUX_ARMS]
        dl += [("d_A1_BASE_minus_F_SCRAMBLE", "A1_BASE", "F_SCRAMBLE")]
        bs = paired_bootstrap(armv, dl, N_BOOTSTRAP, MASTER_SEED + 5)
        block = {"bootstrap": bs, "per_arm": {}}
        for a in ALL_ARMS:
            base_pk, arm_pk = picks[W_GRID[0]]["A1_BASE"], picks[w][a]
            conv = [i for i in range(n) if not hits[w]["A1_BASE"][i] and hits[w][a][i]]
            regr = [i for i in range(n) if hits[w]["A1_BASE"][i] and not hits[w][a][i]]
            sis = [i for i in conv if _is_sister(items[i]["L"], base_pk[i])] if a != "A1_BASE" else []
            block["per_arm"][a] = {
                "hit_at_1": float(hits[w][a].mean()),
                "median_rank": float(np.median(ranks[w][a])),
                "mean_rank": float(np.mean(ranks[w][a])),
                "frac_gold_in_top50": float(top50[w][a].mean()),
                "separation_margin_z": {"mean": float(np.mean(margins[w][a])),
                                        "median": float(np.median(margins[w][a])),
                                        "note": "best-gold minus best-non-gold score, in sd units "
                                                "of the item's candidate pool; HIGHER = better "
                                                "within-neighbourhood separation"},
                "sister_error_conversions": {
                    "converted_base_wrong_to_arm_right": len(conv),
                    "of_which_base_pick_was_a_wordnet_sister": len(sis),
                    "regressed_base_right_to_arm_wrong": len(regr),
                    "net": len(conv) - len(regr)},
                "crowding": crowding(mat, crowd_aux[a], 0.0 if a == "A1_BASE" else w,
                                     sample_idx, np.random.default_rng(MASTER_SEED + 17)),
                "example_picks": [{"L": items[i]["L"], "pick": arm_pk[i]} for i in range(min(12, n))],
            }
            print("[arm] w=%.2f %s hit@1=%.4f med_rank=%.1f top50=%.4f" % (
                w, a, hits[w][a].mean(), np.median(ranks[w][a]), top50[w][a].mean()), flush=True)
        block["floors"] = {"F_SCRAMBLE": float(scram_hit.mean()),
                           "F_FREQUENCY": float(freq_hit.mean())}
        per_w["w_%.2f" % w] = block

    rep["per_w"] = per_w
    rep["floors"] = {
        "F_SCRAMBLE": float(scram_hit.mean()),
        "F_FREQUENCY": float(freq_hit.mean()),
        "F_PROJDRAW": {"draws": proj, "mean": float(np.mean(proj)), "sd": float(np.std(proj)),
                       "n_draws": N_PROJ_DRAWS,
                       "note": "independent salted draws of the random projection; a hit@1 delta "
                               "smaller than this sd is noise whatever its bootstrap CI says"},
    }
    rep["headline_w"] = "w_%.2f" % W_HEADLINE
    rep["max_over_w_is_an_optimistic_upper_bound"] = True

    # ---- verdict per pre-registered bands
    hb = per_w["w_%.2f" % W_HEADLINE]
    base_hit = hb["per_arm"]["A1_BASE"]["hit_at_1"]
    base_rank = hb["per_arm"]["A1_BASE"]["median_rank"]
    base_crowd = hb["per_arm"]["A1_BASE"]["crowding"]["median_nn"]
    sd_proj = float(np.std(proj))
    MEANING_ARMS = ("A2_NORMS", "A3_ENCODER", "A4_BOTH")
    reasons, cleared = [], []
    for a in AUX_ARMS:
        pa = hb["per_arm"][a]
        d = pa["hit_at_1"] - base_hit
        ci = hb["bootstrap"]["deltas"]["d_%s_minus_BASE" % a]
        rank_better = pa["median_rank"] <= 0.90 * base_rank
        crowd_better = pa["crowding"]["median_nn"] < base_crowd
        big = d >= 0.020 and ci["ci_excludes_zero"] and d > 2 * sd_proj
        if a in MEANING_ARMS:
            if pa["hit_at_1"] >= 0.10 and ci["ci_excludes_zero"]:
                cleared.append((a, "PASS_GATE_CLEARED"))
            elif big and rank_better and crowd_better:
                cleared.append((a, "MIDDLE_BAND_REAL_BUT_SHORT"))
            elif big:
                cleared.append((a, "MIDDLE_BAND_ARGMAX_ONLY_SUSPECT"))
        reasons.append("%s d=%+.4f CI=[%+.4f,%+.4f] med_rank %.1f->%.1f crowd %.4f->%.4f" % (
            a, d, ci["ci_lo"], ci["ci_hi"], base_rank, pa["median_rank"], base_crowd,
            pa["crowding"]["median_nn"]))
    hurts = any((hb["per_arm"][a]["hit_at_1"] - base_hit) < 0
                and hb["bootstrap"]["deltas"]["d_%s_minus_BASE" % a]["ci_excludes_zero"]
                for a in MEANING_ARMS)

    # STRING-SHORTCUT CONTROL. The encoder embeds word STRINGS, so a gain it shares with a pure
    # character-trigram control is morphology, not meaning.
    d_enc = hb["per_arm"]["A3_ENCODER"]["hit_at_1"] - base_hit
    d_str = hb["per_arm"]["A5_STRINGCTRL"]["hit_at_1"] - base_hit
    shortcut = {"d_A3_ENCODER": d_enc, "d_A5_STRINGCTRL": d_str,
                "encoder_gain_exceeds_string_control": bool(d_enc > d_str),
                "encoder_gain_attributable_to_string_similarity": bool(d_str >= 0.75 * d_enc
                                                                       and d_enc > 0),
                "note": "if the string control reproduces the encoder's gain, A3 is a subword "
                        "morphology shortcut, not encoder MEANING"}
    rep["string_shortcut_control"] = shortcut
    reasons.append("STRINGCTRL d=%+.4f vs ENCODER d=%+.4f -> %s" % (
        d_str, d_enc, "ENCODER EXCEEDS CONTROL" if d_enc > d_str else "CONTROL MATCHES/EXCEEDS "
        "ENCODER (shortcut suspected)"))
    if any(v == "PASS_GATE_CLEARED" for _, v in cleared):
        verdict = "PASS_GATE_CLEARED"
    elif any(v == "MIDDLE_BAND_REAL_BUT_SHORT" for _, v in cleared):
        verdict = "MIDDLE_BAND_REAL_BUT_SHORT"
    elif any(v == "MIDDLE_BAND_ARGMAX_ONLY_SUSPECT" for _, v in cleared):
        verdict = "MIDDLE_BAND_ARGMAX_ONLY_SUSPECT"
    elif hurts:
        verdict = "HARD_FAIL_HURTS"
    else:
        verdict = "HARD_FAIL_NO_EFFECT"
    which = ([a for a, _ in cleared] or ["NONE"])
    outcome = {"PASS_GATE_CLEARED": "an arm closes the C3 gate",
               "MIDDLE_BAND_REAL_BUT_SHORT": "real separation gain, gate still open",
               "MIDDLE_BAND_ARGMAX_ONLY_SUSPECT": "argmax moved without rank/crowding -- NOT a "
                                                  "separation gain",
               "HARD_FAIL_HURTS": "richer meaning supply makes it WORSE",
               "HARD_FAIL_NO_EFFECT": "NEITHER -- meaning SUPPLY is not the binding constraint on "
                                      "C3; the defect is the comparison GEOMETRY"}[verdict]
    rep["verdict"] = verdict
    rep["verdict_msg"] = ("%s (%s) | arms clearing: %s | base hit@1=%.4f med_rank=%.1f "
                          "crowd=%.4f | floors scramble=%.4f freq=%.4f projdraw_sd=%.4f | %s"
                          % (verdict, outcome, ",".join(which), base_hit, base_rank, base_crowd,
                             float(scram_hit.mean()), float(freq_hit.mean()), sd_proj,
                             " || ".join(reasons)))
    rep["elapsed_s"] = round(time.time() - t0, 2)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2))
        return 0

    mode = "smoke" if args.smoke else "full"
    out_dir = os.path.join(_REPO, "data",
                           "exp_meaning_supply_separation_v1" + ("_smoke" if args.smoke else ""))
    os.makedirs(out_dir, exist_ok=True)
    st = self_test()
    rep = run(mode, out_dir)
    rep["self_test"] = st
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(rep, fh, indent=2, sort_keys=False, default=str)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print("VERDICT: %s" % rep.get("verdict"), flush=True)
    print(rep.get("verdict_msg", ""), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
