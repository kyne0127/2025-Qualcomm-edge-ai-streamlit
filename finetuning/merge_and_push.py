# merge_and_push.py
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login

BASE_MODEL  = "meta-llama/Llama-3.2-3B-Instruct"

ADAPTER_DIR = "fine_tuning/llama3_3b_instr_lora"
REPO_ID     = "hwan99/llama3ko-3b-qualcomm-lora_merged_v1"

def main():
    #Authenticate with Hugging Face Hub
    login(token="your_token")

    #Load tokenizer
    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token 

    #Load base model
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    base.config.use_cache = True
    
    #Load LoRA adapter and merge into base model
    model = PeftModel.from_pretrained(base, ADAPTER_DIR)
    model = model.merge_and_unload()     
    model.to(torch.bfloat16)                   

    #Push merged model + tokenizer to Hugging Face Hub
    print(f"[PUSH] Uploading to Hub: {REPO_ID}")
    model.push_to_hub(REPO_ID)
    tok.push_to_hub(REPO_ID)
    print("[DONE] Pushed to Hugging Face Hub")

if __name__ == "__main__":
    main()
