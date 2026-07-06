"""exp_cert_ledger_global_consistency_v1: the substrate audits its OWN cert-ledger
for WHOLE-GRAPH structural consistency.

SECOND-tier self-reasoning rung (Rung 1 of the ladder in
notes/research_self_reasoning_next_rungs_ladder_2026-07-05.md). Extends
exp_cert_ledger_self_query_v1 (Tier 1: currency + conflict on a single hand-picked
query) to a GLOBAL SWEEP over the whole supersede/tier graph, checking three
structural invariants -- each via the substrate's OWN CHAIN_GRADE KGStore retrieval
(n8/U1 CERT-585), each reported as an INDEPENDENT discriminator:

  GS-1 CYCLE DETECTION: for every subject with >=2 rows, follow SUPERSEDED_BY
    (multi-hop) with the currency-walk's visited-set logic promoted to an explicit
    output: cycle_detected == True iff the walk revisits a node before MAX_WALK
    (A superseded-by B superseded-by C superseded-by A -- impossible in a valid
    lineage). Ground truth: constructed subjects with an injected cyclic
    SUPERSEDED_BY loop (label True) vs constructed proper linear chains (label False).

  GS-2 FORK DETECTION: for every subject, count DISTINCT current-versions its rows
    resolve to (via currency-walk). >1 distinct sink == two unlinked claimed-lineages
    under one subject label == a FORK. Ground truth: constructed subjects with two
    genuinely-independent unlinked 2-row lineages sharing one subject (label True) vs
    single properly-linked chains (label False).

  GS-3 TIER-MONOTONICITY: for every LINKED chain, walk oldest -> newest (longest
    currency-walk path == root->sink) and flag a PASS-family -> FAIL-family regression
    that carries NO explicit override annotation (retrieved via HAS_OVERRIDE). Ground
    truth: constructed chains with an injected silent regression (label True) vs
    normal upgrades / same-family transitions / EXPLICITLY-overridden revisions
    (all label False; the documented-override negative is the Goodhart/precision
    trap -- flagging it is a HARD_FAIL, worse than a null result).

Discriminator (ALL THREE tasks): reuse self_query_v1's exact scrambled-SUPERSEDED_BY-
target-permutation control, unmodified. Under scramble the invariant-detection
balanced-accuracy MUST collapse toward chance on all three. Report GS-1/GS-2/GS-3 as
THREE INDEPENDENT tiers (do NOT collapse to one verdict string).

HONEST SCOPE (USER-LOCKED, Nelson & Narens 1990 monitor-not-control): this cell only
ever WRITES ITS OWN metrics.json (a report). It NEVER edits cert_ledger.jsonl, never
re-labels a cert_status, never edits code, never auto-dispatches a fix. Narrow glass-box
SELF-CHECK (detect structural inconsistency in its own record), explicitly NOT
self-improvement / self-rewriting. Real-ledger inconsistencies found are reported as an
AUDIT BYPRODUCT with the honest atom_id-collision caveat (a naive fork/cycle heuristic
cannot yet distinguish a genuine contested lineage from an atom_id-string collision
across two unrelated independent atoms -- manual review needed; the CONSTRUCTED overlay,
not the real data, drives the discriminator, mirroring self_query_v1's own discipline).

REUSE NOTE: the load-bearing retrieval functions (tier_family, is_contradiction,
_row_hash, _sup_list, load_real_records, _masked_max, calibrate_tau, the currency-walk,
retrieve_status, retrieve_members, calibrate_tau_member, and the scrambled-control
graph-build) are COPIED VERBATIM (logic-identical) from
experiments/exp_cert_ledger_self_query_v1.py. They are copied, not imported, because
that module runs _selftest() and `if _ARGS.self_test: sys.exit(0)` at IMPORT time -- a
plain `import` of it from a process launched with --self-test would sys.exit(0) during
import and kill this cell before it runs. build_graph is extended (N_REL 3 -> 4) to add
a HAS_OVERRIDE relation needed by GS-3; everything else is byte-for-byte the proven code.

# KB_REFERENT: data/substrate_index/meta/cert_ledger.jsonl

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (write_metrics + atomic crash write)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retrieval-accuracy discriminator; scrambled-control-collapse is the floor
# - baseline_in_band at smoke (naive-flag-none baseline recall==0; scrambled bal-acc near chance)
# - discriminator survives scale (mechanism vs scrambled bal-acc gap identical across N_DIM/seeds)
# - HARD_PASS strictly above floor (recall>=0.90 AND zero FP AND scrambled bal-acc collapse)
# - HP_SCOPE per-arm declaration (mechanism arm only; scrambled is the floor)
# - cardinality_ok (EXPECTED subject/edge counts asserted)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (tau termination gate; scramble still-fires)
# - positive control: single-hop SUPERSEDED_BY edge recall reproduces KGStore at test regime
# - structured_gate_claims populated via record_gate (adopts the Tier-2 gate_claims field)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg

ASCII-only. Single-file. CPU-only (tiny graph). Seed permutes only the random codebook.
"""

from __future__ import annotations

import os

# CUDA env before torch import (import-order rule); this cell is CPU-only anyway.
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import sys
import json
import math
import time
import hashlib
import argparse
import platform
import traceback
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

import torch

# Repo root on path
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.kg_traversal import KGStore  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, record_gate,
)


# ---------------------------------------------------------------------------
# Run-mode detection (runner invokes with NO argv flags -> default FULL)
# ---------------------------------------------------------------------------
def _detect_run_mode() -> str:
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

ANCHOR_NAME = "cert_ledger_global_consistency_v1"
LEDGER_PATH = _REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

