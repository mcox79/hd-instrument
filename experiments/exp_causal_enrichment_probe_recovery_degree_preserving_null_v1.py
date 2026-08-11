#!/usr/bin/env python3
# CELL-TEMPLATE MANDATORY (adapted for a KB-ENRICHMENT PROBE-RECOVERY DIAGNOSTIC, DEGREE-PRESERVING
# NULL variant -- see preregs/2026-08-11_causal_enrichment_probe_recovery_degree_preserving_null_v1.md
# for the full SCHEMA-VET declaration table; summary of applicable items):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - start_marker + crash_diagnostic + heartbeat (single deterministic pass, budgeted <=5.5 min FULL)
# - final_metrics_atomicity = tmp_replace (os.replace); PLUS per-unit units.jsonl checkpoint for the
#   null-seed ensemble loop (tools/exp_checkpoint.py, per CLAUDE.md multi-unit mandate)
# - real_code_path: self-test constructs REAL objects at tiny scale via the REUSED v1 module (real
#   edges_shard sample, real parse_gene_ontology() against real go.obo, real regex-parse of the real
#   causenet-precision.jsonl.bz2) PLUS a dedicated degree-preservation invariant check on real data
# - CAN-FAIL recovery test with pre-registered HARD_PASS / MIDDLE_BAND / HARD_FAIL bands (hop-1-only
#   gate) + the RANDOM-EDGES control (reused unchanged from v1)
# - deterministic seeding (fixed int seeds; np.random.default_rng; sorted() for relation-group order;
#   no hash()-seeded RNG)
# - cardinality_ok: EXPECTED_N_UNITS = N_NULL_SEEDS (null-seed loop only); HARD_FAIL_CARDINALITY_
#   BREACH_META_RULE_H if the recorded null-seed units fall short
# - N/A META_RULEs declared in the pre-reg (same exemption class as v1 + exp_cskg_foundation_v1.py)
#
# WHAT: FORK of experiments/exp_causal_enrichment_probe_recovery_v1.py (commit 875598d08). That cell's
# global relation-label SHUFFLE control did not collapse (shuffle=0.55 vs baseline=0.2, delta=0.35 >
# 0.05 tol) -> HARD_FAIL -- but the failure was concentrated at 2-hop (enrichment ~doubled causal-edge
# density, so random 2-hop causal paths appear by chance), while a genuine 1-hop content signal
# survived (enriched hop1=0.425 vs shuffle hop1=0.300, +0.125). This cell REPLACES the wrong null
# (global label permutation) with the CORRECT one (degree-preserving / configuration-model: permute
# the TARGET column per relation type, so every node's per-relation causal degree is preserved exactly
# and only WHICH node each causal edge actually points to is randomized), re-scopes the gate to
# hop-1-only, and reports hop<=2 for context. The 40 probes, the CSKG baseline, the CauseNet-Precision
# + GO-regulates ingestion, canon(), the recovery function, and the RANDOM-EDGES control are REUSED
# UNCHANGED via a direct Python import of the v1 module (not re-authored, not re-ingested) -- this is a
# fair-test REFINEMENT of the null model + hop analysis, nothing else changes.
#
# ASCII-only. Determinism: fixed seeds; sorted() for any set/dict/relation-group ordering; no
# hash()-seeded RNG. NO ORIGIN PUSH this cycle -> runs INLINE-LOCAL, not via queue_add / remote
# dispatch (same constraint as v1).
from __future__ import annotations

import argparse
import hashlib  # noqa: F401 (kept for parity/clarity with v1's imports; hashing itself is done via base._edge_set_hash)
import json
import os
import platform
import sys
import tempfile
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

