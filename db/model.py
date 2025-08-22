# eval_one_qwen.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
# import pdb

def get_LLM_output(task, context, user_input):
    model_name = "hwan99/llama3ko-8b-qualcomm-lora_merged"
    
    if task == "GuideLine":
        system_prompt = "[TASK=GUIDELINE]\n지금은 비상 재난 상황이야. 아래 user가 제공한 상황(question)에 대해, context를 참고하여 가이드라인을 생성해줘. 답변은 500자 이내로 작성해줘.\n\n(숫자 뒤에는 간결한 문장. 불필요한 설명·서론 금지)"
    elif task == "QA":
        system_prompt = "[TASK=QA]\n지금은 비상 재난 상황이야. 아래 user가 제공한 상황(question)에 대해, Context에 근거해 사실만 답해줘. 답변은 한 문장, 150자 이내로 간결히 작성해줘. (추정·불필요한 서론 금지, 단위/수치 그대로 유지)"
    elif task == "caseSearch":
        # caseSearch는 fine-tuning 안함
        model_name = "beomi/Llama-3-Open-Ko-8B-Instruct-preview"
        system_prompt = "친절한 챗봇으로서 상대방의 요청에 최대한 자세하고 친절하게 답하자. 모든 대답은 한국어(Korean)으로 대답해줘."
    else: 
        raise ValueError("Invalid task. Choose either 'QA' or 'GuideLine' or 'caseSearch'")
        print("Invalid task. Choose either 'QA' or 'GuideLine' or 'caseSearch")
    
    print("set system prompt")
    if context == None: 
        model_name = "beomi/Llama-3-Open-Ko-8B-Instruct-preview"
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
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
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

    if task == "GuideLine":
        out_text = out_text.split("\n")[:-1]
        out_text = "\n".join(out_text).strip()
    
    return out_text
