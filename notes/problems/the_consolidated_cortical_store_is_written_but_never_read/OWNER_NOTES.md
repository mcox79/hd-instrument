---
owner_verdict: DONE
---

=====================================================================================
SUBMISSION -- SOLVER PROBLEM: the_consolidated_cortical_store_is_written_but_never_read
Status: PARTIAL  (awaiting owner verdict -> strategy re-verify + integration)
Reverify (scaffold-free, writes nothing landed):
  .venv/Scripts/python.exe verification/test_cortical_store_read_path.py   -> WITNESS PASS
Ledger: 0 malformed. All writes confined to experiments/, verification/, and the
problem folder. hdlab/ untouched (board Q111) -- proposed diff below is NOT landed.
=====================================================================================

THE PROBLEM (plain)
  The system remembers what it read almost perfectly but answers new questions out of the
  FAST, word-for-word "sketchpad" memory and NEVER consults the settled long-term
  "knowledge" store it works to build. Proof: switch the settled store off and the answers
  don't move at all (0.0000). So it looks like it memorises and never learns -- which is the
  brain's fast (hippocampal) memory doing a job that belongs to the slow (cortical) one.

THE BAR (verbatim, PROBLEM.md sec 7)
  "On HELD-OUT (transfer) queries ... a cortical-consolidated read must beat the strongest
  floor (first-order counting) CI-separated over its UPPER bound, info-free twin LOSING, AND
  ablating consolidation must now DEGRADE the answer CI-separated (the positive control
  proving the cortical store is being read, i.e. the current 0.0000 becomes a real drop)."

VERIFIED ON DISK FIRST (the brief is faithful)
  * 0.0000 ablation reproduced (data/exp_substrate_end_to_end_readout_v1): consolidation-off
    held-out read-out is byte-identical to control (0.00667==0.00667 seed 20260819); only
    EPISODIC ablation zeros it.
  * Path traced: substrate.recall_sentence -> recall = EPISODIC (CA3 + inverted index).
    recall_cortical exists but is OFF-PATH; reads the sparse exact-fact consolidated() pool
    in a first-order context space; never touches continual.py's replay W.
  * The consolidated content is term->free-text gloss (148 facts / 3150 sentences), heavily
    noisy ("aire -> the capital of argentina", "april -> the diamond").

-------------------------------------------------------------------------------------
THE VERDICT: a precise BOTH (PARTIAL) -- the read path is real and fixable, the wall is content
-------------------------------------------------------------------------------------
Held-out transfer, 6 units (simplewiki after-cursor + narrative-fiction domain-shift x 3 seeds,
700 items/unit, consolidated pool 274-329, hit@10 pessimistic tie, 2000-boot CIs):

  regime                  | EPISODIC(live) | CORTICAL_OVERLAP | CORTICAL_ASSOC_S | floor(count) | twin
  SEEN exact-key (hit@1)  |   0.992        |   --             |   --             |   --         |  --
  in-domain held-out @10  |   0.064        | 0.484 (lo .448)  | 0.437 (lo .400)  |   0.474      | 0.158
  domain held-out @10     |   0.019        | 0.181            | 0.192            |   0.231      | 0.154
  UNSEEN-cooc @10 (n~260) |   0.010        | 0.006            | 0.029            |   0.165      | 0.094

  (A) PATH half -> validated. The episodic path MEMORISES (exact-key 0.992) and transfers
      almost nothing (0.02-0.06). Reading the store the brain's way beats that WRONG MEMORY
      ~7-10x on transfer and is CI-separated over its info-free twin in-domain (cue-specific
      where co-occurrence was experienced). The ablation control BITES (cortical 0.44 vs
      consolidation-off 0.0 by construction; episodic invariant -- the 0.0000 becomes a real
      drop). So the read-path defect is real and worth wiring.
  (B) FLOOR half -> not met; content is the wall. The read does NOT clear first-order counting
      (ties 0.48 in-domain; below 0.23 on domain), and on the POWERED unseen-cooc regime
      (counting at construction floor) it sits AT/BELOW its own info-free twin and clears the
      floor at NO k on ANY of 6 units. No cue-specific transfer where the query is genuinely
      novel -> the consolidated CONTENT/CODE is the residual wall (the brief's outcome-B
      redirect), reconciling the two prior cortical problems.

