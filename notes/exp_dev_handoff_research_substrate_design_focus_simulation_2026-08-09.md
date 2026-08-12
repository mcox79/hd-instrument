# exp_dev hand-off — research: fleshing the Cowan-4 focus into a simulation engine (pull-in + causal chaining)

**Filed-by:** research sub-agent, 2026-08-09.
**Trigger:** `notes/research_substrate_design_focus_simulation_2026-08-09.md` — USER-requested drill designing
how to flesh the Cowan-4 focus bundle (`hdlab/situation_focus.py`) into a real simulation engine via (1)
associative pull-in of close/relevant content and (2) causal forward-chaining ("what leads to what"), and
diagnosing why the prior `exp_mcscript2_script_chain_predict_gap_fill_v1` chain-prediction probe produced
near-noise signal (bare bag-of-words sentence chaining, no role structure, no causal-link store, no
connection to the focus).

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless of
pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable bands,
context pointers) — exp_dev owns exact implementation (exact fact set, exact threshold values, exact cell
structure, seeds).

## Anchor candidates (rank-ordered)

### 1. Associative-pull-in micro-world probe (primary, do this first — cheapest, reuses every primitive verbatim, no corpus dependency)

**Anchor pointer:** research note section "Staged de-risk sequence -> Stage 1" +
`data/exp_mcscript2_script_chain_predict_gap_fill_v1/metrics.json` (the negative result this stage is
designed to fix the diagnosis for).

**Substrate-product reading:** if this HARD-PASSes, it proves the core retrieval math (iterated attractor
cleanup, salience-gated admission into a bounded focus) discriminates real causal/topical structure from
scrambled structure on typed role-filler content — the missing ingredient the bare-BoW `chain_predict` probe
never had. This unblocks Stage 2 (multi-hop chaining) and Stage 3 (wiring onto real narrative text). If it
HARD-FAILs, it falsifies the central diagnosis of this drill (that representation-shape, not raw
co-occurrence, was the bottleneck) and is the more informative negative result — worth knowing cheaply before
any further build.

**Tier hint:** load-bearing gate for the whole 4-stage program (see research note). A HARD-FAIL here should
STOP the sequence before Stage 2/3 are attempted (cheap-decisive-first ordering) — do not proceed to wiring
onto real narrative text on the strength of "it should still work at scale."

