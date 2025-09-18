# -*- encoding: utf-8 -*-
'''
_______________________    _________________________________________
__  __ \__  /____  _/_ |  / /__    |__  __ \___  _/_  ____/__  ____/
_  / / /_  /  __  / __ | / /__  /| |_  / / /__  / _  /    __  __/   
/ /_/ /_  /____/ /  __ |/ / _  ___ |  /_/ /__/ /  / /___  _  /___   
\____/ /_____/___/  _____/  /_/  |_/_____/ /___/  \____/  /_____/   

@File      :   backup.py
@Author    :   lunzhiPenxil仑质
@Contact   :   lunzhipenxil@gmail.com
@License   :   AGPL
@Copyright :   (C) 2020-2021, OlivOS-Team
@Desc      :   备份功能模块
'''

import OlivOS
import OlivaDiceCore
import OlivaDiceMaster

import os
import datetime
import zipfile
import threading
import time
import shutil
import re

# 全局变量控制备份线程的停止
_backup_thread_stop_event = threading.Event()

# 懒加载缓存相关变量
_backup_schedule_cache = {
    'last_config_hash': None,  # 配置哈希值，用于检测配置变更
    'last_check_date': None,   # 上次检查的日期
    'should_backup_today': False,  # 今天是否需要备份
    'next_backup_time': None,  # 下次备份时间
    'config_valid': False     # 配置是否有效
}

def createBackup(Proc):
    """
    创建备份
    返回: (成功标志, 错误信息)
    """
    try:
        current_time = datetime.datetime.now()
        backup_filename = f"data_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        # 获取备份目录和源目录
        backup_dir = OlivaDiceCore.data.backupDirRoot
        source_dir = OlivaDiceMaster.data.backupPath
        # 确保目录存在
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        if not os.path.exists(source_dir):
            return False, f"备份源目录不存在: {source_dir}"
        # 创建备份文件完整路径
        backup_file_path = os.path.join(backup_dir, backup_filename)
        # 创建ZIP备份
        with zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径
                    relative_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, relative_path)
        # 管理备份数量限制
        manageBackupCount(Proc)
        return True, f"备份创建成功: {backup_filename}"
        
    except Exception as e:
        return False, f"备份创建失败: {str(e)}"

def manageBackupCount(Proc):
    """
    管理备份数量，删除超出限制的旧备份
    """
    try:
        # 获取最大备份数量配置
        max_backup_count = OlivaDiceCore.console.getBackupConfigByKey('maxBackupCount')
        if max_backup_count is None:
            max_backup_count = 1
        backup_dir = OlivaDiceCore.data.backupDirRoot
        # 获取所有备份文件
        backup_files = []
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.startswith('data_') and file.endswith('.zip'):
                    file_path = os.path.join(backup_dir, file)
                    if os.path.isfile(file_path):
                        # 获取文件修改时间
                        mtime = os.path.getmtime(file_path)
                        backup_files.append((file_path, mtime))
        # 按时间排序，最新的在前
        backup_files.sort(key=lambda x: x[1], reverse=True)
        # 删除超出数量限制的备份
        if len(backup_files) > max_backup_count:
            for file_path, _ in backup_files[max_backup_count:]:
                try:
                    os.remove(file_path)
                except Exception as e:
                    if Proc:
                        Proc.log(2, f"删除备份文件失败: {file_path}, 错误: {str(e)}")
    except Exception as e:
        if Proc:
            Proc.log(2, f"管理备份数量失败: {str(e)}")

def _getConfigHash():
    """
    获取当前备份配置的哈希值，用于检测配置变更
    """
    try:
        start_date = OlivaDiceCore.console.getBackupConfigByKey('startDate')
        pass_day = OlivaDiceCore.console.getBackupConfigByKey('passDay')
        backup_time = OlivaDiceCore.console.getBackupConfigByKey('backupTime')
        max_backup_count = OlivaDiceCore.console.getBackupConfigByKey('maxBackupCount')
        is_backup = OlivaDiceCore.console.getBackupConfigByKey('isBackup')
        
        # 创建配置字符串并计算哈希
        config_str = f"{start_date}|{pass_day}|{backup_time}|{max_backup_count}|{is_backup}"
        return hash(config_str)
    except:
        return None

