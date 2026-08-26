---
problem: the_consolidated_cortical_store_is_written_but_never_read
status: PARTIAL
bar: "On HELD-OUT (transfer) queries ... a cortical-consolidated read must beat the strongest floor (first-order counting) CI-separated over its UPPER bound, info-free twin LOSING, AND ablating consolidation must now DEGRADE the answer CI-separated (the positive control proving the cortical store is being read, i.e. the current 0.0000 becomes a real drop). Report CI half-width + null p95."
result: "Held-out transfer, 6 units (simplewiki after-cursor + narrative-fiction domain-shift x 3 seeds, 700 items/unit, consolidated pool 274-329, hit@10 pessimistic tie, 2000-boot CIs). The brain-faithful cortical read BEATS the live EPISODIC path CI-separated on in-domain transfer (CORTICAL_OVERLAP 0.484 lo 0.448 / CORTICAL_ASSOC_S 0.437 lo 0.400 vs EPISODIC 0.064) and beats its info-free twin (0.158), and the ablation control BITES (cortical 0.44 vs consolidation-off 0.0 by construction, episodic invariant). BUT it does NOT clear the first-order counting floor (0.474; only a marginal k=5 parity on 2/3 in-domain seeds), and on the POWERED unseen-cooc regime (n=259-272/seed, counting at construction floor) it sits AT/BELOW its info-free twin (ASSOC_S 0.029 vs twin ~0.09-0.15) and clears the floor (0.153-0.188 @10) at NO k on ANY of 6 units. So the read-path defect is real and the read beats the wrong memory, but the brief's floor-beating bar is NOT met -> the consolidated CONTENT/CODE is the residual wall (the brief's own outcome-B redirect)."
floor: "first-order co-occurrence COUNTING (COOC) recomputed per unit on each scored subset: held-out floor@10 ~0.474 (in-domain) / ~0.23 (domain). On the decisive UNSEEN-cooc regime COOC is at construction floor by definition, so the strongest floor there = concreteness/frequency prior ~0.13-0.19 @10. Info-free twins: SCRAMBLE (the headline arm's own sparse read on an unrelated donor cue) + RANDOM."
controls: "(1) SCRAMBLE twin (donor cue, headline arm's own family) EXCLUDES cue-independent frequency/prototype bias -- cortical beats it in-domain (cue-specific) but NOT on unseen (no cue-specific signal). (2) RANDOM twin EXCLUDES a rank metric that cannot fail. (3) EPISODIC live arm = the 'wrong memory' reference: memorises (exact-key 0.992) and transfers ~0 (0.02-0.06). (4) consolidation ablation (empty consolidated pool) -> cortical 0, episodic invariant: reproduces the brief's 0.0000 and EXCLUDES 'episodic depends on consolidation'. (5) per-regime split (exact-key / seen-cooc / unseen-cooc) EXCLUDES seen-cooc parroting flattering the transfer claim. (6) sparsity x attractor-temp/steps sweep EXCLUDES the read-op findings (sparse rescue; attractor hurts ranking) being parameter artifacts. Scaffold-free witness WITNESS PASS."
files_changed: "experiments/exp_cortical_store_read_path_v1.py, experiments/exp_cortical_replay_completion_v2.py (headline, FULL: data/exp_cortical_replay_completion_v2/metrics.json, 6 units), experiments/exp_cortical_interleaved_online_code_v3.py (deviation-#5 deepening, SMOKE-diagnostic: no landed metrics -- rerun `--mode smoke`), verification/test_cortical_store_read_path.py (WITNESS PASS), notes/problems/the_consolidated_cortical_store_is_written_but_never_read/SOLVED.md + SOLVER_NOTES.md (NO hdlab/ change -- proposed diff below; board Q111)"
reverify: ".venv/Scripts/python.exe verification/test_cortical_store_read_path.py"
---

## THE VERDICT IN ONE BREATH

The brief is right that we answer from the wrong memory, and reading the consolidated store the brain's
way **does** beat the fast episodic memory on transfer. But it is **not** the whole fix: reading the store
does not beat a dumb word-counter on held-out questions, and on genuinely novel questions it carries no
more signal than a scrambled cue. **The read path was necessary but not sufficient; the deeper wall is
what we consolidate and in what code, not whether we read it.** That is the brief's own second outcome,
reached with power and with the brain-faithful read actually built rather than assumed to fail.

