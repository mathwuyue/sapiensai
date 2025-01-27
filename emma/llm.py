import asyncio
import os
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv
from openai import AsyncOpenAI

from logger import logger

load_dotenv()


client = AsyncOpenAI(api_key=os.getenv("LITELLM_KEY"), base_url="http://127.0.0.1:4000")


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
    try:
        start = time.time()
        response = await client.chat.completions.create(
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


if __name__ == "__main__":
    response = asyncio.run(llm("你好", "gpt-4o-mini"))
    print(response)
