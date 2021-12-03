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
    proxy_url = request.args.get('proxy')
    if proxy_url is None:  # 设置图片返回url的代理
        proxy_url = 'https://i.pixiv.re'
    proxy_url = parse.unquote(proxy_url)
    if pic_type != 'pc' and pic_type != 'phone' and pic_type != 'square' and pic_type != 'all':  # 图片样式
        pic_type = 'all'
    if enable_sex == 'True' or enable_sex == 'true' or enable_sex == '1':  # 处理那些sex=1的图片，决定是否屏蔽
        sex = 6
    else:
        sex = 2
    if return_format != 'json' and return_format != 'raw':  # 返回信息样式，raw则重定向到图片
        return_format = 'json'
    pic = random_picture(pic_type, sex, return_format, proxy_url)
    return pic


'''---------------------------------------------下面是主函数部分---------------------------------------------'''


def random_picture(pic_type: str, enable_sex: int, return_format: str, proxy_url: str):
    with open('daily.json', 'r', encoding='utf-8') as file:
        contents = json.loads(file.read())['contents']
    while True:
        content = random.choice(contents)
        pic_width = content['width']
        pic_height = content['height']
        ratio = pic_width / pic_height
        is_sex = content['sanity_level']
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
    urls = content['urls']
    random_url_index = random.choice(range(len(urls)))
    url = proxy_url + parse.urlparse(urls[random_url_index]).path
    backup_url = content['backup_urls'][random_url_index]
    tags = content['tags']
    tag_list = []
    for tag_information in tags:
        tag_name = tag_information['name']
        tag_translated_name = tag_information['translated_name']
        if tag_translated_name is not None:
            tag_list.append(tag_name + '/' + tag_translated_name)
        else:
            tag_list.append(tag_name)
    pic_info = {
        'illust_id': illust_id,
        'url': url,
        'backup_url': backup_url,
        'title': title,
        'rank': rank,
        'tags': tag_list,
        'user_id': user_id,
        'user_name': user_name,
        'upload_timestamp': illust_upload_timestamp
    }
    if return_format == 'json':
        return jsonify(pic_info), 200, {'Access-Control-Allow-Origin': '*'}
    elif return_format == 'raw':
        del pic_info['title']
        del pic_info['user_name']
        del pic_info['url']
        del pic_info['backup_url']
        del pic_info['tags']
        return redirect(url, 307), 307, pic_info


if __name__ == '__main__':
    app.debug = True
    app.run()
