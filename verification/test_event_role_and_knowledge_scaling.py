"""Scaffold-free witness for build_sg_lite_self_supervised_scale_generative_sense_predictor.

Reproduces, from the cached offline-built models (deterministic; no external LLM at inference):

  NEGATIVE (the event/role prediction target does NOT raise a_s -- 4 convergent tests):
    W1  frozen-41M role-conditioned readout: right-role NOT CI-above wrong-role (role identity carries no gain)
    W2  end-to-end role TARGET: ROLE_recon < NEXT_recon (training on the event hurts vs next-word)
    W3  role signal FUSED with next-word: FUSE < NEXT (non-complementary)
    W7  even under the BEST (top-k) readout, the role arm loses (role_max < top-k) -- exhausted, not premature

  POSITIVE (two real glass-box levers):
    W4  MORE KNOWLEDGE raises a_s: paired 41M-vs-8M recon a_s (same items) is CI-separated above zero
    W5  the info-free twin LOSES + net over MFS is CI-separated at the 8M and 120M knowledge points
    W6  a richer TOP-K gloss readout beats the mean-pool readout, CI-separated (the lever past the ~40M plateau)

Run: .venv/Scripts/python.exe verification/test_event_role_and_knowledge_scaling.py
"""
import os
import sys
import json

import numpy as np
import torch
import torch.nn as nn

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_sg_lite_sense_gestalt_v1 as SG
import experiments.exp_sg_lite_generative_readout_v1 as GR
import experiments.exp_sg_lite_event_role_readout_v1 as ER
import experiments.exp_sg_lite_event_target_gestalt_v1 as EVT
import experiments.exp_topdown_situation_sense_selector_v1 as P

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


def _load_role_heads():
    nR = len(ER.ROLES)
    heads = nn.ModuleList([nn.Linear(SG.HID, SG.EMB_DIM) for _ in range(nR)])
    heads.load_state_dict(torch.load(os.path.join(SG._SCRATCH, "sglite_roleheads_s120000.pt"), map_location="cpu"))
    heads.eval()
    return {ER.ROLES[i]: heads[i].weight.detach().cpu().numpy() for i in range(nR)}


def _recon_ok(tag):
    """per-item recon-argmax correctness for the gestalt trained on corpus <tag> (knowledge point).
    NB: clear the gloss-vec cache at the START -- each model has its OWN embedding space, so gloss signatures
    must be rebuilt in it (reusing another model's cached vecs cross-contaminates the comparison)."""
    SG._GLOSSV.clear()
    emb = SG._build_embeddings(0, tag)
    net = SG._train_gestalt(emb, 0, tag, 2, smoke=False)
    recs = GR._gestalts_with_mu(net, emb, 30)
    ok, sub, key, doc = [], [], [], []
    for r in recs:
        mu = r["mu"]; n = np.linalg.norm(mu); mu = mu / n if n > 1e-9 else mu
        sc = [float(np.dot(mu, g)) if (g := SG._gloss_vec(emb, sn)) is not None else -9.0 for sn in r["tn"]]
        ok.append(int(r["tn"][int(np.argmax(sc))] in {r["gold"]})); sub.append(r["subordinate"])
        key.append((r["doc_id"], r["lemma"], r["gold"], tuple(r["tn"]))); doc.append(r["doc_id"])
    SG._GLOSSV.clear()
    return np.array(ok), np.array(sub, bool), key, np.array(doc)


