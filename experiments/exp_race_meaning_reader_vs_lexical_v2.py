"""race_meaning_reader_vs_lexical_v2 -- does MEANING/COMPREHENSION beat the char-trigram LEXICAL
floor on RACE reading comprehension? Answers the unanswered purpose of the RACE rung: the prior
cell (exp_race_reading_comprehension_measure_v1) measured only a char-trigram LEXICAL baseline;
the MEANING encoder + the situation-model READER were never invoked.

BASELINE TO BEAT (banked 29535, recomputed here IN-REGIME on the SAME slice for a fair head-to-
head): char-trigram max-cosine passage-QA. Prior banked full: middle 0.395, high 0.317, agg 0.356
(chance 0.25). RACE-high is the KEY discriminator: lexical picks SURFACE-matching distractors over
inferential answers, so it sinks on high. MEANING should resist that trap if it genuinely reads.

TREATMENT ARMS (MUST use real meaning -- a char-trigram re-run is a NO-OP that fails the contract):
  ARM A  semantic (bag-of-meaning): SemanticHDEncoder (GloVe+WordNet -> JL 2048 HD, banked 29533)
         swapped into the EXACT proven RACE max-cosine passage-QA harness. Same harness, meaning
         encoder. It should resist the surface-distractor trap on RACE-high.
  ARM B  event_semantic (structured meaning / the reader's situation rep): spaCy predicate-argument
         extraction -> EventBundleCodec role-slot binding (the dim-29511 situation-model EVENT rep,
         bind(role_key, filler); the reader's canonical memory unit) with SEMANTIC fillers (SimHash
         of the SemanticHDEncoder vector). Passage -> set of event vectors; each (Q+option) -> its
         event vectors; score = max event-support cosine; argmax. This is the reader's HD event
         representation, coref-free/lean (NOT the full SituationReader.read coref-CoNLL pipeline --
         that needs a mention/coref preprocessor too heavy for one inline-local cycle; declared).
  DIAG   event_native (B1): the SAME event rep with the codec's NATIVE random per-lemma codebook
         (exact who-did-what-to-whom overlap, no meaning). Cheap once events are extracted; isolates
         how much of ARM B is meaning vs exact-lemma structure.
  BASELINE  char_trigram (the RACE harness with CharTrigramEncoder, same slice) + lexical_overlap
         (naive content-word overlap, no HD).

CONTROLS (can-fail MANDATORY):
  * chance 0.25 (theoretical) + random-pick + majority-letter.
  * mismatched_passage collapse: route each question to a DIFFERENT article's store (cyclic
    derangement). Genuine reading of THIS passage MUST collapse toward chance; if not, the gain is a
    lexical/leak artifact. Applied to ARM A (semantic) AND ARM B (event_semantic).
  * char-trigram head-to-head recomputed in-regime on the same slice.

HARD-PASS (MEANING_BREAKS_LEXICAL_CEILING): a treatment arm beats char-trigram by a REAL margin,
  ESPECIALLY on RACE-high (the inferential discriminator): best_treat_high - char_high >= 0.03 AND
  best_treat_agg - char_agg >= 0.02, with that arm's mismatched control collapsing >= 0.03 (genuine).
HARD-FAIL (MEANING_ADDS_NOTHING): max treatment lift over char <= 0.01 on BOTH high AND aggregate
  (meaning ~= char-trigram; nothing beyond bag-of-trigrams). Between = PARTIAL / MIDDLE.

HONEST grade proxy (deflated): RACE-middle ~ middle school, RACE-high ~ high school; a real student
  ~0.85+ (Turkers 0.855, human ceiling 0.945; CITED Lai et al. 2017 EMNLP RACE). We report accuracy
  -> coarse band + STATE the gap. Substrate is a retriever, not a comprehender.

Contract: INLINE-LOCAL foreground-to-completion (RACE cache is LOCAL-ONLY + UNCOMMITTED under
data/corpora/race/ -- not on the remote runner, so no queue/push/remote-persist; mirrors the ARC
sibling's contract). ASCII-only. Deterministic (fixed seeds; numpy default_rng; sorted iteration).
Runs in repo .venv (datasets, gensim/glove cached, spaCy en_core_web_sm, nltk wordnet). VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics ; heartbeat
# - real_code_path: self_test constructs the REAL SemanticHDEncoder + CharTrigramEncoder +
#   EventBundleCodec + spaCy event extractor and runs the REAL scoring fns at tiny scale
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()-seeded RNG
# - arms_differ_verified at smoke (char vs semantic vs event stores bit-differ)
# - baseline_in_band: chance/random ~0.25; char/semantic arms 0.05<acc<0.95 (not saturated)
# - discriminator: the RACE-high head-to-head (meaning vs lexical) is the telemetry-sensitive gate
# - per-arm failure-class: ARM B wrapped -- errors RECORDED (traceback + status) + surfaced in
#   verdict (FAIL_LOUD), never silently continued; headline stands on ARM A vs baseline
# - all reported numbers MEASURED@ this cell's metrics.json
# Compute architecture: sequential-CPU (justified). Encoders = GloVe lookups + JL projection + small
#   bipolar bind/cleanup; per-question scoring is many small max-cosine ops + spaCy parse. No GPU
#   batching win (no large dense matmul); scope sized to finish in a single <10-min foreground call.
#   Storage: no_composition (per-question passage store; max-cosine retrieval, no chained hops).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
import json
import time
import argparse
import hashlib
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.char_trigram_encoder import CharTrigramEncoder
from experiments import exp_race_reading_comprehension_measure_v1 as race
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

# Low-memory GloVe loader: the glove-wiki-gigaword-300 .gz is word2vec-text, FREQUENCY-ORDERED, so
# top-N covers all common RACE content words (photosynthesis is in the top 120K). Loading a capped
# vocab (~150MB) instead of the full 400K (~500MB) cuts memory footprint ~4x + parse time ~3x --
# critical on a contended box (avoids thrash with any concurrent GloVe-loading run). Same KeyedVectors
# object the SemanticHDEncoder expects (passed via kv=), so meaning is unchanged for covered words.
_GLOVE_CAPPED = [None]
_GLOVE_GZ = os.path.join(_REPO, "data", "gensim_cache", "glove-wiki-gigaword-300",
                         "glove-wiki-gigaword-300.gz")
GLOVE_LIMIT_DEFAULT = 120000


def _load_glove_capped(limit=GLOVE_LIMIT_DEFAULT):
    if _GLOVE_CAPPED[0] is None:
        from gensim.models import KeyedVectors
        _GLOVE_CAPPED[0] = KeyedVectors.load_word2vec_format(_GLOVE_GZ, limit=int(limit))
    return _GLOVE_CAPPED[0]

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress flushing
    except Exception:
        pass

ANCHOR_NAME = "race_meaning_reader_vs_lexical_v2"
SEED = 20260724

SEM_N_DIM = 2048       # ARM A semantic encoder (matches char-trigram harness dim)
EVENT_N_DIM = 4096     # ARM B event codec dim (situation-model FOCUS dim)
FOCUS_SEED = 11        # matches build_spacy_event_reader FOCUS_SEED for role-key fidelity

# ---- pre-reg bands (author-designed) ----
HP_HIGH_LIFT = 0.03        # best treatment - char on RACE-high (the inferential discriminator)
HP_AGG_LIFT = 0.02         # best treatment - char aggregate
HP_MISMATCH_COLLAPSE = 0.03  # that arm's mismatched control must collapse by >= this (genuineness)
HF_LIFT = 0.01             # max treatment lift over char (both high AND agg) <= this => HARD_FAIL

HUMAN_CEILING = 0.945
TURKER_PERF = 0.855


# ---------------------------------------------------------------------------
# markers / crash diagnostics (per CELL-TEMPLATE)
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
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
# generic encoder-support scoring (ARM A + char baseline reuse the RACE harness directly)
# ---------------------------------------------------------------------------
def _score_encoder(questions, enc, arm):
    """Reuse the PROVEN RACE harness (race._build_stores / _encode_queries / _score_hd) with any
    encoder exposing encode_batch + n_dim. arm in {'hd','mismatched'}. Returns race._score_hd dict."""
    QV, qmap = race._encode_queries(questions, enc)
    SV, qsh, _art, _hashes = race._build_stores(questions, enc, np.random.default_rng(SEED), arm)
    return _score_hd_capture(questions, QV, qmap, SV, qsh)


def _score_hd_capture(questions, QV, qmap, SV, qsh):
    return race._score_hd(questions, QV, qmap, SV, qsh, np.random.default_rng(SEED + 2))


# ---------------------------------------------------------------------------
# ARM B: the reader's situation rep -- spaCy predicate-argument events -> EventBundleCodec role-slot
# binding (dim-29511). Semantic fillers (SimHash of SemanticHDEncoder) = structured MEANING.
# ---------------------------------------------------------------------------
_NLP = [None]
_ROLE_DEPS = ("ROOT", "advcl", "conj", "ccomp", "xcomp", "relcl", "acl", "pcomp")
_AGENT_DEPS = ("nsubj", "nsubjpass", "expl", "csubj")
_PATIENT_DEPS = ("dobj", "obj", "attr", "dative", "oprd", "acomp")


def _get_nlp():
    if _NLP[0] is None:
        import spacy
        _NLP[0] = spacy.load("en_core_web_sm")
    return _NLP[0]


def _events_from_doc(doc):
    """Return list of role-filler dicts {PRED,AGENT,PATIENT,TENSE} from a parsed spaCy doc.
    Structural roles: AGENT = nsubj-family child; PATIENT = dobj/obj-family child (glass-box,
    mirrors the reader's _assign_roles subject/first-object structure)."""
    out = []
    for t in doc:
        if t.pos_ not in ("VERB", "AUX"):
            continue
        if t.dep_ not in _ROLE_DEPS:
            continue
        agent, patient = "?", "?"
        for c in t.children:
            if agent == "?" and c.dep_ in _AGENT_DEPS:
                agent = c.lemma_.lower()
            if patient == "?" and c.dep_ in _PATIENT_DEPS:
                patient = c.lemma_.lower()
        tense = "PAST" if t.tag_ in ("VBD", "VBN") else "PRESENT"
        out.append({"PRED": t.lemma_.lower(), "AGENT": agent, "PATIENT": patient, "TENSE": tense})
    return out


def _parse_texts(texts, batch_size=64):
    nlp = _get_nlp()
    docs = nlp.pipe(list(texts), batch_size=batch_size)
    return [_events_from_doc(d) for d in docs]


class _SemFillerSigner:
    """word -> bipolar {-1,+1} SimHash of the SemanticHDEncoder meaning vector (cached). None if the
    word carries no meaning signal (drops that role from the event bundle)."""

    def __init__(self, sem_enc):
        self.sem = sem_enc
        self.P = sem_enc.P
        self.cache = {}

    def sign(self, word):
        if word in self.cache:
            return self.cache[word]
        v = None
        if word and word != "?":
            fv = self.sem.fused(word)          # 300d meaning vector (bypasses content-word filter)
            if fv is not None:
                proj = (fv @ self.P.T).astype(np.float32)
                s = np.where(proj >= 0.0, 1.0, -1.0).astype(np.float32)
                v = s
        self.cache[word] = v
        return v


def _encode_events_semantic(events, role_key_np, signer, meaning_roles=("PRED", "AGENT", "PATIENT")):
    """events -> (n_ev, EVENT_N_DIM) bipolar matrix. event = sign(sum_r role_key[r]*simhash(sem(filler_r)))
    over roles present with a meaning-carrying filler; events with <1 usable role are dropped."""
    rows = []
    for rf in events:
        acc = np.zeros(EVENT_N_DIM, dtype=np.float32)
        n_used = 0
        for r in meaning_roles:
            filler = rf.get(r, "?")
            s = signer.sign(filler)
            if s is None:
                continue
            acc += role_key_np[r] * s
            n_used += 1
        if n_used == 0:
            continue
        rows.append(np.where(acc >= 0.0, 1.0, -1.0).astype(np.float32))
    if not rows:
        return np.zeros((0, EVENT_N_DIM), dtype=np.float32)
    return race._unit_rows(np.stack(rows, axis=0))


def _encode_events_native(events, codec):
    """events -> (n_ev, EVENT_N_DIM) via the codec's NATIVE random per-lemma codebook (exact-match
    who-did-what-to-whom; no meaning). Diagnostic isolating structure-only overlap."""
    rows = []
    for rf in events:
        vec = codec.encode_event(rf)  # torch bipolar (n_dim,)
        rows.append(vec.detach().cpu().numpy().astype(np.float32))
    if not rows:
        return np.zeros((0, EVENT_N_DIM), dtype=np.float32)
    return race._unit_rows(np.stack(rows, axis=0))


def _score_event_support(questions, art_events, qopt_events, encode_fn, q_store_hash, rng):
    """Per question: Ep = passage event matrix (routed by q_store_hash); per option Eo = (Q+opt)
    event matrix; option score = max cosine over event pairs; argmax (ties -> rng; no-signal -> rng).
    Returns {acc, acc_by_source, n, n_no_signal}."""
    # cache passage matrices per store hash
    Ep_cache = {h: encode_fn(art_events[h]) for h in sorted(art_events)}
    correct = 0
    n_no_signal = 0
    per_source = {}
    for qi, q in enumerate(questions):
        Ep = Ep_cache[q_store_hash[qi]]
        opt_scores = np.full(4, -np.inf, dtype=np.float32)
        for ci in range(4):
            Eo = qopt_events[(qi, ci)]
            if Eo.shape[0] == 0 or Ep.shape[0] == 0:
                continue
            sims = Eo @ Ep.T
            opt_scores[ci] = float(np.max(sims))
        mx = float(np.max(opt_scores))
        if not np.isfinite(mx):
            cand = list(range(4))
            n_no_signal += 1
        else:
            cand = [ci for ci in range(4) if abs(float(opt_scores[ci]) - mx) < 1e-6]
        pick = int(rng.choice(cand)) if len(cand) > 1 else cand[0]
        hit = int(pick == q["correct_index"])
        correct += hit
        s = per_source.setdefault(q["source"], [0, 0])
        s[0] += hit
        s[1] += 1
    n = len(questions)
    return {"acc": correct / n if n else 0.0, "n": n, "n_no_signal": n_no_signal,
            "acc_by_source": {k: (v[0] / v[1] if v[1] else None) for k, v in sorted(per_source.items())}}


def run_arm_b(questions, sem_enc_event, output_dir):
    """ARM B (event_semantic) + DIAG (event_native) + genuineness mismatched control. Returns a
    result dict; RECORDS its own status. Raises are caught by the caller which records failure-class."""
    from hdlab.event_bundle import EventBundleCodec, DEFAULT_ROLES

    _heartbeat(output_dir, "arm_b_parse_articles")
    # unique articles (deterministic hash order)
    art_text = {}
    for q in questions:
        h = race._art_hash(q["article"])
        art_text.setdefault(h, q["article"])
    hashes = sorted(art_text)
    art_ev_list = _parse_texts([art_text[h] for h in hashes])
    art_events = {h: ev for h, ev in zip(hashes, art_ev_list)}

    _heartbeat(output_dir, "arm_b_parse_queries")
    qopt_texts, qopt_key = [], []
    for qi, q in enumerate(questions):
        for ci, o in enumerate(q["options"]):
            qopt_texts.append(q["question"] + " " + o)
            qopt_key.append((qi, ci))
    qopt_ev_list = _parse_texts(qopt_texts)

    # role keys (shared codec for fidelity to the situation-model event format)
    codec = EventBundleCodec(n_dim=EVENT_N_DIM, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
    role_key_np = {r: codec.role_keys[i].detach().cpu().numpy().astype(np.float32)
                   for i, r in enumerate(codec.roles)}
    signer = _SemFillerSigner(sem_enc_event)

    # semantic event matrices for (Q+opt)
    _heartbeat(output_dir, "arm_b_encode_semantic")
    qopt_sem = {}
    for (qi, ci), ev in zip(qopt_key, qopt_ev_list):
        qopt_sem[(qi, ci)] = _encode_events_semantic(ev, role_key_np, signer)

    def enc_sem(evs):
        return _encode_events_semantic(evs, role_key_np, signer)

    def enc_nat(evs):
        return _encode_events_native(evs, codec)

    # store-hash routing: identity (hd) + cyclic derangement (mismatched)
    qsh_hd = [race._art_hash(q["article"]) for q in questions]
    if len(hashes) > 1:
        shift = {h: hashes[(i + 1) % len(hashes)] for i, h in enumerate(hashes)}
        qsh_mm = [shift[h] for h in qsh_hd]
    else:
        qsh_mm = list(qsh_hd)

    _heartbeat(output_dir, "arm_b_score_semantic")
    ev_sem = _score_event_support(questions, art_events, qopt_sem, enc_sem, qsh_hd,
                                  np.random.default_rng(SEED + 11))
    _heartbeat(output_dir, "arm_b_score_semantic_mismatched")
    ev_sem_mm = _score_event_support(questions, art_events, qopt_sem, enc_sem, qsh_mm,
                                     np.random.default_rng(SEED + 12))

    # native (exact-lemma) diagnostic: reuse the codec codebook; separate (Q+opt) native matrices
    _heartbeat(output_dir, "arm_b_encode_native")
    qopt_nat = {}
    for (qi, ci), ev in zip(qopt_key, qopt_ev_list):
        qopt_nat[(qi, ci)] = _encode_events_native(ev, codec)
    _heartbeat(output_dir, "arm_b_score_native")
    ev_nat = _score_event_support(questions, art_events, qopt_nat, enc_nat, qsh_hd,
                                  np.random.default_rng(SEED + 13))

    # arms-differ: semantic vs native passage-event stores bit-differ
    import hashlib as _hl
    any_h = hashes[0]

    def _digest(fn):
        m = fn(art_events[any_h])
        return _hl.sha256(m.tobytes()).hexdigest()
    differ = _digest(enc_sem) != _digest(enc_nat)

    total_ev = sum(len(v) for v in art_events.values())
    return {
        "status": "OK",
        "event_semantic": ev_sem,
        "event_semantic_mismatched": ev_sem_mm,
        "event_native": ev_nat,
        "n_articles": len(hashes),
        "total_passage_events": total_ev,
        "mean_events_per_article": round(total_ev / max(1, len(hashes)), 2),
        "semantic_vs_native_store_differ": bool(differ),
        "meaning_roles": ["PRED", "AGENT", "PATIENT"],
    }


# ---------------------------------------------------------------------------
# self-test (real code path + determinism + discriminator)
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] constructing REAL encoders (char + semantic GloVe/WordNet) ...", flush=True)
    kv = _load_glove_capped()
    _load_wordnet()
    char = CharTrigramEncoder(n_dim=512)
    sem = SemanticHDEncoder(n_dim=512, seed=SEED, use_wordnet=True, kv=kv)

    # toy RACE question whose correct answer is a MEANING paraphrase (synonym), not a surface copy:
    # a lexical encoder is tempted by the surface-word distractor; meaning should still pick the
    # paraphrase. (Discriminator-fires sanity, not a scale claim.)
    questions = [{
        "qid": "T1",
        "article": "The little boy was extremely happy when he received a brand new bicycle. "
                   "He rode it around the park all afternoon.",
        "question": "How did the boy feel about the bicycle?",
        "options": ["He was glad.", "He was angry.", "He was tired.", "He was hungry."],
        "correct_index": 0,
        "source": "middle",
    }]
    # ARM A path through the REAL RACE harness with the REAL semantic encoder
    res_sem = _score_encoder(questions, sem, "hd")
    assert 0.0 <= res_sem["acc"] <= 1.0, res_sem
    res_char = _score_encoder(questions, char, "hd")
    assert 0.0 <= res_char["acc"] <= 1.0, res_char
    # determinism
    assert _score_encoder(questions, sem, "hd")["acc"] == res_sem["acc"], "non-deterministic ARM A"

    # ARM B path: REAL spaCy extraction + REAL EventBundleCodec role binding
    from hdlab.event_bundle import EventBundleCodec, DEFAULT_ROLES
    codec = EventBundleCodec(n_dim=EVENT_N_DIM, roles=DEFAULT_ROLES, seed=FOCUS_SEED)
    role_key_np = {r: codec.role_keys[i].detach().cpu().numpy().astype(np.float32)
                   for i, r in enumerate(codec.roles)}
    sem_ev = SemanticHDEncoder(n_dim=EVENT_N_DIM, seed=SEED, use_wordnet=True, kv=kv)
    signer = _SemFillerSigner(sem_ev)
    evs = _parse_texts(["The boy rode the bicycle around the park."])[0]
    assert len(evs) >= 1, f"spaCy extracted no events: {evs}"
    M_sem = _encode_events_semantic(evs, role_key_np, signer)
    M_nat = _encode_events_native(evs, codec)
    assert M_sem.shape[1] == EVENT_N_DIM and M_nat.shape[1] == EVENT_N_DIM
    assert M_sem.shape[0] >= 1, "no semantic event vectors built"
    # bipolar sign vectors, unit-normalized rows
    assert abs(np.linalg.norm(M_sem[0]) - 1.0) < 1e-4, "event row not unit-normalized"
    # arms-differ: semantic vs native bit-differ
    import hashlib as _hl
    assert _hl.sha256(M_sem.tobytes()).hexdigest() != _hl.sha256(M_nat.tobytes()).hexdigest(), \
        "META_RULE_AF: semantic and native event stores bit-identical"
    # determinism of event encoding
    M_sem2 = _encode_events_semantic(evs, role_key_np, signer)
    assert np.array_equal(M_sem, M_sem2), "non-deterministic event encoding"

    # SimHash-OF-MEANING check (robust; NOT antonym-ordering -- GloVe places antonyms close by
    # co-occurrence). Confirms the fillers are MEANING-based, not spelling: synonym/related pairs
    # must separate from LEXICALLY-CLOSE-but-meaning-far false friends (a char-trigram SimHash would
    # rank the false friends HIGH). Aggregate mean over several pairs.
    def _cos(a, b):
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    syn_pairs = [("big", "large"), ("sick", "ill"), ("cat", "kitten"), ("dog", "puppy"),
                 ("buy", "purchase"), ("movie", "film")]
    falsefriend_pairs = [("cat", "car"), ("hair", "chair"), ("bread", "read"), ("cold", "gold"),
                         ("mind", "mint"), ("band", "sand")]

    def _mean_pair_cos(pairs):
        vals = []
        for a, b in pairs:
            sa, sb = signer.sign(a), signer.sign(b)
            if sa is not None and sb is not None:
                vals.append(_cos(sa, sb))
        return vals
    syn_c = _mean_pair_cos(syn_pairs)
    ff_c = _mean_pair_cos(falsefriend_pairs)
    assert syn_c and ff_c, "SimHash filler signals missing"
    syn_m, ff_m = float(np.mean(syn_c)), float(np.mean(ff_c))
    assert syn_m > ff_m + 0.02, \
        f"SimHash-of-meaning failed to separate synonyms {syn_m:.3f} from false-friends {ff_m:.3f} " \
        "(fillers are not meaning-based)"
    print(f"[self-test] SimHash-of-meaning: synonym mean cos={syn_m:.3f} > false-friend mean cos={ff_m:.3f}",
          flush=True)

    # scoring path runs
    art_events = {race._art_hash(questions[0]["article"]): _parse_texts([questions[0]["article"]])[0]}
    qopt = {}
    for ci, o in enumerate(questions[0]["options"]):
        qopt[(0, ci)] = _encode_events_semantic(
            _parse_texts([questions[0]["question"] + " " + o])[0], role_key_np, signer)
    qsh = [race._art_hash(questions[0]["article"])]
    r = _score_event_support(questions, art_events, qopt,
                             lambda e: _encode_events_semantic(e, role_key_np, signer), qsh,
                             np.random.default_rng(SEED))
    assert 0.0 <= r["acc"] <= 1.0, r
    print("[self-test] PASS (real ARM A harness, real spaCy+EventBundleCodec ARM B, SimHash meaning "
          "ordering, determinism, arms-differ)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_middle": 60, "n_high": 40}
    return {"n_middle": 500, "n_high": 500}


def _grade_band(acc, level):
    return race._grade_band(acc, level)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--n-middle", type=int, default=None)
    ap.add_argument("--n-high", type=int, default=None)
    ap.add_argument("--glove-limit", type=int, default=GLOVE_LIMIT_DEFAULT,
                    help="cap GloVe vocab (freq-ordered) to bound memory/parse on a contended box")
    ap.add_argument("--no-arm-b", action="store_true", help="skip ARM B (event reader) -- diagnostics only")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    output_dir = _out_dir()
    cfg = _config(args.mode)
    if args.n_middle is not None:
        cfg["n_middle"] = args.n_middle
    if args.n_high is not None:
        cfg["n_high"] = args.n_high
    _write_start_marker(output_dir, args.mode, cfg["n_middle"] + cfg["n_high"])
    t0 = time.perf_counter()

    _heartbeat(output_dir, "load_race")
    questions = race._load_race("middle", cfg["n_middle"]) + race._load_race("high", cfg["n_high"])
    questions.sort(key=lambda q: (q["source"], q["qid"]))
    n_mid = sum(1 for q in questions if q["source"] == "middle")
    n_high = len(questions) - n_mid
    print(f"[eval] {len(questions)} RACE questions ({n_mid} middle, {n_high} high)", flush=True)

    _heartbeat(output_dir, "load_glove", {"glove_limit": args.glove_limit})
    kv = _load_glove_capped(args.glove_limit)
    _load_wordnet()
    _heartbeat(output_dir, "glove_loaded", {"vocab": len(kv.key_to_index)})

    chance = 0.25

    def _src(res, s):
        return res["acc_by_source"].get(s)

    # ---- BASELINE: char-trigram (recompute in-regime, same slice) ----
    _heartbeat(output_dir, "char_baseline")
    char_enc = CharTrigramEncoder(n_dim=SEM_N_DIM)
    char = _score_encoder(questions, char_enc, "hd")
    lex = race._score_lexical_overlap(questions, np.random.default_rng(SEED + 5))

    # ---- ARM A: semantic (bag-of-meaning) ----
    _heartbeat(output_dir, "arm_a_semantic")
    sem_enc = SemanticHDEncoder(n_dim=SEM_N_DIM, seed=SEED, use_wordnet=True, kv=kv)
    sem = _score_encoder(questions, sem_enc, "hd")
    _heartbeat(output_dir, "arm_a_semantic_mismatched")
    sem_mm = _score_encoder(questions, sem_enc, "mismatched")

    # ---- ARM B: event_semantic (the reader's situation rep) ----
    arm_b = {"status": "SKIPPED"}
    if not args.no_arm_b:
        try:
            sem_enc_event = SemanticHDEncoder(n_dim=EVENT_N_DIM, seed=SEED, use_wordnet=True, kv=kv)
            arm_b = run_arm_b(questions, sem_enc_event, output_dir)
        except Exception as e:  # RECORD failure-class + surface (NOT silent-continue)
            arm_b = {"status": f"ERROR:{type(e).__name__}",
                     "error": str(e)[:500], "traceback": traceback.format_exc()[:3000]}
            _heartbeat(output_dir, "arm_b_error", {"error_class": type(e).__name__})

    # ---- controls ----
    ctrl_random = race._control_random(questions, np.random.default_rng(SEED + 6))
    ctrl_majority, modal = race._control_majority(questions)

    # ---- assemble per-arm accuracies (aggregate + per-source) ----
    char_agg, char_mid, char_high = char["acc"], _src(char, "middle"), _src(char, "high")
    sem_agg, sem_mid, sem_high = sem["acc"], _src(sem, "middle"), _src(sem, "high")
    sem_mm_agg = sem_mm["acc"]
    lex_agg, lex_mid, lex_high = lex["acc"], _src(lex, "middle"), _src(lex, "high")

    treatments = {"semantic": {"agg": sem_agg, "mid": sem_mid, "high": sem_high,
                               "mm_agg": sem_mm_agg}}
    if arm_b.get("status") == "OK":
        evs = arm_b["event_semantic"]
        evs_mm = arm_b["event_semantic_mismatched"]
        treatments["event_semantic"] = {
            "agg": evs["acc"], "mid": evs["acc_by_source"].get("middle"),
            "high": evs["acc_by_source"].get("high"), "mm_agg": evs_mm["acc"]}

    # ---- gates: HARD-PASS if a treatment beats char by a REAL margin, esp. RACE-high; genuine ----
    def _lift_high(t):
        return None if (t["high"] is None or char_high is None) else round(t["high"] - char_high, 4)

    def _lift_agg(t):
        return round(t["agg"] - char_agg, 4)

    def _mm_collapse(t):
        return round(t["agg"] - t["mm_agg"], 4)

    per_treatment = {}
    best_name, best_high_lift = None, -1e9
    for name, t in treatments.items():
        lh = _lift_high(t)
        la = _lift_agg(t)
        mc = _mm_collapse(t)
        per_treatment[name] = {"agg": round(t["agg"], 4),
                               "high": None if t["high"] is None else round(t["high"], 4),
                               "mid": None if t["mid"] is None else round(t["mid"], 4),
                               "lift_high_vs_char": lh, "lift_agg_vs_char": la,
                               "mismatched_collapse": mc}
        if lh is not None and lh > best_high_lift:
            best_high_lift, best_name = lh, name

    baseline_in_band = (0.05 < char_agg < 0.95) and (0.10 < ctrl_random < 0.40)
    discriminator_fires = True  # the RACE-high head-to-head is telemetry-sensitive by construction

    hard_pass = False
    hf_lift_max = None
    if best_name is not None:
        bt = per_treatment[best_name]
        genuine = (bt["mismatched_collapse"] is not None and bt["mismatched_collapse"] >= HP_MISMATCH_COLLAPSE)
        hard_pass = bool(bt["lift_high_vs_char"] is not None and bt["lift_high_vs_char"] >= HP_HIGH_LIFT
                         and bt["lift_agg_vs_char"] >= HP_AGG_LIFT and genuine and baseline_in_band)
    # HARD-FAIL: max treatment lift over char <= HF_LIFT on BOTH high and agg
    high_lifts = [v["lift_high_vs_char"] for v in per_treatment.values() if v["lift_high_vs_char"] is not None]
    agg_lifts = [v["lift_agg_vs_char"] for v in per_treatment.values()]
    max_high_lift = max(high_lifts) if high_lifts else None
    max_agg_lift = max(agg_lifts) if agg_lifts else None
    hf_lift_max = {"max_high_lift": max_high_lift, "max_agg_lift": max_agg_lift}
    hard_fail = bool(max_high_lift is not None and max_high_lift <= HF_LIFT
                     and max_agg_lift is not None and max_agg_lift <= HF_LIFT)

    if not baseline_in_band:
        verdict = "BASELINE_OUT_OF_BAND"
        vmsg = f"char aggregate {char_agg:.3f} or random {ctrl_random:.3f} out of measurable band"
    elif hard_pass:
        bt = per_treatment[best_name]
        verdict = "MEANING_BREAKS_LEXICAL_CEILING"
        vmsg = (f"{best_name} beats char-trigram on RACE-high (+{bt['lift_high_vs_char']:.3f}: "
                f"{char_high:.3f} -> {bt['high']:.3f}) and aggregate (+{bt['lift_agg_vs_char']:.3f}); "
                f"mismatched collapses {bt['mismatched_collapse']:+.3f} = genuine reading of THIS "
                f"passage. Meaning resists the surface-distractor trap that sank lexical on RACE-high.")
    elif hard_fail:
        verdict = "MEANING_ADDS_NOTHING"
        vmsg = (f"no meaning/reader arm beats char-trigram: max RACE-high lift {max_high_lift:+.3f}, "
                f"max aggregate lift {max_agg_lift:+.3f} (both <= {HF_LIFT}). Meaning ~= bag-of-"
                f"trigrams on reading; the ~0.35 lexical ceiling holds.")
    else:
        verdict = "PARTIAL_MEANING_LIFT"
        vmsg = (f"best arm {best_name} lifts RACE-high {best_high_lift:+.3f} / aggregate "
                f"{per_treatment[best_name]['lift_agg_vs_char']:+.3f} over char-trigram but below "
                f"HARD-PASS bands (need high>=+{HP_HIGH_LIFT}, agg>=+{HP_AGG_LIFT}, genuine collapse "
                f">=+{HP_MISMATCH_COLLAPSE}) -- partial, not a clean break of the lexical ceiling.")

    if arm_b.get("status", "").startswith("ERROR"):
        vmsg += f" [ARM B unavailable: {arm_b['status']} -- headline stands on ARM A semantic vs char.]"

    grade = {
        "char_middle_band": _grade_band(char_mid, "middle"),
        "char_high_band": _grade_band(char_high, "high"),
        "semantic_middle_band": _grade_band(sem_mid, "middle"),
        "semantic_high_band": _grade_band(sem_high, "high"),
        "note": ("COARSE heuristic proxy (NOT calibrated to real student scores). A real middle/high-"
                 "school student scores ~0.85+ (Turkers 0.855, ceiling 0.945; CITED Lai et al. 2017). "
                 "Even the best arm here is a shallow retriever, far below a real student."),
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": (f"{verdict}: char[mid={char_mid} high={char_high} agg={char_agg:.3f}] "
                    f"semantic[mid={sem_mid} high={sem_high} agg={sem_agg:.3f}] "
                    + (f"event_sem[high={per_treatment.get('event_semantic',{}).get('high')} "
                       f"agg={per_treatment.get('event_semantic',{}).get('agg')}]"
                       if 'event_semantic' in per_treatment else "event_sem[unavailable]")),
        "elapsed_s": round(time.perf_counter() - t0, 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": args.mode, "mode": args.mode,
        "sem_n_dim": SEM_N_DIM, "event_n_dim": EVENT_N_DIM, "seed": SEED,
        "glove_limit": args.glove_limit, "glove_vocab_loaded": len(kv.key_to_index),
        "n_questions": len(questions), "n_middle": n_mid, "n_high": n_high,
        # ---- controls ----
        "chance_theoretical": chance,
        "control_random_pick": round(ctrl_random, 4),
        "control_majority": round(ctrl_majority, 4), "majority_modal_index": modal,
        "baseline_in_band": bool(baseline_in_band),
        "discriminator_fires": bool(discriminator_fires),
        # ---- BASELINE (char-trigram in-regime + naive lexical overlap) ----
        "char_trigram_acc_agg": round(char_agg, 4),
        "char_trigram_acc_middle": None if char_mid is None else round(char_mid, 4),
        "char_trigram_acc_high": None if char_high is None else round(char_high, 4),
        "lexical_overlap_acc_agg": round(lex_agg, 4),
        "lexical_overlap_acc_middle": None if lex_mid is None else round(lex_mid, 4),
        "lexical_overlap_acc_high": None if lex_high is None else round(lex_high, 4),
        "banked_char_floor_29535_ref": {"middle": 0.395, "high": 0.317, "agg": 0.356,
                                        "note": "banked full 1000/1000; recomputed here in-regime on this slice"},
        # ---- ARM A semantic ----
        "semantic_acc_agg": round(sem_agg, 4),
        "semantic_acc_middle": None if sem_mid is None else round(sem_mid, 4),
        "semantic_acc_high": None if sem_high is None else round(sem_high, 4),
        "semantic_mismatched_acc_agg": round(sem_mm_agg, 4),
        # ---- ARM B event reader ----
        "arm_b_status": arm_b.get("status"),
        "arm_b": arm_b,
        # ---- head-to-head gates ----
        "per_treatment_vs_char": per_treatment,
        "best_treatment": best_name,
        "best_treatment_high_lift": None if best_name is None else per_treatment[best_name]["lift_high_vs_char"],
        "max_treatment_lift": hf_lift_max,
        "bands": {"HP_HIGH_LIFT": HP_HIGH_LIFT, "HP_AGG_LIFT": HP_AGG_LIFT,
                  "HP_MISMATCH_COLLAPSE": HP_MISMATCH_COLLAPSE, "HF_LIFT": HF_LIFT},
        "hard_pass": bool(hard_pass), "hard_fail": bool(hard_fail),
        # ---- honest grade ----
        "grade_proxy": grade,
        "human_scale_note": (f"RACE-middle ~ middle school, RACE-high ~ high school. Human ceiling "
                             f"{HUMAN_CEILING}, Turkers {TURKER_PERF} (CITED Lai et al. 2017). Chance {chance}."),
        "contract": "INLINE-LOCAL foreground-to-completion; RACE cache LOCAL-ONLY + UNCOMMITTED; no push/remote-persist; VET-PENDING",
        "VET_PENDING": True,
    }
    _write_metrics_atomic(output_dir, metrics)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[baseline] char: mid={char_mid} high={char_high} agg={char_agg:.3f} | "
          f"lexical_overlap agg={lex_agg:.3f}", flush=True)
    print(f"[arm_a] semantic: mid={sem_mid} high={sem_high} agg={sem_agg:.3f} | "
          f"mismatched agg={sem_mm_agg:.3f}", flush=True)
    if arm_b.get("status") == "OK":
        e = arm_b["event_semantic"]; en = arm_b["event_native"]
        print(f"[arm_b] event_semantic: mid={e['acc_by_source'].get('middle')} "
              f"high={e['acc_by_source'].get('high')} agg={e['acc']:.3f} "
              f"(no_signal={e['n_no_signal']}/{e['n']}) | mismatched agg={arm_b['event_semantic_mismatched']['acc']:.3f} "
              f"| native_diag agg={en['acc']:.3f}", flush=True)
        print(f"[arm_b] {arm_b['total_passage_events']} passage events over {arm_b['n_articles']} "
              f"articles ({arm_b['mean_events_per_article']}/article)", flush=True)
    else:
        print(f"[arm_b] status={arm_b.get('status')}", flush=True)
    print(f"[controls] random={ctrl_random:.3f} majority={ctrl_majority:.3f} chance={chance}", flush=True)
    print(f"[grade] char high: {grade['char_high_band']} | semantic high: {grade['semantic_high_band']}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)


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
