"""SUBSTRATE DIRECTOR-KB CONTENT-CHUNK INGEST v2 TRIPWIRE SURFACED (ANCHOR 1 v2 patch; 2026-06-27).

Pre-reg: preregs/2026-06-27_substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced.md

v1 was reported HARD_PASS by agent a38d457eada23b1ae with content-vs-filename
discriminator FIRED+PASSED inside `_instrumentation_selftest`. Skunkworks batch
5 then searched metrics.json + entities.jsonl + atoms.jsonl across all 3 arm
dirs and found NO banana/elephant strings -- discriminator outcome NEVER
surfaced to metrics. Cert tier held back accordingly.

v2 fix: surface the content-vs-filename discriminator as a real ARM with per-
query top-5 atoms + assertion results logged to metrics.json. Persists the
synthetic 2-file KB to the arm workdir for off-disk re-audit.

ARMS (4 total; v1's 3 + new tripwire):
  ARM_CHUNK_SMOKE_NOTES_ONLY                   - unchanged (sanity)
  ARM_CHUNK_FULL                               - unchanged (full envelope)
  ARM_CHUNK_REINGEST_DET                       - unchanged (determinism)
  ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST   - NEW v2 (surfaces to metrics)

HARD_PASS bar:
  all 4 arms ok AND content-vs-filename discriminator both queries content-
  correct AND env (elapsed/cov/avg_chunks).

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import shutil
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


# ---------- envelope thresholds (unchanged from v1) ----------
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
    return os.environ.get(
        "HDLAB_EXP_NAME",
        "substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced",
    )


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


# ---------- arm implementations (v1 arms unchanged) ----------

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


# ---------- NEW v2 arm: content-vs-filename discriminator SURFACED ----------

def _build_synthetic_discriminator_corpus(src_dir: Path) -> None:
    """Two .md files where filename and content INTENTIONALLY disagree:
      elephant_filename_2026-06-26.md -- content is about banana
      banana_filename_2026-06-26.md   -- content is about elephant
    A correct content-ranked KB retrieves files by CONTENT, not by FILENAME.
    """
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "elephant_filename_2026-06-26.md").write_text(
        "# Topic\n\n"
        + (
            "Banana cultivation banana ripening banana tree banana fruit "
            "in tropical climates with banana plantations. " * 6
        ),
        encoding="utf-8",
    )
    (src_dir / "banana_filename_2026-06-26.md").write_text(
        "# Topic\n\n"
        + (
            "Elephant herds elephant social structures elephant migration "
            "elephant savannas with elephant family groups. " * 6
        ),
        encoding="utf-8",
    )


def _assert_content_correct(
    top_atoms: list[dict], query_word: str
) -> tuple[bool, dict]:
    """An atom is content-correct for `query_word` if EITHER:
      (a) the entity text itself contains the query word, OR
      (b) the linked chunk text in source_paths references the file whose
          CONTENT is about query_word (i.e., the opposite-filename file --
          since we built the corpus with intentional name/content mismatch).

    The mapping (deterministic from our build):
      content about "banana"  -> file 'elephant_filename_2026-06-26.md'
      content about "elephant" -> file 'banana_filename_2026-06-26.md'

    Top-1 is content-correct if its top-1 source_paths includes the
    opposite-filename file (= the file whose CONTENT is `query_word`).
    """
    if not top_atoms:
        return False, {"reason": "empty_top_k"}
    top1 = top_atoms[0]
    top1_entity = top1.get("entity", "")
    top1_paths = top1.get("source_paths", [])
    # Case A: entity text directly contains the query word (= content surfaced)
    entity_text_contains = query_word.lower() in top1_entity.lower()
    # Case B: linked source path is the OPPOSITE-filename file
    if query_word.lower() == "banana":
        correct_content_file = "elephant_filename"
    elif query_word.lower() == "elephant":
        correct_content_file = "banana_filename"
    else:
        correct_content_file = None
    source_paths_correct = (
        correct_content_file is not None
        and any(correct_content_file in str(p).lower() for p in top1_paths)
    )
    passed = bool(entity_text_contains or source_paths_correct)
    diag = {
        "query_word": query_word,
        "top1_entity_preview": top1_entity[:200],
        "top1_source_paths": top1_paths,
        "top1_cosine": top1.get("cosine"),
        "entity_text_contains_query": entity_text_contains,
        "source_paths_match_correct_content_file": source_paths_correct,
        "correct_content_file_substr": correct_content_file,
    }
    return passed, diag


def _run_arm_content_vs_filename_discriminator(schema: dict) -> dict:
    """SURFACED v2 arm: build synthetic corpus, ingest, query 'banana' +
    'elephant', record top-5 atoms + assertion outcomes to metrics.json.

    Persists the resulting 2-file KB to arm_workdir so an auditor can re-query
    off-disk if needed.
    """
    arm_dir = _arm_workdir("content_vs_filename")
    src = arm_dir / "src_notes"
    out = arm_dir / "kb"

    t0 = time.perf_counter()
    try:
        _build_synthetic_discriminator_corpus(src)

        synth_plan = {
            "note": {
                "root": src,
                "files": sorted(src.glob("*.md")),
                "skipped_unreachable": False,
            }
        }
        manifest = run_chunk_ingest(
            plan=synth_plan,
            out_dir=out,
            schema=schema,
            n_dim=N_DIM,
            seed=SEED,
            wipe=True,
            redact_timestamps_in_atoms=False,
        )

        # Query the resulting chunk-aware KB
        from hdlab.director_kb_query import DirectorKBQuery  # noqa: PLC0415
        kb = DirectorKBQuery(kb_dir=out)

        banana_result = kb.query(question="banana", k=10, confidence_floor=0.0)
        elephant_result = kb.query(question="elephant", k=10, confidence_floor=0.0)

        banana_top_5 = banana_result.get("top_k_atoms", [])[:5]
        elephant_top_5 = elephant_result.get("top_k_atoms", [])[:5]

        banana_passed, banana_diag = _assert_content_correct(banana_top_5, "banana")
        elephant_passed, elephant_diag = _assert_content_correct(
            elephant_top_5, "elephant"
        )

        # Sanitize top-k atom dicts for json serialization (the kb.query result
        # is already json-safe; we just truncate entity strings for log brevity)
        def _shrink(atom: dict) -> dict:
            return {
                "entity": atom.get("entity", "")[:300],
                "cosine": atom.get("cosine"),
                "source_paths": atom.get("source_paths", []),
                "source_classes": atom.get("source_classes", []),
                "relations": atom.get("relations", [])[:6],
            }

        banana_top_5_clean = [_shrink(a) for a in banana_top_5]
        elephant_top_5_clean = [_shrink(a) for a in elephant_top_5]

        elapsed = time.perf_counter() - t0
        ok = bool(banana_passed and elephant_passed)
        return {
            "arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST",
            "ok": ok,
            "elapsed_s": round(elapsed, 3),
            "kb_persisted_at": str(out),
            "n_chunks_built": manifest["n_chunks"],
            "n_entities_built": manifest["n_entities"],
            "n_triples_built": manifest["n_triples"],
            "banana_query_assertion_passed": bool(banana_passed),
            "banana_query_diag": banana_diag,
            "banana_query_top_5_atoms": banana_top_5_clean,
            "elephant_query_assertion_passed": bool(elephant_passed),
            "elephant_query_diag": elephant_diag,
            "elephant_query_top_5_atoms": elephant_top_5_clean,
            "banana_query_max_cosine": banana_result.get("confidence"),
            "elephant_query_max_cosine": elephant_result.get("confidence"),
            "banana_query_refused": banana_result.get("refused"),
            "elephant_query_refused": elephant_result.get("refused"),
        }
    except Exception as e:  # noqa: BLE001
        elapsed = time.perf_counter() - t0
        return {
            "arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST",
            "ok": False,
            "elapsed_s": round(elapsed, 3),
            "error": f"{type(e).__name__}: {e}",
        }


# ---------- verdict ----------

def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by_name = {a["arm"]: a for a in arms}
    full = by_name.get("ARM_CHUNK_FULL", {})
    det = by_name.get("ARM_CHUNK_REINGEST_DET", {})
    smoke = by_name.get("ARM_CHUNK_SMOKE_NOTES_ONLY", {})
    disc = by_name.get("ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", {})

    if not all(a.get("ok") for a in arms):
        failing = [a["arm"] for a in arms if not a.get("ok")]
        return "HARD_FAIL", (
            f"one_or_more_arms_not_ok: smoke.ok={smoke.get('ok')} "
            f"full.ok={full.get('ok')} det.ok={det.get('ok')} "
            f"disc.ok={disc.get('ok')} failing={failing}"
        )
    if not det.get("ok"):
        return "HARD_FAIL", (
            f"reingest_non_deterministic_principle_2_violation: "
            f"entities_eq={det.get('entities_byte_equal')} "
            f"relations_eq={det.get('relations_byte_equal')} "
            f"atoms_eq={det.get('atoms_byte_equal')} "
            f"w_l2={det.get('w_l2_diff')} (tol={det.get('w_tolerance')})"
        )
    if not (
        disc.get("banana_query_assertion_passed")
        and disc.get("elephant_query_assertion_passed")
    ):
        return "HARD_FAIL", (
            f"content_vs_filename_discriminator_FAILED_to_surface_content: "
            f"banana_passed={disc.get('banana_query_assertion_passed')} "
            f"elephant_passed={disc.get('elephant_query_assertion_passed')} "
            f"(v1 filename-index behavior; v2 architectural improvement not realized)"
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
            f"< {HF_MIN_AVG_CHUNKS_PER_FILE}"
        )

    if (
        full.get("elapsed_s", 1e9) <= HP_MAX_FULL_ELAPSED_S
        and full.get("coverage_ratio", 0.0) >= HP_MIN_COVERAGE
        and full.get("avg_chunks_per_file", 0.0) >= HP_MIN_AVG_CHUNKS_PER_FILE
    ):
        return "HARD_PASS", (
            f"v2_TRIPWIRE_SURFACED: all 4 arms ok; "
            f"banana_passed={disc.get('banana_query_assertion_passed')} "
            f"elephant_passed={disc.get('elephant_query_assertion_passed')}; "
            f"full_elapsed_s={full.get('elapsed_s')} cov={full.get('coverage_ratio')} "
            f"avg_chunks/file={full.get('avg_chunks_per_file')} "
            f"reingest_det_w_l2={det.get('w_l2_diff')}"
        )
    return "MIDDLE_BAND", (
        f"all_4_arms_ok_but_full_outside_HP_band: "
        f"elapsed={full.get('elapsed_s')} cov={full.get('coverage_ratio')} "
        f"avg_chunks/file={full.get('avg_chunks_per_file')}"
    )


# ---------- instrumentation self-test (formula + discriminator parser) ----------

def _instrumentation_selftest() -> None:
    """Formula tests on synthetic arm dicts + discriminator-parser tests."""

    # --- discriminator-parser tests ---
    # entity-text case A: top-1 entity text contains "banana" -> passes
    pass_case_a = [
        {"entity": "banana plantation cultivation", "cosine": 0.9,
         "source_paths": ["elephant_filename_2026-06-26.md"]},
    ]
    ok, _ = _assert_content_correct(pass_case_a, "banana")
    assert ok, "selftest disc case A (entity contains query): expected pass"

    # source-path case B: top-1 source path is opposite-filename file -> passes
    pass_case_b = [
        {"entity": "::chunk::abc", "cosine": 0.9,
         "source_paths": ["elephant_filename_2026-06-26.md"]},
    ]
    ok, _ = _assert_content_correct(pass_case_b, "banana")
    assert ok, "selftest disc case B (opposite-fname path): expected pass"

    # FAIL case: top-1 source path is same-named (= v1 filename-index behavior)
    fail_case = [
        {"entity": "::chunk::xyz", "cosine": 0.9,
         "source_paths": ["banana_filename_2026-06-26.md"]},
    ]
    ok, _ = _assert_content_correct(fail_case, "banana")
    assert not ok, "selftest disc FAIL case (same-fname path): expected fail"

    # empty top -> fail
    ok, _ = _assert_content_correct([], "banana")
    assert not ok, "selftest disc empty top: expected fail"

    # --- formula tests on full-arm dicts ---
    fake_hp = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": True},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": True,
         "banana_query_assertion_passed": True,
         "elephant_query_assertion_passed": True},
    ]
    v, _msg = _verdict_from_arms(fake_hp)
    assert v == "HARD_PASS", f"selftest HP: expected HARD_PASS, got {v} :: {_msg}"

    # disc-failed -> HARD_FAIL
    fake_disc_fail = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET", "ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": True},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": False,
         "banana_query_assertion_passed": False,
         "elephant_query_assertion_passed": True},
    ]
    v2, _msg2 = _verdict_from_arms(fake_disc_fail)
    assert v2 == "HARD_FAIL", f"selftest disc-fail: expected HARD_FAIL, got {v2}"

    # non-det -> HARD_FAIL
    fake_nondet = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET", "ok": False,
         "entities_byte_equal": False, "relations_byte_equal": True,
         "atoms_byte_equal": False, "w_l2_diff": 1.0,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": False},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": True,
         "banana_query_assertion_passed": True,
         "elephant_query_assertion_passed": True},
    ]
    v3, _ = _verdict_from_arms(fake_nondet)
    assert v3 == "HARD_FAIL", f"selftest nondet: expected HARD_FAIL, got {v3}"

    # --- chunker primitive sanity: synthetic 2-header text -> >=3 chunks ---
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
    assert len(chunks) >= 3, f"chunker primitive: expected >=3 chunks got {len(chunks)}"
    headers = {c["header"] for c in chunks if c["header"]}
    assert "Section A" in headers, f"chunker missed Section A: {headers}"
    assert "Section B" in headers, f"chunker missed Section B: {headers}"

    print(
        "[selftest] substrate_director_kb_content_chunk_ingest_v2_tripwire_surfaced "
        "formula+disc-parser+chunker PASS",
        flush=True,
    )


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
        f"[run] {_exp_name()} smoke={smoke} "
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
            f"n_chunks={a.get('n_chunks')} avg_chunks/file={a.get('avg_chunks_per_file')}",
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
            f"n_chunks={a.get('n_chunks')} n_triples={a.get('n_triples')} "
            f"avg_chunks/file={a.get('avg_chunks_per_file')} "
            f"cov={a.get('coverage_ratio')} per_class={a.get('per_class_discovered')}",
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
            f"ent_eq={a.get('entities_byte_equal')} rel_eq={a.get('relations_byte_equal')} "
            f"atoms_eq={a.get('atoms_byte_equal')} w_l2={a.get('w_l2_diff'):.3e}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_CHUNK_REINGEST_DET", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CHUNK_REINGEST_DET FAILED: {e}", flush=True)

    # NEW v2 arm: content-vs-filename discriminator SURFACED to metrics
    try:
        a = _run_arm_content_vs_filename_discriminator(schema)
        arms.append(a)
        print(
            f"  ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST ok={a['ok']} "
            f"elapsed={a['elapsed_s']}s "
            f"banana_pass={a.get('banana_query_assertion_passed')} "
            f"elephant_pass={a.get('elephant_query_assertion_passed')}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST",
                     "ok": False, "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)

    full_arm = next((a for a in arms if a.get("arm") == "ARM_CHUNK_FULL"), {})
    disc_arm = next(
        (a for a in arms if a.get("arm") == "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST"),
        {},
    )

    summary: dict[str, Any] = {
        "anchor": _exp_name(),
        "smoke": smoke,
        "N_DIM": N_DIM,
        "seed": SEED,
        "max_files_per_class": max_files,
        "schema_version": schema.get("schema_version"),
        "schema_hash": schema_hash(schema),
        "kb_version": schema.get("kb_version"),
        "chunk_ingest_version": "v2_tripwire_surfaced",
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
        "cardinality_ok": bool(
            disc_arm.get("n_chunks_built", 0) >= 2
            and full_arm.get("avg_chunks_per_file", 0.0) >= HP_MIN_AVG_CHUNKS_PER_FILE
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
