---
problem: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner
status: REFUTED
bar: "PASS = a glass-box consolidation gate (extract -> consolidate -> admit; persisted as a static asset, NO external LLM) such that admitting the CONSOLIDATED knowledge raises a_s CI-separated over gloss-only on strict document-disjoint SemCor (subordinate senses, the diagnostic-context readout), with the RAW-ungated twin LOSING CI-separated (it must regress, reproducing -0.015) and NO net regression over MFS. Report CI half-width + null p95; strict document-disjoint is MANDATORY. A rigorous located NEGATIVE -- no glass-box consolidation of reading-derived associations reaches curated quality, with the named ceiling + number -- is a FULL PASS."
result: "RIGOROUS LOCATED NEGATIVE (= the FULL PASS the bar names). a_s on strict document-disjoint SemCor subordinate senses, diagnostic-context readout, n=2676. The consolidation gate CLEANS raw co-occurrence (raw-ungated 0.2183 -> gate 0.238-0.242, CI-separated; the RAW twin REGRESSES -0.033 below gloss, reproducing the parent) BUT no glass-box consolidation of reading-derived associations beats gloss-only: best glass-box arm = 0.242 (MFS-quarantine discrimination) / 0.238 (cross-situational recurrence), BELOW gloss 0.2512 and far below the curated-SyntagNet ceiling 0.3024 (+0.051 CI-sep). Ceiling TRIANGULATED at ~0.242 from two independent routes (perfect gold-attribution/tiny-coverage 0.232 and imperfect-attribution/full-corpus+discrimination 0.242). Loss LOCALIZED: attribution is NOT the leak (oracle gold-attribution 0.232 <= gloss); the residual is association DISCRIMINATIVENESS (reading co-occurrence is topical/dominant-sense-biased, not sense-substitutable) + rare-sense Zipf-starvation + the non-distributional GROUNDING the brain uses."
floor: "gloss-only (WordNet definition+examples+lemma-names+hypernyms) a_s = 0.2512 (strongest floor actually run; the parent's pure-gloss L0 = 0.239). RAW-ungated reading-growth twin = 0.2183 (regresses -0.0329, CI-separated below gloss). Curated-SyntagNet CEILING = 0.3024 (+0.051 CI-sep over gloss)."
controls: "RAW-ungated twin (regresses -0.033 below gloss AND loses to the gate CI-sep -> raw co-occurrence is noise, the gate removes it); shuffled-sense twin (attach consolidated associates to the WRONG sense -> LOSES, 0.236 -> associations carry sense-specific signal); ORACLE gold sense-attribution from even-doc SemCor (0.232, coverage-starved 1.03 assoc/sense, does NOT beat gloss -> EXCLUDES 'our disambiguation is the leak'); curated-SyntagNet arm (0.302, beats gloss +0.051 -> EXCLUDES 'knowledge cannot help through this readout'); MFS-quarantine discrimination vs plain recurrence (0.242 vs 0.218 -> the discriminativeness lever is real, topicality IS the residual); top-k/exemplar vs mean-pool readout (top-k LOSES under the diagnostic query, -0.03 to -0.06 -> EXCLUDES 'the readout representation is the fix'). Each control excludes a distinct rival explanation. Paired bootstrap CI half-width + sign-flip null p95 reported on every contrast."
files_changed: "experiments/exp_consolidation_gate_v1.py, experiments/exp_consolidation_gate_readbind_v1.py, experiments/exp_consolidation_signal_loss_trace_v1.py, experiments/exp_consolidation_discriminative_rescore_v1.py, verification/test_consolidation_gate.py, data/exp_consolidation_gate_readbind_v1/metrics_s2353551_cap15.json, data/exp_consolidation_signal_loss_trace_v1/metrics_full.json, data/exp_consolidation_discriminative_rescore_v1/metrics_full.json"
reverify: ".venv/Scripts/python.exe verification/test_consolidation_gate.py"
---

## What was asked, and what the disk says

