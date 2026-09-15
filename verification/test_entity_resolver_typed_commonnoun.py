"""Witness that the unified `entity_resolver` reproduces the LAST live coref organ -- the typed_coref binding
inlined in the reader as `_resolve_commonnouns` -- BYTE-IDENTICALLY. This closes the one live remainder: after
this, all four default-on retrieval organs (online_entity_cluster, crosstype_bridge, world_state_entity_binding,
typed_coref/_resolve_commonnouns) + the pronoun pick are byte-reproduced by the ONE core.

EntityResolver.resolve_commonnouns(role_mentions, sents, reader) == reader._resolve_commonnouns(role_mentions,
sents), record-for-record, on real conll. The 5 bridge CUES (in-text appos is-a, typed-spokes license, C8
encyclopedic, conceptual, coarse-focus) are cue-PRODUCERS supplied by the reader; the retrieval loop (same-head
recency incumbent + non-writing ACT-R bridge + pronoun ACT-R pick) folds into the ONE core.

Run: .venv/Scripts/python.exe verification/test_entity_resolver_typed_commonnoun.py
"""
from __future__ import annotations
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.situation_reader as HSR
from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from experiments.exp_entity_resolver_unified_v1 import EntityResolver

RESULTS = []


def check(name, cond):
    RESULTS.append((name, bool(cond)))
    print(("  [PASS] " if cond else "  [FAIL] ") + name)
    return bool(cond)


def main():
    files = [
        "data/litbank/coref/conll/11_alices_adventures_in_wonderland_brat.conll",
        "data/litbank/coref/conll/120_treasure_island_brat.conll",
        "data/litbank/coref/conll/271_black_beauty_brat.conll",
        "data/litbank/coref/conll/45_anne_of_green_gables_brat.conll",
    ]
    R = EntityResolver()
    all_ident = True
    n_recs = 0
    n_resolved = 0
    n_docs = 0
    diff_shown = False
    for f in files:
        p = os.path.join(_REPO, f)
        if not os.path.exists(p):
            continue
        reader = HSR.SituationReader()
        reader._read_parse_cache = {}                      # read() sets this; _commonnoun_appos_map needs the parse cache
        role_mentions, n_sents = parse_litbank_conll(p, name_gender_map=reader.gaz)
        sents = parse_conll_sentences(p)
        a = reader._resolve_commonnouns(role_mentions, sents)     # the live reader method (reference)
        b = R.resolve_commonnouns(role_mentions, sents, reader)   # the ONE unified core
        n_docs += 1
        n_recs += len(a)
        n_resolved += sum(1 for r in a if r.get("resolved_ref") is not None)
        ident = (a == b)
        all_ident &= ident
        print("      %-48s records=%d resolved=%d  identical=%s"
              % (os.path.basename(f), len(a), sum(1 for r in a if r.get("resolved_ref") is not None), ident))
        if not ident and not diff_shown:
            diff_shown = True
            for i, (x, y) in enumerate(zip(a, b)):
                if x != y:
                    print("      first diff @rec %d: reader=%s  unified=%s" % (i, x, y))
                    break
            if len(a) != len(b):
                print("      length mismatch: reader=%d unified=%d" % (len(a), len(b)))

    check("SETUP: ran on >=3 conll docs with resolved bridges present (a non-trivial population)",
          n_docs >= 3 and n_resolved > 0)
    check("W1 resolve_commonnouns == reader._resolve_commonnouns byte-for-byte (%d docs, %d records, %d resolved)"
          % (n_docs, n_recs, n_resolved), all_ident)

    npass = sum(1 for _, ok in RESULTS if ok)
    print("\n[witness] %d/%d PASS" % (npass, len(RESULTS)))
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
