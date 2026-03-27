# Stochastic Adaptive TSP Benchmark Rerun Note

This note records the latest observed metrics for the stochastic adaptive TSP benchmark in this repo.

## Prompt
The benchmark prompt is the stochastic adaptive TSP used by:

- [`test_stochastic_tsp_adaptive_llm_only.py`](./test_stochastic_tsp_adaptive_llm_only.py)
- [`test_stochastic_tsp_adaptive.py`](./test_stochastic_tsp_adaptive.py)

The task asks for:

- the optimal adaptive policy as a full decision tree
- the exact expected total cost of that policy

## Rerun Commands

Standard paired run:

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate
python3 test_stochastic_tsp_adaptive_llm_only.py
python3 test_stochastic_tsp_adaptive.py
```

If you want only the `RLM` run:

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate
python3 test_stochastic_tsp_adaptive.py
```

## Latest Observed Result

Observed date: `2026-03-27`

Observed `RLM` metrics from `test_stochastic_tsp_adaptive.py`:

- Total wall time: `73.576s`
- RLM execution time: `73.378s`
- Overhead: `0.199s`
- Input tokens: `14,740`
- Output tokens: `3,328`
- Total tokens: `18,068`
- Reported API calls: `0`
- Output tokens/sec: `45.4`
- ms per output token: `22.0`
- Total tokens/sec: `246.2`

## Interpretation

- This benchmark is substantially more expensive than the under-specified TSP benchmark.
- It is better suited for testing multi-step exact reasoning and adaptive policy derivation rather than simple refusal behavior.
- Because the full terminal output was lost for this run, this note records the observed aggregate metrics so the result can still be referenced in later comparisons.
