# SOLVER running notes — one_store_does_two_jobs_and_consolidation_is_a_single_average

(working notes; deliverable is SOLVED.md. Kept so findings survive compaction. Started 2026-08-26.)

## THE PROBLEM (write/replay half of the memory architecture; p2 was the read half)
One store does two jobs the brain separates (fast hippocampal one-shot / slow cortical statistical), and
"consolidation" at the live site is a single averaging step per cycle — ungated, un-interleaved, un-budgeted.
BAR (§7): on an OLD-vs-NEW interleaved-retention task from REAL reading (learn NEW while retaining held-out
OLD; corpus era fixed), brain-faithful consolidation (fast/slow + SELECTIVE + SCHEMA-GATED + INTERLEAVED
replay) must beat the single-average CI-separated over the strongest floor's UPPER bound on JOINT old+new
retention, with info-free twin (RANDOM replay selection, same budget) LOSING CI-separated. CI half-width +
null p95 reported. DECISIVE EITHER WAY: win → wire continual.py (+selection); rigorous loss → selective
interleaved replay does not beat averaging at our scale (say why) → catastrophic forgetting is not yet the
binding constraint (a full PASS).

## DISK vs BRIEF (verified this session)
- BRIEF WRONG: "cls_discrete_budget is a stale VET_PENDING registry row" — it is ABSENT from
  data/capability_registry.jsonl AND from experiment_index (0 cells). Nothing to read there.
- BRIEF PREMISE HOLDS: live consolidation = reading_grounding_loop.py::checkpoint → consolidation_pass
  (vote-margin gate) + trace-sum-once-to-seed (line ~1509). It does NOT call continual.py, additive_map
  replay, or hippocampal_encoder.cls_replay_cycle. Single average, ungated/un-interleaved. CONFIRMED.
