# -*- encoding: utf-8 -*-
r"""
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/

@File      :   accountManager.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2026, OlivOS-Team
@Desc      :   多账号连接管理模块
"""

import OlivOS
import OlivaDiceCore
import OlivaDiceMaster

import os
import json
import shutil
import re
import zipfile
import tempfile
import copy


def get_bot_display_name(botHash, bot_info, plugin_event=None):
    """
    获取bot的显示名称
    """
    bot_name = '未知'
    # 优先通过API调用获取名称
    try:
        # 如果plugin_event为None，或者plugin_event的bot_info与目标botHash不匹配，构建fake_event
        # 这样可以确保获取的是正确账号的名称
        if plugin_event is None or (hasattr(plugin_event, 'bot_info') and plugin_event.bot_info.hash != botHash):
            fake_event = OlivOS.API.Event(
                OlivOS.contentAPI.fake_sdk_event(bot_info=bot_info, fakename='OlivaDiceMaster'), None
            )
            res_data = fake_event.get_login_info(bot_info)
        else:
            res_data = plugin_event.get_login_info(bot_info)

        if res_data and res_data.get('active') and 'data' in res_data:
            bot_name = res_data['data'].get('name', '未知')
            if bot_name and bot_name != '未知':
                return bot_name
    except Exception:
        pass
    # 尝试从用户配置中获取保存的昵称
    try:
        if hasattr(bot_info, 'id') and hasattr(bot_info, 'platform') and bot_info.platform:
            bot_id = str(bot_info.id)
            bot_user_hash = OlivaDiceCore.userConfig.getUserHash(
                userId=bot_id, userType='user', platform=bot_info.platform['platform']
            )
            saved_name = OlivaDiceCore.userConfig.getUserConfigByKeyWithHash(
                userHash=bot_user_hash, userConfigKey='userName', botHash=botHash
            )
            if saved_name and saved_name != '用户':
                bot_name = saved_name
    except Exception:
        pass
    return bot_name


def checkCircularDependency(slaveBotHash, masterBotHash, relations):
    """
    检查是否存在循环依赖
    """
    if slaveBotHash == masterBotHash:
        return True, '从账号和主账号不能相同'

    # 辅助函数：查找某个账号的主账号
    def find_master(bot_hash):
        for master, slaves in relations.items():
            if bot_hash in slaves:
                return master
        return None

    # 从 masterBotHash 向上查找，看是否会在链中遇到 slaveBotHash
    visited = set()
    queue = [masterBotHash]
    while queue:
        current = queue.pop(0)
        if current == slaveBotHash:
            return True, '检测到循环依赖：主账号已经在从账号的关系链中'
        if current in visited:
            continue
        visited.add(current)
        # 获取 current 的主账号
        master = find_master(current)
        if master:
            queue.append(master)
    # 从 slaveBotHash 向上查找，看是否会在链中遇到 masterBotHash
    visited2 = set()
    queue2 = [slaveBotHash]
    while queue2:
        current = queue2.pop(0)
        if current == masterBotHash:
            return True, '检测到循环依赖：从账号已经在主账号的关系链中'
        if current in visited2:
            continue
        visited2.add(current)
        # 获取 current 的主账号
        master = find_master(current)
        if master:
            queue2.append(master)
    # 检查 slaveBotHash 的所有从账号，看它们是否会在链中回到 masterBotHash
    slaveBotHash_slaves = relations.get(slaveBotHash, [])
    for slave_of_slave in slaveBotHash_slaves:
        visited_slave = set()
        queue_slave = [slave_of_slave]
        while queue_slave:
            current_slave = queue_slave.pop(0)
            if current_slave == masterBotHash:
                return True, '检测到循环依赖：从账号的从账号已经在主账号的关系链中'
            if current_slave in visited_slave:
                continue
            visited_slave.add(current_slave)
            # 检查 current_slave 是否在 masterBotHash 的上级链中
            visited_master = set()
            queue_master = [masterBotHash]
            while queue_master:
                check_master = queue_master.pop(0)
                if check_master == current_slave:
                    return True, '检测到循环依赖：建立此关系后会形成循环'
                if check_master in visited_master:
                    break
                visited_master.add(check_master)
                # 获取 check_master 的主账号
                master = find_master(check_master)
                if master:
                    queue_master.append(master)
            # 继续查找 current_slave 的主账号
            master = find_master(current_slave)
            if master:
                queue_slave.append(master)
    return False, ''


