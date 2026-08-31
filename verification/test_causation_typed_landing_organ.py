"""Witness for the CAUSATION_TYPED landing into the canonical SituationReader (2026-08-31).

Wires the validated force-dynamic typer (p2 wire_the_causation_typer, STRONG) + the foreground/
event-hood gate (p3, STRONG) into the LIVE reader behind a DEFAULT-OFF `causation_typed` flag, which
delegates to hdlab.causation_typing.read_typed_causation (Talmy/Wolff CAUSE/ENABLE/PREVENT force
dynamics; the WSD/literalness gate + spaCy load LAZILY only when the flag is on).

This proves the WIRING is faithful. The headline numbers (AUTO 0.833 within-clause 3-way) are
INHERITED, not re-derived: the port established that read_typed_causation is BYTE-IDENTICAL to the
validated experiment reader (WiredCausationReader) across 11 configs on a full LitBank doc. This
witness confirms the canonical SituationReader produces that SAME typed output end-to-end.

  (1) DEFAULT-OFF byte-identical: SituationReader() == SituationReader(causation_typed=False) --
      identical causal_links, EMPTY typed_causal_links, and spaCy NOT imported on the default path.
  (2) THE FLAG FIRES: SituationReader(causation_typed=True) produces non-empty typed_causal_links
      with real CAUSE/ENABLE/PREVENT types on a causative doc.
  (3) EQUIVALENCE end-to-end: the canonical reader's typed_causal_links == the validated
      WiredCausationReader's, BYTE-FOR-BYTE -> the landed path inherits the validated result.
ASCII-only, deterministic, CPU-only.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader, _write_temp_conll

# A small doc exercising the CAUSE/ENABLE/PREVENT + abstain paths (lexicon-backed verbs).
_SENTS = [
    "The storm flooded the village .".split(),
    "The guard let the visitors into the hall .".split(),
    "The dam prevented the flood .".split(),
    "The news broke yesterday morning .".split(),      # figurative -> ABSTAIN via the gate
]


def _doc_path():
    rows = []
    for si, toks in enumerate(_SENTS):
        for wi, tok in enumerate(toks):
            rows.append((si, wi, tok, "-"))
    return _write_temp_conll(rows)


def _typed_tuples(links):
    return [(l.sent_idx, l.affector, l.verb, l.patient, l.ctype, l.endstate_reached,
             l.engage_label, getattr(l, "source", None)) for l in links]


def test_causation_typed_landing():
    doc = _doc_path()

    # (1) DEFAULT-OFF byte-identical.
    sm_def = SituationReader().read(doc)
    sm_off = SituationReader(causation_typed=False).read(doc)
    cl_def = [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm_def.causal_links]
    cl_off = [(c.sent_idx, c.cause, c.outcome, c.method) for c in sm_off.causal_links]
    assert cl_def == cl_off, "causal_links must be byte-identical default vs explicit causation_typed=False"
    assert sm_def.typed_causal_links == [] and sm_off.typed_causal_links == [], \
        "typed_causal_links must be EMPTY when the flag is off"
    assert "spacy" not in sys.modules, "spaCy must NOT be imported on the default (off) path"
    print("[1] DEFAULT-OFF byte-identical: causal_links=%d identical; typed empty; spaCy not imported" % len(cl_def))

    # Share one spaCy + lexicon for a deterministic canonical-vs-validated comparison.
    import spacy
    nlp = spacy.load("en_core_web_sm")
    from hdlab.force_dynamics_lexicon import build_force_lexicon
    lex = build_force_lexicon()

    # (2) THE FLAG FIRES through the canonical reader.
    r = SituationReader(causation_typed=True)
    r._causation_nlp = nlp
    r._causation_lex = lex
    sm_on = r.read(doc)
    typed = sm_on.typed_causal_links
    types = [l.ctype for l in typed]
    assert len(typed) >= 2, "flag must fire: expected >=2 typed links, got %d" % len(typed)
    assert any(t == "CAUSE" for t in types) and any(t in ("ENABLE", "PREVENT") for t in types), \
        "expected real CAUSE + ENABLE/PREVENT types, got %r" % types
    print("[2] FLAG FIRES: %d typed links %r through the canonical SituationReader(causation_typed=True)"
          % (len(typed), [(l.verb, l.ctype) for l in typed]))

    # (3) EQUIVALENCE end-to-end: canonical == validated WiredCausationReader (byte-for-byte).
    import experiments.exp_wire_causation_typer_live_reader_v1 as W
    w = W.WiredCausationReader(causation_typed=True, gate_mode="force", nlp=nlp, lexicon=lex)
    sm_w = w.read(doc)
    got = _typed_tuples(typed)
    want = _typed_tuples(sm_w.typed_causal_links)
    assert got == want, ("landed typed_causal_links must EQUAL the validated WiredCausationReader's.\n"
                         "  landed: %r\n  wired : %r" % (got, want))
    print("[3] EQUIVALENCE: canonical reader typed_causal_links == validated WiredCausationReader "
          "(%d links, byte-for-byte) -> inherits the validated result" % len(got))

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_causation_typed_landing()
