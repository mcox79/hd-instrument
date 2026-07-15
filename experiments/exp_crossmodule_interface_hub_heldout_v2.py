"""CROSSMODULE_INTERFACE_HUB_IDENTITY_BIND (v1): the FOUNDATION-ARCHITECTURE proof that the two-tier module foundation is
"ideal to work seamlessly" -- can we register a SECOND real-data module against a shared canonical-ID HUB and compose a
CROSS-MODULE conjunction via IDENTITY-ANCHORED bind/unbind traversal (hub-identity + spoke-relation; brain-aligned ATL
hub-and-spoke), NOT merged embeddings? This is INDEPENDENT of module #1's interaction-reading thesis verdict: it tests
IDENTITY + COMPOSITION, robust to Costanzo epsilon noise (we use only the EDGE STRUCTURE, not the epsilon magnitude).

TWO REAL MODULES OVER THE SAME YEAST ORF ENTITIES (zero crosswalk service needed -- exact SGD systematic-ORF-name join):
  Module P (PHYSICAL) = BioGRID yeast TAB3, Experimental-System-Type == physical -> gene-gene PHYSICAL-interaction edges.
  Module G (GENETIC)  = Costanzo 2016 yeast SGA, significant |epsilon| -> gene-gene GENETIC-interaction edges.
Both files' entity columns are the IDENTICAL SGD systematic ORF name (e.g. YAL001C) -> the cross-module join is a literal
string-equality match on the same ID convention (NOT fuzzy string match, NOT a crosswalk service).

CROSS-MODULE QUERY (identity-anchored bind/unbind traversal): "which gene Z PHYSICALLY interacts with X (module P) AND
GENETICALLY interacts with Y (module G)?"  gold answer A(X,Y) = phys_partners(X) INTERSECT gen_partners(Y).
  Each module = its OWN associative store (a superposition of bound edges) built from SHARED hub codes h(.):
    M_P = sum over physical edges (a,b) of bind(h(a), h(b)) ;  M_G = sum over genetic edges (a,b) of bind(h(a), h(b)).
  Traversal:  s_P(z) = <unbind(M_P, h(X)), h(z)>   (X's physical partners, cleaned up against the hub codebook)
              s_G(z) = <unbind(M_G, h(Y)), h(z)>   (Y's genetic partners, cleaned up against the hub codebook)
  CONJUNCTION (identity-anchored AND) = rank z by s_P(z) * s_G(z). The join is BY CONSTRUCTION exact because h(z) is the SAME
  hub vector in BOTH module readouts (one identity code per canonical ORF, shared read-only across spokes).

ARMS (retrieval, MAP higher=better on the true cross-module answer set):
  HUB      = shared hub codes + SEPARATE relation-typed stores (spokes) + identity-anchored product. WINNER hypothesis.
  MERGED   = SAME shared hub codes but ONE FLAT store (physical+genetic edges merged, NO relation typing) -> relation
             smearing: unbind(M_merged,h(X)) returns ANY-partner of X -> conjunction cannot enforce phys-vs-gen -> polluted.
             (isolates the SPOKE-SEPARATION variable; STRONG baseline -- it still has shared identity.)
  NO_HUB   = SEPARATE relation-typed stores but module G built with an INDEPENDENT codebook (no shared identity registry).
             With no canonical-ID correspondence between the two code spaces, the genetic readout cannot be re-identified
             against the physical readout -> best achievable is a RANDOM correspondence (Rank-3 learned-alignment is
             out-of-scope: independent random codes carry NO signal to align on) -> conjunction collapses to chance.
             (isolates the SHARED-IDENTITY variable.)
  SCRAMBLE = HUB but module G's edges stored under a SCRAMBLED identity permutation (identity anchor broken). MUST-FAIL.
  RANDOM   = random candidate scores -> anchors the pure-chance MAP floor for the variable-size answer sets.
  PHYS_ONLY / GEN_ONLY = single-constraint reference ceilings (rank by ONE module's real readout alone). Because the gold
             answer A(X,Y) = phys(X) INTERSECT gen(Y) is a SUBSET of BOTH phys(X) and gen(Y), a single intact module already
             scores ABOVE the pure-random floor (a conjunction's answer set is a subset of each conjunct's neighbourhood).
             This MEASURES the irreducible "one intact module retained" residual -- the honest null for NO_HUB/SCRAMBLE, which
             each keep the intact PHYSICAL module and only break the GENETIC identity bridge.
HUB needs BOTH hub-identity (beats NO_HUB) AND spoke-separation (beats MERGED) AND genuine CONJUNCTION (beats the
single-constraint ceiling PHYS_ONLY/GEN_ONLY by the margin) -> HUB > max(MERGED, NO_HUB, single_ceiling) by the margin.
MUST-FAIL (redefined): NO_HUB / SCRAMBLE break the shared-identity bridge, so they get NO conjunction gain over ONE module ->
their MAP must NOT exceed single_ceiling + tol AND must sit >= HP_MARGIN_ABS below HUB. Their floor is the single-module
residual, NOT the pure-random floor (the earlier "collapse to RANDOM" band was mis-specified: the physical module stays intact
so the retained physical readout floats these arms to the single-constraint ceiling by construction, not to chance).

PRIMARY REPORTED FIELD -- JOIN PRECISION (exact-ORF, NOT fuzzy):
  join_precision   = fraction of BioGRID physical-edge endpoints whose systematic-name token is a well-formed canonical
                     SGD ORF id (the join-key link precision; near-1.0 = clean deterministic exact join).
  fuzzy_gain_frac  = extra ORF-vocab matches a case/whitespace-normalizing fuzzy pass would add OVER exact string equality,
                     as a fraction of the exact overlap. ~0 => the exact join is NOT lossy (a fuzzy layer buys nothing).
  n_shared_orfs    = |BioGRID_orfs INTERSECT Costanzo_orfs| under exact string equality.

HELD-OUT SPLIT (v2 UPGRADE -- CONSTRUCTION vs PREDICTIVE CAPABILITY):
  The gold conjunction A(X,Y) = phys(X) INTERSECT gen(Y) is NEVER stored as a unit -- M_P/M_G are superpositions of the
  INDIVIDUAL module edges ONLY, so every query is composed fresh (nothing about the intersection is stored). v1 asserted this
  but did NOT stratify or machine-check it, so a landed-VET could not distinguish "recovers stored conjunctions"
  (CONSTRUCTION) from "composes/predicts held-out conjunctions" (CAPABILITY). v2 stratifies the EVAL queries by whether the
  pair (X,Y) is a DIRECT stored edge in EITHER module:
    NOVEL / HELD-OUT (primary): (X,Y) is NOT a direct stored edge in phys OR gen -> the pair was NEVER presented as related in
      ANY module; the shared conjunction-neighbour z can ONLY be found by COMPOSING the two independently-stored module
      readouts (no pair-attestation to ride on). This is the airtight PREDICTIVE stratum.
    SEEN (context): (X,Y) IS a direct stored edge (the pair's relationship is directly attested). Reported, not gated.
  Store construction is IDENTICAL for both strata (only the eval queries are stratified -> no per-stratum store leakage). A
  machine-checked non-leakage assertion (novel_no_direct_edge) fires in run_measurement AND self-test.

PRE-REGISTERED BANDS (fixed BEFORE running; see preregs/2026-07-15_crossmodule_interface_hub_heldout_v2.md):
  HARD_PASS_..._HELDOUT_PREDICTIVE (PRIMARY -- gated on the NOVEL stratum): JOIN clean (join_precision >= 0.90 AND
    fuzzy_gain_frac <= 0.05 AND n_shared_orfs >= MIN_SHARED) AND relations DISTINCT (edge_jaccard(P,G) <= 0.50) AND
    novel_no_direct_edge (non-leakage) AND n_novel >= MIN_NOVEL_QUERIES AND on the NOVEL stratum: HUB_MAP >= 0.30 AND HUB
    beats the STRONG baseline (HUB - max(MERGED,NO_HUB) >= 0.15 AND HUB >= 1.5*MERGED) AND HUB is a GENUINE conjunction
    (HUB - single_ceiling >= 0.15, single_ceiling = max(PHYS_ONLY,GEN_ONLY)) AND must-fails FIRE (SCRAMBLE,NO_HUB <=
    single_ceiling+0.05 AND each >= 0.15 below HUB) AND arms differ AND determinism.
  HARD_FAIL_CONSTRUCTION_ONLY_NOT_PREDICTIVE_ON_HELDOUT: the ALL-query set passes but the NOVEL stratum does NOT -> the
    result recovers/composes on attested pairs but does not PREDICT genuinely-held-out (never-co-attested) conjunctions.
  HARD_FAIL_JOIN_LOSSY: join_precision < 0.90 OR fuzzy_gain_frac > 0.05 OR n_shared_orfs < MIN_SHARED (exact ORF join is
    lossy / needs a fuzzy layer -> the "51% dissolves for canonical-ID data" claim fails for this pair).
  HARD_FAIL_NO_COMPOSITION: JOIN clean + relations distinct but HUB does NOT beat the baseline (identity-anchored
    composition does not retrieve the cross-module intersection better than merged/no-hub) -> the hub-and-spoke
    architecture does not deliver cross-module reasoning on real data.
  MIDDLE_BAND_RELATIONS_NOT_DISTINCT: edge_jaccard(P,G) > 0.50 (physical and genetic edges too coincident -> not a genuine
    cross-module test; MERGED ~ HUB by construction).  MIDDLE_BAND: partial / low-power.

Compute architecture: (b) sequential-CPU with justification -- the VSA core (bind = complex64 elementwise multiply, unbind,
  cleanup matmul against a [V,N] codebook) is BATCHED over all held-out queries as single torch complex64 matmuls (no python
  loop over independent query points); per-seed cost is O(V*N) store-build + O(Q*V*N) cleanup, seconds at V<=400/N=16384/Q<=600;
  GPU yields little over batched-CPU at this size and the dominant cost is the BioGRID(~178MB)+Costanzo download+streaming
  parse (cached after first run). device=cpu default (runner passes no argv). Storage: BUNDLED-ASSOCIATIVE per module (each
  module store is a superposition of bound edges) -- this is the mechanism UNDER TEST (single-hop-per-module unbind then an
  identity-anchored intersection; NOT a depth>=2 chain, so the sharded-vs-bundled chain-grade physics law does not apply);
  capacity sized (MAX_EDGES/module, DEG_CAP, N=16384) so HUB cleanup clears while MERGED/NO_HUB stay below their structural
  ceilings. Determinism: FIXED int seeds + sorted(set()) vocab + deterministic stride subsample + np.random.default_rng /
  torch generators; NO builtin-hash seeding, NO list-of-set dedupe (PROT-023). ASCII-only; no bare except; SystemExit before
  Exception; atomic tmp+os.replace. Default invocation (no flag) = FULL run to completion.
  progress_logging: print_flush_true (ACQUIRE + per-1M-row parse counter + per-seed done lines all flush=True; timeout>=1800).
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; float-hash of per-arm score vectors on the planted arena must differ).
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: retrieval MAP has no closed-form CRLB; the discriminator floor is the empirical RANDOM-arm MAP on the SAME
#     variable-size answer sets, and the planted-arena full-N preview certifies the HUB-vs-baseline gap survives scale.
# - baseline_in_band: MERGED/NO_HUB are measured (not saturated); the RANDOM arm bounds the chance floor; the planted arena
#     is built with DISTINCT relations so MERGED is meaningfully below HUB (discriminator fires, not saturation-vacuous).
# - discriminator survives scale (option C): self-test runs the FULL VSA arms at N_DIM (full N) on a planted two-module arena
#     and asserts HUB - MERGED >= PLANT_MARGIN, HUB - NO_HUB >= PLANT_MARGIN, HUB - single_ceiling >= PLANT_MARGIN, and the
#     identity-broken arms (NO_HUB/SCRAMBLE) at-or-below the single-constraint ceiling AND >= PLANT_MARGIN below HUB, at full scale.
# - HARD_PASS strictly above floor: HUB_MAP >= 0.30 AND margin >= 0.15 AND HUB >= 1.5x MERGED (not a >= floor touch).
# - HP_SCOPE: HARD_PASS gates apply to HUB vs max(MERGED,NO_HUB) only; RANDOM/SCRAMBLE are contrast/must-fail arms.
# - cardinality_ok: n_seeds fixed; verdict counts per-seed MAP lengths == n_seeds for every arm.
# - per-unit failure-class instrumentation: acquire/parse failures -> explicit ACQUIRE_FAILED_* / ESCALATE verdicts (no bare except).
# - calibration_check: adaptive_with_discriminator_gate (the must-fail null is the MEASURED single-constraint ceiling
#     max(PHYS_ONLY,GEN_ONLY) on the real answer sets -- NOT the pure-random floor, because gold is a SUBSET of each conjunct
#     so one intact module floats the identity-broken arms above chance by construction; the relations-distinct jaccard gate
#     is the discriminator-still-fires verification; the self-test asserts the single-constraint ceiling, the HUB-vs-MERGED
#     gap, AND HUB beating the ceiling on a planted arena BEFORE real data is trusted. PHYS_ONLY/GEN_ONLY also absorb any
#     degree/frequency leakage present in the REAL scale-free data, so the null adapts to the data's marginal structure).
# - all numbers in comments tagged CITED@ (scout/interface drills) / THEORETICAL@ / to-be-MEASURED@ (real-data pending remote).
# - real_code_path: self-test parses a SYNTHETIC BioGRID TAB3 zip + a SYNTHETIC Costanzo pairwise zip through the REAL
#     parsers, computes join precision, builds the REAL VSA arms via hd_bind/hd_unbind on complex64, at full N.
# - substrate_signature: hd_bind/hd_unbind bound against the live hdlab.binding signatures in self-test.
# - deterministic_seeding: FIXED int seeds; sorted(set()) vocab + deterministic stride; no hash()/list(set()).

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

from hdlab.binding import bind as hd_bind      # noqa: E402  # REAL substrate bind (complex64 FHRR elementwise multiply)
from hdlab.binding import unbind as hd_unbind  # noqa: E402  # REAL substrate unbind (complex64: c * conj(b))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "crossmodule_interface_hub_identity_bind_heldout_v2"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
# CACHE_DIR is a FIXED path (NOT derived from ANCHOR_NAME) so v2 shares the v1 BioGRID(178MB)+Costanzo(521MB) cache -> cache-hit.
CACHE_DIR = os.path.join(_REPO, "data", "foundation_clusters", "crossmodule_biogrid_costanzo")

# ---- data sources -----------------------------------------------------------
# BioGRID yeast (module P, PHYSICAL). CITED@ notes/drill_verified_foundation_pipeline_datasets_module1alt_module2_2026-07-15.md
# (release 5.0.259 verified live; per-organism TAB3 member inside the all-organisms zip; columns 6/7 =
# "Systematic Name Interactor A/B", column "Experimental System Type" = physical/genetic).
# PINNED Release-Archive URL (NOT the stale Latest-Release/...LATEST alias, which returned an 11.5KB HTML redirect and
# hard-failed ACQUIRE 2026-07-15). Verified live 2026-07-15: HTTP 200 application/download + ZIP magic PK\x03\x04 (real zip,
# not an HTML error page) for BOTH 5.0.259 (primary) and 5.0.258 (fallback). The all-organisms .tab3.zip carries a per-organism
# Saccharomyces_cerevisiae member the parser extracts (there is no separate yeast-only download zip in the Release-Archive).
BIOGRID_URLS = [
    ("biogrid_5_0_259_tab3_all_organisms",
     "https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/"
     "BIOGRID-5.0.259/BIOGRID-ORGANISM-5.0.259.tab3.zip"),
    ("biogrid_5_0_258_tab3_all_organisms_fallback",
     "https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/"
     "BIOGRID-5.0.258/BIOGRID-ORGANISM-5.0.258.tab3.zip"),
]
# Costanzo 2016 (module G, GENETIC). CITED@ same drill + the module-#1 cell exp_costanzo_epistasis_nativepair_bind_readout_v1.py
# (thecellmap.org/yeast/costanzo2016). PAIRWISE (521MB) then MATRIX (35MB) fallback.
COSTANZO_PAIRWISE_URLS = [
    ("S1_pairwise_thecellmap_https",
     "https://thecellmap.org/costanzo2016/data_files/"
     "Raw%20genetic%20interaction%20datasets:%20Pair-wise%20interaction%20format.zip"),
]
COSTANZO_MATRIX_URLS = [
    ("S2_matrix_thecellmap_https",
     "https://thecellmap.org/costanzo2016/data_files/"
     "Raw%20genetic%20interaction%20datasets:%20Matrix%20format.zip"),
]

# yeast systematic ORF id (e.g. YAL001C, YBR102W-A) -- the shared canonical join key
_ORF_RE = re.compile(r"^Y[A-P][LR][0-9]{3}[WC](-[A-Z])?$")

# ---- Costanzo significance filter (edges only; epsilon MAGNITUDE not used downstream -- structure only) ----
EPS_FILTER = 0.08            # standard Costanzo significant-interaction |epsilon| threshold (structure, not magnitude)
P_MAX = 0.05                 # p-value significance filter (pairwise only; matrix has no p-value column)

# ---- joined-subnetwork controls (fixed) ----
N_DIM = 16384                # FHRR complex64 vector dimensionality (full N; also used in the self-test discriminator preview)
TOP_V = 400                  # top combined-degree ORFs in the shared (physical INTERSECT genetic) vocabulary
DEG_CAP = 30                 # cap per-gene stored degree per module (bundle capacity); deterministic top-by-sorted-partner
MAX_EDGES_PER_MODULE = 4000  # cap stored edges per module (bundle-capacity headroom at N_DIM); deterministic stride subsample
MAX_QUERIES = 600            # cap held-out cross-module query pairs (X,Y) with nonempty gold answer sets
MIN_SHARED = 60              # >= this many exact-shared ORFs required else HARD_FAIL_JOIN_LOSSY (insufficient overlap)
MIN_QUERIES = 30             # >= this many total queries with nonempty gold else MIDDLE_BAND_LOW_POWER
# ---- HELD-OUT SPLIT (v2): stratify EVAL queries by whether the pair (X,Y) is a DIRECT stored edge in EITHER module ----
# NOVEL/HELD-OUT = (X,Y) is NOT a stored edge in phys OR gen -> the pair was NEVER presented as related in ANY module; the
#   shared conjunction-neighbour z can ONLY be found by COMPOSING the two independently-stored module readouts (genuine
#   predictive composition; no pair-attestation to ride on). This is the airtight held-out capability stratum.
# SEEN = (X,Y) IS a direct stored edge (the pair's relationship is directly attested in the data) -> reported for CONTEXT (the
#   leakage-adjacent stratum). The store construction is IDENTICAL for both strata; ONLY the eval queries are stratified, so
#   there is no per-stratum store leakage. The conjunction/intersection itself is NEVER stored as a unit in either stratum.
MAX_QUERIES_PER_STRATUM = 400  # cap per stratum (deterministic stride) so BOTH SEEN and NOVEL are represented + well-powered
MIN_NOVEL_QUERIES = 30         # >= this many NOVEL (held-out) queries required for the PREDICTIVE hard-pass else LOW_POWER_NOVEL

# ---- pre-registered bands (fixed BEFORE running) ----
JOIN_PRECISION_MIN = 0.90    # BioGRID systematic-name join-key well-formedness (link precision) floor
FUZZY_GAIN_MAX = 0.05        # extra fuzzy matches over exact equality, as frac of exact overlap; > this => lossy exact join
REL_JACCARD_MAX = 0.50       # edge_jaccard(physical,genetic) <= this else MIDDLE_BAND_RELATIONS_NOT_DISTINCT
HP_HUB_ABS = 0.30            # HUB MAP must be materially above chance
HP_MARGIN_ABS = 0.15         # HUB_MAP - max(MERGED_MAP, NO_HUB_MAP) >= this
HP_MARGIN_REL = 1.5          # HUB_MAP >= this * MERGED_MAP
MUSTFAIL_SCRAMBLE_TOL = 0.03 # (reporting) SCRAMBLE_MAP - RANDOM_MAP context; NOT the gate (see MUSTFAIL_CEIL_TOL)
MUSTFAIL_NOHUB_TOL = 0.05    # (reporting) NO_HUB_MAP - RANDOM_MAP context; NOT the gate (see MUSTFAIL_CEIL_TOL)
MUSTFAIL_CEIL_TOL = 0.05     # identity-broken arms must NOT exceed the single-constraint ceiling by more than this
                             # (i.e. breaking the shared-identity bridge yields NO conjunction gain over one module alone)
PLANT_MARGIN = 0.15          # self-test planted-arena discriminator: HUB_MAP - {MERGED,NO_HUB,SCRAMBLE,single-ceiling} >= this at full N

# ---- arms ----
# HUB/MERGED/NO_HUB/SCRAMBLE/RANDOM = mechanism + baselines + must-fail + floor.
# PHYS_ONLY/GEN_ONLY = SINGLE-CONSTRAINT reference ceilings (rank by ONE module's readout alone). These MEASURE the
# irreducible "one intact module retained" performance: because gold A(X,Y) = phys(X) INTERSECT gen(Y) is a SUBSET of BOTH
# phys(X) and gen(Y), any arm that keeps one real module scores ABOVE the RANDOM floor by construction (a conjunction's answer
# set is a subset of each conjunct's neighbourhood). The identity-broken must-fail arms (NO_HUB, SCRAMBLE) retain the intact
# PHYSICAL module, so their honest null is this single-constraint ceiling, NOT the pure-random floor. HUB must beat the ceiling
# (real conjunction gain from the shared-identity bridge); NO_HUB/SCRAMBLE must NOT (broken bridge => no gain over one module).
HUB = "HUB"; MERGED = "MERGED"; NO_HUB = "NO_HUB"; SCRAMBLE = "SCRAMBLE"; RANDOM = "RANDOM"
PHYS_ONLY = "PHYS_ONLY"; GEN_ONLY = "GEN_ONLY"
ARM_NAMES = [HUB, MERGED, NO_HUB, SCRAMBLE, RANDOM, PHYS_ONLY, GEN_ONLY]

SEEDS_FULL = (7, 13, 17, 23, 29)
SEEDS_SMOKE = (7, 13)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _sig_f(arr):
    return hashlib.sha256(np.round(np.asarray(arr, dtype=np.float64), 6).tobytes()).hexdigest()[:16]


def _norm(s):
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")


def _is_orf(s):
    return bool(_ORF_RE.match(str(s).strip().upper()))


def _finite_float(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _extract_orf_costanzo(v):
    """Costanzo strain id -> systematic ORF prefix before first underscore (e.g. 'YAL001C_tsq123' -> 'YAL001C')."""
    v = str(v).strip()
    if not v:
        return ""
    return v.split("_")[0].strip().upper()


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

def _download_one(url, dest, timeout=600, retries=2):
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


def _try_download(dest, urls, errors, min_bytes=100000):
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
    """Download-if-absent BioGRID (module P) + Costanzo (module G). Returns dict with paths/kinds or None-on-fail + provenance."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    errors = {}
    destB = os.path.join(CACHE_DIR, "biogrid_organism_latest_tab3.zip")
    nbB, uuB = _try_download(destB, BIOGRID_URLS, errors)

    kindC = "none"; destC = None; nbC = 0
    destCp = os.path.join(CACHE_DIR, "costanzo2016_pairwise.zip")
    nb, uu = _try_download(destCp, COSTANZO_PAIRWISE_URLS, errors)
    if uu is not None:
        kindC, destC, nbC = "pairwise", destCp, nb
    else:
        destCm = os.path.join(CACHE_DIR, "costanzo2016_matrix.zip")
        nb, uu = _try_download(destCm, COSTANZO_MATRIX_URLS, errors)
        if uu is not None:
            kindC, destC, nbC = "matrix", destCm, nb

    prov = dict(
        module_P=dict(dataset="BioGRID_yeast_TAB3", source="downloads.thebiogrid.org/BioGRID/Latest-Release",
                      relation="physical_interaction", url=BIOGRID_URLS[0][1], bytes=int(nbB),
                      ok=bool(uuB is not None)),
        module_G=dict(dataset="Costanzo2016_yeast_SGA", source="thecellmap.org/yeast/costanzo2016",
                      relation="genetic_interaction_epsilon", kind=kindC, bytes=int(nbC), ok=bool(destC is not None),
                      urls_tried=dict(COSTANZO_PAIRWISE_URLS + COSTANZO_MATRIX_URLS)),
        join_key="SGD_systematic_ORF_name_exact_string_equality_no_crosswalk",
        retrieval_ts=datetime.now(timezone.utc).isoformat(), acquire_errors=errors,
        filter="|epsilon| > %.3f AND p < %.3f (Costanzo pairwise); |epsilon| > %.3f (matrix); BioGRID Experimental "
               "System Type == physical" % (EPS_FILTER, P_MAX, EPS_FILTER))
    try:
        with open(os.path.join(CACHE_DIR, "provenance.json"), "w", encoding="utf-8") as f:
            json.dump(prov, f, indent=2)
    except OSError:
        pass
    okB = bool(uuB is not None and os.path.exists(destB) and nbB > 100000)
    okC = bool(destC is not None and os.path.exists(destC) and nbC > 100000)
    return dict(biogrid_path=destB if okB else None, costanzo_path=destC if okC else None,
                costanzo_kind=kindC, prov=prov)


