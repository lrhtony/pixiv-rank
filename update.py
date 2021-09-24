# -*- coding: utf-8 -*-
import sys
import time
import grequests
import requests
import json

USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
AUTH_TOKEN_URL = "https://oauth.secure.pixiv.net/auth/token"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"

json_dict = {}
progress_start_time = time.time()
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
    print(access_token)
except KeyError:
    print("error:")
    sys.exit(1)

# 获取排行榜部分
request_list = []
for pages in range(1, 11):
    request_list.append(grequests.get('https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%s&format=json'
                                      % (str(pages))))
response_list1 = grequests.map(request_list)

info_list1 = []
for response in response_list1:
    content = response.json()['contents']
    for i in content:
        information = {'title': i['title'], 'illust_id': i['illust_id'],
                       'user_name': i['user_name'], 'user_id': i['user_id'], 'width': i['width'], 'height': i['height'],
                       'rank': i['rank'], 'illust_upload_timestamp': i['illust_upload_timestamp']}
        info_list1.append(information)


# 获取图片信息部分
url = 'https://app-api.pixiv.net/v1/illust/detail'
headers = {
    'host': 'app-api.pixiv.net',
    'app-os': 'ios',
    'app-os-version': '14.6',
    'user-agent': 'PixivIOSApp/7.13.3 (iOS 14.6; iPhone13,2)',
    'Authorization': 'Bearer %s' % access_token,
    'accept-language': 'zh-cn'
}
remake = {}
while len(info_list1) != 0:
    request_list = []
    if len(info_list1) >= 100:
        end_search = 100
    else:
        end_search = len(info_list1)
    for i in info_list1[:end_search]:
        params = {
            'illust_id': i['illust_id']
        }
        request_list.append(grequests.get(url=url, params=params, headers=headers))
    response_list2 = grequests.map(request_list)
    delete_count = 0  # 设置默认前移0
    for response_num in range(len(response_list2)):  # 获取索引位置
        if response_list2[response_num].status_code == 200:
            info_list_index = response_num - delete_count  # response_list2在默认情况下与info_list1索引相对应，但删除元素后需前移
            illust = response_list2[response_num].json()['illust']  # 获取返回数据
            print(illust)
            info = info_list1[info_list_index]  # 继承原有数据
            sanity_level = illust['sanity_level']
            total_view = illust['total_view']
            total_bookmarks = illust['total_bookmarks']
            tags = illust['tags']
            page_count = illust['page_count']
            urls = []
            if page_count == 1:
                urls.append(illust['meta_single_page']['original_image_url'])
            else:
                meta_pages = illust['meta_pages']
                for i in meta_pages:
                    urls.append(i['image_urls']['original'])
            info['sanity_level'] = sanity_level
            info['tags'] = tags
            info['urls'] = urls
            remake[info['rank']] = info
            # 删除该元素
            del info_list1[info_list_index]
            delete_count += 1
    time.sleep(60)  # 每100个请求休息60秒

info_list2 = []
for i in range(1, len(remake)+1):
    info_list2.append(remake[i])
json_dict['contents'] = info_list2
json_dict['date'] = response_list1[0].json()['date']
with open('daily.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(json_dict, ensure_ascii=False))
