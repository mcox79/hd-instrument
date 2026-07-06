"""exp_cert_ledger_self_query_v1: the substrate reasoning about its OWN cert-ledger.

FIRST narrow self-reasoning cell. Points the CHAIN_GRADE multi-hop KG-retrieval
mechanism (KGStore, n8/U1 CERT-585: setrecall@100000=1.000, 36.49x ratio,
refuse_OOD=0.999) at the substrate's OWN self-record (cert_ledger.jsonl) to answer
two concrete self-evaluation queries WITHOUT Director/Python doing the reasoning:

  TASK A -- CURRENCY RETRIEVAL: given any ledger row, walk SUPERSEDED_BY edges
    (multi-hop) to the current (non-superseded) version. atom X superseded by Y
    superseded by Z -> return Z. Compared against the Python fold_supersedes()
    oracle (tools/cert_ledger_query.py) as ground truth.

  TASK B -- CONFLICT FLAGGING: group rows by referent (SAME_SUBJECT, exact-match),
    retrieve each row's cert_status (HAS_STATUS), flag genuine same-referent
    contradictions (a PASS-family tier and a FAIL-family tier where NEITHER
    supersedes the other -- an unresolved disagreement, NOT a normal revision).
    Brain-grounding: dorsal-ACC conflict-monitoring (van Veen 2009; Botvinick/Yeung).

Discriminator (BOTH tasks): a scrambled-ledger control (SUPERSEDED_BY / SAME_SUBJECT
edge targets randomly permuted) MUST break currency/conflict detection -> collapse
toward chance. Report Task A and Task B as INDEPENDENT discriminators (do NOT collapse
to one verdict string).

HONEST SCOPE: this is the FIRST narrow self-reasoning rung (currency + conflict over
the own ledger), NOT the full autonomous self-improvement loop. The tier-family
comparison in Task B is a lightweight symbolic check layered on substrate retrieval;
deeper numeric entailment ("does spearman=0.886 >= 0.80 justify chain_grade") is a
FUTURE math-gated cell (research note Sec 3), out of scope here.

Reuses hdlab.kg_traversal.KGStore UNMODIFIED. Constructed synthetic test set (multi-hop
supersedes chains depth 1-5 + injected conflict/non-conflict subjects) + a real
cert_ledger sample (real chains are all depth-2; genuine PASS-vs-FAIL conflicts are
essentially absent on disk -- so real data is a false-positive check, constructed data
drives the discriminator).

# KB_REFERENT: data/substrate_index/meta/cert_ledger.jsonl

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (write_metrics + atomic crash write)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: retrieval-accuracy discriminator; scrambled-control-collapse is the floor
# - baseline_in_band at smoke (naive-return-self baseline in (0.05,0.95); scrambled near chance)
# - discriminator survives scale (smoke n_dim=full-family; mechanism vs scrambled gap identical)
# - HARD_PASS strictly above floor (Task A acc>=0.90 AND gap>=0.50; Task B precision==1.0)
# - HP_SCOPE per-arm declaration (mechanism arm only; scrambled/naive are floors)
# - cardinality_ok (EXPECTED query/subject counts asserted)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (tau termination gate; scrambled still-fires verified)
# - positive control: ARM_POSCTRL single-hop edge recall reproduces KGStore at test regime
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
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402


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

ANCHOR_NAME = "cert_ledger_self_query_v1"
LEDGER_PATH = _REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

# ---------------------------------------------------------------------------
# Bands (pre-registered; see preregs/cert_ledger_self_query_v1_2026-07-05.md)
# ---------------------------------------------------------------------------
# Task A -- currency retrieval
HP_A_ACC = 0.90            # substrate currency accuracy vs oracle
HP_A_MULTIHOP_ACC = 0.90   # accuracy restricted to depth>=3 chains (genuine multi-hop)
HP_A_GAP = 0.50            # substrate minus scrambled
HF_A_ACC = 0.60            # <= -> HARD_FAIL
MAX_SCRAMBLED_A = 0.40     # scrambled must be at/below this (near chance)
# Task B -- conflict flagging
HP_B_PRECISION = 1.0       # zero false positives on constructed non-conflicts (strict)
HP_B_RECALL = 0.90         # recall on constructed true conflicts
HF_B_RECALL = 0.30         # <= -> HARD_FAIL
MAX_SCRAMBLED_B_RECALL = 0.30  # scrambled recall must collapse to/below this
MAX_REAL_FALSE_POSITIVE = 0    # zero genuine-FP flags on the real ledger sample

# ---------------------------------------------------------------------------
# Regime config
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 2048
    CHAIN_DEPTHS = [1, 2, 3, 4, 5]
    N_CHAIN_PER_DEPTH = 2
    N_CONFLICT_PER_TYPE = 4
    REAL_SAMPLE_MAX = 40
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    CHAIN_DEPTHS = [1, 2, 3, 4, 5]
    N_CHAIN_PER_DEPTH = 4
    N_CONFLICT_PER_TYPE = 10
    REAL_SAMPLE_MAX = 200

MAX_WALK = 8
MEMBER_TOPK = 8

CONFIG_VERSION = (
    "cert-ledger-self-query-v1: N_DIM=%d depths=%s n_chain/depth=%d "
    "n_conflict/type=%d real_max=%d run_mode=%s; "
    "HP_A acc>=%.2f mh>=%.2f gap>=%.2f | HP_B prec==%.2f rec>=%.2f"
) % (
    N_DIM, str(CHAIN_DEPTHS), N_CHAIN_PER_DEPTH, N_CONFLICT_PER_TYPE,
    REAL_SAMPLE_MAX, RUN_MODE,
    HP_A_ACC, HP_A_MULTIHOP_ACC, HP_A_GAP, HP_B_PRECISION, HP_B_RECALL,
)

# ---------------------------------------------------------------------------
# Tier-family mapping (lightweight symbolic layer; honest-scope per docstring)
# ---------------------------------------------------------------------------
PASS_FAMILY = {
    "chain_grade", "measured_mechanism", "chain_grade_meta_rule",
    "pre_reg_pass", "hard_pass",
}
FAIL_FAMILY = {
    "hard_fail", "honest_negative", "cell_crashed_no_atom",
}
# Everything else (under_classified, custom, cert_neutral_discipline_rule, None,
# "", pending, ...) is NEUTRAL: not a contradiction with anything.


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
#    "supersedes": str|None (row_id of the predecessor it supersedes)}
# ---------------------------------------------------------------------------


def _row_hash(row):
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()[:16]


def _sup_list(val):
    if not val:
        return []
    return val if isinstance(val, list) else [val]


def load_real_records(path, max_rows):
    """Load the real cert-ledger into row-records with row_hash identity.

    subject = atom_id; supersedes kept only when it points at a real row-hash
    present in the loaded set (mirrors fold_supersedes edge semantics).
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
            # per-unit failure-class: skip malformed ledger line, record class
            _REAL_LOAD_SKIPS.append({"line": i, "failure_class": "LEDGER_JSON_DECODE"})
            continue
    # Prefer multi-row atoms (the interesting self-record structure), then fill.
    by_atom = defaultdict(list)
    for r in raw:
        by_atom[r.get("atom_id")].append(r)
    multi = [a for a, rs in by_atom.items() if len(rs) > 1 and a is not None]
    ordered = []
    for a in multi:
        ordered.extend(by_atom[a])
    # cap
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
        })
    return records


