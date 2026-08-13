"""Witness: HDFactStore PIPELINE provenance survives a save/reload (flush) cycle and a
legacy fact is NEVER silently attributed to a real pipeline.

WHY THIS EXISTS (source monitoring, not bookkeeping). The brain tags where a memory came
from; losing that tag is the confabulation failure mode -- a weakly-sourced belief becomes
indistinguishable from a well-sourced one. The banked foundation records `source` = the
CORPUS SEGMENT, not the PIPELINE that minted the fact. Two pipelines with wildly different
measured quality (reading/grounding loop vs definitional extractor) feed this store; bank
both under the same schema and they become permanently indistinguishable. This witness
pins the schema-level guarantee that makes them separable BEFORE anything is banked.

GATES (all scaffold-free, real objects, no mocks):
  A  FactRecord / HDFactStore.store expose an explicit `pipeline` field with explicit values.
  B  A fact written with pipeline=DEFINITIONAL_EXTRACTOR reloads with that value intact
     after save_store -> load_store (the "flush" cycle for this store).
  C  ...and is recoverable GLASS-BOX (unbind + cleanup), not only from the plaintext ledger.
  D  A LEGACY row (store_facts.json written with no `pipeline` key at all) loads as
     UNKNOWN_LEGACY and is NOT attributed to any real pipeline.
  E  A LEGACY HD VECTOR (encoded with no PIPELINE binding) recovers as UNKNOWN_LEGACY even
     when exactly one real pipeline symbol is registered -- an unguarded argmax cleanup over
     a one-symbol domain would return that real pipeline for ANY vector, which is precisely
     the misattribution this witness forbids.
  F  The landed canonical store data/foundation/reading_grounding_v1 (READ-ONLY) still loads
     and every one of its facts reads UNKNOWN_LEGACY -- backward compatibility on real data.
  G  NON-REGRESSION: encoding with no pipeline argument is BYTE-IDENTICAL to the pre-change
     encoder. Proven against real landed bytes: re-encoding a canonical fact from its own
     restored codebook must reproduce the on-disk fact vector exactly.

Run: .venv/Scripts/python.exe verification/verify_fact_store_pipeline_provenance.py
Exit 0 = PASS. Any gate failure raises AssertionError (exit 1).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import torch  # noqa: E402

import hdlab.hd_fact_store as hfs  # noqa: E402
from hdlab.foundation_persistence import load_store, save_store  # noqa: E402

CANONICAL_STORE = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v1", "store")

REAL_PIPELINES = ("READING_GROUNDING", "DEFINITIONAL_EXTRACTOR", "SEED_VOCABULARY")
LEGACY = "UNKNOWN_LEGACY"


def _card():
    return {"KNOWN_WORD": "FUNCTIONAL", "GROUNDED_MEANING": "FUNCTIONAL"}


# ---------------------------------------------------------------- A: schema exists
def gate_a_schema_exists() -> dict:
    missing = [n for n in ("PIPELINE_UNKNOWN", "PIPELINE_VALUES", "PIPELINE_ROLE")
               if not hasattr(hfs, n)]
    assert not missing, f"GATE A FAIL: hdlab.hd_fact_store missing {missing}"
    assert hfs.PIPELINE_UNKNOWN == LEGACY, f"GATE A FAIL: PIPELINE_UNKNOWN={hfs.PIPELINE_UNKNOWN!r}"
    for p in REAL_PIPELINES + (LEGACY,):
        assert p in hfs.PIPELINE_VALUES, f"GATE A FAIL: {p!r} not an explicit pipeline value"

    fields = getattr(hfs.FactRecord, "__dataclass_fields__", {})
    assert "pipeline" in fields, "GATE A FAIL: FactRecord has no `pipeline` field"

    import inspect
    sig = inspect.signature(hfs.HDFactStore.store)
    assert "pipeline" in sig.parameters, "GATE A FAIL: HDFactStore.store takes no `pipeline`"
    default = sig.parameters["pipeline"].default
    assert default == LEGACY, (
        f"GATE A FAIL: store() pipeline default is {default!r}; an absent pipeline must default "
        f"to {LEGACY!r}, never to a real pipeline")

    # An unknown pipeline value must be REJECTED, not silently stored.
    st = hfs.HDFactStore(n_dim=512, seed=1, relation_cardinality=_card())
    try:
        st.store("a", "GROUNDED_MEANING", "b", "src", "TRUST_MID", pipeline="NOT_A_PIPELINE")
    except (KeyError, ValueError):
        pass
    else:
        raise AssertionError("GATE A FAIL: an unknown pipeline value was accepted silently")
    return {"pipeline_values": sorted(hfs.PIPELINE_VALUES), "store_default": default}


# ------------------------------------------------- B/C: survives flush + glass-box
def gate_bc_roundtrip(tmp: str) -> dict:
    st = hfs.HDFactStore(n_dim=2048, seed=11, relation_cardinality=_card(), use_index=True)
    st.store("photosynthesis", "GROUNDED_MEANING", "process", "bio_new", "TRUST_MID",
             pipeline="DEFINITIONAL_EXTRACTOR")
    st.store("mitochondrion", "GROUNDED_MEANING", "organelle", "bio_new", "TRUST_MID",
             pipeline="DEFINITIONAL_EXTRACTOR")
    st.store("boat", "GROUNDED_MEANING", "vessel", "reading:ele_cont", "TRUST_MID",
             pipeline="READING_GROUNDING")
    st.store("the", "KNOWN_WORD", "CORE", "seed_base_vocabulary", "TRUST_HIGH",
             pipeline="SEED_VOCABULARY")
    st.store("legacyword", "KNOWN_WORD", "CORE", "reading:bootstrap", "TRUST_MID")  # no pipeline

    d = os.path.join(tmp, "store_pipeline_rt")
    save_store(st, d)

    # the flush ledger must carry the field
    with open(os.path.join(d, "store_facts.json"), encoding="utf-8") as f:
        rows = json.load(f)
    assert all("pipeline" in r for r in rows), "GATE B FAIL: `pipeline` dropped by save_store"

    st2 = load_store(d)
    assert len(st2._facts) == len(st._facts)
    for f1, f2 in zip(st._facts, st2._facts):
        assert f1.pipeline == f2.pipeline, (
            f"GATE B FAIL: pipeline did not survive flush/reload for fid {f1.fid}: "
            f"{f1.pipeline!r} -> {f2.pipeline!r}")
        assert torch.equal(f1.vec, f2.vec), "GATE B FAIL: fact vec not bit-identical after reload"

    got = [f.pipeline for f in st2._facts]
    assert got == ["DEFINITIONAL_EXTRACTOR", "DEFINITIONAL_EXTRACTOR", "READING_GROUNDING",
                   "SEED_VOCABULARY", LEGACY], f"GATE B FAIL: {got}"

    # GATE C: glass-box recovery (unbind + cleanup), on the RELOADED store.
    for f in st2._facts:
        rec = st2.recover_fact(f.vec)
        assert "pipeline" in rec, "GATE C FAIL: recover_fact does not expose `pipeline`"
        assert rec["pipeline"] == f.pipeline, (
            f"GATE C FAIL: glass-box pipeline {rec['pipeline']!r} != ledger {f.pipeline!r} "
            f"for fid {f.fid}")
        # provenance/trust/content must be unharmed by the added binding
        assert rec["subject"] == f.subject and rec["object"] == f.obj
        assert rec["source"] == f.source and rec["trust"] == f.trust_sym
    return {"n_facts": len(st2._facts), "pipelines": got}


# ------------------------------------------- D: legacy LEDGER row -> UNKNOWN_LEGACY
def gate_d_legacy_row_is_unknown(tmp: str) -> dict:
    st = hfs.HDFactStore(n_dim=2048, seed=12, relation_cardinality=_card(), use_index=True)
    st.store("cell", "GROUNDED_MEANING", "unit", "bio_new", "TRUST_MID",
             pipeline="DEFINITIONAL_EXTRACTOR")
    st.store("boat", "GROUNDED_MEANING", "vessel", "reading:ele_cont", "TRUST_MID",
             pipeline="READING_GROUNDING")
    d = os.path.join(tmp, "store_legacy_rows")
    save_store(st, d)

    # Strip the field entirely -- exactly the shape of a pre-change store_facts.json.
    fp = os.path.join(d, "store_facts.json")
    with open(fp, encoding="utf-8") as f:
        rows = json.load(f)
    for r in rows:
        r.pop("pipeline", None)
    tmp_fp = fp + ".tmp"
    with open(tmp_fp, "wb") as f:
        f.write(json.dumps(rows).encode("utf-8"))
    os.replace(tmp_fp, fp)

    st2 = load_store(d)
    for f in st2._facts:
        assert f.pipeline == LEGACY, (
            f"GATE D FAIL: legacy row loaded as {f.pipeline!r}, must be {LEGACY!r}")
        assert f.pipeline not in REAL_PIPELINES, "GATE D FAIL: legacy row attributed to a pipeline"
    return {"n_legacy_rows": len(st2._facts)}


# --------------------------------- E: legacy HD VECTOR must not be misattributed
def gate_e_legacy_vector_is_unknown() -> dict:
    """One real pipeline symbol registered, then a fact stored WITHOUT a pipeline. An
    unguarded argmax cleanup over a one-symbol domain returns that symbol for anything."""
    st = hfs.HDFactStore(n_dim=2048, seed=13, relation_cardinality=_card(), use_index=True)
    st.store("cell", "GROUNDED_MEANING", "unit", "bio_new", "TRUST_MID",
             pipeline="DEFINITIONAL_EXTRACTOR")          # registers the ONLY pipeline symbol
    r = st.store("boat", "GROUNDED_MEANING", "vessel", "reading:ele_cont", "TRUST_MID")
    legacy_vec = st._facts[r.fid].vec
    rec = st.recover_fact(legacy_vec)
    assert rec["pipeline"] == LEGACY, (
        f"GATE E FAIL: an unbound (legacy) vector recovered pipeline={rec['pipeline']!r}; "
        f"a fact with no pipeline binding must read {LEGACY!r}, never a real pipeline")
    assert rec["subject"] == "boat" and rec["object"] == "vessel"
    return {"legacy_vector_pipeline": rec["pipeline"],
            "pipeline_domain": sorted(st._domain_syms.get("PIPELINE", []))}


# ------------------------------------------------- F/G: real landed canonical store
def gate_fg_canonical_store() -> dict:
    if not os.path.isdir(CANONICAL_STORE):
        raise AssertionError(f"GATE F FAIL: canonical store not found at {CANONICAL_STORE}")
    st = load_store(CANONICAL_STORE)          # READ-ONLY; nothing is written back
    n = len(st._facts)
    assert n > 0, "GATE F FAIL: canonical store loaded empty"
    bad = [f.fid for f in st._facts if f.pipeline != LEGACY]
    assert not bad, (f"GATE F FAIL: {len(bad)} canonical facts did not load as {LEGACY!r} "
                     f"(first fids {bad[:5]})")

    # GATE G: default (no-pipeline) encoding is byte-identical to the pre-change encoder.
    # Re-encode landed facts from the store's OWN restored codebook/role keys and compare
    # against the vectors that were written to disk BEFORE this change existed.
    probes = [0, 1, n // 2, n - 2, n - 1]
    for i in probes:
        f = st._facts[i]
        re_enc = st._encode_fact(f.subject, f.relation, f.obj, f.source, f.trust_sym)
        assert torch.equal(re_enc, f.vec), (
            f"GATE G FAIL: default encoding changed -- re-encoding landed fid {f.fid} does not "
            f"reproduce its on-disk vector; the pre-change encoding is NOT preserved")
    return {"canonical_n_facts": n, "all_unknown_legacy": True,
            "reencode_probes_bit_identical": len(probes)}


def main() -> int:
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        out["A_schema"] = gate_a_schema_exists()
        out["BC_flush_roundtrip_and_glassbox"] = gate_bc_roundtrip(tmp)
        out["D_legacy_row_unknown"] = gate_d_legacy_row_is_unknown(tmp)
        out["E_legacy_vector_unknown"] = gate_e_legacy_vector_is_unknown()
        out["FG_canonical_store"] = gate_fg_canonical_store()
    print(json.dumps(out, indent=2, sort_keys=True))
    print("PASS verify_fact_store_pipeline_provenance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
