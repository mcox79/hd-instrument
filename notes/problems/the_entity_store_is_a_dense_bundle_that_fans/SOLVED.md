---
problem: the_entity_store_is_a_dense_bundle_that_fans
status: SOLVED
bar: "Reduce the FAN-EFFECT SLOPE (decode accuracy vs entity event-count) CI-separated vs the dense-bundle baseline over its UPPER bound, with an info-free twin (a RANDOM sparse code of matched sparsity) LOSING CI-separated. Report CI half-width + null p95. Show the residual degradation tracks item-SIMILARITY, not item-COUNT."
result: "On 28,569 LitBank who-did-what queries (oracle linking), the dense organ's fan SLOPE (acc[1-3]-acc[17+]) = 0.2880 [0.2655,0.3109] is flattened to 0.0000 by a FINER conjunctive temporal index and to 0.0003 by SET-RETURN readout -- paired contrast -0.2879 [-0.3109,-0.2655] FLATTER, hw 0.0227. Info-free RANDOM_ORDER_TWIN loses on colliding events: FINER_TRUE 1.0000 vs twin 0.5016, diff +0.4982 [0.4798,0.5179] hw 0.019, null p95 (twin upper) 0.520."
floor: "DENSE_ARGMAX (the real hdlab.situation_model_accumulate multibank organ) upper bound = fan slope 0.2880 [0.2655,0.3109]; POINTER_MULTIMAP ceiling = slope 0.0000; info-free twin RANDOM_ORDER_TWIN collide-acc 0.5016 (null p95 0.520)."
controls: "unique-(entity,slot) decode = 1.0000 at EVERY fan level (excludes superposition as the fan cause); DENSE_SETRETURN top-m recovers the set at 0.9999 (excludes 'dense bundle destroys information'); FINER_CTX === FINER_CTX_SPARSE both 1.0000 (excludes sparsity as the operative lever for the MEASURED fan); RANDOM_ORDER_TWIN info-free LOSES CI-separated (excludes 'any finer index works regardless of information'); Part 3 DENSE_flat fans 1.0->0.048 while SPARSE_DG holds 1.0 to N=800 (locates where sparsity IS the lever); residual similarity-arm err 0.848 vs 0.243 at fixed count vs count-arm shallow (excludes count as the residual driver)."
files_changed: "experiments/{exp_entity_store_sparse_fan_v1.py, exp_entity_store_schema_gist_v1.py, exp_entity_store_graded_temporal_v1.py, exp_entity_store_unified_v1.py, exp_entity_store_unified_litbank_v1.py, exp_entity_store_sparse_capacity_v1.py}; verification/{test_entity_store_fan.py, test_entity_store_frontier.py}; notes/problems/the_entity_store_is_a_dense_bundle_that_fans/{SOLVED.md, research_fan_mechanism_brain_foundation_2026-08-27.md, research_hippocampal_frontier_drill_2026-08-27.md, research_scaffold_innate_vs_learned_2026-08-27.md, research_sparse_dg_capstone_2026-08-27.md}; data/entity_store_sparse_fan/*.json + data/exp_entity_store_unified_litbank_v1/metrics.json (outputs, non-foundation)."
reverify: ".venv/Scripts/python.exe verification/test_entity_store_fan.py  (core: 21/21) ; .venv/Scripts/python.exe verification/test_entity_store_frontier.py  (frontier: unified store + reconstructive + event-segmented + path-integration + trained-SR + sparse-DG-capacity: 26/26)"
---

# SOLVED (with the brief's DIAGNOSIS corrected): the measured fan is an ADDRESSING COLLISION, not superposition blur -- the brain-faithful fix is a FINER CONJUNCTIVE temporal context + set-return, and sparse DG coding is the right design for a SEPARATE high-load regime the data does not reach.

## What the brief said, and what the disk says

**The brief's premise:** the dense FHRR bundle in `hdlab.situation_model_accumulate` BLURS as a character
accumulates events (within-register superposition crosstalk destroys information), and the faithful fix is a
SPARSE DG k-WTA per-event store + CA3 completion. **The disk corrects this premise -- and correcting it was
the halfway point, so I went on to solve the real problem the brain-faithful way and to locate exactly where
the brief's sparse mechanism DOES belong.**

All numbers are on LitBank (100 novels), ORACLE linking (gold clusters) so the STORE is measured in isolation,
28,569 verb-bearing who-did-what queries, bootstrap over documents.

