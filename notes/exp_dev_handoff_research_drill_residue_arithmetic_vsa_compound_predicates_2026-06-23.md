# exp_dev hand-off — research: residue-arithmetic VSA for compound arithmetic predicates

**Filed-by:** research (Opus 4.7 1M context)
**Date:** 2026-06-23
**Trigger:** `notes/research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md` (residue-arithmetic-VSA drill — next-drill from predicate-evaluation-primitives drill).
**Pause state:** check `data/orchestrator_paused.flag` before any dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: this handoff names anchors and gives context pointers, NOT inlined experiment design. exp_dev owns the design.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY — pre-build infrastructure validator)

- **Anchor pointer:** `substrate_rhc_minimum_viable_v1`
- **Substrate-product reading:** validates that substrate CAN host residue-arithmetic VSA at minimum-viable scale (K=4 small primes; dynamic range 0-1155) BEFORE committing to the full ~500-1000-line infrastructure build. If smoke HARD_PASSes, substrate's calculator-class capability lane opens (SVAMP/GSM8K-class structural coverage ~70-95%). If smoke HARD_FAILs, substrate's arithmetic lane is structurally closed at this N_DIM regime — major routing decision.
- **Tier hint:** chain-grade if HARD_PASSes (validates infrastructure); MEASURED_MECHANISM if PARTIAL (some paths work, not all); HARD_FAIL routes to glass-box-LLM L2 closure for arithmetic.
- **Why-now:** parent predicate-evaluation drill (`research_drill_predicate_evaluation_primitives_2026-06-23.md`) explicitly identified residue-arithmetic VSA as the next-drill candidate AND explicitly excluded compound arithmetic from its 5-op set as out-of-scope. RHC fills the excluded class. Per Kymn et al. 2024 Neural Computation (peer-reviewed framework). Per USER 2026-06-23 substrate-only product direction (calculator-class QA requires arithmetic primitives).
- **Routing:** local_cpu_queue (cheap; smoke ~5-15 min CPU; full cell ~30-60 min)
- **Pre-condition:** ~300 lines new substrate code for smoke (`hdlab/qfhrr.py` minimal + `hdlab/rhc.py` minimal + resonator decoder lifted from existing experiments). exp_dev to determine smoke-cell author vs new-code authoring sequence.
- **Pre-reg HARD bands:** see L5 of the research note (4 arms × 3 predicates × 100 trials × 3 seeds; HARD_PASS = A2 OR A3 OR A4 ≥ 0.80 on each of P1, P2, P3; HARD_FAIL = all 3 substrate-compatible paths < 0.80 on any predicate; A1 sanity-control must FAIL < 0.20).

### Anchor 2 (CONDITIONAL — if Anchor 1 HARD_PASSes, validates KG integration)

- **Anchor pointer:** `substrate_rhc_kg_attribute_storage_v1`
- **Substrate-product reading:** validates RHC integer-encoded numerical attributes can be stored in and retrieved from the substrate's KG layer (h_hotpotqa lineage). Extends storage layer to support RHC-encoded values for ages, years, counts, amounts.
- **Tier hint:** chain-grade if HARD_PASSes; depends on Anchor 1.
- **Why-now:** required before any real-corpus RHC test (Anchor 3). Without KG storage integration, RHC is isolated from substrate's atom store.
- **Routing:** local_cpu_queue.
- **Pre-condition:** Anchor 1 HARD_PASS + `hdlab/store/atoms.py` extension for RHC-encoded numerical attribute fields (~100-200 lines).

### Anchor 3 (CONDITIONAL — if Anchors 1+2 HARD_PASS, real-corpus validation)

