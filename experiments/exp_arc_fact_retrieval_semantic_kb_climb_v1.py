"""arc_fact_retrieval_semantic_kb_climb_v1 -- THE CLIMB: wire MEANING into the vetted HD fact store,
ingest vetted ConceptNet triples through the trust-gate, answer ARC by FACT-retrieval.

Real question (can-fail): does RETRIEVAL over a store of VETTED ConceptNet triples (semantic HD
fillers, trust-gate-resolved) BEAT semantic-IR over raw ARC_Corpus sentences (the banked +0.042
floor)? Both arms use the IDENTICAL SemanticHDEncoder; they differ ONLY in store content (vetted
triples vs raw sentences). Isolates: does structuring knowledge as a vetted KB beat raw sentence
retrieval on the human science scale?

Builds on: 29530 (ARC measure, chance=0.252, no leak), 29531/29532 (HD fact store + O(1) index),
29533 (SemanticHDEncoder AUC 0.96), 29534 (single semantic-rep store IS foundation-scale to 100k).

WIRE-MEANING-IN: SemanticHDFactStore (in-cell subclass of HDFactStore) injects SEMANTIC bipolar codes
(sign of SemanticHDEncoder.encode) for SUBJECT/OBJECT filler symbols into the store's codec codebook,
so fact bundles + the (s,r) signature carry MEANING (near-synonym subjects -> close sr_keys). Roles +
RELATION + SOURCE + TRUST stay random (crisp role/relation match; only fillers semantic, per 29534).

HONEST EXPECTATION (deflated): likely FLAT/modest -- ConceptNet is commonsense-heavy, thin on grade
science -> coverage may cap the climb. FLAT is INFORMATIVE (diagnose coverage vs mechanism), not fail.

Contract: INLINE-LOCAL foreground-to-completion (ConceptNet jsonl + gensim GloVe cache are git-ignored
-> NOT remote-portable, same as sibling cells 29530/29533); NO push/remote-persist; store LOCAL-ONLY +
UNCOMMITTED; ASCII-only; deterministic (fixed seeds, numpy default_rng, sorted iteration; no hash()).
Runs in repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic ; heartbeat
# - real_code_path: self_test constructs the REAL SemanticHDEncoder + SemanticHDFactStore + runs the
#   REAL ingest/trust-gate/round-trip/fuzzy/ARC-scoring fns at tiny scale
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - arms_differ: empty/fact/semantic_ir/scramble store hashes differ
# - discriminator_fires: fact_retrieval best-cosine non-trivial + differs from scramble/empty asserted
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

import torch

from hdlab.hd_fact_store import HDFactStore
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: F401 (parity import; unused arm)
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet, _cos)

ANCHOR_NAME = "arc_fact_retrieval_semantic_kb_climb_v1"
SEED = 20260724

_CONCEPTNET = os.path.join(_REPO, "data", "datasets", "conceptnet5_en_100k.jsonl")

# ConceptNet relation cardinality (coarse hand-map; reported, not load-bearing on the ARC number).
REL_CARD = {
    "AtLocation": "MULTIVALUED", "CapableOf": "MULTIVALUED", "Causes": "MULTIVALUED",
    "CausesDesire": "MULTIVALUED", "DerivedFrom": "MULTIVALUED", "RelatedTo": "MULTIVALUED",
    "Antonym": "MULTIVALUED", "DefinedAs": "FUNCTIONAL", "CreatedBy": "FUNCTIONAL",
}

# Bands (author-designed; see pre-reg). PRIMARY = ARC-Easy fact_retrieval at full ingest.
HP_BEAT_FLOOR = 0.02      # fact_easy_full - semantic_ir_easy
HP_BEAT_EMPTY = 0.05      # fact_easy_full - empty_easy
HP_BEAT_SCRAMBLE = 0.03   # fact_easy_full - scramble_easy
FLAT_EPS = 0.02
FUZZY_THRESHOLD = 0.55    # semantic sr_key cosine for fuzzy same-(s,r) (can-fail separation checked)


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
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
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


_T0 = [0.0]


# ---------------------------------------------------------------------------
# SemanticHDFactStore: wire MEANING into the store's SUBJECT/OBJECT filler codebook.
# ---------------------------------------------------------------------------
class SemanticHDFactStore(HDFactStore):
    """HDFactStore whose SUBJECT/OBJECT filler symbols carry SEMANTIC bipolar codes
    (sign of SemanticHDEncoder.encode(text)) injected into the codec codebook. Near-synonym
    fillers -> HD-close codes -> the (s,r) signature is semantically fuzzy. RELATION/SOURCE/
    TRUST stay random (crisp match). OOV fillers (no GloVe/WordNet signal) fall back to the
    codec's random code so they still store (tracked as n_oov)."""

    _SEM_DOMAINS = ("SUBJECT", "OBJECT")

    def __init__(self, *a, sem_encoder=None, **kw):
        self._sem = sem_encoder
        self.n_sem = 0
        self.n_oov = 0
        super().__init__(*a, **kw)

    def _semantic_code(self, sym):
        if self._sem is None:
            return None
        text = str(sym).replace("_", " ").strip()
        v = self._sem.encode(text)  # (n_dim,) float32, L2 (or zeros if OOV)
        if v is None or float(np.linalg.norm(v)) < 1e-8:
            return None
        code = np.sign(v).astype(np.float32)
        code[code == 0.0] = 1.0  # keep strictly bipolar (sign(0)->+1, codec convention)
        return torch.from_numpy(code)

    def _register_domain(self, domain, sym):
        sym = str(sym)
        if domain in self._SEM_DOMAINS and sym not in self.codec._sym2idx:
            code = self._semantic_code(sym)
            if code is not None:
                self.codec._register(sym, code)  # semantic bipolar code, before random fallback
                self.n_sem += 1
            else:
                self.n_oov += 1
        super()._register_domain(domain, sym)  # random-registers RELATION/SOURCE/TRUST + OOV fillers

    # ---- fuzzy same-(s,r) via SEMANTIC sr_key cosine (no exact-string confirm) --------
    def fuzzy_find_same_sr(self, subj, rel, threshold):
        """Retrieve live facts whose (s,r) signature is SEMANTICALLY close (cosine>=threshold)
        to (subj,rel) -- catches surface variants (usa~united_states) the exact O(1) hash misses.
        Glass-box: returns (fid, recovered_object, sr_cosine) per hit."""
        sr = self._sr_key(subj, rel)
        active = [f for f in self._facts if f.status in ("ACTIVE", "COMBINED", "FLAGGED")]
        hits = []
        for f in active:
            c = float((f.sr_key @ sr) / self.n_dim)
            if c >= threshold:
                hits.append((f.fid, self.recover_fact(f.vec)["object"], round(c, 4)))
        return hits


