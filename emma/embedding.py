from typing import List
import dashscope
import httpx
import dotenv
import os
import tempfile
import orjson
import numpy as np
from tool.storage import S3Storage
from volcengine.maas import MaasException, ChatRole
from volcengine.maas.v2 import MaasService
import ollama
from sentence_transformers import SentenceTransformer
import proto.embedding_query_pb2 as embedding_query_pb2
import proto.embedding_query_pb2_grpc as embedding_query_pb2_grpc
import grpc
import pyarrow as pa
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
# import ray
# from ray import serve
from fastapi import FastAPI
from grpc import metadata_call_credentials, composite_channel_credentials, ssl_channel_credentials

dotenv.load_dotenv()

dashscope.api_key = os.getenv('DASHSCOPE_KEY')
# Define a static token
GRPC_STATIC_TOKEN = os.getenv('GRPC_STATIC_TOKEN')


def sliced_norm_l2(vec: List[float], dim=2048) -> List[float] : 
    # dim to 512,1024,2048
    norm = float(np.linalg.norm(vec[:dim]))
    return [v / norm for v in vec[:dim]]


class AliEmbedding:
    def __init__(self, bucket_name=None) -> None:
        self.bucket_name = bucket_name or 'embedding'
    
    def call(self, url: str):
        print(url)
        result = dashscope.BatchTextEmbedding.call(dashscope.BatchTextEmbedding.Models.text_embedding_async_v2,
                                                   url=url,
                                                   text_type="document")
        return result
    
    def minio_tmp_storage(self, inputs: List) -> str:
        # create tmp file and store inputs
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp:
            tmp.write('\n'.join(inputs))
            tmp_name = tmp.name  # Store the temp file name to use after closing
        minio = S3Storage(bucket_name=self.bucket_name)
        object_name = os.path.basename(tmp_name)
        url = minio.upload_and_sign(tmp_name, object_name)
        # delete tmp file
        os.unlink(tmp_name)
        return url
    
    def handle_ali_result(self, result):
        if result.status_code == httpx.codes.OK:
            if result['output']['task_status'] == 'SUCCEEDED':
                url = result['output']['url']
                # httpx download and save file from url to /tmp
                with httpx.get(url) as response:
                    response.raise_for_status()
                    filename = os.path.basename(url)
                    # Create the full path for the file to be saved in /tmp
                    filepath = os.path.join('/tmp', filename)
                    # Open the file in binary write mode and save the content
                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                print(filepath)
            else:
                print(result)
        else:
            print(result)
            return []
    
    def embedding(self, inputs: List):
        if len(inputs) == 0:
            return []
        if len(inputs) == 1:
            resp = dashscope.TextEmbedding.call(
                model=dashscope.TextEmbedding.Models.text_embedding_v2,
                input=inputs[0])
            if resp.status_code == httpx.codes.OK:
                return resp['output']['embeddings'][0]['embedding']
            else:
                print(resp)
                return []
        result = None  # merge the results.
        # batch 
        url = self.minio_tmp_storage(inputs)
        result = self.call(url)
        self.handle_ali_result(result)


class DoubaoEmbedding:
    def __init__(self) -> None:
        self.maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
        # set ak&sk
        self.maas.set_ak(os.getenv("VOLC_ACCESSKEY"))
        self.maas.set_sk(os.getenv("VOLC_SECRETKEY"))
    
    def req_embeddings(self, maas, endpoint_id, req):
        try:
            resp = maas.embeddings(endpoint_id, req)
            return resp
        except MaasException as e:
            print(e)
    
    def embeddings(self, inputs: List) -> List:
        req = {
            "input": inputs
        }
        # send to maas
        resp = self.req_embeddings(self.maas, endpoint_id="ep-20240701094254-bl56d", req=req)
        embeddings = [item["embedding"] for item in resp.data]
        # todo, log tokens usage here
        return embeddings
    
    
class OllamaEmbedding:
    def __init__(self, model: str = 'mxbai-embed-large') -> None:
        self.model = model
    
    def embedding(self, inputs: List) -> List:
        return [ollama.embeddings(model=self.model, prompt=prompt)['embedding'] for prompt in inputs]
    

