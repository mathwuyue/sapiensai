import streamlit as st
import os
import random
import string
from pypinyin import lazy_pinyin
import requests
# from fastapi import FastAPI
# from tortoise.models import Model
# from tortoise import fields
# from tortoise.contrib.fastapi import register_tortoise
from minio import Minio
from minio.error import S3Error
import tempfile


# FastAPI setup
# app = FastAPI()

# MINIO_KEY = "hrbot"
# MINIO_SECRET = "gtps4ZOxL3Q6tiNVO8A3XTYtNq1YwYQa3rOJIIP8"


# # Database model
# class File(Model):
#     id = fields.IntField(primary_key=True)
#     filename = fields.CharField(max_length=255)
#     organization = fields.CharField(max_length=255)
#     directory = fields.CharField(max_length=255)
#     search_privilege = fields.IntField()
#     description = fields.TextField()

#     class Meta:
#         table = "files"
#         schema = "valacy"

# # Database setup
# register_tortoise(
#     app,
#     db_url="postgres://hrbot:!QAZ2wsx@localhost:15432/hrbot",
#     modules={"models": ["__main__"]},
#     generate_schemas=True,
#     add_exception_handlers=True,
# )

# Streamlit app
# st.title("企业文档上传助手")


# Set Organization and create directory
# def create_bucket(organization):
#     pinyin_initials = ''.join([word[0].upper() for word in lazy_pinyin(organization)])
#     random_digits = ''.join(random.choices(string.digits, k=4))
#     bucket_name = f"{pinyin_initials}_{random_digits}"
#     return bucket_name

# organization = st.text_input("输入企业名称:")
# if st.button("确认"):
#     if organization:
#         directory_name, directory_path = create_bucket(organization)
#         st.session_state.organization = organization
#         st.session_state.directory_name = directory_name
#         st.session_state.directory_path = directory_path
#         st.success(f"成功新建企业: {organization}")
#     else:
#         st.error("请输入企业名称。")
        
# # Upload files
# if 'directory_path' in st.session_state:
#     uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
#     if uploaded_files:
#         for file in uploaded_files:
#             file_path = os.path.join(st.session_state.directory_path, file.name)
#             with open(file_path, "wb") as f:
#                 f.write(file.getbuffer())
#         st.success("文件上传成功!")
        
        
