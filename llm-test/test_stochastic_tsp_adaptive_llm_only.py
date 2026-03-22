import os
import time

from dotenv import load_dotenv

from rlm.clients import get_client

load_dotenv()

prompt = """You are a salesman at city A. Cities are A, B, C, D, E. You must visit all cities and return to A.
Edge costs are stochastic — each edge has a base cost, but when you arrive at a city, you roll a private die and learn a local multiplier that applies to all edges leaving that city. This multiplier is unknown until you arrive.
Base edge costs (bidirectional):
EdgeBase CostA↔B4A↔C6A↔D5A↔E8B↔C3B↔D7B↔E2C↔D4C↔E5D↔E3
Multiplier distribution at each city (independent):

With probability 0.5 → multiplier = 0.5 (lucky city)
With probability 0.5 → multiplier = 2.0 (unlucky city)

The actual cost of traveling from city X to city Y = (X's multiplier) × (base cost of X↔Y)
You learn city X's multiplier only when you arrive at X, before deciding where to go next.
You start at A and immediately learn A's multiplier before your first move.
Question:
Derive the optimal adaptive policy — a complete decision tree of the form "at city X, having visited set S, with multiplier m, go to city Y" — that minimizes expected total cost. Then compute the exact expected cost of this optimal policy.
"""

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
