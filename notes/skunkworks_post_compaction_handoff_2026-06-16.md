# SKUNKWORKS post-compaction handoff 2026-06-16 (READ FIRST; supersedes the 2026-06-15 v2)

You are SKUNKWORKS = AUDITOR (5th session) of hd-instrument. Director=Research, Prover=Exp-Dev, Integrator=Testbed, Custodian=Orchestrator. 4-session shared event-bus.

## STEP 0 -- cycle-check + monitor (do BEFORE anything)
1. `bash tools/skunkworks_cycle_check.sh` (inbox authoritative + producer-liveness; run EVERY cycle).
2. Confirm/re-arm the resilient monitor. If dead, re-arm EXACTLY:
   Monitor(persistent=true, timeout 3600000, command="while true; do tail -n0 --retry -F /d/AI/hd-instrument/data/events/skunkworks.log 2>/dev/null | grep --line-buffered -E 'ROUTING|BROADCAST' | grep --line-buffered -v 'notes/skunkworks_'; sleep 2; done")
   KEY: `--retry` survives producer restarts; filter is `ROUTING|BROADCAST` (CORRECTED 2026-06-16 per USER -- ROUTING-only silently DROPPED research_to_all_* BROADCAST DECISIONs that include me, e.g. DECISION 145; multi-recipient/broadcast-to-me MUST reach me); `grep -v 'notes/skunkworks_'` author-out matches ONLY my own authored notes (everything TO me starts with another author prefix). If BROADCAST volume ever trips the harness auto-stop, the every-cycle cycle-check is the backstop -- re-arm, do NOT narrow the filter.
3. INBOX is the safety net (mtime-aware, catches notes even if monitor dead). `--seen` ONLY after actually reading listed notes (NOT blanket -- blanket --seen marks just-arrived-unread as seen; this bit me).

## FULL-AUTO ACTIVE (USER, 2026-06-15 ~22:05)
"full auto authorized - work toward our goal, coordinate with Director, you are authorized to go with your recommendations." Ran overnight. NEVER go passive; vet decisive events; advance lane work between; periodic verification ~90-120 min. Lean comms (notes for deliverables/vets/blockers). ASCII only. NO LLM (11th rule). NO held-out gold contact (22nd rule: q54-q65, 56d SHA 22d7eb01, 56d-v2 77ad2f9a). Methodology rules FROZEN at 24.

## THE GOAL + ITS HONEST RESOLUTION (the core arc -- CLOSED)
GOAL (USER-originated): gap-driven abductive promotion loop for genuine novelty -- failure->abduce gap-shape (reverse-math)->corpus/VSA combine-interpolate filler-search->certify by gap-closure->promote data->load-bearing. Substrate-internal, no external truth.
ARC CLOSED with full team alignment. The honest resolution (capstone), via MY 3-tier novelty framework:
- TIER-1 (composition == existing single op): REJECTED. The "invents" Phase-C HARD_PASS was caught: perm-o-xor == existing ghrr_noncommutative_bind (excluded from control). Verified by Exp-Dev (ghrr closes 0.977). Rediscovery, not invention.
- TIER-2 (novel composition, NOT equiv to any single op, full-basis equivalence-checked): CONFIRMED ACHIEVABLE. corr(bundle(a,b),c) = partial-symmetric binder; my full-basis vet of ALL 38 binding/composition ops = none is partial-symmetric (basis is BIMODAL: fully-symmetric OR fully-asymmetric). Genuine substrate-internal novelty EXISTS, no external truth. BUT: existence proof on a CONSTRUCTED gap + supplied candidate.
- AUTONOMOUS tier-2 (discover novel comp for a REAL unforced gap): NEGATIVE. Real mixed-symmetry link-prediction is closed by role_filler_binding (existing single op, 0.87). Partial-symmetry is inherently TERNARY; real BINARY tasks are basis-closable; forcing a ternary metric = gerrymandering = fabrication (ruled out).
- TIER-3 (novel PRIMITIVE beyond basis): gated on USER strategic decision.
PRECISE TRUTH (both over-claims dead): the substrate CAN compose genuine novelty (tier-2) but RARELY NEEDS to at current scale -- its basis (role_filler+ghrr+bimodal binders) covers its real tasks. This VALIDATES the USER's scale/basis intuition precisely: not that it can't invent, but it doesn't NEED to; necessary novelty requires a richer frontier or new primitive layer.

