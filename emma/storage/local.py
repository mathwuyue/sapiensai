import os
from dotenv import load_dotenv

load_dotenv()


BASE_PATH = os.getenv('STORAGE_PATH')


def get_file(path: str):
    return open(BASE_PATH + path, 'rb').read()