# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   msgCustom.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivOS
import OlivaDiceCore
import OlivaDiceMaster

dictStrCustomDict = {}

dictStrCustom = {
    'strMasterReply': '{tMasterResult}',
    'strMasterOopmApiFailed': '更新源访问失败',
    'strMasterOopmNotMatch': '未找到匹配模块条目',
    'strMasterOopmDownload': '{tMasterOopkNameList}\n模块已下载成功',
    'strMasterOopmCopy': '{tMasterOopkNameList}\n模块已安装成功',
    'strMasterOopmUpdate': '{tMasterOopkNameList}\n模块已更新成功',
    'strMasterOopmUpdateAllDone': '所选模块已更新成功，即将重载',
    'strMasterOopmUpdateNotNeed': '所有模块已为最新版本，无需更新',
    'strMasterOopmUpdateNotSkipSrc': '{tMasterOopkNameList}\n模块为手动部署模式，已跳过',
    'strMasterOopmUpdateNotSkipDev': '{tMasterOopkNameList}\n模块为开发模式，已跳过',
    'strMasterOopmDownloadFailed': '{tMasterOopkNameList}\n模块下载失败',
    'strMasterOopmCopyFailed': '{tMasterOopkNameList}\n模块安装失败'
}

dictStrConst = {
}

dictGValue = {
}

dictTValue = {
    'tMasterResult': 'N/A',
    'tMasterOopkNameList': 'N/A'
}

dictHelpDocTemp = {
    'OlivaDiceMaster': '''[OlivaDiceMaster]
OlivaDice大师模块
本模块为青果跑团掷骰机器人(OlivaDice)大师模块，集成与跑团无关的骰主管理功能功能（如指令更新等）。
核心开发者: lunzhiPenxil仑质
[.help OlivaDiceMaster更新] 查看本模块更新日志
注: 本模块为可选重要模块。''',

    'OlivaDiceMaster更新': '''[OlivaDiceMaster]
3.0.0: 指令更新''',
}
