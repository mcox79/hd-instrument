# Testbed -> Exp-Dev: canonical-remote RUN BUNDLE ordered ship-list -- 23 tools queued for one-pass materialization

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Ordered concrete-command list so Exp-Dev can materialize 23-tool session in a single coordinated run.

## How to use this

Each item below has: (a) the canonical-remote command (b) expected runtime (c) what it produces. Run sequentially OR pick subset; each is independent so failures don't cascade.

Setup: ensure you're on canonical-remote substrate (20820 atoms; branch `origin/testbed-cycle50-option-b` tip `99c9bc5d`).

```bash
cd /path/to/canonical/hd-instrument
git fetch origin
git checkout testbed-cycle50-option-b
git pull origin testbed-cycle50-option-b
# verify branch tip
git log --oneline -1   # should show 99c9bc5d or later
```

## Bundle A: high-leverage / fast (~30 min total)

### A1 — Held-out benchmark verdict (15 min)
```bash
# Per held-out routing note: use production bench script which has v3 refuse heuristic
HDLAB_QA_BENCH_PATH=experiments/data/gap7_benchmark_v1_HELD_OUT_q54_q65.jsonl \
  python experiments/exp_qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1.py
# Or my fallback degraded scorer (no production v3 refuse):
python tools/substrate_score_held_out_benchmark_v1.py --update-scorecard
```
**Produces:** macro F1 + per-axis F1 + Q_neg_2 honesty verdict on canonical 20820. Replaces the local-CPU-degraded 0.0533 with the real number.

### A2 — Authoring priority queue at scale (1 min)
```bash
python tools/substrate_authoring_priority_queue_v1.py
```
**Produces:** `data/authoring_priority_queue_v1.json` top-100 ranked atoms on 20820 substrate. Local TOP-1 was `T2/cleanup` fanin=53; canonical will be richer.

### A3 — BATCH 17 ingest (1 min)
```bash
python tools/substrate_t1_algebra_batch_17_depth3_4_depends_on.py
```
**Produces:** +4 T1 atoms (recursion, optimal_substructure, discrete_fourier_transform, complex_field) + 30 DEPENDS_ON edges across 10 flagged 62pct authoring-gap leaves. KP P5 unblock + L6-PROOF depth jump 1.30 → 2.5+.

### A4 — SHARES_MATH auto-discovery (~3 min wall on 20820)
```bash
python tools/substrate_shares_math_auto_discovery_v1.py
```
**Produces:** `data/substrate_index/bench_reports/shares_math_auto_discovery_candidates.json` with 200-500 expected SHARES_MATH candidates. Unblocks KP P3 + Pi/Sigma + CHTV-2.

### A5 — Monitor cap-map + regression check (1 min)
```bash
python tools/substrate_scorecard_schema_v1.py --summarize
python tools/substrate_monitor_cap_map_v1.py
python tools/substrate_regression_baseline_check_v1.py
python tools/substrate_scorecard_analytics_v1.py
```
**Produces:** recursive-loop Stage 1+6 outputs. Issue list + verdict + analytics for cycle-close synthesis.

## Bundle B: LANE A breadth ingest (~12 hours total; can run overnight)

### B1 — Wikidata math via mapper v2 (~6 hours)
```bash
python tools/substrate_ingest_pipeline_runner_v1.py \
    --facts-jsonl data/substrate_state/wikidata_truthy_50m/facts.jsonl \
    --corpus wikidata --partition wikidata::truthy \
    --output-prefix data/substrate_state/wikidata_v2_math \
    --filter math --vocab-mode qclass
```
**Produces:** 170K-510K math atoms; full LANE A breadth-ingest test.

### B2 — ConceptNet math/science (~1 hour)
```bash
python tools/substrate_ingest_pipeline_runner_v1.py \
    --facts-jsonl data/substrate_state/conceptnet_8m/facts.jsonl \
    --corpus conceptnet --partition conceptnet::all \
    --output-prefix data/substrate_state/conceptnet_v2 \
    --filter science --vocab-mode word
```

### B3 — arXiv ML / PubMed (~2 hours each)
Similar pattern with `--corpus arxiv` / `--corpus pubmed`.

### B4 — Wikipedia math-subset (~3 hours)
```bash
python tools/substrate_ingest_pipeline_runner_v1.py \
    --facts-jsonl data/substrate_state/wikipedia_100k/facts.jsonl \
    --corpus wikipedia --partition wikipedia::math \
    --output-prefix data/substrate_state/wikipedia_v2_math \
    --filter math --vocab-mode word
```

### B5 — OEIS resume (~5-8 hours)
```bash
python tools/substrate_ingest_oeis_v1.py --full
```
**Produces:** +350K remaining OEIS sequences (18,952 already ingested; skip-existing).

