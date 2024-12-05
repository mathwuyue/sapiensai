from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from datetime import datetime, timedelta
from typing import Optional
from serve.db import UploadFile
from db import UserHistory
import uuid
import random
import string
from serve.engine import Query, workflow
import redis
import dotenv
from llm import chunk_to_dict
from serve.model import UploadFileRequest, FileStatusResponse, ChatRequest, ChatSessionRequest, ChatSessionResponse
from history import generate_unique_session_id, delete_session
from logger import file_perf_handler as logger
import time
import traceback


dotenv.load_dotenv()
router = APIRouter()


# init redis set chat key 'fp' to random a-zA-Z0-9 string
def generate_random_string(length=4):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string
random_string = generate_random_string()
r = redis.Redis()
r.set('fp', random_string)


def generate_unique_doc_id():
    while True:
        doc_id = str(uuid.uuid4())
        if not UploadFile.get_or_none(doc_id=doc_id):
            return doc_id

# def validate_token(token: str) -> bool:
#     # Implement your token validation logic here
#     # Return True if valid, False otherwise
#     return token == os.getenv('CAPYBARA_TOKEN')


@router.post("/v1/file")
async def create_upload_file(file: UploadFileRequest):
    '''
    TODO: Implement the logic to handle the file upload request
    '''
    try:
        doc_id = generate_unique_doc_id()
        upload_file = UploadFile.create(
            doc_id=doc_id,
            title=file.title,
            filename=file.filename,
            app_id=file.app_id,
            filetype=file.filetype,
            type=file.type,
            auth=file.auth,
            meta=file.meta,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return {"status": 1, "doc_id": upload_file.doc_id}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/file/status", response_model=FileStatusResponse)
async def get_file_status(doc_id: str):
    try:
        upload_file = UploadFile.get_or_none(doc_id=doc_id)
        if not upload_file:
            return FileStatusResponse(
                status=0,
                resp={
                    "doc_id": doc_id,
                    "doc_status": "not found"
                }
            )
        return FileStatusResponse(
            status=1,
            resp={
                "doc_id": doc_id,
                "doc_status": upload_file.status
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/v1/chat/session", response_model=ChatSessionResponse)
async def create_chat_session(request: ChatSessionRequest):
    try:
        # Generate a unique session ID
        session_id = generate_unique_session_id(request.user_id)
        return ChatSessionResponse(
            user_id=request.user_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

  
@router.post("/v1/chat/session/delete")
async def delete_chat_session(request: ChatSessionResponse):
    try:
        # delete chat session
        delete_session(request.user_id, request.session_id)
        return {"status": 1}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 

@router.websocket("/v1/chat/completions")
async def chat_endpoint(websocket: WebSocket):
    '''
    This is the endpoint for cloud chat completions. Later maybe move to Ray Serve
    '''
    await websocket.accept()
    # logger.info("Websocket打开，等待数据")  # Add log message
    start = time.time()
    is_data_recv_first = True
    try:
        # auth_header = websocket.headers.get('Authorization')
        # if auth_header is None or not auth_header.startswith('Bearer '):
        #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing or invalid Authorization header")
        #     return
        # token = auth_header.split(' ')[1]
        # if not validate_token(token):
        #     await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        #     return
        # # token is valid
        while True:
            data = await websocket.receive_json()
            if is_data_recv_first:
                is_data_recv_first = False
                end = time.time()
                # logger.info(f"Websocket完成接收数据，耗时{end - start:.2f}秒")  # Add log message
            chat_request = ChatRequest(**data)
            config = {
                'user_id': chat_request.user_id,
                'user_meta': chat_request.user_meta,
                'organization': chat_request.app_id,
                'session_id': chat_request.session_id
            }
            # print(config['organization'])
            # workflow in engine
            # filter chat_request.messages which type is text
            message = chat_request.messages[-1]
            text_content = [c for c in message.content if c.type == 'text']
            query = Query(role=message.role, content=text_content[0].text)
            start = time.time()
            response = await workflow(query, config, websocket)
            is_first_chunk = True
            for chunk in response:
                if is_first_chunk:
                    is_first_chunk = False
                    end = time.time()
                    # logger.info(f"完成生成第一个chunk，开始传输数据。耗时{end - start:.2f}秒")
                resp_chunk = chunk_to_dict(chunk)
                resp_chunk['user_id'] = chat_request.user_id
                resp_chunk['session_id'] = str(chat_request.session_id)
                await websocket.send_json(resp_chunk)
            end2 = time.time()
            logger.info(f"Websocket完成传输数据，传输耗时{end2 - end:.2f}秒，总耗时{end2 - start:.2f}秒")
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE, reason=str(e))
 
 
@router.get("/v1/chat/history")
async def get_chat_history(
    user_id: str, 
    session_id: str,
    date: Optional[str] = None,
    offset: Optional[int] = None
):
    try:
        # Start with base query
        query = (UserHistory
                .select()
                .where(
                    (UserHistory.user_id == user_id) & 
                    (UserHistory.session_id == session_id) &
                    (UserHistory.is_deleted == False)
                ))

        # Add date filtering if parameters provided
        if date and offset:
            try:
                end_date = datetime.strptime(date, '%Y-%m-%d')
                start_date = end_date - timedelta(days=offset)
                query = query.where(
                    (UserHistory.created_at >= start_date) &
                    (UserHistory.created_at <= end_date)
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        # Execute query and return results
        history = list(query.order_by(UserHistory.created_at).dicts())
        return {"status": 1, "history": history}
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))
 
        
def init_app(app):
    app.include_router(router)