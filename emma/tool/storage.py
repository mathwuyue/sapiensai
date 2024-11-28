import boto3
from botocore.exceptions import ClientError
import datetime
import dotenv
import os


dotenv.load_dotenv()

# Initialize the MinIO client
client = boto3.client(
    "s3",
    endpoint_url="http://ehr.stalent.cn:19000",  # Replace with your MinIO server URL
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
    use_ssl=False,
)


class S3Storage:
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

    def upload_and_sign(self, file_path: str, object_name: str) -> str:
        # Upload the file
        try:
            with open(file_path, 'rb') as file:
                client.upload_fileobj(file, self.bucket_name, object_name)
            print(f"File '{file_path}' is successfully uploaded as '{object_name}' in bucket '{self.bucket_name}'")
        except ClientError as exc:
            print("Error occurred while uploading the file:", exc)

        # Generate a presigned URL valid for 7 days
        try:
            url = client.generate_presigned_url('get_object',
                                        Params={'Bucket': self.bucket_name, 'Key': object_name},
                                        ExpiresIn=604800)  # 7 days in seconds
            print("Presigned URL:", url)
            return url
        except ClientError as exc:
            print("Error occurred while generating the presigned URL:", exc)
            
    def download_all_files(self, output_dir: str) -> None:
        """
        Download all files from the current bucket to the specified output directory.
        
        Args:
            output_dir (str): The directory where files will be downloaded.
        """
        try:
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # List all objects in the bucket
            response = client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                print(f"No objects found in bucket '{self.bucket_name}'")
                return
            
            # Download each object
            for obj in response['Contents']:
                file_key = obj['Key']
                local_file_path = os.path.join(output_dir, file_key)
                
                # Ensure the local directory structure exists
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Download the file
                client.download_file(self.bucket_name, file_key, local_file_path)
                print(f"Downloaded '{file_key}' to '{local_file_path}'")
                
            print(f"All files downloaded to '{output_dir}'")
        except ClientError as exc:
            print(f"Error occurred while downloading files: {exc}")

