# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   msgReplyModel.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   None
'''

import OlivaDiceCore
import OlivaDiceMaster

import os
import shutil
import time

def replyOOPM_ShowUpdate_command(
    plugin_event,
    Proc,
    tmp_reast_str,
    dictStrCustom,
    dictTValue,
    skipSpaceStart,
    getMatchWordStartRight,
    isMatchWordStart,
    replyMsg,
    flagReply = True
):
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
            if flagReply:
                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterReply'], dictTValue)
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
                                        if flagReply:
                                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmDownloadFailed'], dictTValue)
                                            replyMsg(plugin_event, tmp_reply_str)
                                        else:
                                            OlivaDiceMaster.data.globalProc.log(3, '模块下载失败!' , [
                                                ('OlivaDice', 'default'),
                                                ('autoupdate', 'default')
                                            ])
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
                                        if flagReply:
                                            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmCopyFailed'], dictTValue)
                                            replyMsg(plugin_event, tmp_reply_str)
                                        else:
                                            OlivaDiceMaster.data.globalProc.log(3, '转移流程中出错!' , [
                                                ('OlivaDice', 'default'),
                                                ('autoupdate', 'default')
                                            ])
                                        flag_done = False
                                        flag_done_this = False
                                        break
                                    if flagReply:
                                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmUpdate'], dictTValue)
                                        replyMsg(plugin_event, tmp_reply_str)
                                    else:
                                        OlivaDiceMaster.data.globalProc.log(2, dictTValue['tMasterOopkNameList'] , [
                                            ('OlivaDice', 'default'),
                                            ('autoupdate', 'default')
                                        ])
                                    flag_need_done = True
                                    break
                                if tmp_omodel_ver_compare in ['[SRC]=×']:
                                    if flagReply:
                                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmUpdateNotSkipSrc'], dictTValue)
                                        replyMsg(plugin_event, tmp_reply_str)
                                    else:
                                        OlivaDiceMaster.data.globalProc.log(2, dictTValue['tMasterOopkNameList'] , [
                                            ('OlivaDice', 'default'),
                                            ('autoupdate', 'default')
                                        ])
                                elif tmp_omodel_ver_compare in ['[DEV]=×']:
                                    if flagReply:
                                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmUpdateNotSkipDev'], dictTValue)
                                        replyMsg(plugin_event, tmp_reply_str)
                                    else:
                                        OlivaDiceMaster.data.globalProc.log(2, dictTValue['tMasterOopkNameList'] , [
                                            ('OlivaDice', 'default'),
                                            ('autoupdate', 'default')
                                        ])
                                if not flag_done_this:
                                    break
            if flag_done and flag_need_done:
                if flagReply:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmUpdateAllDone'], dictTValue)
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    OlivaDiceMaster.data.globalProc.log(2, '已全部更新成功，即将重载' , [
                        ('OlivaDice', 'default'),
                        ('autoupdate', 'default')
                    ])
                time.sleep(1)
                Proc.set_restart()
            elif flag_done and not flag_need_done:
                if flagReply:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmUpdateNotNeed'], dictTValue)
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    OlivaDiceMaster.data.globalProc.log(2, '已检测完毕，无需更新' , [
                        ('OlivaDice', 'default'),
                        ('autoupdate', 'default')
                    ])
    elif flag_api_ok:
        if flagReply:
            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmNotMatch'], dictTValue)
            replyMsg(plugin_event, tmp_reply_str)
        else:
            OlivaDiceMaster.data.globalProc.log(3, '更新失败: 未找到匹配模块' , [
                ('OlivaDice', 'default'),
                ('autoupdate', 'default')
            ])
    else:
        if flagReply:
            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(dictStrCustom['strMasterOopmApiFailed'], dictTValue)
            replyMsg(plugin_event, tmp_reply_str)
        else:
            OlivaDiceMaster.data.globalProc.log(3, '更新失败: API连接失败' , [
                ('OlivaDice', 'default'),
                ('autoupdate', 'default')
            ])
