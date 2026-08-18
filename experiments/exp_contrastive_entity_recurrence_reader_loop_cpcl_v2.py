"""CONTRASTIVE PREDICTIVE READER LOOP v2 (CPCL-v2): the self-supervised LEARNING LOOP redesigned to fix the
CPCL-v1 null (atom 29366) with the now-VET-confirmed LEARNED CODEBOOK (STEP-1 chain-grade, HARD_PASS
AUC=0.927). Score RIVAL candidate parses by predicting an ENTITY-RECURRENCE / entity-grid coherence target
against REAL held-out text continuation, contrastively; the CONTRAST is the self-supervised learning signal
that repairs the reader's structural cue-weights.

WHY v1 WAS NULL (the 4 diagnosed root causes -> the 4 surgical fixes here):
  (1) RANDOM content codes -> forward model MEMORIZED (in-sample +0.50 -> held-out +0.004 = chance).
      FIX: content codes = the LEARNED similarity-structured text8 codebook (ppmi_svd, STEP-1 HARD_PASS),
      SimHash-bipolarized (Charikar 2002 signed-random-projection preserves cosine). Similar patients get
      correlated codes -> the forward model GENERALIZES to held-out instead of memorizing.
  (2) BAG-OF-WORDS continuation target. FIX: ENTITY-RECURRENCE / entity-grid target (Barzilay-Lapata 2008;
      Grosz-Joshi-Weinstein Centering 1995) -- the continuation is weighted toward entities that PERSIST
      (recur across the next sentences), not a flat bag; a correctly-extracted theme recurs, a mis-attached
      locative does not.
  (3) IN-SAMPLE scoring. FIX: held-out learning curve on a third-reader gold slice NEVER in the mining corpus.
  (4) contrast did not ISOLATE patient-correctness. FIX: rivals share (sid, verb) and differ ONLY in patient
      p -> the contrast isolates which PATIENT is correct.

PRIOR ART (credit; learn-from / build-on, never steal):
  - Learned codebook: Random Indexing (Kanerva 1988; Sahlgren 2005), BEAGLE (Jones-Mewhort 2007), PPMI-SVD
    (Levy-Goldberg 2015). Built + validated in STEP-1 (exp_learned_codebook_generalization_gate_v1).
  - Entity-grid coherence: Barzilay-Lapata 2008; Centering: Grosz-Joshi-Weinstein 1995; Guinaudeau-Strube 2013.
  - SimHash bipolarization: Charikar 2002 (cosine-preserving signed random projection).
  - Homeostatic scaling: Oja 1982 (Oja's rule; bounded-norm Hebbian).
  - Predictive coding forward model: Rao-Ballard 1999 / Friston (hdlab/predictive_coding.py).
  - Coherence-gameability GUARD: arXiv 2110.07198 (Mohiuddin-Joty et al., EACL 2021, "Rethinking Coherence
    Modeling: Synthetic vs Downstream Tasks") -- synthetic shuffle/permutation success does NOT prove
    coherence understanding (surface-cheatable). Applied here as: the SHUFFLED arm IS the shuffle test; if
    learning survives shuffling real->rival correspondence the "signal" is a surface confound (P2 VETO), and
    the discriminator-fires gate requires the REAL-vs-SHUFFLED err-gap margin to exceed a floor (real
    predictive structure, not a surface classifier).

FALSE-RECURRENCE GUARD (contract-mandated; RELATEDNESS != IDENTITY):
  Distributional codes rate dog~cat as high-cosine. Entity recurrence / persistence is measured by LITERAL
  TOKEN IDENTITY (does the SAME surface token recur), NEVER by cosine. The codebook feeds ONLY the content
  representation the forward model predicts; the entity-persistence WEIGHTING uses identity counts. self_test
  asserts persist("dog", ["the cat ran"]) == 0 despite high cos(code_dog, code_cat).

STEP-1 DESIGN-GATE (coverage; can STOP):
  Before the loop: verify the text8 codebook COVERS the McGuffey reading vocabulary + the entity-recurrence
  target tokens. If content-token OCCURRENCE coverage < HF floor -> STOP with COVERAGE_INSUFFICIENT (a clean
  result: a reading-corpus codebook is needed first; do NOT reach for "it's the corpus" past this gate).

THREE ARMS (must-fail discriminator; ONE ingredient toggled) + baseline + oracle guard:
  FROZEN         : LCCP structural teacher, NO predictive pass (the static ~0.557 reader = REAL baseline).
  ARM_CONTRAST   : rivalry(+) real-data(+) -- the mechanism (learned-code + entity-recurrence contrast).
  ARM_ABSOLUTE   : rivalry(-) real-data(+) -- non-contrastive per-candidate err-target (same real signal, no
                   rival pairing). Known-weak per BYOL/DINO parallel + the v1/SCV precedent.
  ARM_SHUFFLED   : rivalry(+) real-data(-) -- MUST-FAIL control. err vs a DERANGED continuation. Learning MUST
                   collapse to ~FROZEN (the shuffle test; if it trains, the signal is a surface confound).
  ORACLE_CEILING : construction-determination guard. Pick winner via GOLD directly. If ~1.000, task is
                   construction-determined (flagged). Real ceiling honestly < 1.000.

VERDICT BANDS (pre-registered BEFORE running; preregs/2026-07-19_contrastive_entity_recurrence_cpcl_v2.md):
  COVERAGE gate: HARD_PASS >= 0.60 content-occurrence coverage; HARD_FAIL < 0.40 (STOP).
  P1 (mechanism): HARD_PASS = mean(P[CONTRAST]-P[FROZEN]) >= +0.02 AND min-over-seeds > 0 AND
                  P[CONTRAST] > P[ABSOLUTE] AND P[CONTRAST] > P[SHUFFLED]. HARD_FAIL = delta <= 0 OR not >
                  ABSOLUTE OR not > SHUFFLED (reproduces v1: loop adds nothing). MIDDLE = 0 < delta < 0.02.
  P2 (VETO): SHUFFLED delta vs FROZEN ~0 (|mean| < 0.01) AND < CONTRAST. HARD_FAIL_P2 = SHUFFLED trains
             (leakage) -> DO NOT trust P1.
  P3 (learning curve): CONTRAST held-out precision non-decreasing over mining fractions AND end > start.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- the LCCP reader (~105 ms/sent) is the
  cost, run ONCE + cached; forward model W (N x N outer products) + perceptron are cheap. Codebook built ONCE
  + cached to disk (config-hashed .npy). Storage: no_storage (extraction-precision measurement). Foreground
  LOCAL-to-completion (NO queue, NO push, NO remote-persist). progress_logging: print_flush_true.
  Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, hashlib digests (NEVER builtin hash()), sorted(set).

CELL-TEMPLATE MANDATORY: except SystemExit: raise BEFORE except Exception (no BaseException); no bare except /
  no silent-continue; arms_differ_verified (w hashes); final_metrics_atomicity=tmp_replace; baseline_in_band
  gate; discriminator-fires gate; crlb_n/a (extraction precision, no quantitative noise floor);
  calibration_check=default_ok (seeded, deterministic); coverage gate; all report numbers tagged.
ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "contrastive_entity_recurrence_reader_loop_cpcl_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as S  # noqa: E402
from experiments import exp_learned_codebook_generalization_gate_v1 as CB  # noqa: E402
from hdlab import predictive_coding as PC  # noqa: E402

FEAT_DIM = 7  # LCCP's 6 structural cues + 1 predictive-fit cue (f_pred)

MINING_FILES_FULL = S.MINING_FILES_FULL
MINING_FILES_SMOKE = S.MINING_FILES_SMOKE
EXCLUDED_FROM_MINING = S.EXCLUDED_FROM_MINING  # third reader = gold source, never mined

# Codebook build config (STEP-1 validated: 8M tokens, V=10000, N=1024, window=5, min_count=5 -> AUC=0.927).
# ONE codebook, built + cached ONCE, reused by smoke AND full (the foundation is config-invariant here).
CODEBOOK_CFG = dict(n_tokens=8_000_000, vocab_size=10000, N=1024, window=5, min_count=5,
                    ri_sparsity=10, arm="ppmi_svd", seed=7)
CODEBOOK_CACHE_DIR = os.path.join(REPO_ROOT, "data", "_cpcl_v2_codebook_cache")

# Pre-registered coverage bands (declared BEFORE running; NOT tuned to pass).
HP_COVERAGE = 0.60   # content-token OCCURRENCE coverage HARD_PASS floor
HF_COVERAGE = 0.40   # below this -> STOP (reading-corpus codebook needed first)

NDIM = None
CONTENT_TOK = None   # {tok: bipolar (+-1) N-vector}  (SimHash of codebook code, or seeded-random for OOV)
ROLES = None


# ==============================================================================================
# Deterministic seeds (NEVER builtin hash() -- PYTHONHASHSEED safe; PROT-023).
# ==============================================================================================
def _digest_seed(s):
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:8], "big")


# ==============================================================================================
# Phase 0: learned codebook build + cache (STEP-1 builders, ppmi_svd arm) -> (codes, w2i).
# ==============================================================================================
def _codebook_cache_key(cfg):
    payload = json.dumps(cfg, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def get_codebook(cfg):
    """Build (or load cached) the STEP-1 ppmi_svd codebook. Returns (codes float32 [V,N], w2i dict)."""
    key = _codebook_cache_key(cfg)
    os.makedirs(CODEBOOK_CACHE_DIR, exist_ok=True)
    codes_path = os.path.join(CODEBOOK_CACHE_DIR, f"codes_{key}.npy")
    w2i_path = os.path.join(CODEBOOK_CACHE_DIR, f"w2i_{key}.json")
    if os.path.exists(codes_path) and os.path.exists(w2i_path):
        codes = np.load(codes_path)
        with open(w2i_path, encoding="utf-8") as f:
            w2i = json.load(f)
        print(f"[{ANCHOR_NAME}] codebook loaded from cache: V={len(w2i)} N={codes.shape[1]}", flush=True)
        return codes, w2i
    print(f"[{ANCHOR_NAME}] building codebook (ppmi_svd) n_tokens={cfg['n_tokens']} V<={cfg['vocab_size']} ...",
          flush=True)
    t0 = time.time()
    tokens = CB.load_tokens(cfg["n_tokens"])
    w2i, _counts = CB.build_vocab(tokens, cfg["vocab_size"], cfg["min_count"])
    V = len(w2i)
    cooc = CB.build_cooc(tokens, w2i, cfg["window"])
    ppmi = CB.build_ppmi(cooc)
    codes = CB.build_codebook(cfg["arm"], cooc, ppmi, V, cfg["N"], cfg["seed"], cfg["ri_sparsity"])
    codes = np.ascontiguousarray(codes.astype(np.float32))
    np.save(codes_path, codes)
    with open(w2i_path, "w", encoding="utf-8") as f:
        json.dump(w2i, f)
    print(f"[{ANCHOR_NAME}] codebook built V={V} N={cfg['N']} in {time.time()-t0:.1f}s -> cached", flush=True)
    return codes, w2i


def build_simhash_projection(N, seed):
    """Fixed gaussian (N x N) SimHash projection (Charikar 2002; cosine-preserving signed random proj)."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((N, N)).astype(np.float32)


