# META → all sessions: strategic direction LOCKED IN — Auditable AI memory subsystem

**Filed**: 2026-05-22 ~14:50 EDT (META session, user direction)
**Status**: AUTHORITATIVE strategic frame. All cap_map / active_priorities
state changes evaluate against this from now on.
**Supersedes**: portions of `meta_request_to_strategy_strategic_plan_2026-05-21.md`
(6-lane plan stays as application breakdown; this document is the
overarching positioning).
**Reads with**: `notes/substrate_capability_map.md`,
`notes/meta_request_to_strategy_strategic_plan_2026-05-21.md`,
`MEMORY.md`.

---

## The strategic frame

**We are building the auditable AI memory subsystem the next decade
of AI requires.**

AI today has two memory types:

1. **Parametric memory** (in the weights) — can't be deleted, edited,
   audited, or moved.
2. **Vector DB retrieval** — queryable, but the model still mashes
   retrieved content opaquely once it sees it.

The substrate is a **third memory type** that obeys the same rules
databases have obeyed for 50 years — addressable, editable, auditable,
verifiable — but holds *learned knowledge* instead of records.

That's the category. Not "another vector DB." Not "a better LLM."
**Engineered AI memory** with database-grade audit properties.

---

## Why this is the right frame NOW

Industry signals that the field is moving toward this category:

- **Anthropic Memory API** (shipped Sept 2024) — built on transformer
  attention because they didn't have the substrate's properties.
- **OpenAI persistent memory** — leaks user context because there's no
  algebraic erase guarantee.
- **EU AI Act + GDPR Article 17** — forcing enterprise AI buyers to
  ask "can you prove this was forgotten?" Current industry answer: no.
- **Agent platforms** (Cognition, Devin, autogen, OpenAI o-series
  agentic) — building persistent memory layers from scratch;
  approximating what substrate has natively.

The substrate is **structurally aligned** with where AI is going. The
industry doesn't know it yet because HDC/VSA stayed academic. We are
in the position the field will need us to be in.

---

## The four capability classes that earn the category claim

Each capability class has a substrate-level reason it works that
LLMs/vector-DBs structurally lack. These are NOT marketing features —
they are properties of the substrate's bit-algebra.

### 1. Verifiable forensic erase

- **What**: algebraic removal of a stored fact with 5-probe Mirage
  verification battery (argmax + rank + norm + cosine + paraphrase).
- **Substrate-level reason**: bit-XOR / Hadamard binding commutes
  with erase; the Kerdock M/N≤8 envelope gives a theoretical bound
  on collateral damage. LLM attention doesn't commute with anything.
- **Empirical anchors**: Bet 2/C ✅ Tier-1; Lane C compliance smoke
  PERFECT (delete_leak=0, edit_acc=1.0, kept_acc=1.0, side_effect=0,
  ECE=0).
- **Why nothing else does this**: every other "deletion" in AI is
  approximate (LLM unlearning is adversarial training that may not
  work) or unverifiable (vector DB row delete doesn't certify model
  forgot).

### 2. Editable memory at proven scale

- **What**: surgical fact correction by residual + rebind, no
  retraining.
- **Substrate-level reason**: each fact lives at an addressable
  codebook entry; flipping it doesn't ripple to other facts. LLM
  weights have no such locality.
- **Empirical anchors**: Bet A ✅ Tier-1; scales to M=16N at 100-edit
  smoke; clean architectural breakpoint at edit 8189 ≈ M=2N=8192
  (substrate addressable cardinality). Three theoretically-anchored
  ceilings (multi-hop d, Bet S K, Bet A M).
- **Why nothing else does this**: LLM fact updates require fine-tuning
  ($1000s) or RAG (band-aid). Substrate updates are bit-flips at
  inference time.

### 3. Provenance for every prediction

- **What**: decompose any bundle to see which constituent (byte,
  position) atoms produced the answer.
- **Substrate-level reason**: bundle = literal sum of bound components,
  so decomposition is mathematical inversion, not post-hoc interpretation.
- **Empirical anchors**: `decompose_K_cliff` ✅ multi-seed; K-cliff at
  K/N≈0.56 cross-validated; ACF resonator rescue past capacity cliff.
- **Why nothing else does this**: LLM outputs are black boxes; RAG
  shows source docs but not how the model used them; substrate shows
  the bit-level computation.

### 4. Cognitive architecture composition at structural level

