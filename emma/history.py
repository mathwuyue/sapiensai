'''
Common Utility functions. Please modify the functions as needed.
'''

from db import db, UserHistory
from pydantic import BaseModel
from typing import List, Optional
import uuid


class HistoryItem(BaseModel):
    role: str
    content: str


class History(BaseModel):
    state: Optional[str] = None
    history: List[HistoryItem] = []
    

def generate_unique_session_id(user_id):
    while True:
        session_id = str(uuid.uuid4())
        if not UserHistory.get_or_none(user_id=user_id, session_id=session_id):
            return session_id
        
        
def delete_session(user_id, session_id):
    UserHistory.update(is_deleted=True).where((UserHistory.user_id == user_id) & (UserHistory.session_id == session_id)).execute()


def get_history(user_id, session_id, limit=40):
    '''
    Won't use user_meta in this version. Remove Redis
    '''
    results = UserHistory.select(
        UserHistory.role,
        UserHistory.message,
        UserHistory.state,
        UserHistory.created_at
    ).where(
        (UserHistory.user_id == user_id) & 
        (UserHistory.session_id == session_id) &
        (UserHistory.is_deleted == False)
    ).order_by(
        UserHistory.created_at.desc()
    ).limit(limit)

    history = None
    if results:
        history = {
            'state': list(results)[-1].state,
            'history': [
                HistoryItem(
                    role=h.role, 
                    content=h.message
                ).model_dump()
                for h in sorted(list(results), key=lambda x: x.created_at)
            ]
        }
    return history


def update_history(user_id: str, session_id: str, user_meta: dict, state: str, records: HistoryItem | list[HistoryItem]) -> History:
    '''
    Remove redis cache in this version 
    '''
    if not isinstance(records, list):
        records = [records]
    # Insert new records
    data = [
        {
            'user_id': user_id,
            'session_id': session_id,
            'role': record.role,
            'message': record.content,
            'state': state
        }
        for record in records
    ]
    with db.atomic():
        UserHistory.insert_many(data).execute()
    # Return updated history
    return get_history(user_id, session_id, user_meta)


def search_history():
    pass


if __name__ == '__main__':
    user_id = 17601320166
    session_id = 'c5f377f8-9fc6-465c-8498-4d4afc5a134c'
    user_meta = {'organization': 'dehan0001'}
    item1 = HistoryItem(role='user', content='你好')
    item2 = HistoryItem(role='user', content='哈哈')
    item3 = HistoryItem(role='assistant', content='你好吗')
    items = [item2 for _ in range(10)]
    
    history = get_history(user_id, session_id, user_meta, limit=3)
    print(history)
    history = update_history(user_id, session_id, user_meta, 'test', [item1,])
    print(history)
    history = get_history(user_id, session_id, user_meta, limit=3)
    print(history)
    history = update_history(user_id, session_id, user_meta, 'test', items)
    print(history)
    history = get_history(user_id, session_id, user_meta, limit=3)
    print(history)
    history = update_history(user_id, session_id, user_meta, 'test', [item3,])
    print(history)
    history = get_history(user_id, session_id, user_meta, limit=3)
    print(history)