# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 9-arm per-checkpoint prediction hash-differ;
#   arms_differ_exempted=[["bow","never_crutch"]] declared)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (symbolic KB-lookup + vote-count pipeline; no capacity/noise-floor
#   discriminator threshold applies -- 3-way discrete classification accuracy on a real benchmark)
# - HP_SCOPE: {dev_checkpoint_eval: [tier_fire_drop, tier_comprehension_lift, tier_scramble_control,
#   tier_consolidation_fidelity, combined_evidence_promotion, ablation_underperformance]} --
#   ALWAYS/NEVER arms + binary_baseline_verdict are diagnostic/informational, not HP-gated
# - cardinality_ok: EXPECTED_N_CHECKPOINTS=5, EXPECTED_N_ARMS=9
# - per-unit failure-class instrumentation (no bare except; degraded_scoring budget 2%)
# - calibration_check: adaptive_with_discriminator_gate (GATE_THRESH = median BoW-margin; PLUS
#   novelty_thresh calibrated via calibrate_novelty_threshold on this run's own SEMANTIC-BUCKET
#   vocabulary (v2 change, see below) -- both computed fresh at run start, logged, not hand-tuned)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL Library / consolidation_pass / HDFactStore / ScriptLibrary /
#   build_instance_register / match_or_spawn / CharTrigramEncoder objects (real_code_path_exercised);
#   no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-11_crutch_fade_semantic_cluster_key_v2.md for the v2 ONE-VARIABLE pre-reg
# (extends preregs/2026-08-10_crutch_fade_prelim_tier_staged_consolidation_v1.md, the 3-tier
# pre-reg this forks from; that in turn extends preregs/2026-08-10_crutch_fade_social_iqa_v1.md,
# the base binary cell's pre-reg).
"""exp_crutch_fade_social_iqa_v2_semantic_cluster_key -- ONE-VARIABLE fork of
exp_crutch_fade_social_iqa_v1.py (2026-08-11). THE ONLY CHANGE: the CA3/DG near-concept SWEEP
clustering KEY fed into ScriptLibrary.match_or_spawn is swapped from relation_family(idx, pk) (the
CSKG relation-TYPE label, e.g. 'xattr'/'xeffect') to semantic_relation_key(idx, pk) (an OWNED,
from-scratch, zero-borrowed-vector char-trigram-HD-embedding locality-sensitive-hash bucket over the
pair's own two concept strings). This is the disk-diagnosed root-cause fix identified in
notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md (Headline Finding + Gap
G2): the v1 3-tier FULL run (data/exp_crutch_fade_social_iqa_v1_3tier_seed7/metrics.json,
verdict=HARD_FAIL) found relation_family's ~33-40 CSKG relation-TYPE labels are "intrinsically too
coarse" a same-schema key (a relation TYPE spans huge, semantically heterogeneous swaths of common
sense) -- combined-evidence cluster promotions scored WORSE than raw crutch lookups
(tier_fidelity_ok=False, HP2; combined_acc=0.356 < cru_acc=0.369) and the 3-tier arm underperformed
the binary baseline on the coverage-controlled comprehension slice (comp_lift_covered 0.366 < 0.377,
HP3=False), even though fade itself grew MORE than binary (HP1=True, rel_drop 0.36 vs 0.12). EVERY
other design element (HUB_DEGREE_THRESH=500, CLUSTER_EXPOSURE_MULTIPLIER=4, PROMOTE_MIN_EXPOSURE/
CONSISTENCY, the 9-arm/5-checkpoint design, the frozen dev set, the real 1.15M-edge CSKG crutch) is
held BYTE-IDENTICAL to v1; only semantic_relation_key() replaces relation_family() at the ONE call
site inside update_prelim_and_generalize() (+ the matching novelty-threshold-calibration vocabulary
sample in run(), which is downstream bookkeeping of the same key swap, not a second variable). See
semantic_relation_key()'s own docstring below for the mechanism. Original v1 docstring (unchanged
mechanism description below, still accurate for everything except the clustering key) follows.

Composes: CRUTCH = data/cskg_foundation_v1 (1,238,686 typed spine edges, ATOMIC-dominant,
HARD_PASS-certified exp_cskg_foundation_v1), queried as a plain symbolic concept-pair index (NOT
kg_traversal.KGStore's Hebbian single-W substrate -- see prereg "Deviation" section: that store is
the SAME one Stage-2 sub-test B HARD_FAILED at CSKG cardinality, an unrelated open wall this cell
must not get confounded with). LIBRARY (native, strict) = hdlab.grounding_acquisition_loop.Library +
consolidation_pass(native_store=...) + hdlab.hd_fact_store.HDFactStore -- the validated
BANK->native-promotion connector (Test-A cleared: promote 5/5, guard 0/12 leaks, commit 07339e9c6).
FLAG = a predictive_coding-style relative-margin gate over BoW-candidate scores. PRELIM (new,
2026-08-10) = a SEPARATE, permanently-PENDING Library + a TRUST_LOW hd_fact_store.HDFactStore --
sub-threshold crutch-fills are RETAINED (not discarded) and PULLED at re-encounter (the fade lever).
GENERALIZATION (2026-08-10, KEY SWAPPED 2026-08-11) = hdlab.script_grain_acquisition_loop.
ScriptLibrary.match_or_spawn (CA3/DG clustering, now by SEMANTIC-EMBEDDING bucket instead of CSKG
relation-family) lets COMBINED evidence across related PRELIM pairs cross the STILL-STRICT native
promote gate even when no single pair does.

Question: as the substrate reads more of SIQa's train stream (context text only, no labels), does
the live CRUTCH fire LESS on repeat need for the SAME knowledge (fade) while held-out dev
comprehension RISES above a freshly-measured BoW baseline, and does a SCRAMBLED-content crutch fail
to reproduce any gain (proving real knowledge, not retrieval machinery, does the work)? EXTENDED
question (2026-08-10): does the 3-tier PRELIM/generalization architecture buy MORE fade than the
binary promote-or-discard baseline AT THE SAME STRICT GATE, without native fidelity collapsing --
the tradeoff the binary cliff (commit 74d310e11) could not resolve (fade required loosening the
gate, which broke fidelity)? v2 QUESTION (2026-08-11, THIS FILE): does swapping ONLY the clustering
KEY to a semantic-embedding bucket flip the two v1 HARD_FAIL flags (HP2 tier_fidelity_ok, HP3
comp_lift_covered) on the SAME real benchmark, holding everything else fixed?

9 arms x 5 checkpoints (0/10/25/50/100% of exposure), full frozen dev (1,954 items) evaluated at
every checkpoint: bow, never_crutch, always_crutch, gap_driven (BINARY BASELINE, unchanged),
scramble_crutch (unchanged) + gap_driven_3tier (FULL mechanism), gap_driven_3tier_no_generalization
(ablation A: retain+pull, no clustering), gap_driven_3tier_no_pull (ablation B: retain, no pull),
scramble_crutch_3tier (the 3-tier's OWN scramble control). Per-item routing tag (BOW_RESOLVED/
LIBRARY_RESOLVED/PRELIM_RESOLVED/CRUTCH_RESOLVED/ABSTAINED). A re-encounter fade rate (coordinator
refinement) and a crutch-RETRIEVAL-COVERAGE-controlled comprehension read (second coordinator
refinement, mid-3-tier-build, per sibling diagnosis e9ee736ec: overall comprehension is capped by
CSKG's ~45-54% retrieval-coverage ceiling independent of consolidation quality) are both reported
alongside the two headline curves.

Modes:
  --self-test  Real-code-path check: tiny synthetic CSKG index, real Library/consolidation_pass/
               HDFactStore/ScriptLibrary/match_or_spawn objects, verifies routing/promotion/
               re-encounter/PRELIM-retain/combined-evidence-promotion/fidelity-guard machinery. No
               network.
  --smoke      Capped exposure (SMOKE_TRAIN_CAP contexts) + capped dev (SMOKE_DEV_CAP items),
               FULL CSKG index (real scale) -- discriminator-preview per DISCRIMINATOR-MUST-
               SURVIVE-SCALE (the crutch/gate machinery is exercised against the REAL 1.24M-edge
               store, only the exposure/eval VOLUME is reduced). Bumped 3000/250 -> 15000/400
               2026-08-10 (old scale measured zero native promotions; too small to fire the new
               combined-evidence discriminator).
  --full       Full 33,410-context exposure stream, full 1,954-item frozen dev, full CSKG index.
  --seed N / --out-tag TAG  thread a run seed + a distinct output-path suffix (multi-seed FULL
               dispatch without clobbering the committed binary-baseline history).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import numpy as np  # noqa: E402

from hdlab.grounding_acquisition_loop import (  # noqa: E402
    Library, context_vector, consolidation_pass,
    PROMOTE_MIN_EXPOSURE, PROMOTE_MIN_CONSISTENCY, MIN_CONFIRM, PROMOTE_RELATION,
    schema_consistency_split_half, _vote_margin,
)
from hdlab.hd_fact_store import HDFactStore  # noqa: E402
from hdlab.script_grain_acquisition_loop import (  # noqa: E402
    ScriptLibrary, build_instance_register, calibrate_novelty_threshold,
)
from tools.exp_checkpoint import (  # noqa: E402
    unit_key as _unit_key, completed_units as _completed_units,
    record_unit as _record_unit, load_units as _load_units,
)
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402 -- v2 ONE-VARIABLE import:
# OWNED, from-scratch, zero-borrowed-vector text encoder (registry row 12 `char_trigram_encoder`,
# WIRED, 14+ existing consumers) -- used ONLY to build the new semantic clustering key (see
# semantic_relation_key() below). NOT scale_win_tinytransformer_encoder (registry row 3): that
# encoder lives inside experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py as a torch
# nn.Module requiring a reloaded MLM training checkpoint (ckpt_seed_7.pt) + its own tokenizer --
# an exp-cell-internal, TRAPPED_SHARED asset, not a portable importable module (registry itself
# flags it "kind: exp-cell", not "kind: hdlab-module"). The design audit's own smallest-first-
# experiment spec explicitly names char-trigram as the fallback "if [the tiny-transformer encoder
# is] not readily composable" -- it is not (torch model + checkpoint reload + remote-portability
# risk for a light CPU-only symbolic cell), so this fork takes the fallback per that same spec.

ANCHOR_NAME = "crutch_fade_social_iqa_v2_semantic_cluster_key"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")
SIQA_DIR = os.path.join(REPO_ROOT, "data", "corpora", "social_iqa", "hf_dataset")

CHECKPOINTS = [0.0, 0.10, 0.25, 0.50, 1.00]  # MEASURED@drill4 Section 2b
N_PASSES_PER_CHECKPOINT = 3
# SMOKE scale bumped 2026-08-10 (3-tier PRELIM build, see prereg "Smoke-scale change (disclosed)"):
# the old 3000/250 smoke MEASURED zero native promotions in prior history (base cell) -- too small
# to fire the NEW combined-evidence discriminator. 15000/400 matches the --diag scale that MEASURED
# real promotions (data/exp_crutch_fade_social_iqa_v1_diag_*), still << FULL (33410/1954).
SMOKE_TRAIN_CAP = 15000
SMOKE_DEV_CAP = 400
DEGRADED_BUDGET = 0.02
TRUST_WEIGHT = {"TRUST_HIGH": 1.0, "TRUST_MID": 0.6}

# ---- 3-tier PRELIM constants (2026-08-10, see preregs/2026-08-10_crutch_fade_prelim_tier_staged_
# consolidation_v1.md) ----
PRELIM_TRUST = "TRUST_LOW"                 # hd_fact_store.TRUST_LEVEL ladder, reused unmodified
PRELIM_SCHEMA_THRESH = 0.10                # SAME bar as consolidation_pass's own BANK gate default
CLUSTER_MIN_MEMBERS = 3                    # min distinct pairs before a cluster's combined evidence
                                            # is even considered (avoids single-pair "clusters")
NOVELTY_THRESH_FALLBACK = 0.15             # used only if calibrate_novelty_threshold can't discriminate
                                            # on this run's own synthetic pairs (defensive; logged)
RELATION_PREFIXES = ("/r/", "at:", "mw:")  # CSKG namespace prefixes stripped for relation_family()
# HUB_DEGREE_THRESH (2026-08-10, smoke-diagnosed fix, TWO iterations): the FIRST 3-tier smoke run
# (SMOKE_TRAIN_CAP=15000/hub_penalized/pme8) MEASURED tier_fidelity_ok=False -- combined_evidence_
# cluster promotions (n=38, acc=0.368) scored WORSE than raw CRUTCH_RESOLVED (acc=0.448). Root cause
# (same class as Fault-2, hub_penalized's own diagnosed pathology): relation-family clustering alone
# produced only n_clusters=2 by ck100 -- the two most common relation types swallow almost every
# prelim-eligible pair into one undifferentiated mega-schema, DOMINATED by SIQa-template hub concepts
# (MEASURED@compute_node_degree: 'happy' degree=8057, 'person' degree=7646, vs MEDIAN degree=1.0,
# 95th-pctile=24, 97th-pctile=31, 99th-pctile=50, 99.9th-pctile=356 -- an extremely skewed
# distribution). Draft 1 (threshold=30, ~97th pctile) MEASURED an OVER-correction: excludes so many
# pairs at the PAIR level (either of 2 concepts over threshold) that combined_evidence_promoted_n
# dropped to 0 by ck100 -- the crux mechanism went fully inert (HARD_FAIL COMBINED_EVIDENCE_NEVER_
# FIRES). MEASURED@node-degree histogram: >100=2047 nodes, >300=587, >500=301, >1000=81, >2000=16 --
# a genuine power-law tail, not a clean percentile cliff. Draft 2 (this value, 500) targets
# specifically the small super-hub tail (301 nodes, matching Fault-2's own "a handful of ... generic
# concepts" language) while leaving the vast majority of the vocabulary (including moderately-common
# words up to degree ~500) eligible -- re-MEASURED at smoke before FULL dispatch (see completion
# report for the confirming numbers).
HUB_DEGREE_THRESH = 500
# CLUSTER_EXPOSURE_MULTIPLIER (2026-08-10, THIRD iteration): threshold=500 MEASURED n_clusters STILL
# stuck at 2 -- hub-degree filtering alone doesn't fix fidelity because the mega-clusters are not
# primarily hub-node-driven; a broad CSKG relation TYPE (e.g. "xAttr"/"xEffect") is INTRINSICALLY
# semantically heterogeneous (spans huge, unrelated swaths of common sense), so relation-family alone
# is too coarse a "same schema" key regardless of node degree (MEASURED@smoke threshold=500:
# combined_evidence_cluster acc=0.261 n=23, still well below cru_acc=0.449). Principled compensating
# fix (not a clustering-key redesign, out of scope this cycle -- see completion report "next step"):
# require STRICTLY MORE combined evidence for the coarser cluster-grain gate than the single-item
# gate demands, reflecting that coarser grouping needs a larger, more convincing sample before its
# majority is trustworthy. The per-item promote_min_exposure/consistency gate is NEVER loosened --
# this makes the CLUSTER path's OWN gate stricter, never weaker, than the single-item path's.
CLUSTER_EXPOSURE_MULTIPLIER = 4

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "of", "to", "in", "on", "at", "by", "for", "with",
    "as", "is", "was", "were", "are", "be", "been", "being", "it", "its", "he", "she", "they",
    "him", "her", "them", "his", "their", "i", "you", "we", "me", "my", "your", "our", "this",
    "that", "these", "those", "not", "no", "so", "than", "then", "there", "here", "up", "out",
    "into", "over", "again", "very", "just", "would", "could", "should", "will", "shall", "can",
    "did", "do", "does", "had", "has", "have", "from", "all", "any", "some", "one", "two", "when",
    "what", "who", "which", "how", "why", "said", "upon", "others", "other", "before", "after",
})
TOKRE = re.compile(r"[a-z']+")


# =====================================================================================
# canon(): byte-identical to experiments/exp_cskg_foundation_v1.py::canon (copied inline,
# small pure function, attributed -- avoids importing a non-library experiment script).
def canon(label: str) -> str:
    s = label.strip().lower()
    out = []
    prev_us = True
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_us = False
        elif not prev_us:
            out.append("_")
            prev_us = True
    r = "".join(out)
    if r.endswith("_"):
        r = r[:-1]
    return r


def content_words(text: str) -> List[str]:
    return [w for w in TOKRE.findall(text.lower()) if w not in _STOPWORDS and len(w) > 1]


def pair_key(a: str, b: str) -> str:
    lo, hi = (a, b) if a <= b else (b, a)
    return f"{lo}::{hi}"


# =====================================================================================
# FAULT-2 diagnosis + fix (2026-08-10 coordinator follow-up): the smoke's CRUTCH_RESOLVED
# lift over BoW was thin (+0.02-0.03). Two candidate loci: (a) RETRIEVAL -- the gap->CSKG
# query never reaches a fact connected to the GOLD answer at all; (b) USE -- a fact IS
# reachable for gold but the SCORING formula ranks a distractor's fact higher. The legacy
# scoring formula `max(trust) * len(edges)` lets a candidate with several TRUST_MID (0.6)
# edges (e.g. 3 edges = 1.8) outrank a candidate with a single TRUST_HIGH (1.0) edge -- an
# edge-COUNT artifact, not evidence strength; this is a USE-quality bug by construction,
# independent of whether retrieval reached gold. score_mode="max_trust" removes the count
# multiplier (rank by strongest single piece of evidence only, secondary count tie-break via
# a small epsilon so ties still resolve deterministically toward more corroborated pairs
# without letting count DOMINATE trust). MEASURED@diagnostic run (see report) decides which
# mode ships.
def _edge_weight(edges: List[Tuple[str, float]], score_mode: str) -> float:
    max_t = max(t for _, t in edges)
    if score_mode in ("max_trust", "hub_penalized"):  # hub_penalized uses max_trust as its base
        return max_t + 0.001 * min(len(edges), 20)  # count only breaks ties, never dominates trust
    if score_mode == "count_weighted":
        return max_t * len(edges)  # legacy (pre-2026-08-10 fix) formula
    raise ValueError(f"unknown score_mode {score_mode!r}")


# ---- FAULT-2 diagnosis round 2 (2026-08-10): the max_trust fix (edge-COUNT-inflation hypothesis)
# MEASURED zero delta on real SIQa+CSKG data (97% of CSKG pairs have exactly 1 edge; the crafted
# multi-edge-inflation scenario barely occurs). Sampling actual retrieval_hit-but-wrong-argmax
# items found the REAL cause instead: a small set of high-DEGREE, SIQa-template-generic concepts
# ('person', 'mouth', 'want', 'next', 'need', 'baby'...) recur across unrelated items (SIQa's
# question templates: "How would X feel/be described?", "What will X want to do next?") and connect
# to almost anything in a 1.15M-edge KB, producing spurious or wrong-candidate-favoring crutch
# scores that carry no real item-specific signal -- a classic high-document-frequency/low-
# informativeness hub-node problem (same intuition as IDF down-weighting in IR). hub_penalized
# divides the max_trust base score by (1 + log1p(degree)) of the MORE-CONNECTED of the two concepts
# in the driving pair, so a hub-mediated edge is discounted relative to a specific, low-degree,
# genuinely-informative connection.
def _hub_penalty(a: str, b: str, node_degree: Optional[Dict[str, int]]) -> float:
    if not node_degree:
        return 1.0
    deg = max(node_degree.get(a, 0), node_degree.get(b, 0))
    return 1.0 / (1.0 + math.log1p(deg))


# =====================================================================================
# start-marker / crash diagnostics / atomic metrics (per exp_dev canonical checklist)
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _hb(output_dir, stage, t0, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - t0, 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} t={row['elapsed_s']}s {extra or ''}", flush=True)


# =====================================================================================
# CSKG symbolic concept-pair index loader (real edges_shard_*.jsonl format)
def load_cskg_index(cskg_dir: str = CSKG_DIR, max_shards: Optional[int] = None,
                    max_edges: Optional[int] = None) -> Dict[str, List[Tuple[str, float]]]:
    """pair_key -> list[(relation, trust_weight)]. MEASURED@data/exp_cskg_foundation_v1/metrics.json:
    482,588 spine nodes / 1,238,686 typed edges (16 shards)."""
    idx: Dict[str, List[Tuple[str, float]]] = {}
    shard_names = sorted(f for f in os.listdir(cskg_dir) if f.startswith("edges_shard_"))
    if max_shards is not None:
        shard_names = shard_names[:max_shards]
    n_edges = 0
    for shard in shard_names:
        with open(os.path.join(cskg_dir, shard), encoding="utf-8") as f:
            for line in f:
                if max_edges is not None and n_edges >= max_edges:
                    return idx
                row = json.loads(line)
                subj, obj = row["subject"], row["obj"]
                if subj == obj:
                    continue
                trust_w = TRUST_WEIGHT.get(row.get("trust", "TRUST_MID"), 0.6)
                idx.setdefault(pair_key(subj, obj), []).append((row["relation"], trust_w))
                n_edges += 1
    return idx


def cskg_node_set_from_index(idx: Dict[str, List]) -> frozenset:
    nodes = set()
    for k in idx:
        a, b = k.split("::", 1)
        nodes.add(a)
        nodes.add(b)
    return frozenset(nodes)


def compute_node_degree(idx: Dict[str, List]) -> Dict[str, int]:
    """pair-count per concept (a proxy for CSKG node degree -- how many DISTINCT other concepts
    this concept connects to). MEASURED@diag 2026-08-10 root-cause for the retrieval-vs-use split's
    USE shortfall (see _edge_weight docstring 'hub_penalized'): a handful of SIQa-template-generic
    concepts (e.g. 'person', 'mouth', 'want', 'next', 'need') recur across MANY unrelated items and
    connect to almost anything in a 1.15M-edge KB, producing a spuriously-tied or wrong-candidate-
    favoring crutch score that has nothing to do with the item's actual content."""
    deg: Dict[str, int] = {}
    for k in idx:
        a, b = k.split("::", 1)
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    return deg


