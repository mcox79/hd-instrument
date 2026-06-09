"""
Template library for /converse substrate-direct responses (PP-187 port).

Each intent maps to a list of template strings with simple variable substitution.
The router picks a template, fills in substrate-retrieved values, and returns immediately
WITHOUT calling an LLM. Sub-ms response per PP-212.

Variables (substituted via .format()):
  {fact}         a single retrieved substrate fact
  {fact_list}    a bulleted list of facts
  {count}        a cardinality integer
  {term}         user-supplied term
  {term_a}, {term_b} for compositional ops
  {included}, {excluded} for set difference
"""
from __future__ import annotations
import random
from typing import Optional


# Templates organized by intent. ~50 total spanning Phase 2 acceptance.

GREETING_TEMPLATES = [
    "Hello! I am a substrate-augmented assistant. What would you like to know?",
    "Hi there. I have access to a substrate of factual bindings; ask me anything.",
    "Hey! Substrate ready. How can I help?",
    "Greetings. I can retrieve facts, run algebraic queries, and answer counterfactuals - what do you need?",
    "Hi. Substrate is loaded; LLM is on standby. What is your question?",
    "Hello. Ready to talk. Note that 70% of responses come direct from substrate (no LLM call).",
]

FAREWELL_TEMPLATES = [
    "Goodbye. The substrate state is preserved if you return.",
    "Bye! Audit chain for this session is committed.",
    "See you. Session ends with {turn_count} turns logged.",
    "Take care.",
    "Farewell. Cumulative substrate cost for this session: $0.",
]

ACK_TEMPLATES = [
    "You're welcome.",
    "Happy to help.",
    "Glad it was useful.",
    "Sure thing.",
    "Anytime.",
]

FACTUAL_SINGLE = [
    "{fact}",
    "From substrate: {fact}",
    "Substrate-retrieved fact: {fact}",
    "{fact} (substrate-direct; no LLM call)",
]

FACTUAL_MULTI = [
    "Substrate retrieved {n} relevant facts:\n{fact_list}",
    "Found {n} facts. Most relevant:\n{fact_list}",
    "{fact_list}",
]

ABSTENTION_TEMPLATES = [
    "I do not have facts on that in the substrate. Substrate confidence is below threshold for an honest answer.",
    "Substrate has no high-confidence binding for that query. Honest abstention - no hallucination.",
    "I do not know based on the loaded substrate. Add a fact via /add_fact if you want me to remember it.",
    "Substrate does not contain that knowledge. (PP-107 abstention triggered.)",
]

CLARIFICATION_TEMPLATES = [
    "What part should I clarify? My previous answer was: '{last_response}'",
    "Sure - which detail do you want me to expand on?",
    "Happy to elaborate. Specify what is unclear: the source fact, the latency, or the audit chain?",
    "I can re-explain. What specifically needs more detail?",
]

COMPOSITIONAL_AND = [
    "Substrate AND({term_a}, {term_b}) = {count} fact(s):\n{fact_list}",
    "Set intersection - {count} fact(s) contain both '{term_a}' AND '{term_b}':\n{fact_list}",
    "{count} facts mention both '{term_a}' and '{term_b}': {fact_list}",
]

COMPOSITIONAL_NOT = [
    "Substrate {included} NOT {excluded} = {count} fact(s):\n{fact_list}",
    "Set difference - {count} fact(s) contain '{included}' but NOT '{excluded}':\n{fact_list}",
]

COMPOSITIONAL_COUNT = [
    "Substrate cardinality: {count} fact(s) mention '{term}'.",
    "{count} facts contain '{term}'.",
    "COUNT('{term}') = {count} of {kb_size} substrate facts.",
]

COUNTERFACTUAL_TEMPLATES = [
    "Counterfactual do() result: {summary}. Audit chain committed.",
    "If we apply do({intervention}), the substrate recomputes: {summary}",
    "Pearl do() over the DAG: factual = {factual}; counterfactual = {counterfactual}; differences = {diffs}",
]

