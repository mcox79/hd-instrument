"""SOCIAL-RELATIONAL (power x affiliation) CHANNEL CORE-EXPANSION -> re-run the SOCIAL-domain grounding-reach test.

ANCHOR 2 (research hand-off notes/exp_dev_handoff_research_math_social_abstract_grounding_core_expansion_2026-07-10.md).

QUESTION: the spanning grounded core (exp_spanning_grounded_core_reach_v1) cosine-reaches EMOTIONAL (+0.48) / PHYSICAL
(+0.27) fine but BARELY reaches SOCIAL (mean sim_mech +0.015) -- the sensorimotor + affect (VAD) channels have no
dimension that social-STRUCTURAL / RELATIONAL concepts (hierarchy, loyalty, authority, marriage) coherently load onto.
Per the grounding drill, SOCIAL is grounded (brain-first: hippocampal-entorhinal social space; Tavares/Behrens; the
Interpersonal Circumplex) via a 2D POWER/DOMINANCE x AFFILIATION/WARMTH coordinate system -- a RELATIONAL channel, NOT
more affect. FIX = core-EXPANSION: add a 2D social-relational (power x affiliation) exterior channel so social concepts
have a channel to load onto, then re-run the IDENTICAL per-domain cosine grounding-reach test on SOCIAL (apples-to-apples
vs the +0.015 baseline, which is exactly the WITHOUT-social arm here).

PRIOR (honest): the parallel MAGNITUDE channel (Anchor 1) landed MIDDLE_BAND -- a scalar-attribute channel barely moved
even numerals. So there is a real prior that scalar-attribute channels underperform for abstract domains. SOCIAL is a
better bet than magnitude was (power x affiliation is affect-ADJACENT and affect reached +0.48) but an honest
MIDDLE_BAND / negative here is itself informative.

MECHANISM (contract, hand-off Anchor 2 + research note Section 2 SOCIAL):
  * A curated 2D circumplex-coordinate lexicon (POWER, AFFILIATION) for social-relational trait / role / institution
    terms, CITED@Interpersonal-Circumplex (Leary 1957; Wiggins IAS; IPIP-IPC octant structure; public-domain instrument).
    SUBSTITUTION FLAG: rather than downloading raw IPIP-IPC item-level ratings (slow acquisition), the coordinates are
    CURATED IN-CELL from the published IPIP-IPC octant-marker geometry (8 octants at 45-deg spacing on the
    dominance x warmth plane). This is the SOCIAL analog of Anchor 1's definitional magnitude lexicon: self-contained,
    ASCII, no data acquisition, applied UNIFORMLY to the whole vocabulary; a word absent from the lexicon gets NaN
    (honest no-coverage, not fabricated). Optional augmentation: if data/grounding_testbed/social_circumplex_ratings.csv
    (header: word,power,affiliation) is staged, it fills words the curated lexicon does NOT cover (curated takes
    priority); NOT self-acquired.

FUSION: same late-fusion / hub-and-spoke pattern as the Lancaster/VAD channels -- power + affiliation are two more
exterior-attribute channels feeding the SAME diffusion-with-restart consolidation engine and the SAME per-domain cosine
reach metric. No new mechanism; the reach apparatus of exp_spanning_grounded_core_reach_v1 is reused bit-faithful (same
_diffuse_attr, same _cos, same global z-scoring, same channel-SPECIFIC scramble as Anchor 1's magnitude cell).

MANDATORY FAIRNESS GATES (hand-off contract; non-negotiable):
  1. SOCIAL-SPECIFIC scramble must-fail: permute ONLY the power/affiliation column(s) across the core nodes (every other
     channel intact) -> the reach GAIN must VANISH. A positive gain under social-scramble = dimensionality inflation.
  2. PRE-FLIGHT pairwise-correlation gate: the power + affiliation channels must be NON-REDUNDANT (|pearson r| <
     REDUNDANT_R) with the existing channels over the core -- ESPECIALLY vs Warriner VAD (valence/arousal/DOMINANCE).
     Warriner "dominance" is AFFECTIVE dominance (emotional control over a stimulus), a DIFFERENT construct from social
     power/dominance; the gate proves power/affiliation are not a relabeling of affect.
  3. AFFECT-ABLATION (the single most load-bearing SOCIAL control; hand-off): the WITHOUT-social arm KEEPS the VAD/affect
     channel and removes ONLY power/affiliation. If SOCIAL's reach gain collapses (>= ABLATION_MIN_REL relative) when
     power/affiliation are removed WHILE VAD is kept, the gain is genuine social-relational content, NOT relabeled
     EMOTIONAL reach. If the WITHOUT-social arm (keeping VAD) still grounds SOCIAL (ablation < ABLATION_MIN_FLOOR), the
     gain was affect bleed-through -> HARD_FAIL_AFFECT_RELABEL.

BANDS (pre-registered; research note Section 4 SOCIAL items 2/3/4; sharpened not loosened):
  HARD_PASS (ALL): SOCIAL mean sim_mech moves from +0.015 to >= SOCIAL_SIM_PASS (+0.15) held-out; social-scramble gain
    vanishes (scr <= without + null tol); AFFECT-ABLATION collapse >= ABLATION_MIN_REL (0.50 relative) with VAD kept;
    power/affiliation non-redundant (esp. vs VAD); holds on MEDIAN across seeds.
  HARD_FAIL_AFFECT_RELABEL: WITHOUT-social (VAD kept) still grounds SOCIAL, ablation < ABLATION_MIN_FLOOR -> the gain is
    affect bleed-through, not social-relational content (the most likely fake-pass; hand-off-flagged).
  HARD_FAIL_CHANNEL_INSUFFICIENT: SOCIAL stays <= 0 with a well-behaved (correctly-failing) scramble -> channel
    insufficient; residual may need theory-of-mind / mentalizing content or the metaphor-bridge (research note Section 4
    HARD-FAIL item 2), not a channel-count fix.
  HARD_FAIL_FAIRNESS: social-scramble ALSO reaches positive -> reject the operationalization; OR power/affiliation
    redundant with an existing channel (esp. VAD) -> relabeling.

SELF-TEST (planted social world; the LIGHT local gate; NO data; discriminators MUST FIRE + survive scale):
  Plant a world where PHYSICAL concepts ground via SENSORIMOTOR channels and SOCIAL concepts carry a coherent 2D
  power x affiliation signal but INCOHERENT sensorimotor AND INCOHERENT VAD/affect values (so they ground ONLY through the
  social channel; VAD is present-but-uninformative -> the affect-ablation is meaningful). Then:
  (a) sensorimotor + VAD channels only (WITHOUT-social, affect KEPT) -> SOCIAL un-grounded (affect present but does not
      ground it -> the affect-ablation discriminator fires);
  (b) +power/affiliation channels -> SOCIAL reach flips positive (the mechanism fires);
  (c) scramble the power/affiliation core values -> the gain vanishes (fairness discriminator fires);
  (d) power/affiliation non-redundant with BOTH the sensorimotor AND the VAD channels (correlation gate fires).
  Scale-invariant in expectation (per-domain reach fraction) -> DISCRIMINATOR-MUST-SURVIVE-SCALE Path C planted-preview.

## Compute architecture
class (a) batched-GPU-capable but CPU-fast for the eval (dense [n,n]@[n,d] diffusion, n capped ~6000, seconds/seed on CPU;
same regime as the reused a519 engine + the v1 reach cell + the Anchor 1 magnitude cell). Storage SHARDED (each concept
its own grounded vector; no bundling). SELF-TEST planted-only (seconds, tiny n) runs LOCAL. SMOKE uses source="cn" (LOCAL
relations.jsonl; NO CSKG download) on a SMALL core + a SOCIAL/SOCIAL_RELATIONAL/PHYSICAL probe subset -- validates the
mechanism + all 3 fairness discriminators (social-scramble, correlation gate, affect-ablation) fire only. FULL (CSKG
assembly + all domains + social-relational sub-domain, multi-seed) routes to remote_cpu_queue (graph parse dominates;
CPU / numpy diffusion; Tier B).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor/sec.13/sec.16/sec.17):
  arms_differ_verified (>=3 distinct arm sigs: mechanism-with-social / mechanism-without-social-keep-affect / scrambled)
  at self-test gate; final_metrics_atomicity=tmp_replace (write_metrics uses os.replace); except SystemExit before except
  Exception (no BaseException / bare); crlb: per-probe cosine chance ~0, std~1/sqrt(S) in z-err space (THEORETICAL),
  HARD_PASS strictly above 0 by +0.15; baseline_in_band: SOCIAL WITHOUT-social sim ~+0.015 is the in-band (barely-reaching)
  baseline by construction (reproduces the base v1 reach cell's SOCIAL result); discriminator-survives-scale: planted
  social self-test fires the affect-ablation gap + scramble collapse at full reach logic (Path C planted-preview + Path B
  scale-invariance of the reach fraction); HP_SCOPE: SOCIAL-sim-pass + affect-ablation gate apply to MECHANISM_WITH_SOCIAL
  vs MECHANISM_WITHOUT_SOCIAL_KEEP_AFFECT + SCRAMBLED only; calibration_check=default_ok_for_this_regime (engine + reach
  defaults inherited from the validated v1 reach cell); progress_logging=print_flush_true; cell_chunked=false (single
  graph, seeds cheap); start_marker + crash_diagnostic present; heartbeat via per-seed logs; cardinality_ok
  EXPECTED_N_UNITS=n_seeds; provenance: curated circumplex coordinates are cited from the public-domain IPIP-IPC octant
  geometry (no acquisition); optional circumplex CSV -> data/grounding_testbed/ (gitignored; NOT canonical
  substrate_index; never git add -A).
"""

