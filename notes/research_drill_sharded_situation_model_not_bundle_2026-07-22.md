# Research drill: sharded/indexed situation model, not a bundle — brain-first

**Date:** 2026-07-22. **Trigger:** component-#2 comprehension-loop pre-flight (2026-07-21 CI-loop design)
measured that a running situation model encoded as ONE VSA superposition is CAPACITY-DEAD for who-affected
readout: single-unbind decodes 0.53 @2 propositions -> 0.30 @4 -> 0.22 @8; a sharded/indexed proposition
store reads out cleanly (1.000), at which point naive settling adds nothing over retrieval. A bundled state
is also exactly order-invariant (cos 1.0 under permutation) — no sequence structure. **Method:** brain-first
synthesis from established neuroscience + the 6 named prior-drill notes (build-on, not re-derive). No web
fetch performed (headless, no auth) — no WEB-FETCH REQUESTS needed; the mechanism is textbook-consensus.
HYPOTHESIS-pending until a cell + VET.

## HEADLINE

The brain never stores a running multi-proposition state as one superposed content vector either — the
**hippocampal indexing/relational-memory system stores a sparse, pattern-separated INDEX per item (not the
content itself), and working memory holds only a handful of items at once via TIME-MULTIPLEXED discrete
slots, not spatial superposition.** Both mechanisms are indexing/sharding schemes, not bundling schemes. The
substrate's bundle-collapse is not a brain-mismatch to route around — it is a case where the substrate
independently rediscovered, via measurement, a design constraint the brain solved architecturally from the
start. The fix is not a smarter unbind; it is not superposing multiple propositions into one vector in the
first place.

## (1) Brain mechanism — how it avoids bundle collapse

**Hippocampal indexing theory** (Teyler & DiScenna 1986; updated Teyler & Rudy 2007, *Hippocampus*): the
hippocampus does not store episodic content itself. It stores a sparse, pattern-separated INDEX (a DG/CA3
code, orthogonalized via the ~5-11x expansion + sparsification already established in the prior hippocampal
notes) that points to — binds together — the distributed neocortical ensembles active during the episode.
Each episode/proposition gets its OWN largely non-overlapping index code; indices are not superposed onto
each other. This is **relational memory** (Cohen & Eichenbaum 1993; Eichenbaum 2004, *Neuron*): the
hippocampus flexibly binds arbitrary items via a compact pointer structure, while content lives elsewhere,
retrieved by pattern completion FROM a (possibly partial/noisy) cue TO the stored index. Concept/assembly
coding (sparse "concept cells," Quiroga et al. 2005; cell-assembly readout, Buzsaki 2010, *Neuron*) confirms
the same principle at the single-item level: distinct items recruit largely distinct, addressable
populations — a discrete code, not a dense shared accumulator. Separately, **working memory avoids collapse
by TIME-MULTIPLEXING, not superposition**: Lisman & Idiart (1995, *Science*) show WM items are carried as
discrete gamma sub-cycles nested within a slower theta cycle — each item gets its OWN cycle, sequentially
addressed, never algebraically summed into one vector (this is the mechanistic root of the theta-gamma
material already surfaced in the 06-07 DEEPER drill). **Event segmentation theory** (Zacks & Swallow 2007;
Zacks et al. 2007, *Psych Bulletin*; Radvansky & Zacks 2014) adds the temporal-chunking layer: ongoing
experience is not accreted into one growing state at all — it is segmented into discrete EVENT MODELS at
prediction-error boundaries, only the CURRENT event model held live, prior ones checkpointed to
long-term/indexed storage (**time cells**, MacDonald, Lepage, Eden & Eichenbaum 2011, *Neuron*, provide the
temporal-order tag for this indexing). **Net mechanism: index-per-item + time-multiplexed small active set +
event-bounded checkpointing — never N-item superposition.**

## (2) Implied glass-box substrate representation

