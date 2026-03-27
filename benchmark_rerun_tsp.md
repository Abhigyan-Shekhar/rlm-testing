# Under-Specified TSP Benchmark Rerun Note

This note records the latest observed behavior for the cheapest matched LLM / `RLM` benchmark in this repo.

## Prompt
The benchmark prompt is the under-specified 8-city TSP used by:

- [`test_tsp_llm_only.py`](./test_tsp_llm_only.py)
- [`test_tsp_branch_bound.py`](./test_tsp_branch_bound.py)

The prompt intentionally omits the distance matrix. The grounded answer is that the problem cannot be solved as stated because the distances are missing.

## Rerun Commands

Standard paired run:

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate
python3 test_tsp_llm_only.py
python3 test_tsp_branch_bound.py
```

If the baseline call stalls and you still want the `RLM` result on the same prompt, run `RLM` directly:

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate
python3 - <<'PY'
import os
from dotenv import load_dotenv
from rlm import RLM
from rlm.logger import RLMLogger

load_dotenv(".env")

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

agent = RLM(
    backend="gemini",
    backend_kwargs={
        "api_key": os.environ["GEMINI_API_KEY"],
        "model_name": "gemini-2.5-flash",
    },
    environment="local",
    environment_kwargs={"disable_plain_lm_queries": True},
    max_depth=3,
    max_recursive_calls=3,
    max_iterations=6,
    verbose=True,
    logger=RLMLogger(),
)

result = agent.completion(prompt)
print("\nRLM ANSWER:\n" + result.response)
PY
```

## Latest Observed Result

Observed date: `2026-03-27`

- Baseline LLM run:
  - `test_tsp_llm_only.py`
  - Gemini request stalled in the API call and had to be interrupted manually
  - No usable completion was produced in that run

- `RLM` run on the same prompt:
  - completed successfully
  - correctly identified that the distance matrix was missing
  - refused to fabricate a tour or costs

Observed `RLM` answer:

> Final Answer: I cannot solve the Traveling Salesman Problem as presented because the crucial piece of information, the distance matrix between the 8 cities (A, B, C, D, E, F, G, H), is missing from the provided context. Without these distances, it is impossible to calculate path costs, establish an upper bound, perform pruning, or determine the optimal tour and its cost using the specified branch-and-bound strategy.

Observed `RLM` metrics:

- Execution time: `20.25s`
- Input tokens: `24,367`
- Output tokens: `1,006`
- Total tokens: `25,373`

## Interpretation

- This benchmark is useful for checking whether the model invents missing structure.
- A grounded model should refuse to solve the problem and explicitly point out that the distance matrix is missing.
- A hallucinating model will often invent a matrix, fake branch-and-bound steps, and claim an optimal tour.
