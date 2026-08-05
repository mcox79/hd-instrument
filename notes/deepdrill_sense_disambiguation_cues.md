# Deep-brain drill: lexical sense disambiguation — mechanism + cue ranking (angle 1/3)

**Date:** 2026-08-05
**Status:** VERIFICATION drill — prior trained-knowledge synthesis (24 citations) flagged unverified. This pass ran live WebSearch/WebFetch against arxiv/PMC/ScienceDirect/Frontiers/Wikipedia and marks each claim VERIFIED-THIS-PASS or TRAINED-KNOWLEDGE-ONLY.
**Question:** Does the brain disambiguate a polysemous word's grounding primarily via its syntactic governor / argument structure, or is discourse/situation context necessary too? Design target: BRIDGE-1 (governor+frame-based disambiguation component).

---

## 1. The semantic control network: mechanism

**VERIFIED-THIS-PASS** (multiple independent sources converge):

- **LIFG (BA45/47) + posterior MTG (pMTG) form the controlled-semantic-retrieval/selection network.** Confirmed via Jefferies-lineage semantic-control literature and Rodd/Davis/Johnsrude fMRI work (Rodd et al. 2005: high-ambiguity sentences vs low-ambiguity controls recruit bilateral IFG pars triangularis/opercularis + left pMTG/pITG/fusiform). Source: MRC-CBU (Matt Davis) pub PDF; PMC2566953.
- **Functional split within IFG (Badre & Wagner 2005/2007, PMC6672424, Neuron 2005):**
  - **Anterior VLPFC (~BA47):** *controlled retrieval* — top-down search of the posterior conceptual store when automatic activation is insufficient (weak cue-target association). Shows *meaning-specific* coding.
  - **Mid VLPFC (~BA45):** *post-retrieval selection* — resolves competition between simultaneously active representations, irrespective of whether they arrived by automatic or controlled retrieval. Discriminates semantically-related-vs-unrelated generically (not meaning-specific).
  - This is a genuine double dissociation, not just a gradient — confirms two computationally distinct operations (search vs. compete-and-choose), which matters for how BRIDGE-1 should be decomposed (a retrieval stage feeding a separate selection stage).
- **pMTG role:** acts as an *interface* between semantic representations (posterior temporal store) and the IFG control system — i.e., pMTG is not itself the site of competition resolution, IFG is, but pMTG supplies/holds the competing candidate representations. (PMC4582805, and the MEG time-course paper below.)
- **LIFG responds to *resolution of competition*, not mere presence of ambiguity** — the key finding from Rodd/Davis/Johnsrude: LIFG activity requires that competition actually needs resolving in context, not just that a word has multiple senses. This directly supports a **biased-competition / mutual-inhibition** account: candidate senses are co-activated (in pMTG-adjacent temporal cortex) and IFG (BA45 specifically) implements a winner-take-more selection over them, biased by top-down goal/context signal from BA47's retrieval.
- **Hagoort's MUC model (Memory–Unification–Control)**: LIFG = "Unification" site, binding retrieved lexical items into larger structures under contextual/task constraints; information flows recurrently between LIFG and posterior temporal "Memory" regions (not strictly feedforward). Confirmed via Frontiers 2013 review + PMC11035797 (2024 update) + PMC3709422. This generalizes IFG's role beyond ambiguity per se to compositional binding broadly — consistent with sense-selection being a special case of unification-under-constraint rather than a dedicated separate module.

**Mechanism verdict:** biased competition with two computationally separable stages — (1) BA47 controlled retrieval (pulls in candidates, weighted by cue strength), (2) BA45 selection (mutual-inhibition-like competition resolved by top-down bias) — operating over candidate representations held/interfaced by pMTG. This is VERIFIED, not just trained-knowledge; four independent live sources converge on the same two-stage architecture.

---

## 2. WHICH CUES bias the selection — ranked by evidence

This is the crux for BRIDGE-1. Ranking below reflects strength/directness of the verified evidence, not assumption.

### (a) Syntactic governor / argument structure / selectional restrictions — **VERIFIED as a real, early-acting, and often disambiguating cue, but NOT the sole or always-primary one.**

