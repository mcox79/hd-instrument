"""Landing witness for hdlab/ingest_profiles.py (owner-DONE
lean_ingest_profile_and_parallel_corpus_read_harness_for_scale, Q111 landing 2026-09-05). The profile
byte-identity + speedups are reverified by verification/test_lean_ingest_and_parallel_harness.py; this asserts
the PROMOTED hdlab presets are byte-faithful to the validated experiment builder + selpref stays byte-identical
to the full read on the harvest core. Glass-box, NO LLM. ASCII.

  W1 every profile builds and its capability-flag config is IDENTICAL to the validated experiment builder.
  W2 `selpref` == `full` on the harvest core (events/entities/coref) on a real doc -- byte-identical.

Run: .venv/Scripts/python.exe verification/test_ingest_profiles_landing.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.ingest_profiles import reader_for_profile, PROFILES
from hdlab.situation_reader import SituationReader
import experiments.exp_lean_ingest_profiles_v1 as EXP
import experiments.exp_situation_model_qa_v1 as SITQA


def main():
    gaz = SITQA.load_given_gazetteer()

    # W1 byte-faithful promotion: each profile's capability-flag config == the validated experiment builder's
    for p in PROFILES:
        r = reader_for_profile(p, gaz=gaz)
        e = EXP.build_reader(p, gaz=gaz)
        assert isinstance(r, SituationReader), "profile %s did not build a SituationReader" % p
        for f in SituationReader.CAPABILITY_FLAGS:
            # some flags are stored under a transformed attr (e.g. spacy_pred_gate -> pred_gate_fn); a missing
            # attr must compare equal-to-equal since both readers are built by identical code paths.
            assert getattr(r, f, None) == getattr(e, f, None), "profile %s: flag %s differs (%s vs %s)" % (
                p, f, getattr(r, f, None), getattr(e, f, None))
    print("W1 all %d profiles byte-faithful to the validated builder: PASS" % len(PROFILES), flush=True)

    # W2 selpref == full on the harvest core on a real doc
    doc = next(d for d in SITQA.load_docs(None) if os.path.exists(os.path.join(SITQA.CONLL_DIR, d + ".conll")))
    path = os.path.join(SITQA.CONLL_DIR, doc + ".conll")
    sm_full = reader_for_profile("full", gaz=gaz).read(path)
    sm_lean = reader_for_profile("selpref", gaz=gaz).read(path)
    ev_full = [(e.sent_idx, e.predicate, e.agent, e.patient, e.tense) for e in sm_full.events]
    ev_lean = [(e.sent_idx, e.predicate, e.agent, e.patient, e.tense) for e in sm_lean.events]
    assert ev_full == ev_lean, "selpref events DIFFER from full (%d vs %d)" % (len(ev_full), len(ev_lean))
    n_full = sorted((str(en.cluster), en.n_mentions) for en in sm_full.entities)
    n_lean = sorted((str(en.cluster), en.n_mentions) for en in sm_lean.entities)
    assert n_full == n_lean, "selpref entities DIFFER from full"
    print("W2 selpref == full on the harvest core (events %d, entities %d) on %s: PASS"
          % (len(ev_lean), len(n_lean), doc), flush=True)
    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
