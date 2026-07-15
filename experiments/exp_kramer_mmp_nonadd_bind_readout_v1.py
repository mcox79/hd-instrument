"""KRAMER_MMP_NONADD_BIND_READOUT (v1): THE chain-grade REAL-DATA linchpin + conjunction MODULE #1. Ingest the Kramer et
al. 2021 chemistry matched-molecular-pair (MMP) NONADDITIVITY dataset (J. Cheminformatics 13:48; REAL, publicly-MEASURED
double-transformation-cycle nonadditivity) and test whether the substrate's LEARNED SYMMETRIC BIND (shared per-token code +
ELEMENTWISE-PRODUCT composition = swap-symmetric) READS OUT the genuinely-non-additive 2-way interaction -- the pairwise
Nonadditivity of two substituent transformations (R1,R2) -- on NOVEL held-out transformation-pairs, BEATING a
capacity-matched STRONG categorical additive (per-transformation main effects) by a pre-registered relative-MAE margin,
SPECIFICALLY on the noise-floor-cleared |Nonadd|>0.3 subset. Glass-box CPU, NO LLM at readout. All compute REMOTE (the cell
downloads the CSVs at runtime; remote --self-test is the gate).

WHY (inlined; no re-hunt): two prior LLM-GENERATED conjunction clusters (chem mixing-hazard, epistasis severity) came back
ADDITIVE-CAPTURABLE vs a strong additive -- the narration smuggled in structure a strong additive already captured. Genuine
non-additivity must be INGESTED where it is EMPIRICALLY MEASURED. Kramer 2021 Nonadd is the textbook-purest measured
interaction term: a scalar per double-transformation cycle = pAct2 - pAct1 - pAct3 + pAct4 (deviation from strict additivity
of two substituent transformations), computed by the original statisticians from real assay potencies -- no narration step.

THE MECHANISM x DATA question: LEARN_SYM (shared per-token code + PRODUCT) reads a SYMMETRIC 2-way interaction and
GENERALIZES to NOVEL token-pairs because a shared code + bilinear readout extrapolates where a lookup cannot; a per-token
main-effects ADDITIVE provably loses any irreducible pairwise term. Load-bearing claim: on the genuinely-non-additive
(|Nonadd|>0.3, noise-floor-cleared) subset of NOVEL transformation-pairs, LEARN_SYM beats a capacity-matched STRONG additive
by >=30% relative MAE AND the advantage is MATERIALLY LARGER on |Nonadd|>0.3 than on <0.3 (reads chemistry, not noise).

DATA-STRUCTURE-ADAPTIVE (autonomy per spawn contract -- do NOT force a broken encoding): the 3 Kramer MOESM CSVs are
downloaded + column-probed at runtime.
  PATH A (per-circle / transformation structure present -> cycle constituents R1,R2 identifiable): build entity=(t1,t2)
    unordered transformation-pair, target = the cycle Nonadditivity; run the full SYM-vs-STRONG-additive transfer proof.
  PATH B (per-compound aggregate only: ID,SMILES,VALUE,nOccurence,Nonadd_pC -- no cycle/transformation columns, and R1,R2
    are NOT reconstructible from SMILES without RDKit + MMP fragmentation): emit ESCALATE_KRAMER_PERCOMPOUND_NO_CYCLE_
    STRUCTURE with a crisp diagnostic (columns, row counts, |Nonadd_pC|>0.3 clearance fraction across the 3 ChEMBL assays)
    + hand off the scout fallback (KramerChristian/NonadditivityAnalysis per-circle output, or Costanzo/NCI-ALMANAC). This
    is an HONEST, informative verdict about the dataset's ingestability -- NOT a mechanism refute.

ARMS (regression, MAE lower=better): LEARN_SYM (shared code + PRODUCT = substrate symmetric bind; WINNER hypothesis) ;
  LEARN_ADD (shared code + SUM; matched-capacity LEARNED additive) ; ADD_RIDGE (closed-form ridge on per-token COUNT
  design; STRONG closed-form categorical additive) ; ADD_LSTSQ (closed-form lstsq; additive) ; LEARN_ROLE (role-keyed
  product; ALGEBRA contrast -- must NOT beat SYM on a symmetric target) ; MEAN (predict train-mean Nonadd = the regression
  frequency floor) ; MEMORIZE (per-token-pair mean; rote, collapses to MEAN on NOVEL) ; ORACLE (true; MAE~0).
  strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel(s,sub) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.
STRATA: seen / novel token-pair (entity-level split). SUBSET: hi=|Nonadd|>0.3 (genuine interaction) / lo=<=0.3 (control).
REGIMES: CLEAN(real) ; ARBITRARY (random Nonadd per unique token-pair; must-fail on NOVEL) ; SHUFFLE (target permutation;
  must-fail on ALL). FIXED GATE positive control = planted symmetric-interaction arena (SYM beats strong-additive by its own
  bar); negative control = planted ADDITIVE arena (SYM must NOT beat additive -> proves the gate is NOT saturation-vacuous).

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_kramer_mmp_nonadd_bind_readout.md):
  HARD_PASS_TRANSFER (module #1 = real-data linchpin): novel_hi rel_MAE >= 0.30 AND (novel_hi rel - novel_lo rel) >= 0.15
    AND positive-control passes (planted-interaction rel>=0.30) AND negative-control ok (planted-additive rel<=0.10)
    AND must-fails fire (SHUFFLE all rel_sym_vs_mean<=0.08, ARBITRARY novel rel_sym_vs_mean<=0.08) AND oracle MAE~0
    AND leak_ok AND noise-floor cleared (>=15% of rows |Nonadd|>0.3) AND novel_hi has >=4 mean rows (power).
  HARD_FAIL_INSUFFICIENT_SIGNAL: <15% of rows clear |Nonadd|>0.3 -> ESCALATE to ChEMBL-bulk/Costanzo fallback (domain NOT
    closed). REFUTE_NO_TRANSFER: novel_hi rel_MAE <= 0.05 (collapses to noise) with valid must-fails+oracle.
  MIDDLE_BAND: partial / low-power novel_hi / advantage not materially larger on hi than lo.

Compute architecture: (b) sequential-CPU with justification -- arena is O(1e3) real cycles x a handful of tiny (<=Nx32)
  Adam fits (ms each) + numpy solves; total wall < 3min over 8 seeds; GPU yields no speedup on sub-ms matmuls; dominant cost
  is the 3 CSV HTTP downloads (cached). torch thread-capped (HDI_TORCH_THREADS default 2). Storage: no_storage /
  no_composition (single-hop readout). Determinism: FIXED int seeds + stable sorted-unique token-pair ids; NO hash(), NO
  list(set()) (PROT-023). ASCII-only; no bare except; except SystemExit before except Exception; atomic tmp+os.replace.
  Default invocation (no flag) = FULL run to completion (download + adaptive path + gate).
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke/self-test (META_RULE_AF; float-hash arms-differ on planted + real data)
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: regression MAE floor is data-noise-defined (assay reproducibility ~0.3 log); no closed-form CRLB for the
#     bilinear-readout arm; the NOISE_FLOOR=0.3 subset + rel-MAE-reduction gate substitute for a capacity-feasibility cap.
# - baseline_in_band: STRONG additive MAE is measured (not saturated); positive/negative planted controls bound the gate.
# - discriminator survives scale: self-test fires SYM>>additive on planted-interaction SEEN at plant scale (n=600).
# - HARD_PASS strictly above floor: rel>=0.30 AND hi-minus-lo>=0.15 (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive only; MEAN/MEMO/ORACLE/ROLE are contrast arms.
# - cardinality_ok: n_seeds x n_regimes fixed; verdict counts per_seed_regime lengths.
# - per-unit failure-class instrumentation: acquire/parse failures -> explicit ACQUIRE_FAILED / ESCALATE verdicts.
# - calibration_check: adaptive_with_discriminator_gate (NOISE_FLOOR=0.3 from source-paper assay reproducibility; the
#     hi-minus-lo>=0.15 gate is the discriminator-still-fires verification).
# - all numbers in comments tagged CITED@ (scout drill) / THEORETICAL@ / to-be-MEASURED@ (real-data pending remote run).
# - real_code_path: self-test parses SYNTHETIC per-circle rows through the REAL parser + runs planted arenas through the
#     REAL score()/arm code; hd_bind exercised on complex64 phasors.
# - deterministic_seeding: FIXED int seeds; sorted(set()) token ids; no hash()/list(set()).

import argparse
import csv
import hashlib
import io
import json
import math
import os
import sys
import time
import traceback
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("HDI_TORCH_THREADS", "2")))

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.binding import bind as hd_bind  # noqa: E402  # REAL substrate bind (complex64 FHRR elementwise multiply); the
# elementwise-PRODUCT LEARN_SYM composition IS this op. Self-test exercises hd_bind on complex64 unit phasors.

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "kramer_mmp_nonadd_bind_readout_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CACHE_DIR = os.path.join(_REPO, "data", "foundation_clusters", "kramer2021_mmp_nonadd")

# ---- data source (Kramer et al. 2021, J. Cheminformatics 13:48; doi 10.1186/s13321-021-00525-z) ----
# CITED@ notes/drill_real_nonadditive_experimental_datasets_for_conjunction_modules_2026-07-15.md (verified-live,
# unauthenticated Springer static-content URLs; header ID,SMILES,VALUE,nOccurence,Nonadd_pC).
KRAMER_URLS = [
    ("MOESM2_chembl1613797",
     "https://static-content.springer.com/esm/art%3A10.1186%2Fs13321-021-00525-z/MediaObjects/"
     "13321_2021_525_MOESM2_ESM.csv"),
    ("MOESM3_chembl1614027",
     "https://static-content.springer.com/esm/art%3A10.1186%2Fs13321-021-00525-z/MediaObjects/"
     "13321_2021_525_MOESM3_ESM.csv"),
    ("MOESM4_chembl1613777",
     "https://static-content.springer.com/esm/art%3A10.1186%2Fs13321-021-00525-z/MediaObjects/"
     "13321_2021_525_MOESM4_ESM.csv"),
]
NONADD_DEF = ("Nonadditivity = deviation from strict additivity in a double-transformation cycle: "
              "pAct2 - pAct1 - pAct3 + pAct4 (Kramer 2019 JCIM 59:4034; Kramer 2021 JCheminform 13:48).")

# ---- arms ----
SYM = "LEARN_SYM"; ADD = "LEARN_ADD"; ROLE = "LEARN_ROLE"; ADDR = "ADD_RIDGE"; ADDLS = "ADD_LSTSQ"
MEAN = "MEAN"; MEMO = "MEMORIZE"; ORC = "ORACLE"
ARM_NAMES = [SYM, ADD, ROLE, ADDR, ADDLS, MEAN, MEMO, ORC]
ADDITIVE_ARMS = [ADD, ADDR, ADDLS]

# ---- regimes (stable enumerated indices; NO hash()) ----
CLEAN = "CLEAN_REAL"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- learned-arm hyperparams (fixed) ----
EMB_D = 32
EPOCHS = 600
LR = 0.03
QUERY_FRAC = 0.40

# ---- pre-registered bands (fixed BEFORE running) ----
NOISE_FLOOR = 0.30           # |Nonadd|>0.30 = noise-floor-cleared (source-paper assay reproducibility ~0.3 log units)
MIN_HI_FRAC = 0.15           # >=15% of rows must clear the noise floor else HARD_FAIL_INSUFFICIENT -> escalate
HP_REL_HI = 0.30             # novel_hi rel_MAE reduction (SYM vs strong additive) >= 0.30
HP_HI_MINUS_LO = 0.15        # advantage materially larger on hi than lo: rel_hi - rel_lo >= 0.15
REFUTE_REL = 0.05            # novel_hi rel_MAE <= 0.05 => collapses to noise => REFUTE
MUSTFAIL_REL_TOL = 0.08      # SHUFFLE(all)+ARBITRARY(novel) rel_sym_vs_mean ceiling
MIN_NOVEL_HI_N = 4.0         # mean novel-hi query rows for adequate power
POS_CTRL_REL = 0.30          # planted-interaction SEEN rel_MAE (positive control must clear its own bar)
NEG_CTRL_REL = 0.10          # planted-additive SEEN rel_MAE ceiling (gate not saturation-vacuous)

SEEDS_FULL = (7, 13, 17, 23, 29, 31, 37, 41)
SEEDS_SMOKE = (7, 13, 17)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _sig_f(arr):
    return hashlib.sha256(np.round(np.asarray(arr, dtype=np.float64), 6).tobytes()).hexdigest()[:16]


def _write_start_marker(expected_n_units, run_mode):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


# ===========================================================================
# ACQUIRE (download-if-absent; urllib stdlib, no requests dep; cache + provenance)
# ===========================================================================

def _download_one(url, dest, timeout=60, retries=2):
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hd-instrument-foundation-ingest/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)
            return len(data), None
        except Exception as e:  # network/HTTP; record + retry
            last = "%s: %s" % (type(e).__name__, str(e)[:200])
            time.sleep(1.5 * (attempt + 1))
    return 0, last


def acquire():
    """Download-if-absent the 3 Kramer MOESM CSVs -> CACHE_DIR. Returns (files, provenance). files: list of
    (tag, path, n_bytes). Records provenance JSON (URLs, retrieval ts, Nonadd definition)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    files = []
    errors = {}
    for tag, url in KRAMER_URLS:
        dest = os.path.join(CACHE_DIR, tag + ".csv")
        if os.path.exists(dest) and os.path.getsize(dest) > 64:
            files.append((tag, dest, os.path.getsize(dest)))
            _log("ACQUIRE cache-hit %s (%d bytes)" % (tag, os.path.getsize(dest)))
            continue
        nbytes, err = _download_one(url, dest)
        if err is None and nbytes > 64:
            files.append((tag, dest, nbytes))
            _log("ACQUIRE downloaded %s (%d bytes)" % (tag, nbytes))
        else:
            errors[tag] = err or ("too_small:%d" % nbytes)
            _log("ACQUIRE FAILED %s : %s" % (tag, errors[tag]))
    prov = dict(dataset="Kramer2021_MMP_nonadditivity", doi="10.1186/s13321-021-00525-z",
                paper="J. Cheminformatics 13:48", urls=dict(KRAMER_URLS),
                retrieval_ts=datetime.now(timezone.utc).isoformat(), nonadditivity_definition=NONADD_DEF,
                files=[dict(tag=t, path=os.path.relpath(p, _REPO), bytes=n) for (t, p, n) in files],
                acquire_errors=errors, source_note="verified-live unauthenticated Springer static-content URLs")
    try:
        with open(os.path.join(CACHE_DIR, "provenance.json"), "w", encoding="utf-8") as f:
            json.dump(prov, f, indent=2)
    except OSError:
        pass
    return files, prov


