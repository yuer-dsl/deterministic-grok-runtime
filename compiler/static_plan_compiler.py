# ==================== static_plan_compiler.py ====================
"""
Static Reasoning-Chain Compiler for Grok-1

- Loads a reasoning-chain YAML file
- Normalizes sampling parameters
- Adds metadata + SHA256 signature
- Outputs a deterministic .compiled.yaml plan

This file is framework-agnostic and does NOT depend on any internal OS concepts.
"""

import yaml
import hashlib
from datetime import datetime
from pathlib import Path


class StaticPlanCompiler:
    def __init__(self):
        self.signature = None

    def compile(self, yaml_path: str):
        yaml_path = Path(yaml_path)
        with yaml_path.open("r", encoding="utf-8") as f:
            chain = yaml.safe_load(f) or {}

        # Normalize sampling parameters
        for step in chain.get("reasoning_chain", []):
            llm = step.get("llm_call")
            if llm:
                llm["temperature"] = 0.0
                llm.setdefault("top_p", 1.0)
                llm.setdefault("presence_penalty", 0.0)
                llm.setdefault("frequency_penalty", 0.0)

        # Generate SHA256 signature
        content = yaml.dump(chain, sort_keys=True, allow_unicode=True)
        self.signature = hashlib.sha256(content.encode("utf-8")).hexdigest()

        chain["meta"] = {
            "compiled_at": datetime.utcnow().isoformat() + "Z",
            "compiler": "StaticPlanCompiler v0.1",
            "signature_sha256": self.signature,
            "deterministic_sampling": True,
        }

        compiled_path = yaml_path.with_suffix(".compiled.yaml")
        with compiled_path.open("w", encoding="utf-8") as f:
            yaml.dump(chain, f, allow_unicode=True, sort_keys=False)

        print(f"[compiler] Compiled: {compiled_path}")
        print(f"[compiler] Signature: {self.signature}")

        return str(compiled_path), self.signature


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compile a static reasoning chain.")
    parser.add_argument("yaml_path", help="Reasoning chain YAML file.")
    args = parser.parse_args()

    compiler = StaticPlanCompiler()
    compiler.compile(args.yaml_path)
