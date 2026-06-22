# Research (Director) handoff snapshot — 2026-06-22 (pre-compaction)

For fresh Research/Director teammate spawning after compaction.

## 1. SUBSTRATE STATE (live; CERT 588, pending 589 via p1 atomization in flight)

- **CERT N:** 588 (will be 589 once p1 atomization spawn a559f... [no — that was HotpotQA; check active spawns] completes)
- **Atoms:** 177284 (will be 177285 post-p1)
- **Cert_ledger rows:** 654
- **axiom_term:** 206 / **cap_pres:** 6/6 / **honest floor:** ~440 PASS-family

## 2. TODAY'S CHAIN-GRADE TRAJECTORY (CERT 584 → 589 over one autonomous arc)

| CERT | Cell | What |
|---:|---|---|
| 585 | n8 ConceptNet | lexical English KG; 36.5× vs frozen-encoder; OPEN-C unlocked |
| 586 | c3 compressed-sequence-replay | substrate's MISSING sequence-binding primitive; S matrix |
| 587 | g1b capacity-sweep | substrate-native autoregressive generation above by-construction-saturation; chain-grade via headroom-to-fail |
| 588 | HotpotQA ingest | multi-hop Wikipedia QA; 892× over 1-hop; 3rd KG shape at chain-grade |
| 589 (pending) | p1 phase-diagram-action | substrate content survives operating-point shifts (V_C / N_DIM / joint lift); USER-directed lane chain-grade |

Multi-domain chain-grade KG portfolio NOW: U1 FB15k-237 (584) + n8 ConceptNet (585) + HotpotQA (588) = 3 distinct KG shapes at chain-grade.

## 3. hdlab/ SUBSTRATE PRIMITIVES SHIPPED THIS ARC (6 of 7 backlog closed)

- `hdlab/sequence_memory.SequenceMatrix` (c3 payload; CERT 586)
- `hdlab/kg_traversal.KGStore` (n8/U1 payload; CERT 584+585+588)
- `hdlab/multi_hop.iter_cleanup_chain` (r1 payload)
- `hdlab/whitening.WhiteningTransform` (4 chain-grade atoms)
- `hdlab/char_trigram_encoder.CharTrigramEncoder` (substrate-native text encoder; zero external model)
- `hdlab/generation.SubstrateGenerator` (g1/g1b payload; CERT 587)
- **REMAINING:** `hdlab/refuse_gate.py` standalone + `hdlab/conformal.py`

## 4. SUBSTRATE-NATIVE BIDIRECTIONAL CONVERSATION — chain-grade at every layer

Path: English text → char_trigram_encoder (zero LLM) → KGStore single/multi-hop retrieval → SubstrateGenerator emits entity sequence → output. Each layer has chain-grade primitive evidence. The L5 MOAT path.

Dashboard chat live (commits 4f6e2ba5 + ad597d69 + 0667fcdb + 48b7c419): 4 modes (English MiniLM / Structured / `/substrate <text>` char-trigram / `/walk <entity>` graph generation).

## 5. ACTIVE EXPERIMENTS (in flight; check `tools/landing_notifier.py` for arrivals)

- **substrate_self_map_v2 cell-author** (spawn a591dc59) — substrate-native self-mapping via char_trigram + KGStore + multi_hop on cert_ledger relations; ~30-40min total; the TRUE Phase 1 self-improvement work
- **p1 atomization Skunkworks** (just-fired) — CERT 588→589 ratification
- **All others LANDED** (n4 HARD_FAIL, m1 MIDDLE_BAND smoke, c_composition v1 HARD_FAIL discriminator-invalid, g1b HARD_PASS, HotpotQA HARD_PASS, p1 HARD_PASS full)

## 6. DISCIPLINES BANKED THIS ARC (Fixes #20-25)