# =====================================================================================
# 3-tier PRELIM: relation-family bucketing (the CA3/DG cluster's TRIGGER_ROLE category tag).
# MEASURED@shard sample (2026-08-10, edges_shard_00.jsonl, 300k-edge sample): 33 distinct relation
# types (/r/LocatedNear, at:xAttr, at:xWant, at:xEffect, at:xNeed, mw:MayHaveProperty, at:xReact,
# at:xIntent, /r/CapableOf, at:oWant, /r/UsedFor, at:oEffect, /r/AtLocation, at:oReact, /r/PartOf,
# /r/HasSubevent, /r/HasPrerequisite, /r/HasA, /r/Causes, /r/MannerOf, /r/HasProperty,
# /r/MotivatedByGoal, ... ) -- a well-bounded, semantically-meaningful clustering key already
# present in the loaded CSKG index (no invented taxonomy).
# v2 STATUS (2026-08-11): RETAINED VERBATIM, UNMODIFIED, for reference/diagnostic-comparison only.
# It is NO LONGER the live clustering key -- see semantic_relation_key() immediately below, which
# REPLACES this function at the ONE call site inside update_prelim_and_generalize() and in the
# novelty-threshold calibration vocabulary sample in run(). Kept defined (not deleted) so a future
# audit can re-derive v1's exact behavior byte-for-byte from this same file if needed.
def relation_family(idx: Dict[str, List[Tuple[str, float]]], pk: str) -> str:
    edges = idx.get(pk)
    if not edges:
        return "UNKNOWN"
    r0 = sorted(set(r for r, _ in edges))[0]  # deterministic pick (sorted, not list(set()))
    for pre in RELATION_PREFIXES:
        if r0.startswith(pre):
            return canon(r0[len(pre):])
    return canon(r0)


# =====================================================================================
# v2 ONE-VARIABLE CHANGE (2026-08-11): semantic-embedding clustering key, REPLACING relation_family
# as the string fed into build_instance_register's trigger_cat / ScriptLibrary.match_or_spawn.
#
# WHY A STRING, NOT A RAW EMBEDDING: build_instance_register(agent, patient, trigger_cat,
# consequent_cat) (hdlab/script_grain_acquisition_loop.py, REUSED VERBATIM, unmodified) binds
# TRIGGER_ROLE to content_phase_vec(trigger_cat) -- a DETERMINISTIC but hashlib-RANDOM unit-phase
# FHRR vector per distinct STRING (any two different strings are ~orthogonal, by construction; see
# that module's own docstring section CORRECTION #4). That means the only way for two DIFFERENT
# category tags to contribute a nonzero-similarity signal to match_or_spawn's cosine-based CA3/DG
# attractor is for them to be the IDENTICAL string. So a "semantic-embedding cosine key" must take
# the form of a DISCRETIZATION that maps semantically-CLOSE concept pairs onto the SAME (or a
# neighboring) string far more often than semantically-DISTANT pairs -- i.e. locality-sensitive
# hashing (LSH; Charikar 2002 SimHash; T3/locality_sensitive_hashing per substrate-KB math atoms,
# prior-work-checked below) of a real embedding. This is the standard, principled way to turn a
# continuous cosine-similarity space into discrete "same schema" bucket labels while preserving
# locality, and it lets EVERY downstream organ (build_instance_register, match_or_spawn,
# iterative_attractor, calibrate_novelty_threshold, script_consolidation_pass) be reused 100%
# UNCHANGED -- only the STRING VALUE fed in at one call site changes. This satisfies "no new gate
# math, only new WIRING between owned organs" (the same discipline v1's own PRELIM/generalization
# build followed for its OWN new wiring).
#
# ENCODER: hdlab.char_trigram_encoder.CharTrigramEncoder (registry row 12, WIRED, OWNED, zero
# external model / zero borrowed vectors -- pure substrate bag-of-char-trigram bipolar HD encoding).
# NOT scale_win_tinytransformer_encoder (registry row 3): see the import-site comment above for why
# that encoder is not readily composable into a light CPU-only symbolic cell.
#
# WHAT GOES IN: the pair's OWN two concept strings (a, b from pk.split("::")) -- NOT the CSKG
# relation type, matching the design audit's literal framing ("a semantic-embedding cosine key
# built from the pair's own two concept strings"). encode(a) + encode(b) (bundle/sum) is symmetric
# in (a, b) by construction (sum commutes), matching pair_key's own canonical (lo, hi) ordering.
SEM_KEY_ENCODER_DIM = 256           # matches D_CTX (script_grain_acquisition_loop's own bipolar
                                     # context-vector dim) -- a reused, not invented, project scale.
SEM_KEY_N_BITS = 6                  # HYPOTHESIZED@this file (2026-08-11): 2**6=64 possible buckets,
                                     # same ORDER OF MAGNITUDE as relation_family's MEASURED ~33-40
                                     # distinct labels (shard sample comment above) -- a comparable
                                     # granularity budget, driven by CONCEPT-EMBEDDING content
                                     # instead of CSKG relation-TYPE label. Re-measured at smoke
                                     # (n_clusters vs n_distinct_semantic_buckets_seen) before FULL
                                     # dispatch; per the design audit's own contingency, if smoke
                                     # shows collapse toward the v1 degenerate 2-cluster case this
                                     # bit-width is the first thing to widen before concluding the
                                     # key needs a different design entirely.
_SEM_KEY_PROJ_SEED_TAG = "crutch_fade_v2_semantic_cluster_key_projection_2026-08-11"

_sem_key_encoder = CharTrigramEncoder(n_dim=SEM_KEY_ENCODER_DIM)


def _semantic_projection_matrix(n_dim: int, n_bits: int, seed_tag: str) -> np.ndarray:
    """Deterministic (hashlib-seeded, PROT-023/F.5 compliant -- never Python's built-in salted
    hash()) random-hyperplane matrix for locality-sensitive hashing. For two vectors at true cosine
    similarity rho, the probability their sign-projection agrees on one hyperplane is
    1 - arccos(rho)/pi (THEORETICAL@Charikar 2002 SimHash); agreement across all n_bits hyperplanes
    is (that probability)**n_bits, so semantically-CLOSE concept-pair embeddings collide into the
    SAME bucket string far more often than unrelated pairs, without ever comparing every pair to
    every other pair (O(n_bits) per pair, not O(n^2))."""
    seed = int.from_bytes(hashlib.sha256(seed_tag.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_bits, n_dim)).astype(np.float32)


_sem_key_proj = _semantic_projection_matrix(SEM_KEY_ENCODER_DIM, SEM_KEY_N_BITS, _SEM_KEY_PROJ_SEED_TAG)


def semantic_relation_key(idx: Dict[str, List[Tuple[str, float]]], pk: str) -> str:
    """v2 REPLACEMENT for relation_family(idx, pk) as the CA3/DG clustering key. Same call signature
    (idx accepted but UNUSED -- kept for call-site parity; the key is now a property of the CONCEPT
    PAIR itself, not of which CSKG edge/relation happens to connect them, so no index lookup is
    needed and there is no 'UNKNOWN' fallback class). Encodes both concept strings with the OWNED
    CharTrigramEncoder, bundles (sums) them into one pair embedding, projects onto SEM_KEY_N_BITS
    deterministic random hyperplanes, and returns the resulting sign-bit-pattern as a 'sem_<bits>'
    bucket label string."""
    a, b = pk.split("::", 1)
    va = _sem_key_encoder.encode(a)
    vb = _sem_key_encoder.encode(b)
    pair_vec = va + vb
    bits = (_sem_key_proj @ pair_vec) >= 0
    bucket = "".join("1" if x else "0" for x in bits)
    return f"sem_{bucket}"


def _stem_variants(c: str) -> List[str]:
    """Cheap suffix-strip fallback (no external NLP dep) for surface-form mismatch between SIQa's
    inflected text (plurals/verb endings) and CSKG's lemma-like canon ids (mostly ConceptNet-
    convention singular/base forms). Tried IN ORDER only when the raw canon'd token itself is not
    a CSKG node; disclosed limitation (prereg "Deviation"): this is not a real lemmatizer, so some
    irregular forms (e.g. 'went'->'go') will still miss."""
    out = []
    if c.endswith("ies") and len(c) > 4:
        out.append(c[:-3] + "y")
    if c.endswith("es") and len(c) > 3:
        out.append(c[:-2])
    if c.endswith("s") and len(c) > 3:
        out.append(c[:-1])
    if c.endswith("ing") and len(c) > 5:
        out.append(c[:-3])
        out.append(c[:-3] + "e")
    if c.endswith("ed") and len(c) > 4:
        out.append(c[:-2])
        out.append(c[:-1])
    return out


def extract_concepts(text: str, node_set: frozenset) -> List[str]:
    seen = []
    seen_set = set()
    for w in content_words(text):
        c = canon(w)
        if not c:
            continue
        if c not in node_set:
            for variant in _stem_variants(c):
                if variant in node_set:
                    c = variant
                    break
        if c in node_set and c not in seen_set:
            seen_set.add(c)
            seen.append(c)
    return seen


