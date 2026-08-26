# SOLVER running notes — the_consolidated_cortical_store_is_written_but_never_read

(working notes; the deliverable is SOLVED.md. Kept so findings survive compaction.)

## VERIFIED PREMISE (disk, this session) — the brief is FAITHFUL
- Ablation reproduced from `data/exp_substrate_end_to_end_readout_v1`: consolidation-ablated held-out
  read-out == control (0.00667==0.00667 seed 20260819; 0.0033==0.0033 seed 7). `definitions`-ablated
  also identical. Only EPISODIC ablation zeros it (→0.0). The consolidated store is written, never read.
- Path traced: `substrate.recall_sentence → recall` = EPISODIC (CA3 + inverted index). `recall_cortical`
  exists but is OFF-PATH; reads the sparse exact-fact `consolidated()` in a first-order context/spoke
  space; never touches `continual.py`'s replay W.
- Real consolidated store (3150 sents → 148 facts, all GROUNDED_MEANING term→free-text gloss): heavy
  noise ("aire→the capital of argentina", "april→the diamond"). Some real overlap (atom←atomic/neutron
  /nucleus/proton; negative←charge/ion/positive) buried in shared-definition-word artifacts.

## PRIOR WORK (credited, NOT re-run)
- `cortical_read_has_no_scored_path` (REFUTED): cortical CLOZE read loses to first-order counting.
- `cortical_read_never_tested_where_it_matters` (PARTIAL): on truly-UNSEEN (never-cooc) NO self-built
  space clears the floor; only supplied GloVe does; on SEEN a self-built PPMI+SVD (LSA) EQUALS GloVe and
  beats counting ~2:1. Strategy gap note: teaching/distillation > concatenation (filed separately).
- NEITHER ran (a) the live EPISODIC arm as the "wrong memory" comparison, nor (b) the ablation-bites
  positive control. Those + the CLS read decomposition are my distinct contribution.

## RESULTS SO FAR (smoke, seed 20260826)
v1 (`exp_cortical_store_read_path_v1`): the memorised wall reproduced — EPISODIC SEEN exact-key 0.975@1
vs HELD_OUT 0.100@10. CORTICAL_OVERLAP (LSA cosine) 0.306 beats episodic ~3x; ablation bites (0.306 vs 0
consolidation-off). Counting floor 0.519 (mostly seen-cooc held-out) still wins.

v2 (`exp_cortical_replay_completion_v2`): the CLS read decomposed by operation (concept code = PPMI+SVD;
consolidation = `continual.replay_cycle`; read = `cleanup_family.iterative_attractor`). @10 pess-lo:
  in_domain  EPI 0.100 OVERLAP 0.306 ASSOC 0.194 COMPLETE 0.075 | floor 0.525 twin 0.150
  domain     EPI 0.019 OVERLAP 0.100 ASSOC 0.025 COMPLETE 0.056 | floor 0.287 twin 0.138
  domain UNSEEN-cooc: best COMPLETE 0.037 vs floor 0.113 → clears=False; beats_epi=False
  replay vs no-replay (assoc @10): 0.256 vs 0.250 (marginal in a linear associator — expected).

## KEY REALIZATION (the brain-faithful ops LOST — diagnose, don't stop)
The MORE brain-faithful read ops made it WORSE: attractor COMPLETE (0.075) < associative ASSOC (0.194)
< cosine OVERLAP (0.306), COMPLETE near the info-free twin. Cause = HUB COLLAPSE: a dense Hebbian
associator W=Σφ(c)x_cᵀ read y=Wx_q=Σφ(c)(x_c·x_q) is dominated by high-frequency/central concepts, and
the attractor then settles onto those hubs. This is audit DEVIATION #4 (dense where cortex is
sparse+graded) meeting the read — the brain's cortical attractor works because codes are SPARSE (~2%)
and lateral INHIBITION / divisive normalization prevents hub domination. Concluding "the attractor read
loses" WITHOUT fixing sparsity/inhibition would be the USER-08-11 error (weak impl → "impossible").

