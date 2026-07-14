"""RULE-GATED ANCHOR_COMPOSE: high-precision mined Horn rules as a symbolic GATE on which 2-hop terms enter the
additive held-out-entity bundle (the rule-induction NEGATIVE's ENVELOPE).

THE ENVELOPE (from notes/research_drill_composition_operator_rule_theories_2026-07-13.md HEADLINE #2). The
rule-induction VET confirmed mined length<=2 Horn rules on CSKG are HIGH-PRECISION / LOW-COVERAGE: standalone they
tie POP on MRR (they cannot CARRY accuracy on held-out entities). But the drill's strongest quantified field result
(arXiv:2308.07942) is that rules used as a GATE on a stronger base method beat the base on BOTH axes (accuracy AND
legibility). So this cell does NOT use rules as a standalone predictor -- it uses their PCA-confidence purely as a
FILTER deciding which 2-hop compose terms are trustworthy enough to add to a held-out entity's ALREADY-VET-CONFIRMED
additive bundle (ANCHOR_COMPOSE, MEASURED 0.12821 MRR). Add precision where a high-confidence rule fires; keep the
pure additive map everywhere else. The target population is the degree-STARVED d1/d2_3 buckets: an entity with ONE
support edge has a noisy 1-hop bundle, so a trustworthy extra 2-hop estimate denoises it MOST there (and there is the
most oracle headroom -- MEASURED d1~0.059, d2_3~0.079 vs overall ORACLE 0.137).

MECHANISM (single-knob over ANCHOR_COMPOSE; the ONLY difference is the held-out code construction; ALL geometry
arms share the SAME frozen additive fit Xa/Da so the numbers are directly comparable to the 0.128 line):
  1-hop base (= ANCHOR_COMPOSE): E_base[t] = mean_i ( X[h_i] + D[r_i] ) over t's SUPPORT edges (h_i, r_i, t).
  2-hop rule-gated augmentation: for each support edge (h_i, r_i, t) and each TRAIN edge (h2, r1, h_i) INTO the
     anchor h_i, the chain h2 -r1-> h_i -r_i-> t gives an additive estimate X[h2] + D[r1] + D[r_i] of t's position
     (TransE: X[h_i]~X[h2]+D[r1], X[t]~X[h_i]+D[r_i]). GATE: admit that 2-hop term IFF the body pattern (r1, r_i)
     has a mined L2 rule R1(x,y)^R2(y,z)=>R3(x,z) with PCA-confidence >= GATE_CONF; WEIGHT it by that confidence
     (a soft, glass-box gated boost -- high-confidence relational compositions contribute more).
     E_gated[t] = weighted mean of {1-hop terms (weight 1)} U {admitted 2-hop terms (weight conf)}.
  The rules are mined ONCE (AnyBURL/RuleN path-counting, ZERO training, pure graph statistics) on the SAME train
  graph the additive fit uses; the gate is a dict lookup on (r1, r2) -> max L2 confidence. Fully inspectable: the
  admitted rules + their confidences + the per-bucket admit counts are all logged (glass-box).

ARMS (all scored PAIRED on the SAME held-out QUERY edges + candidate set + filtered eval, identical to the additive
cell so RULE_GATED vs ANCHOR is a clean single-knob head-to-head):
  RULE_GATED   : 1-hop base + confidence-gated confidence-weighted 2-hop terms. THE MECHANISM / candidate.
  ANCHOR       : pure additive 1-hop bundle (identical to ANCHOR_COMPOSE) -- the 0.128 line to BEAT + Gate-D
                 positive control (must reproduce ~0.128 at the FULL test regime).
  SHUFFLED     : the SAME construction but the body-pattern -> confidence mapping is DERANGED (identical confidence
                 DISTRIBUTION; each (r1,r2) receives ANOTHER pattern's confidence). MUST-FAIL: isolates whether the
                 RELATION-specific rule carries the lift vs a generic "add more 2-hop terms" confound. Shuffled
                 rules MUST NOT capture the lift.
  ALL_2HOP     : 1-hop base + ALL capped 2-hop terms (NO gate, weight 1). Ablation: tests whether the GATE's
                 SELECTIVITY matters vs blind inclusion (the drill's naive-2-hop-expansion crosstalk baseline).
  RANDOM       : random X + random D + additive readout. The null (clear by >= the abs floor).
  ORACLE       : additive fit with the held-out edges FOLDED IN (codes learned) -> positive control /
                 arena-answerable ceiling. If it fires, a null in the lift is interpretable, not an underfit harness.
  BASELINE_POP : per-relation tail frequency incumbent (held-out tails have train-freq 0 -> ~floor; fit-independence).

PRE-REG BANDS (picked BEFORE the run; primary metric = FILTERED MRR rank-vs-ALL-N, degree-unbiased, KGE standard,
the SAME metric+arena as the additive cell; H = MEASURED oracle headroom = ORACLE_mrr - RANDOM_mrr, resolved in-run;
degree-stratified by SUPPORT degree for weak-point localization on the drill's d1/d2_3 target):
  ORACLE-FIRES (arena answerable) : ORACLE_mrr >= 3x RANDOM_mrr AND ORACLE_mrr - RANDOM_mrr >= 0.003.
  HARD-PASS (rule-gating lifts additive, SELECTIVELY, on the degree-starved population, without crosstalk):
      gate fired (n_2hop_admitted_gated > 0) AND ORACLE fires AND enough held-out AND
      overall lift (RULE_GATED - ANCHOR)_mrr >= LIFT_ABS AND
      SELECTIVITY (RULE_GATED - SHUFFLED)_mrr >= SHUF_MARGIN (shuffled rules do NOT capture the lift) AND
      degree-starved lift on the low-support (d1+d2_3) stratum (RULE_GATED - ANCHOR)_mrr >= DEG_LIFT_ABS AND
      NO crosstalk collapse on well-served entities: RULE_GATED[d8plus]_mrr >= CROSSTALK_FLOOR * ANCHOR[d8plus]_mrr
      AND not broken.
  HARD-FAIL (rule-gating does NOT lift additive -- the clean negative): (RULE_GATED - ANCHOR)_mrr <= FAIL_ABS with
      ORACLE firing (includes the gate-admitted-nothing degenerate: CSKG's taxonomy-flat relation vocab is too flat
      for rule-composition patterns to add trustworthy 2-hop signal over the pure additive map).
  MIDDLE : oracle fires, enough held-out, lift present but not SELECTIVE (shuffled captures it), or not localized to
      the degree-starved population, or crosstalk-degraded -- weak-point-localize via the stratified diagnostics.
  Gated INCONCLUSIVE if ORACLE does not fire, too few held-out queries, or a control beats the mechanism degenerately.

## Compute architecture
class (c) MIXED: split + support/query partition + rule-mining + 2-hop candidate enumeration + POP = sequential-CPU
graph ops (streaming dict counts / adjacency lookups, no matmul, ZERO training); the additive/oracle fits =
minibatch SGD (batched, neg-chunked); E_base/E_gated construction = vectorized index_add_ bundles (the Python loop
only builds integer index lists -- the per-2-hop-term tensor add is ONE batched index_add_, not a per-edge torch
op); readouts = query-chunked batched matmul (the (nq,N) map is never materialized whole). The additive fit is the
matmul-heavy cost driver and is a GPU-batching candidate (per feedback_gpu_batching_mandatory) -> device=auto (cuda
on the GPU host; remote_cpu forces cpu). This cell REUSES the parent additive fit path unchanged (k=24 epochs=500)
so RULE_GATED vs the MEASURED 0.128 ANCHOR line is directly comparable. The rule-mining + gating rides along cheaply
(no GPU, no training). Storage SHARDED (each entity its own code; relations = per-TYPE additive displacements; the
only bundle is the per-ENTITY 1-hop+gated-2-hop mean). Multi-seed IN-PROCESS with per-seed partials + empty_cache +
cardinality gate; a MEMSMOKE (full N, few epochs, 2 seeds) validates no-OOM before the multi-hour FULL. The
discriminator-fires proof is the self-test (planted selective-2-hop arena) + analytical (B), NOT the memsmoke.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 7 arms produce >=6 distinct score signatures on the planted
#   arena (where the gate admits terms). On the FULL, if the gate legitimately admits nothing, RULE_GATED collapses
#   onto ANCHOR by design -> that is a NULL result (verdict GATE_ADMITTED_NOTHING), NOT a cardinality breach; the
#   FULL arms_differ gate requires only >=4 distinct sigs (ANCHOR/ALL_2HOP/RANDOM/ORACLE always differ) and the
#   mechanism verdict is separately gated on gate_fired.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + write_partial os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary metric FILTERED MRR + ceiling-aware; the lift headroom is REAL -- ANCHOR 0.12821
#   sits BELOW ORACLE 0.13729 (MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json) and the
#   degree-starved buckets (d1~0.059 d2_3~0.079) sit FAR below oracle, so a positive lift is reachable there; the
#   ORACLE positive control fires at 284x (MEASURED) so discriminator_reachability=TRUE.
# - baseline_in_band: ORACLE must fire (>=3x RANDOM_mrr AND headroom>=0.003); ANCHOR in a measurable band (MEASURED
#   0.128, neither floor nor saturated vs oracle 0.137); RANDOM/POP near the 1/N floor.
# - discriminator survives scale: analytical (B) + ORACLE-fires + self-test on the REAL fit+mine+gate+score code
#   path. A gate that admits a WRONG (shuffled) pattern adds a garbage 2-hop estimate that pulls E_gated off z[t] --
#   a STRUCTURAL property independent of N -> the real-vs-shuffled selectivity margin does not wash at scale.
# - HARD-PASS strictly above HARD-FAIL: LIFT_ABS clears FAIL_ABS by 4x + requires the SELECTIVITY margin + the
#   degree-starved gain + no-crosstalk, none of which the HARD-FAIL negative can satisfy.
# - HP_SCOPE: the lift HARD-PASS gates apply to RULE_GATED only. ORACLE = positive control (must fire); RANDOM =
#   null; SHUFFLED = must-fail selectivity control; ALL_2HOP = gate-vs-blind ablation; ANCHOR = the beat-target +
#   Gate-D reproducer; POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 7 arms + >=4 distinct sigs (FULL).
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- GATE_CONF/MIN_SUPPORT/MIN_CONF/caps/HELDOUT_ENTITY_FRAC/
#   SUPPORT_FRAC pre-registered, NOT tuned on real data; the lift bands are absolute MRR margins calibrated to the
#   MEASURED oracle/degree-bucket headroom; ORACLE-fire is ceiling-relative (ratio + non-noise abs floor).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the header + prereg.
# - Gate D (positive control at test regime): the ANCHOR arm reproduces ANCHOR_COMPOSE by construction (identical
#   build_anchor_compose_codes call, same fit) -> on the FULL it must land near MEASURED 0.128 (reproduce-at-regime).
# - Gate F: real_code_path = the self-test constructs the REAL additive fit (fit_kge_anchor1) + REAL mine_rules +
#   the REAL gated-compose builder + the REAL split + score at N~400 (no synthetic-only branch); substrate_signature
#   binds fit_kge_anchor1 + additive_direct_scores against the live signature (BASE/portable kwargs only);
#   guard_baseline_valid = the broken-test guard's protected baseline is ANCHOR (validated ABOVE the RANDOM floor),
#   NOT POP (POP structurally ~0 on held-out tails -> a control-beats-POP guard mis-fires; the anchor_compose_
#   magnitude bug; F.4 declared).
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints); timeout>=1800.

Reference lines on the SAME arena (tagged):
  ANCHOR_COMPOSE mrr = 0.12821  CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE
  ORACLE_ADDITIVE mrr= 0.13729  CITED@same:gates.heldout_mrr.ORACLE_ADDITIVE
  RANDOM_CODES mrr   = 0.000483 CITED@same:gates.heldout_mrr.RANDOM_CODES
  d1 anchor_mrr      = 0.0593   CITED@notes/research_drill_composition_operator_rule_theories_2026-07-13.md (scaling_ladder_v3)
  d2_3 anchor_mrr    = 0.0789   CITED@same
  d8plus anchor_mrr  = 0.1277   CITED@same

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
from experiments.exp_gt_induction_fb15k237_dense_v1 import (  # noqa: E402
    Graph, build_ids, mine_rules,
)
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
    stratify_by_tail_degree, PRIMARY_K,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_heldout_entity_split_ac, build_anchor_compose_codes, SUPPORT_BINS,
)

ANCHOR_NAME = "rule_gated_compose_inductive_entity_cskg_v1"

# ---- Arm names ----
GATED = "RULE_GATED"        # mechanism: 1-hop base + confidence-gated confidence-weighted 2-hop terms
ANCHOR = "ANCHOR"           # pure additive 1-hop bundle (= ANCHOR_COMPOSE 0.128 line); Gate-D reproducer
SHUFFLED = "SHUFFLED"       # must-fail: body-pattern -> confidence mapping DERANGED (same conf distribution)
ALL2HOP = "ALL_2HOP"        # ablation: 1-hop base + ALL capped 2-hop terms (no gate); gate-vs-blind
RANDOM = "RANDOM"           # null (random X + random D + additive readout)
ORACLE = "ORACLE"           # positive control: additive fit with held-out folded in (codes learned)
POP = "BASELINE_POP"        # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [GATED, ANCHOR, SHUFFLED, ALL2HOP, RANDOM, ORACLE]   # scored via additive geometry readouts
ALL_ARMS = GEOM_ARMS + [POP]

# ---- CEILING-AWARE, DEGREE-UNBIASED evaluation (same as the additive cell) ----
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"                       # PRIMARY gate metric: filtered MRR (degree-unbiased, full-rank)
PRIMARY_METRIC = "hits@%d" % PRIMARY_K    # legacy hits@10 display + degree stratification

# ---- rule-mining knobs (AnyBURL/RuleN path-counting; PRE-REGISTERED, NOT tuned on real data) ----
MIN_SUPPORT = 3
MIN_CONF = 0.05
MAX_RULES_PER_HEAD = 50
HUB_CAP = 60000

# ---- rule-GATE knobs (PRE-REGISTERED, NOT tuned on real data) ----
GATE_CONF = 0.30            # admit a 2-hop term iff its body-pattern max L2 confidence >= this (drill tried 0.3/0.5)
CAP_IN = 64                 # max incoming train edges per anchor considered for 2-hop expansion (hub bound)
CAP_2HOP = 32               # max admitted 2-hop terms per held-out entity (crosstalk + cost bound)

# ---- ORACLE-fire gate (arena answerable under the primary metric) ----
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003

# ---- pre-reg lift bands (primary metric = filtered MRR; absolute margins calibrated to MEASURED headroom) ----
LIFT_ABS = 0.002            # overall (RULE_GATED - ANCHOR)_mrr HARD-PASS threshold (~1.5% of 0.128; ~22% of the
                            #   0.009 ANCHOR->ORACLE residual headroom)
SHUF_MARGIN = 0.0015        # (RULE_GATED - SHUFFLED)_mrr selectivity margin (the must-fail: shuffled cannot capture)
DEG_LIFT_ABS = 0.004        # (RULE_GATED - ANCHOR)_mrr on the low-support d1+d2_3 stratum (drill's target pop)
CROSSTALK_FLOOR = 0.98      # RULE_GATED[d8plus]_mrr >= this * ANCHOR[d8plus]_mrr (no well-served regression >2%)
FAIL_ABS = 0.0005           # (RULE_GATED - ANCHOR)_mrr <= this with ORACLE firing = clean no-lift negative
BROKEN_EPS = 0.02           # a control (RANDOM/SHUFFLED) beating the mechanism/ANCHOR by > this = degenerate/broken
MIN_HELDOUT = 20
MIN_STRAT_Q = 8

# ---- reference lines on the SAME arena (tagged) ----
ANCHOR_REF_MRR = 0.12821    # CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE
ORACLE_REF_MRR = 0.13729    # CITED@same:gates.heldout_mrr.ORACLE_ADDITIVE
RANDOM_REF_MRR = 0.000483   # CITED@same:gates.heldout_mrr.RANDOM_CODES

# ---- held-out-entity split knobs (pre-registered; NOT tuned on real data; same as the additive cell) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- self-test planted thresholds (calibrated on the synthetic selective-2-hop grid, NOT real data) ----
SELFTEST_ORACLE_MRR_MIN = 0.15       # planted: ORACLE (learned held-out codes) mrr at least this
SELFTEST_ANCHOR_MRR_MIN = 0.04       # planted: ANCHOR (1-hop bundle) mrr at least this
SELFTEST_AC_BEATS_RANDOM = 0.02      # planted: (ANCHOR - RANDOM)_mrr >= this (1-hop works)
SELFTEST_GATED_BEATS_ANCHOR = 0.008  # planted: (RULE_GATED - ANCHOR)_mrr >= this (the gate lifts; observed ~0.014)
SELFTEST_GATED_BEATS_SHUFFLE = 0.008  # planted: (RULE_GATED - SHUFFLED)_mrr >= this (selectivity; observed ~0.016)
SELFTEST_MIN_HO = 8

SCORE_CHUNK = 256

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME split->fit->mine->gate->compose->score->verdict path.
SELFTEST_CFG = dict(k=12, epochs=350, n_neg=32, batch=4096,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)
# MEMSMOKE = FULL memory footprint (full N + k=24 + n_neg=128 + neg_chunk) but few epochs + 2 seeds IN-PROCESS.
MEMSMOKE_CFG = dict(k=24, epochs=25, n_neg=128, batch=8192, neg_chunk=16,
                    heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                    cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                    n_heldout_eval=2000, min_heldout=10, seeds=[7, 13])
# FULL: k=24 epochs=500 = the SAME fit fidelity as the MEASURED 0.128 ANCHOR_COMPOSE line (direct comparability).
FULL_CFG = dict(k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
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
# Rule mining -> body-pattern confidence gate.
# ---------------------------------------------------------------------------

def _mine(train_lbl, ent2i, rel2i):
    """Mine AnyBURL/RuleN Horn rules (L1F/L1I/L2) over train edges; return (accepted_by_head, n_rules, hub_skipped)."""
    g = Graph(train_lbl, ent2i, rel2i)
    target_rels = list(rel2i.values())
    acc, _allpat, hub_skipped = mine_rules(g, target_rels, MIN_SUPPORT, MIN_CONF, MAX_RULES_PER_HEAD, HUB_CAP)
    n_rules = sum(len(v) for v in acc.values())
    return acc, n_rules, hub_skipped


def build_body_conf(acc_by_head):
    """Flatten L2 rules -> {(r1,r2): max PCA-confidence over any head R3}. The gate signal: how reliably the 2-hop
    relation-composition r1;r2 predicts SOME relation (regardless of which). Zero-dimension-cost symbolic filter."""
    body_conf = {}
    for _r3, rules in acc_by_head.items():
        for (kind, r1, r2, conf, _supp) in rules:
            if kind != "L2":
                continue
            key = (int(r1), int(r2))
            if conf > body_conf.get(key, -1.0):
                body_conf[key] = float(conf)
    return body_conf


def _derangement(n, rng, max_tries=1000):
    for _ in range(max_tries):
        p = rng.permutation(n)
        if not any(int(p[i]) == i for i in range(n)):
            return p
    return np.array([(i + 1) % n for i in range(n)], dtype=np.int64)


def shuffle_body_conf(body_conf, seed, cand_patterns=None):
    """DERANGE the body-pattern -> confidence mapping over the FULL candidate-pattern universe (the mined patterns
    UNION the patterns that actually occur among the held-out entities' 2-hop candidates). Each pattern receives
    ANOTHER pattern's confidence (fixed-point-free), so a high confidence can land on a LOW-value / noise pattern
    and a real high-confidence composition pattern can lose its confidence -> the gate admits the WRONG 2-hop
    chains. The confidence DISTRIBUTION is preserved; only WHICH pattern carries which confidence is broken. This
    is the must-fail selectivity control (a reassignment restricted to the accepted high-conf set alone would be a
    near-no-op when those confidences are all high, so the universe MUST include the zero-confidence candidates)."""
    universe = set(body_conf.keys())
    if cand_patterns is not None:
        universe |= set((int(a), int(b)) for (a, b) in cand_patterns)
    keys = sorted(universe)
    n = len(keys)
    if n < 2:
        return dict(body_conf)
    rng = np.random.default_rng(seed * 4441 + 17)
    perm = _derangement(n, rng)
    vals = [body_conf.get(k, 0.0) for k in keys]
    return {keys[i]: vals[int(perm[i])] for i in range(n)}


# ---------------------------------------------------------------------------
# 2-hop candidate enumeration (shared across gated/shuffled/all arms -> fair) + gated-compose code construction.
# ---------------------------------------------------------------------------

def build_2hop_candidates(support_int, in_by_node, cap_in, cap_2hop):
    """Enumerate candidate 2-hop terms for held-out entities. For each support edge (h_i, r_i, t), each TRAIN edge
    (h2 -r1-> h_i) INTO the anchor gives the chain h2 -r1-> h_i -r_i-> t = additive estimate X[h2]+D[r1]+D[r_i] of
    t. Returns int arrays (t_arr, h2_arr, r1_arr, r2_arr) with r2 = the SUPPORT relation r_i. Deterministic: the
    first cap_in incoming edges per anchor (insertion order), at most cap_2hop terms per entity. The candidate SET
    is identical across gated/shuffled/all arms; only the per-term WEIGHT differs (fairness)."""
    t_l, h2_l, r1_l, r2_l = [], [], [], []
    per_ent = defaultdict(int)
    S = support_int.shape[0]
    for i in range(S):
        h_i = int(support_int[i, 0]); r_i = int(support_int[i, 1]); t = int(support_int[i, 2])
        inc = in_by_node.get(h_i, ())
        cnt = 0
        for (r1, h2) in inc:
            if cnt >= cap_in:
                break
            cnt += 1
            if per_ent[t] >= cap_2hop:
                break
            if int(h2) == t:            # never let a query tail estimate itself off its own edge
                continue
            t_l.append(t); h2_l.append(int(h2)); r1_l.append(int(r1)); r2_l.append(r_i)
            per_ent[t] += 1
    return (np.asarray(t_l, dtype=np.int64), np.asarray(h2_l, dtype=np.int64),
            np.asarray(r1_l, dtype=np.int64), np.asarray(r2_l, dtype=np.int64))


def build_gated_compose_codes(X, D, support_int, cand, weight_vec, device):
    """E_gated[t] = weighted mean of 1-hop terms (weight 1) + admitted 2-hop terms (weight in weight_vec, 0 = not
    admitted). weight_vec aligns with cand's rows. Returns (Xp, support_deg_1hop, n_admitted)."""
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    support_deg = np.zeros(N, dtype=np.int64)
    # ---- 1-hop base (identical to ANCHOR_COMPOSE) ----
    if support_int.shape[0] > 0:
        h = torch.from_numpy(support_int[:, 0].copy()).long().to(device)
        r = torch.from_numpy(support_int[:, 1].copy()).long().to(device)
        t = torch.from_numpy(support_int[:, 2].copy()).long().to(device)
        est1 = X[h] + D[r]
        acc.index_add_(0, t, est1)
        cnt.index_add_(0, t, torch.ones(t.shape[0], device=device, dtype=X.dtype))
        deg1 = torch.zeros(N, device=device, dtype=X.dtype)
        deg1.index_add_(0, t, torch.ones(t.shape[0], device=device, dtype=X.dtype))
        support_deg = deg1.detach().to("cpu").numpy().astype(np.int64)
    # ---- admitted 2-hop terms (weight > 0) ----
    n_admitted = 0
    t2_arr, h2_arr, r1_arr, r2_arr = cand
    if t2_arr.shape[0] > 0:
        w = np.asarray(weight_vec, dtype=np.float32)
        keep = np.where(w > 0.0)[0]
        n_admitted = int(keep.shape[0])
        if n_admitted > 0:
            t2 = torch.from_numpy(t2_arr[keep].copy()).long().to(device)
            h2 = torch.from_numpy(h2_arr[keep].copy()).long().to(device)
            r1 = torch.from_numpy(r1_arr[keep].copy()).long().to(device)
            r2 = torch.from_numpy(r2_arr[keep].copy()).long().to(device)
            wt = torch.from_numpy(w[keep].copy()).to(device=device, dtype=X.dtype)
            est2 = X[h2] + D[r1] + D[r2]
            acc.index_add_(0, t2, est2 * wt.unsqueeze(1))
            cnt.index_add_(0, t2, wt)
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    return Xp, support_deg, n_admitted


def _gate_weights(cand, body_conf, gate_conf, mode):
    """Per-candidate weight. mode='gated': conf if body_conf[(r1,r2)]>=gate_conf else 0. mode='all': 1.0 always
    (blind inclusion). Returns (weight_vec, n_admitted)."""
    _t2, _h2, r1_arr, r2_arr = cand
    m = r1_arr.shape[0]
    w = np.zeros(m, dtype=np.float32)
    if mode == "all":
        w[:] = 1.0
        return w, m
    n_adm = 0
    for i in range(m):
        c = body_conf.get((int(r1_arr[i]), int(r2_arr[i])), 0.0)
        if c >= gate_conf:
            w[i] = np.float32(c)
            n_adm += 1
    return w, n_adm


def _top_rules_glassbox(acc, rel_i2lbl, top_n=15):
    flat = []
    for r3, rules in acc.items():
        for (kind, r1, r2, conf, supp) in rules:
            if kind != "L2":
                continue
            b1 = rel_i2lbl.get(int(r1), "r%d" % r1)
            b2 = rel_i2lbl.get(int(r2), "r%d" % r2)
            h3 = rel_i2lbl.get(int(r3), "r%d" % r3)
            flat.append(dict(rule="%s(x,z) <= %s(x,y) & %s(y,z)" % (h3, b1, b2),
                             conf=round(float(conf), 4), support=int(supp)))
    flat.sort(key=lambda d: d["conf"], reverse=True)
    return flat[:top_n]


# ---------------------------------------------------------------------------
# Fit + build every arm's held-out codes + score PAIRED on the SAME query edges.
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                  rel_tail_freq, all_true, in_by_node, body_conf, ckpt_dir=None):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # ADDITIVE fit (shared by ANCHOR / RULE_GATED / SHUFFLED / ALL_2HOP): X (N,k), D (n_rel,k). Base/portable kwargs.
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive", seed))
    _ec()
    # ORACLE additive fit (held-out folded in -> held-out codes LEARNED) = positive control
    Xo, Do = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                             reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_oracle", seed))
    _ec()
    # RANDOM codes (random X + random D + additive readout) = the null
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    # ANCHOR (pure additive 1-hop; IDENTICAL to ANCHOR_COMPOSE via the imported builder -> Gate-D reproducer)
    Xanchor, support_deg = build_anchor_compose_codes(Xa, Da, support_int, device)

    # 2-hop candidate set (shared across gated/shuffled/all -> fair)
    cand = build_2hop_candidates(support_int, in_by_node, CAP_IN, CAP_2HOP)
    n_cand = int(cand[0].shape[0])
    cand_patterns = list(zip(cand[2].tolist(), cand[3].tolist())) if n_cand > 0 else []
    body_conf_shuf = shuffle_body_conf(body_conf, seed, cand_patterns=cand_patterns)
    w_gated, n_adm_gated = _gate_weights(cand, body_conf, GATE_CONF, "gated")
    w_shuf, n_adm_shuf = _gate_weights(cand, body_conf_shuf, GATE_CONF, "gated")
    w_all, n_adm_all = _gate_weights(cand, body_conf, GATE_CONF, "all")

    Xgated, _sd_g, _na_g = build_gated_compose_codes(Xa, Da, support_int, cand, w_gated, device)
    Xshuf, _sd_s, _na_s = build_gated_compose_codes(Xa, Da, support_int, cand, w_shuf, device)
    Xall, _sd_a, _na_a = build_gated_compose_codes(Xa, Da, support_int, cand, w_all, device)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, Xuse in [(GATED, Xgated), (ANCHOR, Xanchor), (SHUFFLED, Xshuf), (ALL2HOP, Xall),
                       (ORACLE, Xo), (RANDOM, Xr)]:
        Duse = Do if name == ORACLE else (Dr if name == RANDOM else Da)
        sc = additive_direct_scores(Xuse, Duse, query_int, device, chunk=SCORE_CHUNK)
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    del Xa, Da, Xo, Do, Xr, Dr, Xgated, Xshuf, Xall, Xanchor
    _ec()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg,
                n_2hop_cand=n_cand, n_2hop_admitted_gated=int(n_adm_gated),
                n_2hop_admitted_shuffled=int(n_adm_shuf), n_2hop_admitted_all=int(n_adm_all))