# =====================================================================================
# SIQA loading (cached local JSONL; no network at run time)
def load_siqa() -> Tuple[List[dict], List[dict]]:
    def _load(fname):
        rows = []
        with open(os.path.join(SIQA_DIR, fname), encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
        return rows
    return _load("train.jsonl"), _load("validation.jsonl")


# =====================================================================================
# scoring primitives
def bow_scores(item: dict) -> List[float]:
    ctx_q = content_words(item["context"] + " " + item["question"])
    ctx_set = set(ctx_q)
    scores = []
    for key in ("answerA", "answerB", "answerC"):
        ans_words = content_words(item[key])
        if not ans_words:
            scores.append(0.0)
            continue
        overlap = sum(1 for w in ans_words if w in ctx_set)
        scores.append(overlap / (len(ans_words) + 1))
    return scores


def bow_margin(scores: List[float]) -> float:
    s = sorted(scores, reverse=True)
    top1, top2 = s[0], s[1]
    return (top1 - top2) / (top1 + top2 + 1e-9)


def argmax_tiebreak(scores: List[float]) -> int:
    best = 0
    for i in range(1, len(scores)):
        if scores[i] > scores[best]:
            best = i
    return best


def crutch_candidate_scores(ctx_concepts: List[str], ans_concepts_list: List[List[str]],
                            idx: Dict[str, List[Tuple[str, float]]],
                            score_mode: str = "count_weighted",
                            node_degree: Optional[Dict[str, int]] = None
                            ) -> Tuple[List[float], List[Optional[str]]]:
    """Returns (per-candidate crutch score, per-candidate best driving pair_key or None).
    score_mode: "count_weighted" (legacy) | "max_trust" (edge-count-inflation fix, MEASURED zero
    delta on real data) | "hub_penalized" (max_trust base / hub-degree penalty, see _hub_penalty
    docstring -- requires node_degree, the shipped 2026-08-10 fix)."""
    scores = []
    driving = []
    for ans_concepts in ans_concepts_list:
        best_score = 0.0
        best_pair = None
        for cc in ctx_concepts:
            for ac in ans_concepts:
                if cc == ac:
                    continue
                pk = pair_key(cc, ac)
                edges = idx.get(pk)
                if not edges:
                    continue
                w = _edge_weight(edges, score_mode)
                if score_mode == "hub_penalized":
                    w *= _hub_penalty(cc, ac, node_degree)
                if w > best_score:
                    best_score = w
                    best_pair = pk
        scores.append(best_score)
        driving.append(best_pair)
    return scores, driving


def _scramble_partner(seed_key: str, node_list: List[str], exclude: str) -> str:
    """Deterministic (hashlib-seeded, PROT-023/F.5 compliant) 'wrong' concept draw."""
    h = int.from_bytes(hashlib.sha256(seed_key.encode("utf-8")).digest()[:8], "big")
    n = len(node_list)
    for attempt in range(8):
        j = (h + attempt * 2654435761) % n
        cand = node_list[j]
        if cand != exclude:
            return cand
    return node_list[h % n]


def scramble_crutch_candidate_scores(item_id: str, ctx_concepts: List[str],
                                     ans_concepts_list: List[List[str]],
                                     idx: Dict[str, List[Tuple[str, float]]],
                                     node_list: List[str],
                                     score_mode: str = "count_weighted",
                                     node_degree: Optional[Dict[str, int]] = None
                                     ) -> Tuple[List[float], List[Optional[str]]]:
    """Same firing structure as crutch_candidate_scores but looks up a deterministically-WRONG
    concept in place of each true context concept -- 'a random OTHER CSKG neighbor unrelated to
    the actual cue' (drill 4 Section 2c, arm 5)."""
    scores = []
    driving = []
    for ci, ans_concepts in enumerate(ans_concepts_list):
        best_score = 0.0
        best_pair = None
        for cc in ctx_concepts:
            wrong_cc = _scramble_partner(f"{item_id}|{cc}|{ci}", node_list, cc)
            for ac in ans_concepts:
                if wrong_cc == ac:
                    continue
                pk = pair_key(wrong_cc, ac)
                edges = idx.get(pk)
                if not edges:
                    continue
                w = _edge_weight(edges, score_mode)
                if score_mode == "hub_penalized":
                    w *= _hub_penalty(wrong_cc, ac, node_degree)
                if w > best_score:
                    best_score = w
                    best_pair = pk
        scores.append(best_score)
        driving.append(best_pair)
    return scores, driving


def library_candidate_scores(ctx_concepts: List[str], ans_concepts_list: List[List[str]],
                             store: HDFactStore) -> Tuple[List[float], List[Optional[str]]]:
    scores = []
    driving = []
    for ans_concepts in ans_concepts_list:
        best_score = 0.0
        best_pair = None
        for cc in ctx_concepts:
            for ac in ans_concepts:
                if cc == ac:
                    continue
                pk = pair_key(cc, ac)
                hits = store.query(pk, "OUTCOME_POLARITY")
                if hits and hits[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"):
                    if 1.0 > best_score:
                        best_score = 1.0
                        best_pair = pk
        scores.append(best_score)
        driving.append(best_pair)
    return scores, driving


def tier_candidate_scores(ctx_concepts: List[str], ans_concepts_list: List[List[str]],
                          store: HDFactStore) -> Tuple[List[float], List[Optional[str]], List[Optional[str]]]:
    """Like library_candidate_scores but ALSO returns the winning hit's glass-box-recovered SOURCE
    (e.g. 'cskg_crutch_real_single' vs 'combined_evidence_cluster' vs 'prelim_retain') -- lets a
    caller split fidelity BY PROMOTION PATH, not just by tier. Used by every 3-tier arm for both its
    LIBRARY (native) and PRELIM lookups (same store interface, different store instance)."""
    scores, driving, sources = [], [], []
    for ans_concepts in ans_concepts_list:
        best_score = 0.0
        best_pair = None
        best_source = None
        for cc in ctx_concepts:
            for ac in ans_concepts:
                if cc == ac:
                    continue
                pk = pair_key(cc, ac)
                hits = store.query(pk, "OUTCOME_POLARITY")
                if hits and hits[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"):
                    if 1.0 > best_score:
                        best_score = 1.0
                        best_pair = pk
                        best_source = hits[0]["source"]
        scores.append(best_score)
        driving.append(best_pair)
        sources.append(best_source)
    return scores, driving, sources


class TierState:
    """Bundles the 3-tier PRELIM/generalization state for ONE side (real or scramble) of the run.
    `prelim_lib` is a Library() instance that is NEVER passed through consolidation_pass -- its
    items' .status is never mutated away from PENDING, so Library.flag()'s existing "reject once
    non-PENDING" guard never fires against it (no modification to grounding_acquisition_loop.py);
    this is exactly the "retain forever, never discard" behavior the binary cliff lacked.
    `native_store_gen` receives BOTH single-item promotions (mirrored from the real/scramble Library
    + HDFactStore's OWN consolidation_pass, unchanged) AND combined-evidence cluster promotions --
    the "no_generalization" ablation arm instead reads the UNMIRRORED single-item store directly, so
    it structurally never sees a cluster promotion (see run())."""

    def __init__(self, seed_base: int) -> None:
        self.prelim_lib = Library()
        self.prelim_store = HDFactStore(n_dim=2048, seed=seed_base + 100, use_index=True)
        self.script_lib = ScriptLibrary()
        self.native_store_gen = HDFactStore(n_dim=2048, seed=seed_base + 200, use_index=True)
        self.pk_cluster: Dict[str, str] = {}          # pair_key -> ScriptLibraryItem.item_id (sticky)
        self.cluster_members: Dict[str, set] = {}      # item_id -> set(pair_key)
        self.promoted_single: set = set()               # pair_keys mirrored into native_store_gen
        self.promoted_cluster: set = set()               # pair_keys promoted via combined evidence


def update_prelim_and_generalize(state: TierState, idx: Dict[str, List[Tuple[str, float]]],
                                 novelty_thresh: float, min_confirm: int = MIN_CONFIRM,
                                 schema_thresh: float = PRELIM_SCHEMA_THRESH,
                                 promote_min_exposure: int = PROMOTE_MIN_EXPOSURE,
                                 promote_min_consistency: float = PROMOTE_MIN_CONSISTENCY,
                                 cluster_min_members: int = CLUSTER_MIN_MEMBERS,
                                 node_degree: Optional[Dict[str, int]] = None,
                                 hub_degree_thresh: int = HUB_DEGREE_THRESH) -> dict:
    """One checkpoint's PRELIM-retain + CA3/DG cluster-registration + combined-evidence-promotion
    pass. Reuses schema_consistency_split_half / _vote_margin (grounding_acquisition_loop, byte-
    identical to the single-item BANK gate) and ScriptLibrary.match_or_spawn / build_instance_register
    (script_grain_acquisition_loop, byte-identical to that module's own CA3/DG keying) -- no new
    gate math, only new WIRING between owned organs (design note's "the crux"). node_degree
    (optional; see HUB_DEGREE_THRESH comment) EXCLUDES a hub-template-word-driven pair from RETAIN +
    cluster registration entirely -- smoke-diagnosed fidelity fix, 2026-08-10."""
    newly_retained = 0
    n_hub_excluded = 0
    for pk in sorted(state.prelim_lib.items):
        it = state.prelim_lib.items[pk]
        n = len(it.traces)
        if n < min_confirm:
            continue
        if node_degree is not None:
            a_deg, b_deg = pk.split("::", 1)
            if max(node_degree.get(a_deg, 0), node_degree.get(b_deg, 0)) > hub_degree_thresh:
                n_hub_excluded += 1
                continue
        score = schema_consistency_split_half(it.traces)
        if score is None or score < schema_thresh:
            continue
        margin, pos, neg = _vote_margin(it.traces)
        if margin == 0.0:
            continue
        label = "POS" if margin > 0 else "NEG"
        # RETAIN (idempotent -- CONSISTENT_DUP if already live with the same object)
        existing = state.prelim_store.query(pk, "OUTCOME_POLARITY")
        if not existing:
            state.prelim_store.store(pk, "OUTCOME_POLARITY", label, "prelim_retain", PRELIM_TRUST)
            newly_retained += 1
        # register into the CA3/DG cluster ONCE (sticky membership; avoid churn on re-evaluation)
        # v2 ONE-VARIABLE CHANGE: semantic_relation_key(idx, pk) replaces relation_family(idx, pk)
        # as the clustering key -- THE ONLY LINE THIS CELL CHANGES relative to v1's mechanism.
        if pk not in state.pk_cluster:
            fam = semantic_relation_key(idx, pk)
            a, b = pk.split("::", 1)
            reg = build_instance_register(a, b, fam, f"OUTCOME_{label}")
            item_id, spawned, m_score = state.script_lib.match_or_spawn(
                reg, pk, label, it.traces[0].context_vec, 0, true_type=fam,
                novelty_thresh=novelty_thresh)
            state.pk_cluster[pk] = item_id
            state.cluster_members.setdefault(item_id, set()).add(pk)

    # combined-evidence promotion: pull each member's OWN current traces fresh (no separate
    # bookkeeping to go stale) and evaluate the IDENTICAL single-item gate at cluster grain, over
    # the AGREEING subset of members only (fidelity guard, HARD-PASS 5) -- a member whose OWN vote
    # opposes the cluster's provisional majority is EXCLUDED from the evidence pool (so one
    # dissenter cannot block the whole cluster's genuinely-agreeing majority from promoting) AND
    # never force-promoted under the majority's label (bounded leakage, not just an aggregate
    # dilution that happens to fail the gate).
    n_combined_promoted_this_pass = 0
    for item_id, members in state.cluster_members.items():
        if len(members) < cluster_min_members:
            continue
        provisional_traces = []
        for pk in members:
            provisional_traces.extend(state.prelim_lib.items[pk].traces)
        if not provisional_traces:
            continue
        prov_margin, _, _ = _vote_margin(provisional_traces)
        if prov_margin == 0.0:
            continue
        majority_positive = prov_margin > 0
        agreeing_members, agreeing_traces = [], []
        for pk in members:
            own_margin, _, _ = _vote_margin(state.prelim_lib.items[pk].traces)
            if own_margin != 0.0 and (own_margin > 0) != majority_positive:
                continue  # dissenter: excluded from the evidence pool AND never promoted
            agreeing_members.append(pk)
            agreeing_traces.extend(state.prelim_lib.items[pk].traces)
        margin, pos, neg = _vote_margin(agreeing_traces)
        exposure = len(agreeing_traces)
        consistency = abs(margin)
        # cluster-grain gate is STRICTER than the single-item gate (never weaker) -- see
        # CLUSTER_EXPOSURE_MULTIPLIER comment (coarser relation-family evidence needs a bigger,
        # more convincing sample before its majority is trustworthy).
        cluster_exposure_floor = promote_min_exposure * CLUSTER_EXPOSURE_MULTIPLIER
        if exposure < cluster_exposure_floor or consistency < promote_min_consistency or margin == 0.0:
            continue
        cluster_label = "POS" if margin > 0 else "NEG"
        trust_sym = "TRUST_HIGH" if consistency >= 0.9 else "TRUST_MID"
        for pk in agreeing_members:
            if pk in state.promoted_cluster:
                continue
            state.native_store_gen.store(pk, "OUTCOME_POLARITY", cluster_label,
                                         "combined_evidence_cluster", trust_sym)
            state.promoted_cluster.add(pk)
            n_combined_promoted_this_pass += 1
    return {
        "newly_retained": newly_retained,
        "n_hub_excluded": n_hub_excluded,
        "n_prelim_pending_items": len(state.prelim_lib.items),
        "n_clusters": len(state.cluster_members),
        "n_clusters_eligible_size": sum(1 for m in state.cluster_members.values()
                                        if len(m) >= cluster_min_members),
        "n_combined_promoted_total": len(state.promoted_cluster),
        "n_combined_promoted_this_pass": n_combined_promoted_this_pass,
    }


# =====================================================================================
# FAULT-2 diagnosis: RETRIEVAL-vs-USE decomposition for gap_driven's CRUTCH_RESOLVED items.
# RETRIEVAL quality = did the gap->CSKG query reach ANY edge connecting a context concept to the
# GOLD answer's concepts (score[gold] > 0), regardless of whether it won the argmax? USE quality =
# GIVEN a gold-connected edge exists (retrieval succeeded), did the scoring/argmax correctly rank
# gold on top? A low retrieval_hit_rate means the query/coverage is the bottleneck (need a broader
# gap->fact query); a high retrieval_hit_rate but low use_quality_given_hit means the SCORING
# formula is mis-ranking a reachable correct fact behind a distractor's fact (need a better
# fact->answer scoring rule). Recomputes crutch_candidate_scores for CRUTCH_RESOLVED items only
# (cheap: bounded per-item dict lookups, same cost class as the resolution call itself).
def retrieval_use_diagnostic(dev: List[dict], node_set: frozenset,
                             idx: Dict[str, List[Tuple[str, float]]],
                             gap_rows: List[dict], score_mode: str,
                             node_degree: Optional[Dict[str, int]] = None) -> dict:
    n_hit = n_use_ok = n_miss = n_correct_despite_miss = n_total = 0
    for r in gap_rows:
        if r["tag"] != "CRUTCH_RESOLVED":
            continue
        it = dev[r["item_idx"]]
        gold_idx = label_idx(it)
        ctx_concepts = extract_concepts(it["context"] + " " + it["question"], node_set)
        ans_concepts_list = [extract_concepts(it[k], node_set) for k in ("answerA", "answerB", "answerC")]
        c_scores, _ = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx, score_mode, node_degree)
        n_total += 1
        if c_scores[gold_idx] > 0:
            n_hit += 1
            if r["pred_idx"] == gold_idx:
                n_use_ok += 1
        else:
            n_miss += 1
            if r["pred_idx"] == gold_idx:
                n_correct_despite_miss += 1  # structurally near-impossible (argmax=0 can't beat
                                              # a rival >0 candidate) but tallied for audit honesty
    return {
        "n_crutch_resolved": n_total,
        "retrieval_hit_rate": (n_hit / n_total) if n_total else None,
        "use_quality_given_hit": (n_use_ok / n_hit) if n_hit else None,
        "retrieval_miss_rate": (n_miss / n_total) if n_total else None,
        "correct_despite_retrieval_miss": (n_correct_despite_miss / n_miss) if n_miss else None,
    }


# =====================================================================================
# per-item resolution (one arm, one item, given current library state)
def resolve_item(item: dict, node_set: frozenset, idx: Dict[str, List[Tuple[str, float]]],
                 gate_thresh: float, arm: str, item_id: str,
                 store: Optional[HDFactStore] = None,
                 node_list: Optional[List[str]] = None,
                 score_mode: str = "count_weighted",
                 node_degree: Optional[Dict[str, int]] = None,
                 tier_state: Optional[TierState] = None) -> dict:
    b_scores = bow_scores(item)
    ctx_concepts = extract_concepts(item["context"] + " " + item["question"], node_set)
    ans_concepts_list = [extract_concepts(item[k], node_set) for k in ("answerA", "answerB", "answerC")]

    if arm == "bow" or arm == "never_crutch":
        pred = argmax_tiebreak(b_scores)
        return {"tag": "BOW_RESOLVED", "pred_idx": pred, "driving_pair": None}

    if arm == "always_crutch":
        c_scores, c_driving = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx, score_mode,
                                                       node_degree)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "BOW_RESOLVED", "pred_idx": pred, "driving_pair": None}

    margin = bow_margin(b_scores)
    gap = (margin == 0.0) or (margin < gate_thresh)  # a TIE (incl. all-zero) always flags
    if not gap:
        pred = argmax_tiebreak(b_scores)
        return {"tag": "BOW_RESOLVED", "pred_idx": pred, "driving_pair": None}

    if arm == "gap_driven":
        l_scores, l_driving = library_candidate_scores(ctx_concepts, ans_concepts_list, store)
        if max(l_scores) > 0:
            pred = argmax_tiebreak(l_scores)
            return {"tag": "LIBRARY_RESOLVED", "pred_idx": pred, "driving_pair": l_driving[pred]}
        c_scores, c_driving = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx, score_mode,
                                                       node_degree)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "ABSTAINED", "pred_idx": pred, "driving_pair": None}

    if arm == "scramble_crutch":
        l_scores, l_driving = library_candidate_scores(ctx_concepts, ans_concepts_list, store)
        if max(l_scores) > 0:
            pred = argmax_tiebreak(l_scores)
            return {"tag": "LIBRARY_RESOLVED", "pred_idx": pred, "driving_pair": l_driving[pred]}
        c_scores, c_driving = scramble_crutch_candidate_scores(item_id, ctx_concepts,
                                                                ans_concepts_list, idx, node_list,
                                                                score_mode, node_degree)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "ABSTAINED", "pred_idx": pred, "driving_pair": None}

    # ---- 3-tier PRELIM arms (2026-08-10). LIBRARY tier store varies per arm:
    #   gap_driven_3tier / gap_driven_3tier_no_pull   -> tier_state.native_store_gen (single+cluster)
    #   gap_driven_3tier_no_generalization             -> `store` (real_store, single-item ONLY --
    #                                                      literally the SAME store gap_driven uses)
    #   scramble_crutch_3tier                          -> tier_state.native_store_gen (scramble side)
    # PRELIM tier is always tier_state.prelim_store, consulted UNLESS arm == ..._no_pull.
    if arm in ("gap_driven_3tier", "gap_driven_3tier_no_generalization",
              "gap_driven_3tier_no_pull", "scramble_crutch_3tier"):
        lib_store = store if arm == "gap_driven_3tier_no_generalization" else tier_state.native_store_gen
        l_scores, l_driving, l_sources = tier_candidate_scores(ctx_concepts, ans_concepts_list, lib_store)
        if max(l_scores) > 0:
            pred = argmax_tiebreak(l_scores)
            return {"tag": "LIBRARY_RESOLVED", "pred_idx": pred, "driving_pair": l_driving[pred],
                   "promo_source": l_sources[pred]}

        if arm != "gap_driven_3tier_no_pull":
            p_scores, p_driving, p_sources = tier_candidate_scores(ctx_concepts, ans_concepts_list,
                                                                    tier_state.prelim_store)
            if max(p_scores) > 0:
                pred = argmax_tiebreak(p_scores)
                return {"tag": "PRELIM_RESOLVED", "pred_idx": pred, "driving_pair": p_driving[pred],
                       "promo_source": p_sources[pred]}

        if arm == "scramble_crutch_3tier":
            c_scores, c_driving = scramble_crutch_candidate_scores(item_id, ctx_concepts,
                                                                    ans_concepts_list, idx, node_list,
                                                                    score_mode, node_degree)
        else:
            c_scores, c_driving = crutch_candidate_scores(ctx_concepts, ans_concepts_list, idx,
                                                           score_mode, node_degree)
        if max(c_scores) > 0:
            pred = argmax_tiebreak(c_scores)
            return {"tag": "CRUTCH_RESOLVED", "pred_idx": pred, "driving_pair": c_driving[pred]}
        pred = argmax_tiebreak(b_scores)
        return {"tag": "ABSTAINED", "pred_idx": pred, "driving_pair": None}

    raise ValueError(f"unknown arm {arm!r}")


