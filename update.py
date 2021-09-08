# -*- coding: utf-8 -*-
import grequests
import json

request_list = []
info_list = []
json_dict = {}
for pages in range(1, 11):
    request_list.append(grequests.get('https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%s&format=json'
                                      % (str(pages))))

response_list = grequests.map(request_list)

for response in response_list:
    content = response.json()['contents']
    for i in content:
        information = {'title': i['title'], 'illust_page_count': i['illust_page_count'], 'illust_id': i['illust_id'],
                       'user_name': i['user_name'], 'user_id': i['user_id'], 'width': i['width'], 'height': i['height'],
                       'rank': i['rank'], 'illust_upload_timestamp': i['illust_upload_timestamp'],
                       'illust_content_type': i['illust_content_type'],
                       'url': i['url']}
        info_list.append(information)


json_dict['contents'] = info_list
json_dict['date'] = response_list[0].json()['date']
with open('daily.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(json_dict, ensure_ascii=False))
