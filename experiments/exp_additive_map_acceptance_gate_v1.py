"""ACCEPTANCE GATE for the promoted live capability hdlab/additive_map.py::AdditiveKGMap.

Scaffold-free witness: fits the additive inductive map LIVE VIA THE CLASS on the CSKG held-out-ENTITY arena and
reproduces the VET-confirmed held-out-entity ANCHOR_COMPOSE MRR ~0.1282
(MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE=0.12821,
verdict HARD_PASS_INDUCTIVE_ANCHOR_COMPOSE, run_mode full, device cuda). The mechanism is driven ONLY through the
class (fit -> compose_into_table -> score); the ARENA helpers (split, filtered MRR) are imported verbatim from the
already-VET-confirmed cell so the comparison is apples-to-apples. The fit run PERSISTS the seed-7 map codes one-time
(the whole point of the promotion: future analyses re-SCORE instead of re-FIT).

ACCEPTANCE (pre-registered, ceiling-aware; VET mean = 0.12821):
  PASS if mean ANCHOR_COMPOSE MRR over seeds [7,13,17] in [0.10, 0.16] (VET +/- ~0.02, device-float tolerance)
  AND ANCHOR fires vs the RANDOM null (anchor_mrr - random_mrr > 0) AND the relation signal holds vs SCRAMBLE
  (anchor_mrr - scramble_mrr > 0) AND the seed-7 fitted map round-trips through save/load. Reproduction is
  bit-faithful by construction: the class's LearnedSGDCoordinateSource calls the SAME fit_kge_anchor1 with the SAME
  (k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, reciprocal, lr=A1_LR) and the SAME compose op on the SAME
  pinned index maps; only device-float summation order can drift the MRR.

## Compute architecture
class (a/c) MIXED: CSKG stream + held-out-entity split + filtered MRR = sequential-CPU graph ops; the additive fit
= minibatch SGD (batched matmul, GPU-batching-mandatory, neg-chunked); compose = one vectorized index_add bundle
(zero training); readout = query-chunked batched matmul (the (nq,N) map is never whole). Storage SHARDED (each entity
its own coord row; relations = per-TYPE additive displacements; the only bundle is the per-ENTITY anchor mean).
device=auto (cuda on the GPU host; matches the VET device); remote_cpu forces cpu. Seeds run sequentially in one
process with empty_cache between (single additive fit each -> no OOM risk). Read-only w.r.t. KGStore (zero regression).

# CELL-TEMPLATE: except SystemExit before except Exception (no BaseException/bare except); start-marker;
# crash-diagnostic; heartbeat; atomic metrics via write_metrics; progress_logging print_flush_true; run_mode verified.

ASCII-only. No emojis.
"""

import argparse
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

from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._kge_anchor1_fit import A1_LR  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores,
)
from experiments.exp_anchor_compose_inductive_entity_cskg_v1 import (  # noqa: E402
    build_heldout_entity_split_ac, build_planted_transe_arena,
)

ANCHOR_NAME = "additive_map_acceptance_gate_v1"

# ---- reproduction target (VET) + pre-registered acceptance band ----
VET_ANCHOR_MRR = 0.12821    # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json (3-seed mean)
REPRO_MRR_LO = 0.10
REPRO_MRR_HI = 0.16
EVAL_KS = (1, 3, 10, 100)

# ---- fit hyperparams pinned to the VET config (any drift breaks bit-faithful reproduction) ----
FIT_K = 24
FIT_EPOCHS = 500
FIT_KW = dict(reciprocal=True, lr=A1_LR, n_neg=128, batch_size=8192, neg_chunk=16)
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5
N_EVAL = 3000
FULL_SEEDS = [7, 13, 17]

# ---- self-test planted-arena bands (fast, CPU, class-driven) ----
ST_ANCHOR_MIN = 0.12
ST_BEATS_RANDOM = 0.05
ST_BEATS_SCRAMBLE = 0.03


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.5f" % x) if (x == x) else "nan"


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(out_dir), exist_ok=True)
    tmp = os.path.join(str(out_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(out_dir), "_start_marker.json"))


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(out_dir), exist_ok=True)
    tmp = os.path.join(str(out_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(out_dir), "metrics.json"))