def label_idx(item: dict) -> int:
    return int(item["label"]) - 1


# =====================================================================================
# exposure processing (gap_driven + scramble_crutch arms only)
def process_exposure_slice(train_slice: List[dict], node_set: frozenset,
                           idx: Dict[str, List[Tuple[str, float]]], node_list: List[str],
                           real_lib: Library, scr_lib: Library,
                           pair_example_context: Dict[str, str],
                           real_prelim_lib: Optional[Library] = None,
                           scr_prelim_lib: Optional[Library] = None) -> None:
    """real_prelim_lib / scr_prelim_lib (2026-08-10, optional -- default None preserves prior
    behavior byte-for-byte): fed the IDENTICAL (pair_key, episode_id, pole, context_vec) calls as
    real_lib/scr_lib, into a SEPARATE, permanently-PENDING Library so exposure keeps accumulating
    past the point real_lib/scr_lib's own item would terminalize (see TierState docstring)."""
    for i, ex in enumerate(train_slice):
        ctx_text = ex["context"]
        concepts = extract_concepts(ctx_text, node_set)
        cvec = context_vector(ctx_text)
        n = len(concepts)
        for a_i in range(n):
            for b_i in range(a_i + 1, n):
                a, b = concepts[a_i], concepts[b_i]
                pk = pair_key(a, b)
                if pk in idx:
                    real_lib.flag(pk, f"exp{i}_{pk}", "POS", cvec, 0)
                    if real_prelim_lib is not None:
                        real_prelim_lib.flag(pk, f"pexp{i}_{pk}", "POS", cvec, 0)
                    if pk not in pair_example_context:
                        pair_example_context[pk] = ctx_text
                    wrong_b = _scramble_partner(f"scr|{a}|{b}", node_list, b)
                    scr_pk = pair_key(a, wrong_b)
                    scr_lib.flag(scr_pk, f"exps{i}_{scr_pk}", "POS", cvec, 0)
                    if scr_prelim_lib is not None:
                        scr_prelim_lib.flag(scr_pk, f"pexps{i}_{scr_pk}", "POS", cvec, 0)


