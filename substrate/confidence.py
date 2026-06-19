"""
substrate.confidence -- PP-107 cleanup confidence threshold for honest abstention.

Port of exp_cleanup_confidence_roc_cpu_v1.py + exp_calibrated_confidence_ece_v1_n1024.py.

CORE IDEA:
After a cleanup operation (top-1 cosine vs codebook), the top-1 score itself is a
reliable indicator of "did the substrate actually know this?". For stored items the
score is high; for novel items it's low. Threshold via AUC = 1.0 (cycle 145; PP-107).

This enables the "I don't know" wow moment: when the substrate's cleanup confidence
is below threshold, the demo renders "I don't have facts about this" instead of
hallucinating.

DEFAULT THRESHOLD: 0.55 (tuned via AUC = 1.0 on synthetic; production threshold
should be re-calibrated per-shard after KB ingest because shard density affects
baseline cosine).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


DEFAULT_THRESHOLD = 0.55


@dataclass
class ConfidenceVerdict:
    confidence: float
    threshold: float
    confident: bool
    band: str           # "high" / "medium" / "low"

    @property
    def message(self) -> str:
        if self.band == "high":
            return f"high confidence ({self.confidence:.2f})"
        if self.band == "medium":
            return f"medium confidence ({self.confidence:.2f}) - some uncertainty"
        return f"low confidence ({self.confidence:.2f}) - substrate does not have reliable facts here"


def classify(confidence: float, threshold: float = DEFAULT_THRESHOLD) -> ConfidenceVerdict:
    """Bucket a confidence score into high/medium/low for UI display.

    Args:
        confidence: top-1 cosine score from a cleanup
        threshold: minimum confidence for "confident" (defaults to PP-107 tuned)

    Returns:
        ConfidenceVerdict with band suitable for UI colorization (green/yellow/red).
    """
    if confidence >= 0.9:
        band = "high"
    elif confidence >= threshold:
        band = "medium"
    else:
        band = "low"
    return ConfidenceVerdict(
        confidence=confidence,
        threshold=threshold,
        confident=confidence >= threshold,
        band=band,
    )


def should_abstain(confidence: float, threshold: float = DEFAULT_THRESHOLD) -> bool:
    """Should the substrate abstain ("I don't know") for this query?"""
    return confidence < threshold


def _self_test():
    high = classify(0.95)
    assert high.band == "high" and high.confident

    med = classify(0.70)
    assert med.band == "medium" and med.confident

    low = classify(0.30)
    assert low.band == "low" and not low.confident

    # Custom threshold
    custom = classify(0.40, threshold=0.30)
    assert custom.confident, "custom threshold lower than confidence"

    assert should_abstain(0.20)
    assert not should_abstain(0.80)

    print("[substrate.confidence] self-test PASS")


if __name__ == "__main__":
    _self_test()
