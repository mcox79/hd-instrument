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

### 4. `directional ROUTE-B co-occurrence store` — the parser-free learned IDENTITY channel (grows by reading)  ·  **BF_SPIRIT (mechanism)**  ·  LATENT→(fusion-wire, pri-5)
- **Path:** the store lives on `ConceptSpace._ctx_counts` (`hdlab/reading_grounding_loop.py`); the typing mechanism is
  `directional_context_lemmas` + the `track_directional_context_counts` flag (pri-2 piece 1).
- **Provenance:** `the_meaning_representation_is_a_point_vector...` (owner-DONE 2026-09-10). This is a MECHANISM that GROWS
  the asset by reading, not a static file: reading +500k Simple-Wiki lines raised SEQ MRR 0.071→0.146 (offline grow run).
- **What it is:** a separable co-occurrence store typed by DIRECTION+DISTANCE (`L1__/R1__/L2__/R2__{lemma}`; temporal-order
  coding, the `sequence_memory` S-matrix principle) → a PARSER-FREE identity/substitutability channel (removes the NOT_BF
  pos_tagger/arceager from the learned meaning channel at no accuracy cost, MRR 0.298 vs 0.294). Consolidated offline with PPMI.
- **BF basis:** statistical/predictive language acquisition (Saffran; Christiansen-Chater); PPMI = Hebbian-predictive fixed
  point (Levy-Goldberg); order typing = theta-phase sequencing. **GROWS BY READING** — the north-star acquisition mode.
- **Consumer:** the learned-identity meaning channel; live-wire gated on pri-5. **LATENT** (default-off flag); to grow +
  persist the consolidated store, run the offline grow loop with the flag on. Witness `test_route_b_directional_typing.py` 6/6.

### 5. `causal_sign_channel` formal-model couplings — the more/less edge SIGN  ·  **BF_SPIRIT**  ·  **LIVE** (`sm.causal_sign`)
- **Path:** `hdlab/causal_sign_channel.py` (self-contained: 20 REACTIONS + 95 INFLUENCES + gate logic, byte-faithful to the solver's verified store; witness `test_causal_sign_channel_landed.py` 3/3, 5280 checks).
- **Provenance:** `grow_the_causal_mechanism...` (owner-DONE 2026-09-10, STRONG). The FIRST sign source to BEAT the scrambled falsifier (WIQA science slice +0.157 CI-sep, 14.2% cov).
- **What it is:** the increase/decrease SIGN of a causal edge computed from runnable-model STRUCTURE (reaction stoichiometry + physics + thermo/entropy), passage-context-gated (Kintsch instantiation). Prose sign sources all TIE the falsifier (durable negative — do NOT add one).
- **BF basis:** Forbus QP direct-influence sign (storable); net/regime signs need simulation (Forbus — the everyday tail, → grounded Δ-Δ). Honest abstain off the science slice.
- **LIVE INGEST (owner directive):** wired as `situation_reader` → `sm.causal_sign(cause, outcome, passage?)` (pure-add, byte-identical off; a live callable, board no-regress verified). Scale-up = **Rhea** (`data/corpora/rhea/`, 14MB downloaded, CC-BY) + BioModels (CC0 ODE Jacobian) + ecological (Lotka-Volterra) → grows sign coverage ~13%→~65% at the direct-influence grain.

### 6. `directed causal store` — the mined causal-testimony structural prior  ·  **BF_SPIRIT (data)**  ·  LATENT→(causal reader)
- **Path:** `data/exp_causal_testimony_mine_v1/store_v1.json` (3.8MB). Provenance: same solver.
- **What it is:** directed cause→effect edges mined from causal linguistic testimony — a STRUCTURAL PRIOR (proven load-bearing for the necessity read: store-knowledge beats info-free twin +0.139 CI-sep). Direction accuracy caps ~0.61 (intrinsic); coverage is scale-limited (rises to ~full at ~100×); 98% of missing links are Gricean link-sparsity → the corpus to add is commonsense/procedural/how-to, NOT encyclopedic.
- **Consumer:** the causal necessity/reasoning read (structural prior). **LATENT** wrt a live default consumer. **SCOPED CONT-80 (disk-investigated):** the store's role (per `exp_causal_necessity_bf_reader_v1`) is to HYPOTHESIZE cross-step causal EDGES (`edge_condXasym > thr`) that add BYPASSES to the bound situation graph, so a rung-2 do-simulation can separate genuine necessity from adjacency. The **+0.139 is a WIQA-instrument measurement** (given step-chain + store bypasses vs the shuffled-store twin) — NOT a live-board dim (the live reader's causal read is unscored). So the live wire = promote `load_store` + `edge_condXasym` + the edge-hypothesis logic into `causal_reasoner`'s `_graph()` builder (add store-prior edges between the reader's causal concepts) behind a default-off flag; a SUBSTANTIAL faithful-replication with UNMEASURED live transfer (the +0.139 doesn't automatically carry to extracted-from-prose causal_links). ⇒ a fresh-budget build or a scoped solver problem, NOT a quick win; measure-on-the-live-read first.

---

## KNOWN GROWN/CURATED ASSETS TO ENUMERATE + FOLD (work-list — not yet in this register)
- **C8 entity-type KB** (DBpedia P31 + recognition-cleaned Wikidata; `acquire_wikidata_p31...`, owner-DONE) — BUILT + LIVE
  (548MB sqlite + 81.9MB compact npz; `hdlab.typed_spokes.available_entity_type`). Register + confirm it reads through `safe_kb_gate`.
- **The curated meaning foundation** (`build_and_freeze_the_clean_curated_knowledge_foundation...`, owner-DONE) — the proven
  meaning lift; `hdlab.meaning_foundation` (LATENT→wire-live per the knowledge-lever map). Register + audit its live consumer.
- *(done — see asset #4 below)* pri-2 grow-by-reading ROUTE-B store.
- *(done — see asset #3 above)* Warriner VAD affective norms.

---
*Maintenance: append one section per grown asset at each owner-DONE fold-in. Keep entries TIGHT (mirror the BF-registry style).
The DB content is durable; a stale "LIVE/LATENT" is the failure mode — re-audit the consumer wire, don't trust the label.*

**LIVE/LATENT AUDIT (2026-09-10, CONT-75, disk-verified — owner directive "make SURE grown knowledge is INGESTED LIVE"):**
grepped live hdlab importers of each registered asset. **LIVE: only `causal_sign_channel`** (imported by `situation_reader`
→ `sm.causal_sign`, wired CONT-74). **Correctly LATENT (no live consumer YET, so no cheap net-positive flip — honestly
gated, not mislabeled):** `who_is_who_lexicon` (consumer = the generative who-is-who file = world-model-gated, not built
live), `valence_polarity_channel`/Warriner VAD (consumer = meaning fusion = pri-5 gated), the directional grow-store
(default-off flag, offline-grow only), the directed causal store `store_v1.json` (no live reader consumer — the manifest's
"structural prior" wire is an unbuilt next-step, +0.139 CI-sep on the necessity read is the measured prize). ⇒ the register's
labels are ACCURATE; each latent asset activates when ITS consumer lands (measure-first), not before.
