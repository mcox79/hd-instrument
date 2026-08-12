"""hdlab/foundation_persistence.py -- deterministic save/reload for the reading-grounded
FOUNDATION (hd-instrument, cycle 2, 2026-08-12).

THE GAP THIS CLOSES: hdlab.hd_fact_store.HDFactStore and hdlab.reading_grounding_loop's
ConceptSpace / hdlab.grounding_acquisition_loop's Library both live ONLY in process memory.
Cycle 1 (exp_reading_grounding_loop_cycle1_v1, HARD_PASS, commit e38fd8454) grew a 0->185
concept foundation from real curriculum reading, but every run starts from an EMPTY store --
so the foundation could never ACCUMULATE across cycles. This module is the additive enabler:
it persists the FULL reconstructible state of one reading-loop run to disk and reloads it
byte-for-byte, so a later process can pick up EXACTLY where the prior one left off (SEGMENT N+1
loading segment N's snapshot is functionally indistinguishable from segment N+1 having run in
the same uninterrupted process -- verified by the continuation self-test below, not merely
"looks the same on inspection").

SIDECAR, NOT A REWRITE: this module imports hdlab.hd_fact_store / hdlab.reading_grounding_loop /
hdlab.grounding_acquisition_loop READ-ONLY and adds NO methods to those classes and changes NO
default behavior in them (per the cycle-2 task's explicit "do NOT modify HDFactStore's existing
behavior" instruction, generalized to the other two reused organs). Every function here either
READS public/private attributes to build a plain-data snapshot, or WRITES those same attributes
back onto a freshly-constructed instance of the original class.

WHY THE SYMBOL CODEBOOK MUST BE MATERIALIZED, NOT RE-DERIVED FROM (seed, order):
hdlab.event_bundle.EventBundleCodec._sym_vec draws a FRESH random bipolar vector from a
STATEFUL torch.Generator the FIRST time each symbol string is seen, and appends it to an
ordered codebook (see event_bundle.py _register / _sym_vec). This is deterministic GIVEN a
fixed (seed, first-sight ORDER) but is NOT a pure hash of the symbol string alone -- two
processes that encounter the same symbols in a different order get DIFFERENT vectors for them.
So a reload cannot "recompute the codebook from the seed"; it must persist the ACTUAL materialized
role keys + symbol rows (in their original order) and the generator's raw state bytes (so that
symbols registered for the FIRST TIME after reload continue the exact same pseudorandom stream a
non-interrupted run would have produced -- this is what the continuation self-test below proves).

FORMAT (a directory per snapshot; matches the two existing on-disk conventions in this codebase
-- hdlab.additive_map's safetensors+json split and hdlab.arc_parser's np.savez_compressed --
this module picks the np.savez_compressed + json split so ONE array library (numpy) covers both
the torch-tensor store state (via .numpy()) and the native-numpy ConceptSpace/Library state,
with no extra dependency and no pickle of arbitrary objects):
  store/store_meta.json     -- n_dim, seed, sr_threshold, use_index, relation_cardinality, roles,
                                codec_seed, symbols (ordered), domain_syms (ordered per domain)
  store/store_tensors.npz   -- gen_state (uint8), role_keys, symbol_codebook, fact_vecs, fact_sr_keys
  store/store_facts.json    -- one row per FactRecord (fid order): plaintext + status fields
  concept_space.npz         -- lemmas (ordered), sums (float64, raw un-quantized), d
  library_pending.json      -- PENDING LibraryItems only (lemma, first_min_confirm_pass, patience,
                                traces metadata); terminal ESCALATED items are NOT persisted
                                (disclosed scope decision, see module docstring tail) --
                                terminal GROUNDED items need no separate persistence at all: they
                                are already fully represented by the promoted HDFactStore facts,
                                and a reloaded (empty) Library correctly treats them as "not
                                pending" (falls through to the GATE, which reports them known).
  library_pending_ctx.npz   -- the pending traces' context_vec rows, same order as the json
  manifest.json             -- growth_curve (concatenated across all cycles/segments so far),
                                known_seed, n_occurrences_seen, n_flagged, next_pass_idx (the pass
                                index the NEXT segment's checkpoint() calls must start from, so
                                consolidation_pass's Dumay-Gaskell intervening-pass rule -- an item
                                may not integrate on the very pass it first qualifies -- stays
                                correct across a reload; restarting pass numbering at 0 after every
                                reload would spuriously re-arm that rule for carried-over PENDING
                                items), source_tag, saved_ts_iso

DISCLOSED SCOPE DECISION on ESCALATED items: a word whose evidence conflicted across cycle 1's
occurrences enough to hit PATIENCE_MAX is not carried forward as "permanently given up on" -- it
is simply absent from the reloaded (empty) Library, so a NEW occurrence in cycle-2 material starts
a fresh PENDING item for it. This is a deliberate simplification (not an oversight): re-trying a
previously-incoherent word against genuinely new contexts is a defensible model of memory (an
"escalate" here is "inconclusive so far", not "proven wrong"), and building full escalation-state
persistence is not required to demonstrate the load-bearing property (accumulation of GROUNDED
concepts across cycles) this module exists to enable. Flagged here so it is a stated tradeoff, not
a silent gap (per META_RULE_AC discipline).

ASCII-only. Deterministic: every ordered collection here is either already order-preserving
(fid order, first-sight symbol order) or explicitly sorted (lemma iteration via sorted(...)) --
PROT-023/F.5 compliant. Atomic writes: every file is written to a `.tmp` sibling then
os.replace()'d into place (META_RULE_AH).
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np
import torch

from hdlab.hd_fact_store import HDFactStore, FactRecord
from hdlab.reading_grounding_loop import ConceptSpace, ReadingLoopState, GAP_FLOOR, CTX_D
from hdlab.gap_detector import GapDetector
from hdlab.grounding_acquisition_loop import Library, LibraryItem, Trace

FORMAT_VERSION = 1


# ============================================================================ atomic I/O
def _write_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def _write_npz(path: str, **arrays: np.ndarray) -> None:
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **arrays)
    os.replace(tmp, path)


# ============================================================================ HDFactStore
def save_store(store: HDFactStore, dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)
    codec = store.codec
    meta = {
        "format_version": FORMAT_VERSION,
        "n_dim": store.n_dim,
        "seed": store.seed,
        "sr_threshold": store.sr_threshold,
        "use_index": store.use_index,
        "relation_cardinality": store.relation_cardinality,
        "roles": list(codec.roles),
        "codec_seed": codec.seed,
        "symbols": list(codec._idx2sym),          # first-sight order; load-bearing
        "domain_syms": {d: list(v) for d, v in store._domain_syms.items()},
        "n_facts": len(store._facts),
    }
    _write_json(os.path.join(dir_path, "store_meta.json"), meta)

    gen_state = codec._gen.get_state().numpy()
    role_keys = codec.role_keys.detach().cpu().numpy().astype(np.float32)
    symbol_cb = (codec.codebook().detach().cpu().numpy().astype(np.float32) if codec._rows
                 else np.zeros((0, store.n_dim), dtype=np.float32))
    fact_vecs = (torch.stack([f.vec for f in store._facts], 0).detach().cpu().numpy().astype(np.float32)
                 if store._facts else np.zeros((0, store.n_dim), dtype=np.float32))
    fact_sr_keys = (torch.stack([f.sr_key for f in store._facts], 0).detach().cpu().numpy().astype(np.float32)
                    if store._facts else np.zeros((0, store.n_dim), dtype=np.float32))
    _write_npz(os.path.join(dir_path, "store_tensors.npz"), gen_state=gen_state, role_keys=role_keys,
              symbol_codebook=symbol_cb, fact_vecs=fact_vecs, fact_sr_keys=fact_sr_keys)

    fact_rows = [dict(fid=f.fid, subject=f.subject, relation=f.relation, obj=f.obj, source=f.source,
                      trust_sym=f.trust_sym, trust_level=f.trust_level, status=f.status)
                for f in store._facts]
    _write_json(os.path.join(dir_path, "store_facts.json"), fact_rows)


def load_store(dir_path: str) -> HDFactStore:
    with open(os.path.join(dir_path, "store_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    npz = np.load(os.path.join(dir_path, "store_tensors.npz"))
    with open(os.path.join(dir_path, "store_facts.json"), encoding="utf-8") as f:
        fact_rows = json.load(f)

    store = HDFactStore(n_dim=meta["n_dim"], seed=meta["seed"],
                        relation_cardinality=meta["relation_cardinality"],
                        sr_threshold=meta["sr_threshold"], use_index=meta["use_index"])
    codec = store.codec
    codec.role_keys = torch.from_numpy(npz["role_keys"]).to(torch.float32)
    codec._gen.set_state(torch.from_numpy(npz["gen_state"]).to(torch.uint8))
    codec._sym2idx, codec._idx2sym, codec._rows, codec._cb_cache = {}, [], [], None
    symbol_cb = npz["symbol_codebook"]
    for i, sym in enumerate(meta["symbols"]):
        codec._register(str(sym), torch.from_numpy(symbol_cb[i]).to(torch.float32))

    store._domain_syms = {d: list(v) for d, v in meta["domain_syms"].items()}
    store._domain_seen = {d: set(v) for d, v in store._domain_syms.items()}
    store._cb_cache = {}

    fact_vecs, fact_sr_keys = npz["fact_vecs"], npz["fact_sr_keys"]
    facts: List[FactRecord] = []
    for row, vec, srk in zip(fact_rows, fact_vecs, fact_sr_keys):
        facts.append(FactRecord(fid=row["fid"], vec=torch.from_numpy(vec).to(torch.float32),
                                sr_key=torch.from_numpy(srk).to(torch.float32),
                                subject=row["subject"], relation=row["relation"], obj=row["obj"],
                                source=row["source"], trust_sym=row["trust_sym"],
                                trust_level=row["trust_level"], status=row["status"]))
    store._facts = facts
    store._sr_index = {}
    if store.use_index:
        for f in facts:
            store._sr_index.setdefault(store._sr_key_bytes(f.sr_key), []).append(f.fid)
    return store


# ============================================================================ ConceptSpace
def save_concept_space(space: ConceptSpace, path: str) -> None:
    lemmas = sorted(space._sums.keys())
    sums = (np.stack([space._sums[l] for l in lemmas], 0).astype(np.float64) if lemmas
           else np.zeros((0, space.d), dtype=np.float64))
    _write_npz(path, lemmas=np.array(lemmas), sums=sums, d=np.array([space.d]))


def load_concept_space(path: str) -> ConceptSpace:
    npz = np.load(path)
    d = int(npz["d"][0])
    space = ConceptSpace(d=d)
    lemmas, sums = list(npz["lemmas"]), npz["sums"]
    for i, lem in enumerate(lemmas):
        space._sums[str(lem)] = sums[i].astype(np.float64)
    return space


# ============================================================================ Library (PENDING only)
def save_library_pending(library: Library, json_path: str, npz_path: str, d: int = CTX_D) -> None:
    lemmas = sorted(l for l, it in library.items.items() if it.status == "PENDING")
    items_meta, ctx_rows = [], []
    for lem in lemmas:
        it = library.items[lem]
        items_meta.append({
            "lemma": lem, "first_min_confirm_pass": it.first_min_confirm_pass, "patience": it.patience,
            "traces": [{"episode_id": t.episode_id, "pole": t.pole, "pass_idx": t.pass_idx} for t in it.traces],
        })
        ctx_rows.extend(t.context_vec for t in it.traces)
    _write_json(json_path, {"d": d, "items": items_meta})
    ctx_arr = np.stack(ctx_rows, 0).astype(np.float64) if ctx_rows else np.zeros((0, d), dtype=np.float64)
    _write_npz(npz_path, context_vecs=ctx_arr)


def load_library_pending(json_path: str, npz_path: str) -> Library:
    with open(json_path, encoding="utf-8") as f:
        meta = json.load(f)
    ctx = np.load(npz_path)["context_vecs"]
    lib = Library()
    row = 0
    for item in meta["items"]:
        li = LibraryItem(lemma=item["lemma"], status="PENDING",
                         first_min_confirm_pass=item["first_min_confirm_pass"], patience=item["patience"])
        for tr in item["traces"]:
            li.traces.append(Trace(episode_id=tr["episode_id"], pole=tr["pole"],
                                   context_vec=ctx[row].astype(np.float64), pass_idx=tr["pass_idx"]))
            row += 1
        lib.items[item["lemma"]] = li
    return lib


# ============================================================================ combined foundation
def save_foundation(state: ReadingLoopState, dir_path: str, *, source_tag: str, next_pass_idx: int,
                    growth_curve_all: Optional[List[dict]] = None) -> dict:
    """Persist the FULL reloadable state of one reading-loop run to `dir_path`."""
    os.makedirs(dir_path, exist_ok=True)
    save_store(state.store, os.path.join(dir_path, "store"))
    save_concept_space(state.space, os.path.join(dir_path, "concept_space.npz"))
    save_library_pending(state.library, os.path.join(dir_path, "library_pending.json"),
                         os.path.join(dir_path, "library_pending_ctx.npz"))
    manifest = {
        "format_version": FORMAT_VERSION,
        "saved_ts_iso": datetime.now(timezone.utc).isoformat(),
        "source_tag": source_tag,
        "known_seed": sorted(state.known_seed),
        "n_occurrences_seen": state.n_occurrences_seen,
        "n_flagged": state.n_flagged,
        "next_pass_idx": int(next_pass_idx),
        "gap_floor": GAP_FLOOR,
        "n_facts": len(state.store._facts),
        "n_live_facts": len(state.store.live_facts()),
        "n_pending_library_items": sum(1 for it in state.library.items.values() if it.status == "PENDING"),
        "growth_curve_all": growth_curve_all if growth_curve_all is not None else list(state.growth_curve),
    }
    _write_json(os.path.join(dir_path, "manifest.json"), manifest)
    return manifest


def load_foundation(dir_path: str) -> ReadingLoopState:
    store = load_store(os.path.join(dir_path, "store"))
    space = load_concept_space(os.path.join(dir_path, "concept_space.npz"))
    library = load_library_pending(os.path.join(dir_path, "library_pending.json"),
                                   os.path.join(dir_path, "library_pending_ctx.npz"))
    with open(os.path.join(dir_path, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    state = ReadingLoopState(store=store, library=library, space=space,
                             known_seed=frozenset(manifest["known_seed"]),
                             n_occurrences_seen=manifest["n_occurrences_seen"],
                             n_flagged=manifest.get("n_flagged", 0),
                             growth_curve=list(manifest.get("growth_curve_all", [])))
    state.gap_detector = GapDetector(store, floor=GAP_FLOOR)
    state.gap_detector.refresh()
    return state


def foundation_exists(dir_path: str) -> bool:
    return os.path.isfile(os.path.join(dir_path, "manifest.json"))


def load_manifest(dir_path: str) -> dict:
    with open(os.path.join(dir_path, "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


# ===================== formula self-tests ==========================================
def _build_tiny_state(seed: int) -> ReadingLoopState:
    from hdlab.reading_grounding_loop import seed_known_words, process_sentence, checkpoint
    store = HDFactStore(n_dim=512, seed=seed, relation_cardinality={"KNOWN_WORD": "FUNCTIONAL",
                                                                    "GROUNDED_MEANING": "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["the", "a", "in", "on", "with", "boat", "storm", "before", "harbor"],
                     "seed_persist_test")
    sentences = [
        "Owen moored the flimzat boat before the storm reached the harbor.",
        "The crew moored a flimzat boat before every storm hit the harbor.",
        "Sailors always moor the flimzat boat before a storm nears the harbor.",
    ]
    for i, s in enumerate(sentences):
        process_sentence(state, s, f"g{i}", pass_idx=0)
    checkpoint(state, pass_idx=0, source_tag="persist_test")  # leaves flimzat PENDING (3 < MIN_CONFIRM=4)
    return state


def _selftest_store_roundtrip_identical(tmp_dir: str) -> None:
    """Save then reload an HDFactStore with a handful of facts (incl. a REPLACE/FLAG/COMBINE
    mix, exercising every status) -- every recover_fact()/query()/live_facts() call on the
    reloaded store must match the original bit-for-bit."""
    st = HDFactStore(n_dim=1024, seed=42, relation_cardinality={"capital_of": "FUNCTIONAL",
                                                                "speaks": "MULTIVALUED"}, use_index=True)
    st.store("x", "capital_of", "o1", "art", "TRUST_MID")
    st.store("x", "capital_of", "o2", "book", "TRUST_HIGH")   # REPLACE
    st.store("z", "capital_of", "o1", "aA", "TRUST_MID")
    st.store("z", "capital_of", "o2", "aB", "TRUST_MID")      # FLAG
    st.store("w", "speaks", "en", "aA", "TRUST_MID")
    st.store("w", "speaks", "fr", "aB", "TRUST_MID")          # COMBINE
    for i in range(10):
        st.store(f"s{i}", "capital_of", f"o{i}", "src", "TRUST_MID")

    d = os.path.join(tmp_dir, "store_rt")
    save_store(st, d)
    st2 = load_store(d)

    assert len(st2._facts) == len(st._facts)
    for f1, f2 in zip(st._facts, st2._facts):
        assert (f1.subject, f1.relation, f1.obj, f1.source, f1.trust_sym, f1.status) == \
              (f2.subject, f2.relation, f2.obj, f2.source, f2.trust_sym, f2.status)
        assert torch.equal(f1.vec, f2.vec), "fact vec not bit-identical after reload"
        assert torch.equal(f1.sr_key, f2.sr_key), "sr_key not bit-identical after reload"
    assert torch.equal(st.codec.codebook(), st2.codec.codebook()), "symbol codebook drifted"
    assert torch.equal(st.codec.role_keys, st2.codec.role_keys), "role keys drifted"
    for probe in [("x", "capital_of"), ("z", "capital_of"), ("w", "speaks"), ("s3", "capital_of")]:
        q1 = sorted((d_["fid"], d_["object"], d_["status"]) for d_ in st.query(*probe))
        q2 = sorted((d_["fid"], d_["object"], d_["status"]) for d_ in st2.query(*probe))
        assert q1 == q2, (probe, q1, q2)
    live1 = sorted((f.fid, f.status) for f in st.live_facts())
    live2 = sorted((f.fid, f.status) for f in st2.live_facts())
    assert live1 == live2


def _selftest_continuation_matches_uninterrupted_run(tmp_dir: str) -> None:
    """THE strongest claim: save -> reload -> continue-adding-facts must produce a store
    BIT-IDENTICAL to an uninterrupted run that added the exact same facts without ever saving.
    This proves the generator-state persistence gives true continuation, not just a static
    round-trip of what was already on disk (a store that only round-trips its SAVED content
    but starts a fresh RNG stream on reload would silently give DIFFERENT vectors to any
    genuinely-new symbol seen post-reload -- still "valid" HD vectors, but NOT what this
    self-test demands: proof the boundary is invisible to future computation)."""
    cfg = dict(n_dim=1024, seed=99, relation_cardinality={"rel": "FUNCTIONAL"}, use_index=True)
    first_batch = [(f"a{i}", "rel", f"v{i}", "src", "TRUST_MID") for i in range(5)]
    second_batch = [(f"b{i}", "rel", f"v{i}", "src", "TRUST_MID") for i in range(5)]

    uninterrupted = HDFactStore(**cfg)
    for row in first_batch + second_batch:
        uninterrupted.store(*row)

    interrupted = HDFactStore(**cfg)
    for row in first_batch:
        interrupted.store(*row)
    d = os.path.join(tmp_dir, "store_continue")
    save_store(interrupted, d)
    reloaded = load_store(d)
    for row in second_batch:
        reloaded.store(*row)

    assert len(uninterrupted._facts) == len(reloaded._facts)
    for f1, f2 in zip(uninterrupted._facts, reloaded._facts):
        assert torch.equal(f1.vec, f2.vec), "continuation NOT bit-identical to uninterrupted run"
        assert torch.equal(f1.sr_key, f2.sr_key)
    assert torch.equal(uninterrupted.codec.codebook(), reloaded.codec.codebook())


def _selftest_concept_space_roundtrip(tmp_dir: str) -> None:
    space = ConceptSpace(d=32)
    rng = np.random.default_rng(7)
    for lem in ["dog", "cat", "run"]:
        space.observe(lem, rng.choice([-1.0, 1.0], size=32))
        space.observe(lem, rng.choice([-1.0, 1.0], size=32))
    p = os.path.join(tmp_dir, "cspace.npz")
    save_concept_space(space, p)
    space2 = load_concept_space(p)
    assert space2.anchors() == space.anchors()
    for lem in space.anchors():
        assert np.array_equal(space._sums[lem], space2._sums[lem])
        assert np.array_equal(space.bundle(lem), space2.bundle(lem))


def _selftest_library_pending_roundtrip(tmp_dir: str) -> None:
    state = _build_tiny_state(seed=501)
    pending_before = {l: it for l, it in state.library.items.items() if it.status == "PENDING"}
    assert "flimzat" in pending_before, "test fixture must leave flimzat PENDING (3 traces, need 4)"
    jp = os.path.join(tmp_dir, "lib_pending.json")
    npzp = os.path.join(tmp_dir, "lib_pending_ctx.npz")
    save_library_pending(state.library, jp, npzp)
    lib2 = load_library_pending(jp, npzp)
    assert set(lib2.items.keys()) == set(pending_before.keys())
    for lem, it in pending_before.items():
        it2 = lib2.items[lem]
        assert it2.first_min_confirm_pass == it.first_min_confirm_pass
        assert it2.patience == it.patience
        assert len(it2.traces) == len(it.traces)
        for t1, t2 in zip(it.traces, it2.traces):
            assert t1.episode_id == t2.episode_id and t1.pole == t2.pole and t1.pass_idx == t2.pass_idx
            assert np.array_equal(t1.context_vec, t2.context_vec)


def _selftest_full_foundation_roundtrip_and_resume_grounds(tmp_dir: str) -> None:
    """End-to-end: save a foundation mid-way through grounding a word (3/4 exposures, PENDING),
    reload it, feed the 4th coherent exposure -- the word must GROUND using evidence pooled
    ACROSS the save/reload boundary (the actual cumulative-growth property the mission needs),
    and pass_idx continuation (next_pass_idx) must make the Dumay-Gaskell intervening-pass rule
    behave exactly as an uninterrupted run would."""
    from hdlab.reading_grounding_loop import process_sentence, checkpoint
    state = _build_tiny_state(seed=777)  # flimzat: 3 traces, PENDING, first_min_confirm_pass=None
    d = os.path.join(tmp_dir, "foundation_rt")
    manifest = save_foundation(state, d, source_tag="unit_test_segment_a", next_pass_idx=1)
    assert manifest["n_pending_library_items"] >= 1

    reloaded = load_foundation(d)
    assert "flimzat" in reloaded.library.items
    assert reloaded.library.items["flimzat"].status == "PENDING"
    assert len(reloaded.library.items["flimzat"].traces) == 3
    from hdlab.reading_grounding_loop import is_gap
    assert is_gap(reloaded, "flimzat") is True

    # 4th coherent exposure, in a NEW "process" continuing at next_pass_idx=1 (not restarting at 0)
    process_sentence(reloaded, "They moored the old flimzat boat before the storm entered the harbor.",
                     "g3", pass_idx=1)
    r1 = checkpoint(reloaded, pass_idx=1, source_tag="segment_b")
    assert r1["cumulative_grounded"] == 0, "intervening-pass rule: must not ground on same pass it qualifies"
    r2 = checkpoint(reloaded, pass_idx=2, source_tag="segment_b")
    assert reloaded.library.items["flimzat"].status == "GROUNDED_POS", (
        f"cross-reload evidence pooling failed: {r2}")
    assert is_gap(reloaded, "flimzat") is False


def _run_all_selftests() -> dict:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        _selftest_store_roundtrip_identical(tmp)
        _selftest_continuation_matches_uninterrupted_run(tmp)
        _selftest_concept_space_roundtrip(tmp)
        _selftest_library_pending_roundtrip(tmp)
        _selftest_full_foundation_roundtrip_and_resume_grounds(tmp)
    return {
        "store_roundtrip_identical_ok": True,
        "continuation_matches_uninterrupted_run_ok": True,
        "concept_space_roundtrip_ok": True,
        "library_pending_roundtrip_ok": True,
        "full_foundation_roundtrip_and_resume_grounds_ok": True,
    }


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(_run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
