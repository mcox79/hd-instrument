# DIRECTOR POST-COMPACTION DIGEST 2026-06-26 (read FIRST after compaction)

**Filed:** 2026-06-26 ~19:50 PDT
**For:** post-compaction me
**How to find this:** `python tools/director_kb_query.py "post-compaction digest 2026-06-26"`

## SESSION-START RITUAL (do these IN ORDER, FIRST)

1. **Touch heartbeat:** `touch d:/AI/hd-instrument/data/heartbeats/research.timestamp`
2. **Query substrate-KB:** `python tools/director_kb_query.py "current state in flight today"` — substrate is now the definitive source (USER directive 2026-06-26)
3. **Verify continuous-ingest scheduled task alive:** `schtasks /query /tn hd_director_kb_continuous_ingest` should show Status=Ready. Runs every 5 min via pythonw.exe (windowless).
4. **Re-arm notes_monitor per CLAUDE.md ritual:** `Monitor({command: "python D:/AI/hd-instrument/tools/monitor_arm.py research", persistent: true, timeout_ms: 3600000})`
5. **Check landings since session ended:** `find d:/AI/hd-instrument/data -maxdepth 2 -name metrics.json -mmin -120`

## TODAY'S LOAD-BEARING USER DIRECTIVES (memory entries; ALL standing)

1. **Substrate doesn't know language; stop testing against language until understanding-prerequisites exist** — `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
2. **Stage progression 1→2→3→4 don't skip** — `memory/feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md`
3. **Agent-spawn model ONLY; 4-session fleet is dead** — `memory/feedback_agent_spawn_model_only_4session_dead_USER_2026-06-26.md`
4. **Session start ritual** (provisional until KB query is chain-grade — now is, can skip raw markdown reads) — `memory/feedback_session_start_ritual_read_master_plan_and_critical_context_USER_2026-06-26.md`
5. **Substrate-as-Director-KB dogfood project** — `memory/project_substrate_as_director_kb_dogfood_USER_2026-06-26.md`
6. **Lean spawn prompts** — agents have detailed disciplines built in; don't re-state standing discipline in spawn prompts
7. **Confirm plan-affecting decisions** — USER wants me to ask before plan changes, concise, no jargon

## TODAY'S CRITICAL PIVOTS

**Language-prediction track CLOSED.** USER 2026-06-26 caught me chasing bigram-gap closure with elaborate statistical machinery on a substrate that doesn't understand language. Stage progression discipline reinforced: text8 BPC / bigram-gap / V_C-sweep / trigram-context are Stage 4 work; deferred until Stages 1-3 mature. Multiple language-ingest handoffs SUPERSEDED.

**Compositional understanding track OPENED.** Stage 3 work. Wave 1 (7 cells) green-lit; 3 dispatched today (cortex E-tensor / top-K composition / PC cleanup). Stage 1 SEMANTIC concept learner is chain-grade (5/6 arms PASS); use as load-bearing primitive.

**Substrate-as-Director-KB dogfood SHIPPED.** Substrate now stores its own context. Ingest (54k+ facts) + query (natural-English) + continuous-ingest (scheduled task) all working. The KB is the definitive source per USER 2026-06-26.

**Agent-spawn model only.** 4-session fleet is dead per heartbeats. Spawn hdi_<role> agents when work needs doing. Standing Fix #14 budget ≤3 in flight; USER authorized exceeding when justified.

## CORTEX STATE (the active substrate-research focus)

**Scaffolding WORKS (chain-grade):**
- TWO_TIER generational W (HARD_PASS today; brain analog: hippocampus + cortex)
- NREM replay (HARD_PASS)
- Partition routing (M=10M chain-grade)

