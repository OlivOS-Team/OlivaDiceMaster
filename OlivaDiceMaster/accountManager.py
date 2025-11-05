# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   accountManager.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2025, OlivOS-Team
@Desc      :   多账号连接管理模块
'''

import OlivOS
import OlivaDiceCore
import OlivaDiceMaster

import os
import json
import shutil
import re
import zipfile
import tempfile

def get_bot_display_name(botHash, bot_info, plugin_event=None):
    """
    获取bot的显示名称
    """
    bot_name = "未知"
    # 优先通过API调用获取名称
    try:
        # 如果plugin_event为None，或者plugin_event的bot_info与目标botHash不匹配，构建fake_event
        # 这样可以确保获取的是正确账号的名称
        if plugin_event is None or (hasattr(plugin_event, 'bot_info') and plugin_event.bot_info.hash != botHash):
            fake_event = OlivOS.API.Event(
                OlivOS.contentAPI.fake_sdk_event(
                    bot_info=bot_info,
                    fakename='OlivaDiceMaster'
                ),
                None
            )
            res_data = fake_event.get_login_info(bot_info)
        else:
            res_data = plugin_event.get_login_info(bot_info)
        
        if res_data and res_data.get('active') and 'data' in res_data:
            bot_name = res_data['data'].get('name', '未知')
            if bot_name and bot_name != '未知':
                return bot_name
    except:
        pass
    # 尝试从用户配置中获取保存的昵称
    try:
        if hasattr(bot_info, 'id') and hasattr(bot_info, 'platform') and bot_info.platform:
            bot_id = str(bot_info.id)
            bot_user_hash = OlivaDiceCore.userConfig.getUserHash(
                userId = bot_id,
                userType = 'user',
                platform = bot_info.platform['platform']
            )
            saved_name = OlivaDiceCore.userConfig.getUserConfigByKeyWithHash(
                userHash = bot_user_hash,
                userConfigKey = 'userName',
                botHash = botHash
            )
            if saved_name and saved_name != '用户':
                bot_name = saved_name
    except:
        pass
    return bot_name

def checkCircularDependency(slaveBotHash, masterBotHash, relations):
    """
    检查是否存在循环依赖
    """
    if slaveBotHash == masterBotHash:
        return True, "从账号和主账号不能相同"
    # 从masterBotHash向上查找，看是否会在链中遇到slaveBotHash
    # 如果masterBotHash已经是slaveBotHash的从账号（通过关系链），会产生循环
    visited = set()
    current = masterBotHash
    
    while current:
        if current == slaveBotHash:
            return True, "检测到循环依赖：主账号已经在从账号的关系链中"
        if current in visited:
            # 已经访问过，说明遇到了其他环，检测到循环
            return True, "检测到循环依赖：关系中已存在循环"
        visited.add(current)
        # 继续向上查找
        current = relations.get(current)
    
    # 从slaveBotHash向上查找，看是否会在链中遇到masterBotHash
    # 如果slaveBotHash已经是masterBotHash的从账号（通过关系链），会产生循环
    # 例如：当前关系 A -> B，要建立 B -> A，会形成 A -> B -> A 的循环
    visited2 = set()
    current2 = slaveBotHash
    
    while current2:
        if current2 == masterBotHash:
            return True, "检测到循环依赖：从账号已经在主账号的关系链中"
        if current2 in visited2:
            return True, "检测到循环依赖：关系中已存在循环"
        visited2.add(current2)
        # 继续向上查找
        current2 = relations.get(current2)
    
    # 检查slaveBotHash的所有从账号，看它们是否会在链中回到masterBotHash或其上级
    # 这是为了防止形成如下的循环：A -> B -> C，然后建立 C -> A 会形成 A -> B -> C -> A
    # 找到所有以slaveBotHash为主账号的从账号
    slaveBotHash_slaves = [s for s, m in relations.items() if m == slaveBotHash]
    for slave_of_slave in slaveBotHash_slaves:
        visited_slave = set()
        current_slave = slave_of_slave
        # 沿着主账号链向上查找
        while current_slave:
            if current_slave == masterBotHash:
                return True, "检测到循环依赖：从账号的从账号已经在主账号的关系链中"
            # 检查current_slave是否在masterBotHash的上级链中
            # 沿着masterBotHash向上查找，看是否会遇到current_slave
            visited_master = set()
            check_master = masterBotHash
            while check_master:
                if check_master == current_slave:
                    return True, "检测到循环依赖：建立此关系后会形成循环"
                if check_master in visited_master:
                    break
                visited_master.add(check_master)
                check_master = relations.get(check_master)
            
            if current_slave in visited_slave:
                break
            visited_slave.add(current_slave)
            current_slave = relations.get(current_slave)
    return False, ""

def linkAccount(slaveBotHash, masterBotHash, bot_info_dict=None):
    """
    建立主从关系
    """
    try:
        # 验证hash是否存在
        if bot_info_dict is not None:
            if slaveBotHash not in bot_info_dict:
                return False, f"从账号 {slaveBotHash} 不存在于当前进程的账号列表中"
            if masterBotHash not in bot_info_dict:
                return False, f"主账号 {masterBotHash} 不存在于当前进程的账号列表中"
        # 获取当前的关系配置
        relations = OlivaDiceCore.console.getAllAccountRelations()
        # 检查账号不能为unity
        # 无论是主账号还是从账号都不能为unity
        if slaveBotHash.lower() == "unity":
            return False, "从账号不能为unity"
        if masterBotHash.lower() == "unity":
            return False, "主账号不能为unity"
        # 检查slaveBotHash是否已经是某个账号的从账号
        # 一个从账号不能有多个主账号，必须先断联才能建立新关系
        if slaveBotHash in relations:
            current_master = relations[slaveBotHash]
            return False, f"账号 {slaveBotHash} 已经是 {current_master} 的从账号，请先断开关系"
        # 检查slaveBotHash是否已经有从账号（主账号不能成为从账号）
        # 找到所有以slaveBotHash为主账号的从账号
        slaveBotHash_slaves = [s for s, m in relations.items() if m == slaveBotHash]
        if slaveBotHash_slaves:
            slave_count = len(slaveBotHash_slaves)
            return False, f"账号 {slaveBotHash} 已经是 {slave_count} 个账号的主账号，主账号不能成为从账号"
        # 检查masterBotHash是否已经是某个账号的从账号
        # 如果masterBotHash是从账号，则它不能作为主账号接受新的从账号
        # （因为一个从账号不能有多个主账号，且主账号不能成为从账号）
        if masterBotHash in relations:
            master_master = relations[masterBotHash]
            return False, f"账号 {masterBotHash} 已经是 {master_master} 的从账号，从账号不能作为主账号"
        # 检查循环依赖（按理来说应该是不会出现这种情况，不过还是检查一遍更保险）
        hasCircular, errorMsg = checkCircularDependency(slaveBotHash, masterBotHash, relations)
        if hasCircular:
            return False, errorMsg
        # 设置主从关系
        OlivaDiceCore.console.setAccountRelation(slaveBotHash, masterBotHash)
        OlivaDiceCore.console.saveAccountRelationConfig()
        return True, f"已建立主从关系: {slaveBotHash}(从) -> {masterBotHash}(主)"
    except Exception as e:
        return False, f"建立主从关系失败: {str(e)}"

def unlinkAccount(slaveBotHash, bot_info_dict=None):
    """
    断开主从关系
    """
    try:
        # 验证hash是否存在
        if bot_info_dict is not None:
            if slaveBotHash not in bot_info_dict:
                return False, f"账号 {slaveBotHash} 不存在于当前进程的账号列表中"
        masterBotHash = OlivaDiceCore.console.getMasterBotHash(slaveBotHash)
        if not masterBotHash:
            return False, f"账号 {slaveBotHash} 未建立主从关系"
        # 删除主从关系
        OlivaDiceCore.console.removeAccountRelation(slaveBotHash)
        OlivaDiceCore.console.saveAccountRelationConfig()
        return True, f"已断开主从关系: {slaveBotHash}(从) ->/<- {masterBotHash}(主)"
    except Exception as e:
        return False, f"断开主从关系失败: {str(e)}"

def listAccountRelations(bot_info_dict, plugin_event=None):
    """
    列出所有账号和主从关系
    """
    try:
        relations = OlivaDiceCore.console.getAllAccountRelations()
        result_lines = []
        result_lines.append("=== 账号列表 ===")
        # 创建主账号到从账号的映射
        master_to_slaves = {}
        for slave, master in relations.items():
            if master not in master_to_slaves:
                master_to_slaves[master] = []
            master_to_slaves[master].append(slave)
        # 遍历所有账号
        for botHash in bot_info_dict:
            bot_name = get_bot_display_name(botHash, bot_info_dict[botHash], plugin_event)
            bot_id = bot_info_dict[botHash].id if hasattr(bot_info_dict[botHash], 'id') else "未知"
            # 检查账号角色
            if botHash in relations:
                # 从账号
                masterHash = relations[botHash]
                master_name = get_bot_display_name(masterHash, bot_info_dict[masterHash], plugin_event) if masterHash in bot_info_dict else "未知"
                result_lines.append(f"[从账号] {bot_name}({bot_id})")
                result_lines.append(f"  Hash: {botHash}")
                result_lines.append(f"  主账号: {master_name} ({masterHash})")
            elif botHash in master_to_slaves:
                # 主账号
                result_lines.append(f"[主账号] {bot_name}({bot_id})")
                result_lines.append(f"  Hash: {botHash}")
                result_lines.append(f"  从账号数量: {len(master_to_slaves[botHash])}")
                for slave in master_to_slaves[botHash]:
                    slave_name = get_bot_display_name(slave, bot_info_dict[slave], plugin_event) if slave in bot_info_dict else "未知"
                    result_lines.append(f"    - {slave_name} ({slave})")
            else:
                # 独立账号
                result_lines.append(f"[独立账号] {bot_name}({bot_id})")
                result_lines.append(f"  Hash: {botHash}")
            result_lines.append("")
        return "\n".join(result_lines)
    except Exception as e:
        return f"列出账号关系失败: {str(e)}"

def showAccountInfo(botHash, bot_info_dict, plugin_event=None):
    """
    显示指定账号的详细信息
    """
    try:
        if botHash not in bot_info_dict:
            return f"未找到账号: {botHash}"
        bot_name = get_bot_display_name(botHash, bot_info_dict[botHash], plugin_event)
        bot_id = bot_info_dict[botHash].id if hasattr(bot_info_dict[botHash], 'id') else "未知"
        result_lines = []
        result_lines.append(f"=== 账号信息 ===")
        result_lines.append(f"名称: {bot_name}")
        result_lines.append(f"ID: {bot_id}")
        result_lines.append(f"Hash: {botHash}")
        # 检查主从关系
        relations = OlivaDiceCore.console.getAllAccountRelations()
        masterHash = OlivaDiceCore.console.getMasterBotHash(botHash)
        if masterHash:
            # 从账号
            result_lines.append(f"角色: 从账号")
            master_name = get_bot_display_name(masterHash, bot_info_dict[masterHash], plugin_event) if masterHash in bot_info_dict else "未知"
            result_lines.append(f"主账号: {master_name} ({masterHash})")
            result_lines.append(f"数据重定向: 已启用")
        else:
            # 主账号
            slaves = []
            for slave, master in relations.items():
                if master == botHash:
                    slaves.append(slave)
            
            if slaves:
                result_lines.append(f"角色: 主账号")
                result_lines.append(f"从账号数量: {len(slaves)}")
                for slave in slaves:
                    slave_name = get_bot_display_name(slave, bot_info_dict[slave], plugin_event) if slave in bot_info_dict else "未知"
                    result_lines.append(f"  - {slave_name} ({slave})")
            else:
                result_lines.append(f"角色: 独立账号")
                result_lines.append(f"主从关系: 未建立")
        return "\n".join(result_lines)
    except Exception as e:
        return f"获取账号信息失败: {str(e)}"

def exportAccountData(sourceBotHash, Proc, export_path=None):
    """
    压缩包导出账号数据
    """
    try:
        source_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, sourceBotHash)
        if not os.path.exists(source_dir):
            return False, f"源账号数据不存在: {sourceBotHash}"
        export_root = OlivaDiceMaster.data.exportPath
        # 确定导出路径
        if export_path is None:
            if not os.path.exists(export_root):
                os.makedirs(export_root)
            export_path = os.path.join(export_root, f"account_export_{sourceBotHash}.zip")
        else:
            # 如果用户提供的是目录，自动添加文件名
            if os.path.isdir(export_path):
                export_path = os.path.join(export_path, f"account_export_{sourceBotHash}.zip")
        # 如果目标文件已存在，先删除
        if os.path.exists(export_path):
            os.remove(export_path)
        # 创建压缩包
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, relative_path)
        return True, f"账号数据已导出到: {export_path}"
    except Exception as e:
        return False, f"导出账号数据失败: {str(e)}"

def importAccountData(sourceBotHash, targetBotHash, Proc, overwrite=False):
    """
    从现有账号导入账号数据
    """
    try:
        # 检查账号不能为unity
        if sourceBotHash.lower() == "unity":
            return False, "源账号不能为unity"
        if targetBotHash.lower() == "unity":
            return False, "目标账号不能为unity"
        # 检查源账号数据是否存在
        source_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, sourceBotHash)
        if not os.path.exists(source_dir):
            return False, f"源账号数据不存在: {sourceBotHash}"
        # 创建目标目录
        target_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, targetBotHash)
        # 备份目标账号数据（如果存在）
        backup_path = None
        if os.path.exists(target_dir):
            backup_base_dir = OlivaDiceMaster.data.exportPath
            # 生成备份文件名
            backup_filename = f"account_import_{targetBotHash}.zip"
            backup_path = os.path.join(backup_base_dir, backup_filename)
            # 确保备份目录存在
            os.makedirs(backup_base_dir, exist_ok=True)
            # 如果备份文件已存在，删除它
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
                Proc.log(2, f"已备份目标账号数据到: {backup_path}")
            if overwrite:
                shutil.rmtree(target_dir)
        # 复制数据并替换BotHash
        _copyAndReplaceBotHash(source_dir, target_dir, sourceBotHash, targetBotHash)
        # 重新加载数据到内存
        try:
            OlivaDiceCore.userConfig.dataUserConfigLoadAll()
            OlivaDiceCore.pcCard.dataPcCardLoadAll()
            if Proc:
                Proc.log(2, f"已重新加载目标账号 {targetBotHash} 的数据到内存")
        except Exception as reload_error:
            if Proc:
                Proc.log(3, f"重新加载数据时出现警告: {str(reload_error)}")
        result_msg = f"账号数据已从 {sourceBotHash} 导入到 {targetBotHash}"
        if backup_path:
            result_msg += f"\n备份已保存到: {backup_path}"
        return True, result_msg
    except Exception as e:
        return False, f"导入账号数据失败: {str(e)}"

def importAccountDataFromZip(zip_path, targetBotHash, Proc, overwrite=False, sourceBotHash=None):
    """
    从压缩包导入账号数据
    """
    try:
        # 检查压缩包是否存在
        if not os.path.exists(zip_path):
            return False, f"压缩包不存在: {zip_path}", None
        # 尝试从文件名自动识别Hash
        auto_detected_hash = None
        filename = os.path.basename(zip_path)
        # 匹配 account_export_xxxxx.zip 或 account_import_xxxxx.zip 格式
        match = re.match(r'account_(?:export_|import_)?([a-f0-9]+)\.zip', filename, re.IGNORECASE)
        if match:
            auto_detected_hash = match.group(1)
        # 如果提供了sourceBotHash，使用提供的；否则使用自动识别的
        if sourceBotHash:
            detected_source_hash = sourceBotHash
        else:
            detected_source_hash = auto_detected_hash
        # 检查账号不能为unity
        if detected_source_hash and detected_source_hash.lower() == "unity":
            return False, "源账号不能为unity", auto_detected_hash
        if targetBotHash.lower() == "unity":
            return False, "目标账号不能为unity", auto_detected_hash
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
                    return False, "无法自动识别Hash，请手动指定目标账号Hash", auto_detected_hash
            # 如果压缩包中包含顶层目录，需要找到实际的数据目录
            source_dir = temp_dir
            subdirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if len(subdirs) == 1:
                # 如果只有一个子目录，可能是压缩包的顶层目录
                potential_source = os.path.join(temp_dir, subdirs[0])
                # 检查是否包含典型的数据结构
                if os.path.exists(os.path.join(potential_source, 'user')) or \
                   os.path.exists(os.path.join(potential_source, 'console')) or \
                   os.path.exists(os.path.join(potential_source, 'extend')):
                    source_dir = potential_source
            # 创建目标目录
            target_dir = os.path.join(OlivaDiceCore.data.dataDirRoot, targetBotHash)
            # 备份目标账号数据（如果存在）
            backup_path = None
            if os.path.exists(target_dir):
                # 使用与导出相同的路径
                backup_base_dir = OlivaDiceMaster.data.exportPath
                backup_filename = f"account_import_{targetBotHash}.zip"
                backup_path = os.path.join(backup_base_dir, backup_filename)
                # 确保备份目录存在
                os.makedirs(backup_base_dir, exist_ok=True)
                # 如果备份文件已存在，删除它
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
                    Proc.log(2, f"已备份目标账号数据到: {backup_path}")
                if overwrite:
                    shutil.rmtree(target_dir)
            # 获取源Hash
            if not detected_source_hash:
                return False, "无法识别源账号Hash，请手动指定", auto_detected_hash
            # 复制数据并替换BotHash
            _copyAndReplaceBotHash(source_dir, target_dir, detected_source_hash, targetBotHash)
            # 重新加载数据到内存
            try:
                OlivaDiceCore.userConfig.dataUserConfigLoadAll()
                OlivaDiceCore.pcCard.dataPcCardLoadAll()
                if Proc:
                    Proc.log(2, f"已重新加载目标账号 {targetBotHash} 的数据到内存")
            except Exception as reload_error:
                if Proc:
                    Proc.log(3, f"重新加载数据时出现警告: {str(reload_error)}")
            # 生成返回消息
            result_msg = f"账号数据已从压缩包导入到 {targetBotHash}\n源账号Hash: {detected_source_hash} -> 目标账号Hash: {targetBotHash}"
            if backup_path:
                result_msg += f"\n备份已保存到: {backup_path}"
            return True, result_msg, auto_detected_hash
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    except Exception as e:
        return False, f"从压缩包导入账号数据失败: {str(e)}", None

def _copyAndReplaceBotHash(source_dir, target_dir, sourceBotHash, targetBotHash):
    """
    复制目录并替换其中的BotHash
    """
    # 黑名单：这些数据不应该被导入
    blacklist_keys = OlivaDiceCore.userConfig.dictRedirectBlacklist
    # 遍历源目录
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        if rel_path == '.':
            current_target_dir = target_dir
        else:
            current_target_dir = os.path.join(target_dir, rel_path)
        if not os.path.exists(current_target_dir):
            os.makedirs(current_target_dir)
        # 复制文件
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(current_target_dir, file)
            # 替换BotHash并过滤黑名单数据
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 如果成功解析为JSON，进行JSON数据处理
                processed_data = _procesJsonData(data, sourceBotHash, targetBotHash, blacklist_keys)
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, ensure_ascii=False, indent=4)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # 其余直接复制
                shutil.copy2(source_file, target_file)
            except Exception as e:
                shutil.copy2(source_file, target_file)

def _procesJsonData(data, sourceBotHash, targetBotHash, blacklist_keys):
    """
    递归处理JSON数据，替换BotHash并过滤黑名单数据
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            # 跳过黑名单中的键
            if key == 'configNote' and isinstance(value, dict):
                # 过滤掉黑名单中的配置项
                filtered_config = {k: v for k, v in value.items() if k not in blacklist_keys}
                if filtered_config:
                    result[key] = _procesJsonData(filtered_config, sourceBotHash, targetBotHash, blacklist_keys)
            elif key not in blacklist_keys:
                result[key] = _procesJsonData(value, sourceBotHash, targetBotHash, blacklist_keys)
        return result
    elif isinstance(data, list):
        return [_procesJsonData(item, sourceBotHash, targetBotHash, blacklist_keys) for item in data]
    elif isinstance(data, str):
        # 替换字符串中的BotHash
        return data.replace(sourceBotHash, targetBotHash)
    else:
        return data

