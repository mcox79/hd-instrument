---
problem: cortical_read_never_tested_where_it_matters
status: PARTIAL
bar: "A TASK SCORE ON ITEMS WHERE COUNTING CANNOT HELP, WITH AT LEAST 200 SUCH ITEMS, AND A CI-SEPARATED MARGIN OVER THE STRONGEST FLOOR YOU ACTUALLY RUN ON THAT POPULATION."
result: "Powered generalisation test (train simplewiki, test held-out narrative fiction; 3 seeds; 269/279/271 UNSEEN-co-occurrence items/seed; pool 274-329; rank_with_ties both conventions; 2000-boot CIs; overlap=0). THE BAR IS CLEARED -- but only by a SUPPLIED distributional retrieval space, never by one built from our own reading. A supplied distributional foundation (GloVe, glass-box lookup, NOT an LLM) ranking the consolidated pool clears the strongest floor CI-separated 3/3 (hit@25 0.377, lo 0.29-0.34 vs floor upper 0.20-0.25; median rank 37 of ~300). NO space built from our reading clears it: current organ CTX_RAW 0.029 / second-order-cue CTX_PROF 0.020 sit AT the info-free twins (RANDOM 0.040); the sensorimotor meaning asset SPOKE/BOTH 0.083/0.092 and glass-box PPMI+SVD LSA_FULL(20k) 0.052 all sit BELOW the concreteness floor 0.115 (hit@10). So the capability is REAL and achievable with admissible supplied knowledge, but the organ-as-built and every self-built space are refuted as generalisers."
floor: "Strongest floor RUN on the UNSEEN population = concreteness prior (CONC, cue-blind): hit@10 0.115, hit@25 upper-CI 0.197/0.247/0.221 across seeds. Also run: FREQ (hit@10 0.011), COOC (0.000, at construction-floor by the definition of unseen), and info-free twins SCRAMBLE (0.033) / RANDOM (0.040). Gate = floor's UPPER CI vs arm's PESSIMISTIC-convention LOWER CI (adversarial to the arm)."
controls: "(1) INFO-FREE TWINS (SCRAMBLE=cue on unrelated donor; RANDOM=permutation): every organ/self-built arm sits AT or BELOW them -> EXCLUDES 'the space carries cue-specific signal'. (2) CONCRETENESS FLOOR: SPOKE/BOTH (=the project's sensorimotor meaning asset, grounded_vector, confirmed cos=1.000) sit below it -> EXCLUDES 'the meaning asset carries retrieval association' (it carries similarity, not cloze retrieval). (3) SUPPLIED-DISTRIBUTIONAL CEILING = could-it-succeed control: clears 3/3 -> EXCLUDES 'unwinnable population / metric cannot separate signal from noise', and IS a proof-of-concept of the rescue. (4) NOT BENCHMARK-SELECTION: items are natural fiction sentences with a random consolidated target; the unseen filter and the candidate pool come from the substrate's co-occurrence, NOT from any embedding -> EXCLUDES 'a benchmark selected by a resource scoring that resource'. (5) CLEAN UNSEEN PARTITION: overlap=0 per item, COOC=0.000 by construction -> EXCLUDES leak. (6) METRIC-FAILS-SAFE witness (planted->rank1 200/200, random->0.025, degenerate->flagged+last). (7) BOTH tie conventions."
files_changed: "experiments/solverB_cortical_paradigmatic_generalization_v1.py, verification/solverB_verify_paradigmatic_generalization.py, data/solverB_cortical_paradigmatic_generalization_v1/metrics.json, data/solverB_cortical_paradigmatic_generalization_v1/units.jsonl, data/solverB_cortical_paradigmatic_generalization_v1/_glove_subset.npz, notes/problems/cortical_read_never_tested_where_it_matters/SOLVED.md (NO hdlab/ change -- proposed change below)"
reverify: ".venv/Scripts/python.exe verification/solverB_verify_paradigmatic_generalization.py  # scaffold-free: proves a distributional space retrieves a target from cue words it NEVER co-occurred with (the mechanism), the metric fails safe, the GloVe ceiling is coherent. Headline numbers are in data/solverB_cortical_paradigmatic_generalization_v1/metrics.json (byte-stable). Full rerun: `.venv/Scripts/python.exe experiments/solverB_cortical_paradigmatic_generalization_v1.py --mode full --seeds 3 --route both` (WARNING: re-stamps metrics.json; not migrated to fresh_run_output_dir; prefer the witness)."
---