def main():
    emb = SG._build_embeddings(0, "full")
    net41 = SG._train_gestalt(emb, 0, "full", 2, smoke=False)

    # ---- W1: frozen role-conditioned readout is null ----
    recs = ER._semcor_role_recs(net41, emb, 30, "f30")
    Wheads = _load_role_heads()
    outA = ER.evaluate(recs, emb, Wheads)
    chk("W1 role readout: right-role NOT CI-above wrong-role",
        outA["paired_rightrole_vs_wrongrole_testsub"]["sep"] is False,
        "right=%.3f wrong=%.3f" % (outA["a_s_test_sub"]["rrecon"], outA["a_s_test_sub_WRONGROLE_rrecon"]))

    # ---- W2/W3: end-to-end event target loses; fusion non-complementary ----
    net_n = EVT._train_target(None, emb, "next", "s80000", 3)
    net_r = EVT._train_target(None, emb, "role", "s80000", 3)
    outB = EVT.evaluate(EVT._semcor_recs(net_n, emb, recs), EVT._semcor_recs(net_r, emb, recs), emb, net_n, net_r)
    chk("W2 event-role TARGET loses to next-word", outB["a_s_test_sub"]["ROLE_recon"] < outB["a_s_test_sub"]["NEXT_recon"],
        "ROLE=%.3f NEXT=%.3f" % (outB["a_s_test_sub"]["ROLE_recon"], outB["a_s_test_sub"]["NEXT_recon"]))
    chk("W3 role signal NON-complementary (FUSE < NEXT)", outB["a_s_test_sub_FUSE"] < outB["a_s_test_sub"]["NEXT_recon"],
        "FUSE=%.3f NEXT=%.3f" % (outB["a_s_test_sub_FUSE"], outB["a_s_test_sub"]["NEXT_recon"]))

    # ---- W4: more knowledge raises a_s, paired CI-separated (41M vs 8M, same items) ----
    ok8, sub8, key8, doc8 = _recon_ok("know530000")
    ok41, sub41, key41, doc41 = _recon_ok("full")
    m41 = {k: i for i, k in enumerate(key41)}
    te8 = doc8 % 2 == 1
    pa, pb = [], []
    for i, k in enumerate(key8):
        if k in m41 and sub8[i] and te8[i]:
            pa.append(ok41[m41[k]]); pb.append(ok8[i])
    d, lo, hi, hw = P._boot(np.array(pa, float), np.array(pb, float), 909)
    chk("W4 MORE KNOWLEDGE raises a_s (paired 41M-vs-8M recon, CI-separated)", lo > 0,
        "delta=%+.4f ci=[%.4f,%.4f] n=%d" % (d, lo, hi, len(pa)))

    # ---- W5: twin loses + net CI-sep at the knowledge points ----
    def _km(tag):
        p = os.path.join(_REPO, "data", "exp_sg_lite_knowledge_scaling_v1", "metrics_%s.json" % tag)
        return json.load(open(p))["result"] if os.path.exists(p) else None
    k8, k120 = _km("know530000"), _km("know7500000")
    if k8 and k120:
        chk("W5 info-free twin LOSES at 8M and 120M",
            bool(k8["twin_real_vs_twin_TEST"]["sep"]) and bool(k120["twin_real_vs_twin_TEST"]["sep"]))
        chk("W5b net over MFS CI-separated at 8M and 120M",
            bool(k8["net_recon"]["sep"]) and bool(k120["net_recon"]["sep"]),
            "8M net=%.4f 120M net=%.4f" % (k8["net_recon"]["delta"], k120["net_recon"]["delta"]))
    else:
        chk("W5 knowledge-point metrics present", False, "missing metrics json")

    # ---- W6/W7: richer top-k readout beats mean-pool CI-sep; role arm still loses under it ----
    sp = os.path.join(_REPO, "data", "exp_sg_lite_selectional_fit_readout_v1", "metrics.json")
    sf = json.load(open(sp))["result"] if os.path.exists(sp) else None
    if sf:
        chk("W6 TOP-K gloss readout beats mean-pool, CI-separated", bool(sf["paired_topk_vs_mean"]["sep"]),
            "topk=%.3f mean=%.3f delta=%+.4f" % (sf["a_s_test_sub"]["topk"], sf["a_s_test_sub"]["mean"],
                                                 sf["paired_topk_vs_mean"]["delta"]))
        chk("W7 event/role arm loses even under the BEST readout (role_max < topk)",
            sf["a_s_test_sub"]["rmax"] < sf["a_s_test_sub"]["topk"],
            "role_max=%.3f topk=%.3f" % (sf["a_s_test_sub"]["rmax"], sf["a_s_test_sub"]["topk"]))
    else:
        chk("W6/W7 selectional-fit metrics present", False, "missing metrics json")

    # ---- W8: the BRAIN-FOUNDATIONAL FIX (biased-competition diagnostic context) beats flat context, twin loses ----
    dp = os.path.join(_REPO, "data", "exp_sg_lite_diagnostic_context_readout_v1", "metrics.json")
    df = json.load(open(dp))["result"] if os.path.exists(dp) else None
    if df:
        chk("W8 diagnostic-context (biased competition) beats flat context, CI-separated",
            bool(df["paired_diagctx_vs_flatctx"]["sep"]),
            "diag=%.3f flat=%.3f delta=%+.4f" % (df["a_s_test_sub"]["diagctx"], df["a_s_test_sub"]["flatctx"],
                                                 df["paired_diagctx_vs_flatctx"]["delta"]))
        chk("W8b shuffled-diagnosticity twin LOSES (correct diagnostic words carry the signal)",
            bool(df["twin_realdiag_vs_shuffled"]["sep"]),
            "real-vs-shuffled=%+.4f" % df["twin_realdiag_vs_shuffled"]["delta"])
    else:
        chk("W8 diagnostic-context metrics present", False, "missing metrics json")

    # ---- W9/W10: knowledge growth is the biggest lever, and it MUST be controlled (raw growth hurts) ----
    kp = os.path.join(_REPO, "data", "exp_sg_lite_knowledge_growth_diagnostic_v1", "metrics_full.json")
    kg = json.load(open(kp))["result"] if os.path.exists(kp) else None
    if kg:
        lad = kg["ladder"]
        chk("W9 knowledge growth boosts a_s (rich >> gloss, CI-separated)",
            lad["L3_+ConceptNet"] > lad["L0_gloss"] and bool(kg["paired_TOP_vs_gloss"]["sep"]),
            "gloss=%.3f rich=%.3f delta=%+.4f" % (lad["L0_gloss"], lad["L3_+ConceptNet"],
                                                  kg["paired_TOP_vs_gloss"]["delta"]))
        chk("W10 growth MUST be controlled: RAW organic knowledge does NOT beat curated (regresses)",
            lad["L4_+ORGANIC(w2vNN)"] <= lad["L3_+ConceptNet"],
            "curated=%.3f raw-organic=%.3f (raw hurts)" % (lad["L3_+ConceptNet"], lad["L4_+ORGANIC(w2vNN)"]))
    else:
        chk("W9/W10 knowledge-growth metrics present", False, "missing metrics json")

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