# ---------------------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_causal_enrichment_probe_recovery_v1 as base  # noqa: E402  REUSE, DO NOT MODIFY -- source of PROBES / KB-ingestion / recovery-logic under test
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "causal_enrichment_probe_recovery_degree_preserving_null_v1"
ART_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
PREREG_PATH = os.path.join(
    REPO_ROOT, "preregs", "2026-08-11_causal_enrichment_probe_recovery_degree_preserving_null_v1.md"
)

# ---- deterministic seeds (fixed ints; never hash()/list(set())) --------------------------------
NULL_SEED_BASE = 20260820  # distinct from base's SHUFFLE_SEED/RANDOM_ENDPOINT_SEED/RANDOM_REL_SEED
N_NULL_SEEDS_FULL = 6
N_NULL_SEEDS_SMOKE = 3
N_NULL_SEEDS_SELFTEST = 2

# ---- smoke-mode reduced caps (reduce wall time; keep all 40 probes -- see prereg TIMEOUT section) -
SMOKE_BASELINE_LINE_CAP = 100000
SMOKE_CAUSENET_LINE_CAP = 30000

# ---- pre-registered gate bands (director-specified, verbatim from task) ------------------------
GATE_HARD_PASS_GAIN = 0.15
GATE_HARD_FAIL_GAIN = 0.05
GATE_RANDOM_STAYLOW_TOL = 0.10  # same tolerance as v1's random_stays_low_ok


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    fin = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, fin)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    fin = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, fin)


def _hb(output_dir, stage, t0, extra=None):
    row = {"ts_iso": _now_iso(), "stage": stage, "elapsed_s": round(time.perf_counter() - t0, 1)}
    if extra:
        row.update(extra)
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} t={row['elapsed_s']}s {extra or ''}", flush=True)


# ---------------------------------------------------------------------------------------
def degree_preserving_shuffle(edges, causal_rels, seed):
    """Configuration-model-style null: permute the TARGET column within each causal relation-type
    group; non-causal edges pass through byte-identical. A column permutation preserves the multiset
    of sources AND targets EXACTLY (by construction, no rejection sampling needed) -- so every node's
    per-relation causal OUT-degree and IN-degree are unchanged, only WHICH node each causal edge
    actually points to is randomized. This isolates 'does having K causal edges of type r matter'
    (density -- PRESERVED) from 'does the specific source->target content matter' (CONTENT --
    DESTROYED). Self-loops (source==target after shuffle) can occur by chance; counted but harmless
    (no probe subject equals its object; _recover excludes n==obj for mid-node search).
    Returns (shuffled_edges: list[(s,r,o)], n_self_loops_introduced: int)."""
    rng = np.random.default_rng(seed)
    by_rel = defaultdict(list)
    passthrough = []
    for s, r, o in edges:
        if r in causal_rels:
            by_rel[r].append((s, o))
        else:
            passthrough.append((s, r, o))

    shuffled = list(passthrough)
    n_self_loops = 0
    for r in sorted(by_rel.keys()):
        pairs = by_rel[r]
        sources = [s for s, _o in pairs]
        targets = [o for _s, o in pairs]
        perm = rng.permutation(len(targets))
        shuffled_targets = [targets[i] for i in perm]
        for s, o in zip(sources, shuffled_targets):
            if s == o:
                n_self_loops += 1
            shuffled.append((s, r, o))
    return shuffled, n_self_loops