Replace "situation model = one accumulating VSA bundle" with a **sharded proposition store**: a dict/table
`{index_key_i: M_i}` where `M_i = bind(role_1,filler_1) + ... ` is a SMALL LOCAL bundle for proposition `i`
alone (3-5 roles — safely inside the already-measured N/16-32 word-level cliff), and `index_key_i` is a
distinct, pattern-separated key (sequential position — the time-cell analog — or a content-addressable hash
of a stable identifying cue, produced by the same DG-style expand+sparsify projection already used elsewhere
in this arc). **Retrieval is two-stage, matching CA3 pattern completion exactly**: (probe) -> nearest/exact
index-key match (possibly via settling if the probe is partial/noisy) -> direct table lookup of `M_i` ->
LOCAL unbind within that one proposition's small bundle (cheap, high-fidelity, the regime already measured
at 1.000). **Order/sequence is preserved for free** — the store is literally an ordered structure (a list or
time-tagged dict), not a symmetric sum; permutation is no longer a no-op. **Inspectability is definitional**
— every slot, key, and role-filler is individually printable; nothing is superposed away. This is not a new
primitive: it is exactly the WSM's Tier-2/3 cue-addressable carry (07-17/07-19 notes) and the reverse-replay
sequence log (06-07 DEEPER drill, P4.3) generalized into the DEFAULT representation for the running state,
not a fallback entered only once a document gets long.

## (3) Why this fixes precondition-(i)

Component #2's 2026-07-21 design specified CONSTRUCTION as "add each sentence's role-binding to the
situation model" (an accumulating superposition) — this IS the mechanism the fresh measurement falsifies.
Swapping CONSTRUCTION to "append a new slot to the indexed table" removes the superposition entirely, so
who-affected readout becomes index-lookup + local-unbind (measured 1.000) instead of unbind-from-an-N-item-
bundle (measured 0.53->0.22). Constraint-satisfaction settling is not deleted — it is **repositioned to the
place the brain actually uses it**: not disambiguating content from a superposition, but resolving a
PARTIAL/AMBIGUOUS PROBE (an anaphor, a degraded cue) to the correct index key — i.e., settling's job becomes
coreference/entity resolution over keys, which the CI-loop note had already deferred as "a later component."
This reconciles "naive settling adds nothing over retrieval" (true for a CLEAN key) with the brain's actual
use of pattern completion (recovering an index from a DEGRADED cue) — settling should be tested there, not
on clean readout.

## (4) Cheapest next measurement

Reuse the existing capacity-probe harness, add: (a) re-run the sharded-store readout inside the REAL
component-#2 who-affected task (not just the toy capacity probe) at proposition counts 2/4/8, to confirm the
1.000 number transfers out of the toy harness; (b) a key-corruption sweep (20-30% index-key noise,
simulating an ambiguous coreferential probe) comparing constraint-satisfaction settling-to-nearest-index vs.
a no-settling nearest-key baseline.

