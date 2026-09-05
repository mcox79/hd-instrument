"""LANDING WITNESS: the deployable situation-gated common-noun former + the canonicalizer wiring, as LANDED
in hdlab (hdlab/commonnoun_binder.py + hdlab/goal_register.make_canonicalizer(commonnoun_canonical=)).

Problem: form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref (Q111, §5).
This asserts the LANDED ORGAN (not the experiments cell) delivers the owner-DONE win:
  (a) THE LANDABLE WIN: the LANDED former hdlab.commonnoun_binder.situation_predict(headmatch_gate=True,
      window=16) reproduces the +0.0128 CoNLL win over surface_head on the SOLVED's population (LitBank gold
      coref, 100 docs, CoNLL avg of MUC/B3/CEAFe, character-cluster population), CI-separated.
  (b) VERBATIM: the LANDED former is byte-identical to the experiments former (labels equal on the sample).
  (c) NO-REGRESS on NAMED coref: the LANDED former's clustering of NAME mentions is byte-stable vs the
      proper-name-centric name_only baseline (names route through the same EntityAliaser; former on == off).
  (d) THE WIRING LEVER (commonnoun_canonical): make_canonicalizer now consumes common-noun clusters -- a
      common-noun-only character binds where the proper-name-centric canonicalizer previously ABSTAINED --
      while OFF stays byte-identical and proper names still bind.

The scoring harness (CoNLL metrics + doc-bootstrap) is REUSED from the experiments cells (metric math, not the
organ); the ORGAN under test is hdlab. Glass-box, NO LLM. Writes nothing. ASCII.
Run: .venv/Scripts/python.exe verification/test_commonnoun_coref_landing_organ.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# the LANDED organ under test
import hdlab.commonnoun_binder as CN
from hdlab.goal_register import make_canonicalizer
from hdlab.situation_reader import SituationModel, TrackedEntity

# scoring harness (metric math only) + the experiments former (for the byte-identity check)
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
import experiments.exp_commonnoun_situation_gated_binder_v1 as SB

N_DOCS = 100        # the SOLVED's population
N_BOOT = 1000


def _landed_char_stats(docs, gaz, window=16):
    """Per-doc CoNLL sufficient-stats for the LANDED deployable former on the CHARACTER-cluster population."""
    st = []
    for _doc, ms in docs:
        lab = CN.situation_predict(ms, gaz, window=window, headmatch_gate=True)
        chars = LK._char_clusters(ms)
        noms = [m for m in ms if not m["is_pronoun"] and m["cluster"] in chars]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def _landed_name_stats(docs, gaz, window=16):
    """Per-doc CoNLL stats for the LANDED former restricted to NAME mentions (the no-regress-on-named pop)."""
    st = []
    for _doc, ms in docs:
        lab = CN.situation_predict(ms, gaz, window=window, headmatch_gate=True)
        noms = [m for m in ms if not m["is_pronoun"] and DIAG.is_name(m, gaz)]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def _name_only_name_stats(docs, gaz):
    """Per-doc CoNLL stats for the proper-name-centric name_only baseline on the NAME subpopulation."""
    st = []
    for _doc, ms in docs:
        lab = DIAG.cluster_labels(ms, gaz, "name_only")
        noms = [m for m in ms if not m["is_pronoun"] and DIAG.is_name(m, gaz)]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def main():
    checks = []
    docs, gaz = DIAG.load_docs(N_DOCS)

    # (a) THE LANDABLE WIN: landed former BEATS surface_head CI-sep on character clusters (~+0.0128).
    _all, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    best = _landed_char_stats(docs, gaz, window=16)
    d_best = LK.bootstrap_delta(best, sh, N_BOOT)
    sh_conll = LK._conll_from_stats(sh)["conll_avg"]
    best_conll = LK._conll_from_stats(best)["conll_avg"]
    checks.append((
        "(a) LANDED former BEATS surface_head CI-sep on char clusters (reproduces the +0.0128 win)",
        d_best["ci_sep"] and d_best["delta"] > 0 and 0.005 <= d_best["delta"] <= 0.025,
        "surface_head %.4f -> landed %.4f ; delta %+.4f CI[%+.4f,%+.4f]"
        % (sh_conll, best_conll, d_best["delta"], d_best["lo"], d_best["hi"])))

    # (b) VERBATIM: landed former == experiments former (byte-identical labels on the sample).
    identical = True
    for _doc, ms in docs[:20]:
        if CN.situation_predict(ms, gaz, window=16, headmatch_gate=True) \
                != SB.situation_predict(ms, gaz, window=16, headmatch_gate=True):
            identical = False
            break
    checks.append(("(b) LANDED former == experiments former (verbatim promotion, byte-identical labels)",
                   identical, "labels equal on 20 docs" if identical else "LABELS DIVERGED"))

    # (c) NO-REGRESS on NAMED coref: the landed former's NAME-mention clustering is byte-stable vs name_only.
    ln = _landed_name_stats(docs, gaz, window=16)
    no = _name_only_name_stats(docs, gaz)
    ln_conll = LK._conll_from_stats(ln)["conll_avg"]
    no_conll = LK._conll_from_stats(no)["conll_avg"]
    d_name = LK.bootstrap_delta(ln, no, N_BOOT)
    byte_stable = abs(ln_conll - no_conll) < 1e-9
    no_regress = not (d_name["ci_sep"] and d_name["delta"] < 0)
    checks.append(("(c) NO-REGRESS on NAMED coref: landed former's name-subpop clustering byte-stable vs name_only",
                   byte_stable and no_regress,
                   "name-subpop CoNLL former %.6f == name_only %.6f (delta %+.4f)"
                   % (ln_conll, no_conll, d_name["delta"])))

    # (d) THE WIRING LEVER: make_canonicalizer(commonnoun_canonical=True) binds a common-noun-only character
    #     where the proper-name-centric canonicalizer (OFF) ABSTAINS; OFF stays byte-identical; names still bind.
    sm = SituationModel(passage_id="w", n_sentences=2)
    sm.entities = [
        TrackedEntity(cluster="CN:R7", heads=["the man", "men"], sent_indices=[0, 1], n_mentions=3, is_person=True),
        TrackedEntity(cluster=0, heads=["John"], sent_indices=[0], n_mentions=2, is_person=True),
    ]
    sm.coref_resolutions = []
    canon_off, _ = make_canonicalizer(sm, commonnoun_canonical=False)
    canon_on, _ = make_canonicalizer(sm, commonnoun_canonical=True)
    off_abstains = (canon_off("man", 1) is None)          # head-only query: OFF abstains on the common noun
    on_binds = (canon_on("man", 1) is not None)           # ON binds 'man' -> the tracked man cluster
    off_name_ok = (canon_off("John", 0) is not None)      # OFF still binds the proper name (byte-identical base)
    on_name_ok = (canon_on("John", 0) is not None)        # ON does not regress the proper name
    checks.append(("(d) WIRING: commonnoun_canonical binds a common-noun-only character where OFF abstains "
                   "(names + OFF-base unchanged)",
                   off_abstains and on_binds and off_name_ok and on_name_ok,
                   "OFF canon('man')=%r  ON canon('man')=%r  OFF canon('John')=%r"
                   % (canon_off("man", 1), canon_on("man", 1), canon_off("John", 0))))

    npass = 0
    print("=" * 92)
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("%d/%d checks passed  (%d docs, %d bootstrap)" % (npass, len(checks), N_DOCS, N_BOOT))
    print("=" * 92)
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
