"""LANDING witness: the by-phrase CASE-MORPHOLOGY AGENT cue (byhead) is WIRED default-on into the LIVE reader.

Landed 2026-09-06 from the owner-DONE
`grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads`. On a NON-CANONICAL /
passive clause ("the mineral was formed by a natural PROCESS") word order misleads and the reader mis-picks the
agent (the surface subject); the fix is a by-phrase CASE cue -- reward the candidate GOVERNED by the passive-
agent preposition "by" through its NP (hdlab.graded_role_assigner.by_governs), gated by the participle+by-PP
CONSTRUCTION detector (participle_bypp_gate), added as ONE additive Competition-Model cue
(AGENT_VALIDITIES["byhead"]=BYHEAD_W=10.0, OUTVOTABLE). Unlike the SOLVER witnesses
(test_noncanonical_agent_bymorph_organ.py / test_cmrole_agent_board_byhead_organ.py, which prove the experiment
impl), this witness exercises the LANDED substrate directly:
  - hdlab.graded_role_assigner.agent_supports/agent_competition_pick (the promoted byhead cue), and
  - hdlab.situation_reader.SituationReader.cm_agent_byhead (the live default-on flag; OFF => exact incumbent).

W1  LIVE WIRE + default-on: the default reader has cm_agent_byhead True (all_capabilities_off => False); on a
    by-agent passive the reader's own AGENT pick (_cm_agent_for) resolves to the by-NP agent with byhead ON and
    to the incumbent surface-subject with byhead OFF -- the flag is live and decisive.
W2  POWERED WIN (MODERN QA-SRL, 19c-clean) reproduced THROUGH THE LANDED hdlab organ: byhead ON beats the
    live-competition floor (byhead OFF) AND the info-free by-membership-shuffled twin, CI-separated, on the clean
    agent-post slice (~0.2556 -> ~0.6889, n=90) and the full non-canonical slice (~0.5224 -> ~0.6866, n=201);
    per-row byte-identical to the validated experiment byhead arm.
W3  ADDITIVE-SAFETY: canonical QA-SRL no-regress (n=845, ~0.696 unchanged, self-gated); the live 19c LitBank
    board is near-byte-identical (byhead self-gates to the participle+by-PP construction, which LitBank's
    syntactic-subject WDW gold barely contains -- it changes a negligible fraction of answers, |delta| small).

Run: .venv/Scripts/python.exe verification/test_byhead_agent_cue_landing.py
"""
from __future__ import annotations
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import json

import numpy as np

import experiments.exp_situation_model_qa_v1 as SITQA
import experiments.exp_noncanonical_agent_bymorph_v1 as M
import experiments.exp_grounded_selfit_role_cue_v1 as G
from hdlab.situation_reader import SituationReader
from hdlab.graded_role_assigner import (
    agent_supports, agent_competition_pick, AGENT_VALIDITIES, BYHEAD_W, participle_bypp_gate,
)
from hdlab.graded_competition import net_activation
from hdlab.incremental_parser import incremental_subject_before

_PASS = []
NOMINAL = {"NOUN", "PROPN", "PRON"}


def _ok(name, cond, detail=""):
    _PASS.append(bool(cond))
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("  -- " + detail) if detail else ""))


# --------------------------------------------------------------------------- W1: live wire + default-on
def w1_live_wire():
    print("W1. LIVE WIRE + default-on (SituationReader.cm_agent_byhead)")
    gaz = SITQA.load_given_gazetteer()
    r_on = SituationReader(gaz=gaz)                               # default reader
    r_off = SituationReader(gaz=gaz, cm_agent_byhead=False)       # explicit incumbent
    _ok("default reader has byhead ON", r_on.cm_agent_byhead is True)
    _ok("all_capabilities_off has byhead OFF (incumbent reachable)",
        SituationReader.all_capabilities_off(gaz=gaz).cm_agent_byhead is False)

    # a by-agent passive with an INANIMATE agent + a competing surface subject: word order + animacy mislead,
    # only the by-phrase morphology identifies the agent. The reader's own AGENT pick must flip ON vs OFF.
    toks = ["the", "mineral", "was", "formed", "by", "a", "natural", "process", "."]
    v0 = 3
    anoms = [{"wtok_start": 1, "head": "mineral", "cluster": None, "is_pronoun": False},
             {"wtok_start": 7, "head": "process", "cluster": None, "is_pronoun": False}]
    a_on = r_on._cm_agent_for(toks, [anoms], {}, 0, v0)
    a_off = r_off._cm_agent_for(toks, [anoms], {}, 0, v0)
    print("    '%s'  ON=%s  OFF=%s" % (" ".join(toks), a_on, a_off))
    _ok("byhead ON resolves to the by-NP agent ('process')", a_on == "process", "ON=%s" % a_on)
    _ok("byhead OFF keeps the incumbent surface subject ('mineral')", a_off == "mineral", "OFF=%s" % a_off)
    _ok("the flag CHANGES the live reader pick", a_on != a_off, "%s vs %s" % (a_on, a_off))


