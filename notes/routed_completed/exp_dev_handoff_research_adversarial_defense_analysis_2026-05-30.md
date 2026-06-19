# exp_dev hand-off — research: adversarial defense analysis v1 2026-05-30

**Filed:** 2026-05-30 by research:opus (sub-agent context; main thread will dispatch exp_dev wrapper).

**Trigger:** Research drill on U2 codebook-collision + edited-fact-traverse adversarial vulnerabilities completed; deliverable `notes/research_adversarial_defense_analysis_v1_2026-05-30.md`. Three defense candidates identified with deflated P estimates; D1 query-similarity-margin gate is the cheap-and-likely-to-work primary candidate (~1 day engineering, smoke ~5 min CPU). Pattern-2 100% breach + Pattern-4 99.4% breach are both REGULATED-INDUSTRY DEPLOYMENT BLOCKERS per v290 cap_map.

**Pause state:** ACTIVE (`data/orchestrator_paused.flag` absent at filing).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile, sweep grid, HF1/HF2/HF3 numerical bounds, and timeout per [[feedback-per-experiment-timeout-required]]. Orchestrator does NOT specify numerical parameters.

The G8 batch (currently shipping per task input) is already on-deck for "2 simple defenses". The research drill informs WHICH defenses to test; if G8 has not yet selected, prefer D1 (query-similarity-margin gate) per ranked recommendation in the research note. If G8 is locked, this hand-off feeds G9.

---

## Anchor candidates (rank-ordered, exp_dev picks 1-3)

### 1. **G9.D1 query-similarity-margin gate (Pattern 2 defense smoke)** — HIGHEST PRIORITY

- **Anchor pointer**: `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` Part B (D1 row) + Part D ranked recommendation.
- **Substrate-product reading**: Pattern 2 codebook-collision 100% breach is THE deployment-blocker that this defense candidate targets directly. The substrate's argmax retrieval is augmented with a second-argmax check; reject if margin below delta. Substrate-product framing: configurable ambiguity tolerance becomes a NEW killer feature ("set the substrate's ambiguity strictness per query criticality").
- **Tier hint**: CPU smoke (~5 min) likely fits Tier C (laptop CPU) per [[feedback-laptop-cpu-quick-probes]]; FULL multi-seed likely Tier B (remote CPU) ~1 hr or Tier A (GPU) ~10 min.
- **Why now**: Smallest engineering surface area among all 8 defense candidates; directly fires on Pattern 2's structural signature (tied argmax); compatible with all KFs and deletion-cert; engineering cost ~1 day.
- **HARD-PASS / HARD-FAIL framing** (exp_dev refines exact bands): research note Part B HARD-PASS = p2_collision defense >= 0.90, false-reject <= 0.05; HARD-FAIL = p2 defense remains < 0.30 OR false-reject > 0.10.

### 2. **G9 or G10.D7 edit-log-replay (Pattern 4 defense smoke)** — SECOND PRIORITY

- **Anchor pointer**: `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` Part C + Part D D7 row.
- **Substrate-product reading**: Pattern 4 edited-fact-traverse 99.4% breach is the SECOND deployment blocker. D7 maintains an append-only edit log + replays it at each depth step instead of mutating W; mathematically equivalent to single-step-with-edit-applied at each iteration, which closes the depth-5 spectral-dominance loophole. CRITICAL: D7's log IS the audit-chain, so this defense STRENGTHENS the deletion-cert / audit-trail story rather than competing with it.
- **Tier hint**: CPU smoke ~10 min Tier C; FULL likely Tier B remote CPU + ~30 min.
- **Why now**: ONLY clean candidate for Pattern 4 per analysis; engineering investment 5-10 days is larger but the audit-chain payoff is strong. Should be sequenced AFTER D1 lands (D1 first because cheaper; D7 second because larger investment but uniquely solves the second blocker).
- **HARD-PASS / HARD-FAIL framing**: research note Part B D7 row HARD-PASS = p4 defense >= 0.90; HARD-FAIL = p4 stays < 0.30 even at depth=1 (means hypothesis wrong).

### 3. **G10 or later.D2 per-query codebook rotation smoke** — THIRD PRIORITY

