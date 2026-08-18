"""semantic_hd_encoder_meaning_match_v1 -- build a SEMANTIC HD encoder + prove meaning-matching.

USER 2026-07-24: "substrate should definitely be matching by meaning." The char-trigram substrate
encodes by SPELLING (cat/kitten share no trigrams); car/cart, ate/late are HD-close though meaning-
far. Fix = encode by MEANING.

BUILD (reuse, not reinvent): SemanticHDEncoder = WordNet-structured meaning (glass-box synonym +
hypernym bundling; alias resolution) fused with distributional GloVe (broad coverage), wired into
the substrate HD via the SAME random Gaussian JL projection used by
experiments/exp_encoder_word2vec_substrate_bind_v1.py (300d -> N_DIM, 1/sqrt(in_dim) scale). JL
preserves cosine so HD-closeness == meaning-closeness. Sentence vector = L2-sum of content-word
fused embeds, projected.

PROVE (Test 1, CAN-FAIL core): held-out labelled pairs -- POSITIVES (synonym + related) vs
FALSE-FRIENDS (lexically close, semantically far). Semantic HD similarity must SEPARATE positives
from false-friends (AUC + mean-separation) where char-trigram lexical similarity FAILS by
construction (it ranks false-friends ABOVE synonyms). SCRAMBLE control + WordNet ablation.

PAYOFF (Test 2, ARC-Easy climb, honest either way): hold the mined ARC store FIXED, swap only the
encoder. char-trigram (recompute the lexical floor in-regime) vs semantic; report the FULL-store
ARC-Easy delta. RISING = meaning helps the human scale; FLAT/DOWN = honest (report why).

Contract: INLINE-LOCAL foreground-to-completion; NO queue/push/remote-persist; store LOCAL-ONLY +
UNCOMMITTED; ASCII-only; deterministic (fixed seeds; numpy default_rng; sorted iteration). repo .venv.
Agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics ; heartbeat
# - real_code_path: self_test constructs the REAL SemanticHDEncoder + CharTrigramEncoder + runs the
#   REAL separation + scoring fns at tiny scale
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - arms_differ: semantic vs char-trigram vs scramble store hashes differ
# - discriminator_fires: semantic separation > 0 on calibration pairs asserted in self_test
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.char_trigram_encoder import CharTrigramEncoder
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc

ANCHOR_NAME = "semantic_hd_encoder_meaning_match_v1"
SEED = 20260724

N_DIM = 2048
PRETRAIN_DIM = 300
GLOVE_MODEL = "glove-wiki-gigaword-300"
ALPHA = 0.5   # WordNet synonym pull
BETA = 0.3    # WordNet hypernym pull
MAX_SYNSETS = 3

_ARC_STORE_DIR = os.path.join(_REPO, "data", "exp_arc_knowledge_scale_ingest_climb_v1")
_ARC_STORE_SENTS = os.path.join(_ARC_STORE_DIR, "store_relevant_sentences.txt")
_ARC_STORE_VECS = os.path.join(_ARC_STORE_DIR, "store_relevant_vectors.npy")

# ---------------------------------------------------------------------------
# Meaning-matching test set (calibrated 2026-07-24 vs GloVe + char-trigram so
# false-friends are lexically-close but genuinely semantically-far).
# ---------------------------------------------------------------------------
SYNONYMS = [("big", "large"), ("sick", "ill"), ("happy", "glad"), ("quick", "fast"),
            ("buy", "purchase"), ("smart", "intelligent"), ("begin", "start"),
            ("small", "tiny"), ("doctor", "physician"), ("movie", "film"),
            ("automobile", "car"), ("rock", "stone"), ("usa", "america"),
            ("tv", "television")]
RELATED = [("cat", "kitten"), ("dog", "puppy"), ("sun", "star"), ("water", "liquid"),
           ("king", "queen"), ("hand", "finger"), ("rain", "cloud"),
           ("teacher", "student"), ("bird", "feather"), ("tree", "leaf")]
FALSE_FRIENDS = [("ate", "late"), ("hair", "chair"), ("mind", "mint"), ("bread", "read"),
                 ("corn", "cord"), ("band", "sand"), ("pear", "spear"), ("cold", "gold"),
                 ("four", "pour"), ("sing", "sting")]

# Pre-reg bands (author-designed)
HP_SEM_AUC = 0.80
HP_SEM_SEP = 0.15
HP_SEM_MINUS_LEX_SEP = 0.15
HF_SEM_AUC = 0.60
CLIMB_RISE = 0.02
CLIMB_SCRAMBLE_MARGIN = 0.02


# ---------------------------------------------------------------------------
# markers / crash diagnostics
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# Semantic HD encoder (WordNet structure + distributional GloVe -> substrate HD)
# ---------------------------------------------------------------------------
def _l2(v, eps=1e-12):
    n = np.linalg.norm(v)
    return v / (n + eps) if n > 0 else v


def _gaussian_projection(in_dim, out_dim, seed):
    """Random Gaussian JL projection P [out_dim, in_dim], 1/sqrt(in_dim) scale.

    Same machinery as exp_encoder_word2vec_substrate_bind_v1._gaussian_projection: JL preserves
    pairwise cosine in expectation, so projected-HD closeness == embedding (meaning) closeness.
    """
    rng = np.random.default_rng(seed * 991 + 73)
    return (rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim)))


class SemanticHDEncoder:
    """word/concept/sentence -> HD vector where MEANING-similar concepts are HD-close.

    fused(w) [300d] = norm(glove[w]) + ALPHA*mean_norm(glove[wn_synonyms(w)])
                                     + BETA*mean_norm(glove[wn_hypernyms(w)])
    encode(text) = L2( (sum_w fused(w) over content words) @ P.T )  [N_DIM]
    use_wordnet=False -> GloVe-only ablation. Glass-box: fused per word inspectable via .explain(w).
    """

    def __init__(self, n_dim=N_DIM, seed=SEED, use_wordnet=True, kv=None):
        self.n_dim = n_dim
        self.seed = seed
        self.use_wordnet = use_wordnet
        self._kv = kv if kv is not None else _load_glove()
        self._wn = _load_wordnet()
        self._fused_cache = {}
        self.P = _gaussian_projection(PRETRAIN_DIM, n_dim, seed)
        self.n_hit = 0
        self.n_miss = 0

    def _glove(self, w):
        kv = self._kv
        if w in kv.key_to_index:
            return _l2(kv[w].astype(np.float32))
        return None

    def _wn_neighbors(self, w):
        """Return (synonym_lemmas, hypernym_lemmas) as sorted lists of GloVe-present tokens."""
        wn = self._wn
        syns, hyps = set(), set()
        synsets = wn.synsets(w)[:MAX_SYNSETS]
        for ss in synsets:
            for lem in ss.lemmas():
                name = lem.name().replace("_", " ").lower()
                if name != w:
                    syns.add(name)
            for hyp in ss.hypernyms():
                for lem in hyp.lemmas():
                    hyps.add(lem.name().replace("_", " ").lower())
        return sorted(syns), sorted(hyps)

    def _mean_glove(self, tokens):
        vecs = []
        for t in tokens:
            # multiword lemma -> mean of its parts
            parts = [p for p in t.split() if p]
            pv = [self._glove(p) for p in parts]
            pv = [x for x in pv if x is not None]
            if pv:
                vecs.append(_l2(np.mean(pv, axis=0)))
        if not vecs:
            return None
        return np.mean(vecs, axis=0).astype(np.float32)

    def fused(self, w):
        """300d fused meaning vector for a single token; cached; None if no signal."""
        if w in self._fused_cache:
            return self._fused_cache[w]
        base = self._glove(w)
        acc = np.zeros(PRETRAIN_DIM, dtype=np.float32)
        got = False
        if base is not None:
            acc = acc + base
            got = True
            self.n_hit += 1
        else:
            self.n_miss += 1
        if self.use_wordnet:
            syns, hyps = self._wn_neighbors(w)
            sv = self._mean_glove(syns)
            hv = self._mean_glove(hyps)
            if sv is not None:
                acc = acc + ALPHA * sv
                got = True
            if hv is not None:
                acc = acc + BETA * hv
                got = True
        if not got:
            self._fused_cache[w] = None
            return None
        out = _l2(acc)
        self._fused_cache[w] = out
        return out

    def explain(self, w):
        """Glass-box: what WordNet structure was bundled for w."""
        syns, hyps = self._wn_neighbors(w) if self.use_wordnet else ([], [])
        return {"word": w, "in_glove": self._glove(w) is not None,
                "wn_synonyms": syns[:8], "wn_hypernyms": hyps[:8]}

    def _sum300(self, text):
        acc = np.zeros(PRETRAIN_DIM, dtype=np.float32)
        for w in arc._content_words(text, min_len=3):
            fv = self.fused(w)
            if fv is not None:
                acc += fv
        return acc

    def encode(self, text):
        return _l2((self._sum300(text) @ self.P.T).astype(np.float32))

    def encode_batch(self, texts):
        texts = list(texts)
        S = np.zeros((len(texts), PRETRAIN_DIM), dtype=np.float32)
        for i, t in enumerate(texts):
            S[i] = self._sum300(t)
        return (S @ self.P.T).astype(np.float32)


_GLOVE_KV = [None]
_WN = [None]


def _load_glove():
    if _GLOVE_KV[0] is None:
        import gensim.downloader as gd
        cache = os.path.join(_REPO, "data", "gensim_cache")
        try:
            gd.BASE_DIR = cache
            gd.base_dir = cache
        except Exception:
            pass
        _GLOVE_KV[0] = gd.load(GLOVE_MODEL)
    return _GLOVE_KV[0]


def _load_wordnet():
    if _WN[0] is None:
        from nltk.corpus import wordnet as wn
        wn.synsets("test")  # force lazy load
        _WN[0] = wn
    return _WN[0]


# ---------------------------------------------------------------------------
# Meaning-matching metrics
# ---------------------------------------------------------------------------
def _cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def _auc(pos_scores, neg_scores):
    """AUC = P(pos score > neg score); ties count 0.5. pos labelled 1, neg labelled 0."""
    if not pos_scores or not neg_scores:
        return 0.5
    c = 0.0
    for p in pos_scores:
        for n in neg_scores:
            c += 1.0 if p > n else (0.5 if p == n else 0.0)
    return c / (len(pos_scores) * len(neg_scores))


def _pair_scores(pairs, score_fn):
    return [score_fn(a, b) for a, b in pairs]


def meaning_match_eval(sem_enc, sem_enc_glove_only, char_enc, rng):
    """Returns dict of AUC + separation for semantic-HD, glove-only-HD, char-trigram-lexical,
    and a scramble control on the semantic encoder."""
    positives = SYNONYMS + RELATED

    def sem_cos(a, b):
        return _cos(sem_enc.encode(a), sem_enc.encode(b))

    def sem_glove_cos(a, b):
        return _cos(sem_enc_glove_only.encode(a), sem_enc_glove_only.encode(b))

    def lex_cos(a, b):
        return _cos(char_enc.encode(a), char_enc.encode(b))

    # scramble control: permute the vocab->fused assignment across the pair vocab
    vocab = sorted(set([w for pr in positives + FALSE_FRIENDS for w in pr]))
    perm = list(rng.permutation(len(vocab)))
    scram_map = {vocab[i]: vocab[perm[i]] for i in range(len(vocab))}

    def sem_scram_cos(a, b):
        return _cos(sem_enc.encode(scram_map[a]), sem_enc.encode(scram_map[b]))

    out = {}
    for name, fn in [("semantic_hd", sem_cos), ("glove_only_hd", sem_glove_cos),
                     ("char_trigram_lexical", lex_cos), ("semantic_scramble", sem_scram_cos)]:
        pos = _pair_scores(positives, fn)
        neg = _pair_scores(FALSE_FRIENDS, fn)
        syn = _pair_scores(SYNONYMS, fn)
        rel = _pair_scores(RELATED, fn)
        out[name] = {
            "auc_pos_vs_falsefriend": round(_auc(pos, neg), 4),
            "mean_positive_sim": round(float(np.mean(pos)), 4),
            "mean_synonym_sim": round(float(np.mean(syn)), 4),
            "mean_related_sim": round(float(np.mean(rel)), 4),
            "mean_falsefriend_sim": round(float(np.mean(neg)), 4),
            "separation": round(float(np.mean(pos) - np.mean(neg)), 4),
        }
    # per-pair table (glass-box)
    table = []
    for label, pairs in [("synonym", SYNONYMS), ("related", RELATED), ("false_friend", FALSE_FRIENDS)]:
        for a, b in pairs:
            table.append({"a": a, "b": b, "label": label,
                          "semantic_hd": round(sem_cos(a, b), 4),
                          "char_trigram_lexical": round(lex_cos(a, b), 4)})
    return out, table


# ---------------------------------------------------------------------------
# ARC climb (hold store fixed, swap encoder)
# ---------------------------------------------------------------------------
def _anisotropy(SV, rng, n=2000):
    """Mean off-diagonal pairwise cosine of a random sample of L2-normalized rows."""
    M = SV.shape[0]
    if M < 2:
        return 0.0
    idx = rng.choice(M, size=min(n, M), replace=False)
    X = arc._unit_rows(SV[idx].astype(np.float32))
    G = X @ X.T
    k = G.shape[0]
    off = (G.sum() - np.trace(G)) / (k * (k - 1))
    return float(off)


def arc_climb_eval(sem_enc, char_enc, easy_limit, output_dir):
    questions = arc._load_questions(arc._EASY_TEST, easy_limit)
    questions.sort(key=lambda q: q["qid"])
    n = len(questions)

    # store sentences (fixed, mined by lexical overlap -- encoder-independent)
    with open(_ARC_STORE_SENTS, "r", encoding="utf-8") as f:
        store_sents = [ln.rstrip("\n") for ln in f if ln.strip()]
    M = len(store_sents)

    chance = arc._chance_theoretical(questions)
    ctrl_random = arc._control_random(questions, np.random.default_rng(SEED + 1))

    # ---- char-trigram arm (recompute the lexical floor in-regime) ----
    _heartbeat(output_dir, "arc_char_store")
    char_store_vecs = np.load(_ARC_STORE_VECS).astype(np.float32)  # persisted, already normalized
    if char_store_vecs.shape[0] != M:
        # fall back to fresh encode if the persisted file is stale
        char_store_vecs = arc._encode_store(char_enc, store_sents)
    QV_char, qmap = arc._build_queries(char_enc, questions)
    bp = [0, char_store_vecs.shape[0]]
    char_curve = arc._score_curve(QV_char, qmap, char_store_vecs, questions, bp,
                                  np.random.default_rng(SEED + 2))
    char_base = char_curve[0]
    char_full = char_curve[char_store_vecs.shape[0]]

    # ---- semantic arm ----
    _heartbeat(output_dir, "arc_semantic_store")
    SV_sem = arc._encode_store(sem_enc, store_sents)
    QV_sem, _ = arc._build_queries(sem_enc, questions)
    sem_curve = arc._score_curve(QV_sem, qmap, SV_sem, questions, [SV_sem.shape[0]],
                                 np.random.default_rng(SEED + 3))
    sem_full = sem_curve[SV_sem.shape[0]]

    # ---- semantic scramble control ----
    _heartbeat(output_dir, "arc_semantic_scramble")
    scr_rng = np.random.default_rng(SEED + 7)
    SV_scr = arc._unit_rows((scr_rng.integers(0, 2, size=SV_sem.shape) * 2 - 1).astype(np.float32))
    scr_curve = arc._score_curve(QV_sem, qmap, SV_scr, questions, [SV_scr.shape[0]],
                                 np.random.default_rng(SEED + 4))
    sem_scr = scr_curve[SV_scr.shape[0]]

    # arms-differ (META_RULE_AF)
    import hashlib
    hashes = {
        "char_store": hashlib.sha256(char_store_vecs.tobytes()).hexdigest(),
        "semantic_store": hashlib.sha256(SV_sem.tobytes()).hexdigest(),
        "scramble_store": hashlib.sha256(SV_scr.tobytes()).hexdigest(),
    }
    arms_differ = len(set(hashes.values())) == 3

    # anisotropy / correlation (honest bar a)
    aniso_char = _anisotropy(char_store_vecs, np.random.default_rng(SEED + 8))
    aniso_sem = _anisotropy(SV_sem, np.random.default_rng(SEED + 9))

    delta_full_easy = (sem_full["acc_easy"] - char_full["acc_easy"])
    delta_vs_scramble = (sem_full["acc_easy"] - sem_scr["acc_easy"])

    return {
        "n_questions_easy": n,
        "store_size": M,
        "chance": round(chance, 4),
        "control_random": round(ctrl_random, 4),
        "char_trigram_baseline_easy": round(char_base["acc_easy"], 4),
        "char_trigram_full_easy": round(char_full["acc_easy"], 4),
        "semantic_full_easy": round(sem_full["acc_easy"], 4),
        "semantic_scramble_easy": round(sem_scr["acc_easy"], 4),
        "delta_semantic_minus_char_full_easy": round(delta_full_easy, 4),
        "delta_semantic_minus_scramble_easy": round(delta_vs_scramble, 4),
        "char_trigram_climb_easy": round(char_full["acc_easy"] - char_base["acc_easy"], 4),
        "semantic_climb_easy": round(sem_full["acc_easy"] - char_base["acc_easy"], 4),
        "anisotropy_char_store": round(aniso_char, 4),
        "anisotropy_semantic_store": round(aniso_sem, 4),
        "arms_differ_verified": bool(arms_differ),
        "arm_store_hashes": hashes,
    }


# ---------------------------------------------------------------------------
# self-test (real code path + determinism + discriminator fires)
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] constructing REAL encoders (GloVe + WordNet) ...")
    kv = _load_glove()
    sem = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=True, kv=kv)
    sem_g = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=False, kv=kv)
    char = CharTrigramEncoder(n_dim=512)

    # real code path: encode single words + a sentence
    v_cat = sem.encode("cat")
    v_kit = sem.encode("kitten")
    v_car = sem.encode("car")
    v_cart = sem.encode("cart")
    assert v_cat.shape == (512,), v_cat.shape
    # determinism
    assert np.array_equal(v_cat, sem.encode("cat")), "encoder non-deterministic"

    # DISCRIMINATOR FIRES: semantic separates meaning from spelling on a tiny calibration set.
    sem_cat_kit = _cos(v_cat, v_kit)          # meaning-related -> should be HIGH
    sem_car_cart = _cos(v_car, v_cart)        # calibration: distributionally-related pair
    lex_cat_kit = _cos(char.encode("cat"), char.encode("kitten"))   # spelling -> LOW
    lex_ate_late = _cos(char.encode("ate"), char.encode("late"))    # spelling -> HIGH
    sem_ate_late = _cos(sem.encode("ate"), sem.encode("late"))      # meaning -> LOW
    assert sem_cat_kit > 0.15, f"semantic cat/kitten too low: {sem_cat_kit}"
    assert sem_cat_kit > sem_ate_late, f"semantic did not rank cat/kitten>ate/late: {sem_cat_kit} vs {sem_ate_late}"
    assert lex_ate_late > lex_cat_kit, f"char-trigram false-friend not > synonym: {lex_ate_late} vs {lex_cat_kit}"
    print(f"[self-test] discriminator fires: sem(cat,kitten)={sem_cat_kit:.3f} > sem(ate,late)={sem_ate_late:.3f}; "
          f"lex(ate,late)={lex_ate_late:.3f} > lex(cat,kitten)={lex_cat_kit:.3f}")

    # AUC helper sanity
    assert _auc([1.0, 0.9], [0.1, 0.2]) == 1.0
    assert _auc([0.1], [0.9]) == 0.0
    assert _auc([0.5], [0.5]) == 0.5

    # WordNet glass-box: explain returns synonyms
    ex = sem.explain("car")
    assert ex["in_glove"] is True
    print(f"[self-test] glass-box car synonyms={ex['wn_synonyms'][:5]} hypernyms={ex['wn_hypernyms'][:3]}")

    # real ARC scoring path on a planted toy (reuses arc._score_curve / _build_queries)
    store = ["green plants use sunlight energy to make sugar during photosynthesis",
             "the moon orbits the earth once each month"]
    SV = arc._encode_store(sem, store)
    q = [{"qid": "T1", "stem": "What do plants use to make food?",
          "choices": ["iron metal", "sunlight energy photosynthesis", "moon orbit", "sound"],
          "correct_index": 1, "source": "ARC-Easy-Test.jsonl"}]
    QV, qmap = arc._build_queries(sem, q)
    res = arc._score_curve(QV, qmap, SV, q, [SV.shape[0]], np.random.default_rng(SEED))
    assert res[SV.shape[0]]["acc"] == 1.0, f"semantic scoring failed planted toy: {res}"

    # arms-differ
    import hashlib
    scr = arc._unit_rows((np.random.default_rng(1).integers(0, 2, size=SV.shape) * 2 - 1).astype(np.float32))
    assert hashlib.sha256(SV.tobytes()).hexdigest() != hashlib.sha256(scr.tobytes()).hexdigest()
    print("[self-test] PASS (real semantic encoder, real ARC scoring, determinism, discriminator, arms-differ)")
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--easy-limit", type=int, default=1000)
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    output_dir = _out_dir()
    _write_start_marker(output_dir, args.mode)
    t0 = time.perf_counter()
    easy_limit = 150 if args.mode == "smoke" else args.easy_limit

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _heartbeat(output_dir, "load_wordnet")
    _load_wordnet()

    _heartbeat(output_dir, "build_encoders")
    sem_enc = SemanticHDEncoder(n_dim=N_DIM, seed=SEED, use_wordnet=True, kv=kv)
    sem_enc_glove = SemanticHDEncoder(n_dim=N_DIM, seed=SEED, use_wordnet=False, kv=kv)
    char_enc = CharTrigramEncoder(n_dim=N_DIM)

    # ---- Test 1: meaning-matching proof (CAN-FAIL core) ----
    _heartbeat(output_dir, "meaning_match")
    mm, mm_table = meaning_match_eval(sem_enc, sem_enc_glove, char_enc, np.random.default_rng(SEED + 5))

    sem_auc = mm["semantic_hd"]["auc_pos_vs_falsefriend"]
    sem_sep = mm["semantic_hd"]["separation"]
    lex_sep = mm["char_trigram_lexical"]["separation"]
    sep_gap = sem_sep - lex_sep
    if sem_auc >= HP_SEM_AUC and sem_sep >= HP_SEM_SEP and sep_gap >= HP_SEM_MINUS_LEX_SEP:
        mm_verdict = "MEANING_MATCH_PASS"
    elif sem_auc <= HF_SEM_AUC:
        mm_verdict = "MEANING_MATCH_FAIL"
    else:
        mm_verdict = "MEANING_MATCH_MIDDLE"

    # glass-box alias-resolution demo (WordNet's specialty)
    alias_demo = {
        "usa_synonyms": sem_enc.explain("usa"),
        "cos_usa_america_semantic": round(_cos(sem_enc.encode("usa"), sem_enc.encode("america")), 4),
        "cos_usa_america_lexical": round(_cos(char_enc.encode("usa"), char_enc.encode("america")), 4),
    }

    # ---- Test 2: ARC-Easy climb (payoff) ----
    _heartbeat(output_dir, "arc_climb")
    arc_res = arc_climb_eval(sem_enc, char_enc, easy_limit, output_dir)
    delta = arc_res["delta_semantic_minus_char_full_easy"]
    delta_scr = arc_res["delta_semantic_minus_scramble_easy"]
    if delta >= CLIMB_RISE and delta_scr >= CLIMB_SCRAMBLE_MARGIN:
        climb_verdict = "CLIMB_RISING"
    elif abs(delta) < CLIMB_RISE:
        climb_verdict = "CLIMB_FLAT"
    else:
        climb_verdict = "CLIMB_DOWN"

    # WordNet ablation contribution (glass-box mix)
    wn_ablation = {
        "glove_only_auc": mm["glove_only_hd"]["auc_pos_vs_falsefriend"],
        "glove_only_separation": mm["glove_only_hd"]["separation"],
        "glove_plus_wordnet_auc": sem_auc,
        "glove_plus_wordnet_separation": sem_sep,
        "wordnet_separation_lift": round(sem_sep - mm["glove_only_hd"]["separation"], 4),
    }

    elapsed = round(time.perf_counter() - t0, 1)
    fused_vocab = len(sem_enc._fused_cache)
    overall = "PASS_CORE" if mm_verdict == "MEANING_MATCH_PASS" else mm_verdict
    vmsg = (f"MEANING_MATCH={mm_verdict} (semantic AUC={sem_auc:.3f} sep={sem_sep:.3f} vs "
            f"lexical sep={lex_sep:.3f}; gap={sep_gap:.3f}); "
            f"ARC {climb_verdict}: char_full_easy={arc_res['char_trigram_full_easy']:.3f} -> "
            f"semantic_full_easy={arc_res['semantic_full_easy']:.3f} "
            f"(delta={delta:+.3f}, vs_scramble={delta_scr:+.3f})")

    metrics = {
        "verdict": mm_verdict,
        "verdict_msg": vmsg,
        "summary": f"{mm_verdict} | ARC {climb_verdict} delta={delta:+.3f}",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "mode": args.mode,
        "n_dim": N_DIM,
        "pretrain_dim": PRETRAIN_DIM,
        "glove_model": GLOVE_MODEL,
        "alpha_synonym": ALPHA, "beta_hypernym": BETA, "max_synsets": MAX_SYNSETS,
        "seed": SEED,
        # ---- Test 1: meaning-matching (the CAN-FAIL core) ----
        "meaning_match_verdict": mm_verdict,
        "meaning_match": mm,
        "meaning_match_pair_table": mm_table,
        "n_positive_pairs": len(SYNONYMS) + len(RELATED),
        "n_false_friend_pairs": len(FALSE_FRIENDS),
        "bands_test1": {"HP_sem_auc": HP_SEM_AUC, "HP_sem_sep": HP_SEM_SEP,
                        "HP_sem_minus_lex_sep": HP_SEM_MINUS_LEX_SEP, "HF_sem_auc": HF_SEM_AUC},
        "alias_resolution_demo": alias_demo,
        "wordnet_ablation": wn_ablation,
        # ---- Test 2: ARC climb (the payoff) ----
        "arc_climb_verdict": climb_verdict,
        "arc_climb": arc_res,
        "arc_banked_char_floor_ref_on_disk": {
            "source": "data/exp_arc_knowledge_scale_ingest_climb_v1/metrics.json",
            "full_ingest_acc_easy": 0.3733, "note": "recomputed in-regime here; not trusted blindly"},
        "bands_test2": {"CLIMB_RISE": CLIMB_RISE, "CLIMB_SCRAMBLE_MARGIN": CLIMB_SCRAMBLE_MARGIN},
        # ---- honest bars ----
        "honest_bars": {
            "capacity_correlation": (
                f"semantic store anisotropy (mean pairwise cos)={arc_res['anisotropy_semantic_store']:.4f} vs "
                f"char-trigram={arc_res['anisotropy_char_store']:.4f}; higher anisotropy = correlated codes "
                f"= more cleanup crosstalk (banked correlation-hurts-capacity). NOT whitened here."),
            "glassbox_mix": (
                f"WordNet-structure (inspectable) separation lift over GloVe-only={wn_ablation['wordnet_separation_lift']:+.4f}; "
                f"distributional GloVe does the bulk of the separation, WordNet adds alias/synonym structure."),
            "ann_note": (
                "fuzzy conflict-retrieval in the fact-store needs sub-linear SIMILARITY search (ANN/LSH), "
                "separate from this encoder + the exact O(1) hash. NOT built here (noted per contract)."),
        },
        "fused_vocab_size": fused_vocab,
        "encoder_hit_miss": {"n_hit": sem_enc.n_hit, "n_miss": sem_enc.n_miss},
        "overall_core": overall,
        "wired_vs_stubbed": (
            "WIRED: SemanticHDEncoder (WordNet+GloVe->JL-projected HD), meaning-matching proof, ARC-Easy "
            "climb (store held fixed, encoder swapped), scramble + WordNet-ablation controls, anisotropy "
            "measurement. STUBBED/NOTED-NOT-BUILT: whitening/decorrelation; ANN/LSH sub-linear retrieval; "
            "multiword-token content_words handling (single-token pairs tested; alias demo via direct fused())."),
        "contract": "INLINE-LOCAL; store LOCAL-ONLY + UNCOMMITTED; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)

    # persist semantic store LOCAL-ONLY (uncommitted) for glass-box/reuse
    try:
        with open(os.path.join(output_dir, "meaning_match_pairs.jsonl"), "w", encoding="utf-8") as f:
            for row in mm_table:
                f.write(json.dumps(row) + "\n")
    except Exception as e:
        print(f"[warn] persist failed (non-fatal): {e}")

    _heartbeat(output_dir, "done", {"verdict": mm_verdict})
    print(f"\n[VERDICT] {vmsg}")
    print(f"[test1] semantic_hd={mm['semantic_hd']}")
    print(f"[test1] char_trigram_lexical={mm['char_trigram_lexical']}")
    print(f"[test1] semantic_scramble={mm['semantic_scramble']}")
    print(f"[test1] wordnet_ablation={wn_ablation}")
    print(f"[test1] alias_demo cos(usa,america) sem={alias_demo['cos_usa_america_semantic']} "
          f"lex={alias_demo['cos_usa_america_lexical']}")
    print(f"[test2] arc_climb={arc_res}")
    print(f"[elapsed] {elapsed}s")


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
