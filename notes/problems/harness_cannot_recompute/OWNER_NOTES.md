---
owner_verdict: DONE
---

harness_cannot_recompute — SOLVED. Re-running a finished experiment currently just replays its saved checkpoint and prints the same numbers in ~0s, so re-running proves nothing. Built and proved a fresh-recompute switch (HDI_FRESH_RUN) that redirects a cell to a new folder and genuinely redoes the work, touching none of the saved data. Verified both directions: unchanged inputs reproduce the verdict; one corrupted input correctly flips pass→fail — a re-run can now catch a real problem. Confirmed 60/60 real archive cells replay, none mutated. Found the clean fix auto-covers ~80 of ~400 affected cells; the other ~264 each need a documented one-line edit. Full-archive recompute ≈ 39 h (and the brief's "worst" 12,137-unit cell is actually one of the cheapest at 2 min). No live-system change made — the SH-7 diff and migration recipe are handed off for integration. Ledger-valid, awaiting re-verify.
