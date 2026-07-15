"""COSTANZO_NEARZERO_SINGLES_CURATED_IVF (v1): SUBSET-CURATED real-data DISCRIMINATOR (conjunction MODULE, Costanzo yeast SGA).
The three prior real-data negatives (chem MMP / LLM-narrated epistasis / the FAIR genome-wide Costanzo epsilon test) all
measured at the BULK/genome-wide scale, where a negative-drill
(notes/drill_negative_why_real_interactions_additive_capturable_where_genuine_2026-07-15.md) shows genuine molecular
non-additivity is MEASUREMENT-HIDDEN (Hill-Goddard-Visscher allele-frequency projection + Simpson's-paradox aggregation
dilution). FIX = SUBSET-CURATION, not domain abandonment: restrict the Costanzo pairwise data to the NEAR-ZERO-SINGLES
synthetic-lethal / AND-gate pocket -- gene-pairs where BOTH single-mutant fitness (SMF) values are within noise of wild-type
(main effect ~0 by DIRECT measurement, NOT inferred from population variance) YET the double-mutant |epsilon| is large -- the
one pocket where the additive escape-hatch (allele-frequency projection) structurally cannot apply (full knockouts, no
segregating alleles at intermediate frequency).

PRIMARY DISCRIMINATING STATISTIC = interaction-variance-fraction IVF (per-pair additive-residual variance / total variance)
computed with ONE shared out-of-fold per-gene-main-effects model on the full significant subnetwork, then evaluated
SEPARATELY on (a) the curated near-zero-singles subset and (b) a size-matched RANDOM subset of all pairs. Shared-model design
is confound-robust: the ONLY difference between the two IVF numbers is WHICH pairs are scored (identical per-gene main-effect
estimates, no subset-sparsity artifact). HARD_PASS requires IVF(curated) >= 3x IVF(matched-random) AND the SUBSET transfer
proof (LEARN_SYM shared-code+PRODUCT symmetric bind vs capacity-matched STRONG categorical-additive) clears >=30% relative-MAE
reduction on NOVEL curated pairs, with the SIGNAL-READABILITY gate as a precondition. This disambiguates the prior fair-test
REFUTE: readable non-additivity present in a curated real pocket => prior REFUTEs were bulk-measurement artifacts + module #1
is real; absent even in the best-available pocket => genuine rarity / operator-structural gap.

Glass-box CPU, NO LLM at readout. All compute REMOTE (the cell downloads the pairwise dataset at runtime; the remote
--self-test with planted arenas -- which fires the near-zero-singles selector, the IVF discriminator, and the transfer/
readability gates on synthetic data -- is the network-independent gate). REQUIRES the PAIRWISE file (SMF columns needed for
the near-zero-singles selector); the MATRIX fallback lacks SMF -> ESCALATE_NEED_PAIRWISE_FOR_SMF.

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
CURATION: parse per-gene single-mutant fitness (SMF) columns; a gene is a NEAR-ZERO-SINGLE if its mean SMF is within the WT
  band [SMF_WT_LO=0.90, SMF_WT_HI=1.10]. CURATED pocket = significant pairs where BOTH genes are near-zero-singles. MATCHED-
  RANDOM = a size-matched random draw of the SAME count from ALL significant pairs.
PRIMARY STATISTIC (IVF): one SHARED out-of-fold per-gene-main-effects ridge model on the FULL subnetwork -> residual per pair
  -> IVF(subset) = Var(residual[subset]) / Var(y[subset]). Report IVF(curated) vs IVF(matched-random) side by side; the ratio
  isolates WHICH pairs (identical main-effect estimates -> no subset-sparsity confound).
STRATA (transfer arena): seen / novel gene-pair (entity-level split) on the CURATED near-zero-singles arena; NOVEL is the
  honest stratum (the whole pocket is high-interaction so the full curated stratum is the transfer target).
REGIMES: CLEAN(real) ; ARBITRARY (random target per unique gene-pair; must-fail on NOVEL) ; SHUFFLE (target permutation;
  must-fail on ALL). FIXED GATE positive control = planted symmetric-interaction arena (SYM beats strong-additive by its own
  bar; pos_rel ~0.908 validated); negative control = planted ADDITIVE arena (SYM must NOT beat additive; neg_rel ~-0.018
  validated -> proves the gate is NOT saturation-vacuous).

SIGNAL-READABILITY GATE (VET a57067090 revival criterion -- precondition): BEFORE the SYM-vs-additive transfer test can be
interpreted, a readable target must be CERTIFIED to exist on the curated pocket -- readable_rel = max(strong_additive, SYM) vs
MEAN >= READABILITY_REL=0.15. Gate FAILS -> UNREADABLE_ESCALATE (a DATASET-SNR null, NOT a thesis result). SNR levers already
applied: |eps|>0.12 STRINGENT tier + >=2 replicate measurements/pair + TOP_ORF=500 subnetwork (well-defined main effects).

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_costanzo_nearzero_singles_curated_ivf.md):
  HARD_PASS (curated pocket is non-additive AND transfers): IVF(curated) >= IVF_RATIO_HP=3x IVF(matched-random) AND IVF(curated)
    >= IVF_CURATED_FLOOR=0.30 AND readability PASSES AND NOVEL curated rel_MAE (SYM vs strong-additive) >= HP_REL_CURATED=0.30
    AND positive-control passes (>=0.30) AND negative-control ok (<=0.10) AND must-fails fire (SHUFFLE all + ARBITRARY novel
    rel_sym_vs_mean <= 0.08) AND oracle MAE~0 AND leak_ok AND novel_curated_n >= 8.
  HARD_FAIL_UNDERPOWERED_CURATED_N: < MIN_CURATED=50 clean near-zero-singles pairs -> insufficient N -> ESCALATE to the enCas12a
    paralog-buffering compendium (Dede et al. PMC7558751) / Benchmarking-GI-Scores harmonized compendium (higher-N fallbacks).
  ESCALATE_NEED_PAIRWISE_FOR_SMF: acquired file has no SMF columns (matrix format) -> near-zero-singles uncomputable -> re-run
    on the pairwise zip.
  UNREADABLE_ESCALATE: readability FAILS on the curated pocket -> DATASET-SNR null (not a thesis result) -> higher-SNR pocket.
  REFUTE_GENUINE_RARITY: readability PASSES but IVF(curated) is within noise of matched-random (ratio <= 1.30) AND novel
    curated rel_MAE <= 0.05 -> genuine rarity dominates even in the best-available real pocket (a deep foundation finding).
  MIDDLE_BAND: partial (IVF enriched but transfer weak, or transfer OK but IVF not enriched) / low-power novel curated.

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
#     bilinear-readout arm; the IVF-ratio>=3x + rel-MAE-reduction gate substitute for a capacity-feasibility cap.
# - baseline_in_band: STRONG additive MAE is measured (not saturated); planted pos/neg controls bound the gate.
# - discriminator survives scale: self-test fires (a) IVF(interaction subset) >> 3x IVF(additive subset) via the SHARED
#     out-of-fold model on a planted arena, AND (b) SYM>>additive on planted-interaction SEEN at plant scale (n=600).
# - HARD_PASS strictly above floor: IVF ratio>=3.0 AND IVF(curated)>=0.30 AND novel curated rel>=0.30 (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive + the IVF ratio only; MEAN/MEMO/ORACLE/ROLE are contrast.
# - cardinality_ok: n_seeds x n_regimes on the curated arena + n_seeds IVF folds; verdict counts per_seed_regime lengths.
# - per-unit failure-class instrumentation: acquire/parse/SMF failures -> explicit ACQUIRE_FAILED / ESCALATE_NEED_PAIRWISE_
#     FOR_SMF / HARD_FAIL_UNDERPOWERED_CURATED_N verdicts (no silent continue).
# - calibration_check: adaptive_with_discriminator_gate (near-zero-singles SMF band + the IVF-ratio>=3x-vs-matched-random gate
#     are the discriminator-still-fires verification; MIN_CURATED=50 is the insufficient-N guard; the SIGNAL-READABILITY gate
#     readable_rel>=0.15 certifies a READABLE target EXISTS before the SYM-vs-additive test is interpretable -- self-test fires
#     the IVF discriminator + readability on planted arenas and rejects a pure-noise/pure-additive arena).
# - all numbers in comments tagged CITED@ (drill) / THEORETICAL@ / to-be-MEASURED@ (real-data pending remote run).
# - real_code_path: self-test parses a SYNTHETIC Costanzo TSV WITH SMF columns (zip-of-txt) through the REAL parser +
#     near_zero_singles_mask + oof_additive_residual/ivf_of + runs planted arenas through the REAL score()/arm code;
#     hd_bind exercised on complex64 phasors.
# - deterministic_seeding: FIXED int seeds; sorted(set()) token ids + deterministic stride + strided IVF folds; no hash()/
#     list(set()).

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

ANCHOR_NAME = "costanzo_nearzero_singles_curated_ivf_v1"
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
# ---- SIGNAL-READABILITY GATE (VET a57067090 revival criterion; the FIRST interpretability gate) ----
# The v1 REFUTE was adjudicated a NARROW encoding/SNR null: at cells_per_pair~1.8 the per-pair epsilon is noise-dominated, the
# strong additive beat a MEAN-predictor by only ~2.9% (CITED@VET a57067090), so NO readable non-additive target existed and the
# SYM-vs-additive comparison was uninterpretable. FIX: certify a READABLE target EXISTS on the hi-|epsilon| subset BEFORE the
# transfer test can mean anything. readable_rel = max(strong_additive, SYM) vs MEAN (best structured readout clears mean =
# readable-signal certificate; the "or oracle-ish readable-signal proxy" the VET permitted -- robust to a PURE-interaction
# target that additive alone would miss). Gate FAILS -> UNREADABLE_ESCALATE (a DATASET-SNR null, NOT a thesis result).
READABILITY_REL = 0.15       # readable_rel (best structured readout vs MEAN on all_hi) >= this else UNREADABLE_ESCALATE
HP_REL_HI = 0.30             # novel_hi rel_MAE reduction (SYM vs strong additive) >= 0.30
HP_HI_MINUS_LO = 0.15        # advantage materially larger on hi than lo: rel_hi - rel_lo >= 0.15
REFUTE_REL = 0.05            # novel_hi rel_MAE <= 0.05 => collapses to additive-capturable => REFUTE (only if readable)
MUSTFAIL_REL_TOL = 0.08      # SHUFFLE(all)+ARBITRARY(novel) rel_sym_vs_mean ceiling
MIN_NOVEL_HI_N = 4.0         # mean novel-hi query rows for adequate power
POS_CTRL_REL = 0.30          # planted-interaction SEEN rel_MAE (positive control must clear its own bar)
NEG_CTRL_REL = 0.10          # planted-additive SEEN rel_MAE ceiling (gate not saturation-vacuous)
# ---- readable-slice SNR levers (raise per-pair SNR so a READABLE target can exist; VET revival strategy) ----
EPS_FILTER = 0.12            # |epsilon| filter RAISED to Costanzo STRINGENT-confidence tier (was 0.08): stronger, cleaner eps
P_MAX = 0.05                 # p-value significance filter (standard Costanzo)
MIN_CELLS_PER_PAIR = 2       # require >=2 replicate measurements/ORF-pair: drop the noisiest singletons (mean-of->=2 = cleaner)
TOP_ORF = 500                # subnetwork density (top-frequency ORFs): well-defined per-gene main effects for the additive model
MAX_PAIRS = 12000            # cap native pair count (RAISED so the near-zero-singles curated SUBSET still clears MIN_CURATED)
MIN_PAIRS = 200              # PATH-A requires >= this many unique native gene-pairs; else escalate

# ---- NEAR-ZERO-SINGLES CURATION (this cell's subset selector; SMF = single-mutant fitness, WT normalized ~1.0) ----
# A gene is a NEAR-ZERO-SINGLE if its mean SMF sits within the WT band [SMF_WT_LO, SMF_WT_HI] (single-mutant fitness DEFECT
# ~0 by DIRECT measurement). CURATED pocket = pairs where BOTH constituent genes are near-zero-singles yet the pair cleared the
# |epsilon|>EPS_FILTER significance filter (large double-mutant deviation = AND-gate / synthetic-lethal). This is the pocket
# where the additive escape-hatch (Hill-Goddard-Visscher allele-frequency projection) structurally cannot apply.
SMF_WT_LO = 0.90             # near-WT lower band (<=10% single-mutant fitness defect)
SMF_WT_HI = 1.10             # near-WT upper band (mild suppressor tolerance)
MIN_CURATED = 50             # HARD-FAIL if < this many clean near-zero-singles pairs (drill's ~50 power floor) -> escalate
# ---- PRIMARY DISCRIMINATING STATISTIC: interaction-variance-fraction (IVF) ----
# IVF(mask) = Var(oof_additive_residual[mask]) / Var(y[mask]); ONE shared out-of-fold per-gene-main-effects model on the FULL
# significant subnetwork -> the ratio IVF(curated)/IVF(matched-random) isolates WHICH pairs (no subset-sparsity confound).
IVF_KFOLD = 5
IVF_RIDGE_L2 = 1.0
IVF_RATIO_HP = 3.0           # HARD_PASS: IVF(curated) >= 3x IVF(matched-random) (drill's >=3x band)
IVF_CURATED_FLOOR = 0.30     # AND IVF(curated) itself >= 0.30 absolute (>=30% of curated variance is irreducibly pairwise)
IVF_RATIO_INDISTINCT = 1.30  # REFUTE (genuine rarity): curated IVF within ~noise of random (ratio <= this) AND transfer weak
# ---- transfer proof on the curated pocket (SYM vs strong additive; NOVEL curated pairs = the honest stratum) ----
HP_REL_CURATED = 0.30        # NOVEL curated rel_MAE reduction (SYM vs strong additive) >= 0.30 (Kramer-comparable margin)
MIN_NOVEL_CURATED_N = 8.0    # mean novel curated query rows for adequate transfer power

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

    # single-mutant fitness columns (near-zero-singles selector needs these; real pairwise file:
    # 'Query single mutant fitness (SMF)' + 'Array SMF'). Optional -> curated pocket unavailable if absent.
    def _smf(role):
        for key in cols:
            if role in key and ("smf" in key or "single_mutant_fitness" in key):
                return cols[key]
        return None
    smf_q = _smf("query"); smf_a = _smf("array")

    if q is not None and a is not None and eps is not None and p is not None:
        return "costanzo", {"q": q, "a": a, "eps": eps, "p": p, "smf_q": smf_q, "smf_a": smf_a}
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
    per_gene_smf = defaultdict(lambda: [0.0, 0])  # orf -> [sum single-mutant-fitness, count] (near-zero-singles selector)
    members_info = []
    counters = {"n_rows": 0, "n_kept": 0, "n_smf": 0}

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
        isq = header.index(colmap["smf_q"]) if colmap.get("smf_q") is not None else -1
        isa = header.index(colmap["smf_a"]) if colmap.get("smf_a") is not None else -1
        need = max(iq, ia, ie, ip)
        kept_here = 0
        for row in rdr:
            counters["n_rows"] += 1
            if (counters["n_rows"] % 1000000) == 0:
                _log("PARSE... %d rows scanned, %d kept (|eps|>%.2f & p<%.2f) %d smf"
                     % (counters["n_rows"], counters["n_kept"], EPS_FILTER, P_MAX, counters["n_smf"]))
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
            # accumulate per-gene single-mutant fitness (map query SMF -> query ORF, array SMF -> array ORF)
            if isq >= 0 and isq < len(row):
                sq = _finite_float(row[isq])
                if sq is not None:
                    g = per_gene_smf[oa]; g[0] += sq; g[1] += 1; counters["n_smf"] += 1
            if isa >= 0 and isa < len(row):
                sa = _finite_float(row[isa])
                if sa is not None:
                    g = per_gene_smf[ob]; g[0] += sa; g[1] += 1; counters["n_smf"] += 1
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

    return _finalize_pairs(per_pair, counters["n_rows"], counters["n_kept"], members_info, per_gene_smf=per_gene_smf)


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


def _finalize_pairs(per_pair, n_rows, n_kept, members_info, per_gene_smf=None):
    """Shared PATH-A finalizer: aggregate ORF-pair means -> dense subnetwork (top-frequency ORFs) -> cap MAX_PAIRS ->
    reindex tokens contiguous. Returns PATH 'A' (X,y,n_tok,smf_tok,...) or PATH 'B' (escalate). smf_tok[t] = mean
    single-mutant fitness of token t (NaN if no SMF observed; matrix format has none -> all NaN -> curated pocket empty)."""
    # SNR lever: require >= MIN_CELLS_PER_PAIR replicate measurements per ORF-pair (drop noisiest singletons) -> cleaner mean.
    pair_mean = {k: (s / c) for k, (s, c) in per_pair.items() if c >= MIN_CELLS_PER_PAIR}
    if not pair_mean:
        return {"path": "B", "reason": "no_pairs_after_replicate_filter_min_%d" % MIN_CELLS_PER_PAIR,
                "n_rows": n_rows, "n_kept": n_kept, "members": members_info}
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
    # per-token mean single-mutant fitness (aligned to token index; NaN where unobserved)
    pgs = per_gene_smf or {}
    smf_tok = np.full(len(toks), np.nan, dtype=np.float64)
    n_smf_tok = 0
    for o, i in tokid.items():
        rec = pgs.get(o)
        if rec is not None and rec[1] > 0:
            smf_tok[i] = rec[0] / rec[1]; n_smf_tok += 1
    return {"path": "A", "X": X, "y": y, "n_tok": len(toks), "n_pairs": len(pairs), "n_rows": n_rows,
            "n_kept": n_kept, "members": members_info, "top_orf_kept": len(top),
            "smf_tok": smf_tok, "n_smf_tok": int(n_smf_tok),
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
# NEAR-ZERO-SINGLES CURATION + INTERACTION-VARIANCE-FRACTION (this cell's PRIMARY discriminator)
# ===========================================================================

def near_zero_singles_mask(X, smf_tok):
    """Pairs where BOTH constituent genes have mean single-mutant fitness within the WT band [SMF_WT_LO, SMF_WT_HI]
    (single-mutant fitness DEFECT ~0 by DIRECT measurement). Genes with no observed SMF (NaN) are excluded (conservative)."""
    a = smf_tok[X[:, 0]]; b = smf_tok[X[:, 1]]
    fin = np.isfinite(a) & np.isfinite(b)
    ok = (a >= SMF_WT_LO) & (a <= SMF_WT_HI) & (b >= SMF_WT_LO) & (b <= SMF_WT_HI)
    return ok & fin


def oof_additive_residual(X, y, n_tok, seed, k=IVF_KFOLD, l2=IVF_RIDGE_L2):
    """Out-of-fold per-gene-main-effects (ridge) residual for EVERY pair on the FULL subnetwork. ONE shared model -> IVF on any
    subset differs ONLY by which pairs are scored (no subset-sparsity confound). Deterministic strided folds (no hash())."""
    n = X.shape[0]
    rng = np.random.default_rng(seed * 99529 + 7)
    perm = rng.permutation(n)
    resid = np.full(n, np.nan, dtype=np.float64)
    for f in range(k):
        te = np.sort(perm[f::k])
        tr = np.sort(np.concatenate([perm[j::k] for j in range(k) if j != f]))
        if tr.size < 2 or te.size == 0:
            continue
        pred = arm_add_ridge(X[tr], y[tr].astype(np.float64), X[te], n_tok, l2=l2)
        resid[te] = y[te].astype(np.float64) - pred
    return resid


def ivf_of(resid, y, mask):
    """Interaction-variance-fraction on a subset = Var(additive-residual) / Var(y). Returns (ivf, n). >0.5 = majority of the
    subset's variance is irreducibly pairwise (not captured by generalizable per-gene main effects)."""
    m = np.asarray(mask, dtype=bool) & np.isfinite(resid)
    nm = int(m.sum())
    if nm < 8:
        return float("nan"), nm
    vy = float(np.var(y[m]))
    if vy <= 1e-12:
        return float("nan"), nm
    return float(np.var(resid[m]) / vy), nm


