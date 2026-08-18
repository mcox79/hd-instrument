"""ARC human-scale knowledge measure + honest baseline + first ingest-and-climb increment.

Builds a HUMAN-SCALE yardstick for the substrate's science knowledge:
  1. GLASS-BOX MC-QA HARNESS (substrate-native, NO external LLM): each ARC question is answered
     by RETRIEVAL/MATCHING over an HD store. Text->HD via the substrate's own
     hdlab.char_trigram_encoder.CharTrigramEncoder (bag-of-char-trigrams bipolar HD). For stem S
     and each choice c_i: query_i = encode(S + " " + c_i); score_i = max_j cos(query_i, store_j);
     pick argmax. Glass-box: the picked choice's top supporting corpus sentence + cosine is logged.
  2. HONEST BASELINE: empty store (curve frac 0.0) -> all scores tie -> seeded random tie-break
     -> ~chance (0.25 on 4-way). Random + majority + theoretical-chance controls reported.
  3. FIRST INGEST-AND-CLIMB: stream ARC_Corpus.txt, keep answer-agnostic RELEVANT sentences,
     encode into the store, re-measure ARC accuracy at store fractions {0,.25,.5,.75,1.0}.
     RISING above chance = climbing the human scale. FLAT = honest can-fail + diagnosis.
  Controls: SCRAMBLE (same-size random-vector store; genuineness) + RANDOM_INGEST (generic
  unfiltered sample; coverage).

Contract: INLINE-LOCAL foreground-to-completion; NO queue/push/remote-persist; store LOCAL-ONLY
+ UNCOMMITTED. ASCII-only. Deterministic (fixed seeds; numpy default_rng; sorted iteration).
Runs in repo .venv. Agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic metrics ; heartbeat
# - real_code_path: self_test constructs the REAL CharTrigramEncoder + runs the REAL scoring fn
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
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

from hdlab.char_trigram_encoder import CharTrigramEncoder

ANCHOR_NAME = "arc_knowledge_scale_ingest_climb_v1"
SEED = 20260724

_ARC = os.path.join(_REPO, "data", "corpora", "arc", "ARC-V1-Feb2018-2")
_EASY_TEST = os.path.join(_ARC, "ARC-Easy", "ARC-Easy-Test.jsonl")
_CHAL_TEST = os.path.join(_ARC, "ARC-Challenge", "ARC-Challenge-Test.jsonl")
_CORPUS = os.path.join(_ARC, "ARC_Corpus.txt")

CURVE_FRACS = [0.0, 0.25, 0.5, 0.75, 1.0]

_STOPWORDS = frozenset("""
the a an and or of to in on at for with from by as is are was were be been being this that these
those it its their they them he she his her you your we our not no do does did which what when where
who whom how why than then into over under out up down off about above below between more most some
any all each both few many much such only same other will would can could should may might must have
has had having also because if but so nor yet very just per via etc within without across during before
after while once here there both either neither one two three four five best explains statement following
""".split())


# ---------------------------------------------------------------------------
# markers / crash diagnostics (per CELL-TEMPLATE)
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# data loading
# ---------------------------------------------------------------------------
def _content_words(text, min_len=4):
    """Lowercased alphanumeric content words, len>=min_len, minus stopwords."""
    out = []
    for tok in text.lower().split():
        w = "".join(ch for ch in tok if ch.isalnum())
        if len(w) >= min_len and w not in _STOPWORDS:
            out.append(w)
    return out


def _load_questions(path, limit):
    """Load ARC questions -> list of dicts {qid, stem, choices:[text], correct_index, source}."""
    qs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            ch = d["question"]["choices"]
            labels = [c["label"] for c in ch]
            key = d.get("answerKey")
            if key not in labels:
                continue  # skip malformed
            qs.append({
                "qid": d["id"],
                "stem": d["question"]["stem"],
                "choices": [c["text"] for c in ch],
                "correct_index": labels.index(key),
                "source": os.path.basename(path),
            })
            if limit and len(qs) >= limit:
                break
    return qs


def _scan_corpus_targeted(questions, k_per_q, n_random, max_lines, min_overlap, cap_q):
    """Faithful IR-index regime: stream the corpus once and, for each eval question, keep its
    top-k lexically-overlapping corpus sentences (answer-agnostic: overlap is with stem+ALL
    choices, NEVER the answerKey). Also collect a generic first-N-valid RANDOM sample.

    Returns (relevant_sentences, random_sample, n_scanned, vocab_kept, n_questions_covered).
    A word appearing in > cap_q questions is dropped from the index (too generic to discriminate).
    A (question, sentence) match requires >= min_overlap shared content words (len>=5)."""
    import heapq
    from collections import defaultdict, Counter
    qwords = [set(_content_words(q["stem"] + " " + " ".join(q["choices"]), min_len=5))
              for q in questions]
    w2q = defaultdict(list)
    for qi, s in enumerate(qwords):
        for w in s:
            w2q[w].append(qi)
    w2q = {w: v for w, v in w2q.items() if len(v) <= cap_q}
    pools = defaultdict(list)  # qi -> min-heap of (overlap, tiebreak, sentence)
    rand = []
    n = 0
    tie = 0
    with open(_CORPUS, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            n += 1
            if n > max_lines:
                break
            s = line.strip()
            ntok = s.count(" ") + 1
            if ntok < 5 or ntok > 60 or len(s) < 20:
                continue
            if len(rand) < n_random:
                rand.append(s)
            c = Counter()
            for w in set(_content_words(s, min_len=5)):
                lst = w2q.get(w)
                if lst:
                    for qi in lst:
                        c[qi] += 1
            for qi, ov in c.items():
                if ov < min_overlap:
                    continue
                h = pools[qi]
                if len(h) < k_per_q:
                    heapq.heappush(h, (ov, tie, s)); tie += 1
                elif ov > h[0][0]:
                    heapq.heapreplace(h, (ov, tie, s)); tie += 1
    relevant, seen = [], set()
    for qi in sorted(pools):
        for ov, _, s in sorted(pools[qi], reverse=True):
            key = s.lower()
            if key not in seen:
                seen.add(key)
                relevant.append(s)
    n_covered = sum(1 for qi in pools if pools[qi])
    return relevant, rand, n, len(w2q), n_covered


# ---------------------------------------------------------------------------
# encoding / scoring
# ---------------------------------------------------------------------------
def _unit_rows(mat):
    """L2-normalize rows; zero rows stay zero."""
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def _encode_store(encoder, sentences):
    if not sentences:
        return np.zeros((0, encoder.n_dim), dtype=np.float32)
    return _unit_rows(encoder.encode_batch(sentences).astype(np.float32))


def _build_queries(encoder, questions):
    """Flatten (question, choice) -> query matrix + index map. query text = stem + ' ' + choice."""
    texts, qmap = [], []
    for qi, q in enumerate(questions):
        for ci, c in enumerate(q["choices"]):
            texts.append(q["stem"] + " " + c)
            qmap.append((qi, ci))
    QV = _unit_rows(encoder.encode_batch(texts).astype(np.float32))
    return QV, qmap


def _score_curve(QV, qmap, SV, questions, breakpoint_cols, rng, chunk=4000, track_support=False):
    """Streaming max-cosine over SV in column order. At each breakpoint (# store cols processed)
    snapshot per-query best cosine and compute per-question accuracy.
    Returns dict: {n_cols: accuracy} plus (if track_support) final best_idx per query."""
    nQ = QV.shape[0]
    M = SV.shape[0]
    best = np.full(nQ, -np.inf, dtype=np.float32)
    best_idx = np.full(nQ, -1, dtype=np.int64)
    breakpoints = sorted(set(int(b) for b in breakpoint_cols))
    results = {}
    # frac 0 / empty snapshot (all tie)
    if 0 in breakpoints:
        results[0] = _accuracy_from_scores(best, qmap, questions, rng)
    processed = 0
    bp_iter = [b for b in breakpoints if b > 0]
    next_bp = 0
    for a in range(0, M, chunk):
        b = min(a + chunk, M)
        sims = QV @ SV[a:b].T  # (nQ, b-a)
        loc = np.argmax(sims, axis=1)
        loc_val = sims[np.arange(nQ), loc]
        upd = loc_val > best
        best_idx[upd] = a + loc[upd]
        best = np.maximum(best, loc_val)
        processed = b
        while next_bp < len(bp_iter) and processed >= bp_iter[next_bp]:
            results[bp_iter[next_bp]] = _accuracy_from_scores(best, qmap, questions, rng)
            next_bp += 1
    # any breakpoints beyond M -> use full-store result
    while next_bp < len(bp_iter):
        results[bp_iter[next_bp]] = _accuracy_from_scores(best, qmap, questions, rng)
        next_bp += 1
    if track_support:
        return results, best_idx, best
    return results


def _accuracy_from_scores(best, qmap, questions, rng):
    """Given per-query best cosine, pick argmax choice per question (seeded random tie-break)."""
    per_q = {}
    for k, (qi, ci) in enumerate(qmap):
        per_q.setdefault(qi, []).append((ci, float(best[k])))
    correct = 0
    n_easy = n_chal = c_easy = c_chal = 0
    for qi, q in enumerate(questions):
        scored = per_q[qi]
        mx = max(s for _, s in scored)
        # tie set (within tiny eps) -> random tie-break
        if not np.isfinite(mx):
            cand = [ci for ci, _ in scored]
        else:
            cand = [ci for ci, s in scored if abs(s - mx) < 1e-6]
        pick = int(rng.choice(cand)) if len(cand) > 1 else cand[0]
        hit = int(pick == q["correct_index"])
        correct += hit
        if q["source"].startswith("ARC-Easy"):
            n_easy += 1; c_easy += hit
        else:
            n_chal += 1; c_chal += hit
    n = len(questions)
    return {
        "acc": correct / n if n else 0.0,
        "acc_easy": c_easy / n_easy if n_easy else None,
        "acc_challenge": c_chal / n_chal if n_chal else None,
        "n": n, "n_easy": n_easy, "n_challenge": n_chal,
    }


def _control_random(questions, rng):
    correct = 0
    for q in questions:
        if int(rng.integers(0, len(q["choices"]))) == q["correct_index"]:
            correct += 1
    return correct / len(questions)


def _control_majority(questions):
    from collections import Counter
    c = Counter(q["correct_index"] for q in questions)
    modal = c.most_common(1)[0][0]
    correct = sum(1 for q in questions
                  if min(modal, len(q["choices"]) - 1) == q["correct_index"])
    return correct / len(questions), int(modal)


def _chance_theoretical(questions):
    return float(np.mean([1.0 / len(q["choices"]) for q in questions]))


def _grade_proxy(easy_acc, chal_acc):
    """COARSE, explicitly-heuristic human-scale proxy. NOT calibrated to real student scores."""
    def band(acc, easy):
        if acc is None:
            return "n/a"
        if acc < 0.30:
            return "below grade 3 (~chance; no science knowledge)"
        if acc < 0.42:
            return "emerging (~grade 2-3, above chance)"
        if acc < 0.55:
            return "~grade 3-4"
        if acc < 0.70:
            return "~grade 4-5" if easy else "~grade 6-7"
        return ">= grade-5 target" if easy else ">= grade-8 target"
    return {
        "easy_band": band(easy_acc, True),
        "challenge_band": band(chal_acc, False),
        "note": "COARSE heuristic proxy: ARC-Easy targets grade 3-5, Challenge grade 6-9 (dataset "
                "design). Bands are an anchor, NOT a measured comparison to real student score "
                "distributions (none available). Chance ~0.25 = bottom of scale.",
    }


# ---------------------------------------------------------------------------
# self-test (real code path + determinism)
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] constructing REAL CharTrigramEncoder ...")
    enc = CharTrigramEncoder(n_dim=1024)  # tiny-scale real object; N>=256 discriminates cleanly
    v1 = enc.encode("photosynthesis converts sunlight into chemical energy")
    v2 = enc.encode("photosynthesis converts sunlight into chemical energy")
    assert v1.shape == (1024,), v1.shape
    assert np.array_equal(v1, v2), "encoder non-deterministic"
    assert set(np.unique(v1)).issubset({-1.0, 1.0}), "encoder not bipolar"

    # REAL scoring path on a toy: planted supporting sentence for choice 1.
    store_sents = [
        "the moon orbits the earth once each month",
        "green plants use sunlight energy to make sugar during photosynthesis",
        "iron is a heavy metal used in construction",
    ]
    SV = _encode_store(enc, store_sents)
    questions = [{
        "qid": "T1",
        "stem": "What do green plants use to make food?",
        "choices": ["sound waves", "sunlight energy from photosynthesis", "iron metal", "moon orbit"],
        "correct_index": 1,
        "source": "ARC-Easy-Test.jsonl",
    }]
    QV, qmap = _build_queries(enc, questions)
    assert QV.shape[0] == 4, QV.shape
    rng = np.random.default_rng(SEED)
    res = _score_curve(QV, qmap, SV, questions, [0, SV.shape[0]], rng)
    # discriminator fires: with the planted store the correct choice must be picked
    assert res[SV.shape[0]]["acc"] == 1.0, f"scoring failed to pick planted choice: {res}"
    # empty store -> tie -> not guaranteed correct; just runs
    assert 0.0 <= res[0]["acc"] <= 1.0

    # determinism: two identical runs (single-threaded numpy) give identical predictions
    r_a = _score_curve(QV, qmap, SV, questions, [SV.shape[0]], np.random.default_rng(SEED))
    r_b = _score_curve(QV, qmap, SV, questions, [SV.shape[0]], np.random.default_rng(SEED))
    assert r_a[SV.shape[0]]["acc"] == r_b[SV.shape[0]]["acc"], "non-deterministic scoring"

    # arms-differ: relevant vs scramble store hash-differ
    import hashlib
    scr = _unit_rows((np.random.default_rng(1).integers(0, 2, size=SV.shape) * 2 - 1).astype(np.float32))
    h_real = hashlib.sha256(SV.tobytes()).hexdigest()
    h_scr = hashlib.sha256(scr.tobytes()).hexdigest()
    assert h_real != h_scr, "META_RULE_AF: real and scramble stores bit-identical"

    # control sanity: random control near chance on a 4-way toy of many items
    many = questions * 200
    rc = _control_random(many, np.random.default_rng(SEED))
    assert 0.10 < rc < 0.40, f"random control off-chance: {rc}"
    print("[self-test] PASS (real encoder, real scoring, determinism, arms-differ, controls)")
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "easy_limit": 150, "chal_limit": 150,
                "k_per_q": 6, "min_overlap": 2, "cap_q": 150,
                "n_random": 6000, "max_lines": 500000}
    return {"n_dim": 2048, "easy_limit": None, "chal_limit": None,
            "k_per_q": 12, "min_overlap": 3, "cap_q": 150,
            "n_random": 60000, "max_lines": 2500000}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    output_dir = _out_dir()
    cfg = _config(args.mode)
    _write_start_marker(output_dir, args.mode, cfg["k_per_q"])
    t0 = time.perf_counter()
    rng = np.random.default_rng(SEED)

    # ---- load eval ----
    _heartbeat(output_dir, "load_eval")
    questions = _load_questions(_EASY_TEST, cfg["easy_limit"]) + _load_questions(_CHAL_TEST, cfg["chal_limit"])
    questions.sort(key=lambda q: q["qid"])  # deterministic order
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    print(f"[eval] {len(questions)} questions ({n_easy} Easy, {n_chal} Challenge)")

    # ---- controls ----
    ctrl_random = _control_random(questions, np.random.default_rng(SEED + 1))
    ctrl_majority, modal_idx = _control_majority(questions)
    chance = _chance_theoretical(questions)

    # ---- ingest corpus (targeted IR-index; answer-agnostic per-question top-k) ----
    _heartbeat(output_dir, "scan_corpus")
    t_scan = time.perf_counter()
    relevant, rand_sample, n_scanned, vocab_kept, n_covered = _scan_corpus_targeted(
        questions, cfg["k_per_q"], cfg["n_random"], cfg["max_lines"], cfg["min_overlap"], cfg["cap_q"])
    # shuffle relevant deterministically so the curve reflects amount-of-science ingested,
    # not question-grouping order.
    order = np.random.default_rng(SEED + 11).permutation(len(relevant))
    relevant = [relevant[i] for i in order]
    kw_size = vocab_kept
    print(f"[ingest] scanned {n_scanned} corpus lines in {time.perf_counter()-t_scan:.1f}s ; "
          f"kept {len(relevant)} relevant ({n_covered}/{len(questions)} questions covered), "
          f"{len(rand_sample)} random ; index_vocab={vocab_kept}")

    # ---- encode ----
    _heartbeat(output_dir, "encode")
    enc = CharTrigramEncoder(n_dim=cfg["n_dim"])
    t_enc = time.perf_counter()
    SV_rel = _encode_store(enc, relevant)
    SV_rand = _encode_store(enc, rand_sample)
    QV, qmap = _build_queries(enc, questions)
    scr_rng = np.random.default_rng(SEED + 7)
    SV_scr = _unit_rows((scr_rng.integers(0, 2, size=SV_rel.shape) * 2 - 1).astype(np.float32)) \
        if SV_rel.shape[0] else SV_rel
    print(f"[encode] store_rel={SV_rel.shape} store_rand={SV_rand.shape} queries={QV.shape} "
          f"in {time.perf_counter()-t_enc:.1f}s ; unique_trigrams={len(enc)}")

    # arms-differ (META_RULE_AF)
    import hashlib
    arm_hashes = {
        "relevant": hashlib.sha256(SV_rel.tobytes()).hexdigest() if SV_rel.shape[0] else "empty",
        "scramble": hashlib.sha256(SV_scr.tobytes()).hexdigest() if SV_scr.shape[0] else "empty",
        "random": hashlib.sha256(SV_rand.tobytes()).hexdigest() if SV_rand.shape[0] else "empty",
    }
    arms_differ = len(set(arm_hashes.values())) == len([v for v in arm_hashes.values() if v != "empty"]) \
        or len(set(arm_hashes.values())) == 3

    # ---- score: relevant curve (with glass-box support) ----
    _heartbeat(output_dir, "score_relevant")
    M = SV_rel.shape[0]
    bp = sorted(set(int(round(f * M)) for f in CURVE_FRACS))
    curve_res, best_idx, best_cos = _score_curve(
        QV, qmap, SV_rel, questions, bp, np.random.default_rng(SEED + 2), track_support=True)
    # map breakpoint cols -> fraction label
    curve = {}
    for f in CURVE_FRACS:
        cols = int(round(f * M))
        # find nearest computed breakpoint
        key = cols if cols in curve_res else min(curve_res.keys(), key=lambda k: abs(k - cols))
        curve[f"{f:.2f}"] = {"store_cols": cols, **curve_res[key]}

    # discriminator-fires check: non-trivial top-1 cosines at full store
    frac_matched = float(np.mean(best_cos > 0.10)) if M else 0.0

    # ---- score: scramble + random ----
    _heartbeat(output_dir, "score_controls")
    scr_res = _score_curve(QV, qmap, SV_scr, questions, [SV_scr.shape[0]], np.random.default_rng(SEED + 3)) \
        if SV_scr.shape[0] else {0: _accuracy_from_scores(np.full(QV.shape[0], -np.inf), qmap, questions, np.random.default_rng(SEED + 3))}
    scr_acc = scr_res[SV_scr.shape[0]] if SV_scr.shape[0] else list(scr_res.values())[0]
    rand_res = _score_curve(QV, qmap, SV_rand, questions, [SV_rand.shape[0]], np.random.default_rng(SEED + 4)) \
        if SV_rand.shape[0] else {}
    rand_acc = rand_res[SV_rand.shape[0]] if SV_rand.shape[0] else None

    # ---- glass-box examples ----
    per_q = {}
    for k, (qi, ci) in enumerate(qmap):
        per_q.setdefault(qi, []).append((ci, k))
    gb_rng = np.random.default_rng(SEED + 5)
    glass = []
    for qi in range(min(len(questions), 6)):
        q = questions[qi]
        scored = [(ci, float(best_cos[k]), k) for ci, k in per_q[qi]]
        mx = max(s for _, s, _ in scored)
        cand = [(ci, k) for ci, s, k in scored if abs(s - mx) < 1e-6]
        pick_ci, pick_k = cand[int(gb_rng.integers(0, len(cand)))] if len(cand) > 1 else cand[0]
        sup_idx = int(best_idx[pick_k])
        glass.append({
            "qid": q["qid"], "source": q["source"], "stem": q["stem"],
            "choices": q["choices"], "picked_index": pick_ci,
            "correct_index": q["correct_index"], "correct": pick_ci == q["correct_index"],
            "pick_cosine": round(mx, 4),
            "supporting_sentence": relevant[sup_idx] if 0 <= sup_idx < len(relevant) else None,
        })

    # ---- verdict ----
    # PASS gate is on ARC-EASY accuracy (the primary grade-3-5 target; per pre-reg). Challenge
    # (grade 6-9 reasoning) is reported separately -- retrieval is not expected to solve it.
    base = curve["0.00"]["acc"]
    full = curve["1.00"]["acc"]
    base_easy = curve["0.00"]["acc_easy"]
    easy_full = curve["1.00"]["acc_easy"]
    chal_base = curve["0.00"]["acc_challenge"]
    chal_full = curve["1.00"]["acc_challenge"]
    scr_easy = scr_acc["acc_easy"]
    baseline_in_band = (0.05 < base < 0.95) and (base_easy is None or 0.05 < base_easy < 0.95)
    # headline climb = ARC-Easy
    climb_easy_abs = (easy_full - base_easy) if (easy_full is not None and base_easy is not None) else 0.0
    climb_easy_vs_scramble = (easy_full - scr_easy) if (easy_full is not None and scr_easy is not None) else 0.0
    climb_abs = full - base
    climb_vs_scramble = full - scr_acc["acc"]
    leak_flag = (scr_easy is not None and base_easy is not None and scr_easy >= base_easy + 0.05)
    passed = (climb_easy_abs >= 0.05) and (climb_easy_vs_scramble >= 0.03) and not leak_flag
    flat = abs(climb_easy_abs) < 0.03
    if leak_flag:
        verdict = "LEAK_FLAG"
        vmsg = (f"SCRAMBLE Easy {scr_easy:.3f} >= baseline Easy {base_easy:.3f}+0.05 -> gain is artifact")
    elif passed:
        verdict = "CLIMB_PASS"
        vmsg = (f"ingest RAISED ARC-Easy {base_easy:.3f}->{easy_full:.3f} (+{climb_easy_abs:.3f}); "
                f"survives scramble (+{climb_easy_vs_scramble:.3f}); "
                f"Challenge {chal_base:.3f}->{chal_full:.3f}")
    elif flat:
        verdict = "FLAT_CAN_FAIL"
        vmsg = (f"ingest FLAT at chance on Easy ({base_easy:.3f}->{easy_full:.3f}); retrieval-QA over "
                f"char-trigram store does not yet answer science Qs")
    else:
        verdict = "PARTIAL_CLIMB"
        vmsg = (f"ingest moved ARC-Easy {base_easy:.3f}->{easy_full:.3f} (+{climb_easy_abs:.3f}) but "
                f"below PASS band or scramble margin ({climb_easy_vs_scramble:.3f})")

    grade = _grade_proxy(easy_full, chal_full)

    metrics = {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: baseline={base:.3f} full={full:.3f} scramble={scr_acc['acc']:.3f} "
                   f"random_ingest={rand_acc['acc'] if rand_acc else None}",
        "elapsed_s": round(time.perf_counter() - t0, 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "mode": args.mode,
        "n_dim": cfg["n_dim"],
        "n_questions": len(questions), "n_easy": n_easy, "n_challenge": n_chal,
        "store_relevant_size": int(M), "store_random_size": int(SV_rand.shape[0]),
        "index_vocab_size": kw_size, "questions_covered": n_covered,
        "corpus_lines_scanned": n_scanned, "unique_trigrams": len(enc),
        # --- controls ---
        "control_random_pick": round(ctrl_random, 4),
        "control_majority": round(ctrl_majority, 4), "majority_modal_index": modal_idx,
        "chance_theoretical": round(chance, 4),
        # --- climb curve (the headline) ---
        "climb_curve": curve,
        "baseline_empty_acc": round(base, 4),
        "full_ingest_acc": round(full, 4),
        "full_ingest_acc_easy": None if easy_full is None else round(easy_full, 4),
        "full_ingest_acc_challenge": None if chal_full is None else round(chal_full, 4),
        # --- controls / genuineness ---
        "scramble_acc": round(scr_acc["acc"], 4),
        "random_ingest_acc": None if rand_acc is None else round(rand_acc["acc"], 4),
        "random_ingest_acc_easy": None if rand_acc is None else (None if rand_acc["acc_easy"] is None else round(rand_acc["acc_easy"], 4)),
        # --- gates (PASS is on ARC-Easy; aggregate + challenge reported for context) ---
        "baseline_in_band": bool(baseline_in_band),
        "baseline_empty_acc_easy": None if base_easy is None else round(base_easy, 4),
        "climb_easy_abs": round(climb_easy_abs, 4),
        "climb_easy_vs_scramble": round(climb_easy_vs_scramble, 4),
        "scramble_acc_easy": None if scr_easy is None else round(scr_easy, 4),
        "challenge_base_acc": None if chal_base is None else round(chal_base, 4),
        "climb_abs_aggregate": round(climb_abs, 4),
        "climb_vs_scramble_aggregate": round(climb_vs_scramble, 4),
        "leak_flag": bool(leak_flag),
        "climb_pass": bool(passed),
        "discriminator_fires_frac_matched_gt_0.10": round(frac_matched, 4),
        "arms_differ_verified": bool(arms_differ),
        "arm_store_hashes": arm_hashes,
        # --- human scale ---
        "grade_proxy": grade,
        "human_scale_statement": (
            f"Substrate science-knowledge baseline = {base:.3f} (~chance) = bottom of the human "
            f"scale (no science knowledge). Ingesting {M} ARC_Corpus science sentences moved "
            f"ARC-Easy to {('%.3f' % easy_full) if easy_full is not None else 'n/a'} "
            f"(proxy: {grade['easy_band']}), ARC-Challenge to "
            f"{('%.3f' % chal_full) if chal_full is not None else 'n/a'} (proxy: {grade['challenge_band']})."),
        # --- glass box ---
        "glassbox_examples": glass,
    }
    _write_metrics_atomic(output_dir, metrics)

    # persist store LOCAL-ONLY (uncommitted) for glass-box / reuse
    try:
        np.save(os.path.join(output_dir, "store_relevant_vectors.npy"), SV_rel)
        with open(os.path.join(output_dir, "store_relevant_sentences.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(relevant))
        with open(os.path.join(output_dir, "glassbox_examples.jsonl"), "w", encoding="utf-8") as f:
            for g in glass:
                f.write(json.dumps(g) + "\n")
    except Exception as e:  # persistence is best-effort; never mask the verdict
        print(f"[warn] store persist failed (non-fatal): {e}")

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"[verdict] {verdict}: {vmsg}")
    print(f"[curve] " + " ".join(f"{f}={curve[f]['acc']:.3f}" for f in sorted(curve)))
    print(f"[controls] random={ctrl_random:.3f} majority={ctrl_majority:.3f} chance={chance:.3f} "
          f"scramble={scr_acc['acc']:.3f} random_ingest={rand_acc['acc'] if rand_acc else None}")
    print(f"[human-scale] {metrics['human_scale_statement']}")
    print(f"[elapsed] {metrics['elapsed_s']}s")


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
