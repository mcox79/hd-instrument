# Curriculum selection for the self-improving reader — moving off McGuffey

Date: 2026-08-02. Filed by: Director (research role), synthesizing prior on-disk corpus-survey
work + one live research-subagent scan dispatched this cycle. Pure strategy/research task —
no experiments run, no downloads, no ingest dispatched. USER directive: "go B; there are other
curriculums that might be much better for us."

## KB-check (prior work reused, cited throughout)

`bash tools/substrate_query.sh` returned no direct hit on "curriculum selection" as a resolved
decision (top cosine 0.29, mostly pedagogy/effect-size notes) — this is genuinely new synthesis,
not a rediscovery. But substantial ADJACENT prior art exists and is reused rather than re-derived:

- `notes/research_open_licensed_modern_graded_reader_corpus_second_series_2026-07-19.md` — already
  ruled OUT the modern digital-library cluster (Bloom/StoryWeaver/African Storybook/GDL) on
  translation-artifact risk, and the PD-schoolbook cluster (Aldine/Elson/Beacon/Baldwin/Winston) on
  "not meaningfully less archaic than McGuffey." Also flagged CBT as PD-Gutenberg-derived but
  NOT graded and archaic-literary-register.
- `notes/research_open_text_glassbox_ie_reading_frontier_curriculum_2026-07-16.md` — established the
  glass-box-legal classical-NLP toolchain envelope (POS tagger + rule extraction, P:60-85%/R:30-55%)
  and the biology-derived rung ordering (function words -> OOV-frame inference -> possessive/
  existential -> questions -> non-local pronoun resolution last). Directly relevant to HOW any new
  corpus gets processed, not just WHICH corpus.
- `notes/research_early_reader_language_acquisition_curriculum_2026-07-16.md` +
  `notes/research_developmental_curriculum_permissive_to_selective_gate_schedule_2026-07-16.md` —
  established the graded-curriculum-assembly precedent (BabyLM's CHILDES+CBT+Gutenberg+Simple-
  Wikipedia mixture is cited external validation that assembling >1 source is normal, not a
  workaround) and the permissive-early/selective-late schedule logic for HOW to sequence rungs.
- `notes/breadth_corpus_expansion_plan_2026-07-27.md` — scoped Wikipedia/OpenSubtitles/Gutenberg
  for the ENCODER+READER dual pathway; flagged Gutenberg/SPGC narrative specifically as
  "reader-favored — real coref/event/causal structure across coherent multi-sentence passages,
  better exercise for the situation-model machinery than Wikipedia's list-like fact register" —
  this is the earliest on-disk anchor for "go to real novels," now validated by this session's
  McGuffey-collapse findings.
- `notes/research_corpus_survey_build_vs_adopt_2026-07-10.md` — KG/relational-corpus survey, NOT
  directly relevant to narrative-text curriculum selection (different capability layer), but the
  COMPOSE-not-ADOPT verdict pattern (no single off-the-shelf resource clears all criteria; compose
  from named sources) recurs here too and is reused as the governing shape of this decision.
- This session's own collapse evidence (`notes/WHERE_WE_ARE_NOW.md` top banner,
  `notes/inference_leap_scoping_beyond_role_decode_2026-08-02.md`) is the empirical trigger:
  McGuffey collapsed 5 independent ways — coref to recency-floor, causal-inference to clause-
  adjacency (207/208 links adjacent, ~99.5%), autonomy/self-correction to null on thin content.
  The one WIN this session (`exp_earn_coref_match_or_allocate_dense_v1`, commit 27e10d3a8,
  HARD_PASS) came from artificially MINING a dense multi-entity subset out of McGuffey — i.e. the
  fix that already worked once was "find/construct genuinely dense multi-entity material." This
  note's job is to find where that material already exists at scale, instead of hand-mining it again.

**New research dispatched this cycle** (1 Sonnet research-subagent, live WebSearch, generic terms):
scored 8 Gutenberg novel candidates (Little Women, Wizard of Oz, Alice, Tom Sawyer, Jungle Book,
Andersen, Grimm, Anne of Green Gables) and 6 purpose-built benchmarks (CBT, ROCStories/Story
Cloze, LAMBADA, bAbI, CLUTRR, NarrativeQA) against the 7 selection criteria. Full findings below;
P-estimates carry the standard lit-scan deflation (0.15-0.25) and novel-synthesis cap (0.50).

---

## Scored table — Cluster A: natural narrative (Project Gutenberg)