def _calculateBackupSchedule(Proc):
    """
    计算备份计划（内部函数，进行实际的计算工作）
    返回: (是否应该备份, 下次备份时间, 配置是否有效)
    """
    try:
        # 获取备份配置
        start_date_str = OlivaDiceCore.console.getBackupConfigByKey('startDate')
        pass_day = OlivaDiceCore.console.getBackupConfigByKey('passDay')
        backup_time_str = OlivaDiceCore.console.getBackupConfigByKey('backupTime')
        
        if not start_date_str or pass_day is None or not backup_time_str:
            return False, None, False
            
        # 解析开始日期
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except:
            return False, None, False
            
        # 解析备份时间
        try:
            backup_time = datetime.datetime.strptime(backup_time_str, '%H:%M:%S').time()
        except:
            return False, None, False
            
        # 获取当前日期和时间
        current_datetime = datetime.datetime.now()
        current_date = current_datetime.date()
        
        # 计算从开始日期到今天的天数差
        days_diff = (current_date - start_date).days
        
        # 检查是否是备份日期
        should_backup_today = False
        if days_diff >= 0 and days_diff % pass_day == 0:
            should_backup_today = True
            
        # 计算下次备份时间（优化：使用数学计算而非循环）
        next_backup_time = None
        if days_diff >= 0:
            # 如果今天是备份日，下次备份就是今天
            if should_backup_today:
                next_backup_time = datetime.datetime.combine(current_date, backup_time)
                # 如果今天的备份时间已过，计算下次备份
                if current_datetime >= next_backup_time:
                    days_to_next = pass_day - (days_diff % pass_day) if days_diff % pass_day != 0 else pass_day
                    next_backup_date = current_date + datetime.timedelta(days=days_to_next)
                    next_backup_time = datetime.datetime.combine(next_backup_date, backup_time)
            else:
                # 计算距离下次备份还需要多少天
                days_to_next = pass_day - (days_diff % pass_day)
                next_backup_date = current_date + datetime.timedelta(days=days_to_next)
                next_backup_time = datetime.datetime.combine(next_backup_date, backup_time)
        else:
            # 开始日期在未来
            next_backup_time = datetime.datetime.combine(start_date, backup_time)
            
        return should_backup_today, next_backup_time, True
        
    except Exception as e:
        if Proc:
            Proc.log(2, f"计算备份计划失败: {str(e)}")
        return False, None, False

def shouldBackupToday(Proc):
    """
    检查今天是否应该进行备份
    返回: (是否应该备份, 下次备份时间)
    """
    global _backup_schedule_cache
    
    try:
        current_date = datetime.date.today()
        current_config_hash = _getConfigHash()
        
        # 检查是否需要重新计算（配置变更或日期变更）
        need_recalculate = (
            _backup_schedule_cache['last_config_hash'] != current_config_hash or
            _backup_schedule_cache['last_check_date'] != current_date or
            not _backup_schedule_cache['config_valid']
        )
        
        if need_recalculate:
            # 重新计算备份计划
            should_backup, next_time, config_valid = _calculateBackupSchedule(Proc)
            
            # 更新缓存
            _backup_schedule_cache.update({
                'last_config_hash': current_config_hash,
                'last_check_date': current_date,
                'should_backup_today': should_backup,
                'next_backup_time': next_time,
                'config_valid': config_valid
            })
            
            if Proc and config_valid:
                # 获取自动备份开关状态
                is_backup_enabled = OlivaDiceCore.console.getBackupConfigByKey('isBackup')
                if is_backup_enabled is None:
                    is_backup_enabled = 0  # 默认开启
                
                if is_backup_enabled == 1:
                    # 自动备份关闭时，只显示状态
                    Proc.log(2, f"备份计划已更新: 自动备份=关闭")
                else:
                    # 自动备份开启时，显示完整信息
                    Proc.log(2, f"备份计划已更新: 自动备份=开启, 今日需备份={should_backup}, 下次备份时间={next_time}")
        
        # 返回缓存的结果
        return (_backup_schedule_cache['should_backup_today'], 
                _backup_schedule_cache['next_backup_time'])
                
    except Exception as e:
        if Proc:
            Proc.log(2, f"检查备份时间失败: {str(e)}")
        return False, None