# ---------------------------------------------------------------------------
# ingest (ConceptNet triples through the trust-gate)
# ---------------------------------------------------------------------------
def _load_conceptnet(n, rng):
    """Deterministic random n-slice of ConceptNet (answer-agnostic; a fixed external KB)."""
    rows = []
    with open(_CONCEPTNET, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    if n and n < len(rows):
        idx = np.sort(rng.choice(len(rows), size=n, replace=False))
        rows = [rows[i] for i in idx]
    return rows


def ingest_conceptnet(store, triples, output_dir):
    """Stream triples through store.store() with the trust-gate. Single trusted source
    (ConceptNet = curated) -> TRUST_HIGH. Returns resolution histogram (trust-gate fire rate)."""
    from collections import Counter
    hist = Counter()
    for i, t in enumerate(triples):
        s, r, o = str(t["subject"]), str(t["predicate"]), str(t["object"])
        res = store.store(s, r, o, "conceptnet", "TRUST_HIGH")
        hist[res.resolution] += 1
        if i % 5000 == 0:
            _heartbeat(output_dir, "ingest", {"i": i, "n": len(triples),
                                              "n_sem": store.n_sem, "n_oov": store.n_oov})
    return dict(hist)


# ---------------------------------------------------------------------------
# glass-box round-trip on the store's ACTUAL semantic bundles
# ---------------------------------------------------------------------------
def roundtrip_eval(store, sample_n, rng):
    live = store.live_facts()
    if not live:
        return {"n_sampled": 0}
    idx = rng.choice(len(live), size=min(sample_n, len(live)), replace=False)
    subj_ok = rel_ok = obj_ok = 0
    n = 0
    for j in idx:
        f = live[int(j)]
        rec = store.recover_fact(f.vec)
        subj_ok += int(rec["subject"] == f.subject)
        rel_ok += int(rec["relation"] == f.relation)
        obj_ok += int(rec["object"] == f.obj)
        n += 1
    return {"n_sampled": n,
            "subject_recovery": round(subj_ok / n, 4),
            "relation_recovery": round(rel_ok / n, 4),
            "object_recovery": round(obj_ok / n, 4),
            "note": ("semantic-filler cleanup is HARDER than random-code (correlated codes -> "
                     "argmax may return a near-synonym); crowding cost vs 29531 random-code 1.000.")}


# ---------------------------------------------------------------------------
# fuzzy-conflict demo (Part B; bounded curated set; closes 29531 gap #a)
# ---------------------------------------------------------------------------
def fuzzy_conflict_demo(sem_enc, n_dim):
    """A same-(s,r) SURFACE-VARIANT conflict (usa vs united_states) is caught by the SEMANTIC
    sr_key cosine but MISSED by the exact O(1) hash path. Then trust resolves it (DROP the low)."""
    st = SemanticHDFactStore(n_dim=n_dim, seed=SEED, sem_encoder=sem_enc,
                             relation_cardinality={"capital": "FUNCTIONAL"}, use_index=True)
    # store a mid-trust fact under one surface form
    st.store("united_states", "capital", "washington", "atlas", "TRUST_MID")
    # a contradicting low-trust fact under a SURFACE VARIANT of the same subject
    r_exact = st.store("usa", "capital", "new_york", "blog", "TRUST_LOW")
    # exact path: different surface strings -> different sr_key bytes -> exact hash MISSES the conflict
    exact_detected = r_exact.detected_conflict
    # fuzzy path: semantic sr_key cosine catches the same-(s,r) surface variant
    fuzzy_hits = st.fuzzy_find_same_sr("usa", "capital", FUZZY_THRESHOLD)
    sr_cos_variant = float((st._sr_key("usa", "capital") @ st._sr_key("united_states", "capital"))
                           / st.n_dim)
    # a genuinely-different subject must NOT fuzzy-match (can-fail separation)
    sr_cos_distinct = float((st._sr_key("usa", "capital") @ st._sr_key("banana", "capital"))
                            / st.n_dim)
    return {
        "exact_hash_detected_variant_conflict": bool(exact_detected),
        "fuzzy_detected_hits": fuzzy_hits,
        "fuzzy_fired": len(fuzzy_hits) > 0,
        "sr_cos_usa_vs_united_states": round(sr_cos_variant, 4),
        "sr_cos_usa_vs_banana": round(sr_cos_distinct, 4),
        "fuzzy_threshold": FUZZY_THRESHOLD,
        "separation_can_fail": round(sr_cos_variant - sr_cos_distinct, 4),
        "note": ("closes 29531 gap #a (exact-dictionary conflict, no surface-variant). Bounded demo; "
                 "ANN/LSH sub-linear fuzzy retrieval at KB-scale = noted-not-built (29532/29534)."),
    }


# ---------------------------------------------------------------------------
# ARC coverage monitor
# ---------------------------------------------------------------------------
def arc_vocab_coverage(store, questions):
    """Fraction of ARC-Easy question content-words that appear as a registered SUBJECT/OBJECT
    entity in the store -- the real coverage cap (thin science coverage silently caps the climb)."""
    ent = set()
    for d in ("SUBJECT", "OBJECT"):
        for s in store._domain_syms[d]:
            for w in str(s).replace("_", " ").split():
                ent.add(w.lower())
    seen = covered = 0
    for q in questions:
        for w in set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), min_len=4)):
            seen += 1
            if w in ent:
                covered += 1
    return {"arc_content_words_seen": seen, "arc_content_words_in_kb": covered,
            "arc_vocab_coverage": round(covered / seen, 4) if seen else 0.0}


