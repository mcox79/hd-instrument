# RESEARCH (Director) -> USER (visibility): remote-reset DONE CLEAN + root cause of the 6-day silent failure FOUND and FIXED. Top-1 + M3 cron now unblocked. One real Research-side discipline catch (my own note-filename habit) adopted.

## What completed
1. **Pre-step 0:** runners IDLE; no in-flight write to clobber. Clean.
2. **Consumer disabled + fresh re-tar:** 533MB current dirty Store preserved on laptop as cert-safety-net.
3. **Reset:** `git reset --hard origin/main` -> HEAD == origin/main (1c211d29) | 0-behind | 0-ahead | dirty=12 (all benign untracked). Zero tracked divergence; zero Store-content divergence. Clean.
4. **Consumer re-enabled:** triggers stay at origin/main; reconciles cleanly now.

## Root cause of the 6-day silent failure: FOUND + FIXED
- **It was Windows MAX_PATH on my own 200+ char note filenames.** The consumer's `git reset --hard` failed partway (`Filename too long`) when it hit one of my long-name notes -> rolled back silently -> never reconciled. Started ~June 12 when the long-name notes accumulated.
- **Fix (Orchestrator):** `git config core.longpaths true` on the remote (Windows \\?\ long-path API).
- **Discipline catch on me:** my filename convention has been producing 200+ char names as a habit. Adopting a <=120-char cap going forward; routing METHODOLOGY_RULE + AUDIT_LESSON to Skunkworks for atomize.

## Cert-verify in flight (Skunkworks's lane)
Sample-diff a set of the discarded remote-dirty atom-ids vs origin/main. If all resolve -> superset confirmed; archive the tars. If any don't -> replay via atomize-VET from the tar (tar is the recovery path; preserved on laptop).

## What just unblocked
- **40h Top-1:** C-deferred A2 v6 on the clean grown 43,892 corpus (Orchestrator dispatching now; commit-hash 1c211d29 + substrate-id-hash to be recorded per Skunkworks's clean-caveat cert-condition).
- **M3 cron runner wiring:** Orchestrator wiring now.
- **40h Next-8 ConceptNet apply:** Director-side CSV acquisition next.

## Lesson worth noting
The verify-OUTPUT-not-liveness rule (the consumer's task "Running" != reconciling) caught this; the producer-attest + consumer-enforce pattern caught it again at this layer. The fix is mechanical (longpaths config) AND substrate-discipline (filename cap). Both adopted.

Will surface again on Top-1 verdict landing or any cert-verify off-pattern.

-- Research (Director)
