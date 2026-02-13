# -*- encoding: utf-8 -*-
r"""
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/

@File      :   msgReply.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2026, OlivOS-Team
@Desc      :   None
"""

import OlivOS
import OlivaDiceMaster
import OlivaDiceCore

import time
import shutil
import os
import re


def unity_init(plugin_event, Proc):
    pass


def data_init(plugin_event, Proc):
    OlivaDiceMaster.msgCustomManager.initMsgCustom(Proc.Proc_data['bot_info_dict'])
    OlivaDiceMaster.webAPI.init_getCheckAPI(Proc.Proc_data['bot_info_dict'])


def unity_reply(plugin_event, Proc):
    OlivaDiceCore.userConfig.setMsgCount()
    dictTValue = OlivaDiceCore.msgCustom.dictTValue.copy()
    dictTValue['tUserName'] = plugin_event.data.sender['name']
    dictTValue['tName'] = plugin_event.data.sender['name']
    dictStrCustom = OlivaDiceCore.msgCustom.dictStrCustomDict[plugin_event.bot_info.hash]
    dictGValue = OlivaDiceCore.msgCustom.dictGValue
    dictTValue.update(dictGValue)
    dictTValue = OlivaDiceCore.msgCustomManager.dictTValueInit(plugin_event, dictTValue)

    sendMsgByEvent = OlivaDiceCore.msgReply.sendMsgByEvent
    replyMsg = OlivaDiceCore.msgReply.replyMsg
    replyMsgLazyHelpByEvent = OlivaDiceCore.msgReply.replyMsgLazyHelpByEvent
    isMatchWordStart = OlivaDiceCore.msgReply.isMatchWordStart
    getMatchWordStartRight = OlivaDiceCore.msgReply.getMatchWordStartRight
    skipSpaceStart = OlivaDiceCore.msgReply.skipSpaceStart
    skipToRight = OlivaDiceCore.msgReply.skipToRight
    msgIsCommand = OlivaDiceCore.msgReply.msgIsCommand

    tmp_at_str = OlivOS.messageAPI.PARA.at(plugin_event.base_info['self_id']).CQ()  # NOQA: F841
    tmp_id_str = str(plugin_event.base_info['self_id'])
    tmp_at_str_sub = None
    tmp_id_str_sub = None
    if 'sub_self_id' in plugin_event.data.extend:
        if plugin_event.data.extend['sub_self_id'] is not None:
            tmp_at_str_sub = OlivOS.messageAPI.PARA.at(plugin_event.data.extend['sub_self_id']).CQ()  # NOQA: F841
            tmp_id_str_sub = str(plugin_event.data.extend['sub_self_id'])
    tmp_command_str_1 = '.'  # NOQA: F841
    tmp_command_str_2 = '。'  # NOQA: F841
    tmp_command_str_3 = '/'  # NOQA: F841
    tmp_reast_str = plugin_event.data.message
    flag_force_reply = False
    flag_is_command = False
    flag_is_from_host = False
    flag_is_from_group = False
    flag_is_from_group_admin = False
    flag_is_from_group_sub_admin = False
    flag_is_from_group_have_admin = False
    flag_is_from_master = False
    if isMatchWordStart(tmp_reast_str, '[CQ:reply,id='):
        tmp_reast_str = skipToRight(tmp_reast_str, ']')
        tmp_reast_str = tmp_reast_str[1:]
    if flag_force_reply is False:
        tmp_reast_str_old = tmp_reast_str
        tmp_reast_obj = OlivOS.messageAPI.Message_templet('old_string', tmp_reast_str)
        tmp_at_list = []
        for tmp_reast_obj_this in tmp_reast_obj.data:
            tmp_para_str_this = tmp_reast_obj_this.CQ()
            if type(tmp_reast_obj_this) is OlivOS.messageAPI.PARA.at:
                tmp_at_list.append(str(tmp_reast_obj_this.data['id']))
                tmp_reast_str = tmp_reast_str.lstrip(tmp_para_str_this)
            elif type(tmp_reast_obj_this) is OlivOS.messageAPI.PARA.text:
                if tmp_para_str_this.strip(' ') == '':
                    tmp_reast_str = tmp_reast_str.lstrip(tmp_para_str_this)
                else:
                    break
            else:
                break
        if tmp_id_str in tmp_at_list:
            flag_force_reply = True
        if tmp_id_str_sub in tmp_at_list:
            flag_force_reply = True
        if 'all' in tmp_at_list:
            flag_force_reply = True
        if flag_force_reply is True:
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
        else:
            tmp_reast_str = tmp_reast_str_old
    [tmp_reast_str, flag_is_command] = msgIsCommand(tmp_reast_str, OlivaDiceCore.crossHook.dictHookList['prefix'])
    if flag_is_command:
        tmp_hagID = None
        flag_is_from_master = OlivaDiceCore.ordinaryInviteManager.isInMasterList(
            plugin_event.bot_info.hash,
            OlivaDiceCore.userConfig.getUserHash(plugin_event.data.user_id, 'user', plugin_event.platform['platform']),
        )
        if plugin_event.plugin_info['func_type'] == 'group_message':
            if plugin_event.data.host_id is not None:
                flag_is_from_host = True
            flag_is_from_group = True
        elif plugin_event.plugin_info['func_type'] == 'private_message':
            flag_is_from_group = False
        if flag_is_from_group:
            if 'role' in plugin_event.data.sender:
                flag_is_from_group_have_admin = True  # NOQA: F841
                if plugin_event.data.sender['role'] in ['owner', 'admin']:
                    flag_is_from_group_admin = True  # NOQA: F841
                elif plugin_event.data.sender['role'] in ['sub_admin']:
                    flag_is_from_group_admin = True  # NOQA: F841
                    flag_is_from_group_sub_admin = True  # NOQA: F841
        if flag_is_from_host and flag_is_from_group:
            tmp_hagID = '%s|%s' % (str(plugin_event.data.host_id), str(plugin_event.data.group_id))
        elif flag_is_from_group:
            tmp_hagID = str(plugin_event.data.group_id)
        flag_hostEnable = True
        if flag_is_from_host:
            flag_hostEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                userId=plugin_event.data.host_id,
                userType='host',
                platform=plugin_event.platform['platform'],
                userConfigKey='hostEnable',
                botHash=plugin_event.bot_info.hash,
            )
        flag_hostLocalEnable = True
        if flag_is_from_host:
            flag_hostLocalEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                userId=plugin_event.data.host_id,
                userType='host',
                platform=plugin_event.platform['platform'],
                userConfigKey='hostLocalEnable',
                botHash=plugin_event.bot_info.hash,
            )
        flag_groupEnable = True
        if flag_is_from_group:
            if flag_is_from_host:
                if flag_hostEnable:
                    flag_groupEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                        userId=tmp_hagID,
                        userType='group',
                        platform=plugin_event.platform['platform'],
                        userConfigKey='groupEnable',
                        botHash=plugin_event.bot_info.hash,
                    )
                else:
                    flag_groupEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                        userId=tmp_hagID,
                        userType='group',
                        platform=plugin_event.platform['platform'],
                        userConfigKey='groupWithHostEnable',
                        botHash=plugin_event.bot_info.hash,
                    )
            else:
                flag_groupEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                    userId=tmp_hagID,
                    userType='group',
                    platform=plugin_event.platform['platform'],
                    userConfigKey='groupEnable',
                    botHash=plugin_event.bot_info.hash,
                )
        # 此频道关闭时中断处理
        if not flag_hostLocalEnable and not flag_force_reply:
            return
        # 此群关闭时中断处理
        if not flag_groupEnable and not flag_force_reply:
            return
        if flag_is_from_master and isMatchWordStart(tmp_reast_str, 'oopm', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'oopm')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            tmp_reply_str = None
            if isMatchWordStart(tmp_reast_str, 'show') or isMatchWordStart(tmp_reast_str, 'update'):
                OlivaDiceMaster.msgReplyModel.replyOOPM_ShowUpdate_command(
                    plugin_event=plugin_event,
                    Proc=Proc,
                    tmp_reast_str=tmp_reast_str,
                    dictStrCustom=dictStrCustom,
                    dictTValue=dictTValue,
                    skipSpaceStart=skipSpaceStart,
                    getMatchWordStartRight=getMatchWordStartRight,
                    isMatchWordStart=isMatchWordStart,
                    replyMsg=replyMsg,
                    flagReply=True,
                )
            elif isMatchWordStart(tmp_reast_str, 'list', fullMatch=True):
                tmp_api_data = OlivaDiceMaster.webTool.GETHttpJson2Dict(OlivaDiceMaster.data.OlivaDiceMaster_oopm_host)
                if tmp_api_data is not None:
                    tmp_model_list = []
                    if 'model' in tmp_api_data:
                        for tmp_api_data_model_this in tmp_api_data['model']:
                            tmp_api_data_model = tmp_api_data['model'][tmp_api_data_model_this]
                            tmp_api_data_model_branch = 'main'
                            if 'command' in tmp_api_data_model[tmp_api_data_model_branch]:
                                tmp_model_list.append(
                                    '[%s] - %s(%s)'
                                    % (
                                        tmp_api_data_model[tmp_api_data_model_branch]['command'],
                                        str(tmp_api_data_model[tmp_api_data_model_branch]['version']),
                                        str(tmp_api_data_model[tmp_api_data_model_branch]['svn']),
                                    )
                                )
                    tmp_reply_str_1 = '可选模块如下:\n%s' % '\n'.join(tmp_model_list)
                    dictTValue['tMasterResult'] = tmp_reply_str_1
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterReply'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterOopmApiFailed'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
            elif isMatchWordStart(tmp_reast_str, 'get'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'get')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                tmp_reast_str = tmp_reast_str.rstrip(' ')
                tmp_get_model_name = tmp_reast_str
                tmp_api_data = OlivaDiceMaster.webTool.GETHttpJson2Dict(OlivaDiceMaster.data.OlivaDiceMaster_oopm_host)
                if tmp_api_data is not None:
                    if 'model' in tmp_api_data:
                        flag_need_update = False
                        for tmp_api_data_model_this in tmp_api_data['model']:
                            tmp_api_data_model = tmp_api_data['model'][tmp_api_data_model_this]
                            tmp_api_data_model_branch = 'main'
                            if 'command' in tmp_api_data_model[tmp_api_data_model_branch]:
                                tmp_api_model_name = tmp_api_data_model[tmp_api_data_model_branch]['command']
                                if tmp_get_model_name.lower() == tmp_api_model_name.lower():
                                    flag_download = False
                                    flag_copy = False
                                    tmp_download_tmp_path = '%s/unity/update/%s.opk' % (
                                        OlivaDiceCore.data.dataDirRoot,
                                        tmp_api_model_name,
                                    )
                                    tmp_oopm_target_path = './plugin/app/%s.opk' % tmp_api_model_name
                                    dictTValue['tMasterOopkNameList'] = tmp_api_data_model_this
                                    if 'version' in tmp_api_data_model[tmp_api_data_model_branch]:
                                        dictTValue['tMasterOopkNameList'] += ' ' + str(
                                            tmp_api_data_model[tmp_api_data_model_branch]['version']
                                        )
                                    if 'svn' in tmp_api_data_model[tmp_api_data_model_branch]:
                                        dictTValue['tMasterOopkNameList'] += (
                                            '(' + str(tmp_api_data_model[tmp_api_data_model_branch]['svn']) + ')'
                                        )
                                    if os.path.exists(tmp_oopm_target_path[:-4]):
                                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                            dictStrCustom['strMasterOopmGetSkipSrc'], dictTValue
                                        )
                                        replyMsg(plugin_event, tmp_reply_str)
                                        return
                                    if 'opk_path' in tmp_api_data_model[tmp_api_data_model_branch]:
                                        tmp_omodel_ver_target_opk_path = tmp_api_data_model[tmp_api_data_model_branch][
                                            'opk_path'
                                        ]
                                        flag_download = OlivaDiceMaster.webTool.GETHttpFile(
                                            tmp_omodel_ver_target_opk_path, tmp_download_tmp_path
                                        )
                                    if not flag_download:
                                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                            dictStrCustom['strMasterOopmDownloadFailed'], dictTValue
                                        )
                                        replyMsg(plugin_event, tmp_reply_str)
                                        flag_done = False
                                        flag_done_this = False
                                        return
                                    try:
                                        shutil.copyfile(tmp_download_tmp_path, tmp_oopm_target_path)
                                        flag_copy = True
                                    except Exception:
                                        flag_copy = False
                                    if not flag_copy:
                                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                            dictStrCustom['strMasterOopmCopyFailed'], dictTValue
                                        )
                                        replyMsg(plugin_event, tmp_reply_str)
                                        flag_done = False  # NOQA: F841
                                        flag_done_this = False  # NOQA: F841
                                        return
                                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                        dictStrCustom['strMasterOopmGet'], dictTValue
                                    )
                                    replyMsg(plugin_event, tmp_reply_str)
                                    flag_need_update = True
                        if not flag_need_update:
                            dictTValue['tMasterOopkNameList'] = tmp_get_model_name
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterOopmGetNone'], dictTValue
                            )
                            replyMsg(plugin_event, tmp_reply_str)
                            return
                else:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterOopmApiFailed'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
            return
        elif flag_is_from_master and isMatchWordStart(tmp_reast_str, 'send', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'send')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            flag_target_type = None
            tmp_send_result = tmp_reast_str
            tmp_target_host_id = None
            tmp_target_id = None
            if isMatchWordStart(tmp_reast_str, 'user'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'user')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_target_type = 'private'
            if isMatchWordStart(tmp_reast_str, 'group'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'group')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_target_type = 'group'
            if flag_target_type is not None:
                tmp_reast_str_list = tmp_reast_str.split(' ')
                if len(tmp_reast_str_list) >= 2:
                    tmp_reast_str_list_0_list = tmp_reast_str_list[0].split('|')
                    if len(tmp_reast_str_list_0_list) == 1:
                        tmp_target_id = str(tmp_reast_str_list_0_list[0])
                    elif len(tmp_reast_str_list_0_list) == 2:
                        tmp_target_host_id = str(tmp_reast_str_list_0_list[0])
                        tmp_target_id = str(tmp_reast_str_list_0_list[1])
                    tmp_send_result = ' '.join(tmp_reast_str_list[1:])
            if tmp_target_id is not None:
                dictTValue['tResult'] = tmp_send_result
                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                    dictStrCustom['strMasterSendFromMaster'], dictTValue
                )
                sendMsgByEvent(plugin_event, tmp_reply_str, tmp_target_id, flag_target_type, host_id=tmp_target_host_id)
            else:
                tmp_reply_str = tmp_send_result
                replyMsg(plugin_event, tmp_reply_str)
            return
        elif isMatchWordStart(tmp_reast_str, 'send', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'send')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            tmp_send_result = tmp_reast_str
            tmp_botHash = plugin_event.bot_info.hash
            tmp_hostId = None
            if 'host_id' in plugin_event.data.__dict__:
                tmp_hostId = plugin_event.data.host_id
            if tmp_botHash in OlivaDiceCore.console.dictConsoleSwitch:
                if 'masterList' in OlivaDiceCore.console.dictConsoleSwitch[tmp_botHash]:
                    for master_this in OlivaDiceCore.console.dictConsoleSwitch[tmp_botHash]['masterList']:
                        if master_this[1] == plugin_event.platform['platform']:
                            if flag_is_from_group:
                                dictTValue['tGroupName'] = '群'
                                dictTValue['tGroupId'] = str(tmp_hagID)
                            else:
                                dictTValue['tGroupName'] = '私聊'
                                dictTValue['tGroupId'] = '-'
                            dictTValue['tUserName'] = '用户'
                            if 'name' in plugin_event.data.sender:
                                dictTValue['tUserName'] = plugin_event.data.sender['name']
                            dictTValue['tUserId'] = str(plugin_event.data.user_id)
                            dictTValue['tResult'] = tmp_send_result
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterSendToMaster'], dictTValue
                            )
                            sendMsgByEvent(
                                plugin_event, tmp_reply_str, str(master_this[0]), 'private', host_id=tmp_hostId
                            )
            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                dictStrCustom['strMasterSendToMasterAlready'], dictTValue
            )
            replyMsg(plugin_event, tmp_reply_str)
            return
        elif isMatchWordStart(tmp_reast_str, 'trust', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'trust')
            flag_data_type = 'trustLevel'
            flag_target_type = 'user'
            tmp_userId = None
            tmp_userTrustVal = None
            tmp_userPlatform = plugin_event.bot_info.platform['platform']
            tmp_botHash = plugin_event.bot_info.hash
            if isMatchWordStart(tmp_reast_str, 'level'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'level')
                flag_data_type = 'trustLevel'
            elif isMatchWordStart(tmp_reast_str, 'rank'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'rank')
                flag_data_type = 'trustRank'
            if flag_data_type == 'trustLevel':
                dictTValue['tMasterTrustName'] = '信任等级'
            elif flag_data_type == 'trustRank':
                dictTValue['tMasterTrustName'] = '信任评分'
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            if isMatchWordStart(tmp_reast_str, 'user'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'user')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_target_type = 'user'
            elif isMatchWordStart(tmp_reast_str, 'group'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'group')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_target_type = 'group'
            elif isMatchWordStart(tmp_reast_str, 'host'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'host')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_target_type = 'host'
            if flag_is_from_master:
                tmp_reast_str = tmp_reast_str.strip(' ')
                tmp_reast_str_list = tmp_reast_str.split(' ')
                tmp_reast_str_list_len = len(tmp_reast_str_list)
                if tmp_reast_str_list_len > 1:
                    tmp_userId = tmp_reast_str_list[0]
                    try:
                        tmp_userTrustVal = int(tmp_reast_str_list[-1])
                    except Exception:
                        tmp_userTrustVal = None
                elif tmp_reast_str_list_len == 1:
                    tmp_userId = tmp_reast_str_list[0]
                if tmp_userId == '':
                    tmp_userId = None
            if tmp_userId is None or tmp_userId == 'this':
                if flag_target_type == 'user':
                    tmp_userId = plugin_event.data.user_id
                elif flag_target_type == 'group':
                    if 'group_id' in plugin_event.data.__dict__:
                        tmp_userId = plugin_event.data.group_id
                        if 'host_id' in plugin_event.data.__dict__:
                            tmp_userId = str(plugin_event.data.host_id) + '|' + str(tmp_userId)
                elif flag_target_type == 'host':
                    if 'host_id' in plugin_event.data.__dict__:
                        tmp_userId = plugin_event.data.host_id
            if tmp_userId is not None:
                tmp_userHash = OlivaDiceCore.userConfig.getUserHash(
                    userId=tmp_userId, userType=flag_target_type, platform=tmp_userPlatform
                )
                tmp_userId_new = OlivaDiceCore.userConfig.getUserDataByKeyWithHash(  # NOQA: F841
                    userHash=tmp_userHash, userDataKey='userId', botHash=tmp_botHash
                )
                dictTValue['tId'] = tmp_userId
                if flag_target_type == 'user':
                    dictTValue['tName'] = OlivaDiceCore.userConfig.getUserConfigByKeyWithHash(
                        userHash=tmp_userHash, userConfigKey='userName', botHash=tmp_botHash
                    )
                elif flag_target_type == 'group':
                    dictTValue['tName'] = '群'
                elif flag_target_type == 'host':
                    dictTValue['tName'] = '频道'
                if tmp_userTrustVal is not None:
                    OlivaDiceCore.userConfig.setUserConfigByKey(
                        userId=tmp_userId,
                        userType=flag_target_type,
                        platform=tmp_userPlatform,
                        userConfigKey=flag_data_type,
                        userConfigValue=tmp_userTrustVal,
                        botHash=tmp_botHash,
                    )
                    OlivaDiceCore.userConfig.writeUserConfigByUserHash(tmp_userHash)
                    dictTValue['tResult'] = str(tmp_userTrustVal)
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterTrustSet'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    tmp_userTrustVal = OlivaDiceCore.userConfig.getUserConfigByKeyWithHash(
                        userHash=tmp_userHash, userConfigKey=flag_data_type, botHash=tmp_botHash
                    )
                    dictTValue['tResult'] = str(tmp_userTrustVal)
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterTrustGet'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
            return
        elif flag_is_from_master and isMatchWordStart(tmp_reast_str, 'group', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'group')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            flag_action = None
            flag_action_next = None
            flag_clear_gate = 60 * 60 * 24 * 30
            flag_clear_trustLevel_gate = 2
            # time mode 按时间查找
            flag_clear_mode = 'time'
            if isMatchWordStart(tmp_reast_str, ['clear', 'clr']):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, ['clear', 'clr'])
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_action = 'clear'
                flag_action_next = 'show'
            # 先检查是否有show或do
            if flag_action == 'clear' and isMatchWordStart(tmp_reast_str, 'show'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'show')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_action_next = 'show'
            elif flag_action == 'clear' and isMatchWordStart(tmp_reast_str, 'do'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'do')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_action_next = 'do'
            # 然后检查是否是清理off状态的群
            if flag_action == 'clear' and isMatchWordStart(tmp_reast_str, 'off'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'off')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                flag_clear_mode = 'off'
            if flag_action == 'clear' and flag_action_next is not None:
                tmp_reast_str = tmp_reast_str.rstrip(' ')
                # 解析自定义回复消息
                custom_reply_msg = ''
                # 只有在time模式下才处理天数参数
                if flag_clear_mode == 'time' and len(tmp_reast_str) > 0:
                    para_result = OlivaDiceCore.msgReply.getNumberPara(tmp_reast_str, reverse=False)
                    number_part = para_result[0]
                    custom_reply_msg = para_result[1].strip()
                    if number_part and number_part.isdigit():
                        flag_clear_gate = 60 * 60 * 24 * int(number_part)
                elif flag_clear_mode == 'off' and len(tmp_reast_str) > 0:
                    # off模式直接取剩余字符串作为自定义消息
                    custom_reply_msg = tmp_reast_str.strip()
                tmp_group_list = []
                res = None
                tmp_userPlatform = plugin_event.bot_info.platform['platform']
                tmp_botHash = plugin_event.bot_info.hash
                if tmp_userPlatform in ['qq', 'telegram']:
                    res = plugin_event.get_group_list()
                if res is not None:
                    if res['active'] is True:
                        for group_this in res['data']:
                            tmp_group_unit = {}
                            tmp_group_unit['name'] = group_this['name']
                            tmp_group_unit['id'] = group_this['id']
                            tmp_group_unit['trustLevel'] = OlivaDiceCore.userConfig.dictUserConfigNoteDefault[
                                'trustLevel'
                            ]
                            tmp_userLastHit = None
                            # 记录群是否开启
                            tmp_group_unit['groupEnable'] = True
                            tmp_userHash = OlivaDiceCore.userConfig.getUserHash(
                                userId=tmp_group_unit['id'], userType='group', platform=tmp_userPlatform
                            )
                            tmp_userId = OlivaDiceCore.userConfig.getUserDataByKeyWithHash(
                                userHash=tmp_userHash, userDataKey='userId', botHash=tmp_botHash
                            )
                            if tmp_userId is not None:
                                tmp_userLastHit = OlivaDiceCore.userConfig.getUserDataByKeyWithHash(
                                    userHash=tmp_userHash, userDataKey='lastHit', botHash=tmp_botHash
                                )
                                tmp_group_unit['trustLevel'] = OlivaDiceCore.userConfig.getUserConfigByKeyWithHash(
                                    userHash=tmp_userHash, userConfigKey='trustLevel', botHash=tmp_botHash
                                )
                                # 获取群是否开启的状态
                                tmp_group_unit['groupEnable'] = OlivaDiceCore.userConfig.getUserConfigByKey(
                                    userId=tmp_group_unit['id'],
                                    userType='group',
                                    platform=tmp_userPlatform,
                                    userConfigKey='groupEnable',
                                    botHash=tmp_botHash,
                                )
                            tmp_group_unit['lastHit'] = tmp_userLastHit
                            tmp_group_unit['lastHitShow'] = tmp_userLastHit
                            if tmp_group_unit['lastHit'] is None:
                                tmp_group_unit['lastHit'] = -1
                                tmp_group_unit['lastHitShow'] = None
                            tmp_group_list.append(tmp_group_unit)
                        tmp_group_list.sort(key=lambda x: x['lastHit'])
                        tmp_group_list_str = []
                        tmp_group_list_clear = {}
                        if flag_clear_mode == 'off':
                            # off模式：清理bot off的群
                            for group_this in tmp_group_list:
                                flag_skip = flag_clear_trustLevel_gate <= group_this['trustLevel']
                                if not group_this['groupEnable']:
                                    tmp_unit_data = {
                                        'tName': group_this['name'],
                                        'tId': group_this['id'],
                                        'tResult': 'Bot已关闭' + (' (信任)' if flag_skip else ''),
                                    }
                                    tmp_strMasterGroupClearUnit = dictStrCustom['strMasterGroupClearUnit'].format(
                                        **tmp_unit_data
                                    )
                                    tmp_group_list_str.append(tmp_strMasterGroupClearUnit)
                                    if not flag_skip:
                                        tmp_group_list_clear[str(group_this['id'])] = {
                                            'show': tmp_strMasterGroupClearUnit,
                                            'time': 'Bot已关闭',
                                        }
                        else:
                            # time模式：按时间清理
                            for group_this in tmp_group_list:
                                flag_skip = flag_clear_trustLevel_gate <= group_this['trustLevel']
                                tmp_time = '无记录'
                                tmp_time_1 = '无记录'
                                tmp_time_type = '秒'
                                tmp_time_int_raw = int(time.time()) + 1
                                if group_this['lastHitShow'] is not None:
                                    tmp_time_int = int(time.time()) - group_this['lastHitShow']
                                    tmp_time_int_raw = tmp_time_int
                                    if tmp_time_int >= 60 * 60 * 24:
                                        tmp_time_int = int(tmp_time_int / (60 * 60 * 24))
                                        tmp_time_type = '天'
                                    elif tmp_time_int >= 60 * 60:
                                        tmp_time_int = int(tmp_time_int / (60 * 60))
                                        tmp_time_type = '小时'
                                    elif tmp_time_int >= 60:
                                        tmp_time_int = int(tmp_time_int / 60)
                                        tmp_time_type = '分钟'
                                    # 时间格式化 - 清单
                                    tmp_time = '%s%s前' % (str(tmp_time_int), tmp_time_type)
                                    # 时间格式化 - 执行后用户侧看到的
                                    tmp_time_1 = '%s%s前' % (str(tmp_time_int), tmp_time_type)
                                    if flag_skip:
                                        tmp_time = tmp_time + ' (信任)'
                                tmp_unit_data = {
                                    'tName': group_this['name'],
                                    'tId': group_this['id'],
                                    'tResult': tmp_time,
                                }
                                if flag_clear_gate < tmp_time_int_raw:
                                    tmp_strMasterGroupClearUnit = dictStrCustom['strMasterGroupClearUnit'].format(
                                        **tmp_unit_data
                                    )
                                    tmp_group_list_str.append(
                                        dictStrCustom['strMasterGroupClearUnit'].format(**tmp_unit_data)
                                    )
                                    if not flag_skip:
                                        tmp_group_list_clear[str(group_this['id'])] = {
                                            'show': tmp_strMasterGroupClearUnit,
                                            'time': tmp_time_1,
                                        }
                        dictTValue['tMasterCount01'] = str(len(tmp_group_list))
                        dictTValue['tMasterCount02'] = str(len(tmp_group_list_clear))
                        dictTValue['tResult'] = '\n'.join(tmp_group_list_str)
                        if flag_action_next == 'do':
                            messageSplitDelay = OlivaDiceCore.console.getConsoleSwitchByHash(
                                'messageSplitDelay', tmp_botHash
                            )
                            for group_this in tmp_group_list_clear:
                                if custom_reply_msg:
                                    tmp_reply_str = custom_reply_msg
                                else:
                                    dictTValue['tResult'] = tmp_group_list_clear[group_this]['time']
                                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                        dictStrCustom['strMasterGroupClearDoUnitSend'], dictTValue
                                    )
                                sendMsgByEvent(plugin_event, tmp_reply_str, group_this, 'group', host_id=None)
                                time.sleep(messageSplitDelay / 1000)
                                plugin_event.set_group_leave(group_id=group_this, is_dismiss=True)
                                dictTValue['tResult'] = tmp_group_list_clear[group_this]['show']
                                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                    dictStrCustom['strMasterGroupClearDoUnit'], dictTValue
                                )
                                replyMsg(plugin_event, tmp_reply_str)
                                time.sleep(messageSplitDelay / 1000)
                            dictTValue['tResult'] = '\n'.join(tmp_group_list_str)
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterGroupClearDo'], dictTValue
                            )
                            replyMsg(plugin_event, tmp_reply_str)
                        elif flag_action_next == 'show':
                            dictTValue['tResult'] = '\n'.join(tmp_group_list_str)
                            if flag_clear_mode == 'off':
                                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                    dictStrCustom['strMasterGroupClearShowOff'], dictTValue
                                )
                            else:
                                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                    dictStrCustom['strMasterGroupClearShow'], dictTValue
                                )
                            replyMsg(plugin_event, tmp_reply_str)
                else:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterPlatformNo'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
            return
        elif flag_is_from_master and isMatchWordStart(tmp_reast_str, 'backup', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'backup')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            # 手动触发备份
            if isMatchWordStart(tmp_reast_str, 'start'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'start')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)

                # 发送开始备份的消息
                dictTValue['tBackupResult'] = ''
                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                    dictStrCustom['strMasterBackupStart'], dictTValue
                )
                replyMsg(plugin_event, tmp_reply_str)
                # 执行备份
                success, result = OlivaDiceMaster.backup.createBackup(Proc)
                # 发送备份结果消息
                dictTValue['tBackupResult'] = result
                if success:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterBackupSuccess'], dictTValue
                    )
                else:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterBackupFailed'], dictTValue
                    )
                replyMsg(plugin_event, tmp_reply_str)

            # 修改配置
            elif isMatchWordStart(tmp_reast_str, 'change'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'change')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                tmp_reast_str_list = tmp_reast_str.split(' ')
                if len(tmp_reast_str_list) >= 2:
                    config_key = tmp_reast_str_list[0]
                    config_value = ' '.join(tmp_reast_str_list[1:])
                    try:
                        # 验证配置项格式
                        validated_value = OlivaDiceMaster.backup.validateBackupConfigItem(config_key, config_value)
                        # 设置配置
                        OlivaDiceCore.console.setBackupConfigByKey(config_key, validated_value)
                        OlivaDiceCore.console.saveBackupConfig()
                        dictTValue['tConfigKey'] = config_key
                        dictTValue['tConfigValue'] = str(validated_value)
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterBackupConfigSet'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)

                    except ValueError as e:
                        dictTValue['tBackupResult'] = str(e)
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterBackupConfigSetFailed'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                else:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterBackupChangeUsage'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
            # 查看配置
            else:
                config_key = tmp_reast_str.strip()
                if config_key:
                    config_value = OlivaDiceCore.console.getBackupConfigByKey(config_key)
                    if config_value is not None:
                        dictTValue['tConfigKey'] = config_key
                        dictTValue['tConfigValue'] = str(config_value)
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterBackupConfigGet'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        dictTValue['tConfigKey'] = config_key
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterBackupConfigNotFound'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                else:
                    # 显示所有配置和状态
                    backup_info = OlivaDiceMaster.backup.getBackupInfo(Proc)
                    dictTValue['tBackupResult'] = backup_info
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterBackupInfo'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
            return
        elif flag_is_from_master and isMatchWordStart(tmp_reast_str, 'account', isCommand=True):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'account')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            if isMatchWordStart(tmp_reast_str, 'link'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'link')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                tmp_reast_str_clean = re.sub(r'[；;，,]', ' ', tmp_reast_str)
                tmp_reast_str_list = tmp_reast_str_clean.split()
                if len(tmp_reast_str_list) >= 2:
                    slaveBotHash = tmp_reast_str_list[0].strip()
                    masterBotHash = tmp_reast_str_list[1].strip()
                    success, result = OlivaDiceMaster.accountManager.linkAccount(
                        slaveBotHash, masterBotHash, Proc.Proc_data['bot_info_dict']
                    )
                    dictTValue['tAccountResult'] = result
                    if success:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterAccountLinkSuccess'], dictTValue
                        )
                    else:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterAccountLinkFailed'], dictTValue
                        )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    replyMsgLazyHelpByEvent(plugin_event, 'account')
                    return
            elif isMatchWordStart(tmp_reast_str, 'unlink'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'unlink')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                tmp_reast_str = tmp_reast_str.strip()
                if tmp_reast_str:
                    slaveBotHash = tmp_reast_str
                    success, result = OlivaDiceMaster.accountManager.unlinkAccount(
                        slaveBotHash, Proc.Proc_data['bot_info_dict']
                    )
                    dictTValue['tAccountResult'] = result
                    if success:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterAccountUnlinkSuccess'], dictTValue
                        )
                    else:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterAccountUnlinkFailed'], dictTValue
                        )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    replyMsgLazyHelpByEvent(plugin_event, 'account')
                    return
            elif isMatchWordStart(tmp_reast_str, 'list', fullMatch=True):
                result = OlivaDiceMaster.accountManager.listAccountRelations(
                    Proc.Proc_data['bot_info_dict'], plugin_event
                )
                dictTValue['tAccountResult'] = result
                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                    dictStrCustom['strMasterAccountList'], dictTValue
                )
                replyMsg(plugin_event, tmp_reply_str)
            elif isMatchWordStart(tmp_reast_str, 'show'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'show')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                tmp_reast_str = tmp_reast_str.strip()
                # 如果没有指定hash，使用当前账号
                if tmp_reast_str:
                    botHash = tmp_reast_str
                else:
                    botHash = plugin_event.bot_info.hash
                result = OlivaDiceMaster.accountManager.showAccountInfo(
                    botHash, Proc.Proc_data['bot_info_dict'], plugin_event
                )
                dictTValue['tAccountResult'] = result
                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                    dictStrCustom['strMasterAccountShow'], dictTValue
                )
                replyMsg(plugin_event, tmp_reply_str)
            elif isMatchWordStart(tmp_reast_str, 'import'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'import')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)

                targetBotHash = plugin_event.bot_info.hash
                # 检查是否是 "path" 选项
                if isMatchWordStart(tmp_reast_str, 'path'):
                    tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'path')
                    tmp_reast_str = skipSpaceStart(tmp_reast_str)
                    tmp_reast_str_clean = tmp_reast_str
                    separator_pos = -1
                    for sep in ['；', ';', '，', ',']:
                        pos = tmp_reast_str_clean.find(sep)
                        if pos != -1:
                            separator_pos = pos
                            break
                    if separator_pos != -1:
                        # 有分隔符，分割路径和源Hash
                        zip_path = tmp_reast_str_clean[:separator_pos].strip()
                        source_hash = tmp_reast_str_clean[separator_pos + 1 :].strip()
                        source_hash = re.sub(r'[；;，,]', '', source_hash).strip()
                    else:
                        # 没有分隔符，按空格分割
                        tmp_reast_str_list = tmp_reast_str_clean.split(None, 1)  # 最多分割成2部分
                        zip_path = tmp_reast_str_list[0].strip() if tmp_reast_str_list else None
                        source_hash = tmp_reast_str_list[1].strip() if len(tmp_reast_str_list) > 1 else None
                    if zip_path:
                        success, result, auto_hash = OlivaDiceMaster.accountManager.importAccountDataFromZip(
                            zip_path, targetBotHash, Proc, overwrite=False, sourceBotHash=source_hash
                        )
                        dictTValue['tAccountResult'] = result

                        if success:
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterAccountImportSuccess'], dictTValue
                            )
                        else:
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterAccountImportFailed'], dictTValue
                            )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        replyMsgLazyHelpByEvent(plugin_event, 'account')
                        return
                # 检查是否是 "hash" 选项
                elif isMatchWordStart(tmp_reast_str, 'hash'):
                    tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'hash')
                    tmp_reast_str = skipSpaceStart(tmp_reast_str)
                    tmp_reast_str = tmp_reast_str.strip()

                    if tmp_reast_str:
                        sourceBotHash = tmp_reast_str
                        success, result = OlivaDiceMaster.accountManager.importAccountData(
                            sourceBotHash, targetBotHash, Proc, overwrite=False
                        )
                        dictTValue['tAccountResult'] = result

                        if success:
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterAccountImportSuccess'], dictTValue
                            )
                        else:
                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                                dictStrCustom['strMasterAccountImportFailed'], dictTValue
                            )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        replyMsgLazyHelpByEvent(plugin_event, 'account')
                        return
                else:
                    replyMsgLazyHelpByEvent(plugin_event, 'account')
                    return
            elif isMatchWordStart(tmp_reast_str, 'export'):
                tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'export')
                tmp_reast_str = skipSpaceStart(tmp_reast_str)
                tmp_reast_str = tmp_reast_str.strip()
                # 如果没有指定hash，导出当前账号数据
                if tmp_reast_str:
                    botHash = tmp_reast_str
                else:
                    botHash = plugin_event.bot_info.hash
                success, result = OlivaDiceMaster.accountManager.exportAccountData(botHash, Proc)
                dictTValue['tAccountResult'] = result
                if success:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterAccountExportSuccess'], dictTValue
                    )
                else:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterAccountExportFailed'], dictTValue
                    )
                replyMsg(plugin_event, tmp_reply_str)
            else:
                replyMsgLazyHelpByEvent(plugin_event, 'account')
                return
