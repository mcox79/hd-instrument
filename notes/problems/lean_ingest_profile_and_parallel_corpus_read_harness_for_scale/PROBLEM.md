---
review: EXCELLENT
review_text: Reverified first-hand test_lean_ingest_and_parallel_harness.py 36/36 + a new pure-hdlab landing witness test_ingest_profiles_landing.py (all 12 profiles byte-faithful to the validated builder; selpref == full on the harvest core, events 346/entities 451). LANDED hdlab/ingest_profiles.py (named presets full/selpref/lean_floor/<dim>_kept, promoted VERBATIM; reuses the flag plumbing -> byte-identical to full on the kept dims). The process-parallel read harness is validated + usable (experiments/exp_parallel_corpus_read_harness_v1.parallel_read: per-doc byte-identical serial-vs-parallel 1/2/4/8 workers, ~0.87->2.69 docs/s = 68% of the box's 12-core CPU ceiling). Honest correction folded: speedup is PER-PROFILE (selpref ~2x roles-keeping / lean_floor ~9x role-free; the parse is the floor), NOT a flat 5x. Located determinism controls (set-order canonicalized; contention-flips only under oversubscription; byte-reproducible workers<=physical cores). DEFERRED (optional, verdict-independent, low-value): the referent_per_np source-determinism fix (harness already canonicalizes; would change global entity order for no gain) + a tools/ CLI (harness usable as-is). §2b folded. INTEGRATED 2026-09-05.
---

# PROBLEM: the knowledge-foundation + learner work (owner-confirmed 2026-09-04) needs to read LARGE corpora, but the full situation-model read is ~3.6s/doc (0.05s/sentence, all 11 dimensions on) → ~10.5 hr / 10k docs on one core. Two measured facts make this cheap to fix: (1) a LEAN read (only the extraction the ingest needs — parse + roles + senses; all other dimensions off) is **0.685s/doc, 5.3x faster** (`SituationReader.all_capabilities_off()` already exists), and (2) reads are EMBARRASSINGLY PARALLEL across documents (each read resets its own cache, no cross-doc state — deterministic). Build (a) a first-class, NAMED "ingest profile" — a documented lean `SituationReader` config that keeps ONLY the extraction a given knowledge store needs (e.g. parse + typed roles for selectional preference; sense contexts for the W) and drops affect/goals/belief/world-state/timeline/entity-states — and (b) a process-parallel corpus-read harness (multiprocessing across docs; the GIL blocks thread-parallelism for the pure-Python parser, so use PROCESSES) that scales linearly with cores + the remote box. Target: a 10k-doc lean parallel ingest in minutes, not hours, with the extraction byte-identical to the full read's on the kept dimensions. Or a located negative naming why the ingest cannot be leaned/parallelized safely.

**slug:** `lean_ingest_profile_and_parallel_corpus_read_harness_for_scale` — **opened:** 2026-09-04 by the strategy session (the scaling lever from the perf/scaling evaluation; serves the owner-confirmed knowledge-foundation + grow-experience work). **status:** OPEN. Strategy lands any hdlab wire (Q111). Glass-box, NO external LLM. Infra/optimization (byte-identical extraction on the kept dims).

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar — work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure.
> 2. **REUSE — does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST.
> 3. **GENERALIZE — does this need to generalize, and HOW does the brain generalize it?** Build for that, not the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed.
> 5. **OPTIMIZE BY EXACT REPLICATION.** Copy the computation, SWEEP (never adopt) the parameters.
> 6. **PERFORMANCE vs THE BRAIN.** WHERE ALONG THE CHAIN do we lose signal? An itemized mechanism-diff.
> 7. **ADJACENT COMPONENTS.** Map the capabilities/limits/opportunities of the neighbours — seeds the next problems.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem, FULLY conveying the benefit? If not, keep pushing.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader does eleven kinds of analysis on every document, which is right for evaluating comprehension but wasteful when we just want to harvest one kind of knowledge from a huge pile of text. Two easy facts: (1) turning off the parts a given ingest doesn't need already makes a read ~5× faster, and (2) different documents are completely independent, so we can read hundreds at once on many cores. The job: make a clean, named "harvest mode" that keeps only what's needed, and a runner that reads a whole corpus across all cores/machines at once — turning a ten-hour corpus into minutes.

## 2. WHY THIS ONE — it is the enabling infrastructure for the whole knowledge/learner program
The owner-confirmed knowledge strategy (build the curated foundation, then grow-experience) reads large corpora. At 3.6s/doc serial it is a ten-hour bottleneck per pass; lean + parallel makes it minutes, which changes what is feasible (iterate the foundation, sweep resolvers, run the propose-and-verify learner at scale). The two wins are ALREADY measured (5.3x lean; embarrassingly parallel) — this problem packages them as durable, correct infrastructure.

## 3. HOW THE BRAIN DOES THIS (the opening move)
This is infrastructure, not a brain mechanism — but it is IN SERVICE of the brain-faithful acquisition (consolidation of experience). PINNED framing: the brain reads for a PURPOSE and engages only the relevant processing (task-set / attentional gating) — the ingest profile is that gating made explicit (harvest selectional preference vs harvest sense contexts vs full comprehension). OUR-INVENTION: the exact profile presets + the parallel harness. The CORRECTNESS constraint is brain-agnostic: the kept dimensions must be byte-identical to the full read.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** full read 3.6s/doc (0.05s/sentence); LEAN (`all_capabilities_off()`) 0.685s/doc (5.3x); the expensive dimensions are the parse-invoking ones (entity_states +1.3s, the who-did-what stack ~2.9s combined, affect +0.8s, goals +0.5s); reads are deterministic + stateless across docs.
- **INFERRED (you must measure):** the exact minimal profile per knowledge store (which dimensions each ingest needs), the parallel throughput scaling (cores × the remote box), and that the kept-dimension extraction is byte-identical to the full read.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: read `notes/KNOWLEDGE_LEVER_MAP_AND_LEARNER_STRATEGY_2026-09-04.md` (what the ingest harvests) + `tools/reader_capabilities.py` (the flags) + `hdlab/situation_reader.py` (`all_capabilities_off`, the CAPABILITY_FLAGS list, the per-read cache reset). Reproduce the 5.3x lean vs full + the per-dimension cost profile first-hand.
- Check the existing remote dispatch (`tools/queue_add.py` + the "heavy runs go remote" discipline) — the parallel harness should compose with it.

## THE BAR (can-fail; correctness = byte-identical on the kept dims)
PASS = a named lean "ingest profile" (or a small set of presets) that keeps only the requested extraction, byte-identical to the full read on those dimensions, at the measured ~5x; PLUS a process-parallel corpus-read harness whose per-doc output is identical to serial and whose throughput scales ~linearly with cores (report the measured scaling + a 10k-doc projection). A located NEGATIVE — a dimension cannot be cleanly leaned out (a hidden cross-dimension dependency), or reads are not safely parallel (a shared-state hazard), with the named cause — is a FULL PASS. Strategy lands the Q111 config + harness.

## ALREADY TRIED / DO NOT REDO
- `all_capabilities_off()` EXISTS (the lean baseline) — build the NAMED profiles + the harness on it, do not re-derive the flag plumbing.
- The per-read tag/parse cache + the shared front-end are landed — the parallelism is CROSS-DOC (processes), not intra-read; do not try to thread the pure-Python parser (GIL-bound).
- Do NOT change any dimension's OUTPUT — this is a config + harness, byte-identical on the kept dims.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/` + a small `tools/` harness. REUSE `hdlab/situation_reader.py` (`all_capabilities_off`, CAPABILITY_FLAGS), `tools/queue_add.py` (remote). Add a witness asserting kept-dimension byte-identity lean-vs-full + serial-vs-parallel. Strategy lands the config/harness.

## DO NOT QUOTE
- Do NOT quote a speedup without asserting the kept-dimension extraction is byte-identical to the full read.
- Do NOT quote parallel throughput without confirming per-doc output identical to serial (no shared-state corruption).