# ===========================================================================
# PARSE + STRUCTURE DETECTION (per-circle -> PATH A ; per-compound -> PATH B escalate)
# ===========================================================================

# permissive transformation-pair column-name candidates (case-insensitive, stripped)
_TRANSF_PAIRS = [
    ("transformation1", "transformation2"), ("transformation_1", "transformation_2"),
    ("transf1", "transf2"), ("transformation1_smirks", "transformation2_smirks"),
    ("smirks1", "smirks2"), ("t1", "t2"), ("frag1", "frag2"), ("r1", "r2"),
]
_NONADD_COLS = ["nonadditivity", "nonadd", "nonadd_pc", "nonadditivity_pc", "delta_delta", "ddg"]
_PERCOMPOUND_COLS = {"id", "smiles", "value", "nooccurence", "noccurence", "noccurrence", "nonadd_pc"}


def _norm(s):
    return str(s).strip().lower().replace(" ", "_")


def detect_structure(header):
    """Return ('per_circle', {'t1':col,'t2':col,'nonadd':col}) | ('per_compound', {'nonadd':col}) | ('unknown', {})."""
    cols = {_norm(h): h for h in header}
    nonadd_col = None
    for c in _NONADD_COLS:
        if c in cols:
            nonadd_col = cols[c]
            break
    for (a, b) in _TRANSF_PAIRS:
        if a in cols and b in cols and nonadd_col is not None:
            return "per_circle", {"t1": cols[a], "t2": cols[b], "nonadd": nonadd_col}
    normset = set(cols.keys())
    if normset & _PERCOMPOUND_COLS and (("nonadd_pc" in cols) or nonadd_col is not None):
        return "per_compound", {"nonadd": cols.get("nonadd_pc", nonadd_col), "smiles": cols.get("smiles"),
                                "value": cols.get("value")}
    return "unknown", {}


