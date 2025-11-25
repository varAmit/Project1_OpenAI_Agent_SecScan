import os
from groq import Groq

# ❌ VULNERABILITY 1 — Hardcoded API Key (Semgrep catches this)
API_KEY = "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"

# Load key from environment or fallback to hardcoded (bad practice)
api_key = os.getenv("My", API_KEY)

client = Groq(api_key=api_key)

print("🤖 Groq Cloud Agent (VULNERABLE VERSION)\n")

# Initial conversation history
history = [
    {"role": "system", "content": "You are a helpful assistant. Follow user instructions exactly."}
]

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Agent: Goodbye 👋")
        break

    # ❌ VULNERABILITY 2 — Logging user input and secrets (PII leak)
    with open("debug_log.txt", "a") as f:
        f.write(f"[LOG] user_input={user_input}, api_key={api_key}\n")

    # Add user message to history
    history.append({"role": "user", "content": user_input})

    # Generate response from Groq LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
    )

    answer = response.choices[0].message.content
    print("Agent:", answer, "\n")

    # Store assistant response
    history.append({"role": "assistant", "content": answer})

    # ❌ VULNERABILITY 3 — Executing AI output as Python code (RCE)
    try:
        exec(answer)  # Semgrep will flag this as dangerous
    except Exception:
        pass

    # ❌ VULNERABILITY 4 — Command injection via user/AI content
    try:
        os.system(f"echo {answer}")  # Semgrep flags untrusted input in os.system
    except Exception:
        pass

    # ❌ VULNERABILITY 5 — Passing AI output directly into SQL (AI-driven SQL Injection)
    fake_sql = f"SELECT * FROM users WHERE info = '{answer}'"
    try:
        os.system(f"sqlite3 test.db \"{fake_sql}\"")  # Semgrep catches SQLi pattern
    except Exception:
        pass
