---
review: EXCELLENT
review_text: Reverified first-hand 10/10. Bar met THROUGH the live reader (mention source swapped, else identical): the who-did-what candidate source reads the coref column (gold patient present only 0.82), and opening a discourse referent for EVERY NP (Kamp/Heim DRT) + demoting coref to a linking pass lifts effective end-to-end 0.4698->0.8054 (+0.336 CI-sep, cleaned-DO) with the info-free twin LOSING AND HURTING, no-regression on the noun-supplied eval, REPLACE>ADD, +0.115 who-has-what theme coverage. Register-invariant introduction (register lives in the linker). rnp = 95% of the competent reader; ideal composition (+frame detector +construction selector) >= competent. Real finding: multi-DO fit is CONSTRUCTIONAL not lexical (+0.040/+0.146 CI-sep; distributional re-rank +0.007 n.s.), reconciling the fit-dominant literature with the parent's fenced grounded-fit negative. WIRE OWED (§6, focused landing): default-off referent_per_np mention-source flag + the frame detector. Successor FILED: construction-aware selector (P4). §2b folded. INTEGRATED 2026-09-03.
---

# PROBLEM: the live reader sources role candidates from the COREF column, so on real documents the patient/agent is a candidate only ~0.82 of the time — open a DISCOURSE REFERENT for EVERY noun phrase (Kamp/Heim), demote coreference to a downstream linking pass, and prove it lifts real-document who-did-what + who-has-what CI-separated with an info-free twin losing.

**slug:** `open_a_discourse_referent_for_every_np_not_just_coref_mentions` — **opened:** 2026-09-03 by the strategy session, lifted from the owner-worked `the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses` (its §0b ranked this the #1 un-worked lever — "the recommended next problem", biggest by leverage, a DEPLOYMENT loss invisible to the noun-supplied eval). **status:** OPEN. Strategy lands any hdlab wire (Q111, default-off, witnessed). Glass-box, NO external LLM at inference (the invariant).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** The mission is the most brain-faithful substrate.
> **🧠 OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN do THIS?** Name the structure + computation, replicate that OPERATION as exactly as you can — the FIRST move, not a tiebreaker. Mark each choice PINNED vs OUR-INVENTION.
> **🚀 EXPLORE FAR + WIDE for the mechanism** — read the neuroscience/linguistics; if a MORE brain-foundational method conflicts with this brief, submit THAT (say why it is more faithful).
> **🧱 A SHARED WALL = GO DEEPER, not stop.** A rigorous located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`**; inherit its PINNED/INVENTED verdicts; add an AUDIT UPDATE for any deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When we test the reader on who-did-what, the test hands it every noun in the sentence as a possible answer. But when the reader reads a real document, it builds its own list of possible answers from the coreference column — and that list only contains entities the coref system already grouped (mostly named people). So on real 19th-century documents the correct patient is even ON the reader's candidate list only ~82% of the time; the other ~18% are lost before role assignment even runs — an invisible ceiling that the standard eval cannot see because it supplies the nouns. The brain does not wait for coreference: it opens a mental "file card" (a discourse referent) for EVERY noun phrase the moment it is mentioned, and only later works out which cards refer to the same thing. The job: make the live reader open a referent for every NP head, feed those as the candidate set, and demote coreference to a downstream linking pass over the referents — then show real-document who-did-what (and who-has-what) improve, with a scrambled control failing.

## 2. WHY THIS ONE — the lever is measured and the fix is prototyped
From the parent's §0b (first-hand, on 25 real LitBank docs): the live `read()` sources candidates from the coref column, so the gold patient is a candidate only **0.8183** of the time (entity-type coref only). A prototype `referent_per_np_mentions` (one mention per content-noun head; coref demoted to a linking pass) lifts patient candidate-coverage to **0.9705 (+0.1521)** across 1354 clauses — a lever that DWARFS the in-eval losses and is invisible to the noun-supplied benchmark. This is the reader's single biggest real-document deployment gap.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: Discourse Representation Theory / File Change Semantics (Kamp 1981; Heim 1982) — comprehension INTRODUCES a discourse referent for every NP (definite or indefinite, pronoun or full), building an incrementally-updated discourse model; coreference is a SEPARATE, later resolution over the introduced referents, not the source of them. OUR-INVENTION-under-test: the exact head-selection + the referent→coref linking interface (sweep). Mark PINNED vs OUR-INVENTION in the submission.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive — from the parent §0b):** live coref-column candidate sourcing → gold patient present 0.8183; `referent_per_np_mentions` prototype → 0.9705 (+0.1521) over 1354 clauses. (Source: `experiments/exp_whodidwhat_referent_per_np_prototype_v1.py`.)
- **INFERRED (you must measure):** wiring referent-per-NP as the live candidate source raises the reader's EFFECTIVE end-to-end who-did-what (abstention = wrong) on REAL documents CI-separated over the current live floor, WITHOUT regressing the noun-supplied-eval accuracy the parent landed (0.981 canonical), with a scrambled-referent info-free twin LOSING; and whether it also lifts who-has-what (the state register's holders come from the same source). The residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- **FIRST STEPS:** (1) understand ALL organs — `python tools/substrate_map.py`, `python tools/reader_capabilities.py`, skim `hdlab/`; (2) read IN FULL the parent `notes/problems/the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses/SOLVED.md` (§0b/§0c are the map — §0c(1) is the ideal referent-per-NP-first pipeline, prototyped); (3) `python tools/before_you_start.py "referent per NP discourse referent candidate sourcing"`.
- Reproduce on your own recompute: the 0.8183 coref-column vs 0.9705 referent-per-NP candidate coverage (the can-fail gap).
- Inspect what you will REUSE: `experiments/exp_whodidwhat_referent_per_np_prototype_v1.py` (the working prototype), `hdlab/situation_reader.py` (the live candidate-sourcing path + `_read_events`), the coref stream (`hdlab/coref`, `event_centrality_coref` — to demote to a linking pass), the NP-head organ (`hdlab/np_head_reduce`, already default-on). Measure on the board's who-did-what LitBank + who-has-what he/she arms (`tools/baseline_board.py`) — the REAL-document instruments, not the noun-supplied population.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = a referent-per-NP candidate source (a discourse referent per content-noun-head NP; coref demoted to a downstream linking pass; glass-box, NO LLM) that raises the LIVE reader's effective end-to-end who-did-what on REAL documents CI-separated over the current live floor, with NO regression on the noun-supplied-eval accuracy (explicit no-regression check) and a scrambled-referent twin LOSING CI-separated; report the who-has-what effect too. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — referent-per-NP does not net-help live, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed).

## ALREADY TRIED / DO NOT REDO
- Entity-type coref candidate sourcing = the current (weak) source; that is the floor, not the fix.
- The coref/entity-tracking/who-has-what axis is EXHAUSTED and owner-DONE (content-addressable retrieval, discourse-focus-stack, pronoun-chaining, Kehler-Rohde next-mention prior). This problem is UPSTREAM of coref (the mention SOURCE), not another coref algorithm — do NOT re-open coref resolution.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE the prototype cell + `hdlab/situation_reader.py` + the coref stream + `np_head_reduce`. Strategy lands any hdlab wire (Q111, default-off, witnessed). Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the noun-supplied-eval number as the deployment number — the gap is exactly that the eval supplies nouns the live reader must source itself.
- Do NOT use an external LLM to open referents or link them (the invariant).
