"""NATIVE_BIND_COMPOSE: does the SUBSTRATE'S OWN native multiplicative (Hadamard) bind + one-shot Hebbian memory
support the ANCHOR_COMPOSE "compose an unseen entity from its support-edge estimates" pattern, delivering the
held-out-ENTITY inductive win -- WITHOUT the additive SGD machinery? (Stage-0 decisive test.)

THE QUESTION (CITED@notes/research_anchor_compose_live_store_integration_path_2026-07-13.md). The VET-confirmed
inductive win (exp_anchor_compose_inductive_entity_cskg_v1) was built on a GRADIENT-TRAINED, low-dim (k=24),
ADDITIVE (TransE) geometry: E_derived[t] = mean_i(X[h_i] + D[r_i]) with direct Euclidean readout. The LIVE store
(hdlab.kg_traversal.KGStore -- the CERT-584/585 chain-grade primitive, 36.49x ratio) is a DIFFERENT regime:
fixed-random bipolar atoms E/R (n_dim=1024), MULTIPLICATIVE bind key(s,p)=E[s]*R[p]*sqrt(n_dim), one-shot Hebbian
W (W += outer(E[o], key)/n_dim; NO gradient descent), bilinear readout score_all(key)=E@(W@key). This cell tests
whether the store's OWN native bind, used with the SAME compose pattern, already carries the induction -- a cheap
CPU probe that resolves which of two very-different-cost integration paths is correct:
  HARD-PASS -> the substrate NATIVELY does inductive generalization; live integration is CHEAP (Stage-0a).
  HARD-FAIL -> the additive SGD construction is essential; a costly adjunct bridge is needed (Stage-0b).
Both outcomes are decisive and publishable-internally.

NATIVE COMPOSE (the crux; the multiplicative-bind analog of the additive mean bundle):
  For a held-out entity t whose (test-time-visible) SUPPORT edges reach seen anchors h_i via relation r_i:
      recall_i    = W @ key(h_i, r_i)                 # the store's OWN Hebbian tail-recall (E-space estimate)
      E_derived[t] = sign( sum_i recall_i )           # MAJORITY-SIGN bundle -> bipolar, SAME format/norm as E
  Majority-sign (not a real-valued mean) keeps the composed code in the store's native bipolar format so its
  norm is degree-INVARIANT and does not create a magnitude/popularity confound in the dot-product readout.
  The composed code REPLACES the held-out entity's fixed-random row in the candidate codebook; the held-out
  QUERY edges are then scored by the store's native readout scores = E_patched @ (W @ key(h_q, r_q)). W is FROZEN
  on both-seen TRAIN edges; SUPPORT and QUERY edges of a held-out entity are DISJOINT -> genuine zero-shot, no
  leakage. This is a NEW READ PATH added in-cell; KGStore's E/R/W and CERT-584/585 code paths are NOT modified.

ARMS (all scored PAIRED on the SAME held-out QUERY edges + candidate set; native bilinear readout unless noted):
  NATIVE_ANCHOR_COMPOSE : held-out codes REPLACED by E_derived (majority-sign bundle of W@key support estimates). MECHANISM.
  MEMORIZE_FIXEDCODE    : held-out codes stay the store's FIXED random bipolar row (never touched by W). The direct
                          native memorize control -- same W, same query recall; ONLY the held-out code differs.
  RANDOM_CODES          : random bipolar candidate codes + random recall vectors (no learned structure). The null bar.
  NATIVE_SCRAMBLE       : NATIVE_ANCHOR with SUPPORT relation ids SCRAMBLED (R[perm[r_i]]) -> same anchors, same
                          degrees, broken relational signal. MUST-FAIL: isolates whether the RELATION operators carry
                          the signal vs an anchor-identity/degree confound.
  IDENTITY_SHUFFLE      : E_derived computed correctly then ASSIGNED to the WRONG held-out entity. MUST-FAIL: isolates
                          whether the composed code is specifically predictive of ITS entity's query edges (breaks the
                          entity-identity binding while preserving the marginal distribution of composed codes).
  ORACLE_FOLDIN         : store with the held-out edges FOLDED INTO the Hebbian W (held-out codes now recalled via
                          their FIXED row) -> positive control / arena-answerable ceiling. If it fires, a null in
                          NATIVE_ANCHOR is interpretable (the native bind cannot induce), not a broken harness.
  BASELINE_POP          : frequency incumbent (held-out tails have train freq 0 -> ~floor; fit-independence sanity).

CEILING-AWARE, DEGREE-UNBIASED EVAL (mirrors the additive arena VERBATIM for direct comparability). Primary metric =
FILTERED MRR rank-vs-ALL-N (KGE standard; NO sampled-negative pool -> no popularity/degree bias). Full filtered rank
spectrum hits@{1,3,10,100}+MRR reported per arm. The held-out-ENTITY arena has an INFO-CEILING (even the ORACLE tops
out low because a held-out entity is constrained only by its OWN sparse edges); bands are set as FRACTIONS of the
in-run MEASURED oracle headroom H = ORACLE_mrr - RANDOM_mrr so ONE FULL computes the ceiling AND scores against it.

PRE-REG BANDS (picked BEFORE the run; primary = FILTERED MRR; H = MEASURED oracle headroom; degree-stratified):
  ORACLE-FIRES (arena answerable) : ORACLE_mrr >= 3x RANDOM_mrr (scale-free) AND ORACLE_mrr - RANDOM_mrr >= 0.003.
  HARD-PASS : (NATIVE_ANCHOR - RANDOM)_mrr >= max(0.50*H, 0.002) AND (NATIVE_ANCHOR - MEMORIZE)_mrr >= 0.10*H AND
              ORACLE fires AND scramble controlled ((SCRAMBLE - RANDOM)_mrr <= 0.25*H) AND identity-shuffle
              controlled ((IDSHUF - RANDOM)_mrr <= 0.25*H) AND not broken AND the margin holds on the low+mid
              degree stratum (not super-hub-confined) => the substrate NATIVELY does inductive generalization.
  MIDDLE    : 0.20*H <= (NATIVE_ANCHOR - RANDOM)_mrr and not HARD-PASS -> stratify by anchor-support degree.
  HARD-FAIL : (NATIVE_ANCHOR - RANDOM)_mrr < 0.20*H with ORACLE firing => native multiplicative bind does NOT
              support the compose pattern; the additive construction is essential (adjunct bridge needed).
  Gated INCONCLUSIVE if ORACLE does not fire (arena not answerable), too few held-out queries, or a null beats POP
  by a ceiling-relative margin (broken).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : ORACLE_FOLDIN recovers planted held-out tails and clears RANDOM by the ceiling-aware
                                (ratio + abs) fire gate on MRR.
  (2) metric_moves            : held-out MRR MOVES across [RANDOM, MEMORIZE, NATIVE_ANCHOR, ORACLE].
  (3) negative_control_margin : RANDOM + NATIVE_SCRAMBLE + IDENTITY_SHUFFLE sit below NATIVE_ANCHOR by an MRR margin,
                                deterministically (>=3 controls).
  (4) full_gates_exercised    : aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate.

## Compute architecture
class (c) MIXED: split + support/query partition + POP = sequential-CPU graph ops (no matmul). The native store is
ONE-SHOT Hebbian (NO SGD, NO epochs) so the whole cell is CHEAP CPU: ingest = chunked Hebbian matmul (KGStore.
ingest_triples); native compose = a single batched (S,n_dim)@(n_dim,n_dim) recall + vectorized index_add bundle +
sign; readouts = query-chunked batched matmul (recall @ E_patched.T; the (nq,N) map is chunked, never materialized
whole across arms). NATIVE_ANCHOR/MEMORIZE/SCRAMBLE/IDSHUF SHARE one train-W recall (computed once). No gradient
training at all -> routed to remote_cpu_queue (device=cpu). GPU would run but is unnecessary (one-shot, small
matmuls); wall estimate < ~20min FULL. Storage: the store's native Hebbian W (a proven CERT-584/585 primitive,
untouched); the ONLY new bundle is the per-ENTITY majority-sign superposition of the entity's own support-edge
recall vectors -- read-only, additive to the store, no mutation of E/R/W.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 7 arms produce >=5 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: raw hits@10-vs-all-N has a CEILING; FIX = primary metric FILTERED MRR + ceiling-RELATIVE
#   bands (fractions of the MEASURED oracle headroom H) -> discriminator_reachability OK by construction (bands
#   scale to whatever H the FULL measures).
# - baseline_in_band: ORACLE must fire (>=3x RANDOM_mrr AND headroom>=0.003); RANDOM/POP near the 1/N floor.
# - discriminator survives scale: analytical (a fixed-random-atom entity code is a random LABEL, not a
#   structure-derived position, so the native memorize null persists at ANY N) + self-test fires the
#   NATIVE_ANCHOR-beats-RANDOM + scramble/identity-shuffle-fail discriminators deterministically on a planted
#   group-structured arena where the store's own recall IS relationally consistent.
# - HARD-PASS strictly above floor: 0.50*H clears HARD-FAIL 0.20*H by 30% of H + a MIN_SIG_MRR abs floor + form-margin.
# - HP_SCOPE: the inductive HARD-PASS gates apply to NATIVE_ANCHOR_COMPOSE only. ORACLE = positive control (must fire);
#   RANDOM/NATIVE_SCRAMBLE/IDENTITY_SHUFFLE = must-not-clear-bar controls; MEMORIZE = native memorize head-to-head;
#   POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 7 arms + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- HELDOUT_ENTITY_FRAC/SUPPORT_FRAC/ORACLE_FIRE_RATIO/
#   ORACLE_FIRE_ABS/HP_CEIL_FRAC pre-registered, NOT tuned on real data; NATIVE_ANCHOR bands are FRACTIONS OF THE
#   MEASURED oracle headroom (computed in-run).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
    stratify_by_tail_degree, PRIMARY_K,
)
from hdlab.kg_traversal import KGStore  # noqa: E402  (the LIVE store; used read-only for its native bind + Hebbian)

ANCHOR_NAME = "native_bind_compose_inductive_entity_cskg_v1"

# ---- Arm names ----
NATIVE = "NATIVE_ANCHOR_COMPOSE"   # mechanism: majority-sign bundle of native Hebbian tail-recall vectors
MEMORIZE = "MEMORIZE_FIXEDCODE"    # native memorize control (held-out code = fixed random bipolar row)
RANDOM = "RANDOM_CODES"            # null (the bar: clear this by the ceiling-relative margin)
SCRAMBLE = "NATIVE_SCRAMBLE"       # must-fail: bundle with support relation ids scrambled (relation-signal control)
IDSHUF = "IDENTITY_SHUFFLE"        # must-fail: composed codes assigned to the wrong held-out entity (identity control)
ORACLE = "ORACLE_FOLDIN"           # positive control: held-out edges folded into W (fixed codes now recalled)
POP = "BASELINE_POP"               # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [NATIVE, MEMORIZE, RANDOM, SCRAMBLE, IDSHUF, ORACLE]   # scored via the native bilinear readout
ALL_ARMS = GEOM_ARMS + [POP]

# ---- CEILING-AWARE, DEGREE-UNBIASED evaluation (identical knobs to the additive arena for direct comparability) ----
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003
HP_CEIL_FRAC = 0.50
FORM_CEIL_FRAC = 0.10
HF_CEIL_FRAC = 0.20
SCRAMBLE_CEIL_FRAC = 0.25       # applies to BOTH the relation-scramble and the identity-shuffle must-fail controls
MIN_SIG_MRR = 0.002
CONTROL_LOSE_EPS = 0.005
MIN_HELDOUT = 20
MIN_STRAT_Q = 8
PRIMARY_METRIC = "hits@%d" % PRIMARY_K

# ---- Held-out-entity split knobs (pre-registered; IDENTICAL to the additive arena; NOT tuned on real data) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- self-test planted thresholds on the PRIMARY metric (MRR); calibrated on the synthetic native-consistent grid,
#      NOT real data. The planted arena is group-structured so the store's OWN Hebbian recall is relationally
#      consistent -> native compose CAN recover a planted held-out entity and the scramble/identity controls collapse.
SELFTEST_ORACLE_MRR_MIN = 0.20
SELFTEST_NATIVE_MRR_MIN = 0.10
SELFTEST_NATIVE_BEATS_RANDOM_MRR = 0.05
SELFTEST_SCRAMBLE_MARGIN_MRR = 0.03   # (NATIVE - SCRAMBLE)_mrr >= this
SELFTEST_IDSHUF_MARGIN_MRR = 0.03     # (NATIVE - IDSHUF)_mrr >= this
SELFTEST_MIN_HO = 8

# ---- hardest relation tertile (weak-point-localization target; CITED@data/exp_cskg_graph_structure_diagnostic_v1) ----
HARDEST_TERTILE_RELS = frozenset([
    "hascontext", "antonym", "mayhaveproperty", "locatednear", "xattr", "haslexicalunit", "hassubevent",
    "motivatedbygoal", "desires", "synonym", "usedfor", "similarto", "hasprerequisite", "xwant",
])

SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3"), (4, 7, "d4_7"), (8, 10 ** 9, "d8plus")]

SCORE_CHUNK = 512

# Config profiles. SELFTEST/FULL exercise the SAME split->ingest->compose->score->verdict path.
SELFTEST_CFG = dict(n_dim=256, heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0,
                    min_heldout=SELFTEST_MIN_HO)
# FULL: n_dim=1024 = the store's default + CERT-584/585 chain-grade regime. CSKG core k_core=12 (N~25.7k), the SAME
# held-out-entity split (frac=0.15, support_frac=0.5), n_heldout_eval=3000, seeds=[7,13,17] as the additive arena.
FULL_CFG = dict(n_dim=1024, heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Held-out-ENTITY split WITH a per-entity SUPPORT / QUERY partition.
# COPIED VERBATIM from experiments.exp_anchor_compose_inductive_entity_cskg_v1.build_heldout_entity_split_ac so the
# native-bind result is scored on a BIT-IDENTICAL split (given the same seed + ent2i + fracs) as the additive
# CHAIN_GRADE, hence directly comparable. Self-contained (numpy + defaultdict only; no SGD dependency).
# ---------------------------------------------------------------------------

def build_heldout_entity_split_ac(pool_lbl, ent2i, frac, support_frac, seed):
    n_ent = len(ent2i)
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(frac * n_ent))
    hold_ids = set(int(x) for x in rng.choice(n_ent, size=n_hold, replace=False))
    train_lbl = []
    held_by_tail = defaultdict(list)
    for (h, r, t) in pool_lbl:
        hi = ent2i[h]; ti = ent2i[t]
        h_hold = hi in hold_ids; t_hold = ti in hold_ids
        if not h_hold and not t_hold:
            train_lbl.append((h, r, t))
        elif t_hold and not h_hold:
            held_by_tail[ti].append((h, r, t))
    support_lbl, query_lbl = [], []
    n_cold = 0
    rng2 = np.random.default_rng(seed * 991 + 5)
    for ti in sorted(held_by_tail.keys()):
        edges = held_by_tail[ti]
        d = len(edges)
        if d == 1:
            query_lbl.append(edges[0]); n_cold += 1
            continue
        order = rng2.permutation(d)
        n_sup = max(1, int(round(support_frac * d)))
        n_sup = min(n_sup, d - 1)
        sup_idx = set(int(x) for x in order[:n_sup].tolist())
        for j, e in enumerate(edges):
            (support_lbl if j in sup_idx else query_lbl).append(e)
    return train_lbl, support_lbl, query_lbl, hold_ids, n_cold


# ---------------------------------------------------------------------------
# Planted GROUP-STRUCTURED arena where the store's OWN Hebbian recall is relationally CONSISTENT so native compose
# CAN recover a held-out entity, and scramble/identity controls collapse. Each group has its own disjoint relation
# set + a dedicated seen "anchor tail" A_g reinforced (anchor_repeat) from every (member, group-relation) pair, so
# W@key(member, group-rel) is DOMINATED by E[A_g]. A held-out member m's support/query edges (member, group-rel, m)
# then all recall ~E[A_g] -> E_derived[m] = sign(sum) = E[A_g] -> m ranks in its group cluster. Scrambling a support
# relation to a FOREIGN group's relation makes key(member, foreign-rel) recall ~0 (that head has no train edge with
# a foreign relation) -> compose fails. Identity-shuffle assigns E[A_g] to a member of a DIFFERENT group -> fails.
# The RELATION operator is thus NECESSARY, so the must-fail controls genuinely fail. Deterministic (default_rng).
# Anchor edges are intentionally DUPLICATED (repeat) to dominate W; member-probe edges are order-preserving-deduped.
# ---------------------------------------------------------------------------

def build_planted_native_arena(seed, n_groups=8, members_per_group=12, rels_per_group=3, anchor_repeat=6,
                               member_edges=4):
    rng = np.random.default_rng(seed * 100019 + 3)
    ent = 0
    ridx = 0
    groups = []
    ganchor = []
    grels = []
    for g in range(n_groups):
        members = list(range(ent, ent + members_per_group)); ent += members_per_group
        anchor = ent; ent += 1
        groups.append(members); ganchor.append(anchor)
        gr = list(range(ridx, ridx + rels_per_group)); ridx += rels_per_group
        grels.append(gr)
    anchor_edges = []      # DUPLICATED on purpose (reinforce E[A_g] in W); NOT deduped
    member_edges_l = []    # deduped (order-preserving)
    for g in range(n_groups):
        M = groups[g]; RG = grels[g]; A = ganchor[g]
        for a in M:
            for r in RG:
                for _ in range(anchor_repeat):
                    anchor_edges.append(("e%d" % a, "r%d" % r, "e%d" % A))
        for m in M:
            others = [x for x in M if x != m]
            for _ in range(member_edges):
                a = int(rng.choice(others))
                r = int(rng.choice(RG))
                member_edges_l.append(("e%d" % a, "r%d" % r, "e%d" % m))
    member_edges_l = list(dict.fromkeys(member_edges_l))
    return anchor_edges + member_edges_l


# ---------------------------------------------------------------------------
# Native store construction + native compose + native readout (the NEW read path; KGStore itself is not modified).
# ---------------------------------------------------------------------------

def build_store(N, n_rel, n_dim, seed, train_int, fold_in=None):
    """A KGStore with FIXED bipolar E/R (generator seeded per (seed, n_dim)) + one-shot Hebbian W over train (+fold_in).
    Two stores built with the SAME (seed, n_dim) share BIT-IDENTICAL E/R -> candidate codes are comparable across
    the train-W store and the ORACLE fold-in store; only W differs."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + n_dim + 1)
    store = KGStore(n_ent=N, n_rel=n_rel, n_dim=n_dim, generator=g)
    tri = torch.from_numpy(train_int).long()
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = torch.cat([tri, torch.from_numpy(fold_in).long()], dim=0)
    store.ingest_triples(tri)
    return store


