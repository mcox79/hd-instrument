"""Course-C ORACLE capacity ladder: WHY did the transductive ORACLE collapse from ~1.0 (grid / 3k-node smoke)
to 0.023 at the full 25.7k-entity CSKG core, and what MINIMUM fit/readout capacity makes it FIRE again?

The ORACLE precondition. The transductive ORACLE fits coords on train + the held-out edges (it SEES the
answers) and must recover them via the readout. If it cannot, the reasoning question (does geometry beat
frequency on genuinely-held-out L2 edges) is not even ASKABLE -- the collapse is a fit/readout capacity
artifact, not a substrate-reasoning wall. The decisive FULL run (course_c_map_builder_cskg_l2_genuine_v1)
landed INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT: oracle=0.023 vs random=0.000. This cell LOCATES the capacity
that fires the oracle BEFORE spending a full 3-seed re-run.

TWO CANDIDATE BOTTLENECKS, disentangled per ladder point:
  (1) FIT capacity  -- the original fit_transe_coords is FULL-BATCH margin-rank: `epochs` gradient steps TOTAL
      (600 for the full run) with the margin loss only pushing gold above KGE_NEG=10 random negatives. At 485k
      edges that is under-trained + weak ranking pressure. Levers: more epochs, MINIBATCH SGD, and the Anchor-1
      recipe (CE self-adversarial loss + N3 + reciprocal relations; Sun 2019 / Lacroix 2018).
  (2) READOUT capacity -- the FPE bounded-kernel readout (dim=4096) may not resolve gold out of 25.7k even
      given a good fit. Lever: readout dim, and the DIRECT-DISTANCE readout as a fit-only-limited reference.

Per ladder point we fit the transductive ORACLE and measure filtered hits@10 under BOTH readouts:
  oracle_fpe    = FPE bounded-kernel readout (the MANDATED geometric readout; this is the gate).
  oracle_direct = rank by -||x_hat - X_c|| on the SAME standardized coords (fit-limited reference).
If oracle_direct FIRES but oracle_fpe does NOT -> readout capacity is the wall (raise dim / change readout).
If NEITHER fires -> fit capacity is the wall (the epochs/objective axis).
The cheapest ladder point with oracle_fpe >= ORACLE_FIRE is the capacity for the decisive re-run.

PREVIEW (single-seed, reported not decided): at the firing point we refit INDUCTIVELY (no held-out folded in),
extract a small L2-genuine held-out set through the IDENTICAL symbolic apparatus, and report ONESHOT geometry
vs POP frequency degree-stratified (HIGH-degree headline). The decisive verdict is the 3-seed FULL re-run.

## Compute architecture
class: (c) MIXED. CSKG assembly + L2-genuine extraction = symbolic graph traversal (sequential-CPU correct,
same as the VET apparatus). Coord fit = minibatch SGD; readout = batched matmul. Single seed, single CSKG
assembly reused across all ladder points -> memory FLAT (no multi-seed accumulation; the OOM driver is absent
by construction). device=cpu on remote_cpu_queue (CPU-safe default, no memory limit). LOCAL = NEVER (USER-
locked: no local experiment execution; this cell is authored for remote_cpu_queue only).

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity: tmp_replace (write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - start_marker + crash_diagnostic + heartbeat present.
# - cell_chunked: false (single seed by design -> no cross-seed accumulation; memory-safe without subprocess).
# - discriminator: ORACLE-fires is the gate; a ladder point either clears ORACLE_FIRE or does not (no vacuous
#   auto-pass -- the L0 control REPRODUCES the collapse, proving the ladder is calibrated to the failing regime).
# - progress_logging: print_flush_true (per-ladder-point + per-fit flush; line-buffered stdout).
# - no numbers hard-coded as claims; every reported value is MEASURED@this metrics.json at run time.
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

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import (  # noqa: E402
    Graph, build_ids, mine_rules,
)
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_operator_fix_ssp_phase_rotation_replay_v1 import (  # noqa: E402
    make_fpe_basis, fit_transe_coords,
)
# Reuse the v1 cell's symbolic + readout apparatus verbatim (identical code path as the decisive run).
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, extract_l2_genuine, build_true_by_hr_int, filtered_hits_from_scores,
    pop_hits, geom_scores, _standardize, stratify_by_tail_degree, per_stratum_hits,
    per_stratum_pop, MAX_RULES_PER_HEAD, HUB_CAP, FPE_ELL, PRIMARY_K, STRATA,
)

ANCHOR_NAME = "course_c_oracle_capacity_ladder_v1"

ORACLE_FIRE = 0.90        # oracle hits@10 threshold that makes the reasoning question askable
N_ORACLE_HOLD = 500       # random held-out edges folded into the ORACLE fit + scored for recovery
FPE_SCORE_CHUNK = 256

# Ladder: (label, fit_kind, k, fpe_dim, epochs, batch). fit_kind in {margin_fb, margin_mb, anchor1}.
#  margin_fb = original full-batch margin-rank (fit_transe_coords) -- reproduces the collapse + epochs axis.
#  margin_mb = same margin objective but MINIBATCH (isolates minibatch vs objective).
#  anchor1   = CE self-adversarial + N3 + reciprocal, minibatch (the pre-registered lever).
FULL_LADDER = [
    ("L0_margin_fb_ep600",   "margin_fb", 24, 4096,  600, 0),      # control: reproduce the 0.023 collapse
    ("L1_margin_fb_ep2400",  "margin_fb", 24, 4096, 2400, 0),      # pure more-epochs (current objective)
    ("L2_margin_mb_ep60",    "margin_mb", 24, 4096,   60, 8192),   # minibatch, same margin objective
    ("L3_anchor1_ep60",      "anchor1",   24, 4096,   60, 8192),   # Anchor-1 recipe, moderate
    ("L4_anchor1_ep150",     "anchor1",   24, 4096,  150, 8192),   # Anchor-1 recipe, more
    ("L5_anchor1_k32_d8192", "anchor1",   32, 8192,  150, 8192),   # + coord/readout resolution axis
]
# Reduced remote pre-check (tiny CSKG slice) -- a small REMOTE validation before the full ladder if wanted.
SMOKE_LADDER = [
    ("L0_margin_fb_ep300", "margin_fb", 16, 1024, 300, 0),
    ("L3_anchor1_ep60",    "anchor1",   16, 1024,  60, 4096),
]

FULL_CFG = dict(seed=7, cskg_max_lines=0, k_core=12, cskg_max_nodes=0, min_support=10, min_conf=0.10,
                n_eval_preview=1500, ladder="full")
SMOKE_CFG = dict(seed=7, cskg_max_lines=800000, k_core=3, cskg_max_nodes=3000, min_support=2, min_conf=0.05,
                 n_eval_preview=600, ladder="smoke")


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
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


def _fit(fit_kind, train_int, N, n_rel, k, dim, epochs, batch, device, seed, hold=None):
    """Return (X, D) for the requested fit. hold != None => transductive (fold held-out into the fit)."""
    if fit_kind == "margin_fb":
        return fit_transe_coords(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold)
    if fit_kind == "margin_mb":
        # minibatch margin: Anchor-1 with CE off is not equivalent; use anchor1 fit with adv_temp low + gamma
        # large approximates margin-rank, but to keep a clean margin control we run anchor1 with n3=0 and a
        # single-negative-style high-temp weighting. Simpler + honest: reuse anchor1 machinery with n3_lambda=0
        # and adv_temp=0 (uniform negative weights = plain CE), labeled as the minibatch-CE baseline.
        return fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold,
                               reciprocal=False, n3_lambda=0.0, adv_temp=0.0, batch_size=batch)
    if fit_kind == "anchor1":
        return fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold,
                               reciprocal=True, batch_size=batch)
    raise ValueError("unknown fit_kind %s" % fit_kind)


def _direct_scores(X, D, hold_edges, device, chunk=FPE_SCORE_CHUNK):
    """Direct-distance readout: score = -||x_hat - X_c|| on standardized coords (fit-limited reference readout).
    Query-chunked to bound peak memory. Higher = better. Numerically the coord-fit's own ranking, no FPE."""
    Xn, Dn = _standardize(X, D)
    h = torch.from_numpy(hold_edges[:, 0]).long().to(device)
    r = torch.from_numpy(hold_edges[:, 1]).long().to(device)
    x_hat = Xn[h] + Dn[r]                                # (nq, k)
    nq = x_hat.shape[0]; n_ent = Xn.shape[0]
    out = torch.empty((nq, n_ent), dtype=torch.float32)
    for s in range(0, nq, chunk):
        e = min(s + chunk, nq)
        d = torch.cdist(x_hat[s:e], Xn)                  # (b, N) L2 distance
        out[s:e] = (-d).detach().to("cpu")
        del d
    return out