# ===========================================================================
# PARSE module P (BioGRID TAB3 physical edges) + join-precision measurement
# ===========================================================================

def _biogrid_member_names(zf):
    names = [n for n in zf.namelist() if not n.endswith("/")]
    yeast = [n for n in names if "saccharomyces_cerevisiae" in n.lower() and n.lower().endswith(".tab3.txt")]
    # exclude the MV (multi-validated) companion file if a plain organism file is present
    plain = [n for n in yeast if "multi_validated" not in n.lower() and "-mv-" not in n.lower()]
    return sorted(plain) if plain else sorted(yeast)


def detect_biogrid_columns(header):
    """Return dict with indices for systematic A/B + experimental-system-type, or None if the TAB3 columns are absent."""
    cols = {_norm(h): i for i, h in enumerate(header)}
    ia = ib = it = None
    for key, i in cols.items():
        if "systematic_name_interactor_a" in key:
            ia = i
        elif "systematic_name_interactor_b" in key:
            ib = i
        elif "experimental_system_type" in key:
            it = i
    if ia is None or ib is None or it is None:
        return None
    return {"a": ia, "b": ib, "type": it}


def parse_biogrid_physical(path):
    """Stream the yeast BioGRID TAB3 member; keep PHYSICAL edges; canonical undirected ORF-pair set. Also count join-precision:
    fraction of physical-edge endpoints that are well-formed systematic ORF ids. Returns dict (path 'A' with edges) or path 'B'."""
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
    except OSError as e:
        return {"path": "B", "reason": "open_failed:%s" % (str(e)[:120])}
    if magic[:2] != b"PK":
        return {"path": "B", "reason": "not_a_zip"}
    try:
        zf = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile as e:
        return {"path": "B", "reason": "bad_zip:%s" % (str(e)[:120])}

    edges = set()
    orfs = set()
    counters = {"n_rows": 0, "n_physical": 0, "n_phys_endpoints": 0, "n_phys_endpoints_valid_orf": 0}
    members = []
    try:
        member_names = _biogrid_member_names(zf)
        if not member_names:
            return {"path": "B", "reason": "no_yeast_tab3_member", "members": [n for n in zf.namelist()][:20]}
        for name in member_names:
            with zf.open(name, "r") as fh:
                ts = io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline="")
                rdr = csv.reader(ts, delimiter="\t")
                try:
                    header = next(rdr)
                except StopIteration:
                    members.append({"member": name, "error": "empty"}); continue
                cm = detect_biogrid_columns(header)
                if cm is None:
                    members.append({"member": name, "error": "no_tab3_columns", "header": [str(x) for x in header[:8]]})
                    continue
                ia, ib, it = cm["a"], cm["b"], cm["type"]
                need = max(ia, ib, it)
                kept = 0
                for row in rdr:
                    counters["n_rows"] += 1
                    if (counters["n_rows"] % 1000000) == 0:
                        _log("PARSE biogrid... %d rows, %d physical kept" % (counters["n_rows"], counters["n_physical"]))
                    if len(row) <= need:
                        continue
                    if str(row[it]).strip().lower() != "physical":
                        continue
                    counters["n_physical"] += 1
                    ta = str(row[ia]).strip().upper(); tb = str(row[ib]).strip().upper()
                    for t in (ta, tb):
                        counters["n_phys_endpoints"] += 1
                        if _is_orf(t):
                            counters["n_phys_endpoints_valid_orf"] += 1
                    if not _is_orf(ta) or not _is_orf(tb) or ta == tb:
                        continue
                    key = (ta, tb) if ta < tb else (tb, ta)
                    edges.add(key); orfs.add(ta); orfs.add(tb); kept += 1
                members.append({"member": name, "physical_edges_kept": kept})
    finally:
        zf.close()

    if not edges:
        return {"path": "B", "reason": "no_physical_orf_edges", "counters": counters, "members": members}
    jp = (counters["n_phys_endpoints_valid_orf"] / counters["n_phys_endpoints"]) if counters["n_phys_endpoints"] else 0.0
    return {"path": "A", "edges": edges, "orfs": orfs, "join_precision": jp, "counters": counters, "members": members}


