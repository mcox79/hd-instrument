# Research: Cortex-side LTM consolidation across days/weeks

**Date:** 2026-07-02
**Trigger:** Sonnet Dim A drill concluded P_def 0.32→0.08 — substrate has no temporal structure by construction
(Hebbian commutative; no forgetting curve). "Cortex owns temporal." M1.5 TWO-TIER (Atom 18) identified as the
correct architectural response, but consolidation mechanism (STM→LTM transfer: when, how, what signal) has
never been drilled. Load-bearing for M3 conversational memory over days/weeks.
**Calibration:** 0.20 deflation on novel-synthesis P; brain-existence-proof prior 0.60-0.75 on
brain-canonical mechanisms. Cap novel-synthesis P at 0.50.

---

## HEADLINE

**P_deflated for M3 conversational-memory-over-days viability: 0.42**

The consolidation TRIGGER question is SEPARABLE from the consolidation MECHANISM question. The substrate
already implements the mechanism (BSD write = dense-Hopfield write at alpha~0.147 ceiling per M1.5 CG).
What is unspecified in M1.5 is (a) what signal fires the write, (b) how STM items are ranked for LTM
promotion, and (c) how LTM persists across process restarts.

Brain literature is unanimous on one finding relevant here: sleep-analog consolidation (NREM SWR replay)
is NOT the only mechanism — semantic novelty + usage frequency are the primary offline selection
criteria in systems-consolidation theory. The substrate already has the raw signals; cortex must compose
them into a promotion policy.

**The main risk is NOT mechanism availability — it is the alpha ceiling.** M1.5 CG explicitly found:
dense-Hopfield LTM at alpha=0.147 FAILS (load=1300 > LTM_K=1200 across above-wall regime). A
multi-session conversational agent accumulates far more than 1200 unique items across weeks. This is
the HARD engineering problem: LTM must either paginate (disk-backed cold storage) or employ structured
compression (schema centroids absorb redundant items), not just grow the dense-Hopfield buffer.

---

## Q1: WHEN should cortex consolidate STM→LTM?

### What M1.5 TWO-TIER specifies

The prereq (`preregs/2026-07-01_cortex_context_retention_v2.md`) specifies WHAT the buffer does (route to
STM if load <= K=100, else LTM), but DOES NOT specify the consolidation TRIGGER. Items enter LTM by
overflow from STM — a purely capacity-driven FIFO. There is no importance gate, no usage signal, no
explicit user-marking.

This is a deliberate design gap: M1.5 proved the two-tier ROUTING mechanism. The promotion POLICY is
the next layer of the problem.

### Brain evidence for trigger candidates

**Trigger A: Frequency of use (usage count)**
- Brain basis: long-term potentiation scales with correlated firing frequency (Bliss-Lomo 1973). Items
  that are retrieved more often have stronger synaptic weights — substrate analog is query_freq counter.
- Substrate-native: query_freq is trivially tracked at the cortex API layer (increment counter per bind
  match). DOES NOT require substrate modification.
- Weakness: recency bias if frequency and recency are conflated. Must decay old counts.
- P(effective discriminator) = 0.55 (deflated: simple signal, but decay schedule is hyperparameter).

**Trigger B: Semantic novelty (surprise)**
- Brain basis: locus coeruleus NE release on unexpected events elevates encoding strength (Aston-Jones
  2005). Novelty detection = low cosine similarity of new item vs existing LTM contents.
- Substrate-native: can compute cosine(new_key, W_LTM @ new_key) at write time; low score = novel;
  high score = redundant.
- Critical prior art: `exp_dev_handoff_research_gap_E_selective_forgetting_importance_compression_2026-06-26.md`
  ANCHOR_1 6-signal importance vector includes "surprise" as signal 4 (exactly this computation).
- Weakness: cosine cost is O(N_DIM) at write time; acceptable at N=8192 but must be designed in.
- P(effective discriminator) = 0.60 (deflated; solid brain basis + substrate-native path already designed).