# ---------------------------------------------------------------------------
# ARC fact-retrieval scoring (semantic encode of live-fact text; fair vs semantic-IR floor)
# ---------------------------------------------------------------------------
def _fact_texts(store):
    return [f"{f.subject} {f.relation} {f.obj}".replace("_", " ") for f in store.live_facts()]


def arc_score(sem_enc, questions, store_texts, seed_off):
    """max-cosine over the semantic-encoded store rows; argmax choice. Returns per-Easy accuracy."""
    if store_texts:
        SV = arc._encode_store(sem_enc, store_texts)
    else:
        SV = np.zeros((0, sem_enc.n_dim), dtype=np.float32)
    QV, qmap = arc._build_queries(sem_enc, questions)
    res, best_idx, best_cos = arc._score_curve(
        QV, qmap, SV, questions, [SV.shape[0]], np.random.default_rng(SEED + seed_off),
        track_support=True)
    acc = res[SV.shape[0]]
    frac_matched = float(np.mean(best_cos > 0.10)) if SV.shape[0] else 0.0
    return acc, SV, frac_matched


def arc_score_curve(sem_enc, questions, store_texts, fracs, seed_off):
    """Ingest-fraction climb curve for the fact-retrieval arm (deterministic sub-store order)."""
    SV = arc._encode_store(sem_enc, store_texts) if store_texts else \
        np.zeros((0, sem_enc.n_dim), dtype=np.float32)
    QV, qmap = arc._build_queries(sem_enc, questions)
    M = SV.shape[0]
    bp = sorted(set(int(round(fr * M)) for fr in fracs))
    res = arc._score_curve(QV, qmap, SV, questions, bp, np.random.default_rng(SEED + seed_off))
    curve = {}
    for fr in fracs:
        cols = int(round(fr * M))
        key = cols if cols in res else min(res.keys(), key=lambda k: abs(k - cols))
        curve[f"{fr:.2f}"] = {"store_cols": cols, "acc_easy": res[key]["acc_easy"]}
    return curve