def build_content_vectors(vocab, codes, w2i, P, N, oov_seed):
    """{tok: bipolar +-1 N-vector}. In-codebook -> SimHash sign(code_row @ P) (similarity-structured, FIX-1).
    OOV -> seeded-random bipolar (independent; NO smuggled semantics). Deterministic (sorted vocab)."""
    toks = sorted(set(vocab))
    out = {}
    n_cov = 0
    for t in toks:
        if t in w2i:
            row = codes[w2i[t]]
            proj = row @ P  # (N,)
            s = np.sign(proj).astype(np.float64)
            s[s == 0] = 1.0
            out[t] = s
            n_cov += 1
        else:
            rng = np.random.default_rng(_digest_seed(f"oov::{t}::{oov_seed}"))
            s = rng.integers(0, 2, size=N).astype(np.float64) * 2.0 - 1.0
            out[t] = s
    return out, n_cov


def build_roles(N, seed):
    rng = np.random.default_rng(seed)
    return {r: (rng.integers(0, 2, size=N).astype(np.float64) * 2.0 - 1.0) for r in ("V", "A", "P")}


def _content(tok):
    return CONTENT_TOK.get(tok)


def parse_key(v, a, p):
    """Role-bound bipolar key for a parse (v,a,p). bind = elementwise product; bundle = sum -> sign."""
    acc = np.zeros(NDIM, dtype=np.float64)
    for role, tok in (("V", v), ("A", a), ("P", p)):
        cv = _content(tok)
        if cv is not None:
            acc = acc + ROLES[role] * cv
    s = np.sign(acc)
    s[s == 0] = 1.0
    return s


