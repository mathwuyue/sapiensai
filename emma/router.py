from history import get_history
from prompt import router_prompt
from pydantic import BaseModel
from typing import List, Dict, Type
from agent.agent import Agent
from llm import llm
from utils import extract_json_from_text


class RouterOptions(BaseModel):
    options: List[str]
    agents: List[Type[Agent]] = None


class Router:
    def __init__(self, model, config):
        self.model = model
        self.user_id = config.get('user_id')
        self.user_meta = config.get('user_meta')
        self.session_id = config.get('session_id')
        self.config = config
        
    def classify(self, choices, question, history):
        pass


class UserIntentionRouter(Router):
    def __init__(self, model, options: RouterOptions, config: Dict, description: str = None):
        super().__init__(model, config)
        self.options = options.options
        self.description = description
        
    async def classify(self, query):
        # get history from redis
        histories = get_history(self.user_id, self.session_id, limit=10)
        if not histories:
            histories = []
        else:
            histories = histories['history']
        prompt = router_prompt(self.options, query, self.description)
        # connect to llm and get the choice
        choice = await llm(prompt, history=histories, is_text=True)
        choice = extract_json_from_text(choice)
        return choice
    
    
if __name__ == "__main__":
    import time
    import asyncio
    
    async def main():
        options = [
            'Input required information',
            'Ask for dietary recommendations',
            'Ask questions about food / nutrition',
            'Topics related to health, medicine, and symptoms',
            'Topics related to exercise and fitness',
            'Chat about feelings, emotions, personal life, tastes, preferences, situations, experiences, relationships and other personal topics',
        ]
        reject = '我是健康助手，我可以帮助您制定饮食计划，回答关于食物和营养的问题，以及提供健康和营养相关的建议。'
        query = '我应该如何饮食'
        prompt = router_prompt(options, query, reject)
        history = [
            {'role': 'assistant', 'content': '我是健康助手，我可以帮助您制定饮食计划，回答关于食物和营养的问题，以及提供健康和营养相关的建议。'}, 
            {'role': 'user', 'content': '你好，请问我应该如何饮食'}, {'role': 'assistant', 'content': '请问您的饮食习惯是什么呢？例如喜欢吃海鲜，不吃生菜等等。'}, 
        ]
        start = time.time()
        choice = await llm(prompt, model='qwen2.5-instruct-awq', history=history)
        choice = extract_json_from_text(choice)
        print(choice)
        print(time.time() - start)

    asyncio.run(main())