- **Selectional restriction directly disambiguates lexical homonyms**, confirmed via IJSRP "Word Sense Disambiguation Using Selectional Restriction" and general WSD literature: canonical example — "John married a **star**" — *star* (celebrity vs. celestial body) is resolved because the object of *marry* selects [+human]. This is a governor-driven, argument-structure-based disambiguation, and it is textbook-confirmed as a real, usable, symbolic mechanism.
- **N400 ERP evidence** (multiple studies, verified): violation of selectional restrictions elicits N400 at the target noun; noun/verb homographs disambiguated by verb argument structure are processed "qualitatively similar to unambiguous words" when semantic constraints are available in the local structure — BUT the dominant/subordinate-meaning frequency asymmetry still leaks through as N400 amplitude differences, and a **frontal negativity component reflects active suppression of the context-inappropriate (governor-excluded) meaning**, not its absence from processing. I.e., syntactic-governor cues *strongly bias* selection and can produce near-normal (fast, low-cost) processing, but the dispreferred sense is still transiently activated and must be actively suppressed — the governor doesn't gate access, it biases/wins the competition.
- **Hare, McRae & Elman (2003), "Sense and structure"** (verified via arxiv/PMC secondary citations): verb subcategorization/argument-structure expectations are *sense-specific* — i.e., the verb's argument-structure preferences are themselves conditioned on which sense of the verb is intended, and thematic-fit/argument-structure information co-determines sense selection bidirectionally (verb sense <-> argument-noun fit), not governor-as-unidirectional-filter. This is an important nuance: the governor constrains the argument's sense, AND the argument's identity constrains which sense of the (potentially polysemous) governor/verb is active — it's a joint constraint-satisfaction, not a one-directional rule.
- Conclusion on (a): syntactic governor/argument-structure/selectional-restriction is a **primary, fast-acting, and often sufficient** disambiguation cue when it applies cleanly (categorical mismatch, e.g. [+human] object) — but it is not universally available (many polysemous words have all senses syntactically compatible with the same governor, e.g. "bank" as financial-institution vs. river-edge are both valid objects of "see/visit near") and even when it does apply, the excluded sense is not fully gated but suppressed post-competition.

### (b) Local lexical association / co-occurrence (collocational cue) — **VERIFIED as present and fast but weaker/more indirect than (a) when both are available; frequently the *carrier* of thematic-fit statistics** (McRae/Elman-style distributional thematic-fit models — arxiv:1707.05967, arxiv:1710.00998 — verified to exist and be an active modeling paradigm, though these are computational-modeling papers, not direct neural-mechanism evidence).

### (c) Discourse / situation-model prior context — **VERIFIED as necessary in the general case, and demonstrably able to act *before* or *independent of* local syntax.**

- Eye-tracking / MEG evidence (verified, PMC12466587 "Distinctive Human Dynamics of Semantic Uncertainty" 2024/2025, and the MEG time-course paper PMC5840520): sentence/discourse context reduces disambiguation uncertainty on a graded, continuous timescale; **stronger contextual bias produces faster uncertainty reduction, following a near-linear trend** — this is a continuous, non-categorical effect, distinct from the more categorical governor/selectional-restriction cue.
- Classic "selective access" vs "exhaustive access" debate (verified as a real, still-cited theoretical framework — the interactive/selective-access model, where context can restrict lexical access itself, is empirically supported for strongly-biasing discourse contexts) — meaning discourse context is not merely a late reranking signal but can act at initial access under strong bias.
- Critically: **discourse-level bias and local-governor bias are not redundant** — governor/selectional-restriction operates over the *local clause* only, and cannot resolve cases where a word's referent/grounding depends on prior discourse entities (e.g., anaphoric grounding, situation-model tracking of *which* bank/star/plant was previously introduced) — this is outside what any local syntactic-governor mechanism can supply in principle, not just in practice.

### (d) Frequency/dominance prior (Giora's Graded Salience Hypothesis) — **VERIFIED, and functions as an always-on default that context/governor must overcome, not compete with as a peer cue.**

- Giora's Graded Salience Hypothesis (verified, Wikipedia + multiple RG/Springer sources, later folded into the "Defaultness Hypothesis"): salient (frequent/conventional/familiar) meanings are activated automatically, directly, and **cannot be preemptively blocked by context** — context can only facilitate the subordinate meaning's ascent or suppress the dominant one *after* it activates, not prevent its activation. This is a strong, specific, falsifiable claim confirmed as still-current in the literature.
- This interacts with (a): the N400/frontal-negativity evidence above (dominant-meaning residual activation + active suppression signature) is direct neural confirmation of Giora's behavioral claim — dominance is a default that always fires and must be overridden, regardless of how strong the governor's categorical constraint is.