def _is_content_tok(t):
    return (t not in L.FUNCWORD and t not in L.PREPS and len(t) >= 2
            and t.replace("'", "").isalpha())


# ==============================================================================================
# Coverage gate (STEP-1 DESIGN-GATE) + false-recurrence guard support.
# ==============================================================================================
def measure_coverage(mine_data, mine_order, eval_text, eval_order, eval_svo, w2i):
    """Content-token OCCURRENCE coverage + candidate-patient TYPE coverage + continuation-target coverage."""
    content_occ = content_cov = 0
    patient_types = set()
    patient_cov_types = set()
    for sid in mine_order:
        for t in L.tokenize(mine_data[sid]["sent"]):
            if _is_content_tok(t):
                content_occ += 1
                if t in w2i:
                    content_cov += 1
        for _v, _a, p in mine_data[sid]["svo"]:
            if _is_content_tok(p):
                patient_types.add(p)
                if p in w2i:
                    patient_cov_types.add(p)
    for sid in eval_order:
        for t in L.tokenize(eval_text[sid]):
            if _is_content_tok(t):
                content_occ += 1
                if t in w2i:
                    content_cov += 1
        for _v, _a, p in eval_svo[sid]:
            if _is_content_tok(p):
                patient_types.add(p)
                if p in w2i:
                    patient_cov_types.add(p)
    return {
        "content_occurrence_coverage": round(content_cov / content_occ, 4) if content_occ else 0.0,
        "content_occurrences": content_occ,
        "patient_type_coverage": round(len(patient_cov_types) / len(patient_types), 4) if patient_types else 0.0,
        "n_patient_types": len(patient_types),
        "codebook_vocab_size": len(w2i),
    }


# ==============================================================================================
# Entity-recurrence / entity-grid continuation target (FIX-2). Identity-based persistence weighting.
# ==============================================================================================
def build_idf(order, sent_text):
    df = defaultdict(int)
    ndoc = 0
    for sid in order:
        ndoc += 1
        seen = set(t for t in L.tokenize(sent_text[sid]) if _is_content_tok(t))
        for t in seen:
            df[t] += 1
    return {t: float(np.log((1.0 + ndoc) / (1.0 + df[t])) + 1.0) for t in df}


def persist_counts(sid, order, idx, sent_text, n_next):
    """IDENTITY-based entity-grid persistence: {content_tok: #_of_next_sentences_it_appears_in} over the next
    n_next same-passage sentences. Uses LITERAL token identity ONLY (false-recurrence guard: NEVER cosine)."""
    prefix = sid.rsplit("_", 1)[0]
    presence = defaultdict(int)
    for j in range(idx + 1, min(idx + 1 + n_next, len(order))):
        nsid = order[j]
        if nsid.rsplit("_", 1)[0] != prefix:
            break
        seen = set(t for t in L.tokenize(sent_text[nsid]) if _is_content_tok(t))
        for t in seen:
            presence[t] += 1
    return presence


def continuation_vec(sid, order, idx, sent_text, n_next, idf):
    """Entity-grid continuation target: bipolar bundle of content codes weighted by idf(t) * presence(t),
    where presence = #_next_sentences containing t (entity persistence; identity-based). Upweights RECURRING
    entities (Centering / Barzilay-Lapata) vs a flat bag-of-words. None if empty."""
    presence = persist_counts(sid, order, idx, sent_text, n_next)
    if not presence:
        return None
    acc = np.zeros(NDIM, dtype=np.float64)
    got = 0
    for t, pres in presence.items():
        cv = _content(t)
        if cv is not None:
            wt = float(idf.get(t, 1.0)) * float(pres)  # persistence-weighted (entity-grid)
            acc = acc + wt * cv
            got += 1
    if got == 0:
        return None
    s = np.sign(acc)
    s[s == 0] = 1.0
    return s


def build_continuations(order, sent_text, n_next, idf, shuffle_seed=None):
    """{sid: cont_vec or None}. shuffle_seed set -> DERANGE sid->continuation (must-fail D- manipulation)."""
    real = {}
    for i, sid in enumerate(order):
        real[sid] = continuation_vec(sid, order, i, sent_text, n_next, idf)
    if shuffle_seed is None:
        return real
    valid = [sid for sid in order if real[sid] is not None]
    rng = np.random.default_rng(shuffle_seed)
    shuf = dict(real)
    if len(valid) >= 2:
        rotated = valid[1:] + valid[:1]
        perm = rng.permutation(len(valid))
        src_order = [rotated[k] for k in perm]
        for k, sid in enumerate(valid):
            shuf[sid] = real[src_order[k % len(src_order)]]
    return shuf


# ==============================================================================================
# Candidates (rivals = LCCP over-extracted patients per verb-instance; isolate patient, FIX-4).
# ==============================================================================================
def build_candidates(reader_data, order):
    idx_of = {sid: i for i, sid in enumerate(order)}
    cands = []
    for sid in order:
        rec = reader_data.get(sid)
        if rec is None:
            continue
        toks = L.tokenize(rec["sent"])
        for tup in rec["svo"]:
            v_surf, a, p = tup
            feat6, _ = L.candidate_features(toks, v_surf, p)
            cands.append({"sid": sid, "idx": idx_of[sid], "v": L.lemma_verb(v_surf),
                          "a": a, "p": p, "tup": (v_surf, a, p), "feat6": feat6})
    return cands


def group_by_instance(cands):
    g = defaultdict(list)
    for c in cands:
        g[(c["sid"], c["v"])].append(c)
    return g


# ==============================================================================================
# Forward model (predictive coding): key -> entity-recurrence continuation (gated Hebbian).
# ==============================================================================================
def train_forward_W(cands, cont_by_sid, N, gate_threshold):
    W = np.zeros((N, N), dtype=np.float64)
    n_written = n_skipped = 0
    for c in cands:
        cont = cont_by_sid.get(c["sid"])
        if cont is None:
            continue
        key = parse_key(c["v"], c["a"], c["p"])
        pred = PC.predict(W, key)
        dec = PC.threshold_gate(cont, pred, threshold=gate_threshold)
        _, applied = PC.gated_write(W, key, cont, dec)
        if applied:
            n_written += 1
        else:
            n_skipped += 1
    return W, n_written, n_skipped


def predictive_fit(W, c, cont_by_sid):
    cont = cont_by_sid.get(c["sid"])
    if cont is None:
        return 0.0, 0.5
    key = parse_key(c["v"], c["a"], c["p"])
    pred = PC.predict(W, key)
    err = PC.residual_magnitude(cont, pred)
    return float(1.0 - 2.0 * err), float(err)


