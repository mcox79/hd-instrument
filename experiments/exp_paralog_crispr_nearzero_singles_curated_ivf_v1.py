"""PARALOG_CRISPR_NEARZERO_SINGLES_CURATED_IVF (v1): HIGH-SNR replacement for the exhausted Costanzo per-pair epsilon.

The RELOCATED thesis test. The three prior real-data negatives (chem MMP / LLM-narrated epistasis / genome-wide Costanzo
epsilon) and the committed Costanzo near-zero-singles curated cell (exp_costanzo_nearzero_singles_curated_ivf_v1, commit
613fa311a) all failed for the SAME root cause: bulk SGA epsilon is measured at ~1.8 cells/pair -- NOISE-DOMINATED in every
pocket (readable_rel ~0.0029). FIX = a HIGHER-SNR MEASUREMENT CLASS, not a different bulk source: a purpose-built combinatorial
paralog-CRISPR synthetic-lethality screen where the AND-gate interaction is measured with high replication (Dede et al. 2020
enCas12a, replicate Pearson r=0.87-0.94: 18 clones/pair x 3 reps x 3 cell lines). A READABLE non-additive target finally exists.

SCHEMA BRANCH (resolved at authoring; the ONE thing the scout flagged). The STRONG-additive baseline REQUIRES the RAW
constituents SMF-A, SMF-B (single-mutant fitness) + DMF (double-mutant fitness): the additive predicts DMF from per-gene main
effects and the INTERACTION = DMF beyond additive-of-singles. A GI-score-only target (zdLFC) makes "SYM beats additive"
VACUOUS -- a GI score is already the interaction residual with main effects removed. Local column-open (2026-07-15):
  - Dede Additional File 3 (MOESM3, per-pair zdLFC x 3 cell lines) = SCORES-ONLY -> the vacuous trap; NOT used as target.
  - Dede Additional File 4 (MOESM4, RAW guide-pair read counts: GENE_CLONE|GENE|<cellline.T2rep.Ex>|plasmid.T0.Ex,
    GENE="geneA.pos:geneB.pos") = carries the raw constituents. TARGET = DMF computed from log2FC-vs-plasmid; SMF from the
    single-KO-vs-control constructs. This is the NON-VACUOUS DMF-target path. THIS is the branch taken.
  - Rank-1 (Benchmarking-GI-Scores harmonized compendium, private figshare /s/ link) DEPRIORITIZED: not programmatically
    resolvable this session AND its per-pair tables are MOESM3-class (scores-only) -> would need the SAME raw processing Dede's
    verified MOESM4 supplies directly. Documented schema-branch decision (see prereg). Higher-N escalation target if Dede is
    underpowered.

THE MECHANISM x DATA question (UNCHANGED): LEARN_SYM (shared per-token code + PRODUCT = substrate symmetric bind) reads a
SYMMETRIC 2-way interaction and GENERALIZES to NOVEL gene-pairs; a per-gene main-effects ADDITIVE (each gene's SMF) provably
loses the irreducible pairwise AND-gate term. Near-zero-singles paralog pairs are the CLEANEST real non-additivity: both
single KOs are ~neutral (main effect ~0 by DIRECT measurement) yet the double is lethal -> the additive escape-hatch
(Hill-Goddard-Visscher allele-frequency projection) structurally cannot apply (full knockouts, no segregating alleles).

PRIMARY DISCRIMINATING STATISTIC = interaction-variance-fraction IVF (per-pair additive-residual variance / total variance)
computed with ONE shared out-of-fold per-gene-main-effects model on the full pair network, evaluated SEPARATELY on (a) the
curated near-zero-singles subset and (b) a size-matched RANDOM subset. Shared-model design is confound-robust (identical
per-gene main-effect estimates; the RATIO isolates WHICH pairs). HARD_PASS requires IVF(curated) >= 3x IVF(matched-random)
AND IVF(curated) >= 0.30 AND the SUBSET transfer proof (LEARN_SYM vs capacity-matched STRONG categorical-additive) clears
>=30% relative-MAE reduction on NOVEL curated pairs, with the SIGNAL-READABILITY gate as a precondition.

Glass-box CPU, NO LLM at readout. All compute REMOTE (the cell downloads the Dede MOESM4/MOESM3 files at runtime; the remote
--self-test with planted arenas -- which fires the raw-count->SMF/DMF pipeline, the near-zero-singles selector, the IVF
discriminator, and the transfer/readability gates on synthetic MOESM4-format data -- is the network-independent gate).

REGRESSION ARMS (MAE lower=better), REUSED UNCHANGED from the validated Costanzo cell: LEARN_SYM (shared code + PRODUCT =
symmetric bind; WINNER hypothesis) ; LEARN_ADD (shared code + SUM) ; ADD_RIDGE (closed-form ridge on per-token COUNT design;
STRONG closed-form categorical additive) ; ADD_LSTSQ ; LEARN_ROLE (role-keyed product; ALGEBRA contrast) ; MEAN (train-mean =
regression frequency floor) ; MEMORIZE (per-pair mean; collapses to MEAN on NOVEL) ; ORACLE.
  strong_additive = min-MAE(LEARN_ADD, ADD_RIDGE, ADD_LSTSQ). rel(s,sub) = (STRONG_ADD_mae - SYM_mae)/STRONG_ADD_mae.
CURATION: per-gene SMF (single-KO log2FC); a gene is NEAR-ZERO-SINGLE if its mean SMF is within the NEUTRAL band (UNITS-ADAPTIVE
  -- log2FC: |SMF| <= 0.5 near-neutral ; WT-normalized fallback: SMF in [0.90,1.10]). CURATED pocket = double-mutant pairs where
  BOTH genes are near-zero-singles. MATCHED-RANDOM = a size-matched random draw from ALL pairs.
STRATA (transfer arena): seen / novel gene-pair (entity-level split) on the CURATED near-zero-singles arena; NOVEL is the honest
  stratum (each measured pair appears once -> the whole curated stratum is the transfer target).
REGIMES: CLEAN(real) ; ARBITRARY (random target per unique gene-pair; must-fail on NOVEL) ; SHUFFLE (target permutation;
  must-fail on ALL). FIXED GATE positive control = planted symmetric-interaction arena (SYM beats strong-additive; pos_rel
  ~0.908 validated); negative control = planted ADDITIVE arena (SYM must NOT beat additive; neg_rel ~-0.018 validated -> the
  gate is NOT saturation-vacuous).

SIGNAL-READABILITY GATE (VET a57067090 revival criterion -- precondition): BEFORE the SYM-vs-additive transfer test can be
interpreted, a readable target must be CERTIFIED to exist on the curated pocket -- readable_rel = max(strong_additive, SYM) vs
MEAN >= READABILITY_REL=0.15. Gate FAILS -> UNREADABLE_ESCALATE (a DATASET-SNR null, NOT a thesis result). The high-SNR Dede
replication (r=0.87-0.94, reps pooled) is the SNR lever that Costanzo's ~1.8 cells/pair lacked.

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_paralog_crispr_nearzero_singles_curated_ivf.md):
  HARD_PASS (curated pocket is non-additive AND transfers): IVF(curated) >= IVF_RATIO_HP=3x IVF(matched-random) AND IVF(curated)
    >= IVF_CURATED_FLOOR=0.30 AND readability PASSES AND NOVEL curated rel_MAE (SYM vs strong-additive) >= HP_REL_CURATED=0.30
    AND positive-control passes (>=0.30) AND negative-control ok (<=0.10) AND must-fails fire AND oracle MAE~0 AND leak_ok AND
    novel_curated_n >= 8 AND n_curated >= MIN_CURATED=50.
  HARD_FAIL_UNDERPOWERED_CURATED_N: < MIN_CURATED=50 clean near-zero-singles pairs -> insufficient N (directional-only) ->
    ESCALATE to the Benchmarking-GI-Scores harmonized compendium (higher-N) or pool Dede+Parrish/pgPEN by hand.
  ESCALATE_NEED_RAW_CONSTITUENTS: acquired file has no raw SMF/DMF constituents (GI-scores-only, e.g. MOESM3) -> re-run on the
    raw-count file (MOESM4) or a per-pair table that retains SMF-A/SMF-B/DMF.
  UNREADABLE_ESCALATE: readability FAILS on the curated pocket -> DATASET-SNR null (not a thesis result) -> higher-SNR pocket.
  REFUTE_GENUINE_RARITY: readability PASSES but IVF(curated) within noise of matched-random (ratio <= 1.30) AND novel curated
    rel_MAE <= 0.05 -> genuine rarity dominates even in the best-available real high-SNR pocket (a deep foundation finding).
  MIDDLE_BAND: partial (IVF enriched but transfer weak, or transfer OK but IVF not enriched) / low-power novel curated.

Compute architecture: (b) sequential-CPU with justification -- arena is O(1e2-1e4) native gene-pairs x tiny (<=Nx32) Adam fits
  (ms each) + numpy solves; GPU yields no speedup on sub-ms matmuls; dominant cost = the (small ~1.5MB) MOESM4 download +
  two-pass CPM parse (cached after first run). torch thread-capped. Storage: no_storage / no_composition (single-hop readout).
  Determinism: FIXED int seeds + stable sorted-unique token ids + deterministic stride subsample; NO hash(), NO list(set())
  (PROT-023). ASCII-only; no bare except; except SystemExit before except Exception; atomic tmp+os.replace. Default invocation
  (no flag) = FULL run to completion. progress_logging: ACQUIRE + parse counters + per-seed done lines, all flush=True.
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; float-hash arms-differ on planted arena).
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: regression MAE floor is data-noise-defined (guide-count assay noise); no closed-form CRLB for the bilinear-readout
#     arm; the IVF-ratio>=3x + rel-MAE-reduction gate substitute for a capacity-feasibility cap.
# - baseline_in_band: STRONG additive MAE is measured (not saturated); planted pos/neg controls bound the gate.
# - discriminator survives scale: self-test fires (a) IVF(interaction subset) >> 3x IVF(additive subset) via the SHARED
#     out-of-fold model on a planted arena, AND (b) SYM>>additive on planted-interaction SEEN at plant scale (n=600).
# - HARD_PASS strictly above floor: IVF ratio>=3.0 AND IVF(curated)>=0.30 AND novel curated rel>=0.30 (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to LEARN_SYM vs strong_additive + the IVF ratio only; MEAN/MEMO/ORACLE/ROLE are contrast.
# - cardinality_ok: n_seeds x n_regimes on the curated arena + n_seeds IVF folds; verdict counts per_seed_regime lengths.
# - per-unit failure-class instrumentation: acquire/parse/SMF failures -> explicit ACQUIRE_FAILED / ESCALATE_NEED_RAW_
#     CONSTITUENTS / HARD_FAIL_UNDERPOWERED_CURATED_N verdicts (no silent continue).
# - calibration_check: adaptive_with_discriminator_gate (units-adaptive near-zero-singles band + the IVF-ratio>=3x-vs-matched-
#     random gate are the discriminator-still-fires verification; MIN_CURATED=50 is the insufficient-N guard; the SIGNAL-
#     READABILITY gate readable_rel>=0.15 certifies a READABLE target EXISTS before SYM-vs-additive is interpretable -- self-test
#     fires the IVF discriminator + readability on planted arenas and rejects a pure-noise/pure-additive arena).
# - all numbers in comments tagged CITED@ (drill/scout) / THEORETICAL@ / to-be-MEASURED@ (real-data pending remote run).
# - real_code_path: self-test builds a SYNTHETIC Dede MOESM4-format raw-count TSV (GENE_CLONE|GENE|endpoint...|plasmid.T0) WITH
#     control constructs, runs it through the REAL parse_dede_encas12a (CPM -> log2FC -> SMF/DMF -> control detection ->
#     subnetwork) + near_zero_singles_mask + oof_additive_residual/ivf_of + planted arenas through the REAL score()/arm code;
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

ANCHOR_NAME = "paralog_crispr_nearzero_singles_curated_ivf_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CACHE_DIR = os.path.join(_REPO, "data", "foundation_clusters", "dede2020_encas12a")

# ---- data source (Dede et al. 2020, Genome Biology 21:262; PMC7558751; DOI 10.1186/s13059-020-02173-2) ----
# CITED@ notes/research_dataset_scout_high_snr_conjunction_module1_replacement_2026-07-15.md + exp_dev web-verified 2026-07-15
# (the static-content.springer.com ESM URLs resolve publicly; MOESM3 = per-pair zdLFC scores-only; MOESM4 = raw guide-pair
# read counts with GENE_CLONE|GENE|<cellline.T2rep.Ex>|plasmid.T0.Ex, GENE="geneA.pos:geneB.pos"). MOESM4 carries the raw
# constituents (log2FC-vs-plasmid -> SMF/DMF) needed for the NON-VACUOUS DMF target; MOESM3 fetched only for cross-check.
_ESM = ("https://static-content.springer.com/esm/art%%3A10.1186%%2Fs13059-020-02173-2/MediaObjects/"
        "13059_2020_2173_MOESM%d_ESM.txt")
COUNTS_URLS = [("MOESM4_rawcounts_springer_https", _ESM % 4)]
ZDLFC_URLS = [("MOESM3_zdlfc_springer_https", _ESM % 3)]

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
HI_Z = 1.0                   # hi = |DMF - median| > HI_Z * robust_sigma (robust_sigma = 1.4826*MAD): large double-mutant effect
# ---- SIGNAL-READABILITY GATE (VET a57067090 revival criterion; the FIRST interpretability gate) ----
READABILITY_REL = 0.15       # readable_rel (best structured readout vs MEAN on the curated pocket) >= this else UNREADABLE
HP_REL_HI = 0.30             # novel_hi rel_MAE reduction (SYM vs strong additive) >= 0.30
REFUTE_REL = 0.05            # novel_hi rel_MAE <= 0.05 => collapses to additive-capturable => REFUTE (only if readable)
MUSTFAIL_REL_TOL = 0.08      # SHUFFLE(all)+ARBITRARY(novel) rel_sym_vs_mean ceiling

# ---- NEAR-ZERO-SINGLES CURATION (UNITS-ADAPTIVE; SMF = single-mutant fitness) ----
# CRISPR SMF is a log2 fold-change vs plasmid T0 (neutral ~0; essential single << 0): near-zero-single = |SMF| <= NZ_LFC.
# WT-normalized SMF (Costanzo-style, neutral ~1.0) fallback band [SMF_WT_LO, SMF_WT_HI]. Units auto-detected by median SMF.
NZ_LFC = 0.5                 # log2FC band: |mean SMF| <= 0.5 (single KO within ~1.4x of neutral fitness) = near-zero-single
SMF_WT_LO = 0.90             # WT-normalized fallback lower band (<=10% single-mutant fitness defect)
SMF_WT_HI = 1.10             # WT-normalized fallback upper band
MIN_CURATED = 50             # HARD-FAIL if < this many clean near-zero-singles pairs (drill's ~50 power floor) -> escalate

# ---- PRIMARY DISCRIMINATING STATISTIC: interaction-variance-fraction (IVF) ----
IVF_KFOLD = 5
IVF_RIDGE_L2 = 1.0
IVF_RATIO_HP = 3.0           # HARD_PASS: IVF(curated) >= 3x IVF(matched-random)
IVF_CURATED_FLOOR = 0.30     # AND IVF(curated) itself >= 0.30 absolute (>=30% of curated variance is irreducibly pairwise)
IVF_RATIO_INDISTINCT = 1.30  # REFUTE (genuine rarity): curated IVF within ~noise of random (ratio <= this) AND transfer weak
# ---- transfer proof on the curated pocket (SYM vs strong additive; NOVEL curated pairs = the honest stratum) ----
HP_REL_CURATED = 0.30        # NOVEL curated rel_MAE reduction (SYM vs strong additive) >= 0.30
MIN_NOVEL_CURATED_N = 8.0    # mean novel curated query rows for adequate transfer power
POS_CTRL_REL = 0.30          # planted-interaction SEEN rel_MAE (positive control must clear its own bar)
NEG_CTRL_REL = 0.10          # planted-additive SEEN rel_MAE ceiling (gate not saturation-vacuous)

# ---- raw-count -> fitness parse controls ----
MIN_PAIRS = 60               # PATH-A requires >= this many unique double-mutant gene-pairs; else escalate (Dede ~400 pairs)
TOP_ORF = 800                # subnetwork density cap (top-frequency genes): well-defined per-gene main effects
MAX_PAIRS = 12000            # cap native pair count
PSEUDO = 0.5                 # CPM pseudocount for log2FC
MIN_CTRL_REF = 3             # >= this many control:control (SAFE:SAFE) constructs to anchor the neutral log2FC reference
CTRL_DEGREE_FRAC = 0.30      # degree heuristic: a token paired with >= this fraction of distinct genes is a control guide
# explicit control-guide token set (uppercased gene symbol); the single-KO-vs-control constructs define SMF
CTRL_TOKENS = {"SAFE", "SAFEHARBOR", "NT", "NONTARGETING", "CONTROL", "CTRL", "NONE", "LUC", "LUCIFERASE",
               "LACZ", "GFP", "AAVS1", "CHR2", "NEG", "NEGATIVE", "INTERGENIC", "OLFR", "DUMMY", "EMPTY", "NA", "0", "-"}
CTRL_PREFIXES = ("SAFE", "CHR2", "CTRL", "CONTROL", "NONTARGET", "NON_TARGET", "OLFR", "INTERGENIC", "ONEHOT", "ONE_HOT")

SEEDS_FULL = (7, 13, 17, 23, 29, 31, 37, 41)
SEEDS_SMOKE = (7, 13, 17)

# self-test synthetic-fixture sizing: the neutral (near-zero-singles) genes are a deliberate MINORITY of the network so the
# curated pocket is a small fraction of all pairs. The e2e IVF discriminator (self-test 7c) scores curated-pocket IVF against
# a matched-RANDOM draw from ALL pairs; if the pocket is a large fraction, the random draw is polluted by interaction pairs and
# the ratio is capped at ~1/pocket_fraction (this is why a ~half-neutral fixture caps e2e_ratio near 2.6 while the BARE IVF
# self-test -- which compares against the PURE additive subset, not a random draw -- clears >6). A minority pocket keeps the
# matched-random baseline clean (as in real data, where near-zero-singles pairs are a curated minority) so the e2e ratio
# reflects the true enrichment. C(7,2)=21 curated pairs preserves the near-zero-singles selector self-test count.
SELFTEST_N_GENES = 45
SELFTEST_N_NEUTRAL = 7


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


def _try_download(dest, urls, errors, min_bytes=2000):
    """Cache-hit or download-first-of urls to dest. Returns (nbytes, used_url) or (0, None)."""
    if os.path.exists(dest) and os.path.getsize(dest) > min_bytes:
        nb = os.path.getsize(dest)
        _log("ACQUIRE cache-hit %s (%d bytes)" % (os.path.basename(dest), nb))
        return nb, "cache"
    for tag, url in urls:
        nb, err = _download_one(url, dest)
        if err is None and nb > min_bytes:
            _log("ACQUIRE downloaded via %s (%d bytes)" % (tag, nb))
            return nb, url
        errors[tag] = err or ("too_small:%d" % nb)
        _log("ACQUIRE candidate FAILED %s : %s" % (tag, errors[tag]))
    return 0, None


def acquire():
    """Download-if-absent the Dede 2020 enCas12a raw-count file (MOESM4; REQUIRED) + the zdLFC file (MOESM3; cross-check).
    Returns (counts_path or None, zdlfc_path or None, prov)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    errors = {}
    destC = os.path.join(CACHE_DIR, "dede2020_MOESM4_rawcounts.txt")
    nbC, uuC = _try_download(destC, COUNTS_URLS, errors)
    destZ = os.path.join(CACHE_DIR, "dede2020_MOESM3_zdlfc.txt")
    nbZ, uuZ = _try_download(destZ, ZDLFC_URLS, errors, min_bytes=1000)

    prov = dict(dataset="Dede2020_enCas12a_paralog_SL", paper="Dede et al. 2020, Genome Biology 21:262 (PMC7558751)",
                source="static-content.springer.com ESM (DOI 10.1186/s13059-020-02173-2)",
                counts_url_used=uuC, zdlfc_url_used=uuZ, urls_tried=dict(COUNTS_URLS + ZDLFC_URLS),
                retrieval_ts=datetime.now(timezone.utc).isoformat(),
                interaction_definition=("DMF = double-mutant fitness = mean log2FC (endpoint reads vs plasmid T0) of dual-gene "
                                        "constructs; SMF = single-mutant fitness = mean log2FC of single-KO-vs-control "
                                        "constructs; interaction = DMF beyond additive-of-SMFs. zdLFC (MOESM3) = z-normalized "
                                        "(observed dLFC minus expected-from-SMF-sum), cross-check only."),
                counts_bytes=int(nbC), zdlfc_bytes=int(nbZ), acquire_errors=errors,
                target="DMF (double-mutant fitness log2FC); NOT the zdLFC GI-score (that would make SYM-vs-additive vacuous)",
                slice_controls=dict(TOP_ORF=TOP_ORF, MAX_PAIRS=MAX_PAIRS, MIN_PAIRS=MIN_PAIRS))
    try:
        with open(os.path.join(CACHE_DIR, "provenance.json"), "w", encoding="utf-8") as f:
            json.dump(prov, f, indent=2)
    except OSError:
        pass
    counts_path = destC if (uuC is not None and nbC > 2000 and os.path.exists(destC)) else None
    zdlfc_path = destZ if (uuZ is not None and nbZ > 1000 and os.path.exists(destZ)) else None
    return counts_path, zdlfc_path, prov