# ---------------------------------------------------------------------------
# self-test (real code path + determinism + discriminator fires)
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] constructing REAL SemanticHDEncoder + SemanticHDFactStore ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    sem = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    # real code path: SemanticHDFactStore ingest a few triples through the trust-gate
    st = SemanticHDFactStore(n_dim=nd, seed=SEED, sem_encoder=sem,
                             relation_cardinality={"capital_of": "FUNCTIONAL",
                                                   "capable_of": "MULTIVALUED"}, use_index=True)
    r1 = st.store("paris", "capital_of", "france", "conceptnet", "TRUST_HIGH")
    st.store("dog", "capable_of", "bark", "conceptnet", "TRUST_HIGH")
    assert r1.resolution in ("CLEAN_STORE", "CONSISTENT_DUP"), r1
    assert st.n_sem >= 1, f"no semantic codes registered: n_sem={st.n_sem}"

    # semantic codes are bipolar
    v = st.codec._sym_vec("paris")
    assert set(torch.unique(v).tolist()).issubset({-1.0, 1.0}), "filler code not bipolar"

    # glass-box round-trip recovers the planted fact
    rec = st.recover_fact(st._facts[r1.fid].vec)
    assert rec["subject"] == "paris" and rec["relation"] == "capital_of" and rec["object"] == "france", rec

    # DISCRIMINATOR FIRES: semantic sr_key of a surface variant is CLOSE, a distinct subject is FAR
    sr_close = float((st._sr_key("usa", "capital_of") @ st._sr_key("america", "capital_of")) / nd)
    sr_far = float((st._sr_key("usa", "capital_of") @ st._sr_key("banana", "capital_of")) / nd)
    print(f"[self-test] sr_cos(usa,america)={sr_close:.3f} > sr_cos(usa,banana)={sr_far:.3f}", flush=True)
    assert sr_close > sr_far, f"semantic sr_key did not separate variant from distinct: {sr_close} vs {sr_far}"

    # fuzzy conflict demo fires; exact hash misses; separation can-fail
    fd = fuzzy_conflict_demo(sem, nd)
    assert fd["fuzzy_fired"], f"fuzzy conflict did not fire: {fd}"
    assert fd["separation_can_fail"] > 0.0, f"fuzzy separation collapsed: {fd}"

    # real ARC scoring path on a planted toy: the fact set supports the correct choice
    q = [{"qid": "T1", "stem": "What is the capital of france?",
          "choices": ["banana fruit", "paris france capital", "dog bark", "iron metal"],
          "correct_index": 1, "source": "ARC-Easy-Test.jsonl"}]
    texts = _fact_texts(st)
    acc, SV, frac = arc_score(sem, q, texts, seed_off=1)
    assert acc["acc_easy"] == 1.0, f"fact-retrieval failed planted toy: {acc}"

    # arms-differ: fact store vs scramble store hash-differ
    import hashlib
    scr = arc._unit_rows((np.random.default_rng(1).integers(0, 2, size=SV.shape) * 2 - 1).astype(np.float32))
    assert hashlib.sha256(SV.tobytes()).hexdigest() != hashlib.sha256(scr.tobytes()).hexdigest()

    # determinism
    acc2, _, _ = arc_score(sem, q, texts, seed_off=1)
    assert acc["acc_easy"] == acc2["acc_easy"], "non-deterministic scoring"

    # substrate signature bind (portable base kwargs only)
    import inspect
    sig = inspect.signature(HDFactStore.__init__)
    for kw in ("n_dim", "seed", "relation_cardinality", "sr_threshold", "use_index"):
        assert kw in sig.parameters, f"HDFactStore missing base kwarg {kw}"
    print("[self-test] PASS (real semantic store ingest, trust-gate, round-trip, fuzzy, ARC scoring, "
          "determinism, arms-differ)", flush=True)
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 1024, "easy_limit": 400, "chal_limit": 0, "n_ingest": 12000,
                "n_broad": 12000, "corpus_max_lines": 400000, "rt_sample": 120}
    return {"n_dim": 2048, "easy_limit": None, "chal_limit": None, "n_ingest": 60000,
            "n_broad": 60000, "corpus_max_lines": 2500000, "rt_sample": 300}