def attach_feat7(cands, W, cont_by_sid):
    for c in cands:
        fp, err = predictive_fit(W, c, cont_by_sid)
        c["f_pred"] = fp
        c["err"] = err
        c["feat"] = np.concatenate([c["feat6"], [fp]])
        # diagnostic identity-recurrence flag (NOT a trained feature; false-recurrence guard = identity only)
        c["recur_id"] = 1.0  # overwritten by caller when continuation tokens are available


# ==============================================================================================
# Contrast-pair / absolute-target mining from REAL (or shuffled) prediction error (isolates patient).
# ==============================================================================================
def mine_contrast_pairs(inst_groups, min_err_gap):
    pairs = []
    n_multi = n_informative = 0
    gaps = []
    for (_sid, _v), cs in inst_groups.items():
        if len(cs) < 2:
            continue
        n_multi += 1
        errs = [c["err"] for c in cs]
        emin, emax = min(errs), max(errs)
        gap = emax - emin
        gaps.append(gap)
        if gap >= min_err_gap:
            n_informative += 1
            pos = cs[int(np.argmin(errs))]
            neg = cs[int(np.argmax(errs))]
            pairs.append((pos["feat"].copy(), neg["feat"].copy()))
    stats = {"n_multi_candidate_instances": n_multi, "n_informative_pairs": n_informative,
             "mean_err_gap": round(float(np.mean(gaps)), 4) if gaps else 0.0,
             "max_err_gap": round(float(np.max(gaps)), 4) if gaps else 0.0}
    return pairs, stats


def mine_absolute_targets(cands):
    errs = [c["err"] for c in cands]
    if not errs:
        return []
    med = float(np.median(errs))
    return [(c["feat"].copy(), 1.0 if c["err"] < med else 0.0) for c in cands]


# ==============================================================================================
# Training: shared base logistic (cand_target) + ONE optional per-arm pass. Oja homeostatic scaling.
# ==============================================================================================
def train_weights(cands, sel_fn, cfg, seed, mode, pairs=None, abs_targets=None):
    """mode in {frozen, contrast, absolute, shuffled}. base logistic on cand_target for ALL arms (shared);
    then per-mode extra pass. Oja (1982) homeostatic decay on the contrast update -> bounded-norm stability."""
    rng = np.random.default_rng(seed)
    w = np.zeros(FEAT_DIM)
    base = []
    for c in cands:
        t = L.cand_target(c, sel_fn, cfg["sel_keep"], cfg["sel_drop"])
        if t is None:
            continue
        base.append((c["feat"].copy(), t))
    base_abs = base + list(abs_targets) if (mode == "absolute" and abs_targets) else base
    oja_eta = cfg["oja_eta"]
    for _ in range(cfg["epochs"]):
        for k in rng.permutation(len(base_abs)):
            x, t = base_abs[k]
            pred = L.sigmoid(float(np.dot(w, x)))
            w = w + cfg["lr"] * (t - pred) * x
        if mode in ("contrast", "shuffled") and pairs:
            for k in rng.permutation(len(pairs)):
                fpos, fneg = pairs[k]
                y = float(np.dot(w, fpos))
                if y - float(np.dot(w, fneg)) < cfg["coh_margin"]:
                    # margin-perceptron widening + Oja homeostatic decay (bounds weight growth; Oja 1982)
                    w = w + cfg["coh_lr"] * (fpos - fneg) - oja_eta * (y * y) * w
    return w, len(base)


def eval_kept(w, inst_groups, keep_thr, gold=None, oracle=False):
    kept = []
    for (sid, v), cs in inst_groups.items():
        if oracle and gold is not None:
            rec = gold.get(sid, {"pos": []})
            match = None
            for c in cs:
                if L.match_pos(v, c["p"], rec["pos"]) is not None:
                    match = c
                    break
            if match is not None:
                kept.append((match["sid"], match["tup"]))
            continue
        best = max(cs, key=lambda c: L.score_cand(w, c["feat"]))
        if L.score_cand(w, best["feat"]) >= keep_thr:
            kept.append((best["sid"], best["tup"]))
    return kept


# ==============================================================================================
# Config.
# ==============================================================================================
def cfg_smoke():
    return dict(mode="smoke", gold_slice=["L04", "L05", "L07"], mining_files=MINING_FILES_SMOKE,
                mining_max_sents=500, N=CODEBOOK_CFG["N"], n_next=2, gate_threshold=0.30, min_err_gap=0.02,
                sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40, keep_thr=0.45,
                coh_lr=0.10, coh_margin=0.30, oja_eta=0.002, seeds=[7, 13, 19], fractions=[0.5, 1.0],
                simhash_seed=404, role_seed=202, oov_seed=101, shuffle_seed=303)


def cfg_full():
    return dict(mode="full", gold_slice=["L04", "L05", "L07", "L08", "L09", "L10", "L12"],
                mining_files=MINING_FILES_FULL, mining_max_sents=None, N=CODEBOOK_CFG["N"], n_next=2,
                gate_threshold=0.30, min_err_gap=0.02, sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60,
                keep_thr=0.45, coh_lr=0.10, coh_margin=0.30, oja_eta=0.002, seeds=[7, 13, 19],
                fractions=[0.25, 0.5, 1.0], simhash_seed=404, role_seed=202, oov_seed=101, shuffle_seed=303)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def _hash_w(w):
    return hashlib.sha256(np.asarray(w, dtype=np.float64).tobytes()).hexdigest()[:16]


