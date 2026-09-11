# project_graveyard.md — The Cautionary Context

> Dead-ends, roadblocks, and risks. Written 2026-09-11 for the incoming session. This project is wide-ranging and
> exploratory; **these are things measured-and-refuted or repeatedly-hit — do NOT re-tread them without a specifically
> stronger, brain-exact version and a reason the prior refutation doesn't apply.** A miss is only a ceiling once a
> fair test of the STRONGER brain-version has also failed.

---

## ⚠️ 0. THE CAVEAT THAT QUALIFIES EVERY NEGATIVE BELOW: partial BF does not compound

**A brain-foundational component can measure as a LOSS purely because its upstream chain is still NOT brain-foundational — not because the component's mechanism is wrong.** This is measured, not hypothetical: making the POS decode BF recovered only **~4%** of its loss, because the top-down signal is only ever as good as the still-NOT_BF *scorer* feeding it. **Partial BF does not compound; strong synergy is GATED on every link being BF.** The same shape recurs: the reasoners beat floors on GOLD but slump to floor on real prose because **extraction (parse/coref/relation) is the shared wall**; the meaning-channel pieces are gated on the fusion-flip landing; the generative who-is-who route is world-model-gated.

**Practical rule for the incoming session:** before filing any negative below as a *durable* ceiling, ask **"was this component's UPCHAIN fully BF when it was tested?"** If the parse spine was still the frozen supervised scaffold, or an upstream channel was still default-off/latent, or extraction was still failing on the prose it was fed, then the negative is likely **"blocked by a non-BF upchain," not "refuted"** — re-test it once the chain above it is fully BF (or on the gold-oracle version of its input) before concluding. The owner has explicitly flagged this. The two theorem-backed negatives (type-level co-occurrence via Scheible-Schulte; coref-separation-is-comprehension on the authenticated FHRR substrate) are the most robust; the parser / meaning / fusion negatives are the most likely to be upchain-gated rather than intrinsic, and should reopen as the chain is completed.

---

## 1. FAILED APPROACHES (durable negatives — refuted with numbers)

**Meaning as a context-free TYPE lookup — REFUTED, do not re-tread any of it.**
- The "learned is-a / taxonomic identity channel" was pitched as the dominant unbuilt meaning lever (+0.488). That number was a **pre-SEQ artifact** (measured vs a weak floor). Against the current strong floor (grounded + grown-SEQ), the is-a channel adds **+0.000**; additive fusion HURTS (−0.054); even the *circular* WordNet taxonomic ceiling isn't CI-separated. **Six** brain-foundational mechanisms (is-a, recurrent-competition/divisive-norm, CSLS, mutual-inclusion, symmetric-coordination, referential-equivalence) ALL null/negative over the strong base.
- **The theorem that explains why (Scheible & Schulte im Walde):** first-order co-occurrence *provably* conflates synonym / antonym / co-hyponym — and all six channels ARE first-order co-occurrence. So **every type-level is-a / similarity / contrast / coordination / equivalence channel is exhausted.** The separator is distinctive perceptual/experiential *differentia* (Binder-2016 features), which raise the oracle but are unroutable + coverage-starved from text. **The validated pivot: meaning is read IN CONTEXT (token-level, N400/predictive), never as a type lookup** (WiC: type-level AUC 0.485 ≈ chance → context-conditioned 0.582 → landed cells 0.66–0.68).