- #20: Foreground execution for sequential Store+ledger writes
- #21: Poll filesystem for remote-landed cells (`find data -mmin -N`)
- #22: GPU routing — N_DIM≥8192 / matmul-bound → hdi_orchestrator
- #23: Cell-author smoke + Fix #17 measurement on remote (not laptop) for heavy cells
- #24: GPU dispatch must use torch.cuda + batched ops + encoder-hoisted + ≥50% steady-state util
- #25 (NEW, just banked): Landing-notifier `tools/landing_notifier.py` — scheduled-task companion that scans for new metrics.json + appends to `data/recent_landings.jsonl`; Director reads at every turn-start. **TODO: register as scheduled task to run every 2-5 min.**

Also banked: cert-owner-overrides-Director (by-construction-saturation tiering) + substrate-mine-before-extrapolating (USER caught the storage-density-claim error) + no-inter-session-routing-notes (3rd correction; ferry mechanism DEPRECATED) + results-to-application cadence (same-cycle atomize + hdlab update)

## 7. USER STRATEGIC VISION (banked 2026-06-22)

`project_user_strategic_vision_self_improvement_portal_core_mathematics_USER_2026-06-22.md`

Three load-bearing directives:
1. **Per-gap research drills** — substrate-mine + brain/matsci per backlog primitive; queued, not yet fired
2. **Portal v1+v2+v3** — all SHIPPED (KG REPL + MiniLM English chat + substrate-native char-trigram)
3. **Phase 1 substrate self-improvement** — v1 Director-scaffolding committed + RELABELED (it was NOT substrate self-improvement; USER correctly pushed back); v2 substrate-native (uses char_trigram + KGStore + multi_hop) in flight (a591dc59)

## 8. CURRENT WORK QUEUE (what to drive next)

After p1 atomization lands (~5 min) + substrate_self_map_v2 lands (~30 min):
- Ship `hdlab/refuse_gate.py` standalone + `hdlab/conformal.py` (closes 7/7 backlog) — main thread; no spawn
- Brain-drills #2 CLS + #3 multi-hop 5x DEEPER (USER strategic vision cadence; queued; never fired) — Sonnet research drill
- MedQA v2 with learned-projection (revival of MedQA HARD_FAIL today) — hdi_exp_dev
- Path A V_C=4096 revival drill (route-negatives) — research drill
- HumanEval revival drill — research drill
- r1b revival drill — research drill
- p1 v2 (deeper N + larger K; verify portability at LLM-class scale) — hdi_orchestrator → GPU
- modern_hopfield_xl revival at scale (chain-grade upper bound; super-linear capacity at LLM scale) — hdi_orchestrator → GPU
- Substrate-as-LLM scaling cells (target ~50GB substrate at compound chain-grade for ~100M facts) — long horizon

## 9. KEY DASHBOARD URLs

- Local: `http://localhost:8765`
- Tailscale: `http://100.124.176.29:8765` (raw IP) or `https://frameworkmpc.tail37031e.ts.net/` (HTTPS via tailscale serve which is configured)
- Legacy 9-tab dashboard preserved at `/legacy`

## 10. WHAT THE USER CARES ABOUT (latest context)

- Substrate-as-LLM-substitute storage density: 4× chain-grade today, ~10-100× compound (chain-grade-evidence in `EXP_substrate_capacity_composition_full_b2xb4xhier` and siblings at N=2048)
- Substrate self-improvement (Phase 1 v2 cell in flight is the real test)
- GPU efficiency (Fix #24 banked; future spawns mandate torch.cuda + batched ops)
- Remote landings notification (Fix #25 banked + landing_notifier.py shipped; needs scheduled-task registration)
- When can we converse with substrate without MiniLM (substrate-native `/substrate` and `/walk` modes shipped today)

## 11. SUSPENDED / DEFERRED

- c_composition v2 cell exists on remote (commit 6f7979bc) but NOT dispatched; USER said skip per "don't waste GPU just because"
- m1 / p1 full runs already dispatched (p1 LANDED HARD_PASS; m1 still in queue per timing report)
- 3 orchestrator spawns were killed (c_comp v2, modern_hopfield_xl, n10) — don't re-fire unless explicit reason; n10 already had a HARD_FAIL result from earlier

— Research (Director); end-of-arc snapshot; resume from here.
