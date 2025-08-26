import os, json
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig, get_peft_model
os.environ["TOKENIZERS_PARALLELISM"] = "false" #DDP set

MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
OUT_DIR    = "llama3_3b_instr_lora"
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")

def main():
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,       
        torch_dtype=torch.bfloat16,     
    )
    model.config.use_cache = False
    # model.gradient_checkpointing_enable()
    TARGETS = ["q_proj","k_proj","v_proj","o_proj"]
    lora_cfg = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=TARGETS,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_cfg)

    # 데이터 로드
    data_files = {
        "train": os.path.join(DATA_DIR, "train_en_all.jsonl"),
    }
    ds = load_dataset("json", data_files=data_files)
    train_ds = ds["train"]
    print(f"Train size: {len(train_ds)}")
    
    def formatting(examples):
        texts = []
        for msgs, resp in zip(examples["messages"], examples["response"]):
            prompt = tok.apply_chat_template(
                msgs, tokenize=False, add_generation_prompt=True
            )
            texts.append(prompt + resp)
        return texts

    sft_cfg = SFTConfig(
        output_dir=OUT_DIR,
        max_steps=200, # formatting 
        per_device_train_batch_size=1,
        gradient_accumulation_steps=2,
        learning_rate=1e-4,
        lr_scheduler_type="cosine",
        warmup_steps=20,
        logging_steps=10,
        save_strategy="steps",
        save_steps=100,
        bf16=True,
        fp16=False,
        dataloader_num_workers=4,
        optim="adamw_torch_fused",
        ddp_find_unused_parameters=False, # ddp
        report_to=[]
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tok,
        train_dataset=train_ds,
        args=sft_cfg,
        formatting_func=formatting,
        max_seq_length=4096,
        packing=False
    )

    trainer.train()
    trainer.save_model()
    tok.save_pretrained(OUT_DIR)
    print(f"Saved LoRA adapter to: {OUT_DIR}")

if __name__ == "__main__":
    main()

#Multi-gpu시, accelerate launch --num_processes [NUM_GPUS] --mixed_precision bf16 train_llama_lora_3b.py
