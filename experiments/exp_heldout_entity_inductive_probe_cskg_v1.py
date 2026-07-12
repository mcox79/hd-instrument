"""DECISIVE held-out-ENTITY inductive probe (Anchor 1 of the does-it-scale hand-off, 2026-07-12).

THE generalize-vs-memorize falsifier. A cheap SCORING pass over already-fit-style codes (NO new corpus, NO new
infra): re-fit the CURRENT glass-box KGE arms (ONESHOT_ROTATE phase-rotation + ADDITIVE_TRANSE) on the SAME
CSKG-core graph the completed run used (build_cskg_core_triples, k_core=12 -> ~25.7k entities / 29 relations),
but under a HELD-OUT-ENTITY split: a fraction of entities is withheld from EVERY train edge, so their per-entity
phase/vector codes are NEVER updated (they stay at random init by construction). We then score queries whose GOLD
TAIL is a held-out entity (head seen) and ask: does the fitted geometry rank an ENTITY it never saw better than a
random-code control?

WHY THIS IS THE RIGHT TEST (vs the existing genuine-L2 harness). The genuine-L2 cell tests unseen EDGES between
KNOWN entities (composition) -- a weaker, different question. This tests transfer to entities ENTIRELY ABSENT from
train (true induction). The GraIL/NBFNet inductive-KGE line (CITED@notes research_does_it_scale_..._2026-07-12
HEADLINE 5) states as an ARCHITECTURAL FACT that a fixed per-entity embedding table (which BOTH ONESHOT_ROTATE and
ADDITIVE_TRANSE are) cannot represent an unseen entity at all -- there is no learned vector for it. This substrate
already ran the analogous test once on a structurally similar mechanism (SR reachability codes,
grounding_learned_sr_heldout_reasoning_v1, 3 seeds FULL 2026-07-10, HARD_FAIL: held-out reach@2 0.1148 vs
random-code 0.104, delta 0.011 < the 0.05 margin) -- memorized search, not reasoning. This cell re-runs that SAME
held-out-entity logic on the CURRENT rotation/additive fit.

MECHANISM (what differs per arm; all share the SAME held-out queries + candidate set = PAIRED):
  ONESHOT_ROTATE : rotation fit on BOTH-seen train edges; gold-tail held-out code stays random-init (the candidate).
  ADDITIVE_TRANSE: additive-TransE fit on the same both-seen train edges (functional-form head-to-head).
  RANDOM_CODES   : random phases + relations + same readout = the random-code control (the bar to clear by >=0.05).
  CODEALIAS      : fitted relation rotations THETA (trained) + RANDOM entity codes = necessity control (does the
                   trained relation-operator ALONE transfer to a random-coded unseen entity? for a per-entity table,
                   no). Reciprocal-necessity: if ONESHOT ~ CODEALIAS, the fitted entity geometry adds nothing on
                   held-out entities.
  ORACLE_TRANSDUCTIVE: the SAME rotation fit but with the held-out entities' edges FOLDED INTO the fit
                   (transductive_extra=hold) so the gold-tail codes ARE trained. This is the POSITIVE CONTROL /
                   validity-preflight: if ORACLE clears RANDOM by a fat margin on the SAME held-out queries, the
                   arena registers positive signal and the >=0.05 HARD-PASS bar is achievable-in-principle -> a null
                   ONESHOT/ADDITIVE result is a genuine "cannot induce," NOT a broken/underfit harness.
  BASELINE_POP   : frequency incumbent (memoryless). Held-out tails have train tail-freq 0 -> POP ~ floor. This is
                   the fit-independence sanity check: POP unaffected by the split confirms the split is genuinely
                   inductive, not a harness artifact.

PRE-REG BANDS (verbatim from the hand-off Anchor 1):
  HARD-PASS  : max(ONESHOT, ADDITIVE) held-out hits@10 clears RANDOM_CODES by >= 0.05 absolute (real transferable
               relational signal to genuinely unseen entities) -> the geometry generalizes; the inductive question
               is alive at scale.
  MIDDLE-BAND: 0.02 <= margin < 0.05 (weak but nonzero; flag for a second seed/split before declaring).
  HARD-FAIL  : margin < 0.02 (memorized search, not reasoning; replicates the SR-code HARD_FAIL). Deflated-prior
               expectation P=0.15-0.20.
Gated INCONCLUSIVE if the ORACLE positive control does NOT fire (arena not answerable -> cannot separate "no
induction" from "underfit"), if there are too few held-out queries, or if a control unexpectedly beats POP (broken).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes    : ORACLE_TRANSDUCTIVE clears RANDOM by the ORACLE_FIRE_MARGIN on held-out queries
                                   (the >=0.05 bar is provably achievable when the entity code IS learned).
  (2) metric_moves               : held-out hits@10 MOVES across [RANDOM, ONESHOT, ORACLE] (not structurally frozen).
  (3) negative_control_margin    : RANDOM_CODES + CODEALIAS sit below ORACLE by margin, deterministically (>=2 vals).
  (4) full_gates_exercised       : aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate.

## Compute architecture
class (c) MIXED: split construction + POP = sequential-CPU graph ops (no matmul); rotation/additive fits =
minibatch SGD (batched, neg-chunked on FULL); readouts = query-chunked batched matmul (the (nq,N) map is never
materialized whole). Storage SHARDED (each entity its own phase code; relations = per-TYPE rotations, no global
bundle). device=cpu on remote_cpu_queue (this is a scoring pass over re-fit codes; no GPU needed). FULL fits are
periodically fit-checkpointed (ckpt_every) so an outage/timeout resumes each arm from its last epoch -- outage-safe.

NOTE on re-fit vs the completed gpu1024 run: the completed course_c_rotate_cskg_l2_seed_17_gpu1024_v1 did NOT
persist loadable fit codes (only metrics.json on disk), so per the hand-off we RE-FIT cheaply on the same graph.
The embedding dim k=24 matches the completed FULL_CFG (the capacity-relevant knob); epochs/n_neg are moderated for
the CPU budget. The inductive metric is insensitive to seen-side fit sharpness (more epochs only sharpen SEEN
geometry; a held-out entity has no vector to sharpen), and the ORACLE positive control fires regardless -- so the
verdict is robust to the epochs/n_neg moderation. HYPOTHESIZED@this prereg (re-fit is faithful for the inductive
question); the completed run's own transductive numbers are CITED for context, not required to reproduce.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 5 arms produce >=4 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: chance hits@10 = 10/N ~ 0.0004 at N~25.7k. HARD-PASS 0.05-above-random is on the achievable side (the
#   ORACLE positive control demonstrates it when the code is learned). discriminator_reachability: OK.
# - baseline_in_band: the ORACLE positive control must fire in (RANDOM+margin, 1.0); RANDOM/POP near the 10/N floor.
# - discriminator survives scale: analytical (B) -- per-entity embedding tables cannot encode an unseen entity by
#   construction (GraIL/NBFNet), so the null persists at ANY N; the ORACLE-fires positive control proves the metric
#   can move at scale. Self-test fires the ORACLE-beats-RANDOM discriminator deterministically (single-thread CPU).
# - HARD-PASS strictly above floor: 0.05 clears HARD-FAIL 0.02 by 5%+ band-width; ORACLE margin adds strictness.
# - HP_SCOPE: the inductive HARD-PASS gate applies to ONESHOT_ROTATE / ADDITIVE_TRANSE only. ORACLE = positive
#   control (must fire); RANDOM/CODEALIAS = must-not-clear-bar controls; POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 5 arms + POP (arm cardinality).
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- HELDOUT_ENTITY_FRAC/ORACLE_FIRE_MARGIN pre-registered,
#   NOT tuned on real data; the planted self-test verifies ORACLE recovers held-out tails when codes ARE learned.
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
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits, PRIMARY_K,
)
from experiments._course_c_rotate_core_v1 import (  # noqa: E402
    fit_kge_rotate, rotate_direct_scores, additive_direct_scores,
    build_syn_dense_grid_composition, ROT_LR,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402

ANCHOR_NAME = "heldout_entity_inductive_probe_cskg_v1"

# ---- Arm names ----
ONESHOT = "ONESHOT_ROTATE"        # rotation fit on both-seen edges; gold-tail held-out code = random init
ADDITIVE = "ADDITIVE_TRANSE"      # additive-TransE fit (functional-form head-to-head)
RANDOM = "RANDOM_CODES"           # random-code control (the bar: clear this by >=0.05)
CODEALIAS = "CODEALIAS"           # fitted relations THETA + random entity codes (necessity control)
ORACLE = "ORACLE_TRANSDUCTIVE"    # positive control: held-out edges folded into the fit (codes learned)
POP = "BASELINE_POP"              # frequency incumbent (fit-independence sanity)
FIT_ARMS = [ONESHOT, ADDITIVE, RANDOM, CODEALIAS, ORACLE]   # 5 arms scored via the geometry readouts
ALL_ARMS = FIT_ARMS + [POP]

# ---- Pre-registered bands (hand-off Anchor 1, verbatim; picked BEFORE the run) ----
HARD_PASS_MARGIN = 0.05    # HARD-PASS: max(ONESHOT, ADDITIVE) hits@10 - RANDOM hits@10 >= this
MIDDLE_LO = 0.02           # MIDDLE-BAND floor: margin in [0.02, 0.05)
ORACLE_FIRE_MARGIN = 0.10  # positive control: ORACLE hits@10 - RANDOM hits@10 >= this (arena answerable)
CONTROL_LOSE_EPS = 0.03    # broken-test guard: a control (RANDOM/CODEALIAS) beating POP by > this = broken
MIN_HELDOUT = 20           # min held-out queries for a valid discriminator
PRIMARY_METRIC = "hits@%d" % PRIMARY_K   # PRIMARY_K = 10

# ---- Held-out-entity split knob (pre-registered; NOT tuned on real data) ----
HELDOUT_ENTITY_FRAC = 0.15   # fraction of entities withheld from EVERY train edge (codes never updated)

# ---- self-test planted thresholds ----
SELFTEST_ORACLE_MIN = 0.30   # planted grid: ORACLE recovers held-out tails (codes learned) to at least this h@10
SELFTEST_MIN_HO = 8          # planted grid: minimum held-out queries

SCORE_CHUNK = 256

# Config profiles. SELFTEST exercises the SAME split->fit->score->verdict path as FULL; only scale + corpus differ.
SELFTEST_CFG = dict(k=12, epochs=220, n_neg=32, batch=4096, heldout_entity_frac=0.15,
                    n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)
SMOKE_CFG = dict(k=16, epochs=60, n_neg=64, batch=8192, heldout_entity_frac=0.15,
                 cskg_max_lines=800000, k_core=3, cskg_max_nodes=3000,
                 n_heldout_eval=800, min_heldout=10, seeds=[7, 13])
# FULL: k=24 matches the completed gpu1024 FULL_CFG (capacity-relevant knob); epochs/n_neg moderated for CPU.
# neg_chunk bounds the (batch,n_neg,k) transient; ckpt_every makes each fit outage-resumable.
FULL_CFG = dict(k=24, epochs=200, n_neg=64, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
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
# Held-out-ENTITY split: withhold a fraction of entities from EVERY train edge.
# ---------------------------------------------------------------------------

def build_heldout_entity_split(pool_lbl, ent2i, frac, seed):
    """Withhold ~frac of entities. train = edges with BOTH endpoints SEEN; held-out queries = edges with the TAIL
    withheld AND the head SEEN (rank an unseen tail). Returns (train_lbl, held_lbl, heldout_ent_ids_set)."""
    n_ent = len(ent2i)
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(frac * n_ent))
    hold_ids = set(int(x) for x in rng.choice(n_ent, size=n_hold, replace=False))
    train_lbl, held_lbl = [], []
    for (h, r, t) in pool_lbl:
        hi = ent2i[h]; ti = ent2i[t]
        h_hold = hi in hold_ids
        t_hold = ti in hold_ids
        if not h_hold and not t_hold:
            train_lbl.append((h, r, t))
        elif t_hold and not h_hold:
            held_lbl.append((h, r, t))   # gold tail is an unseen entity, head is seen -> the inductive query
        # (edges with head withheld, or both withheld, are dropped: not scored, not trained)
    return train_lbl, held_lbl, hold_ids


# ---------------------------------------------------------------------------
# Fit the 5 geometry arms + POP; score PAIRED on the SAME held-out queries.
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score(train_int, hold, N, n_rel, cfg, device, seed, rel_tail_freq, all_true, ckpt_dir=None):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # ONESHOT_ROTATE: rotation fit on both-seen edges (held-out entity phases stay random init)
    PHI, THETA = fit_kge_rotate(train_int, N, n_rel, k, device, seed, epochs, lr=ROT_LR, n_neg=n_neg,
                                batch_size=batch, neg_chunk=neg_chunk,
                                ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "rotate_oneshot", seed))
    _ec()
    # ADDITIVE_TRANSE: same recipe, additive score
    Xa, Da = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=ROT_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive", seed))
    _ec()
    # ORACLE_TRANSDUCTIVE: fold held-out edges into the fit (gold-tail codes learned) = positive control
    PHIo, THETAo = fit_kge_rotate(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold,
                                  lr=ROT_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                                  ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "rotate_oracle", seed))
    _ec()
    # RANDOM_CODES: random phases + relations (the control bar)
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    two_pi = 2.0 * np.pi
    PHIr = ((torch.rand(N, k, generator=gR) * two_pi) - np.pi).to(device)
    THETAr = ((torch.rand(n_rel, k, generator=gR) * two_pi) - np.pi).to(device)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (ONESHOT, rotate_direct_scores(PHI, THETA, hold, device, chunk=SCORE_CHUNK)),
        (ADDITIVE, additive_direct_scores(Xa, Da, hold, device, chunk=SCORE_CHUNK)),
        (ORACLE, rotate_direct_scores(PHIo, THETAo, hold, device, chunk=SCORE_CHUNK)),
        (RANDOM, rotate_direct_scores(PHIr, THETAr, hold, device, chunk=SCORE_CHUNK)),
        # CODEALIAS: fitted relation rotations THETA (trained) + RANDOM entity codes PHIr (necessity control)
        (CODEALIAS, rotate_direct_scores(PHIr, THETA, hold, device, chunk=SCORE_CHUNK)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, hold, all_true, ks=(1, PRIMARY_K))
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, hold, all_true, N, ks=(1, PRIMARY_K))
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    del PHI, THETA, Xa, Da, PHIo, THETAo, PHIr, THETAr
    _ec()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores)


def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None):
    # ids over the FULL entity/relation vocab (held-out entities get ids -> random-init codes exist for them)
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    train_lbl, held_lbl, hold_ids = build_heldout_entity_split(pool_lbl, ent2i, cfg["heldout_entity_frac"], seed)
    n_heldout_total = len(held_lbl)

    # optional bounded subsample of held-out queries (scoring cost = nq * N)
    if cfg.get("n_heldout_eval") and n_heldout_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = rng.choice(n_heldout_total, size=cfg["n_heldout_eval"], replace=False)
        held_lbl = [held_lbl[i] for i in sorted(idx.tolist())]

    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    hold = _to_int_edges(held_lbl, ent2i, rel2i)
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, hold)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel),
                  n_train=int(train_int.shape[0]), n_heldout_entities=len(hold_ids),
                  n_heldout_queries_total=n_heldout_total, n_heldout_scored=int(hold.shape[0]),
                  heldout_entity_frac=cfg["heldout_entity_frac"])
    if hold.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, hold, N, n_rel, cfg, device, seed, gd.rel_tail_freq, all_true, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (per_seed list length 1..3).
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _h10(ps, arm):
    return ps["arm_hits"][arm].get(PRIMARY_METRIC, float("nan"))


def aggregate_and_verdict(per_seed):
    def agg(arm):
        return _nm([_h10(ps, arm) for ps in per_seed])

    h = {a: agg(a) for a in ALL_ARMS}
    n_heldout = int(_nm([ps["n_heldout_scored"] for ps in per_seed]))

    d_oneshot = (h[ONESHOT] - h[RANDOM]) if (h[ONESHOT] == h[ONESHOT] and h[RANDOM] == h[RANDOM]) else float("nan")
    d_additive = (h[ADDITIVE] - h[RANDOM]) if (h[ADDITIVE] == h[ADDITIVE] and h[RANDOM] == h[RANDOM]) else float("nan")
    d_codealias = (h[CODEALIAS] - h[RANDOM]) if (h[CODEALIAS] == h[CODEALIAS] and h[RANDOM] == h[RANDOM]) else float("nan")
    valid_margins = [d for d in (d_oneshot, d_additive) if d == d]
    max_delta = max(valid_margins) if valid_margins else float("nan")
    oracle_margin = (h[ORACLE] - h[RANDOM]) if (h[ORACLE] == h[ORACLE] and h[RANDOM] == h[RANDOM]) else float("nan")

    enough_heldout = bool(n_heldout >= MIN_HELDOUT)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_MARGIN)
    # broken guard: a random-code control materially beats the frequency incumbent -> discriminator not sane
    broken = bool((h[RANDOM] == h[RANDOM] and h[POP] == h[POP] and (h[RANDOM] - h[POP]) > CONTROL_LOSE_EPS)
                  or (h[CODEALIAS] == h[CODEALIAS] and h[POP] == h[POP] and (h[CODEALIAS] - h[POP]) > CONTROL_LOSE_EPS))

    hard_pass = bool(max_delta == max_delta and max_delta >= HARD_PASS_MARGIN and oracle_fires and not broken)
    hard_fail = bool(max_delta == max_delta and max_delta < MIDDLE_LO)
    middle = bool(max_delta == max_delta and MIDDLE_LO <= max_delta < HARD_PASS_MARGIN)

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif hard_pass:
        verdict = "HARD_PASS_INDUCTIVE_ENTITY_TRANSFER"
    elif hard_fail:
        verdict = "HARD_FAIL_MEMORIZED_NO_ENTITY_TRANSFER"
    elif middle:
        verdict = "MIDDLE_BAND_PARTIAL_ENTITY_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_ENTITY_TRANSFER"

    verdict_msg = (
        "%s || HELD-OUT hits@%d [n=%d]: ONESHOT=%s ADDITIVE=%s | RANDOM=%s CODEALIAS=%s | ORACLE=%s POP=%s || "
        "MARGIN vs random-code: oneshot=%s additive=%s (max=%s; HARD_PASS>=%.2f MIDDLE[%.2f,%.2f) HARD_FAIL<%.2f) | "
        "codealias_margin=%s || ORACLE fires (>=%.2f over random)=%s margin=%s | broken(ctrl>POP)=%s | "
        "heldout_entities/seed~%s frac=%.2f seeds=%d" % (
            verdict, PRIMARY_K, n_heldout, _fmt(h[ONESHOT]), _fmt(h[ADDITIVE]), _fmt(h[RANDOM]), _fmt(h[CODEALIAS]),
            _fmt(h[ORACLE]), _fmt(h[POP]), _fmt(d_oneshot), _fmt(d_additive), _fmt(max_delta),
            HARD_PASS_MARGIN, MIDDLE_LO, HARD_PASS_MARGIN, MIDDLE_LO, _fmt(d_codealias),
            ORACLE_FIRE_MARGIN, oracle_fires, _fmt(oracle_margin), broken,
            int(_nm([ps["n_heldout_entities"] for ps in per_seed])),
            _nm([ps["heldout_entity_frac"] for ps in per_seed]), len(per_seed)))

    gates = dict(
        verdict=verdict,
        heldout_hits_at_k={a: (round(h[a], 5) if h[a] == h[a] else None) for a in ALL_ARMS},
        heldout_hits_at_1={a: _nm([ps["arm_hits"][a].get("hits@1", float("nan")) for ps in per_seed])
                           for a in ALL_ARMS},
        primary_k=PRIMARY_K,
        margin_oneshot_vs_random=(round(d_oneshot, 5) if d_oneshot == d_oneshot else None),
        margin_additive_vs_random=(round(d_additive, 5) if d_additive == d_additive else None),
        margin_codealias_vs_random=(round(d_codealias, 5) if d_codealias == d_codealias else None),
        max_margin=(round(max_delta, 5) if max_delta == max_delta else None),
        oracle_margin_vs_random=(round(oracle_margin, 5) if oracle_margin == oracle_margin else None),
        n_heldout_scored=n_heldout,
        bands=dict(HARD_PASS_MARGIN=HARD_PASS_MARGIN, MIDDLE_LO=MIDDLE_LO,
                   ORACLE_FIRE_MARGIN=ORACLE_FIRE_MARGIN, MIN_HELDOUT=MIN_HELDOUT,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, broken=broken,
        hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted DENSE grid: hold out a fraction of entities. ORACLE (held-out edges folded into the
# fit -> codes learned) recovers held-out tails >> RANDOM; ONESHOT (held-out codes random) sits near RANDOM. This
# proves (a) the split->fit->score->verdict path runs, (b) the arena registers positive signal (ORACLE fires) so
# the >=0.05 bar is achievable-in-principle, (c) POP is at floor on held-out (fit-independence), (d) arms differ.
# Determinism-pinned to single-thread CPU (tiny grids have symmetry ties that flip under multi-thread reduction).
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
    tr, va, te = build_syn_dense_grid_composition(grid_L=12, n_distract=120)
    pool = list(tr) + list(te)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "SYN_GRID_HELDOUT_ENTITY")
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_heldout_queries=res.get("n_heldout_scored"))
    if res.get("empty") or res.get("n_heldout_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_heldout_scored")
        return False, out

    ah = res["arm_hits"]
    h = {a: ah[a].get(PRIMARY_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))
    oracle_margin = h[ORACLE] - h[RANDOM]

    oracle_recovers = bool(h[ORACLE] == h[ORACLE] and h[ORACLE] >= SELFTEST_ORACLE_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_MARGIN)
    pop_at_floor = bool(h[POP] == h[POP] and h[POP] <= max(h[RANDOM], 0.05) + CONTROL_LOSE_EPS)
    arms_differ = bool(n_sigs >= 4)

    # VACUOUS-SMOKE guard: the RANDOM control must NOT reach the ORACLE positive control on held-out queries.
    random_reached_oracle = bool((h[ORACLE] - h[RANDOM]) <= ORACLE_FIRE_MARGIN)
    assert_discriminator_fires(random_reached_oracle, control_name=RANDOM,
                               headline_name="oracle_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached ORACLE on the planted held-out-entity arena -> arena not "
                                     "answerable / metric frozen")

    # full_gates_exercised: run the real verdict logic on the planted single-seed per_seed
    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_TRANSDUCTIVE", "headline_name": "oracle_beats_random_heldout",
         "extra": "planted grid: ORACLE recovers held-out tails (codes learned) and clears RANDOM by the fire "
                  "margin -> the >=0.05 inductive bar is achievable when the entity code exists"},
        {"kind": "metric_moves", "metric_name": "heldout_hits_at_k",
         "values": [h[RANDOM], h[ONESHOT], h[ORACLE]],
         "extra": "RANDOM=%.3f ONESHOT=%.3f ORACLE=%.3f: held-out readout responds to learned codes" %
                  (h[RANDOM], h[ONESHOT], h[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [h[RANDOM], h[CODEALIAS]],
         "headline_threshold": h[ORACLE], "higher_is_pass": True, "margin": ORACLE_FIRE_MARGIN, "n_repeats_min": 2,
         "control_name": "RANDOM_and_CODEALIAS_below_oracle",
         "extra": "RANDOM + CODEALIAS must sit below ORACLE by the fire margin on held-out queries"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "broken_test_guard", "enough_heldout", "band_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "broken_test_guard", "enough_heldout", "band_gate"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    out.update(
        heldout_hits={a: round(h[a], 5) for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, oracle_margin=round(oracle_margin, 5),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, pop_at_floor=pop_at_floor,
        arms_differ=arms_differ, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(oracle_recovers and oracle_fires and pop_at_floor and arms_differ)
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

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s oracle_fires=%s vp_ok=%s heldout_hits=%s" %
         (st_ok, st_res.get("oracle_fires"), st_res.get("validity_preflight_ok"), st_res.get("heldout_hits")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (ORACLE positive control did not recover/fire on planted "
                        "held-out-entity grid, or POP not at floor, or arms not distinct): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS held-out-entity inductive probe: ORACLE (learned held-out codes) recovers "
                        "and clears RANDOM by the fire margin, POP at floor, 4 validity-preflight checks declared",
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
            res = run_corpus(pool, cfg, device, seed, "CSKG_XCUT_CORE_HELDOUT_ENTITY", ckpt_dir=out_dir)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_heldout_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity queries too few (%d < %d)" %
                                   (res.get("n_heldout_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 4:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            ah = res["arm_hits"]
            _log("seed=%d n_ho=%d | held-out h@%d ONESHOT=%s ADDITIVE=%s RANDOM=%s ORACLE=%s POP=%s (%.1fs)" %
                 (seed, res["n_heldout_scored"], PRIMARY_K, _fmt(ah[ONESHOT][PRIMARY_METRIC]),
                  _fmt(ah[ADDITIVE][PRIMARY_METRIC]), _fmt(ah[RANDOM][PRIMARY_METRIC]),
                  _fmt(ah[ORACLE][PRIMARY_METRIC]), _fmt(ah[POP][PRIMARY_METRIC]), time.time() - ts))
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
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
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
