# -*- coding: utf-8 -*-
# @Time      :2019/3/22 下午1:28
# @Author    :tack
# @Site      :
# @File      :IpSpider.py
# @Software  :PyCharm

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from app.models import Ip
from app.util.log import *


def validate_ip(ip):
    # 验证ip是否可用
    proxies = {"http": "http://%s:%s" % (ip.ip, ip.port)}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'User - Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    }
    res = False
    try:
        r = requests.get(url='http://www.ip138.com/', headers=headers,
                         timeout=5, proxies=proxies)
        if r.ok:
            res = True
    except Exception as e:
        pass

    return res


# IP爬虫，从不同ip网站获取ip并验证一个可用的
class IpSpdier(object):
    domains = ['xicidaili.com', 'kuaidaili.com', '31f.cn', '89ip.cn', 'all']
    ip_num = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    }

    def __init__(self, domain='all'):
        if domain not in self.domains:
            raise SyntaxError("目前还没实现该ip网站爬虫")
        self.domain = domain

    def crawl(self, ip_num):
        """
        爬取
        :param ip_num: 需要爬取的ip数
        :return:
        """
        self.ip_num = ip_num
        if self.domain == 'xicidaili.com':
            self.__crawl_xicidaili()
        if self.domain == 'kuaidaili.com':
            self.__crawl_kuaidaili()
        if self.domain == '31f.cn':
            self.__crawl_31f()
        if self.domain == '89ip.cn':
            self.__crawl_89ip()
        if self.domain == 'all':
            funcs = [self.__crawl_89ip, self.__crawl_31f, self.__crawl_xicidaili, self.__crawl_kuaidaili]
            crawled_num = 0
            for func in funcs:
                if crawled_num < ip_num:
                    crawled_num += func()

    def __crawl_xicidaili(self):
        page = 1
        crawl_num = 0
        while crawl_num < self.ip_num:
            url = 'https://www.xicidaili.com/wn/%d' % page
            ips = self.__get_by_url(url, {"ip": 1, "port": 2, "address": 3, "ip_type": 4})
            if ips is None:
                INFO('获取url失败')
                continue
            if ips == []:
                INFO("爬取结束....")
                break

            saved_num = self.__save_into_db(ips)
            crawl_num += saved_num
            INFO("已保存%d条" % crawl_num)
            page += 1
        INFO('完成爬取 __crawl_xicidaili %d' % crawl_num)
        return crawl_num

    def __crawl_kuaidaili(self):
        page = 1
        crawl_num = 0
        while crawl_num < self.ip_num:
            url = 'https://www.kuaidaili.com/free/inha/%d/' % page
            ips = self.__get_by_url(url, {"ip": 0, "port": 1, "address": 4, "ip_type": 2})
            if ips is None:
                INFO('获取url失败')
                continue
            if ips == []:
                INFO("爬取结束....")
                break

            saved_num = self.__save_into_db(ips)
            crawl_num += saved_num
            INFO("已保存%d条" % crawl_num)
            page += 1
        INFO('完成爬取 __crawl_kuaidaili %d' % crawl_num)
        return crawl_num

    def __crawl_31f(self):
        page = 1
        crawl_num = 0
        # while crawl_num < self.ip_num:
        url = 'http://31f.cn/http-proxy/'
        ips = self.__get_by_url(url, {"ip": 1, "port": 2, "address": 3, "ip_type": 6})
        if ips is None:
            INFO('获取url失败')
        if ips == []:
            INFO("爬取结束....")

        saved_num = self.__save_into_db(ips)
        crawl_num += saved_num
        INFO("已保存%d条" % crawl_num)
        page += 1
        INFO('完成爬取 __crawl_31f %d' % crawl_num)
        return crawl_num

    def __crawl_89ip(self):
        page = 1
        crawl_num = 0
        while crawl_num < self.ip_num:
            url = 'http://www.89ip.cn/index_%d.html' % page
            ips = self.__get_by_url(url, {"ip": 0, "port": 1, "address": 2, "ip_type": 5})
            if ips is None:
                INFO('获取url失败')
                continue

            if ips == []:
                INFO("爬取结束....")
                break

            saved_num = self.__save_into_db(ips)
            crawl_num += saved_num
            INFO("已保存%d条" % crawl_num)
            page += 1
        INFO('完成爬取 __crawl_kuaidaili %d' % crawl_num)
        return crawl_num

    def __get_by_url(self, url, dict):
        try:
            r = requests.get(url, headers=self.headers, verify=True).content
        except Exception as e:
            ERROR(str(e))
            return None

        ip_list = []
        selector = BeautifulSoup(r, 'lxml')
        trs = selector.select("tr")

        ip_list = []
        if len(trs) < 2:
            return []
        for tr in trs:
            tds = tr.select('td')
            ip = Ip()
            for i in range(len(tds)):
                if i == dict["ip"]:
                    ip.ip = tds[i].get_text().strip()
                if i == dict["port"]:
                    ip.port = tds[i].get_text().strip()
                if i == dict["address"]:
                    ip.address = tds[i].get_text().strip()
                if i == dict["ip_type"]:
                    ip.ip_type = tds[i].get_text().strip()
            ip_list.append(ip)
        return ip_list

    def __save_into_db(self, list):
        """
        保存到数据库
        :param list:
        :return: 成功数
        """
        executor = ThreadPoolExecutor(max_workers=20)
        res = [data for data in executor.map(self.__check_and_save, list)]
        saved_num = sum(res)
        return saved_num

    def __check_and_save(self, ip):
        res = 0
        if validate_ip(ip):
            try:
                ip.save()
                res = 1
            except Exception as e:
                ERROR(e)

        return res