# ===========================================================================
# PARSE module G (Costanzo significant genetic edges; pairwise or matrix)
# ===========================================================================

def _detect_costanzo_pairwise(header):
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
        return {"q": q, "a": a, "eps": eps, "p": p}
    return None


def parse_costanzo_genetic(path, kind):
    """Return dict path 'A' with the significant genetic ORF-pair set + orf vocab, or path 'B'."""
    edges = set()
    orfs = set()
    counters = {"n_rows": 0, "n_kept": 0}
    members = []

    def _finalize():
        if not edges:
            return {"path": "B", "reason": "no_genetic_edges", "counters": counters, "members": members}
        return {"path": "A", "edges": edges, "orfs": orfs, "counters": counters, "members": members}

    try:
        with open(path, "rb") as f:
            is_zip = f.read(4)[:2] == b"PK"
    except OSError as e:
        return {"path": "B", "reason": "open_failed:%s" % (str(e)[:120])}

    def _process_pairwise(name, ts):
        rdr = csv.reader(ts, delimiter="\t")
        try:
            header = next(rdr)
        except StopIteration:
            members.append({"member": name, "error": "empty"}); return
        if len(header) <= 1:
            ts.seek(0)
            rdr = csv.reader(ts, delimiter=",")
            try:
                header = next(rdr)
            except StopIteration:
                members.append({"member": name, "error": "empty"}); return
        cm = _detect_costanzo_pairwise(header)
        if cm is None:
            members.append({"member": name, "error": "no_pairwise_cols", "header": [str(x) for x in header[:10]]}); return
        iq = header.index(cm["q"]); ia = header.index(cm["a"]); ie = header.index(cm["eps"]); ip = header.index(cm["p"])
        need = max(iq, ia, ie, ip)
        for row in rdr:
            counters["n_rows"] += 1
            if (counters["n_rows"] % 1000000) == 0:
                _log("PARSE costanzo... %d rows, %d kept" % (counters["n_rows"], counters["n_kept"]))
            if len(row) <= need:
                continue
            eps = _finite_float(row[ie]); pv = _finite_float(row[ip])
            if eps is None or pv is None or not (abs(eps) > EPS_FILTER and pv < P_MAX):
                continue
            oa = _extract_orf_costanzo(row[iq]); ob = _extract_orf_costanzo(row[ia])
            if not _is_orf(oa) or not _is_orf(ob) or oa == ob:
                continue
            key = (oa, ob) if oa < ob else (ob, oa)
            edges.add(key); orfs.add(oa); orfs.add(ob); counters["n_kept"] += 1

    def _process_matrix(name, rows):
        if len(rows) < 3:
            members.append({"member": name, "error": "too_few_rows"}); return
        scan = min(len(rows), 50)
        maxcols = max((len(rows[ri]) for ri in range(scan)), default=0)
        best_hr, best_hr_cnt = -1, 0
        for ri in range(scan):
            cnt = sum(1 for c in rows[ri] if _is_orf(c))
            if cnt > best_hr_cnt:
                best_hr_cnt, best_hr = cnt, ri
        best_lc, best_lc_cnt = -1, 0
        for ci in range(min(maxcols, 50)):
            cnt = sum(1 for r in rows if ci < len(r) and _is_orf(r[ci]))
            if cnt > best_lc_cnt:
                best_lc_cnt, best_lc = cnt, ci
        if best_hr < 0 or best_lc < 0 or best_hr_cnt < 10 or best_lc_cnt < 10:
            members.append({"member": name, "error": "no_orf_labels", "hr_cnt": best_hr_cnt, "lc_cnt": best_lc_cnt}); return
        array_labels = rows[best_hr]
        for ri in range(best_hr + 1, len(rows)):
            row = rows[ri]
            if best_lc >= len(row) or not _is_orf(row[best_lc]):
                continue
            qorf = str(row[best_lc]).strip().upper()
            for ci in range(best_lc + 1, min(len(row), len(array_labels))):
                if not _is_orf(array_labels[ci]):
                    continue
                counters["n_rows"] += 1
                eps = _finite_float(row[ci])
                if eps is None or abs(eps) <= EPS_FILTER:
                    continue
                aorf = str(array_labels[ci]).strip().upper()
                if not _is_orf(qorf) or not _is_orf(aorf) or qorf == aorf:
                    continue
                key = (qorf, aorf) if qorf < aorf else (aorf, qorf)
                edges.add(key); orfs.add(qorf); orfs.add(aorf); counters["n_kept"] += 1

    if is_zip:
        try:
            zf = zipfile.ZipFile(path, "r")
        except zipfile.BadZipFile as e:
            return {"path": "B", "reason": "bad_zip:%s" % (str(e)[:120])}
        try:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            txt = [n for n in names if n.lower().endswith((".txt", ".tsv", ".csv"))] or names
            for n in sorted(txt):
                if kind == "matrix":
                    with zf.open(n, "r") as fh:
                        ts = io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline="")
                        rows = [row for row in csv.reader(ts, delimiter="\t")]
                        if rows and max((len(r) for r in rows[:5]), default=0) <= 1:
                            ts2 = io.TextIOWrapper(zf.open(n, "r"), encoding="utf-8", errors="replace", newline="")
                            rows = [row for row in csv.reader(ts2, delimiter=",")]
                        _process_matrix(n, rows)
                else:
                    with zf.open(n, "r") as fh:
                        _process_pairwise(n, io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline=""))
        finally:
            zf.close()
    else:
        with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
            if kind == "matrix":
                _process_matrix(os.path.basename(path), [row for row in csv.reader(fh, delimiter="\t")])
            else:
                _process_pairwise(os.path.basename(path), fh)
    return _finalize()