def _read_rows(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        header = rdr.fieldnames or []
        rows = [r for r in rdr]
    return header, rows


def parse_circles(rows, colmap, tok_prefix, tok_map):
    """From per-circle dict rows -> list of (t1_id, t2_id, nonadd_float). tok_map is a running {token->id} (namespaced)."""
    out = []
    for r in rows:
        try:
            na = float(r[colmap["nonadd"]])
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(na):
            continue
        a = tok_prefix + "::" + str(r.get(colmap["t1"], "")).strip()
        b = tok_prefix + "::" + str(r.get(colmap["t2"], "")).strip()
        if a == (tok_prefix + "::") or b == (tok_prefix + "::"):
            continue
        for t in (a, b):
            if t not in tok_map:
                tok_map[t] = len(tok_map)
        out.append((tok_map[a], tok_map[b], na))
    return out


def load_kramer(files):
    """Adaptive loader. Returns dict:
       {'path':'A'|'B'|'ACQUIRE_FAIL', ... }
       PATH A: X (n,2) int token-pair ids, y (n,) float Nonadd, n_tok int, per_assay diagnostics.
       PATH B: per-compound diagnostics (columns, counts, |Nonadd_pC|>0.3 fraction per assay)."""
    if not files:
        return {"path": "ACQUIRE_FAIL"}
    tok_map = {}
    circle_rows = []
    per_assay = []
    percompound_nonadd = []
    any_per_circle = False
    all_per_compound = True
    for (tag, path, nbytes) in files:
        try:
            header, rows = _read_rows(path)
        except (OSError, UnicodeDecodeError, csv.Error) as e:
            per_assay.append(dict(tag=tag, error="%s: %s" % (type(e).__name__, str(e)[:120])))
            continue
        kind, colmap = detect_structure(header)
        info = dict(tag=tag, kind=kind, header=header[:20], n_rows=len(rows))
        if kind == "per_circle":
            any_per_circle = True
            all_per_compound = False
            trip = parse_circles(rows, colmap, tag, tok_map)
            info["n_cycles_parsed"] = len(trip)
            circle_rows.extend(trip)
            if trip:
                mags = np.abs(np.array([t[2] for t in trip], dtype=np.float64))
                info["hi_frac"] = float((mags > NOISE_FLOOR).mean())
        elif kind == "per_compound":
            na_col = colmap.get("nonadd")
            vals = []
            for r in rows:
                try:
                    v = float(r[na_col])
                    if math.isfinite(v):
                        vals.append(v)
                except (KeyError, TypeError, ValueError):
                    continue
            info["n_nonadd_values"] = len(vals)
            if vals:
                a = np.abs(np.array(vals, dtype=np.float64))
                info["hi_frac"] = float((a > NOISE_FLOOR).mean())
                info["nonadd_abs_mean"] = float(a.mean())
                percompound_nonadd.extend(vals)
        else:
            all_per_compound = False
        per_assay.append(info)

    if any_per_circle and len(circle_rows) >= 40:
        X = np.array([[a, b] for (a, b, _na) in circle_rows], dtype=np.int64)
        # canonical unordered token-pair
        X = np.stack([np.minimum(X[:, 0], X[:, 1]), np.maximum(X[:, 0], X[:, 1])], axis=1)
        y = np.array([na for (_a, _b, na) in circle_rows], dtype=np.float64)
        return {"path": "A", "X": X, "y": y, "n_tok": len(tok_map), "per_assay": per_assay,
                "n_cycles": int(X.shape[0])}
    diag_hi_frac = None
    if percompound_nonadd:
        a = np.abs(np.array(percompound_nonadd, dtype=np.float64))
        diag_hi_frac = float((a > NOISE_FLOOR).mean())
    return {"path": "B", "per_assay": per_assay, "all_per_compound": bool(all_per_compound),
            "n_percompound_nonadd": len(percompound_nonadd), "percompound_hi_frac": diag_hi_frac}


# ===========================================================================
# REGRESSION ARMS (shared-product = symmetric bind ; shared-sum = additive ; role-product = asymmetric)
# ===========================================================================

def _train_reg(Xtr, ytr, Xq, mode, seed, n_tok):
    """mode: 'sym' (SHARED code + elementwise PRODUCT = swap-symmetric bind) | 'add' (SHARED code + SUM = additive) |
    'role' (ROLE-KEYED code + PRODUCT = asymmetric). Standardized-target MSE Adam; linear scalar readout."""
    g = torch.Generator().manual_seed(seed * 7919 + {"sym": 3, "add": 2, "role": 1}[mode])
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr.astype(np.float64)).to(torch.float32)
    ymu = yt.mean(); ysd = yt.std() + 1e-3
    ytn = (yt - ymu) / ysd
    k = Xtr.shape[1]  # == 2
    product = (mode in ("sym", "role"))
    if mode == "role":
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(k, n_tok, EMB_D, generator=g))
    else:
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(n_tok, EMB_D, generator=g))
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, 1, generator=g))
    b = torch.nn.Parameter(torch.zeros(1))
    opt = torch.optim.Adam([emb, W, b], lr=LR)

    def compose(Xi):
        if mode == "role":
            e = emb[torch.arange(k).unsqueeze(0), Xi]
        else:
            e = emb[Xi]
        return e.prod(dim=1) if product else e.sum(dim=1)

    for _ in range(EPOCHS):
        opt.zero_grad()
        h = compose(Xt)
        mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        pred = (((h - mu) / sd) @ W + b).squeeze(1)
        loss = ((pred - ytn) ** 2).mean()
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = compose(Xt); mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        predq = (((compose(Xu) - mu) / sd) @ W + b).squeeze(1)
        return (predq * ysd + ymu).numpy().astype(np.float64)


