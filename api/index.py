# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, redirect
import random
import json
import requests
import re
from urllib import parse

app = Flask(__name__)

'''---------------------------------------------下面是主入口---------------------------------------------'''


@app.route('/api/random', methods=['GET'])
def random_picture_route():
    pic_type = request.args.get('type')
    enable_sex = request.args.get('sex')
    return_format = request.args.get('format')
    proxy_url = request.args.get('proxy')
    if proxy_url is None:  # 设置图片返回url的代理
        proxy_url = 'https://i.pixiv.cat'
    proxy_url = parse.unquote(proxy_url)
    if pic_type != 'pc' and pic_type != 'phone' and pic_type != 'square' and pic_type != 'all':  # 图片样式
        pic_type = 'all'
    if enable_sex == 'True' or enable_sex == 'true' or enable_sex == '1':  # 处理那些sex=1的图片，决定是否屏蔽
        enable_sex = 1
    else:
        enable_sex = 0
    if return_format != 'json' and return_format != 'raw':  # 返回信息样式，raw则重定向到图片
        return_format = 'json'
    pic = random_picture(pic_type, enable_sex, return_format, proxy_url)
    return pic


@app.route('/api/proxy', methods=['GET'])
def illust_proxy():
    path = request.args.get('path')
    if path is not None:
        path = parse.unquote(path)
        hostname = parse.urlparse(path).hostname
        url_path = parse.urlparse(path).path
        if hostname == 'i.pximg.net' or hostname == 'i.pixiv.cat' or hostname is None:
            file_type = re.search('\.jpg', url_path)
            if file_type is not None:
                headers = {'Content-Type': 'image/jpeg'}
            else:
                headers = {'Content-Type': 'image/png'}
            result = proxy(url_path)
            return result, 200, headers
    return 'Error'


'''---------------------------------------------下面是主函数部分---------------------------------------------'''


def random_picture(pic_type: str, enable_sex: int, return_format: str, proxy_url: str):
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
    url = proxy_url + parse.urlparse(content['url']).path
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


def proxy(path: str):
    headers = {
        'Referer': 'https://www.pixiv.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.0.0 Safari/537.36 '
    }
    content = requests.get('https://i.pximg.net'+path, headers=headers).content
    return content


if __name__ == '__main__':
    app.debug = True
    app.run()