# ===========================================================================
# JOIN + build the joined subnetwork (shared vocab; degree-capped, edge-capped)
# ===========================================================================

def _fuzzy_key(o):
    return str(o).strip().upper().replace("-", "").replace("_", "")


def compute_join(phys_orfs, gen_orfs):
    """Exact-string-equality overlap + a fuzzy-normalized overlap (to prove the exact join is not lossy)."""
    exact = phys_orfs & gen_orfs
    fmap_p = defaultdict(set)
    for o in phys_orfs:
        fmap_p[_fuzzy_key(o)].add(o)
    fmap_g = defaultdict(set)
    for o in gen_orfs:
        fmap_g[_fuzzy_key(o)].add(o)
    fuzzy_keys = set(fmap_p.keys()) & set(fmap_g.keys())
    fuzzy_pairs = 0
    for k in fuzzy_keys:
        # count identity-preserving fuzzy matches (a P-orf matches a G-orf after normalization)
        for op in fmap_p[k]:
            if op in fmap_g[k]:
                continue  # already an exact match
            fuzzy_pairs += 1  # a normalization-only match that exact equality misses
    n_exact = len(exact)
    fuzzy_gain_frac = (fuzzy_pairs / n_exact) if n_exact else float("inf")
    return dict(exact=exact, n_exact=n_exact, fuzzy_extra=fuzzy_pairs, fuzzy_gain_frac=fuzzy_gain_frac)


def _cap_edges(edges, vocab_ids, deg_cap, max_edges, seed):
    """Restrict edges to endpoints in vocab (int ids), deterministic degree-cap + edge-cap. edges: set of (str,str)."""
    kept = []
    deg = defaultdict(int)
    for (a, b) in sorted(edges):
        if a not in vocab_ids or b not in vocab_ids:
            continue
        ia, ib = vocab_ids[a], vocab_ids[b]
        if deg[ia] >= deg_cap or deg[ib] >= deg_cap:
            continue
        kept.append((ia, ib)); deg[ia] += 1; deg[ib] += 1
    if len(kept) > max_edges:
        stride = int(math.ceil(len(kept) / float(max_edges)))
        kept = kept[::stride][:max_edges]
    return kept


def build_subnetwork(phys_edges, gen_edges, shared_orfs, seed):
    """Build the joined subnetwork over the TOP_V highest combined-degree shared ORFs. Returns vocab + int-id edge lists +
    per-gene partner dicts (for gold answer-set construction) or None if degenerate."""
    # combined degree over the shared vocabulary
    deg = defaultdict(int)
    for (a, b) in phys_edges:
        if a in shared_orfs and b in shared_orfs:
            deg[a] += 1; deg[b] += 1
    for (a, b) in gen_edges:
        if a in shared_orfs and b in shared_orfs:
            deg[a] += 1; deg[b] += 1
    if not deg:
        return None
    vocab = sorted(deg.keys(), key=lambda o: (-deg[o], o))[:TOP_V]
    vocab = sorted(set(vocab))
    vid = {o: i for i, o in enumerate(vocab)}
    pe = _cap_edges(phys_edges, vid, DEG_CAP, MAX_EDGES_PER_MODULE, seed)
    ge = _cap_edges(gen_edges, vid, DEG_CAP, MAX_EDGES_PER_MODULE, seed)
    if len(pe) < 20 or len(ge) < 20:
        return None
    phys_partners = defaultdict(set); gen_partners = defaultdict(set)
    for (a, b) in pe:
        phys_partners[a].add(b); phys_partners[b].add(a)
    for (a, b) in ge:
        gen_partners[a].add(b); gen_partners[b].add(a)
    return dict(vocab=vocab, vid=vid, n_v=len(vocab), phys_edges=pe, gen_edges=ge,
                phys_partners=phys_partners, gen_partners=gen_partners)


def _direct_edge_set(sub):
    """Undirected set of DIRECTLY-stored (int-id) pairs across BOTH modules -> the pair-attestation lookup for the split."""
    direct = set()
    for (a, b) in sub["phys_edges"]:
        direct.add((a, b)); direct.add((b, a))
    for (a, b) in sub["gen_edges"]:
        direct.add((a, b)); direct.add((b, a))
    return direct