# =====================================================================================
# main run
def run(output_dir: str, run_mode: str, train_cap: Optional[int], dev_cap: Optional[int],
       seed: int = 7, promote_min_exposure: int = PROMOTE_MIN_EXPOSURE,
       score_mode: str = "count_weighted") -> dict:
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode, expected_n_units=len(CHECKPOINTS))

    print("[load] CSKG index...", flush=True)
    idx = load_cskg_index()
    node_set = cskg_node_set_from_index(idx)
    node_list = sorted(node_set)  # deterministic order (sorted, not list(set()))
    node_degree = compute_node_degree(idx) if score_mode == "hub_penalized" else None
    _hb(output_dir, "cskg_loaded", t0, {"n_pairs": len(idx), "n_nodes": len(node_list),
        "node_degree_computed": node_degree is not None})

    print("[load] Social IQa...", flush=True)
    train_all, dev_all = load_siqa()
    train = train_all[:train_cap] if train_cap else train_all
    dev = dev_all[:dev_cap] if dev_cap else dev_all
    _hb(output_dir, "siqa_loaded", t0, {"n_train": len(train), "n_dev": len(dev)})

    # ---- Stage-0: BoW baseline measured fresh + adaptive GATE_THRESH ----
    # MEASURED@smoke (2026-08-10, SMOKE_TRAIN_CAP=3000/SMOKE_DEV_CAP=250 run): >=50% of dev items
    # have a TIED top-2 BoW score (median margin over ALL items = 0.0 exactly) -- SIQa's answers are
    # short, non-extractive phrases, so raw lexical overlap frequently ties (often at zero for all
    # 3 candidates). A plain median-of-all-margins threshold degenerates to 0.0 in that regime,
    # which silently disables margin-based gap-flagging (only the explicit all-zero special case
    # still fires) -- a harness bug caught by smoke, not a mechanism reading (constant 0.1640
    # crutch-fire-rate across every checkpoint was this bug, not a real flat result). Fix: (a) a
    # TIE (margin==0, including the all-zero case) always flags -- a tie is uninformative
    # regardless of magnitude; (b) the threshold itself is calibrated from the STRICTLY-POSITIVE
    # (non-tied) margins only, so the tie-mass no longer swamps the percentile.
    dev_bow_scores = [bow_scores(it) for it in dev]
    dev_margins_all = [bow_margin(s) for s in dev_bow_scores]
    dev_margins_pos = sorted(m for m in dev_margins_all if m > 0.0)
    gate_thresh = dev_margins_pos[len(dev_margins_pos) // 2] if dev_margins_pos else 0.5
    bow_acc = sum(1 for it, s in zip(dev, dev_bow_scores) if argmax_tiebreak(s) == label_idx(it)) / len(dev)
    n_tied = sum(1 for m in dev_margins_all if m == 0.0)
    print(f"[stage0] BoW dev accuracy(fresh)={bow_acc:.4f} GATE_THRESH(median of positive "
          f"margins)={gate_thresh:.4f} n_tied={n_tied}/{len(dev_margins_all)}", flush=True)

    # ---- leakage audit (Stage-0 item c) ----
    leak_sample = dev[:100]
    n_leak = 0
    for it in leak_sample:
        ctx_concepts = extract_concepts(it["context"] + " " + it["question"], node_set)
        gold_key = ("answerA", "answerB", "answerC")[label_idx(it)]
        gold_concepts = extract_concepts(it[gold_key], node_set)
        hit = False
        for cc in ctx_concepts:
            for gc in gold_concepts:
                if cc != gc and pair_key(cc, gc) in idx:
                    hit = True
                    break
            if hit:
                break
        if hit:
            n_leak += 1
    leakage_rate = n_leak / len(leak_sample) if leak_sample else 0.0
    print(f"[leakage] {n_leak}/{len(leak_sample)} = {leakage_rate:.4f}", flush=True)

    # ---- coordinator refinement (mid-build, e9ee736ec sibling diagnosis): crutch RETRIEVAL
    # COVERAGE is a hard ceiling on comprehension independent of consolidation quality (~45-54%
    # MEASURED@e9ee736ec's pme=4 run). dev_crutch_covered = gap-flagged dev items where the crutch
    # has ANY nonzero path to the GOLD answer's concepts -- checkpoint-independent (a property of
    # the static idx + item content, computed once here, same score_mode as the run). Every arm's
    # accuracy is ALSO reported restricted to this subset (accuracy_covered) so consolidation
    # quality can be read apart from the coverage bottleneck (prereg criterion 3).
    dev_crutch_covered: List[bool] = []
    n_gap_flagged = 0
    for it in dev:
        b_scores_i = bow_scores(it)
        margin_i = bow_margin(b_scores_i)
        gap_i = (margin_i == 0.0) or (margin_i < gate_thresh)
        if not gap_i:
            dev_crutch_covered.append(False)
            continue
        n_gap_flagged += 1
        ctx_concepts_i = extract_concepts(it["context"] + " " + it["question"], node_set)
        ans_concepts_list_i = [extract_concepts(it[k], node_set) for k in ("answerA", "answerB", "answerC")]
        c_scores_i, _ = crutch_candidate_scores(ctx_concepts_i, ans_concepts_list_i, idx, score_mode,
                                                node_degree)
        dev_crutch_covered.append(c_scores_i[label_idx(it)] > 0)
    n_covered = sum(dev_crutch_covered)
    coverage_rate = (n_covered / n_gap_flagged) if n_gap_flagged else None
    print(f"[coverage] n_gap_flagged={n_gap_flagged} n_covered={n_covered} "
          f"coverage_rate={coverage_rate}", flush=True)

    # ---- 3-tier PRELIM: calibrate novelty_thresh on THIS run's own SEMANTIC-BUCKET vocabulary
    # (v2: downstream bookkeeping of the SAME clustering-key swap, not a second variable --
    # defensive tripwire per prereg "DG pattern-separation not wired" -- calibrate_novelty_thresh
    # is the OWNED script_grain_acquisition_loop function, called against synthetic same-bucket vs
    # different-bucket register pairs built from real semantic_relation_key buckets seen in idx).
    fam_sample = sorted({semantic_relation_key(idx, k) for k in list(idx)[:20000]})
    if len(fam_sample) >= 2:
        matched_pairs = [(build_instance_register("a1", "b1", fam_sample[0], "OUTCOME_POS"),
                          build_instance_register("a2", "b2", fam_sample[0], "OUTCOME_POS"))]
        wrong_pairs = [(build_instance_register("a1", "b1", fam_sample[0], "OUTCOME_POS"),
                       build_instance_register("a3", "b3", fam_sample[1], "OUTCOME_POS"))]
        calib = calibrate_novelty_threshold(matched_pairs, wrong_pairs)
        novelty_thresh = calib["novelty_thresh"] if calib["discriminates"] else NOVELTY_THRESH_FALLBACK
    else:
        calib = {"discriminates": False, "note": "fewer than 2 semantic buckets in sample"}
        novelty_thresh = NOVELTY_THRESH_FALLBACK
    print(f"[calib] novelty_thresh={novelty_thresh:.4f} discriminates={calib.get('discriminates')} "
          f"n_semantic_buckets_sampled={len(fam_sample)} sem_key_n_bits={SEM_KEY_N_BITS}", flush=True)

    # ---- exposure checkpoints ----
    n_total = len(train)
    cum_counts = [int(round(f * n_total)) for f in CHECKPOINTS]
    real_lib = Library()
    scr_lib = Library()
    real_store = HDFactStore(n_dim=2048, seed=seed, use_index=True)
    scr_store = HDFactStore(n_dim=2048, seed=seed + 1, use_index=True)
    real_state = TierState(seed_base=seed + 100)
    scr_state = TierState(seed_base=seed + 600)
    pair_example_context: Dict[str, str] = {}

    def _mirror_single_promotions(rpt: dict, state: "TierState", source_tag: str) -> None:
        """Forward every genuinely-promoted single-item fact from consolidation_pass's own
        promotion_log into the 3-tier's native_store_gen (mirrors, does not re-derive -- so the
        'no_generalization' ablation's real_store and the full 3-tier's native_store_gen agree
        EXACTLY on single-item promotions, differing ONLY by whether cluster promotions are added)."""
        for e in rpt["promotion_log"]:
            if e["promoted"] and e["lemma"] not in state.promoted_single:
                trust_sym = "TRUST_HIGH" if e["consistency"] >= 0.9 else "TRUST_MID"
                state.native_store_gen.store(e["lemma"], PROMOTE_RELATION, e["label"],
                                             source_tag, trust_sym)
                state.promoted_single.add(e["lemma"])

    always_cache: Optional[dict] = None
    checkpoint_rows = []
    pass_counter = 0
    prev_cum = 0
    tier_diag_log = []

    # ---- resumable per-unit (tools/exp_checkpoint.py, CLAUDE.md mandate) ----
    # Unit grain = (checkpoint_index, arm) -- the 5x9=45-cell dev-eval GRID inside each checkpoint,
    # which is read-only given that checkpoint's already-built Library/HDFactStore/TierState (no
    # cross-arm mutation happens during dev eval). DISCLOSED SCOPE: the SEQUENTIAL exposure +
    # consolidation state-building (process_exposure_slice / consolidation_pass /
    # update_prelim_and_generalize, once per checkpoint, shared across all 9 arms) is NOT itself
    # checkpointed -- it always reruns from checkpoint 0 on resume, same as v1's own prereg
    # ("Resumability granularity: per-seed... finer-grained mid-run checkpointing disproportionate
    # per compute-proportionality"; MEASURED@v1 FULL: 340s total). Serializing the mutable
    # Library/HDFactStore/ScriptLibrary objects to make the state-building itself resumable is out
    # of scope for a one-variable diagnostic rebuild at this wall-time scale. What per-unit
    # checkpointing DOES buy here: a killed/hung run resumes without re-scoring the (up to) 45
    # (checkpoint, arm) x 1954-dev-item evaluation grids it already completed, and every completed
    # unit is durable on disk (units.jsonl) the instant it finishes, independent of the final
    # metrics.json write.
    _ckpt_done = _completed_units(output_dir)
    _ckpt_loaded = _load_units(output_dir) if _ckpt_done else {}
    if _ckpt_done:
        print(f"[checkpoint-resume] {len(_ckpt_done)} (checkpoint,arm) dev-eval units already "
              f"recorded in units.jsonl; skipping recompute for those", flush=True)

    for ck_i, (frac, cum) in enumerate(zip(CHECKPOINTS, cum_counts)):
        if cum > prev_cum:
            slice_ = train[prev_cum:cum]
            process_exposure_slice(slice_, node_set, idx, node_list, real_lib, scr_lib,
                                   pair_example_context,
                                   real_prelim_lib=real_state.prelim_lib,
                                   scr_prelim_lib=scr_state.prelim_lib)
            for _ in range(N_PASSES_PER_CHECKPOINT):
                pass_counter += 1
                rpt_real = consolidation_pass(real_lib, pass_counter, register=False,
                                              native_store=real_store,
                                              promote_source="cskg_crutch_real",
                                              promote_min_exposure=promote_min_exposure)
                _mirror_single_promotions(rpt_real, real_state, "cskg_crutch_real_single")
                # scramble arm gets the SAME loosened gate (fair control per drill 4 -- if lowering
                # the exposure floor let scrambled/false pairs promote too, that would falsify the
                # fix; the false-memory guard is schema_thresh + PROMOTE_MIN_CONSISTENCY, untouched)
                rpt_scr = consolidation_pass(scr_lib, pass_counter, register=False,
                                             native_store=scr_store,
                                             promote_source="cskg_crutch_scramble",
                                             promote_min_exposure=promote_min_exposure)
                _mirror_single_promotions(rpt_scr, scr_state, "cskg_crutch_scramble_single")
            # 3-tier PRELIM retain + CA3/DG cluster registration + combined-evidence promotion --
            # once per checkpoint (matches dev-eval cadence, coarser than per-pass, a disclosed
            # simplification of the intervening-pass rule at this grain -- see prereg).
            tier_diag_real = update_prelim_and_generalize(real_state, idx, novelty_thresh,
                                                           promote_min_exposure=promote_min_exposure,
                                                           node_degree=node_degree)
            tier_diag_scr = update_prelim_and_generalize(scr_state, idx, novelty_thresh,
                                                          promote_min_exposure=promote_min_exposure,
                                                          node_degree=node_degree)
            tier_diag_log.append({"checkpoint_frac": frac, "real": tier_diag_real, "scr": tier_diag_scr})
        prev_cum = cum
        _hb(output_dir, f"checkpoint_{ck_i}_exposure_done", t0,
            {"frac": frac, "n_exposed": cum, "real_lib_items": len(real_lib.items),
             "real_promoted": len(real_store.live_facts()),
             "prelim_pending": len(real_state.prelim_lib.items),
             "combined_promoted": len(real_state.promoted_cluster)})

        ARM_LIST = ("bow", "never_crutch", "always_crutch", "gap_driven", "scramble_crutch",
                   "gap_driven_3tier", "gap_driven_3tier_no_generalization",
                   "gap_driven_3tier_no_pull", "scramble_crutch_3tier")
        per_arm_rows: Dict[str, List[dict]] = {}
        for arm in ARM_LIST:
            if arm == "always_crutch" and always_cache is not None:
                per_arm_rows[arm] = always_cache
                continue
            _uk = _unit_key("ck", ck_i, "arm", arm)
            if _uk in _ckpt_done:
                rows = _ckpt_loaded[_uk]["rows"]
                per_arm_rows[arm] = rows
                if arm == "always_crutch":
                    always_cache = rows
                continue
            if arm == "gap_driven":
                store, t_state = real_store, None
            elif arm == "scramble_crutch":
                store, t_state = scr_store, None
            elif arm == "gap_driven_3tier_no_generalization":
                store, t_state = real_store, real_state
            elif arm in ("gap_driven_3tier", "gap_driven_3tier_no_pull"):
                store, t_state = None, real_state
            elif arm == "scramble_crutch_3tier":
                store, t_state = None, scr_state
            else:
                store, t_state = None, None
            rows = []
            for j, it in enumerate(dev):
                item_id = f"dev{j}"
                res = resolve_item(it, node_set, idx, gate_thresh, arm, item_id,
                                   store=store, node_list=node_list, score_mode=score_mode,
                                   node_degree=node_degree, tier_state=t_state)
                res["correct"] = (res["pred_idx"] == label_idx(it))
                res["item_idx"] = j
                rows.append(res)
            per_arm_rows[arm] = rows
            if arm == "always_crutch":
                always_cache = rows
            _record_unit(output_dir, _uk, {"rows": rows})

        # FAULT-2 diagnostic: retrieval-vs-use split on this checkpoint's gap_driven CRUTCH_RESOLVED
        # items (cheap: only re-scores the CRUTCH_RESOLVED subset, not the full dev set)
        ru_diag = retrieval_use_diagnostic(dev, node_set, idx, per_arm_rows["gap_driven"], score_mode,
                                           node_degree)

        TAGS = ("BOW_RESOLVED", "LIBRARY_RESOLVED", "PRELIM_RESOLVED", "CRUTCH_RESOLVED", "ABSTAINED")
        acc = {arm: sum(1 for r in rows if r["correct"]) / len(rows) for arm, rows in per_arm_rows.items()}
        acc_covered = {}
        for arm, rows in per_arm_rows.items():
            covered_rows = [r for r in rows if dev_crutch_covered[r["item_idx"]]]
            acc_covered[arm] = ((sum(1 for r in covered_rows if r["correct"]) / len(covered_rows))
                                if covered_rows else None)
        tag_counts = {arm: {t: sum(1 for r in rows if r["tag"] == t) for t in TAGS}
                     for arm, rows in per_arm_rows.items()}
        tag_acc = {}
        for arm, rows in per_arm_rows.items():
            tag_acc[arm] = {}
            for t in TAGS:
                sub = [r for r in rows if r["tag"] == t]
                tag_acc[arm][t] = (sum(1 for r in sub if r["correct"]) / len(sub)) if sub else None
        # per-promo_source fidelity split (combined_evidence_cluster vs single-item), gap_driven_3tier
        # only -- HARD-PASS 4 needs this specifically, other arms don't carry promo_source.
        promo_source_acc = {}
        for src in ("combined_evidence_cluster", "cskg_crutch_real_single", "prelim_retain"):
            sub = [r for r in per_arm_rows["gap_driven_3tier"]
                  if r.get("promo_source") == src and r["tag"] in ("LIBRARY_RESOLVED", "PRELIM_RESOLVED")]
            promo_source_acc[src] = {"n": len(sub),
                                     "acc": (sum(1 for r in sub if r["correct"]) / len(sub)) if sub else None}

        crutch_fire_rate = tag_counts["gap_driven"]["CRUTCH_RESOLVED"] / len(dev)
        library_resolved_rate = tag_counts["gap_driven"]["LIBRARY_RESOLVED"] / len(dev)
        scramble_fire_rate = tag_counts["scramble_crutch"]["CRUTCH_RESOLVED"] / len(dev)
        tier_fire_rate = tag_counts["gap_driven_3tier"]["CRUTCH_RESOLVED"] / len(dev)
        tier_library_rate = tag_counts["gap_driven_3tier"]["LIBRARY_RESOLVED"] / len(dev)
        tier_prelim_rate = tag_counts["gap_driven_3tier"]["PRELIM_RESOLVED"] / len(dev)
        no_pull_fire_rate = tag_counts["gap_driven_3tier_no_pull"]["CRUTCH_RESOLVED"] / len(dev)
        no_gen_fire_rate = tag_counts["gap_driven_3tier_no_generalization"]["CRUTCH_RESOLVED"] / len(dev)
        scramble_tier_fire_rate = tag_counts["scramble_crutch_3tier"]["CRUTCH_RESOLVED"] / len(dev)

        checkpoint_rows.append({
            "checkpoint_frac": frac, "n_exposed": cum,
            "accuracy": acc, "accuracy_covered": acc_covered,
            "tag_counts": tag_counts, "tag_accuracy": tag_acc, "promo_source_acc": promo_source_acc,
            "crutch_fire_rate": crutch_fire_rate, "library_resolved_rate": library_resolved_rate,
            "scramble_fire_rate": scramble_fire_rate,
            "tier_fire_rate": tier_fire_rate, "tier_library_rate": tier_library_rate,
            "tier_prelim_rate": tier_prelim_rate, "no_pull_fire_rate": no_pull_fire_rate,
            "no_gen_fire_rate": no_gen_fire_rate, "scramble_tier_fire_rate": scramble_tier_fire_rate,
            "real_lib_pending": len(real_lib.items),
            "real_promoted_n": len(real_store.live_facts()),
            "scr_promoted_n": len(scr_store.live_facts()),
            "prelim_pending_n": len(real_state.prelim_lib.items),
            "prelim_retained_n": len(real_state.prelim_store.live_facts()),
            "n_clusters": len(real_state.cluster_members),
            "n_clusters_eligible_size": sum(1 for m in real_state.cluster_members.values()
                                            if len(m) >= CLUSTER_MIN_MEMBERS),
            "combined_evidence_promoted_n": len(real_state.promoted_cluster),
            "native_gen_promoted_n": len(real_state.native_store_gen.live_facts()),
            "retrieval_use_diagnostic": ru_diag,
            "per_arm_rows": {arm: rows for arm, rows in per_arm_rows.items()},
        })
        print(f"[checkpoint {ck_i} frac={frac}] acc={acc} crutch_fire={crutch_fire_rate:.4f} "
              f"tier_fire={tier_fire_rate:.4f} tier_prelim={tier_prelim_rate:.4f} "
              f"combined_promoted={len(real_state.promoted_cluster)} "
              f"n_clusters={len(real_state.cluster_members)} "
              f"lib_resolved={library_resolved_rate:.4f} promoted={len(real_store.live_facts())} "
              f"retrieval_use={ru_diag}", flush=True)

    # ---- RE-ENCOUNTER FADE RATE (coordinator refinement) ----
    # cohort0 = dev items that genuinely needed the live crutch at checkpoint 0% (zero exposure).
    ck0_rows = checkpoint_rows[0]["per_arm_rows"]["gap_driven"]
    cohort0 = [r for r in ck0_rows if r["tag"] == "CRUTCH_RESOLVED" and r["driving_pair"]]
    cohort0_pairs = {r["item_idx"]: r["driving_pair"] for r in cohort0}
    # real_store is monotonic-append (facts never de-promote once live), and promotions occur in
    # the SAME order consolidation_pass visits them (sorted(library.items) each pass) -- so the
    # first `real_promoted_n` fids recorded live-at-checkpoint-T are EXACTLY the set promoted by T.
    # This lets us reconstruct a per-checkpoint promoted-SET snapshot without re-storing one
    # HDFactStore per checkpoint.
    live_sorted = sorted(real_store.live_facts(), key=lambda f: f.fid)
    re_encounter_curve = []
    for ck_i, ck in enumerate(checkpoint_rows):
        n_live_at_ck = ck["real_promoted_n"]
        promoted_pairs_t = {f.subject for f in live_sorted[:n_live_at_ck]}
        eligible = [j for j, pk in cohort0_pairs.items() if pk in promoted_pairs_t]
        rows_at_ck = {r["item_idx"]: r for r in ck["per_arm_rows"]["gap_driven"]}
        n_native = sum(1 for j in eligible if rows_at_ck[j]["tag"] == "LIBRARY_RESOLVED")
        rate = (n_native / len(eligible)) if eligible else None
        re_encounter_curve.append({"checkpoint_frac": ck["checkpoint_frac"], "n_eligible": len(eligible),
                                   "n_native": n_native, "re_encounter_fade_rate": rate})
    print(f"[re-encounter] cohort0_size={len(cohort0)} curve={re_encounter_curve}", flush=True)

    # ---- fallback constructed probe if natural re-encounters are sparse ----
    fallback_probe = None
    last_eligible = re_encounter_curve[-1]["n_eligible"] if re_encounter_curve else 0
    if last_eligible < 20:
        print("[re-encounter] natural cohort too sparse; running constructed fallback probe", flush=True)
        promoted_final = sorted({f.subject for f in real_store.live_facts()})[:200]
        n_native_probe = 0
        n_probe = 0
        for pk in promoted_final:
            ctx_text = pair_example_context.get(pk)
            if not ctx_text:
                continue
            a, b = pk.split("::", 1)
            distractor = _scramble_partner(f"probe|{pk}", node_list, b)
            probe_item = {"context": ctx_text, "question": "What is most related to this?",
                         "answerA": b, "answerB": distractor, "answerC": "unrelated", "label": "1"}
            res = resolve_item(probe_item, node_set, idx, gate_thresh, "gap_driven", f"probe_{pk}",
                               store=real_store, node_list=node_list, score_mode=score_mode,
                               node_degree=node_degree)
            n_probe += 1
            if res["tag"] == "LIBRARY_RESOLVED":
                n_native_probe += 1
        fallback_probe = {"n_probe": n_probe, "n_native": n_native_probe,
                          "native_answer_rate": (n_native_probe / n_probe) if n_probe else None}
        print(f"[re-encounter] fallback probe: {fallback_probe}", flush=True)

    # ---- arms-must-differ (META_RULE_AF) ----
    # EXEMPTED pair (disclosed, not a bug): "bow" and "never_crutch" share the identical
    # resolve_item code branch BY DESIGN -- never_crutch is defined (prereg "NEVER-CRUTCH arm")
    # as "BoW-only, permanently"; its own Library/HDFactStore exists only to confirm it stays
    # empty (leak check), never to change its predictions. All other 9 pairs must differ.
    ARMS_DIFFER_EXEMPTED = [("bow", "never_crutch")]
    def _digest(rows):
        s = json.dumps([(r["pred_idx"], r["tag"]) for r in rows]).encode("utf-8")
        return hashlib.sha256(s).hexdigest()
    final_ck = checkpoint_rows[-1]["per_arm_rows"]
    digests = {arm: _digest(rows) for arm, rows in final_ck.items()}
    arm_names = list(digests)
    differ_pairs_ok = True
    non_exempt_collisions = []
    for i in range(len(arm_names)):
        for j in range(i + 1, len(arm_names)):
            a, b = arm_names[i], arm_names[j]
            if digests[a] == digests[b]:
                if (a, b) in ARMS_DIFFER_EXEMPTED or (b, a) in ARMS_DIFFER_EXEMPTED:
                    continue  # declared, disclosed, by-design (see comment above)
                differ_pairs_ok = False
                non_exempt_collisions.append((a, b))

    # ---- strip per-arm-rows from checkpoint summary (large; keep aggregate only in metrics) ----
    checkpoint_summary = []
    for ck in checkpoint_rows:
        c = {k: v for k, v in ck.items() if k != "per_arm_rows"}
        checkpoint_summary.append(c)

    # ---- BINARY BASELINE verdict (drill 4 Section 3, UNCHANGED bands/logic -- gap_driven arm only;
    # informational, reported as `binary_baseline_verdict`, NOT the top-level verdict this run) ----
    ck0, ck100 = checkpoint_rows[0], checkpoint_rows[-1]
    fire0, fire100 = ck0["crutch_fire_rate"], ck100["crutch_fire_rate"]
    fire_drop_rel = (fire0 - fire100) / fire0 if fire0 > 0 else 0.0
    fire_drop_abs = fire0 - fire100
    fire_drops = fire_drop_rel >= 0.30 or fire_drop_abs >= 0.10
    upticks = sum(1 for i in range(1, len(checkpoint_rows))
                  if checkpoint_rows[i]["crutch_fire_rate"] - checkpoint_rows[i - 1]["crutch_fire_rate"] > 0.03)
    steep_then_tail = upticks <= 1

    gap_acc0, gap_acc100 = ck0["accuracy"]["gap_driven"], ck100["accuracy"]["gap_driven"]
    bow_acc_final = ck100["accuracy"]["bow"]
    comprehension_lift_binary = gap_acc100 - bow_acc_final
    comprehension_lift = comprehension_lift_binary >= 0.05
    no_regression = all(ck["accuracy"]["gap_driven"] >= ck["accuracy"]["bow"] - 0.02 for ck in checkpoint_rows)

    scramble_controlled = all(abs(ck["accuracy"]["scramble_crutch"] - ck["accuracy"]["bow"]) <= 0.02
                              for ck in checkpoint_rows)
    scramble_never_beats_real = all(ck["accuracy"]["scramble_crutch"] <= ck["accuracy"]["gap_driven"]
                                    for ck in checkpoint_rows)

    consolidation_fidelity_ok = True
    consolidation_fidelity_checks = []
    for ck in checkpoint_rows:
        lib_a = ck["tag_accuracy"]["gap_driven"]["LIBRARY_RESOLVED"]
        cru_a = ck["tag_accuracy"]["gap_driven"]["CRUTCH_RESOLVED"]
        lib_n = ck["tag_counts"]["gap_driven"]["LIBRARY_RESOLVED"]
        cru_n = ck["tag_counts"]["gap_driven"]["CRUTCH_RESOLVED"]
        if lib_n >= 20 and cru_n >= 20:
            ok = lib_a >= (cru_a - 0.03)
            consolidation_fidelity_checks.append({"frac": ck["checkpoint_frac"], "lib_acc": lib_a,
                                                   "cru_acc": cru_a, "ok": ok})
            if not ok:
                consolidation_fidelity_ok = False

    re_encounter_final = re_encounter_curve[-1]["re_encounter_fade_rate"]
    re_encounter_first_measurable = next((c["re_encounter_fade_rate"] for c in re_encounter_curve
                                          if c["re_encounter_fade_rate"] is not None), None)
    re_encounter_rises = (re_encounter_final is not None and re_encounter_first_measurable is not None
                          and (re_encounter_final - re_encounter_first_measurable) >= 0.30)

    binary_hard_fail_reasons = []
    if not fire_drops and not re_encounter_rises:
        binary_hard_fail_reasons.append("CRUTCH_FIRE_RATE_FLAT_AND_RE_ENCOUNTER_FLAT")
    if not comprehension_lift:
        binary_hard_fail_reasons.append(f"COMPREHENSION_FLAT_OR_NO_RISE: lift={comprehension_lift_binary:.4f}")
    if not scramble_controlled:
        binary_hard_fail_reasons.append("SCRAMBLE_BEATS_OR_TIES_BOW")
    if not scramble_never_beats_real:
        binary_hard_fail_reasons.append("SCRAMBLE_TIES_OR_BEATS_REAL_ARM")
    if not consolidation_fidelity_ok:
        binary_hard_fail_reasons.append(f"CONSOLIDATION_FIDELITY_COLLAPSE: {consolidation_fidelity_checks}")
    binary_hard_pass_all = (fire_drops and steep_then_tail and comprehension_lift and no_regression
                            and scramble_controlled and consolidation_fidelity_ok)
    if binary_hard_fail_reasons:
        binary_verdict = "HARD_FAIL"
    elif binary_hard_pass_all:
        binary_verdict = "HARD_PASS"
    else:
        binary_verdict = "MIDDLE_BAND"
    binary_verdict_msg = (
        f"{binary_verdict}: fire_rate[0%->100%]={fire0:.4f}->{fire100:.4f} (rel_drop={fire_drop_rel:.4f} "
        f"abs_drop={fire_drop_abs:.4f} steep_then_tail={steep_then_tail}) | comprehension_lift="
        f"{comprehension_lift_binary:.4f} no_regression={no_regression} | scramble_controlled="
        f"{scramble_controlled} scramble_never_beats_real={scramble_never_beats_real} | "
        f"consolidation_fidelity_ok={consolidation_fidelity_ok} | reasons={binary_hard_fail_reasons}"
    )

    # ---- 3-TIER PRELIM verdict (THIS run's headline question; see prereg HARD-PASS 1-7 /
    # HARD-FAIL, coordinator-refined comprehension framing) ----
    tier_fire0, tier_fire100 = ck0["tier_fire_rate"], ck100["tier_fire_rate"]
    tier_fire_drop_rel = (tier_fire0 - tier_fire100) / tier_fire0 if tier_fire0 > 0 else 0.0
    no_pull_fire0, no_pull_fire100 = ck0["no_pull_fire_rate"], ck100["no_pull_fire_rate"]
    no_pull_fire_drop_rel = (no_pull_fire0 - no_pull_fire100) / no_pull_fire0 if no_pull_fire0 > 0 else 0.0

    # HP1: fade grows at the SAME strict pme, by a real (not floor-hugging) margin
    hp1_fade_grows = tier_fire_drop_rel >= fire_drop_rel + 0.05

    # HP2: fidelity preserved at BOTH new tiers
    tier_fidelity_ok = True
    tier_fidelity_checks = []
    for ck in checkpoint_rows:
        cru_a = ck["tag_accuracy"]["gap_driven_3tier"]["CRUTCH_RESOLVED"]
        cru_n = ck["tag_counts"]["gap_driven_3tier"]["CRUTCH_RESOLVED"]
        for tag in ("LIBRARY_RESOLVED", "PRELIM_RESOLVED"):
            a = ck["tag_accuracy"]["gap_driven_3tier"][tag]
            n = ck["tag_counts"]["gap_driven_3tier"][tag]
            if n >= 20 and cru_n >= 20:
                ok = a >= (cru_a - 0.03)
                tier_fidelity_checks.append({"frac": ck["checkpoint_frac"], "tag": tag, "acc": a,
                                             "cru_acc": cru_a, "ok": ok})
                if not ok:
                    tier_fidelity_ok = False

    # HP3 (coverage-controlled, coordinator refinement): comprehension on dev_crutch_covered
    tier_acc_cov0 = ck0["accuracy_covered"]["gap_driven_3tier"]
    tier_acc_cov100 = ck100["accuracy_covered"]["gap_driven_3tier"]
    binary_acc_cov100 = ck100["accuracy_covered"]["gap_driven"]
    bow_acc_cov100 = ck100["accuracy_covered"]["bow"]
    always_acc_cov100 = ck100["accuracy_covered"]["always_crutch"]
    comp_lift_tier_covered = ((tier_acc_cov100 - bow_acc_cov100)
                              if (tier_acc_cov100 is not None and bow_acc_cov100 is not None) else None)
    comp_lift_binary_covered = ((binary_acc_cov100 - bow_acc_cov100)
                                if (binary_acc_cov100 is not None and bow_acc_cov100 is not None) else None)
    hp3_covered_no_regression = (comp_lift_tier_covered is not None and comp_lift_binary_covered is not None
                                 and comp_lift_tier_covered >= comp_lift_binary_covered - 0.01)
    hf_covered_regression = (comp_lift_tier_covered is not None and comp_lift_binary_covered is not None
                             and comp_lift_tier_covered < comp_lift_binary_covered - 0.03)
    # overall (uncontrolled) comprehension -- reported prominently, NOT gating (coverage-capped)
    comp_lift_tier_overall = ck100["accuracy"]["gap_driven_3tier"] - bow_acc_final
    tier_acc_over_checkpoints = [ck["accuracy"]["gap_driven_3tier"] - ck["accuracy"]["bow"]
                                 for ck in checkpoint_rows]
    tier_deltas = [tier_acc_over_checkpoints[i] - tier_acc_over_checkpoints[i - 1]
                  for i in range(1, len(tier_acc_over_checkpoints))]
    rises_across_checkpoints = sum(1 for d in tier_deltas if d >= -0.01) >= 3

    # HP4: combined-evidence promotion works + high-fidelity
    combined_evidence_promotion_count = ck100["combined_evidence_promoted_n"]
    hp4_promotion_fires = combined_evidence_promotion_count > 0
    combined_acc = ck100["promo_source_acc"]["combined_evidence_cluster"]
    cru_acc_100 = ck100["tag_accuracy"]["gap_driven_3tier"]["CRUTCH_RESOLVED"]
    hp4_promotion_fidelity = (combined_acc["n"] < 5 or cru_acc_100 is None
                              or combined_acc["acc"] >= cru_acc_100 - 0.05)

    # HP5: controls hold (3-tier's OWN scramble arm)
    hp5_scramble_controlled = all(abs(ck["accuracy"]["scramble_crutch_3tier"] - ck["accuracy"]["bow"]) <= 0.02
                                  for ck in checkpoint_rows)
    hp5_scramble_never_beats = all(ck["accuracy"]["scramble_crutch_3tier"] <= ck["accuracy"]["gap_driven_3tier"]
                                   for ck in checkpoint_rows)
    hp5_no_regression = all(ck["accuracy"]["gap_driven_3tier"] >= ck["accuracy"]["bow"] - 0.02
                            for ck in checkpoint_rows)

    # HP6: ablation A (no_generalization must not beat full; structurally zero combined promotions
    # -- the no_generalization arm reads real_store DIRECTLY, which never receives a
    # combined_evidence_cluster store() call (only real_state.native_store_gen does); verify this
    # holds on THIS run's actual live facts, not just by code-reading, in case of an implementation
    # slip).
    no_gen_acc100 = ck100["accuracy"]["gap_driven_3tier_no_generalization"]
    tier_acc100 = ck100["accuracy"]["gap_driven_3tier"]
    hp6_ablation_a = tier_acc100 >= no_gen_acc100 - 0.005
    no_gen_combined_leak = sum(1 for f in real_store.live_facts() if f.source == "combined_evidence_cluster")
    hp6_structural = (no_gen_combined_leak == 0)

    # HP7: ablation B (no_pull must show LESS fade than full)
    hp7_ablation_b = tier_fire_drop_rel - no_pull_fire_drop_rel >= 0.02

    tier_hard_fail_reasons = []
    if tier_fire_drop_rel < fire_drop_rel:
        tier_hard_fail_reasons.append(f"TIER_FADE_REGRESSION: tier_rel_drop={tier_fire_drop_rel:.4f} < "
                                      f"binary_rel_drop={fire_drop_rel:.4f}")
    if not tier_fidelity_ok:
        tier_hard_fail_reasons.append(f"TIER_FIDELITY_COLLAPSE: {tier_fidelity_checks}")
    if hf_covered_regression:
        tier_hard_fail_reasons.append(f"COVERED_COMPREHENSION_REGRESSION: tier={comp_lift_tier_covered:.4f} "
                                      f"binary={comp_lift_binary_covered:.4f}")
    if not (hp5_scramble_controlled and hp5_scramble_never_beats):
        tier_hard_fail_reasons.append("TIER_SCRAMBLE_CONTROL_BROKEN")
    if not hp4_promotion_fires:
        tier_hard_fail_reasons.append("COMBINED_EVIDENCE_NEVER_FIRES: crux mechanism inert")
    if not hp6_structural:
        tier_hard_fail_reasons.append(f"ABLATION_ISOLATION_BUG: no_generalization arm's store leaked "
                                      f"{no_gen_combined_leak} combined_evidence_cluster fact(s)")

    tier_hard_pass_all = (hp1_fade_grows and tier_fidelity_ok and hp3_covered_no_regression
                          and hp4_promotion_fires and hp4_promotion_fidelity and hp5_scramble_controlled
                          and hp5_scramble_never_beats and hp5_no_regression and hp6_ablation_a
                          and hp6_structural and hp7_ablation_b)

    if tier_hard_fail_reasons:
        verdict = "HARD_FAIL"
    elif tier_hard_pass_all:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        f"{verdict}: [3-TIER] tier_fire_rate[0%->100%]={tier_fire0:.4f}->{tier_fire100:.4f} "
        f"(rel_drop={tier_fire_drop_rel:.4f} vs binary={fire_drop_rel:.4f}, HP1={hp1_fade_grows}) | "
        f"tier_fidelity_ok={tier_fidelity_ok} (HP2) | comp_lift_covered tier={comp_lift_tier_covered} "
        f"binary={comp_lift_binary_covered} (HP3={hp3_covered_no_regression}) | comp_lift_overall="
        f"{comp_lift_tier_overall:.4f} rises_across_checkpoints={rises_across_checkpoints} | "
        f"combined_evidence_promoted_n={combined_evidence_promotion_count} combined_acc={combined_acc} "
        f"cru_acc={cru_acc_100} (HP4={hp4_promotion_fires and hp4_promotion_fidelity}) | "
        f"scramble_controlled={hp5_scramble_controlled} scramble_never_beats={hp5_scramble_never_beats} "
        f"no_regression={hp5_no_regression} (HP5) | ablationA(no_gen) acc100={no_gen_acc100:.4f} vs "
        f"tier={tier_acc100:.4f} (HP6={hp6_ablation_a}) | ablationB(no_pull) fire_drop={no_pull_fire_drop_rel:.4f} "
        f"vs tier={tier_fire_drop_rel:.4f} (HP7={hp7_ablation_b}) | reasons={tier_hard_fail_reasons}"
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": f"{verdict}: {verdict_msg[:400]}",
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "config": {"checkpoints": CHECKPOINTS, "n_passes_per_checkpoint": N_PASSES_PER_CHECKPOINT,
                  "train_cap": train_cap, "dev_cap": dev_cap, "seed": seed,
                  "gate_thresh_median_margin": gate_thresh,
                  "promote_min_exposure": promote_min_exposure,
                  "promote_min_exposure_default": PROMOTE_MIN_EXPOSURE,
                  "promote_min_consistency": PROMOTE_MIN_CONSISTENCY,
                  "score_mode": score_mode, "node_degree_computed": node_degree is not None,
                  "cluster_min_members": CLUSTER_MIN_MEMBERS, "novelty_thresh": novelty_thresh,
                  "novelty_calibration": calib},
        "stage0_bow_baseline_accuracy": bow_acc,
        "leakage_audit": {"n_sample": len(leak_sample), "n_leaked": n_leak, "leakage_rate": leakage_rate},
        "coverage_audit": {"n_gap_flagged": n_gap_flagged, "n_covered": n_covered,
                          "coverage_rate": coverage_rate},
        "checkpoints": checkpoint_summary,
        "re_encounter_fade_curve": re_encounter_curve,
        "re_encounter_fallback_probe": fallback_probe,
        "cohort0_size": len(cohort0),
        "tier_diag_log": tier_diag_log,
        "hard_fail_reasons": tier_hard_fail_reasons,
        "bands": {"hp1_fade_grows": hp1_fade_grows, "hp2_tier_fidelity_ok": tier_fidelity_ok,
                 "hp3_covered_no_regression": hp3_covered_no_regression,
                 "hp4_promotion_fires": hp4_promotion_fires,
                 "hp4_promotion_fidelity": hp4_promotion_fidelity,
                 "hp5_scramble_controlled": hp5_scramble_controlled,
                 "hp5_scramble_never_beats": hp5_scramble_never_beats,
                 "hp5_no_regression": hp5_no_regression,
                 "hp6_ablation_a": hp6_ablation_a, "hp6_structural": hp6_structural,
                 "hp7_ablation_b": hp7_ablation_b, "rises_across_checkpoints": rises_across_checkpoints},
        "comprehension": {"overall_tier_lift_100": comp_lift_tier_overall,
                         "overall_binary_lift_100": comprehension_lift_binary,
                         "covered_tier_lift_100": comp_lift_tier_covered,
                         "covered_binary_lift_100": comp_lift_binary_covered,
                         "always_crutch_ceiling_acc_covered_100": always_acc_cov100,
                         "bow_acc_covered_100": bow_acc_cov100},
        "binary_baseline_verdict": binary_verdict, "binary_baseline_verdict_msg": binary_verdict_msg,
        "binary_baseline_bands": {"fire_drops": fire_drops, "steep_then_tail": steep_then_tail,
                                 "comprehension_lift": comprehension_lift, "no_regression": no_regression,
                                 "scramble_controlled": scramble_controlled,
                                 "scramble_never_beats_real": scramble_never_beats_real,
                                 "consolidation_fidelity_ok": consolidation_fidelity_ok,
                                 "re_encounter_rises": re_encounter_rises},
        "arms_differ_verified": differ_pairs_ok,
        "arms_differ_exempted": [list(p) for p in ARMS_DIFFER_EXEMPTED],
        "arms_differ_non_exempt_collisions": non_exempt_collisions,
        "arm_digests": digests,
        "cardinality_ok": len(CHECKPOINTS) == 5 and len(final_ck) == 9,
        "expected_n_units": len(CHECKPOINTS), "expected_n_arms": 9,
        "resumable_per_unit": True,
        "resumable_unit_grain": "checkpoint_x_arm (45 dev-eval units; exposure/consolidation "
                                "state-building itself reruns from checkpoint 0 on resume, "
                                "disclosed scope -- see run() comment)",
        "resumable_units_recorded": len(_completed_units(output_dir)),
        "sem_key_n_bits": SEM_KEY_N_BITS, "sem_key_encoder_dim": SEM_KEY_ENCODER_DIM,
        "sem_key_encoder": "CharTrigramEncoder", "n_semantic_buckets_sampled": len(fam_sample),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "symbolic KB-lookup + vote-count pipeline; no argmax/capacity noise-floor "
                   "discriminator applies",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "calibration_check": "adaptive_with_discriminator_gate",
        "hp_scope": {"dev_checkpoint_eval": ["tier_fire_drop", "tier_comprehension_lift",
                                             "tier_scramble_control", "tier_consolidation_fidelity",
                                             "combined_evidence_promotion", "ablation_underperformance"]},
        "n_cskg_pairs": len(idx), "n_cskg_nodes": len(node_list),
        "n_train_exposed": n_total, "n_dev": len(dev),
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\n[binary_baseline_verdict] {binary_verdict}\n"
          f"elapsed={elapsed:.2f}s -> {output_dir}/metrics.json", flush=True)
    return metrics


