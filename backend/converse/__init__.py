"""
Substrate-first /converse cascade router.

Per strategic reframe (substrate-around-LLM): substrate IS the AI; LLM is called only
when language generation is genuinely needed (creative / synthesis / opinion).

All primitives empirically validated (PP-187/188/195/198/212/123/107/180-184).
Engineering is wiring + templates + frontend, not new substrate capability.

Modules:
    intent.py       Intent classification (PP-198 prototype): GREETING / FAREWELL / ACK /
                    FACTUAL / CLARIFICATION / COMPUTATION / COMPOSITIONAL / COUNTERFACTUAL /
                    CREATIVE / UNCERTAIN
    templates.py    Template library organized by intent (PP-187)
    state.py        Multi-turn session state (PP-195): session_id -> turn history
    handlers.py     Per-intent handler functions invoked by the cascade router
"""
