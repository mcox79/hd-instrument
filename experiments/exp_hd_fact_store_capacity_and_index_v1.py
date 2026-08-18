"""CAPACITY BENCHMARK + SUB-LINEAR RETRIEVAL for the HD fact store (glass-box, can-fail).

Two deliverables, one inline-local foreground cell (no queue; runs to completion):

  PART A -- REAL-STORE capacity + index equivalence + insert-scaling.
     Builds REAL HDFactStore instances (exercises the real code path) over a
     (n_dim x n_facts) grid, measuring glass-box round-trip recovery, conflict-
     detection P/R, and asserting the O(1) content-hash index returns BYTE-IDENTICAL
     store() outcomes to the O(n) cosine reference (CAN-FAIL equivalence gate).

  PART B -- CROSSTALK WALL (analytical probe, memory-bounded, reuses the store's OWN
     bipolar primitives). Pushes the cleanup-codebook vocabulary V to 1,000,000 to
     locate where round-trip recovery crosses below 0.95, per n_dim. Validated against
     the real store at the V=10,000 overlap (positive control, Gate D).

  PART C -- INSERT SCALING: O(n) prototype vs O(1) indexed insert wall-time vs n_facts.

WHY THE WALL LIVES IN THE CLEANUP CODEBOOK (glass-box): the store is SHARDED -- every
fact is its OWN 5-role bundle, so a single fact's round-trip does NOT degrade with the
NUMBER of stored facts (no superposition load). The crosstalk that eventually breaks
recovery is the argmax CLEANUP over the per-domain symbol codebook, whose SIZE grows
with the distinct-symbol vocabulary. So capacity is a "how many near-orthogonal symbols
can dim-N distinguish" question, which is exponential in N -- Part B measures exactly
where it bites, per n_dim.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - real_code_path: PART A constructs the REAL HDFactStore + store()/query()/recover_fact
   at N in {1024..8192}, n_facts up to 10000 (NOT a synthetic-only branch).
 - substrate primitives REUSED (Part B): _bipolar_bind/_bipolar_quantize/_bipolar_random
   + codec.role_key -- byte-identical to the store's own encode/recover.
 - determinism guard: bipolar {-1,+1} dot products are EXACT integers (|sum|<=N<2^23),
   so scores + argmax are deterministic regardless of BLAS thread order; a key grid point
   is measured TWICE and asserted bit-identical.
 - arms_differ: the O(n) reference arm and the O(1) index arm produce the SAME outcomes
   BY DESIGN (that IS the equivalence claim) -> arms_differ_exempted for that pair; the
   discriminating axis is n_dim (recovery MUST degrade at small N / large V).
 - baseline_in_band: at n_dim=1024, large V, recovery is driven BELOW 0.95 (wall fires);
   at n_dim=8192 it stays high (headroom) -- the discriminator is not saturated.
 - except SystemExit: raise BEFORE except Exception (no BaseException).
 - atomic metrics: tmp + os.replace. start-marker written at main() entry.
 - all numbers MEASURED@ this cell's metrics.json (nothing hypothesized in the verdict).

INLINE-LOCAL foreground-to-completion. ASCII-only. All vectors torch.Tensor bipolar float32.
"""
from __future__ import annotations

import json
import os
import platform
import time
import traceback
from datetime import datetime, timezone

import torch

from hdlab.hd_fact_store import HDFactStore, TRUST_LEVEL, _run_all_selftests
from hdlab.role_slot_summarizer import _bipolar_bind, _bipolar_quantize, _bipolar_random

ANCHOR_NAME = "hd_fact_store_capacity_and_index_v1"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", f"exp_{ANCHOR_NAME}")

RECOVERY_WALL = 0.95           # round-trip recovery below this = crosstalk wall
FACT_ROLES = ("REL", "ARG0", "ARG1", "SOURCE", "TRUST")
ROLE_DOMAIN = {"ARG0": "SUBJECT", "REL": "RELATION", "ARG1": "OBJECT",
               "SOURCE": "SOURCE", "TRUST": "TRUST"}


# ============================ cell-template plumbing ================================
def _write_start_marker() -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": "inline_local", "host": platform.node()}
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "_start_marker.json"))


def _atomic_write_metrics(metrics: dict) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))


