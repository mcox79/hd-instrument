# KNOWLEDGE-ASSET REGISTER — the grown/curated knowledge DBs the substrate incorporates (owner directive 2026-09-09)

> **Owner directive (2026-09-09):** *"many of the solutions ... have significantly grown knowledge databases that
> resolved many issues in the problem. I'd like us to incorporate that grown knowledge."*
> This register is the ongoing home for those assets. At each owner-DONE integration, any load-bearing grown/curated
> knowledge DB is **persisted to a durable location, labelled BF, registered here, and wired or filed for its consumer**
> — never left latent inside an `experiments/` cell. It mirrors `notes/bf_status_registry.jsonl` for CODE organs;
> this file is for the DATA (the knowledge the organs read). Foundation assets are OK to build (owner 08-16:
> "foundation FREE to build; static offline-built asset OK"); the invariant is **NO external tool/LLM at inference**.

**Columns.** asset · durable path · provenance (which solver grew it) · BF status · what it is · consumer · LIVE/LATENT/FILED.

---

## REGISTERED (durable, on disk)

### 1. `who_is_who_lexicon` — the name-bridge relational who-is-who lexicon  ·  **BF_SPIRIT**  ·  LATENT→(world-model)
- **Path:** `hdlab/who_is_who_lexicon.py` (pure data + accessors; single source of truth — the solver cell imports it).
- **Provenance:** `world_knowledge_common_noun_to_name_bridge_the_81_percent_residual` (owner-DONE 2026-09-10, STRONG).
- **What it is:** three offline curated maps — `POSSESSED_TYPE` (78; possessed-noun→fine possessor type, "X's capital"→country,
  "X's album"→musician), `TITLE_ROLE` (33; honorific→fine role-identity, "President Chao"→president), `TITLES` (37).
  Relational/selectional world-knowledge; the fine graded evidence the online generative who-is-who identity file accrues from.
- **BF basis:** Heim 1982 file-change + Bruce-Young/IAC role-identity nodes + relational selectional semantics. FINE + GRADED
  (the coarse PLACE/PERSON-flag variant is a **measured located negative** — it over-licenses). Curated offline.
- **Consumer:** the online GENERATIVE WHO-IS-WHO identity file (the generative-world-model program's entity layer), fed
  THROUGH `safe_kb_gate`. **LATENT** as a live organ (the generative type-file consumer is world-model-gated / filed with
  `grow_the_causal_mechanism...` pri-1); LIVE as the single source of truth for the name-bridge instrument.
- **Witness:** `verification/test_who_is_who_lexicon.py` 8/8 (byte-identical to the original inline lexicon).

### 2. `safe_kb_gate` — the familiarity gate that makes any broad KB safe to read  ·  **BF** (code organ)  ·  reusable tool
- **Path:** `hdlab/safe_kb_gate.py` (code, in `bf_status_registry.jsonl`; listed here because it is the SAFETY WRAPPER every
  KB asset must pass through).
- **Provenance:** same solver. **Safety theorem proven under noise injection:** an ungated KB is HARMED (0.607→0.399),
  the gated KB is PROTECTED (0.601).
- **BF basis:** Bruce-Young/IAC familiarity gate + Yonelinas dual-process SDT criterion + NLP NIL-detection.
- **Rule (project-wide):** **wrap ANY broad/noisy KB lookup in `safe_kb_types` before its facts fire.** This is what lets
  the world-model acquire a broad entity KB *safely* — the enabler for asset growth.

### 3. `Warriner VAD affective norms` — the signed evaluative axis (antonymy)  ·  **BF_SPIRIT** (curated FOUNDATION)  ·  LATENT→(fusion-wire, pri-5)
- **Path:** `data/frontend_assets/Ratings_Warriner_et_al.csv` (~13,915 words), read via `hdlab/affect_lexicon.py`
  (`valence`/`arousal`); the polarity read is `hdlab/valence_polarity_channel.py` (pri-2 piece 2).
- **Provenance:** Warriner, Kuperman & Brysbaert 2013 (curated offline norm set); wired as the meaning channel's
  polarity axis by `the_meaning_representation_is_a_point_vector...` (owner-DONE 2026-09-10).
- **What it is:** continuous VALENCE (+arousal) norms → the SIGNED evaluative dimension that separates synonyms from
  ANTONYMS (opposite poles), the axis the relatedness channels are BLIND to. `valence_polarity(a,b)=-|val(a)-val(b)|`.
- **BF basis:** Osgood 1957 Evaluation axis; Russell/Barrett core affect; vmPFC valence — PINNED computation over a
  curated norm foundation. Consumed as a COMPLEMENTARY fused channel (corr ~0.11), never pooled into identity.
- **Measured:** fused polarity-aware channel beats the relation-blind distributional floor CI-sep (FUSED 0.878 vs
  0.636), twin loses, WITHOUT WordNet. **LATENT** as a live channel (fusion-wire gated on pri-5); witness
  `verification/test_valence_polarity_channel.py` 2/2.

---

## KNOWN GROWN/CURATED ASSETS TO ENUMERATE + FOLD (work-list — not yet in this register)
- **C8 entity-type KB** (DBpedia P31 + recognition-cleaned Wikidata; `acquire_wikidata_p31...`, owner-DONE) — BUILT + LIVE
  (548MB sqlite + 81.9MB compact npz; `hdlab.typed_spokes.available_entity_type`). Register + confirm it reads through `safe_kb_gate`.
- **The curated meaning foundation** (`build_and_freeze_the_clean_curated_knowledge_foundation...`, owner-DONE) — the proven
  meaning lift; `hdlab.meaning_foundation` (LATENT→wire-live per the knowledge-lever map). Register + audit its live consumer.
- **pri-2 grow-by-reading ROUTE-B store** (`the_meaning_representation_is_a_point_vector...`, owner-DONE, INTEGRATING) — the
  parser-free directional co-occurrence store that grows by reading (SEQ MRR 0.071→0.146 on +500k Simple-Wiki lines). Fold at
  its landing; this register's next entry.
- **Warriner VAD affective norms** (pri-2 affective-valence channel) — on-disk `hdlab.affect_lexicon.valence`; register when the
  antonymy channel lands.

---
*Maintenance: append one section per grown asset at each owner-DONE fold-in. Keep entries TIGHT (mirror the BF-registry style).
The DB content is durable; a stale "LIVE/LATENT" is the failure mode — re-audit the consumer wire, don't trust the label.*