# ===========================================================================
# PARSE: Dede MOESM4 raw guide-pair counts -> per-construct log2FC -> SMF (single-KO) + DMF (double) -> native pairs
# ===========================================================================

def _norm(s):
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")


def _finite_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _gene_sym(tok):
    """Gene symbol = the part of a guide token before the first '.' (strips the tie-breaking guide index, e.g.
    'AARS.1' -> 'AARS'; 'CDX4.2' -> 'CDX4'). Uppercased canonical token."""
    tok = str(tok).strip()
    return tok.split(".")[0].strip().upper()


def _split_gene_pair(g):
    """Parse a GENE cell 'geneA.pos:geneB.pos' -> (symA, symB). Separator auto: ':' (MOESM4), ';', '|', then '_' fallback."""
    g = str(g).strip()
    for sep in (":", ";", "|"):
        if sep in g:
            parts = g.split(sep)
            if len(parts) == 2:
                return _gene_sym(parts[0]), _gene_sym(parts[1])
    if g.count("_") == 1:
        a, b = g.split("_")
        return _gene_sym(a), _gene_sym(b)
    return None, None


def _read_rows(path):
    """Yield rows (list[str]) from a plain-text or zip-of-txt tab/comma-delimited file (auto-delimiter per member)."""
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
    except OSError:
        return []
    out = []

    def _slurp(name, textstream):
        data = textstream.read()
        delim = "\t" if data.count("\t") >= data.count(",") else ","
        for row in csv.reader(io.StringIO(data), delimiter=delim):
            out.append(row)

    if magic[:2] == b"PK":
        try:
            zf = zipfile.ZipFile(path, "r")
        except zipfile.BadZipFile:
            return []
        try:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            txt = [n for n in names if n.lower().endswith((".txt", ".tsv", ".csv"))] or names
            for n in sorted(txt):
                with zf.open(n, "r") as fh:
                    _slurp(n, io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline=""))
        finally:
            zf.close()
    else:
        with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            _slurp(os.path.basename(path), fh)
    return out


