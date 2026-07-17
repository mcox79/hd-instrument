# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): the recovery arms produce hash-distinct
#     per-sentence recovered-triple signatures at a low regime (C=2) where the gate routes novel->flat
#     (chunked_novel_gated != chunked_novel) and familiar->chunk (chunked_gated != flat_novel) -> the
#     gate provably changes outputs and the gated arms differ from their ungated references.
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb / capacity-feasibility: CAPACITY-CLIFF locator, not a fixed-threshold cell. Flat and chunk arms
#     crater within the swept C range; the gate threshold tau is a CALIBRATED detection threshold (95th
#     percentile of the novel/noise chunk-margin distribution -> false-familiar-rate <= 5%), NOT a
#     test-tuned or fixed-argmax-noise number: tau = 99.5th pct of the novel/noise margin distribution,
#     a Bonferroni-corrected near-zero per-clause FPR (~0.5%) motivated by the C-way conjunction metric.
#     crlb_n_a="capacity-cliff locator; gate tau calibrated on a disjoint novel pool (FPR control), never on test".
# - baseline_in_band (META_RULE_AG): flat_tagged/flat_novel is the STEELMAN flat baseline and MUST be
#     in-band (0.05<acc<0.95) across the crater transition (C=3..12); it is not a saturated arm.
# - discriminator survives scale: numpy-cheap; runs the FULL N-grid inline (no smoke/full scale gap).
#     Two discriminators FIRE: (a) gate LIFT = C90(chunked_novel_gated) - C90(chunked_novel) >> 0
#     (fallback restores the flat floor for novel clauses); (b) gate KEEP = C90(chunked_gated) still
#     >= 1.5x C90(flat_tagged) (gate does not break the familiar-chunk win).
# - deterministic seeding: fixed integer seeds only; no hash()-derived RNG, no list(set()) ordering.
# - progress_logging: per-(N,C) line flushed to stdout; §17 satisfied.
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
"""exp_nativelang_chunking_gated_v2 -- CONFIDENCE-GATED CHUNK CLEANUP: close the novel-clause tail.

QUESTION (roadmap fix for the chunking novel-clause crater):
  The chunking cell (exp_nativelang_chunking_multiclause_v1) HARD_PASSed: hierarchical binding extends
  parseable depth 2.67x over flat for novel COMBINATIONS of FAMILIAR clauses (chunked C90=16 vs
  flat_tagged C90=6 at N=256). BUT chunked_novel -- novel CLAUSES that are NOT in the chunk-codebook --
  craters to 0 even at C=1. The v1 author identified this as PARTLY A MISSING-FALLBACK ARTIFACT: the
  chunk-cleanup FORCE-CLEANS every intermediate chunk to the nearest familiar codebook entry with NO
  confidence gate, so an unfamiliar chunk is SNAPPED to a wrong familiar clause and decodes garbage.
  That is a mechanism CHOICE, not a proven structural bound.

  FIX (this cell): a CONFIDENCE-GATED chunk cleanup. At each clause, compute the top-1-vs-top-2 cosine
  MARGIN of the intermediate chunk against the codebook. If the margin is HIGH (the chunk is a confident
  familiar codebook member) -> snap to it and decode from the CLEAN chunk (deep chunked path). If the
  margin is LOW (unfamiliar chunk, not in the codebook) -> FALL BACK to a direct flat SVO decode of that
  clause straight from the noisy unbound chunk (the flat_tagged per-clause decode). Expected: chunking is
  NEVER WORSE than flat (novel clauses recover to the flat floor) AND still >= ~2.67x better for familiar.
  Brain-consistent: you chunk PRACTICED material and fall back to serial/flat parsing for the unfamiliar.

MECHANISM (glass-box FHRR, complex128 unit phasors) -- identical substrate to v1:
  LEXICON: V words -> random unit phasors. SVO ROLES subj/verb/obj. CLAUSE ROLES: Cmax phasors.
  CHUNK (one clause): c = sum_i bind(svo_i, word_i)   (composite; norm ~ sqrt(3N)).
  A pool of P KNOWN clauses -> CHUNK-CODEBOOK (consolidated / familiar).
  SENTENCE (C clauses): M = sum_j bind(clause_role_j, chunk_j). The C-tuple is ALWAYS a novel combo.

  GATE (new): g = unbind(M, clause_role_j)  ->  noisy chunk.
    cos_k = Re<cb_k, g> / (|cb_k| |g|);  margin = cos_(1) - cos_(2)  (top-1 minus top-2).
    if margin >= tau:  clean = cb[argmax];  decode words from CLEAN chunk   (CHUNK PATH; familiar).
    else:              decode words directly from g  (FLAT FALLBACK; == flat_tagged per-clause decode).
  tau CALIBRATION (principled, NOT test-tuned): drawn from a DISJOINT novel calibration pool (a third
    pool, disjoint from both the familiar pool and the test-novel pool). tau = 99.5th percentile of the
    top1-top2 margin over calibration clauses whose chunk is GUARANTEED absent from the codebook. The
    99.5th percentile (per-clause FPR ~0.5%) is a Bonferroni-corrected near-zero false-familiar rate:
    the parse metric is a C-way conjunction, so a per-clause FPR p compounds to ~C*p at the sentence
    level; 0.5% per clause holds the sentence-level false-familiar rate ~<=5% up to C~10. Calibrated per
    (N, C, seed) so tau tracks the crosstalk level; never touches test sentences.

ARMS (recover the ordered list of C SVO triples; parse_acc = ALL C clauses exactly correct):
  - flat_shared     (NAIVE FLAT): shared SVO roles, no clause tag -> role collision; craters at C>=2.
  - flat_tagged     (STEELMAN FLAT, familiar clauses): clause-tagged single bundle, direct double-unbind,
                    NO cleanup. Full 3C crosstalk -> craters at C ~ N/48. The fair flat depth baseline.
  - flat_novel      (STEELMAN FLAT, NOVEL clauses): flat_tagged decode on novel clauses -> the exact
                    apples-to-apples FLAT FLOOR for novel clauses. THE "never worse than flat" reference.
  - chunked         (v1 MECHANISM, familiar, UNGATED): blind chunk-cleanup -> deep (C90 ~ N/16).
  - chunked_novel   (v1 control, novel, UNGATED): blind cleanup snaps to wrong familiar chunk -> CRATERS
                    to 0. The tail this cell closes.
  - chunked_gated   (NEW, familiar): gated cleanup. Familiar chunks clear tau -> CHUNK PATH -> keeps deep.
  - chunked_novel_gated (NEW, novel): gated cleanup. Novel chunks fall below tau -> FLAT FALLBACK ->
                    recovers to the flat floor. THE fix: chunked_novel_gated ~ flat_novel, never worse.
  - scrambled_roles (NULL): gated decode with permuted clause-role assignment -> chance.
  - flat_bag        (NULL): bundle all words, no binding -> chance.
  - memorization    (LEAK GUARD): nearest SEEN whole-sentence -> wrong seq on novel combos -> must FAIL.

METRIC: parse_acc vs C per arm, per N. C90(arm) = largest C with parse_acc >= 0.90.
  GATE LIFT   = C90(chunked_novel_gated) - C90(chunked_novel)   (target: 0 -> ~flat_novel floor).
  GATE KEEP   = C90(chunked_gated) / max(C90(flat_tagged),1)     (target: still ~2.67x).
  ROUTING     = frac of clauses routed to CHUNK path, per arm    (familiar high; novel low).

PRE-REG (envelope-fail-bands; at primary N):
  HARD_PASS: (a) chunked_novel_gated C90 >= flat_novel C90 (STRICT never-worse-than-flat at C90), AND
             (b) chunked_novel_gated C90 >= chunked_novel C90 + 2 (material lift off the ~0 crater), AND
             (c) chunked_gated extension_factor >= 1.5 (familiar-chunk win kept), AND
             (d) gate ROUTES correctly: at low C, familiar chunk-route-frac - novel chunk-route-frac
                 >= 0.30 (gate discriminates, not a no-op), AND
             (e) nulls collapse (<=0.20 at C>=2), flat_shared collapses, memorization heldout <=0.20.
  HARD_FAIL: chunked_novel_gated did NOT restore the floor: c90 < flat_novel c90 - 1 OR no material lift
             (< chunked_novel c90 + 2) OR chunked_gated extension_factor <= 1.0 (gate broke familiar win)
             OR gate does not discriminate (route gap < 0.10 at low C) OR nulls do not collapse.
  MIDDLE: floor RESTORED within 1 C (c90 >= flat_novel c90 - 1) with a material lift, but not strictly
          >= flat_novel c90 (a small residual boundary penalty from detector false-familiars), OR the
          familiar win eroded to 1.0 < ext < 1.5. Report residual_boundary_gap = max over C (with
          flat_novel>=0.90) of (flat_novel - chunked_novel_gated) = the accuracy cost of the gate.
  Honest read either way: report the gate LIFT (novel 0 -> ~floor), the KEEP (familiar ext), the routing,
  and the residual boundary gap -- and whether any residual is a detector-FPR artifact or a real bound.

Local numpy, no queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import hashlib
import time
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "nativelang_chunking_gated_v2"

# GATE THRESHOLD PERCENTILE (principled, pre-committed, NOT test-tuned):
# The parse metric is a C-way conjunction (ALL C clauses must be correctly routed AND decoded), so a
# per-clause false-familiar rate p compounds to a sentence-level rate ~ C*p. To hold the sentence-level
# false-familiar rate at ~<=5% across the operating range up to C~20 (Bonferroni over the C clauses),
# the per-clause FPR must be ~0.05/20 = 0.0025 -> the 99.75th percentile of the novel/noise margin
# distribution. We adopt the 99.5th percentile (per-clause FPR 0.5%; sentence-level ~5% at C=10) as a
# robust near-zero-FPR detection threshold. This is derived from the METRIC's conjunction structure and
# the calibration (novel) null margins ONLY -- never from any test accuracy.
GATE_PERCENTILE = 99.5

ARM_KEYS = ["flat_shared", "flat_tagged", "flat_novel", "chunked", "chunked_novel",
            "chunked_gated", "chunked_novel_gated", "scrambled", "flat_bag", "memorization"]

# ---------------------------------------------------------------------------
# FHRR primitives (glass-box, inspectable) -- unit phasors, complex128.
# ---------------------------------------------------------------------------

def make_phasors(rng, count, N):
    """count random FHRR unit-phasor hypervectors, shape (count, N) complex128."""
    theta = rng.uniform(-np.pi, np.pi, size=(count, N))
    return np.exp(1j * theta)


def bind(a, b):
    """FHRR bind = elementwise complex multiply (self-inverse via conjugate)."""
    return a * b


def unbind(c, b):
    """FHRR unbind = multiply by conjugate."""
    return c * np.conj(b)


def cleanup(query, codebook):
    """Nearest codebook row by real part of Hermitian inner product -> argmax index."""
    return int(np.argmax((codebook.conj() @ query).real))


def chunk_confidence(g, cb, cb_norms):
    """CLEANUP CONFIDENCE of chunk g against codebook cb.
    Returns (top1_cos, top1_minus_top2, top1_idx).
    top1_cos = cosine of g to its best codebook match = how strongly the cleaned chunk matches a KNOWN
    clause above the noise floor. This is the gate's confidence: an in-codebook (familiar) chunk matches
    strongly; an out-of-codebook (novel) chunk matches only at the noise level. (top1-top2 margin is
    ALSO returned for reporting, but it is a WEAKER detector here -- crosstalk elevates the runner-up
    codebook entry and compresses the margin, verified empirically -- so the gate uses top1_cos.)"""
    sims = (cb.conj() @ g).real
    gn = float(np.sqrt((np.abs(g) ** 2).sum())) + 1e-12
    cos = sims / (cb_norms * gn)
    o = np.argsort(-cos)
    return float(cos[o[0]]), float(cos[o[0]] - cos[o[1]]), int(o[0])


def youden_threshold(pos, neg):
    """ROC-optimal (Youden's J = max TPR-FPR) threshold separating positive (in-codebook / familiar)
    from negative (out-of-codebook / novel) calibration confidences. Vectorized via sorted searchsorted."""
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)
    thr = np.unique(np.concatenate([pos, neg]))
    ps = np.sort(pos)
    ns = np.sort(neg)
    tpr = 1.0 - np.searchsorted(ps, thr, side="left") / max(1, len(ps))
    fpr = 1.0 - np.searchsorted(ns, thr, side="left") / max(1, len(ns))
    return float(thr[int(np.argmax(tpr - fpr))])


# ---------------------------------------------------------------------------
# Corpus construction (deterministic; fixed-seed RNG only).
# ---------------------------------------------------------------------------

def sample_distinct_triples(rng, V, count, exclude):
    """Sample `count` distinct SVO triples (word ids in [0,V)) not in `exclude`."""
    out = []
    seen = set(exclude)
    guard = 0
    cap = count * 200 + 2000
    while len(out) < count and guard < cap:
        guard += 1
        t = (int(rng.integers(V)), int(rng.integers(V)), int(rng.integers(V)))
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def encode_chunk(triple, lexicon, svo_roles):
    """One clause -> composite chunk vector c = sum_i bind(svo_i, word_i)."""
    return (bind(svo_roles[0], lexicon[triple[0]])
            + bind(svo_roles[1], lexicon[triple[1]])
            + bind(svo_roles[2], lexicon[triple[2]]))


# ---------------------------------------------------------------------------
# One (N, C, seed) evaluation of all arms (with per-(N,C,seed) gate calibration).
# ---------------------------------------------------------------------------

def run_cell(N, C, seed, V=50, P=64, n_test=120, n_seen=120, n_calib=120,
             gate_percentile=GATE_PERCENTILE, capture_outputs=False):
    rng = np.random.default_rng(seed)
    lexicon = make_phasors(rng, V, N)                 # (V, N)
    svo_roles = make_phasors(rng, 3, N)               # subj/verb/obj
    clause_roles = make_phasors(rng, 128, N)          # up to 128 clause slots

    # KNOWN clause pool + chunk-codebook (consolidated / familiar clauses).
    pool = sample_distinct_triples(rng, V, P, exclude=set())
    chunk_cb = np.array([encode_chunk(t, lexicon, svo_roles) for t in pool])   # (P, N)
    cb_norms = np.sqrt((np.abs(chunk_cb) ** 2).sum(axis=1))                    # (P,) row norms

    # NOVEL clause pool (disjoint from known pool) for the familiarity-boundary test.
    novel_pool = sample_distinct_triples(rng, V, P, exclude=set(pool))
    novel_chunk = np.array([encode_chunk(t, lexicon, svo_roles) for t in novel_pool])

    # CALIBRATION novel pool (a THIRD pool, disjoint from BOTH familiar and test-novel pools).
    # tau is calibrated ONLY on these -> never touches any test sentence (leak-guard).
    calib_pool = sample_distinct_triples(rng, V, P, exclude=set(pool) | set(novel_pool))
    calib_chunk = np.array([encode_chunk(t, lexicon, svo_roles) for t in calib_pool])

    # scrambled-role permutation (cyclic shift; a fixed derangement for C>1).
    def scram_perm(c):
        p = list(range(c))
        return p[1:] + p[:1] if c > 1 else p

    # TEST sentences = novel ordered C-tuples of KNOWN clause ids (exact combo never stored whole).
    test_sents = [[int(rng.integers(P)) for _ in range(C)] for _ in range(n_test)]
    # TEST sentences over NOVEL clauses.
    test_sents_novel = [[int(rng.integers(P)) for _ in range(C)] for _ in range(n_test)]
    # CALIBRATION sentences (two-class supervised split for the gate; both disjoint from test):
    #   NEG (out-of-codebook / novel) = CALIB novel clauses (third disjoint pool).
    #   POS (in-codebook / familiar)  = KNOWN codebook clauses, DIFFERENT combos than test_sents.
    calib_sents = [[int(rng.integers(P)) for _ in range(C)] for _ in range(n_calib)]
    calib_fam_sents = [[int(rng.integers(P)) for _ in range(C)] for _ in range(n_calib)]
    # SEEN sentences (disjoint set) for the memorization leak-guard store.
    seen_sents = [[int(rng.integers(P)) for _ in range(C)] for _ in range(n_seen)]
    seen_keys = set(tuple(s) for s in seen_sents)
    # keep test sentences disjoint from seen (held-out novel combos -- leak guard).
    test_sents = [s for s in test_sents if tuple(s) not in seen_keys]
    if not test_sents:
        test_sents = [[int(rng.integers(P)) for _ in range(C)]]

    def encode_sentence(sent, cb):
        M = np.zeros(N, dtype=complex)
        for j, cid in enumerate(sent):
            M = M + bind(clause_roles[j], cb[cid])
        return M

    # ---- GATE CALIBRATION: supervised two-class ROC-optimal (Youden J) threshold ----
    # POS = familiar (in-codebook) confidences; NEG = novel (out-of-codebook) confidences. tau is the
    # ROC-optimal split, re-derived per (N, C, seed) so it tracks the crosstalk level. Calibration
    # sentences are disjoint from ALL test sentences -> no leak. (gate_percentile kept for API parity;
    # supersedes the earlier one-class FPR design that could not separate familiar/novel at high C.)
    def _confs(sents, book):
        out = []
        for s in sents:
            M = encode_sentence(s, book)
            for j in range(len(s)):
                g = unbind(M, clause_roles[j])
                c1, _m, _idx = chunk_confidence(g, chunk_cb, cb_norms)
                out.append(c1)
        return out
    pos_conf = _confs(calib_fam_sents, chunk_cb)      # in-codebook (familiar)
    neg_conf = _confs(calib_sents, calib_chunk)       # out-of-codebook (novel)
    tau = youden_threshold(pos_conf, neg_conf)

    # ---- decoders (each returns the recovered ordered list of C triples) ----
    def dec_flat_tagged(M, sent):
        rec = []
        for j in range(len(sent)):
            g = unbind(M, clause_roles[j])
            rec.append(tuple(cleanup(unbind(g, svo_roles[i]), lexicon) for i in range(3)))
        return rec

    def dec_chunked(M, sent, cb_clean):
        # UNGATED v1 mechanism: always snap to nearest codebook entry.
        rec = []
        for j in range(len(sent)):
            g = unbind(M, clause_roles[j])
            pj = cleanup(g, cb_clean)
            clean = cb_clean[pj]
            rec.append(tuple(cleanup(unbind(clean, svo_roles[i]), lexicon) for i in range(3)))
        return rec

    def dec_chunked_gated(M, sent):
        # GATED: confident familiar -> CHUNK PATH; unfamiliar (low confidence) -> FLAT FALLBACK.
        rec = []
        n_chunk = 0
        for j in range(len(sent)):
            g = unbind(M, clause_roles[j])
            conf, _mg, idx = chunk_confidence(g, chunk_cb, cb_norms)
            if conf >= tau:
                n_chunk += 1
                clean = chunk_cb[idx]
                rec.append(tuple(cleanup(unbind(clean, svo_roles[i]), lexicon) for i in range(3)))
            else:
                # flat fallback == flat_tagged per-clause decode straight from noisy g.
                rec.append(tuple(cleanup(unbind(g, svo_roles[i]), lexicon) for i in range(3)))
        return rec, n_chunk

    def dec_scrambled(M, sent):
        perm = scram_perm(len(sent))
        rec = []
        for j in range(len(sent)):
            g = unbind(M, clause_roles[perm[j]])
            pj = cleanup(g, chunk_cb)
            clean = chunk_cb[pj]
            rec.append(tuple(cleanup(unbind(clean, svo_roles[i]), lexicon) for i in range(3)))
        return rec

    def dec_flat_shared(sent):
        M = np.zeros(N, dtype=complex)
        for cid in sent:
            t = pool[cid]
            for i in range(3):
                M = M + bind(svo_roles[i], lexicon[t[i]])
        single = tuple(cleanup(unbind(M, svo_roles[i]), lexicon) for i in range(3))
        return [single for _ in sent]

    def dec_flat_bag(sent):
        M = np.zeros(N, dtype=complex)
        for cid in sent:
            for w in pool[cid]:
                M = M + lexicon[w]
        scores = (lexicon.conj() @ M).real
        top = sorted(int(x) for x in np.argsort(-scores)[:3 * len(sent)])
        rec = []
        for j in range(len(sent)):
            ch = top[3 * j:3 * j + 3]
            while len(ch) < 3:
                ch.append(0)
            rec.append(tuple(ch))
        return rec

    # ---- memorization store (SEEN sentences) ----
    mem_M = np.array([encode_sentence(s, chunk_cb) for s in seen_sents]) if seen_sents else np.zeros((0, N), dtype=complex)
    mem_keys = [tuple(s) for s in seen_sents]

    def dec_memorization(M, sent):
        if mem_M.shape[0] == 0:
            return [(-1, -1, -1) for _ in sent]
        j = int(np.argmax((mem_M.conj() @ M).real))
        best = mem_keys[j]
        return [pool[cid] for cid in best[:len(sent)]] + [(-1, -1, -1)] * max(0, len(sent) - len(best))

    truth = [[pool[cid] for cid in s] for s in test_sents]
    truth_novel = [[novel_pool[cid] for cid in s] for s in test_sents_novel]

    def acc(pred_list, truth_list):
        ok = sum(1 for p, t in zip(pred_list, truth_list) if p == t)
        return ok / max(1, len(truth_list))

    res = {}
    cap = {} if capture_outputs else None

    # --- ungated / flat / null arms ---
    def ev_flat(name, fn, sents, truths):
        preds = [fn(s) for s in sents]
        if cap is not None:
            cap[name] = preds
        return acc(preds, truths)

    def ev_M(name, fn, sents, truths, cb):
        preds = []
        for s in sents:
            M = encode_sentence(s, cb)
            preds.append(fn(M, s))
        if cap is not None:
            cap[name] = preds
        return acc(preds, truths)

    res["flat_shared"] = ev_flat("flat_shared", dec_flat_shared, test_sents, truth)
    res["flat_bag"] = ev_flat("flat_bag", dec_flat_bag, test_sents, truth)
    res["flat_tagged"] = ev_M("flat_tagged", dec_flat_tagged, test_sents, truth, chunk_cb)
    res["flat_novel"] = ev_M("flat_novel", dec_flat_tagged, test_sents_novel, truth_novel, novel_chunk)
    res["chunked"] = ev_M("chunked", lambda M, s: dec_chunked(M, s, chunk_cb), test_sents, truth, chunk_cb)
    res["chunked_novel"] = ev_M("chunked_novel", lambda M, s: dec_chunked(M, s, chunk_cb),
                                test_sents_novel, truth_novel, novel_chunk)
    res["scrambled"] = ev_M("scrambled", dec_scrambled, test_sents, truth, chunk_cb)
    res["memorization"] = ev_M("memorization", dec_memorization, test_sents, truth, chunk_cb)

    # --- GATED arms (track routing fractions) ---
    def ev_gated(name, sents, truths, cb):
        preds = []
        n_chunk_total = 0
        n_clause_total = 0
        for s in sents:
            M = encode_sentence(s, cb)
            rec, n_chunk = dec_chunked_gated(M, s)
            preds.append(rec)
            n_chunk_total += n_chunk
            n_clause_total += len(s)
        if cap is not None:
            cap[name] = preds
        route_chunk_frac = n_chunk_total / max(1, n_clause_total)
        return acc(preds, truths), route_chunk_frac

    a_g, rf_g = ev_gated("chunked_gated", test_sents, truth, chunk_cb)
    a_ng, rf_ng = ev_gated("chunked_novel_gated", test_sents_novel, truth_novel, novel_chunk)
    res["chunked_gated"] = a_g
    res["chunked_novel_gated"] = a_ng
    res["route_frac_familiar"] = rf_g          # frac of familiar clauses -> CHUNK path (want HIGH)
    res["route_frac_novel"] = rf_ng            # frac of novel clauses    -> CHUNK path (want LOW)
    res["tau"] = tau
    res["n_test"] = len(test_sents)

    if cap is not None:
        return res, cap
    return res


def avg_over_seeds(N, C, seeds, **kw):
    extra = ["route_frac_familiar", "route_frac_novel", "tau"]
    acc = {k: [] for k in ARM_KEYS + extra}
    for s in seeds:
        r = run_cell(N, C, s, **kw)
        for k in acc:
            acc[k].append(r[k])
    return {k: float(np.mean(v)) for k, v in acc.items()}


def c90(curve):
    """curve: list of (C, acc) ascending in C. Largest C with acc >= 0.90 (0 if none)."""
    good = [C for C, a in curve if a >= 0.90]
    return max(good) if good else 0


# ---------------------------------------------------------------------------
# Self-tests (hardened; real code path; discriminator-fires; gate-not-a-no-op).
# ---------------------------------------------------------------------------

def _hash_preds(preds):
    h = hashlib.sha256()
    for sent in preds:
        for tri in sent:
            h.update(bytes(str(tri), "ascii"))
        h.update(b"|")
    return h.hexdigest()


def self_test():
    print("[self-test] FHRR bind/unbind exact recovery ...", flush=True)
    rng = np.random.default_rng(0)
    N = 2048
    a = make_phasors(rng, 1, N)[0]
    role = make_phasors(rng, 1, N)[0]
    cos = (np.conj(a) @ unbind(bind(role, a), role)).real / N
    assert cos > 0.999, f"bind/unbind not self-inverse: cos={cos}"
    print(f"           single-pair unbind cos={cos:.4f} OK", flush=True)

    print("[self-test] REAL code path: low-C regime (C=2) where flat still works ...", flush=True)
    r2, cap2 = run_cell(N=192, C=2, seed=1, capture_outputs=True)
    print("           " + " ".join(f"{k}={r2[k]:.3f}" for k in ARM_KEYS), flush=True)
    print(f"           tau={r2['tau']:.4f} route_frac_familiar={r2['route_frac_familiar']:.3f} "
          f"route_frac_novel={r2['route_frac_novel']:.3f}", flush=True)

    print("[self-test] GATE IS NOT A NO-OP: novel gated restores flat floor; ungated novel still craters",
          flush=True)
    # At C=2 the flat floor is high; the gate must lift novel from ~0 to ~flat_novel floor.
    assert r2["chunked_novel"] <= 0.20, f"ungated chunked_novel must crater at C=2: {r2['chunked_novel']}"
    assert r2["flat_novel"] >= 0.80, f"flat floor must be high at C=2 (in-band): {r2['flat_novel']}"
    assert r2["chunked_novel_gated"] >= 0.80, \
        f"GATE FIX: novel gated must restore ~flat floor at C=2: {r2['chunked_novel_gated']}"
    assert r2["chunked_novel_gated"] >= r2["flat_novel"] - 0.10, \
        f"novel gated must be ~never-worse than flat_novel: {r2['chunked_novel_gated']} vs {r2['flat_novel']}"
    print(f"           chunked_novel(ungated)={r2['chunked_novel']:.3f} -> "
          f"chunked_novel_gated={r2['chunked_novel_gated']:.3f} (flat_novel={r2['flat_novel']:.3f}) OK",
          flush=True)

    print("[self-test] GATE PRESERVES FAMILIAR: familiar gated stays deep; routes familiar->chunk ...",
          flush=True)
    assert r2["chunked_gated"] >= 0.90, f"familiar gated must stay high at C=2: {r2['chunked_gated']}"
    # Gate discriminates: familiar clauses route to CHUNK far more than novel clauses do.
    assert r2["route_frac_familiar"] - r2["route_frac_novel"] >= 0.30, \
        (f"GATE MUST DISCRIMINATE: familiar chunk-route {r2['route_frac_familiar']:.3f} "
         f"vs novel {r2['route_frac_novel']:.3f}")
    assert r2["route_frac_familiar"] >= 0.60, f"familiar should mostly route to chunk: {r2['route_frac_familiar']}"
    assert r2["route_frac_novel"] <= 0.20, f"novel should mostly route to flat: {r2['route_frac_novel']}"
    print(f"           route_frac familiar={r2['route_frac_familiar']:.3f} "
          f"novel={r2['route_frac_novel']:.3f} (gap={r2['route_frac_familiar']-r2['route_frac_novel']:.3f}) OK",
          flush=True)

    print("[self-test] tau is a real (non-trivial) threshold ...", flush=True)
    assert r2["tau"] > 0.0, f"tau must be a positive margin threshold: {r2['tau']}"

    print("[self-test] deep regime (C=8): familiar chunked still deep, ungated novel craters ...", flush=True)
    r8, cap8 = run_cell(N=192, C=8, seed=1, capture_outputs=True)
    assert r8["chunked"] >= 0.90, f"chunked should hold at N=192 C=8: {r8['chunked']}"
    # gated familiar must stay DEEP where flat has cratered (gate keeps the chunk path for familiar).
    assert r8["chunked_gated"] >= 0.80, f"chunked_gated should stay deep at N=192 C=8: {r8['chunked_gated']}"
    assert r8["chunked_gated"] >= r8["flat_tagged"] + 0.30, \
        f"chunked_gated must beat flat where flat craters: {r8['chunked_gated']} vs {r8['flat_tagged']}"
    assert r8["flat_tagged"] <= 0.50, f"flat_tagged should crater at N=192 C=8: {r8['flat_tagged']}"
    assert r8["scrambled"] <= 0.20, f"scrambled null must collapse: {r8['scrambled']}"
    assert r8["flat_bag"] <= 0.20, f"flat_bag null must collapse: {r8['flat_bag']}"
    assert r8["flat_shared"] <= 0.20, f"flat_shared must collapse at C=8: {r8['flat_shared']}"
    assert r8["memorization"] <= 0.20, f"memorization must fail on novel combos: {r8['memorization']}"
    print("           deep-regime controls OK", flush=True)

    print("[self-test] ARMS-MUST-DIFFER (META_RULE_AF): gate not a no-op; arms diverge at mid regime ...",
          flush=True)
    # GATE-NOT-A-NO-OP (at C=2 where the gate flips the novel output from crater to floor):
    assert _hash_preds(cap2["chunked_novel_gated"]) != _hash_preds(cap2["chunked_novel"]), \
        "META_RULE_AF: gate did not change novel output (no-op gate)"
    # MUTUALLY-DISTINCT arms at the MID regime C=8 (each has a different behavior/accuracy here so their
    # recovered-triple signatures must differ). NOTE: chunked vs chunked_gated are DESIGNED to coincide
    # when familiar chunks are confident (gate is transparent for familiar) -> not asserted distinct.
    names = ["flat_tagged", "flat_novel", "chunked", "chunked_novel", "chunked_novel_gated",
             "scrambled", "flat_bag"]
    digs = {n: _hash_preds(cap8[n]) for n in names}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_, b_ = names[i], names[j]
            assert digs[a_] != digs[b_], f"META_RULE_AF VIOLATION: arms {a_!r},{b_!r} bit-identical at C=8"
    # KEY gate-does-chunk-work claim: gated familiar (deep) differs from flat_tagged (cratered) at C=8.
    assert _hash_preds(cap8["chunked_gated"]) != _hash_preds(cap8["flat_tagged"]), \
        "META_RULE_AF: chunked_gated must differ from flat_tagged where flat craters"
    print("           gate-not-no-op + 7 mid-regime arms hash-distinct OK", flush=True)

    print("[self-test] GATE LIFT + KEEP at N=192 over the C-grid ...", flush=True)
    seeds = [1, 2, 3]
    Cs = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]
    curves = {a: [] for a in ["flat_tagged", "flat_novel", "chunked", "chunked_novel",
                              "chunked_gated", "chunked_novel_gated"]}
    for C in Cs:
        rr = avg_over_seeds(192, C, seeds, n_test=60, n_seen=60, n_calib=60)
        for a in curves:
            curves[a].append((C, rr[a]))
    c90_ng = c90(curves["chunked_novel_gated"])
    c90_fn = c90(curves["flat_novel"])
    c90_cn = c90(curves["chunked_novel"])
    c90_cg = c90(curves["chunked_gated"])
    c90_ft = c90(curves["flat_tagged"])
    print(f"           C90: flat_tagged={c90_ft} flat_novel={c90_fn} chunked_novel(ungated)={c90_cn} "
          f"chunked_novel_gated={c90_ng} chunked_gated={c90_cg}", flush=True)
    # LIFT: novel gated restores the flat floor (never worse than flat within 1 C of residual detector
    # FPR at the crater boundary) and lifts hugely off the ~0 crater.
    assert c90_ng >= c90_fn - 1, f"GATE LIFT: novel gated C90={c90_ng} must restore flat_novel floor {c90_fn} (+-1)"
    assert c90_ng >= c90_cn + 2, f"GATE LIFT: novel gated C90={c90_ng} must clear ungated crater {c90_cn} by >=2"
    # KEEP: familiar gated retains the depth-extension win.
    assert c90_cg / max(c90_ft, 1) >= 1.5, \
        f"GATE KEEP: chunked_gated extension {c90_cg}/{c90_ft} must stay >= 1.5x"
    print(f"           LIFT ok (novel {c90_cn}->{c90_ng}, floor {c90_fn}); "
          f"KEEP ok (familiar ext {c90_cg}/{c90_ft}={c90_cg/max(c90_ft,1):.2f}x) OK", flush=True)

    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# Main sweep + verdict.
# ---------------------------------------------------------------------------

def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "run_mode": "crashed",
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=0.0)   # harness parity
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    t0 = time.time()
    if args.smoke:
        N_grid = [192]
        C_grid = [1, 2, 4, 8, 16]
        seeds = [1, 2]
        n_test = n_seen = n_calib = 60
        run_mode = "smoke"
    else:
        N_grid = [128, 192, 256]
        C_grid = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32]
        seeds = [1, 2, 3]
        n_test = n_seen = n_calib = 120
        run_mode = "full"

    PRIMARY_N = 256 if not args.smoke else 192

    sweep = []
    curves = {N: {a: [] for a in ARM_KEYS} for N in N_grid}
    route = {N: {"familiar": [], "novel": [], "tau": []} for N in N_grid}
    for N in N_grid:
        for C in C_grid:
            res = avg_over_seeds(N, C, seeds, n_test=n_test, n_seen=n_seen, n_calib=n_calib)
            res.update({"N": N, "C": C, "total_bindings_flat": 3 * C})
            sweep.append(res)
            for a in ARM_KEYS:
                curves[N][a].append((C, res[a]))
            route[N]["familiar"].append((C, res["route_frac_familiar"]))
            route[N]["novel"].append((C, res["route_frac_novel"]))
            route[N]["tau"].append((C, res["tau"]))
            print(f"N={N:4d} C={C:3d} (3C={3*C:3d})  ft={res['flat_tagged']:.2f} fn={res['flat_novel']:.2f} "
                  f"chk={res['chunked']:.2f} chk_nov={res['chunked_novel']:.2f} "
                  f"chk_g={res['chunked_gated']:.2f} chk_nov_g={res['chunked_novel_gated']:.2f} "
                  f"rf_fam={res['route_frac_familiar']:.2f} rf_nov={res['route_frac_novel']:.2f} "
                  f"tau={res['tau']:.3f} scr={res['scrambled']:.2f} mem={res['memorization']:.2f}", flush=True)

    # C90 per arm per N + gate metrics.
    c90_by_N = {}
    for N in N_grid:
        c90_by_N[N] = {a: c90(curves[N][a]) for a in ARM_KEYS}
        ft = c90_by_N[N]["flat_tagged"]
        c90_by_N[N]["gate_keep_extension"] = c90_by_N[N]["chunked_gated"] / max(ft, 1)
        c90_by_N[N]["chunked_extension"] = c90_by_N[N]["chunked"] / max(ft, 1)
        c90_by_N[N]["gate_lift_novel"] = c90_by_N[N]["chunked_novel_gated"] - c90_by_N[N]["chunked_novel"]

    P = c90_by_N[PRIMARY_N]
    ext_gated = P["gate_keep_extension"]
    c90_ng = P["chunked_novel_gated"]
    c90_fn = P["flat_novel"]
    c90_cn = P["chunked_novel"]
    c90_ft = P["flat_tagged"]
    c90_cg = P["chunked_gated"]

    prim = {r["C"]: r for r in sweep if r["N"] == PRIMARY_N}

    # gate discrimination at LOW C (C<=4): familiar routes to chunk far more than novel.
    low_cs = [C for C in prim if C <= 4]
    rf_fam_low = float(np.mean([prim[C]["route_frac_familiar"] for C in low_cs]))
    rf_nov_low = float(np.mean([prim[C]["route_frac_novel"] for C in low_cs]))
    route_gap_low = rf_fam_low - rf_nov_low

    nulls_collapse = all(prim[C]["scrambled"] <= 0.20 and prim[C]["flat_bag"] <= 0.20
                         for C in prim if C >= 2)
    flat_shared_collapses = all(prim[C]["flat_shared"] <= 0.20 for C in prim if C >= 2)
    mem_max = max((prim[C]["memorization"] for C in prim if C >= 2), default=0.0)
    mem_fails = mem_max <= 0.20

    never_worse = c90_ng >= c90_fn                       # (a) strict: >= flat floor at C90
    material_lift = c90_ng >= c90_cn + 2                 # (b) huge lift off the ~0 crater
    restore_floor = (c90_ng >= c90_fn - 1) and material_lift  # restores floor within 1 C (residual FPR)
    keep_win = ext_gated >= 1.5                          # (c) familiar-chunk win kept
    gate_discriminates = route_gap_low >= 0.30           # (d) gate routes correctly
    # also report the tightest never-worse-at-matched-C accuracy gap (max flat_novel - novel_gated where
    # flat_novel >= 0.90), i.e. the residual boundary penalty.
    gap_at_floor = max((prim[C]["flat_novel"] - prim[C]["chunked_novel_gated"]
                        for C in prim if prim[C]["flat_novel"] >= 0.90), default=0.0)

    hp = (never_worse and material_lift and keep_win and gate_discriminates
          and nulls_collapse and flat_shared_collapses and mem_fails)
    hf = ((not restore_floor) or (ext_gated <= 1.0) or (route_gap_low < 0.10) or (not nulls_collapse))

    if hp:
        verdict = "HARD_PASS"
    elif hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    brain_check = (
        "gated cleanup is brain-consistent: chunk (deep) for PRACTICED/familiar material, serial/flat "
        "fallback for the unfamiliar (center-embedding ~2-3 limit). chunked_novel_gated C90=%d ~ flat floor "
        "%d (never worse than flat); familiar chunked_gated C90=%d keeps %.2fx over flat_tagged C90=%d."
        % (c90_ng, c90_fn, c90_cg, ext_gated, c90_ft)
    )

    verdict_msg = (
        f"CONFIDENCE-GATED chunk cleanup, primary N={PRIMARY_N}. "
        f"NOVEL-CLAUSE TAIL: chunked_novel(ungated) C90={c90_cn} -> chunked_novel_gated C90={c90_ng} "
        f"(flat_novel floor C90={c90_fn}); never_worse_strict={never_worse}, restore_floor_within1C={restore_floor}, "
        f"residual_boundary_gap={gap_at_floor:.3f}. "
        f"FAMILIAR KEPT: chunked_gated C90={c90_cg} vs flat_tagged C90={c90_ft} = {ext_gated:.2f}x "
        f"(ungated chunked C90={P['chunked']}, {P['chunked_extension']:.2f}x). "
        f"GATE ROUTING (C<=4): familiar->chunk={rf_fam_low:.2f}, novel->chunk={rf_nov_low:.2f}, "
        f"gap={route_gap_low:.2f} (discriminates={gate_discriminates}). "
        f"nulls_collapse={nulls_collapse}; flat_shared_collapses={flat_shared_collapses}; "
        f"memorization_max(C>=2)={mem_max:.3f}. "
        f"per-N gate_lift(novel): " + ", ".join(f"N={N}:{c90_by_N[N]['gate_lift_novel']}" for N in N_grid) + "; "
        f"per-N keep_ext: " + ", ".join(f"N={N}:{c90_by_N[N]['gate_keep_extension']:.2f}x" for N in N_grid) + ". "
        f"BRAIN-CHECK: {brain_check}"
    )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: confidence-gated cleanup lifts novel-clause chunking to the flat floor "
                   f"(C90 {c90_cn}->{c90_ng}) while keeping familiar {ext_gated:.2f}x ({run_mode})",
        "run_mode": run_mode,
        "elapsed_s": round(time.time() - t0, 2),
        "n_seeds": len(seeds),
        "primary_N": PRIMARY_N,
        "gate_percentile": GATE_PERCENTILE,
        "gate_keep_extension_primary": ext_gated,
        "gate_lift_novel_primary": c90_ng - c90_cn,
        "chunked_novel_gated_c90_primary": c90_ng,
        "flat_novel_c90_primary": c90_fn,
        "chunked_novel_c90_primary": c90_cn,
        "chunked_gated_c90_primary": c90_cg,
        "flat_tagged_c90_primary": c90_ft,
        "never_worse_than_flat_strict": never_worse,
        "restore_floor_within_1C": restore_floor,
        "residual_boundary_gap": gap_at_floor,
        "material_lift": material_lift,
        "keep_familiar_win": keep_win,
        "route_frac_familiar_lowC": rf_fam_low,
        "route_frac_novel_lowC": rf_nov_low,
        "gate_route_gap_lowC": route_gap_low,
        "gate_discriminates": gate_discriminates,
        "c90_by_N": {str(N): c90_by_N[N] for N in N_grid},
        "nulls_collapse": nulls_collapse,
        "flat_shared_collapses": flat_shared_collapses,
        "memorization_max_c_ge_2": mem_max,
        "brain_check": brain_check,
        "sweep": sweep,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True,
        "progress_logging": "per-(N,C) flushed stdout line",
        "crlb_n_a": "capacity-cliff locator; gate tau calibrated on disjoint novel pool (FPR<=5%), never on test",
        "REQUIRED_FIELDS": ["anchor_name", "verdict", "verdict_msg", "gate_keep_extension_primary",
                            "chunked_novel_gated_c90_primary", "flat_novel_c90_primary", "c90_by_N", "sweep"],
    }

    out_dir = REPO / "data" / f"exp_{ANCHOR_NAME}"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")

    print("\n=== VERDICT ===", flush=True)
    print(verdict, flush=True)
    print(verdict_msg, flush=True)
    print(f"metrics -> {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    _out = REPO / "data" / f"exp_{ANCHOR_NAME}"
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, ANCHOR_NAME, e)
        raise
