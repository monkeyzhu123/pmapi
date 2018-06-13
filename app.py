# coding:utf8
from flask import Flask, request
import requests
import re
from bs4 import BeautifulSoup
import random
from flask import jsonify, make_response
import urllib2
from lxml import etree
import os
import linecache

app = Flask(__name__)
app.debug = True


def clean_str_for_line_break(pre_str):
    while True:
        if pre_str.startswith(("\n", "\r", " ", "\t")) or pre_str.endswith(("\n", "\r", " ", "\t")):
            pre_str = pre_str.strip(" ").strip("\n").strip("\r").strip("\t")
        else:
            break
    return pre_str


def select_user_agent(file_name='user-agents.txt'):
    with open(file_name) as f:
        total_num = sum(1 for _ in f)
    return linecache.getline(file_name, random.randint(1, total_num)).replace('\n', '')


def create_request_cookie(cookie_file):
    cookies = {}
    with open(cookie_file, 'r') as f:
        for line in f.readline().split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value
    return cookies


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
    # print url
    search_engine_type = request.args.get('search_engine_type')
    # print search_engine_type
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

    if search_engine_type == "sogou":
        headers['Host'] = "www.sogou.com"
        headers['Referer'] = "http://www.sogou.com/"
        result = requests.get(url + "&num=30", headers=headers)
        selector = etree.HTML(result.content)
        for current_xpath, title_xpath in zip(selector.xpath('//div[@class="results"]//div[@class="fb"]'),
                                              selector.xpath('//div[@class="results"]//h3')):
            count_timer = count_timer + 1
            content_dict = {}
            re_rule = 'a/@href'
            try:
                pre_url = current_xpath.xpath(re_rule)[0]
            except IndexError:
                continue
            title = "".join(title_xpath.xpath('a//text()'))
            true_url = urllib2.unquote(re.findall(r"url=(.+?)&", pre_url)[0])
            content_dict['true_url'] = true_url
            content_dict['ranking'] = count_timer
            content_dict['title'] = title
            content_list.append(content_dict)
    elif search_engine_type == "qihu":
        headers['Host'] = "www.so.com"
        for page in range(1, 4):
            try:
                result = requests.get(url + "&pn=" + str(page), headers=headers)
                selector = etree.HTML(result.content)
                for current_xpath in selector.xpath('//ul[@class="result"]/li[@class="res-list"]'):
                    try:
                        count_timer = count_timer + 1
                        content_dict = {}
                        re_rule = 'h3/a/@data-url'
                        title_rule = 'h3/a//text()'

                        # pre_url = current_xpath.xpath(re_rule)[0]
                        true_url = current_xpath.xpath(re_rule)[0]
                        # true_url = urllib2.unquote(re.findall(r"url=(.+?)&", pre_url)[0])

                        content_dict['true_url'] = true_url
                        content_dict['ranking'] = count_timer
                        content_dict['title'] = "".join(current_xpath.xpath(title_rule))
                        content_list.append(content_dict)
                    except IndexError:
                        # news parts
                        news_part = current_xpath.xpath('*//p[contains(@class, "mh-position") or @class="gclearfix"]')
                        for i in news_part:
                            pre_url = "".join(i.xpath('a/@href'))
                            title = "".join(i.xpath('a//text()'))
                            content_dict = {}
                            try:
                                true_url = urllib2.unquote(re.findall(r"url=(.+?)&", pre_url)[0])
                            except IndexError:
                                continue
                            content_dict['true_url'] = true_url
                            content_dict['ranking'] = count_timer
                            content_dict['title'] = title
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
                    re_rule = 'a/@href'
                    content_dict = {}
                    pre_url = next_xpath.xpath(re_rule)[0]
                    title = "".join(next_xpath.xpath('a//text()'))
                    # type 2 is baidu news search result
                    content_dict['type'] = 2
                    content_dict['baidu_index_url'] = pre_url
                    content_dict['ranking'] = current_xpath.xpath('@id')[0]
                    content_dict['title'] = clean_str_for_line_break(title)
                    try:
                        result = requests.head(url=pre_url, headers=headers)
                        url = result.headers['Location']
                    except:
                        continue
                    content_dict['domain'] = url
                    content_list.append(content_dict)
            elif current_xpath.xpath('@tpl')[0] == "se_com_default":

                re_rule = 'h3/a/@href'
                content_dict = {}
                pre_url = current_xpath.xpath(re_rule)[0]
                title = "".join(current_xpath.xpath('h3/a//text()'))
                # type 1 is normal search result
                content_dict['type'] = 1
                content_dict['baidu_index_url'] = pre_url
                content_dict['ranking'] = current_xpath.xpath('@id')[0]
                content_dict['title'] = title
                try:
                    content_dict['domain'] = \
                        "".join(current_xpath.xpath('div//a[@class="c-showurl"]//text()')).split("/")[0]
                except:
                    content_dict['domain'] = "".join(current_xpath.xpath('div//a[@class="c-showurl"]//text()'))
                content_list.append(content_dict)
    elif search_engine_type == "sm":
        headers['User-Agent'] = select_user_agent(file_name='user_agent_for_mobile.txt')
        headers['Host'] = "yz.m.sm.cn"
        if os.path.exists('sm_cookie'):
            try:
                cookies = create_request_cookie('sm_cookie')
                result = requests.get(url + "&num=20", headers=headers, cookies=cookies)
            except:
                result = requests.get(url + "&num=20", headers=headers)

            if len(result.content) < 200:
                with open('sm_cookie', 'wb') as f:
                    f.write(re.findall(r'cookie=\"(.+?)\"', result.content)[0])
                cookies = create_request_cookie('sm_cookie')
                result = requests.get(url + "&num=20", headers=headers, cookies=cookies)

        else:
            result = requests.get(url + "&num=20", headers=headers)
            if len(result.content) < 200:
                with open('sm_cookie', 'wb') as f:
                    f.write(re.findall(r'cookie=\"(.+?)\"', result.content)[0])
                cookies = create_request_cookie('sm_cookie')
                result = requests.get(url + "&num=20", headers=headers, cookies=cookies)

        selector = etree.HTML(result.content.decode('utf-8'))
        for current_xpath in selector.xpath('//div[@class="article ali_row"]'):
            count_timer = count_timer + 1
            content_dict = {}
            url_rule = 'h2/a/@href'
            title_rule = 'h2/a//text()'
            try:
                pre_url = current_xpath.xpath(url_rule)[0]
                title = "".join(current_xpath.xpath(title_rule))
            except IndexError:
                continue

            content_dict['true_url'] = pre_url
            content_dict['ranking'] = count_timer
            content_dict['title'] = title
            content_list.append(content_dict)
    elif search_engine_type == "m_baidu":
        headers['User-Agent'] = select_user_agent(file_name='user_agent_for_mobile.txt')
        headers['Host'] = "m.baidu.com"
        for pn in range(0, 21, 10):
            result = requests.get(url + "&pn=" + str(pn), headers=headers)
            selector = etree.HTML(result.content)
            for current_xpath in selector.xpath('//div[@tpl="www_normal"]'):
                content_dict = {}
                title = "".join(current_xpath.xpath('div[@class="c-container"]/a/h3//text()'))
                # type 1 is normal search result
                content_dict['ranking'] = str(int(current_xpath.xpath('@order')[0]) + pn)
                content_dict['title'] = title
                content_dict['true_url'] = eval(current_xpath.xpath('@data-log')[0])['mu']
                content_list.append(content_dict)
    response = make_response(jsonify({'status': 200, 'content': content_list}))
    response.headers['Access-Control-Allow-Origin'] = 'http://pm.yunwangke.com'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response


