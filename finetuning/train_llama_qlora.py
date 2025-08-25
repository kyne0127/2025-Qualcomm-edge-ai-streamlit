import os, json
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

MODEL_NAME = "beomi/Llama-3-Open-Ko-8B-Instruct-preview"
OUT_DIR    = "llama3ko_8b_instr_qa_guide_lora"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def main():
    #Quantization config (QLoRA: 4-bit)
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True
    )
    
    #Load tokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    #Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model.config.use_cache = False

    #Prepare model for k-bit training (enables gradient checkpointing, etc.)
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=True
    )
    
    #LoRA config(targeting key projection modules)
    TARGETS = ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]
    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=TARGETS,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_cfg)

    #Load dataset
    data_files = {
        "train": os.path.join(DATA_DIR, "train.jsonl"),
        "validation": os.path.join(DATA_DIR, "val.jsonl"),
    }
    ds = load_dataset("json", data_files=data_files)
    train_ds = ds["train"]
    val_ds   = ds["validation"]

    print(f"Train size: {len(train_ds)}, Val size: {len(val_ds)}")
    print("DATA_DIR:", DATA_DIR)

    #Data formatting function
    def formatting(examples):
        texts = []
        for msgs, resp in zip(examples["messages"], examples["response"]):
            prompt = tok.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True
            )
            texts.append(prompt + resp)
        return texts

    #SFT training configuration
    sft_cfg = SFTConfig(
        output_dir=OUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        save_strategy="steps",
        save_steps=100,
        eval_strategy="steps",
        eval_steps=50,
        bf16=True,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tok,            
        train_dataset=train_ds,
        eval_dataset=val_ds,
        args=sft_cfg,
        formatting_func=formatting,
        max_seq_length=4096,      
        packing=False             
    )

    #Train and save
    trainer.train()
    trainer.save_model()
    tok.save_pretrained(OUT_DIR)
    print(f"Saved LoRA adapter to: {OUT_DIR}")

if __name__ == "__main__":
    main()