"""End-to-end ingest pipeline runner: mapper -> adapter -> Phase 6 -> relations.

Closes the "math/science ingest is NOT auto-running" gap from my INGEST_STATUS_RESPONSE.
Chains the 4-step pipeline into one command + tracks per-stage stats + handles common
errors gracefully.

Pipeline stages (per stage, optional skipping):
  1. mapper: substrate_facts_jsonl_to_atoms_v2.py on raw facts.jsonl
            -> mapper-shape JSONL shards
  2. merge:  concat mapper shards (cross-platform; no `cat` dependency)
            -> single mapper-shape JSONL
  3. adapter: substrate_mapper_to_atom_dict_adapter_v1.py
            -> Atom.from_dict-shape JSONL + DEPENDS_ON edges JSONL
  4. atom_ingest: substrate_evolve_phase6_bulk_jsonl.py
            -> substrate +N atoms
  5. edge_ingest: substrate_ingest_math_batch03_relations.py
            -> substrate +M relations

Each stage is independent; --skip-mapper / --skip-adapter / --skip-ingest let you
re-run subsets. Per-stage timing + counts in the final JSON report.

Usage:
  python tools/substrate_ingest_pipeline_runner_v1.py \\
      --facts-jsonl data/external/wikidata/wikidata_truthy_50m.jsonl \\
      --corpus wikidata \\
      --partition wikidata::truthy \\
      --output-prefix data/substrate_state/wikidata_v2_math \\
      --filter math --vocab-mode qclass --max-facts 100000

NO LLM. NO bge. NO torch. Pure stdlib pipeline. Heat-safe; remote_cpu_queue compatible.
"""
from __future__ import annotations
import sys
import json
import time
import subprocess
import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_subprocess(cmd: list, label: str) -> tuple:
    """Run a subprocess; return (exit_code, stdout, elapsed_seconds)."""
    print(f"\n[STAGE: {label}]")
    print(f"  cmd: {' '.join(str(c) for c in cmd)}")
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=21600,  # 6h cap
        )
        elapsed = time.time() - t0
        print(f"  exit={result.returncode}  elapsed={elapsed:.1f}s")
        out_tail = "\n".join(result.stdout.splitlines()[-15:])
        if out_tail:
            print(f"  stdout-tail:\n{out_tail}")
        if result.returncode != 0:
            err_tail = "\n".join(result.stderr.splitlines()[-15:])
            if err_tail:
                print(f"  stderr-tail:\n{err_tail}")
        return result.returncode, result.stdout, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        print(f"  TIMEOUT after {elapsed:.1f}s")
        return 124, "", elapsed
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAILED: {e}")
        return 1, "", elapsed


def merge_mapper_shards(prefix: Path, merged_out: Path) -> int:
    """Concatenate shard_NNNN.jsonl files into one JSONL (cross-platform)."""
    shards = sorted(prefix.parent.glob(prefix.name + ".shard_*.jsonl"))
    if not shards:
        return 0
    line_count = 0
    with merged_out.open("w", encoding="utf-8") as fout:
        for shard in shards:
            with shard.open("r", encoding="utf-8") as fin:
                for line in fin:
                    if line.strip():
                        fout.write(line)
                        line_count += 1
    return line_count