# ---------------------------------------------------------------------------------------
def gate_verdict(baseline_hop1, enriched_hop1, null_hop1_mean, random_hop1,
                  enriched_le2, null_le2_mean):
    gain_hop1 = enriched_hop1 - null_hop1_mean
    gain_le2 = enriched_le2 - null_le2_mean  # reported only, NOT gated (per prereg)
    random_delta_from_baseline_hop1 = abs(random_hop1 - baseline_hop1)
    random_stays_low_ok = random_delta_from_baseline_hop1 <= GATE_RANDOM_STAYLOW_TOL

    if gain_hop1 < GATE_HARD_FAIL_GAIN:
        verdict = "HARD_FAIL"
    elif gain_hop1 >= GATE_HARD_PASS_GAIN and random_stays_low_ok:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"
    return {
        "verdict": verdict,
        "gain_hop1": round(gain_hop1, 4),
        "gain_hop_le2": round(gain_le2, 4),
        "random_delta_from_baseline_hop1": round(random_delta_from_baseline_hop1, 4),
        "random_stays_low_ok": bool(random_stays_low_ok),
        "bands": {
            "hard_pass": f"gain_hop1>={GATE_HARD_PASS_GAIN} AND random_stays_low_ok(<={GATE_RANDOM_STAYLOW_TOL})",
            "middle_band": f"gain_hop1 in [{GATE_HARD_FAIL_GAIN}, {GATE_HARD_PASS_GAIN})  OR  gain_hop1>={GATE_HARD_PASS_GAIN} with random control broken",
            "hard_fail": f"gain_hop1<{GATE_HARD_FAIL_GAIN}",
        },
    }


PRIOR_RUN_REFERENCE = {
    "metrics_path": "data/exp_causal_enrichment_probe_recovery_v1/metrics.json",
    "prior_verdict": "HARD_FAIL",  # CITED@data/exp_causal_enrichment_probe_recovery_v1/metrics.json (this cycle)
    "prior_baseline_recovery": 0.2, "prior_enriched_recovery": 0.675,
    "prior_shuffle_recovery": 0.55, "prior_random_recovery": 0.2,
    "prior_enriched_hop1_rate": 0.425, "prior_shuffle_hop1_rate": 0.3,
    "prior_hop1_only_signal_vs_wrong_null": 0.125,
    "note": ("global relation-label shuffle did not collapse (shuffle_delta=0.35 > 0.05 tol) -- "
             "concentrated at 2-hop; this cell replaces that null with a degree-preserving "
             "(configuration-model) one, scoped to hop-1 for the gate."),
}


