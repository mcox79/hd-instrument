# DIRECTOR POST-COMPACTION BACKUP — 2026-08-03 NIGHT (self-contained; READ FIRST)

Branch `dataprep/mcguffey-graded-corpus`, all LOCAL, NO push. This is the current recovery anchor (supersedes the 07-30 backup). Live blow-by-blow = `notes/WHERE_WE_ARE_NOW.md` TOP BANNER (authoritative).

## THE GOAL (unchanged)
A glass-box HDC/VSA (FHRR) substrate that genuinely COMPREHENDS narrative and you can CONVERSE with — earning meaning the brain's way. Invariants: glass-box always; NO borrowed embeddings / NO external LLM at inference / NO bolt-on reader-parser; supplying DATA/knowledge/a dictionary is fine; store LOCAL-ONLY, git-commit after every bank, NO origin push without in-session auth.

## 🧱 THE FOUNDATIONAL PIVOT (USER 2026-08-03 — the night's real conclusion)
The session's ~8 "we weren't doing it right" corrections are ONE failure, not eight: we tried to comprehend goal/affect/social meaning (revenge, anger, care) from ungrounded TEXT, with no grounded foundation for the words to land on. **Reading BUILDS ON a grounded ~6yo conceptual foundation; a book doesn't teach what anger/revenge ARE — it assumes you know.** USER: "there needs to be a foundational knowledge all other knowledge builds upon... strive for that ~6yo foundation. You can't learn revenge and anger from a book. There must be work on this."

**NEW PROGRAM = the FOUNDATIONAL GROUNDED-KNOWLEDGE LAYER** ([[project_build_the_6yo_grounded_foundation_reading_builds_on_USER_2026-08-03]]; design doc `notes/foundational_grounded_knowledge_layer_program_2026-08-03.md`):
- SUPPLY only genuine INNATE core (Spelke agent/object/goal-directedness — the brain doesn't earn these either).
- EARN affect/goal/social meaning (appraisal theory: anger = goal-blocked-by-an-AGENT + retaliation-tendency = the ground of "revenge") via a minimal NON-TEXTUAL EXPERIENTIAL SIMULATION (the substrate's substitute for pre-literate experience).
- A LIVING SELF-EXTENDING grounded STORE: the substrate ADDS what QUALIFIES (grounding-transfer from grounded primitives / experiential / verified-relational), gated by the self-improving-loop consolidation + a FALSE-CONSOLIDATION guard (headline safety metric).
- THEN reading maps text onto the grounded foundation via the existing organs (which become the READING layer).

## USER BARS (govern everything — LOCKED)
- **EARNED understanding, NOT supplied-assignment** (higher than the meaning=assignment lock; resolves the fork toward understanding). Binder = DIAGNOSTIC/yardstick ONLY, not the grounding [[feedback... not in a memory slug: see WHERE]].
- **Brain-foundational in EVERY aspect we can**; supply only genuine innate, EARN what the brain earns from experience; name the honest limits (we can't give it 6yr of embodied life — the simulation is a substitute).
- **For EVERY mechanism ask (1) which BRAIN STRUCTURE does this? (2) does it SHARE an already-developed process -> REUSE that organ** [[feedback_for_every_mechanism_ask_which_brain_structure_and_does_it_share_existing_processes_USER_2026-08-03]]. The brain reuses circuits; a parallel build = non-faithful + islanding.
- Select by brain-foundational-RIGHT, not cheap [[feedback_select_by_brain_foundational_right_not_by_cheap_regardless_of_hard_USER_2026-08-03]]. Existence-proof: keep digging, a miss is not a ceiling until fair+brain-faithful both hold. VET negatives AND positives hard (13+ of my over-reads corrected this 24h — report MEASURED not READ).

## VERIFIED GROUND (the READING layer, sits ON TOP of the foundation)
Full glass-box comprehension stack, built+WIRED+USED: `hdlab/coreference_resolver.py` (dense B3~0.87), `situation_model_accumulate.py` + `situation_model_multibank.py`, `self_improving_loop.py`, `CausalLinkRegister` (CAUSAL organ, DIRECTOR-VERIFIED 0.9722 cross-chapter GIVEN links), Trabasso goal->causal, Sally-Anne ToM organ (HARD_PASS). These WORK GIVEN structured relations — they just had no grounded meaning underneath, and now become CONSUMERS of the grounded appraisal function.

## WHAT'S BEEN LEARNED TONIGHT (the grounded-appraisal-via-REUSE thread)
The grounded-appraisal computation (disambiguate goals/affect) is turning out to be largely REUSE of proven organs, validated on cheap fair+brain-foundational probes:
- **TARGET (self/other)** = coreference (have it).
- **CAUSAL-ATTRIBUTION (did agent X block agent Y's goal)** = coref-as-BRIDGING: built as a literal retarget of `_pick_strict_cb`/Centering backward-search (commit d3b035e59). REAL but NARROW — trustworthy-gate (commit bce466189) CORRECTED the Director's over-read: the coherence-RANKING is a NO-OP (0-1 candidates ever), the win is an entity-linking FILTER beating recency on ONE item + matching oracle on a corpus with NO multi-candidate cases. Circuit-sharing (coref==bridging) = HYPOTHESIS, NOT validated (ranking untested).
- **VALENCE (harm/help intent)** = mentalizing/ToM: intent toward the BENEFICIARY (goal-object), not surface word — being tested by REUSING the Sally-Anne ToM organ (probe a5a027481 in flight).
- **Recurring bottleneck**: the 12-item eval is too thin to test the mechanisms (ranking never fired; valence a wash under scramble; oracle-only). -> BUILDING a RICHER DISCRIMINATING eval (multi-candidate blockers + irony-vs-sincere + beneficiary-vs-patient; trivial-baseline-DEFEAT check; Director-verify-gated) in flight (a0f0373f).
- Remaining clearly-open gap after grounding is validated = EVENT-EXTRACTION from raw text to feed the organs.

## IN FLIGHT (as of ~21:34Z)
- a5a027481 = valence-via-mentalizing (reuse ToM organ) probe.
- a0f0373f = build the richer discriminating grounded-appraisal eval (UNVERIFIED, Director-verify-gated).

## NEXT (recovery procedure)
1. Heartbeat: `date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp`.
2. Check the two in-flight agents' results ON DISK (subagents repeatedly backgrounded runs + dropped reports tonight — verify metrics.json on disk, don't trust "done"). 
3. When the richer eval lands: DIRECTOR-VERIFY the gold (gold quality has bitten us: material_want-hijack, conflict-origin-cause, 2 muddled thwart items), then RE-TEST bridging (coherence-ranking on multi-candidate cases) + valence-via-mentalizing on it = validate/falsify the reuse-into-appraisal approach PROPERLY.
4. Then decide: the earned experiential-simulation build (the design's only genuinely-new piece) + event-extraction. Do NOT launch the multi-session simulation build without the richer-eval validation + USER steer. Brain-structure/shared-process gate on every new mechanism.
5. Ops: heartbeat turn-end; silent-death sweep ~30min; commit-after-bank local-only; only kill what THIS session spawned.