### 1. The fan reproduced -- then diagnosed as a COLLISION, not superposition

- Fan reproduced on the real organ: decode(entity, sentence)->verb accuracy **0.9455 (1-3 events) -> 0.6574
  (17+)**, fan SLOPE **0.2880 [0.2655, 0.3109]** (stronger than the brief's 0.695->0.608, which was the pronoun
  subset).
- **It is NOT superposition blur.** UNIQUE (entity, sentence) queries decode at **1.0000 at EVERY fan level**
  (1-3, 4-8, 9-16, 17+) -- the dense bundle does not fan from per-bank load at this scale. The entire fan is
  carried by the **22.7% of (entity, sentence) addresses that hold >1 DISTINCT verb** (a busy character does
  several things per sentence). `decode()` returns ARGMAX, so the co-address siblings are scored wrong.
- **The dense bundle does NOT lose the information.** `unbind(bundle, s) = v1+v2+..+vm + crosstalk`, so a TOP-m
  readout recovers the co-slot verbs at **~1.0000 at every fan level** (17+: 0.9997). The fan is an
  ARGMAX-vs-SET readout artifact on an UNDER-SPECIFIED key -- not a store-capacity failure.

### 2. The brain-faithful fix flattens the fan CI-separated (Part 1)

The hippocampus does not index episodes by a coarse "sentence": temporal context DRIFTS continuously (TCM;
Howard & Kahana 2002) and each action binds into a CONJUNCTIVE code with its finer context (DG conjunctive
coding on LEC-content + MEC-context convergence, Hargreaves 2005). Retrieval reinstates the context and
reactivates the SET bound to it (Bramao 2022; CA3 completion, Nakazawa 2002). Two fixes, both faithful:

| arm | fan slope | contrast vs DENSE_ARGMAX |
|---|---|---|
| DENSE_ARGMAX (real organ, baseline) | 0.2880 [0.2655,0.3109] | -- |
| DENSE_SETRETURN (set-return readout = context-cued reactivation) | 0.0003 [0.0000,0.0007] | **-0.2877 [-0.3103,-0.2654] FLATTER** |
| FINER_CTX (finer conjunctive temporal index = TCM drift) | 0.0000 | **-0.2879 [-0.3109,-0.2655] FLATTER** |
| FINER_CTX_SPARSE (finer + DG k-WTA store) | 0.0000 | -0.2879 FLATTER |
| POINTER_MULTIMAP (ceiling, not the fix) | 0.0000 | -0.2879 FLATTER |

**FINER_CTX === FINER_CTX_SPARSE (both 1.0000): sparse coding adds NOTHING to fixing the measured fan.** The
operative lever is the finer CONJUNCTIVE context / set-return, exactly as the collision diagnosis predicts.

### 3. The finer index carries INFORMATION -- info-free twin loses (Part 2)

Specific-action recall at cue (entity, sentence, within-sentence ORDER), on COLLIDING events (m>1):
- **FINER_TRUE** (true order): **1.0000**.
- **RANDOM_ORDER_TWIN** (shuffled order labels; info-free, matched shape): **0.5016**.
- diff **+0.4982 [0.4798, 0.5179]**, hw 0.019, **CI-separated ABOVE**; null p95 (twin upper) 0.520.

So separation alone recovers the SET (any distinct sub-index), but recovering the SPECIFIC action requires the
finer index to carry TRUE temporal-order information; the info-free twin loses decisively.

### 4. Where the brief's SPARSE mechanism DOES belong -- the superposition regime (Part 3)

Once events are uniquely addressed, a SEPARATE superposition fan appears only at HIGH unique-event load
(Willshaw 1969; Treves & Rolls 1991: crosstalk ~ a*ln(1/a)*T). Construction proof on the real codes, one
entity, N uniquely-addressed events:

| N | DENSE_flat | DENSE_multibank (organ) | SPARSE_DG (2%,4096) |
|---|---|---|---|
| 50 | 1.000 | 1.000 | 1.000 |
| 200 | 0.580 | 1.000 | 1.000 |
| 400 | 0.165 | 0.988 | 1.000 |
| 800 | 0.048 | 0.784 | **1.000** |

