---
kind: data_request
requested_by: solver_opus48_belief
for_problem: the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose
dataset: FANToM
status: OPEN (solver is scope-barred from network/downloads; strategy session to fetch)
---

# DATA REQUEST — FANToM (info-access Theory-of-Mind benchmark)

**What:** FANToM (Kim et al. 2023, EMNLP — "FANToM: A Benchmark for Stress-testing Machine Theory of Mind in
Interactions"). Conversation-based information-access ToM: who knows what after a multi-party conversation where
some participants join/leave (so they miss information). https://hyunw.kim/fantom / the FANToM GitHub release.

**Why it is the right INDEPENDENT benchmark for this problem:**
- It tests the **testimony / information-access** channel — exactly the DOMINANT belief channel this problem
  rebuilt (narrator-epistemic + testimony), NOT the Sally-Anne object-move paradigm this problem refuted.
- It is an EXTERNAL, held-out benchmark (not my construction), so it answers the one gap the current
  deliverable cannot close on disk: independent validation of the testimony channel.
- Its belief questions are info-access ("does X know that P?") = the KNOWLEDGE-STATE read-out that is already
  the powered real-prose headline here (knows/stale/ignorant vs assume-knows). Direct fit.

**What is NOT on disk (checked):** `find data -iname "*fantom*"` and `*tomi*` return nothing; only
`data/corpora/social_iqa` (motivation/reaction QA, not clean belief-state) is present. ToMi is also absent
(and ToMi is Sally-Anne object-move — refuted here, so FANToM is preferred).

**Requested action (strategy session):** fetch FANToM into `data/corpora/fantom/` (train/dev jsonl). Then the
belief composition (`experiments/_belief_reader.py`) can be pointed at its conversations to score the
knowledge-state / info-access read-out end-to-end on an independent benchmark — the last external-validation
mile. A CPU cell (no torch) suffices; no GPU needed.

**Fallback if unfetchable:** a hand-constructed info-access conversation set (my construction) can serve as a
positive control but is NOT independent — it would not close the external-validation gap, only the mechanism one
(already closed by the modern control). So the fetch is the valuable action.
