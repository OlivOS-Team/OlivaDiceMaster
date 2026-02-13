# -*- encoding: utf-8 -*-
"""
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
"""

import OlivaDiceCore
import OlivaDiceMaster

import os
import shutil
import time


def find_plugin_path_recursive(base_path, namespace, max_depth=10):
    """
    递归查找插件的实际路径
    """

    def search_recursive(current_path, current_depth):
        if current_depth > max_depth:
            return (None, None)
        try:
            items = os.listdir(current_path)
        except:
            return (None, None)
        opk_file = namespace + '.opk'
        if opk_file in items:
            return ('opk', os.path.join(current_path, opk_file))
        if namespace in items:
            src_path = os.path.join(current_path, namespace)
            if os.path.isdir(src_path):
                app_json = os.path.join(src_path, 'app.json')
                if os.path.exists(app_json):
                    return ('src', src_path)
        for item in items:
            if item.startswith('.'):
                continue
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                result = search_recursive(item_path, current_depth + 1)
                if result[0] != None:
                    return result
        return (None, None)

    return search_recursive(base_path, 0)


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
    flagReply=True,
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
    tmp_api_data = OlivaDiceMaster.webTool.GETHttpJson2Dict(OlivaDiceMaster.data.OlivaDiceMaster_oopm_host)
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
                                tmp_omodel_ver_target_version = tmp_api_data_model[tmp_omodel_list_this[0]][
                                    tmp_model_branch_select
                                ]['version']
                            if 'svn' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                tmp_omodel_ver_target_svn = tmp_api_data_model[tmp_omodel_list_this[0]][
                                    tmp_model_branch_select
                                ]['svn']
                            if tmp_omodel_ver_target_version != None and tmp_omodel_ver_target_svn != None:
                                tmp_omodel_ver_target = '%s(%s)' % (
                                    tmp_omodel_ver_target_version,
                                    tmp_omodel_ver_target_svn,
                                )
                plugin_exist_type, plugin_path = find_plugin_path_recursive('./plugin/app', tmp_omodel_list_this[0])
                if tmp_omodel_list_this[1] == tmp_omodel_ver_target:
                    tmp_omodel_ver_compare = '=='
                elif tmp_omodel_ver_target == 'N/A':
                    tmp_omodel_ver_compare = '=×'
                if plugin_exist_type == 'src':
                    tmp_omodel_ver_compare = '[SRC]=×'
                elif plugin_exist_type == None:
                    tmp_omodel_ver_compare = '[DEV]=×'
                tmp_reply_str_1_list.append(
                    '[%s]\n%s %s %s'
                    % (tmp_omodel_list_this[0], tmp_omodel_list_this[1], tmp_omodel_ver_compare, tmp_omodel_ver_target)
                )
            tmp_reply_str_1 = '\n'.join(tmp_reply_str_1_list)
            dictTValue['tMasterResult'] = tmp_reply_str_1
            if flagReply:
                tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                    dictStrCustom['strMasterReply'], dictTValue
                )
                replyMsg(plugin_event, tmp_reply_str)
        elif flag_type == 'update':
            flag_done = True
            flag_need_done = False
            update_plan_list = []
            blocked_update = False
            blocked_update_list = []
            # 全局检查
            for tmp_omodel_list_this in tmp_omodel_list_select:
                tmp_omodel_ver_target = 'N/A'
                tmp_omodel_ver_compare = '=>'
                tmp_omodel_ver_target_opk_path = None
                flag_have_info = False
                # 查找插件的实际位置，确定正确的目标路径
                plugin_exist_type, plugin_actual_path = find_plugin_path_recursive(
                    './plugin/app', tmp_omodel_list_this[0]
                )
                if plugin_exist_type == 'opk' and plugin_actual_path != None:
                    tmp_oopm_target_path = plugin_actual_path
                else:
                    tmp_oopm_target_path = './plugin/app/%s.opk' % tmp_omodel_list_this[0]
                tmp_download_tmp_path = '%s/unity/update/%s.opk' % (
                    OlivaDiceCore.data.dataDirRoot,
                    tmp_omodel_list_this[0],
                )
                if tmp_api_data_model != None:
                    if tmp_omodel_list_this[0] in tmp_api_data_model:
                        if tmp_model_branch_select in tmp_api_data_model[tmp_omodel_list_this[0]]:
                            tmp_omodel_ver_target_version = None
                            tmp_omodel_ver_target_svn = None
                            if 'version' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                tmp_omodel_ver_target_version = tmp_api_data_model[tmp_omodel_list_this[0]][
                                    tmp_model_branch_select
                                ]['version']
                            if 'svn' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                tmp_omodel_ver_target_svn = tmp_api_data_model[tmp_omodel_list_this[0]][
                                    tmp_model_branch_select
                                ]['svn']
                            if 'opk_path' in tmp_api_data_model[tmp_omodel_list_this[0]][tmp_model_branch_select]:
                                tmp_omodel_ver_target_opk_path = tmp_api_data_model[tmp_omodel_list_this[0]][
                                    tmp_model_branch_select
                                ]['opk_path']
                            if (
                                tmp_omodel_ver_target_version != None
                                and tmp_omodel_ver_target_svn != None
                                and tmp_omodel_ver_target_opk_path != None
                            ):
                                flag_have_info = True
                                tmp_omodel_ver_target = '%s(%s)' % (
                                    tmp_omodel_ver_target_version,
                                    tmp_omodel_ver_target_svn,
                                )
                if not flag_have_info:
                    tmp_omodel_ver_compare = '=×'
                elif tmp_omodel_list_this[1] == tmp_omodel_ver_target:
                    tmp_omodel_ver_compare = '=='
                elif tmp_omodel_ver_target == 'N/A':
                    tmp_omodel_ver_compare = '=×'
                if plugin_exist_type == 'src':
                    tmp_omodel_ver_compare = '[SRC]=×'
                elif plugin_exist_type == None:
                    tmp_omodel_ver_compare = '[DEV]=×'
                tMasterOopkNameList = '[%s]\n%s %s %s' % (
                    tmp_omodel_list_this[0],
                    tmp_omodel_list_this[1],
                    tmp_omodel_ver_compare,
                    tmp_omodel_ver_target,
                )
                update_plan_list.append({
                    'name': tmp_omodel_list_this[0],
                    'current_ver': tmp_omodel_list_this[1],
                    'target_ver': tmp_omodel_ver_target,
                    'compare': tmp_omodel_ver_compare,
                    'exist_type': plugin_exist_type,
                    'download_url': tmp_omodel_ver_target_opk_path,
                    'download_tmp_path': tmp_download_tmp_path,
                    'target_path': tmp_oopm_target_path,
                    'tMasterOopkNameList': tMasterOopkNameList,
                })
                if plugin_exist_type in ['src', None]:
                    blocked_update = True
                    blocked_update_list.append(tmp_omodel_list_this[0])
            if blocked_update:
                if flagReply:
                    dictTValue['tMasterResult'] = '检测到SRC/DEV模式模块[%s]，已取消更新。' % ','.join(
                        blocked_update_list
                    )
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterReply'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    if OlivaDiceMaster.data.globalProc != None:
                        OlivaDiceMaster.data.globalProc.log(
                            2,
                            '检测到SRC/DEV模式模块[%s]，停止自动更新。' % ','.join(blocked_update_list),
                            [('OlivaDice', 'default'), ('autoupdate', 'default')],
                        )
                return
            # 逐个更新
            for update_plan in update_plan_list:
                dictTValue['tMasterOopkNameList'] = update_plan['tMasterOopkNameList']

                if update_plan['compare'] in ['[SRC]=×']:
                    if flagReply:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterOopmUpdateNotSkipSrc'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        OlivaDiceMaster.data.globalProc.log(
                            2, dictTValue['tMasterOopkNameList'], [('OlivaDice', 'default'), ('autoupdate', 'default')]
                        )
                    continue
                elif update_plan['compare'] in ['[DEV]=×']:
                    if flagReply:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterOopmUpdateNotSkipDev'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        OlivaDiceMaster.data.globalProc.log(
                            2, dictTValue['tMasterOopkNameList'], [('OlivaDice', 'default'), ('autoupdate', 'default')]
                        )
                    continue
                if update_plan['compare'] not in ['=>']:
                    continue
                flag_download = False
                flag_copy = False
                try:
                    flag_download = OlivaDiceMaster.webTool.GETHttpFile(
                        update_plan['download_url'], update_plan['download_tmp_path']
                    )
                except:
                    flag_download = False
                if not flag_download:
                    if flagReply:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterOopmDownloadFailed'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        OlivaDiceMaster.data.globalProc.log(
                            3, '模块下载失败!', [('OlivaDice', 'default'), ('autoupdate', 'default')]
                        )
                    flag_done = False
                    break
                try:
                    shutil.copyfile(update_plan['download_tmp_path'], update_plan['target_path'])
                    flag_copy = True
                except:
                    flag_copy = False
                if not flag_copy:
                    if flagReply:
                        tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                            dictStrCustom['strMasterOopmCopyFailed'], dictTValue
                        )
                        replyMsg(plugin_event, tmp_reply_str)
                    else:
                        OlivaDiceMaster.data.globalProc.log(
                            3, '转移流程中出错!', [('OlivaDice', 'default'), ('autoupdate', 'default')]
                        )
                    flag_done = False
                    break
                if flagReply:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterOopmUpdate'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    OlivaDiceMaster.data.globalProc.log(
                        2, dictTValue['tMasterOopkNameList'], [('OlivaDice', 'default'), ('autoupdate', 'default')]
                    )
                flag_need_done = True
            if flag_done and flag_need_done:
                if flagReply:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterOopmUpdateAllDone'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    OlivaDiceMaster.data.globalProc.log(
                        2, '已全部更新成功，即将重载', [('OlivaDice', 'default'), ('autoupdate', 'default')]
                    )
                time.sleep(1)
                Proc.set_restart()
            elif flag_done and not flag_need_done:
                if flagReply:
                    tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                        dictStrCustom['strMasterOopmUpdateNotNeed'], dictTValue
                    )
                    replyMsg(plugin_event, tmp_reply_str)
                else:
                    OlivaDiceMaster.data.globalProc.log(
                        2, '已检测完毕，无需更新', [('OlivaDice', 'default'), ('autoupdate', 'default')]
                    )
    elif flag_api_ok:
        if flagReply:
            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                dictStrCustom['strMasterOopmNotMatch'], dictTValue
            )
            replyMsg(plugin_event, tmp_reply_str)
        else:
            OlivaDiceMaster.data.globalProc.log(
                3, '更新失败: 未找到匹配模块', [('OlivaDice', 'default'), ('autoupdate', 'default')]
            )
    else:
        if flagReply:
            tmp_reply_str = OlivaDiceCore.msgCustomManager.formatReplySTR(
                dictStrCustom['strMasterOopmApiFailed'], dictTValue
            )
            replyMsg(plugin_event, tmp_reply_str)
        else:
            OlivaDiceMaster.data.globalProc.log(
                3, '更新失败: API连接失败', [('OlivaDice', 'default'), ('autoupdate', 'default')]
            )