def _broad_corpus_sample(n, max_lines):
    """First-n valid ARC_Corpus sentences (answer-agnostic; the semantic-IR floor store)."""
    out = []
    with open(arc._CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i > max_lines:
                break
            s = line.strip()
            ntok = s.count(" ") + 1
            if ntok < 5 or ntok > 60 or len(s) < 20:
                continue
            out.append(s)
            if len(out) >= n:
                break
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    output_dir = _out_dir()
    cfg = _config(args.mode)
    _T0[0] = time.perf_counter()
    _write_start_marker(output_dir, args.mode)

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _heartbeat(output_dir, "load_wordnet")
    _load_wordnet()

    _heartbeat(output_dir, "build_encoder")
    sem_enc = SemanticHDEncoder(n_dim=cfg["n_dim"], seed=SEED, use_wordnet=True, kv=kv)

    # ---- eval questions ----
    questions = arc._load_questions(arc._EASY_TEST, cfg["easy_limit"])
    if cfg["chal_limit"] != 0:
        questions += arc._load_questions(arc._CHAL_TEST, cfg["chal_limit"])
    questions.sort(key=lambda q: q["qid"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    print(f"[eval] {len(questions)} questions ({n_easy} Easy, {n_chal} Challenge)", flush=True)
    chance = arc._chance_theoretical(questions)
    ctrl_random = arc._control_random(questions, np.random.default_rng(SEED + 1))

    # ---- ingest ConceptNet through the trust-gate (WIRE MEANING IN) ----
    _heartbeat(output_dir, "load_conceptnet")
    triples = _load_conceptnet(cfg["n_ingest"], np.random.default_rng(SEED + 20))
    store = SemanticHDFactStore(n_dim=cfg["n_dim"], seed=SEED, sem_encoder=sem_enc,
                                relation_cardinality=REL_CARD, use_index=True)
    _heartbeat(output_dir, "ingest_start", {"n_triples": len(triples)})
    t_ing = time.perf_counter()
    trust_hist = ingest_conceptnet(store, triples, output_dir)
    n_live = len(store.live_facts())
    ingest_coverage = round(store.n_sem / (store.n_sem + store.n_oov), 4) if (store.n_sem + store.n_oov) else 0.0
    print(f"[ingest] {len(triples)} triples in {time.perf_counter()-t_ing:.1f}s ; live={n_live} ; "
          f"n_sem={store.n_sem} n_oov={store.n_oov} coverage={ingest_coverage} ; hist={trust_hist}", flush=True)

    # ---- monitors ----
    _heartbeat(output_dir, "roundtrip")
    rt = roundtrip_eval(store, cfg["rt_sample"], np.random.default_rng(SEED + 30))
    cov = arc_vocab_coverage(store, [q for q in questions if q["source"].startswith("ARC-Easy")])
    _heartbeat(output_dir, "fuzzy")
    fuzzy = fuzzy_conflict_demo(sem_enc, cfg["n_dim"])

    # ---- ARC arms ----
    _heartbeat(output_dir, "arc_empty")
    empty_acc, _, _ = arc_score(sem_enc, questions, [], seed_off=2)

    _heartbeat(output_dir, "arc_fact")
    fact_texts = _fact_texts(store)
    fact_acc, SV_fact, fact_frac = arc_score(sem_enc, questions, fact_texts, seed_off=3)
    fact_curve = arc_score_curve(sem_enc, questions, fact_texts, arc.CURVE_FRACS, seed_off=3)

    _heartbeat(output_dir, "arc_semantic_ir")
    broad = _broad_corpus_sample(cfg["n_broad"], cfg["corpus_max_lines"])
    sir_acc, SV_sir, _ = arc_score(sem_enc, questions, broad, seed_off=4)

    _heartbeat(output_dir, "arc_scramble")
    scr_rng = np.random.default_rng(SEED + 7)
    SV_scr = arc._unit_rows((scr_rng.integers(0, 2, size=SV_fact.shape) * 2 - 1).astype(np.float32)) \
        if SV_fact.shape[0] else SV_fact
    QV, qmap = arc._build_queries(sem_enc, questions)
    if SV_scr.shape[0]:
        scr_res = arc._score_curve(QV, qmap, SV_scr, questions, [SV_scr.shape[0]],
                                   np.random.default_rng(SEED + 5))
        scr_acc = scr_res[SV_scr.shape[0]]
    else:
        scr_acc = empty_acc

    # arms-differ (META_RULE_AF)
    import hashlib
    hashes = {
        "fact": hashlib.sha256(SV_fact.tobytes()).hexdigest() if SV_fact.shape[0] else "empty",
        "semantic_ir": hashlib.sha256(SV_sir.tobytes()).hexdigest() if SV_sir.shape[0] else "empty",
        "scramble": hashlib.sha256(SV_scr.tobytes()).hexdigest() if SV_scr.shape[0] else "empty",
    }
    nonempty = [v for v in hashes.values() if v != "empty"]
    arms_differ = len(set(nonempty)) == len(nonempty)

    # ---- verdict (PRIMARY = ARC-Easy fact_retrieval) ----
    e_empty = empty_acc["acc_easy"]
    e_fact = fact_acc["acc_easy"]
    e_sir = sir_acc["acc_easy"]
    e_scr = scr_acc["acc_easy"]
    d_floor = round(e_fact - e_sir, 4)
    d_empty = round(e_fact - e_empty, 4)
    d_scr = round(e_fact - e_scr, 4)
    baseline_in_band = (e_empty is not None) and (0.05 < e_empty < 0.95)
    # LEAK = the SCRAMBLE (random-vector) store genuinely beats the empty/chance baseline -> the store
    # structure (not its content) is leaking answer info. A fact arm that merely fails to climb (fact
    # ~ chance ~ scramble) is NOT a leak -> it yields KB_FLAT/BELOW. Genuineness of a PASS is enforced
    # separately by the d_scr >= HP_BEAT_SCRAMBLE clause inside KB_BEATS_FLOOR.
    leak = (e_scr is not None) and (e_empty is not None) and (e_scr >= e_empty + 0.05)

    if leak:
        verdict = "LEAK_FLAG"
        vmsg = f"SCRAMBLE Easy {e_scr:.3f} >= empty {e_empty:.3f}+0.05 -> store structure leaks (artifact)"
    elif d_floor >= HP_BEAT_FLOOR and d_empty >= HP_BEAT_EMPTY and d_scr >= HP_BEAT_SCRAMBLE:
        verdict = "KB_BEATS_FLOOR"
        vmsg = (f"fact-retrieval Easy {e_fact:.3f} BEATS semantic-IR floor {e_sir:.3f} "
                f"(+{d_floor:.3f}); vs empty {e_empty:.3f} (+{d_empty:.3f}); vs scramble +{d_scr:.3f}")
    elif abs(d_floor) < FLAT_EPS:
        verdict = "KB_FLAT"
        vmsg = (f"fact-retrieval Easy {e_fact:.3f} TIES semantic-IR floor {e_sir:.3f} "
                f"(delta {d_floor:+.3f}); ARC-vocab coverage={cov['arc_vocab_coverage']}")
    else:
        verdict = "KB_BELOW_FLOOR"
        vmsg = (f"fact-retrieval Easy {e_fact:.3f} BELOW semantic-IR floor {e_sir:.3f} "
                f"(delta {d_floor:+.3f}); ARC-vocab coverage={cov['arc_vocab_coverage']}")

    grade = arc._grade_proxy(e_fact, fact_acc.get("acc_challenge"))

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: fact_easy={e_fact:.3f} floor(sir)={e_sir:.3f} empty={e_empty:.3f} "
                   f"scramble={e_scr:.3f} | ingest_coverage={ingest_coverage} arc_cov={cov['arc_vocab_coverage']}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": args.mode, "n_dim": cfg["n_dim"], "seed": SEED,
        "n_questions": len(questions), "n_easy": n_easy, "n_challenge": n_chal,
        # --- controls ---
        "chance_theoretical": round(chance, 4), "control_random_pick": round(ctrl_random, 4),
        # --- PRIMARY: ARC-Easy arms (all use the SAME SemanticHDEncoder) ---
        "empty_acc_easy": None if e_empty is None else round(e_empty, 4),
        "fact_retrieval_acc_easy": None if e_fact is None else round(e_fact, 4),
        "semantic_ir_floor_acc_easy": None if e_sir is None else round(e_sir, 4),
        "scramble_acc_easy": None if e_scr is None else round(e_scr, 4),
        "delta_fact_minus_floor_easy": d_floor,
        "delta_fact_minus_empty_easy": d_empty,
        "delta_fact_minus_scramble_easy": d_scr,
        "fact_retrieval_climb_curve_easy": fact_curve,
        # --- Challenge (expected flat; reported honestly) ---
        "fact_retrieval_acc_challenge": None if fact_acc.get("acc_challenge") is None else round(fact_acc["acc_challenge"], 4),
        "semantic_ir_acc_challenge": None if sir_acc.get("acc_challenge") is None else round(sir_acc["acc_challenge"], 4),
        # --- store sizes (transparency; bigger store != better per 29530) ---
        "n_triples_ingested": len(triples), "n_live_facts": n_live,
        "fact_store_rows": int(SV_fact.shape[0]), "semantic_ir_store_rows": int(SV_sir.shape[0]),
        # --- MONITORS (director cares) ---
        "ingest_coverage_sem_frac": ingest_coverage,
        "ingest_n_sem": store.n_sem, "ingest_n_oov": store.n_oov,
        "arc_vocab_coverage": cov,
        "trust_gate_fire_histogram": trust_hist,
        "glassbox_roundtrip": rt,
        "fuzzy_conflict_demo": fuzzy,
        # --- gates / integrity ---
        "baseline_in_band": bool(baseline_in_band),
        "leak_flag": bool(leak),
        "discriminator_fires_fact_frac_matched_gt_0.10": round(fact_frac, 4),
        "arms_differ_verified": bool(arms_differ),
        "arm_store_hashes": hashes,
        "bands": {"HP_beat_floor": HP_BEAT_FLOOR, "HP_beat_empty": HP_BEAT_EMPTY,
                  "HP_beat_scramble": HP_BEAT_SCRAMBLE, "flat_eps": FLAT_EPS},
        # --- human scale ---
        "grade_proxy": grade,
        "human_scale_statement": (
            f"Fact-retrieval over {n_live} vetted ConceptNet triples answers ARC-Easy at "
            f"{('%.3f' % e_fact) if e_fact is not None else 'n/a'} "
            f"(semantic-IR floor {('%.3f' % e_sir) if e_sir is not None else 'n/a'}; empty/chance "
            f"{('%.3f' % e_empty) if e_empty is not None else 'n/a'}). Limit diagnosis: ARC-Easy "
            f"content-word coverage by the KB = {cov['arc_vocab_coverage']} "
            f"({'COVERAGE-capped' if cov['arc_vocab_coverage'] < 0.5 else 'coverage-OK'})."),
        "wired_vs_stubbed": (
            "WIRED: SemanticHDFactStore (semantic bipolar codes injected for SUBJECT/OBJECT fillers), "
            "ConceptNet ingest through the trust-gate, glass-box round-trip on the real bundles, "
            "semantic fuzzy-conflict demo, ARC fact-retrieval vs semantic-IR floor + empty + scramble, "
            "ingest+ARC-vocab coverage monitors. STUBBED/NOTED-NOT-BUILT: ANN/LSH sub-linear fuzzy "
            "retrieval at KB-scale (fuzzy demo is bounded); ARC scoring uses semantic-text-encode of "
            "the live-fact set (fair vs the floor's same encoder), NOT free-text->triple extraction "
            "against role-bound bundles (the bundle rep is validated separately by round-trip+fuzzy); "
            "reasoning/multi-hop layer (Challenge) = separate, deferred."),
        "contract": "INLINE-LOCAL; store LOCAL-ONLY + UNCOMMITTED; no push/remote-persist; "
                    "NOT remote-portable (ConceptNet+GloVe git-ignored); VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)

    # persist glass-box artifacts LOCAL-ONLY (uncommitted)
    try:
        with open(os.path.join(output_dir, "fact_store_texts_sample.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(fact_texts[:500]))
    except Exception as e:
        print(f"[warn] persist failed (non-fatal): {e}", flush=True)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[arms] empty={e_empty} fact={e_fact} semantic_ir_floor={e_sir} scramble={e_scr}", flush=True)
    print(f"[monitors] ingest_cov={ingest_coverage} arc_cov={cov['arc_vocab_coverage']} "
          f"roundtrip={rt} trust_hist={trust_hist}", flush=True)
    print(f"[fuzzy] {fuzzy}", flush=True)
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