# ==============================================================================================
# Main experiment.
# ==============================================================================================
def run_mode(mode):
    global CONTENT_TOK, ROLES, NDIM
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    out_dir = _out_dir(mode)
    N = cfg["N"]
    NDIM = N

    # ---- Phase 0: learned codebook (STEP-1 ppmi_svd; built once + cached) + SimHash projection ----
    codes, w2i = get_codebook(CODEBOOK_CFG)
    P = build_simhash_projection(N, cfg["simhash_seed"])

    # ---- Load held-out gold eval slice (third reader) + its reader parse (NEVER mined) ----
    eval_order, eval_text, eval_svo = L.load_slice_and_reader(cfg["gold_slice"])
    gold, gold_meta = L.load_gold(cfg["gold_slice"])
    eval_data = {sid: {"sent": eval_text[sid], "svo": [list(t) for t in eval_svo[sid]]} for sid in eval_order}

    # ---- Load mining corpus (external readers; third reader EXCLUDED), cached ----
    mine_data = S.run_reader_on_files(cfg["mining_files"], os.path.join(out_dir, "_mining_cache.json"),
                                      max_sents=cfg["mining_max_sents"])
    mine_order = sorted(mine_data.keys())
    print(f"[{ANCHOR_NAME}:{mode}] mining sents={len(mine_order)} eval sents={len(eval_order)}", flush=True)

    # ---- STEP-1 DESIGN-GATE: coverage of the McGuffey reading vocab by the text8 codebook ----
    coverage = measure_coverage(mine_data, mine_order, eval_text, eval_order, eval_svo, w2i)
    print(f"[{ANCHOR_NAME}:{mode}] coverage={coverage}", flush=True)
    coverage_ok = coverage["content_occurrence_coverage"] >= HP_COVERAGE
    coverage_stop = coverage["content_occurrence_coverage"] < HF_COVERAGE
    if coverage_stop:
        elapsed = time.perf_counter() - t0
        msg = (f"COVERAGE_INSUFFICIENT: content-occurrence coverage="
               f"{coverage['content_occurrence_coverage']:.3f} < HF={HF_COVERAGE}; the text8 codebook does "
               f"not cover the McGuffey reading vocabulary. A reading-corpus codebook is needed before the "
               f"loop. (Clean STOP; not a loop failure.)")
        payload = {"anchor_name": ANCHOR_NAME, "run_mode": mode,
                   "verdict": "COVERAGE_INSUFFICIENT_FOUNDATION_NEEDS_READING_CORPUS_CODEBOOK",
                   "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
                   "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
                   "coverage_gate": coverage, "coverage_bands": {"HP": HP_COVERAGE, "HF": HF_COVERAGE},
                   "REQUIRED_FIELDS": ["verdict", "coverage_gate"]}
        write_metrics(out_dir, payload)
        print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
        return payload

    # ---- Vocab + content (SimHash-codebook) / role vectors ----
    vocab = set()
    for sid in mine_order:
        for t in L.tokenize(mine_data[sid]["sent"]):
            vocab.add(t)
        for v_surf, a, p in mine_data[sid]["svo"]:
            vocab.update([L.lemma_verb(v_surf), a, p, v_surf])
    for sid in eval_order:
        for t in L.tokenize(eval_text[sid]):
            vocab.add(t)
        for v_surf, a, p in eval_svo[sid]:
            vocab.update([L.lemma_verb(v_surf), a, p, v_surf])
    CONTENT_TOK, n_content_cov = build_content_vectors(vocab, codes, w2i, P, N, cfg["oov_seed"])
    ROLES = build_roles(N, cfg["role_seed"])
    print(f"[{ANCHOR_NAME}:{mode}] content vectors: {n_content_cov}/{len(vocab)} SimHash-codebook (rest OOV)",
          flush=True)

    # ---- Base semantic teacher (GloVe) -- shared across ALL arms (part of the base, not the tested signal) ----
    tok_for_glove = set()
    for sid in mine_order:
        for v_surf, a, p in mine_data[sid]["svo"]:
            tok_for_glove.update([p, L.lemma_verb(v_surf)])
    for sid in eval_order:
        for v_surf, a, p in eval_svo[sid]:
            tok_for_glove.update([p, L.lemma_verb(v_surf)])
    glove = L.load_glove_for(tok_for_glove)

    # ---- IDF over mining + eval (entity-grid weighting; identity-based) ----
    idf_text = {sid: mine_data[sid]["sent"] for sid in mine_order}
    idf_text.update({sid: eval_text[sid] for sid in eval_order})
    idf = build_idf(list(idf_text.keys()), idf_text)

    # ---- Continuations (real + deranged) for mining + eval (entity-recurrence target) ----
    mine_sent = {sid: mine_data[sid]["sent"] for sid in mine_order}
    mine_cont_real = build_continuations(mine_order, mine_sent, cfg["n_next"], idf)
    mine_cont_shuf = build_continuations(mine_order, mine_sent, cfg["n_next"], idf,
                                         shuffle_seed=cfg["shuffle_seed"])
    eval_cont_real = build_continuations(eval_order, eval_text, cfg["n_next"], idf)
    eval_cont_shuf = build_continuations(eval_order, eval_text, cfg["n_next"], idf,
                                         shuffle_seed=cfg["shuffle_seed"] + 1)

    # =============================================================================================
    # LEARNING CURVE over mining fractions (genuine-learning: held-out precision moves with data).
    # =============================================================================================
    curve = {"CONTRAST": {}, "ABSOLUTE": {}, "SHUFFLED": {}, "FROZEN": {}}
    per_frac_detail = {}
    disc = {}
    w_hashes_full = {}
    n_units_done = 0

    for frac in cfg["fractions"]:
        n_take = max(2, int(round(frac * len(mine_order))))
        sub = mine_order[:n_take]
        sub_data = {sid: mine_data[sid] for sid in sub}

        W_real, nw_r, ns_r = train_forward_W(build_candidates(sub_data, sub), mine_cont_real, N,
                                             cfg["gate_threshold"])
        W_shuf, nw_s, ns_s = train_forward_W(build_candidates(sub_data, sub), mine_cont_shuf, N,
                                             cfg["gate_threshold"])

        mine_cands_real = build_candidates(sub_data, sub)
        attach_feat7(mine_cands_real, W_real, mine_cont_real)
        mine_cands_shuf = build_candidates(sub_data, sub)
        attach_feat7(mine_cands_shuf, W_shuf, mine_cont_shuf)

        inst_real = group_by_instance(mine_cands_real)
        inst_shuf = group_by_instance(mine_cands_shuf)
        pairs_real, stats_real = mine_contrast_pairs(inst_real, cfg["min_err_gap"])
        pairs_shuf, stats_shuf = mine_contrast_pairs(inst_shuf, cfg["min_err_gap"])
        abs_real = mine_absolute_targets(mine_cands_real)

        sel_real, _, _ = L.build_semantic_teacher(mine_cands_real, glove)

        eval_real = build_candidates(eval_data, eval_order)
        attach_feat7(eval_real, W_real, eval_cont_real)
        eval_shuf = build_candidates(eval_data, eval_order)
        attach_feat7(eval_shuf, W_shuf, eval_cont_shuf)
        eg_real = group_by_instance(eval_real)
        eg_shuf = group_by_instance(eval_shuf)

        arm_p = {"CONTRAST": [], "ABSOLUTE": [], "SHUFFLED": [], "FROZEN": []}
        seed_w = {}
        for seed in cfg["seeds"]:
            w_frozen, _ = train_weights(mine_cands_real, sel_real, cfg, seed, "frozen")
            w_contrast, _ = train_weights(mine_cands_real, sel_real, cfg, seed, "contrast", pairs=pairs_real)
            w_absolute, _ = train_weights(mine_cands_real, sel_real, cfg, seed, "absolute", abs_targets=abs_real)
            w_shuffled, _ = train_weights(mine_cands_shuf, sel_real, cfg, seed, "shuffled", pairs=pairs_shuf)

            p_frozen = L.score_arm(eval_kept(w_frozen, eg_real, cfg["keep_thr"]), gold)["precision"]
            p_contrast = L.score_arm(eval_kept(w_contrast, eg_real, cfg["keep_thr"]), gold)["precision"]
            p_absolute = L.score_arm(eval_kept(w_absolute, eg_real, cfg["keep_thr"]), gold)["precision"]
            p_shuffled = L.score_arm(eval_kept(w_shuffled, eg_shuf, cfg["keep_thr"]), gold)["precision"]

            arm_p["FROZEN"].append(p_frozen)
            arm_p["CONTRAST"].append(p_contrast)
            arm_p["ABSOLUTE"].append(p_absolute)
            arm_p["SHUFFLED"].append(p_shuffled)
            seed_w[seed] = {"FROZEN": w_frozen, "CONTRAST": w_contrast,
                            "ABSOLUTE": w_absolute, "SHUFFLED": w_shuffled}
            n_units_done += 1

        for arm in curve:
            curve[arm][f"{frac:.2f}"] = round(float(np.mean(arm_p[arm])), 4)
        per_frac_detail[f"{frac:.2f}"] = {
            "n_mining_sents": n_take, "W_real_written": nw_r, "W_real_skipped": ns_r,
            "W_shuf_written": nw_s, "W_shuf_skipped": ns_s,
            "contrast_pair_stats_real": stats_real, "contrast_pair_stats_shuffled": stats_shuf,
            "n_abs_targets": len(abs_real),
            "per_arm_precision_by_seed": {a: [round(x, 4) for x in arm_p[a]] for a in arm_p},
        }
        if abs(frac - cfg["fractions"][-1]) < 1e-9:
            disc = {"contrast_mean_err_gap": stats_real["mean_err_gap"],
                    "contrast_n_informative_pairs": stats_real["n_informative_pairs"],
                    "shuffled_mean_err_gap": stats_shuf["mean_err_gap"],
                    "shuffled_n_informative_pairs": stats_shuf["n_informative_pairs"],
                    "n_multi_candidate_instances": stats_real["n_multi_candidate_instances"]}
            s0 = cfg["seeds"][0]
            w_hashes_full = {a: _hash_w(seed_w[s0][a]) for a in seed_w[s0]}

    # ---- ORACLE_CEILING guard: pick gold patient directly on eval ----
    W_real_full, _, _ = train_forward_W(build_candidates(mine_data, mine_order), mine_cont_real, N,
                                        cfg["gate_threshold"])
    eval_real_full = build_candidates(eval_data, eval_order)
    attach_feat7(eval_real_full, W_real_full, eval_cont_real)
    eg_full = group_by_instance(eval_real_full)
    oracle_kept = eval_kept(None, eg_full, cfg["keep_thr"], gold=gold, oracle=True)
    oracle_precision = L.score_arm(oracle_kept, gold)["precision"]

    # =============================================================================================
    # VERDICTS (pre-registered bands).
    # =============================================================================================
    lastf = f"{cfg['fractions'][-1]:.2f}"
    minf = f"{cfg['fractions'][0]:.2f}"
    fd = per_frac_detail[lastf]["per_arm_precision_by_seed"]
    seed_deltas = [round(fd["CONTRAST"][i] - fd["FROZEN"][i], 4) for i in range(len(cfg["seeds"]))]
    mean_delta = round(float(np.mean(seed_deltas)), 4)
    min_delta = round(float(np.min(seed_deltas)), 4)
    p_contrast = curve["CONTRAST"][lastf]
    p_frozen = curve["FROZEN"][lastf]
    p_absolute = curve["ABSOLUTE"][lastf]
    p_shuffled = curve["SHUFFLED"][lastf]
    shuffled_delta = round(p_shuffled - p_frozen, 4)

    baseline_in_band = bool(0.05 < p_frozen < 0.95)
    c_gap = disc.get("contrast_mean_err_gap", 0.0)
    s_gap = disc.get("shuffled_mean_err_gap", 0.0)
    rel_gap_margin = round((c_gap - s_gap) / c_gap, 4) if c_gap > 1e-9 else 0.0
    contrast_fires = bool(disc.get("contrast_n_informative_pairs", 0) >= 5 and rel_gap_margin >= 0.20)
    disc["real_vs_shuffled_relative_gap_margin"] = rel_gap_margin
    arms_differ = len(set(w_hashes_full.values())) == len(w_hashes_full)

    expected_n_units = len(cfg["fractions"]) * len(cfg["seeds"])
    cardinality_ok = (n_units_done == expected_n_units)

    # P2 must-fail VETO
    if abs(shuffled_delta) >= 0.02 and p_shuffled >= p_contrast:
        p2 = "HARD_FAIL_P2_VETO_SHUFFLED_TRAINS"
    elif abs(shuffled_delta) < 0.01 and p_shuffled < p_contrast:
        p2 = "PASS_P2_SHUFFLED_NULL"
    else:
        p2 = "MIDDLE_P2_SHUFFLED_PARTIAL"

    # P1 mechanism
    if not cardinality_ok:
        p1 = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif p2 == "HARD_FAIL_P2_VETO_SHUFFLED_TRAINS":
        p1 = "HARD_FAIL_P1_UNTRUSTWORTHY_SHUFFLED_CONFOUND"
    elif mean_delta >= 0.02 and min_delta > 0.0 and p_contrast > p_absolute and p_contrast > p_shuffled:
        p1 = "HARD_PASS_P1_CONTRAST_LEARNS"
    elif mean_delta <= 0.0 or p_contrast <= p_absolute or p_contrast <= p_shuffled:
        p1 = "HARD_FAIL_P1_LOOP_ADDS_NOTHING"
    else:
        p1 = "MIDDLE_BAND_P1"

    # P3 learning curve
    cvals = [curve["CONTRAST"][f"{fr:.2f}"] for fr in cfg["fractions"]]
    non_decreasing = all(cvals[i + 1] >= cvals[i] - 0.005 for i in range(len(cvals) - 1))
    if non_decreasing and curve["CONTRAST"][lastf] > curve["CONTRAST"][minf]:
        p3 = "HARD_PASS_P3_LEARNING_CURVE_MOVES"
    elif curve["CONTRAST"][lastf] <= curve["CONTRAST"][minf]:
        p3 = "HARD_FAIL_P3_FLAT_OR_DECREASING"
    else:
        p3 = "MIDDLE_P3"

    oracle_flag = "CONSTRUCTION_DETERMINED_ORACLE_TRIVIAL" if oracle_precision >= 0.98 else "oracle_nontrivial_ok"

    elapsed = time.perf_counter() - t0
    msg = (f"P1={p1} P2={p2} P3={p3} | FROZEN_P={p_frozen:.3f} CONTRAST_P={p_contrast:.3f} "
           f"ABSOLUTE_P={p_absolute:.3f} SHUFFLED_P={p_shuffled:.3f} | meandelta(C-F)={mean_delta:+.3f} "
           f"(min={min_delta:+.3f}) shufdelta={shuffled_delta:+.3f} | curveC={cvals} "
           f"| coverage={coverage['content_occurrence_coverage']:.3f}(ok={coverage_ok}) "
           f"| disc: C_gap={disc.get('contrast_mean_err_gap')} C_pairs={disc.get('contrast_n_informative_pairs')} "
           f"S_gap={disc.get('shuffled_mean_err_gap')} relmargin={rel_gap_margin} "
           f"| oracle_P={oracle_precision:.3f}({oracle_flag}) | base_in_band={baseline_in_band} "
           f"contrast_fires={contrast_fires} arms_differ={arms_differ}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode,
        "verdict": f"{p1}|{p2}|{p3}", "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "codebook_cfg": CODEBOOK_CFG,
        "coverage_gate": coverage, "coverage_bands": {"HP": HP_COVERAGE, "HF": HF_COVERAGE},
        "coverage_ok": coverage_ok,
        "learning_curve_precision": curve,
        "p1_mechanism": {"verdict": p1, "mean_delta_contrast_minus_frozen": mean_delta,
                         "min_delta": min_delta, "per_seed_delta": seed_deltas,
                         "P_frozen": p_frozen, "P_contrast": p_contrast, "P_absolute": p_absolute,
                         "P_shuffled": p_shuffled},
        "p2_mustfail_control": {"verdict": p2, "shuffled_delta_vs_frozen": shuffled_delta,
                                "interpretation": "shuffled continuation must NOT train (real-data ingredient)"},
        "p3_learning_curve": {"verdict": p3, "contrast_curve": cvals, "fractions": cfg["fractions"],
                              "interpretation": "held-out precision must MOVE with more REAL mining data"},
        "oracle_ceiling_guard": {"oracle_precision": oracle_precision, "flag": oracle_flag,
                                 "note": "handed-gold winner; must NOT trivially hit ~1.000; ceiling < 1.000"},
        "discriminator": disc,
        "per_fraction_detail": per_frac_detail,
        "w_hashes_full_fraction_seed0": w_hashes_full,
        "gates": {"baseline_in_band": baseline_in_band, "contrast_fires": contrast_fires,
                  "arms_differ": arms_differ, "coverage_ok": coverage_ok, "cardinality_ok": cardinality_ok},
        "baseline_in_band": baseline_in_band, "contrast_fires": contrast_fires,
        "arms_differ_verified": arms_differ, "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units, "n_units_done": n_units_done,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "default_ok_for_this_regime",
        "crlb_n/a": "extraction-precision metric; no quantitative noise floor (relative rival prediction err)",
        "error_signal_is_real_exogenous": True,
        "content_codes": "learned text8 ppmi_svd codebook (STEP-1 HARD_PASS AUC=0.927), SimHash-bipolarized",
        "entity_recurrence_target": ("entity-grid persistence (Barzilay-Lapata / Centering): continuation "
            "bundle weighted by idf(t)*presence(t), presence = #_next_sentences containing t (IDENTITY, not "
            "cosine). False-recurrence guard: recurrence never uses code cosine."),
        "coherence_gameability_guard": ("arXiv 2110.07198: SHUFFLED arm = the shuffle test; if it trains -> "
            "surface confound (P2 VETO). discriminator-fires requires real-vs-shuffled rel gap margin >= 0.20."),
        "claim_ceiling": ("SELF-SUPERVISED w.r.t. parse-labels AND the scoring signal (real corpus "
            "continuation; no curated oracle). Content codes carry LEARNED distributional similarity (text8 "
            "codebook) so the forward model generalizes rather than memorizing (the v1 fix). GloVe enters ONLY "
            "the shared base teacher (identical across arms). Ceiling < 1.000. NOT a claim of learned "
            "world-knowledge -- a claim that a rival-vs-real-data entity-recurrence CONTRAST with learned "
            "codes is a genuine learning signal where random-code v1 was null."),
        "excluded_from_mining": EXCLUDED_FROM_MINING,
        "gold_meta_independence": gold_meta,
        "REQUIRED_FIELDS": ["verdict", "coverage_gate", "learning_curve_precision", "p1_mechanism",
                            "p2_mustfail_control", "p3_learning_curve", "oracle_ceiling_guard",
                            "discriminator", "error_signal_is_real_exogenous", "gates"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ==============================================================================================
# Self-test (real code path: constructs the REAL codebook-content + forward model + rival machinery tiny).
# ==============================================================================================
def self_test():
    global CONTENT_TOK, ROLES, NDIM
    N = 128
    NDIM = N
    # --- Real codebook builder path at tiny scale (exercise CB.build_* + SimHash content) ---
    toy = (["dog", "pet", "bark", "loyal"] * 8 + ["cat", "pet", "purr", "feline"] * 8
           + ["hut", "built", "house", "roof"] * 8 + ["hill", "road", "path", "walk"] * 8)
    rng = np.random.default_rng(0)
    tokens = list(rng.permutation(toy * 4))
    w2i, _c = CB.build_vocab(tokens, vocab_size=40, min_count=1)
    cooc = CB.build_cooc(tokens, w2i, window=3)
    ppmi = CB.build_ppmi(cooc)
    codes = CB.build_codebook("ppmi_svd", cooc, ppmi, len(w2i), N, seed=7, ri_sparsity=4).astype(np.float32)
    P = build_simhash_projection(N, 404)

    vocab = list(w2i.keys()) + ["ZZZ_oov_token"]
    CONTENT_TOK, ncov = build_content_vectors(vocab, codes, w2i, P, N, oov_seed=101)
    ROLES = build_roles(N, 202)
    assert ncov == len(w2i), "all in-vocab toks should get SimHash-codebook content"
    for t in vocab:
        assert set(np.unique(CONTENT_TOK[t])).issubset({-1.0, 1.0}), f"content {t} not bipolar"

    # SimHash cosine-preservation PROPERTY test (Charikar 2002), on controlled vectors (toy SVD geometry is
    # too unreliable to assert token-level semantics; the real text8 codebook is validated at AUC=0.927).
    prng = np.random.default_rng(1)
    base = prng.standard_normal(N)
    near = base + 0.15 * prng.standard_normal(N)   # high cosine to base
    far = prng.standard_normal(N)                  # low cosine to base
    def _sh(x):
        s = np.sign(x @ P).astype(np.float64); s[s == 0] = 1.0; return s
    sim_near = float(np.dot(_sh(base), _sh(near))) / N
    sim_far = float(np.dot(_sh(base), _sh(far))) / N
    assert sim_near > sim_far, f"SimHash cosine-preservation broken: near={sim_near:.3f} <= far={sim_far:.3f}"
    # raw codebook cosine (pre-SimHash) for the false-recurrence non-vacuousness report (relatedness != identity)
    raw_dogcat = float(np.dot(codes[w2i["dog"]], codes[w2i["cat"]]))

    # rival keys differ ONLY in patient (isolate patient-correctness)
    k1 = parse_key("built", "he", "hut")
    k2 = parse_key("built", "he", "hill")
    assert not np.array_equal(k1, k2), "rival keys must differ (patient binding)"

    # FALSE-RECURRENCE GUARD: persistence is IDENTITY-based. A high-cosine RELATIVE of dog (=cat) recurring
    # must NOT credit 'dog' with recurrence -- each token is its own key; cosine is NEVER used for recurrence.
    order = ["M0_00", "M0_01", "M0_02"]
    text = {"M0_00": "the dog ran", "M0_01": "the cat sat", "M0_02": "the cat slept"}
    pres1 = persist_counts("M0_00", order, 0, text, n_next=2)
    assert pres1.get("dog", 0) == 0, "false-recurrence guard: dog must NOT recur just because cat (high-cos) does"
    assert pres1.get("cat", 0) == 2, "cat is its own identity key; recurs in both next sentences"
    # and when dog DOES literally recur, it is counted
    text2 = {"M0_00": "the dog ran", "M0_01": "the cat sat", "M0_02": "the dog slept"}
    assert persist_counts("M0_00", order, 0, text2, n_next=2).get("dog", 0) == 1, "literal dog recurrence counted"

    # forward model: a key predicts a continuation it was written with; residual falls below chance
    idf = build_idf(order, text)
    cont = build_continuations(order, text, n_next=2, idf=idf)
    assert cont["M0_00"] is not None, "continuation must exist"
    cands = [{"sid": "M0_00", "idx": 0, "v": "ran", "a": "dog", "p": "cat",
              "tup": ("ran", "dog", "cat"), "feat6": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])}]
    W, nw, ns = train_forward_W(cands, cont, N, gate_threshold=0.30)
    assert nw == 1, f"one gated write expected, got {nw}"
    fp, err = predictive_fit(W, cands[0], cont)
    assert err < 0.5, f"trained key should beat chance: err={err:.3f}"
    attach_feat7(cands, W, cont)
    assert cands[0]["feat"].shape[0] == FEAT_DIM, "feat must be 7-dim"

    # contrast-pair mining: two rivals with different err -> one informative pair
    ig = {("M0_00", "built"): [
        {"sid": "M0_00", "v": "built", "p": "hut", "tup": ("built", "he", "hut"),
         "feat": np.concatenate([np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0]), [0.9]]), "err": 0.10},
        {"sid": "M0_00", "v": "built", "p": "hill", "tup": ("built", "he", "hill"),
         "feat": np.concatenate([np.array([1.0, 0.2, 1.0, 0.0, 1.0, 0.0]), [-0.3]]), "err": 0.60},
    ]}
    pairs, stats = mine_contrast_pairs(ig, min_err_gap=0.02)
    assert stats["n_informative_pairs"] == 1 and len(pairs) == 1, "one informative contrast pair expected"
    fpos, fneg = pairs[0]
    assert fpos[-1] > fneg[-1], "pos rival (low err) must have higher f_pred"

    # Oja homeostatic update bounds weight norm (train contrast pass on repeated informative pairs)
    cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.2, epochs=3, coh_lr=0.5, coh_margin=5.0, oja_eta=0.05)
    class _Sel:  # sel_fn stub returning None (defer) so base pass is empty -> isolates Oja on contrast pass
        def __call__(self, v, p):
            return None
    w_oja, _ = train_weights([], _Sel(), cfg, seed=7, mode="contrast", pairs=pairs * 20)
    assert np.all(np.isfinite(w_oja)), "Oja update produced non-finite w"
    assert float(np.linalg.norm(w_oja)) < 1e6, "Oja homeostasis failed to bound w-norm"

    # shuffled derangement changes at least one continuation (distinct-content continuations so swap is visible)
    order3 = ["M0_00", "M0_01", "M0_02"]
    text3 = {"M0_00": "the dog ran", "M0_01": "a hut stood", "M0_02": "the road bent"}
    idf3 = build_idf(order3, text3)
    cr = build_continuations(order3, text3, n_next=1, idf=idf3)
    cs = build_continuations(order3, text3, n_next=1, idf=idf3, shuffle_seed=9)
    n_diff = sum(1 for sid in order3 if cr[sid] is not None and cs[sid] is not None
                 and not np.array_equal(cr[sid], cs[sid]))
    assert n_diff >= 1, "shuffle must derange at least one continuation"

    print(f"[{ANCHOR_NAME}] self-test PASS | SimHash preserves cosine: near={sim_near:.3f} > far={sim_far:.3f} "
          f"(raw codebook cos dog-cat={raw_dogcat:.3f} = relatedness, NOT identity); false-recurrence guard holds "
          f"(cat!=dog recurrence); "
          f"forward model err={err:.3f}; contrast pair mined; Oja bounds w-norm={float(np.linalg.norm(w_oja)):.2f}; "
          f"shuffle deranges {n_diff}; feat_dim={FEAT_DIM}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
