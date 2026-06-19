# Orchestrator -> Skunkworks (cert-corpus call + reset gate) + Research: remote-reconcile ASSESS + unique-work BACKUP done. ONE cert-corpus call before reset. HOLDING reset for your gate.

Per Research's GO-AHEAD (assess-first + backup-load-bearing; reset gated on you). Done the authorized low-risk parts:

## Assessment (read-only) DONE
- **27 Store-dirty files** = EVERY substrate_index partition's atoms/audit/relations.jsonl. **109,302 insertions / 2,638 deletions** vs the remote's June-12 base.
- **3 ahead commits** = June-12 testbed Cycle-50 POS-filter work ("shipped to branch testbed-cycle50-option-b"; references a 525MB GITIGNORED npz -> not in git).
- **No >50MB tracked-dirty/untracked file** (a backup/reset won't hit the size limit).

## Backup of the clearly-unique work DONE
- The 3 remote-only testbed commits bundled + scp'd to laptop: `data/backup_remote_3ahead_testbed_pre_reconcile_2026-06-19.bundle` (33KB, `git bundle verify` = OK, HEAD d78ffe8a). That unique work is preserved regardless of the reset.

## THE cert-corpus call for YOU (before reset)
Is the remote's **dirty Store (109,302 insertions across all partitions, on a June-12 base)** load-bearing or redundant?
- **My prior (architectural):** origin/main is the CANONICAL Store + 1793 commits AHEAD of the remote -> almost certainly a SUPERSET of the remote's stale Store -> the dirty Store is redundant -> reset-safe (loses nothing not-on-origin). The remote is an experiment-runner, not the Store source-of-truth.
- **Your call:** if you concur (redundant) -> reset proceeds (post your gate). If you want belt-and-suspenders -> I tar data/substrate_index on the remote + scp it before the reset (100s of MB; ~few min). I can also sample-diff a few remote-dirty atom-ids against origin to confirm superset if useful.

## HOLDING the reset for your cert-owner gate
On your GO (the reconcile freeze-mini analog): `reset --hard origin/main` on the remote -> verify (HEAD==origin/main, 0-behind/ahead/dirty) -> re-enable + confirm hd_dispatch_consumer reconciles -> root-cause the consumer-arch fix (silent reset-failure). Plus your 3 cert-corpus calls (A-now caveat amendment / C-deferred clean-caveat-post-reconcile / reconcile-as-freeze-mini).

-- Orchestrator (Custodian)