# ---------------------------------------------------------------------------
# Bands (pre-registered; see preregs/cert_ledger_global_consistency_v1_2026-07-05.md)
# Three INDEPENDENT tasks; each reported separately.
# ---------------------------------------------------------------------------
HP_RECALL = 0.90            # detection recall on constructed positives (each task)
HF_RECALL = 0.60            # <= -> HARD_FAIL
MAX_CONSTRUCTED_FP = 0      # zero false positives on constructed negatives (strict; Goodhart trap)
MAX_SCRAMBLED_BALACC = 0.65 # scrambled balanced-accuracy must collapse to/below this
HF_SCRAMBLED_BALACC = 0.75  # scrambled bal-acc above this -> discriminator did not collapse -> HARD_FAIL
MIN_DISCRIM_GAP = 0.30      # mechanism_balacc - scrambled_balacc must be >= this
# Real-data gates (per note): GS-1 and GS-3 gate zero real false-positives (null check);
# GS-2 real forks are REPORTED as unconfirmed candidates, NOT gated.
MAX_REAL_CYCLE_FP = 0       # GS-1: zero cycles detected on the real ledger (expected null)
MAX_REAL_REGRESSION_FP = 0  # GS-3: zero silent regressions on the real ledger (expected null)
# Positive control (Gate D): single-hop SUPERSEDED_BY edge recall reproduces KGStore.
HP_POSCTRL = 0.90

# ---------------------------------------------------------------------------
# Regime config
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 2048
    N_PER_CLASS = 10          # positives (and each negative class) per task
    REAL_SAMPLE_MAX = 40
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_PER_CLASS = 20
    REAL_SAMPLE_MAX = 200

MAX_WALK = 8
MEMBER_TOPK = 8

# Constructed shape parameters (deterministic).
CYCLE_LENS = [2, 3, 4]        # GS-1 injected cycle lengths (cycled through)
CHAIN_DEPTHS = [2, 3, 4]      # GS-1/GS-2 proper-chain depths (cycled through)
FORK_LINEAGES = [2, 3]        # GS-2 number of independent lineages in a fork
GS3_DEPTHS = [2, 3]           # GS-3 chain depths (cycled through)

CONFIG_VERSION = (
    "ANCHOR=%s,cert-ledger-global-consistency-v1: N_DIM=%d n_per_class=%d "
    "real_max=%d run_mode=%s; HP recall>=%.2f zeroFP scrambled_balacc<=%.2f gap>=%.2f"
) % (
    ANCHOR_NAME, N_DIM, N_PER_CLASS, REAL_SAMPLE_MAX, RUN_MODE,
    HP_RECALL, MAX_SCRAMBLED_BALACC, MIN_DISCRIM_GAP,
)

# ---------------------------------------------------------------------------
# Tier-family mapping (COPIED VERBATIM from exp_cert_ledger_self_query_v1.py)
# ---------------------------------------------------------------------------
PASS_FAMILY = {
    "chain_grade", "measured_mechanism", "chain_grade_meta_rule",
    "pre_reg_pass", "hard_pass",
}
FAIL_FAMILY = {
    "hard_fail", "honest_negative", "cell_crashed_no_atom",
}


def tier_family(status):
    if status is None:
        return "NEUTRAL"
    s = str(status).strip().lower()
    if s in PASS_FAMILY:
        return "PASS"
    if s in FAIL_FAMILY:
        return "FAIL"
    return "NEUTRAL"


def is_contradiction(fam_a, fam_b):
    """A genuine contradiction: one PASS-family tier and one FAIL-family tier."""
    return {fam_a, fam_b} == {"PASS", "FAIL"}


# ---------------------------------------------------------------------------
# Row-record schema (uniform for constructed + real):
#   {"row_id": str (unique), "subject": str, "status": str|None,
#    "supersedes": str|None (row_id of predecessor), "override": bool}
# ---------------------------------------------------------------------------
_REAL_LOAD_SKIPS = []


def _row_hash(row):
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()[:16]


def _sup_list(val):
    if not val:
        return []
    return val if isinstance(val, list) else [val]


def load_real_records(path, max_rows):
    """Load the real cert-ledger into row-records with row_hash identity.

    COPIED VERBATIM from exp_cert_ledger_self_query_v1.py (adds override=False for
    schema-uniformity; the real ledger has no override field yet). subject = atom_id;
    supersedes kept only when it points at a real row-hash present in the loaded set.
    """
    if not path.exists():
        raise FileNotFoundError("cert_ledger not found at %s" % path)
    raw = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            raw.append(json.loads(line))
        except json.JSONDecodeError:
            _REAL_LOAD_SKIPS.append({"line": i, "failure_class": "LEDGER_JSON_DECODE"})
            continue
    by_atom = defaultdict(list)
    for r in raw:
        by_atom[r.get("atom_id")].append(r)
    multi = [a for a, rs in by_atom.items() if len(rs) > 1 and a is not None]
    ordered = []
    for a in multi:
        ordered.extend(by_atom[a])
    ordered = ordered[:max_rows]
    hashes = {_row_hash(r) for r in ordered}
    records = []
    for r in ordered:
        h = _row_hash(r)
        sup = None
        for t in _sup_list(r.get("supersedes")):
            if isinstance(t, str) and t in hashes and t != h:
                sup = t
                break
        records.append({
            "row_id": h,
            "subject": "real::" + str(r.get("atom_id")),
            "status": r.get("cert_status"),
            "supersedes": sup,
            "override": False,
        })
    return records


