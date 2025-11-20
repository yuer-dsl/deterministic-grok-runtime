"""
100x reproducibility test.

Expected:
- With deterministic plan + deterministic runtime,
  all hashes should be identical.
"""

import hashlib
from runtime.execute_chain_stub import execute_chain
from compiler.static_plan_compiler import StaticPlanCompiler


def sha256(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()


def run_repro_test():
    compiler = StaticPlanCompiler()
    compiled, sig = compiler.compile("examples/static_reasoning_chain.yaml")

    hashes = []
    for i in range(100):
        out = execute_chain(compiled, inputs={
            "current_date": "2025-11-20",
            "current_price_usd": 93000,
        })
        h = sha256(out)
        hashes.append(h)
        print(f"Run {i+1:3d}: {h}")

    uniq = set(hashes)
    print("\nUnique hashes:", uniq)
    if len(uniq) == 1:
        print("\n✓ 100% reproducible.")
    else:
        print("\n✗ Non-deterministic behavior detected.")


if __name__ == "__main__":
    run_repro_test()
