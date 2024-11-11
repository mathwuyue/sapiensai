from http import HTTPStatus
import os
import dashscope
from openai import OpenAI
from dotenv import load_dotenv
import time
import instructor
load_dotenv()


client = OpenAI(api_key=os.getenv("DASHSCOPE_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
dashscope.api_key = os.getenv("DASHSCOPE_KEY")


def llm(query: str, model: str = 'qwen2-72b-instruct', stream=False, temperature=0.85, top_p=0.8, history=[], json_model=None) -> str:
    messages = history + [{"role": "user", "content": query}]
    if 'llama' in model:
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            temperature=temperature,
            result_format='message',
            top_p=top_p
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.text
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
    else:
        start = time.time()
        if json_model:
            json_client = instructor.from_openai(client)
            response = json_client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                response_model=json_model,
                temperature=temperature,
                top_p=top_p
            )
        else:
            print(model)
            print(os.getenv("DASHSCOPE_KEY"))
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                temperature=0.1
            )
        print('llm time: ', time.time()-start)
        if stream:
            return response
        if json_model:
            return response
        return response.choices[0].message.content
    

def chunk_to_dict(chunk) -> dict:
    if isinstance(chunk, dict):
        return chunk
    return chunk.model_dump()
    # return {
    #     'id': chunk.id,
    #     'created': chunk.created,
    #     'model': chunk.model,
    #     'system_fingerprint': chunk.system_fingerprint,
    #     'object': chunk.object,
    #     'choices': [{'index': c.index, 'delta': c.delta, 'logprobs': c.logprobs, 'finish_reason': c.finish_reason} for c in chunk.choices]
    # }