def matched_random_mask(n, n_target, seed):
    """Size-matched random draw of n_target pairs from ALL n pairs (the matched-random IVF baseline)."""
    rng = np.random.default_rng(seed * 100193 + 3)
    n_target = int(min(max(n_target, 0), n))
    idx = rng.choice(np.arange(n), size=n_target, replace=False) if n_target > 0 else np.array([], dtype=np.int64)
    m = np.zeros(n, dtype=bool)
    m[idx] = True
    return m


def build_arena_from_mask(X, y, mask):
    """Reindex a boolean-masked pair subset to a contiguous-token arena (X_r, y_r, n_tok_r) for the transfer proof."""
    Xs = X[mask]; ys = y[mask].astype(np.float64)
    toks = sorted(set(int(t) for t in Xs.reshape(-1).tolist()))
    remap = {t: i for i, t in enumerate(toks)}
    if Xs.shape[0] == 0:
        return np.zeros((0, 2), dtype=np.int64), ys, 0
    Xr = np.array([[remap[int(r[0])], remap[int(r[1])]] for r in Xs], dtype=np.int64)
    Xr = np.stack([Xr.min(axis=1), Xr.max(axis=1)], axis=1)
    return Xr, ys, len(toks)


def _plant_ivf_arena(seed=7, n_tok=20, n_pairs=1400):
    """Planted arena for the IVF-discriminator self-test: HALF the pairs carry a PURE symmetric 2-way interaction (no per-gene
    main effect -> high additive-residual -> high IVF); the other HALF carry a PURE per-gene ADDITIVE structure (captured by
    main effects -> ~0 residual -> low IVF). Returns (X, y, is_interaction_mask). IVF(interaction) must be >> IVF(additive)."""
    rng = np.random.default_rng(seed)
    a = rng.integers(0, n_tok, size=n_pairs); b = rng.integers(0, n_tok, size=n_pairs)
    keep = a != b
    a, b = a[keep], b[keep]
    X = np.stack([np.minimum(a, b), np.maximum(a, b)], axis=1).astype(np.int64)
    n = X.shape[0]
    tab = rng.normal(0.0, 1.0, size=(n_tok, n_tok)); tab = 0.5 * (tab + tab.T)  # symmetric 2-way interaction (no main effect)
    w = rng.normal(0.0, 1.0, size=n_tok)                                        # pure per-gene main effect
    is_int = (np.arange(n) % 2 == 0)
    y = np.where(is_int,
                 np.array([tab[int(X[i, 0]), int(X[i, 1])] for i in range(n)], dtype=np.float64),
                 np.array([w[int(X[i, 0])] + w[int(X[i, 1])] for i in range(n)], dtype=np.float64))
    y = y + 0.03 * rng.normal(0.0, 1.0, size=n)
    return X, y, is_int


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
    elif mode == "noise":
        # UNREADABLE arena: target is pure noise INDEPENDENT of X -> no structured readout can beat MEAN -> readability FAILS.
        return X, rng.normal(0.0, 1.0, size=n).astype(np.float64)
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


