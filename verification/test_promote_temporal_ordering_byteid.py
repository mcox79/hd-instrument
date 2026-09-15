"""Q111 self-containment promotion PROOF: experiments/_temporal_ordering.py -> hdlab/temporal_ordering.py.

The live reader hdlab/situation_reader.py imports `from experiments import _temporal_ordering as T`
(line 135, DEFAULT-ON). This violates the promoted-organ standard (a live organ must have ZERO
experiments/ imports). T's only experiments dependency is the LAZY tagger import inside default_tagger()
(`from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC; ORC.pos_tag_sentence`).

This script:
  1. BUILDS the candidate hdlab module `verification/candidate_temporal_ordering.py` = a byte-faithful
     copy of experiments/_temporal_ordering.py with the ONE surgical change: default_tagger inlines the
     tokenizer + NLTK PerceptronTagger (byte-faithful copy of ORC.tokenize/_tagger/pos_tag_sentence),
     so it has ZERO experiments/ imports.
  2. PROVES the promotion is a pure move: runs the WHOLE live reader.read() on N modern GUM docs with
     stock experiments T, then monkeypatches hdlab.situation_reader.T = candidate (simulating the import
     change `from experiments import _temporal_ordering` -> `from hdlab.temporal_ordering import ...`),
     re-runs, and asserts the serialized SituationModel is BYTE-IDENTICAL for every doc.

Run: .venv/Scripts/python.exe verification/test_promote_temporal_ordering_byteid.py [--docs N]
"""
from __future__ import annotations

import os
import re
import sys
import argparse
import hashlib
import tempfile

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

SRC = os.path.join(_REPO, "experiments", "_temporal_ordering.py")
CAND = os.path.join(_REPO, "verification", "candidate_temporal_ordering.py")

# The stock default_tagger (experiments import) -- replaced verbatim.
_OLD_DEFAULT_TAGGER = '''def default_tagger(text):
    """Reader POS pipeline: NLTK PerceptronTagger via the ORC reader helper.

    Returns list of (surface, low, pos). Imported lazily so the module has no hard
    import-time dependency on the reader cell (keeps it pluggable / testable).
    """
    from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC
    return ORC.pos_tag_sentence(text)'''

# Self-contained replacement: byte-faithful copy of ORC.tokenize / ORC._tagger / ORC.pos_tag_sentence
# (experiments/exp_oracle_mention_upperbound_reader_v1.py lines 229-336) -- same regex, same
# PerceptronTagger, same low-strip. ZERO experiments/ imports; NLTK is an allowed shallow tool.
_NEW_DEFAULT_TAGGER = '''# ---- SELF-CONTAINED POS pipeline (promoted byte-faithfully from ORC.pos_tag_sentence; ZERO
# experiments/ imports; NLTK PerceptronTagger is an allowed shallow tool) --------------------
_TOKEN_RE = _re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_ORC_TAGGER = None


def _perceptron_tagger():
    global _ORC_TAGGER
    if _ORC_TAGGER is None:
        from nltk.tag import PerceptronTagger
        _ORC_TAGGER = PerceptronTagger()
    return _ORC_TAGGER


def _tokenize(sentence):
    return [m.group(0) for m in _TOKEN_RE.finditer(sentence)]


def pos_tag_sentence(sentence):
    """Return list of (surface, low, pos) using NLTK PerceptronTagger (legal shallow tool).
    Byte-faithful copy of ORC.pos_tag_sentence so hdlab has ZERO experiments/ imports."""
    toks = _tokenize(sentence)
    tagged = _perceptron_tagger().tag(toks)
    out = []
    for surf, pos in tagged:
        low = surf.lower().strip(".,'\\"!?;:")
        out.append((surf, low, pos))
    return out


def default_tagger(text):
    """Reader POS pipeline: NLTK PerceptronTagger (SELF-CONTAINED; no experiments import).

    Returns list of (surface, low, pos)."""
    return pos_tag_sentence(text)'''


def build_candidate():
    with open(SRC, "r", encoding="utf-8") as f:
        src = f.read()
    assert _OLD_DEFAULT_TAGGER in src, "default_tagger anchor not found -- source drifted"
    # inject `import re as _re` alongside the existing stdlib imports (byte-faithful otherwise)
    src2 = src.replace("import os\nimport sys\n", "import os\nimport re as _re\nimport sys\n", 1)
    assert src2 != src, "stdlib import anchor not found"
    src2 = src2.replace(_OLD_DEFAULT_TAGGER, _NEW_DEFAULT_TAGGER, 1)
    header = ("# AUTO-GENERATED CANDIDATE for hdlab/temporal_ordering.py by "
              "verification/test_promote_temporal_ordering_byteid.py.\n"
              "# Byte-faithful copy of experiments/_temporal_ordering.py with default_tagger self-contained.\n"
              "# DO NOT hand-edit; this file is the proposed hdlab module content.\n")
    with open(CAND, "w", encoding="utf-8") as f:
        f.write(header + src2)
    # assert zero experiments IMPORTS in the candidate (the word may appear in prose comments)
    imp = re.findall(r"^\s*(?:from|import)\s+experiments\b.*$", src2, flags=re.M)
    assert not imp, "candidate still IMPORTS experiments: %r" % imp
    return CAND