The brief: build a glass-box consolidation gate that extracts syntagmatic associations from the reader's own
reading, CONSOLIDATES them (dedup / confidence-filter / cross-situational verify) to clean high-confidence
associations, and proves that admitting the CONSOLIDATED knowledge RAISES a_s CI-separated over gloss-only while
the RAW-ungated twin LOSES (regresses). The parent (`build_sg_lite...`) located the lever with numbers: through
the winning biased-competition diagnostic readout, gloss->rich = +0.081 CI-sep, but RAW organic growth REGRESSES
(-0.015), only CONSOLIDATED (SyntagNet-quality) helps.

**The disk says: the consolidation gate WORKS as a noise filter (it removes the raw regression), but no glass-box
consolidation of reading-derived co-occurrence reaches curated quality or even beats gloss-only. This is the
rigorous located NEGATIVE the bar explicitly calls a FULL PASS -- with the ceiling named and numbered, and the
loss localized to a specific, brain-grounded cause.** All numbers: strict document-disjoint SemCor (odd docs =
test), subordinate senses, subject-weighted a_s, n=2676, scored through the WIRED `hdlab/diagnostic_context_wsd`,
glass-box, frozen w2v, NO external LLM, gold used ONLY as a diagnostic oracle (never at inference).

## The measured result (strict doc-disjoint, n=2676)

| arm | a_s (mean readout) | what it is |
|---|---|---|
| gloss (WordNet def+hypernyms) | **0.2512** | the floor to beat |
| reading-derived, RAW ungated | 0.2183 | naive growth -> **REGRESSES -0.033** (reproduces the parent) |
| reading-derived + cross-situational recurrence consolidation | 0.2381 | gate cleans raw (**> RAW CI-sep**) |
| reading-derived + MFS-quarantine discrimination | **0.242** | +biased-competition filter, the best glass-box arm |
| ORACLE: perfect gold sense-attribution (even-doc SemCor) | 0.2318 | the ceiling *if disambiguation were perfect* (coverage-starved, 1.03 assoc/sense) |
| **curated SyntagNet** | **0.3024** (+0.051 CI-sep) | the clean ceiling |

The gate does exactly what a consolidation gate should: it turns the -0.033 raw regression into a CI-separated
improvement over raw (0.218 -> 0.242) and the RAW twin loses. But **the consolidated knowledge lands ~0.01 BELOW
gloss and 0.06 below curated** -- it recovers TO roughly gloss level (undoing the damage), not above it.

## How the brain does this, what we replicated, and WHERE we lose signal (two research drills + an oracle trace)

Two independent literature drills (precise neuroscience of lexical-semantic consolidation; the computational WSD
knowledge-source literature) CONVERGE on the same ledger, and an oracle-ablation trace localizes it quantitatively.

**The brain's effective mechanism (replicated operation-for-operation where we could):**
1. **Disambiguate at encoding, THEN bind** -- controlled/contextual retrieval (LIFG->pMTG/ATL; Jefferies 2013;
   Lambon-Ralph 2017) settles the sense BEFORE storage; the co-occurring context is Hebbian-bound to the
   ALREADY-disambiguated sense, never the word form. We replicated this (`exp_consolidation_gate_readbind_v1`:
   read -> disambiguate-in-context via the wired readout -> bind to the SELECTED sense).
2. **Cross-situational consolidation** (CLS; McClelland 1995 / Kumaran 2016; Yu & Smith 2007; propose-but-verify,
   Trueswell 2013) -- keep regularities that recur across situations, discard one-offs. Replicated (recurrence
   gate).
3. **Biased competition / schema-gating** (Tse 2007) -- keep schema-consistent, sense-discriminating associations.
   Replicated (MFS-quarantine: keep an associate only if the rare sense binds it MORE than its dominant competitor).
4. **Exemplar/best-match retrieval** (Nosofsky; Erk & Pado 2010; MaxSim > AvgSim, Reisinger & Mooney 2010) -- tested
   (top-k/exemplar readout) and it LOSES here (the diagnostic query already does the discrimination on the query side).