# =====================================================================================
# self-test (real code path, tiny synthetic scale, no network)
def self_test() -> dict:
    print("[self-test] tiny synthetic CSKG index + real Library/consolidation_pass/HDFactStore",
          flush=True)
    # tiny synthetic CSKG: concepts a0..a9, pairs forming a few "facts"
    idx = {}
    idx[pair_key("party", "friend")] = [("at:xEffect", 1.0)]
    idx[pair_key("party", "happy")] = [("at:xReact", 1.0)]
    idx[pair_key("rain", "wet")] = [("/r/Causes", 0.6)]
    idx[pair_key("hunger", "food")] = [("/r/MotivatedByGoal", 1.0)]
    node_set = cskg_node_set_from_index(idx)
    node_list = sorted(node_set)
    assert len(node_set) == 7, node_set

    # extract_concepts must find known concepts and skip unknowns; the plural "friends" must
    # resolve to the singular CSKG node "friend" via the stem-variant fallback (surface-form
    # mismatch is real on SIQa's inflected text vs CSKG's lemma-like ids -- see prereg deviation).
    got = extract_concepts("There was a big party with friends and food today", node_set)
    assert "party" in got and "friend" in got and "food" in got, got
    assert "today" not in got, got

    # crutch_candidate_scores: a candidate concept linked to a context concept scores > 0
    ctx_concepts = ["party"]
    ans_lists = [["friend"], ["unrelated"], ["happy"]]
    scores, driving = crutch_candidate_scores(ctx_concepts, ans_lists, idx)
    assert scores[0] > 0 and scores[1] == 0 and scores[2] > 0, scores
    assert driving[0] == pair_key("party", "friend"), driving

    # real Library + consolidation_pass + HDFactStore: repeated exposure -> promotion
    lib = Library()
    store = HDFactStore(n_dim=512, seed=99, use_index=True)
    pk = pair_key("party", "friend")
    for i in range(10):
        cvec = context_vector(f"Nell threw a party and invited many friends round {i}.")
        lib.flag(pk, f"e{i}", "POS", cvec, 0)
    for p in range(1, 6):
        consolidation_pass(lib, p, register=False, native_store=store, promote_source="selftest")
    assert lib.items[pk].status == "GROUNDED_POS", lib.items[pk].status
    hits = store.query(pk, "OUTCOME_POLARITY")
    assert hits and hits[0]["object"] == "POS", hits

    # library_candidate_scores now finds the promoted pair
    l_scores, l_driving = library_candidate_scores(["party"], [["friend"], ["unrelated"]], store)
    assert l_scores[0] == 1.0 and l_scores[1] == 0.0, l_scores

    # resolve_item routing: a synthetic SIQA-shaped item that needs the crutch (BoW gives no signal)
    item = {"context": "There was a big party with friends today.", "question": "How would people feel?",
           "answerA": "excited", "answerB": "sad", "answerC": "happy", "label": "3"}
    res_bow = resolve_item(item, node_set, idx, gate_thresh=0.9, arm="bow", item_id="t0")
    assert res_bow["tag"] == "BOW_RESOLVED"
    res_gap = resolve_item(item, node_set, idx, gate_thresh=0.9, arm="gap_driven", item_id="t0",
                           store=HDFactStore(n_dim=64, seed=1), node_list=node_list)
    assert res_gap["tag"] in ("CRUTCH_RESOLVED", "LIBRARY_RESOLVED", "ABSTAINED", "BOW_RESOLVED")

    # scramble arm must differ in mechanism from real crutch (deterministic wrong-partner draw)
    wrong = _scramble_partner("k1", node_list, "party")
    assert wrong != "party" and wrong in node_set

    # arms-must-differ sanity: bow vs always_crutch predictions can differ on this item
    res_always = resolve_item(item, node_set, idx, gate_thresh=0.9, arm="always_crutch", item_id="t0")
    assert res_always["tag"] in ("CRUTCH_RESOLVED", "BOW_RESOLVED")

    # ---- FAULT-2 fix: score_mode="max_trust" must NOT let edge-COUNT outrank edge-TRUST ----
    # candidate A: 1 TRUST_HIGH edge (party--happy). candidate B: 3 TRUST_MID edges (party--wet,
    # crafted so count_weighted's max*len formula (0.6*3=1.8) beats a single TRUST_HIGH (1.0*1=1.0)
    # -- reproducing the exact use-quality bug this fix targets.
    idx2 = dict(idx)
    idx2[pair_key("party", "wet")] = [("/r/A", 0.6), ("/r/B", 0.6), ("/r/C", 0.6)]
    cw_scores, _ = crutch_candidate_scores(["party"], [["happy"], ["wet"]], idx2, "count_weighted")
    mt_scores, _ = crutch_candidate_scores(["party"], [["happy"], ["wet"]], idx2, "max_trust")
    assert cw_scores[1] > cw_scores[0], cw_scores  # legacy bug: 3-edge TRUST_MID beats 1-edge TRUST_HIGH
    assert mt_scores[0] > mt_scores[1], mt_scores  # fix: single TRUST_HIGH correctly ranks first
    assert argmax_tiebreak(cw_scores) == 1 and argmax_tiebreak(mt_scores) == 0

    # ---- FAULT-2 shipped fix: hub_penalized -- a HIGH-DEGREE ("template-generic") concept must be
    # discounted relative to a LOW-degree, equally-trusted, genuinely-specific connection. Candidate
    # A links via a hub concept ("mouth", degree=500 in this synthetic degree map); candidate B links
    # via a low-degree specific concept ("happy", degree=1) at the SAME trust weight -- hub_penalized
    # must rank B above A despite identical raw trust, exactly the pattern sampled from real
    # retrieval-hit-but-wrong-argmax items (MEASURED@diag, see cell docstring).
    idx3 = dict(idx)
    idx3[pair_key("mouth", "genericword")] = [("/r/X", 1.0)]
    deg_map = {"mouth": 500, "genericword": 500, "happy": 1, "party": 1}
    hp_scores, hp_driving = crutch_candidate_scores(["party", "mouth"], [["happy"], ["genericword"]],
                                                     idx3, "hub_penalized", deg_map)
    assert hp_scores[0] > hp_scores[1], hp_scores  # low-degree "happy" link beats hub "mouth" link
    plain_scores, _ = crutch_candidate_scores(["party", "mouth"], [["happy"], ["genericword"]],
                                              idx3, "max_trust", None)
    assert plain_scores[0] == plain_scores[1], plain_scores  # w/o the penalty they'd tie (both TRUST_HIGH)

    # ---- retrieval_use_diagnostic: a tiny synthetic dev + gap_driven rows, one CRUTCH_RESOLVED
    # item that DID reach gold (retrieval hit, use correct) and one that reached only the wrong
    # candidate (retrieval hit on distractor, gold unreachable -> retrieval MISS)
    dev_syn = [
        {"context": "There was a big party today.", "question": "How would people feel?",
         "answerA": "happy", "answerB": "unrelated", "answerC": "sad", "label": "1"},  # gold=idx0
        {"context": "There was a big party today.", "question": "How would people feel?",
         "answerA": "unrelated", "answerB": "sad", "answerC": "happy", "label": "2"},  # gold=idx1=sad
    ]
    gap_rows_syn = [
        {"item_idx": 0, "tag": "CRUTCH_RESOLVED", "pred_idx": 0, "driving_pair": pair_key("party", "happy")},
        {"item_idx": 1, "tag": "CRUTCH_RESOLVED", "pred_idx": 2, "driving_pair": pair_key("party", "happy")},
    ]
    ru = retrieval_use_diagnostic(dev_syn, node_set, idx, gap_rows_syn, "count_weighted")
    assert ru["n_crutch_resolved"] == 2, ru
    assert ru["retrieval_hit_rate"] == 0.5, ru  # item0's gold(happy) reachable; item1's gold(sad) is not
    assert ru["use_quality_given_hit"] == 1.0, ru  # item0's hit was also correctly used (pred==gold)

    # ---- promote_min_exposure threading: a LOWER floor promotes with FEWER exposures than default.
    # 4 traces = exactly MIN_CONFIRM (the bank-eligibility floor; below this an item never reaches
    # the promotion branch at all, regardless of promote_min_exposure -- this IS the mechanism the
    # FAULT-1 sweep measures: promote_min_exposure only binds when set ABOVE min_confirm=4).
    lib_lo = Library()
    store_lo = HDFactStore(n_dim=256, seed=3, use_index=True)
    pk2 = pair_key("hunger", "food")
    for i in range(4):
        cvec = context_vector(f"She felt hungry and wanted food right now, moment {i}.")
        lib_lo.flag(pk2, f"lo{i}", "POS", cvec, 0)
    for p in range(1, 6):
        consolidation_pass(lib_lo, p, register=False, native_store=store_lo,
                           promote_source="selftest_lo", promote_min_exposure=4)
    assert lib_lo.items[pk2].status == "GROUNDED_POS", lib_lo.items[pk2].status
    hits_lo = store_lo.query(pk2, "OUTCOME_POLARITY")
    assert hits_lo, "lowered promote_min_exposure=4 must promote a 4-trace item (default=8 would not)"
    # same 4-trace item at the DEFAULT floor (8) must NOT promote -- confirms the param is load-bearing
    lib_hi = Library()
    store_hi = HDFactStore(n_dim=256, seed=4, use_index=True)
    for i in range(4):
        cvec = context_vector(f"She felt hungry and wanted food right now, moment {i}.")
        lib_hi.flag(pk2, f"hi{i}", "POS", cvec, 0)
    for p in range(1, 6):
        consolidation_pass(lib_hi, p, register=False, native_store=store_hi, promote_source="selftest_hi")
    hits_hi = store_hi.query(pk2, "OUTCOME_POLARITY")
    assert not hits_hi, "default promote_min_exposure=8 must NOT promote a 4-trace item"

    # =====================================================================================
    # (8) 3-tier PRELIM (2026-08-10): relation_family bucketing + retain-without-promote.
    # relation_family itself is RETAINED unmodified (reference/diagnostic only, no longer the live
    # key) -- re-verified byte-identical to v1 as a regression guard.
    idx_fam = dict(idx2)
    idx_fam[pair_key("boat", "fix")] = [("at:xIntent", 1.0)]
    idx_fam[pair_key("wagon", "fix")] = [("at:xIntent", 1.0)]
    idx_fam[pair_key("gate", "fix")] = [("at:xIntent", 1.0)]
    idx_fam[pair_key("lock", "fix")] = [("at:xIntent", 1.0)]
    idx_fam[pair_key("door", "fix")] = [("at:xIntent", 1.0)]
    idx_fam[pair_key("rain", "wet")] = [("/r/Causes", 0.6)]
    assert relation_family(idx_fam, pair_key("boat", "fix")) == "xintent", relation_family(idx_fam, pair_key("boat", "fix"))
    assert relation_family(idx_fam, pair_key("rain", "wet")) == "causes"
    assert relation_family(idx_fam, "nope::nope") == "UNKNOWN"
    node_set_fam = cskg_node_set_from_index(idx_fam)

    # (8b) v2 ONE-VARIABLE CHANGE self-tests: semantic_relation_key(idx, pk) -- the function that
    # REPLACES relation_family at the live call site inside update_prelim_and_generalize (below).
    # (i) deterministic: same pair_key -> same bucket string, twice.
    sk1 = semantic_relation_key(idx_fam, pair_key("boat", "fix"))
    sk2 = semantic_relation_key(idx_fam, pair_key("boat", "fix"))
    assert sk1 == sk2, f"semantic_relation_key must be deterministic, got {sk1!r} vs {sk2!r}"
    assert sk1.startswith("sem_") and len(sk1) == 4 + SEM_KEY_N_BITS, (
        f"bucket format must be 'sem_' + {SEM_KEY_N_BITS} bits, got {sk1!r}")
    # (ii) idx-independence: unlike relation_family, the key is a property of the CONCEPT PAIR only
    # -- an empty/irrelevant idx must yield the IDENTICAL bucket (no CSKG-edge lookup happens).
    sk_empty_idx = semantic_relation_key({}, pair_key("boat", "fix"))
    assert sk_empty_idx == sk1, (
        f"semantic_relation_key must not depend on idx contents, got {sk_empty_idx!r} vs {sk1!r}")
    # (iii) CONTENT-SENSITIVITY (the actual "semantic embedding" claim, tested on the deterministic
    # ENCODER cosine directly -- non-flaky, unlike asserting exact bucket equality under LSH): two
    # pairs that SHARE a concept ("boat"+"fix" and "wagon"+"fix", both share "fix") must have a
    # STRICTLY higher pair-embedding cosine than two pairs sharing NOTHING ("boat"+"fix" vs
    # "rain"+"wet") -- this is the property that makes semantically-close pairs land in the same (or
    # a neighboring) LSH bucket far more often than unrelated pairs, per _semantic_projection_matrix's
    # own docstring (Charikar 2002 SimHash same-bucket-probability formula).
    def _pair_vec(a, b):
        v = _sem_key_encoder.encode(a) + _sem_key_encoder.encode(b)
        return v / (np.linalg.norm(v) + 1e-9)
    cos_shared = float(np.dot(_pair_vec("boat", "fix"), _pair_vec("wagon", "fix")))
    cos_unrelated = float(np.dot(_pair_vec("boat", "fix"), _pair_vec("rain", "wet")))
    assert cos_shared > cos_unrelated + 0.10, (
        f"a shared-concept pair must embed strictly closer than an unrelated pair: "
        f"cos_shared={cos_shared:.4f} cos_unrelated={cos_unrelated:.4f}")
    # (iv) semantic_relation_key is used in place of relation_family EVEN WHEN idx has no edge for
    # the pair at all (relation_family would return 'UNKNOWN' here; semantic_relation_key must still
    # return a real bucket, since it needs no CSKG edge).
    sk_no_edge = semantic_relation_key(idx_fam, pair_key("nope", "alsonope"))
    assert sk_no_edge.startswith("sem_") and sk_no_edge != "UNKNOWN", (
        f"semantic_relation_key must bucket a pair with NO CSKG edge (unlike relation_family's "
        f"UNKNOWN fallback), got {sk_no_edge!r}")

    state = TierState(seed_base=500)
    pk_sub = pair_key("boat", "fix")  # sub-threshold: n=5 traces, < promote_min_exposure=8
    for i in range(5):
        cvec = context_vector(f"Owen wanted to fix the boat before the trip departed, day {i}.")
        state.prelim_lib.flag(pk_sub, f"pr{i}", "POS", cvec, 0)
    diag8 = update_prelim_and_generalize(state, idx_fam, novelty_thresh=0.15)
    assert diag8["newly_retained"] == 1, diag8
    prelim_hit = state.prelim_store.query(pk_sub, "OUTCOME_POLARITY")
    assert prelim_hit and prelim_hit[0]["object"] == "POS", (
        f"sub-threshold (n=5 < promote_min_exposure=8) item must RETAIN into prelim_store, got {prelim_hit}")
    assert state.native_store_gen.query(pk_sub, "OUTCOME_POLARITY") == [], (
        "a lone sub-threshold item (cluster size 1 < CLUSTER_MIN_MEMBERS) must NOT promote to native")

    # re-encounter PULL: resolve_item with arm=gap_driven_3tier must answer via PRELIM_RESOLVED
    # (not CRUTCH_RESOLVED) once the pair is retained -- the fade lever. Answer words deliberately
    # absent from the context (BoW overlap=0 for all 3 -> tied margin -> gap always flags, matching
    # the base cell's own synthetic-item pattern above).
    item_pull = {"context": "Owen went on a trip with a boat.",
                "question": "What did Owen need to do?", "answerA": "fix", "answerB": "paint",
                "answerC": "unrelated", "label": "1"}
    res_pull = resolve_item(item_pull, node_set_fam, idx_fam, gate_thresh=0.9, arm="gap_driven_3tier",
                            item_id="pull0", node_list=sorted(node_set_fam),
                            tier_state=state)
    assert res_pull["tag"] == "PRELIM_RESOLVED", (
        f"a retained-but-not-promoted pair must resolve via PRELIM at re-encounter, got {res_pull}")

    # (9) combined-evidence promotion: 3 DISTINCT pairs sharing the SAME semantic-embedding LSH
    # bucket (v2: replaces v1's "same relation family" grouping -- MEASURED@this cell's own
    # encoder+projection, verified by direct script before authoring: pair_key("gate","fix"),
    # pair_key("lock","fix"), pair_key("door","fix") all collide at bucket sem_011111 under
    # SEM_KEY_N_BITS=6; NOT hand-waved, actually computed with the exact CharTrigramEncoder +
    # projection this file uses). The CLUSTER gate is 4x stricter than the single-item gate
    # (cluster_exposure_floor = 8*4 = 32; see CLUSTER_EXPOSURE_MULTIPLIER) -- 12 traces/pair alone
    # would NOT cross 32, but COMBINED (12x3=36 >= 32, consistency=1.0 >= 0.75) all 3 cross via the
    # SHARED cluster-grain decision.
    state2 = TierState(seed_base=600)
    cluster_pairs = [pair_key("gate", "fix"), pair_key("lock", "fix"), pair_key("door", "fix")]
    for pk_c in cluster_pairs:
        for i in range(12):
            cvec = context_vector(f"{pk_c} needed repair on trip day {i}, weather was fine today.")
            state2.prelim_lib.flag(pk_c, f"{pk_c}_{i}", "POS", cvec, 0)
    diag9 = update_prelim_and_generalize(state2, idx_fam, novelty_thresh=0.15)
    assert diag9["n_clusters_eligible_size"] >= 1, diag9
    assert diag9["n_combined_promoted_total"] == 3, (
        f"3 sub-threshold same-family pairs whose COMBINED evidence clears the gate must all "
        f"promote, got {diag9}")
    for pk_c in cluster_pairs:
        hit = state2.native_store_gen.query(pk_c, "OUTCOME_POLARITY")
        assert hit and hit[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"), (
            f"{pk_c} must be live in native_store_gen after combined-evidence promotion, got {hit}")

    # (10) fidelity guard: a 4th cluster member whose OWN evidence DISAGREES with the cluster's
    # combined majority must NOT be force-promoted under the cluster's label, AND must not block
    # the 3 genuinely-agreeing members from promoting. White-box construction: register + promote
    # the 3 clean members first (real code path, real match_or_spawn clustering), THEN splice the
    # dissenting member directly into that same cluster's membership set -- isolates the FIDELITY
    # GUARD from clustering-correctness (which test (11) below covers on its own).
    state3 = TierState(seed_base=700)
    for pk_c in cluster_pairs:
        for i in range(12):
            cvec = context_vector(f"{pk_c} needed repair on trip day {i}, weather was fine today.")
            state3.prelim_lib.flag(pk_c, f"{pk_c}_{i}", "POS", cvec, 0)
    idx_fam2 = dict(idx_fam)
    pk_dissent = pair_key("gate", "lock")
    idx_fam2[pk_dissent] = [("at:xIntent", 1.0)]
    diag_reg = update_prelim_and_generalize(state3, idx_fam2, novelty_thresh=0.15)
    assert all(pk_c in state3.promoted_cluster for pk_c in cluster_pairs), (
        f"the 3 clean members must promote on their own combined evidence first, got {diag_reg}")
    for i in range(6):
        cvec = context_vector(f"{pk_dissent} early day {i}.")
        state3.prelim_lib.flag(pk_dissent, f"d{i}", "POS", cvec, 0)
    for i in range(6, 16):
        cvec = context_vector(f"{pk_dissent} later day {i}.")
        state3.prelim_lib.flag(pk_dissent, f"d{i}", "NEG", cvec, 0)
    own_m, _, _ = _vote_margin(state3.prelim_lib.items[pk_dissent].traces)
    assert own_m < 0, f"test construction failed: pk_dissent's own margin must be negative, got {own_m}"
    shared_cluster_id = state3.pk_cluster[cluster_pairs[0]]
    state3.pk_cluster[pk_dissent] = shared_cluster_id
    state3.cluster_members[shared_cluster_id].add(pk_dissent)
    diag10 = update_prelim_and_generalize(state3, idx_fam2, novelty_thresh=0.15)
    assert pk_dissent not in state3.promoted_cluster, (
        "a member whose OWN evidence opposes the cluster majority must NOT be force-promoted "
        f"(guard failed): diag={diag10}")
    assert all(pk_c in state3.promoted_cluster for pk_c in cluster_pairs), (
        "the 3 AGREEING members must still be (remain) promoted despite the dissenting member")

    # (11) DG over-merge tripwire: two DIFFERENT relation families must NOT cluster together at the
    # calibrated novelty_thresh (mirrors script_grain_acquisition_loop's own self-test shape).
    reg_causes = build_instance_register("rain", "wet", "causes", "OUTCOME_POS")
    reg_xintent = build_instance_register("boat", "fix", "xintent", "OUTCOME_POS")
    calib_test = calibrate_novelty_threshold(
        matched_pairs=[(build_instance_register("a", "b", "causes", "OUTCOME_POS"),
                       build_instance_register("c", "d", "causes", "OUTCOME_POS"))],
        wrong_pairs=[(build_instance_register("a", "b", "causes", "OUTCOME_POS"),
                     build_instance_register("c", "d", "xintent", "OUTCOME_POS"))])
    assert calib_test["discriminates"], f"same-vocab family registers must discriminate: {calib_test}"
    state4 = TierState(seed_base=800)
    id_a, spawned_a, _ = state4.script_lib.match_or_spawn(reg_causes, "fam_a", "POS", np.ones(8), 0,
                                                           true_type="causes",
                                                           novelty_thresh=calib_test["novelty_thresh"])
    id_b, spawned_b, _ = state4.script_lib.match_or_spawn(reg_xintent, "fam_b", "POS", np.ones(8), 0,
                                                           true_type="xintent",
                                                           novelty_thresh=calib_test["novelty_thresh"])
    assert spawned_b is True and id_a != id_b, (
        f"different relation families must SPAWN separate clusters, not over-merge: "
        f"id_a={id_a} id_b={id_b} spawned_b={spawned_b}")

    # (12) smoke-diagnosed hub-degree exclusion fix (2026-08-10): a pair driven by a high-degree
    # hub-template concept must NOT retain/cluster-register even with sufficient exposure+coherence.
    state5 = TierState(seed_base=900)
    pk_hub = pair_key("happy", "party")  # 'happy' is the hub concept in this synthetic degree map
    for i in range(6):
        cvec = context_vector(f"happy party day {i}, everyone felt happy about it.")
        state5.prelim_lib.flag(pk_hub, f"h{i}", "POS", cvec, 0)
    deg_map_hub = {"happy": 8000, "party": 5}
    diag_nohub = update_prelim_and_generalize(state5, idx_fam, novelty_thresh=0.15,
                                              node_degree=deg_map_hub, hub_degree_thresh=30)
    assert diag_nohub["n_hub_excluded"] == 1, diag_nohub
    assert state5.prelim_store.query(pk_hub, "OUTCOME_POLARITY") == [], (
        "a hub-concept-driven pair must NOT retain into prelim_store regardless of exposure")
    # without node_degree (default None), the SAME pair retains normally (backward-compatible)
    state6 = TierState(seed_base=901)
    for i in range(6):
        cvec = context_vector(f"happy party day {i}, everyone felt happy about it.")
        state6.prelim_lib.flag(pk_hub, f"h{i}", "POS", cvec, 0)
    diag_withhub = update_prelim_and_generalize(state6, idx_fam, novelty_thresh=0.15)
    assert diag_withhub["n_hub_excluded"] == 0
    assert state6.prelim_store.query(pk_hub, "OUTCOME_POLARITY") != [], (
        "without node_degree, retain behavior must be unchanged (backward-compatible default)")

    print("[self-test] PASS: real Library/consolidation_pass/HDFactStore promotion + routing + "
          "scramble-partner determinism + score_mode max_trust fix + retrieval_use_diagnostic + "
          "promote_min_exposure threading + 3-tier PRELIM retain/pull/combined-evidence-promotion/"
          "fidelity-guard/DG-over-merge-tripwire/hub-degree-exclusion + v2 semantic_relation_key "
          "(determinism/idx-independence/content-sensitivity/no-UNKNOWN-fallback) all exercised",
          flush=True)
    return {"promote_ok": True, "routing_ok": True, "scramble_deterministic": True,
           "score_mode_fix_ok": True, "retrieval_use_diagnostic_ok": True,
           "promote_min_exposure_threading_ok": True,
           "prelim_retain_ok": True, "prelim_pull_ok": True, "combined_evidence_promotion_ok": True,
           "fidelity_guard_ok": True, "dg_overmerge_tripwire_ok": True, "hub_exclusion_ok": True,
           "semantic_relation_key_ok": True}


