import re
import torch
import transformers

def get_LLM_pipeline():
    model_id = "rtzr/ko-gemma-2-9b-it"

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )

    pipeline.model.eval()
    return pipeline

LLM_pipeline = get_LLM_pipeline()
terminators = [
    LLM_pipeline.tokenizer.eos_token_id,
    LLM_pipeline.tokenizer.convert_tokens_to_ids("<end_of_turn>")
]

def get_LLM_output(prompt, temperature=0.6, top_p=0.9):
    global LLM_pipeline, terminators

    messages = [
        {"role": "user", "content": prompt}
    ]

    LLM_input = LLM_pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    outputs = LLM_pipeline(
        LLM_input,
        max_new_tokens=2048,
        eos_token_id=terminators,
        do_sample=True,
        temperature=temperature, 
        top_p=top_p,
    )

    response = outputs[0]["generated_text"][len(LLM_input):]
    return response



def get_QA_output(context, input_data):
    prompt = f"""
    지금은 비상 재난 상황이야. 아래 question에 있는 상황에 대해서, context를 참고하여 답변을 생성해줘.
    Context: {context}
    Question: {input_data}
    답변은 500자 이내로 간단하게 생성해줘.
    """

    response = get_LLM_output(prompt, 0.2)
    return response


def get_guide_line_output(context, input_data):
    prompt = f"""    
    지금은 비상 재난 상황이야. 아래 question에 있는 상황에 대해서, context를 참고하여 가이드라인을 생성해줘.
    Context: {context}
    Input: {input_data}
    답변은 500자 이내로 간단하게 생성해줘.
    """

    response = get_LLM_output(prompt, 0.2)
    return response