**Trigger C: Recency (timestamp)**
- Brain basis: theta-phase coding — recent events occupy earlier theta-phase slots; consolidation
  preferentially promotes recent items because they are more likely to be requeried.
- Substrate-native: STM buffer is already a FIFO by construction (K=100 most recent). LTM receives items
  that "fall off" the STM tail. Recency IS the M1.5 default promotion policy.
- Weakness: no semantic discrimination. A frequently-queried item from 200 turns ago is evicted from
  STM and replaced by a trivial item from turn 101. Recency alone is insufficient for days-scale memory.
- P(effective discriminator) = 0.35 (deflated; already tested implicitly by M1.5; honest ceiling noted).

**Trigger D: Explicit user marking ("remember X")**
- Brain basis: mPFC voluntary memory encoding (deliberate rehearsal, Baddeley WM persistence path).
- Substrate-native: trivial to implement — user utterance triggers a flag that bypasses frequency/
  novelty threshold and writes directly to LTM.
- Weakness: requires explicit user behavior; passive accumulation doesn't benefit.
- P(effective discriminator) = 0.80 (deflated; trivial mechanism, high user-experience value, no
  substrate risk). HIGHEST SHORT-TERM VALUE trigger.

**Trigger E: Downstream impact (causal importance)**
- Brain basis: synaptic tagging-and-capture (Frey-Morris 1997) — late LTP requires tag protein synthesis
  triggered by strong activation AT THE DOWNSTREAM SYNAPSE (not the encoding synapse). Downstream
  impact = "did this item's retrieval enable a correct action later?"
- Substrate-native: hard. Requires a credit-assignment signal back from the downstream task to the memory
  write. NOT currently implemented in substrate. Would require cortex causal-chain tracking.
- `notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` Block A: "synaptic
  tagging-and-capture: NOT_TESTED; substrate analog = deferred consolidation."
- P(effective discriminator) = 0.40 (deflated; brain-canonical but requires credit assignment not yet
  implemented; gated on Stage 3 causal machinery).

**Trigger F: Sleep-analog batch (NREM SWR replay)**
- Brain basis: Wilson-McNaughton 1994 (hippocampal replay during SWR); Ji-Wilson 2007 (reverse replay);
  Káli-Dayan 2004 (systems consolidation theory). Replay occurs in offline periods (sleep), replays recent
  episodic traces, transfers to cortex via repeated co-activation.
- Substrate analog: BR6 in experiments_backlog.md — between epochs, run reverse-order and shuffled passes
  over the pool (no new data). PLANNED BUT NOT TESTED.
- SWR v3 design spec (`notes/director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md`): iterative
  sequence replay (biologically accurate), not bundling. v1 and v2 both honest-aborted at smoke.
- CRITICAL CONSTRAINT: SWR replay requires an "offline period" — this maps to session boundary in a
  conversational agent (end of conversation = sleep analog). Per-session batch consolidation is
  structurally available.
- P(effective discriminator) = 0.45 (deflated; v1+v2 both failed, v3 design is speculative; session-
  boundary trigger is clean; mechanism is the risk, not the trigger).

---

## Q2: CONSOLIDATION MECHANISM — how does STM→LTM transfer happen?

### Available mechanism classes

**M-A: Immediate BSD write on eviction from STM (current M1.5 default)**
- Every item that falls off STM tail is written to LTM (dense-Hopfield outer product += lr * k otimes v).
- This is the M1.5 default — purely capacity-driven, no importance gate.
- HARD CEILING: once LTM hits alpha=0.138 (Amit-Gutfreund wall at N=8192, K~1130 items), writes
  BEGIN DEGRADING prior memories. M1.5 verified: at alpha=0.147, load=1300 FAILS (top-1 = 0.000).
- For days-scale memory in a conversational agent: UNSUSTAINABLE without structured compression.

**M-B: Importance-gated write (proposed ANCHOR_1 in Gap E handoff)**
- 6-signal importance vector: recency + query_freq + downstream_impact + surprise + schema_contribution
  + cortex_predicted_salience.
