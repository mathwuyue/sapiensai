'''
Common Utility functions. Please modify the functions as needed.
'''

import orjson
import redis
from db import db, UserHistory
from pydantic import BaseModel
from typing import List, Optional
from peewee import *
import uuid
from jinja2 import Template
from peewee import Model


class HistoryItem(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


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


def get_history(user_id, session_id, user_meta, limit=20):
    '''
    Won't use user_meta in this version
    '''
    r = redis.Redis(host='localhost', port=6379, db=0)
    key = f'{user_id}_{session_id}_history'
    # get history from redis
    history = r.get(key)
    if history:
        history = orjson.loads(history)
        if limit > 0 and len(history['history']) > limit:
            history = {
                'state': history['state'],
                'history': history['history'][-limit:]
            }
    else:
        # get from db
        sql = Template('''
        select state, message, created_at
        from userhistory_index.search('role:user AND is_deleted:false AND user_id:{{ user_id }} AND session_id:{{ session_id }}')
        order by created_at desc limit {{ limit }}
        ''').render(user_id=user_id, session_id=session_id, limit=limit)
        print(sql)
        results = list(UserHistory.raw(sql))
        if results:
            history = {
                'state': results[-1].state,
                'history': [HistoryItem(role='user', content=h.message, timestamp=h.created_at.isoformat()).model_dump()
                            for h in sorted(results, key=lambda x: x.created_at)]
            }
        else:
            history = None
        # save to redis
        if history:
            r.set(key, orjson.dumps(history), ex=18000)
    return history if history is None else History(**history)


def update_history(user_id: str, session_id: str, user_meta: dict, state: str, records: List[HistoryItem]) -> History:
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    key = f'{user_id}_{session_id}_history'
    # Append new records to UserHistory table
    with db.atomic():
        data = [
            {
                'user_id': user_id,
                'session_id': session_id,
                'user_meta': user_meta,
                'role': record.role,
                'message': record.content,
                'state': state
            }
            for record in records
        ]
        UserHistory.insert_many(data).execute()
    # Update Redis cache
    cached_history = r.get(key)
    if cached_history:
        history = History(**orjson.loads(cached_history))
    else:
        history = History(state=state, history=[])
    # Append only user messages to the Redis cache
    user_records = [record for record in records if record.role == 'user']
    history.history.extend(user_records)
    history.state = state
    # Update Redis with the new history
    r.set(key, orjson.dumps(history.model_dump()), ex=18000)
    # return history
    return history


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