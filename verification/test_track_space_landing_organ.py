"""Witness for the SPACE (track_space) landing into the canonical SituationReader (2026-08-31).

Wires the validated end-to-end SPACE dimension (experiments/_space_reader.read_locations_in_substrate,
`prior_ext` mode -- the noisy-channel parse-as-evidence+PRIOR best arm) into the live reader behind a
DEFAULT-OFF `track_space` flag, as an ADDITIVE field `sm.locations` (a hdlab.location_register.
LocationRegister; per-entity where_is(entity,t) / present_in_scene). Integrated from
`the_reader_has_no_spatial_location_dimension_end_to_end` (owner-DONE, STRONG). Same default-off +
equivalence-verified pattern as causation/time/verb_subcat.

  (1) DEFAULT-OFF byte-identical: SituationReader() and SituationReader(track_space=False) both leave
      sm.locations == None, and experiments._space_reader is NOT imported on the default path (no new
      hard dependency / no spaCy / no re-parse on the default reader).
  (2) FLAG FIRES + EQUIVALENCE: SituationReader(track_space=True).read(doc).locations answers where_is,
      and its where_is table EQUALS the validated read_locations_in_substrate(doc, prior_ext) register
      byte-for-byte over every (person-entity, t) -- the wiring is faithful, no new logic.
ASCII-only, deterministic (in-substrate parse, no torch/seed), CPU-only; a truncated real LitBank doc.
"""
import os
import sys
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_reader import SituationReader

_SRC = os.path.join(_REPO, "data", "litbank", "coref", "conll", "1023_bleak_house_brat.conll")


def _truncate_conll(src, n_sents):
    out_lines, blanks = [], 0
    with open(src, encoding="utf-8") as f:
        for line in f:
            out_lines.append(line)
            if line.strip() == "":
                blanks += 1
                if blanks >= n_sents:
                    break
    fd, path = tempfile.mkstemp(suffix=".conll")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.writelines(out_lines)
        if not out_lines or out_lines[-1].strip() != "":
            f.write("\n")
    return path


def _where_table(reg, persons, n_sents):
    return {(str(cid), t): reg.where_is(str(cid), t) for cid in persons for t in range(n_sents)}


def test_track_space_landing():
    doc = _truncate_conll(_SRC, n_sents=40)

    # (1) DEFAULT-OFF byte-identical + no import of the space adapter on the default path.
    # pri 137: `experiments._space_reader` is now an ALIAS of the ONE organ `hdlab.space_reader`, so a check
    # that names only the old path can no longer fail -- it must name the ORGAN, which is what the lazy
    # import on the track_space path actually loads.
    assert "hdlab.space_reader" not in sys.modules and "experiments._space_reader" not in sys.modules, \
        "the SPACE organ must not be imported before a track_space reader runs"
    # isolated all-OFF readers (flags default-ON since 2026-09-03): track_belief-default-ON would import
    # _belief_reader -> _space_reader, breaking this isolation check, so build via the canonical all-off factory.
    sm_def = SituationReader.all_capabilities_off().read(doc)
    sm_off = SituationReader.all_capabilities_off(track_space=False).read(doc)
    assert sm_def.locations is None and sm_off.locations is None, \
        "sm.locations must be None when track_space is off"
    assert "hdlab.space_reader" not in sys.modules and "experiments._space_reader" not in sys.modules, \
        "the SPACE organ (hdlab.space_reader) must NOT be imported on the default (off) path"
    print("[1] DEFAULT-OFF byte-identical: sm.locations None on the default reader; space adapter not imported")

    # (2) FLAG FIRES + EQUIVALENCE to the validated read_locations_in_substrate (prior_ext).
    reader = SituationReader.all_capabilities_off(track_space=True)   # isolate track_space vs the validated direct read
    gaz = reader.gaz
    sm_on = reader.read(doc)
    assert sm_on.locations is not None and hasattr(sm_on.locations, "where_is"), \
        "track_space=True must populate sm.locations with a LocationRegister (where_is)"

    # EQUIVALENCE, LIKE FOR LIKE (pri 137, 2026-09-16). This compared the reader's register against the organ
    # called on a DIFFERENT INPUT: `mentions=None` re-parses the coref ANNOTATION COLUMN, while the reader has
    # handed the organ its OWN discovered stream since pri 125 (and, since pri 137, that stream with one file
    # per referent). Two inputs, two registers -- so this check was RED on HEAD for a reason that has nothing
    # to do with the landing it guards (first observed 2026-09-16, pri 137). Feed the organ the stream the
    # reader actually used and the equivalence tests what it claims: the reader adds no logic of its own.
    from hdlab import space_reader as SP      # the ONE organ (experiments._space_reader is its alias)
    # ...and the reader's OWN parse provider. MEASURED 2026-09-16 on this document (40 sentences, 24 tracked
    # persons, 960 (entity,t) cells): with the annotation-column mentions 633 cells differ; with the reader's
    # stream but the STANDALONE frontend 23 still differ -- the reader's per-read parse cache (fed by the
    # pri-112 in-order categories feed) is NOT byte-identical to `PosTagger.load(_POS_ASSET).tag()`, which
    # `extract_events_in_substrate`'s parse_provider comment still claims it is; with both, 0 differ. The
    # 23-cell parse-provider gap is a LOCATED finding handed to the categories rung, not a defect of this
    # landing, and this check now isolates the landing instead of re-measuring that gap.
    reg_direct, _ev, _names, sents, persons = SP.read_locations_in_substrate(
        doc, gaz=gaz, mode="prior_ext", mentions=getattr(reader, "_space_stream", None),
        parse_provider=reader._space_parse_provider)
    n = len(sents)
    tab_reader = _where_table(sm_on.locations, persons, n)
    tab_direct = _where_table(reg_direct, persons, n)
    assert tab_reader == tab_direct, "sm.locations must EQUAL the validated read_locations_in_substrate register"
    # sanity: the register actually answers (at least one where_is is a real node, not all None)
    answered = sum(1 for v in tab_reader.values() if v is not None)
    assert answered > 0, "expected the register to place at least one entity somewhere"
    print("[2] FLAG FIRES + EQUIVALENCE: sm.locations.where_is == read_locations_in_substrate(prior_ext) "
          "byte-for-byte over %d (entity,t) cells (%d placed); %d persons, %d sents"
          % (len(tab_reader), answered, len(persons), n))

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_track_space_landing()
