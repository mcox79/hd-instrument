# SKUNKWORKS post-compaction handoff v2 (2026-06-15 ~16:15; supersedes the session-start v1)

READ FIRST after compaction. You are SKUNKWORKS = the AUDITOR (5th session) of the hd-instrument substrate project. Director = Research; Integrator = Testbed; Prover = Exp-Dev.

## STEP 0 -- CYCLE-CHECK + RE-ARM MONITOR (do BEFORE anything; 9th USER-LOCKED rule + monitor-death lesson)
1. `bash tools/skunkworks_cycle_check.sh`  (inbox authoritative + producer-liveness; run EVERY cycle)
2. RE-ARM the harness Monitor (the consumer died once this session by event-volume auto-stop -- use ROUTING-ONLY filter, NOT ROUTING|BROADCAST):
   Monitor(persistent=true, command="while true; do tail -n0 -F /d/AI/hd-instrument/data/events/skunkworks.log 2>/dev/null | grep --line-buffered -E 'ROUTING'; sleep 2; done")
3. The INBOX is the SAFETY NET (catches missed notes even if monitor dead). Monitor is best-effort. Run cycle-check every cycle; `--seen` after processing. Ledger: data/skunkworks_seen_notes.txt (93 entries).

## WHERE THE PROJECT IS (as of DECISION 102)
- Phase 3 (retrieval mechanism): EXHAUSTED. M4d sparse-consensus graph-walk = the one mechanism (0.148->0.272 in-distribution, n=7). It is an IN-DISTRIBUTION-CONCEPT AMPLIFIER (+0.124 in-dist; +0.005 new-concept = essentially nothing). 8 augmentations all failed.
- Phase 4 (enabling machinery; USER Level-2 directive): DELIVERED. 4a = 100 operator self-model signatures (LLM-bootstrapped selection per USER ruling; signatures sound). 4e = substrate-SELF-SELECTION operational + production-closed (Claim 15 MEASURED): the substrate picks its own next operators via a composite substrate-internal scorer (no LLM prior); Skunkworks authors + vets.
- Substrate self-corrects its own graph (Claim 14): 5 non-additive op classes validated (edge REMOVE + atom DELETE + edge R&R + tier mutation + atom MERGE) with atomic rollback (2 HARD_FAIL-recovered, 0 unrecovered).
- 84 DEPENDS_ON 2-cycles found; cleaned in batches (v1 10 + v2 batches); ~60 ambiguous held.
- Substrate-product positioning: 15 claims; 14 MEASURED + 1 OPEN.

## SUBSTRATE STATE (post DECISION 103c; ~26283 atoms / 5290 relations / 215/215 axiom-term / cap_pres=1.0)
Self-model: skunkworks_self_model_of_operators_v1.jsonl = 110 signatures (100 Phase4a + 5 batch1 + 5 batch2). (Relations 5290 = +21 net from 103c: 17 STRICT + 4 HAS_USERS auto-reverse.)

## MY OPEN / PENDING ITEMS
1. **Phase 4e batch 2 -> RATIFIED (DECISION 103c HARD_PASS, 2026-06-15):** 17 STRICT (13 SPECIALIZES + 4 USES) + 5 sigs + measure_space correction all landed; R3 preserved; Claim 5a MEASURED on substrate state. CLOSED.
2. **P2 atom-MERGE inventory re-audit (DECISION 102b) -> DELIVERED:** data/substrate_index/skunkworks_atom_merge_inventory_revised_classification_2026-06-15.jsonl + note skunkworks_to_research_testbed_DECISION_102b_COMPLETE_*. HEADLINE: cleanup/cosine_cleanup (413-edge highest-stakes) is NOT a merge -> SPECIALIZES_fix; the 413-edge mass re-point is RETIRED. 16 candidates: 6 genuine_MERGE (kl pair + 4 tier-stub dups + collins word-order) / 4 SPECIALIZES_fix / 1 other_relation_fix (global_discrete/convex) / 3 needs_review (operator vs sub_op + decoder vs decoding -- await Director schema ruling). Phase 3 sequencing recommendation inside.
3. **Standing:** await Director ruling on the 3 needs_review schema questions; Testbed owns Phase 3 execution (gated on pre-check; do NOT execute mutations myself); vet future Iter-4+ STRICT candidates; cycle-cleanup batch 3 (~60 ambiguous, textbook review).

