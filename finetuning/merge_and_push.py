# merge_and_push.py
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login

BASE_MODEL = "beomi/Llama-3-Open-Ko-8B-Instruct-preview"

ADAPTER_DIR = "/home/a2024712006/qualcomm/fine_tuning/llama3ko_8b_instr_qa_guide_lora" 
REPO_ID = "hwan99/llama3ko-8b-qualcomm-lora_merged"  

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
