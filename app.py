# coding:utf8
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


def get_id_content_left_for_baidu_search_page(url=None, headers=None):
    '''    获得百度搜索结果页中id=content_left的网页内容    '''
    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.content, 'html.parser')
    content = soup.find(id="content_left")
    post_content = re.sub(r'src=\"http://(i\d+?\.baidu\.com|bdimg.com|t\d+?\.baidu\.com).+?\"', '', str(content))
    return result.status_code, post_content


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
        response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
        response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        return response

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
    if not url:
        response = {'status': 500, 'message': 'error'}
        return jsonify(response)
    headers = {
        'User-Agent': select_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'BAIDUID=FB798CC753E51492B152DF8749E3D83A:FG=1; PSTM=1489731864; BIDUPSID=5D21609712C498AB54C72D277B060DD6; B64_BOT=1; BD_HOME=0; BD_UPN=12314353; H_PS_645EC=36fdXIOuwppojFeEvyNP2vXM1litJoWrgjCHs4cJOqBz0%2FDbOWP4aLpbb94; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BD_CK_SAM=1; PSINO=3; BDSVRTM=53; H_PS_PSSID=22162_1425_21114_22035_22176_20927',
        'Host': 'www.baidu.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
    }
    try:
        status_code, content = get_id_content_left_for_baidu_search_page(url, headers)
        if len(content) == 4:
            raise ValueError
        response = make_response(jsonify({'status': status_code, 'content': content}))
    except Exception, e:
        try:
            url = re.sub(r'^https://', 'http://', url)
            status_code, content = get_id_content_left_for_baidu_search_page(url, headers)
            response = make_response(jsonify({'status': status_code, 'content': content}))
        except Exception, e:
            response = make_response(jsonify({'status': 500, 'message': e.message}))
    response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


if __name__ == "__main__":
    app.run('0.0.0.0')
