"""Skunkworks perf WRAPPER (no edit to atomize_experiment_records.py): bump the regex compile-cache so the
atomizer's ~2103 distinct primitive-tail patterns all stay cached. Default re cache is 512 -> with 2103
patterns it THRASHES (recompiles ~5.8M times across 3673 records). Bumping _MAXCACHE makes each pattern
compile once. OUTPUT-IDENTICAL (same patterns, same matches; speed-only). Runs the atomizer exactly as a
script; set HDLAB_ATOMIZE_* env vars on the launch command as usual.

Flagged to Exp-Dev (tool-owner) for a proper in-tool fix (precompile in build_atom_index) as a follow-up.
"""
import re
re._MAXCACHE = 16384  # >> 2103 distinct primitive-tail patterns; eliminates recompile thrash
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent / "atomize_experiment_records.py"), run_name="__main__")
