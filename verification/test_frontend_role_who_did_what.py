"""Scaffold-free witnesses for `the_live_front_end_mislabels_who_did_what_to_whom`.

Recompute the headline claims live (no metrics.json dependency), at bounded scale:

  1. THE WALL: the live positional front-end scores end-to-end BELOW the trivial majority floor, and
     its errors are MISASSIGNMENT-dominant (not MISS).
  2. NAIVE WIRING FAILS: CandidateGenerator over-generates (>>2 candidate arg-pairs / clause), so
     labeling every candidate floods resolution -- the naive organ wiring cannot select core mentions.
  3. THE FIX RECOVERS THE WALL: the fair augmented assigner (core-mention selection + quote exclusion +
     SPEECH/quotative verb-class cue + the organ's learned graded integration) beats the live positional
     baseline end-to-end, and the SPEECH cue is load-bearing.
  4. BRAIN-FAITHFUL CUE HIERARCHY (QA-SRL, modern prose): WORD ORDER dominates AGENT/PATIENT assignment;
     it resolves the two-animate reversible cases where ANIMACY is exactly chance; adding THEMATIC-FIT
     does NOT beat the order+voice base (a rigorous negative -- English is word-order dominant).
"""
from __future__ import annotations

import numpy as np
import pytest

import experiments.exp_wire_organs_endtoend_v1 as W
import experiments.exp_thematic_role_labeler_cue_integration_v1 as base
import experiments.exp_frontend_role_augmented_cv_v1 as A
import experiments.exp_frontend_thematic_fit_qasrl_v1 as B
from hdlab.candidate_generator import CandidateGenerator


@pytest.fixture(scope="module")
def gen():
    return CandidateGenerator.load(base.POS_PATH, base.ARC_PATH)


@pytest.fixture(scope="module")
def passages():
    return W.load_gold()


def test_the_wall_position_below_majority_and_misassignment_dominant(passages):
    """Live positional front-end end-to-end < trivial majority floor; errors misassignment-dominant."""
    seed = 20260826
    binds = {p["passage_id"]: W.resolve_raw(W.live_extract_raw(p, mode="position"), p, policy="recency", seed=seed)
             for p in passages}
    e2e = W.score_endtoend(passages, binds, seed)["role_acc"]
    nq = sum(len(p.get("target_queries", [])) for p in passages)
    from collections import Counter
    gm = Counter(q["gold_role"] for p in passages for q in p.get("target_queries", [])).most_common(1)[0]
    maj = gm[1] / nq
    assert e2e < maj - 0.15, (e2e, maj)          # the wall: live front-end well below always-agent
    tax = W.error_taxonomy(passages, seed, mode="position")
    assert tax["n_misassign"] > tax["n_miss"] * 2, tax   # misassignment-dominant, not miss
    assert tax["front_end_inscope_acc"] < 0.5, tax       # in-scope role labeling is broken live


def test_candidate_generator_over_generates(gen, passages):
    """The naive-wiring failure mode: labeling every candidate floods resolution."""
    ncand = []
    for p in passages[:20]:
        for clause in p["clauses"]:
            ncand.append(len(gen.generate(clause).candidates))
    assert np.mean(ncand) > 4.0, np.mean(ncand)          # far more than the <=2 core mentions
    assert max(ncand) > 10                                # some clauses are severely over-generated


