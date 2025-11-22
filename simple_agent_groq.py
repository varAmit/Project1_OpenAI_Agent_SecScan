from groq import Groq
import os

# Load key (either from environment or directly)
api_key = os.getenv("My", "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")
client = Groq(api_key=api_key)

print("🤖 Groq Cloud Agent using Llama3-70B-8192\n")

# Initialize conversation history
history = [
    {"role": "system", "content": "You are a helpful and concise AI assistant."}
]

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Agent: Goodbye 👋")
        break

    # Add user's message to history
    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
    )

    # Extract and print the assistant's reply
    answer = response.choices[0].message.content
    print("Agent:", answer, "\n")

    # Add assistant reply back to history for context
    history.append({"role": "assistant", "content": answer})
    #print(history)