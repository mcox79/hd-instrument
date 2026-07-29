# WHERE WE ARE NOW — clean current state (tier 3; REWRITE each session) — updated 2026-07-28 (clean consolidation)

## Direction (read FIRST)
1. GOAL + invariants + anti-drift: `notes/SUBSTRATE_CHARTER_read_first.md`
2. Plan: `notes/THE_PLAN.md`
3. This = the live snapshot (rewritten clean; tonight's blow-by-blow collapsed to pointers).

## THE GOAL
Glass-box VSA/HDC substrate you can CONVERSE with that genuinely REASONS, EARNING its meaning + knowledge the brain's way (NO borrowed embeddings/LLM at inference; the substrate learns it itself). CLS architecture: SEED a foundation from relational KBs -> READ new material -> SLEEP-consolidate. 3 legs: (1) earn MEANING, (2) REASON over it, (3) LEARN from reading.

## ✅ BANKED — do NOT rebuild (all VET-survived; local-only store, tail 29591)
- **LEG 1 EARN MEANING (29591 CHAIN_GRADE):** own from-scratch encoder on 237M-token ARC (no borrowed vectors) beats grounding on held-out-NEW concepts (+0.050 sem / +0.071 rel text-alone, both seeds, controls at chance). Scale WORKS + is DATA-LIMITED. Modest band (0.56-0.63), held-out-NEW placement of corpus-seen concepts, NOT zero-shot invention. Specs: 6L/512d/128ctx/16k-vocab, MLM on ~158M ARC-science tokens.
- **LEG 2 REASON (29587/88/89):** learned encoder does genuine inductive relational inference on held-out-NEW concepts (beats grounding-homophily +0.108, non-learned 2-hop +0.093; dose-response in #constraints). Local decision-time reasoning EXHAUSTED -> composition lives IN the representation (encode-time), not bolt-on.
- **FOUNDATION (29585):** cskg_foundation_v1 (gitignored 258MB): 482,588 concepts / 1.24M typed edges, cleaned/canonicalized/grounded (Lancaster/concreteness/VAD/AoA), glass-box. Ingest fixed+verified (director-KB 2.83M triples; query via tools/director_kb_query.py).

## 🧭 THE CONVERGED PICTURE (this session's arc — the key strategic update)
The encoder's ~0.56-0.63 held-out-NEW ceiling is **NOT cheaply liftable.** Every cheap lever was tested and spent this session — so the real lever is the deeper COMPREHENSION MECHANISM (situation model), now proven-by-elimination rather than assumed.

**WINS (banked this session):**
- **READOUT FIX = HARD_PASS_MAJORITY, WIRE.** Relational placement is substantially READOUT-limited, not representation-limited. Learned rank-32 bilinear readout beats cosine-NN on held-out-NEW by ~+0.038 mean (2/3 diag-seeds clear +0.03, CI excludes 0; relObj cross-seed +0.043/+0.050 informational). Controls clean, leak-proof. CAVEAT: only 1 MLM training-seed ckpt on disk -> training-seed replication still OPEN (needs a 2nd baseline ckpt). Module: experiments/_learned_relational_readout.py. It's the fair-test harness for any encoder.
- **gated_fusion ISLAND CASHED IN = two-seed HARD_PASS, WIRE.** Per-axis learned gate strictly Pareto-dominates fixed z-avg on both axes both seeds (all 5 pre-reg bands, lambda=0.5==zavg xcheck exact, VAL!=TEST leak-assert, remote==local parity). HONEST SCOPE: a better fusion OPERATOR, NOT a grounding rescue (grounding doesn't transfer); gains small. Module hdlab/gated_fusion.py.

**NULLS (clean, banked this session):**
- **Objective axis DEAD:** relObj retrain (L_mlm+lambda*L_rel from foundation edges) HARD_FAILED both seeds; the full R3/R4 self-teacher (landmark+VICReg+relational-InfoNCE+EMA) tied grounding. The relational OBJECTIVE is not the lever. (Narrow scope: a different objective isn't logically ruled out, but two serious attempts failed.)
- **Grounding DEAD (HARD_FAIL_NO_TRANSFER, both seeds):** experiential (Lancaster sensorimotor, 11-dim) grounding as a training auxiliary does not transfer to held-out-NEW (sem_margin -0.0065, rel ~0). BRAIN-FIDELITY DIAGNOSIS: sensorimotor grounding is for CONCRETE perceptual meaning; the brain grounds ABSTRACT/RELATIONAL meaning RELATIONALLY (from the graph). Mismatch -> null was predicted. SHELVED (revival: relational grounding from the foundation, not sensorimotor).
- **Breadth NULL (seed_7; seed_13 replicating):** v4_breadth (v2 MLM + ARC+SimpleWiki+breadth_v1 at EQUAL 121.08M token budget, one variable = source diversity) does not lift held-out-NEW vs the v2 baseline (readout-margin -0.0096, cosine -0.0054; within HARD_FAIL band). Clean controls, leak-safe all 3 sources, budget pinned. Likely mechanism: SimpleWiki diluted science density at equal budget. HONEST SCOPE: refutes the CHEAP equal-budget general-diversity hypothesis; does NOT refute much-more/richer data (full enwiki 4B untested).

## 🔴 THE FRONTIER — COMPREHENSION MECHANISM (situation model)
The deep gap: our encoder produces a shallow TEXTBASE (bag-of-contextualized-tokens); the brain builds a dynamic updatable SITUATION MODEL (entities/state/time/causality/goals; Kintsch, Zwaan, Frankland-Greene, Rabovsky). Binding is ROLE-GENERAL not positional — brain (lmSTC AGENT/PATIENT slots) AND our own probe agree (position-bind 0.52 self-consistency vs mean-pool 0.95).
- **Full design + biology + invariants + measurement bands: `notes/comprehension_situation_model_frontier_scoping.md`.**
- **First can-fail experiment (design A, IN FLIGHT):** entity-slot scaffold + a small LEARNED write-gate on the FROZEN encoder's own hidden states (reuse hdlab/sequence_memory.SequenceMatrix). Same cheap "learned head on frozen reps" class as the readout fix — NO retrain. Extends the calibration-first instrument in place. Measured with the MANDATORY untrained-random-init control + calibration gate (a known reader must clear the new construction first). Escalation path = design B (forward state-prediction self-teacher).
- INVARIANTS (locked): learned gate NOT a hand-coded resolver (state_of_mind.py resolvers are SHELVED for this); frozen OWN encoder, no borrowed embedding as meaning organ; no external LLM. Supplying STRUCTURE ok; supplying the MECHANISM forbidden.

## 📏 MEASUREMENT STATE (what to trust)
- **VALID = the calibration-first order-critical instrument** (experiments/diag_order_critical_comprehension_calib_v1.py): order-critical minimal pairs where scrambling changes meaning; ACCEPTANCE = a known reader (MiniLM/BGE, diagnostic-only) must pass. This is the ONLY comprehension measure to trust. Score our encoder only after a known reader passes.
- **INVALID = the relation-cloze ruler** (eval_battery_relational_cloze_v7): content-cued (a known reader shows no coherent>scrambled margin) -> does not require reading order. Do NOT draw comprehension conclusions from it.
- Comprehension "encoder reads" signals so far are weak/seed-dependent (seed-7 entity-state +0.283 did NOT replicate on seed-13 +0.130). Superseded comprehension-loop history (v1-v6, 3 stacked measurement artifacts found+fixed): pointers in notes/how_the_brain_reads_comprehension_target_audit_2026-07-28.md, notes/brain_fidelity_full_pipeline_element_audit_2026-07-28.md.

## ⏳ IN FLIGHT
- **Breadth seed_13** (GPU, ~3h) — replicating the seed_7 null to close the data-lever verdict. HEALTHY (verify via ckpt-mtime + GPU-util, NOT the coarse ~6000-unit heartbeat that false-alarmed 3x).
- **Comprehension exp A** (remote CPU) — re-dispatched after an API-flap crash (told to commit early/often); status uncertain, awaiting notification. Do NOT re-dispatch a 3rd time into an unstable API on speculation.

## 🅿️ PARKED (with triggers — not islands)
- **gate code-swap** z-avg->gate in the encoder eval/loop fusion path — HELD until breadth lands (don't destabilize breadth's live eval). Realizes the gated_fusion WIRE.
- **remote fleet-health** — deferred to GPU-idle, NON-destructive: the marsh@home checkout is 1515-behind + dirty BY DESIGN (SCP-freshness per queue_add Patterns 1-6; unsynced result files -> do NOT git reset). Real gaps: queue_add doesn't auto-stage corpus data (fixed ad-hoc this session; testbed durable-fix candidate); remote metrics.json not synced back.
- **bigger data bet** (full enwiki ~4B) — only if we later decide raw volume (not equal-budget diversity) is worth testing; not now.

## 🛠️ OPS LESSONS (this session, durable)
- **Remote liveness: trust ckpt-mtime + GPU-util, NOT the heartbeat** (coarse ~6000-unit cadence fooled the Director 3x into false stall/stale alarms).
- **VET + REPLICATE positives before believing** (seed-luck over-reads recur; check the active-control's GAIN not level; single-seed = hypothesis).
- **Verify what you SAY is in flight** (caught myself repeating "gated_fusion queued" without checking — it wasn't).
- Capability gate healthy: registry 41 rows, undecided 24->0 (triaged), 'other' artifact excluded. Run `tools/capability_registry_audit.py` at session start.

## STORE / DISCIPLINE
Tail 29591, LOCAL-ONLY. Origin pushed to HEAD this session (USER-authorized, private repo mcox79/hd-instrument) so remote runs importing new hdlab modules resolve. NO further push without in-session USER auth. Only stop/kill what THIS session spawned. Heartbeat every turn-end. Brain = existence proof; on every negative evaluate the difference vs the brain + iterate.
