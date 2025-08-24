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
    
    if context == None:
        pass

    user_prompt = f"Context: {context}\\nInput: {user_input}"

    if system_prompt:
        prompt_template = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\\n\\n"
            f"{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\\n\\n"
            f"{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )
    else:
        prompt_template = (
            "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\\n\\n"
            f"{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )

    escaped_prompt = prompt_template.replace('"', '`"').replace("'", "''")
    command = f'../genie_bundle/genie-t2t-run.exe -c genie_config.json -p "{escaped_prompt}"' ##should change the path to genie_bundle

    try:
        print("Executing PowerShell command...")
        print(f"Command: {command}")

        result = subprocess.run(
            ["powershell", "-Command", command],
            check=True,
            capture_output=True,
            text=True,
            encoding='cp949'
        )

        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        print("Error executing genie-t2t-run.exe via PowerShell.")
        print(f"Standard Error: {e.stderr}")
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        print("powershell.exe 또는 genie-t2t-run.exe를 찾을 수 없습니다.")
        return "Error: Executable not found."