def _design(Xm, n_tok):
    """Per-token COUNT design (n x n_tok+1): col 1+t = count of token t in the pair (0/1/2); col0 intercept."""
    D = np.zeros((Xm.shape[0], n_tok + 1), dtype=np.float64)
    D[:, 0] = 1.0
    for r in range(Xm.shape[0]):
        D[r, 1 + int(Xm[r, 0])] += 1.0
        D[r, 1 + int(Xm[r, 1])] += 1.0
    return D


def arm_add_ridge(Xtr, ytr, Xq, n_tok, l2=1.0):
    """STRONG closed-form categorical additive: ridge regression on per-token count main-effects."""
    D = _design(Xtr, n_tok)
    A = D.T @ D + l2 * np.eye(D.shape[1])
    beta = np.linalg.solve(A, D.T @ ytr.astype(np.float64))
    return (_design(Xq, n_tok) @ beta).astype(np.float64)


def arm_add_lstsq(Xtr, ytr, Xq, n_tok):
    """Closed-form additive (lstsq) on per-token count main-effects."""
    beta, _, _, _ = np.linalg.lstsq(_design(Xtr, n_tok), ytr.astype(np.float64), rcond=None)
    return (_design(Xq, n_tok) @ beta).astype(np.float64)


def arm_memorize(Xtr, ytr, Xq, global_mean):
    combo = defaultdict(list)
    for r in range(Xtr.shape[0]):
        combo[(int(Xtr[r, 0]), int(Xtr[r, 1]))].append(float(ytr[r]))
    preds = []
    for q in range(Xq.shape[0]):
        vv = combo.get((int(Xq[q, 0]), int(Xq[q, 1])))
        preds.append(float(np.mean(vv)) if vv else global_mean)
    return np.array(preds, dtype=np.float64)