# ---------------------------------------------------------------------------
# Constructed synthetic test set for GS-1/GS-2/GS-3 (deterministic; identical
# across codebook seeds -- the seed only permutes the random KGStore codebook).
# ---------------------------------------------------------------------------
def build_constructed():
    """Return dict: {records, gs1, gs2, gs3, edges}.

    gs1/gs2/gs3 each: list of {"subject", "label": bool, "members": [row_id,...]}.
    edges: list of (older_row_id, newer_row_id) for the positive-control reproducer.
    """
    records = []
    edges = []
    gs1 = []
    gs2 = []
    gs3 = []

    def add_row(subj, rid, status, sup, override=False):
        row_id = subj + "::" + rid
        sup_id = (subj + "::" + sup) if sup else None
        records.append({
            "row_id": row_id, "subject": subj, "status": status,
            "supersedes": sup_id, "override": override,
        })
        if sup_id is not None:
            edges.append((sup_id, row_id))   # older superseded-by newer
        return row_id

    # ---- GS-1: cyclic (label True) vs proper linear chain (label False) ----
    for c in range(N_PER_CLASS):
        # cyclic subject: L-cycle r0->r1->...->r(L-1)->r0
        L = CYCLE_LENS[c % len(CYCLE_LENS)]
        subj = "syn::gs1::cycle_%d" % c
        rids = ["r%d" % i for i in range(L)]
        members = []
        for i in range(L):
            # ri supersedes r(i-1 mod L): edge r(i-1) -> ri, and r0 supersedes r(L-1)
            pred = rids[(i - 1) % L]
            members.append(add_row(subj, rids[i], "chain_grade", pred))
        gs1.append({"subject": subj, "label": True, "members": members})

        # proper linear chain: r0 (root) <- r1 <- ... <- rd (sink)
        d = CHAIN_DEPTHS[c % len(CHAIN_DEPTHS)]
        subj = "syn::gs1::linear_%d" % c
        members = []
        prev = None
        for i in range(d + 1):
            rid = "r%d" % i
            members.append(add_row(subj, rid, "chain_grade", prev))
            prev = rid
        gs1.append({"subject": subj, "label": False, "members": members})

    # ---- GS-2: fork (label True) vs proper single chain (label False) ----
    for c in range(N_PER_CLASS):
        # fork: K independent unlinked 2-row lineages sharing one subject label
        K = FORK_LINEAGES[c % len(FORK_LINEAGES)]
        subj = "syn::gs2::fork_%d" % c
        members = []
        for k in range(K):
            root = "l%d_r0" % k
            leaf = "l%d_r1" % k
            members.append(add_row(subj, root, "chain_grade", None))
            members.append(add_row(subj, leaf, "chain_grade", root))
        gs2.append({"subject": subj, "label": True, "members": members})

        # proper single chain (one lineage -> one current version)
        d = CHAIN_DEPTHS[c % len(CHAIN_DEPTHS)]
        subj = "syn::gs2::proper_%d" % c
        members = []
        prev = None
        for i in range(d + 1):
            rid = "r%d" % i
            members.append(add_row(subj, rid, "chain_grade", prev))
            prev = rid
        gs2.append({"subject": subj, "label": False, "members": members})

    # ---- GS-3: silent regression (label True) vs 3 negative classes (label False) ----
    for c in range(N_PER_CLASS):
        d = GS3_DEPTHS[c % len(GS3_DEPTHS)]

        # (positive) silent regression: PASS...PASS then FAIL, no override
        subj = "syn::gs3::regress_%d" % c
        members = []
        prev = None
        for i in range(d + 1):
            status = "hard_fail" if i == d else "chain_grade"
            members.append(add_row(subj, "r%d" % i, status, prev, override=False))
            prev = "r%d" % i
        gs3.append({"subject": subj, "label": True, "members": members})

        # (negative) normal upgrade: FAIL...then PASS (improvement, never flagged)
        subj = "syn::gs3::upgrade_%d" % c
        members = []
        prev = None
        for i in range(d + 1):
            status = "chain_grade" if i == d else "hard_fail"
            members.append(add_row(subj, "r%d" % i, status, prev))
            prev = "r%d" % i
        gs3.append({"subject": subj, "label": False, "members": members})

        # (negative) same PASS-family transition (chain_grade -> measured_mechanism)
        subj = "syn::gs3::samefam_%d" % c
        members = []
        prev = None
        fam_seq = ["chain_grade", "measured_mechanism", "chain_grade"]
        for i in range(d + 1):
            members.append(add_row(subj, "r%d" % i, fam_seq[i % len(fam_seq)], prev))
            prev = "r%d" % i
        gs3.append({"subject": subj, "label": False, "members": members})

        # (negative) DOCUMENTED override: PASS then FAIL but newest carries override
        # (a documented revision, NOT a silent regression -- flagging it is the
        #  Goodhart/precision trap).
        subj = "syn::gs3::override_%d" % c
        members = []
        prev = None
        for i in range(d + 1):
            status = "hard_fail" if i == d else "chain_grade"
            ov = (i == d)   # newest row carries the explicit override annotation
            members.append(add_row(subj, "r%d" % i, status, prev, override=ov))
            prev = "r%d" % i
        gs3.append({"subject": subj, "label": False, "members": members})

    return {"records": records, "gs1": gs1, "gs2": gs2, "gs3": gs3, "edges": edges}


# ---------------------------------------------------------------------------
# Graph builder: records -> KGStore (extends self_query_v1 build_graph with a
# 4th relation HAS_OVERRIDE needed by GS-3). scramble control unchanged.
# ---------------------------------------------------------------------------
REL_SUPERSEDED_BY = 0   # older_row -> newer_row
REL_HAS_STATUS = 1      # row -> status_value_node
REL_SAME_SUBJECT = 2    # subject_node -> row
REL_HAS_OVERRIDE = 3    # row -> override_flag_node (NEW; GS-3)
N_REL = 4

_STATUS_SENTINEL_NULL = "__NULL__"
_OVERRIDE_YES = "override::yes"
_OVERRIDE_NO = "override::no"


