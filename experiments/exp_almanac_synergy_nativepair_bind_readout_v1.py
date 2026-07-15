"""ALMANAC_SYNERGY_NATIVEPAIR_BIND_READOUT (v1): NATIVE-PAIR real-data linchpin + conjunction MODULE #2 (also the module-#1
fallback if the Kramer per-compound cell escalates for lack of R1,R2 cycle structure). Ingest the NCI-ALMANAC drug-combination
screen (Holbeck et al. 2017, Cancer Research PMC5499996; REAL, publicly-MEASURED Bliss-excess synergy) and test whether the
substrate's LEARNED SYMMETRIC BIND (shared per-token code + ELEMENTWISE-PRODUCT composition = swap-symmetric) READS OUT the
genuinely-non-additive 2-way interaction -- the measured drug-pair ComboScore -- on NOVEL held-out drug-pairs, BEATING a
capacity-matched STRONG categorical additive (per-drug main effects) by a pre-registered relative-MAE margin, SPECIFICALLY on
the high-|ComboScore| (genuine-interaction) subset. Glass-box CPU, NO LLM at readout. All compute REMOTE (the cell downloads
the ZIP at runtime; remote --self-test with planted arenas is the network-independent gate).

WHY NATIVE-PAIR is cleaner than Kramer: Kramer per-compound CSVs (ID,SMILES,VALUE,nOccurence,Nonadd_pC) lack the R1,R2 cycle
structure -- reconstructing constituents needs RDKit + MMP fragmentation. NCI-ALMANAC has the constituent-pair structure
DIRECTLY: drug1 x drug2 + a MEASURED per-pair synergy (ComboScore = modified Bliss-independence excess-over-additivity,
shipped as a column). The bind reads code(drugA) (x) code(drugB) -> measured ComboScore natively; NO fragmentation.

WHY (inlined; no re-hunt): two prior LLM-GENERATED conjunction pockets (chem mixing-hazard, epistasis-severity) came back
ADDITIVE-CAPTURABLE vs a strong additive -- the narration smuggled in structure a strong additive already captured. Genuine
non-additivity must be INGESTED where it is EMPIRICALLY MEASURED. ComboScore is a measured Bliss-excess per drug pair,
computed by the original experimentalists from real NCI-60 growth-inhibition assays -- no narration step. Drug synergy is
intrinsically a 2-way interaction (excess over what the two single-agent effects predict additively), so the target IS a
measured pairwise nonadditivity term.

THE MECHANISM x DATA question: LEARN_SYM (shared per-token code + PRODUCT) reads a SYMMETRIC 2-way interaction and GENERALIZES
to NOVEL drug-pairs because a shared code + bilinear readout extrapolates where a lookup cannot; a per-drug main-effects
ADDITIVE (each drug's average synergy-proneness) provably loses any irreducible pairwise synergy term. Load-bearing claim: on
the high-|ComboScore| (genuine synergy/antagonism) subset of NOVEL drug-pairs, LEARN_SYM beats a capacity-matched STRONG
additive by >=30% relative MAE AND the advantage is MATERIALLY LARGER on the high subset than on the low (reads chemistry,
not noise).

DATA-STRUCTURE-ADAPTIVE (do NOT force a broken encoding): the ALMANAC ZIP is downloaded + column-probed at runtime.
  PATH A (ALMANAC combo structure present -> NSC1,NSC2,SCORE columns): entity=(drug1,drug2) unordered NSC-pair, target =
    the per-pair mean ComboScore (aggregated over cell lines to collapse the 3rd axis to one measured scalar per native
    pair); run the full SYM-vs-STRONG-additive transfer proof.
  PATH B (structure absent / columns not found): emit ESCALATE_ALMANAC_NO_NATIVEPAIR_STRUCTURE with a crisp diagnostic
    (header, row counts) + hand off the Costanzo yeast SGA (epsilon) fallback. HONEST verdict about ingestability, NOT a
    mechanism refute.

ARMS (regression, MAE lower=better): LEARN_SYM (shared code + PRODUCT = substrate symmetric bind; WINNER hypothesis) ;
  LEARN_ADD (shared code + SUM; matched-capacity LEARNED additive) ; ADD_RIDGE (closed-form ridge on per-token COUNT design;
  STRONG closed-form categorical additive) ; ADD_LSTSQ (closed-form lstsq; additive) ; LEARN_ROLE (role-keyed product;
  ALGEBRA contrast -- must NOT beat SYM on a symmetric target) ; MEAN (predict train-mean = regression frequency floor) ;
  MEMORIZE (per-token-pair mean; rote, collapses to MEAN on NOVEL) ; ORACLE (true; MAE~0).
  strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel(s,sub) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.
STRATA: seen / novel drug-pair (entity-level split). SUBSET (magnitude-defined, PRE-REGISTERED, scale-free): hi = |ComboScore
  - median| > HI_Z * robust_sigma (genuine interaction) / lo = otherwise (near-additive control). robust_sigma = 1.4826*MAD.
REGIMES: CLEAN(real) ; ARBITRARY (random target per unique drug-pair; must-fail on NOVEL) ; SHUFFLE (target permutation;
  must-fail on ALL). FIXED GATE positive control = planted symmetric-interaction arena (SYM beats strong-additive by its own
  bar); negative control = planted ADDITIVE arena (SYM must NOT beat additive -> proves the gate is NOT saturation-vacuous).

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_almanac_synergy_nativepair_bind_readout.md):
  HARD_PASS_TRANSFER (native-pair real-data linchpin): novel_hi rel_MAE >= 0.30 AND (novel_hi rel - novel_lo rel) >= 0.15
    AND positive-control passes (planted-interaction rel>=0.30) AND negative-control ok (planted-additive rel<=0.10)
    AND must-fails fire (SHUFFLE all rel_sym_vs_mean<=0.08, ARBITRARY novel rel_sym_vs_mean<=0.08) AND oracle MAE~0
    AND leak_ok AND enough high-interaction signal (>=15% of pairs clear the robust-sigma floor) AND novel_hi >=4 mean rows.
  HARD_FAIL_INSUFFICIENT_SIGNAL: <15% of pairs clear the floor -> ESCALATE to Costanzo/ChEMBL-bulk (domain NOT closed).
  REFUTE_NO_TRANSFER: novel_hi rel_MAE <= 0.05 (collapses to noise; real measured synergy ALSO additive-capturable = a deep
    foundation finding) with valid must-fails+oracle+controls.
  MIDDLE_BAND: partial / low-power novel_hi / advantage not materially larger on hi than lo.

Compute architecture: (b) sequential-CPU with justification -- arena is O(1e3) native drug-pairs x a handful of tiny (<=Nx32)
  Adam fits (ms each) + numpy solves; total compute wall < 3min over 8 seeds; GPU yields no speedup on sub-ms matmuls;
  dominant cost is the single ALMANAC ZIP HTTP download + streaming parse of the combo CSV (cached after first run). torch
  thread-capped (HDI_TORCH_THREADS default 2). Storage: no_storage / no_composition (single-hop readout). Determinism: FIXED
  int seeds + stable sorted-unique token ids; NO hash(), NO list(set()) (PROT-023). ASCII-only; no bare except; except
  SystemExit before except Exception; atomic tmp+os.replace. Default invocation (no flag) = FULL run to completion.
  progress_logging: ACQUIRE + streaming-parse row counter (every 1M rows) + per-seed done lines, all flush=True (§17,
  timeout_s>=1800).
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; float-hash arms-differ on planted arena).
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: regression MAE floor is data-noise-defined (assay/replicate noise in ComboScore); no closed-form CRLB for the
#     bilinear-readout arm; the robust-sigma hi subset + rel-MAE-reduction gate substitute for a capacity-feasibility cap.
# - baseline_in_band: STRONG additive MAE is measured (not saturated); positive/negative planted controls bound the gate.
# - discriminator survives scale: self-test fires SYM>>additive on planted-interaction SEEN at plant scale (n=600).
# - HARD_PASS strictly above floor: rel>=0.30 AND hi-minus-lo>=0.15 (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive only; MEAN/MEMO/ORACLE/ROLE are contrast arms.
# - cardinality_ok: n_seeds x n_regimes fixed; verdict counts per_seed_regime lengths.
# - per-unit failure-class instrumentation: acquire/parse failures -> explicit ACQUIRE_FAILED / ESCALATE verdicts.
# - calibration_check: adaptive_with_discriminator_gate (HI_Z*robust_sigma magnitude split is data-scale-invariant; the
#     hi-minus-lo>=0.15 gate is the discriminator-still-fires verification; frac_hi>=0.15 is the insufficient-signal gate).
# - all numbers in comments tagged CITED@ (scout drill) / THEORETICAL@ / to-be-MEASURED@ (real-data pending remote run).
# - real_code_path: self-test parses SYNTHETIC ALMANAC rows through the REAL parser + runs planted arenas through the REAL
#     score()/arm code; hd_bind exercised on complex64 phasors.
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
import zipfile
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

ANCHOR_NAME = "almanac_synergy_nativepair_bind_readout_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CACHE_DIR = os.path.join(_REPO, "data", "foundation_clusters", "nci_almanac_combo")

# ---- data source (Holbeck et al. 2017, NCI-ALMANAC; PMC5499996) ----
# CITED@ notes/drill_real_nonadditive_experimental_datasets_for_conjunction_modules_2026-07-15.md (direct bulk ZIP,
# verified reachable, unauthenticated; ComboScore = modified Bliss-independence excess-over-additivity shipped in-file).
ALMANAC_ZIP_URL = ("https://discover.nci.nih.gov/cellminer/download/processeddataset/"
                   "DTP_NCI60_ALMANAC_COMBO_SCORE.zip")
ALMANAC_ZIP_NAME = "DTP_NCI60_ALMANAC_COMBO_SCORE.zip"
COMBOSCORE_DEF = ("ComboScore = modified Bliss-independence excess-over-additivity synergy score per drug pair per cell "
                  "line (NCI-ALMANAC; Holbeck et al. 2017 Cancer Research 77(13):3564). Positive=synergy, negative=antagonism.")

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
HI_Z = 1.0                   # hi = |ComboScore - median| > HI_Z * robust_sigma (robust_sigma = 1.4826*MAD): genuine 2-way
MIN_HI_FRAC = 0.15           # >=15% of pairs must clear the robust-sigma floor else HARD_FAIL_INSUFFICIENT -> escalate
HP_REL_HI = 0.30             # novel_hi rel_MAE reduction (SYM vs strong additive) >= 0.30
HP_HI_MINUS_LO = 0.15        # advantage materially larger on hi than lo: rel_hi - rel_lo >= 0.15
REFUTE_REL = 0.05            # novel_hi rel_MAE <= 0.05 => collapses to noise => REFUTE
MUSTFAIL_REL_TOL = 0.08      # SHUFFLE(all)+ARBITRARY(novel) rel_sym_vs_mean ceiling
MIN_NOVEL_HI_N = 4.0         # mean novel-hi query rows for adequate power
POS_CTRL_REL = 0.30          # planted-interaction SEEN rel_MAE (positive control must clear its own bar)
NEG_CTRL_REL = 0.10          # planted-additive SEEN rel_MAE ceiling (gate not saturation-vacuous)
MIN_PAIRS = 200              # PATH-A requires >= this many unique native drug-pairs; else escalate

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

def _download_one(url, dest, timeout=300, retries=2):
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
            time.sleep(2.0 * (attempt + 1))
    return 0, last


def acquire():
    """Download-if-absent the NCI-ALMANAC combo-score ZIP -> CACHE_DIR. Returns (zip_path or None, provenance)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    dest = os.path.join(CACHE_DIR, ALMANAC_ZIP_NAME)
    err = None
    nbytes = 0
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        nbytes = os.path.getsize(dest)
        _log("ACQUIRE cache-hit %s (%d bytes)" % (ALMANAC_ZIP_NAME, nbytes))
    else:
        nbytes, err = _download_one(ALMANAC_ZIP_URL, dest)
        if err is None and nbytes > 1024:
            _log("ACQUIRE downloaded %s (%d bytes)" % (ALMANAC_ZIP_NAME, nbytes))
        else:
            _log("ACQUIRE FAILED %s : %s" % (ALMANAC_ZIP_NAME, err or ("too_small:%d" % nbytes)))
    prov = dict(dataset="NCI_ALMANAC_combo_score", pmc="PMC5499996",
                paper="Holbeck et al. 2017, Cancer Research 77(13):3564", url=ALMANAC_ZIP_URL,
                retrieval_ts=datetime.now(timezone.utc).isoformat(), interaction_definition=COMBOSCORE_DEF,
                zip_bytes=int(nbytes), acquire_error=err,
                source_note="verified-reachable unauthenticated NCI DTP CellMiner processed-dataset ZIP")
    try:
        with open(os.path.join(CACHE_DIR, "provenance.json"), "w", encoding="utf-8") as f:
            json.dump(prov, f, indent=2)
    except OSError:
        pass
    if err is None and nbytes > 1024 and os.path.exists(dest):
        return dest, prov
    return None, prov