def _load_candidate_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("candidate_temporal_ordering", CAND)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["candidate_temporal_ordering"] = mod   # needed for @dataclass resolution
    spec.loader.exec_module(mod)
    return mod


def _serialize(sm):
    """Deterministic serialization of the load-bearing SituationModel fields the reader produces."""
    def ev(e):
        return (getattr(e, "predicate", None), getattr(e, "agent", None), getattr(e, "patient", None),
                getattr(e, "sent_idx", None), getattr(e, "pred_idx", None), getattr(e, "tense", None))
    parts = []
    parts.append("ENTITIES=" + repr([(getattr(x, "name", None), getattr(x, "eid", None),
                                      getattr(x, "mentions", None)) for x in (sm.entities or [])]))
    parts.append("EVENTS=" + repr([ev(e) for e in (sm.events or [])]))
    parts.append("SUPPRESSED=" + repr(sorted(map(str, sm.suppressed_predicates or []))))
    parts.append("TIMELINE=" + repr([repr(f) for f in (sm.timeline_frames or [])]))
    parts.append("CAUSAL=" + repr([repr(c) for c in (sm.causal_links or [])]))
    parts.append("COREF=" + repr([repr(r) for r in (getattr(sm, "coref_resolutions", None) or [])]))
    parts.append("MEMRT=" + repr(getattr(sm, "memory_roundtrip", None)))
    return "\n".join(parts)


def run(docs_limit=20):
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    import hdlab.situation_reader as SRMOD
    from hdlab.situation_reader import SituationReader

    build_candidate()
    cand = _load_candidate_module()
    print("[build] candidate written: %s (zero experiments/ imports asserted)" % CAND)

    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=docs_limit, name_gazetteer=gaz)
    print("[data] loaded %d modern GUM docs" % len(docs))

    stock_T = SRMOD.T  # the live temporal organ
    if stock_T.__name__ == "hdlab.temporal_model":
        # 2026-09-14 (strategy): this Q111 promotion proof's premise (experiments/_temporal_ordering -> hdlab/temporal_ordering)
        # was superseded on 2026-09-11 when the temporal organs were consolidated into hdlab.temporal_model. The INVARIANT the
        # proof existed for -- the live reader is self-contained, with no experiments/ import on its path -- is checked here
        # directly instead; the byte-identity of the consolidated organ is covered by the temporal witnesses.
        import re as _re
        src = open(SRMOD.__file__, encoding="utf-8").read()
        bad = [l for l in src.splitlines() if _re.match(r"\s*(from|import)\s+experiments(\.|\s|$)", l)]
        assert not bad, "the live reader imports from experiments/: %r" % bad[:3]
        print("SUPERSEDED (2026-09-14): the temporal organ is hdlab.temporal_model (consolidated 2026-09-11); the promotion this proof "
              "targeted no longer exists. Self-containment gate: the live reader has 0 experiments/ imports -- PASS")
        return 0
    assert stock_T.__name__.endswith("_temporal_ordering"), stock_T.__name__

    n_ok = 0
    mismatches = []
    with tempfile.TemporaryDirectory() as td:
        paths = []
        for i, d in enumerate(docs):
            p = os.path.join(td, "doc%d.conll" % i)
            gum_to_conll(d, p)
            paths.append(p)

        # PASS 1: stock experiments T
        SRMOD.T = stock_T
        before = {}
        for i, p in enumerate(paths):
            r = SituationReader(); r.gaz = gaz
            before[i] = _serialize(r.read(p))

        # PASS 2: promoted candidate (simulate the import change)
        SRMOD.T = cand
        for i, p in enumerate(paths):
            r = SituationReader(); r.gaz = gaz
            after = _serialize(r.read(p))
            hb = hashlib.sha256(before[i].encode()).hexdigest()[:12]
            ha = hashlib.sha256(after.encode()).hexdigest()[:12]
            if before[i] == after:
                n_ok += 1
            else:
                mismatches.append((i, hb, ha))
        SRMOD.T = stock_T  # restore

    print("=" * 72)
    print("BYTE-IDENTITY (stock experiments.T  vs  promoted hdlab candidate T):")
    print("  docs byte-identical: %d / %d" % (n_ok, len(paths)))
    if mismatches:
        print("  MISMATCHES:")
        for i, hb, ha in mismatches[:10]:
            print("    doc%d: before=%s after=%s" % (i, hb, ha))
        print("VERDICT: FAIL -- promotion is NOT a pure move")
        return 1
    # witness hash over the concatenation of all docs' serializations
    wit = hashlib.sha256("\n@@@\n".join(before[i] for i in range(len(paths))).encode()).hexdigest()
    print("  WITNESS sha256(all %d docs, both passes identical) = %s" % (len(paths), wit))
    print("VERDICT: PASS -- reader.read() is BYTE-IDENTICAL before/after promotion (pure move)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", type=int, default=20)
    a = ap.parse_args()
    sys.exit(run(a.docs))


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
