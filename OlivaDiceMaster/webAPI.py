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
        try:
            webRes = None
            for botDict_this in botDict:
                webRes = None
                webRes = OlivaDiceMaster.webTool.GETHttpJson2Dict('http://api.oliva.icu/checkout/?hash=%s' % str(botDict_this))
            if webRes == None:
                if OlivaDiceMaster.data.globalProc != None:
                    OlivaDiceMaster.data.globalProc.log(3, '访问更新检测接口失败!', [
                        ('OlivaDice', 'default'),
                        ('autoupdate', 'default')
                    ])
            if webRes != None and 'code' in webRes and webRes['code'] == 0:
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
                        OlivaDiceMaster.data.globalProc.log(3, '检测到新版本: %s, 即将自动更新' % str(webRes['data']['svn']), [
                            ('OlivaDice', 'default'),
                            ('autoupdate', 'default')
                        ])
                        replyMsg = OlivaDiceCore.msgReply.replyMsg
                        isMatchWordStart = OlivaDiceCore.msgReply.isMatchWordStart
                        getMatchWordStartRight = OlivaDiceCore.msgReply.getMatchWordStartRight
                        skipSpaceStart = OlivaDiceCore.msgReply.skipSpaceStart
                        OlivaDiceMaster.msgReplyModel.replyOOPM_ShowUpdate_command(
                            plugin_event = None,
                            Proc = OlivaDiceMaster.data.globalProc,
                            tmp_reast_str = 'update',
                            dictStrCustom = {},
                            dictTValue = {},
                            skipSpaceStart = skipSpaceStart,
                            getMatchWordStartRight = getMatchWordStartRight,
                            isMatchWordStart = isMatchWordStart,
                            replyMsg = replyMsg,
                            flagReply = False
                        )
                else:
                    if OlivaDiceMaster.data.globalProc != None:
                        OlivaDiceMaster.data.globalProc.log(2, '当前已为最新版本' , [
                            ('OlivaDice', 'default'),
                            ('autoupdate', 'default')
                        ])
        except:
            if OlivaDiceMaster.data.globalProc != None:
                OlivaDiceMaster.data.globalProc.log(3, '发生了未曾设想的错误! 但不会影响正常运行~', [
                    ('OlivaDice', 'default'),
                    ('autoupdate', 'default')
                ])
        time.sleep(1 * 60 * 60)