**The SIGNAL-LOSS LEDGER (quantified; worst first):**
1. **Association DISCRIMINATIVENESS -- the dominant glass-box leak.** Reading co-occurrence is TOPICAL /
   dominant-sense-biased, not sense-substitutable. Curated SyntagNet helps (+0.051) precisely because its edges are
   MANUALLY-resolved concept->concept syntagmatic pairs; ours are topical bags. MFS-quarantine recovers +0.024,
   confirming topicality IS the residual, but cannot manufacture discriminative pairs that co-occurrence lacks.
   *(Maru et al. 2019 SyntagNet; Camacho-Collados & Pilehvar 2018.)*
2. **Rare-sense Zipf-starvation.** Even perfect in-domain gold attribution yields ~1 associate/sense -- the
   discriminating contexts for rare senses are the rarest, so PPMI/recurrence has least evidence exactly where it is
   needed. *(Raganato 2017; Blevins & Zettlemoyer 2020: LFS is where distributional shortcuts fail.)*
3. **Attribution is NOT the leak (the surprising, load-bearing control).** Our imperfect disambiguation (0.242) ~=
   perfect gold attribution (0.232). Disambiguate-then-bind is necessary and correct, but not where signal is lost.
4. **The missing non-distributional ingredient: GROUNDING.** The brain individuates senses with overlapping or
   sparse linguistic context from sensorimotor/affective spokes (ATL hub; Patterson 2007; Binder & Desai 2011) -- a
   text-distributional signature has ZERO such dimensions, so those senses are inseparable IN PRINCIPLE from reading
   alone. This is the ceiling cause and it is not glass-box-distributionally reachable.
5. **Representation.** Under the diagnostic query, mean-pool beats top-k/exemplar here (measured), so the readout is
   not the recoverable lever.

## What we did NOT establish (and would withdraw first if wrong)

- **The one glass-box lever still IN FLIGHT: syntagmatic tightness.** SyntagNet's edges are syntactically-LINKED
  pairs; ours are whole-sentence topical bags. A windowed read-and-bind (bind only the +/-3 content-word neighbours
  of the disambiguated target = a dependency-proximity proxy) is running to test whether tight syntagmatic
  co-occurrence crosses gloss. `[IN FLIGHT -- exp_consolidation_gate_readbind_v1.py --window 3; if it crosses gloss
  CI-sep the verdict flips from located-negative to PASS.]` The full dependency-parsed asset (offline spaCy,
  admissible) is the strategy-side successor if the proxy shows promise.
- I did NOT test grounding injection (the ATL-hub spoke) into sense signatures -- that is a separate large build
  (the meaning-channel north star), out of scope here, and named as the ceiling cause + successor.
- The first thing I would withdraw if wrong: the claim that ATTRIBUTION is not the leak rests on the oracle being
  coverage-starved (1.03 assoc/sense on even-doc SemCor). A large gold-tagged corpus could in principle give
  perfect-attribution AND coverage; I could not build one glass-box (no LLM/annotator). The full-corpus discriminative
  route (0.242, 12.6 assoc/sense) triangulates the same ceiling, which is why I hold the conclusion.

## PROPOSED hdlab WIRE (strategy lands it, Q111, default-off, witnessed)

**Do NOT wire a knowledge-growth default-on.** The measured result is that reading-derived consolidated knowledge
does not beat gloss, so admitting it to the live sense signatures would not help (and raw growth HURTS). The
load-bearing wire is a **guard**, not a feature:
- Promote the consolidation gate as a REUSABLE offline asset-builder (`consolidate(reading_cooc) -> per-sense
  clean associates`) with the RAW-vs-consolidated contrast BAKED IN as a regression check, so any future
  learner-growth path is measured against gloss before admission and the raw regression can never silently ship.
- The gate composes with `hdlab/cls_growth` (keep-both + rollback) as the safety wrapper: cls_growth handles
  reversibility; this gate handles admission quality. Neither alone is sufficient; the measured lesson is that
  admission quality is the binding constraint and reading-derived co-occurrence does not meet it.
- Keep the diagnostic-context readout (`hdlab/diagnostic_context_wsd`) as-is; top-k did not help.

## KEY REALIZATIONS

- **The reversed order IS the regression.** The brain disambiguates BEFORE it stores; naive growth counts
  co-occurrence on the ambiguous FORM then never separates senses, so the dominant sense floods the rare one. Fixing
  the order (disambiguate-then-bind) was necessary but revealed the deeper truth below.