def linkAccount(slaveBotHash, masterBotHash, bot_info_dict=None):
    """
    建立主从关系（为从账号添加一个主账号）
    """
    try:
        # 验证hash是否存在
        if bot_info_dict is not None:
            if slaveBotHash not in bot_info_dict:
                return False, f'从账号 {slaveBotHash} 不存在于当前进程的账号列表中'
            if masterBotHash not in bot_info_dict:
                return False, f'主账号 {masterBotHash} 不存在于当前进程的账号列表中'
        # 获取当前的关系配置
        relations = OlivaDiceCore.console.getAllAccountRelations()
        # 检查账号不能为unity
        # 无论是主账号还是从账号都不能为unity
        if slaveBotHash.lower() == 'unity':
            return False, '从账号不能为unity'
        if masterBotHash.lower() == 'unity':
            return False, '主账号不能为unity'
        # 检查 slaveBotHash 是否已经有主账号
        current_masters = OlivaDiceCore.console.getMasterBotHashList(slaveBotHash)
        if current_masters:
            if masterBotHash in current_masters:
                return False, f'账号 {slaveBotHash} 已经是 {masterBotHash} 的从账号'
            else:
                current_master = current_masters[0]
                return (
                    False,
                    f'账号 {slaveBotHash} 已经是 {current_master} 的从账号，一个从账号只能有一个主账号，请先断开现有关系',
                )
        # 检查 masterBotHash 是否已经是某个账号的从账号
        # 如果 masterBotHash 是从账号，则它不能作为主账号接受新的从账号
        master_masters = OlivaDiceCore.console.getMasterBotHashList(masterBotHash)
        if master_masters:
            master_master = master_masters[0]
            return False, f'账号 {masterBotHash} 已经是 {master_master} 的从账号，从账号不能作为主账号'
        # 检查循环依赖（保险起见）
        hasCircular, errorMsg = checkCircularDependency(slaveBotHash, masterBotHash, relations)
        if hasCircular:
            return False, errorMsg
        # 设置主从关系
        OlivaDiceCore.console.setAccountRelation(slaveBotHash, masterBotHash)
        OlivaDiceCore.console.saveAccountRelationConfig()
        return True, f'已建立主从关系: {slaveBotHash}(从) -> {masterBotHash}(主)'
    except Exception as e:
        return False, f'建立主从关系失败: {str(e)}'


def unlinkAccount(slaveBotHash, masterBotHash=None, bot_info_dict=None):
    """
    断开主从关系
    如果账号是主账号，断开所有以它为主账号的从账号关系
    如果账号是从账号，断开它与主账号的关系（从账号只会有一个主账号）
    """
    try:
        if bot_info_dict is not None:
            if slaveBotHash not in bot_info_dict:
                return False, f'账号 {slaveBotHash} 不存在于当前进程的账号列表中'

        # 检查是否是主账号（在relations中是key）
        relations = OlivaDiceCore.console.getAllAccountRelations()
        if slaveBotHash in relations:
            # 是主账号，断开所有从账号与它的关系
            slave_count = len(relations[slaveBotHash])
            if 'unity' in OlivaDiceCore.console.dictAccountRelationConfig:
                if 'relations' in OlivaDiceCore.console.dictAccountRelationConfig['unity']:
                    if slaveBotHash in OlivaDiceCore.console.dictAccountRelationConfig['unity']['relations']:
                        del OlivaDiceCore.console.dictAccountRelationConfig['unity']['relations'][slaveBotHash]
            OlivaDiceCore.console.saveAccountRelationConfig()
            return True, f'已断开主从关系: 主账号 {slaveBotHash} 与 {slave_count} 个从账号的关系已断开'

        # 检查是否是从账号（在某个主账号的value列表中）
        masterBotHash = OlivaDiceCore.console.getMasterBotHash(slaveBotHash)
        if masterBotHash:
            # 是从账号，断开与主账号的关系
            OlivaDiceCore.console.removeAccountRelation(slaveBotHash, masterBotHash)
            OlivaDiceCore.console.saveAccountRelationConfig()
            return True, f'已断开主从关系: {slaveBotHash}(从) ->/<- {masterBotHash}(主)'
        # 既不是主账号也不是从账号
        return False, f'账号 {slaveBotHash} 未建立主从关系'
    except Exception as e:
        return False, f'断开主从关系失败: {str(e)}'


