"""Skunkworks perf WRAPPER (no edit to atomize_experiment_records.py).

Root cause of the slow build: resolve_depends_on does re.search(r'\\b'+tail+r'\\b', text) for ~2103
primitive tails on EACH record's ~8KB text blob -> ~60 billion char-scans over 3673 records. The cost is
SEARCH VOLUME, not compile caching.

FIX (provably output-IDENTICAL): every primitive tail is a maximal [a-z0-9_]+ token (len>=10, contains '_',
all word chars), so `\\btail\\b` matches a text iff `tail` is one of the text's maximal word tokens. So:
tokenize the text ONCE (one findall), then do set-membership for each tail. One scan per record instead of
2103 -> ~2000x fewer scans. Same for the PRIMITIVE_KEYWORDS (all [a-z0-9_]).

SELF-VERIFYING: for the first 200 real records we run BOTH the original re.search path and the fast path and
ASSERT identical output. If the equivalence reasoning is ever wrong, it crashes loudly on real data rather
than silently changing depends_on edges. After 200 clean records -> fast path only.

Flagged to Exp-Dev (tool-owner) for the proper in-tool version. Set HDLAB_ATOMIZE_* on the launch command.
"""
import re
import sys
from pathlib import Path
re._MAXCACHE = 16384
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import importlib.util
_modpath = Path(__file__).resolve().parent / "atomize_experiment_records.py"
_spec = importlib.util.spec_from_file_location("atomize_mod", _modpath)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)   # __name__ != '__main__' -> main() NOT auto-invoked; defs/imports run

_orig_resolve = _mod.resolve_depends_on
_verify = {"n": 0, "max": 200}
_WORD = re.compile(r"[a-z0-9_]+")


def _fast_resolve(text_blob, primitive_targets, all_qids):
    tokens = set(_WORD.findall(text_blob.lower()))
    found = set()
    for tail, q in primitive_targets.items():
        if tail in tokens:
            found.add(q)
    for kw, atom_id in _mod.PRIMITIVE_KEYWORDS.items():
        if kw in tokens:
            q = f"math::{atom_id}"
            if q in all_qids:
                found.add(q)
    out = sorted(found)
    if _verify["n"] < _verify["max"]:
        _verify["n"] += 1
        ref = _orig_resolve(text_blob, primitive_targets, all_qids)
        if ref != out:
            raise AssertionError(
                f"[_fast_resolve] EQUIVALENCE MISMATCH on verify record {_verify['n']}:\n"
                f"  fast={out}\n  orig={ref}")
        if _verify["n"] == _verify["max"]:
            print(f"[_fast_resolve] equivalence VERIFIED on {_verify['max']} real records; "
                  f"fast-path only from here", flush=True)
    return out


_mod.resolve_depends_on = _fast_resolve   # build_atom_spec calls this via module global -> patched
sys.exit(_mod.main())