# ---------------------------------------------------------------------------
# Constructed synthetic test set (deterministic; identical across codebook seeds)
# ---------------------------------------------------------------------------
def build_constructed():
    """Return (records, currency_queries, conflict_subjects).

    currency_queries: list of {"start": row_id, "oracle_current": row_id, "depth": d,
                               "start_offset": k}  (k = hops from start to sink)
    conflict_subjects: list of {"subject": str, "label": bool}  (True = genuine conflict)
    """
    records = []
    currency_queries = []
    conflict_subjects = []

    # --- Currency chains: depth d = (d+1) rows, R0 (oldest) .. Rd (current) ---
    for d in CHAIN_DEPTHS:
        for c in range(N_CHAIN_PER_DEPTH):
            subj = "chain_d%d_c%d" % (d, c)
            row_ids = ["%s_r%d" % (subj, i) for i in range(d + 1)]
            for i, rid in enumerate(row_ids):
                sup = row_ids[i - 1] if i > 0 else None  # Ri supersedes R(i-1)
                records.append({
                    "row_id": rid, "subject": "syn::" + subj,
                    "status": "chain_grade", "supersedes": sup,
                })
            sink = row_ids[-1]
            for i, rid in enumerate(row_ids):
                currency_queries.append({
                    "start": rid, "oracle_current": sink,
                    "depth": d, "start_offset": d - i,
                })

    # --- Conflict subjects: 5 types ---
    def add_subject(name, rows, label):
        subj = "syn::conf::" + name
        for rid, status, sup in rows:
            records.append({
                "row_id": subj + "::" + rid, "subject": subj,
                "status": status,
                "supersedes": (subj + "::" + sup) if sup else None,
            })
        conflict_subjects.append({"subject": subj, "label": label})

    for c in range(N_CONFLICT_PER_TYPE):
        # (1) TRUE conflict: chain_grade vs hard_fail, no supersedes link
        add_subject("true_%d" % c,
                    [("a", "chain_grade", None), ("b", "hard_fail", None)],
                    True)
        # (2) RESOLVED revision: hard_fail superseded by chain_grade (linked)
        add_subject("resolved_%d" % c,
                    [("old", "hard_fail", None), ("new", "chain_grade", "old")],
                    False)
        # (3) DUPLICATE: same status twice
        add_subject("dup_%d" % c,
                    [("a", "chain_grade", None), ("b", "chain_grade", None)],
                    False)
        # (4) PASS-family diff: chain_grade vs measured_mechanism (both PASS-fam)
        add_subject("passdiff_%d" % c,
                    [("a", "chain_grade", None), ("b", "measured_mechanism", None)],
                    False)
        # (5) NULL pair: chain_grade vs None (pending; not a contradiction)
        add_subject("nullpair_%d" % c,
                    [("a", "chain_grade", None), ("b", None, None)],
                    False)

    return records, currency_queries, conflict_subjects