def listAccountRelations(bot_info_dict, plugin_event=None):
    """
    列出所有账号和主从关系
    """
    try:
        relations = OlivaDiceCore.console.getAllAccountRelations()
        result_lines = []
        result_lines.append('=== 账号列表 ===')
        # relations 已经是 master_to_slaves 格式
        master_to_slaves = relations
        # 遍历所有账号
        for botHash in bot_info_dict:
            bot_name = get_bot_display_name(botHash, bot_info_dict[botHash], plugin_event)
            bot_id = bot_info_dict[botHash].id if hasattr(bot_info_dict[botHash], 'id') else '未知'
            # 检查账号角色
            masterHash = OlivaDiceCore.console.getMasterBotHash(botHash)
            if masterHash:
                # 从账号
                master_name = (
                    get_bot_display_name(masterHash, bot_info_dict[masterHash], plugin_event)
                    if masterHash in bot_info_dict
                    else '未知'
                )
                result_lines.append(f'[从账号] {bot_name}({bot_id})')
                result_lines.append(f'  Hash: {botHash}')
                result_lines.append(f'  主账号: {master_name} ({masterHash})')
            elif botHash in master_to_slaves:
                # 主账号
                result_lines.append(f'[主账号] {bot_name}({bot_id})')
                result_lines.append(f'  Hash: {botHash}')
                result_lines.append(f'  从账号数量: {len(master_to_slaves[botHash])}')
                for slave in master_to_slaves[botHash]:
                    slave_name = (
                        get_bot_display_name(slave, bot_info_dict[slave], plugin_event)
                        if slave in bot_info_dict
                        else '未知'
                    )
                    result_lines.append(f'    - {slave_name} ({slave})')
            else:
                # 独立账号
                result_lines.append(f'[独立账号] {bot_name}({bot_id})')
                result_lines.append(f'  Hash: {botHash}')
            result_lines.append('')
        return '\n'.join(result_lines)
    except Exception as e:
        return f'列出账号关系失败: {str(e)}'


def showAccountInfo(botHash, bot_info_dict, plugin_event=None):
    """
    显示指定账号的详细信息
    """
    try:
        if botHash not in bot_info_dict:
            return f'未找到账号: {botHash}'
        bot_name = get_bot_display_name(botHash, bot_info_dict[botHash], plugin_event)
        bot_id = bot_info_dict[botHash].id if hasattr(bot_info_dict[botHash], 'id') else '未知'
        result_lines = []
        result_lines.append('=== 账号信息 ===')
        result_lines.append(f'名称: {bot_name}')
        result_lines.append(f'ID: {bot_id}')
        result_lines.append(f'Hash: {botHash}')
        # 检查主从关系
        relations = OlivaDiceCore.console.getAllAccountRelations()
        masterHash = OlivaDiceCore.console.getMasterBotHash(botHash)
        if masterHash:
            # 从账号
            result_lines.append('角色: 从账号')
            master_name = (
                get_bot_display_name(masterHash, bot_info_dict[masterHash], plugin_event)
                if masterHash in bot_info_dict
                else '未知'
            )
            result_lines.append(f'主账号: {master_name} ({masterHash})')
            result_lines.append('数据重定向: 已启用')
        else:
            # 主账号或独立账号
            slaves = relations.get(botHash, [])
            if slaves:
                result_lines.append('角色: 主账号')
                result_lines.append(f'从账号数量: {len(slaves)}')
                for slave in slaves:
                    slave_name = (
                        get_bot_display_name(slave, bot_info_dict[slave], plugin_event)
                        if slave in bot_info_dict
                        else '未知'
                    )
                    result_lines.append(f'  - {slave_name} ({slave})')
            else:
                result_lines.append('角色: 独立账号')
                result_lines.append('主从关系: 未建立')
        return '\n'.join(result_lines)
    except Exception as e:
        return f'获取账号信息失败: {str(e)}'


