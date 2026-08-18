"""Stage-5 CG cell: GENUINE compositional-generalization (DBCA compound-divergence) test.

Does the glass-box REPLAY-TRAVERSAL learner (b1, atom 29445) achieve SYSTEMATIC generalization to HELD-OUT
relation-COMBINATIONS that a FLAT (non-compositional, learned-memorization) baseline CANNOT -- in a way that is
LEARNED (content/relation-dependent, real-beats-random) and NOT free-by-fixed-algebra (atom 29437)?

WHY THIS CELL (the VET flag it fixes). b1 (exp_grounding_multihop_generative_replay_traversal_v1) showed beam-
rollout traversal ~doubles autonomous multi-hop (reach@2 0.181->0.319) with content-dependence (scramble hurts).
But b1's held-out was pairing + an independent chain DRAW (replication), NOT a disjoint-compound / compound-
divergence split. So b1's *composition* claim was untested against the CG literature's actual bar: systematicity
to novel COMBINATIONS of known primitives, where FLAT architectures fail (Keysers 2020 CFQ/DBCA; Lake & Baroni;
SCAN). This cell builds that missing test.

CLOSURE CONTEXT (design must DISTINGUISH, not re-derive). Prior compgen-CG closed at STRONG-MM because fixed-VSA
systematicity is FREE-by-construction (atom 29437: random relation-geometry BEATS real -> free-algebra signature,
learns nothing). This cell is different only if BOTH hold: (a) the compositional arm beats a FAIR flat baseline on
HIGH-compound-divergence held-out by a margin that WIDENS as divergence rises (flat collapses, compositional
holds); (b) the win is LEARNED (scrambling relation->role geometry HURTS the traversal = real-beats-random), not
free (random-beats-real). Either one missing => NOT a genuine CG (HARD_FAIL or MIDDLE).

BRAIN-FIRST (why compound-divergence is the brain-faithful CG probe). Humans generalize to held-out COMBINATIONS
of familiar primitives (Marcus 1999; wug; Lake 2019 few-shot instruction; Baroni 2020). CFQ/DBCA (Keysers 2020)
operationalizes this: hold ATOM divergence LOW (same primitives in train and test) while MAXIMIZING COMPOUND
divergence (test contains primitive-combinations never seen together). Flat seq2seq nets fail; structure-biased
models generalize. Here the "structure bias" is the glass-box per-hop typed-edge traversal (compose one learned
relation-primitive at a time over the real local graph); the "flat" learner memorizes the whole 2-hop query as an
atomic unit and cannot recombine.

ARMS (ONE VARIABLE = the learner; identical DBCA split + identical learned codes + identical seeds across arms):
  NO_CLEANUP        : global-cleanup-only chain (must-fail / anti-saturation; collapses at reach>=2).
  MEMORYLESS        : goal-blind local decoder = the floor (non-graph-anchored per-hop bind + codebook cleanup).
  FLAT_NN           : PRIMARY flat baseline. Non-compositional MEMORIZER: for a test 2-hop query with compound
                      c=(r1,r2) and start s, retrieve the goal of the nearest TRAIN start under the SAME compound c
                      (1-NN in learned-code space). NO per-hop composition, NO graph traversal. On a HELD-OUT
                      compound (no train chains of c) it falls back to a global 1-NN (wrong compound) -> collapses.
                      This is the textbook flat-net systematicity failure: memorizes seen combinations, cannot
                      recombine to unseen ones.
  FLAT_ASSOC        : SECONDARY flat baseline + learning-curve source. Learned LINEAR associator W = Ktr^T Gtr
                      mapping key=l2(bind(compound_role, Z[start])) -> Z[goal], trained on TRAIN chains only, no
                      intermediate waypoint. Direct start->terminal recall. Same collapse mechanism as FLAT_NN.
  AUTONOMOUS_GREEDY : b1 myopic goal-directed argmax (B=1) over the local typed edges (compound-agnostic).
  REPLAY_TRAVERSAL  : THE CG CANDIDATE. b1 beam-rollout width B over the LOCAL typed edge set; deferred full-path
                      selection. Composes learned relation-primitives ONE HOP AT A TIME -> never needs the compound
                      to have been seen -> should HOLD across compound-divergence (systematicity).
  REPLAY_TRAVERSAL_SCRAMBLED : LEARNED-not-FREE control. Identical beam-rollout but relation-type -> role map is
                      DERANGED. If the traversal win is genuinely relational (learned), scrambling must SEVERELY
                      hurt (real-beats-random). If scrambling HELPS or is neutral -> free-algebra signature (29437).

DBCA SPLIT (the load-bearing new machinery). Atom = relation type r. Compound = ordered relation bigram (r1,r2)
of a 2-hop chain. Held-out set H = a subset of observed bigrams removed from TRAIN while PRESERVING atom coverage
(every relation still appears in train as r1 AND r2 => atom_divergence ~ 0). TRAIN (for the flat arms) is FIXED
across the whole sweep; only the TEST set's compound composition varies. The difficulty axis is compound-divergence
div in {0.0, 0.34, 0.67, 1.0}: the fraction of test chains whose bigram is NOT in train (div=0 = all seen
compounds; div=1 = all held-out compounds). By construction atom_divergence stays ~0 (measured) and
compound_divergence == div (measured). The compositional arms (greedy/traversal/scramble) do NOT train on
compounds, so their performance is compound-agnostic (should be ~flat across div); the flat arms train on train
compounds and should DROP as div rises.

CG DISCRIMINATORS (both must hold for HARD_PASS; each CAN fail):
  (a) SYSTEMATICITY: margin(div) = traversal@2(div) - flat@2(div) WIDENS with div (flat collapses on held-out,
      traversal holds). Fails if flat matches traversal on held-out (widen ~ 0) OR traversal itself collapses.
  (b) LEARNED-not-FREE: content_dep = traversal@2 - scrambled@2 (on held-out) >= CONTENT_DEP_MIN. Fails (HARD_FAIL)
      if content_dep <= 0 (random-beats-real = free-algebra 29437 signature).

LEARNING CURVE: FLAT_ASSOC held-out reach@2 vs train exposure (k_frac in {0.25,0.5,1.0}); traversal/greedy are
exposure-invariant (no compound training) -> reported as their flat line.

PRE-REGISTERED VERDICT (self-calibrated within-run to the measured div0/div1 anchors; robust to config drift):
  HARD_PASS_CG (genuine chain-grade, cert_delta +1 CANDIDATE -> HARDEST skunkworks-VET, ZERO false CG):
      flat_in_band AND flat_collapses AND traversal_holds AND widen>=WIDEN_MIN AND margin(div1)>=MARGIN_HI_MIN
      AND content_dep_fires AND no_global_T_matrix.
  HARD_FAIL_CG: free_algebra_signature (content_dep<=0) OR traversal_collapses OR (widen<=WIDEN_FAIL AND
      margin(div1)<MARGIN_HI_MIN) [flat ties traversal on held-out => not compositional].
  MIDDLE: partial widening, OR gap widens but content-dep does NOT fire (COSMETIC_GRAPH not relational), OR flat
      baseline too weak to be a real baseline (VACUOUS -- widening test undefined from a floor baseline).

GLASS-BOX invariant: bounded top-B rollout over a [n+1, Dmax] LOCAL typed-edge table (Dmax << n), every step
inspectable, NO backprop in the traversal, NO opaque scoring, NO [n,n] transition/reachability matrix (machine-
checked no_global_T_matrix). The FLAT arms are a learned linear/NN readout (their memorization is the point).

## Compute architecture
class: (c) mixed with justification. Storage strategy: SHARDED (each node its own code vector; compositional
multi-hop chaining, per META_STORAGE_STRATEGY). The InfoNCE binding encoder trains ONCE per seed; the DBCA split
and all arms then run over the FIXED codes (cheap). Within a hop, chains x beams x local candidates are batched
einsum. Across hops the traversal is genuinely SEQUENTIAL (data dependency, not a batching flaw). Local is CPU
(torch 2.12.0+cpu here); FULL is sized to complete in the foreground on CPU. No Python-loop matmul over
independent phase points.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FLAT_NN != FLAT_ASSOC != GREEDY != TRAVERSAL != SCRAMBLED !=
#   MEMORYLESS != NO_CLEANUP; asserted per seed on distinct commit signatures at div=1).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: top-1 chance floor = 1/n_nodes (~0.0003 at n=3500). Reference points are MEASURED within-run anchors
#   (MEMORYLESS floor, traversal, flat seen-vs-held). HARD_PASS bars (widen>=0.06, margin>=0.08, content_dep>=0.06)
#   are categorical margins over measured floors, not at-chance thresholds. crlb_reachability: OK.
# - baseline_in_band: MEMORYLESS@1 in (0.05,0.95); NO_CLEANUP@2 collapses (anti-saturation). FLAT@2(div0) must be
#   above MEMORYLESS floor (flat is a REAL baseline) else MIDDLE_BAND_FLAT_BASELINE_VACUOUS.
# - discriminator survives scale: the CG discriminator (traversal-vs-flat WIDENING with div + scramble-hurts) is
#   the MEASUREMENT; it MUST fire at smoke (widen and margin at div1 above SMOKE gates) or FULL is aborted
#   (DISCRIMINATOR-MUST-SURVIVE-SCALE). Anti-saturation must-fail NO_CLEANUP collapses AT smoke scale.
# - HARD_PASS strictly above floor: conjunction of widen + margin + flat-collapse + content-dep is a categorical
#   margin, not an at-floor result.
# - HP_SCOPE: the CG systematicity gate applies to REPLAY_TRAVERSAL (vs FLAT). GREEDY/SUPPLIED/MEMORYLESS are
#   reference; NO_CLEANUP = must-fail; SCRAMBLED = learned-not-free must-fire control; FLAT_* = the baseline to
#   beat on held-out (must collapse for the systematicity claim to have teeth).
# - positive_control: qualitative ordering (MEMORYLESS floor < traversal; NO_CLEANUP collapses; B=1 traversal ==
#   greedy in the self-test isolation). NOTE: config is LIGHTER than b1 FULL (CPU foreground), so exact b1 numeric
#   anchors are NOT asserted; the CG claim is SELF-CALIBRATED within-run.
# - sweep axis: compound_divergence div in {0.0,0.34,0.67,1.0}; EXPECTED_N_UNITS = n_seeds; each seed asserted to
#   produce all arms x all div levels (arm/div-cardinality check).
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate. GAMMA (=b1 GOAL_GAMMA 1.5, held IDENTICAL to greedy so
#   not a tuned knob) + BEAM_WIDTH (=12, b1) are PRE-REGISTERED, NOT tuned on real data. The self-test verifies
#   B=1 reproduces greedy AND flat collapses on a planted held-out compound while traversal holds.
# - no_global_T_matrix (LOAD-BEARING FAIRNESS GUARD): traversal reads ONLY the [n+1, Dmax] local typed-edge table.
#   Machine-checked: assert nbr_idx.shape[1] < n_nodes; record no_global_T_matrix_confirmed.
# - PAIRED trials: all arms share identical codes + roles + seeds + graph + DBCA split + per-div test set.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-epoch/per-seed/per-div flush prints).
# - defensive_error_checking: start_marker + crash_diagnostic + per-seed failure-class + heartbeat (encoder).
# - F.5 nondeterminism: all RNG via np.random.default_rng(fixed int); set ordering via sorted(); no salted-builtin
#   seeding and no set-to-list dedup ordering. (queue_add static scan enforces.)
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
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    char_trigram_features,
)
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import (  # noqa: E402
    SUBGRAPH_BASE_SEED,
)
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph,
    make_unitary_roles,
)
from experiments.exp_grounding_multihop_perhop_cleanup_gate_v1 import (  # noqa: E402
    train_binding_encoder_dev,
    sample_chains,
    build_typed_diradj,
    _hrr_bind_t,
    _l2t,
)
from experiments.exp_grounding_multihop_fair_test_unique_successor_goal_v1 import (  # noqa: E402
    build_nbr_table,
    build_ksr,
    run_chain_arm as ft_run_chain_arm,
    run_no_cleanup as ft_run_no_cleanup,
    MEMORYLESS as FT_MEMORYLESS,
)
from experiments.exp_grounding_multihop_autonomous_subgoal_greedy_v1 import (  # noqa: E402
    run_autonomous_arm as run_greedy_arm,
)
# Reuse b1's beam-rollout traversal + content-scramble derangement + planted mechanism sets VERBATIM.
from experiments.exp_grounding_multihop_generative_replay_traversal_v1 import (  # noqa: E402
    run_beam_traversal_arm,
    _derangement,
    _plant_trap_set,
    _plant_relation_essential_set,
    GAMMA as B1_GAMMA,
    BEAM_WIDTH as B1_BEAM_WIDTH,
)

ANCHOR_NAME = "grounding_cg_compound_divergence_flat_vs_traversal_v1"

MAX_REACH = 2         # 2-hop compounds (the CG claim is at reach@2 = novel relation-bigram combinations)
HIT_K = 10
GAMMA = B1_GAMMA          # 1.5; IDENTICAL to greedy AUTO_GAMMA (held constant -> ONE VARIABLE = learner)
BEAM_WIDTH = B1_BEAM_WIDTH  # 12; b1 beam width

# Arm names
NO_CLEANUP = "NO_CLEANUP"
MEMORYLESS = "MEMORYLESS"
FLAT_NN = "FLAT_NN"
FLAT_ASSOC = "FLAT_ASSOC"
AUTONOMOUS_GREEDY = "AUTONOMOUS_GREEDY"
REPLAY_TRAVERSAL = "REPLAY_TRAVERSAL"
REPLAY_TRAVERSAL_SCRAMBLED = "REPLAY_TRAVERSAL_SCRAMBLED"
ALL_ARMS = [NO_CLEANUP, MEMORYLESS, FLAT_NN, FLAT_ASSOC, AUTONOMOUS_GREEDY,
            REPLAY_TRAVERSAL, REPLAY_TRAVERSAL_SCRAMBLED]
# div-swept arms (their reach@2 depends on the test compound composition)
SWEEP_ARMS = [FLAT_NN, FLAT_ASSOC, AUTONOMOUS_GREEDY, REPLAY_TRAVERSAL, REPLAY_TRAVERSAL_SCRAMBLED]

DIV_LEVELS = [0.0, 0.34, 0.67, 1.0]
DIV_LO = 0.0
DIV_HI = 1.0

# ---------------------------------------------------------------------------
# Pre-registered CG bands (picked BEFORE the run; self-calibrated to within-run div0/div1 anchors).
# ---------------------------------------------------------------------------
WIDEN_MIN = 0.06        # HARD_PASS: margin(div1) - margin(div0) >= this (systematicity gap widens with divergence)
MARGIN_HI_MIN = 0.08    # HARD_PASS: traversal@2 - flat@2 at div1 >= this (traversal clearly beats flat on held-out)
FLAT_DROP_MIN = 0.06    # flat_collapses: flat@2(div0) - flat@2(div1) >= this (flat memorizer degrades on held-out)
TRAV_HOLD_TOL = 0.05    # traversal_holds: traversal@2(div0) - traversal@2(div1) <= this (traversal does not collapse)
TRAV_COLLAPSE = 0.10    # HARD_FAIL: traversal@2(div0) - traversal@2(div1) >= this (traversal itself collapses)
CONTENT_DEP_MIN = 0.06  # HARD_PASS: (traversal@2 - scrambled@2) at div1 >= this (learned/relation-dependent win)
WIDEN_FAIL = 0.02       # HARD_FAIL: widen <= this AND margin(div1) small (flat ties traversal on held-out)

# Smoke discriminator-fires gate (DISCRIMINATOR-MUST-SURVIVE-SCALE): abort FULL if the systematicity signal is
# absent at smoke. Require the gap to already widen and flat to drop.
SMOKE_WIDEN = 0.03
SMOKE_MARGIN_HI = 0.05

# anti-saturation / floor gates
BASE_COLLAPSE_ABS = 0.12
BASE_COLLAPSE_FRAC = 0.55
BASE_IN_BAND_HI = 0.95
HOP1_PRESENT = 0.08
MM_FIRES_MIN = 0.05     # traversal@2(div1) >= memoryless@2 + this (graph traversal beats the non-graph floor)
FLAT_ABOVE_FLOOR = 0.03  # flat@2(div0) >= memoryless@2 + this (flat is a REAL baseline, not the floor)

MIN_BG_COUNT = 6        # min chains per bigram to be split-eligible
HELDOUT_FRAC = 0.5      # cap on fraction of eligible bigrams removed to H
TRAIN_FRAC_SEEN = 0.8   # of non-held-out chains, fraction used as flat TRAIN (rest = seen-compound test pool)
LC_KFRACS = [0.25, 0.5, 1.0]  # FLAT_ASSOC learning-curve exposure fractions


def _resolve_device(arg_device):
    if arg_device == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Config profiles. SMOKE exercises the SAME arms / same code path as FULL; only scale differs. FULL is sized to
# complete in the foreground on CPU (no cuda locally).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(seeds=[7], n_nodes=400, epochs=10, batch=256, code_dim=128, feat_dim=1024,
                    temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                    n_chains=500, chain_chunk=256, test_size=120)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1500, epochs=50, batch=256, code_dim=384, feat_dim=3072,
                 temp=0.15, lr=0.01, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                 n_chains=1800, chain_chunk=256, test_size=350)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=2600, epochs=70, batch=384, code_dim=768, feat_dim=4096,
                temp=0.12, lr=0.009, lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0,
                n_chains=3000, chain_chunk=256, test_size=500)


# ---------------------------------------------------------------------------
# Chain-slice helper: subset (start, targets[L], role_ids[L]) by index array.
# ---------------------------------------------------------------------------

def _slice_chains(start, targets, role_ids, idx):
    idx = np.asarray(idx, dtype=np.int64)
    return (start[idx], [t[idx] for t in targets], [r[idx] for r in role_ids])


def _compound_role(role_ids, idx, roles_t, depth, device):
    """Per-chain compound relation role = product-bind of the first `depth` relation roles. [len(idx), d]."""
    idx = np.asarray(idx, dtype=np.int64)
    cr = roles_t[torch.from_numpy(role_ids[0][idx]).to(device)]
    for h in range(1, depth):
        cr = _hrr_bind_t(cr, roles_t[torch.from_numpy(role_ids[h][idx]).to(device)])
    return _l2t(cr)


# ---------------------------------------------------------------------------
# DBCA compound-divergence split. Atom = relation type; compound = 2-hop relation bigram (r1,r2).
# TRAIN (fixed) = chains whose bigram is NOT in the held-out set H (H chosen to preserve atom coverage). Sweep
# div = fraction of the TEST set drawn from held-out (train-disjoint) bigrams.
# ---------------------------------------------------------------------------

def build_dbca_split(role_ids, C, T, rng, heldout_frac=HELDOUT_FRAC, min_bg_count=MIN_BG_COUNT,
                     train_frac_seen=TRAIN_FRAC_SEEN):
    bg = [(int(role_ids[0][i]), int(role_ids[1][i])) for i in range(C)]
    idx_by_bg = defaultdict(list)
    for i, b in enumerate(bg):
        idx_by_bg[b].append(i)
    eligible = sorted([b for b, ix in idx_by_bg.items() if len(ix) >= min_bg_count])
    if len(eligible) < 4:
        return dict(status="too_sparse", n_eligible_bigrams=len(eligible))

    atoms0 = sorted(set(b[0] for b in eligible))
    atoms1 = sorted(set(b[1] for b in eligible))

    def covered(train_list):
        p0 = set(b[0] for b in train_list)
        p1 = set(b[1] for b in train_list)
        return set(atoms0).issubset(p0) and set(atoms1).issubset(p1)

    order = list(eligible)
    rng.shuffle(order)
    H = set()
    cap = int(heldout_frac * len(eligible))
    for b in order:
        if len(H) >= cap:
            break
        cand_H = H | {b}
        train_list = [x for x in eligible if x not in cand_H]
        if train_list and covered(train_list):
            H = cand_H
    H = set(sorted(H))
    if len(H) == 0:
        return dict(status="no_heldout", n_eligible_bigrams=len(eligible))

    heldout_pool = [i for i in range(C) if bg[i] in H]
    non_h = [i for i in range(C) if bg[i] not in H]
    rng.shuffle(non_h)
    n_train = int(train_frac_seen * len(non_h))
    train_idx = non_h[:n_train]
    train_bg_set = set(sorted(bg[i] for i in train_idx))
    # seen-compound test pool: non-train chains whose bigram IS in train (genuinely "seen" compounds)
    seen_test_pool = [i for i in non_h[n_train:] if bg[i] in train_bg_set]
    # held-out pool: chains whose bigram is in H (guaranteed NOT in train_bg_set)
    heldout_pool = [i for i in heldout_pool if bg[i] not in train_bg_set]

    # atom_divergence over the union of test pools: fraction of test relation-atoms not in train atoms
    train_atoms = set(b[0] for b in train_bg_set) | set(b[1] for b in train_bg_set)
    test_pool_all = seen_test_pool + heldout_pool
    test_atoms = set()
    for i in test_pool_all:
        test_atoms.add(bg[i][0])
        test_atoms.add(bg[i][1])
    atom_div = (len(test_atoms - train_atoms) / max(1, len(test_atoms)))

    return dict(status="ok", bg=bg, H=sorted(H), train_idx=train_idx, seen_test_pool=seen_test_pool,
                heldout_pool=heldout_pool, train_bg_set=train_bg_set,
                n_eligible_bigrams=len(eligible), n_heldout_bigrams=len(H),
                n_train=len(train_idx), n_seen_pool=len(seen_test_pool), n_heldout_pool=len(heldout_pool),
                atom_divergence=float(atom_div), n_train_atoms=len(train_atoms), n_test_atoms=len(test_atoms))


def make_test_set(div, split, size, rng):
    """Compose a size-`size` test set: div fraction from held-out compounds + (1-div) from seen compounds."""
    heldout_pool = list(split["heldout_pool"])
    seen_pool = list(split["seen_test_pool"])
    n_h = int(round(div * size))
    n_s = size - n_h
    n_h = min(n_h, len(heldout_pool))
    n_s = min(n_s, len(seen_pool))
    te = []
    if n_h > 0:
        te += [int(x) for x in rng.choice(heldout_pool, size=n_h, replace=False)]
    if n_s > 0:
        te += [int(x) for x in rng.choice(seen_pool, size=n_s, replace=False)]
    te = np.asarray(sorted(te), dtype=np.int64)
    bg = split["bg"]
    train_bg = split["train_bg_set"]
    actual_div = float(np.mean([bg[i] not in train_bg for i in te])) if te.shape[0] > 0 else float("nan")
    return te, actual_div, int(n_h), int(n_s)


# ---------------------------------------------------------------------------
# FLAT arms (non-compositional learned memorizers). Direct start -> depth-2 terminal, NO per-hop composition,
# NO graph traversal. reach@2 = top-1 predicted terminal == true terminal.
# ---------------------------------------------------------------------------

def run_flat_nn_arm(Z, tr_start, tr_role, tr_tgt2, te_start, te_role, te_tgt2, device):
    """1-NN memorizer keyed on (compound c=(r1,r2), start-code). For a test chain, retrieve the terminal of the
    nearest TRAIN start under the SAME compound; fall back to a GLOBAL nearest train start if compound unseen."""
    n_tr = int(tr_start.shape[0])
    Ztr = Z[torch.from_numpy(tr_start).to(device)]         # [n_tr, d] (L2-normed)
    tr_c = [(int(tr_role[0][i]), int(tr_role[1][i])) for i in range(n_tr)]
    by_c = defaultdict(list)
    for i, c in enumerate(tr_c):
        by_c[c].append(i)
    n_te = int(te_start.shape[0])
    Zte = Z[torch.from_numpy(te_start).to(device)]         # [n_te, d]
    te_c = [(int(te_role[0][i]), int(te_role[1][i])) for i in range(n_te)]
    tr_tgt2_t = torch.from_numpy(np.asarray(tr_tgt2, dtype=np.int64)).to(device)
    te_tgt2_t = torch.from_numpy(np.asarray(te_tgt2, dtype=np.int64)).to(device)
    pred = torch.full((n_te,), -1, dtype=torch.long, device=device)
    # group test by compound for batched NN
    te_by_c = defaultdict(list)
    for j, c in enumerate(te_c):
        te_by_c[c].append(j)
    for c in sorted(te_by_c.keys()):
        js = torch.tensor(te_by_c[c], dtype=torch.long, device=device)
        q = Zte[js]                                        # [m, d]
        if c in by_c:
            rows = torch.tensor(by_c[c], dtype=torch.long, device=device)
        else:
            rows = torch.arange(n_tr, dtype=torch.long, device=device)  # global fallback (wrong compound)
        cand = Ztr[rows]                                   # [g, d]
        sims = q @ cand.t()                                # [m, g]
        nn = sims.argmax(dim=1)                            # [m]
        pred[js] = tr_tgt2_t[rows[nn]]
    reach2 = float((pred == te_tgt2_t).float().mean().item())
    sig = hashlib.sha256(pred.detach().to("cpu").numpy().astype(np.int64).tobytes()).hexdigest()
    return reach2, sig


def run_flat_assoc_arm(Z, roles_t, tr_start, tr_role, tr_tgt2, te_start, te_role, te_tgt2, device,
                       n_nodes, depth=2, k_frac=1.0, rng=None):
    """Learned LINEAR associator W = Ktr^T Gtr mapping key=l2(bind(compound_role, Z[start])) -> Z[terminal].
    Direct start->terminal recall (no waypoint). k_frac subsamples train rows (learning curve)."""
    n_tr = int(tr_start.shape[0])
    if k_frac < 1.0:
        if rng is None:
            rng = np.random.default_rng(0)
        keep = rng.choice(n_tr, size=max(1, int(k_frac * n_tr)), replace=False)
        keep = np.asarray(sorted(int(x) for x in keep), dtype=np.int64)
    else:
        keep = np.arange(n_tr, dtype=np.int64)
    tr_start_k = tr_start[keep]
    tr_role_k = [r[keep] for r in tr_role]
    tr_tgt2_k = np.asarray(tr_tgt2, dtype=np.int64)[keep]

    cr_tr = _compound_role(tr_role_k, np.arange(tr_start_k.shape[0]), roles_t, depth, device)
    Ktr = _l2t(_hrr_bind_t(cr_tr, Z[torch.from_numpy(tr_start_k).to(device)]))   # [n_tr_k, d]
    Gtr = Z[torch.from_numpy(tr_tgt2_k).to(device)]                              # [n_tr_k, d]
    W = Ktr.t() @ Gtr                                                            # [d, d]

    cr_te = _compound_role(te_role, np.arange(te_start.shape[0]), roles_t, depth, device)
    Kte = _l2t(_hrr_bind_t(cr_te, Z[torch.from_numpy(te_start).to(device)]))     # [n_te, d]
    pred = _l2t(Kte @ W)                                                         # [n_te, d]
    score = pred @ Z.t()                                                         # [n_te, n]
    committed = score.argmax(dim=1)                                             # [n_te]
    te_tgt2_t = torch.from_numpy(np.asarray(te_tgt2, dtype=np.int64)).to(device)
    reach2 = float((committed == te_tgt2_t).float().mean().item())
    sig = hashlib.sha256(committed.detach().to("cpu").numpy().astype(np.int64).tobytes()).hexdigest()
    return reach2, sig


# ---------------------------------------------------------------------------
# Per-seed run: train encoder ONCE, build DBCA split, sweep div, run all arms per div (paired test set).
# ---------------------------------------------------------------------------

def run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
             T, cfg, device, out_dir=None):
    n_nodes = len(node_words)
    chunk = cfg["chain_chunk"]
    depth = MAX_REACH
    X = char_trigram_features(node_words, cfg["feat_dim"])
    Z = train_binding_encoder_dev(X, edges, rels, roles_t, cfg, seed, device, out_dir=out_dir, tag="BIND_cgcd")
    enc_dig = hashlib.sha256(Z.detach().to("cpu").numpy().astype(np.float32).tobytes()).hexdigest()
    Zp = torch.cat([Z, torch.zeros(1, cfg["code_dim"], device=device)], dim=0)

    scr_perm = _derangement(T, np.random.default_rng(seed + 4242))
    roles_scr = roles_t[torch.from_numpy(scr_perm).to(device)]

    # sample a large chain pool (L=depth), then build the DBCA split
    pool_rng = np.random.default_rng(seed + 909)
    p_start, p_targets, p_role = sample_chains(dir_adj, cfg["n_chains"], depth, pool_rng)
    C = int(p_start.shape[0])
    split = build_dbca_split(p_role, C, T, np.random.default_rng(seed + 5150))
    if split["status"] != "ok":
        return dict(seed=seed, split_status=split["status"], split=split, arms={}, per_div={},
                    encoder_digest=enc_dig)
    split["bg"] = split["bg"]  # keep
    _log("  seed=%d DBCA split: eligible_bg=%d heldout_bg=%d train=%d seen_pool=%d heldout_pool=%d atom_div=%.3f" % (
        seed, split["n_eligible_bigrams"], split["n_heldout_bigrams"], split["n_train"],
        split["n_seen_pool"], split["n_heldout_pool"], split["atom_divergence"]))

    tr_idx = np.asarray(split["train_idx"], dtype=np.int64)
    tr_start, tr_targets, tr_role = _slice_chains(p_start, p_targets, p_role, tr_idx)
    tr_tgt2 = tr_targets[depth - 1]

    ts_rng = np.random.default_rng(seed + 71717)
    per_div = {}
    arm_sigs_div1 = {}
    for div in DIV_LEVELS:
        te_idx, actual_div, n_h, n_s = make_test_set(div, split, cfg["test_size"], ts_rng)
        if te_idx.shape[0] < 40:
            per_div[str(div)] = dict(status="insufficient_test", n_test=int(te_idx.shape[0]))
            continue
        te_start, te_targets, te_role = _slice_chains(p_start, p_targets, p_role, te_idx)
        te_tgt2 = te_targets[depth - 1]

        arms = {}
        sigs = {}
        # compositional arms (compound-agnostic): greedy, traversal, scrambled
        rg, _hg, sg, _vg = run_greedy_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, te_start, te_targets, te_role,
                                          device, chunk, n_nodes, GAMMA, verify=False)
        arms[AUTONOMOUS_GREEDY] = {d: rg[d] for d in range(1, depth + 1)}; sigs[AUTONOMOUS_GREEDY] = sg
        rt, _ht, st, _stt = run_beam_traversal_arm(Z, Zp, roles_t, nbr_idx, nbr_mask, te_start, te_targets, te_role,
                                                   device, chunk, n_nodes, GAMMA, BEAM_WIDTH)
        arms[REPLAY_TRAVERSAL] = {d: rt[d] for d in range(1, depth + 1)}; sigs[REPLAY_TRAVERSAL] = st
        rs, _hs, ss, _sst = run_beam_traversal_arm(Z, Zp, roles_scr, nbr_idx, nbr_mask, te_start, te_targets,
                                                   te_role, device, chunk, n_nodes, GAMMA, BEAM_WIDTH)
        arms[REPLAY_TRAVERSAL_SCRAMBLED] = {d: rs[d] for d in range(1, depth + 1)}; sigs[REPLAY_TRAVERSAL_SCRAMBLED] = ss
        # flat arms (trained on the FIXED train set; evaluated on this div's test set)
        fnn2, sfnn = run_flat_nn_arm(Z, tr_start, tr_role, tr_tgt2, te_start, te_role, te_tgt2, device)
        arms[FLAT_NN] = {2: fnn2}; sigs[FLAT_NN] = sfnn
        fas2, sfas = run_flat_assoc_arm(Z, roles_t, tr_start, tr_role, tr_tgt2, te_start, te_role, te_tgt2,
                                        device, n_nodes, depth=depth, k_frac=1.0)
        arms[FLAT_ASSOC] = {2: fas2}; sigs[FLAT_ASSOC] = sfas
        # floor / must-fail arms on this test set (compound-agnostic; used for anti-sat + MM-fires at div1)
        rmem, _hm, _sm, smem = ft_run_chain_arm(FT_MEMORYLESS, Z, Zp, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                                                te_start, te_targets, te_role, device, chunk, n_nodes)
        arms[MEMORYLESS] = {d: rmem[d] for d in range(1, depth + 1)}; sigs[MEMORYLESS] = smem
        rnc, _hnc, _snc, snc = ft_run_no_cleanup(Z, roles_t, te_start, te_targets, te_role, device, n_nodes)
        arms[NO_CLEANUP] = {d: rnc[d] for d in range(1, depth + 1)}; sigs[NO_CLEANUP] = snc

        per_div[str(div)] = dict(status="ok", div=div, actual_div=actual_div, n_test=int(te_idx.shape[0]),
                                 n_heldout=n_h, n_seen=n_s, arms=arms)
        if abs(div - DIV_HI) < 1e-9:
            arm_sigs_div1 = sigs
        _log("  seed=%d div=%.2f (actual=%.2f nT=%d h=%d s=%d) flat_nn@2=%.3f flat_as@2=%.3f greedy@2=%.3f "
             "traversal@2=%.3f scrambled@2=%.3f mem@2=%.3f nc@2=%.3f" % (
                 seed, div, actual_div, te_idx.shape[0], n_h, n_s, fnn2, fas2, rg[2], rt[2], rs[2], rmem[2], rnc[2]))

    # ---- learning curve: FLAT_ASSOC held-out (div=1) + seen (div=0) reach@2 vs train exposure ----
    lc = dict(kfracs=LC_KFRACS, heldout={}, seen={})
    lc_rng = np.random.default_rng(seed + 30303)
    for tag, dv in (("heldout", DIV_HI), ("seen", DIV_LO)):
        te_idx, _ad, _nh, _ns = make_test_set(dv, split, cfg["test_size"], np.random.default_rng(seed + 40404))
        if te_idx.shape[0] < 40:
            continue
        te_start2, te_targets2, te_role2 = _slice_chains(p_start, p_targets, p_role, te_idx)
        te_tgt2b = te_targets2[depth - 1]
        for kf in LC_KFRACS:
            r2, _s = run_flat_assoc_arm(Z, roles_t, tr_start, tr_role, tr_tgt2, te_start2, te_role2, te_tgt2b,
                                        device, n_nodes, depth=depth, k_frac=kf,
                                        rng=np.random.default_rng(seed + int(1000 * kf)))
            lc[tag][str(kf)] = float(r2)

    return dict(seed=seed, split_status="ok", split={k: split[k] for k in (
        "H", "n_eligible_bigrams", "n_heldout_bigrams", "n_train", "n_seen_pool", "n_heldout_pool",
        "atom_divergence", "n_train_atoms", "n_test_atoms")},
        per_div=per_div, arm_sigs_div1=arm_sigs_div1, learning_curve=lc,
        encoder_digest=enc_dig, scr_perm=scr_perm.tolist(), code_dim=cfg["code_dim"])


# ---------------------------------------------------------------------------
# Aggregate + CG verdict
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _arm_at(per_seed, div, arm, d=2):
    key = str(div)
    vals = []
    for m in per_seed:
        pv = m.get("per_div", {}).get(key)
        if pv and pv.get("status") == "ok" and arm in pv["arms"] and d in pv["arms"][arm]:
            vals.append(pv["arms"][arm][d])
    return _nm(vals)


def aggregate_and_verdict(per_seed, meta, cfg, no_T_matrix):
    ok_seeds = [m for m in per_seed if m.get("split_status") == "ok"]
    if not ok_seeds:
        vm = "INCONCLUSIVE_SPLIT_TOO_SPARSE: no seed produced a valid DBCA split (statuses=%s)" % (
            [m.get("split_status") for m in per_seed])
        return "INCONCLUSIVE_SPLIT_TOO_SPARSE", vm, dict(verdict="INCONCLUSIVE_SPLIT_TOO_SPARSE")

    # per-div arm reach@2 (mean over seeds)
    trav = {dv: _arm_at(ok_seeds, dv, REPLAY_TRAVERSAL, 2) for dv in DIV_LEVELS}
    greedy = {dv: _arm_at(ok_seeds, dv, AUTONOMOUS_GREEDY, 2) for dv in DIV_LEVELS}
    scr = {dv: _arm_at(ok_seeds, dv, REPLAY_TRAVERSAL_SCRAMBLED, 2) for dv in DIV_LEVELS}
    fnn = {dv: _arm_at(ok_seeds, dv, FLAT_NN, 2) for dv in DIV_LEVELS}
    fas = {dv: _arm_at(ok_seeds, dv, FLAT_ASSOC, 2) for dv in DIV_LEVELS}
    mem = {dv: _arm_at(ok_seeds, dv, MEMORYLESS, 2) for dv in DIV_LEVELS}
    nc = {dv: _arm_at(ok_seeds, dv, NO_CLEANUP, 2) for dv in DIV_LEVELS}
    mem1 = _arm_at(ok_seeds, DIV_HI, MEMORYLESS, 1)
    nc1 = _arm_at(ok_seeds, DIV_HI, NO_CLEANUP, 1)

    # PRIMARY flat = FLAT_NN (sharper, unambiguous memorizer collapse). FLAT_ASSOC reported alongside.
    flat = fnn
    flat_lo = flat[DIV_LO]; flat_hi = flat[DIV_HI]
    trav_lo = trav[DIV_LO]; trav_hi = trav[DIV_HI]
    margin_lo = (trav_lo - flat_lo) if (trav_lo == trav_lo and flat_lo == flat_lo) else float("nan")
    margin_hi = (trav_hi - flat_hi) if (trav_hi == trav_hi and flat_hi == flat_hi) else float("nan")
    widen = (margin_hi - margin_lo) if (margin_hi == margin_hi and margin_lo == margin_lo) else float("nan")
    flat_drop = (flat_lo - flat_hi) if (flat_lo == flat_lo and flat_hi == flat_hi) else float("nan")
    trav_drop = (trav_lo - trav_hi) if (trav_lo == trav_lo and trav_hi == trav_hi) else float("nan")
    content_dep = (trav_hi - scr[DIV_HI]) if (trav_hi == trav_hi and scr[DIV_HI] == scr[DIV_HI]) else float("nan")

    # gates
    hop1_present = bool(mem1 == mem1 and mem1 >= HOP1_PRESENT)
    baseline_in_band = bool(mem1 == mem1 and 0.05 < mem1 < BASE_IN_BAND_HI)
    baseline_collapses = bool(nc1 == nc1 and nc[DIV_HI] == nc[DIV_HI]
                              and nc[DIV_HI] <= BASE_COLLAPSE_ABS
                              and nc[DIV_HI] <= BASE_COLLAPSE_FRAC * max(nc1, 1e-9))
    mm_fires = bool(trav_hi == trav_hi and mem[DIV_HI] == mem[DIV_HI] and trav_hi >= mem[DIV_HI] + MM_FIRES_MIN)
    flat_in_band = bool(flat_lo == flat_lo and mem[DIV_LO] == mem[DIV_LO]
                        and flat_lo >= mem[DIV_LO] + FLAT_ABOVE_FLOOR)

    flat_collapses = bool(flat_drop == flat_drop and flat_drop >= FLAT_DROP_MIN)
    traversal_holds = bool(trav_drop == trav_drop and trav_drop <= TRAV_HOLD_TOL)
    traversal_collapses = bool(trav_drop == trav_drop and trav_drop >= TRAV_COLLAPSE)
    content_dep_fires = bool(content_dep == content_dep and content_dep >= CONTENT_DEP_MIN)
    free_algebra_signature = bool(content_dep == content_dep and content_dep <= 0.0)
    widen_ok = bool(widen == widen and widen >= WIDEN_MIN)
    margin_hi_ok = bool(margin_hi == margin_hi and margin_hi >= MARGIN_HI_MIN)
    no_widening = bool(widen == widen and widen <= WIDEN_FAIL and (not margin_hi_ok))

    cg_hard_pass = bool(flat_in_band and flat_collapses and traversal_holds and widen_ok and margin_hi_ok
                        and content_dep_fires and no_T_matrix)
    cosmetic = bool(widen_ok and margin_hi_ok and flat_collapses and not content_dep_fires)

    if not no_T_matrix:
        verdict = "INCONCLUSIVE_T_MATRIX_LEAK"
    elif not hop1_present:
        verdict = "INCONCLUSIVE_HOP1_ABSENT"
    elif not baseline_collapses:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_FAIL"
    elif not mm_fires:
        verdict = "INCONCLUSIVE_MM_DID_NOT_FIRE"
    elif not flat_in_band:
        verdict = "MIDDLE_BAND_FLAT_BASELINE_VACUOUS"
    elif free_algebra_signature:
        verdict = "HARD_FAIL_CG_FREE_ALGEBRA_RANDOM_BEATS_REAL"
    elif traversal_collapses:
        verdict = "HARD_FAIL_CG_TRAVERSAL_COLLAPSES_ON_HELDOUT"
    elif cg_hard_pass:
        verdict = "HARD_PASS_CG_SYSTEMATICITY"
    elif no_widening:
        verdict = "HARD_FAIL_CG_NO_WIDENING_FLAT_TIES_TRAVERSAL"
    elif cosmetic:
        verdict = "MIDDLE_BAND_CG_COSMETIC_NOT_RELATIONAL"
    else:
        verdict = "MIDDLE_BAND_CG_PARTIAL"

    def dvs(dd):
        return "{%s}" % ",".join("%.2f:%.3f" % (k, dd[k]) for k in DIV_LEVELS)

    verdict_msg = (
        "%s || NO_CLEANUP@1=%.3f @2(div1)=%.3f(collapses=%s) || MEM@1=%.3f(in_band=%s) @2(div1)=%.3f || "
        "FLAT_NN@2 %s || FLAT_ASSOC@2 %s || GREEDY@2 %s || TRAVERSAL@2 %s || SCRAMBLED@2 %s || MEM@2 %s || "
        "CG: margin(div0)=%s margin(div1)=%s WIDEN=%s(>=%.2f=%s) flat_drop=%s(collapses=%s) trav_drop=%s"
        "(holds=%s,collapses=%s) content_dep=%s(fires=%s,free_alg=%s) mm_fires=%s flat_in_band=%s || "
        "HARD_PASS=%s cosmetic=%s || no_T_matrix=%s || B=%d gamma=%.2f nodes=%d E=%d rel=%d seeds=%d run=%s" % (
            verdict, nc1, nc[DIV_HI], baseline_collapses, mem1, baseline_in_band, mem[DIV_HI],
            dvs(fnn), dvs(fas), dvs(greedy), dvs(trav), dvs(scr), dvs(mem),
            _fmt(margin_lo), _fmt(margin_hi), _fmt(widen), WIDEN_MIN, widen_ok, _fmt(flat_drop), flat_collapses,
            _fmt(trav_drop), traversal_holds, traversal_collapses, _fmt(content_dep), content_dep_fires,
            free_algebra_signature, mm_fires, flat_in_band, cg_hard_pass, cosmetic, no_T_matrix,
            BEAM_WIDTH, GAMMA, meta["n_nodes"], meta["n_edges"], meta.get("n_relation_types", -1),
            len(ok_seeds), "full" if len(cfg["seeds"]) == 3 else "smoke"))

    # learning-curve aggregate
    lc_agg = dict(heldout={}, seen={})
    for kf in LC_KFRACS:
        lc_agg["heldout"][str(kf)] = _nm([m["learning_curve"]["heldout"].get(str(kf), float("nan"))
                                          for m in ok_seeds if "learning_curve" in m])
        lc_agg["seen"][str(kf)] = _nm([m["learning_curve"]["seen"].get(str(kf), float("nan"))
                                       for m in ok_seeds if "learning_curve" in m])

    gates = dict(
        verdict=verdict,
        reach_by_div=dict(
            FLAT_NN={str(k): fnn[k] for k in DIV_LEVELS}, FLAT_ASSOC={str(k): fas[k] for k in DIV_LEVELS},
            GREEDY={str(k): greedy[k] for k in DIV_LEVELS}, TRAVERSAL={str(k): trav[k] for k in DIV_LEVELS},
            SCRAMBLED={str(k): scr[k] for k in DIV_LEVELS}, MEMORYLESS={str(k): mem[k] for k in DIV_LEVELS},
            NO_CLEANUP={str(k): nc[k] for k in DIV_LEVELS}),
        cg=dict(primary_flat="FLAT_NN", margin_div0=margin_lo, margin_div1=margin_hi, widen=widen,
                flat_drop=flat_drop, trav_drop=trav_drop, content_dep=content_dep,
                flat_lo=flat_lo, flat_hi=flat_hi, trav_lo=trav_lo, trav_hi=trav_hi, scr_hi=scr[DIV_HI],
                flat_in_band=flat_in_band, flat_collapses=flat_collapses, traversal_holds=traversal_holds,
                traversal_collapses=traversal_collapses, content_dep_fires=content_dep_fires,
                free_algebra_signature=free_algebra_signature, widen_ok=widen_ok, margin_hi_ok=margin_hi_ok,
                cg_hard_pass=cg_hard_pass, cosmetic=cosmetic, no_widening=no_widening),
        anti_sat=dict(hop1_present=hop1_present, baseline_in_band=baseline_in_band,
                      baseline_collapses=baseline_collapses, mm_fires=mm_fires),
        no_global_T_matrix=dict(confirmed=no_T_matrix),
        learning_curve=lc_agg,
        split=dict(atom_divergence=_nm([m["split"]["atom_divergence"] for m in ok_seeds]),
                   n_heldout_bigrams=_nm([m["split"]["n_heldout_bigrams"] for m in ok_seeds]),
                   n_eligible_bigrams=_nm([m["split"]["n_eligible_bigrams"] for m in ok_seeds]),
                   n_train=_nm([m["split"]["n_train"] for m in ok_seeds])),
        bands=dict(WIDEN_MIN=WIDEN_MIN, MARGIN_HI_MIN=MARGIN_HI_MIN, FLAT_DROP_MIN=FLAT_DROP_MIN,
                   TRAV_HOLD_TOL=TRAV_HOLD_TOL, TRAV_COLLAPSE=TRAV_COLLAPSE, CONTENT_DEP_MIN=CONTENT_DEP_MIN,
                   WIDEN_FAIL=WIDEN_FAIL, MM_FIRES_MIN=MM_FIRES_MIN, FLAT_ABOVE_FLOOR=FLAT_ABOVE_FLOOR,
                   GAMMA=GAMMA, BEAM_WIDTH=BEAM_WIDTH, DIV_LEVELS=DIV_LEVELS),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism / discriminator self-test. Proves on PLANTED codes + REAL new machinery:
#  P1 (isolation): beam(B=1) reproduces GREEDY on the lookahead-trap set (ONE-VARIABLE exact; inherits b1).
#  P2 (mechanism): beam(B>1) beats greedy on the lookahead-trap set (inherits b1).
#  P3 (content-dep): scrambling roles collapses the beam on the relation-essential set (inherits b1).
#  P4 (no-T-matrix): local [n+1,Dmax] table, Dmax < n (inherits b1).
#  P_DBCA (the NEW machinery on a REAL code path): on a planted bind-consistent 2-hop multigraph with a HELD-OUT
#     relation-bigram, the DBCA split constructor yields atom_divergence~0 and compound_divergence(div1)~1,
#     FLAT_NN COLLAPSES on the held-out compound while REPLAY_TRAVERSAL HOLDS (systematicity), and all arms differ.
# ---------------------------------------------------------------------------

def _plant_bind_consistent_bigraph(device, d, T, roles_t, rng, n_start=300, n_r1=3, n_r2=3, n_decoy=2):
    """Planted 2-hop multigraph with bind-consistent codes: for edge u--r-->v, Z[v] ~ l2(bind(role_r, Z[u])).
    Distinct bigrams (r1,r2) so a DBCA split can hold out a bigram. Each hop also has n_decoy WRONG-relation decoy
    out-edges (Dmax>1) so the traversal must use relation-bind to pick the correct successor (non-trivial). Returns
    codes, dir_adj, chains, bigrams."""
    node_codes = [c for c in _l2t(torch.randn(n_start, d, device=device))]
    dir_adj = [[] for _ in range(n_start)]
    nid = n_start
    chain_start, chain_t1, chain_t2, chain_r1, chain_r2 = [], [], [], [], []

    def _add(vec, from_node, rel):
        nonlocal nid
        node_codes.append(_l2t(vec[None, :])[0])
        dir_adj.append([])
        new = nid
        nid += 1
        dir_adj[from_node].append((new, rel))
        return new

    for s in range(n_start):
        r1 = int(rng.integers(0, min(n_r1, T)))
        r2 = int(rng.integers(0, min(n_r2, T)))
        v1 = (_hrr_bind_t(roles_t[r1:r1 + 1], node_codes[s][None, :]))[0] + 0.05 * torch.randn(d, device=device)
        t1 = _add(v1, s, r1)
        for _k in range(n_decoy):
            rp = int((r1 + 1 + rng.integers(0, max(1, min(n_r1, T) - 1))) % min(n_r1, T))
            _add(torch.randn(d, device=device), s, rp)          # decoy under wrong relation
        v2 = (_hrr_bind_t(roles_t[r2:r2 + 1], node_codes[t1][None, :]))[0] + 0.05 * torch.randn(d, device=device)
        t2 = _add(v2, t1, r2)
        for _k in range(n_decoy):
            rp = int((r2 + 1 + rng.integers(0, max(1, min(n_r2, T) - 1))) % min(n_r2, T))
            _add(torch.randn(d, device=device), t1, rp)         # decoy under wrong relation
        chain_start.append(s); chain_t1.append(t1); chain_t2.append(t2); chain_r1.append(r1); chain_r2.append(r2)
    Z = _l2t(torch.stack(node_codes, dim=0))
    n = Z.shape[0]
    while len(dir_adj) < n:
        dir_adj.append([])
    start = np.asarray(chain_start, dtype=np.int64)
    targets = [np.asarray(chain_t1, dtype=np.int64), np.asarray(chain_t2, dtype=np.int64)]
    role_ids = [np.asarray(chain_r1, dtype=np.int64), np.asarray(chain_r2, dtype=np.int64)]
    return Z, dir_adj, n, start, targets, role_ids


def _mechanism_selftest():
    device = torch.device("cpu")
    d = 96
    T = 6
    roles_t = torch.from_numpy(make_unitary_roles(T, d, np.random.default_rng(11))).to(device)

    # ---- P1 + P2 lookahead-trap (inherit b1) ----
    Zt, adj_t, nt, s_t, tg_t, rl_t = _plant_trap_set(device, d, T, roles_t, np.random.default_rng(1), 140)
    Zpt = torch.cat([Zt, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx_t, _nr, nbr_mask_t, Dmax_t, _mo = build_nbr_table(adj_t, nt, device)
    rg_t, _h, sg_t, _v = run_greedy_arm(Zt, Zpt, roles_t, nbr_idx_t, nbr_mask_t, s_t, tg_t, rl_t,
                                        device, 256, nt, GAMMA, verify=False)
    rb1_t, _h, sb1_t, _s = run_beam_traversal_arm(Zt, Zpt, roles_t, nbr_idx_t, nbr_mask_t, s_t, tg_t, rl_t,
                                                  device, 256, nt, GAMMA, 1)
    rbB_t, _h, sbB_t, _s = run_beam_traversal_arm(Zt, Zpt, roles_t, nbr_idx_t, nbr_mask_t, s_t, tg_t, rl_t,
                                                  device, 256, nt, GAMMA, BEAM_WIDTH)
    Lt = len(tg_t)
    isolation_ok = bool(all(abs(rb1_t[dd] - rg_t[dd]) <= 0.02 for dd in range(1, Lt + 1)))
    greedy_trapped = bool(rg_t[1] == rg_t[1] and rg_t[1] <= 0.35)
    beam_recovers = bool(rbB_t[1] == rbB_t[1] and rg_t[1] == rg_t[1]
                         and rbB_t[1] >= rg_t[1] + 0.30 and rbB_t[2] >= rg_t[2] + 0.30)

    # ---- P3 relation-essential (inherit b1) ----
    Zr, adj_r, nr, s_r, tg_r, rl_r = _plant_relation_essential_set(device, d, T, roles_t,
                                                                   np.random.default_rng(2), 140)
    Zpr = torch.cat([Zr, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx_r, _nr2, nbr_mask_r, Dmax_r, _mo2 = build_nbr_table(adj_r, nr, device)
    scr_perm = _derangement(T, np.random.default_rng(7))
    roles_scr = roles_t[torch.from_numpy(scr_perm).to(device)]
    rb_r, _h, sb_r, _s = run_beam_traversal_arm(Zr, Zpr, roles_t, nbr_idx_r, nbr_mask_r, s_r, tg_r, rl_r,
                                                device, 256, nr, GAMMA, BEAM_WIDTH)
    rsc_r, _h, ssc_r, _s = run_beam_traversal_arm(Zr, Zpr, roles_scr, nbr_idx_r, nbr_mask_r, s_r, tg_r, rl_r,
                                                  device, 256, nr, GAMMA, BEAM_WIDTH)
    traversal_relational = bool(rb_r[1] == rb_r[1] and rb_r[1] >= 0.60)
    scramble_collapses = bool(rsc_r[1] == rsc_r[1] and rb_r[1] == rb_r[1] and rsc_r[1] <= rb_r[1] - 0.25)

    # ---- P_DBCA: NEW machinery on a bind-consistent planted 2-hop multigraph ----
    Zb, adj_b, nb, sb, tgb, rlb = _plant_bind_consistent_bigraph(device, d, T, roles_t,
                                                                 np.random.default_rng(3),
                                                                 n_start=300, n_r1=3, n_r2=3, n_decoy=2)
    Zpb = torch.cat([Zb, torch.zeros(1, d, device=device)], dim=0)
    nbr_idx_b, _nrb, nbr_mask_b, Dmax_b, _mob = build_nbr_table(adj_b, nb, device)
    C = int(sb.shape[0])
    split = build_dbca_split(rlb, C, T, np.random.default_rng(4), heldout_frac=0.5, min_bg_count=3,
                             train_frac_seen=0.7)
    split_ok = bool(split.get("status") == "ok")
    dbca_atom_div_ok = bool(split_ok and split["atom_divergence"] <= 0.10)
    # ROBUST machinery assertions (not construction-dependent): (a) traversal generalizes to HELD-OUT compounds;
    # (b) the flat MEMORIZER (FLAT_NN) is beaten by traversal on held-out (cannot recombine to unseen compounds).
    trav_holds_pl = False
    flat_beaten_pl = False
    cd_ok = False
    fnn_held = float("nan")
    sfnn_h = sfas_h = st_h = ""
    if split_ok:
        tr_idx = np.asarray(split["train_idx"], dtype=np.int64)
        tr_start, tr_targets, tr_role = _slice_chains(sb, tgb, rlb, tr_idx)
        tr_tgt2 = tr_targets[1]
        rr = np.random.default_rng(5)
        te_seen, ad_s, _a, _b = make_test_set(0.0, split, 70, rr)
        te_held, ad_h, _c, _e = make_test_set(1.0, split, 70, rr)
        cd_ok = bool(ad_s <= 0.10 and ad_h >= 0.90)  # compound_divergence == div by construction
        if te_held.shape[0] >= 20:
            tes_h, tet_h, ter_h = _slice_chains(sb, tgb, rlb, te_held)
            fnn_held, sfnn_h = run_flat_nn_arm(Zb, tr_start, tr_role, tr_tgt2, tes_h, ter_h, tet_h[1], device)
            _fas_held, sfas_h = run_flat_assoc_arm(Zb, roles_t, tr_start, tr_role, tr_tgt2, tes_h, ter_h, tet_h[1],
                                                   device, nb, depth=2, k_frac=1.0)
            rt_held, _h2, st_h, _v2 = run_beam_traversal_arm(Zb, Zpb, roles_t, nbr_idx_b, nbr_mask_b,
                                                             tes_h, tet_h, ter_h, device, 256, nb, GAMMA, BEAM_WIDTH)
            trav_holds_pl = bool(rt_held[2] == rt_held[2] and rt_held[2] >= 0.55)   # compositional generalizes
            flat_beaten_pl = bool(rt_held[2] == rt_held[2] and fnn_held == fnn_held
                                  and rt_held[2] - fnn_held >= 0.20)                 # memorizer cannot recombine

    no_T_matrix = bool(int(nbr_idx_t.shape[1]) < nt and int(nbr_idx_r.shape[1]) < nr
                       and int(nbr_idx_b.shape[1]) < nb)
    # arms-differ from a guaranteed-distinct set (greedy-trapped != beam-recovers; scrambled; flat_nn; flat_assoc)
    arms_differ = bool(len(set([sg_t, sbB_t, ssc_r, sfnn_h, sfas_h]) - {""}) >= 4)

    res = dict(
        trap_greedy={dd: round(rg_t[dd], 4) for dd in range(1, Lt + 1)},
        trap_beam_B1={dd: round(rb1_t[dd], 4) for dd in range(1, Lt + 1)},
        trap_beam_B={dd: round(rbB_t[dd], 4) for dd in range(1, Lt + 1)},
        reless_traversal={dd: round(rb_r[dd], 4) for dd in range(1, len(tg_r) + 1)},
        reless_scrambled={dd: round(rsc_r[dd], 4) for dd in range(1, len(tg_r) + 1)},
        isolation_ok=isolation_ok, greedy_trapped=greedy_trapped, beam_recovers=beam_recovers,
        traversal_relational=traversal_relational, scramble_collapses=scramble_collapses,
        dbca_split_ok=split_ok, dbca_atom_div_ok=dbca_atom_div_ok, dbca_compound_div_ok=cd_ok,
        dbca_traversal_holds=trav_holds_pl, dbca_flat_beaten_heldout=flat_beaten_pl,
        dbca_fnn_held=round(fnn_held, 4) if fnn_held == fnn_held else None,
        no_T_matrix=no_T_matrix, arms_differ=arms_differ,
        Dmax_trap=int(Dmax_t), Dmax_reless=int(Dmax_r), Dmax_bigraph=int(Dmax_b),
    )
    ok = bool(isolation_ok and greedy_trapped and beam_recovers and traversal_relational
              and scramble_collapses and split_ok and dbca_atom_div_ok and cd_ok
              and trav_holds_pl and flat_beaten_pl and no_T_matrix and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    device = _resolve_device(args.device)
    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda_available=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _mechanism_selftest()
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s | rel_types=%d" % ({k: meta[k] for k in ("n_nodes", "n_edges", "median_degree")}, T))
    n_nodes = len(node_ids)
    dir_adj = build_typed_diradj(edges, rels, n_nodes)
    nbr_idx, nbr_rel, nbr_mask, Dmax, mean_out_deg = build_nbr_table(dir_adj, n_nodes, device)
    _ksr, has_rel = build_ksr(dir_adj, n_nodes, T, device)
    no_T_matrix = bool(int(nbr_idx.shape[1]) < n_nodes)
    _log("nbr table: Dmax=%d mean_out_deg=%.3f no_global_T_matrix=%s" % (Dmax, mean_out_deg, no_T_matrix))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["code_dim"], role_rng)).to(device)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS DBCA-CG machinery: B=1 reproduces greedy (isolation); beam beats greedy "
                        "(lookahead-trap); correct-role traversal recovers while scrambled collapses (content-dep); "
                        "DBCA split has atom_div~0 + compound_div(div1)~1; FLAT_NN collapses on held-out compound "
                        "while REPLAY_TRAVERSAL holds (systematicity); no [n,n] T-matrix; arms differ",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res, subgraph_meta=meta, no_global_T_matrix=no_T_matrix))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, node_words, edges, rels, dir_adj, roles_t, nbr_idx, nbr_rel, nbr_mask, has_rel,
                          T, cfg, device, out_dir=out_dir_path)
            if pm.get("split_status") != "ok":
                seed_failures.append(dict(seed=seed, failure_class="DBCA_SPLIT_%s" % pm.get("split_status"),
                                          msg="split not ok"))
                _log("SEED_SPLIT_FAILED seed=%d status=%s" % (seed, pm.get("split_status")))
                continue
            # arm/div cardinality
            for dv in DIV_LEVELS:
                pv = pm["per_div"].get(str(dv))
                if not pv or pv.get("status") != "ok":
                    raise RuntimeError("DIV_CARDINALITY_BREACH seed=%d div=%.2f status=%s" % (
                        seed, dv, (pv or {}).get("status")))
            # arms-differ (META_RULE_AF) at div1
            sigs = pm.get("arm_sigs_div1", {})
            pairs = [(REPLAY_TRAVERSAL, AUTONOMOUS_GREEDY), (REPLAY_TRAVERSAL, REPLAY_TRAVERSAL_SCRAMBLED),
                     (FLAT_NN, FLAT_ASSOC), (FLAT_NN, REPLAY_TRAVERSAL), (MEMORYLESS, NO_CLEANUP)]
            for a, b in pairs:
                if a in sigs and b in sigs and sigs[a] == sigs[b]:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d %s == %s" % (seed, a, b))
            per_seed.append(pm)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:  # per-seed failure-class instrumentation (META_RULE_J)
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (
                expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, meta, cfg, no_T_matrix)

    smoke_discriminator_fires = None
    if run_mode == "smoke":
        cg = gates.get("cg", {})
        widen = cg.get("widen", float("nan"))
        margin_hi = cg.get("margin_div1", float("nan"))
        smoke_discriminator_fires = bool(widen == widen and margin_hi == margin_hi
                                         and widen >= SMOKE_WIDEN and margin_hi >= SMOKE_MARGIN_HI)
        _log("SMOKE discriminator-fires (widen>=%.2f AND margin_div1>=%.2f): %s (widen=%s margin_div1=%s)" % (
            SMOKE_WIDEN, SMOKE_MARGIN_HI, smoke_discriminator_fires, _fmt(widen), _fmt(margin_hi)))

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        device=str(device), n_seeds=len(per_seed), seeds=cfg["seeds"], config=cfg,
        subgraph_meta=meta, gates=gates, no_global_T_matrix=no_T_matrix,
        smoke_discriminator_fires=smoke_discriminator_fires,
        mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
