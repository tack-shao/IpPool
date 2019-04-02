# -*- coding: utf-8 -*-
# @时间      :2019/3/22 下午1:46
# @作者      :tack
# @网站      :
# @文件      :IpPool.py
# @说明      :维护一个ip池，定时检测ip是否可用，当数量低于某个数额时，重新爬取

import time

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from app.models import Ip
from app.spider.IpSpider import IpSpdier, validate_ip
from app.util.log import *


class IpPool(object):
    process = None

    def __init__(self, check_timeout=60*30, keep_num=150):
        """
        初始化
        :param check_timeout: 定期检测的时长
        :param update_num: 需要更新的数量
        """
        self.check_timeout = check_timeout
        self.keep_num = keep_num
        self.spider = IpSpdier()
        self.executor = ThreadPoolExecutor(max_workers=10)

        # 初始化数据库
        if not Ip.table_exists():
            Ip.create_table()

    def __del__(self):
        if self.process:
            # 析构函数
            self.process.terminate()
            self.process.join()
            INFO("IpPool子进程结束")

    def dowork(self):
        if not self.process:
            self.process = Process(target=self.__process_task)
            self.process.start()
        else:
            WARNING("子进程已启动")

    def __process_task(self):
        INFO("子进程启动")
        while True:
            self.check()
            INFO('完成检测, 等待%d秒 ...' % self.check_timeout)
            time.sleep(self.check_timeout)

    def check(self):
        """
        检测ip
        :return:
        """
        INFO('检测ip池')
        datas = [ip for ip in Ip.select()]
        ip_num = len(datas)
        INFO('需要检测%d条记录' % ip_num)
        ip_ids = []
        for data in self.executor.map(self.deal_single_ip, datas):
            if data != 0:
                ip_ids.append(data)
        print('ip_ids:', ip_ids)
        try:
            # 删除失败的ip
            nrows = Ip.delete().where(Ip.id << ip_ids).execute()
        except Exception as e:
            print(e)

        blance = ip_num - nrows
        need = self.keep_num - blance
        INFO("完成检测, 当前ip数: %d" % blance)
        if ip_num < self.keep_num:
            INFO('ip池 余额不足 需要充值%d条' % need)
            self.spider.crawl(need)

    def deal_single_ip(self, ip):
        res = False
        if not validate_ip(ip):
            # try:
            #     Ip.delete_by_id(ip.id)
            # except Exception as e:
            #     ERROR(e)
            return ip.id
        else:
            return 0

