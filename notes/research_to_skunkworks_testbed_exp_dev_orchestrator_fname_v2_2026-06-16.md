# Research (Director) -> All sessions: FILENAME CONVENTION v2 (USER directive; effective immediately)

**From:** Research (DIRECTOR)
**Date:** 2026-06-16 ~21:20
**Re:** USER directive after long-filename Write failure today. Convention v2 caps filename length to avoid Windows MAX_PATH issues. Full reasoning + tags now go in BODY, not filename.

## ROOT CAUSE

Windows MAX_PATH = 260 chars by default. Path prefix `d:\AI\hd-instrument\notes\` = 27 chars. Filename budget = 233 chars max, with safety margin target ~140 chars.

Today's DECISION 234 attempted filename was ~280 chars (5-discipline composition + 3-case description in filename) -> Write ENOENT. The convention of stuffing the full tag descriptor into filename has reached its breaking point.

## CONVENTION v2 (effective NOW; all sessions adopt)

```
FORMAT:
   <sender>_to_<recipient1>_<recipient2>[_<recipient3>]_<short_tag>_<yyyy-mm-dd>.md

CONSTRAINTS:
   - Total filename <= 100 chars (safety margin; hard limit 140)
   - <sender> = one of {research, skunkworks, testbed, exp_dev, orchestrator}
   - <recipients> = up to 3 sessions in filename (more in body's "To:" line)
   - <short_tag> = <= 35 chars; descriptive identifier suitable for grep
     Good: DECISION_234_kymn_ADD, P2_STEP_7_VET, tier_2_phase_2_spec
     Bad: DECISION_234_director_lean_STRONG_ADD_kymn_residue_resonator_ols_to_...
   - <yyyy-mm-dd> = 10 chars date stamp

BODY CONVENTION:
   - H1 line: full descriptive title (no length limit)
   - "From:" / "To:" / "Re:" lines (To: lists ALL recipients incl secondaries)
   - "Tag:" line at end with full descriptive tag (no length limit; for grep)

ROUTING PRESERVED:
   - Event bus filter still matches session-name substrings
     (skunkworks / testbed / exp_dev / research / orchestrator)
   - Widenet catchall picks up any new note (covers 4th+ recipient)
   - Short filenames continue to route correctly
```

## EXAMPLES (v2 compliant)

```
research_to_skunkworks_DECISION_235_STEP_8_ratify_2026-06-16.md       (62 chars)
testbed_to_research_P2_STEP_9_ATOM_FILED_2026-06-16.md                (54 chars)
exp_dev_to_orchestrator_P3_STEP_6_dispatch_2026-06-16.md              (55 chars)
skunkworks_to_research_testbed_tier_2_phase_2_spec_2026-06-16.md      (63 chars)
research_to_skunkworks_testbed_exp_dev_orchestrator_fname_v2_2026-06-16.md  (71 chars; this note)
```

## OLD CONVENTION (deprecated; NOT renaming existing files)

Pre-v2 long filenames stay in place (rename would break git history + event bus log replay). All NEW notes adopt v2.

## VALIDATION TOOL (recommended)

Sessions should sanity-check filename length before Write. Pseudo-check:
```
LEN=$(echo -n "<proposed_filename>" | wc -c)
if [ $LEN -gt 140 ]; then echo "REJECT: filename too long ($LEN chars)"; exit 1; fi
if [ $LEN -gt 100 ]; then echo "WARN: filename approaching limit ($LEN chars)"; fi
```

A formal `tools/check_filename_length.sh` can be added if needed. For now, sessions self-discipline at Write time.

## WHY THIS MATTERS

- USER asked "figure out an updated method that avoids the filename length issue and make sure other sessions adopt it"
- Recovery rule: if Write fails on filename length, the sender MUST shorten and retry; don't push detailed tag into filename
- The full tag/reasoning ALWAYS goes in body H1 + Tag: line, which has no length limit and is grep-able

## ADOPTION CONFIRMATION REQUESTED

Each session ACK adoption in next routine note (no new note needed; just include "fname_v2 adopted" in body somewhere). Going forward all new filenames target <=100 chars.

## Standing duties unchanged

All cert chain + routing + 13th-rule active state-check + 14th-rule explicit dispatch + 9th-rule end-with-waiting-on continue per usual.

-- Research (Director)

Tag: filename_convention_v2_USER_directive_2026-06-16_MAX_PATH_safety_margin_100_chars_target_140_hard_limit_sender_to_recipients_short_tag_date_full_descriptor_in_body_H1_and_Tag_line_old_files_stay_widenet_catchall_covers_4th_recipient_routing_substring_match_preserved_skunkworks_testbed_exp_dev_research_orchestrator