# --------------------------------------------------------------------------- W2/W3a: QA-SRL through hdlab
def _cands(toks, pos, v):
    return [i for i in range(len(pos)) if pos[i] in NOMINAL and i != v]


def _pick_hdlab(toks, pos, v, cand_idxs, subj_before, byhead, by_twin_seed=None):
    """The LANDED hdlab AGENT competition over the same clause-nominal candidate set + scoring convention as the
    validated experiment (returns the winner TOKEN INDEX). byhead routes through the landed agent_supports flag
    + AGENT_VALIDITIES['byhead']. by_twin_seed => shuffle ONLY the byhead support (info-free by-membership twin)."""
    if not cand_idxs:
        return None
    c = [(i, toks[i].lower(), None, i) for i in cand_idxs]
    S = agent_supports(toks, pos, v, c, gaz=None, cluster_freq=None, subj_before=subj_before,
                       byhead_agent_cue=byhead)
    if by_twin_seed is not None and "byhead" in S:
        rng = np.random.default_rng(by_twin_seed + v + len(c))
        S["byhead"] = list(np.asarray(S["byhead"])[rng.permutation(len(S["byhead"]))])
    A = net_activation(S, AGENT_VALIDITIES)
    return c[int(np.argmax(A))][0]


def _qasrl_slices():
    rows = [r for r in G.load_rows() if r.get("agent")]
    key = [tuple(r["toks"]) for r in rows]
    uniq = sorted(set(key))
    rng = np.random.default_rng(M.SEED)
    perm = rng.permutation(len(uniq))
    tr = {uniq[i] for i in perm[: int(0.7 * len(uniq))]}
    test = [r for r, k in zip(rows, key) if k not in tr]

    def agent_post(r):
        v = r["verb_idx"]; g = M.span_set(r["agent"])
        return bool(g) and all(i > v for i in g)

    return {"clean_agent_post": [r for r in test if agent_post(r)],
            "non_canonical": [r for r in test if r.get("voice") == "passive"],
            "canonical": [r for r in test if r.get("voice") == "active"]}


def _score(rows, fn, subj_cache):
    def subj(t, p):
        k = tuple(t)
        if k not in subj_cache:
            subj_cache[k] = incremental_subject_before(t, p)
        return subj_cache[k]
    out = []
    for r in rows:
        t, p, v = r["toks"], r["pos"], r["verb_idx"]
        g = M.span_set(r["agent"])
        if not g or not (0 <= v < len(t)):
            continue
        pk = fn(r, t, p, v, subj(t, p))
        out.append(int(pk is not None and pk in g))
    return np.array(out, float)