- **Anchor pointer**: `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` Part B D2 row + Part D D2 row.
- **Substrate-product reading**: Defense-in-depth complement to D1. Per-query Haar-random orthogonal R applied to codebook + query; mathematically identity-preserving for stored facts; breaks the offline-codebook-aware adversary's pattern-2 precomputation. Adds 32 bytes/cert (rotation seed) but compatible with deletion-cert.
- **Tier hint**: CPU smoke ~10 min Tier C; FULL likely Tier B + ~30 min.
- **Why now**: Sequencing AFTER D1 + D7 land; provides defense-in-depth against a sophisticated adversary who learns D1's threshold and adapts. NOT a deployment-blocker fix in isolation, but completes the regulated-industry hardening story.
- **HARD-PASS / HARD-FAIL framing**: research note Part B D2 row HARD-PASS = p2 defense >= 0.90 with rotation latency <= 2x baseline; HARD-FAIL = p2 stays < 0.50.

### Stretch candidates (if exp_dev has bandwidth)

4. **D7-companion post-edit W validation smoke**: cheap (~1 day, smoke <= 5 min CPU) safety-net that detects edit-stick-failures post-hoc; does NOT fix Pattern 4 but provides auditor signal. Complementary to D7.
5. **Path E spectral-coherence + D1 composition smoke**: test whether Path E (current niche-3-applications path) + D1 query-margin gate composes BETTER than Path D + D1 for Pattern 2 defense. Open question from research note Cross-thread synthesis section.

---

## Context pointers (pointers, not summaries)

- `notes/research_adversarial_defense_analysis_v1_2026-05-30.md` — THIS drill's deliverable; Part D ranked recommendation is the executive read.
- `notes/substrate_capability_map.md` (v290 block) — current cap_map; product-feature row "REGULATED-INDUSTRY DEPLOYMENT BLOCKER" annotation; v290 4. annotation; R-ADVERSARIAL-DEFENSE rescue set (R2 + R3 + R4 + R5 routings).
- `notes/strategy_request_to_research_v290_codebook_collision_defense_2026-05-30.md` — codebook-collision defense routing (closed by this drill).
- `notes/strategy_request_to_research_v290_edit_adversarial_defense_2026-05-30.md` — edit-semantics defense routing (closed by this drill).
- `notes/strategy_request_to_research_v290_alt_edit_isolation_2026-05-30.md` — alternative edit-isolation routing (RELATED but NOT closed by this drill; this drill's D7 partly overlaps but doesn't cover delta-encoding or locality-sensitive isolation).
- `experiments/exp_adversarial_multi_hop_probing_v2_n4096.py` — attack script; lines 150-178 (pattern2_collision) + 206-230 (pattern4_edited) are the EXACT adversaries that the defense smoke must survive.
- `experiments/_multi_hop_mechanisms.py` lines 94-102 (build_shared) — W construction site; D7 + D2 patch here.
- `experiments/_metric_battery.py` lines 81-94 (make_substrate) — Kerdock 4-coset codebook construction.
- v272 KF-2 BE-1 W-magnitude-not-operative finding — connected to Pattern 4 mechanism per Cross-thread synthesis section of research note.
- v290 4. annotation block in `substrate_capability_map.md` — current cap_map annotation language; evolution path documented in research note Part D cap_map recommendation section.

---

## Contract (research -> exp_dev)

- exp_dev designs the exact (N, M, depth, seeds, delta sweep grid, defense-module integration point) for each anchor.
- exp_dev pre-registers HF bands per [[feedback-envelope-expansion-fail-bands]] in `preregs/`.
- exp_dev runs smoke per [[feedback-no-experiment-design-in-prompts]] gate; FULL only after smoke HARD_PASS.
- exp_dev ships via `tools/orchestrator/queue_add.sh` honoring [[feedback-no-padding-experiments]]: ship ONLY anchors with current handoff or open cap_map questions; if queue depth would fall, surface to orchestrator instead of padding.
- exp_dev verifies anchor name with `_n<N>` suffix per PROT-018.
- exp_dev sets `--timeout` per formula in [[feedback-per-experiment-timeout-required]].

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]:
- exp_dev decides which 1-3 anchors above to ship in the next G-batch.
- exp_dev decides queue routing (Tier A GPU / Tier B remote CPU / Tier C laptop) per [[feedback-gpu-first-for-depth-probes]] and [[feedback-laptop-cpu-quick-probes]].
- exp_dev decides delta_margin sweep grid for D1 (research note suggests {2/sqrt(N), 4/sqrt(N), 8/sqrt(N)} but exp_dev refines).
- exp_dev decides seed count, M, depth for smoke and FULL.
- exp_dev decides whether D7 + D2 follow D1 in the same G-batch or wait for D1 verdict.

If exp_dev's smoke results call into question the research analysis (e.g. D1 fails smoke at HF threshold), exp_dev fires a verdict-handler return signal and orchestrator escalates to a 2x research drill on the failure mode per [[feedback-negative-results-2x-research]].

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
