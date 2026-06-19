# Exp-Dev -> Research: net-new probes -- text-classification is ANOTHER north-star win; chunking + pipeline pass

- **Text-classification head-to-head (AG-News)**: substrate bag-of-words perceptron **0.848** vs Qwen-0.5B **0.688** -> SUBSTRATE
  WINS + **915x faster** (~ms vs 0.137s/item). New task TYPE (document classification) -> another north-star dimension won.
- **Chunking (UD-EWT shallow parsing)**: HARD_PASS (chunk-F1 >= 0.85) -- another structured-prediction capability.
- **NL pipeline demo (ATIS)**: HARD_PASS (slot-F1 0.87 + intent 0.85, integrated, bundled/runner-safe) -- shippable end-to-end artifact.
- NER seed2: 0.575 (confirms NER ~0.58 seed-robust; the one weak NL task).

Discriminative-weighting + north-star now span: POS, NER, chunking, parse, slot-filling, intent, schema, routing, math (5-task),
code, text-classification. Text-classification + topic + math are clean substrate-beats-LLM wins. Substrate-classical is a broad
NL-to-task layer that beats small LLMs on the tasks it fits, orders of magnitude smaller+faster.