def _heartbeat(out_dir, t0, tag, i):
    with open(os.path.join(str(out_dir), "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                            "elapsed_s": time.perf_counter() - t0}) + "\n")


def _resolve_device(arg_device):
    env = os.environ.get("HDLAB_QUEUE", ""); env_dev = os.environ.get("HDLAB_DEVICE", "")
    if arg_device == "cpu" or env_dev == "cpu" or env == "remote_cpu_queue":
        return torch.device("cpu")
    want_cuda = arg_device in ("auto", "cuda") or env_dev == "cuda"
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


# ---------------------------------------------------------------------------
# Score the three zero-training arms (ANCHOR / SCRAMBLE / RANDOM) from ONE class-driven additive fit.
# ---------------------------------------------------------------------------

def _score_arms(kmap, support_int, query_int, all_true, N, n_rel, device, seed):
    Xac, _deg = kmap.compose_into_table(support_int)                        # ANCHOR: zero-training bundle
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)   # SCRAMBLE: shuffle support relation ids
    Xscr, _ = kmap.compose_into_table(support_int, rel_perm=rel_perm)
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)          # RANDOM null (matches the VET cell)
    Xr = (torch.randn(N, kmap.k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, kmap.k, generator=gR) * 0.1).to(device)
    out = {}
    for name, X, D in [("ANCHOR", Xac, kmap.D), ("SCRAMBLE", Xscr, kmap.D), ("RANDOM", Xr, Dr)]:
        sc = additive_direct_scores(X, D, query_int, device)
        out[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
    return out


def _run_seed(pool_lbl, seed, device, out_dir, persist):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N, n_rel = len(ent2i), len(rel2i)
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
        pool_lbl, ent2i, HELDOUT_ENTITY_FRAC, SUPPORT_FRAC, seed)
    n_query_total = len(query_lbl)
    if n_query_total > N_EVAL:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=N_EVAL, replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    # LIVE: fit the map via the class (pin the pool vocab so held-out rows exist), same hyperparams as the VET.
    kmap = AdditiveKGMap(device=device).fit(train_lbl, entities=ent2i, relations=rel2i,
                                             k=FIT_K, epochs=FIT_EPOCHS, seed=seed, **FIT_KW)
    if persist:
        pdir = os.path.join(str(out_dir), "fitted_map_seed%d" % seed)
        kmap.save(pdir)
        # verify the persisted map re-loads and re-scores identically (persistence is the load-bearing promotion gap)
        reloaded = AdditiveKGMap.load(pdir, device="cpu")
        s0 = kmap.score_all(int(query_int[0, 0]), int(query_int[0, 1])).cpu()
        s1 = reloaded.score_all(int(query_int[0, 0]), int(query_int[0, 1])).cpu()
        persist_ok = bool(torch.allclose(s0, s1) and reloaded.entity_to_idx == kmap.entity_to_idx)
    else:
        pdir, persist_ok = None, None

    arms = _score_arms(kmap, support_int, query_int, all_true, N, n_rel, device, seed)
    res = dict(seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
               n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
               n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
               anchor_mrr=arms["ANCHOR"]["mrr"], scramble_mrr=arms["SCRAMBLE"]["mrr"],
               random_mrr=arms["RANDOM"]["mrr"],
               anchor_spectrum={("hits@%d" % k): arms["ANCHOR"]["hits@%d" % k] for k in EVAL_KS},
               persisted_dir=pdir, persist_reload_ok=persist_ok)
    del kmap
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return res


# ---------------------------------------------------------------------------
# Self-test: planted TransE arena, class-driven end-to-end (fit/compose/score/persist). Fast, CPU, deterministic.
# ---------------------------------------------------------------------------

def selftest(out_dir):
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        pool = build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
        res = _run_seed(pool, 7, device, out_dir, persist=True)
        a, s, r = res["anchor_mrr"], res["scramble_mrr"], res["random_mrr"]
        checks = dict(
            anchor_recovers=bool(a == a and a >= ST_ANCHOR_MIN),
            beats_random=bool(a == a and r == r and (a - r) >= ST_BEATS_RANDOM),
            beats_scramble=bool(a == a and s == s and (a - s) >= ST_BEATS_SCRAMBLE),
            persist_ok=bool(res.get("persist_reload_ok")),
        )
        ok = all(checks.values())
        res["selftest_checks"] = checks
        return ok, res
    finally:
        torch.set_num_threads(_prev)


# ---------------------------------------------------------------------------
# Core.
# ---------------------------------------------------------------------------