def build_graph(records, seed, scramble=None):
    """Build a KGStore over row/status/subject/override entities.

    scramble in {None, "supersedes"} permutes the SUPERSEDED_BY object targets
    (the discriminator control). Returns dict with kg, maps, masks, oracle
    adjacency, and lookups. HAS_STATUS / SAME_SUBJECT / HAS_OVERRIDE are never
    scrambled -- the discriminator isolates the lineage-graph edges.
    """
    gen = torch.Generator()
    gen.manual_seed(seed)

    row_ids = [r["row_id"] for r in records]
    row_set = set(row_ids)
    if len(row_set) != len(row_ids):
        raise ValueError("INVARIANT_VIOLATION: duplicate row_id in records")

    statuses = sorted({(_STATUS_SENTINEL_NULL if r["status"] is None else str(r["status"]))
                       for r in records})
    subjects = sorted({r["subject"] for r in records})

    ent_names = []
    ent_names.extend(("row::" + r) for r in row_ids)
    ent_names.extend(("status::" + s) for s in statuses)
    ent_names.extend(("subject::" + s) for s in subjects)
    ent_names.append(_OVERRIDE_YES)
    ent_names.append(_OVERRIDE_NO)
    eid = {name: i for i, name in enumerate(ent_names)}
    n_ent = len(ent_names)

    row_mask = torch.zeros(n_ent, dtype=torch.bool)
    status_mask = torch.zeros(n_ent, dtype=torch.bool)
    override_mask = torch.zeros(n_ent, dtype=torch.bool)
    for r in row_ids:
        row_mask[eid["row::" + r]] = True
    status_idx = {}
    for s in statuses:
        status_mask[eid["status::" + s]] = True
        status_idx[s] = eid["status::" + s]
    override_mask[eid[_OVERRIDE_YES]] = True
    override_mask[eid[_OVERRIDE_NO]] = True

    kg = KGStore(n_ent=n_ent, n_rel=N_REL, n_dim=N_DIM, generator=gen)

    sup_triples = []
    status_triples = []
    subj_triples = []
    override_triples = []
    oracle_succ = {}
    subj_members = defaultdict(list)

    for r in records:
        rid = r["row_id"]
        st = _STATUS_SENTINEL_NULL if r["status"] is None else str(r["status"])
        status_triples.append((eid["row::" + rid], REL_HAS_STATUS, eid["status::" + st]))
        subj_triples.append((eid["subject::" + r["subject"]], REL_SAME_SUBJECT, eid["row::" + rid]))
        subj_members[r["subject"]].append(rid)
        ov_node = _OVERRIDE_YES if r.get("override") else _OVERRIDE_NO
        override_triples.append((eid["row::" + rid], REL_HAS_OVERRIDE, eid[ov_node]))
        sup = r["supersedes"]
        if sup and sup in row_set:
            sup_triples.append((eid["row::" + sup], REL_SUPERSEDED_BY, eid["row::" + rid]))
            oracle_succ[sup] = rid

    # Scramble control: permute object targets of SUPERSEDED_BY only.
    if scramble == "supersedes" and sup_triples:
        objs = [t[2] for t in sup_triples]
        perm = torch.randperm(len(objs), generator=gen).tolist()
        sup_triples = [(sup_triples[i][0], REL_SUPERSEDED_BY, objs[perm[i]])
                       for i in range(len(sup_triples))]

    all_triples = sup_triples + status_triples + subj_triples + override_triples
    kg.ingest_triples(torch.tensor(all_triples, dtype=torch.long))

    idx_to_rid = {eid["row::" + r]: r for r in row_ids}

    return {
        "kg": kg, "eid": eid, "n_ent": n_ent,
        "row_mask": row_mask, "status_mask": status_mask, "override_mask": override_mask,
        "status_idx": status_idx,
        "override_yes_idx": eid[_OVERRIDE_YES], "override_no_idx": eid[_OVERRIDE_NO],
        "row_ids": row_ids, "subjects": subjects,
        "oracle_succ": oracle_succ, "subj_members": subj_members,
        "has_out_edge": set(oracle_succ.keys()),
        "idx_to_rid": idx_to_rid,
    }


# ---------------------------------------------------------------------------
# Substrate primitives (all via KGStore retrieval; COPIED VERBATIM from
# self_query_v1 except walk_full which promotes the visited-set to a cycle flag).
# ---------------------------------------------------------------------------
def _masked_max(scores, mask):
    m = scores.clone()
    m[~mask] = -1e30
    top_score, top_idx = torch.max(m, dim=0)
    return float(top_score), int(top_idx)


def calibrate_tau(G):
    """Termination gate tau for SUPERSEDED_BY: separate rows-with-edge from sinks.

    COPIED VERBATIM from self_query_v1. Adaptive, principled (refuse-gate style),
    logged; scrambled-control-collapse verifies the discriminator still fires.
    """
    kg, eid, row_mask = G["kg"], G["eid"], G["row_mask"]
    edge_conf, sink_conf = [], []
    for rid in G["row_ids"]:
        s = eid["row::" + rid]
        key = kg.key(s, REL_SUPERSEDED_BY)
        mx, _ = _masked_max(kg.score_all(key), row_mask)
        if rid in G["has_out_edge"]:
            edge_conf.append(mx)
        else:
            sink_conf.append(mx)
    mean_edge = sum(edge_conf) / len(edge_conf) if edge_conf else 0.0
    mean_sink = sum(sink_conf) / len(sink_conf) if sink_conf else 0.0
    tau = 0.5 * (mean_edge + mean_sink)
    return {"tau": tau, "mean_edge_conf": mean_edge, "mean_sink_conf": mean_sink,
            "separation": mean_edge - mean_sink,
            "n_edge": len(edge_conf), "n_sink": len(sink_conf)}


def walk_full(G, start_rid, tau, member_set=None):
    """Iterative SUPERSEDED_BY follow with tau gate + explicit cycle detection.

    Extends self_query_v1's currency_walk: the visited-set break condition is
    promoted to an explicit cycle flag. Returns (final_row_id, path, cycle_detected).
    cycle_detected == True iff the walk would revisit an already-seen node (a
    self-loop or a back-edge) while the edge confidence is still above tau.

    SUBJECT SCOPING: a lineage invariant for one atom must depend ONLY on that
    atom's own rows, never on an unrelated atom's rows. When member_set (a set of
    row_ids for the subject being audited) is supplied, the walk terminates the
    moment it would step to a row OUTSIDE that set. This is the semantically
    correct scope (a per-atom lineage audit) and it is what makes the
    scrambled-SUPERSEDED_BY control collapse cleanly: under scramble a permuted
    edge points to a random global row (almost never same-subject), so the walk
    stops instead of injecting foreign statuses into the per-atom check.
    """
    kg, row_mask = G["kg"], G["row_mask"]
    eid = G["eid"]
    idx_to_rid = G["idx_to_rid"]
    cur = eid["row::" + start_rid]
    path = [start_rid]
    visited = {cur}
    cycle = False
    for _ in range(MAX_WALK):
        key = kg.key(cur, REL_SUPERSEDED_BY)
        mx, top = _masked_max(kg.score_all(key), row_mask)
        if mx < tau:
            break
        if member_set is not None and idx_to_rid.get(top) not in member_set:
            break  # would leave the subject's own row-set -> not part of this lineage
        if top == cur or top in visited:
            cycle = True
            break
        cur = top
        visited.add(cur)
        path.append(idx_to_rid.get(cur, "?"))
    final = idx_to_rid.get(cur, start_rid)
    return final, path, cycle