def _readable_rel_of(m_mae_fn, stratum, sub):
    """SIGNAL-READABILITY certificate: best structured readout (strong additive OR SYM) vs MEAN on (stratum, sub).
    max() is the "or oracle-ish readable-signal proxy" the VET permitted -- robust to a pure-interaction target additive
    alone would miss. >= READABILITY_REL certifies a READABLE target exists (target not noise-dominated)."""
    mean_mae = m_mae_fn(MEAN)
    add_rel = _rel(mean_mae, m_mae_fn("STRONG_ADD"))
    sym_rel = _rel(mean_mae, m_mae_fn(SYM))
    cands = [v for v in (add_rel, sym_rel) if v == v]
    return (max(cands) if cands else float("nan")), add_rel, sym_rel


def _readable_rel_arena(mode, seeds=(7, 13, 17), n_tok=8):
    """Readability certificate on a planted arena (interaction/additive = readable ; noise = unreadable). Uses ('all','full')
    averaged over seeds -- validates the gate FIRES on readable structure and REJECTS pure noise."""
    X, y = _plant_reg(600, {"interaction": 7, "additive": 11, "noise": 23}[mode], mode, n_tok)
    rs = [score(X, y, CLEAN, sd, n_tok) for sd in seeds]

    def _mm(arm):
        vals = [r["strata"]["all"]["full"][arm] for r in rs]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    rel, add_rel, sym_rel = _readable_rel_of(_mm, "all", "full")
    return rel, add_rel, sym_rel


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
                bands=dict(SMF_WT_LO=SMF_WT_LO, SMF_WT_HI=SMF_WT_HI, MIN_CURATED=MIN_CURATED,
                           IVF_RATIO_HP=IVF_RATIO_HP, IVF_CURATED_FLOOR=IVF_CURATED_FLOOR,
                           IVF_RATIO_INDISTINCT=IVF_RATIO_INDISTINCT, HP_REL_CURATED=HP_REL_CURATED,
                           MIN_NOVEL_CURATED_N=MIN_NOVEL_CURATED_N, READABILITY_REL=READABILITY_REL, REFUTE_REL=REFUTE_REL,
                           MUSTFAIL_REL_TOL=MUSTFAIL_REL_TOL, POS_CTRL_REL=POS_CTRL_REL, NEG_CTRL_REL=NEG_CTRL_REL,
                           EPS_FILTER=EPS_FILTER, P_MAX=P_MAX, MIN_CELLS_PER_PAIR=MIN_CELLS_PER_PAIR,
                           TOP_ORF=TOP_ORF, MAX_PAIRS=MAX_PAIRS, MIN_PAIRS=MIN_PAIRS,
                           IVF_KFOLD=IVF_KFOLD, IVF_RIDGE_L2=IVF_RIDGE_L2, HI_Z=HI_Z))

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

    # ---------- PATH A: SUBSET-CURATED near-zero-singles IVF discriminator + curated transfer proof ----------
    X, y, n_tok = data["X"], data["y"], data["n_tok"]
    smf_tok = data.get("smf_tok")
    n_smf_tok = int(data.get("n_smf_tok", 0))

    # SMF columns are REQUIRED for the near-zero-singles selector. Matrix format / SMF-absent -> escalate (cannot curate).
    if smf_tok is None or n_smf_tok == 0:
        msg = ("ESCALATE_NEED_PAIRWISE_FOR_SMF || the acquired Costanzo file (kind=%s) carries no single-mutant-fitness "
               "columns, so the near-zero-singles curation cannot be computed. HAND-OFF: re-run once the 521MB PAIRWISE zip "
               "is reachable (SMF columns 'Query single mutant fitness (SMF)' + 'Array SMF' are pairwise-only). "
               "pos_ctrl_rel=%s neg_ctrl_rel=%s" % (kind, _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ESCALATE_NEED_PAIRWISE_FOR_SMF", verdict_msg=msg, summary=msg[:200], escalate=True,
                    path="A", kind=kind, n_pairs=int(X.shape[0]), n_tok=int(n_tok), n_smf_tok=n_smf_tok)
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    # curated near-zero-singles pocket (both genes near-WT SMF) among the significant pairs
    cur_mask = near_zero_singles_mask(X, smf_tok)
    n_cur = int(cur_mask.sum())
    n_pairs = int(X.shape[0])
    _log("PATH A: n_pairs=%d n_tok=%d n_smf_tok=%d | NEAR-ZERO-SINGLES curated=%d (SMF in [%.2f,%.2f]) seeds=%d"
         % (n_pairs, n_tok, n_smf_tok, n_cur, SMF_WT_LO, SMF_WT_HI, len(seeds)))

    # PRIMARY discriminator: interaction-variance-fraction (shared out-of-fold additive model on the FULL subnetwork).
    ivf_cur_l, ivf_rand_l, ivf_all_l = [], [], []
    allmask = np.ones(n_pairs, dtype=bool)
    for si, sd in enumerate(seeds):
        resid = oof_additive_residual(X, y, n_tok, sd)
        ic, _nc = ivf_of(resid, y, cur_mask)
        rmask = matched_random_mask(n_pairs, n_cur, sd)
        ir, _nr = ivf_of(resid, y, rmask)
        ia, _na = ivf_of(resid, y, allmask)
        ivf_cur_l.append(ic); ivf_rand_l.append(ir); ivf_all_l.append(ia)
        _log("  IVF seed %d/%d curated=%s random=%s all=%s (elapsed=%.1fs)"
             % (si + 1, len(seeds), _fmt(ic), _fmt(ir), _fmt(ia), time.perf_counter() - t0))

    def _nanmean(vals):
        v = [x for x in vals if x == x]
        return float(np.mean(v)) if v else float("nan")

    ivf_curated = _nanmean(ivf_cur_l)
    ivf_random = _nanmean(ivf_rand_l)
    ivf_all = _nanmean(ivf_all_l)
    ivf_ratio = (ivf_curated / ivf_random) if (ivf_random == ivf_random and ivf_random > 1e-9
                                               and ivf_curated == ivf_curated) else float("nan")
    ivf_enriched = bool(ivf_ratio == ivf_ratio and ivf_ratio >= IVF_RATIO_HP
                        and ivf_curated == ivf_curated and ivf_curated >= IVF_CURATED_FLOOR)

    ivf_block = dict(ivf_curated=round(ivf_curated, 5) if ivf_curated == ivf_curated else None,
                     ivf_matched_random=round(ivf_random, 5) if ivf_random == ivf_random else None,
                     ivf_all=round(ivf_all, 5) if ivf_all == ivf_all else None,
                     ivf_ratio_curated_over_random=round(ivf_ratio, 4) if ivf_ratio == ivf_ratio else None,
                     ivf_enriched=ivf_enriched, IVF_RATIO_HP=IVF_RATIO_HP, IVF_CURATED_FLOOR=IVF_CURATED_FLOOR,
                     per_seed_curated=[round(v, 5) if v == v else None for v in ivf_cur_l],
                     per_seed_random=[round(v, 5) if v == v else None for v in ivf_rand_l])

    # HARD-FAIL / underpowered: fewer than MIN_CURATED clean near-zero-singles pairs -> escalate (drill's ~50 floor).
    if n_cur < MIN_CURATED:
        msg = ("HARD_FAIL_UNDERPOWERED_CURATED_N_ESCALATE_ENCAS12A || only %d clean near-zero-singles pairs "
               "(both SMF in [%.2f,%.2f]) < MIN_CURATED=%d in this Costanzo slice -- insufficient N to test the "
               "measurement-hiding hypothesis at power. IVF(curated=%s vs matched-random=%s ratio=%s) reported but "
               "UNDERPOWERED. HAND-OFF: higher-N fallback = enCas12a paralog-buffering compendium (Dede et al., "
               "PMC7558751) OR the Benchmarking-GI-Scores harmonized compendium, same near-zero-singles logic; OR raise "
               "MAX_PAIRS / widen the SMF band. pos_ctrl_rel=%s neg_ctrl_rel=%s (machinery %s)."
               % (n_cur, SMF_WT_LO, SMF_WT_HI, MIN_CURATED, _fmt(ivf_curated), _fmt(ivf_random), _fmt(ivf_ratio),
                  _fmt(pos_rel), _fmt(neg_rel), "VALID" if (pos_ok and neg_ok) else "CHECK"))
        base.update(verdict="HARD_FAIL_UNDERPOWERED_CURATED_N_ESCALATE_ENCAS12A", verdict_msg=msg, summary=msg[:200],
                    escalate=True, path="A", n_pairs=n_pairs, n_tok=int(n_tok), n_curated=n_cur,
                    n_smf_tok=n_smf_tok, ivf=ivf_block,
                    n_rows_scanned=int(data.get("n_rows", 0)), n_kept=int(data.get("n_kept", 0)),
                    cells_per_pair_mean=round(float(data.get("cells_per_pair_mean", 0.0)), 3))
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    # SECONDARY: transfer proof + readability + must-fails on the CURATED near-zero-singles arena.
    Xc, yc, n_tok_c = build_arena_from_mask(X, y, cur_mask)
    cc, cs = _robust_center_scale(yc)
    perc = {reg: [] for reg in REGIMES}
    for si, sd in enumerate(seeds):
        for reg in REGIMES:
            perc[reg].append(score(Xc, yc, reg, sd, n_tok_c, hi_center=cc, hi_scale=cs, hi_z=HI_Z))
        _log("  curated-arena seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def mc(reg, stratum, sub, arm):
        vals = [ps["strata"][stratum][sub][arm] for ps in perc[reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    def mc_n(reg, stratum, sub):
        return float(np.mean([ps["strata"][stratum][sub]["n"] for ps in perc[reg]]))

    # transfer: SYM vs strong-additive on NOVEL curated pairs (the honest stratum; whole pocket is high-interaction)
    transfer_rel = _rel(mc(CLEAN, "novel", "full", "STRONG_ADD"), mc(CLEAN, "novel", "full", SYM))
    seen_rel = _rel(mc(CLEAN, "seen", "full", "STRONG_ADD"), mc(CLEAN, "seen", "full", SYM))
    role_rel = _rel(mc(CLEAN, "seen", "full", "STRONG_ADD"), mc(CLEAN, "seen", "full", ROLE))
    novel_cur_n = mc_n(CLEAN, "novel", "full")

    # readability gate on the curated pocket (all==novel on real data since each pair appears once)
    readable_rel, read_add_rel, read_sym_rel = _readable_rel_of(
        lambda arm: mc(CLEAN, "all", "full", arm), "all", "full")
    readable_ok = bool(readable_rel == readable_rel and readable_rel >= READABILITY_REL)

    shuf_rel = _rel(mc(SHUFFLE, "all", "full", MEAN), mc(SHUFFLE, "all", "full", SYM))
    arb_rel = _rel(mc(ARBITRARY, "novel", "full", MEAN), mc(ARBITRARY, "novel", "full", SYM))
    orc_mae = mc(CLEAN, "all", "full", ORC)
    leak_ok = all(ps["leak_ok"] for reg in REGIMES for ps in perc[reg])

    mustfails_ok = bool((not (shuf_rel == shuf_rel) or shuf_rel <= MUSTFAIL_REL_TOL)
                        and (not (arb_rel == arb_rel) or arb_rel <= MUSTFAIL_REL_TOL))
    oracle_ok = bool(orc_mae == orc_mae and orc_mae <= 1e-6)
    power_ok = bool(novel_cur_n >= MIN_NOVEL_CURATED_N)
    transfer_pass = bool(transfer_rel == transfer_rel and transfer_rel >= HP_REL_CURATED)

    hard_pass = bool(pos_ok and neg_ok and oracle_ok and mustfails_ok and leak_ok
                     and readable_ok and power_ok and ivf_enriched and transfer_pass)
    rarity_refute = bool(pos_ok and neg_ok and oracle_ok and mustfails_ok and leak_ok and readable_ok and power_ok
                         and ivf_ratio == ivf_ratio and ivf_ratio <= IVF_RATIO_INDISTINCT
                         and transfer_rel == transfer_rel and transfer_rel <= REFUTE_REL)

    if not (pos_ok and neg_ok):
        verdict = "INCONCLUSIVE_CONTROL_GATE_INVALID"
    elif not oracle_ok:
        verdict = "INCONCLUSIVE_ORACLE_MALFORMED"
    elif not mustfails_ok:
        verdict = "INCONCLUSIVE_MUSTFAIL_LEAK"
    elif not readable_ok:
        verdict = "UNREADABLE_ESCALATE_NO_READABLE_NONADDITIVE_TARGET"
    elif not power_ok:
        verdict = "MIDDLE_BAND_LOW_POWER_NOVEL_CURATED"
    elif hard_pass:
        verdict = "HARD_PASS_CURATED_NEARZERO_POCKET_NONADDITIVE_AND_TRANSFERS"
    elif rarity_refute:
        verdict = "REFUTE_GENUINE_RARITY_EVEN_IN_CURATED_NEARZERO_POCKET"
    else:
        verdict = "MIDDLE_BAND"
        if ivf_enriched and not transfer_pass:
            verdict += "_IVF_ENRICHED_BUT_TRANSFER_WEAK"
        elif transfer_pass and not ivf_enriched:
            verdict += "_TRANSFER_OK_BUT_IVF_NOT_ENRICHED"

    escalate_tail = ""
    if verdict.startswith("UNREADABLE_ESCALATE"):
        escalate_tail = (" || HAND-OFF: curated near-zero-singles pocket target noise-dominated (readable_rel=%s < %.2f); "
                         "DATASET-SNR null, NOT a thesis result. ESCALATE to a higher-SNR non-additive dataset (enCas12a "
                         "paralog-buffering PMC7558751 / DrugComb synergy)." % (_fmt(readable_rel), READABILITY_REL))
    msg = ("%s || CURATED n=%d/%d near-zero-singles (SMF in [%.2f,%.2f]) | "
           "IVF curated=%s vs matched-random=%s ratio=%s (>=%.1f enriched=%s; ivf_all=%s floor=%.2f) | "
           "TRANSFER novel_rel_MAE=%s(>=%.2f pass=%s) seen_rel=%s role_rel=%s SYM/SADD=%s/%s | "
           "READABLE_rel=%s(>=%.2f ok=%s add=%s sym=%s) | POS_ctrl=%s(>=%.2f %s) NEG_ctrl=%s(<=%.2f %s) | "
           "MUSTFAIL shuf=%s arb=%s(<=%.2f) oracle=%s leak=%s | novel_cur_n=%.1f power=%s"
           % (verdict, n_cur, n_pairs, SMF_WT_LO, SMF_WT_HI,
              _fmt(ivf_curated), _fmt(ivf_random), _fmt(ivf_ratio), IVF_RATIO_HP, ivf_enriched, _fmt(ivf_all),
              IVF_CURATED_FLOOR, _fmt(transfer_rel), HP_REL_CURATED, transfer_pass, _fmt(seen_rel), _fmt(role_rel),
              _fmt(mc(CLEAN, "novel", "full", SYM)), _fmt(mc(CLEAN, "novel", "full", "STRONG_ADD")),
              _fmt(readable_rel), READABILITY_REL, readable_ok, _fmt(read_add_rel), _fmt(read_sym_rel),
              _fmt(pos_rel), POS_CTRL_REL, pos_ok, _fmt(neg_rel), NEG_CTRL_REL, neg_ok,
              _fmt(shuf_rel), _fmt(arb_rel), MUSTFAIL_REL_TOL, _fmt(orc_mae), leak_ok, novel_cur_n, power_ok) + escalate_tail)

    base.update(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], path="A", escalate=verdict.startswith(("UNREADABLE", "REFUTE")),
        n_pairs=n_pairs, n_tok=int(n_tok), n_curated=n_cur, n_tok_curated=int(n_tok_c), n_smf_tok=n_smf_tok,
        curated_frac=round(n_cur / float(n_pairs), 5) if n_pairs else None,
        n_rows_scanned=int(data.get("n_rows", 0)), n_kept=int(data.get("n_kept", 0)),
        cells_per_pair_mean=round(float(data.get("cells_per_pair_mean", 0.0)), 3), members=data.get("members"),
        ivf=ivf_block,
        transfer=dict(
            novel_rel=round(transfer_rel, 5) if transfer_rel == transfer_rel else None,
            seen_rel=round(seen_rel, 5) if seen_rel == seen_rel else None,
            role_rel=round(role_rel, 5) if role_rel == role_rel else None,
            transfer_pass=transfer_pass, HP_REL_CURATED=HP_REL_CURATED,
            sym_novel_mae=round(mc(CLEAN, "novel", "full", SYM), 5),
            strong_add_novel_mae=round(mc(CLEAN, "novel", "full", "STRONG_ADD"), 5),
            mean_novel_mae=round(mc(CLEAN, "novel", "full", MEAN), 5),
            memo_novel_mae=round(mc(CLEAN, "novel", "full", MEMO), 5),
            novel_cur_n=round(novel_cur_n, 2), seen_cur_n=round(mc_n(CLEAN, "seen", "full"), 2)),
        readability=dict(
            readable_rel=round(readable_rel, 5) if readable_rel == readable_rel else None,
            read_add_vs_mean=round(read_add_rel, 5) if read_add_rel == read_add_rel else None,
            read_sym_vs_mean=round(read_sym_rel, 5) if read_sym_rel == read_sym_rel else None,
            readable_ok=readable_ok, READABILITY_REL=READABILITY_REL,
            mean_mae=round(mc(CLEAN, "all", "full", MEAN), 5),
            strong_add_mae=round(mc(CLEAN, "all", "full", "STRONG_ADD"), 5),
            sym_mae=round(mc(CLEAN, "all", "full", SYM), 5)),
        gates=dict(readable_ok=readable_ok, ivf_enriched=ivf_enriched, transfer_pass=transfer_pass,
                   pos_ok=pos_ok, neg_ok=neg_ok, mustfails_ok=mustfails_ok, oracle_ok=oracle_ok, leak_ok=leak_ok,
                   power_ok=power_ok, hard_pass=hard_pass, rarity_refute=rarity_refute),
        mustfail=dict(shuf_rel_sym_vs_mean=round(shuf_rel, 5) if shuf_rel == shuf_rel else None,
                      arb_rel_sym_vs_mean=round(arb_rel, 5) if arb_rel == arb_rel else None,
                      oracle_mae=round(orc_mae, 8)),
        per_seed_regime={reg: [dict(strata=perc[reg][i]["strata"], leak_ok=perc[reg][i]["leak_ok"],
                                    n_seen=perc[reg][i]["n_seen"], n_novel=perc[reg][i]["n_novel"])
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

def _synth_smf_of(k):
    """Deterministic per-gene single-mutant fitness for the self-test: EVEN-index ORFs are near-WT (0.98, near-zero-single),
    ODD-index ORFs have a large single-mutant defect (0.62). -> near-zero-singles pocket = pairs of two even-index ORFs."""
    return 0.98 if (k % 2 == 0) else 0.62


def _make_synth_costanzo_zip(path, n_pairs=60, n_strains=3, n_orfs=12):
    """Write a tiny synthetic Costanzo-shaped pairwise TSV (zip-of-txt, matching the real release incl. the single-mutant
    fitness columns) -> exercises the REAL parser/detector PATH-A code end-to-end (filter + ORF extraction + per-gene SMF
    accumulation + subnetwork + reindex). Planted symmetric interaction; all |epsilon| > EPS_FILTER and p < P_MAX so every
    pair survives the filter. Per-gene SMF planted via _synth_smf_of (even ORFs near-WT -> near-zero-singles pocket)."""
    rng = np.random.default_rng(101)
    header = ["Query Strain ID", "Query allele name", "Array Strain ID", "Array allele name", "Arm",
              "Genetic interaction score (eps)", "P-value", "Query single mutant fitness (SMF)", "Array SMF",
              "Double mutant fitness", "Double mutant fitness std"]
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
            eps = sgn * (EPS_FILTER + 0.05 + 0.3 * abs(float(tab[i, j])))  # |eps| > EPS_FILTER regardless of the tuned filter
            lines.append("\t".join([
                "%s_tsq%d" % (orfs[i], s), "%s-1" % orfs[i].lower(),
                "%s_dma%d" % (orfs[j], s), "%s-2" % orfs[j].lower(), "chrI",
                "%.4f" % eps, "0.0100", "%.4f" % _synth_smf_of(i), "%.4f" % _synth_smf_of(j), "0.85", "0.02"]))
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
                cells.append("%.4f" % (sgn * (EPS_FILTER + 0.05 + 0.3 * abs(float(tab[i, j])))))  # |eps| > EPS_FILTER
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

    # (3c) NEAR-ZERO-SINGLES selector: per-gene SMF parsed (even ORFs near-WT 0.98 / odd 0.62) -> curated pocket = pairs of
    # two even-index tokens (token index == ORF index here: 12 ORFs sort contiguously). Validates the selector picks EXACTLY
    # the near-WT-both pairs and that per-gene SMF accumulation ran (n_smf_tok == n_orfs).
    smf_tok_st = sd.get("smf_tok")
    n_smf_tok_st = int(sd.get("n_smf_tok", 0))
    Xst = sd.get("X")
    if smf_tok_st is not None and Xst is not None:
        curated_st = near_zero_singles_mask(Xst, smf_tok_st)
        both_even = np.array([(int(Xst[r, 0]) % 2 == 0) and (int(Xst[r, 1]) % 2 == 0) for r in range(Xst.shape[0])],
                             dtype=bool)
        nzs_ok = bool(n_smf_tok_st == 12 and int(curated_st.sum()) > 0
                      and np.array_equal(curated_st, both_even))
        details.update(nzs_n_smf_tok=n_smf_tok_st, nzs_curated_n=int(curated_st.sum()),
                       nzs_expected_n=int(both_even.sum()), nzs_ok=nzs_ok)
    else:
        nzs_ok = False
        details.update(nzs_ok=False, nzs_n_smf_tok=n_smf_tok_st)

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

    # (5b) SIGNAL-READABILITY GATE (VET a57067090 revival criterion) must DISCRIMINATE readable structure from pure noise:
    #   FIRES on a readable (additive) arena AND on a readable (interaction) arena; REJECTS a pure-noise (unreadable) arena.
    read_add, radd_a, rsym_a = _readable_rel_arena("additive")     # readable -> gate fires
    read_int, radd_i, rsym_i = _readable_rel_arena("interaction")  # readable -> gate fires
    read_noise, radd_n, rsym_n = _readable_rel_arena("noise")      # unreadable -> gate rejects
    readability_fires_on_readable = bool(read_add == read_add and read_add >= READABILITY_REL
                                         and read_int == read_int and read_int >= READABILITY_REL)
    readability_rejects_noise = bool(not (read_noise == read_noise) or read_noise < READABILITY_REL)
    details.update(dict(readable_rel_additive=round(read_add, 4), readable_rel_interaction=round(read_int, 4),
                        readable_rel_noise=round(read_noise, 4), read_add_component_noise=round(radd_n, 4),
                        read_sym_component_noise=round(rsym_n, 4)))

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

    # (7b) IVF DISCRIMINATOR (PRIMARY statistic) FIRES: planted arena where HALF the pairs carry pure symmetric interaction
    # (high additive-residual -> high IVF) and HALF carry pure per-gene additive (captured -> low IVF). The shared out-of-fold
    # additive model must leave the interaction subset >> IVF_RATIO_HP more unexplained than the additive subset.
    Xiv, yiv, is_int = _plant_ivf_arena(seed=7)
    resid_iv = oof_additive_residual(Xiv, yiv, int(Xiv.max()) + 1, 7)
    ivf_int, _niv = ivf_of(resid_iv, yiv, is_int)
    ivf_add, _nav = ivf_of(resid_iv, yiv, ~is_int)
    ivf_ratio_test = (ivf_int / ivf_add) if (ivf_add == ivf_add and ivf_add > 1e-9) else float("inf")
    ivf_fires = bool(ivf_int == ivf_int and ivf_add == ivf_add and ivf_ratio_test >= IVF_RATIO_HP
                     and ivf_int >= IVF_CURATED_FLOOR)
    details.update(ivf_interaction=round(ivf_int, 4), ivf_additive=round(ivf_add, 4),
                   ivf_ratio_test=round(ivf_ratio_test, 3) if math.isfinite(ivf_ratio_test) else None,
                   ivf_fires=ivf_fires)

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hadamard_equals_complex_bind": prod_is_bind,
        "real_parser_reconstructs_pairs": parser_ok,
        "near_zero_singles_selector_picks_curated_pocket": nzs_ok,
        "ivf_discriminator_fires_on_planted_arena": ivf_fires,
        "matrix_fallback_parser_reconstructs_pairs": matrix_ok,
        "nonpair_header_routes_to_escalate": nonpair_routes_B,
        "pos_ctrl_SYM_beats_strong_additive": (pos_rel == pos_rel and pos_rel >= POS_CTRL_REL),
        "neg_ctrl_SYM_not_beating_additive": (neg_rel == neg_rel and neg_rel <= NEG_CTRL_REL),
        "readability_gate_fires_on_readable_arena": readability_fires_on_readable,
        "readability_gate_rejects_noise_arena": readability_rejects_noise,
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