def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    seeds = [7] if run_mode == "self_test" else FULL_SEEDS
    _write_start_marker(out_dir, run_mode, len(seeds))
    t0 = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s seeds=%s" % (device, torch.cuda.is_available(), run_mode, seeds))

    st_ok, st_res = selftest(out_dir)
    _heartbeat(out_dir, t0, "selftest", 0)
    _log("selftest ok=%s anchor=%s scramble=%s random=%s persist_ok=%s"
         % (st_ok, _fmt(st_res["anchor_mrr"]), _fmt(st_res["scramble_mrr"]), _fmt(st_res["random_mrr"]),
            st_res.get("persist_reload_ok")))
    if not st_ok:
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                                    verdict_msg="SELFTEST_FAILED (class-driven planted arena): %s" % st_res.get("selftest_checks"),
                                    summary="selftest failed", elapsed_s=time.perf_counter() - t0, selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS AdditiveKGMap live API (fit/compose/insert/score/persist) reproduces the "
                        "anchor-beats-random+scramble discriminator on the planted arena",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(verdict="HARD_FAIL", run_mode=run_mode,
                                    verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
                                    elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    per_seed, failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(0, 12, 0, seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res = _run_seed(pool, seed, device, out_dir, persist=(seed == FULL_SEEDS[0]))
            per_seed.append(res)
            _log("seed=%d nq=%d ANCHOR_mrr=%s RANDOM_mrr=%s SCRAMBLE_mrr=%s persisted=%s (%.1fs)"
                 % (seed, res["n_query_scored"], _fmt(res["anchor_mrr"]), _fmt(res["random_mrr"]),
                    _fmt(res["scramble_mrr"]), res.get("persisted_dir"), time.time() - ts))
            _heartbeat(out_dir, t0, "cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < len(seeds):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                                    verdict_msg="expected %d seeds got %d (failures=%s)" % (len(seeds), len(per_seed), failures),
                                    summary="cardinality breach", elapsed_s=time.perf_counter() - t0,
                                    seed_failures=failures, selftest=st_res))
        raise SystemExit(1)

    def _mean(key):
        vals = [ps[key] for ps in per_seed if ps[key] == ps[key]]
        return float(np.mean(vals)) if vals else float("nan")

    anchor = _mean("anchor_mrr"); random_m = _mean("random_mrr"); scramble = _mean("scramble_mrr")
    in_band = bool(anchor == anchor and REPRO_MRR_LO <= anchor <= REPRO_MRR_HI)
    fires = bool(anchor == anchor and random_m == random_m and (anchor - random_m) > 0.0)
    relation_signal = bool(anchor == anchor and scramble == scramble and (anchor - scramble) > 0.0)
    persist_ok = bool(any(ps.get("persist_reload_ok") for ps in per_seed))
    accepted = bool(in_band and fires and relation_signal and persist_ok)

    verdict = "ACCEPTANCE_PASS_ADDITIVE_MAP_REPRODUCES_VET" if accepted else "ACCEPTANCE_FAIL"
    verdict_msg = (
        "%s || mean ANCHOR_COMPOSE MRR=%s vs VET=%.5f (band [%.2f,%.2f] in_band=%s) | fires_vs_random=%s "
        "(random=%s) | relation_signal_vs_scramble=%s (scramble=%s) | persist_reload_ok=%s | seeds=%s | "
        "fit driven LIVE via hdlab.additive_map.AdditiveKGMap (coord_source=learned_sgd_kge_anchor1)"
        % (verdict, _fmt(anchor), VET_ANCHOR_MRR, REPRO_MRR_LO, REPRO_MRR_HI, in_band, fires, _fmt(random_m),
           relation_signal, _fmt(scramble), persist_ok, [ps["seed"] for ps in per_seed]))

    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device),
                   vet_anchor_mrr=VET_ANCHOR_MRR, mean_anchor_mrr=anchor, mean_random_mrr=random_m,
                   mean_scramble_mrr=scramble, in_band=in_band, fires=fires, relation_signal=relation_signal,
                   persist_ok=persist_ok, accepted=accepted, band=[REPRO_MRR_LO, REPRO_MRR_HI],
                   per_seed=per_seed, seed_failures=failures, selftest=st_res, fit_kw=FIT_KW,
                   fit_config=dict(k=FIT_K, epochs=FIT_EPOCHS))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "full"):
            run_mode = env_mode
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