def clearBackupCache():
    """
    清理备份计划缓存，强制下次调用时重新计算
    """
    global _backup_schedule_cache
    _backup_schedule_cache.update({
        'last_config_hash': None,
        'last_check_date': None,
        'should_backup_today': False,
        'next_backup_time': None,
        'config_valid': False
    })

def checkConfigChanged():
    """
    轻量级配置变更检查，只检查配置哈希是否变更
    返回: 配置是否发生变更
    """
    global _backup_schedule_cache
    try:
        current_config_hash = _getConfigHash()
        return _backup_schedule_cache['last_config_hash'] != current_config_hash
    except:
        return True  # 出错时认为配置已变更

def getCachedBackupStatus():
    """
    获取缓存中的备份状态信息（只读，不触发计算）
    返回: (是否应该备份, 下次备份时间, 缓存是否有效)
    """
    global _backup_schedule_cache
    try:
        # 检查缓存是否有效
        if not _backup_schedule_cache['config_valid']:
            return None, None, False
            
        # 检查日期是否过期
        current_date = datetime.date.today()
        if _backup_schedule_cache['last_check_date'] != current_date:
            return None, None, False
            
        return (_backup_schedule_cache['should_backup_today'], 
                _backup_schedule_cache['next_backup_time'], 
                True)
    except:
        return None, None, False

def hasBackupToday(Proc):
    """
    检查今天是否已经备份过
    """
    try:
        backup_dir = OlivaDiceCore.data.backupDirRoot
        current_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        if not os.path.exists(backup_dir):
            return False
        for file in os.listdir(backup_dir):
            if file.startswith(f'data_{current_date_str}') and file.endswith('.zip'):
                return True
        return False
    except Exception as e:
        if Proc:
            Proc.log(2, f"检查今日备份状态失败: {str(e)}")
        return False

def autoBackupTimer(Proc):
    """
    自动备份定时器
    """
    last_backup_check = None
    
    while not _backup_thread_stop_event.is_set():
        try:
            # 检查停止事件，如果设置了停止事件则退出
            if _backup_thread_stop_event.wait(1.0):  # 等待1秒或直到停止事件被设置
                break
            
            # 每秒进行轻量级配置检查（只有配置变更时才进行完整计算）
            if checkConfigChanged():
                if Proc:
                    Proc.log(2, "检测到备份配置变更，更新缓存")
                shouldBackupToday(Proc)  # 只在配置变更时才调用完整计算
            
            # 检查备份开关状态
            is_backup_enabled = OlivaDiceCore.console.getBackupConfigByKey('isBackup')
            if is_backup_enabled is None:
                is_backup_enabled = 0  # 默认开启自动备份
            
            # 如果自动备份被关闭，则跳过备份执行检查
            if is_backup_enabled == 1:
                continue
            
            # 获取当前时间（HH:MM:SS格式）
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # 获取备份时间配置
            backup_time_str = OlivaDiceCore.console.getBackupConfigByKey('backupTime')
            if backup_time_str:
                # 在备份时间点检查是否需要备份
                if current_time == backup_time_str and last_backup_check != backup_time_str:
                    last_backup_check = backup_time_str
                    should_backup, _ = shouldBackupToday(Proc)
                    if should_backup:
                        success, result = createBackup(Proc)
                        if success:
                            if Proc:
                                Proc.log(2, f"自动备份完成: {result}")
                        else:
                            if Proc:
                                Proc.log(2, f"自动备份失败: {result}")
                elif current_time != backup_time_str:
                    # 重置检查标记，允许下次备份时间再次检查
                    last_backup_check = None
            
        except Exception as e:
            if Proc:
                Proc.log(2, f"自动备份定时器错误: {str(e)}")
            # 出错时等待1分钟，但仍要检查停止事件
            _backup_thread_stop_event.wait(60.0)
    
    if Proc:
        Proc.log(2, "自动备份定时器已停止")