def _detect_counts_columns(header):
    """Return (gene_idx, baseline_idx, endpoint_idxs) for the Dede MOESM4 header, or (None, None, []).
    GENE col = header cell normalizing to 'gene' (NOT 'gene_clone'); baseline = a col mentioning 'plasmid' or 't0';
    endpoints = the remaining columns (the *.t2*.ex endpoint read counts)."""
    norm = [_norm(h) for h in header]
    gene_idx = None
    for i, h in enumerate(norm):
        if h == "gene":
            gene_idx = i
            break
    if gene_idx is None:  # fall back to a 'gene' col that is not the clone id
        for i, h in enumerate(norm):
            if "gene" in h and "clone" not in h:
                gene_idx = i
                break
    base_idx = None
    for i, h in enumerate(norm):
        if "plasmid" in h or h.endswith("t0") or ".t0." in h or "_t0_" in h or h.endswith("_t0"):
            base_idx = i
            break
    if gene_idx is None or base_idx is None:
        return None, None, []
    endpoints = [i for i in range(len(header))
                 if i != gene_idx and i != base_idx and ("clone" not in norm[i])
                 and (".ex" in norm[i] or ".t2" in norm[i] or "_t2" in norm[i] or "endpoint" in norm[i]
                      or "_ex" in norm[i])]
    if not endpoints:  # permissive fallback: every non-gene/non-clone/non-baseline column that is numeric-ish
        endpoints = [i for i in range(len(header)) if i not in (gene_idx, base_idx) and "clone" not in norm[i]
                     and "gene" not in norm[i]]
    return gene_idx, base_idx, endpoints