- ONLY write to LTM if importance score >= tau. Prevents trivial items from consuming capacity.
- LTM management: periodic promotion/eviction based on importance decay (items lose importance over
  time unless re-queried; eviction frees capacity for new items).
- DESIGN GAP: threshold tau is a hyperparameter. Must be calibrated per-user or per-domain.
- NOT YET IMPLEMENTED. ANCHOR_1 is gated on M1.5 landing (which has now landed as CG).

**M-C: Schema-centroids compression (ANCHOR_3 in Gap E handoff)**
- When many items cluster semantically (cosine similarity > tau), compress cluster into a centroid
  "schema" atom. Store centroid rather than all instances. Protects schema atoms as immortal;
  compresses instance atoms over time.
- Brain analog: cortical schema formation (mPFC-MTL, Tse et al. 2011 Science; Winocur et al. 2010).
  Well-established in systems-consolidation literature.
- Substrate-native path: cosine clustering of LTM atoms is computable. Centroid = mean of cluster keys.
- ADVANTAGE: decouples LTM capacity from unique-item count. At N=8192, centroid of 50 similar items
  costs 1 slot instead of 50.
- GATED ON: Gap 3 BCM (W_schema centroids meaningful). Not yet tested.
- P(effective mechanism) = 0.45 (deflated; strong brain basis; schema emergence in substrate is MM
  not CG).

**M-D: Session-boundary batch replay (sleep-analog)**
- At end of each conversation session: run SWR v3 iterative replay over STM contents, writing the
  most-reinforced items to LTM in temporal order.
- STRUCTURALLY CLEAN: session end maps to NREM sleep; within-session is "waking" STM; across-session
  is "cortical LTM."
- GATED ON: SWR v3 honest-abort resolution (v1 and v2 both failed at smoke). V3 design is promising
  but untested.
- P(effective mechanism) = 0.40 (deflated; prior SWR failures both at smoke; v3 design addresses root
  causes but empirically unproven).

---

## Q3: SUBSTRATE CAPACITY CONSTRAINT — how to prioritize STM→LTM at M=1M?

The M=1M CG (hippo v5, Atom cortex LLN) proves kernel_active_fraction = 99% at M=1M with wall 6.9-13.5s.
This is STORAGE capacity (M=1M items can be encoded). But:

- Dense-Hopfield LTM at N=8192 has alpha_c = 0.138 → max K_LTM = 1130 items.
- M=1M refers to the HOPFIELD substrate's total stored pattern capacity at COMMERCIAL SCALE, not the
  cortex's addressable LTM buffer per session.
- THESE ARE DIFFERENT: M=1M is the substrate's storage tank; LTM retrieval accuracy depends on alpha
  (fraction of the total that you query AGAINST at once), not M.

**Resolution:** LTM across days/weeks must be PAGINATED. Store M=1M items to disk; at query time, load
only the most relevant K=1000-1200 items (highest importance-score neighbors) into the active
dense-Hopfield LTM buffer. This is the LSM-tree analog from ANCHOR_4 in the Gap E handoff.

Page-in policy: cosine pre-filter against a fast approximate index (e.g., HNSW or IVF) on the dense key
vectors → retrieve top-K candidate keys → page those into W_LTM → run dense-Hopfield cleanup → return.

This architecture DOES scale across days. M=1M items on disk; active LTM window = 1000 items at alpha
below wall. LTM retrieval cost = ANN search (fast) + K=1000 matrix multiply (fast at N=8192).

---

## Q4: EBBINGHAUS FORGETTING CURVE ANALOG

**Substrate has NO decay by construction.** Hebbian write is cumulative; no write REMOVES a stored pattern
(only new writes that interfere degrade prior retrieval via crosstalk).

Consequence: reinforcement is unnecessary for substrate-side persistence. Once written to W_LTM (or to
disk), a memory trace does NOT fade unless:
(a) alpha exceeds 0.138 (new writes interfere), or
(b) explicit eviction removes the item from the LTM buffer.

