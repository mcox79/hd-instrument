"""Catch %-format errors that `py_compile` CANNOT -- they are runtime errors, not syntax errors.

WHY THIS EXISTS (2026-08-20). A diagnostic was edited with `sed`, the substitution silently failed
to match, and the file was left containing `print("\\n%-9s %>0s" % ("arm", ""))`. `py_compile`
reported success, so it was launched, **spent its whole multi-minute corpus read, and only then died
on the print statement** with `ValueError: unsupported format character '>'`. The run was lost after
paying its full cost, and the check that was supposed to prevent that -- "COMPILES OK" -- was
structurally incapable of catching it.

Two lessons, and the second is the general one:
  1. A `sed` substitution that does not match FAILS SILENTLY. Verify the edit took, do not assume it.
  2. **COMPILING IS NOT EXERCISING.** `py_compile` proves the parser accepted the file. It says
     nothing about whether any statement in it can actually run. For anything expensive, exercise
     the cheap surfaces (format strings, argument counts) BEFORE paying for the expensive one --
     this is the same principle as "check every split against what the source actually yields at
     FULL sizes, before the expensive step".

WHAT IT DOES. Walks the AST for `<str-literal> % <something>` and renders each literal against dummy
arguments matched to its conversion types. Reports every literal that raises. This catches invalid
conversion characters and malformed specs. It deliberately does NOT try to verify argument COUNT --
that needs the runtime values -- so a clean report is necessary, not sufficient.

    python tools/check_format_strings.py <file> [<file> ...]
    python tools/check_format_strings.py --self-test
"""
import ast
import re
import sys

_SPEC = re.compile(r"%[-+ #0-9.*]*([a-zA-Z%])")


def _dummy(conv):
    if conv in "diouxX":
        return 1
    if conv in "feEgG":
        return 1.0
    return "x"


def check_source(src, label):
    """Return a list of (lineno, literal, error) for every unrenderable format literal."""
    bad = []
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [(getattr(exc, "lineno", 0), "<file did not parse>", str(exc))]
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
            continue
        left = node.left
        if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
            continue
        lit = left.value
        convs = [c for c in _SPEC.findall(lit) if c != "%"]
        if not convs:
            continue
        try:
            lit % tuple(_dummy(c) for c in convs)
        except Exception as exc:                      # noqa: BLE001 - reporting, not handling
            bad.append((getattr(left, "lineno", 0), lit[:70], "%s: %s" % (type(exc).__name__, exc)))
    return bad


def _self_test():
    """POSITIVE CONTROL: the checker must FIRE on the literal that actually broke the run, and must
    stay silent on a valid one. A checker nobody has seen fire is a checker nobody has tested."""
    broken = 'print("\\n%-9s %>0s" % ("arm", ""))'
    good = 'print("%-9s %8.1f %d" % ("a", 1.5, 2))'
    b = check_source(broken, "broken")
    g = check_source(good, "good")
    assert b, "checker did NOT fire on the literal that broke the real run -- it is useless"
    assert not g, "checker fired on a VALID literal: %s" % g
    print("self-test: fires on the real broken literal %r" % b[0][1])
    print("self-test: silent on a valid literal")
    print("SELF-TEST PASS")
    return 0


def main(argv):
    if not argv or argv[0] == "--self-test":
        return _self_test()
    rc = 0
    for path in argv:
        with open(path, encoding="utf-8") as fh:
            bad = check_source(fh.read(), path)
        if bad:
            rc = 1
            for lineno, lit, err in bad:
                print("%s:%d  BAD FORMAT %r -> %s" % (path, lineno, lit, err))
        else:
            print("%s: all format literals render" % path)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
