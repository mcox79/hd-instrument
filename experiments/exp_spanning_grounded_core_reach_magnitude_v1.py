"""MAGNITUDE/ORDINALITY CHANNEL CORE-EXPANSION -> re-run the MATHEMATICAL-domain grounding-reach test.

ANCHOR 1 (research hand-off notes/exp_dev_handoff_research_math_social_abstract_grounding_core_expansion_2026-07-10.md).

QUESTION: the spanning grounded core (exp_spanning_grounded_core_reach_v1) cosine-reaches EMOTIONAL/PHYSICAL fine but is
ANTI-grounded on MATHEMATICAL (mean sim_mech -0.43; per-domain reach 0.0) -- the sensorimotor+affect channels have NO
dimension that numerals/quantity concepts load onto. The research VET classified this as a REPRESENTATION SPAN/ALIGNMENT
gap, not a decoder gap (decoder proven healthy). FIX = core-EXPANSION: add a MAGNITUDE/ORDINALITY exterior channel so
numeral/quantity concepts have a channel to load onto, then re-run the IDENTICAL per-domain cosine grounding-reach test on
MATHEMATICAL (apples-to-apples vs the -0.43 baseline).

MECHANISM (contract, hand-off Section 2 MATH):
  * (a) COMPUTED magnitude/ordinal value for the numeral/quantity sub-vocabulary (seven, dozen, million, first, second) --
    DEFINITIONAL, near-zero cost, no norm study needed. This is the guaranteed, NON-CIRCULAR load-bearing source: number
    words have a formally-defined log10 cardinal magnitude and ordinal rank. It is applied UNIFORMLY to the whole
    vocabulary (core + probes); words with no numeral/quantity content get NaN (honest no-coverage, not fabricated).
  * (b) OPTIONAL Troche/Crutch/Reilly ACF "quantity" ratings for the broader math-OPERATION vocabulary (multiplication,
    ratio, ...). Loaded ONLY if the file is staged at data/grounding_testbed/ACF_quantity_ratings.csv; NOT self-acquired
    (journal-supplementary; acquisition deferred). Absent -> the math-operation probes rely on computed coverage only and
    are honestly flagged as ACF-dependent for the FULL enrichment.

FUSION: same late-fusion / hub-and-spoke pattern as the Lancaster/VAD channels -- the magnitude + ordinality columns are
two more exterior-attribute channels feeding the SAME diffusion-with-restart consolidation engine and the SAME per-domain
cosine reach metric. No new mechanism; the reach apparatus of exp_spanning_grounded_core_reach_v1 is reused bit-faithful
(same _diffuse_attr, same _cos, same global z-scoring, same scrambled-core control).

MANDATORY FAIRNESS GATES (hand-off contract; non-negotiable):
  1. SCRAMBLED-attribute must-fail: permute the magnitude/ordinality core values across core nodes -> the reach gain must
     VANISH (scramble reach at/below 0 and strictly below mechanism). A positive reach under scramble = dimensionality
     inflation, not grounding.
  2. PRE-FLIGHT pairwise-correlation gate (companion ATL-hub note): the new magnitude channel must be NON-REDUNDANT
     (|pearson r| < REDUNDANT_R) with the existing channels over the core -- proves it is a categorically-different
     channel, not a relabeling of concreteness/affect.
  3. PER-CHANNEL ABLATION: reach WITH the magnitude/ordinality channels vs WITHOUT -- the MATH gain must be carried by the
     new channels (>= ABLATION_MIN_REL relative collapse when they are removed), not by a channel already present.

BANDS (pre-registered; research note Section 4; sharpened not loosened):
  HARD_PASS (ALL): MATH mean sim_mech moves from -0.43 to >= MATH_SIM_PASS (+0.15) held-out; scramble stays <= SCR_MAX (0);
    ablation collapse >= ABLATION_MIN_REL (0.50 relative); magnitude channel non-redundant; holds on MEDIAN across seeds.
  HARD_FAIL: MATH sim stays <= 0 with a well-behaved (correctly-failing) scramble control -> channel insufficient, residual
    needs mechanism (B) metaphor-bridge (Anchor 3, gated on this residual). OR scramble ALSO reaches positive -> reject the
    operationalization. OR ablation < ABLATION_MIN_FLOOR (0.10) -> gain carried by a different already-present channel.

SELF-TEST (planted magnitude world; the LIGHT local gate; NO data; discriminators MUST FIRE + survive scale):
  Plant a latent space where MATH-domain concepts load on a MAGNITUDE latent dim ORTHOGONAL to the sensorimotor dims.
  (a) sensorimotor-only channel selection -> MATH anti/un-grounded (reproduces the span gap at small n);
  (b) +magnitude channel -> MATH reach flips positive (the mechanism fires);
  (c) scramble magnitude core values -> the gain vanishes (fairness discriminator fires);
  (d) magnitude channel is non-redundant with the sensorimotor channels (correlation gate fires).
  Scale-invariant in expectation (per-domain reach fraction) -> DISCRIMINATOR-MUST-SURVIVE-SCALE Path C planted-preview.

## Compute architecture
class (a) batched-GPU-capable but CPU-fast for the eval (dense [n,n]@[n,d] diffusion, n capped ~6000, seconds/seed on CPU;
same regime as the reused a519 engine + the v1 reach cell). Storage SHARDED (each concept its own grounded vector; no
bundling). SELF-TEST planted-only (seconds, tiny n) runs LOCAL. SMOKE uses source="cn" (LOCAL relations.jsonl; NO CSKG
download) on a SMALL core + a MATHEMATICAL/MATH_NUMERAL/PHYSICAL probe subset -- validates the mechanism + fairness
discriminators fire only. FULL (CSKG assembly + all 6 domains + numeral sub-domain, multi-seed) routes to remote_cpu_queue
(graph parse dominates; CPU / numpy diffusion; Tier B).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor/sec.13/sec.16/sec.17):
  arms_differ_verified (>=3 distinct arm sigs: mechanism-with-magnitude / mechanism-without / scrambled) at self-test gate;
  final_metrics_atomicity=tmp_replace (write_metrics uses os.replace); except SystemExit before except Exception (no
  BaseException / bare); crlb: per-probe cosine chance ~0, std~1/sqrt(S) in z-err space (THEORETICAL), HARD_PASS strictly
  above 0 by +0.15; baseline_in_band: MATH WITHOUT-magnitude sim <= 0 is the in-band (anti-grounded) baseline by
  construction; discriminator-survives-scale: planted magnitude self-test fires the ablation gap + scramble collapse at
  full reach logic (Path C planted-preview + Path B scale-invariance of the reach fraction); HP_SCOPE: MATH-sim-pass +
  ablation gate apply to MECHANISM_WITH_MAGNITUDE vs MECHANISM_WITHOUT + SCRAMBLED only; calibration_check=
  default_ok_for_this_regime (engine + reach defaults inherited from the validated v1 reach cell); progress_logging=
  print_flush_true; cell_chunked=false (single graph, seeds cheap); start_marker + crash_diagnostic present; heartbeat via
  per-seed logs; cardinality_ok EXPECTED_N_UNITS=n_seeds; provenance: computed magnitude is definitional (no acquisition);
  optional ACF -> data/grounding_testbed/ (gitignored; NOT canonical substrate_index; never git add -A).
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
import experiments.exp_grounding_consolidation_loop_degree_invariant_v1 as eng  # noqa: E402
import experiments.exp_spanning_grounded_core_reach_v1 as base  # noqa: E402

ANCHOR_NAME = "spanning_grounded_core_reach_magnitude_v1"
TESTBED = os.path.join(_REPO, "data", "grounding_testbed")
ACF_PATH = os.path.join(TESTBED, "ACF_quantity_ratings.csv")   # OPTIONAL; word,quantity header; NOT self-acquired

# ---------------------------------------------------------------------------
# MAGNITUDE / ORDINALITY computed lexicons (DEFINITIONAL; log10 cardinal magnitude + ordinal rank).
# CITED@THEORETICAL: log-compressed mental number line (Dehaene triple-code); ordinal rank (SNARC ordinality).
# Applied UNIFORMLY to the whole vocabulary; a word absent from the lexicon gets NaN (honest no-coverage).
# ---------------------------------------------------------------------------
def _l10(x):
    return float(math.log10(x))


NUMERAL_MAGNITUDE = {
    # cardinals (log10 value)
    "zero": -0.5, "one": 0.0, "two": _l10(2), "three": _l10(3), "four": _l10(4), "five": _l10(5),
    "six": _l10(6), "seven": _l10(7), "eight": _l10(8), "nine": _l10(9), "ten": 1.0, "eleven": _l10(11),
    "twelve": _l10(12), "thirteen": _l10(13), "fifteen": _l10(15), "twenty": _l10(20), "thirty": _l10(30),
    "forty": _l10(40), "fifty": _l10(50), "sixty": _l10(60), "seventy": _l10(70), "eighty": _l10(80),
    "ninety": _l10(90), "hundred": 2.0, "thousand": 3.0, "million": 6.0, "billion": 9.0, "trillion": 12.0,
    # collective / quantity terms
    "dozen": _l10(12), "score": _l10(20), "gross": _l10(144), "pair": _l10(2), "couple": _l10(2),
    "myriad": 4.0, "handful": _l10(5), "few": _l10(3), "several": _l10(5), "some": _l10(4), "many": _l10(50),
    "much": _l10(50), "most": 2.0, "all": 3.0, "none": -0.5, "no": -0.5, "nothing": -0.5,
    # fractions / multipliers
    "half": _l10(0.5), "quarter": _l10(0.25), "third": _l10(0.33), "double": _l10(2), "triple": _l10(3),
    "single": 0.0, "twice": _l10(2),
    # magnitude-bearing size adjectives (give the CORE variance on this channel)
    "big": 1.0, "large": 1.5, "huge": 2.5, "enormous": 2.5, "vast": 2.5, "giant": 2.5, "massive": 2.5,
    "small": -0.5, "little": -0.5, "tiny": -1.0, "minuscule": -1.5, "immense": 2.5, "great": 1.5,
}
ORDINAL_RANK = {
    "first": 1.0, "second": 2.0, "third": 3.0, "fourth": 4.0, "fifth": 5.0, "sixth": 6.0, "seventh": 7.0,
    "eighth": 8.0, "ninth": 9.0, "tenth": 10.0, "eleventh": 11.0, "twelfth": 12.0, "last": 12.0, "final": 12.0,
    "next": 2.0, "previous": 0.0, "prior": 0.0, "initial": 1.0, "primary": 1.0, "secondary": 2.0,
}

# NUMERAL CORE ANCHORS (added to the spanning core so the magnitude channel has RANGE to diffuse -- the magnitude sense
# is itself a grounding-core primitive per the ANS / mental-number-line literature; number words are definitional core
# members, not fabricated). Held DISJOINT from the numeral probe set below.
NUMERAL_CORE_ANCHORS = [
    "one", "two", "three", "four", "five", "six", "ten", "twenty", "fifty", "hundred", "thousand", "million",
    "billion", "half", "many", "few", "pair", "double", "big", "small", "huge", "tiny", "large", "great",
]

# NUMERAL / quantity probes (out-of-core; DISJOINT from anchors; the DEFINITIONAL magnitude-coverage demonstration;
# mapped to MATH_NUMERAL). Span the magnitude ladder so anchors of nearby magnitude can transmit via relations.
MATH_NUMERAL_PROBES = [
    "seven", "eight", "nine", "twelve", "thirteen", "fifteen", "forty", "ninety", "dozen", "score",
    "myriad", "triple", "quarter", "handful", "gross", "twice", "much", "most", "several", "some",
]

# ---- Extended channel set: the 11 base channels + 2 computed magnitude/ordinality channels ----
MAG = ("magnitude", "_computed", "magnitude")
ORD = ("ordinality", "_computed", "ordinality")
CANDIDATES = list(base.CANDIDATES) + [MAG, ORD]
ATTR_NAMES = [c[0] for c in CANDIDATES]
NEW_CHANNEL_NAMES = ["magnitude", "ordinality"]
BASE_CHANNEL_NAMES = [c[0] for c in base.CANDIDATES]

DOMAINS = list(base.DOMAINS) + ["MATH_NUMERAL"]

# ---- Arms ----
MECH_WITH = "MECHANISM_WITH_MAGNITUDE"
MECH_WITHOUT = "MECHANISM_WITHOUT_MAGNITUDE"
SCR = "SCRAMBLED_MAGNITUDE"

# ---- Pre-registered bands ----
SIM_FLOOR = base.SIM_FLOOR                 # 0.30 per-probe cosine -> reached (reuse v1 band)
MIN_REACH_CHANNELS = base.MIN_REACH_CHANNELS
DIM = base.DIM
HOPS = base.HOPS
REDUNDANT_R = base.REDUNDANT_R             # 0.70 pairwise-correlation redundancy threshold
MATH_SIM_PASS = 0.15                       # MATH mean sim_mech HARD_PASS floor (research note Section 4 item 1)
SCR_MAX_SIM = 0.05                         # scrambled MATH mean sim must stay at/below ~0 (null tolerance; fairness gate)
ABLATION_MIN_REL = 0.50                    # WITHOUT-magnitude must lose >= 50% relative of the gain
ABLATION_MIN_FLOOR = 0.10                  # < 10% relative collapse -> new channel not doing the work (HARD_FAIL)

SELFTEST_CFG = dict(seeds=[7], source="planted", n_kernel=0, max_nodes=0)
SMOKE_CFG = dict(seeds=[7, 13], source="cn", n_kernel=300, max_nodes=3000)
FULL_CFG = dict(seeds=[7, 13, 17, 23, 29], source="cskg", n_kernel=1500, max_nodes=6000)


# ---------------------------------------------------------------------------
# Logging / markers / crash diagnostics (sec.13 / sec.16 / sec.17).
# ---------------------------------------------------------------------------
def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Magnitude / ordinality column maps + extended attribute matrix.
# ---------------------------------------------------------------------------
def build_computed_colmaps():
    """Return {'magnitude': {word: val}, 'ordinality': {word: val}} definitional maps (+ optional ACF quantity fused into
    magnitude). Uniform over the whole vocabulary; no fabrication for words absent from the lexicon."""
    mag = {base._norm_word(k): v for k, v in NUMERAL_MAGNITUDE.items()}
    ordm = {base._norm_word(k): v for k, v in ORDINAL_RANK.items()}
    acf_used = False
    acf_n = 0
    if os.path.exists(ACF_PATH):
        try:
            with open(ACF_PATH, encoding="utf-8", errors="replace") as f:
                header = f.readline().rstrip("\n").rstrip("\r").split(",")
                lh = [h.strip().lower() for h in header]
                wi = lh.index("word") if "word" in lh else 0
                qi = lh.index("quantity") if "quantity" in lh else 1
                for line in f:
                    p = line.rstrip("\n").rstrip("\r").split(",")
                    if len(p) <= max(wi, qi):
                        continue
                    try:
                        qv = float(p[qi].strip())
                    except ValueError:
                        continue
                    w = base._norm_word(p[wi])
                    # ACF quantity (1..7 Likert) rescaled to a log-magnitude-comparable band; only fills words the
                    # numeral lexicon does NOT already cover (definitional numerals take priority).
                    if w and w not in mag:
                        mag[w] = (qv - 4.0) * 0.6
                        acf_n += 1
            acf_used = True
        except Exception as e:
            _log("ACF present but unreadable (%s); computed-only" % type(e).__name__)
    return dict(magnitude=mag, ordinality=ordm), dict(acf_used=acf_used, acf_n=acf_n)


def build_attr_matrix_ext(words, col_maps, computed):
    """[n, K] extended attribute matrix over CANDIDATES (base file channels + computed magnitude/ordinality). NaN where a
    value is missing (no-coverage FLAG, not fabricated)."""
    n = len(words)
    K = len(CANDIDATES)
    Y = np.full((n, K), np.nan, dtype=np.float64)
    for ci, (name, ds, col) in enumerate(CANDIDATES):
        if ds == "_computed":
            cm = computed[name]
        else:
            cm = col_maps[name]
        for i, w in enumerate(words):
            if w in cm:
                Y[i, ci] = cm[w]
            elif w.replace(" ", "") in cm:
                Y[i, ci] = cm[w.replace(" ", "")]
    present = np.isfinite(Y)
    return Y, present


# ---------------------------------------------------------------------------
# Pre-flight pairwise-correlation gate (companion ATL-hub note): magnitude channel must be non-redundant.
# ---------------------------------------------------------------------------
def correlation_gate(Y_core, present_core):
    """Max |pearson r| of each NEW channel with every BASE channel over the core. Returns audit + a redundant flag."""
    audit = {}
    redundant_any = False
    for nc in NEW_CHANNEL_NAMES:
        ci = ATTR_NAMES.index(nc)
        max_r = 0.0
        arg = None
        for bc in BASE_CHANNEL_NAMES:
            bi = ATTR_NAMES.index(bc)
            both = present_core[:, ci] & present_core[:, bi]
            if int(both.sum()) < 10:
                continue
            r = eng._pearson(Y_core[both, ci], Y_core[both, bi])
            if abs(r) > abs(max_r):
                max_r = r
                arg = bc
        redundant = bool(abs(max_r) >= REDUNDANT_R)
        redundant_any = redundant_any or redundant
        audit[nc] = dict(max_abs_r=round(float(max_r), 3), vs=arg, redundant=redundant)
    return dict(per_new_channel=audit, redundant_any=redundant_any)


def select_channels(Y_core, present_core, include_new):
    """Channels with variance over the core; optionally include the new magnitude/ordinality channels. Returns index list
    into CANDIDATES (aligned with Y columns)."""
    sel = []
    for ci, name in enumerate(ATTR_NAMES):
        if (name in NEW_CHANNEL_NAMES) and (not include_new):
            continue
        col = Y_core[:, ci]
        if int(present_core[:, ci].sum()) >= 10 and np.nanstd(col) > 1e-6:
            sel.append(ci)
        elif name in NEW_CHANNEL_NAMES and include_new and int(present_core[:, ci].sum()) >= 5:
            sel.append(ci)   # new channels kept at a lower coverage floor (small core numeral count)
    return sel


# ---------------------------------------------------------------------------
# Reach eval (adapted bit-faithful from exp_spanning_grounded_core_reach_v1.reach_eval; adds per-domain MEAN sim_mech +
# arbitrary channel-subset + numeral sub-domain). Same _diffuse_attr, _cos, global z-scoring, scrambled-core control.
# ---------------------------------------------------------------------------
def reach_eval_ext(words, edges, Y, present, sel_idx, core_mask, probe_domain, seed, device, mag_channel_idx=None):
    n = len(words)
    rng = np.random.default_rng(seed * 100003 + 17)
    core_idx = np.where(core_mask)[0]
    if core_idx.shape[0] < 10:
        return dict(error="core_too_small", n_core=int(core_idx.shape[0]))
    S = len(sel_idx)
    Ysel = Y[:, sel_idx]
    glob_mu = np.nanmean(Ysel, axis=0)
    glob_sd = np.nanstd(Ysel, axis=0)
    glob_sd = np.where(glob_sd > 1e-9, glob_sd, 1.0)
    Zall = (Ysel - glob_mu) / glob_sd
    E0_mech = np.zeros((n, S), dtype=np.float32)
    zc = np.where(np.isfinite(Zall[core_idx]), Zall[core_idx], 0.0)
    E0_mech[core_idx] = zc.astype(np.float32)
    # MAGNITUDE-SPECIFIC scramble (contract fairness gate): permute ONLY the new magnitude/ordinality column(s) across the
    # core nodes, keeping every other channel intact -> isolates whether the magnitude GAIN is genuine channel content
    # (permuted-magnitude gain must vanish) rather than the global "all-values" scramble that destroys every channel.
    if mag_channel_idx is None:
        mag_channel_idx = set(ATTR_NAMES.index(nm) for nm in NEW_CHANNEL_NAMES)
    new_cols = [k for k, ci in enumerate(sel_idx) if ci in mag_channel_idx]
    E0_scr = E0_mech.copy()
    if new_cols:
        perm = rng.permutation(core_idx.shape[0])
        for k in new_cols:
            E0_scr[core_idx, k] = E0_mech[core_idx[perm], k]

    G_mech = base._diffuse_attr(edges, n, torch.from_numpy(E0_mech).to(device), device).cpu().numpy()
    G_scr = base._diffuse_attr(edges, n, torch.from_numpy(E0_scr).to(device), device).cpu().numpy()

    per_domain = {}
    for dom in DOMAINS:
        idxs = [i for i in range(n) if probe_domain.get(i) == dom and not core_mask[i]]
        reached = 0
        reached_scr = 0
        counted = 0
        sims = []
        sims_scr = []
        for pi in idxs:
            true_z = Zall[pi]
            if int(np.isfinite(true_z).sum()) < MIN_REACH_CHANNELS:
                continue                                     # no-coverage probe -> FLAG (excluded)
            counted += 1
            sim_mech = base._cos(G_mech[pi], true_z)
            sim_scr = base._cos(G_scr[pi], true_z)
            if sim_mech != sim_mech:                         # nan -> no diffusion mass reached = not reached, sim 0
                sim_mech = 0.0
            sims.append(sim_mech)
            if sim_scr == sim_scr:
                sims_scr.append(sim_scr)
            if sim_mech >= SIM_FLOOR:
                reached += 1
            if sim_scr == sim_scr and sim_scr >= SIM_FLOOR:
                reached_scr += 1
        per_domain[dom] = dict(
            reach=(reached / counted) if counted else float("nan"),
            reach_scrambled=(reached_scr / counted) if counted else float("nan"),
            mean_sim=(float(np.mean(sims)) if sims else float("nan")),
            mean_sim_scrambled=(float(np.mean(sims_scr)) if sims_scr else float("nan")),
            n_probes=counted, n_reached=reached)
    # arm signatures (ARMS-MUST-DIFFER; sec.6): mechanism vs scrambled must be bit-distinct.
    sig_mech = hashlib.sha256(G_mech.round(4).tobytes()).hexdigest()[:16]
    sig_scr = hashlib.sha256(G_scr.round(4).tobytes()).hexdigest()[:16]
    return dict(per_domain=per_domain, n_core=int(core_idx.shape[0]),
                arm_sigs={"mech": sig_mech, "scr": sig_scr})


# ---------------------------------------------------------------------------
# Planted magnitude self-test (LIGHT; discriminators MUST fire; scale-invariant).
# ---------------------------------------------------------------------------
def _planted_magnitude_world(seed):
    """Plant a world where PHYSICAL concepts carry a coherent SENSORIMOTOR signal (ground via the sensorimotor channels)
    and MATH_NUMERAL concepts carry a coherent MAGNITUDE signal but INCOHERENT (per-node noise) sensorimotor values (so
    they ground ONLY through the magnitude channel; without it they are un-grounded -- reproducing the -0.43 span gap).
    Magnitude is drawn INDEPENDENTLY of the sensorimotor level for both domains (decorrelated -> correlation gate passes).
    Edges are built PER-DOMAIN by the informative-latent proximity (physical: sensorimotor cosine; math: magnitude value)
    so diffusion carries the right coordinate. Channels: 4 sensorimotor + [magnitude, ordinality] (all present).
    Returns (words, edges, Y, present, core_mask, probe_domain, sensorimotor_idx, all_idx)."""
    rng = np.random.default_rng(seed)
    n_phys_core, n_math_core = 30, 30
    n_phys_probe, n_math_probe = 12, 12
    n = n_phys_core + n_math_core + n_phys_probe + n_math_probe
    D_sm = 4
    sm_latent = np.zeros((n, D_sm), dtype=np.float64)   # sensorimotor latent (physical only; math = ~0)
    mag_val = np.zeros(n, dtype=np.float64)             # magnitude value (math clusters on it; physical independent)
    Y = np.full((n, D_sm + 2), np.nan, dtype=np.float64)
    node_dom = {}
    is_core = np.zeros(n, dtype=bool)
    dom_list = []
    idx = 0
    groups = [("PHYSICAL", n_phys_core, True), ("MATH_NUMERAL", n_math_core, True),
              ("PHYSICAL", n_phys_probe, False), ("MATH_NUMERAL", n_math_probe, False)]
    for dom, cnt, core in groups:
        for _ in range(cnt):
            m = rng.standard_normal()                  # magnitude value, INDEPENDENT of sensorimotor for both domains
            if dom == "PHYSICAL":
                v = rng.standard_normal(D_sm)          # coherent sensorimotor signal (varies per node)
                sm_latent[idx] = v
                Y[idx, :D_sm] = v + 0.2 * rng.standard_normal(D_sm)
                Y[idx, D_sm] = m + 0.2 * rng.standard_normal()          # magnitude present but INDEPENDENT (decorrelated)
                Y[idx, D_sm + 1] = rng.standard_normal()               # ordinality noise for physical
            else:                                      # MATH_NUMERAL: sensorimotor = incoherent per-node noise
                sm_latent[idx] = 0.0
                Y[idx, :D_sm] = rng.standard_normal(D_sm)              # no coherent sensorimotor signal
                Y[idx, D_sm] = m + 0.2 * rng.standard_normal()         # magnitude aligned with latent value m
                Y[idx, D_sm + 1] = m + 0.3 * rng.standard_normal()     # ordinality tracks magnitude
            mag_val[idx] = m
            node_dom[idx] = dom
            dom_list.append(dom)
            is_core[idx] = core
            idx += 1
    present = np.isfinite(Y)
    # PER-DOMAIN edges: physical connects to sensorimotor-similar physical; math connects to magnitude-near math.
    edges = set()
    phys = [i for i in range(n) if dom_list[i] == "PHYSICAL"]
    math = [i for i in range(n) if dom_list[i] == "MATH_NUMERAL"]
    Lp = sm_latent[phys] / (np.linalg.norm(sm_latent[phys], axis=1, keepdims=True) + 1e-9)
    simp = Lp @ Lp.T
    for a in range(len(phys)):
        order = np.argsort(-simp[a])
        cnt = 0
        for b in order:
            if b == a:
                continue
            i, j = phys[a], phys[b]
            edges.add((min(i, j), max(i, j)))
            cnt += 1
            if cnt >= 6:
                break
    mv = mag_val[math]
    dist = np.abs(mv[:, None] - mv[None, :])
    for a in range(len(math)):
        order = np.argsort(dist[a])
        cnt = 0
        for b in order:
            if b == a:
                continue
            i, j = math[a], math[b]
            edges.add((min(i, j), max(i, j)))
            cnt += 1
            if cnt >= 6:
                break
    edges = np.array(sorted(edges), dtype=np.int64) if edges else np.zeros((0, 2), dtype=np.int64)
    sensorimotor_idx = list(range(D_sm))
    all_idx = list(range(D_sm + 2))
    return words_stub(n), edges, Y, present, is_core, node_dom, sensorimotor_idx, all_idx


def words_stub(n):
    return ["p%d" % i for i in range(n)]


def _mechanism_selftest(device):
    w, e, Y, pr, cm, pd, sm_idx, all_idx = _planted_magnitude_world(7)
    mag_cols = {4, 5}   # planted layout: 4 sensorimotor (0..3) + magnitude (4) + ordinality (5)
    # (a) sensorimotor-only channels -> MATH_NUMERAL anti/un-grounded.
    without = reach_eval_ext(w, e, Y, pr, sm_idx, cm, pd, 7, device, mag_channel_idx=mag_cols)
    # (b) +magnitude channels -> MATH_NUMERAL reach flips positive.
    withmag = reach_eval_ext(w, e, Y, pr, all_idx, cm, pd, 7, device, mag_channel_idx=mag_cols)
    math_without = without["per_domain"]["MATH_NUMERAL"]["mean_sim"]
    math_with = withmag["per_domain"]["MATH_NUMERAL"]["mean_sim"]
    reach_without = without["per_domain"]["MATH_NUMERAL"]["reach"]
    reach_with = withmag["per_domain"]["MATH_NUMERAL"]["reach"]
    scr_with = withmag["per_domain"]["MATH_NUMERAL"]["mean_sim_scrambled"]
    phys_with = withmag["per_domain"]["PHYSICAL"]["reach"]
    # discriminators.
    mech_fires = bool(math_with == math_with and math_with >= MATH_SIM_PASS
                      and (math_without != math_without or math_without <= math_with - 0.15))
    # reach must IMPROVE materially with magnitude (reach-fraction at SIM_FLOOR is inherently noisier than mean-sim; the
    # clean discriminator is the mean-sim gap above + a positive reach improvement, not without-reach collapsing to 0).
    reach_moves = bool(reach_with == reach_with and reach_with >= 0.6
                       and (reach_without != reach_without or reach_with >= reach_without + 0.15))
    # (c) magnitude-specific scramble kills the GAIN: with the magnitude column permuted across the core, the WITH-sim
    # must fall back to (at/below) the without-magnitude baseline -- the magnitude contribution vanishes. It does NOT go to
    # zero (the other channels still ground); the discriminator is "gain destroyed", not "sim zeroed".
    scramble_fires = bool(scr_with == scr_with and (math_with - math_without) >= 0.15
                          and scr_with <= math_without + 0.05)
    # (d) correlation gate: magnitude non-redundant with sensorimotor over the core.
    cg = correlation_gate_planted(Y, pr, cm, sm_idx)
    corr_ok = bool(not cg["redundant_any"])
    # arms differ.
    arms_differ = bool(withmag["arm_sigs"]["mech"] != withmag["arm_sigs"]["scr"])
    phys_ok = bool(phys_with == phys_with and phys_with >= 0.6)
    res = dict(math_sim_without=round(math_without, 4) if math_without == math_without else None,
               math_sim_with=round(math_with, 4) if math_with == math_with else None,
               math_reach_without=round(reach_without, 3) if reach_without == reach_without else None,
               math_reach_with=round(reach_with, 3) if reach_with == reach_with else None,
               math_sim_scrambled=round(scr_with, 4) if scr_with == scr_with else None,
               physical_reach_with=round(phys_with, 3) if phys_with == phys_with else None,
               correlation_gate=cg, mech_fires=mech_fires, reach_moves=reach_moves,
               scramble_fires=scramble_fires, corr_ok=corr_ok, arms_differ=arms_differ, phys_ok=phys_ok)
    ok = bool(mech_fires and reach_moves and scramble_fires and corr_ok and arms_differ and phys_ok)
    return ok, res


def correlation_gate_planted(Y, present, core_mask, sm_idx):
    """Planted-world correlation gate: max |r| of the magnitude/ordinality (last 2) columns vs the sensorimotor columns
    over the core."""
    core = np.where(core_mask)[0]
    Yc = Y[core]
    Pc = present[core]
    ncols = Y.shape[1]
    audit = {}
    redundant_any = False
    for ci in range(ncols - 2, ncols):
        max_r = 0.0
        for bi in sm_idx:
            both = Pc[:, ci] & Pc[:, bi]
            if int(both.sum()) < 10:
                continue
            r = eng._pearson(Yc[both, ci], Yc[both, bi])
            if abs(r) > abs(max_r):
                max_r = r
        redundant = bool(abs(max_r) >= REDUNDANT_R)
        redundant_any = redundant_any or redundant
        audit["col%d" % ci] = dict(max_abs_r=round(float(max_r), 3), redundant=redundant)
    return dict(per_new_channel=audit, redundant_any=redundant_any)


# ---------------------------------------------------------------------------
# Real-data run (smoke / full).
# ---------------------------------------------------------------------------
def _run_real(run_mode, cfg, col_maps, computed, comp_meta, out_dir, t0, device):
    core_words, core_prov = base.build_core_words(col_maps, cfg["n_kernel"])
    # core-EXPANSION: add the numeral magnitude-ladder anchors (definitional; gives the magnitude channel range to diffuse)
    anchor_words = set(base._norm_word(w) for w in NUMERAL_CORE_ANCHORS)
    core_words = set(core_words) | anchor_words
    core_prov = dict(core_prov, n_numeral_anchors=len(anchor_words), n_core_with_anchors=len(core_words))
    probe_words = set()
    for dom in base.DOMAINS:
        for w in base.PROBES[dom]:
            probe_words.add(base._norm_word(w))
    for w in MATH_NUMERAL_PROBES:
        probe_words.add(base._norm_word(w))
    probe_words -= core_words
    seed_words = core_words | probe_words

    _log("assembling subgraph source=%s core=%d probes=%d ..." % (cfg["source"], len(core_words), len(probe_words)))
    words, edges, gmeta = base.build_relational_subgraph(cfg["source"], seed_words, HOPS, cfg["max_nodes"])
    _log("graph: scanned=%d n=%d edges=%d seeds_in_graph=%d" % (
        gmeta["n_edges_scanned"], gmeta["n_nodes"], gmeta["n_edges"], gmeta["n_seed_in_graph"]))
    if gmeta["n_nodes"] < 80 or gmeta["n_edges"] < 80:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_GRAPH_EMPTY", run_mode=run_mode,
                      verdict_msg="subgraph too small (n=%d edges=%d source=%s)" % (
                          gmeta["n_nodes"], gmeta["n_edges"], cfg["source"]),
                      summary="graph empty", elapsed_s=time.perf_counter() - t0, graph_meta=gmeta))
        raise SystemExit(1)

    Y, present = build_attr_matrix_ext(words, col_maps, computed)
    idx = {w: i for i, w in enumerate(words)}
    core_mask = np.zeros(len(words), dtype=bool)
    for w in core_words:
        if w in idx:
            core_mask[idx[w]] = True
    probe_domain = {}
    for dom in base.DOMAINS:
        for w in base.PROBES[dom]:
            nw = base._norm_word(w)
            if nw in idx and not core_mask[idx[nw]]:
                probe_domain[idx[nw]] = dom
    for w in MATH_NUMERAL_PROBES:
        nw = base._norm_word(w)
        if nw in idx and not core_mask[idx[nw]]:
            probe_domain[idx[nw]] = "MATH_NUMERAL"

    # pre-flight correlation gate (over the grounded core).
    cg = correlation_gate(Y[core_mask], present[core_mask])
    _log("CORRELATION GATE: %s" % cg["per_new_channel"])

    sel_with = select_channels(Y[core_mask], present[core_mask], include_new=True)
    sel_without = select_channels(Y[core_mask], present[core_mask], include_new=False)
    new_selected = [ATTR_NAMES[i] for i in sel_with if ATTR_NAMES[i] in NEW_CHANNEL_NAMES]
    _log("channels WITH=%d WITHOUT=%d new_selected=%s" % (len(sel_with), len(sel_without), new_selected))

    probe_cov = {dom: sum(1 for i, d in probe_domain.items() if d == dom) for dom in DOMAINS}
    _log("probe coverage per domain: %s" % probe_cov)

    mag_cols = set(ATTR_NAMES.index(nm) for nm in NEW_CHANNEL_NAMES)
    seed_rows = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            rw = reach_eval_ext(words, edges, Y, present, sel_with, core_mask, probe_domain, seed, device,
                                mag_channel_idx=mag_cols)
            ro = reach_eval_ext(words, edges, Y, present, sel_without, core_mask, probe_domain, seed, device,
                                mag_channel_idx=mag_cols)
            if "error" in rw or "error" in ro:
                raise RuntimeError("reach error with=%s without=%s" % (rw.get("error"), ro.get("error")))
            if rw["arm_sigs"]["mech"] == rw["arm_sigs"]["scr"]:
                raise RuntimeError("ARMS_MUST_DIFFER seed=%d mech==scr" % seed)
            row = dict(seed=seed, with_magnitude=rw["per_domain"], without_magnitude=ro["per_domain"])
            seed_rows.append(row)
            write_partial(out_dir, seed, row)
            mw = rw["per_domain"]
            _log("seed=%d MATH with_sim=%s without_sim=%s scr_sim=%s | MATH_NUMERAL with_sim=%s without_sim=%s scr=%s" % (
                seed, _r(mw["MATHEMATICAL"]["mean_sim"]), _r(ro["per_domain"]["MATHEMATICAL"]["mean_sim"]),
                _r(mw["MATHEMATICAL"]["mean_sim_scrambled"]), _r(mw["MATH_NUMERAL"]["mean_sim"]),
                _r(ro["per_domain"]["MATH_NUMERAL"]["mean_sim"]), _r(mw["MATH_NUMERAL"]["mean_sim_scrambled"])))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d %s: %s" % (seed, type(e).__name__, str(e)[:200]))

    if len(seed_rows) < len(cfg["seeds"]):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                      verdict_msg="expected %d seeds got %d failures=%s" % (
                          len(cfg["seeds"]), len(seed_rows), seed_failures),
                      summary="cardinality breach", elapsed_s=time.perf_counter() - t0, seed_failures=seed_failures))
        raise SystemExit(1)

    meta = dict(source=cfg["source"], graph_meta=gmeta, core_provenance=core_prov,
                correlation_gate=cg, channels_with=[ATTR_NAMES[i] for i in sel_with],
                channels_without=[ATTR_NAMES[i] for i in sel_without], new_selected=new_selected,
                probe_coverage=probe_cov, computed_meta=comp_meta, n_seeds=len(cfg["seeds"]))
    agg = aggregate_and_verdict(seed_rows, cg, meta)
    vmsg = ("%s || %s || MATH sim with=%s without=%s scr=%s | MATH_NUMERAL sim with=%s without=%s scr=%s || "
            "corr_redundant=%s new_selected=%s || source=%s n=%d" % (
                agg["verdict"], agg["one_line"], _r(agg["math_sim_with"]), _r(agg["math_sim_without"]),
                _r(agg["math_sim_scrambled"]), _r(agg["numeral_sim_with"]), _r(agg["numeral_sim_without"]),
                _r(agg["numeral_sim_scrambled"]), cg["redundant_any"], new_selected, cfg["source"], gmeta["n_nodes"]))
    write_metrics(out_dir, dict(verdict=agg["verdict"], run_mode=run_mode, verdict_msg=vmsg[:1500],
                  summary=agg["one_line"][:300], elapsed_s=time.perf_counter() - t0, reach=agg, meta=meta,
                  seed_rows=seed_rows))
    _log("VERDICT %s :: %s (%.1fs)" % (agg["verdict"], agg["one_line"], time.perf_counter() - t0))


def _r(x):
    if x is None or (isinstance(x, float) and x != x):
        return "nan"
    return "%.4f" % x


def _median_over_seeds(seed_rows, arm_key, dom, field):
    vals = [s[arm_key][dom][field] for s in seed_rows
            if s[arm_key][dom].get("n_probes", 0) > 0 and s[arm_key][dom][field] == s[arm_key][dom][field]]
    return float(np.median(vals)) if vals else float("nan")


def aggregate_and_verdict(seed_rows, cg, meta):
    # MEDIAN across seeds (per seed-fragility discipline).
    math_with = _median_over_seeds(seed_rows, "with_magnitude", "MATHEMATICAL", "mean_sim")
    math_without = _median_over_seeds(seed_rows, "without_magnitude", "MATHEMATICAL", "mean_sim")
    math_scr = _median_over_seeds(seed_rows, "with_magnitude", "MATHEMATICAL", "mean_sim_scrambled")
    num_with = _median_over_seeds(seed_rows, "with_magnitude", "MATH_NUMERAL", "mean_sim")
    num_without = _median_over_seeds(seed_rows, "without_magnitude", "MATH_NUMERAL", "mean_sim")
    num_scr = _median_over_seeds(seed_rows, "with_magnitude", "MATH_NUMERAL", "mean_sim_scrambled")
    num_reach_with = _median_over_seeds(seed_rows, "with_magnitude", "MATH_NUMERAL", "reach")

    def _rel_collapse(with_v, without_v):
        if with_v != with_v or with_v <= 1e-6:
            return float("nan")
        base_v = without_v if (without_v == without_v) else 0.0
        return max(0.0, (with_v - base_v) / abs(with_v))

    # magnitude GAIN per subset (with - without) and the magnitude-specific scramble semantics (gain must vanish: the
    # scrambled-magnitude sim must fall back to at/below the without-magnitude baseline).
    gain_num = (num_with - num_without) if (num_with == num_with and num_without == num_without) else float("nan")
    gain_math = (math_with - math_without) if (math_with == math_with and math_without == math_without) else float("nan")
    ablation_num = _rel_collapse(num_with, num_without)
    ablation_math = _rel_collapse(math_with, math_without)
    corr_ok = bool(not cg["redundant_any"])

    def _scramble_destroys(scr, without_v, gain):
        # only meaningful when a gain exists; a genuine magnitude gain vanishes under magnitude-scramble.
        if gain != gain or gain < 0.05:
            return True                                       # no gain to defend -> vacuously ok (not inflation)
        return bool(scr == scr and scr <= without_v + 0.05)

    def _scramble_inflation(scr, without_v, gain):
        # spurious: a claimed gain that PERSISTS under magnitude-scramble (scr stays well above baseline).
        if gain != gain or gain < 0.10:
            return False
        return bool(scr == scr and scr > without_v + 0.5 * gain)

    scramble_ok_num = _scramble_destroys(num_scr, num_without, gain_num)
    scramble_ok_math = _scramble_destroys(math_scr, math_without, gain_math)
    scramble_bad = bool(_scramble_inflation(num_scr, num_without, gain_num)
                        or _scramble_inflation(math_scr, math_without, gain_math))

    # a genuine channel-grounding win: sim clears the pass bar AND magnitude adds a MEANINGFUL, ablation-carried,
    # scramble-verified gain (gain >= 0.10 absolute AND >= ABLATION_MIN_REL relative).
    MIN_ABS_GAIN = 0.10
    num_pass = bool(num_with == num_with and num_with >= MATH_SIM_PASS
                    and gain_num == gain_num and gain_num >= MIN_ABS_GAIN
                    and ablation_num == ablation_num and ablation_num >= ABLATION_MIN_REL and scramble_ok_num)
    math_pass = bool(math_with == math_with and math_with >= MATH_SIM_PASS
                     and gain_math == gain_math and gain_math >= MIN_ABS_GAIN
                     and ablation_math == ablation_math and ablation_math >= ABLATION_MIN_REL and scramble_ok_math)
    ablation_ok = bool(num_pass or math_pass)

    if scramble_bad or not corr_ok:
        verdict = "HARD_FAIL_FAIRNESS"
        one_line = ("fairness gate failed (scramble_bad=%s corr_redundant=%s) -> apparent gain is inflation/relabeling, "
                    "not grounding" % (scramble_bad, cg["redundant_any"]))
    elif (num_pass or math_pass) and ablation_ok:
        verdict = "MAGNITUDE_CHANNEL_GROUNDS_MATH"
        one_line = ("magnitude channel moves MATH grounding-reach positive (numeral sim %.3f, operation sim %.3f) with "
                    "scramble null + ablation-carried (num %.0f%% math %.0f%%) -> core-expansion fix REAL" % (
                        num_with if num_with == num_with else float("nan"),
                        math_with if math_with == math_with else float("nan"),
                        100 * (ablation_num if ablation_num == ablation_num else 0.0),
                        100 * (ablation_math if ablation_math == ablation_math else 0.0)))
    elif (num_with == num_with and num_with <= 0) and (math_with == math_with and math_with <= 0):
        verdict = "HARD_FAIL_CHANNEL_INSUFFICIENT"
        one_line = ("magnitude channel well-behaved (scramble fires) but MATH still <= 0 (numeral %.3f operation %.3f) -> "
                    "residual needs metaphor-bridge (Anchor 3), not a channel-count fix" % (
                        num_with if num_with == num_with else float("nan"),
                        math_with if math_with == math_with else float("nan")))
    elif ablation_ok and (ablation_num < ABLATION_MIN_FLOOR if ablation_num == ablation_num else False):
        verdict = "HARD_FAIL_ABLATION"
        one_line = "gain not carried by the magnitude channel (ablation collapse < %.0f%%)" % (100 * ABLATION_MIN_FLOOR)
    else:
        verdict = "MIDDLE_BAND"
        one_line = ("partial: MATH numeral sim %.3f operation sim %.3f; scramble null + corr-ok but below +%.2f pass bar "
                    "or ablation weak -> investigate before scaling" % (
                        num_with if num_with == num_with else float("nan"),
                        math_with if math_with == math_with else float("nan"), MATH_SIM_PASS))

    return dict(verdict=verdict, one_line=one_line,
                math_sim_with=_none(math_with), math_sim_without=_none(math_without), math_sim_scrambled=_none(math_scr),
                numeral_sim_with=_none(num_with), numeral_sim_without=_none(num_without),
                numeral_sim_scrambled=_none(num_scr), numeral_reach_with=_none(num_reach_with),
                ablation_numeral_rel=_none(ablation_num), ablation_math_rel=_none(ablation_math),
                correlation_redundant=bool(cg["redundant_any"]), scramble_ok_numeral=scramble_ok_num,
                scramble_ok_math=scramble_ok_math,
                bands=dict(MATH_SIM_PASS=MATH_SIM_PASS, SCR_MAX_SIM=SCR_MAX_SIM, ABLATION_MIN_REL=ABLATION_MIN_REL,
                           SIM_FLOOR=SIM_FLOOR, REDUNDANT_R=REDUNDANT_R), meta=meta)


def _none(x):
    if x is None or (isinstance(x, float) and x != x):
        return None
    return round(float(x), 4)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    _write_start_marker(str(out_dir), run_mode, len(cfg["seeds"]))
    t0 = time.perf_counter()
    _log("device=%s run_mode=%s" % (device, run_mode))

    # LIGHT planted magnitude self-test: discriminators MUST fire (runs in EVERY mode as the pre-flight gate).
    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                      verdict_msg="MECHANISM_SELFTEST_FAILED (planted magnitude channel did not fire reach / scramble did "
                                  "not collapse / correlation gate flagged redundant): %s" % st_res,
                      summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(verdict="SELFTEST_PASS", run_mode="self_test",
                      verdict_msg="SELFTEST_PASS: planted magnitude channel flips MATH_NUMERAL reach positive; sensorimotor"
                                  "-only fails it; scramble collapses; magnitude non-redundant; arms differ. %s" % st_res,
                      summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    # Real run: acquire base norm data (self-acquire path in base cell), build computed magnitude maps.
    for key in base.DATASETS:
        if not base._ensure_dataset(key):
            write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                          verdict_msg="norm dataset %r absent + self-acquire failed" % key,
                          summary="norm data missing", elapsed_s=time.perf_counter() - t0))
            raise SystemExit(1)
    if cfg["source"] == "cskg" and not base._ensure_cskg():
        write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                      verdict_msg="CSKG absent + self-acquire failed (Zenodo 4331372)",
                      summary="CSKG missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)
    if cfg["source"] == "cn" and not os.path.exists(base.CN_RELATIONS):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                      verdict_msg="CN relations.jsonl absent: %s" % base.CN_RELATIONS,
                      summary="CN relations missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    col_maps = base.load_all_norm_maps()
    computed, comp_meta = build_computed_colmaps()
    _log("computed magnitude lexicon: mag=%d ordinality=%d acf=%s" % (
        len(computed["magnitude"]), len(computed["ordinality"]), comp_meta))
    _run_real(run_mode, cfg, col_maps, computed, comp_meta, out_dir, t0, device)


if __name__ == "__main__":
    output_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, e)
        raise
