import requests
import pytest

@pytest.fixture
def access_token_user1():
    response = requests.post('https://api.dev.uspray.kr/api/user/login', json={
        "id": "userid",
        "password": "password"
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()
    return response.json()['access_token']

@pytest.fixture
def access_token_user2():
    response = requests.post('https://api.dev.uspray.kr/api/user/login', json={
        "id": "dddd11",
        "password": "password"
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()
    return response.json()['access_token']

def test_get_share_list(access_token_user1):
    headers = {'Authorization': f'{access_token_user1}'}
    response = requests.get('https://api.dev.uspray.kr/api/share', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.fixture
def test_post_pray(access_token_user2):
    headers = {'Authorization': f'{access_token_user2}'}
    response = requests.post('https://api.dev.uspray.kr/api/pray', headers=headers, json={
    "target": "배서현",
    "title": "share_pytest 입니다",
    "deadline": "2024-08-01"
    })
    assert response.status_code == 200
    assert len(response.json()) > 0
    return response.json()['id']

def test_share_social_pray(access_token_user1, test_post_pray):
    headers = {'Authorization': f'{access_token_user1}'}
    response = requests.get(f'https://api.dev.uspray.kr/api/share/social?pray_list={test_post_pray}', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.fixture
def test_get_share_list(access_token_user1):
    headers = {'Authorization': f'{access_token_user1}'}
    response = requests.get('https://api.dev.uspray.kr/api/share', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    return response.json()[0]['pray_id']

@pytest.fixture
def test_share_save_pray(access_token_user1, test_get_share_list):
    print(test_get_share_list)
    headers = {'Authorization': f'{access_token_user1}'}
    body = {
      "pray_id_list": [
        test_get_share_list
      ]
    }
    response = requests.post('https://api.dev.uspray.kr/api/share/save', headers=headers, json=body)
    assert response.status_code == 200
    assert len(response.json()) > 0
    return response.json()[0]['id']

def test_share_delete_pray(access_token_user1, test_share_save_pray):
    print(test_share_save_pray)
    headers = {'Authorization': f'{access_token_user1}'}
    response = requests.delete(f'https://api.dev.uspray.kr/api/pray/{test_share_save_pray}', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0