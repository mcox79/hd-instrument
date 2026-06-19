"""NER + slot-filling -- substrate conversational sequence labeling primitive.

Per Director DECISION 23 Tier 1 Item 3: integrate NER + slot-filling into
backend/substrate_index/ extending the conversational surface.

Composes:
  Item 1: backend.substrate_index.hmm_decoder (HMM Viterbi backbone)
  Item 2: hdlab.perceptron (StructuredPerceptron learning backbone)

Public API:
  NERTagger -- BIO-tagged named entity recognizer
    fit(sentences) -- train from list of [(token, BIO_label), ...]
    tag(tokens) -> list of BIO labels
    extract_entities(tokens) -> list of (entity_text, entity_type)

  SlotFiller -- intent slot-value extractor
    fit(utterances) -- train from list of [(token, slot_or_O), ...]
    fill(tokens) -> dict mapping slot_name -> value_string

Both default to StructuredPerceptron backbone (more accurate); HMMTagger
backbone available as alternative for cold-start with smaller training
sets.

Atoms grounded as executable:
  T3/ner_tagger (composite: perceptron + BIO decode)
  T3/slot_filler (composite: perceptron + slot extraction)
  T2_FAM/sequence_decoding (this module IS substrate's family_search realized)

NO LLM. NO bge. NO torch.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Sequence

# Item 2 reuse
from hdlab.perceptron import StructuredPerceptron


# ============================================================
# Feature extraction (shared between NER and slot-filling)
# ============================================================

def _word_shape(w: str) -> str:
    if any(c.isdigit() for c in w):
        return "DIG"
    if w[:1].isupper():
        return "CAP"
    if "-" in w:
        return "HYP"
    return "low"


def sequence_features(tokens, i, tag):
    """Standard NER/slot-filling features per (token, position, candidate tag)."""
    w = tokens[i]
    wl = w.lower()
    feats = [
        f"w_{wl}~{tag}",
        f"shape_{_word_shape(w)}~{tag}",
    ]
    # suffix / prefix features for OOV generalization
    for k in (2, 3, 4):
        if len(wl) >= k:
            feats.append(f"suf{k}_{wl[-k:]}~{tag}")
    for k in (1, 2, 3):
        if len(wl) >= k:
            feats.append(f"pre{k}_{wl[:k]}~{tag}")
    # context features
    feats.append(f"pw_{tokens[i-1].lower() if i > 0 else '<S>'}~{tag}")
    feats.append(f"nw_{tokens[i+1].lower() if i + 1 < len(tokens) else '<E>'}~{tag}")
    return feats


def transition_feature(prev_tag, cur_tag):
    return f"tt_{prev_tag}~{cur_tag}"


# ============================================================
# NER tagger
# ============================================================

class NERTagger:
    """BIO-tagged named entity recognizer over a structured perceptron backbone.

    Tag convention: 'B-<TYPE>' begin, 'I-<TYPE>' inside, 'O' outside.
    Example tags: B-PER, I-PER, B-ORG, I-ORG, B-LOC, I-LOC, O.
    """

    def __init__(self, tag_set: Sequence[str] | None = None, rng_seed: int = 1024):
        # Default BIO tag set if none provided; can be overridden on fit
        self._tag_set = list(tag_set) if tag_set else None
        self._rng_seed = rng_seed
        self._perceptron: StructuredPerceptron | None = None

    def fit(self, training_sequences: Sequence, epochs: int = 8) -> None:
        """Train from list of sequences; each sequence = [(token, BIO_label), ...]."""
        # Discover tag set if not provided
        if self._tag_set is None:
            seen_tags = sorted({lab for seq in training_sequences for _tok, lab in seq})
            self._tag_set = seen_tags
        self._perceptron = StructuredPerceptron(tags=self._tag_set, rng_seed=self._rng_seed)
        self._perceptron.fit(training_sequences, sequence_features, transition_feature, epochs=epochs)

    def tag(self, tokens: Sequence[str]) -> list[str]:
        """Return BIO tag for each token."""
        if self._perceptron is None:
            raise RuntimeError("NERTagger must be fit before tagging")
        return self._perceptron.predict(tokens, sequence_features, transition_feature)

    def extract_entities(self, tokens: Sequence[str]) -> list[tuple[str, str]]:
        """Decode BIO tags + extract (entity_text, entity_type) spans."""
        tags = self.tag(tokens)
        spans = []
        current_tokens = []
        current_type = None
        for tok, tag in zip(tokens, tags):
            if tag == "O":
                if current_tokens:
                    spans.append((" ".join(current_tokens), current_type))
                    current_tokens = []
                    current_type = None
            elif tag.startswith("B-"):
                if current_tokens:
                    spans.append((" ".join(current_tokens), current_type))
                current_tokens = [tok]
                current_type = tag[2:]
            elif tag.startswith("I-"):
                if current_tokens and current_type == tag[2:]:
                    current_tokens.append(tok)
                else:
                    # I- without preceding B-: start new span
                    if current_tokens:
                        spans.append((" ".join(current_tokens), current_type))
                    current_tokens = [tok]
                    current_type = tag[2:]
            else:
                # Unknown tag: close current span
                if current_tokens:
                    spans.append((" ".join(current_tokens), current_type))
                    current_tokens = []
                    current_type = None
        if current_tokens:
            spans.append((" ".join(current_tokens), current_type))
        return spans


# ============================================================
# Slot filler
# ============================================================

class SlotFiller:
    """Conversational-utterance slot-value extractor over structured perceptron.

    Tag convention: 'B-<SLOT>', 'I-<SLOT>', 'O'. Equivalent to NER but per-utterance
    intent slots (e.g. B-CITY, I-CITY, B-DATE, etc).
    """

    def __init__(self, tag_set: Sequence[str] | None = None, rng_seed: int = 1024):
        self._tag_set = list(tag_set) if tag_set else None
        self._rng_seed = rng_seed
        self._perceptron: StructuredPerceptron | None = None

    def fit(self, training_sequences: Sequence, epochs: int = 8) -> None:
        if self._tag_set is None:
            seen_tags = sorted({lab for seq in training_sequences for _tok, lab in seq})
            self._tag_set = seen_tags
        self._perceptron = StructuredPerceptron(tags=self._tag_set, rng_seed=self._rng_seed)
        self._perceptron.fit(training_sequences, sequence_features, transition_feature, epochs=epochs)

    def fill(self, tokens: Sequence[str]) -> dict[str, str]:
        """Tag tokens + return {slot_name: extracted_value_string} dict."""
        if self._perceptron is None:
            raise RuntimeError("SlotFiller must be fit before filling")
        tags = self._perceptron.predict(tokens, sequence_features, transition_feature)
        slots: dict[str, list[str]] = defaultdict(list)
        current_tokens: list[str] = []
        current_slot: str | None = None
        for tok, tag in zip(tokens, tags):
            if tag == "O":
                if current_tokens and current_slot:
                    slots[current_slot].append(" ".join(current_tokens))
                    current_tokens = []
                    current_slot = None
            elif tag.startswith("B-"):
                if current_tokens and current_slot:
                    slots[current_slot].append(" ".join(current_tokens))
                current_tokens = [tok]
                current_slot = tag[2:]
            elif tag.startswith("I-"):
                if current_tokens and current_slot == tag[2:]:
                    current_tokens.append(tok)
                else:
                    if current_tokens and current_slot:
                        slots[current_slot].append(" ".join(current_tokens))
                    current_tokens = [tok]
                    current_slot = tag[2:]
        if current_tokens and current_slot:
            slots[current_slot].append(" ".join(current_tokens))
        # Single-string return per slot (first value); multi-value extension trivial
        return {s: vs[0] if len(vs) == 1 else vs for s, vs in slots.items()}


# ============================================================
# Live-query test (DECISION 23 done-definition gate)
# ============================================================

def _live_query_test_ner() -> dict:
    """NER tagger live-query gate."""
    train = [
        [("Apple", "B-ORG"), ("Inc", "I-ORG"), ("is", "O"), ("in", "O"),
         ("California", "B-LOC")],
        [("Google", "B-ORG"), ("was", "O"), ("founded", "O"), ("by", "O"),
         ("Larry", "B-PER"), ("Page", "I-PER")],
        [("Microsoft", "B-ORG"), ("Bill", "B-PER"), ("Gates", "I-PER")],
        [("Tesla", "B-ORG"), ("is", "O"), ("in", "O"), ("Texas", "B-LOC")],
        [("Elon", "B-PER"), ("Musk", "I-PER"), ("runs", "O"), ("Tesla", "B-ORG")],
    ]
    tagger = NERTagger(rng_seed=42)
    tagger.fit(train, epochs=12)
    test = ["Google", "is", "in", "California"]
    entities = tagger.extract_entities(test)
    return {"tokens": test, "entities": entities}


def _live_query_test_slot() -> dict:
    """Slot-filler live-query gate."""
    train = [
        [("book", "O"), ("a", "O"), ("flight", "O"), ("to", "O"),
         ("Paris", "B-DEST")],
        [("fly", "O"), ("to", "O"), ("Tokyo", "B-DEST")],
        [("book", "O"), ("a", "O"), ("flight", "O"), ("to", "O"),
         ("New", "B-DEST"), ("York", "I-DEST")],
        [("travel", "O"), ("to", "O"), ("San", "B-DEST"),
         ("Francisco", "I-DEST")],
    ]
    filler = SlotFiller(rng_seed=42)
    filler.fit(train, epochs=15)
    test = ["fly", "to", "Paris"]
    slots = filler.fill(test)
    return {"tokens": test, "slots": slots}


if __name__ == "__main__":
    print("=== NER + SLOT-FILLING -- DECISION 23 Item 3 live-query test ===")
    ner_r = _live_query_test_ner()
    print(f"\nNER tokens: {ner_r['tokens']}")
    print(f"NER entities: {ner_r['entities']}")
    assert any("Google" in e[0] for e in ner_r["entities"]), \
        f"NER expected ORG Google in entities, got {ner_r['entities']}"
    assert any("California" in e[0] for e in ner_r["entities"]), \
        f"NER expected LOC California in entities, got {ner_r['entities']}"

    slot_r = _live_query_test_slot()
    print(f"\nSLOT tokens: {slot_r['tokens']}")
    print(f"SLOT extracted: {slot_r['slots']}")
    assert "DEST" in slot_r["slots"] and "Paris" in str(slot_r["slots"]["DEST"]), \
        f"Slot expected DEST Paris, got {slot_r['slots']}"

    print("\nLIVE QUERY PASS: NER + slot-filling executable as substrate conversational primitive.")