## Bundle C: LANE B bedrock ingest (~3 days each; can run in parallel)

### C1 — Mizar Mathematical Library (~5 days build + ingest)
```bash
# First-time auto-download (or supply --mizar-tarball if URL unreachable)
python tools/substrate_ingest_mizar_library_v1.py
# Then ingest via adapter + Phase 6 (use pipeline runner with --skip-mapper --skip-merge)
python tools/substrate_ingest_pipeline_runner_v1.py \
    --facts-jsonl data/substrate_index/mizar_mml_atoms_shard_0000.jsonl \
    --corpus wikidata --partition math_foundation::mizar_mml \
    --output-prefix data/substrate_index/mizar_mml_atoms \
    --skip-mapper --skip-merge
```

### C2 — Lean Mathlib v2 (per-decl refs)
```bash
python tools/substrate_ingest_lean_mathlib_v2.py
# (clones mathlib4 first; ~500MB; ~30 min on fast network)
# Then chain through pipeline runner same pattern as C1
```

### C3 — Coq mathcomp + stdlib
```bash
python tools/substrate_ingest_coq_library_v1.py --libraries mathcomp coq_stdlib
# Then chain through pipeline runner
```

### C4 — ProofWiki (needs working dump URL; my candidates may be stale)
```bash
# If you have a ProofWiki XML dump file:
python tools/substrate_ingest_proofwiki_v1.py --xml-dump /path/to/dump.xml
# If dump URL works:
python tools/substrate_ingest_proofwiki_v1.py
# Then pipeline runner chain
```

### C5 — DLMF + MathWorld (manual HTML mirror; provide --dlmf-dir / --mathworld-dir)
```bash
python tools/substrate_ingest_dlmf_mathworld_v1.py \
    --dlmf-dir /path/to/dlmf_html --mathworld-dir /path/to/mathworld_html
# Then pipeline runner chain
```

## Bundle D: validation cells (~5 min total)

### D1 — Compose-fix demo
```bash
python tools/substrate_compose_fix_v1.py \
    --topic "cosine cleanup similarity" --axis C --capability concept::CAP_cleanup \
    --max-candidates 15 --max-fix-specs 5
```

### D2 — Find-relevant-knowledge
```bash
python tools/substrate_find_relevant_knowledge_v1.py "fourier transform circular convolution" \
    --top-k 10 --max-depth 2
```

### D3 — Recursive-loop end-to-end
```bash
python tools/substrate_recursive_loop_demo_v1.py
```

## Recommended run-order

For overnight cycle: **A1 → A2 → A3 → A4 → A5** (decisive verdicts; 30 min) → **B1** (largest atom payoff; 6 hours) → **C2** (Lean Mathlib; high USER-goal-alignment) → **D3** (validate recursive loop on post-ingest substrate).

If 24-hour wall: parallelize B2/B3/B4 alongside C1/C3 on separate cores.

## Verdicts to report back

For each command, please report:
1. Wall time + exit code
2. Atom delta + edge delta
3. Per-axis macro deltas (for A1 held-out + A5 monitor)
4. Any unexpected errors

## Bundle commit hashes (reference)

| Tool | Commit |
|---|---|
| BATCH 17 (A3) | f774c48d |
| SHARES_MATH (A4) | daa969e9 |
| priority queue (A2) | 5394d42e |
| find-relevant-knowledge | 21025d94 |
| mapper v2 (B*) | 3bb6c1a4 |
| adapter (B*) | e71edcd7 |
| held-out benchmark | 99ea2b08 |
| Mizar (C1) | 2e11edd8 |
| pipeline runner (B*/C*) | 10abb07e |
| Lean Mathlib v1 (C2) | 32e08e2a |
| compose-fix (D1) | 0a8aab70 |
| ProofWiki (C4) | f732475c |
| Coq (C3) | b05016cf |
| DLMF/MathWorld (C5) | 66e56ee8 |
| scorecard schema (A5) | 15ba20ff |
| monitor-cap-map (A5) | 15ba20ff |
| recursive-loop demo (D3) | 666265c0 |
| regression check (A5) | f8ee3a9e |
| held-out scorer (A1 fallback) | 50124338 |
| scorecard analytics (A5) | e654538b |
| Lean v2 (C2) | 99c9bc5d |

Tip: 99c9bc5d.

---

**Exp-Dev:** RUN BUNDLE ordered ship-list 23 tools queued for one-pass canonical-remote materialization + Bundle A 5 fast leverage commands 30 min total + Bundle B LANE A breadth ingest 12 hours overnight + Bundle C LANE B bedrock parsers 3 days each parallelizable + Bundle D validation cells 5 min + recommended order A1-A5 then B1 then C2 then D3 + verdicts to report back wall + atom/edge delta + per-axis macro delta + branch tip 99c9bc5d.
