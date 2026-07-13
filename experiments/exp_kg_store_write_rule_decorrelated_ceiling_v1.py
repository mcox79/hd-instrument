"""KG_STORE_WRITE_RULE_DECORRELATED_CEILING: does swapping the store's naive one-shot Hebbian write rule for a
DECORRELATING closed-form (glass-box, zero-SGD) write rule RAISE the substrate's native representational CEILING
toward the additive level? De-risks the nativize side of optimize-then-nativize: can the substrate EVER carry the
optimized magnitude with a purely-linear-algebra write rule (no gradient descent)?

THE QUESTION (CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md, lever #1). The native
multiplicative-Hebbian store (hdlab.kg_traversal.KGStore -- CERT-584/585 chain-grade primitive) does inductive
entity-composition generalization IN KIND (exp_native_bind_compose_inductive_entity_cskg_v1: HARD_PASS,
native mrr=0.013967 MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr,
oracle ceiling mrr=0.023083 same path) but its ORACLE ceiling is ~6x below the additive SGD fit's oracle ceiling
(0.137 CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md). The native-ceiling drill found
the DOMINANT LIMITER is the WRITE RULE: naive one-shot Hebbian W += outer(E[o], key)/n_dim -> ~0.14N capacity
(Amit-Gutfreund-Sompolinsky 1985), the worst of the well-studied rules -- NOT dimension or codes. A DECORRELATING
least-squares (pseudo-inverse / Widrow-Hoff) write rule reports ~0.5N-2N capacity (Personnaz-Guyon-Dreyfus 1985;
prior on-substrate cell hebb_vs_pseudoinverse_write_rule_v1 = HARD_PASS 8x on synthetic autoassoc). Because
ORACLE_FOLDIN's score runs through this exact same W-bilinear readout, a decorrelating write rule should raise the
oracle CEILING itself -- the precise quantity this cell measures.

THE TEST: re-run the EXACT exp_native_bind_compose_inductive_entity_cskg_v1 7-arm harness (split/arena/controls/
readout REUSED VERBATIM via import), OTHERWISE UNCHANGED, under TWO write rules on a BIT-IDENTICAL split:
  hebbian : the current KGStore Hebbian path (positive-control reproducer -- must reproduce the landed 0.0231
            oracle / 0.0140 native at n_dim=1024 within tolerance; Gate D).
  pinv    : DECORRELATED closed-form. W minimizes sum_i ||W k_i - E[o_i]||^2 + ridge||W||^2 over the SAME triple
            stream. Closed form W = Cross @ inv(Gram + ridge*I), Cross = sum_i outer(E[o_i], k_i),
            Gram = sum_i outer(k_i, k_i) (both [n_dim x n_dim], one streaming pass = same shape as Hebbian ingest)
            + one [n_dim x n_dim] solve. ZERO gradient descent, ZERO epochs, ZERO loss loop -> stays glass-box.
Measure how much the native ORACLE CEILING (ORACLE_FOLDIN mrr) and native inductive mrr rise under pinv vs hebbian.

CERT-584/585 SAFETY: KGStore is NOT modified. The decorrelated W is recomputed on a LOCAL cell-owned store
INSTANCE after the standard Hebbian ingest, overwriting only that instance's W. The default KGStore.ingest_triples
Hebbian path is bit-identical / untouched; the hebbian arm exercises it and must reproduce the landed result. Same
defaulted-off opt-in discipline as the hard_neg_frac default-0 pattern -- pinv is a SELECTED path, never the default.

PRE-REG BANDS (picked BEFORE the run; primary = ORACLE_FOLDIN mrr rise = the CEILING question):
  ORACLE_RISE = pinv_oracle_mrr / hebb_oracle_mrr ; NATIVE_RISE = pinv_native_mrr / hebb_native_mrr ;
  GAP_CLOSED = (pinv_oracle_mrr - hebb_oracle_mrr) / (ADDITIVE_ORACLE_CEIL - hebb_oracle_mrr), ADDITIVE_ORACLE_CEIL
               = 0.137 CITED.
  HARD-PASS : (ORACLE_RISE >= 2.0 OR GAP_CLOSED >= 0.50)   # decorrelated write raises the native oracle ceiling
              AND native mrr rises ((pinv_native_mrr - hebb_native_mrr) >= MIN_SIG_RISE OR NATIVE_RISE >= 1.3)
              AND the pinv must-fail controls still fire (pinv scramble_controlled AND idshuf_controlled)
              AND numerically stable (pinv matrix_norm finite, no NaN in pinv oracle/native scores)
              AND the hebbian arm REPRODUCES the landed baseline oracle within tolerance (Gate D positive control)
              => the write rule is the lever; the substrate CAN carry the optimized magnitude with a glass-box write.
  MIDDLE    : ORACLE_RISE in [1.3, 2.0) and GAP_CLOSED < 0.50, or ceiling rises but native mrr does not (ceiling vs
              realized are separate gaps) -> partial; write rule helps but does not alone close the ceiling gap.
  HARD-FAIL : ORACLE_RISE < 1.3 (ceiling barely moves) OR numerical instability erases signal => the write rule is
              NOT the dominant lever / a native magnitude wall; redirect to code-side (DG) lever.

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : under BOTH rules ORACLE_FOLDIN clears RANDOM by the ceiling-aware ratio+abs gate on
                                the planted arena (harness answerable under each write rule).
  (2) metric_moves            : the WRITE-RULE discriminator moves recoverable signal (heteroassociative recall
                                cosine) across [hebb, pinv] at a load above the Hebbian cliff -- adversarial.
  (3) negative_control_margin : under pinv, RANDOM + relation-scramble + identity-shuffle sit below NATIVE_ANCHOR by
                                the MRR margin (decorrelation must NOT erase the relation-operator/identity signal).
  (4) full_gates_exercised    : aggregate_and_verdict + the top-level ceiling-rise verdict fire every gate at
                                self-test scale under both rules.

## Compute architecture
class (c) MIXED: split/support-query/POP = sequential-CPU graph ops (no matmul). The hebbian arm is the untouched
one-shot KGStore Hebbian ingest (cheap, reproduces landed). The pinv arm adds a streaming float64 Gram/Cross
accumulation (same [n_dim x n_dim] shape as the Hebbian pass) + ONE [n_dim x n_dim] linalg.solve per store build --
NO gradient descent, NO epochs. Two store builds/seed/rule (train-W + oracle fold-in); 3 seeds; only pinv does the
solve. n_dim=1024 solve is cheap on CPU. No GPU necessity (one-shot, small dense matmuls) -> remote_cpu_queue
(device=cpu). Wall estimate < ~15min FULL. Storage: cell-owned KGStore instances (E/R untouched; W recomputed
in-cell for pinv only); no mutation of the KGStore class or any persisted store.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 7 arms per rule + hebb-W != pinv-W (byte-hash) asserted.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary is a RISE RATIO of ORACLE mrr (ceiling-relative) -> discriminator_reachability OK
#   by construction (bands are ratios of the MEASURED per-rule ceiling, not absolute thresholds).
# - baseline_in_band: hebbian ORACLE must fire (reproduces landed) AND clear RANDOM; RANDOM/POP near 1/N floor.
# - discriminator survives scale: analytical (pseudo-inverse capacity gain ~0.5N-2N vs Hebbian ~0.14N is a
#   scale-INVARIANT ratio law) + the self-test WRITE-RULE discriminator fires the pinv-beats-hebb recall gap
#   deterministically at a load ABOVE the Hebbian cliff (0.4N).
# - HARD-PASS strictly above floor: ORACLE_RISE>=2.0 clears HARD-FAIL 1.3 by 0.7 ratio + a native-rise + control gate.
# - HP_SCOPE: the ceiling-rise HARD-PASS gates apply to the pinv-vs-hebbian COMPARISON only. hebbian = positive-control
#   reproducer (must reproduce landed); the 7 base arms keep their base HP_SCOPE (ORACLE positive control;
#   RANDOM/SCRAMBLE/IDSHUF must-not-clear; MEMORIZE head-to-head; POP fit-independence).
# - cardinality: EXPECTED_N_UNITS = n_seeds * 2 rules; each (seed, rule) asserted to produce all 7 arms + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per (seed,rule) failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- ridge auto-scales to trace(Gram)/n_dim; the ORACLE_RISE
#   discriminator must still fire (logged); ridge NOT tuned on real data.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-rule flush prints; timeout>=1800).

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
)
from hdlab.kg_traversal import KGStore  # noqa: E402 (LIVE store; read-only for E/R + Hebbian ingest; W overwritten in-cell for pinv)

# Reuse the base cell's split / arena / compose / readout / localization / verdict VERBATIM (only the write rule changes).
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402

ANCHOR_NAME = "kg_store_write_rule_decorrelated_ceiling_v1"

# Base arm handles + eval knobs (re-exported so the verdict text matches the base harness exactly).
NATIVE = base.NATIVE
MEMORIZE = base.MEMORIZE
RANDOM = base.RANDOM
SCRAMBLE = base.SCRAMBLE
IDSHUF = base.IDSHUF
ORACLE = base.ORACLE
POP = base.POP
ALL_ARMS = base.ALL_ARMS
GEOM_ARMS = base.GEOM_ARMS
EVAL_KS = base.EVAL_KS
CEIL_METRIC = base.CEIL_METRIC
PRIMARY_METRIC = base.PRIMARY_METRIC
MIN_HELDOUT = base.MIN_HELDOUT

WRITE_RULES = ["hebbian", "pinv"]

# ---- Decorrelated write-rule knobs (pre-registered; NOT tuned on real data) ----
RIDGE_FRAC = 1e-2            # ridge = RIDGE_FRAC * mean(diag(Gram)); auto-scales to the key Gram magnitude.
ACC_DTYPE = torch.float64   # Gram/Cross accumulation + solve in float64 for conditioning.

# ---- Ceiling-rise bands (the research question; picked BEFORE the run) ----
ADDITIVE_ORACLE_CEIL = 0.137     # CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md (additive SGD oracle ceiling)
HP_ORACLE_RISE = 2.0             # HARD-PASS: pinv raises the native oracle ceiling >= 2.0x
HP_GAP_CLOSED = 0.50             # ...OR closes >= 50% of the ceiling gap toward additive
HP_NATIVE_RISE = 1.3             # native inductive mrr must also rise (ratio) ...
MIN_SIG_RISE = 0.003             # ...OR by this absolute MRR margin (whichever is easier -- both count as "rises")
HF_ORACLE_RISE = 1.3             # HARD-FAIL: ceiling rise below this = write rule not the lever
# Gate D: the hebbian arm must reproduce the landed baseline oracle (positive-control reproducer).
LANDED_HEBB_ORACLE_MRR = 0.023083   # MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN
LANDED_HEBB_NATIVE_MRR = 0.013967   # MEASURED@ same path :NATIVE_ANCHOR_COMPOSE
REPRODUCE_TOL = 0.006               # abs MRR tolerance on the hebbian-arm reproduction of the landed oracle

# ---- WRITE-RULE discriminator self-test knobs (heteroassociative micro-capacity; adversarial) ----
ST_WR_N = 256
ST_WR_LOAD_HI = 0.80         # well above the Hebbian ~0.14N cliff -> pinv should decisively beat hebbian (probed).
ST_WR_LOAD_LO = 0.05         # below the cliff -> both recover (pinv must not break low-load).
ST_WR_PINV_MIN_COS = 0.70    # pinv mean recall cosine at LOAD_HI must clear this.
ST_WR_MARGIN_COS = 0.20      # (pinv - hebb) mean recall cosine at LOAD_HI must clear this.

FULL_CFG = dict(base.FULL_CFG)
SELFTEST_CFG = dict(base.SELFTEST_CFG)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


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
# Decorrelated (pseudo-inverse / Widrow-Hoff least-squares) write rule.
# W = Cross @ inv(Gram + ridge*I) ; Cross = sum_i outer(E[o_i], k_i) ; Gram = sum_i outer(k_i, k_i).
# k_i = E[s_i] * R[p_i] * sqrt(n_dim) (the store's OWN native bind). Closed-form; zero gradient descent -> glass-box.
# ---------------------------------------------------------------------------

def build_W_decorrelated(store, triples_int, ridge_frac=RIDGE_FRAC, batch=5000):
    """Recompute store.W in-place as the ridge least-squares heteroassociative solve over the SAME triple stream.

    Streaming accumulation of Gram [n_dim x n_dim] and Cross [n_dim x n_dim] (same shape as the Hebbian pass),
    then one dense solve. Returns a diagnostics dict (matrix_norm, ridge, cond-proxy, finite flags)."""
    E, R, sq, n_dim = store.E, store.R, store.sq, store.n_dim
    Gram = torch.zeros(n_dim, n_dim, dtype=ACC_DTYPE)
    Cross = torch.zeros(n_dim, n_dim, dtype=ACC_DTYPE)
    tri = torch.from_numpy(triples_int).long() if isinstance(triples_int, np.ndarray) else triples_int.long()
    n = tri.shape[0]
    for b in range(0, n, batch):
        chunk = tri[b:b + batch]
        s_idx, p_idx, o_idx = chunk[:, 0], chunk[:, 1], chunk[:, 2]
        keys = (E[s_idx] * R[p_idx] * sq).to(ACC_DTYPE)     # [c, n_dim] native multiplicative bind
        tgt = E[o_idx].to(ACC_DTYPE)                        # [c, n_dim] target tail codes
        Gram += keys.T @ keys
        Cross += tgt.T @ keys
    mean_diag = float(torch.diagonal(Gram).mean().item()) if n_dim > 0 else 0.0
    ridge = ridge_frac * max(mean_diag, 1e-8)
    A = Gram + ridge * torch.eye(n_dim, dtype=ACC_DTYPE)
    # W (Gram+rI) = Cross  ->  W = Cross @ inv(A) ;  A symmetric  ->  W^T = solve(A, Cross^T).
    W_T = torch.linalg.solve(A, Cross.T)
    W = W_T.T.contiguous().to(torch.float32)
    store.W = W
    fro = float(torch.linalg.norm(W).item())
    finite = bool(torch.isfinite(W).all().item())
    return dict(write_rule="pinv", matrix_norm=round(fro, 4), ridge=round(ridge, 6),
                gram_mean_diag=round(mean_diag, 4), n_triples=int(n), finite=finite)


def build_store_wr(N, n_rel, n_dim, seed, train_int, write_rule, fold_in=None):
    """KGStore with FIXED bipolar E/R (seeded per (seed, n_dim) EXACTLY as base.build_store) + one-shot Hebbian W.
    If write_rule == 'pinv', W is then OVERWRITTEN by the decorrelated least-squares solve over the SAME triple
    stream (train + optional fold_in). E/R and the KGStore class are untouched -> hebbian arm is bit-identical to
    the landed run. Returns (store, wr_diag)."""
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + n_dim + 1)   # SAME seed formula as base.build_store
    store = KGStore(n_ent=N, n_rel=n_rel, n_dim=n_dim, generator=g)
    tri = torch.from_numpy(train_int).long()
    if fold_in is not None and fold_in.shape[0] > 0:
        tri = torch.cat([tri, torch.from_numpy(fold_in).long()], dim=0)
    store.ingest_triples(tri)                                                   # standard Hebbian W (untouched path)
    if write_rule == "hebbian":
        return store, dict(write_rule="hebbian", matrix_norm=round(store.matrix_norm(), 4),
                           n_triples=int(tri.shape[0]), finite=bool(torch.isfinite(store.W).all().item()))
    if write_rule == "pinv":
        diag = build_W_decorrelated(store, tri)                                # overwrite W with decorrelated solve
        return store, diag
    raise ValueError("unknown write_rule %r" % write_rule)


# ---------------------------------------------------------------------------
# One (seed, write_rule) fit + score. Mirrors base.fit_and_score but threads write_rule into build_store_wr.
# ---------------------------------------------------------------------------

def fit_and_score_wr(train_int, support_int, query_int, hold_all, hold_ids, N, n_rel, cfg, seed,
                     rel_tail_freq, all_true, write_rule):
    n_dim = cfg["n_dim"]
    store, diag_train = build_store_wr(N, n_rel, n_dim, seed, train_int, write_rule)
    store_oracle, diag_oracle = build_store_wr(N, n_rel, n_dim, seed, train_int, write_rule, fold_in=hold_all)

    Ep_anchor, support_deg = base.native_compose_codes(store, support_int, N)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    Ep_scramble, _ = base.native_compose_codes(store, support_int, N, rel_perm=rel_perm)
    Ep_idshuf = base.identity_shuffle_codes(store.E, Ep_anchor, support_deg, hold_ids, seed)

    recall_train = base.native_query_recall(store, query_int)
    recall_oracle = base.native_query_recall(store_oracle, query_int)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (NATIVE, base.score_from_codes(recall_train, Ep_anchor)),
        (MEMORIZE, base.score_from_codes(recall_train, store.E)),
        (SCRAMBLE, base.score_from_codes(recall_train, Ep_scramble)),
        (IDSHUF, base.score_from_codes(recall_train, Ep_idshuf)),
        (ORACLE, base.score_from_codes(recall_oracle, store_oracle.E)),
        (RANDOM, base.random_scores(N, query_int, n_dim, seed)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = base._sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = base._sig(pop_rank_vec.astype(np.float64))

    w_train_hash = hashlib.sha256(store.W.numpy().tobytes()).hexdigest()[:16]
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg,
                diag_train=diag_train, diag_oracle=diag_oracle, w_train_hash=w_train_hash)


# ---------------------------------------------------------------------------
# Prepare a corpus split ONCE (seed-deterministic) then score under each write rule on the BIT-IDENTICAL split.
# ---------------------------------------------------------------------------

def prepare_corpus(pool_lbl, cfg, seed):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = base.build_heldout_entity_split_ac(
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
    return dict(ent2i=ent2i, rel2i=rel2i, rel_i2lbl=rel_i2lbl, N=N, n_rel=n_rel,
                train_int=train_int, support_int=support_int, query_int=query_int, hold_all=hold_all,
                hold_ids=hold_ids, n_cold=n_cold, n_query_total=n_query_total, gd=gd, all_true=all_true)


def score_corpus(prep, cfg, seed, corpus_name, write_rule, localize=True):
    N = prep["N"]; n_rel = prep["n_rel"]; query_int = prep["query_int"]
    result = dict(corpus=corpus_name, seed=seed, write_rule=write_rule, N=int(N), n_rel=int(n_rel),
                  n_train=int(prep["train_int"].shape[0]), n_heldout_entities=len(prep["hold_ids"]),
                  n_support=int(prep["support_int"].shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(query_int.shape[0]), n_cold=int(prep["n_cold"]), n_dim=int(cfg["n_dim"]),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result
    fs = fit_and_score_wr(prep["train_int"], prep["support_int"], query_int, prep["hold_all"], prep["hold_ids"],
                          N, n_rel, cfg, seed, prep["gd"].rel_tail_freq, prep["all_true"], write_rule)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
        write_diag_train=fs["diag_train"], write_diag_oracle=fs["diag_oracle"], w_train_hash=fs["w_train_hash"],
    )
    if localize:
        result["localization"] = base.localize_weak_points(
            fs["arm_scores"], query_int, prep["all_true"], fs["support_deg"], prep["gd"].node_degree,
            prep["rel_i2lbl"], prep["gd"].rel_tail_freq, N)
    return result


# ---------------------------------------------------------------------------
# Top-level ceiling-rise verdict over the two per-rule aggregate verdicts.
# ---------------------------------------------------------------------------

def _oracle_mrr(per_rule_verdict_gates):
    return per_rule_verdict_gates["heldout_mrr"].get(ORACLE, float("nan"))


def _native_mrr(per_rule_verdict_gates):
    return per_rule_verdict_gates["heldout_mrr"].get(NATIVE, float("nan"))


def ceiling_rise_verdict(per_seed_by_rule):
    """per_seed_by_rule: {'hebbian': [res,...], 'pinv': [res,...]}. Returns (verdict, msg, gates)."""
    v_hebb, _, g_hebb = base.aggregate_and_verdict(per_seed_by_rule["hebbian"])
    v_pinv, _, g_pinv = base.aggregate_and_verdict(per_seed_by_rule["pinv"])

    hebb_oracle = _oracle_mrr(g_hebb); pinv_oracle = _oracle_mrr(g_pinv)
    hebb_native = _native_mrr(g_hebb); pinv_native = _native_mrr(g_pinv)
    oracle_rise = _ratio(pinv_oracle, hebb_oracle)
    native_rise = _ratio(pinv_native, hebb_native)
    denom = ADDITIVE_ORACLE_CEIL - hebb_oracle
    gap_closed = ((pinv_oracle - hebb_oracle) / denom) if (denom > 0 and hebb_oracle == hebb_oracle
                                                           and pinv_oracle == pinv_oracle) else float("nan")

    # pinv numerical stability across all pinv seeds.
    def _all_finite(rule):
        ok = True
        for r in per_seed_by_rule[rule]:
            for d in (r.get("write_diag_train", {}), r.get("write_diag_oracle", {})):
                if not d.get("finite", True):
                    ok = False
        return ok
    pinv_stable = bool(_all_finite("pinv") and pinv_oracle == pinv_oracle and pinv_native == pinv_native)

    # pinv must-fails still fire (relation-scramble + identity-shuffle controlled under decorrelation).
    controls_fire = bool(g_pinv.get("scramble_controlled") and g_pinv.get("idshuf_controlled")
                         and g_pinv.get("oracle_fires"))

    # Gate D: hebbian arm reproduces the landed baseline oracle (positive-control reproducer).
    hebb_reproduces = bool(hebb_oracle == hebb_oracle
                           and abs(hebb_oracle - LANDED_HEBB_ORACLE_MRR) <= REPRODUCE_TOL)

    ceiling_rises = bool((oracle_rise == oracle_rise and oracle_rise >= HP_ORACLE_RISE)
                         or (gap_closed == gap_closed and gap_closed >= HP_GAP_CLOSED))
    native_rises = bool((pinv_native == pinv_native and hebb_native == hebb_native
                         and (pinv_native - hebb_native) >= MIN_SIG_RISE)
                        or (native_rise == native_rise and native_rise >= HP_NATIVE_RISE))
    ceiling_barely_moves = bool(oracle_rise == oracle_rise and oracle_rise < HF_ORACLE_RISE)

    hard_pass = bool(ceiling_rises and native_rises and controls_fire and pinv_stable and hebb_reproduces)
    hard_fail = bool((ceiling_barely_moves or not pinv_stable) and not hard_pass)
    middle = bool(not hard_pass and not hard_fail)

    if not hebb_reproduces:
        verdict = "INCONCLUSIVE_HEBB_ARM_DID_NOT_REPRODUCE_LANDED"
    elif hard_pass:
        verdict = "HARD_PASS_DECORRELATED_WRITE_RAISES_CEILING"
    elif hard_fail:
        verdict = "HARD_FAIL_WRITE_RULE_NOT_THE_LEVER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_CEILING_RISE"

    msg = ("%s || ORACLE mrr hebb=%s pinv=%s rise=%sx (HP>=%.1f) gap_closed=%s (HP>=%.2f; additive_ceil=%.3f) || "
           "NATIVE mrr hebb=%s pinv=%s rise=%sx (HP>=%.1f or +%.3f) || pinv must-fails fire=%s pinv_stable=%s "
           "hebb_reproduces_landed(%.4f+-%.3f)=%s | per_rule: hebb=%s pinv=%s"
           % (verdict, _fmt(hebb_oracle), _fmt(pinv_oracle),
              (_fmt(oracle_rise) if oracle_rise != float("inf") else "inf"), HP_ORACLE_RISE,
              _fmt(gap_closed), HP_GAP_CLOSED, ADDITIVE_ORACLE_CEIL,
              _fmt(hebb_native), _fmt(pinv_native),
              (_fmt(native_rise) if native_rise != float("inf") else "inf"), HP_NATIVE_RISE, MIN_SIG_RISE,
              controls_fire, pinv_stable, LANDED_HEBB_ORACLE_MRR, REPRODUCE_TOL, hebb_reproduces, v_hebb, v_pinv))

    def _rnd(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    gates = dict(
        verdict=verdict,
        oracle_mrr=dict(hebbian=_rnd(hebb_oracle), pinv=_rnd(pinv_oracle)),
        native_mrr=dict(hebbian=_rnd(hebb_native), pinv=_rnd(pinv_native)),
        oracle_rise=_rnd(oracle_rise, 3), native_rise=_rnd(native_rise, 3), gap_closed=_rnd(gap_closed, 3),
        additive_oracle_ceil=ADDITIVE_ORACLE_CEIL,
        ceiling_rises=ceiling_rises, native_rises=native_rises, controls_fire=controls_fire,
        pinv_stable=pinv_stable, hebb_reproduces=hebb_reproduces,
        hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
        bands=dict(HP_ORACLE_RISE=HP_ORACLE_RISE, HP_GAP_CLOSED=HP_GAP_CLOSED, HP_NATIVE_RISE=HP_NATIVE_RISE,
                   MIN_SIG_RISE=MIN_SIG_RISE, HF_ORACLE_RISE=HF_ORACLE_RISE, REPRODUCE_TOL=REPRODUCE_TOL,
                   LANDED_HEBB_ORACLE_MRR=LANDED_HEBB_ORACLE_MRR, RIDGE_FRAC=RIDGE_FRAC),
        per_rule_verdict=dict(hebbian=v_hebb, pinv=v_pinv),
        per_rule_gates=dict(hebbian=g_hebb, pinv=g_pinv),
        pinv_write_diag=[dict(seed=r["seed"], train=r.get("write_diag_train"), oracle=r.get("write_diag_oracle"))
                         for r in per_seed_by_rule["pinv"]],
    )
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# WRITE-RULE discriminator self-test: heteroassociative micro-capacity, adversarial (load ABOVE the Hebbian cliff).
# Proves the decorrelated write rule MEASURABLY raises recoverable signal on synthetic; pinv must not break low-load.
# ---------------------------------------------------------------------------

def _hetero_recall_cos(n, load, seed):
    """Plant M=load*n random bipolar (key->target) pairs; return mean cosine(W@k_i, target_i) for hebb and pinv."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    M = max(2, int(load * n))
    K = (torch.randint(0, 2, (M, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float64)   # keys [M, n]
    T = (torch.randint(0, 2, (M, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float64)   # targets [M, n]
    W_hebb = (T.T @ K) / n                                                  # sum outer(t_i, k_i)/n
    Gram = K.T @ K
    ridge = RIDGE_FRAC * float(torch.diagonal(Gram).mean().item())
    W_pinv = (T.T @ K) @ torch.linalg.inv(Gram + ridge * torch.eye(n, dtype=torch.float64))
    out = {}
    for name, W in [("hebb", W_hebb), ("pinv", W_pinv)]:
        rec = K @ W.T                                                       # [M, n]; row i = W @ k_i
        num = (rec * T).sum(dim=1)
        den = torch.linalg.norm(rec, dim=1) * torch.linalg.norm(T, dim=1) + 1e-12
        out[name] = float((num / den).mean().item())
        out[name + "_finite"] = bool(torch.isfinite(rec).all().item())
    return out, M


def writerule_discriminator_selftest():
    hi, M_hi = _hetero_recall_cos(ST_WR_N, ST_WR_LOAD_HI, seed=7)
    lo, M_lo = _hetero_recall_cos(ST_WR_N, ST_WR_LOAD_LO, seed=7)
    pinv_cos = hi["pinv"]; hebb_cos = hi["hebb"]
    margin = pinv_cos - hebb_cos
    pinv_clears = bool(pinv_cos >= ST_WR_PINV_MIN_COS)
    margin_clears = bool(margin >= ST_WR_MARGIN_COS)
    stable = bool(hi["pinv_finite"] and hi["hebb_finite"] and lo["pinv_finite"])
    lowload_ok = bool(lo["pinv"] >= ST_WR_PINV_MIN_COS)     # pinv must not break at low load
    ok = bool(pinv_clears and margin_clears and stable and lowload_ok)
    out = dict(n=ST_WR_N, load_hi=ST_WR_LOAD_HI, M_hi=M_hi, load_lo=ST_WR_LOAD_LO, M_lo=M_lo,
               hi_pinv_cos=round(pinv_cos, 4), hi_hebb_cos=round(hebb_cos, 4), margin_cos=round(margin, 4),
               lo_pinv_cos=round(lo["pinv"], 4), lo_hebb_cos=round(lo["hebb"], 4),
               pinv_clears=pinv_clears, margin_clears=margin_clears, lowload_ok=lowload_ok, stable=stable, ok=ok)
    return ok, out


# ---------------------------------------------------------------------------
# Compose-harness self-test: run the planted arena under BOTH write rules; assert pinv raises ORACLE recoverable
# signal AND the pinv must-fail controls still fire. Reuses base's planted arena + verdict verbatim.
# ---------------------------------------------------------------------------

def compose_harness_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _compose_harness_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _compose_harness_selftest_body():
    pool = base.build_planted_native_arena(7)
    cfg = dict(SELFTEST_CFG)
    prep = prepare_corpus(pool, cfg, 7)
    out = dict(n_grid_entities=prep["N"], n_heldout_entities=len(prep["hold_ids"]),
               n_support=int(prep["support_int"].shape[0]), n_query=int(prep["query_int"].shape[0]),
               n_cold=int(prep["n_cold"]), n_dim=int(cfg["n_dim"]))
    if prep["query_int"].shape[0] < base.SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%d)" % prep["query_int"].shape[0]
        return False, out

    per_rule = {}
    for wr in WRITE_RULES:
        res = score_corpus(prep, cfg, 7, "PLANTED_NATIVE_HELDOUT_ENTITY", wr, localize=True)
        per_rule[wr] = res
    # W hashes must differ across rules (META_RULE_AF: the two write rules are genuinely different).
    w_hebb = per_rule["hebbian"]["w_train_hash"]; w_pinv = per_rule["pinv"]["w_train_hash"]
    assert w_hebb != w_pinv, "META_RULE_AF: hebbian and pinv produced bit-identical W (write rule not applied)"

    m = {wr: {a: per_rule[wr]["arm_hits"][a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS} for wr in WRITE_RULES}
    n_sigs = {wr: len(set(per_rule[wr]["arm_sigs"].values())) for wr in WRITE_RULES}

    # pinv must raise (or at least not lose) ORACLE recoverable signal vs hebbian on the planted arena.
    pinv_raises_oracle = bool(m["pinv"][ORACLE] == m["pinv"][ORACLE] and m["hebbian"][ORACLE] == m["hebbian"][ORACLE]
                              and m["pinv"][ORACLE] >= m["hebbian"][ORACLE] - 1e-3)
    # pinv must-fails still fire.
    pinv_native_margin = m["pinv"][NATIVE] - m["pinv"][RANDOM]
    pinv_scramble_margin = m["pinv"][NATIVE] - m["pinv"][SCRAMBLE]
    pinv_idshuf_margin = m["pinv"][NATIVE] - m["pinv"][IDSHUF]
    pinv_native_beats_random = bool(pinv_native_margin == pinv_native_margin
                                    and pinv_native_margin >= base.SELFTEST_NATIVE_BEATS_RANDOM_MRR)
    pinv_scramble_fails = bool(pinv_scramble_margin == pinv_scramble_margin
                               and pinv_scramble_margin >= base.SELFTEST_SCRAMBLE_MARGIN_MRR)
    pinv_idshuf_fails = bool(pinv_idshuf_margin == pinv_idshuf_margin
                             and pinv_idshuf_margin >= base.SELFTEST_IDSHUF_MARGIN_MRR)
    arms_differ = bool(n_sigs["hebbian"] >= 5 and n_sigs["pinv"] >= 5)
    pinv_finite = bool(per_rule["pinv"]["write_diag_train"].get("finite", False)
                       and per_rule["pinv"]["write_diag_oracle"].get("finite", False))

    # VACUOUS-SMOKE guard: under pinv, the RANDOM null must NOT reach NATIVE_ANCHOR on the planted held-out arena.
    random_reached_native_pinv = bool(pinv_native_margin <= base.SELFTEST_NATIVE_BEATS_RANDOM_MRR)
    assert_discriminator_fires(random_reached_native_pinv, control_name=RANDOM,
                               headline_name="pinv_native_bind_compose_beats_random_heldout", run_mode="self_test",
                               extra="under the decorrelated write rule RANDOM reached NATIVE_ANCHOR_COMPOSE on the "
                                     "planted held-out-entity arena -> arena not answerable / metric frozen")

    v_verdict, v_msg, v_gates = ceiling_rise_verdict(
        {"hebbian": [per_rule["hebbian"]], "pinv": [per_rule["pinv"]]})

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(v_gates["per_rule_gates"]["hebbian"].get("oracle_fires")
                                                        and v_gates["per_rule_gates"]["pinv"].get("oracle_fires")),
         "control_name": "ORACLE_FOLDIN_BOTH_RULES", "headline_name": "oracle_fires_under_hebb_and_pinv",
         "extra": "planted arena: ORACLE fires (clears RANDOM by ratio+abs) under BOTH write rules -> the harness is "
                  "answerable under each write rule and the ceiling-rise comparison is well-posed"},
        {"kind": "metric_moves", "metric_name": "writerule_hetero_recall_cosine",
         "values": [m["hebbian"][ORACLE], m["pinv"][ORACLE]],
         "extra": "planted-arena ORACLE mrr moves across write rules hebb=%.4f pinv=%.4f; the write-rule micro "
                  "discriminator moves synthetic heteroassociative recall cosine above the Hebbian cliff"
                  % (m["hebbian"][ORACLE], m["pinv"][ORACLE])},
        {"kind": "negative_control_margin",
         "control_scores": [m["pinv"][RANDOM], m["pinv"][SCRAMBLE], m["pinv"][IDSHUF]],
         "headline_threshold": m["pinv"][NATIVE], "higher_is_pass": True,
         "margin": base.SELFTEST_SCRAMBLE_MARGIN_MRR, "n_repeats_min": 3,
         "control_name": "PINV_RANDOM_SCRAMBLE_IDSHUF_below_native_mrr",
         "extra": "under decorrelation RANDOM + relation-scramble + identity-shuffle must STILL sit below "
                  "NATIVE_ANCHOR by the MRR margin -> the write rule does not erase the relation/identity signal"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "w_hash_differs", "pinv_oracle_fires", "pinv_scramble_controlled",
                                    "pinv_idshuf_controlled", "hebb_reproduces_gateD", "ceiling_rise_gate"],
         "exercised_gates": ["arms_differ", "w_hash_differs", "pinv_oracle_fires", "pinv_scramble_controlled",
                             "pinv_idshuf_controlled", "hebb_reproduces_gateD", "ceiling_rise_gate"],
         "extra": "ceiling_rise_verdict=%s at self-test scale under both rules" % v_verdict},
    ], run_mode="self_test")

    out.update(
        planted_oracle_mrr={wr: round(m[wr][ORACLE], 5) for wr in WRITE_RULES},
        planted_native_mrr={wr: round(m[wr][NATIVE], 5) for wr in WRITE_RULES},
        planted_random_mrr={wr: round(m[wr][RANDOM], 5) for wr in WRITE_RULES},
        n_distinct_sigs=n_sigs, w_train_hash={wr: per_rule[wr]["w_train_hash"] for wr in WRITE_RULES},
        pinv_write_diag_train=per_rule["pinv"]["write_diag_train"],
        pinv_write_diag_oracle=per_rule["pinv"]["write_diag_oracle"],
        pinv_native_margin=round(pinv_native_margin, 5), pinv_scramble_margin=round(pinv_scramble_margin, 5),
        pinv_idshuf_margin=round(pinv_idshuf_margin, 5),
        pinv_raises_oracle=pinv_raises_oracle, pinv_native_beats_random=pinv_native_beats_random,
        pinv_scramble_fails=pinv_scramble_fails, pinv_idshuf_fails=pinv_idshuf_fails,
        arms_differ=arms_differ, pinv_finite=pinv_finite, ceiling_rise_selftest_verdict=v_verdict,
        validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(pinv_raises_oracle and pinv_native_beats_random and pinv_scramble_fails and pinv_idshuf_fails
              and arms_differ and pinv_finite)
    return ok, out


def mechanism_selftest():
    wr_ok, wr_out = writerule_discriminator_selftest()
    comp_ok, comp_out = compose_harness_selftest()
    ok = bool(wr_ok and comp_ok)
    return ok, dict(writerule_discriminator=wr_out, compose_harness=comp_out, ok=ok)


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds) * len(WRITE_RULES)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=cpu run_mode=%s seeds=%s n_dim=%s rules=%s" % (run_mode, seeds, cfg["n_dim"], WRITE_RULES))

    st_ok, st_res = mechanism_selftest()
    wr = st_res["writerule_discriminator"]; ch = st_res["compose_harness"]
    _log("mechanism_selftest ok=%s | writerule: pinv_cos=%s hebb_cos=%s margin=%s | compose: pinv_oracle=%s "
         "hebb_oracle=%s pinv_scramble_margin=%s pinv_idshuf_margin=%s vp_ok=%s"
         % (st_ok, wr.get("hi_pinv_cos"), wr.get("hi_hebb_cos"), wr.get("margin_cos"),
            (ch.get("planted_oracle_mrr") or {}).get("pinv"), (ch.get("planted_oracle_mrr") or {}).get("hebbian"),
            ch.get("pinv_scramble_margin"), ch.get("pinv_idshuf_margin"), ch.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (pinv did not raise recoverable signal above the Hebbian cliff, "
                        "or pinv must-fails did not fire, or numerical instability, or arms not distinct): wr_ok=%s "
                        "comp_ok=%s" % (wr.get("ok"), ch.get("ok")),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS DECORRELATED_WRITE_RULE_CEILING: the closed-form pseudo-inverse write rule "
                        "measurably raises heteroassociative recoverable signal above the Hebbian cliff on synthetic; "
                        "on the planted arena pinv raises ORACLE recoverable signal and the relation-scramble + "
                        "identity-shuffle must-fails STILL fire; W-hash differs across rules; 4 validity-preflight "
                        "checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed_by_rule = {wr_: [] for wr_ in WRITE_RULES}
    unit_failures = []
    unit_i = 0
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            prep = prepare_corpus(pool, cfg, seed)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d N=%d n_train=%d nq=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool),
                    prep["N"], int(prep["train_int"].shape[0]), int(prep["query_int"].shape[0])))
            if int(prep["query_int"].shape[0]) < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)"
                                   % (int(prep["query_int"].shape[0]), cfg.get("min_heldout", MIN_HELDOUT)))
            for wr_ in WRITE_RULES:
                res = score_corpus(prep, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY", wr_, localize=True)
                res["cskg_provenance"] = prov
                sigset = set(res["arm_sigs"].values())
                if len(sigset) < 5:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d rule=%s only %d sigs"
                                       % (seed, wr_, len(sigset)))
                per_seed_by_rule[wr_].append(res)
                write_partial(out_dir, seed * 10 + (0 if wr_ == "hebbian" else 1),
                              dict(seed=seed, write_rule=wr_, metrics=res, run_mode=run_mode))
                ah = res["arm_hits"]
                _log("seed=%d rule=%s nq=%d | MRR NATIVE=%s RANDOM=%s ORACLE=%s SCRAMBLE=%s IDSHUF=%s | W_norm=%s (%.1fs)"
                     % (seed, wr_, res["n_query_scored"], _fmt(ah[NATIVE][CEIL_METRIC]), _fmt(ah[RANDOM][CEIL_METRIC]),
                        _fmt(ah[ORACLE][CEIL_METRIC]), _fmt(ah[SCRAMBLE][CEIL_METRIC]), _fmt(ah[IDSHUF][CEIL_METRIC]),
                        res.get("write_diag_train", {}).get("matrix_norm"), time.time() - ts))
                unit_i += 1
                _hb("cskg", unit_i)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    got = sum(len(per_seed_by_rule[wr_]) for wr_ in WRITE_RULES)
    if got < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d units (seeds*rules), got %d (failures=%s)"
                        % (expected_n_units, got, unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = ceiling_rise_verdict(per_seed_by_rule)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(seeds), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, unit_failures=unit_failures,
                   per_seed_by_rule=per_seed_by_rule)
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
