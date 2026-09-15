"""Scaffold-free witness for seed_the_entity_world_model_resolver_with_a_world_knowledge_role_kinship_prior_phase1.

The identifiability wall is crossed by a brain-foundational CHAIN (owner directive: every component
brain-foundational): curated role/kinship KB (located-negative alone) + situation-model instance binding +
pronoun-into-entity resolution (Sanford-Garrod) + the reader's REAL per-text head-coreference. All four bar
clauses hold (floors recomputed per population).

C1  the full chain lifts hard-link resolution over the unseeded baseline (CI-sep).
C2  world-knowledge, not group-count: the shuffled-KB info-free twin LOSES on the hard links.
C3  located-negative made precise: the static KB alone covers only role-term epithets (~2%) but crushes them;
    the dominant general epithets need the situation model + reader coref.
C4  named-coref no-regress (not CI-sep negative).
C5  AGGREGATE common-noun coref rises CI-sep over surface_head, no-regress on named coref.
C6  the shared DOWNSTREAM (relational reference 'her father') rises CI-sep over surface_head + beats the twin.

Run: .venv/Scripts/python.exe verification/test_entitykb_resolver_v2.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np
from collections import defaultdict
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
from experiments.exp_commonnoun_linktype_decomposition_v1 import KINSHIP_ROLE  # noqa: F401
import experiments.exp_entitykb_resolver_v2 as R

N_DOCS = 40
WINDOW = 8
# The recommended deployable: the full brain-foundational chain (Step 3 = faithful reader head-coref).
FULL = dict(salience="composite", kb=True, repair=True, sitmodel=True, sitmodel_margin=1.0,
            attrs=True, pron_coref=True, use_reader_coref=True)
BASE = dict(salience="positional", kb=False, repair=False)
KBONLY = dict(salience="positional", kb=True, repair=False)


def _load():
    docs, gaz = DIAG.load_docs(N_DOCS)
    trips = [(d, ms, R.collect_ambig_pairs(ms, gaz, WINDOW)) for d, ms in docs]
    return docs, gaz, trips


def _acc(trips, gaz, kw):
    per = []
    for doc, ms, ps in trips:
        if not ps:
            continue
        lab = R.resolve_doc(doc, ms, gaz, window=WINDOW, **kw)
        per.append((sum(1 for (mi, ai, _c) in ps if lab.get(mi) == lab.get(ai)), len(ps)))
    return per


def _boot_delta(pa, pb, seed=20260905, nb=800):
    d = [(pa[i][0] - pb[i][0], pa[i][1]) for i in range(len(pa))]
    rng = np.random.default_rng(seed); idx = np.arange(len(d)); vals = []
    for _ in range(nb):
        s = rng.choice(idx, size=len(idx), replace=True)
        dc = sum(d[i][0] for i in s); nn = sum(d[i][1] for i in s)
        vals.append(dc / nn if nn else 0.0)
    mean = sum(x for x, _ in d) / sum(y for _, y in d)
    return mean, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def c1_c2(docs, gaz, trips):
    base = _acc(trips, gaz, BASE); full = _acc(trips, gaz, FULL)
    r2g_s, r2gen_s = R.shuffle_kb(20260905)
    twin = _acc(trips, gaz, dict(FULL, kb_maps=(r2g_s, r2gen_s)))
    accb = sum(x for x, _ in base) / sum(y for _, y in base)
    accf = sum(x for x, _ in full) / sum(y for _, y in full)
    d, lo, hi = _boot_delta(full, base)
    assert lo > 0, "C1 FAIL: chain not CI-sep over baseline (d=%.4f CI[%.4f,%.4f])" % (d, lo, hi)
    print("  C1 PASS: hard-link resolution %.4f -> %.4f  d=%+.4f CI[%+.4f,%+.4f] (%d docs)" % (accb, accf, d, lo, hi, N_DOCS))
    dt, tlo, thi = _boot_delta(full, twin)
    assert dt > 0, "C2 FAIL: shuffled-KB twin did not lose (d_vs_twin=%.4f)" % dt
    print("  C2 PASS: full chain beats shuffled-KB info-free twin (d=%+.4f CI[%+.4f,%+.4f]); world-knowledge" % (dt, tlo, thi))


def c3(docs, gaz, trips):
    def cat(kw):
        cc = {}
        for doc, ms, ps in trips:
            lab = R.resolve_doc(doc, ms, gaz, window=WINDOW, **kw)
            for (mi, ai, c) in ps:
                a = cc.setdefault(c, [0, 0]); a[1] += 1; a[0] += int(lab.get(mi) == lab.get(ai))
        return {k: (v[0] / v[1] if v[1] else 0.0, v[1]) for k, v in cc.items()}
    cb = cat(BASE); ck = cat(KBONLY); cf = cat(FULL)
    covb = cb.get("epithet_KBcoverable", (0, 0)); covk = ck.get("epithet_KBcoverable", (0, 0))
    othb = cb.get("epithet_other", (0, 0)); othf = cf.get("epithet_other", (0, 0))
    assert covk[0] > covb[0] + 0.10, "C3 FAIL: KB does not lift its coverable subset (%.3f->%.3f)" % (covb[0], covk[0])
    assert othf[0] > othb[0], "C3 FAIL: chain does not lift general epithets (%.3f->%.3f)" % (othb[0], othf[0])
    print("  C3 PASS: KB crushes its ~2%% subset (KBcoverable %.3f->%.3f) but general epithets (n=%d) need the "
          "situation model + reader coref (%.3f->%.3f)" % (covb[0], covk[0], othf[1], othb[0], othf[0]))


def c4(docs, gaz, trips):
    def named(kw):
        per = []
        for doc, ms, ps in trips:
            lab = R.resolve_doc(doc, ms, gaz, window=WINDOW, **kw)
            noms = [m for m in ms if not m["is_pronoun"] and DIAG.is_name(m, gaz)]
            if not noms:
                continue
            per.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
        return per
    d = LK.bootstrap_delta(named(FULL), named(BASE), 800)
    assert not (d["ci_sep"] and d["delta"] < 0), "C4 FAIL: named coref CI-sep REGRESSION (%.4f)" % d["delta"]
    print("  C4 PASS: named-coref no CI-sep regression (d=%+.4f CI[%+.4f,%+.4f])" % (d["delta"], d["lo"], d["hi"]))


def c5_aggregate(docs, gaz):
    _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    full = R._per_doc(docs, gaz, window=WINDOW, **FULL)
    d = LK.bootstrap_delta(full, sh, 800)
    assert d["ci_sep"] and d["delta"] > 0, "C5 FAIL: aggregate CoNLL not CI-sep (%.4f CI[%.4f,%.4f])" % (d["delta"], d["lo"], d["hi"])
    nb = R._per_doc_named(docs, gaz, window=WINDOW, **BASE); nf = R._per_doc_named(docs, gaz, window=WINDOW, **FULL)
    dn = LK.bootstrap_delta(nf, nb, 800)
    assert not (dn["ci_sep"] and dn["delta"] < 0), "C5 FAIL: named CI-sep regression (%.4f)" % dn["delta"]
    print("  C5 PASS: aggregate common-noun CoNLL %+.4f CI[%+.4f,%+.4f] CI-sep over surface_head; named no-regress (%+.4f)"
          % (d["delta"], d["lo"], d["hi"], dn["delta"]))


def c6_downstream(docs, gaz):
    POSS = {"his", "her", "their", "my", "your"}
    def relpairs(ms):
        prior = defaultdict(list); out = []
        for m in sorted(ms, key=lambda x: x["midx"]):
            if m["is_pronoun"]:
                continue
            span = [w.lower() for w in m.get("span_toks", [m["head"]])]; hl = R.head_lemma(m["head"])
            if span and span[0] in POSS and hl in R.ROLE_SET and prior.get(m["cluster"]):
                out.append((m["midx"], prior[m["cluster"]][-1]["midx"]))
            prior[m["cluster"]].append(m)
        return out
    rp = [(d, ms, relpairs(ms)) for d, ms in docs]
    def acc(kw, labels_fn=None):
        per = []
        for doc, ms, ps in rp:
            if not ps:
                continue
            lab = labels_fn(doc, ms) if labels_fn else R.resolve_doc(doc, ms, gaz, window=WINDOW, **kw)
            per.append((sum(1 for (mi, ai) in ps if lab.get(mi) == lab.get(ai)), len(ps)))
        return per
    full = acc(FULL); surf = acc(None, lambda doc, ms: DIAG.cluster_labels(ms, gaz, "surface_head"))
    d, lo, hi = _boot_delta(full, surf)
    assert lo > 0, "C6 FAIL: relational-reference downstream not CI-sep over surface_head (d=%.4f CI[%.4f,%.4f])" % (d, lo, hi)
    print("  C6 PASS: DOWNSTREAM relational-reference rises %+.4f CI[%+.4f,%+.4f] CI-sep over surface_head" % (d, lo, hi))


if __name__ == "__main__":
    print("witness: entity-world-model resolver crosses via KB + situation-model + pronoun-into-entity + reader head-coref")
    docs, gaz, trips = _load()
    npairs = sum(len(p) for _d, _m, p in trips)
    print("  (%d docs, %d hard ambiguous links)" % (N_DOCS, npairs))
    c1_c2(docs, gaz, trips)
    c3(docs, gaz, trips)
    c4(docs, gaz, trips)
    c5_aggregate(docs, gaz)
    c6_downstream(docs, gaz)
    print("ALL CHECKS PASS (6/6)")


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