import argparse
import hashlib
import json
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

ANCHOR_NAME = "spanning_grounded_core_reach_social_v1"
TESTBED = os.path.join(_REPO, "data", "grounding_testbed")
CIRCUMPLEX_CSV = os.path.join(TESTBED, "social_circumplex_ratings.csv")  # OPTIONAL; word,power,affiliation; NOT acquired

# ---------------------------------------------------------------------------
# CURATED INTERPERSONAL-CIRCUMPLEX (power x affiliation) coordinate lexicon.
# CITED@Interpersonal-Circumplex (Leary 1957; Wiggins IAS; IPIP-IPC octant markers, public-domain instrument).
# 8 octants at 45-deg spacing on the dominance(vertical) x warmth(horizontal) plane:
#   PA assured-dominant (+1.4, 0)   NO gregarious-extraverted (+1.0,+1.0)   LM warm-agreeable (0,+1.4)
#   JK unassuming-ingenuous (-1.0,+1.0)   HI unassured-submissive (-1.4,0)   FG aloof-introverted (-1.0,-1.0)
#   DE cold-hearted (0,-1.4)   BC arrogant-calculating (+1.0,-1.0)
# Values are UNIFORM over the whole vocabulary; z-scored downstream; absent words -> NaN (honest no-coverage).
# Two channels: POWER (dominance/control) + AFFILIATION (warmth/solidarity).
# ---------------------------------------------------------------------------
# (power, affiliation) per term.
CIRCUMPLEX = {
    # --- trait adjectives (crisp octant markers; the RANGE-giving core anchors + relational probes) ---
    "dominant": (1.4, 0.0), "assertive": (1.2, 0.2), "commanding": (1.4, -0.2), "authoritative": (1.3, 0.0),
    "forceful": (1.3, -0.3), "bossy": (1.2, -0.5), "domineering": (1.2, -0.8), "controlling": (1.2, -0.6),
    "outgoing": (1.0, 1.0), "sociable": (0.8, 1.2), "gregarious": (1.0, 1.0), "extraverted": (1.0, 0.9),
    "cheerful": (0.5, 1.1), "enthusiastic": (0.9, 0.9), "lively": (0.9, 0.9),
    "warm": (0.0, 1.4), "friendly": (0.2, 1.3), "kind": (0.0, 1.4), "affectionate": (0.0, 1.3),
    "agreeable": (-0.1, 1.3), "caring": (0.0, 1.3), "tender": (-0.2, 1.2), "gentle": (-0.3, 1.2),
    "compassionate": (0.0, 1.3), "loving": (0.1, 1.4), "cordial": (0.1, 1.2), "considerate": (-0.1, 1.2),
    "modest": (-1.0, 0.9), "humble": (-1.0, 0.8), "unassuming": (-1.0, 0.9), "sincere": (-0.5, 1.0),
    "trusting": (-0.7, 1.0), "meek": (-1.2, 0.6), "gullible": (-0.9, 0.7),
    "submissive": (-1.4, 0.0), "timid": (-1.3, 0.1), "shy": (-1.2, 0.1), "passive": (-1.2, -0.1),
    "obedient": (-1.2, 0.3), "subordinate": (-1.3, 0.0), "servile": (-1.3, 0.1), "docile": (-1.2, 0.3),
    "aloof": (-1.0, -1.0), "withdrawn": (-1.0, -0.9), "introverted": (-0.9, -0.9), "distant": (-0.7, -1.1),
    "reserved": (-0.8, -0.7), "reclusive": (-1.0, -1.0), "detached": (-0.8, -0.9),
    "cold": (0.0, -1.4), "unfriendly": (-0.2, -1.3), "cruel": (0.3, -1.4), "hostile": (0.5, -1.3),
    "harsh": (0.4, -1.2), "ruthless": (0.8, -1.3), "heartless": (0.1, -1.4), "callous": (0.1, -1.3),
    "arrogant": (1.0, -1.0), "calculating": (0.8, -1.0), "manipulative": (0.8, -1.1), "tyrannical": (1.3, -1.0),
    "cunning": (0.6, -0.9), "scheming": (0.7, -1.0), "boastful": (1.0, -0.7),
    # --- social roles / relations ---
    "leader": (1.3, 0.3), "boss": (1.2, -0.2), "ruler": (1.4, -0.4), "master": (1.3, -0.3), "chief": (1.3, 0.1),
    "commander": (1.4, -0.2), "captain": (1.2, 0.2), "king": (1.4, 0.0), "president": (1.3, 0.1),
    "manager": (1.0, 0.1), "superior": (1.2, -0.2), "guardian": (0.9, 0.7), "protector": (0.9, 0.8),
    "follower": (-1.1, 0.3), "servant": (-1.2, 0.2), "subject": (-1.0, 0.0), "inferior": (-1.2, -0.1),
    "dependent": (-1.0, 0.4), "slave": (-1.4, -0.1),
    "ally": (0.2, 1.2), "friend": (0.2, 1.3), "companion": (0.0, 1.1), "partner": (0.3, 1.0),
    "colleague": (0.2, 0.7), "peer": (0.0, 0.5), "neighbor": (0.0, 0.6), "parent": (0.8, 0.9),
    "enemy": (0.4, -1.3), "rival": (0.6, -0.9), "stranger": (-0.2, -0.5), "opponent": (0.5, -0.9),
    # --- social-STRUCTURAL / institutional / relational nouns (best-effort circumplex placement; the PRIMARY probes) ---
    "hierarchy": (1.2, -0.6), "authority": (1.3, -0.2), "rank": (1.0, -0.3), "dominance": (1.4, -0.3),
    "leadership": (1.2, 0.3), "command": (1.3, -0.2), "power": (1.4, -0.3), "control": (1.2, -0.4),
    "obedience": (-1.2, 0.3), "servitude": (-1.3, -0.2), "subjugation": (-1.3, -0.4), "oppression": (1.2, -1.1),
    "tyranny": (1.3, -1.1), "exploitation": (0.9, -1.1),
    "loyalty": (-0.2, 1.2), "trust": (0.0, 1.1), "friendship": (0.2, 1.3), "kinship": (0.0, 1.1),
    "fellowship": (0.2, 1.1), "solidarity": (0.3, 1.2), "alliance": (0.3, 1.1), "cooperation": (0.1, 1.1),
    "partnership": (0.3, 1.0), "marriage": (0.1, 1.2), "community": (0.2, 1.0), "belonging": (-0.2, 1.0),
    "betrayal": (0.4, -1.2), "conflict": (0.5, -1.0), "rivalry": (0.6, -0.9), "hostility": (0.4, -1.2),
    "etiquette": (0.2, 0.6), "courtesy": (-0.1, 0.9), "respect": (0.3, 0.7), "politeness": (-0.2, 0.8),
    "manners": (0.0, 0.6), "reputation": (0.6, 0.2), "status": (0.9, -0.1), "prestige": (1.0, 0.1),
    "honor": (0.5, 0.6), "dignity": (0.4, 0.5),
    "debt": (-0.8, -0.3), "obligation": (-0.5, 0.1), "duty": (-0.2, 0.4), "ownership": (1.0, -0.4),
    "possession": (0.9, -0.3), "contract": (0.2, 0.0), "agreement": (0.1, 0.6), "treaty": (0.3, 0.5),
    "citizenship": (0.2, 0.6), "membership": (0.1, 0.7), "tradition": (0.1, 0.5), "custom": (0.0, 0.5),
    "committee": (0.2, 0.4), "bureaucracy": (0.6, -0.5), "institution": (0.5, -0.2), "council": (0.5, 0.3),
    "justice": (0.6, 0.3), "fairness": (0.2, 0.7), "equality": (0.0, 0.8),
}