def count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--facts-jsonl", required=True,
                    help="Raw facts JSONL path (input to mapper)")
    ap.add_argument("--corpus", required=True,
                    choices=["wikidata", "conceptnet", "arxiv", "pubmed", "wikipedia"])
    ap.add_argument("--partition", required=True,
                    help="Partition string, e.g. 'wikidata::truthy'")
    ap.add_argument("--output-prefix", required=True,
                    help="Output path prefix; all stage outputs derived from this")
    ap.add_argument("--filter", default="math", choices=["all", "math", "science"])
    ap.add_argument("--vocab-mode", default="qclass",
                    choices=["qclass", "word", "qclass_or_word"])
    ap.add_argument("--shard-size", type=int, default=10000)
    ap.add_argument("--max-facts", type=int, default=None)

    ap.add_argument("--skip-mapper", action="store_true")
    ap.add_argument("--skip-merge", action="store_true")
    ap.add_argument("--skip-adapter", action="store_true")
    ap.add_argument("--skip-atom-ingest", action="store_true")
    ap.add_argument("--skip-edge-ingest", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the pipeline plan; do not execute")
    args = ap.parse_args()

    out_prefix = Path(args.output_prefix)
    mapper_out = out_prefix  # mapper writes <prefix>.shard_NNNN.jsonl
    merged_path = out_prefix.with_name(out_prefix.name + "_merged.jsonl")
    adapted_prefix = out_prefix.with_name(out_prefix.name + "_adapted")
    adapted_atoms = adapted_prefix.with_suffix(".jsonl")
    adapted_relations = adapted_prefix.with_name(adapted_prefix.name + "_relations.jsonl")

    stages = []
    if not args.skip_mapper:
        stages.append(("mapper", [
            sys.executable, "tools/substrate_facts_jsonl_to_atoms_v2.py",
            "--facts-jsonl", args.facts_jsonl,
            "--corpus", args.corpus,
            "--partition", args.partition,
            "--output", str(mapper_out),
            "--filter", args.filter,
            "--vocab-mode", args.vocab_mode,
            "--shard-size", str(args.shard_size),
        ] + (["--max-facts", str(args.max_facts)] if args.max_facts else [])))
    if not args.skip_merge:
        stages.append(("merge", None))  # in-process; not a subprocess
    if not args.skip_adapter:
        stages.append(("adapter", [
            sys.executable, "tools/substrate_mapper_to_atom_dict_adapter_v1.py",
            "--mapper-jsonl", str(merged_path),
            "--output", str(adapted_prefix),
        ]))
    if not args.skip_atom_ingest:
        stages.append(("atom_ingest", [
            sys.executable, "tools/substrate_evolve_phase6_bulk_jsonl.py",
            str(adapted_atoms),
        ]))
    if not args.skip_edge_ingest:
        stages.append(("edge_ingest", [
            sys.executable, "tools/substrate_ingest_math_batch03_relations.py",
            str(adapted_relations),
        ]))

    print(f"=== PIPELINE PLAN ({len(stages)} stages) ===")
    for label, cmd in stages:
        print(f"  - {label}")
    print(f"output-prefix: {out_prefix}")
    print(f"  mapper shards:    {mapper_out}.shard_NNNN.jsonl")
    print(f"  merged:           {merged_path}")
    print(f"  adapted atoms:    {adapted_atoms}")
    print(f"  adapted edges:    {adapted_relations}")

    if args.dry_run:
        print("\n[DRY-RUN] not executing")
        return

    report = {
        "facts_jsonl": args.facts_jsonl,
        "corpus": args.corpus,
        "partition": args.partition,
        "output_prefix": str(out_prefix),
        "filter": args.filter,
        "vocab_mode": args.vocab_mode,
        "stages": [],
    }
    pipeline_t0 = time.time()
    pipeline_failed = False

    for label, cmd in stages:
        if pipeline_failed:
            report["stages"].append({"label": label, "status": "skipped_due_to_prior_failure"})
            continue
        if label == "merge":
            print(f"\n[STAGE: merge]")
            t0 = time.time()
            n = merge_mapper_shards(mapper_out, merged_path)
            elapsed = time.time() - t0
            print(f"  merged {n} lines from shards into {merged_path}  ({elapsed:.1f}s)")
            report["stages"].append({"label": label, "lines_merged": n, "elapsed_seconds": round(elapsed, 1), "status": "ok"})
            if n == 0:
                print(f"  WARNING: no mapper shard output -- stopping pipeline")
                pipeline_failed = True
        else:
            ec, _, elapsed = run_subprocess(cmd, label)
            status = "ok" if ec == 0 else f"failed_exit_{ec}"
            report["stages"].append({"label": label, "exit_code": ec, "elapsed_seconds": round(elapsed, 1), "status": status})
            if ec != 0:
                pipeline_failed = True

    # Post-run counts (best-effort; some files may not exist if early stages skipped)
    report["counts"] = {
        "merged_jsonl_lines": count_jsonl_lines(merged_path),
        "adapted_atoms_lines": count_jsonl_lines(adapted_atoms),
        "adapted_relations_lines": count_jsonl_lines(adapted_relations),
    }
    report["pipeline_wall_seconds"] = round(time.time() - pipeline_t0, 1)
    report["pipeline_status"] = "FAILED" if pipeline_failed else "OK"

    report_path = out_prefix.with_name(out_prefix.name + "_pipeline_report.json")
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n=== PIPELINE COMPLETE: {report['pipeline_status']} ===")
    print(f"wall: {report['pipeline_wall_seconds']}s")
    print(f"counts: merged={report['counts']['merged_jsonl_lines']} "
          f"adapted_atoms={report['counts']['adapted_atoms_lines']} "
          f"adapted_relations={report['counts']['adapted_relations_lines']}")
    print(f"report: {report_path}")
    if pipeline_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
