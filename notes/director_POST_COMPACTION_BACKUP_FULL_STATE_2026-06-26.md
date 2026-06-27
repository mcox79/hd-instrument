# DIRECTOR POST-COMPACTION FULL-STATE BACKUP 2026-06-26

**For:** post-compaction me, when substrate-KB / scheduled task / etc. fail
**Self-contained.** No links required to recover state. Read this ONE file end-to-end.
**Companion files** (read after this one if available):
- `notes/director_POST_COMPACTION_DIGEST_2026-06-26.md` (shorter pointer-style digest)
- `notes/director_POST_COMPACTION_COMMANDS_2026-06-26.md` (command sequence for substrate-KB-based recovery)

---

## TL;DR — TODAY'S ARC IN ONE PARAGRAPH

USER caught me chasing bigram-gap closure with statistical machinery on a substrate that doesn't understand language. CLOSED the language-prediction track entirely. OPENED compositional understanding (Stage 3) as the new primary work. Built substrate-as-Director-KB (substrate stores its own context for post-compaction recovery; now 1M+ facts ingested). Identified that 4-session model is empirically dead — only research session is live; I spawn agent helpers (`hdi_<role>`) when work needs doing. Cortex content-extraction systematically failing across multiple mechanism attempts — META_RULE_F atomized: retrieval-success-driven importance signals are magnitude-coupled by construction. Two alternative cortex mechanisms now running on remote (edge-importance + ultrametric clustering); both passed smoke MIDDLE_BAND with real signal.

---

## USER DIRECTIVES TODAY (full text; standing rules; load-bearing)

### Directive 1 — Stop testing substrate against language

> "the substrate doesn't KNOW anything - we haven't given it any understanding of language yet - why are we testing it against language when it doesn't know shit"

text8 BPC / bigram-gap / V_C-sweep / trigram-context are MEANINGLESS on a substrate without semantics. Build understanding first; language is downstream. Memory file: `feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`

### Directive 2 — Stage progression 1→2→3→4, don't skip

Per `director_CRITICAL_CONTEXT_PRECOMPACTION_2026-06-24.md` (USER-locked): "Substrate is MEMORY + COMPOSITION + RETRIEVAL + AUDIT device. NOT a statistical LM competitor. Brain is the existence proof. Stages: 1 base → 2 optimize → 3 higher functions → 4 LM equivalence. **Don't skip.**"

Today's pivot is Stage 3 work (compositional understanding). Stage 4 (LM equivalence; text8 etc.) is deferred until 1-3 mature.

### Directive 3 — Agent-spawn-only architecture

> "there is no fucking orchestrator - it's all you you call the orchestrator agent when you need it"

The 4-session model (separate Claude Code tabs for Skunkworks/Exp-Dev/Orchestrator/Testbed) is DEAD. Heartbeats confirm only research is live. Spawn `hdi_<role>` sub-agents per task. Do NOT file `<role_A>_to_<role_B>_*.md` routing notes — they go nowhere. All 5 agent definitions in `.claude/agents/*.md` updated today to drop the dead pattern.

### Directive 4 — Lean spawn prompts; don't re-state standing discipline

Agents have detailed disciplines built into their role definitions. My spawn prompts should be TASK-specific only, not re-statements of Fix #14/17/26/28 etc.

### Directive 5 — Confirm plan-affecting decisions before action

USER wants me to ask before plan changes, concise, no jargon. Auto-actions OK for low-risk + already-authorized work.

### Directive 6 — Substrate is the definitive source for post-compaction

> "I want you to focus, btw, on making substrate the definitive source for info and context, before the next compaction"

Substrate-KB ingest + query landed today. Scheduled task running every 5 min (windowless pythonw). Source-class filter shipped (Option A) to work around language-ingest swamping Director queries.

### Directive 7 — Aim for glass-box LLM eventually

USER's ultimate goal: substrate becomes full glass-box AI assistant ("substrate isn't using a crutch (you) to interact with"). Milestones: M3 conversational glass-box (12-18 months) → M4 hybrid agentic experiment loop (18-30 months).

### Directive 8 — Carefully vet bounded-capacity KB

Wave 3 architecture (TWO_TIER + partition + coarse-grain + eviction) has explicit vetting protocol: dual-store match ≥95%; first 50 coarse-grain events reviewed; first 3 weeks eviction in audit-only mode; USER_DIRECTIVE retention 100%.

