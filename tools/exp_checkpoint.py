"""Per-unit shard/resume helper for multi-unit experiment cells.

Every completed (arm, seed) unit is appended as one JSON line to
`<output_dir>/units.jsonl` immediately after it finishes, so a killed/hung
run loses at most the in-flight unit, not everything already computed.
Resume = read the shard, skip unit_keys already present, continue in the
same deterministic order the single-shot run would have used.

Public API:
  unit_key(*parts) -> str                       stable id, e.g. unit_key("warm", seed)
  completed_units(output_dir) -> set[str]        unit_keys already recorded
  record_unit(output_dir, key, result) -> None   atomic append of one unit
  load_units(output_dir) -> dict[str, dict]      all recorded {unit_key: result}
"""
import json
import os


def unit_key(*parts) -> str:
    """Build a stable unit id string from arm/seed/etc parts, joined by '|'."""
    return "|".join(str(p) for p in parts)


def _shard_path(output_dir: str) -> str:
    return os.path.join(output_dir, "units.jsonl")


def _iter_valid_records(output_dir: str):
    """Yield parsed dicts from units.jsonl, stopping at the first unparsable line
    (an unparsable line means the file was interrupted mid-append; anything after
    the last complete newline-terminated line is discarded, never half-applied)."""
    path = _shard_path(output_dir)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.endswith("\n"):
                break  # partial/interrupted final line, no trailing newline: discard
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                break  # corrupt line: stop, discard this and anything after
            yield rec


def completed_units(output_dir: str) -> set:
    """Return the set of unit_keys already durably recorded in units.jsonl."""
    return {rec["unit_key"] for rec in _iter_valid_records(output_dir)}


def record_unit(output_dir: str, key: str, result: dict) -> None:
    """Atomically append one unit's result as a single line to units.jsonl.

    Append-only + flush + fsync: a crash mid-write leaves at most one
    unterminated trailing line, which _iter_valid_records discards on read.
    """
    os.makedirs(output_dir, exist_ok=True)
    path = _shard_path(output_dir)
    line = json.dumps({"unit_key": key, "result": result}) + "\n"
    with open(path, "a", encoding="utf-8", newline="") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def load_units(output_dir: str) -> dict:
    """Return {unit_key: result} for all durably recorded units."""
    return {rec["unit_key"]: rec["result"] for rec in _iter_valid_records(output_dir)}


def _selftest():
    """(a) resume skips completed units and finishes the rest; (b) resumed final
    result == single-shot final result (bit-identical, same seed); (c) a corrupt/
    partial trailing line is discarded, not silently included."""
    import shutil
    import tempfile

    base = tempfile.mkdtemp(prefix="exp_checkpoint_selftest_")
    try:
        units = [("armA", 1), ("armA", 2), ("armB", 1), ("armB", 2), ("armB", 3)]

        def compute(arm, seed):
            # deterministic stand-in for a real per-unit computation
            return {"arm": arm, "seed": seed, "value": (hash((arm, seed)) % 997) / 997.0}

        # --- single-shot run: all 5 units in one pass ---
        d_single = os.path.join(base, "single")
        for arm, seed in units:
            k = unit_key(arm, seed)
            record_unit(d_single, k, compute(arm, seed))
        single_final = load_units(d_single)
        assert len(single_final) == 5, "single-shot did not record all units"

        # --- (a) simulated death after 3 units, then resume ---
        d_resume = os.path.join(base, "resume")
        for arm, seed in units[:3]:
            record_unit(d_resume, unit_key(arm, seed), compute(arm, seed))
        # "process dies" here; new process "resumes":
        done = completed_units(d_resume)
        assert done == {unit_key(a, s) for a, s in units[:3]}, "resume did not see prior 3 units"
        n_skipped = 0
        for arm, seed in units:
            k = unit_key(arm, seed)
            if k in done:
                n_skipped += 1
                continue
            record_unit(d_resume, k, compute(arm, seed))
        assert n_skipped == 3, "resume did not skip exactly the 3 completed units"
        resumed_final = load_units(d_resume)
        assert len(resumed_final) == 5, "resume did not complete the remaining units"

        # --- (b) resumed final == single-shot final, bit-identical ---
        assert json.dumps(resumed_final, sort_keys=True) == json.dumps(single_final, sort_keys=True), \
            "resumed final metrics differ from single-shot final metrics"

        # --- (c) atomic/append-only: a corrupt trailing line is discarded ---
        d_corrupt = os.path.join(base, "corrupt")
        record_unit(d_corrupt, unit_key("armA", 1), compute("armA", 1))
        record_unit(d_corrupt, unit_key("armA", 2), compute("armA", 2))
        # simulate an interrupted append: partial JSON, no trailing newline
        with open(_shard_path(d_corrupt), "a", encoding="utf-8", newline="") as f:
            f.write('{"unit_key": "armA|3", "result": {"arm": "armA", "seed"')  # truncated, no \n
        done_c = completed_units(d_corrupt)
        assert done_c == {unit_key("armA", 1), unit_key("armA", 2)}, \
            "corrupt trailing line was not discarded cleanly: %r" % done_c
        loaded_c = load_units(d_corrupt)
        assert len(loaded_c) == 2 and "armA|3" not in loaded_c, \
            "corrupt trailing line leaked into load_units"

        print("[exp_checkpoint] SELFTEST PASS: resume-skip, bit-identical resume, corrupt-tail discard")
        return True
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    ok = _selftest()
    raise SystemExit(0 if ok else 1)