CONTROLS (each excludes something)
  * SCRAMBLE twin (headline arm's OWN family, donor cue): EXCLUDES cue-independent frequency/
    prototype bias -- cortical beats it in-domain (cue-specific) but NOT on unseen.
  * RANDOM twin: EXCLUDES a rank metric that cannot fail.
  * EPISODIC live arm: the "wrong memory" reference (memorises, transfers ~0).
  * consolidation ablation (empty pool -> cortical 0, episodic invariant): reproduces 0.0000.
  * per-regime split (exact-key / seen-cooc / unseen-cooc): EXCLUDES seen-cooc parroting.
  * sparsity x attractor-temp/steps sweep: EXCLUDES the read-op findings being param artifacts.
  * Scaffold-free witness WITNESS PASS (mechanism proofs + real-data asserted on the 6 units).

-------------------------------------------------------------------------------------
THE BRAIN-FOUNDATIONAL DRILL (owner pushed hardest here; fidelity paid off, wasn't cosmetic)
-------------------------------------------------------------------------------------
Built the ACTUAL CLS operation, then drilled each part:
  * DEVIATION #4 (dense vs sparse+graded) is LOAD-BEARING ON THE READ. A dense frequency-summed
    Hebbian associator + attractor COLLAPSES TO HUBS (assoc 0.025 domain); k-WTA sparse coding +
    frequency-normalised inhibition rescues it to 0.156, beating cosine. A convenient LSA-cosine
    would have hidden this.
  * NEW deviation: full/partial ATTRACTOR completion HURTS pool-ranking -- it re-settles onto
    concept-code HUBS (witnessed: a hub jumps rank 2 -> 0, ROBUST across temperature 1-64). The
    faithful "which concept" read is a GRADED population read; the attractor is for recognition,
    not ranking.
  * SWEPT the convenience defaults (sparsity 2%..100% x temp {1,4,16,64} x steps {1,8}): the
    graded read is sparsity-robust (0.34-0.39) and beats every attractor setting (0.12-0.19).
    Imposing cortical 2% on the graded read would have been fidelity THEATER -- the drill caught it.
  * DEVIATION #5 CLOSED BY TEST, not assumption. I did NOT leave "offline SVD is a substitute" as
    a hand-wave. exp_cortical_interleaved_online_code_v3 builds the code by the CLS PROCESS
    (online skip-gram over the read stream + interleaved REPLAY of past sentences -- continual.py's
    islanded replay, now building the code) vs batch SVD, with a no-replay ablation and a seen-cooc
    POSITIVE CONTROL. Result: the online learner FAILS the positive control at our data scale
    (0.174 vs batch 0.356 @10 on seen-cooc, unchanged at 6 epochs). Per USER-08-11 I do NOT claim
    online==batch; the safe TESTED claim is: the interleaved PROCESS is EVEN MORE data-hungry than
    batch and shares its data-bound ceiling (SGNS ~ SVD-of-shifted-PPMI). Being more faithful to
    the process is a FALSE lever when the constraint is the DATA the process needs. "Leave the
    family, ask the biology": for a zero-experience concept the brain uses the HIPPOCAMPUS (which
    we have), not cortical magic; cortical transfer needs the lifetime of experience we lack. NOT
    "impossible" -- the priors' supplied GloVe (lifetime-scale) DOES cross the unseen floor.

-------------------------------------------------------------------------------------
BRAIN FIDELITY LEDGER (PINNED vs OURS vs SUBSTITUTED)
-------------------------------------------------------------------------------------
  PINNED    complementary learning systems: hippocampus fast/sparse/exact; cortex slow/overlapping/
            statistical, read by pattern completion; consolidation by interleaved replay.
  FAITHFUL  the READ op as built: sparse coding + lateral inhibition + graded population readout
            (attractor tested and shown to hurt ranking -> graded is the faithful ranking read).
  SUBSTITUTED (all are CONTENT, not the read, and all bounded by DATA not algorithm):
            concept code = offline PPMI+SVD (online process tested: more data-hungry, same ceiling);
            similarity = cosine not sparse-pattern overlap (tested: overlap no better);
            concept identity = distributional-only, not the multimodal ATL hub (NOT closed -- flagship lane).

-------------------------------------------------------------------------------------
PROPOSED hdlab CHANGE -- NOT landed (board Q111; strategy re-verifies + lands)
-------------------------------------------------------------------------------------
The fix is NOT "wire cortical_recall onto recall_sentence and expect transfer" (ties counting at best,
carries nothing on novel queries). The brain-faithful, evidence-backed wiring is the CLS MATCHED PAIR
(this is the cortical complement to the integrated p2 dg_ca3_recollection_gate):
  1. Read the consolidated store in a GRADED SPARSE+INHIBITED overlapping code (k-WTA + frequency-
     normalised prototype match), NOT the exact-fact context space and NOT a settled attractor. Add a
     space="overlap" read to hdlab/cortical_recall.py that ranks the consolidated pool by graded match
     in a distributional code; keep the consolidation gate/membership unchanged (CLS sparsity preserved).
  2. Route EPISODIC <-> CORTICAL by recollection confidence (the p2 CA3-completion-overlap signal):
     confident exact-key cue -> EPISODIC; else -> the cortical read. The per-regime dominance flip
     (episodic 0.992 exact-key vs cortical 0.44 >> episodic 0.06 held-out) makes this beat either single
     system on a mixed population -- the complementary-systems architecture, not either/or.
  3. Do NOT expect it to beat counting on transfer -- it will not until the CONSOLIDATED CONTENT changes.

AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
  * Deviation #3 (wrong memory): refine. Reading the store the brain's way DOES beat the episodic path
    on transfer (~10x, CI-separated over the twin) and ablation can be made to bite -- read-path defect
    real and fixable. BUT it does not clear the counting floor and carries no cue-specific signal on
    unseen-cooc (powered) -- the "memorises-not-transfers" wall is NOT dissolved by the read alone.
    Reframe the missing-organ verdict as "missing cortical-read organ AND transfer-bearing content."
  * Deviation #4 (dense vs sparse+graded) is LOAD-BEARING ON THE READ (measured): sparse+inhibited
    coding rescues the associative read from hub collapse (0.025 -> 0.156). Couple it with the
    cortical-read work, not only the sign() line.
  * NEW deviation: recurrent ATTRACTOR completion (CA3-class) HURTS pool-ranking (re-promotes
    concept-code hubs); the faithful semantic RANKING read is a graded population read.

SUGGESTED FOLLOW-UPS (I do not file problems -- for the architect to scope):
  (a) The residual transfer wall is the consolidated CODE (offline/unimodal/noisy). Levers: an
      overlapping code learned online or SUPPLIED at scale (reader_meaning_channel / supply-a-
      distributional-spoke); TEACHING one channel with another vs concatenating
      (teach_the_self_built_space_instead_of_concatenating_it); a cleaner consolidation gate (what
      gets replayed). Separate problems; I did not open them.
  (b) Demonstrate the dual-process routing live (episodic<->cortical by the p2 gate) -- transfer side
      is capped by the same content wall, so it is architecture validation, not a floor-beater.

WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST
  * A floor-beating transfer read (decisively not achieved on unseen, powered -- robust negative).
  * That replay is load-bearing (linear associator: replay vs no-replay ~identical -- faithful in form
    only; first thing I'd withdraw is any implied replay benefit).
  * That a MULTIMODAL code would still fail (explicitly NOT closed -- flagship's lane).

FILES
  experiments/exp_cortical_store_read_path_v1.py            (decisive frame: episodic arm + ablation)
  experiments/exp_cortical_replay_completion_v2.py          (HEADLINE, FULL: 6 units in metrics.json)
  experiments/exp_cortical_interleaved_online_code_v3.py    (deviation-#5 deepening; SMOKE-diagnostic)
  verification/test_cortical_store_read_path.py             (scaffold-free witness; WITNESS PASS)
  data/exp_cortical_replay_completion_v2/{metrics.json,units.jsonl}
  notes/problems/the_consolidated_cortical_store_is_written_but_never_read/SOLVED.md + SOLVER_NOTES.md

-------------------------------------------------------------------------------------
TLDR
-------------------------------------------------------------------------------------
The system remembers what it read almost perfectly but answers new questions from that fast, word-for-
word memory and never consults the settled "knowledge" store -- so it looks like it memorises and never
learns. I confirmed that (turn the settled store off, nothing changes), then built the brain's way of
reading it. Reading the settled store this way answers new questions about 7-10 times better than the
fast memory, and I proved the settled store is really being used (switch it off, the answer collapses).
So the "we read the wrong memory" diagnosis is right and the read is worth wiring. But it is not the
whole cure: it still loses to simply counting which words co-occur, and on genuinely new questions it
does no better than a deliberately scrambled cue. I went further and built the brain's actual
consolidation PROCESS (interleaved replay learning the code, not a shortcut) -- and it is even hungrier
for data than the shortcut, which pins the real problem: not whether we read the settled store, but that
we lack a lifetime of experience to put a rich enough meaning-map in it. The brain-faithfulness paid off
concretely: the read only worked once I added the cortex's sparse coding and inhibition, and I found the
full "settle on one answer" step actually hurts (it drifts to over-connected hub words), so the faithful
read is a graded one.

QUESTIONS: none.

NEXT STEPS
  1. Land the CLS matched pair (graded sparse+inhibited cortical read, routed against episodic by the p2
     confidence gate); do NOT expect it to beat counting on transfer.
  2. Route the residual (richer/larger-scale or MULTIMODAL meaning code) to the content lanes
     (reader_meaning_channel / teach-don't-concatenate), which I did not close.
  3. Fold the three AUDIT UPDATEs into BRAIN_FOUNDATIONAL_AUDIT.md.
=====================================================================================
