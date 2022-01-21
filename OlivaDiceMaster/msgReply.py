# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   msgReply.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivOS
import OlivaDiceMaster
import OlivaDiceCore

import hashlib
import time
import shutil
import os

def unity_init(plugin_event, Proc):
    pass

def data_init(plugin_event, Proc):
    OlivaDiceMaster.msgCustomManager.initMsgCustom(Proc.Proc_data['bot_info_dict'])

def unity_reply(plugin_event, Proc):
    OlivaDiceCore.userConfig.setMsgCount()
    dictTValue = OlivaDiceCore.msgCustom.dictTValue.copy()
    dictTValue['tName'] = plugin_event.data.sender['name']
    dictStrCustom = OlivaDiceCore.msgCustom.dictStrCustomDict[plugin_event.bot_info.hash]
    dictGValue = OlivaDiceCore.msgCustom.dictGValue
    dictTValue.update(dictGValue)

    replyMsg = OlivaDiceCore.msgReply.replyMsg
    isMatchWordStart = OlivaDiceCore.msgReply.isMatchWordStart
    getMatchWordStartRight = OlivaDiceCore.msgReply.getMatchWordStartRight
    skipSpaceStart = OlivaDiceCore.msgReply.skipSpaceStart
    skipToRight = OlivaDiceCore.msgReply.skipToRight
    msgIsCommand = OlivaDiceCore.msgReply.msgIsCommand

    tmp_at_str = OlivOS.messageAPI.PARA.at(plugin_event.base_info['self_id']).CQ()
    tmp_at_str_sub = None
    if 'sub_self_id' in plugin_event.data.extend:
        if plugin_event.data.extend['sub_self_id'] != None:
            tmp_at_str_sub = OlivOS.messageAPI.PARA.at(plugin_event.data.extend['sub_self_id']).CQ()
    tmp_command_str_1 = '.'
    tmp_command_str_2 = '。'
    tmp_command_str_3 = '/'
    tmp_reast_str = plugin_event.data.message
    flag_force_reply = False
    flag_is_command = False
    flag_is_from_host = False
    flag_is_from_group = False
    flag_is_from_group_admin = False
    flag_is_from_group_have_admin = False
    flag_is_from_master = False
    if isMatchWordStart(tmp_reast_str, '[CQ:reply,id='):
        tmp_reast_str = skipToRight(tmp_reast_str, ']')
        tmp_reast_str = tmp_reast_str[1:]
        if isMatchWordStart(tmp_reast_str, tmp_at_str):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, tmp_at_str)
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            flag_force_reply = True
    if isMatchWordStart(tmp_reast_str, tmp_at_str):
        tmp_reast_str = getMatchWordStartRight(tmp_reast_str, tmp_at_str)
        tmp_reast_str = skipSpaceStart(tmp_reast_str)
        flag_force_reply = True
    if tmp_at_str_sub != None:
        if isMatchWordStart(tmp_reast_str, tmp_at_str_sub):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, tmp_at_str_sub)
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            flag_force_reply = True
    [tmp_reast_str, flag_is_command] = msgIsCommand(
        tmp_reast_str,
        OlivaDiceCore.crossHook.dictHookList['prefix']
    )
    if flag_is_command:
        tmp_hagID = None
        flag_is_from_master = OlivaDiceCore.ordinaryInviteManager.isInMasterList(
            plugin_event.bot_info.hash,
            OlivaDiceCore.userConfig.getUserHash(
                plugin_event.data.user_id,
                'user',
                plugin_event.platform['platform']
            )
        )
        if plugin_event.plugin_info['func_type'] == 'group_message':
            if plugin_event.data.host_id != None:
                flag_is_from_host = True
            flag_is_from_group = True
        elif plugin_event.plugin_info['func_type'] == 'private_message':
            flag_is_from_group = False
        if flag_is_from_group:
            if 'role' in plugin_event.data.sender:
                flag_is_from_group_have_admin = True
                if plugin_event.data.sender['role'] in ['owner', 'admin']:
                    flag_is_from_group_admin = True
                elif plugin_event.data.sender['role'] in ['sub_admin']:
                    flag_is_from_group_admin = True
                    flag_is_from_group_sub_admin = True
        if flag_is_from_host and flag_is_from_group:
            tmp_hagID = '%s|%s' % (str(plugin_event.data.host_id), str(plugin_event.data.group_id))
        elif flag_is_from_group:
            tmp_hagID = str(plugin_event.data.group_id)
        flag_hostEnable = True
        if flag_is_from_host:
            flag_hostEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                userId = plugin_event.data.host_id,
                userType = 'host',
                platform = plugin_event.platform['platform'],
                userConfigKey = 'hostEnable',
                botHash = plugin_event.bot_info.hash
            )
        flag_hostLocalEnable = True
        if flag_is_from_host:
            flag_hostLocalEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                userId = plugin_event.data.host_id,
                userType = 'host',
                platform = plugin_event.platform['platform'],
                userConfigKey = 'hostLocalEnable',
                botHash = plugin_event.bot_info.hash
            )
        flag_groupEnable = True
        if flag_is_from_group:
            if flag_is_from_host:
                if flag_hostEnable:
                    flag_groupEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                        userId = tmp_hagID,
                        userType = 'group',
                        platform = plugin_event.platform['platform'],
                        userConfigKey = 'groupEnable',
                        botHash = plugin_event.bot_info.hash
                    )
                else:
                    flag_groupEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                        userId = tmp_hagID,
                        userType = 'group',
                        platform = plugin_event.platform['platform'],
                        userConfigKey = 'groupWithHostEnable',
                        botHash = plugin_event.bot_info.hash
                    )
            else:
                flag_groupEnable = OlivaDiceCore.userConfig.getUserConfigByKey(
                    userId = tmp_hagID,
                    userType = 'group',
                    platform = plugin_event.platform['platform'],
                    userConfigKey = 'groupEnable',
                    botHash = plugin_event.bot_info.hash
                )
        #此频道关闭时中断处理
        if not flag_hostLocalEnable and not flag_force_reply:
            return
        #此群关闭时中断处理
        if not flag_groupEnable and not flag_force_reply:
            return
        if flag_is_from_master and isMatchWordStart(tmp_reast_str, 'oopm'):
            tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'oopm')
            tmp_reast_str = skipSpaceStart(tmp_reast_str)
            tmp_reply_str = None
            if isMatchWordStart(tmp_reast_str, 'show') or isMatchWordStart(tmp_reast_str, 'update'):
                flag_type = None
                flag_api_ok = False
                if isMatchWordStart(tmp_reast_str, 'show'):
                    tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'show')
                    tmp_reast_str = skipSpaceStart(tmp_reast_str)
                    tmp_reast_str = tmp_reast_str.rstrip(' ')
                    flag_type = 'show'
                elif isMatchWordStart(tmp_reast_str, 'update'):
                    tmp_reast_str = getMatchWordStartRight(tmp_reast_str, 'update')
                    tmp_reast_str = skipSpaceStart(tmp_reast_str)
                    tmp_reast_str = tmp_reast_str.rstrip(' ')
                    flag_type = 'update'
                tmp_reply_str_1 = ''
                tmp_reply_str_1_list = []
                tmp_api_data = None
                tmp_api_data_model = None
                tmp_model_branch_select = 'main'
                if tmp_reast_str == '':
                    tmp_omodel_select = 'all'
                else:
                    tmp_omodel_select = tmp_reast_str
                tmp_api_data = OlivaDiceMaster.webTool.GETHttpJson2Dict(
                    OlivaDiceMaster.data.OlivaDiceMaster_oopm_host
                )
                if type(tmp_api_data) == dict:
                    if 'model' in tmp_api_data:
                        if type(tmp_api_data['model']) == dict:
                            tmp_api_data_model = tmp_api_data['model']
                            flag_api_ok = True
                tmp_omodel_list = OlivaDiceCore.crossHook.dictHookList['model']
                tmp_omodel_list_select = []
                for tmp_omodel_list_this in tmp_omodel_list:
                    if tmp_omodel_select.lower() in [tmp_omodel_list_this[0].lower(), 'all']:
                        tmp_omodel_list_select.append(tmp_omodel_list_this)
                if flag_api_ok and flag_type != None and len(tmp_omodel_list_select) > 0:
                    if flag_type == 'show':
                        for tmp_omodel_list_this in tmp_omodel_list_select:
                            tmp_omodel_ver_target = 'N/A'
                            tmp_omodel_ver_compare = '=>'
                            if tmp_api_data_model != None:
                                if tmp_omodel_list_this[0] in tmp_api_data_model:
                                    if tmp_model_branch_select in tmp_api_data_model[tmp_omodel_list_this[0]]:
                                        tmp_omodel_ver_target_version = None
                                        tmp_omodel_ver_target_svn = None
                                        if 'version' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                            tmp_omodel_ver_target_version = tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]['version']
                                        if 'svn' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                            tmp_omodel_ver_target_svn = tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]['svn']
                                        if tmp_omodel_ver_target_version != None and tmp_omodel_ver_target_svn != None:
                                            tmp_omodel_ver_target = '%s(%s)' % (
                                                tmp_omodel_ver_target_version,
                                                tmp_omodel_ver_target_svn
                                            )
                            tmp_oopm_target_path = './plugin/app/%s.opk' % tmp_omodel_list_this[0]
                            if tmp_omodel_list_this[1] == tmp_omodel_ver_target:
                                tmp_omodel_ver_compare = '=='
                            elif tmp_omodel_ver_target == 'N/A':
                                tmp_omodel_ver_compare = '=×'
                            if os.path.exists(tmp_oopm_target_path[:-4]):
                                tmp_omodel_ver_compare = '[SRC]=×'
                            elif not os.path.exists(tmp_oopm_target_path):
                                tmp_omodel_ver_compare = '[DEV]=×'
                            tmp_reply_str_1_list.append(
                                '[%s]\n%s %s %s' % (
                                    tmp_omodel_list_this[0],
                                    tmp_omodel_list_this[1],
                                    tmp_omodel_ver_compare,
                                    tmp_omodel_ver_target
                                )
                            )
                        tmp_reply_str_1 = '\n'.join(tmp_reply_str_1_list)
                        dictTValue['tMasterResult'] = tmp_reply_str_1
                        tmp_reply_str = dictStrCustom['strMasterReply'].format(**dictTValue)
                        replyMsg(plugin_event, tmp_reply_str)
                    elif flag_type == 'update':
                        flag_done = True
                        flag_need_done = False
                        for tmp_omodel_list_this in tmp_omodel_list_select:
                            tmp_omodel_ver_target = 'N/A'
                            tmp_omodel_ver_compare = '=>'
                            flag_have_info = False
                            if tmp_api_data_model != None:
                                if tmp_omodel_list_this[0] in tmp_api_data_model:
                                    if tmp_model_branch_select in tmp_api_data_model[tmp_omodel_list_this[0]]:
                                        tmp_omodel_ver_target_version = None
                                        tmp_omodel_ver_target_svn = None
                                        tmp_omodel_ver_target_opk_path = None
                                        tmp_download_tmp_path = '%s/unity/update/%s.opk' % (
                                            OlivaDiceCore.data.dataDirRoot,
                                            tmp_omodel_list_this[0]
                                        )
                                        tmp_oopm_target_path = './plugin/app/%s.opk' % tmp_omodel_list_this[0]
                                        if 'version' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                            tmp_omodel_ver_target_version = tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]['version']
                                        if 'svn' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                            tmp_omodel_ver_target_svn = tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]['svn']
                                        if 'opk_path' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                            tmp_omodel_ver_target_opk_path = tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]['opk_path']
                                        if tmp_omodel_ver_target_version != None and tmp_omodel_ver_target_svn != None and tmp_omodel_ver_target_opk_path != None:
                                            flag_have_info = True
                                        if flag_have_info:
                                            tmp_omodel_ver_target = '%s(%s)' % (
                                                tmp_omodel_ver_target_version,
                                                tmp_omodel_ver_target_svn
                                            )
                                            if tmp_omodel_list_this[1] == tmp_omodel_ver_target:
                                                tmp_omodel_ver_compare = '=='
                                            elif tmp_omodel_ver_target == 'N/A':
                                                tmp_omodel_ver_compare = '=×'
                                            if os.path.exists(tmp_oopm_target_path[:-4]):
                                                tmp_omodel_ver_compare = '[SRC]=×'
                                            elif not os.path.exists(tmp_oopm_target_path):
                                                tmp_omodel_ver_compare = '[DEV]=×'
                                            dictTValue['tMasterOopkNameList'] = '[%s]\n%s %s %s' % (
                                                tmp_omodel_list_this[0],
                                                tmp_omodel_list_this[1],
                                                tmp_omodel_ver_compare,
                                                tmp_omodel_ver_target
                                            )
                                            flag_done_this = True
                                            while tmp_omodel_ver_compare in ['=>']:
                                                flag_download = False
                                                flag_copy = False
                                                try:
                                                    flag_download = OlivaDiceMaster.webTool.GETHttpFile(
                                                        tmp_omodel_ver_target_opk_path,
                                                        tmp_download_tmp_path
                                                    )
                                                except:
                                                    flag_download = False
                                                if not flag_download:
                                                    tmp_reply_str = dictStrCustom['strMasterOopmDownloadFailed'].format(**dictTValue)
                                                    replyMsg(plugin_event, tmp_reply_str)
                                                    flag_done = False
                                                    flag_done_this = False
                                                    break
                                                try:
                                                    shutil.copyfile(
                                                        tmp_download_tmp_path,
                                                        tmp_oopm_target_path
                                                    )
                                                    flag_copy = True
                                                except:
                                                    flag_copy = False
                                                if not flag_copy:
                                                    tmp_reply_str = dictStrCustom['strMasterOopmCopyFailed'].format(**dictTValue)
                                                    replyMsg(plugin_event, tmp_reply_str)
                                                    flag_done = False
                                                    flag_done_this = False
                                                    break
                                                tmp_reply_str = dictStrCustom['strMasterOopmUpdate'].format(**dictTValue)
                                                replyMsg(plugin_event, tmp_reply_str)
                                                flag_need_done = True
                                                break
                                            if tmp_omodel_ver_compare in ['[SRC]=×']:
                                                tmp_reply_str = dictStrCustom['strMasterOopmUpdateNotSkipSrc'].format(**dictTValue)
                                                replyMsg(plugin_event, tmp_reply_str)
                                            elif tmp_omodel_ver_compare in ['[DEV]=×']:
                                                tmp_reply_str = dictStrCustom['strMasterOopmUpdateNotSkipDev'].format(**dictTValue)
                                                replyMsg(plugin_event, tmp_reply_str)
                                            if not flag_done_this:
                                                break
                        if flag_done and flag_need_done:
                            tmp_reply_str = dictStrCustom['strMasterOopmUpdateAllDone'].format(**dictTValue)
                            replyMsg(plugin_event, tmp_reply_str)
                            time.sleep(1)
                            Proc.set_restart()
                        elif flag_done and not flag_need_done:
                            tmp_reply_str = dictStrCustom['strMasterOopmUpdateNotNeed'].format(**dictTValue)
                            replyMsg(plugin_event, tmp_reply_str)
                elif flag_api_ok:
                    tmp_reply_str = dictStrCustom['strMasterOopmNotMatch'].format(**dictTValue)
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    tmp_reply_str = dictStrCustom['strMasterOopmApiFailed'].format(**dictTValue)
                    replyMsg(plugin_event, tmp_reply_str)
            return
