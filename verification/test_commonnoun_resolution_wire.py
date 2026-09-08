"""verification/test_commonnoun_resolution_wire.py -- WITNESS for the Q111 common-noun RESOLUTION wire.

Scaffold-free: recomputes every headline from source on the FULL GUM modern TEST (odd docs, n=2855 anaphoric
common-noun mentions) + a real LitBank doc for the no-regress / de-leak checks. Asserts:

  W1  HEADLINE (fair, same-regime): the LIVE reader wire (sm.commonnoun_resolution -- the typed_coref binding on
      the reader's OWN dict-mention stream, routing via is_pronoun/is_name, key via the reader's OWN head_lemma,
      NO GUM gold lemma/mtype) BEATS the SAME-LEMMATIZER string-identity floor CI-separated, and reproduces ~0.539.
  W2  MECHANISM FAITHFUL (positive control): the GOLD-schema reference (typed_coref_liveschema_resolve) reproduces
      the proven 0.5664 and BEATS the GUM-gold-lemma board floor (0.5412) CI-sep -- so the deficit of the live
      wire vs 0.5664 is the gold-lemma ANNOTATION regime, NOT the binding. The wire reaches PARITY (not a beat)
      with the gold-lemma floor -- asserted honestly (beats_gold_lemma_floor_ci_sep is False).
  W3  INFO-FREE TWIN loses CI-sep (bridge -> random gn-compatible prior -> the type signal is load-bearing).
  W4  NO-REGRESS / ADDITIVE (by construction): on a real LitBank doc, the resolver does NOT mutate role_mentions
      (byte-identical, incl every 'cluster' id) and the reader's sm.entities clustering (_build_entities) is
      byte-identical with the resolver run vs not -- so wiring sm.commonnoun_resolution cannot move sm.entities /
      coref_acc (it writes a NEW field, reads role_mentions read-only). resolve_commonnouns is default-on-safe.
  W5  GOLD-FREE (de-leak): stripping every gold field (gold_eid / mtype / lemma_head / gender_mfn / is_ana /
      gov_*) from the mention dicts leaves the resolver's records BYTE-IDENTICAL -> no gold touches a resolution
      decision (gold is used only by the scorer).

Run: .venv/Scripts/python.exe verification/test_commonnoun_resolution_wire.py
Glass-box, CPU, NO external LLM. ASCII.
"""
from __future__ import annotations
import os, sys, copy

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

import experiments.exp_situation_model_qa_modern_v1 as B
import experiments.exp_commonnoun_binder_live_report_v1 as CBL
import hdlab.typed_coref as TC
from hdlab.coref import parse_litbank_conll
from hdlab.situation_reader import _build_entities

_GOLD_KEYS = ("gold_eid", "mtype", "lemma_head", "gender_mfn", "is_ana", "order", "gov_verb", "gov_role")
_LITBANK = os.path.join(_REPO, "data", "litbank", "coref_conll")


def _ents_sig(mentions):
    """Byte-comparable signature of _build_entities output (cluster -> heads/sents/count/person)."""
    return [(e.cluster if isinstance(e.cluster, int) else str(e.cluster), tuple(e.heads),
             tuple(e.sent_indices), e.n_mentions, e.is_person) for e in _build_entities(mentions)]


def w1_w2_w3_gum():
    """W1/W2/W3 -- the FULL board-arm measurement on GUM modern TEST (the instrument that populates the board row)."""
    row, det = B.board_commonnoun_resolution_dimension()      # full GUM TEST (137 docs); doc-paired bootstrap CI
    assert row["n"] == 2855, "population != URG board common (2855): n=%s" % row["n"]

    # W1 -- headline over the FAIR (same-lemmatizer) floor
    m = row["model_acc"]; f = row["strongest_floor"]
    assert row["strongest_floor_name"] == "same_lemmatizer_string_identity_head_lemma", row["strongest_floor_name"]
    # C8 encyclopedic name->type route landed 2026-09-08 (report_the_typed_coref fix 3): 0.5394 -> 0.5482 (+0.0088),
    # margin over the fair floor +0.0238 -> +0.0326 CI-sep; now EXCEEDS the gold-lemma floor 0.5412 point-estimate
    # though the CI still includes 0 (W2 parity holds, honestly).
    assert 0.543 <= m <= 0.554, "live wire acc drifted: %s (expected ~0.5482 with the C8 encyclopedic route)" % m
    assert abs(f - 0.5156) <= 0.004, "fair floor drifted: %s (expected ~0.5156)" % f
    assert row["ci_sep_over_strongest"] and row["model_minus_strongest"][1] > 0, \
        "wire does NOT beat the same-lemmatizer floor CI-sep: %s" % row["model_minus_strongest"]

    # W2 -- mechanism faithful (positive control): the gold-schema reference recovers 0.5664 + beats the gold floor
    ref = row["gold_routed_reference_acc"]
    assert 0.565 <= ref <= 0.568, "gold-routed reference drifted from 0.5664: %s" % ref
    assert row["gold_routed_reference_beats_gold_floor_ci_sep"] and \
        row["gold_routed_reference_minus_gold_floor"][1] > 0, \
        "reference must beat the gold-lemma floor CI-sep (positive control): %s" % row["gold_routed_reference_minus_gold_floor"]
    assert abs(row["gold_lemma_reference_floor"] - 0.5412) <= 0.004, row["gold_lemma_reference_floor"]
    # HONEST: the LIVE wire only TIES the (stronger) gold-lemma floor -- assert we do NOT claim a beat there
    assert row["beats_gold_lemma_floor_ci_sep"] is False, \
        "live wire is NOT expected to beat the gold-lemma floor (parity): %s" % row["model_minus_gold_lemma_floor"]
    assert row["model_minus_gold_lemma_floor"][1] < 0 < row["model_minus_gold_lemma_floor"][2], \
        "gold-lemma-floor delta CI must include 0 (parity): %s" % row["model_minus_gold_lemma_floor"]

    # W3 -- info-free twin loses CI-sep
    assert row["ci_sep_over_twin"] and row["model_minus_twin"][1] > 0, \
        "info-free twin does NOT lose CI-sep: %s" % row["model_minus_twin"]
    assert row["twin_acc"] < m, "twin (%.4f) should be below the wire (%.4f)" % (row["twin_acc"], m)

    print("W1 PASS  live wire common=%.4f  BEATS same-lemmatizer floor %.4f  d=%+.4f CI%s CI-sep=%s"
          % (m, f, row["model_minus_strongest"][0], row["model_minus_strongest"][1:], row["ci_sep_over_strongest"]))
    print("W2 PASS  gold-schema reference common=%.4f (=0.5664) BEATS gold-lemma floor %.4f d=%+.4f CI%s; "
          "LIVE wire PARITY with gold-lemma floor d=%+.4f CI%s (residual = gold-lemma regime, not the binding)"
          % (ref, row["gold_lemma_reference_floor"], row["gold_routed_reference_minus_gold_floor"][0],
             row["gold_routed_reference_minus_gold_floor"][1:], row["model_minus_gold_lemma_floor"][0],
             row["model_minus_gold_lemma_floor"][1:]))
    print("W3 PASS  info-free twin common=%.4f LOSES d=%+.4f CI%s CI-sep=%s"
          % (row["twin_acc"], row["model_minus_twin"][0], row["model_minus_twin"][1:], row["ci_sep_over_twin"]))
    return row


