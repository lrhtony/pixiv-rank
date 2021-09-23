# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()
import sys
import time
from pixivpy3 import *
import grequests
import requests
import json

USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"

json_dict = {}

refresh_token = sys.argv[1]
# 登录部分
response = requests.post(
    AUTH_TOKEN_URL,
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "include_policy": "true",
        "refresh_token": refresh_token,
    },
    headers={"User-Agent": USER_AGENT},
)
data = response.json()

try:
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
except KeyError:
    print("error:")
    sys.exit(1)

# 获取排行榜部分
request_list = []
for pages in range(1, 11):
    request_list.append(grequests.get('https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%s&format=json'
                                      % (str(pages))))
response_list = grequests.map(request_list)

info_list1 = []
for response in response_list:
    content = response.json()['contents']
    for i in content:
        information = {'title': i['title'], 'illust_id': i['illust_id'],
                       'user_name': i['user_name'], 'user_id': i['user_id'], 'width': i['width'], 'height': i['height'],
                       'rank': i['rank'], 'illust_upload_timestamp': i['illust_upload_timestamp']}
        info_list1.append(information)


# 获取图片信息部分
times = 0
info_list2 = []
api = AppPixivAPI()
api.set_auth(access_token, refresh_token)
for info in info_list1:
    times += 1
    print(times)
    illust_id = info['illust_id']
    error_times = 0
    while error_times <= 5:
        json_result = api.illust_detail(illust_id)
        illust = json_result.illust
        if illust is not None:
            break
        else:
            error_times += 1
            print('error:'+str(error_times))
            time.sleep(60)
    sanity_level = illust['sanity_level']
    total_view = illust['total_view']
    total_bookmarks = illust['total_bookmarks']
    tag = illust['tags']
    tags = []
    for i in tag:
        tags.append(i['name'])
    page_count = illust['page_count']
    urls = []
    if page_count == 1:
        urls.append(illust['meta_single_page']['original_image_url'])
    else:
        meta_pages = illust['meta_pages']
        for i in meta_pages:
            urls.append(i['image_urls']['original'])
    info['sanity_level'] = sanity_level
    info['total_view'] = total_view
    info['total_bookmarks'] = total_bookmarks
    info['tags'] = tags
    info['urls'] = urls
    info_list2.append(info)

json_dict['contents'] = info_list2
json_dict['date'] = response_list[0].json()['date']
with open('daily.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(json_dict, ensure_ascii=False))
