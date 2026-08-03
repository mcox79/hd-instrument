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

## 🆕 THE VALIDATION RESULT + THE DECISION (as of ~22:15Z — the current state; nothing in flight)
The richer discriminating eval (Director-verified, 15 items, defeats trivial baselines; commit dfa540a85) was RE-TESTED against the reuse-into-appraisal mechanisms (commit e34d54701/53c4cff8a) = **DECISIVE NEGATIVE, reuse-shortcut FALSIFIED:**
- CAUSAL-ATTRIBUTION coherence-ranking FALSIFIED: `_pick_strict_cb` (coref backward-search) IS recency (argmax position); on the recency-trap it fails 0/4 = identical to recency. "coref-as-bridging = same circuit" is WRONG at the mechanism level (pronoun-antecedent selection = recency/salience != causal-antecedent selection = coherence/EXPLANATION; shared hippocampal substrate, DIFFERENT selection signal).
- VALENCE-via-ToM falsified AS GENERAL: it's a RETALIATION predictor not an irony detector (1/3 genuine on real irony).
- BENEFICIARY = unaddressed gap (oracle-only).
**=> EVERY shortcut tonight is now falsified by a fair test (distributional / next-event-prediction / structural / construction-integration / reuse-of-organs). The inference this needs — which prior event EXPLAINS an outcome (causal-coherence), what an agent INTENDS beneath the surface (mentalizing), what an action FEELS like (affect) — cannot be shortcut; it must be EARNED from grounded experience.** This VINDICATES the foundational design's core claim (affect/causal dynamics must be EARNED via the experiential simulation, NOT supplied/reused) — now evidence-FORCED.

**THE DECISION (USER-gated, holding):** (A) COMMIT to building the EARNED experiential-simulation (the design's genuinely-new piece; multi-session, locked earn-not-borrow territory) vs (B) BANK the verified reading-layer milestone (causal organ 0.9722 given relations) + take the earned foundation up as a fresh dedicated push.
**DIRECTOR RECOMMENDATION = (A), built to the ENTIRELY-brain-foundational bar, STAGED + measurement-first:** it is the ONLY non-falsified brain-faithful path + existence-proof says it's possible. But it is NOT automatically "entirely brain-foundational" — hold these guards or it drifts: (1) REVENGE must EMERGE from primitive harm+targeting, NOT a supplied `retaliate` action label (the adversarial VET's #2 risk); (2) supply ONLY genuine innate (Spelke core); EARN affect/valence/causal-coherence from experience (Binder = yardstick only, not grounding); (3) the sim is a SUBSTITUTE for embodied experience with a NAMED limit (no 6yr multimodal life) — don't claim full understanding from a toy; (4) the SIM-TO-TEXT transfer must be a TESTED claim (adversarial VET #5), never assumed; (5) tonight added: earn causal-COHERENCE selection (which prior event EXPLAINS the outcome, Kintsch/Trabasso), NOT recency. FIRST STEP = a bounded CAN-FAIL cell (does the substrate EARN the appraisal->action dynamics + generalize to held-out agents, with random/memorized/no-appraisal floors that MUST fail) — NOT a blind multi-hour run; if the first cell shows construction-determination or non-transfer, we learned it cheaply.

## NEXT (recovery procedure)
1. Heartbeat: `date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp`.
2. Read WHERE_WE_ARE_NOW.md TOP BANNER (authoritative live state) + the foundational design `notes/foundational_grounded_knowledge_layer_program_2026-08-03.md` (§2b sim spec + §2c can-fail) + the adversarial VET `notes/audit_grounded_foundation_program_VET_2026-08-03.md` (the 6 holes the build must fix).
3. Await/confirm USER decision (A) commit vs (B) bank. Do NOT launch the multi-session earned-simulation build without USER steer (locked territory). If (A): dispatch ONLY the first bounded can-fail cell to the entirely-brain-foundational bar above; VET before believing (14+ over-reads corrected this 24h; every "win" narrowed on a fair test).
4. The one clearly-remaining gap after grounding = EVENT-EXTRACTION from raw text to feed the organs.
5. Ops: heartbeat turn-end; silent-death sweep ~30min (`python tools/inflight_monitor.py`); commit-after-bank local-only; NO origin push w/o in-session auth; only kill what THIS session spawned; subagents keep backgrounding runs -> verify results ON DISK.
