# coding:utf8
from flask import Flask, request
import requests
import re
from bs4 import BeautifulSoup
import random
from flask import jsonify, make_response
import urllib2
from lxml import etree
import time


app = Flask(__name__)
app.debug = False


def clean_str_for_line_break(pre_str):
    while True:
        if pre_str.startswith(("\n", "\r", " ", "\t")) or pre_str.endswith(("\n", "\r", " ", "\t")):
            pre_str = pre_str.strip(" ").strip("\n").strip("\r").strip("\t")
        else:
            break
    return pre_str


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
    if not content:
        raise ValueError
    post_content = re.sub(r'src=\"http://(i\d+?\.baidu\.com|bdimg.com|t\d+?\.baidu\.com|ss\d+?\.baidu\.com).+?\"', '',
                          str(content))
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
        'Host': 'www.baidu.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
    }
    try:
        status_code, content = get_id_content_left_for_baidu_search_page(url, headers)
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


@app.route('/get_ranking_and_url', methods=['GET', 'POST'])
def get_ranking_and_url():
    url = request.args.get('url')
    print url
    search_engine_type = request.args.get('search_engine_type')
    print search_engine_type
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
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
    }
    content_list = []
    count_timer = 0
    news_count_timer = 100

    if search_engine_type == "sogou":
        time.sleep(1)
        headers['Host'] = "www.sogou.com"
        headers['Cookie'] = '''	
SUID=88E0D8AB80430E0A00000000522932D8; SUV=1378431703727616; SMYUV=1378431713141522; ssuid=9930978344
; pgv_pvi=2056938496; IPLOC=CN5101; sct=22; usid=_oy9Hm8LczK4fWe3; wuid=AAEaBy2eEgAAAAqSNjIEzgMAkwA=
; CXID=FEF28FEB003EC0A942171FC383D41B88; SNUID=A8C13E1CABAEE596BCD57F1FABE68C0D; ad=U2VLSkllll2YE4yVlllllV6JzSylllllHISrlZllllwllllllZlll5
@@@@@@@@@@; ABTEST=0|1494494327|v17; browerV=2; osV=1; PHPSESSID=s9hmiegfgvtrcfdon66pnuce05; SUIR=2E46B89A2D286DF59DD38DB42DDFCE70
; seccodeRight=success; successCount=1|Thu, 11 May 2017 09:24:44 GMT; ld=Pkllllllll2BVjhflllllV6UanolllllHISrlZllllYllllljZGll5
@@@@@@@@@@; taspeed=taspeedexist; pgv_si=s1630076928; sst0=325; LSTMV=666%2C418; LCLKINT=693'''
        result = requests.get(url + "&num=30", headers=headers)
        print result.content
        print result.url
        selector = etree.HTML(result.content)
        for current_xpath,title_xpath in zip(selector.xpath('//div[@class="results"]//div[@class="fb"]'),selector.xpath('//div[@class="results"]//h3')):
            count_timer = count_timer + 1
            content_dict = {}
            re_rule = 'a/@href'
            pre_url = current_xpath.xpath(re_rule)[0]
            title = "".join(title_xpath.xpath('a//text()'))
            true_url = urllib2.unquote(re.findall(r"url=(.+?)&", pre_url)[0])
            content_dict['true_url'] = true_url
            content_dict['ranking'] = count_timer
            content_dict['title'] = title
            content_list.append(content_dict)
    elif search_engine_type == "360so":
        headers['Host'] = "www.so.com"
        for page in range(1, 4):
            try:
                result = requests.get(url + "&pn=" + str(page), headers=headers)
                print result.url
                selector = etree.HTML(result.content)
                for current_xpath in selector.xpath('//ul[@class="result"]/li[@class="res-list"]'):
                    print "li"
                    try:
                        count_timer = count_timer + 1
                        content_dict = {}
                        re_rule = 'h3/a/@href'
                        title_rule = 'h3/a//text()'
                        pre_url = current_xpath.xpath(re_rule)[0]
                        true_url = urllib2.unquote(re.findall(r"url=(.+?)&", pre_url)[0])
                        content_dict['true_url'] = true_url
                        content_dict['ranking'] = count_timer
                        content_dict['title'] = "".join(current_xpath.xpath(title_rule))
                        content_list.append(content_dict)
                    except IndexError:
                        for pre_url,title in zip(current_xpath.xpath('*//p/a/@href'),current_xpath.xpath('*//p/a//text()')):
                            content_dict = {}
                            print pre_url
                            try:
                                true_url = urllib2.unquote(re.findall(r"url=(.+?)&", pre_url)[0])
                            except IndexError:
                                continue
                            content_dict['true_url'] = true_url
                            content_dict['ranking'] = count_timer
                            content_dict['title'] = "".join(title)
                            content_list.append(content_dict)
            except Exception, e:
                print e.message
                continue
    elif search_engine_type == "baidu":
        headers['Host'] = "www.baidu.com"
        result = requests.get(url + "&rn=30", headers=headers)
        selector = etree.HTML(result.content)
        for current_xpath in selector.xpath(
                '//div[@id="content_left"]/div[contains(@tpl, "se_com_default") or contains(@tpl, "sp_realtime_bigpic5")]'):
            if current_xpath.xpath('@tpl')[0] == "sp_realtime_bigpic5":
                for next_xpath in current_xpath.xpath('*//div[@class="c-gap-bottom-small" or @class="c-row"]'):
                    print "next_xpath"
                    re_rule = 'a/@href'
                    content_dict = {}
                    pre_url = next_xpath.xpath(re_rule)[0]
                    title = "".join(next_xpath.xpath('a//text()'))
                    content_dict['true_url'] = pre_url
                    content_dict['ranking'] = current_xpath.xpath('@id')[0]
                    content_dict['title'] = clean_str_for_line_break(title)
                    content_list.append(content_dict)
            elif current_xpath.xpath('@tpl')[0] == "se_com_default":
                re_rule = 'h3/a/@href'
                content_dict = {}
                pre_url = current_xpath.xpath(re_rule)[0]
                title = "".join(current_xpath.xpath('h3/a//text()'))
                content_dict['true_url'] = pre_url
                content_dict['ranking'] = current_xpath.xpath('@id')[0]
                content_dict['title'] = title
                content_list.append(content_dict)
    response = make_response(jsonify({'status': 200, 'content': content_list}))
    response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


if __name__ == "__main__":
    app.run('0.0.0.0')
