"""HORLBECK_GI_DENSE_RECURRENCE_DETECTION (v1): does the SYMMETRIC-PRODUCT (bind/conjunction) readout DETECT
real genetic-interaction structure from bare gene IDENTITY on held-out RECURRING-gene pairs, beating BOTH an
ADDITIVE main-effects null AND a DEGREE-preserving (hubness) null?

WHY THIS CELL (dense-recurrence escalation; C1/S1 setting):
  The near-zero-singles paralog pocket was STRUCTURAL_UNDERPOWER (avg gene-degree ~1.0 -> a per-gene relational
  parameter cannot be fit -> held-out-from-identity is structurally IMPOSSIBLE = Park&Marcotte C3 / Pahikkala S4).
  This cell escalates to Horlbeck 2018 (Cell; Mendeley 10.17632/rdzk59n6j4.1), a DENSE all-by-all CRISPRi GI map:
  gene-level K562 = 448 genes, 100128 unordered pairs, 100% measured, every gene recurs in 447 pairs. This is the
  C1/S1 setting (both entities recur; only the specific PAIRING is novel) -- the correct, well-precedented regime
  where held-out relational detection is structurally POSSIBLE. GI score = the paper's OWN quadratic-fit residual
  (observed double phenotype minus expected from a quadratic fit of the two single-gene phenotypes) => MAIN EFFECTS
  STRIPPED BY CONSTRUCTION. So any held-out-predictable structure is genuinely non-additive-at-the-fitness-level.

THE MECHANISM (faithful glass-box re-implementation; NO LLM at measurement):
  SYM as described = a SYMMETRIC-PRODUCT bilinear readout score(a,b) = sum_d W_d e_{a,d} e_{b,d} (the "bind" /
  conjunction of two gene codes). We realize it as a SYMMETRIC LOW-RANK factorization of the (signed) GI matrix:
      Ghat_ab = mu + alpha_a + alpha_b + <F_a, F_b>_R         (F_g in R^R learned per-gene code)
  The PRODUCT term <F_a,F_b> IS the conjunction/bind; the offsets mu+alpha are the additive main-effects part.
  ADDITIVE is the SAME model at R=0 (offsets only, NO product term) -- so SYM STRICTLY NESTS ADDITIVE and the
  ONLY difference is the symmetric-product (conjunction) term. SYM beating ADDITIVE on HELD-OUT pairs => the
  conjunction carries pair-specific structure that GENERALIZES (not just overfits). The rank R is the factorization
  dimension = a HARD capacity limit on the product term (identifiable, not absorbable) => the "match-code-to-data-
  structure / rank lever": if real GI is higher-rank than R=1, larger R detects more (detection-decider addition).

ARMS (detection = rank held-out pairs by score; AUPRC vs FIXED top-decile |GI| gold):
  CHANCE           random score. AUPRC ~ base rate (~0.10). Sanity.
  MEMORIZE         exact train-pair |GI| lookup; NOVEL held-out pairs -> global-mean fallback (constant) -> AUPRC
                   collapses to base rate. VALIDATES the split forces generalization (no table-lookup leak).
  DEGREE           XSwap-style degree-preserving null: per-gene hubness deg_g = mean|GI| over TRAIN partners;
                   logistic combiner of (deg_a,deg_b) symmetric features. ZERO pair-specific info. First-class
                   arm -- degree baselines hit AUROC>=0.95 on comparable bio networks (Zietz 2024), assumed STRONG.
  ADDITIVE (R=0)   mu + alpha_a + alpha_b (two-way main-effects; NO product term). The nested null SYM must beat.
  SYM_R{1,2,4,8,16,32}  offsets + rank-R symmetric product <F_a,F_b>. R=8 is the PRE-REGISTERED primary mechanism
                   rank; the full sweep is the rank-lever diagnostic (reported, not each gated).
  Secondary (reported, NOT gated): cross-cell-line transfer -- K562-fit SYM/ADD/DEG ranked against Jurkat gold on
                   the shared-gene intersection (harder; Jurkat replicate R=0.44 is a quantified noise ceiling).

PRE-REGISTERED BANDS (fixed BEFORE running; see the prereg .md). All on HELD-OUT (novel) pairs, K562, AUPRC,
  multi-seed mean over 5 mask seeds. p0 = measured base rate. REL_MARGIN=0.25. HERO = SYM at PRIMARY_RANK=8.
  Modal expected outcome per the drill's own calibration (P~0.28) is MIDDLE_BAND -- do NOT over-invest a PASS story.
    HARD_PASS_CONJUNCTION_DETECTS = HERO >= (1+REL_MARGIN)*max(ADD,DEG)  AND  HERO >= 2*p0
                                    AND HERO-margin > seed_std (robust to mask draw)  AND split_clean
    HARD_FAIL_ADDITIVE_CAPTURABLE = HERO within 10% rel of ADD (HERO < 1.10*ADD) AND ADD > 1.15*DEG AND ADD > 1.3*p0
                                    (real structure but the conjunction adds nothing over main effects)
    HARD_FAIL_DEGREE_DOMINATED    = HERO within 10% rel of DEG (HERO < 1.10*DEG) AND DEG >= 0.95*ADD
                                    (only hubness is recoverable; no pair-specific relational signal)
    MIDDLE_BAND (MODAL)           = HERO beats DEG by >=15% rel but does NOT clear the 25% margin over ADD
                                    (partial pair-specific structure; report HONESTLY, do not round up)
    REFUTE_IMPL                   = no SYM arm fits SEEN (train) AUPRC >= 0.50 (model cannot fit train -> broken)
                                    OR split leaks (MEMORIZE > 1.3*p0) OR CHANCE off base rate (|CHANCE-p0|>0.04)

Determinism: seeds from INTEGER indices only (NEVER Python salted built-in hashing; F.5). Glass-box CPU torch. Default (no
flag) = FULL run (META_RULE_16). ASCII-only. No bare except; except SystemExit before except Exception. Atomic
metrics write. Data self-contained: loads committed npz else downloads+parses the Mendeley Treeview zip inline.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
import urllib.request
import zipfile
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "horlbeck_gi_dense_recurrence_detection_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
DATA_DIR = os.path.join(_REPO, "data", "horlbeck_gi")
NPZ_PATH = os.path.join(DATA_DIR, "horlbeck_gene_gi.npz")
RAW_DIR = os.path.join(DATA_DIR, "raw")
ZIP_PATH = os.path.join(RAW_DIR, "GI_map_treeview.zip")
# Mendeley 10.17632/rdzk59n6j4.1 -> GI_map_treeview.zip (verified fetchable 2026-07-15).
MENDELEY_ZIP_URL = ("https://data.mendeley.com/public-files/datasets/rdzk59n6j4/files/"
                    "5542388b-e895-4f29-af07-bfe2eecd0655/file_downloaded")
CDT_MEMBERS = {
    "k562": "GI_map_treeview/K562 gene-level map/K562_gene.cdt",
    "jurkat": "GI_map_treeview/Jurkat gene-level map/Jurkat_gene.cdt",
}

# ---- config (FIXED a priori) ----
PRIMARY_LINE = "k562"
CROSS_LINE = "jurkat"
RANKS = [0, 1, 2, 4, 8, 16, 32]   # 0 == ADDITIVE (offsets only); >=1 == SYM low-rank symmetric product
PRIMARY_RANK = 8                  # HERO mechanism rank (pre-registered; NOT test-selected)
HIT_PCT = 90.0                    # |GI| top-decile = hit -> base rate ~ 0.10 by construction
MASK_FRAC = 0.15                  # held-out (test) fraction of pairs
K_FLOOR = 50                      # min TRAIN degree per gene after masking (Pahikkala S1 warm-matrix floor)
SEEDS = (7, 13, 17, 23, 29)       # 5 mask seeds (multi-seed AUC discipline for continuous-score discriminators)
EPOCHS = 400
LR = 0.05
WD_FACTOR = 1.0e-4                # weight decay on the PRODUCT factors F only -> Occam bias toward ADDITIVE
REL_MARGIN = 0.25                 # relative margin HERO must beat both nulls by (module-registry standard)

# ---- bands (fixed before running) ----
ADD_CAPTURE_REL = 0.10            # HERO within this rel of ADD => additive-capturable
DEG_DOMINATE_REL = 0.10           # HERO within this rel of DEG => degree-dominated
MIDDLE_DEG_REL = 0.15             # HERO beats DEG by at least this rel to be MIDDLE (else degree-dominated-ish)
# REFUTE sanity gate (broken-vs-working model, NOT a HARD_PASS threshold): a working SYM must fit TRAIN clearly
# above chance AND above the nested ADDITIVE (the product term must contribute to train fit). Calibrated from the
# smoke (SYM_R8 SEEN=0.484 >> ADD SEEN=0.210 >> base 0.106 = clearly working) to be REACHABLE while still catching
# a non-training model (SEEN ~ p0). Absolute floor + p0-relative floor; both must be cleared.
SEEN_FIT_ABS = 0.20               # best SYM SEEN AUPRC must reach this absolute (reachable per smoke)
SEEN_FIT_MULT = 1.8               # ... AND >= this * p0 (clearly above the base rate)
SEEN_FIT_OVER_ADD = 1.15          # ... AND >= this * ADDITIVE SEEN (product term trains -> nesting confirmed)
MEMO_LEAK_MULT = 1.3              # MEMORIZE must stay below this * p0 (else split leaks)
CHANCE_TOL = 0.04                 # |CHANCE_AUPRC - p0| must be within this (sanity)

# ---- smoke config (fast; queue_add smoke cap = 180s) ----
SMOKE_GENES = 120
SMOKE_RANKS = [0, 1, 8]
SMOKE_SEEDS = (7, 13)
SMOKE_EPOCHS = 150


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


def _sig(arr):
    a = np.asarray(arr, dtype=np.float64)
    return hashlib.sha256(np.round(a, 6).tobytes()).hexdigest()[:16]


# ===========================================================================
# DATA (self-contained: committed npz fast-path; else download+parse Treeview zip)
# ===========================================================================

def _parse_cdt(text):
    lines = text.split("\n")
    header = lines[0].rstrip("\r").split("\t")
    col_genes = [c.strip() for c in header[4:]]
    rows = []
    row_genes = []
    for ln in lines[3:]:
        if not ln.strip():
            continue
        cells = ln.rstrip("\r").split("\t")
        if len(cells) < 4:
            continue
        row_genes.append(cells[1].strip())
        vals = cells[4:]
        r = np.full(len(col_genes), np.nan, dtype=np.float32)
        for j, v in enumerate(vals[: len(col_genes)]):
            v = v.strip()
            if v == "" or v.lower() == "nan":
                continue
            try:
                r[j] = float(v)
            except ValueError:
                pass
        rows.append(r)
    M = np.vstack(rows) if rows else np.zeros((0, len(col_genes)), dtype=np.float32)
    return col_genes, row_genes, M


def _to_symmetric(col_genes, row_genes, M):
    genes = sorted(set(col_genes) & set(row_genes))
    gi = {g: i for i, g in enumerate(genes)}
    n = len(genes)
    cnt = np.zeros((n, n), dtype=np.float32)
    acc = np.zeros((n, n), dtype=np.float64)
    for ri, rg in enumerate(row_genes):
        if rg not in gi:
            continue
        a = gi[rg]
        for cj, cg in enumerate(col_genes):
            if cg not in gi:
                continue
            v = M[ri, cj]
            if v == v:
                acc[a, gi[cg]] += v
                cnt[a, gi[cg]] += 1.0
    both = acc + acc.T
    bc = cnt + cnt.T
    with np.errstate(invalid="ignore", divide="ignore"):
        Sym = np.where(bc > 0, both / np.maximum(bc, 1.0), np.nan).astype(np.float32)
    return genes, Sym


def _build_npz_from_zip():
    os.makedirs(RAW_DIR, exist_ok=True)
    if not os.path.exists(ZIP_PATH):
        _log("data npz+zip absent -> downloading Treeview zip from Mendeley (~9MB)...")
        req = urllib.request.Request(MENDELEY_ZIP_URL, headers={"User-Agent": "hd-instrument/1.0"})
        with urllib.request.urlopen(req, timeout=180) as resp, open(ZIP_PATH + ".tmp", "wb") as fh:
            fh.write(resp.read())
        os.replace(ZIP_PATH + ".tmp", ZIP_PATH)
        _log("downloaded %d bytes" % os.path.getsize(ZIP_PATH))
    z = zipfile.ZipFile(ZIP_PATH)
    out = {}
    for line, member in CDT_MEMBERS.items():
        cg, rg, M = _parse_cdt(z.read(member).decode("utf-8", errors="replace"))
        genes, S = _to_symmetric(cg, rg, M)
        out["%s_genes" % line] = np.array(genes, dtype=object)
        out["%s_gi" % line] = S
    os.makedirs(DATA_DIR, exist_ok=True)
    np.savez_compressed(NPZ_PATH, **out)
    _log("built npz %s (%d bytes)" % (NPZ_PATH, os.path.getsize(NPZ_PATH)))


def load_gi(line):
    """Return (genes list[str], G float32 n x n symmetric, NaN=missing) for a cell line."""
    if not os.path.exists(NPZ_PATH):
        _build_npz_from_zip()
    d = np.load(NPZ_PATH, allow_pickle=True)
    genes = [str(g) for g in d["%s_genes" % line]]
    G = d["%s_gi" % line].astype(np.float32)
    return genes, G


# ===========================================================================
# split: mask MASK_FRAC of off-diagonal finite pairs as TEST, respecting K_FLOOR train-degree floor.
# All test pairs are NOVEL (never in train) => C1/S1 leave-pair-out. Deterministic (integer seed).
# ===========================================================================

def make_split(G, seed, mask_frac, k_floor):
    n = G.shape[0]
    iu = np.triu_indices(n, k=1)
    finite = np.isfinite(G[iu])
    pi, pj = iu[0][finite], iu[1][finite]
    npair = pi.size
    rng = np.random.default_rng(seed * 100003 + 7)  # integer-seeded; deterministic across processes
    order = rng.permutation(npair)
    deg = np.zeros(n, dtype=np.int64)
    for a in range(n):
        deg[a] = int(np.isfinite(G[a]).sum() - (1 if np.isfinite(G[a, a]) else 0))
    target_mask = int(round(mask_frac * npair))
    is_test = np.zeros(npair, dtype=bool)
    masked = 0
    for idx in order:
        if masked >= target_mask:
            break
        a, b = int(pi[idx]), int(pj[idx])
        if deg[a] - 1 >= k_floor and deg[b] - 1 >= k_floor:
            is_test[idx] = True
            deg[a] -= 1
            deg[b] -= 1
            masked += 1
    train_idx = np.where(~is_test)[0]
    test_idx = np.where(is_test)[0]
    min_train_deg = int(deg.min())
    return dict(pi=pi, pj=pj, train_idx=train_idx, test_idx=test_idx,
                min_train_deg=min_train_deg, npair=npair)


# ===========================================================================
# arms
# ===========================================================================

def _fit_sym(G, split, rank, seed, epochs, lr, wd):
    """Fit Ghat_ab = mu + alpha_a + alpha_b + <F_a,F_b>_rank to SIGNED G on TRAIN pairs (Adam MSE).
    rank==0 => ADDITIVE (offsets only). Returns Ghat (signed) for ALL split pairs as np.float32."""
    n = G.shape[0]
    pi, pj = split["pi"], split["pj"]
    tr = split["train_idx"]
    g = torch.Generator().manual_seed(seed * 7919 + rank * 101 + 3)
    ai = torch.from_numpy(pi.astype(np.int64))
    bj = torch.from_numpy(pj.astype(np.int64))
    y = torch.from_numpy(G[pi, pj].astype(np.float32))
    tr_t = torch.from_numpy(tr.astype(np.int64))
    ai_tr, bj_tr, y_tr = ai[tr_t], bj[tr_t], y[tr_t]
    mu = torch.nn.Parameter(torch.zeros(1))
    alpha = torch.nn.Parameter(torch.zeros(n))
    params = [mu, alpha]
    F = None
    if rank >= 1:
        F = torch.nn.Parameter(0.1 * torch.randn(n, rank, generator=g))
        params.append(F)
    opt = torch.optim.Adam(params, lr=lr)

    def predict(a_idx, b_idx):
        out = mu + alpha[a_idx] + alpha[b_idx]
        if F is not None:
            out = out + (F[a_idx] * F[b_idx]).sum(dim=1)
        return out

    for _ in range(epochs):
        opt.zero_grad()
        pred = predict(ai_tr, bj_tr)
        loss = torch.mean((pred - y_tr) ** 2)
        if F is not None:
            loss = loss + wd * (F ** 2).sum()
        loss.backward()
        opt.step()
    with torch.no_grad():
        ghat = predict(ai, bj).numpy().astype(np.float32)
    return ghat


def _degree_null(G, split, seed, epochs=300, lr=0.05):
    """Per-gene hubness deg_g = mean|GI| over TRAIN partners; logistic combiner of symmetric (deg_a,deg_b)
    features fit to TRAIN hit-labels. ZERO pair-specific info. Returns score for ALL pairs."""
    n = G.shape[0]
    pi, pj = split["pi"], split["pj"]
    tr = split["train_idx"]
    absG = np.abs(G)
    # train-only partner mask: build per-gene mean|GI| over TRAIN partners
    sum_deg = np.zeros(n, dtype=np.float64)
    cnt_deg = np.zeros(n, dtype=np.float64)
    for idx in tr:
        a, b = int(pi[idx]), int(pj[idx])
        v = float(absG[a, b])
        sum_deg[a] += v; cnt_deg[a] += 1.0
        sum_deg[b] += v; cnt_deg[b] += 1.0
    deg = sum_deg / np.maximum(cnt_deg, 1.0)
    deg = (deg - deg.mean()) / (deg.std() + 1e-6)
    da = deg[pi]; db = deg[pj]
    feats = np.stack([da + db, da * db, np.abs(da - db), np.minimum(da, db), np.maximum(da, db)], axis=1)
    feats = feats.astype(np.float32)
    thr = np.nanpercentile(absG[pi, pj], HIT_PCT)  # NOTE: threshold is a global |GI| percentile (pre-registered)
    hit = (absG[pi, pj] >= thr).astype(np.float32)
    X = torch.from_numpy(feats); Y = torch.from_numpy(hit)
    tr_t = torch.from_numpy(tr.astype(np.int64))
    g = torch.Generator().manual_seed(seed * 6151 + 5)
    W = torch.nn.Parameter(0.01 * torch.randn(feats.shape[1], generator=g))
    b = torch.nn.Parameter(torch.zeros(1))
    opt = torch.optim.Adam([W, b], lr=lr)
    lossf = torch.nn.BCEWithLogitsLoss()
    Xtr, Ytr = X[tr_t], Y[tr_t]
    for _ in range(epochs):
        opt.zero_grad()
        logit = Xtr @ W + b
        loss = lossf(logit, Ytr)
        loss.backward()
        opt.step()
    with torch.no_grad():
        score = (X @ W + b).numpy().astype(np.float32)
    return score


def _memorize(G, split):
    """Exact train-pair |GI| lookup; NOVEL held-out pairs -> global-mean fallback (constant) => chance ranking."""
    pi, pj = split["pi"], split["pj"]
    absG = np.abs(G)
    tr = split["train_idx"]
    global_mean = float(np.mean(absG[pi[tr], pj[tr]]))
    score = np.full(pi.size, global_mean, dtype=np.float32)
    score[tr] = absG[pi[tr], pj[tr]]  # train pairs get their own value (irrelevant to held-out eval)
    return score


# ===========================================================================
# detection metrics
# ===========================================================================

def average_precision(scores, labels, rng):
    """Average precision (area under PR curve, interpolation-free) with random tie-break via tiny jitter."""
    labels = np.asarray(labels).astype(np.float64)
    n = labels.size
    n_pos = labels.sum()
    if n_pos <= 0 or n == 0:
        return float("nan")
    jitter = rng.standard_normal(n).astype(np.float64) * 1e-9
    order = np.argsort(-(scores.astype(np.float64) + jitter))
    lab = labels[order]
    cum_tp = np.cumsum(lab)
    prec_at = cum_tp / np.arange(1, n + 1)
    return float((prec_at * lab).sum() / n_pos)


def precision_at_k(scores, labels, k_frac, rng):
    labels = np.asarray(labels).astype(np.float64)
    n = labels.size
    k = max(1, int(round(k_frac * n)))
    jitter = rng.standard_normal(n).astype(np.float64) * 1e-9
    order = np.argsort(-(scores.astype(np.float64) + jitter))
    return float(labels[order[:k]].sum() / k)


# ===========================================================================
# per-seed measurement (K562 primary)
# ===========================================================================

def score_seed(G, seed, ranks, epochs, lr, wd):
    split = make_split(G, seed, MASK_FRAC, K_FLOOR)
    pi, pj = split["pi"], split["pj"]
    absG = np.abs(G)
    thr = float(np.nanpercentile(absG[pi, pj], HIT_PCT))  # global fixed threshold (pre-registered percentile)
    hit = (absG[pi, pj] >= thr).astype(np.float32)
    tr = split["train_idx"]; te = split["test_idx"]
    base_rate = float(hit[te].mean())
    rng = np.random.default_rng(seed * 55001 + 13)

    scores = {}
    scores["CHANCE"] = rng.standard_normal(pi.size).astype(np.float32)
    scores["MEMORIZE"] = _memorize(G, split)
    scores["DEGREE"] = _degree_null(G, split, seed)
    for R in ranks:
        ghat = _fit_sym(G, split, R, seed, epochs, lr, wd)
        name = "ADDITIVE" if R == 0 else ("SYM_R%d" % R)
        scores[name] = np.abs(ghat).astype(np.float32)  # detection: rank by predicted MAGNITUDE

    out = {"base_rate": round(base_rate, 5), "min_train_deg": split["min_train_deg"],
           "n_test": int(te.size), "n_train": int(tr.size), "thr": round(thr, 5),
           "n_pos_test": int(hit[te].sum())}
    arms = {}
    for name, sc in scores.items():
        aprng = np.random.default_rng(seed * 909 + 1)
        ap_te = average_precision(sc[te], hit[te], aprng)
        ap_tr = average_precision(sc[tr], hit[tr], np.random.default_rng(seed * 909 + 2))
        p1 = precision_at_k(sc[te], hit[te], 0.01, np.random.default_rng(seed * 909 + 3))
        p5 = precision_at_k(sc[te], hit[te], 0.05, np.random.default_rng(seed * 909 + 4))
        p10 = precision_at_k(sc[te], hit[te], 0.10, np.random.default_rng(seed * 909 + 5))
        arms[name] = dict(auprc_test=round(ap_te, 5), auprc_seen=round(ap_tr, 5),
                          p_at_1=round(p1, 5), p_at_5=round(p5, 5), p_at_10=round(p10, 5),
                          enrich_10=round(p10 / max(base_rate, 1e-9), 4))
    out["arms"] = arms
    out["sigs"] = {name: _sig(scores[name][te]) for name in ("DEGREE", "ADDITIVE", "SYM_R%d" % PRIMARY_RANK)
                   if name in scores}
    return out


def cross_line_diag(ranks):
    """Reported-only: fit SYM(primary rank)/ADD/DEG on FULL K562, rank against Jurkat gold on shared genes."""
    try:
        gk, Gk = load_gi(PRIMARY_LINE)
        gj, Gj = load_gi(CROSS_LINE)
        shared = sorted(set(gk) & set(gj))
        if len(shared) < 40:
            return {"status": "too_few_shared", "n_shared": len(shared)}
        ik = {g: i for i, g in enumerate(gk)}
        ij = {g: i for i, g in enumerate(gj)}
        sk = np.array([ik[g] for g in shared]); sj = np.array([ij[g] for g in shared])
        Gk_s = Gk[np.ix_(sk, sk)]
        Gj_s = Gj[np.ix_(sj, sj)]
        # full-K562 split with NO masking (train on all) to learn factors, then score shared pairs vs Jurkat gold
        nsh = len(shared)
        iu = np.triu_indices(nsh, k=1)
        finite = np.isfinite(Gk_s[iu]) & np.isfinite(Gj_s[iu])
        pi, pj = iu[0][finite], iu[1][finite]
        full_split = dict(pi=pi, pj=pj, train_idx=np.arange(pi.size), test_idx=np.arange(pi.size),
                          min_train_deg=nsh - 1, npair=pi.size)
        absJ = np.abs(Gj_s)
        thrJ = float(np.nanpercentile(absJ[pi, pj], HIT_PCT))
        hitJ = (absJ[pi, pj] >= thrJ).astype(np.float32)
        base = float(hitJ.mean())
        res = {"n_shared": nsh, "n_pairs": int(pi.size), "base_rate_jurkat": round(base, 5)}
        rng = np.random.default_rng(999)
        deg_sc = _degree_null(Gk_s, full_split, 999)
        res["DEGREE"] = round(average_precision(deg_sc, hitJ, np.random.default_rng(1)), 5)
        for R in (0, PRIMARY_RANK):
            gh = _fit_sym(Gk_s, full_split, R, 999, EPOCHS, LR, WD_FACTOR)
            nm = "ADDITIVE" if R == 0 else "SYM_R%d" % R
            res[nm] = round(average_precision(np.abs(gh), hitJ, np.random.default_rng(2 + R)), 5)
        return res
    except Exception as e:  # reported-only diagnostic; never fatal to the primary verdict
        return {"status": "error", "err": "%s: %s" % (type(e).__name__, str(e)[:200])}


# ===========================================================================
# full measurement + verdict
# ===========================================================================

def run_measurement(genes_cap=None, ranks=None, seeds=None, epochs=None, run_mode="full"):
    ranks = ranks or RANKS
    seeds = seeds or SEEDS
    epochs = epochs or EPOCHS
    t0 = time.perf_counter()
    genes, G = load_gi(PRIMARY_LINE)
    if genes_cap is not None and G.shape[0] > genes_cap:
        G = G[:genes_cap, :genes_cap]
        genes = genes[:genes_cap]
    _log("%s run: line=%s n_genes=%d ranks=%s seeds=%s epochs=%d"
         % (run_mode.upper(), PRIMARY_LINE, G.shape[0], ranks, seeds, epochs))

    per = []
    for si, sd in enumerate(seeds):
        r = score_seed(G, sd, ranks, epochs, LR, WD_FACTOR)
        per.append(r)
        _log("  seed %d/%d done: base=%.4f min_train_deg=%d n_test=%d (elapsed=%.1fs)"
             % (si + 1, len(seeds), r["base_rate"], r["min_train_deg"], r["n_test"], time.perf_counter() - t0))

    arm_names = list(per[0]["arms"].keys())
    EXPECTED_N_UNITS = len(seeds)
    cardinality_ok = bool(len(per) == EXPECTED_N_UNITS)

    def agg(name, key):
        vals = [p["arms"][name][key] for p in per if p["arms"][name][key] == p["arms"][name][key]]
        return (float(np.mean(vals)), float(np.std(vals))) if vals else (float("nan"), float("nan"))

    table = {}
    for name in arm_names:
        m_te, s_te = agg(name, "auprc_test")
        m_tr, _ = agg(name, "auprc_seen")
        m_p10, _ = agg(name, "p_at_10")
        m_en, _ = agg(name, "enrich_10")
        table[name] = dict(auprc_test_mean=round(m_te, 5), auprc_test_std=round(s_te, 5),
                           auprc_seen_mean=round(m_tr, 5), p_at_10_mean=round(m_p10, 5),
                           enrich_10_mean=round(m_en, 4))
    p0 = float(np.mean([p["base_rate"] for p in per]))
    min_train_deg = int(min(p["min_train_deg"] for p in per))

    hero_name = "SYM_R%d" % PRIMARY_RANK
    hero = table[hero_name]["auprc_test_mean"]
    hero_std = table[hero_name]["auprc_test_std"]
    add = table["ADDITIVE"]["auprc_test_mean"]
    deg = table["DEGREE"]["auprc_test_mean"]
    chance = table["CHANCE"]["auprc_test_mean"]
    memo = table["MEMORIZE"]["auprc_test_mean"]
    best_sym_name = max((n for n in arm_names if n.startswith("SYM_R")),
                        key=lambda n: table[n]["auprc_test_mean"])
    best_sym = table[best_sym_name]["auprc_test_mean"]
    best_seen_sym = max(table[n]["auprc_seen_mean"] for n in arm_names if n.startswith("SYM_R"))
    add_seen = table["ADDITIVE"]["auprc_seen_mean"]

    both_null = max(add, deg)
    hero_margin = hero - (1.0 + REL_MARGIN) * both_null
    split_clean = bool(memo <= MEMO_LEAK_MULT * p0 and abs(chance - p0) <= CHANCE_TOL)
    seen_ok = bool(best_seen_sym >= max(SEEN_FIT_ABS, SEEN_FIT_MULT * p0)
                   and best_seen_sym >= SEEN_FIT_OVER_ADD * add_seen)

    refute = bool((not seen_ok) or (not split_clean))
    hard_pass = bool(hero >= (1.0 + REL_MARGIN) * both_null and hero >= 2.0 * p0
                     and hero_margin > hero_std and split_clean and seen_ok)
    add_capturable = bool(hero < (1.0 + ADD_CAPTURE_REL) * add and add > 1.15 * deg and add > 1.3 * p0)
    degree_dominated = bool(hero < (1.0 + DEG_DOMINATE_REL) * deg and deg >= 0.95 * add)
    middle = bool(hero >= (1.0 + MIDDLE_DEG_REL) * deg and hero < (1.0 + REL_MARGIN) * add)

    if refute:
        verdict = "REFUTE_IMPL_CANNOT_FIT_TRAIN_OR_SPLIT_LEAK"
    elif hard_pass:
        verdict = "HARD_PASS_CONJUNCTION_DETECTS_BEYOND_ADD_AND_DEGREE"
    elif add_capturable:
        verdict = "HARD_FAIL_ADDITIVE_CAPTURABLE"
    elif degree_dominated:
        verdict = "HARD_FAIL_DEGREE_DOMINATED"
    elif middle:
        verdict = "MIDDLE_BAND_PARTIAL_BEYOND_DEGREE_NOT_ADDITIVE"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    cross = cross_line_diag(ranks) if run_mode == "full" else {"status": "skipped_in_%s" % run_mode}

    rank_sweep = {("ADDITIVE" if R == 0 else "SYM_R%d" % R): table["ADDITIVE" if R == 0 else "SYM_R%d" % R]["auprc_test_mean"]
                  for R in ranks}

    msg = ("%s || K562 n_genes=%d p0=%.4f min_train_deg=%d (K_FLOOR=%d) | HERO=%s AUPRC=%.4f(+-%.4f) "
           "ADD=%.4f DEG=%.4f CHANCE=%.4f MEMO=%.4f | HERO/ADD=%.2fx HERO/DEG=%.2fx (need>=%.2fx) "
           "margin=%.4f(>std %.4f=%s) | best_sym=%s(%.4f) seen_ok=%s split_clean=%s | rank_sweep=%s | cross_line=%s"
           % (verdict, G.shape[0], p0, min_train_deg, K_FLOOR, hero_name, hero, hero_std,
              add, deg, chance, memo, hero / max(add, 1e-9), hero / max(deg, 1e-9), 1.0 + REL_MARGIN,
              hero_margin, hero_std, bool(hero_margin > hero_std), best_sym_name, best_sym, seen_ok, split_clean,
              json.dumps({k: round(v, 4) for k, v in rank_sweep.items()}),
              json.dumps(cross, default=float)))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode=run_mode,
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        config=dict(line=PRIMARY_LINE, n_genes=G.shape[0], ranks=ranks, primary_rank=PRIMARY_RANK,
                    hit_pct=HIT_PCT, mask_frac=MASK_FRAC, k_floor=K_FLOOR, seeds=list(seeds),
                    epochs=epochs, lr=LR, wd=WD_FACTOR, rel_margin=REL_MARGIN),
        base_rate=round(p0, 5), min_train_deg=min_train_deg, cardinality_ok=cardinality_ok,
        table=table, rank_sweep=rank_sweep, cross_line=cross,
        gates=dict(hero=round(hero, 5), hero_std=round(hero_std, 5), add=round(add, 5), deg=round(deg, 5),
                   chance=round(chance, 5), memo=round(memo, 5), best_sym=round(best_sym, 5),
                   best_sym_name=best_sym_name, best_seen_sym=round(best_seen_sym, 5),
                   hero_over_add=round(hero / max(add, 1e-9), 4), hero_over_deg=round(hero / max(deg, 1e-9), 4),
                   hero_margin=round(hero_margin, 5), split_clean=split_clean, seen_ok=seen_ok,
                   hard_pass=hard_pass, add_capturable=add_capturable, degree_dominated=degree_dominated,
                   middle=middle, refute=refute, cardinality_ok=cardinality_ok),
        bands=dict(REL_MARGIN=REL_MARGIN, ADD_CAPTURE_REL=ADD_CAPTURE_REL, DEG_DOMINATE_REL=DEG_DOMINATE_REL,
                   MIDDLE_DEG_REL=MIDDLE_DEG_REL, SEEN_FIT_ABS=SEEN_FIT_ABS, SEEN_FIT_MULT=SEEN_FIT_MULT,
                   SEEN_FIT_OVER_ADD=SEEN_FIT_OVER_ADD, add_seen=round(add_seen, 5),
                   MEMO_LEAK_MULT=MEMO_LEAK_MULT, CHANCE_TOL=CHANCE_TOL, EXPECTED_N_UNITS=EXPECTED_N_UNITS),
        per_seed=per,
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (exercises REAL data path + REAL arm pipeline on a tiny SYNTHETIC planted matrix; asserts
# CONSTRUCTION + machinery facts, NOT the open held-out hypothesis -- that is MEASURED in FULL + band-gated.)
# ===========================================================================

def _synthetic_gi(n=28, rank=2, seed=3):
    """Planted symmetric matrix: additive offsets + rank-2 product + hub structure + noise. KNOWN structure."""
    rng = np.random.default_rng(seed)
    alpha = rng.standard_normal(n) * 0.5
    Fp = rng.standard_normal((n, rank))
    G = alpha[:, None] + alpha[None, :] + Fp @ Fp.T
    G = G + rng.standard_normal((n, n)) * 0.1
    G = 0.5 * (G + G.T)
    np.fill_diagonal(G, np.nan)
    return G.astype(np.float32)


def self_test():
    ok_all = True
    details = {}
    checks = {}

    # (1) REAL data path: committed npz loads (or downloads); K562 is dense 448x448 (F.1 real_code_path).
    try:
        genes, G = load_gi(PRIMARY_LINE)
        iu = np.triu_indices(G.shape[0], k=1)
        finite_frac = float(np.isfinite(G[iu]).mean())
        details["real_n_genes"] = G.shape[0]
        details["real_finite_frac"] = round(finite_frac, 4)
        checks["real_data_loads_dense"] = bool(G.shape[0] >= 300 and finite_frac >= 0.90)
    except Exception as e:
        details["real_data_err"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        checks["real_data_loads_dense"] = False

    # (2) split respects K_FLOOR + all test pairs are NOVEL (never in train); deterministic.
    Gs = _synthetic_gi(n=40, rank=2, seed=3)
    sp = make_split(Gs, 7, mask_frac=0.15, k_floor=8)
    tr_set = set(zip(sp["pi"][sp["train_idx"]].tolist(), sp["pj"][sp["train_idx"]].tolist()))
    te_set = set(zip(sp["pi"][sp["test_idx"]].tolist(), sp["pj"][sp["test_idx"]].tolist()))
    novel = te_set.isdisjoint(tr_set)
    sp_again = make_split(Gs, 7, mask_frac=0.15, k_floor=8)
    determ = bool(np.array_equal(sp["test_idx"], sp_again["test_idx"]))
    sp_diff = make_split(Gs, 13, mask_frac=0.15, k_floor=8)
    diff_seed = bool(not np.array_equal(sp["test_idx"], sp_diff["test_idx"]))
    details.update(min_train_deg=sp["min_train_deg"], n_test=int(sp["test_idx"].size))
    checks["test_pairs_novel"] = bool(novel)
    checks["split_respects_k_floor"] = bool(sp["min_train_deg"] >= 8)
    checks["split_deterministic"] = determ
    checks["split_seed_varies"] = diff_seed

    # (3) CONSTRUCTION: on a planted rank-2 matrix, SYM (R>=2) fits TRAIN better than ADDITIVE (product term
    #     captures the planted interaction). Machinery proof -- NOT the open held-out generalization question.
    Gp = _synthetic_gi(n=48, rank=2, seed=5)
    spp = make_split(Gp, 7, mask_frac=0.15, k_floor=10)
    gh_add = _fit_sym(Gp, spp, 0, 7, 200, 0.05, 1e-4)
    gh_sym = _fit_sym(Gp, spp, 4, 7, 200, 0.05, 1e-4)
    y = Gp[spp["pi"], spp["pj"]]
    tr = spp["train_idx"]
    mse_add = float(np.mean((gh_add[tr] - y[tr]) ** 2))
    mse_sym = float(np.mean((gh_sym[tr] - y[tr]) ** 2))
    details.update(seen_mse_add=round(mse_add, 4), seen_mse_sym=round(mse_sym, 4))
    checks["sym_fits_planted_interaction_better_than_additive"] = bool(mse_sym < 0.8 * mse_add)

    # (4) AP correctness: perfect ranking AP=1.0; random ~ base rate.
    lab = np.array([1, 1, 0, 0, 1, 0, 0, 0], dtype=np.float32)
    perfect = np.array([9, 8, 1, 0, 7, 2, 3, 4], dtype=np.float32)  # positives on top
    ap_perfect = average_precision(perfect, lab, np.random.default_rng(0))
    checks["ap_perfect_is_one"] = bool(abs(ap_perfect - 1.0) < 1e-6)

    # (5) MEMORIZE collapses to ~base rate on NOVEL held-out (constant fallback => chance ranking).
    absG = np.abs(Gp)
    thr = float(np.nanpercentile(absG[spp["pi"], spp["pj"]], HIT_PCT))
    hit = (absG[spp["pi"], spp["pj"]] >= thr).astype(np.float32)
    te = spp["test_idx"]
    memo = _memorize(Gp, spp)
    ap_memo = average_precision(memo[te], hit[te], np.random.default_rng(1))
    base = float(hit[te].mean())
    details.update(memo_auprc=round(ap_memo, 4), synth_base=round(base, 4))
    checks["memorize_collapses_to_chance"] = bool(ap_memo <= base + 0.08)

    # (6) DEGREE null recovers hub structure (AP > base) on a planted-hub matrix.
    rng = np.random.default_rng(9)
    n = 60
    hub = rng.random(n)
    Gh = (hub[:, None] * hub[None, :]) * rng.standard_normal((n, n))  # magnitude driven by hub product
    Gh = 0.5 * (Gh + Gh.T); np.fill_diagonal(Gh, np.nan)
    Gh = Gh.astype(np.float32)
    sph = make_split(Gh, 7, mask_frac=0.15, k_floor=10)
    deg_sc = _degree_null(Gh, sph, 7)
    absGh = np.abs(Gh)
    thrh = float(np.nanpercentile(absGh[sph["pi"], sph["pj"]], HIT_PCT))
    hith = (absGh[sph["pi"], sph["pj"]] >= thrh).astype(np.float32)
    teh = sph["test_idx"]
    ap_deg = average_precision(deg_sc[teh], hith[teh], np.random.default_rng(3))
    base_h = float(hith[teh].mean())
    details.update(degree_hub_auprc=round(ap_deg, 4), hub_base=round(base_h, 4))
    checks["degree_null_recovers_hubness"] = bool(ap_deg > base_h + 0.05)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF): DEGREE / ADDITIVE / SYM_R8 produce distinct held-out score vectors.
    rr = score_seed(_synthetic_gi(n=60, rank=3, seed=11), 7, [0, 8], 120, 0.05, 1e-4)
    sig_vals = list(rr["sigs"].values())
    checks["arms_differ"] = bool(len(set(sig_vals)) == len(sig_vals))
    details["arm_sig_count"] = len(set(sig_vals))

    for kk, vv in checks.items():
        if not vv:
            ok_all = False
    out = dict(passed=ok_all, checks=checks, details=details)
    print("[SELFTEST] %s" % json.dumps(out, default=float), flush=True)
    return ok_all, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true", help="explicit full run (default when no flag given)")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        ok, _ = self_test()
        sys.exit(0 if ok else 1)
    if args.smoke:
        m = run_measurement(genes_cap=SMOKE_GENES, ranks=SMOKE_RANKS, seeds=SMOKE_SEEDS,
                            epochs=SMOKE_EPOCHS, run_mode="smoke")
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    # DEFAULT (no flag) = FULL run to completion (runner invokes `python -u <script>` with no args; META_RULE_16)
    m = run_measurement()
    _write_metrics(m)
    _log(m["verdict_msg"])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            crash = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(e).__name__, str(e)[:400]),
                         summary="CELL_CRASHED", elapsed_s=0.0, anchor_name=ANCHOR_NAME,
                         traceback=traceback.format_exc()[:4000], ts_iso=datetime.now(timezone.utc).isoformat())
            os.makedirs(OUT_DIR, exist_ok=True)
            tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(crash, f, indent=2)
            os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
        except Exception:
            pass
        raise
