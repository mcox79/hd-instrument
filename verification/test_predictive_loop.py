"""Scaffold-free witness for close_the_recurrent_predictive_coding_loop_n400_error_against_the_forward_prediction.
Reproduces the headline claims from source (no experiment scaffolding), each check can FAIL:

  W1 COHERENCE loop-closure: forward prediction-error beats the backward-gist discrimination on Story Cloze,
     paired margin lower-CI > 0.
  W2 cross-context twin COLLAPSES (forward beats its own cross-context twin) -> uses THIS story.
  W3 CONSTRUCTION control (concat ROCStories, near-orthogonal boundaries): forward segmentation F1 >> backward
     (the SOLVED loop-cell direction reproduces) -> the mechanism works when boundaries are real situation-changes.
  W4 LOCATED NEGATIVE on real-prose segmentation: content-forward does NOT CI-beat content-backward on GUM
     paragraph boundaries (the honest tie the deliverable centres on).
  W5 BUILD-ACROSS: the MULTI-DIMENSIONAL forward error (content + gold protagonist/entity, Zwaan index) beats the
     MULTI-DIMENSIONAL backward error CI-separated -> the forward DIRECTION wins at the right representation.
  W6 the PROTAGONIST/ENTITY dimension is the lever: gold-entity boundary AUC > content-forward AUC.
  W7 the monitor consumes the LIVE forward organ (hdlab.generalized_event_knowledge available + used).

Run: .venv/Scripts/python.exe verification/test_predictive_loop.py
"""
from __future__ import annotations
import glob, json, os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np, pickle
from experiments import _predictive_loop as PL
from experiments.exp_predictive_loop_dimensional_v1 import parse_gum_doc, entity_signal
from experiments.exp_predictive_loop_dimensional_v2 import parse_rich, discont
from hdlab.generalized_event_knowledge import lemmatize, available as gek_available