def _write_crash_metrics(exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(diag)


def _log(msg: str) -> None:
    print(f"[{ANCHOR_NAME}] {msg}", flush=True)


# ============================ PART A: real-store capacity ==========================
CARD = {"capital_of": "FUNCTIONAL", "born_in": "FUNCTIONAL", "located_in": "FUNCTIONAL",
        "atomic_number": "FUNCTIONAL", "speaks": "MULTIVALUED"}
FUNC_RELS = ("capital_of", "born_in", "located_in", "atomic_number")


def _build_clean(st: HDFactStore, n_facts: int) -> None:
    """Insert n_facts CLEAN facts: distinct subject + distinct object (vocab grows ~ n_facts),
    few relations, few sources (realistic curriculum shape: many entities, few relations)."""
    for i in range(n_facts):
        rel = FUNC_RELS[i % len(FUNC_RELS)]
        st.store(f"subj{i}", rel, f"obj{i}", f"src{i % 8}", "TRUST_MID")


def _measure_recovery(st: HDFactStore, n_sample: int, gen: torch.Generator) -> dict:
    """Glass-box round-trip: recover a random sample of stored facts, per-field exact accuracy."""
    facts = st.live_facts()
    if not facts:
        return {"n_sample": 0, "roundtrip_all5": 1.0, "obj_acc": 1.0, "subj_acc": 1.0}
    k = min(n_sample, len(facts))
    idx = torch.randperm(len(facts), generator=gen)[:k].tolist()
    all5 = obj = subj = 0
    for j in idx:
        f = facts[j]
        rec = st.recover_fact(f.vec)
        if rec["object"] == f.obj:
            obj += 1
        if rec["subject"] == f.subject:
            subj += 1
        if (rec["subject"] == f.subject and rec["relation"] == f.relation
                and rec["object"] == f.obj and rec["source"] == f.source
                and rec["trust"] == f.trust_sym):
            all5 += 1
    return {"n_sample": k, "roundtrip_all5": all5 / k, "obj_acc": obj / k, "subj_acc": subj / k}


def _measure_conflict_pr(st: HDFactStore, n_probe: int) -> dict:
    """Detection P/R + resolution accuracy on a labeled probe injected AFTER the clean build.
    Conflict trials contradict an existing subject (gt_conflict=True); clean trials use fresh
    subjects (gt_conflict=False). Precision/recall computed on detected_conflict vs ground truth."""
    tp = fp = tn = fn = 0
    res_ok = res_tot = 0
    # conflict trials: contradict existing subj{i} (FUNCTIONAL -> REPLACE via higher trust)
    for i in range(n_probe):
        r = st.store(f"subj{i}", FUNC_RELS[i % len(FUNC_RELS)], f"NEWobj{i}",
                     "chem_textbook", "TRUST_HIGH")
        if r.detected_conflict:
            tp += 1
        else:
            fn += 1
        res_tot += 1
        if r.resolution == "REPLACE":
            res_ok += 1
    # clean trials: fresh subjects, must NOT detect
    base = 10_000_000
    for i in range(n_probe):
        r = st.store(f"fresh{base + i}", "born_in", f"town{i}", "src0", "TRUST_MID")
        if r.detected_conflict:
            fp += 1
        else:
            tn += 1
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    return {"detection_precision": prec, "detection_recall": rec,
            "resolution_replace_acc": res_ok / res_tot if res_tot else 1.0,
            "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn}}


def _run_partA(n_dim_grid, n_facts_grid, sample=400, probe=100) -> list:
    rows = []
    for n_dim in n_dim_grid:
        for n_facts in n_facts_grid:
            t0 = time.perf_counter()
            st = HDFactStore(n_dim=n_dim, seed=7, relation_cardinality=CARD, use_index=True)
            _build_clean(st, n_facts)
            gen = torch.Generator(); gen.manual_seed(123)
            recov = _measure_recovery(st, sample, gen)
            pr = _measure_conflict_pr(st, probe)
            row = {"n_dim": n_dim, "n_facts": n_facts,
                   "vocab_subject": len(st._domain_syms["SUBJECT"]),
                   "vocab_object": len(st._domain_syms["OBJECT"]),
                   **recov, **pr, "elapsed_s": round(time.perf_counter() - t0, 2)}
            rows.append(row)
            _log(f"A n_dim={n_dim} n_facts={n_facts} rt_all5={recov['roundtrip_all5']:.3f} "
                 f"obj={recov['obj_acc']:.3f} det_P/R={pr['detection_precision']:.3f}/"
                 f"{pr['detection_recall']:.3f} ({row['elapsed_s']}s)")
            del st
    return rows


def _run_equivalence(n_dim_grid, n_facts=2000) -> dict:
    """CAN-FAIL: O(n) reference vs O(1) index produce byte-identical store()/query() outcomes
    on a mixed clean/conflict sequence, across all n_dim (small n_facts so O(n) is affordable)."""
    total_ops = 0
    mismatches = []
    for n_dim in n_dim_grid:
        lin = HDFactStore(n_dim=n_dim, seed=11, relation_cardinality=CARD, use_index=False)
        idx = HDFactStore(n_dim=n_dim, seed=11, relation_cardinality=CARD, use_index=True)
        ops = []
        for i in range(n_facts):
            ops.append((f"s{i}", FUNC_RELS[i % 4], f"o{i}", f"src{i % 5}", "TRUST_MID"))
        # inject conflicts of every resolution class against the first 200 subjects
        for i in range(200):
            trust = ("TRUST_HIGH", "TRUST_LOW", "TRUST_MID")[i % 3]
            ops.append((f"s{i}", FUNC_RELS[i % 4], f"alt{i}", "art2", trust))
        for i in range(60):  # MULTIVALUED combine + consistent dup
            ops.append((f"poly{i}", "speaks", f"lang{i}", "surveyA", "TRUST_MID"))
            ops.append((f"poly{i}", "speaks", f"lang2_{i}", "surveyB", "TRUST_MID"))
        for a in ops:
            rl = lin.store(*a)
            ri = idx.store(*a)
            total_ops += 1
            same = (rl.resolution == ri.resolution and rl.detected_conflict == ri.detected_conflict
                    and sorted(rl.conflict_fids) == sorted(ri.conflict_fids)
                    and sorted(rl.conflict_objs) == sorted(ri.conflict_objs))
            if not same and len(mismatches) < 20:
                mismatches.append({"n_dim": n_dim, "op": a, "lin": rl.resolution, "idx": ri.resolution})
        # query equivalence
        for q in [("poly3", "speaks"), ("s5", "capital_of"), ("s1", "born_in"), ("none", "born_in")]:
            ql = sorted((d["fid"], d["object"]) for d in lin.query(*q))
            qi = sorted((d["fid"], d["object"]) for d in idx.query(*q))
            if ql != qi and len(mismatches) < 20:
                mismatches.append({"n_dim": n_dim, "query": q, "lin": ql, "idx": qi})
        del lin, idx
    return {"total_ops": total_ops, "n_mismatches": len(mismatches),
            "mismatches": mismatches, "byte_equivalent": len(mismatches) == 0}


# ============================ PART B: crosstalk wall (analytical probe) =============
def _crosstalk_recovery(n_dim: int, V: int, n_probe: int, seed: int,
                        chunk: int = 20000) -> float:
    """Object-field round-trip recovery accuracy at cleanup-codebook size V, using the
    store's OWN primitives. Builds n_probe fact bundles (each: quantize(sum of 5 role-binds)),
    unbinds the OBJECT role, and cleans up by chunked argmax over V bipolar object codes
    (memory-bounded: codes generated in chunks, running best kept). Bipolar dot = exact int."""
    gen = torch.Generator(); gen.manual_seed(seed)
    # role keys shared; non-object fillers vary PER PROBE (exactly like the real store, where
    # each fact has its own subject/relation/source) so the estimate averages over base
    # randomness rather than conditioning on one draw.
    role_keys = {r: _bipolar_random((n_dim,), gen) for r in FACT_ROLES}
    # true object codes for the probes (their indices are 0..n_probe-1 in the V codebook)
    true_obj = _bipolar_random((n_probe, n_dim), gen)          # (P, N)
    # per-probe non-object base (P, N): sum of bind(role_key, per-probe random filler)
    base = torch.zeros((n_probe, n_dim), dtype=torch.float32)
    for r in FACT_ROLES:
        if r == "ARG1":
            continue
        base = base + _bipolar_bind(role_keys[r], _bipolar_random((n_probe, n_dim), gen))
    bundles = _bipolar_quantize(base + _bipolar_bind(role_keys["ARG1"], true_obj))  # (P,N)
    filler_hat = _bipolar_bind(bundles, role_keys["ARG1"])     # unbind OBJECT -> (P, N)
    # running argmax cleanup over V codes: first n_probe are the true codes, rest are distractors
    best_score = torch.full((n_probe,), -1e30)
    best_idx = torch.full((n_probe,), -1, dtype=torch.long)
    dgen = torch.Generator(); dgen.manual_seed(seed + 777)
    placed = 0
    global_off = 0
    while global_off < V:
        c = min(chunk, V - global_off)
        if placed < n_probe:
            take = min(c, n_probe - placed)
            head = true_obj[placed:placed + take]
            tail = _bipolar_random((c - take, n_dim), dgen) if c - take > 0 else None
            codes = head if tail is None else torch.cat([head, tail], 0)
            placed += take
        else:
            codes = _bipolar_random((c, n_dim), dgen)
        scores = filler_hat @ codes.T                          # (P, c) exact integer dots
        cmax, carg = scores.max(dim=1)
        upd = cmax > best_score
        best_idx = torch.where(upd, carg + global_off, best_idx)
        best_score = torch.where(upd, cmax, best_score)
        global_off += c
    correct = int((best_idx == torch.arange(n_probe)).sum().item())
    return correct / n_probe


def _run_partB(specs, n_probe=120) -> list:
    """specs: list of (n_dim, [V, ...]). Returns per-point recovery + the located wall."""
    rows = []
    for n_dim, Vs in specs:
        for V in Vs:
            t0 = time.perf_counter()
            acc = _crosstalk_recovery(n_dim, V, n_probe, seed=31)
            row = {"n_dim": n_dim, "V": V, "obj_recovery": acc,
                   "below_wall": acc < RECOVERY_WALL, "elapsed_s": round(time.perf_counter() - t0, 2)}
            rows.append(row)
            _log(f"B n_dim={n_dim} V={V} obj_recovery={acc:.3f} "
                 f"{'WALL' if acc < RECOVERY_WALL else 'ok'} ({row['elapsed_s']}s)")
    return rows


# ============================ PART C: insert scaling ===============================
def _time_inserts(n_dim: int, n_facts: int, use_index: bool) -> float:
    st = HDFactStore(n_dim=n_dim, seed=3, relation_cardinality=CARD, use_index=use_index)
    t0 = time.perf_counter()
    for i in range(n_facts):
        st.store(f"s{i}", FUNC_RELS[i % 4], f"o{i}", "src", "TRUST_MID")
    dt = time.perf_counter() - t0
    del st
    return dt


def _run_partC(n_dim, sizes) -> dict:
    linear = {}
    indexed = {}
    for n in sizes:
        indexed[n] = round(_time_inserts(n_dim, n, use_index=True), 4)
        linear[n] = round(_time_inserts(n_dim, n, use_index=False), 4)
        _log(f"C n_facts={n} linear={linear[n]}s indexed={indexed[n]}s "
             f"speedup={linear[n] / max(indexed[n], 1e-6):.1f}x")
    # complexity signature: linear total insert time ~ O(n^2) (per-insert O(n) scan);
    # indexed ~ O(n). Report the ratio growth.
    big = max(sizes)
    small = min(s for s in sizes if s >= 4)
    lin_ratio = linear[big] / max(linear[small], 1e-9)
    idx_ratio = indexed[big] / max(indexed[small], 1e-9)
    size_ratio = big / small
    return {"n_dim": n_dim, "sizes": list(sizes), "linear_s": linear, "indexed_s": indexed,
            "size_ratio": size_ratio,
            "linear_time_growth": round(lin_ratio, 2),   # ~ size_ratio^2 if O(n^2)
            "indexed_time_growth": round(idx_ratio, 2),  # ~ size_ratio   if O(n)
            "speedup_at_max": round(linear[big] / max(indexed[big], 1e-6), 1)}


# ============================ main =================================================
def main() -> None:
    t0 = time.perf_counter()
    _write_start_marker()
    selftest = _run_all_selftests()          # exercises the REAL store incl. index equivalence
    _log("module self-test PASS (incl. index==linear equivalence)")

    # PART A -- real-store capacity + equivalence. Small dims (128/256) sit in the DEGRADING
    # regime (Gate-D overlap not saturated); production dims (1024/8192) show headroom.
    A_grid_dim = [128, 256, 1024, 8192]
    A_grid_facts = [1000, 10000]
    partA = _run_partA(A_grid_dim, A_grid_facts, sample=150, probe=60)
    equiv = _run_equivalence([128, 1024, 8192], n_facts=1000)
    _log(f"equivalence byte_equivalent={equiv['byte_equivalent']} over {equiv['total_ops']} ops")

    # PART B -- crosstalk WALL. Small dims MAP the wall (recovery drops below 0.95); production
    # dims confirm headroom to V=1,000,000. Bipolar cleanup margin ~ 0.375*sqrt(n_dim) sigma, so
    # the wall is exponential in n_dim -- it fires at tiny N and is astronomically far at N>=2048.
    B_Vs = [10000, 100000, 1000000]
    B_specs = [(n_dim, B_Vs) for n_dim in (64, 96, 128, 192, 256, 512, 1024, 2048, 8192)]
    partB = _run_partB(B_specs)

    # Gate D positive control: probe obj-recovery at V=10k must match real store obj_acc
    # at n_facts=10000 (same effective object-codebook size) within tolerance.
    def _probe_at(n_dim, V):
        for r in partB:
            if r["n_dim"] == n_dim and r["V"] == V:
                return r["obj_recovery"]
        return None
    def _real_at(n_dim, n_facts):
        for r in partA:
            if r["n_dim"] == n_dim and r["n_facts"] == n_facts:
                return r["obj_acc"]
        return None
    control = []
    for n_dim in A_grid_dim:
        p = _probe_at(n_dim, 10000); r = _real_at(n_dim, 10000)
        if p is not None and r is not None:
            control.append({"n_dim": n_dim, "probe_obj_recovery": p, "real_obj_acc": r,
                            "abs_delta": round(abs(p - r), 4), "within_0.05": abs(p - r) <= 0.05})
    control_ok = all(c["within_0.05"] for c in control)

    # determinism guard: re-run one Part B point, assert bit-identical
    d1 = _crosstalk_recovery(1024, 100000, 120, seed=31)
    d2 = _crosstalk_recovery(1024, 100000, 120, seed=31)
    deterministic = (d1 == d2)

    # ---- locate the wall per n_dim (smallest V with recovery < 0.95; else headroom) ----
    wall = {}
    for n_dim in A_grid_dim:
        pts = sorted([r for r in partB if r["n_dim"] == n_dim], key=lambda r: r["V"])
        below = [r["V"] for r in pts if r["below_wall"]]
        max_v = max(r["V"] for r in pts)
        wall[str(n_dim)] = {"wall_V": (min(below) if below else None),
                            "max_V_tested": max_v,
                            "recovery_at_max_V": next(r["obj_recovery"] for r in pts if r["V"] == max_v)}

    # ---- verdict bands (pre-registered; see prereg md) ----
    #  PASS requires ALL:
    #   (1) byte_equivalent index == linear (correctness-equivalence, CAN-FAIL)
    #   (2) Gate D control_ok (analytical probe reproduces real store at overlap)
    #   (3) deterministic
    #   (4) discriminator fired: recovery DEGRADES below 0.95 at some (n_dim,V) AND stays
    #       >=0.99 at n_dim=8192,V=10k (band not saturated, not floored)
    disc_degraded = any(r["below_wall"] for r in partB)
    disc_headroom = any(r["n_dim"] == 8192 and r["V"] == 1000000 and r["obj_recovery"] >= 0.99
                        for r in partB)
    discriminator_fired = disc_degraded and disc_headroom
    passes = (equiv["byte_equivalent"] and control_ok and deterministic and discriminator_fired)
    verdict = "PASS" if passes else "FAIL"

    n_dim8192 = wall["8192"]
    foundation_ready = (n_dim8192["wall_V"] is None or n_dim8192["wall_V"] >= 1000000)

    metrics = {
        "verdict": verdict,
        "verdict_msg": (f"index_byte_equiv={equiv['byte_equivalent']} "
                        f"gateD_control_ok={control_ok} determ={deterministic} "
                        f"disc_fired={discriminator_fired} "
                        f"wall@8192={n_dim8192['wall_V']} (max_V={n_dim8192['max_V_tested']}, "
                        f"rec@maxV={n_dim8192['recovery_at_max_V']:.3f}) "
                        f"insertC_speedup@max={None}"),
        "summary": f"HD fact store capacity + sub-linear index: {verdict}",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "recovery_wall_threshold": RECOVERY_WALL,
        "deterministic": deterministic,
        "discriminator_fired": discriminator_fired,
        "partA_real_store": partA,
        "index_equivalence": equiv,
        "partB_crosstalk_wall": partB,
        "wall_per_n_dim": wall,
        "gateD_positive_control": {"points": control, "control_ok": control_ok},
        "foundation_ready_at_8192_to_1M": foundation_ready,
        "selftest": selftest,
        "trust_ladder": TRUST_LEVEL,
        "honest_frame": ("SHARDED store: single-fact recovery is independent of n_facts; the "
                         "wall is cleanup-codebook (vocabulary) crosstalk, exponential in n_dim. "
                         "Sub-linear index = content-hash of the deterministic (s,r) signature "
                         "(exact-match, O(1), byte-equivalent to the O(n) cosine scan)."),
    }
    # Part C is timed last (cheap) and injected so the verdict_msg can carry the speedup.
    partC = _run_partC(n_dim=2048, sizes=[100, 500, 1000, 2000, 4000])
    metrics["partC_insert_scaling"] = partC
    metrics["verdict_msg"] = metrics["verdict_msg"].replace(
        "insertC_speedup@max=None", f"insertC_speedup@max={partC['speedup_at_max']}x")

    _atomic_write_metrics(metrics)
    _log(f"{verdict} :: {metrics['verdict_msg']}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise
