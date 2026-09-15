"""Scaffold-free witness for `predictive_inference_forward_project_the_next_event_and_state...`.
Recomputes every headline claim FROM SOURCE (the cached Story Cloze gold + ROCStories store), not
from any landed metrics.json. Runs with tracing off; NO LLM. Bounded (30k store, val split) so it
completes in ~1-2 min while asserting the SAME qualitative claims as the full cell.

W0  gold + store load; class balance ~50/50 (a real can-fail instrument, not majority-solvable)
W1  POSITIVE: forward GEK projection beats the majority-continuation floor CI-separated
W2  TWIN: cross-context (random other story's context) collapses toward chance (info-free loses)
W3  PRECISION: selective accuracy on the most-confident quartile RISES above all-items accuracy
W4  LOCATED NEGATIVE (SR): multi-step forward horizon does NOT robustly beat the 1-step co-occurrence counter
W5  LOCATED NEGATIVE (grain): event-structured verb-chain GEK does NOT beat the content-bag GEK
W6  LOCATED NEGATIVE (extraction): the live situation model's GOAL/CAUSAL registers fire on <40% of stories
W7  ABSENCE: nothing in hdlab forward-projects a NEXT EVENT/STATE from the situation model
Run: .venv/Scripts/python.exe verification/test_forward_event_projection.py
"""
from __future__ import annotations
import os, re, sys, tempfile
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np
from collections import Counter
from datasets import load_dataset
from experiments.exp_forward_event_projection_v1 import (
    _lemmas_factory, build_store, make_scorer, boot_ci, boot_margin, selective_curve, precision_of)

PASS = []; FAIL = []
def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print("  [%s] %s %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    lemmas = _lemmas_factory()
    roc = load_dataset("wza/roc_stories")["train"]
    S = build_store(roc, lemmas, n_store=30000, seed=0)
    gek = make_scorer(S, "fwd"); sym = make_scorer(S, "sym")
    sc = load_dataset("MoE-UNC/story_cloze")["validation"]
    n = len(sc)
    items = []
    for k in range(n):
        r = sc[k]
        ctx = []
        for j in range(1, 5):
            ctx += lemmas(r["input_sentence_%d" % j])
        items.append((ctx, lemmas(r["sentence_quiz1"]), lemmas(r["sentence_quiz2"]),
                      int(r["answer_right_ending"])))

    # ---- W0 gold + balance
    labels = [it[3] for it in items]
    bal = Counter(labels); maj = max(bal.values()) / n
    check("W0_gold_loads_and_balanced", n == 1871 and maj < 0.55,
          "n=%d majority-class=%.3f" % (n, maj))

    # ---- forward GEK mechanism, 1-step symmetric counter floor, cross-context twin
    def corr(scorer, ctx_of):
        c, p = [], []
        for k, (ctx, e1, e2, g) in enumerate(items):
            cc = ctx_of(k, ctx); s1, s2 = scorer(cc, e1), scorer(cc, e2)
            c.append(int((1 if s1 >= s2 else 2) == g)); p.append(precision_of(s1, s2))
        return np.array(c, float), np.array(p, float)
    same = lambda k, ctx: ctx
    twin = lambda k, ctx: items[(k + 971) % n][0]
    fwd_c, fwd_p = corr(gek, same)
    sym_c, _ = corr(sym, same)
    twin_c, _ = corr(gek, twin)
    maj_label = bal.most_common(1)[0][0]
    maj_c = np.array([int(l == maj_label) for l in labels], float)

    # ---- W1 mechanism beats majority floor CI-separated
    m = boot_margin(fwd_c, maj_c)
    check("W1_forward_beats_majority_floor_CI_sep", m["ci"][0] > 0,
          "acc=%.4f vs majority=%.4f margin=%s" % (fwd_c.mean(), maj_c.mean(), m))

    # ---- W2 cross-context twin collapses toward chance
    tw = boot_ci(twin_c)
    check("W2_cross_context_twin_collapses", tw[0] < fwd_c.mean() - 0.04 and tw[1][0] <= 0.52,
          "twin acc=%.4f CI=%s vs mechanism %.4f" % (tw[0], tw[1], fwd_c.mean()))

    # ---- W3 selective accuracy rises with precision
    sel = selective_curve(fwd_c, fwd_p)
    check("W3_selective_accuracy_rises", sel["0.25"] > sel["1.0"] + 0.01,
          "acc@100%%=%.4f -> acc@25%%=%.4f" % (sel["1.0"], sel["0.25"]))

    # ---- W4 located negative: multi-step horizon does not robustly beat the 1-step counter
    mh = boot_margin(fwd_c, sym_c)
    check("W4_horizon_ties_1step_counter", (mh["ci"][0] <= 0.0) or (mh["d"] < 0.03),
          "forward=%.4f 1step-sym=%.4f margin=%s (SR pre-registered outcome)" % (fwd_c.mean(), sym_c.mean(), mh))

    # ---- W5 located negative: event-structured verb-chain GEK is not better than content GEK
    from nltk.corpus import wordnet as wn
    from hdlab.pos_tagger import PosTagger
    POS = PosTagger.load(os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    _vc = {}
    def vlem(w):
        w = w.lower()
        if w not in _vc: _vc[w] = wn.morphy(w, wn.VERB) or w
        return _vc[w]
    def tok(s): return re.findall(r"[A-Za-z]+|[0-9]+|[^\sA-Za-z0-9]", s)
    from collections import defaultdict
    import math
    rng = np.random.default_rng(0); idx = rng.permutation(len(roc))[:15000]
    vf = defaultdict(Counter); vs = Counter(); vt = Counter(); vtot = 0
    for i in idx:
        r = roc[int(i)]; vbags = []
        for j in range(1, 6):
            tks = tok(r["sentence%d" % j]); up = POS.tag(tks)
            vbags.append(sorted({vlem(tks[t]) for t in range(len(tks)) if up[t] == "VERB" and tks[t].isalpha()}))
        for a in range(len(vbags)):
            for b in range(a + 1, len(vbags)):
                for x in vbags[a]:
                    for y in vbags[b]:
                        vf[x][y] += 1; vs[x] += 1; vt[y] += 1; vtot += 1
    vtot = float(vtot)
    def vppmi(a, c):
        j = vf.get(a, {}).get(c, 0)
        return 0.0 if j == 0 else max(0.0, math.log((j / vtot) / ((vs[a] / vtot) * (vt[c] / vtot) + 1e-12) + 1e-12))
    vc_c = []
    for k in range(n):
        r = sc[k]
        cv = []
        for j in range(1, 5):
            tks = tok(r["input_sentence_%d" % j]); up = POS.tag(tks)
            cv += [vlem(tks[t]) for t in range(len(tks)) if up[t] == "VERB" and tks[t].isalpha()]
        def vsc(qk):
            tks = tok(r[qk]); up = POS.tag(tks)
            ev = [vlem(tks[t]) for t in range(len(tks)) if up[t] == "VERB" and tks[t].isalpha()]
            return (sum(sum(vppmi(a, e) for a in cv) for e in ev) / len(ev)) if ev else 0.0
        s1, s2 = vsc("sentence_quiz1"), vsc("sentence_quiz2")
        vc_c.append(int((1 if s1 >= s2 else 2) == int(r["answer_right_ending"])))
    vc_c = np.array(vc_c, float)
    check("W5_event_structure_not_better_than_content", vc_c.mean() <= fwd_c.mean() + 0.005,
          "verb-chain=%.4f vs content-GEK=%.4f (finer hub does NOT help on discourse continuation)" % (vc_c.mean(), fwd_c.mean()))

    # ---- W6 located negative: live situation-model goal/causal registers fire on <40% of stories
    from hdlab.situation_reader import SituationReader
    reader = SituationReader(role_route="wired")
    NOMINAL = {"NOUN", "PROPN", "PRON"}
    def conll(sentences):
        fd, path = tempfile.mkstemp(suffix=".conll", text=True); cid = 0
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for si, s in enumerate(sentences):
                tks = tok(s); up = POS.tag(tks)
                for i2, tk in enumerate(tks):
                    cf = "(%d)" % cid if up[i2] in NOMINAL else "_"
                    if up[i2] in NOMINAL: cid += 1
                    f.write("\t".join([str(si), "0", str(i2), tk] + ["_"] * 7 + [cf]) + "\n")
                f.write("\n")
        return path
    NF = 40; goal_fire = causal_fire = 0; ok = 0
    for k in range(NF):
        r = sc[k]; path = conll([r["input_sentence_%d" % j] for j in range(1, 5)])
        try:
            sm = reader.read(path); ok += 1
        except Exception:
            os.remove(path); continue
        os.remove(path)
        if getattr(sm, "causal_links", None): causal_fire += 1
        ags = {str(e.agent).lower() for e in sm.events if str(e.agent) not in ("?", "")}
        if any((lambda w: bool(w))(_safe_wants(sm, a)) for a in ags): goal_fire += 1
    check("W6_registers_fire_sparsely", goal_fire / ok < 0.4 and causal_fire / ok < 0.4,
          "goal_fire=%d/%d causal_fire=%d/%d (structure too sparse to drive projection)" % (goal_fire, ok, causal_fire, ok))

    # ---- W7 absence: nothing forward-projects a next event/state from sm
    import subprocess
    hits = []
    for pat in ("def predict_next_event", "def forward_project", "def what_happens_next", "def project_next_event"):
        r = subprocess.run(["grep", "-rl", pat, os.path.join(_REPO, "hdlab")], capture_output=True, text=True)
        if r.stdout.strip():
            hits.append(pat)
    check("W7_absence_no_forward_event_projector", not hits,
          "no next-EVENT/state forward projector in hdlab (found: %s)" % (hits or "none"))

    print("\n%d/%d PASS" % (len(PASS), len(PASS) + len(FAIL)))
    if FAIL:
        print("FAILURES:", FAIL); sys.exit(1)
    sys.exit(0)


def _safe_wants(sm, agent):
    try:
        return sm.wants(agent)
    except Exception:
        return None


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.slow
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