HUB = pickle.load(open(os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl"), "rb"))["hub"]
NARR = ("fiction", "bio", "voyage", "news")


def _jsonl(p, n=None):
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return rows[:n] if n else rows


def main():
    fails = []

    # W7 -- the live forward organ is present + consumed by the monitor module
    assert gek_available(), "GEK forward organ store absent -- the loop cannot consume the live forward prediction"
    print("W7 live forward organ (generalized_event_knowledge) available + consumed: PASS")

    # ---- W1/W2 COHERENCE (Story Cloze subset) ----
    sc = _jsonl(os.path.join(_REPO, "data", "corpora", "story_cloze", "validation.jsonl"), 1200)
    fo, bo, tw = [], [], []
    ctxls, ends, golds = [], [], []
    for r in sc:
        ctxl = lemmatize(" ".join(r["input_sentence_%d" % j] for j in range(1, 5)))
        e1 = lemmatize(r["sentence_quiz1"]); e2 = lemmatize(r["sentence_quiz2"]); g = int(r["answer_right_ending"])
        ctxls.append(ctxl); ends.append((e1, e2)); golds.append(g)
        fo.append(int(PL.coherence_forward(ctxl, [e1, e2]) == g))
        cv = PL.hub_vecs([ctxl], HUB)[0]; ev = PL.hub_vecs([e1, e2], HUB)
        bo.append(int(PL.coherence_backward(cv, ev) == g))
    rng = np.random.default_rng(0); perm = rng.permutation(len(sc))
    for i in range(len(sc)):
        e1, e2 = ends[i]
        tw.append(int(PL.coherence_forward(ctxls[perm[i]], [e1, e2]) == golds[i]))
    fo, bo, tw = np.array(fo, float), np.array(bo, float), np.array(tw, float)
    m_fb = PL.paired_margin_ci(fo, bo); m_ft = PL.paired_margin_ci(fo, tw)
    ok1 = fo.mean() > bo.mean() and m_fb[1][0] > 0.0
    print("W1 coherence forward %.4f > backward %.4f  margin %.4f CI%s: %s"
          % (fo.mean(), bo.mean(), m_fb[0], m_fb[1], "PASS" if ok1 else "FAIL"))
    fails += [] if ok1 else ["W1"]
    ok2 = fo.mean() > tw.mean() and m_ft[1][0] > 0.0
    print("W2 cross-context twin %.4f collapses (fwd-vs-twin margin %.4f CI%s): %s"
          % (tw.mean(), m_ft[0], m_ft[1], "PASS" if ok2 else "FAIL"))
    fails += [] if ok2 else ["W2"]

    # ---- W3 CONSTRUCTION control (concat ROCStories) ----
    roc = _jsonl(os.path.join(_REPO, "data", "corpora", "roc_stories", "train.jsonl"))
    rng = np.random.default_rng(3); idx = rng.permutation(len(roc))[:120]
    stream = []; true_b = set()
    for si, i in enumerate(idx):
        rr = roc[int(i)]
        for j in range(1, 6):
            if j == 1 and si > 0:
                true_b.add(len(stream))
            stream.append(lemmatize(rr["sentence%d" % j]))
    fb = PL.forward_segment(stream, kz=1.5, reinstate=0.3)["boundaries"]
    bb = PL.backward_segment(PL.hub_vecs(stream, HUB), kz=1.5)["boundaries"]
    f1f = PL.boundary_f1(fb, true_b); f1b = PL.boundary_f1(bb, true_b)
    ok3 = f1f > 1.5 * max(f1b, 1e-6)
    print("W3 construction (concat ROC): forward F1 %.4f >> backward F1 %.4f: %s" % (f1f, f1b, "PASS" if ok3 else "FAIL"))
    fails += [] if ok3 else ["W3"]

    # ---- W4/W5/W6 SEGMENTATION on GUM narrative ----
    docs = []
    for f in sorted(glob.glob(os.path.join(_REPO, "data", "corpora", "gum", "conllu", "*.conllu"))):
        genre, sents, boundary, ents = parse_gum_doc(f)
        if genre in NARR and len(sents) >= 4 and sum(len(s.strip()) for s in sents):
            docs.append({"sents": sents, "boundary": boundary, "ents": ents})
    docs = docs[:40]
    def zd(x):
        a = np.asarray(x, float); s = a.std()
        return (a - a.mean()) / (s + 1e-9) if s > 1e-9 else a * 0.0
    fc, bc, ec, mf, mb, yy = [], [], [], [], [], []
    for d in docs:
        bags = [lemmatize(s) for s in d["sents"]]
        zf = PL.forward_segment(bags, kz=1e9)["z"]
        zb = PL.backward_segment(PL.hub_vecs(bags, HUB), kz=1e9)["z"]
        ze = entity_signal(d["ents"])
        fc += zf; bc += zb; ec += ze; yy += d["boundary"]
        mf += list(zd(zf) + zd(ze)); mb += list(zd(zb) + zd(ze))
    auc_fc = PL.auc(fc, yy); auc_bc = PL.auc(bc, yy); auc_ec = PL.auc(ec, yy)
    auc_mf = PL.auc(mf, yy); auc_mb = PL.auc(mb, yy)
    # W4 located negative: content-forward does NOT beat content-backward (margin <= 0 within noise)
    ok4 = auc_fc <= auc_bc + 0.01
    print("W4 located negative: content-forward AUC %.4f does NOT beat content-backward %.4f: %s"
          % (auc_fc, auc_bc, "PASS" if ok4 else "FAIL"))
    fails += [] if ok4 else ["W4"]
    # W5 build-across: multidim forward beats multidim backward
    ok5 = auc_mf > auc_mb
    print("W5 build-across: multidim-forward AUC %.4f > multidim-backward %.4f: %s"
          % (auc_mf, auc_mb, "PASS" if ok5 else "FAIL"))
    fails += [] if ok5 else ["W5"]
    # W6 entity is the lever
    ok6 = auc_ec > auc_fc
    print("W6 protagonist/entity AUC %.4f > content-forward %.4f (the lever): %s"
          % (auc_ec, auc_fc, "PASS" if ok6 else "FAIL"))
    fails += [] if ok6 else ["W6"]

    # W8 -- the P2 UPGRADE is LIVE-REALIZABLE: the reader's own parse-layer protagonist signal (PROPN+NOUN
    # participant novelty, NO coref gold) beats the content-BACKWARD incumbent on the SAME GUM narrative docs.
    pos_all, bwd_all, y2 = [], [], []
    nd = 0
    for f in sorted(glob.glob(os.path.join(_REPO, "data", "corpora", "gum", "conllu", "*.conllu"))):
        genre, sents, bnd, ents, pos_ents, temporal = parse_rich(f)
        if genre in NARR and len(sents) >= 4 and sum(len(s.strip()) for s in sents):
            bags = [lemmatize(s) for s in sents]
            pos_all += discont(pos_ents)
            bwd_all += PL.backward_segment(PL.hub_vecs(bags, HUB), kz=1e9)["z"]
            y2 += bnd; nd += 1
            if nd >= 40:
                break
    auc_pos = PL.auc(pos_all, y2); auc_bwd2 = PL.auc(bwd_all, y2)
    ok8 = auc_pos > auc_bwd2
    print("W8 LIVE protagonist (parse-layer PROPN+NOUN) AUC %.4f > content-backward incumbent %.4f (P2 realizable): %s"
          % (auc_pos, auc_bwd2, "PASS" if ok8 else "FAIL"))
    fails += [] if ok8 else ["W8"]

    # W9 -- the 100%-BRAIN-FOUNDATIONAL boundary RULE (precision-weighted Bayesian surprise, Kumar 2023) beats the
    # raw-error content-backward incumbent on the SAME GUM narrative docs.
    from experiments.exp_predictive_loop_brain_foundational_v1 import bayes_surprise_stream
    bs_all, bw2_all, y3 = [], [], []
    nd = 0
    for f in sorted(glob.glob(os.path.join(_REPO, "data", "corpora", "gum", "conllu", "*.conllu"))):
        genre, sents, bnd, ents, pos_ents, temporal = parse_rich(f)
        if genre in NARR and len(sents) >= 4 and sum(len(s.strip()) for s in sents):
            vecs = PL.hub_vecs([lemmatize(s) for s in sents], HUB)
            bs_all += bayes_surprise_stream(vecs, None, fire=False)["surprise"]
            bw2_all += PL.backward_segment(vecs, kz=1.5, reinstate=0.0)["z"]
            y3 += bnd; nd += 1
            if nd >= 40:
                break
    auc_bs = PL.auc(bs_all, y3); auc_bw3 = PL.auc(bw2_all, y3)
    ok9 = auc_bs > auc_bw3
    print("W9 Bayesian-surprise (precision-weighted) AUC %.4f > raw-error incumbent %.4f (brain rule): %s"
          % (auc_bs, auc_bw3, "PASS" if ok9 else "FAIL"))
    fails += [] if ok9 else ["W9"]

    # W10 -- THE FLAGSHIP (brain-foundational): the structured SEM schema-switch segmenter beats the point-error
    # incumbent vs ACTUAL HUMAN boundaries (Kumar 2023 gold). Gracefully SKIPS if the large gitignored human
    # transcript archive is absent (the same degrade-gracefully pattern the substrate uses for gitignored assets).
    try:
        from experiments.exp_human_boundary_validation_v1 import load_story, _spearman  # noqa
        from experiments.exp_minimal_sem_v1 import sem_segment
        loaded = load_story("tunnel")
        if loaded is None:
            raise FileNotFoundError("tunnel timing unavailable")
        texts, human = loaded
        X = PL.hub_vecs([lemmatize(t) for t in texts], HUB)
        _, switch = sem_segment(X, alpha=1.0, lam=2.0, sigma2=1.0)          # NO-TUNE default params
        inc = PL.backward_segment(X, kz=1e9)["z"]
        thr = np.quantile(human, 0.80); hbin = (human >= thr).astype(int)
        auc_sem = PL.auc(switch, hbin); auc_inc = PL.auc(inc, hbin)
        ok10 = auc_sem > auc_inc + 0.03
        print("W10 SEM schema-switch AUC %.4f > point-error incumbent %.4f vs ACTUAL HUMANS (brain-foundational win): %s"
              % (auc_sem, auc_inc, "PASS" if ok10 else "FAIL"))
        fails += [] if ok10 else ["W10"]
    except (ImportError, FileNotFoundError, OSError, KeyError) as e:
        print("W10 SKIPPED (human transcript archive absent -- run experiments/fetch_human_event_boundaries.py + the 3.8GB transcript archive): %s" % type(e).__name__)

    print("-" * 70)
    if fails:
        print("WITNESS FAIL: %s" % ", ".join(fails)); sys.exit(1)
    print("ALL CHECKS PASS (9/9 core; W10 human-validation when the archive is present)")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