def parse_dede_encas12a(counts_path):
    """Two-pass CPM parse of the Dede MOESM4 raw guide-pair counts. Per construct: log2FC = mean over endpoint columns of
    log2((cpm_endpoint + PSEUDO)/(cpm_plasmid + PSEUDO)). Constructs where exactly one side is a control/safe guide define the
    partner gene's SMF (single-mutant fitness); constructs where NEITHER side is a control define the pair's DMF (double-mutant
    fitness, the TARGET). Returns PATH 'A' (X,y=DMF,smf_tok,...) or PATH 'B' (escalate diagnostic)."""
    rows = _read_rows(counts_path)
    if len(rows) < 3:
        return {"path": "B", "reason": "counts_file_empty_or_unreadable", "n_rows": len(rows)}
    header = rows[0]
    gi, bi, eidx = _detect_counts_columns(header)
    if gi is None:
        return {"path": "B", "reason": "no_gene_or_baseline_column",
                "header": [str(x) for x in header[:20]]}

    # ---- pass 1: column sums (for CPM) over data rows with a finite baseline + >=1 finite endpoint ----
    colsum = defaultdict(float)
    parsed = []  # (symA, symB, base_count, [endpoint_counts])
    ncols = len(header)
    for r in rows[1:]:
        if len(r) <= max(gi, bi, (max(eidx) if eidx else 0)):
            continue
        base = _finite_float(r[bi])
        if base is None:
            continue
        evals = []
        for c in eidx:
            v = _finite_float(r[c]) if c < len(r) else None
            evals.append(v)
        if not any(v is not None for v in evals):
            continue
        symA, symB = _split_gene_pair(r[gi])
        if symA is None or symB is None:
            continue
        colsum[bi] += base
        for c, v in zip(eidx, evals):
            if v is not None:
                colsum[c] += v
        parsed.append((symA, symB, base, evals))
    if len(parsed) < MIN_PAIRS:
        return {"path": "B", "reason": "too_few_parseable_count_rows", "n_rows": len(rows),
                "n_parsed": len(parsed), "header": [str(x) for x in header[:20]]}

    base_tot = colsum[bi] if colsum[bi] > 0 else 1.0
    end_tot = {c: (colsum[c] if colsum[c] > 0 else 1.0) for c in eidx}

    # ---- pass 2: per-construct pooled log2FC (endpoint CPM vs plasmid CPM), averaged over all endpoint columns ----
    # a construct's fitness = mean over endpoint replicate/cell-line columns of log2((cpm_end+PC)/(cpm_base+PC)); pooling all
    # endpoint columns is the SNR lever (Dede replicate r=0.87-0.94 -> pooled reps give a clean per-construct fitness).
    constructs = []  # (symA, symB, lfc)
    for (symA, symB, base, evals) in parsed:
        cpm_base = 1e6 * base / base_tot
        lfcs = []
        for c, v in zip(eidx, evals):
            if v is None:
                continue
            cpm_end = 1e6 * v / end_tot[c]
            lfcs.append(math.log2((cpm_end + PSEUDO) / (cpm_base + PSEUDO)))
        if lfcs:
            constructs.append((symA, symB, float(np.mean(lfcs))))
    if len(constructs) < MIN_PAIRS:
        return {"path": "B", "reason": "too_few_constructs_with_lfc", "n_constructs": len(constructs)}

    # ---- control-guide detection: explicit token set (PRIMARY) + a conservative degree-OUTLIER backup ----
    # PRIMARY = the explicit control/safe token set (reliable). BACKUP = degree-outlier: library-wide control guides pair with
    # MANY genes, so a token whose partner-degree is a strong outlier above the 75th-percentile gene degree is a candidate
    # control. The backup is OUTLIER-only (never fires on ordinary hub genes) AND self-disables if it would flag > 40% of tokens
    # (a dense network where degree cannot discriminate -- e.g. a fully-connected slice) so it can NEVER destroy real genes.
    partners = defaultdict(set)
    all_syms = set()
    for (a, b, _l) in constructs:
        all_syms.add(a); all_syms.add(b)
        partners[a].add(b); partners[b].add(a)
    n_syms = max(1, len(all_syms))

    def _is_ctrl_token(s):
        if s in CTRL_TOKENS:
            return True
        for p in CTRL_PREFIXES:
            if s.startswith(p):
                return True
        return False

    deg = {s: len(partners[s]) for s in all_syms}
    sorted_deg = sorted(deg.values())
    p75 = sorted_deg[int(0.75 * (len(sorted_deg) - 1))] if sorted_deg else 0
    deg_cut = max(8, int(math.ceil(4.0 * max(p75, 1))))       # outlier: >= 4x the 75th-percentile gene degree, min 8
    ctrl_token = set(s for s in all_syms if _is_ctrl_token(s))
    ctrl_deg = set(s for s in all_syms if deg[s] >= deg_cut)
    degree_disabled = False
    if len(ctrl_deg) > 0.40 * n_syms:                          # misfiring on a dense network -> disable the backup entirely
        degree_disabled = True
        ctrl_deg = set()
    ctrl = ctrl_token | ctrl_deg
    ctrl_by_token = len(ctrl_token)
    ctrl_by_degree = len(ctrl_deg - ctrl_token)
    top_degree_tokens = [(s, deg[s]) for s in sorted(all_syms, key=lambda z: (-deg[z], z))[:12]]

    # ---- NEUTRAL REFERENCE (control-anchored log2FC centering) ----
    # CPM per-construct log2FC over a UNIFORM plasmid baseline carries a GLOBAL library-size offset delta=log2(N/sum(2^lfc)):
    # when a net fraction of the library depletes, the surviving constructs read RELATIVELY enriched by delta, so every
    # recovered log2FC (SMF and DMF alike) is shifted by the SAME constant. This offset is INVARIANT to any global re-scaling
    # of the planted fitness (CPM measures only relative abundance), so it CANNOT be corrected downstream of the counts -- it
    # must be removed by referencing to the non-targeting/control level. STANDARD CRISPR normalization = center log2FC on the
    # control:control (SAFE:SAFE) constructs (true neutral, fitness 0 -> their recovered level == delta). We center ONLY when a
    # clean control anchor exists (>= MIN_CTRL_REF control:control constructs); else neutral_ref=0.0 (no centering, prior
    # behavior -- we deliberately do NOT fall back to the bulk median, which would MISPLACE the band whenever the near-neutral
    # pocket is a minority, exactly the regime this cell targets). NaN-safe: median of finite lfc; empty -> 0.0.
    cc_lfcs = [lfc for (a, b, lfc) in constructs if (a in ctrl) and (b in ctrl) and math.isfinite(lfc)]
    if len(cc_lfcs) >= MIN_CTRL_REF:
        neutral_ref = float(np.median(cc_lfcs)); neutral_ref_src = "control_control_median"
    else:
        neutral_ref = 0.0; neutral_ref_src = "none_no_control_anchor"
    if not math.isfinite(neutral_ref):
        neutral_ref = 0.0; neutral_ref_src = "none_nonfinite_guard"

    # ---- aggregate: SMF (single-KO-vs-control) + DMF (double, neither control), on control-anchored log2FC ----
    smf_acc = defaultdict(lambda: [0.0, 0])   # real gene -> [sum lfc, count] over single-KO constructs
    dmf_acc = defaultdict(lambda: [0.0, 0])   # (geneA,geneB) canonical -> [sum lfc, count] over double constructs
    n_single = 0
    n_double = 0
    for (a, b, lfc) in constructs:
        lfc = lfc - neutral_ref  # control-anchored: express fitness relative to the non-targeting neutral level
        a_c = a in ctrl
        b_c = b in ctrl
        if a_c and b_c:
            continue  # control:control -> reference only (already consumed by neutral_ref)
        if a_c ^ b_c:  # exactly one control -> single-KO of the real partner
            real = b if a_c else a
            rec = smf_acc[real]; rec[0] += lfc; rec[1] += 1
            n_single += 1
        else:  # neither control -> double mutant
            if a == b:
                continue  # self-pair; not an interaction
            key = (a, b) if a < b else (b, a)
            rec = dmf_acc[key]; rec[0] += lfc; rec[1] += 1
            n_double += 1

    diag = dict(n_constructs=len(constructs), n_syms=n_syms, n_ctrl=len(ctrl), ctrl_by_token=ctrl_by_token,
                ctrl_by_degree=ctrl_by_degree, deg_cut=deg_cut, degree_disabled=degree_disabled,
                top_degree_tokens=top_degree_tokens, n_single_constructs=n_single,
                n_double_constructs=n_double, ctrl_examples=sorted(ctrl)[:20], n_ctrl_ctrl=len(cc_lfcs),
                neutral_ref=round(neutral_ref, 5), neutral_ref_src=neutral_ref_src,
                endpoint_cols=[str(header[c]) for c in eidx][:12], baseline_col=str(header[bi]),
                gene_col=str(header[gi]))

    if n_single == 0 or len(smf_acc) == 0:
        return {"path": "B", "reason": "no_single_ko_controls_found", **diag}

    pair_dmf = {k: (s / c) for k, (s, c) in dmf_acc.items() if c >= 1}
    if len(pair_dmf) < MIN_PAIRS:
        return {"path": "B", "reason": "too_few_double_mutant_pairs", "n_pairs": len(pair_dmf), **diag}

    smf_gene = {g: (s / c) for g, (s, c) in smf_acc.items() if c >= 1}

    return _finalize_pairs(pair_dmf, smf_gene, len(rows), n_double, diag)


