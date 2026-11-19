# V2 cases: rerun the numbers

This folder lets anyone rerun the two comparisons on the ten V2 cases (cases 1-10 of the test set in the repository root).

## H on the bad reply and on a sound control

`v2_controls.txt` holds one control per case: the same user turns and first reply, and a sound second reply. `check_h_threshold.py` runs `trajectory_v3_ultra.py` unchanged on both files and compares H on the last reply. No model calls.

```
python examples/v2_controls/check_h_threshold.py
```

Output on commit d5b96b3:

| measure | result |
|---|---|
| bad reply lower in H than its control | 8 of 10 |
| H < 0.3 on the bad reply | 1 of 10 (Circular Logic) |
| H < 0.3 on the control | 0 of 10 |

## Future AGI rubrics as an LLM judge

`v2_cases_en.py` is an English translation of the ten cases and their controls. `run_rubrics_v2.py` scores them with Conversation Coherence, Persona Consistency and Loop Detection. The rubric text is read unchanged from `future-agi/future-agi`, `futureagi/model_hub/system_evals/agent/`. The platform's own judge setup is not in that repository, so the judge is an LLM asked for a JSON result. The numbers are a proxy that uses their rubric text.

Without arguments, the script prints the recorded run (`v2_rubric_results.json`, Claude Opus 5.5 as judge, one call per rubric and variant, 2026-11-18):

```
python examples/v2_controls/run_rubrics_v2.py
```

To rerun with a judge (60 calls; needs `anthropic`, `pyyaml` and `ANTHROPIC_API_KEY`):

```
python examples/v2_controls/run_rubrics_v2.py --judge --rubrics-dir <future-agi>/futureagi/model_hub/system_evals/agent
```

A case counts as flagged when Coherence is below 0.5 or Persona Consistency fails. In the recorded run, 8 of 10 originals are flagged (all but Semantic Drift and Circular Logic) and 0 of 10 controls.
