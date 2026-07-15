"""COSTANZO_EPISTASIS_NATIVEPAIR_BIND_READOUT (v1): NATIVE-PAIR real-data linchpin (conjunction MODULE, Costanzo yeast SGA).
Switched from NCI-ALMANAC (whose CellMiner xlsx is a human-formatted presentation spreadsheet: nested xlsx + banner preamble
+ footnote-suffixed WIDE per-cell-line columns -- a poor ingest target, 3 format quirks) to the Costanzo et al. 2016 global
yeast genetic-interaction network (thecellmap.org/yeast/costanzo2016), a CLEAN machine-readable research TSV. Test whether the
substrate's LEARNED SYMMETRIC BIND (shared per-token code + ELEMENTWISE-PRODUCT composition = swap-symmetric) READS OUT the
genuinely-non-additive 2-way interaction -- the MEASURED genetic-interaction score epsilon of a gene PAIR (deviation from the
multiplicative single-mutant-fitness expectation) -- on NOVEL held-out gene-pairs, BEATING a capacity-matched STRONG
categorical additive (per-gene main effects) by a pre-registered relative-MAE margin, SPECIFICALLY on the high-|epsilon|
(genuine-interaction) subset. Glass-box CPU, NO LLM at readout. All compute REMOTE (the cell downloads the pairwise dataset at
runtime; remote --self-test with planted arenas is the network-independent gate).

WHY NATIVE-PAIR / why Costanzo is clean: the pairwise file is long-format by construction -- one row per (query gene, array
gene) with the measured epsilon + p-value + single-mutant fitnesses. entity = (query_gene, array_gene); constituents = the two
genes (systematic ORF ids as canonical tokens); target = measured epsilon. No fragmentation, no xlsx, no wide-format, no
narration -- epsilon is computed by the original experimentalists from real double-/single-mutant colony fitnesses.

WHY (inlined; no re-hunt): two prior LLM-GENERATED conjunction pockets (chem mixing-hazard, epistasis-severity) came back
ADDITIVE-CAPTURABLE vs a strong additive -- the narration smuggled in structure a strong additive already captured. Genuine
non-additivity must be INGESTED where it is EMPIRICALLY MEASURED. epsilon IS the measured pairwise nonadditivity (double-mutant
fitness minus the expected product of single-mutant fitnesses); genetic interaction is intrinsically a 2-way term.

THE MECHANISM x DATA question: LEARN_SYM (shared per-token code + PRODUCT) reads a SYMMETRIC 2-way interaction and GENERALIZES
to NOVEL gene-pairs because a shared code + bilinear readout extrapolates where a lookup cannot; a per-gene main-effects
ADDITIVE (each gene's average interaction-proneness) provably loses any irreducible pairwise epsilon term. Load-bearing claim:
on the high-|epsilon| (genuine interaction) subset of NOVEL gene-pairs, LEARN_SYM beats a capacity-matched STRONG additive by
>=30% relative MAE AND the advantage is MATERIALLY LARGER on the high subset than on the low (reads biology, not noise).

DATA / TRACTABILITY: the raw pairwise dataset is downloaded (urllib) + streaming-parsed (stdlib csv, tab-delimited; zip of
.txt members handled). To avoid the 521MB dense bulk we FILTER to significant measured interactions (|epsilon| > 0.08 AND
p < 0.05, the standard Costanzo threshold), aggregate multi-strain rows to one measured scalar per ORF-pair (mean epsilon),
then restrict to a DENSE SUBNETWORK (top-frequency ORFs, capped pair count) so per-token main effects are well-defined and the
learned/closed-form arms stay capacity-tractable.
  PATH A (pairwise structure present -> query/array gene id + epsilon + p columns): run the full SYM-vs-STRONG-additive
    transfer proof. PATH B (columns/download absent): ACQUIRE_FAILED / ESCALATE with a crisp diagnostic (honest, not a
    mechanism refute).

ARMS (regression, MAE lower=better): LEARN_SYM (shared code + PRODUCT = substrate symmetric bind; WINNER hypothesis) ;
  LEARN_ADD (shared code + SUM; matched-capacity LEARNED additive) ; ADD_RIDGE (closed-form ridge on per-token COUNT design;
  STRONG closed-form categorical additive) ; ADD_LSTSQ (closed-form lstsq; additive) ; LEARN_ROLE (role-keyed product;
  ALGEBRA contrast -- must NOT beat SYM on a symmetric target) ; MEAN (train-mean = regression frequency floor) ; MEMORIZE
  (per-token-pair mean; rote, collapses to MEAN on NOVEL) ; ORACLE (true; MAE~0).
  strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel(s,sub) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.
STRATA: seen / novel gene-pair (entity-level split). SUBSET (magnitude-defined, PRE-REGISTERED, scale-free): hi = |epsilon -
  median| > HI_Z*robust_sigma (genuine interaction) / lo = otherwise (moderate control). robust_sigma = 1.4826*MAD.
REGIMES: CLEAN(real) ; ARBITRARY (random target per unique gene-pair; must-fail on NOVEL) ; SHUFFLE (target permutation;
  must-fail on ALL). FIXED GATE positive control = planted symmetric-interaction arena (SYM beats strong-additive by its own
  bar; pos_rel ~0.908 validated); negative control = planted ADDITIVE arena (SYM must NOT beat additive; neg_rel ~-0.018
  validated -> proves the gate is NOT saturation-vacuous).

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_costanzo_epistasis_nativepair_bind_readout.md):
  HARD_PASS_TRANSFER (native-pair real-data linchpin): novel_hi rel_MAE >= 0.30 AND (novel_hi rel - novel_lo rel) >= 0.15
    AND positive-control passes (planted-interaction rel>=0.30) AND negative-control ok (planted-additive rel<=0.10)
    AND must-fails fire (SHUFFLE all rel_sym_vs_mean<=0.08, ARBITRARY novel rel_sym_vs_mean<=0.08) AND oracle MAE~0
    AND leak_ok AND enough high-interaction signal (>=15% of pairs clear the robust-sigma floor) AND novel_hi >=4 mean rows.
  HARD_FAIL_INSUFFICIENT_SIGNAL: <15% of pairs clear the floor -> ESCALATE (larger slice / different pocket; domain NOT closed).
  REFUTE_NO_TRANSFER: novel_hi rel_MAE <= 0.05 (real measured epistasis ALSO additive-capturable = a deep foundation finding)
    with valid must-fails+oracle+controls.
  MIDDLE_BAND: partial / low-power novel_hi / advantage not materially larger on hi than lo.

Compute architecture: (b) sequential-CPU with justification -- arena is O(1e3-1e4) native gene-pairs x tiny (<=Nx32) Adam
  fits (ms each) + numpy solves; GPU yields no speedup on sub-ms matmuls; dominant cost = the pairwise dataset download +
  streaming parse (cached after first run). Capacity bounded by TOP_ORF/MAX_PAIRS so the dense per-token design stays small.
  torch thread-capped. Storage: no_storage / no_composition (single-hop readout). Determinism: FIXED int seeds + stable
  sorted-unique token ids + deterministic stride subsample; NO hash(), NO list(set()) (PROT-023). ASCII-only; no bare except;
  except SystemExit before except Exception; atomic tmp+os.replace. Default invocation (no flag) = FULL run to completion.
  progress_logging: ACQUIRE + streaming-parse row counter (every 1M rows) + per-seed done lines, all flush=True (§17,
  timeout_s >= 1800).
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; float-hash arms-differ on planted arena).
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: regression MAE floor is data-noise-defined (epsilon replicate/assay noise); no closed-form CRLB for the
#     bilinear-readout arm; the HI_Z*robust_sigma hi subset + rel-MAE-reduction gate substitute for a capacity-feasibility cap.
# - baseline_in_band: STRONG additive MAE is measured (not saturated); planted pos/neg controls bound the gate.
# - discriminator survives scale: self-test fires SYM>>additive on planted-interaction SEEN at plant scale (n=600).
# - HARD_PASS strictly above floor: rel>=0.30 AND hi-minus-lo>=0.15 (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive only; MEAN/MEMO/ORACLE/ROLE are contrast arms.
# - cardinality_ok: n_seeds x n_regimes fixed; verdict counts per_seed_regime lengths.
# - per-unit failure-class instrumentation: acquire/parse failures -> explicit ACQUIRE_FAILED / ESCALATE verdicts.
# - calibration_check: adaptive_with_discriminator_gate (HI_Z*robust_sigma magnitude split is data-scale-invariant; the
#     hi-minus-lo>=0.15 gate is the discriminator-still-fires verification; frac_hi>=0.15 is the insufficient-signal gate).
# - all numbers in comments tagged CITED@ (scout drill) / THEORETICAL@ / to-be-MEASURED@ (real-data pending remote run).
# - real_code_path: self-test parses a SYNTHETIC Costanzo TSV (zip-of-txt) through the REAL parser + runs planted arenas
#     through the REAL score()/arm code; hd_bind exercised on complex64 phasors.
# - deterministic_seeding: FIXED int seeds; sorted(set()) token ids + deterministic stride; no hash()/list(set()).

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
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

ANCHOR_NAME = "costanzo_epistasis_nativepair_bind_readout_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CACHE_DIR = os.path.join(_REPO, "data", "foundation_clusters", "costanzo2016_sga")

# ---- data source (Costanzo et al. 2016, Science 353:aaf1420; thecellmap.org/yeast/costanzo2016) ----
# CITED@ notes/drill_real_nonadditive_experimental_datasets_for_conjunction_modules_2026-07-15.md + orchestrator web-verified
# 2026-07-15 (the live thecellmap.org/yeast/costanzo2016 page: filenames have NO "Data File S1. " prefix). PAIRWISE (521MB) =
# one row per (query,array) gene pair with epsilon + p-value + single-mutant fitnesses (drop-in for parse_costanzo). MATRIX
# (35MB, lighter) = gene-x-gene symmetric epsilon matrix (parse_costanzo_matrix, |eps| filter only -- no p-value column).
# ACQUIRE tries PAIRWISE first, then MATRIX fallback if the (large) pairwise download fails/stalls.
PAIRWISE_URLS = [
    ("S1_pairwise_thecellmap_https",
     "https://thecellmap.org/costanzo2016/data_files/"
     "Raw%20genetic%20interaction%20datasets:%20Pair-wise%20interaction%20format.zip"),
]
MATRIX_URLS = [
    ("S2_matrix_thecellmap_https",
     "https://thecellmap.org/costanzo2016/data_files/"
     "Raw%20genetic%20interaction%20datasets:%20Matrix%20format.zip"),
]
# yeast systematic ORF id (e.g. YAL001C, YBR102W-A) for matrix label-row/col detection
_ORF_RE = re.compile(r"^Y[A-P][LR][0-9]{3}[WC](-[A-Z])?$")


def _is_orf(s):
    return bool(_ORF_RE.match(_extract_orf(s)))
EPSILON_DEF = ("epsilon = genetic-interaction score = double-mutant fitness minus the expected (multiplicative) product of "
               "the two single-mutant fitnesses (Costanzo et al. 2016). Negative=aggravating/synthetic-sick-lethal, "
               "positive=alleviating/suppressive.")

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

# ---- pre-registered bands + slice controls (fixed BEFORE running) ----
HI_Z = 1.0                   # hi = |epsilon - median| > HI_Z * robust_sigma (robust_sigma = 1.4826*MAD): genuine 2-way
MIN_HI_FRAC = 0.15           # >=15% of pairs must clear the robust-sigma floor else HARD_FAIL_INSUFFICIENT -> escalate
HP_REL_HI = 0.30             # novel_hi rel_MAE reduction (SYM vs strong additive) >= 0.30
HP_HI_MINUS_LO = 0.15        # advantage materially larger on hi than lo: rel_hi - rel_lo >= 0.15
REFUTE_REL = 0.05            # novel_hi rel_MAE <= 0.05 => collapses to noise => REFUTE
MUSTFAIL_REL_TOL = 0.08      # SHUFFLE(all)+ARBITRARY(novel) rel_sym_vs_mean ceiling
MIN_NOVEL_HI_N = 4.0         # mean novel-hi query rows for adequate power
POS_CTRL_REL = 0.30          # planted-interaction SEEN rel_MAE (positive control must clear its own bar)
NEG_CTRL_REL = 0.10          # planted-additive SEEN rel_MAE ceiling (gate not saturation-vacuous)
EPS_FILTER = 0.08            # |epsilon| significance-magnitude filter (standard Costanzo threshold)
P_MAX = 0.05                 # p-value significance filter
TOP_ORF = 500                # dense-subnetwork cap: keep the top-frequency ORFs (well-defined per-token main effects)
MAX_PAIRS = 8000             # cap native pair count (capacity/tractability of the dense per-token design)
MIN_PAIRS = 200              # PATH-A requires >= this many unique native gene-pairs; else escalate

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
# ACQUIRE (download-if-absent; urllib stdlib; candidate-URL list; cache + provenance)
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


def _try_download(dest, urls, errors):
    """Cache-hit or download-first-of urls to dest. Returns (nbytes, used_url) or (0, None)."""
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        nb = os.path.getsize(dest)
        _log("ACQUIRE cache-hit %s (%d bytes)" % (os.path.basename(dest), nb))
        return nb, "cache"
    for tag, url in urls:
        nb, err = _download_one(url, dest)
        if err is None and nb > 100000:
            _log("ACQUIRE downloaded via %s (%d bytes)" % (tag, nb))
            return nb, url
        errors[tag] = err or ("too_small:%d" % nb)
        _log("ACQUIRE candidate FAILED %s : %s" % (tag, errors[tag]))
    return 0, None


def acquire():
    """Download-if-absent the Costanzo 2016 dataset -> CACHE_DIR. Tries PAIRWISE first (drop-in), MATRIX fallback if the
    large pairwise download fails/stalls. Returns (path or None, kind in {'pairwise','matrix','none'}, provenance)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    errors = {}
    kind = "none"; used_url = None; nbytes = 0; dest = None

    destP = os.path.join(CACHE_DIR, "costanzo2016_pairwise.zip")
    nb, uu = _try_download(destP, PAIRWISE_URLS, errors)
    if uu is not None:
        kind, used_url, nbytes, dest = "pairwise", uu, nb, destP
    else:
        destM = os.path.join(CACHE_DIR, "costanzo2016_matrix.zip")
        nb, uu = _try_download(destM, MATRIX_URLS, errors)
        if uu is not None:
            kind, used_url, nbytes, dest = "matrix", uu, nb, destM

    prov = dict(dataset="Costanzo2016_yeast_SGA", paper="Costanzo et al. 2016, Science 353:aaf1420",
                source="thecellmap.org/yeast/costanzo2016", kind=kind, url_used=used_url,
                urls_tried=dict(PAIRWISE_URLS + MATRIX_URLS),
                retrieval_ts=datetime.now(timezone.utc).isoformat(), interaction_definition=EPSILON_DEF,
                bytes=int(nbytes), acquire_errors=errors,
                filter=("|epsilon| > %.3f AND p < %.3f (pairwise); |epsilon| > %.3f only (matrix has no p-value)"
                        % (EPS_FILTER, P_MAX, EPS_FILTER)),
                slice_controls=dict(TOP_ORF=TOP_ORF, MAX_PAIRS=MAX_PAIRS))
    try:
        with open(os.path.join(CACHE_DIR, "provenance.json"), "w", encoding="utf-8") as f:
            json.dump(prov, f, indent=2)
    except OSError:
        pass
    if dest is not None and nbytes > 100000 and os.path.exists(dest):
        return dest, kind, prov
    return None, "none", prov


