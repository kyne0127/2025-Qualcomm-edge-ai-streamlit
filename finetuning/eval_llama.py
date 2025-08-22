# eval_all_llama.py
import os, json, torch, re
from typing import List, Dict, Any
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from tqdm import tqdm

# ===== 경로/설정 =====
MODEL_NAME  = "beomi/Llama-3-Open-Ko-8B-Instruct-preview"
ADAPTER_DIR = "/home/a2024712006/qualcomm/fine_tuning/llama3ko_8b_instr_qa_guide_lora"
EVAL_PATH   = "/home/a2024712006/qualcomm/fine_tuning/data/eval.jsonl"
OUT_PATH    = "/home/a2024712006/qualcomm/fine_tuning/eval_outputs_llama.jsonl" 

BATCH_SIZE  = 1     
SEED        = 42
def detect_task(messages: List[Dict[str, str]]) -> str:
    for m in messages:
        if m.get("role") == "system":
            c = (m.get("content") or "").upper()
            if "[TASK=GUIDELINE]" in c:
                return "GUIDELINE"
            if "[TASK=QA]" in c:
                return "QA"
    return "UNKNOWN"

def main():
    torch.manual_seed(SEED)

    tok = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    base.config.use_cache = True

    if not os.path.isdir(ADAPTER_DIR):
        raise FileNotFoundError(f"LoRA 어댑터 디렉터리 없음: {ADAPTER_DIR}")
    model = PeftModel.from_pretrained(base, ADAPTER_DIR)
    model.eval()

    eot_id = tok.convert_tokens_to_ids("<|eot_id|>")
    eos_id = tok.eos_token_id

    ds = load_dataset("json", data_files={"eval": EVAL_PATH})["eval"]
    print(f"Loaded eval set: {len(ds)} samples")

    n = len(ds)
    with open(OUT_PATH, "w", encoding="utf-8") as fout:
        for ex in tqdm(ds, total=n, desc="Infer"):
            messages = ex.get("messages", None)
            if not messages:
                raise ValueError("Sample has no 'messages' field. Please align dataset format.")

            task = detect_task(messages)
            max_new = 220 if task == "GUIDELINE" else 140

            prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tok(prompt, return_tensors="pt").to(model.device)

            with torch.inference_mode():
                gen_ids = model.generate(
                    **inputs,
                    max_new_tokens=max_new,
                    do_sample=False,     
                    top_p=1.0,
                    eos_token_id=[eos_id, eot_id],
                    pad_token_id=tok.eos_token_id,
                )

            prompt_len = inputs["input_ids"].shape[-1]
            out_text = tok.decode(gen_ids[0][prompt_len:], skip_special_tokens=True).strip()
            if task == "GUIDELINE":
                out_text = out_text.split("\n")[:-1]
                out_text = "\n".join(out_text).strip()
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