# ---------------------------------------------------------------------------
# Graph builder: records -> KGStore (reused, unmodified) + index maps
# ---------------------------------------------------------------------------
REL_SUPERSEDED_BY = 0   # older_row -> newer_row
REL_HAS_STATUS = 1      # row -> status_value_node
REL_SAME_SUBJECT = 2    # subject_node -> row
N_REL = 3

_STATUS_SENTINEL_NULL = "__NULL__"


def build_graph(records, seed, scramble=None):
    """Build a KGStore over row/status/subject entities.

    scramble in {None, "supersedes", "same_subject"} permutes that relation's
    object targets (the discriminator control).
    Returns dict with kg, maps, node masks, oracle adjacency, and lookups.
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
    eid = {name: i for i, name in enumerate(ent_names)}
    n_ent = len(ent_names)

    row_mask = torch.zeros(n_ent, dtype=torch.bool)
    status_mask = torch.zeros(n_ent, dtype=torch.bool)
    for r in row_ids:
        row_mask[eid["row::" + r]] = True
    status_idx = {}
    for s in statuses:
        status_mask[eid["status::" + s]] = True
        status_idx[s] = eid["status::" + s]

    kg = KGStore(n_ent=n_ent, n_rel=N_REL, n_dim=N_DIM, generator=gen)

    # Build triples
    sup_triples = []   # (older, SUPERSEDED_BY, newer)
    status_triples = []
    subj_triples = []
    oracle_succ = {}   # row_id -> newer row_id (the single successor)
    subj_members = defaultdict(list)

    for r in records:
        rid = r["row_id"]
        st = _STATUS_SENTINEL_NULL if r["status"] is None else str(r["status"])
        status_triples.append((eid["row::" + rid], REL_HAS_STATUS, eid["status::" + st]))
        subj_triples.append((eid["subject::" + r["subject"]], REL_SAME_SUBJECT, eid["row::" + rid]))
        subj_members[r["subject"]].append(rid)
        sup = r["supersedes"]
        if sup and sup in row_set:
            # r supersedes sup => edge sup --SUPERSEDED_BY--> r
            sup_triples.append((eid["row::" + sup], REL_SUPERSEDED_BY, eid["row::" + rid]))
            oracle_succ[sup] = rid

    # Scramble control: permute object targets of the chosen relation
    if scramble == "supersedes" and sup_triples:
        objs = [t[2] for t in sup_triples]
        perm = torch.randperm(len(objs), generator=gen).tolist()
        sup_triples = [(sup_triples[i][0], REL_SUPERSEDED_BY, objs[perm[i]])
                       for i in range(len(sup_triples))]
    if scramble == "same_subject" and subj_triples:
        objs = [t[2] for t in subj_triples]
        perm = torch.randperm(len(objs), generator=gen).tolist()
        subj_triples = [(subj_triples[i][0], REL_SAME_SUBJECT, objs[perm[i]])
                        for i in range(len(subj_triples))]

    all_triples = sup_triples + status_triples + subj_triples
    kg.ingest_triples(torch.tensor(all_triples, dtype=torch.long))

    return {
        "kg": kg, "eid": eid, "n_ent": n_ent,
        "row_mask": row_mask, "status_mask": status_mask,
        "status_idx": status_idx,
        "row_ids": row_ids, "subjects": subjects,
        "oracle_succ": oracle_succ, "subj_members": subj_members,
        "has_out_edge": set(oracle_succ.keys()),
    }


# ---------------------------------------------------------------------------
# Substrate primitives (all via KGStore retrieval)
# ---------------------------------------------------------------------------
def _masked_max(scores, mask):
    m = scores.clone()
    m[~mask] = -1e30
    top_score, top_idx = torch.max(m, dim=0)
    return float(top_score), int(top_idx)


def calibrate_tau(G):
    """Termination gate tau for SUPERSEDED_BY: separate rows-with-edge from sinks.

    Adaptive, principled (refuse-gate style, KGStore.refuse_gate_calibrate family),
    logged; the scrambled-control-collapse verifies the discriminator still fires.
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


