"""WITNESS: the common-noun discourse-referent former -- the located negative + the reframe, scaffold-free.

Problem: form_a_discourse_referent_for_every_entity_not_just_named_ones_common_noun_coref.

The brief proposed a glass-box common-noun descriptive-content referent former to recover the +0.43
gold-coref headroom. On LitBank gold coref (proper CoNLL MUC/B3/CEAFe, doc-level bootstrap) this witness
asserts what the disk shows:
  (1) THE BARRIER IS REAL: head-match recall <= 0.45 (most literary common-noun links do NOT share a
      head lemma) AND the over-merge errors are >= 0.8 content-IDENTICAL (not separable by any surface cue).
  (2) FORMING A REFERENT FOR EVERY COMMON NOUN HELPS (the reframe / positive sub-finding): the reader's
      surface-head grouping beats the proper-name-centric baseline (name_only) CI-separated on the
      character-cluster population -- the recovery is real and ALREADY in the reader's clustering.
  (3) THE LOCATED NEGATIVE: the FAITHFUL cue-based accessibility former (ACT-R retrieval extended from
      pronouns to definite descriptions, reusing the graded_coref_pick op) does NOT beat surface_head
      CI-separated at the untuned window -- the descriptive-content former is capped; no variant
      approaches the headroom (best swept delta << the name_only->surface_head recovery).
  (4) INFO-FREE TWIN LOSES: the former beats its within-doc label-permuted twin CI-separated.
  (5) NO-REGRESS ON NAMED coref: on the NAME-mention subpopulation the former does not fall below
      name_only CI-separated (names go through the same landed EntityAliaser).

Run: .venv/Scripts/python.exe verification/test_commonnoun_referent_former.py
Glass-box, NO LLM. Writes nothing. ASCII.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK

N_DOCS = 40
N_BOOT = 400


def _name_subpop_stats(docs, gaz, arm, window=6):
    """CoNLL sufficient-stats on the NAME-mention subpopulation (no-regress-on-named check)."""
    st = []
    for di, (doc, ms) in enumerate(docs):
        lab = LK.predicted_for_arm(ms, gaz, arm, window)
        noms = [m for m in ms if not m["is_pronoun"] and DIAG.is_name(m, gaz)]
        st.append(LK._doc_stats([lab[m["midx"]] for m in noms], ["g%d" % m["cluster"] for m in noms]))
    return st


def main():
    checks = []
    docs, gaz = DIAG.load_docs(N_DOCS)

    # (1) the barrier is real -- head-match recall + over-merge content-identity
    pop = DIAG.population_and_headmatch(docs, gaz)
    hmr = pop["headmatch_recall"]["frac"]
    e = pop["recency_head_precision"]["errors"]
    ident_frac = e["identical_ambiguous"] / max(1, sum(e.values()))
    checks.append(("(1) head-match recall <= 0.45 (literary common-noun links are NOT head-identity)",
                   hmr <= 0.45, "head_match_recall=%.3f" % hmr))
    checks.append(("(1b) over-merge errors >= 0.8 content-IDENTICAL (not surface-separable)",
                   ident_frac >= 0.8, "identical_frac=%.3f (gender/mod-separable=%d)"
                   % (ident_frac, e["gender_separable"] + e["modifier_separable"])))

    # per-doc stats for the arms (char-cluster population)
    _, sh = LK.per_doc_stats(docs, gaz, "surface_head")
    _, no = LK.per_doc_stats(docs, gaz, "name_only")
    _, lk = LK.per_doc_stats(docs, gaz, "LINKER")
    _, tw = LK.per_doc_stats(docs, gaz, "TWIN", twin_seed=LK.SEED)

    # (2) forming referents helps: surface_head beats name_only CI-sep (char clusters)
    d_sh_no = LK.bootstrap_delta(sh, no, N_BOOT)
    checks.append(("(2) surface_head > name_only CI-sep (forming common-noun referents helps)",
                   d_sh_no["ci_sep"] and d_sh_no["delta"] > 0,
                   "CoNLL %+.4f CI[%+.4f,%+.4f]" % (d_sh_no["delta"], d_sh_no["lo"], d_sh_no["hi"])))

    # (3) located negative: the faithful accessibility former does NOT beat surface_head CI-sep,
    #     and stays far below the name_only->surface_head recovery (capped, headroom unreachable)
    d_lk_sh = LK.bootstrap_delta(lk, sh, N_BOOT)
    not_ci_sep_win = not (d_lk_sh["ci_sep"] and d_lk_sh["delta"] > 0)
    capped = d_lk_sh["delta"] < 0.5 * d_sh_no["delta"]
    checks.append(("(3) LOCATED NEGATIVE: faithful former does NOT beat surface_head CI-sep, and is "
                   "capped << the referent-formation recovery",
                   not_ci_sep_win and capped,
                   "LINKER-surface_head %+.4f CI[%+.4f,%+.4f] ci_sep=%s ; recovery(sh-name_only)=%+.4f"
                   % (d_lk_sh["delta"], d_lk_sh["lo"], d_lk_sh["hi"], d_lk_sh["ci_sep"], d_sh_no["delta"])))

    # (4) info-free twin loses
    d_lk_tw = LK.bootstrap_delta(lk, tw, N_BOOT)
    checks.append(("(4) former beats info-free (label-permuted) TWIN CI-sep",
                   d_lk_tw["ci_sep"] and d_lk_tw["delta"] > 0,
                   "CoNLL %+.4f CI[%+.4f,%+.4f]" % (d_lk_tw["delta"], d_lk_tw["lo"], d_lk_tw["hi"])))

    # (5) no-regress on NAMED coref (name-mention subpopulation)
    nm_lk = _name_subpop_stats(docs, gaz, "LINKER")
    nm_no = _name_subpop_stats(docs, gaz, "name_only")
    d_nm = LK.bootstrap_delta(nm_lk, nm_no, N_BOOT)
    no_regress = not (d_nm["ci_sep"] and d_nm["delta"] < 0)
    checks.append(("(5) NO-REGRESS on named coref: name-subpop LINKER not CI-sep below name_only",
                   no_regress, "name-subpop LINKER-name_only %+.4f CI[%+.4f,%+.4f]"
                   % (d_nm["delta"], d_nm["lo"], d_nm["hi"])))

    # (6) THE LANDABLE WIN: the DEPLOYABLE former (head-match-gated + modifier-split + wide window +
    #     event-centrality SITUATION gate, reusing hdlab.event_centrality_coref) beats surface_head
    #     CI-separated on character clusters, AND does not regress named coref.
    import experiments.exp_commonnoun_situation_gated_binder_v1 as SB
    best = SB.per_doc_situation(docs, gaz, window=16, headmatch_gate=True)
    _, sh_char = LK.per_doc_stats(docs, gaz, "surface_head")
    d_best = LK.bootstrap_delta(best, sh_char, N_BOOT)
    best_nm = SB.per_doc_situation(docs, gaz, window=16, headmatch_gate=True, subpop="name")
    d_best_nm = LK.bootstrap_delta(best_nm, nm_no, N_BOOT)
    checks.append(("(6) LANDABLE WIN: deployable situation-gated former BEATS surface_head CI-sep + "
                   "no-regress on named",
                   d_best["ci_sep"] and d_best["delta"] > 0
                   and not (d_best_nm["ci_sep"] and d_best_nm["delta"] < 0),
                   "BEST-surface_head %+.4f CI[%+.4f,%+.4f] ; named %+.4f"
                   % (d_best["delta"], d_best["lo"], d_best["hi"], d_best_nm["delta"])))

    npass = 0
    print("=" * 82)
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
        npass += int(ok)
    print("%d/%d checks passed  (%d docs, %d bootstrap)" % (npass, len(checks), N_DOCS, N_BOOT))
    print("=" * 82)
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