**Cue ranking synthesis (by evidence strength + earliness + generality):**
1. **Dominance/frequency prior** — always fires first, unconditionally (default read).
2. **Syntactic governor / selectional restriction / argument-structure fit** — fast, often categorically decisive when it applies; the strongest LOCAL override of the default when a hard mismatch exists.
3. **Local lexical/collocational association (thematic fit)** — graded version of (2), fills in when no hard categorical mismatch exists.
4. **Discourse/situation-model context** — slower-building but only source that can resolve cases beyond the local clause (anaphoric/entity-tracking grounding); necessary complement, not a fallback.

---

## 3. Timing / recurrence

**VERIFIED-THIS-PASS** (MEG time-course paper, PMC5840520 — fetched and read directly):

- Both LIFG and pMTG show **context sensitivity within 100-150ms** of stimulus onset — disambiguation-relevant processing starts fast, essentially as fast as lexical access itself, i.e., **not a late, purely post-lexical reranking stage.**
- LIFG shows sustained context-by-ambiguity interaction from ~100ms through 300-400ms+; pMTG shows a more discrete, punctate pattern (~150ms and ~500-600ms) with the *opposite* directionality (stronger for LOW ambiguity, i.e., pMTG is taxed more by easy/unambiguous lookups, consistent with its role as a passive interface/store rather than the active competition-resolution site).
- The authors' own characterization (directly fetched): **"neither pure feedforward nor purely recurrent, but concurrent multi-level constraint satisfaction"** — i.e., governor/local-syntax, dominance-default, and context all inject their bias into the *same* ongoing competition process nearly simultaneously rather than in a strict serial pipeline (context-then-syntax or syntax-then-context).
- This is corroborated by the N400/frontal-negativity data in §2(a): downstream (post-N400, i.e., >400-600ms) frontal-negativity reflecting active suppression of the syntactically-excluded-but-still-activated dominant sense shows that **even when governor constraint is strong and early, competition resolution is not instantaneous or purely feedforward — a real recurrent suppression step follows.**

**Timing verdict:** sense selection is **fast-onset but genuinely iterative/recurrent** — not feedforward-only. A default (dominance) read activates immediately; governor/local-syntax and available discourse bias inject concurrently within ~100-200ms; but full resolution, especially suppression of a strong dominant competitor, extends past 400ms and shows an active-inhibition signature. Giora's graded-salience "residual activation" of the dispreferred sense is neurally real, not just behavioral.

---

## 4. Glass-box computational analog — what BRIDGE-1 minimally needs

Given the above, the biologically-faithful minimal computation is a **3-input biased-competition step**, not a single-cue lookup:

1. **Default read**: retrieve the sense with highest prior/frequency weight unconditionally (Giora default) — this is the "resting" activation state before any context arrives.
2. **Governor/frame bias**: apply the syntactic-governor / selectional-restriction / argument-structure-frame signal as a **strong, fast, near-categorical bias term** — this is legitimately verified as the single most powerful LOCAL override available, and should be implemented as a hard or near-hard veto when there's a categorical (selectional) mismatch, and a graded thematic-fit weight otherwise.
3. **Discourse/context bias**: apply a second, slower-accumulating bias term sourced from situation-model/entity-tracking state (whatever the substrate's coreference/discourse-state organ provides) — this is NOT optional; it is the only source that can resolve cross-clause/anaphoric grounding cases the governor cannot see.
4. **Competition resolution = winner of (1)+(2)+(3) combined, with an explicit suppression step for the loser** (not merely non-selection — the biology implements active inhibition of the loser, which matters if BRIDGE-1 ever needs to represent graded confidence/ambiguity-residue for downstream reasoning, e.g. for garden-path-style reanalysis).

This maps cleanly onto a symbolic/VSA substrate: (1) a stored per-word default sense vector/pointer; (2) a governor-frame lookup (already something a frame/argument-structure organ can supply) that either hard-filters candidate senses by selectional compatibility or contributes a graded thematic-fit score; (3) a context/situation-state bias vector supplied by whatever tracks discourse entities; (4) a competition/argmax (or soft competition retaining a suppressed-but-present residual) over the combined score.

---

## VERDICT for BRIDGE-1

**Is "disambiguate via syntactic governor + frame" brain-faithful?** Yes — it correctly identifies the single strongest, fastest, most decisive LOCAL cue (§2a), and is neurally verified as acting within ~100-200ms alongside the dominance default.

**Is it SUFFICIENT alone?** **No — necessary but insufficient.** Two verified gaps if BRIDGE-1 uses governor+frame ONLY:
- It will systematically fail whenever governor/local-frame constraints don't categorically distinguish the senses (many real polysemy cases — both senses are syntactically legal arguments of the same governor) and the correct sense depends on discourse/entity-tracking state instead. This is not an edge case; the discourse-dependence literature (§2c) shows this is a distinct, necessary information source in the general case, not a rare fallback.
- It will not naturally reproduce the dominance-default + suppression dynamic (§2d, §3) — meaning if BRIDGE-1 is a pure governor-lookup with no default/prior term, it will get "easy" high-dominance-consistent cases right but will mishandle cases where a rare/subordinate sense is governor-favored (it needs to actively overcome, not just select-instead-of, the default).

**Recommended correction:** BRIDGE-1 should be architected as governor/frame = PRIMARY fast local bias (as planned, keep this), PLUS (a) an explicit frequency/dominance default term it must override, and (b) a discourse/situation-state bias input from whatever organ tracks entity/context state, combined via a competition step (not serial gating) with an explicit "suppressed-but-not-erased" residual for the loser. The governor+frame design is not wrong; it is stage-2-of-3, missing the always-on default (stage 1) and the discourse-context peer (stage 3) that the biology runs concurrently with it.

**Confidence:** P=0.65 (deflated per lit-scan calibration; ~4 independent live-verified sources converge on the two-stage-plus-discourse architecture, so this sits above the 0.50 novel-synthesis cap appropriate for pure synthesis, but is capped below high confidence because: (a) the MEG timing paper's exact framing was read via a single WebFetch pass — not independently cross-checked against a second timing study; (b) I could not fetch the bioRxiv homonym paper directly (HTTP 429) to independently verify the BA45/BA47 dissociation beyond the WebSearch snippet — that specific dissociation is corroborated by Badre & Wagner (2005/2007, independently verified) but not double-verified against the biorxiv source I intended to check.

**HARD-FAIL threshold for this drill's claim**: if a controlled experiment shows governor+frame alone (no discourse/default terms) achieves >=90% match to human sense-selection accuracy on a corpus with a meaningful fraction (>=20%) of governor-syntactically-ambiguous polysemous instances, the "necessary but insufficient" verdict above is falsified and governor+frame alone should be treated as sufficient.

---

## Citations — VERIFIED THIS PASS (live-fetched or WebSearch-confirmed with direct source identification)

- Rodd, Davis, Johnsrude — ambiguity fMRI, IFG/pMTG recruitment for high- vs low-ambiguity sentences. (MRC-CBU Matt Davis pub PDF; PMC2566953)
- Badre & Wagner (2005, Neuron; 2007 J Neurosci, PMC6672424) — dissociable controlled-retrieval (BA47) vs. selection (BA45) in VLPFC.
- Hagoort — MUC model (Memory-Unification-Control), LIFG = Unification site. (Frontiers 2013 review PMC3709422; 2024 update PMC11035797)
- Hare, McRae, Elman (2003) "Sense and structure" — sense-specific verb subcategorization / thematic fit (verified via secondary citation chain, arxiv/PMC).
- Giora — Graded Salience Hypothesis / Defaultness Hypothesis (Wikipedia entry verified current; RG/Springer sources).
- MEG time-course of context-dependent lexical ambiguity resolution, LIFG vs pMTG (PMC5840520) — DIRECTLY FETCHED AND READ this pass.
- N400/frontal-negativity suppression evidence for homograph disambiguation via selectional constraints (PMC4564366 and related ERP literature, WebSearch-confirmed).
- "Distinctive Human Dynamics of Semantic Uncertainty" (PMC12466587) — eye-tracking graded contextual-bias uncertainty reduction, WebSearch-confirmed.
- Selectional-restriction WSD literature ("star"/"marry" example) — WebSearch-confirmed via IJSRP paper and general WSD survey hits.

## TRAINED-KNOWLEDGE-ONLY (not independently re-verified this pass, carried from prior synthesis, treat as lower-confidence)

- Exact numeric details of Badre & Wagner's four experimental manipulations (judgment specificity, cue-target strength, competitor dominance, number of competitors) — the existence of these four manipulations was confirmed via WebSearch snippet, but I did not fetch the full paper to verify parameter-level detail.
- Precise garden-path/reanalysis literature for word-SENSE specifically (as opposed to syntactic garden-pathing) — not directly searched this pass; the "necessary recurrent suppression" claim in §3 is supported by the N400/frontal-negativity evidence instead, which is a reasonable but not identical substitute.
- The bioRxiv "Barking up the right tree" homonym MVPA paper's specific decoding results — WebSearch snippet only; direct fetch was rate-limited (HTTP 429) and not retried.