class LocalEmbedding(embedding_query_pb2_grpc.EmbeddingServiceServicer):
    def __init__(self, model_path: str = None) -> None:
        self.model_path = model_path or '/home/chenxueliang/embedding/xiaobu-embedding-v2'
        self.model = SentenceTransformer(self.model_path, local_files_only=True)
    
    def _embedding(self, inputs: List) -> List:
        return list(self.model.encode(inputs, normalize_embeddings=True))
    
    def GetEmbeddings(self, request, context):
        # Token check
        token = dict(context.invocation_metadata()).get('authorization')
        if token != GRPC_STATIC_TOKEN:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid token')
        
        inputs = request.queries
        embeddings = self._embedding(inputs)
        buffer = pa.BufferOutputStream()
        pa_array = pa.array(embeddings)
        batch = pa.RecordBatch.from_arrays([pa_array], ['embeddings'])
        with pa.ipc.new_stream(buffer, batch.schema) as writer:
            writer.write_batch(batch)
        return embedding_query_pb2.EmbeddingResponse(serialized_embeddings=buffer.getvalue().to_pybytes())
    
    @classmethod
    def embeddings(cls, model='xiaobu-embedding-v2', inputs: List = None) -> np.array:
        ssl_dir = os.getenv('SSL_DIR')
        channel_options = [('grpc.ssl_target_name_override', '115.223.19.227')]
        if isinstance(inputs, str):
            inputs = [inputs]
        
        def metadata_callback(context, callback):
            callback([('authorization', GRPC_STATIC_TOKEN)], None)
        
        auth_credentials = metadata_call_credentials(metadata_callback)
        ssl_credentials = ssl_channel_credentials(
            root_certificates=open(f'{ ssl_dir }/ca/ca.crt', 'rb').read(),
            private_key=open(f'{ ssl_dir }/client/client.key', 'rb').read(),
            certificate_chain=open(f'{ ssl_dir }/client/client.crt', 'rb').read()
        )
        channel_credentials = composite_channel_credentials(ssl_credentials, auth_credentials)
        
        with grpc.secure_channel(os.getenv('EMBEDDING_SERVER'), channel_credentials, options=channel_options) as channel:
            stub = embedding_query_pb2_grpc.EmbeddingServiceStub(channel)
            response = stub.GetEmbeddings(embedding_query_pb2.EmbeddingQuery(queries=inputs))
            buffer = pa.BufferReader(response.serialized_embeddings)
            with pa.ipc.open_stream(buffer) as reader:
                batch = reader.read_next_batch()
                embeddings = batch.column(0).to_pylist()
            return embeddings

    def __str__(self) -> str:
        return f"Running {self.model_path}...."
    
    
# @serve.deployment(num_replicas=4, ray_actor_options={"num_cpus": 1, "num_gpus": 0})
# @serve.ingress(app)
# class LocalEmbeddingServe:
#     def __init__(self, model_path: str = None) -> None:
#         self.model_path = model_path or '/home/chenxueliang/embedding/xiaobu-embedding-v2'
#         self.model = SentenceTransformer(self.model_path, local_files_only=True)
    
#     def _embedding(self, inputs: List) -> List:
#         return list(self.model.encode(inputs, normalize_embeddings=True))
    
#     @app.post("/")
#     def embedding_actor(self, queries: List[str]) -> List:
#         return self._embedding(queries)
    
#     @classmethod
#     def embeddings(cls, model='xiaobu-embedding-v2', inputs: List = None) -> np.array:
#         if isinstance(inputs, str):
#             inputs = [inputs]
#         with grpc.insecure_channel('localhost:50051') as channel:
#             stub = embedding_query_pb2_grpc.EmbeddingServiceStub(channel)
#             response = stub.GetEmbeddings(embedding_query_pb2.EmbeddingQuery(queries=inputs))
#             buffer = pa.BufferReader(response.serialized_embeddings)
#             with pa.ipc.open_stream(buffer) as reader:
#                 batch = reader.read_next_batch()
#                 embeddings = batch.column(0).to_pylist()
#             return embeddings

#     def __str__(self) -> str:
#         return f"Running {self.model_path}...."


if __name__ == '__main__':
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    embedding_query_pb2_grpc.add_EmbeddingServiceServicer_to_server(LocalEmbedding(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    print("Embedding server running on 0.0.0.0:50051")
    server.wait_for_termination()
    