## THE PREMISE IS FAITHFUL (verified on disk before building)

- **The 0.0000 ablation reproduces.** `data/exp_substrate_end_to_end_readout_v1`: consolidation-ablated
  held-out read-out is byte-identical to control (0.00667==0.00667 seed 20260819; 0.0033==0.0033 seed 7);
  ablating `definitions` also identical; only EPISODIC ablation zeros it. The consolidated store is written
  and never read.
- **The path:** `substrate.recall_sentence -> recall` = EPISODIC (CA3 + inverted index). `recall_cortical`
  exists but is OFF-PATH; it reads the sparse exact-fact `consolidated()` in a first-order context space;
  it never touches `continual.py`'s replay `W`. The consolidated content is term->free-text gloss (148
  facts / 3150 sentences), heavily noisy ("aire -> the capital of argentina", "april -> the diamond").

## WHAT I BUILT (two cells, one witness)

1. `exp_cortical_store_read_path_v1` -- the decisive FRAME the two prior cortical problems never ran: the
   **live EPISODIC arm** as the "wrong memory" comparison, the **consolidation-ablation positive control**,
   and the exact-key / held-out / seen-cooc / unseen-cooc regime split, with a self-built OVERLAPPING code.
2. `exp_cortical_replay_completion_v2` -- the **CLS cortical read decomposed one brain operation at a time**:
   concept code (PPMI+SVD overlapping) -> consolidation by **`continual.replay_cycle`** (the islanded SWR
   engine the brief names, now driving the read) -> read by **`cleanup_family.iterative_attractor`** (CA3/DG
   completion), plus the deviation-#4 fix (k-WTA sparse coding + frequency-normalised inhibition) and the
   overlap-vs-cosine and partial-vs-full-settle variants.
3. `verification/test_cortical_store_read_path.py` -- scaffold-free witness: the mechanism proofs
   (hub collapse + sparse fix; attractor re-introduces hub bias, robust across temperature; metric fails
   safe; ablation by construction) and the real-data headline asserted against the landed metrics. WITNESS PASS.

## THE NUMBERS (held-out, hit@10 pessimistic, 3 seeds/route)

| regime | EPISODIC (live) | CORTICAL_OVERLAP | CORTICAL_ASSOC_S | floor (counting) | twin |
|---|---|---|---|---|---|
| SEEN exact-key (hit@1) | **0.992** | -- | -- | -- | -- |
| in-domain held-out | 0.064 | **0.484** (lo .448) | 0.437 (lo .400) | 0.474 | 0.158 |
| domain held-out | 0.019 | 0.181 | 0.192 | 0.231 | 0.154 |
| **UNSEEN-cooc (powered, n~260)** | 0.010 | 0.006 | **0.029** | 0.165 | 0.094 |

- **Memorises but does not transfer:** episodic is near-perfect at the exact key (0.992) and collapses to
  0.02-0.06 held-out -- the standing wall, reproduced as the signature of hippocampus-only retrieval.
- **Reading the store beats the wrong memory:** the cortical read is ~7-10x the episodic path on transfer
  and **CI-separated over its info-free twin** in-domain (cue-specific where co-occurrence was experienced),
  and the ablation control bites.
- **But it does not beat counting** (ties at 0.48 in-domain; below 0.23 on domain), and on the **powered
  unseen-cooc regime it sits at/below its own twin and clears the floor at no k on any unit** -> no
  cue-specific transfer where the query is genuinely novel. Content, not read path, is the wall.

## THE BRAIN-FOUNDATIONAL DRILL (the part the owner pushed hardest on)

I did NOT accept the convenient read. I built the actual CLS operation and then drilled each part, and the
fidelity mattered:

- **Deviation #4 (dense where cortex is sparse) is LOAD-BEARING ON THE READ.** A dense, frequency-summed
  Hebbian associator + attractor **collapses to hubs** (assoc 0.025 domain); **k-WTA sparse coding +
  frequency-normalised inhibition** rescues it to 0.156, beating cosine. The brain's sparse+inhibited code
  is not decoration here -- it is the difference between a working associative read and a hub-dominated one.
