import os
import PyPDF2
from groq import Groq

# --- CONFIG ---
PDF_FOLDER = r"C:\Users\amitv\OneDrive\Documents\RAG_doc"   
MODEL_NAME = "llama-3.3-70b-versatile"

# --- LOAD GROQ API KEY ---
#api_key = os.getenv("GROQ_API_KEY", "gsk_your_api_key_here")
api_key = os.getenv("myAgent", "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")
client = Groq(api_key=api_key)

# --- READ PDF FILES ---
def extract_text_from_pdfs(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
    return all_text

print("📚 Reading PDF files...")
pdf_text = extract_text_from_pdfs(PDF_FOLDER)
print(f"✅ Loaded {len(pdf_text)} characters of text from PDFs.\n")

# --- Q&A LOOP ---
print("🤖 Groq PDF Q&A Agent Ready (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Agent: Goodbye 👋")
        break

    # Build prompt
    prompt = f"""
You are an assistant. Use the following PDF content to answer the user's question.
If the answer is not found, say 'I could not find that in the PDF.'.

PDF content:
{pdf_text[:150000]}   # limit context to 15k chars for performance

Question: {user_input}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful PDF assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    print("Agent:", response.choices[0].message.content, "\n")
