import random
import string
import time
import traceback
import uuid
from datetime import datetime, timedelta
from typing import Optional

import dotenv
import redis
from fastapi import APIRouter, HTTPException, Request, WebSocket

from db import UserHistory
from history import delete_session, generate_unique_session_id
from llm import chunk_to_dict
from logger import logger
from serve.db import ChatMission, UploadFile
from serve.engine import Query, workflow
from serve.model import (
    ChatHistoryRequest,
    ChatMissionRequest,
    ChatRequest,
    ChatSessionRequest,
    ChatSessionResponse,
    FileStatusResponse,
    UploadFileRequest,
)

dotenv.load_dotenv()
router = APIRouter()


# init redis set chat key 'fp' to random a-zA-Z0-9 string
def generate_random_string(length=4):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choices(characters, k=length))
    return random_string


random_string = generate_random_string()
r = redis.Redis()
r.set("fp", random_string)


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
    """
    TODO: Implement the logic to handle the file upload request
    """
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
            updated_at=datetime.now(),
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
                status=0, resp={"doc_id": doc_id, "doc_status": "not found"}
            )
        return FileStatusResponse(
            status=1, resp={"doc_id": doc_id, "doc_status": upload_file.status}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/v1/chat/session", response_model=ChatSessionResponse)
async def create_chat_session(request: ChatSessionRequest):
    try:
        # Extract user_id or use a default if not provided
        user_id = request.user_id
        # Generate a unique session ID
        if request.is_dynamic:
            session_id = generate_unique_session_id(user_id)
        else:
            session_id = "542bf4d5-ec2b-48af-8cf5-6ce527efef9f"
        return ChatSessionResponse(user_id=user_id, session_id=session_id)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/v1/chat/session/delete")
async def delete_chat_session(request: ChatSessionResponse):
    try:
        # delete chat session
        delete_session(request.user_id, request.session_id)
        return {"status": 1}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/v1/chat/mission")
async def create_chat_mission(request: ChatMissionRequest):
    try:
        user_id = request.user_id
        mission_jwt = request.mission_jwt

        # Store the mission
        mission = ChatMission.create(
            user_id=user_id,
            mission_jwt=mission_jwt,
            created_at=request.created_at,
        )

        return {"status": 1, "id": mission.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/v1/chat/mission/delete")
async def delete_chat_mission(request: ChatMissionRequest):
    try:
        mission = (
            ChatMission.update(is_deleted=True)
            .where(ChatMission.mission_jwt == request.mission_jwt)
            .execute()
        )
        return {"status": 1}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/v1/chat/completions")
async def chat_websocket(websocket: WebSocket):
    """
    This is the websocket endpoint for cloud chat completions
    """
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        chat_request = ChatRequest(**data)
        app_key = chat_request.app_key
        mission = ChatMission.get_or_none(mission_jwt=app_key)
        if not mission:
            await websocket.send_json(
                {"event": "error", "data": {"error": "Invalid app key"}}
            )
            await websocket.close()
            return

        config = {
            "user_id": chat_request.user_id,
            "user_meta": chat_request.user_meta,
            "organization": "default",
            "session_id": chat_request.session_id,
            "is_thought": chat_request.is_thought,
        }

        message = chat_request.messages[-1]
        text_content = (
            [message.content]
            if type(message.content) is str
            else [c.text for c in message.content if c.type == "text"]
        )
        query = Query(role=message.role, content=text_content[0])

        start = time.time()
        is_first_chunk = True

        async for chunk in workflow(query, config, None):
            if is_first_chunk:
                is_first_chunk = False
                end = time.time()

            resp_chunk = chunk_to_dict(chunk)
            resp_chunk["user_id"] = chat_request.user_id
            resp_chunk["session_id"] = str(chat_request.session_id)

            await websocket.send_json(resp_chunk)

        end2 = time.time()
        logger.info(
            f"WebSocket完成传输数据，传输耗时{end2 - end:.2f}秒，总耗时{end2 - start:.2f}秒"
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await websocket.send_json({"event": "error", "data": {"error": str(e)}})

    finally:
        await websocket.close()


@router.post("/v1/chat/history")
async def get_chat_history(request: ChatHistoryRequest):
    user_id = request.user_id
    session_id = request.session_id
    app_key = request.app_key
    date = request.date
    offset = request.offset
    limit = request.limit
    page = request.page
    try:
        # Start with base query
        query = UserHistory.select(
            UserHistory.role, UserHistory.message, UserHistory.created_at
        ).where(
            (UserHistory.user_id == user_id)
            & (UserHistory.session_id == session_id)
            & (UserHistory.is_deleted == False)
        )
        # Add date filtering if parameters provided
        if date and offset:
            try:
                end_date = datetime.strptime(date, "%Y-%m-%d")
                start_date = end_date - timedelta(days=offset)
                query = query.where(
                    (UserHistory.created_at >= start_date)
                    & (UserHistory.created_at <= end_date)
                )
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
                )
        # Execute query and return results
        query = query.order_by(UserHistory.created_at)
        if limit > 0:
            query = query.offset(page * limit).limit(limit)
        history = list(query.dicts())
        return {"status": 1, "history": history}
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


def init_app(app):
    app.include_router(router)
