cat > test_llm.py << 'EOF'
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ─── Setup ─────────────────────────────────────────────
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# ─── Context + Question (same as RLM) ──────────────────
context = """
The Battle of the Bastards was fought between Jon Snow and Ramsay Bolton for control 
of Winterfell. Jon's army included the Free Folk led by Tormund Giantsbane, soldiers 
from House Mormont, and the giant Wun Wun. Before the battle, Sansa Stark warned Jon 
that Ramsay would manipulate him, but Jon ignored her. Sansa secretly sent a raven to 
Petyr Baelish requesting the Knights of the Vale.

During battle, Ramsay killed Rickon Stark, causing Jon to abandon his battle plan and 
charge alone. The Bolton shield wall encircled Jon's forces. Tormund fought ferociously 
and Wun Wun smashed through soldiers, but defeat was imminent.

At the last moment, the Knights of the Vale arrived — called by Sansa Stark. The Vale 
cavalry routed the Boltons. Without Sansa's decision to contact Littlefinger, Jon's 
entire army would have been massacred. Her action was the single most decisive factor.
"""

question = "Who was the central ally of the main character in the Battle of the Bastards?"

prompt = f"""{context}

QUESTION: {question}
Identify the main character and their most decisive ally. Give a short answer.
"""

# ─── Cooldown (same as before) ─────────────────────────
print("⏳ Waiting 15 seconds for rate limit to cool down...")
time.sleep(15)

# ─── Run & Measure ─────────────────────────────────────
start = time.perf_counter()
response = model.generate_content(prompt)
end = time.perf_counter()

total_time = end - start

# ─── Extract tokens safely ─────────────────────────────
input_tokens = None
output_tokens = None

if hasattr(response, "usage_metadata") and response.usage_metadata:
    input_tokens = getattr(response.usage_metadata, "prompt_token_count", None)
    output_tokens = getattr(response.usage_metadata, "candidates_token_count", None)

# ─── Results ───────────────────────────────────────────
print("\n" + "=" * 70)
print("🎬 ANSWER")
print("=" * 70)
print(response.text)

# ─── Latency ───────────────────────────────────────────
print("\n" + "=" * 70)
print("⏱️  LATENCY")
print("=" * 70)
print(f"  Total time:        {total_time:.3f}s")

# ─── Token Usage ───────────────────────────────────────
print("\n" + "=" * 70)
print("📊 TOKEN USAGE")
print("=" * 70)

if input_tokens is not None and output_tokens is not None:
    print(f"  Input tokens:   {input_tokens:,}")
    print(f"  Output tokens:  {output_tokens:,}")
    print(f"  Total tokens:   {input_tokens + output_tokens:,}")

    # Throughput
    if output_tokens > 0:
        print(f"\n  ⚡ Tokens/sec (output):  {output_tokens / total_time:.1f} tok/s")
        print(f"  ⚡ ms/token (output):    {(total_time / output_tokens) * 1000:.1f} ms/tok")
else:
    print("  Token usage not available.")

print("=" * 70)
EOF