## THE HEADLINE

**The cortical read CAN clear the floor in the regime counting cannot reach -- but only with a
SUPPLIED distributional retrieval space, never with anything the substrate builds from its own
reading.** On a held-out task where co-occurrence counting is at floor by construction, a supplied
distributional space (GloVe, a glass-box lookup table, not an LLM) ranking the consolidated pool
clears the concreteness floor CI-separated on all three seeds. NOTHING built from our reading does:
not the organ's accumulated-context space, not a second-order paradigmatic cue over it, not the
sensorimotor meaning asset, and not a PPMI+SVD distributional space built from the full 20k-sentence
simplewiki foundation. So this is **PARTIAL**: the capability is real and reachable with admissible
supplied knowledge (the bar is met), while the organ as built -- and every space we can self-build --
is refuted as a generaliser, and the wiring + spoke-combination is unbuilt and belongs to the
flagship `reader_meaning_channel` brief.

## WHERE OUR IMPLEMENTATION FAILS -- THREE POINTS, AND THE BRAIN DOES ALL THREE

The brain recognises a concept in a never-seen context via distributed cortical semantic
representations built from a LIFETIME of experience and integrated across MULTIPLE spokes
(distributional context + sensorimotor grounding + relational structure) in the anterior-temporal
hub. Measured against that, our implementation diverges at three points:

1. **The retrieval space is a CO-OCCURRENCE/spelling code, not a meaning code.** The organ's
   accumulated-context profile is first-order; in the unseen regime it collapses to counting
   (CTX_RAW hit@10 0.029, at chance). **Fixing the cue to be second-order does NOT rescue it**
   (CTX_PROF 0.020 <= CTX_RAW), and this is not new -- `exp_readout_second_order_v1` already landed
   `SYNTAGMATIC_CONFIRMED / NEW_READOUT_CLEARS_FLOOR_NO / BEATS_INCUMBENT_NO` on 2026-08-17. That
   lever is closed; I reproduced it on the powered generalisation task.
2. **Our one supplied MEANING asset is the WRONG KIND for retrieval.** The sensorimotor/Lancaster
   norms are the project's identified meaning channel (flagship `reader_meaning_channel`: rho 0.3171
   on SimLex *similarity*). I confirmed my SPOKE arm IS that asset (`sensorimotor_spoke.profile` ==
   `grounded_vector`, cos=1.000) and tested it on THIS task: hit@10 0.083, **below the concreteness
   floor 0.115** -- concreteness-level, exactly the confound the predecessor named. **Perceptual
   similarity (dog~cat) is not cloze-retrieval association (which words fill this slot).** The asset
   that carries word-word similarity does not carry contextual retrieval, and that is a new,
   task-specific finding that refines the flagship rather than duplicating it.
3. **The DISTRIBUTIONAL structure that DOES solve retrieval needs experience at a scale our reading
   cannot reach.** LSA(8k read) 0.005 -> LSA_FULL(20k simplewiki) 0.052 -> GloVe(6B tokens) 0.189.
   The mechanism is right (GloVe clears 3/3); it is starved of data from our corpora. Our entire
   readable corpus is ~326k sentences (~6.5M tokens), about 1,000x short of GloVe's training, so
   "just read more" does not close it (I enumerated the corpora; the total is the ceiling).

## THE RESCUE, AND IT IS WHAT THE PROJECT'S OWN ARCHITECTURE ALREADY POINTS AT

The rescue is NOT a retrieval-rule tweak (refuted, landed twice), NOT a self-built distributional
space (data-starved by ~1,000x), NOT the sensorimotor asset alone (wrong kind for retrieval), and
NOT a relational knowledge graph (prior work `exp_arc_fact_retrieval_semantic_kb_climb_v1` landed
`KB_BELOW_FLOOR`, and the memory's circular-WordNet-oracle caution reads `0.0365` under a partial
cue -- the relational path is explored and unpromising here). It is:

**Give the cortical read a supplied DISTRIBUTIONAL spoke, and combine it with the sensorimotor spoke
in a hub -- exactly the brain's hub-and-spoke (Lambon Ralph; ATL integration), and exactly the
admissible-supplied-knowledge path the project already sanctions.** Concretely:

- **Distributional spoke** (contextual/topical association -> cloze retrieval): a supplied
  distributional embedding at scale. This is admissible under the project's own rulings ("Supplied
  knowledge is ADMISSIBLE... say which"; "a STATIC OFFLINE-BUILT ASSET IS ADMISSIBLE") and it does
  NOT violate "no external LLM at inference" -- a co-occurrence embedding is a glass-box lookup
  table, not a language model. **On this test it clears the floor CI-separated 3/3.** That is the
  proof-of-concept; the GLOVE arm is not merely a control, it is a demonstration of the fix.
- **Sensorimotor spoke** (perceptual similarity -> SimLex): the Lancaster norms, already identified
  by the flagship and already tested there.
- **Hub combination** (reliability-weighted, not fixed-weight): this is the OPEN problem the flagship
  `reader_meaning_channel` owns -- "combination is the bottleneck", the channel is "a CONTRIBUTOR,
  not a DECIDER". My result adds the specific spoke that its similarity-focused channel is missing
  for the READ task: a distributional one.

### PROPOSED hdlab/ CHANGE (for the strategy session to re-verify and land)

In `hdlab/cortical_recall.py::build_cortical_index`, add a `space="foundation"` that represents each
consolidated term by its supplied distributional vector, leaving the consolidation GATE unchanged
(CLS sparsity preserved -- the foundation supplies geometry, membership stays gated). Wire it as a
SPOKE alongside the sensorimotor one, combined by the hub rule the flagship builds. **Do NOT** try to
fix retrieval with a cue-rule change or a self-built space -- both are refuted here. The tradeoff to
weigh openly (owner's call): the distributional geometry is IMPORTED, not learned by the substrate --
the same supplied-vs-learned line the sensorimotor asset already sits on.

### IMPORT NOW, BUILD OVER TIME -- and the two tiers are COMPLEMENTARY, measured

The right way to do this is not import-or-build, it is BOTH, and the data says why it works. Split
the same run by whether the substrate had read about the target in context:

| arm | SEEN (material we read about, n~450/seed) | UNSEEN (novel context) |
|---|---|---|
| counting | 0.157 | 0.000 |
| **our self-built map (LSA_FULL)** | **0.338** | 0.052 |
| imported map (GLOVE) | 0.336 | 0.189 |

**On the material we have actually read, our OWN self-built map already EQUALS the import (0.338 vs
0.336) and beats counting 2:1.** The import only pulls ahead on the UNREAD. So the two tiers own
different regimes: the imported foundation carries the novel/generic; the learned tier carries the
specific/familiar and already matches the import there. This is the CLS division of labour and it is
exactly the project's own THREE-TIER MULTI-SOURCE architecture (foundation + growing middle tier).

Two consequences that dissolve the data-volume objection above:
1. **"Build over time" means ADAPT + EXTEND, not REBUILD.** My 1,000x-short finding was about
   BUILDING a general map from scratch. ADAPTING a good foundation with our reading, and adding
   coverage for the specific/novel terms it lacks, needs far less data -- and grows monotonically as
   the substrate reads (my LSA(8k)->LSA_FULL(20k) curve already climbs with data).
2. **You get a working read TODAY** (from the foundation) while the learned tier compounds where it
   is already strongest (what we have read). Nothing waits on reading a billion sentences.

**The one genuinely hard part, stated honestly: the COMBINATION RULE.** Naive fixed-weight blending
has a LANDED track record of HURTING here (`exp_substrate_concept_encoder_v2..._2spoke` HARD_FAIL,
"composition HURTS relative to best single spoke"; and the flagship's own prior-plus-channel blend
destroyed the signal). It must be RELIABILITY-WEIGHTED (trust the learned tier only where it has
evidence for that term) and likely SEGREGATED (the flagship's measured result: separate slots beat
superposition). That combination rule is the open problem `reader_meaning_channel` already owns -- so
this plan adds no new hard problem, it routes into the one already funded.

## THE NUMBERS (domain route, 3 seeds, UNSEEN population, hit@k pessimistic tie convention)

`n_unseen` = 269/279/271 (all >= 200). `chance@10` ~ 0.034. Averaged over seeds:

| arm | hit@10 | hit@25 | hit@50 | median | reading |
|---|---|---|---|---|---|
| **GLOVE** (supplied distributional; the rescue) | **0.189** | **0.377** | **0.601** | **37** | clears the floor 3/3, CI-separated |
| CONC floor (strongest floor) | 0.115 | 0.177 | 0.266 | 109 | the bar to beat |
| BOTH / SPOKE (= sensorimotor meaning asset) | 0.092 / 0.083 | 0.183 | 0.31 | ~100 | beats twins; **below CONC** -> concreteness |
| LSA_FULL (glass-box, self-built, 20k) | 0.052 | 0.140 | 0.242 | 111 | **below floor**; under-resourced |
| RANDOM / SCRAMBLE (info-free twins) | 0.040 / 0.033 | 0.08 | 0.17 | ~145 | -- |
| CTX_RAW / CTX_PROF (1st- / 2nd-order cue) | 0.029 / 0.020 | 0.07 | 0.14 | ~149 | at chance / at the twins |
| LSA (glass-box, 8k read) | 0.005 | 0.046 | 0.126 | 141 | below chance |
| COOC (counting) | 0.000 | 0.000 | 0.000 | 294 | at floor by construction |

## THE HONEST WRINKLE: IN-DOMAIN IS HARDER STILL

The second route (in-domain sparse read) is underpowered by construction (114-129 unseen of 900 --
the scarcity the brief warned about), and there the floor is much stronger (CONC hit@10 0.26-0.28)
and **even GLOVE does not clear it at k=10** (only k=25+). So the clean win is specifically ACROSS a
domain shift; recognising a concept in a novel SAME-domain context is harder, and there the
frequency/concreteness prior is a strong baseline for everyone. Reported rather than hidden.

## PRIOR WORK I CHECKED (the owner flagged there is a lot, and there is)

- `reader_meaning_channel` (flagship, priority 1): the sensorimotor asset is the meaning channel for
  SIMILARITY; combination is the bottleneck; `read()` makes zero calls to it. My work adds the
  DISTRIBUTIONAL spoke it lacks for the READ task and shows the sensorimotor asset alone is below
  floor on cloze retrieval. I did NOT touch that brief or its lane.
- `exp_readout_second_order_v1` (paradigmatic readout does not clear the floor) -- reproduced, not
  re-derived; the second-order cue lever is closed.
- `exp_arc_fact_retrieval_semantic_kb_climb_v1` (`KB_BELOW_FLOOR`) + the WordNet-oracle caution --
  the relational/knowledge-graph rescue is explored and unpromising; not built.
- Ran `before_you_start.py` and `experiment_index.py query` across conceptnet/cskg/foundation/
  embedding/cortical/distributional/wordnet/paradigmatic/relational before proposing the rescue.

## WHAT I DID NOT ESTABLISH

- **A working WIRED cortical read** -- I proved the retrieval space that clears the floor (supplied
  distributional) and the ones that do not; wiring it and the hub combination rule are unbuilt and are
  the flagship's lane.
- **That a self-built glass-box space could ever suffice** -- I bounded it below (20k far too little)
  and above (6B suffices), not the crossover; on available corpora (~326k) it almost certainly cannot.
- **That in-domain novel-context retrieval is achievable at all** -- even GLOVE struggles there.

## WHAT I WOULD WITHDRAW FIRST IF WRONG

The status PARTIAL rests on counting the supplied-distributional space as an admissible cortical
retrieval space; if the owner rules a cortical read must LEARN its space from the substrate's own
reading, this becomes a clean powered REFUTED (nothing self-built clears the floor). The powered
negative on the organ and all self-built spaces is the robust part and I would not distrust it.

## A CORRECTION I OWE THE RECORD

An interim read of the SMOKE (n=94, a 136-term pool) showed my self-built LSA_FULL at hit@10 0.255
and I briefly took it as "a glass-box space generalises". **It did not survive the full run** (270
unseen, ~300-term pool): LSA_FULL fell to 0.052, below the floor. The smaller pool made hit@10 easy.
This is the project's own "a smoke with smaller numbers does not test the full run" rule; the
correction is recorded here, not buried.

## TLDR

We have a component meant to recognise a familiar idea in a situation it has never seen it in before.
I built the fair, powered test (200+ questions, three times over) and every brain-faithful way to make
it win from what our system has actually read -- including building it its own "words that keep
similar company are similar" map. **None of them work: they do no better than random on the questions
that matter.** But the questions ARE answerable: a ready-made map built from a very large body of text
-- the kind of experience a real brain gets over a lifetime -- answers them well and beats the
counting baseline cleanly. Our own sensory-meaning table (which is good at "how similar are two
words") turns out to be the wrong tool for "which word goes in this gap". **So the fix is not a
cleverer search and not more of our own reading -- it is to give the reader a ready-made large-scale
word-meaning map as one input, and blend it with the sensory one, the way the brain combines several
sources of meaning. One such map already clears the bar in my test; wiring and blending it is the next
job, and it belongs to the meaning-channel problem that already owns that work.**

## QUESTIONS

One decision belongs to the owner: may the cortical read use an IMPORTED distributional map (a static,
inspectable, offline, non-LLM asset -- admissible under existing rulings), or must it LEARN its map
from the substrate's own reading? The first clears the bar today; the second needs ~1,000x more
reading than all our corpora combined provide.

## NEXT STEPS

1. **Land the `B3'` slot-note update**: the cortical read does not clear the counting-free floor on
   ANY space built from our reading (powered, 3 seeds); it clears with a supplied distributional
   foundation. Keep it `NEEDS_ADAPTER` on THIS evidence.
2. **Route the distributional-spoke finding into `reader_meaning_channel`** (the flagship that owns
   wiring + hub combination): its meaning channel is sensorimotor (similarity); the READ task also
   needs a distributional spoke (retrieval), demonstrated here to clear the floor.
3. **Decide the imported-vs-learned foundation question** -- upstream of any wiring, owner's call.

## INTEGRATED_BY_STRATEGY -- 2026-08-24, re-verified independently before acceptance

**Re-verified: `verification/solverB_verify_paradigmatic_generalization.py` PASSES 6/6, exit 0.**
The witness is genuinely scaffold-free and the metric-fails-safe check is the good kind -- planted
target reaches rank 1 (200/200), random reads 0.025, and the degenerate space is flagged AND sorted
last rather than winning. Review: **STRONG.** The three-point brain-fidelity audit is the most
useful part and the SPOKE identity check (`sensorimotor_spoke.profile == grounded_vector`,
cos=1.000) is exactly the verification most submissions skip.

**THE ARITHMETIC IS RIGHT, SO I AUDITED THE ARGUMENT, AND THERE IS A GAP -- ONE UNTESTED CELL.**

The conclusion is *"no space built from our reading generalises, therefore SUPPLY a distributional
spoke."* Every self-built arm here is either **used alone** or **concatenated**: line 36 of the cell
defines `BOTH` as *"context+spoke concat"*, and the strings `distil` / `teach` / `orient` do not
appear anywhere in the file. **So the two channels were WEIGHTED, never made to TEACH each other.**

That matters because of a result that landed the SAME DAY, on the same kind of self-built space:
`exp_crossmodal_distillation_substitutability_v1` lets the grounded hub **teach a direction over
PPMI+SVD** and reads **`0.8388` CI `[0.8031,0.8720]`**, beating its info-free twin's MAXIMUM over
200 draws -- where **grounded alone is at chance (`0.5513`) and distributional alone is INVERTED
(`0.0285`)**. Neither channel carries it; their AGREEMENT does. That is also the standing
four-instrument finding: *an oracle clears, no unsupervised combiner reaches it -- the missing organ
is "notice which source to trust"*, and teaching is the first thing that has worked where weighting
did not.

**⚠️ THIS IS A GAP, NOT A PREDICTION, AND THE SUBMISSION ITSELF SUPPLIES THE REASON FOR DOUBT.**
Its point 2 -- *perceptual similarity (dog~cat) is not cloze-retrieval association* -- is precisely
why the distillation trick might NOT transfer: it was demonstrated on SUBSTITUTABILITY, and this is
RETRIEVAL. **No number crosses tasks.** The honest statement is that the cheapest remaining rescue
was never run, not that it would have worked.

➡️ **Filed as `teach_the_self_built_space_instead_of_concatenating_it`.** If teaching rescues
retrieval, the "supply a distributional spoke" purchase is unnecessary -- the same shape as tonight's
Phase 1 redirect, where the lever turned out to be projecting the norms we already have rather than
buying 14,704 more. If it does not, that is a clean, powered negative that CLOSES the self-built
route properly and makes the supplied-asset case decisively rather than by absence.

*Kept from the submission unchanged and still load-bearing: `CTX_PROF <= CTX_RAW` reproduces the
landed `exp_readout_second_order_v1` negative, so the retrieval-rule lever stays closed; and the
`~1,000x` corpus shortfall was enumerated, not estimated.*

*Appended by the strategy session, which owns integration (board Q111). Solver text unchanged.*
