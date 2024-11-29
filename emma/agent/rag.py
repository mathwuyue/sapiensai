from prompt import basic_rag_prompt, rag_with_examplar_prompt, rag_with_memory_prompt, rag_with_memory_prompt_cn
from agent.agent import Agent, MemoryAgent
from agent.memory import Memory
from vectorization import VectorRetrival
from redis import Redis


class RagAgent(MemoryAgent):
    def __init__(self, role: dict = None, config: dict = None, splitter='RawMarkdownSplitter'):
        if not role:
            role = {'role': 'system',
                    'content': 'You are a RAG-based AI assistant. You will receive a user query and provide a response based on the context information. You will provide a safe, helpful, and accurate response to the user.'}
        super().__init__(role, config)
        self.vr_meta = {'embedding_model': 'LocalEmbedding', 'sentence_splitter': splitter}
        self.vector_retrieval = VectorRetrival(organization=self.organization, metadata=self.vr_meta)
        
    def rag(self, query):
        self.vector_retrieval.vector_retrieval(query=query)
        self.context, self.context_meta = self.vector_retrieval.rerank(query)
        return self.context, self.context_meta

    async def act(self, query):
        mem_ans = self.memory(query)
        (queries, ans) = Memory.get_memory(self.organization, limit=15)
        examples = list(zip(queries, ans))
        if mem_ans:
            query = rag_with_memory_prompt().render(retrieved_chunk=self.context, question=query, memory=mem_ans, examples=examples)
        else:
            if self.context:
                query = rag_with_examplar_prompt().render(retrieved_chunk=self.context, question=query, examples=examples)
                print(query)
            else:
                return None
        return self.chat(query, stream=True)


class RagLeader(Agent):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.config = config
        self.user_id = config['user_id']
        self.initiate(config)
        self.rag_agent = RagAgent(config=config)
        
    def initiate(self, config):
        r = Redis(host='localhost', port=6379, db=0)
        r.set(f'{self.event_id}_rag_status', 'rag', ex=3600)
    
    def planner(self, query=None):
        '''
        1. Use RagAgent to get the response
        2. If RagAgent has no response, ask user need to Search? [Todo]
        3. Ask user whether get general answer or not
        4. If so use llm to get the response
        '''
        r = Redis(host='localhost', port=6379, db=0)
        status = r.get(f'{self.event_id}_rag_status').decode()
        if status == 'rag':
            if query:
                resp = self.act(query)
                if resp:
                    return resp
                else:
                    r.set(f'{self.event_id}_rag_status', 'llm', ex=3600)
                    return "I don't have the answer to this question. Do you want me to search for you?"
                
    def rag(self, query):
        return self.rag_agent.rag(query)

    def act(self, query):
        return self.rag_agent.act(query)

    def eval(self, query):
        '''
        Check whether should terminate the conversation
        '''
        pass
    
    def save_history(self):
        pass
    
    def get_history(self):
        pass
    
    def update_history(self):
        pass


if __name__ == '__main__':
    # from monitor.monitor import BasicUserStat
    # monitor = BasicUserStat()
    # Memory.load_memory('../data/wenda.docx', 'dehan0001', meta={'embedding': 'local', 'model': 'xiaobu-embedding-v2'}, monitor=monitor)
    resp = RagAgent({'organization': 'dehan0001'}).response('我们要写周报么')
    for chunk in resp:
        print(chunk.choices[0].delta.content)
        print("****************")