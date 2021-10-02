# -*- coding: utf-8 -*-
import requests
import hashlib
import sys
import time
import json
from base64 import b64encode
from nacl import encoding, public

STATUS = 'github'


def refresh(bili_access_token: str, bili_refresh_token: str):
    url = "https://passport.bilibili.com/api/v2/oauth2/refresh_token"
    post_data = {
        'appkey': 'ae57252b0c09105d',
        'access_token': bili_access_token,
        'access_key': bili_access_token,
        'refresh_token': bili_refresh_token,
        'ts': int(time.time()),
    }
    post_data['sign'] = _sign_dict(post_data, 'c75875c596a69eb55bd119e74b07cfe3')
    response = requests.post(url, data=post_data).json()
    return response['data']['token_info']['access_token'], response['data']['token_info']['refresh_token']


def _sign_dict(data: dict, app_secret: str):
    data_str = []
    keys = list(data.keys())
    keys.sort()
    for key in keys:
        data_str.append("{}={}".format(key, data[key]))
    data_str = "&".join(data_str)
    data_str = data_str + app_secret
    return hashlib.md5(data_str.encode("utf-8")).hexdigest()


def get_public_key():
    url = 'https://api.github.com/repos/lrhtony/pixiv-rank/actions/secrets/public-key'
    headers = {'Authorization': 'token ' + GH_TOKEN,
               "Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers).json()
    return response['key_id'], response['key']


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def update_secret(bili_access_token: str, bili_refresh_token: str):
    key_id, public_key = get_public_key()
    access_token_encrypt = encrypt(public_key, bili_access_token)
    refresh_token_encrypt = encrypt(public_key, bili_refresh_token)
    url1 = 'https://api.github.com/repos/lrhtony/pixiv-rank/actions/secrets/BILI_ACCESS_TOKEN'
    url2 = 'https://api.github.com/repos/lrhtony/pixiv-rank/actions/secrets/BILI_REFRESH_TOKEN'
    headers = {'Authorization': 'token ' + GH_TOKEN,
               "Accept": "application/vnd.github.v3+json"}
    access_token_data = {
        'encrypted_value': access_token_encrypt,
        'key_id': key_id
    }
    refresh_token_data = {
        'encrypted_value': refresh_token_encrypt,
        'key_id': key_id
    }
    requests.put(url1, data=json.dumps(access_token_data), headers=headers)
    requests.put(url2, data=json.dumps(refresh_token_data), headers=headers)


if __name__ == '__main__':
    if STATUS == 'github':
        access_token = sys.argv[1]
        refresh_token = sys.argv[2]
        GH_TOKEN = sys.argv[3]
    else:
        with open('token.json', 'r', encoding='utf-8') as file:
            config = json.loads(file.read())
            access_token = config['access_token']
            refresh_token = config['refresh_token']
        GH_TOKEN = ''

    access_token, refresh_token = refresh(access_token, refresh_token)
    if STATUS == 'test':
        with open('token.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps({
                'access_token': access_token,
                'refresh_token': refresh_token
            }))
        update_secret(access_token, refresh_token)
    if STATUS == 'github':
        update_secret(access_token, refresh_token)
