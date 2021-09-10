# -*- coding: utf-8 -*-
import grequests
import json

request_list = []
info_list = []
json_dict = {}
headers = {
    'Referer': 'https://www.pixiv.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.31 Safari/537.36 Edg/94.0.992.14'
}

for pages in range(1, 11):
    request_list.append(grequests.get('https://www.pixiv.net/ranking.php?mode=daily&content=illust&p=%s&format=json'
                                      % (str(pages))))

response_list = grequests.map(request_list)

for response in response_list:
    info_list_part = []
    format_test_list = []
    content = response.json()['contents']
    for i in content:
        information = {'title': i['title'], 'illust_page_count': i['illust_page_count'], 'illust_id': i['illust_id'],
                       'user_name': i['user_name'], 'user_id': i['user_id'], 'width': i['width'], 'height': i['height'],
                       'rank': i['rank'], 'illust_upload_timestamp': i['illust_upload_timestamp'],
                       'illust_content_type': i['illust_content_type'],
                       'preview_url': i['url']}
        info_list_part.append(information)
        format_test_list.append(grequests.head(i['url'].replace('/c/240x480/img-master/', '/img-original/')
                                               .replace('_master1200', ''), headers=headers))

    format_response_list = grequests.map(format_test_list)
    for j in range(len(format_response_list)):
        if format_response_list[j].status_code == 404:
            info_list_part[j]['url'] = format_response_list[j].url.replace('.jpg', '.png')
        elif format_response_list[j].status_code == 200:
            info_list_part[j]['url'] = format_response_list[j].url
        else:
            print(info_list_part[j]['url'] + 'error')
    info_list = info_list + info_list_part

json_dict['contents'] = info_list
json_dict['date'] = response_list[0].json()['date']
with open('daily.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(json_dict, ensure_ascii=False))
