import requests
import pytest

@pytest.fixture
def access_token():
    response = requests.post('https://api.dev.uspray.kr/api/user/login', json={
        "id": "userid",
        "password": "password"
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()
    return response.json()['access_token']

def test_get_pray_list(access_token):
    headers = {'Authorization': f'{access_token}'}
    response = requests.get('https://api.dev.uspray.kr/api/pray?sort_by=date', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    response = requests.get('https://api.dev.uspray.kr/api/pray?sort_by=cnt', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_post_pray(access_token):
    headers = {'Authorization': f'{access_token}'}
    response = requests.post('https://api.dev.uspray.kr/api/pray', headers=headers, json={
    "target": "배서현",
    "title": "Pytest입니다",
    "deadline": "2024-08-01"
    })
    assert response.status_code == 200
    assert len(response.json()) == 7


def test_get_pray(access_token):
    headers = {'Authorization': f'{access_token}'}
    response = requests.get('https://api.dev.uspray.kr/api/pray/184', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 7


def test_complete_pray(access_token):
    headers = {'Authorization': f'{access_token}'}
    response = requests.put('https://api.dev.uspray.kr/api/pray/complete/184', headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_put_pray(access_token):
    headers = {'Authorization': f'{access_token}'}
    response = requests.put('https://api.dev.uspray.kr/api/pray/my/184', headers=headers, json={
    "target": "배서현",
    "title": "Pytest 수정입니다",
    "deadline": "2024-08-01"
    })
    assert response.status_code == 200
    assert len(response.json()) == 7