def test_augmented_assigner_beats_positional_baseline_and_speech_cue_matters(gen, passages):
    """The fix recovers the wall end-to-end over the live positional baseline; speech cue load-bearing."""
    ps = passages[:30]
    seed = 20260826
    parses = {(p["passage_id"], ci): gen.generate(c) for p in ps for ci, c in enumerate(p["clauses"])}
    A._load_centroids()
    # live positional baseline on the same subset
    binds = {p["passage_id"]: W.resolve_raw(W.live_extract_raw(p, mode="position"), p, policy="recency", seed=seed)
             for p in ps}
    pos_all = np.mean(A._score_items(ps, binds, subset=None))
    # augmented (speech ON, thematic-fit OFF -- the best McGuffey config), held-out CV
    av_tagged, iv = A.cv_endtoend(ps, parses, seed, k=3, use_speech=True, use_fit=False)
    aug_all = np.mean([ok for _r, ok in av_tagged])
    aug_ins = np.mean(iv)
    # speech-ablated
    av_ns, iv_ns = A.cv_endtoend(ps, parses, seed, k=3, use_speech=False, use_fit=False)
    aug_ns_ins = np.mean(iv_ns)
    assert aug_all > pos_all + 0.10, (aug_all, pos_all)         # recovers the wall over the live baseline
    assert aug_ins >= aug_ns_ins, (aug_ins, aug_ns_ins)        # speech cue helps in-scope role labeling


def test_qasrl_word_order_dominates_and_thematic_fit_does_not_help():
    """Brain-faithful cue hierarchy on modern prose: order resolves two-animate (animacy=chance);
    adding thematic-fit does NOT beat the order+voice base (rigorous negative)."""
    entries = B.load_entries(max_sent=6000)
    import hashlib
    def in_test(e):
        h = int(hashlib.md5(f"{e['verb']}|{e['agent']['head']}|{e['patient']['head']}|{e['vi']}".encode()).hexdigest()[:8], 16)
        return (h % 5) == 0
    train_e = [e for e in entries if not in_test(e)]
    test_e = [e for e in entries if in_test(e)]
    vr, role_c = B.build_centroids(train_e)

    def examples(elist):
        out = []
        for e in elist:
            for arg in (e["agent"], e["patient"]):
                out.append({"feats": B.feats_for_arg(e, arg, vr, role_c), "role": arg["role"], "e": e})
        return out
    tr, te = examples(train_e), examples(test_e)
    two_anim = [x for x in te if x["e"]["agent"]["agent_capable"] and x["e"]["patient"]["agent_capable"]]
    assert len(two_anim) >= 20, len(two_anim)

    from hdlab.thematic_role_labeler import train_perceptron

    def acc(prefixes, testset):
        trf = [(B.filter_feats(x["feats"], prefixes), x["role"]) for x in tr]
        pred, w, _ = train_perceptron(trf, seed=7, epochs=25, roles=("AGENT", "PATIENT"))
        return np.mean([int(pred(B.filter_feats(x["feats"], prefixes)) == x["role"]) for x in testset])

    anim = acc(B.ARM_PREFIXES["ANIMACY_ONLY"], two_anim)
    pos = acc(B.ARM_PREFIXES["POSITION_ONLY"], two_anim)
    org = acc(B.ARM_PREFIXES["ORGAN_BASE"], two_anim)
    tf = acc(B.ARM_PREFIXES["THEMFIT"], two_anim)
    pure = acc(B.ARM_PREFIXES["THEMFIT_PURE"], two_anim)   # thematic fit with NO order (no tfxo leak)
    assert anim < 0.62, anim                       # animacy ~ chance on two-animate
    assert pos > anim + 0.20, (pos, anim)          # word order resolves reversible role assignment
    assert tf <= org + 0.02, (tf, org)             # additive thematic-fit does NOT improve over order+voice
    # deepening: pure thematic-fit is a REAL but LOW-VALIDITY cue, DOMINATED by word order (Competition Model)
    assert pos > pure + 0.15, (pos, pure)          # word order dominates pure thematic fit
    assert pure >= 0.50, pure                       # pure thematic fit is not below chance (carries some info)


