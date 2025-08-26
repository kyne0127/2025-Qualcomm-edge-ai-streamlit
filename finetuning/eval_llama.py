# eval_all_llama.py
import os, json, torch, re
from typing import List, Dict, Any
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from tqdm import tqdm

# ===== Paths / Settings =====
MODEL_NAME  = "hwan99/llama3ko-3b-qualcomm-lora_merged_v1"
EVAL_PATH   = "/home/a2024712006/qualcomm/fine_tuning/data/eval_en.jsonl"
OUT_PATH    = "/home/a2024712006/qualcomm/fine_tuning/eval_outputs_en_llama_fine_tune.jsonl"  # Save path for results

BATCH_SIZE  = 1         # Safer to generate one at a time
SEED        = 42

def main():
    torch.manual_seed(SEED)

    # ===== Tokenizer =====
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # ===== Load Model =====
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model.config.use_cache = True
    model.eval()

    # ===== End-of-Text Stop Tokens =====
    eot_id = tok.convert_tokens_to_ids("<|eot_id|>")
    eos_id = tok.eos_token_id

    # ===== Load Evaluation Data =====
    # eval_dataset.jsonl is assumed to have {"messages":[...], "response": "..."} format 
    # ("response" may or may not exist)
    ds = load_dataset("json", data_files={"eval": EVAL_PATH})["eval"]
    print(f"Loaded eval set: {len(ds)} samples")

    # ===== Run Inference on All Samples and Save =====
    n = len(ds)
    with open(OUT_PATH, "w", encoding="utf-8") as fout:
        for ex in tqdm(ds, total=n, desc="Infer"):
            messages = ex.get("messages", None)
            if not messages:
                raise ValueError("Sample has no 'messages' field. Please align dataset format.")

            # Build prompt
            prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tok(prompt, return_tensors="pt").to(model.device)

            with torch.inference_mode():
                gen_ids = model.generate(
                    **inputs,
                    max_new_tokens=220,
                    do_sample=False,          # Deterministic output
                    top_p=1.0,
                    eos_token_id=[eos_id, eot_id],
                    pad_token_id=tok.eos_token_id,
                )

            # Decode excluding the prompt
            prompt_len = inputs["input_ids"].shape[-1]
            out_text = tok.decode(gen_ids[0][prompt_len:], skip_special_tokens=True).strip()
            out = {
                "messages": messages,
                "prediction": out_text,
            }
            if "response" in ex and ex["response"] is not None:
                out["reference"] = ex["response"]

            fout.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"[DONE] Saved predictions to: {OUT_PATH}")

if __name__ == "__main__":
    main()