- **Anchor pointer:** `substrate_rhc_svamp_pilot_v1`
- **Substrate-product reading:** validates substrate-only product on SVAMP-class arithmetic word problems (100-question subset). Composes RHC + 5-op predicate set + MiniLM-L6 encoder for end-to-end calculator-class QA. First test of substrate's structural-vs-actual coverage gap (encoder-side bottleneck).
- **Tier hint:** chain-grade if em ≥ 0.20 (vs random-guess ~0.001); MEASURED_MECHANISM if 0.05-0.20; HARD_FAIL if < 0.05 (encoder is dominant bottleneck).
- **Why-now:** first substrate-only product surface in calculator-class. Major USER directive alignment.
- **Routing:** remote_cpu or local_cpu (depends on encoder load).
- **Pre-condition:** Anchors 1+2 HARD_PASS + 5-op predicate set landed + MiniLM-L6 encoder integrated.

---

## Context pointers (file paths; not summaries)

- `notes/research_drill_residue_arithmetic_vsa_compound_predicates_2026-06-23.md` (this drill — full spec)
- `notes/research_drill_predicate_evaluation_primitives_2026-06-23.md` (parent — 5-op set scope and arithmetic exclusion)
- `notes/exp_dev_handoff_research_drill_predicate_evaluation_primitives_2026-06-23.md` (parent handoff — 5-op set anchor; predecessor in priority)
- `notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` (substrate bind is involutive — depth-lossless; relevant for RHC chain noise analysis)
- `experiments/exp_comparator_resonator_primitive_smoke_v1.py` (existing resonator framework; partial — needs lift to `hdlab/resonator.py`)
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` (per-arm metrics from comparator smoke)
- arxiv 2311.04872 / PMC10659444 (Kymn et al. 2024 Neural Computation — primary RHC reference)
- arxiv 2511.08767 (Tomkins-Flanagan-Kelly 2025 Vector-Symbolic Lisp — upper bound on RHC+VSA expressivity)
- arxiv 2604.25939 (qFHRR — substrate-compatible bridge to RHC)
- arxiv 2412.00488 (FPE cleanup — for Path A FPE-log construction in smoke arm A2)

---

## Contract section

exp_dev to:
1. Read this handoff + the research note + parent handoff.
2. Decide on cell-author sequencing: substrate-code-first (author `hdlab/qfhrr.py` + `hdlab/rhc.py` minimal) THEN smoke cell, OR cell-author smoke directly using stub primitives. exp_dev's call.
3. Author and pre-flight `substrate_rhc_minimum_viable_v1` per the HARD-band pre-reg specified in research note L5. NO experiment-design inlining beyond the band-spec.
4. Ship via `tools/queue_add.sh local_cpu_queue substrate_rhc_minimum_viable_v1` (or equivalent routing).
5. Post-ship REMOTE VERIFY (check `data/exp_substrate_rhc_minimum_viable_v1/metrics.json` per-arm metrics; do NOT trust verdict_msg per [[feedback-fix28-verify-per-arm-metrics-not-summary-verdict-text]]).
6. Self-test per formula-selftests if applicable.

PRIORITIZATION: parent's `substrate_predicate_primitive_set_v1` (5-op set) should land FIRST. RHC smoke is the LOGICAL NEXT after 5-op set chain-grades or HARD_FAILs (the routing depends on parent outcome). If parent HARD_FAILs, RHC ROI drops sharply (parse-side bottleneck dominates regardless of arithmetic primitives).

If pause flag set: defer. Filed for visibility regardless.

---

## Autonomy declaration

exp_dev owns all of:
- Cell-author smoke design beyond the HARD-band pre-reg
- Substrate-code-first vs cell-first sequencing
- Smoke vs full cell budgeting
- Routing (local_cpu vs remote_cpu vs overnight_queue) — research recommends local_cpu_queue but exp_dev may override
- Implementation details of qFHRR/RHC minimal primitives if cell-author-first sequencing is chosen
- Per-arm code-path decisions in the smoke cell

Research has scoped the discriminator (4 arms covering the 3 substrate-compatible paths + 1 reference oracle), the HARD-bands, the prediction set, and the substrate-product implications. Implementation details are exp_dev's call.
