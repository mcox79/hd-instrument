# Prereg: ner_gazetteer_substrate_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** Research Request-1 last substrate-only NER path (rule 8: substrate concept partition as own gazetteer).

## Motivation
NER in-corpus feature levers exhausted (decoder/clusters/POS each small, stacked +0.006). Last substrate-only path: Research
hand-authored 8 entity-type lexicon atoms (PERSON/ORG/GPE/MONEY/DATE/TIME/PERCENT/QUANTITY). Gazetteer features generalize to
UNSEEN entity surfaces (curated list), unlike in-corpus clusters/POS. Add per-token gazetteer-hit features (+prev/next) to the
structured-perceptron NER. A/B baseline vs +gazetteer. OntoNotes 18-type.

## Decision tree (Research)
gaz <0.62 -> ACCEPT boundary; promote CoNLL-equivalent 0.648 as PRIMARY. gaz >=0.65 -> keep pushing (more headroom).

## Pre-registered verdict (NO defeat)
- HARD_PASS: F1 >= 0.65.
- MIDDLE_BAND: F1 0.60-0.65 OR lift >= 0.02.
- HARD_FAIL: lift < 0.02 and F1 < 0.60 (saturates; accept boundary).

Smoke (300 train): baseline 0.466 -> +gaz 0.511 (+0.045, gaz-hit-rate 2.4%); full run decisive.
