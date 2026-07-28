# Memory consolidation: brain-fidelity audit + brain-faithful redesign (2026-07-28)

Research/design drill (Director, main thread). NOT built/dispatched/banked. Deliverable = this note.
Grounds in: notes/v4_negative_brain_fidelity_audit_readout_is_order_blind_next_lever_2026-07-27.md,
notes/research_fast_concept_learning_informs_selflearning_loop_2026-07-27.md,
experiments/exp_unified_self_learning_loop_v2.py (`_sleep_consolidate`/`_kalman_fold`/`_ca3_complete`),
experiments/exp_unified_self_learning_loop_v5.py (`_sleep_consolidate_v5`/`_fast_episodic_read`),
hdlab/hippocampal_encoder.py (`DGProjection`, `CA3AutoAssociator`, `cls_replay_cycle`,
`cls_discrete_budget_consolidate`), preregs/2026-07-08_cls_ca3complete_consolidation_v1.md +
data/exp_cls_ca3complete_consolidation_v1/metrics.json (landed HARD_PASS).
Citations below are standard consolidation-neuroscience landmarks (McClelland/O'Reilly 1995;
Marr 1971; Tse/Morris 2007/2011; Frey/Morris 1997; Wilson/McNaughton 1994; Diba/Buzsaki 2007;
Buzsaki 1989/2015) recalled from general knowledge, NOT re-verified against fresh sources this
drill (no web fan-out was run) — treat as reasoning aids, not VET'd literature, per the lit-scan
calibration discipline.

## 0. Bottom line (read this first)

Our loop's consolidation step, in every version so far (v1 plain-average, v2 precision-Kalman,
v2 CA3-single-shot-denoise, v4/v5 fast-episodic **competitive weighted average**), is a form of
**eager, single-pass, direct cortical writing** — it takes whatever mentions have accumulated
this cycle and folds them into ONE concept-level slow-store vector immediately, once. The brain
never does this. Cortical semantic memory is written **only via offline REPLAY**, over many
repetitions, interleaved with old material, and the replay budget/priority is **not uniform** —
it is gated by novelty/prediction-error (which items get replayed, and how often) and by
schema-consistency (how fast an item is allowed to integrate). None of our arms do offline
replay. The "fast_episodic" mode (v4/v5) got closest — it keeps mentions as separate traces and
does a context-addressed *competitive read* at measurement/commit time — but the read is still a
**single soft-weighted blend computed once**, not an iterated interleaved replay loop, and the
value it blends over is still not schema/novelty-gated. That is the load-bearing gap.

We also already possess a **certified** (HARD_PASS, CHAIN_GRADE-eligible) primitive that DOES do
brain-faithful offline discrete-budget replay with SWR-style partial cueing and CA3 completion —
`hdlab.hippocampal_encoder.cls_discrete_budget_consolidate` (landed via
`exp_cls_ca3complete_consolidation_v1`, commit 92e01cf3f, gap 0.913 old-retention vs naive) — and
the self-learning loop has never used it. This is a WIRE-DON'T-ISLAND gap, not a build gap.

## 1. How the brain consolidates a newly-read item (lead with neuroscience)

**Hippocampal rapid encoding (fast, sparse, one-shot).** New experience enters via entorhinal
cortex -> dentate gyrus (DG) -> CA3 -> CA1 -> back to cortex. DG performs **pattern separation**:
a high-dimensional sparse expansion (many more granule cells than entorhinal input units, ~3-5%
active) that decorrelates similar inputs so overlapping experiences get near-orthogonal codes
(Marr 1971; O'Reilly/McClelland 1994). CA3 is a **recurrent autoassociator** (sparse Hebbian
outer-product) that can pattern-complete a full episode from a partial cue. Critically, this is a
**single encoding trial** — hippocampus can bind an entire episode (who/what/where/when, i.e. a
structured *conjunction*, not a centroid) in one shot, at high learning rate, because sparse
coding minimizes interference between one item's write and another's.