**Why now:** cheapest possible test of the mechanism — every primitive is already built and individually
validated: `hdlab.situation_model_accumulate.CausalLinkRegister` (typed CAUSE/EFFECT chaining, unused since
2026-08-02), `hdlab.event_bundle.EventBundleCodec` + `hdlab.situation_focus.ChunkedFocus` (Cowan-4 bounded
focus, currently WIRED into `situation_reader.py`), `hdlab.cleanup_family.iterative_attractor` /
`hdlab.iterative_attractor.iterative_cleanup` (CA3-style iterated softmax settle, registry status
"WIRED" but only into offline experiment cells — never into the live focus's query path). Only the salience
GATE (a similarity/confidence threshold deciding what gets admitted into the focus) is genuinely new code —
small, ~1 function.

**Design (from the research note, exp_dev owns implementation details):**
1. Hand-author ~25-30 CAUSE->EFFECT facts across 5-6 scenario clusters (same toy-instance style already used
   by the mcscript2 cells — e.g. "cracked egg"->"whisked mixture"->"heated pan"; "clipped leash"->"walked
   dog"->"sniffed grass"). Store the facts' CAUSE/EFFECT links in one `CausalLinkRegister`; store the facts'
   event content (role-filler tuples) in one shared `EventBundleCodec`/`ChunkedFocus`.
2. Pull-in mechanism: seed the focus with a current event from cluster X (via `ChunkedFocus.push` +
   `EventBundleCodec.encode_event`); unbind its role fillers; query the content codebook via
   `iterative_attractor`/`iterative_cleanup` (NOT one-shot `argmax`) to retrieve associated content; apply a
   salience/confidence threshold (exp_dev picks the exact value) to decide admission.
3. MANDATORY SCRAMBLE control: same facts, CAUSE/EFFECT re-paired via a hashlib-seeded deterministic
   permutation (same convention as `exp_mcscript2_script_chain_predict_gap_fill_v1::_deterministic_perm` and
   the already-validated M2 "pairscramble" pattern on the OOV union channel) — same content distribution,
   destroyed causal/associative structure.
4. MANDATORY off-topic probe: query pull-in from a DIFFERENT, unrelated cluster and measure the false-pull-in
   rate (does the salience gate actually suppress irrelevant retrieval, or does it flood indiscriminately).
5. Report: (a) in-cluster correct-retrieval rate (real vs. scramble), (b) off-topic false-pull-in rate,
   (c) the settled-state trace at each iteration step (glass-box inspectability requirement — every pull-in
   decision must be auditable: which candidate, what similarity score, admitted or gated out).

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS:** in-cluster correct-retrieval rate >= 0.70 AND real beats scramble by >= 0.20 absolute AND
  off-topic false-pull-in rate <= 0.15.
- **HARD-FAIL:** real correct-retrieval rate within 0.05 of scramble's (no structure signal — reproduces the
  diagnosed bare-BoW failure even with typed role/causal-link representation) OR off-topic false-pull-in
  rate > 0.40 (gate doesn't discriminate — indiscriminate flooding).
- **MIDDLE_BAND:** everything else.

### 2. Multi-hop causal chaining on the same micro-world (do only if #1 HARD-PASSes)

**Anchor pointer:** research note section "Staged de-risk sequence -> Stage 2."

**Design:** chain `CausalLinkRegister.query_effect_of` 2-3 hops forward from a seed event on the SAME
micro-world #1 built; compare real vs. scramble accuracy at each hop depth.

**Pre-registered bands:**
- **HARD-PASS:** real 2-hop accuracy stays above scramble at every hop AND degrades gracefully (no cliff to
  chance between hop 1 and hop 2).
- **HARD-FAIL:** real collapses to scramble-level by hop 2, OR hop-1 accuracy is at or below anchor #1's
  in-cluster floor (chaining adds nothing beyond single-hop pull-in).

**Why now:** trivial incremental cost once #1's micro-world exists (`query_effect_of` already implemented;
this is a repeated-call wrapper, ~10 lines). Honest caveat: the resonator literature (Frady, Kent, Olshausen
& Sommer 2020) establishes iterated-cleanup-beats-one-shot for FACTORIZATION specifically; the
accuracy-vs-hop-depth degradation curve for multi-hop GRAPH chaining is this drill's own extrapolation, not
directly literature-verified — flag this in the pre-reg.

### 3. Wire onto real narrative text — re-run the mcscript2 gap-fill test through the structured path (do only if #1 AND #2 HARD-PASS)

**Anchor pointer:** research note section "Staged de-risk sequence -> Stage 3" +
`experiments/exp_mcscript2_script_chain_predict_gap_fill_v1.py` (the cell to modify) +
`hdlab/situation_reader.py::_read_causation` (the flat connective-list to replace with a queryable register).

**Design:** replace `situation_reader.py`'s flat connective-adjacency `CausalLink` list with
`CausalLinkRegister`-backed storage+query; replace the bare-BoW `SequenceMatrix` fallback in
`exp_mcscript2_script_chain_predict_gap_fill_v1.py` with `EventBundleCodec` role-filler events +
`CausalLinkRegister` chaining, keeping the SAME staged-decision harness (`PRIMARY_MARGIN_THRESH`,
`compute_primary`, the real/scramble arm structure) so this is a clean ablation — only the fallback
representation changes.

**Pre-registered bands (verbatim, matching the ORIGINAL mcscript2 pre-reg the bare-BoW version missed):**
- **HARD-PASS:** staged accuracy margin over primary-only content-matching >= +0.02 AND fallback accuracy on
  residual > 0.55 AND real beats scramble.
- **HARD-FAIL:** margin <= 0 OR residual accuracy still in/below the [0.45, 0.55] chance band.

**Honest caveat to carry into the pre-reg:** `data/exp_mcscript2_script_chain_predict_gap_fill_v1/metrics.json`
already discloses `text_overlap_acc=0.5859` (commonsense) vs. `majority_acc=0.4565` — the primary
content-matching baseline is unusually strong/dominant on THIS specific corpus. A HARD-FAIL at this stage,
even with a mechanically-correct fix, would not refute the pull-in/chaining mechanism itself (validated
independently at #1/#2) — it would mean this fix doesn't move the needle on THIS benchmark specifically.
Report the two possibilities separately, do not fold into one combined verdict.

### 4. Acquisition-loop wiring to grow the content store (explicitly OUT OF SCOPE for this hand-off — multi-week program, sequenced last)

Not an anchor to ship now. Flagged in the research note as Stage 4: extend
`hdlab.grounding_acquisition_loop`'s FLAG->LIBRARY->CONSOLIDATE->BANK loop (built 2026-08-09, currently
scoped to OOV outcome-verb valence only) to grow the causal-link/concept store at real scale, per the USER's
standing anti-batch-ingest reframe. Only attempt after #1-#3 have validated the retrieval/chaining math is
worth feeding.

## Context pointers (files, not summaries)

- `notes/research_substrate_design_focus_simulation_2026-08-09.md` — full design, diagnosis of the prior
  failure, reuse-vs-build table, all 4 stages, 3 lit-scan lane citations, honest feasibility/capacity read.
- `hdlab/situation_model_accumulate.py` — `CausalLinkRegister` (`add_causal_link`, `query_cause_of`,
  `query_effect_of`), `AccumulateRegister` (base class, validated atom 29609), `RelationRegister` (sibling
  pattern that HARD_PASSed today, 2026-08-09, via `exp_situation_model_relation_ablation_v1` — direct
  precedent for the register-extension approach).
- `hdlab/situation_focus.py` — `ChunkedFocus` (Cowan-4 bounded focus, capacity=4/fanout=2, validated
  graceful-degradation selftest), `FlatFocus` (unbounded contrast arm).
- `hdlab/event_bundle.py` — `EventBundleCodec` (role-slot event encoding, `encode_event`/`query_role_vec`).
- `hdlab/cleanup_family.py` + `hdlab/iterative_attractor.py` — `iterative_attractor`/`iterative_cleanup` (CA3
  softmax settle), `PRIMITIVES` registry.
- `experiments/exp_connectivity_resonator.py` — `resonator_query_khop` (iterated-cleanup-per-hop multi-hop
  retrieval pattern, beats one-shot cleanup on a 50-entity toy knowledge graph; not yet promoted to `hdlab/`).
- `experiments/exp_mcscript2_script_chain_predict_gap_fill_v1.py` +
  `data/exp_mcscript2_script_chain_predict_gap_fill_v1/metrics.json` — the negative result this whole program
  diagnoses and fixes; `_deterministic_perm` is the scramble-control convention to reuse verbatim.
- `hdlab/situation_reader.py` — `_read_causation` (the flat connective-list to replace at Stage 3),
  `_read_events` (the existing `ChunkedFocus`/`EventBundleCodec` wiring pattern to mirror for pull-in).
- `hdlab/grounding_acquisition_loop.py` — the acquisition loop (Stage 4, out of scope for this hand-off).
- `hdlab/event_centrality_coref.py` — `query_memory=True` path (`hd_centrality`): existing precedent for
  querying `ChunkedFocus` content from outside; pull-in is the reverse direction.

## Contract section

- exp_dev owns: exact fact set / scenario-cluster content for the Stage-1 micro-world, exact salience-gate
  threshold value and functional form, exact `iterative_attractor` hyperparameters (temp, max_steps), exact
  cell/file naming, exact seed handling.
- Research (this hand-off + parent note) fixes: the falsifiable HARD-PASS/MIDDLE_BAND/HARD-FAIL bands per
  stage, the mandatory scramble control (hashlib-seeded CAUSE/EFFECT re-pairing, not optional), the mandatory
  off-topic false-pull-in-rate measurement (Stage 1) and the cheap-decisive-first sequencing (do not attempt
  Stage 2/3 if Stage 1 HARD-FAILs), the glass-box/no-LLM-at-inference invariant, and the requirement that
  every pull-in/inference step be inspectable (which candidate, what score, admitted or gated).

## Autonomy declaration

exp_dev decides the exact micro-world content, exact gate threshold/form, exact cell/file naming, and exact
seed count for Stage 1. The falsifiable bands, the mandatory scramble control, the mandatory off-topic probe,
and the cheap-decisive-first stage ordering are NOT exp_dev's to loosen or drop without flagging the change
explicitly in the pre-reg.
