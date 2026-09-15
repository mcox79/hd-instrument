"""Scaffold-free witness for acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref.

Reproduces the load-bearing claims WITHOUT re-running/overwriting any landed cell's metrics.
  W1  the entity-type spoke LICENSES directionally (Zurbaran/Artist licenses 'the artist'; Argentina/Country
      licenses 'the country'; an artist does NOT license 'the country') -- reuses the landed C5 is-a closure.
  W2  predict() narrows recency to the TYPE-LICENSED name (license, recency selects).
  W3  string-identity AND WordNet-only are 0.000 on name-bridge (a name is not 'artist'; proper names not in
      WordNet); recency (the strongest honest floor) is well above 0.
  W4  the CONSOLIDATED-KB route beats recency CI-separated on the LICENSED subpopulation (where it has coverage).
  W5  the info-free SHUFFLED-KB twin LOSES to the real KB on the whole slice (correct types, not 'any type-token').
  W6  ABSTENTION is safe: on items with NO licensed candidate the KB arm == recency exactly (no regress).
  W7  the brain-foundational TWO-ROUTE (CLS) system -- consolidated entity-type KB UNION episodic in-text is-a --
      beats recency CI-separated on the WHOLE name-bridge slice, and the two routes are COMPLEMENTARY (KB-unique
      and in-text-unique wins are both substantial, overlap ~1).
  W8  the KB's unique name-bridge wins COLLAPSE under a shuffled KB (the consolidated route's contribution is the
      correct encyclopedic types, not chance).

Run: .venv/Scripts/python.exe verification/test_namebridge_entity_type_spoke.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
import experiments._entity_type_spoke as ES
import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
import experiments.exp_namebridge_coref_kb_v1 as NB


def main():
    assert ES.available(), "entity-type spoke asset absent -- run build_entity_type_spoke_v1.py --build"
    ok = 0

    # W1 -- directed licensing (reuses C5)
    assert ES.type_licenses("artist", "Francisco de Zurbaran"), "Zurbaran(Artist) must license 'the artist'"
    assert ES.type_licenses("country", "Argentina"), "Argentina(Country) must license 'the country'"
    assert ES.type_licenses("painter", "Francisco de Zurbaran"), "Zurbaran licenses the more-specific 'the painter'"
    assert not ES.type_licenses("country", "Francisco de Zurbaran"), "an artist must NOT license 'the country'"
    print("W1 PASS: entity-type spoke licenses directionally via C5 (artist<-Artist, country<-Country; not crossed)")
    ok += 1

    # W2 -- predict narrows recency to the licensed name (4-tuple item: head, gold, active, intext)
    item = ("artist", 7, [{"surfaces": ["Barack Obama"], "tokens": ["barack", "obama"], "eid": 3, "order": 9, "gender": "m"},
                          {"surfaces": ["Francisco de Zurbaran"], "tokens": ["francisco", "de", "zurbaran"],
                           "eid": 7, "order": 5, "gender": ""}], [])
    assert NB.predict(item, "recency") == 3, "recency picks the most-recent name (Obama)"
    assert NB.predict(item, "kb_typelicense") == 7, "KB narrows to the type-licensed Artist (Zurbaran)"
    print("W2 PASS: predict() narrows recency to the type-licensed name")
    ok += 1

    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, name_gazetteer=gaz)
    items = NB.collect_items(docs)
    assert len(items) > 250, "expected >250 GUM name-bridge items, got %d" % len(items)

    v_str = NB._vec(items, "string_identity"); v_wn = NB._vec(items, "wordnet_only")
    v_rec = NB._vec(items, "recency"); v_kb = NB._vec(items, "kb_typelicense")
    v_it = NB._vec(items, "intext_only"); v_ki = NB._vec(items, "kb_intext")
    v_kg = NB._vec(items, "kb_graded"); v_kt = NB._vec(items, "kb_thematic")

    # W3 -- named floors are 0.000; recency is the real floor
    assert v_str.mean() == 0.0 and v_wn.mean() == 0.0, "string-identity & WordNet-only must be 0.000 on name-bridge"
    assert v_rec.mean() > 0.30, "recency (the honest floor) should be well above 0: %.3f" % v_rec.mean()
    print("W3 PASS: string-identity=0.000, wordnet-only=0.000, recency floor=%.3f (n=%d)" % (v_rec.mean(), len(items)))
    ok += 1

    # W4 -- licensed subpopulation: KB beats recency CI-separated
    lic = np.array([1 if any(ES.type_licenses(h, s) for r in active if r["eid"] == ge for s in r["surfaces"])
                    else 0 for (h, ge, active, intext) in items], bool)
    d = NB.boot_delta(v_kb[lic], v_rec[lic])
    assert lic.sum() >= 40 and d["sep"] and d["delta"] > 0, "KB must beat recency CI-sep on licensed subpop: %s" % d
    print("W4 PASS: LICENSED subpop n=%d -- recency=%.3f -> kb=%.3f (%+.4f CI[%+.4f,%+.4f] sep)" % (
        int(lic.sum()), v_rec[lic].mean(), v_kb[lic].mean(), d["delta"], d["lo"], d["hi"]))
    ok += 1

    # W5 -- shuffled-KB twin loses on the whole slice
    twin = NB.build_twin_map(items, seed=0)
    v_tw = NB._vec(items, "kb_typelicense", twin=twin)
    dt = NB.boot_delta(v_kb, v_tw)
    assert dt["sep"] and dt["delta"] > 0, "real KB must beat the shuffled-KB twin CI-sep: %s" % dt
    print("W5 PASS: whole slice kb=%.3f > shuffled-twin=%.3f (%+.4f CI[%+.4f,%+.4f] sep)" % (
        v_kb.mean(), v_tw.mean(), dt["delta"], dt["lo"], dt["hi"]))
    ok += 1

    # W6 -- abstention safe
    no_lic = np.array([0 if any(ES.type_licenses(h, s) for r in active for s in r["surfaces"]) else 1
                       for (h, ge, active, intext) in items], bool)
    assert np.array_equal(v_kb[no_lic], v_rec[no_lic]), "abstention must fall back to recency exactly"
    print("W6 PASS: abstention-safe -- on %d items with no licensed candidate, kb == recency exactly" % int(no_lic.sum()))
    ok += 1

    # W7 -- two-route CLS beats recency CI-sep + complementarity; GRADED constraint-integration is >= binary
    dki = NB.boot_delta(v_ki, v_rec)
    dkg = NB.boot_delta(v_kg, v_rec)
    assert dki["sep"] and dki["delta"] > 0, "two-route binary (KB + in-text) must beat recency CI-sep: %s" % dki
    assert dkg["sep"] and dkg["delta"] > 0, "two-route GRADED must beat recency CI-sep: %s" % dkg
    assert v_kg.mean() >= v_ki.mean() - 1e-9, "graded constraint-integration must be >= binary license+recency"
    dkt = NB.boot_delta(v_kt, v_rec)
    assert dkt["sep"] and v_kt.mean() >= v_kg.mean() - 1e-9, "kb_thematic (fullest BF mechanism) >= graded, beats recency CI-sep: %s" % dkt
    kb_only = int(np.sum((v_kb > v_rec) & (v_it <= v_rec) & (v_kb > v_it)))
    it_only = int(np.sum((v_it > v_rec) & (v_kb <= v_rec) & (v_it > v_kb)))
    assert kb_only >= 15 and it_only >= 15, "routes must be complementary (kb_only=%d it_only=%d)" % (kb_only, it_only)
    print("W7 PASS: two-route CLS binary=%.3f / GRADED=%.3f vs recency (graded %+.4f CI[%+.4f,%+.4f] sep); "
          "complementary (KB-unique=%d, in-text-unique=%d)" % (
              v_ki.mean(), v_kg.mean(), dkg["delta"], dkg["lo"], dkg["hi"], kb_only, it_only))
    ok += 1

    # W8 -- KB-unique wins collapse under a shuffled KB
    kb_only_twin = int(np.sum((v_tw > v_rec) & (v_it <= v_rec) & (v_tw > v_it)))
    assert kb_only_twin < kb_only, "KB-unique wins must collapse under shuffled KB (real=%d twin=%d)" % (kb_only, kb_only_twin)
    print("W8 PASS: KB-unique wins real=%d -> shuffled-KB twin=%d (correct encyclopedic types carry it)" % (
        kb_only, kb_only_twin))
    ok += 1

    print("\nALL WITNESSES PASS (%d/8)" % ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
