from openai import OpenAI
from dotenv import load_dotenv
import os
from agent.memory import Memory
from redis import Redis
from llm import llm
from typing import Dict
import time

load_dotenv()
model = os.getenv("MODEL")
# model = "llama3-70b-instruct"


class Agent:
    def __init__(self, description: str = None, config=None) -> None:
        self.description = description
        
    def description(self):
        return self.description
    
    def act(self, query: str) -> str:
        raise NotImplementedError
    
    def handle_function_call(self, query: str) -> str:
        raise NotImplementedError
    
    def handle_tool_calls(self, query: str) -> str:
        raise NotImplementedError
    
class MemoryAgent(Agent):
    def __init__(self, role: Dict = None, config=None) -> None:
        super().__init__(role, config)
        self.organization = config['organization']
        
    def memory(self, query):
        return Memory.think_about(self.organization, query)
    

class NullAgent(Agent):
    def __init__(self, role: str = None, config=None) -> None:
        super().__init__(role, config)
        self.user_id = config['user_id']
        self.session_id = config['session_id']
        self.answer = config['answer']
    
    def act(self, query: str) -> str:
        print('in NullAgent')
        created = int(time.time())
        content = [{'role': 'assistant', 'content': ''}, {'content': self.answer}, {'content': ''}]
        finish_reason = [None, None, 'stop']
        resp = [{'id': 'chatcmpl-000',
                 'object': 'chat.completion.chunk',
                 'created': created,
                 'model': model,
                 'system_fingerprint': 'fp_990915emma',
                 'choices': [{'index': 0, 'delta': d[0], 'logprobs': None, 'finish_reason': d[1]}]} for d in zip(content, finish_reason)]
        return resp
    

class AgentLeader(Agent):
    def __init__(self, agents: dict, config=None) -> None:
        self.agents = agents
    
    def act(self, query: str) -> str:
        for agent in self.agents:
            response = agent.act(query)
            if response:
                return response
        return "I am sorry. I am not able to answer your question."
    
    def planner(self, query: str) -> str:
        return self.act(query)
    
    
class AgentCoordinator:
    def __init__(self, agents: dict) -> None:
        self.agents = agents
    
    def act(self, query: str) -> str:
        for agent in self.agents:
            response = agent.act(query)
            if response:
                return response
        return "I am sorry. I am not able to answer your question."