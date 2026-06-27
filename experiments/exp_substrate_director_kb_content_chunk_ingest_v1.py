"""SUBSTRATE DIRECTOR-KB CONTENT-CHUNK INGEST v1 (ANCHOR 1 v2; TOOLING; 2026-06-26).

Architectural fix for Option A USER 2026-06-26:
  v1 KB is a filename-metadata INDEX (entities = filepaths; cosine returns
  "this file has stuff about your query" -- user must Read the file). v2
  CONTENT-CHUNK ingest produces atoms whose entity = chunk_id and whose
  CHUNK_CONTENT relation carries the actual chunk text; query returns ranked
  content snippets DIRECTLY.

Composes on hdlab.director_kb_chunk_ingest (this cycle's new primitive) +
chain-grade KGStore + CharTrigramEncoder.

ARMS (3 mandatory):
  ARM_CHUNK_SMOKE_NOTES_ONLY   - notes/ only, capped at 50 files; sanity
  ARM_CHUNK_FULL               - notes + memory + prereg + director_plan +
                                  fleet_state (TEXT classes only;
                                  jsonl/api/bio are not chunkable)
  ARM_CHUNK_REINGEST_DET       - run FULL twice; assert byte-equal
                                  entities/relations/atoms (ts-redacted) +
                                  W L2 diff < 1e-6.

SUCCESS CRITERIA (pre-reg HARD_PASS):
  - All 3 arms run without uncaught exceptions
  - ARM_CHUNK_FULL elapsed_s <= 900s (15 min envelope; Principle 9)
  - ARM_CHUNK_FULL coverage_ratio >= 0.95
  - ARM_CHUNK_FULL avg_chunks_per_file >= 2.0 (cardinality_ok)
  - ARM_CHUNK_REINGEST_DET passes exact-equal + W L2 < 1e-6
  - Smoke discriminator: content-query test (synthetic; 'banana zebra phrase')
    matches by content NOT by filename (chunk content present in different-
    named file ranks above same-named empty file)

FAILURE CRITERIA (pre-reg HARD_FAIL):
  - ARM_CHUNK_FULL elapsed_s > 1800s (twice envelope cap)
  - ARM_CHUNK_REINGEST_DET non-deterministic (Principle 2 violation)
  - Coverage < 0.80 (too many silent skips)
  - avg_chunks_per_file < 1.2 (chunker effectively producing 1 chunk per
    file = no benefit over v1 filename index)
  - Smoke discriminator FAILS (content-query returns by filename = same
    behavior as v1 = no architectural improvement)

Anchor: substrate_director_kb_content_chunk_ingest_v1
Queue:  local_cpu_queue
Pre-reg: preregs/2026-06-26_substrate_director_kb_content_chunk_ingest_v1.md
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb import load_schema, schema_hash  # noqa: E402
from hdlab.director_kb_chunk_ingest import (  # noqa: E402
    DEFAULT_CHUNK_CLASSES,
    W_l2_diff,
    build_chunk_plan,
    chunk_text,
    files_byte_equal,
    run_chunk_ingest,
)


# ---------- envelope thresholds (Principle 9 + pre-reg bands) ----------
HP_MAX_FULL_ELAPSED_S = 900
HF_MAX_FULL_ELAPSED_S = 1800
HP_MIN_COVERAGE = 0.95
HF_MIN_COVERAGE = 0.80
HP_MIN_AVG_CHUNKS_PER_FILE = 2.0
HF_MIN_AVG_CHUNKS_PER_FILE = 1.2
HP_MAX_W_L2 = 1e-6

# ---------- smoke caps ----------
SMOKE_MAX_FILES_PER_CLASS = 50
FULL_MAX_FILES_PER_CLASS = None

N_DIM = 2048
SEED = 17


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "substrate_director_kb_content_chunk_ingest_v1")


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _arm_workdir(arm_name: str) -> Path:
    d = _exp_dir() / f"_arm_{arm_name}"
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- arm implementations ----------

def _run_arm_smoke_notes_only(schema: dict, max_files: int | None) -> dict:
    arm_dir = _arm_workdir("smoke_notes_only")
    out_dir = arm_dir / "kb"
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=("note",),
        max_files_per_class=max_files,
    )
    n_disc = sum(len(plan[c]["files"]) for c in plan)
    t0 = time.perf_counter()
    manifest = run_chunk_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=N_DIM,
        seed=SEED,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0
    ok = (
        manifest["n_triples"] > 0
        and manifest["n_chunks"] > 0
        and manifest["n_entities"] > 0
        and manifest["avg_chunks_per_file"] >= 1.0
    )
    return {
        "arm": "ARM_CHUNK_SMOKE_NOTES_ONLY",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "n_discovered": n_disc,
        "n_chunks": manifest["n_chunks"],
        "n_triples": manifest["n_triples"],
        "n_entities": manifest["n_entities"],
        "avg_chunks_per_file": manifest["avg_chunks_per_file"],
        "coverage_ratio": manifest["coverage_ratio"],
        "out_dir": str(out_dir),
    }


def _run_arm_full(schema: dict, max_files: int | None) -> dict:
    arm_dir = _arm_workdir("full")
    out_dir = arm_dir / "kb"
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=DEFAULT_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )
    per_class_disc = {c: len(plan[c]["files"]) for c in plan}
    n_disc = sum(per_class_disc.values())
    t0 = time.perf_counter()
    manifest = run_chunk_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=N_DIM,
        seed=SEED,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0
    n_classes_with_files = sum(1 for c in per_class_disc.values() if c > 0)
    ok = (
        manifest["n_triples"] > 0
        and manifest["n_chunks"] > 0
        and manifest["n_entities"] > 0
        and n_classes_with_files >= 2
        and manifest["avg_chunks_per_file"] >= HF_MIN_AVG_CHUNKS_PER_FILE
    )
    return {
        "arm": "ARM_CHUNK_FULL",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "n_discovered": n_disc,
        "per_class_discovered": per_class_disc,
        "n_chunks": manifest["n_chunks"],
        "n_triples": manifest["n_triples"],
        "n_entities": manifest["n_entities"],
        "n_relations": manifest["n_relations"],
        "avg_chunks_per_file": manifest["avg_chunks_per_file"],
        "coverage_ratio": manifest["coverage_ratio"],
        "out_dir": str(out_dir),
    }


def _run_arm_reingest_deterministic(schema: dict, max_files: int | None) -> dict:
    """LOAD-BEARING: Principle 2 wipe-and-rebuild safety for chunk-ingest."""
    arm_dir = _arm_workdir("reingest_det")
    out_a = arm_dir / "kb_a"
    out_b = arm_dir / "kb_b"
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=DEFAULT_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )
    t0 = time.perf_counter()
    man_a = run_chunk_ingest(
        plan=plan, out_dir=out_a, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=True,
    )
    t_a = time.perf_counter() - t0
    t1 = time.perf_counter()
    plan2 = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=DEFAULT_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )
    man_b = run_chunk_ingest(
        plan=plan2, out_dir=out_b, schema=schema,
        n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=True,
    )
    t_b = time.perf_counter() - t1
    elapsed = time.perf_counter() - t0

    entities_eq = files_byte_equal(out_a / "entities.jsonl", out_b / "entities.jsonl")
    relations_eq = files_byte_equal(out_a / "relations.jsonl", out_b / "relations.jsonl")
    atoms_eq = files_byte_equal(out_a / "atoms.jsonl", out_b / "atoms.jsonl")
    w_diff = W_l2_diff(out_a / "W.pt", out_b / "W.pt")
    w_ok = w_diff < HP_MAX_W_L2

    ok = entities_eq and relations_eq and atoms_eq and w_ok

    return {
        "arm": "ARM_CHUNK_REINGEST_DET",
        "ok": bool(ok),
        "elapsed_s": round(elapsed, 3),
        "t_run_a_s": round(t_a, 3),
        "t_run_b_s": round(t_b, 3),
        "entities_byte_equal": bool(entities_eq),
        "relations_byte_equal": bool(relations_eq),
        "atoms_byte_equal": bool(atoms_eq),
        "w_l2_diff": w_diff,
        "w_within_tolerance": bool(w_ok),
        "w_tolerance": HP_MAX_W_L2,
        "n_chunks_a": man_a["n_chunks"],
        "n_chunks_b": man_b["n_chunks"],
    }


# ---------- verdict ----------

def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by_name = {a["arm"]: a for a in arms}
    full = by_name.get("ARM_CHUNK_FULL", {})
    det = by_name.get("ARM_CHUNK_REINGEST_DET", {})
    smoke = by_name.get("ARM_CHUNK_SMOKE_NOTES_ONLY", {})

    if not all(a.get("ok") for a in arms):
        return "HARD_FAIL", (
            f"one_or_more_arms_not_ok: smoke.ok={smoke.get('ok')} "
            f"full.ok={full.get('ok')} det.ok={det.get('ok')}"
        )
    if not det.get("ok"):
        return "HARD_FAIL", (
            f"reingest_non_deterministic_principle_2_violation: "
            f"entities_eq={det.get('entities_byte_equal')} "
            f"relations_eq={det.get('relations_byte_equal')} "
            f"atoms_eq={det.get('atoms_byte_equal')} "
            f"w_l2={det.get('w_l2_diff')} (tol={det.get('w_tolerance')})"
        )
    if full.get("elapsed_s", 1e9) > HF_MAX_FULL_ELAPSED_S:
        return "HARD_FAIL", (
            f"full_chunk_ingest_exceeds_hf_envelope: "
            f"elapsed_s={full.get('elapsed_s')} > {HF_MAX_FULL_ELAPSED_S}"
        )
    if full.get("coverage_ratio", 0.0) < HF_MIN_COVERAGE:
        return "HARD_FAIL", (
            f"full_coverage_below_hf_band: coverage={full.get('coverage_ratio')} "
            f"< {HF_MIN_COVERAGE}"
        )
    if full.get("avg_chunks_per_file", 0.0) < HF_MIN_AVG_CHUNKS_PER_FILE:
        return "HARD_FAIL", (
            f"chunker_degenerate_one_chunk_per_file: "
            f"avg_chunks_per_file={full.get('avg_chunks_per_file')} "
            f"< {HF_MIN_AVG_CHUNKS_PER_FILE} (no benefit over v1 filename index)"
        )

    if (
        full.get("elapsed_s", 1e9) <= HP_MAX_FULL_ELAPSED_S
        and full.get("coverage_ratio", 0.0) >= HP_MIN_COVERAGE
        and full.get("avg_chunks_per_file", 0.0) >= HP_MIN_AVG_CHUNKS_PER_FILE
    ):
        return "HARD_PASS", (
            f"all_3_arms_ok; full_elapsed_s={full.get('elapsed_s')} "
            f"<= {HP_MAX_FULL_ELAPSED_S}; coverage={full.get('coverage_ratio')} "
            f">= {HP_MIN_COVERAGE}; avg_chunks/file={full.get('avg_chunks_per_file')} "
            f">= {HP_MIN_AVG_CHUNKS_PER_FILE}; reingest_det_w_l2={det.get('w_l2_diff')} "
            f"< {HP_MAX_W_L2}"
        )

    return "MIDDLE_BAND", (
        f"all_3_arms_ok_but_outside_HP_band: "
        f"elapsed={full.get('elapsed_s')} cov={full.get('coverage_ratio')} "
        f"avg_chunks/file={full.get('avg_chunks_per_file')}"
    )


# ---------- instrumentation self-test (formula-selftests; at import) ----------

def _instrumentation_selftest() -> None:
    """Formula + chunker discriminator + content-vs-filename discriminator."""

    # --- formula tests (HP/HF/MB) ---
    fake_hf = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0, "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET", "ok": False,
         "entities_byte_equal": False, "relations_byte_equal": True,
         "atoms_byte_equal": False, "w_l2_diff": 1.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": False},
    ]
    v, _ = _verdict_from_arms(fake_hf)
    assert v == "HARD_FAIL", f"selftest non-det: expected HARD_FAIL, got {v}"

    fake_degen = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99, "avg_chunks_per_file": 1.0},
        {"arm": "ARM_CHUNK_FULL", "ok": False, "elapsed_s": 100.0, "coverage_ratio": 0.99, "avg_chunks_per_file": 1.0},
        {"arm": "ARM_CHUNK_REINGEST_DET", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": True},
    ]
    v2, _ = _verdict_from_arms(fake_degen)
    assert v2 == "HARD_FAIL", f"selftest degen-chunker: expected HARD_FAIL, got {v2}"

    fake_hp = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0, "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "w_tolerance": HP_MAX_W_L2,
         "w_within_tolerance": True},
    ]
    v3, _ = _verdict_from_arms(fake_hp)
    assert v3 == "HARD_PASS", f"selftest HP: expected HARD_PASS, got {v3}"

    # --- chunker discriminator: synthetic text with 2 headers -> >= 2 chunks ---
    synthetic = (
        "# Title\n\nIntro paragraph one with some text.\n\n"
        + "Paragraph two of intro with more text here.\n\n"
        + "## Section A\n\n"
        + ("This is section A content. " * 30) + "\n\n"
        + ("More section A content with banana zebra phrase markers. " * 20) + "\n\n"
        + "## Section B\n\n"
        + ("Different content in section B. " * 30) + "\n\n"
    )
    chunks = chunk_text(synthetic)
    assert len(chunks) >= 3, f"chunker discriminator: expected >=3 chunks got {len(chunks)}"
    headers_seen = {c["header"] for c in chunks if c["header"]}
    assert "Section A" in headers_seen, f"chunker missed Section A header: {headers_seen}"
    assert "Section B" in headers_seen, f"chunker missed Section B header: {headers_seen}"
    # content present in chunks
    all_content = " ".join(c["content"] for c in chunks)
    assert "banana zebra phrase" in all_content, "chunker dropped marker content"

    # --- content-vs-filename discriminator (smoke must fire this) ---
    # Build a tiny synthetic corpus: file A has filename mentioning "elephant"
    # but content about "banana"; file B has filename mentioning "banana" but
    # content about "elephant". Ingest at chunk granularity; query for "banana"
    # should rank file A's chunk above file B's chunk (content > filename).
    schema = load_schema(REPO)
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        src = tdp / "src_notes"
        src.mkdir()
        (src / "elephant_filename_2026-06-26.md").write_text(
            "# Topic\n\n" + ("Banana cultivation banana ripening banana tree banana fruit "
                              "in tropical climates with banana plantations. " * 6),
            encoding="utf-8",
        )
        (src / "banana_filename_2026-06-26.md").write_text(
            "# Topic\n\n" + ("Elephant herds elephant social structures elephant migration "
                              "elephant savannas with elephant family groups. " * 6),
            encoding="utf-8",
        )

        # Build a one-off plan that points class 'note' at our synthetic dir
        synth_plan = {
            "note": {
                "root": src,
                "files": sorted(src.glob("*.md")),
                "skipped_unreachable": False,
            }
        }
        out = tdp / "kb"
        man = run_chunk_ingest(
            plan=synth_plan, out_dir=out, schema=schema,
            n_dim=N_DIM, seed=SEED, wipe=True, redact_timestamps_in_atoms=False,
        )
        assert man["n_chunks"] >= 2, f"discriminator: expected >=2 chunks got {man['n_chunks']}"

        # Query via the chunk-aware path
        from hdlab.director_kb_query import DirectorKBQuery  # noqa: PLC0415
        kb = DirectorKBQuery(kb_dir=out)
        result = kb.query(question="banana", k=10, confidence_floor=0.0)
        assert result["top_k_atoms"], "discriminator: empty top_k"

        # CONTENT-VS-FILENAME DISCRIMINATOR (load-bearing):
        # In the chunk KB, three entity TYPES coexist: chunk_ids (`::chunk`),
        # filenames (`...md`), and content-tag entities (chunk text). All are
        # encoded by their TEXT. A correct content-ranked KB returns
        # banana-content entities OR chunk_ids whose IS_CHUNK_OF source is the
        # elephant_filename file (the file whose CONTENT is banana). The
        # WRONG behavior (v1 filename-index) would surface "banana_filename"
        # filename entities at the top.
        # Check: among the top-k results, the top-ranked source_path entity
        # references the file whose CONTENT matches the query, NOT the file
        # whose FILENAME matches.
        top_atoms = result["top_k_atoms"][:5]
        # The source_paths field carries the rel_path of any file linked to
        # the entity. For a chunk entity, source_paths includes the file it
        # was chunked from; for a content-tag entity, source_paths includes
        # the file whose chunk contains that text.
        for rank, atom in enumerate(top_atoms):
            paths = atom.get("source_paths", [])
            for p in paths:
                if "elephant_filename" in p:
                    elephant_rank = rank
                    break
                if "banana_filename" in p:
                    banana_rank = rank
                    break
            else:
                continue
            break

        elephant_ranks = [r for r, a in enumerate(top_atoms)
                          if any("elephant_filename" in p for p in a.get("source_paths", []))]
        banana_ranks = [r for r, a in enumerate(top_atoms)
                        if any("banana_filename" in p for p in a.get("source_paths", []))]
        # Either: elephant ranks higher than banana (best path-tagged result wins),
        # OR top entity is a banana-content string (content directly surfaced).
        top_ent = top_atoms[0]["entity"]
        content_directly_surfaced = ("banana" in top_ent.lower()
                                      and "filename" not in top_ent.lower())
        if not content_directly_surfaced:
            assert elephant_ranks, (
                f"discriminator FAILED: no elephant_filename in top-{len(top_atoms)} "
                f"paths and top entity is not a banana-content string: top='{top_ent[:80]}'"
            )
            if banana_ranks:
                assert elephant_ranks[0] < banana_ranks[0], (
                    f"discriminator FAILED: banana_filename ranks ({banana_ranks}) "
                    f"above elephant_filename ranks ({elephant_ranks}); v1 filename-"
                    f"index behavior, NOT content-ranked retrieval"
                )

    print("[selftest] substrate_director_kb_content_chunk_ingest_v1 "
          "formula+chunker+content-vs-filename PASS", flush=True)


_instrumentation_selftest()


# ---------- main ----------

def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    max_files = SMOKE_MAX_FILES_PER_CLASS if smoke else FULL_MAX_FILES_PER_CLASS
    out_dir = _exp_dir()
    schema = load_schema(REPO)

    t0 = time.time()
    print(
        f"[run] substrate_director_kb_content_chunk_ingest_v1 smoke={smoke} "
        f"N_DIM={N_DIM} seed={SEED} max_files_per_class={max_files} "
        f"schema_hash={schema_hash(schema)[:12]}",
        flush=True,
    )

    arms: list[dict] = []
    try:
        a = _run_arm_smoke_notes_only(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_CHUNK_SMOKE_NOTES_ONLY ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_chunks={a['n_chunks']} avg_chunks/file={a['avg_chunks_per_file']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CHUNK_SMOKE_NOTES_ONLY FAILED: {e}", flush=True)

    try:
        a = _run_arm_full(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_CHUNK_FULL ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"n_chunks={a['n_chunks']} n_triples={a['n_triples']} "
            f"avg_chunks/file={a['avg_chunks_per_file']} "
            f"cov={a['coverage_ratio']} per_class={a['per_class_discovered']}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_CHUNK_FULL", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CHUNK_FULL FAILED: {e}", flush=True)

    try:
        a = _run_arm_reingest_deterministic(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_CHUNK_REINGEST_DET ok={a['ok']} elapsed={a['elapsed_s']}s "
            f"ent_eq={a['entities_byte_equal']} rel_eq={a['relations_byte_equal']} "
            f"atoms_eq={a['atoms_byte_equal']} w_l2={a['w_l2_diff']:.3e}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_CHUNK_REINGEST_DET", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CHUNK_REINGEST_DET FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    summary: dict[str, Any] = {
        "anchor": "substrate_director_kb_content_chunk_ingest_v1",
        "smoke": smoke,
        "N_DIM": N_DIM,
        "seed": SEED,
        "max_files_per_class": max_files,
        "schema_version": schema.get("schema_version"),
        "schema_hash": schema_hash(schema),
        "kb_version": schema.get("kb_version"),
        "chunk_ingest_version": "v1",
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "envelope_hp_max_full_elapsed_s": HP_MAX_FULL_ELAPSED_S,
        "envelope_hf_max_full_elapsed_s": HF_MAX_FULL_ELAPSED_S,
        "envelope_hp_min_coverage": HP_MIN_COVERAGE,
        "envelope_hf_min_coverage": HF_MIN_COVERAGE,
        "envelope_hp_min_avg_chunks_per_file": HP_MIN_AVG_CHUNKS_PER_FILE,
        "envelope_hf_min_avg_chunks_per_file": HF_MIN_AVG_CHUNKS_PER_FILE,
        "envelope_hp_max_w_l2": HP_MAX_W_L2,
        # cardinality_ok pre-reg field (per new discipline 2026-06-26)
        "cardinality_ok": bool(
            any(a.get("arm") == "ARM_CHUNK_FULL"
                and a.get("avg_chunks_per_file", 0.0) >= HP_MIN_AVG_CHUNKS_PER_FILE
                for a in arms)
        ),
    }
    payload = {
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
