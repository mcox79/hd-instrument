"""CONTRASTIVE PREDICTIVE READER LOOP (CPCL): the missing base element -- a predictive-coding LEARNING
LOOP that scores RIVAL candidate parses against REAL EXOGENOUS TEXT CONTINUATION and uses the CONTRAST
as a self-supervised learning signal to repair the reader's structural cue-weights.

WHY THIS EXISTS (read before interpreting any number):
  The Scene-Coherence Verifier (SCV, VET atom 29360) scored rival parses against a HAND-CURATED WordNet/
  VerbNet coherence ORACLE and used a STATIC perceptron -- it gave 0 training delta even gold-perfect.
  Drill C (notes/drill_brain_how_it_does_it_given_failures_5x_2026-07-20.md) diagnosed the fix: score
  rivals against REAL subsequent text (prediction-error / surprise vs the actual next words, NOT a curated
  oracle, NOT a static selector), and let the CONTRAST (which rival predicts real data better) be the
  learning signal. THIS cell operationalizes exactly that, re-wiring hdlab/predictive_coding.py (the
  predict/residual machinery) + the SCV/LCCP rival-candidate machinery. No new representational math.

THE LOOP (glass-box, CPU, NO gold parses, NO external LLM at runtime):
  1. RIVALS: per verb-instance, the LCCP reader's >=2 over-extracted candidate patients (the SCV rival set).
  2. FORWARD MODEL (predictive_coding.py): each rival parse (v,a,p) -> a role-bound bipolar KEY
     (ROLE_V*content(v) + ROLE_A*content(a) + ROLE_P*content(p), bipolar bind/bundle). A gated-Hebbian W
     is learned over the MINING corpus: key -> the REAL next-sentence content bundle (real transitions,
     self-supervised, no gold). content(tok) = fixed seeded random bipolar vector (glass-box; NOT GloVe --
     the predictive signal must come from REAL corpus transitions learned by W, not a pretrained embedding).
  3. SCORE vs REAL DATA: predict(W, key) = sign(W @ key); err = residual_magnitude(real_continuation, pred)
     in [0,1] (fraction of bits the substrate gets WRONG about the actual continuation). f_pred = 1-2*err
     (signed predictive fit; +1 perfect, 0 chance). This is scored against the ACTUAL next text.
  4. CONTRAST -> learning signal: per verb-instance, pos = rival with LOWEST err (best predicts real
     continuation), neg = HIGHEST err, kept iff err-gap >= MIN_ERR_GAP (informative). Margin/perceptron
     update widens w.f_pos - w.f_neg -> the reader INTERNALIZES a portable cue-weight preferring rivals
     that predict real subsequent text. Repairs the extractor.

THREE ARMS (the must-fail discriminator; ONE ingredient toggled each) + baseline + guard:
  FROZEN         : LCCP structural teacher, NO predictive pass (the ~0.557 static reader = REAL baseline).
  ARM_CONTRAST   : rivalry(+) real-data(+)  -- the mechanism. Contrast pairs vs REAL continuation.
  ARM_ABSOLUTE   : rivalry(-) real-data(+)  -- KNOWN-to-fail non-contrastive. Per-candidate absolute err
                   thresholded at the corpus median -> per-candidate target (no rival pairing). Same real
                   signal, no contrast. Per BYOL/DINO cautionary parallel + SCV precedent -> must underperform.
  ARM_SHUFFLED   : rivalry(+) real-data(-)  -- MUST-FAIL control. err computed against a DERANGED
                   continuation (each instance scored vs a random OTHER instance's continuation, consistent
                   in W-training AND scoring). Learning MUST collapse to null (~FROZEN).
  ORACLE_CEILING : construction-determination guard. Pick winner via GOLD directly. If this trivially hits
                   ~1.000, the task is construction-determined (flagged). Real ceiling honestly < 1.000.

  This is a clean 2x2 isolation: CONTRAST=(R+,D+), ABSOLUTE=(R-,D+), SHUFFLED=(R+,D-). If CONTRAST beats
  BOTH, then rivalry AND real-data are JOINTLY necessary -- exactly Drill C's claim.

NON-CONSTRUCTION-DETERMINED GUARDS (load-bearing, per atoms 29360/29363/29364):
  (G1) error signal is REAL EXOGENOUS next-sentence text -- NOT a curated oracle, NOT self-generated, NOT gold.
  (G2) ORACLE_CEILING must NOT trivially win (>= 0.98 -> flag construction-determined).
  (G3) GENUINE LEARNING = held-out precision improves as more REAL mining data is consumed (a LEARNING CURVE
       over mining fractions that MOVES), evaluated on the third-reader gold slice NEVER in the mining corpus.
  (G4) ceiling honestly < 1.000 on real data (reported).

DESIGN-GATE (pre-registered; verified at smoke BEFORE trusting the full):
  REAL baseline = FROZEN (LCCP structural reader), in-band 0.05<P<0.95.
  Discriminator FIRES at smoke: (a) informative contrast pairs exist (n_informative >= 1), AND
    (b) SHUFFLED err-gap ~ 0 while CONTRAST err-gap > 0 (real predictive structure present, not a confound).
  ONE ingredient toggled per arm. ARMS-MUST-DIFFER (w hashes). Multi-seed. Determinism enforced.

VERDICT BANDS (pre-registered BEFORE running; do NOT redefine mid-run):
  P1 (mechanism, the crux):
    HARD_PASS = mean(P[CONTRAST] - P[FROZEN]) >= +0.02 over seeds AND min-over-seeds > 0 (consistent sign)
                AND mean P[CONTRAST] > mean P[ABSOLUTE] AND mean P[CONTRAST] > mean P[SHUFFLED].
    HARD_FAIL = mean(P[CONTRAST]-P[FROZEN]) <= 0  OR  CONTRAST not > ABSOLUTE  OR  CONTRAST not > SHUFFLED
                (= reproduces 29360; the loop adds nothing beyond non-contrastive / shuffled).
    MIDDLE    = 0 < mean delta < 0.02 or inconsistent sign.
  P2 (must-fail control, veto): SHUFFLED delta vs FROZEN must be ~0 (|mean| < 0.01) AND clearly < CONTRAST.
    HARD_FAIL_P2 (VETO) = SHUFFLED trains as well as CONTRAST (leakage/confound) -> DO NOT trust P1.
  P3 (learning curve, genuine-learning): CONTRAST held-out precision non-decreasing across mining fractions
    AND P[frac=1.0] > P[frac=min]. HARD_FAIL_P3 = flat/decreasing (a one-shot fit, not learning).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- the LCCP reader (~105 ms/sent) is the
  cost; run ONCE on mining + gold slice, cache to JSON (reuse SCV run_reader_on_files). Forward-model W
  (N x N outer-product memory, N small) + perceptron are cheap linear algebra. Storage: no_storage
  (extraction-precision measurement). Foreground local-to-completion (NO queue; NO push; NO remote-persist).
  progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, hashlib digests
  (NEVER builtin hash()), sorted(set); numpy default_rng seeded.

CELL-TEMPLATE MANDATORY: except SystemExit: raise BEFORE except Exception (no BaseException);
  no bare except / no silent-continue; arms_differ_verified (w hashes); final_metrics_atomicity=tmp_replace;
  baseline_in_band gate; discriminator-fires gate; crlb_n/a (extraction precision, no quantitative noise
  floor); calibration_check=default_ok (seeded default_rng, deterministic); all report numbers tagged.
ASCII-only.
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

ANCHOR_NAME = "contrastive_predictive_reader_loop_cpcl_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as S  # noqa: E402
from hdlab import predictive_coding as PC  # noqa: E402

FEAT_DIM = 7  # LCCP's 6 structural cues + 1 predictive-fit cue (f_pred)

MINING_FILES_FULL = S.MINING_FILES_FULL
MINING_FILES_SMOKE = S.MINING_FILES_SMOKE
EXCLUDED_FROM_MINING = S.EXCLUDED_FROM_MINING  # third reader = gold source, never mined


# ==============================================================================================
# Deterministic bipolar content + role vectors (glass-box; seeded; NEVER builtin hash()).
# ==============================================================================================
def _digest_seed(s):
    """Deterministic 64-bit seed from a string via sha256 (NOT builtin hash() -- PYTHONHASHSEED safe)."""
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:8], "big")


def build_content_vectors(vocab, N, seed):
    """vocab: iterable of tokens. Returns {tok: bipolar (+-1) vector of dim N}. Deterministic: sorted vocab
    + one seeded generator. content vectors are RANDOM (no pretrained semantics) -- the predictive signal
    must be learned by W from REAL corpus transitions, not smuggled in via embeddings."""
    toks = sorted(set(vocab))
    rng = np.random.default_rng(seed)
    mat = rng.integers(0, 2, size=(len(toks), N)).astype(np.float64) * 2.0 - 1.0
    return {t: mat[i] for i, t in enumerate(toks)}


def build_roles(N, seed):
    rng = np.random.default_rng(seed)
    return {r: (rng.integers(0, 2, size=N).astype(np.float64) * 2.0 - 1.0) for r in ("V", "A", "P")}


CONTENT_TOK = None  # set per-run
ROLES = None
NDIM = None


def _content(tok):
    v = CONTENT_TOK.get(tok)
    return v


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


def continuation_vec(sid, order, idx, sent_text, n_next, idf=None):
    """IDF-weighted bipolar bundle of content-token vectors in the next n_next sentences that share sid's
    prefix (same file / same lesson). Returns None if empty. This is the REAL EXOGENOUS continuation (G1).
    IDF weighting makes continuations DISTINCTIVE from one another (down-weights the tiny reused
    graded-reader vocabulary) so the shuffled-control (D-) manipulation is actually separable -- distinctive
    content (where argument recurrence lives) dominates the bundle sign."""
    prefix = sid.rsplit("_", 1)[0]
    acc = np.zeros(NDIM, dtype=np.float64)
    got = 0
    for j in range(idx + 1, min(idx + 1 + n_next, len(order))):
        nsid = order[j]
        if nsid.rsplit("_", 1)[0] != prefix:
            break
        for t in L.tokenize(sent_text[nsid]):
            if _is_content_tok(t):
                cv = _content(t)
                if cv is not None:
                    wt = 1.0 if idf is None else float(idf.get(t, 1.0))
                    acc = acc + wt * cv
                    got += 1
    if got == 0:
        return None
    s = np.sign(acc)
    s[s == 0] = 1.0
    return s


# ==============================================================================================
# Candidate + instance construction (rivals = LCCP over-extracted patients per verb-instance).
# ==============================================================================================
def build_candidates(reader_data, order, sent_text):
    """reader_data: {sid:{sent,svo}}. order: sid sequence (for continuation lookup). Returns list of cand
    dicts {sid, idx, v, a, p, tup, feat6}. feat7 (with f_pred) added later once W exists."""
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
# Forward model: learn W (real + deranged) over mining candidate keys -> real continuation (gated).
# ==============================================================================================
def build_idf(order, sent_text):
    """Inverse document frequency over content tokens (doc = sentence). Deterministic."""
    df = defaultdict(int)
    ndoc = 0
    for sid in order:
        ndoc += 1
        seen = set(t for t in L.tokenize(sent_text[sid]) if _is_content_tok(t))
        for t in seen:
            df[t] += 1
    return {t: float(np.log((1.0 + ndoc) / (1.0 + df[t])) + 1.0) for t in df}


def build_continuations(order, sent_text, n_next, shuffle_seed=None, idf=None):
    """Returns {sid: cont_vec or None}. If shuffle_seed is not None, DERANGE the sid->continuation mapping
    (each instance scored vs a RANDOM OTHER instance's continuation) -- the must-fail (D-) manipulation."""
    real = {}
    for i, sid in enumerate(order):
        real[sid] = continuation_vec(sid, order, i, sent_text, n_next, idf=idf)
    if shuffle_seed is None:
        return real
    valid = [sid for sid in order if real[sid] is not None]
    rng = np.random.default_rng(shuffle_seed)
    perm = rng.permutation(len(valid))
    # derangement: rotate by 1 among valid then apply permutation (ensures sid != source)
    shuf = dict(real)
    if len(valid) >= 2:
        rotated = valid[1:] + valid[:1]
        src_order = [rotated[k] for k in perm]
        for k, sid in enumerate(valid):
            shuf[sid] = real[src_order[k % len(src_order)]]
    return shuf


def train_forward_W(cands, cont_by_sid, N, gate_threshold):
    """Gated-Hebbian W over candidate keys -> instance continuation. Returns (W, n_written, n_skipped).
    Uses predictive_coding.threshold_gate so predictable (already-modelled) transitions are skipped
    (free-energy ingest) -- concentrates plasticity + limits capacity overload."""
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
    """Signed real-data predictive fit f_pred = 1 - 2*err in [-1,1] (err = residual_magnitude vs REAL
    continuation). Returns (f_pred, err). If no continuation, f_pred=0 (chance), err=0.5."""
    cont = cont_by_sid.get(c["sid"])
    if cont is None:
        return 0.0, 0.5
    key = parse_key(c["v"], c["a"], c["p"])
    pred = PC.predict(W, key)
    err = PC.residual_magnitude(cont, pred)
    return float(1.0 - 2.0 * err), float(err)


def attach_feat7(cands, W, cont_by_sid):
    """Append f_pred as the 7th feature. Returns feats keyed by id(cand) and per-cand err (for mining stats)."""
    for c in cands:
        fp, err = predictive_fit(W, c, cont_by_sid)
        c["f_pred"] = fp
        c["err"] = err
        c["feat"] = np.concatenate([c["feat6"], [fp]])


# ==============================================================================================
# Contrast-pair / absolute-target mining from REAL (or shuffled) prediction error.
# ==============================================================================================
def mine_contrast_pairs(inst_groups, min_err_gap):
    """Per verb-instance with >=2 rivals: pos = min-err rival, neg = max-err rival, kept iff err-gap
    >= min_err_gap (informative). Returns (pairs [(feat_pos,feat_neg)], stats)."""
    pairs = []
    n_multi = n_informative = 0
    gaps = []
    for (sid, v), cs in inst_groups.items():
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
    """Non-contrastive per-candidate targets: err below the median -> 1 (good parse), else 0. Same real
    signal, NO rival pairing (rivalry-). Returns list of (feat, target)."""
    errs = [c["err"] for c in cands]
    if not errs:
        return []
    med = float(np.median(errs))
    return [(c["feat"].copy(), 1.0 if c["err"] < med else 0.0) for c in cands]


# ==============================================================================================
# Training: shared base logistic (cand_target) + ONE optional extra pass per arm.
# ==============================================================================================
def train_weights(cands, sel_fn, cfg, seed, mode, pairs=None, abs_targets=None):
    """mode in {frozen, contrast, absolute, shuffled}. base logistic on cand_target for ALL arms (shared);
    then per-mode extra pass. ONE variable = the extra pass + its data source."""
    rng = np.random.default_rng(seed)
    w = np.zeros(FEAT_DIM)
    base = []
    for c in cands:
        t = L.cand_target(c, sel_fn, cfg["sel_keep"], cfg["sel_drop"])
        if t is None:
            continue
        base.append((c["feat"].copy(), t))
    # ABSOLUTE (rivalry-): fold the per-candidate real-data err-targets into the SAME base logistic pass
    # (same lr) -- a FAIR non-contrastive use of the identical real signal (no rival pairing).
    base_abs = base + list(abs_targets) if (mode == "absolute" and abs_targets) else base
    for _ in range(cfg["epochs"]):
        for k in rng.permutation(len(base_abs)):
            x, t = base_abs[k]
            pred = L.sigmoid(float(np.dot(w, x)))
            w = w + cfg["lr"] * (t - pred) * x
        if mode in ("contrast", "shuffled") and pairs:
            for k in rng.permutation(len(pairs)):
                fpos, fneg = pairs[k]
                if float(np.dot(w, fpos)) - float(np.dot(w, fneg)) < cfg["coh_margin"]:
                    w = w + cfg["coh_lr"] * (fpos - fneg)
    return w, len(base)


def eval_kept(w, inst_groups, keep_thr, gold=None, oracle=False):
    """Pick best-scoring rival per instance; keep iff score >= keep_thr. oracle=True picks the GOLD patient
    directly (construction-determination guard). Returns kept [(sid, tup)]."""
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
                mining_max_sents=500, N=1024, n_next=2, gate_threshold=0.30, min_err_gap=0.02,
                sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40, keep_thr=0.45,
                coh_lr=0.10, coh_margin=0.30, seeds=[7, 13, 19], fractions=[0.5, 1.0],
                content_seed=101, role_seed=202, shuffle_seed=303)