## INBOX GLOB FIXED (2026-06-15 post-compaction; 19th-rule self-correction)
tools/skunkworks_inbox.sh globbed `*to_skunkworks*` and SILENTLY DROPPED multi-recipient notes where skunkworks is secondary (research_to_testbed_skunkworks_*). Fixed to `*skunkworks*` + author-out guard (skip skunkworks_to_*). The cycle-check now genuinely catches ALL skunkworks-addressed notes. Ledger reset to 171-entry baseline.

## CLAIM 5 -- the honest open question (split into two sub-claims)
- MEASURED on MEMBER-GROWTH path: authoring new operator/family signatures yields new sound STRICT edges at grounding (batch 2: 17 new STRICT, 0 reject). BUT all are authored-from-textbook relations among PRE-EXISTING atoms.
- STILL OPEN on AUTONOMOUS-DISCOVERY: the substrate does NOT autonomously discover STRICT relations to structurally-NEW atoms, nor re-discover on grounded atoms (Iter 3 = 0; Iter 4's one candidate measure_space->set was REJECTED by Skunkworks as mis-typed). Generalization is AUTHORING-DRIVEN member-growth, not autonomous concept-invention.

## HONEST TRUTH-STATE (do NOT let re-inflate)
- M4d is in-distribution-amplifier only (n=7; 9/14 gold shared with dev); new-concept lift +0.005.
- Selection is substrate-driven but SIGNAL-DESIGN of the scorer is Skunkworks's bootstrap (~10 of ~110 sigs substrate-selected; mechanism proven, scaling pending).
- MY OWN MISSES this session (the discipline catches mine too): 2 leaf-strand failures (batch-2b family edges + 84a re-tier) auto-rolled-back; measure_space specializes->composed_of error (caught on vet); the monitor-death lapse (missed DECISION 100/101/102; fixed via cycle-check). 19th-rule self-correction operating on Auditor's own output repeatedly.
- I also made GOOD catches: integral/lebesgue NOT-a-merge (SPECIALIZES), PP-376 re-type, cleanup_retrieval dup, em_algorithm genuine-merge -- relation-type-precision both directions.

## TOOLBOX (new/key this session, under hd-instrument/)
tools/skunkworks_cycle_check.sh (NEW; run every cycle); tools/skunkworks_inbox.sh (authoritative inbound); tools/skunkworks_gold_connectivity_profile.py (28th-finding). Self-model: data/substrate_index/skunkworks_self_model_of_operators_v1.jsonl. The Phase-4e self-selection scorer is INLINE python (composite: 3*pointer_nominations + 2*family_member + min(op_out_degree,5); dedup pre-filter excludes signed+merge-syn+superseded+_atom). Vet pattern: STRICT/PLAUSIBLE/REJECT; SPECIALIZES/INSTANCE_OF are STRICT-by-direction (DECISION 101); others need tier-gradient. Pre-check stack (Exp-Dev): forward-walk + corpus-scoped tier-monotone + axiom-term + dangling. tier-monotone is MATH-CORPUS-SCOPED (cross-corpus exempt). capability->math edges = USES not DEPENDS_ON.

## SAFETY (HARD)
ASCII only (no emoji/em-dash in notes/code); NEVER AskUserQuestion; local CPU (remote GPU is C:/dev/hd-instrument Windows-native via ssh marsh@home, NOT WSL); substrate-on-its-own (11th); 18th refuse-what-can't-prove; 19th adversarial-self-correction (incl own output); 22nd held-out gold (q54-q65, 56d SHA 22d7eb01, 56d-v2 SHA 77ad2f9a) DO-NOT-INGEST; gate state-mutations on the pre-check stack, NOT on my analysis (the leaf-strand lesson). Methodology rules FROZEN at 24 (Director). Notes for handoffs/deliverables/blockers only; lean.

-- SKUNKWORKS (Auditor)
