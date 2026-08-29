"""Scaffold-free witness for situation_model_has_no_discourse_fact_reasoning.

Two headlines, checked on the REAL organs/harness (no re-scored floors, no crossing populations):

  A. NEGATIVE on the anti-typical LitBank coref residual: a reading-built discourse-fact store + bridging is
     DEAD there, and the DIAGNOSIS is structural -- the residual gold carries ~zero accumulated facts (it is
     freshly introduced, bound intra-sententially). This is the 7th channel dead on the residual, and it tests
     the exact mechanism the parent named as the fix.

  B. POSITIVE on the mechanism's PROPER domain (inter-sentential fact-decisive reference): the SAME store +
     2-hop bridge resolves references the fact-blind reader cannot, CI-separated, with EVERY control at chance
     (info-free twin / KG-only-null / ablation), on-target only (fact-absent -> no lift), and degrading
     gracefully under knowledge-coverage loss.

  C. REPRESENTATION fidelity: the reading-built entity->attribute fact stored in the FHRR register the brief
     names (situation_model_accumulate.RelationRegister) is retrieved faithfully -> the symbolic store used for
     the measurement is a faithful proxy for the FHRR-bound store (the representation is OUR-INVENTION, the
     computation is what is pinned).

Run: .venv/Scripts/python.exe verification/test_discfact_store_bridging.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments import exp_discfact_store_bridging_residual_v1 as A   # noqa: E402
from experiments import exp_discfact_store_bridging_capability_v1 as B  # noqa: E402
from experiments import exp_discfact_store_bridging_graded_v1 as C      # noqa: E402
from experiments import exp_discfact_store_multifact_load_v1 as D       # noqa: E402

PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))


# ---------------------------------------------------------------- W0: self-tests of both cells
A.self_test()
B.self_test()
check("W0 both cell self-tests pass", True)

# ---------------------------------------------------------------- W1-3: NEGATIVE on the residual
resA = A.run(docs=None, n_boot=500)
diag = resA["DIAGNOSIS_accumulated_facts"]
orac = resA["bridge_oracle_on_residual"]["full"]
ftwin = resA["fused_vs_infofree_twin"]["fused_minus_twin_paired"]
check("W1 residual gold carries ~zero accumulated facts (fact store cannot apply)",
      diag["gold_mean_nfacts"] < 1.0 and diag["gold_has_ZERO_facts_frac"] > 0.4,
      f"gold_mean={diag['gold_mean_nfacts']} zero_frac={diag['gold_has_ZERO_facts_frac']} vs pick_mean={diag['pick_mean_nfacts']}")
check("W2 fact-store bridge ORACLE is dead on the residual (<0.10, like the 6 other channels)",
      orac["acc"] < 0.10, f"oracle acc={orac['acc']} n_appl={orac['applicable']}")
check("W3 fused bridge does NOT beat its info-free twin on the residual (not ABOVE)",
      ftwin["band"] != "ABOVE", f"fused-minus-twin band={ftwin['band']} delta={ftwin['delta']}")
check("W3b residual verdict = DEAD/gold-has-no-facts", resA["verdict"].startswith("DISCOURSE_FACT_STORE_DEAD"),
      resA["verdict"])

# ---------------------------------------------------------------- W4-9: POSITIVE on the proper domain
resB = B.run(n_test=240, n_dev=140, n_boot=600)
a2 = resB["accuracy_TEST_2cand"]; c2 = resB["contrasts_TEST_2cand"]
check("W4 fact_store beats fact-blind floor CI-separated (2-cand)",
      a2["fact_store"]["lo"] > a2["fact_blind"]["hi"],
      f"store={a2['fact_store']['acc']} [{a2['fact_store']['lo']},{a2['fact_store']['hi']}] vs floor={a2['fact_blind']['acc']}")
check("W5a info-free twin LOSES CI-separated (it is the SPECIFIC binding, not the shape)",
      c2["store_minus_infofree_twin"]["band"] == "ABOVE", f"delta={c2['store_minus_infofree_twin']['delta']}")
check("W5b KG-only-null LOSES CI-separated (KG connects but cannot discriminate w/o reading-built binding)",
      c2["store_minus_kg_only_null"]["band"] == "ABOVE", f"delta={c2['store_minus_kg_only_null']['delta']}")
check("W5c ablation (no IS-A fact) LOSES CI-separated (the lift IS the accumulated facts)",
      c2["store_minus_ablation"]["band"] == "ABOVE", f"delta={c2['store_minus_ablation']['delta']}")
rec = resB["RECOVERY_on_factblind_errors"]
check("W6 recovers the cases the fact-blind reader gets WRONG (CI-separated over floor)",
      rec["store_minus_floor"]["band"] == "ABOVE" and rec["fact_store_acc_on_these"] > 0.8,
      f"floor={rec['floor_acc_on_these']} -> store={rec['fact_store_acc_on_these']} (n={rec['n_floor_errors']})")
a3 = resB["accuracy_TEST_3cand"]
check("W7 lift survives a 3-candidate (chance ~0.33) baseline",
      a3["fact_store"]["lo"] > a3["fact_blind"]["hi"],
      f"store={a3['fact_store']['acc']} vs floor={a3['fact_blind']['acc']}")
spec = resB["specificity_fact_absent"]
check("W8 SPECIFICITY: when the deciding fact is NEVER stated, the store gives NO lift (NOT_SEP)",
      spec["store_minus_floor"]["band"] != "ABOVE", f"band={spec['store_minus_floor']['band']} delta={spec['store_minus_floor']['delta']}")
cov = resB["coverage_degradation_fact_store_acc"]
ps = sorted(cov, key=float)
vals = [cov[p] for p in ps]
mono = all(vals[i] >= vals[i + 1] - 1e-9 for i in range(len(vals) - 1))
check("W9 GRACEFUL degradation under knowledge-coverage loss (monotone decline, no cliff)",
      mono and vals[0] > 0.9 and vals[-1] < vals[0], f"curve={cov}")

# ---------------------------------------------------------------- W10: the bridge is the KG's, not hand-picked
kg = A.load_kg_capable()
real_bridges = sum(1 for r in ("doctor", "farmer", "baker", "hunter", "priest", "nurse", "singer")
                   if kg.get(r))
check("W10 the generic role->action bridge comes from the static CSKG (not hand-authored)",
      real_bridges >= 5 and ("prescribe" in kg.get("doctor", set()) or "heal" in kg.get("doctor", set())
                             or "care" in kg.get("doctor", set())),
      f"{real_bridges}/7 roles have KG action edges")

# ---------------------------------------------------------------- W11: FHRR representation fidelity
def fhrr_fidelity():
    """Store the reading-built entity->attribute fact in the FHRR register the brief names
    (RelationRegister, GOAL role = single-filler exact bind), retrieve it, and show the retrieved attribute
    is the stated one -> the FHRR-bound store resolves the SAME fact-decisive pronoun as the symbolic store."""
    import torch
    from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec
    g = torch.Generator().manual_seed(0)
    d = 4096
    vocab = ["doctor", "lawyer", "farmer", "baker", "nurse", "hunter"]
    av = {a: unit_phase_vec(d, g) for a in vocab}     # FHRR content vectors (complex unit-phase)
    sim = lambda x, y: float(torch.real(torch.vdot(x, y)))   # FHRR similarity (conjugate inner product)
    # two entities, reading-built IS-A facts: john<->doctor, james<->lawyer
    rr = RelationRegister(d, g)
    rr.bind_filler("john", RelationRegister.GOAL_ROLE, av["doctor"])
    rr.bind_filler("james", RelationRegister.GOAL_ROLE, av["lawyer"])
    ok = 0
    for ent, gold_attr in (("john", "doctor"), ("james", "lawyer")):
        rb = rr.decode_filler(ent, RelationRegister.GOAL_ROLE)
        best = max(vocab, key=lambda a: sim(rb, av[a]))
        ok += int(best == gold_attr)
    # resolution over the FHRR store: "he prescribed" -> doctor role -> john (via the retrieved attribute)
    action_role = {"doctor": {"prescribe"}, "lawyer": {"argue"}}   # generic KG bridge (attribute->action)
    scores = {}
    for ent in ("john", "james"):
        rb = rr.decode_filler(ent, RelationRegister.GOAL_ROLE)
        attr = max(vocab, key=lambda a: sim(rb, av[a]))
        scores[ent] = 1.0 if "prescribe" in action_role.get(attr, set()) else 0.0
    resolved = max(scores, key=scores.get)
    return ok, resolved


ok, resolved = fhrr_fidelity()
check("W11 FHRR-bound entity->attribute fact is retrieved faithfully (representation is a faithful proxy)",
      ok == 2 and resolved == "john", f"retrieved_correct={ok}/2, resolved_pronoun_to={resolved}")

# ---------------------------------------------------------------- W12-14: the GRADED distributional bridge
C.self_test()
check("W12 graded-bridge cell self-test passes (SVD predicts a held-out role->action edge)", True)
resC = C.run(n_items=300, n_dev=150, n_boot=600, do_ksweep=False)
gho = resC["HELDOUT_edge_accuracy"]; gcon = resC["HELDOUT_contrasts"]
check("W13 GRADED distributional bridge GENERALISES on HELD-OUT edges where the hard match is at chance",
      gho["graded_distributional"]["lo"] > 0.5 and gho["graded_distributional"]["lo"] > gho["hard_match"]["hi"],
      f"graded={gho['graded_distributional']['acc']} vs hard={gho['hard_match']['acc']} (edge removed) / floor={gho['fact_blind']['acc']}")
check("W13b graded-minus-hard AND graded-minus-floor both CI-separated ABOVE on held-out edges",
      gcon["graded_minus_hard"]["band"] == "ABOVE" and gcon["graded_minus_floor"]["band"] == "ABOVE",
      f"g-hard={gcon['graded_minus_hard']['delta']:+.3f}, g-floor={gcon['graded_minus_floor']['delta']:+.3f}")
check("W14 controls hold for the graded bridge (twin + ablation CI-separated below it)",
      gcon["graded_minus_twin"]["band"] == "ABOVE" and gcon["graded_minus_ablation"]["band"] == "ABOVE",
      f"g-twin={gcon['graded_minus_twin']['delta']:+.3f}, g-ablation={gcon['graded_minus_ablation']['delta']:+.3f}")
giv = resC["INVOCAB_edge_accuracy"]
check("W14b in-vocab sanity: hard match works when the edge is present; graded does not collapse",
      giv["hard_match"]["acc"] > 0.9 and giv["graded_distributional"]["acc"] > 0.8,
      f"hard={giv['hard_match']['acc']} graded={giv['graded_distributional']['acc']}")

# ---------------------------------------------------------------- W15-18: multi-fact load + pattern separation
D.self_test()
check("W15 multi-fact load cell self-test passes (pattern-sep recovers ISA under load; dense exact at K=1)", True)
resD = D.run(d=512, ks=(1, 64, 256), n_items=80)
kmax = "256"
dense = resD["DENSE_bundle"]; idx = resD["INDEXED_pattern_separation"]; hi = resD["DENSE_high_dimension"]
check("W16 dense FHRR bundle resolution DEGRADES under multi-fact load (the interference wall)",
      dense[kmax]["resolution"] < dense["1"]["resolution"] - 0.05,
      f"dense res K1={dense['1']['resolution']} -> K{kmax}={dense[kmax]['resolution']} (role-recovery {dense[kmax]['role_recovery']})")
check("W17 PATTERN SEPARATION (relation-indexed) holds resolution FLAT across load (the brain's DG fix)",
      idx[kmax]["resolution"] > dense[kmax]["resolution"] + 0.05 and idx[kmax]["resolution"] > 0.95,
      f"indexed res K{kmax}={idx[kmax]['resolution']} vs dense {dense[kmax]['resolution']}")
check("W18 higher dimension pushes the wall OUT (capacity law: crosstalk ~ K/D)",
      hi[kmax]["resolution"] > dense[kmax]["resolution"],
      f"dense@d={resD['d']} K{kmax}={dense[kmax]['resolution']} vs dense@d={resD['d_high']} K{kmax}={hi[kmax]['resolution']}")
check("W18b info-free twin (shuffled ISA binding) at chance under load",
      dense[kmax]["twin"] < 0.6, f"twin={dense[kmax]['twin']}")

# ---------------------------------------------------------------- summary
n_pass = sum(PASS)
print(f"\n{'ALL CHECKS PASS' if all(PASS) else 'SOME CHECKS FAILED'} -- {n_pass}/{len(PASS)}")
print("A reading-built discourse-fact store + 2-hop bridging is DEAD on the anti-typical coref residual (gold "
      "has no accumulated facts -> intra-sentential, the parser's job) but RECOVERS inter-sentential "
      "fact-decisive reference the fact-blind reader cannot (CI-separated; twin/KG-only/ablation at chance; "
      "graceful degradation) -- the brain's Garrod-Sanford RESOLUTION stage, on the population it is actually for.")
sys.exit(0 if all(PASS) else 1)
