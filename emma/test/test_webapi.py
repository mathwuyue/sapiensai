import asyncio
import json
import uuid

import httpx
import websockets


async def connect_and_send(user_input, url):
    headers = {"Authorization": "Bearer 2e6380b6537c5fce2bb321b48bf0785d"}
    user_id = str(uuid.uuid4())

    async with websockets.connect(url, additional_headers=headers) as websocket:
        if user_input == "\\q":
            await websocket.close()
            return
        data = {
            "model": "qwen2.5-instruct-awq",
            "user_id": "ssdix112",
            "session_id": "542bf4d5-ec2b-48af-8cf5-6ce527efef9f",
            "app_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoic2RkaW5jMTIzIiwic2Vzc2lvbl9pZCI6WyJkc3NpLWRkZy1jY25nIiwiZHNpZG4tc2lkbjExIl0sImlhdCI6MTczNzQ2NjM1MX0.n7ZTfsY8SU4dL2ANqMzPukNS50rDmeXzMR6iIts4gWY",
            "user_meta": {
                "category": "health",
                "page": "exercise",
                "section": "",
                "url": "",
            },
            "messages": [{"role": "user", "content": "#test%"}],
        }
        await websocket.send(json.dumps(data))
        while True:
            try:
                chunk = await websocket.recv()
                chunk = json.loads(chunk)
                print(chunk)
                if chunk["object"] == "chat.completion.ref":
                    print("检索到的文档：")
                    print(chunk["choices"][0]["delta"]["content"], end="\n\n")
                else:
                    print(chunk["choices"][0]["delta"]["content"], end="")
                if chunk["choices"][0].get("finish_reason") == "stop":
                    break
            except websockets.ConnectionClosed:
                break


async def test_v1_file():
    url = "http://ehr.stalent.cn:19066/v1/file"
    headers = {
        "Authorization": "Bearer 2e6380b6537c5fce2bb321b48bf0785d",
        "Content-Type": "application/json",
    }
    data = {}

    response = httpx.post(url, headers=headers, json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response Message: {response.text}")


async def test_chat_session():
    url = "http://115.223.19.227:8001/v1/chat/session"
    headers = {
        "Authorization": "Bearer 2e6380b6537c5fce2bb321b48bf0785d",
        "Content-Type": "application/json",
    }
    data = {"user_id": "18533266055"}
    response = httpx.post(url, headers=headers, json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response Message: {response.text}")


url = "ws://ehr.stalent.cn:19030/v1/chat/completions"
# while True:
#     user_input = input("Enter your message: ")
#     asyncio.get_event_loop().run_until_complete(connect_and_send(user_input, url))
#     # close websocket

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(
        connect_and_send("上班迟到了怎么办", url)
    )
