#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015  k <5f3579d1@gmail.com>

import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 用户名，密码
username = '用户名'
passwd = '密码'

# cookies 在浏览中去查找
fromStation = '%u676D%u5DDE%2CHZH'
toStation = '%u8D35%u9633%2CGIW'
fromDate = '2015-12-10'

# 车次，乘车人
train_numbers = ['G1325', 'G1323']
passengers = [u'乘车人']

chromedriver_path = '/usr/local/bin/chromedriver'

# 网址
ticket_url = "https://kyfw.12306.cn/otn/leftTicket/init"
login_url  = "https://kyfw.12306.cn/otn/login/init"
initmy_url = "https://kyfw.12306.cn/otn/index/initMy12306"
config_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"

def main():

    init()

    login()

    try:

        # 跳回购票页面
        driver.get(ticket_url)

        # 加载查询信息
        driver.add_cookie({'name': '_jc_save_fromStation', 'value': fromStation})
        driver.add_cookie({'name': '_jc_save_toStation', 'value': toStation})
        driver.add_cookie({'name': '_jc_save_fromDate', 'value': fromDate})
        driver.refresh()

        count = 0;

        while driver.current_url == ticket_url:

            count += 1
            print u'开始第 %s 次查询...' % count

            driver.find_element_by_link_text(u'查询').click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'no-br'))
              )

            for i in driver.find_elements_by_class_name('btn72'):
                train = i.find_element_by_xpath('../..')
                cells = train.find_elements_by_tag_name('td')
                tnumber = train.find_element_by_class_name('train').text
                if(is_i_want(tnumber, cells)):
                    i.click()
                    purchase(tnumber)
                    break
                else:
                    print u'%s 还有票： 出发时间 %s，历时 %s。' % (tnumber,
                    	cells[0].find_element_by_class_name('start-t').text,
                     	cells[0].find_element_by_class_name('ls').find_element_by_tag_name('strong').text)

            time.sleep(0.1)


    except:
        traceback.print_exc()

def init():
    """ 初始化 driver

    1. 可以每次启动一个 chromedriver
    2. 连接一个已经启动的 chromedriver
    """
    global driver
    #driver = webdriver.Chrome(chromedriver_path)  # Optional argument, if not specified will search path.
    capabilities = {'chrome.binary': chromedriver_path}
    driver = webdriver.Remote("http://localhost:9515", capabilities)
    driver.get(ticket_url)

def login():
    while driver.find_element_by_link_text(u"登录"):
        try:
            driver.find_element_by_link_text(u"登录").click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "loginSub"))
              )
            driver.find_element_by_name("loginUserDTO.user_name").send_keys(username)
            driver.find_element_by_name("userDTO.password").send_keys(passwd)

            print u'请自行输入验证码。'

            WebDriverWait(driver, 30).until(
                EC.text_to_be_present_in_element((By.ID, 'my12306page'), u'欢迎您登录中国铁路客户服务中心网站。')
              )
            print '登录成功。'
            if driver.current_url == initmy_url:
                break
        except:
            print u'登录失败，请重新登录。'

def purchase(train_number):

    print u'购买 %s' % train_number

    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.ID, 'normal_passenger_id'), passengers[0])
      )

    for passenger in passengers:
    	print u'选取 %s' % passenger
    	time.sleep(1)
        driver.find_element_by_xpath('//label[contains(., "' + passenger + '")]').click()

    print u'请自行输入验证码'

def is_i_want(train_number, cells):
    # TODO 判断不够灵活，这里限定了只购买二等座。
    return train_number in train_numbers and cells[4].text not in ['--', u'无']

if __name__ == "__main__":
    main()
