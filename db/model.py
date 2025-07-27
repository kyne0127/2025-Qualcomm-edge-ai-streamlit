import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-7B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
model.eval()
tokenizer = AutoTokenizer.from_pretrained(model_name)


def get_LLM_output(prompt):
    # global model, tokenizer

    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response



def get_QA_output(context, input_data):
    prompt = f"""
    지금은 비상 재난 상황이야. 아래 question에 있는 상황에 대해서, context를 참고하여 답변을 생성해줘.
    Context: {context}
    Question: {input_data}
    답변은 500자 이내로 간단하게 생성해줘.
    """

    response = get_LLM_output(prompt)
    return response


def get_guide_line_output(context, input_data):
    prompt = f"""    
    지금은 비상 재난 상황이야. 아래 question에 있는 상황에 대해서, context를 참고하여 가이드라인을 생성해줘.
    Context: {context}
    Input: {input_data}
    답변은 500자 이내로 간단하게 생성해줘.
    """

    response = get_LLM_output(prompt)
    return response

def get_case_search_output(context, input_data):
    prompt = f"""
    아래 context에 있는 사례들 중 keyword와 관련 있는 사례들을 뽑아서, 사례를 정리해줘. 각 사례들은 <case> </case> 안에 넣어서 사례끼리 분류해줘. 
    답변은 500자 이내로 간단하게 생성해주고, 필요하면 사례에 말을 더 붙여서 깔끔하게 설명을 만들어줘.
    Context: {context}
    Keyword: {input_data}
    
    답변은 무조건 한국어로 해줘.
    """
    
    response = get_LLM_output(prompt)
    return response




