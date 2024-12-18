import boto3
import os
import traceback
from botocore.config import Config


ak = os.getenv("OSS_AccessKey")
sk = os.getenv("OSS_SecretKey")
session_token = os.getenv("OSS_SessionToken")
endpoint = "https://oss-cn-hongkong.aliyuncs.com"
bucketName = "qihaotest"
# 创建obsClient实例
# 如果使用临时AKSK和SecurityToken访问OBS，需要在创建实例时通过security_token参数指定securityToken值
s3 = boto3.client(
    's3',
    aws_access_key_id=ak,
    aws_secret_access_key=sk,
    aws_session_token=session_token,
    endpoint_url=endpoint,
    config=Config(s3={"addressing_style": "virtual"}, signature_version='v4'))


def get_file(objectKey: str):
    try:
        # 流式下载
        resp = s3.getObject(bucketName=bucketName, objectKey=objectKey, loadStreamInMemory=True)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            print('Get Object Succeeded')
            print('requestId:', resp.requestId)
            # 读取对象内容
            return resp.body.buffer
        else:
            print('Get Object Failed')
            print('requestId:', resp.requestId)
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
            return None
    except:
        print('Get Object Failed')  
        print(traceback.format_exc())
        return None