def mae(pred, gold, m):
    if m.sum() == 0:
        return float("nan")
    return float(np.abs(np.asarray(pred)[m] - np.asarray(gold)[m]).mean())


# ===========================================================================
# regimes + split
# ===========================================================================

def make_regime_target(X, y_real, regime, seed):
    n = X.shape[0]
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ARBITRARY:
        rng = np.random.default_rng(seed * 100057 + REG_IDX[regime] * 131 + 17)
        uniq = sorted(set((int(X[i, 0]), int(X[i, 1])) for i in range(n)))
        lo, hi = float(np.min(y_real)), float(np.max(y_real))
        lab = {t: float(rng.uniform(lo, hi)) for t in uniq}
        y = np.array([lab[(int(X[i, 0]), int(X[i, 1]))] for i in range(n)], dtype=np.float64)
        return y, y.copy()
    if regime == SHUFFLE:
        rng = np.random.default_rng(seed * 100057 + REG_IDX[regime] * 131 + 17)
        return y_real[rng.permutation(n)].copy(), y_real.copy()
    raise ValueError(regime)


def split_query(X, seed):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100081 + 13)
    perm = rng.permutation(n)
    nq = max(1, int(round(QUERY_FRAC * n)))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_pairs = set((int(X[i, 0]), int(X[i, 1])) for i in tr)
    seen = np.array([(int(X[i, 0]), int(X[i, 1])) in train_pairs for i in q], dtype=bool)
    return q, tr, seen, train_pairs


def score(X, y_real, regime, seed, n_tok):
    q, tr, seen, train_pairs = split_query(X, seed)
    y_used, y_oracle = make_regime_target(X, y_real, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    gmean = float(np.mean(ytr))
    mag = np.abs(y_real[q])  # subset membership defined on the REAL Nonadd magnitude

    preds = {
        SYM: _train_reg(Xtr, ytr, Xq, "sym", seed, n_tok),
        ADD: _train_reg(Xtr, ytr, Xq, "add", seed, n_tok),
        ROLE: _train_reg(Xtr, ytr, Xq, "role", seed, n_tok),
        ADDR: arm_add_ridge(Xtr, ytr, Xq, n_tok),
        ADDLS: arm_add_lstsq(Xtr, ytr, Xq, n_tok),
        MEMO: arm_memorize(Xtr, ytr, Xq, gmean),
        MEAN: np.full(Xq.shape[0], gmean, dtype=np.float64),
        ORC: y_oracle[q].astype(np.float64),
    }
    leak_ok = (len(set(q.tolist()) & set(tr.tolist())) == 0
               and all(((int(Xq[i, 0]), int(Xq[i, 1])) not in train_pairs) for i in range(len(q)) if not seen[i]))

    hi = mag > NOISE_FLOOR
    lo = ~hi
    allm = np.ones(len(gold), dtype=bool)
    out = {}
    for sname, smask in (("seen", seen), ("novel", ~seen), ("all", allm)):
        out[sname] = {}
        for subn, submask in (("hi", hi), ("lo", lo), ("full", allm)):
            m = smask & submask
            d = {arm: mae(preds[arm], gold, m) for arm in preds}
            adds = [d[a] for a in ADDITIVE_ARMS if d[a] == d[a]]
            d["STRONG_ADD"] = float(min(adds)) if adds else float("nan")
            d["n"] = int(m.sum())
            out[sname][subn] = d
    sigs = {arm: _sig_f(preds[arm]) for arm in (SYM, ADD, ROLE, ADDR, ADDLS, MEMO)}
    return dict(strata=out, sigs=sigs, leak_ok=bool(leak_ok),
                n_seen=int(seen.sum()), n_novel=int((~seen).sum()))


def _rel(strong_add_mae, sym_mae):
    if not (strong_add_mae == strong_add_mae) or strong_add_mae <= 1e-9:
        return float("nan")
    return (strong_add_mae - sym_mae) / strong_add_mae


# ===========================================================================
# planted arenas (positive control = interaction ; negative control = additive)
# ===========================================================================

def _plant_reg(n, seed, mode, n_tok=8):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, n_tok, size=n); b = rng.integers(0, n_tok, size=n)
    X = np.stack([np.minimum(a, b), np.maximum(a, b)], axis=1).astype(np.int64)
    if mode == "interaction":
        tab = rng.normal(0.0, 1.0, size=(n_tok, n_tok)); tab = 0.5 * (tab + tab.T)  # symmetric 2-way interaction
        y = np.array([tab[int(X[i, 0]), int(X[i, 1])] for i in range(n)], dtype=np.float64)
    else:
        w = rng.normal(0.0, 1.0, size=n_tok)
        y = np.array([w[int(X[i, 0])] + w[int(X[i, 1])] for i in range(n)], dtype=np.float64)
    y = y + 0.05 * rng.normal(0.0, 1.0, size=n)
    return X, y


