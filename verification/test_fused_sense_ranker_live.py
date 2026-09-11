"""verification/test_fused_sense_ranker_live.py -- witnesses for the pri-5 landing (2026-09-11): the reading-grounding
loop's sense-assignment read is the FUSED convergent-cue read (grounded-distinctive + grown-SEQ + referent, SDT accept
criterion), LIVE by default, with the recall path untouched and the grown SEQ store persistable.

  W1 live default: ReadingLoopState (what hdlab.substrate constructs) has fused ranking ON, the space accrues
     direction-typed counts for every content lemma; fused_ranking=False restores the incumbent primitive.
  W2 recall path byte-identical: `_sums` / bundles / trace counts are identical fused-on vs fused-off on the same
     ingest (only the separable count store differs).
  W3 mechanism: on the real curriculum ingest the ranker decides (accepts only when z_top >= the SDT criterion),
     falls back to the incumbent when no channel carries evidence, and the criterion is the (1-FA) null quantile.
  W4 the grounding gate USES it: gate decisions / refusals carry the `fused` record; a fused acceptance banks a
     GROUNDED_MEANING fact with provenance.
  W5 coverage-QUALITY (the instrument, smoke): FUSED beats the INCUMBENT bag-cosine read CI-separated on the loop's
     own live decision (SimLex/SimVerb high-sim, anchor-pool), the info-free TWIN loses.
  W6 persistence: the grown separable store roundtrips through the ROUTE-B sidecar and MERGES into a live space.
  W7 the tool's ingest == the loop's ingest: tools/grow_seq_store's accrual reproduces process_sentence's counts.
Run: .venv/Scripts/python.exe verification/test_fused_sense_ranker_live.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import sys
import tempfile
from collections import Counter

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (ReadingLoopState, FusedSenseRanker, ConceptSpace, CTX_D, seed_known_words,
                                          process_sentence, checkpoint, content_words, normalize_lemma,
                                          directional_context_lemmas, is_eligible_meaning, KNOWN_RELATION,
                                          MEANING_RELATION, FUSED_RANKING_DEFAULT, SDT_FALSE_ALARM)
import experiments.exp_reading_grounding_loop_cycle1_v1 as H

PASSED = []


def _state(fused=True, seed=1):
    st = HDFactStore(n_dim=2048, seed=seed, relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                                                  MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    s = ReadingLoopState(store=st, fused_ranking=fused)
    seed_known_words(s, H.load_base_vocab_seed(), "seed")
    return s


def _ingest(s, pool, ckpt_every=300):
    for i, (_t, sent) in enumerate(pool):
        process_sentence(s, sent, "e%d" % i, pass_idx=0)
        if ckpt_every and (i + 1) % ckpt_every == 0:
            checkpoint(s, (i + 1) // ckpt_every, "cur")


def w1_live_default():
    assert FUSED_RANKING_DEFAULT is True
    s = ReadingLoopState(store=HDFactStore(n_dim=256, seed=0))
    assert s.fused_ranking and isinstance(s.ranker, FusedSenseRanker)
    assert s.space.track_all_content_lemmas and s.space.track_directional_context_counts
    off = ReadingLoopState(store=HDFactStore(n_dim=256, seed=0), fused_ranking=False)
    assert off.ranker is None and not off.space.track_directional_context_counts
    from hdlab.substrate import Substrate
    sub = Substrate()
    assert sub.state.fused_ranking and sub.state.ranker is not None, "the live substrate must construct the fused loop"
    PASSED.append("W1 live default ON (ReadingLoopState + Substrate); fused_ranking=False = incumbent primitive")


def w2_recall_path_byte_identical(pool):
    a = _state(False); b = _state(True)
    _ingest(a, pool[:300], ckpt_every=0); _ingest(b, pool[:300], ckpt_every=0)
    assert a.space.anchors() == b.space.anchors()
    for lem in a.space.anchors():
        assert np.array_equal(a.space._sums[lem], b.space._sums[lem]), lem
        assert a.space.trace_count(lem) == b.space.trace_count(lem), lem
    assert not a.space.all_context_counts() and b.space.all_context_counts()
    PASSED.append("W2 recall path (_sums/bundle/trace_count) byte-identical fused-off vs fused-on on the same ingest")


def w3_mechanism(pool):
    s = _state(True)
    _ingest(s, pool, ckpt_every=300)
    st = s.ranker.stats
    assert st["decisions"] > 20, dict(st)
    assert st["accepted"] + st["refused_by_criterion"] == st["decisions"]
    crit = s.ranker.criterion(500)
    rng = np.random.default_rng(20260911 + 500)
    d = rng.standard_normal((4000, 500)); z = (d.max(1) - d.mean(1)) / (d.std(1) + 1e-12)
    assert abs(crit - float(np.quantile(z, 1 - SDT_FALSE_ALARM))) < 1e-9, "criterion = (1-FA) null quantile"
    assert crit > 3.0, crit
    # a synthetic word with no norms / no referent / no counts -> no channel -> fallback (None)
    assert s.ranker.rank("zzqxv_unseen", eligible=is_eligible_meaning) is None
    # accept obeys the criterion on a real decision
    seen = False
    for lem in list(s.space.all_context_counts())[:400]:
        if lem in s.known_seed:
            continue
        r = s.ranker.rank(lem, eligible=is_eligible_meaning)
        if r is not None:
            assert r["accept"] == (r["z_top"] >= r["criterion"]); seen = True
            assert abs(sum(r["weights"].values()) - len(r["weights"])) < 1e-3, r["weights"]
            break
    assert seen
    PASSED.append("W3 mechanism: decisions=%d accepted=%d refused=%d fallback=%d; SDT criterion(N=500)=%.3f"
                  % (st["decisions"], st["accepted"], st["refused_by_criterion"], st["fallback_no_channel"], crit))
    return s


def w4_gate_uses_it(s):
    fused_rows = [r for r in s.refusals if r.get("fused")]
    assert fused_rows, "refusals must carry the fused record when the ranker decided"
    assert all(r["reason"] == "TAUTOLOGY_NO_ANCHOR" and r["fused"]["accept"] is False for r in fused_rows)
    banked = [p for p in s.provenance if p["relation"] == MEANING_RELATION]
    assert banked, "the live loop must bank some fused groundings on the curriculum"
    PASSED.append("W4 gate wired: %d fused refusals carry the record; %d GROUNDED_MEANING facts banked with provenance"
                  % (len(fused_rows), len(banked)))


def w5_coverage_quality():
    import experiments.exp_board_grounding_coverage_quality_v1 as G
    r = G.run(mode="smoke", n_boot=500, grown_store=None)
    fi = r["FUSED_minus_INCUMBENT@0.5"]; ft = r["FUSED_minus_TWIN@0.5"]
    assert r["n_queries"] >= 40, r["n_queries"]
    assert fi["ci_sep_positive"], fi
    assert ft["ci_sep_positive"], ft
    PASSED.append("W5 coverage-QUALITY (n=%d): FUSED MRR@0.5 %.4f vs INCUMBENT %.4f CI %s; vs TWIN %+.4f CI %s"
                  % (r["n_queries"], fi["a"], fi["b"], fi["ci"], ft["diff"], ft["ci"]))


def w6_persistence():
    from hdlab.foundation_persistence import save_concept_space, load_concept_space, load_ctx_counts_into, _ctx_sidecar_path
    sp = ConceptSpace(d=16); sp.track_all_content_lemmas = True; sp.track_directional_context_counts = True
    sp.observe("dog", np.ones(16)); sp.observe_context_counts("dog", ["L1__the", "R1__bark", "R1__bark"])
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "cs.npz"); save_concept_space(sp, p)
        assert os.path.isfile(_ctx_sidecar_path(p))
        sp2 = load_concept_space(p)
        assert sp2.context_counts("dog") == Counter({"R1__bark": 2, "L1__the": 1}) and sp2.track_directional_context_counts
        live = ConceptSpace(d=16); live.observe_context_counts("dog", ["R1__bark"])
        live.track_all_content_lemmas = True
        live.observe_context_counts("dog", ["R1__bark"])
        merged = load_ctx_counts_into(live, _ctx_sidecar_path(p))
        assert merged == 3 and live.context_counts("dog")["R1__bark"] == 3, live.context_counts("dog")
    PASSED.append("W6 sidecar roundtrip + merge into a live space")


def w7_tool_ingest_equals_loop_ingest(pool):
    s = _state(True); _ingest(s, pool[:120], ckpt_every=0)
    tool = ConceptSpace(d=CTX_D); tool.track_all_content_lemmas = True; tool.track_directional_context_counts = True
    for _t, sent in pool[:120]:
        multiset = [normalize_lemma(w) for w in content_words(sent)]
        for tgt in set(multiset):
            tool.observe_context_counts(tgt, directional_context_lemmas(multiset, tgt))
    a, b = s.space.all_context_counts(), tool.all_context_counts()
    assert set(a) == set(b) and all(a[k] == b[k] for k in a), "tool ingest must equal process_sentence's accrual"
    PASSED.append("W7 tools/grow_seq_store ingest == process_sentence all-content directional accrual (%d lemmas)" % len(a))


def w8_substrate_merges_grown_store():
    from hdlab.substrate import Substrate
    path = os.path.join(_REPO, "data", "foundation", "seq_store_v1", "concept_space_ctx_counts.npz")
    sub = Substrate()
    if os.path.isfile(path):
        assert sub.seq_store_merged_tokens > 1_000_000, sub.seq_store_merged_tokens
        assert sub.state.space.context_counts("dog"), "a common noun must carry grown directional counts"
        off = Substrate(seq_store=None)
        assert off.seq_store_merged_tokens == 0 and not off.state.space.all_context_counts()
        PASSED.append("W8 Substrate() merges the grown SEQ store (%d tokens); seq_store=None = cold start"
                      % sub.seq_store_merged_tokens)
    else:
        assert sub.seq_store_merged_tokens == 0
        PASSED.append("W8 grown SEQ store absent on this machine -> cold start stated (regenerate: tools/grow_seq_store.py)")


def main():
    pool = H.build_curriculum_pool(limit_sentences=900)
    w1_live_default()
    w8_substrate_merges_grown_store()
    w2_recall_path_byte_identical(pool)
    s = w3_mechanism(pool)
    w4_gate_uses_it(s)
    w6_persistence()
    w7_tool_ingest_equals_loop_ingest(pool)
    w5_coverage_quality()
    for p in PASSED:
        print("[PASS]", p)
    print("%d/8 witnesses passed." % len(PASSED))
    print("FUSED SENSE-ASSIGNMENT READ IS LIVE -- grounded-distinctive + grown-SEQ + referent, SDT criterion; "
          "beats the incumbent bag-cosine on coverage QUALITY CI-sep, twin loses, recall path intact.")


if __name__ == "__main__":
    main()
