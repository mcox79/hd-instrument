"""A5-gated LOCAL-ONLY in-place amend of seq 29522: down-tier CHAIN_GRADE -> MEASURED_MECHANISM.
Director tier-adjudication accepted (symmetric anti-negativity, honest DOWN-tier of my own over-credit):
CHAIN_GRADE overstated a SUPPLY-preprocessing validation measured on a proxy noise-count (no event gold,
downstream who-did-what accuracy unproven). It is a validated MECHANISM (predicate-half of the events
bottleneck IS upstream-POS, fixed confound-free by supplied grammar; validates 29520's localization via
intervention), NOT a substrate-reasoning capability-at-ceiling (cf 29504 = genuine reasoning CG). Tier ->
MEASURED_MECHANISM / proven-bound. cert_delta stays +1 (positive validation, matches 29520/29521 MM +1).
Verification + honest scope UNCHANGED. In-place rewrite of the last line of atoms + ledger (never synced).
"""
import json, os, tempfile, time, datetime

ATOMS = "data/substrate_index/math/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"

with open(ATOMS, encoding="utf-8") as f:
    atom_lines = [l for l in f.read().splitlines() if l.strip()]
with open(LEDGER, encoding="utf-8") as f:
    ledger_lines = [l for l in f.read().splitlines() if l.strip()]

atom = json.loads(atom_lines[-1])
led = json.loads(ledger_lines[-1])
assert atom["seq"] == 29522 and atom["tier"] == "CHAIN_GRADE", f"unexpected last atom: {atom.get('seq')}/{atom.get('tier')}"
assert led["seq"] == 29522 and led["tier"] == "CHAIN_GRADE", f"unexpected last ledger: {led.get('seq')}/{led.get('tier')}"
OLD_AID = atom["atom_id"]
assert led["atom_id"] == OLD_AID
assert "_CHAIN_GRADE_SUPPLY_GRAMMAR_" in OLD_AID
print("PRE-AMEND OK: last atom + ledger both seq 29522 tier CHAIN_GRADE; atom_id matched.")

NEW_AID = OLD_AID.replace("_CHAIN_GRADE_SUPPLY_GRAMMAR_", "_MEASURED_MECHANISM_SUPPLY_GRAMMAR_", 1)
NEW_GRADE = "MM_SUPPLY_GRAMMAR_VALIDATION_PREDICATE_HALF_POS"

TIER_AMENDMENT = ("TIER DOWN-CORRECTED CHAIN_GRADE -> MEASURED_MECHANISM (proven-bound) at Director "
    "tier-adjudication; auditor DEFERS (symmetric anti-negativity: honest downward correction of my own "
    "over-credit gets the same rigor as an upward one). The WIN and all 7/7 bit-for-bit verifications are "
    "UNCHANGED and undisputed. Reason CHAIN_GRADE was wrong: (1) this is a SUPPLY/preprocessing-tool swap "
    "(NLTK->spaCy off-the-shelf tagger held as fixed input), not a substrate READING/REASONING capability at a "
    "proven ceiling -- the arc's only genuine chain-grade (29504) was selective-reanalysis REASONING on real "
    "text (naive=0/24); a better supplied tagger is a supply-lever VALIDATION. (2) The metric is a proxy "
    "NOISE-COUNT (obviously-wrong / nonverb_pred) with NO LitBank event gold, so a downstream who-did-what "
    "ACCURACY improvement is UNPROVEN -- a capability chain-grade of a reader should demonstrate accuracy at "
    "ceiling, not proxy-noise reduction. (3) My rubric does NOT count any reproduced can-fail proxy win as "
    "chain-grade regardless of proxy-vs-gold and preprocessing-vs-reasoning, so the 'all skeptic checks pass' "
    "bar for a capability claim is not met. The durable finding is a VALIDATED MECHANISM: the predicate half of "
    "the events bottleneck IS upstream POS, fixed confound-free by supplied grammar (intervention validating "
    "29520's localization); agent-typing is the un-fixed separate residual. This tier is consistent with the "
    "sibling MM atoms 29520/29521 and preserves the deliberately-strict chain-grade guardrail (~88 MM, 1 CG).")

# ---- atom mutations (preserve every other field, incl all verification) ----
atom["atom_id"] = NEW_AID
atom["tier"] = "MEASURED_MECHANISM"
atom["cert_status"] = "proven-bound"
atom["grade"] = NEW_GRADE
atom["cert_class"] = atom["cert_class"].replace("CHAIN_GRADE_supply", "MEASURED_MECHANISM_supply", 1)
atom["headline"] = atom["headline"].replace("SUPPLY-GRAMMAR VALIDATED (CHAIN_GRADE, CERT +1):",
                                            "SUPPLY-GRAMMAR VALIDATED (MEASURED_MECHANISM, CERT +1):", 1)