# SOCIAL CORE ANCHORS (added to the spanning core so the power/affiliation channels have RANGE to diffuse -- the social
# coordinate is itself a grounding-core primitive per the hippocampal-social-space / circumplex literature). Trait/role
# terms spanning all 8 octants; DISJOINT from the SOCIAL_RELATIONAL probe set below; likely ConceptNet nodes.
SOCIAL_CORE_ANCHORS = [
    "dominant", "submissive", "warm", "cold", "friendly", "hostile", "leader", "follower", "boss", "servant",
    "kind", "cruel", "outgoing", "shy", "arrogant", "humble", "master", "enemy", "ally", "gentle",
    "commanding", "obedient", "sociable", "aloof", "loving", "harsh", "superior", "inferior", "trusting", "distant",
]

# SOCIAL-RELATIONAL trait/role probes (out-of-core; DISJOINT from anchors; the crisp circumplex-coverage demonstration,
# mapped to SOCIAL_RELATIONAL -- the parallel to Anchor 1's MATH_NUMERAL probes). Span the circumplex octants.
SOCIAL_RELATIONAL_PROBES = [
    "assertive", "gregarious", "affectionate", "agreeable", "modest", "timid", "passive", "withdrawn",
    "unfriendly", "ruthless", "manipulative", "domineering", "cordial", "meek", "reclusive", "callous",
    "cunning", "considerate", "docile", "boastful",
]

# ---- Extended channel set: the 11 base channels + 2 social power/affiliation channels ----
POW = ("power", "_computed", "power")
AFF = ("affiliation", "_computed", "affiliation")
CANDIDATES = list(base.CANDIDATES) + [POW, AFF]
ATTR_NAMES = [c[0] for c in CANDIDATES]
NEW_CHANNEL_NAMES = ["power", "affiliation"]
BASE_CHANNEL_NAMES = [c[0] for c in base.CANDIDATES]
VAD_CHANNEL_NAMES = ["valence", "arousal", "dominance"]   # Warriner affect channels kept in the WITHOUT-social arm

DOMAINS = list(base.DOMAINS) + ["SOCIAL_RELATIONAL"]

# ---- Arms ----
MECH_WITH = "MECHANISM_WITH_SOCIAL"
MECH_WITHOUT = "MECHANISM_WITHOUT_SOCIAL_KEEP_AFFECT"   # affect-ablation arm: drop power/affiliation, KEEP VAD
SCR = "SCRAMBLED_SOCIAL"

