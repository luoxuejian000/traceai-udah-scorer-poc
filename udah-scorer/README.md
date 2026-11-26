# udah-scorer

Deterministic U/D/A/H scores for multi-turn conversations and for traceAI exports.
Standard library only, Python 3.10 or later, no model calls.

## What it computes

The scoring core is `trajectory_v3_ultra.py` by Guanghao Li. This package ships it
byte-identical to the copy at the root of the repository and only wraps it: a command line, a
traceAI adapter, and tests. `udah verify-core` checks the installed core against its pinned hash.

For each assistant turn the core returns four numbers:

- **U** (Unity)
- **D** (Development)
- **A** (Adversarial)
- **H** (Harmony) = 0.4 U + 0.4 D - 0.2 A

The scores are diagnostics only. The package gives no advice and generates no text.

## Install

```bash
pip install udah-scorer
```

## Use

```bash
udah text "Rayleigh scattering: shorter wavelengths scatter more."
udah traceai trace.json --out turn_scores.csv
udah cases --input cases.json
udah verify-core
```

From Python:

```python
from udah_scorer import score_text
u, d, a, h = score_text("Rayleigh scattering: shorter wavelengths scatter more.")
```

`udah traceai` reads a traceAI export (OTLP JSON, a JSON list of spans, or JSONL), groups spans
by `session.id`, and scores each conversation turn once, even when every request resends the
whole history. `gen_ai.usage.*` is copied from the span.

## What has been measured

On the ten silent-dissonance cases in `examples/v2_controls/` of the repository, each with a
matched control in which only the last reply changes:

- the bad reply scored lower in H than its control in 8 of 10;
- a fixed threshold H < 0.3 flagged 1 of 10 bad replies and 0 of 10 controls;
- on the circular-reasoning case, H fell from 0.58 to 0.16 and D to 0.04, while the control
  stayed at H 0.50.

Read these as a paired comparison on a small set, not as a detector's accuracy. The core uses
word lists and fixed weights, so its behaviour depends on the vocabulary of the text.

## Tests

```bash
python -m unittest discover -s tests
```

The tests check that the core matches its pinned hash, that the V2-06 example reproduces
H 0.5759 to 0.1559, that the adapter gives the same scores as the core run on the same
conversation, and that each turn is counted once.

## License

MIT, see `LICENSE`.
