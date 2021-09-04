# -*- coding: utf-8 -*-
from flask import Flask, request

app = Flask(__name__)


@app.route('/api/random')
def main():
    pass


if __name__ == '__main__':
    app.debug = True
    app.run()
