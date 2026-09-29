import os
import time
import markdown
from flask import Flask, render_template, request, session, redirect
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "pocketsmartai-secret-123")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]

SYSTEM_PROMPT = "You are PocketSmartAI. If the user writes in Tamil or Tanglish, reply in simple Tamil. Otherwise reply in the user's language. Keep answers clear and short."

def ask_ai(question):
    last_error = ""
    for model in MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=SYSTEM_PROMPT + "\n\nUser: " + question,
                )
                return response.text
            except Exception as e:
                last_error = str(e)
                time.sleep(2)
    return "Sorry, AI ippo busy. Konjam neram kazhichu try pannunga.\n\n" + last_error
def fix_lists(text):
    lines = text.split("\n")
    result = []
    for i, line in enumerate(lines):
        is_item = line.strip().startswith(("* ", "- "))
        prev_is_item = i > 0 and lines[i - 1].strip().startswith(("* ", "- "))
        if is_item and i > 0 and not prev_is_item and lines[i - 1].strip() != "":
            result.append("")
        result.append(line)
    return "\n".join(result)
@app.route("/", methods=["GET", "POST"])
def home():
    if "history" not in session:
        session["history"] = []
    if request.method == "POST":
        question = request.form["question"]
        answer = ask_ai(question)
        history = session["history"]
        history.append({"q": question, "a": answer})
        session["history"] = history
        return redirect("/")
    rendered = [
        {"q": h["q"], "a": markdown.markdown(fix_lists(h["a"]), extensions=["nl2br"])}
        for h in session["history"]
    ]
    return render_template("index.html", history=rendered)
    

@app.route("/clear")
def clear():
    session["history"] = []
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)