# ---- Pre-registered bands ----
SIM_FLOOR = base.SIM_FLOOR                 # 0.30 per-probe cosine -> reached (reuse v1 band)
MIN_REACH_CHANNELS = base.MIN_REACH_CHANNELS
DIM = base.DIM
HOPS = base.HOPS
REDUNDANT_R = base.REDUNDANT_R             # 0.70 pairwise-correlation redundancy threshold
SOCIAL_SIM_PASS = 0.15                     # SOCIAL mean sim_mech HARD_PASS floor (research note Section 4 item 2)
SCR_MAX_SIM = 0.05                         # scrambled SOCIAL mean sim must stay at/below ~0 (null tolerance; fairness)
ABLATION_MIN_REL = 0.50                    # WITHOUT-social (VAD kept) must lose >= 50% relative of the gain
ABLATION_MIN_FLOOR = 0.10                  # < 10% relative collapse -> gain carried by affect not social (AFFECT_RELABEL)
MIN_ABS_GAIN = 0.10                        # WITH minus WITHOUT must be a meaningful absolute gain

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
# Power / affiliation column maps + extended attribute matrix.
# ---------------------------------------------------------------------------
def build_computed_colmaps():
    """Return {'power': {word: val}, 'affiliation': {word: val}} curated circumplex maps (+ optional staged CSV fused for
    uncovered words). Uniform over the whole vocabulary; no fabrication for words absent from the lexicon."""
    powm = {base._norm_word(k): v[0] for k, v in CIRCUMPLEX.items()}
    affm = {base._norm_word(k): v[1] for k, v in CIRCUMPLEX.items()}
    csv_used = False
    csv_n = 0
    if os.path.exists(CIRCUMPLEX_CSV):
        try:
            with open(CIRCUMPLEX_CSV, encoding="utf-8", errors="replace") as f:
                header = f.readline().rstrip("\n").rstrip("\r").split(",")
                lh = [h.strip().lower() for h in header]
                wi = lh.index("word") if "word" in lh else 0
                pi = lh.index("power") if "power" in lh else 1
                ai = lh.index("affiliation") if "affiliation" in lh else 2
                for line in f:
                    p = line.rstrip("\n").rstrip("\r").split(",")
                    if len(p) <= max(wi, pi, ai):
                        continue
                    try:
                        pv = float(p[pi].strip())
                        av = float(p[ai].strip())
                    except ValueError:
                        continue
                    w = base._norm_word(p[wi])
                    if w and w not in powm:                 # curated coordinates take priority
                        powm[w] = pv
                        affm[w] = av
                        csv_n += 1
            csv_used = True
        except Exception as e:
            _log("circumplex CSV present but unreadable (%s); curated-only" % type(e).__name__)
    return dict(power=powm, affiliation=affm), dict(csv_used=csv_used, csv_n=csv_n)


