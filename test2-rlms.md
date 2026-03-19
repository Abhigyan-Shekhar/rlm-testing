```bash

The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
Abhigyans-MacBook-Air:RLM-FULL abhigyanshekhar$ cat > test_got.py << 'EOF'
> import os
> import time
> from dotenv import load_dotenv
> from rlm import RLM
> from rlm.logger import RLMLogger
> 
> load_dotenv()
> 
> context = """
> The Battle of the Bastards was fought between Jon Snow and Ramsay Bolton for control 
> of Winterfell. Jon's army included the Free Folk led by Tormund Giantsbane, soldiers 
> from House Mormont, and the giant Wun Wun. Before the battle, Sansa Stark warned Jon 
> that Ramsay would manipulate him, but Jon ignored her. Sansa secretly sent a raven to 
> Petyr Baelish requesting the Knights of the Vale.
> 
> During battle, Ramsay killed Rickon Stark, causing Jon to abandon his battle plan and 
> charge alone. The Bolton shield wall encircled Jon's forces. Tormund fought ferociously 
> and Wun Wun smashed through soldiers, but defeat was imminent.
> 
> At the last moment, the Knights of the Vale arrived — called by Sansa Stark. The Vale 
> cavalry routed the Boltons. Without Sansa's decision to contact Littlefinger, Jon's 
> entire army would have been massacred. Her action was the single most decisive factor.
> """
> 
> question = "Who was the central ally of the main character in the Battle of the Bastards?"
> 
> prompt = f"""{context}
> 
> QUESTION: {question}
> Identify the main character and their most decisive ally. Give a short answer.
> Do NOT use llm_query. Just analyze the context variable directly with Python code.
> """
> 
> print("⏳ Waiting 15 seconds for rate limit to cool down...")
> time.sleep(15)
> 
> logger = RLMLogger()
> 
> agent = RLM(
>     backend="gemini",
>     backend_kwargs={
>         "api_key": os.environ["GEMINI_API_KEY"],
>         "model_name": "gemini-2.5-flash-lite",
>     },
>     environment="local",
>     max_depth=1,
>     max_iterations=3,
>     verbose=True,
>     logger=logger,
> )
> 
> # ─── Run & Measure ─────────────────────────────────────
> wall_start = time.perf_counter()
> result = agent.completion(prompt)
> wall_end = time.perf_counter()
> 
> # ─── Results ───────────────────────────────────────────
> print("\n" + "=" * 70)
> print("🎬 ANSWER")
> print("=" * 70)
> print(result.response)
> 
> # ─── Latency Breakdown ────────────────────────────────
> print("\n" + "=" * 70)
> print("⏱️  LATENCY BREAKDOWN")
> print("=" * 70)
> print(f"  Total wall time:        {wall_end - wall_start:.3f}s")
> print(f"  RLM execution time:     {result.execution_time:.3f}s")
> 
> # Per-iteration latency from logger
> trajectory = logger.get_trajectory()
> if trajectory:
>     total_llm_time = 0.0
>     total_code_time = 0.0
> 
>     for i, iteration in enumerate(trajectory):
>         iter_time = iteration.get("iteration_time", 0.0)
>         print(f"\n  ── Iteration {i + 1} ({'%.3f' % iter_time}s total)")
> 
>         # Code block execution times
>         for j, block in enumerate(iteration.get("code_blocks", [])):
>             code_time = block.get("result", {}).get("execution_time", 0.0)
>             total_code_time += code_time
>             code_preview = block.get("code", "")[:60].replace("\n", " ")
>             print(f"     Code block {j + 1}:  {code_time:.3f}s  │ {code_preview}...")
> 
>         # LLM time = iteration time - code execution time
>         code_in_iter = sum(
>             b.get("result", {}).get("execution_time", 0.0)
>             for b in iteration.get("code_blocks", [])
>         )
>         llm_time = iter_time - code_in_iter
>         total_llm_time += llm_time
>         print(f"     LLM thinking:  {llm_time:.3f}s")
> 
>     print(f"\n  ── Totals ──────────────────────")
>     print(f"     Total LLM time:      {total_llm_time:.3f}s")
>     print(f"     Total code exec:     {total_code_time:.3f}s")
>     print(f"     Iterations:          {len(trajectory)}")
>     print(f"     Avg per iteration:   {result.execution_time / len(trajectory):.3f}s")
> 
> # ─── Token Usage ───────────────────────────────────────
> print("\n" + "=" * 70)
> print("📊 TOKEN USAGE")
> print("=" * 70)
> if result.usage_summary:
>     usage = result.usage_summary.to_dict()
>     for model_name, model_usage in usage.get("model_usage_summaries", {}).items():
>         print(f"  Model: {model_name}")
>         print(f"    Input tokens:   {model_usage.get('total_input_tokens', 0):,}")
>         print(f"    Output tokens:  {model_usage.get('total_output_tokens', 0):,}")
>         print(f"    Total tokens:   {model_usage.get('total_input_tokens', 0) + model_usage.get('total_output_tokens', 0):,}")
>         print(f"    API calls:      {model_usage.get('num_calls', 0)}")
>         cost = model_usage.get('total_cost')
>         if cost:
>             print(f"    Cost:           ${cost:.6f}")
> 
>     # Latency per token
>     total_out = sum(
>         m.get("total_output_tokens", 0)
>         for m in usage.get("model_usage_summaries", {}).values()
>     )
>     if total_out > 0:
>         print(f"\n  ⚡ Tokens/sec (output):  {total_out / result.execution_time:.1f} tok/s")
>         print(f"  ⚡ ms/token (output):    {(result.execution_time / total_out) * 1000:.1f} ms/tok")
> 
> print("=" * 70)
> EOF
Abhigyans-MacBook-Air:RLM-FULL abhigyanshekhar$ uv run python test_got.py
⏳ Waiting 15 seconds for rate limit to cool down...

╭─ ◆ RLM ━ Recursive Language Model ───────────────────────────────────────────────────────────╮
│                                                                                              │
│    Backend                  gemini                         Environment             local     │
│    Model                    gemini-2.5-flash-lite          Max Iterations          3         │
│    Max Depth                1                                                                │
│                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯

────────────────────────────────────────  Iteration 1  ─────────────────────────────────────────
╭─ ◇ LLM Response  (1.70s) ────────────────────────────────────────────────────────────────────╮
│ The user wants me to analyze the provided context and answer a prompt. The context is a      │
│ single string of 1148 characters. I need to examine the context and then formulate an        │
│ answer. Since there's only one chunk, I can directly query an LLM on the entire context.     │
│                                                                                              │
│ First, I will print the context to see what it contains. Then, I will formulate a prompt to  │
│ ask an LLM to answer the (currently unknown) prompt based on this context. Since I don't     │
│ know the prompt yet, I'll have to make a placeholder. However, the current instruction is    │
│ just to "look through and figure out how to answer the prompt," so I should first inspect    │
│ the context.                                                                                 │
│                                                                                              │
│ ```repl                                                                                      │
│ print(context)                                                                               │
│ ```                                                                                          │
│                                                                                              │
│ ~119 words                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ ▸ Code Execution  (0.000s) ─────────────────────────────────────────────────────────────────╮
│ Code:                                                                                        │
│ print(context)                                                                               │
│                                                                                              │
│ Output:                                                                                      │
│                                                                                              │
│ The Battle of the Bastards was fought between Jon Snow and Ramsay Bolton for control         │
│ of Winterfell. Jon's army included the Free Folk led by Tormund Giantsbane, soldiers         │
│ from House Mormont, and the giant Wun Wun. Before the battle, Sansa Stark warned Jon         │
│ that Ramsay would manipulate him, but Jon ignored her. Sansa secretly sent a raven to        │
│ Petyr Baelish requesting the Knights of the Vale.                                            │
│                                                                                              │
│ During battle, Ramsay killed Rickon Stark, causing Jon to abandon his battle plan and        │
│ charge alone. The Bolton shield wall encircled Jon's forces. Tormund fought ferociously      │
│ and Wun Wun smashed through soldiers, but defeat was imminent.                               │
│                                                                                              │
│ At the last moment, the Knights of the Vale arrived — called by Sansa Stark. The Vale        │
│ cavalry routed the Boltons. Without Sansa's decision to contact Littlefinger, Jon's          │
│ entire army would have been massacred. Her action was the single most decisive factor.       │
│                                                                                              │
│                                                                                              │
│ QUESTION: Who was the central ally of the main character in the Battle of the Bastards?      │
│ Identify the main character and their most decisive ally. Give a short answer.               │
│ Do NOT use llm_query. Just analyze the context variable directly with Python code.           │
│                                                                                              │
│                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────  Iteration 2  ─────────────────────────────────────────
╭─ ◇ LLM Response  (2.28s) ────────────────────────────────────────────────────────────────────╮
│ The user has provided a question and the context. I need to identify the main character and  │
│ their most decisive ally in the Battle of the Bastards based *only* on the provided text,    │
│ and *without* using `llm_query`.                                                             │
│                                                                                              │
│ From the text:                                                                               │
│ - Main character: Jon Snow is clearly a central figure, as the battle is fought for control  │
│ of Winterfell and his army is described.                                                     │
│ - Allies of Jon: Free Folk (Tormund Giantsbane), House Mormont, Wun Wun.                     │
│ - Sansa Stark: She warned Jon, and secretly sent a raven to Petyr Baelish requesting the     │
│ Knights of the Vale.                                                                         │
│ - Knights of the Vale: Arrived at the last moment due to Sansa's action.                     │
│ - Decisive factor: "Without Sansa's decision to contact Littlefinger, Jon's entire army      │
│ would have been massacred. Her action was the single most decisive factor."                  │
│                                                                                              │
│ Therefore, Jon Snow is the main character, and Sansa Stark's action was the most decisive    │
│ factor, making her his most decisive ally in this context.                                   │
│                                                                                              │
│ I will now formulate the answer based on this analysis.                                      │
│ Final Answer: Jon Snow was the main character. His most decisive ally was Sansa Stark, whose │
│ decision to contact Littlefinger for the Knights of the Vale was the single most decisive    │
│ factor in the battle.                                                                        │
│                                                                                              │
│ ~204 words                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────  Iteration 3  ─────────────────────────────────────────
╭─ ◇ LLM Response  (2.33s) ────────────────────────────────────────────────────────────────────╮
│ The user is reminding me to use the REPL environment and sub-LLMs to answer the prompt,      │
│ based on the `context` variable. The previous interaction already provided the context and   │
│ the question, and I analyzed it directly without using `llm_query`.                          │
│                                                                                              │
│ The question is: "Who was the central ally of the main character in the Battle of the        │
│ Bastards? Identify the main character and their most decisive ally. Give a short answer. Do  │
│ NOT use llm_query. Just analyze the context variable directly with Python code."             │
│                                                                                              │
│ I have already performed the analysis in my previous response. The context clearly states    │
│ that Jon Snow is a central figure, and that Sansa Stark's actions (contacting Littlefinger   │
│ for the Knights of the Vale) were the "single most decisive factor." This implies she was    │
│ his most decisive ally, even though the Knights of the Vale were the ones who physically     │
│ arrived. Sansa's decision initiated their arrival.                                           │
│                                                                                              │
│ Since the instruction was "Do NOT use llm_query. Just analyze the context variable directly  │
│ with Python code," and I have already done that analysis and formulated an answer, I should  │
│ now provide that answer. I don't need to use the REPL again for analysis as I've already     │
│ extracted the necessary information.                                                         │
│                                                                                              │
│ Therefore, my next action is to present the final answer.                                    │
│                                                                                              │
│ The main character in the Battle of the Bastards was Jon Snow. His most decisive ally was    │
│ Sansa Stark, as her secret communication with Littlefinger to summon the Knights of the Vale │
│ was the most critical factor in preventing the massacre of Jon's army.                       │
│                                                                                              │
│ ~254 words                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯

╭─ ★ Final Answer ─────────────────────────────────────────────────────────────────────────────╮
│                                                                                              │
│                                                                                              │
│  Your question was: "Who was the central ally of the main character in the Battle of the     │
│  Bastards? Identify the main character and their most decisive ally. Give a short answer.    │
│  Do NOT use llm_query. Just analyze the context variable directly with Python code."         │
│                                                                                              │
│  Based on the context:                                                                       │
│  The main character is Jon Snow.                                                             │
│  His most decisive ally was Sansa Stark, whose secret communication to Petyr Baelish to      │
│  request the Knights of the Vale was the single most decisive factor in the battle, saving   │
│  Jon's army from being massacred.                                                            │
│                                                                                              │
│  FINAL(Jon Snow was the main character. His most decisive ally was Sansa Stark, whose        │
│  decision to contact Littlefinger for the Knights of the Vale was the single most decisive   │
│  factor in the battle.)                                                                      │
│                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯


════════════════════════════════════════════════════════════════════════════════════════════════
                                    Iterations       3                                          
                                    Total Time       6.82s                                      
                                    Input Tokens     13,276                                     
                                    Output Tokens    920                                        
════════════════════════════════════════════════════════════════════════════════════════════════


======================================================================
🎬 ANSWER
======================================================================

Your question was: "Who was the central ally of the main character in the Battle of the Bastards? Identify the main character and their most decisive ally. Give a short answer. Do NOT use llm_query. Just analyze the context variable directly with Python code."

Based on the context:
The main character is Jon Snow.
His most decisive ally was Sansa Stark, whose secret communication to Petyr Baelish to request the Knights of the Vale was the single most decisive factor in the battle, saving Jon's army from being massacred.

FINAL(Jon Snow was the main character. His most decisive ally was Sansa Stark, whose decision to contact Littlefinger for the Knights of the Vale was the single most decisive factor in the battle.)

======================================================================
⏱️  LATENCY BREAKDOWN
======================================================================
  Total wall time:        9.014s
  RLM execution time:     6.818s
Traceback (most recent call last):
  File "/Users/abhigyanshekhar/Desktop/RLM-FULL/test_got.py", line 77, in <module>
    iter_time = iteration.get("iteration_time", 0.0)
                ^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'
Abhigyans-MacBook-Air:RLM-FULL abhigyanshekhar$ 