def run_ladder(run_mode, device):
    cfg = FULL_CFG if run_mode == "full" else SMOKE_CFG
    ladder = FULL_LADDER if cfg["ladder"] == "full" else SMOKE_LADDER
    seed = cfg["seed"]
    t0 = time.perf_counter()

    if not _ensure_cskg():
        return dict(verdict="HARD_FAIL", verdict_msg="CSKG data absent and self-acquire failed",
                    summary="cskg missing", elapsed_s=time.perf_counter() - t0)

    train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
        cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
    _log("cskg core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d train=%d test=%d"
         % (prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"], prov["n_rel_tokens"],
            prov["n_train"], prov["n_test"]))

    ent2i, rel2i = build_ids(train_lbl, valid_lbl, test_lbl)
    N = len(ent2i); n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    valid_int = _to_int_edges(valid_lbl, ent2i, rel2i)
    test_int = _to_int_edges(test_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, valid_int, test_int)

    # ORACLE held-out: random test edges (memorization-capacity probe; L2-genuineness irrelevant to the ORACLE).
    rng = np.random.default_rng(seed * 100057 + 7)
    sel = rng.permutation(test_int.shape[0])[:min(N_ORACLE_HOLD, test_int.shape[0])]
    hold_oracle = test_int[sel].copy()
    _log("oracle held-out sample n=%d (of %d test edges); N_candidates=%d" % (hold_oracle.shape[0], test_int.shape[0], N))

    hb_path = os.path.join(str(get_output_dir(ANCHOR_NAME)), "_heartbeat.jsonl")

    def _hb(tag):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag,
                                "elapsed_s": time.perf_counter() - t0}) + "\n")

    rows = []
    for (label, fit_kind, k, dim, epochs, batch) in ladder:
        tp = time.perf_counter()
        W = make_fpe_basis(k, dim, FPE_ELL, device, seed)
        X_or, D_or = _fit(fit_kind, train_int, N, n_rel, k, dim, epochs, batch, device, seed, hold=hold_oracle)
        fpe = geom_scores(X_or, D_or, W, hold_oracle, device)
        fpe_m = filtered_hits_from_scores(fpe, hold_oracle, all_true)
        direct = _direct_scores(X_or, D_or, hold_oracle, device)
        direct_m = filtered_hits_from_scores(direct, hold_oracle, all_true)
        row = dict(label=label, fit_kind=fit_kind, k=k, fpe_dim=dim, epochs=epochs, batch=batch,
                   oracle_fpe_h10=round(fpe_m["hits@%d" % PRIMARY_K], 4),
                   oracle_fpe_h1=round(fpe_m["hits@1"], 4), oracle_fpe_mrr=round(fpe_m["mrr"], 4),
                   oracle_direct_h10=round(direct_m["hits@%d" % PRIMARY_K], 4),
                   oracle_direct_mrr=round(direct_m["mrr"], 4),
                   fires_fpe=bool(fpe_m["hits@%d" % PRIMARY_K] >= ORACLE_FIRE),
                   fires_direct=bool(direct_m["hits@%d" % PRIMARY_K] >= ORACLE_FIRE),
                   elapsed_s=round(time.perf_counter() - tp, 1))
        rows.append(row)
        _log("LADDER %s: oracle_fpe h@10=%.3f (h@1=%.3f) oracle_direct h@10=%.3f | fires_fpe=%s fires_direct=%s (%.1fs)"
             % (label, row["oracle_fpe_h10"], row["oracle_fpe_h1"], row["oracle_direct_h10"],
                row["fires_fpe"], row["fires_direct"], row["elapsed_s"]))
        _hb(label)
        del W, X_or, D_or, fpe, direct
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    fires = [r for r in rows if r["fires_fpe"]]
    firing = fires[0] if fires else None            # cheapest firing point (ladder ordered cheap->expensive)
    best = max(rows, key=lambda r: r["oracle_fpe_h10"])
    fit_limited = bool(best["oracle_direct_h10"] < ORACLE_FIRE and best["oracle_fpe_h10"] < ORACLE_FIRE)
    readout_limited = bool(best["oracle_direct_h10"] >= ORACLE_FIRE and best["oracle_fpe_h10"] < ORACLE_FIRE)

    preview = None
    if firing is not None:
        preview = _reasoning_preview(firing, train_int, valid_lbl, test_int, train_lbl, test_lbl,
                                     ent2i, rel2i, N, n_rel, all_true, cfg, device, seed)

    if firing is not None:
        verdict = "LADDER_ORACLE_FIRES"
        vm = ("ORACLE FIRES at %s (oracle_fpe h@10=%.3f >= %.2f); minimum capacity located. fit_kind=%s "
              "k=%d dim=%d epochs=%d batch=%d. Reasoning preview (single-seed): geom_best=%s POP=%s HIGH geom=%s "
              "POP=%s. Decisive 3-seed re-run at this capacity is now askable."
              % (firing["label"], firing["oracle_fpe_h10"], ORACLE_FIRE, firing["fit_kind"], firing["k"],
                 firing["fpe_dim"], firing["epochs"], firing["batch"],
                 preview and preview.get("geom_best"), preview and preview.get("pop"),
                 preview and preview.get("geom_high"), preview and preview.get("pop_high")))
    elif readout_limited:
        verdict = "LADDER_READOUT_LIMITED"
        vm = ("ORACLE does NOT fire under FPE readout but DOES under direct-distance at %s (fpe h@10=%.3f, "
              "direct h@10=%.3f): the FPE bounded-kernel READOUT is the wall, not the fit. Raise readout dim "
              "or change readout before the re-run." % (best["label"], best["oracle_fpe_h10"], best["oracle_direct_h10"]))
    else:
        verdict = "LADDER_FIT_LIMITED"
        vm = ("ORACLE does not fire at any laddered capacity (best %s: fpe h@10=%.3f direct h@10=%.3f). FIT "
              "capacity is the wall; escalate epochs / dim / objective beyond the ladder top before the re-run."
              % (best["label"], best["oracle_fpe_h10"], best["oracle_direct_h10"]))

    return dict(verdict=verdict, verdict_msg=vm, summary=vm[:200], run_mode=run_mode,
                elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), seed=seed,
                N=int(N), n_rel=int(n_rel), oracle_fire_threshold=ORACLE_FIRE,
                cskg_provenance=prov, ladder=rows, firing_config=firing, best_config=best,
                fit_limited=fit_limited, readout_limited=readout_limited, reasoning_preview=preview)


