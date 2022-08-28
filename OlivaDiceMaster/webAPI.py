# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   webAPI.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivaDiceCore
import OlivaDiceMaster

import threading
import time

def init_getCheckAPI(botDict:dict):
    threading.Thread(
        target = getCheckAPI,
        args = (botDict, )
    ).start()

def getCheckAPI(botDict:dict):
    while True:
        webRes = None
        for botDict_this in botDict:
            webRes = None
            webRes = OlivaDiceMaster.webTool.GETHttpJson2Dict('http://api.oliva.icu/checkout/?hash=%s' % str(botDict_this))
        if 'code' in webRes and webRes['code'] == 0:
            if (
                'data' in webRes 
            ) and (
                'svn' in webRes['data']
            ) and (
                type(webRes['data']['svn']) == int
            ) and (
                webRes['data']['svn'] > OlivaDiceCore.data.OlivaDiceCore_svn
            ):
                if OlivaDiceMaster.data.globalProc != None:
                    OlivaDiceMaster.data.globalProc.log(3, '检测到新版本: %s' % str(webRes['data']['svn']), [
                        ('OlivaDice', 'default'),
                        ('init', 'default')
                    ])
            else:
                if OlivaDiceMaster.data.globalProc != None:
                    OlivaDiceMaster.data.globalProc.log(2, '当前已为最新版本' , [
                        ('OlivaDice', 'default'),
                        ('init', 'default')
                    ])
        time.sleep(1 * 60 * 60)
