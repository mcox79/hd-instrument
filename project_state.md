# project_state.md — The Active Context

> Handoff document for the incoming session. Written 2026-09-11; LIVING — updated 2026-09-11 evening (Fable 5.1 session) after the meaning-channel landing. This is a *synthesis*; the always-current
> machine-derived truth lives in `python tools/substrate_health.py`, `notes/STATUS.md`, `git log`, and
> `notes/bf_status_registry.jsonl` — **those OUTRANK this document wherever they disagree.** Read STATUS.md first,
> then this.

---

## 1. THE NORTH STAR

**hd-instrument is a glass-box, brain-foundational reading-comprehension substrate.** The mission (owner, load-bearing): *"You are a neuroscientist recreating a functional brain in software; you just happen to be an expert at coding."* You build the organ the brain uses to perform a computation — you do not build the tractable thing and cite neuroscience afterward.

Two hard invariants gate everything:
1. **Every component must be 100% brain-foundational.** "100%" = the *computation* is the brain's (PINNED to a known neural equation, or a defensible computational-level model where the implementation is genuinely unpinned — e.g. FHRR/VSA binding). Parameters are *swept*, never adopted. A non-brain-foundational component is a **DEFECT that BLOCKS** — you fix it to BF or remove it; you never keep a cheap/convenient stand-in for a metric. (spaCy / GLUCOSE / MAVEN / any off-the-shelf parser/model = NOT brain-foundational.)
2. **No external LLM or tool at inference (THE invariant).** A static, fully-vetted *offline foundation asset* (WordNet, a mined store, frozen vision embeddings computed at ingest) is admissible SUPPLY; an external tool *at read-time* is a defect.

**Where the frontier is now (the strategic pivot):** the substrate has **exhausted what TEXT-DISTRIBUTIONAL + TYPE-LEVEL representations can give.** Meaning read as a context-free *type* lookup is provably capped (Scheible-Schulte theorem — see graveyard). The remaining comprehension capability is gated on two things: **(a) grounding beyond text** (real perceptual/experiential differentia — the pri-5 visual-referent line: DINOv2/THINGS frozen-at-ingest), and **(b) the in-context / token-level GENERATIVE WORLD-MODEL** — reading meaning as an online predictive act, not a lookup. The generative world-model is the **named main event**, not a follow-on.

---

## 2. CURRENT ARCHITECTURE & STACK

**The reader.** `hdlab/situation_reader.py` is the central organ. `SituationReader.read(passage)` produces a *situation model* (`sm`) with many dimensions: coreference, common-noun resolution, who-did-what (agent/patient), state, spatial, causal (sign + necessity), affected-entity, word-sense, etc. Almost every integration touches this file — **it is the serialization bottleneck** (land one situation_reader change at a time).

**Organs.** ~84 organs live in `hdlab/`. Each carries a machine-checked `__bf_status__` tag; the registry is `notes/bf_status_registry.jsonl` (currently **BF≈7, BF_SPIRIT≈70, NOT_BF≈7**), enforced by `verification/test_bf_status_tags.py` + a pre-commit gate. Taxonomy: `BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED`.

