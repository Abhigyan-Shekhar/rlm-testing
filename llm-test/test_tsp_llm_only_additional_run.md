Captured visible terminal output provided by the user for:

```bash
python3 test_tsp_llm_only.py
```

Note: the pasted capture starts mid-answer rather than at the top of the baseline response.

Observed baseline behavior:

- The model hallucinated a full branch-and-bound solution despite the prompt not containing a distance matrix.
- It invented a detailed lower-bound formulation, pruning trace, and complete tour.
- It claimed:
  - optimal tour: `A -> B -> C -> D -> E -> G -> H -> F -> A`
  - optimal cost: `74`

Visible terminal metrics from the captured run:

- baseline wall time: `97.364s`
- model: `gemini-2.5-flash`
- input tokens: `190`
- output tokens: `6,171`
- calls: `1`