**The parser's real wall is the SCORER acquisition, and text alone caps it.**
- Signal-loss ranked (UD-EWT UAS pts): **SCORER 20.7 ≫ POS-tagger 3.0 ≫ DECODE 0.2.** Routing through the exact graded decode fixes only ~1.9% of head errors; ~99% is scorer error the normalization cannot touch. Errors are *confident* (only 1.3% of tokens uncertain but ~21% of heads wrong) → no reliability-gated / defer / world-model-arbitrate mechanism reaches them.
- A treebank-free reading-learned scorer caps at **UAS ~0.478** (vs supervised ~0.80). **Scale is NOT the lever** (0-EM UAS flat 2k→12k sentences); EM likelihood peaks at round 2 then *accuracy declines*; online/Hebbian re-estimation does NOT beat batch-EM (decay hurts). The residual is the **disambiguation signal text lacks** (PP/clausal attachment — prosody / joint-attention / world-knowledge), the PINNED Klein-Manning ceiling. **Attachment is POS-structural + locality-dominated; adding semantics HURTS it** (lexical features, distributed embeddings, DMV valence, GEK grounding, thematic-fit, supersense coherence, world-model rescoring — all refuted, twin-controlled). The ONE lever that helped is STRUCTURE (Now-or-Never incremental left-corner + coordination parallelism). The self-taught scorer's *realizable* win is reading it as a **graded distribution** (register-general 2nd track), not raising raw UAS.

**Coreference separation is a comprehension act, not a cue problem.**
- Reference is a **two-half machine**: forward generative PRIOR (token-mint + situational address + next-referent prediction) × backward retrieval LIKELIHOOD. The substrate built only the *backward* half and argmaxes it → every backward cue-tweak (substrate participation, prominence, near-identity) was *predicted-null*, not a ceiling.
- The same-head-ambiguous prize is real (oracle: perfect entity separation + recency = +0.36 slice / ~+0.075 board, CI-sep every genre) but is **NOT capturable by any text-extractable per-entity signal**: situational participation (AUC 0.539 = scramble), descriptive identity (55% descriptively identical = irreducible), world-knowledge event-coherence (worse than recency) — ALL null on the authenticated D=2048 FHRR substrate. Separation → the generative world-model.

**Fusion / calibration dead-ends.**
- **Precision-weighted fusion cannot beat equal-weight Bayes** on the meaning channel (a fitted weight also fails — the reweighting lever does not exist; closed across 34k→534k exposure). The loss is *representational depth*, not a missing knob.
- No BF certainty signal recovers the parser/meaning posterior-quality gap (z_top/SDT marginally best +0.006; gain+agreement anti-track). The gap is representational, not metacognitive.
- The meaning-fusion **coverage-COUNT** metric is decision-quality-blind (tracks threshold-clearing, not correctness). Measure coverage **QUALITY** instead.

**Grounding / read-out dead-ends.**
- The live grounding decision-variable was a bag-of-content-words co-occurrence cosine that *loses to plain word-counting* on the loop's own metric — locally optimal for a mis-specified (relatedness) objective over an ungrounded input.
- The DINOv2/THINGS visual referent spoke is REAL but small (+0.018 unique R² on perceptual similarity; MEN +0.044) and **data-coverage-bound** for strict synonymy (~18–21 covered pairs). Real referent data adds what text can't, but it's small and coverage-limited for the synonymy target.

**Smaller banked negatives (built faithfully, lost):** online-EM (drifts); joint POS-parse co-adaptation (co-training fails — both views share the parse-quality error mode at 0.40, the Lateen anti-drift gate correctly rejects it); 2nd-order sibling readout (treebank-free bootstrapping wall); Hindle-Rooth prep-specific PP cue (ambiguity-limited); implicit-causality prior for *argument* pronouns (misapplies — IC is a next-mention prior for a *following* pronoun); type-coherence for pronoun undergoers (φ-agreement already subsumes it); the C6 governor perceptron (trained-at-inference → removed); coarse discourse-derived typing on the name-bridge (over-licenses, −0.025); prose/co-occurrence causal *sign* sources (all TIE the scrambled falsifier — mine no more).

---

## 2. KNOWN ROADBLOCKS (unsolved friction — live traps)

