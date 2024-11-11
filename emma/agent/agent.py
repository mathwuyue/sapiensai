from openai import OpenAI
from dotenv import load_dotenv
import os
from agent.memory import Memory
from redis import Redis
from llm import llm
from typing import Dict
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("DASHSCOPE_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
model = "qwen2-72b-instruct"
# model = "llama3-70b-instruct"


class Agent:
    def __init__(self, role: Dict = None, config=None) -> None:
        self.role = role or {'role': 'system', 
                             'content': '你是一个名为Qwen的AI助手，你更擅长中文和英文对话。你将接收到一个用户的问题，请根据你的知识库回答这个问题。你会为用户提供安全，有帮助，准确的回答。'}
        self.config = config
        self.event_id = config['event_id']
        r = Redis(host='localhost', port=6379, db=0)
        r.set(f"{self.event_id}_rag_status", "start")
    
    def act(self, query: str) -> str:
        return query
    
    def chat(self, query: str, stream=False, history=[], json_model=None) -> str:
        return llm(query, model, stream, history, json_model)
    
    def response(self, query: str) -> str:
        return self.chat(query)
    
    
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
    
    def planner(self, instruction: str) -> str:
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