def exportAccountData(sourceBotHash, Proc, export_path=None):
    """
    压缩包导出账号数据
    """
    try:
        source_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, sourceBotHash)
        if not os.path.exists(source_dir):
            return False, f'源账号数据不存在: {sourceBotHash}'
        export_root = OlivaDiceMaster.data.exportPath
        # 确定导出路径
        if export_path is None:
            if not os.path.exists(export_root):
                os.makedirs(export_root)
            export_path = os.path.join(export_root, f'account_export_{sourceBotHash}.zip')
        else:
            if os.path.isdir(export_path):
                export_path = os.path.join(export_path, f'account_export_{sourceBotHash}.zip')
        if os.path.exists(export_path):
            os.remove(export_path)
        # 创建压缩包
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, relative_path)
        return True, f'账号数据已导出到: {export_path.replace(chr(92), "/")}'
    except Exception as e:
        return False, f'导出账号数据失败: {str(e)}'


def _performAccountDataImport(source_dir, sourceBotHash, targetBotHash, Proc, overwrite=False):
    """
    执行账号数据导入的逻辑
    """
    try:
        # 创建目标目录
        target_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, targetBotHash)
        # 备份目标账号数据
        backup_path = None
        if os.path.exists(target_dir):
            backup_base_dir = OlivaDiceMaster.data.exportPath
            backup_filename = f'account_import_{targetBotHash}.zip'
            backup_path = os.path.join(backup_base_dir, backup_filename)
            os.makedirs(backup_base_dir, exist_ok=True)
            if os.path.exists(backup_path):
                os.remove(backup_path)
            # 创建压缩备份
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(target_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, target_dir)
                        zipf.write(file_path, relative_path)
            if Proc:
                Proc.log(2, f'已备份目标账号数据到: {backup_path.replace(chr(92), "/")}')
        # 先清空内存中目标账号相关的所有数据
        _clearBotHashFromMemory(targetBotHash)
        _copyAndReplaceBotHash(source_dir, target_dir, sourceBotHash, targetBotHash)
        # 重新加载目标账号的数据到内存
        try:
            _loadBotHashToMemory(targetBotHash)
            if Proc:
                Proc.log(2, f'已重新加载目标账号 {targetBotHash} 的数据到内存')
        except Exception as reload_error:
            if Proc:
                Proc.log(3, f'重新加载数据时出现警告: {str(reload_error)}')
        return True, None, backup_path
    except Exception as e:
        return False, f'执行导入操作失败: {str(e)}', None


def _clearBotHashFromMemory(botHash):
    """
    清空内存中指定账号的所有数据
    """
    try:
        if hasattr(OlivaDiceCore.userConfig, 'dictUserConfigData'):
            for userHash in list(OlivaDiceCore.userConfig.dictUserConfigData.keys()):
                if botHash in OlivaDiceCore.userConfig.dictUserConfigData[userHash]:
                    del OlivaDiceCore.userConfig.dictUserConfigData[userHash][botHash]
                    if not OlivaDiceCore.userConfig.dictUserConfigData[userHash]:
                        del OlivaDiceCore.userConfig.dictUserConfigData[userHash]
        if hasattr(OlivaDiceCore.pcCard, 'dictPcCardData'):
            if botHash in OlivaDiceCore.pcCard.dictPcCardData:
                del OlivaDiceCore.pcCard.dictPcCardData[botHash]
    except Exception:
        pass


def _loadBotHashToMemory(botHash):
    """
    将指定账号的数据加载到内存
    """
    try:
        # 加载用户配置数据
        user_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, botHash, 'user')
        if os.path.exists(user_dir):
            userHash_list = os.listdir(user_dir)
            for userHash in userHash_list:
                user_config_path = os.path.join(user_dir, userHash)
                if os.path.isfile(user_config_path):
                    try:
                        with open(user_config_path, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                        if userHash not in OlivaDiceCore.userConfig.dictUserConfigData:
                            OlivaDiceCore.userConfig.dictUserConfigData[userHash] = {}
                        # 只更新该botHash的数据
                        if botHash in user_data:
                            OlivaDiceCore.userConfig.dictUserConfigData[userHash][botHash] = user_data[botHash]
                    except Exception:
                        pass
        # 加载人物卡数据
        pccard_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, botHash, 'pcCard', 'data')
        if os.path.exists(pccard_dir):
            pcHash_list = os.listdir(pccard_dir)
            for pcHash in pcHash_list:
                try:
                    OlivaDiceCore.pcCard.dataPcCardLoad(botHash, pcHash)
                except Exception:
                    pass
    except Exception:
        pass


