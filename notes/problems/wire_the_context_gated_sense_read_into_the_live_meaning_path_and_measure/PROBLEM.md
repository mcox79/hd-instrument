---
priority: 3
slug: wire_the_context_gated_sense_read_into_the_live_meaning_path_and_measure
status: OPEN
review:
review_text:
---

# PROBLEM: the in-context (token-level) meaning read is BUILT + board-measured (`sm.select_sense`, context-primed biased-competition over the curated hub, ~0.66-0.68 on the WiC arm) but DORMANT — it is a lazy query callable with NO live consumer; the live reader never invokes it (`sm.senses` stays `[]`), so the substrate's meaning read on real prose is NOT context-gated where the pri-1 refutation proved it must be. WIRE the context-gated sense read into the live meaning path and MEASURE whether it lifts a real board dimension on modern prose — measure-first, byte-identical when off, keep only if it clearly helps.

**opened:** 2026-09-11 by strategy (owner Q127: "you can evaluate integration and implement your recommendation"). **status:** OPEN. Glass-box, NO external LLM at inference.

> ## SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** THE OPENING MOVE: how does the BRAIN do THIS? Name the structure + computation and replicate that operation FIRST. **EVERY COMPONENT 100% BRAIN-FOUNDATIONAL** — spaCy/GLUCOSE/MAVEN + any off-the-shelf parser/dataset/model = NOT brain-foundational; a vetted static offline FOUNDATION asset is OK, an external tool/LLM AT INFERENCE is a DEFECT that BLOCKS. **ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS** (`BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md`). A rigorous located-negative is a PASS. **MEASURE-FIRST + BOARD-PROXY CAUTION (strategy 2026-09-11):** some board arms measure a SIMPLIFIED STAND-IN, not the full live `read()` — confirm your wire actually fires on the path the board scores (instrument it: count invocations), or you will "measure" a flat number that never ran. Reference `notes/BRAIN_FOUNDATIONAL_AUDIT.md`; add an AUDIT UPDATE for any stale verdict.

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN — how does the brain do THIS?** Meaning is read IN CONTEXT (N400/predictive, token-level biased-competition), NOT a context-free type lookup (pri-1 refutation: WiC type 0.485 → context 0.582 → landed cells 0.66-0.68). Replicate that operation on the live read.
> 2. **REUSE.** `sm.select_sense` (`hdlab.underspecified_sense_reader.select_sense` over `hdlab.meaning_foundation` + `diagnostic_context_wsd`) already exists + is board-measured. The job is to CALL it on the live comprehension path where a meaning/sense decision is made, not to rebuild it.
> 3. **MEASURE-FIRST + no-more-default-off.** Wire behind a flag, default OFF = byte-identical. Measure the LIVE board impact on a real dim; flip default-on ONLY if net-positive (the prior `the_meaning_win_offline_context_free_and_unwired` was PARTIAL — do NOT assume a gain).
> 4. **HIT A WALL → GO DEEPER.** If no live consumer benefits, that is itself the finding (name exactly why the in-context read has no live decision to inform — with a number).
> 5–8. Full-stack upstream (confirm no downstream regress), adjacent components, plain-language completion bar.
> **(FULL-STACK UPSTREAM.)** The in-context read consumes the passage context + the hub; confirm every scored dim is byte-identical or measured no-regress. ACCEPT that changing the live meaning read may ripple; fix downstream to receive it.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The system can already work out a word's meaning *from the sentence it's in* — and we've measured that it's decent at it (~two-thirds right on the standard in-context test). But nothing in the live reader ever *asks* it to. That ability sits switched off: it's available to call, but the reader reads meaning the context-free way and never invokes the in-context version. Since we just proved (with a theorem) that the context-free way has hit its ceiling and reading-in-context is the way past it, this switched-off ability is one of the most valuable things sitting idle. This problem is to plug it into the live reading path and measure honestly whether it helps.

