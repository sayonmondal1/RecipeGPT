from flask import Flask, request, jsonify, render_template, Response
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import time
app = Flask(__name__)
# Load model
model_path = "./recipe_gpt2_foodcom"
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)
model.eval()
# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
def format_steps(text):
    """
    Convert raw recipe text into step-by-step format.
    """
    sentences = [
        s.strip()
        for s in text.replace("\n", ". ").split(".")
        if s.strip() and len(s.strip()) > 3
    ]
    steps = [f"Step {i+1}: {sentence}" for i, sentence in enumerate(sentences)]
    return "\n".join(steps)
def generate_recipe_stream(ingredients, max_length=200):
    """
    Generate recipe and yield step-by-step for streaming.
    """
    prompt = f"Ingredients: {ingredients}\nRecipe Instructions:"
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            top_k=50,
            top_p=0.95,
            temperature=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    raw_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    recipe_text = raw_text.split("Recipe Instructions:")[-1].strip()
    step_text = format_steps(recipe_text)
    for line in step_text.split("\n"):
        yield f"data: {line} \n\n"
        time.sleep(0.3)
# ---------- ROUTES ----------
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")
@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")
@app.route("/generator", methods=["GET"])
def generator():
    return render_template("index1.html")
@app.route("/stream")
def stream():
    ingredients = request.args.get("ingredients", "")
    return Response(generate_recipe_stream(ingredients), mimetype="text/event-stream")
if __name__ == "__main__":
    app.run(debug=True)