## NEXT (precise brain part): SPARSITY + INHIBITION on the cortical read
v3: k-WTA sparse concept codes + divisive normalization on the associative read/attractor. Test whether
COMPLETE_SPARSE beats OVERLAP and approaches the floor. If yes → the read op IS the lever once coded
brain-faithfully (deviation #4 is load-bearing on the read). If it still ties cosine → the read op is
not the lever; the CONTENT/CODE is (data-starved self-built, per priors) → the brief's fork (B).

## FORK STATUS (brief §7)
- PATH: reading the store (overlapping space) beats the episodic path on transfer + ablation bites →
  the read-path defect is real and fixable. Leaning (A) on the PATH half.
- CONTENT: no self-built arm clears the counting floor on unseen-cooc (priors + mine) → leaning (B) on
  the "does it beat the floor" half. Synthesis likely: path is necessary but content/code is the wall;
  the brain-faithful read needs sparse+inhibited codes AND transfer-bearing consolidated content.

## FULL-SCALE (8550 read, 298 concepts, 700 items) — in_domain seed 20260826
@10 pess-lo: EPI 0.046 OVERLAP 0.487 ASSOC_S 0.434 PARTIAL_S 0.084 COMPLETE_S 0.076 HAMMING_S 0.143 |
floor(COOC) 0.519 twin 0.144. So cortical read (cosine OR sparse-inhibited) beats the episodic path ~10x
and beats the twin (cue-specific), but loses to counting in-domain (seen-cooc heavy). Attractor arms
collapse (0.076-0.084). UNSEEN-cooc in-domain only 60 items (underpowered; domain route powers it).

## CONVERGENCE (read op) — met the SOLVER "converged" bar for THIS brief's core
- Brain mechanism identified + built + tested: CLS cortical read = sparse(k-WTA)+inhibited(freq-norm
  prototype) graded associative read; attractor completion (iterative_attractor) tested.
- Precise findings, witnessed (verification/test_cortical_store_read_path.py, WITNESS PASS):
  (1) hub collapse of the dense freq-summed associator; sparse+inhibited prototype fixes it (deviation
      #4 load-bearing on the read). (2) the attractor RE-INTRODUCES hub bias (settles over concept-code
      geometry; a central hub jumps rank 2->0) -> full/partial completion HURTS pool-ranking; the
      faithful "which concept" read is the GRADED population read, not a settled attractor. (3) metric
      fails safe. (4) ablation by construction (empty pool -> 0; episodic invariant).
- Honest boundary: on truly-UNSEEN cooc, NO cortical arm beats its own info-free twin -> no cue-specific
  transfer signal there (content/data wall), reconciling the two priors.

## VERDICT (brief fork) — BOTH, precisely
(A) PATH half: reading the store brain-faithfully beats the episodic path ~10x on transfer + beats the
    twin (in-domain) + ablation bites -> the read-path defect is REAL and fixable; the faithful read op
    NEEDS deviation-#4's sparse+inhibited fix. (B) FLOOR half: no self-built cortical read beats
    first-order counting on held-out, and none beats its twin on unseen -> the CONSOLIDATED CONTENT/CODE
    is the residual wall (data-bound; noisy glosses), which is the brief's own outcome-(B) redirect to
    "what gets consolidated" + multimodal/supplied code (reader_meaning_channel / teach-don't-concat /
    supply-distributional-spoke lanes, NOT this brief).

## PROPOSED WIRING (for SOLVED.md; strategy lands) — the CLS matched pair
Route by recollection confidence (the p2 dg_ca3 gate / episodic CA3 completion overlap): confident
exact-key -> EPISODIC; else -> the sparse+inhibited CORTICAL read. Per-regime dominance flip (EPI 0.975
exact-key vs cortical 0.43>>EPI 0.046 held-out) makes this beat either single system on a mixed
population. NOT a floor-beater on transfer (content wall). This is the cortical complement to the
integrated p2 (which routed episodic-vs-familiarity only).

## AUDIT UPDATE candidates (BRAIN_FOUNDATIONAL_AUDIT.md)
- Deviation #3 (wrong read): reading the consolidated store DOES beat the episodic path on transfer
  (~10x) and ablation can be made to bite -> the read-path fix is real; but it does not clear the
  counting floor -> the standing "memorises-not-transfers" wall is NOT dissolved by the read alone;
  content is the residual. - Deviation #4 (dense vs sparse) is LOAD-BEARING ON THE READ (measured):
  sparse+inhibited rescues the associative read from hub collapse (0.025->0.156 domain smoke).
- New deviation: full/partial ATTRACTOR completion HURTS pool-ranking (re-introduces concept-code hub
  bias); the faithful ranking read is graded, attractor is for recognition not ranking.

## FIDELITY DRILL (USER: drill ever finer during implementation) — swept the convenience defaults
2200-read diagnostic, held-out hit@10, sweeping k-WTA sparsity x attractor temp/steps:
  keep=0.02 graded=0.344 | attr(t1..64,s8)=0.15-0.19  attr(t16,s1)=0.188
  keep=0.15 graded=0.381 | attr=0.13-0.15
  keep=1.00 graded=0.388 | attr=0.12-0.18
FINDINGS: (1) "attractor completion hurts pool-ranking" is ROBUST across temp {1,4,16,64} and steps
{1,8} and sparsity {2%..100%} -- NOT a param artifact (witnessed: hub promoted at every temp). (2)
cortical ~2% sparsity does NOT help the GRADED read (0.344@2% vs 0.388@100%); sparsity mattered only to
rescue the ASSOCIATIVE read from hub collapse. So imposing 2% on the graded read would be false
brain-fidelity theater -- the faithful RANKING read is the graded population match, sparsity-robust,
attractor is for RECOGNITION not ranking. This is the earned (not default) fidelity conclusion.
Least-faithful remaining part = the CODE (offline SVD, cosine, unimodal) = the content wall = other lanes.

## DEEPENING TICK RESULT (deviation #5: is interleaved replay the missing lever?) -- CLOSED
v3 (`exp_cortical_interleaved_online_code_v3`) builds the overlapping code by the ACTUAL CLS PROCESS
(online SGNS over the read stream + interleaved REPLAY of past sentences), vs batch SVD, no-replay
ablation, seen-cooc POSITIVE CONTROL. Smoke: the online learner FAILS the positive control (0.174 vs
batch 0.356 @10 on seen-cooc, unchanged at 6 epochs) -> UNDERTRAINED at our data scale; cannot claim
online==batch, so per USER-08-11 I do NOT. The safe, tested claim: the interleaved PROCESS is even MORE
data-hungry than batch and shares batch's data-bound ceiling (SGNS~SVD-of-shifted-PPMI). So being more
faithful to the consolidation PROCESS is a FALSE lever when the constraint is the DATA the process needs.
"Leave the family, ask the biology": for a zero-experience concept the brain uses the HIPPOCAMPUS (which
we have), not cortical magic. Residual = lifetime-scale experience (priors' GloVe crosses) = other lanes.

## CONVERGED -- brain-mechanism bar MET; deepening cron DELETED (job bdc25d9f)
Identified the brain's operation (CLS cortical read = sparse+inhibited graded associative; consolidation
= interleaved replay), replicated + tested BOTH (read op v2 + drill; process v3), and gave a SPECIFIC
TESTED reason the residual transfer can't be crossed in-scope (data/scale-bound from two angles; not
"impossible" -- supply crosses it). SOLVED.md = PARTIAL, witness PASS, ledger 0 malformed.

## GOVERNANCE
- Announced in dispatch_queue as solver_cortical_store. Deepening cron DELETED (converged).
- Writes only experiments/ + verification/ + this problem folder. hdlab/ untouched (Q111). Awaiting owner
  verdict (OWNER_NOTES owner_verdict: DONE) before strategy integrates.
