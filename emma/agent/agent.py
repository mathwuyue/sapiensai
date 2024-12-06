from dotenv import load_dotenv
import os
from agent.memory import Memory
from llm import llm
from typing import Dict, Generator, Any
import time
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from history import UserHistory
from logger import file_error_handler as err_logger

load_dotenv()
model = os.getenv("MODEL")
# model = "llama3-70b-instruct"


class AgentConfig(BaseModel):
    user_id: str = Field(..., description="User identifier")
    session_id: UUID = Field(..., description="Session identifier")
    model: Optional[str] = Field(default="qwen2.5-instruct-awq", description="Model identifier")
    priority: Optional[int] = Field(default=0, description="Priority level (optional)", ge=0, le=100)


class Agent:
    """TODO: add memory for agents"""
    def __init__(self, config: AgentConfig, description: str = '') -> None:
        self.config = config
        self.description = description
        self.task_report = ''
        
    def description(self):
        return self.description
    
    def act(self, query: str, state) -> str:
        raise NotImplementedError
    
    def assign_task(self, query: str, state: int = 0, task_type: int = 0) -> str:
        if task_type == 0:
            return self.act(query, state)
    
    def report_task(self) -> str:
        return self.task_report
    
    def handle_function_call(self, query: str) -> str:
        raise NotImplementedError
    
    def handle_tool_calls(self, query: str) -> str:
        raise NotImplementedError
    
    def _store_history(self, role: str, message: str, state: int = 0) -> None:
        """Store user query in UserHistory"""
        try:
            UserHistory.create(
                user_id=self.config.user_id,
                session_id=self.config.session_id,
                role=role,
                message=message,
                state=state,
            )
        except Exception as e:
            err_logger.error(f"Failed to store history: {e}")
            raise
        
    async def _user_llm(self, query: str, model: str, history: list, temperature: float = 0.85, stream: bool = False):
        """User LLM. Final return to user
            TODO: how to decide the conversation state?
        """
        if stream:
            agent_resp = ''
            async for chunk in llm(query, model=self.config.model, history=history, temperature=temperature, stream=stream):
                agent_resp += chunk.choices[0].message.content
                yield chunk
        else:
            llm_resp = await llm(query, model=self.config.model, history=history, temperature=temperature, stream=stream)
            agent_resp = llm_resp.choices[0].message.content
            yield llm_resp
        # save to history
        self._store_history('assistant', agent_resp)


class ChatAgent(Agent):
    def act(self, query: str, state: int, agent_type: str = 'default', template=None, contex: dict = None, temperature=0.85, stream=False) -> Generator[Any, None, None]:
        # get UserHistory
        history = [{'role': item.role, 'content': item.content} for item in UserHistory.get_history(self.config.user_id, self.config.session_id)]
        # store user query in UserHistory
        self._store_history('user', query, state)
        # create query
        if agent_type == 'default':
            llm_query = template(query, **contex)
            for chunk in self._user_llm(llm_query, self.config.model, history, temperature, stream):
                yield chunk


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