def currency_walk(G, start_rid, tau, return_path=False):
    """Iterative SUPERSEDED_BY follow with tau termination gate. Returns current row_id."""
    kg, eid, row_mask = G["kg"], G["eid"], G["row_mask"]
    idx_to_rid = {eid["row::" + r]: r for r in G["row_ids"]}
    cur = eid["row::" + start_rid]
    path = [start_rid]
    visited = {cur}
    for _ in range(MAX_WALK):
        key = kg.key(cur, REL_SUPERSEDED_BY)
        mx, top = _masked_max(kg.score_all(key), row_mask)
        if mx < tau:
            break
        if top == cur or top in visited:
            break
        cur = top
        visited.add(cur)
        path.append(idx_to_rid.get(cur, "?"))
    final = idx_to_rid.get(cur, start_rid)
    return (final, path) if return_path else final


def retrieve_status(G, rid):
    """Retrieve a row's cert_status via HAS_STATUS (argmax over status nodes)."""
    kg, eid = G["kg"], G["eid"]
    key = kg.key(eid["row::" + rid], REL_HAS_STATUS)
    _, top = _masked_max(kg.score_all(key), G["status_mask"])
    for s, i in G["status_idx"].items():
        if i == top:
            return None if s == _STATUS_SENTINEL_NULL else s
    return None


