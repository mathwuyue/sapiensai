import httpx
import pytest


def test_post_user_id():
    # Configure headers
    headers = {
        "Authorization": "Bearer 2e6380b6537c5fce2bb321b48bf0785d",
        "Content-Type": "application/json"
    }
    
    # Define endpoint
    url = "http://ehr.stalent:19030/v1/userinfo/basicinfo"
    
    # Prepare data
    data = {
        "user_id": "17601320166"
    }
    
    # Make POST request
    with httpx.Client() as client:
        response = client.post(
            url=url,
            headers=headers,
            json=data
        )
    
    # Verify response
    assert response.status_code == 200
    print(response.json())  # Verify response contains JSON


def test_post_user_food_info():
    # Configure headers
    headers = {
        "Authorization": "Bearer 2e6380b6537c5fce2bb321b48bf0785d",
        "Content-Type": "application/json"
    }
    
    # Define endpoint
    url = "http://ehr.stalent.cn:19030/v1/userinfo/food"
    
    # Prepare data
    data = {
        "user_id": "17601320166",
        "url": "1.jpg",
        "storage": "local",
        "type": 3
    }
    
    # Make POST request
    with httpx.Client(timeout=20) as client:
        response = client.post(
            url=url,
            headers=headers,
            json=data
        )
    
    # Verify response
    assert response.status_code == 200
    print(response.json())  # Verify response contains JSON