**The parse stack (glass-box, no spaCy at inference).** `hdlab/pos_tagger` + `arc_parser` + `arceager_parser` + `arc_labeler` are frozen supervised averaged-perceptrons — the last **NOT_BF** organs, a *declared offline scaffold*. The live default head path is **arc-EAGER** (`parser_arceager=True`). `hdlab/graded_parser` is the BF exact decode (Chu-Liu/Edmonds MAP + single-root Matrix-Tree marginals, brute-verified). **Gotcha:** parser "route-through" wins measured on `arc_parser`/`graded_parser` do NOT touch the live arc-eager head path (they're byte-identical to the live reader).

**Meaning / grounding.** `hdlab/reading_grounding_loop.py` (`canonicalize_fast`, the directional grow-by-reading channel), `hdlab/meaning_foundation` (curated sense hub, live via `sm.select_sense`), `hdlab/valence_polarity_channel.py` (antonymy axis — LATENT), `hdlab/grounded_similarity`. FHRR/VSA: an authenticated **D=2048 situation-vector** (read by UNBIND-QUERY, never cosine — see nuance).

**The board (evaluation).** `experiments/exp_situation_model_qa_modern_v1.py`. `--self-test` = capped smoke (~2 min, **standing no-regress AGG = 0.6313** since the 2026-09-11 WiC re-point); `--run` = full population (~17-40 min, run detached; full-pop aggregate on disk **0.6409**, 2026-09-11). Always `PYTHONHASHSEED=0`. **Grade on MODERN gold only** (UD-EWT / GUM / QA-SRL); 19c corpora (McGuffey/LitBank) are BANNED (10× confound).

**Grown-knowledge assets** (`notes/KNOWLEDGE_ASSET_REGISTER.md`): LIVE = `causal_sign` (formal-model more/less sign; modest — beats its falsifier, ties co-occurrence), the C8 entity-type KB (DBpedia P31, live in `_resolve_commonnouns`), the curated `meaning_foundation` (WiC/sense dims). LATENT (measured-positive, awaiting their consumer) = the antonymy/valence axis + the directional grow-by-reading channel (gated on pri-5), the directed causal store `store_v1.json` (+0.139, no live consumer → pri-10).

**Tooling / process.** Front door = `python tools/substrate_health.py` (derived health: BF counts, integration backlog, gates, top-issues) + `notes/SUBSTRATE_PROCESS_AND_ROADMAP.md`. Other derived views: `tools/substrate_map.py` (organs/stages/briefs, `--gaps`), `tools/problem_ledger.py` (problem states), `tools/board.py` (the owner's board + `self-test`). Recovery entry point = `notes/STATUS.md`.

**The fleet + roles.** Multiple concurrent Claude sessions act as *solvers* on posted problems in `notes/problems/<slug>/` (each has PROBLEM.md; a solved one adds SOLVED.md + OWNER_NOTES.md). **You are the strategy/integration session.** The owner reviews submissions and sets `owner_verdict: DONE`; only then do you integrate. The **orchestrator** is the only role that pushes to origin (you NEVER push). The git index is SHARED across concurrent sessions → **always commit path-limited** (see nuance).

---

## 3. PROGRESS SUMMARY (milestones actually completed)

- **100% BF-certification of the live set** — every organ in situation_reader's import closure tagged + machine-enforced.
- **A large run of owner-DONE integrations**, each reverified first-hand: name-bridge (`safe_kb_gate` + who-is-who lexicon); meaning-representation point-vector (3 latent BF pieces: directional parser-free channel, valence_polarity antonymy axis, intrinsic-gain); the causal mechanism (`causal_sign` wired live + rung-1/2/3 relabel); grounding-subsystem + reward-cluster audits; **pri-3 parser** (located negative: the wall is the scorer); **pri-1 is-a channel** (REFUTED = the capability-wall diagnosis); **who_was_affected** (forward salience prior + Principle-B/parallelism → `affected_entity_resolver`); **pri-4 common-noun coref** (`concept_lemma` + 3 backward-half bridges, 0.5818).
- **This session's wave:** **pri-2 reading-learned arc scorer** INTEGRATED (durable knowledge: read the self-taught scorer as a graded distribution → matches supervised in-domain, beats OOD +0.0235 CI-sep = the register-general 2nd-track reframe; text-only ceiling 0.478 located; fully-BF-acquisition chain 78.9% of gold-POS). **Coref-consolidation** landed (6 coref organs → ONE `hdlab/entity_resolver.py` + `hdlab/lexical_utils.py`, proven byte-identical, witnesses 12/12+2/2+3/3, board 0.6294).
- **Durable knowledge banked** (`notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b, newest-first): the coref two-half machine; the taxonomic-is-a refutation; the parser scorer wall; the FHRR-unbind lesson; the who-was-affected grammar-not-semantics lever.
- **The capability-wall pivot** recorded: text-distributional + type-level exhausted → grounding-beyond-text + the in-context generative world-model.
- **2026-09-11 evening (Fable 5.1 session):** the **meaning-channel pair** integrated — the grounding loop's sense-assignment read is the fused BF read (grounded-distinctive + grown-SEQ + referent, SDT criterion), LIVE, with its own coverage-quality board arm (0.375 vs 0.014); the grown SEQ knowledge is persisted and merged live (the first grown-by-reading asset that both exists AND is consumed); WiC board arm scores the live wire; SCWS graded arm added. Fold-in backlog 0.

---

## 4. THE ACTIVE VECTOR (what we are tackling right now)

**The owner-DONE backlog is CLEAR (2026-09-11 evening).** Landed this session, each reverified first-hand before and after:
- **pri-5 meaning-fusion — LANDED LIVE.** The reading-grounding loop's sense-assignment read is now the FUSED convergent-cue read (`hdlab/reading_grounding_loop.py::FusedSenseRanker`, wired at the grounding gate, default ON): grounded-distinctive ATL (+) reading-grown direction-typed SEQ (+) visual referent (new `sensorimotor_spoke` arm; FOUNDATION asset at ingest), z-field divisive normalisation, earned-gain (log1p) weighting, SDT accept criterion on the info-free null. The fixed 0.45 cosine is gone from the decision; the recall path is byte-identical. The grown SEQ store (1M modern Simple-Wiki lines, `tools/grow_seq_store.py`, ~1 min) ships as `data/foundation/seq_store_v1` (gitignored — regenerate on a new machine) and is merged into every fresh `Substrate`. **Measured on its own new board arm `grounding_coverage_quality` (FULL population n=247): MRR@0.5 0.382 vs grounded-only 0.159 vs incumbent 0.027; twin 0.027; all CI-separated; monotone in reading (0.16 curriculum → 0.32 @250k → 0.38 @1M lines).**
- **context-gated sense — LANDED (measurement).** Board WiC re-pointed at the live wire (`landed == live`); SCWS graded arm added; NO discrete consumer gated (durable DO-NOT). The forward consumer is pri-1.

**Full board run done (2026-09-11): AGG 0.6253 → 0.6409, 5/7 dims CI-sep** (the rise is the WiC instrument change: live wire 0.749 vs the old stand-in 0.664 on the same n=2038; the reader is untouched); SCWS graded arm n=1260 +0.0156 CI-sep.

**Research kept (2026-09-11, owner directive "do the requisite research and keep it"):** `notes/RESEARCH_one_semantic_hub_many_readouts_2026-09-11.md` — the brain has ONE graded semantic hub read by every task, built by error-driven convergence of spokes with task control as input gain; the precision-weighted fusion the substrate uses is a normative analogy (its rule is now labelled OPEN), and the substrate holds ≥6 graded lexical-semantic copies (2 islands). **pri-13** (one learned convergence hub with task readouts, pre-registered HARD-PASS/HARD-FAIL) is posted to settle it. **Honest live-BF state:** 7 BF / 72 BF_SPIRIT / 7 NOT_BF of 86 tagged organs + runtime WordNet-morphy — not yet 100% mathematically BF; every defect has a posted or in-review fix.

**The vector now:** (0) pri-13 semantic-hub consolidation is the structural answer to "islanded copies"; (1) pri-12 `the_lemmatizer_is_wordnet_morphy_at_inference…` is POSTED (the last external-tool rung on the meaning chain); (2) the generative world-model (pri-1) as the graded consumer of the validated settled-vector currency — the main event; (3) owner review of the 3 in-flight SOLVED submissions (pri-7 harm/help, pos_tagger max-margin, type-generalized selectional preference) → integrate on DONE.

## 5. IMMEDIATE NEXT STEPS (prioritized plan for the next session)

**SHORT TERM (next 1–2 weeks, owner-confirmed 2026-09-11):** (a) pre-stage then integrate the three in-review submissions on owner-DONE (pri-7 harm/help → removes NOT_BF `force_dynamics_valence`; pos_tagger max-margin → parser cluster; type-generalized selectional preference); (b) steer + integrate pri-13 (one learned semantic hub, pre-registered test) and pri-12 (glass-box morphology); (c) the remaining consolidation-audit merges (temporal, thematic roles, force, appraisal, salience) as byte-identity-gated refactors; (d) full board `--run` + SCORECARD.md update after every landing; the per-dimension no-regress gate judges each. **LONG TERM (months):** the generative world-model (pri-1) as the graded consumer of the settled meaning vector, resolving coref/causal/affected-entity by prediction; grounding beyond text into the one hub; flip the reading-learned parse scorer once it matches on real prose (pri-11); drive the registry from 7 BF / 72 BF_SPIRIT / 7 NOT_BF toward pinned math everywhere — each landing must move a part from model to pinned or remove a stand-in.

0. **[DONE 2026-09-11] The meaning-channel pair (pri-5 + context-gated sense) is fully integrated and the full board run folded in** (AGG 0.6409 standing; self-test 0.6313 standing no-regress; full-pop grounding_coverage_quality 0.382 vs 0.159/0.027). pri-12 glass-box morphology POSTED; pri-9 narrowed. Fold-in backlog 0; 6 assignable.
1. **[DONE this session] coref-consolidation fully integrated.** Two follow-ons remain filed/open: the BF prize (upgrade `entity_resolver.retrieve()` to graded L&V cue-combination — a separate behavior-changing problem) and clearing `entity_world_model_resolver`'s dormant experiments-import debt.
2. **THE TOP NEXT ITEM — land the meaning-channel pair (pri-5 + context-gated-sense) TOGETHER** — reverify both witness sets first-hand, read both SOLVED wire specs in full, land + measure as one behavior-changing pass (flip the pieces, persist the store, board `--run` to confirm the lift, keep if net-positive / revert + record a located negative if not). This realizes the largest measured-but-unrealized grown-knowledge performance in the substrate.
3. **Then descend the owner-DONE queue one situation_reader landing at a time.** Reverify → read SOLVED in full → land the full chain (owner directive: implement ALL upstream fixes, accept downstream breakage, fix downstream to receive) → §2b + registry + ledger + `INTEGRATED_BY_STRATEGY` marker → commit path-limited, nothing pushed.
4. **Keep the fleet fed.** Assignable OPEN problems right now (7, incl. pri-12 glass-box morphology + pri-13 semantic-hub consolidation): `generative_entity_state_reranks_which_entity_is_the_affected_undergoer` (pri-1 — the world-model main event), `reading_learned_pos_category_induction…` (pri-8), `grounding_coverage_quality_metric…` (pri-9), `wire_the_mined_directed_causal_store_into_the_live_causal_reasoner_and_measure` (pri-10), `wire_the_reading_learned_arc_scorer_as_a_register_general_second_track_and_measure` (pri-11). In-flight awaiting OWNER review (do NOT integrate until owner-DONE): `harm_help_valence…` (pri-7, SOLVED), `pos_tagger_is_a_notbf_maxmargin…` (SOLVED), `type_generalized_selectional_preference` (SOLVED).
5. **Board:** Q128 (a brief-format governance question) is OPEN and awaits the owner; do not block on it. Q129 (land-pri-5) was resolved (owner marked pri-5 DONE).
6. **The strategic through-line** once the wave clears: the generative world-model program (pri-1) is the main event; the pri-5 visual-referent / grounding-beyond-text line supplies the perceptual differentia text can't; the reading-learned scorer 2nd-track (pri-11) is the parser's BF path forward.
