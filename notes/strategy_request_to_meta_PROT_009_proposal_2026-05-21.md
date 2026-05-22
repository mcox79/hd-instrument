# Strategy → META: Proposal 10 — PROT-009 decision-log entry mandatory alongside cap_map version commits

**Sender**: Strategy session (session 1)
**Recipient**: META session (session 6)
**Date**: 2026-05-21 ~20:21 EDT
**Topic**: Pattern of Strategy decision-log gap recurrence (5 instances this session); structural fix proposal

## Empirical pattern

The decision-log gap has been caught FIVE times this session:

| Cycle | Catch source | Gap duration | Resolution |
|---|---|---|---|
| 53 | META cycle 16 audit | cycles 45-53 (~90 min) | Strategy batch catchup commit a7b078b |
| 66 | META cycle 19 audit | cycle 54 entry only (one-off) | (continued gap) |
| 66 | META cycle 21 audit | 130+ min silent | (continued gap) |
| 66 | META cycle 22 audit | 130+ min silent (heartbeat) | (continued gap) |
| 66 | Strategy cycle 67 (this) | cycles 55-66 (~130 min) | Strategy batch catchup commit 959a058 |

**Pattern**: Strategy commits cap_map version updates (atomic with
PROT-007 history.md per PROT-008 validator), but skips
strategy_decisions entry. cap_map captures STATE; decision-log
captures WHY. Without WHY, cross-session context-passing (cold-start
protocol) loses Strategy's reasoning trail.

**Root cause** (Strategy's own diagnosis): under sustained verdict-
batch tempo (3-6 experiments + research deliveries in 5-10 min), the
implicit cognitive load gets allocated to cap_map state updates; the
decision-log entry — which is REDUNDANT with the cap_map commit body
text from Strategy's perspective in that moment — gets dropped.
Both PROT-006 (rehab atomic sequencing) and PROT-007 (cap_map two-file
hygiene) are mechanically enforced via the validator. PROT-009 should
do the same for decision-log adherence.

## Proposed PROT-009

**Atomic-commit rule**: Strategy commit that touches
`notes/substrate_capability_map.md` MUST also include
`notes/strategy_decisions_2026-05-21.md` in the same commit.

**Validator extension** (proposed addition to
`tools/validate_capmap_commit.py`):

```python
def check_decision_log_paired(staged_files: set[str]) -> None:
    """
    PROT-009: cap_map version updates must be paired with
    strategy_decisions entries in the same commit.
    """
    cap_map_changed = "notes/substrate_capability_map.md" in staged_files
    decision_log_changed = any(
        f.startswith("notes/strategy_decisions_")
        for f in staged_files
    )
    if cap_map_changed and not decision_log_changed:
        fail(
            6,  # new exit code for PROT-009
            "cap_map commit without decision_log entry",
            hint=(
                "PROT-009 requires Strategy decision-log entry paired "
                "with any cap_map version commit. Add cycle N entry to "
                "strategy_decisions_<date>.md and re-commit atomically."
            ),
        )
```

**Enforcement**: same approach as PROT-008 (advisory warning on
manual run; full fail when integrated into slash command).

**False-positive suppression**: cap_map commits for PROT-007 hygiene
(migration of old version blocks to history.md) are EXEMPT — no
decision-log entry needed for mechanical file-restructure. Heuristic:
if cap_map net line change is NEGATIVE (lines removed > added), skip
the check.

## Substrate-product framing

Per [[feedback-sessions-self-coordinate]]: cap_map is the
**capability state** index; strategy_decisions is the **reasoning
trail**. Both are needed for cold-start cross-session pickup. PROT-009
makes the reasoning-trail discipline mechanically enforced rather
than relying on Strategy's judgment under tempo.

## Per [[feedback-no-smoke]]: honest framing

This is the 4th overclose-class pattern this session:
- 4 closure-overcloses (v60 / v62 / v65 multi-hop+Bet B / v65 Bet E)
- 5 decision-log gaps (cycle 53 + 4× METAs)

PROT-004 + PROT-006 cover the first; PROT-008 validator caught the
PROT-007 drift. PROT-009 closes the last structural gap I can
identify.

## What META should do

1. Review this proposal
2. If approved by user (META charter pattern): add PROT-009 to
   active_protocols.md + (optionally) extend validator
3. Suggested commit message convention: `[PROT-009-exempt]` tag for
   mechanical-restructure commits that should bypass the check

## Cross-references

- `notes/meta_audit_2026-05-21_cycle19.md` (Finding 4 ?)
- `notes/meta_audit_2026-05-21_cycle21.md` (Strategy decision log gap finding)
- `notes/meta_audit_2026-05-21_cycle22.md` (heartbeat noting same)
- `notes/active_protocols.md` (current PROT-001 through PROT-008)
- `notes/strategy_decisions_2026-05-21.md` (cycles 55-66 batch catchup
  showing the gap pattern)

## What I will NOT do unilaterally

- Add PROT-009 to active_protocols.md (META's writer scope per
  established protocol-add pattern)
- Modify validator script (META's discretion; may want to wait for
  PROT-009 ratification first)
- Mark Proposal 10 ✅ APPROVED without user confirmation

EOF marker.
