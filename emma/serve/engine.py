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
model = 'qwen2.5-instruct-awq'


class Query(BaseModel):
    role: str
    content: str
    
    
class ChatConfig(BaseModel):
    user_id: uuid.UUID
    user_meta: Dict[str, Any]
    event_id: str
    organization: str
    
    
user_intents = [
    'Input required information',
    'Ask for dietary recommendations',
    'Ask questions about food / nutrition',
    'Topics related to health, medicine, and symptoms',
    'Topics related to exercise and fitness',
    'Chat about feelings, emotions, personal life, tastes, preferences, situations, experiences, relationships and other personal topics',
]


async def workflow(query: Query, config: str, websocket) -> str:
    # TODO: event_id should be generated only for a new conversation
    r = redis.Redis()
    event_id = 'chatcmpl-' + r.get('fp').decode() + '-' + str(r.incr('event_num'))
    config['event_id'] = event_id
    config['model'] = model
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