def w2_w3a_qasrl():
    print("\nW2. POWERED WIN reproduced through the LANDED hdlab organ (MODERN QA-SRL, 19c-clean)")
    sl = _qasrl_slices()
    sc = {}
    off = lambda r, t, p, v, sb: _pick_hdlab(t, p, v, _cands(t, p, v), sb, False)
    on = lambda r, t, p, v, sb: _pick_hdlab(t, p, v, _cands(t, p, v), sb, True)
    twin = lambda r, t, p, v, sb: _pick_hdlab(t, p, v, _cands(t, p, v), sb, True, by_twin_seed=13)
    exp_on = lambda r, t, p, v, sb: M.pick(t, p, v, _cands(t, p, v), sb, byhead_w=BYHEAD_W)

    # -- clean agent-post slice (positional/incumbent NECESSARILY wrong) --
    ap = sl["clean_agent_post"]
    ap_off = _score(ap, off, sc); ap_on = _score(ap, on, sc)
    ap_twin = _score(ap, twin, sc); ap_exp = _score(ap, exp_on, sc)
    b_off = M._boot(ap_on, ap_off); b_twin = M._boot(ap_on, ap_twin)
    print("    clean agent-post n=%d: OFF(incumbent)=%.4f  byhead_ON=%.4f  twin=%.4f  [exp byhead=%.4f]"
          % (len(ap_on), ap_off.mean(), ap_on.mean(), ap_twin.mean(), ap_exp.mean()))
    print("      byhead vs OFF %s | byhead vs twin %s" % (b_off, b_twin))
    _ok("byhead ON CI-beats the live-competition floor on the clean slice", b_off["sep"], str(b_off))
    _ok("byhead ON lift on the clean slice is large (> +0.20)", ap_on.mean() > ap_off.mean() + 0.20,
        "%.4f -> %.4f" % (ap_off.mean(), ap_on.mean()))
    _ok("byhead ON CI-beats the info-free by-membership twin", b_twin["sep"], str(b_twin))
    _ok("landed hdlab byhead == validated experiment byhead PER-ROW (byte-faithful)",
        np.array_equal(ap_on, ap_exp))

    # -- full non-canonical slice --
    nc = sl["non_canonical"]
    nc_off = _score(nc, off, sc); nc_on = _score(nc, on, sc)
    b_nc = M._boot(nc_on, nc_off)
    print("    full non-canonical n=%d: OFF=%.4f  byhead_ON=%.4f  vs_OFF %s"
          % (len(nc_on), nc_off.mean(), nc_on.mean(), b_nc))
    _ok("byhead ON CI-beats the floor on the full non-canonical slice", b_nc["sep"], str(b_nc))
    _ok("byhead ON lift on the full non-canonical slice (> +0.10)", nc_on.mean() > nc_off.mean() + 0.10,
        "%.4f -> %.4f" % (nc_off.mean(), nc_on.mean()))

    # -- W3a: canonical no-regress (self-gated OFF where the construction is absent) --
    print("\nW3a. ADDITIVE-SAFETY: canonical QA-SRL no-regress (byhead self-gates)")
    cn = sl["canonical"]
    cn_off = _score(cn, off, sc); cn_on = _score(cn, on, sc)
    b_cn = M._boot(cn_on, cn_off)
    print("    canonical n=%d: OFF=%.4f  byhead_ON=%.4f  vs_OFF %s" % (len(cn_on), cn_off.mean(), cn_on.mean(), b_cn))
    _ok("byhead does NOT CI-regress canonical (hi >= -0.005)", b_cn["hi"] >= -0.005, str(b_cn))
    _ok("canonical accuracy is essentially unchanged (drop < 0.005)", cn_on.mean() >= cn_off.mean() - 0.005,
        "%.4f -> %.4f" % (cn_off.mean(), cn_on.mean()))


# --------------------------------------------------------------------------- W3b: live board additive-safety
def w3b_board():
    print("\nW3b. ADDITIVE-SAFETY: live 19c LitBank board (byhead self-gates to the by-PP construction)")
    gaz = SITQA.load_given_gazetteer()
    wdw = {r["doc"]: r for r in json.load(open(SITQA.WDW_GOLD, encoding="utf-8"))}
    docs = SITQA.load_docs(8)
    ds = [d for d in docs if d in wdw and os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll"))]

    def collect(reader):
        rows = []
        for doc in ds:
            sm = reader.read(os.path.join(SITQA.CONLL_DIR, doc + ".conll"))
            qa = SITQA.SituationQA(sm)
            prev = SITQA.ANSWER_INSTANCED
            SITQA.ANSWER_INSTANCED = False
            try:
                for q in SITQA.build_events_questions(sm, wdw[doc]):
                    _d, a = qa.answer(q["question"], q)
                    rows.append((str(a), int(SITQA._match(a, q["gold"], "events"))))
            finally:
                SITQA.ANSWER_INSTANCED = prev
        return rows

    on = collect(SituationReader(gaz=gaz))
    off = collect(SituationReader(gaz=gaz, cm_agent_byhead=False))
    n = len(on)
    oc = np.array([x[1] for x in on], float); fc = np.array([x[1] for x in off], float)
    changed = sum(1 for i in range(n) if on[i][0] != off[i][0])
    delta = float(oc.mean() - fc.mean())
    print("    %d docs, n_q=%d: acc ON=%.4f OFF=%.4f  delta=%+.4f  answers changed=%d"
          % (len(ds), n, oc.mean(), fc.mean(), delta, changed))
    # byhead self-gates to the participle+by-PP construction, which LitBank's syntactic-subject WDW gold barely
    # contains -> it changes only a NEGLIGIBLE fraction of board answers (the powered win is on QA-SRL, W2). This
    # is an additive-safety bound, NOT a positive-lift claim: the honest sign of the tiny delta is printed above.
    _ok("byhead changes only a negligible fraction of board answers (<= ~1%%)", changed <= max(4, n // 100),
        "changed=%d / %d" % (changed, n))
    _ok("byhead does not MATERIALLY move the 19c board (|delta| < 0.01)", abs(delta) < 0.01,
        "delta=%+.4f" % delta)


def main():
    print("witness: byhead case-morphology AGENT cue wired default-on into the live who-did-what competition\n")
    w1_live_wire()
    w2_w3a_qasrl()
    w3b_board()
    n = len(_PASS); k = sum(_PASS)
    print("\n%d/%d PASS" % (k, n))
    return 0 if k == n else 1


if __name__ == "__main__":
    sys.exit(main())