def native_query_recall(store, query_int, chunk=SCORE_CHUNK):
    """recall[i] = W @ key(h_q, r_q) = the store's native Hebbian tail-estimate for query edge i. Shape [nq, n_dim]."""
    hq = torch.from_numpy(query_int[:, 0]).long()
    rq = torch.from_numpy(query_int[:, 1]).long()
    E = store.E; R = store.R; W = store.W; sq = store.sq
    nq = query_int.shape[0]
    out = torch.empty(nq, store.n_dim, dtype=torch.float32)
    for b in range(0, nq, chunk):
        Q = (E[hq[b:b + chunk]] * R[rq[b:b + chunk]] * sq)      # [c, n_dim] native multiplicative bind
        out[b:b + chunk] = Q @ W.T                              # native bilinear recall (E-space)
    return out


def native_compose_codes(store, support_int, N, rel_perm=None):
    """E_derived[t] = sign(sum over t's support edges of W@key(h_i, r_i)) -- majority-sign bundle of the store's OWN
    Hebbian tail-recall vectors -> bipolar (same format/norm as E), degree-invariant magnitude. Returns a patched
    codebook (held-out rows with support replaced) + per-entity support degree. rel_perm scrambles support relations."""
    E = store.E; R = store.R; W = store.W; sq = store.sq
    Ep = E.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Ep, support_deg
    h = torch.from_numpy(support_int[:, 0]).long()
    r_np = support_int[:, 1].copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]
    r = torch.from_numpy(r_np).long()
    t = torch.from_numpy(support_int[:, 2]).long()
    Ks = (E[h] * R[r] * sq)                                     # [S, n_dim] native bind of each support edge
    recall = Ks @ W.T                                          # [S, n_dim] native Hebbian tail-recall
    acc = torch.zeros(N, store.n_dim, dtype=torch.float32)
    acc.index_add_(0, t, recall)                               # superpose per held-out tail
    cnt = torch.zeros(N, dtype=torch.float32)
    cnt.index_add_(0, t, torch.ones(t.shape[0], dtype=torch.float32))
    mask = cnt > 0
    comp = torch.sign(acc[mask])                              # majority-sign -> bipolar bundle
    comp[comp == 0] = 1.0                                      # deterministic tie-break
    Ep[mask] = comp
    support_deg = cnt.numpy().astype(np.int64)
    return Ep, support_deg


