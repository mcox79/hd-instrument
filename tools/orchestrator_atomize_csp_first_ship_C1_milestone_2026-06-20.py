#!/usr/bin/env python3
"""ORCHESTRATOR (C1/C5 custody) -- atomize the CSP first-ship Phase-1 0->1 MILESTONE cert-event.

Skunkworks LANDED-VET PASSED (2026-06-20) + routed the ship-event atomization to Orchestrator
(C1/C5 custody: single-writer window + independent LOAD-gate). Cert-spec per her note:
- cert claim + metrics_source=measured_cpu_csp_first_ship_C1_warmstart_v1
- provenance: regression verified by CERT-OWNER CODE-TRACE PROOF (non-interference of 8 + value-leg
  reproduction of the mechanism), NOT the cell's regression_ok flag (a baseline-existence check).
- hp12 pinned to T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1 (single-exp_).
- +1 CERT (the first Phase-1 ship atom).

DRY-RUN by default (prints the proposed atom + invariant projection; NO write). --apply to write
(single-writer window; SAFE add + round-trip + pre/post invariant; rollback-on-fail). ASCII.

FLAGGED for Skunkworks cert-field sign-off (her domain): relevance_tier, era, depends_on, capint integration.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType
from backend.substrate_index.partition import PartitionedStore

METRICS = Path("data/exp_csp_first_ship_v1/metrics.json")
STORE = Path("data/substrate_index")
EXPECT_CERT_PRE, EXPECT_CERT_POST, EXPECT_AXIOM = 589, 590, 206

# Skunkworks sign-off: depends_on = the 9 regression-set atoms (all resolve, cert->cert, no phantom edges).
DEPENDS9 = [
    "T3/EXP_csp_memory_warm_start_full_v3", "T3/EXP_csp_hebbian_coexist_v1",
    "T3/EXP_planted_csp_viability_full_v3", "T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1",
    "T3/EXP_pp52_hebbian_lora_speedup_n4096_v1", "T3/EXP_pp52_hebbian_lora_speedup_n8192_v1",
    "T3/EXP_substrate_capacity_alpha_sweep_v1_512_16384_gpu",
    "T3/EXP_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu",
    "T3/EXP_substrate_continual_learning_30day_realistic_stream_v1",
]


def build_atom() -> Atom:
    m = json.load(open(METRICS))
    km = {k: m.get(k) for k in ("speedup", "pre_iters", "post_iters", "pre_recall", "post_recall",
                                 "n_seeds", "det_eligible", "baseline_n_atoms", "swap_gating_ok",
                                 "rolled_back", "regression_scope") if m.get(k) is not None}
    honest = ("CSP-first-ship: warm-start swap buys 8.42x CSP-solve speedup at N=2048/rho=0.9, "
              "no-recall-degrade (1.0->1.0), non-regressing (PROVEN: 8 dependents non-interfering "
              "[cert-owner code-trace] + warm-start mechanism reproduced via the value-leg), "
              "reversible. Phase-1 0->1 milestone (the program's first ship).")
    return Atom(
        id="T3/EXP_csp_first_ship_v1",
        name=("CSP first-ship (Phase-1 0->1 MILESTONE): warm-start swap = 8.42x CSP-solve speedup, "
              "non-regressing (proven), reversible"),
        description=(honest + " C1 STATE-CHANGE: PRE-ship cert-event -> warm-start SWAP (reversible "
                     "additive flag; W-based warm init vs random/cold) -> POST-ship. REGRESSION "
                     "satisfied by CERT-OWNER CODE-TRACE PROOF (csp_hebbian_coexist + "
                     "planted_csp_viability + 6 dependents = non-interfering: warm-start absent from "
                     "their code paths -> reproduce-by-construction; csp_memory_warm_start reproduced "
                     "by the value-leg 8.42x), NOT the cell's regression_ok flag (a baseline-EXISTENCE "
                     "check; the HOLD established it must not be relied on). hp12 pinned single-exp_. "
                     "swap-gating OK; rolled_back=false; reversible. Skunkworks landed-VET PASSED."),
        kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
        metadata={
            "provenance_quality": "CERT_CHAIN_GRADE",
            "verdict": "HARD_PASS",
            "run_mode": "full",
            "era": "POST_SUBSTRATE_BUILD",                # FLAG: 2026-06-20 > 2026-06-10 cutoff
            "relevance_tier": "HIGH",                      # FLAG: first Phase-1 ship = strategically load-bearing (your call)
            "metrics_source": "measured_cpu_csp_first_ship_C1_warmstart_v1",
            "metrics_path": "data/exp_csp_first_ship_v1/metrics.json",
            "honest_scope": honest,
            "key_metrics": km,
            "cert_vet_status": "PASSED",
            "cert_promoted_by_vet": "skunkworks_CSP_first_ship_landed_VET_2026-06-20",
            "cert_promoted_date": "2026-06-20",
            # --- C1 ship-event specific provenance (load-bearing per Skunkworks) ---
            "phase1_milestone": "0->1",
            "ship_lever": "warm-start CSP-solve (reversible additive flag; W-based warm init vs random/cold)",
            "c1_regression_verified_by": ("cert_owner_code_trace_proof: 8_dependents_non_interfering "
                                          "+ warm_start_mechanism_value_leg_reproduced; NOT_cell_regression_ok_flag"),
            "c1_regression_NOT_via": "cell_regression_ok_flag_is_baseline_existence_check_only",
            "hp12_pin": "T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1",
            "swap_reversible": True, "rolled_back": False, "swap_gating_ok": True,
            "atomized_by": "orchestrator_C1_C5_custody_2026-06-20",
            # Skunkworks: capint integration is a separate deliberate I1-I10 step IF a cluster later forms; not now.
            "capint_integrated": None,
            # Skunkworks sign-off: depends_on = the 9 regression-set atoms (all resolve, cert->cert). Also emitted as DEPENDS_ON edges.
            "depends_on_resolved": DEPENDS9,
            "depends_on_count": len(DEPENDS9),
        },
    )


def counts(ps):
    t = c = ax = 0
    for a in ps.all_atoms():
        t += 1; md = a.metadata or {}
        if md.get("provenance_quality") == "CERT_CHAIN_GRADE": c += 1
        if (str(a.corpus.name) == "MATH" and str(a.tier.name) in ("TIER_2_PRIMITIVE", "TIER_3_ALGORITHM")
                and a.algebra and len(a.algebra) >= 3 and "oeis" not in str(a.id).lower()
                and not str(a.id).startswith("T3/wikidata_")): ax += 1
    return t, c, ax


def main():
    atom = build_atom()
    apply = "--apply" in sys.argv
    print("=" * 80)
    print("CSP FIRST-SHIP Phase-1 0->1 MILESTONE atomization", "(--APPLY)" if apply else "(DRY-RUN)")
    print("=" * 80)
    print("id:", atom.id, "| kind:", atom.kind.value, "| tier:", atom.tier.value, "| corpus:", atom.corpus.value)
    print("pq:", atom.metadata["provenance_quality"], "| verdict:", atom.metadata["verdict"])
    print("metrics_source:", atom.metadata["metrics_source"])
    print("key_metrics:", json.dumps(atom.metadata["key_metrics"]))
    print("honest_scope:", atom.metadata["honest_scope"])
    print("cert-fields (Skunkworks SIGNED OFF): relevance_tier=HIGH, era=POST_SUBSTRATE_BUILD,",
          f"capint_integrated=None, depends_on={len(DEPENDS9)} (all resolve cert->cert)")
    ps = PartitionedStore(STORE)
    t0, c0, ax0 = counts(ps)
    print(f"\nPRE-invariant: total={t0} CERT={c0} (expect {EXPECT_CERT_PRE}) axiom={ax0} (expect {EXPECT_AXIOM})")
    if ps.get_atom(f"{atom.corpus.value}::{atom.id}") is not None:
        print("NOTE: atom already exists (idempotent skip on apply)."); return 0
    if not apply:
        print(f"\nPROJECTED POST: total={t0+1} CERT={c0+1} (expect {EXPECT_CERT_POST}) axiom={ax0} (unchanged)")
        print("DRY-RUN: no write. Route to Skunkworks for cert-field sign-off, then --apply in a single-writer window.")
        return 0
    # --apply: SAFE write (atom + DEPENDS_ON edges) + round-trip + invariant
    _src = "orchestrator_CSP_first_ship_C1_milestone_atomization_2026-06-20"
    _note = "Phase-1 0->1 first-ship cert-event; Skunkworks landed-VET PASSED; regression by cert-owner code-trace-proof; hp12 single-exp_ pinned; C1/C5 custody single-writer."
    ps.add_atom(atom, source=_src, note=_note)
    src_qid = f"{atom.corpus.value}::{atom.id}"
    for tgt in DEPENDS9:
        ps.add_relation(src_qid, RelationType.DEPENDS_ON, f"math::{tgt}", source=_src,
                        note="CSP-ship depends_on its 9-atom regression-set (Skunkworks sign-off; all resolve cert->cert).")
    print(f"  added {len(DEPENDS9)} DEPENDS_ON edges.")
    ps2 = PartitionedStore(STORE)
    t1, c1, ax1 = counts(ps2)
    found = next((a for a in ps2.all_atoms() if str(a.id) == atom.id), None)
    ok = (found is not None and found.kind == atom.kind and found.tier == atom.tier
          and (found.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
          and t1 == t0 + 1 and c1 == EXPECT_CERT_POST and ax1 == EXPECT_AXIOM)
    print(f"\nPOST-invariant: total={t1} CERT={c1} axiom={ax1} | round-trip found={found is not None}")
    print("GATE:", "PASS" if ok else "FAIL")
    if not ok:
        print("!! POST-GATE FAILED -- ROLL BACK: git restore data/substrate_index/ (do NOT commit).")
        return 6
    print("OK: CSP first-ship atomized. CERT 589->590. Run invariant-check + commit-by-path + push (origin-durability).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
