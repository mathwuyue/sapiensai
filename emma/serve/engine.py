import os
import sys
sys.path.append(os.path.abspath('..'))

import dotenv
from router import RouterOptions, UserIntentionRouter
from pydantic import BaseModel
from agent.agent import NullAgent, AgentConfig, ChatAgent
import redis
from typing import Dict, Any
import uuid
import time
from prompt import emma_chat, emma_future, emma_fitness, emma_nutrition
from nutrition.emma import get_user_info
from utils import extract_json_from_text


dotenv.load_dotenv()
model = os.getenv("MODEL")


class Query(BaseModel):
    role: str
    content: str
    
    
class ChatConfig(BaseModel):
    user_id: uuid.UUID
    user_meta: Dict[str, Any]
    event_id: str
    organization: str
    
    
user_intents = [
    'Ask for or in a conversation about dietary recommendations',
    'Ask questions or in a conversation about food / nutrition',
    'In a conversation related to health, medicine, and symptoms',
    'In a conversation related to exercise and fitness',
    'In a conversation about feelings, emotions, personal life, tastes, preferences, situations, experiences, relationships and other personal topics',
]


options = RouterOptions(options=user_intents)


async def workflow(query: Query, config: str, websocket) -> str:
    # TODO: event_id should be generated only for a new conversation
    r = redis.Redis()
    event_id = 'chatcmpl-' + r.get('fp').decode() + '-' + str(r.incr('event_num'))
    config['event_id'] = event_id
    config['model'] = model
    router = UserIntentionRouter(model, options, config, '我是健康助手，我可以帮助您制定饮食计划，回答关于食物和营养的问题，以及提供健康和营养相关的建议。')
    question = query.content
    choice = await router.classify(question)
    if choice.get('message'):
        agent = NullAgent(AgentConfig(user_id=config['user_id'], session_id=config['session_id']))
        yield agent.act(question, choice['message'])
    elif int(choice.get('choice')) == 1:
        pass
    elif int(choice.get('choice')) == 2:
        pass    
    elif int(choice.get('choice')) == 3:
        emma_future_agent = ChatAgent(AgentConfig(user_id=config['user_id'], session_id=config['session_id']))
        userinfo = await get_user_info(config['user_id'])
        # Extract gestational age from userinfo
        ga_weeks = int(''.join(filter(str.isdigit, userinfo.split('Gestational Age: ')[1].split(' weeks')[0])))
        if config['is_thought']:
            yield emma_future_agent.act(question, 0, 'default', emma_future, {'context': ga_weeks}, stream=True)
        else:
            response = await emma_future_agent.act(question, 0, 'default', emma_future, {'context': ga_weeks}, stream=False)
            resp_json = extract_json_from_text(response)
            yield resp_json['answer']
    elif int(choice.get('choice')) == 4:
        emma_agent = ChatAgent(AgentConfig(user_id=config['user_id'], session_id=config['session_id']))
        userinfo = await get_user_info(config['user_id'])
        if config['is_thought']:
            yield emma_agent.act(question, 0, 'default', emma_fitness, stream=True)
        else:
            response = await emma_agent.act(question, 0, 'default', emma_fitness, stream=False)
            resp_json = extract_json_from_text(response)
            yield resp_json['message']
    else:
        emma_chat_agent = ChatAgent(AgentConfig(user_id=config['user_id'], session_id=config['session_id']))
        yield emma_chat_agent.act(question, 0, 'default', emma_chat, stream=True)


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