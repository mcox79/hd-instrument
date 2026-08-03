"""situation_model_multibank_capacity_v1 -- flat-bundle capacity wall vs multi-bank fix.

DIRECTOR TASK (2026-08-02): hdlab.situation_model_accumulate.AccumulateRegister stores an
entity's whole event history as ONE flat FHRR bundle of bind(role, event_idx) terms. This IS
the reported decode self-consistency regression 89.8% -> 67.2% on the Anne consolidation-
ledger scenes (atom 29629): too many events crammed into one register -> cross-talk. This
cell MEASURES that degradation directly (ONE variable: memory backend flat vs multi-bank,
per hdlab.situation_model_multibank.MultiBankAccumulateRegister) as events-per-entity scales,
and checks whether multi-bank HOLDS decode self-consistency high where flat degrades.

CAN-FAIL: the flat-bundle arm MUST degrade as events/entity rises (this is not assumed --
regime below is chosen so the degradation is empirically observed, see PROTOTYPE SWEEP note).
The multi-bank arm (n_banks in {4, 8, 16}) should hold decode self-consistency high at the
SAME event load if the capacity fix is real.

PROTOTYPE SWEEP (foreground, not banked as an atom -- informs the regime choice below):
  d=512, n_events=256, 5 seeds: flat=0.655, multibank(n_banks=8)=0.999, multibank(n_banks=16)=1.000
  d=512, n_events=128: flat=0.839, multibank(n_banks=8)=1.000
  d=256, n_events=256: flat=0.487, multibank(n_banks=8)=0.973
This is a FIXTURE-SCALE d (512), not the production situation-model d -- chosen only to make
the capacity wall reachable in a foreground run of seconds rather than needing production-scale
d and thousands of events. The MECHANISM (superposition cross-talk vs bundle load) is dtype/
d-invariant; the specific crossover point (which n_events at which d) is d-dependent, and is
reported per-point below rather than assumed.

REGIME-DISCRIMINATING-REGIME HONESTY (per hdlab.working_memory docstring): that module's
BSC-bipolar chain-grade guarantee (recall>=0.95) is anchored ONLY at k_per_bank>=64, N_DIM=8192,
FEATURE_OVERLAP_FRAC<=0.20. This cell's mechanism is FHRR complex64 bind/bundle/cleanup-argmax,
a DIFFERENT primitive family running at d=512 (below the BSC anchor's N_DIM=8192), so
assert_k_per_bank_in_discriminating_regime() is called for scope-declaration compliance but
is EXPECTED to no-op (its guard condition requires n_dim>=8192) -- it does NOT certify this
cell's regime as chain-grade. The regime-honesty evidence for THIS cell is the empirical
flat-vs-multibank gap measured in-cell, reported per event-count point, not a borrowed
threshold from a different mechanism family. Verdict is tiered MEASURED_MECHANISM (capacity-
headroom result), not chain-grade, unless a future dedicated FHRR chain-grade cell ratifies it.

ANNE CONSOLIDATION-LEDGER RE-RUN (task item 3): searched repo (notes/*.md, experiments/*.py)
for "Anne", "consolidation_ledger", "ch6"/"ch9"/"ch16" -- NO MATCHES FOUND. The referenced
scenario/dataset is not present in this checkout, so it is NOT re-run here (honest NOT_FOUND,
not fabricated). See completion report for the exact search performed.

SMOKE: SMOKE and FULL are IDENTICAL config here -- the whole cell is a single foreground
measurement (no remote dispatch; Director instructed "Do NOT dispatch anything"), wall time
is seconds, so there is no smaller/faster smoke regime to define. --self-test asserts the
CAN-FAIL fixture (flat degrades, multibank holds) at fixed seed=0 BEFORE the full sweep runs.

Author: exp_dev 2026-08-02. ASCII-only; local-only run (no queue_add); deterministic (seeded
torch.Generator per arm/seed); atomic metrics write via experiments._seed_checkpoint.write_metrics.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics
from hdlab.situation_model_accumulate import AccumulateRegister
from hdlab.situation_model_multibank import (
    MultiBankAccumulateRegister,
    assert_k_per_bank_in_discriminating_regime,
)

ANCHOR_NAME = "situation_model_multibank_capacity_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

ROLE_VOCAB = ["agent", "patient", "theme", "instrument", "location",
              "recipient", "experiencer", "goal"]

# Regime (single regime; see module docstring PROTOTYPE SWEEP for why these values discriminate)
D_DIM = 512
N_EVENTS_SWEEP = [64, 96, 128, 192, 256]
SEEDS = [0, 1, 2, 3, 4]
N_BANKS_ARMS = [4, 8, 16]

# Bands (MEASURED_MECHANISM tier, not chain-grade -- see REGIME-DISCRIMINATING-REGIME HONESTY)
HP_FLAT_MUST_DEGRADE_BELOW = 0.85   # flat arm mean decode self-consistency at max n_events
HP_MULTIBANK_MUST_HOLD_ABOVE = 0.95  # best multibank arm mean decode self-consistency at max n_events
CRLB_N_A = (
    "no closed-form CRLB used; discriminator is an empirical flat-vs-multibank gap at fixed "
    "(d, n_events, seed) -- see REGIME-DISCRIMINATING-REGIME HONESTY docstring section"
)

CONFIG_VERSION = (
    "situationModelMultibankCapacity-v1: D_DIM=%d N_EVENTS_SWEEP=%s SEEDS=%s "
    "N_BANKS_ARMS=%s HP_flat_degrade_below=%.2f HP_multibank_hold_above=%.2f"
) % (D_DIM, N_EVENTS_SWEEP, SEEDS, N_BANKS_ARMS,
     HP_FLAT_MUST_DEGRADE_BELOW, HP_MULTIBANK_MUST_HOLD_ABOVE)


def _arms_must_differ(arms_outputs: Dict[str, torch.Tensor]) -> Dict[str, str]:
    """META_RULE_AF hash-test: catches bit-identical arm bugs."""
    digests = {}
    for name, out in arms_outputs.items():
        b = out.detach().cpu().numpy().tobytes() if hasattr(out, "detach") else bytes(out)
        digests[name] = hashlib.sha256(b).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b_ = names[i], names[j]
            assert digests[a] != digests[b_], (
                f"META_RULE_AF VIOLATION: arms {a!r} and {b_!r} bit-identical")
    return digests


def run_one_trial(d: int, n_events: int, seed: int, n_banks: int) -> Dict[str, float]:
    """One (d, n_events, seed) trial: build ground-truth role assignment, run flat + all
    multibank arms against it (SAME seed -> identical role_vecs/idx_vecs per arm, isolating
    the routing/bundling difference), return per-arm decode self-consistency.
    """
    gt_rng = torch.Generator().manual_seed(seed + 999)
    gt_roles: List[str] = []
    for _ in range(n_events):
        gt_roles.append(ROLE_VOCAB[int(torch.randint(0, len(ROLE_VOCAB), (1,), generator=gt_rng).item())])

    def score(reg_cls, **kw) -> float:
        gen = torch.Generator().manual_seed(seed)
        reg = reg_cls(ROLE_VOCAB, d, gen, max_event_slots=n_events, **kw)
        for idx, role in enumerate(gt_roles):
            reg.add_event("E", role, idx)
        correct = 0
        for idx, role in enumerate(gt_roles):
            pred, _ = reg.decode("E", idx)
            if pred == role:
                correct += 1
        return correct / n_events

    out = {"flat": score(AccumulateRegister)}
    for nb in N_BANKS_ARMS:
        out["multibank_%d" % nb] = score(MultiBankAccumulateRegister, n_banks=nb)
    return out


def _selftest() -> None:
    """CAN-FAIL fixture: at (d=512, n_events=256, seed=0) flat MUST degrade below
    HP_FLAT_MUST_DEGRADE_BELOW and multibank(n_banks=8) MUST hold above
    HP_MULTIBANK_MUST_HOLD_ABOVE. Deterministic (fixed seed).
    """
    d, n_events, seed = 512, 256, 0
    res = run_one_trial(d, n_events, seed, n_banks=8)
    print("[selftest] fixture (d=%d n_events=%d seed=%d): %s" % (d, n_events, seed, res))
    assert res["flat"] < HP_FLAT_MUST_DEGRADE_BELOW, (
        "T1 FAIL: flat register did NOT degrade at high event count "
        "(flat=%.3f, expected < %.2f) -- CAN-FAIL discriminator did not fire" % (
            res["flat"], HP_FLAT_MUST_DEGRADE_BELOW))
    print("[selftest] T1 PASS: flat degraded (%.3f < %.2f)" % (res["flat"], HP_FLAT_MUST_DEGRADE_BELOW))
    assert res["multibank_8"] >= HP_MULTIBANK_MUST_HOLD_ABOVE, (
        "T2 FAIL: multibank(n_banks=8) did NOT hold decode self-consistency "
        "(multibank_8=%.3f, expected >= %.2f)" % (res["multibank_8"], HP_MULTIBANK_MUST_HOLD_ABOVE))
    print("[selftest] T2 PASS: multibank_8 held (%.3f >= %.2f)" % (
        res["multibank_8"], HP_MULTIBANK_MUST_HOLD_ABOVE))

    # T3: arms-must-differ (flat vs multibank actually produce different register tensors)
    gen1 = torch.Generator().manual_seed(seed)
    flat_reg = AccumulateRegister(ROLE_VOCAB, d, gen1, max_event_slots=n_events)
    gen2 = torch.Generator().manual_seed(seed)
    multi_reg = MultiBankAccumulateRegister(ROLE_VOCAB, d, gen2, max_event_slots=n_events, n_banks=8)
    for idx in range(8):
        flat_reg.add_event("E", ROLE_VOCAB[idx % len(ROLE_VOCAB)], idx)
        multi_reg.add_event("E", ROLE_VOCAB[idx % len(ROLE_VOCAB)], idx)
    _arms_must_differ({"flat": flat_reg.register("E"), "multibank": multi_reg._bank_register(
        "E", multi_reg.bank_loads("E").__iter__().__next__())})
    print("[selftest] T3 PASS: flat and multibank arms produce distinct register tensors")

    # T4: assert_k_per_bank_in_discriminating_regime is callable and behaves as documented
    # (no-op below N_DIM=8192; do not treat its silence as chain-grade certification here)
    try:
        assert_k_per_bank_in_discriminating_regime(
            k_total=n_events, n_banks=8, feature_overlap_frac=0.20, n_dim=d)
        regime_flag = "no_op_below_n_dim_8192_anchor (d=%d < 8192)" % d
    except ValueError as e:
        regime_flag = "raised: %s" % str(e)[:200]
    print("[selftest] T4 PASS: regime-check callable, result=%s" % regime_flag)

    # T5: bands locked
    assert 0.0 < HP_FLAT_MUST_DEGRADE_BELOW < 1.0
    assert 0.0 < HP_MULTIBANK_MUST_HOLD_ABOVE <= 1.0
    assert HP_MULTIBANK_MUST_HOLD_ABOVE > HP_FLAT_MUST_DEGRADE_BELOW
    print("[selftest] T5 PASS: bands locked")

    print("[selftest] ALL PASS")


try:
    _selftest()
except Exception as e:
    print("[selftest] FAILED: %s\n%s" % (e, traceback.format_exc()), flush=True)
    raise

if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def compute_verdict(units: List[Dict]) -> tuple:
    """units: one dict per (n_events, seed) with per-arm scores. Aggregate by n_events."""
    by_n = {}
    for u in units:
        by_n.setdefault(u["n_events"], []).append(u)

    per_n_summary = {}
    for n_events in sorted(by_n.keys()):
        us = by_n[n_events]
        arm_names = ["flat"] + ["multibank_%d" % nb for nb in N_BANKS_ARMS]
        row = {}
        for arm in arm_names:
            vals = [u["scores"][arm] for u in us]
            row[arm] = round(sum(vals) / len(vals), 4)
        per_n_summary[n_events] = row

    max_n = max(per_n_summary.keys())
    flat_at_max = per_n_summary[max_n]["flat"]
    best_multibank_at_max = max(per_n_summary[max_n]["multibank_%d" % nb] for nb in N_BANKS_ARMS)
    best_multibank_label = max(
        N_BANKS_ARMS, key=lambda nb: per_n_summary[max_n]["multibank_%d" % nb])

    summ = " | ".join(
        "n_events=%d %s" % (n, {k: v for k, v in row.items()})
        for n, row in per_n_summary.items()
    )

    flat_degrades = flat_at_max < HP_FLAT_MUST_DEGRADE_BELOW
    multibank_holds = best_multibank_at_max >= HP_MULTIBANK_MUST_HOLD_ABOVE

    if not flat_degrades:
        return ("HARD_FAIL",
                "HARD_FAIL_NO_DISCRIMINATOR: flat register did NOT degrade at n_events=%d "
                "(flat=%.4f, expected < %.2f) -- regime too easy, CAN-FAIL gate did not fire | %s" % (
                    max_n, flat_at_max, HP_FLAT_MUST_DEGRADE_BELOW, summ))

    if flat_degrades and multibank_holds:
        return ("MEASURED_MECHANISM",
                "CAPACITY_FIXED_MEASURED_MECHANISM: flat degrades to %.4f at n_events=%d "
                "(below %.2f) while multibank(n_banks=%d) holds %.4f (above %.2f). "
                "NOT chain-grade (see REGIME-DISCRIMINATING-REGIME HONESTY; d=%d below "
                "the BSC-anchor N_DIM=8192) -- capacity-headroom result, empirically fair "
                "one-variable (memory backend) test. | %s" % (
                    flat_at_max, max_n, HP_FLAT_MUST_DEGRADE_BELOW, best_multibank_label,
                    best_multibank_at_max, HP_MULTIBANK_MUST_HOLD_ABOVE, D_DIM, summ))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL: flat degrades to %.4f (below %.2f) but best multibank "
            "(n_banks=%d) only reaches %.4f (below hold-threshold %.2f) -- multibank helps "
            "(gap=%.4f) but does not fully recover | %s" % (
                flat_at_max, HP_FLAT_MUST_DEGRADE_BELOW, best_multibank_label,
                best_multibank_at_max, HP_MULTIBANK_MUST_HOLD_ABOVE,
                best_multibank_at_max - flat_at_max, summ))


if __name__ == "__main__":
    t0 = time.time()
    print("[config] anchor=%s | %s" % (ANCHOR_NAME, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    units = []
    try:
        for n_events in N_EVENTS_SWEEP:
            for seed in SEEDS:
                scores = run_one_trial(D_DIM, n_events, seed, n_banks=8)  # n_banks arg unused inside (loops N_BANKS_ARMS)
                unit = {"n_events": n_events, "seed": seed, "scores": scores, "d": D_DIM}
                units.append(unit)
                print("  [n_events=%d seed=%d] %s" % (n_events, seed, scores), flush=True)
    except Exception as e:
        print("[FATAL] sweep failed: %s\n%s" % (e, traceback.format_exc()), flush=True)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:500]),
            "summary": "CELL_CRASHED during sweep", "elapsed_s": round(time.time() - t0, 1),
            "run_mode": "full", "config_version": CONFIG_VERSION,
        }
        write_metrics(out_dir, metrics, results=units)
        raise

    v, vmsg = compute_verdict(units)
    print("\n[VERDICT] " + vmsg, flush=True)

    # Per-n_events summary table for the report
    by_n = {}
    for u in units:
        by_n.setdefault(u["n_events"], []).append(u)
    summary_table = {}
    for n_events in sorted(by_n.keys()):
        us = by_n[n_events]
        arm_names = ["flat"] + ["multibank_%d" % nb for nb in N_BANKS_ARMS]
        summary_table[str(n_events)] = {
            arm: round(sum(u["scores"][arm] for u in us) / len(us), 4) for arm in arm_names
        }

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": "full", "n_units": len(units),
        "config_version": CONFIG_VERSION, "per_unit": units,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": vmsg,
        "D_DIM": D_DIM, "N_EVENTS_SWEEP": N_EVENTS_SWEEP, "SEEDS": SEEDS,
        "N_BANKS_ARMS": N_BANKS_ARMS, "summary_table_by_n_events": summary_table,
        "crlb_n_a": CRLB_N_A,
        "anne_ledger_rerun": "NOT_FOUND: no 'Anne'/'consolidation_ledger'/ch6-9-16 match in repo; skipped honestly",
        "DESIGN_NOTE": (
            "Fair one-variable test (memory backend: flat AccumulateRegister vs "
            "MultiBankAccumulateRegister) at matched (d, n_events, seed, role_vocab). "
            "See module docstring REGIME-DISCRIMINATING-REGIME HONESTY for why this is tiered "
            "MEASURED_MECHANISM (capacity-headroom) not chain-grade."
        ),
    }
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (len(units), metrics["elapsed_s"]), flush=True)
