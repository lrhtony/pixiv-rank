# -*- coding: utf-8 -*-
from flask import Flask, request
import json

app = Flask(__name__)

'''Here is the routes part!'''


@app.route('/api/random', methods=['GET'])
def random_picture_route():
    pic_type = request.args.get('type')
    enable_sex = request.args.get('sex')
    if pic_type != 'pc' or pic_type != 'phone' or pic_type != 'square' or pic_type != 'all':
        pic_type = 'all'
    if enable_sex == 'True':
        enable_sex = True
    else:
        enable_sex = False
    a = random_picture(pic_type, enable_sex)
    return a


'''Here is the logical part!'''


def random_picture(pic_type: str, enable_sex: bool):
    with open('../daily.json', 'r', encoding='utf-8') as daily_file:
        contents = json.loads(daily_file.read())['contents']
    return str(contents[0])


if __name__ == '__main__':
    app.debug = True
    app.run()
