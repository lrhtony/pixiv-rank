# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import requests
import random
import json

app = Flask(__name__)

'''Here is the routes part!'''


@app.route('/api/random-pic', methods=['GET'])
def random_picture_route():
    pic_type = request.args.get('type')
    enable_sex = request.args.get('sex')
    if pic_type != 'pc' and pic_type != 'phone' and pic_type != 'square' and pic_type != 'all':
        pic_type = 'all'
    if enable_sex == 'True' or enable_sex == 'true' or enable_sex == '1':
        enable_sex = 1
    else:
        enable_sex = 0
    pic_info = random_picture(pic_type, enable_sex)
    return jsonify(pic_info)


'''Here is the logical part!'''


def random_picture(pic_type: str, enable_sex: int):
    with open('daily.json', 'r', encoding='utf-8') as file:
        contents = json.loads(file.read())['contents']
    while True:
        content = random.choice(contents)
        pic_width = content['width']
        pic_height = content['height']
        ratio = pic_width / pic_height
        is_sex = content['illust_content_type']['sexual']
        if ratio < 0.85 and (pic_type == 'phone' or pic_type == 'all') and enable_sex >= is_sex:
            break
        elif ratio > 1.25 and (pic_type == 'pc' or pic_type == 'all') and enable_sex >= is_sex:
            break
        elif 0.85 <= ratio <= 1.25 and (pic_type == 'square' or pic_type == 'all') and enable_sex >= is_sex:
            break

    illust_id = content['illust_id']
    illust_page_count = int(content['illust_page_count'])
    illust_upload_timestamp = content['illust_upload_timestamp']
    rank = content['rank']
    title = content['title']
    user_id = content['user_id']
    user_name = content['user_name']
    url = content['url'].replace('i.pximg.net', 'i.pixiv.cat')
    pic_info = {
        'illust_id': illust_id,
        'url': url,
        'title': title,
        'rank': rank,
        'user_id': user_id,
        'user_name': user_name,
        'upload_timestamp': illust_upload_timestamp
    }
    return pic_info


if __name__ == '__main__':
    app.debug = True
    app.run()
