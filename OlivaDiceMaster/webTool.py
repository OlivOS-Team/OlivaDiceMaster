# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   webTool.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivaDiceMaster

import requests as req
import json
import os

dictTemp = {}

def GETHttpJson2Dict(url):
    msg_res = None
    res = None
    send_url = url
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'OlivaDiceMaster/%s' % OlivaDiceMaster.data.OlivaDiceMaster_ver_short
    }
    try:
        msg_res = req.request("GET", send_url, headers = headers, timeout = 60)
        res = json.loads(msg_res.text)
    except:
        pass
    return res

def GETHttpFile(url, path):
    res = False
    send_url = url
    headers = {
        'User-Agent': 'OlivaDiceMaster/%s' % OlivaDiceMaster.data.OlivaDiceMaster_ver_short
    }
    try:
        msg_res = req.request("GET", send_url, headers = headers)
        releaseToDirForFile(path)
        with open(path, 'wb+') as tmp:
            tmp.write(msg_res.content)
        if msg_res.status_code in [200, 300]:
            res = True
        else:
            res = False
    except:
        res = False
    return res

def releaseDir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def releaseToDir(dir_path):
    tmp_path_list = dir_path.rstrip('/').split('/')
    for tmp_path_list_index in range(len(tmp_path_list)):
        if tmp_path_list[tmp_path_list_index] != '':
        	releaseDir('/'.join(tmp_path_list[:tmp_path_list_index + 1]))

def releaseToDirForFile(dir_path):
    tmp_path_list = dir_path.rstrip('/').split('/')
    if len(tmp_path_list) > 0:
        tmp_path_list = tmp_path_list[:-1]
    for tmp_path_list_index in range(len(tmp_path_list)):
        if tmp_path_list[tmp_path_list_index] != '':
        	releaseDir('/'.join(tmp_path_list[:tmp_path_list_index + 1]))
