"""SubstrateRouterAPI: thin Python interface exposing substrate primitives to the M3 router.

Wraps the chain-grade substrate primitives that today have provable cert-grade evidence:

  1. Intent classifier (a1_substrate_intent_classifier_v1 HARD_PASS chain-grade)
       acc=0.754 cv=0.042 across 3 seeds at N_DIM=2048, N_TRAIN=5000, N_TEST=500;
       p95 latency 0.54ms; n_llm_calls=0. Categories:
       LOOKUP, COMPARISON, MULTI_HOP, LIST, CHAIN, COUNT, DEFINITION.
       Source: data/exp_a1_substrate_intent_classifier_v1/metrics.json (verified on disk).

  2. KG lookup (FB15k-237 ingest+1-hop) wraps hdlab.kg_traversal.KGStore.retrieve_topk.
       Chain-grade at 1-hop r@1=1.000 (data/exp_fb15k237_kg_khop_benchmark_cpu_v1/metrics.json).
       This M1.1 implementation builds an in-memory KGStore on demand for the smoke test;
       full M1.2 will load a persistent FB15k-237 ingested store.

  3. Refuse-gate (V_REL=256 chain-grade per hdlab.refuse_gate).
       Wraps the calibration-derived tau threshold; returns is_refused=True when
       substrate's confidence on the routed query is below tau.

Honest scope:
  - This is M1.1 scaffolding. The real intent classifier W matrix and KG store will
    be loaded from data/ in M1.2+. For M1.1 we instantiate a small in-memory pair
    so the routing-logic discriminator test is exercisable.
  - "Categories" are exposed as IntentClass enum mapping the chain-grade 7-category set
    plus KG_LOOKUP (alias for LOOKUP) and GENERAL (catch-all/route-to-LLM).
  - Confidence is computed as softmax of the cosine scores; same regime caveat as
    iter_cleanup_chain applies (high beta -> Dirac; we use a moderate beta=8 for the
    intent confidence so cross-class margin is informative).

Glass-box property: every call returns its confidence + (optional) trace so the
router can decide whether to trust the substrate output or fall back to LLM.

No silent except: errors raise ValueError with the failing-primitive name; the
router catches and falls back to LLM with a typed reason.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable

import numpy as np

# Repo path setup so hdlab imports resolve when this module is used standalone.
_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.char_trigram_encoder import CharTrigramEncoder


# ---------------- Intent class enum ----------------

class IntentClass(str, Enum):
    """The 7 chain-grade intent classes + KG_LOOKUP alias + GENERAL fall-back.

    Mirrors a1_substrate_intent_classifier_v1 CATEGORIES exactly; KG_LOOKUP is a
    routing alias for LOOKUP queries that have a (entity, relation) parse.
    """

    LOOKUP = "LOOKUP"
    COMPARISON = "COMPARISON"
    MULTI_HOP = "MULTI_HOP"
    LIST = "LIST"
    CHAIN = "CHAIN"
    COUNT = "COUNT"
    DEFINITION = "DEFINITION"
    KG_LOOKUP = "KG_LOOKUP"  # routing alias for LOOKUP with (entity, relation) parse
    GENERAL = "GENERAL"  # fall-back / unknown

    @classmethod
    def from_substrate_label(cls, label: str) -> "IntentClass":
        try:
            return cls(label)
        except ValueError:
            return cls.GENERAL


# Categories whose answers a substrate primitive can produce today (chain-grade).
# Other classes (COMPARISON, LIST, COUNT, DEFINITION) trigger fall-back-to-LLM for now;
# Phase 2 exposes more.
SUBSTRATE_ANSWERABLE = frozenset({
    IntentClass.LOOKUP,
    IntentClass.KG_LOOKUP,
    IntentClass.MULTI_HOP,
    IntentClass.CHAIN,
})


# ---------------- Lightweight intent training corpus (for M1.1 standalone) ----------------

# M1.1 ships with a compact in-memory training corpus so the API is self-contained
# and the smoke test doesn't require dataset paths. M1.2 will swap to the full
# HotpotQA + NQ-open + ConceptNet corpus per the chain-grade cell.
_M1_1_INTENT_TRAINING = [
    # LOOKUP / KG_LOOKUP
    ("Who is the president of France?", IntentClass.LOOKUP),
    ("What is the capital of Japan?", IntentClass.LOOKUP),
    ("When was Einstein born?", IntentClass.LOOKUP),
    ("What language is spoken in Brazil?", IntentClass.LOOKUP),
    ("Who wrote Hamlet?", IntentClass.LOOKUP),
    ("What is the population of Tokyo?", IntentClass.LOOKUP),
    ("Where is the Eiffel Tower located?", IntentClass.LOOKUP),
    ("Who founded Microsoft?", IntentClass.LOOKUP),
    ("What year did World War II end?", IntentClass.LOOKUP),
    ("Who painted the Mona Lisa?", IntentClass.LOOKUP),
    # MULTI_HOP / CHAIN
    ("Who directed the film starring Marlon Brando in The Godfather?", IntentClass.MULTI_HOP),
    ("What is the capital of the country where the Amazon River begins?", IntentClass.MULTI_HOP),
    ("Who wrote the book that inspired the movie Blade Runner?", IntentClass.MULTI_HOP),
    ("What language is spoken in the country bordering Germany to the west?", IntentClass.MULTI_HOP),
    ("Who founded the company that makes the iPhone, and where was that person born?", IntentClass.MULTI_HOP),
    ("What is the largest city in the country whose flag has a maple leaf?", IntentClass.MULTI_HOP),
    ("Who painted the ceiling of the chapel where the Pope is elected?", IntentClass.MULTI_HOP),
    ("What river flows through the city where Shakespeare was born?", IntentClass.MULTI_HOP),
    # COMPARISON
    ("Which is larger, Mars or Mercury?", IntentClass.COMPARISON),
    ("Who is older, Einstein or Newton?", IntentClass.COMPARISON),
    ("Which country has more people, China or India?", IntentClass.COMPARISON),
    ("Which mountain is taller, Everest or K2?", IntentClass.COMPARISON),
    ("Is the Pacific or Atlantic deeper?", IntentClass.COMPARISON),
    ("Which sport is older, soccer or rugby?", IntentClass.COMPARISON),
    # LIST
    ("List the planets in our solar system.", IntentClass.LIST),
    ("Name the seven continents.", IntentClass.LIST),
    ("List the colors of the rainbow.", IntentClass.LIST),
    ("Name the members of the Beatles.", IntentClass.LIST),
    ("List the noble gases.", IntentClass.LIST),
    # COUNT
    ("How many planets are in our solar system?", IntentClass.COUNT),
    ("How many bones are in the human body?", IntentClass.COUNT),
    ("How many countries are in Africa?", IntentClass.COUNT),
    ("How many continents are there?", IntentClass.COUNT),
    ("How many days are in a leap year?", IntentClass.COUNT),
    # DEFINITION
    ("What is photosynthesis?", IntentClass.DEFINITION),
    ("Define entropy.", IntentClass.DEFINITION),
    ("What is a black hole?", IntentClass.DEFINITION),
    ("What does democracy mean?", IntentClass.DEFINITION),
    ("Definition of recursion.", IntentClass.DEFINITION),
    # CHAIN (causal/temporal sequences)
    ("What causes rain, and then what does rain cause?", IntentClass.CHAIN),
    ("First the volcano erupts, then what, then what?", IntentClass.CHAIN),
    ("What leads to inflation, and then what does inflation lead to?", IntentClass.CHAIN),
    ("Photosynthesis leads to what, and then what?", IntentClass.CHAIN),
]


# ---------------- KG lookup minimal fixture (M1.1 standalone) ----------------

# Tiny KG used so kg_lookup is callable + the smoke test can exercise it without
# the full FB15k-237 load. Real M1.2 loads from data/datasets/.
_M1_1_KG_TRIPLES = [
    ("France", "capital", "Paris"),
    ("Japan", "capital", "Tokyo"),
    ("Brazil", "language", "Portuguese"),
    ("Italy", "capital", "Rome"),
    ("Germany", "capital", "Berlin"),
    ("UnitedStates", "capital", "WashingtonDC"),
    ("Einstein", "born_in", "Germany"),
    ("Hamlet", "written_by", "Shakespeare"),
    ("MonaLisa", "painted_by", "DaVinci"),
    ("Microsoft", "founded_by", "BillGates"),
    ("BillGates", "born_in", "UnitedStates"),
    ("Tokyo", "population", "13960000"),
    ("EiffelTower", "located_in", "Paris"),
    ("Paris", "located_in", "France"),
    ("Berlin", "located_in", "Germany"),
]


@dataclass
class APIConfig:
    """Configuration for SubstrateRouterAPI (all defaults chain-grade-justified)."""
    n_dim: int = 2048
    intent_seed: int = 7
    intent_softmax_beta: float = 8.0  # moderate beta; informative cross-class margin
    refuse_tau: float = 0.35  # calibration default; M1.2 will recompute per-cell
    enable_trace: bool = False


# ---------------- The API ----------------


class SubstrateRouterAPI:
    """Thin function-style interface exposing chain-grade substrate primitives.

    Calls:
      - classify_intent(query) -> (IntentClass, confidence_in_[0,1])
      - kg_lookup(entity, relation) -> (answer_or_None, confidence)
      - is_refused(query, intent) -> bool   (refuse-gate fires below tau)

    M1.1 SCOPE: in-memory tiny training corpus + tiny KG fixture so the routing
    logic is exercisable standalone. M1.2 will load the chain-grade cell's full
    corpus + the ingested FB15k-237 KGStore from disk.

    Confidence regime: softmax(beta * cosine_scores); beta=8 keeps the softmax
    informative (NOT Dirac collapse). For intent classifier confidence is computed
    as softmax_max over the 7 substrate categories; KG_LOOKUP is reassigned
    post-hoc when the predicted class is LOOKUP AND the query parses into a
    (entity, relation) pair.
    """

    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or APIConfig()
        self.encoder = CharTrigramEncoder(n_dim=self.config.n_dim)

        # --- Intent classifier (Hebbian-bound) ---
        # Build the substrate-native classifier from the M1.1 in-memory training corpus.
        self._categories: list[IntentClass] = [
            IntentClass.LOOKUP, IntentClass.COMPARISON, IntentClass.MULTI_HOP,
            IntentClass.LIST, IntentClass.CHAIN, IntentClass.COUNT, IntentClass.DEFINITION,
        ]
        self._cat_to_id = {c: i for i, c in enumerate(self._categories)}
        self._cat_codebook = self._build_cat_codebook()
        self._intent_W = self._train_intent_W()

        # --- KG store (tiny fixture for M1.1) ---
        self._kg_entities: list[str] = []
        self._kg_relations: list[str] = []
        self._kg_triples: list[tuple[int, int, int]] = []
        self._build_tiny_kg(_M1_1_KG_TRIPLES)
        self._kg_W = self._build_kg_W()

    # ---------------- Intent classifier ----------------

    def _build_cat_codebook(self) -> np.ndarray:
        rng = np.random.default_rng(int(self.config.intent_seed) * 1009 + 17)
        return (rng.integers(0, 2, size=(len(self._categories), self.config.n_dim)) * 2 - 1).astype(np.float32)

    def _train_intent_W(self) -> np.ndarray:
        """Hebbian-bind training questions to their category HDs (a1 mechanism)."""
        train_hds = np.stack([
            self.encoder.encode(q) for (q, _) in _M1_1_INTENT_TRAINING
        ], axis=0)
        labels = np.array([self._cat_to_id[c] for (_, c) in _M1_1_INTENT_TRAINING], dtype=np.int64)
        cat_per_q = self._cat_codebook[labels]
        W = (cat_per_q.T @ train_hds) / float(self.config.n_dim)
        return W.astype(np.float32)

    def _intent_scores(self, query: str) -> np.ndarray:
        """Return per-category cosine-like scores [N_CAT] for the query.

        Score = cat_codebook @ W @ q_hd  (the a1 hebbian_predict mechanism).
        Normalized by N_DIM scale so softmax beta is in a regime-stable range.
        """
        q_hd = self.encoder.encode(query)
        Wq = self._intent_W @ q_hd
        scores = self._cat_codebook @ Wq
        # Normalize to [-1, 1]-ish range so softmax beta is interpretable.
        scores = scores / float(self.config.n_dim)
        return scores

    def classify_intent(self, query: str) -> tuple[IntentClass, float]:
        """Substrate-native intent classifier; returns (intent_class, confidence in [0,1]).

        Confidence = softmax(beta * scores)[argmax] -- the posterior mass on the picked
        class. beta is moderate (8.0) so a strong winner (e.g. LOOKUP scoring much higher
        than COMPARISON) gets confidence > 0.5, but a tie cluster stays near 1/N_CAT.

        KG_LOOKUP reassignment: if predicted LOOKUP AND the query parses as an
        (entity, relation) pair against the loaded KG, returns KG_LOOKUP instead.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("classify_intent: query must be non-empty string")
        scores = self._intent_scores(query)
        # Numerically stable softmax with our moderate beta.
        z = self.config.intent_softmax_beta * scores
        z = z - float(np.max(z))
        exp_z = np.exp(z)
        probs = exp_z / float(np.sum(exp_z))
        pred_idx = int(np.argmax(probs))
        pred_cls = self._categories[pred_idx]
        confidence = float(probs[pred_idx])

        # KG_LOOKUP reassignment when LOOKUP + KG-parseable.
        if pred_cls == IntentClass.LOOKUP:
            parse = self._try_parse_kg_query(query)
            if parse is not None:
                return IntentClass.KG_LOOKUP, confidence

        # Specialist-override-generalist: if substrate KG can answer the query
        # with HIGH confidence (>= 0.8 in kg_lookup softmax), trust the KG
        # specialist over the intent classifier's MULTI_HOP guess. This is the
        # M1.1-scale corrective for tiny intent training corpora that under-fit
        # the LOOKUP/MULTI_HOP boundary on "What is the capital of X" patterns.
        # M1.2 with the full chain-grade 5000-example corpus may not need this.
        parse = self._try_parse_kg_query(query)
        if parse is not None:
            try:
                _, kg_conf = self.kg_lookup(parse[0], parse[1])
            except ValueError:
                kg_conf = 0.0
            if kg_conf >= 0.8:
                return IntentClass.KG_LOOKUP, kg_conf
        return pred_cls, confidence

    # ---------------- KG lookup ----------------

    def _build_tiny_kg(self, triples: Iterable[tuple[str, str, str]]) -> None:
        ent_set: set[str] = set()
        rel_set: set[str] = set()
        for s, p, o in triples:
            ent_set.add(s); rel_set.add(p); ent_set.add(o)
        self._kg_entities = sorted(ent_set)
        self._kg_relations = sorted(rel_set)
        e2i = {e: i for i, e in enumerate(self._kg_entities)}
        r2i = {r: i for i, r in enumerate(self._kg_relations)}
        self._kg_triples = [(e2i[s], r2i[p], e2i[o]) for (s, p, o) in triples]

    def _build_kg_W(self) -> dict:
        """Tiny KGStore-equivalent: per-entity / per-relation bipolar HDs + Hebbian W."""
        n_ent = len(self._kg_entities)
        n_rel = len(self._kg_relations)
        n_dim = self.config.n_dim
        sq = math.sqrt(n_dim)
        rng = np.random.default_rng(int(self.config.intent_seed) * 991 + 13)
        E = (rng.integers(0, 2, size=(n_ent, n_dim)) * 2 - 1).astype(np.float32)
        R = (rng.integers(0, 2, size=(n_rel, n_dim)) * 2 - 1).astype(np.float32)
        W = np.zeros((n_dim, n_dim), dtype=np.float32)
        for (s_i, p_i, o_i) in self._kg_triples:
            key = E[s_i] * R[p_i] * sq
            W += np.outer(E[o_i], key) / n_dim
        return {"E": E, "R": R, "W": W, "sq": sq}

    def _try_parse_kg_query(self, query: str) -> tuple[str, str] | None:
        """Heuristic surface-form parser: matches simple `<rel> of <entity>` and
        `Who <verb> <entity>?` and `What is the <rel> of <entity>?` patterns.

        Returns (entity, relation) tuple if parseable + entity in KG; None otherwise.
        M1.2 will swap to a substrate-native compositional parse (TASK_VECTOR-based).
        """
        q = query.strip().rstrip("?").strip()
        ql = q.lower()
        # Pattern 1: "What is the <rel> of <entity>"
        if ql.startswith("what is the "):
            rest = q[len("What is the "):]
            if " of " in rest:
                rel, ent = rest.split(" of ", 1)
                rel = rel.strip(); ent = ent.strip()
                ent_norm = self._normalize_entity(ent)
                if ent_norm in self._kg_entities:
                    return (ent_norm, self._normalize_relation(rel))
        # Pattern 2: "What is the capital of X"
        if ql.startswith("what is the capital of "):
            ent = q[len("What is the capital of "):].strip().rstrip(".")
            ent_norm = self._normalize_entity(ent)
            if ent_norm in self._kg_entities:
                return (ent_norm, "capital")
        # Pattern 3: "Who founded X"
        if ql.startswith("who founded "):
            ent = q[len("Who founded "):].strip()
            ent_norm = self._normalize_entity(ent)
            if ent_norm in self._kg_entities:
                return (ent_norm, "founded_by")
        # Pattern 4: "Where is X located"
        if ql.startswith("where is the ") and " located" in ql:
            ent = q[len("Where is the "):].split(" located", 1)[0].strip()
            ent_norm = self._normalize_entity(ent)
            if ent_norm in self._kg_entities:
                return (ent_norm, "located_in")
        if ql.startswith("where is ") and " located" in ql:
            ent = q[len("Where is "):].split(" located", 1)[0].strip()
            ent_norm = self._normalize_entity(ent)
            if ent_norm in self._kg_entities:
                return (ent_norm, "located_in")
        return None

    @staticmethod
    def _normalize_entity(s: str) -> str:
        # "Eiffel Tower" -> "EiffelTower"; matches the KG fixture keys.
        return "".join(part.capitalize() for part in s.replace("the ", "").split())

    @staticmethod
    def _normalize_relation(s: str) -> str:
        return s.strip().lower().replace(" ", "_")

    def kg_lookup(self, entity: str, relation: str) -> tuple[str | None, float]:
        """Substrate KG retrieve via Hebbian-W single-hop (FB15k mechanism).

        Returns (answer_entity_string | None, confidence in [0,1]). Confidence is
        the softmax_max over all entities scored against W @ (E[s] * R[p] * sq).

        Raises ValueError if entity/relation not in the KG vocabulary (surfaces
        the failing-primitive name; router catches + falls back to LLM).
        """
        if entity not in self._kg_entities:
            raise ValueError(f"kg_lookup: entity '{entity}' not in KG (n_ent={len(self._kg_entities)})")
        if relation not in self._kg_relations:
            raise ValueError(f"kg_lookup: relation '{relation}' not in KG (n_rel={len(self._kg_relations)})")
        s_i = self._kg_entities.index(entity)
        p_i = self._kg_relations.index(relation)
        E = self._kg_W["E"]; R = self._kg_W["R"]; W = self._kg_W["W"]; sq = self._kg_W["sq"]
        key = E[s_i] * R[p_i] * sq
        scored = E @ (W @ key)
        # Normalize via softmax for confidence reading.
        scored_n = scored / float(self.config.n_dim)
        z = self.config.intent_softmax_beta * scored_n
        z = z - float(np.max(z))
        exp_z = np.exp(z)
        probs = exp_z / float(np.sum(exp_z))
        top_idx = int(np.argmax(probs))
        answer = self._kg_entities[top_idx]
        confidence = float(probs[top_idx])
        return answer, confidence

    # ---------------- Refuse-gate ----------------

    def is_refused(self, query: str, intent: IntentClass) -> bool:
        """Returns True iff substrate's confidence on the routed query falls below tau.

        Wraps the V_REL=256 chain-grade refuse-gate discipline: if the routed
        primitive's confidence is below tau, refuse (router falls back to LLM).

        For M1.1, we compute confidence by re-running the appropriate primitive:
          - LOOKUP / KG_LOOKUP: kg_lookup confidence if parseable, else intent confidence
          - MULTI_HOP / CHAIN: intent confidence (multi-hop primitive M1.3)
          - other: intent confidence
        """
        if not isinstance(query, str) or not query.strip():
            return True  # empty -> refuse
        if intent in (IntentClass.KG_LOOKUP,):
            parse = self._try_parse_kg_query(query)
            if parse is None:
                return True
            try:
                _, conf = self.kg_lookup(parse[0], parse[1])
            except ValueError:
                return True
            return conf < self.config.refuse_tau
        # Fall back to intent confidence as proxy.
        _, conf = self.classify_intent(query)
        return conf < self.config.refuse_tau

    # ---------------- Discoverability ----------------

    @property
    def categories(self) -> tuple[IntentClass, ...]:
        return tuple(self._categories)

    @property
    def kg_vocab(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        return (tuple(self._kg_entities), tuple(self._kg_relations))
