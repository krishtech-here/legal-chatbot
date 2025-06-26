import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

app = Flask(__name__)

# Keywords per category to check context relevance
category_keywords = {
    "vehicle": ["accident", "license", "insurance", "traffic", "hit and run", "driving"],
    "online": ["cyber", "online", "scam", "harassment", "social media"],
    "property": ["property", "land", "ownership", "dispute", "boundary", "real estate"],
    "family": ["divorce", "marriage", "child", "custody", "alimony", "domestic"],
    "criminal": ["murder", "theft", "crime", "criminal", "police", "jail"],
    "employment": ["job", "employee", "salary", "labour", "termination", "work"],
    "financial": ["loan", "bank", "cheque", "finance", "fraud", "debt"],
    "others": []
}

def is_question_relevant(category, question):
    if category == "others":
        return True
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in category_keywords.get(category, []))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/category/<category>")
def category_page(category):
    return render_template("chat.html", category=category)

@app.route("/ask/<category>", methods=["POST"])
def ask(category):
    question = request.form["question"]
    if not is_question_relevant(category, question):
        response = "⚠ This question doesn't match the selected category. Please choose the correct category for your issue."
    else:
        try:
            raw = model.generate_content(question)
            full_response = raw.text.strip()
            # Brief, clear, but still informative response limit
            sentences = full_response.split(". ")
            response = ". ".join(sentences[:4]).strip()  # First 4 sentences max
            if not response.endswith("."):
                response += "."
        except Exception as e:
            response = f"⚠ Error: {str(e)}"
    return render_template("chat.html", category=category, response=response, question=question)

if __name__ == "__main__":
    app.run(debug=True)