# =====================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")
    # 2026-08-10 FAULT-1/FAULT-2 diagnostic follow-up: --diag runs a custom-scale profile (not the
    # certified --smoke/--full contract) so the promote_min_exposure sweep + score_mode A/B can be
    # measured cheaply before committing to a FULL dispatch. Output dir is disclosed + tagged.
    ap.add_argument("--diag", action="store_true")
    ap.add_argument("--train-cap", type=int, default=None)
    ap.add_argument("--dev-cap", type=int, default=None)
    ap.add_argument("--promote-min-exposure", type=int, default=PROMOTE_MIN_EXPOSURE)
    ap.add_argument("--score-mode", default="count_weighted",
                    choices=["count_weighted", "max_trust", "hub_penalized"])
    ap.add_argument("--out-tag", default="diag")
    # 2026-08-10 3-tier PRELIM build: --seed (never threaded before -- run()'s seed=7 default was
    # silently unreachable from the CLI) + --out-tag support for --smoke/--full (not just --diag) so
    # a multi-seed 3-tier FULL sweep can write distinct paths without clobbering the committed
    # binary-baseline history at the canonical exp_crutch_fade_social_iqa_v1[_smoke] paths.
    ap.add_argument("--seed", type=int, default=7)
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        tag = f"_{args.out_tag}" if args.out_tag != "diag" else ""
        out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_smoke{tag}")
        run(out, run_mode="smoke", train_cap=SMOKE_TRAIN_CAP, dev_cap=SMOKE_DEV_CAP,
            seed=args.seed, promote_min_exposure=args.promote_min_exposure, score_mode=args.score_mode)
        sys.exit(0)

    if args.diag:
        out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_{args.out_tag}")
        run(out, run_mode="diag", train_cap=args.train_cap, dev_cap=args.dev_cap,
            seed=args.seed, promote_min_exposure=args.promote_min_exposure, score_mode=args.score_mode)
        sys.exit(0)

    tag = f"_{args.out_tag}" if args.out_tag != "diag" else ""
    out = OUTPUT_DIR_FULL + tag
    run(out, run_mode="full", train_cap=None, dev_cap=None,
        seed=args.seed, promote_min_exposure=args.promote_min_exposure, score_mode=args.score_mode)
    sys.exit(0)


if __name__ == "__main__":
    _tag = None
    if "--out-tag" in sys.argv:
        _cli_tag = sys.argv[sys.argv.index("--out-tag") + 1]
        _tag = _cli_tag if _cli_tag != "diag" else None
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_smoke" + (f"_{_tag}" if _tag else ""))
    elif "--diag" in sys.argv:
        _out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_{_tag or 'diag'}")
    else:
        _out = OUTPUT_DIR_FULL + (f"_{_tag}" if _tag else "")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
