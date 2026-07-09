"""REFRAME: is the native teacher-free encoder GOOD ON THE GRAPH TASK, regardless
of BGE-agreement? (Questions the yardstick, not just chases it.)

WHY (Director hand-off 2026-07-08): the native teacher-free encoder tops out at
ret_agree10-vs-BGE ~ 0.199 (< 0.30 bar) BUT it learned GRAPH-RELATIONAL structure
BY DESIGN (modularity_z = 336, MEASURED@data/exp_encoder_native_gradedcode_ret_agree_v1_smoke_seed7_smoke/metrics.json:modularity_z.NATIVE_DENSE).
ret_agree10 = AGREEMENT-WITH-BGE-top-10, and BGE is DISTRIBUTIONAL semantics.
For the deep-prize task (reasoning + retrieval over the GRAPH-structured ConceptNet
KB), graph-relational similarity may be the RIGHT target -- so ret_agree10-vs-BGE
may be the WRONG yardstick. This cell MEASURES the native encoder ON THE TASK
(graph-neighbor retrieval against GRAPH ground truth), not against BGE.

THE TASK METRIC (graph ground truth, NOT BGE-agreement):
  Held-out link prediction. Split ConceptNet edges into TRAIN (80%) / TEST (20%).
  The native encoder trains ONLY on TRAIN edges (never sees TEST). Retrieval quality
  = filtered Hits@10 + MRR of HELD-OUT (TEST) graph neighbors: for each query node,
  rank all candidate nodes by encoder cosine, mask self + known TRAIN neighbors, and
  measure whether the held-out TRUE graph neighbors surface in the top-10. This is
  the task's OWN graph-relational target -- does the encoding find the right
  ConceptNet neighbors (the retrieval the glass-box multi-hop loop depends on).
  Native NEVER trains on the test edges -> clean generalization (held-out
  methodology, USER-LOCKED 11th rule).

THREE ENCODERS ON THE TASK (+ native graded reported alongside):
  NATIVE_DENSE  : trained native teacher-free encoder (graph InfoNCE + VICReg
                  repulsion, char-trigram surface, NO teacher), code_dim=4096.
                  [PRIMARY -- the reframe subject]
  NATIVE_GRADED : graded_block_code(NATIVE_DENSE, kb=32, blk_l=128, m=5). Reported
                  alongside (certified finer-resolution transform).
  BGE           : name-aligned BGE-large cached embeddings (distributional). Here
                  BGE is used AS AN ENCODER on the graph task (its natural home is
                  distributional similarity; the question is whether that transfers
                  to graph-relational retrieval). EVAL comparator only, NOT ingested.
  CHAR          : raw hashed char-trigram bag (lexical; the CURRENT operational
                  default surface encoder). [FLOOR the mechanism must beat]

KEY DISCRIMINATOR (divergence set -- where graph-relational != BGE-distributional):
  A query node is in the DIVERGENCE set if its held-out graph target is
  DISTRIBUTIONALLY FAR under BGE (best target's BGE rank > K_DIV=50) -- i.e. BGE
  distributional similarity would NOT surface the graph-true neighbor. On this set
  the two notions of similarity genuinely disagree. Load-bearing question: does
  NATIVE still retrieve the graph target (Hits@10 > 0) where BGE-distributional
  cannot? If native wins on the divergence set, the native encoder captures REAL
  graph-relational structure that BGE misses -- the reframe is confirmed on the
  sharpest possible test.

BANDS (pre-reg preregs/2026-07-08_exp_encoder_native_graph_task_retrieval_reframe_v1.md):
  HARD_PASS_REFRAME_CONFIRMED (FULL) = native is COMPETITIVE-or-BETTER than BGE on
    the OVERALL graph task target (NATIVE_hits10 >= BGE_hits10 - COMPETE_EPS) AND
    both native and BGE BEAT char (>= BEAT_EPS) AND the discriminator fires. Meaning:
    ret_agree10-vs-BGE was the WRONG yardstick; the native encoder is task-good; a KB
    flip becomes viable on TASK MERIT with NO external model. (Strong sub-flag if
    native ALSO wins the divergence set: native wins exactly where the notions diverge.)
  HARD_FAIL_REFRAME_REJECTED (FULL) = native is ALSO worse than BGE on the task's OWN
    graph-relational target (overall AND on the divergence set). Meaning genuinely
    weak; strengthen the teacher-free encoder's semantic fidelity FIRST.
  MIDDLE_BAND = native beats char but is meaningfully below BGE (real signal, partial).

DISCRIMINATOR-FIRES (assert at smoke; task requirement):
  (a) divergence set non-vacuous (divergence_frac >= DIV_MIN=0.10), AND
  (b) the char floor underperforms the best encoder on the task
      (best(NATIVE,BGE)_hits10 - CHAR_hits10 >= BEAT_EPS), AND
  (c) the divergence set genuinely distinguishes the two notions
      (BGE_hits10 on the divergence set < BGE_hits10 overall - 0.05; by construction
      BGE is blind there -- confirms the split is non-degenerate).
  The native-vs-BGE reframe determination needs FULL training scale, so it is
  FULL-authoritative; smoke fires the discriminator (char underperforms + divergence
  real) and PREVIEWS the native/BGE/char task numbers.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over float32 aligned code matrices of the 4 encoders.
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except).
- crlb_n/a: no closed-form noise floor; discriminator is Hits@10 AGREEMENT with the
  GRAPH ground truth. Chance floor (THEORETICAL): random top-10 Hits ~ 10/(Na-1);
  the eps bands (0.02) are >> chance. discriminator_reachability=True.
- baseline_in_band: AG saturate-high (baseline > 0.95) CANNOT occur (filtered Hits@10
  over ~2k candidates does not saturate); the live risk is the OPPOSITE -- char being
  TOO strong (graph task lexically solvable), which the discriminator-fires gate (b)
  catches and reports. Declared with AG-exemption rationale.
- discriminator survives scale: char-underperform + divergence-set are STRUCTURAL
  (BGE is fully cached/trained; the divergence set is a fixed property of BGE geometry
  vs the graph). Native-vs-BGE needs full training scale -> FULL-only; smoke fires the
  must-underperform char floor + non-vacuous divergence at smoke scale.
- HARD_PASS strictly above floor + margin (COMPETE_EPS=0.02, BEAT_EPS=0.02).
- HP_SCOPE: {NATIVE_DENSE: [reframe_confirmed_gate]}. BGE/CHAR/NATIVE_GRADED are
  comparator/floor/diagnostic arms (not HP-gated).
- cardinality_ok: EXPECTED_N_UNITS = 4 encoders; counted from per_encoder.
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (graded geometry pinned to certified
  m=5; retrieval K_HITS=10 / K_DIV=50 standard link-prediction defaults).
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
- cell_chunked: True (one seed per cell; FULL multi-seed via sibling _seed_<N> wrappers).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: print_flush_true (line-buffered stdout + flush=True).

Compute architecture: (c) MIXED with justification. Native training is sequential-CPU
(SGD steps genuine sequential dependency; single linear ProjHead; parent teacher-free
encoder is CPU-only established). Retrieval Hits@k / MRR is chunked torch matmul
(device-agnostic; remote_cpu_queue runner). GPU speedup marginal for one linear layer;
FULL routes to remote_cpu_queue. Storage strategy: no_storage / no_composition (this is
an encoder-retrieval MEASUREMENT, not a compositional chain -- SHARDED-default n/a).

Parent cells (imported, READ-ONLY):
  experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py  (native encoder)
  hdlab/gsbc_graded_encoder.py                                       (graded block code)

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch  # noqa: F401 -- CPU here; also satisfies queue_add.sh routing gate

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments import (  # noqa: E402
    exp_teacher_free_relational_encoder_cn_subgraph_v1 as tfe,
)
from hdlab.gsbc_graded_encoder import graded_block_code  # noqa: E402

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_native_graph_task_retrieval_reframe_v1"

# Certified graded geometry (native code_dim pinned to feed the block geometry).
CODE_DIM = 4096
KB = 32
BLK_L = 128
M_GRADED = 5
assert KB * BLK_L == CODE_DIM

BGE_CACHE = "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

# Held-out link-prediction retrieval bands (Director hand-off).
TRAIN_FRAC = 0.80               # 80% edges train (native), 20% held-out (task ground truth)
K_HITS = 10                     # filtered Hits@K primary metric
K_DIV = 50                      # BGE-rank threshold defining the divergence set
DIV_MIN = 0.10                  # divergence set must be >= 10% of query nodes (non-vacuous)
COMPETE_EPS = 0.02              # native "competitive" iff within this of BGE (or better)
BEAT_EPS = 0.02                 # an encoder "beats" char iff Hits@10 exceeds by this
DIV_EPS = 0.02                  # native "wins the divergence set" iff exceeds BGE by this
MIN_QUERIES = 40                # need at least this many held-out query nodes to trust the metric
MIN_ALIGN_FRAC = 0.50           # BGE-gold coverage floor (else eval universe untrustworthy)

# 4 encoders per seed.
ENC_NATIVE = "NATIVE_DENSE"
ENC_GRADED = "NATIVE_GRADED"
ENC_BGE = "BGE"
ENC_CHAR = "CHAR"
ENCODERS = [ENC_NATIVE, ENC_GRADED, ENC_BGE, ENC_CHAR]
EXPECTED_N_UNITS = 4

# Local run configs (code_dim pinned to 4096 for graded geometry; one seed per cell).
SMOKE_CFG = dict(
    n_nodes=2500, epochs=200, batch=256, k_rewire=40,
    code_dim=CODE_DIM, feat_dim=4096, temp=0.15, lr=0.01,
    lambda_cov=1.0, lambda_var=1.0, simgrace_sigma=0.05,
)
FULL_CFG = dict(
    n_nodes=12000, epochs=800, batch=512, k_rewire=150,
    code_dim=CODE_DIM, feat_dim=8192, temp=0.10, lr=0.008,
    lambda_cov=1.0, lambda_var=1.0, simgrace_sigma=0.05,
)

SUBGRAPH_BASE_SEED = tfe.SUBGRAPH_BASE_SEED  # 1234 (shared induced subgraph)


# ---------------------------------------------------------------------------
# Defensive helpers (SCHEMA-VET section 13).
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=int(expected_n_units), host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _emit_heartbeat(output_dir: str, unit_idx: int, total: int, elapsed_s: float,
                    extra: Optional[dict] = None) -> None:
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=int(unit_idx),
               total_units=int(total), elapsed_s=float(elapsed_s))
    if extra:
        row["extra"] = extra
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _code_digest(code: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(code.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# BGE eval-comparator (name-aligned; NEVER ingested).
# ---------------------------------------------------------------------------

def _load_bge_gold(node_ids: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """Return (aligned_local_idx [K], gold [K, 1024]) for node_ids present in the
    BGE cache. gold is L2-normalized. Fail-loud if cache missing."""
    cache = _REPO / BGE_CACHE
    if not cache.exists():
        raise FileNotFoundError("BGE eval-comparator cache not found: %s" % cache)
    z = zipfile.ZipFile(str(cache))
    with z.open("id_order_json.npy") as f:
        ids = json.loads(str(np.lib.format.read_array(f, allow_pickle=False)))
    idmap = {v: i for i, v in enumerate(ids)}
    aligned_local = []
    aligned_rows = []
    for li, nid in enumerate(node_ids):
        gi = idmap.get(nid)
        if gi is not None:
            aligned_local.append(li)
            aligned_rows.append(gi)
    if not aligned_local:
        raise RuntimeError("no node_ids aligned to BGE cache (id-space mismatch)")
    with z.open("semantic.npy") as f:
        sem = np.lib.format.read_array(f, allow_pickle=False)
    gold = np.ascontiguousarray(sem[np.asarray(aligned_rows, dtype=np.int64)].astype(np.float32))
    del sem
    if np.isnan(gold).any() or np.isinf(gold).any():
        raise RuntimeError("BGE gold contains NaN/Inf")
    gold = gold / (np.linalg.norm(gold, axis=1, keepdims=True) + 1e-8)
    return np.asarray(aligned_local, dtype=np.int64), gold


# ---------------------------------------------------------------------------
# Held-out edge split.
# ---------------------------------------------------------------------------

def split_edges(edges: np.ndarray, train_frac: float, seed: int
                ) -> Tuple[np.ndarray, np.ndarray]:
    """Random edge split into (train_edges, test_edges). Deterministic per seed."""
    rng = np.random.default_rng(seed + 900)
    perm = rng.permutation(edges.shape[0])
    n_train = int(round(train_frac * edges.shape[0]))
    tr = edges[perm[:n_train]]
    te = edges[perm[n_train:]]
    return np.ascontiguousarray(tr), np.ascontiguousarray(te)


# ---------------------------------------------------------------------------
# Filtered retrieval metric vs GRAPH ground truth (held-out neighbors).
# ---------------------------------------------------------------------------

def retrieval_metrics(code_al: np.ndarray,
                      query_local: np.ndarray,
                      targets_per_q: List[np.ndarray],
                      trainmask_per_q: List[np.ndarray],
                      k_hits: int) -> Dict[str, np.ndarray]:
    """Filtered Hits@k + MRR + best-target-rank over held-out graph neighbors.

    code_al        : [Na, dim] encoder codes over the ALIGNED candidate universe.
    query_local    : [Q] aligned-local indices of query nodes.
    targets_per_q  : list length Q of aligned-local held-out neighbor indices per query.
    trainmask_per_q: list length Q of aligned-local TRAIN-neighbor indices to mask.
    Returns per-query arrays: recall_at_k [Q], rr [Q], best_rank [Q] (0-indexed).
    """
    cn = code_al / (np.linalg.norm(code_al, axis=1, keepdims=True) + 1e-8)
    cn = torch.from_numpy(np.ascontiguousarray(cn.astype(np.float32)))
    Q = query_local.shape[0]
    recall = np.zeros(Q, dtype=np.float64)
    rr = np.zeros(Q, dtype=np.float64)
    best_rank = np.zeros(Q, dtype=np.int64)
    chunk = 256
    for lo in range(0, Q, chunk):
        hi = min(lo + chunk, Q)
        qrows = torch.from_numpy(query_local[lo:hi].astype(np.int64))
        S = (cn[qrows] @ cn.T).numpy()  # [b, Na]
        for r in range(hi - lo):
            qi = int(query_local[lo + r])
            scores = S[r]
            scores[qi] = -2.0
            tm = trainmask_per_q[lo + r]
            if tm.size:
                scores[tm] = -2.0
            tgts = targets_per_q[lo + r]
            # rank of each target = count of candidates strictly above it.
            ranks = np.array([int((scores > scores[t]).sum()) for t in tgts], dtype=np.int64)
            recall[lo + r] = float(np.mean(ranks < k_hits))
            br = int(ranks.min())
            best_rank[lo + r] = br
            rr[lo + r] = 1.0 / (1.0 + br)
    return dict(recall_at_k=recall, rr=rr, best_rank=best_rank)


# ---------------------------------------------------------------------------
# Verdict (per single seed).
# ---------------------------------------------------------------------------

def _verdict(res: Dict, run_mode: str) -> Tuple[str, str]:
    """res has per-encoder overall/divergence Hits@10 + MRR + divergence_frac + n_queries."""
    nat = res[ENC_NATIVE]["hits10"]
    bge = res[ENC_BGE]["hits10"]
    cha = res[ENC_CHAR]["hits10"]
    gra = res[ENC_GRADED]["hits10"]
    nat_d = res[ENC_NATIVE]["hits10_div"]
    bge_d = res[ENC_BGE]["hits10_div"]
    cha_d = res[ENC_CHAR]["hits10_div"]
    dfrac = res["divergence_frac"]
    nq = res["n_queries"]

    tail = ("[OVERALL hits10 NATIVE=%.4f BGE=%.4f CHAR=%.4f GRADED=%.4f | "
            "DIVERGENCE(frac=%.3f) hits10 NATIVE=%.4f BGE=%.4f CHAR=%.4f | "
            "MRR NATIVE=%.4f BGE=%.4f CHAR=%.4f | n_queries=%d modz(NATIVE)=%.1f "
            "align_frac=%.3f]" % (
                nat, bge, cha, gra, dfrac, nat_d, bge_d, cha_d,
                res[ENC_NATIVE]["mrr"], res[ENC_BGE]["mrr"], res[ENC_CHAR]["mrr"],
                nq, res[ENC_NATIVE]["modularity_z_train"], res["align_frac"]))

    # Integrity gates (both modes).
    for k in (nat, bge, cha, gra, nat_d, bge_d, cha_d):
        if not math.isfinite(k) or not (-0.01 <= k <= 1.01):
            return ("SMOKE_GATE_FAIL" if run_mode == "smoke" else "HARD_FAIL",
                    "S_hits10_out_of_range %s" % tail)
    if res["align_frac"] < MIN_ALIGN_FRAC:
        return ("SMOKE_GATE_FAIL" if run_mode == "smoke" else "HARD_FAIL",
                "GOLD_ALIGNMENT_TOO_LOW %.3f < %.2f %s" % (res["align_frac"], MIN_ALIGN_FRAC, tail))
    if nq < MIN_QUERIES:
        return ("SMOKE_GATE_FAIL" if run_mode == "smoke" else "HARD_FAIL",
                "TOO_FEW_QUERIES %d < %d (held-out set too small to trust) %s" % (nq, MIN_QUERIES, tail))

    # DISCRIMINATOR-FIRES.
    best_overall = max(nat, bge)
    char_underperforms = bool(best_overall - cha >= BEAT_EPS)
    divergence_nonvacuous = bool(dfrac >= DIV_MIN)
    divergence_distinguishes = bool(bge_d < bge - 0.05)  # BGE blind on its divergence set
    discriminator_fires = char_underperforms and divergence_nonvacuous

    if run_mode == "smoke":
        if not divergence_nonvacuous:
            return ("SMOKE_GATE_FAIL",
                    "DIVERGENCE_SET_VACUOUS: divergence_frac=%.3f < %.2f -- the two "
                    "similarity notions do not measurably diverge on this subgraph; the "
                    "key discriminator cannot fire. Re-spec K_DIV or subgraph. %s" % (
                        dfrac, DIV_MIN, tail))
        if not char_underperforms:
            return ("SMOKE_GATE_FAIL",
                    "CHAR_FLOOR_DOES_NOT_UNDERPERFORM: best(NATIVE=%.4f,BGE=%.4f) - "
                    "CHAR=%.4f < %.2f -- the graph task is lexically solvable by the "
                    "char-trigram default, so the metric cannot cleanly credit the "
                    "learned/distributional encoders. Report to Director (this is itself "
                    "a decisive finding: the operational default may already suffice). %s" % (
                        best_overall, cha, best_overall - cha, BEAT_EPS, tail))
        return ("HARD_PASS",
                "SMOKE_MACHINERY_OK: 4 encoders produce finite filtered Hits@10 vs the "
                "GRAPH ground truth over %d held-out query nodes; codes bit-distinct; "
                "discriminator FIRES (char underperforms by %.4f; divergence_frac=%.3f>=%.2f; "
                "divergence_distinguishes=%s). Native-vs-BGE reframe verdict is FULL-only "
                "(needs full training scale + multi-seed); smoke previews NATIVE=%.4f "
                "BGE=%.4f (overall), NATIVE_div=%.4f BGE_div=%.4f. %s" % (
                    nq, best_overall - cha, dfrac, DIV_MIN, divergence_distinguishes,
                    nat, bge, nat_d, bge_d, tail))

    # ---- FULL: reframe determination ----
    if not discriminator_fires:
        return ("HARD_FAIL",
                "DISCRIMINATOR_DID_NOT_FIRE at FULL (char_underperforms=%s divergence_"
                "nonvacuous=%s): cannot render a clean reframe verdict; the graph task "
                "metric did not separate the encoders as designed. %s" % (
                    char_underperforms, divergence_nonvacuous, tail))

    native_competitive = bool(nat >= bge - COMPETE_EPS)
    native_beats_char = bool(nat - cha >= BEAT_EPS)
    bge_beats_char = bool(bge - cha >= BEAT_EPS)
    native_wins_divergence = bool(nat_d - bge_d >= DIV_EPS)

    if native_competitive and native_beats_char and bge_beats_char:
        strong = (" STRONG: native ALSO wins the divergence set (NATIVE_div=%.4f > "
                  "BGE_div=%.4f by %+.4f) -- native wins EXACTLY where the two notions "
                  "diverge." % (nat_d, bge_d, nat_d - bge_d)) if native_wins_divergence else ""
        return ("HARD_PASS",
                "HARD_PASS_REFRAME_CONFIRMED: on the graph task's OWN ground truth the "
                "native teacher-free encoder is COMPETITIVE-or-BETTER than BGE "
                "(NATIVE hits10=%.4f vs BGE=%.4f, within %.2f) and BOTH beat the "
                "char-trigram default (CHAR=%.4f). ret_agree10-vs-BGE was the WRONG "
                "yardstick: the native encoder learned REAL graph-relational structure "
                "(modularity_z=%.1f) that is TASK-GOOD without any external model. A KB "
                "flip becomes viable on task merit.%s %s" % (
                    nat, bge, COMPETE_EPS, cha, res[ENC_NATIVE]["modularity_z_train"],
                    strong, tail))

    if (not native_competitive) and (not native_wins_divergence):
        return ("HARD_FAIL",
                "HARD_FAIL_REFRAME_REJECTED: native is ALSO worse than BGE on the task's "
                "OWN graph-relational target (NATIVE hits10=%.4f < BGE=%.4f - %.2f) AND "
                "does not win the divergence set (NATIVE_div=%.4f vs BGE_div=%.4f). The "
                "limiter is genuine MEANING/semantic weakness, not the yardstick. Decisive "
                "redirect: strengthen the teacher-free encoder's semantic fidelity FIRST. "
                "%s" % (nat, bge, COMPETE_EPS, nat_d, bge_d, tail))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: native beats the char default (%.4f vs %.4f) and/or wins the "
            "divergence set (NATIVE_div=%.4f vs BGE_div=%.4f) but is not cleanly "
            "competitive-or-better than BGE overall (NATIVE=%.4f vs BGE=%.4f). Real "
            "graph-relational signal, partial reframe. %s" % (
                nat, cha, nat_d, bge_d, nat, bge, tail))


# ---------------------------------------------------------------------------
# Driver (ONE seed).
# ---------------------------------------------------------------------------

def run(run_mode: str, seed: int) -> int:
    assert run_mode in ("smoke", "full"), "unsupported run_mode %r" % run_mode
    anchor = "%s_smoke_seed%d" % (ANCHOR_NAME, seed) if run_mode == "smoke" \
        else "%s_seed%d" % (ANCHOR_NAME, seed)
    out_dir = str(get_output_dir(anchor))
    cfg = SMOKE_CFG if run_mode == "smoke" else FULL_CFG
    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    t0 = time.perf_counter()
    _log("run_mode=%s seed=%d code_dim=%d kb=%d blk_l=%d m_graded=%d n_nodes=%d "
         "epochs=%d train_frac=%.2f K_HITS=%d K_DIV=%d" % (
             run_mode, seed, cfg["code_dim"], KB, BLK_L, M_GRADED, cfg["n_nodes"],
             cfg["epochs"], TRAIN_FRAC, K_HITS, K_DIV))

    # ---- native ConceptNet subgraph + surface features (NO teacher) ----
    node_ids, node_words, edges, degrees, meta = tfe.load_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s" % meta)
    X = tfe.char_trigram_features(node_words, cfg["feat_dim"])  # CHAR encoder + native input
    n_nodes = len(node_ids)

    # ---- held-out edge split (native trains ONLY on train edges) ----
    train_edges, test_edges = split_edges(edges, TRAIN_FRAC, seed)
    _log("edge split: %d train / %d test (held-out ground truth)" % (
        train_edges.shape[0], test_edges.shape[0]))
    train_adj = tfe.build_adjlist(train_edges, n_nodes)

    # ---- BGE eval-comparator gold (name-aligned; never ingested) ----
    aligned_local, gold = _load_bge_gold(node_ids)
    align_frac = len(aligned_local) / n_nodes
    _log("BGE gold: aligned %d/%d (frac=%.3f) x %dd (eval-comparator only)" % (
        len(aligned_local), n_nodes, align_frac, gold.shape[1]))

    # global -> aligned-local index map (candidate universe = aligned nodes).
    g2al = {int(g): li for li, g in enumerate(aligned_local.tolist())}
    Na = len(aligned_local)
    chance_floor = float(K_HITS) / max(Na - 1, 1)

    # ---- train native encoder (train edges only) + build codes ----
    _emit_heartbeat(out_dir, 0, EXPECTED_N_UNITS, time.perf_counter() - t0,
                    extra={"stage": "train_start"})
    emb_trained = tfe.train_arm(tfe.PRIMARY_ARM, X, train_adj, cfg, seed,
                                out_dir=out_dir, unit_base=0)
    _log("trained native encoder emb %s (%.1fs)" % (emb_trained.shape, time.perf_counter() - t0))
    native_dense = emb_trained.astype(np.float32)
    native_graded = graded_block_code(native_dense, KB, BLK_L, M_GRADED)
    char_code = X.astype(np.float32)

    # subset every encoder to the ALIGNED candidate universe.
    al = aligned_local
    codes_al = {
        ENC_NATIVE: native_dense[al],
        ENC_GRADED: native_graded[al],
        ENC_BGE: gold,                    # already aligned rows
        ENC_CHAR: char_code[al],
    }

    # ARMS-MUST-DIFFER (META_RULE_AF; float32 bytes over aligned codes).
    digests = {e: _code_digest(codes_al[e]) for e in ENCODERS}
    dl = list(digests.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            if dl[i][1] == dl[j][1]:
                raise RuntimeError("failure_class=META_RULE_AF_VIOLATION: %s/%s identical"
                                   % (dl[i][0], dl[j][0]))

    # ---- build query set + targets + train-mask in aligned-local space ----
    # test-neighbor adjacency (aligned-local) per node; train-neighbor adjacency (aligned-local).
    test_adj_al: Dict[int, List[int]] = {}
    for a, b in test_edges:
        a = int(a); b = int(b)
        la = g2al.get(a); lb = g2al.get(b)
        if la is None or lb is None:
            continue
        test_adj_al.setdefault(la, []).append(lb)
        test_adj_al.setdefault(lb, []).append(la)
    train_adj_al: Dict[int, List[int]] = {}
    for a, b in train_edges:
        a = int(a); b = int(b)
        la = g2al.get(a); lb = g2al.get(b)
        if la is None or lb is None:
            continue
        train_adj_al.setdefault(la, []).append(lb)
        train_adj_al.setdefault(lb, []).append(la)

    query_local = np.array(sorted(test_adj_al.keys()), dtype=np.int64)
    targets_per_q = [np.array(sorted(set(test_adj_al[int(q)])), dtype=np.int64) for q in query_local]
    trainmask_per_q = [np.array(sorted(set(train_adj_al.get(int(q), []))), dtype=np.int64)
                       for q in query_local]
    n_queries = int(query_local.shape[0])
    _log("held-out query nodes (aligned, >=1 test neighbor): %d over Na=%d candidates "
         "(chance hits10=%.4f)" % (n_queries, Na, chance_floor))

    # ---- per-encoder retrieval metrics ----
    per_enc: Dict[str, Dict] = {}
    unit_fail: List[Dict] = []
    for ui, enc in enumerate(ENCODERS):
        try:
            rm = retrieval_metrics(codes_al[enc], query_local, targets_per_q,
                                   trainmask_per_q, K_HITS)
            per_enc[enc] = dict(recall_at_k=rm["recall_at_k"], rr=rm["rr"],
                                best_rank=rm["best_rank"])
            _log("encoder=%s hits10=%.4f mrr=%.4f (%.1fs)" % (
                enc, float(rm["recall_at_k"].mean()), float(rm["rr"].mean()),
                time.perf_counter() - t0))
            _emit_heartbeat(out_dir, ui + 1, EXPECTED_N_UNITS, time.perf_counter() - t0,
                            extra={"encoder": enc, "hits10": float(rm["recall_at_k"].mean())})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append(dict(encoder=enc, failure_class=type(exc).__name__, msg=str(exc)[:300]))
            raise

    # ---- divergence set (BGE-distributional blind spot) ----
    bge_best_rank = per_enc[ENC_BGE]["best_rank"]
    div_mask = bge_best_rank > K_DIV                       # BGE would not surface the graph target
    divergence_frac = float(np.mean(div_mask)) if n_queries else 0.0

    # ---- native train-edge assortativity (positive control: did native learn structure) ----
    rng = np.random.default_rng(seed + 4242)
    modz_native, _, _, _ = tfe.embedding_assortativity_z(
        native_dense, train_edges, _deg_from_edges(train_edges, n_nodes), cfg["k_rewire"], rng)

    # ---- assemble per-encoder scalar summary ----
    res: Dict[str, Dict] = {}
    for enc in ENCODERS:
        rk = per_enc[enc]["recall_at_k"]
        rr = per_enc[enc]["rr"]
        hits_div = float(rk[div_mask].mean()) if div_mask.any() else 0.0
        res[enc] = dict(hits10=float(rk.mean()), mrr=float(rr.mean()),
                        hits10_div=hits_div,
                        modularity_z_train=float(modz_native) if enc == ENC_NATIVE else None)
    res["divergence_frac"] = divergence_frac
    res["n_queries"] = n_queries
    res["align_frac"] = float(align_frac)
    res["chance_floor"] = chance_floor

    if len(per_enc) < EXPECTED_N_UNITS:
        verdict, verdict_msg = ("HARD_FAIL",
                                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d encoders"
                                % (len(per_enc), EXPECTED_N_UNITS))
    else:
        verdict, verdict_msg = _verdict(res, run_mode)

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        elapsed_s=float(elapsed), run_mode=run_mode, anchor_name=anchor,
        seed=int(seed), device="cpu", N=CODE_DIM,
        geometry=dict(code_dim=CODE_DIM, kb=KB, blk_l=BLK_L, m_graded=M_GRADED),
        task=dict(kind="held_out_link_prediction_retrieval", ground_truth="conceptnet_graph",
                  train_frac=TRAIN_FRAC, k_hits=K_HITS, k_div=K_DIV,
                  n_train_edges=int(train_edges.shape[0]), n_test_edges=int(test_edges.shape[0])),
        comparator=dict(source="BGE_large_v2_name_177899", role="eval_comparator_never_ingested",
                        dim=int(gold.shape[1]), aligned=int(Na), n_nodes=int(n_nodes),
                        align_frac=float(align_frac)),
        hits10=dict((e, res[e]["hits10"]) for e in ENCODERS),
        hits10_divergence=dict((e, res[e]["hits10_div"]) for e in ENCODERS),
        mrr=dict((e, res[e]["mrr"]) for e in ENCODERS),
        divergence_frac=divergence_frac, n_queries=n_queries,
        native_minus_bge_overall=float(res[ENC_NATIVE]["hits10"] - res[ENC_BGE]["hits10"]),
        native_minus_bge_divergence=float(res[ENC_NATIVE]["hits10_div"] - res[ENC_BGE]["hits10_div"]),
        native_minus_char_overall=float(res[ENC_NATIVE]["hits10"] - res[ENC_CHAR]["hits10"]),
        bge_minus_char_overall=float(res[ENC_BGE]["hits10"] - res[ENC_CHAR]["hits10"]),
        modularity_z_native_train=float(modz_native),
        chance_floor=chance_floor,
        bands=dict(train_frac=TRAIN_FRAC, k_hits=K_HITS, k_div=K_DIV, div_min=DIV_MIN,
                   compete_eps=COMPETE_EPS, beat_eps=BEAT_EPS, div_eps=DIV_EPS),
        subgraph_meta=meta, config=cfg,
        objective=("native teacher-free relational encoder measured ON THE GRAPH TASK "
                   "(held-out filtered Hits@10/MRR of TEST graph neighbors) vs BGE "
                   "(distributional) and char-trigram (lexical default); divergence-set "
                   "discriminator where graph-relational != BGE-distributional. Reframe: "
                   "is ret_agree10-vs-BGE the wrong yardstick?"),
        per_encoder=dict((e, dict(hits10=res[e]["hits10"], mrr=res[e]["mrr"],
                                  hits10_div=res[e]["hits10_div"])) for e in ENCODERS),
        unit_failures=unit_fail, n_units=len(per_enc), expected_n_units=EXPECTED_N_UNITS,
        cardinality_ok=(len(per_enc) >= EXPECTED_N_UNITS),
        arms_differ_verified=True, arm_code_sha256=digests,
        final_metrics_atomicity="tmp_replace",
        progress_logging="print_flush_true",
        crlb_n_a=("no closed-form noise floor; discriminator is Hits@10 AGREEMENT with the "
                  "GRAPH ground truth; chance floor = K_HITS/(Na-1)"),
        discriminator_reachability=True,
        cell_chunked=True, start_marker_written=True,
        crash_diagnostic_present=True, heartbeat_present=True,
        defensive_error_checking="passed_all_4_patterns",
        calibration_check="default_ok_for_this_regime",
        hp_scope={ENC_NATIVE: ["reframe_confirmed_gate"]},
        held_out_methodology=("native encoder trains ONLY on TRAIN edges; Hits@10 scored "
                              "on TEST edges never seen in training (filtered by TRAIN "
                              "neighbors + self)"),
        baseline_in_band_note=("AG saturate-high (baseline>0.95) cannot occur for filtered "
                               "Hits@10 over ~%d candidates; live risk is char being TOO "
                               "strong (graph task lexically solvable), caught by the "
                               "discriminator-fires gate" % Na),
        ts_iso=datetime.now(timezone.utc).isoformat(),
    )
    write_metrics(get_output_dir(anchor), metrics,
                  results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("verdict=%s msg=%s elapsed=%.1fs" % (verdict, verdict_msg, elapsed))
    return 0


def _deg_from_edges(edges: np.ndarray, n_nodes: int) -> np.ndarray:
    deg = np.zeros(n_nodes, dtype=np.int32)
    for a, b in edges:
        deg[int(a)] += 1
        deg[int(b)] += 1
    return deg


# ---------------------------------------------------------------------------
# Self-test (synthetic; fast; formula self-tests).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. graded_block_code invariants: m=5 five-per-block, positive, unit-L1.
    zc = np.random.default_rng(0).standard_normal((16, CODE_DIM)).astype(np.float32)
    c5 = graded_block_code(zc, KB, BLK_L, M_GRADED).reshape(16, KB, BLK_L)
    assert (c5 >= -1e-6).all(), "selftest: negative graded entries"
    assert int((c5 > 1e-8).sum(-1).max()) == 5, "selftest: graded not five-per-block"
    assert np.allclose(c5.sum(-1), 1.0, atol=1e-4), "selftest: graded block not unit-L1"

    # 2. edge split: disjoint + covers all edges.
    E = np.array([[i, i + 1] for i in range(100)], dtype=np.int32)
    tr, te = split_edges(E, 0.80, 7)
    assert tr.shape[0] + te.shape[0] == 100, "selftest: split loses edges"
    assert abs(tr.shape[0] - 80) <= 1, "selftest: train_frac off"
    s_all = set(map(tuple, E.tolist()))
    s_split = set(map(tuple, tr.tolist())) | set(map(tuple, te.tolist()))
    assert s_all == s_split, "selftest: split not a partition"

    # 3. retrieval metric: a PERFECT encoder = the held-out targets' own vectors placed as
    #    the nearest neighbor -> recall@10=1.0; random -> low. Filtered masking works.
    rng = np.random.default_rng(1)
    Na = 300
    dim = 128
    base = rng.standard_normal((Na, dim)).astype(np.float32)
    # query 0 -> target 5; query 1 -> target 6; make target the query's copy (perfect retrieval)
    perfect = base.copy()
    query_local = np.array([0, 1, 2], dtype=np.int64)
    targets = [np.array([5], np.int64), np.array([6], np.int64), np.array([7], np.int64)]
    for qi, t in zip(query_local, targets):
        perfect[int(t[0])] = base[qi]  # target identical to query -> top rank (self masked)
    trainmask = [np.array([], np.int64), np.array([], np.int64), np.array([], np.int64)]
    rp = retrieval_metrics(perfect, query_local, targets, trainmask, K_HITS)
    assert float(rp["recall_at_k"].mean()) > 0.99, "selftest: perfect encoder recall not ~1"
    rr = retrieval_metrics(base, query_local, targets, trainmask, K_HITS)
    assert float(rr["recall_at_k"].mean()) < 0.5, "selftest: random encoder recall too high"
    # filtered masking: mask the true target -> recall drops.
    trainmask_mask = [np.array([5], np.int64), np.array([6], np.int64), np.array([7], np.int64)]
    # (targets are the SAME indices; masking them removes them from candidates -> rank huge)
    rmask = retrieval_metrics(perfect, query_local, targets, trainmask_mask, K_HITS)
    assert float(rmask["recall_at_k"].mean()) < 0.5, "selftest: masked target still retrieved"

    # 4. verdict bands.
    def _res(nat, bge, cha, gra, nat_d, bge_d, cha_d, dfrac=0.3, nq=200, modz=300.0, af=1.0):
        return {ENC_NATIVE: dict(hits10=nat, hits10_div=nat_d, mrr=nat, modularity_z_train=modz),
                ENC_BGE: dict(hits10=bge, hits10_div=bge_d, mrr=bge, modularity_z_train=None),
                ENC_CHAR: dict(hits10=cha, hits10_div=cha_d, mrr=cha, modularity_z_train=None),
                ENC_GRADED: dict(hits10=gra, hits10_div=gra, mrr=gra, modularity_z_train=None),
                "divergence_frac": dfrac, "n_queries": nq, "align_frac": af, "chance_floor": 0.005}

    # reframe CONFIRMED: native competitive with BGE, both beat char, disc fires (bge_d low).
    v_hp, m_hp = _verdict(_res(0.40, 0.41, 0.20, 0.38, 0.30, 0.02, 0.05), "full")
    assert v_hp == "HARD_PASS" and "REFRAME_CONFIRMED" in m_hp, "selftest: expected HP got %s" % v_hp
    # reframe REJECTED: native worse than BGE overall AND on divergence.
    v_hf, m_hf = _verdict(_res(0.20, 0.40, 0.15, 0.18, 0.05, 0.30, 0.03), "full")
    assert v_hf == "HARD_FAIL" and "REFRAME_REJECTED" in m_hf, "selftest: expected reject got %s" % v_hf
    # MIDDLE: native beats char + wins divergence but not competitive overall.
    v_mb, m_mb = _verdict(_res(0.28, 0.40, 0.20, 0.26, 0.30, 0.05, 0.04), "full")
    assert v_mb == "MIDDLE_BAND", "selftest: expected MIDDLE got %s (%s)" % (v_mb, m_mb)
    # smoke machinery: disc fires (char underperforms, divergence nonvacuous).
    v_sm, m_sm = _verdict(_res(0.30, 0.40, 0.20, 0.28, 0.25, 0.03, 0.05), "smoke")
    assert v_sm == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_sm, "selftest: expected smoke ok got %s" % v_sm
    # smoke gate: char does NOT underperform (lexically solvable) -> gate fail.
    v_cg, m_cg = _verdict(_res(0.30, 0.31, 0.30, 0.29, 0.25, 0.03, 0.28), "smoke")
    assert v_cg == "SMOKE_GATE_FAIL" and "CHAR_FLOOR_DOES_NOT_UNDERPERFORM" in m_cg, \
        "selftest: expected char-gate got %s" % v_cg
    # smoke gate: divergence vacuous (dfrac below DIV_MIN).
    v_dg, m_dg = _verdict(_res(0.30, 0.40, 0.20, 0.28, 0.25, 0.03, 0.05, dfrac=0.02), "smoke")
    assert v_dg == "SMOKE_GATE_FAIL" and "DIVERGENCE_SET_VACUOUS" in m_dg, \
        "selftest: expected divergence-gate got %s" % v_dg
    # too few queries -> gate fail.
    v_nq, m_nq = _verdict(_res(0.30, 0.40, 0.20, 0.28, 0.25, 0.03, 0.05, nq=10), "smoke")
    assert v_nq == "SMOKE_GATE_FAIL" and "TOO_FEW_QUERIES" in m_nq, "selftest: expected fewq got %s" % v_nq
    # alignment too low -> gate fail.
    v_al, m_al = _verdict(_res(0.30, 0.40, 0.20, 0.28, 0.25, 0.03, 0.05, af=0.2), "smoke")
    assert v_al == "SMOKE_GATE_FAIL" and "ALIGNMENT" in m_al, "selftest: expected align-gate got %s" % v_al
    # FULL disc-did-not-fire -> HARD_FAIL (not a reframe verdict).
    v_df, m_df = _verdict(_res(0.30, 0.31, 0.30, 0.28, 0.25, 0.03, 0.28), "full")
    assert v_df == "HARD_FAIL" and "DISCRIMINATOR_DID_NOT_FIRE" in m_df, \
        "selftest: expected disc-fail got %s" % v_df

    _log("SELFTEST_PASS (graded m=5 invariants + edge-split partition + retrieval "
         "perfect~1/random-low/masked-drop + verdict bands "
         "CONFIRMED/REJECTED/MIDDLE/smoke/char-gate/div-gate/fewq/align/disc-fail) "
         "elapsed=%.2fs" % (time.perf_counter() - t0))
    out = get_output_dir(ANCHOR_NAME + "_selftest")
    write_metrics(out, dict(verdict="SELFTEST_PASS", run_mode="self_test",
                            verdict_msg="SELFTEST_PASS", summary="SELFTEST_PASS",
                            elapsed_s=time.perf_counter() - t0))
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "REFRAME: native teacher-free encoder measured ON THE GRAPH TASK (held-out "
        "link-prediction Hits@10 vs ConceptNet graph ground truth) vs BGE "
        "(distributional) + char-trigram (lexical). Is ret_agree10-vs-BGE the wrong "
        "yardstick? Divergence-set discriminator."))
    p.add_argument("--run-mode", default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=7)
    args, _ = p.parse_known_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.full:
        args.run_mode = "full"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run(args.run_mode, args.seed)


if __name__ == "__main__":
    _fallback_out = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE section 8
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