**Sharp-wave-ripple (SWR) replay during rest/sleep.** Offline (quiet wakefulness, slow-wave
sleep), hippocampus spontaneously reactivates recently stored sequences in compressed, punctate
bursts (Wilson & McNaughton 1994; Buzsaki 1989/2015). Replay is NOT literal-every-item-uniformly:
it is **biased toward high reward / high prediction-error / behaviorally salient experiences**
(Ambrose, Foster, Buzsaki lines of evidence), and includes REVERSE replay for credit assignment
(Foster & Wilson 2006; Diba & Buzsaki 2007). Each replay event feeds a Hebbian update to cortical
synapses — cortex learns from **many small, repeated, interleaved exposures**, not from a single
fold of the raw episode.

**Two-stage CLS model (McClelland, McNaughton & O'Reilly 1995; McClelland & O'Reilly).**
Hippocampus = fast, sparse, high-plasticity, pattern-separated store, good for one-shot episodic
binding but a bad long-term semantic substrate (interference-prone, doesn't generalize). Cortex =
slow, dense, low-plasticity, statistically-structured store, built by **interleaved replay** of
hippocampal traces mixed with the existing cortical training distribution — this interleaving is
the mechanism that prevents catastrophic interference (a cortical net trained only on the new item
would overwrite old knowledge; replaying old + new together lets gradient-like updates find a
representation that fits both). Systems consolidation moves the "authoritative" copy from
hippocampus to cortex over days-to-years as replay accumulates.

**Schema-consistency gating (Tse, Langston, Kaag, Morris et al. 2007, 2011 — the "PRE" paradigm
in rodents).** New information that is CONSISTENT with an existing well-established cortical
schema can be assimilated into cortex **rapidly, sometimes in a single trial**, because the
existing schema provides most of the structure and only the delta needs writing — and this fast
learning can even become hippocampus-INdependent quickly. Information INCONSISTENT with any
existing schema still requires the slow, many-replay hippocampal-dependent route (or is
gated/rejected). This is asymmetric: schema-fit determines HOW FAST + THROUGH WHICH ROUTE
something consolidates, not merely how much it's trusted.

**Prediction-error / novelty weighting.** Hippocampal encoding strength and replay priority both
scale with surprise — novel or poorly-predicted events drive stronger dopaminergic/
noradrenergic-gated plasticity (novelty signal, VTA/locus-coeruleus inputs to hippocampus) and are
preferentially replayed. Well-predicted, redundant repeats add little new information and get
comparatively little consolidation resource.

**Synaptic tagging and capture (Frey & Morris 1997).** A weak/novel event sets a short-lived
molecular "tag" at the synapses it activated; that tag can later CAPTURE plasticity-related
proteins synthesized during a subsequent salient event (or during sleep replay) to make the change
durable. Functionally: a novel item is not committed on first exposure — it is flagged, and
becomes durably written only if a later consolidation pass (replay) "captures" it. Commitment is
gated by SUBSEQUENT replay, not by the immediate encoding.

**Interleaved replay avoids catastrophic interference.** The mechanism that makes cortical
learning safe for continual acquisition is that every consolidation phase touches a **mix of new
and previously-consolidated items** (replay budget spent across a schedule, not spent entirely on
whatever just arrived), which is exactly the design already certified in
`cls_discrete_budget_consolidate` (fixed per-phase budget B, replay drawn from a recency-decayed
fast store of BOTH old and new keys, SWR partial-cue -> CA3-cleanup -> write to a slow store).

## 2. Element-by-element gap audit: brain vs. our mechanism

| # | Element | Brain | Us (v1/v2 plain, precision, ca3-single-shot; v4/v5 fast_episodic) | Gap |
|---|---|---|---|---|
| 1 | What gets written per exposure | a structured, pattern-separated EPISODE (conjunctive; DG-sparse; distinct trace per event) | v1-v4: mean-pooled scalar-per-mention vector, kept as a list (OK-ish, list is per-mention) but READ via mean/weighted-mean, so structure is destroyed at readout, not storage. v5 fixes the per-mention READOUT (HRR-bind), so the trace itself is now closer to brain-faithful. | v1-v4 defect at readout (already found + partly fixed in v5); v5 fixed this element |
| 2 | Consolidation TIMING | OFFLINE, during rest/sleep, as a SEPARATE phase from encoding, over MANY repeated replay events | our "sleep" phase runs once per cycle and does exactly ONE update per concept (one Kalman fold, or one softmax blend) — a single pass, not iterated replay | **THE CORE GAP** — "sleep" in our loop is a commit gate, not a replay loop |
| 3 | What gets consolidated (each replay event) | ONE sampled/cued episode at a time, reconstructed via CA3 pattern-completion from a partial cue, written into cortex with a small Hebbian step | ALL accumulated mentions for a concept are FOLDED TOGETHER in one shot (mean, Kalman-fold-over-all, or softmax-weighted-sum-over-all) | averaging/blending-over-all-at-once is structurally the opposite of one-at-a-time small-step replay |
| 4 | Priority: which items get consolidation resource | replay is BIASED toward high prediction-error / salient / poorly-consolidated items; well-predicted repeats get little further resource | uniform: every accumulated mention for a concept participates in the fold/blend with equal (or purely similarity-derived, not surprise-derived) weight | **missing prediction-error-based priority entirely** |
| 5 | Interleaving old + new | replay phases mix OLD (already-consolidated) and NEW items from a shared budget, which is what prevents catastrophic interference | no interleaving: each concept's update only ever touches THAT concept's OWN new mentions; nothing analogous to shared cross-concept replay budget exists in the loop | **missing entirely** — but `cls_discrete_budget_consolidate` already implements exactly this and is certified |
| 6 | Schema-consistency gating | schema-CONSISTENT info assimilates FAST (can be near one-shot); schema-INCONSISTENT info is slow/gated | our "override gate" (`new_conf >= override_min`) gates on CONFIDENCE/COVERAGE (how many corroborating mentions, how coherent they are with EACH OTHER), never on fit to the concept's EXISTING relational neighborhood in the foundation graph | related but distinct axis — we gate on internal agreement, brain gates on external fit-to-schema; **wrong gating signal** |
| 7 | Synaptic tagging / delayed capture | a novel trace is flagged and only durably committed if CAPTURED by a later consolidation event | commit is immediate (same cycle) once the coverage/coherence gate passes; nothing persists a novel-but-unconfirmed trace across MULTIPLE future sleep phases waiting for corroboration | **missing** — no notion of "tagged, not yet committed, eligible for future capture" |
| 8 | Denoising/completion | CA3 iterative pattern-completion pulls a noisy partial cue back to the nearest stored attractor DURING replay (i.e., it operates on ONE replayed item against the FULL stored manifold) | our `_ca3_complete` (v2) is a single soft k-NN attractor step applied to the ALREADY-FOLDED consolidated candidate, once, at write time — same idea, wrong point in the pipeline (post-fold, not per-replay-item; against a FIXED foundation manifold, not the growing episodic store) | partial credit — mechanism exists, wrong place/wrong target set |

**Why averaging specifically destroys the comprehension signal (mechanistic, not just empirical):**
a concept's mention set typically contains a MIX of high-information sentences (the specific new
fact) and low-information/boilerplate context. A single mean (or single softmax blend, which is
just a temperature-smoothed mean) necessarily produces a **compromise point** — any one mention's
specific content is diluted by 1/n (or by its blend weight) into every other mention's content in
the SAME operation, in the SAME timestep. There is no mechanism by which a specific, surprising
fact ever gets to dominate a durable memory trace, because it is never treated differently from
routine repeats — it only ever contributes a fractional vote to a single running centroid. The
brain's route to specificity is exactly the opposite: a novel item gets ITS OWN sparse trace,
tagged for priority, and consolidated via many SEPARATE small-step replay events that are
INTERLEAVED with (not blended into) everything else — so it is capable of dominating cortical
weight-space near its own attractor without ever being algebraically averaged against unrelated
content. "Retrieve-not-average" (the v4/v5 fast_episodic softmax read) is a real improvement in
KIND (keeps traces separate until read) but is still a single-shot weighted-mean AT READ TIME —
mathematically it is `sum(w_i * x_i)`, i.e. still one averaging operation, just with learned
(similarity-derived, not surprise-derived) weights instead of uniform weights. That is why it
"didn't help": it is the same operation-class as plain averaging, one level removed.

