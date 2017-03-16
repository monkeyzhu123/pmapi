from flask import Flask, request
import requests
import re
from bs4 import BeautifulSoup
import random
from flask import jsonify, make_response

app = Flask(__name__)
app.debug = False


def select_user_agent(file_name='user-agents.txt'):
    user_agent_file = open(file_name)
    line = next(user_agent_file)
    for num, aline in enumerate(user_agent_file):
        if random.randrange(num + 2):
            continue
        line = aline.replace('\n', '')
    return line


@app.route('/')
def hello():
    return "Hello, world! - Flask"


@app.route('/get_true_url', methods=['GET'])
def get_true_url():
    url = request.args.get('url')
    if not url:
        response = {'status': 500, 'message': 'error'}
        return jsonify(response)
    headers = {
        'User-Agent': select_user_agent()
    }
    try:
        result = requests.head(url=url, headers=headers)
        url = result.headers['Location']
    except Exception, e:
        response = make_response(jsonify({'status': 500, 'message': e.message}))

    response = make_response(jsonify({
        'status': result.status_code,
        'true_url': url}))
    response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route('/get_baidu_url_content', methods=['GET'])
def get_baidu_url_content():
    url = request.args.get('url')
    headers = {
        'User-Agent': select_user_agent()
    }
    try:
        result = requests.get(url, headers=headers)
    except Exception, e:
        response = make_response(jsonify({'status': 500, 'message': e.message}))
        response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
        response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        return response

    soup = BeautifulSoup(result.content, 'html.parser')
    content = soup.find(id="content_left")
    b = re.sub(r'src=\"http://(i\d+?\.baidu\.com|bdimg.com|t\d+?\.baidu\.com).+?\"', '', str(content))
    response = make_response(jsonify({
        'status': result.status_code,
        'content': b}))
    response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


if __name__ == "__main__":
    app.run('0.0.0.0')