def build_attr_matrix_ext(words, col_maps, computed):
    """[n, K] extended attribute matrix over CANDIDATES (base file channels + computed power/affiliation). NaN where a
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
# Pre-flight pairwise-correlation gate: power/affiliation must be non-redundant (ESP. vs VAD).
# ---------------------------------------------------------------------------
def correlation_gate(Y_core, present_core):
    """Max |pearson r| of each NEW channel with every BASE channel over the core. Also reports the specific VAD
    correlations (the relabeling risk). Returns audit + a redundant flag."""
    audit = {}
    redundant_any = False
    for nc in NEW_CHANNEL_NAMES:
        ci = ATTR_NAMES.index(nc)
        max_r = 0.0
        arg = None
        vad_r = {}
        for bc in BASE_CHANNEL_NAMES:
            bi = ATTR_NAMES.index(bc)
            both = present_core[:, ci] & present_core[:, bi]
            if int(both.sum()) < 10:
                continue
            r = eng._pearson(Y_core[both, ci], Y_core[both, bi])
            if bc in VAD_CHANNEL_NAMES:
                vad_r[bc] = round(float(r), 3)
            if abs(r) > abs(max_r):
                max_r = r
                arg = bc
        redundant = bool(abs(max_r) >= REDUNDANT_R)
        redundant_any = redundant_any or redundant
        audit[nc] = dict(max_abs_r=round(float(max_r), 3), vs=arg, redundant=redundant, vad_r=vad_r)
    return dict(per_new_channel=audit, redundant_any=redundant_any)


def orthogonalize_new_vs_vad(Y, present, core_mask):
    """Residualize the power/affiliation channels against the VAD/affect channels (fit least-squares on CORE rows with full
    coverage -- leakage-safe; apply the core-fit coefficients to ALL rows). This is the ATL-hub note's mandated decorrel-
    ation (Pitfall #1: |r|>0.5 -> orthogonalize) that turns the RAW (affect-redundant) circumplex coordinate into the
    affect-RESIDUAL social-relational channel -- i.e. the part of power/affiliation NOT explained by valence/arousal/
    dominance. This is the channel-level implementation of the mandatory affect-ablation: the FULL then tests whether the
    residual social content grounds SOCIAL beyond the affect baseline. Rows where the channel is present but VAD is not
    cannot be residualized -> set NaN (honest: we can only claim affect-residual social content where affect is removable).
    Mutates + returns Y (a copy) + a report."""
    Y = Y.copy()
    vad_idx = [ATTR_NAMES.index(v) for v in VAD_CHANNEL_NAMES]
    core = np.where(core_mask)[0]
    report = {}
    for nc in NEW_CHANNEL_NAMES:
        ci = ATTR_NAMES.index(nc)
        fit_mask = present[core, ci].copy()
        for vi in vad_idx:
            fit_mask = fit_mask & present[core, vi]
        rows = core[fit_mask]
        apply_mask = present[:, ci].copy()
        for vi in vad_idx:
            apply_mask = apply_mask & present[:, vi]
        if rows.shape[0] < 10:
            # cannot residualize -> keep raw (report the gap); the RAW correlation gate will govern the fairness verdict.
            report[nc] = dict(residualized=False, reason="insufficient_core_vad_overlap", n_fit=int(rows.shape[0]))
            continue
        X = np.column_stack([Y[rows][:, vi] for vi in vad_idx] + [np.ones(rows.shape[0])])
        yv = Y[rows, ci]
        beta, _res, _rank, _sv = np.linalg.lstsq(X, yv, rcond=None)
        # residual for every row with full VAD coverage; others -> NaN (no affect-removable coverage).
        newcol = np.full(Y.shape[0], np.nan, dtype=np.float64)
        ar = np.where(apply_mask)[0]
        Xa = np.column_stack([Y[ar][:, vi] for vi in vad_idx] + [np.ones(ar.shape[0])])
        newcol[ar] = Y[ar, ci] - (Xa @ beta)
        Y[:, ci] = newcol
        report[nc] = dict(residualized=True, n_fit=int(rows.shape[0]), n_applied=int(ar.shape[0]),
                          beta_vad=[round(float(b), 3) for b in beta[:-1]], intercept=round(float(beta[-1]), 3))
    present2 = np.isfinite(Y)
    return Y, present2, report


def select_channels(Y_core, present_core, include_new):
    """Channels with variance over the core; optionally include the new power/affiliation channels. Returns index list
    into CANDIDATES (aligned with Y columns)."""
    sel = []
    for ci, name in enumerate(ATTR_NAMES):
        if (name in NEW_CHANNEL_NAMES) and (not include_new):
            continue
        col = Y_core[:, ci]
        if int(present_core[:, ci].sum()) >= 10 and np.nanstd(col) > 1e-6:
            sel.append(ci)
        elif name in NEW_CHANNEL_NAMES and include_new and int(present_core[:, ci].sum()) >= 5:
            sel.append(ci)   # new channels kept at a lower coverage floor (small core social-term count)
    return sel


def _vad_selected(sel_idx):
    """True iff at least one VAD/affect channel is in the selection (the affect-ablation is only meaningful if the
    WITHOUT-social arm actually keeps affect)."""
    names = set(ATTR_NAMES[i] for i in sel_idx)
    return sorted(names & set(VAD_CHANNEL_NAMES))


# ---------------------------------------------------------------------------
# Reach eval (adapted bit-faithful from exp_spanning_grounded_core_reach_v1.reach_eval; adds per-domain MEAN sim_mech +
# arbitrary channel-subset + social sub-domain). Same _diffuse_attr, _cos, global z-scoring, SOCIAL-SPECIFIC scramble.
# ---------------------------------------------------------------------------
def reach_eval_ext(words, edges, Y, present, sel_idx, core_mask, probe_domain, seed, device, soc_channel_idx=None):
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
    # SOCIAL-SPECIFIC scramble (contract fairness gate): permute ONLY the power/affiliation column(s) across the core
    # nodes, keeping every other channel intact -> isolates whether the social GAIN is genuine channel content (permuted-
    # social gain must vanish) rather than the global "all-values" scramble that destroys every channel.
    if soc_channel_idx is None:
        soc_channel_idx = set(ATTR_NAMES.index(nm) for nm in NEW_CHANNEL_NAMES)
    new_cols = [k for k, ci in enumerate(sel_idx) if ci in soc_channel_idx]
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
# Planted social self-test (LIGHT; discriminators MUST fire; scale-invariant).
# ---------------------------------------------------------------------------
def _planted_social_world(seed):
    """Plant a world where PHYSICAL concepts carry a coherent SENSORIMOTOR signal (ground via the sensorimotor channels)
    and SOCIAL concepts carry a coherent 2D power x affiliation signal but INCOHERENT (per-node noise) sensorimotor AND
    INCOHERENT VAD/affect values (so they ground ONLY through the social channel; VAD is present-but-uninformative -- the
    affect-ablation is meaningful: keeping VAD but dropping social must collapse social reach). Power/affiliation are
    drawn INDEPENDENTLY of the VAD noise for social nodes (decorrelated -> correlation gate passes vs VAD). Edges are built
    PER-DOMAIN by the informative-latent proximity (physical: sensorimotor cosine; social: 2D power/affiliation distance)
    so diffusion carries the right coordinate. Channels: 4 sensorimotor + 3 VAD + [power, affiliation].
    Returns (words, edges, Y, present, core_mask, probe_domain, sensorimotor+vad idx, all idx)."""
    rng = np.random.default_rng(seed)
    n_phys_core, n_soc_core = 30, 30
    n_phys_probe, n_soc_probe = 12, 12
    n = n_phys_core + n_soc_core + n_phys_probe + n_soc_probe
    D_sm = 4
    D_vad = 3
    K = D_sm + D_vad + 2                                    # 4 sensorimotor + 3 VAD + power + affiliation
    sm_latent = np.zeros((n, D_sm), dtype=np.float64)      # sensorimotor latent (physical only; social = ~0)
    soc_latent = np.zeros((n, 2), dtype=np.float64)        # 2D power x affiliation latent (social clusters on it)
    Y = np.full((n, K), np.nan, dtype=np.float64)
    node_dom = {}
    is_core = np.zeros(n, dtype=bool)
    dom_list = []
    idx = 0
    groups = [("PHYSICAL", n_phys_core, True), ("SOCIAL", n_soc_core, True),
              ("PHYSICAL", n_phys_probe, False), ("SOCIAL", n_soc_probe, False)]
    for dom, cnt, core in groups:
        for _ in range(cnt):
            if dom == "PHYSICAL":
                v = rng.standard_normal(D_sm)                          # coherent sensorimotor signal (varies per node)
                sm_latent[idx] = v
                Y[idx, :D_sm] = v + 0.2 * rng.standard_normal(D_sm)
                Y[idx, D_sm:D_sm + D_vad] = rng.standard_normal(D_vad)  # VAD noise for physical
                Y[idx, D_sm + D_vad] = rng.standard_normal()           # power noise (independent)
                Y[idx, D_sm + D_vad + 1] = rng.standard_normal()       # affiliation noise (independent)
            else:                                            # SOCIAL: sensorimotor + VAD = incoherent per-node noise
                # 2D social latent at 1.5x spread so the aligned power/affiliation signal dominates the unit-scale noise
                # on the 7 non-social channels in the cosine (2 signal dims vs 7 noise dims dilute the reach-fraction; the
                # signal magnitude must exceed the noise scale for a majority of planted social probes to clear SIM_FLOOR).
                pw = 1.5 * rng.standard_normal()                       # 2D social latent (power, affiliation)
                af = 1.5 * rng.standard_normal()
                soc_latent[idx] = (pw, af)
                # social-structural concepts have WEAK sensorimotor + affect engagement (you do not taste "hierarchy");
                # small-scale (0.25) DECORRELATED noise on those channels keeps them present-but-uninformative for the
                # social coordinate (affect-ablation stays meaningful: VAD present, does not ground social) without
                # diluting the reach cosine the way unit-scale noise would (the 2 signal dims must dominate 7 noise dims).
                Y[idx, :D_sm] = 0.25 * rng.standard_normal(D_sm)      # no coherent sensorimotor signal (weak)
                Y[idx, D_sm:D_sm + D_vad] = 0.25 * rng.standard_normal(D_vad)  # VAD present, DECORRELATED + weak
                Y[idx, D_sm + D_vad] = pw + 0.1 * rng.standard_normal()      # power aligned with social latent
                Y[idx, D_sm + D_vad + 1] = af + 0.1 * rng.standard_normal()  # affiliation aligned with social latent
            node_dom[idx] = dom
            dom_list.append(dom)
            is_core[idx] = core
            idx += 1
    present = np.isfinite(Y)
    # PER-DOMAIN edges: physical connects on sensorimotor cosine, social on 2D power/affiliation distance. Probes are
    # wired to their nearest CORE nodes (guaranteeing a correlation PATH to the grounded core exists -- the planted world
    # demonstrates the mechanism WHEN a path exists; probe-probe chains with no core path are a graph-sparsity artifact,
    # not a test of the channel). Core-core edges by the same proximity give the core internal structure to diffuse over.
    edges = set()
    phys = [i for i in range(n) if dom_list[i] == "PHYSICAL"]
    soc = [i for i in range(n) if dom_list[i] == "SOCIAL"]

    def _wire_domain(members, proximity, higher_is_closer, kcore=6, kprobe=6):
        core_m = [i for i in members if is_core_lookup[i]]
        for ai, a in enumerate(members):
            row = proximity[ai]
            order = np.argsort(-row) if higher_is_closer else np.argsort(row)
            targets = core_m                                 # everyone (core + probe) wires to nearest CORE members
            cand = [members[b] for b in order if members[b] in targets and members[b] != a]
            k = kcore if is_core_lookup[a] else kprobe
            for j in cand[:k]:
                edges.add((min(a, j), max(a, j)))

    is_core_lookup = {i: bool(is_core[i]) for i in range(n)}
    Lp = sm_latent[phys] / (np.linalg.norm(sm_latent[phys], axis=1, keepdims=True) + 1e-9)
    _wire_domain(phys, Lp @ Lp.T, higher_is_closer=True)
    sv = soc_latent[soc]
    soc_dist = np.sqrt(((sv[:, None, :] - sv[None, :, :]) ** 2).sum(axis=2))
    _wire_domain(soc, soc_dist, higher_is_closer=False)
    edges = np.array(sorted(edges), dtype=np.int64) if edges else np.zeros((0, 2), dtype=np.int64)
    without_idx = list(range(D_sm + D_vad))                # sensorimotor + VAD (affect kept, social dropped)
    all_idx = list(range(K))                               # + power + affiliation
    vad_idx = list(range(D_sm, D_sm + D_vad))
    return (words_stub(n), edges, Y, present, is_core, node_dom, without_idx, all_idx, vad_idx)


def words_stub(n):
    return ["p%d" % i for i in range(n)]


def _mechanism_selftest(device):
    w, e, Y, pr, cm, pd, without_idx, all_idx, vad_idx = _planted_social_world(7)
    soc_cols = {7, 8}   # planted layout: 4 sensorimotor (0..3) + 3 VAD (4..6) + power (7) + affiliation (8)
    # (a) sensorimotor + VAD channels only (WITHOUT-social, affect KEPT) -> SOCIAL un-grounded (affect-ablation fires).
    without = reach_eval_ext(w, e, Y, pr, without_idx, cm, pd, 7, device, soc_channel_idx=soc_cols)
    # (b) +power/affiliation channels -> SOCIAL reach flips positive.
    withsoc = reach_eval_ext(w, e, Y, pr, all_idx, cm, pd, 7, device, soc_channel_idx=soc_cols)
    soc_without = without["per_domain"]["SOCIAL"]["mean_sim"]
    soc_with = withsoc["per_domain"]["SOCIAL"]["mean_sim"]
    reach_without = without["per_domain"]["SOCIAL"]["reach"]
    reach_with = withsoc["per_domain"]["SOCIAL"]["reach"]
    scr_with = withsoc["per_domain"]["SOCIAL"]["mean_sim_scrambled"]
    phys_with = withsoc["per_domain"]["PHYSICAL"]["reach"]
    # discriminators.
    mech_fires = bool(soc_with == soc_with and soc_with >= SOCIAL_SIM_PASS
                      and (soc_without != soc_without or soc_without <= soc_with - 0.15))
    reach_moves = bool(reach_with == reach_with and reach_with >= 0.6
                       and (reach_without != reach_without or reach_with >= reach_without + 0.15))
    # (c) social-specific scramble kills the GAIN: with power/affiliation permuted across the core, the WITH-sim falls
    # back to (at/below) the without-social baseline. Not zeroed (other channels still present); "gain destroyed".
    scramble_fires = bool(scr_with == scr_with and (soc_with - soc_without) >= 0.15
                          and scr_with <= soc_without + 0.05)
    # (d) AFFECT-ABLATION explicit: the WITHOUT arm KEEPS VAD selected, yet SOCIAL still collapses -> the gain is genuine
    # social content, not affect bleed-through.
    vad_kept = _vad_selected(without_idx)
    affect_ablation_fires = bool(len(vad_kept) >= 1 and soc_without == soc_without
                                 and soc_without <= soc_with - 0.15)
    # (e) correlation gate: power/affiliation non-redundant with sensorimotor AND VAD over the core.
    cg = correlation_gate_planted(Y, pr, cm, without_idx)
    corr_ok = bool(not cg["redundant_any"])
    arms_differ = bool(withsoc["arm_sigs"]["mech"] != withsoc["arm_sigs"]["scr"])
    phys_ok = bool(phys_with == phys_with and phys_with >= 0.6)
    res = dict(social_sim_without=round(soc_without, 4) if soc_without == soc_without else None,
               social_sim_with=round(soc_with, 4) if soc_with == soc_with else None,
               social_reach_without=round(reach_without, 3) if reach_without == reach_without else None,
               social_reach_with=round(reach_with, 3) if reach_with == reach_with else None,
               social_sim_scrambled=round(scr_with, 4) if scr_with == scr_with else None,
               physical_reach_with=round(phys_with, 3) if phys_with == phys_with else None,
               vad_kept_in_without=vad_kept, correlation_gate=cg,
               mech_fires=mech_fires, reach_moves=reach_moves, scramble_fires=scramble_fires,
               affect_ablation_fires=affect_ablation_fires, corr_ok=corr_ok, arms_differ=arms_differ, phys_ok=phys_ok)
    ok = bool(mech_fires and reach_moves and scramble_fires and affect_ablation_fires
              and corr_ok and arms_differ and phys_ok)
    return ok, res


def correlation_gate_planted(Y, present, core_mask, without_idx):
    """Planted-world correlation gate: max |r| of the power/affiliation (last 2) columns vs the sensorimotor+VAD columns
    over the core (the affect channels are in without_idx)."""
    core = np.where(core_mask)[0]
    Yc = Y[core]
    Pc = present[core]
    ncols = Y.shape[1]
    audit = {}
    redundant_any = False
    for ci in range(ncols - 2, ncols):
        max_r = 0.0
        for bi in without_idx:
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
    # core-EXPANSION: add the social circumplex anchors (curated; gives power/affiliation range to diffuse)
    anchor_words = set(base._norm_word(w) for w in SOCIAL_CORE_ANCHORS)
    core_words = set(core_words) | anchor_words
    core_prov = dict(core_prov, n_social_anchors=len(anchor_words), n_core_with_anchors=len(core_words))
    probe_words = set()
    for dom in base.DOMAINS:
        for w in base.PROBES[dom]:
            probe_words.add(base._norm_word(w))
    for w in SOCIAL_RELATIONAL_PROBES:
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
    for w in SOCIAL_RELATIONAL_PROBES:
        nw = base._norm_word(w)
        if nw in idx and not core_mask[idx[nw]]:
            probe_domain[idx[nw]] = "SOCIAL_RELATIONAL"

    # PRE-FLIGHT correlation gate on the RAW curated circumplex channel (the FINDING: the interpersonal-circumplex warmth
    # axis is inherently valenced, so raw affiliation ~ Warriner valence; this is the affect-confound the hand-off flagged).
    cg_raw = correlation_gate(Y[core_mask], present[core_mask])
    _log("CORRELATION GATE (raw): %s" % cg_raw["per_new_channel"])
    # ATL-hub mandated decorrelation: residualize power/affiliation against VAD (fit on core) -> affect-RESIDUAL channel.
    Y, present, orth_report = orthogonalize_new_vs_vad(Y, present, core_mask)
    _log("ORTHOGONALIZE vs VAD: %s" % orth_report)
    # POST correlation gate: the residual channel must now be non-redundant with VAD (near-0 by construction on the fit
    # set; report it as the sanity check). The load-bearing fairness controls are now the SOCIAL-scramble + affect-ablation.
    cg = correlation_gate(Y[core_mask], present[core_mask])
    _log("CORRELATION GATE (post-orthogonalization): %s" % cg["per_new_channel"])

    sel_with = select_channels(Y[core_mask], present[core_mask], include_new=True)
    sel_without = select_channels(Y[core_mask], present[core_mask], include_new=False)
    new_selected = [ATTR_NAMES[i] for i in sel_with if ATTR_NAMES[i] in NEW_CHANNEL_NAMES]
    vad_kept = _vad_selected(sel_without)
    _log("channels WITH=%d WITHOUT=%d new_selected=%s vad_kept_in_without=%s" % (
        len(sel_with), len(sel_without), new_selected, vad_kept))

    probe_cov = {dom: sum(1 for i, d in probe_domain.items() if d == dom) for dom in DOMAINS}
    _log("probe coverage per domain: %s" % probe_cov)

    soc_cols = set(ATTR_NAMES.index(nm) for nm in NEW_CHANNEL_NAMES)
    seed_rows = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            rw = reach_eval_ext(words, edges, Y, present, sel_with, core_mask, probe_domain, seed, device,
                                soc_channel_idx=soc_cols)
            ro = reach_eval_ext(words, edges, Y, present, sel_without, core_mask, probe_domain, seed, device,
                                soc_channel_idx=soc_cols)
            if "error" in rw or "error" in ro:
                raise RuntimeError("reach error with=%s without=%s" % (rw.get("error"), ro.get("error")))
            if rw["arm_sigs"]["mech"] == rw["arm_sigs"]["scr"]:
                raise RuntimeError("ARMS_MUST_DIFFER seed=%d mech==scr" % seed)
            row = dict(seed=seed, with_social=rw["per_domain"], without_social=ro["per_domain"])
            seed_rows.append(row)
            write_partial(out_dir, seed, row)
            mw = rw["per_domain"]
            _log("seed=%d SOCIAL with_sim=%s without_sim=%s scr_sim=%s | SOCIAL_RELATIONAL with_sim=%s without_sim=%s "
                 "scr=%s" % (
                     seed, _r(mw["SOCIAL"]["mean_sim"]), _r(ro["per_domain"]["SOCIAL"]["mean_sim"]),
                     _r(mw["SOCIAL"]["mean_sim_scrambled"]), _r(mw["SOCIAL_RELATIONAL"]["mean_sim"]),
                     _r(ro["per_domain"]["SOCIAL_RELATIONAL"]["mean_sim"]),
                     _r(mw["SOCIAL_RELATIONAL"]["mean_sim_scrambled"])))
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
                correlation_gate_raw=cg_raw, orthogonalization=orth_report, correlation_gate=cg,
                channels_with=[ATTR_NAMES[i] for i in sel_with],
                channels_without=[ATTR_NAMES[i] for i in sel_without], new_selected=new_selected,
                vad_kept_in_without=vad_kept, probe_coverage=probe_cov, computed_meta=comp_meta,
                n_seeds=len(cfg["seeds"]))
    agg = aggregate_and_verdict(seed_rows, cg, vad_kept, meta)
    vmsg = ("%s || %s || SOCIAL sim with=%s without=%s scr=%s | SOCIAL_RELATIONAL sim with=%s without=%s scr=%s || "
            "affect_kept_in_without=%s corr_redundant=%s new_selected=%s || source=%s n=%d" % (
                agg["verdict"], agg["one_line"], _r(agg["social_sim_with"]), _r(agg["social_sim_without"]),
                _r(agg["social_sim_scrambled"]), _r(agg["socrel_sim_with"]), _r(agg["socrel_sim_without"]),
                _r(agg["socrel_sim_scrambled"]), vad_kept, cg["redundant_any"], new_selected, cfg["source"],
                gmeta["n_nodes"]))
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


def aggregate_and_verdict(seed_rows, cg, vad_kept, meta):
    # MEDIAN across seeds (per seed-fragility discipline).
    soc_with = _median_over_seeds(seed_rows, "with_social", "SOCIAL", "mean_sim")
    soc_without = _median_over_seeds(seed_rows, "without_social", "SOCIAL", "mean_sim")
    soc_scr = _median_over_seeds(seed_rows, "with_social", "SOCIAL", "mean_sim_scrambled")
    sr_with = _median_over_seeds(seed_rows, "with_social", "SOCIAL_RELATIONAL", "mean_sim")
    sr_without = _median_over_seeds(seed_rows, "without_social", "SOCIAL_RELATIONAL", "mean_sim")
    sr_scr = _median_over_seeds(seed_rows, "with_social", "SOCIAL_RELATIONAL", "mean_sim_scrambled")
    soc_reach_with = _median_over_seeds(seed_rows, "with_social", "SOCIAL", "reach")

    def _rel_collapse(with_v, without_v):
        if with_v != with_v or with_v <= 1e-6:
            return float("nan")
        base_v = without_v if (without_v == without_v) else 0.0
        return max(0.0, (with_v - base_v) / abs(with_v))

    gain_soc = (soc_with - soc_without) if (soc_with == soc_with and soc_without == soc_without) else float("nan")
    gain_sr = (sr_with - sr_without) if (sr_with == sr_with and sr_without == sr_without) else float("nan")
    # AFFECT-ABLATION relative collapse (WITHOUT-social KEEPS VAD): fraction of the WITH-social sim lost when
    # power/affiliation are removed while affect is retained.
    ablation_soc = _rel_collapse(soc_with, soc_without)
    ablation_sr = _rel_collapse(sr_with, sr_without)
    corr_ok = bool(not cg["redundant_any"])
    affect_kept = bool(len(vad_kept) >= 1)

    def _scramble_destroys(scr, without_v, gain):
        if gain != gain or gain < 0.05:
            return True                                       # no gain to defend -> vacuously ok (not inflation)
        return bool(scr == scr and scr <= without_v + 0.05)

    def _scramble_inflation(scr, without_v, gain):
        if gain != gain or gain < 0.10:
            return False
        return bool(scr == scr and scr > without_v + 0.5 * gain)

    scramble_ok_soc = _scramble_destroys(soc_scr, soc_without, gain_soc)
    scramble_ok_sr = _scramble_destroys(sr_scr, sr_without, gain_sr)
    scramble_bad = bool(_scramble_inflation(soc_scr, soc_without, gain_soc)
                        or _scramble_inflation(sr_scr, sr_without, gain_sr))

    # a genuine social-grounding win: sim clears the pass bar AND the social channel adds a MEANINGFUL, AFFECT-ABLATION-
    # carried, scramble-verified gain (gain >= 0.10 absolute AND >= ABLATION_MIN_REL relative, with VAD kept in WITHOUT).
    soc_pass = bool(soc_with == soc_with and soc_with >= SOCIAL_SIM_PASS
                    and gain_soc == gain_soc and gain_soc >= MIN_ABS_GAIN
                    and ablation_soc == ablation_soc and ablation_soc >= ABLATION_MIN_REL and scramble_ok_soc)
    sr_pass = bool(sr_with == sr_with and sr_with >= SOCIAL_SIM_PASS
                   and gain_sr == gain_sr and gain_sr >= MIN_ABS_GAIN
                   and ablation_sr == ablation_sr and ablation_sr >= ABLATION_MIN_REL and scramble_ok_sr)

    # affect-relabel detector: a claimed WITH-social sim above the bar whose gain does NOT collapse when social is removed
    # (VAD kept) -> the reach was carried by affect, not social-relational content.
    def _affect_relabel(with_v, gain, ablation):
        if with_v != with_v or with_v < SOCIAL_SIM_PASS:
            return False
        if gain != gain or gain < MIN_ABS_GAIN:              # no real gain over the VAD-kept baseline
            return True
        return bool(ablation == ablation and ablation < ABLATION_MIN_FLOOR)

    affect_relabel = bool(affect_kept and (_affect_relabel(soc_with, gain_soc, ablation_soc)
                                           or _affect_relabel(sr_with, gain_sr, ablation_sr))
                          and not (soc_pass or sr_pass))

    if scramble_bad or not corr_ok:
        verdict = "HARD_FAIL_FAIRNESS"
        one_line = ("fairness gate failed (scramble_bad=%s corr_redundant=%s) -> apparent gain is inflation/relabeling of "
                    "an existing channel, not social grounding" % (scramble_bad, cg["redundant_any"]))
    elif not affect_kept:
        verdict = "HARD_FAIL_AFFECT_ABLATION_VACUOUS"
        one_line = ("affect-ablation vacuous: no VAD channel selected in the WITHOUT-social arm -> cannot disambiguate "
                    "social-relational content from affect; re-spec core coverage")
    elif soc_pass or sr_pass:
        verdict = "SOCIAL_CHANNEL_GROUNDS_SOCIAL"
        one_line = ("power x affiliation channel moves SOCIAL grounding-reach positive (social sim %.3f, social-relational "
                    "sim %.3f) with scramble null + AFFECT-ABLATION-carried (social %.0f%% socrel %.0f%%, VAD kept) -> "
                    "gain is genuine social content, not relabeled affect; core-expansion fix REAL" % (
                        soc_with if soc_with == soc_with else float("nan"),
                        sr_with if sr_with == sr_with else float("nan"),
                        100 * (ablation_soc if ablation_soc == ablation_soc else 0.0),
                        100 * (ablation_sr if ablation_sr == ablation_sr else 0.0)))
    elif affect_relabel:
        verdict = "HARD_FAIL_AFFECT_RELABEL"
        one_line = ("SOCIAL reach did not survive the affect-ablation (WITHOUT-social keeps VAD, gain collapse < %.0f%%) "
                    "-> the apparent social reach is relabeled EMOTIONAL reach, not social-relational content" % (
                        100 * ABLATION_MIN_FLOOR))
    elif (soc_with == soc_with and soc_with <= 0) and (sr_with == sr_with and sr_with <= 0):
        verdict = "HARD_FAIL_CHANNEL_INSUFFICIENT"
        one_line = ("power x affiliation channel well-behaved (scramble fires) but SOCIAL still <= 0 (social %.3f "
                    "social-relational %.3f) -> residual needs mentalizing/theory-of-mind content or the metaphor-bridge, "
                    "not this channel" % (soc_with if soc_with == soc_with else float("nan"),
                                          sr_with if sr_with == sr_with else float("nan")))
    else:
        verdict = "MIDDLE_BAND"
        one_line = ("partial: SOCIAL sim %.3f social-relational sim %.3f; scramble null + corr-ok + VAD-kept but below "
                    "+%.2f pass bar or affect-ablation weak -> investigate before scaling (matches the Anchor-1 magnitude "
                    "MIDDLE_BAND prior: scalar/coordinate channels underperform for abstract domains)" % (
                        soc_with if soc_with == soc_with else float("nan"),
                        sr_with if sr_with == sr_with else float("nan"), SOCIAL_SIM_PASS))

    return dict(verdict=verdict, one_line=one_line,
                social_sim_with=_none(soc_with), social_sim_without=_none(soc_without),
                social_sim_scrambled=_none(soc_scr), socrel_sim_with=_none(sr_with),
                socrel_sim_without=_none(sr_without), socrel_sim_scrambled=_none(sr_scr),
                social_reach_with=_none(soc_reach_with),
                gain_social=_none(gain_soc), gain_socrel=_none(gain_sr),
                ablation_social_rel=_none(ablation_soc), ablation_socrel_rel=_none(ablation_sr),
                affect_kept_in_without=vad_kept, correlation_redundant=bool(cg["redundant_any"]),
                scramble_ok_social=scramble_ok_soc, scramble_ok_socrel=scramble_ok_sr,
                bands=dict(SOCIAL_SIM_PASS=SOCIAL_SIM_PASS, SCR_MAX_SIM=SCR_MAX_SIM, ABLATION_MIN_REL=ABLATION_MIN_REL,
                           ABLATION_MIN_FLOOR=ABLATION_MIN_FLOOR, MIN_ABS_GAIN=MIN_ABS_GAIN, SIM_FLOOR=SIM_FLOOR,
                           REDUNDANT_R=REDUNDANT_R), meta=meta)


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

    # LIGHT planted social self-test: discriminators MUST fire (runs in EVERY mode as the pre-flight gate).
    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                      verdict_msg="MECHANISM_SELFTEST_FAILED (planted power x affiliation channel did not fire reach / "
                                  "scramble did not collapse / affect-ablation did not fire / correlation gate flagged "
                                  "redundant): %s" % st_res,
                      summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(verdict="SELFTEST_PASS", run_mode="self_test",
                      verdict_msg="SELFTEST_PASS: planted power x affiliation channel flips SOCIAL reach positive; "
                                  "sensorimotor+VAD (affect kept) fails it; scramble collapses; affect-ablation fires; "
                                  "power/affiliation non-redundant; arms differ. %s" % st_res,
                      summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    # Real run: acquire base norm data (self-acquire path in base cell), build computed social circumplex maps.
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
    _log("computed social circumplex lexicon: power=%d affiliation=%d csv=%s" % (
        len(computed["power"]), len(computed["affiliation"]), comp_meta))
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
