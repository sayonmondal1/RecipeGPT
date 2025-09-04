import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
# Load your fine-tuned model and tokenizerQ
model_path = "./recipe_gpt2_foodcom"
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)
# Ensure model is on GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
def generate_recipe(ingredient_list, max_length=200):
    # Format input prompt
    prompt = f"Ingredients: {ingredient_list}\nRecipe:"
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    # Generate output
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.9,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )
    # Decode and return
    recipe = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return recipe
# Command line interaction
if __name__ == "__main__":
    print("\nSmart Recipe Generator")
    ingredients = input("Enter ingredients (comma-separated): ").strip()
    print("\nGenerating recipe...\n")
    recipe_output = generate_recipe(ingredients)
    print(recipe_output)