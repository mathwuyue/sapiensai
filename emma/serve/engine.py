import os
import sys
sys.path.append(os.path.abspath('..'))

import dotenv
from openai import AsyncOpenAI
from outlines import models
from outlines.models.openai import OpenAIConfig
from router import OptionRouter, RouterOptions
from pydantic import BaseModel
from agent.rag import RagLeader
from agent.agent import NullAgent
from agent.qa import QAAgent
import redis
from typing import Dict, Any
import uuid
import time


dotenv.load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("DASHSCOPE_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
config = OpenAIConfig("qwen2-72b-instruct")
model = models.openai(client, config)


class Query(BaseModel):
    role: str
    content: str
    
    
class ChatConfig(BaseModel):
    user_id: uuid.UUID
    user_meta: Dict[str, Any]
    event_id: str
    organization: str


router_options = RouterOptions(
    options=["人力资源相关问题", "与前续对话相关", "Other"],
    actions={"人力资源相关问题": RagLeader, "Other": NullAgent, "与前续对话相关": NullAgent}
)


async def workflow(query: Query, config: str, websocket) -> str:
    '''
    TODO: Only support single round conversation. Future should be async and support multi-round conversation.
    '''
    # TODO: event_id should be generated only for a new conversation
    r = redis.Redis()
    event_id = 'chatcmpl-' + r.get('fp').decode() + '-' + str(r.incr('event_num'))
    config['event_id'] = event_id

    if config['organization'] == 'wz0001' or config['organization'] == 'wuzi0001':
        agent = QAAgent(config, splitter='RawDocxSplitter')
        vectors, context = agent.rag(query.content)
        context_meta = [{'filename': v.doc.filename, 'path': v.doc.path} for v in vectors]
        await websocket.send_json(build_context_resp(context, context_meta, event_id, config))
        return agent.act(query.content)
    router = OptionRouter(model, router_options, config)
    question = query.content
    agentcls, choice = router.classify(question)
    if agentcls is RagLeader:
        # TODO: evaluate config and call RagLeader
        agent = RagLeader(config)
        # rag context
        context, context_meta = agent.rag(question)
        ref_resp = build_context_resp(context, context_meta, event_id, config)
        if ref_resp:
            await websocket.send_json(ref_resp)
    else:
        config['answer'] = '您好！我是您的物资问题助手，关于物资相关的问题，如发票、采购等，我都能尽量帮您解决。但是别的问题我不懂，不能回复，不好意思哦。'
        agent = agentcls(config=config)
    return agent.act(question)


def build_context_resp(context, context_meta, event_id, config):
    # Extract the unique part of the event_id
    unique_part = event_id.split('-', 1)[1]
    # Create the new id with 'refcmpl-' prefix
    new_id = f"refcmpl-{unique_part}"
    # chunks
    if context:
        chunks = context.split('\n')[:-1]
    else:
        return None
    # Build the response dictionary
    response = {
        "id": new_id,
        "user_id": config['user_id'],
        "session_id": str(config['session_id']),
        "object": "chat.completion.ref",
        "created": int(time.time()),
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {
                "index": i,
                "delta": {
                    "title": context_meta[i]['filename'],
                    "filename": context_meta[i]['path'],
                    "content": chunks[i],
                }
            }
            for i in range(len(chunks))]
    }
    return response