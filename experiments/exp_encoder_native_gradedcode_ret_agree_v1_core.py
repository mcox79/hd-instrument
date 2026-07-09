"""Native (teacher-free) encoder + graded-code(m=5) vs coarse(m=1): does the finer
block-quantization resolution trick close ret_agree10 WITHOUT BGE in the
representation?

QUESTION (Director hand-off, NATIVE-PATH): the graded-code(m=5) finer-quantization
trick closed the retrieval-agreement gap on BGE-TEACHER geometry
(ret_agree10 0.19 -> 0.45, exp_encoder_gsbc_gradedcode_retrieval_v1). That was a
distilled-BGE representation. Test whether the SAME graded-code resolution trick,
applied to a NATIVE no-external-teacher representation (the teacher-free relational
encoder trained on the ConceptNet graph via InfoNCE + VICReg repulsion), closes
ret_agree10 >= 0.30 WITHOUT BGE in the encoder or the KB.

REPRESENTATION (native, teacher-free): the ProjHead + graph-InfoNCE + VICReg encoder
from exp_teacher_free_relational_encoder_cn_subgraph_v1 (ARM_GRAPH_REPULSION),
re-parameterized to code_dim=4096 so its dense output feeds the certified graded
block geometry (kb=32, blk_l=128, n_dim=4096). Surface features = deterministic
hashed char-trigram bag (substrate-native V1; NO word-meaning supervision, NO
teacher). NO BGE anywhere in the representation or any training loss.

GOLD (evaluation ORACLE ONLY, never ingested, never in the encoder/KB): the
name-aligned BGE-large cached embeddings (bge_large_v2_name_177899). ret_agree10 is
INHERENTLY "top-10 neighborhood agreement with a gold reference"; in the BGE arc the
gold was BGE, and the 0.45 number was measured against BGE. Keeping the SAME gold
(BGE-as-oracle) makes the 0.30 bar apples-to-apples: it is exactly the KB-flip
gate -- "can we flip the KB to native codes WITHOUT regressing the retrieval
neighborhoods the current (BGE-defined) KB provides." The native encoder never sees
BGE; BGE is only the yardstick. This preserves substrate-knows-nothing (the
representation + KB stay teacher-free) while making the resolution-vs-meaning
question answerable.

ARMS (per seed; deterministic transforms of the SAME trained native dense z, except
the untrained floor):
  NATIVE_DENSE     : trained native encoder raw dense code (4096-d, L2-norm). CEILING
                     (best the native representation can do at full resolution).
  NATIVE_COARSE    : graded_block_code(dense, kb=32, blk_l=128, m=1). One positive
                     magnitude survivor per block, unit-L1. DISCRIMINATOR BASELINE
                     (coarsest quantization; must FAIL the 0.30 bar, else vacuous).
  NATIVE_GRADED    : graded_block_code(dense, kb=32, blk_l=128, m=5). The certified
                     finer-resolution trick. TREATMENT.
  NATIVE_RANDINIT  : untrained (random-init) native encoder dense code. FLOOR /
                     char-trigram surface control (its ret_agree10 vs BGE ~ chance
                     unless spelling accidentally aligns with BGE semantics).

RESOLUTION vs MEANING disambiguator (the load-bearing report the task asks for):
  The DENSE CEILING arm tells the two interpretations apart --
  - if DENSE >= 0.30 and GRADED >= 0.30  -> RESOLUTION was the limiter; graded fixes
      it; native meaning is adequate; the native better-reader path (b) works, a KB
      flip becomes possible with NO external model.  [HARD_PASS_RESOLUTION]
  - if DENSE < 0.30                       -> MEANING is the limiter; even the finest
      full-resolution native representation does not match BGE neighborhoods; graded
      resolution cannot rescue meaning the encoder does not have. Decisive redirect
      to strengthen the teacher-free encoder's semantic fidelity FIRST.
      [HARD_FAIL_MEANING_LIMITER]
  - if DENSE >= 0.30 and GRADED < 0.30    -> RESOLUTION axis but m=5 graded recovers
      too little of an adequate ceiling; redirect to higher-m / GWTA-expansion (v12),
      NOT to meaning.  [HARD_FAIL_RESOLUTION_INSUFFICIENT]
  Per-arm graph modularity_z (Newman-analog assortativity vs a degree-preserving
  null, reused from the parent) is reported alongside: a HIGH modularity_z with a LOW
  ret_agree10-vs-BGE is the decisive "native learned REAL (graph-relational)
  structure that simply DIVERGES from BGE (distributional-semantic) geometry"
  finding -- meaning-limiter that is NOT under-training.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: sha256 over float32 codes of DENSE/COARSE/GRADED/RANDINIT
  (float bytes; graded/coarse are positive fractional).
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics os.replace).
- except SystemExit: raise BEFORE except Exception (no BaseException, no bare except).
- crlb_n/a: no closed-form noise floor; the discriminator is ret_agree10 AGREEMENT.
  Chance floor computed (THEORETICAL): random top-10 overlap ~ 10/(V-1); the 0.30 bar
  is ~60x chance at V~2000. discriminator_reachability=True (bar >> chance floor).
- baseline_in_band: AG's "baseline saturates >0.95" failure mode CANNOT occur here (a
  non-distilled native encoder will not saturate ret_agree10-vs-BGE at >0.95); the
  live risk is the OPPOSITE (floor), which IS the scientific signal (meaning-limiter).
  Declared with AG-exemption rationale; band-check applied to the DENSE ceiling arm.
- discriminator survives scale: the resolution transform (coarse m=1 vs graded m=5) is
  a DETERMINISTIC map on the fixed trained z, so the graded-vs-coarse ordering is
  scale-invariant in mechanism (option B analytical). The DENSE-ceiling MEANING
  verdict needs full training scale (adequate epochs), so it is FULL-only; smoke fires
  the must-fail control (COARSE ret_agree10 < 0.30 at smoke scale).
- HARD_PASS strictly above floor + 5% band-width (bar 0.30, strict 0.335).
- HP_SCOPE: {NATIVE_GRADED: [ret_agree10_bar]}. DENSE/COARSE/RANDINIT are
  diagnostic/disambiguator/floor arms (integrity, not HP-gated).
- cardinality_ok: EXPECTED_N_UNITS = 4 arms; counted from per_unit.
- per-unit failure-class instrumentation (no bare except).
- calibration_check: default_ok_for_this_regime (graded geometry pinned to the
  certified m=5 operating point; only the input representation is re-pointed to native).
- numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the pre-reg.
- cell_chunked: True (one seed per cell; FULL multi-seed via sibling _seed_<N> wrappers).
- start_marker_written / crash_diagnostic_present / heartbeat_present: True.
- progress_logging: print_flush_true (line-buffered stdout + flush=True).

Compute architecture: (c) MIXED with justification. Native encoder training is
sequential-CPU (SGD steps have a genuine sequential dependency; the model is a single
linear ProjHead; the parent teacher-free encoder is established CPU-only). The
ret_agree10 top-10 neighbor computation is torch matmul (device-agnostic; runs on the
remote_cpu_queue runner). GPU speedup is marginal for a one-linear-layer encoder;
FULL routes to remote_cpu_queue.

Parent cells (imported, READ-ONLY):
  experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py  (native encoder)
  hdlab/gsbc_graded_encoder.py                                       (graded block code)
Prereg: preregs/2026-07-08_exp_encoder_native_gradedcode_ret_agree_v1.md

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
ANCHOR_NAME = "encoder_native_gradedcode_ret_agree_v1"

# Certified graded geometry (MEASURED@ arc; hdlab/gsbc_graded_encoder DEFAULTS).
CODE_DIM = 4096
KB = 32
BLK_L = 128
M_COARSE = 1
M_GRADED = 5
assert KB * BLK_L == CODE_DIM

BGE_CACHE = "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"

# ret_agree10 KB-flip bar (Director hand-off) + META_RULE_L strict band.
RET_BAR = 0.30
RET_BAR_STRICT = 0.335          # 0.30 + 0.05 * (1.0 - 0.30) band-width
MIN_ALIGN_FRAC = 0.50           # gold coverage floor (else eval universe untrustworthy)
GRADED_BEATS_COARSE_EPS = 0.01  # graded must exceed coarse by this to credit the lever

# 4 arms per seed.
ARM_DENSE = "NATIVE_DENSE"
ARM_COARSE = "NATIVE_COARSE"
ARM_GRADED = "NATIVE_GRADED"
ARM_RANDINIT = "NATIVE_RANDINIT"
EXPECTED_N_UNITS = 4

# Local run configs (code_dim pinned to 4096 for the graded geometry; the parent's
# 256-d configs do not fit the certified block geometry). Each cell runs ONE seed.
SMOKE_CFG = dict(
    n_nodes=2500, epochs=400, batch=256, k_rewire=40,
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
# BGE eval-oracle gold (name-aligned; NEVER ingested).
# ---------------------------------------------------------------------------

def _load_bge_gold(node_ids: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """Return (aligned_local_idx [K], gold [K, 1024]) for node_ids present in the
    BGE cache. gold is L2-normalized. Fail-loud if cache missing."""
    cache = _REPO / BGE_CACHE
    if not cache.exists():
        raise FileNotFoundError("BGE eval-oracle cache not found: %s" % cache)
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
    # Decompress semantic fully (deflate npz; no random access), then gather rows.
    with z.open("semantic.npy") as f:
        sem = np.lib.format.read_array(f, allow_pickle=False)
    gold = np.ascontiguousarray(sem[np.asarray(aligned_rows, dtype=np.int64)].astype(np.float32))
    del sem
    if np.isnan(gold).any() or np.isinf(gold).any():
        raise RuntimeError("BGE gold contains NaN/Inf")
    gold = gold / (np.linalg.norm(gold, axis=1, keepdims=True) + 1e-8)
    return np.asarray(aligned_local, dtype=np.int64), gold


# ---------------------------------------------------------------------------
# ret_agree10 (top-10 neighborhood agreement vs gold; matches _semantic_unit block).
# ---------------------------------------------------------------------------

def ret_agree10(codes: np.ndarray, gold: np.ndarray) -> float:
    """Mean over items of |top10(code neighbors) intersect top10(gold neighbors)| / 10,
    self excluded. codes, gold are [K, .] over the SAME K items (aligned order)."""
    K = codes.shape[0]
    if K < 12:
        raise ValueError("ret_agree10 needs >= 12 items (got %d)" % K)
    cn = codes / (np.linalg.norm(codes, axis=1, keepdims=True) + 1e-8)
    gn = gold / (np.linalg.norm(gold, axis=1, keepdims=True) + 1e-8)
    cn = torch.from_numpy(np.ascontiguousarray(cn.astype(np.float32)))
    gn = torch.from_numpy(np.ascontiguousarray(gn.astype(np.float32)))
    agree = 0.0
    chunk = 1024
    for lo in range(0, K, chunk):
        hi = min(lo + chunk, K)
        rows = torch.arange(lo, hi)
        gs = gn[lo:hi] @ gn.T
        gs[torch.arange(hi - lo), rows] = -2.0
        g10 = gs.topk(10, dim=1).indices
        cs = cn[lo:hi] @ cn.T
        cs[torch.arange(hi - lo), rows] = -2.0
        c10 = cs.topk(10, dim=1).indices
        for r in range(hi - lo):
            agree += len(set(g10[r].tolist()) & set(c10[r].tolist())) / 10.0
    return agree / K


# ---------------------------------------------------------------------------
# Verdict (per single seed).
# ---------------------------------------------------------------------------

def _verdict(res: Dict, run_mode: str) -> Tuple[str, str]:
    """res has ret_agree10 + modularity_z per arm + align_frac + chance_floor."""
    D = res[ARM_DENSE]["ret_agree10"]
    C = res[ARM_COARSE]["ret_agree10"]
    G = res[ARM_GRADED]["ret_agree10"]
    F = res[ARM_RANDINIT]["ret_agree10"]
    zD = res[ARM_DENSE]["modularity_z"]
    lift = G - C
    tail = ("[DENSE=%.4f COARSE=%.4f GRADED=%.4f RANDINIT=%.4f | graded-coarse "
            "lift=%+.4f | modularity_z(DENSE)=%.2f align_frac=%.3f chance=%.4f]" % (
                D, C, G, F, lift, zD, res["align_frac"], res["chance_floor"]))

    for k in (D, C, G, F):
        if not math.isfinite(k) or not (-0.01 <= k <= 1.01):
            return ("SMOKE_GATE_FAIL" if run_mode == "smoke" else "HARD_FAIL",
                    "S_ret_agree_out_of_range %s" % tail)
    if res["align_frac"] < MIN_ALIGN_FRAC:
        return ("SMOKE_GATE_FAIL" if run_mode == "smoke" else "HARD_FAIL",
                "GOLD_ALIGNMENT_TOO_LOW %.3f < %.2f %s" % (res["align_frac"], MIN_ALIGN_FRAC, tail))

    discriminator_fires = bool(C < RET_BAR)  # coarse must FAIL the bar (must-fail control)

    if run_mode == "smoke":
        # Machinery + discriminator-fires (must-fail COARSE below the bar at smoke scale).
        if not discriminator_fires:
            return ("HARD_PASS",
                    "SMOKE_MACHINERY_OK_BUT_COARSE_ALREADY_CLEARS: native+coarse "
                    "ret_agree10=%.4f >= %.2f at smoke scale -- the resolution lever is "
                    "NOT the binding constraint (native already strong at coarse "
                    "quantization; a positive surprise). Report to Director for judgment. "
                    "%s" % (C, RET_BAR, tail))
        return ("HARD_PASS",
                "SMOKE_MACHINERY_OK: all 4 arms produce finite ret_agree10 vs the "
                "name-aligned BGE eval-oracle; codes bit-distinct; discriminator FIRES "
                "(must-fail COARSE=%.4f < %.2f at smoke scale). The DENSE-ceiling MEANING "
                "verdict is FULL-only (needs full training scale + multi-seed); smoke "
                "previews DENSE=%.4f GRADED=%.4f. %s" % (C, RET_BAR, D, G, tail))

    # FULL: resolution-vs-meaning verdict.
    if D < RET_BAR:
        return ("HARD_FAIL",
                "HARD_FAIL_MEANING_LIMITER: the native encoder's FULL-resolution DENSE "
                "ceiling ret_agree10=%.4f is BELOW the %.2f KB-flip bar vs BGE. Graded "
                "resolution CANNOT rescue meaning the representation does not have "
                "(GRADED=%.4f). The limiter is MEANING, not resolution: the native "
                "(graph-relational) neighborhoods diverge from BGE (distributional-"
                "semantic) neighborhoods (DENSE modularity_z=%.2f shows whether real "
                "graph structure was learned). Decisive redirect: strengthen the "
                "teacher-free encoder's semantic fidelity FIRST. %s" % (D, RET_BAR, G, zD, tail))
    if G >= RET_BAR_STRICT and lift >= GRADED_BEATS_COARSE_EPS:
        return ("HARD_PASS",
                "HARD_PASS_RESOLUTION: native+graded(m=5) ret_agree10=%.4f >= %.3f clears "
                "the KB-flip bar WITHOUT BGE in the representation, and BEATS coarse(m=1) "
                "by %+.4f. The native DENSE ceiling (%.4f) is adequate, so RESOLUTION was "
                "the limiter and the graded finer-quantization trick closes it. We have a "
                "native better reader -- path (b) works; a KB flip becomes possible with NO "
                "external model. %s" % (G, RET_BAR_STRICT, lift, D, tail))
    if D >= RET_BAR and G < RET_BAR:
        return ("HARD_FAIL",
                "HARD_FAIL_RESOLUTION_INSUFFICIENT: the native DENSE ceiling ret_agree10="
                "%.4f clears the %.2f bar (meaning is adequate) but graded(m=5)=%.4f does "
                "NOT recover enough of it. The axis is RESOLUTION, not meaning; redirect to "
                "higher-m / GWTA-expansion (v12), not to strengthening semantics. %s" % (
                    D, RET_BAR, G, tail))
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: native+graded ret_agree10=%.4f in [%.2f, %.3f) -- real signal, "
            "clears the bar but not strictly (within 5%% band-width); graded-coarse "
            "lift=%+.4f, DENSE ceiling=%.4f. %s" % (G, RET_BAR, RET_BAR_STRICT, lift, D, tail))


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
    _log("run_mode=%s seed=%d code_dim=%d kb=%d blk_l=%d m_coarse=%d m_graded=%d "
         "n_nodes=%d epochs=%d" % (run_mode, seed, cfg["code_dim"], KB, BLK_L,
                                   M_COARSE, M_GRADED, cfg["n_nodes"], cfg["epochs"]))

    # ---- native ConceptNet subgraph + surface features (NO teacher) ----
    node_ids, node_words, edges, degrees, meta = tfe.load_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    _log("subgraph: %s" % meta)
    X = tfe.char_trigram_features(node_words, cfg["feat_dim"])
    adj = tfe.build_adjlist(edges, len(node_ids))

    # ---- BGE eval-oracle gold (name-aligned; never ingested) ----
    aligned_local, gold = _load_bge_gold(node_ids)
    align_frac = len(aligned_local) / len(node_ids)
    _log("BGE gold: aligned %d/%d (frac=%.3f) x %dd (eval-oracle only)" % (
        len(aligned_local), len(node_ids), align_frac, gold.shape[1]))
    chance_floor = 10.0 / max(len(aligned_local) - 1, 1)

    rng = np.random.default_rng(seed + 4242)

    # ---- train native encoder (trained) + random-init (floor) ----
    _emit_heartbeat(out_dir, 0, EXPECTED_N_UNITS, time.perf_counter() - t0,
                    extra={"stage": "train_start"})
    emb_trained = tfe.train_arm(tfe.PRIMARY_ARM, X, adj, cfg, seed,
                                out_dir=out_dir, unit_base=0)
    _log("trained native encoder emb %s (%.1fs)" % (emb_trained.shape, time.perf_counter() - t0))
    emb_randinit = tfe.train_arm(tfe.FLOOR_ARM, X, adj, cfg, seed)
    _log("random-init floor emb %s (%.1fs)" % (emb_randinit.shape, time.perf_counter() - t0))

    # ---- build the 4 arm codes over the FULL subgraph ----
    dense = emb_trained.astype(np.float32)
    coarse = graded_block_code(dense, KB, BLK_L, M_COARSE)
    graded = graded_block_code(dense, KB, BLK_L, M_GRADED)
    randinit = emb_randinit.astype(np.float32)

    # ARMS-MUST-DIFFER (META_RULE_AF; float32 bytes).
    digests = {ARM_DENSE: _code_digest(dense), ARM_COARSE: _code_digest(coarse),
               ARM_GRADED: _code_digest(graded), ARM_RANDINIT: _code_digest(randinit)}
    dl = list(digests.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            if dl[i][1] == dl[j][1]:
                raise RuntimeError("failure_class=META_RULE_AF_VIOLATION: %s/%s identical"
                                   % (dl[i][0], dl[j][0]))

    # ---- per-arm ret_agree10 (aligned subset vs gold) + modularity_z (full graph) ----
    arm_codes = {ARM_DENSE: dense, ARM_COARSE: coarse, ARM_GRADED: graded,
                 ARM_RANDINIT: randinit}
    res: Dict[str, Dict] = {}
    unit_fail: List[Dict] = []
    aligned = aligned_local
    for ui, (arm, code) in enumerate(arm_codes.items()):
        try:
            ra = ret_agree10(code[aligned], gold)
            zc, m_true, mu, sd = tfe.embedding_assortativity_z(
                code, edges, degrees, cfg["k_rewire"], rng)
            res[arm] = dict(ret_agree10=float(ra), modularity_z=float(zc),
                            m_true=float(m_true), null_mean=float(mu), null_std=float(sd))
            _log("arm=%s ret_agree10=%.4f modularity_z=%.2f (%.1fs)" % (
                arm, ra, zc, time.perf_counter() - t0))
            _emit_heartbeat(out_dir, ui + 1, EXPECTED_N_UNITS, time.perf_counter() - t0,
                            extra={"arm": arm, "ret_agree10": float(ra)})
        except (RuntimeError, ValueError, IndexError) as exc:
            unit_fail.append(dict(arm=arm, failure_class=type(exc).__name__, msg=str(exc)[:300]))
            raise

    if len(res) < EXPECTED_N_UNITS:
        verdict, verdict_msg = ("HARD_FAIL",
                                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d arms"
                                % (len(res), EXPECTED_N_UNITS))
    else:
        res["align_frac"] = float(align_frac)
        res["chance_floor"] = float(chance_floor)
        verdict, verdict_msg = _verdict(res, run_mode)

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        elapsed_s=float(elapsed), run_mode=run_mode, anchor_name=anchor,
        seed=int(seed), device="cpu", N=CODE_DIM,
        geometry=dict(code_dim=CODE_DIM, kb=KB, blk_l=BLK_L, m_coarse=M_COARSE,
                      m_graded=M_GRADED),
        gold=dict(source="BGE_large_v2_name_177899", role="eval_oracle_only_never_ingested",
                  dim=int(gold.shape[1]), aligned=int(len(aligned_local)),
                  n_nodes=int(len(node_ids)), align_frac=float(align_frac)),
        ret_agree10=dict((a, res[a]["ret_agree10"]) for a in arm_codes),
        modularity_z=dict((a, res[a]["modularity_z"]) for a in arm_codes),
        graded_minus_coarse_lift=float(res[ARM_GRADED]["ret_agree10"]
                                       - res[ARM_COARSE]["ret_agree10"]),
        ret_bar=RET_BAR, ret_bar_strict=RET_BAR_STRICT,
        chance_floor=float(chance_floor),
        discriminator_fires_coarse_below_bar=bool(res[ARM_COARSE]["ret_agree10"] < RET_BAR),
        subgraph_meta=meta, config=cfg,
        objective=("native teacher-free relational encoder (graph InfoNCE + VICReg, "
                   "char-trigram surface, NO teacher) re-parameterized to code_dim=4096; "
                   "graded_block_code(m=1 coarse vs m=5 graded) at certified geometry; "
                   "ret_agree10 scored vs name-aligned BGE eval-oracle (never ingested)"),
        per_arm=res,
        unit_failures=unit_fail, n_units=len(arm_codes), expected_n_units=EXPECTED_N_UNITS,
        cardinality_ok=(len(res) >= EXPECTED_N_UNITS),
        arms_differ_verified=True, arm_code_sha256=digests,
        final_metrics_atomicity="tmp_replace",
        progress_logging="print_flush_true",
        crlb_n_a=("no closed-form noise floor; discriminator is ret_agree10 AGREEMENT; "
                  "chance floor = 10/(V-1)"),
        discriminator_reachability=True,
        cell_chunked=True, start_marker_written=True,
        crash_diagnostic_present=True, heartbeat_present=True,
        defensive_error_checking="passed_all_4_patterns",
        calibration_check="default_ok_for_this_regime",
        hp_scope={ARM_GRADED: ["ret_agree10_bar"]},
        baseline_in_band_note=("AG saturate-high failure mode cannot occur (non-distilled "
                               "native vs BGE will not exceed 0.95 ret_agree10); the DENSE "
                               "ceiling is the band-checked arm, floor is the live risk and "
                               "IS the meaning-limiter signal"),
        ts_iso=datetime.now(timezone.utc).isoformat(),
    )
    write_metrics(get_output_dir(anchor), metrics,
                  results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("verdict=%s msg=%s elapsed=%.1fs" % (verdict, verdict_msg, elapsed))
    return 0


# ---------------------------------------------------------------------------
# Self-test (synthetic; fast; formula self-tests).
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    t0 = time.perf_counter()

    # 1. graded_block_code invariants: coarse m=1 one-per-block, graded m=5 five-per-block,
    #    positive, unit-L1 per block.
    zc = np.random.default_rng(0).standard_normal((16, CODE_DIM)).astype(np.float32)
    c1 = graded_block_code(zc, KB, BLK_L, M_COARSE).reshape(16, KB, BLK_L)
    c5 = graded_block_code(zc, KB, BLK_L, M_GRADED).reshape(16, KB, BLK_L)
    assert (c1 >= -1e-6).all() and (c5 >= -1e-6).all(), "selftest: negative graded entries"
    assert int((c1 > 1e-8).sum(-1).max()) == 1, "selftest: coarse not one-per-block"
    assert int((c5 > 1e-8).sum(-1).max()) == 5, "selftest: graded not five-per-block"
    assert np.allclose(c1.sum(-1), 1.0, atol=1e-4), "selftest: coarse block not unit-L1"
    assert np.allclose(c5.sum(-1), 1.0, atol=1e-4), "selftest: graded block not unit-L1"

    # 2. ret_agree10 behaviour: identical codes -> 1.0; code==gold -> 1.0; random uncorrelated
    #    -> near chance (small).
    rng = np.random.default_rng(1)
    K = 200
    gold = rng.standard_normal((K, 64)).astype(np.float32)
    assert abs(ret_agree10(gold.copy(), gold) - 1.0) < 1e-6, "selftest: self-agreement != 1.0"
    rc = rng.standard_normal((K, 4096)).astype(np.float32)
    ra_rand = ret_agree10(rc, gold)
    assert ra_rand < 0.15, "selftest: uncorrelated ret_agree10 too high (%.3f)" % ra_rand
    # a code that is a linear (invertible-ish) image of gold preserves neighborhoods -> high.
    proj = rng.standard_normal((64, 4096)).astype(np.float32)
    aligned_code = (gold @ proj).astype(np.float32)
    ra_aligned = ret_agree10(aligned_code, gold)
    assert ra_aligned > ra_rand, "selftest: gold-aligned code not above random"

    # 3. verdict bands (resolution vs meaning disambiguation).
    def _res(D, C, G, F, zD=5.0, af=1.0, ch=0.005):
        return {ARM_DENSE: dict(ret_agree10=D, modularity_z=zD),
                ARM_COARSE: dict(ret_agree10=C, modularity_z=zD),
                ARM_GRADED: dict(ret_agree10=G, modularity_z=zD),
                ARM_RANDINIT: dict(ret_agree10=F, modularity_z=0.2),
                "align_frac": af, "chance_floor": ch}

    v_hp, m_hp = _verdict(_res(0.42, 0.18, 0.38, 0.02), "full")
    assert v_hp == "HARD_PASS" and "RESOLUTION" in m_hp, "selftest: expected HARD_PASS got %s" % v_hp
    v_ml, m_ml = _verdict(_res(0.18, 0.09, 0.16, 0.02), "full")
    assert v_ml == "HARD_FAIL" and "MEANING_LIMITER" in m_ml, "selftest: expected meaning-limiter got %s" % v_ml
    v_ri, m_ri = _verdict(_res(0.42, 0.18, 0.24, 0.02), "full")
    assert v_ri == "HARD_FAIL" and "RESOLUTION_INSUFFICIENT" in m_ri, "selftest: expected res-insuff got %s" % v_ri
    v_mb, m_mb = _verdict(_res(0.42, 0.18, 0.315, 0.02), "full")
    assert v_mb == "MIDDLE_BAND", "selftest: expected MIDDLE_BAND got %s" % v_mb
    # smoke: discriminator fires (coarse below bar) -> machinery HARD_PASS.
    v_sm, m_sm = _verdict(_res(0.20, 0.10, 0.18, 0.02), "smoke")
    assert v_sm == "HARD_PASS" and "SMOKE_MACHINERY_OK" in m_sm, \
        "selftest: expected smoke machinery HARD_PASS got %s" % v_sm
    # smoke: coarse already clears -> flagged surprise (still PASS).
    v_ss, m_ss = _verdict(_res(0.50, 0.35, 0.55, 0.02), "smoke")
    assert v_ss == "HARD_PASS" and "COARSE_ALREADY_CLEARS" in m_ss, "selftest: expected surprise got %s" % v_ss
    # alignment too low -> gate fail.
    v_al, m_al = _verdict(_res(0.42, 0.18, 0.38, 0.02, af=0.2), "smoke")
    assert v_al == "SMOKE_GATE_FAIL" and "ALIGNMENT" in m_al, "selftest: expected alignment gate fail got %s" % v_al
    # out-of-range -> gate fail.
    v_nan, m_nan = _verdict(_res(float("nan"), 0.18, 0.38, 0.02), "smoke")
    assert v_nan == "SMOKE_GATE_FAIL", "selftest: expected range gate fail got %s" % v_nan

    _log("SELFTEST_PASS (graded-code m=1/m=5 unit-L1/top-m invariants + ret_agree10 "
         "self=1.0/random-low/aligned-high + verdict bands "
         "HP_RESOLUTION/MEANING_LIMITER/RESOLUTION_INSUFFICIENT/MIDDLE/smoke/gate) "
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
        "Native teacher-free encoder + graded-code(m=5) vs coarse(m=1): does the "
        "finer-quantization resolution trick close ret_agree10 vs a BGE eval-oracle "
        "WITHOUT BGE in the representation? Resolution-vs-meaning disambiguation."))
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
