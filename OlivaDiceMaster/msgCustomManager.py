# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   msgCustomManager.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivOS
import OlivaDiceCore
import OlivaDiceMaster

import os
import json

def initMsgCustom(bot_info_dict):
    for bot_info_dict_this in bot_info_dict:
        if bot_info_dict_this not in OlivaDiceCore.msgCustom.dictStrCustomDict:
            OlivaDiceCore.msgCustom.dictStrCustomDict[bot_info_dict_this] = {}
        for dictStrCustom_this in OlivaDiceMaster.msgCustom.dictStrCustom:
            if dictStrCustom_this not in OlivaDiceCore.msgCustom.dictStrCustomDict[bot_info_dict_this]:
                OlivaDiceCore.msgCustom.dictStrCustomDict[bot_info_dict_this][dictStrCustom_this] = OlivaDiceMaster.msgCustom.dictStrCustom[dictStrCustom_this]
        for dictHelpDoc_this in OlivaDiceMaster.msgCustom.dictHelpDocTemp:
            if dictHelpDoc_this not in OlivaDiceCore.helpDocData.dictHelpDoc[bot_info_dict_this]:
                OlivaDiceCore.helpDocData.dictHelpDoc[bot_info_dict_this][dictHelpDoc_this] = OlivaDiceMaster.msgCustom.dictHelpDocTemp[dictHelpDoc_this]
    OlivaDiceCore.msgCustom.dictStrConst.update(OlivaDiceMaster.msgCustom.dictStrConst)
    OlivaDiceCore.msgCustom.dictGValue.update(OlivaDiceMaster.msgCustom.dictGValue)
    OlivaDiceCore.msgCustom.dictTValue.update(OlivaDiceMaster.msgCustom.dictTValue)
    for dictConsoleSwitchTemplate_this in OlivaDiceMaster.msgCustom.dictConsoleSwitchTemplate:
        if dictConsoleSwitchTemplate_this in OlivaDiceCore.console.dictConsoleSwitchTemplate:
            OlivaDiceCore.console.dictConsoleSwitchTemplate[dictConsoleSwitchTemplate_this].update(
                OlivaDiceMaster.msgCustom.dictConsoleSwitchTemplate[dictConsoleSwitchTemplate_this]
            )
    OlivaDiceCore.console.initConsoleSwitchByBotDict(bot_info_dict)
    OlivaDiceCore.console.readConsoleSwitch()
    OlivaDiceCore.console.saveConsoleSwitch()
