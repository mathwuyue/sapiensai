from minio import Minio
from llama_parse import LlamaParse
import tempfile
import dotenv
import os


dotenv.load_dotenv()

LLAMAPARSE_KEY = os.getenv('LLAMAPARSE_KEY')
MINIO = {'endpoint': '192.168.1.40:19000', 
         'access_key': os.getenv('MINIO_ACCESS_KEY'),
         'secret_key': os.getenv('MINIO_SECRET_KEY')}


class MinIOParse:
    def __init__(self, bucket):
        self.bucket = bucket
        # Initialize Minio client here. Replace 'YOUR_ENDPOINT', 'YOUR_ACCESS_KEY', and 'YOUR_SECRET_KEY' with actual values.
        self.minio_client = Minio(MINIO['endpoint'],
                                  access_key=MINIO['access_key'],
                                  secret_key=MINIO['secret_key'],
                                  secure=False)
        self.parser = LlamaParse(api_key=LLAMAPARSE_KEY, result_type='markdown')

    def parse(self, document_name):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as temp_file:
            # Get the object from the bucket
            response = self.minio_client.get_object(self.bucket, document_name)
            for d in response.stream(32*1024):
                temp_file.write(d)
            # Now the document is downloaded to temp_file.name
            # Implement the parsing logic here
            print(f"Document {document_name} has been loaded to {temp_file.name}")
            documents = self.parser.load_data(temp_file.name)
            # save to files
            for idx, doc in enumerate(documents):
                print(doc.get_doc_id())
                with open(f"result/{document_name}_{idx}.md", 'w') as f:
                    f.write(doc.get_content())
            return documents

    def parse_all(self):
        # List all objects in the bucket
        objects = self.minio_client.list_objects(self.bucket)
        documents = []
        for obj in objects:
            documents.append(self.parse(obj.object_name))
        return documents


if __name__ == '__main__':
    parser = MinIOParse('dehan0001')
    documents = parser.parse_all()
    print(documents)