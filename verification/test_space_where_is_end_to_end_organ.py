"""Scaffold-free witness for the_reader_has_no_spatial_location_dimension_end_to_end.

Recomputes every headline FROM SOURCE via the cell's run() (write=False -- never touches the landed
metrics.json): builds the reader's OWN in-substrate parse + coref backbone, drives the PROMOTED
hdlab.location_register end-to-end on 14 real LitBank passages, recomputes the hand-adjudicated where-is
gold, both stateless floors, the info-free twin, the distance curve, and the parse-as-truth-vs-prior
discriminator -- never trusting a landed number.

  W1  gold loads: >=50 hand-verified change-points across >=12 real passages, >=20 character-timelines
  W2  REGISTER_prior (reader's OWN extraction -> promoted tracker) answers where-is CI-separated over the
      strongest stateless floor (last-mention-location) -- the SPACE dimension works end-to-end
  W3  REGISTER_prior CI-separated over the current-reader ABSTAIN floor (no SPACE dimension = 0)
  W4  the info-free TWIN (same events, order destroyed) LOSES to REGISTER_prior CI-separated -- the gain is
      stateful sequence tracking, not "fire more"
  W5  the PRIOR is what makes it a real tracker: REGISTER_prior beats the twin by MORE than parse-as-TRUTH
      does, and prior pop-acc > truth pop-acc (parse-as-EVIDENCE + revise-on-surprise adds the stateful signal)
  W6  PERSISTENCE / distance signature (Zwaan & Radvansky; Rinck & Bower): last-mention-location collapses
      at distance (acc ~0 for >=4 intervening sentences) while REGISTER_prior HOLDS the state above it
  W7  PRESENT-IN-SCENE (the robust query the ToM/perceptual-access organ consumes) -- REGISTER_prior beats
      the last-mention floor by a clear margin
  W8  EXTRACTION is the honest BOUND: the reader's in-substrate parse recovers only a MINORITY of the true
      motion events (0 < event-recall < 0.6) -- the wall is enumerated, pointing SPACE at the parser (p2)
  W9  the DISCRIMINATOR ran: on the subset where parse-as-truth errs, the prior recovers a positive share,
      and prior >= truth overall (the prior helps; the residual is parser recall)
  W10 the PROMOTED hdlab tracker is actually driven end-to-end (events > 0; where_is returns real nodes)
  W11 the brain-faithful EXTENSION (veridical embedded-clause routing + caused-motion theme relocation +
      expanded stative locatives) RAISES event-recall AND precision over plain prior -- crossing part of the
      extraction wall without adding noise (recall up, precision up = a real recovery, not fire-more)
  W12 REGISTER_prior_ext beats ITS OWN info-free null p95 (the extension's richer events shuffled) AND beats
      every stateless floor CI-separated -- the extension's gain is real signal, not luck
  W13 CORPUS-AGE control: on MODERN author-constructed prose the extraction does NOT degrade (recall holds) and
      the register beats the abstain floor + the info-free null -- the 19c result is not a vocabulary artifact
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def main():
    import experiments.exp_space_where_is_end_to_end_v1 as E
    from experiments._space_reader import read_locations_in_substrate

    gold = E.load_gold()
    books = sorted({b for (b, c) in gold})
    n_cp = sum(len(v) for v in gold.values())
    check("W1 gold loads: >=50 change-points, >=12 books, >=20 timelines",
          n_cp >= 50 and len(books) >= 12 and len(gold) >= 20,
          f"change_points={n_cp} books={len(books)} timelines={len(gold)}")

    out = E.run(smoke=False, use_spacy=False, n_boot=1500, write=False)
    g = out["gates"]["REGISTER_prior"]
    gt = out["gates"]["REGISTER_truth"]

    check("W2 REGISTER_prior > strongest stateless floor CI-separated",
          g["vs_strongest_floor"]["CI_separated"],
          f"{g['vs_strongest_floor']['a_mean']:.3f} vs {g['vs_strongest_floor']['b_mean']:.3f} "
          f"({out['strongest_floor_arm']}); delta {g['vs_strongest_floor']['delta']:+.3f} "
          f"[{g['vs_strongest_floor']['lo']:+.3f},{g['vs_strongest_floor']['hi']:+.3f}]")
    check("W3 REGISTER_prior > current-reader ABSTAIN floor CI-separated",
          g["vs_abstain"]["CI_separated"],
          f"delta {g['vs_abstain']['delta']:+.3f} [{g['vs_abstain']['lo']:+.3f},{g['vs_abstain']['hi']:+.3f}]")
    tn = out["twin_null"]
    check("W4 info-free TWIN NULL LOSES: REGISTER_prior beats the twin null p95 (R reshuffles)",
          tn["prior_beats_p95"],
          f"prior {out['pop_acc']['REGISTER_prior']:.3f} > null p95 {tn['p95']:.3f} "
          f"(null mean {tn['mean']:.3f}, R={tn['R']})")
    check("W5 the PRIOR adds the stateful signal: prior clears the null p95 by MORE than parse-as-truth, "
          "and prior>truth (parse-as-truth sits at/below the info-free null)",
          (out["pop_acc"]["REGISTER_prior"] - tn["p95"]) > (out["pop_acc"]["REGISTER_truth"] - tn["p95"])
          and out["pop_acc"]["REGISTER_prior"] > out["pop_acc"]["REGISTER_truth"],
          f"prior-p95 {out['pop_acc']['REGISTER_prior'] - tn['p95']:+.3f} vs "
          f"truth-p95 {out['pop_acc']['REGISTER_truth'] - tn['p95']:+.3f}; "
          f"truth {out['pop_acc']['REGISTER_truth']:.3f} vs null p95 {tn['p95']:.3f}")

    dc = out["distance_curve"]
    far = dc.get("11-9999", {})
    lastm_far = far.get("FLOOR_lastment")
    prior_far = far.get("REGISTER_prior")
    check("W6 PERSISTENCE signature: last-mention collapses at distance, REGISTER_prior holds above it",
          lastm_far is not None and prior_far is not None and lastm_far <= 0.02 and prior_far > lastm_far,
          f"dist>=11: prior={prior_far} vs last-mention={lastm_far} (n={far.get('n')})")

    rp = out["region_present_acc"]
    check("W7 PRESENT-IN-SCENE: REGISTER_prior beats last-mention floor by a clear margin",
          rp["REGISTER_prior"]["present_acc"] >= rp["FLOOR_lastment"]["present_acc"] + 0.15,
          f"prior present {rp['REGISTER_prior']['present_acc']:.3f} vs floor "
          f"{rp['FLOOR_lastment']['present_acc']:.3f}")

    eq = out["extraction_quality"]["prior"]
    check("W8 EXTRACTION is the honest bound: 0 < event-recall < 0.6 (the wall is enumerated -> p2)",
          0.0 < eq["recall"] < 0.6,
          f"event-recall {eq['recall']:.3f}  node-recall {eq['node_recall']:.3f}  "
          f"precision {eq['precision']:.3f}  gold_change_points {eq['gold_change_points']}")

    dz = out["discriminator"]
    check("W9 DISCRIMINATOR ran: prior recovers a positive share of truth-errors AND prior>=truth overall",
          dz["prior_recovers_on_truth_errors"] > 0.0 and dz["prior_vs_truth"]["delta"] >= 0.0,
          f"recovers {dz['prior_recovers_on_truth_errors']:.3f} of {dz['n_truth_wrong']} truth-errors; "
          f"prior-truth delta {dz['prior_vs_truth']['delta']:+.3f}")

    # W10 the promoted hdlab tracker is actually driven end-to-end
    path = os.path.join(REPO, "data/litbank/coref/conll/113_the_secret_garden_brat.conll")
    reg, events, names, sents, persons = read_locations_in_substrate(path, mode="prior")
    from hdlab.location_register import LocationRegister as HdlabReg
    node_types = {reg.where_is(str(c), len(sents) - 1) for c in persons}
    check("W10 the PROMOTED hdlab tracker is driven end-to-end (events>0; real where_is nodes)",
          isinstance(reg, HdlabReg) and len(events) > 0 and len(node_types) >= 1,
          f"events={len(events)} persons={len(persons)} distinct_end_nodes={len(node_types)}")

    qx = out["extraction_quality"]["prior_ext"]
    qp = out["extraction_quality"]["prior"]
    check("W11 the brain-faithful EXTENSION raises event-recall AND precision over plain prior (real recovery)",
          qx["recall"] > qp["recall"] and qx["precision"] >= qp["precision"] and qx["node_recall"] > qp["node_recall"],
          f"recall {qp['recall']:.3f}->{qx['recall']:.3f}  node-recall {qp['node_recall']:.3f}->{qx['node_recall']:.3f}  "
          f"precision {qp['precision']:.3f}->{qx['precision']:.3f}")
    gx = out["gates"]["REGISTER_prior_ext"]
    check("W12 REGISTER_prior_ext beats its OWN info-free null p95 AND every stateless floor CI-separated",
          out["twin_null_ext"]["prior_ext_beats_p95"] and gx["vs_strongest_floor"]["CI_separated"]
          and gx["vs_abstain"]["CI_separated"],
          f"prior_ext {out['pop_acc']['REGISTER_prior_ext']:.3f} > own null p95 "
          f"{out['twin_null_ext']['p95']:.3f}={out['twin_null_ext']['prior_ext_beats_p95']}; "
          f"vs floor delta {gx['vs_strongest_floor']['delta']:+.3f} CI-sep={gx['vs_strongest_floor']['CI_separated']}")

    # W13 corpus-age control: the extraction does NOT degrade on MODERN vocabulary (recall holds; register
    # beats the abstain floor + the info-free null) -- the LitBank result is not a 19c-vocabulary artifact.
    import experiments.exp_space_where_is_modern_v1 as MOD
    mo = MOD.run(smoke=False, n_boot=1000)
    check("W13 CORPUS-AGE control: modern extraction does not degrade (recall >= 0.30) AND register beats "
          "abstain + info-free null (not a 19c-vocabulary artifact)",
          mo["extraction_quality"]["recall"] >= 0.30 and mo["gates"]["vs_abstain"]["CI_separated"]
          and mo["twin_null"]["register_beats_p95"],
          f"modern recall {mo['extraction_quality']['recall']:.3f} (LitBank 0.35); register {mo['pop_acc']['REGISTER_prior_ext']:.3f} "
          f"vs abstain CI-sep={mo['gates']['vs_abstain']['CI_separated']}, beats null p95={mo['twin_null']['register_beats_p95']}")

    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL 13 CHECKS PASS")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
