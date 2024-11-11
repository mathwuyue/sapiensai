from util import get_history
from prompt import router_prompt
from pydantic import BaseModel
from typing import List, Dict, Type
from agent.agent import Agent
from llm import llm


class RouterOptions(BaseModel):
    options: List[str]
    actions: Dict[str, Type[Agent]]


class Router:
    def __init__(self, model, config):
        self.model = model
        self.user_id = config.get('user_id')
        self.user_meta = config.get('user_meta')
        self.session_id = config.get('session_id')
        self.config = config
        
    def classify(self, choices, question, history):
        pass


class OptionRouter(Router):
    def __init__(self, model, options: RouterOptions, config: Dict):
        super().__init__(model, config)
        self.options = options
        
    def classify(self, query):
        # get history from redis
        histories = get_history(self.user_id, self.session_id, self.user_meta)
        if not histories:
            histories = []
        else:
            histories = histories.history
        prompt = router_prompt(self.options, query, histories)
        # connect to llm and get the choice
        choice = llm(prompt)
        choice = choice.strip("'\"")  # Remove any quotes from the choice
        agent = self.options.actions[choice]
        return agent, choice