## 2. WHY THIS ONE — under the 100%-BF gate
The pri-1 refutation (owner-DONE) proved type-level text-distributional meaning is EXHAUSTED (first-order co-occurrence provably conflates synonym/antonym/co-hyponym, Scheible-Schulte) and VALIDATED in-context/token-level reading as the way through. The in-context capability is built + measured but not live — the "landed ≠ live" trap on the #1 validated meaning lever. Making it live (if it helps) directly advances the frontier.

## 3. MEASURED vs INFERRED
- **MEASURED:** `sm.select_sense` reaches ~0.66-0.68 on the WiC board arm; type-level is 0.485 (chance-by-construction), context lifts it to 0.582 then 0.66-0.68 (pri-1 `exp_meaning_fusion_incontext_probe_v1`). `sm.senses` stays `[]` live; `sm.select_sense` has no live consumer (only a demo block + the board arm call it).
- **INFERRED (prove or refute WITH A NUMBER):** that invoking the context-gated sense read on the live comprehension path lifts a real board dim (WiC / sense / a downstream meaning-dependent dim) CI-separated, info-free twin losing, byte-identical when off — OR a located negative naming exactly why the in-context read has no live decision it can improve (the prior PARTIAL suggests this is not a clean win).

## 4. ALREADY TRIED / DO NOT REDO
- `the_meaning_win_is_offline_context_free_and_unwired` (integrated PARTIAL) already found the meaning win is offline/unwired — read it IN FULL; this problem is the wire+measure it did not close. Do NOT re-derive `select_sense` (it exists). Do NOT wire it as a decision-DEAD callable again (that is the current dormant state). Barred: spaCy / any external LLM at inference.

## 5. VERIFY BEFORE YOU START (the disk outranks this brief)
Read IN FULL: `hdlab/underspecified_sense_reader.py`, `hdlab/situation_reader.py` `_read_senses` (~L3091) + where the live read makes any sense/meaning decision, `hdlab/meaning_foundation.py`, the pri-1 SOLVED (`the_learned_is_a_taxonomic_identity_channel...`) + `the_meaning_win_is_offline_context_free_and_unwired`. INSTRUMENT your wire (count `select_sense` invocations on the board path) — the board's meaning dims may score a stand-in, not the live `read()`. CAP local runs below all cores (`OMP_NUM_THREADS=4 …`); heavy runs remote.

## 6. THE BAR (can-fail; a rigorous located-negative with a number is a full pass)
Wire the context-gated sense read into the live meaning path and SHOW a real board dim lifts CI-separated on modern prose (info-free twin losing, byte-identical when off), THEN flip default-on per no-more-default-off — OR a rigorous LOCATED NEGATIVE naming exactly why the in-context read cannot lift a live decision (with a number; e.g. no live consumer makes a sense-dependent choice the board scores). INVARIANT: recall path byte-identical; NO external tool/LLM at inference; instrument that your wire actually fires on the scored path.

## 7. FILES AND ENTRY POINTS
`hdlab/underspecified_sense_reader.py`, `hdlab/situation_reader.py` (`_read_senses`, the live meaning/sense decision), `hdlab/meaning_foundation.py`, `hdlab/diagnostic_context_wsd.py`; the board `experiments/exp_situation_model_qa_modern_v1.py` (WiC / sense dims); pri-1 folder + `the_meaning_win_is_offline_context_free_and_unwired`.

## 8. DO NOT QUOTE / DO NOT REDO
Do NOT quote retired figures (`notes/reference_retired_claims_never_requote.md`). Do NOT use spaCy / any external model at inference. Do NOT re-land `select_sense` as a decision-dead callable (that is the dormant state to fix). Do NOT claim a live win from a board number without instrumenting that your wire fired on the scored path (the strategy 2026-09-11 board-proxy caution). Do NOT assume a gain — the prior attempt was PARTIAL.
