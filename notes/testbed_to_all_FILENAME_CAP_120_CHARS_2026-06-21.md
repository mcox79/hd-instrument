# FILENAME CAP 120 CHARS (USER 2026-06-21)

USER flagged drift: recent filenames hitting 100-160+ chars (mine + others). Old notes from Jun 13-16 hit 230-250+.

**Now in CLAUDE.md (commit incoming):**

- Cap 120 chars total (incl `.md`)
- Format: `<from>_to_<recipient>_<TOPIC_SLUG>_<YYYY-MM-DD>.md`
- `<recipient>` = single role OR `cc_all` for broadcasts. Drop multi-role enumeration; put cc-list in body.
- `<TOPIC_SLUG>` = 5-10 snake_case words, headline-quality. Body holds detail.

**Examples:**
- BAD (156): `testbed_to_research_skunkworks_exp_dev_orchestrator_FLEET_WAITING_ON_SUBSTRUCTURE_v2_section_template_2026-06-21.md`
- GOOD (~60): `testbed_to_all_FLEET_WAITING_SUBSTRUCTURE_v2_2026-06-21.md`

**Why:** unreadable `ls`; hard copy-paste; encourages stuffing context into filenames instead of bodies; the monitor's filter still works either way but the human + dashboard parser don't.

**Action:** apply on next note. No retroactive renames (would break git history + monitor diff state).

— Testbed