# ---------------------------------------------------------------------------
# Weak-point localization by SUPPORT degree (the drill's d1/d2_3 target) + global-degree tertile.
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


def localize_weak_points(arm_scores, query_int, all_true, support_deg, node_degree, rel_tail_freq, N):
    gold = query_int[:, 2]
    q_support = np.array([support_deg[int(g)] for g in gold], dtype=np.int64)
    strat, tert = stratify_by_tail_degree(query_int, node_degree)
    report_arms = [GATED, ANCHOR, SHUFFLED, ALL2HOP, RANDOM, ORACLE]

    def _by_mask(mask):
        out = {a: _hits_subset(arm_scores[a], query_int, all_true, mask) for a in report_arms}
        out[POP] = _pop_subset(rel_tail_freq, query_int, all_true, N, mask)
        return out

    by_support = {}
    for lo, hi, name in SUPPORT_BINS:
        by_support[name] = _by_mask((q_support >= lo) & (q_support <= hi))
    # low-support (drill target = cold+d1+d2_3, i.e. support degree <= 3) vs well-served (>= 8)
    low_support = _by_mask(q_support <= 3)
    by_gdeg_tertile = {nm: _by_mask(strat == si) for si, nm in enumerate(["low", "mid", "high"])}
    return dict(by_support_degree=by_support, low_support_le3=low_support,
                by_global_degree_tertile=by_gdeg_tertile, global_degree_tertile_bounds=tert,
                support_deg_hist={name: int(((q_support >= lo) & (q_support <= hi)).sum())
                                  for lo, hi, name in SUPPORT_BINS})


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None, localize=True):
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
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    # mine rules on train only -> body-pattern confidence gate (ZERO training, pure graph statistics)
    acc_train, n_rules_train, hub_skip = _mine(train_lbl, ent2i, rel2i)
    body_conf = build_body_conf(acc_train)
    n_body_ge_gate = int(sum(1 for v in body_conf.values() if v >= GATE_CONF))
    _log("seed=%d N=%d n_rel=%d n_rules=%d n_L2_body_patterns=%d n_body>=%.2f=%d hub_skip=%d"
         % (seed, N, n_rel, n_rules_train, len(body_conf), GATE_CONF, n_body_ge_gate, hub_skip))

    fs = fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                       gd.rel_tail_freq, all_true, gd.in_by_node, body_conf, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
        n_rules_train=int(n_rules_train), n_L2_body_patterns=int(len(body_conf)),
        n_body_ge_gate=n_body_ge_gate, hub_skipped=int(hub_skip),
        n_2hop_cand=fs["n_2hop_cand"], n_2hop_admitted_gated=fs["n_2hop_admitted_gated"],
        n_2hop_admitted_shuffled=fs["n_2hop_admitted_shuffled"], n_2hop_admitted_all=fs["n_2hop_admitted_all"],
        top_rules=_top_rules_glassbox(acc_train, rel_i2lbl, top_n=15),
    )
    if localize:
        result["localization"] = localize_weak_points(
            fs["arm_scores"], query_int, all_true, fs["support_deg"], gd.node_degree, gd.rel_tail_freq, N)
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


