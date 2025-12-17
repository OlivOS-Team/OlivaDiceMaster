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

dictConsoleSwitchTemplate = {
    'default' : {
        'masterAutoUpdate': 1
    }
}

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
    'strMasterOopmGet': '{tMasterOopkNameList}\n模块已安装成功，请使用[.system restart]应用安装',
    'strMasterOopmGetNone': '{tMasterOopkNameList}\n模块不存在，请先使用[.oopm list]指令查看受支持的模块',
    'strMasterOopmGetSkipSrc': '{tMasterOopkNameList}\n模块为手动部署模式，已跳过',
    'strMasterOopmDownloadFailed': '{tMasterOopkNameList}\n模块下载失败',
    'strMasterOopmCopyFailed': '{tMasterOopkNameList}\n模块安装失败',
    'strMasterSendFromMaster': '来自Master的消息：\n{tResult}',
    'strMasterSendToMaster': '[{tGroupName}]({tGroupId})中[{tUserName}]({tUserId})发来的消息：\n{tResult}',
    'strMasterSendToMasterAlready': '已将消息发送至Master',
    'strMasterTrustSet': '[{tName}]({tId})的{tMasterTrustName}已设置为：{tResult}',
    'strMasterTrustGet': '[{tName}]({tId})的{tMasterTrustName}为：{tResult}',
    'strMasterPlatformNo': '该功能在此平台不受支持',
    'strMasterGroupClearShow': '已检查[{tMasterCount01}]个群:\n{tResult}\n已经决定清除[{tMasterCount02}]个群\n请使用[.group clear do (天数)]指令执行这项操作',
    'strMasterGroupClearShowOff': '已检查[{tMasterCount01}]个群:\n{tResult}\n已经决定清除[{tMasterCount02}]个群\n请使用[.group clear do off]指令执行这项操作',
    'strMasterGroupClearDoUnit': '已经清除群:\n{tResult}',
    'strMasterGroupClearDoUnitSend': '检测到在此处最后发言为{tResult}，即将自动退出',
    'strMasterGroupClearDo': '已检查[{tMasterCount01}]个群\n已经清除[{tMasterCount02}]个群',
    'strMasterGroupClearUnit': '[{tName}] - ({tId}): {tResult}',
    'strMasterBackupStart': '正在开始备份数据...',
    'strMasterBackupSuccess': '数据备份完成：\n{tBackupResult}',
    'strMasterBackupFailed': '数据备份失败：\n{tBackupResult}',
    'strMasterBackupConfigSet': '配置项 {tConfigKey} 已设置为: {tConfigValue}',
    'strMasterBackupConfigSetFailed': '配置项设置失败：\n{tBackupResult}',
    'strMasterBackupChangeUsage': '用法: .backup change 配置项 配置值\n可用配置项: startDate, passDay, backupTime, maxBackupCount, isBackup',
    'strMasterBackupConfigGet': '配置项 {tConfigKey}: {tConfigValue}',
    'strMasterBackupConfigNotFound': '配置项 {tConfigKey} 不存在或未设置',
    'strMasterBackupInfo': '{tBackupResult}',
    'strMasterAccountLinkSuccess': '已成功建立主从关系：\n{tAccountResult}',
    'strMasterAccountLinkFailed': '建立主从关系失败：\n{tAccountResult}',
    'strMasterAccountUnlinkSuccess': '已成功断开主从关系：\n{tAccountResult}',
    'strMasterAccountUnlinkFailed': '断开主从关系失败：\n{tAccountResult}',
    'strMasterAccountList': '{tAccountResult}',
    'strMasterAccountShow': '{tAccountResult}',
    'strMasterAccountImportSuccess': '数据导入成功：\n{tAccountResult}',
    'strMasterAccountImportFailed': '数据导入失败：\n{tAccountResult}',
    'strMasterAccountExportSuccess': '数据导出成功：\n{tAccountResult}',
    'strMasterAccountExportFailed': '数据导出失败：\n{tAccountResult}',
}

dictStrConst = {
}

dictGValue = {
}

dictTValue = {
    'tMasterResult': 'N/A',
    'tMasterOopkNameList': 'N/A',
    'tMasterTrustName': '无名信任',
    'tMasterCount01': 'N/A',
    'tMasterCount02': 'N/A',
    'tBackupResult': 'N/A',
    'tConfigKey': 'N/A',
    'tConfigValue': 'N/A',
    'tAccountResult': 'N/A'
}

dictHelpDocTemp = {
    'OlivaDiceMaster': '''[OlivaDiceMaster]
OlivaDice大师模块
本模块为青果跑团掷骰机器人(OlivaDice)大师模块，集成与跑团无关的骰主管理功能功能（如指令更新等）。
核心开发者: lunzhiPenxil仑质
注: 本模块为可选重要模块。''',

    'oopm': '''青果包管理:
本指令可以用于远程更新插件
.oopm update 自动检查并更新全部插件
.oopm update [插件名称] 更新特定插件
.oopm show [插件名称] 检查插件更新状态
.oopm list 查看所有可选模块
.oopm get [插件名称] 获取所选模块''',

    'send': '''send反馈发送:
对于普通用户
.send [反馈消息] 发送反馈消息给Master

对于骰主
.send [回复消息] 发送消息到当前窗口
.send (user/group) [ID] [回复消息] 发送消息到指定窗口''',

    'groupclear': '''指令清群:
.group clear [天数] 查找超过对应天数未触发的多人聊天
.group clear do [天数] 清理超过对应天数未触发的多人聊天
.group clear off 查找bot off的多人聊天
.group clear do off 清理bot off的多人聊天''',

    'backup': '''数据备份:
.backup 查看备份配置和状态
.backup start 手动触发数据备份
.backup change 配置项 配置值 修改备份配置
.backup 配置项 查看指定配置项的值

可用配置项:
- isBackup: 自动备份开关 (0=开启, 1=关闭)
- startDate: 备份开始日期 (yyyy-MM-dd格式)
- passDay: 备份间隔天数 (整数)
- backupTime: 备份时间 (HH:mm:ss格式)
- maxBackupCount: 最大备份数量 (整数)

数据备份路径：./plugin/backup
备份文件格式: data_yyyy-MM-dd_HH-mm-ss.zip''',

    'account': '''多账号连接管理:
.account link [从账号Hash] [主账号Hash] - 建立主从关系
  从账号和主账号可用空格、分号、逗号分隔
  系统会自动检测循环依赖并阻止

.account unlink [从账号Hash] - 断开主从关系
  断开后，从账号将恢复为独立账号

.account list - 列出所有账号和主从关系
  显示所有账号的Hash和对应的主从关系状态

.account show (账号Hash) - 显示账号详细信息
  不指定Hash时，显示当前账号的详细信息
  查询指定账号的连接状态和数据重定向状态

.account import path [路径] (源账号Hash) - 从压缩包导入账号数据
  路径和源账号Hash可用空格、分号、逗号分隔
  源账号Hash可选，如未提供则尝试从文件名自动识别
  将压缩包中的数据导入到当前账号
  操作前会自动备份目标账号数据

.account import hash [源账号Hash] - 从指定账号导入数据
  将源账号的数据复制到当前账号
  操作前会自动备份目标账号数据

.account export (账号Hash) - 导出账号数据
  不指定Hash时，导出当前账号的数据
  将指定账号的数据导出到压缩包（默认路径：./plugin/export）''',

    '指令更新': '&oopm',
    '反馈发送': '&send',
    '数据备份': '&backup',
    '备份': '&backup',
    '指令清群': '&groupclear',
    '多账号连接': '&account',
    '账号管理': '&account'
}