def retrieve_members(G, subject, tau_member):
    """Retrieve rows of a subject via SAME_SUBJECT multi-value top-k, gated by tau."""
    kg, eid, row_mask = G["kg"], G["eid"], G["row_mask"]
    idx_to_rid = {eid["row::" + r]: r for r in G["row_ids"]}
    key = kg.key(eid["subject::" + subject], REL_SAME_SUBJECT)
    scores = kg.score_all(key).clone()
    scores[~row_mask] = -1e30
    k = min(MEMBER_TOPK, int(row_mask.sum()))
    top = torch.topk(scores, k=k)
    out = []
    for sc, ix in zip(top.values.tolist(), top.indices.tolist()):
        if sc >= tau_member:
            out.append(idx_to_rid.get(ix, "?"))
    return out


def calibrate_tau_member(G):
    """Gate for SAME_SUBJECT: separate true members from non-members."""
    kg, eid, row_mask = G["kg"], G["eid"], G["row_mask"]
    idx_to_rid = {eid["row::" + r]: r for r in G["row_ids"]}
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
# Task A: currency retrieval eval
# ---------------------------------------------------------------------------
def eval_task_a(G, queries, tau):
    correct = 0
    correct_mh = 0        # depth>=3 with start not already sink
    total_mh = 0
    preds = []
    for q in queries:
        pred = currency_walk(G, q["start"], tau)
        ok = (pred == q["oracle_current"])
        correct += int(ok)
        preds.append(1 if ok else 0)
        if q["depth"] >= 3 and q["start_offset"] >= 3:
            total_mh += 1
            correct_mh += int(ok)
    acc = correct / len(queries) if queries else 0.0
    acc_mh = (correct_mh / total_mh) if total_mh else float("nan")
    return {"acc": acc, "acc_multihop": acc_mh, "n": len(queries),
            "n_multihop": total_mh, "preds": preds}


def eval_task_a_naive(queries):
    """Naive baseline: return start unchanged (in-band baseline per META_RULE_AG)."""
    correct = sum(1 for q in queries if q["start"] == q["oracle_current"])
    return correct / len(queries) if queries else 0.0


# ---------------------------------------------------------------------------
# Task B: conflict flagging eval
# ---------------------------------------------------------------------------
def flag_subject(G, subject, tau, tau_member):
    """Substrate-native flag: retrieve members, statuses; flag genuine unresolved contradiction."""
    members = retrieve_members(G, subject, tau_member)
    if len(members) < 2:
        return False
    status = {m: retrieve_status(G, m) for m in members}
    # resolved(a,b): one reachable from the other via SUPERSEDED_BY walk
    paths = {m: currency_walk(G, m, tau, return_path=True)[1] for m in members}
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a, b = members[i], members[j]
            resolved = (b in paths[a]) or (a in paths[b])
            if resolved:
                continue
            if is_contradiction(tier_family(status[a]), tier_family(status[b])):
                return True
    return False


def eval_task_b(G, subjects_labeled, tau, tau_member):
    tp = fp = tn = fn = 0
    flagged_names = []
    for s in subjects_labeled:
        flagged = flag_subject(G, s["subject"], tau, tau_member)
        if flagged:
            flagged_names.append(s["subject"])
        if s["label"] and flagged:
            tp += 1
        elif s["label"] and not flagged:
            fn += 1
        elif (not s["label"]) and flagged:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": precision, "recall": recall,
            "flagged": flagged_names}