# ===========================================================================
# PARSE + STRUCTURE DETECTION (native drug-pair ALMANAC combo CSV inside the ZIP)
# ===========================================================================

_NSC1_COLS = ["nsc1", "nsc_1", "nsc1id", "nsc_1_id"]
_NSC2_COLS = ["nsc2", "nsc_2", "nsc2id", "nsc_2_id"]
_SCORE_COLS = ["score", "comboscore", "combo_score", "scorecombo"]
_CELL_COLS = ["cellname", "cell", "cellline", "cell_line", "cell_name"]


def _norm(s):
    return str(s).strip().lower().replace(" ", "_")


def detect_almanac_columns(header):
    """Return ('almanac', {'nsc1','nsc2','score','cell'?}) | ('unknown', {})."""
    cols = {_norm(h): h for h in header}

    def _first(cands):
        for c in cands:
            if c in cols:
                return cols[c]
        return None

    nsc1 = _first(_NSC1_COLS); nsc2 = _first(_NSC2_COLS)
    score = _first(_SCORE_COLS); cell = _first(_CELL_COLS)
    if nsc1 is not None and nsc2 is not None and score is not None:
        return "almanac", {"nsc1": nsc1, "nsc2": nsc2, "score": score, "cell": cell}
    return "unknown", {}