# ---------------------------------------------------------------------------------------
def run(run_mode, output_dir, causenet_line_cap=None, go_max_terms=None, baseline_line_cap=None,
        n_probes_override=None, n_null_seeds=None):
    t0 = time.perf_counter()
    _write_start_marker(output_dir, run_mode)
    _hb(output_dir, "begin", t0, {"run_mode": run_mode})

    n_null_seeds = N_NULL_SEEDS_FULL if n_null_seeds is None else n_null_seeds
    null_seeds = [NULL_SEED_BASE + i for i in range(n_null_seeds)]

    probes = base.PROBES if n_probes_override is None else base.PROBES[:n_probes_override]

    baseline_edges = base.load_baseline_edges(base.CSKG_DIR, output_dir, t0, line_cap=baseline_line_cap)

    causenet_edges, n_causenet_lines = base._extract_causenet_pairs(
        base.CAUSENET_BZ2, output_dir, t0, line_cap=causenet_line_cap)
    go_edges = base._extract_go_regulates(base.GO_OBO, output_dir, t0, max_terms=go_max_terms)
    new_source_edges = causenet_edges + go_edges

    enriched_edges = baseline_edges + new_source_edges

    # ---- RANDOM-EDGES control (reused unchanged from v1: same construction, same seeds) -----------
    random_new_edges = base.build_random_control_edges(
        baseline_edges, new_source_edges, len(new_source_edges), output_dir, t0)
    random_control_edges = baseline_edges + random_new_edges

    # ---- fixed-condition recovery: baseline / enriched / random (no seed axis; single pass each) ---
    fixed_conditions = {}
    fixed_hashes = {}
    for name, edges in (("baseline", baseline_edges), ("enriched", enriched_edges),
                         ("random", random_control_edges)):
        adj = base.build_adjacency(edges)
        rec = base.compute_recovery(adj, base.ENRICHED_CAUSAL_RELS, probes)
        fixed_conditions[name] = {"n_edges": len(edges), **rec}
        fixed_hashes[name] = base._edge_set_hash(edges)
        _hb(output_dir, f"recovery_{name}", t0,
            {"n_edges": len(edges), "hop1_rate": rec["hop1_rate"], "recovery_rate": rec["recovery_rate"]})
        del adj

    # ---- degree-preserving null ENSEMBLE (checkpointed per seed, resumable) ------------------------
    done_units = completed_units(output_dir)
    for seed in null_seeds:
        key = unit_key("null", seed)
        if key in done_units:
            continue
        null_edges, n_self_loops = degree_preserving_shuffle(enriched_edges, base.ENRICHED_CAUSAL_RELS, seed)
        adj = base.build_adjacency(null_edges)
        rec = base.compute_recovery(adj, base.ENRICHED_CAUSAL_RELS, probes)
        result = {"n_edges": len(null_edges), **rec, "edge_hash": base._edge_set_hash(null_edges),
                  "n_self_loops_introduced": n_self_loops}
        record_unit(output_dir, key, result)
        _hb(output_dir, "recovery_null", t0,
            {"seed": seed, "hop1_rate": rec["hop1_rate"], "recovery_rate": rec["recovery_rate"],
             "n_self_loops_introduced": n_self_loops})
        del adj

    all_units = load_units(output_dir)
    null_results = {seed: all_units[unit_key("null", seed)] for seed in null_seeds
                     if unit_key("null", seed) in all_units}

    # ---- cardinality gate (META_RULE_H) -------------------------------------------------------------
    if len(null_results) != n_null_seeds:
        missing = sorted(s for s in null_seeds if unit_key("null", s) not in all_units)
        elapsed_s = round(time.perf_counter() - t0, 1)
        metrics = {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": (f"expected {n_null_seeds} null-seed units, got {len(null_results)}; "
                             f"missing_seeds={missing}"),
            "summary": "CAUSAL_ENRICHMENT_DEGREE_PRESERVING_NULL cardinality breach",
            "elapsed_s": elapsed_s, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
            "pid": os.getpid(), "run_mode": run_mode,
            "n_null_seeds_expected": n_null_seeds, "n_null_seeds_recorded": len(null_results),
            "missing_null_seeds": missing, "prereg": PREREG_PATH,
        }
        tmp = os.path.join(output_dir, "metrics.json.tmp")
        fin = os.path.join(output_dir, "metrics.json")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(tmp, fin)
        print(f"[done] {metrics['summary']} -> {fin}", flush=True)
        return metrics

    null_hop1 = np.array([null_results[s]["hop1_rate"] for s in null_seeds], dtype=np.float64)
    null_le2 = np.array([null_results[s]["recovery_rate"] for s in null_seeds], dtype=np.float64)
    null_hop1_mean = float(np.mean(null_hop1))
    null_hop1_std = float(np.std(null_hop1))
    null_le2_mean = float(np.mean(null_le2))
    null_le2_std = float(np.std(null_le2))
    n_self_loops_total = sum(null_results[s]["n_self_loops_introduced"] for s in null_seeds)

    GATE = gate_verdict(
        baseline_hop1=fixed_conditions["baseline"]["hop1_rate"],
        enriched_hop1=fixed_conditions["enriched"]["hop1_rate"],
        null_hop1_mean=null_hop1_mean,
        random_hop1=fixed_conditions["random"]["hop1_rate"],
        enriched_le2=fixed_conditions["enriched"]["recovery_rate"],
        null_le2_mean=null_le2_mean,
    )

    # ---- arms-must-differ (META_RULE_AF): baseline / enriched / random / each null seed -------------
    all_hashes = dict(fixed_hashes)
    for seed in null_seeds:
        all_hashes[f"null_seed_{seed}"] = null_results[seed]["edge_hash"]
    pairs = sorted(all_hashes.keys())
    arm_collisions = []
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            a, b = pairs[i], pairs[j]
            if all_hashes[a] == all_hashes[b]:
                arm_collisions.append((a, b))
    arms_differ_verified = len(arm_collisions) == 0

    # ---- causal-edge-fraction gap-closure metric (unchanged from v1; baseline/enriched only) --------
    frac_strict_baseline = base.causal_edge_fraction(baseline_edges, base.STRICT_CAUSAL_RELS)
    frac_strict_enriched = base.causal_edge_fraction(enriched_edges, base.STRICT_CAUSAL_RELS)
    frac_generous_baseline = base.causal_edge_fraction(baseline_edges, base.ENRICHED_CAUSAL_RELS)
    frac_generous_enriched = base.causal_edge_fraction(enriched_edges, base.ENRICHED_CAUSAL_RELS)

    elapsed_s = round(time.perf_counter() - t0, 1)
    metrics = {
        "verdict": GATE["verdict"], "run_mode": run_mode,
        "verdict_msg": (
            f"causal enrichment degree-preserving-null {run_mode}: "
            f"baseline_hop1={fixed_conditions['baseline']['hop1_rate']} "
            f"enriched_hop1={fixed_conditions['enriched']['hop1_rate']} "
            f"null_hop1_mean={round(null_hop1_mean, 4)}(+-{round(null_hop1_std, 4)}) "
            f"random_hop1={fixed_conditions['random']['hop1_rate']} "
            f"gain_hop1={GATE['gain_hop1']} gate={GATE['verdict']} "
            f"(random_ok={GATE['random_stays_low_ok']}) | "
            f"hop<=2: enriched={fixed_conditions['enriched']['recovery_rate']} "
            f"null_mean={round(null_le2_mean, 4)} gain_le2={GATE['gain_hop_le2']}"
        ),
        "summary": f"CAUSAL_ENRICHMENT_DEGREE_PRESERVING_NULL {run_mode} {GATE['verdict']}",
        "elapsed_s": elapsed_s, "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME, "pid": os.getpid(),
        "n_probes": len(probes), "n_null_seeds": n_null_seeds, "null_seeds": null_seeds,
        "conditions": {
            "baseline": fixed_conditions["baseline"],
            "enriched": fixed_conditions["enriched"],
            "random": fixed_conditions["random"],
            "degree_preserving_null": {
                "per_seed": {str(s): null_results[s] for s in null_seeds},
                "hop1_rate_mean": round(null_hop1_mean, 4), "hop1_rate_std": round(null_hop1_std, 4),
                "hop_le2_rate_mean": round(null_le2_mean, 4), "hop_le2_rate_std": round(null_le2_std, 4),
                "n_self_loops_introduced_total": n_self_loops_total,
            },
        },
        "gate": GATE,
        "arms_differ_verified": arms_differ_verified,
        "arm_edge_hashes": all_hashes,
        "arm_hash_collisions": arm_collisions,
        "cardinality_ok": True, "n_null_seeds_expected": n_null_seeds, "n_null_seeds_recorded": len(null_results),
        "causenet_n_lines": n_causenet_lines, "causenet_n_unique_pairs": len(causenet_edges),
        "go_n_regulates_resolved": len(go_edges),
        "n_new_source_edges": len(new_source_edges),
        "causal_edge_fraction": {
            "strict_bucket_rels": sorted(base.STRICT_CAUSAL_RELS),
            "generous_bucket_rels": sorted(base.ENRICHED_CAUSAL_RELS),
            "strict_baseline": frac_strict_baseline, "strict_enriched": frac_strict_enriched,
            "generous_baseline": frac_generous_baseline, "generous_enriched": frac_generous_enriched,
        },
        "prior_run_reference": PRIOR_RUN_REFERENCE,
        "prereg": PREREG_PATH,
        "sources": {
            "causenet_precision_bz2": base.CAUSENET_BZ2, "causenet_license": "CC BY 4.0",
            "go_obo_full": base.GO_OBO, "go_license": "CC BY 4.0",
        },
        "base_cell_reused": "experiments/exp_causal_enrichment_probe_recovery_v1.py (imported, not retyped)",
    }
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    fin = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, fin)
    print(f"[done] {metrics['summary']} elapsed={metrics['elapsed_s']}s -> {fin}", flush=True)
    return metrics