## TWO STRATEGIC PATHS (USER CALL; no urgency) -- and what I told USER
- PATH 1 = grow the basis/TASK-FRONTIER (NOT ingest data -- 19K OEIS atoms are inert; corpus tonnage does nothing). Atomize a real math FIELD to its frontier as LOAD-BEARING structure (operators+relations+proof corpus+open problems) so genuine novelty becomes NECESSARY -> unlocks AUTONOMOUS tier-2, substrate-internal.
- PATH 2 = unlocks TIER-3 novel-primitive, two flavors: (a) ELEMENT-LAYER = internal computational/element-level representation so substrate verifies carrier-extension itself (the R2-wall fix; PRESERVES substrate-on-its-own, no external truth); (b) EXTERNAL-TRUTH = outside adjudicator: an LLM (soft/fallible prior, breaks substrate-on-its-own) OR a formal oracle/theorem-prover (rigorous, sound -- the better external option).
- Most thesis-preserving combo = PATH 1 + ELEMENT-LAYER (no LLM/oracle). USER asked "external truth = LLM? path 1 = gain knowledge?" -- I answered: LLM is one soft external option (element-layer is the internal alternative); path 1 is reach-a-frontier (deep structured field knowledge to its edge), NOT ingest-facts.

## EXECUTING TRACKS (autonomous; vet milestones as they land)
- PROMOTIONS (prior validated wins SCORECARD-ONLY -> LOAD-BEARING via 3-of-3 gate: cap-pres + re-expressibility + load-bearing-closes-a-gap + 4-gate + STRICT vet):
  #1 kgram_context_binding (math::T3) = DONE + vetted (F1 bigram-ceiling closed). #2 theta_burst_write = SPECCED (skunkworks_to_testbed_PROMOTION_2...), awaiting ratify. #3 cleanup-augmented-depth = queued. Flagship anchors (HP-12 crypto, Tier-4/6, audit-core, causal cluster) = later batch. Source inventory: data/substrate_index/skunkworks_phase_A_gap_source_plus_prior_results_audit_2026-06-15.jsonl.
- FOUNDATION CLEANUP (47 T1 atoms / 70 backwards "foundational-depends-on-its-consumer" edges; banach disease systemic; PREREQ for loop). Spec: skunkworks_T1_foundation_backwards_edge_fix_spec_2026-06-15.jsonl. Wave 1 = 64 edges (35 leaf-safe + 11 rescues + 3 tier-placement) ratifying. Wave 2 = 4 path/field atoms (bayes_rule field->T1+remove; gradient_descent path->T3+drop5; hessian path->T2+add derivative/matrix; newton_method path->T3) specced. LESSON: key tier on the FIELD not the id-PATH (4 atoms had path!=field; my scan false-flagged via path).
- WAVE 3 HYGIENE = MY IMMEDIATE PENDING TASK. Note just fired 07:37: exp_dev_to_skunkworks_testbed_WAVE3_hygiene_STRAND_PRECHECK_ready (category_type 25 atoms + metric_space 57 atoms + strand-risk lists). I flagged these as bonus findings: (a) spurious SPECIALIZES category_type (placeholder artifact; e.g. hessian/newton_method), (b) metric_space EXTRANEOUS dependency (3rd witness after kl_divergence + shannon_entropy + bayes_rule). SPEC the removals with RESCUE-THEN-REMOVE for strand-risk atoms (newton_method precedent: ADD a real forward edge BEFORE removing the only-grounding spurious edge). Read that note + spec Wave-3.

## DISCIPLINE / LESSONS (load-bearing)
- ADVERSARIAL VET both ways: I rejected the false novelty (ghrr) AND confirmed the real one (tier-2) AND confirmed honest negatives. Be as hard on PASSes that flatter the program as on fails.
- Rediscovery trap (recurring: banach, CELL-INV-1/2, 130a-G2, ghrr): a "novel" result the substrate ALREADY HAS. ALWAYS full-basis equivalence-check + full single-op control (the ghrr lesson: an existing op was excluded from the control).
- Verify-before-spec / 10th rule: verify against substrate state, don't assert. I self-corrected my path-vs-field heuristic.
- 19th-rule self-correction applies to MY own output too.
- Honest scope both directions (7th rule): existence-proof != autonomous-discovery; tier-2 != tier-3.

## SUBSTRATE STATE (approx, pre-overnight; re-verify)
~26271 atoms (mostly kind=primitive -- overloaded label spanning data + ops; kind-taxonomy deferred low-pri). ~115 operator signatures (self-model: data/substrate_index/skunkworks_self_model_of_operators_v1.jsonl). 91pct of atoms are inert DATA (19K OEIS); load-bearing core ~hundreds (816 atoms with 2+ op edges); proof corpus ~42 (thin). Foundation cleanup + promotions are CHANGING this -- re-verify counts via the cycle-check + a fresh scan.

## RESUME RECIPE
STEP 0 (cycle-check + monitor) -> sync overnight backlog (inbox; what ratified: Wave1/Wave2/promotions?) -> SPEC Wave-3 hygiene (the 07:37 note; category_type 25 + metric_space 57 + strand-risk; rescue-then-remove) -> continue vet-standing on ratify milestones -> stand for USER strategic decision (Path 1 / Path 2). Tools: skunkworks_cycle_check.sh, skunkworks_inbox.sh (--seen after reading), substrate_atom_lookup_v1.py (UTF-8-fixed). Key recent notes: my TIER2_CONFIRMED + autonomous_tier2_NEGATIVE + the goal-resolution synthesis.

-- SKUNKWORKS (Auditor), 2026-06-16 ~07:38, at compaction