def getBackupInfo(Proc):
    """
    获取备份系统信息（优化版：优先使用缓存，避免不必要的计算）
    返回: 备份配置和状态信息的字符串
    """
    try:
        info_lines = []
        # 获取备份配置
        start_date = OlivaDiceCore.console.getBackupConfigByKey('startDate')
        pass_day = OlivaDiceCore.console.getBackupConfigByKey('passDay')
        backup_time = OlivaDiceCore.console.getBackupConfigByKey('backupTime')
        max_backup_count = OlivaDiceCore.console.getBackupConfigByKey('maxBackupCount')
        is_backup = OlivaDiceCore.console.getBackupConfigByKey('isBackup')
        
        info_lines.append(f"自动备份状态: {'关闭' if is_backup == 1 else '开启'}")
        info_lines.append(f"备份开始日期: {start_date}")
        info_lines.append(f"备份间隔天数: {pass_day}")
        info_lines.append(f"自动备份时间: {backup_time}")
        info_lines.append(f"最大备份数量: {max_backup_count}")
        
        # 优先从缓存获取备份状态信息
        should_backup, next_backup_time, cache_valid = getCachedBackupStatus()
        
        if cache_valid:
            # 使用缓存数据，避免重新计算
            info_lines.append(f"今天是否需要备份: {'是' if should_backup else '否'}")
            if next_backup_time:
                info_lines.append(f"下次备份时间: {next_backup_time}")
        else:
            # 缓存无效时才进行计算（这种情况应该很少发生）
            should_backup, next_backup_time = shouldBackupToday(Proc)
            info_lines.append(f"今天是否需要备份: {'是' if should_backup else '否'}")
            if next_backup_time:
                info_lines.append(f"下次备份时间: {next_backup_time}")
            else:
                info_lines.append("下次备份时间: 配置无效或未设置")
        
        # 检查今天是否已备份
        has_backup = hasBackupToday(Proc)
        info_lines.append(f"今天是否已备份: {'是' if has_backup else '否'}")
        
        return "\n".join(info_lines)
    except Exception as e:
        return f"获取备份信息失败: {str(e)}"

def validateBackupConfigItem(key, value):
    """
    验证单个备份配置项的格式
    """
    try:
        if key == 'startDate':
            # 验证日期格式 yyyy-MM-dd
            if not isinstance(value, str):
                raise ValueError("日期必须为字符串格式")
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                raise ValueError("日期格式必须为 yyyy-MM-dd")
            datetime.datetime.strptime(value, '%Y-%m-%d')
        elif key == 'passDay':
            # 验证整数
            if not isinstance(value, int):
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                else:
                    raise ValueError("天数必须为整数")
            if value <= 0:
                raise ValueError("天数不能为负数或0")
        elif key == 'backupTime':
            # 验证时间格式 HH:mm:ss
            if not isinstance(value, str):
                raise ValueError("时间必须为字符串格式")
            if not re.match(r'^\d{2}:\d{2}:\d{2}$', value):
                raise ValueError("时间格式必须为 HH:mm:ss")
            datetime.datetime.strptime(value, '%H:%M:%S')
        elif key == 'maxBackupCount':
            # 验证备份最大数量
            if not isinstance(value, int):
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                else:
                    raise ValueError("备份数量必须为整数")
            if value <= 0:
                raise ValueError("备份数量不能小于等于0")
        elif key == 'isBackup':
            # 验证备份开关（只能为0或1）
            if not isinstance(value, int):
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                else:
                    raise ValueError("备份开关必须为整数")
            if value not in [0, 1]:
                raise ValueError("备份开关只能为0（开启）或1（关闭）")
        # 其他配置项按字符串处理，不需要特殊验证
        return value if key in ['passDay', 'maxBackupCount', 'isBackup'] else str(value)
    except Exception as e:
        raise ValueError(f"配置项 '{key}' 格式验证失败: {str(e)}")

def stopBackupSystem(Proc):
    """
    停止备份系统
    """
    global _backup_thread_stop_event
    _backup_thread_stop_event.set()
    if Proc:
        Proc.log(2, "备份系统停止信号已发送")

def initBackupSystem(Proc):
    """
    初始化备份系统并运行自动备份定时器
    """
    try:
        # 重置停止事件
        global _backup_thread_stop_event
        _backup_thread_stop_event.clear()
        
        # 初始化备份配置
        OlivaDiceCore.console.initBackupConfig()
        OlivaDiceCore.console.readBackupConfig()
        
        # 清理缓存，确保使用最新配置
        clearBackupCache()
        
        if Proc:
            Proc.log(2, "备份系统初始化成功，启动自动备份定时器")
        autoBackupTimer(Proc)
    except Exception as e:
        if Proc:
            Proc.log(2, f"初始化备份系统失败: {str(e)}")
        return False
