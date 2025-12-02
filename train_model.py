import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model
import json
from datasets import Dataset

def load_training_data():
    """Load our generated training data"""
    data = []
    with open('training_data.jsonl', 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    texts = []
    for item in data:
        text = item['prompt'] + "\n\n" + item['completion']
        texts.append(text)
    
    return texts

def main():
    model_name = "microsoft/DialoGPT-small"
    
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # FIXED: Use correct target modules for DialoGPT
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["c_attn", "c_proj"],  # Changed from ["q_proj", "v_proj"]
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    print("Applying LoRA...")
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    print("Loading training data...")
    texts = load_training_data()
    
    def tokenize_function(examples):
        # FIX: Return the tokenized outputs directly, not as strings
        tokenized = tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=256,
            return_tensors=None  # This returns Python lists, not tensors
        )
        return tokenized
    
    dataset = Dataset.from_dict({"text": texts})
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    training_args = TrainingArguments(
        output_dir="./vulnfix-ai-model",
        overwrite_output_dir=True,
        num_train_epochs=2,
        per_device_train_batch_size=2,
        save_steps=50,
        save_total_limit=1,
        logging_steps=10,
        learning_rate=1e-3,
        warmup_steps=10,
        report_to=None,
        remove_unused_columns=False
    )
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_dataset,
    )
    
    print("Starting training...")
    trainer.train()
    
    print("Saving model...")
    trainer.save_model()
    tokenizer.save_pretrained("./vulnfix-ai-model")
    
    print("Training completed!")

if __name__ == "__main__":
    main()