def _finite_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _open_combo_csv(zip_path):
    """Return (member_name, DictReader-header, row-iterator) for the largest .csv inside the ALMANAC ZIP.
    Streams the member (does not extract to disk)."""
    zf = zipfile.ZipFile(zip_path, "r")
    csv_members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    if not csv_members:
        # some releases ship a .txt / no-extension delimited member; take the largest member
        members = [(zf.getinfo(n).file_size, n) for n in zf.namelist() if not n.endswith("/")]
        if not members:
            zf.close()
            return None, None, None, None
        members.sort(reverse=True)
        member = members[0][1]
    else:
        csv_members.sort(key=lambda n: zf.getinfo(n).file_size, reverse=True)
        member = csv_members[0]
    fh = zf.open(member, "r")
    text = io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline="")
    rdr = csv.DictReader(text)
    return zf, member, rdr.fieldnames or [], rdr


def parse_almanac(zip_path):
    """Stream the ALMANAC combo CSV; aggregate ComboScore to one measured scalar per native (drug1,drug2) pair.
    Two-level aggregation: per (canonical-pair, cell-line) mean, then per canonical-pair mean over its cell lines (each
    cell line weighted equally). Returns dict with PATH 'A' (X,y,n_tok,...) or PATH 'B' (escalate diagnostics)."""
    zf, member, header, rdr = _open_combo_csv(zip_path)
    if rdr is None:
        return {"path": "B", "reason": "no_csv_member_in_zip", "header": [], "n_rows": 0}
    kind, colmap = detect_almanac_columns(header)
    if kind != "almanac":
        try:
            zf.close()
        except Exception:  # noqa: BLE001 (best-effort close; not control flow)
            pass
        return {"path": "B", "reason": "columns_not_found", "header": header[:30], "n_rows": 0,
                "member": member}

    tok_map = {}
    # (canonical-pair-token-tuple, cell) -> [sum, count]
    cellagg = defaultdict(lambda: [0.0, 0])
    n_rows = 0
    n_scored = 0
    c_nsc1, c_nsc2, c_score, c_cell = colmap["nsc1"], colmap["nsc2"], colmap["score"], colmap.get("cell")
    for r in rdr:
        n_rows += 1
        if (n_rows % 1000000) == 0:
            _log("PARSE streaming... %d rows scanned, %d scored, %d pair-cell cells so far"
                 % (n_rows, n_scored, len(cellagg)))
        s = _finite_float(r.get(c_score))
        if s is None:
            continue
        a_raw = str(r.get(c_nsc1, "")).strip()
        b_raw = str(r.get(c_nsc2, "")).strip()
        if not a_raw or not b_raw or a_raw in ("0", "0.0") or b_raw in ("0", "0.0") or a_raw == b_raw:
            continue
        ta = "NSC::" + a_raw
        tb = "NSC::" + b_raw
        for t in (ta, tb):
            if t not in tok_map:
                tok_map[t] = len(tok_map)
        ia, ib = tok_map[ta], tok_map[tb]
        pairkey = (min(ia, ib), max(ia, ib))
        cell = str(r.get(c_cell, "ALL")).strip() if c_cell else "ALL"
        acc = cellagg[(pairkey, cell)]
        acc[0] += s
        acc[1] += 1
        n_scored += 1
    try:
        zf.close()
    except Exception:  # noqa: BLE001
        pass

    # per-pair mean over its cell-line means
    pair_scores = defaultdict(list)
    for (pairkey, _cell), (ssum, scnt) in cellagg.items():
        if scnt > 0:
            pair_scores[pairkey].append(ssum / scnt)
    pairs = sorted(pair_scores.keys())  # stable ordering (no list(set))
    if len(pairs) < MIN_PAIRS:
        return {"path": "B", "reason": "insufficient_native_pairs", "n_pairs": len(pairs), "n_rows": n_rows,
                "n_scored": n_scored, "header": header[:30], "member": member}
    X = np.array([[pk[0], pk[1]] for pk in pairs], dtype=np.int64)
    y = np.array([float(np.mean(pair_scores[pk])) for pk in pairs], dtype=np.float64)
    return {"path": "A", "X": X, "y": y, "n_tok": len(tok_map), "n_pairs": len(pairs), "n_rows": n_rows,
            "n_scored": n_scored, "member": member,
            "cells_per_pair_mean": float(np.mean([len(pair_scores[pk]) for pk in pairs])),
            "header": header[:30]}


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


