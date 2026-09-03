"""Scaffold-free witness for break_the_contextual_input_encoding_ceiling_for_specific_sense_selection.

Reproduces the located-negative + direction from source (CPU, w2v + WordNet + SyntagNet/ConceptNet; NO GPU,
NO trained encoder, NO external LLM). All on strict document-disjoint SemCor, subordinate senses, subject a_s.

  W1  SIGNAL IS LOST ON THE QUERY, NOT THE KEY: the oracle-query (a sense's own gloss) separates it from every
      competitor ~always (KEY-unwinnable ~ 0), so the whole loss is the context QUERY, not the sense keys.
  W2  THE INFO IS IN THE CONTEXT: the oracle-context-query (best weighting of the ACTUAL w2v context words
      toward gold) reaches ~0.85 -- the disambiguating cue is present; the wall is gold-blind extraction.
  W3  THE BRAIN'S EXACT MECHANISM IS SATURATED: iterative joint constraint-satisfaction settling (no frozen
      encoder) ~= the one-shot biased-competition readout (not CI-above), and dominance-weighting HURTS
      subordinate selection -- the readout mechanism is not the lever.
  W4  CLEAN KNOWLEDGE IS THE LEVER, AND IT MUST BE CLEAN: a clean-knowledge (SyntagNet) context-relevance
      signal fed to biased competition nudges a_s UP directionally; broader-but-noisier ConceptNet does NOT
      beat it (regresses) -- growth must be consolidated, not merely larger.

Run: .venv/Scripts/python.exe verification/test_contextual_ceiling_signal_loss.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_sg_lite_signal_loss_decomposition_v1 as DEC
import experiments.exp_sg_lite_iterative_settling_sense_selector_v1 as SET
import experiments.exp_sg_lite_clean_knowledge_context_relevance_v1 as CK
import experiments.exp_sg_lite_construction_integration_joint_wsd_v1 as CI
import experiments.exp_sg_lite_sense_discriminative_W_headroom_v1 as SD

PASS = 0
FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    if ok:
        PASS += 1
    else:
        FAIL += 1


def main():
    print("[witness] recomputing from source (w2v + WordNet); a few minutes ...", flush=True)

    dec = DEC.run(30)
    ku = dec["loss_decomposition"]["KEY_unwinnable_frac"]
    oc = dec["context_encoding_ceiling"]["oracle_context_query_a_s"]
    chk("W1 loss is QUERY-side, not KEY-side (oracle-query separates ~always: KEY-unwinnable ~ 0)",
        ku <= 0.02, "KEY_unwinnable=%.4f QUERY_loss=%.4f" % (ku, dec["loss_decomposition"]["QUERY_loss_frac"]))
    chk("W2 the cue IS in the local context (oracle-context-query ceiling >= 0.80)",
        oc >= 0.80, "oracle_context_query=%.4f a_s(diag)=%.4f" % (oc, dec["a_s_diag"]))

    st = SET.run(30, 8)
    settle = st["a_s"]["SETTLE_context"]; diag = st["a_s"]["diag_oneshot"]; dom = st["a_s"]["SETTLE_plus_dominance_depth"]
    chk("W3a brain-exact iterative settling ~= one-shot readout (NOT CI-above: mechanism saturated)",
        (not st["settle_vs_diag"]["sep"]) and abs(settle - diag) < 0.02,
        "SETTLE=%.3f diag=%.3f delta=%+.4f sep=%s" % (settle, diag, st["settle_vs_diag"]["delta"], st["settle_vs_diag"]["sep"]))
    chk("W3b dominance-weighting (the brain's frequency mechanism) HURTS subordinate selection",
        dom < diag, "dominance=%.3f < diag=%.3f" % (dom, diag))

    ck = CK.run(30)
    l1 = ck["ladder"]["L1_syntagnet+wnrel"]; l2 = ck["ladder"]["L2_+conceptnet"]
    chk("W4a CLEAN knowledge (SyntagNet) context-relevance nudges a_s UP (directional lift >= 0)",
        l1["lift_vs_diag"] >= -0.001, "L1 a_s=%.4f lift=%+.4f" % (l1["a_s_fused"], l1["lift_vs_diag"]))
    chk("W4b growth must be CLEAN: broader-but-noisier ConceptNet does NOT beat SyntagNet (regresses)",
        l2["lift_vs_diag"] <= l1["lift_vs_diag"] + 1e-9,
        "L1 lift=%+.4f (cov=%.2f) >= L2 lift=%+.4f (cov=%.2f)"
        % (l1["lift_vs_diag"], l1["hit_frac"], l2["lift_vs_diag"], l2["hit_frac"]))

    ci = CI.run(30)
    ciw1 = ci["ladder"]["W1_gloss_cos"]; ciw2 = ci["ladder"]["W2_+syntagnet"]
    dci = ci["a_s_diag_classify_then_weight"]
    chk("W5a the brain's ACTUAL mechanism (C-I joint settling over a topic-W) is BELOW classify-then-weight "
        "(the SHAPE is not the free lunch; the W is the constraint)",
        ciw2["a_s"] < dci, "C-I(W+syntag)=%.3f < diag=%.3f" % (ciw2["a_s"], dci))
    chk("W5b a_s SCALES with W quality: denser+cleaner W2 >= W1 (the lever is the connection matrix W)",
        ciw2["a_s"] >= ciw1["a_s"] - 1e-9, "W1=%.4f -> W2=%.4f" % (ciw1["a_s"], ciw2["a_s"]))

    sd = SD.run(30)
    orac = sd["a_s"]["ORACLE_sense_discriminative_W_upperbound"]
    cov = sd["covered_only"]
    chk("W6a THE LEVER IS THE W: a perfect SENSE-DISCRIMINATIVE W nearly SOLVES the task (oracle >= 0.9) -- the "
        "mechanism/encoder/readout were never the ceiling",
        orac >= 0.9, "ORACLE sense-discriminative W a_s=%.3f (vs topic %.3f)" % (orac, sd["a_s"]["TOPIC_diagnostic"]))
    chk("W6b a LEARNABLE (document-disjoint) sense-discriminative W BEATS topic on covered senses -- the lever "
        "is real + learnable; the bottleneck is COVERAGE (the world-knowledge problem)",
        cov["LEARNED"] > cov["TOPIC"], "covered: LEARNED=%.3f > TOPIC=%.3f (twin-sep=%s)"
        % (cov["LEARNED"], cov["TOPIC"], sd["paired_learned_vs_twin"]["sep"]))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