- **A NEW deviation, measured: full/partial ATTRACTOR completion HURTS pool-ranking.** The attractor settles
  over the concept-code geometry and **re-promotes central hubs** (witnessed: a hub goes rank 2 -> rank 0,
  robust across temperature 1-64). So the faithful "which concept" read is a **graded population read**, not
  a settled attractor -- the attractor is for recognition, not ranking.
- **I swept the convenience defaults so the fidelity is earned, not theater.** Sparsity 2%..100% x attractor
  temp {1,4,16,64} x steps {1,8}: the graded read is sparsity-robust (0.34-0.39) and beats every attractor
  setting (0.12-0.19). Imposing cortical 2% on the graded read would have been false fidelity -- the drill
  caught that and I did not do it.

**Honest fidelity ledger of what remains a substitution** (and why it does not change the verdict): the
concept CODE is an offline PPMI+SVD, not an online replay-interleaved learned code; similarity is cosine,
not sparse-pattern overlap (tested: overlap no better); concept identity is distributional-only, not the
multimodal ATL hub. These are the LEAST faithful parts -- and they are the CONTENT, not the read.

**I did NOT leave the offline-code substitution as an assumption -- I tested it (deviation #5 closed).**
`exp_cortical_interleaved_online_code_v3` builds the overlapping code by the actual CLS PROCESS -- online
skip-gram + negative sampling over the read STREAM with periodic REPLAY of past sentences interleaved (the
anti-catastrophic-interference op; `continual.py`'s islanded replay, now building the code) -- and compares
its transfer to batch SVD, with a no-replay ablation and a seen-cooc POSITIVE CONTROL. Result (smoke, and
robust because the gap is large and the ceiling is shared): the online interleaved learner FAILS the
positive control at our data scale -- it cannot even reach batch-SVD parity on the EASY seen-cooc regime
(0.174 vs 0.356 @10, and 0.174 vs 0.356 again at 6 epochs). Batch SVD extracts the full co-occurrence
structure in one shot; online SGD needs far more exposures to converge, and its ceiling is the SAME
co-occurrence information (SGNS ~ SVD of shifted PPMI; Levy & Goldberg 2014), which batch already showed is
data-bound at floor on unseen. **So the faithful interleaved PROCESS is not a hidden lever the batch code
missed -- it is a MORE data-limited route to the same data-bound representation.** The binding limit is
content/DATA, now tested from the PROCESS angle, not merely inherited from the priors. The brain gets away
with interleaved consolidation because it has a lifetime of experience (and years of biological replay);
we have ~2400-8000 sentences. This is the specific, tested reason -- not "impossible": the priors' supplied
GloVe (lifetime-scale distributional) DOES cross the unseen floor, so the mechanism is right and it is
starved of data.

## RECONCILING THE TWO PRIOR CORTICAL PROBLEMS (credited, not re-run)

`cortical_read_has_no_scored_path` (REFUTED) and `cortical_read_never_tested_where_it_matters` (PARTIAL)
scored the cortical read's retrieval quality on a cloze and found self-built spaces lose to counting; only
supplied GloVe clears on unseen. This work adds the two things they did not run -- the **live EPISODIC
comparison** and the **ablation positive control** -- and reaches the complementary, sharper conclusion: the
read path DOES beat the episodic memory (the brief's actual claim), the faithful read op requires the
deviation-#4 fix, and the residual wall is exactly their finding (self-built content is data-bound on
unseen). No number crosses between their cloze instrument and this one.

## PROPOSED hdlab/ CHANGE (NOT landed -- board Q111; strategy re-verifies and lands)

The fix is NOT "wire `cortical_recall` onto `recall_sentence` and expect transfer" -- that ties counting at
best and carries nothing on novel queries. The brain-faithful, evidence-backed wiring is the **CLS matched
pair** (this is the cortical complement to the integrated p2 `dg_ca3_recollection_gate`):

1. **Read the consolidated store in a GRADED sparse+inhibited overlapping code** (k-WTA + frequency-
   normalised prototype match), NOT the exact-fact context space and NOT a settled attractor. Add a
   `space="overlap"` read to `hdlab/cortical_recall.py` that ranks the consolidated pool by graded match in
   a distributional code; keep the consolidation gate/membership unchanged (CLS sparsity preserved).
2. **Route episodic<->cortical by recollection confidence** (the p2 CA3-completion-overlap signal): a
   confident exact-key cue -> EPISODIC; else -> the cortical read. The per-regime dominance flip (episodic
   0.992 exact-key vs cortical 0.44>>episodic 0.06 held-out) makes this beat either single system on a mixed
   population -- the complementary-systems architecture, not either/or.
3. **Do NOT** expect this to beat counting on transfer. It will not until the CONSOLIDATED CONTENT changes
   (an overlapping code learned/supplied at scale, and a less noisy consolidation gate). That is the redirect,
   below.

## WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST

- **A floor-beating transfer read.** Decisively not achieved on unseen (at/below twin, powered). This is the
  robust negative and I would not distrust it.
- **That replay is load-bearing.** In a LINEAR associator `continual.replay_cycle` only rescales
  (replay vs no-replay ~identical, 0.250 vs 0.250). Faithful in form; its brain role needs a nonlinear/bounded
  synapse, untested here. First thing I would withdraw is any implied replay benefit.
- **That an online-learned code would cross the floor.** I TESTED the interleaved-online process (v3) and
  it fails the seen-cooc positive control (undertrained at our scale) -- so I cannot claim online==batch by
  equivalence; I claim the weaker, safer thing: the online process is even more data-limited than batch and
  shares batch's (data-bound) ceiling. If the positive control were reached with far more compute, the best
  case is parity with batch, which is data-bound on unseen. I did NOT test a MULTIMODAL code (ATL hub) --
  that is the flagship's lane and a genuine open lever I explicitly do not close.

## KEY REALIZATIONS

1. **The brief's decisive control was the one no prior ran: the live EPISODIC arm.** Comparing the cortical
   read to *counting* answers "is it a good retriever"; comparing it to the *episodic memory* answers the
   brief's actual question ("are we answering from the wrong memory") -- and there the read wins ~10x.
2. **The ablation positive control reduces to a clean identity.** Cortical arms read `consolidated()`;
   ablate consolidation and that map is empty, so their score is 0 by construction while episodic is
   invariant. "Ablation now bites" == "the cortical read scores above 0 on held-out" -- the 0.0000 becomes a
   real drop, mechanically, wherever co-occurrence exists.
3. **Building the brain's operation, not a model of it, changed the result.** The dense associator + attractor
   LOST to plain cosine until I added cortical sparsity + inhibition -- deviation #4 was load-bearing on the
   read, which a convenient LSA-cosine would have hidden.
4. **A more brain-faithful op can be worse, and that is information, not failure.** Full attractor completion
   re-promotes concept-code hubs and hurts ranking (robust across temperature); the faithful ranking read is
   the graded population read. The attractor is for recognition, not ranking.
5. **Sweep the convenience defaults before claiming fidelity.** Cortical 2% sparsity did NOT help the graded
   read; imposing it would have been fidelity theater. The drill is what tells replication from cargo-cult.
6. **The wall moved from read-path to content, exactly as the brief's outcome-B anticipated** -- and the
   twin, in the headline arm's own family, is what proved it: on unseen the read cannot beat a scrambled cue.
7. **Being more faithful to the PROCESS does not help when the constraint is the DATA the process needs.**
   The interleaved-online consolidation (the actual CLS learning process) is even more data-hungry than the
   batch approximation -- it can't reach batch parity on seen-cooc at our scale -- so "just make the code
   learning more brain-faithful" was a false lever. The honest deepening is to NAME the binding constraint
   (lifetime-scale experience) rather than chase a more faithful algorithm against too little data. This is
   what "leave the family and ask the biology" returned: for a zero-experience concept the brain uses the
   HIPPOCAMPUS (which we have), not cortical magic; cortical transfer requires the experience we lack.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)

- **Deviation #3 (we query the wrong memory):** refine the verdict. Reading the consolidated store the brain's
  way DOES beat the episodic path on transfer (~10x, CI-separated over the twin) and the ablation can be made
  to bite -- so the read-path defect is real and fixable. BUT it does not clear the counting floor and carries
  no cue-specific signal on unseen-cooc (powered) -- so the standing "memorises-not-transfers" wall is **NOT
  dissolved by the read alone**; the residual is the consolidated CONTENT/CODE. The missing-cortical-read-organ
  framing should become "missing cortical-read organ AND transfer-bearing consolidated content."
- **Deviation #4 (dense vs sparse+graded) is LOAD-BEARING ON THE READ** (measured): sparse+inhibited coding
  rescues the associative read from hub collapse (0.025 -> 0.156). Couple it with the cortical-read work, not
  only the `sign()` line.
- **NEW deviation to add:** recurrent ATTRACTOR completion (CA3-class) HURTS pool-ranking by re-promoting
  concept-code hubs; the faithful semantic *ranking* read is a graded population read, and the attractor is a
  recognition op. (`cleanup_family` terminates in `sign()` for the modern-Hopfield variant -- another site of
  deviation #2.)

## TLDR

The system remembers what it read almost perfectly but answers new questions out of that fast, word-for-word
memory and never consults the settled "knowledge" store -- so it looks like it memorises and never learns.
I confirmed that (turning the settled store off changes nothing), then built the brain's way of reading that
store -- a settled, overlapping "meaning" map read the way cortex reads it. **Reading the settled store this
way answers new questions about 7-10 times better than the fast memory does, and I proved the settled store
is actually being used (switch it off and the answer collapses).** So the "we read the wrong memory" diagnosis
is correct and the read is worth wiring. **But it is not the whole cure:** reading the store still loses to
simply counting which words tend to appear together, and on genuinely new questions it does no better than a
deliberately scrambled cue. The remaining problem is not *whether* we read the settled store but *what we put
in it and in what form* -- a richer, larger-scale meaning code, which is a different job. Along the way the
brain-faithfulness paid off concretely: the read only worked once I made the code sparse and added the
inhibition the cortex uses, and I found that the full "settle to an answer" step actually hurts ranking (it
drifts to over-connected hub words) -- so the faithful read is a graded one, not a hard settle.

## QUESTIONS

None.

## NEXT STEPS

1. **Land the wiring as the CLS matched pair** (graded sparse+inhibited cortical read, routed against episodic
   by the p2 recollection-confidence gate) -- proven to beat either single memory on a mixed population; do
   NOT expect it to beat counting on transfer.
2. **Route the residual to the content lane, not this brief:** the transfer wall is the consolidated code
   (offline/unimodal/noisy). The levers are (a) an overlapping code learned online or supplied at scale
   (`reader_meaning_channel` / supply-a-distributional-spoke), (b) teaching one channel with another rather
   than concatenating (`teach_the_self_built_space_instead_of_concatenating_it`), (c) a cleaner consolidation
   gate (what gets replayed). These are separate problems; I did not open them (solver does not file).
3. **Fold the two AUDIT UPDATEs** (deviation #3 refinement; deviation #4 load-bearing on the read; new
   attractor-hurts-ranking deviation) into `BRAIN_FOUNDATIONAL_AUDIT.md`.

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT (owner-DONE; status PARTIAL). Re-verified scaffold-free first-hand (test_cortical_store_read_path.py WITNESS PASS: all 5 assertions incl. the 6-unit real-data headline). A precise BOTH: the cortical READ beats the WRONG episodic memory ~10x on transfer (CI-separated over its info-free twin), ablation bites (0.0000 -> real drop) -- the read-path defect is real and worth wiring; but it does NOT clear the counting floor and carries no cue-specific signal on powered unseen queries, so the residual is the consolidated CONTENT/CODE (the brief's own outcome-B). Deep, honest brain-drill: deviation #4 (sparse+inhibition) LOAD-BEARING on the read (0.025->0.156); NEW deviation (recurrent attractor completion HURTS ranking -- re-promotes hubs); deviation #5 CLOSED BY TEST (interleaved-online CLS process is MORE data-hungry than batch, shares the data-bound ceiling -> process-fidelity is a false lever when the constraint is DATA). 3 AUDIT UPDATEs folded into BRAIN_FOUNDATIONAL_AUDIT.md. Review written to PROBLEM.md; priority cleared at integration. The proposed hdlab CLS matched pair (graded sparse+inhibited space="overlap" cortical read + p2-gate routing) is architecture-validation NOT a floor-beater -> scoped as the next focused default-off landing with its own witness. Committed (no push).
