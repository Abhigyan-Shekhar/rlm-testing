import os
import time

from dotenv import load_dotenv

from rlm.clients import get_client

load_dotenv()

prompt = """You are solving a Traveling Salesman Problem with 8 cities.

Cities: A, B, C, D, E, F, G, H

Distance matrix is symmetric and satisfies triangle inequality.

Task:
- Find the optimal tour
- You MUST use a branch-and-bound or systematic search strategy

Solve the Traveling Salesman Problem below.

IMPORTANT:
You must NOT compute all permutations directly.
Instead:
- Use logical reasoning to eliminate impossible or suboptimal paths early
- Justify every pruning decision

STRICT REQUIREMENTS:
- Maintain a table of explored paths
- Track current best solution (upper bound)
- Prune paths that exceed current best
- Show recursive exploration clearly

After giving the answer, explain:
"Why is this solution guaranteed optimal?"

Output format:
1. Exploration steps
2. Pruned branches with reasons
3. Final optimal path and cost
"""

expected_result = (
    "The problem is under-specified. No optimal tour can be determined because "
    "the actual distance matrix values are missing."
)

backend_kwargs = {
    "api_key": os.environ["GEMINI_API_KEY"],
    "model_name": "gemini-2.5-flash",
}

print("Waiting 15 seconds for rate limit to cool down...")
time.sleep(15)

print("\n" + "=" * 70)
print("PROMPT")
print("=" * 70)
print(prompt)

print("\n" + "=" * 70)
print("EXPECTED CORRECT RESULT")
print("=" * 70)
print(expected_result)

print("\n" + "=" * 70)
print("BASELINE LLM")
print("=" * 70)

client = get_client("gemini", backend_kwargs.copy())
wall_start = time.perf_counter()
response = client.completion(prompt)
wall_end = time.perf_counter()

print(response)
print("\n" + "-" * 40)
print(f"Baseline wall time: {wall_end - wall_start:.3f}s")

usage = client.get_usage_summary().to_dict()
for model_name, model_usage in usage.get("model_usage_summaries", {}).items():
    print(
        f"{model_name}: input={model_usage.get('total_input_tokens', 0):,}, "
        f"output={model_usage.get('total_output_tokens', 0):,}, "
        f"calls={model_usage.get('total_calls', 0)}"
    )