def _control_rel(mode, seeds=(7, 13, 17), n_tok=8):
    X, y = _plant_reg(600, {"interaction": 7, "additive": 11}[mode], mode, n_tok)
    rs = [score(X, y, CLEAN, sd, n_tok) for sd in seeds]
    sym = float(np.mean([r["strata"]["seen"]["full"][SYM] for r in rs]))
    sadd = float(np.mean([r["strata"]["seen"]["full"]["STRONG_ADD"] for r in rs]))
    return _rel(sadd, sym), sym, sadd


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds, run_mode):
    _write_start_marker(expected_n_units=len(seeds) * len(REGIMES), run_mode=run_mode)
    t0 = time.perf_counter()
    files, prov = acquire()
    data = load_kramer(files)
    base = dict(run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
                elapsed_s=round(time.perf_counter() - t0, 2), provenance=prov, seeds=list(seeds),
                bands=dict(NOISE_FLOOR=NOISE_FLOOR, MIN_HI_FRAC=MIN_HI_FRAC, HP_REL_HI=HP_REL_HI,
                           HP_HI_MINUS_LO=HP_HI_MINUS_LO, REFUTE_REL=REFUTE_REL, MUSTFAIL_REL_TOL=MUSTFAIL_REL_TOL,
                           MIN_NOVEL_HI_N=MIN_NOVEL_HI_N, POS_CTRL_REL=POS_CTRL_REL, NEG_CTRL_REL=NEG_CTRL_REL))

    # positive/negative controls (planted; the FIXED gate carries a genuine non-additive positive control)
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    pos_ok = bool(pos_rel == pos_rel and pos_rel >= POS_CTRL_REL)
    neg_ok = bool(neg_rel == neg_rel and neg_rel <= NEG_CTRL_REL)
    base["controls"] = dict(pos_rel=round(pos_rel, 5), pos_sym_mae=round(pos_sym, 5), pos_sadd_mae=round(pos_sadd, 5),
                            neg_rel=round(neg_rel, 5), neg_sym_mae=round(neg_sym, 5), neg_sadd_mae=round(neg_sadd, 5),
                            pos_ok=pos_ok, neg_ok=neg_ok)

    if data["path"] == "ACQUIRE_FAIL":
        msg = ("ACQUIRE_FAILED || could not download any Kramer MOESM CSV (see provenance.acquire_errors). "
               "pos_ctrl_rel=%s neg_ctrl_rel=%s (machinery %s)." %
               (_fmt(pos_rel), _fmt(neg_rel), "VALID" if (pos_ok and neg_ok) else "CHECK"))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200])
        return base

    if data["path"] == "B":
        hf = data.get("percompound_hi_frac")
        rec = ("ChEMBL-bulk NonadditivityAnalysis per-circle output (KramerChristian/NonadditivityAnalysis) which "
               "carries Transformation1/2 columns, OR Costanzo yeast SGA / NCI-ALMANAC fallback")
        msg = ("ESCALATE_KRAMER_PERCOMPOUND_NO_CYCLE_STRUCTURE || the 3 Kramer MOESM CSVs are per-COMPOUND aggregate "
               "(ID,SMILES,VALUE,nOccurence,Nonadd_pC) with NO cycle/transformation columns; R1,R2 are NOT "
               "reconstructible without RDKit+MMP fragmentation (not forcing a broken SMILES encoding). "
               "per-compound |Nonadd_pC|>%.2f fraction=%s over n=%d values. HAND-OFF: %s. pos_ctrl_rel=%s neg_ctrl_rel=%s"
               % (NOISE_FLOOR, _fmt(hf) if hf is not None else "n/a", data.get("n_percompound_nonadd", 0),
                  rec, _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ESCALATE_KRAMER_PERCOMPOUND_NO_CYCLE_STRUCTURE", verdict_msg=msg, summary=msg[:200],
                    escalate=True, path="B", per_assay=data["per_assay"],
                    percompound_hi_frac=hf, n_percompound_nonadd=data.get("n_percompound_nonadd", 0))
        return base

    # ---------- PATH A: real per-circle transfer proof ----------
    X, y, n_tok = data["X"], data["y"], data["n_tok"]
    frac_hi = float((np.abs(y) > NOISE_FLOOR).mean())
    _log("PATH A: n_cycles=%d n_tok=%d frac_hi(|Nonadd|>%.2f)=%.3f seeds=%d"
         % (X.shape[0], n_tok, NOISE_FLOOR, frac_hi, len(seeds)))

    per = {reg: [] for reg in REGIMES}
    for si, sd in enumerate(seeds):
        for reg in REGIMES:
            per[reg].append(score(X, y, reg, sd, n_tok))
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def m_mae(reg, stratum, sub, arm):
        vals = [ps["strata"][stratum][sub][arm] for ps in per[reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    def m_n(reg, stratum, sub):
        return float(np.mean([ps["strata"][stratum][sub]["n"] for ps in per[reg]]))

    def rel_at(stratum, sub):
        return _rel(m_mae(CLEAN, stratum, sub, "STRONG_ADD"), m_mae(CLEAN, stratum, sub, SYM))

    novel_hi_rel = rel_at("novel", "hi")
    novel_lo_rel = rel_at("novel", "lo")
    seen_hi_rel = rel_at("seen", "hi")
    seen_full_rel = rel_at("seen", "full")
    role_hi_rel = _rel(m_mae(CLEAN, "seen", "hi", "STRONG_ADD"), m_mae(CLEAN, "seen", "hi", ROLE))
    novel_hi_n = m_n(CLEAN, "novel", "hi")

    # must-fails (regression): SYM must NOT beat the MEAN predictor on shuffled/arbitrary targets
    def rel_sym_vs_mean(reg, stratum, sub):
        return _rel(m_mae(reg, stratum, sub, MEAN), m_mae(reg, stratum, sub, SYM))

    shuf_rel = rel_sym_vs_mean(SHUFFLE, "all", "full")
    arb_rel = rel_sym_vs_mean(ARBITRARY, "novel", "full")
    orc_mae = m_mae(CLEAN, "all", "full", ORC)
    leak_ok = all(ps["leak_ok"] for reg in REGIMES for ps in per[reg])

    mustfails_ok = bool((not (shuf_rel == shuf_rel) or shuf_rel <= MUSTFAIL_REL_TOL)
                        and (not (arb_rel == arb_rel) or arb_rel <= MUSTFAIL_REL_TOL))
    oracle_ok = bool(orc_mae == orc_mae and orc_mae <= 1e-6)
    algebra_ok = bool(not (role_hi_rel == role_hi_rel) or (novel_hi_rel == novel_hi_rel and role_hi_rel == role_hi_rel
                      and novel_hi_rel >= role_hi_rel - 0.10) or seen_hi_rel >= role_hi_rel - 0.10)
    noise_floor_ok = bool(frac_hi >= MIN_HI_FRAC)
    power_ok = bool(novel_hi_n >= MIN_NOVEL_HI_N)
    hi_gt_lo = bool(novel_hi_rel == novel_hi_rel and novel_lo_rel == novel_lo_rel
                    and (novel_hi_rel - novel_lo_rel) >= HP_HI_MINUS_LO)
    rel_hi_pass = bool(novel_hi_rel == novel_hi_rel and novel_hi_rel >= HP_REL_HI)

    hard_pass = bool(rel_hi_pass and hi_gt_lo and pos_ok and neg_ok and mustfails_ok and oracle_ok
                     and leak_ok and noise_floor_ok and power_ok)
    refute = bool(novel_hi_rel == novel_hi_rel and novel_hi_rel <= REFUTE_REL and mustfails_ok and oracle_ok
                  and pos_ok and neg_ok and noise_floor_ok and power_ok)

    if not (pos_ok and neg_ok):
        verdict = "INCONCLUSIVE_CONTROL_GATE_INVALID"
    elif not oracle_ok:
        verdict = "INCONCLUSIVE_ORACLE_MALFORMED"
    elif not mustfails_ok:
        verdict = "INCONCLUSIVE_MUSTFAIL_LEAK"
    elif not noise_floor_ok:
        verdict = "HARD_FAIL_INSUFFICIENT_SIGNAL_ESCALATE_TO_CHEMBL_BULK_OR_COSTANZO"
    elif not power_ok:
        verdict = "MIDDLE_BAND_LOW_POWER_NOVEL_HI"
    elif hard_pass:
        verdict = "HARD_PASS_TRANSFER_SYMMETRIC_BIND_READS_REAL_MMP_NONADDITIVITY"
    elif refute:
        verdict = "REFUTE_NO_TRANSFER_SYM_DOES_NOT_READ_MMP_NONADDITIVITY"
    else:
        verdict = "MIDDLE_BAND"
        if rel_hi_pass and not hi_gt_lo:
            verdict += "_ADVANTAGE_NOT_HI_SPECIFIC"

    msg = ("%s || PATH_A n_cycles=%d n_tok=%d frac_hi=%.3f | NOVEL_HI rel_MAE=%s(>=%.2f) NOVEL_LO rel=%s "
           "(hi-lo=%s>=%.2f) SEEN_HI rel=%s | SYM/SADD novel_hi=%s/%s | POS_ctrl_rel=%s(>=%.2f ok=%s) "
           "NEG_ctrl_rel=%s(<=%.2f ok=%s) | MUSTFAIL shuf=%s arb=%s(<=%.2f) oracle_mae=%s leak=%s | "
           "novel_hi_n=%.1f power=%s noise_floor=%s"
           % (verdict, X.shape[0], n_tok, frac_hi, _fmt(novel_hi_rel), HP_REL_HI, _fmt(novel_lo_rel),
              _fmt(novel_hi_rel - novel_lo_rel) if (novel_hi_rel == novel_hi_rel and novel_lo_rel == novel_lo_rel)
              else "nan", HP_HI_MINUS_LO, _fmt(seen_hi_rel),
              _fmt(m_mae(CLEAN, "novel", "hi", SYM)), _fmt(m_mae(CLEAN, "novel", "hi", "STRONG_ADD")),
              _fmt(pos_rel), POS_CTRL_REL, pos_ok, _fmt(neg_rel), NEG_CTRL_REL, neg_ok,
              _fmt(shuf_rel), _fmt(arb_rel), MUSTFAIL_REL_TOL, _fmt(orc_mae), leak_ok, novel_hi_n, power_ok,
              noise_floor_ok))

    base.update(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], path="A", escalate=False,
        n_cycles=int(X.shape[0]), n_tok=int(n_tok), frac_hi=round(frac_hi, 5),
        per_assay=data["per_assay"],
        clean=dict(
            novel_hi_rel=round(novel_hi_rel, 5) if novel_hi_rel == novel_hi_rel else None,
            novel_lo_rel=round(novel_lo_rel, 5) if novel_lo_rel == novel_lo_rel else None,
            seen_hi_rel=round(seen_hi_rel, 5) if seen_hi_rel == seen_hi_rel else None,
            seen_full_rel=round(seen_full_rel, 5) if seen_full_rel == seen_full_rel else None,
            role_hi_rel=round(role_hi_rel, 5) if role_hi_rel == role_hi_rel else None,
            sym_novel_hi_mae=round(m_mae(CLEAN, "novel", "hi", SYM), 5),
            strong_add_novel_hi_mae=round(m_mae(CLEAN, "novel", "hi", "STRONG_ADD"), 5),
            mean_novel_hi_mae=round(m_mae(CLEAN, "novel", "hi", MEAN), 5),
            memo_novel_hi_mae=round(m_mae(CLEAN, "novel", "hi", MEMO), 5),
            sym_seen_hi_mae=round(m_mae(CLEAN, "seen", "hi", SYM), 5),
            strong_add_seen_hi_mae=round(m_mae(CLEAN, "seen", "hi", "STRONG_ADD"), 5),
            novel_hi_n=round(novel_hi_n, 2), seen_hi_n=round(m_n(CLEAN, "seen", "hi"), 2)),
        gates=dict(rel_hi_pass=rel_hi_pass, hi_gt_lo=hi_gt_lo, pos_ok=pos_ok, neg_ok=neg_ok,
                   mustfails_ok=mustfails_ok, oracle_ok=oracle_ok, leak_ok=leak_ok, noise_floor_ok=noise_floor_ok,
                   power_ok=power_ok, algebra_ok=algebra_ok, hard_pass=hard_pass, refute=refute),
        mustfail=dict(shuf_rel_sym_vs_mean=round(shuf_rel, 5) if shuf_rel == shuf_rel else None,
                      arb_rel_sym_vs_mean=round(arb_rel, 5) if arb_rel == arb_rel else None,
                      oracle_mae=round(orc_mae, 8)),
        per_seed_regime={reg: [dict(strata=per[reg][i]["strata"], leak_ok=per[reg][i]["leak_ok"],
                                    n_seen=per[reg][i]["n_seen"], n_novel=per[reg][i]["n_novel"])
                               for i in range(len(seeds))] for reg in REGIMES},
    )
    base["elapsed_s"] = round(time.perf_counter() - t0, 2)
    return base


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (real bind path + REAL parser on synthetic per-circle rows + planted controls + arms-differ + determinism)
# ===========================================================================

def self_test():
    ok_all = True
    details = {}

    # (1) REAL substrate bind (complex64 FHRR = elementwise multiply): bind of FPE phasors reads out (i+j) mod m.
    g = np.random.default_rng(31)
    m = g.integers(1, 9, size=64).astype(np.float64)
    jj = np.arange(9, dtype=np.float64)[:, None]
    Yc = torch.from_numpy(np.exp(1j * (2.0 * np.pi / 9.0) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Yc[torch.tensor([1, 2])], Yc[torch.tensor([2, 3])])
    homo_pred = torch.argmax((bound @ Yc.conj().T.contiguous()).real, 1).tolist()
    homo_ok = homo_pred == [3 % 9, 5 % 9]
    details["fhrr_bind_homomorphism_ok"] = homo_ok

    # (2) elementwise product (LEARN_SYM composition) == real part of hd_bind on aligned complex phasors.
    va = torch.tensor([[2.0, -1.0, 0.5, 3.0]]); vb = torch.tensor([[-1.0, 2.0, 4.0, -0.5]])
    prod_is_bind = bool(torch.allclose(va * vb, hd_bind(va.to(torch.complex64), vb.to(torch.complex64)).real, atol=1e-5))
    details["hadamard_equals_complex_bind_real"] = prod_is_bind

    # (3) REAL PARSER on synthetic per-circle rows (exercises detect_structure + parse_circles PATH-A code path).
    synth_header = ["Compound1", "Compound2", "Transformation1", "Transformation2", "Nonadditivity"]
    kind, colmap = detect_structure(synth_header)
    tok_map = {}
    synth_rows = [{"Compound1": "a", "Compound2": "b", "Transformation1": "R%d" % (i % 5),
                   "Transformation2": "R%d" % ((i * 3 + 1) % 5), "Nonadditivity": "%.3f" % (0.4 * ((i % 7) - 3))}
                  for i in range(50)]
    trip = parse_circles(synth_rows, colmap, "assayS", tok_map) if kind == "per_circle" else []
    parser_ok = bool(kind == "per_circle" and len(trip) == 50 and len(tok_map) == 5)
    details["parser_kind"] = kind; details["parser_n_trip"] = len(trip); details["parser_n_tok"] = len(tok_map)
    details["parser_ok"] = parser_ok
    # per-compound header must route to PATH B
    pc_kind, _ = detect_structure(["ID", "SMILES", "VALUE", "nOccurence", "Nonadd_pC"])
    percompound_routes_B = (pc_kind == "per_compound")
    details["percompound_routes_B"] = percompound_routes_B

    # (4) POSITIVE control: planted symmetric-interaction arena -> SYM beats STRONG additive (discriminator FIRES at scale).
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    details.update(dict(pos_rel=round(pos_rel, 4), pos_sym_mae=round(pos_sym, 4), pos_sadd_mae=round(pos_sadd, 4)))
    # (5) NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (gate not saturation-vacuous).
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    details.update(dict(neg_rel=round(neg_rel, 4), neg_sym_mae=round(neg_sym, 4), neg_sadd_mae=round(neg_sadd, 4)))

    # (6) MUST-FAIL: SHUFFLE on interaction arena -> SYM must NOT beat MEAN predictor.
    Xi, yi = _plant_reg(600, 7, "interaction")
    rsh = [score(Xi, yi, SHUFFLE, sd, 8) for sd in (7, 13, 17)]
    shuf_rel = float(np.mean([_rel(r["strata"]["all"]["full"][MEAN], r["strata"]["all"]["full"][SYM]) for r in rsh]))
    details["shuffle_rel_sym_vs_mean"] = round(shuf_rel, 4)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF) + ORACLE ceiling + determinism on the planted interaction arena.
    scr = score(Xi, yi, CLEAN, 7, 8)
    digs = scr["sigs"]
    arms_differ = (len(set(digs.values())) >= len(digs) - 1)  # tolerate ADD_RIDGE/ADD_LSTSQ coinciding on simple data
    orc_mae = float(np.mean([score(Xi, yi, CLEAN, sd, 8)["strata"]["all"]["full"][ORC] for sd in (7, 13)]))
    d1 = score(Xi, yi, CLEAN, 5, 8)["sigs"][SYM]; d2 = score(Xi, yi, CLEAN, 5, 8)["sigs"][SYM]
    determinism_ok = (d1 == d2)
    details.update(dict(arms_sig_count=len(set(digs.values())), oracle_mae=round(orc_mae, 8),
                        arms_differ=arms_differ, determinism_ok=determinism_ok))

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hadamard_equals_complex_bind": prod_is_bind,
        "real_parser_reconstructs_circles": parser_ok,
        "percompound_routes_to_escalate": percompound_routes_B,
        "pos_ctrl_SYM_beats_strong_additive": (pos_rel == pos_rel and pos_rel >= POS_CTRL_REL),
        "neg_ctrl_SYM_not_beating_additive": (neg_rel == neg_rel and neg_rel <= NEG_CTRL_REL),
        "shuffle_mustfail_fires": (shuf_rel <= MUSTFAIL_REL_TOL),
        "oracle_ceiling": (orc_mae <= 1e-6),
        "arms_differ": arms_differ,
        "determinism_ok": determinism_ok,
    }
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
        m = run_measurement(SEEDS_SMOKE, run_mode="smoke")
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    m = run_measurement(SEEDS_FULL, run_mode="full")
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
