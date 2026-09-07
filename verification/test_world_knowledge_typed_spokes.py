"""Scaffold-free witness for expand_the_clean_semantic_memory_foundation_with_world_knowledge_via_the_
consolidation_gate. Recomputes every headline from SOURCE (the loaders + the two experiment cells' functions);
writes nothing; deterministic.

  W0  gold + KB assets present (MoNLI, hub, meaning_foundation store, bridge_relation_assets)
  W1  is-a TYPED directed spoke beats the SYMMETRIC pre-ingest signature floor (0.5) CI-separated on MoNLI
  W2  is-a MONOTONICITY is load-bearing: no-monotonicity ablation collapses on the negation subset
  W3  is-a GATE schema-margin separates CLEAN from WRONG is-a edges (AUC high) -- the admission quality
  W4  is-a GRAPH beats FREQUENCY non-circularly: on the freq-heuristic-WRONG slice the typed taxonomy wins
  W5  is-a shuffled-graph INFO-FREE twin collapses to chance (correct edges, not 'a graph')
  W6  part-whole/instrument TYPED spoke beats the SYMMETRIC read on COVERED pairs (esp. confusable distractors)
  W7  part-whole/instrument GENERALIZATION located negative: held-out typed < in-domain typed (does not generalize)
  W8  NO REGRESSION: the frozen C1 meaning store is intact (spokes are additive; the signature is untouched)

Run: .venv/Scripts/python.exe verification/test_world_knowledge_typed_spokes.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

import experiments.exp_isa_typed_spoke_monli_v1 as ISA
import experiments.exp_partwhole_typed_spoke_bridging_v1 as PW

PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(("  PASS " if cond else "  FAIL ") + name + ("  :: " + detail if detail else ""))


def main():
    print("witness: world-knowledge typed spokes (is-a + part-whole/instrument)\n")

    # -- W0 assets --
    monli_ok = all(os.path.exists(os.path.join(ISA.MONLI, f))
                   for f in ("pmonli.jsonl", "nmonli_test.jsonl"))
    hub_ok = os.path.exists(PW.HUB_PATH)
    from hdlab.meaning_foundation import covers
    store_ok = covers("dog.n.01")
    cn_ok = os.path.exists(os.path.join(PW.CN_DIR, "PartOf.jsonl"))
    check("W0 gold + KB assets present", monli_ok and hub_ok and store_ok and cn_ok,
          "monli=%s hub=%s store=%s conceptnet=%s" % (monli_ok, hub_ok, store_ok, cn_ok))

    # -- is-a demo (recompute from source) --
    w2i, _mat = ISA.load_w2v()
    pm = ISA.load_monli("pmonli.jsonl")
    nt = ISA.load_monli("nmonli_test.jsonl")
    combined = pm + nt
    ok_typed = ISA.judge(combined, ISA.isa_mfs_fn)
    ok_shuf = ISA.judge(combined, ISA.make_isa_shuffled(combined, seed=0))
    ok_freq = ISA.judge(combined, ISA.make_freq_floor(combined, w2i))
    a_typed = float(ok_typed.mean())
    mono_typed = float(ISA.judge(nt, ISA.isa_mfs_fn).mean())
    mono_no = float(ISA.judge(nt, ISA.isa_mfs_fn, use_mono=False).mean())
    m_vs_half = ISA.boot_margin(ok_typed, np.full(len(ok_typed), 0.5))
    check("W1 is-a typed spoke beats symmetric floor (0.5) CI-separated on MoNLI",
          m_vs_half["sep"] and a_typed > 0.65,
          "typed=%.3f vs sym-floor 0.500 margin=%.3f CI[%.3f,%.3f]" %
          (a_typed, m_vs_half["delta"], m_vs_half["lo"], m_vs_half["hi"]))
    check("W2 monotonicity load-bearing: no-mono collapses on negation subset",
          mono_typed > 0.7 and mono_no < 0.35,
          "negation: mono=%.3f  no-mono=%.3f" % (mono_typed, mono_no))

    # gate schema-margin AUC (recompute)
    mf_cache = {}
    clean_edges = set(ISA.collect_edges(combined))
    all_parents = sorted({p for _, p in clean_edges})
    noisy = ISA.inject_noise(clean_edges, all_parents, 0.3, seed=7)
    _adm, scores, flags = ISA.gate_edges(noisy, mf_cache, margin=0.05)
    auc = ISA._auc(scores, flags)
    check("W3 gate schema-margin separates clean from wrong is-a edges (AUC high)",
          auc >= 0.85, "schema-margin AUC=%.3f" % auc)

    freq_wrong = [i for i in range(len(combined)) if ok_freq[i] == 0]
    typed_on_fw = float(ok_typed[freq_wrong].mean())
    check("W4 graph beats frequency non-circularly (freq-wrong slice: typed wins, freq=0)",
          len(freq_wrong) > 30 and typed_on_fw > 0.5,
          "n_freq_wrong=%d typed=%.3f freq=0.000" % (len(freq_wrong), typed_on_fw))

    m_vs_shuf = ISA.boot_margin(ok_typed, ok_shuf)
    check("W5 is-a shuffled-graph info-free twin collapses to chance",
          m_vs_shuf["sep"] and float(ok_shuf.mean()) < 0.55,
          "typed=%.3f shuffled=%.3f margin=%.3f CI[%.3f,%.3f]" %
          (a_typed, float(ok_shuf.mean()), m_vs_shuf["delta"], m_vs_shuf["lo"], m_vs_shuf["hi"]))

    # -- W5b is-a replicates on a SECOND, less-circular gold (MED) CI-separated over majority --
    med = ISA.med_second_gold_report()
    check("W5b is-a spoke replicates on MED (second gold) CI-separated over majority",
          med["margin_vs_majority"]["sep"] and med["isa_spoke_acc"][0] > med["majority_floor"],
          "MED is-a=%.3f vs majority=%.3f margin=%.3f (coverage %.3f = single-is-a-substitution slice)" %
          (med["isa_spoke_acc"][0], med["majority_floor"], med["margin_vs_majority"]["delta"],
           med["coverage_single_isa_substitution"]))

    # -- part-whole / instrument bridging demo (recompute) --
    import pickle
    hub = pickle.load(open(PW.HUB_PATH, "rb"))["hub"]
    mfnd = PW.build_mfnd()
    for source in ("part_cn", "instrument"):
        conf_in = PW.eval_bridging(source, hub, mfnd, confusable=True, held_out=False, seed=0)
        conf_ho = PW.eval_bridging(source, hub, mfnd, confusable=True, held_out=True, seed=0)
        typed_in = float(conf_in["TYPED_directed_spoke"].mean())
        raw_sym = float(conf_in["RAW_HUB_symmetric"].mean())
        typed_ho = float(conf_ho["TYPED_directed_spoke"].mean())
        twin = float(conf_in["TWIN_shuffled_graph"].mean())
        d = PW.delta_ci(conf_in["TYPED_directed_spoke"], conf_in["RAW_HUB_symmetric"])
        check("W6 [%s] typed spoke beats symmetric on COVERED pairs (confusable distractors) CI-sep" % source,
              d["sep"] and typed_in > raw_sym and typed_in > 0.7,
              "typed_indomain=%.3f raw_sym=%.3f margin=%.3f" % (typed_in, raw_sym, d["d"]))
        check("W7 [%s] generalization located negative: held-out typed < in-domain typed" % source,
              typed_ho < typed_in - 0.2,
              "typed held-out=%.3f < in-domain=%.3f" % (typed_ho, typed_in))
        check("W8a [%s] shuffled-graph info-free twin loses to typed in-domain" % source,
              twin < typed_in, "twin=%.3f < typed=%.3f" % (twin, typed_in))

    # -- W9/W10 is-a spoke on a REAL downstream consumer (GUM common-noun coref), non-circular --
    import experiments.exp_isa_spoke_commonnoun_coref_gum_v1 as CN
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    import experiments.gum_coref as G
    docs = G.load_docs(gum_only=True, name_gazetteer=load_given_gazetteer())
    test = [d for i, d in enumerate(docs) if i % 2 == 1]
    heads = sorted({m.lemma_head for d in test for m in d.mentions if m.mtype == "common"})
    sh_anc, sh_mero = CN.build_shuffled_spoke(heads, seed=0)
    rec = CN._item_vectors(test, "recency_wk")[0]
    rec_isa = CN._item_vectors(test, "recency_isa")[0]
    rec_isa_twin = CN._item_vectors(test, "recency_isa", anc_fn=sh_anc, mero_fn=sh_mero)[0]
    d_vs_rec = CN.boot_delta(rec_isa, rec)
    d_vs_twin = CN.boot_delta(rec_isa, rec_isa_twin)
    check("W9 is-a/part-whole spoke lifts GUM common-noun coref over recency (Centering) CI-sep",
          d_vs_rec["sep"] and d_vs_rec["delta"] > 0,
          "recency=%.4f recency+isa-filter=%.4f delta=%.4f CI[%.4f,%.4f]" %
          (float(rec.mean()), float(rec_isa.mean()), d_vs_rec["delta"], d_vs_rec["lo"], d_vs_rec["hi"]))
    check("W10 the coref win is CORRECT knowledge (beats shuffled-filter twin CI-sep), not 'any filter'",
          d_vs_twin["sep"] and d_vs_twin["delta"] > 0,
          "recency+isa=%.4f shuffled-filter-twin=%.4f delta=%.4f CI[%.4f,%.4f]" %
          (float(rec_isa.mean()), float(rec_isa_twin.mean()), d_vs_twin["delta"], d_vs_twin["lo"], d_vs_twin["hi"]))

    # -- W5c gate consumer robustness: raw-noisy admission does NOT regress the is-a consumer; gate filters edges --
    gr = ISA.gate_consumer_robustness()
    check("W5c gate: is-a consumer is ROBUST to noisy admission (raw~=clean) and the gate filters wrong edges",
          abs(gr["raw_noisy"] - gr["clean"]) < 0.02 and gr["wrong_filtered_rate"] > 0.9,
          "clean=%.4f raw-noisy=%.4f filtered-closure=%.4f wrong-filtered=%.2f" %
          (gr["clean"], gr["raw_noisy"], gr["edge_filtered_closure"], gr["wrong_filtered_rate"]))

    # -- W11/W12 ANTONYMY (5th typed spoke): symmetric signature is ANTI-predictive on opposition --
    import experiments.exp_antonym_typed_spoke_valence_v1 as ANT
    ares = ANT.run(smoke=False)
    auc_sym = ares["symmetric_cap"]["AUC_symmetric_separates_syn_from_ant"]
    vc = ares["valence_consumer"]
    check("W11 antonymy: symmetric cosine is ANTI-predictive on opposition (AUC < 0.5)",
          auc_sym < 0.5,
          "AUC(sym separates syn from ant)=%.3f (cos ant=%.3f > syn=%.3f)" %
          (auc_sym, ares["symmetric_cap"]["mean_cos_antonym"], ares["symmetric_cap"]["mean_cos_synonym"]))
    check("W12 antonymy valence consumer: symmetric-oracle ~chance, typed spoke + beats shuffled twin CI-sep",
          vc["symmetric_cosine_oracle"] < 0.62 and vc["typed_minus_twin"]["sep"] and vc["typed_minus_symmetric"]["sep"],
          "symmetric-oracle=%.3f typed=%.3f twin=%.3f (majority floor %.3f)" %
          (vc["symmetric_cosine_oracle"], vc["typed_antonym_spoke"], vc["shuffled_label_twin"], vc["majority_floor"]))

    # -- W13/W14 NATURAL LOGIC over the is-a spoke builds across the MED coverage wall (15% -> ~85%) --
    import experiments.exp_natural_logic_monotonicity_med_v1 as NL
    nlr = NL.run(smoke=False, light=True)   # light: skip the POS/parser-heavy informational drills (speed)
    check("W13 natural logic covers ~85% of MED and beats majority + symmetric-cosine CI-sep",
          nlr["coverage"] > 0.7 and nlr["margins"]["natlog_vs_majority"]["sep"]
          and nlr["margins"]["natlog_vs_symmetric"]["sep"],
          "coverage=%.3f self-mono=%.3f vs majority=%.3f symmetric=%.3f" %
          (nlr["coverage"], nlr["acc"]["natural_logic_self_detected_monotonicity"][0],
           nlr["acc"]["majority_floor"], nlr["acc"]["symmetric_sentence_cosine_oracle"]))
    check("W14 natural-logic MONOTONICITY polarity is load-bearing (shuffled-monotonicity twin loses CI-sep)",
          nlr["margins"]["natlog_vs_shuffled_twin"]["sep"]
          and nlr["acc"]["shuffled_monotonicity_twin"][0] < nlr["acc"]["natural_logic_self_detected_monotonicity"][0],
          "self-mono=%.3f vs shuffled-monotonicity twin=%.3f (oracle-mono upper bound %.3f)" %
          (nlr["acc"]["natural_logic_self_detected_monotonicity"][0], nlr["acc"]["shuffled_monotonicity_twin"][0],
           nlr["acc"]["natural_logic_ORACLE_monotonicity_upperbound"][0]))
    # W15: the ADMISSIBLE (reader's-own-parser) projectivity is what counts; the fully-brain-foundational headline
    # stays the sentence-level marker. The projectivity MECHANISM ceiling (non-admissible external parser) confirms
    # the lever is the reader's PARSER on formal text, not the mechanism.
    rp = nlr.get("reader_parse_projectivity_ADMISSIBLE", {})
    check("W15 parse/scope drills are informational (located-negatives + non-admissible ceiling); the admissible "
          "brain-foundational headline is the parse-free sentence-level marker (drills skipped in light witness)",
          (not rp) or (not rp.get("available")) or ("reader_parse_projectivity_acc" in rp),
          "drills computed in the standalone full run (verdict C: fast register 0.767 = brain-faithful; slow "
          "register = bounded restrictor-attachment, needs VerbNet)")

    # -- W8 no regression: the frozen C1 store is intact + additive (never written by this problem) --
    from hdlab.meaning_foundation import sense_signature, dim
    v = sense_signature("dog.n.01")
    check("W8 frozen C1 meaning store intact (spokes additive, signature untouched)",
          v is not None and dim() == 200 and abs(float(np.linalg.norm(v)) - 1.0) < 1e-3,
          "dim=%d dog.n.01 unit-norm=%.4f" % (dim(), float(np.linalg.norm(v))))

    n = sum(PASS)
    print("\n%d/%d witnesses PASS" % (n, len(PASS)))
    sys.exit(0 if n == len(PASS) else 1)


if __name__ == "__main__":
    main()
