"""Scaffold-free witness for causal_encoding_over_fires_without_a_foreground_event_hood_gate.

Recomputes every headline FROM SOURCE: builds the ForegroundGatedReader + the LitBank realis-event gold
(independent, non-circular) + the two floors (ungated reader, p2 stopgap gate) + the p2 within-clause
recall gold + the info-free shuffled-event-hood twin + the document bootstrap, all FRESH via the cell's
run() -- never trusting a landed metrics.json.

  W1  instrument sanity: LitBank event gold loads, the live reader fires on real narrative, and fired
      triggers are a MIX of EVENT/O (the over-fire the gate must separate)
  W2  the graded event-hood gate raises open-text precision CI-separated over the UNGATED reader
  W3  ...and CI-separated over the p2 STOPGAP dep-label gate (it beats BOTH floors, per the bar)
  W4  the info-free SHUFFLED-EVENT-HOOD twin LOSES CI-separated (paired doc-bootstrap) AND the observed
      precision beats the twin null p95 -> the win is alignment with event-hood, not "abstain more"
  W5  RECALL guard: on the p2 within-clause causative gold (n=42) the graded gate does NOT regress 3-way
      accuracy CI-separated below the ungated reader (where the p2 stopgap regressed it 0.833->0.810)
  W6  MECHANISM: the links the gate REMOVES are disproportionately LitBank NON-events (correct removals)
  W7  GENERALIZATION across genre: the precision lift is CI-separated on the DESCRIPTIVE (low-event-
      density) docs -- the gate targets background/description exactly as Hopper predicts
  W8  the graded transitivity CLUSTER beats the p2 dep-label gate BECAUSE aspect/individuation are strong
      event-hood signals while grounding-alone (the stopgap's only signal) is weak -- leg alignment
  W9  the gate reduces over-fire VOLUME (graded fires fewer links than the ungated reader)
  W10 INVARIANT: the gated reader's UNGATED base pipeline is byte-identical to the p2 WiredCausationReader
      (the gate is purely additive; nothing in the proven within-clause path changed)
  W11 CROSS-CORPUS: the event-hood signal transfers to a DIFFERENT corpus/genre/scheme (MAVEN Wikipedia,
      event-mention gold) -- graded > ungated CI-separated (magnitude genre-dependent, honestly smaller on
      event-dense factual prose, but directionally robust)
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
    import spacy
    import numpy as np
    import experiments.exp_causal_foreground_gate_v1 as E
    import experiments._foreground_eventhood as F
    import experiments.exp_wire_causation_typer_live_reader_v1 as W

    nlp = spacy.load("en_core_web_sm")
    lex = W.build_force_lexicon()

    # W1 -- instrument sanity on a real doc
    docs = E.list_docs()
    sents, labels = E.load_litbank_events(docs[0])
    recs = E.score_doc(nlp, lex, sents, labels)
    fired = [r for r in recs if r["fires_ungated"]]
    ev = sum(r["trigger_is_event"] for r in fired)
    check("W1 instrument: reader fires on real LitBank narrative with MIXED event/O triggers",
          len(docs) == 100 and len(fired) >= 5 and 0 < ev < len(fired),
          f"{len(docs)} docs; doc0 fired={len(fired)} event-triggers={ev}")

    # the headline run (all 100 docs; reader+gold+floors+bootstrap all rebuilt fresh)
    res = E.run(nlp, n_docs=None, theta=E.THETA_DEFAULT)
    p = res["precision_by_config"]
    d = res["precision_diffs"]
    t = res["twin_shuffled_eventhood"]
    r = res["recall_guard_p2_gold"]

    # W2 -- beats ungated CI-separated
    check("W2 graded precision > UNGATED reader CI-separated",
          d["graded_vs_ungated"]["CI_separated"],
          f"graded {p['graded']['precision']:.4f} vs ungated {p['ungated']['precision']:.4f}; "
          f"diff {d['graded_vs_ungated']['delta']:+.4f} [{d['graded_vs_ungated']['lo']:.4f},"
          f"{d['graded_vs_ungated']['hi']:.4f}]")

    # W3 -- beats the p2 stopgap CI-separated
    check("W3 graded precision > p2 STOPGAP dep-label gate CI-separated",
          d["graded_vs_stopgap"]["CI_separated"],
          f"graded {p['graded']['precision']:.4f} vs stopgap {p['stopgap']['precision']:.4f}; "
          f"diff {d['graded_vs_stopgap']['delta']:+.4f} [{d['graded_vs_stopgap']['lo']:.4f},"
          f"{d['graded_vs_stopgap']['hi']:.4f}]")

    # W4 -- info-free twin loses
    check("W4 info-free shuffled-event-hood twin LOSES (paired CI-sep AND observed > null p95)",
          t["paired_doc_bootstrap"]["CI_separated"] and t["observed_beats_null_p95"],
          f"paired {t['paired_doc_bootstrap']['delta']:+.4f} "
          f"[{t['paired_doc_bootstrap']['lo']:.4f},{t['paired_doc_bootstrap']['hi']:.4f}]; "
          f"observed {t['graded_precision']:.4f} > null p95 {t['p95']:.4f}")

    # W5 -- recall not regressed CI-separated
    check("W5 recall held: no CI-separated regression on the p2 within-clause gold (n=42)",
          not r["paired_diff_graded_minus_ungated"]["regression_CI_separated"],
          f"ungated_acc {r['ungated_acc']:.4f} graded_acc {r['graded_acc']:.4f} "
          f"eng_recall {r['engagement_recall']}; diff {r['paired_diff_graded_minus_ungated']['delta']:+.4f} "
          f"[{r['paired_diff_graded_minus_ungated']['lo']:.4f},"
          f"{r['paired_diff_graded_minus_ungated']['hi']:.4f}]")

    # W6 -- mechanism: removed links are disproportionately non-events
    rm = res["removal_analysis"]
    check("W6 mechanism: the gate REMOVES disproportionately NON-events (correct removals)",
          rm["removed_correct_nonevent_rate"] > rm["base_ungated_event_rate"] and rm["n_removed"] >= 100
          and rm["removed_correct_nonevent_rate"] >= 0.65,
          f"removed {rm['n_removed']}, {rm['removed_correct_nonevent_rate']:.3f} non-events "
          f"(base event-rate {rm['base_ungated_event_rate']:.3f})")

    # W7 -- generalization across genre (descriptive stratum lift CI-separated)
    g = res["genre_split_descriptive_vs_eventive"]
    desc = g.get("descriptive_low_density", {})
    check("W7 generalization: precision lift CI-separated on DESCRIPTIVE (low-density) docs",
          bool(desc) and desc.get("CI_separated"),
          f"descriptive lift {desc.get('lift'):+.4f} lo {desc.get('lift_lo'):+.4f} "
          f"(ungated {desc.get('ungated_prec'):.3f} -> graded {desc.get('graded_prec'):.3f})")

    # W8 -- leg alignment: aspect strong, grounding-alone weak (why the cluster beats the dep-label gate)
    li = res["leg_informativeness"]
    asp = li["aspect"]; grd = li["ground"]
    check("W8 leg alignment: ASPECT is a strong event-hood signal, GROUNDING-alone is weak "
          "(explains why the transitivity cluster beats the p2 dep-label gate)",
          asp["gap"] is not None and asp["gap"] > 0.15 and grd["gap"] is not None and grd["gap"] < asp["gap"],
          f"aspect fg/bg {asp['event_rate_if_foreground']}/{asp['event_rate_if_background']} (gap {asp['gap']}); "
          f"ground gap {grd['gap']}")

    # W9 -- over-fire volume reduced
    vol = res["over_fire_volume"]
    check("W9 gate reduces over-fire volume (graded fires fewer links than ungated)",
          vol["graded"] < vol["ungated"],
          f"ungated {vol['ungated']} -> graded {vol['graded']} (-{vol['ungated'] - vol['graded']})")

    # W11 -- CROSS-CORPUS: the event-hood signal transfers to a different corpus/genre/scheme (MAVEN
    # Wikipedia): graded > ungated CI-separated. (Honestly genre-dependent magnitude -- small on
    # event-dense factual prose -- but directionally robust and CI-separated.)
    mv = res.get("crosscorpus_maven", {})
    check("W11 cross-corpus: graded > ungated CI-separated on MAVEN (Wikipedia, different corpus/scheme)",
          mv.get("ran") and mv["graded_vs_ungated"]["CI_separated"],
          (f"MAVEN ungated {mv['ungated']['precision']:.3f} -> graded {mv['graded']['precision']:.3f}; "
           f"diff {mv['graded_vs_ungated']['delta']:+.4f} [{mv['graded_vs_ungated']['lo']:.4f},"
           f"{mv['graded_vs_ungated']['hi']:.4f}]") if mv.get("ran") else "MAVEN not reachable")

    # W10 -- invariant: the ungated base pipeline is byte-identical to the p2 WiredCausationReader
    fg = F.ForegroundGatedReader(gaz={}, nlp=nlp, lexicon=lex, gate_mode="force",
                                 use_constructions=True, sense_gate=True, sense_tau=1.0)
    base_links = [(l.sent_idx, l.affector, l.verb, l.patient, l.ctype)
                  for l in fg._read_causation_typed([list(s) for s in sents])]
    p2 = W.WiredCausationReader(gaz={}, causation_typed=True, nlp=nlp, lexicon=lex, gate_mode="force",
                                use_constructions=True, sense_gate=True, sense_tau=1.0)
    p2_links = [(l.sent_idx, l.affector, l.verb, l.patient, l.ctype)
                for l in p2._read_causation_typed([list(s) for s in sents])]
    check("W10 invariant: gated reader's UNGATED base pipeline == p2 WiredCausationReader (purely additive)",
          base_links == p2_links, f"{len(base_links)} base links identical to p2")

    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL %d CHECKS PASS" % 11)


if __name__ == "__main__":
    main()
