import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)
import os

def main():
    model_name = "microsoft/DialoGPT-small"
    
    print("Loading tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Create a simple text file from our training data
    with open('training_data.jsonl', 'r') as f_in, open('training_text.txt', 'w') as f_out:
        for line in f_in:
            data = eval(line)
            text = data['prompt'] + " " + data['completion'] + tokenizer.eos_token
            f_out.write(text + '\n')
    
    # Create dataset
    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path="training_text.txt",
        block_size=128
    )
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    training_args = TrainingArguments(
        output_dir="./vulnfix-ai-model",
        overwrite_output_dir=True,
        num_train_epochs=2,
        per_device_train_batch_size=2,
        save_steps=100,
        save_total_limit=1,
        logging_steps=10,
        learning_rate=5e-4,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Saving model...")
    trainer.save_model()
    
    print("Training completed!")

if __name__ == "__main__":
    main()