def score(X, y_real, regime, seed, n_tok, hi_center=0.0, hi_scale=1.0, hi_z=HI_Z):
    q, tr, seen, train_pairs = split_query(X, seed)
    y_used, y_oracle = make_regime_target(X, y_real, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    gmean = float(np.mean(ytr))
    mag = np.abs(y_real[q] - hi_center)  # subset membership defined on the REAL ComboScore magnitude (robust-centered)

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

    hi = mag > (hi_z * hi_scale)
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
    rs = [score(X, y, CLEAN, sd, n_tok) for sd in seeds]  # controls use 'full'; hi/lo irrelevant (defaults ok)
    sym = float(np.mean([r["strata"]["seen"]["full"][SYM] for r in rs]))
    sadd = float(np.mean([r["strata"]["seen"]["full"]["STRONG_ADD"] for r in rs]))
    return _rel(sadd, sym), sym, sadd


# ===========================================================================
# full measurement
# ===========================================================================

def _robust_center_scale(y):
    med = float(np.median(y))
    mad = float(np.median(np.abs(y - med)))
    scale = 1.4826 * mad
    if not math.isfinite(scale) or scale < 1e-9:
        scale = float(np.std(y)) + 1e-9
    return med, scale


def run_measurement(seeds, run_mode):
    _write_start_marker(expected_n_units=len(seeds) * len(REGIMES), run_mode=run_mode)
    t0 = time.perf_counter()
    zip_path, prov = acquire()
    base = dict(run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
                elapsed_s=round(time.perf_counter() - t0, 2), provenance=prov, seeds=list(seeds),
                bands=dict(HI_Z=HI_Z, MIN_HI_FRAC=MIN_HI_FRAC, HP_REL_HI=HP_REL_HI, HP_HI_MINUS_LO=HP_HI_MINUS_LO,
                           REFUTE_REL=REFUTE_REL, MUSTFAIL_REL_TOL=MUSTFAIL_REL_TOL, MIN_NOVEL_HI_N=MIN_NOVEL_HI_N,
                           POS_CTRL_REL=POS_CTRL_REL, NEG_CTRL_REL=NEG_CTRL_REL, MIN_PAIRS=MIN_PAIRS))

    # positive/negative controls (planted; the FIXED gate carries a genuine non-additive positive control)
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    pos_ok = bool(pos_rel == pos_rel and pos_rel >= POS_CTRL_REL)
    neg_ok = bool(neg_rel == neg_rel and neg_rel <= NEG_CTRL_REL)
    base["controls"] = dict(pos_rel=round(pos_rel, 5), pos_sym_mae=round(pos_sym, 5), pos_sadd_mae=round(pos_sadd, 5),
                            neg_rel=round(neg_rel, 5), neg_sym_mae=round(neg_sym, 5), neg_sadd_mae=round(neg_sadd, 5),
                            pos_ok=pos_ok, neg_ok=neg_ok)

    if zip_path is None:
        msg = ("ACQUIRE_FAILED || could not download the NCI-ALMANAC combo-score ZIP (see provenance.acquire_error). "
               "pos_ctrl_rel=%s neg_ctrl_rel=%s (machinery %s)." %
               (_fmt(pos_rel), _fmt(neg_rel), "VALID" if (pos_ok and neg_ok) else "CHECK"))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200])
        return base

    try:
        data = parse_almanac(zip_path)
    except (zipfile.BadZipFile, OSError, csv.Error, UnicodeDecodeError) as e:
        msg = ("ACQUIRE_FAILED || ALMANAC ZIP present but unreadable: %s: %s. pos_ctrl_rel=%s neg_ctrl_rel=%s."
               % (type(e).__name__, str(e)[:160], _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200], parse_error=str(e)[:300])
        return base

    if data["path"] == "B":
        rec = ("Costanzo yeast SGA (epsilon score; gene1 x gene2 measured epistasis; thecellmap.org/yeast/costanzo2016) "
               "OR DrugComb (Bliss/Loewe/ZIP synergy) as the native-pair fallback")
        msg = ("ESCALATE_ALMANAC_NO_NATIVEPAIR_STRUCTURE || could not build a native drug-pair slice from the ALMANAC ZIP "
               "(reason=%s n_pairs=%s n_rows=%s member=%s). HAND-OFF: %s. pos_ctrl_rel=%s neg_ctrl_rel=%s"
               % (data.get("reason"), data.get("n_pairs"), data.get("n_rows"), data.get("member"),
                  rec, _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ESCALATE_ALMANAC_NO_NATIVEPAIR_STRUCTURE", verdict_msg=msg, summary=msg[:200],
                    escalate=True, path="B", parse_diag={k: v for k, v in data.items() if k != "path"})
        return base

    # ---------- PATH A: real native-pair transfer proof ----------
    X, y, n_tok = data["X"], data["y"], data["n_tok"]
    hi_center, hi_scale = _robust_center_scale(y)
    frac_hi = float((np.abs(y - hi_center) > (HI_Z * hi_scale)).mean())
    _log("PATH A: n_pairs=%d n_tok=%d n_rows_scanned=%d n_scored=%d cells/pair=%.1f | median=%.3f robust_sigma=%.3f "
         "frac_hi(|z|>%.1f)=%.3f seeds=%d"
         % (X.shape[0], n_tok, data.get("n_rows", 0), data.get("n_scored", 0), data.get("cells_per_pair_mean", 0.0),
            hi_center, hi_scale, HI_Z, frac_hi, len(seeds)))

    per = {reg: [] for reg in REGIMES}
    for si, sd in enumerate(seeds):
        for reg in REGIMES:
            per[reg].append(score(X, y, reg, sd, n_tok, hi_center=hi_center, hi_scale=hi_scale, hi_z=HI_Z))
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
        verdict = "HARD_FAIL_INSUFFICIENT_SIGNAL_ESCALATE_TO_COSTANZO_OR_DRUGCOMB"
    elif not power_ok:
        verdict = "MIDDLE_BAND_LOW_POWER_NOVEL_HI"
    elif hard_pass:
        verdict = "HARD_PASS_TRANSFER_SYMMETRIC_BIND_READS_REAL_ALMANAC_SYNERGY"
    elif refute:
        verdict = "REFUTE_NO_TRANSFER_SYM_DOES_NOT_READ_ALMANAC_SYNERGY"
    else:
        verdict = "MIDDLE_BAND"
        if rel_hi_pass and not hi_gt_lo:
            verdict += "_ADVANTAGE_NOT_HI_SPECIFIC"

    msg = ("%s || PATH_A n_pairs=%d n_tok=%d frac_hi=%.3f | NOVEL_HI rel_MAE=%s(>=%.2f) NOVEL_LO rel=%s "
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
        n_pairs=int(X.shape[0]), n_tok=int(n_tok), frac_hi=round(frac_hi, 5),
        hi_center=round(hi_center, 5), hi_scale=round(hi_scale, 5),
        n_rows_scanned=int(data.get("n_rows", 0)), n_scored=int(data.get("n_scored", 0)),
        cells_per_pair_mean=round(float(data.get("cells_per_pair_mean", 0.0)), 3), member=data.get("member"),
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
# SELF-TEST (real bind path + REAL parser on synthetic ALMANAC rows + planted controls + arms-differ + determinism)
# ===========================================================================

def _make_synth_almanac_zip(path, n_pairs=60, n_cells=3, n_drugs=12):
    """Write a tiny synthetic ALMANAC-shaped combo CSV inside a ZIP -> exercises the REAL parser/detector PATH-A code."""
    rng = np.random.default_rng(101)
    header = ["COMBODRUGSEQ", "NSC1", "CONC1", "NSC2", "CONC2", "PERCENTGROWTH", "SCORE", "CELLNAME"]
    rows = [",".join(header)]
    drugs = [1000 + d for d in range(n_drugs)]
    tab = rng.normal(0, 1, size=(n_drugs, n_drugs)); tab = 0.5 * (tab + tab.T)
    seq = 0
    made = set()
    while len(made) < n_pairs:
        i, j = int(rng.integers(0, n_drugs)), int(rng.integers(0, n_drugs))
        if i == j:
            continue
        made.add((min(i, j), max(i, j)))
    for (i, j) in sorted(made):
        for c in range(n_cells):
            seq += 1
            sc = tab[i, j] * 20.0 + rng.normal(0, 1)  # ComboScore-scale
            rows.append("%d,%d,1e-5,%d,1e-5,50.0,%.4f,CELL_%d" % (seq, drugs[i], drugs[j], sc, c))
    csv_text = "\n".join(rows) + "\n"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ComboDrugGrowth_synth.csv", csv_text)


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

    # (3) REAL PARSER on a synthetic ALMANAC ZIP (exercises detect_almanac_columns + parse_almanac PATH-A code path).
    tmp_zip = os.path.join(CACHE_DIR, "_selftest_synth_almanac.zip")
    os.makedirs(CACHE_DIR, exist_ok=True)
    _make_synth_almanac_zip(tmp_zip, n_pairs=60, n_cells=3, n_drugs=12)
    saved_min = MIN_PAIRS
    try:
        globals()["MIN_PAIRS"] = 40  # synthetic slice is tiny; relax the PATH-A floor for the self-test only
        sd = parse_almanac(tmp_zip)
    finally:
        globals()["MIN_PAIRS"] = saved_min
        try:
            os.remove(tmp_zip)
        except OSError:
            pass
    parser_ok = bool(sd.get("path") == "A" and sd.get("n_pairs", 0) == 60 and sd.get("n_tok", 0) == 12
                     and sd["X"].shape == (60, 2) and sd["y"].shape == (60,))
    details["parser_path"] = sd.get("path"); details["parser_n_pairs"] = sd.get("n_pairs")
    details["parser_n_tok"] = sd.get("n_tok"); details["parser_ok"] = parser_ok
    # a header with no NSC pair columns must route to PATH B
    unk_kind, _ = detect_almanac_columns(["ID", "SMILES", "VALUE", "Nonadd_pC"])
    percompound_routes_B = (unk_kind == "unknown")
    details["nonpair_header_routes_B"] = percompound_routes_B

    # (4) POSITIVE control: planted symmetric-interaction arena -> SYM beats STRONG additive (discriminator FIRES at scale).
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    details.update(dict(pos_rel=round(pos_rel, 4), pos_sym_mae=round(pos_sym, 4), pos_sadd_mae=round(pos_sadd, 4)))
    # (5) NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (gate not saturation-vacuous).
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    details.update(dict(neg_rel=round(neg_rel, 4), neg_sym_mae=round(neg_sym, 4), neg_sadd_mae=round(neg_sadd, 4)))

    # (6) MUST-FAIL: SHUFFLE on interaction arena -> SYM must NOT beat MEAN predictor.
    Xi, yi = _plant_reg(600, 7, "interaction")
    rsh = [score(Xi, yi, SHUFFLE, sd_, 8) for sd_ in (7, 13, 17)]
    shuf_rel = float(np.mean([_rel(r["strata"]["all"]["full"][MEAN], r["strata"]["all"]["full"][SYM]) for r in rsh]))
    details["shuffle_rel_sym_vs_mean"] = round(shuf_rel, 4)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF) + ORACLE ceiling + determinism on the planted interaction arena.
    scr = score(Xi, yi, CLEAN, 7, 8)
    digs = scr["sigs"]
    arms_differ = (len(set(digs.values())) >= len(digs) - 1)  # tolerate ADD_RIDGE/ADD_LSTSQ coinciding on simple data
    orc_mae = float(np.mean([score(Xi, yi, CLEAN, sd_, 8)["strata"]["all"]["full"][ORC] for sd_ in (7, 13)]))
    d1 = score(Xi, yi, CLEAN, 5, 8)["sigs"][SYM]; d2 = score(Xi, yi, CLEAN, 5, 8)["sigs"][SYM]
    determinism_ok = (d1 == d2)
    details.update(dict(arms_sig_count=len(set(digs.values())), oracle_mae=round(orc_mae, 8),
                        arms_differ=arms_differ, determinism_ok=determinism_ok))

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hadamard_equals_complex_bind": prod_is_bind,
        "real_parser_reconstructs_pairs": parser_ok,
        "nonpair_header_routes_to_escalate": percompound_routes_B,
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
