import subprocess

def get_LLM_output(task, context, user_input):
    model_name = "hwan99/llama3ko-8b-qualcomm-lora_merged"

    if task == "GuideLine":
        system_prompt = "[TASK=GUIDELINE]\\n지금은 비상 재난 상황이야. 아래 user가 제공한 상황(question)에 대해, context를 참고하여 가이드라인을 생성해줘. 답변은 500자 이내로 작성해줘.\\n\\n(숫자 뒤에는 간결한 문장. 불필요한 설명·서론 금지)"
    elif task == "QA":
        system_prompt = "[TASK=QA]\\n지금은 비상 재난 상황이야. 아래 user가 제공한 상황(question)에 대해, Context에 근거해 사실만 답해줘. 답변은 한 문장, 150자 이내로 간결히 작성해줘. (추정·불필요한 서론 금지, 단위/수치 그대로 유지)"
    elif task == "caseSearch":
        system_prompt = "친절한 챗봇으로서 상대방의 요청에 최대한 자세하고 친절하게 답하자. 모든 대답은 한국어(Korean)으로 대답해줘."
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
    command = f'./genie-t2t-run.exe -c genie_config.json -p "{escaped_prompt}"'

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
