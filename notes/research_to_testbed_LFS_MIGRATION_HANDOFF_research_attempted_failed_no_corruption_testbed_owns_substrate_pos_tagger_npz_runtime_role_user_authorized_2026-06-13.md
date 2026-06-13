# Research -> Testbed: LFS migration HANDOFF -- Research attempted + failed at 49% (no corruption; repo intact) -- Testbed owns production substrate_pos_tagger.npz runtime + better positioned -- USER explicit authorization preserved

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** LFS migration P0.3 attempt outcome + handoff to Testbed per USER question "should testbed be doing this?"

## ACK + handoff

USER directly asked "should testbed be doing this?" -- correct call. Research attempted LFS migration twice + hit `gitobj: no such object: ff3e8a49e8471c4eff53890b1faa2871a985b444` at 49% of the second attempt. Handing off cleanly.

USER explicit authorization PRESERVED + carries forward for Testbed action.

## Research attempts (record)

1. **Attempt 1**: `git lfs migrate import --include="data/substrate_index/substrate_pos_tagger.npz" --everything --yes`
   - First failed: "dubious ownership in repository" (D: drive ownership not recorded)
   - Fixed with: `git config --global --add safe.directory D:/AI/hd-instrument/.git`
   - Re-ran: "Rewriting commits: 100% (3773/3773), done. Updating refs: ..., done."
   - BUT: 550MB blob still in HEAD tree post-migration; LFS ls-files empty
   - Cause: `--include` pattern with full path didn't match; LFS migrate expects glob pattern relative to repo root

2. **Attempt 2**: `git lfs migrate import --include="*.npz" --everything --yes`
   - Started: "Rewriting commits: 49% (3633/7409)"
   - Failed: "gitobj: no such object: ff3e8a49e8471c4eff53890b1faa2871a985b444"
   - Repo state: HEAD intact (fsck clean); refs not updated; no destructive change

## Current repo state (verified)

- `git fsck --no-dangling` clean (NO corruption)
- HEAD at `2f545ec8` (Testbed CELL KP 5-path feasibility map; latest commit)
- All recent Testbed + Research commits intact
- LFS-tracked files: NONE
- 550MB blob still at `data/substrate_index/substrate_pos_tagger.npz` in HEAD tree

## Why Testbed should own this

1. **Production runtime context**: Testbed knows substrate_pos_tagger.npz current runtime role (production POS tagger artifact); knows whether it needs to remain a real file or can be gitignored + re-generated
2. **Repo infrastructure access**: Testbed has remote desktop runners + production git environment; better positioned to handle 7K+ commit rewrite + force-push reliably
3. **Long-standing P0.3 ownership**: Testbed has flagged LFS P0.3 in 5+ coordination notes; this is their P0
4. **Per Research memory** `feedback-research-external-corpus-inventory-requires-grep-git-log-notes-before-asserting-not-built` -- Research session repeatedly under-claims production state; this is consistent pattern

## Recommended Testbed LFS migration approach

Three options (Testbed picks based on runtime needs):

**Option A**: Full LFS migration (preserves file content via LFS pointer)
```bash
git lfs install
git lfs track "*.npz"
git add .gitattributes && git commit -m "lfs: track *.npz"
git lfs migrate import --include="*.npz" --everything --yes
git push --force origin main
git push --force origin testbed-cycle50-option-b
```

**Option B**: Remove file from history entirely (if file is regenerable / no longer needed)
```bash
git filter-repo --invert-paths --path "data/substrate_index/substrate_pos_tagger.npz"
# requires git-filter-repo install
git push --force origin main
```

**Option C**: BFG Repo-Cleaner (lighter alternative to filter-repo)
```bash
bfg --strip-blobs-bigger-than 100M
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force origin main
```

USER authorization is on file: "if that is your recommendation, and testbed/expdev support, then yes". Testbed can act on this without further user signoff.

## Coordinated cleanup

Post Testbed migration:
- All sessions re-fetch + reset --hard origin/<branch>
- Open PR `testbed-cycle50-option-b` may need close+reopen
- LFS ~/.gitattributes propagation across sessions

## Substrate-product positioning artifact still tracking

Cycle 51 close + post Exp-Dev capstones:
- HP_v1+ 0.75 HARD-PASS
- CHTV-1 verifier 1.0 precision
- L6-PROOF PHASE 2 prove + EMPIRICALLY VALIDATED depth-2
- L6-PROOF FINDER 20/20 SOUND + 20/20 axiom-terminating
- **CH-P6 SOUNDNESS-GAP CAPSTONE HARD-PASS** (substrate 0 false-accepts vs Qwen-0.5B 3/12 + 1.5B 1/12) -- PROVER NARRATIVE COMPLETE
- **CELL KP path P1 frequency-promotion HARD-PASS** (24 T3->T2 candidates)
- 144 T1 atoms + BATCH 15 depth-2 + BATCH 16 supplementary
- 4.37M facts ready + extract-from-facts mapper skeleton + 5 ingest cell skeletons
- 8d mathematical-foundation pillar STANDS post-F4 re-spec
- Knowledge promotion operator 5 substrate-only paths IDENTIFIED + P1 first path SHIPPED
- USER goal "substrate understands own mathematics" CLOSED at deduction level

24+ substrate-product positioning artifacts. Path-to-USER-vision substrate-on-all-knowledge concrete + executing.

## Routing

- **Testbed**: LFS migration P0.3 OWNERSHIP (USER authorized); pick Option A/B/C; CELL KP P1 already SHIPPED + 24 T3->T2 candidate list ready for promotion; coordinate post-migration
- **Exp-Dev**: CH-P6 capstone done + CELL KP P1 done; standing for direction on path P2 DRUM rule mining (~2 day build) vs path P4 sleep-replay approximation
- **Research**: filing this handoff; standing for LFS migration + KP path P2/P4 ship verdicts + BATCH 17 deeper DEPENDS_ON authoring on demand to address 62% authoring-gap-leaf depth caveat

## Cross-references

- notes/research_to_testbed_exp_dev_LFS_MIGRATION_P0_3_EXECUTING_NOW_*.md (intent announcement)
- notes/exp_dev_to_research_CH_P6_SOUNDNESS_GAP_HARD_PASS_LLM_hallucinates_substrate_sound_capstone_*.md (capstone source)
- commit 6a925bc8 (CH-P6 SOUNDNESS-GAP CAPSTONE HARD-PASS)
- commit 93fbb3ac (CELL KP P1 HARD-PASS 24 T3->T2 candidates)
- commit 2f545ec8 (CELL KP 5-path feasibility map)

---

**Testbed:** LFS MIGRATION HANDOFF Research attempted + failed at 49pct + no corruption fsck clean + Testbed owns substrate_pos_tagger.npz runtime role + better positioned production runner + USER authorization PRESERVED if testbed/expdev support yes + 3 options Option A LFS migrate Option B filter-repo delete Option C BFG + post-migration cleanup all sessions re-fetch + reset hard + open PR close+reopen + meanwhile CH-P6 SOUNDNESS-GAP CAPSTONE HARD-PASS substrate 0 false-accepts vs Qwen-0.5B 3/12 LLM categorical gap empirically demonstrated + CELL KP P1 HARD-PASS 24 T3->T2 candidates first knowledge-promotion path SHIPPED + USER full-auto overnight continuing.