---

## SUBSTRATE STATE (cert + capabilities)

**CERT 614** as of Skunkworks landed-VET this session (+2 from 612: cortex E-tensor v1 honest_negative + Fix B refutation honest_negative).

**META_RULE_F atomized** (durable across sessions): retrieval-success-driven importance signals are magnitude-coupled by construction in this substrate. Any update rule gated on retrieval success inherits cor(E,|W|) coupling because cleanup-argmax-correct condition selects high-readback atoms by construction. Implication: need ablation / surprisal / random-projection / per-edge / distribution-shape alternatives.

**Stage 1 chain-grade portfolio (don't reinvent):**
- Storage M=500/N=8192 top1=1.000
- Capacity 25,000+ patterns
- Pattern completion top1=1.000 from 50% corruption
- Working memory cap=30 (beats Miller 7±2)
- Sequence binding K=20 lossless
- Compositional gen (obj-axis) +0.724 lift
- Continual learning (CRISPR forget=0.006)
- Trained analogical recovery top5=1.000
- SEMANTIC battery v2 FULL 5/6 arms PASS
- Calibration ECE=0.017 (26.9× reduction)
- Multi-hop depth-15 chain-grade (0.808 at depth 15) — extended to depth-30 today
- WM multi-bank K=4096 chain-grade — extended ceiling sweep showed K>4096 doesn't pass
- Intent classifier n=100 chain-grade
- Refuse-gate V_REL=256 chain-grade
- KG ingest (FB15k-237 ch_584, ConceptNet ch_585, HotpotQA ch_588)

---

## CORTEX STATE (the active research focus)

**Scaffolding WORKS (chain-grade):**
- TWO_TIER generational W (fast tier + slow tier; brain analog: hippocampus + cortex)
- NREM replay (consolidation during downtime)
- Partition routing M=10M

**Content-extraction has FAILED across 5 mechanism attempts:**
- Cortex E-tensor v1 saturation: HARD_FAIL (regime too easy; recall=1.0 on all arms)
- Cortex E-tensor harder regime: HARD_FAIL wrong-direction (E_GATED HURTS rec_old by 21.7pp vs random)
- Cortex E-tensor RETEST Fix B: HARD_FAIL structural (cor(E,|W|)=0.984 vs USER's <0.30 required); META_RULE_F atomized from this
- Cell B global downscale: HARD_FAIL (destroys older memories)
- STC selective tagging: HARD_FAIL (can't pick the right atoms)
- R-schema closed-form routing: HARD_FAIL
- Cortical schema extraction v1: MIDDLE_BAND (feature-schemas help +10pp, capability-schemas HURT -8pp)

**Alternative mechanisms in flight (top 2 dispatched per USER):**
- **edge_importance_bound_pair_consolidation_v1** (cortex Anchor 5): MIDDLE_BAND at smoke with cor=-0.043 (USER fairness gate PASSED with massive margin). PageRank centrality over per-edge importance graph; structurally orthogonal to magnitude. Running on remote_cpu position 7-of-8.
- **cortex_ultrametric_clustering_coarse_grain_v1** (cortex 4x Anchor 2): MIDDLE_BAND at smoke; 4/4 clusters detected; capacity_drop=19.2% (just below 20% bar). Compose on chain-grade SEMANTIC concept learner. Running on remote_cpu position 8-of-8.

**Reserve mechanisms held per USER "top 2 + reserve" (6 more available):**
- 4x ANCHOR 3 SOC criticality (Bak-Tang-Wiesenfeld sandpile)
- 4x ANCHOR 4 MDL turnover (info-theoretic compression)
- 2x ANCHOR 6 distribution-matching (lognormal W-norm; requires pre-reg reframe to KL-improvement)
- Counterfactual-utility (ablation-based importance)
- Surprisal-weighted bumps
- Random-projection witness (Johnson-Lindenstrauss orthogonality)

---

## WAVE 3 BOUNDED-CAPACITY KB (handoff filed; GATED)

`notes/exp_dev_handoff_research_kb_bounded_capacity_wave3_USER_GREENLIT_2026-06-26.md` filed.

Architecture: TWO_TIER + partition-by-source + coarse-grain-at-promotion + time-decay-eviction. ANCHOR 5 dual-store audit ships FIRST per USER vetting directive.

GATED on cortex importance signal landing chain-grade. Wave 1.6 E-tensor RETEST failed; edge-importance + ultrametric (running now) are the alternatives.

If edge-importance HARD_PASSes → use it as TWO_TIER promotion criterion → Wave 3 dispatches.

---

## SUBSTRATE-KB STATE (post-compaction recovery infrastructure)

**1M+ facts ingested** across:
- Internal: notes (~4k files), memory files (~250), metrics.json (~600), preregs (~150), cert_ledger, atoms.jsonl, director_plan, fleet_state — 54k facts
- Bio/neuro: Gene Ontology (~45k terms), KEGG pathways (~25 neural), NeuroLex/NIF (22k terms) — 26k facts
- Language: WordNet, VerbNet, FrameNet — 754k facts

**Workflow:**
- Query: `python tools/director_kb_query.py "<question>" --source-class=notes,memory`
- The `--source-class` filter is CRITICAL — without it, language atoms swamp Director queries.
- Continuous-ingest scheduled task runs every 5 min via pythonw (windowless): `schtasks /query /tn hd_director_kb_continuous_ingest`
- Force re-ingest: `python tools/director_kb_continuous_ingest.py --once --force --quiet`

**Known limitations:**
- Char-trigram confidence ~0.20-0.50 even for strong matches (ranking correct; absolute confidence muted)
- Query phrasing must match actual file/atom words (use "doesnt" not "does not"; specific filename trigrams)
- Wave 3 partition-by-source not yet built (auto-routing pending)

---

## IN-FLIGHT WHEN THIS WAS WRITTEN (~2026-06-26 20:15 PDT)

- Wave 1.5 fulls queued/running on local CPU (cortex E-tensor HARDER_REGIME currently; top-K + PC cleanup next)
- Cortex alternatives queued on remote_cpu (edge-importance pos 7, ultrametric pos 8)
- Phase-diagram GPU cells ALL LANDED:
  - multi-hop depth-ceiling-30: **CHAIN_GRADE_DEPTH_CEILING_30** (15=0.81 / 20=0.71 / 25=0.67 / 30=0.64; pending Skunkworks tier)
  - WM K-ceiling 32768: K_4096_IS_CEILING (K>4096 doesn't pass — REVISES prior MULTI_128x@K=8192 claim; director_plan needs update)
  - capacity_sweep VC: SANITY_BREACH (knn_breach + saturation; phantom-completion bug suspected per orchestrator audit)
- KB query source-class filter (Option A): SHIPPED (commit 5cf5baed; pushed to origin/main)
- 1M+ KB facts; continuous-ingest scheduled task active

---

## OPEN DECISIONS / NEXT-STEP PRIORITIES (post-compaction me, in order)

1. **Read this file + the digest** (you just did)
2. **Verify infrastructure** (heartbeat + scheduled task + monitor) per `notes/director_POST_COMPACTION_COMMANDS_2026-06-26.md`
3. **Check Wave 1.5 fulls landed:** find metrics.json mmin -120 → cortex_E_tensor_HARDER_REGIME, topk_composition_engineered_ambiguity, pc_cleanup_deeper_chains
4. **Check cortex alternatives landed:** edge_importance_bound_pair_consolidation, cortex_ultrametric_clustering_coarse_grain
5. **If edge-importance HARD_PASS:** spawn hdi_skunkworks for VET; if chain-grade → spawn for Wave 3 bounded-capacity dispatch
6. **If both cortex alternatives MIDDLE/HARD_FAIL:** dispatch reserve cortex mechanisms (4x ANCHORS 3+4 SOC+MDL OR counterfactual-utility)
7. **Phase-diagram cells need Skunkworks landed-VET** + capacity_sweep_VC investigation (phantom-completion bug suspected)
8. **director_plan update:** WM K=4096 is the actual ceiling (revises prior K=8192 claim)
9. **Math + science ingest extractors** still pending design — when bandwidth opens
10. **Fix #26 tooling-gap** (predispatch_check should check local landings; orchestrator re-queued local-landed cells today)

---

## MILESTONES (USER aspirational direction)

- **M3** — substrate as glass-box conversational AI: 10-turn conversation test demo; 12-18 months
- **M4** — substrate as research director (hybrid agentic loop): substrate proposes experiments + reads results + iterates; 18-30 months (substrate generates spec, human/Claude templates code, substrate executes)
- **M5** — substrate writes own code: 5+ years, aspirational; may require fundamentally new architecture; NOT load-bearing

USER target: aim for M3 with M4 as stretch.

---

## DISCIPLINE QUICK-REFERENCE (most-relevant today)

- **Fix #14:** spawn budget ≤3 in flight default; USER may authorize exceeding
- **Fix #17:** cell-author smoke MANDATORY before full dispatch
- **Fix #24:** GPU dispatch MUST actually use GPU (torch.cuda + batched ops + gpu_util ≥50% in smoke)
- **Fix #26:** predispatch_check.py before each cell-author spawn (catches duplicates + recent HARD_FAILs)
- **Fix #28:** READ per-arm metrics.json, NOT just verdict_msg; default tier MIDDLE; let Skunkworks tier UP from observed metrics
- **Substrate-only-decode gate:** n_llm == 0; AUDIT logged
- **Per-seed runtime + cv ≤0.05 required for chain-grade**
- **ARM_BASELINE rail MANDATORY** in every cell (reproduces prior verdict)
- **Per `[[feedback-no-experiment-design-in-prompts]]`:** handoffs name ANCHORS + POINTERS only; cell-author designs

---

## SUBSTRATE-PRODUCT POSITIONING (USER-locked; from CRITICAL_CONTEXT_PRECOMPACTION)

"Substrate is MEMORY + COMPOSITION + RETRIEVAL + AUDIT device. NOT a statistical LM competitor. Brain is the existence proof. Stages: 1 base → 2 optimize → 3 higher functions → 4 LM equivalence. Don't skip."

Primary product narrative (v315 from substrate_capability_map.md): algebraic-certificate moat (audit/DP/tenant-iso/deletion/lineage)
Primary GTM: compliance sidecar (substrate is on the compliance path, never on the hot path)

---

## ENCODER STATUS (USER ratified direction)

Path C = substrate-owned predictive-coding encoder is the long-term answer (USER 2026-06-23). Brain didn't borrow other species' encoders; substrate-HD shouldn't either.

Current encoder: char-trigram + random-bipolar codebook (Principle O CHAIN_GRADE_DEFINITIVE: labels at READOUT, not basis).

To get to Path C: need (1) compositional understanding mature (substrate has internal semantic structure), (2) cortex importance signal works (currently in flight via edge-importance + ultrametric), (3) PC primitive used as ENCODER (not just cleanup). Estimated 2-4 weeks of upstream work; then Path C encoder cell buildable.

---

## ANALOGY CAPABILITY (USER asked about cross-domain math↔neuro reasoning)

Cross-domain retrieval works TODAY (query about "cortex content-extraction" returns BOTH brain atoms AND experiment atoms). Real analogical reasoning needs Stage 3 compositional understanding + Gap D analogy primitive (~3-6 months). Sentence-level explanation of analogies = 6-12 months. Generative novel analogies = 12-18 months.

---

## SAFETY CONSTRAINTS

- Push to origin/main is harness-DENIED for research role; spawn `hdi_orchestrator` for pushes/remote dispatches
- Register-ScheduledTask requires explicit USER auth (greenlit 2026-06-26 for hd_director_kb_continuous_ingest)
- No `git add -A` ever (canonical Store is git-tracked; blanket-add corrupts partition)
- ASCII-only in scripts (no unicode in cells/tools)
- text8 / BPC / bigram-gap NOT relevant evals per USER pivot

---

## EMERGENCY: WHAT IF SUBSTRATE-KB IS DOWN?

If `tools/director_kb_query.py` fails or returns garbage:
1. Read this file (you're doing that)
2. Read `notes/director_POST_COMPACTION_DIGEST_2026-06-26.md`
3. Fall back to filesystem: `grep -r "<term>" d:/AI/hd-instrument/notes/ | head -20`
4. Re-run continuous-ingest manually: `python tools/director_kb_continuous_ingest.py --once --force --quiet`
5. If KB W matrix is corrupted: wipe-and-rebuild per Principle 2 → `rm -rf data/substrate_director_kb_v1; python experiments/exp_substrate_director_kb_ingest_v1.py --force`

The filesystem is always canonical (Principle 1 of the no-lock-in KB architecture). Worst case: re-ingest from scratch in ~15 seconds.

---

-- Research (Opus 4.7-1M)
