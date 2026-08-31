"""Re-export shim -> hdlab.patient_tendency (promoted 2026-08-31)."""
from hdlab.patient_tendency import *  # noqa: F401,F403
from hdlab.patient_tendency import (  # noqa: F401
    type_with_full_tendency, patient_tendency_signal, AMBIGUOUS_VERBS, lemmatize_verb,
    derive_ambiguous_verbs, affector_magnitude_sign, patient_affordance_sign,
    directional_sign, affector_letting_sign,
    WEAK_FORCE, STRONG_FORCE, AFFORDS, RESIST_PROPS, PATIENT_PROPS,
    PROPERTY_ADJ_RESIST, PROPERTY_ADJ_AFFORD, DEFAULT_WEIGHTS,
    RESTRAINT_REMOVER_INSTRUMENTS, RELEASE_CONTEXT_CUES, ONSET_CAUSE_INSTRUMENTS,
)
