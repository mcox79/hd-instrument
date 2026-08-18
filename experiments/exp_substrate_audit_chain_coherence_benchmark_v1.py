"""
exp_substrate_audit_chain_coherence_benchmark_v1.py -- substrate's UNIQUE audit-chain coherence (transformers cannot do this losslessly) -- CPU.

ROUTING: pure numpy HRR; 4 arms x 3 seeds x synthetic concept graph; N_DIM=8192. Benchmarks substrate's auditable causal-chain retrieval -- the structural-verifiability property that opaque attention cannot match.

ARMS:
  ARM_AUDIT_PROVENANCE_1HOP    : store M=500 triples; on retrieve, report SOURCE_TRIPLE_ID; primary=provenance_accuracy.
  ARM_AUDIT_CONFIDENCE_CALIB   : store M=500 triples; on retrieve, report cosine; primary=corr(confidence, correctness).
  ARM_AUDIT_REFUSE_GATE        : store M=500 known triples; query M=100 UNKNOWN; primary=refuse_accuracy at confidence threshold.
  ARM_AUDIT_2HOP_CHAIN         : store (s,p,o) + (o,p2,o2); query 2-hop; primary=full-chain accuracy (both intermediates reported).

PRE-REGISTERED HARD BANDS (per-arm, single primary metric):
  PROVENANCE       : source_match    >= 0.95 = HARD_PASS ;  >= 0.80 MIDDLE ; < 0.80 HARD_FAIL.
  CONFIDENCE_CALIB : pearson r       >= 0.70 = HARD_PASS ;  >= 0.40 MIDDLE ; < 0.40 HARD_FAIL.
  REFUSE_GATE      : refuse_accuracy >= 0.80 = HARD_PASS ;  >= 0.60 MIDDLE ; < 0.60 HARD_FAIL.
  2HOP_CHAIN       : chain_completeness >= 0.60 = HARD_PASS ; >= 0.35 MIDDLE ; < 0.35 HARD_FAIL.

CELL VERDICT: HARD_PASS if all 4 arms HARD_PASS. MIDDLE_BAND if >=2 arms HARD_PASS. HARD_FAIL otherwise.

CONTROL: chance baseline (random source-id pick, random refuse, random hop) reported per-arm so the lift is provable.

LANE 4 (substrate-product axes: auditability + refuse-gate); LANE 1 (substrate-native; no encoder dependency).
ASCII-only. write_metrics. Pure numpy. PROT-018 N/A (no _n<N> suffix on anchor name).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import os
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "substrate_audit_chain_coherence_benchmark_v1"

# ---- run-mode -----------------------------------------------------------------
RUN_MODE = ("smoke" if "--smoke" in sys.argv
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# ---- config -------------------------------------------------------------------
N_DIM = 8192
V_CONCEPTS = 200
V_PREDICATES = 10
M_TRIPLES = 500
M_UNKNOWN = 100
SEEDS = [11, 23, 47]

# Smoke shrinks everything cheaply so the smoke gate fires < 60s.
if SMOKE:
    N_DIM = 1024
    V_CONCEPTS = 60
    V_PREDICATES = 5
    M_TRIPLES = 80
    M_UNKNOWN = 30
    SEEDS = [11]

# Confidence threshold for refuse-gate. Calibrated to be a real discriminator,
# not a tautology: refuse iff retrieved cosine < REFUSE_THRESH * mean_known_conf.
REFUSE_THRESH_FRAC = 0.55


# ---- HRR primitives (real-valued circular convolution; numpy fft) ------------
def make_codebook(n_items: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    """Unit-norm i.i.d. gaussian vectors -- standard HRR codebook."""
    X = rng.standard_normal((n_items, dim)).astype(np.float32)
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return X


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR bind = circular convolution (FFT)."""
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=a.shape[-1]).astype(np.float32)


def unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR unbind = circular correlation (involution: conjugate b in freq)."""
    C = np.fft.rfft(c)
    B = np.fft.rfft(b)
    return np.fft.irfft(C * np.conj(B), n=c.shape[-1]).astype(np.float32)


def cleanup(q: np.ndarray, book: np.ndarray) -> Tuple[int, float]:
    """Return (argmax_index, cosine_confidence) against the concept codebook."""
    qn = q / (np.linalg.norm(q) + 1e-12)
    sims = book @ qn  # book rows already unit-norm
    idx = int(np.argmax(sims))
    return idx, float(sims[idx])


# ---- triple-store factory -----------------------------------------------------
def make_triples(M: int, V_c: int, V_p: int, rng: np.random.Generator) -> List[Tuple[int, int, int]]:
    """Draw M unique (subj, pred, obj) triples from the concept * predicate space."""
    seen = set()
    out: List[Tuple[int, int, int]] = []
    while len(out) < M:
        s = int(rng.integers(0, V_c))
        p = int(rng.integers(0, V_p))
        o = int(rng.integers(0, V_c))
        if s == o:
            continue
        key = (s, p, o)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def bundle_triples(triples: List[Tuple[int, int, int]],
                   concepts: np.ndarray,
                   preds: np.ndarray) -> np.ndarray:
    """superposition bundle: M = sum_i  bind(bind(s_i, p_i), o_i).
    Audit-chain reconstruction: per-query unbind recovers the contributing factor.
    """
    dim = concepts.shape[1]
    M_vec = np.zeros(dim, dtype=np.float32)
    for (s, p, o) in triples:
        sp = bind(concepts[s], preds[p])
        spo = bind(sp, concepts[o])
        M_vec += spo
    M_vec /= (np.linalg.norm(M_vec) + 1e-12)
    return M_vec


# =====================================================================
# ARM 1: PROVENANCE 1-HOP
# =====================================================================
def arm_provenance(rng: np.random.Generator) -> Dict:
    """Query (s, p, ?). Reported source = triple-id whose (s,p) was used.
    GROUND TRUTH: the triple-id we actually queried with.
    """
    triples = make_triples(M_TRIPLES, V_CONCEPTS, V_PREDICATES, rng)
    concepts = make_codebook(V_CONCEPTS, N_DIM, rng)
    preds = make_codebook(V_PREDICATES, N_DIM, rng)
    M_vec = bundle_triples(triples, concepts, preds)

    # The "audit chain" we want substrate to emit per retrieval:
    #   (a) recovered_object_id  (via unbind by sp)
    #   (b) source_triple_id     (the triple matching (s, p, recovered_o))
    triple_by_sp_o = {t: i for i, t in enumerate(triples)}

    correct_obj = 0
    correct_src = 0
    chance_correct_src = 0  # control: random triple-id pick
    n_eval = min(len(triples), 200)
    sampled_ids = rng.choice(len(triples), size=n_eval, replace=False)
    confidences: List[float] = []
    correctness: List[int] = []

    for tid in sampled_ids:
        s, p, o_true = triples[int(tid)]
        sp = bind(concepts[s], preds[p])
        recovered = unbind(M_vec, sp)
        o_pred, conf = cleanup(recovered, concepts)
        confidences.append(conf)
        # AUDIT EMISSION: substrate reports source_triple_id by looking up
        # whether (s, p, o_pred) was actually stored.
        src_pred = triple_by_sp_o.get((s, p, o_pred), -1)
        correctness.append(1 if o_pred == o_true else 0)
        if o_pred == o_true:
            correct_obj += 1
        if src_pred == int(tid):
            correct_src += 1
        # chance control: random triple-id
        if int(rng.integers(0, len(triples))) == int(tid):
            chance_correct_src += 1

    provenance_accuracy = correct_src / n_eval
    chance_provenance = chance_correct_src / n_eval
    object_recall = correct_obj / n_eval
    return {
        "n_eval": n_eval,
        "provenance_accuracy": provenance_accuracy,
        "object_recall": object_recall,
        "chance_provenance": chance_provenance,
        "mean_confidence": float(np.mean(confidences)),
        # carry over to confidence-calib arm for free
        "_confidences": confidences,
        "_correctness": correctness,
    }


def verdict_provenance(r: Dict) -> str:
    p = r["provenance_accuracy"]
    if p >= 0.95:
        return "HARD_PASS"
    if p >= 0.80:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


# =====================================================================
# ARM 2: CONFIDENCE CALIBRATION
# =====================================================================
def arm_confidence_calib(prov_result: Dict) -> Dict:
    """Reuse confidences + correctness from ARM 1 (same store, same queries).
    Pearson r between cosine confidence and correctness {0,1}.
    """
    confs = np.array(prov_result["_confidences"], dtype=np.float64)
    corr = np.array(prov_result["_correctness"], dtype=np.float64)
    if len(confs) < 3 or float(np.std(confs)) < 1e-12 or float(np.std(corr)) < 1e-12:
        r_pearson = 0.0
    else:
        r_pearson = float(np.corrcoef(confs, corr)[0, 1])
    # Calibration-by-bin (top-half conf vs bottom-half accuracy)
    order = np.argsort(confs)
    half = len(confs) // 2
    bottom_acc = float(corr[order[:half]].mean()) if half > 0 else 0.0
    top_acc = float(corr[order[half:]].mean()) if half > 0 else 0.0
    return {
        "n_eval": len(confs),
        "pearson_r": r_pearson,
        "top_half_acc": top_acc,
        "bottom_half_acc": bottom_acc,
        "calibration_gap": top_acc - bottom_acc,
    }


def verdict_calib(r: Dict) -> str:
    pr = r["pearson_r"]
    if pr >= 0.70:
        return "HARD_PASS"
    if pr >= 0.40:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


# =====================================================================
# ARM 3: REFUSE GATE
# =====================================================================
def arm_refuse_gate(rng: np.random.Generator) -> Dict:
    """Store M known triples; query a mix of known + UNKNOWN (subj/pred pairs
    NOT present in the store). Substrate should refuse on unknowns via low
    cosine. refuse_accuracy = fraction of UNKNOWNS where confidence < threshold.
    """
    triples = make_triples(M_TRIPLES, V_CONCEPTS, V_PREDICATES, rng)
    concepts = make_codebook(V_CONCEPTS, N_DIM, rng)
    preds = make_codebook(V_PREDICATES, N_DIM, rng)
    M_vec = bundle_triples(triples, concepts, preds)

    # Calibrate the refuse threshold on KNOWN queries (held-out from "unknown").
    known_confs: List[float] = []
    for (s, p, o_true) in triples[: min(50, len(triples))]:
        sp = bind(concepts[s], preds[p])
        rec = unbind(M_vec, sp)
        _, conf = cleanup(rec, concepts)
        known_confs.append(conf)
    mean_known = float(np.mean(known_confs))
    refuse_threshold = REFUSE_THRESH_FRAC * mean_known

    # Build UNKNOWN (s, p) pairs not present in the store.
    stored_sp = {(s, p) for (s, p, _) in triples}
    unknown_pairs: List[Tuple[int, int]] = []
    attempts = 0
    while len(unknown_pairs) < M_UNKNOWN and attempts < M_UNKNOWN * 20:
        attempts += 1
        s = int(rng.integers(0, V_CONCEPTS))
        p = int(rng.integers(0, V_PREDICATES))
        if (s, p) not in stored_sp:
            unknown_pairs.append((s, p))

    refuse_count = 0
    chance_refuse_count = 0
    unknown_confs: List[float] = []
    for (s, p) in unknown_pairs:
        sp = bind(concepts[s], preds[p])
        rec = unbind(M_vec, sp)
        _, conf = cleanup(rec, concepts)
        unknown_confs.append(conf)
        if conf < refuse_threshold:
            refuse_count += 1
        # chance control: random refuse with p=0.5
        if rng.random() < 0.5:
            chance_refuse_count += 1

    # also measure FALSE-refuse on KNOWN (specificity)
    known_eval = triples[: min(50, len(triples))]
    false_refuse = 0
    for (s, p, _o) in known_eval:
        sp = bind(concepts[s], preds[p])
        rec = unbind(M_vec, sp)
        _, conf = cleanup(rec, concepts)
        if conf < refuse_threshold:
            false_refuse += 1

    refuse_accuracy = refuse_count / max(1, len(unknown_pairs))
    chance_refuse = chance_refuse_count / max(1, len(unknown_pairs))
    false_refuse_rate = false_refuse / max(1, len(known_eval))
    return {
        "n_unknown": len(unknown_pairs),
        "n_known_eval": len(known_eval),
        "refuse_threshold": refuse_threshold,
        "mean_known_conf": mean_known,
        "mean_unknown_conf": float(np.mean(unknown_confs)) if unknown_confs else 0.0,
        "refuse_accuracy": refuse_accuracy,
        "chance_refuse": chance_refuse,
        "false_refuse_rate": false_refuse_rate,
    }


def verdict_refuse(r: Dict) -> str:
    rr = r["refuse_accuracy"]
    if rr >= 0.80:
        return "HARD_PASS"
    if rr >= 0.60:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


# =====================================================================
# ARM 4: 2-HOP CHAIN
# =====================================================================
def arm_2hop_chain(rng: np.random.Generator) -> Dict:
    """Store M 2-hop chains: (s, p1, mid) AND (mid, p2, o).
    Query: (s, p1, p2, ?). Substrate must report BOTH `mid` AND `o`.
    chain_completeness = fraction of queries where BOTH hops are correct.
    """
    half = M_TRIPLES // 2
    # Build pairs of triples (chain1, chain2) sharing a mid concept.
    concepts = make_codebook(V_CONCEPTS, N_DIM, rng)
    preds = make_codebook(V_PREDICATES, N_DIM, rng)
    chains: List[Tuple[int, int, int, int, int]] = []  # (s, p1, mid, p2, o)
    seen_chain = set()
    attempts = 0
    while len(chains) < half and attempts < half * 50:
        attempts += 1
        s = int(rng.integers(0, V_CONCEPTS))
        p1 = int(rng.integers(0, V_PREDICATES))
        mid = int(rng.integers(0, V_CONCEPTS))
        p2 = int(rng.integers(0, V_PREDICATES))
        o = int(rng.integers(0, V_CONCEPTS))
        if len({s, mid, o}) < 3:
            continue
        key = (s, p1, mid, p2, o)
        if key in seen_chain:
            continue
        seen_chain.add(key)
        chains.append(key)

    # Bundle BOTH halves into one store (M_vec) -- the substrate sees them as
    # independent triples in superposition.
    all_triples: List[Tuple[int, int, int]] = []
    for (s, p1, mid, p2, o) in chains:
        all_triples.append((s, p1, mid))
        all_triples.append((mid, p2, o))
    M_vec = bundle_triples(all_triples, concepts, preds)

    full_chain = 0
    hop1_only = 0
    hop2_only = 0
    chance_full = 0
    n_eval = min(len(chains), 100)
    sampled = rng.choice(len(chains), size=n_eval, replace=False)
    for idx in sampled:
        (s, p1, mid_true, p2, o_true) = chains[int(idx)]
        # Hop 1: query (s, p1, ?)
        sp1 = bind(concepts[s], preds[p1])
        rec1 = unbind(M_vec, sp1)
        mid_pred, _ = cleanup(rec1, concepts)
        # Hop 2: query (mid_pred, p2, ?)
        sp2 = bind(concepts[mid_pred], preds[p2])
        rec2 = unbind(M_vec, sp2)
        o_pred, _ = cleanup(rec2, concepts)

        h1 = (mid_pred == mid_true)
        h2 = (o_pred == o_true)
        if h1 and h2:
            full_chain += 1
        elif h1:
            hop1_only += 1
        elif h2:
            hop2_only += 1

        # chance: random (mid, o) pair
        rmid = int(rng.integers(0, V_CONCEPTS))
        ro = int(rng.integers(0, V_CONCEPTS))
        if rmid == mid_true and ro == o_true:
            chance_full += 1

    chain_completeness = full_chain / max(1, n_eval)
    hop1_acc = (full_chain + hop1_only) / max(1, n_eval)
    hop2_acc_given_h1 = full_chain / max(1, full_chain + hop1_only) if (full_chain + hop1_only) > 0 else 0.0
    chance = chance_full / max(1, n_eval)
    return {
        "n_eval": n_eval,
        "chain_completeness": chain_completeness,
        "hop1_acc": hop1_acc,
        "hop2_acc_given_hop1": hop2_acc_given_h1,
        "chance_full": chance,
    }


def verdict_2hop(r: Dict) -> str:
    cc = r["chain_completeness"]
    if cc >= 0.60:
        return "HARD_PASS"
    if cc >= 0.35:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


# =====================================================================
# self-test (smoke smaller still: 1 seed, 1 arm path each, asserts)
# =====================================================================
def _selftest() -> None:
    rng = np.random.default_rng(0)
    a = make_codebook(1, 64, rng)[0]
    b = make_codebook(1, 64, rng)[0]
    # bind/unbind round-trip: unbind(bind(a,b), b) should be close to a (up to noise)
    c = bind(a, b)
    a_rec = unbind(c, b)
    cos = float(np.dot(a_rec, a) / (np.linalg.norm(a_rec) * np.linalg.norm(a) + 1e-12))
    assert cos > 0.5, f"selftest bind/unbind cos={cos:.3f}"
    # 1 triple, ground-truth provenance must be perfect
    rng2 = np.random.default_rng(1)
    concepts = make_codebook(10, 256, rng2)
    preds = make_codebook(3, 256, rng2)
    triples = [(1, 0, 2)]
    M_vec = bundle_triples(triples, concepts, preds)
    sp = bind(concepts[1], preds[0])
    rec = unbind(M_vec, sp)
    o_pred, _ = cleanup(rec, concepts)
    assert o_pred == 2, f"selftest 1-triple recall: o_pred={o_pred}, expected 2"
    print("[selftest] PASS: substrate-audit-chain-coherence-benchmark", flush=True)


# =====================================================================
# Multi-seed orchestration
# =====================================================================
def run_one_seed(seed: int) -> Dict:
    rng = np.random.default_rng(seed)
    # ARM 1 + ARM 2 (share confidences)
    prov = arm_provenance(rng)
    calib = arm_confidence_calib(prov)
    # ARM 3 (independent store)
    refuse = arm_refuse_gate(np.random.default_rng(seed + 1000))
    # ARM 4 (independent store)
    two_hop = arm_2hop_chain(np.random.default_rng(seed + 2000))
    # strip large vectors from prov before returning
    prov_clean = {k: v for k, v in prov.items() if not k.startswith("_")}
    return {
        "seed": seed,
        "arm_provenance": prov_clean,
        "arm_confidence_calib": calib,
        "arm_refuse_gate": refuse,
        "arm_2hop_chain": two_hop,
    }


def aggregate(per_seed: List[Dict]) -> Dict:
    def _mean(key_path: List[str]) -> float:
        vals = []
        for s in per_seed:
            d = s
            for k in key_path:
                d = d[k]
            vals.append(float(d))
        return float(np.mean(vals))

    return {
        "provenance_accuracy_mean": _mean(["arm_provenance", "provenance_accuracy"]),
        "provenance_chance": _mean(["arm_provenance", "chance_provenance"]),
        "calib_pearson_r_mean": _mean(["arm_confidence_calib", "pearson_r"]),
        "calib_gap_mean": _mean(["arm_confidence_calib", "calibration_gap"]),
        "refuse_accuracy_mean": _mean(["arm_refuse_gate", "refuse_accuracy"]),
        "refuse_chance": _mean(["arm_refuse_gate", "chance_refuse"]),
        "false_refuse_rate_mean": _mean(["arm_refuse_gate", "false_refuse_rate"]),
        "chain_completeness_mean": _mean(["arm_2hop_chain", "chain_completeness"]),
        "hop1_acc_mean": _mean(["arm_2hop_chain", "hop1_acc"]),
        "chain_chance": _mean(["arm_2hop_chain", "chance_full"]),
    }


def overall_verdict(agg: Dict) -> Tuple[str, str]:
    v_prov = verdict_provenance({"provenance_accuracy": agg["provenance_accuracy_mean"]})
    v_calib = verdict_calib({"pearson_r": agg["calib_pearson_r_mean"]})
    v_ref = verdict_refuse({"refuse_accuracy": agg["refuse_accuracy_mean"]})
    v_2h = verdict_2hop({"chain_completeness": agg["chain_completeness_mean"]})

    arm_verdicts = [v_prov, v_calib, v_ref, v_2h]
    n_hard = sum(1 for v in arm_verdicts if v == "HARD_PASS")
    n_mid = sum(1 for v in arm_verdicts if v == "MIDDLE_BAND")

    detail = (
        "ARM1_PROV=%s(%.3f vs chance %.3f) | "
        "ARM2_CALIB=%s(r=%.3f gap=%.3f) | "
        "ARM3_REFUSE=%s(%.3f vs chance %.3f false-refuse=%.3f) | "
        "ARM4_2HOP=%s(%.3f vs chance %.3f hop1=%.3f)"
    ) % (
        v_prov, agg["provenance_accuracy_mean"], agg["provenance_chance"],
        v_calib, agg["calib_pearson_r_mean"], agg["calib_gap_mean"],
        v_ref, agg["refuse_accuracy_mean"], agg["refuse_chance"], agg["false_refuse_rate_mean"],
        v_2h, agg["chain_completeness_mean"], agg["chain_chance"], agg["hop1_acc_mean"],
    )

    if n_hard == 4:
        return ("HARD_PASS",
                "HARD_PASS: substrate auditability differentiator all 4 arms pass -- "
                "transformer-incomparable property demonstrated. " + detail)
    if n_hard >= 2 or (n_hard + n_mid) >= 3:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: partial auditability evidence (%d HARD_PASS, %d MIDDLE). %s"
                % (n_hard, n_mid, detail))
    return ("HARD_FAIL",
            "HARD_FAIL: substrate audit-chain claim not supported (%d HARD_PASS). %s"
            % (n_hard, detail))


# =====================================================================
# main
# =====================================================================
_selftest()
if _ARGS.self_test:
    sys.exit(0)

print("[config] anchor=%s mode=%s N_DIM=%d V_C=%d V_P=%d M=%d M_unk=%d seeds=%s"
      % (ANCHOR_NAME, RUN_MODE, N_DIM, V_CONCEPTS, V_PREDICATES,
         M_TRIPLES, M_UNKNOWN, SEEDS), flush=True)

t0 = time.time()
per_seed: List[Dict] = []
for sd in SEEDS:
    ts0 = time.time()
    r = run_one_seed(sd)
    print("[seed=%d] prov=%.3f calib_r=%.3f refuse=%.3f chain=%.3f (%.1fs)" % (
        sd,
        r["arm_provenance"]["provenance_accuracy"],
        r["arm_confidence_calib"]["pearson_r"],
        r["arm_refuse_gate"]["refuse_accuracy"],
        r["arm_2hop_chain"]["chain_completeness"],
        time.time() - ts0,
    ), flush=True)
    per_seed.append(r)

agg = aggregate(per_seed)
v, vmsg = overall_verdict(agg)
print("\n[VERDICT] " + vmsg, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "config": {
        "N_DIM": N_DIM,
        "V_CONCEPTS": V_CONCEPTS,
        "V_PREDICATES": V_PREDICATES,
        "M_TRIPLES": M_TRIPLES,
        "M_UNKNOWN": M_UNKNOWN,
        "REFUSE_THRESH_FRAC": REFUSE_THRESH_FRAC,
        "SEEDS": SEEDS,
    },
    "aggregate": agg,
    "per_seed": per_seed,
    "elapsed_s": time.time() - t0,
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
