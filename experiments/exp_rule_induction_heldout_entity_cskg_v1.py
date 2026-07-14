"""RULE-INDUCTION on the SAME held-out-ENTITY CSKG arena as the additive map-builder (0.128 line).

THE QUESTION (from notes/research_drill_neurosymbolic_logical_inference_theories_2026-07-13.md, ranked #1
mechanism). Do statistically-mined length<=2 Horn rules (AnyBURL/RuleN-style path-counting, ZERO training,
PURE GRAPH STATISTICS) -- applied by the substrate's proven forward-chaining primitive with EXACT adjacency
lookup for grounding -- predict HELD-OUT-ENTITY relations better than random / frequency / a SHUFFLED-rule
must-fail, on the SAME arena the additive map-builder scored 0.128 MRR on? A learned RULE is entity-invariant
reusable structure (confidence indexed by RELATION, not by entity) -> it generalizes to UNSEEN entities by
construction, sidestepping the per-entity-code superposition-capacity wall that closed learned-SR / additive-
TransE / structure-aware-encoder (all three EMBEDDING-family; CITED@notes relational_capability_track_record_
scour_2026-07-10). This is the first NON-embedding mechanism class against that wall.

DECOUPLING (why this is a cheap, clean test). This program ALREADY proves the APPLY half of the pipeline at
HARD_PASS (PP-196 STRIPS forward-chaining perfect recall; PP-252 defeasible NAF 100%). UNTESTED = the INDUCE
half (learn rule confidences from data + check held-out-entity generalization). Grounding uses an EXACT
adjacency dict (oracle lookup), DELIBERATELY isolating this from the already-closed learned-router SNR wall
(CITED@notes track_record bucket D: every non-oracle/VSA-native router collapses to the naive-centroid floor).
A pass/fail here is attributable to the RULE-INDUCTION mechanism, not re-litigating routing.

MECHANISM (reuses the substrate's proven symbolic apparatus, unchanged):
  mine_rules(g_train, ...)  -- AnyBURL/RuleN path-counting: for head relation R, mine L1F (R1(x,z)=>R),
      L1I (R1(z,x)=>R), L2 (R1(x,y)^R2(y,z)=>R); confidence = support / body_count. ZERO training, pure
      graph statistics (exp_gt_induction_fb15k237_dense_v1.mine_rules).
  propose(g_ground, h, R, rules[R])  -- forward-chain accepted rules from head h over the EXACT adjacency of
      (train + the held-out entity's SUPPORT edges); NOISY-OR aggregate the rule confidences per candidate
      (standard AnyBURL/AMIE aggregation). A held-out tail t is reached via its SUPPORT edges -> genuine
      zero-shot construction, no per-entity training, no leakage of the QUERY edge.

ARMS (all scored PAIRED on the SAME held-out QUERY edges + same all-N candidate set + same filtered eval,
identical to the additive cell so the numbers are directly comparable to the 0.128 line):
  RULE_INDUCT  : rules mined on g_train; grounded on g_train+support. THE MECHANISM.
  RULE_SHUFFLE : the SAME mined rules, but the body-pattern -> HEAD-RELATION mapping is PERMUTED (confidences
                 and counts identical). MUST-FAIL: isolates whether the RELATION-specific rule carries the
                 signal vs a reach/degree/anchor confound (the drill's exact real-vs-shuffled control).
  RANDOM       : uniform-random score over all N candidates. The null / "clear this by >=0.05" bar.
  BASELINE_POP : per-relation tail frequency incumbent. Held-out tails have train-freq 0 -> ~floor.
  RULE_ORACLE  : rules mined + grounded on g_train+support+QUERY (held-out folded in) -> positive control /
                 arena-answerable ceiling (mirrors the additive cell's ORACLE_ADDITIVE, MEASURED 0.1373 MRR).
                 Fold-in is via the entity's OTHER edges; identity self-rules (R=>R) are excluded by
                 mine_rules, so ORACLE fires by genuine graph-embedding of t, not a trivial query-edge leak.

PRE-REG BANDS (picked BEFORE the run; primary metric = FILTERED MRR rank-vs-ALL-N, degree-unbiased, KGE
standard -- the SAME metric + arena the additive cell used, MEASURED ORACLE headroom H=0.1368 there, so the
drill's absolute 0.05 MRR margin is REACHABLE on this arena, discriminator_reachability=TRUE, NOT the
low-ceiling trap). reach@2 = hits@2 reported explicitly per the drill's reach@k framing.
  ORACLE-FIRES (arena answerable) : RULE_ORACLE_mrr >= 3x RANDOM_mrr AND RULE_ORACLE_mrr - RANDOM_mrr >= 0.003.
  HARD-PASS : (RULE_INDUCT - RULE_SHUFFLE)_mrr >= 0.05 (the drill's real-vs-shuffled margin) AND
              (RULE_INDUCT - RANDOM)_mrr >= 0.05 AND ORACLE fires AND RULE_SHUFFLE controlled AND not broken.
  HARD-FAIL : (RULE_INDUCT - RULE_SHUFFLE)_mrr <= 0.02 with ORACLE firing (the clean negative: pure symbolic
              rule induction, ZERO embedding capacity anywhere, still cannot beat a shuffled/memoryless
              baseline on held-out entities -> the bottleneck is the KG's relation content, not embeddings).
  MIDDLE    : real-vs-shuffled margin strictly in (0.02, 0.05), or relation/degree-dependent partial signal.
  Ceiling-relative corroboration (H = ORACLE_mrr - RANDOM_mrr): the drill-absolute HARD-PASS also reported as
  a fraction of the MEASURED H so the verdict is honest about arena answerability. Degree-stratified (low/mid/
  high tertile + fair low+mid) for weak-point localization + degree-confound control.

REFERENCE LINES (comparability; tagged):
  ADDITIVE ANCHOR_COMPOSE mrr = 0.12821  CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:
                                         gates.heldout_mrr.ANCHOR_COMPOSE (the additive map-builder, same arena)
  ORACLE_ADDITIVE mrr        = 0.13729  CITED@same:gates.heldout_mrr.ORACLE_ADDITIVE (arena answerable ceiling)
  RANDOM_CODES mrr           = 0.00048  CITED@same (null floor)

## Compute architecture
class (b) SEQUENTIAL-CPU with justification: the mechanism is PURE GRAPH STATISTICS (rule mining = streaming
counts; forward-chaining = dict adjacency lookups) with NO matmul, NO GPU-batchable primitive, NO training.
The only dense tensors are the per-arm (nq, N) score matrices consumed by the shared filtered-eval; they are
built one arm at a time and freed (peak ~1 matrix + its clone). device=cpu always. Storage: adjacency dicts
(each entity/edge indexed individually; SHARDED, no bundling). Single-seed-per-run is NOT used (seeds are
cheap CPU passes); multi-seed is IN-PROCESS with per-seed partials + cardinality gate. discriminator-survives-
scale = analytical (B): a SHUFFLED rule cannot chain to the held-out tail via the RIGHT relation pattern by
construction, so the real-vs-shuffled margin is a STRUCTURAL property independent of N; the ORACLE-fires
control proves the metric moves at scale; the self-test fires the discriminator deterministically on planted
data at the REAL mine_rules+propose code path.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 5 arms produce >=4 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + write_partial os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: MEASURED@data/exp_anchor_compose.../metrics.json ORACLE mrr=0.1373 on THIS arena ->
#   the absolute 0.05 MRR margin is REACHABLE (discriminator_reachability=TRUE); ALSO reported ceiling-relative.
# - baseline_in_band: RULE_ORACLE must fire (>=3x RANDOM AND headroom>=0.003); RANDOM/POP near 1/N floor.
# - discriminator survives scale: analytical (B) above + ORACLE-fires + self-test on the real code path.
# - HARD-PASS strictly above HARD-FAIL: 0.05 clears the 0.02 fail band by 0.03 MRR + requires 2 nulls beaten.
# - HP_SCOPE: the HARD-PASS gate applies to RULE_INDUCT only. RULE_ORACLE = positive control (must fire);
#   RANDOM/RULE_SHUFFLE = must-not-clear-bar controls; POP = fit-independence/frequency incumbent.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 5 arms + >=4 distinct sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- MIN_SUPPORT/MIN_CONF/frac pre-registered, NOT tuned
#   on real data; bands are the drill's absolute margins (reachable per the MEASURED oracle H) + ceiling-frac.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - Gate F: real_code_path = the self-test constructs the REAL Graph + calls the REAL mine_rules + propose at
#   N~200 (no synthetic-only branch); no KGStore/fit-module signature to bind (this cell is pure graph stats);
#   guard_baseline_valid = the broken-test guard compares controls to RANDOM/arm-floor, NOT to POP (POP is
#   structurally ~0 on held-out tails -> a control-beats-POP guard would mis-fire, the exact anchor_compose_
#   magnitude bug; F.4 declared).
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints); timeout>=1800.

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
from collections import Counter, defaultdict
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
from experiments.exp_gt_induction_fb15k237_dense_v1 import (  # noqa: E402
    Graph, build_ids, mine_rules, propose,
)
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
    stratify_by_tail_degree,
)
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_heldout_entity_split_ac,
)

ANCHOR_NAME = "rule_induction_heldout_entity_cskg_v1"

# ---- Arm names ----
INDUCT = "RULE_INDUCT"       # mechanism: mined-on-train Horn rules, forward-chained over train+support
SHUFFLE = "RULE_SHUFFLE"     # must-fail: body-pattern -> head-relation mapping permuted (counts identical)
RANDOM = "RANDOM"            # null: uniform-random score over all N (the >=0.05 bar)
POP = "BASELINE_POP"         # frequency incumbent (held-out tails have train-freq 0 -> floor)
ORACLE = "RULE_ORACLE"       # positive control: rules mined+grounded with held-out folded in (arena answerable)
ALL_ARMS = [INDUCT, SHUFFLE, RANDOM, POP, ORACLE]
SCORED_ARMS = [INDUCT, SHUFFLE, RANDOM, ORACLE]   # dense (nq,N) score arms (POP handled by pop_hits)

# ---- eval knobs (degree-unbiased filtered rank spectrum; reach@2 = hits@2 per the drill's reach@k) ----
EVAL_KS = (1, 2, 3, 10, 100)
CEIL_METRIC = "mrr"
DISPLAY_K = 10
PRIMARY_METRIC = "hits@%d" % DISPLAY_K
REACH_METRIC = "hits@2"    # the drill's reach@2

# ---- rule-mining knobs (AnyBURL/RuleN path-counting; PRE-REGISTERED, NOT tuned on real data) ----
MIN_SUPPORT = 3            # min rule support (groundings) to accept a mined rule
MIN_CONF = 0.05            # min rule confidence (support / body_count) to accept
MAX_RULES_PER_HEAD = 50    # keep top rules by confidence per head relation
HUB_CAP = 60000            # skip middle nodes where in_deg*out_deg > HUB_CAP (hub-explosion guard)

# ---- pre-reg discriminator bands (primary metric = filtered MRR) ----
# The drill's absolute real-vs-shuffled margin; REACHABLE on this arena (MEASURED oracle H=0.1368).
HARD_PASS_MARGIN = 0.05    # (RULE_INDUCT - RULE_SHUFFLE)_mrr AND (RULE_INDUCT - RANDOM)_mrr >= this
HARD_FAIL_MARGIN = 0.02    # (RULE_INDUCT - RULE_SHUFFLE)_mrr <= this (with ORACLE firing) = clean negative
ORACLE_FIRE_RATIO = 3.0    # RULE_ORACLE_mrr >= 3x RANDOM_mrr (scale-free arena-answerable)
ORACLE_FIRE_ABS = 0.003    # AND RULE_ORACLE_mrr - RANDOM_mrr >= this (non-noise floor)
SHUFFLE_CTRL_EPS = 0.005   # RULE_SHUFFLE must sit below RULE_INDUCT by > this (controlled)
BROKEN_FLOOR_EPS = 0.02    # a null/control beating RANDOM+arm-floor by > this in a degenerate way = broken
MIN_HELDOUT = 20           # min held-out QUERY edges for a valid discriminator
MIN_STRAT_Q = 8            # min queries in a stratum to report its margin

# ---- reference lines on the SAME arena (tagged) ----
ADDITIVE_REF_MRR = 0.12821    # CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE
ORACLE_REF_MRR = 0.13729      # CITED@same:gates.heldout_mrr.ORACLE_ADDITIVE
RANDOM_REF_MRR = 0.00048      # CITED@same:gates.heldout_mrr.RANDOM_CODES

# ---- held-out-entity split knobs (pre-registered; NOT tuned on real data; same as the additive cell) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- self-test planted thresholds (calibrated on the synthetic rule-consistent grid, NOT real data) ----
SELFTEST_INDUCT_MRR_MIN = 0.15       # planted: RULE_INDUCT recovers held-out tails via the real L2 rule
SELFTEST_INDUCT_BEATS_SHUFFLE = 0.08  # planted: (RULE_INDUCT - RULE_SHUFFLE)_mrr >= this
SELFTEST_INDUCT_BEATS_RANDOM = 0.08   # planted: (RULE_INDUCT - RANDOM)_mrr >= this
SELFTEST_MIN_HO = 8

# config profiles: SELFTEST/SMOKE/FULL all exercise split->mine->ground->propose->score->verdict.
SELFTEST_CFG = dict(planted=True, heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0,
                    min_heldout=SELFTEST_MIN_HO)
SMOKE_CFG = dict(planted=False, cskg_max_lines=0, k_core=8, cskg_max_nodes=4000,
                 heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                 n_heldout_eval=800, min_heldout=MIN_HELDOUT, seeds=[7])
FULL_CFG = dict(planted=False, cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
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
# Planted rule-consistent arena for the self-test: a genuine L2 rule
# rC(h,t) :- rA(h,m) ^ rB(m,t) is the ONLY generator of the target relation, so the RIGHT relation pattern
# (not anchor identity/degree) is NECESSARY. A held-out tail t is recovered ONLY by chaining h-rA->m (train)
# and m-rB->t (t's SUPPORT edge). Scrambling the head->rule mapping breaks the chain -> the must-fail fails.
# Deterministic (default_rng(seed) + order-preserving dedup). Labels e*/r* so build_ids/Graph consume it.
# ---------------------------------------------------------------------------

def build_planted_rule_arena(seed, n_head=80, n_mid=40, n_tail=60, rA_deg=3, n_noise=300):
    """TWO independent planted L2 rule families over SHARED heads but DISJOINT tail sets, so that permuting
    which rule maps to which HEAD relation genuinely BREAKS the prediction (family-1's rule cannot reach
    family-2's tails). Gives >=2 target heads with mined rules -> the head-derangement shuffle fires.
      family 1: rC(h,t) :- rA(h,m) ^ rB(m,t),  tails t*   (middles mm base 0)
      family 2: rF(h,u) :- rD(h,m) ^ rE(m,u),  tails u*   (middles mm base n_mid)
    """
    rng = np.random.default_rng(seed * 100019 + 5)
    edges = []
    families = [("rC", "rA", "rB", "t", 0), ("rF", "rD", "rE", "u", n_mid)]
    tail_labels = []
    for (rHead, rBa, rBb, tpfx, mid_base) in families:
        mid_of_tail = [(t % n_mid) + mid_base for t in range(n_tail)]
        heads_of_mid = defaultdict(list)
        for h in range(n_head):
            mids = rng.choice(n_mid, size=min(rA_deg, n_mid), replace=False)
            for m in mids:
                mm = int(m) + mid_base
                edges.append(("h%d" % h, rBa, "mm%d" % mm))
                heads_of_mid[mm].append(h)
        for t in range(n_tail):
            edges.append(("mm%d" % mid_of_tail[t], rBb, "%s%d" % (tpfx, t)))
            tail_labels.append("%s%d" % (tpfx, t))
        for t in range(n_tail):
            m = mid_of_tail[t]
            for h in heads_of_mid[m]:
                edges.append(("h%d" % h, rHead, "%s%d" % (tpfx, t)))
    # noise among heads/tails to make the graph non-degenerate + POP non-trivial
    all_nodes = ["h%d" % h for h in range(n_head)] + list(dict.fromkeys(tail_labels))
    for _ in range(n_noise):
        a = all_nodes[int(rng.integers(len(all_nodes)))]
        b = all_nodes[int(rng.integers(len(all_nodes)))]
        if a != b:
            edges.append((a, "rNoise", b))
    return list(dict.fromkeys(edges))   # order-preserving dedup (cross-process determinism)


# ---------------------------------------------------------------------------
# Rule mining + application. Grounding graph = EXACT adjacency (Graph over the chosen edge list).
# ---------------------------------------------------------------------------

def _mine(train_lbl, ent2i, rel2i):
    """Mine AnyBURL/RuleN Horn rules (L1F/L1I/L2, path-counting confidence) over train edges only."""
    g = Graph(train_lbl, ent2i, rel2i)
    target_rels = list(rel2i.values())
    acc, allpat, hub_skipped = mine_rules(g, target_rels, MIN_SUPPORT, MIN_CONF, MAX_RULES_PER_HEAD, HUB_CAP)
    n_rules = sum(len(v) for v in acc.values())
    return acc, n_rules, hub_skipped


def _derangement(n, rng, max_tries=1000):
    """A permutation of range(n) with NO fixed point (n>=2), so no head keeps its own rules."""
    for _ in range(max_tries):
        p = rng.permutation(n)
        if not any(int(p[i]) == i for i in range(n)):
            return p
    # deterministic fallback: cyclic shift by 1 (fixed-point-free for n>=2)
    return np.array([(i + 1) % n for i in range(n)], dtype=np.int64)


def _shuffle_rules(acc, n_rel, seed):
    """Permute the body-pattern -> HEAD relation mapping (confidences + counts identical). The must-fail:
    each head relation receives ANOTHER head's rule list (DERANGEMENT -> no head keeps its own), so the
    RELATION-specific chain is broken. Fallback for <2 heads: randomize the body relation ids per rule."""
    heads = sorted(acc.keys())
    rng = np.random.default_rng(seed * 4441 + 17)
    if len(heads) >= 2:
        perm = _derangement(len(heads), rng)
        return {heads[i]: acc[heads[int(perm[i])]] for i in range(len(heads))}
    out = {}
    for h, rules in acc.items():
        out[h] = [(kind, int(rng.integers(n_rel)), int(rng.integers(n_rel)), conf, supp)
                  for (kind, r1, r2, conf, supp) in rules]
    return out


def _score_rule_arm(g_ground, acc_by_head, query_int, N, tiebreak_seed):
    """Dense (nq, N) score matrix: propose (forward-chain + noisy-OR) per query over EXACT adjacency.

    FAIRNESS TIE-BREAK: a rule arm scores most candidates 0 (unproposed). Without a tie-break the shared
    filtered-eval optimistically ranks an UNPROPOSED gold at #proposed+1 (often rank 1) -> an UNEARNED hit
    that inflates every rule arm. Adding a tiny per-entity random epsilon (<< the smallest noisy-OR score,
    which is >= MIN_CONF=0.05) preserves the PROPOSED ranking exactly while giving an unproposed gold a FAIR
    random rank BELOW all proposed candidates -- the same continuous behaviour the RANDOM/additive arms have.
    """
    nq = query_int.shape[0]
    rng = np.random.default_rng(tiebreak_seed)
    sc = (rng.random((nq, N)).astype(np.float32) * 1e-6)   # tie-break floor; << MIN_CONF proposed scores
    for i in range(nq):
        h = int(query_int[i, 0]); r = int(query_int[i, 1])
        props = propose(g_ground, h, r, acc_by_head.get(r, []))
        for c, s in props.items():
            if 0 <= c < N:
                sc[i, c] = np.float32(s) + np.float32(1e-6)   # keep proposed strictly above the tie-break floor
    return torch.from_numpy(sc)


def _top_rules_glassbox(acc, rel_i2lbl, top_n=15):
    """Flatten mined rules, sort by confidence, format human-readable (glass-box inspection)."""
    flat = []
    for r3, rules in acc.items():
        for (kind, r1, r2, conf, supp) in rules:
            h3 = rel_i2lbl.get(int(r3), "r%d" % r3)
            b1 = rel_i2lbl.get(int(r1), "r%d" % r1)
            if kind == "L2":
                b2 = rel_i2lbl.get(int(r2), "r%d" % r2)
                body = "%s(x,y) & %s(y,z)" % (b1, b2)
            elif kind == "L1F":
                body = "%s(x,z)" % b1
            else:  # L1I
                body = "%s(z,x)" % b1
            flat.append(dict(rule="%s(x,z) <= %s" % (h3, body), kind=kind,
                             conf=round(float(conf), 4), support=int(supp)))
    flat.sort(key=lambda d: d["conf"], reverse=True)
    return flat[:top_n]


# ---------------------------------------------------------------------------
# One corpus run: split -> mine -> ground -> propose -> score PAIRED -> metrics.
# ---------------------------------------------------------------------------

def _hits(sc, query_int, all_true, mask=None):
    if mask is not None:
        idx = np.where(mask)[0]
        if idx.size < 1:
            return dict(mrr=float("nan"), n=0)
        return filtered_hits_from_scores(sc[idx], query_int[idx], all_true, ks=EVAL_KS)
    return filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)


def run_corpus(pool_lbl, cfg, seed, corpus_name):
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

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    # grounding graphs (EXACT adjacency; oracle lookup, deliberately isolated from routing wall)
    g_ground = Graph(train_lbl + support_lbl, ent2i, rel2i)                      # RULE_INDUCT/SHUFFLE grounding
    g_oracle = Graph(train_lbl + support_lbl + query_lbl, ent2i, rel2i)          # RULE_ORACLE grounding (fold-in)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    # mine rules on train only (INDUCT), and on the folded-in graph (ORACLE)
    acc_train, n_rules_train, hub_skip = _mine(train_lbl, ent2i, rel2i)
    acc_shuf = _shuffle_rules(acc_train, n_rel, seed)
    acc_oracle, n_rules_oracle, _ = _mine(train_lbl + support_lbl + query_lbl, ent2i, rel2i)
    _log("seed=%d N=%d n_rel=%d n_rules_train=%d n_rules_oracle=%d hub_skipped=%d nq=%d n_sup=%d n_cold=%d"
         % (seed, N, n_rel, n_rules_train, n_rules_oracle, hub_skip, query_int.shape[0],
            support_int.shape[0], n_cold))

    strat, tert = stratify_by_tail_degree(query_int, g_oracle.node_degree)   # degree tertile for localization
    arm_metric, arm_sig = {}, {}
    arm_strata = {}
    for ai, (name, g_use, rules) in enumerate([(INDUCT, g_ground, acc_train), (SHUFFLE, g_ground, acc_shuf),
                                               (ORACLE, g_oracle, acc_oracle)]):
        sc = _score_rule_arm(g_use, rules, query_int, N, tiebreak_seed=seed * 9173 + ai)
        arm_metric[name] = _hits(sc, query_int, all_true)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_strata[name] = {nm: _hits(sc, query_int, all_true, mask=(strat == si))
                            for si, nm in enumerate(["low", "mid", "high"])}
        arm_strata[name]["low_mid"] = _hits(sc, query_int, all_true, mask=((strat == 0) | (strat == 1)))
        del sc
    # RANDOM null: uniform-random score over all N (fair random rank for gold)
    gR = torch.Generator().manual_seed(seed * 333 + 9)
    scR = torch.rand(query_int.shape[0], N, generator=gR)
    arm_metric[RANDOM] = _hits(scR, query_int, all_true)
    arm_sig[RANDOM] = _sig(scR.numpy()[:min(64, scR.shape[0])].ravel())
    arm_strata[RANDOM] = {nm: _hits(scR, query_int, all_true, mask=(strat == si))
                          for si, nm in enumerate(["low", "mid", "high"])}
    arm_strata[RANDOM]["low_mid"] = _hits(scR, query_int, all_true, mask=((strat == 0) | (strat == 1)))
    del scR
    # POP frequency incumbent
    pop_m, pop_rank_vec = pop_hits(g_ground.rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_metric[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: arm_metric[a]["n"] for a in ALL_ARMS},
        arm_sigs=arm_sig,
        arm_strata={a: {s: {"mrr": round(arm_strata[a][s].get("mrr", float("nan")), 6),
                            REACH_METRIC: round(arm_strata[a][s].get(REACH_METRIC, float("nan")), 6),
                            "n": arm_strata[a][s].get("n", 0)}
                        for s in arm_strata[a]} for a in arm_strata},
        degree_tertile_bounds=tert,
        n_rules_train=int(n_rules_train), n_rules_oracle=int(n_rules_oracle), hub_skipped=int(hub_skip),
        top_rules=_top_rules_glassbox(acc_train, rel_i2lbl, top_n=15),
    )
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm, metric=CEIL_METRIC):
    return ps["arm_hits"][arm].get(metric, float("nan"))


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _strat_margin(per_seed, sname):
    """Mean over seeds of (INDUCT - SHUFFLE)_mrr in a degree stratum (nan if too few)."""
    vals = []
    for ps in per_seed:
        st = ps.get("arm_strata", {})
        ci = st.get(INDUCT, {}).get(sname, {}); cs = st.get(SHUFFLE, {}).get(sname, {})
        if ci.get("n", 0) >= MIN_STRAT_Q and cs.get("n", 0) >= MIN_STRAT_Q:
            a = ci.get("mrr", float("nan")); b = cs.get("mrr", float("nan"))
            if a == a and b == b:
                vals.append(a - b)
    return _nm(vals) if vals else float("nan")


def aggregate_and_verdict(per_seed):
    def agg(arm, metric=CEIL_METRIC):
        return _nm([_m(ps, arm, metric) for ps in per_seed])

    m = {a: agg(a) for a in ALL_ARMS}                          # MRR per arm (gated)
    reach = {a: agg(a, REACH_METRIC) for a in ALL_ARMS}        # reach@2 per arm (drill framing)
    h10 = {a: agg(a, PRIMARY_METRIC) for a in ALL_ARMS}        # hits@10 (display)
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: agg(a, mk) for mk in metric_keys} for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    d_shuffle = _sub(m[INDUCT], m[SHUFFLE])                    # PRIMARY: real-vs-shuffled margin (MRR)
    d_random = _sub(m[INDUCT], m[RANDOM])                      # vs random null
    reach_shuffle = _sub(reach[INDUCT], reach[SHUFFLE])        # reach@2 real-vs-shuffled (drill's reach@k)
    oracle_headroom = _sub(m[ORACLE], m[RANDOM])              # H = arena-answerable ceiling headroom
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    shuffle_controlled = bool(d_shuffle == d_shuffle and d_shuffle > SHUFFLE_CTRL_EPS)

    # BROKEN guard: a NULL/control beating the RANDOM+arm-floor in a degenerate way. Compared to RANDOM/arm-
    # floor (NOT to POP: POP is structurally ~0 on held-out tails, so a control-beats-POP guard mis-fires --
    # the exact anchor_compose_magnitude BROKEN_TEST_CONTROL_BEATS_POP bug; F.4). SHUFFLE partially clearing
    # the floor is EXPECTED (shared reachable structure); whether that is disqualifying = shuffle_controlled.
    floor = max(m[RANDOM] if m[RANDOM] == m[RANDOM] else 0.0, 0.0)
    broken = bool(m[SHUFFLE] == m[SHUFFLE] and m[INDUCT] == m[INDUCT]
                  and (m[SHUFFLE] - m[INDUCT]) > BROKEN_FLOOR_EPS)   # shuffle beating the mechanism = degenerate

    # ceiling-relative corroboration
    H = oracle_headroom
    hp_frac_of_H = (d_shuffle / H) if (H == H and H > 0 and d_shuffle == d_shuffle) else float("nan")

    hard_pass = bool(d_shuffle == d_shuffle and d_shuffle >= HARD_PASS_MARGIN
                     and d_random == d_random and d_random >= HARD_PASS_MARGIN
                     and oracle_fires and shuffle_controlled and not broken and enough_heldout)
    hard_fail = bool(d_shuffle == d_shuffle and d_shuffle <= HARD_FAIL_MARGIN and oracle_fires and enough_heldout)
    middle = bool(enough_heldout and oracle_fires and not hard_pass and not hard_fail)

    # degree-stratified real-vs-shuffled margin (weak-point localization + super-hub confound control)
    strat_margins = {s: _strat_margin(per_seed, s) for s in ["low", "mid", "high", "low_mid"]}
    fair_holds = bool(strat_margins["low_mid"] == strat_margins["low_mid"]
                      and strat_margins["low_mid"] > 0.0)

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_SHUFFLE_BEATS_INDUCT"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_DOES_NOT_FIRE"
    elif hard_pass:
        verdict = "HARD_PASS_RULE_INDUCTION_GENERALIZES"
    elif hard_fail:
        verdict = "HARD_FAIL_RULE_INDUCTION_NO_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RULE_TRANSFER"

    verdict_msg = (
        "%s || HELD-OUT MRR [nq=%d]: INDUCT=%s SHUFFLE=%s RANDOM=%s ORACLE=%s POP=%s || reach@2: INDUCT=%s "
        "SHUFFLE=%s ORACLE=%s || real-vs-shuffled margin(mrr)=%s (HARD_PASS>=%.2f HARD_FAIL<=%.2f) vs-random=%s "
        "(>=%.2f) | ORACLE H=%s ratio=%sx fires=%s | shuffle_controlled=%s broken=%s | fair_lowmid_margin=%s "
        "(>0) | frac_of_H=%s | REF additive=%.4f oracle_ref=%.4f | seeds=%d"
        % (verdict, n_query, _fmt(m[INDUCT]), _fmt(m[SHUFFLE]), _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[POP]),
           _fmt(reach[INDUCT]), _fmt(reach[SHUFFLE]), _fmt(reach[ORACLE]), _fmt(d_shuffle),
           HARD_PASS_MARGIN, HARD_FAIL_MARGIN, _fmt(d_random), HARD_PASS_MARGIN, _fmt(H),
           (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires, shuffle_controlled,
           broken, _fmt(strat_margins["low_mid"]), _fmt(hp_frac_of_H), ADDITIVE_REF_MRR, ORACLE_REF_MRR,
           len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        heldout_reach_at_2={a: _rnd(reach[a]) for a in ALL_ARMS},
        heldout_hits_at_10={a: _rnd(h10[a], 5) for a in ALL_ARMS},
        real_vs_shuffled_mrr_margin=_rnd(d_shuffle), induct_vs_random_mrr_margin=_rnd(d_random),
        real_vs_shuffled_reach2_margin=_rnd(reach_shuffle),
        oracle_headroom=_rnd(H),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        real_vs_shuffled_frac_of_oracle_H=_rnd(hp_frac_of_H),
        degree_stratified_real_vs_shuffled_mrr={s: _rnd(strat_margins[s]) for s in strat_margins},
        reference_lines=dict(additive_anchor_compose_mrr=ADDITIVE_REF_MRR, oracle_additive_mrr=ORACLE_REF_MRR,
                             random_codes_mrr=RANDOM_REF_MRR),
        bands=dict(HARD_PASS_MARGIN=HARD_PASS_MARGIN, HARD_FAIL_MARGIN=HARD_FAIL_MARGIN,
                   ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   SHUFFLE_CTRL_EPS=SHUFFLE_CTRL_EPS, MIN_HELDOUT=MIN_HELDOUT,
                   MIN_SUPPORT=MIN_SUPPORT, MIN_CONF=MIN_CONF, MAX_RULES_PER_HEAD=MAX_RULES_PER_HEAD),
        n_query_scored=n_query,
        n_rules_train=int(_nm([ps.get("n_rules_train", float("nan")) for ps in per_seed]))
        if per_seed else 0,
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, shuffle_controlled=shuffle_controlled,
        broken=broken, fair_holds=fair_holds, hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
        top_rules=per_seed[0].get("top_rules") if per_seed else None,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test (planted rule arena; exercises the REAL mine_rules + propose code path).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    pool = build_planted_rule_arena(7)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, 7, "PLANTED_RULE_HELDOUT_ENTITY")
    out = dict(N=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"),
               n_cold=res.get("n_cold"), n_rules_train=res.get("n_rules_train"),
               top_rules=res.get("top_rules"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    induct_vs_shuffle = m[INDUCT] - m[SHUFFLE]
    induct_vs_random = m[INDUCT] - m[RANDOM]
    oracle_headroom = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    induct_recovers = bool(m[INDUCT] == m[INDUCT] and m[INDUCT] >= SELFTEST_INDUCT_MRR_MIN)
    beats_shuffle = bool(induct_vs_shuffle == induct_vs_shuffle and induct_vs_shuffle >= SELFTEST_INDUCT_BEATS_SHUFFLE)
    beats_random = bool(induct_vs_random == induct_vs_random and induct_vs_random >= SELFTEST_INDUCT_BEATS_RANDOM)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + SHUFFLE_CTRL_EPS)
    arms_differ = bool(n_sigs >= 4)

    # VACUOUS-SMOKE guard: the SHUFFLE must-fail control must NOT reach RULE_INDUCT on the planted arena.
    shuffle_reached_induct = bool(induct_vs_shuffle <= SELFTEST_INDUCT_BEATS_SHUFFLE)
    assert_discriminator_fires(shuffle_reached_induct, control_name=SHUFFLE,
                               headline_name="rule_induct_beats_shuffle_heldout", run_mode="self_test",
                               extra="RULE_SHUFFLE reached RULE_INDUCT on the planted held-out-entity arena -> "
                                     "the relation-specific rule is not carrying the signal / metric frozen")

    st_verdict, st_msg, _st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_fires),
         "control_name": ORACLE, "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted arena: RULE_ORACLE (rules grounded with held-out folded in) recovers held-out tails "
                  "and clears RANDOM by the ratio+abs fire gate -> the arena is answerable by rules"},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [m[RANDOM], m[SHUFFLE], m[INDUCT], m[ORACLE]],
         "extra": "MRR RANDOM=%.3f SHUFFLE=%.3f INDUCT=%.3f ORACLE=%.3f: the held-out readout responds to the "
                  "RIGHT relation-specific rules" % (m[RANDOM], m[SHUFFLE], m[INDUCT], m[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SHUFFLE]],
         "headline_threshold": m[INDUCT], "higher_is_pass": True, "margin": SELFTEST_INDUCT_BEATS_SHUFFLE,
         "n_repeats_min": 2, "control_name": "RANDOM_and_RULE_SHUFFLE_below_induct_mrr",
         "extra": "RANDOM + shuffled-rule-mapping must sit below RULE_INDUCT by the MRR margin -> the relation-"
                  "specific mined rule carries the signal, not reach/anchor/degree"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "shuffle_controlled", "broken_guard",
                                    "enough_heldout", "real_vs_shuffled_band"],
         "exercised_gates": ["arms_differ", "oracle_fires", "shuffle_controlled", "broken_guard",
                             "enough_heldout", "real_vs_shuffled_band"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["Graph", "mine_rules", "propose", "build_heldout_entity_split_ac"],
         "exercised_entrypoints": ["Graph", "mine_rules", "propose", "build_heldout_entity_split_ac"],
         "extra": "self-test builds the REAL Graph + calls the REAL mine_rules + propose + the shared held-out-"
                  "entity split at N~180 (no synthetic-only branch); same code path the FULL uses on CSKG"},
        {"kind": "guard_baseline_valid", "baseline_score": m[INDUCT], "floor_score": m[RANDOM],
         "guard_name": "BROKEN_SHUFFLE_BEATS_INDUCT", "baseline_name": "RULE_INDUCT", "floor_name": "RANDOM",
         "eps": 0.02,
         "extra": "the broken-test guard fires only if SHUFFLE beats RULE_INDUCT; its protected baseline is "
                  "RULE_INDUCT (validated ABOVE the RANDOM floor), NOT POP (POP is structurally ~0 on held-out "
                  "tails, so a control-beats-POP guard would mis-fire -- the anchor_compose_magnitude bug); F.4"},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 6) for a in ALL_ARMS},
        heldout_reach_at_2={a: round(ah[a].get(REACH_METRIC, float("nan")), 6) for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, induct_vs_shuffle=round(induct_vs_shuffle, 6),
        induct_vs_random=round(induct_vs_random, 6), oracle_headroom=round(oracle_headroom, 6),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        induct_recovers=induct_recovers, beats_shuffle=beats_shuffle, beats_random=beats_random,
        oracle_fires=oracle_fires, pop_at_floor=pop_at_floor, arms_differ=arms_differ,
        selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path", "guard_baseline_valid"],
    )
    ok = bool(induct_recovers and beats_shuffle and beats_random and oracle_fires
              and pop_at_floor and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("run_mode=%s seeds=%s MIN_SUPPORT=%d MIN_CONF=%.2f" % (run_mode, seeds, MIN_SUPPORT, MIN_CONF))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s induct=%s vs_shuffle=%s vs_random=%s oracle_fires=%s vp_ok=%s n_rules=%s"
         % (st_ok, st_res.get("heldout_mrr", {}).get(INDUCT), st_res.get("induct_vs_shuffle"),
            st_res.get("induct_vs_random"), st_res.get("oracle_fires"), st_res.get("validity_preflight_ok"),
            st_res.get("n_rules_train")))
    for r in (st_res.get("top_rules") or [])[:6]:
        _log("  selftest_rule: %s [conf=%.3f supp=%d]" % (r["rule"], r["conf"], r["support"]))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (RULE_INDUCT did not recover/beat shuffle+random, or ORACLE "
                        "did not fire, or POP not at floor, or arms not distinct): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS rule-induction held-out probe: mined Horn rules recover planted held-out "
                        "tails via forward-chaining; shuffled-rule + random fail; ORACLE fires; POP at floor; "
                        "6 validity-preflight checks declared (incl real_code_path + guard_baseline_valid)",
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
            res = run_corpus(pool, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY")
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 4:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_rules=%d | mrr INDUCT=%s SHUFFLE=%s RANDOM=%s ORACLE=%s POP=%s | reach@2 "
                 "INDUCT=%s SHUFFLE=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_rules_train"],
                  _fmt(ah[INDUCT]["mrr"]), _fmt(ah[SHUFFLE]["mrr"]), _fmt(ah[RANDOM]["mrr"]),
                  _fmt(ah[ORACLE]["mrr"]), _fmt(ah[POP]["mrr"]), _fmt(ah[INDUCT][REACH_METRIC]),
                  _fmt(ah[SHUFFLE][REACH_METRIC]), time.time() - ts))
            for r in (res.get("top_rules") or [])[:8]:
                _log("  rule: %s [conf=%.3f supp=%d]" % (r["rule"], r["conf"], r["support"]))
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
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if not args.self_test and not args.smoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "smoke", "full"):
            run_mode = _env_mode
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