# ===========================================================================
# PARSE + STRUCTURE DETECTION (native gene-pair Costanzo pairwise TSV; zip-of-txt or plain text)
# ===========================================================================

def _norm(s):
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")


def detect_costanzo_columns(header):
    """Return ('costanzo', {'q','a','eps','p'}) | ('unknown', {}). Matches the pairwise columns Query/Array Strain ID,
    'Genetic interaction score (eps)' (ASCII substring match avoids the unicode epsilon), and P-value."""
    cols = {_norm(h): h for h in header}

    def _role(role):
        for key in cols:
            if role in key and "strain" in key:
                return cols[key]
        for key in cols:
            if role in key and "orf" in key:
                return cols[key]
        for key in cols:
            if role in key and "allele" in key:
                return cols[key]
        return None

    q = _role("query"); a = _role("array")
    eps = None
    for key in cols:
        if ("genetic_interaction_score" in key or "interaction_score" in key
                or key.startswith("epsilon") or key == "eps"):
            eps = cols[key]; break
    if eps is None:
        for key in cols:
            if "score" in key and "interaction" in key:
                eps = cols[key]; break
    p = None
    for key in cols:
        if "p_value" in key or key == "pvalue" or key == "p_val" or key == "p":
            p = cols[key]; break
    if q is not None and a is not None and eps is not None and p is not None:
        return "costanzo", {"q": q, "a": a, "eps": eps, "p": p}
    return "unknown", {}


