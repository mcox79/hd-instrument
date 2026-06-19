# Research -> Testbed: User authorized 3 actions -- per-token Pythia + KG/QA datasets + GPU runner inspection

**From:** Research session
**To:** Testbed (primary)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-05 ~08:30
**Subject:** User explicitly authorized 3 actions this morning. All 3 unblock high-value empirical cells.

---

## Authorizations (user confirmed 2026-06-05 ~08:30)

### Action 1: AUGMENT Pythia extraction script with --per-token flag + re-run

User AUTHORIZED.

Per Exp-Dev's 00:25 note: current npz is per-doc (shape (n, 768)) -- final-token activations only. EX-CONCEPT-1 REAL needs per-token sequences within docs.

Spec:
- Augment `experiments/exp_phase05_v1_pythia160m_residual_extract_v1.py` with `--per-token` flag
- When set: extract `hidden_states[12]` for ALL token positions (not `[:, -1, :]`)
- Clip to MAX_TOK_LEN=64 (existing) or extend to 128 if richer sequences desired
- Output: `residuals_per_token.npz` with shape (sum_T_clipped, 768) + doc_indices + token_offsets sidecar
- Keep per-doc HARD_PASS preserved (different output filename)

Expected wall: ~15-30 min on remote 4060 Ti (Pythia-160M is small; same model load).
Cost: $0.

Output destination: `data/exp_phase05_v1_pythia160m_residual_extract_v1/residuals_per_token.npz`

Unblocks: EX-CONCEPT-1 REAL (substrate trained on per-token Pythia concept-ID sequences).

### Action 2: DOWNLOAD offline KG/QA datasets to runner

User AUTHORIZED.

Datasets needed (all free public; small downloads):
- **HotpotQA** (~1k multi-hop Q&A pairs; ~50 MB)
  - https://hotpotqa.github.io/ -- HotpotQA distractor dev set is sufficient (1k examples)
- **Natural Questions multi-hop subset** (~1k multi-hop questions; ~50 MB)
  - HuggingFace `google/natural-questions`; filter to multi-hop (questions with >=2 answer sources)
- **Wikidata triple subset** (~50k subject-predicate-object triples; ~10 MB compressed)
  - Wikidata SPARQL endpoint; query top-K entities + relations; export as JSON
  - OR HuggingFace dataset `bigbio/wikidata5m` subset

Spec:
- Download to `data/datasets/` on Testbed local
- scp to runner at `C:\dev\hd-instrument\data\datasets\`
- Verify each loadable + format-correct on runner
- Note: Wikitext loader has HfUriError; need offline-only versions for these

Expected wall: ~1-2h (downloads + scp).
Cost: $0.

Unblocks: CCC-1 REVISED-v2 (smallest viable cognitive-core test at Pythia-160M tier) + CCC-1-EXTRA (KG relational reasoning).

### Action 3: INSPECT GPU runner for capacity-comp silent failures

User AUTHORIZED.

Per Exp-Dev's 03:45 note: capacity-comp N=4096/N=8192 GPU failed 3x with no logs/metrics. Script passes --self-test + smoke; problem is GPU-runner infra.

Diagnostic procedure:
- `nvidia-smi` -- check for stale processes, memory pressure
- Check for any leftover Python processes from killed runs (`Get-Process python*`)
- Clear CUDA cache if needed (`torch.cuda.empty_cache()` in startup)
- Verify disk space + I/O healthy
- Check stdout/stderr capture is working (Testbed scripts use tee; runner should be doing same)
- Try one capacity-comp run with verbose `python -u` + `tee` + heartbeat flush

Expected wall: ~30-60 min Testbed work.
Cost: $0.

Unblocks: capacity-comp scaling beyond N=2048 (lower priority -- 125k patterns already validated at N=2048 multiplicative composition).

---

## Priority order (per user's strategic focus)

User's strategic focus this morning: substrate cognitive-core at Pythia-160M tier with real reasoning data + training-speed optimization.

Recommended Testbed sequence:
1. **Action 1 (Per-token Pythia)** -- highest priority; quickest (~15-30 min); unblocks substrate cognitive-core
2. **Action 2 (KG/QA datasets)** -- second priority; ~1-2h; unblocks substrate vs LLM head-to-head test
3. **Action 3 (GPU inspection)** -- third priority; lower urgency; unblocks scaling but not strategic-critical

Actions 1 + 2 are the gate for CCC-1 REVISED-v2 which is the load-bearing empirical test of substrate cognitive-core vs Pythia-160M baseline.

---

## STILL pending user action: UMLS license registration

Separate from the 3 above:
- UMLS = Unified Medical Language System; NIH/NLM
- Free for research; 5-min form at uts.nlm.nih.gov
- Approval 1-3 business days
- User to register; not delegating to Testbed

When UMLS approves: Medical Path Y prototype becomes buildable (first domain-specialized substrate cognitive core).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Testbed primary on infra + data + model extraction
- Per [[feedback-cloud-only-when-absolutely-necessary]]: all 3 actions $0
- Per user authorization 2026-06-05 ~08:30
- ASCII-only

---

**END.**

**Testbed:** 3 user-authorized actions queued. Recommend per-token Pythia first (quickest unblock). Standing for your bandwidth.

**Exp-Dev:** when per-token Pythia npz lands, build EX-CONCEPT-1 REAL + CCC-1 REVISED-v2. When KG/QA datasets land, build CCC-1-EXTRA KG reasoning test.

**User:** all 3 authorizations routed to Testbed. UMLS license registration is the remaining user action item (separate; user to do directly).
