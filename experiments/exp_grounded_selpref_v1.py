"""exp_grounded_selpref_v1 -- GROUNDED-FEATURE selectional-preference verb channel (McRae 1998 /
Erk & Pado 2010 event-schema mechanism), replacing the convenient word-identity PPMI selpref arm
(SELPREF_WORDID, the existing build_selpref_cooc floor, ~0.148 rho on SimVerb at 15M HYPOTHESIZED@
data/exp_structured_context_learner_v1/metrics.json).

BRAIN MECHANISM (PINNED): a verb's meaning is the distribution over the FEATURES of its typical
argument fillers ("a chaser is animate/fast"), not the co-occurring word identities. Feature-based
selectional preference should GENERALIZE to unseen/rare fillers -- the diagnostic advantage over
sparse word-identity counts.

PRIOR-WORK CHECK (SUBSTRATE-KB / experiment_index discipline): this cell was scoped by the spawning
SOLVER, which named the exact reuse targets below; the McRae/selpref word-identity floor and the
DEP_TYPED context-shape lever were BOTH already built and landed in
exp_structured_context_learner_v1 (HARD_PASS-adjacent, see its metrics.json). This cell is NOT a
rediscovery of that result -- it swaps the FEATURE SPACE fillers are read through (word-identity ->
grounded sensorimotor / learned-embedding / thematic-role-normalized), which that cell did not test.

VERB REPRESENTATION (shared construction for all feature-based arms): verb row = per-ARGUMENT-ROLE
MEAN of its fillers' feature vectors; verb-verb similarity = cosine of the CONCATENATED per-role
centroids (roles: AGENT, PATIENT; L2-normalized after concat).

ARMS:
  SELPREF_WORDID    the floor -- build_selpref_cooc (REUSED VERBATIM, its own ARG_SLOTS) -> PPMI ->
                     SVD -> dense cosine. Word-IDENTITY selectional preference.
  SELPREF_GROUNDED  Q2, pure McRae: filler feature = grounded_vector(filler) (12-dim sensorimotor +
                     concreteness). AGENT = active nsubj. PATIENT = active dobj/obj UNION passive
                     nsubjpass (an unambiguous grammatical merge -- nsubjpass IS the patient
                     realized as subject; not voice-DETECTION, just label union).
  SELPREF_EMB       Q2 higher-dim variant (12-dim grounded may ceiling): filler feature = that
                     word's DEP_TYPED SVD embedding (build_typed_cooc+ppmi_matrix+svd_vectors,
                     REUSED from exp_structured_context_learner_v1, same 15M-token cache). Same
                     AGENT/PATIENT slots as SELPREF_GROUNDED.
  SELPREF_THEMATIC  Q1 layered on Q2/grounded: SELPREF_GROUNDED's slots, PLUS AGENT also recovers
                     the demoted agent of a passive by-phrase (spacy: token with dep_='agent' whose
                     head is the VERB names the 'by' marker; that marker's dep_='pobj' child is the
                     filler). This is the ONE genuinely voice-AWARE addition (nsubj vs by-object are
                     alternate surface realizations of the SAME thematic role depending on voice;
                     PATIENT's dobj/nsubjpass merge above needed no such detection). One-variable
                     vs SELPREF_GROUNDED: identical everything except this AGENT recovery.
INFO-FREE TWINS (grounded-feature arms only; must LOSE CI-separated):
  GROUNDED_SHUFFLE  SELPREF_GROUNDED, but every filler that WOULD have contributed a grounded vector
                     instead contributes a RANDOM OTHER grounded-covered filler's vector (same
                     occurrence counts, same slot structure, destroyed identity<->grounding link).
  ROLE_SHUFFLE      SELPREF_GROUNDED's slots, but per verb the AGENT+PATIENT filler multiset is
                     pooled and re-split into two groups of the ORIGINAL sizes at random (same
                     fillers, wrong roles).

SCORE on SimVerb (primary, verb-verb) + SimLex (context only, mixed-POS, low verb-table coverage
expected). GATE: paired bootstrap Delta-rho (paired_delta, matched population per pair of arms
compared -- the higher-power test the baseline module itself uses) of each candidate vs WORDID and
vs the two twins, CI-separated (lower bound of the 95% paired-delta CI > 0).

GENERALIZATION TEST (the decisive McRae discriminator): among SimVerb pairs both WORDID and a
candidate arm cover, split by pair_freq = min(corpus_freq(w1), corpus_freq(w2)) at the median into
RARE / FREQUENT halves. Report each arm's own-coverage rho on the RARE half and the WORDID-vs-
candidate paired delta restricted to RARE pairs -- feature-based arms should win MORE where
word-identity has the least data.

PASS band (informal pre-reg, embedded per hd-instrument convention): HARD_PASS if >=1 of
{SELPREF_GROUNDED, SELPREF_EMB, SELPREF_THEMATIC} beats SELPREF_WORDID CI-separated on SimVerb AND
beats both info-free twins CI-separated. MIDDLE_BAND if a candidate beats WORDID but not both twins,
or beats WORDID within <5% of its own CI half-width of zero. RIGOROUS_NEGATIVE if no candidate beats
WORDID CI-separated -- report plainly with the likely reason (12-dim grounded ceiling, thin filler
coverage, etc), do not force a positive framing.

Deterministic seed (SEED=13, matches the baseline module). ASCII-only. Writes only to its own data
dir (data/exp_grounded_selpref_v1/). Reads the 15M-token parse cache and reuses functions from
exp_structured_context_learner_v1 READ-ONLY (imports only; hdlab/ and that module are not modified).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# REUSE verbatim (read-only imports; hdlab/ and the structured-context cell are never modified).
from experiments.exp_structured_context_learner_v1 import (
    load_parsed, token_sents, build_vocab, benchmark_vocab, build_selpref_cooc,
    build_typed_cooc, ppmi_matrix, svd_vectors, dense_vec_cosine_fn, paired_delta,
)
from experiments.exp_learn_from_reading_strong_arm_v1 import (
    load_simverb, load_simlex, score_arm, covered_pairs, PPMI_ALPHA, SVD_K, SVD_P,
)
from hdlab.grounded_similarity import grounded_vector

ANCHOR = "grounded_selpref_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_" + ANCHOR)
STRUCTURED_CACHE_DIR = os.path.join(_REPO, "data", "exp_structured_context_learner_v1")  # READ-ONLY
SEED = 13
ROLES = ("AGENT", "PATIENT")


# ------------------------------------------------------------------------------- crash diagnostic
def _write_crash_metrics(exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR,
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(diag, fh, indent=2)
    os.replace(tmp, final)


# ------------------------------------------------------------------------------- slot extraction
def collect_verb_slot_fillers(parsed, word_index, add_by_phrase_agent=False):
    """verb(lower) -> {'AGENT': [filler,...], 'PATIENT': [filler,...]}, restricted to verb+filler
    both in word_index (same population discipline as build_selpref_cooc/build_typed_cooc).
    PATIENT always merges active dobj/obj with passive nsubjpass (an unambiguous grammatical-role
    merge -- nsubjpass IS the patient realized as subject; no voice DETECTION needed). AGENT is
    active nsubj by default; when add_by_phrase_agent=True (the THEMATIC arm) it additionally
    recovers the demoted agent of a passive by-phrase: spacy marks the 'by' token dep_='agent'
    (head = the VERB), and that marker's own dep_='pobj' child is the filler. This is the one
    genuinely voice-AWARE addition layered on top of the grounded construction (Q1 on Q2)."""
    out = {}
    for s in parsed:
        n = len(s)
        by_mark_verb = {}
        if add_by_phrase_agent:
            for i, (tok, head, rel, upos) in enumerate(s):
                base = rel.split(":")[0]
                if base == "agent" and 0 <= head < n and s[head][3] == "VERB":
                    by_mark_verb[i] = s[head][0]
        for i, (tok, head, rel, upos) in enumerate(s):
            base = rel.split(":")[0]
            if add_by_phrase_agent and base == "pobj" and head in by_mark_verb:
                verb = by_mark_verb[head]
                if verb in word_index and tok in word_index:
                    out.setdefault(verb, {}).setdefault("AGENT", []).append(tok)
                continue
            if not (0 <= head < n) or s[head][3] != "VERB":
                continue
            verb = s[head][0]
            if verb not in word_index or tok not in word_index:
                continue
            if base == "nsubj":
                out.setdefault(verb, {}).setdefault("AGENT", []).append(tok)
            elif base in ("dobj", "obj", "nsubjpass"):
                out.setdefault(verb, {}).setdefault("PATIENT", []).append(tok)
    return out


def build_role_shuffle_slots(slot_fillers, rng):
    """Per verb: pool AGENT+PATIENT fillers, shuffle, re-split at the ORIGINAL slot sizes. Same
    filler multiset per verb, same slot sizes, wrong role assignment."""
    out = {}
    for verb in sorted(slot_fillers.keys()):
        slots = slot_fillers[verb]
        agent = list(slots.get("AGENT", []))
        patient = list(slots.get("PATIENT", []))
        pool = agent + patient
        idx = np.arange(len(pool))
        rng.shuffle(idx)
        shuf = [pool[i] for i in idx]
        out[verb] = {"AGENT": shuf[:len(agent)], "PATIENT": shuf[len(agent):]}
    return out


# ------------------------------------------------------------------------------- feature spaces
def grounded_feat(word):
    v = grounded_vector(word)
    return None if v is None else v.numpy().astype(np.float64)


def make_emb_feat(index, vecs):
    def feat(word):
        i = index.get(word)
        return None if i is None else vecs[i].astype(np.float64)
    return feat


def make_shuffled_grounded_feat(rng, pool_words):
    """Deterministic pool of grounded-covered filler words. On each call, if `word` itself WOULD
    have contributed a grounded vector, return a RANDOM OTHER pool word's grounded vector instead
    (same contributing occurrences as SELPREF_GROUNDED, destroyed identity<->grounding link). If
    `word` has no grounded vector it contributes nothing here either (matches SELPREF_GROUNDED)."""
    pool_vecs = [grounded_vector(w).numpy().astype(np.float64) for w in pool_words]
    n = len(pool_vecs)

    def feat(word):
        if n == 0 or grounded_vector(word) is None:
            return None
        j = int(rng.integers(0, n))
        return pool_vecs[j]
    return feat


# ------------------------------------------------------------------------------- verb vectors
def verb_role_vectors(slot_fillers, feat_fn, roles=ROLES):
    """verb -> L2-normalized concat of per-role MEAN filler-feature vectors. A role with zero
    covered fillers contributes a zero block (same feature dim as whichever role has data)."""
    out = {}
    for verb in sorted(slot_fillers.keys()):
        slots = slot_fillers[verb]
        parts = []
        any_data = False
        dim_hint = None
        for r in roles:
            vecs = []
            for f in slots.get(r, []):
                v = feat_fn(f)
                if v is not None:
                    vecs.append(v)
            if vecs:
                any_data = True
                dim_hint = vecs[0].shape[0]
                parts.append(np.mean(np.stack(vecs), axis=0))
            else:
                parts.append(None)
        if not any_data:
            continue
        parts = [p if p is not None else np.zeros(dim_hint) for p in parts]
        vec = np.concatenate(parts)
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        out[verb] = vec
    return out


def dict_cosine_fn(table):
    def sim(w1, w2):
        a = table.get(w1)
        b = table.get(w2)
        if a is None or b is None:
            return None
        na = float(np.linalg.norm(a))
        nb = float(np.linalg.norm(b))
        if na < 1e-9 or nb < 1e-9:
            return None
        return float(np.dot(a, b) / (na * nb))
    return sim


def _table_signature(table):
    h = hashlib.sha256()
    for w in sorted(table.keys()):
        h.update(w.encode("utf-8"))
        h.update(np.round(np.asarray(table[w], dtype=np.float64), 6).tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------------------- checkpointed heavy builds
def _cache_path(name, ntok, vocab_n):
    return os.path.join(OUTPUT_DIR, "_cache_%s_tok%d_v%d.npz" % (name, ntok, vocab_n))


def cached_svd(name, cooc, ntok, vocab_n, seed=SEED):
    """PPMI+SVD with an npz checkpoint keyed by (name, n_tokens, vocab_size) under OUTPUT_DIR --
    resilience for the two expensive builds (WORDID's selpref cooc, EMB's dep_typed cooc) so a
    second foreground attempt after a timeout resumes instantly instead of recomputing."""
    path = _cache_path(name, ntok, vocab_n)
    if os.path.exists(path):
        d = np.load(path)
        print("[cache] HIT %s" % path, flush=True)
        return d["vecs"]
    vecs = svd_vectors(ppmi_matrix(cooc), seed=seed)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = path + ".tmp"
    # np.savez APPENDS ".npz" to string paths that don't already end in ".npz" -- passing an open
    # file OBJECT (not a string) suppresses that so the on-disk name matches `tmp` exactly and the
    # subsequent os.replace(tmp, path) finds it.
    with open(tmp, "wb") as fh:
        np.savez(fh, vecs=vecs)
    os.replace(tmp, path)
    print("[cache] WROTE %s" % path, flush=True)
    return vecs


# ------------------------------------------------------------------------------- generalization split
def median_split_by_freq(rows, common, freq):
    """common: set of row indices covered by the population under test. pair_freq = min(freq of
    w1, freq of w2) (the bottleneck word -- word-identity approaches are limited by the sparser
    side of the pair). Median split -> (rare_idx, freq_idx, median)."""
    pf = {}
    for k in common:
        w1, w2 = rows[k][0], rows[k][1]
        pf[k] = min(freq.get(w1, 0), freq.get(w2, 0))
    if not pf:
        return set(), set(), None
    vals = sorted(pf.values())
    median = vals[len(vals) // 2]
    rare = {k for k, v in pf.items() if v < median}
    freqy = {k for k, v in pf.items() if v >= median}
    return rare, freqy, median


def pairwise_common(rows, fn_a, fn_b):
    return covered_pairs(rows, fn_a) & covered_pairs(rows, fn_b)


# ------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--tokens", type=int, default=None)
    ap.add_argument("--timeout", type=float, default=None, help="unused by this cell; accepted for queue-runner compatibility")
    args = ap.parse_args()

    if args.mode == "smoke":
        max_tokens = args.tokens or 300_000
        vocab_cap, min_count, n_boot, n_null = 8_000, 3, 200, 200
    else:
        max_tokens = args.tokens or 15_000_000
        vocab_cap, min_count, n_boot, n_null = 60_000, 8, 500, 500

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cache_path = os.path.join(STRUCTURED_CACHE_DIR, "parsed_simplewiki_%dtok.jsonl" % max_tokens)
    if not os.path.exists(cache_path):
        raise SystemExit(
            "MISSING PARSE CACHE %s -- this cell REUSES the structured-context cell's cache "
            "read-only and does not parse; pick --tokens matching an existing cache file." % cache_path)

    t0 = time.time()
    parsed, ntok = load_parsed(cache_path, max_tokens)
    toks = token_sents(parsed)
    print("[load] %d sentences / %d tokens" % (len(parsed), ntok), flush=True)

    freq = Counter(t for s in toks for t in s)

    benches = {"simverb": load_simverb(), "simlex": load_simlex()}
    force = set().union(*(benchmark_vocab(r) for r in benches.values()))
    index = build_vocab(toks, force, vocab_cap, min_count)
    print("[vocab] %d words" % len(index), flush=True)

    # ---- arm: SELPREF_WORDID (existing floor, REUSED verbatim) ----
    selpref_cooc, n_sp = build_selpref_cooc(parsed, index)
    wordid_vecs = cached_svd("wordid", selpref_cooc, ntok, len(index))
    wordid_fn = dense_vec_cosine_fn(wordid_vecs, index)
    print("[build] SELPREF_WORDID cols=%d" % n_sp, flush=True)

    # ---- feature space for SELPREF_EMB: DEP_TYPED SVD embeddings (REUSED build) ----
    dep_typed_cooc, n_typed = build_typed_cooc(parsed, index, typed=True)
    emb_vecs = cached_svd("emb", dep_typed_cooc, ntok, len(index))
    emb_feat = make_emb_feat(index, emb_vecs)
    print("[build] DEP_TYPED (for SELPREF_EMB) cols=%d" % n_typed, flush=True)

    # ---- slot extraction: naive (nsubj / dobj+obj+nsubjpass) and thematic (+ by-phrase agent) ----
    naive_slots = collect_verb_slot_fillers(parsed, index, add_by_phrase_agent=False)
    thematic_slots = collect_verb_slot_fillers(parsed, index, add_by_phrase_agent=True)
    n_verbs_naive = len(naive_slots)
    n_verbs_thematic = len(thematic_slots)
    n_by_agent_verbs = sum(1 for v, sl in thematic_slots.items()
                            if len(sl.get("AGENT", [])) > len(naive_slots.get(v, {}).get("AGENT", [])))
    print("[slots] naive verbs=%d thematic verbs=%d verbs_gaining_by_agent=%d"
          % (n_verbs_naive, n_verbs_thematic, n_by_agent_verbs), flush=True)

    grounded_table = verb_role_vectors(naive_slots, grounded_feat)
    emb_table = verb_role_vectors(naive_slots, emb_feat)
    thematic_table = verb_role_vectors(thematic_slots, grounded_feat)

    filler_pool = sorted({f for slots in naive_slots.values() for fl in slots.values() for f in fl
                          if grounded_vector(f) is not None})
    shuffled_feat = make_shuffled_grounded_feat(np.random.default_rng(SEED + 11), filler_pool)
    grounded_shuffle_table = verb_role_vectors(naive_slots, shuffled_feat)

    role_shuffled_slots = build_role_shuffle_slots(naive_slots, np.random.default_rng(SEED + 17))
    role_shuffle_table = verb_role_vectors(role_shuffled_slots, grounded_feat)

    print("[tables] grounded=%d emb=%d thematic=%d gshuffle=%d rshuffle=%d filler_pool=%d"
          % (len(grounded_table), len(emb_table), len(thematic_table),
             len(grounded_shuffle_table), len(role_shuffle_table), len(filler_pool)), flush=True)

    # ---- META_RULE_AF-style arms-must-differ check (dict-shaped tables: signature hash) ----
    sigs = {
        "SELPREF_GROUNDED": _table_signature(grounded_table),
        "SELPREF_EMB": _table_signature(emb_table),
        "SELPREF_THEMATIC": _table_signature(thematic_table),
        "GROUNDED_SHUFFLE": _table_signature(grounded_shuffle_table),
        "ROLE_SHUFFLE": _table_signature(role_shuffle_table),
    }
    names = sorted(sigs.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert sigs[a] != sigs[b], "META_RULE_AF VIOLATION: %s and %s bit-identical tables" % (a, b)
    print("[arms_differ] verified: %s" % ", ".join(names), flush=True)

    arms = {
        "SELPREF_WORDID": wordid_fn,
        "SELPREF_GROUNDED": dict_cosine_fn(grounded_table),
        "SELPREF_EMB": dict_cosine_fn(emb_table),
        "SELPREF_THEMATIC": dict_cosine_fn(thematic_table),
        "GROUNDED_SHUFFLE": dict_cosine_fn(grounded_shuffle_table),
        "ROLE_SHUFFLE": dict_cosine_fn(role_shuffle_table),
    }

    # ---- discriminator-fires gate: SimVerb coverage must be non-trivial for the 4 real arms ----
    for nm in ("SELPREF_WORDID", "SELPREF_GROUNDED", "SELPREF_EMB", "SELPREF_THEMATIC"):
        cov = len(covered_pairs(benches["simverb"], arms[nm]))
        if cov < 20:
            raise SystemExit("DISCRIMINATOR_DID_NOT_FIRE: arm %s covers only %d SimVerb pairs (<20)" % (nm, cov))

    # ---- score every arm on both benchmarks, own coverage + coverage common across the 4 real arms
    core = ["SELPREF_WORDID", "SELPREF_GROUNDED", "SELPREF_EMB", "SELPREF_THEMATIC"]
    scored = {}
    common_sets = {}
    for bn, rows in benches.items():
        common = None
        for nm in core:
            cov = covered_pairs(rows, arms[nm])
            common = cov if common is None else (common & cov)
        common = common or set()
        common_sets[bn] = common
        res = {"n_common_core": len(common), "arms": {}}
        for nm, fn in arms.items():
            res["arms"][nm] = {
                "common_core": score_arm(rows, fn, restrict_pairs=common, n_boot=n_boot, n_null=n_null, seed=SEED),
                "own": score_arm(rows, fn, restrict_pairs=None, n_boot=n_boot, n_null=n_null, seed=SEED),
            }
        scored[bn] = res
        for nm in arms:
            r = res["arms"][nm]["own"]
            print("[%s] %s own_rho=%s n=%s coverage=%.3f" %
                  (bn, nm, ("%.4f" % r["rho"]) if r["rho"] is not None else "NA", r["n"], r["coverage"]),
                  flush=True)

    # ---- main gate: paired delta on SimVerb, maximal fair (pairwise) population per comparison ----
    simverb_rows = benches["simverb"]
    gates = {}
    for cand in ("SELPREF_GROUNDED", "SELPREF_EMB", "SELPREF_THEMATIC"):
        fn = arms[cand]
        d_wordid = paired_delta(simverb_rows, pairwise_common(simverb_rows, fn, arms["SELPREF_WORDID"]),
                                 fn, arms["SELPREF_WORDID"], n_boot, SEED + 42)
        entry = {"vs_WORDID": d_wordid, "beats_wordid": bool(d_wordid and d_wordid["separated_above"])}
        if cand in ("SELPREF_GROUNDED", "SELPREF_THEMATIC"):
            d_gshuf = paired_delta(simverb_rows, pairwise_common(simverb_rows, fn, arms["GROUNDED_SHUFFLE"]),
                                    fn, arms["GROUNDED_SHUFFLE"], n_boot, SEED + 43)
            d_rshuf = paired_delta(simverb_rows, pairwise_common(simverb_rows, fn, arms["ROLE_SHUFFLE"]),
                                    fn, arms["ROLE_SHUFFLE"], n_boot, SEED + 44)
            entry["vs_GROUNDED_SHUFFLE"] = d_gshuf
            entry["vs_ROLE_SHUFFLE"] = d_rshuf
            entry["beats_gshuf"] = bool(d_gshuf and d_gshuf["separated_above"])
            entry["beats_rshuf"] = bool(d_rshuf and d_rshuf["separated_above"])
            entry["pass"] = entry["beats_wordid"] and entry["beats_gshuf"] and entry["beats_rshuf"]
        else:
            entry["twin_gate_note"] = "SELPREF_EMB has no requested info-free twin; gated vs WORDID only"
            entry["pass"] = entry["beats_wordid"]
        gates[cand] = entry
        print("[gate] %s: %s" % (cand, entry), flush=True)

    any_pass = any(gates[c]["pass"] for c in gates)

    # ---- generalization test: RARE vs FREQUENT SimVerb pairs by min(corpus_freq(w1),freq(w2)) ----
    generalization = {}
    for cand in ("SELPREF_GROUNDED", "SELPREF_EMB", "SELPREF_THEMATIC"):
        fn = arms[cand]
        pop = pairwise_common(simverb_rows, fn, arms["SELPREF_WORDID"])
        rare, freqy, median = median_split_by_freq(simverb_rows, pop, freq)
        rec = {"median_pair_freq": median, "n_rare": len(rare), "n_freq": len(freqy)}
        for half_name, half in (("RARE", rare), ("FREQUENT", freqy)):
            rec[half_name] = {
                cand: score_arm(simverb_rows, fn, restrict_pairs=half, n_boot=n_boot, n_null=n_null, seed=SEED),
                "SELPREF_WORDID": score_arm(simverb_rows, arms["SELPREF_WORDID"], restrict_pairs=half,
                                             n_boot=n_boot, n_null=n_null, seed=SEED),
            }
            d = paired_delta(simverb_rows, half, fn, arms["SELPREF_WORDID"], n_boot, SEED + 51)
            rec[half_name]["paired_delta_vs_wordid"] = d
        generalization[cand] = rec
        print("[generalization] %s median_freq=%s n_rare=%d n_freq=%d rare_delta=%s freq_delta=%s"
              % (cand, median, len(rare), len(freqy),
                 rec["RARE"]["paired_delta_vs_wordid"], rec["FREQUENT"]["paired_delta_vs_wordid"]), flush=True)

    if any_pass:
        verdict = "HARD_PASS_GROUNDED_SELPREF_BEATS_WORDID_CISEP" if any(
            gates[c]["pass"] and gates[c].get("beats_gshuf", True) and gates[c].get("beats_rshuf", True)
            for c in gates) else "MIDDLE_BAND_BEATS_WORDID_ONLY"
    else:
        verdict = "RIGOROUS_NEGATIVE_NO_GROUNDED_ARM_BEATS_WORDID_CISEP"

    metrics = {
        "anchor_name": ANCHOR, "mode": args.mode, "n_tokens": ntok, "vocab": len(index),
        "verdict": verdict,
        "verdict_msg": "gates=%s" % json.dumps({c: gates[c]["pass"] for c in gates}),
        "summary": verdict,
        "context_cols": {"selpref_wordid": n_sp, "dep_typed_for_emb": n_typed},
        "verb_tables": {"naive": n_verbs_naive, "thematic": n_verbs_thematic,
                        "verbs_gaining_by_agent": n_by_agent_verbs, "grounded": len(grounded_table),
                        "emb": len(emb_table), "thematic_tbl": len(thematic_table),
                        "grounded_shuffle": len(grounded_shuffle_table), "role_shuffle": len(role_shuffle_table),
                        "filler_pool_grounded_covered": len(filler_pool)},
        "config": {"ppmi_alpha": PPMI_ALPHA, "svd_k": SVD_K, "svd_p": SVD_P, "vocab_cap": vocab_cap,
                  "min_count": min_count, "n_boot": n_boot, "n_null": n_null, "seed": SEED,
                  "roles": list(ROLES), "grounded_feature_dim": 12, "emb_feature_dim": SVD_K},
        "scored": scored, "gates": gates, "generalization": generalization,
        "elapsed_s": round(time.time() - t0, 1),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print("[verdict] %s | %.0fs" % (verdict, time.time() - t0), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise
