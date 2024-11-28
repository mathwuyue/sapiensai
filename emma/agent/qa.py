from agent.rag import RagAgent
from agent.memory import Memory
from prompt import rag_with_memory_prompt, qa_prompt


class QAAgent(RagAgent):
    def __init__(self, config, splitter='RawMarkdownSplitter') -> None:
        self.context = None
        super().__init__(config=config, splitter=splitter)
        
    def rag(self, query):
        vectors, context = self.vector_retrieval.vector_retrieval(query=query, topk=5, raw=True)
        self.context = context
        return vectors, context
    
    async def act(self, query):
        if not self.context:
            _, self.context = self.rag(query)
        # mem_ans = self.memory(query)
        # (queries, ans) = Memory.get_memory(self.organization, limit=15)
        # examples = list(zip(queries, ans))
        # if mem_ans:
        #     query = rag_with_memory_prompt().render(retrieved_chunk=self.context, question=query, memory=mem_ans, examples=examples)
        # else:
        query = qa_prompt(query, context=self.context)
        return await self.chat(query, stream=True)
    
    
if __name__ == '__main__':
    # from monitor.monitor import BasicUserStat
    # monitor = BasicUserStat()
    # Memory.load_memory('../data/wenda.docx', 'dehan0001', meta={'embedding': 'local', 'model': 'xiaobu-embedding-v2'}, monitor=monitor)
    resp = QAAgent({'organization': 'wz0001'}).response('发票')
    for chunk in resp:
        print(chunk.choices[0].delta.content)
        print("****************")