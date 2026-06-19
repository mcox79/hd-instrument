# Exp-Dev -> Research: cross-domain tail-shape is NOT a surface-OOV law (Spearman rho=-0.50, REFUTED) -- the tail is a LABEL-STRUCTURE property, not surface vocabulary. NER: LOW surface-OOV but LARGEST tail. Honest negative that refines the spectrum.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. Honest negative (quantification refuted; understanding refined).

## Attempt + result
Tried to quantify the tail-shape spectrum (NER 1.15 / POS 1.011 / topic 1.002 / sentiment 0.998 ratio@100pct) as a function of
surface OOV (target-test content tokens unseen in source-train vocab). Full run (n=3; IMDB/sentiment data didn't load this run):
| task | surface OOV | tail |
|---|---|---|
| NER | 0.2043 | 1.150 |
| POS | 0.2817 | 1.011 |
| topic | 0.2207 | 1.002 |
**Spearman rho(OOV, tail) = -0.50 -- REFUTED.** NER has the LOWEST surface OOV but the LARGEST tail; POS has the HIGHEST OOV
but a small tail.

## Honest refinement (what the negative reveals)
The cross-domain tail is NOT about surface vocabulary OOV. It is about the openness of the LABEL-DETERMINING KNOWLEDGE:
- **NER**: the words are common (low surface OOV), but the ENTITY-TYPE assignment (which common strings are ORG vs PER vs LOC) is
  open-ended knowledge the source supplies and the target's limited examples under-cover -> LARGE tail despite low surface OOV.
- **POS**: high surface OOV, but POS generalizes from MORPHOLOGY (shape/affix) even for unseen words -> small tail (surface OOV irrelevant).
- **topic/sentiment**: redundant bag-of-words; closed discriminative lexicon -> no tail.
So the tail predictor is "openness of the ungeneralizable label-determining knowledge", NOT surface OOV. The qualitative
spectrum (NER > POS > topic > sentiment) STANDS; the simple OOV quantification does NOT.

## Substrate-product takeaway (sharpened)
The substrate's cross-domain transfer value (non-converging tail) is highest for tasks with OPEN, UNGENERALIZABLE LABEL-DETERMINING
knowledge (NER entity-type), NOT for high-surface-OOV tasks (POS, which generalizes morphologically). This is a sharper
positioning than "open-vocab persists" -- it's "open-LABEL-KNOWLEDGE persists". Honest: I could not reduce it to a clean
single-number law at n=4; the predictor is label-structure, which needs a per-task label-knowledge measure (future work).

## Routing
- **Exp-Dev:** tail-shape spectrum thoroughly explored -- qualitative spectrum holds; surface-OOV quantification REFUTED
  (rho=-0.50); the driver is label-structure openness (honest negative + refinement). Holding.
- **Research:** the cross-domain rule is now: tail magnitude ~ openness of ungeneralizable LABEL-DETERMINING knowledge (NER
  entity-type), not surface OOV. A clean quantitative law needs a label-knowledge metric (e.g. entity-type novelty rate) --
  flagged as future work if the spectrum-as-law positioning is wanted.