def cfg_full():
    return dict(mode="full", gold_slice=["L04", "L05", "L07", "L08", "L09", "L10", "L12"],
                mining_files=MINING_FILES_FULL, mining_max_sents=None, N=1024, n_next=2,
                gate_threshold=0.30, min_err_gap=0.02, sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60,
                keep_thr=0.45, coh_lr=0.10, coh_margin=0.30, seeds=[7, 13, 19],
                fractions=[0.25, 0.5, 1.0], content_seed=101, role_seed=202, shuffle_seed=303)


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

    # ---- Load gold eval slice (third reader) + its reader parse (held-out; NEVER in mining) ----
    eval_order, eval_text, eval_svo = L.load_slice_and_reader(cfg["gold_slice"])
    gold, gold_meta = L.load_gold(cfg["gold_slice"])
    eval_data = {sid: {"sent": eval_text[sid], "svo": [list(t) for t in eval_svo[sid]]} for sid in eval_order}

    # ---- Load mining corpus (external readers, third-reader EXCLUDED), cached ----
    mine_data = S.run_reader_on_files(cfg["mining_files"], os.path.join(out_dir, "_mining_cache.json"),
                                      max_sents=cfg["mining_max_sents"])
    mine_order = sorted(mine_data.keys())  # deterministic

    print(f"[{ANCHOR_NAME}:{mode}] mining sents={len(mine_order)} eval sents={len(eval_order)}", flush=True)

    # ---- Vocab + content/role vectors (deterministic) ----
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
    CONTENT_TOK = build_content_vectors(vocab, N, cfg["content_seed"])
    ROLES = build_roles(N, cfg["role_seed"])

    # ---- Base semantic teacher (GloVe) -- shared across ALL arms (part of the base, not the tested signal) ----
    tok_for_glove = set()
    for sid in mine_order:
        for v_surf, a, p in mine_data[sid]["svo"]:
            tok_for_glove.update([p, L.lemma_verb(v_surf)])
    for sid in eval_order:
        for v_surf, a, p in eval_svo[sid]:
            tok_for_glove.update([p, L.lemma_verb(v_surf)])
    glove = L.load_glove_for(tok_for_glove)

    # ---- IDF (over mining + eval sentences) to make continuations distinctive (isolates the D- control) ----
    idf_text = {sid: mine_data[sid]["sent"] for sid in mine_order}
    idf_text.update({sid: eval_text[sid] for sid in eval_order})
    idf = build_idf(list(idf_text.keys()), idf_text)

    # ---- Continuations (real + deranged) for mining + eval ----
    mine_sent = {sid: mine_data[sid]["sent"] for sid in mine_order}
    mine_cont_real = build_continuations(mine_order, mine_sent, cfg["n_next"], idf=idf)
    mine_cont_shuf = build_continuations(mine_order, mine_sent, cfg["n_next"],
                                         shuffle_seed=cfg["shuffle_seed"], idf=idf)
    eval_cont_real = build_continuations(eval_order, eval_text, cfg["n_next"], idf=idf)
    eval_cont_shuf = build_continuations(eval_order, eval_text, cfg["n_next"],
                                         shuffle_seed=cfg["shuffle_seed"] + 1, idf=idf)

    # ---- Eval candidates (fixed) ----
    eval_cands = build_candidates(eval_data, eval_order, eval_text)

    # =============================================================================================
    # LEARNING CURVE over mining fractions (G3: genuine learning = held-out precision moves with data).
    # For each fraction: build W_real/W_shuf on that fraction, attach f_pred, mine pairs, train + eval.
    # =============================================================================================
    curve = {"CONTRAST": {}, "ABSOLUTE": {}, "SHUFFLED": {}, "FROZEN": {}}
    per_frac_detail = {}
    disc = {}  # discriminator diagnostics at frac=1.0
    w_hashes_full = {}

    for frac in cfg["fractions"]:
        n_take = max(2, int(round(frac * len(mine_order))))
        sub = mine_order[:n_take]
        sub_data = {sid: mine_data[sid] for sid in sub}
        sub_text = {sid: mine_data[sid]["sent"] for sid in sub}
        sub_cands = build_candidates(sub_data, sub, sub_text)

        # forward models on this fraction
        W_real, nw_r, ns_r = train_forward_W(sub_cands, mine_cont_real, N, cfg["gate_threshold"])
        W_shuf, nw_s, ns_s = train_forward_W(sub_cands, mine_cont_shuf, N, cfg["gate_threshold"])

        # feat7 for mining cands (real-based, for CONTRAST/ABSOLUTE/FROZEN) and shuf-based (for SHUFFLED)
        mine_cands_real = build_candidates(sub_data, sub, sub_text)
        attach_feat7(mine_cands_real, W_real, mine_cont_real)
        mine_cands_shuf = build_candidates(sub_data, sub, sub_text)
        attach_feat7(mine_cands_shuf, W_shuf, mine_cont_shuf)

        # mine contrast pairs / absolute targets
        inst_real = group_by_instance(mine_cands_real)
        inst_shuf = group_by_instance(mine_cands_shuf)
        pairs_real, stats_real = mine_contrast_pairs(inst_real, cfg["min_err_gap"])
        pairs_shuf, stats_shuf = mine_contrast_pairs(inst_shuf, cfg["min_err_gap"])
        abs_real = mine_absolute_targets(mine_cands_real)

        # base teacher on the fraction's real cands
        sel_real, _, _ = L.build_semantic_teacher(mine_cands_real, glove)

        # eval feat7 (real-based for most arms; shuf-based for SHUFFLED)
        eval_real = build_candidates(eval_data, eval_order, eval_text)
        attach_feat7(eval_real, W_real, eval_cont_real)
        eval_shuf = build_candidates(eval_data, eval_order, eval_text)
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

        for arm in curve:
            curve[arm][f"{frac:.2f}"] = round(float(np.mean(arm_p[arm])), 4)
        per_frac_detail[f"{frac:.2f}"] = {
            "n_mining_sents": n_take, "W_real_written": nw_r, "W_real_skipped": ns_r,
            "W_shuf_written": nw_s, "W_shuf_skipped": ns_s,
            "contrast_pair_stats_real": stats_real, "contrast_pair_stats_shuffled": stats_shuf,
            "n_abs_targets": len(abs_real),
            "per_arm_precision_by_seed": {a: [round(x, 4) for x in arm_p[a]] for a in arm_p},
        }
        if abs(frac - cfg["fractions"][-1]) < 1e-9:  # last (full) fraction -> discriminator + hashes
            disc = {"contrast_mean_err_gap": stats_real["mean_err_gap"],
                    "contrast_n_informative_pairs": stats_real["n_informative_pairs"],
                    "shuffled_mean_err_gap": stats_shuf["mean_err_gap"],
                    "shuffled_n_informative_pairs": stats_shuf["n_informative_pairs"],
                    "n_multi_candidate_instances": stats_real["n_multi_candidate_instances"]}
            # arm hashes from seed 0 for arms-must-differ
            s0 = cfg["seeds"][0]
            w_hashes_full = {a: _hash_w(seed_w[s0][a]) for a in seed_w[s0]}

    # ---- ORACLE_CEILING guard (G2): pick gold patient directly on eval (real-based W) ----
    eval_real_full = build_candidates(eval_data, eval_order, eval_text)
    W_real_full, _, _ = train_forward_W(build_candidates(mine_data, mine_order,
                                        {sid: mine_data[sid]["sent"] for sid in mine_order}),
                                        mine_cont_real, N, cfg["gate_threshold"])
    attach_feat7(eval_real_full, W_real_full, eval_cont_real)
    eg_full = group_by_instance(eval_real_full)
    oracle_kept = eval_kept(None, eg_full, cfg["keep_thr"], gold=gold, oracle=True)
    oracle_precision = L.score_arm(oracle_kept, gold)["precision"]

    # =============================================================================================
    # VERDICTS (pre-registered bands).
    # =============================================================================================
    lastf = f"{cfg['fractions'][-1]:.2f}"
    minf = f"{cfg['fractions'][0]:.2f}"
    # per-seed deltas at full fraction
    seed_deltas = []
    fd = per_frac_detail[lastf]["per_arm_precision_by_seed"]
    for i in range(len(cfg["seeds"])):
        seed_deltas.append(round(fd["CONTRAST"][i] - fd["FROZEN"][i], 4))
    mean_delta = round(float(np.mean(seed_deltas)), 4)
    min_delta = round(float(np.min(seed_deltas)), 4)
    p_contrast = curve["CONTRAST"][lastf]
    p_frozen = curve["FROZEN"][lastf]
    p_absolute = curve["ABSOLUTE"][lastf]
    p_shuffled = curve["SHUFFLED"][lastf]
    shuffled_delta = round(p_shuffled - p_frozen, 4)

    baseline_in_band = bool(0.05 < p_frozen < 0.95)
    # GENUINE discriminator: the REAL-continuation rival err-gap must exceed the SHUFFLED err-gap by a
    # non-trivial RELATIVE margin (>=20%). C_gap ~ S_gap means the "signal" is a confound (continuations
    # too mutually similar), NOT real predictive structure -> the real-data ingredient is not contributing.
    c_gap = disc.get("contrast_mean_err_gap", 0.0)
    s_gap = disc.get("shuffled_mean_err_gap", 0.0)
    rel_gap_margin = round((c_gap - s_gap) / c_gap, 4) if c_gap > 1e-9 else 0.0
    contrast_fires = bool(disc.get("contrast_n_informative_pairs", 0) >= 5 and rel_gap_margin >= 0.20)
    disc["real_vs_shuffled_relative_gap_margin"] = rel_gap_margin
    arms_differ = len(set(w_hashes_full.values())) == len(w_hashes_full)

    # P2 must-fail VETO first
    if abs(shuffled_delta) >= 0.02 and p_shuffled >= p_contrast:
        p2 = "HARD_FAIL_P2_VETO_SHUFFLED_TRAINS"
    elif abs(shuffled_delta) < 0.01 and p_shuffled < p_contrast:
        p2 = "PASS_P2_SHUFFLED_NULL"
    else:
        p2 = "MIDDLE_P2_SHUFFLED_PARTIAL"

    # P1 mechanism
    if p2 == "HARD_FAIL_P2_VETO_SHUFFLED_TRAINS":
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
           f"| disc: C_gap={disc.get('contrast_mean_err_gap')} C_pairs={disc.get('contrast_n_informative_pairs')} "
           f"S_gap={disc.get('shuffled_mean_err_gap')} | oracle_P={oracle_precision:.3f}({oracle_flag}) "
           f"| base_in_band={baseline_in_band} contrast_fires={contrast_fires} arms_differ={arms_differ}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode,
        "verdict": f"{p1}|{p2}|{p3}", "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
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
                                 "note": "handed-gold winner; must NOT trivially hit ~1.000 (G2); "
                                         "real ceiling honestly < 1.000 (G4)"},
        "discriminator": disc,
        "per_fraction_detail": per_frac_detail,
        "w_hashes_full_fraction_seed0": w_hashes_full,
        "gates": {"baseline_in_band": baseline_in_band, "contrast_fires": contrast_fires,
                  "arms_differ": arms_differ},
        "baseline_in_band": baseline_in_band, "contrast_fires": contrast_fires,
        "arms_differ_verified": arms_differ,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "default_ok_for_this_regime",
        "crlb_n/a": "extraction-precision metric; no quantitative noise floor (relative rival prediction err)",
        "error_signal_is_real_exogenous": True,
        "error_signal_rationale": ("G1: err = residual_magnitude(REAL next-sentence content bundle, "
            "predict(W, parse_key)). The target is the ACTUAL subsequent text (next n_next same-file "
            "sentences), NOT a WordNet/VerbNet oracle, NOT gold, NOT self-generated. This is the exact "
            "fix for the SCV null (atom 29360): oracle-scored static selector -> real-data predictive loop."),
        "claim_ceiling": ("SELF-SUPERVISED w.r.t. parse-labels AND w.r.t. the scoring signal (real corpus "
            "continuation; no curated oracle). content vectors are RANDOM (no pretrained semantics) so the "
            "predictive signal is learned by W from REAL transitions. GloVe enters ONLY the shared base "
            "teacher (identical across all arms), NOT the tested contrast signal. Ceiling < 1.000 on real "
            "data (G4). NOT a claim of learned world-knowledge -- a claim that a rival-vs-real-data "
            "predictive CONTRAST is a genuine learning signal where a static oracle selector was not."),
        "excluded_from_mining": EXCLUDED_FROM_MINING,
        "gold_meta_independence": gold_meta,
        "REQUIRED_FIELDS": ["verdict", "learning_curve_precision", "p1_mechanism", "p2_mustfail_control",
                            "p3_learning_curve", "oracle_ceiling_guard", "discriminator",
                            "error_signal_is_real_exogenous", "gates"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ==============================================================================================
# Self-test (real code path: constructs the REAL forward model + rival machinery at tiny scale).
# ==============================================================================================
def self_test():
    global CONTENT_TOK, ROLES, NDIM
    N = 256
    NDIM = N
    # tiny vocab + vectors
    vocab = ["dog", "cat", "hut", "out", "built", "ran", "boy", "hill", "the", "a", "he"]
    CONTENT_TOK = build_content_vectors(vocab, N, 1)
    ROLES = build_roles(N, 2)

    # parse_key differs across rivals (different patient) -- the substrate of contrast
    k1 = parse_key("built", "he", "hut")
    k2 = parse_key("built", "he", "out")
    assert not np.array_equal(k1, k2), "rival keys must differ (patient binding)"
    assert set(np.unique(k1)).issubset({-1.0, 1.0}), "key must be bipolar"

    # forward model: a key strongly predicts a continuation it was written with; residual_magnitude falls
    order = ["M0_0", "M0_1"]
    text = {"M0_0": "he built a hut", "M0_1": "the hut kept him"}
    cont = build_continuations(order, text, n_next=1)
    assert cont["M0_0"] is not None, "continuation must exist for first sentence"
    cands = [{"sid": "M0_0", "idx": 0, "v": "built", "a": "he", "p": "hut", "tup": ("built", "he", "hut"),
              "feat6": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])}]
    W, nw, ns = train_forward_W(cands, cont, N, gate_threshold=0.30)
    assert nw == 1, f"one gated write expected, got {nw}"
    fp, err = predictive_fit(W, cands[0], cont)
    assert err < 0.5, f"trained key should predict its own continuation better than chance: err={err:.3f}"

    # attach_feat7 makes a 7-dim feature
    attach_feat7(cands, W, cont)
    assert cands[0]["feat"].shape[0] == FEAT_DIM, "feat must be 7-dim (6 struct + f_pred)"

    # contrast-pair mining: two rivals with different err -> an informative pair
    ig = {("M0_0", "built"): [
        {"sid": "M0_0", "v": "built", "p": "hut", "tup": ("built", "he", "hut"),
         "feat": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0, 0.9]), "err": 0.10},
        {"sid": "M0_0", "v": "built", "p": "out", "tup": ("built", "he", "out"),
         "feat": np.array([1.0, 0.2, 1.0, 0.0, 1.0, 0.0, -0.3]), "err": 0.60},
    ]}
    pairs, stats = mine_contrast_pairs(ig, min_err_gap=0.02)
    assert stats["n_informative_pairs"] == 1 and len(pairs) == 1, "one informative contrast pair expected"
    fpos, fneg = pairs[0]
    assert fpos[-1] > fneg[-1], "pos rival (low err) must have higher f_pred than neg"

    # shuffled derangement: continuation mapping changes
    cont_shuf = build_continuations(order, text, n_next=1, shuffle_seed=9)
    # with only 1 valid continuation, derangement is a no-op; test with more
    order3 = ["M0_0", "M0_1", "M0_2"]
    text3 = {"M0_0": "he built a hut", "M0_1": "the dog ran", "M0_2": "the boy sat"}
    cr = build_continuations(order3, text3, n_next=1)
    cs = build_continuations(order3, text3, n_next=1, shuffle_seed=9)
    n_diff = sum(1 for sid in order3 if cr[sid] is not None and cs[sid] is not None
                 and not np.array_equal(cr[sid], cs[sid]))
    assert n_diff >= 1, "shuffle must derange at least one continuation"

    print(f"[{ANCHOR_NAME}] self-test PASS | rival keys differ; forward model predicts real continuation "
          f"(err={err:.3f}); contrast pair mined (f_pred pos>{fneg[-1]:.2f}); shuffle deranges "
          f"({n_diff} changed); feat_dim={FEAT_DIM}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
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