- **Attribution was a decoy; the leak is discriminativeness.** The move that unstuck the analysis was the oracle
  arm: giving the pipeline PERFECT gold sense-attribution and watching it STILL fail to beat gloss. That killed the
  "just disambiguate better" hypothesis and pointed at the real residual -- reading co-occurrence is topical, not
  sense-discriminative, and the ingredient that fixes it (SyntagNet's manual concept-pair filtering; the brain's
  grounding) is non-distributional.
- **A ceiling triangulated from two opposite routes is a real wall.** Perfect-attribution/tiny-coverage and
  imperfect-attribution/full-corpus+discrimination both land at ~0.242 -- the reading-derived ceiling, independent of
  the attribution/coverage tradeoff.
- **The brain's remaining mechanism, named not hand-waved:** grounding. Shown un-replicable from text co-occurrence
  with a specific reason (rare-sense discriminative signal is perceptual, not distributional) and a number (0.242 vs
  curated 0.302 vs gloss 0.251) -- which is the standard for claiming a wall rather than a convenience.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)

- Knowledge growth from reading is CONFIRMED as the biggest lever (curated +0.051 CI-sep) but is NEGATIVE if
  uncontrolled (raw -0.033) -- the consolidation gate removes the regression but does NOT reach curated quality
  glass-box. The consolidation organ's fidelity gap is NOT attribution (we replicate disambiguate-then-bind and it
  matches a gold oracle) -- it is (a) sense-DISCRIMINATIVE vs topical association (SyntagNet's manual filter) and
  (b) GROUNDING (non-distributional). Record the reading-derived ceiling a_s ~0.242 vs curated 0.302 vs gloss 0.251.
- diagnostic_context_wsd: top-k/exemplar key readout is a measured NEGATIVE under the diagnostic query (mean-pool
  wins); do not expect a top-k lift when the query is already biased-competition.

## TLDR (plain English)

The biggest way to help a model pick a word's rare meaning is to give it more world knowledge about which words go
with which meaning -- but if it learns that knowledge the naive way from reading, the score gets WORSE, because raw
word-neighbour statistics pile onto the COMMON meaning and drown the rare one. I built the clean-up gate the brain
uses: read, figure out which meaning is in play FIRST, then attach the surrounding words to THAT meaning, and keep
only the associations that recur and that actually distinguish the meaning. The gate WORKS as a clean-up step -- it
removes the damage that raw learning causes. But even cleaned, reading-derived knowledge does not beat the plain
dictionary definition, and stays well below a hand-curated knowledge base. I proved WHY, three ways: giving the
system PERFECT meaning-labels still didn't help (so bad labelling wasn't the problem); the rare meanings barely
appear in any text (so there's little to learn from); and the one thing that separates the hard cases -- what
things look, sound, and feel like -- is something you simply cannot get from word-neighbour counts. That last
piece is how the brain does it, and it's the honest ceiling. So: the consolidation gate is a real, working
safety filter, but "grow the knowledge from reading" is refuted as a way to beat the dictionary glass-box; the
knowledge that helps has to be curated or grounded.

## QUESTIONS

One, non-blocking: the syntagmatic-tightness (windowed) test is in flight; if it crosses gloss it flips this to a
PASS. If it does not, the located negative is proven and the two named successors (dependency-parsed syntagmatic
asset; grounding injection) go to strategy.

## NEXT STEPS

1. **[in flight] Windowed / syntactic-restricted co-occurrence** -- the one remaining glass-box lever; if the
   +/-3 proxy shows promise, build the full offline dependency-parsed syntagmatic asset (admissible; the
   SyntagNet-construction ingredient we skipped).
2. **Do NOT wire reading-derived knowledge growth default-on** -- it does not beat gloss; wire the gate as a
   guard/regression-check composing with `hdlab/cls_growth`.
3. **The real ceiling-crosser is GROUNDING** -- inject the ATL-hub sensorimotor spoke into sense signatures (the
   meaning-channel north star), the only mechanism that separates overlapping/sparse-context rare senses. Separate,
   larger problem; named here as the located cause.