def _finalize_pairs(pair_dmf, smf_gene, n_rows, n_kept, diag):
    """Dense subnetwork (top-frequency genes) -> cap MAX_PAIRS -> contiguous token reindex. y = DMF; smf_tok[t] = mean SMF of
    token t (NaN if no single-KO construct). Returns PATH 'A' (X,y,n_tok,smf_tok,...) or PATH 'B' (escalate)."""
    gene_freq = defaultdict(int)
    for (a, b) in pair_dmf:
        gene_freq[a] += 1; gene_freq[b] += 1
    top = set(sorted(gene_freq.keys(), key=lambda o: (-gene_freq[o], o))[:TOP_ORF])
    pairs = sorted([k for k in pair_dmf.keys() if k[0] in top and k[1] in top])
    if len(pairs) > MAX_PAIRS:
        stride = int(math.ceil(len(pairs) / float(MAX_PAIRS)))
        pairs = pairs[::stride][:MAX_PAIRS]  # deterministic evenly-spaced subsample
    if len(pairs) < MIN_PAIRS:
        return {"path": "B", "reason": "insufficient_native_pairs_after_subnetwork", "n_pairs": len(pairs), **diag}
    toks = sorted(set([o for k in pairs for o in k]))
    tokid = {o: i for i, o in enumerate(toks)}
    Xl = []
    for k in pairs:
        i0 = tokid[k[0]]; i1 = tokid[k[1]]
        Xl.append([min(i0, i1), max(i0, i1)])
    X = np.array(Xl, dtype=np.int64)
    y = np.array([pair_dmf[k] for k in pairs], dtype=np.float64)
    smf_tok = np.full(len(toks), np.nan, dtype=np.float64)
    n_smf_tok = 0
    for o, i in tokid.items():
        if o in smf_gene:
            smf_tok[i] = smf_gene[o]; n_smf_tok += 1
    return {"path": "A", "X": X, "y": y, "n_tok": len(toks), "n_pairs": len(pairs), "n_rows": n_rows, "n_kept": n_kept,
            "smf_tok": smf_tok, "n_smf_tok": int(n_smf_tok), "diag": diag}


# ===========================================================================
# REGRESSION ARMS (shared-product = symmetric bind ; shared-sum = additive ; role-product = asymmetric) -- UNCHANGED
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
# NEAR-ZERO-SINGLES CURATION (UNITS-ADAPTIVE) + INTERACTION-VARIANCE-FRACTION (PRIMARY discriminator)
# ===========================================================================

def detect_smf_band(smf_tok):
    """Auto-detect the SMF units and return (lo, hi, units). CRISPR SMF is log2FC (neutral ~0) -> |SMF|<=NZ_LFC.
    WT-normalized SMF (neutral ~1.0) -> [SMF_WT_LO, SMF_WT_HI]. Decision by the median of finite SMF values."""
    finite = smf_tok[np.isfinite(smf_tok)]
    if finite.size == 0:
        return -NZ_LFC, NZ_LFC, "log2fc_default"
    med = float(np.median(finite))
    if med > 0.5:
        return SMF_WT_LO, SMF_WT_HI, "wt_normalized"
    return -NZ_LFC, NZ_LFC, "log2fc"


def near_zero_singles_mask(X, smf_tok, lo, hi):
    """Pairs where BOTH constituent genes have mean single-mutant fitness within the near-neutral band [lo, hi] (single-mutant
    fitness DEFECT ~0 by DIRECT measurement). Genes with no observed SMF (NaN) are excluded (conservative)."""
    a = smf_tok[X[:, 0]]; b = smf_tok[X[:, 1]]
    fin = np.isfinite(a) & np.isfinite(b)
    ok = (a >= lo) & (a <= hi) & (b >= lo) & (b <= hi)
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
    """Interaction-variance-fraction on a subset = Var(additive-residual) / Var(y). Returns (ivf, n)."""
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
# regimes + split -- UNCHANGED
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
    mag = np.abs(y_real[q] - hi_center)  # subset membership defined on the REAL DMF magnitude (robust-centered)

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
# planted arenas (positive control = interaction ; negative control = additive) -- UNCHANGED
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
    """SIGNAL-READABILITY certificate: best structured readout (strong additive OR SYM) vs MEAN on (stratum, sub)."""
    mean_mae = m_mae_fn(MEAN)
    add_rel = _rel(mean_mae, m_mae_fn("STRONG_ADD"))
    sym_rel = _rel(mean_mae, m_mae_fn(SYM))
    cands = [v for v in (add_rel, sym_rel) if v == v]
    return (max(cands) if cands else float("nan")), add_rel, sym_rel


def _readable_rel_arena(mode, seeds=(7, 13, 17), n_tok=8):
    """Readability certificate on a planted arena (interaction/additive = readable ; noise = unreadable)."""
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