def retrieve_status(G, rid):
    """Retrieve a row's cert_status via HAS_STATUS (argmax over status nodes).

    COPIED VERBATIM from self_query_v1.
    """
    kg, eid = G["kg"], G["eid"]
    key = kg.key(eid["row::" + rid], REL_HAS_STATUS)
    _, top = _masked_max(kg.score_all(key), G["status_mask"])
    for s, i in G["status_idx"].items():
        if i == top:
            return None if s == _STATUS_SENTINEL_NULL else s
    return None


def retrieve_override(G, rid):
    """Retrieve a row's override annotation via HAS_OVERRIDE (argmax over 2 nodes)."""
    kg, eid = G["kg"], G["eid"]
    key = kg.key(eid["row::" + rid], REL_HAS_OVERRIDE)
    _, top = _masked_max(kg.score_all(key), G["override_mask"])
    return top == G["override_yes_idx"]


def calibrate_tau_member(G):
    """Gate for SAME_SUBJECT: separate true members from non-members.

    COPIED VERBATIM from self_query_v1.
    """
    kg, eid, row_mask = G["kg"], G["eid"], G["row_mask"]
    idx_to_rid = G["idx_to_rid"]
    mem_conf, non_conf = [], []
    for subj in G["subjects"]:
        key = kg.key(eid["subject::" + subj], REL_SAME_SUBJECT)
        scores = kg.score_all(key).clone()
        scores[~row_mask] = -1e30
        true_members = set(G["subj_members"][subj])
        top = torch.topk(scores, k=min(MEMBER_TOPK, int(row_mask.sum())))
        for sc, ix in zip(top.values.tolist(), top.indices.tolist()):
            rid = idx_to_rid.get(ix, "?")
            (mem_conf if rid in true_members else non_conf).append(sc)
    mean_mem = sum(mem_conf) / len(mem_conf) if mem_conf else 0.0
    mean_non = sum(non_conf) / len(non_conf) if non_conf else 0.0
    return 0.5 * (mean_mem + mean_non)


# ---------------------------------------------------------------------------
# Invariant-detection heads (NEW; all built on walk_full / retrieve_* retrieval)
# ---------------------------------------------------------------------------
def detect_cycle(G, members, tau):
    """GS-1: subject is cyclic iff ANY member's SUPERSEDED_BY walk revisits a node."""
    ms = set(members)
    return any(walk_full(G, m, tau, member_set=ms)[2] for m in members)


def detect_fork(G, members, tau):
    """GS-2: subject is a fork iff its rows resolve to >1 distinct current-version."""
    ms = set(members)
    sinks = set()
    for m in members:
        final, _, _ = walk_full(G, m, tau, member_set=ms)
        sinks.add(final)
    return len(sinks) > 1, len(sinks)


def detect_silent_regression(G, members, tau):
    """GS-3: flag a PASS->FAIL step along the resolved (root->sink) chain with no override."""
    ms = set(members)
    best_path = []
    for m in members:
        _, path, _ = walk_full(G, m, tau, member_set=ms)
        if len(path) > len(best_path):
            best_path = path
    if len(best_path) < 2:
        return False
    fams = [tier_family(retrieve_status(G, r)) for r in best_path]
    for i in range(len(best_path) - 1):
        if fams[i] == "PASS" and fams[i + 1] == "FAIL" and not retrieve_override(G, best_path[i + 1]):
            return True
    return False


def _score_task(subjects, detect_fn):
    """Run detect_fn over labeled subjects; return tp/fp/tn/fn + derived metrics + preds."""
    tp = fp = tn = fn = 0
    preds = []
    for s in subjects:
        flagged = bool(detect_fn(s["members"]))
        preds.append(1 if flagged else 0)
        if s["label"] and flagged:
            tp += 1
        elif s["label"] and not flagged:
            fn += 1
        elif (not s["label"]) and flagged:
            fp += 1
        else:
            tn += 1
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    balacc = 0.5 * (recall + specificity)
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "recall": recall, "specificity": specificity,
            "precision": precision, "balanced_accuracy": balacc,
            "preds": preds}


def eval_task(constructed, task_key, G, tau):
    """Eval one GS task on graph G at gate tau. task_key in {gs1,gs2,gs3}."""
    subjects = constructed[task_key]
    if task_key == "gs1":
        fn = lambda members: detect_cycle(G, members, tau)
    elif task_key == "gs2":
        fn = lambda members: detect_fork(G, members, tau)[0]
    elif task_key == "gs3":
        fn = lambda members: detect_silent_regression(G, members, tau)
    else:
        raise ValueError("INVARIANT_VIOLATION: unknown task_key %r" % task_key)
    return _score_task(subjects, fn)


