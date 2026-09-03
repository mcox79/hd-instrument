---
priority: 2
review:
review_text:
---

# PROBLEM: the NP-head fix repaired the who-did-what ACCURACY error (+0.20 per consumer, at the parse ceiling), but the live reader still silently ABSTAINS on ~22% of answerable clauses — its event/predicate gate + parse-dependent mention builder drop a fifth of clauses that DO have a recoverable patient (effective end-to-end 0.629 vs the full-coverage stack 0.981, i.e. abstention counted as wrong is the larger remaining loss); diagnose exactly which clauses are dropped and why, and recover them (attempt every finite verb; Davidsonian coverage) CI-separated end-to-end with NO precision regression — or a located negative naming the coverage blocker.

**slug:** `the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses` — **opened:** 2026-09-03 by the strategy session, lifted from the owner-DONE `the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning` (which SOLVED the accuracy half via NP-head reduction and MEASURED that coverage — not accuracy — is now the larger end-to-end loss: live reader effective 0.629 at 78% coverage vs the parser-free full stack 0.981 at 100%). **status:** OPEN — a COVERAGE/recall problem on the extraction front end, NOT the accuracy pick (that is fixed). Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> **PRIORITY NOTE:** filed at `2` — the LARGER remaining who-did-what loss end-to-end (a fifth of answerable clauses silently dropped), directly downstream of the just-landed NP-head accuracy fix; compounds across every role-output organ. Below the meaning north-star at 1.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + the computation, replicate that OPERATION as exactly as you can. It is the FIRST thing you do, not a tiebreaker.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience, cross domains; if a MORE brain-foundational method conflicts with this brief, submit THAT instead (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A wall is a fidelity gap to BUILD ACROSS, never a ceiling.
> **⛔ "CONVERGED" HAS A HIGH BAR** — claim it only with (a) the brain's mechanism identified AND (b) replicated + tested, or a SPECIFIC reason it cannot be.
> **🔁 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`):** each fire — gather a high-value control/curve/ablation/2nd-gold; enumerate what's LEFT + do it; MAP adjacent bottlenecks + EVALUATE each for brain-fidelity + optimization; a wall → a FINER research drill, never stop. Implement → test (can-fail, strongest real floor, twin LOSING) → iterate.
> **A rigorous negative is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.**
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
"Who did what" was just made much more accurate — when the reader gives an answer, it is now right ~98% of the time on clean old-prose clauses. But it still stays SILENT on about one in five clauses that actually have an answer: the machinery that decides "is there an event here, and where are its nouns" throws the clause out (usually because the old-prose grammar tool it leans on stumbled), so the reader never even tries. Counting those silent skips as wrong, the reader is effectively right only ~63% of the time end-to-end — so the silent skipping is now the bigger loss, not the picking. The brain treats every finite verb as an event to be understood; it does not skip a clause because its parse was messy. The job is to find exactly which clauses get dropped and why, and recover them — try every finite verb, build candidates robustly — without hurting the accuracy the fix just bought.

## 2. WHY THIS ONE — the larger remaining who-did-what loss, directly downstream of the accuracy fix
The parent measured it precisely: the accuracy fix (NP-head reduction) takes the pick to 0.981 at 100% coverage, but the LIVE reader only reaches 0.629 effective because it abstains on 22% of answerable clauses (its event/pred gate + parse-dependent mention builder). Recovering coverage is worth more end-to-end than any further accuracy gain, and it compounds through the ~20 role-output organs (which lose the dropped clauses entirely). The accuracy pick is done; coverage is the open lever.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: comprehension is DAVIDSONIAN — every finite verb projects an event to be interpreted (Davidson 1967); the parser is EXPERIENCE-BASED + robust, recovering structure even from noisy/degraded input (Now-or-Never bounded processing, Christiansen & Chater 2016; good-enough / noisy-channel comprehension, Ferreira 2002 / Gibson 2013 — the reader does not silently drop a clause because a single cue was ambiguous). So the faithful move is to ATTEMPT every finite verb and build candidates parser-robustly, abstaining only when there is genuinely no candidate — not gating on a brittle parse. Mark PINNED vs OUR-INVENTION: Davidsonian per-verb coverage + robust candidate recovery = PINNED; the specific event-detection gate / candidate builder = OUR-INVENTION-under-test.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent):** the full parser-free NP-head stack reaches 100% coverage at 0.981; the LIVE reader (`wired_pick`) abstains on 22% and scores 0.807 on its picks; effective end-to-end (abstention=wrong) live reader 0.629 vs full stack 0.981 (+0.3513 CI-sep); the abstention is the reader's event/pred gate + the parse-dependent mention builder (not the accuracy pick, now fixed). (Sources: `exp_whodidwhat_full_fix_v1`, `exp_whodidwhat_downstream_live_reader_v1`, the parent SOLVED.md §4.)
- **INFERRED (you must measure):** exactly which answerable clauses the live reader drops and WHY (event-gate false-negatives vs mention-builder drops vs genuine no-candidate); whether attempting every finite verb + a parser-robust candidate builder recovers coverage CI-separated on the effective end-to-end metric WITHOUT regressing the picked-clause precision (the NP-head accuracy must be preserved); whether the recovered clauses have recoverable patients or are genuinely ambiguous; the residual coverage floor + its named cause.

## ALREADY TRIED / DO NOT REDO (check `experiment_index` first)
- **The NP-head ACCURACY fix** — DONE + landed (the parent). This problem is COVERAGE, a different axis; do NOT re-litigate the pick.
- **Leaning on a modern parser for coverage** — refuted by the parent (spaCy is DEGRADED on 19c, 0.9297 < ours; a full parse does NOT beat the parser-free candidate builder). Robust parser-FREE recovery is the lever, not a better parser.
- **Register-native parse/POS data acquisition** — refuted upstream (`register_native_parse...`); not the lever.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** (1) understand ALL organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the parent `notes/problems/the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning/{SOLVED.md, BRAIN_FIDELITY_AND_SIGNAL_LOSS.md}` (the coverage decomposition + `exp_whodidwhat_full_fix_v1`'s Davidsonian coverage stage); (3) `python tools/before_you_start.py "who did what coverage abstention front end"`.
- Reproduce on your own recompute: the live reader's 22% abstention + 0.629 effective vs the full stack's 100%/0.981 (the can-fail gap).
- Inspect what you will REUSE: `hdlab/situation_reader.py` (the event/pred gate + `_read_events` mention builder), `hdlab/np_head_reduce.py` (the landed accuracy fix — coverage must PRESERVE it), `experiments/exp_whodidwhat_full_fix_v1.py` (the 100%-coverage reference), the cleaned 19c gold.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a coverage recovery (attempt every finite verb + parser-robust candidate building, glass-box, NO LLM) that raises the LIVE reader's EFFECTIVE end-to-end who-did-what (abstention counted as wrong) CI-separated over the current 0.629, WITHOUT regressing the picked-clause NP-head precision (an explicit no-regression check on the accuracy the parent landed), with an info-free twin (recover random clauses) LOSING. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the dropped clauses are genuinely un-recoverable glass-box, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed).

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE: `hdlab/situation_reader.py` (the event gate + mention builder), `hdlab/np_head_reduce.py` (preserve the accuracy fix), `experiments/exp_whodidwhat_full_fix_v1.py` (the Davidsonian 100%-coverage reference stack), `experiments/exp_whodidwhat_downstream_live_reader_v1.py` (the live-reader coverage measurement), the cleaned 19c gold. Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the picked-clause accuracy (0.98) as the end-to-end number — the effective (abstention=wrong) number is 0.629; coverage is the loss.
- Do NOT re-open the NP-head accuracy pick — it is fixed + landed.
- Do NOT propose a modern parser for coverage — refuted (spaCy degraded on 19c).
- Do NOT use an external LLM to recover clauses (the invariant); robust glass-box coverage is the deliverable.