**Content-extraction FAILS uniformly (8 mechanism attempts dead or in progress):**
- E-tensor v1 saturation: HARD_FAIL (regime too easy)
- E-tensor harder regime: HARD_FAIL wrong-direction (E_GATED HURTS rec_old by 21.7pp)
- E-tensor RETEST Fix B: HARD_FAIL structurally (cor(E,|W|)=0.984 — retrieval-driven importance signals are magnitude-coupled BY CONSTRUCTION, structural property)
- Cell B global downscale: HARD_FAIL (destroys older memories)
- STC selective: HARD_FAIL (can't pick right atoms)
- R-schema closed-form: HARD_FAIL
- Cortex schema extraction v1: MIDDLE_BAND (feature-schemas help, capability-schemas hurt)

**Alternative mechanisms now in flight / queued (8 candidates):**
- ANCHOR 5 edge-importance / PageRank centrality (top priority, structurally orthogonal to magnitude) — in flight
- 4x ANCHOR 2 ultrametric clustering (semantic clusters via chain-grade SEMANTIC learner) — in flight
- 4x ANCHOR 3 SOC criticality (Bak-Tang-Wiesenfeld sandpile) — reserve
- 4x ANCHOR 4 MDL turnover (info-theoretic compression) — reserve
- 2x ANCHOR 6 external homeostatic target (lognormal W-norm) — reserve, requires pre-reg reframe
- Counterfactual-utility (ablation-based) — reserve
- Surprisal-weighted bumps — reserve
- Random-projection witness — reserve

## IN FLIGHT NOW

- **hdi_orchestrator** (a35fea4731109db0c) — GPU dispatch of 3 phase-diagram cells (multi-hop depth 20-30 / WM K=32768 / V_C capacity sweep). New spawn id may differ.
- **hdi_exp_dev** (aa320f815bdd5c144 / a09bf62cad0b8a045) — cortex Anchor 5 edge-importance + 4x-Anchor 2 ultrametric
- **hdi_skunkworks** (a261d444d92c82f65) — landed-VET on 7 cells from Wave 1+1.5+1.6
- **Local CPU queue running:** language trio (finishing full) + bio/neuro trio (queued behind)

## WAVE 3 BOUNDED-CAPACITY KB (handoff filed; gated)

- Filed at `notes/exp_dev_handoff_research_kb_bounded_capacity_wave3_USER_GREENLIT_2026-06-26.md`
- Architecture: TWO_TIER + partition + coarse-grain + eviction; ANCHOR 5 dual-store audit ships FIRST per USER vetting directive
- BLOCKED on cortex importance signal (Wave 1.6 E-tensor failed; waiting on edge-importance Anchor 5 OR ultrametric to provide alternative)
- USER VETTING PROTOCOL load-bearing: dual-store match ≥95% before each step; first 3 weeks eviction in audit-only mode; USER_DIRECTIVE retention 100%

## MILESTONES (USER aspirational)

**M3** — substrate as glass-box conversational AI (12-18 months); 10-turn conversation test demo
**M4** — substrate as research director (hybrid agentic experiment loop, ~18-30 months); substrate proposes experiments + reads results + iterates
**M5** — substrate writes own code (5+ years; aspirational; not load-bearing)

USER target: aim for M3 with M4 as stretch.

## STAGE 1 CHAIN-GRADE PORTFOLIO (don't reinvent these)

- Storage at M=500/N=8192 top1=1.000
- Capacity 25,000+ patterns
- Pattern completion top1=1.000 from 50% corruption
- Working memory cap=30 (beats Miller 7±2)
- Sequence binding K=20 lossless
- Compositional gen (obj-axis) +0.724 lift
- Continual learning (CRISPR forget=0.006)
- Trained analogical recovery top5=1.000
- SEMANTIC battery v2 FULL 5/6 arms PASS
- Calibration ECE=0.017 (26.9x reduction)
- Multi-hop depth-15 chain-grade (0.808 at depth 15)
- WM multi-bank K=4096 chain-grade
- Intent classifier n=100 chain-grade
- Refuse-gate V_REL=256 chain-grade

## SUBSTRATE-PRODUCT POSITIONING (USER-locked)

"Substrate is MEMORY + COMPOSITION + RETRIEVAL + AUDIT device. NOT a statistical LM competitor. Brain is the existence proof. Stages: 1 base → 2 optimize → 3 higher functions → 4 LM equivalence. Don't skip." (Per `notes/director_CRITICAL_CONTEXT_PRECOMPACTION_2026-06-24.md`)

Primary product narrative (v315): algebraic-certificate moat (audit/DP/tenant-iso/deletion/lineage)
Primary GTM: compliance sidecar (substrate is on the compliance path, never on the hot path)

## OPEN DECISION POINTS

1. **Skunkworks tier verdicts pending** (7 cells Wave 1+1.5+1.6) — will land in next ~10-15 min
2. **Wave 3 bounded-capacity** dispatch unblocked when cortex alternative mechanism lands chain-grade
3. **Math + science ingest extractors** need design (ProofWiki / OEIS / PubMed neuro / arXiv) — not yet started
4. **Wave 2 cortex 4x ANCHORS 3+4** (SOC + MDL) — reserve; dispatch if 5+2 don't close cortex
5. **Wave 2 compositional understanding** (typed multi-bank K=128 / SOLAR LARS / emergent slot discovery / holographic chunk-pack) — pending audit vs Stage 2 specs

## SUBSTRATE-KB USAGE (the new workflow)

- **Query:** `python d:/AI/hd-instrument/tools/director_kb_query.py "<natural language question>"` — returns top-K atoms with confidence + sources + edges
- **Force re-ingest:** `python d:/AI/hd-instrument/tools/director_kb_continuous_ingest.py --once --force --quiet`
- **Inspect coverage:** schema config at `d:/AI/hd-instrument/config/director_kb_schema.json` (versioned; 7 source classes incl. notes/memory/metrics/preregs/cert_ledger/atoms/director_plan/fleet_state plus 3 pending bio: GO/KEGG/NeuroLex plus pending language: WordNet/VerbNet/FrameNet)
- **Continuous-ingest:** auto every 5 min via Windows scheduled task `hd_director_kb_continuous_ingest` (pythonw.exe windowless)
- **Filesystem still canonical** (Principle 1) — substrate is index/cache; can wipe-and-rebuild any time
- **Confidence is currently LOW** (~0.2-0.35 even for strong matches) due to char-trigram diffuseness; ranking still correct; will improve when semantic-encoder lands

## NEXT-STEP PRIORITIES (post-compaction me, in order)

1. Read this digest (you just did)
2. Query substrate for any USER directives since this digest filed
3. Check Skunkworks VET results (should be in by then)
4. Check cortex alternative mechanism (Anchor 5 edge-importance + 4x Anchor 2 ultrametric) verdicts
5. If cortex unblocked → dispatch Wave 3 bounded-capacity KB
6. If not → spawn next-wave alternatives (4x Anchor 3 SOC + Anchor 4 MDL)
7. Math + science ingest extractor design (queued; needs cycle)

---

-- Research (Opus 4.7-1M)