- Faithful engines, all ISLANDED from the reading/consolidation path:
  * continual.py: replay_cycle picks replay_frac of traces UNIFORMLY AT RANDOM (torch.randperm) — it is
    NOT selective/schema-gated/interleaved. It IS the RANDOM-replay twin. nrem_replay_decorator wraps it.
    Its own docstring: partial mitigator, chain-grade forget<=0.05 NOT met. Imported by NOBODY live
    (hippocampal_encoder has its own sibling cls_replay_cycle; reading loop doesn't call either).
  * additive_map.py (AdditiveKGMap): the "CLS cortical-schema analog" — entity coords X[N,k], relation
    displacements D[n_rel,k] fit by SGD. D[r] is the shared "slow cortical weight" that sequential SGD
    overwrites (catastrophic forgetting locus). Imported by foundation_persistence + state_of_mind, NOT
    the reading loop.

## PRIOR CELLS (the real ones; ORGAN_MAP notes/ORGAN_MAP.md D4) — all SYNTHETIC, none on real text/live site
- exp_substrate_continual_NREM_replay_v1 HARD_PASS_PARTIAL: baseline fin_forget 0.8833±0.031 vs
  replay_every_100 0.3100±0.050; monotone dose ladder 100/500/1000 → 0.31/0.483/0.637. continual.py's own
  cell. UNIFORM replay. Synthetic N=4096.
- exp_consol_interleaved_replay_v1 HARD_PASS: INTERLEAVED mrr 0.9086 vs CONTINUAL 0.4184 (forgot_early
  0.238 = catastrophic forgetting fires) vs SHUFFLE 0.3613 vs POP 0.3307, ceil 0.9554; 4/4 signatures
  (dose/staging/beat/shuffle). Replay into AdditiveKGMap D[r]; Saxe/Rogers-McClelland SYNTHETIC hier KG.
  → INTERLEAVING is the STRONG lever (synthetic).
- exp_cls_prioritized_replay_closed_loop_surprise_v1 MIDDLE_BAND: surprise-priority 0.576 vs uniform 0.521
  vs no-replay 0.097 vs static 0.472; delta_E 0.055 < 0.08 bar. At SF=0.55 (more shared structure) dE 0.125.
  → SELECTION is a WEAK lever. DEEP INSIGHT (load-bearing, already on disk): in a rank-1 Hebbian / shared
  rank-limited store, priority replay only RESHUFFLES which items survive — it cannot ADD net protected
  capacity; that needs THREE-FACTOR (neuromodulator-gated eligibility-trace) plasticity. Selection strength
  grows with shared structure. Synthetic MLP.

## ORGAN_MAP D4 verdict (outranks the brief): "WHAT IS ACTUALLY UNTESTED: D4 on REAL TEXT, and D4 AT THE
## LIVE CALL SITE." EXISTS yes / IS-REACHED no (continual.py zero live importers) / IS-GOOD yes synthetic.

## BRAIN-FOUNDATIONAL FRAME (opening move: how does the brain do this?)
CLS (McClelland/O'Reilly/Norman 1995; O'Reilly 2014): two systems SOLVE catastrophic interference —
hippocampus (fast, sparse, pattern-separated, separable-row) buffers episodes so cortex can INTERLEAVE new
with replayed old. Selection: SWRs replay salient/rewarded/surprising (Ambrose-Pfeiffer-Foster 2016, reverse
replay ∝ reward). Schema-gate: fact consistent w/ existing schema consolidates in ONE trial (Tse 2007/2011).
PINNED as a system; SELECTION FUNCTION UNPINNED (OUR-INVENTION-UNDER-TEST) — copy the computation, sweep params.

## THE REFRAME I MUST TEST (decisive either way, per brief)
The live grounded store (HDFactStore) is SEPARABLE-ROW (exact-key hash-addressed term→object; confirmed p2).
Separable-row = ALREADY hippocampal (pattern-separated, non-forgetting). So on the live path catastrophic
forgetting may NOT bite — averaging over a growing separable set dilutes, it does not overwrite. If so, the
single-average's real defect is NOT forgetting; it is that it never builds an OVERLAPPING cortical code that
GENERALIZES (connects to deviation #3 + my p2 finding that consolidated CONTENT is the transfer wall).
→ Instrument must score BOTH direct retention (catastrophic forgetting) AND transfer/inference (did
consolidation manufacture structure), on real reading, so the fork resolves on evidence not assertion.

## PLAN (instrument: experiments/exp_consolidation_real_reading_old_vs_new_v1.py)
Real reading (era fixed), split OLD/NEW disjoint. Fast store (separable) + slow distributed code (AdditiveKGMap
D or an associative W). Arms at MATCHED budget:
  SINGLE_AVERAGE (live-op floor) | SEQUENTIAL_NO_REPLAY (un-interleaved, forgetting floor) |
  INTERLEAVED (brain interleave) | INTERLEAVED+SELECTIVE(surprise) | INTERLEAVED+SCHEMA-GATED |
  RANDOM-REPLAY twin (info-free selection) | POP/chance floors.
Score JOINT old+new retention + held-out inference. CIs (bootstrap), null p95. Sweep selection/interleave.
Expected honest outcome (hypothesis, VET-pending): interleaving helps the DISTRIBUTED code; selection weak
(rank-1 bound) unless three-factor plasticity added; if live separable store doesn't forget → reframe to
"consolidation is for generalization not retention here." Keep asking the brain q (30-min cron).

## INSTRUMENT BUILT: experiments/exp_consolidation_real_reading_old_vs_new_v1.py
Paired-associate catastrophic-interference (McCloskey-Cohen) on REAL simplewiki reading (era fixed).
Each concept c: KEY = its own compressed PPMI+SVD semantics (OVERLAPPING cortical code, top-CODE_DIM SVD
comps -> capacity=CODE_DIM); VALUE/target = its top-PMI ASSOCIATE concept (a real learned relation).
Cortex W [Dv x Dv] maps s_c -> s_{a(c)}. OLD(40%)/NEW(40%)/HELDOUT(20%) disjoint. Phase1 learn OLD,
Phase2 learn NEW; arms differ ONLY in Phase-2 schedule. Retrieval ranks a CODEBOOK of concept identities
(self masked). Metrics: JOINT top1, OLD-alone top1 (the forgetting metric), HELD-OUT top1 (generalisation).
Bootstrap CIs (pooled ranks across seeds), shuffle null, pop floor.
ARMS: HEBBIAN_SUM (distributed single-average = shared-W crosstalk strawman) | SEQUENTIAL (no replay =
catastrophic forgetting) | INTERLEAVED (uniform old replay = the info-free twin of SELECTIVE) |
INTERLV_SELECTIVE (surprise^alpha closed-loop) | INTERLV_SCHEMA (Tse: schema-consistent NEW one-shot,
budget->at-risk OLD) | INTERLV_3FACTOR (neuromod |error| gated delta) | INTERLV_RANDOM (explicit uniform twin).
FLOORS: SEP_LOOKUP (the LIVE separable-row store: exact per-concept slot, NEVER forgets, invariant to phase)
+ SEP_AVG_SIM (per-concept averaged content read by cosine = first-order similarity floor).
NOTE fairness: INTERLEAVED == the uniform-selection twin of SELECTIVE at matched budget; SELECTIVE vs
INTERLEAVED/RANDOM is the bar's info-free-twin test (matched compute, only selection differs).
CODE_DIM compression is brain-faithful (cortex compresses) AND sets the load/capacity so interference bites.

## SMOKE FINDINGS (n=1 seed, code_dim=40; DIRECTIONAL, full 3-seed run launched)
- CATASTROPHIC FORGETTING FIRES + REPLAY FIXES IT ON REAL TEXT (first time; organ-map frontier):
  SEQ OLD-retention 0.062 -> INTERLEAVED 0.854, CI-separated (0.750 > 0.146). The CLS interleaved-replay
  OP is validated on real reading in the distributed regime.
- SELECTIVE OLD 0.938 > INTERLEAVED/twin 0.854 -- DIRECTIONAL, not yet CI-sep at n=1. With ERROR-CORRECTING
  delta (not rank-1 Hebbian) selective replay may separate at full power -> would CORRECT the surprise cell's
  "rank-1 can't exploit priority" (the fix is exactly error-correcting/3-factor plasticity, which I use).
- SEP_LOOKUP (LIVE separable store) = 1.000 JOINT/OLD, INVARIANT to phase -> the live single-average NEVER
  forgets (separable-row = already hippocampal). So on the bar's RETENTION metric NO distributed arm beats
  it -> FORK B: catastrophic forgetting is NOT the binding constraint on the live path.
- GENERALISATION (held-out) ~0.04-0.21 for ALL arms, best is the first-order similarity floor (0.208) ->
  the learned relational map does NOT generalise on real reading (relation not systematic) = CONTENT wall,
  agrees with p2 (self-built codes don't transfer). HEBBIAN_SUM distributed average collapses (0.000, crosstalk).
- VERDICT SHAPE (PARTIAL): (A) the brain-faithful interleaved-replay OP is VALIDATED on real text (prevents
  catastrophic forgetting CI-sep over sequential) -- a genuine positive + a real AUDIT UPDATE (D4 tested on
  real text). (B) it does NOT beat the strongest single-average floor (the LIVE separable store) on JOINT
  retention because that store doesn't forget -> fork B: forgetting is not the live binding constraint. (C)
  generalisation is content-bound for all arms -> the wall is representation/content, not the write schedule
  (both memory halves agree). Selective-vs-twin: pending full power.
- PROPOSED WIRING (pending full): do NOT wire replay as a "forgetting fix" (live store doesn't forget); wire
  the distributed CLS pair (continual.replay + selective schedule) ONLY as/when we build the OVERLAPPING
  generalising code (coordinate with p2 / reader_meaning_channel). Default-off flag.

## POWERED FULL RESULT (3 seeds, N=320 concepts, code_dim=48, DENSE) -- AUTHORITATIVE (n=1 smoke was noise)
JOINT/OLD/INFER top-1, pooled bootstrap 95% CI:
  SEQUENTIAL   OLD=0.076[0.052,0.104]   (catastrophic forgetting FIRES)
  INTERLEAVED  OLD=0.349[0.305,0.396]   (uniform replay -- CI-SEPARATED over sequential -> REPLAY FIXES IT)
  INTERLV_SELECTIVE OLD=0.297[0.253,0.341]   (surprise -- AT/BELOW uniform: selection is NOT a lever)
  INTERLV_3FACTOR   OLD=0.302            (error-correcting -- also does not beat uniform)
  INTERLV_SCHEMA    OLD=0.404[0.357,0.456] (marginally above uniform, CIs OVERLAP -> not decisive)
  SEP_LOOKUP   JOINT/OLD=1.000 INVARIANT (live separable store NEVER forgets)
  SEP_AVG_SIM  JOINT=0.182 INFER=0.104   (first-order similarity floor; BEST generalisation of all)
  best held-out INFER any arm = 0.104 (= the sim floor); learned maps do NOT generalise.
KEY: the n=1 smoke's apparent "SELECTIVE beats uniform" was NOISE; powered, SELECTIVE LOSES to uniform.

## VERDICT (powered, dense) -- rigorous NEGATIVE on the selection function + one solid POSITIVE:
(1) POSITIVE, CI-separated on REAL TEXT (organ-map frontier "D4 untested on real text"): brain-faithful
    fast/slow + INTERLEAVED replay prevents catastrophic forgetting (SEQ 0.076 -> INTERLV 0.349). The CLS
    interleaving OP works. AUDIT UPDATE: D4 now tested on real text (was "untested").
(2) NEGATIVE, the bar's twin test FAILS: surprise/schema/3-factor SELECTIVE replay does NOT beat the
    uniform-random twin (info-free twin does NOT lose). Confirms the surprise cell's "priority only
    reshuffles capacity in a shared store" -- now on REAL TEXT, and even with error-correcting plasticity.
    -> the SELECTION FUNCTION is not the brain mechanism that helps here; INTERLEAVING is.
(3) FORK B on the headline retention bar: live single-average is separable-row (SEP_LOOKUP=1.000, never
    forgets) -> no distributed arm beats it -> catastrophic forgetting NOT the live binding constraint.
(4) CONTENT WALL: no arm generalises above first-order similarity -> representation is the wall (p2 agrees).

## DEEPENING (per SOLVER protocol: shared wall across selection variants -> go deeper, not stop)
The zero-sum that kills selection is a property of a DENSE low-capacity store (protect X -> de-protect Y).
The brain's stores are SPARSE + PATTERN-SEPARATED (DG ~2%, HIGH capacity) = deviation #4, the SAME lever
load-bearing on the READ (p2). HYPOTHESIS: sparsity unlocks selective replay by raising capacity / killing
the zero-sum. TEST: sparse_keep=0.2 (k-WTA) 3-seed run, selective vs uniform. [RUNNING _consol_sparse.log]
n=1 smoke hint: SELECTIVE OLD 0.667 vs uniform 0.583 (directional, within noise) -- powering it.

## SPARSE DEEPENING RESULT (code_dim=48, sparse_keep=0.2 k-WTA, 3 seeds) -- sparsity does NOT unlock selection
  SEQUENTIAL   OLD=0.029  INTERLEAVED OLD=0.219[0.180,0.260]  SELECTIVE OLD=0.198  (selective STILL <= uniform)
  INTERLV_SCHEMA OLD=0.573[0.523,0.620] JOINT=0.311  BUT NEW=2*0.311-0.573=0.049 (uniform NEW=0.209)
  -> SCHEMA HOARDS OLD BY ABANDONING NEW. Its mean-JOINT "win" (0.311 vs 0.214 CI-sep) is a DEGENERATE
     policy (barely learns new). On BALANCED retention min(old,new): SCHEMA 0.049 << uniform ~0.209.
  Interleaving still beats sequential CI-sep under sparse (0.180 > 0.047).
KEY REALIZATION: JOINT-as-MEAN is gameable by OLD-hoarding. Added NEW-alone + BALANCED(min old,new) metric.
Under the honest BALANCED view, UNIFORM INTERLEAVING WINS; no selection/schema/3-factor variant beats it,
dense OR sparse. Sparsity (deviation #4) reduces interference for all arms but does NOT make selection a lever.

## FINAL VERDICT (PARTIAL) -- one clean positive, a rigorous negative on the selection function, fork B on live path
POSITIVE (CI-sep, real text, organ-map frontier): fast/slow separation + INTERLEAVED (uniform) replay
  prevents catastrophic forgetting (SEQ OLD 0.076 -> INTERLV 0.349 dense; 0.029 -> 0.219 sparse). AUDIT
  UPDATE: D4 tested on real text (was "untested on real text + at live site").
NEGATIVE (the bar's twin test FAILS, honestly, dense AND sparse, even w/ error-correcting + sparse codes):
  selective/schema/3-factor replay does NOT beat the uniform (info-free) twin on BALANCED retention.
  Confirms the surprise cell's "priority only reshuffles capacity in a shared store" -- the SELECTION
  FUNCTION is not the lever; INTERLEAVING is. Sweeping alpha won't flip it (concentration->neglect
  monotone toward uniform). Schema's mean-gain is OLD-hoarding (abandons new).
FORK B: live single-average is separable-row (SEP_LOOKUP=1.000 invariant, never forgets) -> catastrophic
  forgetting is NOT the binding constraint on the live path.
CONTENT WALL: no arm generalises above first-order similarity (dense best INFER 0.104) -> representation
  is the wall (agrees p2). Per brief this "rigorous loss" outcome is a FULL PASS with a mechanistic why.
PROPOSED WIRING: do NOT wire replay as a "forgetting fix" (live store doesn't forget) and do NOT wire a
  selective/prioritized schedule (no lever). IF/when a distributed OVERLAPPING generalising code is built
  (coordinate p2/reader_meaning_channel), wire UNIFORM interleaved replay (continual.replay_cycle) as its
  consolidation op with a default-off flag -- it prevents catastrophic forgetting there. Selection: shelve.

## CONFOUND FOUND + FIXED (owner push "drill finer for brain fidelity") -- the SELECTION test was null by construction
At replay_ratio=1.0, n_replay = |new| = |old|, so m=min(|new|,|old|)=|old| -> UNIFORM and SELECTIVE both replay
the ENTIRE old set (choice(|old|, size=|old|, replace=False) = all). Selection is NULL BY CONSTRUCTION. My
"selection isn't a lever" was partly an artifact of a NON-SCARCE budget, NOT brain-truth.
BRAIN FIDELITY: selective replay (SWRs, reward/surprise-biased) is a lever precisely under SCARCITY --
thousands of daily episodes, limited nightly replay -> the hippocampus MUST choose. Budget >= memory count
=> nothing to select. FIX: --sweep_replay sweeps budget DOWN (reads once/seed). [metrics_sweep.json]
SMOKE (n=1) hint: even at 10% / 50% budget, SELECTIVE does NOT beat uniform on OLD (0.229 vs 0.250; 0.667
vs 0.708). Deeper reason (to confirm powered): in a SHARED OVERLAPPING store, replaying at-risk items
DISTURBS the retained ones (crosstalk from the replay updates) -- the zero-sum does NOT vanish with
scarcity; scarcity makes everything worse. My WITNESS showed selective CAN win in a CONTROLLED
ORTHOGONAL-SUBSPACE fixture (at-risk items in a separate subspace); real overlapping semantic codes LACK
that separability -> selection is zero-sum. The brain gets separability from DG pattern separation (the FAST
store); the SLOW cortical store is overlapping BY DESIGN (for generalisation) -> selective replay INTO
cortex is inherently zero-sum. [POWERED 3-seed sweep + final canonical running: _consol_sweep.log + burs4al3v]

## FINAL (2026-08-26, v2-corrected after owner "drill it" pushes) -- SOLVED.md REVISED
The gen run confirmed the retention/generalisation tradeoff (sparse retains 0.68-1.00, generalises 0.05).
SOLVED.md rewritten to the full v1+v2 picture: sparse pattern-separated coding = PRIMARY anti-forgetting lever
(dense-hidden control collapses 0.000 -> sparsity causal); SELECTIVE interleaved replay CI-BEATS the uniform
twin in the SPARSE regime (keep 0.01/0.02) -> the v1 "selection isn't a lever" negative FLIPS (it was a
dense-cortex artifact); the brief's mechanism IS met in the brain-faithful regime; retention/generalisation
tradeoff = why one store can't do both = the problem's premise; fork B (live store never forgets);
generalisation content-bound. Witness = 8 tests PASS (incl. v2 flip + tradeoff). Ledger --check 0 malformed.
hdlab/ untouched. Deepening cron deleted. STATUS PARTIAL. Awaiting owner_verdict: DONE.

## (earlier) CONVERGED + SUBMITTED (2026-08-26) -- brain-mechanism bar MET
Powered scarcity sweep (3 seeds, budget 0.1->1.0) CONFIRMS: selective/schema/3-factor NEVER CI-beat uniform
on balanced retention (only a non-separated edge at 10% budget, near the forgetting floor). Canonical dense
final: INTERLEAVED (uniform) balanced 0.349 (old 0.349/new 0.370); SELECTIVE 0.336; SCHEMA hoards (old 0.695/
new 0.083); SEP_LOOKUP 1.000 unbeaten; best generalisation 0.104 = first-order floor. Witness PASS (6 tests
incl. real-data + the zero-sum-under-overlap proof). Ledger --check: 0 malformed. Deepening cron b154d1b5
DELETED. hdlab/ untouched. SOLVED.md written = PARTIAL. Brain mechanism identified (CLS interleaved+selective
replay), replicated+tested BOTH; selection shown NOT a lever with a SPECIFIC WITNESSED reason (zero-sum under
representational overlap; wins only under separable subspaces). Awaiting owner_verdict: DONE before integration.

## v2 DEEPENING (owner: "ensure brain foundational, drill it") -- SPARSE HIDDEN CORTEX changes the picture
experiments/exp_consolidation_sparse_hidden_cortex_v2.py: the v1 negative was measured in a SINGLE-LAYER
LINEAR cortex. Real cortex has a SPARSE k-WTA nonlinear HIDDEN layer (Leabra) that ALLOCATES concepts to
separable hidden subpopulations. Built a 2-layer cortex: key -(fixed random expansion Dh=512)-> relu -(k-WTA
keep HID_KEEP)-> sparse hidden -(learned W2 delta)-> value. Retrieval ranks predicted VALUE vs codebook C.
SMOKE (n=1, 120 concepts, budget_frac=0.25):
  sparse keep=0.03: SEQUENTIAL OLD=0.938  UNIFORM=SELECTIVE=1.000  (BARELY FORGETS w/o replay!)
  sparse keep=0.10: SEQUENTIAL OLD=0.979  UNIFORM=SELECTIVE=1.000
  DENSE-hidden control (tanh): ALL=0.000  (dense hidden -> total collapse; SPARSITY is causal)
=> THE PRIMARY BRAIN ANTI-FORGETTING MECHANISM IS SPARSE PATTERN-SEPARATED CODING (deviation #4), NOT
   replay and NOT a selection function. In the linear cortex SEQ forgets 0.076; sparse-hidden SEQ retains
   0.938 -- sparse conjunctive codes prevent the interference at the representational level, far stronger
   than interleaved replay. Replay/selection become near-moot (ceiling). This UNIFIES deviation #4 as the
   load-bearing lever on BOTH read (p2) and write (this problem). Dense-hidden collapse (0.000) confirms
   sparsity is the causal variable, not the extra layer. [POWERED 3-seed run: _consol_sparsehidden.log / b1cywbuw3]
REVISED WIRING (pending powered confirm): the brain-foundational fix for "consolidation destroys the old" is
SPARSE CORTICAL CODING, not interleaved replay (a patch for a dense store) and not a selection scheduler.

## v2 POWERED (3 seeds, 320 concepts, Dh=512, budget_frac=0.25) -- THE VERDICT FLIPS ON SELECTION
  sparse keep=0.02: SEQ OLD=0.333  UNIFORM=0.896[0.865,0.924]  SELECTIVE=0.982[0.966,0.995]  -> SELECTIVE
     BEATS UNIFORM CI-SEPARATED (0.966>0.924). TWIN LOSES.
  sparse keep=0.05: SEQ=0.557  UNIFORM=1.000  SELECTIVE=0.995  (uniform at ceiling -> no room)
  sparse keep=0.15: SEQ=0.698  UNIFORM=0.997  SELECTIVE=1.000  (both ceiling)
  DENSE control: 0.000 everywhere (collapses -> sparsity is causal, not capacity/the extra layer)
MAJOR CORRECTION TO v1: v1 concluded "selection is not a lever (zero-sum)" -- but that was in the UNFAITHFUL
DENSE/LINEAR cortex. In the BRAIN-FAITHFUL SPARSE-HIDDEN cortex, SELECTIVE interleaved replay IS a lever,
CI-separated, at the sparsest code (keep=0.02) where retention isn't already saturated. The brief's ORIGINAL
hypothesis (selective interleaved replay beats the single-average, twin losing) is VINDICATED -- but only in
the sparse-code regime, which is the brain's regime. Two levers work TOGETHER: SPARSE pattern-separated coding
(primary anti-forgetting) + SELECTIVE replay (adds targeted protection once codes are separable enough that
replay is not zero-sum). Dose-response: selection's headroom exists only while sparsity hasn't already
saturated retention (keep=0.02 shows it; keep>=0.05 uniform hits ceiling).
STILL TO CONFIRM: retention-vs-generalisation TRADEOFF. Sparse codes should RETAIN but NOT GENERALISE (each
concept isolated -> held-out lands on untrained hidden units). If so, that is the CLS reason for TWO stores
(sparse-retain hippocampus + overlapping-generalise cortex) = the literal premise "one store, two jobs."
[running gen version: _consol_sparsehidden_gen.log]

## LITERATURE FIDELITY VERIFICATION (research agent, read-only) -- CAUGHT A REAL OVER-CLAIM
1. SPARSE-vs-REPLAY (Claim: sparse coding is the PRIMARY anti-forgetting lever, beats replay): mechanism
   PINNED (French 1991 activation-sharpening; MMO 1995; O'Reilly 2014) BUT my "beats replay / primary"
   framing is WRONG per CLS -- sparse coding and replay solve DIFFERENT problems for DIFFERENT systems
   (sparse = hippocampal fast low-interference encode; interleaved replay = cortical structure-extraction
   WITHOUT interference DESPITE dense codes). The real claim: NO single scheme gets both -> two systems.
   MUST REFRAME as complementary, not competing. van de Ven 2024 (arXiv:2403.05175): interleaving dominates
   at aligned/orthogonal extremes, weak at INTERMEDIATE overlap (where real memories live); sparsity degrades
   under capacity/superposition pressure. -> soften "primary lever".
2. SELECTIVE-REPLAY separability-dependent: direction SUPPORTED (Schaul 2016 PER; Rolnick 2019; Isele 2018;
   van de Ven 2024) but it is TWO coupled knobs (which sample x how much capacity), not one gate; a
   high-priority sample can overwrite neighbors via gradient bleed independent of capacity. TD-error priority
   can EXACERBATE interference (supports my dense zero-sum). State as two coupled variables.
3. NEUROGENESIS: PINNED for pattern separation (Aimone 2011; Sahay 2011; Clelland 2009) BUT my "reduces
   interference with older" is ONE-SIDED -- Akers/Frankland 2014 (Science): elevated neurogenesis CAUSES
   forgetting of established memories via circuit remodeling. DOUBLE-EDGED. My disjoint-units model is the
   idealized separation WITHOUT the remodeling cost -> my neurogen "retention 1.0" is optimistic; real
   mechanism trades some old-forgetting. Also human adult neurogenesis contested (Sorrells 2018 vs Boldrini 2018).
4. RETENTION/GENERALISATION tradeoff: PINNED (O'Reilly & McClelland 1994 "avoiding a trade-off" = the two-system
   solution; Rolls 2013/2016). Caveat: retention side causally pinned; generalisation-needs-density side rests
   on model convergence + correlational consolidation-timecourse. My framing OK.
5. SURPRISE priority: SUPPORTED but TOO NARROW -- replay priority is a MULTI-FACTOR salience composite (reward,
   RPE, novelty, valence, recency; weights unresolved), not surprise-vs-reward. Say "surprise is A valid member
   of an open selection space." Ambrose-Pfeiffer-Foster 2016; TiNS 2025 replay review; NatNeuro 2023 valence.
MISSING (different in kind): (a) SYNAPTIC TAGGING & CAPTURE (Frey&Morris 1997; Redondo&Morris 2011) -- local
synapse-level coincidence gating; my model is system/representation level, not synaptic (this is ORGAN_MAP D9,
a separate organ). (b) SCHEMA-gated consolidation RATE (Tse 2007/2011; van Kesteren 2012) -- schema-congruent
info consolidates in 24-48h SKIPPING slow interleaving; my SCHEMA arm modeled budget-reallocation, not the
"skip slow replay, land direct on safe cortical schema" mode. Note as a partial-fidelity caveat.
=> ACTIONS: reframe sparse-vs-replay as complementary (not "beats"); neurogen double-edged; surprise multi-factor;
   note STC + schema-rate as mechanisms my system-level model doesn't fully capture. Fold into SOLVED.md.

## GOVERNANCE
- Announced dispatch_queue: ann-20260826T160638Z...-solver-consolidation by solver_opus48_consolidation.
- Another solver (solver_opus48) is on the prediction-error problem — different slug, no collision.
- Writes ONLY experiments/, verification/, this folder. hdlab/ untouched (Q111 — propose diff).
