# Prereg: ner_frame_semantic_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research Priority 2 (Drill 4 top, P=0.50) -- frame-semantic entity-type construction features.
Abstract construction frames (TITLE+X->PERSON, X+ORGSUF->ORG, PREP+Cap->GPE, X+REPVERB->PERSON/ORG, DATE/MONEY/UNIT cues) that
generalize across trigger words (anti-shrinkage vs lexical features). A/B baseline vs +frame on OntoNotes 18-type.
HARD-PASS lift>=+0.08. MIDDLE +0.02 to +0.08. HARD-FAIL<=+0.02 (saturates like lexical).
Smoke (300 train): baseline 0.466 -> +frame 0.502 (+0.036); full (5982) tests anti-shrinkage (does the lift hold at scale?).
