"""Score the ten V2 cases and their controls with three Future AGI rubrics, using an LLM as the judge.

The rubric text (config.rule_prompt) is read unchanged from a checkout of future-agi/future-agi,
futureagi/model_hub/system_evals/agent/. The Future AGI platform uses its own judge model and
output wrapper, which are not in that repository, so this script asks the judge for a JSON object
{"result", "reason"}. The numbers are a proxy that uses their rubric text.

Usage, from the repository root:
  python examples/v2_controls/run_rubrics_v2.py
      Reads the recorded run (v2_rubric_results.json) and prints the summary. No model calls.
  python examples/v2_controls/run_rubrics_v2.py --judge --rubrics-dir <future-agi>/futureagi/model_hub/system_evals/agent
      Calls the judge once per rubric and variant (60 calls) and writes v2_rubric_results_rerun.json.
      Needs the anthropic package and ANTHROPIC_API_KEY. --model sets the judge (default claude-opus-5-5).

A case counts as flagged when Conversation Coherence is below 0.5 or Persona Consistency fails.
"""
import argparse
import json
import os
import re
import uuid

import v2_cases_en as V

HERE = os.path.dirname(os.path.abspath(__file__))
RUBRICS = {"conversation_coherence": "conversation_coherence.yaml",
           "persona_consistency": "persona_consistency.yaml",
           "loop_detection": "customer_agent_loop_detection.yaml"}


def prompt_for(rule, variant):
    conv = "\n".join("%s: %s" % tuple(m) for m in variant["msgs"])
    return (rule.replace("{{conversation}}", conv) +
            '\n\nReturn only a JSON object: {"result": <your score, choice or Passed/Failed>, '
            '"reason": "<one sentence>"}.\n(run id %s)' % uuid.uuid4().hex[:8])


def judge(rubrics_dir, model):
    import anthropic
    import yaml
    client = anthropic.Anthropic()
    rules = {k: yaml.safe_load(open(os.path.join(rubrics_dir, f), encoding="utf-8"))["config"]["rule_prompt"]
             for k, f in RUBRICS.items()}
    rows = []
    for v in V.all_variants():
        res, why = {}, {}
        for k, rule in rules.items():
            msg = client.messages.create(model=model, max_tokens=3000,
                                         messages=[{"role": "user", "content": prompt_for(rule, v)}])
            text = "".join(b.text for b in msg.content if b.type == "text")
            m = re.search(r"\{.*\}", text, re.S)
            try:
                parsed = json.loads(m.group(0)) if m else {}
            except json.JSONDecodeError:
                parsed = {}
            res[k], why[k] = parsed.get("result"), parsed.get("reason")
            print("%-7s %-24s %s" % (v["id"], k, res[k]), flush=True)
        rows.append({"id": v["id"], "results": res, "reasons": why})
    out = {"judge_model": model, "calls_per_rubric_and_variant": 1, "rows": rows}
    json.dump(out, open(os.path.join(HERE, "v2_rubric_results_rerun.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    return out


def flagged(results):
    coh = results.get("conversation_coherence")
    persona = str(results.get("persona_consistency") or "").lower()
    return (isinstance(coh, (int, float)) and coh < 0.5) or persona.startswith("fail")


def summary(data):
    rows = {r["id"]: r["results"] for r in data["rows"]}
    print("judge model:", data["judge_model"])
    print("%-7s %-11s %-12s %-14s %s" % ("case", "coherence", "persona", "loop", "flagged"))
    for rid, r in rows.items():
        print("%-7s %-11s %-12s %-14s %s" % (rid, r.get("conversation_coherence"), r.get("persona_consistency"),
                                            r.get("loop_detection"), flagged(r)))
    bad = [rid for rid in rows if not rid.endswith("-ctl")]
    print("flagged originals: %d of %d" % (sum(flagged(rows[i]) for i in bad), len(bad)))
    print("flagged controls:  %d of %d" % (sum(flagged(rows[i + "-ctl"]) for i in bad), len(bad)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--rubrics-dir")
    ap.add_argument("--model", default="claude-opus-5-5")
    a = ap.parse_args()
    if a.judge:
        if not a.rubrics_dir:
            ap.error("--judge needs --rubrics-dir")
        summary(judge(a.rubrics_dir, a.model))
    else:
        summary(json.load(open(os.path.join(HERE, "v2_rubric_results.json"), encoding="utf-8")))
