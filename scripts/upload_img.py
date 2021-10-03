# -*- coding: utf-8 -*-
import grequests
import json
import sys
import os
import time

'''
此脚本原理主要是将请求列表和总列表的索引对应起来，获取完数据后根据索引将链接填回相应位置
写完后自己就看不懂了，反正能跑就行，凑合着看吧
通过异步请求的方式可以将原来1个小时的过程缩短至？分钟（没办法毕竟是要下载并上传至少500个的大文件）
'''


start_time = time.time()

#with open('token.json', 'r', encoding='utf-8') as access_file:
    #access_token = json.loads(access_file.read())['access_token']
access_token = sys.argv[1]

with open('../daily.json', 'r', encoding='utf-8') as rank_file:
    daily_rank = json.loads(rank_file.read())
    daily_list = daily_rank['contents']


def exception_handler(request, exception):
    print("Request failed")


img_request_headers = {
        'Referer': 'https://www.pixiv.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/94.0.4606.31 Safari/537.36 Edg/94.0.992.14'
    }
upload_request_data = {
    'biz': 'draw',
    'pos': '0',
    'access_key': access_token,
    'category': 'daily'
}
daily_list_index_to_run = []
img_request_list = []
upload_request_list = []
request_list_index = 0
index_map = {}
step = 20  # 越大越快，但内存占用更大，更容易失败
for i in range(step-1, len(daily_list), step):
    daily_list_index_to_run.append(i)
daily_list_index_to_run.append(len(daily_list)-1)

for daily_list_index in range(len(daily_list)):
    img_urls = daily_list[daily_list_index]['urls']
    for img_url in img_urls:
        img_request_list.append(grequests.get(img_url, headers=img_request_headers))
        index_map[request_list_index] = daily_list_index
        request_list_index += 1
    if daily_list_index in daily_list_index_to_run:
        print(daily_list_index)
        img_response_list = grequests.map(img_request_list, exception_handler=exception_handler)
        print('开始上传')
        for img_response in img_response_list:
            img = img_response.content
            filename = os.path.basename(img_response.url)
            files = {'file_up': (filename, img)}
            upload_request_list.append(grequests.post('https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs',
                                                      data=upload_request_data, files=files))
        upload_response_list = grequests.map(upload_request_list)
        for upload_response_list_index in range(len(upload_response_list)):
            try:
                response = upload_response_list[upload_response_list_index]
                response_json = response.json()
                backup_url = response_json['data']['image_url'].replace('http://', 'https://')
            except json.decoder.JSONDecodeError:
                print('File maybe too large')
                backup_url = None
            find_daily_list_index = index_map[upload_response_list_index]
            information = daily_list[find_daily_list_index]
            try:
                print(backup_url)
                information['backup_urls'].append(backup_url)
            except KeyError:
                backup_urls = [backup_url]
                information['backup_urls'] = backup_urls
            daily_list[find_daily_list_index] = information
        img_request_list = []
        upload_request_list = []
        request_list_index = 0
        index_map = {}

with open('daily.json', 'w', encoding='utf-8') as rank_file_new:
    daily_rank['contents'] = daily_list
    rank_file_new.write(json.dumps(daily_rank, ensure_ascii=False))

end_time = time.time()
print('用时：', end_time-start_time)
