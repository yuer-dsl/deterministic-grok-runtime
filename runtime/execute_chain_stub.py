"""
A minimal runtime stub for executing compiled reasoning chains.

NOTE:
- Grok-1 API/JAX integration intentionally left as TODO.
- This file ensures the project remains framework-agnostic.
"""

import json
import yaml
from pathlib import Path


def call_grok_stub(prompt: str, params: dict) -> str:
    """
    Stub for Grok-1 calls. Replace with actual JAX or API calls.
    """
    return f"[STUB OUTPUT for prompt hash={hash(prompt) % 100000}]"


def execute_chain(compiled_yaml: str, inputs: dict) -> str:
    with Path(compiled_yaml).open("r", encoding="utf-8") as f:
        chain = yaml.safe_load(f)

    ctx = {}

    for step in chain["reasoning_chain"]:
        sid = step["id"]

        if step["type"] == "llm_call":
            tmpl = step["llm_call"]["prompt_template"] if "prompt_template" in step["llm_call"] else step["llm_call"]["prompt"]
            fmt = {}
            fmt.update(inputs)
            fmt.update({f"{k}_output": v for k, v in ctx.items()})
            prompt = tmpl.format(**fmt)

            out = call_grok_stub(prompt, step["llm_call"])
            ctx[sid] = out

        elif step["type"] == "tool_call":
            args = step["tool_call"]["args"]
            prev = json.loads(ctx[args["input_from"]])
            iw = args.get("impact_weight", 0.6)
            lw = args.get("likelihood_weight", 0.4)
            scores = [(x["impact_score"] * iw + x["likelihood_score"] * lw) for x in prev]
            ctx[sid] = json.dumps({"scores": scores, "avg": sum(scores) / len(scores)}, sort_keys=True)

    return ctx[ list(ctx.keys())[-1] ]