atom["key_metrics"]["tier"] = "MEASURED_MECHANISM_cell_verdict_HARD_PASS"
atom["tier_amendment"] = TIER_AMENDMENT
atom["framing_correction"] = ("Director framing UPHELD; tier DOWN-CORRECTED to MEASURED_MECHANISM (see "
    "tier_amendment). The discriminator is genuinely can-fail and fired well above floor (L1 confound-free rel "
    "+0.5611, L2 +0.5625 vs 0.25; CLEAN_NEGATIVE at rel<=0 reachable) and reproduced bit-for-bit -- a clean, "
    "real SUPPLY-VALIDATION. TWO STANDING SHARPENINGS: (1) the load-bearing number is L1 (pure POS, NO parser); "
    "L2 carries a mild train/test tag-shift because parser W + clf were fit on NLTK-tagged McGuffey -- cite L1 "
    "primary, L2 as corroboration, never L2 alone. (2) This validates 29520's LOCALIZATION and demonstrates the "
    "supply-lever works on the PREDICATE half only (agent-typing 196->195 untouched = the separate residual / "
    "next lever); because the metric is a proxy noise-count with no event gold, it does NOT by itself prove "
    "downstream who-did-what accuracy rose -- which is precisely why this is MEASURED_MECHANISM (validated "
    "mechanism), not a capability chain-grade.")
atom["ts_amended"] = time.time()
atom["ts_iso_amended"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.loads(json.dumps(atom))

# ---- ledger mutations ----
led["atom_id"] = NEW_AID
led["tier"] = "MEASURED_MECHANISM"
led["cert_status"] = "proven-bound"
led["grade"] = NEW_GRADE
led["cert_class"] = atom["cert_class"]
led["headline"] = atom["headline"]
led["key_metrics"] = atom["key_metrics"]
led["framing_correction"] = atom["framing_correction"]
led["tier_amendment"] = TIER_AMENDMENT
led["op"] = "landed_vet_atomize_tier_amended_in_place"
led["decision"] = led["decision"].replace("BANK as CHAIN_GRADE (chain-grade / CERT +1).",
    "BANK as MEASURED_MECHANISM (proven-bound / CERT +1); DOWN-CORRECTED from CHAIN_GRADE at Director "
    "tier-adjudication (see tier_amendment -- supply/preprocessing swap on a proxy noise-count, not a "
    "reasoning-capability-at-ceiling).", 1)
led["ts_amended"] = atom["ts_amended"]
led["ts_iso_amended"] = atom["ts_iso_amended"]
json.loads(json.dumps(led))

# ---- BINARY-SAFE in-place rewrite of the last line, both files ----
def rewrite_last(path, lines, new_obj, seq_expect):
    new_line = json.dumps(new_obj, ensure_ascii=False)
    assert "\r" not in new_line and "\n" not in new_line
    text = "\n".join(lines[:-1] + [new_line]) + "\n"
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    with open(path, "rb") as f:
        assert b"\r\n" not in f.read(), f"CRLF doubling in {path}"
    with open(path, encoding="utf-8") as f:
        v = [json.loads(l) for l in f.read().splitlines() if l.strip()]
    assert v[-1]["seq"] == seq_expect and v[-1]["tier"] == "MEASURED_MECHANISM"
    assert v[-1]["atom_id"] == NEW_AID and v[-1].get("cert_status") == "proven-bound"
    return len(v)

na = rewrite_last(ATOMS, atom_lines, atom, 29522)
nl = rewrite_last(LEDGER, ledger_lines, led, 29522)
assert na == len(atom_lines) and nl == len(ledger_lines), "line count changed -- in-place amend should not add/remove lines"
print(f"ATOMS OK: {na} atoms (unchanged count); seq 29522 -> MEASURED_MECHANISM/proven-bound; no CRLF.")
print(f"LEDGER OK: {nl} entries (unchanged count); seq 29522 -> MEASURED_MECHANISM/proven-bound; no CRLF.")
print("NEW_AID tail:", NEW_AID[-60:])
print("DONE. tier CHAIN_GRADE -> MEASURED_MECHANISM; cert_delta stays +1. LOCAL-ONLY; needs orchestrator sync.")