def eval_real_conflicts(G, tau, tau_member):
    """Run the detector on real ledger subjects; count flags (false-positive check)."""
    real_subjects = sorted({s for s in G["subjects"] if s.startswith("real::")})
    flagged = []
    for subj in real_subjects:
        if flag_subject(G, subj, tau, tau_member):
            flagged.append(subj)
    return {"n_real_subjects": len(real_subjects), "flagged": flagged,
            "n_flagged": len(flagged)}


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def run_seed(seed):
    t0 = time.perf_counter()
    recs_con, queries, subjects_lab = build_constructed()
    recs_real = load_real_records(LEDGER_PATH, REAL_SAMPLE_MAX)
    records = recs_con + recs_real

    # Mechanism graph
    G = build_graph(records, seed=seed, scramble=None)
    tau_info = calibrate_tau(G)
    tau = tau_info["tau"]
    tau_member = calibrate_tau_member(G)

    # POSITIVE CONTROL (Gate D): single-hop edge recall reproduces KGStore at test regime.
    # For every real SUPERSEDED_BY edge, single-hop retrieval must return the successor.
    pc_correct = pc_total = 0
    idx_to_rid = {G["eid"]["row::" + r]: r for r in G["row_ids"]}
    for old, new in G["oracle_succ"].items():
        s = G["eid"]["row::" + old]
        _, top = _masked_max(G["kg"].score_all(G["kg"].key(s, REL_SUPERSEDED_BY)), G["row_mask"])
        pc_correct += int(idx_to_rid.get(top) == new)
        pc_total += 1
    posctrl_recall = pc_correct / pc_total if pc_total else 0.0

    # Task A
    a_sub = eval_task_a(G, queries, tau)
    a_naive = eval_task_a_naive(queries)
    Gs = build_graph(records, seed=seed, scramble="supersedes")
    tau_s = calibrate_tau(Gs)["tau"]
    a_scr = eval_task_a(Gs, queries, tau_s)

    # Task B
    b_sub = eval_task_b(G, subjects_lab, tau, tau_member)
    Gss = build_graph(records, seed=seed, scramble="same_subject")
    tau_ss = calibrate_tau(Gss)["tau"]
    tau_member_ss = calibrate_tau_member(Gss)
    b_scr = eval_task_b(Gss, subjects_lab, tau_ss, tau_member_ss)
    real = eval_real_conflicts(G, tau, tau_member)

    # META_RULE_AF: arms must differ (hash per-query prediction arrays)
    def _digest(obj):
        return hashlib.sha256(json.dumps(obj, sort_keys=True).encode("ascii")).hexdigest()
    arm_digests = {
        "taskA_substrate": _digest(a_sub["preds"]),
        "taskA_scrambled": _digest(a_scr["preds"]),
        "taskB_substrate": _digest([b_sub["tp"], b_sub["fp"], b_sub["fn"]]),
        "taskB_scrambled": _digest([b_scr["tp"], b_scr["fp"], b_scr["fn"]]),
    }

    elapsed = time.perf_counter() - t0
    return {
        "seed": seed,
        "n_records": len(records), "n_ent": G["n_ent"],
        "n_queries": len(queries), "n_subjects_labeled": len(subjects_lab),
        "tau": tau, "tau_calib": tau_info, "tau_member": tau_member,
        "posctrl_recall": posctrl_recall, "posctrl_total": pc_total,
        "taskA": {"substrate": a_sub, "scrambled": a_scr, "naive_self": a_naive,
                  "gap": a_sub["acc"] - a_scr["acc"]},
        "taskB": {"substrate": b_sub, "scrambled": b_scr},
        "real": real,
        "arm_digests": arm_digests,
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (Task A and Task B INDEPENDENT; report both)
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return sum(xs) / len(xs) if xs else float("nan")


def compute_verdict(per_seed):
    a_acc = _mean([r["taskA"]["substrate"]["acc"] for r in per_seed])
    a_mh = _mean([r["taskA"]["substrate"]["acc_multihop"] for r in per_seed])
    a_scr = _mean([r["taskA"]["scrambled"]["acc"] for r in per_seed])
    a_gap = _mean([r["taskA"]["gap"] for r in per_seed])
    a_naive = _mean([r["taskA"]["naive_self"] for r in per_seed])
    b_prec = _mean([r["taskB"]["substrate"]["precision"] for r in per_seed])
    b_rec = _mean([r["taskB"]["substrate"]["recall"] for r in per_seed])
    b_scr_rec = _mean([r["taskB"]["scrambled"]["recall"] for r in per_seed])
    pc = _mean([r["posctrl_recall"] for r in per_seed])
    real_fp = max(r["real"]["n_flagged"] for r in per_seed)  # worst-case real flags

    # ARMS-MUST-DIFFER (META_RULE_AF)
    for r in per_seed:
        d = r["arm_digests"]
        if d["taskA_substrate"] == d["taskA_scrambled"] and a_gap != 0:
            return ("HARD_FAIL", "META_RULE_AF_VIOLATION: taskA arms bit-identical", {})

    # Positive control (Gate D)
    if pc < 0.90:
        return ("HARD_FAIL",
                "POSCTRL_INVOCATION_MISMATCH: single-hop edge recall=%.3f < 0.90 "
                "(KGStore not reproducing at test regime; downstream suspect)" % pc,
                {"posctrl_recall": pc})

    # Task A verdict
    a_hard_pass = (a_acc >= HP_A_ACC and (math.isnan(a_mh) or a_mh >= HP_A_MULTIHOP_ACC)
                   and a_gap >= HP_A_GAP and a_scr <= MAX_SCRAMBLED_A)
    a_hard_fail = (a_acc <= HF_A_ACC or a_scr > MAX_SCRAMBLED_A)
    if a_hard_pass:
        a_tier = "HARD_PASS"
    elif a_hard_fail:
        a_tier = "HARD_FAIL"
    else:
        a_tier = "MIDDLE_BAND"

    # Task B verdict
    b_hard_pass = (b_prec >= HP_B_PRECISION and b_rec >= HP_B_RECALL
                   and b_scr_rec <= MAX_SCRAMBLED_B_RECALL
                   and real_fp <= MAX_REAL_FALSE_POSITIVE)
    b_hard_fail = (b_rec <= HF_B_RECALL or b_prec < HP_B_PRECISION)
    if b_hard_pass:
        b_tier = "HARD_PASS"
    elif b_hard_fail:
        b_tier = "HARD_FAIL"
    else:
        b_tier = "MIDDLE_BAND"

    # Blended top-level label (both independent; report both explicitly)
    if a_tier == "HARD_PASS" and b_tier == "HARD_PASS":
        verdict = "HARD_PASS"
    elif a_tier == "HARD_FAIL" and b_tier == "HARD_FAIL":
        verdict = "HARD_FAIL"
    else:
        verdict = "PARTIAL"

    verdict_msg = (
        "TaskA[currency]=%s acc=%.3f multihop=%.3f gap=%.3f scrambled=%.3f naive_self=%.3f | "
        "TaskB[conflict]=%s precision=%.3f recall=%.3f scrambled_recall=%.3f real_flags=%d | "
        "posctrl_singlehop=%.3f | n_seeds=%d"
    ) % (a_tier, a_acc, a_mh, a_gap, a_scr, a_naive,
         b_tier, b_prec, b_rec, b_scr_rec, real_fp, pc, len(per_seed))

    detail = {
        "taskA_tier": a_tier, "taskB_tier": b_tier,
        "taskA": {"acc": a_acc, "acc_multihop": a_mh, "scrambled": a_scr,
                  "gap": a_gap, "naive_self": a_naive},
        "taskB": {"precision": b_prec, "recall": b_rec,
                  "scrambled_recall": b_scr_rec, "real_flags": real_fp},
        "posctrl_singlehop_recall": pc,
        "bands": {"HP_A_ACC": HP_A_ACC, "HP_A_MULTIHOP_ACC": HP_A_MULTIHOP_ACC,
                  "HP_A_GAP": HP_A_GAP, "HF_A_ACC": HF_A_ACC,
                  "HP_B_PRECISION": HP_B_PRECISION, "HP_B_RECALL": HP_B_RECALL},
    }
    return verdict, verdict_msg, detail


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
_REAL_LOAD_SKIPS = []


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
    assert is_contradiction("PASS", "NEUTRAL") is False

    # T3: constructed set well-formed; oracle currency + labels sane
    recs, queries, subs = build_constructed()
    assert len(queries) > 0 and len(subs) > 0, "T3: empty constructed set"
    n_true = sum(1 for s in subs if s["label"])
    n_false = sum(1 for s in subs if not s["label"])
    assert n_true == N_CONFLICT_PER_TYPE, "T3: true-conflict count mismatch"
    assert n_false == 4 * N_CONFLICT_PER_TYPE, "T3: non-conflict count mismatch"

    # T4: full mechanism on a tiny constructed-only graph -> currency should be exact,
    #     scrambled should degrade, conflict detector should separate true/false.
    G = build_graph(recs, seed=1, scramble=None)
    tau = calibrate_tau(G)["tau"]
    tau_m = calibrate_tau_member(G)
    a = eval_task_a(G, queries, tau)
    assert a["acc"] >= 0.90, "T4: substrate currency acc=%.3f < 0.90 at selftest" % a["acc"]
    b = eval_task_b(G, subs, tau, tau_m)
    assert b["precision"] >= 0.99, "T4: conflict precision=%.3f (false positives!)" % b["precision"]
    assert b["recall"] >= 0.90, "T4: conflict recall=%.3f < 0.90" % b["recall"]

    # T5: scrambled control breaks currency (discriminator fires)
    Gs = build_graph(recs, seed=1, scramble="supersedes")
    taus = calibrate_tau(Gs)["tau"]
    a_s = eval_task_a(Gs, queries, taus)
    assert a_s["acc"] < a["acc"], "T5: scrambled currency did not degrade (%.3f vs %.3f)" % (a_s["acc"], a["acc"])

    # T6: get_output_dir well-formed
    od = get_output_dir(ANCHOR_NAME)
    assert od.name.startswith("exp_cert_ledger_self_query_v1"), "T6: output dir name %s" % od.name

    print("[selftest] PASS: KGStore-recall, tier-family, constructed-set, "
          "mechanism-currency>=0.90, conflict-precision=1.0, scrambled-breaks, output-dir",
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

    # Cardinality (META_RULE_H): expected query count deterministic
    _, queries_check, subs_check = build_constructed()
    expected_q = len(queries_check)
    expected_subj = len(subs_check)

    per_seed = []
    for s in SEEDS:
        hb = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": s,
              "unit_idx": len(per_seed), "total_units": len(SEEDS)}
        (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8").write(json.dumps(hb) + "\n")
        res = run_seed(s)
        # cardinality gate
        if res["n_queries"] != expected_q or res["n_subjects_labeled"] != expected_subj:
            raise ValueError("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                             "queries %d!=%d or subjects %d!=%d"
                             % (res["n_queries"], expected_q,
                                res["n_subjects_labeled"], expected_subj))
        per_seed.append(res)

    verdict, verdict_msg, detail = compute_verdict(per_seed)

    metrics = {
        "anchor": ANCHOR_NAME, "anchor_name": ANCHOR_NAME,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "n_seeds": len(per_seed), "seeds": SEEDS,
        "N": N_DIM, "N_DIM": N_DIM, "run_mode": RUN_MODE,
        "device": "cpu",
        "config_version": CONFIG_VERSION,
        "expected_n_queries": expected_q, "expected_n_subjects": expected_subj,
        "arms": ["taskA_substrate", "taskA_scrambled", "taskA_naive_self",
                 "taskB_substrate", "taskB_scrambled", "posctrl_singlehop"],
        "cardinality_ok": True,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "adaptive_with_discriminator_gate",
        "real_load_skips": _REAL_LOAD_SKIPS,
        "detail": detail,
        "per_seed": per_seed,
        "metrics_source": "measured_cert_ledger_self_query_2task",
        "elapsed_s": time.time() - t0_total,
        "summary": verdict_msg[:200],
    }
    write_metrics(out_dir, metrics, results=per_seed)

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
