# WHERE THE SUBSTRATE FUNCTIONS STAND: **36 OF 150 RUN WHEN IT READS. 81 ARE BUILT, BLESSED, AND NEVER CALLED.**

**Owner, 2026-08-21: *"Why did we stop working on reading? Where are we on the different functions of
substrate?"*** Answered by measurement. `tools/substrate_function_status.py`.

| | count |
|---|---|
| modules on disk (`hdlab/`) | **150** |
| registered in `capability_registry.jsonl` | **150** -- *all of them* |
| **loaded by a LIVE `Substrate().read()`** | **36** |
| **registered `gate=WIRE` but NOT loaded by a live read** | **81** |

---

## 1. 🚨 **THE ANSWER TO "WHY DID READING STALL" IS PROBABLY THAT NUMBER**

**Eighty-one modules are built, tested, registered and blessed `WIRE` -- and the reading path never
calls them.** *That is not a filing discrepancy; it is more than half the built capability sitting
beside the loop rather than inside it.*

**Islanded modules that bear directly on reading:**

| module | what it is |
|---|---|
| `prelim_tier`, `three_tier_loop` | **the owner's "cold storage"** -- proven end-to-end, 3 HARD_PASS |
| `successor_representation` | **D7, fully pinned in `ORGAN_MAP`** |
| `situation_model_multibank` | the capacity fix for the situation register |
| `pos_tagger`, `arc_parser`, `semantic_parser` | syntax, available and unused by the loop |
| `modern_hopfield_readout`, `streaming_attention` | read-out mechanisms |
| `learning`, `word_learning_tool` | *learning*, not called by the reading loop |
| `sensorimotor_spoke` | `WIRE_NARROWED` -- the one route measured NOT subsumed by counting |

## 2. ✅ WHAT DOES RUN WHEN IT READS -- 36 MODULES, AND THE CORE IS THERE

`reading_grounding_loop`, `grounding_acquisition_loop`, `definitional_extraction`,
`coreference_resolver`, `situation_model_accumulate`, `hd_fact_store`, `information_foraging`,
`hippocampal_encoder`, `gap_detector`, `state_of_mind`, `thematic_role_labeler`, `frame_induction`,
`self_improving_loop`, plus the primitives (`binding`, `bundling`, `cleanup_family`,
`iterative_attractor`).

**The reading loop is not a stub. It is a real pipeline of ~36 parts.** *The gap is not that reading
is unbuilt; it is that two thirds of what has been built is not in it.*

## 3. 📌 AND IT CORRECTS TWO STALE FIGURES IN `CLAUDE.md`

- *"62 of 141 modules have no registry row at all"* -> **now 0 of 150.** The registry has been
  completed since that was written; a registry-first audit is no longer structurally blind.
- *"35 of 141 are reachable from the live path"* -> **36 of 150**, measured the same way.
  *That one held up, which is worth saying: the figure I was most likely to find stale did not
  move.*

## 4. WHY I DID NOT ANSWER THIS FROM MEMORY

**The registry's own `pipeline_status` is documented as wrong in BOTH directions** -- 19 rows claim
not-reachable while measurably live, 3 claim the reverse. **So this is measured at RUNTIME**, by
running a read and inspecting `sys.modules`, which is the only method that catches the three modules
imported inside a function body (invisible to grep) and rejects the two that appear only in a string
constant and a comment.

**⚠️ SCOPE, SO IT CANNOT BE OVER-READ: "not loaded by a live read" does NOT mean dead.** A module may
serve query, consolidation, or another entry point. **It means only that the READING path does not
touch it** -- which is the precise question the owner asked.

## 5. 🎯 AND IT CONVERGES WITH THE OWNER'S OTHER NOTE

*"we should have a hierarchical memory - optimized, not in the weeds on details, and then a 2nd
level based on what it finds there that is way faster."*

**That is `three_tier_loop` + `prelim_tier`, which are in the 81.** *The design the owner is
describing is built, proven, and among the modules the reading path never calls.*

## TLDR

You asked why reading stalled and where each part stands. I measured it rather than answering from
memory.

**Of 150 components in the system, 36 actually run when it reads. 81 are finished, tested, approved
for use — and never called by the reading process.**

That is very likely the answer to your question. Reading did not stall because reading is unbuilt:
the reading pipeline is a real thing with about three dozen working parts. **It stalled because two
thirds of everything we have built sits next to that pipeline instead of inside it.**

Among the unconnected ones: the tiered "cold storage" you described, the fast-lookup layer you
proposed an hour ago, the grammar tools, and the one component previously measured as genuinely
adding something over plain word-counting.

I also checked two figures our own documentation states, and one is out of date: it claims 62
components are unregistered, and the real number is now zero. The other — how many run during a read
— was almost exactly right, which is worth saying, because it is the figure I expected to have
drifted.

**One caution I want to be precise about:** "not used while reading" is not the same as "dead". Some
of those 81 serve answering questions rather than reading. What is certain is that the reading path
does not touch them.

## QUESTIONS

None.

## NEXT STEPS

1. **The 81 is the real backlog**, and it is a wiring backlog, not a build one.
2. Wiring needs a measured target per module -- WIRE-or-SHELVE demands a reason, and 81 assumptions
   would be 81 chances to repeat today's pattern of proposing before measuring.
3. `tools/substrate_function_status.py` is repeatable; this is not a one-off audit.