def _strat_mrr(per_seed, arm, sname):
    """Mean over seeds of arm MRR in a SUPPORT-degree stratum ('low_support_le3' or a SUPPORT_BINS name)."""
    vals = []
    for ps in per_seed:
        loc = ps.get("localization", {})
        cell = (loc.get("low_support_le3", {}) if sname == "low_support_le3"
                else loc.get("by_support_degree", {}).get(sname, {}))
        c = cell.get(arm, {})
        if c.get("n", 0) >= MIN_STRAT_Q:
            v = c.get("mrr", float("nan"))
            if v == v:
                vals.append(v)
    return _nm(vals) if vals else float("nan")


def aggregate_and_verdict(per_seed):
    def agg(arm, metric=CEIL_METRIC):
        return _nm([_m(ps, arm, metric) for ps in per_seed])

    m = {a: agg(a) for a in ALL_ARMS}
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: agg(a, mk) for mk in metric_keys} for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    n_adm_gated = int(_nm([ps.get("n_2hop_admitted_gated", 0) for ps in per_seed]))
    n_adm_shuf = int(_nm([ps.get("n_2hop_admitted_shuffled", 0) for ps in per_seed]))
    n_adm_all = int(_nm([ps.get("n_2hop_admitted_all", 0) for ps in per_seed]))

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    lift = _sub(m[GATED], m[ANCHOR])                    # PRIMARY: does rule-gating beat pure additive?
    shuffle_lift = _sub(m[SHUFFLED], m[ANCHOR])         # must-fail: shuffled rules should NOT lift
    gate_vs_shuffle = _sub(m[GATED], m[SHUFFLED])       # selectivity margin (the must-fail contrast)
    all2hop_lift = _sub(m[ALL2HOP], m[ANCHOR])          # blind-inclusion ablation
    H = _sub(m[ORACLE], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    # degree-starved (drill target) lift on the low-support (<=3) stratum + per-bucket d1/d2_3
    gated_low = _strat_mrr(per_seed, GATED, "low_support_le3")
    anchor_low = _strat_mrr(per_seed, ANCHOR, "low_support_le3")
    shuffled_low = _strat_mrr(per_seed, SHUFFLED, "low_support_le3")
    deg_lift_low = _sub(gated_low, anchor_low)
    gated_d1 = _strat_mrr(per_seed, GATED, "d1"); anchor_d1 = _strat_mrr(per_seed, ANCHOR, "d1")
    gated_d23 = _strat_mrr(per_seed, GATED, "d2_3"); anchor_d23 = _strat_mrr(per_seed, ANCHOR, "d2_3")
    deg_lift_d1 = _sub(gated_d1, anchor_d1); deg_lift_d23 = _sub(gated_d23, anchor_d23)
    # crosstalk on well-served entities (d8plus)
    gated_d8 = _strat_mrr(per_seed, GATED, "d8plus"); anchor_d8 = _strat_mrr(per_seed, ANCHOR, "d8plus")
    d8_ratio = _ratio(gated_d8, anchor_d8)

    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(H == H and H >= ORACLE_FIRE_ABS and oracle_ratio == oracle_ratio
                        and oracle_ratio >= ORACLE_FIRE_RATIO)
    gate_fired = bool(n_adm_gated > 0)

    # BROKEN guard: a control (RANDOM/SHUFFLED) beating the mechanism/ANCHOR degenerately. Protected baseline =
    # ANCHOR (MEASURED 0.128, validated ABOVE the RANDOM floor), NOT POP (structurally ~0 on held-out tails -> a
    # control-beats-POP guard mis-fires; the anchor_compose_magnitude bug; F.4).
    broken = bool((m[RANDOM] == m[RANDOM] and m[ANCHOR] == m[ANCHOR] and (m[RANDOM] - m[ANCHOR]) > BROKEN_EPS)
                  or (m[SHUFFLED] == m[SHUFFLED] and m[GATED] == m[GATED] and (m[SHUFFLED] - m[GATED]) > BROKEN_EPS))

    selective = bool(gate_vs_shuffle == gate_vs_shuffle and gate_vs_shuffle >= SHUF_MARGIN)
    lifts_overall = bool(lift == lift and lift >= LIFT_ABS)
    lifts_degstarved = bool((deg_lift_low == deg_lift_low and deg_lift_low >= DEG_LIFT_ABS)
                            or (deg_lift_d1 == deg_lift_d1 and deg_lift_d1 >= DEG_LIFT_ABS)
                            or (deg_lift_d23 == deg_lift_d23 and deg_lift_d23 >= DEG_LIFT_ABS))
    no_crosstalk = bool((d8_ratio != d8_ratio)   # unknown (too few d8plus) -> do not fail on it
                        or d8_ratio == float("inf") or d8_ratio >= CROSSTALK_FLOOR)

    hard_pass = bool(gate_fired and oracle_fires and enough_heldout and not broken
                     and lifts_overall and selective and lifts_degstarved and no_crosstalk)
    hard_fail = bool(oracle_fires and enough_heldout and not broken
                     and lift == lift and lift <= FAIL_ABS)
    middle = bool(oracle_fires and enough_heldout and not broken and not hard_pass and not hard_fail)

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_CONTROL_BEATS_MECHANISM"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not gate_fired:
        verdict = "HARD_FAIL_GATE_ADMITTED_NOTHING"
    elif hard_pass:
        verdict = "HARD_PASS_RULE_GATE_LIFTS_ADDITIVE"
    elif hard_fail:
        verdict = "HARD_FAIL_RULE_GATE_NO_LIFT"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RULE_GATE_LIFT"

    verdict_msg = (
        "%s || HELD-OUT MRR [nq=%d]: GATED=%s ANCHOR=%s SHUFFLED=%s ALL_2HOP=%s | RANDOM=%s ORACLE=%s POP=%s || "
        "lift(GATED-ANCHOR)=%s (HP>=%.4f FAIL<=%.4f) | selectivity(GATED-SHUFFLED)=%s (>=%.4f) shuffle_lift=%s | "
        "all2hop_lift=%s | ORACLE H=%s ratio=%sx fires=%s | gate_fired=%s admitted g/s/all=%d/%d/%d cand=%d || "
        "low-sup(<=3) GATED=%s ANCHOR=%s deg_lift=%s (>=%.4f) | d1 lift=%s d2_3 lift=%s | d8plus GATED=%s "
        "ANCHOR=%s ratio=%s (>=%.2f) | broken=%s | REF anchor=%.5f oracle=%.5f | seeds=%d"
        % (verdict, n_query, _fmt(m[GATED]), _fmt(m[ANCHOR]), _fmt(m[SHUFFLED]), _fmt(m[ALL2HOP]),
           _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[POP]), _fmt(lift), LIFT_ABS, FAIL_ABS, _fmt(gate_vs_shuffle),
           SHUF_MARGIN, _fmt(shuffle_lift), _fmt(all2hop_lift), _fmt(H),
           (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires, gate_fired,
           n_adm_gated, n_adm_shuf, n_adm_all, int(_nm([ps.get("n_2hop_cand", 0) for ps in per_seed])),
           _fmt(gated_low), _fmt(anchor_low), _fmt(deg_lift_low), DEG_LIFT_ABS, _fmt(deg_lift_d1),
           _fmt(deg_lift_d23), _fmt(gated_d8), _fmt(anchor_d8),
           (_fmt(d8_ratio) if d8_ratio != float("inf") else "inf"), CROSSTALK_FLOOR, broken,
           ANCHOR_REF_MRR, ORACLE_REF_MRR, len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        lift_gated_vs_anchor=_rnd(lift), selectivity_gated_vs_shuffled=_rnd(gate_vs_shuffle),
        shuffle_lift_vs_anchor=_rnd(shuffle_lift), all2hop_lift_vs_anchor=_rnd(all2hop_lift),
        degree_starved_lift=dict(low_support_le3=_rnd(deg_lift_low), d1=_rnd(deg_lift_d1), d2_3=_rnd(deg_lift_d23),
                                 gated_low=_rnd(gated_low), anchor_low=_rnd(anchor_low),
                                 shuffled_low=_rnd(shuffled_low)),
        crosstalk_d8plus=dict(gated=_rnd(gated_d8), anchor=_rnd(anchor_d8),
                              ratio=(round(d8_ratio, 4) if (d8_ratio == d8_ratio and d8_ratio != float("inf")) else None)),
        oracle_headroom=_rnd(H),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        n_2hop_admitted_gated=n_adm_gated, n_2hop_admitted_shuffled=n_adm_shuf, n_2hop_admitted_all=n_adm_all,
        n_query_scored=n_query,
        reference_lines=dict(anchor_compose_mrr=ANCHOR_REF_MRR, oracle_additive_mrr=ORACLE_REF_MRR,
                             random_codes_mrr=RANDOM_REF_MRR),
        bands=dict(LIFT_ABS=LIFT_ABS, SHUF_MARGIN=SHUF_MARGIN, DEG_LIFT_ABS=DEG_LIFT_ABS,
                   CROSSTALK_FLOOR=CROSSTALK_FLOOR, FAIL_ABS=FAIL_ABS, ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO,
                   ORACLE_FIRE_ABS=ORACLE_FIRE_ABS, GATE_CONF=GATE_CONF, MIN_SUPPORT=MIN_SUPPORT, MIN_CONF=MIN_CONF,
                   CAP_IN=CAP_IN, CAP_2HOP=CAP_2HOP, MIN_HELDOUT=MIN_HELDOUT),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, gate_fired=gate_fired, broken=broken,
        selective=selective, lifts_overall=lifts_overall, lifts_degstarved=lifts_degstarved,
        no_crosstalk=no_crosstalk, hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
        top_rules=per_seed[0].get("top_rules") if per_seed else None,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Planted SELECTIVE-2-HOP arena for the self-test. EXPLICIT clean composition chains: for group g, each chain has
# fresh nodes h -rA-> mid -rB-> tail AND h -rC-> tail (SAME tail), so the rule rA(x,y)^rB(y,z)=>rC(x,z) holds
# EXACTLY -> mined L2 confidence ~1.0 (>> GATE_CONF). The edge set is additively consistent (rC = rA+rB) so the
# additive fit + ANCHOR_COMPOSE + ORACLE all work. NOISE relations point INTO mids, so noise 2-hop patterns
# (rN, rB) OCCUR as candidates but mine near-zero confidence -> the real gate REJECTS them; a DERANGED gate
# reassigns the high confidence to a noise pattern -> admits garbage 2-hop estimates -> the must-fail SHUFFLED
# fails. A held-out tail is denoised by the 2-hop chain h -rA-> mid -rB-> tail (body rA;rB, high conf) added to
# its noisy 1-hop bundle. Deterministic (default_rng + order-preserving dedup).
# ---------------------------------------------------------------------------

def build_planted_gate_arena(seed, n_groups=3, n_chains=90, n_noise=4, noise_into_mid=2):
    rng = np.random.default_rng(seed * 100019 + 11)
    edges = []
    nid = [0]

    def fresh():
        e = "e%d" % nid[0]; nid[0] += 1
        return e

    mids, heads = [], []
    for g in range(n_groups):
        rA = "rA%d" % g; rB = "rB%d" % g; rC = "rC%d" % g
        for _i in range(n_chains):
            h = fresh(); mid = fresh(); tail = fresh()
            edges.append((h, rA, mid))
            edges.append((mid, rB, tail))
            edges.append((h, rC, tail))     # rA(h,mid)^rB(mid,tail)=>rC(h,tail) holds EXACTLY
            mids.append(mid); heads.append(h)
    n_nodes = nid[0]
    # noise edges INTO mids -> noise 2-hop patterns (rN, rB) exist as candidates but mine ~0 confidence
    for mid in mids:
        for _ in range(noise_into_mid):
            rh = heads[int(rng.integers(len(heads)))]
            rn = "rN%d" % int(rng.integers(n_noise))
            if rh != mid:
                edges.append((rh, rn, mid))
    # extra random noise for POP non-triviality + a non-degenerate relation vocab
    all_nodes = ["e%d" % i for i in range(n_nodes)]
    for _ in range(n_chains * 2):
        a = all_nodes[int(rng.integers(n_nodes))]
        b = all_nodes[int(rng.integers(n_nodes))]
        if a != b:
            edges.append((a, "rNoiseX", b))
    return list(dict.fromkeys(edges))


# ---------------------------------------------------------------------------
# Mechanism self-test (planted selective-2-hop arena; exercises the REAL fit + mine + gate + compose + score path).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    pool = build_planted_gate_arena(7)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_SELECTIVE_2HOP", ckpt_dir=None, localize=True)
    out = dict(N=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"),
               n_rules_train=res.get("n_rules_train"), n_2hop_cand=res.get("n_2hop_cand"),
               n_2hop_admitted_gated=res.get("n_2hop_admitted_gated"),
               n_2hop_admitted_shuffled=res.get("n_2hop_admitted_shuffled"),
               n_2hop_admitted_all=res.get("n_2hop_admitted_all"), top_rules=res.get("top_rules"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted arena produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    lift = m[GATED] - m[ANCHOR]
    gate_vs_shuffle = m[GATED] - m[SHUFFLED]
    anchor_vs_random = m[ANCHOR] - m[RANDOM]
    oracle_headroom = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    anchor_recovers = bool(m[ANCHOR] == m[ANCHOR] and m[ANCHOR] >= SELFTEST_ANCHOR_MRR_MIN)
    anchor_beats_random = bool(anchor_vs_random == anchor_vs_random and anchor_vs_random >= SELFTEST_AC_BEATS_RANDOM)
    gate_lifts = bool(lift == lift and lift >= SELFTEST_GATED_BEATS_ANCHOR)
    gate_selective = bool(gate_vs_shuffle == gate_vs_shuffle and gate_vs_shuffle >= SELFTEST_GATED_BEATS_SHUFFLE)
    gate_fired = bool(res.get("n_2hop_admitted_gated", 0) > 0)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + 0.005)
    arms_differ = bool(n_sigs >= 6)

    # VACUOUS-SMOKE guard: the SHUFFLED must-fail control must NOT reach RULE_GATED on the planted arena.
    shuffle_reached_gated = bool(gate_vs_shuffle <= SELFTEST_GATED_BEATS_SHUFFLE)
    assert_discriminator_fires(shuffle_reached_gated, control_name=SHUFFLED,
                               headline_name="rule_gated_beats_shuffled_heldout", run_mode="self_test",
                               extra="SHUFFLED rule-gate reached RULE_GATED on the planted selective-2-hop arena -> "
                                     "the relation-specific gate is not carrying the lift / metric frozen")

    st_verdict, _st_msg, _st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": ORACLE, "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted arena: ORACLE (learned held-out codes) recovers held-out tails and clears RANDOM by the "
                  "ratio+abs fire gate -> the arena is answerable and the lift bar is achievable-in-principle"},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [m[RANDOM], m[ANCHOR], m[GATED], m[ORACLE]],
         "extra": "MRR RANDOM=%.3f ANCHOR=%.3f GATED=%.3f ORACLE=%.3f: the held-out readout responds to the "
                  "rule-gated 2-hop augmentation" % (m[RANDOM], m[ANCHOR], m[GATED], m[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SHUFFLED]],
         "headline_threshold": m[GATED], "higher_is_pass": True, "margin": SELFTEST_GATED_BEATS_SHUFFLE,
         "n_repeats_min": 2, "control_name": "RANDOM_and_SHUFFLED_below_gated_mrr",
         "extra": "RANDOM + shuffled-rule-gate must sit below RULE_GATED by the MRR margin -> the relation-specific "
                  "gate (not blind 2-hop expansion / degree / anchor identity) carries the lift"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "gate_fired", "broken_guard", "enough_heldout",
                                    "selective", "lift_band"],
         "exercised_gates": ["arms_differ", "oracle_fires", "gate_fired", "broken_guard", "enough_heldout",
                             "selective", "lift_band"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1", "mine_rules", "build_anchor_compose_codes",
                                        "build_gated_compose_codes", "additive_direct_scores",
                                        "build_heldout_entity_split_ac"],
         "exercised_entrypoints": ["fit_kge_anchor1", "mine_rules", "build_anchor_compose_codes",
                                   "build_gated_compose_codes", "additive_direct_scores",
                                   "build_heldout_entity_split_ac"],
         "extra": "self-test runs the REAL additive fit + REAL rule mining + REAL gated-compose builder + REAL "
                  "split + score at N~420 (no synthetic-only branch); same code path the FULL uses on CSKG"},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1,
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": None, "seed": 0, "epochs": 1,
                    "reciprocal": True, "lr": A1_LR, "n_neg": 1, "batch_size": 8, "neg_chunk": None,
                    "transductive_extra": None, "ckpt": None},
         "callable_name": "fit_kge_anchor1",
         "extra": "binds the additive fit call against the live signature (base/portable kwargs)"},
        {"kind": "substrate_signature", "callable_obj": additive_direct_scores,
         "kwargs": {"X": None, "D": None, "hold_edges": None, "device": None, "chunk": SCORE_CHUNK},
         "callable_name": "additive_direct_scores",
         "extra": "binds the readout call against the live signature"},
        {"kind": "guard_baseline_valid", "baseline_score": m[ANCHOR], "floor_score": m[RANDOM],
         "guard_name": "BROKEN_CONTROL_BEATS_MECHANISM", "baseline_name": "ANCHOR", "floor_name": "RANDOM",
         "eps": 0.02,
         "extra": "the broken guard's protected baseline is ANCHOR (validated ABOVE the RANDOM floor), NOT POP "
                  "(structurally ~0 on held-out tails -> a control-beats-POP guard mis-fires; anchor_compose_"
                  "magnitude bug); F.4"},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 6) for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, lift=round(lift, 6), gate_vs_shuffle=round(gate_vs_shuffle, 6),
        anchor_vs_random=round(anchor_vs_random, 6), oracle_headroom=round(oracle_headroom, 6),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, anchor_recovers=anchor_recovers,
        anchor_beats_random=anchor_beats_random, gate_lifts=gate_lifts, gate_selective=gate_selective,
        gate_fired=gate_fired, pop_at_floor=pop_at_floor, arms_differ=arms_differ,
        selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path", "substrate_signature(x2)", "guard_baseline_valid"],
    )
    ok = bool(oracle_recovers and oracle_fires and anchor_recovers and anchor_beats_random
              and gate_lifts and gate_selective and gate_fired and pop_at_floor and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s GATE_CONF=%.2f" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"], GATE_CONF))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s lift=%s gate_vs_shuffle=%s anchor=%s oracle_fires=%s gate_fired=%s adm(g/s/all)="
         "%s/%s/%s vp_ok=%s"
         % (st_ok, st_res.get("lift"), st_res.get("gate_vs_shuffle"),
            st_res.get("heldout_mrr", {}).get(ANCHOR), st_res.get("oracle_fires"), st_res.get("gate_fired"),
            st_res.get("n_2hop_admitted_gated"), st_res.get("n_2hop_admitted_shuffled"),
            st_res.get("n_2hop_admitted_all"), st_res.get("validity_preflight_ok")))
    for r in (st_res.get("top_rules") or [])[:6]:
        _log("  selftest_rule: %s [conf=%.3f supp=%d]" % (r["rule"], r["conf"], r["support"]))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (gate did not lift over ANCHOR, or shuffled reached gated, or "
                        "ORACLE did not fire, or gate did not fire, or arms not distinct): %s"
                        % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS rule-gated compose: high-confidence rule gate admits reliable 2-hop terms that "
                        "lift the additive bundle over pure ANCHOR; shuffled-rule gate + random fail; ORACLE fires; "
                        "POP at floor; 8 validity-preflight checks declared (incl real_code_path + 2x signature + "
                        "guard_baseline_valid)",
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
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", ckpt_dir=out_dir, localize=True)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            # FULL arms_differ: require >=4 distinct sigs (ANCHOR/ALL_2HOP/RANDOM/ORACLE always differ). RULE_GATED
            # may legitimately collapse onto ANCHOR if the gate admits nothing -> that is a NULL, not a breach.
            if len(sigset) < 4:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d n_rules=%d body>=gate=%d adm(g/s/all)=%d/%d/%d | mrr GATED=%s "
                 "ANCHOR=%s SHUFFLED=%s ALL2HOP=%s RANDOM=%s ORACLE=%s POP=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"], res["n_cold"], res["n_rules_train"],
                  res["n_body_ge_gate"], res["n_2hop_admitted_gated"], res["n_2hop_admitted_shuffled"],
                  res["n_2hop_admitted_all"], _fmt(ah[GATED]["mrr"]), _fmt(ah[ANCHOR]["mrr"]),
                  _fmt(ah[SHUFFLED]["mrr"]), _fmt(ah[ALL2HOP]["mrr"]), _fmt(ah[RANDOM]["mrr"]),
                  _fmt(ah[ORACLE]["mrr"]), _fmt(ah[POP]["mrr"]), time.time() - ts))
            for r in (res.get("top_rules") or [])[:8]:
                _log("  rule: %s [conf=%.3f supp=%d]" % (r["rule"], r["conf"], r["support"]))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

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
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    if not args.self_test and not args.memsmoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
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