# ---------------------------------------------------------------------------
# Real-data byproduct (audit; REPORTED, gated only where the note specifies)
# ---------------------------------------------------------------------------
def audit_real(G, tau, cap=25):
    """Run all three detectors over the real ledger subjects; return counts + capped lists.

    GS-1 real cycles / GS-3 real regressions are gated (expect 0 -- null/false-positive
    check). GS-2 real forks are REPORTED as UNCONFIRMED candidates (atom_id-collision
    caveat; manual review needed to separate genuine forks from string-collisions).
    """
    real_subjects = sorted({s for s in G["subjects"] if s.startswith("real::")})
    subj_members = G["subj_members"]
    cyc, forks, regr = [], [], []
    for subj in real_subjects:
        members = subj_members.get(subj, [])
        if len(members) < 2:
            continue
        if detect_cycle(G, members, tau):
            cyc.append(subj)
        is_fork, n_sinks = detect_fork(G, members, tau)
        if is_fork:
            forks.append({"subject": subj, "n_rows": len(members), "n_distinct_sinks": n_sinks})
        if detect_silent_regression(G, members, tau):
            regr.append(subj)
    return {
        "n_real_subjects": len(real_subjects),
        "n_real_multirow": sum(1 for s in real_subjects if len(subj_members.get(s, [])) >= 2),
        "cycles": {"count": len(cyc), "subjects": cyc[:cap]},
        "forks_unconfirmed": {"count": len(forks), "candidates": forks[:cap],
                              "caveat": ("UNCONFIRMED audit candidates: a naive distinct-sink "
                                         "fork heuristic cannot yet separate a genuine contested "
                                         "lineage from an atom_id-string collision across two "
                                         "unrelated independent landed atoms. Manual/hdi_skunkworks "
                                         "review required. NOT gated; reported only.")},
        "silent_regressions": {"count": len(regr), "subjects": regr[:cap]},
    }


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def run_seed(seed):
    t0 = time.perf_counter()
    constructed = build_constructed()
    recs_con = constructed["records"]
    recs_real = load_real_records(LEDGER_PATH, REAL_SAMPLE_MAX)
    records = recs_con + recs_real

    # Mechanism graph
    G = build_graph(records, seed=seed, scramble=None)
    tau = calibrate_tau(G)["tau"]
    tau_info = calibrate_tau(G)

    # Scrambled control graph (SUPERSEDED_BY targets permuted)
    Gs = build_graph(records, seed=seed, scramble="supersedes")
    tau_s = calibrate_tau(Gs)["tau"]

    # POSITIVE CONTROL (Gate D): single-hop SUPERSEDED_BY edge recall reproduces KGStore.
    pc_correct = pc_total = 0
    idx_to_rid = G["idx_to_rid"]
    for old, new in G["oracle_succ"].items():
        s = G["eid"]["row::" + old]
        _, top = _masked_max(G["kg"].score_all(G["kg"].key(s, REL_SUPERSEDED_BY)), G["row_mask"])
        pc_correct += int(idx_to_rid.get(top) == new)
        pc_total += 1
    posctrl_recall = pc_correct / pc_total if pc_total else 0.0

    # Three tasks: mechanism + scrambled
    tasks = {}
    for tk in ("gs1", "gs2", "gs3"):
        mech = eval_task(constructed, tk, G, tau)
        scr = eval_task(constructed, tk, Gs, tau_s)
        tasks[tk] = {
            "mechanism": mech, "scrambled": scr,
            "gap_balacc": mech["balanced_accuracy"] - scr["balanced_accuracy"],
        }

    # Real-data byproduct audit
    real = audit_real(G, tau)

    # META_RULE_AF: arms must differ (hash per-subject prediction arrays per task)
    def _digest(obj):
        return hashlib.sha256(json.dumps(obj, sort_keys=True).encode("ascii")).hexdigest()
    arm_digests = {}
    for tk in ("gs1", "gs2", "gs3"):
        arm_digests[tk + "_mechanism"] = _digest(tasks[tk]["mechanism"]["preds"])
        arm_digests[tk + "_scrambled"] = _digest(tasks[tk]["scrambled"]["preds"])

    elapsed = time.perf_counter() - t0
    return {
        "seed": seed,
        "n_records": len(records), "n_ent": G["n_ent"],
        "n_gs1": len(constructed["gs1"]), "n_gs2": len(constructed["gs2"]),
        "n_gs3": len(constructed["gs3"]), "n_edges": len(constructed["edges"]),
        "tau": tau, "tau_scrambled": tau_s, "tau_calib": tau_info,
        "posctrl_recall": posctrl_recall, "posctrl_total": pc_total,
        "tasks": tasks,
        "real": real,
        "arm_digests": arm_digests,
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (GS-1 / GS-2 / GS-3 INDEPENDENT; report all three)
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return sum(xs) / len(xs) if xs else float("nan")


def _task_tier(recall, max_fp_hit, scr_balacc, gap, real_fp_ok):
    """Classify a single task. max_fp_hit: True if any constructed FP occurred.
    real_fp_ok: True if the task's gated real-data null check passed (GS-2 always True).
    """
    hard_pass = (recall >= HP_RECALL and not max_fp_hit
                 and scr_balacc <= MAX_SCRAMBLED_BALACC and gap >= MIN_DISCRIM_GAP
                 and real_fp_ok)
    hard_fail = (recall <= HF_RECALL or max_fp_hit or scr_balacc > HF_SCRAMBLED_BALACC
                 or not real_fp_ok)
    if hard_pass:
        return "HARD_PASS"
    if hard_fail:
        return "HARD_FAIL"
    return "MIDDLE_BAND"


def compute_verdict(per_seed):
    pc = _mean([r["posctrl_recall"] for r in per_seed])

    # ARMS-MUST-DIFFER (META_RULE_AF)
    for r in per_seed:
        d = r["arm_digests"]
        for tk in ("gs1", "gs2", "gs3"):
            m_id = d[tk + "_mechanism"]
            s_id = d[tk + "_scrambled"]
            gap = r["tasks"][tk]["gap_balacc"]
            if m_id == s_id and abs(gap) > 1e-9:
                return ("HARD_FAIL",
                        "META_RULE_AF_VIOLATION: %s mechanism/scrambled preds bit-identical "
                        "but gap=%.3f" % (tk, gap), {})

    # Positive control (Gate D)
    if pc < HP_POSCTRL:
        return ("HARD_FAIL",
                "POSCTRL_INVOCATION_MISMATCH: single-hop edge recall=%.3f < %.2f "
                "(KGStore not reproducing at test regime; downstream suspect)" % (pc, HP_POSCTRL),
                {"posctrl_recall": pc})

    tiers = {}
    detail_tasks = {}
    for tk, real_key, real_gate in (
        ("gs1", "cycles", MAX_REAL_CYCLE_FP),
        ("gs2", None, None),
        ("gs3", "silent_regressions", MAX_REAL_REGRESSION_FP),
    ):
        recall = _mean([r["tasks"][tk]["mechanism"]["recall"] for r in per_seed])
        scr_balacc = _mean([r["tasks"][tk]["scrambled"]["balanced_accuracy"] for r in per_seed])
        mech_balacc = _mean([r["tasks"][tk]["mechanism"]["balanced_accuracy"] for r in per_seed])
        gap = _mean([r["tasks"][tk]["gap_balacc"] for r in per_seed])
        precision = _mean([r["tasks"][tk]["mechanism"]["precision"] for r in per_seed])
        max_fp = max(r["tasks"][tk]["mechanism"]["fp"] for r in per_seed)
        if real_key is None:
            real_fp = None
            real_fp_ok = True
        else:
            real_fp = max(r["real"][real_key]["count"] for r in per_seed)
            real_fp_ok = (real_fp <= real_gate)
        tier = _task_tier(recall, max_fp > MAX_CONSTRUCTED_FP, scr_balacc, gap, real_fp_ok)
        tiers[tk] = tier
        detail_tasks[tk] = {
            "tier": tier, "recall": recall, "precision": precision,
            "mechanism_balacc": mech_balacc, "scrambled_balacc": scr_balacc,
            "gap_balacc": gap, "constructed_fp": max_fp, "real_fp": real_fp,
        }

    # Overall (report all three; blended label only for the runner)
    tier_vals = list(tiers.values())
    if all(t == "HARD_PASS" for t in tier_vals):
        verdict = "HARD_PASS"
    elif all(t == "HARD_FAIL" for t in tier_vals):
        verdict = "HARD_FAIL"
    else:
        verdict = "PARTIAL"

    verdict_msg = (
        "GS1[cycle]=%s recall=%.3f fp=%d scr_balacc=%.3f gap=%.3f real_cyc=%s | "
        "GS2[fork]=%s recall=%.3f fp=%d scr_balacc=%.3f gap=%.3f real_fork_cand=%s | "
        "GS3[monotonicity]=%s recall=%.3f fp=%d scr_balacc=%.3f gap=%.3f real_regr=%s | "
        "posctrl_singlehop=%.3f n_seeds=%d"
    ) % (
        tiers["gs1"], detail_tasks["gs1"]["recall"], detail_tasks["gs1"]["constructed_fp"],
        detail_tasks["gs1"]["scrambled_balacc"], detail_tasks["gs1"]["gap_balacc"],
        str(detail_tasks["gs1"]["real_fp"]),
        tiers["gs2"], detail_tasks["gs2"]["recall"], detail_tasks["gs2"]["constructed_fp"],
        detail_tasks["gs2"]["scrambled_balacc"], detail_tasks["gs2"]["gap_balacc"],
        str(max(r["real"]["forks_unconfirmed"]["count"] for r in per_seed)),
        tiers["gs3"], detail_tasks["gs3"]["recall"], detail_tasks["gs3"]["constructed_fp"],
        detail_tasks["gs3"]["scrambled_balacc"], detail_tasks["gs3"]["gap_balacc"],
        str(detail_tasks["gs3"]["real_fp"]),
        pc, len(per_seed),
    )

    detail = {
        "tiers": tiers,
        "tasks": detail_tasks,
        "posctrl_singlehop_recall": pc,
        "real_fork_candidates_max": max(r["real"]["forks_unconfirmed"]["count"] for r in per_seed),
        "bands": {"HP_RECALL": HP_RECALL, "HF_RECALL": HF_RECALL,
                  "MAX_CONSTRUCTED_FP": MAX_CONSTRUCTED_FP,
                  "MAX_SCRAMBLED_BALACC": MAX_SCRAMBLED_BALACC,
                  "MIN_DISCRIM_GAP": MIN_DISCRIM_GAP,
                  "MAX_REAL_CYCLE_FP": MAX_REAL_CYCLE_FP,
                  "MAX_REAL_REGRESSION_FP": MAX_REAL_REGRESSION_FP},
    }
    return verdict, verdict_msg, detail


def build_gate_claims(detail):
    """Structured gate_claims (adopts the Tier-2 gate_claims field for machine-clean audit)."""
    t = detail["tasks"]
    claims = []
    for tk in ("gs1", "gs2", "gs3"):
        claims.append(record_gate("%s_recall" % tk, t[tk]["recall"], HP_RECALL, ">=",
                                   note="detection recall on constructed positives"))
        claims.append(record_gate("%s_constructed_fp" % tk, t[tk]["constructed_fp"],
                                   MAX_CONSTRUCTED_FP, "<=",
                                   note="false positives on constructed negatives (zero required)"))
        claims.append(record_gate("%s_scrambled_balacc" % tk, t[tk]["scrambled_balacc"],
                                   MAX_SCRAMBLED_BALACC, "<=",
                                   note="scrambled-control balanced accuracy must collapse"))
        claims.append(record_gate("%s_discrim_gap" % tk, t[tk]["gap_balacc"], MIN_DISCRIM_GAP, ">=",
                                   note="mechanism minus scrambled balanced accuracy"))
    claims.append(record_gate("posctrl_singlehop_recall", detail["posctrl_singlehop_recall"],
                              HP_POSCTRL, ">=", note="Gate D: KGStore reproduces at test regime"))
    claims.append(record_gate("gs1_real_cycles", t["gs1"]["real_fp"] or 0, MAX_REAL_CYCLE_FP, "<=",
                              note="real-ledger cycles (null/false-positive check; gated)"))
    claims.append(record_gate("gs3_real_regressions", t["gs3"]["real_fp"] or 0,
                              MAX_REAL_REGRESSION_FP, "<=",
                              note="real-ledger silent regressions (null check; gated)"))
    return claims


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _selftest():
    # T1: KGStore basic single-hop recall (positive control of the reused primitive)
    gen = torch.Generator(); gen.manual_seed(0)
    kg = KGStore(n_ent=10, n_rel=1, n_dim=512, generator=gen)
    kg.ingest_triples(torch.tensor([[0, 0, 1], [1, 0, 2], [2, 0, 3]], dtype=torch.long))
    assert kg.predict_one_hop(0, 0) == 1, "T1: single-hop recall broken"
    assert kg.predict_one_hop(2, 0) == 3, "T1: single-hop recall broken (2->3)"

    # T2: tier-family + contradiction logic
    assert tier_family("chain_grade") == "PASS"
    assert tier_family("hard_fail") == "FAIL"
    assert tier_family("under_classified") == "NEUTRAL"
    assert tier_family(None) == "NEUTRAL"
    assert is_contradiction("PASS", "FAIL") is True
    assert is_contradiction("PASS", "PASS") is False

    # T3: constructed set well-formed; class balance sane
    c = build_constructed()
    assert len(c["gs1"]) == 2 * N_PER_CLASS, "T3: gs1 count"
    assert len(c["gs2"]) == 2 * N_PER_CLASS, "T3: gs2 count"
    assert len(c["gs3"]) == 4 * N_PER_CLASS, "T3: gs3 count (1 pos + 3 neg classes)"
    assert sum(s["label"] for s in c["gs1"]) == N_PER_CLASS, "T3: gs1 positives"
    assert sum(s["label"] for s in c["gs2"]) == N_PER_CLASS, "T3: gs2 positives"
    assert sum(s["label"] for s in c["gs3"]) == N_PER_CLASS, "T3: gs3 positives"
    # row_ids unique
    rids = [r["row_id"] for r in c["records"]]
    assert len(rids) == len(set(rids)), "T3: duplicate row_id in constructed set"

    # T4: mechanism on constructed-only graph -> all three detectors separate pos/neg exactly.
    G = build_graph(c["records"], seed=1, scramble=None)
    tau = calibrate_tau(G)["tau"]
    for tk in ("gs1", "gs2", "gs3"):
        m = eval_task(c, tk, G, tau)
        assert m["recall"] >= 0.90, "T4: %s recall=%.3f < 0.90" % (tk, m["recall"])
        assert m["fp"] == 0, "T4: %s false-positives=%d (must be 0)" % (tk, m["fp"])

    # T4b: override retrieval works (documented-override chain NOT flagged as regression)
    ov_subj = [s for s in c["gs3"] if "override_0" in s["subject"]][0]
    assert not detect_silent_regression(G, ov_subj["members"], tau), \
        "T4b: documented-override chain WRONGLY flagged as silent regression (Goodhart trap)"
    reg_subj = [s for s in c["gs3"] if "regress_0" in s["subject"]][0]
    assert detect_silent_regression(G, reg_subj["members"], tau), \
        "T4b: genuine silent regression NOT detected"

    # T5: scrambled control collapses the discriminator (bal-acc drops) on all three
    Gs = build_graph(c["records"], seed=1, scramble="supersedes")
    tau_s = calibrate_tau(Gs)["tau"]
    for tk in ("gs1", "gs2", "gs3"):
        m = eval_task(c, tk, G, tau)
        s = eval_task(c, tk, Gs, tau_s)
        assert s["balanced_accuracy"] < m["balanced_accuracy"], \
            "T5: %s scrambled bal-acc did not drop (%.3f vs %.3f)" % (
                tk, s["balanced_accuracy"], m["balanced_accuracy"])

    # T6: get_output_dir well-formed
    od = get_output_dir(ANCHOR_NAME)
    assert od.name.startswith("exp_cert_ledger_global_consistency_v1"), "T6: output dir %s" % od.name

    print("[selftest] PASS: KGStore-recall, tier-family, constructed-set, "
          "GS1/GS2/GS3-recall>=0.90-zeroFP, override-retrieval, scrambled-collapses, output-dir",
          flush=True)


# ---------------------------------------------------------------------------
# Defensive: start-marker, heartbeat, crash-diagnostic (Sec 13)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
        "expected_n_units": len(SEEDS), "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, output_dir / "_start_marker.json")


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, output_dir / "metrics.json")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)
    t0_total = time.time()

    # Cardinality (META_RULE_H): expected subject counts deterministic
    c_check = build_constructed()
    expected = {
        "gs1": 2 * N_PER_CLASS, "gs2": 2 * N_PER_CLASS, "gs3": 4 * N_PER_CLASS,
    }
    assert len(c_check["gs1"]) == expected["gs1"], "cardinality gs1"
    assert len(c_check["gs2"]) == expected["gs2"], "cardinality gs2"
    assert len(c_check["gs3"]) == expected["gs3"], "cardinality gs3"

    per_seed = []
    for s in SEEDS:
        hb = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": s,
              "unit_idx": len(per_seed), "total_units": len(SEEDS)}
        (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8").write(json.dumps(hb) + "\n")
        res = run_seed(s)
        # cardinality gate per seed
        if (res["n_gs1"] != expected["gs1"] or res["n_gs2"] != expected["gs2"]
                or res["n_gs3"] != expected["gs3"]):
            raise ValueError("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                             "gs1 %d gs2 %d gs3 %d != %s"
                             % (res["n_gs1"], res["n_gs2"], res["n_gs3"], expected))
        per_seed.append(res)
        print("[progress] seed=%d done elapsed=%.2fs" % (s, res["elapsed_s"]), flush=True)

    verdict, verdict_msg, detail = compute_verdict(per_seed)
    gate_claims = build_gate_claims(detail)

    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "n_seeds": len(per_seed), "seeds": SEEDS,
        "N": N_DIM, "N_DIM": N_DIM, "run_mode": RUN_MODE,
        "device": "cpu",
        "config_version": CONFIG_VERSION,
        "expected_n_subjects": expected,
        "arms": ["gs1_mechanism", "gs1_scrambled", "gs2_mechanism", "gs2_scrambled",
                 "gs3_mechanism", "gs3_scrambled", "posctrl_singlehop"],
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "adaptive_with_discriminator_gate",
        "real_load_skips": _REAL_LOAD_SKIPS,
        "detail": detail,
        "per_seed": per_seed,
        "metrics_source": "measured_cert_ledger_global_consistency_3task",
        "elapsed_s": time.time() - t0_total,
        "summary": verdict_msg[:200],
    }
    write_metrics(out_dir, metrics, results=per_seed, gate_claims=gate_claims)

    print("\n[VERDICT] %s" % verdict, flush=True)
    print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
    print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)


# Self-test always runs at import (cheap); exit if --self-test.
_selftest()
if _ARGS.self_test:
    sys.exit(0)


if __name__ == "__main__":
    _OUT = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_OUT, e)
        raise
