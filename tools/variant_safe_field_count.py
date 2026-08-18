"""Variant-safe field-value counter for data/substrate_index/*/atoms.jsonl.

Promoted from scratch/_iam_axes2.py (2026-08-15,
.claude/scan-out/identical-across-models.json, JOB_2). Incident: a literal match on
cert_status == "chain_grade" counted 59 atoms; the store also carries the hyphenated spelling
"chain-grade" (10 atoms), so the literal-match count UNDER-counted by 17%. The same drift shows
on a second field in the same store: "proven-bound" 209 rows vs "proven_bound" 35 -- an
independent field with the identical hazard. The store has 390+ distinct raw cert_status
strings; any single-spelling `==` or `in` check against a field this repo writes by hand is
liable to miss variants. "Any field-value count in this repo must be spelling-variant-safe or
it is wrong" (2026-08-15 directive).

Generalises the original (hardcoded to cert_status/provenance_quality/CHAIN_GRADE) to any
field name(s) and any target value, so the same variant-safety applies the next time a count
is needed on a field nobody has audited yet.

Usage:
    .venv/Scripts/python.exe tools/variant_safe_field_count.py --self-test
    .venv/Scripts/python.exe tools/variant_safe_field_count.py --field cert_status --value chain_grade
    .venv/Scripts/python.exe tools/variant_safe_field_count.py --field provenance_quality --value CERT_CHAIN_GRADE
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json
import collections

REPO = "D:/AI/hd-instrument"
DEFAULT_SI = os.path.join(REPO, "data", "substrate_index")


def norm(s):
    """Normalise a field value for variant-safe comparison: lowercase, hyphen/space -> underscore.
    Deliberately conservative -- it merges spelling variants of the SAME token, not different
    tokens that happen to share a substring (see the over-merge negatives in the self-test)."""
    return str(s).strip().lower().replace("-", "_").replace(" ", "_")


def getfield(atom, name):
    """Read a field from an atom dict, checking top-level first, then a nested 'metadata' dict
    -- this store has atoms where the same logical field lives in either place, and some atoms
    where 'metadata' itself is a bare string rather than a dict (crash-safe: returns None)."""
    if isinstance(atom, dict):
        if name in atom and atom[name] is not None:
            return atom[name]
        md = atom.get("metadata")
        if isinstance(md, dict) and md.get(name) is not None:
            return md[name]
    return None


def iter_atoms(substrate_index_dir=DEFAULT_SI):
    """Yield (corpus_name, atom_dict) for every parseable atom.jsonl line across all corpora.
    Uses os.scandir per CLAUDE.md convention; skips unparseable lines rather than raising."""
    with os.scandir(substrate_index_dir) as it:
        corpora = sorted(e.name for e in it if e.is_dir())
    for corp in corpora:
        p = os.path.join(substrate_index_dir, corp, "atoms.jsonl")
        if not os.path.isfile(p):
            continue
        with open(p, "rb") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    a = json.loads(ln.decode("utf-8", "replace"))
                except Exception:
                    continue
                yield corp, a


def variant_safe_count(field, target_value, substrate_index_dir=DEFAULT_SI, fields_extra=()):
    """Count atoms whose `field` value normalises to the same token as `target_value`, across
    all corpora. Also returns the raw (un-normalised) values that matched, for auditability --
    a count with no visibility into WHICH spellings it merged is not trustworthy per the
    field-value-count-is-wrong-unless-variant-safe directive.

    fields_extra: additional field names to co-report on the matching atoms (e.g. checking what
    provenance_quality the cert_status matches carry) -- returned as a Counter per extra field.
    """
    target_norm = norm(target_value)
    raw_values_seen = collections.Counter()
    by_corpus = collections.Counter()
    matched_raw = collections.Counter()
    extra_counters = {f: collections.Counter() for f in fields_extra}
    total_atoms = 0
    total_with_field = 0

    for corp, atom in iter_atoms(substrate_index_dir):
        total_atoms += 1
        v = getfield(atom, field)
        if v is None:
            continue
        total_with_field += 1
        raw_values_seen[str(v)] += 1
        if norm(v) == target_norm:
            by_corpus[corp] += 1
            matched_raw[str(v)] += 1
            for f in fields_extra:
                extra_counters[f][str(getfield(atom, f))] += 1

    return {
        "field": field,
        "target_value": target_value,
        "total_atoms_scanned": total_atoms,
        "total_atoms_with_field": total_with_field,
        "distinct_raw_values_for_field": len(raw_values_seen),
        "count": sum(by_corpus.values()),
        "by_corpus": dict(by_corpus.most_common()),
        "matched_raw_spellings": dict(matched_raw.most_common()),
        "extra_field_breakdowns": {f: dict(c.most_common()) for f, c in extra_counters.items()},
    }


def _selftest():
    # --- norm() self-test: 3 positive, 2 negative (over-merge guards) ---
    assert norm("CHAIN-GRADE") == "chain_grade"
    assert norm(" Chain_Grade ") == "chain_grade"
    assert norm("proven-bound") == "proven_bound"
    assert norm("chain_graded") != "chain_grade", "OVER-MERGE: must not fold in a longer word"
    assert norm("not_chain_grade") != "chain_grade", "OVER-MERGE: must not fold in a compound"
    print("norm() selftest: 5/5 PASS (3 positive, 2 negative over-merge guards)")

    # --- getfield() self-test: top-level, nested metadata, and the crash case ---
    assert getfield({"cert_status": "chain_grade"}, "cert_status") == "chain_grade"
    assert getfield({"metadata": {"cert_status": "chain-grade"}}, "cert_status") == "chain-grade"
    assert getfield({"metadata": "a bare string, not a dict"}, "cert_status") is None  # NEGATIVE
    assert getfield("not even a dict", "cert_status") is None  # NEGATIVE
    print("getfield() selftest: 4/4 PASS (2 positive, 2 negative crash-safety guards)")

    # --- variant_safe_count() against the REAL store: known positive is the documented finding
    # itself (69 atoms, hyphen variant present); known negative is a nonsense target that must
    # return 0, proving the function doesn't over-match everything. ---
    pos = variant_safe_count("cert_status", "chain_grade")
    assert pos["count"] == 69, (
        "REGRESSION or store changed: expected 69 variant-safe chain_grade atoms (the "
        "documented 2026-08-15 finding), got %d. If the store genuinely changed, update this "
        "assertion WITH a note of why; do not silently adjust it." % pos["count"])
    assert "chain-grade" in pos["matched_raw_spellings"], (
        "expected the hyphenated spelling to be present and merged: %r" % pos["matched_raw_spellings"])
    hyphen_n = pos["matched_raw_spellings"].get("chain-grade", 0)
    underscore_n = pos["matched_raw_spellings"].get("chain_grade", 0)
    assert hyphen_n == 10 and underscore_n == 59, (
        "expected 10 hyphenated + 59 underscored = 69; got hyphen=%d underscore=%d"
        % (hyphen_n, underscore_n))
    print("variant_safe_count() POSITIVE (real store, cert_status~chain_grade) PASS: "
          "count=%d (%d underscore-spelled + %d hyphen-spelled), matches the documented finding"
          % (pos["count"], underscore_n, hyphen_n))

    neg = variant_safe_count("cert_status", "this_value_does_not_exist_anywhere_xyz123")
    assert neg["count"] == 0, "NEGATIVE FAILED: nonsense target matched %d atoms" % neg["count"]
    assert neg["total_atoms_with_field"] > 0, "sanity: field itself must still be found on atoms"
    print("variant_safe_count() NEGATIVE (nonsense target, real store) PASS: count=0 as expected, "
          "field still recognised on %d atoms" % neg["total_atoms_with_field"])

    # --- axis-mismatch regression guard: provenance_quality~CERT_CHAIN_GRADE must NOT equal
    # cert_status~chain_grade (this was the entire point of the corrected finding: 642 vs 69). ---
    pq = variant_safe_count("provenance_quality", "CERT_CHAIN_GRADE")
    assert pq["count"] != pos["count"], (
        "the two axes collapsed to the same count (%d) -- if the store changed such that "
        "these are now equal, that is itself worth flagging, not silently accepting"
        % pq["count"])
    print("axis-mismatch regression guard PASS: provenance_quality~CERT_CHAIN_GRADE=%d != "
          "cert_status~chain_grade=%d (the corrected-axis finding still holds)"
          % (pq["count"], pos["count"]))

    print("\nvariant_safe_field_count selftest: ALL PASS (11 assertions: 5 norm, 4 getfield, "
          "2 variant_safe_count incl. positive+negative on the live store, 1 axis regression guard)")


def _cli():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--field", help="field name to count, e.g. cert_status")
    ap.add_argument("--value", help="target value to variant-match, e.g. chain_grade")
    ap.add_argument("--substrate-index", default=DEFAULT_SI)
    ap.add_argument("--extra-field", action="append", default=[],
                     help="co-report this field's distribution on the matching atoms (repeatable)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        _selftest()
        return

    if not args.field or not args.value:
        ap.error("--field and --value are required (or pass --self-test)")

    result = variant_safe_count(args.field, args.value, args.substrate_index, tuple(args.extra_field))
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print("field=%s  target=%s (variant-safe)" % (result["field"], result["target_value"]))
    print("distinct raw spellings of this field seen in the store: %d" % result["distinct_raw_values_for_field"])
    print("COUNT: %d" % result["count"])
    print("by corpus: %s" % result["by_corpus"])
    print("matched raw spellings: %s" % result["matched_raw_spellings"])
    for f, dist in result["extra_field_breakdowns"].items():
        print("co-occurring %s: %s" % (f, dist))


if __name__ == "__main__":
    _cli()