def _finite_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _extract_orf(v):
    """Systematic ORF token = the strain-id prefix before the first underscore (e.g. 'YAL001C_tsq123' -> 'YAL001C');
    falls back to the whole value if no underscore (e.g. an allele name)."""
    v = str(v).strip()
    if not v:
        return ""
    return v.split("_")[0].strip().upper()


def parse_costanzo(path):
    """Stream the Costanzo pairwise TSV (zip-of-txt members or plain text); filter to significant measured interactions
    (|epsilon|>EPS_FILTER AND p<P_MAX); aggregate multi-strain rows to mean epsilon per canonical ORF-pair; restrict to a
    dense subnetwork (top-frequency ORFs) capped at MAX_PAIRS. Returns PATH 'A' (X,y,n_tok,...) or PATH 'B' (escalate)."""
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
    except OSError as e:
        return {"path": "B", "reason": "open_failed:%s" % (str(e)[:120])}
    is_zip = magic[:2] == b"PK"

    per_pair = defaultdict(lambda: [0.0, 0])  # (orfA, orfB) canonical string tuple -> [sum epsilon, count]
    members_info = []
    counters = {"n_rows": 0, "n_kept": 0}

    def _process(name, textstream):
        rdr = csv.reader(textstream, delimiter="\t")
        try:
            header = next(rdr)
        except StopIteration:
            members_info.append({"member": name, "error": "empty"}); return
        # some releases are comma-delimited; retry if tab header did not split
        if len(header) <= 1:
            textstream.seek(0)
            rdr = csv.reader(textstream, delimiter=",")
            try:
                header = next(rdr)
            except StopIteration:
                members_info.append({"member": name, "error": "empty"}); return
        kind, colmap = detect_costanzo_columns(header)
        if kind != "costanzo":
            members_info.append({"member": name, "kind": "unknown", "header": [str(x) for x in header[:14]]}); return
        iq = header.index(colmap["q"]); ia = header.index(colmap["a"])
        ie = header.index(colmap["eps"]); ip = header.index(colmap["p"])
        need = max(iq, ia, ie, ip)
        kept_here = 0
        for row in rdr:
            counters["n_rows"] += 1
            if (counters["n_rows"] % 1000000) == 0:
                _log("PARSE... %d rows scanned, %d kept (|eps|>%.2f & p<%.2f)"
                     % (counters["n_rows"], counters["n_kept"], EPS_FILTER, P_MAX))
            if len(row) <= need:
                continue
            eps = _finite_float(row[ie]); pv = _finite_float(row[ip])
            if eps is None or pv is None:
                continue
            if not (abs(eps) > EPS_FILTER and pv < P_MAX):
                continue
            oa = _extract_orf(row[iq]); ob = _extract_orf(row[ia])
            if not oa or not ob or oa == ob:
                continue
            key = (oa, ob) if oa < ob else (ob, oa)
            acc = per_pair[key]; acc[0] += eps; acc[1] += 1
            counters["n_kept"] += 1; kept_here += 1
        members_info.append({"member": name, "kind": "costanzo", "kept": kept_here})

    if is_zip:
        try:
            zf = zipfile.ZipFile(path, "r")
        except zipfile.BadZipFile as e:
            return {"path": "B", "reason": "bad_zip:%s" % (str(e)[:120])}
        try:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            txt = [n for n in names if n.lower().endswith((".txt", ".tsv"))] or names
            for n in sorted(txt):
                with zf.open(n, "r") as fh:
                    _process(n, io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline=""))
        finally:
            zf.close()
    else:
        with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            _process(os.path.basename(path), fh)

    return _finalize_pairs(per_pair, counters["n_rows"], counters["n_kept"], members_info)