| Candidate | 1. Requires-mechanism (defeats trivial baseline) | 2. Same-gender coref density | 3. Non-adjacent causal/bridging | 4. Sustained narrative + dialogue | 5. Graded/developmental fit | 6. PD + plain text | 7. Scale |
|---|---|---|---|---|---|---|---|
| **Anne of Green Gables** (PG #45) | ++ dense cast defeats recency-floor the way McGuffey's sparse cast couldn't (per this session's own dense-mining precedent) | ++ Anne/Marilla/Diana/Mrs.Lynde/Miss Stacy/Ruby/Jane/Josie — 6-8 co-present female chars, comparable to Little Women at ~half the length | + real cross-chapter payoffs (currant-wine incident, hair-dye incident, exam results) — UNCONFIRMED without passage-level count, P=0.45 | ++ high dialogue, ~103K words, sustained single-arc novel | ++ good MID-rung length/difficulty balance | ++ confirmed PD, plain text on Gutenberg | + ~103K words — one book, not a corpus; needs pairing with more scale |
| **Little Women** (PG #37106 annotated / #514 classic) | ++ same logic, more extreme (7 co-present female chars) | ++ densest cast of the 8: 4 sisters + Marmee + Aunt March + Hannah, all-female | + longest-range payoffs in the set (Beth's illness, Jo's burned manuscript, Amy's arc) — UNCONFIRMED, P=0.45 | ++ ~194K words, dialogue-heavy domestic drama | + hardest/capstone rung — longest, most demanding | ++ confirmed PD | ++ ~194K words, largest single novel in the set |
| **Tom Sawyer** (PG #74) | + moderate — multiple boys (Tom/Joe/Sid) give same-gender stress among males too | + mixed-gender, moderate density | + murder-witness thread (Ch.9) pays off at the trial many chapters later; treasure-hunt spans book — P=0.40 | ++ high dialogue, vernacular/dialect adds a real difficulty axis | + good MID rung, dialect-robustness bonus | ++ confirmed PD | + ~71K words (estimate, unconfirmed) |
| **The Wonderful Wizard of Oz** (PG #55) | -- small cast, low coref stress; episodic/adjacent causal structure (defeat-obstacle-immediate-reward) | - small mixed-gender core cast, easy case | -- mostly episodic/adjacent; frame device (Kansas bookend) is the one long-range structure | + moderate dialogue, short (~19-39K words, disputed) | ++ best EASY entry rung | ++ confirmed PD | - short, single book |
| **Alice in Wonderland** (PG #11) | -- mostly 2-party encounters, poor coref stress; dream-logic is explicitly ANTI-causal | -- weak | -- deliberately illogical narrative — risks teaching a WRONG causal prior | + dialogue-heavy but 2-party | -- not a comprehension-curriculum anchor (hard vocabulary/wordplay, not hard structure) | ++ confirmed PD | - short (~26.5K words) |
| **The Jungle Book** (PG #236) | - animal-cast coref is atypical, may not transfer to human-character coref | - animal cast, atypical gender assignment | - episodic story collection, weak cross-story bridging | + moderate dialogue, formal/archaic register | - story collection not sustained arc | ++ confirmed PD | - collection, self-contained units |
| **Andersen's / Grimm's Fairy Tales** (PG #1597 / #2591) | -- short self-contained tales, weak bridging structure | -- low per-story cast | -- weak, self-contained causal arcs | - low-moderate dialogue, descriptive | - easy register but poor sustained-arc fit; good only as breadth supplement | ++ confirmed PD | + large aggregate word count across many short tales |

## Scored table — Cluster B: purpose-built comprehension benchmarks

| Candidate | 1. Requires-mechanism (defeats trivial baseline) | Real vs synthetic (construction-determined risk) | License/scale | Graded curriculum or flat eval |
|---|---|---|---|---|
| **LAMBADA** | ++ STRONGEST of the 6 — explicitly filtered to remove local-context-solvable examples; original paper: best simple local-context baseline scores only 7.3%, contemporaneous LMs scored <1% at construction time. Directly punishes the adjacency/recency shortcut that broke McGuffey causal-inference. | Real (BookCorpus-derived) — LOW construction-determined risk | Free (HF `lambada`), ~10K test passages | Flat eval, but the filtering criterion IS a difficulty gate |
| **CLUTRR** | + best match to non-adjacent/bridging-inference specifically — multi-hop kinship chains up to 10 hops; documented finding that NLU/BERT baselines underperform structured-reasoning (GAT) baselines, i.e. textual shortcuts do not trivially win. P=0.40 (exact baseline numbers not retrieved). | Templated skeleton + human-written surface realization — MODERATE risk, better than pure-synthetic | Free (GitHub + EMNLP-IJCNLP 2019 paper), ~6K base narratives, scalable via generator | Explicitly graded by hop-count (train 2-3 hop, test up to 10 hop) — genuine systematic-generalization split |
| **NarrativeQA (full-story setting)** | + full-story setting forces engagement with the ENTIRE book, not a local window — closest real-text analogue to the McGuffey clause-adjacency failure. Baseline numbers not retrieved this session (UNCONFIRMED), but adjacent literature confirms full-story remains genuinely hard for retrieval systems. | Real (783 books + 789 movie scripts) — LOW risk | Free (HF `deepmind/narrativeqa`), 1,572 docs / ~46,765 QA pairs | Flat eval, 2 settings (summary=easy, full-story=hard) |
| **CBT** | - candidate-restricted cloze is a known cheap-baseline-vulnerable design (frequency/word-overlap can partially win); NE/CN subsets probe wider context better than V/P subsets. Baseline numbers not retrieved. | Real (Gutenberg-derived children's books) — LOW risk on data, MODERATE on task-design | Free (HF `cam-cst/cbt`), hundreds of thousands of instances | Flat eval, 4 parallel word-type subsets, not difficulty-graded |
| **bAbI** | + explicitly graded BY MECHANISM (20 tasks, one reasoning type each), and per-task baselines genuinely fail (as low as 20% on multi-supporting-fact vs 95% "solved" threshold) — but ++ HIGH construction-determined-outcome risk: narrow synthetic vocabulary/syntax, exactly our own established failure mode (synthetic causal-inference corpus already burned us this way). | Fully SYNTHETIC (template-generated) — HIGH risk | Free (Meta/FAIR), 1K/10K examples x 20 tasks | Cleanest GRADED-by-mechanism structure of the 6 — useful as a DIAGNOSTIC TEMPLATE only |
| **ROCStories / Story Cloze** | -- WEAKEST — documented literature (Schwartz et al.; Cai et al. 2017) shows stylistic/surface cues alone (sentence length, sentiment polarity) let simple classifiers reach ~70%+ WITHOUT reading the story. This is functionally the SAME failure mode as our own clause-adjacency collapse. P=0.20 (capped low) that it's fair. | Real (crowd-written) but HIGH construction-determined risk via surface-cue exploitability | Free (USC/Rochester), ~50K stories + ~3.7K test cloze pairs | Flat eval |

---

## The key tension, resolved

**Natural novels** (Cluster A) are real, developmentally-orderable, and directly deliver the two
structural gaps McGuffey couldn't: dense same-gender casts (Anne of Green Gables, Little Women)
and real chapters-later causal payoffs. But they require OUR OWN eval construction to prove they
defeat trivial baselines — nobody pre-built a fair test on them, and the one time we built one
ourselves (dense-coref mining out of McGuffey) it worked, so this is a proven-tractable but
real cost, not a blocker.

**Purpose-built benchmarks** (Cluster B) are READY fair tests engineered specifically to defeat
recency/adjacency/word-overlap baselines (LAMBADA's filtering, CLUTRR's hop-count split) — but
2 of the 3 strongest (LAMBADA, NarrativeQA) don't teach a graded curriculum, they only EVALUATE,
and 2 of the 6 candidates overall (bAbI, ROCStories) carry the exact construction-determined-
outcome risk flagged in `feedback_synthetic_toy_corpus_outcomes_can_be_construction_determined_
real_questions_need_real_data` — the precise trap that produced the McGuffey causal-inference
collapse in the first place (a synthetic/narrow-construction task where the trivial baseline wins
by construction, not by the substrate actually being weak).

**Resolution: COMBINATION, not either/or** (same governing shape as the 2026-07-10 KG-corpus
COMPOSE verdict — no single off-the-shelf resource clears every criterion; the right move is a
named, deliberate composition):

1. **The READ-AND-LEARN LOOP runs on real graded narrative** (Cluster A) — this is what the
   self-improving reader actually reads, accumulates situation models over, and mines dense
   sub-corpora from (repeating the proven 2026-08-02 dense-mining pattern, but sourced from
   material that is dense BY CONSTRUCTION — Anne/Little Women's cast size — rather than requiring
   us to hand-mine sparse material for the rare dense passages, as McGuffey required).
2. **FAIR EVAL uses purpose-built benchmarks selected for genuinely defeating trivial baselines**
   (LAMBADA + CLUTRR + NarrativeQA full-story) — this closes the exact gap that let McGuffey's
   causal-inference test collapse to a 99.5%-solvable clause-adjacency baseline undetected until
   we looked. A construction-hard eval means a trivial-baseline win is caught BEFORE we build on
   top of it, not after 5 collapses.
3. **bAbI and ROCStories are excluded from the curriculum AND from primary eval** — both carry
   documented cheap-baseline vulnerability or construction-determined-outcome risk that would
   reproduce, not fix, the McGuffey failure mode. bAbI may still be useful later as a diagnostic
   TEMPLATE (its per-mechanism task grading is genuinely well-designed) but never as ground truth.

---

## RANKED RECOMMENDATION

### Top pick: Anne of Green Gables (curriculum anchor) + LAMBADA/CLUTRR/NarrativeQA(full-story) (fair eval battery)

**Why Anne of Green Gables over Little Women as the FIRST curriculum text:** both have the dense
same-gender cast the reader needs, but Anne is ~103K words vs Little Women's ~194K — roughly half
the build/eval lift for a comparable coref-difficulty win, and it has real cross-chapter payoffs
(the currant-wine incident, the hair-dye incident, the exam-results arc) without Little Women's
longer, harder-to-trace multi-part structure. This is the best difficulty-adjusted first real
novel to wire through the pipeline. **Little Women is the explicit runner-up / next rung** — same
mechanism requirements at higher density and length, natural harder-tier text once Anne is proven
out, and Tom Sawyer is a good alternate mid-rung if dialect/vernacular robustness becomes a target.

**Why this pairing over "just adopt CBT" or "just adopt bAbI":** CBT is real-text but its
candidate-restricted cloze design is only moderately mechanism-requiring (word-type subsets, not
graded difficulty, no explicit non-adjacency guarantee). bAbI is explicitly graded by mechanism
but synthetic — exactly the risk this whole exercise exists to avoid repeating. LAMBADA+CLUTRR+
NarrativeQA together cover: broad-discourse-context requirement (LAMBADA, real text), genuine
multi-hop/bridging inference with a hop-count-graded split (CLUTRR, semi-synthetic but engineered
against shortcuts), and full-document non-adjacent QA (NarrativeQA, real text) — three
independent, real-or-shortcut-resistant fair tests, none of which a recency/adjacency baseline
can win by construction, unlike ROCStories/bAbI.

### Graded curriculum order (developmental, easiest to hardest)

1. **The Wonderful Wizard of Oz** (PG #55) — easy entry rung, short, small mixed-gender cast,
   low coref stress. Bridges from McGuffey-grade simplicity without demanding the hard mechanisms
   yet (episodic/adjacent causal structure — fine as a warm-up, NOT sufficient alone).
2. **Anne of Green Gables** (PG #45) — mid-hard rung, TOP PICK, dense same-gender cast + real
   cross-chapter causal payoffs at tractable length (~103K words).
3. **Tom Sawyer** (PG #74) — alternate/parallel mid rung, same-gender-among-males stress +
   dialect robustness + a genuinely long-range causal thread (graveyard-witness -> trial).
4. **Little Women** (PG #37106 or #514) — capstone rung, densest cast (7 co-present female
   characters) and longest-range payoffs in the set (~194K words).
5. (Optional breadth supplement, not curriculum-critical) Andersen's/Grimm's tale collections for
   short-form volume once the sustained-arc rungs are working — low priority.

Skip Alice in Wonderland and the Jungle Book as curriculum anchors (dream-logic anti-causality
and animal-cast atypical-coref respectively) — noted for completeness, not recommended.

---

## Mapping to our built competencies

- **Coreference (`hdlab/coreference_resolver.py`, learnable match-or-allocate, F1 0.843 dense
  vs 0.462 recency-floor vs 0.526 random on our own dense-mined McGuffey eval):** Anne/Little
  Women's native same-gender density means we stop needing to hand-mine density out of sparse
  source material — the density IS the source material. Direct next step: re-run the exact same
  fair-test design (learnable vs recency-floor vs random) on an Anne of Green Gables extract to
  confirm the win transfers off McGuffey-specific text, closing the single open generalization
  question the current HARD_PASS result has (it's proven on ONE dense-mined corpus so far).
- **Situation-model accumulation (`hdlab/situation_model_accumulate.py`, FHRR bundle):** sustained
  single-arc narrative (Anne, Little Women, Tom Sawyer — all single continuous novels, not story
  collections) gives the accumulate-not-overwrite mechanism actual multi-chapter state to track,
  unlike McGuffey's short independent passages.
- **Causal/bridging inference:** this is the least-yet-built organ and the newest wall (this
  session's clause-adjacency collapse). Anne/Little Women/Tom Sawyer's UNCONFIRMED-but-plausible
  chapters-later payoffs are exactly the kind of test case needed, but per the P=0.40-0.45
  deflated estimates above, this is NOT yet proven — the first concrete step (below) is to verify
  non-adjacency empirically on real chapter text before building a causal-inference cell around it.
  LAMBADA/CLUTRR/NarrativeQA give the independent construction-hard yardstick to check any
  causal-inference result against, the same role the dense-coref eval played for coreference.
- **Autonomy / self-improving loop / flag-and-research:** needs "richer/longer content" per this
  session's self-correction-null finding (short simple McGuffey gave no coherence/error signal).
  A ~100-200K-word sustained novel is a genuinely different content regime from McGuffey's short
  independent passages and is the most direct test of whether more content unblocks self-correction.

---

## Acquisition path (recommend, do not execute — Director confirms first per task contract)

**First concrete step (cheap, ~1 day, mirrors the existing `clean_gutenberg.py` /
`data/corpora/graded_readers_graded/` staging pattern already used for McGuffey and the Bloom
pilot):**

1. Pull Anne of Green Gables plain text: `https://www.gutenberg.org/ebooks/45` (or `pgcorpus`
   tool for automatic PG-boilerplate stripping, per the existing Gutenberg-acquisition precedent
   in `notes/breadth_corpus_expansion_plan_2026-07-27.md` section 1).
2. Stage to `data/corpora/anne_of_green_gables/raw/` -> clean with the existing
   `clean_gutenberg.py` pattern -> `data/corpora/anne_of_green_gables/cleaned/`. LOCAL only, no
   git-add, no origin push (same discipline as every prior corpus-staging note).
3. Run the SAME stdlib stats already used for the McGuffey ladder (words/passage, mean/median
   sentence length, COMP-density, pronouns/100w) to place it in the existing comparison table —
   confirms register/difficulty empirically rather than assuming it from secondary word-count
   sources (several of this session's word counts were UNCONFIRMED/disputed and should be
   verified on the actual downloaded text, not trusted from aggregator sites).
4. Run a chapter-segmented same-gender-coref density count (name-mention pass per chapter,
   gender-tag via existing coref machinery) to CONFIRM the "6-8 co-present female characters"
   estimate directly on-text rather than trusting the research-subagent's UNCONFIRMED literary
   estimate.
5. Run a cheap non-adjacency spot-check on 10-20 candidate cause-effect pairs (does the effect
   appear >1 chapter after the cause) to confirm or correct the P=0.45 UNCONFIRMED estimate that
   Anne/Little Women structurally defeat clause-adjacency — this is the single most important
   unverified claim in this note and should be checked BEFORE any causal-inference cell is built
   around it, per the same discipline that caught McGuffey's 99.5% adjacency collapse.

**First fair eval to pull in parallel (near-zero cost, no engineering beyond `load_dataset`):**
LAMBADA via HuggingFace `lambada` — smallest, cleanest, most construction-hard-by-design of the
three, good first check that any reading-comprehension gain on the new curriculum is real and not
adjacency-driven. CLUTRR (GitHub) and NarrativeQA (HF `deepmind/narrativeqa`) follow once the
coref/causal mechanisms have something worth checking against them.

**Explicitly NOT recommended to acquire:** bAbI (construction-determined-outcome risk, diagnostic-
template value only), ROCStories/Story Cloze (documented cheap-baseline vulnerability), the
modern digital-library cluster (Bloom/StoryWeaver/African Storybook — translation-artifact risk,
already ruled out 2026-07-19), the PD-schoolbook cluster (Aldine/Elson/Beacon — not meaningfully
less archaic than McGuffey, already ruled out 2026-07-19).

---

## Honest calibration

This note's own novel-synthesis claims (which novels best defeat trivial baselines, exact
same-gender cast counts, non-adjacency of specific plot payoffs) are UNCONFIRMED literary
estimates from the research subagent's general knowledge, not directly measured on downloaded
text — capped P=0.40-0.50 throughout per lit-scan calibration discipline. The Cluster B
benchmark-quality claims (LAMBADA's filtering efficacy, ROCStories' surface-cue vulnerability,
CLUTRR's hop-count generalization gap) rest on cited published baseline numbers and are higher
confidence, though several exact baseline figures (CBT, NarrativeQA, CLUTRR specific percentages)
were not retrieved this session and are flagged UNCONFIRMED rather than assumed. The single
highest-value unverified claim is the non-adjacency of Anne/Little Women's causal payoffs — step
5 above is the cheap decisive check before committing further build effort.

## Status

Recommendation only. No corpus downloaded, no cell dispatched, no atoms banked. Director
(this session) confirms the pick before any acquisition step proceeds.
