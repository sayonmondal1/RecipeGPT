import pandas as pd
import torch
import ast
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments
# Load and preprocess the dataset
df = pd.read_csv("./dataset/recipes.csv")
def format_data(row):
    try:
        ingredients = ast.literal_eval(row["RecipeIngredientParts"]) if isinstance(row["RecipeIngredientParts"], str) else []
        instructions = row["RecipeInstructions"] if isinstance(row["RecipeInstructions"], str) else ""
        prompt = f"Ingredients: {', '.join(ingredients)}\nRecipe:"
        return f"{prompt} {instructions}"
    except Exception as e:
        return ""
# Apply formatting
data = df.apply(format_data, axis=1)
data = data[data.str.strip().astype(bool)]  # Remove empty strings
# Save formatted data to a text file
with open("formatted_recipes.txt", "w", encoding="utf-8") as f:
    for line in data:
        f.write(line.strip() + "\n")
# Load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token  # Set pad token
model = GPT2LMHeadModel.from_pretrained("gpt2")
# Create dataset
dataset = TextDataset(
    tokenizer=tokenizer,
    file_path="formatted_recipes.txt",
    block_size=128
)
# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False
)
# Training arguments
training_args = TrainingArguments(
    output_dir="./recipe_gpt2_foodcom",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    save_steps=500,
    save_total_limit=2,
    prediction_loss_only=True,
    logging_steps=10
)
# Check if GPU is available
if torch.cuda.is_available():
    print("GPU is available. Training will use GPU.")
else:
    print("GPU not available. Training will use CPU.")
# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
)
# Train model
trainer.train()
# Save model and tokenizer
trainer.save_model("./recipe_gpt2_foodcom")
tokenizer.save_pretrained("./recipe_gpt2_foodcom")