## 3. Design: the brain-faithful replacement

**Do NOT propose centroid-averaging in any form (uniform, precision-weighted, or
similarity-weighted-softmax) as the terminal write.** Replace the *single-fold* consolidation step
with an **offline discrete-budget replay loop**, reusing certified substrate primitives:

### 3.1 Candidate menu, scored for brain-fidelity and build cost

1. **Replay-based interleaved updates (RECOMMENDED, cheapest — already built + certified).**
   `hdlab.hippocampal_encoder.cls_discrete_budget_consolidate` already implements: a
   recency-decayed fast associative store (episodic mentions, keyed by context), a fixed
   per-phase replay budget B, SWR-style partial-cue reactivation (`cue = rho*key +
   sqrt(1-rho^2)*noise`), CA3 pattern-completion of the noisy readout against a concept
   codebook, and a Hebbian-style write into a SEPARATE slow store — proven (HARD_PASS,
   `data/exp_cls_ca3complete_consolidation_v1/metrics.json`, gap=0.913) to retain OLD material
   while acquiring NEW under a fixed budget, i.e. genuine continual-learning-without-forgetting
   via interleaving. **Cost: wiring, not invention.** The loop currently discards this primitive
   entirely and reinvents a weaker single-shot mechanism.
2. **Schema-consistency-gated writes (RECOMMENDED, cheap, additive on top of #1).** Before a
   replayed item is captured into the slow store, test whether its CA3-completed value is
   CONSISTENT with the concept's existing relational neighborhood in the (already-built) 1.24M-
   edge foundation graph — e.g. does completion converge with low residual / does the completed
   value's nearest foundation neighbors agree with the concept's known typed relations. If
   consistent -> fast-track (large capture probability / small budget cost, can even skip
   multiple replay rounds). If inconsistent/novel -> route to the SLOW path: keep tagged in the
   fast store, spend MULTIPLE replay rounds across MULTIPLE future sleep phases before capture
   (see #4). This reuses the SAME foundation-graph machinery the loop's leak-proof relational
   probe already reads (careful: the schema check must read the TRAIN-side graph only, never the
   held-out answer edges being scored, to preserve leak-proofness — same discipline already
   enforced for CA3-completion's leak-proof note in the v2 pre-reg).
3. **Prediction-error-gated priority replay (RECOMMENDED, cheap, additive).** Order/weight the
   discrete replay budget by SURPRISE instead of recency or uniform draw: surprise(mention) =
   1 - cos(mention_rep, concept's CURRENT slow-store rep at encoding time) (i.e., how far the new
   read is from what the substrate already "expected" for that concept). High-surprise mentions
   get replayed EARLY and get MORE of the fixed budget; well-predicted repeats get little/no
   budget. This is a straightforward re-ordering of `replay_keys` before calling
   `cls_discrete_budget_consolidate` — no new primitive needed.
4. **Synaptic-tagging-style delayed capture (moderate cost, second-order refinement).** A novel
   mention is written to the fast episodic store with a "tag" (elevated future-replay-priority)
   but is NOT eligible for slow-store commit until it has been successfully replayed/completed
   >= K times across >= K DISTINCT sleep phases (not K times in one phase). This requires the
   loop to persist per-item replay-counts across cycles (small state addition) — doable, but adds
   a temporal-consistency requirement current cycle-boundaries don't track cleanly. Sequence it
   AFTER #1-3 land (it refines the capture criterion of a mechanism that must exist first).
5. **Pattern-separated episodic storage with cue-dependent completion at RETRIEVAL, not eager
   consolidation (already partially built).** v4/v5's `_fast_episodic_read` already keeps
   per-mention traces distinct in the store and defers blending to read-time — this is the right
   SHAPE (episodic-store, not eager-average) but the wrong OPERATION at read time (a single
   softmax blend, not iterated replay+Hebbian-write). Recommendation: keep the DG-sparse KEY
   space v5 built (`_sparse_keys` with common-mode removal — this part is brain-faithful DG
   pattern-separation and should be REUSED, not replaced), but stop using it to compute a
   softmax-blend VALUE. Instead use the sparse keys as the CUE space that
   `cls_discrete_budget_consolidate`'s SWR partial-cue mechanism reads from.

**Cheapest defensible next build = #1 + #2 + #3 composed**, because #1 is already certified code
(zero new mechanism risk), #2 and #3 are both O(10-30 line) additions around an existing call
(a similarity/consistency check and a re-sort), and all three compose naturally: replay ORDER is
set by surprise (#3), replay ITEMS are drawn from the interleaved discrete-budget SWR mechanism
(#1), and CAPTURE into the slow store is gated by schema-fit (#2). #4 is deferred as the next
refinement once #1-3 show a real (not tied) comprehension-specific gain.

### 3.2 What stays fixed (do not re-litigate; these are settled by v4/v5)

- **Readout: v5's `BIND_HRR_position`** (HRR-bind per-position role x token hidden, own-mechanism,
  no bolt-on reader) stays as the per-mention encoding. STEP-0 (2026-07-27) already proved
  mean-pool is order-blind (coh-vs-scram cos=0.9944) and bind separates it (0.7304); re-deriving
  this is not in scope. Consolidation redesign must consume BIND-space traces, not re-introduce
  pooled centroids anywhere in the pipeline (the same space-consistency discipline v5's pre-reg
  already enforced for the readout swap applies here: every call site that touches a rep must
  agree on geometry).
- **DG key space: v5's centered `_sparse_keys`** (common-mode removed before k-WTA) is real
  brain-faithful pattern separation (STEP-0: raw cross-concept cos 0.9444 -> -0.0645 centered) and
  should be REUSED as the cue/key space for the new replay mechanism, not rebuilt.
- **Leak-proofness**: schema-consistency checks (#2) and any foundation-graph lookups must stay
  on the TRAIN-side graph, structurally disjoint from the held-out predicted edges scored by
  `relational_eval` — same invariant every prior arm in this lineage has enforced.

## 4. Fairness / can-fail design

**Isolate consolidation from encoder/readout (hold both fixed).** Use the SAME frozen v2
checkpoint (`ckpt_seed_7`) and the SAME v5 monkeypatched `BIND_HRR_position` readout for every
arm. The ONLY variable across arms is the consolidation/store mechanism:
- `plain` (v1/v2 baseline, expected wash-out — reproduces v1/v2's negative as the sanity check
  that the harness still shows the KNOWN failure mode)
- `fast_episodic` (v4/v5 softmax-blend baseline — the CURRENT best arm, must be beaten, not just
  matched, or the new mechanism has not earned its added complexity)
- `replay_schema_gated` (NEW: #1+#2+#3 composed — the candidate under test)

**Matched controls, same discipline v4/v5 already used (do not relax it):** SCRAMBLED-text and
WRONG-CONCEPT controls must run through the IDENTICAL `replay_schema_gated` consolidation mode as
MAIN (not a different, easier mode) — this is exactly what made v4/v5's comparison fair and must
be preserved. Additionally, this design specifically predicts SCRAMBLED should now behave
DIFFERENTLY from before: word-scrambled text should have LOW schema-consistency (garbled content
should fail the CA3-completion consistency check more often) -> should get GATED to the slow path
more often -> should show REDUCED capture rate, not just reduced final-rep quality. That is a
NEW, sharper, mechanism-specific discriminator this design predicts and prior arms could not even
express (a can-fail prediction beyond "gain > scrambled's gain").

**DEFLATE null (pre-registered, honest failure mode):** if `replay_schema_gated` STILL ties
SCRAMBLED on comprehension-specific gain even though (a) the readout demonstrably separates
coherent-vs-scrambled at the representation level (v5 STEP-0 already showed this, modestly:
0.7304, not near-zero) and (b) the schema-consistency gate demonstrably fires differently for
coherent vs scrambled mentions (a NEW self-test-level check this design must include: verify
schema-consistency SCORES differ, coherent > scrambled, before trusting downstream gain), then the
honest conclusion is that the residual gap is NOT the consolidation update rule — it is (i)
insufficient replay dosage/budget at the data density available (LOW-slice concepts may simply
have too few mentions for ANY replay-based scheme to accumulate signal — check n_mentions/concept
LOW-slice median before over-interpreting a null), or (ii) the metric (relational-AUC + specific-
fact probe) under-detects real acquisition, or (iii) the bind-readout's 0.73 coherent-vs-scrambled
separation, while real, is still too weak a signal-to-noise ratio for a mean-field metric to catch
at LOW exposure. Do not conclude "consolidation is fully solved" from a tie without checking
schema-gate discriminant validity first (VET POSITIVES HARDEST, VET NULLS for confound too).

**Isolating "better consolidation" from "better readout":** the comparison above already holds
readout fixed across ALL three consolidation arms (plain / fast_episodic / replay_schema_gated),
so any gain difference among them is attributable to the consolidation mechanism alone, not to
the v5 readout fix (which is common to all three and already separately proven necessary-but-
insufficient by the v5 FULL MIDDLE_BAND result).

## 5. Recommended next experiment (cheapest brain-faithful, once encoder work settles)

**v6 (name suggestion): `unified_self_learning_loop_v6_replay_consolidation`.** Reuse v5's cell
wholesale (frozen ckpt, BIND_HRR_position readout, centered `_sparse_keys`, 7-arm/LOW-MID-HIGH-ALL
exposure design, leak-proof `relational_eval`). Swap ONLY `_sleep_consolidate_v5`'s
`fast_episodic` mode for a new `replay_schema_gated` mode that:
1. Maintains each concept's accumulated mentions as a fast associative store keyed by the
   centered DG sparse key (reuse `_sparse_keys` verbatim).
2. At each sleep phase, calls `hdlab.hippocampal_encoder.cls_discrete_budget_consolidate` with
   `replay_keys` ORDERED by surprise = `1 - cos(mention_rep, current slow_store[ci])` (highest
   surprise first; #3), a small fixed `budget` per concept per phase (start with budget=3-5,
   matching the discrete-budget gate the certified cell validated), `concept_codebook` = the
   FIXED train-side foundation reps (same as `_ca3_complete`'s `base_clean`, leak-proof), and
   `ca3_complete=True`.
3. Adds the schema-consistency gate (#2) on the completion output: compute residual/consistency
   between the CA3-completed value and the concept's train-side foundation-graph relational
   neighborhood (reuse whatever adjacency structure `relational_eval` already loads, train-side
   only); commit to `slow_store` if consistent OR if replay-count for that item has exceeded a
   patience threshold (forced slow-path commit, avoiding permanent starvation of genuinely novel
   but consistent-with-nothing-yet facts).
4. NEW self-test additions beyond v5's: (a) schema-consistency score is HIGHER for coherent than
   scrambled mentions on synthetic toy data (mechanism-correctness gate, not the capability
   claim); (b) surprise-ordering actually reorders (a high-surprise synthetic mention is replayed
   before a low-surprise one within the same budget-limited phase); (c) discrete-budget-respected
   (inherited from the certified cell, re-verify it still holds when driven by loop-supplied
   keys/codebook rather than the original cell's synthetic ones).

**Brain metric to judge it on (not just AUC):** in addition to the existing relational-AUC
LOW-slice gain (must beat fast_episodic AND both matched controls, same bar v4/v5 used), add a
**capture-latency / interleaving-retention metric** directly modeled on the certified cell's own
HARD_PASS criterion — does the NEW mechanism retain OLD concepts' AUC (no forgetting, gap vs a
NAIVE/no-consolidation control analogous to the certified cell's 0.913 gap) WHILE acquiring NEW
LOW-slice concepts, simultaneously, under a shared fixed replay budget across concepts (this is
the genuinely novel prediction interleaved replay makes that averaging-based consolidation cannot
even be tested on, since averaging has no shared budget or old/new interleaving to begin with).
This is the brain's actual signature capability (continual acquisition without catastrophic
forgetting) and is a strictly harder, more specific bar than AUC-gain alone.

**Sequencing note:** hold this behind whatever encoder work is currently in flight (per the task's
framing "once the encoder work settles") — this redesign assumes v5's readout + DG key fixes as
given and does not re-open them. If a v6/learned-extraction-head encoder change lands first, this
consolidation redesign should be re-run against THAT frozen encoder, not v2's, following the same
space-consistency discipline v5 established.