def _nanmean(vals):
    v = [x for x in vals if x == x]
    return float(np.mean(v)) if v else float("nan")


def run_measurement(seeds, run_mode):
    _write_start_marker(expected_n_units=len(seeds) * len(REGIMES), run_mode=run_mode)
    t0 = time.perf_counter()
    counts_path, zdlfc_path, prov = acquire()
    base = dict(run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
                elapsed_s=round(time.perf_counter() - t0, 2), provenance=prov, seeds=list(seeds),
                bands=dict(NZ_LFC=NZ_LFC, SMF_WT_LO=SMF_WT_LO, SMF_WT_HI=SMF_WT_HI, MIN_CURATED=MIN_CURATED,
                           IVF_RATIO_HP=IVF_RATIO_HP, IVF_CURATED_FLOOR=IVF_CURATED_FLOOR,
                           IVF_RATIO_INDISTINCT=IVF_RATIO_INDISTINCT, HP_REL_CURATED=HP_REL_CURATED,
                           MIN_NOVEL_CURATED_N=MIN_NOVEL_CURATED_N, READABILITY_REL=READABILITY_REL, REFUTE_REL=REFUTE_REL,
                           MUSTFAIL_REL_TOL=MUSTFAIL_REL_TOL, POS_CTRL_REL=POS_CTRL_REL, NEG_CTRL_REL=NEG_CTRL_REL,
                           TOP_ORF=TOP_ORF, MAX_PAIRS=MAX_PAIRS, MIN_PAIRS=MIN_PAIRS,
                           IVF_KFOLD=IVF_KFOLD, IVF_RIDGE_L2=IVF_RIDGE_L2, HI_Z=HI_Z, PSEUDO=PSEUDO))

    # positive/negative controls (planted; the FIXED gate carries a genuine non-additive positive control)
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    pos_ok = bool(pos_rel == pos_rel and pos_rel >= POS_CTRL_REL)
    neg_ok = bool(neg_rel == neg_rel and neg_rel <= NEG_CTRL_REL)
    base["controls"] = dict(pos_rel=round(pos_rel, 5), pos_sym_mae=round(pos_sym, 5), pos_sadd_mae=round(pos_sadd, 5),
                            neg_rel=round(neg_rel, 5), neg_sym_mae=round(neg_sym, 5), neg_sadd_mae=round(neg_sadd, 5),
                            pos_ok=pos_ok, neg_ok=neg_ok)

    if counts_path is None:
        msg = ("ACQUIRE_FAILED || could not download the Dede 2020 MOESM4 raw-count file from any candidate URL (see "
               "provenance.acquire_errors). pos_ctrl_rel=%s neg_ctrl_rel=%s (machinery %s)." %
               (_fmt(pos_rel), _fmt(neg_rel), "VALID" if (pos_ok and neg_ok) else "CHECK"))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200])
        return base

    try:
        data = parse_dede_encas12a(counts_path)
    except (zipfile.BadZipFile, OSError, csv.Error, UnicodeDecodeError, ValueError) as e:
        msg = ("ACQUIRE_FAILED || Dede MOESM4 present but unreadable: %s: %s. pos_ctrl_rel=%s neg_ctrl_rel=%s."
               % (type(e).__name__, str(e)[:160], _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200], parse_error=str(e)[:300])
        return base

    if data["path"] == "B":
        reason = data.get("reason", "")
        if reason in ("no_gene_or_baseline_column", "no_single_ko_controls_found"):
            verdict = "ESCALATE_NEED_RAW_CONSTITUENTS"
            handoff = ("the acquired file does not yield the raw SMF/DMF constituents (reason=%s). A GI-score-only target "
                       "(zdLFC) would make SYM-vs-additive vacuous. HAND-OFF: re-run on the raw-count file (MOESM4) with a "
                       "verified control-guide token, OR a per-pair table retaining SMF-A/SMF-B/DMF (Horlbeck GSE116198)." % reason)
        else:
            verdict = "ESCALATE_NO_NATIVEPAIR_STRUCTURE"
            handoff = ("could not build a native gene-pair slice (reason=%s). HAND-OFF: verify the MOESM4 schema / raise "
                       "MAX_PAIRS / pool Dede+Parrish or use the Benchmarking-GI-Scores harmonized compendium." % reason)
        msg = ("%s || %s diag=%s pos_ctrl_rel=%s neg_ctrl_rel=%s"
               % (verdict, handoff, json.dumps({k: v for k, v in data.items() if k not in ("path", "X", "y", "smf_tok")})[:500],
                  _fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict=verdict, verdict_msg=msg, summary=msg[:200], escalate=True, path="B",
                    parse_diag={k: v for k, v in data.items() if k not in ("path", "X", "y", "smf_tok")})
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    # ---------- PATH A: SUBSET-CURATED near-zero-singles IVF discriminator + curated transfer proof ----------
    X, y, n_tok = data["X"], data["y"], data["n_tok"]
    smf_tok = data.get("smf_tok")
    n_smf_tok = int(data.get("n_smf_tok", 0))
    diag = data.get("diag", {})

    if smf_tok is None or n_smf_tok == 0:
        msg = ("ESCALATE_NEED_RAW_CONSTITUENTS || parsed pairs carry no per-gene single-mutant fitness (SMF), so the near-zero-"
               "singles curation cannot be computed. HAND-OFF: verify the single-KO-vs-control constructs in MOESM4. "
               "pos_ctrl_rel=%s neg_ctrl_rel=%s" % (_fmt(pos_rel), _fmt(neg_rel)))
        base.update(verdict="ESCALATE_NEED_RAW_CONSTITUENTS", verdict_msg=msg, summary=msg[:200], escalate=True, path="A",
                    n_pairs=int(X.shape[0]), n_tok=int(n_tok), n_smf_tok=n_smf_tok, parse_diag=diag)
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    smf_lo, smf_hi, smf_units = detect_smf_band(smf_tok)
    cur_mask = near_zero_singles_mask(X, smf_tok, smf_lo, smf_hi)
    n_cur = int(cur_mask.sum())
    n_pairs = int(X.shape[0])
    _log("PATH A: n_pairs=%d n_tok=%d n_smf_tok=%d units=%s band=[%.3f,%.3f] | NEAR-ZERO-SINGLES curated=%d seeds=%d"
         % (n_pairs, n_tok, n_smf_tok, smf_units, smf_lo, smf_hi, n_cur, len(seeds)))

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
        msg = ("HARD_FAIL_UNDERPOWERED_CURATED_N || only %d clean near-zero-singles pairs (both SMF in [%.3f,%.3f], units=%s) "
               "< MIN_CURATED=%d in this Dede slice -- insufficient N to test at power (directional-only). IVF(curated=%s vs "
               "matched-random=%s ratio=%s) reported but UNDERPOWERED. HAND-OFF: higher-N fallback = Benchmarking-GI-Scores "
               "harmonized compendium (~8000 pairs) OR pool Dede+Parrish/pgPEN by hand; OR widen the near-zero band / raise "
               "MAX_PAIRS. pos_ctrl_rel=%s neg_ctrl_rel=%s (machinery %s)."
               % (n_cur, smf_lo, smf_hi, smf_units, MIN_CURATED, _fmt(ivf_curated), _fmt(ivf_random), _fmt(ivf_ratio),
                  _fmt(pos_rel), _fmt(neg_rel), "VALID" if (pos_ok and neg_ok) else "CHECK"))
        base.update(verdict="HARD_FAIL_UNDERPOWERED_CURATED_N", verdict_msg=msg, summary=msg[:200],
                    escalate=True, path="A", n_pairs=n_pairs, n_tok=int(n_tok), n_curated=n_cur, n_smf_tok=n_smf_tok,
                    smf_units=smf_units, ivf=ivf_block, parse_diag=diag)
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    # SECONDARY: transfer proof + readability + must-fails on the CURATED near-zero-singles ARENA.
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

    transfer_rel = _rel(mc(CLEAN, "novel", "full", "STRONG_ADD"), mc(CLEAN, "novel", "full", SYM))
    seen_rel = _rel(mc(CLEAN, "seen", "full", "STRONG_ADD"), mc(CLEAN, "seen", "full", SYM))
    role_rel = _rel(mc(CLEAN, "seen", "full", "STRONG_ADD"), mc(CLEAN, "seen", "full", ROLE))
    novel_cur_n = mc_n(CLEAN, "novel", "full")

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
                         "DATASET-SNR null, NOT a thesis result. Even the high-SNR Dede screen unreadable in this pocket -> "
                         "higher-N/higher-SNR compendium or pooled screens." % (_fmt(readable_rel), READABILITY_REL))
    msg = ("%s || CURATED n=%d/%d near-zero-singles (SMF in [%.3f,%.3f] units=%s) | "
           "IVF curated=%s vs matched-random=%s ratio=%s (>=%.1f enriched=%s; ivf_all=%s floor=%.2f) | "
           "TRANSFER novel_rel_MAE=%s(>=%.2f pass=%s) seen_rel=%s role_rel=%s SYM/SADD=%s/%s | "
           "READABLE_rel=%s(>=%.2f ok=%s add=%s sym=%s) | POS_ctrl=%s(>=%.2f %s) NEG_ctrl=%s(<=%.2f %s) | "
           "MUSTFAIL shuf=%s arb=%s(<=%.2f) oracle=%s leak=%s | novel_cur_n=%.1f power=%s"
           % (verdict, n_cur, n_pairs, smf_lo, smf_hi, smf_units,
              _fmt(ivf_curated), _fmt(ivf_random), _fmt(ivf_ratio), IVF_RATIO_HP, ivf_enriched, _fmt(ivf_all),
              IVF_CURATED_FLOOR, _fmt(transfer_rel), HP_REL_CURATED, transfer_pass, _fmt(seen_rel), _fmt(role_rel),
              _fmt(mc(CLEAN, "novel", "full", SYM)), _fmt(mc(CLEAN, "novel", "full", "STRONG_ADD")),
              _fmt(readable_rel), READABILITY_REL, readable_ok, _fmt(read_add_rel), _fmt(read_sym_rel),
              _fmt(pos_rel), POS_CTRL_REL, pos_ok, _fmt(neg_rel), NEG_CTRL_REL, neg_ok,
              _fmt(shuf_rel), _fmt(arb_rel), MUSTFAIL_REL_TOL, _fmt(orc_mae), leak_ok, novel_cur_n, power_ok) + escalate_tail)

    base.update(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], path="A",
        escalate=verdict.startswith(("UNREADABLE", "REFUTE")),
        n_pairs=n_pairs, n_tok=int(n_tok), n_curated=n_cur, n_tok_curated=int(n_tok_c), n_smf_tok=n_smf_tok,
        smf_units=smf_units, smf_band=[smf_lo, smf_hi],
        curated_frac=round(n_cur / float(n_pairs), 5) if n_pairs else None,
        n_rows_scanned=int(data.get("n_rows", 0)), n_kept=int(data.get("n_kept", 0)), parse_diag=diag,
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
# SELF-TEST (real bind path + REAL raw-count parser on a synthetic Dede MOESM4 TSV + planted controls + determinism)
# ===========================================================================