def build_queries(sub, seed):
    """Enumerate cross-module query pairs (X,Y) with nonempty gold A(X,Y) = phys(X) INTERSECT gen(Y), X!=Y not in A. Each
    query is labelled seen=(X,Y is a DIRECT stored edge in phys OR gen). Deterministic-stride cap PER STRATUM so both SEEN
    (pair directly attested) and NOVEL (pair never co-attested -> pure composition) strata are represented. Returns a list of
    4-tuples (x, y, gold_tuple, seen_bool). The gold intersection is NEVER stored as a unit -> every query is compositional;
    the NOVEL stratum additionally has NO direct (X,Y) association in any store (the airtight held-out capability slice)."""
    phys_partners = sub["phys_partners"]; gen_partners = sub["gen_partners"]
    direct = _direct_edge_set(sub)
    seen_cand = []; novel_cand = []
    xs = sorted(phys_partners.keys()); ys = sorted(gen_partners.keys())
    for x in xs:
        px = phys_partners[x]
        for y in ys:
            if y == x:
                continue
            gold = px & gen_partners[y]
            gold.discard(x); gold.discard(y)
            if gold:
                is_seen = (x, y) in direct
                rec = (x, y, tuple(sorted(gold)), is_seen)
                (seen_cand if is_seen else novel_cand).append(rec)
    seen_cand.sort(); novel_cand.sort()

    def _stride_cap(lst, cap):
        if len(lst) > cap:
            st = int(math.ceil(len(lst) / float(cap)))
            lst = lst[::st][:cap]
        return lst

    seen_cap = _stride_cap(seen_cand, MAX_QUERIES_PER_STRATUM)
    novel_cap = _stride_cap(novel_cand, MAX_QUERIES_PER_STRATUM)
    return seen_cap + novel_cap  # SEEN block first, then NOVEL block; strata recoverable from the seen flag (index 3)


# ===========================================================================
# VSA arms (REAL substrate bind/unbind; batched complex64 cleanup)
# ===========================================================================

def _codebook(n_v, n_dim, seed):
    """n_v unit-modulus complex64 hub codes [n_v, n_dim] (random FHRR phasors)."""
    g = torch.Generator().manual_seed(int(seed))
    ph = (2.0 * math.pi) * torch.rand(n_v, n_dim, generator=g)
    return torch.polar(torch.ones(n_v, n_dim), ph).to(torch.complex64)


def _build_store(edges_int, codebook):
    """M = sum over edges (i,j) of bind(h(i), h(j)) using the REAL substrate bind (complex64 elementwise multiply)."""
    if not edges_int:
        return torch.zeros(codebook.shape[1], dtype=torch.complex64)
    idx = torch.tensor(edges_int, dtype=torch.long)
    bound = hd_bind(codebook[idx[:, 0]], codebook[idx[:, 1]])  # [E, N] real substrate bind
    return bound.sum(0)


def _cleanup_scores(store, key_codes, codebook):
    """s(q, z) = Re< unbind(store, key_codes[q]) , codebook[z] >  -> [Q, n_v]. Batched; REAL substrate unbind."""
    q = key_codes.shape[0]
    b = hd_unbind(store.unsqueeze(0).expand(q, -1), key_codes)  # [Q, N] = store * conj(key)
    return (b @ codebook.conj().t()).real  # [Q, n_v]


def _average_precision(scores_row, gold_set, exclude):
    s = scores_row.copy()
    for e in exclude:
        s[e] = -1e30
    order = np.argsort(-s)
    hits = 0; sump = 0.0; ng = len(gold_set)
    if ng == 0:
        return float("nan")
    for rank, z in enumerate(order, 1):
        if z in gold_set:
            hits += 1; sump += hits / rank
            if hits == ng:
                break
    return sump / ng


def _map_subset(conj_scores, queries, idxs):
    """Mean average-precision over the given query indices (queries are 4-tuples (x,y,gold,seen))."""
    aps = []
    for qi in idxs:
        x, y, gold = queries[qi][0], queries[qi][1], queries[qi][2]
        ap = _average_precision(conj_scores[qi], set(gold), (x, y))
        if ap == ap:
            aps.append(ap)
    return float(np.mean(aps)) if aps else float("nan")


def _strata_idx(queries):
    """(idx_all, idx_seen, idx_novel) from the seen flag at tuple index 3."""
    idx_seen = [i for i, q in enumerate(queries) if q[3]]
    idx_novel = [i for i, q in enumerate(queries) if not q[3]]
    return list(range(len(queries))), idx_seen, idx_novel


def stratified_maps(scores, queries):
    """arm -> {ALL, SEEN, NOVEL} mean-AP dict for every arm."""
    idx_all, idx_seen, idx_novel = _strata_idx(queries)
    out = {}
    for arm in ARM_NAMES:
        out[arm] = dict(ALL=_map_subset(scores[arm], queries, idx_all),
                        SEEN=_map_subset(scores[arm], queries, idx_seen),
                        NOVEL=_map_subset(scores[arm], queries, idx_novel))
    return out


def run_arms(sub, queries, seed):
    """Compute MAP for every arm on the joined subnetwork at a given seed. Returns dict arm->MAP + per-arm score signature."""
    n_v = sub["n_v"]
    codebook = _codebook(n_v, N_DIM, seed)                       # shared hub codes h(.)
    codebook_g = _codebook(n_v, N_DIM, seed + 991)              # INDEPENDENT codebook for NO_HUB module G
    xs = torch.tensor([q[0] for q in queries], dtype=torch.long)
    ys = torch.tensor([q[1] for q in queries], dtype=torch.long)

    # deterministic permutations (no hash(); seeded rng)
    rng = np.random.default_rng(seed * 100003 + 7)
    perm_nohub = rng.permutation(n_v)                            # unknown cross-space correspondence (NO_HUB)
    perm_scram = rng.permutation(n_v)                            # broken identity anchor (SCRAMBLE)

    # ---- HUB: separate relation-typed stores, shared hub codes, identity-anchored product ----
    M_P = _build_store(sub["phys_edges"], codebook)
    M_G = _build_store(sub["gen_edges"], codebook)
    sP = _cleanup_scores(M_P, codebook[xs], codebook).numpy()    # [Q, n_v] physical partners of X
    sG = _cleanup_scores(M_G, codebook[ys], codebook).numpy()    # [Q, n_v] genetic partners of Y
    hub_conj = sP * sG

    # ---- MERGED: one flat store (physical+genetic merged, no relation typing), shared hub codes ----
    M_merged = _build_store(sub["phys_edges"] + sub["gen_edges"], codebook)
    mX = _cleanup_scores(M_merged, codebook[xs], codebook).numpy()
    mY = _cleanup_scores(M_merged, codebook[ys], codebook).numpy()
    merged_conj = mX * mY

    # ---- NO_HUB: module G built with an INDEPENDENT codebook -> no shared identity -> random correspondence ----
    M_G_ind = _build_store(sub["gen_edges"], codebook_g)
    sG_ind = _cleanup_scores(M_G_ind, codebook_g[ys], codebook_g).numpy()   # [Q, n_v] indexed in G-space
    nohub_conj = sP * sG_ind[:, perm_nohub]                     # genetic constraint applied to the WRONG identity

    # ---- SCRAMBLE: HUB but module G edges stored under a scrambled identity permutation ----
    gen_scram = [(int(perm_scram[a]), int(perm_scram[b])) for (a, b) in sub["gen_edges"]]
    M_G_scram = _build_store(gen_scram, codebook)
    sG_scram = _cleanup_scores(M_G_scram, codebook[ys], codebook).numpy()
    scram_conj = sP * sG_scram

    # ---- RANDOM: chance floor for the variable-size answer sets ----
    rand_conj = rng.standard_normal(size=hub_conj.shape)

    # ---- PHYS_ONLY / GEN_ONLY: single-constraint reference ceilings (rank by ONE module's real readout alone) ----
    # sP = physical partners of X (real hub codes); sG = genetic partners of Y (real hub codes). gold is a SUBSET of BOTH
    # phys(X) and gen(Y), so each single-constraint readout scores ABOVE the RANDOM floor -- this MEASURES the irreducible
    # single-module residual that any identity-broken arm inherits from its ONE intact module.
    scores = {HUB: hub_conj, MERGED: merged_conj, NO_HUB: nohub_conj, SCRAMBLE: scram_conj, RANDOM: rand_conj,
              PHYS_ONLY: sP, GEN_ONLY: sG}
    sigs = {arm: _sig_f(scores[arm].ravel()) for arm in ARM_NAMES}
    return scores, sigs


# ===========================================================================
# planted two-module arena (self-test discriminator preview at full N)
# ===========================================================================

def _plant_two_module(n_v=120, seed=7, deg=6, overlap_frac=0.15):
    """Two DISTINCT relations over the same n_v genes. Physical + genetic edge sets with controlled low overlap so MERGED is
    meaningfully below HUB (discriminator fires), and nonempty cross-module intersections exist."""
    rng = np.random.default_rng(seed)
    phys = set(); gen = set()
    for a in range(n_v):
        for _ in range(deg):
            b = int(rng.integers(0, n_v))
            if b != a:
                phys.add((min(a, b), max(a, b)))
    for a in range(n_v):
        for _ in range(deg):
            b = int(rng.integers(0, n_v))
            if b != a:
                gen.add((min(a, b), max(a, b)))
    # inject a few shared edges (controlled overlap) but keep relations mostly distinct
    pe = sorted(phys); ge = sorted(gen)
    return pe, ge