**Cortex CAN implement artificial decay if desired** (multiply W_LTM by decay_factor < 1 per session). But
the brain argument for decay (synaptic homeostasis — Tononi-Cirelli 2006 slow oscillation downscaling
hypothesis, SHY) exists to FREE capacity for new learning. The substrate has the same capacity argument:
if you never decay/evict, alpha grows and precision degrades. SHY is a capacity-management mechanism, not
a feature; substrate LTM needs the same management even without biological decay.

**Spaced repetition:** useful for ensuring important items are ACCESSIBLE (i.e., loaded into the active LTM
buffer at query time via page-in policy). Not needed for persistence. The operational analog is ensuring
high-importance items survive the page-in priority queue rather than being displaced by newer items.

---

## Q5: CROSS-ITEM CONSOLIDATION — explicit vs implicit

**Explicit ("remember X for tomorrow"):** Trigger D (user marking). Trivially implementable. Bypasses all
threshold logic; writes directly to LTM + disk. HIGH VALUE first step.

**Implicit:** Requires Trigger A (usage frequency) + Trigger B (semantic novelty) as the minimum viable
importance signal. Both are substrate-native computations.

The 6-signal ANCHOR_1 vector is the full-stack implicit policy. But minimum viable is 2 signals:
query_freq + novelty_cosine. This is testable today (ANCHOR_1's 4FACTOR_NOCORTEX arm).

---

## Q6: STM OVERFLOW FAILURE MODES

M1.5 discriminator explicitly probes this: at load > K_STM = 100, items are evicted from STM.
Three distinct failure modes:

**FM-1: Item in STM gap (evicted from K100, not yet in LTM because no importance trigger fired)**
- Occurs when: item was retrieved once (low query_freq), novelty was moderate, user didn't mark.
- Result: LOST. No recovery path.
- Mitigation: raise default K_STM (cost: more WM capacity per session) OR lower importance threshold
  (cost: LTM fills faster).

**FM-2: LTM above-wall alpha degradation**
- Occurs when: LTM buffer accumulates > K~1130 items without eviction (M1.5 directly measured: load=1300
  FAILS at top-1=0.000).
- Result: RETRIEVAL NOISE for all items, not just the newest.
- Mitigation: importance-gated eviction OR schema-centroid compression OR pagination.

**FM-3: Session boundary loss (no persistence)**
- Occurs when: torch tensors freed at process exit (current substrate is in-memory).
- Result: ALL LTM lost between sessions.
- Mitigation: persistence layer (Q7).

---

## Q7: PERSISTENCE ACROSS SESSIONS — STORAGE MODEL

**Current substrate status:** in-memory torch tensors. Zero persistence across process restarts.

**What "persistence" means for LTM:**
- W_LTM is a float32 tensor of shape (N_DIM, N_DIM) = (8192, 8192) = 64M floats = 256 MB per session.
- THIS IS SMALL ENOUGH FOR DISK. torch.save / torch.load is sufficient for V1 persistence.

**Storage model recommendation (ranked by M3 deployment feasibility):**

**TIER 1 — V1 (ship now): torch.save(W_LTM, path)**
- At session end: torch.save(state_dict, "{session_id}_ltm.pt")
- At session start: torch.load if file exists
- Cost: 256 MB per session, instantaneous read/write on SSD
- No schema required; works today
- LIMITATION: one LTM tensor per session; no cross-session merging; 256 MB per user-day

**TIER 2 — V2 (when M1.5 multi-session CG is needed): item-level disk index**
- Store individual (key, value, metadata) tuples in SQLite or HDF5
- At session start: load top-K_LTM items by importance score into W_LTM via batch Hebbian write
- Supports: importance-gated eviction, cross-session ranking, ANN pre-filter
- Cost: O(M_total) storage; schema design required; ~1 week to implement

**TIER 3 — V3 (production M3): HNSW vector index + W_LTM page-in**
- Full ANN index (HNSW via faiss or hnswlib) over all stored keys
- Query-time: ANN search → retrieve top-K candidates → page into temp W_LTM → cleanup
- Decouples storage capacity from retrieval alpha (solves Q3 capacity problem permanently)
- Cost: significant infra; appropriate only when multi-user or M >> 1M scale

**RECOMMENDATION:** Ship TIER 1 now. It closes the "zero persistence" gap immediately and unblocks M3
proof-of-concept. TIER 2 becomes necessary when consolidation trigger experiments (ANCHOR_1) land and
multi-session importance ranking is needed. TIER 3 is commercial scale.

---

## RANKED CONSOLIDATION-TRIGGER CANDIDATES (by M3 value)

### Rank 1: EXPLICIT USER MARKING (Trigger D)
- P(effective) = 0.80 (deflated from 0.95; trivial mechanism, no substrate risk)
- M3 value: HIGH (conversational agents need "remember X" as a first-class primitive; matches user
  mental model; closes the "I told it something important and it forgot" failure mode)
- Implementation cost: 2-3 days (flag detection in cortex API + direct LTM write path)
- Ships independently of any pending cell results
- BUILD FIRST

### Rank 2: FREQUENCY + NOVELTY composite (Triggers A+B)
- P(effective) = 0.52 (deflated; both signals have brain basis; composite not yet tested in substrate)
- M3 value: HIGH (covers the implicit case — items user never explicitly marked but naturally requeried
  + semantically unique items should survive; enables passive memory without user overhead)
- Implementation cost: 1-2 weeks (requires ANCHOR_1 4FACTOR_NOCORTEX arm to land CG first)
- GATED ON: ANCHOR_1 dispatch (ANCHOR_1 is now dispatch-eligible since M1.5 = CG)
- BUILD SECOND (dispatch ANCHOR_1 4FACTOR_NOCORTEX arm now)

### Rank 3: SESSION-BOUNDARY BATCH REPLAY (Trigger F, sleep-analog)
- P(effective) = 0.38 (deflated; SWR v1+v2 both honest-aborted; v3 design promising but unproven)
- M3 value: MEDIUM (adds biological fidelity + offline reinforcement of within-session sequences;
  secondary to the two triggers above for a practical agent)
- Implementation cost: 3-4 weeks (SWR v3 must land CG first)
- GATED ON: SWR v3 cell landing
- BUILD THIRD after SWR v3 lands

---

## FALSIFIABLE PREDICTIONS

**P1 (explicit trigger, testable now):** Explicit-mark LTM items retrieved at load=2000 (well above K=1200
LTM default) with top-1 >= 0.80 after importance-gated eviction clears the above-wall pressure. Test: mark
10 items explicitly, fill with 2000 others, query marked items. CHEAP (1 cell, 1 arm, numpy).

**P2 (composite trigger, gated on ANCHOR_1):** query_freq + novelty signal achieves > +0.15 top-1 vs
recency-FIFO promotion at load=1500 (above standard LTM wall). ANCHOR_1 4FACTOR_NOCORTEX arm tests this.

**P3 (cross-session persistence, testable now with TIER 1 torch.save):** W_LTM saved at session end,
reloaded at session start, achieves same top-1 accuracy as within-session retrieval for K=100 explicitly
marked items. Trivially true by tensor round-trip; value is proving the end-to-end path works.

**CHEAPEST CELL DESIGN for falsifying P1:** `ltm_explicit_mark_above_wall_v1`
- Arms: (1) FIFO promotion baseline, (2) explicit-mark protected promotion
- Sweep axis: load in [200, 800, 1500, 2500]
- N_DIM=8192, K_LTM=1200, K_PROTECT=10 (marked items)
- Discriminator: top-1 accuracy for marked items vs unmarked at above-wall loads
- Expected HARD_PASS if explicit-mark protection gate correctly skips the FIFO eviction path
- CPU cost: ~2 hr; single seed smoke; numpy only

---

## M3 ARCHITECTURE IMPLICATIONS

**Primary implication: The TWO-TIER buffer in M1.5 is NECESSARY but NOT SUFFICIENT for days-scale memory.**

The M1.5 CG establishes the routing mechanism (STM K=100 for recent context; LTM K=1200 for session
history). What it does NOT provide:

1. A promotion POLICY (importance gate) — ANCHOR_1 is the next cell
2. Cross-session PERSISTENCE — TIER 1 torch.save unblocks this immediately
3. Above-wall CAPACITY MANAGEMENT — pagination (TIER 2/3) or schema compression (ANCHOR_3)

**Build sequence for M3 conversational memory:**

STEP 1 (this week): Ship TIER 1 persistence (torch.save at session end/load at start). Zero risk; closes
the cross-session loss gap. Can be done in main-thread code, no cell required.

STEP 2 (dispatch now): ANCHOR_1 4FACTOR_NOCORTEX arm — tests frequency + novelty composite without
cortex composition. This is the minimum-viable implicit promotion policy. If HARD_PASS, it directly gates
Step 3.

STEP 3 (gated on ANCHOR_1 HARD_PASS): Wire frequency + novelty scores into TWO-TIER promotion logic.
Items above threshold get LTM write; items below threshold age out of STM with no LTM promotion. This is
the practical importance gate for a conversational agent.

STEP 4 (gated on SWR v3): Add session-boundary batch replay to reinforce items that were frequently
queried within the session before writing to disk LTM.

STEP 5 (gated on ANCHOR_3 + schema CG): Add schema-centroid compression to decouple LTM capacity from
item count.

**The M1.5 alpha ceiling (0.138 Amit-Gutfreund wall) is the single most load-bearing constraint.** EVERY
design choice above is ultimately about staying below this wall while maximizing the semantic coverage of
the items that DO make it into the active LTM buffer.

---

## PRIOR WORK OVERLAP CHECK (substrate-KB queries run 2026-07-02)

- `bash tools/substrate_query.sh "STM LTM consolidation hippocampal replay sleep"` — top hit: engram
  consolidation block 2026-06-02 (cosine=0.41). That anchor BLOCKED at smoke due to sub-threshold alpha
  (alpha_total < alpha_c). Root cause is now understood (needed alpha_total > 0.138); M1.5 addresses it.
- `bash tools/substrate_query.sh "memory consolidation cortex sleep NREM replay transfer"` — top hits:
  BR6 sleep-replay backlog (cosine=0.36); hippocampal-cortical consolidation replay (cosine=0.34). Both
  are NOT DONE per 2026-06-24 inventory. This drill is the first directed analysis of this gap.
- Gap E handoff (2026-06-26): ANCHOR_1 6-signal importance vector is directly relevant. Now dispatch-
  eligible since M1.5 = CG. 4FACTOR_NOCORTEX arm (substrate-only signals) is the cheapest next step.

---

## REFERENCES (all from substrate + project notes)

- `preregs/2026-07-01_cortex_context_retention_v2.md` — M1.5 TWO-TIER full spec; alpha ceiling at 0.147
- `notes/exp_dev_to_strategy_engram_consolidation_block_2026-06-02.md` — prior consolidation cell blocked (alpha < alpha_c)
- `notes/exp_dev_handoff_research_gap_E_selective_forgetting_importance_compression_2026-06-26.md` — ANCHOR_1 6-signal design; ANCHOR_4 LSM-tree baseline
- `notes/director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md` — sleep-analog replay v3 design
- `notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md` — synaptic tagging-and-capture NOT_TESTED; Block D memory/consolidation inventory
- `notes/experiments_backlog.md` — BR6 sleep-replay offline consolidation entry
- Brain lit via existing notes: Bliss-Lomo 1973 (LTP); Frey-Morris 1997 (tagging-capture); Wilson-McNaughton 1994 (SWR replay); Tononi-Cirelli 2006 (SHY homeostasis); Tse et al. 2011 (cortical schema); Aston-Jones 2005 (NE novelty modulation)
