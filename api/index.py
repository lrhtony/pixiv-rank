# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, redirect
import random
import json
from urllib import parse

app = Flask(__name__)

'''---------------------------------------------下面是主入口---------------------------------------------'''


@app.route('/api/random', methods=['GET'])
def random_picture_route():
    pic_type = request.args.get('type')
    enable_sex = request.args.get('sex')
    return_format = request.args.get('format')
    proxy = request.args.get('proxy')
    if proxy is None:  # 设置图片返回url的代理
        proxy = 'https://i.pixiv.cat/'
    proxy = parse.unquote(proxy)
    if pic_type != 'pc' and pic_type != 'phone' and pic_type != 'square' and pic_type != 'all':  # 图片样式
        pic_type = 'all'
    if enable_sex == 'True' or enable_sex == 'true' or enable_sex == '1':  # 处理那些sex=1的图片，决定是否屏蔽
        enable_sex = 1
    else:
        enable_sex = 0
    if return_format != 'json' and return_format != 'raw':  # 返回信息样式，raw则重定向到图片
        return_format = 'json'
    pic = random_picture(pic_type, enable_sex, return_format, proxy)
    return pic

@app.route('/api/proxy', methods=['GET'])
def illust_proxy():
    return 'test_success'

'''---------------------------------------------下面是主函数部分---------------------------------------------'''


def random_picture(pic_type: str, enable_sex: int, return_format: str, proxy: str):
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
    illust_upload_timestamp = content['illust_upload_timestamp']
    rank = content['rank']
    title = content['title']
    user_id = content['user_id']
    user_name = content['user_name']
    url = content['url'].replace('https://i.pximg.net/', proxy)
    pic_info = {
        'illust_id': illust_id,
        'url': url,
        'title': title,
        'rank': rank,
        'user_id': user_id,
        'user_name': user_name,
        'upload_timestamp': illust_upload_timestamp
    }
    if return_format == 'json':
        return jsonify(pic_info)
    elif return_format == 'raw':
        del pic_info['title']
        del pic_info['user_name']
        del pic_info['url']
        return redirect(url, 307), 307, pic_info


if __name__ == '__main__':
    app.debug = True
    app.run()
