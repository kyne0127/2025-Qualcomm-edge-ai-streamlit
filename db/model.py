import subprocess
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def get_LLM_output(task, context, user_input):
    model_name = "meta-llama/Llama-3.2-3B-Instruct"

    if task == "GuideLine":
        system_prompt = "[TASK=GUIDELINE]\\nThis is an emergency disaster situation. Generate guidelines based on the Context and the user's question. Keep the response under 500 characters. (Use concise sentences after numbers; avoid unnecessary explanations or introductions)."
    elif task == "QA":
        system_prompt = "[TASK=QA]\\nThis is an emergency disaster situation. Based on the Context provided, answer the user's question with facts only. Keep the response to one sentence under 300 characters, and be concise. (No speculation, unnecessary introductions; maintain original units/numbers)."
    elif task == "caseSearch":
        system_prompt = "The Input describes how an emergency response case was handled in the past similar emergency cases. Please summarize it in under 500 characters for readability. And if a line break seems necessary, please insert \n in the response. (Use concise sentences after numbers; avoid unnecessary explanations or introductions). "
    else:
        raise ValueError("Invalid task. Choose either 'QA' or 'GuideLine' or 'caseSearch'")

    print("set system prompt")
    
    # if context == None:
    #     pass

    # user_prompt = f"Context: {context}\\nInput: {user_input}"

    # if system_prompt:
    #     prompt_template = (
    #         "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\\n\\n"
    #         f"{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\n"
    #         f"{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    #     )
    # else:
    #     prompt_template = (
    #         "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\\n\\n"
    #         f"{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    #     )

    # escaped_prompt = prompt_template.replace('"', '`"').replace("'", "''")
    # command = f'../genie_bundle/genie-t2t-run.exe -c genie_config.json -p "{escaped_prompt}"' ##should change the path to genie_bundle

    # try:
    #     print("Executing PowerShell command...")
    #     print(f"Command: {command}")

    #     result = subprocess.run(
    #         ["powershell", "-Command", command],
    #         check=True,
    #         capture_output=True,
    #         text=True,
    #         encoding='cp949'
    #     )

    #     return result.stdout.strip()

    # except subprocess.CalledProcessError as e:
    #     print("Error executing genie-t2t-run.exe via PowerShell.")
    #     print(f"Standard Error: {e.stderr}")
    #     return f"Error: {e.stderr}"
    # except FileNotFoundError:
    #     print("powershell.exe 또는 genie-t2t-run.exe를 찾을 수 없습니다.")
    #     return "Error: Executable not found."
    
    if context == None: 
        model_name = "meta-llama/Llama-3.2-3B-Instruct"
        # 사용자 질문에 대해 무조건 vectorDB에 존재하는게 아님 
        # 이때, 어떻게 처리할 지 생각해야함 -> 유사도가 낮을 때, 현재 DB에는 없는 정보지만, 이런식으로 생각한다 같이 처리? 
        pass 

    model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    
    user_prompt = f"Context: {context}\nInput: {user_input}"
    messages = [
        {"role": "system", "content": system_prompt}, 
        {"role": "user", "content": user_prompt}]

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.inference_mode():
        eot_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")
        eos_id = tokenizer.eos_token_id

        gen_ids = model.generate(
            **inputs,
            max_new_tokens=220,
            do_sample=False,
            temperature=0.0,
            top_p=1.0,
            eos_token_id=[eos_id, eot_id],  
            pad_token_id=tokenizer.eos_token_id,
        )
    prompt_len = inputs["input_ids"].shape[-1]
    out_text = tokenizer.decode(gen_ids[0][prompt_len:], skip_special_tokens=True).strip()
    if task == "GUIDELINE":
        out_text = out_text.split("\n")[:-1]
        out_text = "\n".join(out_text).strip()
    
    return out_text