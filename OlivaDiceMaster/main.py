# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   main.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivOS
import OlivaDiceMaster
import OlivaDiceCore
import OlivaDiceMaster.backup
import threading

class Event(object):
    def init(plugin_event, Proc):
        OlivaDiceMaster.data.globalProc = Proc
        OlivaDiceMaster.msgReply.unity_init(plugin_event, Proc)

    def init_after(plugin_event, Proc):
        OlivaDiceCore.crossHook.dictHookList['model'].append(['OlivaDiceMaster', OlivaDiceMaster.data.OlivaDiceMaster_ver_short])
        OlivaDiceMaster.msgReply.data_init(plugin_event, Proc)
        # after后启动备份系统
        threads = threading.Thread(target=OlivaDiceMaster.backup.initBackupSystem, args=(Proc,))
        threads.daemon = True  # 设置为守护线程，主程序退出时自动结束
        threads.start()

    def private_message(plugin_event, Proc):
        OlivaDiceMaster.msgReply.unity_reply(plugin_event, Proc)

    def group_message(plugin_event, Proc):
        OlivaDiceMaster.msgReply.unity_reply(plugin_event, Proc)

    def poke(plugin_event, Proc):
        pass