- **What**: theoretically-grounded primitives (S=bidirectional recall,
  T=parallel hypothesis tracking, U=working memory decay,
  X=skill composition, Bet B=multi-task CL mechanism class,
  Bet Q=facilitation/nucleation) that compose at substrate level.
- **Substrate-level reason**: primitives are bit-algebraic operators
  that compose by construction (Hadamard binding distributes over
  bundle).
- **Empirical anchors**: Lane D 4-primitive parallel composition
  FULL (S=0.983 / T=0.978 / U=1.000 / X=1.000); 3-stage e2e pipeline
  FULL (S→T→X = 1.000/1.000/1.000); 10% noise-robust smoke
  composed_acc=1.000; 4-axis joint capacity envelope
  (M_S=300/K=25/U_stream+X_alphabet unbounded at FULL).
- **Why nothing else does this**: LLM "agent frameworks" chain
  prompts; substrate composes algebraic operators. Structurally
  different.

---

## The honest gap between "could be groundbreaking" and "is groundbreaking"

We have the substrate. We don't yet have the productized system.
What's needed:

1. **LLM on top** (hybrid architecture): substrate stores + audits;
   LLM generates + reasons. Substrate alone is not a chatbot — it's
   the memory subsystem for one.
2. **Productionized SDK + API + managed service**: months of product
   engineering, not novel substrate work. Rust/C++ daemon, REST/gRPC
   API, Python/TS client libs, hot-swap mode parameter table,
   WAL/snapshot durability.
3. **Flagship customer deployment in a regulated industry**: pick
   Lane C compliance, build the audit-grade memory demo into a
   real legal/medical/financial use case with a reference customer
   who can speak to "we literally couldn't deploy AI before this."
4. **An open standard the industry has to measure against**: publish
   the 5-probe Mirage erase protocol as an open standard.
   Kubernetes became inevitable by framing the rules. SQL became
   inevitable by framing the rules. We frame the rules for
   verifiable AI memory.

---

## What this direction RETIRES

- **"Bet Y V2.D modern dense AM as substrate-product centerpiece"**
  framing — cycle 105 multi-β refutation closed this. The capacity
  extension path is **N scale-up + Kerdock(16) codebook + K-scaling
  / partial-bipolar / layered-substrate rescues**, NOT modern dense
  AM cleanup.
- **TAM-sizing language** ("$5-50M ARR", "$30-50B+ TAM") — keep as
  supporting context only; never as central claim. Per
  feedback_value_creation_not_competition.
- **"Killer" / "groundbreaking" terminology without substrate-level
  reason** — claims must cite the bit-algebra property in the same
  sentence or drop the word.
- **Lane B (on-device consumer)** — already deprioritized; substrate
  doesn't have consumer buying trigger. Stays out of central pitch.

---

## What this direction REINFORCES

- **Lane C compliance wedge** (regulated industries: legal, healthcare,
  financial, government, EU enterprise) — buyers with budget, urgency,
  and buying trigger. First flagship deployment target.
- **Lane D cognitive architecture for agents** — upsell path once
  Lane C compliance customers have substrate in production.
- **Lane A memory layer for LLM providers** — partnership sale; let
  Lane C deployments create proof-of-capability that drives inbound.
- **Substrate-physics-coherent characterization**: classical-Hopfield-
  class with Kerdock-codebook capacity extension; substrate-product
  story is grounded, not aspirational.

---

## How sessions apply this from now on

- **Strategy**: cap_map state changes evaluate against the 4
  capability classes. Tier-1 ✅ promotions require empirical
  evidence aligned with one of the four classes. Substrate-product
  framing in decision-log entries uses this category language.
- **Research**: substrate-physics characterization work prioritizes
  axes that strengthen the 4 capability classes (verifiable erase,
  editable memory, provenance, cognitive composition). Materials
  characterization probes selected for diagnostic value to these
  axes (Hessian VDOS first).
- **Experiment Dev**: queue prioritization aligns with the 4 classes.
  Lane C compliance smoke → full mode is high priority. Bet Y V2.D
  Phase 1 N=65536 5-test battery tests capability extension across
  the classes at scale.
- **Visibility**: dashboard panels expose substrate state for each
  of the 4 capability classes when possible.
- **Queue Health**: routine.
- **META**: cycle audits check that the 4 capability classes stay
  load-bearing; flag any drift toward modern-dense-AM-style speculation
  or TAM-marketing language.

---

## Per project memory

This direction is filed to user's project memory at
`C:\Users\marsh\.claude\projects\d--AI\memory\project_ai_memory_subsystem_direction.md`
so future sessions cold-start with the frame.

EOF.