def w4_no_regress():
    """W4 -- ADDITIVE / no-regress on a REAL LitBank doc: the resolver mutates NOTHING and the clustering
    (_build_entities, which drives sm.entities) is byte-identical whether or not the resolver has run."""
    files = sorted(f for f in os.listdir(_LITBANK) if f.endswith(".conll"))
    assert files, "no LitBank coref_conll docs on disk"
    path = os.path.join(_LITBANK, files[0])
    role_mentions, n = parse_litbank_conll(path, name_gender_map={})     # exactly what read() calls
    assert n > 0 and role_mentions, "empty parse: %s" % path
    snapshot = copy.deepcopy(role_mentions)
    ents_before = _ents_sig(role_mentions)
    res = B._reader_commonnoun_resolution(role_mentions, {}, {})         # the wire mechanism, run in place
    # (a) no mutation of ANY mention field (incl every gold/coref 'cluster' id)
    assert role_mentions == snapshot, "resolver MUTATED role_mentions (not additive)"
    assert all(a["cluster"] == b["cluster"] for a, b in zip(role_mentions, snapshot)), "resolver changed a cluster id"
    # (b) the clustering that feeds sm.entities is byte-identical
    assert _ents_sig(role_mentions) == ents_before, "sm.entities clustering changed after the resolver ran"
    # (c) the resolution is a well-formed NEW structure over the NON-PRONOUN mentions only
    nonpron = {m["midx"] for m in role_mentions if not m["is_pronoun"]}
    assert {r["midx"] for r in res} == nonpron, "resolution records != the non-pronoun mention set"
    assert all(set(r) == {"midx", "mtype", "own_ref", "resolved_ref"} for r in res), "malformed resolution record"
    print("W4 PASS  additive/no-regress on %s: %d role-mentions byte-identical, %d resolution records, "
          "sm.entities clustering byte-identical" % (files[0], len(role_mentions), len(res)))


def w5_gold_free():
    """W5 -- de-leak: strip every gold field from the mention dicts; the resolver's records must be byte-identical
    (no gold touches a resolution decision -- gold is used ONLY by the scorer)."""
    gaz, test = CBL._load(None)
    checked = 0
    for d in test[:10]:
        ms = CBL.doc_to_binder_mentions(d)
        ap = TC.appos_copula_isa(d)
        a = B._reader_commonnoun_resolution(ms, gaz, ap)
        stripped = []
        for m in ms:
            mm = {k: v for k, v in m.items() if k not in _GOLD_KEYS}
            stripped.append(mm)
        b = B._reader_commonnoun_resolution(stripped, gaz, ap)
        assert a == b, "resolver output CHANGED when gold fields stripped -> a resolution decision reads gold (doc %s)" % d.docid
        checked += 1
    print("W5 PASS  gold-free: resolver records byte-identical with all gold fields stripped (%d GUM docs)" % checked)


def main():
    row = w1_w2_w3_gum()
    w4_no_regress()
    w5_gold_free()
    print("\nALL WITNESSES PASS (5/5). Live common-noun RESOLUTION wire: sm.commonnoun_resolution common=%.4f "
          "beats the fair same-lemmatizer floor %.4f CI-sep; twin loses; additive/no-regress; gold-free."
          % (row["model_acc"], row["strongest_floor"]))


if __name__ == "__main__":
    main()
