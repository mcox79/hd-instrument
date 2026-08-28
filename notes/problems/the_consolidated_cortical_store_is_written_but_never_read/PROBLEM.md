---
priority:
review: EXCELLENT
review_text: "INTEGRATED 2026-08-26 (owner-DONE, status PARTIAL). Re-verified scaffold-free first-hand: test_cortical_store_read_path.py WITNESS PASS (all 5 assertions incl. the 6-unit real-data headline -- memorises-not-transfers 6/6, cortical beats episodic in-domain 3/3, beats twin 3/3, unseen no-clear 6/6). A precise BOTH: the READ-PATH half is validated (the brain-faithful cortical read beats the WRONG episodic memory ~10x on transfer, CI-separated over its info-free twin, ablation bites -- the 0.0000 becomes a real drop); the FLOOR half is not met (ties counting in-domain, at/below twin on powered unseen-cooc) -- so the residual wall is the consolidated CONTENT/CODE, the brief's own outcome-B. The brain-foundational drill was deep and honest (deviation #4 sparse+inhibition LOAD-BEARING on the read: 0.025->0.156; NEW deviation: recurrent attractor completion HURTS ranking by re-promoting hubs; deviation #5 CLOSED BY TEST -- the interleaved-online CLS process is MORE data-hungry than batch and shares its data-bound ceiling, so process-fidelity is a false lever when the constraint is DATA). 3 AUDIT UPDATEs folded into BRAIN_FOUNDATIONAL_AUDIT.md (dev #3 refined, dev #4 load-bearing on the read, new attractor-hurts-ranking deviation). hdlab landing (the CLS matched pair -- graded sparse+inhibited space=overlap cortical read routed against episodic by the p2 recollection gate) is architecture-validation NOT a floor-beater; scoped as the next focused default-off landing with its own witness. Converges with the sign_quantiser refutation + the meaning re-frame: the wall is meaning SUPPLY/CONTENT (grounding + scale), not the read mechanism, the code format, or the sign()."
---

# PROBLEM: we answer every question out of the fast episodic memory and NEVER read the consolidated cortical store we bothered to write -- a missing cortical-read organ, not a representational ceiling