def parse_costanzo_matrix(path):
    """FALLBACK parser for the Costanzo MATRIX format (35MB; used only if the 521MB pairwise download fails). Each member is
    a gene-x-gene symmetric epsilon matrix. CONSERVATIVE: locate the array-label ROW and query-label COLUMN by counting
    ORF-like cells (systematic yeast ORF ids); require substantial ORF labelling else ESCALATE (never fabricate pairs). No
    p-value in matrix format -> filter on |epsilon|>EPS_FILTER only. Canonical upper-triangle dedupes the symmetric matrix."""
    per_pair = defaultdict(lambda: [0.0, 0])
    members_info = []
    counters = {"n_rows": 0, "n_kept": 0}

    def _process(name, all_rows):
        if len(all_rows) < 3:
            members_info.append({"member": name, "error": "too_few_rows"}); return
        scan = min(len(all_rows), 50)
        maxcols = max((len(all_rows[ri]) for ri in range(scan)), default=0)
        best_hr, best_hr_cnt = -1, 0
        for ri in range(scan):
            cnt = sum(1 for c in all_rows[ri] if _is_orf(c))
            if cnt > best_hr_cnt:
                best_hr_cnt, best_hr = cnt, ri
        best_lc, best_lc_cnt = -1, 0
        for ci in range(min(maxcols, 50)):
            cnt = sum(1 for r in all_rows if ci < len(r) and _is_orf(r[ci]))
            if cnt > best_lc_cnt:
                best_lc_cnt, best_lc = cnt, ci
        if best_hr < 0 or best_lc < 0 or best_hr_cnt < 10 or best_lc_cnt < 10:
            members_info.append({"member": name, "error": "no_orf_labels", "hr_cnt": best_hr_cnt,
                                 "lc_cnt": best_lc_cnt, "header": [str(x) for x in all_rows[0][:14]]}); return
        array_labels = all_rows[best_hr]
        kept_here = 0
        for ri in range(best_hr + 1, len(all_rows)):
            row = all_rows[ri]
            if best_lc >= len(row) or not _is_orf(row[best_lc]):
                continue
            qorf = _extract_orf(row[best_lc])
            for ci in range(best_lc + 1, min(len(row), len(array_labels))):
                if not _is_orf(array_labels[ci]):
                    continue
                counters["n_rows"] += 1
                eps = _finite_float(row[ci])
                if eps is None or abs(eps) <= EPS_FILTER:
                    continue
                aorf = _extract_orf(array_labels[ci])
                if not qorf or not aorf or qorf == aorf:
                    continue
                key = (qorf, aorf) if qorf < aorf else (aorf, qorf)
                acc = per_pair[key]; acc[0] += eps; acc[1] += 1
                counters["n_kept"] += 1; kept_here += 1
        members_info.append({"member": name, "kind": "matrix", "kept": kept_here, "hr": best_hr, "lc": best_lc})

    try:
        with open(path, "rb") as f:
            is_zip = f.read(4)[:2] == b"PK"
    except OSError as e:
        return {"path": "B", "reason": "open_failed:%s" % (str(e)[:120])}
    if is_zip:
        try:
            zf = zipfile.ZipFile(path, "r")
        except zipfile.BadZipFile as e:
            return {"path": "B", "reason": "bad_zip:%s" % (str(e)[:120])}
        try:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            txt = [n for n in names if n.lower().endswith((".txt", ".tsv", ".csv"))] or names
            for n in sorted(txt):
                with zf.open(n, "r") as fh:
                    ts = io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline="")
                    rows = [row for row in csv.reader(ts, delimiter="\t")]
                    if rows and max((len(r) for r in rows[:5]), default=0) <= 1:
                        ts2 = io.TextIOWrapper(zf.open(n, "r"), encoding="utf-8", errors="replace", newline="")
                        rows = [row for row in csv.reader(ts2, delimiter=",")]
                    _process(n, rows)
        finally:
            zf.close()
    else:
        with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            _process(os.path.basename(path), [row for row in csv.reader(fh, delimiter="\t")])
    return _finalize_pairs(per_pair, counters["n_rows"], counters["n_kept"], members_info)