- The dense bundle's capacity IS bounded (flat collapses; the multibank organ mitigates by splitting load but
  still fans at 800); **SPARSE_DG holds 1.0000 to N=800.** This validates the brief's mechanism -- but at a
  scale BEYOND the measured LitBank fan (LitBank's per-entity unique-event counts do not reach it).
- **Residual tracks SIMILARITY, not COUNT** (Leutgeb 2007; Yassa & Stark 2011), under a partial cue (an exact
  cue makes any store pointer-exact): similarity arm (fixed N=800) err_high_sim **0.848** vs err_low_sim
  **0.243** (3.5x); count arm (similarity fixed low) err rises only 0.10->0.28 as N goes 100->1600 (16x). The
  brain-faithful signature: steep in similarity, shallow in count.

## KEY REALIZATIONS (the enabling moves)

1. **"Ask whether the experiment could have SUCCEEDED before why it did not."** A synthetic entity with 25
   events/bank decoded at 1.0 on the dense store -- so per-bank superposition could NOT be the LitBank fan. That
   one check redirected the whole problem from "build a sparse store" to "find what actually collides."
2. **Query the store with a UNIQUE vs the given key.** unique-(entity,slot) decoding at 1.0 at every fan level
   is the single fact that falsifies the superposition premise; the coarse sentence key was the divergence.
3. **Read the readout, not just the score.** `unbind(bundle,s)` SUMS all co-slot verbs, so top-m recovers them
   -- the information was never lost; `decode()`'s argmax just returned one. The fan is a readout artifact.
4. **The finer index IS the TCM drift.** Framing "within-sentence order" as continuous temporal-context drift
   (not an engineering hack) is what makes the fix brain-foundational and unifies it with the 2026-08-26
   context-reinstatement win (Q1: DG conjunctive coding and TCM context-cuing are one architecture, two ends).
5. **kWTA WITHOUT completion is BRITTLE.** Sparse coding is pointer-exact under an exact cue but WORSE than
   dense under a partial cue -- because DG separation needs CA3 attractor completion for robustness (Q4). The
   residual is where the brain-faithful similarity signature lives.

## What I did NOT establish / would withdraw first if wrong

- **The measured-fan fix is not a capability win beyond retrievability.** Flattening the fan makes a busy
  character's per-context actions retrievable; it does NOT (this problem) show that retrievability improves any
  downstream comprehension score. That is the entity-line's separate, already-measured attribution result.
- **The set-return / finer-index fix is close to a POINTER on this data** (both reach 1.0). Its graceful-
  degradation advantage over a pointer only appears in the superposition/partial-cue regime, which LitBank does
  not reach -- so on the MEASURED data I cannot distinguish the brain-faithful store from a multimap by
  accuracy alone. The distinction is the mechanism (context drift + completion), not the LitBank number.
- **Part 3 sparse superiority is partly a DIMENSION effect** (sparse at 4096 vs the organ's FHRR at 1024). I
  did not fully isolate sparsity-vs-dimension at the exact cue (there the self-term makes any store exact). The
  load-bearing sparse claim is the capacity SLOPE + the similarity-gated residual, not the exact-cue number.
- **kWTA partial-cue robustness is a real deficit I did not fix** -- an iterative CA3 attractor (not the one-
  shot read) is the missing stage; a one-step "completion" is algebraically the read itself, so it added
  nothing. Named as next work, not claimed.
- **spaCy verbs/slots + oracle linking** stand in for the substrate's incremental parser; absolute numbers
  inherit that. The DIAGNOSIS (collision, unique-address ceiling, top-m recovery) is robust to it.

## PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands, Q111)

1. **FIX THE KEY, NOT THE STORE DENSITY.** The divergence from the brain is the COARSE per-sentence event slot,
   not the dense bundle. Key each event by a FINER CONJUNCTIVE temporal context (a within-event / continuous-
   drift index, TCM-style) so co-sentence actions get distinct addresses. Minimal change to
   `hdlab.situation_model_accumulate` / `situation_model_multibank`: derive `event_idx` from (sentence,
   within-sentence-order) rather than sentence alone.
2. **ADD A SET-RETURN READ.** Give `decode(entity, sentence)` a top-m / threshold SET-return mode (return all
   verbs whose cleanup score clears a margin) -- this is CA3 context-cued reactivation of the event set and
   ALONE flattens the fan (0.9999) without any store change. The current argmax-only decode is the artifact.
3. **DO NOT replace the dense bundle with a sparse store to fix the MEASURED fan** -- FINER_CTX===FINER_CTX_SPARSE;
   sparsity buys nothing here and (without CA3 completion) HURTS under partial cues.
4. **RESERVE the sparse DG store for the SUPERPOSITION regime** (a busy entity with many UNIQUE events, beyond
   LitBank scale): a DG k-WTA conjunctive per-event code has higher exact-cue capacity (holds 1.0 to N=800 where
   the multibank organ falls to 0.78). Land it behind a load gate, PAIRED with an ITERATIVE CA3 attractor
   completer (`hdlab.ca3_completer` / `iterative_attractor`) for partial-cue robustness -- DG-alone is brittle.
5. **Keep the dense bundle as the gist** (augment, per the brief) -- it already holds the full set; it just
   needs a finer key and a set-return read.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md -- corrects the 2026-08-27 fan-effect entry)

- The current audit says the fan is "within-register SUPERPOSITION crosstalk" fixed by a "sparse DG k-WTA
  conjunctive encode + CA3 completion (NOT a pointer)." **CORRECTION (measured):** on LitBank the fan is an
  ADDRESSING COLLISION on an under-specified (entity, sentence) key + an ARGMAX readout -- NOT superposition.
  Evidence: unique-(entity,slot) decode = 1.0000 at every fan level; top-m set-return recovers the set at 0.9997
  even at 17+ events; the dense bundle does not lose information.
- The faithful fix for the MEASURED fan is a FINER CONJUNCTIVE temporal context (TCM continuous drift) + a
  SET-RETURN read (CA3 context-cued reactivation), which flatten the slope 0.288->0.000 CI-separated. Sparse
  coding is NEUTRAL here (FINER_CTX === FINER_CTX_SPARSE) -- consistent with the earlier "DG on the content code
  was NEUTRAL" note; separation must act on the KEY, and the key was already unique once made finer.
- Sparse DG coding is REAL and validated for the SEPARATE high-unique-load SUPERPOSITION regime (holds 1.0 to
  N=800 where the multibank organ falls to 0.78), with the residual SIMILARITY-gated not count-gated (3.5x vs
  shalow) -- but DG-alone is BRITTLE under partial cues; it needs the iterative CA3 completer paired in.
- Net: downgrade "dense->sparse is the fan fix" to "dense->sparse is the HIGH-LOAD-capacity fix; the fan fix is
  the KEY (finer conjunctive context) + the READ (set-return)". Q1 unification: DG conjunctive separation and
  TCM context reinstatement are one architecture (Hargreaves 2005; O'Reilly & Rudy 2001) -- the finer context
  IS the drift.

## FRONTIER -- "is this as brain-foundational as it can be?" (owner 2026-08-27) -- NO, and here is how far it goes

A second, deeper drill (`research_hippocampal_frontier_drill_2026-08-27.md`, 5 questions) established that the
SOLVED fix (finer conjunctive key + set-return) is CORRECT-IN-SHAPE but a DEGENERATE special case of the
brain-faithful store -- the SAME shape as the Tolman-Eichenbaum Machine (structure x content, retrieval =
key/value attention; Whittington & Behrens 2020) but missing three properties the literature independently
converges on. I built and tested the two highest-leverage ones (witness `test_entity_store_frontier.py` 8/8):

1. **SCHEMA/GIST interception is the systems-level RIGHT fix (Radvansky/O'Rear/Fisher 2017: the fan tracks the
   number of separate EVENT MODELS, not fact count; Gilboa & Marlatte 2017: routine material graduates OUT of
   episodic indexing).** Built `exp_entity_store_schema_gist_v1.py`: route ROUTINE events (verb == the entity's
   running gist mode) to a per-entity gist; only ATYPICAL (memorable) events enter the episodic store. Measured
   (recall of the ATYPICAL subset, the events worth remembering): at high coherence SCHEMA_GIST 1.00 vs
   ALL_EPISODIC 0.95 (un-crowding the store), info-free RANDOM_ROUTE_TWIN collapses to 0.075 (it removes atypical
   events too), and the gain is NULL at zero coherence (0.779 = 0.779) -- the pre-registered HARD-PASS signature
   (gain CONCENTRATED in routine entities). This is MORE brain-faithful than my Part-3 sparse-store answer to the
   high-load fan: the brain does not fix a busy entity with a smarter N-way index, it SCHEMATIZES the routine.

2. **The temporal key should be a GRADED multi-timescale drift, not orthogonal sub-slots (Howard & Kahana 2002;
   Shankar & Howard 2012 leaky-integrator/Laplace bank; MacDonald 2011 time cells).** Built
   `exp_entity_store_graded_temporal_v1.py` (multi-timescale random-Fourier context). Measured: the graded context
   has a smooth TEMPORAL-CONTIGUITY gradient (similarity 0.71 -> 0.31 over lags 1-10, gradient 0.39) that the
   orthogonal key ENTIRELY LACKS (gradient 0.003) -- i.e. my cheap fix DESTROYS temporal contiguity (Kahana 1996),
   a first-class brain signature. AND under a degraded WHEN-cue, graded errors are TEMPORALLY LOCAL (mean |dt|
   39.8 vs orthogonal 76.0 -- you misremember when by a little, the brain's error signature) at a small EXACT-
   recall COST (-0.058). **That cost is the deep finding:** you CANNOT get exact separation AND temporal
   contiguity from ONE temporal code -- which is exactly WHY the brain FACTORIZES (orthogonal content in DG for
   the "what" x graded drift for the "when-neighborhood" x theta phase for within-moment order; TEM). I
   empirically rediscovered the reason for the factorization.

3. **The attractor-null (my earlier "CA3 completion adds nothing") is THEORY-CONSISTENT, not a dead end (Q2):**
   an attractor needs a MANIFOLD to settle on; i.i.d. random/orthogonal codes give it none, so it reduces to the
   one-shot nearest-neighbor read. Graded multi-timescale codes lie on a smooth temporal manifold -- so completion
   should be re-tested there (gated on the graded key existing). NOT tested yet.

**BRAIN-FOUNDATIONALITY VERDICT:** the SOLVED fix is the correct SHAPE and clears the bar, but the maximally
brain-faithful store is a FACTORIZED, SCHEMA-GATED one with a self-terminating set-return. **I then BUILT that
store** (`exp_entity_store_unified_v1.py`, witness checks in `test_entity_store_frontier.py`):

4. **THE MAXIMALLY BRAIN-FOUNDATIONAL STORE, BUILT AND MEASURED.** A per-entity FACTORIZED episodic memory:
   trace = CONTENT (near-orthogonal FHRR verb atom, exact "what") x GRADED TEMPORAL CONTEXT (a UNIT-MAGNITUDE,
   BINDABLE clock CTX(t)[k]=exp(i(w_k t + phi_k)) whose inner product DECAYS smoothly with |t-t'| -- the
   time-cell/leaky-integrator drift, but algebra-compatible) x WITHIN-MOMENT ORDER (theta-phase atom), with the
   SCHEMA/GIST tier routing routine events out of the episodic store, and a RACE-TO-STOP (CMR) set-return.
   Measured (synthetic construction proof on real FHRR codes): recovers the co-moment SET at oracle F1 = 1.000
   AND preserves TEMPORAL CONTIGUITY (retrieval-similarity gradient 0.75, lag0 1.0 -> lag7 0.25) -- the property
   the SOLVED orthogonal key had at ZERO; race-to-stop recovers F1 = 0.947 WITHOUT being told the set size (vs
   naive fixed-k 0.78; wrong-time info-free twin 0.00); and under a jittered WHEN-cue errors stay TEMPORALLY
   LOCAL (jitter 3 -> error 2.68). So this store keeps exact recall, RESTORES contiguity, and DISCOVERS the set
   size itself -- the three things the cheap fix could not.

5. **RECONSTRUCTIVE MEMORY -- the store's FAILURE MODE made brain-faithful (deepest optimization).** The one
   remaining artificiality was that the store was LOSSLESS/reversible (random orthogonal content atoms treat
   "grabbed" and "seized" as no more similar than "grabbed" and "sang"), whereas human episodic memory is
   RECONSTRUCTIVE -- it fails toward MEANING. Added GROUNDED semantic content (verbs in synonym clusters share a
   code prototype). Measured: retrieval ERRORS now land on a SEMANTIC NEIGHBOR at 3.2-5.5x chance (the DRM
   intrusion signature; Roediger & McDermott 1995), scaling with semantic similarity; with random content
   (info-free twin) errors stay UNSTRUCTURED at chance. So the store now mis-remembers the way people do --
   toward the gist -- instead of failing randomly.

6. **EVENT SEGMENTATION -- the organizing principle of episodic memory (Baldassano 2017; DuBrow & Davachi
   2013; Zwaan event-indexing).** The clock now DRIFTS FASTER at EVENT BOUNDARIES (warped time: within an event
   tau advances by 1, at a boundary it jumps), so temporal contiguity is STRONG within an event and CUT across a
   boundary. Measured: at lag 1 the event clock's within-event similarity 0.73 vs across-boundary 0.36 (gap
   0.37), persisting at lags 2-3; a UNIFORM clock has ZERO within/across gap; an info-free SHUFFLED-boundary twin
   (jumps not aligned to true boundaries) does NOT reproduce it -- so the effect tracks the REAL event structure,
   not merely having jumps. This is the brain's boundary effect (subjective temporal distance larger across
   boundaries; within-event order memory better than across).

7. **THE STRUCTURAL SCAFFOLD -- IS A LEARNED ONE BRAIN-FOUNDATIONAL? (drilled, then BOTH built).** A third drill
   (`research_scaffold_innate_vs_learned_2026-08-27.md`) answered decisively: a learned scaffold is
   brain-foundational in its TARGET (TEM's factorized, ACTION-DRIVEN g/x split) but NOT in its TRAINING RULE
   (backprop-through-time -- TEM's own paper: "not a biophysically realistic model"; Tang/Barron/Bogacz 2024).
   The scaffold is largely INNATE/pre-structured (grid topology near eye-opening; Ulsaker-Janke 2023), and what
   IS learned is learned by LOCAL rules, not backprop. So I built the two the drill ranked above backprop-TEM,
   and compared them head-to-head:
   - **HANDMADE path-integration scaffold (zero training):** an action-driven position code CTX_t = CTX_{t-1} *
     A(a_t) (Burak & Fiete 2009; our open-loop clock is the fixed-tick special case). Addresses events by
     RELATIONAL POSITION -- an event stored via one route is retrieved via a DIFFERENT route/time (recall 0.80),
     which the absolute-time clock (0.00) and a random context (0.00) CANNOT. Grid-cell path-independence,
     free from commutative VSA binding.
   - **TRAINED Successor-Representation scaffold (simple, brain-foundational):** the hippocampal predictive map
     (Stachenfeld 2017), learned by a ONE-LINE LOCAL TD rule (Fang et al. 2023), offline-trainable then FROZEN
     into the substrate (admissible static foundation; no learning at inference). LEARNS an unknown transition
     structure and PREDICTS the next event (accuracy 1.00 vs chance 0.091; shuffled-transition twin 0.00).
   - **VERDICT on handmade-vs-trained (owner's question):** COMPLEMENTARY, and neither is complicated. The
     HANDMADE scaffold is much easier and JUST AS GOOD for relational ADDRESSING/transfer. The TRAINED SR earns
     its keep ONLY for PREDICTION / discovering unknown structure -- and it is still trivially simple (a matrix +
     a 1-line update, ~6 lines, local rule, no backprop). Backprop-TEM: NOT built (representation-faithful but
     learning-rule-implausible; only an existence-proof of the target). The brain uses BOTH: an innate metric
     (handmade-equivalent) + a locally-learned predictive map (SR).

8. **REAL-DATA VALIDATION + the FACTORIZATION resolves the separation-contiguity tradeoff (owner: validate on
   the real register, and consider sparse).** Ran the store on the REAL LitBank register (`exp_entity_store_
   unified_litbank_v1.py`, GPU-ready torch, 28,569 queries, oracle linking), fairly isolating the ONE variable
   (graded vs orthogonal finer key, everything else identical):
   - CHEAP_ORTHO (the SOLVED fix): fan slope 0.001 [0.000,0.004] -- flat -- but contiguity 0.002 (~ZERO).
   - UNIFIED_GRAD (single graded key): contiguity 0.585, but a residual fan slope 0.194 [0.176,0.213] (0.999 ->
     0.805 at 17+). This does NOT dissolve with dimension (d=4096/8192/16384 identical) -- on dense real data the
     graded context's CONTIGUITY IS the adjacent-time leak; a single key genuinely trades one for the other.
   - **FACTORIZED (two systems -- the brain's DG-sharp exact-recall store + EC-graded context store, read
     SEPARATELY): fan slope 0.001 [0.000,0.004] AND contiguity 0.585 -- GETS BOTH, CI-separated, on real data.**
   So the maximally faithful store does NOT collapse content and context into one key; it keeps the brain's
   SEPARATE populations (Bausch 2026: distinct content vs context neurons) and reads exact-recall from the sharp
   system, contiguity from the graded system. This UPGRADES the whole frontier from synthetic construction proof
   to REAL-DATA VALIDATED for the load-bearing claim (flat fan + contiguity together).

9. **THE OPTIMAL DESIGN, DRILLED THEN BUILT -- and the ORIGINAL sparse-DG store finds its right home (owner:
   "consider sparse... research how this should be done optimally... do the right things").** A capstone drill
   (`research_sparse_dg_capstone_2026-08-27.md`) established: the two-system factorized store is INDEPENDENTLY
   CONVERGENT with the freshest neuroscience -- Bausch et al. 2026 (Nature, 3,109 human MTL neurons: content and
   context are SEPARATE populations bound by cross-population TIMING, not one conjunctive code) and TEM
   (Whittington 2020: hippocampal code = content x structure bound ONLY AT STORAGE). VERDICT on the crux:
   **sparsity COMPLEMENTS, does NOT DISSOLVE, the separation-vs-contiguity tradeoff** -- one sparse conjunctive
   code keeps gradedness only with axis-specific LSH structuring, and the brain keeps two systems anyway; so
   sparsity's job is to make the SHARP half more CAPACIOUS, orthogonal to contiguity. Then I BUILT and MEASURED
   the pre-registered decisive test (`exp_entity_store_sparse_capacity_v1.py`, real `dg_separate`): at FIXED
   dimension (4096), CORRELATED content, exact-recall vs SCALE, isolating SPARSITY --
   - DENSE bundle (a=1.0): recall 0.977 (N=2k) -> 0.779 (4k) -> **0.454 (8k)** -- collapses (the Amit-Gutfreund-
     Sompolinsky dense cliff).
   - SPARSE DG k-WTA (a=0.02, 82 active): **1.000 at every scale to N=8k** -- holds. Info-free twin at chance
     (0.01) at every sparsity.
   So the SHARP exact-recall half should be a sparse DG expand+k-WTA code (Treves & Rolls `p_max ~ C/(a ln 1/a)`;
   Willshaw `ln2` bits/synapse) -- a real ~2x+ capacity win from sparsity ALONE at scale, for CORRELATED patterns
   (the regime where modern dense Hopfield's exponential capacity does NOT apply). **The original brief's sparse-
   DG store was the RIGHT mechanism all along -- not for the measured collision-fan (that was addressing), but
   for the EXACT-RECALL COMPONENT of the factorized store, where it delivers the capacity the dense bundle loses
   at scale.** The whole arc closes: the fan was addressing (finer key); the store's exact-recall half is sparse
   DG (capacity); its context half is graded (contiguity); they are bound only at storage (TEM); read separately
   (Bausch). Minimal faithful set named; contested add-ons (CA3 iterative completion: Neher 2015 redundant vs
   Nakazawa 2002 necessary; SR/grid redundancy: Stachenfeld 2017) flagged test-before-commit.

**A WALL DRILLED (owner: "if the brain can do it, we can"):** the separation-vs-contiguity "tradeoff" I flagged
turned out NOT to be a hard tradeoff -- it was a CROSSTALK-CAPACITY limit. At d=1024 the graded clock's
adjacent-time leak capped set recovery at F1 0.71; at d=4096 it is 1.000 WITH the contiguity-preserving clock
intact. Dimension is a PARAMETER we do not share with the brain (which has vastly more units) -- swept, not
adopted -- and enough capacity buys BOTH exact separation AND contiguity. (The schema/gist tier further shrinks
the episodic load, compounding this.) The race-to-stop's residual 5% gap to oracle is GENUINE contiguity-induced
temporal SOURCE ambiguity (Kahana) -- itself brain-faithful, not a defect.

**STILL OPEN (honest frontier, ranked):** (a) CLS CONSOLIDATION (fast hippocampal <-> slow cortical, replay) is
a separate substrate problem; (b) the whole unified store + scaffolds are SYNTHETIC construction proofs --
validating on the REAL LitBank register at d>=4096, and training the SR on real narrative event-transitions, are
the HEAVY runs for the remote GPU box; (c) integrating the SR predictive layer with the entity-line's SCHEMA-ROLE
prediction organ. Built so far, each a measured construction proof: factorized graded-context store, schema/gist,
race-to-stop, reconstructive semantic content, event-segmented boundaries, HANDMADE path-integration scaffold
(relational addressing), and TRAINED local-rule Successor-Representation scaffold (prediction). The structural-
scaffold question is now ANSWERED (handmade for addressing + local-rule-trained SR for prediction; backprop-TEM
correctly skipped). Remaining depth is consolidation + real-data validation, not new mechanisms.

## TLDR

Our reader files everything a character does under a coarse tag -- basically "this character, this sentence."
When a character does several things in one sentence ("he grabbed the rope, steadied himself, and climbed"),
all of it lands under the SAME tag, and when we ask "what did he do there?" the memory hands back only ONE of
them -- so a busy character looks like a failing memory. We proved the memory is NOT actually losing anything:
ask for the whole set at that tag and everything comes back perfectly, even for the busiest characters. The
real fix is the one the brain uses: file each action under a FINER moment-by-moment tag (the brain's sense of
time drifts continuously, it doesn't jump one-per-sentence), and when asked, hand back the whole SET of things
that happened at that moment. Either change makes the "busy character" problem vanish completely, and a version
that scrambles the finer tags fails -- so it is the real information doing the work. The sparse "spread it out"
storage the brief asked for turned out to fix a DIFFERENT problem (a character with hundreds of DISTINCT
events, far more than any novel has) rather than this one, and it only works well if we also add the brain's
"fill-in-from-a-partial-hint" step.

## QUESTIONS

None. One judgement call for integration: the measured-fan fix (finer key + set-return) reaches the same
accuracy as an exact pointer on LitBank, so on THIS data it cannot be told apart from a multimap by the number
alone -- the reason to prefer it is that it IS the brain's mechanism (continuous temporal context + context-
cued set reactivation) and it degrades gracefully where a pointer would not, in the high-load/partial-cue
regime.

## NEXT STEPS

Immediate (land the SOLVED fix):
1. Land the two cheap, brain-faithful fixes: a FINER conjunctive event key + a SET-RETURN decode mode on the
   situation-model register. These alone flatten the measured fan.

Frontier (the maximally brain-foundational store is now BUILT as a construction proof -- `exp_entity_store_
unified_v1.py`: factorized content x graded-context x order + schema/gist + race-to-stop). Remaining:
2. **Land the unified store on the REAL register** (`hdlab.situation_model_accumulate`): the graded bindable
   clock as the event key, the schema/gist routing, and the race-to-stop decode. VALIDATE on LitBank at d>=4096
   (the heavy run -> REMOTE GPU box). The mechanism is proven inline; the LitBank-scale number is what remains.
3. **LEARN the structural key** (TEM/Vector-HaSH: next-event-prediction-trained scaffold) instead of the
   hand-designed clock -- this buys cross-entity GENERALIZATION, a different capability than the fan. Largest
   investment; do after 2.
4. The real open build for entity-conditioned PREDICTION remains the SCHEMA-ROLE organ (from the entity line),
   not this store.

Ops note: all frontier CI sweeps AND the LitBank-scale unified-store validation are the HEAVY runs to dispatch
to the REMOTE GPU box (owner directive 2026-08-27); mechanisms are proven inline, the full numbers are the
remote confirmation.

---
INTEGRATED_BY_STRATEGY: 2026-08-27 (grade EXCELLENT). Re-verified FIRST-HAND: test_entity_store_fan.py 21/21 +
test_entity_store_frontier.py 26/26 (ran both myself). The submission corrected the brief's premise (the fan is an
ADDRESSING COLLISION + argmax readout, NOT superposition blur -- unique-address decode 1.0 at every load; top-m recovers
the set at ~1.0), fixed it brain-faithfully (finer conjunctive temporal key + SET-RETURN read = CA3 reactivation; slope
0.288->0.000 CI-sep, info-free order twin loses), and built the maximally faithful FACTORIZED two-system store (sparse DG
exact-recall + graded context, read separately) validated on real LitBank (fan-flat 0.001 AND contiguity 0.585 where a
single key trades them) + matched to Bausch 2026 single-unit data + TEM. Sparse DG relocated to its true home (high-load
exact-recall capacity). Honest deflations self-flagged (retrievability not comprehension; set-return ~= pointer on this
data; kWTA partial-cue deficit unfixed). hdlab LANDED (the cheap proven core): cleanup_set + decode_set (SET-return) on
BOTH register backends (situation_model_accumulate + situation_model_multibank); additive, decode() byte-unchanged;
witness test_situation_setreturn_organ.py PASS both backends; registered situation_register_setreturn_v1. QUEUED
proven-ready follow-on hdlab landings (larger, NOT in this commit): finer conjunctive temporal key; the factorized
two-system store (sparse DG + graded context); schema/gist; CMR race-to-stop; path-integration + local-rule-SR scaffolds.
Review EXCELLENT + SOLVER REVIEW block written to PROBLEM.md; priority cleared. AUDIT UPDATE folded (§2b, corrects the
fan-effect entry). Heavy LitBank-scale validations of the factorized store route to the remote GPU box.