def importAccountData(sourceBotHash, targetBotHash, Proc, overwrite=False):
    """
    从现有账号导入账号数据
    """
    try:
        # 检查账号不能为unity
        if sourceBotHash.lower() == 'unity':
            return False, '源账号不能为unity'
        if targetBotHash.lower() == 'unity':
            return False, '目标账号不能为unity'
        # 获取进程内的账号列表并验证
        bot_info_dict = None
        if Proc:
            try:
                bot_info_dict = Proc.Proc_data.get('bot_info_dict', None)
            except Exception:
                pass
        if bot_info_dict is not None:
            if sourceBotHash not in bot_info_dict:
                return False, f'源账号 {sourceBotHash} 不存在于当前进程的账号列表中'
            if targetBotHash not in bot_info_dict:
                return False, f'目标账号 {targetBotHash} 不存在于当前进程的账号列表中'
        # 检查源账号数据是否存在
        source_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, sourceBotHash)
        if not os.path.exists(source_dir):
            return False, f'源账号数据不存在: {sourceBotHash}'
        # 执行导入
        success, error_msg, backup_path = _performAccountDataImport(
            source_dir, sourceBotHash, targetBotHash, Proc, overwrite
        )
        if not success:
            return False, error_msg
        # 构建结果消息
        result_msg = f'账号数据已从 {sourceBotHash} 导入到 {targetBotHash}'
        if backup_path:
            result_msg += f'\n备份已保存到: {backup_path.replace(chr(92), "/")}'
        return True, result_msg
    except Exception as e:
        return False, f'导入账号数据失败: {str(e)}'


def importAccountDataFromZip(zip_path, targetBotHash, Proc, overwrite=False, sourceBotHash=None):
    """
    从压缩包导入账号数据
    """
    try:
        # 检查压缩包是否存在
        if not os.path.exists(zip_path):
            return False, f'压缩包不存在: {zip_path}', None
        # 尝试从文件名自动识别Hash
        auto_detected_hash = None
        filename = os.path.basename(zip_path)
        match = re.match(r'account_(?:export_|import_)?([a-f0-9]+)\.zip', filename, re.IGNORECASE)
        if match:
            auto_detected_hash = match.group(1)
        # 如果提供了sourceBotHash，使用提供的Hash；否则使用自动识别的Hash
        if sourceBotHash:
            detected_source_hash = sourceBotHash
        else:
            detected_source_hash = auto_detected_hash
        if detected_source_hash and detected_source_hash.lower() == 'unity':
            return False, '源账号不能为unity', auto_detected_hash
        if targetBotHash.lower() == 'unity':
            return False, '目标账号不能为unity', auto_detected_hash
        # 获取进程内的账号列表并验证
        bot_info_dict = None
        if Proc:
            try:
                bot_info_dict = Proc.Proc_data.get('bot_info_dict', None)
            except Exception:
                pass
        if bot_info_dict is not None:
            if targetBotHash not in bot_info_dict:
                return False, f'目标账号 {targetBotHash} 不存在于当前进程的账号列表中', auto_detected_hash
        temp_dir = tempfile.mkdtemp()
        try:
            # 解压到临时目录
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            # 如果没有指定目标Hash，使用自动识别的Hash
            if targetBotHash is None:
                if auto_detected_hash:
                    targetBotHash = auto_detected_hash
                else:
                    return False, '无法自动识别Hash，请手动指定目标账号Hash', auto_detected_hash
            # 如果压缩包中包含顶层目录，需要找到实际的数据目录
            source_dir = temp_dir
            subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if len(subdirs) == 1:
                potential_source = os.path.join(temp_dir, subdirs[0])
                if (
                    os.path.exists(os.path.join(potential_source, 'user'))
                    or os.path.exists(os.path.join(potential_source, 'console'))
                    or os.path.exists(os.path.join(potential_source, 'extend'))
                ):
                    source_dir = potential_source
            # 获取源Hash
            if not detected_source_hash:
                return False, '无法识别源账号Hash，请手动指定', auto_detected_hash
            # 执行导入
            success, error_msg, backup_path = _performAccountDataImport(
                source_dir, detected_source_hash, targetBotHash, Proc, overwrite
            )
            if not success:
                return False, error_msg, auto_detected_hash
            # 构建结果消息
            result_msg = f'账号数据已从压缩包导入到 {targetBotHash}\n源账号Hash: {detected_source_hash} -> 目标账号Hash: {targetBotHash}'
            if backup_path:
                result_msg += f'\n备份已保存到: {backup_path.replace(chr(92), "/")}'

            return True, result_msg, auto_detected_hash
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
    except Exception as e:
        return False, f'从压缩包导入账号数据失败: {str(e)}', None