COMPUTATION_TEMPLATES = [
    "Computed: {expression} = {result}",
    "{expression} = {result}",
    "Result: {result}",
]

CREATIVE_HANDOFF = [
    "Creative tasks (poems, stories, opinions) are routed to the LLM - calling now...",
    "Substrate handles facts; creative generation calls the LLM. Routing query...",
    "Engaging LLM for language generation (substrate alone does not compose creative content).",
]

UNCERTAIN_TEMPLATES = [
    "I am not sure what you are asking. Could you rephrase?",
    "That message did not match any intent I can handle. Try rephrasing or be more specific.",
    "Substrate intent classifier returned uncertain. Please clarify.",
]


_INTENT_TO_TEMPLATES = {
    "greeting": GREETING_TEMPLATES,
    "farewell": FAREWELL_TEMPLATES,
    "acknowledgment": ACK_TEMPLATES,
    "factual_single": FACTUAL_SINGLE,
    "factual_multi": FACTUAL_MULTI,
    "abstention": ABSTENTION_TEMPLATES,
    "clarification": CLARIFICATION_TEMPLATES,
    "compositional_and": COMPOSITIONAL_AND,
    "compositional_not": COMPOSITIONAL_NOT,
    "compositional_count": COMPOSITIONAL_COUNT,
    "counterfactual": COUNTERFACTUAL_TEMPLATES,
    "computation": COMPUTATION_TEMPLATES,
    "creative_handoff": CREATIVE_HANDOFF,
    "uncertain": UNCERTAIN_TEMPLATES,
}


def pick_template(category: str, seed: Optional[int] = None) -> str:
    """Pick a template by category, deterministic if seed given."""
    pool = _INTENT_TO_TEMPLATES.get(category)
    if not pool:
        return "(no template available)"
    if seed is None:
        return random.choice(pool)
    return pool[seed % len(pool)]


def render(category: str, seed: Optional[int] = None, **kwargs) -> str:
    """Pick a template and substitute kwargs via .format()."""
    tpl = pick_template(category, seed=seed)
    try:
        return tpl.format(**kwargs)
    except KeyError as e:
        return tpl + f" (missing template var: {e})"


def total_template_count() -> int:
    return sum(len(p) for p in _INTENT_TO_TEMPLATES.values())


def _self_test():
    # Category coverage + variable substitution
    cases = [
        ("greeting", {}),
        ("farewell", {"turn_count": 5}),
        ("acknowledgment", {}),
        ("factual_single", {"fact": "Anthropic was founded in 2021."}),
        ("factual_multi", {"n": 3, "fact_list": "- a\n- b\n- c"}),
        ("abstention", {}),
        ("clarification", {"last_response": "Substrate found 12 facts."}),
        ("compositional_and", {"term_a": "Anthropic", "term_b": "OpenAI", "count": 1, "fact_list": "- Dario was at OpenAI"}),
        ("compositional_not", {"included": "founded", "excluded": "2023", "count": 5, "fact_list": "- ..."}),
        ("compositional_count", {"term": "substrate", "count": 12, "kb_size": 169}),
        ("counterfactual", {"summary": "founder_still_ceo flipped True", "intervention": "year=2020", "factual": "F", "counterfactual": "T", "diffs": "{age:11->6}"}),
        ("computation", {"expression": "2 + 2", "result": 4}),
        ("creative_handoff", {}),
        ("uncertain", {}),
    ]
    for cat, kwargs in cases:
        rendered = render(cat, seed=0, **kwargs)
        assert rendered, f"empty render for {cat}"
        assert "{" not in rendered or "missing template" in rendered, f"unsubstituted vars in {cat}: {rendered}"

    total = total_template_count()
    assert total >= 40, f"need >= 40 templates total (Phase 2 gate), got {total}"
    print(f"[converse.templates] self-test PASS ({total} templates across {len(_INTENT_TO_TEMPLATES)} categories)")


if __name__ == "__main__":
    _self_test()
