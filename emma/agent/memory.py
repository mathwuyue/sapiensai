import sys
import os

# Add the parent directory to the package search path
sys.path.append(os.path.abspath('..'))

from peewee import *
from openai import OpenAI
import dotenv
import os
from embedding import LocalEmbedding
from prompt import memory_prompt
from db import MemoryModel
from tool.load_file import LoadWordDoc
import time
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from llm import llm

dotenv.load_dotenv()

      
class Memory:
    model = 'qwen2-72b-instruct'
    client = OpenAI(api_key=os.getenv("DASHSCOPE_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    embedding_engine = LocalEmbedding

    @classmethod
    def load_memory(cls, filepath, organization, meta=None, file_type="docx", monitor=None):
        if file_type == "docx":
            pairs = LoadWordDoc().load(filepath).split_content()
        text_list = [pair['query'] for pair in pairs]
        start_time = time.time()
        embeddings = LocalEmbedding.embeddings(inputs=text_list)
        if monitor:
            end_time = time.time()
            monitor.insert_execution_stat({'name': 'embedding',
                                           'size': len(text_list),
                                           'meta': {'embedding': 'local', 'model': 'xiaobu-embedding-v2'},
                                           'duration': end_time - start_time})
        db_data = [{'text': p['query'],
                    'ans': p['ans'],
                    'embedding': e,
                    'organization': organization,
                    'meta': meta} for (p, e) in zip(pairs, embeddings)]
        MemoryModel.insert_many(db_data).execute()
        return 1

    @classmethod
    def get_memory(cls, organization, limit=0):
        try:
            if limit:
                result = MemoryModel.select(MemoryModel.text, MemoryModel.ans).where(MemoryModel.organization == organization).limit(limit)
            else:
                result = MemoryModel.select(MemoryModel.text, MemoryModel.ans).where(MemoryModel.organization == organization)
            return ([r.text for r in result], [r.ans for r in result])
        except MemoryModel.DoesNotExist:
            return None

    @classmethod
    def search_memory(cls, organization, query, topk=10):
        # achieve topk by using vector similarity
        query_embedding = cls.embedding_engine.embeddings(inputs=query)[0]
        mem_query = MemoryModel.select(MemoryModel.id, MemoryModel.text, MemoryModel.ans).where(MemoryModel.organization == organization).order_by(MemoryModel.embedding.cosine_distance(query_embedding)).limit(topk)
        return mem_query
    
    @classmethod
    def think_about(cls, organization, query):
        mem_query = cls.search_memory(organization, query)
        llm_query_examples = [q.text for q in mem_query]
        llm_query_ans = [q.ans for q in mem_query]
        llm_query = memory_prompt().render(query=query, memory=llm_query_examples)
        if not llm_query:
            return None
        # connect to llm model and wait for response
        response = cls.client.chat.completions.create(
            model=cls.model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": llm_query}],
            stream=False,
            temperature=0.1
        )
        llm_ans = response.choices[0].message.content
        if 'Fuiyo' in llm_ans:
            print(llm_query)
            print(llm_ans)
            return None
        # ans = MemoryModel.select(MemoryModel.ans).where(MemoryModel.id == mem_query[0].id).get().ans
        ans = llm_query_ans[int(llm_ans)-1]
        return ans


class LocalMemoryModel(BaseModel):
    memory_id: UUID = Field(default_factory=uuid4)
    content: str
    tag: str = ""


class LocalMemory:
    def __init__(self, user_id):
        '''
        Record memory and history. Now only accept text. Future will accept picture, audio and video
        memeory: Used to store the observation of the agent. Key part of the history
        summary: Used to store the summary of the memory
        history: Used to store the history of the conversation
        '''
        self.user_id = user_id
        self.memory = []
        self.summary = ''
        self.history = []
        self.is_memory_changed = False
        
    def get_memory(self, limit=0, tag=None):
        if tag:
            memory = [m for m in self.memory if tag in m.tag]
        else:
            memory = self.memory
        if limit and len(memory) > limit:
            return memory[-limit:]
        else:
            return memory

    def add_memory(self, mem_obj, tag=''):
        local_mem = LocalMemoryModel(content=mem_obj.text, tag=tag)
        self.memory.append(local_mem)
        self.is_memory_changed = True
        return local_mem.memory_id
        
    def update_memory(self, memory_id, mem_obj='', tag=''):
        _tmp = list(filter(lambda x: x.memory_id == memory_id, self.memory))[0]
        if mem_obj:
            _tmp.content = mem_obj
        if tag:
            _tmp.tag = tag
        self.is_memory_changed = True
        
    def delete_memory(self, memory_id):
        self.memory = list(filter(lambda x: x.memory_id != memory_id, self.memory))
        self.is_memory_changed = True
        
    def clear_memory(self):
        self.memory = []
        self.is_memory_changed = False
        self.summary = ''
        
    def get_summary(self):
        if self.is_memory_changed:
            # TODO: use llm to generate summary
            pass
        else:
            return self.summary
        
    def get_history(self, limit=0):
        if limit and len(self.history) > limit:
            return self.history[-limit:]
        else:
            return self.history
    
        
if __name__ == '__main__':
    from monitor.monitor import BasicUserStat
    # monitor = BasicUserStat()
    # Memory.load_memory('../data/wenda.docx', 'dehan0001', meta={'embedding': 'local', 'model': 'xiaobu-embedding-v2'}, monitor=monitor)
    # resp = Memory.think_about('dehan0001', '我们要写周报么')
    # if resp:
    #     print(resp)
    resp = Memory.get_memory('dehan0001', limit=5)
    for r in resp:
        print(r.text, r.ans)