def _make_synth_dede_moesm4(path, n_genes=SELFTEST_N_GENES, n_neutral=SELFTEST_N_NEUTRAL, n_guides=3, seed=101):
    """Write a tiny synthetic Dede MOESM4-format raw-count TSV (GENE_CLONE|GENE|<endpoint cols>|plasmid.T0.Ex) exercising the
    REAL parse_dede_encas12a end-to-end (CPM -> log2FC -> control detection -> SMF/DMF -> subnetwork). Layout:
      - a 'SAFE' control gene paired with every real gene -> single-KO constructs -> SMF (planted so the FIRST n_neutral genes
        are near-neutral single-KO -> the near-zero-singles pocket = both-neutral pairs).
      - real:real double constructs -> DMF planted with a symmetric 2-way interaction ON near-zero-singles (both-neutral) pairs
        (an AND-gate: low DMF only when both singles are near-neutral), so the curated pocket carries readable non-additivity.
    The neutral genes are a deliberate MINORITY (n_neutral << n_genes): the curated pocket is then a small fraction of the
    network, so the matched-random IVF baseline (self-test 7c) samples FEW interaction pairs and stays clean. A balanced
    (~half-neutral) fixture would POLLUTE the matched-random baseline with interaction pairs and cap the e2e IVF ratio at
    ~1/pocket_fraction (the BARE IVF self-test compares against the PURE additive subset so it is unaffected; only the e2e
    path uses a random draw). This mirrors real Dede data where near-zero-singles pairs are a curated minority.
    Counts are back-computed from a target log2FC vs a fixed plasmid baseline so the pipeline recovers the planted fitness."""
    rng = np.random.default_rng(seed)
    genes = ["G%02d" % d for d in range(n_genes)]
    # planted per-gene single-KO fitness (log2FC): the FIRST n_neutral genes near-neutral (~0), the rest depleted (~ -1.5)
    smf_true = {g: (0.02 if (int(g[1:]) < n_neutral) else -1.5) for g in genes}
    tab = rng.normal(0.0, 1.0, size=(n_genes, n_genes)); tab = 0.5 * (tab + tab.T)  # symmetric interaction table
    base_reads = 500.0  # fixed plasmid baseline read count per construct
    end_cols = ["A549.T2A.Ex", "A549.T2B.Ex", "HT29.T2A.Ex", "HT29.T2B.Ex", "OVCAR8.T2A.Ex", "OVCAR8.T2B.Ex"]
    header = ["GENE_CLONE", "GENE"] + end_cols + ["plasmid.T0.Ex"]
    lines = ["\t".join(header)]

    def _row(gene_label, clone, target_lfc):
        # back-compute endpoint reads from target_lfc: end = base * 2^lfc (CPM cancels since all columns share the same total
        # by construction here; small noise added per column).
        cells = [clone, gene_label]
        for _c in end_cols:
            reads = base_reads * (2.0 ** (target_lfc + 0.02 * rng.normal()))
            cells.append("%.1f" % max(reads, 1.0))
        cells.append("%.1f" % base_reads)
        return "\t".join(cells)

    # control:control (SAFE:SAFE) NEUTRAL-ANCHOR constructs (fitness 0): the parser centers all log2FC on their level, which
    # removes the CPM library-size offset delta=log2(N/sum(2^lfc)) that a net-depleted synthetic library imposes on EVERY
    # recovered log2FC. Without this anchor the planted near-neutral (even-gene) SMF is shifted out of the +/-0.5 band and the
    # curated pocket selects zero pairs. n_anchor > MIN_CTRL_REF so the control-anchored branch fires.
    for gd in range(max(n_guides, MIN_CTRL_REF) + 3):
        lines.append(_row("SAFE.%d:SAFE.%d" % (gd + 1, gd + 2), "SAFE_SAFE_%d" % gd, 0.0 + 0.03 * rng.normal()))
    # single-KO constructs: each real gene paired with SAFE (multiple guides) -> defines SMF
    for gi, g in enumerate(genes):
        for gd in range(n_guides):
            lines.append(_row("%s.%d:SAFE.%d" % (g, gd + 1, gd + 1), "%s_SAFE_%d" % (g, gd),
                              smf_true[g] + 0.03 * rng.normal()))
    # double constructs: all real:real pairs; DMF = additive-of-singles + (interaction only on both-neutral near-zero pairs).
    # The interaction magnitude (1.6*tab, std ~1.13) DWARFS the both-neutral additive background (0.04) -> the curated pocket
    # already carries a NEAR-PURE symmetric interaction; the plant strength is NOT the limiter (the pocket FRACTION is).
    for i in range(n_genes):
        for j in range(i + 1, n_genes):
            both_near_zero = (i < n_neutral and j < n_neutral)
            inter = (1.6 * float(tab[i, j])) if both_near_zero else 0.0  # AND-gate: interaction only in the curated pocket
            dmf = smf_true[genes[i]] + smf_true[genes[j]] + inter
            for gd in range(n_guides):
                lines.append(_row("%s.%d:%s.%d" % (genes[i], gd + 1, genes[j], gd + 1),
                                  "%s_%s_%d" % (genes[i], genes[j], gd), dmf + 0.03 * rng.normal()))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


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

    # (3) REAL raw-count PARSER on a synthetic Dede MOESM4 TSV (exercises parse_dede_encas12a PATH-A end-to-end:
    #     CPM -> log2FC -> control detection -> SMF/DMF -> subnetwork -> reindex).
    tmp_txt = os.path.join(CACHE_DIR, "_selftest_synth_moesm4.txt")
    os.makedirs(CACHE_DIR, exist_ok=True)
    _make_synth_dede_moesm4(tmp_txt, n_genes=SELFTEST_N_GENES, n_neutral=SELFTEST_N_NEUTRAL, n_guides=3)
    saved_min = MIN_PAIRS
    try:
        globals()["MIN_PAIRS"] = 40  # synthetic slice is tiny; relax the PATH-A floor for the self-test only
        sd = parse_dede_encas12a(tmp_txt)
    finally:
        globals()["MIN_PAIRS"] = saved_min
        try:
            os.remove(tmp_txt)
        except OSError:
            pass
    # SELFTEST_N_GENES real genes -> C(n,2) double pairs; SAFE is the control -> excluded from tokens; SMF for all real genes.
    n_exp_pairs = SELFTEST_N_GENES * (SELFTEST_N_GENES - 1) // 2
    parser_ok = bool(sd.get("path") == "A" and sd.get("n_tok", 0) == SELFTEST_N_GENES
                     and sd.get("n_pairs", 0) == n_exp_pairs and sd.get("n_smf_tok", 0) == SELFTEST_N_GENES)
    diag = sd.get("diag", {})
    details["parser_path"] = sd.get("path"); details["parser_n_pairs"] = sd.get("n_pairs")
    details["parser_n_tok"] = sd.get("n_tok"); details["parser_n_smf_tok"] = sd.get("n_smf_tok")
    details["parser_ctrl_detected"] = diag.get("n_ctrl"); details["parser_n_single"] = diag.get("n_single_constructs")
    details["parser_ok"] = parser_ok

    # (3b) NEAR-ZERO-SINGLES selector on the synthetic slice: units auto-detected log2fc; even-index genes near-neutral -> the
    # curated pocket = pairs of two even-index genes. Validates the selector picks EXACTLY the both-even near-neutral pairs.
    smf_tok_st = sd.get("smf_tok"); Xst = sd.get("X")
    nzs_ok = False
    if smf_tok_st is not None and Xst is not None:
        lo_st, hi_st, units_st = detect_smf_band(smf_tok_st)
        curated_st = near_zero_singles_mask(Xst, smf_tok_st, lo_st, hi_st)
        # token index == sorted gene order == G00,G01,... so the FIRST SELFTEST_N_NEUTRAL tokens are the near-neutral genes;
        # the curated pocket = pairs of two neutral genes (a realistic MINORITY of the network).
        both_neutral = np.array([(int(Xst[r, 0]) < SELFTEST_N_NEUTRAL) and (int(Xst[r, 1]) < SELFTEST_N_NEUTRAL)
                                 for r in range(Xst.shape[0])], dtype=bool)
        nzs_ok = bool(units_st == "log2fc" and int(curated_st.sum()) > 0 and np.array_equal(curated_st, both_neutral))
        details.update(nzs_units=units_st, nzs_band=[round(lo_st, 3), round(hi_st, 3)],
                       nzs_curated_n=int(curated_st.sum()), nzs_expected_n=int(both_neutral.sum()), nzs_ok=nzs_ok)
    else:
        details.update(nzs_ok=False)

    # (3c) a header with no gene/baseline columns must route to escalate (PATH B).
    gi_u, bi_u, _e = _detect_counts_columns(["ID", "SMILES", "VALUE", "Nonadd_pC"])
    nonpair_routes_B = (gi_u is None or bi_u is None)
    details["nonpair_header_routes_B"] = nonpair_routes_B

    # (4) POSITIVE control: planted symmetric-interaction arena -> SYM beats STRONG additive (discriminator FIRES at scale).
    pos_rel, pos_sym, pos_sadd = _control_rel("interaction")
    details.update(dict(pos_rel=round(pos_rel, 4), pos_sym_mae=round(pos_sym, 4), pos_sadd_mae=round(pos_sadd, 4)))
    # (5) NEGATIVE control: planted ADDITIVE arena -> SYM must NOT beat additive (gate not saturation-vacuous).
    neg_rel, neg_sym, neg_sadd = _control_rel("additive")
    details.update(dict(neg_rel=round(neg_rel, 4), neg_sym_mae=round(neg_sym, 4), neg_sadd_mae=round(neg_sadd, 4)))

    # (5b) SIGNAL-READABILITY GATE must DISCRIMINATE readable structure from pure noise.
    read_add, radd_a, rsym_a = _readable_rel_arena("additive")     # readable -> gate fires
    read_int, radd_i, rsym_i = _readable_rel_arena("interaction")  # readable -> gate fires
    read_noise, radd_n, rsym_n = _readable_rel_arena("noise")      # unreadable -> gate rejects
    readability_fires_on_readable = bool(read_add == read_add and read_add >= READABILITY_REL
                                         and read_int == read_int and read_int >= READABILITY_REL)
    readability_rejects_noise = bool(not (read_noise == read_noise) or read_noise < READABILITY_REL)
    details.update(dict(readable_rel_additive=round(read_add, 4), readable_rel_interaction=round(read_int, 4),
                        readable_rel_noise=round(read_noise, 4)))

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

    # (7b) IVF DISCRIMINATOR (PRIMARY statistic) FIRES on a planted mixed arena.
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

    # (7c) END-TO-END on the synthetic Dede slice: the CURATED near-zero-singles pocket must be IVF-enriched vs matched-random
    # (the AND-gate interaction was planted ONLY on both-even pairs) AND carry a readable target -- proves the raw-count->DMF
    # pipeline yields a discriminating pocket, not just that the parser runs.
    e2e_ok = False
    if sd.get("path") == "A" and Xst is not None:
        Xf, yf, ntf = sd["X"], sd["y"], sd["n_tok"]
        lo_f, hi_f, _u = detect_smf_band(sd["smf_tok"])
        cur_f = near_zero_singles_mask(Xf, sd["smf_tok"], lo_f, hi_f)
        resid_f = oof_additive_residual(Xf, yf, ntf, 7)
        ivf_c, _n1 = ivf_of(resid_f, yf, cur_f)
        ivf_r, _n2 = ivf_of(resid_f, yf, matched_random_mask(Xf.shape[0], int(cur_f.sum()), 7))
        ratio_f = (ivf_c / ivf_r) if (ivf_r == ivf_r and ivf_r > 1e-9) else float("inf")
        e2e_ok = bool(ivf_c == ivf_c and ivf_c >= IVF_CURATED_FLOOR and ratio_f >= IVF_RATIO_HP)
        details.update(e2e_ivf_curated=round(ivf_c, 4) if ivf_c == ivf_c else None,
                       e2e_ivf_random=round(ivf_r, 4) if ivf_r == ivf_r else None,
                       e2e_ivf_ratio=round(ratio_f, 3) if math.isfinite(ratio_f) else None, e2e_ok=e2e_ok)

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hadamard_equals_complex_bind": prod_is_bind,
        "real_rawcount_parser_reconstructs_smf_dmf": parser_ok,
        "near_zero_singles_selector_picks_curated_pocket": nzs_ok,
        "end_to_end_curated_pocket_ivf_enriched": e2e_ok,
        "ivf_discriminator_fires_on_planted_arena": ivf_fires,
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
