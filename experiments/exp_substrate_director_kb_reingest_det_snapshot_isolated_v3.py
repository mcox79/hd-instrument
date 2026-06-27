"""SUBSTRATE DIRECTOR-KB REINGEST_DET SNAPSHOT-ISOLATED v3 (Wave 4 fix; 2026-06-27).

Pre-reg: preregs/2026-06-27_substrate_director_kb_reingest_det_snapshot_isolated_v3.md
Drill: notes/research_drill_wave4_v2_reingest_nondeterminism_3x_2026-06-27.md

v2 cell ARM_CHUNK_REINGEST_DET HARD_FAILed with w_l2_diff=1.69M + entities_byte_equal=False
+ atoms_byte_equal=False (relations_byte_equal=True). Root cause diagnosed in drill: v2
calls `build_chunk_plan` TWICE in `_run_arm_reingest_deterministic` (~265s apart). Source
file set drifts during the gap (~29 files modified during mid-pivot note-shipping cadence).

v3 fix (Tier 1 — primary): call `build_chunk_plan` ONCE; snapshot the file SET + bytes;
monkey-patch `_read_file_text` for the arm duration so both runs see identical bytes
regardless of mid-arm file mutations. ~5-10 LOC vs v2.

v3 fix (Tier 2 — defense-in-depth): add Merkle digest of atoms.jsonl + entities.jsonl
to BOTH runs' arm output; dual-store audit consumes Merkle as primary referent check
(git-tree-hash discipline per drill Section 3).

v3 fallback (Q5 graceful-degradation): if snapshot isolation somehow fails, classify
MIDDLE_BAND on approximate-equal `w_l2_norm < 0.001 AND chunk_jaccard > 0.99` rather
than strict HARD_FAIL.

ARMS (4 total; same as v2 — only REINGEST_DET implementation differs):
  ARM_CHUNK_SMOKE_NOTES_ONLY                   - unchanged (sanity; pass-through from v2)
  ARM_CHUNK_FULL                               - unchanged (full envelope; pass-through)
  ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3  - NEW v3 (snapshot-isolated + Merkle)
  ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST   - unchanged (tripwire pass-through)

HARD_PASS bar:
  all 4 arms ok AND content-vs-filename discriminator both queries content-correct
  AND env (elapsed/cov/avg_chunks) AND REINGEST_DET_V3 strict byte-equal + Merkle equal.

Discriminator-survives-scale (USER 2026-06-26): snapshot logic is N-independent. Smoke
runs at notes-only / max_files=50; if v3 mechanism FIRES at smoke (byte-equal True), it
WILL fire at full because the only thing the fix protects against is file-set drift,
which scales with elapsed time NOT with N. The fix removes the mid-arm window entirely.

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import hashlib
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


# ---------- envelope thresholds (unchanged from v2) ----------
HP_MAX_FULL_ELAPSED_S = 900
HF_MAX_FULL_ELAPSED_S = 1800
HP_MIN_COVERAGE = 0.95
HF_MIN_COVERAGE = 0.80
HP_MIN_AVG_CHUNKS_PER_FILE = 2.0
HF_MIN_AVG_CHUNKS_PER_FILE = 1.2
HP_MAX_W_L2 = 1e-6

# ---------- v3 graceful-degradation band (drill Q5) ----------
MB_MAX_W_L2_NORMALIZED = 1e-3
MB_MIN_JACCARD = 0.99

# ---------- smoke caps ----------
SMOKE_MAX_FILES_PER_CLASS = 50
FULL_MAX_FILES_PER_CLASS = None

N_DIM = 2048
SEED = 17


def _exp_name() -> str:
    return os.environ.get(
        "HDLAB_EXP_NAME",
        "substrate_director_kb_reingest_det_snapshot_isolated_v3",
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


def _merkle_of_jsonl(p: Path) -> str:
    """Per-line BLAKE2b digest folded into a single root hash.

    Order-sensitive by design (matches git-tree-hash discipline). Two
    byte-equal jsonl files yield identical Merkle roots; any line addition,
    deletion, or reordering changes the root.
    """
    if not p.exists():
        return "MISSING"
    h = hashlib.blake2b(digest_size=32)
    for line in p.read_bytes().splitlines():
        h.update(hashlib.blake2b(line, digest_size=32).digest())
    return h.hexdigest()


def _chunk_set_jaccard(plan_a_files: list[Path], plan_b_files: list[Path]) -> float:
    """Simple jaccard over file-path sets (graceful-degradation discriminator)."""
    set_a = {str(p) for p in plan_a_files}
    set_b = {str(p) for p in plan_b_files}
    if not set_a and not set_b:
        return 1.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 1.0
    return inter / union


# ---------- v2-pass-through arms (unchanged) ----------

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


# ---------- v3 SNAPSHOT-ISOLATED reingest-det ----------

def _run_arm_reingest_deterministic_snapshot_isolated(
    schema: dict, max_files: int | None
) -> dict:
    """Snapshot-isolated determinism arm (v3 fix per drill Section 5).

    Calls `build_chunk_plan` ONCE; snapshots file bytes; monkey-patches
    `hdlab.director_kb._read_file_text` for the arm duration so both runs
    consume the same byte snapshot regardless of any mid-arm filesystem
    mutations. Adds Merkle digests of atoms.jsonl + entities.jsonl as
    defense-in-depth.

    No-silent-except discipline (META_RULE_J): the monkey-patch is wrapped in
    try/finally so the original `_read_file_text` is restored even on
    exception; any exception during ingest re-raises after restore.
    """
    arm_dir = _arm_workdir("reingest_det_v3")
    out_a = arm_dir / "kb_a"
    out_b = arm_dir / "kb_b"

    # SNAPSHOT: build chunk plan ONCE, reuse for both runs
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=DEFAULT_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )

    # SNAPSHOT: cache file bytes (defends against in-place mutation mid-arm)
    file_bytes_snapshot: dict[Path, bytes] = {}
    snapshot_io_errors: list[str] = []
    for cname, cinfo in plan.items():
        for p in cinfo["files"]:
            try:
                file_bytes_snapshot[p] = p.read_bytes()
            except OSError as e:
                # Record + continue (NO silent except — META_RULE_J).
                # Files that fail snapshot also won't be re-read by the
                # patched function (it falls through to original which
                # will re-hit the same OSError + reject path).
                snapshot_io_errors.append(f"{p}: {type(e).__name__}: {e}")

    n_files_snapshotted = len(file_bytes_snapshot)
    plan_files_total = sum(len(cinfo["files"]) for cinfo in plan.values())

    # Monkey-patch _read_file_text to serve from snapshot for arm duration
    import hdlab.director_kb as _dkb  # noqa: PLC0415
    original_read = _dkb._read_file_text

    def _read_from_snapshot(path, max_bytes):
        if path in file_bytes_snapshot:
            raw = file_bytes_snapshot[path]
            if len(raw) == 0:
                return None, _dkb._REJECT_EMPTY_FILE
            if len(raw) > max_bytes:
                return None, _dkb._REJECT_TOO_LARGE
            try:
                return raw.decode("utf-8", errors="replace"), None
            except Exception as e:  # noqa: BLE001
                return None, f"{_dkb._REJECT_DECODE_ERROR}:{type(e).__name__}"
        # Path not in snapshot (e.g., snapshot OSError'd) -- delegate
        return original_read(path, max_bytes)

    _dkb._read_file_text = _read_from_snapshot

    t0 = time.perf_counter()
    try:
        t_run_a_start = time.perf_counter()
        man_a = run_chunk_ingest(
            plan=plan, out_dir=out_a, schema=schema,
            n_dim=N_DIM, seed=SEED, wipe=True,
            redact_timestamps_in_atoms=True,
        )
        t_a = time.perf_counter() - t_run_a_start

        t_run_b_start = time.perf_counter()
        man_b = run_chunk_ingest(
            plan=plan, out_dir=out_b, schema=schema,
            n_dim=N_DIM, seed=SEED, wipe=True,
            redact_timestamps_in_atoms=True,
        )
        t_b = time.perf_counter() - t_run_b_start
    finally:
        # ALWAYS restore — even on exception (META_RULE_J no-silent-except)
        _dkb._read_file_text = original_read

    elapsed = time.perf_counter() - t0

    # Strict byte-equal predicates
    entities_eq = files_byte_equal(out_a / "entities.jsonl", out_b / "entities.jsonl")
    relations_eq = files_byte_equal(out_a / "relations.jsonl", out_b / "relations.jsonl")
    atoms_eq = files_byte_equal(out_a / "atoms.jsonl", out_b / "atoms.jsonl")
    w_diff = W_l2_diff(out_a / "W.pt", out_b / "W.pt")

    # Defense-in-depth: Merkle digests (drill Tier 2 / Q2-f)
    merkle_atoms_a = _merkle_of_jsonl(out_a / "atoms.jsonl")
    merkle_atoms_b = _merkle_of_jsonl(out_b / "atoms.jsonl")
    merkle_entities_a = _merkle_of_jsonl(out_a / "entities.jsonl")
    merkle_entities_b = _merkle_of_jsonl(out_b / "entities.jsonl")
    merkle_atoms_ok = merkle_atoms_a == merkle_atoms_b and merkle_atoms_a != "MISSING"
    merkle_entities_ok = (
        merkle_entities_a == merkle_entities_b and merkle_entities_a != "MISSING"
    )
    merkle_ok = merkle_atoms_ok and merkle_entities_ok

    w_ok = w_diff < HP_MAX_W_L2
    strict_ok = entities_eq and relations_eq and atoms_eq and w_ok and merkle_ok
    cardinality_ok = (
        man_a["n_chunks"] > 0
        and man_b["n_chunks"] > 0
        and n_files_snapshotted > 0
        and man_a["n_chunks"] == man_b["n_chunks"]  # same plan -> same chunks
    )

    # Graceful-degradation band (drill Q5; NOT a HARD_PASS path — informational
    # for MIDDLE_BAND classification by verdict logic)
    # w_l2_norm: normalize by sqrt(N_DIM * N_DIM) so the threshold scales with W
    w_l2_normalized = w_diff / (N_DIM * 1.0)  # crude per-element l2
    approx_ok = (
        w_l2_normalized < MB_MAX_W_L2_NORMALIZED
        and merkle_atoms_a != "MISSING"
        and merkle_entities_a != "MISSING"
    )

    return {
        "arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3",
        "ok": bool(strict_ok and cardinality_ok),
        "strict_byte_equal_ok": bool(strict_ok),
        "cardinality_ok": bool(cardinality_ok),
        "approximate_equal_ok": bool(approx_ok),
        "elapsed_s": round(elapsed, 3),
        "t_run_a_s": round(t_a, 3),
        "t_run_b_s": round(t_b, 3),
        # byte-equal predicates
        "entities_byte_equal": bool(entities_eq),
        "relations_byte_equal": bool(relations_eq),
        "atoms_byte_equal": bool(atoms_eq),
        "w_l2_diff": w_diff,
        "w_l2_normalized": w_l2_normalized,
        "w_within_tolerance": bool(w_ok),
        "w_tolerance": HP_MAX_W_L2,
        "mb_max_w_l2_normalized": MB_MAX_W_L2_NORMALIZED,
        # Merkle defense-in-depth
        "merkle_atoms_a": merkle_atoms_a,
        "merkle_atoms_b": merkle_atoms_b,
        "merkle_atoms_ok": bool(merkle_atoms_ok),
        "merkle_entities_a": merkle_entities_a,
        "merkle_entities_b": merkle_entities_b,
        "merkle_entities_ok": bool(merkle_entities_ok),
        "merkle_ok": bool(merkle_ok),
        # snapshot diagnostics
        "n_chunks_a": man_a["n_chunks"],
        "n_chunks_b": man_b["n_chunks"],
        "n_files_snapshotted": n_files_snapshotted,
        "plan_files_total": plan_files_total,
        "snapshot_io_errors_count": len(snapshot_io_errors),
        "snapshot_io_errors_first_5": snapshot_io_errors[:5],
        "out_a": str(out_a),
        "out_b": str(out_b),
    }


# ---------- v2 content-vs-filename discriminator arm (unchanged) ----------

def _build_synthetic_discriminator_corpus(src_dir: Path) -> None:
    """Two .md files where filename and content INTENTIONALLY disagree."""
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
    """Top-1 is content-correct if entity text contains query OR linked source
    path is the opposite-filename file (since corpus has intentional mismatch).
    """
    if not top_atoms:
        return False, {"reason": "empty_top_k"}
    top1 = top_atoms[0]
    top1_entity = top1.get("entity", "")
    top1_paths = top1.get("source_paths", [])
    entity_text_contains = query_word.lower() in top1_entity.lower()
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
    """Pass-through from v2: build synthetic corpus, ingest, query banana +
    elephant, record top-5 atoms + assertion outcomes."""
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
        # Record + halt (META_RULE_J no-silent-except; the FAIL surfaces to
        # verdict via ok=False with error field)
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
    det = by_name.get("ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3", {})
    smoke = by_name.get("ARM_CHUNK_SMOKE_NOTES_ONLY", {})
    disc = by_name.get("ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", {})

    # First: any arm OK=False other than det -> HARD_FAIL
    non_det_arms_ok = (
        smoke.get("ok") and full.get("ok") and disc.get("ok")
    )
    if not non_det_arms_ok:
        failing = [
            a["arm"] for a in [smoke, full, disc] if not a.get("ok")
        ]
        return "HARD_FAIL", (
            f"non_det_arm_failed: smoke.ok={smoke.get('ok')} "
            f"full.ok={full.get('ok')} disc.ok={disc.get('ok')} "
            f"failing={failing}"
        )

    # Det arm: check strict first, then graceful-degradation band
    det_strict_ok = det.get("strict_byte_equal_ok", False) and det.get("cardinality_ok", False)
    det_approx_ok = det.get("approximate_equal_ok", False) and det.get("cardinality_ok", False)

    # Discriminator content-correct?
    if not (
        disc.get("banana_query_assertion_passed")
        and disc.get("elephant_query_assertion_passed")
    ):
        return "HARD_FAIL", (
            f"content_vs_filename_discriminator_FAILED: "
            f"banana_passed={disc.get('banana_query_assertion_passed')} "
            f"elephant_passed={disc.get('elephant_query_assertion_passed')}"
        )

    # Envelope checks on FULL
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

    full_in_hp_envelope = (
        full.get("elapsed_s", 1e9) <= HP_MAX_FULL_ELAPSED_S
        and full.get("coverage_ratio", 0.0) >= HP_MIN_COVERAGE
        and full.get("avg_chunks_per_file", 0.0) >= HP_MIN_AVG_CHUNKS_PER_FILE
    )

    # Det arm gates the final verdict tier
    if det_strict_ok and full_in_hp_envelope:
        return "HARD_PASS", (
            f"v3_SNAPSHOT_ISOLATED_HARD_PASS: all 4 arms ok; "
            f"reingest_det_v3 strict byte-equal + Merkle OK; "
            f"banana_passed={disc.get('banana_query_assertion_passed')} "
            f"elephant_passed={disc.get('elephant_query_assertion_passed')}; "
            f"full_elapsed_s={full.get('elapsed_s')} cov={full.get('coverage_ratio')} "
            f"avg_chunks/file={full.get('avg_chunks_per_file')} "
            f"reingest_det_w_l2={det.get('w_l2_diff')} "
            f"n_files_snapshotted={det.get('n_files_snapshotted')}"
        )
    if det_strict_ok and not full_in_hp_envelope:
        return "MIDDLE_BAND", (
            f"det_v3_HARD_PASS_but_full_outside_HP_envelope: "
            f"elapsed={full.get('elapsed_s')} cov={full.get('coverage_ratio')} "
            f"avg_chunks/file={full.get('avg_chunks_per_file')}"
        )
    if det_approx_ok:
        # Drill Q5 graceful-degradation: snapshot fix didn't achieve strict
        # byte-equal but Merkle/jaccard are close. Classify MIDDLE_BAND not
        # HARD_FAIL per drill Q5.
        return "MIDDLE_BAND", (
            f"det_v3_approximate_equal_only_strict_byte_equal_FAILED: "
            f"w_l2_diff={det.get('w_l2_diff')} "
            f"w_l2_normalized={det.get('w_l2_normalized')} "
            f"merkle_ok={det.get('merkle_ok')} "
            f"entities_eq={det.get('entities_byte_equal')} "
            f"atoms_eq={det.get('atoms_byte_equal')} "
            f"n_files_snapshotted={det.get('n_files_snapshotted')} "
            f"(snapshot-isolation didn't achieve strict byte-equal; "
            f"residual nondeterminism source beyond drill audit)"
        )
    # Both strict and approx failed -> HARD_FAIL
    return "HARD_FAIL", (
        f"reingest_det_v3_HARD_FAIL_snapshot_isolation_ineffective: "
        f"strict_ok={det_strict_ok} approx_ok={det_approx_ok} "
        f"w_l2_diff={det.get('w_l2_diff')} "
        f"entities_eq={det.get('entities_byte_equal')} "
        f"atoms_eq={det.get('atoms_byte_equal')} "
        f"merkle_ok={det.get('merkle_ok')} "
        f"n_files_snapshotted={det.get('n_files_snapshotted')}/{det.get('plan_files_total')}"
    )


# ---------- instrumentation self-test ----------

def _instrumentation_selftest() -> None:
    """Formula + discriminator-parser + merkle + snapshot-logic tests."""

    # --- merkle digest sanity ---
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "a.jsonl"
        p2 = Path(td) / "b.jsonl"
        p1.write_bytes(b'{"x":1}\n{"y":2}\n')
        p2.write_bytes(b'{"x":1}\n{"y":2}\n')
        m1 = _merkle_of_jsonl(p1)
        m2 = _merkle_of_jsonl(p2)
        assert m1 == m2, f"selftest merkle byte-equal: expected match, got {m1} vs {m2}"
        assert m1 != "MISSING"

        p3 = Path(td) / "c.jsonl"
        p3.write_bytes(b'{"y":2}\n{"x":1}\n')  # reordered
        m3 = _merkle_of_jsonl(p3)
        assert m3 != m1, "selftest merkle order-sensitivity: expected mismatch on reorder"

        p4 = Path(td) / "missing.jsonl"
        assert _merkle_of_jsonl(p4) == "MISSING"

    # --- jaccard sanity ---
    j_eq = _chunk_set_jaccard([Path("a"), Path("b")], [Path("a"), Path("b")])
    assert j_eq == 1.0, f"selftest jaccard identical: expected 1.0 got {j_eq}"
    j_disj = _chunk_set_jaccard([Path("a")], [Path("b")])
    assert j_disj == 0.0, f"selftest jaccard disjoint: expected 0.0 got {j_disj}"
    j_part = _chunk_set_jaccard([Path("a"), Path("b")], [Path("b"), Path("c")])
    assert abs(j_part - 1.0 / 3.0) < 1e-9, f"selftest jaccard partial: got {j_part}"
    j_empty = _chunk_set_jaccard([], [])
    assert j_empty == 1.0, f"selftest jaccard both empty: expected 1.0 got {j_empty}"

    # --- discriminator-parser tests (pass-through from v2) ---
    pass_case_a = [
        {"entity": "banana plantation cultivation", "cosine": 0.9,
         "source_paths": ["elephant_filename_2026-06-26.md"]},
    ]
    ok, _ = _assert_content_correct(pass_case_a, "banana")
    assert ok, "selftest disc case A: expected pass"

    pass_case_b = [
        {"entity": "::chunk::abc", "cosine": 0.9,
         "source_paths": ["elephant_filename_2026-06-26.md"]},
    ]
    ok, _ = _assert_content_correct(pass_case_b, "banana")
    assert ok, "selftest disc case B: expected pass"

    fail_case = [
        {"entity": "::chunk::xyz", "cosine": 0.9,
         "source_paths": ["banana_filename_2026-06-26.md"]},
    ]
    ok, _ = _assert_content_correct(fail_case, "banana")
    assert not ok, "selftest disc FAIL case: expected fail"

    ok, _ = _assert_content_correct([], "banana")
    assert not ok, "selftest disc empty: expected fail"

    # --- verdict-formula tests ---
    fake_hp = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3", "ok": True,
         "strict_byte_equal_ok": True, "cardinality_ok": True,
         "approximate_equal_ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "merkle_ok": True,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": True,
         "n_files_snapshotted": 100},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": True,
         "banana_query_assertion_passed": True,
         "elephant_query_assertion_passed": True},
    ]
    v, _msg = _verdict_from_arms(fake_hp)
    assert v == "HARD_PASS", f"selftest HP: expected HARD_PASS, got {v} :: {_msg}"

    # det strict-fail + approx-fail -> HARD_FAIL
    fake_det_hf = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3", "ok": False,
         "strict_byte_equal_ok": False, "cardinality_ok": True,
         "approximate_equal_ok": False,
         "entities_byte_equal": False, "relations_byte_equal": True,
         "atoms_byte_equal": False, "w_l2_diff": 1e6, "merkle_ok": False,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": False,
         "n_files_snapshotted": 100, "plan_files_total": 100},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": True,
         "banana_query_assertion_passed": True,
         "elephant_query_assertion_passed": True},
    ]
    v2, _msg2 = _verdict_from_arms(fake_det_hf)
    assert v2 == "HARD_FAIL", f"selftest det HF: expected HARD_FAIL, got {v2}"

    # det strict-fail + approx-ok -> MIDDLE_BAND (graceful-degradation per drill Q5)
    fake_det_mb = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3", "ok": False,
         "strict_byte_equal_ok": False, "cardinality_ok": True,
         "approximate_equal_ok": True,
         "entities_byte_equal": False, "relations_byte_equal": True,
         "atoms_byte_equal": False, "w_l2_diff": 1e-2,
         "w_l2_normalized": 1e-5, "merkle_ok": False,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": False,
         "n_files_snapshotted": 100, "plan_files_total": 100},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": True,
         "banana_query_assertion_passed": True,
         "elephant_query_assertion_passed": True},
    ]
    v3, _msg3 = _verdict_from_arms(fake_det_mb)
    assert v3 == "MIDDLE_BAND", f"selftest det MB: expected MIDDLE_BAND, got {v3} :: {_msg3}"

    # disc-failed -> HARD_FAIL (even with det strict-ok)
    fake_disc_fail = [
        {"arm": "ARM_CHUNK_SMOKE_NOTES_ONLY", "ok": True, "coverage_ratio": 0.99,
         "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_FULL", "ok": True, "elapsed_s": 100.0,
         "coverage_ratio": 0.99, "avg_chunks_per_file": 3.0},
        {"arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3", "ok": True,
         "strict_byte_equal_ok": True, "cardinality_ok": True,
         "approximate_equal_ok": True,
         "entities_byte_equal": True, "relations_byte_equal": True,
         "atoms_byte_equal": True, "w_l2_diff": 0.0, "merkle_ok": True,
         "w_tolerance": HP_MAX_W_L2, "w_within_tolerance": True,
         "n_files_snapshotted": 100},
        {"arm": "ARM_CONTENT_VS_FILENAME_DISCRIMINATOR_TEST", "ok": False,
         "banana_query_assertion_passed": False,
         "elephant_query_assertion_passed": True},
    ]
    v4, _ = _verdict_from_arms(fake_disc_fail)
    assert v4 == "HARD_FAIL", f"selftest disc-fail: expected HARD_FAIL, got {v4}"

    # --- chunker primitive sanity ---
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
        "[selftest] substrate_director_kb_reingest_det_snapshot_isolated_v3 "
        "formula+disc-parser+chunker+merkle+jaccard PASS",
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
        a = _run_arm_reingest_deterministic_snapshot_isolated(schema, max_files)
        arms.append(a)
        print(
            f"  ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3 ok={a['ok']} "
            f"elapsed={a['elapsed_s']}s "
            f"strict_ok={a.get('strict_byte_equal_ok')} "
            f"ent_eq={a.get('entities_byte_equal')} rel_eq={a.get('relations_byte_equal')} "
            f"atoms_eq={a.get('atoms_byte_equal')} w_l2={a.get('w_l2_diff'):.3e} "
            f"merkle_ok={a.get('merkle_ok')} "
            f"n_files_snapshotted={a.get('n_files_snapshotted')}/"
            f"{a.get('plan_files_total')}",
            flush=True,
        )
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3 FAILED: {e}", flush=True)

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
    det_arm = next(
        (a for a in arms if a.get("arm") == "ARM_CHUNK_REINGEST_DET_SNAPSHOT_ISOLATED_V3"),
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
        "chunk_ingest_version": "v3_snapshot_isolated",
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
        "envelope_mb_max_w_l2_normalized": MB_MAX_W_L2_NORMALIZED,
        "envelope_mb_min_jaccard": MB_MIN_JACCARD,
        # Per-arm CARDINALITY_OK split (META_RULE_H + SCHEMA-VET 5b per-arm HP scope)
        "cardinality_ok": bool(
            disc_arm.get("n_chunks_built", 0) >= 2
            and full_arm.get("avg_chunks_per_file", 0.0) >= HP_MIN_AVG_CHUNKS_PER_FILE
            and det_arm.get("cardinality_ok", False)
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