**slug:** `the_consolidated_cortical_store_is_written_but_never_read` - **opened:** 2026-08-26 by the strategy session
(packaged from `notes/BRAIN_FOUNDATIONAL_AUDIT.md` deviation #3 / system-defect #1 -- the retrieval-ORDER inversion)
**status:** OPEN - **first-hand in the audit; the complement to the just-integrated DG/CA3 episodic win**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2`. The audit named this a SYSTEM-LEVEL defect
> that no per-organ row could catch: every organ in the retrieval path is individually fine, yet the path is wrong
> because we read from the wrong memory. It is now especially timely -- `no_automatic_reliability_signal` just made
> the EPISODIC (hippocampal) recollection self-certifying; this is the CORTICAL complement that makes consolidated
> knowledge transfer. Re-rank if you judge the cross-cutting `sign->graded` fix (p1) or the meaning wiring higher.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

The system reads, files what it learns into a long-term ("consolidated") store, and keeps it between runs -- all
of that works. But when we ask it a question, it answers out of the FAST, one-shot "sketchpad" memory (the
hippocampal/episodic codes) and **never actually reads the consolidated store back.** Proof: turn consolidation
OFF and the answers don't move at all (0.0000). So the store we work to build is write-only. This is why the
programme's oldest wall -- "the system MEMORISES what it read but does not TRANSFER to new questions" (near-perfect
at the exact key, near-zero held-out) -- keeps reproducing: that pattern is the signature of answering from the
sketchpad instead of from consolidated knowledge. The brain answers general/semantic questions from CORTEX (the
slowly consolidated store), not from the hippocampus. We are missing the organ that reads the cortical store.

## 2. WHY THIS ONE

- **It reframes the standing negative.** "Memorises but does not transfer" has been read as a representational
  ceiling. The audit says it is a POSITION error: consolidation sits downstream of retrieval here and upstream in
  the brain. If reading the cortical store fixes transfer, a long line of nulls was measuring the wrong path.
- **It is the complement to a proven win.** `no_automatic_reliability_signal` (integrated EXCELLENT) made the
  episodic recollection SELF-CERTIFY via DG/CA3. That is the fast system. This is the slow system's READ -- the
  two are a matched pair in the brain (complementary learning systems), and the meaning line needs the same
  consolidated tier.
- **It is a WIRING/organ gap with a clear positive control** (ablating consolidation must MOVE the answer once the
  read path exists), so it can fail honestly.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED (complementary learning systems -- McClelland, O'Reilly, Norman):** the hippocampus binds an episode in
one shot; the neocortex consolidates statistics slowly and is the store queried for GENERAL/semantic knowledge.
Retrieval of consolidated knowledge is a CORTICAL read (pattern completion over the slowly-learned distributed
code), not an episodic lookup. The two systems are complementary: fast/sparse/pattern-separated vs
slow/overlapping/statistical.
**OUR-INVENTION-UNDER-TEST:** the exact cortical-read operation (how a cue addresses and completes over the
consolidated distributed store) -- copy the COMPUTATION (a completion/read over the consolidated statistics that
answers held-out queries), SWEEP the parameters. The organs partly exist: `hdlab/cortical_recall.py`,
`hdlab/additive_map.py`, `hdlab/continual.py` (the faithful, ISLANDED consolidation engine), the fact store.

**Corpus-age note:** McGuffey is ~200 years old; score transfer against gold with the mismatch in mind.

## 4. MEASURED vs INFERRED

**MEASURED** (`BRAIN_FOUNDATIONAL_AUDIT.md` system-defect #1, re-verify): ablating consolidation left the read-out
IDENTICAL in 9 of 12 cells and ablating `definitions` moved it by exactly `0.0000` -- because `recall()` /
`recall_sentence()` address the episodic codes and never touch the fact store. The standing store result is
exact-key ~`0.93` / held-out ~`0.004` -- the signature of hippocampus-only retrieval.
**INFERRED (open, decisive either way):** whether a CORTICAL-consolidated read path -- querying the consolidated
store rather than the episodic codes -- lets a HELD-OUT query beat the counting floor CI-separated (i.e. TRANSFER),
with ablating consolidation now DEGRADING the answer (the positive control that the store is actually being read).

## 5. ALREADY TRIED (do not re-run)

- The episodic (DG/CA3) recollection self-certification -- DONE (`no_automatic_reliability_signal`, integrated).
  That is the FAST system; do NOT re-solve it. This problem is the SLOW/cortical read.
- Reading MORE into the same episodic path -- does not fix transfer (the path, not the volume, is the issue for
  transfer; volume raises episodic coverage, a separate lever).
- Query `experiment_index.py query "consolidation"`, `query "cortical"`, `query "transfer"`, `query "recall"`;
  read `hdlab/cortical_recall.py`, `hdlab/continual.py`, and the `recall()`/`recall_sentence()` sites first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Reproduce the ablation result: turn consolidation / `definitions` off and confirm the read-out does NOT move --
  establishing that the consolidated store is currently unread.
- Trace `recall()` / `recall_sentence()` and confirm they address the episodic codes, not the fact store.
- Confirm what `continual.py` (faithful consolidation) actually produces and whether `cortical_recall.py` reads it.

## 7. THE BAR

On HELD-OUT (transfer) queries -- questions whose answer was consolidated from reading but is NOT at an exact
episodic key -- with floors recomputed on that population: **a cortical-consolidated read must beat the strongest
floor (first-order counting) CI-separated over its UPPER bound, info-free twin LOSING**, AND **ablating
consolidation must now DEGRADE the answer CI-separated** (the positive control proving the cortical store is being
read, i.e. the current `0.0000` becomes a real drop). Report CI half-width + null p95.
**DECISIVE EITHER WAY:** if the cortical read clears the floor on held-out and the ablation bites -> wire the
cortical-read organ (propose the hdlab diff; strategy lands it). If reading the consolidated store still does NOT
beat episodic-only / the floor on held-out -> the consolidated store's CONTENT is the problem, not the read path
(the statistics we consolidate are not transfer-bearing) -- report that precisely; a rigorous negative is a PASS
and it redirects the memory line from "read path" to "what gets consolidated."

## 8. FILES AND ENTRY POINTS

- `hdlab/cortical_recall.py`, `hdlab/additive_map.py`, `hdlab/continual.py` (faithful consolidation, islanded),
  `hdlab/hd_fact_store.py`, and the `recall()` / `recall_sentence()` sites in `hdlab/reading_grounding_loop.py`.
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (deviation #3 / system-defect #1; memory tier D3/D4) -- report any
  correction as an AUDIT UPDATE.
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, board Q111).
  Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT quote the exact-key ~0.93 as a capability -- it is the memorisation number; the whole point is held-out
  TRANSFER.
- Do NOT read the current `0.0000` ablation as "consolidation is useless" -- it means consolidation is UNREAD; the
  test is whether reading it helps.
- Do NOT carry any number between the episodic (DG/CA3) instrument and this cortical-read instrument -- different
  path, different population, no number crosses.

---

> ## 📎 REINFORCING DATAPOINT (2026-08-28, routed from the dimensional phase-diagram audit — NOT a reopen)
> The `dimensional_phase_diagram_audit_of_the_current_organs` submission (integrated EXCELLENT, owner-DONE) measured the
> cortical/consolidated READ regime directly (`exp_addressed_store_partial_cue_v1`) and it is the audit's **biggest LIVE
> lever**: a RELATED (partial) cue retrieves the right family at **1.00 with a DISTRIBUTED semantic code but ~0.11 (≈chance)
> with the exact-key hash the substrate currently reads** → **+0.88 generalisation headroom**; the real-WordNet arm confirms
> (nn-sim 0.41 vs 0.05). This reproduces this problem's own "read-path validated, floor half not met" split from the READ-CODE
> side: the residual wall is the consolidated CONTENT/CODE **format** (exact-key hash vs distributed/overlapping code), exactly
> the outcome-B named here. The audit deliberately did NOT build the wiring (Q113 role-separation — it would compete with this
> filed work); it hands this problem a strong datapoint that the **read regime (distributed-cue vs exact-key)** is where the
> generalisation headroom lives. Also reinforces `cortical_read_never_tested_where_it_matters`. Fix direction (audit's): DG
> sparse pattern-separation + a distributed/semantic read key, NOT more dimensions (N ruled out as a lever everywhere).