**HARD-PASS:** sharded readout stays >=0.95 through 8 propositions in the real harness, AND settling on a
degraded key recovers the correct slot at >=0.80 vs. <0.60 for no-settling (settling earns its keep
specifically on the noisy-cue margin). **HARD-FAIL:** real-harness readout drops below 0.90 at 8 propositions
(toy result doesn't transfer — likely a key-collision confound), OR settling shows <=0.05 delta over
no-settling on degraded keys (constraint-satisfaction adds nothing anywhere in this design, not just on
clean readout — a genuinely informative negative that would argue for simpler nearest-neighbor-only
retrieval throughout).

## Cross-thread synthesis

Directly resolves the open question left by `research_drill_CI_comprehension_loop_situation_model_brain_
mechanism_2026-07-21.md` (component #2), whose CONSTRUCTION step is the exact mechanism now shown
capacity-dead. Confirms and generalizes (rather than contradicts) `research_working_memory_integration_
upper_limit_2026-07-16.md`'s B4/B5 "exact external paging / RAM+disk split" — that note treated indexing as
a Frontier-2 escape hatch for LONG documents; this drill's correction is that indexing should be the
DEFAULT representation for the situation model from proposition #1, since real proposition-level crosstalk
(steeper than the word-level N/16-32 cliff, because each proposition already consumes several slots) arrives
far earlier than document length would suggest. Reuses the ordered-write-log / reverse-replay index design
from `research_drill_natural_analog_hippocampal_5x_2026-06-07.md` (P4.3) and its DEEPER companion's
theta-gamma multiplexing analysis as the direct mechanistic root of "why time-multiplex, not superpose."
Repositions (does not discard) the constraint-satisfaction settling machinery from the 07-19 compress-and-
carry note and the 07-08 hippocampal-consolidation note's CA3-completion design: settling's correct job is
degraded-cue index resolution (coreference), not content disambiguation from a bundle.

## Substrate-product implications

If HARD-PASS: the product claim becomes "tracks who-did-what-to-whom across a discourse via an inspectable,
per-fact index — never blends facts into an opaque vector," which is a stronger, more honest glass-box claim
than "holds a large situation model" (an indexed table scales by construction; a bundle does not). Ship the
representation swap in component #2 BEFORE any further settling/coreference work, since settling's value is
untestable while it is answering the wrong question (bundle disambiguation instead of key resolution). If
HARD-FAIL on the key-corruption arm, the honest fallback is a pure nearest-neighbor index store with no
settling step at all — cheaper, and not a regression, since HARD-PASS was never claimed for that path.

## Calibration

Raw confidence in the cited biology (indexing theory, relational memory, event segmentation, time-cell
temporal tagging, theta-gamma multiplexing) is high (~0.85) — textbook-consensus, cross-checked against 6
prior substrate-KB notes with no contradicting source. Standard lit-scan deflation (-0.15/-0.25) applied
since this session could not re-verify citations via live web (headless, no auth) — treat citations as
recalled/high-confidence, not freshly re-fetched. The SUBSTRATE-MAPPING claim (sharded table as default
representation, settling repositioned to key-resolution) is novel-synthesis and capped per house discipline.
**P_deflated = 0.48** for the mechanism-transfer claim (the toy-harness 1.000 sharded number generalizing to
the real component-#2 task); **P_deflated = 0.35** for the settling-earns-its-keep-on-degraded-cues
prediction specifically (no direct precedent in this arc for settling tested against a corrupted-key
regime — genuinely new measurement, not an import).

## Citations (verified count: 10 primary sources, all recalled from established neuroscience literature this
session — not freshly re-fetched via web, per no-web-auth constraint; consistent with and extending the
already-cross-checked citations in the 6 prior notes this drill builds on)

Teyler & DiScenna (1986, *Behavioral Neuroscience*, hippocampal indexing theory); Teyler & Rudy (2007,
*Hippocampus*, updated indexing theory); Cohen & Eichenbaum (1993, *Memory, Amnesia, and the Hippocampal
System*, relational memory); Eichenbaum (2004, *Neuron*, hippocampal relational binding); Quiroga et al.
(2005, *Nature*, sparse concept-cell coding); Buzsaki (2010, *Neuron*, cell-assembly discrete readout);
Lisman & Idiart (1995, *Science*, theta-gamma time-multiplexed WM slots); Zacks & Swallow (2007, *Current
Directions in Psychological Science*, event segmentation); Zacks, Speer, Swallow, Braver & Reynolds (2007,
*Psychological Bulletin*, event perception); MacDonald, Lepage, Eden & Eichenbaum (2011, *Neuron*,
hippocampal time cells). Internal (build-on, not re-derived): `research_working_memory_integration_upper_
limit_2026-07-16.md`; `research_drill_natural_analog_hippocampal_5x_2026-06-07.md`;
`research_drill_natural_analog_hippocampal_DEEPER_3x_2026-06-07.md`;
`research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md`;
`research_situation_model_guided_comprehension_loop_compress_and_carry_2026-07-19.md`;
`research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md`.

## Status

USER-locked discipline applied: no `exp_dev_handoff_*.md` or `strategy_request_to_*.md` routing files
written (ferry mechanism deprecated). Every actionable pointer is inline above (design in (2), cheap test in
(4), falsifiable thresholds, cross-thread pointers). No cap_map or strategy files modified.