def _reasoning_preview(firing, train_int, valid_lbl, test_int, train_lbl, test_lbl, ent2i, rel2i,
                       N, n_rel, all_true, cfg, device, seed):
    """Single-seed preview at the firing capacity: refit INDUCTIVELY (no held-out folded in), extract a small
    L2-genuine set through the identical symbolic apparatus, report ONESHOT geometry vs POP degree-stratified."""
    try:
        gd = Graph(train_lbl, ent2i, rel2i)
        known = defaultdict(set)
        for tr in (train_lbl, valid_lbl, test_lbl):
            for (h, r, t) in tr:
                known[(ent2i[h], rel2i[r])].add(ent2i[t])
        acc, allpat, _hub = mine_rules(gd, list(rel2i.values()), cfg["min_support"], cfg["min_conf"],
                                       MAX_RULES_PER_HEAD, HUB_CAP)
        hold, hold_prov = extract_l2_genuine(gd, allpat, known, test_int, cfg["n_eval_preview"], seed)
        if hold.shape[0] < 10:
            return dict(note="L2-genuine held-out too small for preview", n_l2_genuine=int(hold.shape[0]))
        strat, tert = stratify_by_tail_degree(hold, gd.node_degree)
        k = firing["k"]; dim = firing["fpe_dim"]; epochs = firing["epochs"]; batch = firing["batch"]
        W = make_fpe_basis(k, dim, FPE_ELL, device, seed)
        X, D = _fit(firing["fit_kind"], train_int, N, n_rel, k, dim, epochs, batch, device, seed, hold=None)
        sc = geom_scores(X, D, W, hold, device)
        geo_m = filtered_hits_from_scores(sc, hold, all_true)
        pop_m, _ = pop_hits(gd.rel_tail_freq, hold, all_true, N)
        geo_strat = per_stratum_hits(sc, hold, strat, all_true)
        pop_strat = per_stratum_pop(gd.rel_tail_freq, hold, strat, all_true, N)
        return dict(n_l2_genuine=int(hold.shape[0]), l2_genuine_prov=hold_prov, tert_bounds=tert,
                    geom_best=round(geo_m["hits@%d" % PRIMARY_K], 4), pop=round(pop_m["hits@%d" % PRIMARY_K], 4),
                    geom_high=(geo_strat["high"]["hits"]), pop_high=(pop_strat["high"]["hits"]),
                    geom_strat={s: geo_strat[s] for s in STRATA}, pop_strat={s: pop_strat[s] for s in STRATA},
                    margin_vs_pop=round(geo_m["hits@%d" % PRIMARY_K] - pop_m["hits@%d" % PRIMARY_K], 4))
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        return dict(preview_error=type(e).__name__, preview_msg=str(e)[:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "smoke" if args.smoke else args.run_mode
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (args.device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        device = torch.device("cpu")
    else:
        want_cuda = (args.device in ("auto", "cuda")) or (env_dev == "cuda")
        device = torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")

    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, run_mode, 1)
    _log("device=%s cuda=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))
    metrics = run_ladder(run_mode, device)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics.get("elapsed_s", 0.0)}])
    _log("VERDICT: %s" % metrics.get("verdict_msg", ""))
    _log("done (%.1fs)" % metrics.get("elapsed_s", 0.0))


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
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