- **BOARD-PROXY caveat.** Some board arms score a SIMPLIFIED STAND-IN (a copy), not the live `read()` path — e.g. an arm may call a structural helper directly, bypassing the live wire. **A flat board delta can mean the wire never ran on the scored path.** Instrument invocations (assert the live function was called) before trusting a flat delta. Recorded in `notes/SUBSTRATE_PROCESS_AND_ROADMAP.md`.
- **Board-invisibility.** Whole capabilities have no smoke-viable gold: causal reasoning (no causal gold in the smoke board), coref-separation. Their wins are real but must be measured on **dedicated instruments** (e.g. the WIQA necessity harness), NOT the smoke board — and a smoke-board arm for them shows a misleading noisy loss (underpowered subset). Do not "disprove" a board-invisible capability with a smoke arm.
- **The live head path is arc-EAGER.** `parser_arceager=True` is the owner-DONE consolidation. Anything measured on `arc_parser`/`graded_parser` (arc-factored) is byte-identical to the live reader — a route-through "win" there does not move the live path. Don't reverse the arc-eager consolidation for a decode micro-win.
- **Integration serializes on `situation_reader.py`.** Nearly every owner-DONE land edits it → land one at a time; never run two agents/passes editing it concurrently. Reverifying a witness that *imports* situation_reader while another pass is mid-edit gives spurious failures.
- **Shared git index.** Concurrent fleet sessions stage files (data/, notes/) in the shared working index. **You MUST commit path-limited** (`git commit -m "msg" -- <path…>`); a bare `git commit` after `git add`, or `git add -A`, sweeps other sessions' files into your commit. (This mistake was made twice early; it is now a hard discipline.)
- **19c corpora BANNED for grading** (McGuffey/LitBank — ~10× confound, "basically a different language"). Grade on modern gold (UD-EWT / GUM / QA-SRL). The well-powered corpus is often the banned 19c one = a power gap to close, not a shortcut to take.
- **Latent grown-knowledge (measured-positive, not yet delivering).** The meaning channel (antonymy/valence axis + directional grow-by-reading identity channel) is measured to lift live grounding (+0.16→+0.26 CI-sep) but is default-off, gated on the pri-5 fusion-flip landing. The directed causal store (`store_v1.json`, +0.139 on the necessity read) has NO live consumer (→ pri-10 problem). "Landed ≠ live" — grep situation_reader for a real consumer before calling anything live.

---

## 3. OPEN CONCERNS & RISKS

- **Integration backlog > safe throughput.** The owner marks solutions DONE faster than one session's context can absorb, and they serialize on situation_reader; the behavior-changing ones (meaning-channel flip) have no byte-identity safety net. **Risk:** a rushed land introduces a subtle live regression that the smoke board (0.6294) doesn't catch. Mitigation: reverify first-hand, land one at a time, prefer fresh context for behavior-changing flips, board `--run` (not just self-test) for meaning-channel changes, and delegate *byte-identical* refactors to fresh-context agents (witness-gated).
- **The frontier is a big open build.** The generative world-model (the main event) is not built; the reasoners are "shown, not end-to-end" — they beat floors on GOLD but slump to floor on real prose because **extraction is the shared wall** (parser/coref/relation-extraction). The world-model must be built at the TOKEN/event level (Bicknell: P(patient|agent,verb) is not type-decomposable — the type-level negatives do NOT preclude a token-level lever).
- **The last NOT_BF defects are the supervised parser perceptrons.** A BF-acquisition replacement exists (pri-2 reading-learned scorer) but flipping it live is gated (it caps below supervised in-domain; the register-general 2nd track is the path — pri-11). Until that lands, the parse spine remains a declared scaffold.
- **Grounding-beyond-text is data-bound.** The visual-referent line is real but small and coverage-limited; closing the synonymy target needs broad perceptual-feature coverage the current assets don't have.
- **Over-fragmentation was a real tendency.** The owner flagged "organs left and right — same structure, different arms." The coref-consolidation (6→1) is the flagship fix; the anti-fragmentation gate (one-structure-one-organ) is now standing. Watch for it: prefer an *arm* of an existing organ over a new organ.
