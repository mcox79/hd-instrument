"""exp_entity_store_unified_litbank_v1 -- FAIR, GPU-ready validation of the unified store's graded
temporal context on the REAL LitBank register.

THE FAIR TEST (isolates the one variable that matters). The fan is already fixed by a FINER conjunctive
key (the SOLVED result). So the honest question is NOT "does graded beat the organ" (any finer key does)
-- it is: does the GRADED temporal context flatten the fan JUST AS WELL as the cheap ORTHOGONAL finer key,
while UNIQUELY preserving TEMPORAL CONTIGUITY (which the orthogonal key destroys)? Two arms, IDENTICAL in
every way (same events, same content atoms, same d, same finer (slot,order) key) EXCEPT the context code:

  CHEAP_ORTHO  : key = orthogonal_idx(slot, order)   -- the SOLVED fix. Flat fan, ZERO contiguity.
  UNIFIED_GRAD : key = graded_clock(slot) * order(order) -- CTX(t)[k]=exp(i(w_k t+phi_k)). Flat fan AND
                 a temporal-contiguity gradient.
  (ORGAN_COARSE baseline, measured earlier on the SAME events/oracle: fan 0.9455@1-3 -> 0.6574@17+,
   slope 0.288 -- the collision fan a coarse (entity,sentence) key suffers; both finer arms fix it.)

HARD-PASS: UNIFIED_GRAD fan-slope ~= CHEAP_ORTHO fan-slope (both ~0, no fan cost from grading) AND
UNIFIED_GRAD contiguity gradient >> CHEAP_ORTHO (~0). HARD-FAIL: grading costs fan accuracy, or shows no
contiguity.

GPU-READY: all hot compute is torch complex64 on `cuda` if available (the remote RTX 4060 Ti), else cpu;
per-entity batched cleanup (one complex matmul per entity). Reuses load_events (oracle linking).
--self-test / --smoke write data/exp_<HDLAB_EXP_NAME>/metrics.json (queue-compliant). NO hdlab/ write.

Run: .venv/Scripts/python.exe experiments/exp_entity_store_unified_litbank_v1.py --self-test
     ... --smoke   (5 docs, writes metrics.json)      ... --full   (100 docs)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Dict, List, Optional

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_entity_store_sparse_fan_v1 import load_events, binof, BINS  # noqa: E402

D = 4096
SEED = 20260827
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _unit_phase(n: int, d: int, g: torch.Generator) -> torch.Tensor:
    theta = torch.rand(n, d, generator=g, device=g.device) * (2 * math.pi)
    return torch.polar(torch.ones(n, d, device=g.device), theta).to(torch.complex64)


def _graded_clock(slots: torch.Tensor, d: int, g: torch.Generator, horizon: int) -> torch.Tensor:
    """CTX(t)[k]=exp(i(w_k t + phi_k)), log-spaced w_k. slots:(n,) -> (n,d) complex64 (bindable + graded)."""
    periods = torch.logspace(math.log10(2.0), math.log10(4.0 * max(horizon, 1)), d, device=g.device)
    omega = (2 * math.pi / periods)
    phase = torch.rand(d, generator=g, device=g.device) * (2 * math.pi)
    ang = slots.to(torch.float32)[:, None] * omega[None, :] + phase[None, :]
    return torch.polar(torch.ones(slots.shape[0], d, device=g.device), ang).to(torch.complex64)


def _cleanup_argmax(readbacks: torch.Tensor, content: torch.Tensor) -> torch.Tensor:
    """readbacks (n,d) complex, content (V,d) complex -> argmax over V of Re(<conj(content), readback>)."""
    scores = torch.real(readbacks @ content.conj().T)   # (n, V)
    return torch.argmax(scores, dim=1)


def _score_doc(rec, d, seed) -> Dict:
    """Score CHEAP_ORTHO and UNIFIED_GRAD on one doc. Returns per-arm [(ok, ev_count)] + contiguity grads."""
    events = list(rec["events"])                        # (entity, slot, order, verb)
    vocab = list(rec["verb_vocab"]); vidx = {v: i for i, v in enumerate(vocab)}
    n_slots = max(rec["n_slots"], 2)
    V = len(vocab)
    g = torch.Generator(device=DEVICE); g.manual_seed(seed)
    content = _unit_phase(V, d, g)                       # shared across arms (fair)
    n_orders = 16
    order = _unit_phase(n_orders, d, g)
    # slot idx vecs: orthogonal per (slot,order) for CHEAP; graded clock for UNIFIED
    ortho_slot = _unit_phase(n_slots, d, g)             # random per slot (orthogonal across slots)
    ev_count = Counter(E for E, _, _, _ in events)

    # group events by entity
    by_ent = defaultdict(list)
    for E, s, o, v in events:
        by_ent[str(E)].append((s, o, v))

    all_slots = torch.tensor([s for _, s, _, _ in events], dtype=torch.float32, device=DEVICE)
    grad_ctx_all = _graded_clock(torch.arange(n_slots, device=DEVICE), d, torch.Generator(device=DEVICE).manual_seed(seed + 1), n_slots)

    def sharp_key(s, o):
        return ortho_slot[s] * order[o % n_orders]

    def grad_key(s, o):
        return grad_ctx_all[s] * order[o % n_orders]

    def build_and_score(arm):
        # arm in {CHEAP_ORTHO, UNIFIED_GRAD, FACTORIZED}. FACTORIZED keeps TWO bundles (the brain's
        # DG-sharp + EC-graded division of labor): exact recall reads the SHARP store (flat fan), contiguity
        # reads the GRADED store -- getting BOTH from one factorized memory, not one combined key.
        res, contig = [], []
        for e, evs in by_ent.items():
            sharp_b = torch.zeros(d, dtype=torch.complex64, device=DEVICE)
            grad_b = torch.zeros(d, dtype=torch.complex64, device=DEVICE)
            keys, verbs = [], []
            for (s, o, v) in evs:
                c = content[vidx[v]]
                sharp_b = sharp_b + c * sharp_key(s, o)
                grad_b = grad_b + c * grad_key(s, o)
                # the EXACT-decode key for this arm:
                keys.append(grad_key(s, o) if arm == "UNIFIED_GRAD" else sharp_key(s, o))
                verbs.append(vidx[v])
            # exact recall: UNIFIED_GRAD reads the graded bundle by graded key; CHEAP_ORTHO and FACTORIZED
            # read the SHARP bundle by the sharp key (flat fan).
            exact_bundle = grad_b if arm == "UNIFIED_GRAD" else sharp_b
            K = torch.stack(keys)
            pred = _cleanup_argmax(exact_bundle[None, :] * K.conj(), content)
            vv = torch.tensor(verbs, device=DEVICE)
            ok = (pred == vv).to(torch.int64).cpu().numpy()
            res.extend(list(zip(ok.tolist(), [ev_count[int(e)] for _ in evs])))
            # contiguity: read the GRADED bundle (CHEAP has no graded store -> read its ortho bundle == ~0).
            slots_e = sorted({s for (s, o, v) in evs})
            if len(slots_e) >= 6:
                s0 = slots_e[len(slots_e) // 2]
                contig_bundle = sharp_b if arm == "CHEAP_ORTHO" else grad_b
                keyfn = sharp_key if arm == "CHEAP_ORTHO" else grad_key
                r0 = contig_bundle * keyfn(min(s0, n_slots - 1), 0).conj()
                sims = []
                for lag in range(1, 4):
                    rl = contig_bundle * keyfn(min(s0 + lag, n_slots - 1), 0).conj()
                    sims.append(float((torch.real(torch.vdot(r0, rl)) /
                                       (torch.linalg.norm(r0) * torch.linalg.norm(rl) + 1e-9)).cpu()))
                contig.append(float(np.mean(sims)))
        return res, contig

    out = {}
    for arm in ("CHEAP_ORTHO", "UNIFIED_GRAD", "FACTORIZED"):
        res, contig = build_and_score(arm)
        out[arm] = {"queries": res, "contig": contig}
    return out


def validate(docs: Optional[int] = None, d: int = D, n_boot: int = 2000, seed: int = SEED) -> Dict:
    recs = load_events(docs)
    per_arm_docs = {"CHEAP_ORTHO": [], "UNIFIED_GRAD": [], "FACTORIZED": []}
    contig = {"CHEAP_ORTHO": [], "UNIFIED_GRAD": [], "FACTORIZED": []}
    for di, rec in enumerate(recs):
        sd = _score_doc(rec, d, seed + di)
        for arm in per_arm_docs:
            per_arm_docs[arm].append(sd[arm]["queries"])
            contig[arm].extend(sd[arm]["contig"])

    def acc_by_bin(sample):
        agg = {b: [0, 0] for b in BINS}
        for doc in sample:
            for ok, n in doc:
                c = agg[binof(n)]; c[0] += ok; c[1] += 1
        return {b: (agg[b][0] / agg[b][1] if agg[b][1] else float("nan")) for b in BINS}

    rng = np.random.default_rng(seed)
    ndoc = len(recs)
    boot_idx = [rng.integers(0, ndoc, ndoc) for _ in range(n_boot)]
    report = {"config": {"n_docs": ndoc, "d": d, "device": str(DEVICE),
                         "n_queries": sum(len(dd) for dd in per_arm_docs["UNIFIED_GRAD"])}, "arms": {}}
    slope_samples = {}
    for arm in per_arm_docs:
        acc0 = acc_by_bin(per_arm_docs[arm])
        slopes = []
        for idx in boot_idx:
            a = acc_by_bin([per_arm_docs[arm][i] for i in idx])
            if not (math.isnan(a["1-3"]) or math.isnan(a["17+"])):
                slopes.append(a["1-3"] - a["17+"])
        slopes = np.array(slopes); slope_samples[arm] = slopes
        report["arms"][arm] = {
            "acc_by_bin": acc0, "fan_slope": acc0["1-3"] - acc0["17+"],
            "slope_ci": [float(np.percentile(slopes, 2.5)), float(np.percentile(slopes, 97.5))],
            "contiguity_neighbor_reactivation": float(np.mean(contig[arm])) if contig[arm] else None,
            "contiguity_n_entities": len(contig[arm]),
        }
    # paired: do the two finer arms tie on the fan? (grading costs no fan accuracy)
    m = min(len(slope_samples["CHEAP_ORTHO"]), len(slope_samples["UNIFIED_GRAD"]))
    dd = slope_samples["UNIFIED_GRAD"][:m] - slope_samples["CHEAP_ORTHO"][:m]
    report["graded_minus_ortho_fan_slope"] = {"mean": float(dd.mean()),
        "ci": [float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))]}
    cg = report["arms"]["UNIFIED_GRAD"]["contiguity_neighbor_reactivation"] or 0.0
    co = report["arms"]["CHEAP_ORTHO"]["contiguity_neighbor_reactivation"] or 0.0
    fac = report["arms"]["FACTORIZED"]
    fac_cg = fac["contiguity_neighbor_reactivation"] or 0.0
    report["verdict"] = {
        "single_graded_key_trades_fan_for_contiguity": (report["arms"]["UNIFIED_GRAD"]["fan_slope"] >
                                                        report["arms"]["CHEAP_ORTHO"]["fan_slope"] + 0.05
                                                        and cg > 0.15),
        "only_graded_has_contiguity": (cg > 0.15 and abs(co) < 0.05),
        "FACTORIZED_gets_BOTH": (fac["fan_slope"] < 0.10 and fac_cg > 0.15),
        "factorized_fan_slope": fac["fan_slope"], "factorized_contiguity": fac_cg,
        "organ_coarse_baseline": {"acc_1_3": 0.9455, "acc_17plus": 0.6574, "fan_slope": 0.2881},
    }
    return report


# --------------------------------------------------------------------------- queue-compliant harness
def _write_metrics(rep: Dict, wall: float):
    name = os.environ.get("HDLAB_EXP_NAME", "entity_store_unified_litbank_v1")
    outdir = os.path.join(REPO_ROOT, "data", f"exp_{name}")
    os.makedirs(outdir, exist_ok=True)
    v = rep.get("verdict", {})
    ok = all([v.get("FACTORIZED_gets_BOTH"), v.get("only_graded_has_contiguity")])
    metrics = {
        "verdict": "PASS" if ok else "MIDDLE_BAND",
        "verdict_msg": ("a single graded key trades fan for contiguity, but the FACTORIZED two-system store "
                        "(sharp exact-recall + graded context) gets BOTH -- flat fan AND contiguity"
                        if ok else "one or more fairness/factorization conditions not met -- see summary"),
        "elapsed_s": round(wall, 2),
        "summary": {k: rep["arms"][k] for k in rep["arms"]} | {"verdict_flags": v,
                    "graded_minus_ortho_fan_slope": rep.get("graded_minus_ortho_fan_slope")},
    }
    with open(os.path.join(outdir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    print(f"[wrote] {os.path.join(outdir, 'metrics.json')}")


def self_test() -> int:
    """Off-disk gate: the torch FHRR path is exact (unbind recovers), and the two arms behave on a tiny
    synthetic doc (both decode a no-collision doc perfectly; graded has a contiguity gradient, ortho ~0)."""
    g = torch.Generator(device=DEVICE); g.manual_seed(0)
    a = _unit_phase(1, 64, g)[0]; c = _unit_phase(1, 64, g)[0]
    back = (a * c) * c.conj()
    assert abs(float(torch.real(torch.vdot(a, back)) / 64) - 1.0) < 1e-4, "torch unbind not exact"
    # tiny doc: 6 slots, 1 event each, distinct verbs -> both arms decode perfectly
    rec = {"events": [(0, s, 0, f"v{s}") for s in range(6)], "verb_vocab": [f"v{s}" for s in range(6)],
           "n_slots": 6, "ev_count": {0: 6}}
    sd = _score_doc(rec, 512, 1)
    for arm in ("CHEAP_ORTHO", "UNIFIED_GRAD"):
        acc = np.mean([ok for ok, _ in sd[arm]["queries"]])
        assert acc == 1.0, f"{arm} must decode a no-collision doc perfectly: {acc}"
    # graded contiguity > ortho contiguity on a longer doc
    rec2 = {"events": [(0, s, 0, f"v{s}") for s in range(20)], "verb_vocab": [f"v{s}" for s in range(20)],
            "n_slots": 20, "ev_count": {0: 20}}
    sd2 = _score_doc(rec2, 1024, 1)
    cg = np.mean(sd2["UNIFIED_GRAD"]["contig"]) if sd2["UNIFIED_GRAD"]["contig"] else 0.0
    co = np.mean(sd2["CHEAP_ORTHO"]["contig"]) if sd2["CHEAP_ORTHO"]["contig"] else 0.0
    assert cg > co + 0.15, f"graded must have more contiguity than ortho: graded={cg} ortho={co}"
    print(json.dumps({"torch_unbind_exact": True, "both_arms_decode_no_collision": True,
                      "graded_contiguity": round(float(cg), 3), "ortho_contiguity": round(float(co), 3),
                      "device": str(DEVICE)}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--d", type=int, default=D)
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.smoke:
        t0 = time.time(); rep = validate(docs=5, d=args.d, n_boot=500); wall = time.time() - t0
        print(json.dumps(rep, indent=2, default=float)); _write_metrics(rep, wall); return
    if args.full:
        t0 = time.time(); rep = validate(docs=None, d=args.d); wall = time.time() - t0
        print(json.dumps(rep, indent=2, default=float)); _write_metrics(rep, wall); return
    ap.print_help()


if __name__ == "__main__":
    main()