def identity_shuffle_codes(E, Ep_anchor, support_deg, hold_ids, seed):
    """Assign each composed held-out code to a DIFFERENT held-out entity (breaks entity-identity binding)."""
    Ep = E.clone()
    ids = [t for t in range(E.shape[0]) if support_deg[t] > 0 and t in hold_ids]
    if len(ids) <= 1:
        return Ep
    rng = np.random.default_rng(seed * 7919 + 1)
    perm = rng.permutation(len(ids))
    if np.all(perm == np.arange(len(ids))):
        perm = np.roll(perm, 1)
    for j, t in enumerate(ids):
        Ep[t] = Ep_anchor[ids[int(perm[j])]]
    return Ep


def score_from_codes(recall, Ep, chunk=SCORE_CHUNK):
    """scores[i] = Ep @ recall[i] = the store's native readout with a patched candidate codebook. Shape [nq, N]."""
    nq = recall.shape[0]
    N = Ep.shape[0]
    out = torch.empty(nq, N, dtype=torch.float32)
    EpT = Ep.T.contiguous()
    for b in range(0, nq, chunk):
        out[b:b + chunk] = recall[b:b + chunk] @ EpT
    return out


def random_scores(N, query_int, n_dim, seed):
    """Random bipolar candidate codes + random recall vectors -> genuine chance ranking (the null bar)."""
    nq = query_int.shape[0]
    g = torch.Generator(device="cpu").manual_seed(seed * 555 + 13)
    Er = (torch.randint(0, 2, (N, n_dim), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    qr = torch.randn(nq, n_dim, generator=g, dtype=torch.float32)
    return score_from_codes(qr, Er)


# ---------------------------------------------------------------------------
# Fit the arms + score PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def fit_and_score(train_int, support_int, query_int, hold_all, hold_ids, N, n_rel, cfg, seed,
                  rel_tail_freq, all_true):
    n_dim = cfg["n_dim"]
    store = build_store(N, n_rel, n_dim, seed, train_int)                      # train-only Hebbian W
    store_oracle = build_store(N, n_rel, n_dim, seed, train_int, fold_in=hold_all)   # held-out folded in (same E/R)

    Ep_anchor, support_deg = native_compose_codes(store, support_int, N)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Ep_scramble, _ = native_compose_codes(store, support_int, N, rel_perm=rel_perm)
    Ep_idshuf = identity_shuffle_codes(store.E, Ep_anchor, support_deg, hold_ids, seed)

    recall_train = native_query_recall(store, query_int)                      # shared by NATIVE/MEMORIZE/SCRAMBLE/IDSHUF
    recall_oracle = native_query_recall(store_oracle, query_int)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (NATIVE, score_from_codes(recall_train, Ep_anchor)),
        (MEMORIZE, score_from_codes(recall_train, store.E)),                  # held-out codes = fixed bipolar rows
        (SCRAMBLE, score_from_codes(recall_train, Ep_scramble)),
        (IDSHUF, score_from_codes(recall_train, Ep_idshuf)),
        (ORACLE, score_from_codes(recall_oracle, store_oracle.E)),           # fixed codes, fold-in W recalls them
        (RANDOM, random_scores(N, query_int, n_dim, seed)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg)


# ---------------------------------------------------------------------------
# Weak-point localization: per anchor-support-degree bin, per global-degree tertile, per relation-tertile.
# ---------------------------------------------------------------------------

def _hits_subset(scores, query_int, all_true, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub = filtered_hits_from_scores(scores[idx], query_int[idx], all_true, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


def _pop_subset(rel_tail_freq, query_int, all_true, n_ent, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub, _ = pop_hits(rel_tail_freq, query_int[idx], all_true, n_ent, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


def localize_weak_points(arm_scores, query_int, all_true, support_deg, node_degree, rel_i2lbl, rel_tail_freq, N):
    nq = query_int.shape[0]
    gold = query_int[:, 2]
    q_support = np.array([support_deg[int(g)] for g in gold], dtype=np.int64)
    strat, tert = stratify_by_tail_degree(query_int, node_degree)
    q_hardest = np.array([rel_i2lbl.get(int(query_int[i, 1]), "") in HARDEST_TERTILE_RELS for i in range(nq)],
                         dtype=bool)
    report_arms = [NATIVE, MEMORIZE, RANDOM, ORACLE]

    def _by_mask(mask):
        out = {a: _hits_subset(arm_scores[a], query_int, all_true, mask) for a in report_arms}
        out[POP] = _pop_subset(rel_tail_freq, query_int, all_true, N, mask)
        return out

    by_support = {}
    for lo, hi, name in SUPPORT_BINS:
        by_support[name] = _by_mask((q_support >= lo) & (q_support <= hi))
    by_gdeg_tertile = {nm: _by_mask(strat == si) for si, nm in enumerate(["low", "mid", "high"])}
    fair_lowmid = _by_mask((strat == 0) | (strat == 1))
    by_reltertile = dict(hardest=_by_mask(q_hardest), rest=_by_mask(~q_hardest))
    return dict(by_support_degree=by_support, by_global_degree_tertile=by_gdeg_tertile,
                fair_low_mid=fair_lowmid, by_relation_tertile=by_reltertile,
                global_degree_tertile_bounds=tert,
                support_deg_hist={name: int(((q_support >= lo) & (q_support <= hi)).sum())
                                  for lo, hi, name in SUPPORT_BINS})


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, seed, corpus_name, localize=True):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)

    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]

    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    hold_all = np.concatenate([support_int, query_int], axis=0) if query_int.shape[0] else support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  n_dim=int(cfg["n_dim"]),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, support_int, query_int, hold_all, hold_ids, N, n_rel, cfg, seed,
                       gd.rel_tail_freq, all_true)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    if localize:
        result["localization"] = localize_weak_points(
            fs["arm_scores"], query_int, all_true, fs["support_deg"], gd.node_degree, rel_i2lbl,
            gd.rel_tail_freq, N)
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (per_seed list length 1..3).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _h10(ps, arm):
    return ps["arm_hits"][arm].get(PRIMARY_METRIC, float("nan"))


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _fair_lowmid_mrr(ps, arm):
    loc = ps.get("localization", {})
    cell = loc.get("fair_low_mid", {}).get(arm, {})
    if cell.get("n", 0) >= MIN_STRAT_Q:
        return cell.get("mrr", float("nan"))
    return float("nan")


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def aggregate_and_verdict(per_seed):
    def agg_m(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    def agg_h10(arm):
        return _nm([_h10(ps, arm) for ps in per_seed])

    def agg_fair(arm):
        return _nm([_fair_lowmid_mrr(ps, arm) for ps in per_seed])

    m = {a: agg_m(a) for a in ALL_ARMS}
    h10 = {a: agg_h10(a) for a in ALL_ARMS}
    mf = {a: agg_fair(a) for a in [NATIVE, MEMORIZE, RANDOM, ORACLE, POP]}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    d_native = _sub(m[NATIVE], m[RANDOM])
    form_margin = _sub(m[NATIVE], m[MEMORIZE])          # native compose beats the native fixed-code memorize control
    d_scramble = _sub(m[SCRAMBLE], m[RANDOM])
    d_idshuf = _sub(m[IDSHUF], m[RANDOM])
    oracle_headroom = _sub(m[ORACLE], m[RANDOM])
    fair_native_margin = _sub(mf[NATIVE], mf[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)

    H = oracle_headroom
    hp_native_target = (max(HP_CEIL_FRAC * H, MIN_SIG_MRR) if H == H else float("nan"))
    hp_form_target = (FORM_CEIL_FRAC * H if H == H else float("nan"))
    hf_native_target = (HF_CEIL_FRAC * H if H == H else float("nan"))
    control_target = (SCRAMBLE_CEIL_FRAC * H if H == H else float("nan"))

    scramble_controlled = bool(d_scramble == d_scramble and control_target == control_target
                               and d_scramble <= control_target)
    idshuf_controlled = bool(d_idshuf == d_idshuf and control_target == control_target
                             and d_idshuf <= control_target)
    broken_margin = (max(CONTROL_LOSE_EPS, SCRAMBLE_CEIL_FRAC * H) if H == H else CONTROL_LOSE_EPS)
    broken = bool((m[RANDOM] == m[RANDOM] and m[POP] == m[POP] and (m[RANDOM] - m[POP]) > broken_margin))
    fair_holds = bool(fair_native_margin == fair_native_margin and fair_native_margin > 0.0)

    hard_pass = bool(d_native == d_native and hp_native_target == hp_native_target and d_native >= hp_native_target
                     and form_margin == form_margin and hp_form_target == hp_form_target
                     and form_margin >= hp_form_target
                     and oracle_fires and scramble_controlled and idshuf_controlled and not broken and fair_holds)
    hard_fail = bool(d_native == d_native and hf_native_target == hf_native_target and d_native < hf_native_target)
    middle = bool(d_native == d_native and not hard_pass and not hard_fail)

    oracle_fire_by_metric = {}
    for mk in metric_keys:
        ov = spectrum[ORACLE][mk]; rv = spectrum[RANDOM][mk]
        hh = _sub(ov, rv); rr = _ratio(ov, rv)
        oracle_fire_by_metric[mk] = dict(
            oracle=(round(ov, 6) if ov == ov else None), random=(round(rv, 6) if rv == rv else None),
            headroom=(round(hh, 6) if hh == hh else None),
            ratio=(round(rr, 2) if (rr == rr and rr != float("inf")) else None),
            fires_ratio=bool(rr == rr and rr >= ORACLE_FIRE_RATIO and hh == hh and hh > 0))

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif hard_pass:
        verdict = "HARD_PASS_NATIVE_BIND_INDUCTIVE"
    elif hard_fail:
        verdict = "HARD_FAIL_NATIVE_BIND_NO_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_NATIVE_TRANSFER"

    verdict_msg = (
        "%s || HELD-OUT MRR [nq=%d n_dim=%s]: NATIVE=%s | MEMORIZE=%s | RANDOM=%s SCRAMBLE=%s IDSHUF=%s | ORACLE=%s "
        "POP=%s || CEILING H(oracle-random)=%s ratio=%sx (fires>=%.1fx&>=%.3f=%s) | native_margin=%s vs "
        "HARD_PASS>=%s (=%.2f*H|min%.3f) HARD_FAIL<%s (=%.2f*H) | form_margin=%s (>=%s) | fair_lowmid_margin=%s (>0) "
        "| scramble_margin=%s idshuf_margin=%s (<=%s) | broken=%s | frac=%.2f support_frac=%.2f seeds=%d"
        % (
            verdict, n_query, str(per_seed[0].get("n_dim")), _fmt(m[NATIVE]), _fmt(m[MEMORIZE]), _fmt(m[RANDOM]),
            _fmt(m[SCRAMBLE]), _fmt(m[IDSHUF]), _fmt(m[ORACLE]), _fmt(m[POP]), _fmt(H),
            (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS,
            oracle_fires, _fmt(d_native), _fmt(hp_native_target), HP_CEIL_FRAC, MIN_SIG_MRR, _fmt(hf_native_target),
            HF_CEIL_FRAC, _fmt(form_margin), _fmt(hp_form_target), _fmt(fair_native_margin), _fmt(d_scramble),
            _fmt(d_idshuf), _fmt(control_target), broken,
            _nm([ps["heldout_entity_frac"] for ps in per_seed]),
            _nm([ps["support_frac"] for ps in per_seed]), len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict,
        ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        heldout_hits_at_10={a: _rnd(h10[a], 5) for a in ALL_ARMS},
        fair_lowmid_mrr={a: _rnd(mf[a]) for a in [NATIVE, MEMORIZE, RANDOM, ORACLE, POP]},
        primary_k=PRIMARY_K,
        native_margin_vs_random=_rnd(d_native),
        form_margin_vs_memorize=_rnd(form_margin),
        fair_lowmid_native_margin=_rnd(fair_native_margin),
        scramble_margin_vs_random=_rnd(d_scramble),
        idshuf_margin_vs_random=_rnd(d_idshuf),
        oracle_headroom=_rnd(H),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_fire_by_metric=oracle_fire_by_metric,
        resolved_thresholds=dict(hard_pass_native=_rnd(hp_native_target), hard_pass_form=_rnd(hp_form_target),
                                 hard_fail_native=_rnd(hf_native_target), control_ceiling=_rnd(control_target),
                                 broken_margin=_rnd(broken_margin)),
        n_query_scored=n_query,
        bands=dict(CEIL_METRIC=CEIL_METRIC, ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   HP_CEIL_FRAC=HP_CEIL_FRAC, FORM_CEIL_FRAC=FORM_CEIL_FRAC, HF_CEIL_FRAC=HF_CEIL_FRAC,
                   SCRAMBLE_CEIL_FRAC=SCRAMBLE_CEIL_FRAC, MIN_SIG_MRR=MIN_SIG_MRR, MIN_HELDOUT=MIN_HELDOUT,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, scramble_controlled=scramble_controlled,
        idshuf_controlled=idshuf_controlled, broken=broken, fair_holds=fair_holds,
        hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test (planted group-structured native-consistent arena; adversarial positive control).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    pool = build_planted_native_arena(7)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, 7, "PLANTED_NATIVE_HELDOUT_ENTITY", localize=True)
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"),
               n_dim=res.get("n_dim"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    h10 = {a: ah[a].get(PRIMARY_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    native_margin = m[NATIVE] - m[RANDOM]
    scramble_margin = m[NATIVE] - m[SCRAMBLE]
    idshuf_margin = m[NATIVE] - m[IDSHUF]
    oracle_margin = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    native_recovers = bool(m[NATIVE] == m[NATIVE] and m[NATIVE] >= SELFTEST_NATIVE_MRR_MIN)
    native_beats_random = bool(native_margin == native_margin and native_margin >= SELFTEST_NATIVE_BEATS_RANDOM_MRR)
    scramble_fails = bool(scramble_margin == scramble_margin and scramble_margin >= SELFTEST_SCRAMBLE_MARGIN_MRR)
    idshuf_fails = bool(idshuf_margin == idshuf_margin and idshuf_margin >= SELFTEST_IDSHUF_MARGIN_MRR)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + CONTROL_LOSE_EPS)
    arms_differ = bool(n_sigs >= 5)

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    oracle_fire_by_metric = {}
    for mk in metric_keys:
        ov = ah[ORACLE].get(mk, float("nan")); rv = ah[RANDOM].get(mk, float("nan"))
        hh = (ov - rv) if (ov == ov and rv == rv) else float("nan")
        rr = _ratio(ov, rv)
        oracle_fire_by_metric[mk] = dict(
            oracle=(round(ov, 5) if ov == ov else None), random=(round(rv, 5) if rv == rv else None),
            headroom=(round(hh, 5) if hh == hh else None),
            fires_ratio=bool(rr == rr and rr >= ORACLE_FIRE_RATIO and hh == hh and hh > 0))

    # VACUOUS-SMOKE guard: the RANDOM null must NOT reach NATIVE_ANCHOR on the planted held-out arena.
    random_reached_native = bool(native_margin <= SELFTEST_NATIVE_BEATS_RANDOM_MRR)
    assert_discriminator_fires(random_reached_native, control_name=RANDOM,
                               headline_name="native_bind_compose_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached NATIVE_ANCHOR_COMPOSE on the planted held-out-entity arena -> "
                                     "arena not answerable / metric frozen")

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_FOLDIN", "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted arena: ORACLE (held-out edges folded into Hebbian W) recovers held-out tails via their "
                  "fixed codes and clears RANDOM by the ceiling-aware ratio+abs fire gate -> the arena is answerable "
                  "by the native store and the ceiling-relative inductive bar is achievable when the code is recalled"},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [m[RANDOM], m[MEMORIZE], m[NATIVE], m[ORACLE]],
         "extra": "MRR RANDOM=%.3f MEMORIZE=%.3f NATIVE=%.3f ORACLE=%.3f: the native readout responds to "
                  "composed/recalled codes" % (m[RANDOM], m[MEMORIZE], m[NATIVE], m[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SCRAMBLE], m[IDSHUF]],
         "headline_threshold": m[NATIVE], "higher_is_pass": True, "margin": SELFTEST_SCRAMBLE_MARGIN_MRR,
         "n_repeats_min": 3, "control_name": "RANDOM_SCRAMBLE_IDSHUF_below_native_mrr",
         "extra": "RANDOM + relation-scrambled + identity-shuffled compose must sit below NATIVE_ANCHOR by the MRR "
                  "margin on held-out queries -> the RELATION operators AND the entity-identity binding carry the "
                  "signal, not anchor identity/degree"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "idshuf_controlled",
                                    "broken_test_guard", "enough_heldout", "ceiling_relative_band_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "idshuf_controlled",
                             "broken_test_guard", "enough_heldout", "ceiling_relative_band_gate"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        heldout_hits_at_10={a: round(h10[a], 5) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: round(ah[a].get(mk, float("nan")), 5) for mk in metric_keys}
                                 for a in ALL_ARMS},
        oracle_fire_by_metric=oracle_fire_by_metric,
        n_distinct_sigs=n_sigs, native_margin=round(native_margin, 5), scramble_margin=round(scramble_margin, 5),
        idshuf_margin=round(idshuf_margin, 5), oracle_margin=round(oracle_margin, 5),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, native_recovers=native_recovers,
        native_beats_random=native_beats_random, scramble_fails=scramble_fails, idshuf_fails=idshuf_fails,
        pop_at_floor=pop_at_floor, arms_differ=arms_differ, selftest_verdict=st_verdict,
        validity_preflight_ok=bool(vp_ok),
        support_deg_hist=res.get("localization", {}).get("support_deg_hist"),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(oracle_recovers and oracle_fires and native_recovers and native_beats_random
              and scramble_fails and idshuf_fails and pop_at_floor and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    # This cell is CPU-only by design (one-shot Hebbian, small matmuls). Kept for interface parity; always CPU.
    return torch.device("cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=cpu run_mode=%s seeds=%s n_dim=%s" % (run_mode, seeds, cfg["n_dim"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s native_margin=%s scramble_margin=%s idshuf_margin=%s oracle_fires=%s vp_ok=%s" %
         (st_ok, st_res.get("native_margin"), st_res.get("scramble_margin"), st_res.get("idshuf_margin"),
          st_res.get("oracle_fires"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (NATIVE_ANCHOR did not recover/beat-random, or scramble/identity-"
                        "shuffle did not fail, or ORACLE did not fire, or POP not at floor, or arms not distinct): %s"
                        % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS NATIVE_BIND_COMPOSE inductive probe: majority-sign bundle of native Hebbian "
                        "tail-recall vectors recovers planted held-out tails and clears RANDOM; relation-scramble AND "
                        "identity-shuffle fail; ORACLE fires; POP at floor; 4 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool)))
            res = run_corpus(pool, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY", localize=True)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d | MRR NATIVE=%s MEMORIZE=%s RANDOM=%s SCRAMBLE=%s IDSHUF=%s "
                 "ORACLE=%s POP=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"], res["n_cold"],
                  _fmt(ah[NATIVE][CEIL_METRIC]), _fmt(ah[MEMORIZE][CEIL_METRIC]), _fmt(ah[RANDOM][CEIL_METRIC]),
                  _fmt(ah[SCRAMBLE][CEIL_METRIC]), _fmt(ah[IDSHUF][CEIL_METRIC]), _fmt(ah[ORACLE][CEIL_METRIC]),
                  _fmt(ah[POP][CEIL_METRIC]), time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
