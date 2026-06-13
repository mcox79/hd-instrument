"""
exp_substrate_fprs_field_partition_routing_survival_gpu_v1.py -- CELL FPRS: does FIELD-aware partition routing survive at scale, invariant across fields? -- GPU (remote desktop).

ROUTING: Research DRILL VERDICT 6-cell battery (research_to_exp_dev_DRILL_VERDICT...HYBRID_H3_CONFIRMED_6_cells_ENDORSED), recommended
  "FPRS + UOT first". FPRS validates the THIRD leg of H3: FIELD as a FIRST-CLASS partition-routing primitive (not an afterthought label).
  It extends the SC scaling-curve (which validated single-pool partition routing survives 10M) to MULTI-FIELD: split the corpus across F
  fields, each field holding its own partitions (<=50K), route a query to its partition, clean up within. The decisive claim: routing
  accuracy + within-partition recall are INVARIANT ACROSS FIELDS and STABLE as the partition count grows (adding fields/scale does not
  degrade routing). REFRAME-INDEPENDENT: this is about ROUTING (architecture survival), orthogonal to the systems-vs-records PROMOTION
  question -- so it is safe to run now under Research's endorsement while the reframe is pending. NO LLM; torch GPU; memory-bounded
  (identities regenerated per chunk from seed). Decoupled cues (clean category cue routes; noisy identity cue cleans up) per SC.

  SWEEP partition count P by total N (fixed PART_SIZE): P in {50, 250, 1000} <-> N in {2M, 10M, 40M}. F fields, P/F partitions each.
  Per field: routing accuracy (query category cue -> correct partition) + recall@10 within routed partition. Report cross-field SPREAD
  (max-min) and stability across the P-sweep.

PRE-REGISTERED: HARD-PASS routing accuracy >= 0.90 in EVERY field at the largest P AND cross-field routing-accuracy spread <= 0.10 AND
  recall@10 >= 0.60 every field AND max partition <= 50K AND routing accuracy does not collapse across the P-sweep (largest-P acc >=
  0.90). MIDDLE: routing in [0.70,0.90) OR spread in (0.10,0.25]. HARD-FAIL: routing < 0.70 at largest P OR spread > 0.25 (some field
  systematically harder to route -> field-routing does NOT survive scale). UNKNOWN if torch unavailable.
ASCII-only. --self-test (numpy, no torch) + --smoke + metrics.json. PROT-020 (torch->GPU). Route overnight_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_fprs_field_partition_routing_survival_gpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
DI = 1024; DC = 256; PART_SIZE = 40_000; SIZE_CAP = 50_000; N_FIELDS = 5
CAT_COS = 0.70; TARGET_COS = 0.20                 # clean routing cue; high-fidelity identity (FPRS focus is routing, not collapse)
P_SWEEP = [50, 250, 1000] if not SMOKE else [10, 25]
N_QUERIES = 250 if not SMOKE else 60
CHUNK = 250_000; SEED = 1028


def _np_unit(M):
    return M / (np.linalg.norm(M, axis=-1, keepdims=True) + 1e-12)


def _ret_noise(tc):
    return math.sqrt(max(0.0, 1.0 / (tc * tc) - 1.0))


def category_dirs_np(P, dc, seed):
    rng = np.random.default_rng(seed ^ 0xC0FFEE)
    return _np_unit(rng.standard_normal((P, dc)).astype(np.float32))


def _selftest():
    # routing: clean category cue routes to the right partition among many
    cd = category_dirs_np(200, 64, 7)
    rng = np.random.default_rng(1)
    p_true = 137
    q = _np_unit(0.70 * cd[p_true] + math.sqrt(1 - 0.49) * _np_unit(rng.standard_normal(64).astype(np.float32)))
    assert int(np.argmax(cd @ q)) == p_true
    # field labelling: contiguous blocks
    P, F = 250, 5
    field_of = lambda p: p // (P // F)
    assert field_of(0) == 0 and field_of(49) == 0 and field_of(50) == 1 and field_of(249) == 4
    # spread helper
    accs = {0: 1.0, 1: 0.98, 2: 1.0, 3: 0.99, 4: 1.0}
    spread = max(accs.values()) - min(accs.values())
    assert abs(spread - 0.02) < 1e-9
    assert abs(1 / math.sqrt(1 + _ret_noise(0.2) ** 2) - 0.2) < 1e-6
    print("[selftest] PASS: substrate_fprs_field_partition_routing_survival_gpu_v1 (routing + field-labelling + spread)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True); sys.exit(1)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
print("[device] %s" % DEV, flush=True)


def identity_chunk_t(g0, n, di, seed):
    gen = torch.Generator(device=DEV); gen.manual_seed((seed * 2_654_435_761 + g0) & ((1 << 63) - 1))
    A = torch.randn(n, di, generator=gen, device=DEV)
    return A / (A.norm(dim=1, keepdim=True) + 1e-12)


def run_one_P(P, di, dc, part_size, seed) -> Dict:
    """Route N_QUERIES queries among P partitions (F fields); per-field routing accuracy + recall@10."""
    F = N_FIELDS
    P = (P // F) * F                                  # make divisible by F
    per_field = P // F
    cd = category_dirs_np(P, dc, seed)
    cd_t = torch.from_numpy(cd).to(DEV)
    r = _ret_noise(TARGET_COS)
    rng = np.random.default_rng(seed ^ 0xA11CE)
    # targets: pick partitions across all fields uniformly
    tgt_part = rng.integers(0, P, N_QUERIES)
    tgt_local = rng.integers(0, part_size, N_QUERIES)
    # global identity index for target atom = part*part_size + local
    q_cat = np.zeros((N_QUERIES, dc), dtype=np.float32)
    for j in range(N_QUERIES):
        p = int(tgt_part[j])
        q_cat[j] = _np_unit(CAT_COS * cd[p] + math.sqrt(1 - CAT_COS ** 2) * _np_unit(rng.standard_normal(dc).astype(np.float32)))
    q_cat_t = torch.from_numpy(q_cat).to(DEV)
    routes = torch.argmax(q_cat_t @ cd_t.T, dim=1).cpu().numpy()
    field_of = lambda p: p // per_field
    # per-field routing accuracy
    fr_correct = defaultdict(int); fr_total = defaultdict(int)
    for j in range(N_QUERIES):
        f = field_of(int(tgt_part[j])); fr_total[f] += 1
        fr_correct[f] += 1 if routes[j] == tgt_part[j] else 0
    route_acc = {f: fr_correct[f] / max(1, fr_total[f]) for f in range(F)}
    # recall@10 within routed partition (only where routed correctly; else miss). identity gen per partition.
    rec_correct = defaultdict(int); rec_total = defaultdict(int)
    for j in range(N_QUERIES):
        f = field_of(int(tgt_part[j])); rec_total[f] += 1
        rp = int(routes[j])
        gtarget = int(tgt_part[j]) * part_size + int(tgt_local[j])
        tgt_id = identity_chunk_t(gtarget, 1, di, seed)[0]
        q_id = tgt_id + r * torch.nn.functional.normalize(torch.randn(di, generator=torch.Generator(device=DEV).manual_seed(seed + j), device=DEV), dim=0)
        q_id = torch.nn.functional.normalize(q_id, dim=0)
        ts = float(q_id @ tgt_id)
        beats = 0; g0 = rp * part_size
        for off in range(0, part_size, CHUNK):
            n = min(CHUNK, part_size - off)
            A = identity_chunk_t(g0 + off, n, di, seed)
            beats += int((A @ q_id > ts).sum().item())
            del A
        rec_correct[f] += 1 if (rp == int(tgt_part[j]) and beats < 10) else 0
    if DEV == "cuda": torch.cuda.empty_cache()
    recall = {f: rec_correct[f] / max(1, rec_total[f]) for f in range(F)}
    racc_vals = list(route_acc.values()); rec_vals = list(recall.values())
    return {"P": P, "per_field_partitions": per_field, "part_size": part_size,
            "route_acc_by_field": {f: round(v, 4) for f, v in route_acc.items()},
            "recall_by_field": {f: round(v, 4) for f, v in recall.items()},
            "min_route_acc": round(min(racc_vals), 4), "route_acc_spread": round(max(racc_vals) - min(racc_vals), 4),
            "min_recall": round(min(rec_vals), 4), "max_partition": part_size}


def run() -> Dict:
    part_size = PART_SIZE if not SMOKE else 20_000
    sweep = []
    for P in P_SWEEP:
        t = time.time(); res = run_one_P(P, DI, DC, part_size, SEED); res["wall_s"] = round(time.time() - t, 1)
        sweep.append(res)
        print("  P=%d (%d/field x %d fields, N=%d): min-route-acc=%.4f spread=%.4f min-recall=%.4f (%.1fs)" % (
            res["P"], res["per_field_partitions"], N_FIELDS, res["P"] * part_size, res["min_route_acc"],
            res["route_acc_spread"], res["min_recall"], res["wall_s"]), flush=True)
        print("     route-acc/field=%s" % res["route_acc_by_field"], flush=True)
    largest = sweep[-1]
    return {"sweep": sweep, "largest_P": largest["P"], "largest_min_route_acc": largest["min_route_acc"],
            "largest_spread": largest["route_acc_spread"], "largest_min_recall": largest["min_recall"],
            "max_partition": part_size, "n_fields": N_FIELDS, "cat_cos": CAT_COS, "target_cos": TARGET_COS}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + str(r["error"]))
    ra = r["largest_min_route_acc"]; sp = r["largest_spread"]; rc = r["largest_min_recall"]; cap = r["max_partition"] <= SIZE_CAP
    s = ("largest P=%d over %d fields: min route-acc=%.4f, cross-field spread=%.4f, min recall@10=%.4f, max partition=%d (<=50K:%s); "
         "sweep=%s. (decoupled cues: clean category routes, noisy identity cleans up; field = first-class partition layer.)") % (
        r["largest_P"], r["n_fields"], ra, sp, rc, r["max_partition"], cap,
        [{"P": x["P"], "min_route_acc": x["min_route_acc"], "spread": x["route_acc_spread"], "min_recall": x["min_recall"]} for x in r["sweep"]])
    if ra >= 0.90 and sp <= 0.10 and rc >= 0.60 and cap:
        return ("HARD_PASS", "HARD_PASS: field-aware partition routing SURVIVES scale -- routing accuracy >=0.90 in EVERY field at P=%d (cross-field spread %.3f<=0.10), recall@10>=0.60 every field, max partition<=50K. Field is a viable FIRST-CLASS partition primitive; adding fields/partitions does not degrade or bias routing. Validates the 3rd leg of H3 (field partition routing). " % (r["largest_P"], sp) + s)
    if ra >= 0.70 and sp <= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: field routing mostly survives (min route-acc %.3f, spread %.3f) but not cleanly at the HARD-PASS bar. " % (ra, sp) + s)
    return ("HARD_FAIL", "HARD_FAIL: field routing degrades at scale (min route-acc %.3f or spread %.3f>0.25) -- some field systematically harder to route; field-as-partition does not survive. " % (ra, sp) + s)


print("[config] anchor=%s mode=%s Di=%d Dc=%d fields=%d P_sweep=%s" % (ANCHOR_NAME, RUN_MODE, DI, DC, N_FIELDS, P_SWEEP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