def test_speech_verb_class_is_semantic_and_learnable_vs_null(gen, passages):
    """Deepening (null-controlled): the speech-verb cue's value is SEMANTIC and shows on the ROLE-BALANCED
    (macro) metric -- the distributionally-LEARNED quotative class (from quote co-occurrence, brain-faithful)
    beats a NULL DISTRIBUTION of random verb classes. (A single random draw is NOT a valid twin -- an
    arbitrary verb partition is a free feature; only the null p95 controls for it. Correction from the drill.)"""
    import experiments.exp_frontend_verbclass_source_v1 as V
    import experiments.exp_frontend_role_augmented_cv_v1 as A
    from hdlab.thematic_role_labeler import lemma_verb
    seed = 20260827
    parses = {(p["passage_id"], ci): gen.generate(c) for p in passages for ci, c in enumerate(p["clauses"])}
    A._load_centroids()
    corpus_verbs = {lemma_verb(res.tokens[v - 1]) for res in parses.values() for (v, a) in res.candidates}
    corpus_verbs = {v for v in corpus_verbs if v.isalpha()}
    learned = V.learn_quotative_verbs(parses)
    assert len(learned) >= 8 and "say" in learned, sorted(learned)   # quote co-occurrence learns verba dicendi

    def macro(speech_set, use_speech=True):
        saved = A.SPEECH_VERBS
        try:
            A.SPEECH_VERBS = speech_set
            av, _iv = A.cv_endtoend(passages, parses, seed, k=6, use_speech=use_speech, use_fit=False)
        finally:
            A.SPEECH_VERBS = saved
        return A.macro_balanced(av)[0]
    learned_macro = macro(learned)
    off_macro = macro(set(), use_speech=False)
    rng = np.random.default_rng(seed + 777)
    allv = sorted(corpus_verbs)
    # 2026-09-13 (strategy): the null is its p95 over 200 draws, as the docstring states -- the earlier max-of-10 criterion
    # compared against an extreme-value statistic with large variance (it failed by 0.007 on a day the learned class sat at
    # the null's 99th percentile: learned 0.2053 vs p95 0.1897 vs max-of-200 0.2097; with the category organ's unknown-word
    # cues OFF the class sits at the 90th percentile -- the cues IMPROVE the separation). 200 draws cost ~2 minutes.
    null_macros = np.array([macro(set(rng.choice(allv, size=len(learned), replace=False).tolist())) for _ in range(200)])
    p95 = float(np.percentile(null_macros, 95))
    assert learned_macro > off_macro, (learned_macro, off_macro)             # the learned class helps
    assert learned_macro > p95, (learned_macro, p95, float(null_macros.max()))  # beats the random null's p95 (semantic)


def test_normalized_recurrence_is_an_accuracy_equivalent_integrator():
    """Deepening Q2: the brain runs constraint-satisfaction DYNAMICS (Spivey-Knowlton normalized
    recurrence), a more brain-faithful MECHANISM than a feedforward perceptron. Robust, honest claim:
    it is a VALID, accuracy-equivalent integrator (word order dominant). Its distinctive settling-based
    difficulty signal is NOT cleanly validated on this corpus (documented in SOLVED.md) -- so this
    witness asserts only the accuracy equivalence, not a clean difficulty signal."""
    import experiments.exp_frontend_normalized_recurrence_v1 as R
    entries = R.B.load_entries(max_sent=5000)
    import hashlib
    key = lambda e: int(hashlib.md5(f"{e['verb']}|{e['agent']['head']}|{e['patient']['head']}|{e['vi']}".encode()).hexdigest()[:8], 16) % 5
    train = [e for e in entries if key(e) != 0]
    test = [e for e in entries if key(e) == 0]
    vr, role_c = R.B.build_centroids(train)
    val = R.learn_validities(train, vr, role_c)
    corr = []
    for e in test:
        sup, gold, _two = R.cue_supports(e, vr, role_c)
        win, _cyc, _gap = R.normalized_recurrence(sup, val)
        corr.append(int(win == gold))
    acc = float(np.mean(corr))
    assert len(test) >= 200, len(test)
    assert acc > 0.75, acc          # a valid, order-dominant integrator (near the perceptron ~0.85-0.93)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