@app.route('/check_article_collected', methods=['GET'])
def check_article_collected():
    url = request.args.get('url')
    headers = {
        'User-Agent': 'Opera/9.80 (Android 4.1.2; Linux; Opera Mobi/ADR-1305251841) Presto/2.11.355 Version/12.10',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.baidu.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
    }
    article_link = "https://www.baidu.com/s?ie=utf-8&wd=site%3A({0})%20inurl%3A/{1}".format(url.split("/")[2],
                                                                                            "/".join(
                                                                                                url.split("/")[3:]))
    # https://www.baidu.com/s?ie=utf-8&wd=site%3A(e.chengdu.cn)%20inurl%3A/syxw/26740579.html
    result = requests.get(url=article_link, headers=headers)
    soup = BeautifulSoup(result.content, 'html.parser')
    response = {}
    if result.status_code == 200:
        if soup.find(attrs={'id': 'content_left'}):
            response['title'] = re.sub(r'\d{4}.*', '', soup.find(id="1").h3.a.get_text())
            response['status'] = 1
            response['info'] = u"已收录"
        # class is python build-in key word,use attrs avoid this
        elif soup.find(attrs={'class': 'content_none'}):
            response['status'] = 0
            response['info'] = u"未收录1"
        else:
            # with open('disable_user_agent.txt', 'a+') as f:
            #     f.write(headers['User-Agent'] + "\n")
            print result.status_code, headers['User-Agent']
            response['status'] = 2
            response['info'] = u"未收录2"
    else:
        print result.status_code, headers['User-Agent']
        response['status'] = 3
        response['info'] = u"查询错误"

    response = make_response(jsonify(response))
    return response


if __name__ == "__main__":
    app.run('0.0.0.0')
