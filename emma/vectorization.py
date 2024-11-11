from llama_index.core.node_parser import SentenceSplitter
from embedding import sliced_norm_l2, LocalEmbedding
from db import db, Document, Vector1792
import time
from jinja2 import Template
from llm import llm
from prompt import rerank_prompt
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

load_dotenv()


class VectorModel(BaseModel):
    doc_id: str
    text: str
    embedding: List[float]
    organization: str
    meta: dict


class Vectorization:
    def __init__(self, embedding_model=None, sentence_splitter=None):
        self.embedding_model = embedding_model or LocalEmbedding()
        self.sentence_splitter = sentence_splitter or SentenceSplitter(chunk_size=512, chunk_overlap=128)

    def create_sentence_vector(self, text, doc_id=None, dimensions=None, is_store=False, table=Vector1792):
        doc_id = doc_id or 'default'
        embedding = self.embedding_model.embedding([text])[0]
        meta = {'embedding_model': self.embedding_model.__class__.__name__}
        if is_store:
            table.insert(doc_id=doc_id, text=text, embedding=embedding, meta=meta).execute()
        return embedding

    def create_doc_vectors(self, document: Document, dimensions=None, is_store=True, table=Vector1792):
        meta = {}
        doc_txt = document.text
        # sentence split
        if isinstance(self.sentence_splitter, SentenceSplitter):
            # remove all '\n'
            text = doc_txt.replace('\n', '')
            document.text = text
            nodes = self.sentence_splitter.get_nodes_from_documents([document])
            inputs = [node.text for node in nodes]
            meta['sentence_splitter'] = 'Llamaindex'
        else:
            inputs = self.sentence_splitter.split(doc_txt)
            meta['sentence_splitter'] = repr(self.sentence_splitter)
        # embedding
        meta['embedding_model'] = self.embedding_model.__class__.__name__
        print('start to embedding...')
        start = time.time()
        embeddings = self.embedding_model.embeddings(inputs=inputs)
        print(time.time() - start)
        # embedding storage
        if is_store:
            if dimensions:
                assert ''.join(filter(str.isdigit, table.__name__)) == str(dimensions), 'Table dimensions not match'
                embeddings = [sliced_norm_l2(emb, dimensions) for emb in embeddings]
            vector_objs = [{
                'doc_id': document.doc_id,
                'text': vm[0],
                'embedding': vm[1],
                'organization': document.metadata['organization'],
                'meta': meta} for vm in zip(inputs, embeddings)]
            with db.atomic():
                table.insert_many(vector_objs).execute()
                Document.get_or_create(doc_id=document.doc_id,
                                       defaults={'filename': document.metadata['filename'],
                                                 'organization': document.metadata['organization']})
        return embeddings


class VectorRetrival:
    def __init__(self, organization, embedding_model=None, rerank_model='qwen2-72b-instruct', table=Vector1792, metadata=None):
        self.organizaton = organization
        self.table = table
        self.metadata = metadata or {'embedding_model': 'LocalEmbedding', 'sentence_splitter': 'RawMarkdownSplitter'}
        self.docs = ''
        self.doc_meta = []
        self.rerank_model = rerank_model
        self.embedding_model = embedding_model or LocalEmbedding()
        
    def build_retrieved_result(self, chunks):
        retrival_chunks = ""
        for i, chunk in enumerate(chunks, start=1):
            # Remove special characters and newlines
            cleaned_chunk = chunk.text.replace('#', '').replace('\n', '')
            # Append to the formatted string
            retrival_chunks += f"{i}. {cleaned_chunk}\n"
        return retrival_chunks

    def vector_retrieval(self, query, topk=20, raw=False):
        db.execute_sql('SET search_path TO valacy,public')
        query_embedding = self.embedding_model.embeddings(inputs=[query])[0]
        vectors = (self.table.select(self.table.doc_id, self.table.text, self.table.meta, self.table.embedding.cosine_distance(query_embedding).alias('distance'), Document.filename, Document.path)
                   .join(Document, on=(self.table.doc_id == Document.doc_id), attr='doc')
                   .where(
                       (self.table.meta['embedding_model']==self.metadata['embedding_model']) & (self.table.meta['sentence_splitter']==self.metadata['sentence_splitter']) & (self.table.organization == self.organizaton))
                   .order_by(
                       self.table.embedding.cosine_distance(query_embedding))
                   .limit(topk))
        context = self.build_retrieved_result(vectors)
        self.docs += context
        self.doc_meta.extend([v.meta for v in vectors])
        if raw:
            return vectors, context
        return context
    
    def keyword_retrieval(self, query, topk=20, raw=False):
        index_name = self.table.__name__.lower()
        sql_tpl = '''SELECT doc_id, text FROM {{ index_name }}_index.search('(text:"{{ query }}" AND organization:{{ organization }} AND meta.embedding_model:{{ emb_model }} AND meta.sentence_splitter:{{ splitter }})',
            limit_rows => {{ topk }});
        '''
        sql = Template(sql_tpl).render(index_name=index_name, query=query, organization=self.organizaton, emb_model=self.metadata['embedding_model'], splitter=self.metadata['sentence_splitter'], topk=topk)
        items = self.table.raw(sql)
        context = self.build_retrieved_result(items)
        self.docs += context
        self.doc_meta.extend([v.meta for v in items])
        if raw:
            return items
        return context
    
    def hybrid_retrieval(self, query, topk=20):
        pass
    
    def rerank(self, query, topk=5) -> tuple[str, List[dict]]:
        if not self.docs:
            return None, None
        query = rerank_prompt().render(query=query, documents=self.docs, topk=topk)
        result: str = llm(query, self.rerank_model, stream=False)
        # build dict from result string
        doc_ids_dict = eval(result)
        doc_ids = doc_ids_dict.get("documents", [])
        doc_ids = [int(doc_id) for doc_id in doc_ids]
        if not doc_ids:
            return None, None
        # return rerank context
        reranked_chunks = []
        chunks = self.docs.split('\n')
        reranked_meta = []
        for doc_id in doc_ids:
            for chunk in zip(chunks, self.doc_meta):
                if chunk[0].startswith(f"{doc_id}. "):
                    reranked_chunks.append(chunk[0])
                    reranked_meta.append(chunk[1])
                    break
        return "\n".join(reranked_chunks), reranked_meta


if __name__ == '__main__':
    from tool.splitter import RawMarkdownSplitter