# ---------------------------------------------------------------------------------------
def self_test():
    """Real-code-path self-test at tiny scale: exercises the REUSED v1 module's real loaders (real
    edges_shard sample, real parse_gene_ontology() against the REAL go.obo, real regex-parse of the
    REAL causenet-precision.jsonl.bz2), plus THIS cell's own degree-preservation invariant (the crux
    correctness check), the passthrough-identity check, the shuffle-nontrivial check, the checkpoint
    round-trip, and a reduced end-to-end run() including a tiny null ensemble."""
    exercised = set()
    out = tempfile.mkdtemp(prefix="causal_enrich_degnull_selftest_")
    t0 = time.perf_counter()

    baseline_edges = base.load_baseline_edges(base.CSKG_DIR, out, t0, line_cap=5000)
    exercised.add("base.load_baseline_edges")
    assert len(baseline_edges) > 100, ("too few baseline edges in sample", len(baseline_edges))

    causenet_edges, n_lines = base._extract_causenet_pairs(base.CAUSENET_BZ2, out, t0, line_cap=200)
    exercised.add("base._extract_causenet_pairs")
    assert n_lines == 200, ("causenet line cap not honored", n_lines)
    assert len(causenet_edges) > 50, ("too few causenet pairs extracted", len(causenet_edges))

    go_edges = base._extract_go_regulates(base.GO_OBO, out, t0, max_terms=None)
    exercised.add("base._extract_go_regulates")
    assert len(go_edges) > 100, ("too few GO regulates edges resolved", len(go_edges))

    sample_enriched = baseline_edges[:2000] + causenet_edges[:200] + go_edges[:100]

    # ---- degree-preservation invariant (THE crux correctness check for this cell) -----------------
    shuffled, n_self_loops = degree_preserving_shuffle(sample_enriched, base.ENRICHED_CAUSAL_RELS, seed=1)
    exercised.add("degree_preserving_shuffle")
    assert len(shuffled) == len(sample_enriched), "shuffle changed edge COUNT"

    def _by_rel_source_target(edges, rel_set):
        d = defaultdict(lambda: ([], []))
        for s, r, o in edges:
            if r in rel_set:
                d[r][0].append(s)
                d[r][1].append(o)
        return d

    before = _by_rel_source_target(sample_enriched, base.ENRICHED_CAUSAL_RELS)
    after = _by_rel_source_target(shuffled, base.ENRICHED_CAUSAL_RELS)
    assert set(before.keys()) == set(after.keys()), "shuffle changed which relations appear"
    for r in before:
        assert sorted(before[r][0]) == sorted(after[r][0]), \
            f"relation {r}: source multiset changed (per-relation causal OUT-degree not preserved)"
        assert sorted(before[r][1]) == sorted(after[r][1]), \
            f"relation {r}: target multiset changed (per-relation causal IN-degree not preserved)"
    exercised.add("degree_invariant_check")

    # ---- passthrough (non-causal) edges must be byte-identical, same order ------------------------
    before_passthrough = [(s, r, o) for s, r, o in sample_enriched if r not in base.ENRICHED_CAUSAL_RELS]
    after_passthrough = [(s, r, o) for s, r, o in shuffled if r not in base.ENRICHED_CAUSAL_RELS]
    assert before_passthrough == after_passthrough, "non-causal edges were touched by the causal-only shuffle"
    exercised.add("passthrough_identity_check")

    # ---- shuffle actually did something (not a vacuous identity permutation) -----------------------
    assert base._edge_set_hash(shuffled) != base._edge_set_hash(sample_enriched), \
        "degree-preserving shuffle produced an identical edge set (vacuous null)"
    exercised.add("shuffle_nontrivial_check")

    # ---- known-positive / known-negative recovery sanity (reused _recover) -------------------------
    adj = base.build_adjacency(baseline_edges)
    exercised.add("base.build_adjacency")
    known_causal = next(((s, o) for s, r, o in baseline_edges if r in base.CAUSAL_RELS_BASE), None)
    assert known_causal is not None, "no causal-typed edge in the 5000-line baseline sample (unlucky shard?)"
    hop = base._recover(adj, base.ENRICHED_CAUSAL_RELS, known_causal[0], known_causal[1])
    assert hop == 1, ("known-present causal edge failed to recover", known_causal, hop)
    exercised.add("base._recover_positive")
    hop0 = base._recover(adj, base.ENRICHED_CAUSAL_RELS, "zzz_selftest_nonexistent_a", "zzz_selftest_nonexistent_b")
    assert hop0 == 0, ("recovery function is vacuously true", hop0)
    exercised.add("base._recover_negative")

    # ---- checkpoint round-trip (real exp_checkpoint API, tiny scale) -------------------------------
    ck_dir = os.path.join(out, "ckpt")
    assert unit_key("null", 999) not in completed_units(ck_dir)
    record_unit(ck_dir, unit_key("null", 999), {"hop1_rate": 0.5})
    assert unit_key("null", 999) in completed_units(ck_dir)
    assert load_units(ck_dir)[unit_key("null", 999)]["hop1_rate"] == 0.5
    exercised.add("exp_checkpoint_roundtrip")

    # ---- end-to-end pipeline on a reduced probe subset + tiny null ensemble ------------------------
    m = run("self_test", os.path.join(out, "run"), causenet_line_cap=2000, go_max_terms=None,
            baseline_line_cap=5000, n_probes_override=5, n_null_seeds=N_NULL_SEEDS_SELFTEST)
    exercised.add("run")
    assert m["n_probes"] == 5
    assert m["n_null_seeds"] == N_NULL_SEEDS_SELFTEST
    assert m["cardinality_ok"], m
    assert m["arms_differ_verified"], ("self-test arms collided", m["arm_hash_collisions"])
    assert m["gate"]["verdict"] in ("HARD_PASS", "MIDDLE_BAND", "HARD_FAIL")
    exercised.add("gate_verdict")

    need = {"base.load_baseline_edges", "base._extract_causenet_pairs", "base._extract_go_regulates",
            "degree_preserving_shuffle", "degree_invariant_check", "passthrough_identity_check",
            "shuffle_nontrivial_check", "base.build_adjacency", "base._recover_positive",
            "base._recover_negative", "exp_checkpoint_roundtrip", "run", "gate_verdict"}
    missing = need - exercised
    assert not missing, ("self-test skipped real entrypoints", missing)
    print(f"[self_test] PASS exercised={sorted(exercised)} "
          f"baseline_causal_edge_example={known_causal} causenet_pairs={len(causenet_edges)} "
          f"go_regulates={len(go_edges)} n_self_loops_sample={n_self_loops}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    output_dir = ART_DIR if mode == "full" else os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_{mode}")
    global _OUTPUT_DIR
    _OUTPUT_DIR = output_dir
    if mode == "self_test":
        self_test()
        return
    if mode == "smoke":
        run(mode, output_dir, causenet_line_cap=SMOKE_CAUSENET_LINE_CAP, go_max_terms=None,
            baseline_line_cap=SMOKE_BASELINE_LINE_CAP, n_null_seeds=N_NULL_SEEDS_SMOKE)
        return
    run(mode, output_dir, n_null_seeds=N_NULL_SEEDS_FULL)


_OUTPUT_DIR = ART_DIR

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_OUTPUT_DIR, e)
        raise
