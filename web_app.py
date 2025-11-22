import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("My", "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")
if not API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY")

client = Groq(api_key=API_KEY)
MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "You are a helpful, concise AI assistant."

app = FastAPI()
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Groq Agent</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; }
    #log { border: 1px solid #ddd; padding: 1rem; min-height: 300px; }
    .u { color: #333; }
    .a { color: #0a7; white-space: pre-wrap; }
    #msg { width: 80%; padding: .6rem; }
    button { padding: .6rem 1rem; }
  </style>
</head>
<body>
  <h2>🤖 Groq AI Agent</h2>
  <div id="log"></div>
  <p>
    <input id="msg" placeholder="Ask your question..." />
    <button id="send">Send</button>
    <button id="clear">Clear</button>
  </p>
  <script>
    const log = document.getElementById('log');
    const msg = document.getElementById('msg');
    const send = document.getElementById('send');
    const clearBtn = document.getElementById('clear');

    let history = [];

    function append(role, text) {
      const p = document.createElement('p');
      p.className = role === 'user' ? 'u' : 'a';
      p.textContent = (role === 'user' ? 'You: ' : 'Agent: ') + text;
      log.appendChild(p);
      log.scrollTop = log.scrollHeight;
    }

    async function ask() {
      const q = msg.value.trim();
      if (!q) return;
      append('user', q);
      msg.value = '';
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, history })
      });
      const data = await res.json();
      if (data.answer) {
        append('assistant', data.answer);
        history.push(['' + q, '' + data.answer]);
      } else {
        append('assistant', 'Error: ' + (data.error || 'unknown'));
      }
    }

    send.addEventListener('click', ask);
    msg.addEventListener('keydown', (e) => { if (e.key === 'Enter') ask(); });
    clearBtn.addEventListener('click', () => { history = []; log.innerHTML=''; });
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML

@app.post("/chat")
async def chat(payload: dict):
    question = payload.get("question", "")
    hist = payload.get("history", [])  # list of [user, assistant] pairs
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for u, a in hist:
        if u:
            messages.append({"role": "user", "content": u})
        if a:
            messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": question})

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        answer = resp.choices[0].message.content
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Groq AI Agent at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