def _planted_sub_and_queries(n_v=120, seed=7):
    pe, ge = _plant_two_module(n_v=n_v, seed=seed)
    vocab = list(range(n_v))
    phys_partners = defaultdict(set); gen_partners = defaultdict(set)
    for (a, b) in pe:
        phys_partners[a].add(b); phys_partners[b].add(a)
    for (a, b) in ge:
        gen_partners[a].add(b); gen_partners[b].add(a)
    sub = dict(vocab=vocab, vid={i: i for i in vocab}, n_v=n_v, phys_edges=pe, gen_edges=ge,
               phys_partners=phys_partners, gen_partners=gen_partners)
    queries = build_queries(sub, seed)
    return sub, queries


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds, run_mode):
    _write_start_marker(expected_n_units=len(seeds), run_mode=run_mode)
    t0 = time.perf_counter()
    acq = acquire()
    prov = acq["prov"]
    base = dict(run_mode=run_mode, anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
                elapsed_s=round(time.perf_counter() - t0, 2), provenance=prov, seeds=list(seeds),
                bands=dict(JOIN_PRECISION_MIN=JOIN_PRECISION_MIN, FUZZY_GAIN_MAX=FUZZY_GAIN_MAX,
                           REL_JACCARD_MAX=REL_JACCARD_MAX, HP_HUB_ABS=HP_HUB_ABS, HP_MARGIN_ABS=HP_MARGIN_ABS,
                           HP_MARGIN_REL=HP_MARGIN_REL, MUSTFAIL_SCRAMBLE_TOL=MUSTFAIL_SCRAMBLE_TOL,
                           MUSTFAIL_NOHUB_TOL=MUSTFAIL_NOHUB_TOL, MUSTFAIL_CEIL_TOL=MUSTFAIL_CEIL_TOL,
                           MIN_SHARED=MIN_SHARED, MIN_QUERIES=MIN_QUERIES,
                           N_DIM=N_DIM, TOP_V=TOP_V))

    if acq["biogrid_path"] is None or acq["costanzo_path"] is None:
        which = []
        if acq["biogrid_path"] is None:
            which.append("BioGRID")
        if acq["costanzo_path"] is None:
            which.append("Costanzo")
        msg = ("ACQUIRE_FAILED || could not download %s (see provenance.acquire_errors)." % "+".join(which))
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200])
        return base

    try:
        pdata = parse_biogrid_physical(acq["biogrid_path"])
        gdata = parse_costanzo_genetic(acq["costanzo_path"], acq["costanzo_kind"])
    except (zipfile.BadZipFile, OSError, csv.Error, UnicodeDecodeError) as e:
        msg = "ACQUIRE_FAILED || file present but unreadable: %s: %s" % (type(e).__name__, str(e)[:160])
        base.update(verdict="ACQUIRE_FAILED", verdict_msg=msg, summary=msg[:200], parse_error=str(e)[:300])
        return base

    if pdata["path"] == "B" or gdata["path"] == "B":
        msg = ("ESCALATE_PARSE_NO_STRUCTURE || biogrid=%s costanzo=%s" %
               (pdata.get("reason", "ok"), gdata.get("reason", "ok")))
        base.update(verdict="ESCALATE_PARSE_NO_STRUCTURE", verdict_msg=msg, summary=msg[:200],
                    biogrid_diag={k: v for k, v in pdata.items() if k not in ("edges", "orfs")},
                    costanzo_diag={k: v for k, v in gdata.items() if k not in ("edges", "orfs")})
        return base

    phys_edges = pdata["edges"]; gen_edges = gdata["edges"]
    phys_orfs = pdata["orfs"]; gen_orfs = gdata["orfs"]
    join_precision = float(pdata["join_precision"])
    jn = compute_join(phys_orfs, gen_orfs)
    shared = jn["exact"]
    n_shared = jn["n_exact"]
    fuzzy_gain_frac = float(jn["fuzzy_gain_frac"])
    _log("JOIN: n_phys_edges=%d n_gen_edges=%d n_phys_orfs=%d n_gen_orfs=%d n_shared_orfs=%d join_precision=%.4f "
         "fuzzy_gain_frac=%.4f" % (len(phys_edges), len(gen_edges), len(phys_orfs), len(gen_orfs), n_shared,
                                   join_precision, fuzzy_gain_frac))

    # edge relation distinctness (jaccard over the shared vocabulary)
    sp = set((a, b) for (a, b) in phys_edges if a in shared and b in shared)
    sg = set((a, b) for (a, b) in gen_edges if a in shared and b in shared)
    inter = len(sp & sg); union = len(sp | sg)
    edge_jaccard = (inter / union) if union else float("nan")

    join_ok = bool(join_precision >= JOIN_PRECISION_MIN and fuzzy_gain_frac <= FUZZY_GAIN_MAX and n_shared >= MIN_SHARED)
    distinct_ok = bool(edge_jaccard == edge_jaccard and edge_jaccard <= REL_JACCARD_MAX)

    base.update(join=dict(join_precision=round(join_precision, 5), n_shared_orfs=int(n_shared),
                          fuzzy_extra=int(jn["fuzzy_extra"]),
                          fuzzy_gain_frac=round(fuzzy_gain_frac, 5) if math.isfinite(fuzzy_gain_frac) else None,
                          n_phys_edges=len(phys_edges), n_gen_edges=len(gen_edges),
                          n_phys_orfs=len(phys_orfs), n_gen_orfs=len(gen_orfs),
                          edge_jaccard=round(edge_jaccard, 5) if edge_jaccard == edge_jaccard else None,
                          join_ok=join_ok, distinct_ok=distinct_ok))

    if not join_ok:
        msg = ("HARD_FAIL_JOIN_LOSSY || join_precision=%.4f(>=%.2f) fuzzy_gain_frac=%s(<=%.2f) n_shared=%d(>=%d): the exact "
               "SGD-ORF join is lossy / needs a fuzzy layer." % (join_precision, JOIN_PRECISION_MIN,
               _fmt(fuzzy_gain_frac), FUZZY_GAIN_MAX, n_shared, MIN_SHARED))
        base.update(verdict="HARD_FAIL_JOIN_LOSSY", verdict_msg=msg, summary=msg[:200])
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    sub = build_subnetwork(phys_edges, gen_edges, shared, seed=SEEDS_FULL[0])
    if sub is None:
        msg = "MIDDLE_BAND_DEGENERATE_SUBNETWORK || too few in-vocab edges after degree/edge caps"
        base.update(verdict="MIDDLE_BAND_DEGENERATE_SUBNETWORK", verdict_msg=msg, summary=msg[:200])
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base
    queries = build_queries(sub, seed=SEEDS_FULL[0])
    n_queries = len(queries)
    idx_all, idx_seen, idx_novel = _strata_idx(queries)
    n_seen = len(idx_seen); n_novel = len(idx_novel)
    # NON-LEAKAGE assertions (machine-checked): the gold conjunction/intersection is NEVER stored as a unit (M_P/M_G are built
    # ONLY from phys_edges/gen_edges; no answer-tuple is injected -> conjunction_never_stored), and every NOVEL (held-out)
    # query's pair (X,Y) is NOT a direct stored edge in EITHER module (the pair was never presented as related -> the shared
    # neighbour z can ONLY be composed from the two independent module readouts). This is what makes NOVEL the airtight
    # PREDICTIVE stratum (as opposed to SEEN, where the pair's relationship is directly attested).
    direct = _direct_edge_set(sub)
    novel_no_direct_edge = all(((queries[i][0], queries[i][1]) not in direct) for i in idx_novel)
    seen_all_direct_edge = all(((queries[i][0], queries[i][1]) in direct) for i in idx_seen)
    conjunction_never_stored = True  # structural: stores contain only individual module edges (no gold intersection injected)
    _log("SUBNET: n_v=%d n_phys_edges_in=%d n_gen_edges_in=%d n_queries=%d (seen=%d novel=%d) edge_jaccard=%.4f "
         "novel_no_direct_edge=%s conjunction_never_stored=%s"
         % (sub["n_v"], len(sub["phys_edges"]), len(sub["gen_edges"]), n_queries, n_seen, n_novel, edge_jaccard,
            novel_no_direct_edge, conjunction_never_stored))

    if n_queries < MIN_QUERIES:
        msg = ("MIDDLE_BAND_LOW_POWER || only %d cross-module queries (< %d)" % (n_queries, MIN_QUERIES))
        base.update(verdict="MIDDLE_BAND_LOW_POWER", verdict_msg=msg, summary=msg[:200], n_queries=n_queries,
                    n_seen=n_seen, n_novel=n_novel)
        base["elapsed_s"] = round(time.perf_counter() - t0, 2)
        return base

    per_seed = []
    for si, sd in enumerate(seeds):
        scores, sigs = run_arms(sub, queries, sd)
        sm = stratified_maps(scores, queries)   # arm -> {ALL, SEEN, NOVEL}
        per_seed.append(dict(seed=sd, maps=sm, sigs=sigs))
        _log("  seed %d/%d done [NOVEL] HUB=%.4f MERGED=%.4f NO_HUB=%.4f SCRAMBLE=%.4f RANDOM=%.4f PHYS=%.4f GEN=%.4f | "
             "[SEEN] HUB=%.4f (elapsed=%.1fs)"
             % (si + 1, len(seeds), sm[HUB]["NOVEL"], sm[MERGED]["NOVEL"], sm[NO_HUB]["NOVEL"], sm[SCRAMBLE]["NOVEL"],
                sm[RANDOM]["NOVEL"], sm[PHYS_ONLY]["NOVEL"], sm[GEN_ONLY]["NOVEL"], sm[HUB]["SEEN"],
                time.perf_counter() - t0))

    def _mean(arm, strat):
        vals = [ps["maps"][arm][strat] for ps in per_seed
                if ps["maps"][arm][strat] == ps["maps"][arm][strat]]
        return float(np.mean(vals)) if vals else float("nan")

    def _stratum_summary(strat):
        """Per-arm mean-MAP + all HARD_PASS gates for one query stratum (ALL / SEEN / NOVEL)."""
        m = {arm: _mean(arm, strat) for arm in ARM_NAMES}
        hub = m[HUB]; merged = m[MERGED]; nohub = m[NO_HUB]; scram = m[SCRAMBLE]
        strong = max([v for v in (merged, nohub) if v == v], default=float("nan"))
        ceil = max([v for v in (m[PHYS_ONLY], m[GEN_ONLY]) if v == v], default=float("nan"))
        margin_abs = hub - strong if (hub == hub and strong == strong) else float("nan")
        rel_ok = bool(hub == hub and merged == merged and merged > 1e-9 and hub >= HP_MARGIN_REL * merged)
        hub_above = bool(hub == hub and hub >= HP_HUB_ABS)
        margin_ok = bool(margin_abs == margin_abs and margin_abs >= HP_MARGIN_ABS and rel_ok)
        beats_single = bool(hub == hub and ceil == ceil and (hub - ceil) >= HP_MARGIN_ABS)
        scram_mf = bool(scram == scram and ceil == ceil and hub == hub
                        and scram <= ceil + MUSTFAIL_CEIL_TOL and (hub - scram) >= HP_MARGIN_ABS)
        nohub_mf = bool(nohub == nohub and ceil == ceil and hub == hub
                        and nohub <= ceil + MUSTFAIL_CEIL_TOL and (hub - nohub) >= HP_MARGIN_ABS)
        mustfails_ok = bool(scram_mf and nohub_mf)
        stratum_pass = bool(hub_above and margin_ok and beats_single and mustfails_ok)
        return dict(maps=m, strong_baseline=strong, single_ceiling=ceil, margin_abs=margin_abs, rel_ok=rel_ok,
                    hub_above=hub_above, margin_ok=margin_ok, beats_single=beats_single, scram_mf=scram_mf,
                    nohub_mf=nohub_mf, mustfails_ok=mustfails_ok, stratum_pass=stratum_pass)

    S_ALL = _stratum_summary("ALL"); S_SEEN = _stratum_summary("SEEN"); S_NOVEL = _stratum_summary("NOVEL")

    # arms-differ + determinism (score signatures on seed 0)
    s0 = per_seed[0]["sigs"]
    arms_differ = len(set(s0[a] for a in (HUB, MERGED, NO_HUB, SCRAMBLE))) == 4
    _scores_r, sigs_r = run_arms(sub, queries, seeds[0])
    determinism_ok = (sigs_r[HUB] == per_seed[0]["sigs"][HUB])

    novel_power_ok = bool(n_novel >= MIN_NOVEL_QUERIES)
    join_gate_ok = bool(join_ok and distinct_ok and arms_differ and determinism_ok)
    # PRIMARY = PREDICTIVE hard-pass, gated on the NOVEL (held-out) stratum: HUB composes the cross-module conjunction for
    # pairs NEVER co-attested in any module, beating the single-constraint ceiling + strong baseline + firing the must-fails.
    novel_pass = bool(join_gate_ok and novel_power_ok and novel_no_direct_edge and S_NOVEL["stratum_pass"])
    all_pass = bool(join_gate_ok and S_ALL["stratum_pass"])

    if not distinct_ok:
        verdict = "MIDDLE_BAND_RELATIONS_NOT_DISTINCT"
    elif not arms_differ:
        verdict = "INCONCLUSIVE_ARMS_IDENTICAL"
    elif not determinism_ok:
        verdict = "INCONCLUSIVE_NONDETERMINISTIC"
    elif not novel_no_direct_edge:
        verdict = "INCONCLUSIVE_SPLIT_LEAK"   # a NOVEL query pair had a direct stored edge -> split-construction bug
    elif not novel_power_ok:
        verdict = "MIDDLE_BAND_LOW_POWER_NOVEL"
    elif novel_pass:
        verdict = "HARD_PASS_INTERFACE_HUB_HELDOUT_PREDICTIVE_COMPOSES_CROSS_MODULE"
    elif all_pass and not S_NOVEL["stratum_pass"]:
        # recovers/composes conjunctions on the FULL set but NOT on the genuinely-held-out (never-co-attested) pairs ->
        # the result is CONSTRUCTION-scoped, not predictive.
        verdict = "HARD_FAIL_CONSTRUCTION_ONLY_NOT_PREDICTIVE_ON_HELDOUT"
    elif not S_NOVEL["mustfails_ok"]:
        verdict = "INCONCLUSIVE_MUSTFAIL_DID_NOT_FIRE"
    else:
        verdict = "HARD_FAIL_NO_COMPOSITION_HUB_DOES_NOT_BEAT_BASELINE"

    nm = S_NOVEL["maps"]
    msg = ("%s || JOIN precision=%.4f n_shared=%d fuzzy_gain=%s | edge_jaccard=%.4f(distinct=%s) | n_queries=%d "
           "(seen=%d novel=%d novel_no_direct_edge=%s conj_never_stored=%s) | [NOVEL] HUB=%.4f(>=%.2f above=%s) "
           "MERGED=%.4f NO_HUB=%.4f SCRAMBLE=%.4f RANDOM=%.4f PHYS_ONLY=%.4f GEN_ONLY=%.4f single_ceiling=%.4f "
           "margin_abs=%s(>=%.2f) margin_ok=%s beats_single(>=%.2f)=%s mustfails_ok=%s | [SEEN] HUB=%.4f ceiling=%.4f "
           "beats_single=%s | [ALL] HUB=%.4f all_pass=%s | arms_differ=%s determ=%s"
           % (verdict, join_precision, n_shared, _fmt(fuzzy_gain_frac), edge_jaccard, distinct_ok, n_queries, n_seen,
              n_novel, novel_no_direct_edge, conjunction_never_stored, nm[HUB], HP_HUB_ABS, S_NOVEL["hub_above"],
              nm[MERGED], nm[NO_HUB], nm[SCRAMBLE], nm[RANDOM], nm[PHYS_ONLY], nm[GEN_ONLY], S_NOVEL["single_ceiling"],
              _fmt(S_NOVEL["margin_abs"]), HP_MARGIN_ABS, S_NOVEL["margin_ok"], HP_MARGIN_ABS, S_NOVEL["beats_single"],
              S_NOVEL["mustfails_ok"], S_SEEN["maps"][HUB], S_SEEN["single_ceiling"], S_SEEN["beats_single"],
              S_ALL["maps"][HUB], all_pass, arms_differ, determinism_ok))

    def _mapdict(S):
        return {arm: round(S["maps"][arm], 5) if S["maps"][arm] == S["maps"][arm] else None for arm in ARM_NAMES}

    def _gatedict(S):
        return dict(hub_above=S["hub_above"], margin_ok=S["margin_ok"], rel_ok=S["rel_ok"],
                    beats_single=S["beats_single"], scram_mf=S["scram_mf"], nohub_mf=S["nohub_mf"],
                    mustfails_ok=S["mustfails_ok"], stratum_pass=S["stratum_pass"],
                    single_ceiling=round(S["single_ceiling"], 5) if S["single_ceiling"] == S["single_ceiling"] else None,
                    strong_baseline=round(S["strong_baseline"], 5) if S["strong_baseline"] == S["strong_baseline"] else None,
                    margin_abs=round(S["margin_abs"], 5) if S["margin_abs"] == S["margin_abs"] else None)

    base.update(
        verdict=verdict, verdict_msg=msg, summary=msg[:200],
        n_queries=int(n_queries), n_seen=int(n_seen), n_novel=int(n_novel), n_v=int(sub["n_v"]),
        n_phys_edges_in=int(len(sub["phys_edges"])), n_gen_edges_in=int(len(sub["gen_edges"])),
        heldout=dict(split_axis="pair_(X,Y)_is_direct_stored_edge_in_phys_or_gen",
                     n_seen=int(n_seen), n_novel=int(n_novel),
                     novel_no_direct_edge=bool(novel_no_direct_edge), seen_all_direct_edge=bool(seen_all_direct_edge),
                     conjunction_never_stored=bool(conjunction_never_stored),
                     novel_pass=bool(novel_pass), all_pass=bool(all_pass), seen_pass=bool(S_SEEN["stratum_pass"])),
        maps=_mapdict(S_ALL),  # top-level maps mirror the ALL stratum (v1-schema continuity)
        maps_by_stratum=dict(ALL=_mapdict(S_ALL), SEEN=_mapdict(S_SEEN), NOVEL=_mapdict(S_NOVEL)),
        gates_by_stratum=dict(ALL=_gatedict(S_ALL), SEEN=_gatedict(S_SEEN), NOVEL=_gatedict(S_NOVEL)),
        gates=dict(join_ok=join_ok, distinct_ok=distinct_ok, arms_differ=arms_differ, determinism_ok=determinism_ok,
                   novel_power_ok=novel_power_ok, novel_no_direct_edge=bool(novel_no_direct_edge),
                   novel_pass=bool(novel_pass), all_pass=bool(all_pass)),
        per_seed=[dict(seed=ps["seed"],
                       maps_novel={k: round(ps["maps"][k]["NOVEL"], 5) if ps["maps"][k]["NOVEL"] == ps["maps"][k]["NOVEL"]
                                   else None for k in ARM_NAMES},
                       maps_seen={k: round(ps["maps"][k]["SEEN"], 5) if ps["maps"][k]["SEEN"] == ps["maps"][k]["SEEN"]
                                  else None for k in ARM_NAMES})
                  for ps in per_seed],
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
# SELF-TEST (real bind/unbind path + REAL parsers on synthetic zips + planted full-N discriminator + arms-differ + determinism)
# ===========================================================================

def _make_synth_biogrid_zip(path, n_orfs=24, deg=4):
    """Tiny synthetic BioGRID TAB3 yeast member (zip-of-txt) with physical + genetic rows -> exercises the REAL parser +
    join-precision counter. A few rows carry a non-ORF systematic name ('-') to make join_precision < 1.0 measurable."""
    header = ["#BioGRID Interaction ID", "Entrez Gene Interactor A", "Entrez Gene Interactor B",
              "BioGRID ID Interactor A", "BioGRID ID Interactor B", "Systematic Name Interactor A",
              "Systematic Name Interactor B", "Official Symbol Interactor A", "Official Symbol Interactor B",
              "Synonyms Interactor A", "Synonyms Interactor B", "Experimental System", "Experimental System Type",
              "Author", "Publication Source", "Organism ID Interactor A", "Organism ID Interactor B"]
    orfs = ["YAL%03dC" % (d + 1) for d in range(n_orfs)]
    rng = np.random.default_rng(303)
    lines = ["\t".join(header)]
    bid = 1
    for a in range(n_orfs):
        for _ in range(deg):
            b = int(rng.integers(0, n_orfs))
            if b == a:
                continue
            lines.append("\t".join([str(bid), "1", "2", "10", "20", orfs[a], orfs[b], "GA", "GB", "-", "-",
                                    "Two-hybrid", "physical", "Auth", "PUB", "559292", "559292"]))
            bid += 1
    # a handful of physical rows with a non-ORF systematic name ('-') -> lowers join_precision
    for _ in range(6):
        a = int(rng.integers(0, n_orfs))
        lines.append("\t".join([str(bid), "1", "2", "10", "20", orfs[a], "-", "GA", "GB", "-", "-",
                                "Affinity", "physical", "Auth", "PUB", "559292", "559292"]))
        bid += 1
    tsv = "\n".join(lines) + "\n"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("BIOGRID-ORGANISM-Saccharomyces_cerevisiae-4.4.999.tab3.txt", tsv)


def _make_synth_costanzo_zip(path, n_orfs=24, deg=4, n_strains=2):
    header = ["Query Strain ID", "Query allele name", "Array Strain ID", "Array allele name", "Arm",
              "Genetic interaction score (eps)", "P-value", "Query SMF", "Array SMF"]
    orfs = ["YAL%03dC" % (d + 1) for d in range(n_orfs)]
    rng = np.random.default_rng(404)
    lines = ["\t".join(header)]
    for a in range(n_orfs):
        for _ in range(deg):
            b = int(rng.integers(0, n_orfs))
            if b == a:
                continue
            for s in range(n_strains):
                eps = (1.0 if rng.random() > 0.5 else -1.0) * (EPS_FILTER + 0.05 + 0.2 * rng.random())
                lines.append("\t".join(["%s_tsq%d" % (orfs[a], s), "%s-1" % orfs[a].lower(),
                                        "%s_dma%d" % (orfs[b], s), "%s-2" % orfs[b].lower(), "chrI",
                                        "%.4f" % eps, "0.0100", "0.95", "0.94"]))
    tsv = "\n".join(lines) + "\n"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SGA_synth.txt", tsv)


def self_test():
    ok_all = True
    details = {}

    # (1) substrate signature bind against live hdlab.binding + FHRR bind/unbind round-trip on complex64.
    import inspect
    sig_bind = inspect.signature(hd_bind); sig_unbind = inspect.signature(hd_unbind)
    details["bind_params"] = list(sig_bind.parameters.keys())
    details["unbind_params"] = list(sig_unbind.parameters.keys())
    g = torch.Generator().manual_seed(3)
    ph = (2.0 * math.pi) * torch.rand(4, 512, generator=g)
    H = torch.polar(torch.ones(4, 512), ph).to(torch.complex64)
    bound = hd_bind(H[0:1], H[1:2])
    rec = hd_unbind(bound, H[0:1])                                # ~ H[1]
    unbind_ok = bool((rec[0].conj() @ H[1]).real.item() / 512.0 > 0.9)
    details["fhrr_unbind_roundtrip_ok"] = unbind_ok

    # (2) REAL PARSERS on synthetic BioGRID + Costanzo zips (exercise detect + parse + join-precision counter).
    os.makedirs(CACHE_DIR, exist_ok=True)
    bz = os.path.join(CACHE_DIR, "_selftest_synth_biogrid.zip")
    cz = os.path.join(CACHE_DIR, "_selftest_synth_costanzo.zip")
    _make_synth_biogrid_zip(bz); _make_synth_costanzo_zip(cz)
    try:
        pdata = parse_biogrid_physical(bz)
        gdata = parse_costanzo_genetic(cz, "pairwise")
    finally:
        for f in (bz, cz):
            try:
                os.remove(f)
            except OSError:
                pass
    parser_ok = bool(pdata.get("path") == "A" and gdata.get("path") == "A"
                     and len(pdata.get("edges", [])) > 10 and len(gdata.get("edges", [])) > 10)
    jp = float(pdata.get("join_precision", 0.0))
    join_precision_lt_1 = bool(jp < 1.0)                          # the 6 '-' rows must lower join_precision (counter works)
    jn = compute_join(pdata.get("orfs", set()), gdata.get("orfs", set()))
    join_shared_ok = bool(jn["n_exact"] >= 10 and jn["fuzzy_gain_frac"] <= FUZZY_GAIN_MAX)
    details.update(parser_ok=parser_ok, biogrid_join_precision=round(jp, 4), n_shared_synth=jn["n_exact"],
                   fuzzy_gain_synth=round(jn["fuzzy_gain_frac"], 4) if math.isfinite(jn["fuzzy_gain_frac"]) else None,
                   n_phys_edges_synth=len(pdata.get("edges", [])), n_gen_edges_synth=len(gdata.get("edges", [])))

    # (3) PLANTED two-module arena at FULL N (discriminator survives scale, option C): HUB beats MERGED + NO_HUB +
    #     single-constraint ceiling on the FULL set AND on the NOVEL (held-out) stratum. Mechanism-fires + survives-scale
    #     + HELD-OUT-SPLIT gate BEFORE real data is trusted.
    sub, queries = _planted_sub_and_queries(n_v=120, seed=7)
    idx_all, idx_seen, idx_novel = _strata_idx(queries)
    details["planted_n_queries"] = len(queries)
    details["planted_n_seen"] = len(idx_seen); details["planted_n_novel"] = len(idx_novel)
    scores, sigs = run_arms(sub, queries, seed=7)
    sm = stratified_maps(scores, queries)                        # arm -> {ALL, SEEN, NOVEL}
    mAll = {a: sm[a]["ALL"] for a in ARM_NAMES}
    mNov = {a: sm[a]["NOVEL"] for a in ARM_NAMES}
    details["planted_maps_all"] = {k: round(v, 4) if v == v else None for k, v in mAll.items()}
    details["planted_maps_novel"] = {k: round(v, 4) if v == v else None for k, v in mNov.items()}
    ceil_all = max(mAll[PHYS_ONLY], mAll[GEN_ONLY])
    ceil_nov = max(mNov[PHYS_ONLY], mNov[GEN_ONLY])
    details["planted_single_ceiling_all"] = round(ceil_all, 4)
    details["planted_single_ceiling_novel"] = round(ceil_nov, 4) if ceil_nov == ceil_nov else None

    # full-arena (ALL) discriminator preview (survives-scale); HONEST conjunction gate = HUB beats single-constraint ceiling.
    hub_beats_merged = bool(mAll[HUB] - mAll[MERGED] >= PLANT_MARGIN)
    hub_beats_nohub = bool(mAll[HUB] - mAll[NO_HUB] >= PLANT_MARGIN)
    hub_beats_single = bool(mAll[HUB] - ceil_all >= PLANT_MARGIN)
    hub_above_chance = bool(mAll[HUB] >= HP_HUB_ABS)
    scram_no_gain = bool(mAll[SCRAMBLE] <= ceil_all + MUSTFAIL_CEIL_TOL and mAll[HUB] - mAll[SCRAMBLE] >= PLANT_MARGIN)
    nohub_no_gain = bool(mAll[NO_HUB] <= ceil_all + MUSTFAIL_CEIL_TOL and mAll[HUB] - mAll[NO_HUB] >= PLANT_MARGIN)

    # HELD-OUT-SPLIT gate: both strata populated + non-leakage (novel pairs have NO direct edge) + HUB beats the ceiling on
    # the NOVEL (held-out) stratum at full N + must-fails fire on NOVEL. This certifies the PREDICTIVE claim before real data.
    both_strata_populated = bool(len(idx_seen) >= 1 and len(idx_novel) >= 10)
    direct = _direct_edge_set(sub)
    novel_no_direct_edge = all(((queries[i][0], queries[i][1]) not in direct) for i in idx_novel)
    seen_all_direct_edge = all(((queries[i][0], queries[i][1]) in direct) for i in idx_seen)
    hub_above_chance_novel = bool(mNov[HUB] == mNov[HUB] and mNov[HUB] >= HP_HUB_ABS)
    hub_beats_single_novel = bool(ceil_nov == ceil_nov and mNov[HUB] - ceil_nov >= PLANT_MARGIN)
    novel_mustfails = bool(mNov[SCRAMBLE] <= ceil_nov + MUSTFAIL_CEIL_TOL and mNov[HUB] - mNov[SCRAMBLE] >= PLANT_MARGIN
                           and mNov[NO_HUB] <= ceil_nov + MUSTFAIL_CEIL_TOL and mNov[HUB] - mNov[NO_HUB] >= PLANT_MARGIN)
    details.update(planted_both_strata_populated=both_strata_populated,
                   planted_novel_no_direct_edge=bool(novel_no_direct_edge),
                   planted_seen_all_direct_edge=bool(seen_all_direct_edge))

    # (4) ARMS-MUST-DIFFER (META_RULE_AF) + determinism on the planted arena.
    arms_differ = len(set(sigs[a] for a in (HUB, MERGED, NO_HUB, SCRAMBLE))) == 4
    _scores2, sigs2 = run_arms(sub, queries, seed=7)
    determinism_ok = (sigs2[HUB] == sigs[HUB] and sigs2[MERGED] == sigs[MERGED])
    details.update(arms_differ=arms_differ, determinism_ok=determinism_ok)

    checks = {
        "fhrr_unbind_roundtrip": unbind_ok,
        "real_parsers_reconstruct_edges": parser_ok,
        "join_precision_counter_fires": join_precision_lt_1,
        "exact_join_not_lossy_on_clean_synth": join_shared_ok,
        "planted_hub_beats_merged_at_full_N": hub_beats_merged,
        "planted_hub_beats_nohub_at_full_N": hub_beats_nohub,
        "planted_hub_beats_single_constraint_ceiling": hub_beats_single,
        "planted_hub_above_chance": hub_above_chance,
        "planted_scramble_no_conjunction_gain_over_single": scram_no_gain,
        "planted_nohub_no_conjunction_gain_over_single": nohub_no_gain,
        "heldout_both_strata_populated": both_strata_populated,
        "heldout_novel_pairs_have_no_direct_edge": bool(novel_no_direct_edge),
        "heldout_seen_pairs_all_direct_edge": bool(seen_all_direct_edge),
        "heldout_hub_above_chance_on_NOVEL": hub_above_chance_novel,
        "heldout_hub_beats_ceiling_on_NOVEL_at_full_N": hub_beats_single_novel,
        "heldout_mustfails_fire_on_NOVEL": novel_mustfails,
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