def _copyAndReplaceBotHash(source_dir, target_dir, sourceBotHash, targetBotHash):
    """
    复制目录并替换其中的BotHash
    """
    # 在内存中准备所有需要写入的数据
    files_to_write = {}
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        for file in files:
            source_file = os.path.join(root, file)
            if rel_path == '.':
                file_rel_path = file
            else:
                file_rel_path = os.path.join(rel_path, file)
            target_file = os.path.join(target_dir, file_rel_path)
            is_user_json = False
            if rel_path == 'user' or (rel_path.startswith('user' + os.sep) and rel_path.count(os.sep) == 0):
                if not os.path.isdir(source_file):
                    is_user_json = True
            if is_user_json:
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    processed_data = _procesJsonData(data, sourceBotHash, targetBotHash)
                    files_to_write[file_rel_path] = (target_file, 'json', processed_data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    files_to_write[file_rel_path] = (target_file, 'binary', source_file)
                except Exception:
                    files_to_write[file_rel_path] = (target_file, 'binary', source_file)
            else:
                files_to_write[file_rel_path] = (target_file, 'binary', source_file)
    # 清空目标目录
    if os.path.exists(target_dir):
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
    else:
        os.makedirs(target_dir)
    # 写入所有文件
    failed_files = []
    for file_rel_path, (target_file, data_type, content) in files_to_write.items():
        target_file_dir = os.path.dirname(target_file)
        if not os.path.exists(target_file_dir):
            os.makedirs(target_file_dir)
        try:
            if data_type == 'json':
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=4)
            else:
                shutil.copy2(content, target_file)
        except Exception:
            failed_files.append(file_rel_path)
            continue
    if failed_files:
        pass


def _procesJsonData(data, sourceBotHash, targetBotHash):
    """
    递归处理JSON数据，替换BotHash
    如果targetBotHash == sourceBotHash，直接跳过，保留所有hash
    如果targetBotHash != sourceBotHash：
    - 删除targetBotHash的键（如果存在）
    - 将sourceBotHash的值复制一份，一份保持原样（sourceBotHash），一份经过处理后作为targetBotHash
    - 保留其他hash键
    - 递归处理值中的字符串，替换hash
    """
    # 如果目标hash和源hash相同，直接跳过，不做任何处理
    if targetBotHash == sourceBotHash:
        return data
    if isinstance(data, dict):
        result = {}
        source_value = None
        for key, value in data.items():
            if key == targetBotHash:
                continue
            if key == sourceBotHash:
                source_value = copy.deepcopy(value)
                result[sourceBotHash] = source_value
            else:
                result[key] = copy.deepcopy(value)
        if source_value is not None:
            copied_value = copy.deepcopy(source_value)
            processed_copied_value = _replaceHashInData(copied_value, sourceBotHash, targetBotHash)
            result[targetBotHash] = processed_copied_value
        return result
    else:
        return data


def _replaceHashInData(data, oldHash, newHash):
    """
    递归替换数据中的hash字符串
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = _replaceHashInData(value, oldHash, newHash)
        return result
    elif isinstance(data, list):
        return [_replaceHashInData(item, oldHash, newHash) for item in data]
    elif isinstance(data, str):
        return data.replace(oldHash, newHash)
    else:
        return data