def _finalize_pairs(per_pair, n_rows, n_kept, members_info):
    """Shared PATH-A finalizer: aggregate ORF-pair means -> dense subnetwork (top-frequency ORFs) -> cap MAX_PAIRS ->
    reindex tokens contiguous. Returns PATH 'A' (X,y,n_tok,...) or PATH 'B' (escalate)."""
    pair_mean = {k: (s / c) for k, (s, c) in per_pair.items() if c > 0}
    if not pair_mean:
        return {"path": "B", "reason": "no_pairs_after_filter", "n_rows": n_rows, "members": members_info}
    orf_freq = defaultdict(int)
    for (a, b) in pair_mean:
        orf_freq[a] += 1; orf_freq[b] += 1
    top = set(sorted(orf_freq.keys(), key=lambda o: (-orf_freq[o], o))[:TOP_ORF])
    pairs = sorted([k for k in pair_mean.keys() if k[0] in top and k[1] in top])
    if len(pairs) > MAX_PAIRS:
        stride = int(math.ceil(len(pairs) / float(MAX_PAIRS)))
        pairs = pairs[::stride][:MAX_PAIRS]  # deterministic evenly-spaced subsample
    if len(pairs) < MIN_PAIRS:
        return {"path": "B", "reason": "insufficient_native_pairs", "n_pairs": len(pairs), "n_rows": n_rows,
                "n_kept": n_kept, "members": members_info}
    toks = sorted(set([o for k in pairs for o in k]))
    tokid = {o: i for i, o in enumerate(toks)}
    Xl = []
    for k in pairs:
        i0 = tokid[k[0]]; i1 = tokid[k[1]]
        Xl.append([min(i0, i1), max(i0, i1)])
    X = np.array(Xl, dtype=np.int64)
    y = np.array([pair_mean[k] for k in pairs], dtype=np.float64)
    return {"path": "A", "X": X, "y": y, "n_tok": len(toks), "n_pairs": len(pairs), "n_rows": n_rows,
            "n_kept": n_kept, "members": members_info, "top_orf_kept": len(top),
            "cells_per_pair_mean": float(np.mean([per_pair[k][1] for k in pairs]))}


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
    mag = np.abs(y_real[q] - hi_center)  # subset membership defined on the REAL epsilon magnitude (robust-centered)

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
    path, kind, prov = acquire()
    base = dict(run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
                elapsed_s=round(time.perf_counter() - t0, 2), provenance=prov, seeds=list(seeds),
                bands=dict(HI_Z=HI_Z, MIN_HI_FRAC=MIN_HI_FRAC, HP_REL_HI=HP_REL_HI, HP_HI_MINUS_LO=HP_HI_MINUS_LO,
                           REFUTE_REL=REFUTE_REL, MUSTFAIL_REL_TOL=MUSTFAIL_REL_TOL, MIN_NOVEL_HI_N=MIN_NOVEL_HI_N,
                           POS_CTRL_REL=POS_CTRL_REL, NEG_CTRL_REL=NEG_CTRL_REL, EPS_FILTER=EPS_FILTER, P_MAX=P_MAX,
                           TOP_ORF=TOP_ORF, MAX_PAIRS=MAX_PAIRS, MIN_PAIRS=MIN_PAIRS))

    # positive/negative controls (planted; the FIXED gate carries a genuine non-additive positive control)
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    pos_ok = bool(pos_rel == pos_rel and pos_rel >= POS_CTRL_REL)
    neg_ok = bool(neg_rel == neg_rel and neg_rel <= NEG_CTRL_REL)
    base["controls"] = dict(pos_rel=round(pos_rel, 5), pos_sym_mae=round(pos_sym, 5), pos_sadd_mae=round(pos_sadd, 5),
                            neg_rel=round(neg_rel, 5), neg_sym_mae=round(neg_sym, 5), neg_sadd_mae=round(neg_sadd, 5),
                            pos_ok=pos_ok, neg_ok=neg_ok)

    if path is None:
        msg = ("ACQUIRE_FAILED || could not download the Costanzo pairwise dataset from any candidate URL (see "
               "provenance.acquire_errors). pos_ctrl_rel=%s neg_ctrl_rel=%s (machinery %s)." %
               (_fmt(pos_rel), _fmt(neg_rel), "VALID" if (pos_ok and neg_ok) else "CHECK"))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200])
        return base

    try:
        data = parse_costanzo_matrix(path) if kind == "matrix" else parse_costanzo(path)
    except (zipfile.BadZipFile, OSError, csv.Error, UnicodeDecodeError) as e:
        msg = ("ACQUIRE_FAILED || Costanzo file present but unreadable: %s: %s. pos_ctrl_rel=%s neg_ctrl_rel=%s."
               % (type(e).__name__, str(e)[:160], _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200], parse_error=str(e)[:300])
        return base

    if data["path"] == "B":
        rec = ("larger Costanzo slice (raise MAX_PAIRS / lower EPS_FILTER) OR DrugComb synergy fallback")
        msg = ("ESCALATE_COSTANZO_NO_NATIVEPAIR_STRUCTURE || could not build a native gene-pair slice "
               "(reason=%s n_pairs=%s n_rows=%s members=%s). HAND-OFF: %s. pos_ctrl_rel=%s neg_ctrl_rel=%s"
               % (data.get("reason"), data.get("n_pairs"), data.get("n_rows"),
                  json.dumps(data.get("members", []))[:400], rec, _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ESCALATE_COSTANZO_NO_NATIVEPAIR_STRUCTURE", verdict_msg=msg, summary=msg[:200],
                    escalate=True, path="B", parse_diag={k: v for k, v in data.items() if k not in ("path",)})
        return base

    # ---------- PATH A: real native-pair transfer proof ----------
    X, y, n_tok = data["X"], data["y"], data["n_tok"]
    hi_center, hi_scale = _robust_center_scale(y)
    frac_hi = float((np.abs(y - hi_center) > (HI_Z * hi_scale)).mean())
    _log("PATH A: n_pairs=%d n_tok=%d n_rows=%d n_kept=%d cells/pair=%.1f | median=%.4f robust_sigma=%.4f "
         "frac_hi(|z|>%.1f)=%.3f seeds=%d"
         % (X.shape[0], n_tok, data.get("n_rows", 0), data.get("n_kept", 0), data.get("cells_per_pair_mean", 0.0),
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
        verdict = "HARD_FAIL_INSUFFICIENT_SIGNAL_ESCALATE_LARGER_SLICE"
    elif not power_ok:
        verdict = "MIDDLE_BAND_LOW_POWER_NOVEL_HI"
    elif hard_pass:
        verdict = "HARD_PASS_TRANSFER_SYMMETRIC_BIND_READS_REAL_YEAST_EPISTASIS"
    elif refute:
        verdict = "REFUTE_NO_TRANSFER_SYM_DOES_NOT_READ_YEAST_EPISTASIS"
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
        n_rows_scanned=int(data.get("n_rows", 0)), n_kept=int(data.get("n_kept", 0)),
        cells_per_pair_mean=round(float(data.get("cells_per_pair_mean", 0.0)), 3), members=data.get("members"),
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
# SELF-TEST (real bind path + REAL parser on a synthetic Costanzo TSV + planted controls + arms-differ + determinism)
# ===========================================================================

def _make_synth_costanzo_zip(path, n_pairs=60, n_strains=3, n_orfs=12):
    """Write a tiny synthetic Costanzo-shaped pairwise TSV (zip-of-txt, matching the real release) -> exercises the REAL
    parser/detector PATH-A code end-to-end (filter + ORF extraction + subnetwork + reindex). Planted symmetric interaction;
    all |epsilon| > EPS_FILTER and p < P_MAX so every pair survives the filter."""
    rng = np.random.default_rng(101)
    header = ["Query Strain ID", "Query allele name", "Array Strain ID", "Array allele name", "Arm",
              "Genetic interaction score (eps)", "P-value", "Query SMF", "Array SMF", "Double mutant fitness",
              "Double mutant fitness std"]
    orfs = ["YAL%03dC" % (d + 1) for d in range(n_orfs)]
    tab = rng.normal(0, 1, size=(n_orfs, n_orfs)); tab = 0.5 * (tab + tab.T)
    made = set()
    while len(made) < n_pairs:
        i, j = int(rng.integers(0, n_orfs)), int(rng.integers(0, n_orfs))
        if i != j:
            made.add((min(i, j), max(i, j)))
    lines = ["\t".join(header)]
    for (i, j) in sorted(made):
        for s in range(n_strains):
            sgn = 1.0 if tab[i, j] >= 0 else -1.0
            eps = sgn * (0.1 + 0.3 * abs(float(tab[i, j])))  # |eps| >= 0.1 > EPS_FILTER
            lines.append("\t".join([
                "%s_tsq%d" % (orfs[i], s), "%s-1" % orfs[i].lower(),
                "%s_dma%d" % (orfs[j], s), "%s-2" % orfs[j].lower(), "chrI",
                "%.4f" % eps, "0.0100", "0.95", "0.94", "0.85", "0.02"]))
    tsv_text = "\n".join(lines) + "\n"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SGA_NxN_synth.txt", tsv_text)


def _make_synth_costanzo_matrix_zip(path, n_orfs=12):
    """Write a tiny synthetic Costanzo MATRIX-format zip (gene-x-gene symmetric epsilon matrix with ORF label row + col) ->
    exercises the REAL parse_costanzo_matrix fallback end-to-end."""
    rng = np.random.default_rng(202)
    orfs = ["YAL%03dC" % (d + 1) for d in range(n_orfs)]
    tab = rng.normal(0, 1, size=(n_orfs, n_orfs)); tab = 0.5 * (tab + tab.T)
    lines = ["\t".join([""] + orfs)]  # header row: blank corner + array-gene labels
    for i in range(n_orfs):
        cells = [orfs[i]]  # row label = query gene
        for j in range(n_orfs):
            if i == j:
                cells.append("0.0000")
            else:
                sgn = 1.0 if tab[i, j] >= 0 else -1.0
                cells.append("%.4f" % (sgn * (0.1 + 0.3 * abs(float(tab[i, j])))))  # |eps| >= 0.1 > EPS_FILTER
        lines.append("\t".join(cells))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("costanzo_matrix_synth.txt", "\n".join(lines) + "\n")


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

    # (3) REAL PARSER on a synthetic Costanzo pairwise TSV zip (exercises detect_costanzo_columns + parse_costanzo PATH-A).
    tmp_zip = os.path.join(CACHE_DIR, "_selftest_synth_costanzo.zip")
    os.makedirs(CACHE_DIR, exist_ok=True)
    _make_synth_costanzo_zip(tmp_zip, n_pairs=60, n_strains=3, n_orfs=12)
    saved_min = MIN_PAIRS
    try:
        globals()["MIN_PAIRS"] = 40  # synthetic slice is tiny; relax the PATH-A floor for the self-test only
        sd = parse_costanzo(tmp_zip)
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
    # a header with no query/array/eps columns must route to unknown (escalate)
    unk_kind, _ = detect_costanzo_columns(["ID", "SMILES", "VALUE", "Nonadd_pC"])
    nonpair_routes_B = (unk_kind == "unknown")
    details["nonpair_header_routes_B"] = nonpair_routes_B

    # (3b) REAL MATRIX-FALLBACK parser on a synthetic gene-x-gene epsilon matrix (exercises parse_costanzo_matrix PATH-A).
    tmp_mzip = os.path.join(CACHE_DIR, "_selftest_synth_matrix.zip")
    _make_synth_costanzo_matrix_zip(tmp_mzip, n_orfs=12)
    saved_min2 = MIN_PAIRS
    try:
        globals()["MIN_PAIRS"] = 40
        md = parse_costanzo_matrix(tmp_mzip)
    finally:
        globals()["MIN_PAIRS"] = saved_min2
        try:
            os.remove(tmp_mzip)
        except OSError:
            pass
    matrix_ok = bool(md.get("path") == "A" and md.get("n_tok", 0) == 12 and md.get("n_pairs", 0) == 66)
    details["matrix_path"] = md.get("path"); details["matrix_n_pairs"] = md.get("n_pairs")
    details["matrix_n_tok"] = md.get("n_tok"); details["matrix_ok"] = matrix_ok

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
        "matrix_fallback_parser_reconstructs_pairs": matrix_ok,
        "nonpair_header_routes_to_escalate": nonpair_routes_B,
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
