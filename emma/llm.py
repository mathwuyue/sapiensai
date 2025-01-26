import asyncio
import os
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv
from litellm import acompletion

from logger import logger

load_dotenv()


# client = AsyncOpenAI(api_key=os.getenv("DASHSCOPE_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
api_key = {"dashscope": os.getenv("DASHSCOPE_KEY"), "vllm": os.getenv("VLLM_API_KEY")}
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
LLM_PROVIDER = {
    "qwen2-72b-instruct": "dashscope",
    "qwen2.5-72b-instruct": "dashscope",
    "qwen-max": "dashscope",
    "qwen-plus": "dashscope",
    "qwen-vl-max": "dashscope",
    "qwen2-vl-7b-instruct": "dashscope",
    "Qwen/Qwen2.5-32B-Instruct-AWQ": "vllm",
    "Qwen/Qwen2.5-7B-Instruct-AWQ": "vllm",
    "qwen2.5-32b-instruct-awq": "vllm",
    "qwen2.5-7b-instruct-awq": "vllm",
    "qwen2.5-instruct-awq": "vllm",
}


async def llm(
    query: str,
    model: str = os.getenv("MODEL"),
    sys_msg=None,
    stream=False,
    temperature=0.85,
    top_p=0.8,
    history=[],
    json_format=None,
    is_text=False,
) -> str:
    if sys_msg:
        messages = (
            [{"role": "system", "content": sys_msg}]
            + history
            + [{"role": "user", "content": query}]
        )
    else:
        messages = history + [{"role": "user", "content": query}]
    llm_provider = LLM_PROVIDER.get(model, None)
    try:
        start = time.time()
        if llm_provider == "dashscope":
            response = await acompletion(
                model=f"openai/{model}",
                api_key=api_key["dashscope"],
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                messages=messages,
                temperature=temperature,
                stream=stream,
            )
        elif llm_provider == "vllm":
            response = await acompletion(
                model=f"hosted_vllm/{model}",
                api_key=api_key["vllm"],
                api_base=os.getenv("VLLM_API_BASE"),
                messages=messages,
                temperature=temperature,
                stream=stream,
                response_format=json_format,
            )
        else:
            response = await acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=stream,
                response_format=json_format,
            )
        print("llm time:", time.time() - start)
        if not is_text:
            return response
        assert stream is False
        return response.choices[0].message.content
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_msg = (
            f"{timestamp} - Model: {model} - Error: {str(e)}\n{traceback.format_exc()}"
        )
        logger.error(error_msg)
        print(error_msg)


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


if __name__ == "__main__":
    response = asyncio.run(llm("你好", "gpt-4o-mini"))
    print(response)
